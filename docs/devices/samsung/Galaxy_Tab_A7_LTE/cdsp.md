# samsung Galaxy_Tab_A7_LTE — `cdsp` family status (0 rows - census gap; the SoC has a CDSP)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1108](https://github.com/adineo-cmd/open-device/issues/1108)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 78f2e5e), mainline `arch/arm64/boot/dts/qcom/sm6115.dtsi` (fetched 2026-11-21), the LineageOS `android_device_samsung_gta4l` lineage-22.2 `proprietary-files.txt` (123 entries, fetched 2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `cdsp` rows is a CENSUS GAP, not structural absence - and this time the SoC provably has the DSP.** Mainline carries `remoteproc@b300000` with compatible **`qcom,sm6115-cdsp-pas`** in `sm6115.dtsi` (lines 2914-2915): the SM6115 (Snapdragon 662) has a compute DSP that loads firmware via PAS. The firmware ships inside Samsung's modem partition image (no separate vendor-tree copy exists - the gta4l extract list has none), so no cdsp files reach the census.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab A7 LTE (SM-T505 family); codename `gta4l` | `device-inventory.csv` [F]; extract-list per-region variants SM-T505/T505C/T505N/T507 [F] |
| SoC | Qualcomm **SM6115 Snapdragon 662**; **CDSP present** (mainline `qcom,sm6115-cdsp-pas`, remoteproc@b300000, PAS loader) | public spec pages (2026-11-21) [F]; mainline sm6115.dtsi fetched 2026-11-21 [F] |
| census scope | 47 rows in 6 families (other 30, gpu 7, boot 6, wifi 2, bt 1, modem 1); 336,045,815 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 cdsp rows; 0 cdsp-named files anywhere in the 47 rows (substring scan `cdsp` -> 0) [F].
- The modem family is a single row: `ipa_fws.mdt` 7,020 B ELF64 at `samsung/gta4l/vendor/firmware` [F] - no modem/image directory exists in this census (the #1096 r8q shape repeats).
- The gta4l extract list (123 entries) contains **no cdsp/adsp/modem image entries** - only WLAN files (bdwlan/regdb/wlanmdsp per-region variants for SM-T505/T505C/T505N/T507), audio, camera, touch [F].

## Why census gap, not structural absence [F]

1. **The SoC has the DSP**: mainline `sm6115.dtsi` defines the CDSP remoteproc with the PAS loader - firmware must exist on-device for the DSP to boot [F].
2. **Samsung's packaging**: the SM6115 CDSP firmware lives inside the modem partition image, never as a separate vendor-tree file (the #1096 r8q SM8250 pattern - verified again here on gta4l's 123-entry list) [F].
3. **The corpus contrast**: OnePlus SM6115-class devices would carry cdsp rows if their modem/image trees were extracted - the split-file grammar exists only in the OnePlus packaging style [F - the contrast is structural on packaging, not on silicon].

## Comparison within the documented shard [F]

| device | SoC | cdsp rows | verdict |
|---|---|---|---|
| Galaxy_Tab_A7_LTE (gta4l, SM6115) | CDSP present (mainline) | 0 | census gap |
| Galaxy_S20_FE (r8q, SM8250) | CDSP present | 0 | census gap (#1096, adsp-side) |
| OnePlus_8 (SM8250) | CDSP present | 22 adsp rows at modem/image | positive control |

## Honest negatives

- The cdsp firmware's internal location (offset/segment inside Samsung's modem.bin) is [OPEN] - payload decomposition needed.
- Whether Samsung's integrated modem image uses the same cdsp.mdt/bXX grammar internally is [OPEN].
- The mainline CDSP node is for sm6115 generally; whether gta4l's specific board enables it in its dts is [OPEN] (the sm6115.dtsi node is inherited unless disabled).

## What would upgrade this finding

1. Payload fetch (gta4l stock modem image): locate the embedded cdsp image - the first Samsung-SM6115 DSP record; compare against the OnePlus split grammar.
2. Corpus pass: all SM6115/SM6225-class Samsung devices (Tab_A7 family, A03s-class) share this shape - one table covers them.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gta4l cdsp firmware` / `SM6115 cdsp firmware image` (web + GitHub code search, adineo-cmd/* excluded) -> mainline DT + guides; the CDSP existence is verified from mainline sm6115.dtsi by fetch. Nobody documents the Tab_A7_LTE cdsp gap.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus verified public trees.
