import hashlib
import json
import os
import struct
import sys

path, outdir = sys.argv[1], sys.argv[2]
os.makedirs(outdir, exist_ok=True)
data = open(path, "rb").read()

byts = struct.unpack_from("<H", data, 11)[0]
spc = data[13]
rsvd = struct.unpack_from("<H", data, 14)[0]
nfats = data[16]
rootents = struct.unpack_from("<H", data, 17)[0]
fatsz = struct.unpack_from("<H", data, 22)[0]
total_sectors = struct.unpack_from("<H", data, 19)[0] or struct.unpack_from("<I", data, 32)[0]

root_start = (rsvd + nfats * fatsz) * byts
root_bytes = rootents * 32
data_start = root_start + root_bytes


def fat_entry(n):
    return struct.unpack_from("<H", data, (rsvd) * byts + n * 2)[0]


def read_chain(first, size=0):
    out = bytearray()
    c = first
    seen = set()
    while 2 <= c < 0xFFF7 and c not in seen:
        seen.add(c)
        out += data[data_start + (c - 2) * spc * byts:data_start + (c - 1) * spc * byts]
        c = fat_entry(c)
    return bytes(out[:size]) if size else bytes(out)


def name83(e):
    base = e[0:8].decode("latin-1").rstrip()
    ext = e[8:11].decode("latin-1").rstrip()
    return base + ("." + ext if ext else "")


def walk_dir(blob, prefix, result):
    for i in range(0, len(blob), 32):
        e = blob[i:i + 32]
        if e[0] in (0x00, 0xE5) or len(e) < 32:
            continue
        if e[11] & 0x08:
            continue
        nm = name83(e)
        if nm.startswith("."):
            continue
        first = struct.unpack_from("<H", e, 26)[0]
        size = struct.unpack_from("<I", e, 28)[0]
        if e[11] & 0x10:
            sub = read_chain(first)
            walk_dir(sub, prefix + nm + "/", result)
        else:
            blob2 = read_chain(first, size)
            result["files"].append({
                "path": prefix + nm, "size": size, "first_cluster": first,
                "chain_bytes": len(read_chain(first)),
                "size_check": len(blob2) == size,
                "md5": hashlib.md5(blob2).hexdigest(),
                "head_hex": blob2[:16].hex(),
            })
            open(os.path.join(outdir, prefix.replace("/", "_") + nm), "wb").write(blob2)


result = {"bytes_per_sector": byts, "sectors_per_cluster": spc, "reserved": rsvd,
          "fats": nfats, "fat_sectors": fatsz, "root_entries": rootents,
          "total_sectors": total_sectors, "volume_bytes": total_sectors * byts,
          "image_bytes": len(data), "files": []}
walk_dir(data[root_start:root_start + root_bytes], "", result)
print(json.dumps(result, indent=1, sort_keys=True))
