#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""test_a650_fleet_probe.py -- unittest suite for the a650 fleet probe.

Run from this directory:

    python3 -m unittest -v test_a650_fleet_probe

The suite is organised in the order the probe applies its logic:

  1. RULE 0 premise -- the public sources document a ``struct block_header``
     chain and a ``gmu->legacy`` raw path, and the SQE version contract is a
     four-way branch, not one rule.
  2. Format classification, positive AND negative: every fixture is asserted
     to land in its intended class, and every *near-miss* is asserted to be
     rejected (the a650 header on a truncated body, a raw image of the wrong
     length, a container whose last record overruns EOF).
  3. Vector-table decode, including the a650-specific "word0 is not an SP"
     shape that distinguishes it from a619/a640.
  4. Reset-stub decode: MSP/PSP/VTOR literals, the stack paint loop, the
     boot-counter addends, the branch target.
  5. SQE version extraction and the per-arm kernel verdict, in both
     directions (pass and fail).
  6. The cross-generation table.
  7. Malformed and truncated input.
  8. CLI and JSON contracts, including exit codes.
  9. Fixture determinism and the no-proprietary-bytes guarantee.

All fixtures are synthetic (``make_fixture.py``).  No vendor byte is read.
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

import a650_fleet_probe as ap      # noqa: E402
import make_fixture as mf         # noqa: E402

PROBE = os.path.join(HERE, "a650_fleet_probe.py")
FIXTURES = os.path.join(HERE, "fixtures")

A650 = "a650like_container.bin"
A640 = "a640like_container.bin"
A619 = "a619like_raw.bin"
OVERRUN = "container_overrun.bin"
BADSP = "raw_badsp.bin"
TRUNC = "raw_truncated.bin"
SQE_OK = "sqe_ok.bin"
SQE_OLD = "sqe_old.bin"
UNKNOWN = "unknown.bin"


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def load(name):
    with open(os.path.join(FIXTURES, name), "rb") as f:
        return f.read()


def analyze(fixture, **kw):
    """Load a fixture and analyse it.  ``name=`` is forwarded to the probe as
    the catalog filename under test."""
    with open(os.path.join(FIXTURES, fixture), "rb") as f:
        data = f.read()
    return ap.analyze(data, **kw)


def codes(report):
    return [d["code"] for d in report["diagnostics"]]


def run_cli(args, **kw):
    proc = subprocess.run([sys.executable, "-I", PROBE] + args,
                          capture_output=True, text=True, **kw)
    return proc.returncode, proc.stdout, proc.stderr


class FixtureMixin:
    """Regenerate fixtures once, so the suite never depends on stale bytes."""

    @classmethod
    def setUpClass(cls):
        os.makedirs(FIXTURES, exist_ok=True)
        for name, blob in mf.build_all():
            with open(os.path.join(FIXTURES, name), "wb") as f:
                f.write(blob)


# ---------------------------------------------------------------------------
# 1. RULE 0: the public-source premise
# ---------------------------------------------------------------------------

class TestPublicSourcePremise(unittest.TestCase):
    """Pin the documented facts the probe is built on, so a future reader
    cannot silently re-introduce an assumed-but-wrong structure."""

    def test_block_header_is_four_u32_and_16_bytes(self):
        # a6xx_gmu.c:857-863
        self.assertEqual(ap.BLOCK_HEADER.size, 16)
        self.assertEqual(ap.BLOCK_HEADER.format, "<IIII")

    def test_two_loader_paths_are_modelled(self):
        # a6xx_gmu.c:894 selects on gmu->legacy; both branches are modelled.
        raw, _ = analyze(A619)
        box, _ = analyze(A640)
        self.assertEqual(raw["format"], "raw-tcm")
        self.assertEqual(box["format"], "container")
        self.assertIn("gmu->legacy", raw["load_path"]["kernel"])
        self.assertIn("block_header", box["header_struct"])

    def test_legacy_size_cap_is_0x8000(self):
        # a6xx_gmu.c:896
        self.assertEqual(ap.LEGACY_FW_MAX, 0x8000)
        self.assertEqual(len(load(A619)), ap.LEGACY_FW_MAX)

    def test_dtcm_probe_offset_is_0xff8(self):
        # a6xx_gmu.c:311 reads REG_A6XX_GMU_CM3_DTCM_START + 0xff8
        self.assertEqual(ap.FW_INIT_PROBE_OFF, 0xFF8)

    def test_vtor_is_armv7m_scb_vtor(self):
        self.assertEqual(ap.VTOR_ADDR, 0xE000ED08)

    def test_sqe_floors_are_four_distinct_branches(self):
        # a6xx_gpu.c:997-1041
        modes = {k: v["mode"] for k, v in ap.SQE_FLOORS.items()}
        self.assertEqual(modes["a630_sqe.fw"], "patched-or-floor")
        self.assertEqual(modes["a650_sqe.fw"], "floor")
        self.assertEqual(modes["a660_sqe.fw"], "unconditional")
        self.assertEqual(modes["a702_sqe.fw"], "a7xx-early-return")
        self.assertEqual(ap.SQE_FLOORS["a650_sqe.fw"]["floor"], 0x095)

    def test_payload_tag_is_not_the_host_sentinel(self):
        # 0xEFBEADDE on disk vs 0xDEADBEEF in host order: different words.
        self.assertEqual(struct.pack("<I", ap.PAYLOAD_TAG), b"\xde\xad\xbe\xef")
        self.assertEqual(struct.pack("<I", ap.HOST_SENTINEL),
                         b"\xef\xbe\xad\xde")
        self.assertNotEqual(ap.PAYLOAD_TAG, ap.HOST_SENTINEL)

    def test_only_two_catalog_entries_name_a_650_gmu_and_three_name_its_sqe(
            self):
        gmu = ap.catalog_for("a650_gmu.bin")
        sqe = ap.catalog_for("a650_sqe.fw")
        self.assertEqual(gmu["entry_count"], 1)
        self.assertEqual(gmu["entries"][0]["chip_ids"], "0x06050002")
        self.assertEqual(sqe["entry_count"], 3)
        # the SQE outlives the GMU file: a621 and a623 also name it
        self.assertIn("0x06020100", {e["chip_ids"] for e in sqe["entries"]})
        self.assertIn("0x06020300", {e["chip_ids"] for e in sqe["entries"]})


