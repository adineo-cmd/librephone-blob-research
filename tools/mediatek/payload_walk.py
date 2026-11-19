#!/usr/bin/env python3
"""payload_walk.py — split MediaTek mtk_hdr (0x58881688) containers into
sub-image payload files, one directory per partition.

Empirical layout (verified on rosemary LineageOS 24.0 20261104, MT6785):
  record header (512 B):
    0x00 magic 0x58881688
    0x04 payload size (u32 LE)
    0x08 name, NUL-padded ASCII (>= 8 bytes; may run past 0x10)
    0x30 ext magic 0x58891689 (when present)
    0x34 header size (0x200), 0x38 flag, 0x44 payload alignment (0x10)
  payload at +0x200, next record at align(payload_end).
  Every payload observed is followed by cert1 (1709 B) + cert2 (957 B) DER
  X.509 signature records of its own.

GFH 'MMM\\x01' chains (preloader, md1dsp) are recorded but not split here.
Derived facts only.

Usage: python3 -I payload_walk.py <parts-dir> <out-trees-dir>
"""
import os
import re
import struct
import sys

LK_MAGIC = 0x58881688
GFH_MAGIC = 0x58891689


def safe_name(n):
    return re.sub(r"[^A-Za-z0-9._-]", "_", n) or "unnamed"


def walk(path, outdir):
    blob = open(path, "rb").read()
    os.makedirs(outdir, exist_ok=True)
    off = 0
    n = 0
    index = []
    while off + 0x210 <= len(blob) and n < 64:
        magic, size = struct.unpack_from("<II", blob, off)
        if magic != LK_MAGIC:
            break
        name_raw = blob[off + 8:off + 0x28].split(b"\x00", 1)[0]
        try:
            name = name_raw.decode("ascii")
        except UnicodeDecodeError:
            name = name_raw.hex()
        ext = {}
        if len(blob) >= off + 0x48:
            m2 = struct.unpack_from("<I", blob, off + 0x30)[0]
            if m2 == GFH_MAGIC:
                ext = {
                    "header_size": struct.unpack_from("<I", blob, off + 0x34)[0],
                    "flag_0x38": struct.unpack_from("<I", blob, off + 0x38)[0],
                    "word_0x3c": struct.unpack_from("<I", blob, off + 0x3C)[0],
                    "align_0x44": struct.unpack_from("<I", blob, off + 0x44)[0],
                }
        pstart = off + 0x200
        pend = pstart + size
        payload = blob[pstart:pend] if pend <= len(blob) else b""
        fn = f"{n:02d}_{safe_name(name)}.bin"
        with open(os.path.join(outdir, fn), "wb") as f:
            f.write(payload)
        index.append({
            "name": name, "size": size, "offset": off,
            "payload_offset": pstart, "file": fn, "ext": ext,
        })
        n += 1
        align = (ext.get("align_0x44") or 16) or 16
        off = (pend + align - 1) & ~(align - 1)
    return index


def main():
    parts, trees = sys.argv[1], sys.argv[2]
    for fn in sorted(os.listdir(parts)):
        if not fn.endswith(".img"):
            continue
        part = fn[:-4]
        blob = open(os.path.join(parts, fn), "rb").read()
        if blob[:4] == b"\x7fELF":
            kind = "ELF"
        elif struct.unpack_from("<I", blob, 0)[0] == LK_MAGIC:
            kind = "mtk_hdr"
        elif blob.startswith(b"MMM\x01"):
            kind = "GFH-MMM-chain"
        elif blob.startswith(b"AVB0"):
            kind = "AVB"
        else:
            kind = "unknown"
        outdir = os.path.join(trees, part)
        idx = walk(os.path.join(parts, fn), outdir) if kind == "mtk_hdr" else []
        print(f"{part}: {kind}, {len(idx)} records")
        for r in idx:
            print(f"   {r['name']:<24} size={r['size']:>9,} -> {r['file']}")


if __name__ == "__main__":
    main()
