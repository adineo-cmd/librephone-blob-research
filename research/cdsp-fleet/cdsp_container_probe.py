#!/usr/bin/env python3
"""
cdsp_container_probe.py -- byte-level container and ISA probe for Qualcomm
split-MDT CDSP images.

Provenance (written 2026-11-20, adineo-cmd/open-device issue #595). Public
sources used: the ELF gABI Elf32_Ehdr/Elf32_Phdr field order; GPL-2.0-only
torvalds/linux drivers/soc/qcom/mdt_loader.c plus
include/linux/soc/qcom/mdt_loader.h (QCOM_MDT_TYPE_MASK, QCOM_MDT_TYPE_HASH,
QCOM_MDT_RELOCATABLE); include/uapi/linux/elf-em.h (EM_HEXAGON = 164); and
Apache-2.0-with-LLVM-exception
llvm/lib/Target/Hexagon/MCTargetDesc/HexagonBaseInfo.h (INST_PARSE_* and
INST_ICLASS_* bit fields). Every number printed below is measured from files
under the read-only data root; no payload bytes are copied into any output.

Usage:
    python3 -I cdsp_container_probe.py [DATA_ROOT] [--json OUT.json]
"""

import hashlib
import json
import math
import os
import random
import struct
import sys
from collections import Counter

DEFAULT_ROOT = (
    "/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-6cf6375c0730"
    "/data-fetch"
)
CDSP_SUBDIR = "second-device/instantnoodle/modem-fat-lfn"

EHDR = struct.Struct("<16sHHIIIIIHHHHHH")
PHDR = struct.Struct("<8I")

EHDR_FIELDS = [
    ("e_ident", 0, 16),
    ("e_type", 16, 2),
    ("e_machine", 18, 2),
    ("e_version", 20, 4),
    ("e_entry", 24, 4),
    ("e_phoff", 28, 4),
    ("e_shoff", 32, 4),
    ("e_flags", 36, 4),
    ("e_ehsize", 40, 2),
    ("e_phentsize", 42, 2),
    ("e_phnum", 44, 2),
    ("e_shentsize", 46, 2),
    ("e_shnum", 48, 2),
    ("e_shstrndx", 50, 2),
]

PHDR_FIELDS = [
    ("p_type", 0),
    ("p_offset", 4),
    ("p_vaddr", 8),
    ("p_paddr", 12),
    ("p_filesz", 16),
    ("p_memsz", 20),
    ("p_flags", 24),
    ("p_align", 28),
]

EM_HEXAGON = 164
ET_EXEC = 2
ET_DYN = 3
PT_NULL = 0
PT_LOAD = 1

QC_TYPE_MASK = 7 << 24
QC_TYPE_HASH = 2 << 24
QC_TYPE_HDR = 7 << 24
QC_RELOCATABLE = 1 << 27

HEXAGON_ISA = {
    0x00: "unspecified (defer to e_machine)",
    0x10: "V2",
    0x20: "V3",
    0x30: "V4",
    0x40: "V5",
    0x50: "V55",
    0x60: "V60",
    0x61: "V61",
    0x62: "V62",
    0x65: "V65",
    0x66: "V66",
    0x67: "V67",
    0x68: "V68",
    0x69: "V69",
    0x71: "V71",
    0x73: "V73",
    0x75: "V75",
    0x77: "V77",
    0x79: "V79",
    0x81: "V81",
    0x83: "V83",
    0x85: "V85",
    0x87: "V87",
    0x89: "V89",
    0x91: "V91",
    0x93: "V93",
}

ICLASS_NAMES = {
    0x0: "EXTENDER",
    0x1: "J_1",
    0x2: "J_2",
    0x3: "LD_ST_1",
    0x4: "LD_ST_2",
    0x5: "J_3",
    0x6: "CR",
    0x7: "ALU32_1",
    0x8: "XTYPE_1",
    0x9: "LD",
    0xA: "ST",
    0xB: "ALU32_2",
    0xC: "XTYPE_2",
    0xD: "XTYPE_3",
    0xE: "XTYPE_4",
    0xF: "ALU32_3",
}

PARSE_MASK = 0x0000C000
PARSE_PACKET_END = 0x0000C000
PARSE_LOOP_END = 0x00008000
PARSE_NOT_END = 0x00004000
PARSE_ZERO = 0x00000000
ICLASS_MASK = 0xF0000000
ICLASS_EXTENDER = 0x00000000


def u16(b, o):
    return struct.unpack_from("<H", b, o)[0]


def u32(b, o):
    return struct.unpack_from("<I", b, o)[0]


def shannon(data):
    if not data:
        return 0.0
    counts = Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def zero_fraction(data):
    if not data:
        return 0.0
    return data.count(0) / len(data)


def ascii_fraction(data):
    if not data:
        return 0.0
    return sum(1 for x in data if 32 <= x < 127) / len(data)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def parse_elf(raw):
    if len(raw) < 52 or raw[:4] != b"\x7fELF":
        return None
    vals = EHDR.unpack_from(raw, 0)
    hdr = {}
    for (name, off, size), val in zip(EHDR_FIELDS, vals):
        hdr[name] = val
    hdr["_offsets"] = {name: off for name, off, _ in EHDR_FIELDS}
    phdrs = []
    base = hdr["e_phoff"]
    if hdr["e_phentsize"] == 32 and base + 32 * hdr["e_phnum"] <= len(raw):
        for i in range(hdr["e_phnum"]):
            fields = PHDR.unpack_from(raw, base + 32 * i)
            d = {name: fields[k] for k, (name, _) in enumerate(PHDR_FIELDS)}
            d["index"] = i
            d["_phdr_offset"] = base + 32 * i
            d["_field_offsets"] = {
                name: base + 32 * i + off for name, off in PHDR_FIELDS
            }
            phdrs.append(d)
    hdr["phdrs"] = phdrs
    return hdr


def resolve_jsn(path):
    if os.path.isfile(path):
        return path
    directory = os.path.dirname(os.path.abspath(path))
    target = os.path.basename(path).lower()
    try:
        for name in os.listdir(directory):
            if name.lower() == target:
                return os.path.join(directory, name)
    except OSError:
        pass
    try:
        for name in os.listdir(directory):
            low = name.lower()
            if low.startswith("cdspr") and low.endswith(".jsn"):
                return os.path.join(directory, name)
    except OSError:
        pass
    return None


def sibling_path(mdt_path, index):
    candidate = mdt_path[:-3] + "b%02d" % index
    if os.path.isfile(candidate):
        return candidate
    directory = os.path.dirname(os.path.abspath(candidate))
    target = os.path.basename(candidate).lower()
    try:
        for name in os.listdir(directory):
            if name.lower() == target:
                return os.path.join(directory, name)
    except OSError:
        pass
    return candidate