# ---------------------------------------------------------------------------
# 2. Format classification -- positive
# ---------------------------------------------------------------------------

class TestClassificationPositive(FixtureMixin, unittest.TestCase):

    def test_a650_fixture_is_a_container(self):
        r, _ = analyze(A650)
        self.assertEqual(r["format"], "container")
        self.assertTrue(r["header_present"])

    def test_a650_walk_reaches_exact_eof(self):
        r, _ = analyze(A650)
        self.assertEqual(r["walk_termination"]["status"], "exact-eof")
        self.assertEqual(r["walk_termination"]["offset"], len(load(A650)))

    def test_a650_block_census(self):
        r, _ = analyze(A650)
        self.assertEqual(r["block_count"], 16)
        self.assertEqual(r["payload_block_count"], 7)
        self.assertEqual(r["manifest_block_count"], 9)

    def test_a650_dtcm_base_is_derived_from_the_blocks(self):
        r, _ = analyze(A650)
        self.assertEqual(r["dtcm_base"], 0x10004000)
        self.assertIn("0x10004000", r["dtcm_basis"])

    def test_a640_fixture_is_a_container_at_the_legacy_dtcm_base(self):
        r, _ = analyze(A640)
        self.assertEqual(r["format"], "container")
        self.assertEqual(r["dtcm_base"], 0x00040000)
        self.assertEqual(r["block_count"], 7)
        self.assertEqual(r["manifest_block_count"], 0)

    def test_a619_fixture_is_raw_tcm(self):
        r, _ = analyze(A619)
        self.assertEqual(r["format"], "raw-tcm")
        self.assertFalse(r["header_present"])

    def test_sqe_fixtures_classify_as_sqe(self):
        for name in (SQE_OK, SQE_OLD):
            r, _ = analyze(name)
            self.assertEqual(r["format"], "sqe", name)
            self.assertEqual(r["kind"], "sqe", name)

    def test_all_payload_blocks_carry_the_tag(self):
        r, _ = analyze(A650)
        self.assertEqual(r["payload_tags"], ["0xefbeadde"])
        self.assertTrue(all(b["tag_is_payload"]
                            for b in r["blocks"] if b["size"]))

    def test_windows_match_the_block_addresses(self):
        r, _ = analyze(A650)
        self.assertEqual(set(r["windows"]), {"ITCM", "icache", "DTCM"})
        self.assertEqual(r["windows"]["DTCM"]["blocks"], 2)
        self.assertEqual(r["windows"]["DTCM"]["bytes"], 3776 + 24)


# ---------------------------------------------------------------------------
# 3. Format classification -- negative (the "near miss" cases)
# ---------------------------------------------------------------------------

class TestClassificationNegative(FixtureMixin, unittest.TestCase):

    def test_container_that_overruns_eof_is_rejected(self):
        r, _ = analyze(OVERRUN)
        self.assertEqual(r["format"], "unknown")
        self.assertIn("unrecognised-layout", codes(r))

    def test_truncated_raw_image_is_rejected(self):
        # Right prologue, wrong length: the legacy path cannot copy it.
        r, _ = analyze(TRUNC)
        self.assertEqual(r["format"], "unknown")
        self.assertLess(len(load(TRUNC)), ap.LEGACY_FW_MAX)

    def test_random_bytes_are_rejected(self):
        r, _ = analyze(UNKNOWN)
        self.assertEqual(r["format"], "unknown")
        self.assertIn("unrecognised-layout", codes(r))

    def test_empty_file_is_rejected(self):
        r, diag = ap.analyze(b"")
        self.assertEqual(r["format"], "unknown")
        self.assertEqual(codes(r), ["empty"])
        self.assertTrue(diag.has_errors)

    def test_a_container_is_not_mistaken_for_an_sqe(self):
        r, _ = analyze(A650)
        self.assertNotEqual(r["format"], "sqe")

    def test_an_sqe_is_not_mistaken_for_a_container(self):
        r, _ = analyze(SQE_OK)
        self.assertNotEqual(r["format"], "container")
        self.assertNotIn("block_count", r)

    def test_a_650_header_on_a_short_body_is_not_a_container(self):
        """Take a real container, keep the first record, drop the rest.  The
        first record declares more payload than the file now holds."""
        data = load(A650)
        blocks, _ = ap.walk_block_headers(data)
        first_payload = next(b for b in blocks if b["size"])
        cut = first_payload["offset"] + 16 + first_payload["size"] // 2
        cls = ap.classify_format(data[:cut])
        self.assertEqual(cls["format"], "unknown")

    def test_raw_image_of_the_wrong_size_is_not_raw(self):
        data = load(A619)[:ap.LEGACY_FW_MAX - 4]
        self.assertEqual(ap.classify_format(data)["format"], "unknown")

    def test_sqe_zero_lead_dword_is_required(self):
        data = bytearray(load(SQE_OK))
        data[0] = 0x01                        # break the stripped prefix
        self.assertEqual(ap.classify_format(bytes(data))["format"], "unknown")

    def test_sqe_shape_requires_a_non_zero_version(self):
        data = bytearray(load(SQE_OK))
        struct.pack_into("<I", data, 4, 0)
        self.assertFalse(ap.sqe_shape_plausible(bytes(data)))

    def test_sqe_shape_rejects_tiny_and_misaligned_files(self):
        self.assertFalse(ap.sqe_shape_plausible(b"\0\0\0\0" + b"\x11" * 64))
        ok = bytearray(load(SQE_OK))
        self.assertTrue(ap.sqe_shape_plausible(bytes(ok)))
        self.assertFalse(ap.sqe_shape_plausible(bytes(ok) + b"\x00"))


