#!/usr/bin/env python3
"""hp_fleet_probe.py — clean-room structural probe for the SECOND QCA BT
firmware family: the ``hp*`` (QCA2066) and ``hmt*`` (WCN7850) TLV
rampatch / NVM families.

Scope: the "h-prefix" generation — ``hpbtfw*.tlv``, ``hmtbtfw*.tlv``,
``hpnv*``, ``hmtnv*`` — which is a *structurally different generation* from
the F-75 ``cr*``/``ap*`` family documented in ``implementations/qca-bt/``.
This module is deliberately self-contained: it does NOT import
``implementations/qca-bt/qca_tlv.py`` so that this family's claims stand on
their own. ``--cross-check`` optionally shells out to that parser and
reports agreement.

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-18 from public GPL sources only:

  - linux/drivers/bluetooth/btqca.h (torvalds/linux master, GPL-2.0-only,
    fetched 2026-11-18) — struct tlv_type_patch (24 B), struct
    tlv_type_nvm (12-B prefix), struct tlv_type_hdr, enum qca_tlv_type,
    enum qca_tlv_dnld_mode, MAX_SIZE_PER_TLV_SEGMENT=243,
    EDL_TAG_ID_BD_ADDR=2 / EDL_TAG_ID_HCI=17 / EDL_TAG_ID_DEEP_SLEEP=27,
    QCA_HSP_GF_SOC_ID / QCA_HSP_GF_SOC_MASK (GlobalFoundries variant gate).
  - linux/drivers/bluetooth/btqca.c (same tree, fetched 2026-11-18) —
    qca_tlv_check_data (type/length decomposition, the type-4 enclosing
    unwrap, the tag loop bounds, the three in-flight tag mutations),
    qca_uart_setup's chip->filename switch (hpbtfw = QCA2066, hmtbtfw =
    WCN7850, plus the WCN6855 hpbtfw fallback), qca_get_nvm_name_by_board
    (the ``b``/``g`` variant suffix and the ``.<b>NN`` board-id suffix),
    the rom_ver formulas, and qca_download_firmware's whole-file 243-byte
    segment loop.
  - linux-firmware WHENCE (git.kernel.org, main, fetched 2026-11-18) —
    the public per-file version strings that bind ``hp*`` to the HSP/QCA2066
    driver section and ``hmt*`` to the WCN7850/ATH12K-HMT section.

No proprietary material was accessed. No decompiled or disassembled code
was used: the patch body is treated as opaque bytes and only *statistics*
over byte ranges are reported. Payload bytes are never reproduced here —
only offsets, lengths, digests and counts.

WHAT THIS TOOL ADDS OVER qca_tlv.py
  The gen-2 ("h-prefix") patch files carry a 32-byte, not 24-byte, vendor
  header, and a 36-byte trailer (a 4-byte tag plus a 32-byte SHA-256) in
  place of F-75's 256-byte signature-class tail. Measured on all 14 gen-2
  files (2026-11-18 — two chip families, seven distinct byte-identities,
  four independent sources):

      file_size  == 4 + 32 + data_length + 36
      total_size == 4 + 32 + data_length        (note the leading 4!)
      trailer[4:36] == sha256(file[4 : file_size-32])

  The last line is a payload-integrity digest that the kernel never even
  looks at, but it holds on every gen-2 file measured. F-75's
  ``4 + 24 + data_length + 256`` is the same shape with a different header
  size and a different trailer size — so the *rule* generalises while the
  *constants* do not. Both are measured, not documented.

Usage:
    python3 -I hp_fleet_probe.py <file> [--json out.json] [--brief]
                                 [--fleet f1 f2 ...] [--cross-check PATH]
                                 [--no-hash]

Exit status: 0 = structural facts only / info diagnostics; 1 = at least one
error-class diagnostic (truncation, bad digest, tag overflow).
"""

import hashlib
import json
import math
import os
import struct
import sys

# ---------------------------------------------------------------- constants
# (all from btqca.h / btqca.c, fetched from torvalds/linux master 2026-11-18)

TLV_TYPE_PATCH = 1          # enum qca_tlv_type
TLV_TYPE_NVM = 2
ELF_TYPE_PATCH = 3
TLV_TYPE_MULTI_NVM_ENCLOSING = 4   # documented in btqca.c, not in the enum

TLV_TYPES = {
    1: "TLV_TYPE_PATCH",
    2: "TLV_TYPE_NVM",
    3: "ELF_TYPE_PATCH",
    4: "MULTI_NVM_ENCLOSING",
}

DNLD_MODES = {0: "QCA_SKIP_EVT_NONE", 1: "QCA_SKIP_EVT_VSE",
              2: "QCA_SKIP_EVT_CC", 3: "QCA_SKIP_EVT_VSE_CC"}

MAX_SIZE_PER_TLV_SEGMENT = 243      # btqca.h
EDL_PATCH_CMD_OPCODE = 0xFC00
EDL_PATCH_TLV_REQ_CMD = 0x1E

TAG_BD_ADDR = 2
TAG_HCI = 17
TAG_DEEP_SLEEP = 27