def is_loadable(p):
    if p["p_type"] != PT_LOAD:
        return False
    if (p["p_flags"] & QC_TYPE_MASK) == QC_TYPE_HASH:
        return False
    if p["p_memsz"] == 0:
        return False
    return True


SEG_TYPE_NAMES = {
    0x0: "L4/AMSS",
    0x1: "AMSS",
    0x2: "HASH",
    0x3: "BOOT",
    0x4: "L4BSP",
    0x5: "SWAPPED/XBL_SEC",
    0x6: "SWAP_POOL",
    0x7: "PHDR",
}

ACCESS_NAMES = {
    0x0: "RW",
    0x1: "RO",
    0x2: "ZI",
    0x3: "NOTUSED",
    0x4: "SHARED",
    0x7: "RWE",
}


def decode_pflags(v):
    bits = [k for k in range(32) if (v >> k) & 1]
    seg_type = (v >> 24) & 7
    access = (v >> 21) & 7
    page_mode = (v >> 20) & 1
    pool_index = (v >> 27) & 1
    return {
        "raw": v,
        "raw_hex": "0x%08x" % v,
        "bits_set": bits,
        "pf_x": bool(v & 1),
        "pf_w": bool(v & 2),
        "pf_r": bool(v & 4),
        "rwx": "".join(
            c for c, on in (("R", v & 4), ("W", v & 2), ("X", v & 1)) if on
        ) or "-",
        "seg_type": seg_type,
        "seg_type_hex": "0x%02x" % seg_type,
        "seg_type_name": SEG_TYPE_NAMES.get(seg_type, "reserved"),
        "access_type": access,
        "access_type_hex": "0x%x" % access,
        "access_type_name": ACCESS_NAMES.get(access, "reserved"),
        "page_mode": page_mode,
        "page_mode_name": "PAGED" if page_mode else "NON_PAGED",
        "pool_index": pool_index,
        "relocatable_bit27": bool(v & QC_RELOCATABLE),
        "bit31": bool(v & (1 << 31)),
        "unknown_high": "0x%08x" % (v & 0x78000000),
    }


def packet_scan(words, extender_model=True):
    lengths = Counter()
    ins = 0
    duplex_ok = 0
    duplex_bad = 0
    extender_count = 0
    leading_extender = 0
    for w in words:
        parse = w & PARSE_MASK
        iclass = w & ICLASS_MASK
        if extender_model:
            if parse == PARSE_ZERO and iclass == ICLASS_EXTENDER:
                if ins == 0:
                    leading_extender += 1
                extender_count += 1
                continue
            if parse == PARSE_ZERO:
                duplex = ((w >> 28) & 0xE) | ((w >> 13) & 0x1)
                if duplex <= 14:
                    duplex_ok += 1
                else:
                    duplex_bad += 1
                ins += 1
                lengths[ins] += 1
                ins = 0
                continue
        if parse == PARSE_NOT_END:
            ins += 1
            continue
        if parse in (PARSE_PACKET_END, PARSE_LOOP_END):
            ins += 1
            lengths[ins] += 1
            ins = 0
            continue
        ins += 1
    total = sum(lengths.values())
    over4 = sum(v for k, v in lengths.items() if k > 4)
    return {
        "packets": total,
        "length_histogram": dict(sorted(lengths.items())),
        "over4": over4,
        "over4_fraction": (over4 / total) if total else 0.0,
        "duplex_ok": duplex_ok,
        "duplex_bad": duplex_bad,
        "extenders": extender_count,
        "leading_extenders": leading_extender,
        "trailing_instructions": ins,
    }


def naive_low2_scan(words):
    lengths = Counter()
    ins = 0
    for w in words:
        low = w & 3
        if low == 1:
            ins += 1
            continue
        ins += 1
        lengths[ins] += 1
        ins = 0
    total = sum(lengths.values())
    over4 = sum(v for k, v in lengths.items() if k > 4)
    return {
        "packets": total,
        "over4": over4,
        "over4_fraction": (over4 / total) if total else 0.0,
    }


def words_at(data, byte_offset):
    n = (len(data) - byte_offset) // 4
    if n <= 0:
        return ()
    return struct.unpack_from("<%dI" % n, data, byte_offset)


def alignment_sweep(data, model="extender"):
    out = []
    for bo in range(4):
        ws = words_at(data, bo)
        if model == "extender":
            r = packet_scan(ws, True)
        elif model == "naive_low2":
            r = naive_low2_scan(ws)
        else:
            r = packet_scan(ws, False)
        out.append(
            {
                "byte_offset": bo,
                "packets": r["packets"],
                "over4": r["over4"],
                "over4_fraction": r["over4_fraction"],
            }
        )
    return out


def printable_run_fraction(data):
    if not data:
        return 0.0
    total = 0
    run = 0
    for x in data:
        if 32 <= x < 127:
            run += 1
        else:
            if run >= 8:
                total += run
            run = 0
    if run >= 8:
        total += run
    return total / len(data)


def entropy_profile(data):
    return {
        "bytes": len(data),
        "sha256": sha256(data),
        "md5": md5(data),
        "entropy_bits_per_byte": round(shannon(data), 6),
        "zero_fraction": round(zero_fraction(data), 6),
        "ascii_printable_fraction": round(ascii_fraction(data), 6),
        "printable_run_fraction": round(printable_run_fraction(data), 6),
    }


def classify_role(p, prof, stats, ref):
    if p["index"] == 0 and p["p_type"] == PT_NULL:
        return ("header/phdr-table",
                "PT_NULL seg-0; p_filesz == e_ehsize + e_phnum*e_phentsize; type-bits 7")
    if (p["p_flags"] & QC_TYPE_MASK) == QC_TYPE_HASH:
        return ("hash/cert-segment",
                "type-bits == 2 (QCOM_MDT_TYPE_HASH); skipped by mdt_phdr_loadable()")
    if p["p_filesz"] == 0:
        return ("BSS (zero-fill)", "p_filesz == 0 and p_memsz > 0; no sibling file")
    if prof["printable_run_fraction"] >= 0.40:
        return ("data (string/table blob)",
                "%.1f%% of bytes lie in printable runs >= 8"
                % (100.0 * prof["printable_run_fraction"]))
    if prof["entropy_bits_per_byte"] < 1.0:
        return ("data (sparse / zero-heavy)",
                "entropy %.3f bits/byte" % prof["entropy_bits_per_byte"])
    if stats["words"] < 2048:
        return ("data (too small for packet statistics)",
                "%d words; below the 2048-word threshold for a stable parse-bit estimate"
                % stats["words"])
    par = stats["parse"]
    if par["p10"] < 0.05 and par["p00"] < 0.25:
        return ("code-like (Hexagon packet statistics)",
                "p10=%.4f (loop-end rare), p00=%.3f (extender/duplex), iClassH=%.2f"
                % (par["p10"], par["p00"], stats["iclass_entropy"]))
    return ("data (parse bits inconsistent with code)",
            "p10=%.4f, p00=%.3f do not match a compiled Hexagon stream"
            % (par["p10"], par["p00"]))


