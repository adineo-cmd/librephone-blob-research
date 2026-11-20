# Agent assignment — 6 providers, effort-balanced, no collisions

Six agents work `adineo-cmd/open-device`. The two zcode providers run GLM-5.3,
which is strong at firmware/blob RE, so they own the deepest RE streams. The
opencode providers take the SoC, device, driver, doc and fleet work. Every
`area:` label has exactly one owner, so no two agents can pick the same issue.

## Measured backlog (from the committed catalogs)

| work kind | count | effort |
|---|---|---|
| firmware family docs (present) | 858 | deep |
| device parts/subfamilies | 18 | deep |
| device packages (per-device, mixed) | 245 | mixed |
| SoC + CPU + GPU core packages | 81 | deep |
| driver interfaces + blob specs | 51 | deep |
| clean-room / OSS implementations | 26 | deep |
| fleet + deep-RE + site packages | 31 | deep |
| "verify absence" negatives | 249 | quick |

## The six slots — effort-balanced

### zcode — GLM-5.3 (deepest firmware/blob RE)

| slot | owns `area:` | issues | workload |
|---|---|---|---|
| **ZC-1** | `firmware` | 876 deep + 245 device packages = **1,121** | The core firmware RE stream. Device packages mix quick checks with deep per-family work, so no monotony. |
| **ZC-2** | `blobs`, `drivers`, `cpu`, `gpu` | 105 deep | Pure container-format, driver-contract and core-ID RE. Uniformly deep, high-value work; ZC-2 also reviews ZC-1's blob/driver output. |

### opencode (SoC, cores, fleet, clean-room, docs, historic)

| slot | owns `area:` | issues | workload |
|---|---|---|---|
| **OC-1** | `soc`, `historic` | 29 SoC + 3 deep-RE = **32** deep | SoC generations + historic queue. |
| **OC-2** | `triage`, `upstream` | 249 quick negatives + 1 upstream filing | Standalone absence checks (relabelled `area:triage`) + upstream PR work. Genuine work that would otherwise be lost. |
| **OC-3** | `tools` | 26 clean-room/impl + 1 link-maintenance | Clean-room implementations from published specs; external code-host directory upkeep. |
| **OC-4** | `docs`, `site`, `repo` | 141 doc verifications + 7 site + repo upkeep | Documentation/link verification and website upkeep. Quick but necessary; balances the strong models' deep work. |

The 249 standalone "verify absence" negatives were relabelled `area:triage`
and belong to OC-2. ZC-1 therefore works only deep firmware RE. OC-1 and OC-3
have smaller, uniformly deep queues; OC-4 has the document-verification sweep.
Every provider has real work; no one is left idle or given only trivia.

## Overflow rule (no idle strong model)

If a provider empties its queue, it may take from another area **only after**:
- posting `CLAIM` on the specific issue, and
- the current area owner posting `HANDOFF <slot>` on that issue.

HANDOFF is the only ownership transfer. Without it, ownership is fixed. This
lets GLM-5.3 helpers absorb opencode overflow without colliding, and vice versa.

## Procedure (every agent)

1. Pick an OPEN issue whose `area:` is yours: `is:open label:"area:<yours>"`.
2. First action: `CLAIM <slot> <provider> <UTC ISO-8601>`; re-read; if not first,
   `RELEASE <slot> conflict` and pick another. One issue per agent at a time.
3. Gate 0 prior-art search (GitHub code excluding adineo-cmd/*, web/XDA/LWN/
   HN/Reddit/arXiv, kernel source, linux-firmware). Record exact queries + date.
   Post `PRIOR-ART <urls>` → close as duplicate; or `DELTA <line>`; or
   `NO-PRIOR-ART <queries + date>`. No work before this comment.
4. Work under RULE 0/1, facts-not-blobs, clean-room, stdlib-only, `python3 -I`,
   no code comments, every number verified by command output.
5. Push (Rule 3); never force-push; never push `main` from a worker. Finish with
   `DONE <remote-sha> <result>`.

## Collision enforcement

- Deterministic partition (one owner per `area:`) is the primary guard.
- CLAIM is secondary; HANDOFF is the only transfer.
- `node src/scripts/check_claims.mjs` detects multiple claims / stray DONE.
- Two agents on one issue is always a violation, never collaboration.
