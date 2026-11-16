#!/usr/bin/env python3
"""md1rom_taskmap.py — data-driven model of the MT6785 (Helio G95)
md1rom modem image's documented task interface and dispatch structure.

======================================================================
CLEAN-ROOM STATEMENT
Written from the lab's published spec documents on 2026-11-16:
  - librephone-blob-research/mediatek/docs/md1rom-decode.md (F-31): the
    byte-verified entry chain, decode-density region map, version strings
    and auto-analysis facts for md1rom (MOLY LR13, MIPS32 LE + MIPS16e).
  - librephone-blob-research/mediatek/rosemary-census.md: the md1img
    payload manifest, per-payload container/signedness facts, and the
    MOLY version-string table.
  - librephone-blob-research/mediatek/docs/md1dsp-decode.md (F-36) and
    docs/md32-gap.md (F-45): the modem L1/PHY task-name strings (LTE /
    HSPA / CDMA2000 families) recovered at decode level from the same
    MOLY LR13 package.
No proprietary material (no firmware payload bytes, no decompiled code)
was accessed during development. Every fact below traces to one of the
named documents; everything the specs do NOT pin is emitted as an
explicit stub (see STUBS) — never guessed.
======================================================================

What this module is NOT: it is not a disassembler and not a decoder of
md1rom's code. It is the data-driven dispatch/task-interface model the
workorder asks for: the documented facts as data, plus the honest stubs.

CLI: python3 -I md1rom_taskmap.py [--json OUT.json] [--verify-entry FILE]
"""

import argparse
import json
import os
import struct
import sys

# ---------------------------------------------------------------------
# Documented facts (each entry cites its spec document)
# ---------------------------------------------------------------------

IMAGE = {
    "name": "md1rom",
    "partition": "md1img",
    "size_bytes": 26682512,           # F-31 (census F-16 extraction)
    "container": "mtk_hdr record chain (0x58881688), no ELF header",  # census
    "isa_entry": "MIPS32 little-endian",      # F-31
    "isa_islands": "MIPS16e (MIPS:LE:32:16e)",  # F-31
    "isa_ruled_out": ["microMIPS", "nanoMIPS"],  # F-31 decode-density
    "modem_os_version": "MOLY.LR13.R1.MP.V89.6.P79",  # F-31 strings
    "flavor_path": "mtk_rel/XIAOMI_S0MP1_K6785V1_64/LWCTG_CUSTOM/L4/csm/ss/…",  # F-31
    "auto_analysis": {"language": "MIPS:LE:32:default",
                      "instruction_count": 1322630,
                      "function_count": 16297},   # F-31
    "source": "mediatek/docs/md1rom-decode.md (F-31)",
}

ENTRY_CHAIN = {
    # F-31 "entry point at 0x0" — the reset trampoline, byte-verified:
    "base": 0x0,
    "instructions": [
        {"offset": 0x00, "word": 0x3C060174, "mnemonic": "lui   a2,0x174"},
        {"offset": 0x04, "word": 0x24C62ED0, "mnemonic": "addiu a2,a2,0x2ed0"},
        {"offset": 0x08, "word": 0x00C00008, "mnemonic": "jr    a2  -> 0x176ed0"},
        # 4th instruction (_mtc0 zero,Count) is documented by mnemonic only —
        # the spec does not pin its encoding word, so we do not model one.
        {"offset": 0x0C, "word": None, "mnemonic": "_mtc0 zero,Count (delay slot)"},
    ],
    "jr_target": 0x176ED0,
    "filler_after": {"pattern": "00 65", "from": 0x10, "to": 0x30},
    "source": "mediatek/docs/md1rom-decode.md (F-31) claim 1",
}

# F-31 region map (coverage-derived; the doc's own honest negative is that
# island boundaries are coarse and segment semantics are unmapped).
REGION_MAP = [
    {"region": "0x0",           "kind": "mips32-entry", "coverage_pct": 6.25,
     "note": "reset trampoline + 00 65 filler"},
    {"region": "0x174000-0x176ed0+", "kind": "mips16e-partial", "coverage_pct": "25.0-51.0",
     "note": "code the entry jr targets; island boundaries not mapped"},
    {"region": "0x80000",  "kind": "code-island", "coverage_pct": 100.8},
    {"region": "0x100000", "kind": "code-island", "coverage_pct": 55.5},
    {"region": "0x200000", "kind": "code-island", "coverage_pct": 88.3},
    {"region": "0x300000", "kind": "code-island", "coverage_pct": 50.8},
    {"region": "0x700000", "kind": "code-island", "coverage_pct": 93.0},
    {"region": "0xe00000", "kind": "code-island", "coverage_pct": 84.4},
    {"region": "0x1000000-0x1400000", "kind": "code-island", "coverage_pct": "32.8-100.8"},
    {"region": "0x1960000", "kind": "code-island", "coverage_pct": 100.0},
    {"region": "0x400000-0x500000,0x800000,0x900000,0xb00000,0xc00000,"
               "0xd00000,0xf00000,0x1500000,0x1600000-0x1900000",
     "kind": "data/compressed", "coverage_pct": 0,
     "note": "zero/near-zero under every tested ISA (data, compressed payloads, DB/EM tables)"},
    {"region": "0x176ed0", "kind": "jr-target", "coverage_pct": 25.0},
    {"region": "0x174100", "kind": "mips16e-partial", "coverage_pct": 50.0},
]

