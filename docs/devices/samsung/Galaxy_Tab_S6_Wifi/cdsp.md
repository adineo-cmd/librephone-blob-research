# samsung Galaxy_Tab_S6_Wifi — `cdsp` family status (0 rows - honest negative; the #1126 identity correction applies)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1132](https://github.com/adineo-cmd/open-device/issues/1132)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 213d0b3), the identity correction in `docs/devices/samsung/Galaxy_Tab_S6_LTE/cdsp.md` (#1126), the [LineageOS wiki gta4xl page](https://wiki.lineageos.org/devices/gta4xl) (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `cdsp` family is structurally ABSENT - and the #1126 identity correction applies to this wifi sibling.** The DB name "Galaxy_Tab_S6_Wifi" is the same trap: codename `gta4xlwifi` + census path `samsung/gta4xlwifi/firmware/SM-P610` prove this is the **Galaxy Tab S6 Lite (Wifi), SM-P610, Exynos 9611** - no Qualcomm CDSP on this silicon. Additionally, the census has **no modem family at all** (wifi-only device, no modem.bin).

## Device identity

| fact | value | source |
|---|---|---|
| model | **Samsung Galaxy Tab S6 Lite (Wifi), SM-P610** - DB name "Tab_S6_Wifi" misleading | census path `samsung/gta4xlwifi/firmware/SM-P610` [F]; [LineageOS wiki gta4xl](https://wiki.lineageos.org/devices/gta4xl) (variants page, 2026-11-21) [F] |
| SoC | Samsung **Exynos 9611** (Mali-G72 MP3) - same SoC as SM-P615 (#1126) | spec pages (2026-11-21) [F]; inventory SoC cell empty, supplied here [F] |
| census scope | 38 rows in 2 families (boot 6, other 32); **no modem family** | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 cdsp rows; 0 cdsp-named tokens anywhere in the 38 rows [F].
- **No modem family**: the wifi-only variant ships no modem partition content, unlike the LTE sibling's modem.bin 43,332,816 B (#1126) [F].
- No gpu rows, no bootchain-grammar rows - the Exynos shape [F].

## Why structural absence [F]

The #1126 reasoning transfers directly: the Exynos 9611 has no Qualcomm CDSP - the cdsp grammar cannot exist on this silicon. Both Tab S6 Lite variants (SM-P615 LTE, SM-P610 wifi) are Exynos 9611 devices; both censuses show 0 cdsp rows, consistent with the samsung-slice-wide zero (#1030's full-samsung scan).

## Comparison with the LTE sibling (#1126) [F]

| aspect | Tab S6 Lite LTE (SM-P615, gta4xl) | Tab S6 Lite Wifi (SM-P610, gta4xlwifi) |
|---|---|---|
| rows / families | 49 / 3 (boot, modem, other) | 38 / 2 (boot, other) |
| modem family | modem.bin 43,332,816 + modem_debug 5,242,880 | **absent** |
| cdsp rows | 0 | 0 |

## Honest negatives

- The Exynos 9611's own DSP firmware location (vendor partitions, outside the DB's scope) is [OPEN] - same as #1126.
- modem.bin absence on the wifi variant is expected (wifi-only) but recorded as a census-shape fact rather than assumed. [F]

## What would upgrade this finding

1. Lead-level: the samsung name-vs-codename audit (#1126) covers both Tab S6 Lite variants and the wider samsung slice.
2. Payload fetch: SM-P610 vendor decomposition for the Exynos DSP images - [OPEN] as in #1126.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gta4xlwifi cdsp` / `SM-P610 Exynos 9611 cdsp` (web + GitHub code search, adineo-cmd/* excluded) -> LineageOS wiki + spec pages; the identity correction is #1126's, cited.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs and the verified wiki.
