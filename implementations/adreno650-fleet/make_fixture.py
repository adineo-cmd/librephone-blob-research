#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""make_fixture.py -- deterministic synthetic fixtures for a650_fleet_probe.py.

CLEAN-ROOM / NO-PROPRIETARY-BYTES STATEMENT
===========================================
Every byte written by this script is generated here.  Nothing is copied,
embedded, transcribed or truncated from a vendor payload.  The *structure*
comes from two places only:

  1. Public GPL-2.0 kernel sources (the ``struct block_header`` chain, the
     two loader paths, the DTCM probe offset, the SQE version contract) --
     see the citations in ``a650_fleet_probe.py``.
  2. The lab's own measurements of the fleet, reduced to *shape*: how many
     records, which block addresses, which window each address belongs to.
     No literal taken from a payload is reproduced; where a real image has a
     particular constant, the fixture uses a different one and the test
     asserts the shape, not the value.

Why synthetic at all: the repo forbids committing proprietary bytes, and a
synthetic fixture lets the tests assert *exact* expected values instead of
"whatever the vendor shipped".  A parser regression then fails loudly.

FIXTURES
--------
  a650like_container.bin         41,548 B  the a650 measured shape: 9
                                           zero-size manifest records + 7
                                           payload blocks tagged 0xEFBEADDE,
                                           reset prologue at ITCM 0x10,
                                           80-word vector table at 0x200
                                           with word0 == 0, stack paint.
  a640like_container.bin         37,680 B  the pre-a650 container shape: no
                                           manifest run, 7 payload blocks,
                                           reset prologue at 0x08, DTCM at
                                           0x00040000.
  a619like_raw.bin               32,768 B  the legacy raw ITCM+DTCM image
                                           (both TCMs back to back; exactly
                                           the 0x8000 legacy cap).
  container_overrun.bin           ~2,000 B a chain whose last record declares
                                           more payload than remains -> the
                                           walk must reject it.
  raw_badsp.bin                  32,768 B  raw image with an initial SP
                                           outside DTCM -> error path.
  raw_truncated.bin              16,384 B  half a raw image -> unrecognised.
  sqe_ok.bin                     40,000 B  SQE shape whose version passes
                                           the a650 floor.
  sqe_old.bin                    40,000 B  SQE shape whose version fails it.
  unknown.bin                       512 B  bytes that match no model.

Sizes 41,548 / 37,680 / 32,768 intentionally mirror the fleet magnitudes.
``*.bin`` is gitignored at the repo root; regenerate with

    python3 -I make_fixture.py

