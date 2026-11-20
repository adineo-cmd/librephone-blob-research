# Issue workflow — claim, partition, finish

The lab's work is decomposed into atomic GitHub issues on
`adineo-cmd/librephone-blob-research`. This file is the contract every agent
reads before starting, on opencode or zcode, on any provider key.

## 1. Pick by partition, not by interest

Each harness owns a disjoint set of `area:` labels. Work only your own labels.

| harness | owns `area:` labels |
|---|---|
| opencode key 1 (`100milionseek`) | `firmware`, `historic` |
| opencode key 2 (`100milionseek-2`) | `soc`, `upstream`, `cpu`, `gpu`, `drivers`, `blobs` |
| zcode | `docs`, `site`, `repo`, `tools` |

This partition is the primary collision guard. Free-token providers can run at
full concurrency without two harnesses reaching for the same issue.

## 2. Claim before touching files

Post the first comment on the issue:

```
CLAIM <agent-id> <provider> <UTC ISO-8601 timestamp>
```

Re-read the comments. The first valid claim wins. If yours is not first:

```
RELEASE <agent-id> conflict
```

Then pick another issue. One agent holds one issue at a time in this repo.

## 3. Work under the standing rules

- RULE 0: search first, record exact queries and dates. Prior art means find
  the delta or pick a different target.
- RULE 1: fix stale counts, dangling references and broken links in the same
  session, respecting file walls; list before/after.
- Facts-not-blobs: no proprietary payload is ever committed.
- Python is standard library only, run with `python3 -I`, no comments in code.
- Every number is verified by command output before it is written.
- Honest negatives are deliverables. Report them, do not omit them.
- Push everything when done (Rule 3). Fetch and rebase first, never force-push,
  push the `feat/open-device-site` branch rather than `main`, and report the
  final remote SHA in the `DONE` comment. A finished issue with no remote commit
  is not done. Exception: issue #143 (the owner-paused merge) stays local.

## 4. Finish and push

Verify, commit, fetch, rebase, push every commit that belongs to this issue to
`feat/open-device-site`, then post:

```
DONE <remote-sha> <one-line result>
```

Reference the issue number in the commit message. A completed issue with no
matching remote commit is not done. A claim older than 24 hours with no `DONE`
comment is stale; the first `STALE` comment releases it.

## 5. Lead verification

The lead checks the first `CLAIM` comment on each issue against the commit's
issue reference. Commits made without a winning claim are protocol violations
and may be reassigned or reverted.
