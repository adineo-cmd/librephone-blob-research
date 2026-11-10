#!/usr/bin/env python3
"""region_scan.py — entropy-scan a raw payload to locate real code regions,
then report ISA decode plausibility at the best candidate windows.

Usage: python3 region_scan.py <file>
"""
import math
import sys
from capstone import (Cs, CS_ARCH_ARM, CS_ARCH_MIPS, CS_MODE_ARM, CS_MODE_THUMB,
                      CS_MODE_MIPS32, CS_MODE_LITTLE_ENDIAN)

CHUNK = 4096


def entropy(b):
    if not b:
        return 0.0
    counts = [0] * 256
    for x in b:
        counts[x] += 1
    n = len(b)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def decode_rate(code, arch, mode, n=64):
    md = Cs(arch, mode)
    got = 0
    mnems = []
    for i in md.disasm(code, 0):
        got += 1
        if got <= 4:
            mnems.append(f"{i.mnemonic} {i.op_str}")
        if got >= n:
            break
    return got, mnems


def main():
    path = sys.argv[1]
    blob = open(path, "rb").read()
    print(f"{path}: {len(blob):,} bytes")
    # entropy map, 4KB windows
    regions = []
    for off in range(0, min(len(blob), 4 << 20), CHUNK):
        e = entropy(blob[off:off + CHUNK])
        regions.append((off, e))
    # report profile: fraction of windows in entropy bands
    hi = sum(1 for _, e in regions if e > 6.0)
    mid = sum(1 for _, e in regions if 3.0 < e <= 6.0)
    low = sum(1 for _, e in regions if e <= 3.0)
    print(f"4KB windows: high-entropy(>6.0)={hi} mid={mid} low={low}")
    # print entropy profile every 64KB
    for off in range(0, min(len(blob), 1 << 20), 65536):
        w = [e for o, e in regions if off <= o < off + 65536]
        if w:
            print(f"  {off:#010x}: avg entropy {sum(w)/len(w):.2f} "
                  f"max {max(w):.2f}")
    # probe candidate code offsets: windows with mid/high entropy, aligned
    cands = [o for o, e in regions if 4.5 < e <= 6.8][:40]
    seen = set()
    for off in cands:
        key = off // 65536
        if key in seen:
            continue
        seen.add(key)
        code = blob[off:off + 2048]
        out = []
        for name, arch, mode in (("arm32", CS_ARCH_ARM, CS_MODE_ARM),
                                 ("thumb2", CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN),
                                 ("mips32", CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN)):
            got, mn = decode_rate(code, arch, mode, 64)
            out.append(f"{name}={got}/64 {mn[:2]}")
        print(f"@{off:#x}: " + " | ".join(out))


if __name__ == "__main__":
    main()
