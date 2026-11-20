# samsung Galaxy_Note_10 — `gpu` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1036](https://github.com/adineo-cmd/open-device/issues/1036)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 6cd9500), the LineageOS `android_device_motorola_d1` tree (fetched 2026-11-20 for #922 - d1 = SM-N970F Note 10), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `gpu` family (Adreno firmware grammar) is structurally ABSENT on Galaxy_Note_10 - not a census gap.** The device is Exynos 9825 with a Mali-G76 MP12 GPU: Mali GPUs of this generation carry no Adreno-style firmware blobs (GMU/SQE/zap). The samsung slice itself proves the split: the only samsung devices with gpu rows are the Snapdragon-sourced ones (6 devices), while every Exynos-sourced samsung device (11 devices, Note_10 included) carries zero.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Note 10 (SM-N970F); codename `d1` | `device-inventory.csv` [F]; LineageOS `android_device_motorola_d1` tree header `Firmware for model SM-N970F` (fetched 2026-11-20 for #922) [F] |
| SoC | Samsung **Exynos 9825**; GPU **Mali-G76 MP12** | public spec pages (2026-11-21) [F]; #1030 identity table (same SoC as Galaxy_F62) [F] |
| census scope | 67 rows in 3 families (other 58, boot 7, modem 2) | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 of 67 rows match the gpu grammar (`gmu/sqe/zap/aNNN_*`, per `research/soc/per-soc-method-plans.md`); no filename in the census contains gpu-grammar tokens (checked `mali|gpu|kgsl|gmu|sqe|zap` substring scans) [F].
- The census paths are the Samsung shape: `samsung/d1/firmware/SM-N970F` (BL files incl. sboot.bin 4,194,304 B), `samsung/d1/radio`, `samsung/d1/vendor/etc`, `samsung/d1/vendor/firmware(+nfc)` [F].

## The samsung-slice split that proves structure [F]

| samsung device | SoC class | gpu rows |
|---|---|---|
| Galaxy_A71 | Snapdragon 730 (Adreno 618) | 3 (a618_gmu, a630_gmu, a630_sqe - #1018) |
| Galaxy_S20_FE | Snapdragon 865 (Adreno 650) | 2 (a650_gmu, a650_sqe) |
| Galaxy_Tab_A7_LTE / Wifi | Snapdragon-class | 7 each (a620_zap, a630_sqe, a650_gmu/sqe/zap, a702_sqe/zap) |
| Galaxy_Tab_S7_LTE / Wifi | Snapdragon 865+ (Adreno 650) | 2 each (a650_gmu, a650_sqe) |
| Galaxy_Note_10, Note_10_5G, Note_10_Plus, S10 family, F62, A21S, Tab_S6 family | **Exynos** (Mali GPUs) | **0** |

The grammar appears on samsung devices **only** where the SoC is a Snapdragon: 6 devices carry 23 gpu rows total, all Adreno builds; the 11 Exynos devices carry zero. Note_10's absence is the Exynos side of that exact line - its Mali-G76 MP12 has no Adreno-style userspace firmware (Mali kernel drivers of this generation load no GMU/SQE blobs; public ARM/kernel knowledge [I, labeled]).

## Interface facts

- Mali-G76 userspace is the binary-blob driver inside vendor/system partitions, not a firmware file family this DB censuses - the gpu family grammar simply has no Exynos counterpart [F - zero rows; carrier question [OPEN]].
- Evidence class: P3 metadata-only [F].

## Honest negatives

- Whether Note_10's Mali stack involves any loadable firmware at all (it does not, for G76-class Mali per public kernel sources, but this is [I] from public knowledge, not payload-verified for this device) - [OPEN].
- Note_10 5G's SM-N971N/Exynos variant shares the profile; its census (50 tz rows under #940-class analysis) carries no gpu rows either [F].
- The Snapdragon Note10+ 5G (SM-N976, SD855) exists publicly but is not this DB's Note_10 identity; if it entered the corpus it would carry a660-class rows (its absence here is a census-scope fact, not an absence on hardware). [OPEN]

## What would upgrade this finding

1. Nothing payload-side is needed to strengthen the absence - it is structural. A samsung-slice SoC audit (like #934/#946's corrections) would firm the 6-vs-11 device split into a lead-level table.
2. If a Snapdragon Note10+ 5G ever joins the census, its a660 rows would be the positive control.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy Note 10 Exynos 9825 Mali G76 gpu firmware` (web + GitHub code search, adineo-cmd/* excluded) -> spec pages only. Nobody documents the Note_10 gpu absence or the samsung gpu-row split.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
