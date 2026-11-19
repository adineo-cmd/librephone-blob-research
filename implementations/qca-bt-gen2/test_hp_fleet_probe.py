#!/usr/bin/env python3
"""test_hp_fleet_probe.py — unittest suite for the clean-room gen-2
("h-prefix") QCA BT TLV probe, driven by self-made synthetic fixtures.

CLEAN-ROOM STATEMENT
Written from the public GPL sources (linux btqca.h / btqca.c, torvalds/linux
master, fetched 2026-11-18 — see hp_fleet_probe.py / make_fixture.py
headers); no proprietary material was accessed. Fixture bytes are self-made
from the documented field layout plus the *measured* gen-2 header/trailer
sizes. No Qualcomm firmware bytes exist in this repository.

Covers: the type/length decomposition, the full 24-byte upstream
tlv_type_patch decode inside the 32-byte gen-2 vendor header, the gen-2
size invariant 4 + 32 + data_length + 36 in BOTH directions (positive on
gen-2 fixtures, negative/gen-1 on an F-75-shaped fixture), the gen-1
discrimination, the SHA-256 trailer digest including its covered-span
boundary (the 4-byte tag is inside the digest), the 243-byte segment math,
single-set and type-4 multi-set NVM walks, the fleet identity matrix, the
truncation / bad-digest / unknown-type error paths with exit status 1, the
per-family chip annotation, and the CLI/JSON contracts plus fixture
determinism.
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

import hp_fleet_probe as probe
import make_fixture

FIX = os.path.join(HERE, "fixtures")

HP20_FX = os.path.join(FIX, "hpbtfw20_synthetic.tlv")
HP21_FX = os.path.join(FIX, "hpbtfw21_synthetic.tlv")
HMT20_FX = os.path.join(FIX, "hmtbtfw20_synthetic.tlv")
GEN1_FX = os.path.join(FIX, "hpbtfw20_gen1_synthetic.tlv")
BADTRAIL_FX = os.path.join(FIX, "hpbtfw20_badtrailer.tlv")
TRUNC_FX = os.path.join(FIX, "hpbtfw20_truncated.tlv")
NVM_FX = os.path.join(FIX, "hpnv20_synthetic.bin")
HMTNVM_FX = os.path.join(FIX, "hmtnv20_synthetic.bin")
MULTI_FX = os.path.join(FIX, "hpnv20_multi_synthetic.bin")


def run_cli(args):
    return subprocess.run(
        [sys.executable, "-I", os.path.join(HERE, "hp_fleet_probe.py")] + args,
        capture_output=True, text=True)


def error_codes(doc):
    return {d["code"] for d in doc.get("diagnostics", [])
            if d["class"] == "error"}


def info_codes(doc):
    return {d["code"] for d in doc.get("diagnostics", [])
            if d["class"] == "info"}


class TestFixtureGeneration(unittest.TestCase):
    def test_all_fixtures_exist(self):
        for f in (HP20_FX, HP21_FX, HMT20_FX, GEN1_FX, BADTRAIL_FX, TRUNC_FX,
                  NVM_FX, HMTNVM_FX, MULTI_FX):
            self.assertTrue(os.path.isfile(f), "missing fixture %s" % f)

    def test_regeneration_is_byte_identical(self):
        """The generator is fully deterministic: SHA-256 counter streams plus
        a real SHA-256 trailer, so re-running reproduces every byte."""
        names = [os.path.basename(p) for p in
                 (HP20_FX, HP21_FX, HMT20_FX, GEN1_FX, BADTRAIL_FX, TRUNC_FX,
                  NVM_FX, HMTNVM_FX, MULTI_FX)]
        before = {n: open(os.path.join(FIX, n), "rb").read() for n in names}
        make_fixture.main()
        for n, blob in before.items():
            self.assertEqual(open(os.path.join(FIX, n), "rb").read(), blob,
                             "fixture %s not deterministic" % n)

    def test_fleet_magnitude_sizes(self):
        """Fixtures mirror the real fleet magnitudes so segment counts and
        tag counts are realistic, not toy."""
        self.assertEqual(os.path.getsize(HP20_FX), 201560)   # hpbtfw20.tlv
        self.assertEqual(os.path.getsize(HP21_FX), 146068)   # hpbtfw21.tlv
        self.assertEqual(os.path.getsize(HMT20_FX), 280628)  # hmtbtfw20.tlv
        self.assertEqual(os.path.getsize(NVM_FX), 6319)      # hpnv20.bin

    def test_fixtures_share_no_payload_bytes(self):
        """Per-fixture SHA-256 tagging: unrelated fixtures must not share a
        body. Otherwise a cross-file test could pass for the wrong reason."""
        a = open(HP20_FX, "rb").read()
        b = open(HMT20_FX, "rb").read()
        # bodies start after 4+32 and stop before the 36-byte trailer
        ba = a[36:len(a) - 36]
        bb = b[36:len(b) - 36]
        n = min(len(ba), len(bb))
        same = sum(1 for i in range(n) if ba[i] == bb[i])
        self.assertLess(same / float(n), 0.02,
                        "fixture bodies unexpectedly correlated")


class TestDocumentedConstants(unittest.TestCase):
    """Constants must match the public btqca.h / btqca.c definitions."""

    def test_packed_struct_sizes(self):
        self.assertEqual(probe.PATCH_HDR.size, 24)     # struct tlv_type_patch
        self.assertEqual(probe.NVM_TAG_HDR.size, 12)   # struct tlv_type_nvm

    def test_documented_constants(self):
        self.assertEqual(probe.MAX_SIZE_PER_TLV_SEGMENT, 243)
        self.assertEqual(probe.EDL_PATCH_CMD_OPCODE, 0xFC00)
        self.assertEqual(probe.EDL_PATCH_TLV_REQ_CMD, 0x1E)
        self.assertEqual(probe.TAG_BD_ADDR, 2)
        self.assertEqual(probe.TAG_HCI, 17)
        self.assertEqual(probe.TAG_DEEP_SLEEP, 27)
        self.assertEqual(probe.TLV_TYPE_PATCH, 1)
        self.assertEqual(probe.TLV_TYPE_NVM, 2)
        self.assertEqual(probe.TLV_TYPE_MULTI_NVM_ENCLOSING, 4)

    def test_measured_generation_constants(self):
        """These are MEASURED, not documented — assert they have not drifted
        away from the values the analysis text reports."""
        self.assertEqual(probe.GEN1_PATCH_HDR_SIZE, 24)
        self.assertEqual(probe.GEN1_TRAILER_SIZE, 256)
        self.assertEqual(probe.GEN2_PATCH_HDR_SIZE, 32)
        self.assertEqual(probe.GEN2_TRAILER_SIZE, 36)
        self.assertEqual(probe.GEN2_TRAILER_SIZE, 4 + 32)

    def test_type_length_decomposition(self):
        """btqca.c: type in the low byte, length in bits 8..31."""
        self.assertEqual(probe.decode_type_len((0x1234 << 8) | 1), (1, 0x1234))
        self.assertEqual(probe.decode_type_len(0x0003070C), (0x0C, 0x0307))
        raw = (0x03070C << 8) | 1
        self.assertEqual(struct.pack("<I", raw), bytes([1, 0x0C, 0x07, 0x03]))


class TestGen2PatchContainer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.rc = probe.probe_file(HP20_FX)

    def test_exit_status_ok(self):
        self.assertEqual(self.rc, 0)
        self.assertFalse(error_codes(self.doc),
                         "unexpected errors: %s" % error_codes(self.doc))

    def test_container_fields(self):
        self.assertEqual(self.doc["type"], 1)
        self.assertEqual(self.doc["type_name"], "TLV_TYPE_PATCH")
        self.assertEqual(self.doc["size_bytes"], 201560)
        c = self.doc["patch"]["container"]
        self.assertEqual(c["length_field"], 201556)     # file_size - 4
        self.assertTrue(c["declared_length_consistent"])

    def test_upstream_header_decode(self):
        """The 24-byte upstream struct is a PREFIX of the 32-byte vendor
        header; every field must decode at offset 4 exactly as btqca.h
        declares it."""
        h = self.doc["patch"]["patch_header"]
        self.assertEqual(h["offset"], 4)
        self.assertEqual(h["upstream_struct_size"], 24)
        self.assertEqual(h["total_size"], 4 + 32 + h["data_length"])
        self.assertEqual(h["data_length"], 201560 - 4 - 32 - 36)
        self.assertEqual(h["format_version"], 1)
        self.assertEqual(h["signature_algorithm"], 0)
        self.assertEqual(h["download_mode"], 3)
        self.assertEqual(h["download_mode_name"], "QCA_SKIP_EVT_VSE_CC")
        self.assertEqual(h["product_id"], 19)           # QCA2066
        self.assertEqual(h["rom_build"], "0x0200")
        self.assertEqual(h["patch_version"], "0x3ed8")
        self.assertEqual(h["entry"], "0x00000000")      # gen-2: no entry here

    def test_gen2_invariant_holds_and_f75_does_not(self):
        """The core cross-family claim, asserted in both directions: the
        gen-2 rule passes, the F-75 rule fails by a constant -212."""
        lay = self.doc["patch"]["layout"]
        self.assertEqual(lay["header_size_used"], 32)
        self.assertEqual(lay["trailer_size_measured"], 36)
        self.assertEqual(lay["generation"], "gen2-32byte-header")
        self.assertTrue(lay["invariant_gen2"]["holds"])
        self.assertEqual(lay["invariant_gen2"]["delta"], 0)
        self.assertFalse(lay["invariant_f75"]["holds"])
        self.assertEqual(lay["invariant_f75"]["delta"], -212)
        self.assertTrue(lay["total_size_covers_header_plus_payload"])
        self.assertIn("size-invariant-holds", info_codes(self.doc))

    def test_trailer_digest_and_covered_span(self):
        """trailer[4:36] == sha256(file[4 : file_size-32]). The 4-byte tag is
        the first word of the trailer but the LAST word of the covered span,
        so digesting file[4:file_size-36] instead must fail."""
        raw = open(HP20_FX, "rb").read()
        n = len(raw)
        t = self.doc["patch"]["trailer"]
        self.assertTrue(t["sha256_matches"])
        self.assertEqual(t["trailer_offset"], 4 + 32 + 201488)
        self.assertEqual(t["trailer_size"], 36)
        self.assertEqual(t["sha256_over"], "file[4:%d]" % (n - 32))
        stored = raw[n - 32:]
        self.assertEqual(t["sha256_stored"], stored.hex())
        self.assertEqual(hashlib.sha256(raw[4:n - 32]).digest(), stored)
        # negative: excluding the 4-byte tag is NOT the scheme
        self.assertNotEqual(hashlib.sha256(raw[4:n - 36]).digest(), stored)

    def test_segment_math(self):
        """qca_download_firmware sends the whole file in 243-byte segments."""
        p = self.doc["patch"]["download_protocol"]
        self.assertEqual(p["max_segment"], 243)
        self.assertEqual(p["segments_to_send"], 830)     # ceil(201560/243)
        self.assertEqual(p["last_segment_size"], 113)
        self.assertEqual(829 * 243 + 113, 201560)
        self.assertEqual(p["bytes_over_wire"], 201560 + 2 * 830)

    def test_family_annotation_hp(self):
        fam = self.doc["patch"]["family_annotation"]
        self.assertEqual(fam["filename_prefix"], "hp")
        self.assertEqual(fam["chips"], ["QCA2066"])
        self.assertEqual(fam["expected_rampatch_name"], "qca/hpbtfw20.tlv")
        self.assertTrue(fam["name_matches_filename"])
        self.assertTrue(fam["filename_digit_decodes_as_rom_build"])

    def test_body_is_opaque_statistics_only(self):
        """The patch body is never described as code: only statistics."""
        ranges = {r["range"]: r for r in self.doc["patch"]["ranges"]}
        body = [r for k, r in ranges.items() if "patch body" in r["role"]]
        self.assertEqual(len(body), 1)
        self.assertGreater(body[0]["stats"]["entropy"], 7.0)
        for w in self.doc["patch"]["body_word_histogram"]:
            self.assertEqual(len(w["word"]), 10)        # 0x + 8 hex digits
        self.assertIn("no disassembly", self.doc["patch"]["body_alignment_note"])


class TestGen2AcrossFamilies(unittest.TestCase):
    """The same gen-2 invariant must hold on both chip families."""

    def test_hpbtfw21(self):
        doc, rc = probe.probe_file(HP21_FX)
        self.assertEqual(rc, 0)
        lay = doc["patch"]["layout"]
        self.assertTrue(lay["invariant_gen2"]["holds"])
        self.assertEqual(lay["invariant_f75"]["delta"], -212)
        h = doc["patch"]["patch_header"]
        self.assertEqual(h["rom_build"], "0x0201")
        self.assertEqual(h["product_id"], 19)
        self.assertTrue(doc["patch"]["trailer"]["sha256_matches"])
        fam = doc["patch"]["family_annotation"]
        self.assertEqual(fam["expected_rampatch_name"], "qca/hpbtfw21.tlv")
        self.assertTrue(fam["name_matches_filename"])

    def test_hmtbtfw20(self):
        """WCN7850: product_id 25, and this fixture carries a non-zero entry
        dword to prove the probe reports it rather than assuming zero."""
        doc, rc = probe.probe_file(HMT20_FX)
        self.assertEqual(rc, 0)
        lay = doc["patch"]["layout"]
        self.assertTrue(lay["invariant_gen2"]["holds"])
        self.assertEqual(lay["invariant_f75"]["delta"], -212)
        h = doc["patch"]["patch_header"]
        self.assertEqual(h["product_id"], 25)
        self.assertEqual(h["entry"], "0x00020010")
        self.assertTrue(doc["patch"]["trailer"]["sha256_matches"])
        fam = doc["patch"]["family_annotation"]
        self.assertEqual(fam["chips"], ["WCN7850"])
        self.assertEqual(fam["filename_prefix"], "hmt")

    def test_prefix_annotation_switch(self):
        """Longest prefix first: 'wcnhp' must win over 'hp'."""
        self.assertEqual(probe.annotate_filename("wcnhpbtfw21.tlv")
                         ["filename_prefix"], "wcnhp")
        self.assertEqual(probe.annotate_filename("hpbtfw20.tlv")
                         ["filename_prefix"], "hp")
        self.assertEqual(probe.annotate_filename("hmtbtfw20.tlv")
                         ["filename_prefix"], "hmt")
        self.assertEqual(probe.annotate_filename("htbtfw20.tlv")
                         ["filename_prefix"], "ht")
        self.assertIsNone(probe.annotate_filename("crbtfw20.tlv"))


class TestGenerationDiscrimination(unittest.TestCase):
    """The probe must tell gen-1 (F-75) from gen-2 from the bytes alone."""

    @classmethod
    def setUpClass(cls):
        cls.doc, cls.rc = probe.probe_file(GEN1_FX)

    def test_gen1_ok_and_recognised(self):
        self.assertEqual(self.rc, 0)
        lay = self.doc["patch"]["layout"]
        self.assertEqual(lay["header_size_used"], 24)
        self.assertEqual(lay["generation"], "gen1-24byte-header")
        self.assertTrue(lay["invariant_f75"]["holds"])
        self.assertFalse(lay["invariant_gen2"]["holds"])
        self.assertEqual(lay["invariant_gen2"]["delta"], +212)

    def test_gen1_has_no_sha256_trailer(self):
        t = self.doc["patch"]["trailer"]
        self.assertEqual(t["trailer_size"], 256)
        self.assertIsNone(t["sha256_matches"])
        self.assertIn("no SHA-256 field observed", t["note"])

    def test_gen1_entry_is_real(self):
        """F-75 files carry a real entry point at +20; gen-2 files carry 0."""
        h = self.doc["patch"]["patch_header"]
        self.assertEqual(h["entry"], "0x000209e4")
        gen2, _ = probe.probe_file(HP20_FX)
        self.assertEqual(gen2["patch"]["patch_header"]["entry"], "0x00000000")

    def test_gen1_recognised_exits_zero(self):
        """A recognised gen-1 file is a FACT, not an error: the gen-2 rule
        fails on it, but the probe must exit 0 and label it gen-1. This pins
        the documented exit-status claim."""
        self.assertEqual(self.rc, 0)
        self.assertFalse(error_codes(self.doc))
        self.assertIn("size-invariant-holds", info_codes(self.doc))


class TestTrailerDigestErrorPath(unittest.TestCase):
    def test_bad_digest_is_an_error(self):
        doc, rc = probe.probe_file(BADTRAIL_FX)
        self.assertEqual(rc, 1)
        self.assertIn("trailer-digest-mismatch", error_codes(doc))
        # The size invariant itself still holds — only the digest is wrong.
        self.assertTrue(doc["patch"]["layout"]["invariant_gen2"]["holds"])
        self.assertFalse(doc["patch"]["trailer"]["sha256_matches"])


class TestTruncationErrorPath(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.rc = probe.probe_file(TRUNC_FX)

    def test_exit_one_and_both_codes(self):
        self.assertEqual(self.rc, 1)
        codes = error_codes(self.doc)
        self.assertIn("length-field-mismatch", codes)
        self.assertIn("size-invariant-failed", codes)

    def test_shortfall_reported_not_crashed(self):
        lay = self.doc["patch"]["layout"]
        self.assertLess(lay["trailer_size_measured"], 0)
        self.assertEqual(lay["shortfall_bytes"], 4)
        self.assertIn("missing from the trailer", lay["shortfall_note"])

    def test_short_file_does_not_raise(self):
        with tempfile.NamedTemporaryFile(suffix=".tlv", delete=False) as f:
            f.write(struct.pack("<I", (100 << 8) | 1) + b"\x00" * 8)
            path = f.name
        try:
            doc, rc = probe.probe_file(path)
            self.assertEqual(rc, 1)
            self.assertIn("truncated-patch-header", error_codes(doc))
        finally:
            os.unlink(path)

    def test_unknown_container_type(self):
        with tempfile.NamedTemporaryFile(suffix=".tlv", delete=False) as f:
            f.write(struct.pack("<I", (10 << 8) | 5) + b"\x00" * 8)
            path = f.name
        try:
            doc, rc = probe.probe_file(path)
            self.assertEqual(rc, 1)
            self.assertIn("unknown-container-type", error_codes(doc))
        finally:
            os.unlink(path)

    def test_empty_file(self):
        with tempfile.NamedTemporaryFile(suffix=".tlv", delete=False) as f:
            path = f.name
        try:
            doc, rc = probe.probe_file(path)
            self.assertEqual(rc, 1)
            self.assertIn("file-too-small", error_codes(doc))
        finally:
            os.unlink(path)


class TestNvmSingleSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc, cls.rc = probe.probe_file(NVM_FX)
        cls.hmt, cls.hmtrc = probe.probe_file(HMTNVM_FX)

    def test_container(self):
        self.assertEqual(self.rc, 0)
        self.assertFalse(error_codes(self.doc))
        self.assertEqual(self.doc["type"], 2)
        self.assertNotIn("multi_nvm", self.doc["nvm"])
        self.assertEqual(self.doc["nvm"]["set_count_scanned"], 1)
        c = self.doc["nvm"]["container"]
        self.assertEqual(c["length_field"], 6319 - 4)
        self.assertTrue(c["declared_length_consistent"])

    def test_consumed_equals_declared_exactly(self):
        """Plain type-2 single-set files consume their declared length with no
        residue — unlike the F-75 cr/ap multi-set shape."""
        s = self.doc["nvm"]["nvm_sets"][0]
        self.assertEqual(s["consumed_bytes"], s["declared_bytes"])
        total = sum(probe.NVM_TAG_HDR.size + t["tag_len"] for t in s["tags"])
        self.assertEqual(total, s["declared_bytes"])
        self.assertNotIn("trailing", self.doc["nvm"])

    def test_kernel_known_tags(self):
        tags = {t["tag_id"]: t for t in self.doc["nvm"]["nvm_sets"][0]["tags"]}
        self.assertEqual(tags[2]["tag_len"], 6)         # BD_ADDR: kernel == 6
        self.assertIn("BD_ADDR", tags[2]["meaning"])
        self.assertIn("HCI", tags[17]["meaning"])
        self.assertIn("baud byte", tags[17]["meaning"])
        self.assertIn("DEEP_SLEEP", tags[27]["meaning"])

    def test_hp_and_hmt_tag_maps_differ(self):
        """Two chip families, two different tag censuses — the NVM is not a
        shared blob. Counts come from the fixtures' distinct tag plans."""
        hp_tags = self.doc["nvm"]["nvm_sets"][0]["tag_count"]
        hmt_tags = self.hmt["nvm"]["nvm_sets"][0]["tag_count"]
        self.assertGreater(hp_tags, 50)
        self.assertGreater(hmt_tags, 50)
        self.assertNotEqual(hp_tags, hmt_tags)

    def test_opaque_tags_stay_opaque(self):
        filler = [t for t in self.doc["nvm"]["nvm_sets"][0]["tags"]
                  if t["tag_id"] not in (2, 17, 27)]
        self.assertGreater(len(filler), 50)
        for t in filler[:5]:
            self.assertIn("unknown to upstream", t["meaning"])
            self.assertEqual(len(t["data_sha1"]), 40)
            self.assertLessEqual(len(t["data_preview_hex"]), 32)

    def test_nvm_family_annotation_from_filename(self):
        fam = self.doc["nvm"]["family_annotation"]
        self.assertEqual(fam["filename_prefix"], "hp")
        self.assertEqual(fam["rom_ver_from_filename"], "0x20")
        self.assertEqual(fam["expected_nvm_name"], "qca/hpnv20.bin")
        self.assertEqual(fam["board_variant_suffix"], "bin")
        hfam = self.hmt["nvm"]["family_annotation"]
        self.assertEqual(hfam["expected_nvm_name"], "qca/hmtnv20.bin")