and the bytes are identical every time (test_a650_fleet_probe verifies).
"""

import argparse
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_OUTDIR = os.path.join(HERE, "fixtures")

# ---------------------------------------------------------------------------
# Layout constants (citations live in a650_fleet_probe.py)
# ---------------------------------------------------------------------------
ITCM_BASE = 0x00000000
ITCM_SIZE = 0x4000
LEGACY_DTCM_BASE = 0x00040000
A650_DTCM_BASE = 0x10004000
DTCM_SIZE = 0x4000
RAW_IMAGE_SIZE = 0x8000
VTOR_ADDR = 0xE000ED08
PAYLOAD_TAG = 0xEFBEADDE
HOST_SENTINEL = 0xDEADBEEF

# Synthetic fill / counter constants.  Chosen to be visibly NOT the measured
# fleet values so no fixture byte can be mistaken for a payload byte.
SYNTH_FILL = 0xCCCCCCCC
SYNTH_COUNTER_MAGIC = 0x53594E54          # "SYNT"


def stream(n, tag):
    """Deterministic pseudo-random stream: SHA-256 of a tagged counter."""
    tag = tag.encode() if isinstance(tag, str) else tag
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(b"a650fleet:%s:%d" % (tag, counter)).digest()
        counter += 1
    return bytes(out[:n])


# ---------------------------------------------------------------------------
# Thumb-2 encoders -- only the forms the probe decodes.  Each is written from
# the published ARMv7-M encoding, and the decoder in a650_fleet_probe.py is
# written independently from the same document, so an encoder/decoder
# disagreement shows up as a test failure rather than as silent agreement.
# ---------------------------------------------------------------------------

def ldr_pc(rd, target, insn_off):
    """ldr rt,[pc,#imm8*4]; the literal must land on a 4-byte boundary."""
    ea = (insn_off + 4) & ~3
    assert target >= ea and (target - ea) % 4 == 0
    imm8 = (target - ea) // 4
    assert 0 <= imm8 <= 0xFF and 0 <= rd <= 7
    return struct.pack("<H", 0x4800 | (rd << 8) | imm8)


def ldr_imm(rt, rn, off):
    """ldr rt,[rn,#imm5*4] (thumb16)."""
    assert off % 4 == 0 and 0 <= off // 4 <= 31
    return struct.pack("<H", 0x6800 | ((off // 4) << 6) | (rn << 3) | rt)


def str_imm(rt, rn, off):
    """str rt,[rn,#imm5*4] (thumb16)."""
    assert off % 4 == 0 and 0 <= off // 4 <= 31
    return struct.pack("<H", 0x6000 | ((off // 4) << 6) | (rn << 3) | rt)


def msr_sp(psp=False, rn=0):
    """msr msp|psp, Rn -- 1111 0011 1000 Rn / 1000 10x0 1000."""
    return struct.pack("<HH", 0xF380 | rn, 0x8808 | (1 if psp else 0))


def movw_shift(rd, rm, shift):
    """mov.w rd,rm,lsl #shift -- EA4F with imm3:imm2 = shift."""
    assert 0 <= shift <= 31
    h2 = ((shift >> 2) & 7) << 12 | rd << 8 | rm
    return struct.pack("<HH", 0xEA4F, h2)


def addw(rd, rn, imm):
    """add.w rd,rn,#imm12."""
    assert 0 <= imm <= 0xFFF
    h = 0xF100 | (((imm >> 11) & 1) << 10) | rn
    h2 = (((imm >> 8) & 7) << 12) | (rd << 8) | (imm & 0xFF)
    return struct.pack("<HH", h, h2)


def movw_imm(rd, imm32):
    """mov.w rd,#imm32 -- the modified-immediate form.

    Only the values this script needs are supported; the encoder searches
    the legal (mode, byte) / (v, rotate) pairs and raises if the constant is
    not representable, rather than silently emitting something else.
    """
    # mode-based form: imm12 = 00:mode:byte  (imm12 >> 10 == 0)
    for mode in range(4):
        for b in range(256):
            n = sum([1 << (8 * i) for i in range(4)
                     if (mode >> i) & 1 or mode == 0][:1]) if False else None
            if mode == 0:
                cand = b
            elif mode == 1:
                cand = (b << 16) | b
            elif mode == 2:
                cand = (b << 24) | (b << 8)
            else:
                cand = (b << 24) | (b << 16) | (b << 8) | b
            if cand == imm32:
                imm12 = (mode << 8) | b
                return _emit_movw(rd, imm12)
    # modified form: v = 0x80 | imm7, rotate right by imm5
    for v in range(0x80, 0x100):
        for r in range(32):
            cand = ((v >> r) | (v << (32 - r))) & 0xFFFFFFFF if r else v
            if cand == imm32:
                imm12 = (1 << 11) | (r << 7) | (v & 0x7F)
                return _emit_movw(rd, imm12)
    raise ValueError("0x%08x is not a ThumbExpandImm candidate" % imm32)


def _emit_movw(rd, imm12):
    h = 0xF04F | (((imm12 >> 11) & 1) << 10)
    h2 = (((imm12 >> 8) & 7) << 12) | (rd << 8) | (imm12 & 0xFF)
    return struct.pack("<HH", h, h2)


def subs_imm(rn, imm):
    """subs rn,#imm8 (thumb16)."""
    assert 0 <= imm <= 0xFF
    return struct.pack("<H", 0x3800 | (rn << 8) | imm)


def bcond(cond, insn_off, target):
    """b<cond> short form."""
    delta = (target - (insn_off + 4)) // 2
    assert -128 <= delta <= 127
    return struct.pack("<H", 0xD000 | ((cond & 0xF) << 8) | (delta & 0xFF))


def b_wide(insn_off, target):
    """b.w T4 / bl T1 -- 25-bit displacement, sign in hw1 bit 10."""
    delta = target - (insn_off + 4)
    assert -(1 << 24) <= delta < (1 << 24)
    s = 1 if delta < 0 else 0
    u = delta & 0x1FFFFFF
    i1 = (u >> 23) & 1
    i2 = (u >> 22) & 1
    j1 = (1 - (i1 ^ s)) & 1
    j2 = (1 - (i2 ^ s)) & 1
    h1 = 0xF000 | (s << 10) | ((u >> 12) & 0x3FF)
    h2 = 0x9000 | (j1 << 13) | (j2 << 11) | ((u >> 1) & 0x7FF)
    return struct.pack("<HH", h1, h2)


def nop():
    return struct.pack("<H", 0xBF00)


def bx_lr():
    return struct.pack("<H", 0x4770)


# ---------------------------------------------------------------------------
# Shared: vector table + code body
# ---------------------------------------------------------------------------

VECTOR_SLOTS = 16


def vector_table(sp_slot, reset, handlers, irq_target, word0_zero=True):
    """80 words: 16 architectural vectors then 64 external IRQ entries.

    ``word0_zero`` selects the a640/a650 measured shape (no initial-SP slot;
    the stack pointer comes from the reset prologue's own literal) versus the
    a619 shape (word0 repeats the SP).
    """
    words = [0 if word0_zero else sp_slot, reset]
    # NMI, HardFault, MemManage, BusFault, UsageFault
    words += handlers[:5]
    # Reserved 7..10
    words += [0, 0, 0, 0]
    # SVCall, DebugMonitor, Reserved, PendSV, SysTick
    words += [handlers[5], 0, 0, handlers[6], handlers[7]]
    assert len(words) == VECTOR_SLOTS, len(words)
    words += [irq_target] * 64
    return struct.pack("<%dI" % len(words), *words)


def code_body(lo, hi, tag, entry_lo, entry_hi, jitter_src):
    """Deterministic Thumb-ish filler whose census shape is stable.

    Real code is not synthesised here -- only a stream that exercises the
    census and the "handler targets resolve" check.  Per-tag jitter keeps two
    fixtures from sharing a body.
    """
    body = bytearray(stream(hi - lo, "code:" + tag))
    jitter = int(hashlib.sha256(jitter_src.encode()).hexdigest()[:8], 16)

    off = lo
    while off + 24 < hi:
        rel = off - lo
        chunk = b"".join((
            struct.pack("<H", 0xB510 | (rel % 8)),          # push {r4,lr}
            struct.pack("<H", 0x2000 | ((rel + jitter) % 0x100)),   # movs
            struct.pack("<H", 0x6800 | ((rel // 4) % 8)),   # ldr rt,[rn]
            struct.pack("<HH", 0xF000,
                        0xF800 | ((rel + jitter) % 0x100)),  # bl prefix
            struct.pack("<H", 0x6000 | ((rel // 4) % 8)),   # str
            struct.pack("<H", 0xD100 | ((rel + jitter) % 0x100)),  # bne
            bx_lr(),
            nop(),
        ))
        body[off - lo:off - lo + len(chunk)] = chunk
        off += 0x20

    # A handful of odd (Thumb) addresses inside the entry window that the
    # vector table can point at.  Written as `bx lr` preceded by a nop so
    # they are valid instruction boundaries, not random odd numbers.
    for k in range(8):
        a = entry_lo + 4 * (k * 2 + 1)
        if lo <= a < hi - 2:
            body[a - lo:a - lo + 2] = bx_lr()
    return bytes(body)


# ---------------------------------------------------------------------------
# a650-shape container: 9 manifests + 7 payload blocks, 41,548 B
# ---------------------------------------------------------------------------

A650_MANIFEST = (
    (0x00000000, 0x00000200, 0x1),
    (0x00000200, 0x00000200, 0x1),
    (0x00000400, 0x00003C00, 0x1),
    (0x00004000, 0x00008000, 0x1),
    (0x10004000, 0x00003FE0, 0x1),
    (0x10007FDC, 0x00000024, 0x1),
    (0x00144000, 0x00013000, 0x1),
    (0x00157000, 0x00009000, 0x1),
    (0x60000000, 0x00001000, 0x7),
)

A650_PAYLOAD = (
    (0x00000000, 192),
    (0x00000200, 320),
    (0x00000400, 14092),
    (0x00004000, 21968),
    (0x00157000, 920),
    (0x10004000, 3776),
    (0x10007FDC, 24),
)


def make_a650_container(tag="a650like"):
    """The a650 measured block plan, with synthetic contents."""
    dtcm = A650_DTCM_BASE
    top = dtcm + DTCM_SIZE
    msp = top - 0x80
    counter = dtcm + DTCM_SIZE - 0x24          # the 24-byte DTCM tail block
    paint_base = dtcm + 0x3000
    paint_len = 0xF80
    vt_off = 0x200
    entry = 0x10
    code_lo = A650_PAYLOAD[2][0]                # the ITCM code block: 0x400
    code_hi = code_lo + A650_PAYLOAD[2][1]      # ..0x3B0C
    branch_target = code_lo + 0x20              # 0x420, not the measured 0x400

    itcm0 = bytearray(192)                      # block @ 0x0
    itcm_vt = bytearray(320)                    # block @ 0x200
    itcm_code = bytearray(14092)                # block @ 0x400
    icache = bytearray(21968)                   # block @ 0x4000
    icache2 = bytearray(920)                    # block @ 0x157000
    dtcm_body = bytearray(3776)                 # block @ 0x10004000
    dtcm_tail = bytearray(24)                   # block @ 0x10007fdc

    # ---- reset prologue at ITCM 0x10 -----------------------------------
    # Same architectural idiom sequence the decoder supports, different
    # constants and a different branch target from anything measured.
    prog = bytearray()
    o = entry

    def emit(blob):
        nonlocal o
        prog.extend(blob)
        o += len(blob)

    lit_counter1 = 0x58
    lit_msp = 0x5C
    lit_psp = 0x60
    lit_vtor_val = 0x64
    lit_vtor_reg = 0x68
    lit_counter2 = 0x6C
    lit_paint = 0x70

    emit(ldr_pc(0, lit_counter1, entry))        # 0x10
    emit(ldr_imm(1, 0, 0))                      # 0x12
    emit(movw_shift(1, 1, 8))                   # 0x14
    emit(addw(1, 1, 1))                         # 0x18
    emit(str_imm(1, 0, 0))                      # 0x1c
    emit(ldr_pc(0, lit_msp, 0x1E))              # 0x1e
    emit(msr_sp(False, 0))                      # 0x20
    emit(ldr_pc(0, lit_psp, 0x24))              # 0x24
    emit(msr_sp(True, 0))                       # 0x26
    emit(ldr_pc(0, lit_vtor_val, 0x2A))         # 0x2a
    emit(ldr_pc(1, lit_vtor_reg, 0x2C))         # 0x2c
    emit(str_imm(0, 1, 0))                      # 0x2e
    emit(ldr_pc(0, lit_counter2, 0x30))         # 0x30
    emit(ldr_imm(1, 0, 0))                      # 0x32
    emit(movw_shift(1, 1, 8))                   # 0x34
    emit(addw(1, 1, 2))                         # 0x38
    emit(str_imm(1, 0, 0))                      # 0x3c
    emit(ldr_pc(0, lit_paint, 0x3E))            # 0x3e
    emit(movw_imm(1, paint_len))                # 0x40
    emit(movw_imm(2, SYNTH_FILL))               # 0x44
    paint_loop = o                             # 0x48
    emit(str_imm(2, 0, 0))                      # 0x48
    emit(addw(0, 0, 4))                         # 0x4a
    emit(subs_imm(1, 4))                        # 0x4e
    emit(bcond(0x1, o, paint_loop))             # 0x50 bne back to the store
    bw_site = o                                # 0x52
    emit(b_wide(bw_site, branch_target))        # 0x52
    emit(nop())                                 # 0x56
    assert o == 0x58, hex(o)

    # literals (word-aligned, inside the 192-byte block)
    struct.pack_into("<I", itcm0, lit_counter1, counter)
    struct.pack_into("<I", itcm0, lit_msp, msp)
    struct.pack_into("<I", itcm0, lit_psp, HOST_SENTINEL)
    struct.pack_into("<I", itcm0, lit_vtor_val, vt_off)
    struct.pack_into("<I", itcm0, lit_vtor_reg, VTOR_ADDR)
    struct.pack_into("<I", itcm0, lit_counter2, counter)
    struct.pack_into("<I", itcm0, lit_paint, paint_base)
    itcm0[entry:entry + len(prog)] = prog
    struct.pack_into("<II", itcm0, 0, msp, entry | 1)

    # ---- vector table ---------------------------------------------------
    handler = [0x4C1, 0x4C1, 0x4C1, 0x4C1, 0x4C1,      # NMI..UsageFault
               0x3601, 0x511, 0x3603]                  # SVCall, PendSV, SysTick
    handler = [h if (code_lo <= (h & ~1) < code_hi) else 0x4C1
               for h in handler]
    itcm_vt[:] = vector_table(msp, entry | 1, handler, 0x5A1, word0_zero=True)

    # ---- code -----------------------------------------------------------
    body = code_body(code_lo, code_hi, tag, code_lo, code_hi, tag)
    itcm_code[code_lo - 0x400:code_hi - 0x400] = body
    icache[:] = stream(len(icache), tag + ":icache")
    icache2[:] = stream(len(icache2), tag + ":icache2")

    # ---- DTCM -----------------------------------------------------------
    dtcm_body[:] = stream(len(dtcm_body), tag + ":dtcm")
    # The FW-init probe word lives at DTCM_START+0xff8 = 0x10004ff8.  The
    # measured a650 DTCM payload block is 3,776 B and ends at 0x10004ec0, so
    # that word is NOT covered: the driver reads 0 and takes the legacy
    # 0xbabeface branch (a6xx_gmu.c:311-318).  Reproduce that shape exactly
    # instead of synthesising a covered word -- this fixture must report
    # "uncovered" just as the real payload does.
    struct.pack_into("<I", dtcm_tail, 0, 0xFFFFFFFF)
    struct.pack_into("<I", dtcm_tail, 4, SYNTH_COUNTER_MAGIC)
    struct.pack_into("<I", dtcm_tail, 8, 0xFFFFFFFF)
    struct.pack_into("<I", dtcm_tail, 12, SYNTH_COUNTER_MAGIC)
    struct.pack_into("<I", dtcm_tail, 16, 0)
    struct.pack_into("<I", dtcm_tail, 20, 0x20010000)

    bodies = [itcm0, itcm_vt, itcm_code, icache, icache2, dtcm_body, dtcm_tail]

    out = bytearray()
    for addr, value, typ in A650_MANIFEST:
        out += struct.pack("<IIII", addr, 0, typ, value)
    for (addr, size), body in zip(A650_PAYLOAD, bodies):
        assert len(body) == size, (hex(addr), len(body), size)
        out += struct.pack("<IIII", addr, size, PAYLOAD_TAG, PAYLOAD_TAG)
        out += body
    return bytes(out)


# ---------------------------------------------------------------------------
# a640-shape container: 7 payload blocks, no manifest run, 37,680 B
# ---------------------------------------------------------------------------

A640_PAYLOAD = (
    (0x00000000, 48),
    (0x00000200, 320),
    (0x00000400, 14524),
    (0x00004000, 14936),
    (0x00040000, 6944),
    (0x00043FE0, 20),
    (0x00057000, 776),
)


def make_a640_container(tag="a640like"):
    """The pre-a650 container shape: no manifest run, DTCM at 0x00040000,
    reset prologue at 0x08, vector table at 0x200 with word0 == 0."""
    dtcm = LEGACY_DTCM_BASE
    top = dtcm + DTCM_SIZE
    msp = top - 0x80
    vt_off = 0x200
    entry = 0x08
    code_lo, code_hi = 0x400, 0x3A5C

    blk0 = bytearray(48)
    vt = bytearray(320)
    code = bytearray(14524)
    icache = bytearray(14936)
    dtcm_body = bytearray(6944)
    dtcm_tail = bytearray(20)
    bo = bytearray(776)

    prog = bytearray()
    o = entry

    def emit(blob):
        nonlocal o
        prog.extend(blob)
        o += len(blob)

    lit_sp, lit_psp, lit_vtor_val, lit_vtor_reg = 0x20, 0x24, 0x28, 0x2C
    emit(ldr_pc(0, lit_sp, entry))              # 0x08
    emit(msr_sp(False, 0))                      # 0x0a
    emit(ldr_pc(0, lit_psp, 0x0E))              # 0x0e
    emit(msr_sp(True, 0))                       # 0x10
    emit(ldr_pc(0, lit_vtor_val, 0x14))         # 0x14
    emit(ldr_pc(1, lit_vtor_reg, 0x16))         # 0x16
    emit(str_imm(0, 1, 0))                      # 0x18
    bw_site = o                                # 0x1a
    emit(b_wide(bw_site, 0x400))                # 0x1a
    emit(nop())                                 # 0x1e
    assert o == 0x20, hex(o)
    struct.pack_into("<IIII", blk0, 0, msp, entry | 1, 0, 0)
    struct.pack_into("<IIII", blk0, lit_sp, msp, HOST_SENTINEL, vt_off,
                     VTOR_ADDR)
    blk0[entry:entry + len(prog)] = prog

    handler = [0x4B5] * 5 + [0x37F9, 0x4CD, 0x37FB]
    handler = [h if (code_lo <= (h & ~1) < code_hi) else 0x4B5
               for h in handler]
    vt[:] = vector_table(msp, entry | 1, handler, 0x53D, word0_zero=True)

    code[code_lo - 0x400:code_hi - 0x400] = code_body(
        code_lo, code_hi, tag, code_lo, code_hi, tag)
    icache[:] = stream(len(icache), tag + ":icache")
    dtcm_body[:] = stream(len(dtcm_body), tag + ":dtcm4")
    struct.pack_into("<I", dtcm_body, 0xFF8, 0x20000105)   # legacy branch
    struct.pack_into("<IIIII", dtcm_tail, 0, 0x20000105,
                     0xFFFFFFFF, 0x20000012, 0, 0x20000001)
    bo[:] = stream(len(bo), tag + ":bo")

    bodies = [blk0, vt, code, icache, dtcm_body, dtcm_tail, bo]
    out = bytearray()
    for (addr, size), body in zip(A640_PAYLOAD, bodies):
        assert len(body) == size, (hex(addr), len(body), size)
        out += struct.pack("<IIII", addr, size, PAYLOAD_TAG, PAYLOAD_TAG)
        out += body
    assert len(out) == 37680, len(out)
    return bytes(out)


# ---------------------------------------------------------------------------
# Legacy raw ITCM+DTCM image, 32,768 B
# ---------------------------------------------------------------------------

def make_raw_image(tag="a619like", total=RAW_IMAGE_SIZE, msp=None):
    img = bytearray(total)
    if msp is None:
        msp = LEGACY_DTCM_BASE + DTCM_SIZE - 0x80
    psp = LEGACY_DTCM_BASE + 0x1440
    vt_off = 0x200
    entry = 0x08

    prog = bytearray()
    o = entry

    def emit(blob):
        nonlocal o
        prog.extend(blob)
        o += len(blob)

    lit_sp, lit_psp, lit_vtor_val, lit_vtor_reg = 0x20, 0x24, 0x28, 0x2C
    emit(ldr_pc(0, lit_sp, entry))
    emit(msr_sp(False, 0))
    emit(ldr_pc(0, lit_psp, 0x0E))
    emit(msr_sp(True, 0))
    emit(ldr_pc(0, lit_vtor_val, 0x14))
    emit(ldr_pc(1, lit_vtor_reg, 0x16))
    emit(str_imm(0, 1, 0))
    bw_site = o
    emit(b_wide(bw_site, 0x400))
    emit(nop())
    assert o == 0x20

    struct.pack_into("<IIII", img, 0, msp, entry | 1, 0, 0)
    struct.pack_into("<IIII", img, lit_sp, msp, psp, vt_off, VTOR_ADDR)
    img[entry:entry + len(prog)] = prog

    handler = [0x51, 0x71, 0x31, 0xC1, 0x81]
    vt = bytearray(vector_table(msp, entry | 1, handler + [0xA1, 0x91, 0xB1],
                                0x61, word0_zero=False))
    img[vt_off:vt_off + len(vt)] = vt

    code_lo, code_hi = 0x340, 0x3EA4
    img[code_lo:code_hi] = code_body(code_lo, code_hi, tag, code_lo, code_hi, tag)

    # A stride-8 {addr, 0} table in the DTCM half (the measured a619 shape).
    tbl = ITCM_SIZE + 0x4D8
    addrs = [0x440020C0, 0x440020C4, 0x44021800, 0x440218AC, 0x440218A8,
             0x440218A4, 0x440218A0, 0x44034008, 0x4402F810, 0x44027800]
    for k in range(10):
        struct.pack_into("<II", img, tbl + 8 * k, addrs[k], 0)

    # The FW-init sentinel appears in the code half of the measured image.
    struct.pack_into("<II", img, 0x1AF4, 0xBABEFACE, 0xBABEFACE)
    struct.pack_into("<HH", img, ITCM_SIZE + 2, 0x1022, 0x3D90)
    return bytes(img)


def make_raw_truncated(tag="rawtrunc"):
    """Half of the raw image: the prologue is intact but the file is not the
    0x8000 bytes the legacy loader copies, so the classifier must not accept
    it.  Built by truncating the synthetic image, not by laying out a
    different one -- that is exactly the failure mode being tested."""
    return make_raw_image(tag)[:RAW_IMAGE_SIZE // 2]


def make_raw_bad_sp(tag="rawbadsp"):
    return make_raw_image(tag, msp=0x00012340)


def make_container_overrun(tag="overrun"):
    out = bytearray()
    out += struct.pack("<IIII", 0, 0, PAYLOAD_TAG, PAYLOAD_TAG)
    out += struct.pack("<IIII", 0x00000000, 0x100, PAYLOAD_TAG, PAYLOAD_TAG)
    out += stream(0x100, tag + ":b0")
    out += struct.pack("<IIII", 0x00004000, 0x400, PAYLOAD_TAG, PAYLOAD_TAG)
    out += stream(0x40, tag + ":b1")          # only 0x40 of the declared 0x400
    return bytes(out)


def make_unknown(tag="unknown"):
    return stream(512, tag)


# ---------------------------------------------------------------------------
# SQE shape
# ---------------------------------------------------------------------------

def make_sqe(version_bits, tag, size=40000):
    """A file matching the documented SQE contract: dword0 is the stripped
    prefix (0), dword1 carries the driver-visible version."""
    body = bytearray(stream(size, "sqe:" + tag))
    struct.pack_into("<I", body, 0, 0)
    struct.pack_into("<I", body, 4, (0x016D << 16) | (version_bits & 0xFFF))
    return bytes(body)


def build_all():
    return [
        ("a650like_container.bin", make_a650_container()),
        ("a640like_container.bin", make_a640_container()),
        ("a619like_raw.bin", make_raw_image()),
        ("container_overrun.bin", make_container_overrun()),
        ("raw_badsp.bin", make_raw_bad_sp()),
        ("raw_truncated.bin", make_raw_truncated()),
        ("sqe_ok.bin", make_sqe(0x112, "ok")),
        ("sqe_old.bin", make_sqe(0x093, "old")),
        ("unknown.bin", make_unknown()),
    ]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--outdir", default=DEFAULT_OUTDIR)
    args = ap.parse_args(argv)

    os.makedirs(args.outdir, exist_ok=True)
    rows = []
    for name, blob in build_all():
        with open(os.path.join(args.outdir, name), "wb") as f:
            f.write(blob)
        rows.append((name, len(blob), hashlib.md5(blob).hexdigest()))

    width = max(len(r[0]) for r in rows)
    for name, n, md5 in rows:
        print("%-*s %8d B  md5 %s" % (width, name, n, md5))
    print()
    print("All fixtures are synthetic: generated by this script from the public")
    print("layout and the lab's measured shape only. No payload byte is copied,")
    print("and regeneration is byte-identical (test_a650_fleet_probe verifies).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