# The modem L1/PHY task names the spec corpus documents (all recovered at
# string level from the same MOLY LR13 package — F-36 build-tree evidence).
# Radio-access grouping follows the F-36/F-45 string families.
TASK_INVENTORY = [
    {"task": "4g_dci_parse_task",       "rat": "LTE",  "role": "L1/PHY DCI parse",
     "evidence": "F-36 string level", "source_file": "4g_dci_parse_task.c"},
    {"task": "4g_pcfich_parse_task",    "rat": "LTE",  "role": "L1/PHY PCFICH parse",
     "evidence": "F-36 string level", "source_file": "4g_pcfich_parse_task.c"},
    {"task": "4g_pdsch_crc_task",       "rat": "LTE",  "role": "L1/PHY PDSCH CRC",
     "evidence": "F-36 string level", "source_file": "4g_pdsch_crc_task.c"},
    {"task": "4g_pdsch_proc_task",      "rat": "LTE",  "role": "L1/PHY PDSCH processing",
     "evidence": "F-36 string level", "source_file": "4g_pdsch_proc_task.c"},
    {"task": "hspa_agch_event_task",    "rat": "HSPA", "role": "AGCH event handling",
     "evidence": "F-36 string level", "source_file": "hspa_agch_event_task.c"},
    {"task": "c2k_scheduler",           "rat": "CDMA2000", "role": "c2k scheduler",
     "evidence": "F-36 string level", "source_file": "c2k_scheduler.c"},
    {"task": "LISR_c2k_pilot_arrival",  "rat": "CDMA2000", "role": "pilot arrival ISR",
     "evidence": "F-36 string level", "source_file": None},
]

