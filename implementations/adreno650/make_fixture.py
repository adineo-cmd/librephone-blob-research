#!/usr/bin/env python3
"""make_fixture.py — build SYNTHETIC fixtures for the a650-generation GMU/SQE
structures documented in a650-gmu-analysis.md (no real payload bytes).

  fixtures/a650_gmu.bin     block-chain GMU image: zero-size manifest blocks
                            (type 1, value = region size), payload blocks
                            tagged type=value 0xEFBEADDE ("DEADBEEF" byte
                            pattern) in the ITCM / icache / DTCM windows
  fixtures/a619_gmu.bin     legacy raw 0x8000 ITCM-class image (code at 0,
                            zero padding to 32768)
  fixtures/a650_sqe_ok.fw   SQE file: lead dword 0x00000000 + version dword
                            passing the a650 (>= 0x095) driver check
  fixtures/a650_sqe_old.fw  SQE file with version bits < 0x095 (fails the
                            check, as the real device fleet build 0x093 does)

Run:  python3 make_fixture.py            (writes into ./fixtures/)
"""

import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, 'fixtures')


def w(name, data):
    os.makedirs(FIX, exist_ok=True)
    p = os.path.join(FIX, name)
    with open(p, 'wb') as f:
        f.write(data)
    print(f'wrote {p} ({len(data)} bytes)')
    return p


def make_a650_gmu():
    """Block chain per a6xx_gmu.c struct block_header + NEXT_BLK."""
    out = b''
    out += struct.pack('<IIII', 0x00000000, 0, 1, 0x200)      # marker
    out += struct.pack('<IIII', 0x00000200, 0, 1, 0x200)      # marker
    itcm = bytes.fromhex('00bf10b5') * 64                     # Thumb-ish
    out += struct.pack('<IIII', 0x00000400, len(itcm), 0xEFBEADDE, 0xEFBEADDE) + itcm
    dtcm = b'\xa1\x02' * 32
    out += struct.pack('<IIII', 0x10004000, len(dtcm), 0xEFBEADDE, 0xEFBEADDE) + dtcm
    bo = b'\x03\x04\x05\x06' * 64
    out += struct.pack("<IIII", 0x144000, len(bo), 0xEFBEADDE, 0xEFBEADDE) + bo  # icache window
    out += struct.pack('<IIII', 0x10007fdc, 24, 0xEFBEADDE, 0xEFBEADDE) \
        + bytes(24)
    return out


def make_a619_gmu():
    # leading words mirror the documented real-file pattern:
    # 0x00043f80, 0x00000009, then Thumb-pair words
    code = bytes.fromhex('803f040009000000054880f308880548') * 64
    img = bytearray(0x8000)
    img[:len(code)] = code
    return bytes(img)


def make_sqe(version_bits, lead=0x00000000):
    ver = 0x0016dd000 | version_bits
    body = bytes.fromhex('00bf00bf00bf4908') * 64
    return struct.pack('<II', lead, ver) + body


if __name__ == '__main__':
    w('a650_gmu.bin', make_a650_gmu())
    w('a619_gmu.bin', make_a619_gmu())
    w('a650_sqe_ok.fw', make_sqe(0x112))
    w('a650_sqe_old.fw', make_sqe(0x093))
    print('all fixtures written')
