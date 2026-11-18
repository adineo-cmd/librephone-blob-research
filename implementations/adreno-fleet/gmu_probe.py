#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""gmu_probe.py -- clean-room structural probe for Qualcomm Adreno GMU
microcode images (``*_gmu.bin``).

CLEAN-ROOM STATEMENT
====================
This file was written from two sources only:

  1. Public GPL-2.0 kernel sources -- the mainline msm drm/msm driver
     (``drivers/gpu/drm/msm/adreno/a6xx_gmu.c``, ``a6xx_gmu.h``,
     ``a6xx_gmu.xml``, ``adreno_gpu.h``, ``a6xx_catalog.c``) and
     linux-firmware's ``WHENCE``.  All fetched 2026-11-18.
  2. The author's own structural measurements of payload bytes: byte
     histograms, offset arithmetic, entropy, and ARMv7-M architectural
     encodings that are publicly documented (ARM Architecture Reference
     Manual, ARMv7-M, exception model and Thumb-2 instruction encodings).

No decompiler, disassembler, Ghidra/IDA project, vendor datasheet,
proprietary header or leaked documentation was consulted.  No payload
bytes are reproduced in this file.  Every constant below is either
(a) quoted from the public sources named in the comment, or (b) the
result of the measurements documented in ``gmu-analysis.md``.

WHAT THIS PROBE ESTABLISHES (and what it does not)
==================================================
The premise "Adreno GMU firmware carries a documented ``a6xx_gmu_fw_header``
struct" is FALSE for mainline Linux.  No such struct exists in
``a6xx_gmu.h`` at v5.4, v5.10, v5.15, v6.1 or master, and a GitHub code
search for the identifier returns zero hits.  What mainline actually
documents is:

  * a *container* format: ``struct block_header`` (a6xx_gmu.c:857-863),
    a chain of ``{u32 addr; u32 size; u32 type; u32 value; u8 data[];}``
    records, each followed by ``size`` bytes of payload.  This is the
    NON-legacy load path.
  * a *raw* path for ``gmu->legacy`` parts (a619/a618/a630 belong to
    ``ADRENO_6XX_GEN1``, see a6xx_catalog.c and a6xx_gmu.c:2412-2414),
    which does no container parsing at all: it sanity-checks
    ``fw_image->size > 0x8000`` and then ``gmu_write_bulk``s the whole
    file to ``REG_A6XX_GMU_CM3_ITCM_START`` (a6xx_gmu.c:894-904).

So the probe tries the mainline ``block_header`` walk FIRST, reports
honestly whether it fits, and only then falls back to the layout that the
bytes actually exhibit.  Both branches are first-class; a negative result
on the mainline header is a valid finding, not a failure.

The probe reports STRUCTURE.  It does not, and does not claim to, recover
the semantics of the microcode's functions.