KNOWN_TAGS = {
    2: "EDL_TAG_ID_BD_ADDR (6 bytes; kernel enforces tag_len==6)",
    17: "EDL_TAG_ID_HCI (>=3 bytes; data[0]|=0x80 inband-sleep; baud byte "
        "at data[1] for WCN3950/WCN3991+ (which includes QCA2066 and "
        "WCN7850), else data[2])",
    27: "EDL_TAG_ID_DEEP_SLEEP (>=1 byte; data[0]|=0x01 sleep-enable)",
}

# Chip mapping for the h-prefix family. Each entry: (chips, evidence).
# btqca.c qca_uart_setup() constructs exactly these names.
CHIP_FAMILIES = {
    "hp": (["QCA2066"],
           "btqca.c: case QCA_QCA2066 -> \"qca/hpbtfw%02x.tlv\"; NVM via "
           "qca_get_nvm_name_by_board(stem=\"hpnv\"); also the documented "
           "WCN6855 fallback path (\"Due to historical reasons ...\" then a "
           "retry with hpbtfw/hpnv)"),
    "hmt": (["WCN7850"],
            "btqca.c: case QCA_WCN7850 -> \"qca/hmtbtfw%02x.tlv\"; NVM stem "
            "\"hmtnv\""),
    "ht": (["QCA6390"], "btqca.c: case QCA_QCA6390 -> \"qca/htbtfw%02x.tlv\""),
    "wcnhp": (["WCN6855"],
              "btqca.c: case QCA_WCN6855 -> \"qca/wcnhpbtfw%02x.tlv\"; the "
              "modern corrected name"),
}

# gen-2 on-disk layout, MEASURED (see module docstring). These are the
# values that hold on every gen-2 file; the 24-byte upstream struct is a
# PREFIX of the 32-byte vendor header.
UPSTREAM_PATCH_HDR_SIZE = 24        # sizeof(struct tlv_type_patch)
GEN2_PATCH_HDR_SIZE = 32            # measured vendor header (after type_len)
GEN1_PATCH_HDR_SIZE = 24            # the F-75 cr/ap generation
GEN2_TRAILER_SIZE = 36              # 4-byte tag + 32-byte SHA-256 digest
GEN1_TRAILER_SIZE = 256             # F-75 cr/ap signature-class tail

PATCH_HDR = struct.Struct("<II BBBB HHHH I")   # upstream tlv_type_patch, 24 B
assert PATCH_HDR.size == UPSTREAM_PATCH_HDR_SIZE
NVM_TAG_HDR = struct.Struct("<HH II")          # tlv_type_nvm prefix, 12 B
assert NVM_TAG_HDR.size == 12


# ---------------------------------------------------------------- diagnostics

class Report:
    """Diagnostics: 'error' class -> exit 1; 'info' class -> recorded only."""

    def __init__(self):
        self.items = []

    def error(self, code, detail):
        self.items.append({"class": "error", "code": code, "detail": detail})

    def info(self, code, detail):
        self.items.append({"class": "info", "code": code, "detail": detail})

    @property
    def has_errors(self):
        return any(i["class"] == "error" for i in self.items)


# ---------------------------------------------------------------- helpers

def decode_type_len(raw):
    """btqca.c NVM branch: low byte = type, upper 24 bits = length.
    `length` counts bytes AFTER the 4-byte tlv_type_hdr."""
    return raw & 0xFF, (raw >> 8) & 0xFFFFFF


def rom_ver_from_soc_ver(soc_ver, chip_family):
    """The kernel's three rom_ver formulas (btqca.c qca_uart_setup).
    rom_ver is a u8 in the kernel, so C's implicit truncation is modelled
    with & 0xFF. NOTE: the kernel applies these to the 32-bit soc_ver that
    the CONTROLLER reports at runtime (get_soc_ver(soc_id, rom_ver)), not to
    the 16-bit rom_build stored in the patch file — see
    rom_ver_from_rom_build() for the caveat."""
    soc_ver &= 0xFFFFFFFF
    if chip_family == "ap":                 # WCN3988
        return (((soc_ver & 0x00000F00) >> 0x05) |
                (soc_ver & 0x0000000F)) & 0xFF
    if chip_family == "cr":                 # WCN3998
        return (((soc_ver & 0x0000F000) >> 0x07) |
                (soc_ver & 0x0000000F)) & 0xFF
    return (((soc_ver & 0x00000F00) >> 0x04) |
            (soc_ver & 0x0000000F)) & 0xFF  # default


def rom_ver_from_rom_build(rom_build):
    """Apply the DEFAULT formula to the file's 16-bit rom_build field.

    This is a *correlation test*, not a derivation: the kernel never feeds
    rom_build to this formula. What the measurement shows (14 gen-2 files,
    2026-11-18) is that for every gen-2 file the default formula applied to
    rom_build reproduces the filename's hex digit exactly — e.g.
    rom_build 0x0200 -> 0x20 -> "hpbtfw20.tlv". The same correlation holds
    for the F-75 cr* files. It is therefore strong evidence that the
    filename digit IS the ROM build in the default encoding, and that the
    field is used as a stand-in for the low half of soc_ver."""
    return (((rom_build & 0x0F00) >> 4) | (rom_build & 0x000F)) & 0xFF


