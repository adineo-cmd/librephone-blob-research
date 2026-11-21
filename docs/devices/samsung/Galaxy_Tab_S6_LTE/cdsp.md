# samsung Galaxy_Tab_S6_LTE — `cdsp` family status (0 rows - honest negative, plus an identity correction)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1126](https://github.com/adineo-cmd/open-device/issues/1126)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 416d7ac), the [LineageOS wiki gta4xl page](https://wiki.lineageos.org/devices/gta4xl) (2026-11-21), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `cdsp` family (Qualcomm compute-DSP grammar) is structurally ABSENT - and the device's identity needed correcting first.** The DB name "Galaxy_Tab_S6_LTE" suggests the 2019 Snapdragon-855 Tab S6 LTE, but the codename (`gta4xl`), the census paths (`samsung/gta4xl/firmware/SM-P615`), and the [LineageOS wiki](https://wiki.lineageos.org/devices/gta4xl) prove this device is the **Galaxy Tab S6 Lite (LTE), SM-P615, Samsung Exynos 9611** (Mali-G72 MP3). Exynos 9611 has no Qualcomm CDSP at all - the 0-row census is structural, the #1030-class honest negative.

## Device identity

| fact | value | source |
|---|---|---|
| model | **Samsung Galaxy Tab S6 Lite (LTE), SM-P615** - the DB name "Galaxy_Tab_S6_LTE" is misleading | census paths `samsung/gta4xl/firmware/SM-P615` [F]; [LineageOS wiki gta4xl](https://wiki.lineageos.org/devices/gta4xl) (2026-11-21) [F] |
| SoC | Samsung **Exynos 9611** (4x A73 + 4x A53; Mali-G72 MP3); released 2020-04-02 | LineageOS wiki + spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** - supplied here [F] |
| census scope | 49 rows in 3 families (other 41, boot 6, modem 2); 292,501,472 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 cdsp rows; 0 cdsp-named tokens anywhere in the 49 rows [F].
- The modem family is 2 rows: **modem.bin 43,332,816 B** + modem_debug.bin 5,242,880 B at `samsung/gta4xl/firmware/SM-P615` - the Exynos 9611's own modem, not a Qualcomm PIL image set [F].
- No gpu rows, no bootchain-grammar rows - the Exynos shape throughout (#1030/#1036 method) [F].

## Why structural absence [F]

1. **Silicon**: the Exynos 9611 contains Samsung's own DSP/IP blocks; there is no Qualcomm CDSP on this silicon - the cdsp grammar (cdsp.mdt/bXX, PAS-loaded) cannot exist here [F - grammar is Qualcomm-specific per the repo's taxonomy].
2. **The identity trap resolved**: had this device actually been the 2019 Tab S6 LTE (SM-T865, SD855/Adreno 640), a cdsp census gap would have been the verdict (the #1108/#1096 class - mainline sm8150.dtsi carries `remoteproc_cdsp` at line 3366). The codename + census paths settle it as Exynos 9611.
3. **The samsung-slice consistency**: 0 cdsp rows across all 17 samsung devices (the full-samsung scan from #1030 shows no cdsp rows on any vendor-mix) - consistent with the census's Samsung scope being Exynos-heavy plus the SM8250 r8q case (#1096) where the DSP is inside the modem image [F].

## Honest negatives

- The Exynos 9611's own DSP firmware (Samsung's audio/vision DSP images) lives inside the vendor partitions and is outside this DB's blob census scope - [OPEN] (same `/vendor` scope limitation as #1030's TEE carriers).
- modem.bin (43,332,816 B) internal structure is undecoded - [OPEN] (payload-gated).

## What would upgrade this finding

1. Lead-level: an identity audit of samsung device names vs codenames (Tab_S6_LTE -> Tab S6 Lite LTE is the second samsung naming trap after the #934/#946 SoC-cell errors).
2. Payload fetch: decompose SM-P615's modem.bin - the first Exynos 9611 modem record.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gta4xl cdsp firmware` / `SM-P615 Exynos 9611 cdsp` (web + GitHub code search, adineo-cmd/* excluded) -> LineageOS wiki + spec pages; mainline sm8150.dtsi fetched 2026-11-21 for the counterfactual check. Nobody documents the identity trap or the cdsp absence.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs and the verified wiki.
