#!/usr/bin/env python3
"""make_compact.py — trim the full census JSON to a publishable compact form.

Keeps derived facts only (paths, sizes, hash prefixes, ELF metadata, container
structure, version strings). Output must stay under git size limits.
Usage: python3 -I make_compact.py <full.json> <compact.json>
"""
import json
import sys


def trim_elf(elf):
    if not elf or not elf.get("is_elf"):
        return None
    out = {
        "class": elf.get("class"), "endian": elf.get("endian"),
        "type": elf.get("type"), "machine": elf.get("machine"),
        "machine_id": elf.get("machine_id"), "entry": elf.get("entry"),
        "phnum": elf.get("phnum"), "entry_in_load": elf.get("entry_in_load"),
    }
    if elf.get("thumb_entry") is not None:
        out["thumb_entry"] = elf["thumb_entry"]
    if elf.get("vaddr_span"):
        out["vaddr_span"] = elf["vaddr_span"]
    phdrs = []
    for p in elf.get("phdrs", []):
        phdrs.append({k: p[k] for k in ("type", "flags", "offset", "vaddr", "filesz")
                      if k in p})
    out["phdrs"] = phdrs
    return out


def trim_lk(lk):
    if not lk:
        return None
    out = {k: lk[k] for k in ("lk_magic", "lk_file_info_offset", "layout",
                              "lk_name", "gfh_file_info", "subimage_align")
           if k in lk}
    subs = []
    for s in lk.get("subimages", []):
        subs.append({k: s[k] for k in ("name", "size", "offset",
                                       "payload_is_elf", "payload_first8")
                     if k in s})
    if subs:
        out["subimages"] = subs
    return out


def main():
    src, dst = sys.argv[1], sys.argv[2]
    d = json.load(open(src))
    files = []
    for r in d.get("files", []):
        row = {"path": r["path"], "size": r["size"], "sha256_16": r["sha256_16"],
               "magic": r.get("magic")}
        elf = trim_elf(r.get("elf"))
        if elf:
            row["elf"] = elf
        lk = trim_lk(r.get("lk"))
        if lk:
            row["lk"] = lk
        if r.get("md1_table"):
            row["md1_table"] = r["md1_table"]
        if r.get("strings"):
            row["strings"] = r["strings"]
        if r.get("error"):
            row["error"] = r["error"]
        files.append(row)
    out = {"root": d.get("root"), "machines": d.get("machines", {}),
           "files": files}
    json.dump(out, open(dst, "w"), indent=1)
    print(f"compact: {len(files)} files -> {dst}")


if __name__ == "__main__":
    main()