# md1img payload manifest (census per-partition architecture map).
# signedness per the census: modem data payloads ship unsigned.
PAYLOAD_MANIFEST = [
    {"payload": "md1rom",       "size_bytes": 26682512,
     "container": "mtk_hdr", "signed": True,
     "arch": "MIPS32 LE + MIPS16e islands (F-31)"},
    {"payload": "md1drdi",      "size_bytes": 1368064,
     "container": "mtk_hdr", "signed": False,
     "arch": "data/debug image, entropy 0.8-1.5, no ISA claim"},
    {"payload": "md1dsp",       "size_bytes": 6783260,
     "container": "GFH MMM-chain (record type 260) + DSP! inner header",
     "signed": True,
     "arch": "MD32-class DSP (F-36); instruction-level decode gap (F-45)"},
    {"payload": "md1_filter*",  "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "modem catcher-filter data (x8 payloads)"},
    {"payload": "md1_emfilter", "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "modem filter data"},
    {"payload": "md1_mddbmeta", "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "modem DB metadata"},
    {"payload": "md1_mddbmetaodb", "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "gzipped modem-DB XML (2.9 MB decoded), kal_uint32 tables"},
    {"payload": "md1_mddb",     "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "modem DB"},
    {"payload": "md1_mdmlayout", "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "modem layout"},
    {"payload": "md1_file_map", "size_bytes": None, "container": "mtk_hdr",
     "signed": False, "arch": "plain-text name map (carries MOLY_LR13_..._P79.bin/.EDB/.XML.GZ names)"},
]

# ---------------------------------------------------------------------
# Stubs — everything the spec corpus does NOT pin. Emitted verbatim so
# downstream consumers see the boundary; never filled with guesses.
# ---------------------------------------------------------------------

STUBS = {
    "task_entry_addresses": {
        "status": "stub — not pinned by any spec document",
        "reason": "F-31 maps decode coverage, not segment semantics; no task "
                  "table or task entry point has been byte-verified in md1rom.",
    },
    "task_to_region_binding": {
        "status": "stub — not pinned by any spec document",
        "reason": "no public evidence binds the F-36 task-name strings to "
                  "specific md1rom/md1dsp regions.",
    },
    "ccci_channel_map": {
        "status": "stub — not pinned by any spec document",
        "reason": "the host<->modem CCCI interface channel IDs for this build "
                  "are not documented in the lab corpus (taszk/NCC prior art is "
                  "Dimensity-era).",
    },
    "md1rom_segment_map": {
        "status": "stub — named future work by F-31",
        "reason": "per-segment byte-exact map (the loader's INT_InitRegions_C "
                  "route) is F-31's own named next lever; coverage windows are "
                  "256 B / 1 MiB steps.",
    },
    "md32_isa": {
        "status": "stub — open ISA gap (F-45)",
        "reason": "the MD32 instruction encoding for the LR13-era md1dsp core "
                  "is not byte-verified anywhere public; see "
                  "implementations/mediatek/md32-interface/ for the spec'd "
                  "subset (container/interface layer only).",
    },
    "host_interface": {
        "status": "stub — not pinned by any spec document",
        "reason": "the driver-side consumable interface (CCCI/mbIMC/RPC "
                  "message formats) for this MOLY build is undocumented in "
                  "the corpus; the upstream-contribution recon records that "
                  "0.34% of upstream DB rows have any documented interface.",
    },
}


def build_taskmap():
    """Assemble the documented dispatch/task-interface model as one dict."""
    rats = {}
    for t in TASK_INVENTORY:
        rats.setdefault(t["rat"], []).append(t["task"])
    return {
        "component": "md1rom-taskmap",
        "clean_room": ("written from mediatek/docs/*.md + rosemary-census.md "
                       "on 2026-11-16; no proprietary material accessed"),
        "image": IMAGE,
        "entry_chain": ENTRY_CHAIN,
        "region_map": REGION_MAP,
        "task_inventory": TASK_INVENTORY,
        "task_dispatch_families": rats,
        "payload_manifest": PAYLOAD_MANIFEST,
        "stubs": STUBS,
        "notes": [
            "The dispatch structure emitted here is the DOCUMENTED subset: "
            "entry chain, region/ISA map, task-name inventory by radio access "
            "technology, payload manifest. Any field not pinned by the spec "
            "corpus appears under 'stubs'.",
            "The 0x80000/0x700000/0xe00000 windows decode densely under both "
            "MIPS32-default and 16e (shared mips16.sinc) — per-instruction "
            "ISA-mode attribution is F-31's stated negative, so island kind "
            "attribution there is 'code-island', not 'mips16e'.",
        ],
    }


# ---------------------------------------------------------------------
# Byte-level verifier for the documented entry chain.
# Self-contained: verifies exactly the facts F-31 pins (three instruction
# words + the documented 00 65 filler pattern). The _mtc0 encoding is NOT
# checked (mnemonic-only in the spec).
# ---------------------------------------------------------------------

def verify_entry_chain(data):
    """Check a local md1rom image (or any bytes) against the F-31 entry
    chain. Returns a per-field report dict; never raises."""
    checks = []
    if len(data) < 0x30:
        return {"status": "too-short", "checks": [{"field": "length", "ok": False}]}

    def word_at(off):
        return struct.unpack_from("<I", data, off)[0]

    for ins in ENTRY_CHAIN["instructions"]:
        if ins["word"] is None:
            continue  # mnemonic-only in the spec — not byte-checked
        w = word_at(ins["offset"])
        checks.append({"field": "word@0x%x" % ins["offset"],
                       "expected": "0x%08x" % ins["word"],
                       "observed": "0x%08x" % w, "ok": w == ins["word"]})
    fill = data[0x10:0x30]
    ok_fill = fill == b"\x00\x65" * 16
    checks.append({"field": "filler 0x10..0x30", "expected": "00 65 x16",
                   "observed": fill[:8].hex() + "…", "ok": ok_fill})
    status = "ok" if all(c["ok"] for c in checks) else "mismatch"
    return {"status": status, "checks": checks,
            "spec": ENTRY_CHAIN["source"]}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--json", dest="json_out", help="write the taskmap JSON")
    ap.add_argument("--verify-entry", metavar="FILE",
                    help="verify a local md1rom image against the documented "
                         "F-31 entry chain")
    args = ap.parse_args(argv)

    if args.verify_entry:
        with open(args.verify_entry, "rb") as fh:
            rep = verify_entry_chain(fh.read())
        print(json.dumps(rep, indent=1))
        return 0 if rep["status"] == "ok" else 1

    doc = build_taskmap()
    out = json.dumps(doc, indent=1)
    if args.json_out:
        with open(args.json_out, "w") as fh:
            fh.write(out + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
