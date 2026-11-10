#!/usr/bin/env python3
"""census_mtk.py — MediaTek blob census (derived facts only).

Walks extracted MTK firmware images/partition dumps and records, per file:
  size, sha256[:16], magic sniff, ELF metadata (class/endian/type/machine/
  entry/program headers), MediaTek LK/GFH container structure (magic
  0x58881688, GFH_FILE_INFO 0x58891689, cert2 signature blocks, sub-images),
  md1img-style file-table container entries, and targeted version strings.

Adapted from open-discovery-lab track-a-android-blobs/tools/census.py.
Header/layout knowledge cross-checked against:
  - bkerler/mtkclient gfh.py (LK/GFH header magic values)
  - nccgroup/mtk_bp md1_extract.py (md1img file table: name/addr/size entries)
  - CrimsonGlory/wairz mediatek_gfh.py (compact vs legacy LK name offsets)
Never emits binary content: safe to commit.

Usage:
  python3 -I census_mtk.py <root> [--out census.json] [--hexdump LOG]
"""
import argparse
import hashlib
import json
import os
import re
import struct
from collections import Counter

# ---------------------------------------------------------------- constants
EM_NAMES = {
    2: "SPARC", 3: "x86", 8: "MIPS", 20: "PowerPC", 40: "ARM",
    42: "SuperH", 50: "IA-64", 62: "x86-64", 83: "AVR",
    92: "Altera Nios II", 94: "RISC-V (old, bespoke)", 183: "AArch64",
    164: "QDSP6 / Hexagon", 243: "RISC-V", 247: "BPF", 252: "C-SKY",
    166: "Xtensa", 190: "ARC", 216: "Kalimba (CSR)",
}

PF_NAMES = {1: "X", 2: "W", 4: "R"}
PT_NAMES = {
    0: "NULL", 1: "LOAD", 2: "DYNAMIC", 3: "INTERP", 4: "NOTE",
    6: "PHDR", 7: "TLS",
    0x60000000: "LOOS", 0x6474e550: "GNU_EH_FRAME", 0x6474e551: "GNU_STACK",
    0x6474e552: "GNU_RELRO", 0x6474e553: "GNU_PROPERTY",
    0x70000000: "LOPROC", 0x70000001: "ARM_EXIDX",
    0x68000000: "HIOS",
}

LK_MAGIC = 0x58881688          # MediaTek LK/GFH container record header
LK_FILE_INFO_MAGIC = 0x58891689  # GFH_FILE_INFO record
LK_HEADER_SIZE = 0x200         # container record header total size

# md1img file-table container (nccgroup/mtk_bp): entries {name, addr, size}
MD1_ENTRY_NAMES = re.compile(
    rb"^(md1rom|md1drdi|md1dsp|md1_filter|md1_emfilter|md1_dbginfodsp|"
    rb"md1_dbginfo|md1_mddbmeta|md1_mddbmetaodb|md1_mddb|md1_mdmlayout|"
    rb"md1_file_map|cert1md|cert2)")

VERSION_PATTERNS = [
    ("moly", re.compile(rb"MOLY[.\w/:-]{4,80}")),
    ("mdl_rom", re.compile(rb"MDL_[A-Z_0-9]{2,40}")),
    ("md_dbgi", re.compile(rb"DbgInfo [.\w_/-]{4,120}")),
    ("tinysys", re.compile(rb"tinysys [.\w_/-]{2,60}")),
    ("elbrus", re.compile(rb"ELBRUS [.\w_/-]{0,60}")),
    ("ver_opt", re.compile(rb"VER(?:ION)?[ :=_]{0,3}[.\w/-]{4,60}")),
    ("mtk_chip", re.compile(rb"MT[0-9]{4}[A-Z0-9_]{0,8}")),
    ("pcm_spm", re.compile(rb"(?:PCM|SPM)[.\w_ -]{4,60}")),
    ("scp_vcore", re.compile(rb"scp [.\w_/-]{2,60}", re.I)),
    ("tee", re.compile(rb"(?:GenieZone|beanpod|TEE_[A-Za-z0-9_]{2,40}|tlApi|drApi|mtk_sec)[\w.:/-]{0,50}")),
    ("swver", re.compile(rb"SW(?:_)?VER[A-Z_0-9:= ./-]{2,60}")),
    ("flavor", re.compile(rb"(?:K69V1|K6853|MT6785|ELBRUS|LG855|G95)[\w.:/-]{0,60}")),
]


