#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_fixture.py -- deterministic SYNTHETIC fixtures for cpp_probe.py.

WHY SYNTHETIC
-------------
The real ``cpp_firmware_vN_N_N.fw`` images are proprietary Qualcomm vendor
blobs. The repo ``.gitignore`` excludes ``*.bin`` and this family's ``*.fw``
is not tracked either; the programme rule is that no real payload bytes are
ever committed. So, following the pattern already used in
``implementations/qca-bt-gen2/make_fixture.py`` and
``implementations/adsp-fleet/make_fixture.py``, the fixtures here are
**self-made bytes**.

They reproduce only the *layout* this session measured on the real fleet
(see ``cpp-version-matrix-analysis.md``); they reproduce **none** of its
content. Every payload byte comes from a SHA-256 counter stream keyed by a
per-fixture tag, so re-running this script reproduces every fixture
byte-for-byte -- which ``test_cpp_probe.py`` verifies.

WHAT GETS BUILT
---------------
A twelve-entry ladder mirroring the real fleet's version list and its
measured shape, so the matrix / first-diff / padding logic is exercised at
the same scale as the real data:

    fixtures/cpp_firmware_v1_1_1.fw    16,128 B   (the short-window outlier)
    fixtures/cpp_firmware_v1_1_6.fw    16,384 B
    fixtures/cpp_firmware_v1_2_0.fw    16,384 B
    fixtures/cpp_firmware_v1_4_0.fw    16,384 B
    fixtures/cpp_firmware_v1_5_0.fw    16,384 B
    fixtures/cpp_firmware_v1_5_1.fw    16,384 B   (2-byte step delta from 1_5_0)
    fixtures/cpp_firmware_v1_5_2.fw    16,384 B
    fixtures/cpp_firmware_v1_6_0.fw    16,384 B
    fixtures/cpp_firmware_v1_8_0.fw    16,384 B
    fixtures/cpp_firmware_v1_10_0.fw   16,384 B
    fixtures/cpp_firmware_v1_12_0.fw   16,384 B
    fixtures/cpp_firmware_v1_12_1.fw   16,384 B

plus deliberately-broken fixtures for the error paths:

    fixtures/bad_size_synthetic.fw      16,383 B  (not word-aligned, exit 1)
    fixtures/truncated_synthetic.fw        16 B   (header unreadable, exit 1)
    fixtures/all_fill_synthetic.fw     16,384 B   (no payload, exit 1)

MODELLED LAYOUT (own measurement of the real fleet, 2026-11-19)
--------------------------------------------------------------
    [0x0000, 0x0002)  lead word 0x7140
    [0x0002, 0x0022)  16 x u16 vector table
    [0x0022, code_end)  opaque code/table region (counter stream)
    [code_end, 0x3efe)  0xFF fill (erased-flash pattern)
    [0x3efe, 0x3fca)  invariant 204-byte epilogue (shared across the ladder)
    [0x3fca, 0x4000)  0xFF fill
    within code:      one u16 == 0x1000 | BCD(minor)  (the version marker)
    within code:      the three CPP protocol magic words

The real files' code_end varies from 0x19b6 to 0x3b02; the fixtures pick a
deterministic code_end per version inside that observed band so that the
padding length varies the way it really does.

CLEAN-ROOM
----------
Only the layout is reproduced, and the layout is this session's own
measurement of payload bytes. The three protocol magic words and the
``CPP_FW_VERSION_*`` bitfield are quoted from public GPL-2.0-only /
vendor-source headers (``msm_cpp.h``, ``cpp_hw_params.h``) cited in
``cpp_probe.py``'s header. No proprietary content, no decompilation.
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures")

WINDOW = 16384
SHORT_WINDOW = 16128

LEAD_WORD = 0x7140
EPILOGUE_START = 0x3EFE
EPILOGUE_END = 0x3FCA
PAD = 0xFF

