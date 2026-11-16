#!/usr/bin/env python3
"""md32_interface.py — clean-room parser for the documented interface layer
of the MT6785 md1dsp image (the MTK MD32-class modem DSP): the GFH prefix,
the ``DSP!`` image header, the descriptor table, and the USIP/RAKE named
section records.

TODO (THE ISA GAP — F-45, open): this module implements ONLY the
container/interface subset the specs pin. The MD32 *instruction encoding*
for the LR13-era core is not byte-verified anywhere public — Ghidra's
stock module is a stalled WIP for the older ADI-heritage MD32
(cyrozap/ghidra-md32; F-45's leading hypothesis is a generation/variant
mismatch), and F-45's decode pass produced no control-flow-coherent code
in 21 windows x 6 languages. Do NOT extend this module with instruction
semantics: there is no spec. Named levers live in mediatek/docs/md32-gap.md
(real MD32 ELF with machine 0x2454, end-to-end USIP expansion, Check-Point-
methodology SLEIGH build).

======================================================================
CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16:
  - librephone-blob-research/mediatek/docs/md1dsp-decode.md (F-36): DSP!
    header field inventory (+0x0C size, +0x10 version, +0x18 marker,
    +0x1C chip id, +0x2C asic string, +0xAC build string, relative to the
    DSP! magic), sig_type=0 / load_addr=0xFFFFFFFF GFH values.
  - librephone-blob-research/mediatek/docs/md32-gap.md (F-45) + results/
    md32-gap.json: absolute offsets re-verified (magic @0x118, size @0x124,
    version @0x128, marker @0x134, chip @0x138, descriptor table @0x248
    with its three records, USIP tag @0x274 body @0x278 with two sample
    records, RAKE tag @0x4b4 with the six-record chain 0x58c814 -> 0x60a9d0
    and the documented crc32 constants).
  - librephone-blob-research/mediatek/rosemary-census.md: the GFH MMM
    record model and the md1dsp partition facts.
No proprietary material (no firmware payload bytes, no decompiled code)
was accessed during development.
======================================================================

DOCUMENTED INTERNAL CONFLICT (reported, not silently resolved — Rule 1):
F-36 gives marker/chip relative to the DSP! magic (+0x18/+0x1C = absolute
0x130/0x134); F-45's re-verified absolute offsets are 0x134/0x138 — a
4-byte shift. No md1dsp image exists on this machine to adjudicate, so
``parse_dsp_image`` reads BOTH maps, reports which matched, and never
guesses. Same for F-36-only fields (asic @base+0x2C, build @base+0xAC):
single-source, unverified.

CLI: python3 -I md32_interface.py <file> [--json OUT.json] [--no-crc]
"""

import argparse
import json
import struct
import sys
import zlib

DSP_MAGIC = b"DSP!"
DSP_MAGIC_OFFSET = 0x118       # F-45 re-verified (F-36 agrees)
DSP_SIZE_OFFSET = 0x124        # F-36 +0x0C; F-45 absolute (agree)
DSP_VERSION_OFFSET = 0x128     # F-36 +0x10; F-45 absolute (agree)
# dual documented readings (see module docstring):
MARKER_F45 = 0x134             # F-45 absolute
CHIP_F45 = 0x138               # F-45 absolute
MARKER_F36 = 0x130             # F-36 relative (+0x18)
CHIP_F36 = 0x134               # F-36 relative (+0x1C)
ASIC_OFFSET = 0x144            # F-36 only (+0x2C)
BUILD_OFFSET = 0x1C4           # F-36 only (+0xAC)

DESCRIPTOR_TABLE_OFFSET = 0x248  # both docs
DESCRIPTOR_RECORDS = 3
USIP_TAG_OFFSET = 0x274          # F-45
USIP_BODY_OFFSET = 0x278         # F-45
RAKE_TAG_OFFSET = 0x4B4          # F-45
RAKE_RECORD_SIZE = 16

GFH_MAGIC_LE = 0x014D4D4D

# Documented RAKE chain (F-45 / results/md32-gap.json). Record layout per
# the JSON ordering: (w0 opaque, off, len, crc32). The chain tiles
# 0x58c814 -> 0x60a9d0 over the md32/rake+scq16 string zone.
RAKE_CHAIN_EXPECTED = [
    (0x58C814, 0x4D0C, 0x9C681227),
    (0x591520, 0x26C8, 0x8E4ABFDC),
    (0x5D6540, 0x12484, 0xDAF6CE8D),
    (0x5EFAC4, 0x54A8, 0x04A1A1C8),
    (0x5F4F6C, 0x10C68, 0x0D410876),
    (0x605BD4, 0x4DFC, 0x1FBF2927),
]
RAKE_WINDOW = (0x58C814, 0x60A9D0)

