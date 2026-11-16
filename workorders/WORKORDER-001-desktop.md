# WORKORDER-001 — DESKTOP agent program

**Machine:** DESKTOP · **Agent budget:** ~300M tokens · **Repo:** `librephone-blob-research` (this clone)
**Issued:** 2026-11-16 by the Open Discovery Lab lead · **Duration:** one full agent session
**Repo roles (standing):**
- `librephone-blob-research` — LibrePhone work. **PRIORITY 1 on BOTH machines.**
- `open-research-lab` — mathematics and other fields. **PRIORITY 2.**
- `open-discovery-lab` — the NOTEBOOK: records every finding, solved problem, or improvement
  made in either repo (or any other repo). You never work IN it — but every session's
  discoveries belong in its FINDINGS.md ledger, which the lead merges.

**Work division between the two machines (LibrePhone first, split evenly):**
- DESKTOP = the DATA+COVERAGE side (below). LAPTOP = the ISSUES+UPSTREAM side (see
  WORKORDER-002-laptop.md). No overlap.

**Discipline:** commit locally per deliverable; push at the end of each domain; write
`workorders/inbox/STATUS-DESKTOP.md` when done and after any halt. Read this repo's `AGENTS.md`
first (RULE 0 prior-art search, RULE 1 improve previous work, RULE 3 clean-room spec producer —
you document, you never write firmware). Facts-not-blobs: no proprietary payload is ever
committed.

## DOMAIN 1 (LibrePhone) — the 444-device blob coverage matrix + fragmentation analysis

The core open item: everything LibrePhone lists, measured and mapped.

1. Fetch the upstream data: `https://codeberg.org/rsavoye/librephone/raw/branch/main/data/devices.csv`
   (444 devices) and `data/sizes.csv` (the lab's `upstream-contribution/pr7-sizes-fp6.md` added
   702 FP6 rows — read it for the exact format). Enumerate the repo tree via the codeberg API
   (`/api/v1/repos/rsavoye/librephone/git/trees/{sha}?recursive=true`) for every other data file.
2. Build `blob-matrix/devices-analysis.md`: the vendor × SoC × generation breakdown of all 444
   devices — the fragmentation picture IS the deliverable (distinct SoC generations, device
   families sharing firmware families, leverage points where one RE result covers N devices).
3. Build `blob-matrix/coverage-matrix.csv`: one row per device —
   `device,vendor,soc,families_present,in_sizes_csv,lab_coverage(none/fp6/mt6785-method),priority(P1|P2|P3)`.
   P1 = Fairphone FP6 (FSF flagship — fully covered), P2 = SoCs the lab's method already covers,
   P3 = the rest. Honest marks only: no coverage claim without a committed doc behind it.
4. If upstream or librephone.fsf.org hosts per-device firmware listings/blobs for devices beyond
   FP6: extend the matrix with their inventories (names+sizes+hashes only — metadata is fine,
   payload bytes stay out of the repo).
5. Fallback: the owner is NOT certain a 100 GB blob database exists. If your enumeration finds
   no such corpus, document that finding (every probe + URL) and build the matrix from
   devices.csv + sizes.csv alone — the 444-device metadata picture is still the deliverable.

## DOMAIN 2 (LibrePhone) — per-SoC census method plans (P2/P3 devices)

1. For the top P2 device clusters from your matrix (biggest device counts sharing an SoC family
   the lab's method covers — e.g. other Snapdragon 8-series phones, other MT6785-era devices):
   write per-SoC census method plans into `blob-matrix/method-<soc>.md` — the FP6/MT6785
   pipeline (container walk → ISA identification → per-family census → interface decode)
   adapted to each SoC's known public data (mainline kernel support, public vendor trees).
2. These plans are what turn the matrix from a picture into a queue: each plan names the
   public sources, the extraction steps, and the expected per-family outputs.

## DOMAIN 3 (LibrePhone) — provenance + hygiene sweep (RULE 1)

1. Re-verify recorded hashes against fresh fetches where payloads are public (sizes.csv rows,
   the DVE ISO md5); fix dangling references, stale counts, wrong F-numbers anywhere in this
   repo (leave it better than you found it; before/after in your status file).
2. Re-fetch the paste-ready packages' target texts (pr5/pr7/pr8/pr9 quote upstream lines
   exactly) and confirm they are still current.

## DOMAIN 4 (Priority 2 — open-research-lab, ONLY after Domains 1-3)

Clone https://github.com/adineo-cmd/open-research-lab. Then, in order:
1. OEIS A385403 proof attack — execute the named plan in
   `math/property-b-covering/results/a385403-results.md` §"Continuation attack": FIRST the
   structural probe "does any Fano-free non-2-colorable 3-graph with 8 edges exist (no
   coverage)" — INFEASIBLE there proves BOTH a(13)=9 and a(14)=10-bound by counting alone;
   then the replay-seeded lazy master (all 1716 size-55 colorings, checkpoint per iteration,
   12 workers, 4-6 h). Solver setup workaround is documented in the results doc.
2. Erdős #614 extension — re-run the bounded cells at 3600 s budgets, add the derived redundant
   per-subset cut, extend the exact tables (`math/erdos614-fnk/`).
Record what you did in `math/.../results/` docs; the lead merges the ledger rows.

## Deliverables + push discipline

- Commit locally per deliverable; push after each domain.
- `workorders/inbox/STATUS-DESKTOP.md`: full report (domains done, counts, findings, honest
  negatives, could-not-do list).
- Do NOT touch: `workorders/WORKORDER-002-laptop.md`, the laptop's files, or
  open-discovery-lab (the notebook is the lead's).
