#!/usr/bin/env python3
"""make_fixture.py — deterministic synthetic-fixture generator for the
clean-room gen-2 ("h-prefix") QCA BT TLV probe (hp_fleet_probe.py).

Every byte here is SELF-MADE from the documented field layout (linux
btqca.h / btqca.c, GPL-2.0-only, fetched from torvalds/linux master
2026-11-18) plus the *measured* gen-2 header/trailer sizes (32-byte vendor
header, 4-byte tag + 32-byte SHA-256 trailer). No Qualcomm firmware bytes
are present in this repository or were used to produce these files — the
real fleet payloads live only in scratch space and were never copied in.

Regeneration is byte-exact: every byte is a deterministic SHA-256
counter-stream (tagged per fixture), and the trailer is a real SHA-256 over
the fixture's own bytes, so re-running reproduces every file bit-for-bit.
The test suite verifies that.

Fixtures written (sizes mirror the real fleet magnitudes):

  fixtures/hpbtfw20_synthetic.tlv      gen-2 patch, rom_build 0x0200 ->
                                       filename digit "20", product_id 19
                                       (QCA2066), download_mode 3, 201,560 B
  fixtures/hpbtfw21_synthetic.tlv      same family, rom_build 0x0201 -> "21",
                                       146,068 B
  fixtures/hmtbtfw20_synthetic.tlv     gen-2 patch, product_id 25 (WCN7850),
                                       rom_build 0x0200, 280,628 B
  fixtures/hpbtfw20_gen1_synthetic.tlv GEN-1 (F-75 cr/ap) layout: 24-byte
                                       header + 256-byte tail, to prove the
                                       probe distinguishes the generations
  fixtures/hpnv20_synthetic.bin        single-set NVM (type 2), 6,319 B, with
                                       the three kernel-known tags 2/17/27
  fixtures/hmtnv20_synthetic.bin       single-set NVM, 9,508 B
  fixtures/hpnv20_multi_synthetic.bin  type-4 enclosing header + two type-2
                                       sets + a trailing type-3 record
  fixtures/hpbtfw20_badtrailer.tlv     gen-2 patch whose SHA-256 trailer is
                                       intentionally wrong (error path)
  fixtures/hpbtfw20_truncated.tlv      gen-2 patch whose type_len declares
                                       more than the file holds (error path)
"""

import hashlib
import os
import struct
import sys

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures")

# documented constants (btqca.h)
TLV_TYPE_PATCH = 1
TLV_TYPE_NVM = 2
ELF_TYPE_PATCH = 3
TLV_TYPE_MULTI_NVM_ENCLOSING = 4

PATCH_HDR = struct.Struct("<II BBBB HHHH I")     # 24-byte upstream struct
NVM_TAG_HDR = struct.Struct("<HH II")            # 12-byte tag prefix

# measured gen-2 constants (see hp_fleet_probe.py docstring)
GEN1_HDR = 24
GEN1_TRAILER = 256
GEN2_HDR = 32
GEN2_TAG = 4
GEN2_DIGEST = 32
GEN2_TRAILER = GEN2_TAG + GEN2_DIGEST          # 36

# real fleet sizes from blob-matrix/laptop/sharing-clusters.csv
FLEET_SIZES = {
    "hpbtfw20.tlv": 201560,
    "hpbtfw21.tlv": 146068,
    "hpbtfw10.tlv": 178532,
    "hmtbtfw20.tlv": 280628,
    "hmtbtfw10.tlv": 91308,
    "hpnv20.bin": 6319,
    "hmtnv20.bin": 9508,
}


def pattern(n, tag):
    """Deterministic pseudo-random stream: SHA-256 of a counter, tagged per
    fixture so unrelated fixtures never share payload bytes."""
    tag = tag.encode() if isinstance(tag, str) else tag
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(b"%s:%d" % (tag, counter)).digest()
        counter += 1
    return bytes(out[:n])


def tlv_header(type_, length):
    """struct tlv_type_hdr: type in the LOW byte, length in bits 8..31."""
    return struct.pack("<I", ((length & 0xFFFFFF) << 8) | (type_ & 0xFF))


