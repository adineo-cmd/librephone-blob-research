#!/usr/bin/env python3
"""mtk_container.py — clean-room parser/verifier for the two documented
MediaTek firmware container formats:

  1. the ``mtk_hdr`` signed record chain (the lab's name for the LK
     ``part_hdr`` chain), and
  2. the GFH ``MMM`` record chain (preloader / md1dsp outer layer).

It walks a chain, VERIFIES the documented structural invariants
(bounds, alignment, stride progress, truncation), decodes every field the
spec corpus pins, emits the record table as JSON, and classifies
signature blocks (the per-payload DER X.509 cert1/cert2 pairs).
It is an inspector: it detects signature blocks by DER shape and the
documented pair sizes; it does NOT perform RSA verification of the
certificate chain (public tooling exists for that — see README, prior art).

======================================================================
CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16:
  - librephone-blob-research/mediatek/rosemary-census.md, section
    "Container formats (empirical, cross-checked)": mtk_hdr byte-for-byte
    layout (magic 0x58881688 @0, payload size @4, NUL-padded ASCII name @8
    with >=20-byte names on MT6785, extension record 0x58891689 @0x30 with
    header size 0x200 @0x34 and payload alignment 0x10 @0x44, next record
    at align(payload_end)); GFH MMM-chain record model; per-payload
    cert1 (1,709 B) + cert2 (957 B) DER X.509 pairs; unsigned modem data
    payload list.
  - librephone-blob-research/mediatek/docs/md1dsp-decode.md (F-36): GFH
    MMM chain on md1dsp (sig_type=0, load_addr=0xFFFFFFFF) and record
    type 260 (0x104) absent from U-Boot's enum.
  - U-Boot tools/mtk_image.h (GPL-2.0+, public) for the GFH record struct
    field layout (gfh_common_header magic[3]="MMM", version u8, size u16,
    type u16; gfh_file_info / gfh_bl_info / gfh_brom_cfg / gfh_anti_clone /
    gfh_brom_sec_cfg field order), which the census confirms the rosemary
    production images match "exactly U-Boot's structs".
No proprietary material (no firmware payload bytes, no decompiled code,
no vendor headers) was accessed during development.
======================================================================

Usage:
    python3 -I mtk_container.py <firmware-file> [--kind auto|mtk_hdr|gfh]
                                 [--json OUT.json] [--hash]

Exit status 0 on a fully-verified parse; 1 on verification failures
(bad magic, truncated payload, non-advancing chain) — diagnostics are in
the JSON under ``verification``.
"""

import argparse
import hashlib
import json
import struct
import sys

# --- documented constants (rosemary-census.md, "Container formats") ---
MTK_HDR_MAGIC = 0x58881688   # mtk_hdr record magic @0x00
MTK_EXT_MAGIC = 0x58891689   # extension-record magic @0x30
MTK_HDR_FIXED = 0x200        # 512-byte record headers; ext header_size documents this
MTK_DEFAULT_ALIGN = 0x10     # payload alignment @0x44 (0x10 observed on MT6785)
NAME_OFF = 0x08              # NUL-padded ASCII name @0x08
NAME_MAX = 0x20              # read window for the name (>=20 bytes on MT6785)

CERT1_SIZE = 1709            # documented DER X.509 cert1 size (rosemary)
CERT2_SIZE = 957             # documented DER X.509 cert2 size (rosemary)
DER_SEQ_82 = b"\x30\x82"     # DER SEQUENCE, two length bytes

GFH_MAGIC_LE = 0x014D4D4D    # b"MMM" + version byte 1, little-endian u32 view
GFH_FIXED = 8                # gfh_common_header: magic[3], version u8, size u16, type u16

# GFH record types pinned by U-Boot tools/mtk_image.h + the census.
GFH_TYPES = {
    0: "FILE_INFO",
    1: "BL_INFO",
    2: "ANTI_CLONE",
    3: "BL_SEC_KEY",
    7: "BROM_CFG",
    8: "BROM_SEC_CFG",
}
# Type 260 (0x104): observed on md1dsp (F-36); beyond U-Boot's enum.
# Body semantics are NOT pinned by any public spec — decoded as opaque.
GFH_TYPE_MD1DSP = 260

