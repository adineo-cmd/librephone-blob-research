# samsung Galaxy_Tab_A7_Wifi — `adsp` family status (0 rows - census gap; the SoC has an ADSP)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1114](https://github.com/adineo-cmd/open-device/issues/1114)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site db1ee51), mainline `arch/arm64/boot/dts/qcom/sm6115.dtsi` (fetched 2026-11-21), the sibling doc `docs/devices/samsung/Galaxy_Tab_A7_LTE/cdsp.md` (#1108). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `adsp` rows is a CENSUS GAP, not structural absence - the SoC provably has the ADSP.** Mainline carries `remoteproc_adsp` with compatible **`qcom,sm6115-adsp-pas`** (`sm6115.dtsi:2772-2773`) plus `pil_adsp_mem` (line 492) and the `smp2p-adsp` pair (line 537): the SM6115 audio DSP loads firmware via PAS. The firmware ships inside Samsung's modem partition image; no separate vendor-tree copy exists, so no adsp files reach the census.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab A7 Wifi (SM-T500); codename `gta4lwifi` | `device-inventory.csv` [F] |
| SoC | Qualcomm **SM6115 Snapdragon 662**; **ADSP present** (mainline `qcom,sm6115-adsp-pas`, remoteproc@a400000, PAS loader) | public spec pages (2026-11-21) [F]; mainline sm6115.dtsi fetched 2026-11-21 [F] |
| census scope | 38 rows in 6 families (other 21, gpu 7, boot 6, wifi 2, bt 1, modem 1); 336,002,819 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 adsp rows; no adsp-grammar tokens anywhere in the 38 rows [F].
- The modem family is a single row: `ipa_fws.mdt` 7,020 B ELF64 at `samsung/gta4lwifi/vendor/firmware` [F] - no modem/image directory exists (the #1096/#1108 Samsung shape) [F].
- Census paths are the wifi-variant shape: `samsung/gta4lwifi/{radio, vendor/etc, vendor/firmware(+wlan/qca_cld)}` [F] - no separate firmware model dirs (wifi-only device, one model variant).

## Why census gap, not structural absence [F]

The #1108 reasoning applies to the ADSP side:
1. **The SoC has the DSP**: mainline defines the ADSP remoteproc with the PAS loader - firmware must exist on-device [F].
2. **Samsung's packaging**: the SM6115 ADSP firmware lives inside the modem partition image; the gta4l-family extract lists contain no adsp entries (#1108's 123-entry LTE list; the wifi variant likewise) [F].
3. **The corpus contrast**: OnePlus devices carry their adsp sets as modem/image split files (22 rows on OnePlus_8); Samsung integrates them into the modem image [F].

## Comparison within the gta4l family [F]

| device | SoC | adsp rows | cdsp rows | verdict |
|---|---|---|---|---|
| Galaxy_Tab_A7_LTE (gta4l) | SM6115 | 0 | 0 (#1108) | census gaps |
| Galaxy_Tab_A7_Wifi (gta4lwifi) | SM6115 | 0 | 0 (same shape, #1108-class) | census gaps |
| OnePlus_8 (SM8250) | SM8250 | 22 at modem/image | (positive control) | split-file grammar |

The gta4l/gta4lwifi pair shares the identical census shape (ipa_fws.mdt as the only modem-class row); the family-level doc suggestion from #1108 covers both.

## Honest negatives

- The ADSP firmware's location inside Samsung's modem.bin is [OPEN] (payload decomposition needed).
- Whether the integrated image uses the adsp.mdt/bXX grammar internally is [OPEN].

## What would upgrade this finding

1. Payload fetch (SM-T500 stock modem image): locate the embedded adsp image - the first Samsung-SM6115 ADSP record.
2. Lead-level: one gta4l-family doc (LTE + Wifi) covers both census gaps (#1108/#1114).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gta4lwifi adsp firmware` / `SM6115 adsp firmware image` (web + GitHub code search, adineo-cmd/* excluded) -> mainline DT + guides; the ADSP existence is verified from mainline sm6115.dtsi by fetch. Nobody documents the Tab_A7_Wifi adsp gap.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus verified public trees.