def sniff_magic(head: bytes):
    if head.startswith(b"\x7fELF"):
        return "ELF"
    if len(head) >= 4:
        magic = struct.unpack_from("<I", head, 0)[0]
        if magic == LK_MAGIC:
            return "MTK-LK-CONTAINER"
    if head.startswith(b"MMM\x01"):
        return "MTK-MMM-CHAIN"
    if head.startswith(b"AVB0"):
        return "AVB"
    if head.startswith(b"BZh"):
        return "BZIP2"
    if head.startswith(b"PK\x03\x04"):
        return "ZIP"
    if head.startswith(b"\xfd7zXZ"):
        return "XZ"
    if head.startswith(b"\x1f\x8b"):
        return "GZIP"
    if head.startswith(b"VXA"):
        return "MTK-VXA(?)"
    if head.startswith(b"BOOTLDR"):
        return "BOOTLDR"
    return None


# ---------------------------------------------------------------- ELF parse
def parse_elf(blob: bytes, max_phdrs: int = 32):
    """Parse ELF header + program headers from in-memory bytes (stdlib only)."""
    info = {"is_elf": False}
    head = blob[:64]
    if len(head) < 64 or not head.startswith(b"\x7fELF"):
        return info
    info["is_elf"] = True
    ei_class, ei_data = head[4], head[5]
    info["class"] = {1: "ELF32", 2: "ELF64"}.get(ei_class, f"unk{ei_class}")
    info["endian"] = {1: "LE", 2: "BE"}.get(ei_data, f"unk{ei_data}")
    fmt = "<" if ei_data == 1 else ">"
    try:
        if ei_class == 1:
            e_type, e_machine = struct.unpack_from(fmt + "HH", head, 16)
            e_entry, e_phoff = struct.unpack_from(fmt + "II", head, 24)
            e_phentsize, e_phnum = struct.unpack_from(fmt + "HH", head, 42)
            ph_fmt, ph_size = fmt + "IIIIIIII", 32
        else:
            e_type, e_machine = struct.unpack_from(fmt + "HH", head, 16)
            e_entry, e_phoff = struct.unpack_from(fmt + "QQ", head, 24)
            e_phentsize, e_phnum = struct.unpack_from(fmt + "HH", head, 54)
            ph_fmt, ph_size = fmt + "IIQQQQQQ", 56
        info["phoff"] = e_phoff
        info["type"] = {1: "REL", 2: "EXEC", 3: "DYN", 4: "CORE"}.get(e_type, e_type)
        info["machine_id"] = e_machine
        info["machine"] = EM_NAMES.get(e_machine, f"UNKNOWN({e_machine})")
        info["entry"] = e_entry
        info["phnum"] = e_phnum
        phdrs = []
        loads = []
        off = e_phoff
        for _ in range(min(e_phnum, max_phdrs)):
            if off + ph_size > len(blob):
                break
            raw = blob[off:off + ph_size]
            off += ph_size
            if ei_class == 1:
                p_type, p_off, p_vaddr, _pa, p_filesz, _m, p_flags, _a = struct.unpack(ph_fmt, raw)
            else:
                p_type, p_flags, p_off, p_vaddr, _pa, p_filesz, _m, _a = struct.unpack(ph_fmt, raw)
            name = PT_NAMES.get(p_type, hex(p_type))
            phdrs.append({
                "type": name,
                "flags": "".join(PF_NAMES.get(b, "?") for b in (4, 2, 1) if p_flags & b),
                "offset": p_off, "vaddr": p_vaddr, "filesz": p_filesz,
            })
            if p_type == 1:
                loads.append((p_vaddr, p_vaddr + p_filesz))
        info["phdrs"] = phdrs
        # entry-point sanity: entry must land inside a PT_LOAD file range
        if loads:
            inside = any(lo <= e_entry < hi or (lo <= e_entry - 1 < hi and e_entry & 1)
                         for lo, hi in loads)
            info["entry_in_load"] = bool(inside)
            info["vaddr_span"] = [min(l[0] for l in loads), max(l[1] for l in loads)]
            if e_machine == 40:
                info["thumb_entry"] = bool(e_entry & 1)
        else:
            info["entry_in_load"] = False
    except (struct.error, IndexError) as e:
        info["error"] = str(e)
    return info