# ---------------------------------------------------------------------------
# 4. Vector-table decode
# ---------------------------------------------------------------------------

class TestVectorTable(FixtureMixin, unittest.TestCase):

    def test_a650_table_is_at_0x200_and_has_16_architectural_vectors(self):
        r, _ = analyze(A650)
        vt = r["image"]["vector_table"]
        self.assertEqual(vt["offset"], 0x200)
        self.assertEqual(len(vt["words"]), 16)

    def test_a650_word0_is_not_a_stack_pointer(self):
        """The a650-family discriminator: a handler table with no SP slot."""
        r, _ = analyze(A650)
        self.assertEqual(r["image"]["vt_word0_role"], "unused (zero)")
        self.assertEqual(r["image"]["vector_table"]["words"][0], 0)

    def test_a619_word0_repeats_the_initial_sp(self):
        """The pre-a650 shape: word0 IS the ARMv7-M initial-SP slot."""
        r, _ = analyze(A619)
        self.assertEqual(r["image"]["vt_word0_role"], "initial-SP copy")
        self.assertEqual(r["image"]["vector_table"]["words"][0],
                         r["image"]["msp"])

    def test_reset_slot_matches_the_itcm_reset_vector(self):
        for name in (A650, A640, A619):
            r, _ = analyze(name)
            vt = r["image"]["vector_table"]
            self.assertEqual(vt["words"][1], r["image"]["reset_vector_word"],
                             name)

    def test_every_non_zero_handler_is_odd_and_resolves(self):
        for name in (A650, A640, A619):
            r, _ = analyze(name)
            self.assertTrue(r["image"]["vector_targets_resolve"], name)
            for i, w in enumerate(r["image"]["vector_table"]["words"]):
                if i == 0 or w == 0:
                    continue
                self.assertEqual(w & 1, 1, "%s vector %d" % (name, i))

    def test_irq_tail_is_64_entries_with_one_handler(self):
        r, _ = analyze(A650)
        irq = r["image"]["irq_tail"]
        self.assertEqual(irq["count"], 64)
        self.assertTrue(irq["single_handler"])
        self.assertEqual(len(irq["distinct_targets"]), 1)

    def test_vector_names_cover_the_architecture(self):
        # ARMv7-M exception table, indices 0..15
        self.assertEqual(ap.VECTOR_NAMES[0], "Initial SP")
        self.assertEqual(ap.VECTOR_NAMES[1], "Reset")
        self.assertEqual(ap.VECTOR_NAMES[11], "SVCall")
        self.assertEqual(ap.VECTOR_NAMES[14], "PendSV")
        self.assertEqual(ap.VECTOR_NAMES[15], "SysTick")
        self.assertEqual(len(ap.VECTOR_NAMES), 16)

    def test_vector_table_absent_when_no_block_covers_0x200(self):
        """The a660 family never loads the 0x200 window; the probe must say
        so instead of inventing a table out of zero-fill."""
        img = ap.LoadedImage([(0x400, b"\x00" * 16)])
        self.assertIsNone(ap.read_vector_table(img, 0x200))
        self.assertFalse(img.contains(0x200, 4))


# ---------------------------------------------------------------------------
# 5. Reset-stub decode
# ---------------------------------------------------------------------------

