#!/usr/bin/env python3
"""qca_tlv.py — clean-room structural parser/verifier for the Qualcomm
Bluetooth ROM-patch (.tlv rampatch) and NVRAM (.bin NVM) file families:
the ``crbtfw*/crnv*`` (WCN3990/3991/3998), ``apbtfw*/apnv*`` (WCN3988),
``cmbtfw*/cmnv*`` (WCN3950), ``htbtfw*/htnv*`` (QCA6390), ``hpbtfw*/hpnv*``
(QCA2066 / wcnhp* WCN6855) and ``hmtbtfw*/hmtnv*`` (WCN7850) families —
i.e. every TLV-container family the mainline kernel downloads, per the
GPL-published download code (see CLEAN-ROOM STATEMENT).

It walks the documented TLV container chain, VERIFIES the structural
invariants the kernel's own download path relies on (record bounds, tag
stride arithmetic, declared-length vs actual-file-size consistency), decodes
every field the public header pins, and emits a record table as JSON.
It is an inspector: it tabulates what is on disk. It does NOT execute,
decompile or reinterpret patch payload bytes, and it does NOT mutate NVM
tags (the kernel's own loader patches three tags in-flight — that behaviour
is documented in the output, not performed here).

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-16 from public GPL sources only:
  - linux/drivers/bluetooth/btqca.h (torvalds/linux master, GPL-2.0-only):
    struct tlv_type_patch {__le32 total_size; __le32 data_length; u8
    format_version; u8 signature; u8 download_mode; u8 reserved1;
    __le16 product_id; __le16 rom_build; __le16 patch_version;
    __le16 reserved2; __le32 entry;} __packed  (24 bytes);
    struct tlv_type_nvm {__le16 tag_id; __le16 tag_len; __le32 reserve1;
    __le32 reserve2; u8 data[];} __packed  (12-byte prefix);
    struct tlv_type_hdr {__le32 type_len; u8 data[];} __packed (4 bytes);
    enum qca_tlv_type {TLV_TYPE_PATCH=1, TLV_TYPE_NVM, ELF_TYPE_PATCH};
    enum qca_tlv_dnld_mode {NONE, VSE, CC, VSE_CC};
    EDL_TAG_ID_BD_ADDR=2, EDL_TAG_ID_HCI=17, EDL_TAG_ID_DEEP_SLEEP=27;
    MAX_SIZE_PER_TLV_SEGMENT=243; EDL_PATCH_CMD_OPCODE=0xFC00;
    EDL_PATCH_TLV_REQ_CMD=0x1E.
  - linux/drivers/bluetooth/btqca.c (same tree): the type/length
    decomposition (``length = type_len >> 8; type = type_len & 0xff``,
    qca_tlv_check_data NVM branch), the type-4 multi-NVM enclosing-header
    unwrap ("When there is more than one set there is an enclosing header
    of type 4"), the tag loop bounds (``idx + sizeof(struct tlv_type_nvm)
    <= length`` and per-tag ``length < idx + sizeof + tag_len`` -> EINVAL),
    the in-flight NVM tag mutations (tag 17: data[0]|=0x80 + baud byte at
    data[1] for WCN3950/WCN3991+ else data[2]; tag 27: data[0]|=0x01),
    the chip->filename switch (crbtfw/apbtfw/cmbtfw/htbtfw/hpbtfw/
    wcnhpbtfw/hmtbtfw + msnv/crnv/apnv/...), the rom_ver math per chip,
    and the segment download loop (whole file in 243-byte segments; last
    segment always acked; synthetic command-complete injected when VSE is
    skipped).
No proprietary material (no firmware payload bytes, no decompiled code,
no vendor headers) was accessed during development. Payload bytes of the
fleet files themselves remain un-RE'd; this parser covers STRUCTURE only
(what each patch payload DOES to the ROM is marked [OPEN] in README.md).
======================================================================

Usage:
    python3 -I qca_tlv.py <file.tlv|file.bin> [--json out.json] [--hash]
                          [--brief]

Exit status: 0 = structural facts only / info diagnostics; 1 = at least one
error-class diagnostic (truncation, tag overflow, declared-length mismatch).
"""

import hashlib
import json
import math
import os
import struct
import sys

