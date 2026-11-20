#!/usr/bin/env python3
"""test_cdsp_probe.py -- unittest suite for the clean-room Qualcomm split-MDT
CDSP container probe (``cdsp_probe.py``), driven by self-made synthetic
fixtures.

CLEAN-ROOM STATEMENT
Written from public, GPL-2.0-licensed sources only:
``include/uapi/linux/elf-em.h`` (``EM_HEXAGON`` = 164),
``include/uapi/linux/elf.h`` (the ``Elf32_Ehdr`` / ``Elf32_Phdr`` field order
and the ``PT_NULL`` / ``PT_LOAD`` / ``PF_R`` / ``PF_W`` / ``PF_X`` constants),
``include/linux/soc/qcom/mdt_loader.h`` (``QCOM_MDT_TYPE_MASK``,
``QCOM_MDT_TYPE_HASH``, ``QCOM_MDT_RELOCATABLE``),
``drivers/soc/qcom/mdt_loader.c`` (the split predicate, the sibling naming
rule and the sibling-size rejection), and coreboot
``util/qualcomm/mbn_tools.py`` (the packed ``p_flags`` bit layout and the
segment-type / access-type vocabularies). No decompiled code, no proprietary
documentation and no disassembly were used. Fixture bytes are self-made from
the measured layout only (``make_fixture.py``); no vendor payload is committed
or required by this suite.

Run from this directory:

    python3 -m unittest -v test_cdsp_probe

Covers: fixture existence, byte-for-byte determinism and total size; every
``Elf32_Ehdr`` field plus each rejection path (magic, class, endianness,
version, machine, type, table bounds); the ``decode_pflags()`` bit layout
against the known-good words the specification is written from; the
program-header walk and each field read back from the file bytes; the
sibling-size invariant in all five verdicts, including BSS rows that must have
no sibling and a deliberately short sibling; the header-block and hash-adjacency
rules; the ``PT_NULL`` with ``p_filesz > 0 && p_memsz == 0`` convention being
reported as an observed fact rather than a violation; malformed-input
resilience; and the CLI text / ``--json`` / ``--brief`` contracts.
"""

import contextlib
import hashlib
import io
import json
import os
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import cdsp_probe
import make_fixture

FIX = os.path.join(HERE, "fixtures")

MAIN_MDT = os.path.join(FIX, "cdsp_synthetic.mdt")
BSS_MDT = os.path.join(FIX, "bss_synthetic.mdt")
MISMATCH_MDT = os.path.join(FIX, "mismatch_synthetic.mdt")
BADMAGIC_MDT = os.path.join(FIX, "badmagic_synthetic.mdt")
TRUNC_MDT = os.path.join(FIX, "truncated_synthetic.mdt")
BADHASH_MDT = os.path.join(FIX, "badhash_synthetic.mdt")

ALL_MDT = (MAIN_MDT, BSS_MDT, MISMATCH_MDT, BADMAGIC_MDT, TRUNC_MDT,
           BADHASH_MDT)

FIXTURE_FILE_COUNT = 60
FIXTURE_TOTAL_BYTES = 775214
MAIN_MDT_BYTES = 84992
BSS_MDT_BYTES = 14336

REAL_DIR = ("/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-"
            "6cf6375c0730/data-fetch/second-device/instantnoodle/"
            "modem-fat-lfn")
REAL_MDT = os.path.join(REAL_DIR, "image_cdsp.mdt")


def have_real_blob():
    return os.path.isfile(REAL_MDT)


def readf(path):
    with open(path, "rb") as fh:
        return fh.read()


def run_cli(args):
    return subprocess.run(
        [sys.executable, "-I", os.path.join(HERE, "cdsp_probe.py")] + args,
        capture_output=True, text=True)


def tmpdir():
    base = "/tmp/opencode" if os.path.isdir("/tmp/opencode") else None
    return tempfile.mkdtemp(dir=base, prefix="cdsp-test-")


def clean_split_image():
    """A faithful split image: the ``.mdt`` holds the header block plus the
    hash segment only, and every payload row lives on disk as a sibling.
    ``make_fixture`` writes its main image unsplit so a single file shows the
    whole row table; this helper assembles the split case the loader sees."""
    rows = make_fixture.split_rows()
    image = make_fixture.build_image("fx-cdsp", rows)
    header_block = cdsp_probe.ELF32_EHDR_SIZE + cdsp_probe.ELF32_PHDR_SIZE * len(rows)
    parts = dict(make_fixture.write_split(".", "clean", image, rows))
    return image[:header_block] + parts["clean.b01"], parts, header_block


def write_clean_tree(directory):
    rows = make_fixture.split_rows()
    image = make_fixture.build_image("fx-cdsp", rows)
    header_block = cdsp_probe.ELF32_EHDR_SIZE + cdsp_probe.ELF32_PHDR_SIZE * len(rows)
    parts = dict(make_fixture.write_split(directory, "clean", image, rows))
    for name, blob in parts.items():
        if name != "clean.mdt":
            with open(os.path.join(directory, name), "wb") as fh:
                fh.write(blob)
    mdt = os.path.join(directory, "clean.mdt")
    with open(mdt, "wb") as fh:
        fh.write(image[:header_block] + parts["clean.b01"])
    return mdt


class TestFixtures(unittest.TestCase):

    def test_all_six_mdt_fixtures_exist(self):
        for path in ALL_MDT:
            self.assertTrue(os.path.isfile(path), "missing fixture %s" % path)

    def test_fixture_directory_holds_sixty_files(self):
        names = sorted(os.listdir(FIX))
        self.assertEqual(len(names), FIXTURE_FILE_COUNT, names)

    def test_fixture_total_byte_count(self):
        total = sum(os.path.getsize(os.path.join(FIX, n))
                    for n in os.listdir(FIX))
        self.assertEqual(total, FIXTURE_TOTAL_BYTES)

    def test_regeneration_is_byte_identical(self):
        before = {n: readf(os.path.join(FIX, n)) for n in os.listdir(FIX)}
        with contextlib.redirect_stdout(io.StringIO()):
            make_fixture.main()
        after = {n: readf(os.path.join(FIX, n)) for n in os.listdir(FIX)}
        self.assertEqual(sorted(before), sorted(after))
        for name in before:
            self.assertEqual(
                hashlib.sha256(after[name]).hexdigest(),
                hashlib.sha256(before[name]).hexdigest(),
                "fixture %s is not deterministic" % name)

    def test_build_all_returns_sixty_jobs(self):
        d = tmpdir()
        try:
            jobs = make_fixture.build_all(d)
            self.assertEqual(len(jobs), FIXTURE_FILE_COUNT)
            total = sum(len(blob) for _, blob in jobs)
            self.assertEqual(total, FIXTURE_TOTAL_BYTES)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_main_image_and_bss_image_sizes(self):
        self.assertEqual(os.path.getsize(MAIN_MDT), MAIN_MDT_BYTES)
        self.assertEqual(os.path.getsize(BSS_MDT), BSS_MDT_BYTES)

    def test_mismatch_sibling_is_two_bytes_short(self):
        self.assertEqual(os.path.getsize(os.path.join(FIX, "mismatch_synthetic.b05")),
                         os.path.getsize(os.path.join(FIX, "cdsp_synthetic.b05")) - 2)

    def test_pattern_stream_is_reproducible_per_tag(self):
        a = make_fixture.pattern(4096, "tag-a")
        b = make_fixture.pattern(4096, "tag-a")
        c = make_fixture.pattern(4096, "tag-b")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(len(a), 4096)

    def test_pattern_is_a_sha256_counter_stream(self):
        expected = hashlib.sha256(b"t:0").digest() + hashlib.sha256(b"t:1").digest()
        self.assertEqual(make_fixture.pattern(64, "t"), expected)

    def test_fixtures_carry_no_vendor_bytes(self):
        if not have_real_blob():
            self.skipTest("real blob not present on disk")
        real = readf(REAL_MDT)
        for name in ("cdsp_synthetic.b05", "cdsp_synthetic.b02"):
            body = readf(os.path.join(FIX, name))
            self.assertNotIn(body[:4096], real, "%s appears in the real blob" % name)

    def test_fixture_names_match_the_gitignore_families(self):
        for name in os.listdir(FIX):
            tail = name[-4:]
            sibling = (len(tail) == 4 and tail[0] == "." and tail[1] == "b"
                       and tail[2:].isdigit())
            self.assertTrue(name.endswith(".mdt") or sibling,
                            "unexpected fixture name %s" % name)


