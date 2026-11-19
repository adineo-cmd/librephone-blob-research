#!/usr/bin/env python3
"""
bm2n_container_probe.py — header/segment-table parser and fleet-diff metrics for
Qualcomm ADSP `bm2nXX.bin` blobs.

Evidence class: MEASURED PAYLOADS. No prior art parse of this container exists
publicly as of 2026-11-18 (see the companion .md for the audit trail); every
claim below is derived from the bytes and labelled with the sample it holds on.

Usage:
    python3 bm2n_container_probe.py DIR [DIR ...]

Every *.bin in the given directories is parsed. Files whose u32@0x00 is not a
plausible load base (i.e. not one of 0x200000/0x400000/0x800000) are reported
as NOT-the-container rather than silently skipped.

Derived layout (12/12 distinct blobs, 48 files):

    0x00  u32    load_base          segment-0 load address; duplicated at 0x1c
                                     and equal to entry[0].addr
    0x04  u32    0                   reserved (constant 0)
    0x08  u32    build_id_len        == strlen(build_id); always 7 in the sample
    0x0c  char[8] build_id           ASCII NUL-terminated, e.g. "5371806"
    0x14  u32    0xfa0000fa          magic marker (constant)
    0x18  u32    4                   constant; purpose unresolved
    0x1c  u32    load_base           repeat of 0x00
    0x20  u32    segment_count       nseg (2..4 observed)
    0x24  { u32 addr; u32 flags } x nseg
    0x24+8*nseg  u32  terminator == ((~nseg & 0xffff) << 16) | nseg

`addr` fields are LOAD ADDRESSES, not file offsets: they routinely exceed the
file size (e.g. bm2n13 entry[1].addr = 0xac7000 in a 0x10e400-byte file).
"""

import hashlib
import itertools
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

MAGIC = 0xFA0000FA
LOAD_BASES = (0x00200000, 0x00400000, 0x00800000)
HDR_END_MIN = 0x24


def u32(b, off):
    return struct.unpack_from("<I", b, off)[0]


def parse(blob):
    """Return a dict describing the container, or None if it is not one."""
    if len(blob) < 0x60:
        return None
    base = u32(blob, 0x00)
    if base not in LOAD_BASES:
        return None
    nseg = u32(blob, 0x20)
    if not (1 <= nseg <= 8):
        return None
    tbl_off = 0x24
    term_off = tbl_off + 8 * nseg
    if term_off + 4 > len(blob):
        return None
    segs = []
    for k in range(nseg):
        addr, flags = struct.unpack_from("<II", blob, tbl_off + 8 * k)
        segs.append({"addr": addr, "flags": flags})
    term = u32(blob, term_off)
    predicted_term = (((~nseg) & 0xFFFF) << 16) | nseg
    build_id = blob[12:20].split(b"\x00")[0]
    return {
        "load_base": base,
        "reserved_04": u32(blob, 0x04),
        "build_id_len": u32(blob, 0x08),
        "build_id": build_id.decode("ascii", "replace"),
        "magic_14": u32(blob, 0x14),
        "const_18": u32(blob, 0x18),
        "base_1c": u32(blob, 0x1C),
        "nseg": nseg,
        "segments": segs,
        "terminator": term,
        "terminator_predicted": predicted_term,
        "terminator_ok": term == predicted_term,
        "bases_agree": base == u32(blob, 0x1C) == segs[0]["addr"],
        "magic_ok": u32(blob, 0x14) == MAGIC,
        "size": len(blob),
        "md5": hashlib.md5(blob).hexdigest(),
    }


def lcp(a, b):
    n = min(len(a), len(b))
    i = 0
    while i < n and a[i] == b[i]:
        i += 1
    return i


def identity(a, b):
    """Same-offset byte identity over the min length, as a percentage."""
    n = min(len(a), len(b))
    same = sum(1 for i in range(n) if a[i] == b[i])
    return same, n, same / n * 100.0


def nonzero_identity(a, b):
    n = min(len(a), len(b))
    same = sum(1 for i in range(n) if a[i] == b[i] and a[i] != 0)
    return same, same / n * 100.0


def chance_identity(a, b):
    """sum_v pA(v)*pB(v) — null model: bodies statistically independent."""
    ca, cb = Counter(a), Counter(b)
    na, nb = len(a), len(b)
    return sum(ca[v] / na * cb[v] / nb for v in set(ca) | set(cb)) * 100.0