MAX_RECORDS = 4096           # sanity cap: rosemary partitions carry <= 49 records


def _sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]


def _name(blob, off):
    raw = blob[off + NAME_OFF:off + NAME_OFF + NAME_MAX].split(b"\x00", 1)[0]
    try:
        return raw.decode("ascii")
    except UnicodeDecodeError:
        return "hex:" + raw.hex()


def parse_mtk_hdr_chain(data, hash_payloads=False):
    """Walk an mtk_hdr signed record chain with verification.

    Returns {"format", "file_size", "verification", "records", "signature_blocks"}.
    Never raises on malformed input: failures are recorded in
    ``verification`` (status != "ok") and the walk stops at the first
    structural inconsistency (per the spec, the chain layout is
    deterministic, so any inconsistency means the rest is untrustworthy).
    """
    diags = []
    records = []
    off = 0
    status = "ok"
    for _ in range(MAX_RECORDS):
        if off >= len(data):
            break  # clean end of chain
        if off + MTK_HDR_FIXED > len(data):
            diags.append("truncated-header@0x%x" % off)
            status = "truncated-header"
            break
        magic, size = struct.unpack_from("<II", data, off)
        if magic != MTK_HDR_MAGIC:
            diags.append("bad-magic@0x%x (0x%08x)" % (off, magic))
            status = "bad-magic"
            break
        rec = {
            "index": len(records),
            "header_offset": off,
            "name": _name(data, off),
            "size": size,
        }
        ext = None
        if off + 0x48 <= len(data) and struct.unpack_from("<I", data, off + 0x30)[0] == MTK_EXT_MAGIC:
            ext = {
                "header_size": struct.unpack_from("<I", data, off + 0x34)[0],
                "flag_0x38": struct.unpack_from("<I", data, off + 0x38)[0],
                "word_0x3c": struct.unpack_from("<I", data, off + 0x3C)[0],
                "align": struct.unpack_from("<I", data, off + 0x44)[0],
            }
        rec["ext"] = ext
        hdr_size = ext["header_size"] if ext and ext["header_size"] >= MTK_HDR_FIXED else MTK_HDR_FIXED
        pstart = off + hdr_size
        pend = pstart + size
        payload = None
        if pend > len(data):
            payload = data[pstart:len(data)]
            diags.append("truncated-payload@0x%x: need %d B, %d available"
                         % (pstart, size, len(data) - pstart))
            status = "truncated-payload"
            rec["payload_offset"] = pstart
            rec["payload_available"] = len(payload)
            rec["_payload"] = payload
            records.append(rec)
            break
        payload = data[pstart:pend]
        rec["payload_offset"] = pstart
        rec["_payload"] = payload
        if hash_payloads:
            rec["sha256_16"] = _sha16(payload)
        records.append(rec)

        align = (ext["align"] if ext and ext["align"] else MTK_DEFAULT_ALIGN)
        if align & (align - 1):
            diags.append("non-power-of-two-align@0x%x (%d)" % (off, align))
            status = "bad-alignment"
            break
        nxt = (pend + align - 1) & ~(align - 1)
        if nxt <= off:
            diags.append("non-advancing-chain@0x%x -> 0x%x" % (off, nxt))
            status = "non-advancing-chain"
            break
        off = nxt

    _classify_signature_blocks(records)
    for r in records:
        r.pop("_payload", None)  # bytes are not JSON-serializable
    return {
        "format": "mtk_hdr",
        "file_size": len(data),
        "verification": {"status": status, "diagnostics": diags,
                         "records": len(records)},
        "records": records,
        "signature_blocks": _signature_summary(records),
    }


