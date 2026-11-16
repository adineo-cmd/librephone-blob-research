# WORKORDER-002 — LAPTOP agent program (research frontier: math + format-RE)

**Machine:** LAPTOP · **Agent budget:** ~300M tokens · **Repo:** `open-research-lab` (clone it:
https://github.com/adineo-cmd/open-research-lab)
**Issued:** 2026-11-16 by the Open Discovery Lab lead · **Duration:** one full agent session
**Rule:** you have this repo to yourself — the desktop agent works a different repo. Commit
locally per deliverable; push at the end of each domain; write
`workorders/inbox/STATUS-LAPTOP.md` (in THIS repo, librephone-blob-research — cross-repo status
lives there) when done and after any halt.

You are an AI coding agent running on the owner's laptop. First read the repo's `AGENTS.md`
(RULE 0 uniqueness + prior-art search, RULE 1 improve previous work, candidates-not-claims,
everything reproducible) and the track READMEs for the areas below. Solver environment: install
`python3 -m venv --system-site-packages venv-math && venv-math/bin/pip install ortools` (known
workaround for this network: if wheel downloads corrupt, `curl -sL -C -` resume loops until
`unzip -t` passes).

## DOMAIN 1 — OEIS A385403: break the a(13)/a(14) lower-bound proofs (math/grid-ramsey sibling: math/property-b-covering/)

Read `results/a385403-results.md` §"Continuation attack" + the final-report notes first. State:
a(11)=9, a(12)=9 proved; **8 ≤ a(13) ≤ 9** and **9 ≤ a(14) ≤ 10** open — a systematic ladder
(deduped constraints m=55/70, lazy cutting-planes 196 cuts, Fano case-split 51,480 nogoods, SCIP,
halved model at 3000 s) all returned UNKNOWN at (13,8).

The named next-session plan (execute it):
1. Seed the lazy cutting-plane master with **all 1716 size-55 colorings** (the balanced
   minimal-mono-set class — saved in the lazy certificate `a385403b_n13_k08*.json` pool) +
   checkpoint the pool each iteration + fano-free master + 12 workers, ≥ 4–6 h wall.
2. Pure structural probe: **"does any Fano-free non-2-colorable 3-graph with 8 edges exist
   (no coverage constraint)?"** — INFEASIBLE there proves BOTH (13,8) and (14,9) by counting
   alone (Fano 7 edges cover 7 vertices; each extra triple covers ≤ 3 new). Try this FIRST —
   it is a much smaller search space than the covering variant.
3. Re-run halved (13,8) / fano (14,9) at 12 workers ≥ 3600 s as the fallback evidence run.
4. If (13,8) INFEASIBLE lands: a(13)=9 is proved immediately (the k=9 witness is already
   certified). Update certificates (`a385403d_*` prefix — don't overwrite `b_`/`c_`),
   `results/a385403-results.md`, and the OEIS draft `results/oeis-submission-draft.md`.
5. Honest fallback: if all attempts still return UNKNOWN, record the new attempt ladder and
   stop — brackets stand, no overclaiming.

## DOMAIN 2 — Erdős #614: extend the exact tables (math/erdos614-fnk/)

Current: f(n,2) exact n=4..9 (2,4,8,12,17,23), f(n,3) exact n=5..9 (3,7,11,15,22), f(n,4)
exact n=6..9 (4,9,15,21); bounds beyond. The optimality proofs harden fast (n=9 k=2 took
147 s; n=10 hit the 240 s cap).

1. Re-run the bounded cells with LONG budgets (3600 s, 12 workers): (10,2), (11,2), (12,2),
   (10,3), (11,3), (10,4), (11,4) — every OPTIMAL result extends the exact table; every
   FEASIBLE result yields a better upper bound + proven lower bound (`best_bound` field —
   record both).
2. Extend the model where it helps: add a redundant cut the solver can use (e.g. per-subset
   edge-count lower bound: a (k+2)-set with max-deg ≥ k needs ≥ k edges inside the set —
   wait, ≥ ceil(k·(k+2)/2)? derive it exactly: induced max-degree ≥ k forces ≥ k edges in the
   subset — add Σ_{edges ⊆ S} e ≥ k as a redundant constraint per subset; measure the speedup).
3. Rule 0 re-check: OEIS-search the extended sequences again; if any sequence matches a
   graph-theoretic meaning now, cite it; else the tables remain new data for EP614.
4. Update `results/ep614-results.md` + certificates (`fnk_*` naming continues).

## DOMAIN 3 — Track C: mine the file-formats wiki successor + one format RE (track-c in open-discovery-lab is desktop-adjacent — keep your outputs in open-research-lab/discovery-engine/)

1. Mine https://fileformats.archiveteam.org (direct access may be blocked on some networks —
   Wayback snapshots work: `http://web.archive.org/web/2026/http://fileformats.archiveteam.org/wiki/Category:...`)
   for formats with **no public documentation** and **obtainable samples** (cross-reference the
   dexvert samples corpus: https://github.com/Sembiance/dexvert — the samples/ tree names which
   formats have files). Build `discovery-engine/format-targets-2026-11.md`: the top-20 target
   queue scored by (novelty × sample availability × apparent difficulty), RULE-0 checked (no
   target the lab already did: dwm, lpec, igs, nt, pvd, aik, clarion, professional-draw,
   psion-aik are taken).
2. Pick ONE target from your queue and execute the full lab methodology end-to-end: fetch
   samples → census (headers, structure) → decode attempt → spec document. Commit the script +
   JSON results + doc under `discovery-engine/format-re-2026-11/`. Honest negative results are
   valid deliverables.
3. If the chosen target needs samples you cannot fetch (network), swap to the next queue item —
   the queue document is the durable deliverable.

## DOMAIN 4 — Track B (only if budget remains — lowest priority)

The astro follow-ups left open: Karpov-corroborated vocabulary stays ready for any pm > 300
mas/yr future candidate; SDSS blink extends to the 621-candidate tail (18/35 done — the rest
are no-DR18-coverage cases; check the LS-DR10 release if it exists). This is stretch — skip if
Domains 1-3 consumed the session.

## Deliverables + push discipline

- Commit locally per deliverable; push after each domain. STATUS file:
  `workorders/inbox/STATUS-LAPTOP.md` inside the librephone-blob-research clone (or paste it
  into your final report if that clone is not present on the laptop).
- Sizing note: sized for ~300M tokens. Domain 1 is the hardest and highest-value; Domain 2 is
  mechanical and safe; Domain 3 is the discovery frontier. Do NOT touch
  `librephone-blob-research` content (the desktop's domain) except the single STATUS file.
