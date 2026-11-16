#!/usr/bin/env python3
"""test_md32_interface.py — unittest suite for the clean-room md1dsp
interface parser, driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16 (see
md32_interface.py header); no proprietary material accessed. Fixtures are
generated at test time by make_fixture.py from the documented field layout
and documented constants only.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import md32_interface as mi      # noqa: E402
import make_fixture as mf        # noqa: E402


class FixtureBuildTests(unittest.TestCase):
    def test_crc32_forge_roundtrip(self):
        prefix = mf.filler("forge", 0, 1000)
        target = 0xDEADBEEF
        suffix = mf.crc32_forge(prefix, target)
        self.assertEqual(len(suffix), 4)
        self.assertEqual(zlib.crc32(prefix + suffix) & 0xFFFFFFFF, target)
        # deterministic
        self.assertEqual(suffix, mf.crc32_forge(prefix, target))

    def test_header_fixture_determinism(self):
        self.assertEqual(mf.build_header_fixture(), mf.build_header_fixture())


class ParserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hdr = mf.build_header_fixture()

    def test_gfh_prefix(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=False)
        self.assertNotIn("error", doc)
        recs = doc["gfh_prefix"]
        self.assertEqual(recs[0]["type"], 0)
        self.assertEqual(recs[0]["name"], "FILE_INFO")
        self.assertEqual(recs[0]["sig_type"], 0)
        self.assertEqual(recs[0]["load_addr"], 0xFFFFFFFF)
        self.assertEqual(recs[0]["total_size"], 0x678000)
        self.assertEqual(recs[-1]["type"], 260)

    def test_dsp_header(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=False)
        h = doc["header"]
        self.assertEqual(h["payload_size"], 0x678000)
        self.assertEqual(h["version"], 1)
        # the fixture encodes the F-45 absolute reading
        self.assertIn("F-45", h["marker_reading"])
        self.assertIn("F-45", h["chip_reading"])
        self.assertEqual(h["chip"], "MT6785")
        self.assertTrue(h["asic_string"].startswith("DEFAULT_ASIC"))
        self.assertTrue(h["build_string"].startswith("MOLY.LR13.R1.MP.V89.6.P79"))
        self.assertIn("differ", h["documented_conflict"])
        self.assertIn("both read and reported", h["documented_conflict"])

    def test_dsp_header_f36_reading_also_detected(self):
        # build a variant fixture using the F-36 relative offsets and
        # confirm the parser reports that reading instead (no guessing)
        buf = bytearray(self.hdr)
        import struct
        marker = struct.unpack_from("<I", buf, mi.MARKER_F45)[0]
        chip = bytes(buf[mi.CHIP_F45:mi.CHIP_F45 + 6])
        buf[mi.MARKER_F45:mi.MARKER_F45 + 4] = b"\x00" * 4
        buf[mi.CHIP_F45:mi.CHIP_F45 + 6] = b"\x00" * 6
        struct.pack_into("<I", buf, mi.MARKER_F36, marker)
        buf[mi.CHIP_F36:mi.CHIP_F36 + 6] = chip
        doc = mi.parse_dsp_image(bytes(buf), check_crc=False)
        self.assertIn("F-36", doc["header"]["marker_reading"])
        self.assertIn("F-36", doc["header"]["chip_reading"])

    def test_descriptor_table(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=False)
        dt = doc["descriptor_table"]
        self.assertEqual(dt["offset"], 0x248)
        self.assertEqual(len(dt["records"]), 3)
        self.assertTrue(all(r["matches_documented"] for r in dt["records"]))
        self.assertEqual(dt["records"][2]["tag_is_ascii"], "USIP")

    def test_usip_shape_and_samples(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=False)
        u = doc["usip"]
        self.assertEqual(u["tag"], "USIP")
        self.assertEqual(u["body_offset"], 0x278)
        self.assertTrue(u["documented_samples_match"])
        self.assertIn("NOT pinned", u["termination"])

    def test_rake_chain_checks(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=False)
        r = doc["rake"]
        self.assertEqual(r["tag"], "RAKE")
        self.assertTrue(all(rec["matches_documented"] for rec in r["records"]))
        cc = r["chain_checks"]
        self.assertTrue(cc["documented_window_ok"])
        self.assertTrue(cc["sorted_offsets"])
        self.assertTrue(cc["non_overlapping"])
        self.assertIn("NOT pinned", cc["contiguity"])
        # no crc check possible on the header-only fixture (regions absent)
        self.assertFalse(r["crc32_checked"])

    def test_no_crc_check_without_regions(self):
        doc = mi.parse_dsp_image(self.hdr, check_crc=True)
        # the header-only fixture has no bytes at the RAKE offsets, so the
        # parser must NOT claim crc verification
        self.assertFalse(all("crc32_file_match" in rec for rec in doc["rake"]["records"]))

    def test_full_fixture_crc32_verification(self):
        blob = mf.build_full_fixture()
        self.assertEqual(len(blob), 0x60A9D0)
        # the forged regions carry exactly the documented crc32 constants
        for off, ln, crc in mi.RAKE_CHAIN_EXPECTED:
            self.assertEqual(zlib.crc32(blob[off:off + ln]) & 0xFFFFFFFF, crc)
        doc = mi.parse_dsp_image(blob, check_crc=True)
        recs = doc["rake"]["records"]
        self.assertTrue(all(rec["matches_documented"] for rec in recs))
        self.assertTrue(all(rec.get("crc32_file_match") for rec in recs))

    def test_full_fixture_crc_tamper_detected(self):
        blob = bytearray(mf.build_full_fixture())
        blob[0x58C814] ^= 0xFF  # corrupt the first RAKE region
        doc = mi.parse_dsp_image(bytes(blob), check_crc=True)
        self.assertFalse(doc["rake"]["records"][0]["crc32_file_match"])
        self.assertTrue(doc["rake"]["records"][1]["crc32_file_match"])

    def test_bad_magic(self):
        doc = mi.parse_dsp_image(b"\x00" * 0x200)
        self.assertIn("error", doc)
        doc = mi.parse_dsp_image(self.hdr[:0x100])
        self.assertIn("error", doc)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as td:
            fx = os.path.join(td, "md1dsp.bin")
            with open(fx, "wb") as fh:
                fh.write(self.hdr)
            out = os.path.join(td, "out.json")
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "md32_interface.py"),
                 fx, "--json", out, "--no-crc"], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            doc = json.load(open(out))
            self.assertEqual(doc["header"]["payload_size"], 0x678000)

    def test_committed_fixture_matches_generator(self):
        path = os.path.join(HERE, "fixtures", "md1dsp_header_fixture.bin")
        if not os.path.exists(path):
            subprocess.run([sys.executable, "-I",
                            os.path.join(HERE, "make_fixture.py"),
                            os.path.join(HERE, "fixtures")],
                           check=True, capture_output=True)
        with open(path, "rb") as fh:
            self.assertEqual(fh.read(), self.hdr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