class TestResetStub(FixtureMixin, unittest.TestCase):

    def test_a650_entry_is_itcm_0x10(self):
        r, _ = analyze(A650)
        stub = r["image"]["reset_stub"]
        self.assertEqual(r["image"]["reset_vector_word"], 0x11)
        self.assertEqual(stub["entry"], 0x10)

    def test_a650_stub_shape_names_every_fact_it_establishes(self):
        r, _ = analyze(A650)
        self.assertEqual(r["image"]["reset_stub"]["shape"],
                         "cnt+msp+psp+vtor+paint+bw")

    def test_a640_stub_has_no_counter_and_no_paint(self):
        """The format boundary inside the container class."""
        r, _ = analyze(A640)
        stub = r["image"]["reset_stub"]
        self.assertEqual(stub["shape"], "msp+psp+vtor+bw")
        self.assertEqual(stub["counter_sites"], [])
        self.assertIsNone(stub["paint"])
        self.assertEqual(stub["entry"], 0x08)

    def test_a650_msp_is_dtcm_top_minus_0x80(self):
        r, _ = analyze(A650)
        im = r["image"]
        self.assertEqual(im["msp"], 0x10007F80)
        self.assertEqual(im["msp_offset_from_dtcm_top"], 0x80)
        self.assertIn("msp-at-conventional-slot", codes(r))

    def test_a650_stack_page_is_not_written_by_any_block(self):
        """The measured a650 bound: the DTCM blocks end at 0x10004ec0 and
        resume at 0x10007fdc, so the initial SP at 0x10007f80 falls in a gap.
        The stack is established at runtime by the paint loop, not by the
        container."""
        r, _ = analyze(A650)
        im = r["image"]
        self.assertFalse(im["msp_covered_by_a_block"])
        self.assertIn("msp-unmapped", codes(r))
        # and the paint loop is what establishes it
        self.assertEqual(im["stack_paint"]["base"] + im["stack_paint"]["bytes"],
                         im["msp"])

    def test_a650_psp_holds_the_host_sentinel(self):
        r, _ = analyze(A650)
        self.assertEqual(r["image"]["reset_stub"]["psp"], ap.HOST_SENTINEL)

    def test_a650_paint_ends_exactly_at_the_initial_sp(self):
        r, _ = analyze(A650)
        paint = r["image"]["stack_paint"]
        self.assertEqual(paint["bytes"], 0xF80)
        self.assertEqual(paint["base"] + paint["bytes"], r["image"]["msp"])
        self.assertEqual(paint["fill"], mf.SYNTH_FILL)
        self.assertIn("stack-paint", codes(r))

    def test_a650_vtor_store_targets_scb_vtor(self):
        r, _ = analyze(A650)
        stub = r["image"]["reset_stub"]
        self.assertEqual(stub["vtor_value"], 0x200)
        self.assertEqual(stub["vtor_reg"], ap.VTOR_ADDR)
        self.assertTrue(stub["vtor_reg_is_scb_vtor"])

    def test_a650_counter_is_bumped_twice(self):
        r, _ = analyze(A650)
        sites = r["image"]["reset_stub"]["counter_sites"]
        self.assertEqual(len(sites), 2)
        self.assertEqual([s["addend"] for s in sites], [1, 2])
        self.assertEqual(len({s["counter_addr"] for s in sites}), 1)

    def test_a650_all_literals_resolve_to_known_targets(self):
        """Every literal must be one of: inside the ITCM block, inside the
        DTCM window the prologue paints, the PSP sentinel, or SCB->VTOR.
        A literal pointing anywhere else would mean the decode drifted."""
        r, _ = analyze(A650)
        im = r["image"]
        paint = im["stack_paint"]
        dtcm_lo = 0x10004000
        dtcm_hi = dtcm_lo + ap.DTCM_SIZE
        allowed_exact = {ap.HOST_SENTINEL, ap.VTOR_ADDR, 0x200}
        for lit in im["reset_stub"]["literals"]:
            v = lit["value"]
            self.assertIsNotNone(v, lit)
            if v in allowed_exact:
                continue
            if dtcm_lo <= v < dtcm_hi:
                # the DTCM counter/tail or the paint base
                self.assertTrue(v >= paint["base"], hex(v))
                continue
            self.assertLess(v, ap.ITCM_SIZE, "literal 0x%08x" % v)

    def test_a650_branch_target_days_inside_loaded_code(self):
        r, _ = analyze(A650)
        im = r["image"]
        target = im["reset_stub"]["branch_target"]
        self.assertTrue(im["reset_stub"]["terminated"])
        self.assertEqual(target, 0x420)
        self.assertNotEqual(target, 0x400)   # fixture uses its own constant

    def test_stub_stops_at_the_first_unconditional_transfer(self):
        r, _ = analyze(A650)
        dis = r["image"]["reset_stub"]["disassembly"]
        self.assertEqual(dis[-1]["mnemonic"].split()[0], "b.w")

    def test_raw_stub_has_no_paint_or_counter(self):
        r, _ = analyze(A619)
        stub = r["image"]["reset_stub"]
        self.assertEqual(stub["shape"], "msp+psp+vtor+bw")
        self.assertEqual(stub["entry"], 0x08)
        self.assertEqual(stub["vtor_value"], 0x200)


# ---------------------------------------------------------------------------
# 6. SQE version extraction and the kernel verdict
# ---------------------------------------------------------------------------