# ------------------------------------------------------- MTK LK/GFH container
def parse_lk_container(blob: bytes):
    """Parse MediaTek LK record header + GFH_FILE_INFO + sub-image chain."""
    out = {}
    if len(blob) < 0x40:
        return out
    magic, file_info_off = struct.unpack_from("<II", blob, 0)
    out["lk_magic"] = hex(magic)
    out["lk_file_info_offset"] = file_info_off
    # compact layout (MT6785-era): 8-byte name at 0x08; legacy: 32-byte at 0x20
    name_c = blob[8:16].split(b"\x00", 1)[0]
    name_l = blob[0x20:0x40].split(b"\x00", 1)[0]
    def plausible(n):
        return bool(n) and re.fullmatch(rb"[A-Za-z][A-Za-z0-9_\-]{0,31}", n)
    name = None
    if plausible(name_c):
        out["layout"] = "compact-16B"
        name = name_c
    elif plausible(name_l):
        out["layout"] = "legacy-512B"
        name = name_l
    if name:
        out["lk_name"] = name.decode("ascii", "replace")
    if len(blob) >= 0x14:
        out["word_0x0c"] = struct.unpack_from("<I", blob, 0x0C)[0]
    if len(blob) >= 0x10:
        out["word_0x08_if_name_slot"] = blob[8:16].hex() if not plausible(name_c) else None
    # GFH/mtk_hdr extension record at 0x30 (48):
    #   0x30 magic 0x58891689, 0x34 header size, 0x38.., 0x44 payload alignment
    align = 16
    if len(blob) >= 0x34:
        m2 = struct.unpack_from("<I", blob, 0x30)[0]
        if m2 == LK_FILE_INFO_MAGIC:
            fi = {"magic_at": 0x30}
            if len(blob) >= 0x38:
                fi["header_size"] = struct.unpack_from("<I", blob, 0x34)[0]
            if len(blob) >= 0x3C:
                fi["word_0x38"] = struct.unpack_from("<I", blob, 0x38)[0]
            if len(blob) >= 0x40:
                fi["word_0x3c"] = struct.unpack_from("<I", blob, 0x3C)[0]
            if len(blob) >= 0x48:
                w44 = struct.unpack_from("<I", blob, 0x44)[0]
                fi["word_0x44"] = w44
                if w44 and (w44 & (w44 - 1)) == 0 and w44 <= 4096:
                    align = w44
                else:
                    fi["word_0x44_note"] = "not power-of-two <= 4096"
            out["gfh_file_info"] = fi
    # walk sub-images: header(0x200) + payload, next header alignment-aligned after
    subs = []
    off = 0
    while off + 0x40 <= len(blob) and len(subs) < 32:
        m, sz = struct.unpack_from("<II", blob, off)
        if m != LK_MAGIC:
            break
        nm = blob[off + 8:off + 0x20].split(b"\x00", 1)[0]
        nm = nm.decode("ascii", "replace") if plausible(nm) else "?"
        pstart = off + LK_HEADER_SIZE
        pend = pstart + sz
        sub = {"name": nm, "size": sz, "offset": off}
        if pend <= len(blob):
            sub["payload_is_elf"] = blob[pstart:pstart + 4] == b"\x7fELF"
            sub["payload_first8"] = blob[pstart:pstart + 8].hex()
        subs.append(sub)
        if pend <= off:
            break
        off = (pend + align - 1) & ~(align - 1)
    if subs:
        out["subimages"] = subs
        out["subimage_align"] = align
    return out


