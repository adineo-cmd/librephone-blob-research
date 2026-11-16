#!/usr/bin/env python3
"""test_qca_tlv.py — unittest suite for the clean-room QCA BT TLV parser,
driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written from the public GPL sources (linux btqca.h/btqca.c, torvalds/linux
master, fetched 2026-11-16 — see qca_tlv.py / make_fixture.py headers); no
proprietary material was accessed during development. Fixture bytes are
self-made from the documented layout only.

Covers: type/length decomposition (type in the low byte), the full
24-byte tlv_type_patch decode, segment-count math against the documented
243-byte download protocol, single-set and multi-set (type-4 enclosing)
NVM walks with the kernel's first-set-only semantics recorded, the three
kernel-known NVM tags (BD_ADDR 2 / HCI 17 / DEEP_SLEEP 27) plus opaque
tags kept opaque, truncation + length-mismatch error diagnostics with exit
status 1, raw-ELF rampatch (msbtfw*.mbn) byte-4..6 reads, the per-chip
rom_ver name math, fixture determinism, and the JSON/brief CLI contracts.
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

import make_fixture
import qca_tlv

FIX = os.path.join(HERE, "fixtures")

PATCH_FX = os.path.join(FIX, "crbtfw20_synthetic.tlv")
NVM_FX = os.path.join(FIX, "crnv20_synthetic.bin")
APNVM_FX = os.path.join(FIX, "apnv10_synthetic.bin")
MULTI_FX = os.path.join(FIX, "nvm_multi_synthetic.bin")
TRUNC_FX = os.path.join(FIX, "crbtfw20_truncated.tlv")
ELF_FX = os.path.join(FIX, "msbtfw11_synthetic.mbn")


def run_cli(args):
    return subprocess.run([sys.executable, "-I", os.path.join(HERE,
                            "qca_tlv.py")] + args, capture_output=True,
                          text=True)


class TestFixtureGeneration(unittest.TestCase):
    def test_fixtures_exist(self):
        for f in (PATCH_FX, NVM_FX, APNVM_FX, MULTI_FX, TRUNC_FX, ELF_FX):
            self.assertTrue(os.path.isfile(f), "missing fixture %s" % f)

    def test_regeneration_is_byte_identical(self):
        """Deterministic generator: re-running reproduces every fixture
        byte-for-byte (the lab's mediatek/container precedent)."""
        before = {f: open(os.path.join(FIX, f), "rb").read() for f in
                  ("crbtfw20_synthetic.tlv", "crnv20_synthetic.bin",
                   "apnv10_synthetic.bin", "nvm_multi_synthetic.bin",
                   "crbtfw20_truncated.tlv", "msbtfw11_synthetic.mbn")}
        make_fixture.main()  # rewrites in place
        for name, blob in before.items():
            self.assertEqual(open(os.path.join(FIX, name), "rb").read(),
                             blob, "fixture %s not deterministic" % name)

    def test_fleet_magnitude_sizes(self):
        """Fixtures mirror the fleet files' sizes from coverage-matrix.csv:
        crbtfw20.tlv 56,180 B; crnv20.bin 3,936 B; apnv10.bin 1,243 B."""
        self.assertEqual(os.path.getsize(PATCH_FX), 56180)
        self.assertEqual(os.path.getsize(NVM_FX), 3936)
        self.assertEqual(os.path.getsize(APNVM_FX), 1243)


class TestStructuralConstants(unittest.TestCase):
    """The layout constants must match the documented btqca.h structs."""

    def test_packed_struct_sizes(self):
        self.assertEqual(qca_tlv.PATCH_HDR.size, 24)   # tlv_type_patch
        self.assertEqual(qca_tlv.NVM_TAG_HDR.size, 12)  # tlv_type_nvm prefix

    def test_documented_constants(self):
        self.assertEqual(qca_tlv.MAX_SIZE_PER_TLV_SEGMENT, 243)
        self.assertEqual(qca_tlv.EDL_PATCH_CMD_OPCODE, 0xFC00)
        self.assertEqual(qca_tlv.EDL_PATCH_TLV_REQ_CMD, 0x1E)
        self.assertEqual(qca_tlv.TAG_BD_ADDR, 2)
        self.assertEqual(qca_tlv.TAG_HCI, 17)
        self.assertEqual(qca_tlv.TAG_DEEP_SLEEP, 27)

    def test_type_length_decomposition(self):
        """btqca.c:370-371: type = low byte, length = bits 8..31."""
        self.assertEqual(qca_tlv.decode_type_len((0x1234 << 8) | 1), (1, 0x1234))
        self.assertEqual(qca_tlv.decode_type_len(0x0003070C), (0x0C, 0x0307))
        raw = (0x03070C << 8) | 1   # len=0x03070C, type=1
        self.assertEqual(struct.pack("<I", raw), bytes([1, 0x0C, 0x07, 0x03]))


class TestPatchContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out, cls.rc = qca_tlv.parse_file(PATCH_FX)

    def test_exit_status_ok(self):
        self.assertEqual(self.rc, 0)

    def test_container_fields(self):
        self.assertEqual(self.out["type"], 1)
        self.assertEqual(self.out["type_name"], "TLV_TYPE_PATCH")
        self.assertEqual(self.out["size_bytes"], 56180)
        c = self.out["patch"]["container"]
        self.assertEqual(c["length_field"], 56176)      # file_size - 4
        self.assertTrue(c["declared_length_consistent"])

    def test_patch_header_fields(self):
        h = self.out["patch"]["patch_header"]
        self.assertEqual(h["offset"], 4)
        self.assertEqual(h["size"], 24)
        self.assertEqual(h["total_size"], 56180)
        self.assertEqual(h["data_length"], 56180 - 4 - 24)
        self.assertEqual(h["format_version"], 1)        # Signing Format Version
        self.assertEqual(h["signature_algorithm"], 0)
        self.assertEqual(h["download_mode"], 3)
        self.assertEqual(h["download_mode_name"], "QCA_SKIP_EVT_VSE_CC")
        self.assertEqual(h["product_id"], 21)
        self.assertEqual(h["rom_build"], "0x0200")
        self.assertEqual(h["patch_version"], "0x89fd")
        self.assertEqual(h["entry"], "0x00020000")

    def test_download_protocol_math(self):
        """Whole file in 243-byte segments: ceil(56180/243)=232 segments,
        last = 56180 - 231*243 = 107 bytes."""
        p = self.out["patch"]["download_protocol"]
        self.assertEqual(p["max_segment"], 243)
        self.assertEqual(p["segments_to_send"], 232)
        self.assertEqual(p["last_segment_size"], 47)
        self.assertEqual(231 * 243 + 47, 56180)

    def test_family_annotation(self):
        fam = self.out["patch"]["family_annotation"]
        self.assertEqual(fam["filename_prefix"], "cr")
        self.assertEqual(fam["chips"], ["WCN3990", "WCN3991", "WCN3998"])
        self.assertEqual(fam["rom_ver_derived_from_rom_build"], "0x20")
        self.assertEqual(fam["expected_rampatch_name"], "qca/crbtfw20.tlv")


class TestNvmSingleSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out, cls.rc = qca_tlv.parse_file(NVM_FX)
        cls.apout, cls.aprc = qca_tlv.parse_file(APNVM_FX)

    def test_container(self):
        self.assertEqual(self.rc, 0)
        self.assertEqual(self.out["type"], 2)
        self.assertNotIn("multi_nvm", self.out["nvm"])
        self.assertEqual(self.out["nvm"]["set_count_scanned"], 1)

    def test_kernel_known_tags(self):
        tags = {t["tag_id"]: t for t in
                self.out["nvm"]["nvm_sets"][0]["tags"]}
        self.assertEqual(tags[1]["tag_len"], len(b"BTFW.SYNTH.1.0-00001-PATCHZ-1"))
        self.assertEqual(tags[2]["tag_len"], 6)          # BD_ADDR: kernel==6
        self.assertIn("BD_ADDR", tags[2]["meaning"])
        self.assertEqual(tags[17]["tag_len"], 8)
        self.assertIn("HCI", tags[17]["meaning"])
        self.assertIn("baud byte", tags[17]["meaning"])  # documented mutation
        self.assertEqual(tags[27]["tag_len"], 4)
        self.assertIn("DEEP_SLEEP", tags[27]["meaning"])

    def test_opaque_tags_kept_opaque(self):
        """Filler tags unknown to upstream stay opaque (facts-not-blobs)."""
        filler = [t for t in self.out["nvm"]["nvm_sets"][0]["tags"]
                  if t["tag_id"] not in (1, 2, 17, 27)]
        self.assertGreater(len(filler), 40)
        for t in filler[:5]:
            self.assertIn("unknown to upstream", t["meaning"])
            self.assertEqual(len(t["data_preview_hex"]), 32)  # 16 bytes hex
            self.assertEqual(len(t["data_sha1"]), 40)

    def test_stride_arithmetic_consumed_equals_declared(self):
        s = self.out["nvm"]["nvm_sets"][0]
        self.assertEqual(s["consumed_bytes"], s["declared_bytes"])
        total = sum(qca_tlv.NVM_TAG_HDR.size + t["tag_len"]
                    for t in s["tags"])
        self.assertEqual(total, s["declared_bytes"])

    def test_apnv10_family(self):
        self.assertEqual(self.aprc, 0)
        self.assertEqual(self.apout["size_bytes"], 1243)
        fam = self.apout["nvm"]["family_annotation"]
        self.assertEqual(fam["filename_prefix"], "ap")
        self.assertEqual(fam["chips"], ["WCN3988"])


class TestNvmMultiSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out, cls.rc = qca_tlv.parse_file(MULTI_FX)

    def test_enclosing_header_unwrapped(self):
        self.assertEqual(self.rc, 0)
        nvm = self.out["nvm"]
        self.assertIn("multi_nvm", nvm)
        self.assertEqual(nvm["multi_nvm"]["enclosing_header_type"], 4)
        self.assertIn("FIRST set only", nvm["multi_nvm"]["kernel_behaviour"])

    def test_two_sets_scanned(self):
        nvm = self.out["nvm"]
        self.assertEqual(nvm["set_count_scanned"], 2)
        s0, s1 = nvm["nvm_sets"]
        self.assertEqual(s0["tag_count"], 3)
        self.assertEqual(s1["tag_count"], 2)
        # kernel parses set 0 first, at the header right after the type-4
        self.assertEqual(s0["header_offset"], 4)
        self.assertEqual(s1["header_offset"],
                         4 + 4 + s0["declared_bytes"])

    def test_trailing_bytes_reported(self):
        codes = [d["code"] for d in self.out["diagnostics"] if
                 d["class"] == "info"]
        self.assertIn("trailing-bytes", codes)


class TestErrorPaths(unittest.TestCase):
    def test_truncated_patch_errors(self):
        out, rc = qca_tlv.parse_file(TRUNC_FX)
        self.assertEqual(rc, 1)
        codes = {d["code"] for d in out["diagnostics"] if
                 d["class"] == "error"}
        self.assertIn("length-field-mismatch", codes)

    def test_unknown_container_type(self):
        with tempfile.NamedTemporaryFile(suffix=".tlv", delete=False) as f:
            f.write(struct.pack("<I", (10 << 8) | 5) + b"\x00" * 8)
            path = f.name
        try:
            out, rc = qca_tlv.parse_file(path)
            self.assertEqual(rc, 1)
            self.assertIn("unknown-container-type",
                          [d["code"] for d in out["diagnostics"]])
        finally:
            os.unlink(path)

    def test_cli_exit_one_on_truncated(self):
        r = run_cli([TRUNC_FX, "--brief"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("length-field-mismatch", r.stderr)

    def test_cli_exit_zero_on_valid(self):
        r = run_cli([PATCH_FX, "--brief"])
        self.assertEqual(r.returncode, 0)


class TestElfPatch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out, cls.rc = qca_tlv.parse_file(ELF_FX)

    def test_elf_fields_kernel_reads(self):
        self.assertEqual(self.rc, 0)
        self.assertTrue(self.out["elf_magic"])
        self.assertEqual(self.out["elf_patch"]["container"],
                         "raw ELF (magic 0x7f 'E' 'L' 'F'; no TLV wrapper)")
        f = self.out["elf_patch"]["elf_header_fields_kernel_reads"]
        self.assertEqual(f["file_class_at_4"], "0x01")
        self.assertEqual(f["data_encoding_at_5"], "0x01")
        self.assertEqual(f["file_version_at_6"], "0x01")
        self.assertIn("QCA_SKIP_EVT_VSE_CC",
                      self.out["elf_patch"]["download_mode_forced"])

    def test_family_annotation_ms(self):
        fam = self.out["family_annotation"]
        self.assertEqual(fam["filename_prefix"], "ms")
        self.assertEqual(fam["chips"], ["WCN6750"])


class TestRomVerMath(unittest.TestCase):
    """The kernel's three rom_ver formulas (btqca.c qca_uart_setup)."""

    def test_default_formula(self):
        self.assertEqual(qca_tlv.rom_ver_from_soc_ver(0x00000101, "default"),
                         0x11)     # FP6-census cross-check: 0x0101 -> 0x11
        self.assertEqual(qca_tlv.rom_ver_from_soc_ver(0x00000200, "default"),
                         0x20)     # -> crbtfw20

    def test_wcn3988_formula(self):
        # WCN3988: ((soc_ver & 0xf00) >> 5) | (soc_ver & 0xf)
        soc = 0x0000CA00          # (0xa00 >> 5) | 0 = 0x50
        self.assertEqual(qca_tlv.rom_ver_from_soc_ver(soc, "ap"), 0x50)

    def test_wcn3998_formula(self):
        # WCN3998: ((soc_ver & 0xf000) >> 7) | (soc_ver & 0xf)
        soc = 0x0000DA00          # (0xd000 >> 7) | 0 = 0x1a0 & 0xff -> 0xa0
        self.assertEqual(qca_tlv.rom_ver_from_soc_ver(soc, "cr"), 0xA0)


class TestCliJsonContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.jout = os.path.join(cls.tmp.name, "out.json")
        r = run_cli([PATCH_FX, "--json", cls.jout, "--hash"])
        cls.rc = r.returncode
        with open(cls.jout) as f:
            cls.doc = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_json_written_with_required_keys(self):
        self.assertEqual(self.rc, 0)
        for key in ("file", "size_bytes", "type_len_raw", "type", "type_name",
                    "patch", "diagnostics", "sha256"):
            self.assertIn(key, self.doc)
        self.assertIn("patch_header", self.doc["patch"])
        self.assertIn("download_protocol", self.doc["patch"])

    def test_hash_matches_file(self):
        self.assertEqual(self.doc["sha256"],
                         hashlib.sha256(open(PATCH_FX, "rb").read())
                         .hexdigest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