# ---------------------------------------------------------------- constants
# (all from btqca.h / btqca.c, fetched from torvalds/linux master 2026-11-16)

TLV_TYPE_PATCH = 1          # enum qca_tlv_type
TLV_TYPE_NVM = 2
ELF_TYPE_PATCH = 3
TLV_TYPE_MULTI_NVM_ENCLOSING = 4   # not in the enum; documented in btqca.c
                                   # ("an enclosing header of type 4")

TLV_TYPES = {
    1: "TLV_TYPE_PATCH",
    2: "TLV_TYPE_NVM",
    3: "ELF_TYPE_PATCH",
    4: "MULTI_NVM_ENCLOSING",
}

DNLD_MODES = {0: "QCA_SKIP_EVT_NONE", 1: "QCA_SKIP_EVT_VSE",
              2: "QCA_SKIP_EVT_CC", 3: "QCA_SKIP_EVT_VSE_CC"}

MAX_SIZE_PER_TLV_SEGMENT = 243      # btqca.h
EDL_PATCH_CMD_OPCODE = 0xFC00       # btqca.h (VSC carrying every segment)
EDL_PATCH_TLV_REQ_CMD = 0x1E        # btqca.h (sub-command in cmd[0])

TAG_BD_ADDR = 2                     # EDL_TAG_ID_BD_ADDR (kernel: tag_len==6)
TAG_HCI = 17                        # EDL_TAG_ID_HCI (kernel: tag_len>=3)
TAG_DEEP_SLEEP = 27                 # EDL_TAG_ID_DEEP_SLEEP (kernel: >=1)

KNOWN_TAGS = {
    2: "EDL_TAG_ID_BD_ADDR (6 bytes; kernel enforces tag_len==6)",
    17: "EDL_TAG_ID_HCI (>=3 bytes; byte0 |= 0x80 inband-sleep; baud byte "
        "at data[1] for WCN3950/WCN3991+, else data[2])",
    27: "EDL_TAG_ID_DEEP_SLEEP (>=1 byte; byte0 |= 0x01 sleep-enable)",
}

# chip -> rampatch/nvm filename stems, from the qca_uart_setup() switch
CHIP_FAMILIES = {
    "cr": ["WCN3990", "WCN3991", "WCN3998"],
    "ap": ["WCN3988"],
    "cm": ["WCN3950"],
    "ht": ["QCA6390"],
    "hp": ["QCA2066"],
    "wcnhp": ["WCN6855"],
    "hmt": ["WCN7850"],
    "ms": ["WCN6750"],
}

PATCH_HDR = struct.Struct("<II BBBB HHHH I")   # tlv_type_patch, 24 bytes
assert PATCH_HDR.size == 24
NVM_TAG_HDR = struct.Struct("<HH II")          # tlv_type_nvm prefix, 12 bytes
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
    """btqca.c NVM-branch decomposition: low byte = type, upper 24 bits =
    length (length counts bytes AFTER the 4-byte tlv_type_hdr)."""
    type_ = raw & 0xFF
    length = (raw >> 8) & 0xFFFFFF
    return type_, length


def rom_ver_from_soc_ver(soc_ver, chip_family):
    """The kernel's three rom_ver formulas (btqca.c qca_uart_setup).
    rom_ver is a u8 in the kernel — the WCN3998 shift can exceed 8 bits,
    so C's implicit truncation is modelled with & 0xFF."""
    soc_ver &= 0xFFFFFFFF
    if chip_family == "ap":                 # WCN3988
        return (((soc_ver & 0x00000F00) >> 0x05) |
                (soc_ver & 0x0000000F)) & 0xFF
    if chip_family == "cr":                 # WCN3998 documented separately
        return (((soc_ver & 0x0000F000) >> 0x07) |
                (soc_ver & 0x0000000F)) & 0xFF
    return (((soc_ver & 0x00000F00) >> 0x04) |
            (soc_ver & 0x0000000F)) & 0xFF


def expected_rampatch_name(rom_ver, chip_family):
    stem = {"cr": "crbtfw", "ap": "apbtfw", "cm": "cmbtfw", "ht": "htbtfw",
            "hp": "hpbtfw", "wcnhp": "wcnhpbtfw", "hmt": "hmtbtfw",
            "ms": "msbtfw"}[chip_family]
    if chip_family == "ms":
        return "qca/%s%02x.mbn (fallback qca/%s%02x.tlv)" % (stem, rom_ver,
                                                             stem, rom_ver)
    return "qca/%s%02x.tlv" % (stem, rom_ver)