def gen2_patch(tag, file_size, product_id, rom_build, patch_version=0x3ED8,
               download_mode=3, entry_tag=0x00000000, break_digest=False,
               truncate=False):
    """Build a gen-2 patch container from the measured layout:

        [0,4)                        tlv_type_hdr (type=1, len=file-4)
        [4,36)                       32-byte vendor header
          [4,28)                       upstream tlv_type_patch (24 B)
          [28,36)                      vendor extension (8 B; entries are
                                       all zero on every measured gen-2 file)
        [36, 36+data_length)         patch body (opaque)
        [36+data_length, file)       36-byte trailer
          first 4 B                    tag (inside the digested span)
          last 32 B                    SHA-256 over file[4 : file-32]

    total_size covers the type_len word + header + payload, i.e.
    data_length + 4 + 32 — matching every measured gen-2 file.
    """
    tag = tag.encode() if isinstance(tag, str) else tag
    data_length = file_size - 4 - GEN2_HDR - GEN2_TRAILER
    if data_length < 0:
        raise ValueError("file_size too small for the gen-2 layout")
    body = pattern(data_length, tag)
    total_size = 4 + GEN2_HDR + data_length
    hdr24 = PATCH_HDR.pack(total_size, data_length,
                           1,             # format_version
                           0,             # signature algorithm
                           download_mode,
                           0,             # reserved1
                           product_id,
                           rom_build,
                           patch_version,
                           0,             # reserved2
                           entry_tag)
    assert len(hdr24) == 24
    ext = struct.pack("<II", 0, 0)          # vendor extension, always zero
    head = tlv_header(TLV_TYPE_PATCH, file_size - 4) + hdr24 + ext + body
    assert len(head) == file_size - GEN2_TRAILER, (len(head), file_size)

    # The 4-byte tag is the FIRST word of the trailer but the LAST word of
    # the digested span: the digest covers file[4 : file_size-32], i.e.
    # head[4:] plus the tag. (Verified on all 14 measured gen-2 files.)
    tag_bytes = pattern(GEN2_TAG, tag + b":tag")
    digest = hashlib.sha256(head[4:] + tag_bytes).digest()
    if break_digest:
        digest = bytes(32)                  # all-zero digest: must be caught
    out = head + tag_bytes + digest
    assert len(out) == file_size
    if truncate:
        out = out[:file_size - 40]          # chop 40 bytes off the tail
    return out


def gen1_patch(tag, file_size, product_id, rom_build, patch_version=0x0002):
    """Build a GEN-1 (F-75 cr/ap) patch container, so the probe can be shown
    to tell the two generations apart: 24-byte header + 256-byte tail."""
    tag = tag.encode() if isinstance(tag, str) else tag
    data_length = file_size - 4 - GEN1_HDR - GEN1_TRAILER
    body = pattern(data_length, tag)
    hdr = PATCH_HDR.pack(data_length + GEN1_HDR, data_length,
                         1, 2, 3, 0, product_id, rom_build, patch_version,
                         0x8000, 0x000209E4)
    out = tlv_header(TLV_TYPE_PATCH, file_size - 4) + hdr + body + \
        pattern(GEN1_TRAILER, tag + b":sig")
    assert len(out) == file_size, (len(out), file_size)
    return out


def tag_record(tag_id, data):
    """tlv_type_nvm: tag_id LE16 + tag_len LE16 + reserve1 + reserve2 + data."""
    return NVM_TAG_HDR.pack(tag_id, len(data), 0, 0) + data


def make_nvm(tag, file_size, bd_addr=b"\x02\x00\x5e\x10\x00\x00"):
    """Single-set NVM at an exact fleet-magnitude size. Tag plan:

      2  BD address      (kernel: tag_len must be 6; RFC 7042 documentation
                          address — no real address)
      17 HCI transport   (kernel: >=3 bytes, data[0]|=0x80, baud byte)
      27 deep-sleep      (kernel: >=1 byte, data[0]|=0x01)
      rest opaque filler (unknown to upstream — proves opaque handling)
    """
    tag = tag.encode() if isinstance(tag, str) else tag
    set_len_target = file_size - 4
    tags = bytearray()
    tags += tag_record(2, bd_addr)
    tags += tag_record(17, pattern(6, tag + b":hci"))
    tags += tag_record(27, pattern(9, tag + b":ds"))
    counter = 0
    filler_ids = [0x20 + (i % 0x60) for i in range(256)]
    while True:
        remaining = set_len_target - len(tags)
        if remaining == 0:
            break
        if remaining <= 80:
            assert remaining >= NVM_TAG_HDR.size, "unreachable gap %d" % remaining
            tags += tag_record(filler_ids[counter % len(filler_ids)],
                               pattern(remaining - NVM_TAG_HDR.size,
                                       tag + b":fill%d" % counter))
            break
        n = 16 + (counter % 6) * 8
        tags += tag_record(filler_ids[counter % len(filler_ids)],
                           pattern(n, tag + b":fill%d" % counter))
        counter += 1
    assert len(tags) == set_len_target, (len(tags), set_len_target)
    return tlv_header(TLV_TYPE_NVM, len(tags)) + bytes(tags)


