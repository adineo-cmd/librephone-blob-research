# samsung Galaxy_Tab_S7_Wifi — `adsp` family status (0 rows - census gap; LTE/Wifi census is 23/26 byte-identical)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1150](https://github.com/adineo-cmd/open-device/issues/1150)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site e023204), the sibling doc `docs/devices/samsung/Galaxy_Tab_S7_LTE/cdsp.md` (#1144), mainline `sm8250.dtsi` (verified 2026-11-21 for #1144). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `adsp` rows is a CENSUS GAP - the SM8250 ADSP is proven by the same-SoC OnePlus positive control (22 adsp rows at modem/image) - and this device contributes a stronger finding: the Tab S7 LTE/Wifi pair's censuses are 23-of-26 rows byte-identical.** Only the three Android images (boot/recovery/dtbo) differ between the variants, and even those share identical sizes.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab S7 Wifi (SM-T970); codename `gts7lwifi` | `device-inventory.csv` [F] |
| SoC | Qualcomm **SM8250-AC Snapdragon 865+**; Hexagon ADSP present (mainline `sm8250.dtsi` remoteproc set, verified for the family in #1144) | public spec pages (2026-11-21) [F]; the a650_gmu/a650_sqe gpu rows corroborate [F] |
| census scope | 26 rows in 6 families (other 14, boot 5, wifi 3, gpu 2, bt 1, modem 1); 260,387,951 B - **byte-identical total to gts7l** | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 adsp rows; no modem/image directory in the census (paths: `samsung/gts7lwifi/{radio, vendor/etc(+locale), vendor/firmware(+qca6390), vendor/lib64/camera}`) [F].
- The modem family is a single row: `ipa_fws.mdt` 7,020 B ELF64 [F] - the #1144 Samsung shape.

## The LTE/Wifi byte-identity finding [F]

Row-by-row comparison of gts7l vs gts7lwifi (26 rows each):

- **23 rows byte-identical** (same filename, size, md5 - only the census path prefix differs): a650_gmu.bin 41,548, a650_sqe.fw 31,632, amss20.bin 4,389,024, cs35l40-spk pair (4,220 + 984), htnv20.bin 5,950, ipa_fws.mdt 7,020, ipa_uc.mdt 6,860, m3.bin 266,668, all 9 PLMN files, regdb.bin 19,348, both ToF calibration files, unsparse_super_empty.img 4,644 [F].
- **3 rows differ in md5 only** (sizes identical): boot.img 71,303,168, recovery.img 86,888,448, dtbo.img 10,485,760 [F].
- Consequence: the census total (260,387,951 B) is identical for both variants [F].

Reading: the LTE and Wifi Tab S7 variants ship **one shared firmware extract** for everything except the three Android images - the wifi/LTE difference lives entirely in boot/recovery/dtbo (and the absent modem partition on the wifi variant, which this census never captured anyway). The shared rows include the entire Qualcomm radio-side set that rides in vendor/firmware.

## Why census gap, not structural absence [F]

The #1144 reasoning transfers to the adsp side: mainline's SM8250 defines the ADSP remoteproc; OnePlus_8 (same SoC) carries **22 adsp rows** (`adsp.mdt` + `b00..b07` + manifest) at modem/image; Samsung's gts7lwifi census has no modem/image extraction, so the DSP firmware never reaches the census. The #1096/#1144/#1150 trio is the same phenomenon on three Samsung SM8250 devices.

## Honest negatives

- The adsp firmware's location inside Samsung's modem.bin is [OPEN] (payload decomposition needed) - identical to #1144's cdsp [OPEN].
- Whether the wifi variant's modem image (absent from the census) differs from the LTE one is [OPEN] - the census cannot see it.

## What would upgrade this finding

1. Payload fetch (gts7lwifi modem image): decompose for the embedded adsp/cdsp images - then the LTE/Wifi identity question extends into the DSP layer.
2. Lead-level: the byte-identity finding suggests census deduplication policy for variant pairs (gts7l/gts7lwifi joins the dual-model notes from #1072/#1090).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gts7lwifi adsp firmware` / `SM8250 adsp firmware image` (web + GitHub code search, adineo-cmd/* excluded) -> mainline DT + ROM guides; the SM8250 adsp grammar is the in-repo OnePlus fleet work, cited. Nobody documents the Tab_S7_Wifi adsp gap or the LTE/Wifi byte-identity.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus verified public trees.
