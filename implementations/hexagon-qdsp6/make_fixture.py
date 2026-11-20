#!/usr/bin/env python3
"""make_fixture.py -- deterministic SYNTHETIC Hexagon container fixtures.

CLEAN-ROOM STATEMENT
The images written here are **entirely self-made**. They reproduce only the
header grammar documented in ``hexagon-qdsp6/analysis.md`` and derived from
public sources (ELF gABI, ``drivers/soc/qcom/mdt_loader.c`` GPL-2.0-only,
``llvm/lib/Target/Hexagon`` Apache-2.0-WITH-LLVM-exception). No byte in any
fixture comes from a vendor artifact. All code bytes are generated from a
fixed arithmetic pattern, all metadata bytes from a deterministic PRNG, so
the fixtures are reproducible and provably synthetic.

Fixtures written to ``fixtures/``:

  monolithic_v67.hexbin   one ELF, every PT_LOAD inline, e_flags 0x67
  split_v66.mdt           header-only ELF, segments expected in .bNN
  split_v66.b00           the matching segment-0 blob for the above
  selfcontained_v67.mbn   header-table segment 0 but segments inline
  dyn_v67.mbn             ET_DYN, single big load, embedded inner ELF
  no_sections.mbn         valid image with e_shnum=0 (every real one)
  bad_phoff.mbn           e_phoff is not e_ehsize  (invariant violation)
  bad_memsz.mbn           a segment with p_memsz < p_filesz (violation)
  truncated.mbn           program header table runs past EOF (parse error)

All extensions are gitignored; regenerate with
``python3 -I make_fixture.py``.
"""

import os
import struct

EM_QDSP6 = 164
HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")

EHDR = struct.Struct("<16sHHIIIIIHHHHHH")
PHDR = struct.Struct("<8I")


def pattern(size, seed):
    out = bytearray(size)
    x = seed & 0xFFFFFFFF
    for i in range(size):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        out[i] = (x >> 16) & 0xFF
    return bytes(out)


def code_pattern(size, seed):
    out = bytearray(size)
    for i in range(size):
        out[i] = (i * 7 + seed) & 0xFF
    return bytes(out)


def build(e_type, e_flags, segments, e_entry=0, phoff=None, phnum=None,
          shnum=0, header_seg=False, force_memsz=None):
    """segments: list of dicts with keys filesz, memsz, flags, body, align.

    When ``header_seg`` is true a leading PT_NULL placeholder is inserted as
    program header 0, and the caller-supplied segments start at index 1 --
    which is the layout every split-MDT and self-contained image uses.
    """
    entries = list(segments)
    if header_seg:
        entries = [None] + entries
    if phnum is None:
        phnum = len(entries)
    ehsize = 52
    phentsize = 32
    natural_phoff = ehsize
    phoff = natural_phoff if phoff is None else phoff
    table_end = ehsize + len(entries) * phentsize
    cursor = max(table_end, 4096)
    placed = []
    for seg in entries:
        if seg is None:
            placed.append((0, None))
            continue
        align = seg.get("align", 4096)
        cursor = (cursor + align - 1) // align * align
        placed.append((cursor, seg))
        cursor += seg["filesz"]
    total = cursor
    buf = bytearray(total)
    ident = b"\x7fELF\x01\x01\x01" + b"\x00" * 9
    EHDR.pack_into(buf, 0, ident, e_type, EM_QDSP6, 1, e_entry, phoff, 0,
                   e_flags, ehsize, phentsize, len(entries), 40, shnum, 0)
    for i, (offset, seg) in enumerate(placed):
        if seg is None:
            PHDR.pack_into(buf, phoff + i * phentsize, 0, 0, 0, 0, table_end,
                           0, 0x07000000, 0)
            continue
        memsz = seg["memsz"]
        if force_memsz is not None and i == force_memsz[0]:
            memsz = force_memsz[1]
        PHDR.pack_into(buf, phoff + i * phentsize, seg.get("p_type", 1), offset,
                       seg.get("vaddr", 0),
                       seg.get("paddr", 0), seg["filesz"], memsz,
                       seg.get("flags", 0x08000007), seg.get("align", 4096))
        buf[offset:offset + seg["filesz"]] = seg["body"]
    return bytes(buf)


