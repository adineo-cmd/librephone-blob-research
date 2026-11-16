#!/usr/bin/env python3
"""test_mtk_container.py — unittest suite for the clean-room MediaTek
container parser, driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16 (see
mtk_container.py / make_fixture.py headers); no proprietary material was
accessed during development. Fixture bytes are self-made from the
documented layout only.

Covers: chain walk + alignment arithmetic, the >=20-byte name field,
ext-record field decode, cert1/cert2 pair detection, unsigned-record
classification, GFH record decode (types 0/1/2/3/7/8/260) with the
documented rosemary field values, truncation / bad-magic / bad-alignment
diagnostics, fixture determinism, and the JSON CLI contract.
"""

import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import mtk_container as mc  # noqa: E402
import make_fixture as mf   # noqa: E402


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mtk = mf.build_mtk_chain()
        cls.gfh_pre = mf.build_gfh_preloader()
        cls.gfh_dsp = mf.build_gfh_md1dsp()

    def test_fixture_determinism(self):
        self.assertEqual(mf.build_mtk_chain(), self.mtk)
        self.assertEqual(mf.build_gfh_preloader(), self.gfh_pre)

    def test_der_shaped_blocks(self):
        for size in (mf.CERT1_SIZE, mf.CERT2_SIZE):
            blob = mf.der_shaped(size)
            self.assertEqual(len(blob), size)
            self.assertTrue(blob.startswith(b"\x30\x82"))
            self.assertEqual(struct.unpack_from(">H", blob, 2)[0], size - 4)

    # --- mtk_hdr chain ---

    def test_mtk_chain_walk(self):
        res = mc.parse_mtk_hdr_chain(self.mtk)
        self.assertEqual(res["verification"]["status"], "ok", res["verification"])
        names = [r["name"] for r in res["records"]]
        self.assertEqual(names, ["tinysys-loader-CM4_A", "cert1", "cert2",
                                 "md1_file_map", "tiny-stub", "spmfw",
                                 "cert1", "cert2"])
        # every header is 512 B and the payload sits at +0x200
        for r in res["records"]:
            self.assertEqual(r["payload_offset"] - r["header_offset"], 0x200)
        # chain stride arithmetic: next record = align(payload_end, 0x10)
        r0 = res["records"][0]
        self.assertEqual(r0["size"], 1080)
        self.assertEqual(res["records"][1]["header_offset"],
                         (r0["payload_offset"] + 1080 + 0xF) & ~0xF)
        # the >=20-byte name field survives ("tinysys-loader-CM4_A" is 20 chars)
        self.assertEqual(r0["name"], "tinysys-loader-CM4_A")
        # ext record fields: header_size 0x200, alignment 0x10
        self.assertEqual(r0["ext"]["header_size"], 0x200)
        self.assertEqual(r0["ext"]["align"], 0x10)

    def test_mtk_chain_signature_pairs(self):
        res = mc.parse_mtk_hdr_chain(self.mtk)
        sig = res["signature_blocks"]
        self.assertEqual(sig["cert1_cert2_pairs"], 2)
        recs = res["records"]
        self.assertEqual(recs[0]["signature"], "signed-by-cert-pair")
        self.assertEqual(recs[1]["signature"], "cert1")
        self.assertEqual(recs[2]["signature"], "cert2")
        # md1_file_map (modem data payload class) stays unsigned
        self.assertEqual(recs[3]["signature"], "none")
        # the no-ext stub record is not a signature block
        self.assertEqual(recs[4]["signature"], "none")

    def test_mtk_hashing(self):
        res = mc.parse_mtk_hdr_chain(self.mtk, hash_payloads=True)
        self.assertIn("sha256_16", res["records"][0])
        self.assertEqual(len(res["records"][0]["sha256_16"]), 16)

    def test_mtk_truncated_payload(self):
        cut = self.mtk[:0x200 + 1080 + 16 + 0x200 + 100]  # ends inside cert1's payload
        res = mc.parse_mtk_hdr_chain(cut)
        self.assertNotEqual(res["verification"]["status"], "ok")
        self.assertTrue(any("truncated-payload" in d for d in res["verification"]["diagnostics"]))

    def test_mtk_bad_magic(self):
        blob = bytearray(self.mtk)
        # record 1 starts at align(0x200 + 1080, 0x10) = 1600; corrupt its magic
        blob[1600] = 0x00
        res = mc.parse_mtk_hdr_chain(bytes(blob))
        self.assertEqual(res["verification"]["status"], "bad-magic")
        self.assertEqual(len(res["records"]), 1)

    def test_mtk_bad_alignment_field(self):
        rec = mf.mtk_record("ali", b"x" * 64, align=0x18)  # not a power of two
        res = mc.parse_mtk_hdr_chain(rec)
        self.assertEqual(res["verification"]["status"], "bad-alignment")

    def test_mtk_zero_size_payload_walks_cleanly(self):
        # a zero-payload record advances past its own 0x200 header
        # (payload_end = 0x200, aligned next = 0x200), then the chain ends;
        # the non-advancing guard is defensive-only with the 0x200 header
        # (align(pend) >= pend > off always) — assert the clean walk.
        blob = mf.mtk_record("loop", b"", align=0x10)
        res = mc.parse_mtk_hdr_chain(blob)
        self.assertEqual(res["verification"]["status"], "ok")
        self.assertEqual(res["records"][0]["size"], 0)
        self.assertEqual(len(res["records"]), 1)

    # --- GFH MMM chains ---

    def test_gfh_preloader_records(self):
        res = mc.parse_gfh_chain(self.gfh_pre)
        self.assertEqual(res["verification"]["status"], "ok", res["verification"])
        types = [r["type"] for r in res["records"]]
        self.assertEqual(types, [0, 1, 2, 3, 7, 8])
        names = [r["type_name"] for r in res["records"]]
        self.assertEqual(names, ["FILE_INFO", "BL_INFO", "ANTI_CLONE",
                                 "BL_SEC_KEY", "BROM_CFG", "BROM_SEC_CFG"])
        fi = res["records"][0]["fields"]
        # the rosemary preloader values documented in the census
        self.assertEqual(fi["name"], "FILE_INFO")
        self.assertEqual(fi["file_type"], 1)
        self.assertEqual(fi["flash_type"], 5)
        self.assertEqual(fi["sig_type"], 5)
        self.assertEqual(fi["load_addr"], 0x00200F10)
        self.assertEqual(fi["total_size"], 0x55134)
        self.assertEqual(fi["jump_offset"], 0xF0)
        bc = res["records"][4]["fields"]
        self.assertEqual(bc["cfg_bits"], 0x90)
        self.assertEqual(bc["jump_bl_arm64"], 0)
        bs = res["records"][5]["fields"]
        self.assertEqual(bs["customer_name"], "LIBREPHONE")

    def test_gfh_md1dsp_records(self):
        res = mc.parse_gfh_chain(self.gfh_dsp)
        self.assertEqual(res["verification"]["status"], "ok", res["verification"])
        types = [r["type"] for r in res["records"]]
        self.assertEqual(types, [0, 260])
        fi = res["records"][0]["fields"]
        self.assertEqual(fi["sig_type"], 0)
        self.assertEqual(fi["load_addr"], 0xFFFFFFFF)
        r260 = res["records"][1]
        self.assertEqual(r260["type"], mc.GFH_TYPE_MD1DSP)
        self.assertIn("not pinned", r260["fields"]["note"])

    def test_gfh_bad_magic(self):
        blob = b"XMM\x01\x10\x00\x00\x00" + b"\x00" * 8
        res = mc.parse_gfh_chain(blob)
        self.assertEqual(res["verification"]["status"], "bad-magic")

    def test_gfh_truncated_record(self):
        res = mc.parse_gfh_chain(self.gfh_dsp[:20])
        self.assertEqual(res["verification"]["status"], "truncated-record")

    def test_auto_kind(self):
        self.assertEqual(mc.auto_kind(self.mtk), "mtk_hdr")
        self.assertEqual(mc.auto_kind(self.gfh_pre), "gfh")
        self.assertIsNone(mc.auto_kind(b"\x7fELF"))

    # --- CLI contract ---

    def test_cli_json_and_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            fx = os.path.join(td, "chain.bin")
            with open(fx, "wb") as fh:
                fh.write(self.mtk)
            out = os.path.join(td, "out.json")
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "mtk_container.py"),
                 fx, "--json", out, "--hash"],
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            doc = json.loads(p.stdout)
            self.assertEqual(doc["format"], "mtk_hdr")
            self.assertEqual(doc["verification"]["records"], 8)
            with open(out) as fh:
                self.assertEqual(json.load(fh)["records"][0]["size"], 1080)
            # a chain whose SECOND record's magic is corrupted exits 1
            # (auto-detection keys on the first record's magic, so corrupting
            # record 0 would exit 2 "unrecognized format" instead)
            bad = os.path.join(td, "bad.bin")
            blob = bytearray(self.mtk)
            blob[1600] = 0x00
            with open(bad, "wb") as fh:
                fh.write(bytes(blob))
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "mtk_container.py"), bad],
                capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(json.loads(p.stdout)["verification"]["status"], "bad-magic")

    def test_cli_fixture_files_parse(self):
        fx_dir = os.path.join(HERE, "fixtures")
        for fn, kind, status in (("mtk_chain_fixture.bin", "mtk_hdr", "ok"),
                                 ("gfh_preloader_fixture.bin", "gfh", "ok"),
                                 ("gfh_md1dsp_fixture.bin", "gfh", "ok")):
            path = os.path.join(fx_dir, fn)
            if not os.path.exists(path):
                subprocess.run([sys.executable, "-I",
                                os.path.join(HERE, "make_fixture.py"), fx_dir],
                               check=True, capture_output=True)
            with open(path, "rb") as fh:
                data = fh.read()
            if kind == "mtk_hdr":
                res = mc.parse_mtk_hdr_chain(data)
            else:
                res = mc.parse_gfh_chain(data)
            self.assertEqual(res["verification"]["status"], status, fn)
            # committed fixtures must match what the generator produces today
            gen = (mf.build_mtk_chain() if fn.startswith("mtk")
                   else mf.build_gfh_preloader() if "preloader" in fn
                   else mf.build_gfh_md1dsp())
            self.assertEqual(data, gen, fn)


if __name__ == "__main__":
    unittest.main(verbosity=2)