def annotate_filename(filename):
    """Family prefix -> chip mapping (btqca.c qca_uart_setup switch)."""
    base = os.path.basename(filename).lower()
    for prefix, chips in CHIP_FAMILIES.items():
        if base.startswith(prefix):
            return {"filename_prefix": prefix, "chips": chips}
    return None


# ---------------------------------------------------------------- patch walk

def parse_patch(data, rep, path):
    """TLV_TYPE_PATCH: 4-byte container header + 24-byte tlv_type_patch."""
    file_size = len(data)
    if file_size < 4 + PATCH_HDR.size:                      # btqca.c:322
        rep.error("truncated-patch-header",
                  "file is %d bytes; kernel requires >= %d" %
                  (file_size, 4 + PATCH_HDR.size))
        return None
    type_, length = decode_type_len(struct.unpack_from("<I", data, 0)[0])
    hdr = PATCH_HDR.unpack_from(data, 4)
    (total_size, data_length, format_version, signature, download_mode,
     reserved1, product_id, rom_build, patch_version, reserved2,
     entry) = hdr

    rec = {
        "container": {
            "type": type_,
            "type_name": TLV_TYPES.get(type_, "UNKNOWN"),
            "length_field": length,
            "declared_length_consistent": length == file_size - 4,
        },
        "patch_header": {
            "offset": 4,
            "size": PATCH_HDR.size,
            "total_size": total_size,
            "data_length": data_length,
            "format_version": format_version,
            "signature_algorithm": signature,
            "download_mode": download_mode,
            "download_mode_name": DNLD_MODES.get(download_mode,
                                                 "UNKNOWN(%d)" % download_mode),
            "reserved1": reserved1,
            "product_id": product_id,
            "rom_build": "0x%04x" % rom_build,
            "patch_version": "0x%04x" % patch_version,
            "reserved2": reserved2,
            "entry": "0x%08x" % entry,
        },
        "payload": {
            "offset": 4 + PATCH_HDR.size,
            "bytes_available": file_size - 4 - PATCH_HDR.size,
        },
    }
    if type_ != TLV_TYPE_PATCH:
        rep.error("unexpected-type",
                  "expected TLV_TYPE_PATCH(1), got %d (%s)" %
                  (type_, TLV_TYPES.get(type_, "?")))
    if length != file_size - 4:
        rep.error("length-field-mismatch",
                  "type_len length field %d != file_size-4 (%d)" %
                  (length, file_size - 4))
    payload_after_hdr = file_size - 4 - PATCH_HDR.size
    if data_length != payload_after_hdr:
        rep.info("data-length-note",
                 "header data_length %d != bytes after header (%d); the "
                 "kernel does not validate this field" %
                 (data_length, payload_after_hdr))
    if total_size != file_size:
        rep.info("total-size-note",
                 "header total_size %d != file size %d; the kernel does not "
                 "validate this field" % (total_size, file_size))
    # The type_len length field of a patch container counts header+payload
    # (kernel never validates it), so the true header size is structurally
    # undecidable from the file alone; recorded as a note, not a diagnostic.
    rec["patch_header"]["size_note"] = (
        "upstream struct tlv_type_patch is 24 bytes and the kernel never "
        "validates the patch type_len; the lab's FP6 census observed a "
        "32-byte vendor header on the sibling msbtfw/evr family (entry at "
        "container offset 0x24). Fields above are decoded at the upstream "
        "offsets; if they decode as nonsense on a real file, the "
        "extended-header hypothesis is the first thing to test. [OPEN]")

    # download-protocol facts (documented behaviour, computed not executed)
    rec["download_protocol"] = {
        "vsc_opcode": "0x%04x" % EDL_PATCH_CMD_OPCODE,
        "sub_command": "0x%02x" % EDL_PATCH_TLV_REQ_CMD,
        "max_segment": MAX_SIZE_PER_TLV_SEGMENT,
        "segments_to_send": int(math.ceil(file_size /
                                          float(MAX_SIZE_PER_TLV_SEGMENT))),
        "last_segment_size": (file_size % MAX_SIZE_PER_TLV_SEGMENT) or
                             MAX_SIZE_PER_TLV_SEGMENT,
        "note": "kernel sends the WHOLE file (container header included) in "
                "243-byte segments; last segment always acked "
                "(QCA_SKIP_EVT_NONE forced); if download_mode skips VSE, "
                "the host injects a synthetic command-complete",
    }
    fam = annotate_filename(path)
    if fam:
        rec["family_annotation"] = fam
        # The kernel's name math needs the 32-bit soc_ver the controller
        # reports at runtime (qca_read_soc_version), not the 16-bit
        # rom_build stored in the file; applying the DEFAULT formula
        # (>>4) to rom_build alone is what the lab's FP6 census used and
        # reproduces filenames there. The chip-specific WCN3988/WCN3998
        # formulas (different shifts) cannot be evaluated from the file
        # alone — recorded, not guessed.
        derived = rom_ver_from_soc_ver(rom_build, "default")
        rec["family_annotation"]["rom_ver_derived_from_rom_build"] = \
            "0x%02x" % derived
        rec["family_annotation"]["rom_ver_formula_note"] = \
            "default ((soc_ver & 0xf00) >> 4) | (soc_ver & 0xf) applied to " \
            "rom_build; WCN3988/WCN3998 use different shifts of the full " \
            "32-bit soc_ver which is only knowable at runtime"
        rec["family_annotation"]["expected_rampatch_name"] = \
            expected_rampatch_name(derived, fam["filename_prefix"])
    return rec


