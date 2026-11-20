#!/usr/bin/env python3
"""cdsp_probe.py -- clean-room parser and validation probe for the Qualcomm
split-MDT CDSP firmware container (``image_cdsp.mdt`` plus its ``.bNN``
siblings).

CLEAN-ROOM STATEMENT
--------------------
This file was written from public, permissively/GPL-licensed sources only:

  * ``include/uapi/linux/elf-em.h`` -- GPL-2.0 WITH Linux-syscall-note,
        ``#define EM_HEXAGON 164`` (the Qualcomm Hexagon / QDSP6 machine id).
  * ``include/uapi/linux/elf.h`` -- GPL-2.0 WITH Linux-syscall-note,
        the ``Elf32_Ehdr`` / ``Elf32_Phdr`` field order and sizes, the
        ``PT_NULL`` / ``PT_LOAD`` program-header types and the ``PF_R`` /
        ``PF_W`` / ``PF_X`` permission bits.
  * ``include/linux/soc/qcom/mdt_loader.h`` -- GPL-2.0-only,
        ``QCOM_MDT_TYPE_MASK``, ``QCOM_MDT_TYPE_HASH`` and
        ``QCOM_MDT_RELOCATABLE``. These give the bit positions of the
        Qualcomm segment-type field and the relocatable/pool bit, which is
        what makes the ``p_flags`` layout a fact rather than a guess.
  * ``drivers/soc/qcom/mdt_loader.c`` -- GPL-2.0-only, the loader that
        consumes these images. ``mdt_phdr_loadable()`` defines which rows
        are loaded, ``qcom_mdt_read_metadata()`` documents that in a split
        image the hash segment follows the ELF header rather than sitting at
        ``p_offset``, and ``qcom_mdt_bins_are_split()`` defines the split
        predicate. ``mdt_load_split_segment()`` builds the sibling name with
        ``sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)`` and
        rejects a sibling whose size differs from ``p_filesz``.
  * ``util/qualcomm/mbn_tools.py`` in coreboot -- GPL-2.0, the packed
        ``p_flags`` bit layout: bit 27 pool index, bits 26-24 segment type,
        bits 23-21 access type, bit 20 page mode, bits 2-0 R/W/X, plus the
        segment-type and access-type vocabularies.
  * ``llvm/lib/Target/Hexagon/MCTargetDesc/HexagonBaseInfo.h`` --
        Apache-2.0-with-LLVM-exception, the ``INST_PARSE_*`` parse bits at
        ``[15:14]`` and the ``INST_ICLASS_*`` opcode-class field at
        ``[31:28]``, plus ``llvm/include/llvm/BinaryFormat/ELF.h`` for the
        ``EF_HEXAGON_ISA_V*`` e_flags encoding.

plus **own structural measurements** of publicly redistributable firmware
images. No decompiled code, no proprietary documentation and no disassembly
were used. Every number this tool prints is either (a) read from the file in
front of it or (b) one of the public constants named above. Anything else is
reported as ``[OPEN]`` rather than guessed.

WHAT THIS TOOL ESTABLISHES
--------------------------
A Qualcomm split-MDT image is an ELF32 little-endian executable whose section
headers are absent and whose entire structure lives in the program headers.
The ``.mdt`` file holds only the ELF header block and the hash segment; every
payload byte lives in a sibling ``.bNN`` file, one per program header, named
by the segment index. Three invariants are checked, each traceable to the
loader sources above:

``header_block``
    ``phdr[0]`` is ``PT_NULL`` and its ``p_filesz`` equals
    ``e_ehsize + e_phnum * e_phentsize``: the first segment *is* the ELF
    header plus the program-header table.

``hash_follows_header``
    exactly one further ``PT_NULL`` row carries segment type 2 (``HASH``),
    and ``phdr[0].p_filesz + phdr[hash].p_filesz == len(mdt)``. In a split
    image the hash bytes sit directly after the header block, not at the
    hash row's ``p_offset`` -- this is the behaviour
    ``qcom_mdt_read_metadata()`` describes in its own comment.

``sibling_size``
    for every row with ``p_filesz > 0`` a sibling ``<stem>.bNN`` exists and
    its size equals ``p_filesz`` exactly. A row with ``p_filesz == 0`` is a
    zero-fill (BSS) segment and has no sibling: there is no payload to
    place. ``mdt_load_split_segment()`` refuses a sibling whose size differs
    from ``p_filesz``, so this is the loader's own contract, not a
    convention invented here.

The ``p_flags`` word is decoded in full and reported per segment. Two
independent role agreements make the decode verifiable rather than merely
self-consistent: segment 0 decodes to type 7 (``PHDR``) and really is the
program-header table, and segment 1 decodes to type 2 (``HASH``) and really
is the hash/certificate segment.

A ``PT_NULL`` row that decodes to ``PHDR`` or ``HASH`` legitimately carries a
non-zero ``p_filesz`` with ``p_memsz = 0``: a header or hash block has a file
image and no memory image. That is reported as an ``[F] observed convention``
note. The same size relation on a ``PT_LOAD`` row *is* a violation, because
there the loader would have to place more bytes than the segment reserves.

Everything about *meaning* -- why one segment is RWX and the next is RW, what
consumes the payload at runtime, whether a given segment is code -- is out of
scope and reported as ``[OPEN]``. This tool establishes STRUCTURE and
VALIDATION, not semantics.

CLI
---
    python3 -I cdsp_probe.py <image.mdt> [--json out.json] [--brief]

Exit status: 0 = every invariant holds, 1 = at least one violation, 2 =
usage or IO error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import struct
import sys

ELF_MAGIC = b"\x7fELF"
EI_CLASS = 4
EI_DATA = 5
EI_VERSION = 6
ELFCLASS32 = 1
ELFDATA2LSB = 1
EV_CURRENT = 1
ELF32_EHDR_SIZE = 52
ELF32_PHDR_SIZE = 32

EHDR_STRUCT = struct.Struct("<16sHHIIIIIHHHHHH")
PHDR_STRUCT = struct.Struct("<IIIIIIII")

EM_HEXAGON = 164
EM_NAMES = {
    3: "EM_386",
    40: "EM_ARM",
    62: "EM_X86_64",
    94: "EM_XTENSA",
    164: "EM_HEXAGON/EM_QDSP6",
    183: "EM_AARCH64",
    243: "EM_RISCV",
}

ET_NAMES = {0: "ET_NONE", 1: "ET_REL", 2: "ET_EXEC", 3: "ET_DYN", 4: "ET_CORE"}

PT_NULL = 0
PT_LOAD = 1
PT_NAMES = {
    0: "PT_NULL",
    1: "PT_LOAD",
    2: "PT_DYNAMIC",
    3: "PT_INTERP",
    4: "PT_NOTE",
    5: "PT_SHLIB",
    6: "PT_PHDR",
    7: "PT_TLS",
}

PF_X = 0x1
PF_W = 0x2
PF_R = 0x4

QCOM_MDT_TYPE_MASK = 7 << 24
QCOM_MDT_TYPE_HASH = 2 << 24
QCOM_MDT_RELOCATABLE = 1 << 27

MI_PBT_FLAG_POOL_INDEX_MASK = 0x08000000
MI_PBT_FLAG_POOL_INDEX_SHIFT = 0x1B
MI_PBT_FLAG_SEGMENT_TYPE_MASK = 0x07000000
MI_PBT_FLAG_SEGMENT_TYPE_SHIFT = 0x18
MI_PBT_FLAG_ACCESS_TYPE_MASK = 0x00E00000
MI_PBT_FLAG_ACCESS_TYPE_SHIFT = 0x15
MI_PBT_FLAG_PAGE_MODE_MASK = 0x00100000
MI_PBT_FLAG_PAGE_MODE_SHIFT = 0x14

SEG_TYPE_NAMES = {
    0: "L4/AMSS",
    1: "AMSS",
    2: "HASH",
    3: "BOOT",
    4: "L4BSP",
    5: "SWAPPED/XBL_SEC",
    6: "SWAP_POOL",
    7: "PHDR",
}

ACCESS_TYPE_NAMES = {
    0: "RW",
    1: "RO",
    2: "ZI",
    3: "NOTUSED",
    4: "SHARED",
    5: "UNUSED5",
    6: "UNUSED6",
    7: "RWE",
}

PAGE_MODE_NAMES = {0: "NON_PAGED", 1: "PAGED"}

ISA_NAMES = {
    0x60: "V60",
    0x61: "V61",
    0x62: "V62",
    0x65: "V65",
    0x66: "V66",
    0x67: "V67",
    0x68: "V68",
    0x69: "V69",
    0x71: "V71",
    0x73: "V73",
    0x75: "V75",
}

VERDICT_MATCH = "MATCH"
VERDICT_SIZE_MISMATCH = "SIZE-MISMATCH"
VERDICT_MISSING = "MISSING"
VERDICT_ABSENT = "ABSENT-as-predicted"
VERDICT_ZERO_BYTE = "ZERO-BYTE-SIBLING"


class StructureError(Exception):
    """Raised when an image violates the established container layout."""

    def __init__(self, message, violations=None):
        super().__init__(message)
        self.violations = list(violations or [message])


def u16(buf, off):
    return struct.unpack_from("<H", buf, off)[0]


def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def rwx_string(flags):
    """Render the standard PF_R/PF_W/PF_X bits as a three-character string."""
    return "".join((
        "R" if flags & PF_R else "-",
        "W" if flags & PF_W else "-",
        "X" if flags & PF_X else "-",
    ))


def isa_name(e_flags):
    """Name the Hexagon ISA nibble, or None when it is not in the public table."""
    return ISA_NAMES.get(e_flags & 0xFFF)


def decode_pflags(word):
    """Decode the packed Qualcomm ``p_flags`` word.

    Layout, from coreboot ``util/qualcomm/mbn_tools.py`` and the
    ``QCOM_MDT_*`` masks in ``include/linux/soc/qcom/mdt_loader.h``::

        31 30 29 28 | 27 pool/relocatable | 26-24 segment type
                    | 23-21 access type | 20 page mode | 2-0 R/W/X

    Every field is reported; nothing is inferred. ``unknown_high`` is
    ``word >> 28`` and is expected to be zero on every image measured so far,
    but it is reported rather than asserted away.
    """
    seg_type = (word & MI_PBT_FLAG_SEGMENT_TYPE_MASK) >> MI_PBT_FLAG_SEGMENT_TYPE_SHIFT
    access = (word & MI_PBT_FLAG_ACCESS_TYPE_MASK) >> MI_PBT_FLAG_ACCESS_TYPE_SHIFT
    page = (word & MI_PBT_FLAG_PAGE_MODE_MASK) >> MI_PBT_FLAG_PAGE_MODE_SHIFT
    pool = (word & MI_PBT_FLAG_POOL_INDEX_MASK) >> MI_PBT_FLAG_POOL_INDEX_SHIFT
    bits = [b for b in range(32) if word & (1 << b)]
    return {
        "raw": word,
        "raw_hex": "0x%08x" % word,
        "relocatable": bool(word & QCOM_MDT_RELOCATABLE),
        "pool_index": pool,
        "seg_type": seg_type,
        "seg_type_hex": "0x%02x" % seg_type,
        "seg_type_name": SEG_TYPE_NAMES.get(seg_type, "UNKNOWN"),
        "is_hash": (word & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH,
        "is_phdr": seg_type == 7,
        "access_type": access,
        "access_type_hex": "0x%x" % access,
        "access_type_name": ACCESS_TYPE_NAMES.get(access, "UNKNOWN"),
        "is_zi": access == 2,
        "page_mode": page,
        "page_mode_name": PAGE_MODE_NAMES.get(page, "UNKNOWN"),
        "pf_r": bool(word & PF_R),
        "pf_w": bool(word & PF_W),
        "pf_x": bool(word & PF_X),
        "rwx": rwx_string(word),
        "low3": word & 0x7,
        "unknown_high": word >> 28,
        "unknown_high_hex": "0x%08x" % (word & 0xF0000000),
        "bits_set": bits,
    }


def parse_ehdr(buf):
    """Parse and validate the 52-byte ``Elf32_Ehdr`` at offset 0."""
    n = len(buf)
    if n < ELF32_EHDR_SIZE:
        raise StructureError(
            "file is %d bytes, too small for an Elf32_Ehdr (%d bytes)"
            % (n, ELF32_EHDR_SIZE)
        )
    (ident, e_type, e_machine, e_version, e_entry, e_phoff, e_shoff, e_flags,
     e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum,
     e_shstrndx) = EHDR_STRUCT.unpack_from(buf, 0)

    v = []
    if ident[:4] != ELF_MAGIC:
        v.append(
            "e_ident magic is %s, expected %s"
            % (ident[:4].hex(), ELF_MAGIC.hex())
        )
    if ident[EI_CLASS] != ELFCLASS32:
        v.append(
            "e_ident[EI_CLASS] = %d, expected %d (ELFCLASS32)"
            % (ident[EI_CLASS], ELFCLASS32)
        )
    if ident[EI_DATA] != ELFDATA2LSB:
        v.append(
            "e_ident[EI_DATA] = %d, expected %d (ELFDATA2LSB)"
            % (ident[EI_DATA], ELFDATA2LSB)
        )
    if ident[EI_VERSION] != EV_CURRENT:
        v.append(
            "e_ident[EI_VERSION] = %d, expected %d (EV_CURRENT)"
            % (ident[EI_VERSION], EV_CURRENT)
        )
    if e_version != EV_CURRENT:
        v.append("e_version = %d, expected %d" % (e_version, EV_CURRENT))
    if e_ehsize != ELF32_EHDR_SIZE:
        v.append(
            "e_ehsize = %d, expected %d (sizeof(Elf32_Ehdr))"
            % (e_ehsize, ELF32_EHDR_SIZE)
        )
    if e_phentsize != ELF32_PHDR_SIZE:
        v.append(
            "e_phentsize = %d, expected %d (sizeof(Elf32_Phdr))"
            % (e_phentsize, ELF32_PHDR_SIZE)
        )
    if e_phnum < 2:
        v.append(
            "e_phnum = %d, a split image needs at least a header row and a "
            "hash row" % e_phnum
        )
    if e_machine != EM_HEXAGON:
        v.append(
            "e_machine = %d (%s), expected %d (EM_HEXAGON/EM_QDSP6)"
            % (e_machine, EM_NAMES.get(e_machine, "unknown"), EM_HEXAGON)
        )
    if e_type not in (2, 3):
        v.append(
            "e_type = %d (%s), expected ET_EXEC (2) or ET_DYN (3)"
            % (e_type, ET_NAMES.get(e_type, "unknown"))
        )
    if e_phnum and e_phoff < ELF32_EHDR_SIZE:
        v.append(
            "e_phoff = %d overlaps the ELF header (min %d)"
            % (e_phoff, ELF32_EHDR_SIZE)
        )
    table_end = e_phoff + e_phentsize * e_phnum
    if e_phnum and table_end > n:
        v.append(
            "program-header table ends at 0x%x, past the file size 0x%x"
            % (table_end, n)
        )
    if e_shnum and e_shoff + e_shentsize * e_shnum > n:
        v.append(
            "section-header table ends at 0x%x, past the file size 0x%x"
            % (e_shoff + e_shentsize * e_shnum, n)
        )

    if v and ident[:4] != ELF_MAGIC:
        raise StructureError(v[0], v)

    return {
        "e_ident_hex": ident.hex(),
        "e_type": e_type,
        "e_type_name": ET_NAMES.get(e_type, "unknown"),
        "e_machine": e_machine,
        "e_machine_name": EM_NAMES.get(e_machine, "unknown"),
        "e_version": e_version,
        "e_entry": e_entry,
        "e_entry_hex": "0x%08x" % e_entry,
        "e_phoff": e_phoff,
        "e_shoff": e_shoff,
        "e_flags": e_flags,
        "e_flags_hex": "0x%08x" % e_flags,
        "e_flags_isa_nibble": "0x%03x" % (e_flags & 0xFFF),
        "e_flags_isa_name": isa_name(e_flags),
        "e_flags_high": "0x%08x" % (e_flags & ~0xFFF & 0xFFFFFFFF),
        "e_ehsize": e_ehsize,
        "e_phentsize": e_phentsize,
        "e_phnum": e_phnum,
        "e_shentsize": e_shentsize,
        "e_shnum": e_shnum,
        "e_shstrndx": e_shstrndx,
        "phdr_table_offset": e_phoff,
        "phdr_table_bytes": e_phentsize * e_phnum,
        "phdr_table_end": table_end,
        "sectionless": e_shnum == 0 and e_shoff == 0,
        "violations": v,
    }


def parse_phdrs(buf, ehdr):
    """Walk every program header and attach its decoded ``p_flags``."""
    phoff = ehdr["e_phoff"]
    phnum = ehdr["e_phnum"]
    phentsize = ehdr["e_phentsize"]
    rows = []
    for i in range(phnum):
        off = phoff + i * phentsize
        if off + ELF32_PHDR_SIZE > len(buf):
            raise StructureError(
                "program header %d at 0x%x is past the end of the file" % (i, off)
            )
        (p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags,
         p_align) = PHDR_STRUCT.unpack_from(buf, off)
        row = {
            "index": i,
            "phdr_offset": off,
            "p_type": p_type,
            "p_type_name": PT_NAMES.get(p_type, "0x%x" % p_type),
            "p_offset": p_offset,
            "p_offset_hex": "0x%08x" % p_offset,
            "p_vaddr": p_vaddr,
            "p_vaddr_hex": "0x%08x" % p_vaddr,
            "p_paddr": p_paddr,
            "p_paddr_hex": "0x%08x" % p_paddr,
            "p_filesz": p_filesz,
            "p_memsz": p_memsz,
            "p_align": p_align,
            "p_flags": p_flags,
            "p_flags_hex": "0x%08x" % p_flags,
            "flags": decode_pflags(p_flags),
            "bss": p_filesz == 0 and p_memsz > 0,
            "loadable": (
                p_type == PT_LOAD
                and (p_flags & QCOM_MDT_TYPE_MASK) != QCOM_MDT_TYPE_HASH
                and p_memsz != 0
            ),
            "in_file": p_filesz > 0 and p_offset + p_filesz <= len(buf),
        }
        rows.append(row)
    return rows


def bins_are_split(buf, phdrs):
    """The loader's split predicate, from ``qcom_mdt_bins_are_split()``.

    A non-split image is large enough to contain every segment in-line. If
    any row with ``p_filesz > 0`` claims bytes beyond the end of the file,
    the payload must live in siblings instead.
    """
    n = len(buf)
    for row in phdrs:
        if not row["p_filesz"]:
            continue
        if row["p_offset"] > n or row["p_offset"] + row["p_filesz"] > n:
            return True
    return False


def find_hash_segment(phdrs):
    """Index of the single ``QCOM_MDT_TYPE_HASH`` row at index >= 1, or None."""
    for row in phdrs[1:]:
        if (row["p_flags"] & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH:
            return row["index"]
    return None


def sibling_path(mdt_path, index):
    """Sibling name exactly as the loader builds it.

    ``mdt_load_split_segment()`` does
    ``sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)``: it
    overwrites the last three characters of the ``.mdt`` name, so
    ``image_cdsp.mdt`` becomes ``image_cdsp.b00``.

    The on-disk name is resolved case-insensitively, because vendor FAT
    volumes carry 8.3 uppercase names (``CDSP.MDT`` with ``CDSP.B00``
    beside it) while the loader builds lowercase ones. A case-sensitive
    join reports a valid image as nine missing siblings.
    """
    if len(mdt_path) < 4:
        return None
    candidate = mdt_path[:-3] + "b%02d" % index
    if os.path.isfile(candidate):
        return candidate
    resolved = _resolve_ci(candidate)
    return resolved if resolved is not None else candidate


def _resolve_ci(path):
    """Return the real on-disk name of ``path``, matched case-insensitively."""
    directory = os.path.dirname(os.path.abspath(path))
    target = os.path.basename(path).lower()
    try:
        names = os.listdir(directory)
    except OSError:
        return None
    for name in names:
        if name.lower() == target:
            return os.path.join(directory, name)
    return None


def scan_siblings(mdt_path, phdrs):
    """Read sibling sizes from disk and classify each program header row."""
    sizes = {}
    for row in phdrs:
        path = sibling_path(mdt_path, row["index"])
        if path and os.path.isfile(path):
            sizes[row["index"]] = os.path.getsize(path)
    orphans = []
    directory = os.path.dirname(os.path.abspath(mdt_path))
    stem = os.path.basename(mdt_path)[:-3]
    stem_lower = stem.lower()
    referenced = {row["index"] for row in phdrs}
    try:
        names = sorted(os.listdir(directory))
    except OSError:
        names = []
    for name in names:
        if not name.lower().startswith(stem_lower + "b") or len(name) != len(stem) + 3:
            continue
        suffix = name[len(stem) + 1:]
        if not suffix.isdigit():
            continue
        index = int(suffix)
        if index not in referenced:
            orphans.append({
                "name": name,
                "index": index,
                "bytes": os.path.getsize(os.path.join(directory, name)),
            })
    return sizes, orphans


def classify_sibling(row, sizes):
    """Apply the sibling-size rule to one program header row."""
    index = row["index"]
    path = row.get("name") or row.get("sibling_name")
    present = index in sizes
    size = sizes.get(index)
    filesz = row["p_filesz"]
    if filesz > 0:
        if not present:
            verdict = VERDICT_MISSING
        elif size == filesz:
            verdict = VERDICT_MATCH
        else:
            verdict = VERDICT_SIZE_MISMATCH
    else:
        if not present:
            verdict = VERDICT_ABSENT
        elif size == 0:
            verdict = VERDICT_ZERO_BYTE
        else:
            verdict = VERDICT_SIZE_MISMATCH
    return {
        "index": index,
        "expected_bytes": filesz,
        "sibling_name": path,
        "sibling_present": present,
        "sibling_bytes": size,
        "verdict": verdict,
        "ok": verdict in (VERDICT_MATCH, VERDICT_ABSENT, VERDICT_ZERO_BYTE),
    }


def probe_bytes(buf, path="<memory>", sibling_sizes=None):
    """Full structural probe of one in-memory ``.mdt`` payload.

    ``sibling_sizes`` maps segment index to on-disk sibling size. When it is
    ``None`` the sibling rule is reported as unchecked rather than guessed.
    """
    result = {
        "path": path,
        "size": len(buf),
        "md5": hashlib.md5(buf).hexdigest(),
        "sha256": hashlib.sha256(buf).hexdigest(),
        "header": None,
        "program_headers": [],
        "siblings": [],
        "orphans": [],
        "counts": {},
        "totals": {},
        "split": None,
        "hash_segment": None,
        "entry_segment": None,
        "entry_inside_load": False,
        "violations": [],
        "notes": [],
        "open": [],
        "structural_ok": False,
    }

    try:
        ehdr = parse_ehdr(buf)
    except StructureError as exc:
        result["violations"] = exc.violations or [str(exc)]
        result["parse_error"] = str(exc)
        result["open"] = default_open_list()
        return result

    violations = list(ehdr.pop("violations"))
    result["header"] = ehdr

    try:
        phdrs = parse_phdrs(buf, ehdr)
    except StructureError as exc:
        result["violations"] = violations + (exc.violations or [str(exc)])
        result["parse_error"] = str(exc)
        result["open"] = default_open_list()
        return result

    result["program_headers"] = phdrs
    phnum = len(phdrs)
    n = len(buf)

    if phdrs:
        first = phdrs[0]
        expected_block = ehdr["e_ehsize"] + ehdr["e_phentsize"] * phnum
        if first["p_type"] != PT_NULL:
            violations.append(
                "phdr[0].p_type = %d (%s), expected PT_NULL: the first segment "
                "is the ELF header plus the program-header table"
                % (first["p_type"], first["p_type_name"])
            )
        if first["p_filesz"] != expected_block:
            violations.append(
                "phdr[0].p_filesz = %d, expected %d "
                "(e_ehsize + e_phnum * e_phentsize)"
                % (first["p_filesz"], expected_block)
            )
        if not first["flags"]["is_phdr"]:
            violations.append(
                "phdr[0].p_flags = %s decodes to segment type %d (%s), "
                "expected 7 (PHDR)"
                % (first["p_flags_hex"], first["flags"]["seg_type"],
                   first["flags"]["seg_type_name"])
            )

    hash_index = find_hash_segment(phdrs)
    result["hash_segment"] = hash_index
    if hash_index is None:
        violations.append(
            "no program header carries QCOM_MDT_TYPE_HASH (segment type 2); "
            "the loader requires exactly one hash segment"
        )
    else:
        hash_row = phdrs[hash_index]
        if hash_row["p_type"] != PT_NULL:
            violations.append(
                "phdr[%d] is the hash segment but p_type = %d (%s), expected "
                "PT_NULL" % (hash_index, hash_row["p_type"],
                             hash_row["p_type_name"])
            )
        if phdrs:
            pair = phdrs[0]["p_filesz"] + hash_row["p_filesz"]
            if pair != n:
                violations.append(
                    "phdr[0].p_filesz + phdr[%d].p_filesz = %d, expected the "
                    "file size %d: in a split image the .mdt holds only the "
                    "header block and the hash segment"
                    % (hash_index, pair, n)
                )

    for row in phdrs:
        if row["p_filesz"] > row["p_memsz"]:
            if row["p_memsz"] == 0 and (row["p_type"] == PT_NULL
                                       or row["flags"]["is_phdr"]):
                result["notes"].append(
                    "[F] observed convention: phdr[%d] is %s with segment "
                    "type %d (%s) and carries p_filesz = %d with p_memsz = 0; "
                    "a header or hash block has no memory image, so a "
                    "non-zero p_filesz here is the format's own shape and "
                    "not a violation"
                    % (row["index"], row["p_type_name"],
                       row["flags"]["seg_type"],
                       row["flags"]["seg_type_name"], row["p_filesz"])
                )
            else:
                violations.append(
                    "phdr[%d].p_filesz = %d exceeds p_memsz = %d; the loader "
                    "refuses this segment"
                    % (row["index"], row["p_filesz"], row["p_memsz"])
                )
        if row["flags"]["unknown_high"]:
            violations.append(
                "phdr[%d].p_flags = %s has bits 31-28 set (%s); those bits "
                "are not part of any public Qualcomm layout"
                % (row["index"], row["p_flags_hex"],
                   row["flags"]["unknown_high_hex"])
            )

    load_rows = [row for row in phdrs if row["p_type"] == PT_LOAD]
    reloc = {row["flags"]["relocatable"] for row in load_rows}
    if len(reloc) > 1:
        violations.append(
            "QCOM_MDT_RELOCATABLE (bit 27) is not uniform across the %d "
            "PT_LOAD rows" % len(load_rows)
        )

    split = bins_are_split(buf, phdrs)
    result["split"] = split
    if not split:
        for row in phdrs:
            if row["p_filesz"] and row["p_offset"] + row["p_filesz"] > n:
                violations.append(
                    "phdr[%d] claims bytes [0x%x, 0x%x) past the file size "
                    "0x%x" % (row["index"], row["p_offset"],
                              row["p_offset"] + row["p_filesz"], n)
                )

    entry = ehdr["e_entry"]
    entry_segment = None
    for row in load_rows:
        if row["p_paddr"] <= entry < row["p_paddr"] + row["p_memsz"]:
            entry_segment = row["index"]
            break
    result["entry_segment"] = entry_segment
    result["entry_inside_load"] = entry_segment is not None
    result["entry_matches_paddr"] = any(
        row["p_paddr"] == entry for row in phdrs
    )
    if entry_segment is None:
        violations.append(
            "e_entry = 0x%08x lies in no PT_LOAD segment's "
            "[p_paddr, p_paddr + p_memsz)" % entry
        )

    if sibling_sizes is None:
        result["siblings"] = []
        result["notes"].append(
            "sibling files were not inspected (in-memory probe); the "
            "sibling-size rule is UNCHECKED, not satisfied"
        )
    else:
        siblings = []
        for row in phdrs:
            row["sibling_name"] = sibling_path(path, row["index"])
            entry_sib = classify_sibling(row, sibling_sizes)
            siblings.append(entry_sib)
            if entry_sib["verdict"] == VERDICT_MISSING:
                violations.append(
                    "phdr[%d] has p_filesz = %d but %s is missing"
                    % (row["index"], row["p_filesz"], entry_sib["sibling_name"])
                )
            elif entry_sib["verdict"] == VERDICT_SIZE_MISMATCH:
                violations.append(
                    "%s is %d bytes but phdr[%d].p_filesz = %d"
                    % (entry_sib["sibling_name"], entry_sib["sibling_bytes"],
                       row["index"], row["p_filesz"])
                )
            elif entry_sib["verdict"] == VERDICT_ZERO_BYTE:
                result["notes"].append(
                    "%s exists with 0 bytes for the p_filesz == 0 row %d; "
                    "this image ships an explicit empty sibling"
                    % (entry_sib["sibling_name"], row["index"])
                )
        result["siblings"] = siblings

    bss_rows = [row for row in phdrs if row["bss"]]
    result["counts"] = {
        "phdr_total": phnum,
        "pt_load": len(load_rows),
        "pt_null": sum(1 for row in phdrs if row["p_type"] == PT_NULL),
        "hash_segments": 1 if hash_index is not None else 0,
        "bss": len(bss_rows),
        "bss_indices": [row["index"] for row in bss_rows],
        "nonzero_filesz": sum(1 for row in phdrs if row["p_filesz"] > 0),
        "sibling_match": sum(1 for s in result["siblings"]
                             if s["verdict"] == VERDICT_MATCH),
        "sibling_size_mismatch": sum(1 for s in result["siblings"]
                                     if s["verdict"] == VERDICT_SIZE_MISMATCH),
        "sibling_missing": sum(1 for s in result["siblings"]
                               if s["verdict"] == VERDICT_MISSING),
        "sibling_absent_as_predicted": sum(
            1 for s in result["siblings"] if s["verdict"] == VERDICT_ABSENT),
        "relocatable_rows": sum(1 for row in phdrs
                                if row["flags"]["relocatable"]),
        "zi_rows": sum(1 for row in phdrs if row["flags"]["is_zi"]),
    }
    result["totals"] = {
        "sum_p_filesz": sum(row["p_filesz"] for row in phdrs),
        "sum_p_memsz": sum(row["p_memsz"] for row in phdrs),
        "bss_bytes": sum(row["p_memsz"] for row in bss_rows),
    }

    result["violations"] = violations
    result["structural_ok"] = not violations
    result["open"] = default_open_list()
    return result


def probe_file(path):
    """Probe one ``.mdt`` file and its sibling directory."""
    with open(path, "rb") as fh:
        buf = fh.read()
    result = probe_bytes(buf, path)
    if result["header"] is not None and result["program_headers"]:
        sizes, orphans = scan_siblings(path, result["program_headers"])
        result = probe_bytes(buf, path, sibling_sizes=sizes)
        result["orphans"] = orphans
        for orphan in orphans:
            result["notes"].append(
                "%s (%d bytes) is not referenced by any program header"
                % (orphan["name"], orphan["bytes"])
            )
        if orphans:
            result["structural_ok"] = not result["violations"]
    return result


def default_open_list():
    return [
        "why a given segment is RWX and the next is RW: linker policy, not "
        "decodable from p_flags",
        "what consumes the payload at runtime beyond the generic PAS loader",
        "whether a segment holds Hexagon instructions: p_flags and p_type do "
        "not say, and no disassembly is performed here",
        "the meaning of e_flags nibbles outside the public EF_HEXAGON_ISA_V* "
        "table",
        "the contents and record semantics of the hash/certificate segment",
    ]


def brief_line(res):
    counts = res.get("counts") or {}
    header = res.get("header") or {}
    return (
        "%s  %d B  phdr=%s load=%s bss=%s hash=%s split=%s siblings=%s/%s  %s"
        % (
            os.path.basename(res["path"]),
            res["size"],
            counts.get("phdr_total", "-"),
            counts.get("pt_load", "-"),
            counts.get("bss", "-"),
            counts.get("hash_segments", "-"),
            {True: "yes", False: "no", None: "?"}.get(res.get("split"), "?"),
            counts.get("sibling_match", "-"),
            counts.get("nonzero_filesz", "-"),
            "OK" if res.get("structural_ok")
            else "VIOLATIONS:%d" % len(res["violations"]),
        )
    )


def render_text(res):
    out = []
    a = out.append
    a("file            : %s" % res["path"])
    a("size            : %d bytes" % res["size"])
    a("md5             : %s" % res["md5"])
    a("sha256          : %s" % res["sha256"])

    hdr = res.get("header")
    if hdr:
        a("")
        a("ELF HEADER")
        a("  e_ident       : %s" % hdr["e_ident_hex"])
        a("  e_type        : %d (%s)" % (hdr["e_type"], hdr["e_type_name"]))
        a("  e_machine     : %d (%s)" % (hdr["e_machine"],
                                         hdr["e_machine_name"]))
        a("  e_entry       : %s" % hdr["e_entry_hex"])
        a("  e_phoff       : %d" % hdr["e_phoff"])
        a("  e_shoff       : %d" % hdr["e_shoff"])
        a("  e_flags       : %s  isa=%s high=%s"
          % (hdr["e_flags_hex"], hdr["e_flags_isa_name"] or "[OPEN]",
             hdr["e_flags_high"]))
        a("  e_ehsize      : %d" % hdr["e_ehsize"])
        a("  e_phentsize   : %d" % hdr["e_phentsize"])
        a("  e_phnum       : %d" % hdr["e_phnum"])
        a("  e_shentsize   : %d" % hdr["e_shentsize"])
        a("  e_shnum       : %d" % hdr["e_shnum"])
        a("  e_shstrndx    : %d" % hdr["e_shstrndx"])
        a("  sectionless   : %s" % hdr["sectionless"])

    rows = res.get("program_headers") or []
    if rows:
        a("")
        a("PROGRAM HEADERS (%d x %d B @ 0x%x)"
          % (len(rows), ELF32_PHDR_SIZE, rows[0]["phdr_offset"]))
        a("   i  type       offset      vaddr       paddr        filesz"
          "      memsz  p_flags     type       acc      pg   rwx")
        for row in rows:
            f = row["flags"]
            a("  %2d  %-9s %s  %s  %s  %8d  %8d  %s  %d %-9s %d %-7s %d %s"
              % (row["index"], row["p_type_name"], row["p_offset_hex"],
                 row["p_vaddr_hex"], row["p_paddr_hex"], row["p_filesz"],
                 row["p_memsz"], row["p_flags_hex"], f["seg_type"],
                 f["seg_type_name"], f["access_type"], f["access_type_name"],
                 f["page_mode"], f["rwx"]))
        a("")
        a("P_FLAGS DECODE (bit 27 pool/reloc, 26-24 type, 23-21 access, "
          "20 page, 2-0 R/W/X)")
        for row in rows:
            f = row["flags"]
            a("  [%2d] %s reloc=%d pool=%d type=%d(%-11s) access=%d(%-7s) "
              "page=%d(%-9s) %s high=%s"
              % (row["index"], row["p_flags_hex"], int(f["relocatable"]),
                 f["pool_index"], f["seg_type"], f["seg_type_name"],
                 f["access_type"], f["access_type_name"], f["page_mode"],
                 f["page_mode_name"], f["rwx"], f["unknown_high_hex"]))

    sibs = res.get("siblings") or []
    if sibs:
        a("")
        a("SIBLINGS")
        a("  %3s  %10s  %10s  %-24s %s"
          % ("i", "expected", "actual", "name", "verdict"))
        for s in sibs:
            a("  %3d  %10d  %10s  %-24s %s"
              % (s["index"], s["expected_bytes"],
                 "-" if s["sibling_bytes"] is None else s["sibling_bytes"],
                 s["sibling_name"] or "-", s["verdict"]))

    counts = res.get("counts") or {}
    totals = res.get("totals") or {}
    if counts:
        a("")
        a("COUNTS")
        a("  phdr total / PT_LOAD / PT_NULL : %d / %d / %d"
          % (counts["phdr_total"], counts["pt_load"], counts["pt_null"]))
        a("  hash segments                  : %d @ row %s"
          % (counts["hash_segments"], res.get("hash_segment")))
        a("  BSS rows (filesz==0, memsz>0)  : %d %s"
          % (counts["bss"], counts["bss_indices"]))
        a("  rows with p_filesz > 0         : %d" % counts["nonzero_filesz"])
        a("  relocatable rows (bit 27)      : %d" % counts["relocatable_rows"])
        a("  ZI-tagged rows                 : %d" % counts["zi_rows"])
        if sibs:
            a("  siblings match / mismatch      : %d / %d"
              % (counts["sibling_match"], counts["sibling_size_mismatch"]))
            a("  siblings missing / absent      : %d / %d"
              % (counts["sibling_missing"],
                 counts["sibling_absent_as_predicted"]))

    if totals:
        a("")
        a("TOTALS")
        a("  sum p_filesz                   : %d" % totals["sum_p_filesz"])
        a("  sum p_memsz                    : %d" % totals["sum_p_memsz"])
        a("  BSS reservation (filesz==0)    : %d" % totals["bss_bytes"])

    if res.get("orphans"):
        a("")
        a("ORPHAN SIBLINGS")
        for orphan in res["orphans"]:
            a("  %s  %d bytes  index %d unreferenced"
              % (orphan["name"], orphan["bytes"], orphan["index"]))

    if res.get("notes"):
        a("")
        a("NOTES")
        for note in res["notes"]:
            a("  - %s" % note)

    a("")
    if res.get("violations"):
        a("STRUCTURAL VIOLATIONS")
        for message in res["violations"]:
            a("  - %s" % message)
    else:
        a("STRUCTURAL VIOLATIONS: none")

    if res.get("open"):
        a("")
        a("[OPEN] (not claimed by this tool)")
        for message in res["open"]:
            a("  - %s" % message)
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="cdsp_probe.py",
        description="Clean-room parser and validation probe for Qualcomm "
                    "split-MDT CDSP images. Structure and invariants only; "
                    "semantics are [OPEN].",
    )
    ap.add_argument("files", nargs="+", help="split-MDT .mdt file(s)")
    ap.add_argument("--json", metavar="PATH", help="write full JSON to PATH")
    ap.add_argument("--brief", action="store_true",
                    help="one line per file instead of the full report")
    args = ap.parse_args(argv)

    missing = [p for p in args.files if not os.path.isfile(p)]
    if missing:
        for path in missing:
            sys.stderr.write("error: not a file: %s\n" % path)
        return 2

    results = []
    rc = 0
    for path in args.files:
        try:
            res = probe_file(path)
        except OSError as exc:
            sys.stderr.write("error: %s: %s\n" % (path, exc))
            rc = 2
            continue
        results.append(res)
        if not res["structural_ok"]:
            rc = 1

    if args.json:
        payload = results[0] if len(results) == 1 else results
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2, sort_keys=True)
            fh.write("\n")

    if args.brief:
        for res in results:
            sys.stdout.write(brief_line(res) + "\n")
    else:
        for i, res in enumerate(results):
            if i:
                sys.stdout.write("\n" + "=" * 78 + "\n\n")
            sys.stdout.write(render_text(res) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
