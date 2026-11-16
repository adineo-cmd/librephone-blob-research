# WORKORDER-001 — DESKTOP agent program (v3)

**Machine:** DESKTOP · **Agent budget:** ~300M tokens · **Repo:** `librephone-blob-research` (this clone)
**Issued:** 2026-11-16 (v3) by the Open Discovery Lab lead · **Duration:** one full agent session
**Repo roles (standing):**
- `librephone-blob-research` — LibrePhone work. **PRIORITY 1 on BOTH machines.**
- `open-research-lab` — mathematics and other fields. PRIORITY 2.
- `open-discovery-lab` — the NOTEBOOK (findings from any repo; lead-merged).

**THE DEVICE SPLIT (authoritative 236-device list — F-71 corrected; the "444" was the audit's miscount of the file-centric CSV):**
Fetch `https://codeberg.org/rsavoye/librephone/raw/branch/main/data/devices.sql.bz2` (pg_dump,
fetched byte-exact 2026-11-16), parse the devices COPY block, sort by lower(vendor), lower(model),
lower(build) — codepoint, both machines identical. Script-verified split:
- **DESKTOP owns rows 1–118.**
- **LAPTOP owns rows 119–236** (see WORKORDER-002-laptop.md) — 118 devices, 46 extracted,
  holding the ADSP bm2nXX leverage fleet (bm2n12/14/15.bin ×14 devices each) plus 6 QCA BT
  files (×4 devices) and a619_gmu.bin (×5). Pre-built inventory:
  `blob-matrix/laptop/devices-half.csv`.
Each machine runs the SAME four-phase program on its half. The lead merges the two halves into
the full 236-device picture.

**THE FOUR WORK TYPES (owner directive — every phase runs on your device half):**
deep RE · blob families documented · clean-room implementation · device fragmentation.

**Discipline:** commit locally per phase; push at phase end; write
`workorders/inbox/STATUS-DESKTOP.md` when done and after any halt. Read `AGENTS.md` first
(RULE 0 prior-art search, RULE 1 improve previous work). Facts-not-blobs: no proprietary
payload ever committed. Clean-room rule (owner directive 2026-11-16, amending RULE 3): you
MAY write implementations, but ONLY from the lab's published spec documents — an implementer
never reads proprietary code, headers, or strings; every implementation file carries a
clean-room statement header (spec-only derivation, no proprietary access).

## PHASE 1 — DEEP RE (metadata-first, per device in rows 1–222)

**UPDATED 2026-11-16 (F-71): the coverage matrix already EXISTS.**
`upstream-contribution/blob-database/coverage-matrix.csv` holds 33,917 blob rows × 123
blob-populated devices (distilled from the upstream PostgreSQL/CSV metadata — the published
"database" is metadata-only; the payload corpus lives on the maintainer's machine at
/work/Lineage-images/ and is published nowhere; full findings in
`blob-database/recon.md`). Your Phase 1 therefore starts from that matrix:

(a) map your half (rows 1–222) against it — which of your devices are among the 123
extracted, which fall in the 113 listed-not-populated;
(b) LEVERAGE-FIRST ordering: check your half against the top-20 leverage list in recon.md
(the QCA BT patch fleet covers 29 devices per file — whichever top-20 entries sit in your
half are your Phase 2/3 headline);
(c) for your half's not-populated devices, attempt population from the **public LineageOS
install packages** (per-device ~1–1.3 GB fetches, only as needed — no bulk download exists
anywhere);
(d) extend the matrix rows for your half (`blob-matrix/desktop/` outputs below).

1. For each device: gather every public fact obtainable without the payload — upstream data
   repo rows, vendor/SoC identification, public mainline kernel support status, public vendor
   trees, published teardown/firmware listings. Network is flaky: retries, and mark failures
   honestly.
2. Per family present (modem/wifi/bt/tz/boot/adsp/cdsp/camera/gpu/other): census what is
   obtainable (file names, sizes, hashes where public, ISA from public analyses where they
   exist — cite them; never re-claim another project's result as lab work).
3. Output: `blob-matrix/desktop/devices-001-222.csv` —
   `device,vendor,soc,family,file,bytes,sha256,public_status,notes`. Plus
   `blob-matrix/desktop/deep-re-notes.md` for per-device findings that exceed a CSV row.

## PHASE 2 — BLOB FAMILIES DOCUMENTED (template-driven, per device/family in rows 1–222)

1. For every family where Phase 1 produced real data: write the family doc from the FP6/MT6785
   exemplar templates (`qualcomm-fp6/docs/`, `mediatek/docs/` are the patterns): container
   layout, ISA/proof status, interface facts, open questions — each doc marked with its
   evidence class (census/ISA-identified/spec-complete).
2. Output: `docs/devices/<device>/<family>.md` (stub-level is honest for metadata-only
   devices; the FP6/MT6785 depth is the target only where payloads/analysis exist).

## PHASE 3 — CLEAN-ROOM IMPLEMENTATION (from published specs ONLY)

1. Inventory the lab's completed specs (FP6 WMI dispatch architecture, LPEC codec model
   (100%-closed), boot-chain map, TrustZone census, MT6785 ISA maps…).
2. Write clean-room implementation components from those specs ONLY — every file headered
   with the clean-room statement. Suggested starts (highest value first):
   - **Qualcomm side:** the wpss WMI/HTT/CE interface components that open PR #58
     (codeberg rsavoye/librephone) explicitly lacks — the lab's decoded dispatch spec is
     exactly what its author asked for. Liaison note: implement against
     `qualcomm-fp6/docs/wmi-*` + the dispatch paper, NOT against ath11k's header copies
     unless they are clean-room-safe public code (they are GPL public code — usable).
   - **LPEC:** the decoder exists (`track-c-discovery-engine` lpec_decoder) — package it as a
     standalone implementation with the spec doc as its design document.
3. Output: `implementations/<family>/<component>/` with README stating the spec-derived
   provenance. Where a spec is incomplete, implement the spec'd subset and file the gap as an
   open item — never guess beyond the spec.

## PHASE 4 — DEVICE FRAGMENTATION (your half, merge-ready)

1. From Phases 1-2: the fragmentation analysis for rows 1–222 — SoC generations, family
   sharing, leverage ranking (blobs shared across the most devices), and the split-notes the
   lead needs to merge your half with the laptop's into the full 444-device picture.
2. Output: `blob-matrix/desktop/fragmentation-half.md` + the merge-ready CSV.

## FALLBACK (Priority 2 — after all four phases)

`open-research-lab`: OEIS A385403 proof attack per
`math/property-b-covering/results/a385403-results.md` §"Continuation attack" (structural
Fano-free-8-edge probe FIRST — it proves both brackets by counting), then EP614 extension
(`math/erdos614-fnk/`). Only if Phases 1-4 consumed little budget.

## Do NOT touch

`workorders/WORKORDER-002-laptop.md`, the laptop's files (rows 223-444 outputs),
open-discovery-lab (the notebook is the lead's).