class TestElfHeader(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = cdsp_probe.probe_file(MAIN_MDT)
        cls.hdr = cls.res["header"]

    def test_ident_magic_is_elf(self):
        self.assertEqual(self.hdr["e_ident_hex"][:8], "7f454c46")
        self.assertEqual(readf(MAIN_MDT)[:4], b"\x7fELF")

    def test_ident_class_data_version(self):
        ident = bytes.fromhex(self.hdr["e_ident_hex"])
        self.assertEqual(ident[4], 1, "ELFCLASS32")
        self.assertEqual(ident[5], 1, "ELFDATA2LSB")
        self.assertEqual(ident[6], 1, "EV_CURRENT")
        self.assertEqual(ident[7:16], b"\x00" * 9)

    def test_e_type_is_et_exec(self):
        self.assertEqual(self.hdr["e_type"], 2)
        self.assertEqual(self.hdr["e_type_name"], "ET_EXEC")

    def test_e_machine_is_hexagon(self):
        self.assertEqual(self.hdr["e_machine"], 164)
        self.assertEqual(self.hdr["e_machine"], cdsp_probe.EM_HEXAGON)
        self.assertEqual(self.hdr["e_machine_name"], "EM_HEXAGON/EM_QDSP6")

    def test_e_version_and_e_ehsize(self):
        self.assertEqual(self.hdr["e_version"], 1)
        self.assertEqual(self.hdr["e_ehsize"], 52)
        self.assertEqual(self.hdr["e_ehsize"], cdsp_probe.ELF32_EHDR_SIZE)

    def test_e_phoff_is_52_and_e_phentsize_is_32(self):
        self.assertEqual(self.hdr["e_phoff"], 52)
        self.assertEqual(self.hdr["e_phentsize"], 32)
        self.assertEqual(self.hdr["e_phentsize"], cdsp_probe.ELF32_PHDR_SIZE)

    def test_program_header_table_bounds(self):
        self.assertEqual(self.hdr["phdr_table_offset"], 52)
        self.assertEqual(self.hdr["phdr_table_bytes"], 32 * 13)
        self.assertEqual(self.hdr["phdr_table_end"], 468)

    def test_no_section_headers(self):
        self.assertEqual(self.hdr["e_shoff"], 0)
        self.assertEqual(self.hdr["e_shnum"], 0)
        self.assertEqual(self.hdr["e_shstrndx"], 0)
        self.assertTrue(self.hdr["sectionless"])

    def test_e_flags_names_the_v66_isa(self):
        self.assertEqual(self.hdr["e_flags"], 0x66)
        self.assertEqual(self.hdr["e_flags_isa_name"], "V66")
        self.assertEqual(self.hdr["e_flags_high"], "0x00000000")

    def test_isa_table_is_the_public_one(self):
        self.assertEqual(cdsp_probe.isa_name(0x65), "V65")
        self.assertEqual(cdsp_probe.isa_name(0x68), "V68")
        self.assertIsNone(cdsp_probe.isa_name(0x7F))

    def test_magic_rejection(self):
        res = cdsp_probe.probe_file(BADMAGIC_MDT)
        self.assertFalse(res["structural_ok"])
        self.assertIn("magic", res["parse_error"])
        self.assertIn("7f454c47", res["violations"][0])
        self.assertIsNone(res["header"])

    def test_one_byte_short_of_the_header_is_rejected(self):
        res = cdsp_probe.probe_bytes(readf(MAIN_MDT)[:51], "51")
        self.assertFalse(res["structural_ok"])
        self.assertIn("too small", res["parse_error"])
        self.assertIn("51 bytes", res["parse_error"])

    def test_wrong_class_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        buf[4] = 2
        res = cdsp_probe.probe_bytes(bytes(buf), "class")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("EI_CLASS" in m for m in res["violations"]))

    def test_wrong_endianness_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        buf[5] = 2
        res = cdsp_probe.probe_bytes(bytes(buf), "data")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("ELFDATA2LSB" in m for m in res["violations"]))

    def test_wrong_ident_version_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        buf[6] = 0
        res = cdsp_probe.probe_bytes(bytes(buf), "identver")
        self.assertFalse(res["structural_ok"])
        self.assertTrue(any("EI_VERSION" in m for m in res["violations"]))

    def test_wrong_machine_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<H", buf, 18, 40)
        res = cdsp_probe.probe_bytes(bytes(buf), "machine")
        self.assertTrue(any("EM_ARM" in m for m in res["violations"]),
                        res["violations"])

    def test_wrong_e_type_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<H", buf, 16, 9)
        res = cdsp_probe.probe_bytes(bytes(buf), "etype")
        self.assertTrue(any("ET_EXEC" in m for m in res["violations"]),
                        res["violations"])

    def test_wrong_e_ehsize_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<H", buf, 40, 64)
        res = cdsp_probe.probe_bytes(bytes(buf), "ehsize")
        self.assertTrue(any("e_ehsize" in m for m in res["violations"]),
                        res["violations"])

    def test_wrong_e_phentsize_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<H", buf, 42, 0)
        res = cdsp_probe.probe_bytes(bytes(buf), "phentsize")
        self.assertTrue(any("e_phentsize" in m for m in res["violations"]),
                        res["violations"])

    def test_e_phoff_inside_the_header_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<I", buf, 28, 16)
        res = cdsp_probe.probe_bytes(bytes(buf), "phoff")
        self.assertTrue(any("overlaps the ELF header" in m
                            for m in res["violations"]), res["violations"])

    def test_section_header_table_past_eof_is_rejected(self):
        buf = bytearray(readf(MAIN_MDT))
        struct.pack_into("<H", buf, 46, 40)
        struct.pack_into("<H", buf, 48, 2)
        struct.pack_into("<I", buf, 32, 0x100000)
        res = cdsp_probe.probe_bytes(bytes(buf), "shoff")
        self.assertTrue(any("section-header table ends" in m
                            for m in res["violations"]), res["violations"])