def make_nvm_multi(tag):
    """Type-4 enclosing header + two adjacent type-2 sets + a trailing
    type-3 record (the shape F-75 found on crnv20/crnv11/apnv10)."""
    tag = tag.encode() if isinstance(tag, str) else tag
    set1 = (tag_record(2, b"\x02\x00\x5e\x10\x00\x01")
            + tag_record(17, pattern(6, tag + b":hci"))
            + tag_record(27, b"\x01"))
    set2 = tag_record(1, b"SET-B") + tag_record(17, b"\x80\x0d\x00\x00")
    trailer = pattern(60, tag + b":t3")
    out = tlv_header(TLV_TYPE_MULTI_NVM_ENCLOSING, 0)
    out += tlv_header(TLV_TYPE_NVM, len(set1)) + set1
    out += tlv_header(TLV_TYPE_NVM, len(set2)) + set2
    out += tlv_header(3, len(trailer)) + trailer   # the type-3 record
    return out


def main():
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    jobs = [
        # gen-2 rampatches at real fleet magnitudes
        ("hpbtfw20_synthetic.tlv",
         gen2_patch("hpbtfw20-synthetic", FLEET_SIZES["hpbtfw20.tlv"],
                    product_id=19, rom_build=0x0200,
                    patch_version=0x3ED8)),
        ("hpbtfw21_synthetic.tlv",
         gen2_patch("hpbtfw21-synthetic", FLEET_SIZES["hpbtfw21.tlv"],
                    product_id=19, rom_build=0x0201,
                    patch_version=0x5E81)),
        ("hmtbtfw20_synthetic.tlv",
         gen2_patch("hmtbtfw20-synthetic", FLEET_SIZES["hmtbtfw20.tlv"],
                    product_id=25, rom_build=0x0200,
                    patch_version=0x694D, entry_tag=0x00020010)),
        # a gen-1 file, to prove the probe distinguishes the generations
        ("hpbtfw20_gen1_synthetic.tlv",
         gen1_patch("hpbtfw20-gen1-synthetic", 56180, product_id=19,
                    rom_build=0x0200)),
        # NVMs at real fleet magnitudes
        ("hpnv20_synthetic.bin",
         make_nvm("hpnv20-synthetic", FLEET_SIZES["hpnv20.bin"])),
        ("hmtnv20_synthetic.bin",
         make_nvm("hmtnv20-synthetic", FLEET_SIZES["hmtnv20.bin"])),
        ("hpnv20_multi_synthetic.bin", make_nvm_multi("hpnv20-multi")),
        # error-path fixtures
        ("hpbtfw20_badtrailer.tlv",
         gen2_patch("hpbtfw20-badtrailer", FLEET_SIZES["hpbtfw20.tlv"],
                    product_id=19, rom_build=0x0200, break_digest=True)),
        ("hpbtfw20_truncated.tlv",
         gen2_patch("hpbtfw20-trunc", FLEET_SIZES["hpbtfw20.tlv"],
                    product_id=19, rom_build=0x0200, truncate=True)),
    ]
    written = []
    for name, blob in jobs:
        path = os.path.join(FIXTURE_DIR, name)
        with open(path, "wb") as f:
            f.write(blob)
        written.append((name, len(blob)))
    for name, n in written:
        print("%-34s %8d bytes" % (name, n))
    print("\nreal fleet sizes: " + " ".join(
        "%s=%d" % (k, v) for k, v in sorted(FLEET_SIZES.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
