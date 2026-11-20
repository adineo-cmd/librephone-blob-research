# Agent assignment — 6 providers, disjoint areas

Six agents will work `adineo-cmd/open-device`. Collision prevention is
**deterministic**: every `area:` label has exactly one owner. No two agents may
work the same issue, on any provider or harness.

## The six slots

| slot | harness / provider | owns `area:` labels | work |
|---|---|---|---|
| **OC-1** | opencode — 100milionseek key 1 | `firmware` | Per-device firmware family docs, IoT/parts, fleet RE |
| **OC-2** | opencode — 100milionseek key 2 | `soc`, `upstream` | SoC/CPU/GPU packages, upstream filings, PR work |
| **OC-3** | opencode — provider 3 | `cpu`, `gpu` | CPU core ID + GPU core ID per SoC |
| **OC-4** | opencode — provider 4 | `drivers`, `blobs` | Driver-interface mapping + proprietary blob specs |
| **ZC-1** | zcode — provider 1 | `docs`, `site` | Document verification, website, Astro build |
| **ZC-2** | zcode — provider 2 | `historic`, `repo`, `tools` | Historic devices, repo upkeep, clean-room implementations |

Note: `historic` and `blobs` are assigned to exactly one slot each; there is no
overlap. If your actual provider names differ, keep the **area → slot** mapping
above and substitute the provider names in the right column.

## What each agent does, in order

1. **Pick an OPEN issue whose `area:` label is yours.** Use the GitHub label
   filter: `is:open label:"area:<your-area>"`.
2. **Post the claim as the FIRST action**, before reading files:
   `CLAIM <slot-id> <provider> <UTC ISO-8601 timestamp>`
   e.g. `CLAIM OC-1 100milionseek 2026-11-20T08:00:00Z`
3. **Re-read the comments.** If a `CLAIM` already exists and it is not yours,
   post `RELEASE <slot-id> conflict` and pick another issue. Never work it.
4. **Gate 0 — prior art (mandatory, before any work).** Search GitHub code
   (excluding `adineo-cmd/*`), the web (XDA/LWN/HN/Reddit/arXiv), kernel source
   and linux-firmware. Record the exact queries and date. Then post one of:
   - `PRIOR-ART <urls>` → **close the issue as a duplicate**, do not rebuild;
   - `DELTA <one-line>` → partial overlap, state the new contribution;
   - `NO-PRIOR-ART <queries + date>` → proceed.
5. **Do the work** under RULE 0/1, facts-not-blobs, clean-room, stdlib-only,
   `-I`, no code comments, every number verified by command output.
6. **Push everything (Rule 3)** to `feat/open-device-site`, never force-push,
   never push `main` from a worker. Finish with
   `DONE <remote-sha> <one-line result>`.

## Ownership rules

- One agent holds one issue at a time. Two agents on one issue is always a
  violation, never collaboration.
- Do not touch an issue whose area is not yours, even if you are idle.
- Do not work an issue with a CLAIM comment from another slot.
- The lead runs `node src/scripts/check_claims.mjs` before merging; violations
  are reverted or reassigned.

## Lead verification

Before launching a full wave, confirm each slot is idle/current, then assign
issues strictly by the table. When the 1,239-issue publish completes, every open
issue will carry one of the 12 `area:` labels and therefore exactly one owner.