class TestNvmMultiSet(unittest.TestCase):
    """The type-4 enclosing shape is F-75's, not gen-2's — but the probe must
    still handle it correctly if it ever appears in an h-prefix file."""

    @classmethod
    def setUpClass(cls):
        cls.doc, cls.rc = probe.probe_file(MULTI_FX)

    def test_enclosing_header_unwrapped(self):
        self.assertEqual(self.rc, 0)
        nvm = self.doc["nvm"]
        self.assertIn("multi_nvm", nvm)
        self.assertEqual(nvm["multi_nvm"]["enclosing_header_type"], 4)
        self.assertIn("FIRST set only",
                      nvm["multi_nvm"]["kernel_behaviour"])

    def test_two_sets_and_trailing_record(self):
        nvm = self.doc["nvm"]
        self.assertEqual(nvm["set_count_scanned"], 2)
        s0, s1 = nvm["nvm_sets"]
        self.assertEqual(s0["header_offset"], 4)
        self.assertEqual(s1["header_offset"], 4 + 4 + s0["declared_bytes"])
        self.assertEqual(s0["consumed_bytes"], s0["declared_bytes"])
        self.assertEqual(s1["consumed_bytes"], s1["declared_bytes"])
        self.assertIn("trailing", nvm)
        self.assertEqual(nvm["trailing"]["decodes_as_tlv_type"], 3)
        self.assertEqual(nvm["trailing"]["declared_len"], 60)
        self.assertTrue(nvm["trailing"]["declares_the_rest"])
        self.assertIn("trailing-bytes", info_codes(self.doc))


