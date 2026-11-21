# samsung Galaxy_Tab_S7_LTE — `cdsp` family status (0 rows - census gap; the SoC has a CDSP, positive control attached)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1144](https://github.com/adineo-cmd/open-device/issues/1144)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 213d0b3), mainline `arch/arm64/boot/dts/qcom/sm8250.dtsi` (fetched 2026-11-21), the sibling doc `docs/devices/samsung/Galaxy_S20_FE/adsp.md` (#1096, same SoC), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `cdsp` rows is a CENSUS GAP, not structural absence - the strongest case yet, because the same-SoC positive control is inside this corpus.** The device is an SM8250 (Snapdragon 865+, codename `gts7l`, SM-T875): mainline carries the CDSP remoteproc (`sm8250.dtsi:3789`, `cdsp: remoteproc@8300000`), and OnePlus_8 - the same SoC - carries **12+ cdsp rows** (`cdsp.mdt` + non-contiguous `cdsp.b00..b06/b08/b09/b11` + `cdspr.jsn`) at its modem/image directory. Samsung's gts7l census has no modem/image extraction at all, so the DSP firmware (which lives inside Samsung's modem partition image) never reaches the census.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab S7 LTE (SM-T875); codename `gts7l` | `device-inventory.csv` [F] |
| SoC | Qualcomm **SM8250-AC Snapdragon 865+**; Adreno 650; Hexagon CDSP present (mainline `sm8250.dtsi:3789`) | public spec pages (2026-11-21) [F]; mainline fetched 2026-11-21 [F]; the device's a650_gmu/a650_sqe gpu rows (#1036-class) corroborate the SoC [F] |
| census scope | 26 rows in 6 families (other 14, boot 5, wifi 3, gpu 2, bt 1, modem 1); 260,387,951 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 cdsp rows; the census has **no modem/image directory** - paths are `samsung/gts7l/{radio, vendor/etc(+locale), vendor/firmware(+qca6390), vendor/lib64/camera}` [F].
- The modem family is a single row (the #1096/#1108 Samsung shape) [F].
- The gpu family (2 rows: a650_gmu 41,548 + a650_sqe 31,632) confirms the SM8250 identity from the firmware side [F].

## The positive control [F]

| device | SoC | cdsp rows | form |
|---|---|---:|---|
| OnePlus_8 (instantnoodle) | SM8250 | **12+** | split: cdsp.mdt + cdsp.b00..b06, b08, b09, b11 (non-contiguous - real segment holes) + cdspr.jsn manifest, at `oneplus/instantnoodle/modem/image` |
| Galaxy_Tab_S7_LTE (gts7l) | SM8250 | 0 | Samsung packages the DSP inside the modem partition image; no vendor-tree copy |
| Galaxy_S20_FE (r8q) | SM8250 | 0 | same shape (#1096, adsp side) |

The OnePlus slice is the corpus's window into the SM8250 DSP grammar - the split-form cdsp files with their **non-contiguous segment numbering** (b07 and b10 absent) are recorded there and absent here purely by packaging.

## Comparison across the documented Samsung census gaps [F]

| device | SoC | missing family | class |
|---|---|---|---|
| Galaxy_S20_FE (r8q) | SM8250 | adsp (0 rows) | census gap (#1096) |
| Galaxy_Tab_S7_LTE (gts7l) | SM8250 | cdsp (0 rows) | census gap (this doc) |
| Galaxy_Tab_A7_LTE (gta4l) | SM6115 | cdsp (0 rows) | census gap (#1108) |
| Galaxy_Tab_A7_Wifi (gta4lwifi) | SM6115 | adsp (0 rows) | census gap (#1114) |
| Galaxy_Note_10_Plus (d2s) | Exynos 9611 | gpu/cdsp (0 rows) | structural (#1036/#1126) |
| Galaxy_F62/A21S/S10 family | Exynos | tz/gpu/cdsp | structural (#1030-class) |

The rule that emerges: **Samsung SM-class devices show census gaps for families that ride in the modem image; Samsung Exynos devices show structural absences.** Both are extract-scope effects, cleanly separated by the SoC line.

## Honest negatives

- The cdsp firmware's exact location inside Samsung's modem.bin is [OPEN] (payload decomposition needed).
- Whether Samsung's integrated image uses the cdsp.mdt/bXX grammar with the same non-contiguous segment holes is [OPEN].
- The `qca6390` firmware dir in gts7l's census (the WCN685x-class BT/WLAN companion SoC) is outside this family; its census is a wifi/bt-family matter. [OPEN scope]

## What would upgrade this finding

1. Payload fetch (gts7l stock modem image): decompose for the embedded cdsp/cdsp_r images - the first Samsung-SM8250 CDSP record; diff against the OnePlus split grammar.
2. Lead-level: the samsung census-gap table above is ready to become a family-classification rule (modem-image-integrated vs vendor-tree families).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `gts7l cdsp firmware` / `SM8250 cdsp firmware image` (web + GitHub code search, adineo-cmd/* excluded) -> mainline DT + ROM guides; the SM8250 CDSP is proven by mainline fetch and the OnePlus positive control. Nobody documents the Tab_S7_LTE cdsp gap.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus verified public trees.