def expected_rampatch_name(rom_ver, prefix):
    return "qca/%sbtfw%02x.tlv" % (prefix, rom_ver)


def expected_nvm_name(rom_ver, prefix, variant="", board_id=None):
    """qca_get_nvm_name_by_board(): variant is "g" for GlobalFoundries
    parts, prefix is "b" ("" for QCA2066), and a non-zero board id appends
    ".<b>%02x"."""
    if board_id in (None, 0x0, 0xFFFF):
        return "qca/%snv%02x%s.bin" % (prefix, rom_ver, variant)
    bp = "" if prefix == "hp" else "b"
    return "qca/%snv%02x%s.%s%02x" % (prefix, rom_ver, variant, bp, board_id)


def annotate_filename(filename):
    """Map a basename to its chip family using the btqca.c switch order.
    Longest prefix first so 'wcnhp' wins over 'hp'."""
    base = os.path.basename(filename).lower()
    for prefix in ("wcnhp", "hmt", "hp", "ht"):
        if base.startswith(prefix):
            chips, evidence = CHIP_FAMILIES[prefix]
            return {"filename_prefix": prefix, "chips": chips,
                    "evidence": evidence}
    return None


def entropy(data):
    """Shannon entropy in bits/byte (0.0 for empty input)."""
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = float(len(data))
    h = 0.0
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log(p, 2)
    return h


def printable_ratio(data):
    """Fraction of bytes in the printable-ASCII + whitespace set."""
    if not data:
        return 0.0
    ok = sum(1 for b in data if 32 <= b < 127 or b in (9, 10, 13))
    return ok / float(len(data))


def block_stats(data):
    """Cheap distribution facts used to characterise opaque ranges."""
    if not data:
        return {"len": 0, "entropy": 0.0, "printable_ratio": 0.0,
                "zero_pct": 0.0, "ff_pct": 0.0}
    n = float(len(data))
    return {
        "len": len(data),
        "entropy": round(entropy(data), 3),
        "printable_ratio": round(printable_ratio(data), 4),
        "zero_pct": round(100.0 * data.count(0) / n, 2),
        "ff_pct": round(100.0 * data.count(0xFF) / n, 2),
    }


# ---------------------------------------------------------------- patch walk

