#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_cpp_probe.py -- unittest suite for the clean-room Qualcomm MSM CPP
firmware analyser (``cpp_probe.py``), driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written 2026-11-19 from public sources only: the GPL-2.0-only kernel
consumer ``msm_cpp.c``/``msm_cpp.h`` (LineageOS/android_kernel_xiaomi_msm8953
@ lineage-21) and the userspace producer ``cpp_hardware.c`` /
``cpp_hw_params.h`` (Sushrut1101/android_vendor_qcom_proprietary), plus this
session's own structural measurements of the payload bytes. No decompiled
code and no proprietary documentation were used. Fixture bytes are self-made
from the measured layout only (``make_fixture.py``); no vendor payload is
committed or read by this suite except opportunistically behind a skip guard.

Run from this directory:

    python3 -m unittest -v test_cpp_probe

Covers: fixture existence/determinism/size fidelity, the fixed-window check
(exact 16 KiB and the 16,128 B outlier), the header/vector-table probe, the
ASCII version-string scan (including the honest "no self-version string"
result), the numeric version-marker rule, protocol-magic detection, padding
characterisation (0xFF fill, epilogue, trailing fill), the entropy profile
shape, adjacent-version first-diff, the N x N matrix math (all three
variants), malformed/truncated input diagnostics, the CLI and JSON contracts,
exit statuses, and fixture determinism.
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

import cpp_probe
import make_fixture

FIX = os.path.join(HERE, "fixtures")

# The ladder, in the semantic order the real fleet uses.
LADDER = [
    "cpp_firmware_v1_1_1.fw",
    "cpp_firmware_v1_1_6.fw",
    "cpp_firmware_v1_2_0.fw",
    "cpp_firmware_v1_4_0.fw",
    "cpp_firmware_v1_5_0.fw",
    "cpp_firmware_v1_5_1.fw",
    "cpp_firmware_v1_5_2.fw",
    "cpp_firmware_v1_6_0.fw",
    "cpp_firmware_v1_8_0.fw",
    "cpp_firmware_v1_10_0.fw",
    "cpp_firmware_v1_12_0.fw",
    "cpp_firmware_v1_12_1.fw",
]
BAD_SIZE = "bad_size_synthetic.fw"
TRUNCATED = "truncated_synthetic.fw"
ALL_FILL = "all_fill_synthetic.fw"

LADDER_PATHS = [os.path.join(FIX, n) for n in LADDER]
BAD_SIZE_PATH = os.path.join(FIX, BAD_SIZE)
TRUNCATED_PATH = os.path.join(FIX, TRUNCATED)
ALL_FILL_PATH = os.path.join(FIX, ALL_FILL)


def ensure_fixtures():
    """Materialise fixtures if absent (they are git-ignored by design)."""
    if not all(os.path.isfile(p) for p in LADDER_PATHS +
               [BAD_SIZE_PATH, TRUNCATED_PATH, ALL_FILL_PATH]):
        make_fixture.build_all(FIX, verbose=False)


def read(path):
    with open(path, "rb") as f:
        return f.read()


# ---------------------------------------------------------------- fixtures

class TestFixtures(unittest.TestCase):
    """The fixtures exist, are the documented sizes, and are reproducible."""

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_all_fixtures_present(self):
        for p in LADDER_PATHS + [BAD_SIZE_PATH, TRUNCATED_PATH, ALL_FILL_PATH]:
            self.assertTrue(os.path.isfile(p), "missing fixture %s" % p)

    def test_ladder_sizes(self):
        for name in LADDER:
            data = read(os.path.join(FIX, name))
            if name == "cpp_firmware_v1_1_1.fw":
                self.assertEqual(len(data), cpp_probe.SHORT_WINDOW_BYTES)
            else:
                self.assertEqual(len(data), cpp_probe.WINDOW_BYTES)

    def test_determinism(self):
        """Rebuilding must reproduce every byte, so fixtures are regenerable."""
        before = {n: hashlib.md5(read(os.path.join(FIX, n))).hexdigest()
                  for n in LADDER + [BAD_SIZE, TRUNCATED, ALL_FILL]}
        make_fixture.build_all(FIX, verbose=False)
        after = {n: hashlib.md5(read(os.path.join(FIX, n))).hexdigest()
                 for n in LADDER + [BAD_SIZE, TRUNCATED, ALL_FILL]}
        self.assertEqual(before, after)

    def test_build_image_pure_function(self):
        """Same arguments -> same bytes, with no dependence on prior state."""
        a = make_fixture.build_image(1, 5, 1, 16384, 0x1A5E)
        b = make_fixture.build_image(1, 5, 1, 16384, 0x1A5E)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16384)

    def test_fixtures_carry_no_vendor_bytes(self):
        """A synthetic fixture must not equal any real fleet identity.

        The real md5s are recorded in the analysis document; none may match.
        This is the guard that keeps a vendor blob out of the repo.
        """
        real_md5 = {
            "4d145d5a13a3956bf33aec94a8e7fe62",   # v1_1_1
            "738a83a673dd45fa5852b5cc9519ee94",   # v1_1_6
            "3f078c3d1658679a762f7d77c99517cd",   # v1_2_0
            "b6f54efc4675040f7b7e99398905646e",   # v1_4_0
            "e51087ba19409150103faafaff849627",   # v1_5_0
            "ed1f2071b61447924f50fe8670cd51be",   # v1_5_1
            "02e4044179d7dfc069aa9a42db690642",   # v1_5_2
            "de85a5f8196ec73cffc61382b3e0d5f6",   # v1_6_0
            "04423a29e78bb01d9be62256a65354a6",   # v1_8_0
            "8d08bfdf92db5b1df58af9b6adf61eae",   # v1_10_0
            "ef031a3f24f877242621ba695d8dcbd2",   # v1_12_0
            "a59e732fcbf71cb5fcc6c54fef0124d6",   # v1_12_1
        }
        for name in LADDER:
            md5 = hashlib.md5(read(os.path.join(FIX, name))).hexdigest()
            self.assertNotIn(md5, real_md5,
                             "%s accidentally reproduces a real vendor blob"
                             % name)


