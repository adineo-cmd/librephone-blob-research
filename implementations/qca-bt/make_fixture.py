#!/usr/bin/env python3
"""make_fixture.py — deterministic synthetic-fixture generator for the
clean-room QCA BT TLV parser (qca_tlv.py).

No Qualcomm Bluetooth firmware exists on this machine (checked 2026-11-16:
no crbtfw/apbtfw/crnv/apnv payloads anywhere in the home tree; the
coverage-matrix carries their md5s but the payloads are NOT on this box —
see README.md, fleet scope), so per the lab's mediatek/container precedent
the fixtures are **synthetic, self-made bytes** generated from the
documented field layout alone (linux btqca.h / btqca.c, GPL-2.0-only,
fetched from torvalds/linux master 2026-11-16). They prove the parser
against the documented layout, not against real firmware. A real fleet
file can be dropped in any time: `python3 -I qca_tlv.py crbtfw20.tlv`.

Every byte is deterministic (SHA-256 counter-stream pattern); regenerating
reproduces the committed/working-tree fixtures byte-exactly, which the
test suite verifies.

Fixtures written (sizes chosen to mirror the fleet magnitudes in
coverage-matrix.csv — crbtfw20.tlv = 56,180 B; crnv20.bin = 3,936 B;
apnv10.bin = 1,243 B):

  fixtures/crbtfw20_synthetic.tlv   patch container, type 1, download_mode
                                    QCA_SKIP_EVT_VSE_CC(3), rom_build 0x0200
  fixtures/crnv20_synthetic.bin     single-set NVM (type 2) with the three
                                    kernel-known tags (2/17/27) + opaque tags
  fixtures/apnv10_synthetic.bin     single-set NVM, apnv10 fleet size
  fixtures/nvm_multi_synthetic.bin  type-4 enclosing header + two type-2
                                    sets + trailing bytes (multi-NVM path)
  fixtures/crbtfw20_truncated.tlv   patch whose type_len declares more than
                                    the file holds (error-path fixture)
  fixtures/msbtfw11_synthetic.mbn   raw ELF rampatch (WCN6750 primary path;
                                    NOT TLV-wrapped) — kernel reads bytes
                                    4..6 of the file itself
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
PATCH_HDR = struct.Struct("<II BBBB HHHH I")     # 24 bytes, little-endian
NVM_TAG_HDR = struct.Struct("<HH II")            # 12-byte prefix

FLEET_SIZES = {                    # from upstream-contribution/blob-database/
    "crbtfw20.tlv": 56180,         # coverage-matrix.csv (md5 16077492…)
    "crnv20.bin": 3936,            # (md5 bb6ca169…)
    "apnv10.bin": 1243,            # (md5 4905d516…)
}


def pattern(n, tag):
    """Deterministic pseudo-random byte stream: SHA-256 of a counter, tagged
    per fixture so unrelated fixtures never share payload bytes."""
    tag = tag.encode() if isinstance(tag, str) else tag
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(b"%s:%d" % (tag, counter)).digest()
        counter += 1
    return bytes(out[:n])


def tlv_header(type_, length):
    """struct tlv_type_hdr: type in the LOW byte, length in bits 8..31
    (btqca.c:370-371)."""
    return struct.pack("<I", ((length & 0xFFFFFF) << 8) | (type_ & 0xFF))


def make_patch(tag, file_size=56180, download_mode=3, product_id=21,
               rom_build=0x0200, patch_version=0x89FD, entry=0x00020000,
               truncate=False):
    tag = tag.encode() if isinstance(tag, str) else tag
    """Patch container: 4-byte TLV hdr + 24-byte tlv_type_patch + payload."""
    payload_len = file_size - 4 - PATCH_HDR.size
    payload = pattern(payload_len, tag)
    # total_size = file size; data_length = bytes after the patch header
    hdr = PATCH_HDR.pack(file_size, payload_len,
                         1,          # format_version ("Signing Format Version")
                         0,          # signature ("Signature Algorithm")
                         download_mode,
                         0,          # reserved1
                         product_id,
                         rom_build,
                         patch_version,
                         0,          # reserved2
                         entry)
    body = hdr + payload
    declared = len(body)
    if truncate:
        body = body[:declared - 40]           # chop 40 bytes off the tail
    return tlv_header(TLV_TYPE_PATCH, declared) + body


def tag_record(tag_id, data):
    """tlv_type_nvm: tag_id LE16 + tag_len LE16 + reserve1 + reserve2 + data
    (12-byte prefix; kernel strides 12 + tag_len)."""
    return NVM_TAG_HDR.pack(tag_id, len(data), 0, 0) + data


def make_nvm(tag, file_size=3936, bd_addr=b"\x02\x00\x5e\x10\x00\x00"):
    """Single-set NVM at an exact fleet-magnitude size. Tag plan:
    1  version string (lab FP6-census role for tag 1 on the Moselle
       family; upstream btqca.c does not name tag 1 — kept opaque-annotated
       in the parser),
    2  BD address (kernel: tag_len must be 6; RFC 7042 documentation
       address used — no real address),
    17 HCI transport parameters (kernel: >=3 bytes, byte0|0x80, baud byte),
    27 deep-sleep (kernel: >=1 byte),
    rest opaque filler tags (unknown to upstream — proves opaque handling).
    """
    set_len_target = file_size - 4            # minus the one type-2 header
    tag = tag.encode() if isinstance(tag, str) else tag
    tags = bytearray()
    tags += tag_record(1, b"BTFW.SYNTH.1.0-00001-PATCHZ-1")   # 24 B
    tags += tag_record(2, bd_addr)                            # 6 B
    tags += tag_record(17, pattern(8, tag + b":hci"))         # 8 B
    tags += tag_record(27, pattern(4, tag + b":ds"))          # 4 B
    counter = 0
    filler_ids = [0x20 + (i % 0x60) for i in range(256)]
    while True:
        remaining = set_len_target - len(tags)
        if remaining == 0:
            break
        if remaining <= 80:
            # final filler consumes the remaining bytes exactly (a tag
            # header is 12; from a >80 start, every filler step keeps the
            # remainder >= 13, so a >=12 gap can always be closed)
            assert remaining >= NVM_TAG_HDR.size, \
                "unreachable gap %d" % remaining
            tags += tag_record(filler_ids[counter % len(filler_ids)],
                               pattern(remaining - NVM_TAG_HDR.size,
                                       tag + b":fill%d" % counter))
            break
        n = 16 + (counter % 6) * 8             # 16..56 byte filler bodies
        tags += tag_record(filler_ids[counter % len(filler_ids)],
                           pattern(n, tag + b":fill%d" % counter))
        counter += 1
    assert len(tags) == set_len_target, (len(tags), set_len_target)
    # single-set NVM: ONE type-2 header, tag bytes directly after it
    # (kernel reads the header at offset 0, tags at offset 4)
    return tlv_header(TLV_TYPE_NVM, len(tags)) + bytes(tags)


def make_nvm_multi(tag):
    """Type-4 enclosing header + two adjacent type-2 sets + trailing bytes
    (the btqca.c multi-NVM comment path; the lab's FP6 census observed the
    type-4 form + 903 trailing bytes on evrnv20.bin)."""
    tag = tag.encode() if isinstance(tag, str) else tag
    set1 = tag_record(1, b"SET-A") + tag_record(2, b"\x02\x00\x5e\x10\x00\x01") \
        + tag_record(27, b"\x01")
    set2 = tag_record(1, b"SET-B") + tag_record(17, b"\x80\x0d\x00\x00")
    trailing = pattern(12, tag + b":trail")
    out = tlv_header(TLV_TYPE_MULTI_NVM_ENCLOSING, 0)
    out += tlv_header(TLV_TYPE_NVM, len(set1)) + set1
    out += tlv_header(TLV_TYPE_NVM, len(set2)) + set2
    out += trailing
    return out


def make_elf_patch(tag):
    """Raw ELF rampatch fixture (WCN6750 msbtfw*.mbn primary path) — NOT
    TLV-wrapped: the kernel's ELF branch reads fw_data[4]=File Class,
    [5]=Data Encoding, [6]=File version of the file itself and forces
    SKIP_EVT_VSE_CC (btqca.c:310-320). Bytes 0..3 = ELF magic."""
    tag = tag.encode() if isinstance(tag, str) else tag
    return b"\x7fELF" + bytes([1, 1, 1]) + pattern(40, tag)


def main():
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    written = []
    jobs = [
        ("crbtfw20_synthetic.tlv",
         make_patch("crbtfw20-synthetic", file_size=FLEET_SIZES["crbtfw20.tlv"])),
        ("crnv20_synthetic.bin",
         make_nvm("crnv20-synthetic", file_size=FLEET_SIZES["crnv20.bin"])),
        ("apnv10_synthetic.bin",
         make_nvm("apnv10-synthetic", file_size=FLEET_SIZES["apnv10.bin"])),
        ("nvm_multi_synthetic.bin", make_nvm_multi("nvm-multi-synthetic")),
        ("crbtfw20_truncated.tlv", make_patch("crbtfw20-trunc", truncate=True)),
        ("msbtfw11_synthetic.mbn", make_elf_patch("msbtfw11-synthetic")),
    ]
    for name, blob in jobs:
        path = os.path.join(FIXTURE_DIR, name)
        with open(path, "wb") as f:
            f.write(blob)
        written.append((name, len(blob)))
    for name, n in written:
        print("%-28s %8d bytes" % (name, n))
    print("\nsizes vs fleet: crbtfw20.tlv=%d crnv20.bin=%d apnv10.bin=%d"
          % (FLEET_SIZES["crbtfw20.tlv"], FLEET_SIZES["crnv20.bin"],
             FLEET_SIZES["apnv10.bin"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