def parse_patch(data, rep, path):
    """TLV_TYPE_PATCH. Decodes the 24-byte UPSTREAM struct at [4,28) and
    then *tests* two candidate on-disk layouts against the measured file:

      gen-1 (F-75 cr/ap):  4 + 24 + data_length + 256
      gen-2 (h-prefix):    4 + 32 + data_length + 36

    Both are tested and both are reported; neither is assumed.
    """
    file_size = len(data)
    if file_size < 4 + UPSTREAM_PATCH_HDR_SIZE:
        rep.error("truncated-patch-header",
                  "file is %d bytes; kernel requires >= %d"
                  % (file_size, 4 + UPSTREAM_PATCH_HDR_SIZE))
        return None

    type_, length = decode_type_len(struct.unpack_from("<I", data, 0)[0])
    (total_size, data_length, format_version, signature, download_mode,
     reserved1, product_id, rom_build, patch_version, reserved2,
     entry) = PATCH_HDR.unpack_from(data, 4)

    declared_ok = length == file_size - 4

    rec = {
        "container": {
            "type": type_,
            "type_name": TLV_TYPES.get(type_, "UNKNOWN"),
            "length_field": length,
            "declared_length_consistent": declared_ok,
            "file_size": file_size,
        },
        "patch_header": {
            "offset": 4,
            "upstream_struct_size": UPSTREAM_PATCH_HDR_SIZE,
            "total_size": total_size,
            "data_length": data_length,
            "format_version": format_version,
            "signature_algorithm": signature,
            "download_mode": download_mode,
            "download_mode_name": DNLD_MODES.get(
                download_mode, "UNKNOWN(%d)" % download_mode),
            "reserved1": reserved1,
            "product_id": product_id,
            "rom_build": "0x%04x" % rom_build,
            "patch_version": "0x%04x" % patch_version,
            "reserved2": "0x%04x" % reserved2,
            "entry": "0x%08x" % entry,
        },
    }
    rec["patch_header"]["rom_ver_from_rom_build"] = "0x%02x" % \
        rom_ver_from_rom_build(rom_build)

    if type_ != TLV_TYPE_PATCH:
        rep.error("unexpected-type",
                  "expected TLV_TYPE_PATCH(1), got %d (%s)"
                  % (type_, TLV_TYPES.get(type_, "?")))
    if not declared_ok:
        rep.error("length-field-mismatch",
                  "type_len length field %d != file_size-4 (%d)"
                  % (length, file_size - 4))

    # ---- layout discrimination: measure, do not assume -------------------
    # Two header conventions are observed across the programme:
    #   gen-1 (F-75 cr/ap): total_size == data_length + 24   (header only)
    #   gen-2 (h-prefix):   total_size == data_length + 36   (4-B type_len
    #                                                        + 32-B header)
    # so total_size - data_length is 24 or 36 respectively. Both are tested
    # against the header's own arithmetic; the file size is a second,
    # independent check.
    hdr_size = None
    if total_size == data_length + UPSTREAM_PATCH_HDR_SIZE:
        hdr_size = GEN1_PATCH_HDR_SIZE
    elif total_size == data_length + 4 + GEN2_PATCH_HDR_SIZE:
        hdr_size = GEN2_PATCH_HDR_SIZE
    else:
        # Fall back: prefer whichever candidate reproduces the file size.
        for cand, trailer in ((GEN2_PATCH_HDR_SIZE, GEN2_TRAILER_SIZE),
                              (GEN1_PATCH_HDR_SIZE, GEN1_TRAILER_SIZE)):
            if 4 + cand + data_length + trailer == file_size:
                hdr_size = cand
                break
        if hdr_size is None:
            hdr_size = GEN2_PATCH_HDR_SIZE
        rep.info("header-size-inferred",
                 "total_size-data_length (%d) is neither 24 nor 36; "
                 "assumed header size %d" % (total_size - data_length,
                                             hdr_size))

    layout = {
        "total_minus_data_length": total_size - data_length,
        "header_size_used": hdr_size,
        "trailer_size_measured": file_size - 4 - hdr_size - data_length,
        "generation": ("gen2-32byte-header" if hdr_size == GEN2_PATCH_HDR_SIZE
                       else "gen1-24byte-header"),
    }
    if layout["trailer_size_measured"] < 0:
        layout["shortfall_bytes"] = -layout["trailer_size_measured"]
        layout["shortfall_note"] = (
            "the file is shorter than its own data_length demands: %d byte(s) "
            "missing from the trailer" % layout["shortfall_bytes"])

    # The F-75 invariant is tested EXPLICITLY for every file, plus the
    # gen-2 counterpart, and both verdicts are reported.
    f75_expected = 4 + GEN1_PATCH_HDR_SIZE + data_length + GEN1_TRAILER_SIZE
    gen2_expected = 4 + GEN2_PATCH_HDR_SIZE + data_length + GEN2_TRAILER_SIZE
    layout["invariant_f75"] = {
        "formula": "4 + 24 + data_length + 256",
        "expected_size": f75_expected,
        "actual_size": file_size,
        "holds": f75_expected == file_size,
        "delta": file_size - f75_expected,
    }
    layout["invariant_gen2"] = {
        "formula": "4 + 32 + data_length + 36",
        "expected_size": gen2_expected,
        "actual_size": file_size,
        "holds": gen2_expected == file_size,
        "delta": file_size - gen2_expected,
    }
    # header self-consistency: total_size covers type_len + header + payload
    layout["total_size_covers_header_plus_payload"] = (
        total_size == hdr_size + data_length or
        total_size == 4 + hdr_size + data_length)

    layout["holds"] = layout["invariant_gen2"]["holds"] if hdr_size == \
        GEN2_PATCH_HDR_SIZE else layout["invariant_f75"]["holds"]
    rec["layout"] = layout

    if not layout["holds"]:
        rep.error("size-invariant-failed",
                  "neither 4+%d+data_length+%d nor 4+%d+data_length+%d "
                  "matches %d bytes (deltas %d / %d)"
                  % (GEN1_PATCH_HDR_SIZE, GEN1_TRAILER_SIZE,
                     GEN2_PATCH_HDR_SIZE, GEN2_TRAILER_SIZE, file_size,
                     layout["invariant_f75"]["delta"],
                     layout["invariant_gen2"]["delta"]))
    else:
        rep.info("size-invariant-holds",
                 "%s: %s == %d"
                 % (layout["generation"],
                    "4 + %d + data_length + %d" % (
                        hdr_size, layout["trailer_size_measured"]), file_size))

    # ---- trailer / digest -----------------------------------------------
    body_start = 4 + hdr_size
    body_end = body_start + data_length
    trailer = data[body_end:] if body_end <= file_size else b""
    digest = {
        "trailer_offset": body_end,
        "trailer_size": len(trailer),
        "first_word_le": ("0x%08x" % struct.unpack_from("<I", trailer, 0)[0]
                          if len(trailer) >= 4 else None),
    }
    if len(trailer) >= 36 and hdr_size == GEN2_PATCH_HDR_SIZE:
        # gen-2 shape: 4-byte tag + SHA-256 over file[4 : file_size-32], i.e.
        # everything after type_len up to (but excluding) the 32-byte digest.
        # The 4-byte tag IS inside the digested range — it is the first word
        # of the trailer but the last word of the covered span.
        digest_end = file_size - 32
        digest["sha256_over"] = "file[4:%d]" % digest_end
        digest["sha256_expected"] = hashlib.sha256(
            data[4:digest_end]).hexdigest()
        digest["sha256_stored"] = trailer[4:36].hex()
        digest["sha256_matches"] = (hashlib.sha256(data[4:digest_end]).digest()
                                    == trailer[4:36])
        digest["covered_span_note"] = (
            "the covered span ends at file_size-32, so the 36-byte trailer "
            "splits into a 4-byte tag that is INSIDE the digest and a "
            "32-byte SHA-256 that is not")
        if not digest["sha256_matches"]:
            rep.error("trailer-digest-mismatch",
                      "trailer SHA-256 does not cover file[4:%d]" % digest_end)
        else:
            rep.info("trailer-digest-verified",
                     "trailer[4:36] == sha256(file[4:%d])" % digest_end)
    elif len(trailer) >= 36:
        digest["sha256_matches"] = None
        digest["note"] = ("gen-1 %d-byte trailer: no SHA-256 field observed; "
                          "F-75 characterises this range as signature-class "
                          "content whose semantics are [OPEN]"
                          % len(trailer))
    else:
        digest["sha256_matches"] = None
        digest["note"] = ("%d-byte trailer: neither the gen-2 36-byte "
                          "tag+SHA-256 shape nor the gen-1 256-byte "
                          "signature-class tail" % len(trailer))
    rec["trailer"] = digest

    # ---- byte-range statistics (opaque body kept opaque) ----------------
    body = data[body_start:body_end] if body_end <= file_size else \
        data[body_start:]
    ranges = [
        {"range": "[0,4)", "role": "tlv_type_hdr",
         "stats": block_stats(data[0:4])},
        {"range": "[4,%d)" % body_start,
         "role": "patch header (%d B: 24-B upstream struct + %d B vendor "
                 "extension)" % (hdr_size, hdr_size - 24),
         "stats": block_stats(data[4:body_start])},
        {"range": "[%d,%d)" % (body_start, body_end),
         "role": "patch body (opaque machine code; statistics only)",
         "stats": block_stats(body)},
        {"range": "[%d,%d)" % (body_end, file_size),
         "role": "trailer (digest/signature-class; opaque)",
         "stats": block_stats(trailer)},
    ]
    rec["ranges"] = ranges
    if body:
        # Most-common little-endian 32-bit words: a purely statistical
        # description of the code-like body (no disassembly performed).
        counts = {}
        for off in range(0, len(body) - 3, 4):
            w = struct.unpack_from("<I", body, off)[0]
            counts[w] = counts.get(w, 0) + 1
        top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:8]
        rec["body_word_histogram"] = [
            {"word": "0x%08x" % w, "count": c} for w, c in top]
        rec["body_alignment_note"] = (
            "body start is 4-byte aligned for both header sizes; word "
            "histogram is computed at that alignment, no disassembly")

    # ---- download protocol (documented behaviour, computed not executed)
    rec["download_protocol"] = {
        "vsc_opcode": "0x%04x" % EDL_PATCH_CMD_OPCODE,
        "sub_command": "0x%02x" % EDL_PATCH_TLV_REQ_CMD,
        "max_segment": MAX_SIZE_PER_TLV_SEGMENT,
        "segments_to_send": int(math.ceil(file_size /
                                          float(MAX_SIZE_PER_TLV_SEGMENT))),
        "last_segment_size": (file_size % MAX_SIZE_PER_TLV_SEGMENT) or
                             MAX_SIZE_PER_TLV_SEGMENT,
        "bytes_over_wire": file_size + 2 * int(
            math.ceil(file_size / float(MAX_SIZE_PER_TLV_SEGMENT))),
        "note": "qca_download_firmware sends the WHOLE file (container "
                "header and trailer included) in 243-byte segments; 2 extra "
                "bytes per segment are the sub-command + length prefix; the "
                "last segment is always acked and a synthetic "
                "command-complete is injected when VSE is skipped",
    }

    # ---- chip / filename annotation -------------------------------------
    fam = annotate_filename(path)
    if fam:
        rom_ver = int(rec["patch_header"]["rom_ver_from_rom_build"], 16)
        fam["expected_rampatch_name"] = expected_rampatch_name(
            rom_ver, fam["filename_prefix"])
        base = os.path.basename(path).lower()
        fam["name_matches_filename"] = base.startswith(
            "%sbtfw%02x" % (fam["filename_prefix"], rom_ver))
        fam["filename_digit_decodes_as_rom_build"] = (
            os.path.basename(path).lower().startswith(
                "%sbtfw%02x" % (fam["filename_prefix"],
                                rom_ver_from_rom_build(rom_build))))
        rec["family_annotation"] = fam
    return rec


