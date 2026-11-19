#!/usr/bin/env python3
"""test_bm2n_probe.py -- unittest suite for the clean-room ADSP bm2n container
probe (``bm2n_probe.py``), driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written from the public BSD-3-Clause-Clear QNN/HTP headers
(``QNN/HTP/core/tensor.h`` -> ``TENSOR_MAGIC``;
``QNN/HTP/include/HTP/pickle_header_tags.h`` -> ``Hdr_MAGIC`` and the
``htp_header_locate_field()`` tag grammar) plus the GPL-2.0-only
``drivers/misc/fastrpc.c``, and from own structural measurements of the
payload bytes. No decompiled code and no proprietary documentation were used.
Fixture bytes are self-made from the measured layout only
(``make_fixture.py``); no vendor payload is committed or read by this suite
except opportunistically, behind a skip guard.

Run from this directory:

    python3 -m unittest -v test_bm2n_probe

Covers: fixture existence/determinism/size fidelity, compact header decode
(window / frozen constants / build-id / segment count), the segment-table
walk (count-complement sentinel, kind vocabulary, ascending 0x100-aligned
values, last value == base), prologue grammar (zero run, sentinel N+1,
length-prefixed RTTI type name, float 1.0f), record walk, tail terminator and
padding, printable-string extraction, entropy block shape, word/short-word
histogram shape, fleet-diff percentages (F-75 method), the pickle family and
its documented tag walk, structural-violation diagnostics for each deliberate
breakage class, JSON and --brief CLI contracts, exit statuses, and the
``json_ready`` serialiser.
"""

import contextlib
import hashlib
import io
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import bm2n_probe
import make_fixture

FIX = os.path.join(HERE, "fixtures")

BM2N14_FX = os.path.join(FIX, "bm2n14_synthetic.bin")
BM2N06_FX = os.path.join(FIX, "bm2n06_synthetic.bin")
BM2N12_FX = os.path.join(FIX, "bm2n12_synthetic.bin")
PICKLE_FX = os.path.join(FIX, "bm2n12_pickle_synthetic.bin")
BAD_MAGIC_FX = os.path.join(FIX, "bad_magic_synthetic.bin")
BAD_CONST_FX = os.path.join(FIX, "bad_constant_synthetic.bin")
TRUNC_FX = os.path.join(FIX, "truncated_synthetic.bin")

ALL_FIXTURES = (BM2N14_FX, BM2N06_FX, BM2N12_FX, PICKLE_FX,
                BAD_MAGIC_FX, BAD_CONST_FX, TRUNC_FX)

# Real payloads are proprietary and git-ignored; the suite never requires
# them. When a local fetch exists these extra assertions run, otherwise they
# are skipped so the suite is self-contained.
REAL_DIRS = ("/tmp/astro_u/payloads", "/tmp/astro_u/hunt")
REAL_BRIEF = ("bm2n06", "bm2n08", "bm2n12", "bm2n13_sm8350", "bm2n14",
              "bm2n15")


def real_payloads():
    found = []
    for d in REAL_DIRS:
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if name.startswith("bm2n") and name.endswith(".bin"):
                found.append(os.path.join(d, name))
    return found


def have_real_fleet():
    return all(os.path.isfile(os.path.join(REAL_DIRS[0], n + ".bin"))
               for n in REAL_BRIEF)


def readf(path):
    """Read a file's bytes without leaking the handle (keeps the suite
    ResourceWarning-clean)."""
    with open(path, "rb") as fh:
        return fh.read()


def run_cli(args):
    return subprocess.run(
        [sys.executable, "-I", os.path.join(HERE, "bm2n_probe.py")] + args,
        capture_output=True, text=True)


def tmpdir():
    base = "/tmp/opencode" if os.path.isdir("/tmp/opencode") else None
    return tempfile.mkdtemp(dir=base, prefix="bm2n-test-")


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------

class TestFixtures(unittest.TestCase):
    """Fixture layer: existence, determinism, and fleet-magnitude sizes."""

    def test_all_fixtures_exist(self):
        for f in ALL_FIXTURES:
            self.assertTrue(os.path.isfile(f), "missing fixture %s" % f)

    def test_regeneration_is_byte_identical(self):
        """Deterministic generator: re-running reproduces every fixture
        byte-for-byte, the lab's make_fixture precedent."""
        before = {}
        for f in ALL_FIXTURES:
            with open(f, "rb") as fh:
                before[f] = fh.read()
        # rewrites the fixtures in place; its progress chatter is not part of
        # this test's contract, so keep the run output clean
        with contextlib.redirect_stdout(io.StringIO()):
            make_fixture.main()
        for f, blob in before.items():
            with open(f, "rb") as fh:
                after = fh.read()
            self.assertEqual(
                hashlib.md5(after).hexdigest(),
                hashlib.md5(blob).hexdigest(),
                "fixture %s is not deterministic" % os.path.basename(f))

    def test_sizes_mirror_fleet_magnitudes(self):
        """Synthetic sizes equal the measured real sizes for the files they
        mirror (own measurement: bm2n14 103,168 B; bm2n06 864,824 B;
        bm2n12 2,623,528 B)."""
        self.assertEqual(os.path.getsize(BM2N14_FX), 103168)
        self.assertEqual(os.path.getsize(BM2N06_FX), 864824)
        self.assertEqual(os.path.getsize(BM2N12_FX), 2623528)

    def test_fixtures_carry_no_real_payload_bytes(self):
        """Clean-room guard: fixtures are generated from a SHA-256 counter
        stream, so a fixture must not share a long run with any real payload
        that happens to be on disk."""
        reals = real_payloads()
        if not reals:
            self.skipTest("no real payload on disk")
        fx = readf(BM2N14_FX)
        probe = fx[0x1000:0x1100]      # a body slice, past the header
        for r in reals:
            blob = readf(r)
            self.assertNotIn(probe, blob,
                             "fixture body slice appears in %s" % r)