# Documented USIP sample records (semantics NOT fully pinned — F-45).
USIP_SAMPLES = [
    (1, 0x100000, 0xAEE80, 0x3DE5FC84),
    (0, 0x101000, 0x48B814, 0x30F210D6),
]

# Documented descriptor table (off/len semantics NOT pinned — F-45).
DESCRIPTOR_EXPECTED = [
    (0x15C, 0x58B814, 0, 1),
    (0x39C, 0x73D4, 0, 2),
    (0x56C, 0x49A58, 0, 0x50495355),  # b"USIP" little-endian
]


def _u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def walk_gfh_prefix(data, limit):
    """Minimal GFH MMM record walk over data[0:limit] (type/size/offset
    only; full field decode lives in implementations/mediatek/container/)."""
    recs = []
    off = 0
    while off + 8 <= limit:
        if struct.unpack_from("<I", data, off)[0] != GFH_MAGIC_LE:
            break
        size, rtype = struct.unpack_from("<HH", data, off + 4)
        rec = {"offset": off, "type": rtype, "size": size,
               "version": data[off + 3]}
        if rtype == 0 and off + 56 <= len(data):
            rec["name"] = data[off + 8:off + 20].split(b"\x00", 1)[0].decode(
                "ascii", "replace")
            rec["sig_type"] = data[off + 27]
            rec["load_addr"] = _u32(data, off + 28)
            rec["total_size"] = _u32(data, off + 32)
        recs.append(rec)
        if size < 8 or off + size > limit:
            break
        off += size
    return recs


