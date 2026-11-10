#!/usr/bin/env python3
"""entry_sanity.py — disassembly cross-check of claimed ELF e_machine.

For a given blob (or LK-container payload), locate the entry point inside a
PT_LOAD and disassemble the first N instructions with capstone in the
architecture the header claims. A claimed ARM entry that decodes as garbage
while Thumb decodes plausibly (or vice versa) is flagged.

Derived facts only: prints instruction mnemonics (not raw bytes beyond 8 bytes
of hex, acceptable as it is machine-instruction data, not content blobs).
Usage: python3 -I entry_sanity.py <file> [--entry 0x..] [--machine arm|thumb|arm64|riscv|mips|mips64|xtensa] [--skip 0x200]
"""
import argparse
import struct
import sys

try:
    from capstone import (Cs, CS_ARCH_ARM, CS_ARCH_ARM64, CS_ARCH_RISCV,
                          CS_ARCH_MIPS, CS_MODE_ARM, CS_MODE_THUMB,
                          CS_MODE_MIPS32, CS_MODE_MIPS64, CS_MODE_RISCV32,
                          CS_MODE_RISCV64, CS_MODE_LITTLE_ENDIAN)
except ImportError:
    sys.exit("capstone required (pip install --user --break-system-packages capstone)")

ARCHS = {
    "arm": (CS_ARCH_ARM, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN, 4),
    "thumb": (CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN, 4),
    "arm64": (CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN, 4),
    "riscv": (CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_LITTLE_ENDIAN, 4),
    "riscv64": (CS_ARCH_RISCV, CS_MODE_RISCV64 | CS_MODE_LITTLE_ENDIAN, 4),
    "mips": (CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN, 4),
    "mips64": (CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_LITTLE_ENDIAN, 4),
}


def load_blob(path):
    with open(path, "rb") as f:
        return f.read()


def parse_loads(blob, skip=0):
    """Return (entry, [(vaddr, filesz, offset)]) of the ELF (after `skip`)."""
    b = blob[skip:skip + 64]
    if not b.startswith(b"\x7fELF"):
        return None, []
    ei_class, ei_data = b[4], b[5]
    fmt = "<" if ei_data == 1 else ">"
    if ei_class == 1:
        (e_type, e_machine) = struct.unpack_from(fmt + "HH", b, 16)
        (e_entry, e_phoff) = struct.unpack_from(fmt + "II", b, 24)
        e_phentsize, e_phnum = struct.unpack_from(fmt + "HH", b, 42)
        ph_fmt, ph_size = fmt + "IIIIIIII", 32
    else:
        (e_type, e_machine) = struct.unpack_from(fmt + "HH", b, 16)
        (e_entry, e_phoff) = struct.unpack_from(fmt + "QQ", b, 24)
        e_phentsize, e_phnum = struct.unpack_from(fmt + "HH", b, 54)
        ph_fmt, ph_size = fmt + "IIQQQQQQ", 56
    loads = []
    off = e_phoff
    blob2 = blob[skip:]
    for _ in range(e_phnum):
        raw = blob2[off:off + ph_size]
        off += ph_size
        if len(raw) < ph_size:
            break
        if ei_class == 1:
            p_type, p_off, p_vaddr, _pa, p_filesz, _m, p_flags, _a = struct.unpack(ph_fmt, raw)
        else:
            p_type, p_flags, p_off, p_vaddr, _pa, p_filesz, _m, _a = struct.unpack(ph_fmt, raw)
        if p_type == 1:
            loads.append((p_vaddr, p_filesz, p_off))
    return e_entry, loads


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--entry", type=lambda x: int(x, 0), default=None)
    ap.add_argument("--machine", default=None, choices=list(ARCHS))
    ap.add_argument("--skip", type=lambda x: int(x, 0), default=0,
                    help="bytes to skip (0x200 for LK container payload)")
    ap.add_argument("-n", type=int, default=12)
    args = ap.parse_args()

    blob = load_blob(args.file)
    entry, loads = parse_loads(blob, args.skip)
    if args.entry is not None:
        entry = args.entry
    if entry is None:
        sys.exit("no ELF entry found")
    # map entry vaddr to file offset
    foff = None
    for vaddr, filesz, off in loads:
        if vaddr <= entry < vaddr + filesz:
            foff = off + (entry - vaddr)
            break
    if foff is None:
        print(f"entry {entry:#x} NOT inside any PT_LOAD — sanity FAIL")
        foff = 0
    base = args.skip + foff
    code = blob[base:base + 128]
    print(f"file={args.file} entry={entry:#x} file_offset={base:#x} loads={len(loads)}")
    for name in ([args.machine] if args.machine else list(ARCHS)):
        if name not in ARCHS:
            continue
        arch, mode, _align = ARCHS[name]
        md = Cs(arch, mode)
        out = []
        for i in md.disasm(code, entry & ~1 if name != "thumb" else entry):
            out.append(f"{i.mnemonic} {i.op_str}")
            if len(out) >= args.n:
                break
        valid = len(out)
        print(f"[{name}] {valid}/{args.n} instructions decoded:")
        for line in out[:6]:
            print(f"    {line}")
        if valid < args.n // 2:
            print("    -> LOW decode rate (implausible for this ISA)")


if __name__ == "__main__":
    main()