# ------------------------------------------------------- md1img file table
def parse_md1_table(blob: bytes):
    """Probe for the md1img file-table container (name/addr/size entries).

    Empirical (per nccgroup/mtk_bp md1_extract.py): header then entries of
    {name[32], addr, size}? — we detect by finding 'md1rom' early and dump
    the first 64 bytes hex for manual mapping; exact stride is determined
    after inspection.
    """
    out = {}
    i = blob.find(b"md1rom")
    if i < 0 or i > 4096:
        return out
    out["md1rom_at"] = i
    # try entry stride: name(32B) + addr(4) + size(4)? or name(8)+addr+size?
    # record hex of a window for manual decode
    win = blob[max(0, i - 8):i + 40]
    out["window_hex"] = win.hex()
    return out


# ---------------------------------------------------------------- strings
def extract_strings(blob: bytes, limit=40):
    """Run targeted version regexes over the whole file; return grouped hits."""
    found = {}
    for tag, rx in VERSION_PATTERNS:
        hits = set()
        for m in rx.finditer(blob):
            s = m.group(0).decode("ascii", "replace").strip()
            if len(s) >= 5:
                hits.add(s[:100])
            if len(hits) >= 8:
                break
        if hits:
            found[tag] = sorted(hits)[:limit]
    return found


def sha16(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def census_file(path, rel, hexdump_log=None):
    size = os.path.getsize(path)
    row = {"path": rel, "size": size, "sha256_16": sha16(path)}
    with open(path, "rb") as f:
        head = f.read(256)
    row["magic"] = sniff_magic(head)
    blob = None
    with open(path, "rb") as f:
        if size <= 64 << 20:
            blob = f.read()
        else:
            blob = f.read(64 << 20)
    if row["magic"] == "MTK-LK-CONTAINER":
        row["lk"] = parse_lk_container(blob)
        # ELF metadata of the primary payload (after the 0x200 header)
        if blob[0x200:0x204] == b"\x7fELF":
            row["elf"] = parse_elf(blob[0x200:0x200 + (4 << 20)])
    elif row["magic"] == "ELF":
        row["elf"] = parse_elf(blob)
    row["md1_table"] = parse_md1_table(blob)
    row["strings"] = extract_strings(blob)
    if hexdump_log is not None and size < 1 << 22:
        hexdump_log.write(f"\n===== {rel} ({size} bytes) =====\n")
        hexdump_log.write(blob[:512].hex())
        hexdump_log.write("\n")
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", default="census.json")
    ap.add_argument("--hexdump", default=None)
    args = ap.parse_args()

    rows = []
    machines = Counter()
    hexlog = open(args.hexdump, "w") if args.hexdump else None
    for dirpath, _dirs, files in os.walk(args.root):
        for fn in sorted(files):
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, args.root)
            try:
                row = census_file(full, rel, hexlog)
                rows.append(row)
                elf = row.get("elf") or {}
                if elf.get("is_elf"):
                    machines[elf.get("machine", "?")] += 1
                for sub in (row.get("lk", {}).get("subimages") or []):
                    pass  # sub-image ELF payloads parsed by follow-up tool
            except Exception as e:
                rows.append({"path": rel, "error": f"{type(e).__name__}: {e}"})
    if hexlog:
        hexlog.close()
    with open(args.out, "w") as f:
        json.dump({"root": args.root, "files": rows, "machines": dict(machines)},
                  f, indent=1)
    print(f"census: {len(rows)} files, machines={dict(machines)} -> {args.out}")


if __name__ == "__main__":
    main()
