#!/usr/bin/env python3
"""make_fixture.py — generate synthetic md1dsp interface fixtures.

CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16
(see md32_interface.py header). All fixture bytes are self-made from the
documented layout; the only spec constants embedded are the DOCUMENTED
field values (F-36/F-45): DSP! header fields, the three descriptor
records, the two USIP sample records, and the six RAKE chain records
(offsets, lengths, crc32 constants) — facts, not payload content.

Two fixtures:
  md1dsp_header_fixture.bin  (~1.4 KB, committed): GFH prefix + DSP! header
                             + descriptor table + USIP + RAKE records.
  md1dsp_full_fixture.bin    (0x60a9d0 B, generated into a scratch dir at
                             test time, NOT committed): the same layout
                             with real bytes at every RAKE chain region,
                             each region's tail forged so its crc32 equals
                             the DOCUMENTED F-45 constant — exercising the
                             parser's crc32 verification end-to-end.

Usage: python3 make_fixture.py [outdir]   (writes the small fixture)
       python3 make_fixture.py --full <outdir>  (writes both)
"""

import hashlib
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import md32_interface as mi  # noqa: E402


def filler(tag, off, size):
    """Deterministic self-made bytes (structure only)."""
    out = bytearray()
    seed = tag.encode()
    pos = off
    while len(out) < size:
        out.extend(hashlib.sha256(seed + pos.to_bytes(8, "little")).digest())
        pos += 32
    return bytes(out[:size])


def crc32_forge(prefix, target):
    """Return 4 bytes b s.t. zlib.crc32(prefix + b) == target.

    crc32 is GF(2)-affine in the message bits for fixed length (the
    table is multiplication by the generator polynomial), so the 32-bit
    suffix is found by a 32x32 GF(2) solve over basis vectors.
    """
    def raw(data):
        return zlib.crc32(data) ^ 0xFFFFFFFF

    base = prefix + b"\x00\x00\x00\x00"
    c0 = raw(base)
    cols = []
    for k in range(32):
        m = bytearray(base)
        m[len(prefix) + (k >> 3)] ^= 1 << (k & 7)
        cols.append(raw(bytes(m)) ^ c0)
    rhs = (target ^ 0xFFFFFFFF) ^ c0
    rows = [[(cols[k] >> j) & 1 for k in range(32)] + [(rhs >> j) & 1]
            for j in range(32)]
    pivots = []
    r = 0
    for col in range(32):
        sel = next((i for i in range(r, 32) if rows[i][col]), None)
        if sel is None:
            continue
        rows[r], rows[sel] = rows[sel], rows[r]
        for i in range(32):
            if i != r and rows[i][col]:
                rows[i] = [a ^ b for a, b in zip(rows[i], rows[r])]
        pivots.append(col)
        r += 1
    sol = [0] * 32
    for i, col in enumerate(pivots):
        sol[col] = rows[i][32]
    b = bytearray(4)
    for k in range(32):
        if sol[k]:
            b[k >> 3] |= 1 << (k & 7)
    return bytes(b)


def gfh_file_info():
    """GFH FILE_INFO with the F-36-documented md1dsp values."""
    body = bytearray(48)
    body[0:9] = b"FILE_INFO"
    struct.pack_into("<H", body, 16, 1)          # file_type
    body[18] = 5                                  # flash_type
    body[19] = 0                                  # sig_type = 0 (F-36)
    struct.pack_into("<IIIIIII", body, 20,
                     0xFFFFFFFF,   # load_addr (F-36)
                     0x678000,     # total_size (F-36)
                     0x678000, 0x100, 0, 0, 0)
    return struct.pack("<3sBHH", b"MMM", 1, 56, 0) + bytes(body)


