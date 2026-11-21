# samsung Galaxy_S10e — `gpu` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1090](https://github.com/adineo-cmd/open-device/issues/1090)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 78f2e5e), the proven samsung-slice split in `docs/devices/samsung/Galaxy_Note_10/gpu.md` (#1036), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `gpu` family (Adreno firmware grammar) is structurally ABSENT on Galaxy_S10e - not a census gap.** The device is Exynos 9820 (SM-G970F/SM-G970N, codename `beyond0lte`) with a Mali-G76 MP11 GPU; 0 of its 69 census rows match the gpu grammar, and it sits on the Exynos side of the samsung-slice split proven in #1036.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S10e (SM-G970F international / SM-G970N Korea); codename `beyond0lte` | `device-inventory.csv` [F]; census paths carry both model firmware dirs [F] |
| SoC | Samsung **Exynos 9820**; GPU **Mali-G76 MP11** (two fewer cores than the S10/Plus MP12) | public spec pages (2026-11-21) [F] |
| census scope | 69 rows in 4 families (boot 7, other 57, modem 4, wifi 1) | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 of 69 rows match the gpu grammar (`gmu/sqe/zap/aNNN_*`) [F].
- The census is dual-model: `samsung/beyond0lte/firmware/SM-G970F` + `SM-G970N` dirs plus the shared radio/vendor paths - the same dual-model shape as beyondx (#1072) [F].
- No gpu-grammar tokens anywhere in the census [F].

## The #1036 split, applied [F]

Samsung devices with gpu rows: exactly the 6 Snapdragon-sourced ones (23 rows, all Adreno builds - #1036's table). Every Exynos-sourced samsung device - **beyond0lte included** - carries zero. Mali-G76 MP11 has no Adreno-style userspace firmware blobs; the Mali stack lives in the vendor-blob driver partitions outside this census ([I] from public ARM/kernel knowledge; carrier question [OPEN]).

## Honest negatives

- The Mali carrier question is [I] from public kernel sources, not payload-verified for beyond0lte. [OPEN]
- The dual-model census shape (SM-G970F + SM-G970N dirs under one device row) joins the beyondx and A21S census-shape notes for lead-level deduplication policy. [OPEN]

## What would upgrade this finding

1. Nothing payload-side needed - the absence is structural (#1036's split).
2. The dual-model census deduplication policy (beyond0lte, beyondx, A21S-class) is a lead-level item spanning several devices.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S10e Exynos Mali gpu firmware` (web + GitHub code search, adineo-cmd/* excluded) -> spec pages only; the samsung gpu-row split is #1036's, cited.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