class TestDecodePflags(unittest.TestCase):

    def test_phdr_word_decodes_to_type_seven(self):
        d = cdsp_probe.decode_pflags(0x07000000)
        self.assertEqual(d["seg_type"], 7)
        self.assertEqual(d["seg_type_name"], "PHDR")
        self.assertTrue(d["is_phdr"])
        self.assertFalse(d["is_hash"])
        self.assertFalse(d["relocatable"])

    def test_hash_word_decodes_to_type_two(self):
        d = cdsp_probe.decode_pflags(0x02200000)
        self.assertEqual(d["seg_type"], 2)
        self.assertEqual(d["seg_type_name"], "HASH")
        self.assertTrue(d["is_hash"])
        self.assertFalse(d["is_phdr"])
        self.assertEqual(d["access_type"], 1)
        self.assertEqual(d["access_type_name"], "RO")

    def test_rx_word(self):
        d = cdsp_probe.decode_pflags(0x08000005)
        self.assertEqual(d["rwx"], "R-X")
        self.assertTrue(d["pf_r"])
        self.assertFalse(d["pf_w"])
        self.assertTrue(d["pf_x"])

    def test_r_only_word(self):
        d = cdsp_probe.decode_pflags(0x08000004)
        self.assertEqual(d["rwx"], "R--")
        self.assertTrue(d["pf_r"])
        self.assertFalse(d["pf_w"])
        self.assertFalse(d["pf_x"])

    def test_rw_word(self):
        d = cdsp_probe.decode_pflags(0x08000006)
        self.assertEqual(d["rwx"], "RW-")
        self.assertFalse(d["pf_x"])

    def test_rwx_word(self):
        d = cdsp_probe.decode_pflags(0x08000007)
        self.assertEqual(d["rwx"], "RWX")
        self.assertEqual(d["low3"], 7)

    def test_relocatable_bit_twentyseven(self):
        self.assertTrue(cdsp_probe.decode_pflags(0x08000005)["relocatable"])
        self.assertFalse(cdsp_probe.decode_pflags(0x00000005)["relocatable"])
        self.assertEqual(cdsp_probe.decode_pflags(0x08000005)["pool_index"], 1)
        self.assertEqual(cdsp_probe.decode_pflags(0x00000005)["pool_index"], 0)

    def test_access_type_zero(self):
        d = cdsp_probe.decode_pflags(0x07000000)
        self.assertEqual(d["access_type"], 0)
        self.assertEqual(d["access_type_name"], "RW")
        self.assertFalse(d["is_zi"])

    def test_access_type_one(self):
        d = cdsp_probe.decode_pflags(0x02200000)
        self.assertEqual(d["access_type"], 1)
        self.assertEqual(d["access_type_name"], "RO")

    def test_access_type_two_is_zi(self):
        d = cdsp_probe.decode_pflags(0x00400000)
        self.assertEqual(d["access_type"], 2)
        self.assertEqual(d["access_type_name"], "ZI")
        self.assertTrue(d["is_zi"])

    def test_access_type_three_is_notused(self):
        d = cdsp_probe.decode_pflags(0x00600000)
        self.assertEqual(d["access_type"], 3)
        self.assertEqual(d["access_type_name"], "NOTUSED")

    def test_page_mode_field(self):
        self.assertEqual(cdsp_probe.decode_pflags(0)["page_mode"], 0)
        self.assertEqual(cdsp_probe.decode_pflags(0)["page_mode_name"],
                         "NON_PAGED")
        d = cdsp_probe.decode_pflags(0x00100000)
        self.assertEqual(d["page_mode"], 1)
        self.assertEqual(d["page_mode_name"], "PAGED")

    def test_low_bits_are_not_the_segment_type(self):
        self.assertEqual(cdsp_probe.decode_pflags(0x07000000)["low3"], 0)
        self.assertEqual(cdsp_probe.decode_pflags(0x07000007)["seg_type"], 7)
        self.assertEqual(cdsp_probe.decode_pflags(0x07000007)["rwx"], "RWX")

    def test_bits_set_is_the_exact_population(self):
        self.assertEqual(cdsp_probe.decode_pflags(0x02200000)["bits_set"],
                         [21, 25])
        self.assertEqual(cdsp_probe.decode_pflags(0x08000005)["bits_set"],
                         [0, 2, 27])
        self.assertEqual(cdsp_probe.decode_pflags(0)["bits_set"], [])

    def test_high_nibble_is_reported_not_swallowed(self):
        d = cdsp_probe.decode_pflags(0x11000000)
        self.assertEqual(d["unknown_high"], 1)
        self.assertEqual(d["unknown_high_hex"], "0x10000000")
        self.assertEqual(cdsp_probe.decode_pflags(0x07000000)["unknown_high"], 0)

    def test_raw_roundtrip(self):
        for word in (0x07000000, 0x02200000, 0x08000005, 0x08F00007):
            d = cdsp_probe.decode_pflags(word)
            self.assertEqual(d["raw"], word)
            self.assertEqual(d["raw_hex"], "0x%08x" % word)

    def test_masks_match_the_public_loader_constants(self):
        self.assertEqual(cdsp_probe.QCOM_MDT_TYPE_MASK, 7 << 24)
        self.assertEqual(cdsp_probe.QCOM_MDT_TYPE_HASH, 2 << 24)
        self.assertEqual(cdsp_probe.QCOM_MDT_RELOCATABLE, 1 << 27)
        self.assertEqual(cdsp_probe.MI_PBT_FLAG_ACCESS_TYPE_MASK, 0x00E00000)
        self.assertEqual(cdsp_probe.MI_PBT_FLAG_PAGE_MODE_MASK, 0x00100000)


