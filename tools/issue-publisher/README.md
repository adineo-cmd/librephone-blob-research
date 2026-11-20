# Issue publisher

Publishes the committed issue catalogs to `adineo-cmd/open-device`.

## Files

- `../../docs/issue-catalog/full-coverage.jsonl` — 1,239 full-coverage issues
  (the authoritative catalog; every device x firmware family, parts, CPU/GPU,
  drivers, blob specs, open-source implementations).
- `../../docs/issue-catalog/device-packages.jsonl` — 276 device work packages.
- `../../docs/issue-catalog/coverage-packages.jsonl` — 50 SoC/clean-room/
  link-maintenance packages.
- `../../docs/issue-catalog/issues.jsonl` — the original 2,836 micro-issues
  (superseded; kept for provenance).

## Usage

```
python3 -I resume_full.py          # publish missing issues, resumable
bash keep_publishing.sh            # auto-restart until all 1,239 exist
python3 -I ../../src/scripts/check_claims.mjs   # not Python; node instead
```

`resume_full.py` derives the already-published set from GitHub by title, so it
is safe against loss of the local state file. It respects GitHub's 500/hour
content-creation limit with a 430/hour window cap and 8-second pacing.

`full-published.jsonl` and `full-publish.log` are runtime state and are
gitignored.
