#!/usr/bin/env python3
"""test_md1rom_taskmap.py — unittest suite for the clean-room md1rom
taskmap model.

CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16 (see
md1rom_taskmap.py header); no proprietary material accessed. The entry
fixture below is self-made bytes reproducing ONLY the three instruction
words + filler pattern documented in mediatek/docs/md1rom-decode.md (F-31)
— the _mtc0 word is deliberately arbitrary because the spec pins it by
mnemonic only.
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

import md1rom_taskmap as tm  # noqa: E402


def make_entry_fixture():
    """Self-made bytes exercising the documented F-31 entry chain."""
    buf = bytearray(0x40)
    struct.pack_into("<I", buf, 0x00, 0x3C060174)  # lui   a2,0x174
    struct.pack_into("<I", buf, 0x04, 0x24C62ED0)  # addiu a2,a2,0x2ed0
    struct.pack_into("<I", buf, 0x08, 0x00C00008)  # jr    a2
    struct.pack_into("<I", buf, 0x0C, 0xDEADBEEF)  # _mtc0 (encoding not pinned)
    buf[0x10:0x30] = b"\x00\x65" * 16              # documented filler
    return bytes(buf)


class TaskmapTests(unittest.TestCase):
    def test_taskmap_structure(self):
        doc = tm.build_taskmap()
        for key in ("image", "entry_chain", "region_map", "task_inventory",
                    "task_dispatch_families", "payload_manifest", "stubs"):
            self.assertIn(key, doc)
        self.assertEqual(doc["image"]["size_bytes"], 26682512)
        self.assertEqual(doc["image"]["modem_os_version"],
                         "MOLY.LR13.R1.MP.V89.6.P79")
        self.assertEqual(doc["entry_chain"]["jr_target"], 0x176ED0)

    def test_dispatch_families_match_inventory(self):
        doc = tm.build_taskmap()
        fams = doc["task_dispatch_families"]
        self.assertEqual(set(fams), {"LTE", "HSPA", "CDMA2000"})
        self.assertEqual(len(fams["LTE"]), 4)
        self.assertEqual(len(fams["CDMA2000"]), 2)
        total = sum(len(v) for v in fams.values())
        self.assertEqual(total, len(doc["task_inventory"]))

    def test_every_inventory_task_cites_evidence(self):
        for t in tm.build_taskmap()["task_inventory"]:
            self.assertTrue(t["evidence"].startswith("F-"), t)

    def test_payload_manifest_signedness_matches_census(self):
        pm = {p["payload"]: p for p in tm.build_taskmap()["payload_manifest"]}
        self.assertTrue(pm["md1rom"]["signed"])
        self.assertTrue(pm["md1dsp"]["signed"])
        for data_payload in ("md1_file_map", "md1_mddbmeta", "md1_mdmlayout"):
            self.assertFalse(pm[data_payload]["signed"],
                             "modem data payloads ship unsigned per the census")
        self.assertIn("GFH", pm["md1dsp"]["container"])
        self.assertIn("260", pm["md1dsp"]["container"])

    def test_stubs_are_explicit(self):
        stubs = tm.build_taskmap()["stubs"]
        required = ("task_entry_addresses", "task_to_region_binding",
                    "ccci_channel_map", "md1rom_segment_map", "md32_isa",
                    "host_interface")
        for k in required:
            self.assertIn(k, stubs)
            self.assertTrue(stubs[k]["status"].startswith("stub"), k)
            self.assertTrue(stubs[k]["reason"].strip(), k)

    def test_verify_entry_chain_pass(self):
        rep = tm.verify_entry_chain(make_entry_fixture())
        self.assertEqual(rep["status"], "ok", rep)
        self.assertEqual(len(rep["checks"]), 4)

    def test_verify_entry_chain_rejects_corrupted_word(self):
        buf = bytearray(make_entry_fixture())
        buf[0x04] ^= 0xFF  # break addiu
        rep = tm.verify_entry_chain(bytes(buf))
        self.assertEqual(rep["status"], "mismatch")
        self.assertFalse(rep["checks"][1]["ok"])

    def test_verify_entry_chain_rejects_broken_filler(self):
        buf = bytearray(make_entry_fixture())
        buf[0x12] = 0x66  # filler pattern broken
        rep = tm.verify_entry_chain(bytes(buf))
        self.assertEqual(rep["status"], "mismatch")
        self.assertFalse(rep["checks"][-1]["ok"])

    def test_verify_entry_chain_too_short(self):
        rep = tm.verify_entry_chain(b"\x00" * 16)
        self.assertEqual(rep["status"], "too-short")

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "taskmap.json")
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "md1rom_taskmap.py"),
                 "--json", out], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            doc = json.load(open(out))
            self.assertEqual(doc["component"], "md1rom-taskmap")

    def test_cli_verify_entry_exit_codes(self):
        with tempfile.TemporaryDirectory() as td:
            good = os.path.join(td, "entry.bin")
            with open(good, "wb") as fh:
                fh.write(make_entry_fixture())
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "md1rom_taskmap.py"),
                 "--verify-entry", good], capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            bad = os.path.join(td, "bad.bin")
            with open(bad, "wb") as fh:
                fh.write(b"\x00" * 0x40)
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "md1rom_taskmap.py"),
                 "--verify-entry", bad], capture_output=True, text=True)
            self.assertEqual(p.returncode, 1)
            self.assertEqual(json.loads(p.stdout)["status"], "mismatch")


if __name__ == "__main__":
    unittest.main(verbosity=2)
