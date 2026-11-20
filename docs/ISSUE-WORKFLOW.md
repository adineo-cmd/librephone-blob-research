# Issue workflow — claim, partition, finish

The lab's work is decomposed into atomic GitHub issues on
`adineo-cmd/open-device`. This file is the contract every agent
reads before starting, on opencode or zcode, on any provider key.

## 1. Pick by shard, not by interest

Ownership is decided by issue number:

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

Work only issues in your shard. `area:` labels describe the kind of work and
grant no ownership. Each shard holds the same proportion of every area, so all
providers get equally deep work.

The lead reassigns a shard with one comment on #379:

```
SHARD-REASSIGN <shard> -> <slot>[,<slot>...]
```

Nothing else is needed — no relabelling, no per-issue edits. This is how the
fleet survives a provider going offline or being moved to another task.

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

## 2a. Check the repo before the internet

Previous work is not prior art to exclude; it is the first place to look.

1. Record `git rev-parse HEAD`. The per-family verdicts are in
   `docs/REPO-STATE-MAP.md`; start there.
2. Resolve the deliverable path from the issue body, or derive it from the
   title conventions (`docs/devices/<vendor>/<device>/<family>.md`,
   `research/soc/<soc>-cpu.md`, `research/drivers/<family>.md`,
   `research/devices/<device>.md`, `implementations/<component>/`).
3. If it exists and is substantive, post `ALREADY-DONE <path> <sha> <evidence>`
   and close the issue.
4. If it exists as a stub, post `STUB <path> <what is missing>` and do only the
   missing part.
5. If it does not exist, post `NO-REPO-WORK <paths checked>` and go to Gate 0.

A component with committed code and a passing self-test is done; its `[OPEN]`
register lists separate future work, not a reason to rewrite it.

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
