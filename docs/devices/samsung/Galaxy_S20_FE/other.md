# samsung Galaxy_S20_FE — `other` family status (26 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1102](https://github.com/adineo-cmd/open-device/issues/1102)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 416d7ac), the LineageOS r8q extract list (fetched 2026-11-21 for #1096), public component documentation. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the `other` family is PRESENT as a pure peripheral-firmware census** - 26 rows, zero main-compute payloads: touch controller (2 region variants), Cirrus Logic audio-amplifier/haptic firmware (7, db_type AUDIOAMP), camera OIS MCU + ToF calibration (3), PLMN carrier tables (9), NFC controller firmware + registers (3, db_type NFC), dax_param.bin, and the IPA firmware row already analyzed in #1096. Every row is a vendor peripheral; all P3.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S20 FE 5G (SM-G781B); codename `r8q` | `device-inventory.csv` [F]; LineageOS r8q tree (2026-11-21) [F] |
| SoC | Qualcomm SM8250 Snapdragon 865 | public specs (2026-11-21) [F]; SoC cell supplied in #1096 |
| census scope | 38 rows in 6 families; other = 26 rows | coverage-matrix.csv [F] |

## The 26 rows, grouped [F]

| group | rows | files (bytes, md5 status) | role [I, name/vendor-derived] |
|---|---|---|---|
| Touch | 2 | a96t356_r8q_all.bin 14,368 `87343d8e...`; a96t356_r8q_usa.bin 14,368 `c5789101...` | Samsung a96t356 touch-controller firmware - two region builds (all/USA), same size, distinct md5s |
| Audio amp + haptic | 7 | cs35l40-bot-dsp1-spk-prot.bin 4,216; -calib 980; cs35l40-rcv-dsp1-spk-prot.bin 4,216; -calib 980; cs40l20.bin 7,768; cs40l25a_clab.bin 100; cs40l25a_exc.bin 48 - all db_type **AUDIOAMP** | Cirrus Logic SmartAmp speaker protection (bot = bottom speaker, rcv = receiver) + CS40L haptic-driver firmware/config; the cs35l40/cs40l families have mainline ASoC driver support (firmware FILE names appear in kernel sources) |
| Camera | 3 | ois_mcu_stm32g_fw.bin 40,100 (vendor/lib64/camera); t_tof_calibration.bin 760; w_tof_calibration.bin 760 (same path) | OIS actuator MCU firmware (STM32G-class MCU) + front/rear ToF sensor calibration blobs |
| PLMN tables | 9 | plmn_se13.bin 24,562; plmn_delta.bin 11,412; plmn_delta_{attaio,eng,hktw,usagsm,zh-rCN,zh-rHK,zh-rTW}.bin 446-1,233 (vendor/etc + vendor/etc/locale) | carrier/region PLMN lists (SE.13 = the 3GPP country-code standard; deltas per region: eng, HK/TW/CN, USA-GSM) |
| NFC | 3 | sec_s3nrn4v_firmware.bin 184,620 (vendor/firmware/nfc, db_type NFC); sec_s3nrn4v_hwreg.bin 3,232; sec_s3nrn4v_swreg.bin 336 (vendor/etc/nfc) | Samsung SEC S3NRN4V NFC controller firmware + hardware/software register images - the F62-class NFC set (#1030) |
| misc | 2 | dax_param.bin 34,736; ipa_uc.mdt 6,860 ELF64 | dax_param = Samsung parameter blob (identical 34,736-B size across F62/Note10/S10 censuses); ipa_uc = IPA firmware (analyzed in #1096) |

Group sums [F, python-verified]: touch 28,736 + audio/haptic 18,308 + camera 41,620 + PLMN 42,709 + NFC 188,188 + misc 41,596 = 361,157 B total.

## Cross-device facts [F]

- All 26 md5s are corpus-unique to Galaxy_S20_FE - every row is single-device in this census [F].
- `dax_param.bin` 34,736 B appears at the identical size on Galaxy_F62, Note_10, Note_10_Plus, S10, S10e, S10_5G censuses (a fleet-wide Samsung parameter file, per-device md5s) [F].
- `sec_s3nrn4v_*` (184,620/3,232/336 B) matches the F62 NFC set sizes [F]; `cs35l40`/`cs40l25a` files appear across the samsung slice with per-device md5s [F].
- The r8q extract list carries every one of these files - census complete against its public package source [F].
- No modem/image grammar anywhere in this family (the #1096 packaging fact) [F].

## ISA proof and interface facts

- `ipa_uc.mdt` is `isa_identified=ELF64` [F]; all other rows UNKNOWN [F]. Peripheral-firmware ISAs (Cortex-M-class for the OIS MCU, proprietary DSP cores for Cirrus SmartAmps) are [I] from component families - not payload-verified.
- Interface [I, labeled]: touch I2C/SPI firmware load at probe; Cirrus amps load via ASoC regmap; OIS via camera I2C; NFC firmware via the NFC controller HAL. None payload-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- Internal structure of every peripheral blob (touch calibration layout, SmartAmp WMFW/CRBZ containers, PLMN binary format) is [OPEN] - the wmfw/crabz-style Cirrus containers have public format documentation upstream (linux-firmware carries cs35lxx-derived files) but no Samsung-specific decode exists.
- The a96t356 region split (all vs USA) semantics (hardware variant vs regulatory config) is [OPEN].

## What would upgrade this finding

1. Payload fetch: parse the Cirrus cs35l40/cs40l containers against the upstream format docs (linux-firmware ships cs35lxx-derived files) - the first Samsung SmartAmp blob decode.
2. Corpus pass: the dax_param.bin fleet (identical 34,736-B size across 6+ samsung devices) and the sec_s3nrn4v NFC trio are Samsung-wide leverage families - one decode covers many devices.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `a96t356 touch firmware`, `cs35l40 Cirrus SmartAmp firmware`, `ois_mcu_stm32g`, `sec_s3nrn4v NFC` (web + GitHub code search, adineo-cmd/* excluded) -> component datasheets/kernel sources/ROM guides; no Samsung-specific structural analysis exists.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public component documentation.