# ---------------------------------------------------------------- nvm walk

def parse_nvm_tag_set(data, offset, length, rep, set_index):
    """One NVM tag set: tlv_type_nvm records until `length` is consumed.
    Boundary arithmetic is exactly the kernel's (btqca.c tag loop)."""
    tags = []
    idx = 0
    while idx + NVM_TAG_HDR.size <= length:
        base = offset + idx
        tag_id, tag_len = struct.unpack_from("<HH", data, base)
        if length < idx + NVM_TAG_HDR.size + tag_len:
            rep.error("tag-overruns-set",
                      "set %d: tag %d declares %d data bytes but only %d "
                      "remain" % (set_index, tag_id, tag_len,
                                  length - idx - NVM_TAG_HDR.size))
            break
        payload = data[base + NVM_TAG_HDR.size:
                       base + NVM_TAG_HDR.size + tag_len]
        tag = {
            "index": len(tags),
            "tag_id": tag_id,
            "tag_len": tag_len,
            "data_sha1": hashlib.sha1(payload).hexdigest(),
            "data_preview_hex": payload[:16].hex(),
            "meaning": KNOWN_TAGS.get(
                tag_id, "unknown to upstream btqca.c (kept opaque — "
                        "facts-not-blobs)"),
        }
        if tag_id == TAG_BD_ADDR and tag_len != 6:
            rep.error("bd-addr-tag-length",
                      "tag 2 (BD_ADDR) tag_len %d != 6" % tag_len)
        if tag_id == TAG_HCI and tag_len < 3:
            rep.error("hci-tag-length",
                      "tag 17 (HCI) tag_len %d < 3" % tag_len)
        if tag_id == TAG_DEEP_SLEEP and tag_len < 1:
            rep.error("deep-sleep-tag-length",
                      "tag 27 (DEEP_SLEEP) tag_len %d < 1" % tag_len)
        tags.append(tag)
        idx += NVM_TAG_HDR.size + tag_len
    return tags, idx


