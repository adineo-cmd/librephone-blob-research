#!/usr/bin/env python3
"""make_fixture.py -- deterministic SYNTHETIC fixtures for cdsp_probe.py.

WHY SYNTHETIC
-------------
The real ``image_cdsp.mdt`` and its ``.bNN`` siblings are proprietary vendor
firmware. The repository ``.gitignore`` excludes ``*.mdt``, ``*.b[0-9][0-9]``,
``*.elf`` and ``*.bin``, and the lab rule is that no real payload byte is ever
committed. So, following the pattern in ``implementations/adsp-fleet/`` and
``implementations/qca-bt-gen2/``, every fixture here is **self-made**: the
bytes come from a SHA-256 counter stream keyed by a per-fixture tag, and only
the container *layout* is reproduced.

That is the whole point. A fixture proves the probe against the format the
public loader sources describe, never against any vendor's content.

DETERMINISM
-----------
Every byte is deterministic. Re-running this script reproduces every fixture
byte-for-byte, which ``test_cdsp_probe.py`` verifies. Fixtures live in a
sub-directory per image, because a split-MDT image is a *set* of files that
must sit next to each other:

    fixtures/cdsp_synthetic.mdt  +  fixtures/cdsp_synthetic.b00 .. b12
    fixtures/bss_synthetic.mdt   +  fixtures/bss_synthetic.b00 .. b06
    fixtures/mismatch_synthetic.mdt + siblings with one wrong size
    fixtures/badmagic_synthetic.mdt
    fixtures/truncated_synthetic.mdt
    fixtures/badhash_synthetic.mdt

WHAT GETS BUILT
---------------
``cdsp_synthetic``
    A faithful shape copy of the measured image: 13 program headers, the
    first ``PT_NULL`` covering the ELF header plus the program-header table,
    the second the hash segment, ten loadable rows of which three are BSS
    (``p_filesz == 0``, ``p_memsz > 0``, no sibling), and a ``p_flags`` set
    drawn from the values the decode is specified against
    (``0x07000000``, ``0x02200000``, ``0x08000005``, ``0x08000004``, ...).
    Sizes are small: this proves the rule, it does not need 4 MiB to do it.

``bss_synthetic``
    A minimal image whose only interesting property is that several rows
    have ``p_filesz == 0`` and therefore no sibling at all.

``mismatch_synthetic``
    Byte-identical to ``cdsp_synthetic`` except that one sibling is written
    two bytes short. The validator must name that sibling and fail.

``badmagic_synthetic``
    An ELF-shaped file whose magic is wrong. Rejection path.

``truncated_synthetic``
    A valid image with the tail of the ``.mdt`` cut off, so the
    header-block-plus-hash size rule no longer holds.

``badhash_synthetic``
    A valid image with the hash row's segment type flipped from 2 to 0, so
    no ``QCOM_MDT_TYPE_HASH`` row exists. Rejection path.

CLEAN-ROOM
----------
Only the container layout is reproduced, and that layout comes from public
GPL-2.0-only sources: ``include/uapi/linux/elf.h`` (the ``Elf32_Ehdr`` and
``Elf32_Phdr`` field order), ``include/uapi/linux/elf-em.h`` (``EM_HEXAGON``
= 164), ``include/linux/soc/qcom/mdt_loader.h`` (the ``QCOM_MDT_*`` masks)
and coreboot ``util/qualcomm/mbn_tools.py`` (the packed ``p_flags`` bit
layout). No proprietary content, no decompilation, no vendor header.
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures")

EM_HEXAGON = 164
EF_HEXAGON_V66 = 0x066

PT_NULL = 0
PT_LOAD = 1

PF_R = 0x4
PF_W = 0x2
PF_X = 0x1

FLAG_PHDR = 0x07000000
FLAG_HASH = 0x02200000
FLAG_RX = 0x08000005
FLAG_RW = 0x08000006
FLAG_R = 0x08000004
FLAG_RWX = 0x08000007

PAGE = 0x1000


def pattern(n, tag):
    """Deterministic pseudo-random byte stream: SHA-256 of a tagged counter."""
    tag = tag.encode() if isinstance(tag, str) else tag
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(b"%s:%d" % (tag, counter)).digest()
        counter += 1
    return bytes(out[:n])


def align(n, page):
    return (n + page - 1) // page * page


def ehdr(e_phoff, e_phnum, e_entry, e_flags=EF_HEXAGON_V66, e_type=2,
         magic=b"\x7fELF"):
    ident = bytearray(16)
    ident[0:4] = magic
    ident[4] = 1
    ident[5] = 1
    ident[6] = 1
    return struct.pack(
        "<16sHHIIIIIHHHHHH",
        bytes(ident),
        e_type,
        EM_HEXAGON,
        1,
        e_entry,
        e_phoff,
        0,
        e_flags,
        52,
        32,
        e_phnum,
        40,
        0,
        0,
    )


def phdr(p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags,
         p_align):
    return struct.pack("<IIIIIIII", p_type, p_offset, p_vaddr, p_paddr,
                       p_filesz, p_memsz, p_flags, p_align)


def build_image(tag, rows, tail_trim=0, drop_hash=False, magic=b"\x7fELF",
                entry_row=2):
    """Assemble one split-MDT image from a row specification.

    ``rows`` is a list of dicts with keys ``type``, ``vaddr``, ``paddr``,
    ``filesz``, ``memsz``, ``flags``, ``align``. ``p_offset`` is assigned
    here so the file layout is always consistent: the header block occupies
    the first page, the hash segment starts at the next page boundary, and
    every later payload-bearing row gets its own page-aligned offset. Rows
    with ``filesz == 0`` inherit the next row's offset, exactly as the
    measured image does, because they occupy no file space.
    """
    phnum = len(rows)
    header_block = 52 + 32 * phnum
    offsets = []
    cursor = PAGE
    for i, row in enumerate(rows):
        if i == 0:
            offsets.append(0)
            continue
        if row["filesz"] == 0:
            offsets.append(cursor)
        else:
            cursor = align(cursor, row.get("align") or PAGE)
            offsets.append(cursor)
            cursor += row["filesz"]
    for i in range(len(rows) - 1, -1, -1):
        if rows[i]["filesz"] == 0:
            nxt = offsets[i + 1] if i + 1 < len(rows) else cursor
            offsets[i] = nxt

    entry = rows[entry_row]["paddr"] if entry_row < phnum else 0

    table = bytearray()
    for i, row in enumerate(rows):
        flags = row["flags"]
        if drop_hash and i == 1:
            flags = flags & ~(7 << 24)
        table += phdr(row["type"], offsets[i], row["vaddr"], row["paddr"],
                      row["filesz"], row["memsz"], flags,
                      row.get("align", PAGE))
    head = ehdr(52, phnum, entry, magic=magic) + bytes(table)
    if len(head) > PAGE:
        raise ValueError("program-header table does not fit one page")

    body = bytearray(head)
    body += b"\x00" * (PAGE - len(head))
    for i, row in enumerate(rows):
        if row["filesz"] == 0:
            continue
        if offsets[i] > len(body):
            body += b"\x00" * (offsets[i] - len(body))
        body += pattern(row["filesz"], "%s:seg%d" % (tag, i))
    if tail_trim:
        body = body[:len(body) - tail_trim]
    return bytes(body)


def split_rows(count=13):
    """The row specification for the main synthetic image.

    Thirteen rows, matching the measured shape: header block, hash segment,
    ten payload rows, three of them BSS. ``p_memsz`` is always at least
    ``p_filesz`` because the loader refuses anything else.
    """
    specs = [
        (PT_NULL, 0x00000000, 0x00000000, None, 0, FLAG_PHDR, PAGE),
        (PT_NULL, 0x88C00000, 0x88C00000, 0x1C18, 0x2000, FLAG_HASH, PAGE),
        (PT_LOAD, 0xFE000000, 0x87800000, 0x3A00, 0xB000, FLAG_RX, PAGE),
        (PT_LOAD, 0xFE0B0000, 0x878B0000, 0x1A00, 0x2000, FLAG_RX, PAGE),
        (PT_LOAD, 0xC00CA000, 0x878CA000, 0x0400, 0x1000, FLAG_RX, PAGE),
        (PT_LOAD, 0xC00CB000, 0x878CB000, 0x4800, 0x8000, FLAG_RWX, PAGE),
        (PT_LOAD, 0xC05C5000, 0x87DC5000, 0x1400, 0x2000, FLAG_RW, PAGE),
        (PT_LOAD, 0xC05DA000, 0x87DDA000, 0, 0x26000, FLAG_R, PAGE),
        (PT_LOAD, 0x01000000, 0x87E00000, 0x1800, 0x4000, FLAG_RWX, PAGE),
        (PT_LOAD, 0x01B11000, 0x88911000, 0x0A00, 0x1000, FLAG_RW, PAGE),
        (PT_LOAD, 0xC0600000, 0x88912000, 0, 0xEE000, FLAG_R, PAGE),
        (PT_LOAD, 0x74000000, 0x88A00000, 0x0C00, 0x4000, FLAG_RWX, PAGE),
        (PT_LOAD, 0xC06EE000, 0x88A43000, 0, 0x1BD000, FLAG_R, PAGE),
    ]
    rows = []
    for i, (p_type, vaddr, paddr, filesz, memsz, flags, page) in enumerate(specs):
        if filesz is None:
            filesz = 52 + 32 * count
        if memsz < filesz:
            memsz = filesz
        rows.append({
            "type": p_type,
            "vaddr": vaddr,
            "paddr": paddr,
            "filesz": filesz,
            "memsz": memsz,
            "flags": flags,
            "align": page,
        })
    return rows


def bss_rows():
    """A minimal image dominated by zero-fill rows."""
    count = 7
    block = 52 + 32 * count
    specs = [
        (PT_NULL, 0x00000000, 0x00000000, block, 0, FLAG_PHDR),
        (PT_NULL, 0x88000000, 0x88000000, 0x0800, 0x1000, FLAG_HASH),
        (PT_LOAD, 0xFE000000, 0x87800000, 0x1000, 0x2000, FLAG_RX),
        (PT_LOAD, 0xFE001000, 0x87801000, 0, 0x4000, FLAG_R),
        (PT_LOAD, 0xFE005000, 0x87805000, 0, 0x8000, FLAG_R),
        (PT_LOAD, 0xFE00D000, 0x8780D000, 0x0800, 0x1000, FLAG_RW),
        (PT_LOAD, 0xFE00E000, 0x8780E000, 0, 0x10000, FLAG_R),
    ]
    rows = []
    for p_type, vaddr, paddr, filesz, memsz, flags in specs:
        if memsz < filesz:
            memsz = filesz
        rows.append({
            "type": p_type,
            "vaddr": vaddr,
            "paddr": paddr,
            "filesz": filesz,
            "memsz": memsz,
            "flags": flags,
            "align": PAGE,
        })
    return rows


def write_split(out_dir, stem, image, rows, overrides=None):
    """Write one ``.mdt`` plus its siblings. Returns [(name, bytes)]."""
    overrides = overrides or {}
    written = [("%s.mdt" % stem, image)]
    header_block = 52 + 32 * len(rows)
    cursor = PAGE
    offsets = []
    for i, row in enumerate(rows):
        if i == 0:
            offsets.append(0)
            continue
        if row["filesz"] == 0:
            offsets.append(cursor)
        else:
            cursor = align(cursor, row.get("align") or PAGE)
            offsets.append(cursor)
            cursor += row["filesz"]
    for i in range(len(rows) - 1, -1, -1):
        if rows[i]["filesz"] == 0:
            offsets[i] = offsets[i + 1] if i + 1 < len(rows) else cursor
    for i, row in enumerate(rows):
        if row["filesz"] == 0:
            continue
        name = "%s.b%02d" % (stem, i)
        data = image[offsets[i]:offsets[i] + row["filesz"]]
        if i in overrides:
            data = overrides[i](data)
        written.append((name, data))
    return written


def build_all(out_dir=None):
    """Build every fixture. Returns a list of (name, bytes)."""
    directory = out_dir or FIXTURE_DIR
    os.makedirs(directory, exist_ok=True)

    jobs = []

    rows = split_rows()
    image = build_image("fx-cdsp", rows)
    jobs.extend(write_split(directory, "cdsp_synthetic", image, rows))

    b_rows = bss_rows()
    b_image = build_image("fx-bss", b_rows)
    jobs.extend(write_split(directory, "bss_synthetic", b_image, b_rows))

    m_rows = split_rows()
    m_image = build_image("fx-cdsp", m_rows)
    jobs.extend(write_split(
        directory, "mismatch_synthetic", m_image, m_rows,
        overrides={5: lambda data: data[:-2]},
    ))

    bad_rows = split_rows()
    bad_image = build_image("fx-cdsp", bad_rows, magic=b"\x7fELG")
    jobs.extend(write_split(directory, "badmagic_synthetic", bad_image,
                            bad_rows))

    trunc_rows = split_rows()
    trunc_image = build_image("fx-cdsp", trunc_rows, tail_trim=0x40)
    jobs.extend(write_split(directory, "truncated_synthetic", trunc_image,
                            trunc_rows))

    hash_rows = split_rows()
    hash_image = build_image("fx-cdsp", hash_rows, drop_hash=True)
    jobs.extend(write_split(directory, "badhash_synthetic", hash_image,
                            hash_rows))

    return jobs


def main():
    jobs = build_all()
    total = 0
    for name, blob in jobs:
        path = os.path.join(FIXTURE_DIR, name)
        with open(path, "wb") as fh:
            fh.write(blob)
        total += len(blob)
        print("%-34s %9d bytes  md5=%s"
              % (name, len(blob), hashlib.md5(blob).hexdigest()))
    print("\n%d files, %d bytes total, in %s"
          % (len(jobs), total, FIXTURE_DIR))
    print("note: fixtures are *.mdt / *.bNN and therefore git-ignored; re-run "
          "this script to materialise them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
