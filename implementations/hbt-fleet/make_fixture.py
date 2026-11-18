#!/usr/bin/env python3
"""make_fixture.py — build SYNTHETIC fixtures from the documented structures
only (no real payload bytes). Generates:

  fixtures/hgen_patch.tlv   h-generation-style rampatch: TLV_TYPE_PATCH
                            container, 24-byte tlv_type_patch header with
                            product_id=19 / signature_algorithm=0, tiny body,
                            44-byte footer {0x04040202, 0x05ca0404 + 36B}
                            (real prologue is build-varying; fixture uses the
                            r0s-build values)
  fixtures/crap_patch.tlv   cr/ap-generation-style rampatch: product_id=10,
                            signature_algorithm=2, reserved2=0x8000, real
                            entry, 256-byte signature-class tail
  fixtures/hgen_nvm.bin     bare type-2 NVM (no enclosing/trailing records)
                            with a 12-byte-prefix tag stream incl. tag 2
                            (BD_ADDR, 6B), tag 17 (HCI, 6B), tag 27 (9B)
  fixtures/crap_nvm.bin     cr/ap-style NVM: type-4 enclosing + type-2 set +
                            trailing type-3 record

Run:  python3 make_fixture.py            (writes into ./fixtures/)
"""

import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, 'fixtures')


def w(fi, name, data):
    os.makedirs(FIX, exist_ok=True)
    p = os.path.join(FIX, name)
    with open(p, 'wb') as f:
        f.write(data)
    print(f'wrote {p} ({len(data)} bytes)')
    return p


def make_hgen_patch():
    body = bytes(range(256)) * 4  # 1024-byte pseudo body (synthetic)
    footer = struct.pack('<II', 0x04040202, 0x05ca0404) + bytes(36)
    data_length = len(body)
    total_size = data_length + 24 + 12  # h-generation arithmetic: +36 total
    hdr = struct.pack('<II4BHHHHI', total_size, data_length, 1, 0, 3, 0,
                      19, 0x0200, 0x3d71, 0x0, 0x0)
    file_len = 4 + 24 + data_length + len(footer)
    return struct.pack('<I', (file_len - 4) << 8 | 1) + hdr + body + footer


def make_crap_patch():
    body = bytes(range(256)) * 4
    tail = bytes(256)  # signature-class tail placeholder (zeros here; real
    # files are high-entropy — fixture only checks LENGTH/ARITHMETIC)
    data_length = len(body)
    total_size = data_length + 24  # cr/ap arithmetic: total = data + 24
    hdr = struct.pack('<II4BHHHHI', total_size, data_length, 1, 2, 3, 0,
                      10, 0x0200, 0x0002, 0x8000, 0x0001b0e0)
    file_len = 4 + 24 + data_length + len(tail)
    return struct.pack('<I', (file_len - 4) << 8 | 1) + hdr + body + tail


def nvm_records(tags):
    """tags: list of (id, bytes) -> packed 12-byte-prefix records."""
    out = b''
    for tid, payload in tags:
        out += struct.pack('<HHII', tid, len(payload), 0, 0) + payload
    return out


def make_hgen_nvm():
    tags = [
        (2, bytes.fromhex('0123456789ab')),       # BD_ADDR, 6 B
        (17, bytes.fromhex('806400000000')),      # HCI/inband, 6 B (h-gen len)
        (27, bytes(9)),                            # deep sleep, 9 B (h-gen len)
        (35, bytes(120)),                          # unknown-to-kernel tag
        (206, b'\x01\x02'),                        # extended-id tag (>150)
    ]
    set_body = nvm_records(tags)
    # bare type-2: [0,4) = {type=2, len} little-endian word
    return struct.pack('<I', (len(set_body) << 8) | 2) + set_body


def make_crap_nvm():
    tags = [
        (2, bytes.fromhex('cdef01234567')),
        (17, bytes.fromhex('8064000000') + b'\x00\x00\x00\x00'),  # 9 B
        (27, b'\x01'),                                             # 1 B
    ]
    set_body = nvm_records(tags)
    type3 = struct.pack('<I', (943 << 8) | 3) + bytes(943)
    return (struct.pack('<I', ((4 + 4 + len(set_body) + len(type3) - 4) << 8) | 4)
            + struct.pack('<I', (len(set_body) << 8) | 2)
            + set_body + type3)


if __name__ == '__main__':
    w(None, 'hgen_patch.tlv', make_hgen_patch())
    w(None, 'crap_patch.tlv', make_crap_patch())
    w(None, 'hgen_nvm.bin', make_hgen_nvm())
    w(None, 'crap_nvm.bin', make_crap_nvm())
    print('all fixtures written')