class TestSqeVersion(FixtureMixin, unittest.TestCase):

    def test_version_is_read_from_dword_1(self):
        """dword0 is stripped by adreno_fw_create_bo, so the driver's buf[0]
        is file dword 1."""
        ver = ap.read_sqe_version(load(SQE_OK))
        self.assertEqual(ver["lead_dword"], 0)
        self.assertEqual(ver["version_bits"], 0x112)

    def test_version_text_is_hex_major_dot_two_digit_minor(self):
        r, _ = analyze(SQE_OK)
        self.assertEqual(r["version_text"], "1.12")
        r, _ = analyze(SQE_OLD)
        self.assertEqual(r["version_text"], "0.93")

    def test_new_enough_sqe_passes(self):
        r, diag = analyze(SQE_OK, name="a650_sqe.fw")
        self.assertTrue(r["kernel_verdict"]["passes"])
        self.assertFalse(diag.has_errors)
        self.assertIn("sqe-version", codes(r))

    def test_old_sqe_fails_with_the_eperm_consequence(self):
        r, diag = analyze(SQE_OLD, name="a650_sqe.fw")
        self.assertFalse(r["kernel_verdict"]["passes"])
        self.assertTrue(diag.has_errors)
        self.assertIn("sqe-too-old", codes(r))
        msg = next(d["message"] for d in r["diagnostics"]
                   if d["code"] == "sqe-too-old")
        self.assertIn("-EPERM", msg)
        self.assertIn("no GPU registers", msg)

    def test_the_floor_is_exactly_0x095(self):
        self.assertTrue(ap.sqe_verdict(0x095, "a650_sqe.fw")["passes"])
        self.assertFalse(ap.sqe_verdict(0x094, "a650_sqe.fw")["passes"])

    def test_a630_accepts_the_patched_nibble_or_1_90(self):
        self.assertTrue(ap.sqe_verdict(0x190, "a630_sqe.fw")["passes"])
        self.assertFalse(ap.sqe_verdict(0x18F, "a630_sqe.fw")["passes"])
        # the patched form: dword1 low nibble == 0xa does not change the
        # version bits, so pass patched_ok explicitly
        self.assertTrue(ap.sqe_verdict(0x100, "a630_sqe.fw",
                                       patched_ok=True)["passes"])

    def test_a660_accepts_unconditionally(self):
        for bits in (0x001, 0x000, 0xABC):
            self.assertTrue(ap.sqe_verdict(bits, "a660_sqe.fw")["passes"])

    def test_a702_uses_the_a7xx_early_return(self):
        v = ap.sqe_verdict(0x001, "a702_sqe.fw")
        self.assertTrue(v["passes"])
        self.assertEqual(v["mode"], "a7xx-early-return")

    def test_unknown_name_is_refused(self):
        v = ap.sqe_verdict(0x112, "a999_sqe.fw")
        self.assertFalse(v["passes"])
        self.assertEqual(v["mode"], "unknown-gpu")

    def test_bo_size_is_file_size_minus_four(self):
        r, _ = analyze(SQE_OK)
        self.assertEqual(r["body"]["bo_bytes"], len(load(SQE_OK)) - 4)

    def test_name_inference_uses_the_version_high_bits(self):
        self.assertEqual(ap._infer_sqe_name(load(SQE_OK)), "a650_sqe.fw")
        a730 = b"\0\0\0\0" + struct.pack("<I", 0x01730181) + b"\0" * 64
        self.assertEqual(ap._infer_sqe_name(a730), "a730_sqe.fw")
        a740 = b"\0\0\0\0" + struct.pack("<I", 0x01740181) + b"\0" * 64
        self.assertEqual(ap._infer_sqe_name(a740), "a740_sqe.fw")
        self.assertEqual(ap._infer_sqe_name(b"\0\0\0\0" +
                                            struct.pack("<I", 0x09990001)),
                         "unknown")


# ---------------------------------------------------------------------------
# 7. Cross-generation table
# ---------------------------------------------------------------------------

class TestCrossGeneration(FixtureMixin, unittest.TestCase):

    def test_row_reports_the_discriminating_fields(self):
        row = ap.cross_generation_row(os.path.join(FIXTURES, A650))
        self.assertEqual(row["format"], "container")
        self.assertEqual(row["records"], 16)
        self.assertEqual(row["u32_0"], "0x10007f80")
        self.assertEqual(row["u32_1"], "0x00000011")
        self.assertTrue(row["vt_at_0x200"])
        self.assertEqual(row["vt_word0"], "0x00000000")
        self.assertEqual(row["reset_entry"], "0x10")
        self.assertEqual(row["stub_shape"], "cnt+msp+psp+vtor+paint+bw")
        self.assertEqual(row["stub_paint_bytes"], 0xF80)

    def test_raw_row_has_no_record_count(self):
        row = ap.cross_generation_row(os.path.join(FIXTURES, A619))
        self.assertEqual(row["format"], "raw-tcm")
        self.assertIsNone(row["records"])
        self.assertEqual(row["vt_word0"], "0x00043f80")

    def test_sqe_row_stops_after_the_classification(self):
        row = ap.cross_generation_row(os.path.join(FIXTURES, SQE_OK))
        self.assertEqual(row["format"], "sqe")
        self.assertIsNone(row["u32_0"])

    def test_missing_file_becomes_an_error_row_not_an_exception(self):
        row = ap.cross_generation_row(os.path.join(FIXTURES, "nope.bin"))
        self.assertIn("error", row)

    def test_table_renders_all_rows_with_a_header(self):
        rows = [ap.cross_generation_row(os.path.join(FIXTURES, n))
                for n in (A650, A640, A619)]
        text = ap.format_crossgen_table(rows)
        lines = text.splitlines()
        self.assertIn("file", lines[0])
        self.assertEqual(len(lines), 2 + 3)          # header + rule + 3 rows
        for name in (A650, A640, A619):
            self.assertIn(name, text)

    def test_table_columns_are_declared(self):
        keys = [k for k, _ in ap.CROSSGEN_COLUMNS]
        for k in ("file", "bytes", "format", "vt@200", "vt_w0", "entry",
                  "stub shape"):
            self.assertIn(k, keys)

    def test_error_row_renders_without_crashing(self):
        text = ap.format_crossgen_table([{"file": "x.bin", "error": "boom"}])
        self.assertIn("ERROR boom", text)