# ---------------------------------------------------------------- window

class TestFixedWindow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_exact_window(self):
        rep = cpp_probe.Report()
        info = cpp_probe.check_window(read(LADDER_PATHS[1]), rep)
        self.assertTrue(info["is_exact_window"])
        self.assertFalse(info["is_short_window"])
        self.assertEqual(info["download_words"], 4096)
        self.assertFalse(rep.has_errors)

    def test_short_window_outlier(self):
        rep = cpp_probe.Report()
        info = cpp_probe.check_window(read(LADDER_PATHS[0]), rep)
        self.assertFalse(info["is_exact_window"])
        self.assertTrue(info["is_short_window"])
        self.assertEqual(info["bytes"], 16128)
        self.assertEqual(info["download_words"], 4032)
        codes = [i["code"] for i in rep.items]
        self.assertIn("fixed-window-short", codes)

    def test_not_word_aligned_is_error(self):
        rep = cpp_probe.Report()
        info = cpp_probe.check_window(read(BAD_SIZE_PATH), rep)
        self.assertFalse(info["multiple_of_4"])
        self.assertTrue(rep.has_errors)
        self.assertIn("not-word-aligned", [i["code"] for i in rep.items])

    def test_window_constants(self):
        self.assertEqual(cpp_probe.WINDOW_BYTES, 16384)
        self.assertEqual(cpp_probe.SHORT_WINDOW_BYTES, 16128)


# ---------------------------------------------------------------- header

