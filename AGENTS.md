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

The repo's work is decomposed into atomic GitHub issues in
`adineo-cmd/librephone-blob-research`. Every agent — opencode on key 1 or key 2,
or zcode on any model — MUST claim an issue before touching files for it.

Before any file work, post the first comment on the issue:

```
CLAIM <agent-id> <provider> <UTC ISO-8601 timestamp>
```

Then re-read the comments. The FIRST valid claim wins. If yours is not first,
comment `RELEASE <agent-id> conflict` and pick another issue. One agent holds
one issue at a time in this repository. A claim older than 24 h with no `DONE`
comment is stale; the first `STALE` comment releases it. Finish with
`DONE <commit-sha> <one-line result>`.

No agent may work an issue claimed by another agent, on any provider or in any
harness. A commit made without a winning claim is a protocol violation. The
lead verifies by reading issue comments and may reassign violating commits.

Claims have a race window, so work is also partitioned by label. An agent may
only start issues whose `area:` label is assigned to its harness:

| harness | owns `area:` labels |
|---|---|
| opencode key 1 (`100milionseek`) | `firmware`, `historic` |
| opencode key 2 (`100milionseek-2`) | `soc`, `upstream` |
| zcode | `docs`, `site`, `blobs`, `repo`, `tools` |

The partition is the primary guard; the `CLAIM` comment is the secondary one.
If a partition owner is idle, it may take from another partition only after
claiming that issue and confirming no competing claim exists.

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