# ---------------------------------------------------------------------------
# 8. Malformed and truncated input
# ---------------------------------------------------------------------------

class TestMalformedInput(FixtureMixin, unittest.TestCase):

    def test_bad_msp_is_an_error(self):
        r, diag = analyze(BADSP)
        self.assertTrue(diag.has_errors)
        self.assertIn("bad-msp", codes(r))

    def test_bad_msp_still_classifies_as_raw(self):
        """A structurally valid image with a bad SP is a raw image with a
        defect, not an unknown format.  The two verdicts must be distinct."""
        r, _ = analyze(BADSP)
        self.assertEqual(r["format"], "raw-tcm")
        self.assertIn("bad-msp", codes(r))

    def test_every_prefix_of_a_container_is_handled(self):
        data = load(A650)
        for cut in (0, 1, 4, 15, 16, 17, 100, 4096, len(data) - 1):
            with self.subTest(cut=cut):
                r, _ = ap.analyze(data[:cut])
                self.assertIn(r["format"], ("unknown", "container"))

    def test_walk_reports_the_overflow_offset(self):
        _, term = ap.walk_block_headers(load(OVERRUN))
        self.assertEqual(term["status"], "overflow")
        self.assertIn("detail", term)
        self.assertGreater(term["declared_next"], term["file_size"])

    def test_walk_stops_at_the_block_limit(self):
        # a chain of 40 valid empty records with max_blocks=8
        rec = struct.pack("<IIII", 0, 0, 1, 1) * 40
        blocks, term = ap.walk_block_headers(rec, max_blocks=8)
        self.assertEqual(len(blocks), 8)
        self.assertEqual(term["status"], "block-limit")

    def test_reset_vector_with_thumb_bit_clear_is_an_error(self):
        data = bytearray(load(A619))
        struct.pack_into("<I", data, 4, 0x00000008)   # clear bit 0
        r, diag = ap.analyze(bytes(data))
        self.assertTrue(diag.has_errors)
        self.assertIn("reset-not-thumb", codes(r))

    def test_reset_vector_pointing_outside_the_image_is_an_error(self):
        data = bytearray(load(A619))
        struct.pack_into("<I", data, 4, 0xDEADBEEF)
        r, diag = ap.analyze(bytes(data))
        self.assertTrue(diag.has_errors)
        self.assertIn("reset-out-of-image", codes(r))

    def test_non_thumb_vector_target_is_an_error(self):
        data = bytearray(load(A650))
        blocks, _ = ap.walk_block_headers(bytes(data))
        # the *payload* block at 0x200 (the manifest record has size 0)
        vt = next(b for b in blocks if b["addr"] == 0x200 and b["size"])
        # vector 2 (NMI) lives at payload offset 8; store an even address
        off = vt["offset"] + 16 + 8
        self.assertEqual(struct.unpack_from("<I", data, off)[0], 0x4C1)
        struct.pack_into("<I", data, off, 0x4C2)
        r, diag = ap.analyze(bytes(data))
        self.assertTrue(diag.has_errors)
        self.assertIn("vector-targets", codes(r))
        self.assertFalse(r["image"]["vector_targets_resolve"])

    def test_entropy_of_one_repeated_byte_is_zero(self):
        self.assertEqual(ap.shannon_entropy(b"\x00" * 4096), 0.0)

    def test_entropy_bounds(self):
        self.assertAlmostEqual(ap.shannon_entropy(bytes(range(256))), 8.0,
                               places=6)

    def test_entropy_profile_covers_the_whole_file(self):
        prof = ap.entropy_profile(load(A650)[:5000], 512)
        self.assertEqual(sum(p["length"] for p in prof), 5000)
        self.assertEqual(prof[0]["offset"], 0)


# ---------------------------------------------------------------------------
# 9. CLI and JSON contracts
# ---------------------------------------------------------------------------

