# STATUS-LAPTOP — WORKORDER-002 session 2026-11-16 (updated)

| item | status |
|---|---|
| Phase 1 (deep RE, rows 119–236) | DONE — devices-half.csv from the authoritative devices.sql.bz2; leverage-first mapping vs the recon top-20 (verified: all 20 present, presence counts exact) |
| Phase 2 (families documented) | DONE — 3 fleet docs (ADSP bm2nXX, QCA BT, Adreno GMU) + 20 per-device leverage stubs |
| Phase 3 (clean-room implementation) | DONE — mediatek container/md1rom-taskmap/md32-interface + LPEC re-home (57/57 tests) AND qca-bt TLV parser (the ×29-device leverage family, all mainline-downloaded families covered) |
| Phase 4 (fragmentation half) | DONE — fragmentation-half.md + sharing-clusters.csv (7,042 clusters) + summary JSON + re-runnable builder |
| Domains 1-2 (Codeberg issues program) | DONE — fresh 28-issue sweep (open set unchanged; pr5/pr8 need no rework), pr10 package completes the set (#15 BT interface doc, #19 split table doc, #36, #35 partial, #56 companion, honest classification of the rest) + interface-bt.md + userspace-firmware-split.md |
| Per-SoC method plans | DONE — blob-matrix/per-soc-method-plans.md |
| Regulatory hurdles | DONE — radio-regulatory-hurdles.md (675 lines: type-approval, RE legality, export controls, FSF position, precedents, recommended order of operations) |
| Provenance sweep (Domain 3) | DONE — recon.md stub pointer added; implementations/README.md RULE-0 delta recorded |

Push state: merged by the lead as F-73 (issues) + F-74 (regulatory + QCA) and pushed.