def _classify_signature_blocks(records):
    """Mark DER-shaped records and the payload each pair signs.

    Per the census: every *code* payload is followed by cert1 (1,709 B) +
    cert2 (957 B) records, both starting 30 82 (DER X.509 SEQUENCEs);
    modem data payloads (md1_filter*, md1_mddb*, md1_mdmlayout,
    md1_file_map), gz/unmap2 and lk/kaeru carry no signature records.
    Classification is by DER shape + the documented pair sizes; exact
    pair sizes are recorded but are rosemary-build facts, not format law.
    """
    for i, r in enumerate(records):
        r["signature"] = "none"
    for i, r in enumerate(records):
        body = r.get("_payload")
        if body is None:
            continue
        if not body.startswith(DER_SEQ_82):
            continue
        if body is not None and len(body) == CERT1_SIZE:
            r["signature"] = "cert1"
        elif body is not None and len(body) == CERT2_SIZE:
            r["signature"] = "cert2"
        else:
            r["signature"] = "der-signature-block"
        # mark the immediately preceding payload record as signed (stop at
        # the first non-plain record — never skip past another signature
        # block or an already-marked payload)
        for j in range(i - 1, -1, -1):
            if records[j]["signature"] != "none":
                break
            records[j]["signature"] = "signed-by-cert-pair"
            break


def _signature_summary(records):
    blocks = [r for r in records if r["signature"] in ("cert1", "cert2", "der-signature-block")]
    pairs = 0
    i = 0
    recs = records
    while i < len(recs):
        if recs[i]["signature"] == "cert1" and i + 1 < len(recs) and recs[i + 1]["signature"] == "cert2":
            pairs += 1
            i += 2
        else:
            i += 1
    return {
        "cert1_cert2_pairs": pairs,
        "der_blocks": len(blocks),
        "signed_records": sum(1 for r in records if r["signature"] == "signed-by-cert-pair"),
        "unsigned_records": sum(1 for r in records if r["signature"] == "none"),
    }


# --- GFH MMM chain --------------------------------------------------

def parse_gfh_chain(data):
    """Walk a GFH ``MMM`` record chain (preloader_raw, md1dsp outer layer).

    Record layout per U-Boot tools/mtk_image.h (public, GPL-2.0+), which
    the rosemary census confirms byte-for-byte on production images:
      gfh_common_header: magic[3] = "MMM", version u8, size u16, type u16
    (the census writes the 4-byte prefix as magic_version 0x014D4D4D LE).
    """
    diags = []
    records = []
    off = 0
    status = "ok"
    for _ in range(MAX_RECORDS):
        if off + GFH_FIXED > len(data):
            if off < len(data):
                diags.append("truncated-gfh-header@0x%x" % off)
                status = "truncated-header"
            break
        magic_le = struct.unpack_from("<I", data, off)[0]
        if magic_le != GFH_MAGIC_LE or data[off:off + 3] != b"MMM":
            diags.append("bad-gfh-magic@0x%x" % off)
            status = "bad-magic"
            break
        version = data[off + 3]
        size, rtype = struct.unpack_from("<HH", data, off + 4)
        rec = {
            "index": len(records),
            "header_offset": off,
            "version": version,
            "size": size,
            "type": rtype,
            "type_name": GFH_TYPES.get(rtype, "MD1DSP(observed-on-md1dsp)" if rtype == GFH_TYPE_MD1DSP else "UNKNOWN"),
        }
        body = data[off:min(off + size, len(data))]
        if size < GFH_FIXED:
            diags.append("gfh-size<8@0x%x (%d)" % (off, size))
            status = "bad-size"
            records.append(rec)
            break
        if off + size > len(data):
            diags.append("truncated-gfh-record@0x%x: need %d B" % (off, size))
            status = "truncated-record"
            records.append(rec)
            break
        rec["fields"] = _decode_gfh_body(rtype, body)
        records.append(rec)
        if size == 0:
            diags.append("zero-size-gfh-record@0x%x" % off)
            status = "non-advancing-chain"
            break
        off += size
    return {
        "format": "gfh_mmm",
        "file_size": len(data),
        "verification": {"status": status, "diagnostics": diags,
                         "records": len(records)},
        "records": records,
    }