# ---------------------------------------------------------------------------
# compact header
# ---------------------------------------------------------------------------

class TestCompactHeader(unittest.TestCase):
    """Header decode against the 48/48-measured compact layout."""

    @classmethod
    def setUpClass(cls):
        cls.res = bm2n_probe.probe_file(BM2N14_FX)

    def test_family_and_no_violations(self):
        self.assertEqual(self.res["family"], "compact")
        self.assertEqual(self.res["violations"], [])
        self.assertTrue(self.res["structural_ok"])

    def test_window_field_is_repeated_three_times(self):
        buf = readf(BM2N14_FX)
        h = self.res["header"]
        self.assertEqual(h["window"], 0x200000)
        for off in (0x00, 0x1C, 0x24):
            self.assertEqual(struct.unpack_from("<I", buf, off)[0], 0x200000,
                             "window not repeated at 0x%02x" % off)
        self.assertEqual(h["window_hex"], "0x00200000")

    def test_frozen_header_constants(self):
        h = self.res["header"]
        self.assertEqual(h["const_0x04"], 0)
        self.assertEqual(h["const_0x08"], 7)
        self.assertEqual(h["const_0x14"], "0xfa0000fa")
        self.assertEqual(h["const_0x18"], 4)
        self.assertEqual(h["const_0x28"], "0x00010400")

    def test_build_id_is_seven_ascii_bytes(self):
        h = self.res["header"]
        self.assertEqual(h["build_id"], "2a8527c")
        self.assertEqual(len(h["build_id"]), 7)
        self.assertTrue(all(0x20 <= ord(c) <= 0x7E for c in h["build_id"]))
        self.assertEqual(h["build_id_offset"], 0x0C)

    def test_header_length_follows_segment_count(self):
        h = self.res["header"]
        self.assertEqual(h["count"], 2)
        self.assertEqual(h["length"], 0x2C + 8 * h["count"])
        self.assertEqual(h["length"], 0x3C)

    def test_header_length_for_n3_and_n4(self):
        """hlen = 0x2c + 8*N: 0x44 for N=3 (bm2n12) and 0x4c for N=4."""
        r3 = bm2n_probe.probe_file(BM2N12_FX)
        self.assertEqual(r3["header"]["count"], 3)
        self.assertEqual(r3["header"]["length"], 0x44)
        buf = make_fixture.build_compact(
            "fx-n4", 1 << 20, 4, 0x400000, "1234567",
            [bm2n_probe.KIND_FILE, bm2n_probe.KIND_PROLOGUE_END],
            mem_value=0x00AC7000)
        r4 = bm2n_probe.probe_bytes(buf, "n4")
        self.assertEqual(r4["header"]["count"], 4)
        self.assertEqual(r4["header"]["length"], 0x4C)
        self.assertTrue(r4["structural_ok"], r4["violations"])

    def test_too_small_file_is_a_structural_error(self):
        for blob, label in ((b"\x00\x00\x20\x00" * 2, "8 B"),
                            (b"\x00\x00\x20\x00\x00\x00\x00\x00", "8 B hdr")):
            res = bm2n_probe.probe_bytes(blob, label)
            self.assertFalse(res["structural_ok"], label)
            joined = " ".join(res["violations"]).lower()
            self.assertTrue("too small" in joined or "unrecognised" in joined,
                            "%s: %s" % (label, res["violations"]))

    def test_segment_count_out_of_range(self):
        buf = bytearray(make_fixture.build_compact(
            "fx-cnt", 1 << 16, 2, 0x200000, "1234567",
            [bm2n_probe.KIND_PROLOGUE_END]))
        struct.pack_into("<I", buf, 0x20, 0)      # N = 0
        res = bm2n_probe.probe_bytes(bytes(buf), "cnt0")
        self.assertFalse(res["structural_ok"])
        self.assertIn("count", " ".join(res["violations"]).lower())


# ---------------------------------------------------------------------------
# segment table
# ---------------------------------------------------------------------------