def parse_dsp_image(data, check_crc=True):
    """Parse the documented md1dsp interface layer. Never raises;
    unverifiable fields are reported as such."""
    out = {
        "format": "md1dsp-interface",
        "file_size": len(data),
        "isa": "MD32-class core; INSTRUCTION ENCODING NOT SPEC'D (F-45 gap) "
               "— this module intentionally stops at the interface layer",
    }
    # --- GFH prefix (records up to the DSP! magic) ---
    if len(data) < DSP_MAGIC_OFFSET + 4:
        out["error"] = "file shorter than the documented DSP! magic offset 0x118"
        return out
    if data[DSP_MAGIC_OFFSET:DSP_MAGIC_OFFSET + 4] != DSP_MAGIC:
        out["error"] = "no DSP! magic at 0x118 (observed %s)" % (
            data[DSP_MAGIC_OFFSET:DSP_MAGIC_OFFSET + 4].hex())
        return out
    out["gfh_prefix"] = walk_gfh_prefix(data, DSP_MAGIC_OFFSET)

    # --- DSP! header, dual documented readings ---
    size = _u32(data, DSP_SIZE_OFFSET)
    version = _u32(data, DSP_VERSION_OFFSET)
    marker_f45 = _u32(data, MARKER_F45)
    marker_f36 = _u32(data, MARKER_F36)
    chip_f45 = data[CHIP_F45:CHIP_F45 + 6]
    chip_f36 = data[CHIP_F36:CHIP_F36 + 6]
    marker_read = ("F-45(abs 0x134)" if marker_f45 == 0x12345678 else
                   "F-36(rel +0x18 = 0x130)" if marker_f36 == 0x12345678 else
                   "NEITHER (0x130=%08x 0x134=%08x)" % (marker_f36, marker_f45))
    chip_read = ("F-45(abs 0x138)" if chip_f45 == b"MT6785" else
                 "F-36(rel +0x1C = 0x134)" if chip_f36 == b"MT6785" else
                 "NEITHER")
    out["header"] = {
        "magic_offset": DSP_MAGIC_OFFSET,
        "payload_size": size,
        "version": version,
        "marker": "0x%08x" % marker_f45,
        "marker_reading": marker_read,
        "chip": chip_f45.decode("ascii", "replace"),
        "chip_reading": chip_read,
        "asic_string": data[ASIC_OFFSET:ASIC_OFFSET + 16].split(b"\x00", 1)[0]
                           .decode("ascii", "replace") + "  (F-36-only offset, unverified)",
        "build_string": data[BUILD_OFFSET:BUILD_OFFSET + 32].split(b"\x00", 1)[0]
                            .decode("ascii", "replace") + "  (F-36-only offset, unverified)",
        "documented_conflict": "marker/chip offsets differ between F-36 "
                               "(+0x18/+0x1C) and F-45 (0x134/0x138) — both "
                               "read and reported; see module docstring",
    }

    # --- descriptor table @0x248 (shape pinned; off/len semantics NOT) ---
    desc = []
    for i in range(DESCRIPTOR_RECORDS):
        o = DESCRIPTOR_TABLE_OFFSET + 16 * i
        rec = {"raw": [_u32(data, o + k * 4) for k in range(4)]}
        if i < len(DESCRIPTOR_EXPECTED):
            exp = DESCRIPTOR_EXPECTED[i]
            rec["matches_documented"] = tuple(rec["raw"]) == exp
            tag = exp[3]
            rec["tag_is_ascii"] = (tag if isinstance(tag, str) else
                                   struct.pack("<I", tag).decode("ascii", "replace"))
        desc.append(rec)
    out["descriptor_table"] = {
        "offset": DESCRIPTOR_TABLE_OFFSET,
        "record_shape": "(u32, u32, u32, u32) x3 — F-45 'off/len semantics not pinned'",
        "records": desc,
    }

    # --- USIP (tag @0x274, body @0x278; record count NOT pinned) ---
    usip_tag = data[USIP_TAG_OFFSET:USIP_TAG_OFFSET + 4]
    body = USIP_BODY_OFFSET
    # stop before the RAKE tag; the remaining slack is a spec-gap note
    max_bytes = RAKE_TAG_OFFSET - body
    n_full = max_bytes // RAKE_RECORD_SIZE
    usip_recs = []
    for i in range(n_full):
        o = body + 16 * i
        usip_recs.append([_u32(data, o + k * 4) for k in range(4)])
    out["usip"] = {
        "tag_offset": USIP_TAG_OFFSET,
        "tag": usip_tag.decode("ascii", "replace"),
        "body_offset": body,
        "record_count_parsed": len(usip_recs),
        "termination": "NOT pinned by the spec (parsed up to the RAKE tag; "
                       "%d B slack — F-45 records_partially_parsed=true)" % (max_bytes % 16),
        "documented_samples_match": all(
            usip_recs[i] == list(USIP_SAMPLES[i])
            for i in range(min(len(USIP_SAMPLES), len(usip_recs)))),
        "records_head": usip_recs[:8],
        "semantics": "field semantics not fully pinned (F-45) — opaque",
    }

    # --- RAKE chain @0x4b4 (fully pinned: 6 records, window, crc32s) ---
    rake_tag = data[RAKE_TAG_OFFSET:RAKE_TAG_OFFSET + 4]
    recs = []
    for i in range(len(RAKE_CHAIN_EXPECTED)):
        o = RAKE_TAG_OFFSET + 4 + 16 * i
        if o + 16 > len(data):
            recs.append(None)
            continue
        w0, off, ln, crc = struct.unpack_from("<IIII", data, o)
        rec = {"w0_opaque": w0, "off": off, "len": ln, "crc32": crc}
        exp = RAKE_CHAIN_EXPECTED[i]
        rec["matches_documented"] = (off, ln, crc) == exp
        if check_crc and off + ln <= len(data):
            actual = zlib.crc32(data[off:off + ln]) & 0xFFFFFFFF
            rec["crc32_file_match"] = (actual == crc)
        recs.append(rec)
    offs = [r["off"] for r in recs if r]
    ends = [r["off"] + r["len"] for r in recs if r]
    window_ok = bool(offs) and offs[0] == RAKE_WINDOW[0] and max(ends) == RAKE_WINDOW[1]
    sorted_ok = offs == sorted(offs)
    nonoverlap = all(ends[i] <= offs[i + 1] for i in range(len(ends) - 1))
    out["rake"] = {
        "tag_offset": RAKE_TAG_OFFSET,
        "tag": rake_tag.decode("ascii", "replace"),
        "record_layout": "(u32 w0 opaque, u32 off, u32 len, u32 crc32) x16 B — "
                         "field order per results/md32-gap.json",
        "records": recs,
        "chain_checks": {
            "documented_window_ok": window_ok,
            "sorted_offsets": sorted_ok,
            "non_overlapping": nonoverlap,
            "contiguity": "NOT pinned — the documented chain itself carries "
                          "two gaps (F-45 shows 0x591520+0x26c8 -> 0x5d6540); "
                          "only the window bounds are spec facts",
        },
        "crc32_checked": check_crc,
    }
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--no-crc", action="store_true",
                    help="skip per-region crc32 verification")
    args = ap.parse_args(argv)

    with open(args.file, "rb") as fh:
        data = fh.read()
    doc = parse_dsp_image(data, check_crc=not args.no_crc)
    out = json.dumps(doc, indent=1)
    if args.json_out:
        with open(args.json_out, "w") as fh:
            fh.write(out + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