class TestFleetMatrix(unittest.TestCase):
    """Cross-file identity, F-75 method: same-offset bytes over the common
    prefix plus 16-byte-block overlap."""

    @classmethod
    def setUpClass(cls):
        cls.m = probe.fleet_matrix([HP20_FX, HP21_FX, HMT20_FX])

    def test_file_records_carry_digests_only(self):
        self.assertEqual(len(self.m["files"]), 3)
        for f in self.m["files"]:
            self.assertNotIn("_data", f)
            self.assertEqual(len(f["md5"]), 32)
            self.assertEqual(len(f["sha256"]), 64)
            self.assertEqual(f["md5"],
                             hashlib.md5(open(f["file"], "rb").read())
                             .hexdigest())

    def test_pairwise_counts_are_consistent(self):
        self.assertEqual(len(self.m["pairs"]), 3)
        for p in self.m["pairs"]:
            self.assertEqual(p["common_len"], min(p["a_size"], p["b_size"]))
            self.assertLessEqual(p["identical_bytes"], p["common_len"])
            self.assertAlmostEqual(
                p["identity_pct"],
                round(100.0 * p["identical_bytes"] / p["common_len"], 2),
                places=2)

    def test_distinct_fixtures_are_low_identity(self):
        """Synthetic bodies are independently tagged, so same-offset identity
        must be at chance level — the real files sit at 2-3%."""
        for p in self.m["pairs"]:
            self.assertLess(p["identity_pct"], 5.0,
                            "%s vs %s unexpectedly similar"
                            % (p["a"], p["b"]))
            self.assertFalse(p["byte_identical"])

    def test_identity_census(self):
        census = self.m["identity_census"]
        self.assertIn("hpbtfw20_synthetic.tlv", census)
        self.assertTrue(all(v["distinct_md5"] >= 1
                            for v in census.values()))

    def test_identical_file_is_100_percent(self):
        m = probe.fleet_matrix([HP20_FX, HP20_FX])
        p = m["pairs"][0]
        self.assertEqual(p["identity_pct"], 100.0)
        self.assertTrue(p["byte_identical"])
        self.assertEqual(m["identity_census"]["hpbtfw20_synthetic.tlv"]
                         ["distinct_md5"], 1)


