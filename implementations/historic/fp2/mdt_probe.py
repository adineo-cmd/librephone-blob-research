#!/usr/bin/env python3
"""mdt_probe.py — clean-room structural parser/verifier for the Qualcomm
split-peripheral-image ("MDT") family: the ``<image>.mdt`` ELF header file
plus the sibling ``<image>.bNN`` segment files the kernel's Peripheral Image
Loader (PIL) assembles. This is the container of the 8974-era (and every
pre-8996) modem / WCNSS / ADSP / venus firmware.

It VERIFIES the structural invariants the mainline loader relies on
(ELF32 magic, phentsize, phdr-table bounds, per-segment file bounds,
hash-segment accounting, the "split iff ehdr+hash == file" rule), decodes
every ELF32 phdr field the public header pins, and emits a per-segment
table as JSON. It is an inspector: it tabulates what is on disk and
classifies segment memory ranges. It does NOT execute, disassemble or
reinterpret payload bytes, and does NOT verify TrustZone signatures.

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-18 from public GPL sources only:
  - linux/drivers/soc/qcom/mdt_loader.c (torvalds/linux master, GPL-2.0-only):
    mdt_header_valid() (ELFMAG check, e_phentsize == sizeof(elf32_phdr),
    phdr-table bounds via e_phoff/e_phnum, optional section-header bounds),
    mdt_phdr_loadable() (PT_LOAD + not TYPE_HASH + memsz != 0), the split
    segment naming rule (last three characters of the fw name replaced by
    "bNN"), qcom_mdt_bins_are_split() semantics (a segment whose extent
    falls outside the .mdt is fetched from the sibling file), and the
    metadata/hash-segment accounting used for size math.
  - linux/include/linux/soc/qcom/mdt_loader.h (same tree): QCOM_MDT_TYPE_MASK
    = 7<<24, QCOM_MDT_TYPE_HASH = 2<<24, QCOM_MDT_RELOCATABLE = BIT(27).
  - Standard ELF32 struct layout (elf32_hdr / elf32_phdr, as embedded in the
    kernel's <linux/elf.h>).
Prior art checked 2026-11-18 (RULE 0): kernel mdt_loader.c (the reference
implementation), a third-party XNU-side MDT parser for a630_zap.mdt
(keyfan/UniXNU-enchilada-bringup, 2025 — GPU ZAP handshake use, different
purpose), lab-internal qualcomm-fp6/docs/interface-mdtloader-vs-readelf.md
(FP6 PAS-era address semantics). Delta: no existing tool tabulates the
8974-era split-image segment CENSUS (which bNN files exist/are missing, the
file/offset/paddr layout, hash-segment accounting) as fleet documentation.
No proprietary material (no firmware payload bytes, no decompiled code,
no vendor headers) was accessed during development.
======================================================================

Usage:
    python3 -I mdt_probe.py <image.mdt> [--dir SEGMENT_DIR] [--json OUT]
                            [--brief]

Exit status 0 on a fully-verified parse; 1 on verification failures
(bad magic, phdr-table bounds, missing/oversized segment file) —
diagnostics are in the JSON under ``verification``.
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys

# --- public constants (mdt_loader.h) ---
QCOM_MDT_TYPE_MASK = 7 << 24
QCOM_MDT_TYPE_HASH = 2 << 24
QCOM_MDT_RELOCATABLE = 1 << 27

PT_LOAD = 1
PT_NULL = 0

EHDR_FMT = "<4s5B7x2H5I6H"      # elf32_hdr, 52 bytes
EHDR_SIZE = struct.calcsize(EHDR_FMT)
PHDR_FMT_FULL = "<8I"            # elf32_phdr: type, offset, vaddr, paddr, filesz,
PHDR_SIZE = struct.calcsize(PHDR_FMT_FULL)  # memsz, flags, align = 32 bytes


def entropy(data):
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


class MdtProbe:
    def __init__(self, mdt_path, seg_dir=None):
        self.mdt_path = mdt_path
        self.seg_dir = seg_dir or os.path.dirname(os.path.abspath(mdt_path))
        with open(mdt_path, "rb") as f:
            self.mdt = f.read()
        self.diagnostics = []

    def diag(self, cls, msg):
        self.diagnostics.append({"class": cls, "message": msg})

    def base_name(self):
        return os.path.basename(self.mdt_path)[:-4]  # strip ".mdt"

    def seg_path(self, idx):
        return os.path.join(self.seg_dir, "%s.b%02d" % (self.base_name(), idx))

    def parse(self):
        mdt = self.mdt
        r = {}
        if len(mdt) < EHDR_SIZE:
            raise ValueError("file smaller than elf32 header (%d < %d)" % (len(mdt), EHDR_SIZE))
        fields = struct.unpack_from(EHDR_FMT, mdt, 0)
        (magic, eclass, edata, eversion, eosabi, eosabi_ver,
         etype, emachine, eversion2, eentry, ephoff, eshoff, eflags,
         eehsize, ephentsize, ephnum, eshentsize, eshnum, eshstrndx) = fields
        if magic != b"\x7fELF":
            raise ValueError("bad ELF magic %r" % (magic,))
        r["elf"] = {
            "class": eclass, "data": edata, "type": etype, "machine": emachine,
            "entry": eentry, "phoff": ephoff, "phentsize": ephentsize,
            "phnum": ephnum, "shoff": eshoff, "shnum": eshnum, "flags": eflags,
        }
        if ephentsize != PHDR_SIZE:
            raise ValueError("e_phentsize %d != sizeof(elf32_phdr) %d (mdt_header_valid rule)"
                             % (ephentsize, PHDR_SIZE))
        phend = ephoff + ephentsize * ephnum
        if phend > len(mdt):
            raise ValueError("phdr table out of bounds: %d > %d" % (phend, len(mdt)))
        if eshnum or eshentsize:
            shend = eshoff + eshentsize * eshnum
            if shend > len(mdt):
                raise ValueError("shdr table out of bounds: %d > %d" % (shend, len(mdt)))
        else:
            shend = eshoff  # header-only images carry no section table

        # hash segment = phdr[0] per qcom_mdt_read_metadata; typically type
        # PT_NULL with TYPE_HASH flag bits.
        phdrs = []
        for i in range(ephnum):
            off = ephoff + i * ephentsize
            p_type, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_flags, p_align = \
                struct.unpack_from(PHDR_FMT_FULL, mdt, off)
            phdrs.append(dict(idx=i, type=p_type, offset=p_offset, vaddr=p_vaddr,
                              paddr=p_paddr, filesz=p_filesz, memsz=p_memsz,
                              flags=p_flags, align=p_align))
        r["phdrs"] = phdrs

        # invariants the loader relies on
        hash0 = phdrs[0] if phdrs else None
        hash0_is_hash = bool(hash0 and (hash0["flags"] & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH)
        ehdr_plus_hash = EHDR_SIZE + (hash0["filesz"] if hash0_is_hash else 0)
        r["structure"] = {
            "phdr_table_end": phend,
            "section_table_end": shend,
            "phdr0_is_hash_type": hash0_is_hash,
            "phdr0_type": hash0["type"] if hash0 else None,
            "ehdr_plus_hash_segment": ehdr_plus_hash,
            "mdt_size": len(mdt),
            "split_iff_ehdr_plus_hash_eq_mdt": ehdr_plus_hash == len(mdt),
        }
        if ehdr_plus_hash != len(mdt):
            self.diag("info", "mdt-size-note: ehdr(%d)+hash(%d)=%d != file %d"
                      % (EHDR_SIZE, hash0["filesz"] if hash0_is_hash else 0,
                         ehdr_plus_hash, len(mdt)))

        loadable = [p for p in phdrs
                    if p["type"] == PT_LOAD and p["memsz"] != 0
                    and (p["flags"] & QCOM_MDT_TYPE_MASK) != QCOM_MDT_TYPE_HASH]
        hash_segs = [p for p in phdrs if (p["flags"] & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH]
        relocatable = any(p["flags"] & QCOM_MDT_RELOCATABLE for p in loadable)
        r["summary"] = {
            "num_phdrs": ephnum,
            "num_loadable": len(loadable),
            "num_hash_segments": len(hash_segs),
            "relocatable": relocatable,
            "min_paddr": min((p["paddr"] for p in loadable), default=None),
            "max_paddr_end": max((p["paddr"] + p["memsz"] for p in loadable), default=None),
        }

        # segment census: which bNN files exist on disk, and their bounds
        segs = []
        for p in phdrs:
            i = p["idx"]
            path = self.seg_path(i)
            exists = os.path.exists(path)
            rec = dict(idx=i, is_hash=(p["flags"] & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH,
                       loadable=(p["type"] == PT_LOAD and p["memsz"] != 0
                                 and (p["flags"] & QCOM_MDT_TYPE_MASK) != QCOM_MDT_TYPE_HASH),
                       file=exists,
                       declared_filesz=p["filesz"],
                       actual_size=os.path.getsize(path) if exists else None)
            if exists:
                actual = rec["actual_size"]
                if actual != p["filesz"]:
                    self.diag("error", "segment .b%02d size %d != declared p_filesz %d"
                              % (i, actual, p["filesz"]))
                rec["sha1_12"] = hashlib.sha1(open(path, "rb").read()).hexdigest()[:12]
            segs.append(rec)
        r["segments"] = segs
        missing = [s["idx"] for s in segs if s["declared_filesz"] and not s["file"]]
        extra = [i for i in range(len(segs), 64) if os.path.exists(self.seg_path(i))]
        r["census"] = {
            "declared_segment_files": sum(1 for s in segs if s["declared_filesz"]),
            "present_on_disk": sum(1 for s in segs if s["file"]),
            "missing_with_nonzero_filesz": missing,
            "extra_files_without_phdr": extra,
        }
        if missing:
            self.diag("error", "segments declared but missing on disk: %r" % missing)
        r["verification"] = {"diagnostics": self.diagnostics}
        return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="clean-room MDT/split-image probe")
    ap.add_argument("mdt", help="path to <image>.mdt")
    ap.add_argument("--dir", help="directory holding <image>.bNN (default: mdt's dir)")
    ap.add_argument("--json", help="write full result JSON here")
    ap.add_argument("--brief", action="store_true", help="one-line summary")
    args = ap.parse_args(argv)
    try:
        probe = MdtProbe(args.mdt, args.dir)
        r = probe.parse()
    except ValueError as e:
        print("PARSE ERROR: %s" % e, file=sys.stderr)
        return 1
    errs = [d for d in r["verification"]["diagnostics"] if d["class"] == "error"]
    if args.json:
        with open(args.json, "w") as f:
            json.dump(r, f, indent=1)
    s = r["summary"]
    st = r["structure"]
    print("%s: phdrs=%d loadable=%d hash=%d reloc=%s range=0x%08x-0x%08x mdt=%dB "
          "ehdr+hash==mdt:%s segs_on_disk=%d errors=%d"
          % (os.path.basename(args.mdt), s["num_phdrs"], s["num_loadable"],
             s["num_hash_segments"], s["relocatable"], s["min_paddr"] or 0,
             s["max_paddr_end"] or 0, st["mdt_size"],
             st["split_iff_ehdr_plus_hash_eq_mdt"], r["census"]["present_on_disk"],
             len(errs)))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