def parse_nvm(data, rep, path):
    """TLV_TYPE_NVM file (btqca.c: single set at [0,4); multi-set has a
    type-4 enclosing header and the kernel parses only the first set)."""
    file_size = len(data)
    if file_size < 4:
        rep.error("truncated-nvm-header", "file is %d bytes" % file_size)
        return None
    type_, length = decode_type_len(struct.unpack_from("<I", data, 0)[0])
    rec = {"container": {"type": type_,
                         "type_name": TLV_TYPES.get(type_, "UNKNOWN"),
                         "length_field": length,
                         "declared_length_consistent": length == file_size - 4,
                         "file_size": file_size}}
    if type_ not in (TLV_TYPE_NVM, TLV_TYPE_MULTI_NVM_ENCLOSING):
        rep.error("unexpected-type",
                  "expected TLV_TYPE_NVM(2) or enclosing header(4), got %d"
                  % type_)
        return rec

    if type_ == TLV_TYPE_MULTI_NVM_ENCLOSING:
        if file_size < 8:
            rep.error("truncated-multi-nvm",
                      "enclosing header without a following set header")
            return rec
        type_, length = decode_type_len(struct.unpack_from("<I", data, 4)[0])
        rec["multi_nvm"] = {
            "enclosing_header_type": 4,
            "kernel_behaviour": "parses the FIRST set only ('only parse the "
                                "first set when it has type 2 for now')",
        }
        first = 4
    else:
        first = 0

    rec["container"]["first_set_header_offset"] = first
    if type_ != TLV_TYPE_NVM:
        rep.error("unexpected-type", "set header type %d != 2" % type_)
        return rec
    if length != file_size - first - 4:
        rep.info("set-length-note",
                 "first set header at %d declares %d bytes; file has %d after "
                 "the header (the kernel does not validate the tail)"
                 % (first, length, file_size - first - 4))
    if file_size < first + 4 + length:
        rep.error("truncated-nvm-set",
                  "first set declares %d bytes after its header at %d; "
                  "file has %d" % (length, first, file_size))
        return rec
    tags, consumed = parse_nvm_tag_set(data, first + 4, length, rep, 0)
    sets = [{"set_index": 0, "header_offset": first,
             "declared_bytes": length, "consumed_bytes": consumed,
             "tag_count": len(tags), "tags": tags}]
    cursor = first + 4 + length
    trailing = file_size - cursor
    while cursor + 4 <= file_size and len(sets) < 8:
        nxt_type, nxt_len = decode_type_len(
            struct.unpack_from("<I", data, cursor)[0])
        if nxt_type != TLV_TYPE_NVM:
            break
        if file_size < cursor + 4 + nxt_len:
            rep.info("adjacent-set-truncated",
                     "adjacent type-2 set at %d declares %d bytes, only %d "
                     "remain" % (cursor, nxt_len, file_size - cursor - 4))
            break
        more, more_consumed = parse_nvm_tag_set(
            data, cursor + 4, nxt_len, rep, len(sets))
        sets.append({"set_index": len(sets), "header_offset": cursor,
                     "declared_bytes": nxt_len,
                     "consumed_bytes": more_consumed,
                     "tag_count": len(more), "tags": more})
        cursor += 4 + nxt_len
        trailing = file_size - cursor
    if trailing > 0:
        rec["trailing"] = block_stats(data[cursor:])
        rec["trailing"]["offset"] = cursor
        # Is it a further TLV record the kernel ignores?
        if cursor + 4 <= file_size:
            t3, l3 = decode_type_len(
                struct.unpack_from("<I", data, cursor)[0])
            rec["trailing"]["decodes_as_tlv_type"] = t3
            rec["trailing"]["declared_len"] = l3
            rec["trailing"]["declares_the_rest"] = (l3 == file_size - cursor - 4)
        rep.info("trailing-bytes",
                 "%d trailing byte(s) beyond the scanned sets; the kernel "
                 "ignores them" % trailing)
    rec["nvm_sets"] = sets
    rec["set_count_scanned"] = len(sets)
    rec["tag_id_census"] = sorted({t["tag_id"] for s in sets for t in s["tags"]})

    fam = annotate_filename(path)
    if fam:
        # The rom_ver digit is in the filename itself for an NVM blob (there is
        # no patch header to carry rom_build). Derive it from the basename so
        # the expected-name cross-check is meaningful, not constant 0.
        base = os.path.basename(path).lower()
        suffix = base.rsplit(".", 1)[1] if "." in base else ""
        stem = base[:-(len(suffix) + 1)] if suffix else base
        digits = "".join(ch for ch in stem if ch.isdigit())
        rom_ver = None
        if len(digits) >= 2:
            try:
                rom_ver = int(digits[:2], 16)
            except ValueError:
                rom_ver = None
        fam["board_variant_suffix"] = suffix
        if rom_ver is not None:
            fam["rom_ver_from_filename"] = "0x%02x" % rom_ver
            fam["expected_nvm_name"] = expected_nvm_name(
                rom_ver, fam["filename_prefix"])
        rec["family_annotation"] = fam
    return rec


