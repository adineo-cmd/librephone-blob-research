# WORKORDER-002 — LAPTOP agent program (v3)

**Machine:** LAPTOP · **Agent budget:** ~300M tokens · **Repo:** `librephone-blob-research` (this clone)
**Issued:** 2026-11-16 (v3) by the Open Discovery Lab lead · **Duration:** one full agent session
**Repo roles (standing):**
- `librephone-blob-research` — LibrePhone work. **PRIORITY 1 on BOTH machines.**
- `open-research-lab` — mathematics and other fields. PRIORITY 2.
- `open-discovery-lab` — the NOTEBOOK (findings from any repo; lead-merged).

**THE DEVICE SPLIT (owner directive: divide the 444 listed devices evenly):**
Fetch `https://codeberg.org/rsavoye/librephone/raw/branch/main/data/devices.csv`, sort by
device name (plain codepoint sort — BOTH machines use the same sort so halves never overlap),
then:
- DESKTOP owns **rows 1–222** (see WORKORDER-001-desktop.md).
- **LAPTOP owns rows 223–444.**
Each machine runs the SAME four-phase program on its half. The lead merges the two halves.

**THE FOUR WORK TYPES:** deep RE · blob families documented · clean-room implementation ·
device fragmentation.

**Discipline:** commit locally per phase; push at phase end; write
`workorders/inbox/STATUS-LAPTOP.md` when done and after any halt. Read `AGENTS.md` first.
Facts-not-blobs. Clean-room rule (owner directive 2026-11-16, amending RULE 3): you MAY write
implementations, but ONLY from the lab's published spec documents — never from proprietary
material; every implementation file carries the clean-room statement header.

## PHASE 1 — DEEP RE (metadata-first, per device in rows 223–444)

Identical to the desktop's Phase 1 (WORKORDER-001-desktop.md — read it for the full spec).
**UPDATED 2026-11-16 (F-71):** the coverage matrix already exists —
`upstream-contribution/blob-database/coverage-matrix.csv` (33,917 blob rows × 123
blob-populated devices; the published upstream "database" is metadata-only, payloads are not
published anywhere — see `blob-database/recon.md`). Your job: map your half (rows 223-444)
against the matrix, LEVERAGE-FIRST (the top-20 list in recon.md — the bm2nXX.bin ADSP fleet
and image-level sharing like abl.img ×75 / devcfg.img ×76 fall where they fall; whichever of
the QCA BT fleet / ADSP fleet sits in your half is your Phase 2/3 headline), attempt
population of your half's not-populated devices from public LineageOS packages per-device as
needed, and extend the matrix rows for your half.
Output: `blob-matrix/laptop/devices-223-444.csv` + `blob-matrix/laptop/deep-re-notes.md`.

## PHASE 2 — BLOB FAMILIES DOCUMENTED (per device/family in rows 223–444)

Family docs from the FP6/MT6785 exemplar templates, evidence-classed
(census/ISA-identified/spec-complete). Output: `docs/devices/<device>/<family>.md`.

## PHASE 3 — CLEAN-ROOM IMPLEMENTATION (from published specs ONLY)

Same rules as the desktop's Phase 3; your assignment is the **MediaTek side** (the lab's
MT6785 ISA maps are the spec corpus — the desktop takes the Qualcomm side):
1. **MediaTek implementations from the committed specs** (`mediatek/docs/`): the md1rom
   task-interface components, the MD32 spec-derived interface stubs (the MD32 ISA gap is
   named in ROADMAP M-1/I-4 — implement only what the specs actually pin), the container/
   signed-record-chain walkers (the container format is documented byte-for-byte).
2. Where a spec is incomplete: implement the spec'd subset, file the gap as an open item —
   never guess beyond the spec.
3. Output: `implementations/<family>/<component>/` with clean-room statement headers.

## PHASE 4 — DEVICE FRAGMENTATION (your half, merge-ready)

Fragmentation analysis for rows 223–444 (SoC generations, family sharing, leverage ranking),
merge-ready for the lead: `blob-matrix/laptop/fragmentation-half.md` + CSV.

## FALLBACK (Priority 2 — after all four phases)

`open-research-lab`: Track C frontier — mine the file-formats wiki successor
(https://fileformats.archiveteam.org; Wayback snapshots work when direct fails) for
undocumented formats with obtainable samples (dexvert corpus:
https://github.com/Sembiance/dexvert), build the top-20 target queue
(`discovery-engine/format-targets-2026-11.md`), then execute ONE full format RE end-to-end
(census → decode attempt → spec doc; honest negatives are valid). RULE-0: dwm, lpec, igs, nt,
pvd, aik, clarion, professional-draw, psion-aik are already taken.

## Do NOT touch

`workorders/WORKORDER-001-desktop.md`, the desktop's files (rows 1-222 outputs),
open-discovery-lab (the notebook is the lead's).
