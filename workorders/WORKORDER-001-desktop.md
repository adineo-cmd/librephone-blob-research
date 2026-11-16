# WORKORDER-001 — DESKTOP agent program (LibrePhone corpus + upstream)

**Machine:** DESKTOP · **Agent budget:** ~300M tokens · **Repo:** `librephone-blob-research` (this clone)
**Issued:** 2026-11-16 by the Open Discovery Lab lead · **Duration:** one full agent session
**Rule:** you have the repo to yourself — no other agent works in it. Commit locally per
deliverable; push at the end of each domain; write `workorders/inbox/STATUS-DESKTOP.md` when done
(and after any halt).

You are an AI coding agent running on the owner's desktop. Work through the program below IN
ORDER. First read this repo's `AGENTS.md` (RULE 0 uniqueness + prior-art search, RULE 1 improve
previous work, RULE 2 cross-vendor, RULE 3 clean-room spec producer — you document; you do not
write firmware) and `upstream-contribution/librephone-wants.md` (the F-69 47-row audit — rows
marked OPEN-E are your source list).

## DOMAIN 1 — The 444-device blob coverage matrix (the biggest open item)

1. Fetch the upstream data: `https://codeberg.org/rsavoye/librephone/raw/branch/main/data/devices.csv`
   (444 devices) and `data/sizes.csv` (format reference — the lab's pr7 package added 702 FP6
   rows: `upstream-contribution/pr7-sizes-fp6.md`). Enumerate the repo tree via the codeberg API
   (`/api/v1/repos/rsavoye/librephone/git/trees/{sha}?recursive=true`) for any other data files.
2. Build `blob-matrix/devices.csv-analysis.md`: vendor × SoC × generation breakdown of all 444
   devices. The fragmentation picture IS the deliverable: how many distinct SoC generations, how
   many device families share the same firmware families, where the leverage points are (one RE
   result that covers N devices).
3. Build `blob-matrix/coverage-matrix.csv` scaffold: one row per device — columns:
   `device,vendor,soc,families_present,rows_in_sizes_csv,lab_coverage(none/fp6/mt6785-method-applicable),priority(P1|P2|P3)`.
   P1 = Fairphone FP6 (the FSF flagship, fully covered by the lab already), P2 = devices whose
   SoC family the lab has method coverage for, P3 = the rest. Mark honestly — no coverage
   claims without a committed doc behind them.
4. If the upstream repo (or librephone.fsf.org) hosts per-device firmware listings/blobs for any
   devices beyond FP6: extend the matrix with their file inventories (names+sizes+hashes only —
   metadata is fine; payload bytes stay out of the repo).

## DOMAIN 2 — The 28 open Codeberg issues: finish every answerable one

The F-69 audit classified them; Agent L already produced interface docs for #17/#18/#26/#37/
#39/#40/#44/#45/#46 (`qualcomm-fp6/docs/interface-*.md`) and answer packages pr5/pr8. Your job is
the remainder:

1. Fetch all 28 open issues fresh (API: `/api/v1/repos/rsavoye/librephone/issues?state=open`) —
   re-check status (some may have been answered upstream since the audit; RULE 1: don't redo
   done work — cite what's already there).
2. For each still-open issue without a packaged answer: write the doc or the paste-ready answer
   into `upstream-contribution/pr9-remaining-issues-package.md`, same style as pr5/pr8 (read
   those for format). The lab's committed docs + public kernel sources are your evidence base;
   mark [PUBLIC]/[LAB]/[OPEN] per claim, URL + access date every time.
3. High-priority items specifically: #15 (BT driver↔blob interface — the lab's bt-firmware-census
   is the base), #19 (user-space-vs-firmware split — the bootchain + per-family censuses answer
   this), #36 (radio-directory blobs), #34 (TrustZone exploit — OUT OF SCOPE per owner exclusion,
   say so in the package if it comes up).
4. Update `upstream-contribution/README.md` with the new package pointer (append; don't rewrite
   existing sections).

## DOMAIN 3 — Provenance + hygiene sweep (RULE 1)

1. Verify every hash recorded in the docs against your fresh re-fetches where the payload is
   public (e.g. sizes.csv rows, the DVE ISO md5).
2. Fix any dangling reference, stale count, or wrong F-number in this repo's docs (the lab's
   rule: leave the repo better than you found it; list before/after in your status file).
3. Re-verify the paste-ready packages' target texts are still unchanged upstream (the pr5/pr8
   blocks quote exact upstream lines — re-fetch each and confirm).

## Deliverables + push discipline

- Commit locally per deliverable. Push after Domain 1, after Domain 2, and after Domain 3.
- `workorders/inbox/STATUS-DESKTOP.md`: the full report (domains done, counts, findings, honest
  negatives, anything you could NOT do and why).
- Sizing note: this program is sized for ~300M tokens. If you finish early, the stretch goal is
  Domain 4: draft the P2-device census plans (per-SoC method adaptations of the lab's FP6/MT6785
  pipeline) as doc stubs in `blob-matrix/`.
- Do NOT touch: `open-research-lab` (the laptop's domain), other repos, anything in
  `workorders/WORKORDER-002-laptop.md`.