# ---------------------------------------------------------------- fleet

def same_offset_identity(a, b):
    """F-75 method: fraction of bytes identical at the same offset over the
    common prefix, plus a 16-byte-block overlap count."""
    n = min(len(a), len(b))
    if not n:
        return {"common_len": 0, "identical_bytes": 0, "identity_pct": 0.0,
                "blocks_a": 0, "blocks_b": 0, "blocks_shared": 0}
    same = sum(1 for i in range(n) if a[i] == b[i])
    sa = {a[i:i + 16] for i in range(0, len(a) - 15, 16)}
    sb = {b[i:i + 16] for i in range(0, len(b) - 15, 16)}
    return {"common_len": n, "identical_bytes": same,
            "identity_pct": round(100.0 * same / n, 2),
            "blocks_a": len(sa), "blocks_b": len(sb),
            "blocks_shared": len(sa & sb)}


def fleet_matrix(paths):
    """Cross-file identity matrix. Each entry keeps only digests/counts."""
    docs = []
    for p in paths:
        with open(p, "rb") as f:
            data = f.read()
        docs.append({
            "file": p,
            "basename": os.path.basename(p),
            "size_bytes": len(data),
            "md5": hashlib.md5(data).hexdigest(),
            "sha256": hashlib.sha256(data).hexdigest(),
            "_data": data,
        })
    pairs = []
    for i in range(len(docs)):
        for j in range(i + 1, len(docs)):
            ident = same_offset_identity(docs[i]["_data"], docs[j]["_data"])
            ident.update({"a": docs[i]["basename"], "b": docs[j]["basename"],
                          "a_size": docs[i]["size_bytes"],
                          "b_size": docs[j]["size_bytes"],
                          "byte_identical": docs[i]["md5"] == docs[j]["md5"]})
            pairs.append(ident)
    for d in docs:
        del d["_data"]
    # Distinct byte-identity census per filename.
    by_name = {}
    for d in docs:
        by_name.setdefault(d["basename"], set()).add(d["md5"])
    census = {k: {"distinct_md5": len(v), "md5s": sorted(v)}
              for k, v in sorted(by_name.items())}
    return {"files": docs, "pairs": pairs, "identity_census": census}


# ---------------------------------------------------------------- driver

def probe_file(path, do_hash=True):
    rep = Report()
    with open(path, "rb") as f:
        data = f.read()
    out = {"file": path, "basename": os.path.basename(path),
           "size_bytes": len(data)}
    if do_hash:
        out["md5"] = hashlib.md5(data).hexdigest()
        out["sha256"] = hashlib.sha256(data).hexdigest()
    if len(data) < 4:
        rep.error("file-too-small", "%d bytes; no tlv_type_hdr possible"
                  % len(data))
        out["diagnostics"] = rep.items
        return out, 1

    raw = struct.unpack_from("<I", data, 0)[0]
    type_, length = decode_type_len(raw)
    out["type_len_raw"] = "0x%08x" % raw
    out["type"] = type_
    out["type_name"] = TLV_TYPES.get(type_, "UNKNOWN")

    fam = annotate_filename(path)
    if fam and type_ in (TLV_TYPE_PATCH, TLV_TYPE_NVM,
                         TLV_TYPE_MULTI_NVM_ENCLOSING):
        out["family_annotation"] = dict(fam)

    if type_ == TLV_TYPE_PATCH:
        body = parse_patch(data, rep, path)
        if body:
            out["patch"] = body
    elif type_ in (TLV_TYPE_NVM, TLV_TYPE_MULTI_NVM_ENCLOSING):
        body = parse_nvm(data, rep, path)
        if body:
            out["nvm"] = body
    elif data[:4] == b"\x7fELF":
        out["elf_magic"] = True
        rep.info("elf-rampatch",
                 "raw ELF rampatch (msbtfw*.mbn class) — not a TLV "
                 "container; kernel reads bytes 4..6 of the file itself")
    else:
        rep.error("unknown-container-type",
                  "type %d is not in {1 PATCH, 2 NVM, 4 multi-NVM enclosing}"
                  % type_)
    out["diagnostics"] = rep.items
    return out, (1 if rep.has_errors else 0)


