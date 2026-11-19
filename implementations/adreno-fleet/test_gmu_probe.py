#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""test_gmu_probe.py -- unittest suite for the clean-room GMU microcode probe.

Run from this directory:

    python3 -m unittest -v test_gmu_probe

Covers, in the order the probe applies them:

  * the RULE-0 premise check -- that the mainline sources document
    `struct block_header` and NOT an `a6xx_gmu_fw_header`, and that both
    loader paths (legacy raw write / block_header walk) are modelled;
  * the container branch ("has mainline header") AND the raw-image branch
    ("no header at all"), each parsed to its expected values;
  * the startup-stub decode (SP/PSP/VTOR literals, the b.w target);
  * vector-table and IRQ-tail enumeration;
  * string extraction, entropy shape, Thumb census;
  * truncation and corruption diagnostics, with exit codes;
  * fixture determinism (regeneration is byte-identical);
  * the CLI and JSON contracts.

The fixtures are synthetic (make_fixture.py). No proprietary byte is used.
"""

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

import gmu_probe as gp          # noqa: E402
import make_fixture as mf       # noqa: E402

PROBE = os.path.join(HERE, "gmu_probe.py")
FIXTURES = os.path.join(HERE, "fixtures")


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def load(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def run_cli(args, **kw):
    """Run the probe as a subprocess; return (rc, stdout, stderr)."""
    proc = subprocess.run([sys.executable, "-I", PROBE] + args,
                          capture_output=True, text=True, **kw)
    return proc.returncode, proc.stdout, proc.stderr


class FixtureMixin:
    """Regenerate fixtures once so the suite never depends on stale bytes."""

    @classmethod
    def setUpClass(cls):
        os.makedirs(FIXTURES, exist_ok=True)
        for name, blob in mf.build_all():
            with open(os.path.join(FIXTURES, name), "wb") as f:
                f.write(blob)


# ---------------------------------------------------------------------------
# 1. RULE 0: the public-header premise
# ---------------------------------------------------------------------------

class TestPublicHeaderPremise(unittest.TestCase):
    """The task premise was that GMU firmware carries `a6xx_gmu_fw_header`.
    These tests pin the *opposite*, documented finding so a future reader
    cannot silently re-introduce the wrong assumption."""

    def test_mainline_documents_block_header_not_fw_header(self):
        # The probe's model of mainline must be the block_header chain.
        self.assertEqual(gp.BLOCK_HEADER.size, 16)
        self.assertEqual(gp.BLOCK_HEADER.format, "<IIII")
        # Nothing in this component may DECLARE an a6xx_gmu_fw_header type:
        # mainline has no such struct (checked v5.4/v5.10/v5.15/v6.1/master).
        # Only the probe's layout constants count as declarations -- prose
        # that mentions the name while refuting it is expected.
        for name in ("gmu_probe.py", "make_fixture.py"):
            with open(os.path.join(HERE, name), "r", errors="replace") as f:
                text = f.read()
            self.assertNotIn("struct a6xx_gmu_fw_header {", text)
            self.assertNotIn("A6XX_GMU_FW_HEADER", text)

    def test_two_documented_loader_paths_are_modelled(self):
        # a6xx_gmu.c:894-904 (legacy: raw bulk write, 0x8000 cap)
        self.assertEqual(gp.LEGACY_FW_MAX, 0x8000)
        # a6xx_gmu.c:886-887 (the driver's TCM bases)
        self.assertEqual(gp.ITCM_BASE, 0x00000000)
        self.assertEqual(gp.DTCM_BASE, 0x00040000)
        self.assertEqual(gp.TCM_SIZE, 0x4000)
        # a6xx_gmu.xml:45-46 -- the two TCM windows are exactly SZ_16K apart,
        # which is what makes a flat 32 KiB image contiguous.
        self.assertEqual((gp.DTCM_START_REG - gp.ITCM_START_REG) * 4,
                         gp.TCM_SIZE)
        # a6xx_gmu.c:896 -- the cap is exactly ITCM + DTCM.
        self.assertEqual(gp.LEGACY_FW_MAX, 2 * gp.TCM_SIZE)

    def test_fw_init_magic_matches_driver_constant(self):
        self.assertEqual(gp.FW_INIT_MAGIC, 0xBABEFACE)

    def test_vtor_constant_is_armv7m_scb_vtor(self):
        self.assertEqual(gp.VTOR_ADDR, 0xE000ED08)

    def test_dtcm_probe_lands_on_fw_version_register(self):
        # a6xx_gmu.c:311 reads DTCM_START+0xff8; a6xx_gmu.xml:55 names that
        # same address GMU_CORE_FW_VERSION.
        self.assertEqual(gp.DTCM_START_REG + gp.DTCM_PROBE_OFF,
                         gp.FW_VERSION_REG)


# ---------------------------------------------------------------------------
# 2. Raw-image branch (the a619/a630 shape) -- "no header"
# ---------------------------------------------------------------------------

class TestRawImageBranch(FixtureMixin, unittest.TestCase):

    def setUp(self):
        self.data = load("a619like_raw.bin")
        self.report, self.diag = gp.analyze(self.data)

    def test_identifies_raw_tcm_image(self):
        self.assertEqual(self.report["format"], "raw-tcm-image")
        self.assertFalse(self.report["header_present"])
        self.assertIsNone(self.report["header_struct"])
        self.assertIn("stack pointer", self.report["header_verdict"])

    def test_mainline_walk_is_attempted_first_and_rejected(self):
        walk = self.report["mainline_block_walk"]
        self.assertTrue(walk["attempted"])
        self.assertFalse(walk["fits"])
        codes = [d["code"] for d in self.diag.items]
        self.assertIn("block-container-rejected", codes)
        # the rejection must precede the fallback
        self.assertLess(codes.index("block-container-rejected"),
                        codes.index("legacy-size"))

    def test_rejected_because_a6xx_size_field_overflows(self):
        term = self.report["mainline_block_walk"]["termination"]
        self.assertEqual(term["status"], "overflow")
        self.assertGreater(term["declared_next"], term["file_size"])

    def test_size_equals_legacy_cap(self):
        self.assertEqual(len(self.data), gp.LEGACY_FW_MAX)
        self.assertEqual(self.report["size"], 0x8000)
        self.assertIn("legacy-size", [d["code"] for d in self.diag.items])

    def test_no_errors(self):
        self.assertFalse(self.diag.has_errors,
                         [d for d in self.diag.items if d["level"] == "error"])

    def test_startup_stub_decoded(self):
        stub = self.report["startup_stub"]
        self.assertEqual(stub["stub_offset"], 0x08)
        self.assertEqual(stub["initial_sp"], 0x00043F80)
        self.assertEqual(stub["psp"], 0x00041440)
        self.assertEqual(stub["vtor_value"], 0x200)
        self.assertEqual(stub["vtor_reg"], 0xE000ED08)
        self.assertTrue(stub["vtor_reg_is_scb_vtor"])

    def test_stub_writes_vtor_before_branching(self):
        # Hand-check the encoding chain: each `ldr rX,[pc,#imm]` must resolve
        # to the literal the probe reports.
        data = self.data
        hw = lambda o: struct.unpack_from("<H", data, o)[0]
        self.assertEqual(hw(0x08) & 0xF800, 0x4800)      # ldr r0,[pc,#..]
        self.assertEqual(hw(0x0A), 0xF380)               # msr (hi half)
        self.assertEqual(hw(0x0C) & 0xFF00, 0x8800)
        self.assertEqual(hw(0x18), 0x6008)               # str r0,[r1,#0]
        # and the literals the probe reports must be the ones actually there
        self.assertEqual(struct.unpack_from("<I", data, 0x20)[0],
                         self.report["initial_sp"])
        self.assertEqual(struct.unpack_from("<I", data, 0x2C)[0], 0xE000ED08)

    def test_initial_sp_sits_in_dtcm_at_conventional_slot(self):
        sp = self.report["initial_sp"]
        self.assertTrue(self.report["initial_sp_in_dtcm"])
        self.assertEqual(sp, gp.DTCM_BASE + gp.TCM_SIZE - 0x80)
        self.assertEqual(self.report["sp_offset_from_dtcm_top"], 0x80)

    def test_reset_vector_is_thumb_and_in_itcm(self):
        rv = self.report["reset_vector"]
        self.assertTrue(rv & 1, "Thumb bit clear")
        self.assertLess(rv & ~1, gp.TCM_SIZE)

    def test_vector_table_starts_with_same_sp(self):
        vt = self.report["vector_table"]
        self.assertEqual(vt["offset"], 0x200)
        self.assertEqual(len(vt["entries"]), 16)
        self.assertEqual(vt["entries"][0]["value"], self.report["initial_sp"])
        self.assertEqual(vt["entries"][0]["name"], "Initial SP")
        self.assertEqual(vt["entries"][1]["name"], "Reset")
        # every architectural handler entry is a Thumb address
        for e in vt["entries"][1:]:
            if e["value"]:
                self.assertTrue(e["value"] & 1, e)

    def test_irq_tail_enumerated(self):
        irq = self.report["irq_table"]
        self.assertEqual(irq["count"], 64)
        self.assertEqual(len(irq["distinct_targets"]), 1)

    def test_region_descriptor_table(self):
        d = self.report["region_descriptor_table"]
        self.assertEqual(d["offset"], 0x3EA4)
        self.assertEqual(d["pair_count"], 8)
        self.assertTrue(d["all_ascending"])
        self.assertTrue(d["alternating_regions"])
        self.assertEqual(d["offset"] + d["length"], 0x3EE4)

    def test_dtcm_address_pair_table(self):
        p = self.report["dtcm_address_pairs"]
        self.assertEqual(p["offset"], 0x44D8)
        self.assertEqual(p["count"], 10)
        self.assertEqual(p["stride"], 8)
        self.assertTrue(p["all_values_zero"])
        self.assertEqual(p["address_min"], "0x440020c0")

    def test_fw_init_magic_present(self):
        # Same absolute sites as the real image (measured 0x1AF4 / 0x2EC8).
        self.assertEqual(self.report["fw_init_magic_sites"], [0x1AF4, 0x2EC8])

    def test_no_container_markers(self):
        self.assertFalse(self.report["container_markers_present"])

    def test_layout_halves(self):
        self.assertEqual(self.report["itcm"]["file_offset"], 0x0000)
        self.assertEqual(self.report["dtcm"]["file_offset"], 0x4000)
        self.assertEqual(self.report["itcm"]["size"], gp.TCM_SIZE)
        self.assertEqual(self.report["dtcm"]["size"], gp.TCM_SIZE)


# ---------------------------------------------------------------------------
# 3. Container branch (the a640/a650/a660/a623/a663 shape) -- "has header"
# ---------------------------------------------------------------------------

class TestContainerBranch(FixtureMixin, unittest.TestCase):

    def setUp(self):
        self.data = load("a640like_container.bin")
        self.report, self.diag = gp.analyze(self.data)

    def test_identifies_mainline_container(self):
        self.assertEqual(self.report["format"], "mainline-block-container")
        self.assertTrue(self.report["header_present"])
        self.assertIn("block_header", self.report["header_struct"])

    def test_walk_is_the_documented_struct(self):
        # struct block_header { u32 addr; u32 size; u32 type; u32 value; }
        blocks = self.report["blocks"]
        first = blocks[0]
        addr, size, typ, value = struct.unpack_from("<IIII", self.data,
                                                    first["offset"])
        self.assertEqual((first["addr"], first["size"], first["type"],
                          first["value"]), (addr, size, typ, value))

    def test_walk_terminates_at_exact_eof(self):
        self.assertEqual(self.report["walk_termination"]["status"], "exact-eof")
        last = self.report["blocks"][-1]
        self.assertEqual(last["next"], len(self.data))

    def test_descriptor_table_detected(self):
        d = self.report["descriptor_table"]
        self.assertEqual(d["entry_count"], 6)
        self.assertEqual(d["stride"], 16)

    def test_payload_blocks_land_in_tcm(self):
        regions = self.report["regions"]
        self.assertIn("ITCM", regions)
        self.assertIn("DTCM", regions)
        # real a640/a650/a660 also carry blocks outside both TCM windows,
        # which the driver maps into icache/dcache/dummy BOs (a6xx_gmu.c:923)
        self.assertIn("outside-TCM", regions)

    def test_no_errors_and_no_raw_fallback(self):
        self.assertFalse(self.diag.has_errors)
        codes = [d["code"] for d in self.diag.items]
        self.assertIn("block-container", codes)
        self.assertNotIn("block-container-rejected", codes)

    def test_region_entropy_per_block(self):
        self.assertIn("region_entropy", self.report)
        self.assertTrue(self.report["region_entropy"])


# ---------------------------------------------------------------------------
# 4. Diagnostics: truncation and corruption
# ---------------------------------------------------------------------------

class TestDiagnostics(FixtureMixin, unittest.TestCase):

    def test_truncated_raw_image_is_a_size_error(self):
        data = load("a619like_truncated.bin")
        report, diag = gp.analyze(data)
        self.assertEqual(report["format"], "raw-tcm-image")
        self.assertTrue(diag.has_errors)
        errs = [d for d in diag.items if d["level"] == "error"]
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0]["code"], "legacy-size")

    def test_bad_sp_is_reported(self):
        data = load("a619like_badsp.bin")
        report, diag = gp.analyze(data)
        self.assertFalse(report["initial_sp_in_dtcm"])
        self.assertTrue(diag.has_errors)
        self.assertIn("bad-sp", [d["code"] for d in diag.items])

    def test_container_overrun_rejects_and_falls_through(self):
        data = load("container_truncated.bin")
        report, diag = gp.analyze(data)
        self.assertEqual(report["format"], "unknown")
        self.assertTrue(diag.has_errors)
        self.assertIn("unrecognised-layout", [d["code"] for d in diag.items])
        self.assertIn("block-container-rejected",
                      [d["code"] for d in diag.items])

    def test_unknown_bytes_are_rejected(self):
        data = load("unknown.bin")
        report, diag = gp.analyze(data)
        self.assertEqual(report["format"], "unknown")
        self.assertTrue(diag.has_errors)

    def test_empty_file(self):
        report, diag = gp.analyze(b"")
        self.assertEqual(report["size"], 0)
        self.assertTrue(diag.has_errors)
        self.assertIn("empty", [d["code"] for d in diag.items])

    def test_container_walk_overflow_message_names_offsets(self):
        blocks, term = gp.walk_block_headers(load("container_truncated.bin"))
        self.assertEqual(term["status"], "overflow")
        self.assertIn("offset", term)
        self.assertIn("declared_next", term)


# ---------------------------------------------------------------------------
# 5. Measurement primitives
# ---------------------------------------------------------------------------

class TestMeasurementPrimitives(unittest.TestCase):

    def test_shannon_entropy_bounds(self):
        self.assertEqual(gp.shannon_entropy(b"\x00" * 1000), 0.0)
        uniform = bytes(range(256)) * 4
        self.assertAlmostEqual(gp.shannon_entropy(uniform), 8.0, places=6)
        self.assertEqual(gp.shannon_entropy(b""), 0.0)

    def test_entropy_profile_shapes(self):
        data = b"\x00" * 512 + bytes(range(256)) * 2
        prof = gp.entropy_profile(data, block=512)
        self.assertEqual(prof[0]["entropy"], 0.0)
        self.assertGreater(prof[1]["entropy"], 7.0)
        self.assertEqual(prof[0]["zero_fraction"], 1.0)

    def test_zero_regions(self):
        data = b"\xff" * 10 + b"\x00" * 20 + b"\xaa" * 10
        regs = gp.zero_regions(data, min_len=16)
        self.assertEqual(len(regs), 1)
        self.assertEqual(regs[0], {"offset": 10, "length": 20})
        # below min_len -> not reported
        self.assertEqual(gp.zero_regions(data, min_len=21), [])

    def test_string_extraction_ascii_and_offsets(self):
        data = b"\x00\x01" + b"SIGABRT: boom" + b"\x00" + b"abcdefg" + b"\x00"
        found = gp.extract_strings(data, min_len=4)
        texts = [s["text"] for s in found]
        self.assertIn("SIGABRT: boom", texts)
        self.assertIn("abcdefg", texts)
        sig = next(s for s in found if s["text"].startswith("SIGABRT"))
        self.assertEqual(sig["offset"], 2)
        self.assertEqual(sig["encoding"], "ascii")

    def test_string_extraction_utf16(self):
        data = b"\x00\x00" + "VERSION".encode("utf-16-le") + b"\x00\x00"
        found = gp.extract_strings(data, min_len=4)
        u = [s for s in found if s["encoding"] == "utf-16-le"]
        self.assertTrue(u)
        self.assertEqual(u[0]["text"], "VERSION")
        self.assertEqual(u[0]["offset"], 2)

    def test_string_min_length_respected(self):
        data = b"abc\x00abcd\x00"
        self.assertEqual([s["text"] for s in gp.extract_strings(data, 4)],
                         ["abcd"])

    def test_thumb_census_counts_known_encodings(self):
        # one of each: nop, b ., bx lr, ldr r0,[pc,#0], push {lr}, pop {pc}
        data = struct.pack("<6H", 0xBF00, 0xE7FE, 0x4770, 0x4800,
                           0xB500, 0xBD00)
        c = gp.thumb_census(data, 0, len(data))
        self.assertEqual(c["halfwords"], 6)
        for name in ("nop", "b . (infinite loop)", "bx lr",
                     "ldr Rt,[pc,#imm8]", "push {...,lr}", "pop {...,pc}"):
            self.assertEqual(c["counts"][name], 1, name)

    def test_thumb_census_ldr_pc_covers_high_registers(self):
        # 0x4905 is `ldr r1,[pc,#0x14]` -- must count as ldr-Rt,[pc,#imm8].
        c = gp.thumb_census(struct.pack("<H", 0x4905), 0, 2)
        self.assertEqual(c["counts"]["ldr Rt,[pc,#imm8]"], 1)

    def test_thumb_census_empty_range(self):
        c = gp.thumb_census(b"\x00" * 4, 10, 20)
        self.assertEqual(c["halfwords"], 0)
        self.assertEqual(c["counts"], {})

    def test_thumb_census_odd_offset_is_aligned(self):
        c = gp.thumb_census(struct.pack("<3H", 0xBF00, 0xE7FE, 0x4770), 1, 6)
        self.assertEqual(c["start"], 0)

    def test_block_region_classification(self):
        self.assertEqual(gp.describe_block_region(0x0000, 4), "ITCM")
        self.assertEqual(gp.describe_block_region(0x3FFC, 4), "ITCM")
        self.assertEqual(gp.describe_block_region(0x40000, 4), "DTCM")
        self.assertEqual(gp.describe_block_region(0x43FFC, 4), "DTCM")
        # Anything outside both TCM windows gets the committed probe's
        # `outside-TCM` label.  Note this class is NOT an error: a6xx_gmu.c
        # :923-926 also maps blocks into icache/dcache/dummy BOs at arbitrary
        # IOVAs, and real a640/a650/a660 carry such blocks.
        self.assertEqual(gp.describe_block_region(0x57000, 4), "outside-TCM")
        self.assertEqual(gp.describe_block_region(0x10000000, 4),
                         "outside-TCM")


# ---------------------------------------------------------------------------
# 6. Real-payload-derived layout invariants (synthetic re-derivation)
# ---------------------------------------------------------------------------

class TestLayoutInvariants(FixtureMixin, unittest.TestCase):
    """These assert the *layout contract* the analysis established, using the
    synthetic fixture that encodes it.  If the real blob is ever re-probed,
    the same numbers must come out."""

    def test_raw_layout_offsets_are_where_analysis_says(self):
        data = load("a619like_raw.bin")
        report, _ = gp.analyze(data)

        # 0x0000 initial SP / 0x0004 reset vector: the ARMv7-M vector layout
        sp, rv = struct.unpack_from("<II", data, 0)
        self.assertEqual(sp, report["initial_sp"])
        self.assertEqual(rv, report["reset_vector"])

        # 0x0008 startup stub
        self.assertEqual(report["startup_stub"]["stub_offset"], 0x08)

        # 0x0200 vector table
        self.assertEqual(report["vector_table"]["offset"], 0x0200)

        # 0x3EA4 region descriptor table: 8 pairs * 8 B = 0x40, ending at
        # 0x3EE4, then zero padding out to the ITCM boundary at 0x4000.
        self.assertEqual(report["region_descriptor_table"]["offset"], 0x3EA4)
        self.assertEqual(report["region_descriptor_table"]["length"], 0x40)
        self.assertEqual(report["region_descriptor_table"]["offset"] +
                         report["region_descriptor_table"]["length"],
                         0x3EE4)

        # ITCM half ends at 0x4000; DTCM starts there
        self.assertEqual(report["dtcm"]["file_offset"], gp.TCM_SIZE)

    def test_entropy_shape_is_code_then_data(self):
        data = load("a619like_raw.bin")
        report, _ = gp.analyze(data)
        itcm = report["region_entropy"]["itcm"]
        dtcm = report["region_entropy"]["dtcm"]
        # ITCM carries instructions -> high entropy, low zero fraction
        self.assertGreater(itcm["entropy"], 4.0)
        self.assertLess(itcm["zero_fraction"], 0.5)
        # DTCM is a mostly-zero data/BSS region
        self.assertLess(dtcm["entropy"], 1.0)
        self.assertGreater(dtcm["zero_fraction"], 0.8)
        self.assertGreater(report["entropy"]["whole"], 2.0)
        self.assertLess(report["entropy"]["whole"], 6.0)

    def test_thumb_census_lands_in_the_measured_ballpark(self):
        data = load("a619like_raw.bin")
        report, _ = gp.analyze(data)
        c = report["thumb_census"]
        self.assertGreater(c["halfwords"], 1000)
        # bl prefixes and movs/adds/str/ldr dominate, as on the real image
        top = sorted(c["counts"].items(), key=lambda kv: -kv[1])[:4]
        names = [k for k, _ in top]
        self.assertTrue(any(n in names for n in
                            ("bl / blx prefix", "movs Rd,#imm8",
                             "str Rt,[Rn,#imm5]", "ldr Rt,[pc,#imm8]")),
                        names)


# ---------------------------------------------------------------------------
# 7. Fixture determinism
# ---------------------------------------------------------------------------

class TestFixtureDeterminism(unittest.TestCase):

    def test_regeneration_is_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            rc = mf.main(["--outdir", tmp])
            self.assertEqual(rc, 0)
            for name, blob in mf.build_all():
                path = os.path.join(tmp, name)
                with open(path, "rb") as f:
                    got = f.read()
                self.assertEqual(got, blob, "%s not reproducible" % name)
                self.assertEqual(hashlib.sha256(got).hexdigest(),
                                 hashlib.sha256(blob).hexdigest())

    def test_two_runs_in_memory_agree(self):
        a = dict(mf.build_all())
        b = dict(mf.build_all())
        self.assertEqual(set(a), set(b))
        for name in a:
            self.assertEqual(a[name], b[name], name)

    def test_fixtures_do_not_share_payload_bytes(self):
        """Two fixtures built from different tags must not be byte-identical.

        Note what is *intentionally* shared: the structural bytes (vector
        table, reset stub, descriptor tables) encode the layout contract and
        are therefore the same across fixtures -- that is the point of the
        fixtures.  Only the synthetic code/data fill is tag-derived, so the
        assertion is that a substantial minority of the code region differs,
        not that the files are unrelated.
        """
        a = mf.make_raw_image("tag-a")
        b = mf.make_raw_image("tag-b")
        self.assertNotEqual(a, b)
        lo, hi = 0x340, 0x3EA4          # the synthetic code body
        diff = sum(1 for x, y in zip(a[lo:hi], b[lo:hi]) if x != y)
        self.assertGreater(diff / (hi - lo), 0.25,
                           "code body is insufficiently tag-dependent")
        # ...and the whole-file difference must be non-trivial too
        whole = sum(1 for x, y in zip(a, b) if x != y)
        self.assertGreater(whole / len(a), 0.10)

    def test_raw_image_size_is_the_legacy_cap(self):
        self.assertEqual(len(mf.make_raw_image()), gp.LEGACY_FW_MAX)

    def test_container_size_matches_a640_fleet_magnitude(self):
        self.assertEqual(len(mf.make_container()), 37680)


# ---------------------------------------------------------------------------
# 8. CLI / JSON contract
# ---------------------------------------------------------------------------

class TestCLI(FixtureMixin, unittest.TestCase):

    def test_brief_exit_zero_on_clean_raw_image(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, "a619like_raw.bin"),
                              "--brief"])
        self.assertEqual(rc, 0)
        self.assertIn("raw-tcm-image", out)
        self.assertIn("header    : ABSENT", out)
        self.assertIn("initial SP:", out)

    def test_brief_exit_zero_on_container(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, "a640like_container.bin"),
                              "--brief"])
        self.assertEqual(rc, 0)
        self.assertIn("mainline-block-container", out)
        self.assertIn("header    : present", out)
        self.assertIn("struct block_header", out)

    def test_exit_nonzero_on_structural_violation(self):
        for name in ("a619like_truncated.bin", "a619like_badsp.bin",
                     "unknown.bin"):
            rc, out, _ = run_cli([os.path.join(FIXTURES, name), "--brief"])
            self.assertEqual(rc, 1, "%s should exit 1" % name)
            self.assertIn("[error]", out, name)

    def test_missing_file_exits_two(self):
        rc, _, err = run_cli([os.path.join(FIXTURES, "does-not-exist.bin")])
        self.assertEqual(rc, 2)
        self.assertIn("cannot read", err)

    def test_json_written_to_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_json = os.path.join(tmp, "r.json")
            rc, _, err = run_cli([os.path.join(FIXTURES, "a619like_raw.bin"),
                                  "--json", out_json])
            self.assertEqual(rc, 0, err)
            with open(out_json) as f:
                doc = json.load(f)
            self.assertEqual(doc["format"], "raw-tcm-image")
            self.assertEqual(doc["size"], 0x8000)
            self.assertEqual(doc["tool"], "gmu_probe.py")
            self.assertIn("thumb_census", doc)
            self.assertIn("entropy", doc)
            self.assertIn("diagnostic_counts", doc)
            # JSON must be pure-JSON types (no bytes leaked through)
            json.dumps(doc)

    def test_json_to_stdout(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, "a640like_container.bin"),
                              "--json", "-"])
        self.assertEqual(rc, 0)
        doc = json.loads(out)
        self.assertEqual(doc["format"], "mainline-block-container")
        self.assertTrue(doc["header_present"])

    def test_json_records_hashes(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "h.json")
            run_cli([os.path.join(FIXTURES, "a619like_raw.bin"), "--json", p])
            with open(p) as f:
                doc = json.load(f)
            with open(os.path.join(FIXTURES, "a619like_raw.bin"), "rb") as f:
                data = f.read()
            self.assertEqual(doc["md5"], hashlib.md5(data).hexdigest())
            self.assertEqual(doc["sha256"], hashlib.sha256(data).hexdigest())

    def test_thumb_range_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "t.json")
            run_cli([os.path.join(FIXTURES, "a619like_raw.bin"),
                     "--json", p, "--thumb-range", "0x240:0x3ea4"])
            with open(p) as f:
                doc = json.load(f)
            self.assertEqual(doc["thumb_census"]["start"], 0x240)
            self.assertEqual(doc["thumb_census"]["end"], 0x3EA4)

    def test_strings_min_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            p4 = os.path.join(tmp, "s4.json")
            p12 = os.path.join(tmp, "s12.json")
            run_cli([os.path.join(FIXTURES, "a619like_raw.bin"),
                     "--json", p4, "--strings-min", "4"])
            run_cli([os.path.join(FIXTURES, "a619like_raw.bin"),
                     "--json", p12, "--strings-min", "12"])
            with open(p4) as f:
                n4 = len(json.load(f)["strings"])
            with open(p12) as f:
                n12 = len(json.load(f)["strings"])
            self.assertGreaterEqual(n4, n12)


if __name__ == "__main__":
    unittest.main(verbosity=2)