class TestSegmentTable(unittest.TestCase):
    """The segment table is the highest-value structural finding."""

    @classmethod
    def setUpClass(cls):
        cls.res = bm2n_probe.probe_file(BM2N12_FX)

    def test_table_offset_and_entry_count(self):
        st = self.res["segment_table"]
        self.assertEqual(st["offset"], 0x2C)
        self.assertEqual(st["entry_count"], 3)
        # N-1 real pairs; the last pair is the sentinel
        self.assertEqual(len(st["entries"]), st["entry_count"] - 1)

    def test_sentinel_encodes_count_and_complement(self):
        buf = readf(BM2N12_FX)
        n = self.res["header"]["count"]
        hlen = self.res["header"]["length"]
        sentinel = struct.unpack_from("<I", buf, hlen - 8)[0]
        base = struct.unpack_from("<I", buf, hlen - 4)[0]
        self.assertEqual(sentinel, bm2n_probe.count_complement(n))
        self.assertEqual(sentinel & 0xFFFF, n)
        self.assertEqual((sentinel >> 16) & 0xFFFF, (~n) & 0xFFFF)
        self.assertEqual(self.res["header"]["base"], base)

    def test_last_entry_value_equals_base(self):
        entries = self.res["segment_table"]["entries"]
        self.assertEqual(entries[-1]["value"], self.res["header"]["base"])

    def test_last_entry_kind_is_prologue_end(self):
        entries = self.res["segment_table"]["entries"]
        self.assertEqual(entries[-1]["kind"], bm2n_probe.KIND_PROLOGUE_END)
        self.assertEqual(entries[-1]["role"], "prologue-end")

    def test_entries_ascending_and_0x100_aligned(self):
        entries = self.res["segment_table"]["entries"]
        resident = [e["value"] for e in entries
                    if e["value"] <= self.res["header"]["base"]]
        self.assertEqual(resident, sorted(resident))
        self.assertEqual(len(resident), len(set(resident)))
        for e in entries:
            self.assertEqual(e["value"] % 0x100, 0,
                             "entry %d not 0x100-aligned" % e["index"])

    def test_kind_vocabulary(self):
        """All observed kinds share low byte 0 and bits 8..15 == 0x01."""
        seen = set()
        for f in (BM2N14_FX, BM2N06_FX, BM2N12_FX):
            for e in bm2n_probe.probe_file(f)["segment_table"]["entries"]:
                seen.add(e["kind"])
                self.assertEqual(e["kind"] & 0xFF, 0)
                self.assertEqual((e["kind"] >> 8) & 0xFF, 0x01)
                self.assertIn(e["kind"], bm2n_probe.KIND_ROLE)
        self.assertTrue(seen)

    def test_non_resident_entry_is_larger_than_the_file(self):
        st = self.res["segment_table"]
        nonres = st["non_resident_entries"]
        self.assertEqual(len(nonres), 1)
        e = nonres[0]
        self.assertEqual(e["kind"], bm2n_probe.KIND_MEM)
        self.assertEqual(e["role"], "non-resident")
        self.assertGreater(e["value"], self.res["size"])
        self.assertEqual(e["value"] % 0x1000, 0)

    def test_corrupt_kind_is_reported(self):
        buf = bytearray(readf(BM2N14_FX))
        struct.pack_into("<I", buf, 0x2C + 4, 0x00000123)   # bad kind
        res = bm2n_probe.probe_bytes(bytes(buf), "badkind")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("vocabulary" in m for m in res["violations"]))

    def test_corrupt_sentinel_is_reported(self):
        buf = bytearray(readf(BM2N14_FX))
        struct.pack_into("<I", buf, 0x3C - 8, 0xDEADBEEF)
        res = bm2n_probe.probe_bytes(bytes(buf), "badsent")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("sentinel" in m for m in res["violations"]))

    def test_base_outside_file_is_a_structural_error(self):
        buf = bytearray(readf(BM2N14_FX))
        struct.pack_into("<I", buf, 0x3C - 4, 0xFFFFFF00)
        res = bm2n_probe.probe_bytes(bytes(buf), "badbase")
        self.assertFalse(res["structural_ok"])
        self.assertIn("base", " ".join(res["violations"]).lower())

    def test_region_boundaries_match_table(self):
        """Derived regions partition the file with no gaps or overlaps."""
        regions = self.res["regions"]
        self.assertEqual(regions[0]["start"], 0)
        for a, b in zip(regions, regions[1:]):
            self.assertEqual(a["end"], b["start"])
        self.assertEqual(regions[-1]["end"], self.res["size"])
        names = [r["name"] for r in regions]
        self.assertIn("header", names)
        self.assertIn("prologue", names)
        self.assertIn("records", names)
        self.assertIn("tail", names)


# ---------------------------------------------------------------------------
# prologue
# ---------------------------------------------------------------------------

