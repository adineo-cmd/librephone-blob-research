# implementations/mediatek/md1rom-taskmap — clean-room data-driven task-interface model

A data-driven module for the MT6785 (Helio G95) `md1rom` modem image's
**documented** task interface and dispatch structure. Every fact is a
committed spec fact; everything the specs do not pin is an explicit stub.

CLEAN-ROOM STATEMENT: written from `mediatek/docs/md1rom-decode.md` (F-31),
`mediatek/rosemary-census.md`, `mediatek/docs/md1dsp-decode.md` (F-36) and
`mediatek/docs/md32-gap.md` (F-45) on **2026-11-16**; no proprietary
material accessed during development.

## What it emits (`python3 -I md1rom_taskmap.py [--json out.json]`)

- `image` — size, container, ISA attribution (MIPS32 LE entry + MIPS16e
  islands; microMIPS/nanoMIPS ruled out), MOLY LR13 version strings,
  auto-analysis counts (F-31).
- `entry_chain` — the byte-verified reset trampoline at 0x0
  (`lui a2,0x174 / addiu a2,a2,0x2ed0 / jr a2 -> 0x176ed0 / _mtc0
  zero,Count`) plus the documented `00 65` filler pattern (F-31).
- `region_map` — the F-31 decode-density region map (code islands,
  partial windows, data/compressed regions), honestly coverage-derived.
- `task_inventory` / `task_dispatch_families` — the modem L1/PHY task
  names the corpus documents (LTE: 4g_dci_parse_task, 4g_pcfich_parse_task,
  4g_pdsch_crc_task, 4g_pdsch_proc_task; HSPA: hspa_agch_event_task;
  CDMA2000: c2k_scheduler, LISR_c2k_pilot_arrival), each with its
  evidence class (string level, F-36).
- `payload_manifest` — the md1img payload set with container + signedness
  per the census (modem data payloads unsigned; md1dsp via GFH type 260).
- `stubs` — the boundary, verbatim: task entry addresses, task-to-region
  binding, CCCI channel map, per-segment map, MD32 ISA, host interface.

## Byte verifier

`verify_entry_chain(data)` checks a local md1rom image against exactly the
F-31-pinned bytes: the three instruction words (`0x3c060174`, `0x24c62ed0`,
`0x00c00008`) and the `00 65` filler at 0x10..0x30. The `_mtc0` word is
deliberately **not** checked — the spec pins it by mnemonic only (facts-not-
blobs: no invented encoding). CLI: `--verify-entry FILE` (exit 0/1).

## RULE 0 note

This is a model of the lab's own published findings (no equivalent public
artifact exists — the F-31 doc records that no public decode-level analysis
of MT6785 md1rom exists, checked 2026-11-12; re-confirmed 2026-11-16 via the
container component's searches, which surfaced no md1rom task-map or
dispatch-structure tool). The component is a faithful, testable packaging
of documented facts, not a new binary-analysis claim.

## Tests

`python3 -m unittest -v test_md1rom_taskmap` — 11 tests, including
entry-chain verification pass/negative cases on self-made fixture bytes.