# ---------------------------------------------------------------- nvm walk

def parse_nvm_tag_set(data, offset, length, rep, set_index):
    """One NVM tag set: tlv_type_nvm records until `length` bytes consumed.
    Boundary arithmetic is exactly the kernel's (btqca.c:399-450)."""
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
        payload = data[base + NVM_TAG_HDR.size: base + NVM_TAG_HDR.size +
                       tag_len]
        tag = {
            "index": len(tags),
            "tag_id": tag_id,
            "tag_len": tag_len,
            "header": "tlv_type_nvm (12-byte prefix incl. reserve1/reserve2)",
            "data_sha1": hashlib.sha1(payload).hexdigest(),
            "data_preview_hex": payload[:16].hex(),
            "meaning": KNOWN_TAGS.get(tag_id, "unknown to upstream btqca.c "
                                           "(kept opaque — facts-not-blobs)"),
        }
        if tag_id == TAG_BD_ADDR and tag_len != 6:
            rep.error("bd-addr-tag-length",
                      "tag 2 (BD_ADDR) tag_len %d != 6" % tag_len)
        if tag_id == TAG_HCI and tag_len < 3:
            rep.error("hci-tag-length",
                      "tag 17 (HCI) tag_len %d < 3" % tag_len)
        tags.append(tag)
        idx += NVM_TAG_HDR.size + tag_len
    return tags, idx


