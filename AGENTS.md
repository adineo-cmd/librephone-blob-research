# AGENTS.md — standing rules for every agent working in this repo

## ⚠️ RULE 0 — PARAMOUNT: ABSOLUTE UNIQUENESS (owner directive, never override)

**Everything produced here must be unique — no one may have done it before.
Never build anything that has already been built. Research it beforehand:
search the whole internet FIRST.**

Mandatory sequence for every task and finding:

1. **Search before building** — GitHub code search (excluding
   adineo-cmd/*), the wider web (XDA, Reddit, LWN, HN), arXiv/Scholar,
   linux-firmware/kernel trees (firmware coverage). Record exact query
   strings and dates in the deliverable.
2. **Prior art found → do not rebuild.** Find the genuinely new delta or
   pick a different target. Partial overlap is still overlap.
3. **Adversarial audit after** — a dedicated prior-art audit agent
   re-attacks every claim (run every ~10 findings or per session). A
   finding survives only if the auditor genuinely tried to break it.
4. **Corrections in place** — any finding that fails the audit is
   corrected where the original claim lives.

## Rule 1 — IMPROVE PREVIOUS WORK WHEN YOU FIND THE OPPORTUNITY (owner directive)

If during any task you notice something in the lab's prior work that can be
improved — a dangling reference, a stale number, a missing citation, an
uncorrected claim, a missing artifact, a broken link — **fix it in the same
session** (respecting file-walls: only files no other running agent owns).
Improvements are first-class deliverables: list them in your report with
before/after. The lab compounds: every session must leave the repos better
than it found them.

## Rule 2 — ISSUE CLAIMS ARE EXCLUSIVE (owner directive, 2026-11-19)

The repo's work is decomposed into GitHub work packages in `adineo-cmd/open-device`.
Every agent — opencode on key 1 or key 2, or zcode on any model — MUST claim an
issue before touching files for it. ONE ISSUE = ONE OWNER. NO EXCEPTIONS.

Before any file work, post the first comment on the issue:

```
CLAIM <agent-id> <provider> <UTC ISO-8601 timestamp>
```

Then RE-READ the comments. The FIRST valid claim wins. If yours is not first,
you MUST comment `RELEASE <agent-id> conflict` and STOP — do not work the issue.
One agent holds one issue at a time in this repository. A claim older than 48 h
with no `DONE` comment is stale; the first `STALE` comment releases it. After
pushing (Rule 3), finish with `DONE <remote-sha> <one-line result>`.

NO agent may work an issue already claimed by another agent — on any provider,
any model, or any harness. If you see a CLAIM comment that is not yours, leave
the issue alone, even if the other agent is idle or slow. A commit made without
a winning claim, or any work on a claimed issue by a second agent, is a protocol
violation. The lead verifies by reading issue comments and may revert or
reassign violating commits. Two agents on one issue is always a violation,
never a collaboration.

Claims have a race window, so ownership is also partitioned deterministically
by **issue number**, not by `area:` label:

```
shard(issue) = issue_number % 6
```

| shard | owner |
|---|---|
| 0 | OC-1 (opencode key 1) |
| 1 | OC-2 (opencode key 2) |
| 2 | OC-3 (opencode provider 3) |
| 3 | OC-4 (opencode provider 4) |
| 4 | ZC-1 (zcode GLM-5.3) |
| 5 | ZC-2 (zcode GLM-5.3) |

An agent may only start an open issue in its own shard. `area:` labels are
descriptive only and grant no ownership. Every shard carries the same mix of
firmware, blobs, SoC, driver, CPU/GPU, docs and clean-room work, so no provider
is left with only trivia and no provider owns an area exclusively.

The lead moves ownership with a single comment on #379:

```
SHARD-REASSIGN <shard> -> <slot>[,<slot>...]
```

That is the only way a shard changes hands; it needs no relabelling and no
per-issue edits. A claim has a 4-hour lease refreshed by any comment from the
claimant; an expired claim is revoked by the lead with
`REVOKE <slot> <issue#> <reason>` and the issue returns to its shard pool.

Full contract: `docs/ISSUE-ASSIGNMENT.md`.

## Rule 2a — REPO-STATE GATE BEFORE THE INTERNET

Before Gate 0, check whether this issue's deliverable already exists in THIS
repository at the current HEAD. Previous work is not prior art to be excluded;
it is the first thing to look for.

1. Record the HEAD SHA: `git rev-parse HEAD`. The per-family verdicts are in
   `docs/REPO-STATE-MAP.md`; start there.
2. Resolve the issue's deliverable path from its body. If the body has no
   explicit path, derive it from the title using the catalog conventions
   (`docs/devices/<vendor>/<device>/<family>.md`, `research/soc/<soc>-cpu.md`,
   `research/drivers/<family>.md`, `research/devices/<device>.md`,
   `implementations/<component>/`).
3. If the path exists and is substantive, post
   `ALREADY-DONE <path> <sha> <evidence>` and close the issue. Evidence is the
   test command and its result, or the committed analysis with its byte counts.
4. If the path exists but is a stub (for example a `leverage-families.md` that
   says "Deep-RE status: none yet"), post `STUB <path> <what is missing>` and
   scope the work to the missing part only. Never rebuild what exists.
5. If the path does not exist, post `NO-REPO-WORK <paths checked>` and continue
   to Gate 0.

A component with committed code and a passing self-test is done, even if its
`[OPEN]` register still lists semantic gaps; those gaps are separate issues,
not a reason to rewrite the component.

## Rule 2b — PRIOR-ART GATE BEFORE ANY WORK (owner directive, 2026-11-20)

Immediately after claiming an issue, and before touching any repository file,
the agent MUST search the whole internet for prior art and record the exact
query strings and access date as a comment on the issue:

1. GitHub code search, excluding `adineo-cmd/*`.
2. Web search: XDA, LWN, HN, Reddit, arXiv/Scholar, project and vendor docs.
3. Kernel source, linux-firmware, and the relevant upstream code trees.

Then post exactly one of:

- `PRIOR-ART <urls>` and **close the issue as a duplicate** if someone has
  already done the work. Do not rebuild it. Record what the prior art covers.
- `DELTA <one-line>` if only partial overlap exists — state the precise new
  contribution before starting.
- `NO-PRIOR-ART <queries + date>` if nothing was found, then proceed.

No work or commit may begin before one of these three comments exists. An
agent that finds existing prior art and keeps the issue open is in violation.
This gate is the cheapest way to spend the free tokens on genuinely new work.

## Rule 3 — PUSH EVERYTHING WHEN DONE (owner directive, 2026-11-19)

Once an issue is verified and the `DONE` comment is posted, push the work.
Do not leave completed work sitting only in a local commit.

- Fetch and rebase onto the current remote tip before pushing. Never force-push.
- Push every local commit that belongs to the claimed issue. Do not push commits
  claimed by another agent or work from an unclaimed issue.
- The `feat/open-device-site` branch is the integration branch. Push there;
  never push directly to `main`.
- If a push is rejected, fetch, rebase, re-run the verification commands, and
  push again. Report the final remote SHA in the `DONE` comment.
- A completed issue with no corresponding remote commit is not done.

This supersedes the earlier "commit locally, the lead pushes" rule. That rule is
retained only for the merge tracked by issue #143, which the owner paused.

## Fleet rules

- Two agents run concurrently (account cap = 2; a third launch is
  rejected — queue and resume via SendMessage when a slot frees).
- File-wall isolation: agents push ONLY their own directories; shared
  files are edited by the lead when merging agent reports.
- Pushes go through the GitHub MCP (push_files); verify large files
  byte-for-byte after push.
- The account cap is per harness. The issue-claim rule (Rule 2) is what
  prevents two harnesses from colliding; file walls alone do not.

## Repo principles (unchanged — see README.md)

Facts, not blobs · clean-room discipline · negative results are results ·
everything reproducible · contribute upstream · MediaTek + Qualcomm fronts.