class TestRomVerStory(unittest.TestCase):
    """Cross-family version story: the default rom_ver formula applied to the
    16-bit rom_build reproduces the filename digit on every gen-2 file."""

    def test_default_formula_on_soc_ver(self):
        self.assertEqual(probe.rom_ver_from_soc_ver(0x00000101, "default"),
                         0x11)
        self.assertEqual(probe.rom_ver_from_soc_ver(0x00000200, "default"),
                         0x20)

    def test_formula_on_rom_build_reproduces_filename_digit(self):
        self.assertEqual(probe.rom_ver_from_rom_build(0x0200), 0x20)
        self.assertEqual(probe.rom_ver_from_rom_build(0x0201), 0x21)
        self.assertEqual(probe.rom_ver_from_rom_build(0x0100), 0x10)

    def test_fixture_filenames_match(self):
        for path, expected in ((HP20_FX, "qca/hpbtfw20.tlv"),
                               (HP21_FX, "qca/hpbtfw21.tlv"),
                               (HMT20_FX, "qca/hmtbtfw20.tlv")):
            doc, _ = probe.probe_file(path, do_hash=False)
            fam = doc["patch"]["family_annotation"]
            self.assertEqual(fam["expected_rampatch_name"], expected)
            self.assertTrue(fam["name_matches_filename"])
            self.assertTrue(fam["filename_digit_decodes_as_rom_build"])

    def test_expected_nvm_names(self):
        self.assertEqual(probe.expected_nvm_name(0x20, "hp"),
                         "qca/hpnv20.bin")
        self.assertEqual(probe.expected_nvm_name(0x21, "hmt"),
                         "qca/hmtnv21.bin")
        self.assertEqual(probe.expected_nvm_name(0x20, "hp", variant="g"),
                         "qca/hpnv20g.bin")
        self.assertEqual(probe.expected_nvm_name(0x20, "hp", board_id=0x0A),
                         "qca/hpnv20.0a")
        self.assertEqual(probe.expected_nvm_name(0x20, "cr", board_id=0x0A),
                         "qca/crnv20.b0a")


class TestCliContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.jout = os.path.join(cls.tmp.name, "out.json")
        cls.r = run_cli([HP20_FX, "--json", cls.jout])
        with open(cls.jout) as f:
            cls.doc = json.load(f)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_json_written_with_required_keys(self):
        self.assertEqual(self.r.returncode, 0)
        for key in ("file", "basename", "size_bytes", "md5", "sha256",
                    "type_len_raw", "type", "type_name", "patch",
                    "diagnostics"):
            self.assertIn(key, self.doc)
        self.assertIn("layout", self.doc["patch"])
        self.assertIn("download_protocol", self.doc["patch"])

    def test_hashes_match_file(self):
        raw = open(HP20_FX, "rb").read()
        self.assertEqual(self.doc["md5"], hashlib.md5(raw).hexdigest())
        self.assertEqual(self.doc["sha256"], hashlib.sha256(raw).hexdigest())

    def test_no_hash_option(self):
        r = run_cli([HP20_FX, "--no-hash"])
        doc = json.loads(r.stdout)
        self.assertNotIn("md5", doc)
        self.assertNotIn("sha256", doc)

    def test_brief_exit_zero_on_valid(self):
        r = run_cli([HP20_FX, "--brief"])
        self.assertEqual(r.returncode, 0)
        self.assertIn("gen-2 PASS", r.stdout)
        self.assertIn("F-75 FAIL(delta -212)", r.stdout)

    def test_brief_exit_one_on_truncated(self):
        r = run_cli([TRUNC_FX, "--brief"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("length-field-mismatch", r.stderr)

    def test_brief_exit_one_on_bad_digest(self):
        r = run_cli([BADTRAIL_FX, "--brief"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("trailer-digest-mismatch", r.stderr)

    def test_fleet_mode_produces_matrix(self):
        out = os.path.join(self.tmp.name, "fleet.json")
        r = run_cli(["--fleet", HP20_FX, HP21_FX, HMT20_FX,
                     "--json", out])
        self.assertEqual(r.returncode, 0)
        with open(out) as f:
            doc = json.load(f)
        self.assertIn("fleet", doc)
        self.assertEqual(len(doc["files"]), 3)
        self.assertEqual(len(doc["fleet"]["pairs"]), 3)
        self.assertIn("identity_census", doc["fleet"])

    def test_help_exits_two(self):
        r = run_cli(["--help"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("hp_fleet_probe.py", r.stdout)


class TestCrossCheckIsOptional(unittest.TestCase):
    """The component does not import implementations/qca-bt; the cross-check
    only shells out, so this module's claims stand alone."""

    def test_no_import_of_sibling_package(self):
        src = open(os.path.join(HERE, "hp_fleet_probe.py")).read()
        self.assertNotIn("import qca_tlv", src)
        self.assertNotIn("from qca_tlv", src)

    def test_cross_check_runs_on_the_data_file(self):
        """Regression: --cross-check must run the F-75 parser on the DATA
        file, not on the parser path. An earlier version passed the parser
        path through as the input and analysed qca_tlv.py itself."""
        other = os.path.abspath(os.path.join(HERE, "..", "qca-bt",
                                            "qca_tlv.py"))
        if not os.path.isfile(other):
            self.skipTest("implementations/qca-bt/qca_tlv.py not present")
        res = probe.cross_check(HP20_FX, other)
        self.assertTrue(res["available"])
        self.assertEqual(res["returncode"], 0)
        # the F-75 parser must have seen OUR file (product_id 19, rom_build
        # 0x0200), not qca_tlv.py itself
        joined = " ".join(res["stdout_head"])
        self.assertIn("product_id 19", joined)
        self.assertIn("rom_build 0x0200", joined)
        self.assertNotIn("unknown-container-type", joined)

    def test_cross_check_missing_parser_is_reported_not_raised(self):
        res = probe.cross_check(HP20_FX, "/nonexistent/qca_tlv.py")
        self.assertFalse(res["available"])
        self.assertIn("not found", res["reason"])

    def test_cli_cross_check_targets_input_not_parser(self):
        other = os.path.abspath(os.path.join(HERE, "..", "qca-bt",
                                            "qca_tlv.py"))
        if not os.path.isfile(other):
            self.skipTest("implementations/qca-bt/qca_tlv.py not present")
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "o.json")
            r = run_cli([HP20_FX, "--cross-check", other, "--json", out])
            self.assertEqual(r.returncode, 0)
            with open(out) as f:
                doc = json.load(f)
        cc = doc["cross_check"]
        self.assertEqual(cc["returncode"], 0)
        self.assertIn("product_id 19", " ".join(cc["stdout_head"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