class TestCLI(FixtureMixin, unittest.TestCase):

    def test_brief_exit_zero_on_a_clean_container(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--brief"])
        self.assertEqual(rc, 0)
        self.assertIn("format    : container", out)
        self.assertIn("cnt+msp+psp+vtor+paint+bw", out)

    def test_brief_exit_zero_on_raw_image(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A619), "--brief"])
        self.assertEqual(rc, 0)
        self.assertIn("format    : raw-tcm", out)

    def test_exit_one_on_structural_violation(self):
        for name in (OVERRUN, TRUNC, UNKNOWN, SQE_OLD):
            rc, _, _ = run_cli([os.path.join(FIXTURES, name), "--brief"])
            self.assertEqual(rc, 1, name)

    def test_exit_zero_on_passing_sqe(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, SQE_OK), "--brief"])
        self.assertEqual(rc, 0)
        self.assertIn("1.12", out)

    def test_missing_file_exits_two(self):
        rc, _, err = run_cli([os.path.join(FIXTURES, "does-not-exist.bin"),
                              "--brief"])
        self.assertEqual(rc, 2)
        self.assertIn("cannot read", err)

    def test_json_to_stdout_is_valid_and_complete(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-"])
        self.assertEqual(rc, 0)
        rep = json.loads(out)
        self.assertEqual(rep["format"], "container")
        self.assertEqual(rep["size"], len(load(A650)))
        self.assertIn("blocks", rep)
        self.assertIn("diagnostics", rep)

    def test_json_written_to_a_file(self):
        with tempfile.TemporaryDirectory() as td:
            dest = os.path.join(td, "r.json")
            rc, _, err = run_cli([os.path.join(FIXTURES, A650),
                                  "--json", dest])
            self.assertEqual(rc, 0)
            self.assertIn("wrote", err)
            with open(dest) as f:
                rep = json.load(f)
            self.assertEqual(rep["format"], "container")

    def test_json_records_hashes(self):
        data = load(A650)
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-"])
        rep = json.loads(out)
        self.assertEqual(rep["md5"], hashlib.md5(data).hexdigest())
        self.assertEqual(rep["sha256"], hashlib.sha256(data).hexdigest())

    def test_cross_gen_table_appears_in_the_output(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--brief",
                              "--cross-gen", os.path.join(FIXTURES, A640),
                              os.path.join(FIXTURES, A619)])
        self.assertEqual(rc, 0)
        self.assertIn("cross-generation table", out)
        self.assertIn(A640, out)
        self.assertIn(A619, out)

    def test_cross_gen_rows_land_in_the_json(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-",
                              "--cross-gen", os.path.join(FIXTURES, A640)])
        rep = json.loads(out)
        self.assertEqual(len(rep["cross_generation"]), 2)

    def test_strings_min_changes_the_count(self):
        _, loose, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-",
                               "--strings-min", "4"])
        _, tight, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-",
                               "--strings-min", "12"])
        a = json.loads(loose)["image"]["string_count"]
        b = json.loads(tight)["image"]["string_count"]
        self.assertLessEqual(b, a)

    def test_entropy_block_option_is_honoured(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, A650), "--json", "-",
                              "--entropy-block", "1024"])
        rep = json.loads(out)
        self.assertEqual(rep["entropy_block"], 1024)
        self.assertEqual(rep["entropy_profile"][0]["length"], 1024)

    def test_sqe_name_option_drives_the_verdict(self):
        rc, out, _ = run_cli([os.path.join(FIXTURES, SQE_OK), "--json", "-",
                              "--sqe-name", "a660_sqe.fw"])
        rep = json.loads(out)
        self.assertEqual(rep["sqe_name"], "a660_sqe.fw")
        self.assertTrue(rep["kernel_verdict"]["passes"])

    def test_kind_hint_cannot_override_a_positive_classification(self):
        """--kind is a hint.  Forcing 'gmu' on an SQE must not make the probe
        decode a fake GMU out of it."""
        rc, out, _ = run_cli([os.path.join(FIXTURES, SQE_OK), "--json", "-",
                              "--kind", "gmu"])
        rep = json.loads(out)
        self.assertEqual(rep["kind"], "sqe")
        self.assertEqual(rep["format"], "sqe")

    def test_kind_hint_cannot_hide_a_structural_failure(self):
        rc, _, _ = run_cli([os.path.join(FIXTURES, UNKNOWN), "--brief",
                            "--kind", "sqe"])
        self.assertEqual(rc, 1)


# ---------------------------------------------------------------------------
# 10. Fixture determinism and the no-proprietary-bytes guarantee
# ---------------------------------------------------------------------------

class TestFixtureGuarantees(unittest.TestCase):

    def test_regeneration_is_byte_identical(self):
        first = dict(mf.build_all())
        second = dict(mf.build_all())
        self.assertEqual(set(first), set(second))
        for name in first:
            self.assertEqual(first[name], second[name], name)

    def test_a_second_process_produces_the_same_bytes(self):
        out = subprocess.run(
            [sys.executable, "-I", os.path.join(HERE, "make_fixture.py"),
             "--outdir", tempfile.mkdtemp()],
            capture_output=True, text=True, check=True)
        self.assertIn("byte-identical", out.stdout)

    def test_expected_fixture_set(self):
        self.assertEqual({n for n, _ in mf.build_all()},
                         {A650, A640, A619, OVERRUN, BADSP, TRUNC,
                          SQE_OK, SQE_OLD, UNKNOWN})

    def test_fleet_magnitudes_are_reproduced(self):
        sizes = dict((n, len(b)) for n, b in mf.build_all())
        self.assertEqual(sizes[A650], 41548)
        self.assertEqual(sizes[A640], 37680)
        self.assertEqual(sizes[A619], 32768)

    def test_fixtures_do_not_share_bytes_with_each_other(self):
        blobs = dict(mf.build_all())
        digests = {n: hashlib.sha256(b).digest() for n, b in blobs.items()}
        self.assertEqual(len(set(digests.values())), len(digests))

    def test_fixtures_use_their_own_constants_not_measured_ones(self):
        """The synthetic fill and counter magic must differ from the values
        the real fleet ships, so no fixture byte can be mistaken for a
        payload byte."""
        self.assertNotEqual(mf.SYNTH_FILL, 0xAAAAAAAA)   # measured paint fill
        self.assertNotEqual(mf.SYNTH_COUNTER_MAGIC, 0xFFFFFFFF)
        # The paint constant is carried as a ThumbExpandImm immediate, not as
        # a stored literal word, so look for the instruction, not the value.
        self.assertEqual(load(A650).count(
            mf.movw_imm(2, mf.SYNTH_FILL)), 1)

    def test_measured_fill_value_does_not_appear_in_any_fixture(self):
        """0xaaaaaaaa is the measured a650 paint fill.  If a fixture were
        built by truncating a real payload, this encoding would show up."""
        measured = mf.movw_imm(2, 0xAAAAAAAA)
        for name, blob in mf.build_all():
            self.assertNotIn(measured, blob, name)

    def test_fixture_a650_paint_uses_the_synthetic_fill(self):
        r, _ = analyze(A650)
        self.assertEqual(r["image"]["stack_paint"]["fill"], mf.SYNTH_FILL)

    def test_no_fixture_carries_a_copied_reset_stub_branch(self):
        """The measured a650 branches to 0x400; the fixture uses 0x420.  If
        someone regenerates a fixture by truncating a real payload this
        fails."""
        r, _ = analyze(A650)
        self.assertNotEqual(r["image"]["reset_stub"]["branch_target"], 0x400)

    def test_fixtures_directory_is_ignored_by_git(self):
        ignore = os.path.join(FIXTURES, ".gitignore")
        self.assertTrue(os.path.exists(ignore))
        with open(ignore) as f:
            self.assertIn("!.gitignore", f.read())

    def test_generator_declares_its_clean_room_provenance(self):
        with open(os.path.join(HERE, "make_fixture.py")) as f:
            doc = f.read()
        self.assertIn("CLEAN-ROOM", doc)
        self.assertIn("No payload byte is copied", doc.replace("\n", " "))