def main(argv):
    dirs = [Path(p) for p in argv[1:]] or [Path(".")]
    payloads = {}
    for d in dirs:
        for p in sorted(d.glob("*.bin")):
            payloads[str(p)] = p.read_bytes()

    if not payloads:
        print("no .bin files found", file=sys.stderr)
        return 1

    parsed, rejected = {}, {}
    for name, blob in payloads.items():
        info = parse(blob)
        if info is None:
            rejected[name] = blob
        else:
            parsed[name] = (blob, info)

    print(f"files scanned : {len(payloads)}")
    print(f"container ok  : {len(parsed)}")
    print(f"NOT container : {len(rejected)}")
    for name, blob in rejected.items():
        print(f"   {name}  size={len(blob):,}  u32@0x00={u32(blob, 0) if len(blob) >= 4 else 0:#010x}"
              f"  md5={hashlib.md5(blob).hexdigest()}")

    # ---- structural invariants -------------------------------------------
    print("\n== structural invariants ==")
    checks = {
        "magic@0x14 == 0xfa0000fa": lambda i: i["magic_ok"],
        "reserved@0x04 == 0": lambda i: i["reserved_04"] == 0,
        "build_id_len == strlen": lambda i: i["build_id_len"] == len(i["build_id"]),
        "load_base == 0x1c == entry[0].addr": lambda i: i["bases_agree"],
        "terminator formula": lambda i: i["terminator_ok"],
    }
    for label, fn in checks.items():
        ok = sum(1 for _, i in parsed.values() if fn(i))
        print(f"  {label:38} {ok}/{len(parsed)}")

    # ---- distinct payloads ------------------------------------------------
    uniq = {}
    for name, (blob, info) in parsed.items():
        uniq.setdefault(info["md5"], (name, blob, info))
    print(f"\ndistinct container payloads: {len(uniq)}")

    print("\n== per-blob header ==")
    hdr = (f"{'blob':34}{'size':>10}{'base':>10}{'bid':>9}{'nseg':>5}"
           f"{'entry0.flags':>14}{'terminator':>12}")
    print(hdr)
    for name, blob, i in sorted(uniq.values(), key=lambda t: (t[2]["build_id"], t[2]["size"])):
        print(f"{Path(name).name:34}{i['size']:>10,}{i['load_base']:>#10x}{i['build_id']:>9}"
              f"{i['nseg']:>5}{i['segments'][0]['flags']:>#14x}{i['terminator']:>#12x}")

    print("\n== segment flag values by table position ==")
    by_pos = defaultdict(Counter)
    for _, _, i in uniq.values():
        for k, s in enumerate(i["segments"]):
            by_pos[k][s["flags"]] += 1
    for k in sorted(by_pos):
        vals = {hex(v): c for v, c in by_pos[k].items()}
        print(f"  entry[{k}]: {vals}")

    # ---- does load_base track build-id? -----------------------------------
    print("\n== load_base grouped by build-id (is it a build-lineage property?) ==")
    by_bid = defaultdict(set)
    for _, _, i in uniq.values():
        by_bid[i["build_id"]].add(i["load_base"])
    for bid in sorted(by_bid):
        vals = sorted(hex(v) for v in by_bid[bid])
        tag = "constant" if len(vals) == 1 else "*** VARIES ***"
        print(f"  {bid:>9}: {vals}  {tag}")

    # ---- similarity matrix ------------------------------------------------
    items = list(uniq.values())
    print("\n== pairwise similarity, grouped by build-id equality ==")
    groups = defaultdict(list)
    for (n1, b1, i1), (n2, b2, i2) in itertools.combinations(items, 2):
        key = (i1["build_id"] == i2["build_id"])
        same, n, pct = identity(b1, b2)
        _, nzpct = nonzero_identity(b1, b2)
        groups[key].append((Path(n1).name, Path(n2).name, lcp(b1, b2),
                            pct, nzpct, chance_identity(b1, b2)))
    for same_bid in (True, False):
        g = groups[same_bid]
        if not g:
            continue
        idp = [x[3] for x in g]
        nz = [x[4] for x in g]
        ch = [x[5] for x in g]
        lcps = sorted({x[2] for x in g})
        print(f"  build_id {'EQUAL' if same_bid else 'DIFF ':5} n={len(g):3}"
              f"  identity mean={sum(idp)/len(idp):6.2f}%"
              f"  non-zero mean={sum(nz)/len(nz):5.2f}%"
              f"  chance mean={sum(ch)/len(ch):6.2f}%"
              f"  lcp set={lcps}")

    print("\n  ratio (measured / chance identity):")
    for same_bid in (True, False):
        g = groups[same_bid]
        if not g:
            continue
        r = [x[3] / x[5] for x in g if x[5]]
        print(f"    build_id {'EQUAL' if same_bid else 'DIFF ':5}: mean ratio={sum(r)/len(r):.2f}"
              f"  max={max(r):.2f}")

    sep_same = min((x[2] for x in groups[True]), default=0)
    sep_diff = max((x[2] for x in groups[False]), default=0)
    print(f"\n== lcp separation: min(lcp | same build-id)={sep_same}"
          f"  max(lcp | different)={sep_diff}"
          f"  -> clean separator: {sep_same > sep_diff}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