def parse_nvm(data, rep, path):
    """TLV_TYPE_NVM file. Kernel shape (btqca.c:363-451):
      - single set: [type-2 header][tags...]  (header at offset 0, tag bytes
        counted by the header's length field);
      - multi set:  [type-4 enclosing header][type-2 header + set 1][...]
        ("When there is more than one set there is an enclosing header of
        type 4"); the kernel parses the FIRST set only.
    The kernel ignores anything past the first set; this parser scans
    adjacent further sets as info-level facts."""
    file_size = len(data)
    if file_size < 4:                                       # btqca.c:364
        rep.error("truncated-nvm-header", "file is %d bytes" % file_size)
        return None
    type_, length = decode_type_len(struct.unpack_from("<I", data, 0)[0])
    rec = {"container": {"type": type_,
                         "type_name": TLV_TYPES.get(type_, "UNKNOWN"),
                         "length_field": length}}
    if type_ not in (TLV_TYPE_NVM, TLV_TYPE_MULTI_NVM_ENCLOSING):
        rep.error("unexpected-type",
                  "expected TLV_TYPE_NVM(2) or enclosing header(4), got %d" %
                  type_)
        return rec

    if type_ == TLV_TYPE_MULTI_NVM_ENCLOSING:
        if file_size < 8:                                   # btqca.c:378
            rep.error("truncated-multi-nvm",
                      "enclosing header without a following set header")
            return rec
        # kernel steps one 4-byte header (tlv++) and re-decodes
        type_, length = decode_type_len(
            struct.unpack_from("<I", data, 4)[0])
        rec["multi_nvm"] = {
            "enclosing_header_type": 4,
            "kernel_behaviour": "parses the FIRST set only "
                                "('only parse the first set when it has "
                                "type 2 for now' — btqca.c comment)",
        }
        first_set_header_at = 4
    else:
        first_set_header_at = 0

    if type_ != TLV_TYPE_NVM:
        rep.error("unexpected-type", "set header type %d != 2" % type_)
        return rec
    if file_size < first_set_header_at + 4 + length:        # btqca.c:394
        rep.error("truncated-nvm-set",
                  "first set declares %d bytes after its header at %d; "
                  "file has %d" % (length, first_set_header_at, file_size))
        return rec
    tags, consumed = parse_nvm_tag_set(data, first_set_header_at + 4, length,
                                       rep, 0)
    sets = [{"set_index": 0,
             "header_offset": first_set_header_at,
             "declared_bytes": length,
             "consumed_bytes": consumed,
             "tag_count": len(tags),
             "tags": tags}]
    cursor = first_set_header_at + 4 + length
    trailing = file_size - cursor
    while cursor + 4 <= file_size and len(sets) < 8:
        nxt_type, nxt_len = decode_type_len(
            struct.unpack_from("<I", data, cursor)[0])
        if nxt_type != TLV_TYPE_NVM:
            break
        if file_size < cursor + 4 + nxt_len:
            rep.info("adjacent-set-truncated",
                     "adjacent type-2 set at %d declares %d bytes, only %d "
                     "remain; the kernel ignores beyond the first set" %
                     (cursor, nxt_len, file_size - cursor - 4))
            break
        more_tags, more_consumed = parse_nvm_tag_set(
            data, cursor + 4, nxt_len, rep, len(sets))
        sets.append({"set_index": len(sets),
                     "header_offset": cursor,
                     "declared_bytes": nxt_len,
                     "consumed_bytes": more_consumed,
                     "tag_count": len(more_tags),
                     "tags": more_tags})
        cursor += 4 + nxt_len
        trailing = file_size - cursor
    if trailing > 0:
        rep.info("trailing-bytes",
                 "%d trailing byte(s) beyond the scanned sets; the kernel "
                 "ignores them (FP6 census observed 903 on evrnv20.bin)"
                 % trailing)
    rec["nvm_sets"] = sets
    rec["set_count_scanned"] = len(sets)
    fam = annotate_filename(path)
    if fam:
        rec["family_annotation"] = fam
        rec["family_annotation"]["expected_nvm_name"] = \
            rec["family_annotation"]["filename_prefix"] + "nv%02x.bin"
    return rec


# ---------------------------------------------------------------- elf walk

def parse_elf_patch(data, rep):
    """ELF rampatch (WCN6750 msbtfw*.mbn primary path): a RAW ELF file, NOT
    TLV-wrapped — the kernel's ELF_TYPE_PATCH branch inspects fw_data[4..6]
    of the file itself (btqca.c:310-320: File Class @4, Data Encoding @5,
    File version @6) and forces SKIP_EVT_VSE_CC. ELF_TYPE_PATCH=3 is the
    kernel's internal config enum, never a container type byte on disk."""
    if len(data) < 7:                                       # btqca.c:311
        rep.error("truncated-elf-patch", "file is %d bytes; kernel requires "
                ">= 7" % len(data))
        return None
    import math as _math
    return {
        "container": "raw ELF (magic 0x7f 'E' 'L' 'F'; no TLV wrapper)",
        "elf_header_fields_kernel_reads": {
            "file_class_at_4": "0x%02x" % data[4],
            "data_encoding_at_5": "0x%02x" % data[5],
            "file_version_at_6": "0x%02x" % data[6],
        },
        "download_mode_forced": "QCA_SKIP_EVT_VSE_CC (both dnld_mode and "
                                "dnld_type, btqca.c:314-315)",
        "download_protocol": {
            "max_segment": MAX_SIZE_PER_TLV_SEGMENT,
            "segments_to_send": int(_math.ceil(len(data) /
                                               float(MAX_SIZE_PER_TLV_SEGMENT))),
            "last_segment_size": (len(data) % MAX_SIZE_PER_TLV_SEGMENT) or
                                 MAX_SIZE_PER_TLV_SEGMENT,
            "note": "the same qca_download_firmware loop sends the WHOLE "
                    "ELF file in 243-byte segments; with SKIP_EVT_VSE_CC "
                    "segments are send-only and the host injects a "
                    "synthetic command-complete",
        },
    }


