# samsung Galaxy_S10_5G — `gpu` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1072](https://github.com/adineo-cmd/open-device/issues/1072)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 33b4a80), the proven samsung-slice split in `docs/devices/samsung/Galaxy_Note_10/gpu.md` (#1036), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `gpu` family (Adreno firmware grammar) is structurally ABSENT on Galaxy_S10_5G - not a census gap.** The device is Exynos 9820 (SM-G977B/SM-G977N, codename `beyondx`) with a Mali-G76 MP12 GPU; 0 of its 73 census rows match the gpu grammar, and it sits on the Exynos side of the samsung-slice split proven in #1036.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S10 5G (SM-G977B international / SM-G977N Korea); codename `beyondx` | `device-inventory.csv` [F]; census paths carry **both** model firmware dirs (SM-G977B + SM-G977N) [F] |
| SoC | Samsung **Exynos 9820**; GPU **Mali-G76 MP12** | public spec pages (2026-11-21) [F]; same SoC as Galaxy_S10 (#1066) [F] |
| census scope | 73 rows in 4 families (boot 7, modem 8, other 57, wifi 1); 423,025,895 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 of 73 rows match the gpu grammar (`gmu/sqe/zap/aNNN_*`) [F].
- The census is dual-model: two BL firmware dirs (`SM-G977B`, `SM-G977N`) plus the shared radio/vendor paths [F] - the S10 5G shipped both variants under one codename.
- No gpu-grammar tokens anywhere in the census (checked gmu/sqe/zap/mali/kgsl scans) [F].

## The #1036 split, applied [F]

Samsung devices with gpu rows: exactly the 6 Snapdragon-sourced ones (Galaxy_A71, Galaxy_S20_FE, Galaxy_Tab_A7 LTE/Wifi, Galaxy_Tab_S7 LTE/Wifi - 23 rows, all Adreno builds). Every Exynos-sourced samsung device - **beyondx included** - carries zero. Mali-G76 MP12 has no Adreno-style userspace firmware blobs; the Mali stack lives in the vendor-blob driver partitions outside this census ([I] from public ARM/kernel knowledge; carrier question [OPEN]).

## Honest negatives

- The Mali carrier question is [I] from public kernel sources, not payload-verified for beyondx. [OPEN]
- Whether the SM-G977B and SM-G977N firmware dirs carry different modem/BT builds (the dual-model census split) is a census-shape fact outside this family's scope. [OPEN]

## What would upgrade this finding

1. Nothing payload-side needed - the absence is structural (#1036's split).
2. The dual-model census shape (two firmware dirs under one device row) is worth a lead-level look for census deduplication policy, as with A21S's duplicated rows (#1006).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S10 5G Exynos Mali gpu firmware` (web + GitHub code search, adineo-cmd/* excluded) -> spec pages only; the samsung gpu-row split is #1036's, cited.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