def metadata_body(size=4096, seed=12345):
    body = bytearray(pattern(size, seed))
    struct.pack_into("<I", body, 0, 12)
    struct.pack_into("<I", body, 4, 6)
    struct.pack_into("<I", body, 0x10, 0x1DD8)
    struct.pack_into("<I", body, 0x14, 0x570)
    return bytes(body)


def write(name, data):
    os.makedirs(FIXTURES, exist_ok=True)
    path = os.path.join(FIXTURES, name)
    with open(path, "wb") as fh:
        fh.write(data)
    print("%-24s %8d B" % (name, len(data)))


def main():
    seg_code = {"filesz": 8192, "memsz": 8192, "flags": 0x08000005,
                "body": code_pattern(8192, 3), "vaddr": 0xC1600000,
                "paddr": 0x81600000}
    seg_data = {"filesz": 4096, "memsz": 8192, "flags": 0x08000006,
                "body": pattern(4096, 99), "vaddr": 0xC1610000,
                "paddr": 0x81610000}
    seg_bss = {"filesz": 0, "memsz": 16384, "flags": 0x08000006,
               "body": b"", "vaddr": 0xC1620000, "paddr": 0x81620000}

    write("monolithic_v67.hexbin",
          build(2, 0x67, [seg_code, seg_data, seg_bss], e_entry=0xC1600000))

    seg_meta = {"filesz": 4096, "memsz": 8192, "flags": 0x02200000,
                "body": metadata_body(4096, 7), "vaddr": 0x8F700000,
                "paddr": 0x8F700000, "p_type": 0}
    write("signed_v67.mbn",
          build(2, 0x67, [seg_meta, seg_code, seg_data, seg_bss],
                e_entry=0xC1600000))

    split_meta = {"filesz": 4096, "memsz": 8192, "flags": 0x02200000,
                  "body": metadata_body(4096, 7), "vaddr": 0x8F700000,
                  "paddr": 0x8F700000}
    seg_bss_split = {"filesz": 0, "memsz": 8192, "flags": 0x08000004,
                     "body": b"", "vaddr": 0xC1620000, "paddr": 0x81620000}
    full = build(2, 0x66, [seg_code, seg_data, seg_bss_split],
                 e_entry=0xC1600000, header_seg=True)
    fields = list(EHDR.unpack_from(full, 0))
    table_end = fields[8] + 4 * fields[9]
    table = full[:table_end]
    write("split_v66.mdt", table)
    write("split_v66.b00", table)
    write("split_v66.b01", seg_code["body"])
    write("split_v66.b02", seg_data["body"])
    del split_meta

    write("selfcontained_v67.mbn",
          build(2, 0x67, [seg_code, seg_data], header_seg=True,
                e_entry=0xC1600000))

    inner = build(3, 0x67, [{"filesz": 2048, "memsz": 2048,
                             "flags": 0x00000005,
                             "body": code_pattern(2048, 11)}])
    write("dyn_v67.mbn",
          build(3, 0x67, [{"filesz": len(inner), "memsz": len(inner),
                           "flags": 0x00000005, "body": inner}]))
    del inner

    write("no_sections.mbn",
          build(2, 0x67, [seg_code, seg_data], shnum=0, e_entry=0xC1600000,
                header_seg=True))

    write("bad_phoff.mbn",
          build(2, 0x67, [seg_code, seg_data], phoff=64))

    write("bad_memsz.mbn",
          build(2, 0x67, [seg_code, seg_data], force_memsz=(0, 4096)))

    good = build(2, 0x67, [seg_code, seg_data])
    write("truncated.mbn", good[:80])


if __name__ == "__main__":
    main()
