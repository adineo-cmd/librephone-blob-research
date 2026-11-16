# WORKORDER-002 — LAPTOP agent program

**Machine:** LAPTOP · **Agent budget:** ~300M tokens · **Repos:** `librephone-blob-research`
(PRIORITY 1) then `open-research-lab` (PRIORITY 2 — clone:
https://github.com/adineo-cmd/open-research-lab)
**Issued:** 2026-11-16 by the Open Discovery Lab lead · **Duration:** one full agent session
**Repo roles (standing):**
- `librephone-blob-research` — LibrePhone work. **PRIORITY 1 on BOTH machines.**
- `open-research-lab` — mathematics and other fields. **PRIORITY 2.**
- `open-discovery-lab` — the NOTEBOOK: records every finding/solved/improved item from either
  repo; the lead merges it — you never work IN it.

**Work division (LibrePhone first, split evenly with the desktop):**
- LAPTOP = the ISSUES+UPSTREAM side (below). DESKTOP = the DATA+COVERAGE side (see
  WORKORDER-001-desktop.md). No overlap. LibrePhone domains come FIRST on both machines;
  open-research-lab work starts only after your LibrePhone domains are done.

**Discipline:** commit locally per deliverable; push at the end of each domain; write
`workorders/inbox/STATUS-LAPTOP.md` when done and after any halt. Read `AGENTS.md` first (RULE 0
prior-art search, RULE 1 improve previous work, RULE 3 clean-room spec producer). Facts-not-blobs.

## DOMAIN 1 (LibrePhone) — the 28 open Codeberg issues: finish every answerable one

1. Fetch all 28 open issues FRESH (API: `/api/v1/repos/rsavoye/librephone/issues?state=open`).
   The F-69 audit (`upstream-contribution/librephone-wants.md`) classified them — re-check
   current status first: some may have been answered or closed upstream since; RULE 1 — do not
   redo done work, cite what is already there.
2. For each still-open issue without a packaged answer, write the doc + paste-ready answer.
   Already covered by prior packages (do NOT redo): #17/#18/#26/#37/#39/#40/#44/#45/#46
   (pr8 + interface docs), #38/#41/#42/#43/#33 (pr5 C-1..C-3), the AVR/RISC-V corrections
   (pr5/pr6). YOUR targets are the remainder, especially the High-priority ones:
   - **#15 (High) — BT driver↔blob interface doc.** Base: `qualcomm-fp6/docs/bt-firmware-census.md`
     + mainline `drivers/bluetooth/btqca.c` + `hci_qca` sources.
   - **#19 (High) — the user-space-vs-firmware split.** The bootchain census + per-family
     censuses answer exactly this: produce the split table (which function lives where, per
     family) as its own doc.
   - **#36 — radio-directory blobs.** Identify what the radio/modem directory contains per the
     bootchain census + public modem-partition naming.
   - #50/#56/#59/#61/#62/#63/#2/#5/#23 — classify honestly: answer from public data, or mark
     BLOCKED-WITH-PLAN (needs binaries/hardware/owner), never fake.
3. Package: `upstream-contribution/pr10-remaining-issues-package.md` — paste-ready, same style
   as pr5/pr8 (read them first for format), every claim [PUBLIC]/[LAB]/[OPEN] with URL + access
   date. Append a pointer to `upstream-contribution/README.md` (append only).

## DOMAIN 2 (LibrePhone) — per-SoC census method plans (P2/P3 devices)

1. The desktop builds the 444-device matrix; your complementary half: for the SAME top P2
   device clusters, write the **upstream-facing method plans** into
   `blob-matrix/method-<soc>-upstream.md` — what LibrePhone could accept upstream per SoC
   (which doc stubs, which sizes.csv rows, which interface facts), so the queue converts into
   filed contributions. Coordinate via the matrix files the desktop produces (poll
   `blob-matrix/` — if the desktop hasn't landed them yet, work from devices.csv directly and
   note it).
2. If you finish before the desktop's matrix lands: start with the FP6/MT6785 method templates
   (they exist — `qualcomm-fp6/docs/`, `mediatek/docs/`) as the pattern.

## DOMAIN 3 (LibrePhone) — provenance + hygiene sweep (RULE 1)

Same sweep as the desktop's Domain 3 but on YOUR files: verify package target texts are still
current upstream, fix stale references in your docs, list before/after in your status file.

## DOMAIN 4 (Priority 2 — open-research-lab, ONLY after Domains 1-3)

Clone https://github.com/adineo-cmd/open-research-lab. Then, in order:
1. Track C frontier: mine the file-formats wiki successor
   (https://fileformats.archiveteam.org — direct access may fail; Wayback snapshots work) for
   formats with NO public documentation and OBTAINABLE samples (cross-reference the dexvert
   samples corpus: https://github.com/Sembiance/dexvert). Build
   `discovery-engine/format-targets-2026-11.md` — top-20 queue scored by novelty × sample
   availability × difficulty, RULE-0 checked against everything the lab already did (dwm, lpec,
   igs, nt, pvd, aik, clarion, professional-draw, psion-aik are taken). Then execute ONE full
   format RE end-to-end (samples → census → decode attempt → spec doc) under
   `discovery-engine/format-re-2026-11/`. Honest negatives are valid deliverables.
2. A385403 proof attack (only if Domain 3's RE consumed little budget): execute the plan in
   `math/property-b-covering/results/a385403-results.md` §"Continuation attack" — FIRST the
   structural probe "does any Fano-free non-2-colorable 3-graph with 8 edges exist (no
   coverage)" — INFEASIBLE there proves BOTH a(13)=9 and a(14)=10-bound by counting alone;
   then the replay-seeded lazy master (all 1716 size-55 colorings, 12 workers, 4-6 h).
   Solver env: `python3 -m venv --system-site-packages venv-math && venv-math/bin/pip install
   ortools` (network workaround documented in the results doc).

## Deliverables + push discipline

- Commit locally per deliverable; push after each domain.
- `workorders/inbox/STATUS-LAPTOP.md`: full report.
- Do NOT touch: `workorders/WORKORDER-001-desktop.md`, the desktop's matrix files, or
  open-discovery-lab (the notebook is the lead's).