# ---------------------------------------------------------------- driver

def parse_file(path):
    rep = Report()
    with open(path, "rb") as f:
        data = f.read()
    if data[:4] == b"\x7fELF":
        # ELF rampatch (msbtfw*.mbn class): raw ELF, no TLV container
        body = parse_elf_patch(data, rep)
        out = {"file": path, "size_bytes": len(data), "elf_magic": True}
        if body:
            out["elf_patch"] = body
        fam = annotate_filename(path)
        if fam:
            out["family_annotation"] = fam
        out["diagnostics"] = rep.items
        return out, (1 if rep.has_errors else 0)
    if len(data) < 4:
        rep.error("file-too-small", "%d bytes; no tlv_type_hdr possible"
                  % len(data))
        return {"file": path, "size_bytes": len(data),
                "diagnostics": rep.items}, 1

    type_, length = decode_type_len(struct.unpack_from("<I", data, 0)[0])
    out = {"file": path, "size_bytes": len(data),
           "type_len_raw": "0x%08x" % struct.unpack_from("<I", data, 0)[0],
           "type": type_, "type_name": TLV_TYPES.get(type_, "UNKNOWN")}

    if type_ == TLV_TYPE_PATCH:
        body = parse_patch(data, rep, path)
        if body:
            out["patch"] = body
    elif type_ in (TLV_TYPE_NVM, TLV_TYPE_MULTI_NVM_ENCLOSING):
        body = parse_nvm(data, rep, path)
        if body:
            out["nvm"] = body
    else:
        rep.error("unknown-container-type",
                  "type %d is not in {1 PATCH, 2 NVM, 4 multi-NVM "
                  "enclosing} (ELF rampatches are raw ELF files, magic "
                  "0x7f 'E' 'L' 'F' — not TLV containers)" % type_)
    out["diagnostics"] = rep.items
    return out, (1 if rep.has_errors else 0)


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    path = args[0]
    json_path = None
    do_hash = "--hash" in args
    do_brief = "--brief" in args
    if "--json" in args:
        i = args.index("--json")
        json_path = args[i + 1]
    out, rc = parse_file(path)
    if do_hash:
        import hashlib
        out["sha256"] = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if do_brief:
        # one-line-per-record rendering for quick triage
        for key in ("patch", "nvm", "elf_patch"):
            if key not in out:
                continue
            node = out[key]
            if key == "nvm":
                for s in node.get("nvm_sets", []):
                    print("set %d: %d tags, %d bytes declared" %
                          (s["set_index"], s["tag_count"], s["declared_bytes"]))
                    for t in s["tags"]:
                        print("  tag %3d len %4d  %s" %
                              (t["tag_id"], t["tag_len"],
                               t["meaning"].split(" (")[0]))
            elif key == "patch":
                print("patch: product_id %d rom_build %s patch_version %s "
                      "download_mode %s entry %s" %
                      (node["patch_header"]["product_id"],
                       node["patch_header"]["rom_build"],
                       node["patch_header"]["patch_version"],
                       node["patch_header"]["download_mode_name"],
                       node["patch_header"]["entry"]))
                print("  %d segments (243 B each; last %d B)" %
                      (node["download_protocol"]["segments_to_send"],
                       node["download_protocol"]["last_segment_size"]))
            else:
                print("elf_patch:", json.dumps(node))
    for d in out["diagnostics"]:
        print("[%s] %s: %s" % (d["class"], d["code"], d["detail"]),
              file=sys.stderr)
    if json_path:
        with open(json_path, "w") as f:
            json.dump(out, f, indent=2, sort_keys=True)
    else:
        print(json.dumps(out, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