Exit status: 0 if no error-class diagnostic was raised, 1 otherwise.
"""

import argparse
import collections
import hashlib
import json
import math
import struct
import sys

PROBE_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Constants quoted from public GPL sources (access date 2026-11-18)
# ---------------------------------------------------------------------------

# drivers/gpu/drm/msm/adreno/a6xx_gmu.c:857-863 (master) -- the ONLY firmware
# container struct mainline documents.  16-byte header + `size` payload bytes.
#
#     struct block_header {
#             u32 addr;
#             u32 size;
#             u32 type;
#             u32 value;
#             u32 data[];
#     };
BLOCK_HEADER = struct.Struct("<IIII")
BLOCK_HEADER_SIZE = BLOCK_HEADER.size              # 16

# a6xx_gmu.c:893-897 -- the legacy load path rejects anything larger than
# 0x8000 and writes it verbatim to ITCM_START.  (0x8000 == 2 * SZ_16K.)
LEGACY_FW_MAX = 0x8000

# a6xx_gmu.c:886-887 -- the GMU's two TCM windows as the driver models them.
ITCM_BASE = 0x00000000
DTCM_BASE = 0x00040000
TCM_SIZE = 0x4000                                  # SZ_16K each

# a6xx_gmu.xml:45-46 -- GMU_CM3_ITCM_START / GMU_CM3_DTCM_START are 0x1000
# dwords apart == 0x4000 bytes == exactly SZ_16K.  This is what makes a flat
# 32 KiB image a *contiguous* ITCM+DTCM memory dump.
ITCM_START_REG = 0x1b400
DTCM_START_REG = 0x1c400

# a6xx_gmu.xml:55-58 -- GMU_CORE_FW_VERSION bitfields (the value the driver
# prints as "Loaded GMU firmware vMAJOR.MINOR.STEP").  It is a REGISTER read
# at runtime, not a field in the file.
FW_VERSION_REG = 0x1d3f8

# a6xx_gmu.c:311 -- the driver probes DTCM_START + 0xff8 while deciding which
# FW-init handshake the microcode speaks.
DTCM_PROBE_OFF = 0xff8

# a6xx_gmu.c:313-318 -- legacy parts must land 0xbabeface in
# REG_A6XX_GMU_CM3_FW_INIT_RESULT; newer parts must land 0x100 with mask 0x1ff.
FW_INIT_MAGIC = 0xBABEFACE

# Marker words that padding/terminator records use in the container family
# (measured: present in a623/a640/a650/a660/a663, absent in a619/a630).
MARKERS = (0xEFBEADDE, 0xDEADBEEF)

# ARMv7-M architectural anchor: SCB->VTOR.
VTOR_ADDR = 0xE000ED08

# ---------------------------------------------------------------------------
# ARMv7-M / Thumb-2 encodings used by the census.
#
# These are the shortest, least ambiguous 16-bit encodings from the ARMv7-M
# ARM (ARM DDI 0403) -- chosen so that a *count* is meaningful without a
# disassembler.  Each predicate is an exact bit-mask test on a halfword, not
# a guess: e.g. "ldr Rt,[pc,#imm8]" is `0100 1` + Rt in bits 10:8, i.e.
# (hw & 0xF800) == 0x4800.
# ---------------------------------------------------------------------------
THUMB16_CENSUS = (
    ("nop",                   lambda h: h == 0xBF00),
    ("b . (infinite loop)",   lambda h: h == 0xE7FE),
    ("bx lr",                 lambda h: h == 0x4770),
    ("ldr Rt,[pc,#imm8]",     lambda h: (h & 0xF800) == 0x4800),
    ("push {...,lr}",         lambda h: (h & 0xFF00) == 0xB500),
    ("pop {...,pc}",          lambda h: (h & 0xFF00) == 0xBD00),
    ("movs Rd,#imm8",         lambda h: (h & 0xF800) == 0x2000),
    ("cmp Rn,#imm8",          lambda h: (h & 0xF800) == 0x2800),
    ("adds Rd,#imm8",         lambda h: (h & 0xF800) == 0x3000),
    ("subs Rd,#imm8",         lambda h: (h & 0xF800) == 0x3800),
    ("mov Rd,Rm",             lambda h: (h & 0xFFC0) == 0x4600),
    ("add Rd,Rm",             lambda h: (h & 0xFFC0) == 0x4400),
    ("str Rt,[Rn,#imm5]",     lambda h: (h & 0xF800) == 0x6000),
    ("ldr Rt,[Rn,#imm5]",     lambda h: (h & 0xF800) == 0x6800),
    ("strb Rt,[Rn,#imm5]",    lambda h: (h & 0xF800) == 0x7000),
    ("ldrb Rt,[Rn,#imm5]",    lambda h: (h & 0xF800) == 0x7800),
    ("strh Rt,[Rn,#imm5]",    lambda h: (h & 0xF800) == 0x8000),
    ("ldrh Rt,[Rn,#imm5]",    lambda h: (h & 0xF800) == 0x8800),
    ("str Rt,[sp,#imm8]",     lambda h: (h & 0xFF00) == 0x9000),
    ("ldr Rt,[sp,#imm8]",     lambda h: (h & 0xFF00) == 0x9800),
    ("add Rd,pc,#imm8",       lambda h: (h & 0xF800) == 0xA000),
    ("add Rd,sp,#imm8",       lambda h: (h & 0xF800) == 0xA800),
    ("stm/ldm",               lambda h: (h & 0xF000) == 0xC000),
    ("b<cond>",               lambda h: (h & 0xF000) == 0xD000),
    ("svc",                   lambda h: (h & 0xFF00) == 0xDF00),
    ("b (uncond, 16-bit)",    lambda h: (h & 0xF800) == 0xE000),
    ("bl / blx prefix",       lambda h: (h & 0xF800) in (0xF000, 0xF800)),
)

# ARMv7-M exception names, vector-table order (ARM DDI 0403, table "Vector
# table").  Used to label the 16 architectural entries.
VECTOR_NAMES = (
    "Initial SP", "Reset", "NMI", "HardFault", "MemManage", "BusFault",
    "UsageFault", "Reserved", "Reserved", "Reserved", "Reserved", "SVCall",
    "DebugMonitor", "Reserved", "PendSV", "SysTick",
)

DEFAULT_STRING_MIN = 4


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

class Diagnostics:
    """Ordered diagnostic sink.  `error` sets the process exit status."""

    def __init__(self):
        self.items = []

    def add(self, level, code, message, **extra):
        rec = {"level": level, "code": code, "message": message}
        rec.update(extra)
        self.items.append(rec)
        return rec

    def info(self, code, message, **extra):
        return self.add("info", code, message, **extra)

    def warn(self, code, message, **extra):
        return self.add("warning", code, message, **extra)

    def error(self, code, message, **extra):
        return self.add("error", code, message, **extra)

    @property
    def has_errors(self):
        return any(d["level"] == "error" for d in self.items)

    def counts(self):
        c = collections.Counter(d["level"] for d in self.items)
        return {k: c.get(k, 0) for k in ("error", "warning", "info")}


# ---------------------------------------------------------------------------
# Measurement helpers
# ---------------------------------------------------------------------------

def shannon_entropy(data):
    """Bits per byte.  Measured, not modelled."""
    if not data:
        return 0.0
    counts = collections.Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def entropy_profile(data, block=512):
    """Whole-block Shannon entropy.  Deliberately coarse: 512 B is large
    enough that a code block reads ~6 bits and an all-zero block reads 0,
    which is all the separation needed to draw a code/data map."""
    out = []
    for off in range(0, len(data), block):
        chunk = data[off:off + block]
        out.append({
            "offset": off,
            "length": len(chunk),
            "entropy": round(shannon_entropy(chunk), 4),
            "zero_fraction": round(chunk.count(0) / len(chunk), 4) if chunk else 0.0,
        })
    return out


def zero_regions(data, min_len=16):
    """Maximal all-zero runs at byte granularity -- the filler map."""
    out = []
    i, n = 0, len(data)
    while i < n:
        if data[i] == 0:
            j = i
            while j < n and data[j] == 0:
                j += 1
            if j - i >= min_len:
                out.append({"offset": i, "length": j - i})
            i = j
        else:
            i += 1
    return out


def extract_strings(data, min_len=DEFAULT_STRING_MIN):
    """Printable ASCII and UTF-16LE runs, with file offsets."""
    found = []

    start = None
    for i, b in enumerate(data):
        printable = 0x20 <= b <= 0x7E
        if printable and start is None:
            start = i
        elif not printable and start is not None:
            if i - start >= min_len:
                found.append({
                    "offset": start,
                    "encoding": "ascii",
                    "length": i - start,
                    "text": data[start:i].decode("ascii", "replace"),
                })
            start = None
    if start is not None and len(data) - start >= min_len:
        found.append({
            "offset": start, "encoding": "ascii",
            "length": len(data) - start,
            "text": data[start:].decode("ascii", "replace"),
        })

    # UTF-16LE: printable ASCII byte followed by NUL, >= min_len chars.
    i = 0
    n = len(data)
    while i + 2 <= n:
        if 0x20 <= data[i] <= 0x7E and data[i + 1] == 0:
            j = i
            chars = []
            while j + 2 <= n and 0x20 <= data[j] <= 0x7E and data[j + 1] == 0:
                chars.append(chr(data[j]))
                j += 2
            if len(chars) >= min_len:
                found.append({
                    "offset": i, "encoding": "utf-16-le",
                    "length": len(chars), "text": "".join(chars),
                })
            i = j
        else:
            i += 1

    found.sort(key=lambda s: (s["offset"], s["encoding"]))
    return found


def thumb_census(data, start, end):
    """Count the well-known 16-bit Thumb encodings in [start, end).

    Halfword-aligned scan over a 2-byte stride.  This is a census, not a
    disassembly: overlapping 32-bit instructions and data literals are
    counted as whatever their low halfword happens to look like, so use
    the rates comparatively, not as an exact instruction mix.
    """
    start -= start % 2
    end = min(end, len(data))
    if end <= start:
        return {"start": start, "end": end, "halfwords": 0, "counts": {}}
    halfwords = [struct.unpack_from("<H", data, o)[0]
                 for o in range(start, end - 1, 2)]
    counts = {}
    for name, pred in THUMB16_CENSUS:
        counts[name] = sum(1 for h in halfwords if pred(h))
    total = len(halfwords)
    return {
        "start": start,
        "end": end,
        "halfwords": total,
        "counts": counts,
        "rates": {k: round(v / total, 4) for k, v in counts.items()},
    }


# ---------------------------------------------------------------------------
# Format 1: mainline `struct block_header` container (a6xx_gmu.c:857-863)
# ---------------------------------------------------------------------------

def walk_block_headers(data, start=0, max_blocks=4096):
    """Walk mainline's block_header chain.

    Mirrors a6xx_gmu.c:906-908 and its NEXT_BLK macro (a6xx_gmu.c:869-871):
    the next record begins at ``current + 16 + size``.  A ``size == 0``
    record still advances one header (the driver's `continue`), which is
    how the container family stores metadata-only entries.
    """
    blocks = []
    off = start
    n = len(data)

    while off + BLOCK_HEADER_SIZE <= n:
        if len(blocks) >= max_blocks:
            return blocks, {"status": "block-limit", "offset": off}
        addr, size, typ, value = BLOCK_HEADER.unpack_from(data, off)
        nxt = off + BLOCK_HEADER_SIZE + size
        if nxt > n:
            return blocks, {
                "status": "overflow", "offset": off,
                "declared_next": nxt, "file_size": n,
                "detail": "record at 0x%x declares %d payload bytes past EOF"
                          % (off, nxt - n),
            }
        blocks.append({
            "offset": off, "addr": addr, "size": size,
            "type": typ, "value": value, "next": nxt,
        })
        off = nxt

    if off == n:
        status = "exact-eof"
    else:
        status = "short"
    return blocks, {"status": status, "offset": off}


def describe_block_region(addr, size):
    """Map a block's load address onto the GMU windows the driver names."""
    if addr < ITCM_BASE + TCM_SIZE:
        return "ITCM"
    if DTCM_BASE <= addr < DTCM_BASE + TCM_SIZE:
        return "DTCM"
    return "outside-TCM"


def analyze_block_container(data, diag):
    """Mainline container branch.  Returns a findings dict or None if the
    byte stream is not a plausible block_header chain."""
    blocks, term = walk_block_headers(data)

    payload_blocks = [b for b in blocks if b["size"] > 0]
    # A believable container needs at least one real payload block and must
    # consume the file exactly (mainline's loop condition is `blk < end`).
    if term["status"] != "exact-eof" or not payload_blocks:
        return None, blocks, term

    # Reject a chain that only "fits" because sizes happen to be tiny/garbage:
    # every payload block must land in a window the driver actually writes to,
    # or be one of its BO regions.  Mainline only warns on a mismatch, so we
    # warn too -- but a chain where *nothing* lands in TCM is not evidence.
    for b in payload_blocks:
        b["region"] = describe_block_region(b["addr"], b["size"])
    in_tcm = [b for b in payload_blocks if b["region"] in ("ITCM", "DTCM")]
    if not in_tcm:
        return None, blocks, term

    diag.info("block-container",
              "mainline struct block_header chain fits the file exactly "
              "(%d records, %d with payload)"
              % (len(blocks), len(payload_blocks)))

    # Leading metadata table: a run of size==0 records before the first
    # payload block, terminated by a marker entry.  Observed on a623/a640/
    # a650/a660/a663 (measured).  Semantics [OPEN].
    lead = []
    for b in blocks:
        if b["size"] != 0:
            break
        lead.append(b)
    descriptor_table = None
    if lead:
        entries = []
        for b in lead:
            if b["type"] in MARKERS:
                break
            entries.append({
                "offset": b["offset"], "name_or_addr": b["addr"],
                "value": b["value"], "size": b["size"],
                "type": b["type"],
            })
        if entries:
            descriptor_table = {
                "offset": entries[0]["offset"],
                "entry_count": len(entries),
                "stride": 16,
                "entries": entries,
                "note": ("size==0 records carrying {addr, value}; the first "
                         "record of each entry is a TCM/window base address "
                         "and the second a length or elaboration [OPEN]"),
            }
            diag.info("descriptor-table",
                      "%d zero-size descriptor records at 0x%x before the "
                      "first payload block (semantics [OPEN])"
                      % (len(entries), entries[0]["offset"]))

    return {
        "format": "mainline-block-container",
        "confidence": "measured-and-cross-checked",
        "header_present": True,
        "header_struct": "struct block_header (a6xx_gmu.c:857-863)",
        "block_count": len(blocks),
        "payload_block_count": len(payload_blocks),
        "blocks": blocks,
        "descriptor_table": descriptor_table,
        "walk_termination": term,
        "regions": _region_summary(payload_blocks),
    }, blocks, term


def _region_summary(blocks):
    out = collections.OrderedDict()
    for b in blocks:
        if b.get("size", 0) == 0:
            continue
        r = b.get("region", describe_block_region(b["addr"], b["size"]))
        e = out.setdefault(r, {"blocks": 0, "bytes": 0, "min_addr": b["addr"],
                               "max_addr": b["addr"] + b["size"]})
        e["blocks"] += 1
        e["bytes"] += b["size"]
        e["min_addr"] = min(e["min_addr"], b["addr"])
        e["max_addr"] = max(e["max_addr"], b["addr"] + b["size"])
    for e in out.values():
        e["min_addr"] = "0x%08x" % e["min_addr"]
        e["max_addr"] = "0x%08x" % e["max_addr"]
    return out


# ---------------------------------------------------------------------------
# Format 2: raw ITCM+DTCM memory image (the driver's `gmu->legacy` path)
# ---------------------------------------------------------------------------

def detect_startup_stub(data):
    """Recognise the ARMv7-M reset stub measured at file offset 0x08.

    Measured byte-for-byte on a619_gmu.bin (md5 9e23c520...) and
    a630_gmu.bin (md5 ab20135f...), which share this 32-byte prologue
    identically.  Encodings, from the ARMv7-M ARM:

        0x08  48xx        ldr  r0, [pc, #imm8]      ; literal (initial SP)
        0x0a  f380 88xx   msr  msp, r0              (32-bit Thumb-2)
        0x0e  48xx        ldr  r0, [pc, #imm8]      ; literal (PSP)
        0x10  f380 88xx   msr  psp, r0
        0x14  48xx        ldr  r0, [pc, #imm8]      ; literal (0x200)
        0x16  49xx        ldr  r1, [pc, #imm8]      ; literal (0xE000ED08)
        0x18  6008        str  r0, [r1, #0]         ; *VTOR = 0x200
        0x1a  f000 b9f1   b.w  0x400
        0x1e  bf00        nop

    Returns a dict describing what was found, or None.
    """
    if len(data) < 0x30:
        return None
    hw = lambda o: struct.unpack_from("<H", data, o)[0]
    w = lambda o: struct.unpack_from("<I", data, o)[0]

    if (hw(0x08) & 0xF800) != 0x4800:
        return None
    if hw(0x0A) != 0xF380 or (hw(0x0C) & 0xFF00) != 0x8800:
        return None
    if (hw(0x0E) & 0xF800) != 0x4800:
        return None
    if hw(0x10) != 0xF380 or (hw(0x12) & 0xFF00) != 0x8800:
        return None
    if (hw(0x14) & 0xF800) != 0x4800:
        return None
    # NB: `ldr Rt,[pc,#imm8]` is 0x48xx for Rt 0-7 and 0x49xx for Rt 8-15 --
    # bit 8 belongs to Rt, so the register-exact test needs mask 0xFF00.
    if (hw(0x16) & 0xFF00) != 0x4900:
        return None
    if hw(0x18) != 0x6008:
        return None

    def ldr_literal(insn_off):
        """Effective address of a 16-bit `ldr rX,[pc,#imm8]`: align(PC,4)+imm*4."""
        insn = hw(insn_off)
        imm = (insn & 0xFF) * 4
        ea = ((insn_off + 4) & ~3) + imm
        return ea, (w(ea) if ea + 4 <= len(data) else None)

    sp_addr, sp_val = ldr_literal(0x08)
    psp_addr, psp_val = ldr_literal(0x0E)
    vtor_src, vtor_target = ldr_literal(0x14)
    vtor_reg_addr, vtor_reg = ldr_literal(0x16)

    return {
        "stub_offset": 0x08,
        "stub_length": 0x18,
        "initial_sp_literal_offset": sp_addr,
        "initial_sp": sp_val,
        "psp_literal_offset": psp_addr,
        "psp": psp_val,
        "vtor_value_literal_offset": vtor_src,
        "vtor_value": vtor_target,
        "vtor_reg_literal_offset": vtor_reg_addr,
        "vtor_reg": vtor_reg,
        "vtor_reg_is_scb_vtor": vtor_reg == VTOR_ADDR,
        "comments": [
            "u32[0] of the image is the ARMv7-M initial stack pointer, "
            "loaded here into MSP -- not a magic and not a length",
            "u32[1] is the Reset vector, loaded by the core's reset "
            "sequence (not by this stub)",
            "the stub points SCB->VTOR at the vector table inside the image",
        ],
    }


def read_vector_table(data, offset, count=16):
    """Read the 16 architecturally-defined ARMv7-M vectors at `offset`."""
    if offset < 0 or offset + 4 * count > len(data):
        return None
    words = list(struct.unpack_from("<%dI" % count, data, offset))
    entries = []
    for i, v in enumerate(words):
        entries.append({
            "index": i,
            "name": VECTOR_NAMES[i],
            "value": v,
            "thumb": bool(v & 1) if i else None,
        })
    return {"offset": offset, "entries": entries, "words": words}


def analyze_raw_tcm(data, diag):
    """Raw ITCM+DTCM branch -- the driver's legacy load path.

    Layout established by measurement (gmu-analysis.md):
        [0x0000, 0x4000)  ITCM image, mapped at 0x00000000
        [0x4000, 0x8000)  DTCM image, mapped at 0x00040000
    The split at 0x4000 is forced by the register map: GMU_CM3_ITCM_START
    and GMU_CM3_DTCM_START are exactly SZ_16K apart (a6xx_gmu.xml:45-46).
    """
    n = len(data)
    if n < 0x400:
        return None

    stub = detect_startup_stub(data)
    if stub is None:
        return None

    sp = stub["initial_sp"]
    reset = struct.unpack_from("<I", data, 4)[0]

    findings = {
        "format": "raw-tcm-image",
        "confidence": "measured-and-cross-checked",
        "header_present": False,
        "header_struct": None,
        "header_verdict": (
            "no container header of any kind: the file is a flat memory "
            "image whose first word is the ARMv7-M initial stack pointer"),
        "startup_stub": stub,
        "initial_sp": sp,
        "reset_vector": reset,
        "itcm": {"file_offset": 0x0000, "load_addr": ITCM_BASE,
                 "size": min(TCM_SIZE, n)},
        "dtcm": {"file_offset": TCM_SIZE, "load_addr": DTCM_BASE,
                 "size": max(0, min(TCM_SIZE, n - TCM_SIZE))},
        "load_path": {
            "kernel": "a6xx_gmu.c:894-904 (gmu->legacy branch)",
            "mechanism": ("gmu_write_bulk(REG_A6XX_GMU_CM3_ITCM_START, "
                          "fw->data, fw->size) -- the file is DMA'd verbatim "
                          "into TCM, no parsing"),
            "size_cap": LEGACY_FW_MAX,
        },
    }

    # --- structural checks -------------------------------------------------
    if n != LEGACY_FW_MAX:
        diag.error("legacy-size",
                   "raw TCM image is %d bytes, expected exactly 0x%x "
                   "(ITCM 0x4000 + DTCM 0x4000) -- the legacy loader's cap"
                   % (n, LEGACY_FW_MAX), size=n)
    else:
        diag.info("legacy-size",
                  "%d bytes == 0x%x == ITCM(0x4000) + DTCM(0x4000), exactly "
                  "the legacy loader's size cap (a6xx_gmu.c:896)"
                  % (n, n))

    # SP must be a plausible DTCM stack top.
    sp_ok = DTCM_BASE <= sp <= DTCM_BASE + TCM_SIZE
    findings["initial_sp_in_dtcm"] = sp_ok
    if not sp_ok:
        diag.error("bad-sp",
                   "initial SP 0x%08x is outside the DTCM window "
                   "[0x%08x, 0x%08x)" % (sp, DTCM_BASE, DTCM_BASE + TCM_SIZE))
    elif sp % 4:
        diag.error("misaligned-sp",
                   "initial SP 0x%08x is not 4-byte aligned" % sp)
    else:
        # ARM's vector-table convention leaves a small reserved slot above
        # the stack top; the measured value is exactly top-0x80.
        top = DTCM_BASE + TCM_SIZE
        findings["sp_offset_from_dtcm_top"] = top - sp
        if top - sp == 0x80:
            diag.info("sp-at-conventional-slot",
                      "initial SP 0x%08x == DTCM top 0x%08x - 0x80, the "
                      "conventional reserved slot below the vector table"
                      % (sp, top))

    # Reset vector must be an odd (Thumb) address inside ITCM.
    if not (reset & 1):
        diag.error("reset-not-thumb",
                   "reset vector 0x%08x has the Thumb bit clear" % reset)
    elif not (ITCM_BASE <= (reset & ~1) < ITCM_BASE + TCM_SIZE):
        diag.error("reset-out-of-itcm",
                   "reset vector 0x%08x is outside the ITCM window"
                   % reset)
    else:
        diag.info("reset-vector",
                  "reset vector 0x%08x -> ITCM+0x%x (Thumb)"
                  % (reset, reset & ~1))

    # The stub writes VTOR; the table it points at must be inside the image
    # and must begin with the same SP the stub loaded.  This is a strong
    # self-consistency check that costs nothing to run.
    vtor = stub.get("vtor_value")
    if stub.get("vtor_reg_is_scb_vtor"):
        diag.info("vtor-anchor",
                  "startup stub writes 0x%08x (SCB->VTOR) = 0x%x"
                  % (VTOR_ADDR, vtor or 0))
    else:
        diag.warn("vtor-anchor",
                  "startup stub writes a literal 0x%08x, not SCB->VTOR "
                  "(0x%08x)" % (stub.get("vtor_reg") or 0, VTOR_ADDR))

    vt = None
    if vtor is not None and 0 < vtor < n:
        vt = read_vector_table(data, vtor)
        if vt is None:
            diag.error("vtor-out-of-range",
                       "VTOR target 0x%x is not a readable in-image table"
                       % vtor)
        else:
            findings["vector_table"] = vt
            if vt["words"][0] != sp:
                diag.error("vtor-sp-mismatch",
                           "vector table at 0x%x starts with 0x%08x but the "
                           "stub loaded SP=0x%08x -- not a Cortex-M vector "
                           "table" % (vtor, vt["words"][0], sp))
            else:
                diag.info("vector-table",
                          "vector table at 0x%x begins with the same SP "
                          "(0x%08x) the stub loaded -- Cortex-M reset-table "
                          "anchor confirmed" % (vtor, sp))
            # Enumerate the external-interrupt tail: everything after the
            # 16 architectural vectors that is non-zero and still inside the
            # ITCM half is an IRQ handler address.
            irq = _irq_table(data, vtor + 4 * 16, ITCM_BASE + TCM_SIZE)
            if irq:
                findings["irq_table"] = irq
                diag.info("irq-table",
                          "%d external interrupt vectors, %d distinct Thumb "
                          "targets" % (irq["count"], len(irq["distinct_targets"])))

    # --- DTCM header word pair (measured, semantics [OPEN]) -----------------
    if n >= TCM_SIZE + 8:
        a, b = struct.unpack_from("<HH", data, TCM_SIZE + 2)
        findings["dtcm_header_halfwords"] = {
            "offset": TCM_SIZE + 2,
            "word0": a, "word1": b,
            "note": ("two 16-bit values at DTCM+0x02; a619 carries "
                     "0x1011/0x3d79, a630 carries 0x1006/0x3d61. The first "
                     "differs between builds and is plausibly a build id; "
                     "neither has a name in public sources [OPEN]"),
        }

    # --- descriptor/region table at the end of ITCM -------------------------
    desc = _find_region_descriptor_table(data, diag)
    if desc:
        findings["region_descriptor_table"] = desc

    # --- DTCM address-pair table -------------------------------------------
    pairs = _find_dtcm_pairs(data, TCM_SIZE)
    if pairs:
        findings["dtcm_address_pairs"] = pairs

    # --- firmware-init handshake corroboration -----------------------------
    probe_off = TCM_SIZE + DTCM_PROBE_OFF
    if probe_off + 4 <= n:
        val = struct.unpack_from("<I", data, probe_off)[0]
        findings["dtcm_probe_0xff8"] = val
        diag.info("dtcm-probe",
                  "DTCM+0x%x (the word a6xx_gmu.c:311 reads to pick the "
                  "init handshake) is 0x%08x -> driver branch: %s"
                  % (DTCM_PROBE_OFF, val,
                     "legacy 0x%08x" % FW_INIT_MAGIC
                     if val <= 0x20010004 else "0x100 with mask 0x1ff"))

    hits = []
    pos = data.find(struct.pack("<I", FW_INIT_MAGIC))
    while pos >= 0:
        hits.append(pos)
        pos = data.find(struct.pack("<I", FW_INIT_MAGIC), pos + 1)
    if hits:
        findings["fw_init_magic_sites"] = hits
        diag.info("fw-init-magic",
                  "0x%08x occurs %d time(s) in the code at %s -- the value "
                  "the driver polls for after reset (a6xx_gmu.c:313-318)"
                  % (FW_INIT_MAGIC, len(hits),
                     ", ".join("0x%x" % h for h in hits)))

    # --- marker absence is itself the discriminator -------------------------
    marker_free = not any(data.find(struct.pack("<I", m)) >= 0 for m in MARKERS)
    findings["container_markers_present"] = not marker_free
    if marker_free:
        diag.info("no-container-markers",
                  "none of the container marker words %s occur -- consistent "
                  "with a raw image, not a block_header chain"
                  % ", ".join("0x%08x" % m for m in MARKERS))

    return findings


def _irq_table(data, start, limit):
    """Walk non-zero words from `start` while they are in-image Thumb
    addresses, i.e. the external-interrupt tail of a Cortex-M vector table."""
    words = []
    off = start
    while off + 4 <= min(limit, len(data)):
        v = struct.unpack_from("<I", data, off)[0]
        if v == 0:
            break
        if not (v & 1) or (v & ~1) >= len(data):
            break
        words.append({"offset": off, "index": (off - start) // 4, "value": v})
        off += 4
    if not words:
        return None
    targets = sorted({w["value"] for w in words})
    return {
        "offset": start,
        "count": len(words),
        "first_index": 0,
        "distinct_targets": ["0x%08x" % t for t in targets],
        "note": ("all interrupt vectors collapsing onto a single handler is "
                 "the measured norm for this image; the handler body is not "
                 "interpreted here"),
    }


def _find_region_descriptor_table(data, diag):
    """Find the {start,end} address-pair table that sits at the end of ITCM.

    Measured on a619: 8 ascending address pairs at ITCM+0x3ea4, alternating
    between the DTCM window (0x00040xxx) and ITCM (0x00000xxx), followed by
    zero padding to the 0x4000 boundary.  Semantics [OPEN].
    """
    # Scan backwards from the ITCM boundary for the start of the last
    # non-zero run in the ITCM half.
    end = min(TCM_SIZE, len(data))
    last = None
    for o in range(0, end - 3, 4):
        if struct.unpack_from("<I", data, o)[0]:
            last = o
    if last is None:
        return None
    table_end = last + 4
    # Walk back in 4-byte steps while words look like TCM addresses.
    def looks(v):
        return (ITCM_BASE <= v < ITCM_BASE + TCM_SIZE) or \
               (DTCM_BASE <= v < DTCM_BASE + TCM_SIZE)
    start = table_end
    while start - 4 >= 0 and looks(struct.unpack_from("<I", data, start - 4)[0]):
        start -= 4
    if table_end - start < 32:
        return None
    words = list(struct.unpack_from("<%dI" % ((table_end - start) // 4),
                                    data, start))
    pairs = [(words[i], words[i + 1]) for i in range(0, len(words) - 1, 2)]
    ascending = all(a < b for a, b in pairs)
    kinds = []
    for a, b in pairs:
        if DTCM_BASE <= a < DTCM_BASE + TCM_SIZE:
            kinds.append("DTCM")
        elif ITCM_BASE <= a < ITCM_BASE + TCM_SIZE:
            kinds.append("ITCM")
        else:
            kinds.append("other")
    alternating = all(kinds[i] != kinds[i + 1] for i in range(len(kinds) - 1))
    diag.info("region-descriptor-table",
              "%d {start,end} address pairs at 0x%x-0x%x (ascending=%s, "
              "alternating TCM/ITCM=%s); semantics [OPEN]"
              % (len(pairs), start, table_end, ascending, alternating))
    return {
        "offset": start,
        "length": table_end - start,
        "pair_count": len(pairs),
        "pairs": [{"start": "0x%08x" % a, "end": "0x%08x" % b,
                   "region": k} for (a, b), k in zip(pairs, kinds)],
        "all_ascending": ascending,
        "alternating_regions": alternating,
        "note": "region descriptor table; semantics [OPEN]",
    }


def _find_dtcm_pairs(data, dtcm_file_off):
    """Find the stride-8 {addr,value} table in the DTCM half (measured)."""
    n = len(data)
    best = None
    o = dtcm_file_off
    run_start = None
    run = 0
    while o + 8 <= n:
        a, v = struct.unpack_from("<II", data, o)
        plausible = 0x44000000 <= a < 0x44040000
        if plausible:
            if run_start is None:
                run_start = o
            run += 1
        else:
            if run >= 4 and (best is None or run > best[1]):
                best = (run_start, run)
            run_start, run = None, 0
        o += 8
    if run >= 4 and (best is None or run > best[1]):
        best = (run_start, run)
    if best is None:
        return None
    start, count = best
    entries = [struct.unpack_from("<II", data, start + 8 * i) for i in range(count)]
    return {
        "offset": start,
        "count": count,
        "stride": 8,
        "distinct_addresses": len({e[0] for e in entries}),
        "address_min": "0x%08x" % min(e[0] for e in entries),
        "address_max": "0x%08x" % max(e[0] for e in entries),
        "all_values_zero": all(e[1] == 0 for e in entries),
        "note": ("stride-8 {address, value} table in DTCM; addresses sit in "
                 "the 0x44000000 range the microcode's own code uses as a "
                 "peripheral/register window. Semantics [OPEN]"),
    }


# ---------------------------------------------------------------------------
# Top-level analysis
# ---------------------------------------------------------------------------

def analyze(data, string_min=DEFAULT_STRING_MIN, entropy_block=512,
            thumb_region=None):
    """Full structural analysis.  Returns (report_dict, Diagnostics)."""
    diag = Diagnostics()
    n = len(data)

    report = {
        "tool": "gmu_probe.py",
        "tool_version": PROBE_VERSION,
        "size": n,
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "entropy": {
            "whole": round(shannon_entropy(data), 4),
            "block_size": entropy_block,
            "profile": entropy_profile(data, entropy_block),
        },
        "zero_byte_fraction": round(data.count(0) / n, 4) if n else 0.0,
        "zero_regions": zero_regions(data),
        "strings": extract_strings(data, string_min),
        "diagnostics": diag,
    }

    if n == 0:
        diag.error("empty", "input file is empty")
        report["format"] = "unknown"
        report["diagnostics"] = diag.items
        report["diagnostic_counts"] = diag.counts()
        return report, diag

    # ---- RULE 0 order: try the documented mainline container first --------
    container, blocks, term = analyze_block_container(data, diag)
    report["mainline_block_walk"] = {
        "attempted": True,
        "fits": container is not None,
        "termination": term,
        "records_seen": len(blocks),
        "first_records": blocks[:6],
    }

    if container is not None:
        report.update(container)
    else:
        diag.info("block-container-rejected",
                  "mainline struct block_header chain does not describe this "
                  "file (%s after %d record(s)); falling back to the raw "
                  "TCM-image model" % (term.get("status"), len(blocks)))
        raw = analyze_raw_tcm(data, diag)
        if raw is not None:
            report.update(raw)
        else:
            diag.error("unrecognised-layout",
                       "neither the mainline block_header chain nor the raw "
                       "ITCM+DTCM image model explains these bytes")
            report["format"] = "unknown"
            report["confidence"] = "unrecognised"

    # ---- entropy map over the whole file ---------------------------------
    report["region_entropy"] = _region_entropy(report, data)

    # ---- Thumb census ----------------------------------------------------
    if thumb_region:
        lo, hi = thumb_region
    elif report.get("format") == "raw-tcm-image":
        vt = report.get("vector_table")
        lo = vt["offset"] + 4 * 16 if vt else 0x100
        # stop before the trailing descriptor/zero padding
        hi = TCM_SIZE
        for o in range(TCM_SIZE - 4, 0, -4):
            if struct.unpack_from("<I", data, o)[0]:
                hi = o + 4
                break
    else:
        lo, hi = 0, n
    report["thumb_census"] = thumb_census(data, lo, hi)

    report["diagnostics"] = diag.items
    report["diagnostic_counts"] = diag.counts()
    return report, diag


def _region_entropy(report, data):
    """Per-region entropy for whatever layout was identified."""
    out = collections.OrderedDict()
    fmt = report.get("format")

    def add(name, lo, hi):
        lo = max(0, lo)
        hi = min(len(data), hi)
        if hi <= lo:
            return
        chunk = data[lo:hi]
        out[name] = {
            "file_offset": lo, "length": hi - lo,
            "entropy": round(shannon_entropy(chunk), 4),
            "zero_fraction": round(chunk.count(0) / len(chunk), 4),
        }

    if fmt == "raw-tcm-image":
        add("itcm", 0, TCM_SIZE)
        add("dtcm", TCM_SIZE, 2 * TCM_SIZE)
        vt = report.get("vector_table")
        if vt:
            add("vector_table", vt["offset"], vt["offset"] + 4 * 80)
        stub = report.get("startup_stub")
        if stub:
            add("startup_stub", 0, stub["stub_offset"] + stub["stub_length"])
    elif fmt == "mainline-block-container":
        for b in report.get("blocks", []):
            if b.get("size", 0) == 0:
                continue
            add("block@0x%x(%s)" % (b["offset"], b.get("region", "?")),
                b["offset"] + BLOCK_HEADER_SIZE, b["next"])
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _json_ready(obj):
    if isinstance(obj, dict):
        return {k: _json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_ready(v) for v in obj]
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    return obj


def print_brief(report, stream=sys.stdout):
    w = stream.write
    w("file      : %d bytes  md5 %s\n" % (report["size"], report["md5"]))
    fmt = report.get("format", "unknown")
    w("format    : %s  [%s]\n" % (fmt, report.get("confidence", "-")))
    w("header    : %s\n" % ("present" if report.get("header_present") else
                            "ABSENT -- " + report.get("header_verdict", "")))
    if report.get("header_struct"):
        w("            %s\n" % report["header_struct"])

    if fmt == "raw-tcm-image":
        stub = report.get("startup_stub") or {}
        w("initial SP: 0x%08x (DTCM=%s)\n"
          % (report.get("initial_sp", 0),
             report.get("initial_sp_in_dtcm")))
        w("reset vec : 0x%08x\n" % report.get("reset_vector", 0))
        vt = report.get("vector_table")
        if vt:
            w("vector tbl: 0x%x, %d architectural vectors\n"
              % (vt["offset"], len(vt["entries"])))
        pairs = report.get("dtcm_address_pairs")
        if pairs:
            w("dtcm table: %d x {addr,value} at 0x%x (vals all zero=%s)\n"
              % (pairs["count"], pairs["offset"], pairs["all_values_zero"]))
        desc = report.get("region_descriptor_table")
        if desc:
            w("region tbl: %d {start,end} pairs at 0x%x\n"
              % (desc["pair_count"], desc["offset"]))
    elif fmt == "mainline-block-container":
        w("blocks    : %d (%d with payload)\n"
          % (report.get("block_count", 0), report.get("payload_block_count", 0)))
        desc = report.get("descriptor_table")
        if desc:
            w("descriptor: %d records at 0x%x\n"
              % (desc["entry_count"], desc["offset"]))

    ent = report["entropy"]
    w("entropy   : whole %.2f bits/byte\n" % ent["whole"])
    for name, r in report.get("region_entropy", {}).items():
        w("            %-22s 0x%05x-0x%05x  %5d B  H=%.2f  zero=%.0f%%\n"
          % (name, r["file_offset"], r["file_offset"] + r["length"],
             r["length"], r["entropy"], 100 * r["zero_fraction"]))

    strings = report.get("strings", [])
    w("strings   : %d printable run(s)\n" % len(strings))
    for s in strings[:10]:
        w("            0x%05x  %-9s %r\n" % (s["offset"], s["encoding"], s["text"]))
    if len(strings) > 10:
        w("            ... %d more\n" % (len(strings) - 10))

    tc = report.get("thumb_census", {})
    if tc.get("halfwords"):
        top = sorted(tc["counts"].items(), key=lambda kv: -kv[1])[:6]
        w("thumb     : %d halfwords in 0x%x-0x%x; top: %s\n"
          % (tc["halfwords"], tc["start"], tc["end"],
             ", ".join("%s %d (%.1f%%)" % (k, v, 100 * tc["rates"][k])
                       for k, v in top)))

    counts = report["diagnostic_counts"]
    w("diagnostics: %d error, %d warning, %d info\n"
      % (counts["error"], counts["warning"], counts["info"]))
    for d in report["diagnostics"]:
        w("  [%s] %-24s %s\n" % (d["level"], d["code"], d["message"]))


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Clean-room structural probe for Adreno GMU microcode "
                    "(mainline block_header check first, then the established "
                    "raw ITCM+DTCM layout).")
    ap.add_argument("path", help="microcode image (e.g. a619_gmu.bin)")
    ap.add_argument("--json", metavar="OUT",
                    help="write the full report as JSON to OUT ('-' for stdout)")
    ap.add_argument("--brief", action="store_true",
                    help="human-readable one-screen summary")
    ap.add_argument("--strings-min", type=int, default=DEFAULT_STRING_MIN,
                    help="minimum printable run length (default %d)"
                         % DEFAULT_STRING_MIN)
    ap.add_argument("--entropy-block", type=int, default=512,
                    help="entropy block size in bytes (default 512)")
    ap.add_argument("--thumb-range", metavar="LO:HI",
                    help="override the Thumb census range, e.g. 0x340:0x3e90")
    args = ap.parse_args(argv)

    try:
        with open(args.path, "rb") as f:
            data = f.read()
    except OSError as exc:
        sys.stderr.write("gmu_probe: cannot read %s: %s\n" % (args.path, exc))
        return 2

    thumb_region = None
    if args.thumb_range:
        try:
            lo, hi = args.thumb_range.split(":")
            thumb_region = (int(lo, 0), int(hi, 0))
        except ValueError:
            sys.stderr.write("gmu_probe: --thumb-range wants LO:HI in hex\n")
            return 2

    report, diag = analyze(data, string_min=args.strings_min,
                           entropy_block=args.entropy_block,
                           thumb_region=thumb_region)

    if args.json:
        text = json.dumps(_json_ready(report), indent=2, sort_keys=False)
        if args.json == "-":
            sys.stdout.write(text + "\n")
        else:
            with open(args.json, "w") as f:
                f.write(text + "\n")
            sys.stderr.write("gmu_probe: wrote %s\n" % args.json)

    if args.brief or not args.json:
        print_brief(report)

    return 1 if diag.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