def build_header_fixture():
    buf = bytearray(0x580)
    # GFH prefix: FILE_INFO (56 B) + one type-260 record sized so the
    # prefix ends exactly at the documented DSP! magic offset 0x118.
    buf[0:56] = gfh_file_info()
    r260_size = mi.DSP_MAGIC_OFFSET - 56
    struct.pack_into("<3sBHH", buf, 56, b"MMM", 1, r260_size, 260)
    buf[64:mi.DSP_MAGIC_OFFSET] = filler("md1dsp-260", 64, r260_size - 8)

    # DSP! header — F-45 absolute readings used for marker/chip (the
    # later, re-verified doc); F-36-only fields (asic/build) at their
    # documented relative positions.
    buf[mi.DSP_MAGIC_OFFSET:mi.DSP_MAGIC_OFFSET + 4] = b"DSP!"
    struct.pack_into("<I", buf, mi.DSP_SIZE_OFFSET, 0x678000)
    struct.pack_into("<I", buf, mi.DSP_VERSION_OFFSET, 1)
    struct.pack_into("<I", buf, mi.MARKER_F45, 0x12345678)
    buf[mi.CHIP_F45:mi.CHIP_F45 + 6] = b"MT6785"
    buf[mi.ASIC_OFFSET:mi.ASIC_OFFSET + 12] = b"DEFAULT_ASIC"
    build = b"MOLY.LR13.R1.MP.V89.6.P79"
    buf[mi.BUILD_OFFSET:mi.BUILD_OFFSET + len(build)] = build

    # descriptor table @0x248: three documented 16-B records
    for i, (off, ln, rsv, tag) in enumerate(mi.DESCRIPTOR_EXPECTED):
        o = mi.DESCRIPTOR_TABLE_OFFSET + 16 * i
        struct.pack_into("<IIII", buf, o, off, ln, rsv, tag)

    # USIP: tag @0x274, body @0x278 with the two documented sample records
    buf[mi.USIP_TAG_OFFSET:mi.USIP_TAG_OFFSET + 4] = b"USIP"
    for i, rec in enumerate(mi.USIP_SAMPLES):
        o = mi.USIP_BODY_OFFSET + 16 * i
        struct.pack_into("<IIII", buf, o, *rec)

    # RAKE: tag @0x4b4, six documented records (w0 opaque = 0)
    buf[mi.RAKE_TAG_OFFSET:mi.RAKE_TAG_OFFSET + 4] = b"RAKE"
    for i, (off, ln, crc) in enumerate(mi.RAKE_CHAIN_EXPECTED):
        o = mi.RAKE_TAG_OFFSET + 4 + 16 * i
        struct.pack_into("<IIII", buf, o, 0, off, ln, crc)
    return bytes(buf)


def build_full_fixture():
    """Header fixture + real bytes in every RAKE region, each region's
    crc32 forged to the DOCUMENTED F-45 constant."""
    buf = bytearray(build_header_fixture())
    end = max(off + ln for off, ln, _ in mi.RAKE_CHAIN_EXPECTED)
    buf.extend(filler("md1dsp-body", len(buf), end - len(buf)))
    for off, ln, crc in mi.RAKE_CHAIN_EXPECTED:
        region = bytearray(buf[off:off + ln])
        head = bytes(region[:-4])
        tail = crc32_forge(head, crc)
        patched = head + tail
        assert zlib.crc32(patched) & 0xFFFFFFFF == crc
        buf[off:off + ln] = patched
    return bytes(buf)


def main():
    args = [a for a in sys.argv[1:]]
    full = "--full" in args
    if full:
        args.remove("--full")
    outdir = args[0] if args else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures")
    os.makedirs(outdir, exist_ok=True)
    small = os.path.join(outdir, "md1dsp_header_fixture.bin")
    with open(small, "wb") as fh:
        fh.write(build_header_fixture())
    print("%s  %d bytes" % (small, len(build_header_fixture())))
    if full:
        blob = build_full_fixture()
        path = os.path.join(outdir, "md1dsp_full_fixture.bin")
        with open(path, "wb") as fh:
            fh.write(blob)
        print("%s  %d bytes (scratch; do not commit)" % (path, len(blob)))


if __name__ == "__main__":
    main()