class TestPrologue(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = bm2n_probe.probe_file(BM2N12_FX)
        cls.pro = cls.res["prologue"]

    def test_prologue_bounds_precede_first_record(self):
        self.assertEqual(self.pro["start"], self.res["header"]["base"])
        self.assertEqual(self.pro["end"], self.res["records"]["first"])
        self.assertGreater(self.pro["length"], 0)

    def test_zero_run_equals_header_length(self):
        """Own measurement: the prologue opens with hlen bytes of padding."""
        self.assertEqual(self.pro["zero_run"], self.res["header"]["length"])

    def test_sentinel_counts_n_plus_one(self):
        """Prologue sentinel is count_complement(N+1), header sentinel is
        count_complement(N): an off-by-one trap this suite pins."""
        self.assertEqual(self.pro["count"], self.res["header"]["count"] + 1)
        buf = readf(BM2N12_FX)
        self.assertEqual(struct.unpack_from("<I", buf, self.pro["sentinel"])[0],
                         bm2n_probe.count_complement(self.pro["count"]))

    def test_length_prefixed_rtti_type_name(self):
        self.assertEqual(len(self.pro["type_strings"]), 1)
        t = self.pro["type_strings"][0]
        self.assertEqual(t["text"], "14ConcreteTensorIN5Tdefs10QuantUint8EE")
        self.assertEqual(len(t["text"]), 38)
        self.assertEqual(t["declared_length"], 38)
        self.assertTrue(t["length_matches"])

    def test_tail_words_contain_float_one(self):
        self.assertTrue(self.pro["has_float_one"])
        self.assertIn(bm2n_probe.PROLOGUE_TAIL_FLOAT_ONE,
                      self.pro["tail_words"])

    def test_pointer_words_are_file_offsets(self):
        """0x40xxxxxx words decode to offsets inside the file."""
        pts = self.pro["pointer_words"]
        self.assertTrue(pts)
        for p in pts:
            self.assertLess(p["value"] - 0x40000000, self.res["size"])


# ---------------------------------------------------------------------------
# records
# ---------------------------------------------------------------------------

class TestRecords(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = bm2n_probe.probe_file(BM2N14_FX)
        cls.rec = cls.res["records"]

    def test_record_delimiters_are_the_magic_only(self):
        buf = readf(BM2N14_FX)
        first, last = self.rec["first"], self.rec["last"]
        self.assertEqual(buf[first:first + 4], bm2n_probe.RECORD_MAGIC)
        self.assertEqual(buf[last:last + 4], bm2n_probe.RECORD_MAGIC)
        self.assertEqual(self.rec["count"],
                         buf.count(bm2n_probe.RECORD_MAGIC))

    def test_lengths_are_multiples_of_four_and_aligned(self):
        self.assertTrue(self.rec["all_lengths_multiple_of_4"])
        self.assertTrue(self.rec["all_offsets_aligned_4"])
        self.assertEqual(self.rec["length_min"], 40)

    def test_record_walk_depends_only_on_the_magic(self):
        """Own measurement: there is no length field. Corrupting any single
        non-magic word of a record must leave the boundaries unchanged."""
        raw = readf(BM2N14_FX)
        base = struct.unpack_from("<I", raw, 0x3C - 4)[0]
        longs = [i for i in range(base, len(raw) - 3)
                 if raw[i:i + 4] == bm2n_probe.RECORD_MAGIC]
        base_res = bm2n_probe.probe_bytes(raw, "base")
        for k in (2, 3, 4, 5, 6):            # skip the magic at +0
            buf = bytearray(raw)
            struct.pack_into("<I", buf, longs[3] + 4 * k, 0xFFFFFFFF)
            res = bm2n_probe.probe_bytes(bytes(buf), "mut")
            self.assertEqual(res["records"]["count"],
                             base_res["records"]["count"])
            self.assertEqual(res["records"]["first"], base_res["records"]["first"])
            self.assertEqual(res["records"]["last"], base_res["records"]["last"])

    def test_walk_records_rejects_empty_region(self):
        buf = b"\x00" * 64
        out = bm2n_probe.walk_records(buf, 0, len(buf) - 4)
        self.assertEqual(out["count"], 0)

    def test_missing_all_magic_is_a_structural_error(self):
        buf = bytearray(readf(BM2N14_FX))
        base = struct.unpack_from("<I", buf, 0x3C - 4)[0]
        for i in range(base, len(buf) - 3):
            if buf[i:i + 4] == bm2n_probe.RECORD_MAGIC:
                buf[i:i + 4] = b"\x00\x00\x00\x00"
        res = bm2n_probe.probe_bytes(bytes(buf), "nomagic")
        self.assertFalse(res["structural_ok"])


# ---------------------------------------------------------------------------
# tail
# ---------------------------------------------------------------------------

class TestTail(unittest.TestCase):

    def test_terminator_and_padding(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        tail = res["tail"]
        buf = readf(BM2N14_FX)
        self.assertEqual(tail["terminator"], "0xbeeff00d")
        self.assertEqual(buf[tail["terminator_offset"]:
                             tail["terminator_offset"] + 4],
                         bm2n_probe.RECORD_TERMINATOR)
        self.assertLessEqual(tail["padding_length"], 8)
        self.assertEqual(tail["terminator_offset"] + 4 +
                         tail["padding_length"], res["size"])

    def test_oversized_padding_is_reported(self):
        raw = readf(BM2N14_FX)
        t = bm2n_probe.probe_file(BM2N14_FX)["tail"]["terminator_offset"]
        buf = raw[:t + 4] + b"\xAA" * 12
        res = bm2n_probe.probe_bytes(buf, "pad")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("padding" in m for m in res["violations"]),
                        res["violations"])

    def test_padding_must_be_zero_or_0x55(self):
        import shutil
        raw = readf(BM2N14_FX)
        t = bm2n_probe.probe_file(BM2N14_FX)["tail"]["terminator_offset"]
        for fill, ok in ((b"\x00" * 4, True), (b"\x55" * 4, True),
                         (b"\x12\x34\x56\x78", False)):
            buf = raw[:t + 4] + fill
            res = bm2n_probe.probe_bytes(buf, "padfill")
            self.assertEqual(res["structural_ok"], ok,
                             "fill %r -> %s" % (fill, res["violations"]))
        del shutil


# ---------------------------------------------------------------------------
# strings / entropy / histograms
# ---------------------------------------------------------------------------

class TestStrings(unittest.TestCase):

    def test_offsets_are_ascending_and_lengths_honest(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        buf = readf(BM2N14_FX)
        strs = res["strings"]
        self.assertTrue(strs)
        prev = -1
        for s in strs:
            self.assertGreater(s["offset"], prev)
            prev = s["offset"]
            self.assertGreaterEqual(s["length"], 6)
            self.assertEqual(buf[s["offset"]:s["offset"] + s["length"]],
                             s["text"].encode("ascii", "replace"))

    def test_extract_strings_min_length_boundary(self):
        buf = b"\x00" + b"ABCDE" + b"\x00" + b"ABCDEF" + b"\x00"
        got = bm2n_probe.extract_strings(buf, min_len=6)
        self.assertEqual([g["text"] for g in got], ["ABCDEF"])

    def test_extract_strings_handles_run_at_eof(self):
        got = bm2n_probe.extract_strings(b"\x00" + b"ABCDEFGH", min_len=6)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["text"], "ABCDEFGH")
        self.assertEqual(got[0]["offset"], 1)

    def test_type_name_is_found_in_the_string_list(self):
        res = bm2n_probe.probe_file(BM2N12_FX)
        texts = [s["text"] for s in res["strings"]]
        self.assertTrue(any("ConcreteTensor" in t for t in texts))


class TestEntropy(unittest.TestCase):

    def test_profile_shape_and_partition(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        ent = res["entropy"]
        self.assertEqual(ent["block_size"], 65536)
        expected_blocks = (res["size"] + 65535) // 65536
        self.assertEqual(len(ent["blocks"]), expected_blocks)
        self.assertEqual(sum(b["length"] for b in ent["blocks"]), res["size"])
        self.assertLessEqual(ent["min"], ent["mean"])
        self.assertLessEqual(ent["mean"], ent["max"])

    def test_entropy_bounds_and_flat_block(self):
        self.assertEqual(bm2n_probe.entropy(b""), 0.0)
        self.assertEqual(bm2n_probe.entropy(b"\x00" * 1000), 0.0)
        self.assertAlmostEqual(bm2n_probe.entropy(bytes(range(256))), 8.0,
                               places=6)

    def test_region_entropy_is_bounded(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        for r in res["regions"]:
            self.assertGreaterEqual(r["entropy"], 0.0)
            self.assertLessEqual(r["entropy"], 8.0001)
            self.assertGreaterEqual(r["zero_pct"], 0.0)
            self.assertLessEqual(r["zero_pct"], 100.0)

    def test_custom_block_size(self):
        prof = bm2n_probe.entropy_profile(b"A" * 1000, block=256)
        self.assertEqual(prof["block_size"], 256)
        self.assertEqual(len(prof["blocks"]), 4)


class TestHistograms(unittest.TestCase):

    def test_word_histogram_shape_and_totals(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        w = res["words"]
        self.assertEqual(w["u32_total"], res["size"] // 4)
        self.assertEqual(w["u16_total"], res["size"] // 2)
        self.assertLessEqual(len(w["u32_top"]), 16)
        counts = [x["count"] for x in w["u32_top"]]
        self.assertEqual(counts, sorted(counts, reverse=True))
        self.assertLessEqual(sum(counts), w["u32_total"])

    def test_magic_dominates_the_u32_histogram(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        top = res["words"]["u32_top"][0]
        self.assertEqual(top["value"], bm2n_probe.TENSOR_MAGIC)
        self.assertEqual(top["count"], res["records"]["count"])

    def test_small_histogram(self):
        w = bm2n_probe.word_histograms(b"\x01\x00\x01\x00\x02\x00", top=4)
        self.assertEqual(w["u32_total"], 1)
        self.assertEqual(w["u16_total"], 3)
        self.assertEqual(w["u16_top"][0]["value"], 1)
        self.assertEqual(w["u16_top"][0]["count"], 2)


# ---------------------------------------------------------------------------
# pickle family
# ---------------------------------------------------------------------------

class TestPickleFamily(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = bm2n_probe.probe_file(PICKLE_FX)

    def test_detected_as_pickle_with_public_magic(self):
        self.assertEqual(self.res["family"], "pickle")
        self.assertEqual(self.res["header"]["magic"], "0x7309f72b")
        self.assertEqual(bm2n_probe.HTP_HDR_MAGIC, 0x7309F72B)

    def test_header_word_count_matches_documented_field(self):
        buf = readf(PICKLE_FX)
        hwords = struct.unpack_from("<I", buf, 4)[0] & 0xFFFF
        self.assertEqual(self.res["header"]["header_words"], hwords)
        self.assertEqual(self.res["header"]["length"] // 4, hwords)

    def test_tag_walk_follows_documented_grammar(self):
        """recdesc = (tag << 16) | rlen, rlen in words incl. the descriptor."""
        buf = readf(PICKLE_FX)
        tags = self.res["pickle_tags"]
        self.assertTrue(tags)
        expected = 8
        for t in tags:
            self.assertEqual(t["offset"], expected)
            recdesc = struct.unpack_from("<I", buf, t["offset"])[0]
            self.assertEqual(recdesc & 0xFFFF, t["rlen_words"])
            self.assertEqual(recdesc >> 16, t["tag"])
            self.assertEqual(t["payload_bytes"], (t["rlen_words"] - 1) * 4)
            expected = t["offset"] + 4 * t["rlen_words"]
        self.assertEqual(expected, self.res["header"]["length"])

    def test_expected_tags_present_in_order(self):
        names = [t["tag_ascii"] for t in self.res["pickle_tags"]]
        self.assertEqual(names, ["Id", "Sz", "Vr", "Op", "Zz"])

    def test_build_id_from_version_tag(self):
        self.assertEqual(self.res["header"]["build_id"], "2c855d1")

    def test_no_segment_table_is_claimed(self):
        st = self.res["segment_table"]
        self.assertEqual(st["entry_count"], 0)
        self.assertIsNone(st["offset"])
        self.assertIn("OPEN", st["note"])

    def test_shared_record_machinery(self):
        self.assertGreater(self.res["records"]["count"], 0)
        self.assertEqual(self.res["tail"]["terminator"], "0xbeeff00d")

    def test_regions_partition_the_file(self):
        regs = self.res["regions"]
        self.assertEqual(regs[0]["start"], 0)
        for a, b in zip(regs, regs[1:]):
            self.assertEqual(a["end"], b["start"])
        self.assertEqual(regs[-1]["end"], self.res["size"])
        names = [r["name"] for r in regs]
        self.assertIn("pickle_header", names)
        self.assertIn("pickle_preamble", names)

    def test_bad_pickle_record_length_is_a_structural_error(self):
        buf = bytearray(readf(PICKLE_FX))
        struct.pack_into("<I", buf, 8, (0x6449 << 16) | 0xFFFF)
        with self.assertRaises(bm2n_probe.StructureError):
            bm2n_probe.parse_pickle(bytes(buf), "badpickle")

    def test_multi_pickle_magic_is_flagged_open(self):
        buf = bytearray(readf(PICKLE_FX))
        struct.pack_into("<I", buf, 0, bm2n_probe.HTP_HDR_MAGIC_MULTI)
        res = bm2n_probe.probe_bytes(bytes(buf), "multi")
        self.assertEqual(res["family"], "pickle-multi")
        self.assertTrue(any("MULTI" in m for m in res["open"]))


# ---------------------------------------------------------------------------
# error diagnostics
# ---------------------------------------------------------------------------

class TestDiagnostics(unittest.TestCase):

    def test_bad_magic_reports_unrecognised_container(self):
        res = bm2n_probe.probe_file(BAD_MAGIC_FX)
        self.assertFalse(res["structural_ok"])
        self.assertIn("parse_error", res)
        self.assertGreaterEqual(len(res["violations"]), 4)

    def test_bad_constant_is_pinpointed(self):
        res = bm2n_probe.probe_file(BAD_CONST_FX)
        self.assertFalse(res["structural_ok"])
        self.assertEqual(len(res["violations"]), 1)
        self.assertIn("header[0x04]", res["violations"][0])
        self.assertIn("expected 0", res["violations"][0])

    def test_truncated_file_reports_bad_base_not_a_crash(self):
        res = bm2n_probe.probe_file(TRUNC_FX)
        self.assertFalse(res["structural_ok"])
        self.assertIn("base", " ".join(res["violations"]).lower())

    def test_parser_never_raises_on_random_input(self):
        import random
        rnd = random.Random(1234)
        for n in (0, 1, 4, 12, 44, 60, 100, 4096):
            blob = bytes(rnd.randrange(256) for _ in range(n))
            res = bm2n_probe.probe_bytes(blob, "rnd")
            self.assertIn("family", res)
            self.assertIn("structural_ok", res)

    def test_zero_byte_file_is_a_violation(self):
        res = bm2n_probe.probe_bytes(b"", "empty")
        self.assertFalse(res["structural_ok"])
        self.assertEqual(res["size"], 0)


# ---------------------------------------------------------------------------
# fleet diff
# ---------------------------------------------------------------------------

class TestFleetDiff(unittest.TestCase):

    def test_identical_file_is_100_percent(self):
        f = bm2n_probe.fleet_diff([BM2N14_FX, BM2N14_FX])
        pair = f["pairs"][0]
        self.assertEqual(pair["a"], pair["b"])
        self.assertEqual(pair["pct"], 100.0)
        self.assertEqual(pair["identical_bytes"], pair["common_prefix"])
        self.assertTrue(pair["same_md5"])

    def test_pair_count_and_prefix_math(self):
        files = [BM2N14_FX, BM2N06_FX, BM2N12_FX]
        f = bm2n_probe.fleet_diff(files)
        self.assertEqual(len(f["pairs"]), 3)          # C(3,2)
        for p in f["pairs"]:
            self.assertGreaterEqual(p["pct"], 0.0)
            self.assertLessEqual(p["pct"], 100.0)
            self.assertEqual(p["common_prefix"],
                             min(x["size"] for x in f["files"]
                                 if x["name"] in (p["a"], p["b"])))
            expect = round(100.0 * p["identical_bytes"] / p["common_prefix"], 2)
            self.assertEqual(p["pct"], expect)
            self.assertFalse(p["same_md5"])

    def test_different_sizes_are_flagged(self):
        f = bm2n_probe.fleet_diff([BM2N14_FX, BM2N06_FX])
        self.assertFalse(f["pairs"][0]["size_equal"])

    def test_fleet_files_carry_no_buffers(self):
        f = bm2n_probe.fleet_diff([BM2N14_FX, BM2N12_FX])
        for entry in f["files"]:
            self.assertNotIn("buf", entry)

    def test_same_content_different_name_is_full_identity(self):
        """F-75: identity follows content, not filename."""
        d = tmpdir()
        try:
            copy = os.path.join(d, "renamed_variant.bin")
            with open(BM2N14_FX, "rb") as src, open(copy, "wb") as dst:
                dst.write(src.read())
            f = bm2n_probe.fleet_diff([BM2N14_FX, copy])
            pair = f["pairs"][0]
            self.assertNotEqual(pair["a"], pair["b"])
            self.assertTrue(pair["same_md5"])
            self.assertEqual(pair["pct"], 100.0)
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)


# ---------------------------------------------------------------------------
# JSON + CLI contracts
# ---------------------------------------------------------------------------

class TestJsonContract(unittest.TestCase):

    def test_json_ready_handles_bytes_and_nesting(self):
        src = {"a": b"\x01\x02", "b": [b"\xff", {"c": b"x"}], "d": 1}
        out = bm2n_probe.json_ready(src)
        self.assertEqual(out["a"], "0102")
        self.assertEqual(out["b"][0], "ff")
        self.assertEqual(out["b"][1]["c"], "78")
        json.dumps(out)          # must not raise

    def test_probe_result_is_json_serialisable(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        json.dumps(bm2n_probe.json_ready(res))

    def test_required_top_level_keys(self):
        res = bm2n_probe.probe_file(BM2N14_FX)
        for key in ("path", "size", "md5", "sha256", "family", "header",
                    "segment_table", "segments", "prologue", "records",
                    "tail", "regions", "violations", "strings", "entropy",
                    "words", "open", "structural_ok"):
            self.assertIn(key, res)

    def test_hashes_match_the_file(self):
        buf = readf(BM2N14_FX)
        res = bm2n_probe.probe_file(BM2N14_FX)
        self.assertEqual(res["md5"], hashlib.md5(buf).hexdigest())
        self.assertEqual(res["sha256"], hashlib.sha256(buf).hexdigest())


class TestCliContract(unittest.TestCase):

    def test_brief_is_one_line_and_exit_zero(self):
        r = run_cli([BM2N14_FX, "--brief"])
        self.assertEqual(r.returncode, 0)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)
        self.assertIn("family=compact", lines[0])
        self.assertIn("OK", lines[0])

    def test_violation_exits_one(self):
        for f in (BAD_MAGIC_FX, BAD_CONST_FX, TRUNC_FX):
            r = run_cli([f, "--brief"])
            self.assertEqual(r.returncode, 1, f)

    def test_missing_file_exits_two(self):
        r = run_cli(["/nonexistent/bm2nXX.bin", "--brief"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a file", r.stderr)

    def test_fleet_mode_needs_two_files(self):
        r = run_cli([BM2N14_FX, "--fleet"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("at least two", r.stderr)

    def test_fleet_mode_output_and_exit(self):
        r = run_cli([BM2N14_FX, BM2N12_FX, "--fleet"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("FLEET DIFF", r.stdout)
        self.assertIn("100.0", run_cli([BM2N14_FX, BM2N14_FX,
                                        "--fleet"]).stdout)

    def test_json_file_written_and_valid(self):
        d = tmpdir()
        try:
            out = os.path.join(d, "res.json")
            r = run_cli([BM2N14_FX, "--json", out, "--brief"])
            self.assertEqual(r.returncode, 0)
            with open(out) as fh:
                data = json.load(fh)
            self.assertEqual(data["family"], "compact")
            self.assertEqual(data["size"], 103168)
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_json_fleet_mode_written(self):
        d = tmpdir()
        try:
            out = os.path.join(d, "fleet.json")
            r = run_cli([BM2N14_FX, BM2N12_FX, "--fleet", "--json", out])
            self.assertEqual(r.returncode, 0)
            with open(out) as fh:
                data = json.load(fh)
            self.assertEqual(len(data["pairs"]), 1)
            self.assertEqual(len(data["files"]), 2)
        finally:
            import shutil
            shutil.rmtree(d, ignore_errors=True)

    def test_full_text_report_sections(self):
        r = run_cli([BM2N14_FX])
        self.assertEqual(r.returncode, 0)
        for section in ("HEADER", "SEGMENT TABLE", "REGIONS", "PROLOGUE",
                        "RECORDS", "TAIL", "ENTROPY", "WORD HISTOGRAM",
                        "STRINGS", "STRUCTURAL VIOLATIONS: none", "[OPEN]"):
            self.assertIn(section, r.stdout)


# ---------------------------------------------------------------------------
# real payloads (skipped unless locally fetched)
# ---------------------------------------------------------------------------

@unittest.skipUnless(have_real_fleet(),
                     "real bm2n payloads not present locally")
class TestRealFleet(unittest.TestCase):
    """Live validation against the six brief payloads, when available.
    These are proprietary and git-ignored; the suite never depends on them."""

    @classmethod
    def setUpClass(cls):
        cls.results = {}
        for name in REAL_BRIEF:
            path = os.path.join(REAL_DIRS[0], name + ".bin")
            cls.results[name] = bm2n_probe.probe_file(path)

    def test_all_six_are_structurally_clean(self):
        for name, res in self.results.items():
            self.assertTrue(res["structural_ok"],
                            "%s: %s" % (name, res["violations"]))
            self.assertEqual(res["family"], "compact")

    def test_measured_header_values(self):
        expect = {
            "bm2n06": (2, 0x400000, 0x000B8900, "4bd22b0"),
            "bm2n08": (3, 0x200000, 0x002D1A00, "32da3bd"),
            "bm2n12": (3, 0x200000, 0x00064D00, "2c855d1"),
            "bm2n13_sm8350": (3, 0x200000, 0x00081A00, "2c855d1"),
            "bm2n14": (2, 0x200000, 0x00001000, "2a8527c"),
            "bm2n15": (3, 0x200000, 0x00081A00, "5371806"),
        }
        for name, (n, window, base, build) in expect.items():
            h = self.results[name]["header"]
            self.assertEqual(h["count"], n, name)
            self.assertEqual(h["window"], window, name)
            self.assertEqual(h["base"], base, name)
            self.assertEqual(h["build_id"], build, name)

    def test_record_counts_and_terminators(self):
        expect = {"bm2n06": 781, "bm2n08": 1227, "bm2n12": 17241,
                  "bm2n13_sm8350": 4348, "bm2n14": 885, "bm2n15": 4348}
        for name, n in expect.items():
            res = self.results[name]
            self.assertEqual(res["records"]["count"], n, name)
            self.assertEqual(res["tail"]["terminator"], "0xbeeff00d", name)

    def test_bm2n13_and_bm2n15_share_a_version_stable_prologue(self):
        """Own measurement: the prologue is 100% identical between these two
        variants even though the bodies differ."""
        a = readf(os.path.join(REAL_DIRS[0], "bm2n13_sm8350.bin"))
        b = readf(os.path.join(REAL_DIRS[0], "bm2n15.bin"))
        pa = self.results["bm2n13_sm8350"]["prologue"]
        pb = self.results["bm2n15"]["prologue"]
        self.assertEqual(pa["length"], pb["length"])
        self.assertEqual(a[pa["start"]:pa["end"]], b[pb["start"]:pb["end"]])
        self.assertNotEqual(
            a[self.results["bm2n13_sm8350"]["records"]["first"]:][:4096],
            b[self.results["bm2n15"]["records"]["first"]:][:4096])

    def test_fleet_diff_matrix_percentages(self):
        pairs = {
            ("bm2n06", "bm2n08"): 7.18, ("bm2n06", "bm2n12"): 32.68,
            ("bm2n06", "bm2n13_sm8350"): 32.83,
            ("bm2n06", "bm2n14"): 4.64, ("bm2n06", "bm2n15"): 32.45,
            ("bm2n08", "bm2n12"): 17.25, ("bm2n08", "bm2n13_sm8350"): 13.50,
            ("bm2n08", "bm2n14"): 4.71, ("bm2n08", "bm2n15"): 13.72,
            ("bm2n12", "bm2n13_sm8350"): 41.77,
            ("bm2n12", "bm2n14"): 40.42, ("bm2n12", "bm2n15"): 42.22,
            ("bm2n13_sm8350", "bm2n14"): 39.83,
            ("bm2n13_sm8350", "bm2n15"): 47.25,
            ("bm2n14", "bm2n15"): 39.94,
        }
        paths = [os.path.join(REAL_DIRS[0], n + ".bin") for n in REAL_BRIEF]
        f = bm2n_probe.fleet_diff(paths)
        got = {}
        for p in f["pairs"]:
            a, b = p["a"][:-4], p["b"][:-4]
            got[(a, b)] = p["pct"]
            got[(b, a)] = p["pct"]
        for key, want in pairs.items():
            self.assertAlmostEqual(got[key], want, delta=0.02,
                                   msg="%s vs %s" % key)

    def test_bm2n13_filename_is_not_identity(self):
        """F-75: 2d267761.. (bm2n13_sm8350) and 5371806-build variants are
        genuinely distinct payloads, not a mismatch failure."""
        res = self.results["bm2n13_sm8350"]
        self.assertEqual(res["md5"], "2d267761f3291c9ca4a7850ab0ef1966")
        self.assertEqual(res["size"], 1082824)
        self.assertNotEqual(res["md5"], self.results["bm2n15"]["md5"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
