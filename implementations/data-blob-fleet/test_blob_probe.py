#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""test_blob_probe.py -- unit tests for the clean-room blob analyser.

Run:  python3 -I -m unittest -v test_blob_probe

Every test either (a) exercises a documented code path on the synthetic
fixtures, or (b) pins an *arithmetic* fact that is true for any input (e.g.
164480 = 2^7 x 5 x 257).  No real payload is required and none is present.
"""

import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import blob_probe as bp          # noqa: E402
import make_fixture as mf        # noqa: E402

PROBE = os.path.join(HERE, "blob_probe.py")
FIXTURES = os.path.join(HERE, "fixtures")


def fixture(name):
    path = os.path.join(FIXTURES, name)
    if not os.path.exists(path):
        mf.write_all(FIXTURES)
    with open(path, "rb") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# arithmetic
# ---------------------------------------------------------------------------

class TestFactorisation(unittest.TestCase):

    def test_fleet_sizes_factorise_as_documented(self):
        # 164480 = 2^7 * 5 * 257  and  34736 = 2^4 * 13 * 167
        self.assertEqual(bp.factorize(164480), {2: 7, 5: 1, 257: 1})
        self.assertEqual(bp.factorize(34736), {2: 4, 13: 1, 167: 1})
        self.assertEqual(bp.factor_string(164480), "2^7 x 5 x 257")
        self.assertEqual(bp.factor_string(34736), "2^4 x 13 x 167")

    def test_factor_string_leaves_out_unit_exponents(self):
        self.assertEqual(bp.factor_string(1620), "2^2 x 3^4 x 5")

    def test_divisors_are_complete_and_sorted(self):
        ds = bp.divisors(164480)
        self.assertEqual(ds, sorted(ds))
        self.assertEqual(len(ds), 32)          # (7+1)*(1+1)*(1+1)
        self.assertEqual(ds[0], 1)
        self.assertEqual(ds[-1], 164480)
        self.assertIn(257, ds)
        self.assertIn(41120, ds)

    def test_grid_decomposition_finds_the_hrtf_shape(self):
        # 164480 = 40 dirs x 2 ears x 2 (mag,phase) x 257 bins x 4 bytes
        self.assertEqual(40 * 2 * 2 * 257 * 4, 164480)
        self.assertEqual(80 * 514 * 4, 164480)
        recs = bp.grid_decompositions(164480)
        # the enumerator must offer at least one split that leaves the 257
        # divisor exposed with a 4-byte sample width available
        w4 = [r for r in recs if 257 in r["factors"] and 4 in r["widths"]]
        self.assertTrue(w4)
        # and at least one that leaves a 2-byte width
        w2 = [r for r in recs if 2 in r["widths"]]
        self.assertTrue(w2)

    def test_grid_decomposition_rejects_impossible_widths(self):
        # for size 6 the split [3] leaves remainder 2: divisible by 2, not by 4
        recs = bp.grid_decompositions(6)
        rec = [r for r in recs if r["factors"] == [3]][0]
        self.assertEqual(rec["remainder"], 2)
        self.assertIn(2, rec["widths"])
        self.assertNotIn(4, rec["widths"])


# ---------------------------------------------------------------------------
# header probe
# ---------------------------------------------------------------------------

class TestHeaderProbe(unittest.TestCase):

    def test_known_public_magics_are_recognised(self):
        h = bp.probe_header(b"MinPHR03" + b"\x00" * 56)
        self.assertIn("OpenAL Soft HRTF data set", h["magic_hints"])
        h = bp.probe_header(b"\x89HDF\r\n\x1a\n" + b"\x00" * 56)
        self.assertIn("HDF5 (the container SOFA/AES69 files are stored in)",
                      h["magic_hints"])

    def test_fourcc_container_header_is_reported(self):
        buf = b"VER0" + b"\x00" * 12 + b"DATE" + struct.pack("<I", 2023) + b"\x00" * 8
        h = bp.probe_header(buf)
        tags = [t["tag"] for t in h["fourcc_first_kib"]]
        self.assertIn("VER0", tags)
        self.assertIn("DATE", tags)
        self.assertEqual(tags[0], "VER0")

    def test_no_false_magic_on_random_bytes(self):
        h = bp.probe_header(fixture("unknown.bin"))
        self.assertEqual(h["magic_hints"], [])

    def test_header_fields_are_present_and_correct_width(self):
        h = bp.probe_header(fixture("dax_like.bin"))
        self.assertEqual(len(h["u32_le_first6"]), 6)
        self.assertEqual(len(h["u32_be_first6"]), 6)
        # fixture header word 0 is 9 little-endian
        self.assertEqual(h["u32_le_first6"][0], 9)
        self.assertEqual(h["first_bytes_hex"].split()[0], "09")


# ---------------------------------------------------------------------------
# stride detection
# ---------------------------------------------------------------------------

class TestStride(unittest.TestCase):

    def test_sixteen_byte_records_are_detected(self):
        buf = fixture("dax_like.bin")
        s = bp.detect_stride(buf)
        self.assertIsNotNone(s["best_tiling_stride"])
        self.assertEqual(s["best_tiling_stride"]["stride"], 16)
        self.assertTrue(s["best_tiling_stride"]["divides_length"])

    def test_detects_each_synthetic_stride_class(self):
        for stride in (8, 12, 16, 24, 32):
            buf = b"".join(bytes([i % 251]) * 3 + b"\x00" * (stride - 3)
                           for i in range(2000 // stride * 8))
            got = bp.detect_stride(buf, max_stride=64)["best_tiling_stride"]
            self.assertIsNotNone(got, "stride %d not found" % stride)
            # the fundamental must divide the reported period
            self.assertEqual(got["stride"] % stride, 0,
                             "stride %d -> reported %d" % (stride, got["stride"]))

    def test_flat_float_table_has_no_record_period(self):
        # a packed float table is self-similar only at the sample width
        s = bp.detect_stride(fixture("hrtf_like.bin"))
        self.assertEqual(s["best_tiling_stride"]["stride"], 4)
        self.assertLess(s["best_tiling_stride"]["byte_eq"], 0.40)

    def test_random_bytes_show_no_structure(self):
        s = bp.detect_stride(fixture("unknown.bin"))
        for rec in s["top_by_byte_equality"][:4]:
            self.assertLess(rec["byte_eq"], 0.10)

    def test_phase_profile_spikes_where_tags_live(self):
        buf = fixture("dax_like.bin")
        prof = bp.stride_flag_profile(buf, 16)
        hits = dict(prof["hits_by_phase"])
        self.assertTrue(hits)
        # every tag sits at one fixed phase of the 16-byte record; which phase
        # depends on where the header ends, so assert concentration not 0.
        top_phase = max(hits, key=hits.get)
        self.assertEqual(sum(1 for p in hits if p % 16 == top_phase % 16), 1)
        self.assertGreater(hits[top_phase], 1000)
        self.assertEqual(top_phase % 16, 24 % 16)

    def test_max_stride_is_respected(self):
        s = bp.detect_stride(b"\x00" * 4096, max_stride=32)
        self.assertEqual(s["max_stride_probed"], 32)
        self.assertTrue(all(r["stride"] <= 32
                            for r in s["top_by_byte_equality"]))


# ---------------------------------------------------------------------------
# float / int plausibility
# ---------------------------------------------------------------------------

class TestFloatPass(unittest.TestCase):

    def test_coefficient_table_passes(self):
        f = bp.float_pass(fixture("hrtf_like.bin"))
        self.assertTrue(f["verdict"]["looks_like_coefficient_table"])
        self.assertGreater(f["le"]["finite_fraction"], 0.999)
        self.assertGreater(f["le"]["in_physical_range_1e4"], 0.99)
        self.assertLess(f["le"]["denormal_fraction"], 0.01)

    def test_coefficient_table_is_not_unit_normalised(self):
        # the real table's DC gain is ~1.08, so |x| <= 1 is NOT the majority
        f = bp.float_pass(fixture("hrtf_like.bin"))
        self.assertFalse(f["verdict"]["unit_normalised"])

    def test_tag_container_fails(self):
        f = bp.float_pass(fixture("dax_like.bin"))
        self.assertFalse(f["verdict"]["looks_like_coefficient_table"])

    def test_unit_normalised_signal_is_recognised(self):
        vals = [0.5 * ((i % 17) - 8) / 8.0 for i in range(1024)]
        buf = b"".join(struct.pack("<f", v) for v in vals)
        f = bp.float_pass(buf)
        self.assertTrue(f["verdict"]["unit_normalised"])
        self.assertTrue(f["verdict"]["looks_like_coefficient_table"])

    def test_big_endian_reading_is_worse_than_little(self):
        f = bp.float_pass(fixture("hrtf_like.bin"))
        self.assertGreaterEqual(f["le"]["in_physical_range_1e4"],
                                f["be"]["in_physical_range_1e4"])

    def test_empty_input_is_safe(self):
        f = bp.float_pass(b"")
        self.assertIsNone(f["le"])
        self.assertFalse(f["verdict"]["looks_like_coefficient_table"])


class TestIntPass(unittest.TestCase):

    def test_tag_container_is_low_cardinality(self):
        i = bp.int_pass(fixture("dax_like.bin"))
        self.assertLess(i["u32"]["distinct_fraction"], 0.10)
        # 58-63% of the file is zero bytes, most of them inside u32 fields
        self.assertGreater(i["u32"]["zero_fraction"], 0.05)

    def test_coefficient_table_is_high_cardinality(self):
        i = bp.int_pass(fixture("hrtf_like.bin"))
        self.assertGreater(i["u32"]["distinct_fraction"], 0.5)

    def test_i16_range_reported(self):
        i = bp.int_pass(fixture("hrtf_like.bin"))
        self.assertIn("i16", i)
        self.assertGreaterEqual(i["i16"]["min"], -32768)
        self.assertLessEqual(i["i16"]["max"], 32767)


# ---------------------------------------------------------------------------
# entropy
# ---------------------------------------------------------------------------

class TestEntropy(unittest.TestCase):

    def test_flat_profile_for_homogeneous_table(self):
        e = bp.block_entropy(fixture("hrtf_like.bin"), blocks=16)
        self.assertEqual(e["blocks"], 16)
        labels = [b["entropy"] for b in e["profile"]]
        self.assertLess(max(labels) - min(labels), 1.0)

    def test_falling_tail_when_padding_is_appended(self):
        buf = bytes(range(256)) * 40 + b"\x00" * 4000
        e = bp.block_entropy(buf, blocks=8)
        self.assertLess(e["profile"][-1]["entropy"], e["profile"][0]["entropy"])
        self.assertEqual(e["shape"], "falling-tail")

    def test_zero_fraction_is_tracked_per_block(self):
        # 400 B: 200 zeros then all-nonzero. blocks=4 -> 100 B blocks, so the
        # first two blocks are pure zero and the last two are pure nonzero.
        buf = b"\x00" * 200 + b"\x01\x02\x03\x04" * 50
        e = bp.block_entropy(buf, blocks=4)
        self.assertEqual([b["zero_fraction"] for b in e["profile"]],
                         [1.0, 1.0, 0.0, 0.0])

    def test_empty_input_entropy(self):
        e = bp.block_entropy(b"")
        self.assertEqual(e["blocks"], 0)
        self.assertEqual(e["profile"], [])

    def test_entropy_bounds(self):
        self.assertEqual(bp.shannon_entropy(b"\x00" * 100), 0.0)
        self.assertAlmostEqual(bp.shannon_entropy(bytes(range(256)) * 4), 8.0, places=6)


# ---------------------------------------------------------------------------
# strings
# ---------------------------------------------------------------------------

class TestStrings(unittest.TestCase):

    def test_fourcc_vocabulary_is_counted(self):
        s = bp.extract_strings(fixture("dax_like.bin"))
        self.assertGreater(s["fourcc_lower_count"], 50)

    def test_float_table_yields_no_fourcc(self):
        s = bp.extract_strings(fixture("hrtf_like.bin"))
        self.assertEqual(s["fourcc_lower_count"], 0)

    def test_min_length_is_honoured(self):
        buf = b"abc\x00abcdef\x00"
        self.assertEqual(len(bp.extract_strings(buf, min_len=4)["strings"]), 1)
        self.assertEqual(len(bp.extract_strings(buf, min_len=2)["strings"]), 2)


# ---------------------------------------------------------------------------
# diff mode (the F-75 method)
# ---------------------------------------------------------------------------

class TestDiff(unittest.TestCase):

    def test_identical_files(self):
        a = fixture("dax_like.bin")
        d = bp.diff_bytes(a, a)
        self.assertEqual(d["identical_fraction"], 1.0)
        self.assertEqual(d["differing"], 0)
        self.assertEqual(d["diff_run_count"], 0)

    def test_single_region_change_is_localised(self):
        a = fixture("dax_like.bin")
        b = fixture("dax_like_2.bin")
        d = bp.diff_bytes(a, b)
        self.assertGreater(d["identical_fraction"], 0.99)
        self.assertEqual(d["diff_runs"], [{"start": 27224, "end": 27383,
                                           "length": 160}])
        self.assertEqual(d["diff_span"], [27224, 27383])

    def test_two_versions_differ_somewhere(self):
        d = bp.diff_bytes(fixture("hrtf_like.bin"), fixture("hrtf_like_2.bin"))
        self.assertLess(d["identical_fraction"], 1.0)
        self.assertGreater(d["differing"], 1000)

    def test_unequal_lengths_are_reported_not_truncated(self):
        a = b"AAAA" * 100
        b = b"AAAA" * 50
        d = bp.diff_bytes(a, b)
        self.assertFalse(d["same_length"])
        self.assertEqual(d["len_a"], 400)
        self.assertEqual(d["len_b"], 200)
        self.assertEqual(d["compared"], 200)
        self.assertEqual(d["identical_fraction"], 1.0)


# ---------------------------------------------------------------------------
# malformed input
# ---------------------------------------------------------------------------

class TestMalformed(unittest.TestCase):

    def test_truncated_float_table(self):
        buf = fixture("hrtf_like_truncated.bin")
        self.assertEqual(len(buf), 100001)
        rep = bp.analyse(buf, name="trunc")
        self.assertEqual(rep["bytes"], 100001)
        self.assertIn("floats", rep)          # must not raise

    def test_empty_file(self):
        rep = bp.analyse(b"", name="empty")
        self.assertEqual(rep["bytes"], 0)
        self.assertEqual(rep["factorisation"]["prime_factors"], "0")

    def test_one_byte_file(self):
        rep = bp.analyse(b"\x01", name="one")
        self.assertEqual(rep["bytes"], 1)
        self.assertIsNotNone(rep["ints"].get("u8"))

    def test_stride_on_tiny_input(self):
        s = bp.detect_stride(b"\x01\x02", max_stride=256)
        self.assertIsNotNone(s)

    def test_strings_on_binary_only(self):
        s = bp.extract_strings(b"\x00\x01\x02" * 100)
        self.assertEqual(s["count"], 0)


# ---------------------------------------------------------------------------
# CLI / JSON contracts
# ---------------------------------------------------------------------------

class TestCLI(unittest.TestCase):

    def run_probe(self, *args):
        return subprocess.run([sys.executable, "-I", PROBE] + list(args),
                              capture_output=True, text=True)

    def test_brief_runs_and_prints_summary(self):
        r = self.run_probe(os.path.join(FIXTURES, "dax_like.bin"), "--brief")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("34736 bytes", r.stdout)
        self.assertIn("best stride", r.stdout)

    def test_json_contract(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "r.json")
            r = self.run_probe(os.path.join(FIXTURES, "hrtf_like.bin"),
                               "--json", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
        for key in ("file", "bytes", "md5", "sha256", "factorisation",
                    "header", "stride", "entropy", "strings", "ints",
                    "floats", "decompositions"):
            self.assertIn(key, rep)
        self.assertEqual(rep["bytes"], 164480)
        self.assertEqual(rep["factorisation"]["prime_factors"],
                         "2^7 x 5 x 257")

    def test_json_floats_flag_adds_samples(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "r.json")
            self.run_probe(os.path.join(FIXTURES, "hrtf_like.bin"),
                           "--json", out, "--floats")
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
        self.assertIn("values", rep["floats"])
        self.assertLessEqual(len(rep["floats"]["values"]), 4096)

    def test_diff_mode_in_json(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "r.json")
            self.run_probe(os.path.join(FIXTURES, "dax_like.bin"),
                           "--diff", os.path.join(FIXTURES, "dax_like_2.bin"),
                           "--json", out)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
        self.assertIn("diff", rep)
        self.assertEqual(rep["diff"]["diff_runs"],
                         [{"start": 27224, "end": 27383, "length": 160}])

    def test_missing_file_exits_2(self):
        r = self.run_probe("/nonexistent/blob.bin")
        self.assertEqual(r.returncode, 2)
        self.assertIn("cannot read", r.stderr)

    def test_bad_argument_exits_2(self):
        r = self.run_probe("--no-such-flag")
        self.assertEqual(r.returncode, 2)

    def test_md5_matches_hashlib(self):
        buf = fixture("dax_like.bin")
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "r.json")
            self.run_probe(os.path.join(FIXTURES, "dax_like.bin"), "--json", out)
            with open(out, encoding="utf-8") as fh:
                rep = json.load(fh)
        self.assertEqual(rep["md5"], hashlib.md5(buf).hexdigest())
        self.assertEqual(rep["sha256"], hashlib.sha256(buf).hexdigest())


# ---------------------------------------------------------------------------
# fixture determinism
# ---------------------------------------------------------------------------

class TestFixtureDeterminism(unittest.TestCase):

    def test_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as td:
            first = mf.write_all(td)
            digests = {}
            for name, size, digest in first:
                digests[name] = (size, digest)
            second = mf.write_all(td)
            for name, size, digest in second:
                self.assertEqual(digests[name], (size, digest),
                                 "%s not deterministic" % name)

    def test_fixture_magnitudes_mirror_the_real_files(self):
        sizes = {name: size for name, size, _ in mf.write_all(tempfile.mkdtemp())}
        self.assertEqual(sizes["hrtf_like.bin"], 164480)
        self.assertEqual(sizes["dax_like.bin"], 34736)

    def test_fixture_arithmetic_matches_real(self):
        # same factorisation, therefore the same plausible-grid question
        self.assertEqual(bp.factorize(164480), bp.factorize(164480))
        self.assertEqual(struct.calcsize("<257f") * 160, 164480)

    def test_generator_uses_no_real_tags(self):
        # the synthetic tag vocabulary is the NATO alphabet only
        for tag in mf.SYNTH_TAGS:
            core = tag.rstrip(b"\x00").decode()
            self.assertTrue(core.isalpha())
        self.assertEqual(len(set(mf.SYNTH_TAGS)), len(mf.SYNTH_TAGS))


# ---------------------------------------------------------------------------
# end-to-end shape assertions on the synthetic fleet
# ---------------------------------------------------------------------------

class TestEndToEnd(unittest.TestCase):

    def test_two_classes_are_separable(self):
        hrtf = bp.analyse(fixture("hrtf_like.bin"), name="hrtf")
        dax = bp.analyse(fixture("dax_like.bin"), name="dax")
        self.assertTrue(hrtf["floats"]["verdict"]["looks_like_coefficient_table"])
        self.assertFalse(dax["floats"]["verdict"]["looks_like_coefficient_table"])
        self.assertEqual(dax["stride"]["best_tiling_stride"]["stride"], 16)
        self.assertGreater(dax["strings"]["fourcc_lower_count"], 50)
        self.assertEqual(hrtf["strings"]["fourcc_lower_count"], 0)
        self.assertGreater(hrtf["entropy"]["overall"], 6.0)
        self.assertLess(dax["entropy"]["overall"], 5.0)

    def test_analyse_is_json_serialisable(self):
        rep = bp.analyse(fixture("unknown.bin"), name="u")
        json.dumps(rep)                        # must not raise


if __name__ == "__main__":
    unittest.main(verbosity=2)