class TestProgramHeaders(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.buf = readf(MAIN_MDT)
        cls.res = cdsp_probe.probe_file(MAIN_MDT)
        cls.rows = cls.res["program_headers"]

    def test_thirteen_rows_at_32_byte_stride(self):
        self.assertEqual(len(self.rows), 13)
        for i, row in enumerate(self.rows):
            self.assertEqual(row["index"], i)
            self.assertEqual(row["phdr_offset"], 52 + 32 * i)

    def test_every_field_reads_back_from_the_file_bytes(self):
        for row in self.rows:
            fields = struct.unpack_from("<IIIIIIII", self.buf, row["phdr_offset"])
            self.assertEqual(
                fields,
                (row["p_type"], row["p_offset"], row["p_vaddr"], row["p_paddr"],
                 row["p_filesz"], row["p_memsz"], row["p_flags"], row["p_align"]),
                "row %d disagrees with the file bytes" % row["index"])

    def test_row_zero_is_the_header_block(self):
        first = self.rows[0]
        self.assertEqual(first["p_type"], cdsp_probe.PT_NULL)
        self.assertEqual(first["p_offset"], 0)
        self.assertEqual(first["p_filesz"], 468)
        self.assertEqual(first["p_filesz"],
                         self.res["header"]["e_ehsize"] +
                         self.res["header"]["e_phnum"] *
                         self.res["header"]["e_phentsize"])
        self.assertFalse(first["bss"])
        self.assertTrue(first["flags"]["is_phdr"])

    def test_hash_row_is_the_second_null_row(self):
        self.assertEqual(self.res["hash_segment"], 1)
        self.assertEqual(self.rows[1]["p_type"], cdsp_probe.PT_NULL)
        self.assertTrue(self.rows[1]["flags"]["is_hash"])
        self.assertEqual(self.rows[1]["p_filesz"], 7192)

    def test_only_rows_zero_and_one_are_null(self):
        null = [r["index"] for r in self.rows
                if r["p_type"] == cdsp_probe.PT_NULL]
        self.assertEqual(null, [0, 1])
        self.assertEqual(self.res["counts"]["pt_null"], 2)

    def test_eleven_load_rows(self):
        load = [r["index"] for r in self.rows if r["p_type"] == cdsp_probe.PT_LOAD]
        self.assertEqual(load, list(range(2, 13)))
        self.assertEqual(self.res["counts"]["pt_load"], 11)

    def test_load_rows_are_relocatable_and_pool_one(self):
        for row in self.rows[2:]:
            self.assertTrue(row["flags"]["relocatable"])
            self.assertEqual(row["flags"]["pool_index"], 1)
        self.assertEqual(self.res["counts"]["relocatable_rows"], 11)

    def test_segment_type_field_is_uniform_across_load_rows(self):
        types = {row["flags"]["seg_type"] for row in self.rows[2:]}
        self.assertEqual(types, {0})
        self.assertEqual(self.rows[2]["flags"]["seg_type_name"], "L4/AMSS")

    def test_p_flags_words_are_the_measured_vocabulary(self):
        words = [row["p_flags"] for row in self.rows]
        self.assertEqual(words[0], 0x07000000)
        self.assertEqual(words[1], 0x02200000)
        self.assertIn(0x08000005, words)
        self.assertIn(0x08000004, words)
        self.assertIn(0x08000006, words)
        self.assertIn(0x08000007, words)

    def test_no_row_uses_the_high_nibble(self):
        for row in self.rows:
            self.assertEqual(row["flags"]["unknown_high"], 0,
                             "row %d sets bits 31-28" % row["index"])

    def test_alignments_are_page_sized(self):
        for row in self.rows:
            self.assertEqual(row["p_align"], 0x1000, "row %d" % row["index"])

    def test_payload_offsets_are_page_aligned(self):
        for row in self.rows[1:]:
            if row["p_filesz"]:
                self.assertEqual(row["p_offset"] % 0x1000, 0,
                                 "row %d" % row["index"])

    def test_bss_rows_are_filesz_zero_with_memsz(self):
        bss = [r for r in self.rows if r["bss"]]
        self.assertEqual([r["index"] for r in bss], [7, 10, 12])
        for row in bss:
            self.assertEqual(row["p_filesz"], 0)
            self.assertGreater(row["p_memsz"], 0)
            self.assertEqual(row["p_type"], cdsp_probe.PT_LOAD)
            self.assertEqual(row["flags"]["rwx"], "R--")

    def test_totals_agree_with_the_rows(self):
        self.assertEqual(self.res["totals"]["sum_p_filesz"],
                         sum(r["p_filesz"] for r in self.rows))
        self.assertEqual(self.res["totals"]["sum_p_memsz"],
                         sum(r["p_memsz"] for r in self.rows))
        self.assertEqual(self.res["totals"]["bss_bytes"],
                         sum(r["p_memsz"] for r in self.rows if r["bss"]))

    def test_entry_point_lands_in_the_first_code_segment(self):
        self.assertEqual(self.res["header"]["e_entry"], 0x87800000)
        self.assertEqual(self.res["header"]["e_entry_hex"], "0x87800000")
        self.assertEqual(self.res["entry_segment"], 2)
        self.assertTrue(self.res["entry_inside_load"])
        self.assertTrue(self.res["entry_matches_paddr"])

    def test_entry_outside_every_load_row_is_a_violation(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 24, 0x00000010)
        res = cdsp_probe.probe_bytes(bytes(buf), "entry")
        self.assertFalse(res["entry_inside_load"])
        self.assertTrue(any("lies in no PT_LOAD" in m for m in res["violations"]),
                        res["violations"])

    def test_walk_stops_at_the_file_end(self):
        buf = readf(MAIN_MDT)[:52 + 32 * 3]
        res = cdsp_probe.probe_bytes(buf, "short-table")
        self.assertIsNotNone(res.get("parse_error"))
        self.assertTrue(any("past the end of the file" in m
                            for m in res["violations"]), res["violations"])

    def test_split_predicate_is_false_when_every_row_fits(self):
        ehdr = cdsp_probe.parse_ehdr(self.buf)
        phdrs = cdsp_probe.parse_phdrs(self.buf, ehdr)
        self.assertFalse(cdsp_probe.bins_are_split(self.buf, phdrs))
        self.assertFalse(self.res["split"])


class TestSiblingRule(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = cdsp_probe.probe_file(MAIN_MDT)

    def test_ten_rows_match_their_sibling(self):
        self.assertEqual(self.res["counts"]["sibling_match"], 10)
        matches = [s for s in self.res["siblings"]
                   if s["verdict"] == cdsp_probe.VERDICT_MATCH]
        self.assertEqual([s["index"] for s in matches],
                         [0, 1, 2, 3, 4, 5, 6, 8, 9, 11])

    def test_no_mismatch_and_no_missing_on_a_good_image(self):
        self.assertEqual(self.res["counts"]["sibling_size_mismatch"], 0)
        self.assertEqual(self.res["counts"]["sibling_missing"], 0)

    def test_expected_byte_count_equals_p_filesz(self):
        for s in self.res["siblings"]:
            self.assertEqual(s["expected_bytes"],
                             self.res["program_headers"][s["index"]]["p_filesz"])

    def test_bss_rows_are_absent_as_predicted(self):
        absent = [s for s in self.res["siblings"]
                  if s["verdict"] == cdsp_probe.VERDICT_ABSENT]
        self.assertEqual([s["index"] for s in absent], [7, 10, 12])
        self.assertEqual(self.res["counts"]["sibling_absent_as_predicted"], 3)
        for s in absent:
            self.assertFalse(s["sibling_present"])
            self.assertIsNone(s["sibling_bytes"])
            self.assertEqual(s["expected_bytes"], 0)
            self.assertTrue(s["ok"])

    def test_bss_rows_have_no_file_on_disk(self):
        for index in (7, 10, 12):
            path = os.path.join(FIX, "cdsp_synthetic.b%02d" % index)
            self.assertFalse(os.path.isfile(path),
                             "%s should not exist for a p_filesz==0 row" % path)

    def test_sibling_names_follow_the_loader_rule(self):
        for s in self.res["siblings"]:
            self.assertEqual(
                s["sibling_name"],
                cdsp_probe.sibling_path(MAIN_MDT, s["index"]))
            self.assertTrue(s["sibling_name"].endswith(".b%02d" % s["index"]))
            self.assertFalse(s["sibling_name"].endswith(".mdt"))

    def test_sibling_path_rewrites_the_last_three_characters(self):
        self.assertEqual(cdsp_probe.sibling_path("/x/image_cdsp.mdt", 5),
                         "/x/image_cdsp.b05")
        self.assertEqual(cdsp_probe.sibling_path("/x/image_cdsp.mdt", 12),
                         "/x/image_cdsp.b12")
        self.assertIsNone(cdsp_probe.sibling_path("ab", 0))

    def test_uppercase_fat_image_resolves_case_insensitively(self):
        lower = tmpdir()
        upper = tmpdir()
        try:
            clean = write_clean_tree(lower)
            for name in os.listdir(lower):
                src = os.path.join(lower, name)
                base, ext = name.rsplit(".", 1)
                os.link(src, os.path.join(upper, base.upper() + "." + ext.upper()))
            low_res = cdsp_probe.probe_file(clean)
            up_res = cdsp_probe.probe_file(
                os.path.join(upper, "CLEAN.MDT"))
            self.assertTrue(low_res["structural_ok"], low_res["violations"])
            self.assertTrue(up_res["structural_ok"], up_res["violations"])
            self.assertEqual(up_res["counts"]["sibling_match"],
                             low_res["counts"]["sibling_match"])
            self.assertEqual(up_res["counts"]["sibling_missing"], 0)
        finally:
            shutil.rmtree(lower, True)
            shutil.rmtree(upper, True)

    def test_wrong_sibling_size_is_named_and_fails(self):
        res = cdsp_probe.probe_file(MISMATCH_MDT)
        self.assertFalse(res["structural_ok"])
        self.assertEqual(res["counts"]["sibling_size_mismatch"], 1)
        bad = [s for s in res["siblings"]
               if s["verdict"] == cdsp_probe.VERDICT_SIZE_MISMATCH]
        self.assertEqual(len(bad), 1)
        self.assertEqual(bad[0]["index"], 5)
        self.assertEqual(bad[0]["expected_bytes"], 18432)
        self.assertEqual(bad[0]["sibling_bytes"], 18430)
        self.assertFalse(bad[0]["ok"])
        self.assertTrue(any("mismatch_synthetic.b05 is 18430 bytes" in m
                            for m in res["violations"]), res["violations"])

    def test_truncated_sibling_is_named(self):
        res = cdsp_probe.probe_file(TRUNC_MDT)
        self.assertFalse(res["structural_ok"])
        bad = [s for s in res["siblings"]
               if s["verdict"] == cdsp_probe.VERDICT_SIZE_MISMATCH]
        self.assertEqual([b["index"] for b in bad], [11])
        self.assertEqual(bad[0]["sibling_bytes"], 3008)
        self.assertEqual(bad[0]["expected_bytes"], 3072)

    def test_missing_sibling_is_a_violation(self):
        sizes = {s["index"]: s["sibling_bytes"] for s in self.res["siblings"]
                 if s["sibling_bytes"] is not None}
        del sizes[2]
        res = cdsp_probe.probe_bytes(
            readf(MAIN_MDT), MAIN_MDT, sibling_sizes=sizes)
        verdicts = {s["index"]: s["verdict"] for s in res["siblings"]}
        self.assertEqual(verdicts[2], cdsp_probe.VERDICT_MISSING)
        self.assertTrue(any("is missing" in m for m in res["violations"]))

    def test_classify_sibling_covers_all_five_verdicts(self):
        row = {"index": 3, "p_filesz": 100}
        self.assertEqual(cdsp_probe.classify_sibling(row, {3: 100})["verdict"], "MATCH")
        self.assertEqual(cdsp_probe.classify_sibling(row, {3: 99})["verdict"], "SIZE-MISMATCH")
        self.assertEqual(cdsp_probe.classify_sibling(row, {})["verdict"], "MISSING")
        bss = {"index": 3, "p_filesz": 0}
        self.assertEqual(cdsp_probe.classify_sibling(bss, {})["verdict"],
                         "ABSENT-as-predicted")
        self.assertEqual(cdsp_probe.classify_sibling(bss, {3: 0})["verdict"],
                         "ZERO-BYTE-SIBLING")
        self.assertEqual(cdsp_probe.classify_sibling(bss, {3: 7})["verdict"],
                         "SIZE-MISMATCH")

    def test_only_match_and_absent_are_ok(self):
        self.assertTrue(cdsp_probe.classify_sibling({"index": 0, "p_filesz": 4},
                                                    {0: 4})["ok"])
        self.assertTrue(cdsp_probe.classify_sibling({"index": 0, "p_filesz": 0},
                                                    {})["ok"])
        self.assertFalse(cdsp_probe.classify_sibling({"index": 0, "p_filesz": 4},
                                                     {})["ok"])
        self.assertFalse(cdsp_probe.classify_sibling({"index": 0, "p_filesz": 4},
                                                     {0: 5})["ok"])

    def test_siblings_are_unchecked_when_not_supplied(self):
        res = cdsp_probe.probe_bytes(readf(MAIN_MDT), MAIN_MDT)
        self.assertEqual(res["siblings"], [])
        self.assertTrue(any("UNCHECKED" in n for n in res["notes"]), res["notes"])

    def test_explicit_zero_byte_sibling_is_accepted_and_noted(self):
        d = tmpdir()
        try:
            mdt = write_clean_tree(d)
            empty = os.path.join(d, "clean.b07")
            with open(empty, "wb") as fh:
                fh.write(b"")
            self.assertEqual(os.path.getsize(empty), 0)
            res = cdsp_probe.probe_file(mdt)
            entry = [s for s in res["siblings"] if s["index"] == 7][0]
            self.assertEqual(entry["verdict"], cdsp_probe.VERDICT_ZERO_BYTE)
            self.assertEqual(entry["sibling_bytes"], 0)
            self.assertTrue(entry["ok"])
            self.assertTrue(any("explicit empty sibling" in n
                                for n in res["notes"]), res["notes"])
            self.assertEqual(res["counts"]["sibling_absent_as_predicted"], 2)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_real_zero_byte_sibling_family_is_accepted(self):
        alt = os.path.join(
            "/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-"
            "6cf6375c0730/data-fetch/second-device/larry/tree-vendor/"
            "firmware/evass.mdt")
        if not os.path.isfile(alt):
            self.skipTest("evass.mdt not present locally")
        res = cdsp_probe.probe_file(alt)
        zero = [s["index"] for s in res["siblings"]
                if s["verdict"] == cdsp_probe.VERDICT_ZERO_BYTE]
        self.assertTrue(zero)
        for index in zero:
            self.assertTrue(os.path.isfile(os.path.join(os.path.dirname(alt),
                                                        "evass.b%02d" % index)))
        self.assertFalse(any("mismatch" in v for v in res["violations"]))

    def test_real_missing_sibling_is_named(self):
        alt = os.path.join(
            "/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-"
            "6cf6375c0730/data-fetch/second-device/larry/tree-vendor/"
            "firmware/vpu20_1v.mdt")
        if not os.path.isfile(alt):
            self.skipTest("vpu20_1v.mdt not present locally")
        res = cdsp_probe.probe_file(alt)
        missing = [s for s in res["siblings"]
                   if s["verdict"] == cdsp_probe.VERDICT_MISSING]
        self.assertEqual([m["index"] for m in missing], [0])
        self.assertEqual(missing[0]["expected_bytes"], 692)
        self.assertIsNone(missing[0]["sibling_bytes"])
        self.assertFalse(missing[0]["ok"])
        self.assertTrue(any("vpu20_1v.b00 is missing" in v
                            for v in res["violations"]), res["violations"])

    def test_orphan_sibling_is_reported_without_failing(self):
        d = tmpdir()
        try:
            mdt = write_clean_tree(d)
            with open(os.path.join(d, "clean.b13"), "wb") as fh:
                fh.write(b"zz")
            res = cdsp_probe.probe_file(mdt)
            self.assertEqual([o["index"] for o in res["orphans"]], [13])
            self.assertEqual(res["orphans"][0]["bytes"], 2)
            self.assertTrue(any("not referenced by any program header" in n
                                for n in res["notes"]), res["notes"])
        finally:
            shutil.rmtree(d, ignore_errors=True)


class TestStructuralRules(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.buf = readf(MAIN_MDT)

    def test_unsplit_fixture_reports_the_hash_adjacency_rule(self):
        res = cdsp_probe.probe_file(MAIN_MDT)
        self.assertFalse(res["structural_ok"])
        self.assertEqual(len(res["violations"]), 1)
        self.assertIn("phdr[0].p_filesz + phdr[1].p_filesz = 7660",
                      res["violations"][0])
        self.assertIn("expected the file size 84992", res["violations"][0])

    def test_clean_split_tree_has_no_violations(self):
        d = tmpdir()
        try:
            res = cdsp_probe.probe_file(write_clean_tree(d))
            self.assertTrue(res["structural_ok"], res["violations"])
            self.assertEqual(res["violations"], [])
            self.assertTrue(res["split"])
            self.assertEqual(res["counts"]["sibling_match"], 10)
            self.assertEqual(res["counts"]["sibling_absent_as_predicted"], 3)
            self.assertEqual(res["size"], 7660)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_phdr0_with_memsz_zero_is_a_note_not_a_violation(self):
        rows = make_fixture.split_rows()
        rows[0]["memsz"] = 0
        image = make_fixture.build_image("fx-cdsp", rows)
        header_block = 52 + 32 * len(rows)
        parts = dict(make_fixture.write_split(".", "z", image, rows))
        sizes = {int(name[-2:]): len(blob) for name, blob in parts.items()
                 if name != "z.mdt"}
        res = cdsp_probe.probe_bytes(
            image[:header_block] + parts["z.b01"], "z.mdt",
            sibling_sizes=sizes)
        self.assertTrue(res["structural_ok"], res["violations"])
        self.assertEqual(res["violations"], [])
        notes = [n for n in res["notes"] if n.startswith("[F] observed convention")]
        self.assertEqual(len(notes), 1)
        self.assertIn("phdr[0]", notes[0])
        self.assertIn("p_memsz = 0", notes[0])
        self.assertIn("p_filesz = 468", notes[0])
        self.assertNotIn("loader refuses", notes[0])

    def test_hash_row_with_memsz_zero_is_also_a_note(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 32 + 20, 0)
        res = cdsp_probe.probe_bytes(bytes(buf), "hash-m0")
        self.assertTrue(any(n.startswith("[F] observed convention")
                            and "phdr[1]" in n for n in res["notes"]),
                        res["notes"])
        self.assertFalse(any("loader refuses" in m for m in res["violations"]))

    def test_a_load_row_with_filesz_over_memsz_is_still_a_violation(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 2 * 32 + 20, 0x1000)
        res = cdsp_probe.probe_bytes(bytes(buf), "load-over")
        self.assertTrue(any("phdr[2].p_filesz = 14848 exceeds p_memsz = 4096"
                            in m for m in res["violations"]), res["violations"])

    def test_missing_hash_segment_is_a_violation(self):
        res = cdsp_probe.probe_file(BADHASH_MDT)
        self.assertFalse(res["structural_ok"])
        self.assertIsNone(res["hash_segment"])
        self.assertEqual(res["counts"]["hash_segments"], 0)
        self.assertEqual(len(res["violations"]), 1)
        self.assertIn("QCOM_MDT_TYPE_HASH", res["violations"][0])

    def test_hash_row_may_not_be_a_load_row(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 32, cdsp_probe.PT_LOAD)
        res = cdsp_probe.probe_bytes(bytes(buf), "hash-load")
        self.assertTrue(any("is the hash segment but p_type" in m
                            for m in res["violations"]), res["violations"])

    def test_relocatable_bit_must_be_uniform(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 2 * 32 + 24, 0x00000005)
        res = cdsp_probe.probe_bytes(bytes(buf), "reloc")
        self.assertTrue(any("not uniform" in m for m in res["violations"]),
                        res["violations"])

    def test_high_nibble_in_p_flags_is_a_violation(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 24, 0x17000000)
        res = cdsp_probe.probe_bytes(bytes(buf), "high")
        self.assertTrue(any("bits 31-28 set" in m for m in res["violations"]),
                        res["violations"])

    def test_row_zero_must_be_a_null_row(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52, cdsp_probe.PT_LOAD)
        res = cdsp_probe.probe_bytes(bytes(buf), "row0")
        self.assertTrue(any("expected PT_NULL" in m for m in res["violations"]),
                        res["violations"])

    def test_row_zero_filesz_must_equal_the_header_block(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 16, 100)
        res = cdsp_probe.probe_bytes(bytes(buf), "row0-filesz")
        self.assertTrue(any("expected 468" in m for m in res["violations"]),
                        res["violations"])

    def test_row_zero_must_decode_to_phdr(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 52 + 24, 0x02000000)
        res = cdsp_probe.probe_bytes(bytes(buf), "row0-flags")
        self.assertTrue(any("expected 7 (PHDR)" in m for m in res["violations"]),
                        res["violations"])

    def test_fewer_than_two_rows_is_a_violation(self):
        buf = bytearray(self.buf)
        struct.pack_into("<H", buf, 44, 1)
        res = cdsp_probe.probe_bytes(bytes(buf), "one-row")
        self.assertTrue(any("at least a header row and a hash row" in m
                            for m in res["violations"]), res["violations"])

    def test_violations_and_structural_ok_never_disagree(self):
        for path in ALL_MDT:
            res = cdsp_probe.probe_file(path)
            self.assertEqual(res["structural_ok"], not res["violations"], path)


class TestSiblinglessBssFixture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = cdsp_probe.probe_file(BSS_MDT)

    def test_seven_rows_and_five_load_rows(self):
        self.assertEqual(self.res["counts"]["phdr_total"], 7)
        self.assertEqual(self.res["counts"]["pt_load"], 5)
        self.assertEqual(self.res["counts"]["pt_null"], 2)

    def test_three_bss_rows_have_no_sibling(self):
        self.assertEqual(self.res["counts"]["bss_indices"], [3, 4, 6])
        for index in (3, 4, 6):
            self.assertFalse(
                os.path.isfile(os.path.join(FIX, "bss_synthetic.b%02d" % index)))
            entry = [s for s in self.res["siblings"] if s["index"] == index][0]
            self.assertEqual(entry["verdict"], cdsp_probe.VERDICT_ABSENT)
            self.assertEqual(entry["expected_bytes"], 0)

    def test_four_payload_rows_match(self):
        self.assertEqual(self.res["counts"]["sibling_match"], 4)
        self.assertEqual(self.res["counts"]["sibling_absent_as_predicted"], 3)

    def test_bss_reservation_exceeds_the_file_size(self):
        self.assertEqual(self.res["totals"]["bss_bytes"], 114688)
        self.assertGreater(self.res["totals"]["bss_bytes"], self.res["size"])

    def test_every_filesz_row_is_smaller_than_its_memsz(self):
        for row in self.res["program_headers"]:
            self.assertLessEqual(row["p_filesz"], row["p_memsz"])


class TestMalformedInput(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.buf = readf(MAIN_MDT)

    def test_huge_e_phnum(self):
        buf = bytearray(self.buf)
        struct.pack_into("<H", buf, 44, 0xFFF0)
        res = cdsp_probe.probe_bytes(bytes(buf), "huge")
        self.assertFalse(res["structural_ok"])
        self.assertIn("parse_error", res)
        self.assertTrue(any("program-header table ends" in m
                            for m in res["violations"]), res["violations"])

    def test_e_phoff_past_eof(self):
        buf = bytearray(self.buf)
        struct.pack_into("<I", buf, 28, 0x7FFFFFF0)
        res = cdsp_probe.probe_bytes(bytes(buf), "phoff-eof")
        self.assertFalse(res["structural_ok"])
        self.assertIn("past the end of the file", res["parse_error"])
        self.assertEqual(res["header"]["e_phoff"], 0x7FFFFFF0)
        self.assertEqual(res["program_headers"], [])

    def test_zero_length_file(self):
        res = cdsp_probe.probe_bytes(b"", "empty")
        self.assertFalse(res["structural_ok"])
        self.assertEqual(res["size"], 0)
        self.assertIn("too small", res["parse_error"])
        self.assertEqual(res["sha256"], hashlib.sha256(b"").hexdigest())

    def test_fifty_two_zero_bytes(self):
        res = cdsp_probe.probe_bytes(b"\x00" * 52, "zeros")
        self.assertFalse(res["structural_ok"])
        self.assertIn("magic", res["parse_error"])
        self.assertGreaterEqual(len(res["violations"]), 8)

    def test_non_elf_ascii_is_rejected(self):
        res = cdsp_probe.probe_bytes(b"NOT AN ELF FILE AT ALL" * 4, "ascii")
        self.assertFalse(res["structural_ok"])
        self.assertIn("magic", res["parse_error"])

    def test_random_input_never_raises(self):
        rnd = random.Random(595)
        for n in (0, 1, 51, 52, 53, 96, 512, 8192):
            blob = bytes(rnd.randrange(256) for _ in range(n))
            res = cdsp_probe.probe_bytes(blob, "rnd")
            self.assertIn("structural_ok", res)
            self.assertIn("violations", res)
            self.assertFalse(res["structural_ok"])

    def test_probe_always_returns_the_open_list(self):
        for blob in (b"", b"\x7fELF", readf(MAIN_MDT)):
            res = cdsp_probe.probe_bytes(blob, "open")
            self.assertTrue(res["open"])
            self.assertTrue(any("OPEN" in m or "not" in m for m in res["open"]))

    def test_hashes_are_always_present(self):
        res = cdsp_probe.probe_bytes(b"\x01\x02\x03", "short")
        self.assertEqual(res["md5"], hashlib.md5(b"\x01\x02\x03").hexdigest())
        self.assertEqual(res["sha256"],
                         hashlib.sha256(b"\x01\x02\x03").hexdigest())


class TestRenderAndJson(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = cdsp_probe.probe_file(MAIN_MDT)

    def test_result_is_json_serialisable(self):
        json.dumps(self.res, sort_keys=True)

    def test_required_top_level_keys(self):
        for key in ("path", "size", "md5", "sha256", "header",
                    "program_headers", "siblings", "counts", "totals",
                    "split", "hash_segment", "entry_segment", "violations",
                    "notes", "open", "structural_ok", "orphans"):
            self.assertIn(key, self.res)

    def test_hashes_match_the_file(self):
        buf = readf(MAIN_MDT)
        self.assertEqual(self.res["md5"], hashlib.md5(buf).hexdigest())
        self.assertEqual(self.res["sha256"], hashlib.sha256(buf).hexdigest())

    def test_text_report_names_every_section(self):
        text = cdsp_probe.render_text(self.res)
        for section in ("ELF HEADER", "PROGRAM HEADERS", "P_FLAGS DECODE",
                        "SIBLINGS", "COUNTS", "TOTALS",
                        "STRUCTURAL VIOLATIONS", "[OPEN]"):
            self.assertIn(section, text)

    def test_text_report_carries_the_measured_values(self):
        text = cdsp_probe.render_text(self.res)
        self.assertIn("e_phoff       : 52", text)
        self.assertIn("e_phentsize   : 32", text)
        self.assertIn("e_phnum       : 13", text)
        self.assertIn("0x07000000", text)
        self.assertIn("ABSENT-as-predicted", text)
        self.assertIn("isa=V66", text)

    def test_text_report_states_the_observed_convention(self):
        rows = make_fixture.split_rows()
        rows[0]["memsz"] = 0
        image = make_fixture.build_image("fx-cdsp", rows)
        res = cdsp_probe.probe_bytes(image, "conv.mdt")
        text = cdsp_probe.render_text(res)
        self.assertIn("[F] observed convention", text)
        self.assertNotIn("loader refuses this segment", text)

    def test_brief_line_is_one_line_with_counts(self):
        line = cdsp_probe.brief_line(self.res)
        self.assertEqual(len(line.splitlines()), 1)
        self.assertIn("phdr=13", line)
        self.assertIn("load=11", line)
        self.assertIn("bss=3", line)
        self.assertIn("hash=1", line)


class TestCli(unittest.TestCase):

    def test_full_report_exit_one_on_violation(self):
        r = run_cli([MAIN_MDT])
        self.assertEqual(r.returncode, 1)
        self.assertIn("ELF HEADER", r.stdout)
        self.assertIn("VIOLATIONS", r.stdout)

    def test_clean_split_image_exits_zero(self):
        d = tmpdir()
        try:
            r = run_cli([write_clean_tree(d)])
            self.assertEqual(r.returncode, 0, r.stderr)
            self.assertIn("STRUCTURAL VIOLATIONS: none", r.stdout)
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_brief_is_one_line_per_file(self):
        r = run_cli([MAIN_MDT, BSS_MDT, "--brief"])
        self.assertEqual(r.returncode, 1)
        lines = [l for l in r.stdout.splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("cdsp_synthetic.mdt"))
        self.assertTrue(lines[1].startswith("bss_synthetic.mdt"))

    def test_json_file_is_written_and_valid(self):
        d = tmpdir()
        try:
            out = os.path.join(d, "res.json")
            r = run_cli([MAIN_MDT, "--json", out, "--brief"])
            self.assertEqual(r.returncode, 1)
            with open(out) as fh:
                data = json.load(fh)
            self.assertEqual(data["size"], MAIN_MDT_BYTES)
            self.assertEqual(data["header"]["e_phnum"], 13)
            self.assertEqual(len(data["program_headers"]), 13)
            self.assertEqual(data["counts"]["bss_indices"], [7, 10, 12])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_json_list_for_multiple_files(self):
        d = tmpdir()
        try:
            out = os.path.join(d, "res.json")
            r = run_cli([MAIN_MDT, BSS_MDT, "--json", out, "--brief"])
            self.assertEqual(r.returncode, 1)
            with open(out) as fh:
                data = json.load(fh)
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[1]["counts"]["bss_indices"], [3, 4, 6])
        finally:
            shutil.rmtree(d, ignore_errors=True)

    def test_missing_file_exits_two(self):
        r = run_cli(["/nonexistent/image_cdsp.mdt"])
        self.assertEqual(r.returncode, 2)
        self.assertIn("not a file", r.stderr)

    def test_no_arguments_exits_two(self):
        r = run_cli([])
        self.assertEqual(r.returncode, 2)
        self.assertIn("usage", r.stderr.lower())

    def test_bad_magic_exit_and_message(self):
        r = run_cli([BADMAGIC_MDT, "--brief"])
        self.assertEqual(r.returncode, 1)
        self.assertIn("VIOLATIONS:1", r.stdout)

    def test_hash_fixture_names_the_missing_hash_segment(self):
        r = run_cli([BADHASH_MDT])
        self.assertEqual(r.returncode, 1)
        self.assertIn("QCOM_MDT_TYPE_HASH", r.stdout)

    def test_probe_runs_isolated_with_no_site_packages(self):
        r = subprocess.run(
            [sys.executable, "-I", "-c",
             "import sys; sys.path.insert(0, %r); import cdsp_probe; "
             "print(cdsp_probe.EM_HEXAGON)" % HERE],
            capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "164")


@unittest.skipUnless(have_real_blob(), "real image_cdsp.mdt not present locally")
class TestRealBlob(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.res = cdsp_probe.probe_file(REAL_MDT)

    def test_real_image_is_structurally_clean(self):
        self.assertTrue(self.res["structural_ok"], self.res["violations"])
        self.assertEqual(self.res["violations"], [])

    def test_real_image_measured_header(self):
        h = self.res["header"]
        self.assertEqual(self.res["size"], 7660)
        self.assertEqual(self.res["totals"]["sum_p_filesz"], 4129418)
        self.assertEqual(h["e_phoff"], 52)
        self.assertEqual(h["e_phentsize"], 32)
        self.assertEqual(h["e_phnum"], 13)
        self.assertEqual(h["e_entry"], 0x87800000)
        self.assertEqual(h["e_flags"], 0x66)
        self.assertEqual(h["sectionless"], True)

    def test_real_image_mdt_is_header_block_plus_hash(self):
        rows = self.res["program_headers"]
        self.assertEqual(rows[0]["p_filesz"], 468)
        self.assertEqual(rows[1]["p_filesz"], 7192)
        self.assertEqual(rows[0]["p_filesz"] + rows[1]["p_filesz"],
                         self.res["size"])

    def test_real_image_has_no_zi_tagged_row(self):
        self.assertEqual(self.res["counts"]["zi_rows"], 0)
        for index in (7, 10, 12):
            self.assertEqual(self.res["program_headers"][index]
                             ["flags"]["access_type"], 0)

    def test_real_image_siblings_all_match(self):
        self.assertEqual(self.res["counts"]["sibling_match"], 10)
        self.assertEqual(self.res["counts"]["sibling_size_mismatch"], 0)
        self.assertEqual(self.res["counts"]["sibling_missing"], 0)
        self.assertEqual(self.res["counts"]["sibling_absent_as_predicted"], 3)
        self.assertEqual(self.res["counts"]["bss_indices"], [7, 10, 12])

    def test_real_image_row_zero_convention_is_a_note(self):
        self.assertFalse(any("loader refuses" in m
                             for m in self.res["violations"]))
        self.assertTrue(any(n.startswith("[F] observed convention")
                            and "phdr[0]" in n for n in self.res["notes"]),
                        self.res["notes"])

    def test_real_image_program_header_shape(self):
        self.assertEqual(self.res["counts"]["pt_null"], 2)
        self.assertEqual(self.res["counts"]["pt_load"], 11)
        self.assertEqual(self.res["hash_segment"], 1)
        self.assertEqual(self.res["entry_segment"], 2)
        self.assertTrue(self.res["entry_matches_paddr"])
        self.assertTrue(self.res["split"])

    def test_real_image_role_agreements_hold(self):
        rows = self.res["program_headers"]
        self.assertEqual(rows[0]["flags"]["seg_type"], 7)
        self.assertEqual(rows[0]["flags"]["seg_type_name"], "PHDR")
        self.assertEqual(rows[1]["flags"]["seg_type"], 2)
        self.assertEqual(rows[1]["flags"]["seg_type_name"], "HASH")
        self.assertEqual(rows[1]["flags"]["access_type_name"], "RO")
        self.assertEqual(rows[0]["p_filesz"],
                         self.res["header"]["e_ehsize"] +
                         self.res["header"]["e_phnum"] *
                         self.res["header"]["e_phentsize"])

    def test_real_image_permissions_match_the_fixture_vocabulary(self):
        words = {row["p_flags"] for row in self.res["program_headers"]}
        self.assertEqual(words, {0x07000000, 0x02200000, 0x08000005,
                                 0x08000006, 0x08000004, 0x08000007})
        for row in self.res["program_headers"]:
            self.assertEqual(row["flags"]["unknown_high"], 0)

    def test_real_image_alignment_is_not_uniform(self):
        aligns = {row["index"]: row["p_align"]
                  for row in self.res["program_headers"]}
        self.assertEqual(aligns[0], 0)
        self.assertEqual(aligns[2], 0x100000)
        for index in range(1, 13):
            if index != 2:
                self.assertEqual(aligns[index], 0x1000)

    def test_real_brief_line_is_ok(self):
        r = run_cli([REAL_MDT, "--brief"])
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("OK", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
