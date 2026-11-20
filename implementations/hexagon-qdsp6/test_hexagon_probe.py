#!/usr/bin/env python3
"""test_hexagon_probe.py -- unittest suite for the clean-room Hexagon
container probe.

Run with:
    python3 -m unittest -v test_hexagon_probe

(Do not add ``-I`` here: it drops the CWD from ``sys.path`` and the loader
cannot find the module. ``hexagon_probe.py`` itself is always runnable with
``-I``, which is how the CLI tests invoke it.)

Fixtures are synthetic (see make_fixture.py); no vendor artifact is
required or referenced. Tests that need a real image are skipped unless
``HEXAGON_REAL_FILE`` points at one.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import hexagon_probe as hp  # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
REAL = os.environ.get("HEXAGON_REAL_FILE")


def fixture(name):
    return os.path.join(FIXTURES, name)


def ensure_fixtures():
    if not os.path.isdir(FIXTURES) or not os.listdir(FIXTURES):
        subprocess.run([sys.executable, "-I", os.path.join(HERE, "make_fixture.py")],
                       check=True, capture_output=True)


class TestEhdr(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_rejects_non_elf(self):
        with self.assertRaises(hp.ProbeError):
            hp.parse_ehdr(b"NOTELF" + b"\x00" * 60)

    def test_rejects_short_file(self):
        with self.assertRaises(hp.ProbeError):
            hp.parse_ehdr(b"\x7fELF\x01\x01")

    def test_rejects_elf64(self):
        buf = bytearray(64)
        buf[:4] = b"\x7fELF"
        buf[4] = 2
        buf[5] = 1
        with self.assertRaises(hp.ProbeError):
            hp.parse_ehdr(bytes(buf))

    def test_rejects_big_endian(self):
        buf = bytearray(64)
        buf[:4] = b"\x7fELF"
        buf[4] = 1
        buf[5] = 2
        with self.assertRaises(hp.ProbeError):
            hp.parse_ehdr(bytes(buf))

    def test_fields_of_synthetic(self):
        with open(fixture("monolithic_v67.hexbin"), "rb") as fh:
            hdr = hp.parse_ehdr(fh.read())
        self.assertEqual(hdr["e_machine"], hp.EM_QDSP6)
        self.assertEqual(hdr["e_type"], hp.ET_EXEC)
        self.assertEqual(hdr["e_flags"], 0x67)
        self.assertEqual(hdr["e_ehsize"], 52)
        self.assertEqual(hdr["e_phentsize"], 32)


class TestPhdrTable(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_phentsize_enforced(self):
        with open(fixture("monolithic_v67.hexbin"), "rb") as fh:
            data = fh.read()
        hdr = hp.parse_ehdr(data)
        hdr["e_phentsize"] = 40
        with self.assertRaises(hp.ProbeError):
            hp.parse_phdrs(data, hdr)

    def test_table_past_eof(self):
        with open(fixture("monolithic_v67.hexbin"), "rb") as fh:
            data = fh.read()
        hdr = hp.parse_ehdr(data)
        hdr["e_phnum"] = 1000
        with self.assertRaises(hp.ProbeError):
            hp.parse_phdrs(data, hdr)

    def test_flags_decoded(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        code = res["program_headers"][0]
        self.assertTrue(code["mdt_relocatable"])
        self.assertEqual(code["mdt_type"], 0)
        self.assertFalse(code["mdt_type_hash"])
        self.assertTrue(code["read"])
        self.assertFalse(code["write"])
        self.assertTrue(code["execute"])

    def test_hash_segment_found_by_type_field(self):
        res = hp.probe(fixture("signed_v67.mbn"))
        self.assertEqual(res["hash_segment"], 0)
        meta = res["program_headers"][0]
        self.assertEqual(meta["p_type"], hp.PT_NULL)
        self.assertTrue(meta["mdt_type_hash"])
        self.assertFalse(meta["mdt_relocatable"])
        self.assertEqual(meta["kind"], "metadata")

    def test_zero_phnum(self):
        with open(fixture("monolithic_v67.hexbin"), "rb") as fh:
            data = fh.read()
        hdr = hp.parse_ehdr(data)
        hdr["e_phnum"] = 0
        self.assertEqual(hp.parse_phdrs(data, hdr), [])


class TestClassify(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_header_table_segment(self):
        res = hp.probe(fixture("selfcontained_v67.mbn"))
        self.assertEqual(res["program_headers"][0]["kind"], "header-table")

    def test_bss_segment(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        kinds = [p["kind"] for p in res["program_headers"]]
        self.assertIn("bss", kinds)

    def test_code_segment(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        self.assertEqual(res["program_headers"][0]["kind"], "code")

    def test_metadata_segment(self):
        res = hp.probe(fixture("split_v66.mdt"))
        self.assertEqual(res["program_headers"][0]["kind"], "header-table")

    def test_zlib_detected(self):
        import zlib
        body = zlib.compress(b"A" * 4096)
        seg = {"filesz": len(body), "memsz": len(body), "flags": 0x08000004,
               "body": body}
        res = hp.classify_phdr(
            {"p_type": 1, "p_offset": 4096, "p_filesz": len(body),
             "p_memsz": len(body), "p_flags": 0x08000004, "read": True,
             "write": False, "execute": False},
            {"e_ehsize": 52, "e_phnum": 1},
            b"\x00" * 4096 + body)
        self.assertEqual(res, "zlib-compressed")
        del seg


class TestGeneration(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_monolithic(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        self.assertEqual(res["generation"], "monolithic")

    def test_split_mdt(self):
        res = hp.probe(fixture("split_v66.mdt"))
        self.assertEqual(res["generation"], "split-mdt")

    def test_self_contained(self):
        res = hp.probe(fixture("selfcontained_v67.mbn"))
        self.assertEqual(res["generation"], "self-contained")

    def test_split_siblings_found(self):
        res = hp.probe(fixture("split_v66.mdt"))
        self.assertIsNotNone(res["split_siblings"])
        names = [r["file"] for r in res["split_siblings"]["present"]]
        self.assertIn("split_v66.b00", names)
        self.assertIn("split_v66.b01", names)
        self.assertIn("split_v66.b02", names)

    def test_split_sibling_sizes_match(self):
        res = hp.probe(fixture("split_v66.mdt"))
        for row in res["split_siblings"]["present"]:
            self.assertTrue(row["size_matches"],
                            "%s size %d != expected %s"
                            % (row["file"], row["bytes"], row["expected_bytes"]))

    def test_split_absent_sibling_is_bss(self):
        res = hp.probe(fixture("split_v66.mdt"))
        absent = res["split_siblings"]["absent"]
        self.assertEqual(len(absent), 1)
        self.assertEqual(absent[0]["p_filesz"], 0)
        self.assertEqual(absent[0]["reason"], "p_filesz==0")

    def test_b00_equals_header_table(self):
        res = hp.probe(fixture("split_v66.mdt"))
        b00 = [r for r in res["split_siblings"]["present"] if r["index"] == 0][0]
        self.assertEqual(b00["bytes"], res["e_phoff"] + 4 * 32)


class TestGaps(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_gap_sum_equals_uncovered(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        self.assertEqual(sum(g["bytes"] for g in res["gaps"]),
                         res["uncovered_bytes"])

    def test_no_gaps_when_dense(self):
        spans = [{"p_offset": 0, "p_filesz": 100, "index": 0},
                 {"p_offset": 100, "p_filesz": 100, "index": 1}]
        gaps = hp.gap_analysis(spans, 200)
        self.assertEqual(gaps, [])

    def test_trailing_gap_reported(self):
        spans = [{"p_offset": 0, "p_filesz": 100, "index": 0}]
        gaps = hp.gap_analysis(spans, 200)
        self.assertEqual(len(gaps), 1)
        self.assertEqual(gaps[0]["bytes"], 100)
        self.assertIsNone(gaps[0]["before_segment"])

    def test_overlap_detected(self):
        spans = [{"p_type": 1, "p_offset": 0, "p_filesz": 100, "index": 0},
                 {"p_type": 1, "p_offset": 50, "p_filesz": 100, "index": 1}]
        self.assertEqual(len(hp.overlap_check(spans)), 1)

    def test_no_overlap_adjacent(self):
        spans = [{"p_type": 1, "p_offset": 0, "p_filesz": 100, "index": 0},
                 {"p_type": 1, "p_offset": 100, "p_filesz": 100, "index": 1}]
        self.assertEqual(hp.overlap_check(spans), [])


class TestInvariants(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def test_good_image_clean(self):
        res = hp.probe(fixture("selfcontained_v67.mbn"))
        self.assertEqual(res["violations"], [])

    def test_bad_phoff_flagged(self):
        res = hp.probe(fixture("bad_phoff.mbn"))
        self.assertTrue(any("e_phoff" in v for v in res["violations"]))

    def test_bad_memsz_flagged(self):
        res = hp.probe(fixture("bad_memsz.mbn"))
        self.assertTrue(any("p_memsz" in v for v in res["violations"]))

    def test_truncated_raises(self):
        with self.assertRaises(hp.ProbeError):
            hp.probe(fixture("truncated.mbn"))

    def test_wrong_machine_raises(self):
        import struct
        with open(fixture("monolithic_v67.hexbin"), "rb") as fh:
            buf = bytearray(fh.read())
        struct.pack_into("<H", buf, 18, 40)
        path = fixture("_tmp_arm.mbn")
        with open(path, "wb") as fh:
            fh.write(buf)
        try:
            with self.assertRaises(hp.ProbeError):
                hp.probe(path)
        finally:
            os.unlink(path)


class TestEntropy(unittest.TestCase):
    def test_empty_is_zero(self):
        self.assertEqual(hp.entropy(b""), 0.0)

    def test_uniform_bytes_is_zero(self):
        self.assertEqual(hp.entropy(b"\x00" * 1000), 0.0)

    def test_two_symbols_is_one(self):
        self.assertAlmostEqual(hp.entropy(b"\x00\x01" * 500), 1.0, places=6)

    def test_full_alphabet_near_eight(self):
        data = bytes(range(256)) * 4
        self.assertGreater(hp.entropy(data), 7.9)

    def test_word_entropy_short_input(self):
        self.assertEqual(hp.entropy_words(b"\x00\x01"), 0.0)


class TestHexagonArch(unittest.TestCase):
    def test_v67_mapped(self):
        self.assertEqual(hp.HEXAGON_ARCH[0x67], "v67")

    def test_v66_mapped(self):
        self.assertEqual(hp.HEXAGON_ARCH[0x66], "v66")

    def test_unknown_reported(self):
        res = hp.probe(fixture("monolithic_v67.hexbin"))
        self.assertEqual(res["hexagon_arch"], "v67")
        self.assertEqual(res["e_flags_high"], "0x0")


class TestCli(unittest.TestCase):
    def setUp(self):
        ensure_fixtures()

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", os.path.join(HERE, "hexagon_probe.py")]
            + list(args),
            capture_output=True, text=True)

    def test_brief_output(self):
        r = self.run_cli(fixture("monolithic_v67.hexbin"), "--brief")
        self.assertEqual(r.returncode, 0)
        self.assertIn("v67", r.stdout)
        self.assertIn("OK", r.stdout)

    def test_violation_exit_one(self):
        r = self.run_cli(fixture("bad_memsz.mbn"), "--brief")
        self.assertEqual(r.returncode, 1)

    def test_parse_error_exit_two(self):
        r = self.run_cli(fixture("truncated.mbn"), "--brief")
        self.assertEqual(r.returncode, 2)

    def test_json_roundtrip(self):
        out = os.path.join(HERE, "_tmp_probe.json")
        try:
            r = self.run_cli(fixture("selfcontained_v67.mbn"),
                             "--json", out, "--quiet")
            self.assertEqual(r.returncode, 0)
            with open(out) as fh:
                doc = json.load(fh)
            self.assertEqual(doc["e_machine"], 164)
            self.assertIn("program_headers", doc)
        finally:
            if os.path.exists(out):
                os.unlink(out)

    def test_dir_mode(self):
        r = self.run_cli("--dir", FIXTURES)
        self.assertIn("monolithic_v67.hexbin", r.stdout)

    def test_no_args_errors(self):
        r = self.run_cli()
        self.assertEqual(r.returncode, 2)


@unittest.skipUnless(REAL, "set HEXAGON_REAL_FILE to a real qdsp6sw.mbn")
class TestRealImage(unittest.TestCase):
    def test_real_image(self):
        res = hp.probe(REAL)
        self.assertEqual(res["e_machine"], 164)
        self.assertEqual(res["violations"], [])
        self.assertEqual(sum(g["bytes"] for g in res["gaps"]),
                         res["uncovered_bytes"])
        self.assertFalse(res["has_section_headers"])


if __name__ == "__main__":
    unittest.main()
