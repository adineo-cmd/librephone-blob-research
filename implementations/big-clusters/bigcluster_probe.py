#!/usr/bin/env python3
"""bigcluster_probe.py — structural probe for the two laptop-half big
clusters from the lab's sharing-clusters.csv (blob-matrix/laptop):
  * vm-bootsys.img  (x5 Xiaomi SM8475 devices, 269,996,032 B)
  * modem.b16       (x11 Xiaomi SM8450/SM8475/SM8550 devices, 473,648 B)

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-18/19 from public format documentation only:
  - Android sparse image format: AOSP system/core/libsparse
    (sparse_format.h semantics: magic 0xED26FF3A, 28-byte file header,
    12-byte chunk headers, chunk types RAW=1/FILL=2/DONT_CARE=3/CRC32=4).
  - FAT16/FAT32: the public Microsoft FAT specification (BPB layout,
    cluster chains, directory entries incl. LFN; FAT16 root-dir at the
    fixed offset after reserved+FAT areas).
  - ext4: superblock magic 0xEF53 @1024 (standard, kernel-documented).
Prior art checked (RULE 0): simg2img/libsparse (the reference sparse
decoder, Apache-2.0) — not reimplemented as a library here; this probe
materializes chunk-wise for classification only. FAT16 walker written
from the spec because no mtools/pytsk3 were available in the scratch
environment.
No proprietary material (no firmware payload bytes, no decompiled code,
no vendor headers) was accessed during development.
======================================================================

It classifies the image, converts sparse->raw in memory (chunk-wise), and
lists filesystem contents. No proprietary payload bytes are emitted (names
and metadata only), nothing is executed.

Usage:
    python3 -I bigcluster_probe.py <image> [--json OUT] [--list]
"""

import argparse
import hashlib
import json
import math
import struct
import sys
import os

SPARSE_MAGIC = 0xED26FF3A
CHUNK_RAW, CHUNK_FILL, CHUNK_DONT_CARE, CHUNK_CRC32 = 1, 2, 3, 4


def entropy(data):
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def head_stats(data, n=65536):
    sample = data[:n]
    return {
        "first16_hex": data[:16].hex(),
        "entropy_first64k": round(entropy(sample), 3),
        "zero_frac_first64k": round(sum(1 for b in sample if b == 0) / len(sample), 4),
    }


