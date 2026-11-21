# samsung Galaxy_Tab_A7_Wifi — `other` family status (21 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1120](https://github.com/adineo-cmd/open-device/issues/1120)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site db1ee51), the sibling doc `docs/devices/samsung/Galaxy_Tab_A7_LTE/cdsp.md` (#1108), public touch-IC vendor documentation. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the `other` family is PRESENT as a touch/display-panel firmware fleet plus two platform files** - 21 rows: FocalTech touch x3, Himax touch x8 (all 131,072 B), Novatek touch x8 (fw/mp pairs, all 196,608 B), the `scuba_ipa_fws.mdt` IPA row (scuba = the SM6115 platform codename - the Moto SM6115 fleet carries the same firmware as a 6-row split), and the fleet-wide `dax_param.bin`. All 21 md5s corpus-unique; all P3.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab A7 Wifi (SM-T500); codename `gta4lwifi` | `device-inventory.csv` [F] |
| SoC | Qualcomm SM6115 Snapdragon 662 (platform codename **scuba** per the ipa firmware naming) | public spec pages (2026-11-21) [F]; the codename reading is [I] from the `scuba_ipa_fws` filename + mainline sm6115 support |
| census scope | 38 rows in 6 families; other = 21 rows | coverage-matrix.csv [F] |

## The 21 rows, grouped [F]

| group | rows | files (bytes) | role [I, vendor-derived] |
|---|---|---:|---|
| FocalTech touch | 3 | focaltech_ts_fw_lide.bin 61,520; focal_ts_fw_lide_hsd.bin 68,680; focal_ts_fw_tianma_tianma.bin 70,080 | FocalTech touch-controller firmware, per display panel (lide/hsd = HSD-shipped lide panel; tianma) |
| Himax touch | 8 | Himax_firmware_{djn_jdi, hlt_auo, inx_fhd, lide_hsd, tianma_tianma, txd_auo_al, txd_auo, txd_inx}.bin - **all exactly 131,072 B** | Himax touch firmware, one build per panel pairing (jdi/auo/inx/tianma = panel makers; djn/hlt/txd/lce = touch-combo codes) |
| Novatek touch | 8 | novatek_ts_fw_{hlt_auo, lce_panda, lide_hsd, txd_inx}.bin + novatek_ts_mp_{same 4}.bin - **all exactly 196,608 B** | Novatek touch firmware (fw) + MP production-test firmware (mp) pairs, 4 panel variants |
| IPA firmware | 1 | scuba_ipa_fws.mdt 6,868 ELF64 | IPA (IP accelerator) firmware, single-file form; **scuba = the SM6115 platform codename** |
| Samsung param | 1 | dax_param.bin 34,736 | Samsung parameter blob - the fleet-wide file (#1102) |

Group sums [F, python-verified]: FocalTech 200,280 + Himax 1,048,576 + Novatek 1,572,864 + scuba IPA 6,868 + dax_param 34,736 = 2,863,324 B total.

## The touch-panel fleet [F]

The tablet ships with multiple display-panel vendors, and the census carries one firmware per panel pairing across **three touch-controller vendors**: FocalTech (3 panels), Himax (8), Novatek (8). Panel codes recur across vendors (lide_hsd appears in all three; tianma in FocalTech+Himax; txd_inx in Himax+Novatek; hlt_auo in Himax+Novatek) - the bootloader/FE loads the matching set at probe. Size laws: Himax builds are uniformly 131,072 B; Novatek uniformly 196,608 B; FocalTech varies per panel (61,520/68,680/70,080).

## The scuba IPA finding [F + I]

- `scuba_ipa_fws.mdt` 6,868 B ELF64 (single-file form) on this device [F].
- The Moto SM6115 fleet (Defy_2021/bathena, Moto_G42/G30/G32/G9/G9_Power/G_Power/G_Stylus_5G/G10/E7_Plus) carries the same firmware as a **6-row split** - `scuba_ipa_fws.mdt` 7,020 ELF64 + b00 212/b01 6,808/b02 12,040/b03 128/b04 320, db_type **CELL**, at `modem/image` [F].
- Reading [I]: scuba is Qualcomm's platform codename for SM6115; the IPA firmware exists fleet-wide on SM6115 devices in two packaging forms (Samsung: single file in vendor/firmware; Moto: split in modem/image). The corpus's IPA rows were previously known only from #1096's r8q note - this extends the IPA family to the whole SM6115 Moto fleet.

## Honest negatives

- The Himax/Novatek/FocalTech firmware internals (panel-config structure, calibration blocks) are undecoded - the touch ICs have public driver sources but no firmware-format docs for these blobs. [OPEN]
- The mp-vs-fw Novatek split (production test vs runtime) is [I] from vendor naming. [OPEN]
- Which panel/touch pairing a given unit actually uses is runtime-selected; the census carries all variants. [F - shape only]

## What would upgrade this finding

1. Payload fetch: decode one Himax and one Novatek blob (131,072/196,608 B fixed-size containers suggest header+padding layouts) - the first Samsung touch-firmware structural record.
2. Corpus pass: the scuba_ipa split-form vs single-form comparison across the SM6115 fleet (sizes 6,868 vs 7,020 mdt) - one table covers ~12 devices.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `focaltech ts firmware lide`, `himax touch firmware tablet`, `novatek ts_fw mp` (web + GitHub code search, adineo-cmd/* excluded) -> vendor driver sources/ROM guides; no structural firmware decodes exist for these blobs. Nobody documents the Tab_A7_Wifi other-family census or the scuba codename.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public vendor documentation.