# public constants (msm_cpp.h, GPL-2.0-only)
MSG_ID_CMD = 0x3E646D63
MSG_ID_OK = 0x0A0A4B4F
MSG_ID_TRAILER = 0xABCDEFAA

# The ladder, with the code_end each fixture uses. Values are chosen inside
# the band the real fleet occupies (0x19b6 .. 0x3b02) and vary per version so
# that fill length and matrix distances are not constant.
LADDER = [
    # (major, minor, step, total_bytes, code_end)
    (1, 1, 1, SHORT_WINDOW, 0x3B02),   # the short-window outlier
    (1, 1, 6, WINDOW, 0x3B02),
    (1, 2, 0, WINDOW, 0x1B36),
    (1, 4, 0, WINDOW, 0x1AFE),
    (1, 5, 0, WINDOW, 0x1A5E),
    (1, 5, 1, WINDOW, 0x1A5E),         # same code_end as 1_5_0: 2-byte delta
    (1, 5, 2, WINDOW, 0x1B4E),
    (1, 6, 0, WINDOW, 0x19B6),
    (1, 8, 0, WINDOW, 0x3B02),
    (1, 10, 0, WINDOW, 0x2704),
    (1, 12, 0, WINDOW, 0x28D4),
    (1, 12, 1, WINDOW, 0x287C),
]

# Step-bump shapes actually measured on the real fleet (2026-11-19):
#   1.5.0 -> 1.5.1  two bytes differ (0x0034 and 0x00c4); the code is
#                   otherwise untouched, so whole-file identity is 99.99%.
#   1.12.0 -> 1.12.1  a substantial rewrite: whole 61.06%, content 32.95%.
# The ladder models both, so the probe's diff logic is exercised against a
# tiny delta and a large one rather than only one of them.
STEP_VARY = {
    # version: (base version whose code is reused, content mix fraction)
    (1, 5, 1): ((1, 5, 0), 0.0),
    (1, 12, 1): ((1, 12, 0), 0.65),
}

# Measured: the byte outside the enum word that a step bump moves.
STEP_DELTA_OFFSET = 0x0034


# Measured trailer behaviour (see cpp_probe.probe_trailer): the u16 at 0x3EFC
# is a halfword count of the region it terminates, i.e. code_end == 2*(w+1).
# Three identities leave it at the erased value 0xffff instead; three later
# ones append a further 176-byte fixed-stride block after the described
# region. The fixtures model all three cases.
TRAILER_ERASED = {(1, 1, 1), (1, 1, 6), (1, 8, 0)}
TRAILER_STRIDE_BLOCK = {(1, 10, 0), (1, 12, 0), (1, 12, 1)}
STRIDE_BLOCK_LEN = 176
STRIDE_PROLOGUE_LEN = 14
STRIDE_RECORD_LEN = 20
STRIDE_RECORD_COUNT = 8
STRIDE_TAIL_LEN = 2
STRIDE_BODY_LEN = 12


# ---------------------------------------------------------------- primitives

def counter_stream(tag: bytes, n: int) -> bytes:
    """Deterministic pseudo-random bytes: SHA-256 in counter mode.

    Fully reproducible from ``tag`` + ``n``; used so fixtures are regenerable
    and carry no vendor content whatsoever.
    """
    out = bytearray()
    block = 0
    while len(out) < n:
        out.extend(hashlib.sha256(tag + struct.pack("<Q", block)).digest())
        block += 1
    return bytes(out[:n])