def cross_check(path, parser):
    """Shell out to implementations/qca-bt/qca_tlv.py on `path` and report
    agreement. Optional: this component does not import it, so its own
    claims stand."""
    here = os.path.dirname(os.path.abspath(__file__))
    if parser is None:
        other = os.path.abspath(os.path.join(here, "..", "qca-bt",
                                             "qca_tlv.py"))
    else:
        other = os.path.abspath(parser)
    if not os.path.isfile(other):
        return {"available": False, "reason": "qca_tlv.py not found at %s"
                % other}
    import subprocess
    r = subprocess.run([sys.executable, "-I", other, path, "--brief"],
                       capture_output=True, text=True)
    return {"available": True, "path": other, "returncode": r.returncode,
            "stdout_head": r.stdout.splitlines()[:12],
            "stderr_lines": r.stderr.strip().splitlines()}


def render_brief(out):
    if "size_bytes" not in out:
        # unreadable file: the error doc has no bytes to describe
        return ["%s: UNREADABLE (%s)" % (out.get("basename", "?"),
                                         out.get("error", "unknown error"))]
    lines = ["%s: %d bytes type=%s" % (out["basename"], out["size_bytes"],
                                       out.get("type_name"))]
    if "patch" in out:
        h = out["patch"]["patch_header"]
        lay = out["patch"]["layout"]
        lines.append("  header: product_id %d rom_build %s patch_version %s "
                     "download_mode %s entry %s"
                     % (h["product_id"], h["rom_build"], h["patch_version"],
                        h["download_mode_name"], h["entry"]))
        lines.append("  layout: %s hdr=%d trailer=%d  F-75 %s  gen-2 %s"
                     % (lay["generation"], lay["header_size_used"],
                        lay["trailer_size_measured"],
                        "PASS" if lay["invariant_f75"]["holds"] else
                        "FAIL(delta %+d)" % lay["invariant_f75"]["delta"],
                        "PASS" if lay["invariant_gen2"]["holds"] else
                        "FAIL(delta %+d)" % lay["invariant_gen2"]["delta"]))
        lines.append("  segments: %d x %d B (last %d B)"
                     % (out["patch"]["download_protocol"]["segments_to_send"],
                        out["patch"]["download_protocol"]["max_segment"],
                        out["patch"]["download_protocol"]
                        ["last_segment_size"]))
        if out["patch"]["trailer"].get("sha256_matches") is not None:
            lines.append("  trailer sha256 matches: %s"
                         % out["patch"]["trailer"]["sha256_matches"])
        f = out["patch"].get("family_annotation")
        if f:
            lines.append("  family: %s -> %s (filename match: %s)"
                         % (f["filename_prefix"], "/".join(f["chips"]),
                            f.get("name_matches_filename")))
    if "nvm" in out:
        for s in out["nvm"]["nvm_sets"]:
            lines.append("  set %d: %d tags, %d/%d bytes consumed"
                         % (s["set_index"], s["tag_count"],
                            s["consumed_bytes"], s["declared_bytes"]))
            for t in s["tags"][:6]:
                lines.append("    tag %3d len %4d  %s"
                             % (t["tag_id"], t["tag_len"],
                                t["meaning"].split(" (")[0]))
            if s["tag_count"] > 6:
                lines.append("    ... %d more tags" % (s["tag_count"] - 6))
    return lines


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2

    do_brief = "--brief" in args
    do_hash = "--no-hash" not in args
    json_path = None
    if "--json" in args:
        json_path = args[args.index("--json") + 1]
    cross = None
    if "--cross-check" in args:
        i = args.index("--cross-check")
        cross = args[i + 1] if len(args) > i + 1 else None

    # Positional arguments are the files to analyse; option values are not.
    option_values = {v for v in (json_path, cross) if v}
    flag_names = {"--brief", "--no-hash"}
    positional = []
    skip_next = False
    for i, a in enumerate(args):
        if skip_next:
            skip_next = False
            continue
        if a in ("--json", "--cross-check"):
            skip_next = True
            continue
        if a.startswith("--"):
            continue
        positional.append(a)

    fleet = []
    if "--fleet" in args:
        fleet = [a for a in positional if a not in option_values]
        paths = fleet
    else:
        paths = [a for a in positional if a not in option_values][:1]

    out_docs = []
    rc = 0
    for p in paths:
        try:
            doc, status = probe_file(p, do_hash=do_hash)
        except (IOError, OSError) as exc:
            doc = {"file": p, "basename": os.path.basename(p),
                   "error": str(exc),
                   "diagnostics": [{"class": "error",
                                    "code": "io-error",
                                    "detail": str(exc)}]}
            status = 1
        rc = max(rc, status)
        out_docs.append(doc)
        if do_brief:
            for line in render_brief(doc):
                print(line)
            for d in doc.get("diagnostics", []):
                print("[%s] %s: %s" % (d["class"], d["code"], d["detail"]),
                      file=sys.stderr)

    result = out_docs[0] if len(out_docs) == 1 else {"files": out_docs}
    if len(fleet) > 1:
        result["fleet"] = fleet_matrix(fleet)
    if cross:
        # Cross-check the FIRST analysed file, not the parser path itself.
        target = paths[0] if paths else None
        if target:
            result["cross_check"] = cross_check(target, cross)

    if json_path:
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2, sort_keys=True)
    elif not do_brief:
        print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
