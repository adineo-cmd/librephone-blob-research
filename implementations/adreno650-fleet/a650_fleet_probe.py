#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""a650_fleet_probe.py -- clean-room structural probe for the Adreno 650 (and
neighbouring) GPU firmware generation: ``a650_gmu.bin``, ``a650_sqe.fw`` and
the rest of the a6xx GMU/SQE fleet.

CLEAN-ROOM STATEMENT
====================
This file was written from exactly two sources:

  1. Public GPL-2.0 kernel sources.  All fetched 2026-11-19 from
     torvalds/linux master and from linux-firmware:

       drivers/gpu/drm/msm/adreno/a6xx_gmu.c     (loader, block_header)
       drivers/gpu/drm/msm/adreno/a6xx_gmu.h     (gmu_read/gmu_write_bulk)
       drivers/gpu/drm/msm/adreno/a6xx_gpu.c     (a6xx_ucode_check_version)
       drivers/gpu/drm/msm/adreno/a6xx_catalog.c (per-chip firmware table)
       drivers/gpu/drm/msm/adreno/adreno_gpu.c   (adreno_fw_create_bo)
       drivers/gpu/drm/msm/adreno/adreno_gpu.h   (family predicates)
       drivers/gpu/drm/msm/adreno/adreno_device.c(find_chipid / load_gpu)
       linux-firmware WHENCE                     (declared versions)

  2. The author's own measurements of payload bytes: byte histograms,
     offset arithmetic, Shannon entropy, and ARMv7-M / Thumb-2
     *architectural* encodings, which are publicly specified
     (ARM DDI 0403, "ARMv7-M Architecture Reference Manual").  Every
     instruction decoded below is decoded from its published bit pattern
     with a mask test, not from a vendor tool or a leaked header.

No decompiler, disassembler, Ghidra/IDA project, vendor datasheet,
proprietary header, or leaked document was consulted.  No payload bytes
are reproduced in this file, and none are committed to the repo.

WHAT THIS PROBE ANSWERS
=======================
Two questions, in this order, because the second depends on the first.

  Q1  Which of the two firmware *container* formats is this file?
      Mainline has two load paths and they are selected by ``gmu->legacy``
      (a6xx_gmu.c:894), not by the filename:

        * ``legacy``  -> the file IS the image: one size check
          (``> 0x8000`` rejects, a6xx_gmu.c:896) then
          ``gmu_write_bulk(REG_A6XX_GMU_CM3_ITCM_START, ...)``.  No parsing.
        * otherwise   -> the file is a chain of
          ``struct block_header {addr,size,type,value,data[]}``
          (a6xx_gmu.c:857-863, advanced by NEXT_BLK at 874-875).

      The probe therefore *tries the documented walk first* and reports
      honestly when it does not fit.  A negative answer is a finding.

  Q2  What is inside?  For the container class the probe reconstructs the
      loaded address space from the block chain and then decodes, from the
      bytes themselves:
        * the reset stub the CM3 core will execute first,
        * the VTOR vector table, if the image carries one,
        * the DTCM/FW-init handshake word the driver polls (a6xx_gmu.c:311),
        * the per-arm SQE version dword and the kernel branch it selects.

WHERE THIS SITS IN THE FLEET
============================
``a650_gmu.bin`` is named in exactly one mainline catalog entry
(a6xx_catalog.c:1052-1057, chip id 0x06050002, ADRENO_6XX_GEN3, revn 650).
``a650_sqe.fw`` is named in three (a621 0x06020100, a623 0x06020300, a650
0x06050002) -- so the SQE outlives the GMU file.  The probe therefore
handles both artifacts and a ``--cross-gen`` mode that measures the format
boundary across the whole neighbouring fleet.

The probe reports STRUCTURE.  It does not and cannot recover what the
microcode computes.

Exit status: 0 = no error-class diagnostic, 1 = structural violation,
2 = the file could not be read.
"""

import argparse
import collections
import hashlib
import json
import math
import os
import struct
import sys

PROBE_VERSION = "1.0"

# ---------------------------------------------------------------------------
# Constants quoted from public GPL sources (access date 2026-11-19)
# ---------------------------------------------------------------------------

# a6xx_gmu.c:857-863 -- the one firmware container struct mainline documents.
BLOCK_HEADER = struct.Struct("<IIII")
BLOCK_HEADER_SIZE = BLOCK_HEADER.size                  # 16

# a6xx_gmu.c:896 -- the legacy path rejects fw_image->size > 0x8000.
LEGACY_FW_MAX = 0x8000

# a6xx_gmu.c:886-892 -- the driver's two memory maps.
ITCM_BASE = 0x00000000
ITCM_SIZE = 0x4000                                     # SZ_16K
LEGACY_DTCM_BASE = 0x00040000                          # itcm_base/dtcm_base defaults
A650_DTCM_BASE = 0x10004000                            # a650_family/a7xx/a8xx
DTCM_SIZE = 0x4000                                     # SZ_16K
ICACHE_BASE = 0x04000                                  # a6xx_gmu.c:2393 (a650 family)
ICACHE_SIZE = 0x1000000 - 0x4000                       # SZ_16M - SZ_16K
DUMMY_BASE = 0x60000000                                # a6xx_gmu.c:2384
DUMMY_SIZE = 0x1000                                    # gmu->dummy.size (SZ_4K pre-a660)

# a6xx_gmu.c:311-318 -- the FW-init handshake selector.  The driver reads
# DTCM_START + 0xff8; <= 0x20010004 keeps the legacy 0xbabeface / all-ones
# mask branch, anything larger switches to 0x100 / mask 0x1ff.
FW_INIT_PROBE_OFF = 0xFF8
FW_INIT_PROBE_MAX_LEGACY = 0x20010004
FW_INIT_MAGIC_LEGACY = 0xBABEFACE
FW_INIT_MAGIC_NEW = 0x100

# a6xx_catalog.c -- the payload tag.  Measured on every container-generation
# block that carries bytes: type == value == 0xEFBEADDE.  The on-disk byte
# order is DE AD BE EF; the host-order sentinel 0xDEADBEEF is a *different*
# word and the two must not be conflated.
PAYLOAD_TAG = 0xEFBEADDE
HOST_SENTINEL = 0xDEADBEEF

# Manifest record types seen in the leading zero-size run.
MANIFEST_TYPE_PLAIN = 0x1
MANIFEST_TYPE_DUMMY = 0x7

# ARMv7-M architectural anchor.
VTOR_ADDR = 0xE000ED08

# a6xx_gpu.c:1032-1039 -- the per-firmware SQE version contract.  The
# version the kernel tests is buf[0] of the *BO*, i.e. file dword 1,
# because adreno_fw_create_bo (adreno_gpu.c:644-656) strips file dword 0.
#
#   name            branch                                   floor
#   a630_sqe.fw     patched nibble OR >= 1.90                 0x190
#   a650_sqe.fw     >= 0.95                                   0x095
#   a660_sqe.fw     unconditional accept                      None
#   a702_sqe.fw     a7xx/a702 early return (a6xx_gpu.c:997)   None
SQE_FLOORS = collections.OrderedDict([
    ("a630_sqe.fw", {"floor": 0x190, "mode": "patched-or-floor",
                     "cite": "a6xx_gpu.c:1012-1025"}),
    ("a650_sqe.fw", {"floor": 0x095, "mode": "floor",
                     "cite": "a6xx_gpu.c:1032-1039"}),
    ("a660_sqe.fw", {"floor": None, "mode": "unconditional",
                     "cite": "a6xx_gpu.c:1040-1041"}),
    ("a702_sqe.fw", {"floor": None, "mode": "a7xx-early-return",
                     "cite": "a6xx_gpu.c:997-999"}),
])

# Which catalog entries name which file.  Quoted from a6xx_catalog.c
# (line numbers are master @ 2026-11-19).  Used for the "live vs carrying"
# distinction, which is the difference between a file being present in a
# vendor tree and the kernel ever asking for it.
CATALOG = (
    # (chip_ids,            family,             revn, gmu,            sqe,           line)
    ("0x06010900", "ADRENO_6XX_GEN1", 619, "a619_gmu.bin", "a630_sqe.fw", 871),
    ("0x06010901", "ADRENO_6XX_GEN1", 619, "a619_gmu.bin", "a630_sqe.fw", 896),
    ("0x06010900", "ADRENO_6XX_GEN1", 619, "a619_gmu.bin", "a630_sqe.fw", 920),
    ("0x06020100", "ADRENO_6XX_GEN3", None, "a621_gmu.bin", "a650_sqe.fw", 947),
    ("0x06020300", "ADRENO_6XX_GEN3", None, "a623_gmu.bin", "a650_sqe.fw", 971),
    ("0x06030001", "ADRENO_6XX_GEN1", 630, "a630_gmu.bin", "a630_sqe.fw", 1005),
    ("0x06030002", "ADRENO_6XX_GEN1", 630, "a630_gmu.bin", "a630_sqe.fw", 1005),
    ("0x06040001", "ADRENO_6XX_GEN2", 640, "a640_gmu.bin", "a630_sqe.fw", 1028),
    ("0x06050002", "ADRENO_6XX_GEN3", 650, "a650_gmu.bin", "a650_sqe.fw", 1052),
    ("0x06060001", "ADRENO_6XX_GEN4", 660, "a660_gmu.bin", "a660_sqe.fw", 1079),
    ("0x06060300", "ADRENO_6XX_GEN4", None, "a663_gmu.bin", "a660_sqe.fw", 1100),
    ("0x06030500", "ADRENO_6XX_GEN4", None, "a660_gmu.bin", "a660_sqe.fw", 1124),
    ("0x06080001", "ADRENO_6XX_GEN2", 680, "a640_gmu.bin", "a630_sqe.fw", 1151),
    ("0x06090000", "ADRENO_6XX_GEN4", None, "a660_gmu.bin", "a660_sqe.fw", 1171),
    ("0x07000200", "ADRENO_6XX_GEN1", None, None, "a702_sqe.fw", 1191),
    ("0x07000400", "ADRENO_6XX_GEN1", None, None, "a702_sqe.fw", 1191),
)

DEFAULT_STRING_MIN = 4


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

class Diagnostics:
    """Ordered diagnostic sink.  An ``error`` sets the process exit status."""

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
    if not data:
        return 0.0
    counts = collections.Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def entropy_profile(data, block=512):
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


def extract_strings(data, min_len=DEFAULT_STRING_MIN):
    """Printable ASCII runs with file offsets (16-bit Thumb code produces
    many spurious short runs; use min_len >= 8 to keep only real ones)."""
    found = []
    start = None
    n = len(data)
    for i, b in enumerate(data):
        printable = 0x20 <= b <= 0x7E
        if printable and start is None:
            start = i
        elif not printable and start is not None:
            if i - start >= min_len:
                found.append({
                    "offset": start, "encoding": "ascii", "length": i - start,
                    "text": data[start:i].decode("ascii", "replace"),
                })
            start = None
    if start is not None and n - start >= min_len:
        found.append({
            "offset": start, "encoding": "ascii", "length": n - start,
            "text": data[start:].decode("ascii", "replace"),
        })
    return found


THUMB16_CENSUS = (
    ("nop",                 lambda h: h == 0xBF00),
    ("bx lr",               lambda h: h == 0x4770),
    ("ldr Rt,[pc,#imm8]",   lambda h: (h & 0xF800) == 0x4800),
    ("push {...,lr}",       lambda h: (h & 0xFF00) == 0xB500),
    ("pop {...,pc}",        lambda h: (h & 0xFF00) == 0xBD00),
    ("movs Rd,#imm8",       lambda h: (h & 0xF800) == 0x2000),
    ("cmp Rn,#imm8",        lambda h: (h & 0xF800) == 0x2800),
    ("str Rt,[Rn,#imm5]",   lambda h: (h & 0xF800) == 0x6000),
    ("ldr Rt,[Rn,#imm5]",   lambda h: (h & 0xF800) == 0x6800),
    ("ldrb Rt,[Rn,#imm5]",  lambda h: (h & 0xF800) == 0x7800),
    ("str Rt,[sp,#imm8]",   lambda h: (h & 0xFF00) == 0x9000),
    ("ldr Rt,[sp,#imm8]",   lambda h: (h & 0xFF00) == 0x9800),
    ("add Rd,pc,#imm8",     lambda h: (h & 0xF800) == 0xA000),
    ("stm/ldm",             lambda h: (h & 0xF000) == 0xC000),
    ("b<cond>",             lambda h: (h & 0xF000) == 0xD000),
    ("b (16-bit)",          lambda h: (h & 0xF800) == 0xE000),
    ("bl/blx prefix",       lambda h: (h & 0xF800) in (0xF000, 0xF800)),
)


def thumb_census(data, start, end):
    """Counts, over a halfword-aligned scan.  A census, not a disassembly:
    overlapping 32-bit instructions are counted as their low halfword."""
    start -= start % 2
    end = min(end, len(data))
    if end <= start:
        return {"start": start, "end": end, "halfwords": 0, "counts": {}}
    halfwords = [struct.unpack_from("<H", data, o)[0]
                 for o in range(start, end - 1, 2)]
    counts = {name: sum(1 for h in halfwords if pred(h))
              for name, pred in THUMB16_CENSUS}
    total = len(halfwords)
    return {"start": start, "end": end, "halfwords": total, "counts": counts,
            "rates": {k: round(v / total, 4) for k, v in counts.items()}}


# ---------------------------------------------------------------------------
# Thumb-2 decode primitives (ARM DDI 0403).  Each is an exact mask test.
# ---------------------------------------------------------------------------

def thumb_expand_imm(imm12):
    """ThumbExpandImm_C -- the modified-immediate expansion, ARM DDI 0403
    A5.3.2.  Needed because ``mov.w r2,#0xaaaaaaaa`` stores 0x3aa."""
    if (imm12 >> 10) == 0:
        mode = (imm12 >> 8) & 3
        b = imm12 & 0xFF
        if mode == 0:
            return b
        if mode == 1:
            return (b << 16) | b
        if mode == 2:
            return (b << 24) | (b << 8)
        return (b << 24) | (b << 16) | (b << 8) | b
    v = 0x80 | (imm12 & 0x7F)
    r = (imm12 >> 7) & 0x1F
    return ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF


def decode_thumb(image, off, limit=64):
    """Linear sweep of the small instruction alphabet a reset prologue uses.

    ``image`` is a :class:`LoadedImage`; ``off`` is an absolute address.
    Every match below is an exact mask test on the halfword from the
    published ARMv7-M encoding -- no heuristic, no table copied from a
    vendor tool.  The sweep stops at an unconditional transfer, after the
    ``nop`` that closes a prologue, at the limit, or as soon as a halfword
    is not recognised.
    """
    def half(addr):
        b = image.read(addr, 2)
        return struct.unpack("<H", b)[0] if b is not None else None

    def word(addr):
        b = image.read(addr, 4)
        return struct.unpack("<I", b)[0] if b is not None else None

    out = []
    o = off
    while len(out) < limit:
        h = half(o)
        if h is None:
            out.append({"offset": o, "halfwords": [], "length": 0,
                        "mnemonic": "unmapped", "text": "<unmapped>",
                        "unmapped": True})
            break
        rec = {"offset": o, "halfwords": [h], "length": 2}

        if h == 0xBF00:
            rec["mnemonic"] = "nop"
            out.append(rec)
            o += 2
            if len(out) > 1:
                break
            continue

        if h == 0x4770:
            rec["mnemonic"] = "bx lr"
            out.append(rec)
            break

        # ldr Rt,[pc,#imm8*4].  Rt is THREE bits (0100 1 Rt imm8), so 0x49xx
        # is ldr r1 and 0x4fxx is ldr r7 -- there is no high-register form of
        # this encoding; that needs the 32-bit LDR (literal).
        if (h & 0xF800) == 0x4800:
            rt = (h >> 8) & 7
            imm = (h & 0xFF) * 4
            ea = ((o + 4) & ~3) + imm
            val = word(ea)
            rec.update(mnemonic="ldr r%d,[pc,#0x%x]" % (rt, imm),
                       rt=rt, literal_offset=ea, literal=val)
            out.append(rec)
            o += 2
            continue

        h2 = half(o + 2)

        # msr <spec>, Rn -- F380|Rn 88xx.  The source register is the low
        # nibble of the FIRST halfword (1111 0011 1000 Rn); the second
        # halfword's low byte is SYSm (8 = MSP, 9 = PSP).  Taking Rn from
        # hw2 yields "msr msp, r8" for every site in the fleet, which is
        # the tell that the field assignment is wrong.
        if (h & 0xFFF0) == 0xF380 and h2 is not None and (h2 & 0xFF00) == 0x8800:
            spec = h2 & 0xFF
            nm = {8: "msp", 9: "psp"}.get(spec, "sysm%d" % spec)
            rec.update(mnemonic="msr %s, r%d" % (nm, h & 0xF),
                       halfwords=[h, h2], length=4, sysm=spec, rn=h & 0xF)
            out.append(rec)
            o += 4
            continue

        # mov.w Rd,Rm,LSL #imm -- EA4F, imm3:imm2 = shift
        if h == 0xEA4F and h2 is not None and (h2 & 0xC000) == 0:
            shift = (((h2 >> 12) & 7) << 2) | ((h2 >> 6) & 3)
            rd, rm = (h2 >> 8) & 0xF, h2 & 0xF
            rec.update(mnemonic=("mov.w r%d,r%d,lsl #%d" % (rd, rm, shift)
                                 if shift else "mov.w r%d,r%d" % (rd, rm)),
                       halfwords=[h, h2], length=4, rd=rd, rm=rm, shift=shift)
            out.append(rec)
            o += 4
            continue

        # add.w Rd,Rn,#imm12 -- F1xx with imm12 = i:imm3:imm8
        if (h & 0xFB00) == 0xF100 and h2 is not None:
            imm = (((h >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
            rd, rn = (h2 >> 8) & 0xF, h & 0xF
            rec.update(mnemonic="add.w r%d,r%d,#%d" % (rd, rn, imm),
                       halfwords=[h, h2], length=4, rd=rd, rn=rn, imm=imm)
            out.append(rec)
            o += 4
            continue

        # mov.w Rd,#imm16 -- F04F/F44F, imm12 then ThumbExpandImm
        if (h & 0xFBEF) == 0xF04F and h2 is not None:
            imm12 = (((h >> 10) & 1) << 11) | (((h2 >> 12) & 7) << 8) | (h2 & 0xFF)
            rd = (h2 >> 8) & 0xF
            rec.update(mnemonic="mov.w r%d,#0x%x" % (rd, thumb_expand_imm(imm12)),
                       halfwords=[h, h2], length=4, rd=rd,
                       imm=thumb_expand_imm(imm12), imm12=imm12)
            out.append(rec)
            o += 4
            continue

        # ldr/str Rt,[Rn,#imm5*4] (thumb16)
        if (h & 0xF800) in (0x6800, 0x6000):
            rn, rt = (h >> 3) & 7, h & 7
            imm = ((h >> 6) & 0x1F) * 4
            mn = "ldr" if (h & 0xF800) == 0x6800 else "str"
            rec.update(mnemonic="%s r%d,[r%d,#0x%x]" % (mn, rt, rn, imm),
                       rt=rt, rn=rn, imm=imm)
            out.append(rec)
            o += 2
            continue

        # subs Rn,#imm8
        if (h & 0xF800) == 0x3800:
            rn, imm = (h >> 8) & 7, h & 0xFF
            rec.update(mnemonic="subs r%d,#%d" % (rn, imm), rn=rn, imm=imm)
            out.append(rec)
            o += 2
            continue

        # b<cond> (short)
        if (h & 0xF000) == 0xD000:
            cond = {0: "eq", 1: "ne", 2: "cs", 3: "cc", 4: "mi", 5: "pl",
                    6: "vs", 7: "vc", 8: "hi", 9: "ls", 10: "ge", 11: "lt",
                    12: "gt", 13: "le"}.get((h >> 8) & 0xF, "?")
            imm = h & 0xFF
            if imm & 0x80:
                imm -= 0x100
            rec.update(mnemonic="b%s 0x%x" % (cond, o + 4 + imm * 2),
                       target=o + 4 + imm * 2)
            out.append(rec)
            o += 2
            continue

        # b.w T4 / bl T1 -- same 25-bit displacement layout
        if (h & 0xF800) == 0xF000 and h2 is not None:
            is_b = (h2 & 0xD000) == 0x9000
            is_bl = (h2 & 0xD000) == 0xD000
            if is_b or is_bl:
                s = (h >> 10) & 1
                i1 = (1 - ((h2 >> 13) & 1)) ^ s
                i2 = (1 - ((h2 >> 11) & 1)) ^ s
                imm = ((s << 24) | (i1 << 23) | (i2 << 22)
                       | ((h & 0x3FF) << 12) | ((h2 & 0x7FF) << 1))
                if s:
                    imm -= 1 << 25
                rec.update(mnemonic="%s 0x%x" % ("b.w" if is_b else "bl",
                                                 o + 4 + imm),
                           halfwords=[h, h2], length=4, target=o + 4 + imm,
                           is_call=is_bl)
                out.append(rec)
                o += 4
                if is_b:
                    break
                continue

        rec.update(mnemonic="unknown", text="0x%04x" % h)
        out.append(rec)
        break

    return out


# ---------------------------------------------------------------------------
# Loaded-image reconstruction (address space the driver would create)
# ---------------------------------------------------------------------------

class LoadedImage:
    """The address space a container produces once a6xx_gmu_fw_load has
    copied every payload block to its target.  Unwritten addresses read as
    zero, exactly as the TCMs/BOs would after allocation + memcpy.
    """

    def __init__(self, segments=None):
        # segments: list of (addr, bytes)
        self.segments = sorted(segments or [])
        self._by_addr = collections.OrderedDict(self.segments)

    @classmethod
    def from_raw(cls, data, itcm_size=ITCM_SIZE, dtcm_base=LEGACY_DTCM_BASE):
        segs = [(ITCM_BASE, data[:min(itcm_size, len(data))])]
        if len(data) > itcm_size:
            segs.append((dtcm_base, data[itcm_size:]))
        return cls(segs)

    def read(self, addr, n=4):
        for a, body in self.segments:
            if a <= addr and addr + n <= a + len(body):
                return body[addr - a: addr - a + n]
        return None

    def word(self, addr):
        b = self.read(addr, 4)
        return struct.unpack("<I", b)[0] if b is not None else None

    def contains(self, addr, n=1):
        return self.read(addr, n) is not None

    def coverage(self, lo, hi):
        """Covered sub-ranges of [lo, hi)."""
        out = []
        for a, body in self.segments:
            s = max(lo, a)
            e = min(hi, a + len(body))
            if e > s:
                out.append((s, e))
        return out

    def as_flat(self, lo, hi):
        """Zero-filled flat image over [lo, hi) -- what the core would see."""
        buf = bytearray(hi - lo)
        for a, body in self.segments:
            s = max(lo, a)
            e = min(hi, a + len(body))
            if e > s:
                buf[s - lo:e - lo] = body[s - a:e - a]
        return bytes(buf)

    def segments_repr(self):
        return [{"addr": "0x%08x" % a, "size": len(b),
                 "file_sha1": hashlib.sha1(b).hexdigest()[:16]}
                for a, b in self.segments]


# ---------------------------------------------------------------------------
# Format 1: the documented block_header chain (a6xx_gmu.c:877-930)
# ---------------------------------------------------------------------------

def walk_block_headers(data, start=0, max_blocks=4096):
    """Walk mainline's chain exactly as NEXT_BLK advances it: the next record
    begins at ``current + 16 + size``.  A ``size == 0`` record still advances
    one header (that is how the manifest entries are stored)."""
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
                "status": "overflow", "offset": off, "declared_next": nxt,
                "file_size": n,
                "detail": "record at 0x%x declares %d payload bytes past EOF"
                          % (off, nxt - n),
            }
        blocks.append({"offset": off, "addr": addr, "size": size,
                       "type": typ, "value": value, "next": nxt})
        off = nxt
    return blocks, {"status": "exact-eof" if off == n else "short", "offset": off}


def classify_region(addr, size, dtcm_base):
    """Map a block's load address onto the windows a6xx_gmu.c:906-930 names."""
    if ITCM_BASE <= addr < ITCM_BASE + ITCM_SIZE:
        return "ITCM"
    if dtcm_base <= addr < dtcm_base + DTCM_SIZE:
        return "DTCM"
    if ICACHE_BASE <= addr < ICACHE_BASE + ICACHE_SIZE:
        return "icache"
    if DUMMY_BASE <= addr < DUMMY_BASE + ICACHE_SIZE:
        return "dummy/BO"
    return "outside-known-windows"


def detect_dtcm_base(blocks):
    """Derive the DTCM base from the file rather than assuming a family.

    Measured rule: a container that targets the a650-family map carries a
    block or manifest entry at 0x10004000; the pre-a650 map uses 0x40000.
    Returns (base, basis)."""
    addrs = {b["addr"] for b in blocks}
    if A650_DTCM_BASE in addrs:
        return A650_DTCM_BASE, "block at 0x10004000 (a650-family map)"
    if LEGACY_DTCM_BASE in addrs:
        return LEGACY_DTCM_BASE, "block at 0x00040000 (pre-a650 map)"
    # Fall back to the block whose address is nearest above the icache window
    # but still below the dummy page.
    cand = [b["addr"] for b in blocks
            if ICACHE_BASE <= b["addr"] < DUMMY_BASE and b["size"]]
    if cand:
        return min(cand) if min(cand) >= LEGACY_DTCM_BASE else LEGACY_DTCM_BASE, \
               "inferred from the lowest mapped block"
    return LEGACY_DTCM_BASE, "default (no block in a DTCM window)"


def build_load_map(data, blocks):
    """(addr -> bytes) segments, in file order, skipping manifest records."""
    segs = []
    for b in blocks:
        if b["size"] == 0:
            continue
        body = data[b["offset"] + BLOCK_HEADER_SIZE: b["next"]]
        segs.append((b["addr"], body))
    return segs


# ---------------------------------------------------------------------------
# Vector table
# ---------------------------------------------------------------------------

VECTOR_NAMES = (
    "Initial SP", "Reset", "NMI", "HardFault", "MemManage", "BusFault",
    "UsageFault", "Reserved", "Reserved", "Reserved", "Reserved", "SVCall",
    "DebugMonitor", "Reserved", "PendSV", "SysTick",
)


def read_vector_table(image, offset, count=16):
    """Read the architectural vectors at ``offset`` out of a LoadedImage."""
    words = []
    for i in range(count):
        w = image.word(offset + 4 * i)
        if w is None:
            return None
        words.append(w)
    entries = [{"index": i, "name": VECTOR_NAMES[i], "value": w,
                "thumb": bool(w & 1) if i else None}
               for i, w in enumerate(words)]
    return {"offset": offset, "entries": entries, "words": words}


def enumerate_irq_tail(image, start, limit=64, max_addr=1 << 32):
    """Walk the external-interrupt tail: consecutive non-zero words that are
    odd (Thumb) addresses resolving into the loaded image."""
    words = []
    for i in range(limit):
        off = start + 4 * i
        v = image.word(off)
        if v is None or v == 0:
            break
        if not (v & 1) or (v & ~1) >= max_addr:
            break
        if not image.contains(v & ~1, 2):
            break
        words.append({"offset": off, "index": i, "value": v})
    if not words:
        return None
    targets = sorted({w["value"] for w in words})
    return {
        "offset": start, "count": len(words),
        "distinct_targets": ["0x%08x" % t for t in targets],
        "single_handler": len(targets) == 1,
    }


# ---------------------------------------------------------------------------
# Reset stub
# ---------------------------------------------------------------------------

def decode_reset_stub(image, entry):
    """Decode the reset prologue at ``entry`` (mask the Thumb bit first).

    The decode is a straight-line simulation over the register/literal
    state; nothing is pattern-matched against a remembered byte string.
    The facts reported are exactly the architectural ones the core will
    observe: MSP, PSP, the value stored to SCB->VTOR, any stack paint loop,
    any boot-counter increment, and where control leaves the prologue.
    """
    dis = decode_thumb(image, entry)
    stub = {
        "entry": entry,
        "instruction_count": len(dis),
        "length": sum(r["length"] for r in dis),
        "disassembly": dis,
        "msp": None, "psp": None,
        "vtor_value": None, "vtor_reg": None, "vtor_reg_is_scb_vtor": False,
        "branch_target": None, "call_targets": [],
        "paint": None, "counter_sites": [], "literals": [],
        "terminated": False,
    }

    reg = {}          # register -> last loaded literal / computed value
    loaded = {}       # register -> (address it was loaded from)
    vtor_store = None
    pending_add = {}  # register -> constant added since the load

    for rec in dis:
        mn = rec["mnemonic"]

        if rec.get("literal") is not None:
            reg[rec["rt"]] = rec["literal"]
            loaded.pop(rec["rt"], None)
            pending_add.pop(rec["rt"], None)
            stub["literals"].append({"insn_offset": rec["offset"],
                                     "value": rec["literal"], "text": mn})
            continue

        if mn.startswith("msr"):
            v = reg.get(rec["rn"])
            if rec.get("sysm") == 8:
                stub["msp"] = v
            elif rec.get("sysm") == 9:
                stub["psp"] = v
            continue

        if mn.startswith("mov.w") and rec.get("imm") is not None:
            reg[rec["rd"]] = rec["imm"]
            loaded.pop(rec["rd"], None)
            pending_add.pop(rec["rd"], None)
            continue

        if mn.startswith("add.w") and rec.get("rd") == rec.get("rn"):
            base = reg.get(rec["rn"])
            if base is not None:
                reg[rec["rd"]] = (base + rec["imm"]) & 0xFFFFFFFF
                if rec["rd"] in loaded:
                    pending_add[rec["rd"]] = rec["imm"]
            continue

        if mn.startswith("ldr") and rec.get("rt") is not None:
            base = reg.get(rec["rn"])
            if base is not None and rec.get("imm") is not None:
                addr = (base + rec["imm"]) & 0xFFFFFFFF
                reg[rec["rt"]] = image.word(addr)
                loaded[rec["rt"]] = addr
                pending_add.pop(rec["rt"], None)
            else:
                reg.pop(rec["rt"], None)
                loaded.pop(rec["rt"], None)
            continue

        if mn.startswith("str") and rec.get("rt") is not None:
            addr_reg = reg.get(rec["rn"])
            val = reg.get(rec["rt"])
            if addr_reg is not None and val is not None:
                if addr_reg == VTOR_ADDR:
                    vtor_store = {"value": val, "target": addr_reg,
                                  "insn_offset": rec["offset"]}
                elif rec["rt"] in loaded and \
                        loaded[rec["rt"]] == addr_reg + rec.get("imm", 0):
                    # read-modify-write back to the SAME address: the
                    # measured "bump this counter" idiom.  Record the
                    # constant added, not the resulting value.
                    stub["counter_sites"].append({
                        "counter_addr": addr_reg,
                        "insn_offset": rec["offset"],
                        "addend": pending_add.get(rec["rt"]),
                    })
            continue

        if mn.startswith("subs"):
            continue
        if mn.startswith("b") and rec.get("is_call"):
            stub["call_targets"].append(rec["target"])
            continue
        if rec.get("target") is not None:
            stub["branch_target"] = rec["target"]
            stub["terminated"] = True
            continue

    if vtor_store:
        stub["vtor_value"] = vtor_store["value"]
        stub["vtor_reg"] = vtor_store["target"]
        stub["vtor_reg_is_scb_vtor"] = (vtor_store["target"] == VTOR_ADDR)

    # Stack paint: a `mov.w len ; mov.w fill ; str ; add ; subs ; bne` loop.
    # Identified by the fill constant being a repeating byte (0xaaaaaaaa or
    # 0xcccccccc are the measured idioms) and the length being page-scale.
    for i, rec in enumerate(dis):
        if rec.get("imm") is None or rec["length"] != 4:
            continue
        fill = rec["imm"]
        if fill in (0, 0xFFFFFFFF) or len({(fill >> (8 * k)) & 0xFF
                                           for k in range(4)}) != 1:
            continue
        length = None
        for back in range(i - 1, max(i - 4, -1), -1):
            cand = dis[back].get("imm")
            if cand is not None and cand > 0x100 and cand % 4 == 0:
                length = cand
                break
        if length is None:
            continue
        base = None
        for back in range(i - 1, -1, -1):
            if dis[back].get("literal") is not None:
                base = dis[back]["literal"]
                break
        if base is None:
            continue
        stub["paint"] = {"base": base, "bytes": length, "fill": fill}
        break

    stub["shape"] = _stub_shape(stub)
    return stub


def _stub_shape(stub):
    """Name the prologue by which architectural facts it establishes.  Two
    measured shapes dominate; a third covers the a660-family entry."""
    parts = []
    if stub["counter_sites"]:
        parts.append("cnt")
    if stub["msp"] is not None:
        parts.append("msp")
    if stub["psp"] is not None:
        parts.append("psp")
    if stub["vtor_value"] is not None:
        parts.append("vtor")
    if stub["paint"]:
        parts.append("paint")
    if stub["call_targets"]:
        parts.append("call")
    if stub["branch_target"] is not None:
        parts.append("bw")
    return "+".join(parts) if parts else "unrecognised"


# ---------------------------------------------------------------------------
# SQE
# ---------------------------------------------------------------------------

def sqe_shape_plausible(data):
    """Is this plausibly an Adreno SQE microcode file?

    The discriminator is architectural, from adreno_gpu.c:644-656:
    adreno_fw_create_bo() allocates ``fw->size - 4`` and copies from
    ``&fw->data[4]``, so file dword 0 is a stripped prefix.  In every build
    measured (13 files, 30-77 KiB, a6xx and a7xx) that dword is 0x00000000.
    A 4-byte zero prefix on a multi-KiB, dword-aligned file is a 2^-32
    coincidence elsewhere, so the test is strong; the *meaning* of the
    prefix is [OPEN].
    """
    n = len(data)
    if n < 0x2000 or n % 4 or n > 0x400000:
        return False
    d0, d1 = struct.unpack_from("<II", data, 0)
    if d0 != 0:
        return False
    if d1 == 0 or (d1 & 0xFFF) == 0:
        return False
    return True


def read_sqe_version(data):
    """The driver-visible version: file dword 1, because dword 0 is stripped."""
    if len(data) < 8:
        return None
    dwords = struct.unpack_from("<II", data, 0)
    return {
        "lead_dword": dwords[0],
        "version_dword": dwords[1],
        "version_bits": dwords[1] & 0xFFF,
        "version_major": (dwords[1] & 0xFFF) >> 8,
        "version_minor": (dwords[1] & 0xFFF) & 0xFF,
        # The a630 patched form looks at the low nibble of the BO's dword 2,
        # i.e. file dword 3 (a6xx_gpu.c:1015-1020).
        "patched_nibble": (dwords[1] & 0xF) == 0xA,
        "dword3_low_nibble": (struct.unpack_from("<I", data, 12)[0] & 0xF)
                             if len(data) >= 16 else None,
    }


def sqe_verdict(version_bits, name, patched_ok=None):
    """Which branch of a6xx_ucode_check_version() applies, and the result."""
    info = SQE_FLOORS.get(name)
    if info is None:
        return {"name": name, "mode": "unknown-gpu", "passes": False,
                "cite": "a6xx_gpu.c:1042-1045",
                "detail": "no entry in a6xx_ucode_check_version(); the "
                          "kernel logs 'unknown GPU' and refuses"}
    mode, floor = info["mode"], info["floor"]
    if mode in ("unconditional", "a7xx-early-return"):
        return {"name": name, "mode": mode, "passes": True,
                "floor": None, "cite": info["cite"],
                "detail": "accepted without a version test"}
    if mode == "patched-or-floor":
        ok = bool(patched_ok) or version_bits >= floor
        return {"name": name, "mode": mode, "passes": ok, "floor": floor,
                "cite": info["cite"],
                "detail": ("patched nibble accepted" if patched_ok and ok else
                           "version 0x%03x vs floor 0x%03x"
                           % (version_bits, floor))}
    return {"name": name, "mode": mode, "passes": version_bits >= floor,
            "floor": floor, "cite": info["cite"],
            "detail": "version 0x%03x vs floor 0x%03x"
                      % (version_bits, floor)}


# ---------------------------------------------------------------------------
# Format classification -- the answer to Q1
# ---------------------------------------------------------------------------

def classify_format(data):
    """Return {"format": ..., "basis": ...} for one of

        container  -- mainline block_header chain, exact EOF, >=1 payload
        raw-tcm    -- the legacy bulk-write image (no header at all)
        sqe        -- SQE microcode (4-byte stripped prefix)
        unknown    -- none of the above
    """
    n = len(data)
    if n == 0:
        return {"format": "unknown", "basis": "empty file"}

    blocks, term = walk_block_headers(data)
    payload = [b for b in blocks if b["size"] > 0]
    if term["status"] == "exact-eof" and payload:
        dtcm_base, dtcm_basis = detect_dtcm_base(blocks)
        in_window = [b for b in payload
                     if classify_region(b["addr"], b["size"], dtcm_base)
                     in ("ITCM", "DTCM", "icache", "dummy/BO")]
        if in_window:
            return {
                "format": "container",
                "basis": ("block_header chain reaches EOF exactly at 0x%x "
                          "after %d records (%d with payload); %d payload "
                          "block(s) land in a window a6xx_gmu.c:906-930 writes"
                          % (term["offset"], len(blocks), len(payload),
                             len(in_window))),
                "blocks": blocks, "termination": term,
                "dtcm_base": dtcm_base, "dtcm_basis": dtcm_basis,
            }

    if n == LEGACY_FW_MAX and looks_like_raw_image(data):
        return {
            "format": "raw-tcm",
            "basis": ("exactly 0x8000 bytes (the legacy loader's cap, "
                      "a6xx_gmu.c:896) with the ARMv7-M reset prologue at "
                      "0x08; the block walk %s at 0x%x"
                      % (term["status"], term["offset"])),
            "termination": term,
        }

    if sqe_shape_plausible(data):
        return {"format": "sqe",
                "basis": ("dword0 == 0 (the 4-byte prefix "
                          "adreno_fw_create_bo strips, adreno_gpu.c:648-656) "
                          "and a non-zero version dword")}

    return {"format": "unknown",
            "basis": ("block walk %s at 0x%x; not 0x8000 bytes; no SQE "
                      "prefix" % (term["status"], term["offset"])),
            "termination": term}


def looks_like_raw_image(data):
    """The a619/a630 legacy prologue, measured byte-for-byte on both:
    ldr r0,[pc]; msr msp,r0; ldr r0,[pc]; msr psp,r0; ..."""
    if len(data) < 0x30:
        return False
    hw = lambda o: struct.unpack_from("<H", data, o)[0]
    return (hw(0x08) & 0xF800) == 0x4800 and \
           hw(0x0A) == 0xF380 and (hw(0x0C) & 0xFF00) == 0x8800 and \
           (hw(0x0E) & 0xF800) == 0x4800 and \
           hw(0x10) == 0xF380 and (hw(0x12) & 0xFF00) == 0x8800


# ---------------------------------------------------------------------------
# Body analysis for the container / raw classes
# ---------------------------------------------------------------------------

def analyze_gmu(data, diag, string_min=DEFAULT_STRING_MIN, entropy_block=512):
    report = {"kind": "gmu"}
    cls = classify_format(data)
    report["format"] = cls["format"]
    report["format_basis"] = cls["basis"]
    n = len(data)

    if cls["format"] == "container":
        blocks = cls["blocks"]
        dtcm_base = cls["dtcm_base"]
        payload = [b for b in blocks if b["size"] > 0]
        for b in blocks:
            b["region"] = classify_region(b["addr"], b["size"], dtcm_base)
            b["tag_is_payload"] = (b["type"] == PAYLOAD_TAG and
                                   b["value"] == PAYLOAD_TAG)

        lead = []
        for b in blocks:
            if b["size"] != 0:
                break
            lead.append({
                "offset": b["offset"], "addr": b["addr"], "value": b["value"],
                "type": b["type"],
            })

        report.update({
            "header_present": True,
            "header_struct": "struct block_header (a6xx_gmu.c:857-863)",
            "block_count": len(blocks),
            "payload_block_count": len(payload),
            "manifest_block_count": len(lead),
            "blocks": blocks,
            "manifest": lead,
            "walk_termination": cls["termination"],
            "dtcm_base": dtcm_base,
            "dtcm_basis": cls["dtcm_basis"],
            "loaded_segments": [
                {"addr": "0x%08x" % a, "size": len(b),
                 "sha1_16": hashlib.sha1(b).hexdigest()[:16]}
                for a, b in build_load_map(data, blocks)],
        })

        windows = collections.OrderedDict()
        for b in payload:
            e = windows.setdefault(b["region"], {"blocks": 0, "bytes": 0,
                                                 "lo": b["addr"],
                                                 "hi": b["addr"] + b["size"]})
            e["blocks"] += 1
            e["bytes"] += b["size"]
            e["lo"] = min(e["lo"], b["addr"])
            e["hi"] = max(e["hi"], b["addr"] + b["size"])
        for e in windows.values():
            e["lo"] = "0x%08x" % e["lo"]
            e["hi"] = "0x%08x" % e["hi"]
        report["windows"] = windows

        # tag discipline: every payload block should carry the same tag
        tags = {b["type"] for b in payload}
        report["payload_tags"] = ["0x%08x" % t for t in sorted(tags)]
        if tags == {PAYLOAD_TAG}:
            diag.info("payload-tag",
                      "all %d payload blocks carry type == value == "
                      "0x%08x (the container payload tag)" % (len(payload), PAYLOAD_TAG))
        elif tags:
            diag.warn("payload-tag",
                      "payload blocks carry %d distinct type words: %s"
                      % (len(tags), ", ".join("0x%08x" % t for t in sorted(tags))))

        # manifest tiling: do the manifest records tile the loader windows?
        if lead:
            tiles = [(m["addr"], m["addr"] + m["value"]) for m in lead
                     if m["value"] and m["type"] == MANIFEST_TYPE_PLAIN]
            report["manifest_tiles"] = [
                {"start": "0x%08x" % a, "end": "0x%08x" % b} for a, b in tiles]
            diag.info("manifest",
                      "%d zero-size manifest records precede the first "
                      "payload block (types %s); they tile %d window(s)"
                      % (len(lead),
                         ", ".join(sorted({"0x%x" % m["type"] for m in lead})),
                         len(tiles)))

        image = LoadedImage(build_load_map(data, blocks))
        report["image"] = _image_analysis(data, image, dtcm_base, diag,
                                          entropy_block, string_min,
                                          container=True)

    elif cls["format"] == "raw-tcm":
        report.update({
            "header_present": False,
            "header_struct": None,
            "header_verdict": ("no container header of any kind: the file is "
                               "a flat memory image whose first word is the "
                               "ARMv7-M initial stack pointer"),
            "load_path": {
                "kernel": "a6xx_gmu.c:894-904 (gmu->legacy branch)",
                "mechanism": ("gmu_write_bulk(REG_A6XX_GMU_CM3_ITCM_START, "
                              "fw->data, fw->size) -- DMA'd verbatim, no parsing"),
                "size_cap": LEGACY_FW_MAX,
            },
            "dtcm_base": LEGACY_DTCM_BASE,
            "dtcm_basis": "legacy map (a6xx_gmu.c:887 default)",
        })
        image = LoadedImage.from_raw(data, ITCM_SIZE, LEGACY_DTCM_BASE)
        report["image"] = _image_analysis(data, image, LEGACY_DTCM_BASE, diag,
                                          entropy_block, string_min,
                                          container=False)
    else:
        diag.error("unrecognised-layout",
                   "neither the mainline block_header chain, the legacy raw "
                   "image, nor the SQE shape explains these bytes (%s)"
                   % cls["basis"])
        report["header_present"] = False
        report["image"] = {}

    return report


def _image_analysis(data, image, dtcm_base, diag, entropy_block, string_min,
                    container):
    """Facts that come from the *loaded* address space, whichever format."""
    out = collections.OrderedDict()

    # --- reset entry ------------------------------------------------------
    w0 = image.word(ITCM_BASE + 0)
    w1 = image.word(ITCM_BASE + 4)
    out["itcm_word0"] = w0
    out["itcm_word1"] = w1
    reset = w1
    out["reset_vector_word"] = reset

    if reset is None:
        diag.error("no-reset-vector", "no bytes are loaded at ITCM 0x0/0x4")
        return out

    if not (reset & 1):
        diag.error("reset-not-thumb",
                   "reset vector 0x%08x has the Thumb bit clear" % reset)
        return out

    entry = reset & ~1
    if not image.contains(entry, 4):
        diag.error("reset-out-of-image",
                   "reset vector 0x%08x points at 0x%x, which no block loads"
                   % (reset, entry))
        return out

    stub = decode_reset_stub(image, entry)
    out["reset_stub"] = stub
    diag.info("reset-stub",
              "reset vector 0x%08x -> ITCM+0x%x; %d-instruction prologue, "
              "shape '%s'" % (reset, entry, stub["instruction_count"],
                              stub["shape"]))
    if not stub["terminated"]:
        diag.warn("stub-not-terminated",
                  "the reset prologue did not reach a transfer within %d "
                  "instructions; decode stops at 0x%x"
                  % (stub["instruction_count"],
                     stub["disassembly"][-1]["offset"] if stub["disassembly"]
                     else entry))

    # --- MSP sanity -------------------------------------------------------
    msp = stub["msp"]
    if msp is None:
        msp = w0
        out["msp_source"] = "ITCM word 0 (no msr in the prologue)"
    else:
        out["msp_source"] = "msr msp in the reset prologue"
    out["msp"] = msp
    top = dtcm_base + DTCM_SIZE
    if msp is None:
        diag.warn("no-msp", "no initial stack pointer could be established")
    elif not (dtcm_base <= msp <= top):
        diag.error("bad-msp",
                   "initial SP 0x%08x is outside the DTCM window "
                   "[0x%08x, 0x%08x)" % (msp, dtcm_base, top))
    elif msp % 4:
        diag.error("misaligned-msp",
                   "initial SP 0x%08x is not 4-byte aligned" % msp)
    else:
        out["msp_offset_from_dtcm_top"] = top - msp
        if top - msp == 0x80:
            diag.info("msp-at-conventional-slot",
                      "initial SP 0x%08x == DTCM top 0x%08x - 0x80"
                      % (msp, top))
        else:
            diag.warn("msp-off-convention",
                      "initial SP 0x%08x sits 0x%x below the DTCM top, not "
                      "the measured 0x80" % (msp, top - msp))

    # --- stack paint ------------------------------------------------------
    if stub["paint"]:
        p = stub["paint"]
        out["stack_paint"] = p
        if p["base"] is not None and p["bytes"]:
            diag.info("stack-paint",
                      "prologue paints 0x%x bytes at 0x%08x with 0x%08x "
                      "(ends at 0x%08x%s)"
                      % (p["bytes"], p["base"], p["fill"],
                         p["base"] + p["bytes"],
                         ", exactly the initial SP" if p["base"] + p["bytes"] == msp
                         else ""))

    # --- is the initial SP inside a block at all? -------------------------
    # On a650 the answer is NO, and that is the interesting part: the file
    # never writes the stack page.  The reset prologue paints it at runtime
    # and the first push lands below MSP.  A container that *did* map the
    # stack would be initialising a region the core overwrites anyway.
    if msp is not None:
        covered = image.contains(msp, 4)
        out["msp_covered_by_a_block"] = covered
        if not covered:
            if stub["paint"]:
                where = ("the paint loop covers 0x%08x..0x%08x"
                         % (stub["paint"]["base"],
                            stub["paint"]["base"] + stub["paint"]["bytes"]))
            else:
                where = ("DTCM block coverage: %s"
                         % ", ".join("0x%08x..0x%08x" % (s, e)
                                     for s, e in
                                     image.coverage(dtcm_base,
                                                    dtcm_base + DTCM_SIZE)))
            diag.info("msp-unmapped",
                      "initial SP 0x%08x is not written by any block -- the "
                      "stack page is established at runtime (%s)"
                      % (msp, where))

    # --- vector table -----------------------------------------------------
    vtor = stub["vtor_value"]
    out["vtor_value"] = vtor
    out["vtor_reg"] = stub["vtor_reg"]
    out["vtor_reg_is_scb_vtor"] = stub["vtor_reg_is_scb_vtor"]
    vt_off = None
    if stub["vtor_reg_is_scb_vtor"] and vtor is not None:
        vt_off = vtor
    elif image.contains(0x200, 64):
        vt_off = 0x200           # measured: every generation uses 0x200
        diag.info("vector-table-default",
                  "no SCB->VTOR store decoded; using the measured 0x200 slot")

    if vt_off is not None:
        vt = read_vector_table(image, vt_off, 16)
        if vt is None:
            if image.contains(0x200, 4):
                diag.error("vtor-out-of-range",
                           "VTOR target 0x%x is not readable in the loaded "
                           "image" % vt_off)
            else:
                out["vector_table"] = None
                out["vector_table_absent"] = True
                diag.info("no-vector-table",
                          "no block loads the 0x%x vector-table window (the "
                          "measured 0x200 slot is not covered)" % vt_off)
        else:
            out["vector_table"] = vt
            words = vt["words"]
            if words[0] == msp:
                out["vt_word0_role"] = "initial-SP copy"
                diag.info("vector-table",
                          "table at 0x%x begins with the same SP (0x%08x) the "
                          "prologue loaded" % (vt_off, msp))
            elif words[0] == 0:
                out["vt_word0_role"] = "unused (zero)"
                diag.info("vector-table",
                          "table at 0x%x has word0 == 0 -- a handler table "
                          "with no SP slot" % vt_off)
            else:
                out["vt_word0_role"] = "unexpected"
                diag.warn("vt-word0",
                          "table at 0x%x has word0 == 0x%08x, which is "
                          "neither the loaded SP nor zero" % (vt_off, words[0]))

            # every non-zero handler must be odd and resolve into the image
            bad = []
            for i, w in enumerate(words):
                if w == 0 or i == 0:
                    continue
                if not (w & 1):
                    bad.append({"index": i, "value": w, "why": "thumb bit clear"})
                elif not image.contains(w & ~1, 2):
                    bad.append({"index": i, "value": w, "why": "target not loaded"})
            out["vector_targets_resolve"] = not bad
            if bad:
                diag.error("vector-targets",
                           "%d architectural vector(s) do not resolve into "
                           "loaded code: %s" % (len(bad), bad[:4]))
            else:
                diag.info("vector-targets",
                          "all 15 non-zero architectural vectors are odd "
                          "(Thumb) and resolve into loaded code")

            if words[1] != reset:
                diag.warn("vt-reset-mismatch",
                          "table's Reset slot is 0x%08x but ITCM word1 is "
                          "0x%08x" % (words[1], reset))
            irq = enumerate_irq_tail(image, vt_off + 64)
            if irq:
                out["irq_tail"] = irq
                diag.info("irq-tail",
                          "%d external interrupt entries, %d distinct target(s)"
                          % (irq["count"], len(irq["distinct_targets"])))

    # --- FW-init handshake -------------------------------------------------
    probe = image.word(dtcm_base + FW_INIT_PROBE_OFF)
    out["fw_init_probe_offset"] = "0x%08x" % (dtcm_base + FW_INIT_PROBE_OFF)
    out["fw_init_probe_value"] = probe      # None == uncovered == reads 0
    effective = 0 if probe is None else probe
    if effective <= FW_INIT_PROBE_MAX_LEGACY:
        out["fw_init_branch"] = "legacy 0x%08x, mask 0xffffffff" % FW_INIT_MAGIC_LEGACY
    else:
        out["fw_init_branch"] = "new 0x%x, mask 0x1ff" % FW_INIT_MAGIC_NEW
    diag.info("fw-init-probe",
              "DTCM+0x%x = %s -> driver takes the %s branch (a6xx_gmu.c:311-318)"
              % (FW_INIT_PROBE_OFF,
                 "uncovered (reads 0)" if probe is None else "0x%08x" % probe,
                 "legacy" if effective <= FW_INIT_PROBE_MAX_LEGACY else "new"))

    # --- marker census -----------------------------------------------------
    out["markers"] = {
        "payload_tag": data.count(struct.pack("<I", PAYLOAD_TAG)),
        "host_sentinel": data.count(struct.pack("<I", HOST_SENTINEL)),
        "fw_init_magic": data.count(struct.pack("<I", FW_INIT_MAGIC_LEGACY)),
    }

    # --- code / data split -------------------------------------------------
    code_ranges = []
    for a, body in image.segments:
        if a < ITCM_BASE + ITCM_SIZE:
            code_ranges.append((0, min(len(body), ITCM_SIZE - a)))
        elif a < ICACHE_BASE + ICACHE_SIZE:
            code_ranges.append((0, len(body)))
    out["entropy"] = collections.OrderedDict()
    for a, body in image.segments:
        key = "seg@0x%08x" % a
        out["entropy"][key] = {
            "size": len(body),
            "entropy": round(shannon_entropy(body), 4),
            "zero_fraction": round(body.count(0) / len(body), 4),
        }

    strings = extract_strings(data, string_min)
    out["string_count"] = len(strings)
    out["strings_sample"] = strings[:12]

    return out


def analyze_sqe(data, diag, name=None, string_min=DEFAULT_STRING_MIN):
    report = {"kind": "sqe", "format": "sqe",
              "format_basis": classify_format(data)["basis"]}
    ver = read_sqe_version(data)
    if ver is None:
        diag.error("sqe-too-short", "file is shorter than two dwords")
        return report
    report["version"] = ver
    report["version_text"] = "%x.%02x" % (ver["version_major"],
                                          ver["version_minor"])

    if name is None:
        name = _infer_sqe_name(data)
    report["sqe_name"] = name
    verdict = sqe_verdict(ver["version_bits"], name,
                          patched_ok=ver["patched_nibble"] and
                          (ver["dword3_low_nibble"] or 0) >= 1
                          if ver["dword3_low_nibble"] is not None else False)
    report["kernel_verdict"] = verdict
    if verdict["passes"]:
        diag.info("sqe-version",
                  "%s: driver version 0x%03x (%s) passes the %s branch (%s)"
                  % (name, ver["version_bits"], report["version_text"],
                     verdict["mode"], verdict["cite"]))
    else:
        diag.error("sqe-too-old",
                   "%s: driver version 0x%03x (%s) FAILS the %s branch -- "
                   "a6xx_ucode_load returns -EPERM and adreno_load_gpu "
                   "returns NULL, so no GPU registers (%s)"
                   % (name, ver["version_bits"], report["version_text"],
                      verdict["mode"], verdict["cite"]))

    report["strings"] = extract_strings(data, string_min)[:12]
    prof = [round(shannon_entropy(data[i:i + 1024]), 3)
            for i in range(0, len(data) - len(data) % 1024, 1024)]
    report["entropy"] = {
        "whole": round(shannon_entropy(data), 4),
        "zero_fraction": round(data.count(0) / len(data), 4),
        "per_1k_min": min(prof) if prof else None,
        "per_1k_max": max(prof) if prof else None,
    }
    report["body"] = {
        "bo_bytes": len(data) - 4,
        "cite": "adreno_gpu.c:644-656 -- BO is size-4 copied from data[4]",
    }
    # dword histogram is a cheap identity check between two builds
    words = struct.unpack_from("<%dI" % (len(data) // 4), data)
    top = collections.Counter(words).most_common(5)
    report["top_dwords"] = [["0x%08x" % w, c] for w, c in top]
    return report


def _infer_sqe_name(data):
    """Best-effort: the file cannot name itself.  Use the version's high bits
    only to distinguish a6xx from a7xx, and report the guess as a guess."""
    if len(data) < 8:
        return "unknown"
    d1 = struct.unpack_from("<I", data, 4)[0]
    top = d1 >> 16
    if top == 0x0173:
        return "a730_sqe.fw"
    if top == 0x0174:
        return "a740_sqe.fw"
    if top == 0x016D:
        # a630/a650/a660 all ship 0x016d....  The low 12 bits separate them
        # on every build measured, but that is a measurement, not a rule.
        return "a650_sqe.fw"
    return "unknown"


# ---------------------------------------------------------------------------
# Cross-generation table
# ---------------------------------------------------------------------------

def cross_generation_row(path):
    """One row of the fleet table.  Never raises; unreadable files become a
    row with an ``error`` field so a partial fleet still tabulates."""
    row = {"file": os.path.basename(path), "path": path}
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError as exc:
        row["error"] = str(exc)
        return row
    row.update({
        "bytes": len(data),
        "md5": hashlib.md5(data).hexdigest(),
        "entropy": round(shannon_entropy(data), 3),
        "zero_fraction": round(data.count(0) / len(data), 4),
    })
    cls = classify_format(data)
    row["format"] = cls["format"]
    row["format_basis"] = cls["basis"]

    if cls["format"] == "container":
        blocks = cls["blocks"]
        dtcm_base = cls["dtcm_base"]
        payload = [b for b in blocks if b["size"]]
        image = LoadedImage(build_load_map(data, blocks))
        row.update({
            "records": len(blocks),
            "payload_blocks": len(payload),
            "manifest_blocks": len(blocks) - len(payload),
            "walk": cls["termination"]["status"],
            "dtcm_base": "0x%08x" % dtcm_base,
            "windows": sorted({classify_region(b["addr"], b["size"], dtcm_base)
                               for b in payload}),
        })
    elif cls["format"] == "raw-tcm":
        image = LoadedImage.from_raw(data)
        row.update({"records": None, "payload_blocks": None,
                    "manifest_blocks": None,
                    "walk": cls["termination"]["status"],
                    "dtcm_base": "0x00040000",
                    "windows": ["ITCM", "DTCM"]})
    else:
        row["u32_0"] = None
        return row

    w0 = image.word(0)
    w1 = image.word(4)
    row["u32_0"] = "0x%08x" % w0 if w0 is not None else None
    row["u32_1"] = "0x%08x" % w1 if w1 is not None else None
    row["vt_at_0x200"] = image.contains(0x200, 64)
    row["vt_word0"] = ("0x%08x" % image.word(0x200)
                       if row["vt_at_0x200"] else None)
    row["reset_entry"] = ("0x%x" % (w1 & ~1)) if w1 else None
    row["markers_payload_tag"] = data.count(struct.pack("<I", PAYLOAD_TAG))
    row["markers_host_sentinel"] = data.count(struct.pack("<I", HOST_SENTINEL))
    row["markers_fw_init"] = data.count(struct.pack("<I", FW_INIT_MAGIC_LEGACY))

    if w1:
        stub = decode_reset_stub(image, w1 & ~1)
        row["stub_shape"] = stub["shape"]
        row["stub_msp"] = "0x%08x" % stub["msp"] if stub["msp"] is not None else None
        row["stub_paint_bytes"] = stub["paint"]["bytes"] if stub["paint"] else None
        row["stub_branch"] = ("0x%x" % stub["branch_target"]
                              if stub["branch_target"] is not None else None)
    return row


CROSSGEN_COLUMNS = (
    ("file", 22), ("bytes", 7), ("format", 10), ("rec", 4),
    ("u32_0", 10), ("u32_1", 10), ("vt@200", 6), ("vt_w0", 10),
    ("entry", 8), ("stub shape", 28), ("paint", 6), ("branch", 8),
)


def format_crossgen_table(rows):
    """Fixed-width table, no external deps."""

    def cell(key, r):
        if key == "rec":
            v = r.get("records")
            return "-" if v is None else str(v)
        if key == "vt@200":
            v = r.get("vt_at_0x200")
            return "-" if v is None else ("yes" if v else "no")
        if key == "vt_w0":
            v = r.get("vt_word0")
            return "-" if v is None else v
        if key == "entry":
            v = r.get("reset_entry")
            return "-" if v is None else v
        if key == "paint":
            v = r.get("stub_paint_bytes")
            return "-" if v is None else str(v)
        if key == "branch":
            v = r.get("stub_branch")
            return "-" if v is None else v
        if key == "stub shape":
            v = r.get("stub_shape")
            return "-" if v is None else v
        v = r.get(key)
        return "-" if v is None else str(v)

    header = "  ".join("%-*s" % (w, k) for k, w in CROSSGEN_COLUMNS)
    lines = [header, "-" * len(header)]
    for r in rows:
        if r.get("error"):
            lines.append("%-22s  ERROR %s" % (r["file"], r["error"]))
            continue
        parts = []
        for k, w in CROSSGEN_COLUMNS:
            v = cell(k, r)
            if len(v) > w:
                v = v[:w - 1] + "~"
            parts.append("%-*s" % (w, v))
        lines.append("  ".join(parts))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Top level
# ---------------------------------------------------------------------------

def analyze(data, name=None, kind="auto", string_min=DEFAULT_STRING_MIN,
            entropy_block=512):
    diag = Diagnostics()
    n = len(data)
    report = {
        "tool": "a650_fleet_probe.py",
        "tool_version": PROBE_VERSION,
        "size": n,
        "md5": hashlib.md5(data).hexdigest(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "whole_entropy": round(shannon_entropy(data), 4) if n else 0.0,
        "zero_byte_fraction": round(data.count(0) / n, 4) if n else 0.0,
        "entropy_block": entropy_block,
        "entropy_profile": entropy_profile(data, entropy_block) if n else [],
    }

    if n == 0:
        diag.error("empty", "input file is empty")
        report.update({"kind": "unknown", "format": "unknown",
                       "diagnostics": diag.items,
                       "diagnostic_counts": diag.counts()})
        return report, diag

    cls = classify_format(data)
    if kind == "auto":
        kind = "sqe" if cls["format"] == "sqe" else "gmu"
    elif cls["format"] == "unknown":
        # Nothing is modelled, so no --kind hint can rescue the file.  Route
        # to the GMU analyser unconditionally: it is the one that raises the
        # "unrecognised-layout" error instead of decoding a bogus version.
        if kind != "gmu":
            diag.warn("kind-mismatch",
                      "--kind %s was forced, but the bytes match no modelled "
                      "format; reporting the structural failure instead" % kind)
        kind = "gmu"
    elif kind == "sqe" and cls["format"] != "sqe":
        # --kind is a hint, not a blindfold.  Analysing a block_header
        # container as an SQE would report a version decoded out of the first
        # record's address field, which is worse than useless.
        diag.warn("kind-mismatch",
                  "--kind sqe requested, but the bytes classify as '%s'; "
                  "analysing them as %s instead"
                  % (cls["format"], cls["format"]))
        kind = "gmu"
    elif kind == "gmu" and cls["format"] == "sqe":
        diag.warn("kind-mismatch",
                  "--kind gmu requested, but the bytes carry the SQE "
                  "shape (dword0 == 0, non-zero version dword); analysing "
                  "them as sqe instead")
        kind = "sqe"

    if kind == "sqe":
        body = analyze_sqe(data, diag, name=name, string_min=string_min)
    else:
        body = analyze_gmu(data, diag, string_min=string_min,
                           entropy_block=entropy_block)
    report.update(body)
    report["catalog"] = catalog_for(name or os.path.basename(
        getattr(data, "name", "") or ""))
    report["diagnostics"] = diag.items
    report["diagnostic_counts"] = diag.counts()
    return report, diag


def catalog_for(filename):
    """Which catalog entries name this file, and do those entries load a GMU
    at all?  This is the live-vs-carrying distinction, straight from
    a6xx_catalog.c."""
    if not filename:
        return {"filename": filename, "entries": [], "note": "no filename"}
    entries = []
    for chip, family, revn, gmu, sqe, line in CATALOG:
        if filename in (gmu, sqe):
            entries.append({
                "chip_ids": chip, "family": family, "revn": revn,
                "gmu": gmu, "sqe": sqe, "catalog_line": line,
                "role": "gmu" if filename == gmu else "sqe",
                "loads_a_gmu": gmu is not None,
            })
    return {"filename": filename, "entries": entries,
            "entry_count": len(entries)}


def print_brief(report, stream=sys.stdout):
    w = stream.write
    w("file      : %d bytes  md5 %s\n" % (report["size"], report["md5"]))
    w("kind      : %s\n" % report.get("kind", "?"))
    w("format    : %s\n" % report.get("format", "?"))
    w("  basis   : %s\n" % _wrap(report.get("format_basis", ""), 11, 68))

    if report.get("kind") == "sqe":
        v = report["version"]
        w("lead dword: 0x%08x (stripped by adreno_fw_create_bo)\n"
          % v["lead_dword"])
        w("version   : 0x%08x -> %s  (bits 0xfff = 0x%03x)\n"
          % (v["version_dword"], report["version_text"], v["version_bits"]))
        kv = report["kernel_verdict"]
        w("kernel    : %s  %s\n"
          % ("PASS" if kv["passes"] else "FAIL", kv["mode"]))
        w("            %s (%s)\n" % (kv["detail"], kv["cite"]))
    else:
        img = report.get("image") or {}
        if report.get("header_present"):
            w("header    : present -- %s\n" % report.get("header_struct"))
            w("blocks    : %d (%d payload, %d manifest), walk %s\n"
              % (report.get("block_count", 0),
                 report.get("payload_block_count", 0),
                 report.get("manifest_block_count", 0),
                 report.get("walk_termination", {}).get("status")))
            w("dtcm base : 0x%08x (%s)\n" % (report.get("dtcm_base", 0),
                                             report.get("dtcm_basis")))
        else:
            w("header    : ABSENT -- %s\n" % report.get("header_verdict", ""))
        if img:
            w("reset vec : %s -> entry 0x%x\n"
              % (img.get("reset_vector_word"), (img.get("reset_vector_word") or 0) & ~1))
            stub = img.get("reset_stub") or {}
            w("stub      : %s\n" % stub.get("shape"))
            w("            msp=%s psp=%s vtor=%s reg=%s\n"
              % (_hx(stub.get("msp")), _hx(stub.get("psp")),
                 _hx(stub.get("vtor_value")), _hx(stub.get("vtor_reg"))))
            if stub.get("paint"):
                p = stub["paint"]
                w("            paint %d B @ %s with %s\n"
                  % (p["bytes"], _hx(p["base"]), _hx(p["fill"])))
            if stub.get("branch_target") is not None:
                w("            transfers to 0x%x\n" % stub["branch_target"])
            vt = img.get("vector_table")
            if vt:
                w("vector tbl: 0x%x  word0=%s (%s)\n"
                  % (vt["offset"], _hx(vt["words"][0]),
                     img.get("vt_word0_role")))
                irq = img.get("irq_tail") or {}
                if irq:
                    w("            %d IRQ entries, targets %s\n"
                      % (irq["count"], ", ".join(irq["distinct_targets"])))
            elif img.get("vector_table_absent"):
                w("vector tbl: ABSENT -- the 0x200 window is not loaded\n")
            w("fw init   : %s = %s -> %s\n"
              % (img.get("fw_init_probe_offset"),
                 _hx(img.get("fw_init_probe_value")) if
                 img.get("fw_init_probe_value") is not None else "uncovered (0)",
                 img.get("fw_init_branch")))
            m = img.get("markers") or {}
            w("markers   : payload-tag %d, host-sentinel %d, fw-init %d\n"
              % (m.get("payload_tag", 0), m.get("host_sentinel", 0),
                 m.get("fw_init_magic", 0)))
            w("strings   : %d run(s) >= the minimum length\n"
              % img.get("string_count", 0))

    cat = report.get("catalog") or {}
    if cat.get("entries"):
        w("catalog   : %d entry/entries name this file\n" % cat["entry_count"])
        for e in cat["entries"]:
            w("            %s %-17s %-8s revn=%-4s -> %s\n"
              % (e["chip_ids"], e["family"],
                 "gmu" if e["role"] == "gmu" else "sqe",
                 e["revn"] if e["revn"] else "-",
                 "loads " + (e["gmu"] or "(no gmu)") + " + " + (e["sqe"] or "-")))

    counts = report["diagnostic_counts"]
    w("diagnostics: %d error, %d warning, %d info\n"
      % (counts["error"], counts["warning"], counts["info"]))
    for d in report["diagnostics"]:
        w("  [%s] %-22s %s\n" % (d["level"], d["code"], d["message"]))


def _hx(v):
    return "-" if v is None else "0x%08x" % v


def _wrap(text, indent, width):
    out = []
    line = ""
    for word in text.split():
        if len(line) + len(word) + 1 > width:
            out.append(line)
            line = word
        else:
            line = (line + " " + word).strip()
    if line:
        out.append(line)
    return ("\n" + " " * indent).join(out)


def _json_ready(obj):
    if isinstance(obj, dict):
        return {k: _json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_ready(v) for v in obj]
    if isinstance(obj, (bytes, bytearray)):
        return obj.hex()
    return obj


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Clean-room structural probe for the Adreno a650 GPU "
                    "firmware generation (GMU container + SQE), with a "
                    "cross-generation format table.")
    ap.add_argument("path", help="firmware file (a650_gmu.bin, a650_sqe.fw, ...)")
    ap.add_argument("--json", metavar="OUT",
                    help="write the full report as JSON to OUT ('-' = stdout)")
    ap.add_argument("--brief", action="store_true",
                    help="human-readable one-screen summary")
    ap.add_argument("--cross-gen", nargs="+", metavar="FILE",
                    help="also measure these files and print the "
                         "cross-generation table")
    ap.add_argument("--kind", choices=("auto", "gmu", "sqe"), default="auto",
                    help="force the artifact class (default: auto-detect)")
    ap.add_argument("--sqe-name", metavar="NAME",
                    help="the catalog filename to test the SQE against, "
                         "e.g. a650_sqe.fw (default: infer)")
    ap.add_argument("--strings-min", type=int, default=DEFAULT_STRING_MIN,
                    help="minimum printable run length (default %d)"
                         % DEFAULT_STRING_MIN)
    ap.add_argument("--entropy-block", type=int, default=512,
                    help="entropy block size in bytes (default 512)")
    args = ap.parse_args(argv)

    try:
        with open(args.path, "rb") as f:
            data = f.read()
    except OSError as exc:
        sys.stderr.write("a650_fleet_probe: cannot read %s: %s\n"
                         % (args.path, exc))
        return 2

    report, diag = analyze(data, name=args.sqe_name, kind=args.kind,
                           string_min=args.strings_min,
                           entropy_block=args.entropy_block)

    if args.cross_gen:
        paths = [args.path] + [p for p in args.cross_gen if p != args.path]
        rows = [cross_generation_row(p) for p in paths]
        report["cross_generation"] = rows
    else:
        rows = None

    if args.json:
        text = json.dumps(_json_ready(report), indent=2, sort_keys=False)
        if args.json == "-":
            sys.stdout.write(text + "\n")
        else:
            with open(args.json, "w") as f:
                f.write(text + "\n")
            sys.stderr.write("a650_fleet_probe: wrote %s\n" % args.json)
    else:
        print_brief(report)
        if rows:
            sys.stdout.write("\ncross-generation table\n")
            sys.stdout.write(format_crossgen_table(rows) + "\n")

    if args.brief and args.json:
        print_brief(report)
        if rows:
            sys.stdout.write("\ncross-generation table\n")
            sys.stdout.write(format_crossgen_table(rows) + "\n")

    return 1 if diag.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