# ---------------------------------------------------------------------------
# 11. Measurement primitives used by the analysis
# ---------------------------------------------------------------------------

class TestPrimitives(unittest.TestCase):

    def test_thumb_expand_imm_matches_the_architecture(self):
        # ARM DDI 0403 A5.3.2: 0x0FF -> 0xFF, 0x1FF -> 0xFF00FF,
        # 0x2FF -> 0xFF00FF00, and the rotate form
        self.assertEqual(ap.thumb_expand_imm(0x0FF), 0xFF)
        self.assertEqual(ap.thumb_expand_imm(0x1FF), 0xFF00FF)
        self.assertEqual(ap.thumb_expand_imm(0x2FF), 0xFF00FF00)
        self.assertEqual(ap.thumb_expand_imm(0x3AA), 0xAAAAAAAA)

    def test_loaded_image_reads_are_bounds_checked(self):
        img = ap.LoadedImage([(0x1000, b"\x11\x22\x33\x44")])
        self.assertEqual(img.word(0x1000), 0x44332211)
        self.assertIsNone(img.word(0x2000))
        self.assertIsNone(img.read(0x0FFE, 4))   # straddles the start

    def test_loaded_image_zero_fills_unwritten_space(self):
        img = ap.LoadedImage([(0x1000, b"\x11\x22\x33\x44")])
        flat = img.as_flat(0x1000, 0x1008)
        self.assertEqual(flat, b"\x11\x22\x33\x44" + b"\x00" * 4)

    def test_region_classification_matches_the_windows(self):
        self.assertEqual(ap.classify_region(0x0, 4, 0x40000), "ITCM")
        self.assertEqual(ap.classify_region(0x3FFF, 1, 0x40000), "ITCM")
        self.assertEqual(ap.classify_region(0x400, 4, 0x10004000), "ITCM")
        self.assertEqual(ap.classify_region(0x4000, 4, 0x40000), "icache")
        self.assertEqual(ap.classify_region(0x40000, 4, 0x40000), "DTCM")
        self.assertEqual(ap.classify_region(0x60000000, 4, 0x40000),
                         "dummy/BO")
        self.assertEqual(ap.classify_region(0x90000000, 4, 0x40000),
                         "outside-known-windows")

    def test_dtcm_base_detection_prefers_the_650_map(self):
        blocks = [{"addr": 0x10004000, "size": 16, "offset": 0},
                  {"addr": 0x40000, "size": 16, "offset": 32}]
        base, basis = ap.detect_dtcm_base(blocks)
        self.assertEqual(base, 0x10004000)
        self.assertIn("a650-family", basis)

    def test_dtcm_base_detection_falls_back_to_the_legacy_map(self):
        blocks = [{"addr": 0x40000, "size": 16, "offset": 0}]
        base, _ = ap.detect_dtcm_base(blocks)
        self.assertEqual(base, 0x40000)

    def test_string_extraction_reports_offsets(self):
        data = b"\x00\x00hello world\x00\x00"
        found = ap.extract_strings(data, 5)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["text"], "hello world")
        self.assertEqual(found[0]["offset"], 2)

    def test_string_extraction_respects_the_minimum(self):
        data = b"abcdefg\x00"
        self.assertEqual(ap.extract_strings(data, 8), [])
        self.assertEqual(len(ap.extract_strings(data, 7)), 1)

    def test_thumb_census_counts_known_encodings(self):
        data = struct.pack("<HHHH", 0xBF00, 0x4770, 0x4801, 0x6001)
        c = ap.thumb_census(data, 0, len(data))
        self.assertEqual(c["counts"]["nop"], 1)
        self.assertEqual(c["counts"]["bx lr"], 1)
        self.assertEqual(c["counts"]["ldr Rt,[pc,#imm8]"], 1)
        self.assertEqual(c["counts"]["str Rt,[Rn,#imm5]"], 1)
        self.assertEqual(c["halfwords"], 4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
