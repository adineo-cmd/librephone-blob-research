#!/usr/bin/env python3
"""hexagon_probe.py -- clean-room structural probe for Qualcomm Hexagon
modem/ADSP firmware containers (``qdsp6sw.mbn``, ``*.mdt`` + ``*.bNN``,
``*_skel.so``).

CLEAN-ROOM STATEMENT
--------------------
This file was written from public sources only:

  * ``include/uapi/linux/elf.h`` and the ELF gABI (public, standardised):
    the ``Elf32_Ehdr`` / ``Elf32_Phdr`` field order used here.
  * ``drivers/soc/qcom/mdt_loader.c`` (GPL-2.0-only, torvalds/linux) --
    the split-MDT contract: an ``.mdt`` is a normal ELF whose ``PT_LOAD``
    segments are stored in ``.bNN`` sibling files in program-header order.
  * ``drivers/remoteproc/qcom_q6v5_pas.c`` (GPL-2.0-only) -- which
    ``e_machine`` values the mainline remoteproc driver accepts.
  * ``llvm/lib/Target/Hexagon`` and ``llvm/include/llvm/BinaryFormat/ELF.h``
    (Apache-2.0 WITH LLVM-exception) -- ``EM_QDSP6`` and the Hexagon
    ``e_flags`` architecture-version nibble.
  * ``QNN/HTP`` headers (BSD-3-Clause-Clear) -- not used here.

plus **own structural measurements** of the payload bytes. No decompiled
code, no proprietary documentation and no vendor header was read. Every
number this tool prints is either (a) read from the file in front of it,
or (b) one of the public constants named above. Anything else is reported
as ``[OPEN]`` rather than guessed.

WHAT IS ESTABLISHED (own measurement)
-------------------------------------
Two container generations ship the same Hexagon image:

``monolithic``
    one ELF file holding every ``PT_LOAD`` segment inline. ``qdsp6sw.mbn``
    is this form: 84,123,868 B, 29 program headers, no section headers.

``split-MDT``
    an ``.mdt`` ELF that carries only the header block, plus ``.b00`` ..
    ``.bNN`` sibling files holding the segments. This is what
    ``mdt_loader.c`` documents.

The distinguishing structural invariant, measured on the `EM_QDSP6` objects in this
corpus: a *header-only* image has program header 0 as
``p_type=PT_NULL, p_offset=0, p_memsz=0, p_filesz=ehsize+phnum*phentsize,
p_flags=0x07000000``, i.e. segment 0 *is* the ELF header plus the program
header table. Monolithic images instead open with a real ``PT_LOAD`` at
file offset 0.

The vendor's ``p_flags`` bits are the ones mainline Linux names: the type
field ``bits[26:24]`` (``QCOM_MDT_TYPE_MASK``) with ``0x2`` meaning "this is
the hash/metadata segment" (``QCOM_MDT_TYPE_HASH``), and ``BIT(27)``
(``QCOM_MDT_RELOCATABLE``) marking the image relocatable. Both are defined in
``include/linux/soc/qcom/mdt_loader.h`` since v4.11 and used by
``mdt_loader.c``; the low three bits remain the standard R/W/X. The kernel
finds the metadata segment by the *type field*, not by ``p_type``, which is
why segment 1 can be ``PT_NULL`` and still be the one that gets validated.

USAGE
    python3 -I hexagon_probe.py <file> [--json out.json] [--brief] [--quiet]
    python3 -I hexagon_probe.py --dir <dir> [--json out.json]

Exit codes: 0 valid, 1 parseable but violating an invariant, 2 unparseable.
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys
import zlib

EM_QDSP6 = 164
ET_EXEC = 2
ET_DYN = 3
PT_NULL = 0
PT_LOAD = 1
MDT_TYPE_MASK = 0x07000000
MDT_TYPE_HASH = 0x02000000
MDT_RELOCATABLE = 0x08000000
HDR_SEG_FLAGS = 0x07000000
META_SEG_FLAGS = 0x02200000
EHDR = struct.Struct("<16sHHIIIIIHHHHHH")
PHDR = struct.Struct("<8I")

HEXAGON_ARCH = {
    0x60: "v60",
    0x61: "v61",
    0x62: "v62",
    0x63: "v63",
    0x64: "v64",
    0x65: "v65",
    0x66: "v66",
    0x67: "v67",
    0x68: "v68",
    0x69: "v69",
    0x73: "v73",
    0x75: "v75",
    0x79: "v79",
}

SECTION_MAGIC = (
    (b"\x7fELF", "elf"),
    (b"QDB\x00", "qdb"),
    (b"\x78\x9c", "zlib-default"),
    (b"\x78\xda", "zlib-best"),
    (b"\x78\x01", "zlib-fastest"),
    (b"PDPF", "clip"),
)


class ProbeError(Exception):
    pass


def entropy(buf):
    if not buf:
        return 0.0
    counts = [0] * 256
    for byte in buf:
        counts[byte] += 1
    n = len(buf)
    total = 0.0
    for c in counts:
        if c:
            p = c / n
            total -= p * math.log2(p)
    return total


def entropy_words(buf):
    if len(buf) < 4:
        return 0.0
    counts = {}
    for i in range(0, len(buf) - 3, 4):
        w = buf[i:i + 4]
        counts[w] = counts.get(w, 0) + 1
    n = sum(counts.values())
    total = 0.0
    for c in counts.values():
        p = c / n
        total -= p * math.log2(p)
    return total


def parse_ehdr(data):
    if len(data) < EHDR.size:
        raise ProbeError("file shorter than an ELF32 header")
    if data[:4] != b"\x7fELF":
        raise ProbeError("no ELF magic")
    if data[4] != 1:
        raise ProbeError("not ELF32 (EI_CLASS=%d)" % data[4])
    if data[5] != 1:
        raise ProbeError("not little-endian (EI_DATA=%d)" % data[5])
    fields = EHDR.unpack_from(data, 0)
    names = (
        "e_ident", "e_type", "e_machine", "e_version", "e_entry", "e_phoff",
        "e_shoff", "e_flags", "e_ehsize", "e_phentsize", "e_phnum",
        "e_shentsize", "e_shnum", "e_shstrndx",
    )
    hdr = dict(zip(names, fields))
    hdr["e_ident"] = data[:16].hex()
    return hdr


def parse_phdrs(data, hdr):
    if hdr["e_phnum"] == 0:
        return []
    if hdr["e_phentsize"] != PHDR.size:
        raise ProbeError("phentsize %d != 32" % hdr["e_phentsize"])
    end = hdr["e_phoff"] + hdr["e_phnum"] * PHDR.size
    if end > len(data):
        raise ProbeError("program header table runs past EOF")
    out = []
    for i in range(hdr["e_phnum"]):
        off = hdr["e_phoff"] + i * PHDR.size
        p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = \
            PHDR.unpack_from(data, off)
        out.append({
            "index": i,
            "p_type": p_type,
            "p_offset": p_offset,
            "p_vaddr": p_vaddr,
            "p_paddr": p_paddr,
            "p_filesz": p_filesz,
            "p_memsz": p_memsz,
            "p_flags": p_flags,
            "p_align": p_align,
            "mdt_type": (p_flags & MDT_TYPE_MASK) >> 24,
            "mdt_type_hash": (p_flags & MDT_TYPE_MASK) == MDT_TYPE_HASH,
            "mdt_relocatable": bool(p_flags & MDT_RELOCATABLE),
            "read": bool(p_flags & 4),
            "write": bool(p_flags & 2),
            "execute": bool(p_flags & 1),
            "file_range": [p_offset, p_offset + p_filesz],
        })
    return out


def classify_phdr(ph, hdr, data):
    flags = ph["p_flags"]
    if ph["p_type"] == PT_NULL and ph["p_offset"] == 0 and ph["p_memsz"] == 0 \
            and ph["p_filesz"] == hdr["e_ehsize"] + hdr["e_phnum"] * hdr["e_phentsize"] \
            and flags == HDR_SEG_FLAGS:
        return "header-table"
    if ph["p_type"] == PT_NULL and flags == META_SEG_FLAGS:
        return "metadata"
    if ph["p_type"] != PT_LOAD:
        return "non-load"
    if ph["p_filesz"] == 0:
        return "bss"
    body = data[ph["p_offset"]:ph["p_offset"] + min(ph["p_filesz"], 64)]
    for magic, name in SECTION_MAGIC:
        if body.startswith(magic):
            if name == "zlib-default" or name.startswith("zlib"):
                return "zlib-compressed"
            return "embedded-" + name
    if entropy(body) < 0.5:
        return "fill"
    if ph["execute"]:
        return "code"
    if ph["read"] and not ph["write"]:
        return "rodata"
    return "rwdata"


def inflate_probe(data, ph):
    if ph["p_filesz"] < 8:
        return None
    body = data[ph["p_offset"]:ph["p_offset"] + ph["p_filesz"]]
    if body[:2] not in (b"\x78\x9c", b"\x78\xda", b"\x78\x01"):
        return None
    try:
        out = zlib.decompress(body)
    except zlib.error as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "inflated_bytes": len(out),
        "ratio": round(len(out) / len(body), 3),
        "first16": out[:16].hex(),
    }


def find_embedded(data, magic, limit=8):
    hits = []
    start = 0
    while len(hits) < limit:
        at = data.find(magic, start)
        if at < 0:
            break
        hits.append(at)
        start = at + 1
    return hits


def gap_analysis(phdrs, filesize):
    spans = []
    for ph in phdrs:
        if ph["p_filesz"] == 0:
            continue
        spans.append((ph["p_offset"], ph["p_offset"] + ph["p_filesz"], ph["index"]))
    spans.sort()
    gaps = []
    cursor = 0
    for begin, end, idx in spans:
        if begin > cursor:
            gaps.append({"at": cursor, "bytes": begin - cursor,
                         "before_segment": idx})
        cursor = max(cursor, end)
    if cursor < filesize:
        gaps.append({"at": cursor, "bytes": filesize - cursor,
                     "before_segment": None})
    return gaps


def split_siblings(path, phdrs, hdr):
    stem = os.path.splitext(os.path.basename(path))[0]
    directory = os.path.dirname(os.path.abspath(path))
    found = {}
    for name in os.listdir(directory):
        base, ext = os.path.splitext(name)
        if base != stem:
            continue
        if len(ext) == 4 and ext[1] == "b" and ext[2:].isdigit():
            found[int(ext[2:])] = os.path.join(directory, name)
    if not found:
        return None
    table_end = hdr["e_ehsize"] + hdr["e_phnum"] * hdr["e_phentsize"]
    rows = []
    for index in sorted(found):
        size = os.path.getsize(found[index])
        ph = phdrs[index] if index < len(phdrs) else None
        expected = ph["p_filesz"] if ph else None
        if index == 0:
            expected = table_end
        rows.append({
            "index": index,
            "file": os.path.basename(found[index]),
            "bytes": size,
            "p_filesz": ph["p_filesz"] if ph else None,
            "expected_bytes": expected,
            "size_matches": (size == expected),
        })
    present = set(found)
    absent = []
    for index, ph in enumerate(phdrs):
        if index in present:
            continue
        absent.append({
            "index": index,
            "p_filesz": ph["p_filesz"],
            "p_memsz": ph["p_memsz"],
            "reason": "p_filesz==0" if ph["p_filesz"] == 0 else "missing",
        })
    return {"present": rows, "absent": absent}


def overlap_check(phdrs):
    spans = sorted((p["p_offset"], p["p_offset"] + p["p_filesz"], p["index"])
                   for p in phdrs if p["p_filesz"] > 0 and p["p_type"] == PT_LOAD)
    bad = []
    for i in range(1, len(spans)):
        if spans[i][0] < spans[i - 1][1]:
            bad.append({"a": spans[i - 1][2], "b": spans[i][2]})
    return bad


def probe(path):
    with open(path, "rb") as handle:
        data = handle.read()
    hdr = parse_ehdr(data)
    if hdr["e_machine"] != EM_QDSP6:
        raise ProbeError("e_machine %d is not EM_QDSP6 (%d)"
                         % (hdr["e_machine"], EM_QDSP6))
    phdrs = parse_phdrs(data, hdr)
    for ph in phdrs:
        ph["kind"] = classify_phdr(ph, hdr, data)
        if ph["p_filesz"]:
            body = data[ph["p_offset"]:ph["p_offset"] + ph["p_filesz"]]
            ph["entropy"] = round(entropy(body[:262144]), 3)
            ph["entropy_words"] = round(entropy_words(body[:262144]), 3)
            ph["fill_pct"] = (round(100.0 * ph["p_filesz"] / ph["p_memsz"], 1)
                              if ph["p_memsz"] else None)
            ph["head16"] = body[:16].hex()
        else:
            ph["entropy"] = 0.0
            ph["entropy_words"] = 0.0
            ph["fill_pct"] = 0.0
            ph["head16"] = ""
        z = inflate_probe(data, ph)
        if z is not None:
            ph["zlib"] = z
    first = phdrs[0] if phdrs else None
    header_table_first = bool(first and first["kind"] == "header-table")
    inline = all(p["p_offset"] + p["p_filesz"] <= len(data)
                 for p in phdrs if p["p_filesz"])
    if not header_table_first:
        generation = "monolithic"
    elif inline:
        generation = "self-contained"
    else:
        generation = "split-mdt"
    loads = [p for p in phdrs if p["p_type"] == PT_LOAD]
    total_filesz = sum(p["p_filesz"] for p in phdrs)
    siblings = split_siblings(path, phdrs, hdr) if generation == "split-mdt" else None
    result = {
        "path": os.path.abspath(path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "e_type": hdr["e_type"],
        "e_type_name": {2: "EXEC", 3: "DYN"}.get(hdr["e_type"], "?"),
        "e_machine": hdr["e_machine"],
        "e_flags": hdr["e_flags"],
        "e_flags_hex": hex(hdr["e_flags"]),
        "hexagon_arch": HEXAGON_ARCH.get(hdr["e_flags"] & 0xFF,
                                        "unknown(%#x)" % (hdr["e_flags"] & 0xFF)),
        "e_flags_high": hex(hdr["e_flags"] & 0xFFFFFF00),
        "e_entry": hdr["e_entry"],
        "e_phoff": hdr["e_phoff"],
        "e_phnum": hdr["e_phnum"],
        "e_shnum": hdr["e_shnum"],
        "has_section_headers": hdr["e_shnum"] > 0,
        "generation": generation,
        "load_segments": len(loads),
        "total_p_filesz": total_filesz,
        "uncovered_bytes": len(data) - total_filesz,
        "gaps": gap_analysis(phdrs, len(data)),
        "overlaps": overlap_check(phdrs),
        "program_headers": phdrs,
        "split_siblings": siblings,
        "embedded_elf_offsets": find_embedded(data, b"\x7fELF"),
        "relocatable_segments": sum(1 for p in phdrs if p["mdt_relocatable"]),
        "hash_segment": next((p["index"] for p in phdrs if p["mdt_type_hash"]), None),
    }
    violations = []
    if hdr["e_phoff"] != hdr["e_ehsize"] and hdr["e_phnum"]:
        violations.append("e_phoff %d != e_ehsize %d"
                          % (hdr["e_phoff"], hdr["e_ehsize"]))
    if result["overlaps"]:
        violations.append("%d overlapping file ranges" % len(result["overlaps"]))
    for ph in phdrs:
        if ph["p_filesz"] and ph["p_offset"] + ph["p_filesz"] > len(data) \
                and generation != "split-mdt":
            violations.append("segment %d runs past EOF" % ph["index"])
        if ph["p_memsz"] and ph["p_memsz"] < ph["p_filesz"]:
            violations.append("segment %d p_memsz < p_filesz" % ph["index"])
    if generation == "split-mdt" and not siblings:
        violations.append("split-MDT header with no .bNN siblings found")
    result["violations"] = violations
    return result


def brief_line(res):
    return ("%s: %dB %s %s %s phnum=%d load=%d gaps=%dB [%s]"
            % (os.path.basename(res["path"]), res["bytes"], res["e_type_name"],
               res["hexagon_arch"], res["generation"], res["e_phnum"],
               res["load_segments"],
               sum(g["bytes"] for g in res["gaps"]),
               "OK" if not res["violations"] else "%dVIOL" % len(res["violations"])))


def render(res):
    out = []
    out.append("file            %s" % res["path"])
    out.append("bytes           %d" % res["bytes"])
    out.append("sha256          %s" % res["sha256"])
    out.append("e_type          %d (%s)" % (res["e_type"], res["e_type_name"]))
    out.append("e_machine       %d (EM_QDSP6)" % res["e_machine"])
    out.append("e_flags         %s  -> hexagon %s, high %s"
               % (res["e_flags_hex"], res["hexagon_arch"], res["e_flags_high"]))
    out.append("e_entry         %#x" % res["e_entry"])
    out.append("phdrs           %d (e_phoff %d)" % (res["e_phnum"], res["e_phoff"]))
    out.append("shdrs           %d%s" % (res["e_shnum"],
               "" if res["has_section_headers"] else "  (none: no section headers)"))
    out.append("generation      %s" % res["generation"])
    out.append("hash segment    %s  (p_flags TYPE field == QCOM_MDT_TYPE_HASH)"
               % ("none" if res["hash_segment"] is None else res["hash_segment"]))
    out.append("relocatable     %d segments (QCOM_MDT_RELOCATABLE, BIT(27))"
               % res["relocatable_segments"])
    out.append("covered bytes   %d of %d (%d uncovered)"
               % (res["total_p_filesz"], res["bytes"], res["uncovered_bytes"]))
    out.append("")
    out.append(" idx type  off        vaddr      paddr      filesz      memsz"
               "       flags     rwx  kind")
    for ph in res["program_headers"]:
        out.append(" %3d %#5x %#010x %#010x %#010x %10d %10d  %#010x  %s%s%s  %s"
                   % (ph["index"], ph["p_type"], ph["p_offset"], ph["p_vaddr"],
                      ph["p_paddr"], ph["p_filesz"], ph["p_memsz"], ph["p_flags"],
                      "r" if ph["read"] else "-",
                      "w" if ph["write"] else "-",
                      "x" if ph["execute"] else "-",
                      ph["kind"]))
    out.append("")
    out.append(" idx  entropy  ent_words  fill%   head16")
    for ph in res["program_headers"]:
        out.append(" %3d  %7.3f  %9.3f  %5s   %s"
                   % (ph["index"], ph["entropy"], ph["entropy_words"],
                      "-" if ph["fill_pct"] is None else "%.1f" % ph["fill_pct"],
                      ph["head16"]))
    out.append("")
    if res["gaps"]:
        out.append("file-space gaps between segments:")
        for g in res["gaps"]:
            out.append("   %#010x  %7d bytes  before segment %s"
                       % (g["at"], g["bytes"], g["before_segment"]))
    else:
        out.append("file-space gaps: none")
    zl = [p for p in res["program_headers"] if p.get("zlib")]
    for ph in zl:
        z = ph["zlib"]
        if z["ok"]:
            out.append("segment %d zlib: %d B -> %d B (x%.2f)"
                       % (ph["index"], ph["p_filesz"], z["inflated_bytes"], z["ratio"]))
        else:
            out.append("segment %d zlib: FAILED %s" % (ph["index"], z["error"]))
    if res["embedded_elf_offsets"]:
        out.append("embedded ELF magic at: %s"
                   % ", ".join("%#x" % o for o in res["embedded_elf_offsets"]))
    if res["violations"]:
        out.append("")
        out.append("VIOLATIONS")
        for v in res["violations"]:
            out.append("  - %s" % v)
    else:
        out.append("")
        out.append("invariants: OK")
    return "\n".join(out)


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?")
    ap.add_argument("--dir")
    ap.add_argument("--json")
    ap.add_argument("--brief", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    if not args.path and not args.dir:
        ap.error("need a path or --dir")
    targets = []
    if args.dir:
        for name in sorted(os.listdir(args.dir)):
            p = os.path.join(args.dir, name)
            if not os.path.isfile(p):
                continue
            try:
                with open(p, "rb") as h:
                    if h.read(4) != b"\x7fELF":
                        continue
            except OSError:
                continue
            targets.append(p)
    else:
        targets.append(args.path)
    results = []
    code = 0
    for path in targets:
        try:
            res = probe(path)
        except (ProbeError, OSError) as exc:
            if not args.quiet:
                print("%s: ERROR %s" % (os.path.basename(path), exc))
            code = max(code, 2)
            continue
        results.append(res)
        if res["violations"]:
            code = max(code, 1)
        if args.quiet:
            continue
        if args.brief or args.dir:
            print(brief_line(res))
        else:
            print(render(res))
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(results if args.dir else results[0], fh, indent=1)
            fh.write("\n")
        if not args.quiet:
            print("\nwrote %s" % args.json)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
