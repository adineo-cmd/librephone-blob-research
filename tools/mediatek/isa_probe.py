#!/usr/bin/env python3
"""isa_probe.py — byte-level ISA plausibility probe for raw MTK payload code.

For a given file and offset, disassembles 256 instructions with capstone in
each candidate ISA and reports the fraction that decoded. Raw MTK payloads
carry no ELF header, so the header-derived e_machine evidence used on
Qualcomm does not exist here; this probe is the substitute sanity check.

Usage: python3 -I isa_probe.py <file> <offset> [offset...]
"""
import sys
from capstone import (Cs, CS_ARCH_ARM, CS_ARCH_ARM64, CS_ARCH_MIPS,
                      CS_ARCH_RISCV, CS_MODE_ARM, CS_MODE_THUMB,
                      CS_MODE_MIPS32, CS_MODE_MIPS64, CS_MODE_RISCV32,
                      CS_MODE_RISCV64, CS_MODE_LITTLE_ENDIAN)

MODES = {
    "arm32": (CS_ARCH_ARM, CS_MODE_ARM | CS_MODE_LITTLE_ENDIAN),
    "thumb2": (CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN),
    "arm64": (CS_ARCH_ARM64, CS_MODE_LITTLE_ENDIAN),
    "mips32le": (CS_ARCH_MIPS, CS_MODE_MIPS32 | CS_MODE_LITTLE_ENDIAN),
    "mips64le": (CS_ARCH_MIPS, CS_MODE_MIPS64 | CS_MODE_LITTLE_ENDIAN),
    "riscv32": (CS_ARCH_RISCV, CS_MODE_RISCV32 | CS_MODE_LITTLE_ENDIAN),
    "riscv64": (CS_ARCH_RISCV, CS_MODE_RISCV64 | CS_MODE_LITTLE_ENDIAN),
}

N = 256


def probe(path, off, vaddr=None):
    blob = open(path, "rb").read()
    code = blob[off:off + 4096]
    print(f"\n{path} @ file offset {off:#x} (vaddr {hex(vaddr) if vaddr else '?'})")
    for name, (arch, mode) in MODES.items():
        md = Cs(arch, mode)
        got, ops = 0, 0
        sample = []
        for i in md.disasm(code, (vaddr or 0) + off):
            ops += 1
            got += 1
            if got <= 3:
                sample.append(f"{i.mnemonic} {i.op_str}")
            if got >= N:
                break
        # crude plausibility: count of data-processing/jump-ish mnemonics
        print(f"  {name:<9} decoded {got}/{N}  {sample}")


if __name__ == "__main__":
    path = sys.argv[1]
    for a in sys.argv[2:]:
        off, _, v = a.partition(":")
        probe(path, int(off, 0), int(v, 0) if v else None)