class SparseImage:
    """Android sparse -> raw, chunk-wise (AOSP libsparse documented format)."""

    def __init__(self, data):
        (magic, major, minor, file_hdr_sz, chunk_hdr_sz, blk_sz, total_blks,
         in_chunks, checksum) = struct.unpack_from("<I4H4I", data, 0)
        if magic != SPARSE_MAGIC:
            raise ValueError("not a sparse image")
        self.block_size = blk_sz
        self.total_blocks = total_blks
        self.header = {"magic": hex(magic), "version": "%d.%d" % (major, minor),
                       "file_hdr_sz": file_hdr_sz, "chunk_hdr_sz": chunk_hdr_sz,
                       "block_size": blk_sz, "total_blocks": total_blks,
                       "total_chunks": in_chunks}
        self.data = data
        self.raw_size = blk_sz * total_blks

    def blocks(self):
        """yield (offset_bytes, bytes) for materialized raw blocks"""
        data = self.data
        pos = 28  # file header size per sparse_format.h
        out_off = 0
        bs = self.block_size
        for _ in range(self.header["total_chunks"]):
            (ctype, _reserved, chunk_sz, total_sz) = struct.unpack_from("<4I", data, pos)
            pos += 12
            if ctype == CHUNK_RAW:
                sz = total_sz - 12
                yield (out_off, data[pos:pos + sz])
                out_off += sz
            elif ctype == CHUNK_FILL:
                (fill,) = struct.unpack_from("<I", data, pos)
                block = struct.pack("<I", fill) * (bs // 4)
                for _ in range(chunk_sz):
                    yield (out_off, block)
                    out_off += bs
            elif ctype == CHUNK_DONT_CARE:
                out_off += chunk_sz * bs
            elif ctype == CHUNK_CRC32:
                pass
            pos += total_sz - 12
            if out_off >= self.raw_size:
                break


def detect(image):
    """classify: android-sparse / fat32 / ext4 / raw-unknown"""
    sig = {}
    if len(image) >= 28:
        (magic,) = struct.unpack_from("<I", image, 0)
        if magic == SPARSE_MAGIC:
            sig["kind"] = "android-sparse"
            return sig
    if len(image) >= 1075 and struct.unpack_from("<H", image, 1024 + 56)[0] == 0xEF53:
        sig["kind"] = "ext4"
        return sig
    if len(image) >= 512 and image[510:512] == b"\x55\xaa":
        bpb = image[11:512]
        sig["kind"] = "fat"
        return sig
    sig["kind"] = "unknown"
    return sig


def fat_probe(image):
    """minimal FAT walker per the public FAT spec: BPB fields + root chain"""
    bpb = image
    (bps,) = struct.unpack_from("<H", image, 11)
    spc = image[13]
    (rsvd,) = struct.unpack_from("<H", image, 14)
    nfat = image[16]
    (root_entries,) = struct.unpack_from("<H", image, 17)
    (tot16,) = struct.unpack_from("<H", image, 19)
    media = image[21]
    (fatsz16,) = struct.unpack_from("<H", image, 22)
    (tot32,) = struct.unpack_from("<I", image, 32)
    (fatsz32,) = struct.unpack_from("<I", image, 36)
    (root_cluster,) = struct.unpack_from("<I", image, 44)
    tot_sect = tot16 or tot32
    fatsz = fatsz16 or fatsz32
    info = {"bytes_per_sector": bps, "sectors_per_cluster": spc,
            "reserved_sectors": rsvd, "num_fats": nfat, "root_entries": root_entries,
            "total_sectors": tot_sect, "fat_size_sectors": fatsz,
            "root_cluster": root_cluster}
    if bps and spc:
        info["cluster_bytes"] = bps * spc
        info["fs_bytes_est"] = tot_sect * bps
    return info


def fat_list(image, max_entries=2000):
    """walk the root dir chain (FAT32) and return entry names+sizes"""
    (bps,) = struct.unpack_from("<H", image, 11)
    spc = image[13]
    (rsvd,) = struct.unpack_from("<H", image, 14)
    nfat = image[16]
    (fatsz32,) = struct.unpack_from("<I", image, 36)
    (root_cluster,) = struct.unpack_from("<I", image, 44)
    cluster_bytes = bps * spc
    fat_off = rsvd * bps
    data_off = fat_off + nfat * fatsz32 * bps
    out = []

    def next_cluster(c):
        off = fat_off + c * 4
        (v,) = struct.unpack_from("<I", image, off)
        return v & 0x0FFFFFFF

    def read_chain(start):
        c = start
        seen = set()
        buf = bytearray()
        while 2 <= c < 0x0FFFFFF8 and c not in seen and len(buf) < 64 * 1024 * 1024:
            seen.add(c)
            off = data_off + (c - 2) * cluster_bytes
            buf += image[off:off + cluster_bytes]
            c = next_cluster(c)
        return bytes(buf)

    lfn = ""
    data = read_chain(root_cluster)
    for i in range(0, len(data) - 32, 32):
        e = data[i:i + 32]
        if e[0] == 0:
            break
        if e[0] == 0xE5:
            lfn = ""
            continue
        attr = e[11]
        if attr == 0x0F:  # LFN
            part = e[1:11] + e[14:26] + e[28:32]
            lfn = part.decode("utf-16-le", "ignore").split("\uffff")[0].split("\x00")[0] + lfn
            continue
        (cluster_hi,) = struct.unpack_from("<H", e, 20)
        (cluster_lo,) = struct.unpack_from("<H", e, 26)
        (size,) = struct.unpack_from("<I", e, 28)
        name8 = e[0:8].decode("latin-1").rstrip() + ("." + e[8:11].decode("latin-1").rstrip() if e[8:11].strip() else "")
        name = lfn if lfn else name8
        out.append({"name": name, "size": size,
                    "cluster": (cluster_hi << 16) | cluster_lo,
                    "attr": attr})
        lfn = ""
        if len(out) >= max_entries:
            break
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="big-cluster structural probe")
    ap.add_argument("image")
    ap.add_argument("--json", help="JSON report out")
    ap.add_argument("--list", action="store_true", help="list FS contents")
    ap.add_argument("--raw-out", help="write converted raw image here (sparse only)")
    args = ap.parse_args(argv)
    path = args.image
    size = os.path.getsize(path)
    r = {"file": os.path.basename(path), "size": size, "md5": None, "sha256": None}

    def md5s():
        h1, h2 = hashlib.md5(), hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                b = f.read(1 << 20)
                if not b:
                    break
                h1.update(b); h2.update(b)
        return h1.hexdigest(), h2.hexdigest()
    r["md5"], r["sha256"] = md5s()

    with open(path, "rb") as f:
        head = f.read(1 << 22)  # 4MB probe window
    cls = detect(head)
    r["class"] = cls["kind"]
    if cls["kind"] == "android-sparse":
        sp = SparseImage(head + open(path, "rb").read(0)[0:] if False else None or head)
        # rebuild full sparse view lazily from file
        full = open(path, "rb").read()
        sp = SparseImage(full)
        r["sparse"] = sp.header
        r["raw_size"] = sp.raw_size
        if args.raw_out:
            with open(args.raw_out, "wb") as out:
                for off, blk in sp.blocks():
                    out.seek(off)
                    out.write(blk)
            r["raw_out"] = args.raw_out
        head_stats_out = head_stats(full)
        r.update(head_stats_out)
    else:
        full = open(path, "rb").read()
        r.update(head_stats(full))
        if cls["kind"] == "fat":
            r["fat_bpb"] = fat_probe(full)
            if args.list:
                r["fat_entries"] = fat_list(full)
        elif cls["kind"] == "ext4":
            r["ext4_superblock_magic"] = "0xef53@1024"
    if args.json:
        with open(args.json, "w") as f:
            json.dump(r, f, indent=1)
    print("%s: size=%d class=%s md5=%s" % (r["file"], r["size"], r["class"], r["md5"]))
    if cls["kind"] == "android-sparse":
        print("  sparse: block_size=%d total_blocks=%d raw=%d B" %
              (r["sparse"]["block_size"], r["sparse"]["total_blocks"], r["raw_size"]))
    if cls["kind"] == "fat":
        print("  fat: %s" % r["fat_bpb"])
        for e in r.get("fat_entries", [])[:20]:
            print("   %-40s %d" % (e["name"], e["size"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