def corpus_mdt_scan(root):
    rows = []
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            if not fn.endswith(".mdt"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                raw = open(path, "rb").read()
            except OSError:
                continue
            hdr = parse_elf(raw)
            if hdr is None or not hdr["phdrs"]:
                continue
            if hdr["e_machine"] != EM_HEXAGON:
                continue
            row = {
                "path": os.path.relpath(path, root),
                "bytes": len(raw),
                "e_machine": hdr["e_machine"],
                "e_flags": "0x%08x" % hdr["e_flags"],
                "e_flags_low12": "0x%03x" % (hdr["e_flags"] & 0x3FF),
                "e_phnum": hdr["e_phnum"],
                "loadable_segments": 0,
                "loadable_rule_violations": [],
                "zero_filesz_segments": 0,
                "zero_filesz_with_sibling": 0,
                "zero_filesz_sibling_nonzero": 0,
                "relocatable": False,
            }
            for p in hdr["phdrs"]:
                sib = sibling_path(path, p["index"])
                exists = os.path.exists(sib)
                size = os.path.getsize(sib) if exists else None
                if p["p_filesz"] == 0:
                    row["zero_filesz_segments"] += 1
                    if exists:
                        row["zero_filesz_with_sibling"] += 1
                        if size:
                            row["zero_filesz_sibling_nonzero"] += 1
                    continue
                if is_loadable(p):
                    row["loadable_segments"] += 1
                    if not exists:
                        row["loadable_rule_violations"].append(
                            [p["index"], "missing", p["p_filesz"], None]
                        )
                    elif size != p["p_filesz"]:
                        row["loadable_rule_violations"].append(
                            [p["index"], "size", p["p_filesz"], size]
                        )
                    if p["p_flags"] & QC_RELOCATABLE:
                        row["relocatable"] = True
            row["loadable_rule_holds"] = not row["loadable_rule_violations"]
            b00 = sibling_path(path, 0)
            b01 = sibling_path(path, 1)
            row["mdt_equals_b00_plus_b01"] = (
                os.path.exists(b00)
                and os.path.exists(b01)
                and os.path.getsize(b00) + os.path.getsize(b01) == len(raw)
            )
            rows.append(row)
    return rows


def parse_histogram(words):
    c = Counter((w >> 14) & 3 for w in words)
    n = len(words) or 1
    return {
        "p00": c[0] / n,
        "p01": c[1] / n,
        "p10": c[2] / n,
        "p11": c[3] / n,
    }


def iclass_entropy(words):
    c = Counter((w >> 28) & 0xF for w in words)
    n = len(words)
    if not n:
        return 0.0
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def gap_scan(words):
    lengths = Counter()
    cur = 0
    for w in words:
        cur += 1
        if (w >> 14) & 3 in (2, 3):
            lengths[cur] += 1
            cur = 0
    total = sum(lengths.values())
    over = sum(v for k, v in lengths.items() if k > 4)
    return {
        "packets": total,
        "over4": over,
        "over4_fraction": (over / total) if total else 1.0,
    }


def segment_stats(data, byte_offset=0):
    ws = words_at(data, byte_offset)
    return {
        "words": len(ws),
        "parse": parse_histogram(ws),
        "gap": gap_scan(ws),
        "iclass_entropy": iclass_entropy(ws),
    }


def text_section(data):
    if len(data) < 52 or data[:4] != b"\x7fELF":
        return None
    hdr = EHDR.unpack_from(data, 0)
    shoff = hdr[6]
    shentsize = hdr[11]
    shnum = hdr[12]
    shstrndx = hdr[13]
    if not shoff or shentsize != 40:
        return None
    count = min(shnum, (len(data) - shoff) // 40)
    if count <= shstrndx:
        return None
    shdrs = [struct.unpack_from("<10I", data, shoff + 40 * i) for i in range(count)]
    strtab = shdrs[shstrndx]
    for sh in shdrs:
        name = data[strtab[4] + sh[0]:].split(b"\x00")[0]
        if name == b".text" and sh[1] == 1:
            off, size = sh[4], sh[5]
            if off + size <= len(data):
                return {"offset": off, "size": size, "data": data[off:off + size]}
    return None


def positive_control(root):
    d = os.path.join(root, "second-device/instantnoodle/dsp-ext4/cdsp")
    if not os.path.isdir(d):
        return None
    picks = ["libnn_preproc.so", "libsysmon_skel.so", "libvpp_mvp.so"]
    out = []
    for name in picks:
        p = os.path.join(d, name)
        if not os.path.exists(p):
            continue
        data = open(p, "rb").read()
        t = text_section(data)
        if not t or t["size"] < 4096:
            continue
        row = {
            "file": name,
            "text_offset": t["offset"],
            "text_size": t["size"],
            "sha256": sha256(t["data"]),
        }
        for bo in range(4):
            s = segment_stats(t["data"], bo)
            row["offset_%d" % bo] = {
                "parse": s["parse"],
                "gap_over4_fraction": s["gap"]["over4_fraction"],
                "gap_packets": s["gap"]["packets"],
            }
        out.append(row)
    return out


def pflag_census(root):
    values = Counter()
    by_role = {}
    files = 0
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in filenames:
            path = os.path.join(dirpath, fn)
            try:
                if os.path.getsize(path) < 64:
                    continue
                with open(path, "rb") as fh:
                    head = fh.read(64)
                    if head[:4] != b"\x7fELF" or head[4] != 1:
                        continue
                    fh.seek(0)
                    raw = fh.read()
            except OSError:
                continue
            hdr = parse_elf(raw)
            if hdr is None or not hdr["phdrs"]:
                continue
            files += 1
            for p in hdr["phdrs"]:
                v = p["p_flags"]
                values[v] += 1
                if p["index"] == 0 and p["p_type"] == PT_NULL:
                    role = "phdr0_ptnull"
                elif (v & QC_TYPE_MASK) == QC_TYPE_HASH:
                    role = "type_hash"
                elif (v & QC_TYPE_MASK) == QC_TYPE_HDR:
                    role = "type_hdr"
                elif p["p_filesz"] == 0 and p["p_memsz"] > 0:
                    role = "bss"
                elif p["p_type"] == PT_LOAD:
                    role = "pt_load"
                else:
                    role = "other"
                if role not in by_role:
                    by_role[role] = Counter()
                by_role[role][v] += 1
    return files, values, by_role


def main():
    argv = sys.argv[1:]
    out_json = None
    mdt_override = None
    positional = []
    skip = False
    for i, a in enumerate(argv):
        if skip:
            skip = False
            continue
        if a == "--json":
            out_json = argv[i + 1] if i + 1 < len(argv) else None
            skip = True
            continue
        if a == "--mdt":
            mdt_override = argv[i + 1] if i + 1 < len(argv) else None
            skip = True
            continue
        if a.startswith("--"):
            continue
        positional.append(a)
    root = positional[0] if positional else DEFAULT_ROOT

    cdir = os.path.join(root, CDSP_SUBDIR)
    mdt_path = mdt_override or os.path.join(cdir, "image_cdsp.mdt")
    jsn_path = os.path.join(os.path.dirname(mdt_path), "image_cdspr.jsn")
    raw = open(mdt_path, "rb").read()
    hdr = parse_elf(raw)
    result = {
        "provenance": {
            "issue": "adineo-cmd/open-device#595",
            "date": "2026-11-20",
            "data_root": root,
            "mdt": mdt_path,
            "mdt_bytes": len(raw),
            "mdt_sha256": sha256(raw),
            "mdt_md5": md5(raw),
        }
    }

    print("=" * 78)
    print("SECTION 1  ELF header of image_cdsp.mdt")
    print("=" * 78)
    print("file           %s" % mdt_path)
    print("bytes          %d" % len(raw))
    print("sha256         %s" % result["provenance"]["mdt_sha256"])
    print("md5            %s" % result["provenance"]["mdt_md5"])
    print()
    print("%-14s %-6s %-6s %-18s %s" % ("field", "offset", "size", "value", "note"))
    hdr_rows = []
    for name, off, size in EHDR_FIELDS:
        val = hdr[name]
        if name == "e_ident":
            shown = val.hex()
            note = "ELF32, little-endian, EV_CURRENT, System V ABI"
            val = val.hex()
        else:
            shown = "%d (0x%x)" % (val, val)
            note = ""
        if name == "e_machine":
            note = "EM_HEXAGON / EM_QDSP6 (include/uapi/linux/elf-em.h)"
        elif name == "e_type":
            note = "ET_EXEC" if val == ET_EXEC else ("ET_DYN" if val == ET_DYN else "?")
        elif name == "e_flags":
            note = "Hexagon ISA nibble = %s; high bits 0x%08x" % (
                HEXAGON_ISA.get(val & 0x3FF, "unmapped"),
                val & 0xFFFFFC00,
            )
        elif name == "e_ehsize":
            note = "== 52, matches Elf32_Ehdr"
        elif name == "e_phentsize":
            note = "== 32, matches Elf32_Phdr"
        elif name == "e_phnum":
            note = "13 program headers"
        elif name == "e_shnum":
            note = "no section headers"
        hdr_rows.append(
            {"field": name, "offset": off, "size": size, "value": val, "note": note}
        )
        print("%-14s %-6d %-6d %-18s %s" % (name, off, size, shown, note))
    result["elf_header"] = {
        "fields": hdr_rows,
        "e_ident_hex": hdr["e_ident"].hex(),
        "e_flags": hdr["e_flags"],
        "e_flags_hex": "0x%08x" % hdr["e_flags"],
        "e_flags_isa_nibble": "0x%03x" % (hdr["e_flags"] & 0x3FF),
        "e_flags_isa_name": HEXAGON_ISA.get(hdr["e_flags"] & 0x3FF, "unmapped"),
        "e_flags_high": "0x%08x" % (hdr["e_flags"] & 0xFFFFFC00),
        "phdr_table_offset": hdr["e_phoff"],
        "phdr_table_end": hdr["e_phoff"] + 32 * hdr["e_phnum"],
        "phdr_table_bytes": 32 * hdr["e_phnum"],
    }

    print()
    print("=" * 78)
    print("SECTION 2  program headers, sibling files, p_filesz rule")
    print("=" * 78)
    segs = []
    print(
        "%-3s %-6s %-8s %-10s %-10s %-9s %-9s %-11s %-9s %s"
        % ("i", "type", "offset", "vaddr", "paddr", "filesz", "memsz", "flags", "sibling", "verdict")
    )
    match = 0
    present = 0
    zero_segs = []
    for p in hdr["phdrs"]:
        sib = sibling_path(mdt_path, p["index"])
        exists = os.path.exists(sib)
        size = os.path.getsize(sib) if exists else None
        if exists:
            present += 1
        if p["p_filesz"] == 0:
            verdict = "ABSENT-as-predicted" if not exists else "PRESENT-but-filesz0"
            zero_segs.append((p["index"], exists, size))
        elif exists and size == p["p_filesz"]:
            verdict = "MATCH"
            match += 1
        elif exists:
            verdict = "SIZE-MISMATCH"
        else:
            verdict = "MISSING"
        print(
            "%-3d %-6d %-8s %-10s %-10s %-9d %-9d %-11s %-9s %s"
            % (
                p["index"],
                p["p_type"],
                "0x%x" % p["p_offset"],
                "0x%08x" % p["p_vaddr"],
                "0x%08x" % p["p_paddr"],
                p["p_filesz"],
                p["p_memsz"],
                "0x%08x" % p["p_flags"],
                ("%d" % size) if exists else "-",
                verdict,
            )
        )
        segs.append(
            {
                "index": p["index"],
                "p_type": p["p_type"],
                "p_offset": p["p_offset"],
                "p_vaddr": p["p_vaddr"],
                "p_paddr": p["p_paddr"],
                "p_filesz": p["p_filesz"],
                "p_memsz": p["p_memsz"],
                "p_flags": p["p_flags"],
                "p_flags_hex": "0x%08x" % p["p_flags"],
                "p_align": p["p_align"],
                "phdr_file_offset": p["_phdr_offset"],
                "sibling_name": os.path.basename(sib),
                "sibling_present": exists,
                "sibling_bytes": size,
                "size_matches_p_filesz": bool(exists and size == p["p_filesz"]),
                "verdict": verdict,
            }
        )

    nonzero = [s for s in segs if s["p_filesz"] > 0]
    print()
    print(
        "nonzero p_filesz segments: %d, of which sibling present and exact-size: %d"
        % (len(nonzero), match)
    )
    print(
        "p_filesz == 0 segments: %d at indices %s; sibling present for %d of them"
        % (
            len(zero_segs),
            [z[0] for z in zero_segs],
            sum(1 for z in zero_segs if z[1]),
        )
    )
    print(
        "all nonzero-p_filesz segments have an exact-size sibling: %s"
        % (match == len(nonzero))
    )

    b00 = open(sibling_path(mdt_path, 0), "rb").read()
    b01 = open(sibling_path(mdt_path, 1), "rb").read()
    concat_ok = b00 + b01 == raw
    print()
    print("b00 == mdt[0:%d]            %s" % (len(b00), b00 == raw[: len(b00)]))
    print("b01 == mdt[%d:]             %s" % (len(b00), b01 == raw[len(b00):]))
    print("b00 + b01 == whole .mdt      %s" % concat_ok)
    print("b00 bytes %d == phdr[0].p_filesz %d" % (len(b00), segs[0]["p_filesz"]))
    print("b01 bytes %d == phdr[1].p_filesz %d" % (len(b01), segs[1]["p_filesz"]))

    result["program_headers"] = {
        "segments": segs,
        "nonzero_filesz_count": len(nonzero),
        "nonzero_filesz_with_exact_sibling": match,
        "zero_filesz_indices": [z[0] for z in zero_segs],
        "zero_filesz_with_sibling": [z[0] for z in zero_segs if z[1]],
        "rule_holds_all_nonzero": match == len(nonzero),
        "mdt_is_b00_plus_b01": concat_ok,
        "b00_bytes": len(b00),
        "b01_bytes": len(b01),
    }

    print()
    print("=" * 78)
    print("SECTION 3  p_flags decoding")
    print("=" * 78)
    print("Layout (coreboot util/qualcomm/mbn_tools.py, GPL-2.0, bits 20-27):")
    print("  31 30 29 28 | 27 pool | 26-24 segment type | 23-21 access | 20 page | 2-0 R/W/X")
    print()
    print("%-3s %-11s %-4s %-6s %-9s %-6s %-9s %-6s %s"
          % ("i", "p_flags", "rwx", "segtyp", "segtyp-name", "access",
             "access-name", "page", "unknown_high"))
    flag_rows = []
    for s in segs:
        d = decode_pflags(s["p_flags"])
        d["index"] = s["index"]
        flag_rows.append(d)
        print(
            "%-3d %-11s %-4s %-6s %-9s %-6s %-9s %-6s %s"
            % (
                s["index"],
                d["raw_hex"],
                d["rwx"],
                d["seg_type_hex"],
                d["seg_type_name"],
                d["access_type_hex"],
                d["access_type_name"],
                d["page_mode_name"],
                d["unknown_high"],
            )
        )
    print()
    print("low 3 bits observed in this image: %s" % sorted({s["p_flags"] & 7 for s in segs}))
    print("segment-type (24-26) observed:     %s"
          % sorted({(s["p_flags"] >> 24) & 7 for s in segs}))
    print("access-type (21-23) observed:      %s"
          % sorted({(s["p_flags"] >> 21) & 7 for s in segs}))
    print("page-mode bit 20 observed:         %s"
          % sorted({(s["p_flags"] >> 20) & 1 for s in segs}))
    print("bit 27 (RELOCATABLE / pool index) on every PT_LOAD: %s"
          % all(decode_pflags(s["p_flags"])["relocatable_bit27"]
                for s in segs if s["p_type"] == PT_LOAD))
    print()
    print("role agreement check, this image:")
    checks = [
        (0, "PHDR", "phdr[0] is the ELF header block"),
        (1, "HASH", "phdr[1] is the hash/certificate segment"),
    ]
    for idx, want, why in checks:
        d = decode_pflags(segs[idx]["p_flags"])
        print("  phdr[%d] type-bits decode to %-5s (expected %-5s) : %s -- %s"
              % (idx, d["seg_type_name"], want, d["seg_type_name"] == want, why))
    ro = [s["index"] for s in segs
          if decode_pflags(s["p_flags"])["access_type_name"] == "RO"]
    rwe = [s["index"] for s in segs
           if decode_pflags(s["p_flags"])["access_type_name"] == "RWE"]
    zi = [s["index"] for s in segs
          if decode_pflags(s["p_flags"])["access_type_name"] == "ZI"]
    print("  access-type RO segments: %s (low 3 bits %s)"
          % (ro, sorted({segs[i]["p_flags"] & 7 for i in ro})))
    print("  access-type RWE segments: %s (low 3 bits %s)"
          % (rwe, sorted({segs[i]["p_flags"] & 7 for i in rwe})))
    print("  access-type ZI segments: %s ; p_filesz of each: %s"
          % (zi, [segs[i]["p_filesz"] for i in zi]))
    print("  ZI segments are exactly the p_filesz==0 set: %s"
          % (sorted(zi) == sorted(z[0] for z in zero_segs)))
    print()
    print("corpus-wide p_flags census, every ELF32 file under the data root:")
    nfiles, allvals, byrole = pflag_census(root)
    print("  files parsed: %d ; distinct p_flags words: %d" % (nfiles, len(allvals)))
    print("  %-11s %-6s %-5s %-9s %-4s %-4s %-4s %s"
          % ("p_flags", "count", "type", "access", "R", "W", "X", "bits"))
    for v, c in sorted(allvals.items()):
        print("  0x%08x %-6d %-5d 0x%-7x %-4d %-4d %-4d %s"
              % (v, c, (v >> 24) & 7, (v >> 21) & 7,
                 int(bool(v & 4)), int(bool(v & 2)), int(bool(v & 1)),
                 [k for k in range(32) if (v >> k) & 1]))
    print()
    print("  by segment role:")
    for role in sorted(byrole):
        print("    %-12s %s" % (role, {("0x%08x" % k): v
                                       for k, v in sorted(byrole[role].items())}))
    low3 = sorted({v & 7 for v in allvals})
    print()
    print("  distinct low-3-bit (R/W/X) values across the corpus: %s" % low3)
    print("  every observed low-3 value lies in 0..7 (standard PF_R/W/X range): %s"
          % all(0 <= v <= 7 for v in low3))
    print("  type-bits values observed: %s"
          % sorted({(v >> 24) & 7 for v in allvals}))
    print("  access-bits (21..23) observed: %s"
          % sorted({(v >> 21) & 7 for v in allvals}))
    print("  bit 27 (QCOM_MDT_RELOCATABLE) words: %d of %d"
          % (sum(c for v, c in allvals.items() if v & QC_RELOCATABLE),
             sum(allvals.values())))

    result["pflags"] = {
        "corpus_census": {
            "files": nfiles,
            "distinct_words": len(allvals),
            "values": {("0x%08x" % k): v for k, v in sorted(allvals.items())},
            "by_role": {
                role: {("0x%08x" % k): v for k, v in sorted(c.items())}
                for role, c in sorted(byrole.items())
            },
            "low3_values": low3,
            "type_values": sorted({(v >> 24) & 7 for v in allvals}),
            "access_values": sorted({(v >> 21) & 7 for v in allvals}),
            "relocatable_words": sum(
                c for v, c in allvals.items() if v & QC_RELOCATABLE
            ),
            "total_words": sum(allvals.values()),
        },
        "segments": flag_rows,
        "low3_values": sorted({s["p_flags"] & 7 for s in segs}),
        "segtype_values": sorted({(s["p_flags"] >> 24) & 7 for s in segs}),
        "access_values": sorted({(s["p_flags"] >> 21) & 7 for s in segs}),
        "bit27_on_all_loadable": all(
            decode_pflags(s["p_flags"])["relocatable_bit27"]
            for s in segs
            if s["p_type"] == PT_LOAD
        ),
    }

    print()
    print("=" * 78)
    print("SECTION 4  ISA evidence (Hexagon packet structure)")
    print("=" * 78)
    print("e_machine = %d = EM_HEXAGON / EM_QDSP6" % hdr["e_machine"])
    print("e_flags   = 0x%08x ; ISA nibble (bits 11:0) = 0x%03x -> %s"
          % (hdr["e_flags"], hdr["e_flags"] & 0x3FF,
             HEXAGON_ISA.get(hdr["e_flags"] & 0x3FF, "unmapped")))
    print()
    print("Parse-bit model (LLVM HexagonBaseInfo.h, Apache-2.0-with-LLVM-exception):")
    print("  bits [15:14] of each little-endian 32-bit word")
    print("    00  iClass 0 -> constant extender or duplex word (NOT a packet end)")
    print("    00  iClass!=0 -> duplex packet, both halves end together")
    print("    01  more instructions follow in this packet")
    print("    10  end of inner loop")
    print("    11  end of packet")
    print("  packet length is 1..4 words. A 5th instruction word in one packet is")
    print("  architecturally impossible, so the >4-word rate is a validity probe.")
    print()
    seg_data = {}
    for s in segs:
        if s["sibling_present"] and s["p_filesz"] > 0:
            seg_data[s["index"]] = open(sibling_path(mdt_path, s["index"]), "rb").read()

    ctrl = positive_control(root)
    ctrl_text = None
    if ctrl:
        ctrl_text = ctrl[0]
        print("POSITIVE CONTROL, real Hexagon code in the same data root:")
        print("  %s .text  offset %d  size %d bytes  sha256 %s"
              % (ctrl_text["file"], ctrl_text["text_offset"],
                 ctrl_text["text_size"], ctrl_text["sha256"]))
        for bo in range(4):
            r = ctrl_text["offset_%d" % bo]
            print("    byte offset +%d : p00=%.3f p01=%.3f p10=%.3f p11=%.3f  gap>4word=%.3f%% (n=%d)"
                  % (bo, r["parse"]["p00"], r["parse"]["p01"], r["parse"]["p10"],
                     r["parse"]["p11"], 100.0 * r["gap_over4_fraction"],
                     r["gap_packets"]))
        print()

    rng = random.Random(595)
    noise = bytes(rng.randrange(256) for _ in range(300000))
    print("NEGATIVE CONTROL, %d bytes of uniform random data:" % len(noise))
    for bo in range(4):
        s = segment_stats(noise, bo)
        print("    byte offset +%d : p00=%.3f p01=%.3f p10=%.3f p11=%.3f  gap>4word=%.3f%% (n=%d)"
              % (bo, s["parse"]["p00"], s["parse"]["p01"], s["parse"]["p10"],
                 s["parse"]["p11"], 100.0 * s["gap"]["over4_fraction"],
                 s["gap"]["packets"]))
    print()

    isa_rows = []
    print("%-3s %-9s %-7s %-7s %-7s %-7s %-7s %-9s %-7s"
          % ("i", "bytes", "p00", "p01", "p10", "p11", "gap>4%", "iClassH", "aligned"))
    for idx in sorted(seg_data):
        data = seg_data[idx]
        s0 = segment_stats(data, 0)
        sweep = [segment_stats(data, bo)["gap"]["over4_fraction"] for bo in range(4)]
        best = min(range(4), key=lambda k: sweep[k])
        aligned = "YES" if best == 0 else "no(+%d)" % best
        print("%-3d %-9d %-7.3f %-7.3f %-7.3f %-7.3f %-7.3f %-9.3f %-7s"
              % (idx, len(data), s0["parse"]["p00"], s0["parse"]["p01"],
                 s0["parse"]["p10"], s0["parse"]["p11"],
                 100.0 * s0["gap"]["over4_fraction"], s0["iclass_entropy"],
                 aligned))
        isa_rows.append(
            {
                "index": idx,
                "bytes": len(data),
                "words": s0["words"],
                "parse_fractions": s0["parse"],
                "gap_over4_fraction": round(s0["gap"]["over4_fraction"], 6),
                "gap_packets": s0["gap"]["packets"],
                "iclass_entropy": round(s0["iclass_entropy"], 6),
                "alignment_best_byte_offset": best,
                "gap_sweep": [round(v, 6) for v in sweep],
                "hexagon_like": bool(
                    s0["gap"]["over4_fraction"] < 0.10
                    and s0["iclass_entropy"] > 2.0
                    and best == 0
                ),
            }
        )

    largest = max(
        (s for s in segs if s["sibling_present"] and s["p_filesz"] > 0),
        key=lambda s: s["p_filesz"],
    )
    big_idx = largest["index"]
    big = seg_data[big_idx]
    print()
    print("largest segment: phdr[%d] %d bytes (%.3f MiB) sibling %s"
          % (big_idx, len(big), len(big) / 1048576.0,
             largest["sibling_name"]))
    print()
    print("packet-length distribution, phdr[%d], parse bits [15:14], gap model:"
          % big_idx)
    big_words = words_at(big, 0)
    lengths = Counter()
    cur = 0
    for w in big_words:
        cur += 1
        if (w >> 14) & 3 in (2, 3):
            lengths[cur] += 1
            cur = 0
    tot = sum(lengths.values())
    for k in sorted(lengths):
        if k <= 8:
            print("  %d word(s)  %8d  %7.3f%%" % (k, lengths[k], 100.0 * lengths[k] / tot))
    over = sum(v for k, v in lengths.items() if k > 4)
    print("  >4 words   %8d  %7.3f%%  (architecturally impossible)"
          % (over, 100.0 * over / tot))
    print("  residue after last packet end: %d words" % cur)

    ext_scan = packet_scan(big_words, True)
    print()
    print("extender/duplex consistency check, phdr[%d]:" % big_idx)
    print("  words with parse=00 and iClass=0 (extender candidate): %d" % ext_scan["extenders"])
    print("  of those, packet-leading (illegal for an extender):     %d"
          % ext_scan["leading_extenders"])
    print("  words with parse=00 and iClass!=0 (duplex):             %d"
          % (ext_scan["duplex_ok"] + ext_scan["duplex_bad"]))
    print("  duplex iClass out of range 0..14:                       %d"
          % ext_scan["duplex_bad"])

    print()
    print("byte-alignment sweep on the gap >4-word rate, phdr[%d]:" % big_idx)
    sweep = []
    for bo in range(4):
        s = segment_stats(big, bo)
        sweep.append(
            {
                "byte_offset": bo,
                "gap_packets": s["gap"]["packets"],
                "gap_over4_fraction": round(s["gap"]["over4_fraction"], 6),
                "parse": {k: round(v, 6) for k, v in s["parse"].items()},
            }
        )
        print("  byte offset +%d : packets %8d  >4-word %7.3f%%"
              % (bo, s["gap"]["packets"], 100.0 * s["gap"]["over4_fraction"]))

    iclass_hist = Counter((w >> 28) & 0xF for w in big_words)
    nw = sum(iclass_hist.values())
    print()
    print("opcode-class (iClass, bits 31:28) histogram, phdr[%d]:" % big_idx)
    for k in sorted(iclass_hist):
        print("  0x%x %-9s %8d  %6.2f%%"
              % (k, ICLASS_NAMES[k], iclass_hist[k],
                 100.0 * iclass_hist[k] / nw))
    print()
    print("all 16 iClass values present: %s ; distinct values: %d"
          % (len(iclass_hist) == 16, len(iclass_hist)))

    result["isa"] = {
        "e_machine": hdr["e_machine"],
        "e_machine_name": "EM_HEXAGON/EM_QDSP6",
        "e_flags_isa_nibble": "0x%03x" % (hdr["e_flags"] & 0x3FF),
        "e_flags_isa_name": HEXAGON_ISA.get(hdr["e_flags"] & 0x3FF, "unmapped"),
        "parse_bits_field": "bits [15:14] of the little-endian 32-bit word",
        "parse_bits_source": "llvm/lib/Target/Hexagon/MCTargetDesc/HexagonBaseInfo.h INST_PARSE_*",
        "positive_control": ctrl,
        "negative_control": {
            "bytes": len(noise),
            "sweep": [
                {
                    "byte_offset": bo,
                    "parse": {k: round(v, 6) for k, v in segment_stats(noise, bo)["parse"].items()},
                    "gap_over4_fraction": round(
                        segment_stats(noise, bo)["gap"]["over4_fraction"], 6),
                }
                for bo in range(4)
            ],
        },
        "largest_segment_index": big_idx,
        "largest_segment_bytes": len(big),
        "largest_segment_packets": tot,
        "largest_segment_length_histogram": dict(sorted(lengths.items())),
        "largest_segment_over4_fraction": round(over / tot, 6),
        "largest_segment_extender_candidates": ext_scan["extenders"],
        "largest_segment_leading_extenders": ext_scan["leading_extenders"],
        "largest_segment_duplex_valid": ext_scan["duplex_ok"],
        "largest_segment_duplex_invalid": ext_scan["duplex_bad"],
        "largest_segment_alignment_sweep": sweep,
        "largest_segment_iclass_entropy": round(iclass_entropy(big_words), 6),
        "iclass_histogram": {
            "0x%x" % k: {"name": ICLASS_NAMES[k], "count": iclass_hist[k]}
            for k in sorted(iclass_hist)
        },
        "all_16_iclass_present": len(iclass_hist) == 16,
        "per_segment": isa_rows,
    }

    print()
    print("=" * 78)
    print("SECTION 5  segment roles, entropy, layout")
    print("=" * 78)
    ref = None
    if ctrl_text:
        ref = {
            "parse": ctrl_text["offset_0"]["parse"],
            "gap_over4_fraction": ctrl_text["offset_0"]["gap_over4_fraction"],
        }
        print("reference (known Hexagon .text, byte offset 0): "
              "p00=%.3f p01=%.3f p10=%.3f p11=%.3f gap>4=%.3f%%"
              % (ref["parse"]["p00"], ref["parse"]["p01"], ref["parse"]["p10"],
                 ref["parse"]["p11"], 100 * ref["gap_over4_fraction"]))
        print()
    print("%-3s %-40s %-8s %-5s %-5s %-6s %-6s %s"
          % ("i", "role", "bytes", "H", "zero%", "ascii%", "gap>4%", "evidence"))
    role_rows = []
    for s in segs:
        idx = s["index"]
        if idx in seg_data:
            prof = entropy_profile(seg_data[idx])
            st = segment_stats(seg_data[idx], 0)
            role, why = classify_role(s, prof, st, ref)
            gapstr = "%.3f" % (100.0 * st["gap"]["over4_fraction"])
            stats_out = st
        else:
            prof = {
                "bytes": 0,
                "entropy_bits_per_byte": 0.0,
                "zero_fraction": 0.0,
                "ascii_printable_fraction": 0.0,
                "sha256": None,
                "md5": None,
            }
            stats_out = {"parse": {"p00": 0.0, "p01": 0.0, "p10": 0.0, "p11": 0.0},
                         "gap": {"packets": 0, "over4": 0, "over4_fraction": 0.0},
                         "words": 0, "iclass_entropy": 0.0}
            role, why = classify_role(s, prof, stats_out, ref)
            gapstr = "-"
        print("%-3d %-40s %-8d %-5.2f %-5.1f %-6.1f %-6s %s"
              % (idx, role, prof["bytes"], prof["entropy_bits_per_byte"],
                 100.0 * prof["zero_fraction"],
                 100.0 * prof["ascii_printable_fraction"],
                 gapstr, why))
        role_rows.append(
            {
                "index": idx,
                "role": role,
                "evidence": why,
                "profile": prof,
                "packet_stats": stats_out,
            }
        )
    for s, r in zip(segs, role_rows):
        s["role"] = r["role"]
        s["role_evidence"] = r["evidence"]
    result["roles"] = role_rows
    result["program_headers"]["segments"] = segs

    total_bytes = sum(s["p_filesz"] for s in segs)
    print()
    print("sum of p_filesz over all 13 phdrs: %d ; .mdt file is %d"
          % (total_bytes, len(raw)))
    print("largest segment: phdr[%d] %d bytes" % (big_idx, len(big)))
    print("smallest nonzero segment: phdr[%d] %d bytes"
          % min(((s["index"], s["p_filesz"]) for s in segs if s["p_filesz"] > 0),
                key=lambda t: t[1]))
    result["layout"] = {
        "sum_p_filesz": total_bytes,
        "mdt_bytes": len(raw),
        "largest_segment_index": big_idx,
        "largest_segment_bytes": len(big),
        "total_sibling_bytes": sum(
            s["sibling_bytes"] for s in segs if s["sibling_bytes"]
        ),
    }

    print()
    print("=" * 78)
    print("SECTION 6  cross-check against image_cdspr.jsn")
    print("=" * 78)
    jsn_raw = open(resolve_jsn(jsn_path), "rb").read() if resolve_jsn(jsn_path) else None
    if jsn_raw is None:
        print("path            (no .jsn manifest beside this image)")
        print("skipped         no manifest present; §6 is source-specific")
        jsn_raw = b"{}"
    jsn = json.loads(jsn_raw.decode("utf-8"))
    print("path            %s" % jsn_path)
    print("bytes           %d" % len(jsn_raw))
    print("sha256          %s" % sha256(jsn_raw))
    print("md5             %s" % md5(jsn_raw))
    print("sr_version      %s" % json.dumps(jsn.get("sr_version")))
    print("sr_domain       %s" % json.dumps(jsn.get("sr_domain")))
    print("sr_service      %s" % json.dumps(jsn.get("sr_service")))
    dom = jsn.get("sr_domain", {})
    print()
    print("declared domain  %s/%s/%s"
          % (dom.get("soc"), dom.get("domain"), dom.get("subdomain")))
    print("qmi_instance_id  %s" % dom.get("qmi_instance_id"))
    print("contains any MDT/phdr/sibling key: %s"
          % any(k in jsn_raw.decode("utf-8").lower()
                for k in ("mdt", "phdr", "b00", "segment", "hash")))
    result["jsn"] = {
        "path": jsn_path,
        "bytes": len(jsn_raw),
        "sha256": sha256(jsn_raw),
        "md5": md5(jsn_raw),
        "sr_version": jsn.get("sr_version"),
        "sr_domain": jsn.get("sr_domain"),
        "sr_service": jsn.get("sr_service"),
        "declared_domain": "%s/%s/%s"
        % (dom.get("soc"), dom.get("domain"), dom.get("subdomain")),
        "qmi_instance_id": dom.get("qmi_instance_id"),
        "mentions_mdt_or_segments": any(
            k in jsn_raw.decode("utf-8").lower()
            for k in ("mdt", "phdr", "b00", "segment", "hash")
        ),
        "repo_crossref": "research/laptop/qualcomm-pil-manifest-family.md",
    }

    print()
    print("=" * 78)
    print("SECTION 7  second device / corpus generalisation")
    print("=" * 78)
    corpus = corpus_mdt_scan(root)
    ok = [c for c in corpus if c["loadable_rule_holds"]]
    concat = [c for c in corpus if c["mdt_equals_b00_plus_b01"]]
    reloc = [c for c in corpus if c["relocatable"]]
    print("EM_HEXAGON split-MDT images found under data root: %d" % len(corpus))
    print("loadable-segment rule holds (sibling present, size == p_filesz): %d/%d"
          % (len(ok), len(corpus)))
    print(".mdt == b00 ++ b01: %d/%d" % (len(concat), len(corpus)))
    print("images with QCOM_MDT_RELOCATABLE on a loadable segment: %d/%d"
          % (len(reloc), len(corpus)))
    bad = [c for c in corpus if not c["loadable_rule_holds"]]
    if bad:
        print()
        print("rule violations:")
        for c in bad:
            print("  %s : %s" % (c["path"], c["loadable_rule_violations"]))
    print()
    print("%-62s %-7s %-9s %s" % ("path", "seg", "flags", "e_flags"))
    for c in corpus:
        print("%-62s %-7d %-9s %s"
              % (c["path"], c["loadable_segments"], c["e_flags"], c["e_flags_low12"]))
    print()
    print("distinct e_flags low-12 (ISA nibble) across the corpus: %s"
          % sorted({c["e_flags_low12"] for c in corpus}))
    print("distinct e_flags words: %s" % sorted({c["e_flags"] for c in corpus}))
    result["corpus"] = {
        "images": len(corpus),
        "rule_holds": len(ok),
        "concat_holds": len(concat),
        "relocatable_images": len(reloc),
        "violations": bad,
        "rows": corpus,
        "distinct_e_flags_low12": sorted({c["e_flags_low12"] for c in corpus}),
        "distinct_e_flags": sorted({c["e_flags"] for c in corpus}),
    }

    print()
    print("=" * 78)
    print("SECTION 8  metadata region inside b01")
    print("=" * 78)
    prefix = b01[:24]
    print("b01 prefix (24 B): %s" % prefix.hex())
    print("b01 prefix as u32 LE: %s" % [hex(u32(prefix, 4 * i)) for i in range(6)])
    recs = [b01[24 + 32 * i:24 + 32 * (i + 1)] for i in range((len(b01) - 24) // 32)]
    print("b01 32-byte records after prefix: %d, distinct: %d, all-zero: %d"
          % (len(recs), len(set(recs)), sum(1 for r in recs if r == b"\x00" * 32)))
    der = [i for i in range(len(b01) - 4) if b01[i] == 0x30 and b01[i + 1] == 0x82]
    der_chain = []
    off = der[0] if der else None
    while off is not None and off < len(b01) and b01[off] == 0x30 and b01[off + 1] == 0x82:
        ln = struct.unpack_from(">H", b01, off + 2)[0]
        if off + 4 + ln > len(b01):
            break
        der_chain.append({"offset": off, "length": ln + 4})
        off = off + 4 + ln
    print("DER SEQUENCE (0x30 0x82) candidates: %d" % len(der))
    print("contiguous DER certificate chain: %s" % json.dumps(der_chain))
    if der_chain:
        print("first certificate sample (16 B at its offset): %s"
              % b01[der_chain[0]["offset"]:der_chain[0]["offset"] + 16].hex())
    print("sample of hash-table region (16 B at b01 offset 24+32*8): %s"
          % b01[24 + 32 * 8:24 + 32 * 8 + 16].hex())
    result["b01_metadata"] = {
        "prefix_hex": prefix.hex(),
        "prefix_u32": [u32(prefix, 4 * i) for i in range(6)],
        "record_count": len(recs),
        "distinct_records": len(set(recs)),
        "all_zero_records": sum(1 for r in recs if r == b"\x00" * 32),
        "der_chain": der_chain,
        "sample_hash_record_hex": b01[24 + 32 * 8:24 + 32 * 8 + 16].hex(),
    }

    print()
    print("=" * 78)
    print(
        "SUMMARY cdsp.mdt bytes=%d phdr=%d nonzero_filesz=%d sibling_exact=%d/%d "
        "zero_filesz_idx=%s zero_filesz_sibling=%d b00_plus_b01=%s "
        "relocatable=%s isa_nibble=%s largest_seg=%d over4=%.3f%% "
        "align0=%.3f%% align1=%.3f%% code_like=%d corpus=%d/%d"
        % (
            len(raw),
            hdr["e_phnum"],
            len(nonzero),
            match,
            len(nonzero),
            ",".join(str(z[0]) for z in zero_segs),
            sum(1 for z in zero_segs if z[1]),
            concat_ok,
            result["pflags"]["bit27_on_all_loadable"],
            result["elf_header"]["e_flags_isa_nibble"],
            big_idx,
            100.0 * result["isa"]["largest_segment_over4_fraction"],
            100.0 * sweep[0]["gap_over4_fraction"],
            100.0 * sweep[1]["gap_over4_fraction"],
            sum(1 for r in role_rows if r["role"].startswith("code-like")),
            len(ok),
            len(corpus),
        )
    )
    print("=" * 78)

    if out_json:
        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote %s" % out_json)


if __name__ == "__main__":
    main()
