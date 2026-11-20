# Agent assignment — 6 providers, sharded by issue, equal depth for all

Six agents work `adineo-cmd/open-device`. Ownership is decided by **issue
number**, not by `area:` label. This gives every provider an equal mix of deep
firmware, blobs, SoC, driver, CPU/GPU and clean-room work, and lets any shard
be handed to another provider in one command if a provider goes offline.

## The shard rule

```
shard(issue) = issue_number % 6
```

| shard | owner | provider |
|---|---|---|
| 0 | **OC-1** | opencode key 1 |
| 1 | **OC-2** | opencode key 2 |
| 2 | **OC-3** | opencode provider 3 |
| 3 | **OC-4** | opencode provider 4 |
| 4 | **ZC-1** | zcode GLM-5.3 |
| 5 | **ZC-2** | zcode GLM-5.3 |

An agent may only start an open issue whose number maps to its own shard, or to
a shard that has been explicitly reassigned to it (see Failover).

`area:` labels are **descriptive only** — they say what kind of work an issue
is (firmware, blobs, drivers, soc, cpu, gpu, docs, site, repo, tools,
historic, upstream, triage). They no longer grant ownership. This is the change
that lets every provider touch every kind of work.

## Measured balance (live, 690 open issues at 2026-11-20T07:22Z)

| shard | issues | firmware | drivers | cpu | soc | tools | blobs |
|---|---|---|---|---|---|---|---|
| 0 | 116 | 95 | 7 | 4 | 4 | 4 | 2 |
| 1 | 115 | 92 | 7 | 4 | 4 | 4 | 2 |
| 2 | 116 | 93 | 7 | 4 | 6 | 3 | 2 |
| 3 | 113 | 92 | 7 | 5 | 5 | 3 | 1 |
| 4 | 115 | 93 | 7 | 5 | 5 | 3 | 2 |
| 5 | 115 | 93 | 7 | 5 | 5 | 4 | 1 |

Spread is 113–116 issues per shard (2.6%), and the area mix inside each shard is
the same. As the remaining catalog publishes, each shard continues to receive
its proportional share of every area, including gpu, docs, site and triage.

## Why shard instead of area

| failure | area partition | shard partition |
|---|---|---|
| Provider goes offline | its whole area stalls; other providers cannot touch it | only ~1/6 of each area stalls; lead reassigns the shard in one comment |
| Provider finishes early | cannot help other areas without a handoff per issue | lead moves one shard, or the provider takes an unowned shard |
| Provider reassigned to another task | an entire area sits idle | the shard moves with the provider |
| Strong model on trivial work | possible | impossible — every shard is a mix of deep and quick |
| Collision | area prevents it | shard prevents it deterministically |

## Failover — one command, no relabelling

The lead posts on the START HERE issue (#379):

```
SHARD-REASSIGN 4 -> OC-2,OC-3
```

From that comment onward, OC-2 and OC-3 may work shard 4 issues as well as
their own. Nothing else changes: no issue edits, no label churn, no new files.
To undo it:

```
SHARD-REASSIGN 4 -> ZC-1
```

The active reassignment table is whatever the latest `SHARD-REASSIGN` line for
each shard says. `node src/scripts/check_claims.mjs` reads #379 and enforces it.

## Claim lease — a crashed agent cannot hold work forever

`CLAIM <slot> <provider> <UTC ISO-8601>` starts a **4-hour lease**, refreshed by
any later comment from the same claimant on that issue (`WIP`, `PUSH`, `DELTA`,
`NO-PRIOR-ART`). If the lease expires:

- the issue returns to its shard pool automatically;
- the lead posts `REVOKE <slot> <issue#> <reason>`;
- any eligible agent may then claim it normally.

This is the second half of the offline problem: a provider that dies mid-issue
does not leave that issue frozen.

## Procedure (every agent, every issue)

1. **Pick**: open issue, `state=open`, `number % 6` equals your shard (or a
   reassigned shard). Ignore every other issue.
2. **Claim first**: post `CLAIM <slot> <provider> <UTC ISO-8601>` before reading
   files. Re-read the comments.
   - If another valid claim is first: post `RELEASE <slot> conflict`, pick
     another issue, never work this one.
3. **Gate -1 — repo state (mandatory, before the internet)**: record
   `git rev-parse HEAD`, resolve the deliverable path, and check it. Exists and
   substantive → `ALREADY-DONE <path> <sha> <evidence>` and close. Exists as a
   stub → `STUB <path> <what is missing>` and do only the missing part. Does
   not exist → `NO-REPO-WORK <paths checked>`. Never rebuild committed work.
4. **Gate 0 — prior art (mandatory, before any work)**: search GitHub code
   (excluding `adineo-cmd/*`), the web (XDA, LWN, HN, Reddit, arXiv/Scholar),
   kernel source and linux-firmware. Record exact queries and date. Then post
   exactly one of:
   - `PRIOR-ART <urls>` → **close the issue as duplicate**, do not rebuild;
   - `DELTA <one line>` → partial overlap, state the new contribution;
   - `NO-PRIOR-ART <queries + date>` → proceed.
5. **Work** under RULE 0/1, facts-not-blobs, clean-room, stdlib-only,
   `python3 -I`, no code comments, every number verified by command output.
6. **Push** (Rule 3) to `feat/open-device-site`; never force-push; never push
   `main` from a worker. Post `WIP <slot> <remote-sha>` after each push.
7. **Finish** with `DONE <slot> <remote-sha> <one-line result>`.

## Enforcement

- **Shard is the primary guard** — deterministic, no race, machine-checkable.
- **CLAIM is the secondary guard** — first comment wins inside a shard.
- **SHARD-REASSIGN is the only way ownership moves**, and only the lead posts it.
- `node src/scripts/check_claims.mjs` fails on: a claim outside the claimant's
  shard, two claims on one issue, a DONE from a non-claimant, and reports stale
  leases.
- Two agents on one issue is always a violation, never collaboration.