def _u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def _u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def _decode_gfh_body(rtype, body):
    """Decode only the fields the public struct layout pins; opaque
    otherwise (facts-not-blobs: unknown fields stay unknown)."""
    f = {}
    if rtype == 0 and len(body) >= 0x38:  # gfh_file_info
        f["name"] = body[8:20].split(b"\x00", 1)[0].decode("ascii", "replace")
        f["unused"] = _u32(body, 20)
        f["file_type"] = _u16(body, 24)
        f["flash_type"] = body[26]
        f["sig_type"] = body[27]
        f["load_addr"] = _u32(body, 28)
        f["total_size"] = _u32(body, 32)
        f["max_size"] = _u32(body, 36)
        f["hdr_size"] = _u32(body, 40)
        f["sig_size"] = _u32(body, 44)
        f["jump_offset"] = _u32(body, 48)
        f["processed"] = _u32(body, 52)
    elif rtype == 1 and len(body) >= 12:  # gfh_bl_info
        f["attr"] = _u32(body, 8)
    elif rtype == 2 and len(body) >= 20:  # gfh_anti_clone
        f["ac_b2k"] = body[8]
        f["ac_b2c"] = body[9]
        f["ac_offset"] = _u32(body, 12)
        f["ac_len"] = _u32(body, 16)
    elif rtype == 3:  # gfh_bl_sec_key — opaque pad[0x20c]
        f["note"] = "opaque key material (not decoded)"
    elif rtype == 7 and len(body) >= 96:  # gfh_brom_cfg
        f["cfg_bits"] = _u32(body, 8)
        f["usbdl_by_auto_detect_timeout_ms"] = _u32(body, 12)
        f["jump_bl_arm64"] = body[8 + 4 + 4 + 0x45]
        f["usbdl_by_kcol0_timeout_ms"] = _u32(body, 8 + 4 + 4 + 0x45 + 1 + 2)
        f["usbdl_by_flag_timeout_ms"] = _u32(body, 8 + 4 + 4 + 0x45 + 1 + 2 + 4)
    elif rtype == 8 and len(body) >= 44:  # gfh_brom_sec_cfg
        f["cfg_bits"] = _u32(body, 8)
        f["customer_name"] = body[12:12 + 0x20].split(b"\x00", 1)[0].decode("ascii", "replace")
    elif rtype == GFH_TYPE_MD1DSP:
        f["note"] = ("record type 260 (0x104) observed on md1dsp (F-36); "
                     "absent from U-Boot's enum; body semantics not pinned by any "
                     "public spec — left opaque")
    return f


def auto_kind(data):
    if len(data) >= 4 and struct.unpack_from("<I", data, 0)[0] == MTK_HDR_MAGIC:
        return "mtk_hdr"
    if data[:3] == b"MMM":
        return "gfh"
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file")
    ap.add_argument("--kind", choices=["auto", "mtk_hdr", "gfh"], default="auto")
    ap.add_argument("--json", dest="json_out")
    ap.add_argument("--hash", action="store_true",
                    help="include sha256_16 of each payload in the record table")
    args = ap.parse_args(argv)

    with open(args.file, "rb") as fh:
        data = fh.read()

    kind = args.kind
    if kind == "auto":
        kind = auto_kind(data)
        if kind is None:
            print("mtk_container: neither mtk_hdr (0x58881688) nor GFH (MMM) magic",
                  file=sys.stderr)
            return 2

    result = (parse_mtk_hdr_chain(data, hash_payloads=args.hash) if kind == "mtk_hdr"
              else parse_gfh_chain(data))
    out = json.dumps(result, indent=1)
    if args.json_out:
        with open(args.json_out, "w") as fh:
            fh.write(out + "\n")
    print(out)
    return 0 if result["verification"]["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