class TestHeaderProbe(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_lead_word(self):
        h = cpp_probe.probe_header(read(LADDER_PATHS[5]))
        self.assertTrue(h["available"])
        self.assertEqual(h["lead_word_u16"], "0x7140")
        self.assertTrue(h["lead_word_constant_across_fleet"])

    def test_vector_table_shape(self):
        h = cpp_probe.probe_header(read(LADDER_PATHS[5]))
        vt = h["vector_table"]
        self.assertEqual(vt["offset"], 2)
        self.assertEqual(vt["count"], 16)
        self.assertEqual(vt["end_offset"], 0x22)
        self.assertEqual(len(vt["values"]), 16)
        # MEASURED: the real table is NOT all even (slot 15 is odd in 10/12
        # files, slot 9 in 9/12), so the probe must report parity, not assume
        # it. The fixtures model that: slots 9 and 15 are odd.
        self.assertFalse(vt["all_even"])
        self.assertEqual(vt["odd_slots"], [9, 15])
        self.assertGreaterEqual(vt["distinct_count"], 2)

    def test_vectors_land_below_code_end(self):
        """Every vector, doubled, must sit inside the image."""
        for p in LADDER_PATHS:
            data = read(p)
            h = cpp_probe.probe_header(data)
            mx = int(h["vector_table"]["max"], 16)
            self.assertLess(mx * 2, len(data),
                            "%s vector table escapes the file" % p)

    def test_short_file_has_no_header(self):
        h = cpp_probe.probe_header(b"\xff" * 8)
        self.assertFalse(h["available"])


# ---------------------------------------------------------------- version

class TestVersionDetection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_parse_version_from_name(self):
        self.assertEqual(
            cpp_probe.parse_version_from_name("cpp_firmware_v1_12_0.fw"),
            (1, 12, 0))
        self.assertEqual(
            cpp_probe.parse_version_from_name("/a/b/cpp_firmware_v1_5_2.fw"),
            (1, 5, 2))
        self.assertIsNone(cpp_probe.parse_version_from_name("firmware.bin"))
        self.assertIsNone(cpp_probe.parse_version_from_name("cpp_firmware_v1.fw"))

    def test_version_marker_word_bcd(self):
        """The marker is 0x1000 | BCD(minor); 10 and 12 must not collide."""
        self.assertEqual(cpp_probe.version_marker_word(1, 1, 0), 0x1001)
        self.assertEqual(cpp_probe.version_marker_word(1, 2, 0), 0x1002)
        self.assertEqual(cpp_probe.version_marker_word(1, 10, 0), 0x1010)
        self.assertEqual(cpp_probe.version_marker_word(1, 12, 0), 0x1012)
        self.assertNotEqual(cpp_probe.version_marker_word(1, 1, 0),
                            cpp_probe.version_marker_word(1, 10, 0))

    def test_marker_present_in_every_ladder_entry(self):
        for p in LADDER_PATHS:
            rep = cpp_probe.Report()
            vm = cpp_probe.scan_version_marker(read(p), p, rep)
            self.assertTrue(vm["marker_present"],
                            "%s has no version marker" % p)
            self.assertTrue(vm["marker_offsets"])
            # markers must be 16-bit aligned
            for off in vm["marker_offsets"]:
                self.assertEqual(off % 2, 0)

    def test_marker_matches_filename_minor(self):
        for p in LADDER_PATHS:
            ver = cpp_probe.parse_version_from_name(p)
            rep = cpp_probe.Report()
            vm = cpp_probe.scan_version_marker(read(p), p, rep)
            self.assertEqual(vm["marker_word"],
                             "0x%04x" % cpp_probe.version_marker_word(*ver))

    def test_enum_values_match_public_header(self):
        """Spot-check the CPP_FW_VERSION_* constants against the enum."""
        self.assertEqual(cpp_probe.fw_version_word(1, 12, 1), 0x100C0001)
        self.assertEqual(cpp_probe.fw_version_word(1, 10, 0), 0x100A0000)
        self.assertEqual(cpp_probe.fw_version_word(1, 1, 6), 0x10010006)
        self.assertEqual(cpp_probe.KNOWN_FW_VERSIONS[(1, 12, 0)], 0x100C0000)

    def test_no_ascii_self_version_string(self):
        """The honest negative: the images carry no ASCII version of themselves."""
        for p in LADDER_PATHS:
            vs = cpp_probe.scan_version_strings(read(p))
            self.assertFalse(vs["self_version_string_present"])

    def test_epilogue_v1_1_literal_is_not_a_version_field(self):
        """'v1.1' appears in the shared epilogue at 0x3f80 regardless of version."""
        for p in LADDER_PATHS[1:]:          # every file that has the epilogue
            data = read(p)
            self.assertEqual(data[0x3F80:0x3F84], b"v1.1")
            vs = cpp_probe.scan_version_strings(data)
            hits = [h for h in vs["version_like"] if h["text"] == "v1.1"]
            self.assertEqual(len(hits), 1)
            self.assertEqual(hits[0]["offset"], 0x3F80)

    def test_marker_absent_reports_info_not_error(self):
        """A file with no marker must be reported, not guessed at."""
        rep = cpp_probe.Report()
        vm = cpp_probe.scan_version_marker(b"\xff" * 4096,
                                           "/tmp/cpp_firmware_v1_9_9.fw", rep)
        self.assertFalse(vm["marker_present"])
        self.assertFalse(rep.has_errors)
        self.assertIn("version-marker-absent", [i["code"] for i in rep.items])

    def test_unknown_version_not_in_enum(self):
        rep = cpp_probe.Report()
        cpp_probe.scan_version_marker(b"\xff" * 4096,
                                      "cpp_firmware_v9_9_9.fw", rep)
        self.assertIn("version-not-in-enum", [i["code"] for i in rep.items])


# ---------------------------------------------------------------- magics

class TestProtocolMagics(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_magics_found_in_fixtures(self):
        m = cpp_probe.scan_protocol_magics(read(LADDER_PATHS[5]))
        self.assertIn("MSM_CPP_MSG_ID_CMD", m)
        self.assertIn("MSM_CPP_MSG_ID_TRAILER", m)
        self.assertIn("MSM_CPP_MSG_ID_OK", m)

    def test_magic_values_from_header(self):
        """The three needles must be the msm_cpp.h values."""
        self.assertEqual(cpp_probe.MSG_ID_CMD, 0x3E646D63)
        self.assertEqual(cpp_probe.MSG_ID_OK, 0x0A0A4B4F)
        self.assertEqual(cpp_probe.MSG_ID_TRAILER, 0xABCDEFAA)

    def test_no_magic_in_fill(self):
        self.assertEqual(cpp_probe.scan_protocol_magics(b"\xff" * 1024), {})


# ---------------------------------------------------------------- padding

class TestPadding(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_fill_byte_is_ff_not_zero(self):
        rep = cpp_probe.Report()
        p = cpp_probe.characterise_padding(read(LADDER_PATHS[5]), rep)
        self.assertEqual(p["fill_byte"], "0xff")
        self.assertTrue(p["fill_is_erased_flash"])
        self.assertFalse(p["zero_fill_used"])

    def test_fill_region_accounting(self):
        """code_end + fill_after_code_end must reach the epilogue."""
        rep = cpp_probe.Report()
        p = cpp_probe.characterise_padding(read(LADDER_PATHS[5]), rep)
        self.assertEqual(p["code_end"] + p["fill_after_code_end"],
                         cpp_probe.EPILOGUE_START)

    def test_epilogue_present_and_invariant(self):
        rep = cpp_probe.Report()
        a = cpp_probe.characterise_padding(read(LADDER_PATHS[5]), rep)["epilogue"]
        b = cpp_probe.characterise_padding(read(LADDER_PATHS[10]), rep)["epilogue"]
        self.assertTrue(a["present"])
        self.assertEqual(a["sha1"], b["sha1"],
                         "the epilogue must be identical across the ladder")
        self.assertEqual(a["len"], 204)

    def test_short_window_has_no_epilogue(self):
        rep = cpp_probe.Report()
        p = cpp_probe.characterise_padding(read(LADDER_PATHS[0]), rep)
        self.assertFalse(p["epilogue"]["present"])

    def test_trailing_fill_block(self):
        rep = cpp_probe.Report()
        p = cpp_probe.characterise_padding(read(LADDER_PATHS[5]), rep)
        tf = p["trailing_fill_block"]
        self.assertIsNotNone(tf)
        self.assertTrue(tf["all_fill"])
        self.assertEqual(tf["offset"], 0x3FCA)
        self.assertEqual(tf["len"], 16384 - 0x3FCA)

    def test_content_islands_are_inside_the_file(self):
        rep = cpp_probe.Report()
        p = cpp_probe.characterise_padding(read(LADDER_PATHS[10]), rep)
        for isl in p["content_islands"]:
            self.assertGreaterEqual(isl["start"], 0)
            self.assertLessEqual(isl["end"], 16384)
            self.assertEqual(isl["len"], isl["end"] - isl["start"])

    def test_all_fill_image_is_an_error(self):
        rep = cpp_probe.Report()
        cpp_probe.characterise_padding(read(ALL_FILL_PATH), rep)
        self.assertTrue(rep.has_errors)
        self.assertIn("all-fill-image", [i["code"] for i in rep.items])

    def test_find_fill_runs(self):
        data = b"\x00" * 4 + b"\xff" * 32 + b"\x00" * 4
        runs = cpp_probe.find_fill_runs(data, 0xFF, min_len=16)
        self.assertEqual(runs, [(4, 36, 32)])

    def test_find_fill_runs_respects_min_len(self):
        data = b"\xff" * 8 + b"\x00" * 8
        self.assertEqual(cpp_probe.find_fill_runs(data, 0xFF, min_len=16), [])


# ---------------------------------------------------------------- trailer

class TestTrailer(unittest.TestCase):
    """The u16 at 0x3efc is a halfword count: code_end == 2*(field+1)."""

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_exact_field_is_a_halfword_count(self):
        for name in ("cpp_firmware_v1_2_0.fw", "cpp_firmware_v1_4_0.fw",
                     "cpp_firmware_v1_5_0.fw", "cpp_firmware_v1_5_1.fw",
                     "cpp_firmware_v1_5_2.fw", "cpp_firmware_v1_6_0.fw"):
            d = read(os.path.join(FIX, name))
            ce = cpp_probe.code_end_of(d)
            tr = cpp_probe.probe_trailer(d, ce)
            self.assertFalse(tr["erased"], name)
            self.assertTrue(tr["exact"], name)
            self.assertEqual(tr["implied_end"], ce, name)
            self.assertEqual(tr["residual_after_implied_end"], 0, name)

    def test_field_is_not_the_file_length(self):
        """The field describes a region, not the 16 KiB window."""
        d = read(os.path.join(FIX, "cpp_firmware_v1_5_0.fw"))
        ce = cpp_probe.code_end_of(d)
        tr = cpp_probe.probe_trailer(d, ce)
        self.assertNotEqual(tr["implied_end"], len(d))
        self.assertLess(tr["implied_end"], len(d))

    def test_erased_field_reported_not_guessed(self):
        for name in ("cpp_firmware_v1_1_1.fw", "cpp_firmware_v1_1_6.fw",
                     "cpp_firmware_v1_8_0.fw"):
            d = read(os.path.join(FIX, name))
            tr = cpp_probe.probe_trailer(d, cpp_probe.code_end_of(d))
            self.assertTrue(tr["erased"], name)
            self.assertEqual(tr["field_u16"], "0xffff", name)
            self.assertFalse(tr["exact"], name)

    def test_stride_block_residual(self):
        """The three later identities append a 176-byte fixed-stride block."""
        for name in ("cpp_firmware_v1_10_0.fw", "cpp_firmware_v1_12_0.fw",
                     "cpp_firmware_v1_12_1.fw"):
            d = read(os.path.join(FIX, name))
            tr = cpp_probe.probe_trailer(d, cpp_probe.code_end_of(d))
            self.assertFalse(tr["erased"], name)
            self.assertFalse(tr["exact"], name)
            self.assertEqual(tr["residual_after_implied_end"],
                             make_fixture.STRIDE_BLOCK_LEN, name)
            sb = tr["stride_block"]
            self.assertTrue(sb["available"], name)
            self.assertEqual(sb["record_count"], 8, name)
            self.assertEqual(sb["record_len"], 20, name)
            self.assertEqual(sb["prologue_len"], 14, name)
            self.assertTrue(sb["bodies_identical"], name)
            self.assertEqual(sb["a_step"], 0x0A, name)
            self.assertEqual(sb["b_step"], 8, name)

    def test_stride_block_absent_when_field_is_exact(self):
        d = read(os.path.join(FIX, "cpp_firmware_v1_5_0.fw"))
        tr = cpp_probe.probe_trailer(d, cpp_probe.code_end_of(d))
        self.assertNotIn("stride_block", tr)

    def test_stride_block_out_of_range(self):
        sb = cpp_probe.probe_stride_block(b"\xff" * 64, 32, 176)
        self.assertFalse(sb["available"])

    def test_trailer_short_file(self):
        tr = cpp_probe.probe_trailer(b"\xff" * 16, 16)
        self.assertFalse(tr["available"])
        self.assertIn("reason", tr)


# ---------------------------------------------------------------- entropy

class TestEntropy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_entropy_bounds(self):
        self.assertEqual(cpp_probe.entropy(b""), 0.0)
        self.assertEqual(cpp_probe.entropy(b"\x00" * 100), 0.0)
        self.assertAlmostEqual(cpp_probe.entropy(bytes(range(256))), 8.0,
                               places=6)

    def test_profile_shape(self):
        e = cpp_probe.entropy_profile(read(LADDER_PATHS[5]), block=1024)
        self.assertEqual(len(e["blocks"]), 16)
        self.assertEqual(e["blocks"][0]["offset"], 0)
        self.assertEqual(sum(b["len"] for b in e["blocks"]), 16384)
        for b in e["blocks"]:
            self.assertGreaterEqual(b["entropy"], 0.0)
            self.assertLessEqual(b["entropy"], 8.0)

    def test_fill_regions_have_zero_entropy(self):
        e = cpp_probe.entropy_profile(read(LADDER_PATHS[5]), block=1024)
        tail = e["regions"]["tail[0x3fca,end)"]
        self.assertEqual(tail["entropy"], 0.0)
        self.assertEqual(tail["ff_pct"], 100.0)

    def test_code_region_entropy_is_sub_maximal(self):
        """Real code regions sit well below 8.0 bits/byte; fixtures must too."""
        e = cpp_probe.entropy_profile(read(LADDER_PATHS[10]))
        cr = e["regions"]["code[0x22,%d)" % cpp_probe.CODE_REGION_END]
        self.assertLess(cr["entropy"], 8.0)
        self.assertGreater(cr["entropy"], 0.5)

    def test_block_stats(self):
        s = cpp_probe.block_stats(b"\xff" * 10 + b"\x00" * 10)
        self.assertEqual(s["len"], 20)
        self.assertEqual(s["ff_pct"], 50.0)
        self.assertEqual(s["zero_pct"], 50.0)
        self.assertEqual(s["distinct_bytes"], 2)


# ---------------------------------------------------------------- diff

class TestFirstDiff(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_first_diff_basic(self):
        self.assertEqual(cpp_probe.first_diff(b"abcd", b"abcd"), None)
        self.assertEqual(cpp_probe.first_diff(b"abcd", b"abXd"), 2)
        self.assertEqual(cpp_probe.first_diff(b"abc", b"abcdef"), 3)

    def test_diff_runs(self):
        runs = cpp_probe.diff_runs(b"aabbcc", b"aXbYcc")
        self.assertEqual(runs, [[1, 1], [3, 3]])

    def test_diff_runs_merges_adjacent(self):
        runs = cpp_probe.diff_runs(b"aaaa", b"aXXa")
        self.assertEqual(runs, [[1, 2]])

    def test_adjacent_diff_1_5_0_to_1_5_1(self):
        """The step delta is tiny and starts at a low offset."""
        d = cpp_probe.adjacent_diffs(
            [os.path.join(FIX, "cpp_firmware_v1_5_0.fw"),
             os.path.join(FIX, "cpp_firmware_v1_5_1.fw")])
        self.assertEqual(len(d), 1)
        self.assertLess(d[0]["differing_bytes"], 64,
                        "a step bump should not rewrite the image")
        self.assertIsNotNone(d[0]["first_diff_offset"])

    def test_adjacent_diff_across_major_minor_is_large(self):
        d = cpp_probe.adjacent_diffs(
            [os.path.join(FIX, "cpp_firmware_v1_5_2.fw"),
             os.path.join(FIX, "cpp_firmware_v1_6_0.fw")])
        self.assertGreater(d[0]["differing_bytes"], 1000)

    def test_first_diff_offset_is_reported_in_hex(self):
        d = cpp_probe.adjacent_diffs(
            [os.path.join(FIX, "cpp_firmware_v1_5_0.fw"),
             os.path.join(FIX, "cpp_firmware_v1_5_1.fw")])
        self.assertTrue(d[0]["first_diff_offset_hex"].startswith("0x"))


# ---------------------------------------------------------------- matrix

class TestMatrix(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()
        cls.m = cpp_probe.build_matrix(
            LADDER_PATHS,
            labeler=lambda p: "%d.%d.%d" % cpp_probe.parse_version_from_name(p))

    def test_dimensions(self):
        n = len(LADDER_PATHS)
        for key in ("matrix_whole", "matrix_code_region",
                    "matrix_content_only"):
            mat = self.m[key]
            self.assertEqual(len(mat), n)
            for row in mat:
                self.assertEqual(len(row), n)
        self.assertEqual(len(self.m["labels"]), n)

    def test_diagonal_is_100(self):
        for key in ("matrix_whole", "matrix_code_region",
                    "matrix_content_only"):
            for i, row in enumerate(self.m[key]):
                self.assertEqual(row[i], 100.0)

    def test_symmetry(self):
        for key in ("matrix_whole", "matrix_code_region",
                    "matrix_content_only"):
            mat = self.m[key]
            n = len(mat)
            for i in range(n):
                for j in range(n):
                    self.assertAlmostEqual(mat[i][j], mat[j][i], places=6,
                                           msg="%s not symmetric at %d,%d"
                                               % (key, i, j))

    def test_values_in_range(self):
        for key in ("matrix_whole", "matrix_code_region",
                    "matrix_content_only"):
            for row in self.m[key]:
                for v in row:
                    self.assertGreaterEqual(v, 0.0)
                    self.assertLessEqual(v, 100.0)

    def test_whole_is_inflated_vs_content(self):
        """Padding must inflate whole-file identity: the core honesty check."""
        lab = self.m["labels"]
        i = lab.index("1.5.0")
        j = lab.index("1.6.0")
        whole = self.m["matrix_whole"][i][j]
        content = self.m["matrix_content_only"][i][j]
        self.assertGreater(whole, content,
                           "shared 0xFF fill should raise whole-file identity")

    def test_step_pair_is_near_identical(self):
        lab = self.m["labels"]
        i, j = lab.index("1.5.0"), lab.index("1.5.1")
        self.assertGreater(self.m["matrix_whole"][i][j], 99.0)
        self.assertGreater(self.m["matrix_content_only"][i][j], 99.0)

    def test_short_window_file_is_least_similar(self):
        """1.1.1 is the structural outlier; it must be the odd one out."""
        lab = self.m["labels"]
        i = lab.index("1.1.1")
        row = self.m["matrix_content_only"][i]
        others = [v for k, v in enumerate(row) if k != i]
        self.assertLess(max(others), 95.0)

    def test_identity_functions(self):
        a = b"abcdef"
        b = b"abcXef"
        r = cpp_probe.same_offset_identity(a, b)
        self.assertEqual(r["identical_bytes"], 5)
        self.assertAlmostEqual(r["identity_pct"], 83.33, places=2)
        r2 = cpp_probe.same_offset_identity_excluding_fill(
            b"\xff\x01\x02", b"\xff\x01\x03")
        # position 0 excluded (fill on both), 1 same, 2 different
        self.assertEqual(r2["positions"], 2)
        self.assertEqual(r2["identical_bytes"], 1)

    def test_empty_identity(self):
        self.assertEqual(
            cpp_probe.same_offset_identity(b"", b"")["identity_pct"], 0.0)
        self.assertEqual(
            cpp_probe.same_offset_identity_excluding_fill(b"", b"")["positions"],
            0)


# ---------------------------------------------------------------- malformed

class TestMalformedInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_missing_file(self):
        doc, status = cpp_probe.probe_file("/nonexistent/nope.fw")
        self.assertEqual(status, 1)
        self.assertIn("error", doc)
        self.assertEqual(doc["diagnostics"][0]["code"], "io-error")

    def test_truncated_file(self):
        doc, status = cpp_probe.probe_file(TRUNCATED_PATH)
        self.assertEqual(status, 1)
        codes = [d["code"] for d in doc["diagnostics"]]
        self.assertIn("file-too-small", codes)

    def test_bad_size_file(self):
        doc, status = cpp_probe.probe_file(BAD_SIZE_PATH)
        self.assertEqual(status, 1)
        codes = [d["code"] for d in doc["diagnostics"]]
        self.assertIn("not-word-aligned", codes)

    def test_all_fill_file(self):
        doc, status = cpp_probe.probe_file(ALL_FILL_PATH)
        self.assertEqual(status, 1)
        codes = [d["code"] for d in doc["diagnostics"]]
        self.assertIn("all-fill-image", codes)

    def test_good_file_exits_zero(self):
        doc, status = cpp_probe.probe_file(LADDER_PATHS[5])
        self.assertEqual(status, 0)
        self.assertFalse([d for d in doc["diagnostics"]
                          if d["class"] == "error"])

    def test_probe_file_has_expected_keys(self):
        doc, _ = cpp_probe.probe_file(LADDER_PATHS[5])
        for k in ("file", "basename", "bytes", "md5", "sha256",
                  "fixed_window", "header", "version_strings",
                  "version_marker", "protocol_magics", "padding", "entropy",
                  "family", "diagnostics"):
            self.assertIn(k, doc)


# ---------------------------------------------------------------- CLI

class TestCLI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, "-I", os.path.join(HERE, "cpp_probe.py")] + list(args),
            capture_output=True, text=True)

    def test_brief(self):
        r = self._run(LADDER_PATHS[5], "--brief")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("cpp_firmware_v1_5_1.fw", r.stdout)
        self.assertIn("window:", r.stdout)
        self.assertIn("version:", r.stdout)
        self.assertIn("layout:", r.stdout)

    def test_json_output(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "o.json")
            r = self._run(LADDER_PATHS[5], "--json", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out) as f:
                doc = json.load(f)
            self.assertEqual(doc["basename"], "cpp_firmware_v1_5_1.fw")
            self.assertTrue(doc["fixed_window"]["is_exact_window"])

    def test_json_to_stdout(self):
        r = self._run(LADDER_PATHS[5])
        self.assertEqual(r.returncode, 0, r.stderr)
        doc = json.loads(r.stdout)
        self.assertEqual(doc["bytes"], 16384)

    def test_exit_status_on_bad_file(self):
        r = self._run(BAD_SIZE_PATH, "--brief")
        self.assertEqual(r.returncode, 1)

    def test_help(self):
        r = self._run("--help")
        self.assertEqual(r.returncode, 2)
        self.assertIn("CLEAN-ROOM", r.stdout)

    def test_no_args(self):
        r = self._run()
        self.assertEqual(r.returncode, 2)

    def test_matrix_cli(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "m.json")
            r = self._run("--matrix", *LADDER_PATHS[:4], "--json", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out) as f:
                m = json.load(f)
            self.assertEqual(len(m["labels"]), 4)
            self.assertEqual(len(m["matrix_whole"]), 4)
            for row in m["matrix_whole"]:
                self.assertEqual(len(row), 4)

    def test_versions_cli(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "v.json")
            r = self._run("--versions",
                          os.path.join(FIX, "cpp_firmware_v1_5_0.fw"),
                          os.path.join(FIX, "cpp_firmware_v1_5_1.fw"),
                          "--json", out)
            self.assertEqual(r.returncode, 0, r.stderr)
            with open(out) as f:
                doc = json.load(f)
            self.assertEqual(len(doc["files"]), 2)
            self.assertEqual(len(doc["adjacent_diffs"]), 1)
            self.assertEqual(doc["adjacent_diffs"][0]["a"], "1.5.0")
            self.assertEqual(doc["adjacent_diffs"][0]["b"], "1.5.1")

    def test_versions_brief(self):
        r = self._run("--versions", "--brief",
                      os.path.join(FIX, "cpp_firmware_v1_5_0.fw"),
                      os.path.join(FIX, "cpp_firmware_v1_5_1.fw"))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("first diff", r.stdout)


# ---------------------------------------------------------------- real fleet

REAL_DIRS = ("/tmp/astro_u/cpp/real", "/tmp/astro_u/cpp/payloads")
REAL_BRIEF = [
    "v1_1_1", "v1_1_6", "v1_2_0", "v1_4_0", "v1_5_0", "v1_5_1",
    "v1_5_2", "v1_6_0", "v1_8_0", "v1_10_0", "v1_12_0", "v1_12_1",
]


def real_payload_dir():
    for d in REAL_DIRS:
        if all(os.path.isfile(os.path.join(d, "cpp_firmware_%s.fw" % v))
               for v in REAL_BRIEF):
            return d
    return None


@unittest.skipUnless(real_payload_dir(),
                     "real cpp_firmware payloads not present locally")
class TestRealFleet(unittest.TestCase):
    """Live validation against the twelve fetched identities.

    These are proprietary vendor bytes and are never committed; the suite
    runs without them. When they are present, the measured claims in
    ``cpp-version-matrix-analysis.md`` are asserted directly.
    """

    @classmethod
    def setUpClass(cls):
        cls.dir = real_payload_dir()
        cls.paths = [os.path.join(cls.dir, "cpp_firmware_%s.fw" % v)
                     for v in REAL_BRIEF]
        cls.docs = {}
        for v, p in zip(REAL_BRIEF, cls.paths):
            doc, _ = cpp_probe.probe_file(p)
            cls.docs[v] = doc

    def test_md5_matches_the_database(self):
        expect = {
            "v1_1_1": "4d145d5a13a3956bf33aec94a8e7fe62",
            "v1_1_6": "738a83a673dd45fa5852b5cc9519ee94",
            "v1_2_0": "3f078c3d1658679a762f7d77c99517cd",
            "v1_4_0": "b6f54efc4675040f7b7e99398905646e",
            "v1_5_0": "e51087ba19409150103faafaff849627",
            "v1_5_1": "ed1f2071b61447924f50fe8670cd51be",
            "v1_5_2": "02e4044179d7dfc069aa9a42db690642",
            "v1_6_0": "de85a5f8196ec73cffc61382b3e0d5f6",
            "v1_8_0": "04423a29e78bb01d9be62256a65354a6",
            "v1_10_0": "8d08bfdf92db5b1df58af9b6adf61eae",
            "v1_12_0": "ef031a3f24f877242621ba695d8dcbd2",
            "v1_12_1": "a59e732fcbf71cb5fcc6c54fef0124d6",
        }
        for v, md5 in expect.items():
            self.assertEqual(self.docs[v]["md5"], md5, v)

    def test_sizes(self):
        for v in REAL_BRIEF:
            want = 16128 if v == "v1_1_1" else 16384
            self.assertEqual(self.docs[v]["bytes"], want, v)

    def test_lead_word_invariant_and_marker_rule(self):
        for v in REAL_BRIEF:
            h = self.docs[v]["header"]
            self.assertEqual(h["lead_word_u16"], "0x7140", v)
            self.assertTrue(self.docs[v]["version_marker"]["marker_present"], v)
            self.assertFalse(
                self.docs[v]["version_strings"]["self_version_string_present"],
                v)

    def test_code_end_matches_measurement(self):
        expect = {"v1_1_1": 0x3B02, "v1_1_6": 0x3B02, "v1_2_0": 0x1B36,
                  "v1_4_0": 0x1AFE, "v1_5_0": 0x1A5E, "v1_5_1": 0x1A5E,
                  "v1_5_2": 0x1B4E, "v1_6_0": 0x19B6, "v1_8_0": 0x3B02,
                  "v1_10_0": 0x2704, "v1_12_0": 0x28D4, "v1_12_1": 0x287C}
        for v, ce in expect.items():
            self.assertEqual(self.docs[v]["padding"]["code_end"], ce, v)

    def test_epilogue_is_invariant_across_the_windowed_files(self):
        for v in REAL_BRIEF:
            ep = self.docs[v]["padding"]["epilogue"]
            if v == "v1_1_1":
                self.assertFalse(ep["present"], v)
            else:
                self.assertTrue(ep["present"], v)
                self.assertEqual(ep["sha1"],
                                 "f81d97b070307896ce03469472c85d6d443a5d15",
                                 v)

    def test_step_pair_identity(self):
        a = read(self.paths[REAL_BRIEF.index("v1_5_0")])
        b = read(self.paths[REAL_BRIEF.index("v1_5_1")])
        r = cpp_probe.same_offset_identity(a, b)
        self.assertGreater(r["identity_pct"], 99.9)
        self.assertEqual(r["common_len"] - r["identical_bytes"], 2)

    def test_magics_present_in_every_identity(self):
        for v in REAL_BRIEF:
            pm = self.docs[v]["protocol_magics"]
            self.assertIn("MSM_CPP_MSG_ID_CMD", pm, v)
            self.assertIn("MSM_CPP_MSG_ID_TRAILER", pm, v)

    def test_build_counter_beside_marker_is_not_the_step(self):
        """MEASURED: the low u16 of the marker's u32 is a build counter.

        It moves with the build (1.5.0 = 0x10, 1.5.1 = 0x02) but it is NOT
        the filename step: it disagrees in 7 of the 12 real files. If this
        changes, the claim in the analysis doc section 6.3 is stale.
        """
        expect = {
            "v1_1_1": 0x0001, "v1_1_6": 0x0006, "v1_2_0": 0x000A,
            "v1_4_0": 0x0005, "v1_5_0": 0x0010, "v1_5_1": 0x0002,
            "v1_5_2": 0x0021, "v1_6_0": 0x0000, "v1_8_0": 0x001E,
            "v1_10_0": 0x0011, "v1_12_0": 0x0007, "v1_12_1": 0x0008,
        }
        mismatches = 0
        for v, want in expect.items():
            vm = self.docs[v]["version_marker"]
            self.assertEqual(vm["adjacent_build_counter"][0],
                             "0x%04x" % want, v)
            if not vm["build_counter_matches_filename_step"][0]:
                mismatches += 1
        self.assertEqual(mismatches, 9, "the build counter must disagree with "
                         "the filename step in 9 of 12 files")

    def test_no_identity_carries_its_own_enum_word(self):
        """CPP_FW_VERSION_* is a userspace identifier, not an in-file field.

        Only 1.1.1, 1.1.6 and 1.6.0 contain their enum value anywhere, and
        there it is the marker+build-counter word (their counter happens to
        equal the filename step). Every other file has zero hits.
        """
        for v in REAL_BRIEF:
            if v in ("v1_1_1", "v1_1_6", "v1_6_0"):
                continue
            data = read(os.path.join(self.dir,
                                     "cpp_firmware_%s.fw" % v))
            ver = cpp_probe.parse_version_from_name("cpp_firmware_%s.fw" % v)
            enum = cpp_probe.fw_version_word(*ver)
            self.assertNotIn(enum.to_bytes(4, "little"), data,
                             "%s unexpectedly carries its enum word" % v)


# ---------------------------------------------------------------- brief

class TestBriefRender(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        ensure_fixtures()

    def test_brief_lines(self):
        doc, _ = cpp_probe.probe_file(LADDER_PATHS[5])
        lines = cpp_probe.render_brief(doc)
        text = "\n".join(lines)
        self.assertIn("window:", text)
        self.assertIn("header:", text)
        self.assertIn("version:", text)
        self.assertIn("ascii version string", text)
        self.assertIn("layout:", text)
        self.assertIn("entropy:", text)

    def test_brief_unreadable(self):
        lines = cpp_probe.render_brief({"basename": "x.fw",
                                        "error": "boom"})
        self.assertIn("UNREADABLE", lines[0])

    def test_matrix_brief(self):
        paths = [os.path.join(FIX, "cpp_firmware_v1_5_0.fw"),
                 os.path.join(FIX, "cpp_firmware_v1_5_1.fw"),
                 os.path.join(FIX, "cpp_firmware_v1_6_0.fw")]
        m = cpp_probe.build_matrix(
            paths,
            labeler=lambda p: "%d.%d.%d" % cpp_probe.parse_version_from_name(p))
        lines = cpp_probe.render_matrix_brief(m)
        text = "\n".join(lines)
        self.assertIn("matrix over 3 files", text)
        for lab in ("1.5.0", "1.5.1", "1.6.0"):
            self.assertIn(lab, text)
        self.assertIn("closest", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