def version_marker(major: int, minor: int, step: int) -> int:
    """The measured self-identification word: 0x1000 | BCD(minor)."""
    return 0x1000 | (((minor // 10) << 4) | (minor % 10))


def fw_enum(major: int, minor: int, step: int) -> int:
    """cpp_hw_params.h bitfield: 31:28 major, 27:16 minor, 15:0 step."""
    return ((major & 0xF) << 28) | ((minor & 0xFFF) << 16) | (step & 0xFFFF)


def build_epilogue() -> bytes:
    """The invariant 204-byte trailing block, synthesised once.

    Real files share one byte-identical epilogue; the fixtures share one
    self-made block so the probe's epilogue-identity logic is exercised.
    """
    tag = b"cpp-fixture-epilogue-v1"
    body = bytearray(counter_stream(tag, EPILOGUE_END - EPILOGUE_START))

    def plant(at, text):
        i = at - EPILOGUE_START
        # MEASURED: in the real epilogue each literal sits between
        # non-printable bytes (0xff before 'v1.1', 0x8d after), so each is an
        # exact printable run. Model that, otherwise the scanner reports a
        # longer run and the "this literal is not a version field" check
        # cannot be made cleanly.
        body[i - 1] = PAD
        body[i:i + len(text)] = text
        body[i + len(text)] = 0x8D

    # Plant the same ASCII landmarks the real epilogue carries so the
    # version-string scanner has something honest to find and classify.
    plant(0x3F80, b"v1.1")
    plant(0x3FB4, b"cmd>")
    return bytes(body)


EPILOGUE = build_epilogue()


# ---------------------------------------------------------------- builder

def build_image(major: int, minor: int, step: int,
                total_bytes: int = WINDOW, code_end: int = 0x1A5E) -> bytes:
    """Assemble one synthetic CPP image with the measured layout."""
    if total_bytes not in (WINDOW, SHORT_WINDOW):
        raise ValueError("total_bytes must be %d or %d, got %d"
                         % (WINDOW, SHORT_WINDOW, total_bytes))
    if not 0x22 + 32 < code_end <= EPILOGUE_START:
        raise ValueError("code_end out of range: 0x%x" % code_end)
    # MEASURED: the one short-window file (v1_1_1, 16,128 B) ends before the
    # epilogue and carries none of it; every 16,384 B file carries it.
    has_epilogue = total_bytes >= EPILOGUE_END

    buf = bytearray(b"\xff" * total_bytes)

    # lead word + u16 vector table (16 entries, self-made but shaped like the
    # real one: a few distinct values with repeats)
    struct.pack_into("<H", buf, 0x00, LEAD_WORD)
    # A step bump that reuses the base image's code (1.5.0 -> 1.5.1) must also
    # reuse its header, otherwise the modelled delta is not the measured
    # 2 bytes. Key the header stream on the lineage, not the exact version.
    vec_ver = (major, minor, step)
    if STEP_VARY.get(vec_ver, (None, 1.0))[1] == 0.0:
        vec_ver = STEP_VARY[vec_ver][0]
    vec_tag = b"cpp-fixture-vectors-%d.%d.%d" % vec_ver
    vec_stream = counter_stream(vec_tag, 32)
    for i in range(16):
        # Values inside the code region, with the real fleet's observed repeat
        # pattern: slot 1 plus slots 4-8 and 10-14 all share one value.
        if i in (1, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14):
            v = 0x0400 + (0x0100 * 1)
        elif i == 9:
            v = 0x0A01          # MEASURED: slot 9 is odd in 9/12 real files
        elif i == 15:
            v = 0x0C01          # MEASURED: slot 15 is odd in 10/12 real files
        else:
            # slots 0, 2, 3 get their own distinct values (6 distinct total,
            # matching the 11/12 real pattern)
            v = 0x0200 + 0x0300 * i
        # per-version wobble, applied per distinct value (an even step, so
        # parity stays as set above and the repeat pattern survives)
        v = (v + (vec_stream[v % 32] % 0x20) * 2) & 0x1FFF
        struct.pack_into("<H", buf, 0x02 + 2 * i, v)

    # opaque code region: deterministic stream thinned with 0xFF fill so the
    # region's entropy lands in the real measured band (~3.3-4.7 bits/byte).
    # The thinning mask is deterministic (a multiplicative hash of the index),
    # not random, so fixtures stay reproducible.
    #
    # code_end semantics match the probe: code_end is the first fill byte, so
    # the code region is [0x22, code_end) and the fill starts exactly at
    # code_end.
    code_len = code_end - 0x22

    def thinned(ver):
        """The thinned deterministic code stream for one version."""
        tag = b"cpp-fixture-code-%d.%d.%d" % ver
        raw = counter_stream(tag, code_len)
        out = bytearray(code_len)
        for i in range(code_len):
            # deterministic thinning: a well-mixed per-index selector, no
            # periodicity (a multiplicative hash on the index repeats visibly
            # at these lengths and skews the entropy band)
            sel = hashlib.sha256(b"thin" + struct.pack("<Q", i)).digest()[0]
            out[i] = raw[i] if sel < 148 else PAD   # ~58% content, 42% fill
        return out

    ver = (major, minor, step)
    code = thinned(ver)

    # Step bumps: model the two shapes measured on the real fleet so the
    # diff logic meets both a 2-byte delta and a substantial rewrite.
    vary = STEP_VARY.get(ver)
    if vary:
        base_ver, mix = vary
        base = thinned(base_ver)
        if mix == 0.0:
            # 1.5.0 -> 1.5.1: the code is reused verbatim; only the enum step
            # nibble and one code byte move -- two differing bytes, measured.
            code = base
            j = STEP_DELTA_OFFSET - 0x22
            code[j] = code[j] ^ 0x5A
        else:
            # 1.12.0 -> 1.12.1: partial rewrite. Adopt the base byte at a
            # deterministic subset of positions; the rest keep this
            # version's own stream.
            for i in range(code_len):
                sel = hashlib.sha256(b"mix" + struct.pack("<Q", i)).digest()[0]
                if sel < int(mix * 256):
                    code[i] = base[i]

    # guarantee the code region ends exactly at code_end: force the last 4
    # bytes to be content so code_end is not eroded by trailing fill. The
    # substitute bytes are constants, so step siblings still agree here.
    for i in range(max(0, code_len - 4), code_len):
        if code[i] == PAD:
            code[i] = (0x21, 0x43, 0x65, 0x87)[code_len - 1 - i]
    # version marker: 16-bit aligned, planted away from the enum word so it
    # is found exactly once
    marker_off = (code_len // 3) & ~1
    struct.pack_into("<H", code, marker_off, version_marker(major, minor, step))
    # enum constant (contains the marker nibbles at +2), so the probe can
    # cross-check name -> enum -> bytes; placed far from marker_off
    enum_off = ((code_len * 3 // 4) & ~3)
    if abs(enum_off - marker_off) < 8:
        enum_off = ((code_len * 3 // 4) + 16) & ~3
    struct.pack_into("<I", code, enum_off, fw_enum(major, minor, step))
    # the three protocol magic words, 4-byte aligned, in the low part
    struct.pack_into("<I", code, 0x0040, MSG_ID_CMD)
    struct.pack_into("<I", code, 0x0080, MSG_ID_TRAILER)
    struct.pack_into("<I", code, 0x00C0, MSG_ID_OK)
    # a small zero table, mirroring the real files' interior 0x00 run
    for i in range(0x0100, min(0x0100 + 128, len(code))):
        code[i] = 0x00
    buf[0x22:0x22 + code_len] = code

    # the u16 halfword-length field just below the epilogue, and (for the
    # three later identities) the 176-byte fixed-stride block after the
    # region it describes
    if ver in TRAILER_ERASED:
        struct.pack_into("<H", buf, 0x3EFC, 0xFFFF)
    else:
        # The field counts the region it terminates. For the three later
        # identities that region ends 176 bytes before the code end, because
        # the fixed-stride block follows it.
        described_end = code_end
        if ver in TRAILER_STRIDE_BLOCK:
            described_end = code_end - STRIDE_BLOCK_LEN
        struct.pack_into("<H", buf, 0x3EFC, (described_end // 2) - 1)
        if ver in TRAILER_STRIDE_BLOCK:
            base = code_end - STRIDE_BLOCK_LEN
            if base < 0x22:
                raise ValueError("stride block does not fit: 0x%x" % base)
            # MEASURED shape: 14-byte prologue + 8 x 20-byte records + 2-byte
            # tail. The 12-byte record body is identical in all 8 records;
            # field A advances by 10 and field B by 8 per record; the last 4
            # bytes are constant.
            prologue = counter_stream(b"cpp-fixture-stride-prologue",
                                      STRIDE_PROLOGUE_LEN)
            body = counter_stream(b"cpp-fixture-stride-body", STRIDE_BODY_LEN)
            tail = counter_stream(b"cpp-fixture-stride-tail", STRIDE_TAIL_LEN)
            buf[base:base + STRIDE_PROLOGUE_LEN] = prologue
            for k in range(STRIDE_RECORD_COUNT):
                off = base + STRIDE_PROLOGUE_LEN + k * STRIDE_RECORD_LEN
                buf[off:off + STRIDE_BODY_LEN] = body
                struct.pack_into("<H", buf, off + 12, 0xD338 + 0x0A * k)
                struct.pack_into("<H", buf, off + 14, 0x0700 + 8 * k)
                buf[off + 16:off + 20] = b"\x00\x80\x20\x64"
            tail_off = (base + STRIDE_PROLOGUE_LEN
                        + STRIDE_RECORD_COUNT * STRIDE_RECORD_LEN)
            buf[tail_off:tail_off + STRIDE_TAIL_LEN] = tail

    # the invariant epilogue and the trailing fill
    if has_epilogue:
        buf[EPILOGUE_START:EPILOGUE_END] = EPILOGUE

    return bytes(buf)


def build_broken():
    """Three deliberately-broken fixtures covering the error classes."""
    out = {}
    # not word-aligned: 16,383 bytes
    good = build_image(1, 5, 0)
    out["bad_size_synthetic.fw"] = good[:WINDOW - 1]
    # header unreadable: 16 bytes
    out["truncated_synthetic.fw"] = good[:16]
    # no payload at all: every byte is fill
    out["all_fill_synthetic.fw"] = b"\xff" * WINDOW
    return out


# ---------------------------------------------------------------- driver

def filename_for(major, minor, step):
    return "cpp_firmware_v%d_%d_%d.fw" % (major, minor, step)


def build_all(outdir=FIXTURE_DIR, verbose=False):
    """Materialise every fixture. Returns {name: (path, bytes, md5)}."""
    os.makedirs(outdir, exist_ok=True)
    manifest = {}
    for major, minor, step, total, code_end in LADDER:
        data = build_image(major, minor, step, total, code_end)
        name = filename_for(major, minor, step)
        path = os.path.join(outdir, name)
        with open(path, "wb") as f:
            f.write(data)
        manifest[name] = (path, len(data), hashlib.md5(data).hexdigest())
        if verbose:
            print("%-32s %6d  %s" % (name, len(data),
                                     hashlib.md5(data).hexdigest()))
    for name, data in build_broken().items():
        path = os.path.join(outdir, name)
        with open(path, "wb") as f:
            f.write(data)
        manifest[name] = (path, len(data), hashlib.md5(data).hexdigest())
        if verbose:
            print("%-32s %6d  %s" % (name, len(data),
                                     hashlib.md5(data).hexdigest()))
    return manifest


def main(argv):
    verbose = "-q" not in argv
    outdir = FIXTURE_DIR
    for i, a in enumerate(argv):
        if a == "--outdir" and i + 1 < len(argv):
            outdir = argv[i + 1]
    m = build_all(outdir, verbose=verbose)
    if verbose:
        print("\n%d fixtures written to %s" % (len(m), outdir))
        print("All bytes are SYNTHETIC (SHA-256 counter streams); no vendor "
              "payload is reproduced.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
