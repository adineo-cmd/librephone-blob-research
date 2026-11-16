#!/usr/bin/env python3
"""make_fixture.py — generate synthetic MediaTek container fixtures.

CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16
(see mtk_container.py header for the full list). The fixture bytes are
entirely self-made from the documented field layout — no proprietary
material was accessed; every payload byte is deterministic filler derived
from SHA-256 of the record name, exercising the documented structure only.

Fixtures (written next to this script under fixtures/):
  mtk_chain_fixture.bin      mtk_hdr signed record chain: a 20-char-name
                             code record, an unsigned modem-data record, a
                             no-extension record, and a code record followed
                             by a cert1 (1,709 B) + cert2 (957 B) DER-shaped
                             signature pair.
  gfh_preloader_fixture.bin  GFH MMM chain with the rosemary preloader's
                             documented record set {FILE_INFO, BL_INFO,
                             ANTI_CLONE, BL_SEC_KEY, BROM_CFG, BROM_SEC_CFG}
                             and the census's documented preloader field
                             values.
  gfh_md1dsp_fixture.bin     GFH MMM chain with FILE_INFO (sig_type=0,
                             load_addr=0xFFFFFFFF) + record type 260 (0x104),
                             as documented for md1dsp (F-36).

Usage: python3 make_fixture.py [outdir]
"""

import hashlib
import os
import struct
import sys

MTK_HDR_MAGIC = 0x58881688
MTK_EXT_MAGIC = 0x58891689
CERT1_SIZE = 1709
CERT2_SIZE = 957

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def filler(name, size):
    """Deterministic self-made payload bytes (structure only, no content).
    Guard: the stream is forced NOT to start with the DER SEQUENCE prefix
    (30 82) so non-signature records can never be misclassified."""
    out = bytearray()
    seed = name.encode()
    while len(out) < size:
        out.extend(hashlib.sha256(seed + len(out).to_bytes(4, "little")).digest())
    if out[:2] == b"\x30\x82":
        out[0] ^= 0x01
    return bytes(out[:size])


def mtk_record(name, payload, align=0x10, with_ext=True, ext_flag=0):
    """Build one mtk_hdr record (512-B header [+ ext fields] + payload,
    padded to the alignment per the documented next-record rule)."""
    hdr = bytearray(0x200)
    struct.pack_into("<II", hdr, 0x00, MTK_HDR_MAGIC, len(payload))
    nb = name.encode("ascii")[:0x20]
    hdr[0x08:0x08 + len(nb)] = nb  # NUL-padded ASCII name @0x08 (>=20 B names)
    if with_ext:
        struct.pack_into("<IIII", hdr, 0x30, MTK_EXT_MAGIC, 0x200, ext_flag, 0)
        struct.pack_into("<I", hdr, 0x44, align)
    blob = bytes(hdr) + payload
    pad = (-len(payload)) % align
    return blob + b"\x00" * pad


def der_shaped(size):
    """A DER-looking SEQUENCE: 30 82 <u16 len> + filler. Self-made."""
    body = filler("der", size - 4)
    return b"\x30\x82" + struct.pack(">H", size - 4) + body


def build_mtk_chain():
    """Chain layout (all bytes self-made; names/sizes chosen to exercise
    the documented layout rules, not copied from any real image):"""
    recs = []
    # 20-byte name (the documented MT6785 minimum name width), signed pair:
    recs.append(mtk_record("tinysys-loader-CM4_A", filler("tinysys-loader-CM4_A", 1080)))
    recs.append(mtk_record("cert1", der_shaped(CERT1_SIZE)))
    recs.append(mtk_record("cert2", der_shaped(CERT2_SIZE)))
    # unsigned modem data payload (documented unsigned class):
    recs.append(mtk_record("md1_file_map", filler("md1_file_map", 4096)))
    # a record without the 0x58891689 extension record (alignment defaults
    # to the documented 0x10 when the ext record is absent):
    recs.append(mtk_record("tiny-stub", filler("tiny-stub", 17), with_ext=False))
    # second signed pair:
    recs.append(mtk_record("spmfw", filler("spmfw", 2048)))
    recs.append(mtk_record("cert1", der_shaped(CERT1_SIZE)))
    recs.append(mtk_record("cert2", der_shaped(CERT2_SIZE)))
    return b"".join(recs)


# --- GFH fixtures (field values documented in the rosemary census) ---

def gfh_record(rtype, body):
    """gfh_common_header: magic[3]='MMM', version u8=1, size u16, type u16."""
    size = 8 + len(body)
    return struct.pack("<3sBHH", b"MMM", 1, size, rtype) + body


def gfh_file_info(name="FILE_INFO", file_type=1, flash_type=5, sig_type=5,
                  load_addr=0x00200F10, total_size=0x55134, max_size=0x55134,
                  hdr_size=0x100, sig_size=0x800, jump_offset=0xF0, processed=0):
    """U-Boot gfh_file_info field order; rosemary preloader values per census."""
    body = bytearray(48)
    nb = name.encode("ascii")[:12]
    body[0:0 + len(nb)] = nb
    struct.pack_into("<I", body, 12, 0)          # unused
    struct.pack_into("<H", body, 16, file_type)  # u16
    body[18] = flash_type                        # u8
    body[19] = sig_type                          # u8
    struct.pack_into("<IIIIIII", body, 20, load_addr, total_size, max_size,
                     hdr_size, sig_size, jump_offset, processed)
    return gfh_record(0, bytes(body))


def build_gfh_preloader():
    recs = [
        gfh_file_info(),
        gfh_record(1, struct.pack("<I", 1)),                       # BL_INFO attr=1
        gfh_record(2, struct.pack("<BBHII", 0, 0, 0, 0, 0)),       # ANTI_CLONE
        gfh_record(3, b"\x00" * 0x20C),                            # BL_SEC_KEY (opaque)
        gfh_record(7, struct.pack("<II", 0x90, 0) + b"\x00" * 0x45
                   + bytes([0]) + b"\x00" * 2                      # jump_bl_arm64 = 0 (census: no ARM64 hand-off flag)
                   + struct.pack("<III", 0, 0, 0)),                # BROM_CFG cfg_bits=0x90 (+ trailing pad)
        gfh_record(8, struct.pack("<I", 0) + b"LIBREPHONE".ljust(0x20, b"\x00")
                   + struct.pack("<I", 0)),                        # BROM_SEC_CFG
    ]
    return b"".join(recs)


def build_gfh_md1dsp():
    """md1dsp GFH: FILE_INFO with sig_type=0, load_addr=0xFFFFFFFF (F-36)
    followed by record type 260 (0x104), absent from U-Boot's enum."""
    recs = [
        gfh_file_info(name="FILE_INFO", file_type=1, flash_type=5, sig_type=0,
                      load_addr=0xFFFFFFFF, total_size=0x678000,
                      max_size=0x678000, hdr_size=0x100, sig_size=0,
                      jump_offset=0),
        gfh_record(260, filler("md1dsp-260", 64)),  # body opaque per spec
    ]
    return b"".join(recs)


def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fixtures")
    os.makedirs(outdir, exist_ok=True)
    fixtures = {
        "mtk_chain_fixture.bin": build_mtk_chain(),
        "gfh_preloader_fixture.bin": build_gfh_preloader(),
        "gfh_md1dsp_fixture.bin": build_gfh_md1dsp(),
    }
    for fn, blob in fixtures.items():
        path = os.path.join(outdir, fn)
        with open(path, "wb") as fh:
            fh.write(blob)
        print("%s  %d bytes" % (path, len(blob)))


if __name__ == "__main__":
    main()
