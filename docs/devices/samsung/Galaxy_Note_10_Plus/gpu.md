# samsung Galaxy_Note_10_Plus — `gpu` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1054](https://github.com/adineo-cmd/open-device/issues/1054)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site a2f6759), the proven samsung-slice split in `docs/devices/samsung/Galaxy_Note_10/gpu.md` (#1036), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `gpu` family (Adreno firmware grammar) is structurally ABSENT on Galaxy_Note_10_Plus - not a census gap.** The device is Exynos 9825 (SM-N975F, codename `d2s`) with a Mali-G76 MP12 GPU; 0 of its 67 census rows match the gpu grammar, and it sits on the Exynos side of the samsung-slice split proven in #1036 (6 Snapdragon-sourced samsung devices carry all 23 gpu rows; all 11 Exynos-sourced ones carry zero).

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Note 10+ (SM-N975F); codename `d2s` | `device-inventory.csv` (`build_codename=d2s`) [F] |
| SoC | Samsung **Exynos 9825**; GPU **Mali-G76 MP12** | public spec pages (2026-11-21) [F]; #1030 identity table (family SoC) [F] |
| census scope | 67 rows in 3 families (other 58, boot 7, modem 2) | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 of 67 rows match the gpu grammar (`gmu/sqe/zap/aNNN_*`); the tz-grammar scan is also 0 (this device's tz status is the #1048-class honest negative) [F].
- Census paths are the Samsung shape: `samsung/d2s/firmware/SM-N975F` (BL files), `samsung/d2s/radio`, `samsung/d2s/vendor/etc`, `samsung/d2s/vendor/firmware(+nfc)` [F].

## The #1036 split, applied [F]

The samsung slice's gpu rows map exactly to Snapdragon-sourced hardware: Galaxy_A71 (SD730 -> a618/a630 set), Galaxy_S20_FE (SD865 -> a650 set), Galaxy_Tab_A7 LTE/Wifi (7 rows each), Galaxy_Tab_S7 LTE/Wifi (a650 set) - 6 devices, 23 rows. Every Exynos-sourced samsung device - Note_10 (d1), Note_10_5G (d1x), **Note_10_Plus (d2s)**, S10 family, F62, A21S, Tab_S6 family - carries zero. Note_10_Plus's Mali-G76 MP12 has no Adreno-style userspace firmware blobs; the Mali stack lives in the vendor-blob driver partitions outside this census ([I] from public ARM/kernel knowledge; carrier question [OPEN]).

## Honest negatives

- The Mali carrier question (no loadable firmware for G76-class Mali per public kernel sources) is [I], not payload-verified for this device. [OPEN]
- The Snapdragon Note10+ 5G (SM-N976, SD855) is a different hardware identity not in this DB; if it joined, it would carry a660-class rows - a census-scope note, not an absence on hardware. [OPEN]

## What would upgrade this finding

1. Nothing payload-side needed - the absence is structural; the #1036 lead-level SoC audit would formalize the 6-vs-11 split.
2. A positive control (any Snapdragon samsung device joining the census) would close the loop.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy Note 10 Plus Exynos Mali gpu firmware` (web + GitHub code search, adineo-cmd/* excluded) -> spec pages only; the samsung gpu-row split is #1036's, cited.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
