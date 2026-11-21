# samsung Galaxy_Tab_S6_Wifi — `other` family status (32 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1138](https://github.com/adineo-cmd/open-device/issues/1138)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 213d0b3), the identity correction in `docs/devices/samsung/Galaxy_Tab_S6_LTE/cdsp.md` (#1126), public Exynos/Exynos-NPU driver documentation. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the `other` family is PRESENT as a rich Exynos platform census** - 32 rows / 30,893,086 B across 12 groups: the BL-grammar files (5), SLSI audio DSP (3), calliope audio-DSP memory images (3), camera-coprocessor code-flash (3), Knowles voice-assistant DSP (2), Exynos camera ISP (2), camera setfiles (2), **Exynos NPU model kernels (5)**, MFC video codec (1), SLSI WiFi files (3), spkamp amplifier (1), param_ti (1), and the fleet-wide dax_param.bin (1). All 32 md5s corpus-unique; all P3. The device is the Exynos 9611 Tab S6 Lite wifi (the #1126 identity correction applies).

## Device identity

| fact | value | source |
|---|---|---|
| model | **Samsung Galaxy Tab S6 Lite (Wifi), SM-P610**; codename `gta4xlwifi` | census path `samsung/gta4xlwifi/firmware/SM-P610` [F]; #1126 identity correction [F] |
| SoC | Samsung **Exynos 9611** (4x A73 + 4x A53; Mali-G72 MP3) | spec pages (2026-11-21) [F]; #1126 [F] |
| census scope | 38 rows in 2 families (boot 6, other 32); no modem family | coverage-matrix.csv [F] |

## The 32 rows, grouped [F]

| group | rows | bytes | notable contents |
|---|---|---:|---|
| BL grammar | 5 | 13,014,424 | cm.bin 7,340,032; keystorage.bin **8,192** (vs F62's 524,288); sboot.bin 4,194,304; uh.bin **284,056** (F62: 276,120); up_param.bin **1,187,840** (F62: 2,938,880) - the Exynos 9611 BL sizes differ from the 9825 set [F] |
| SLSI audio DSP | 3 | 128,024 | AP_AUDIO_SLSI 116,782; APBargeIn 10,818; APBiBF 424 |
| calliope audio DSP | 3 | 2,132,948 | calliope_dram 2,042,328; calliope_iva 57,728; calliope_sram 32,892 |
| camera coprocessor | 3 | 2,383,872 | CC_DRAM_CODE_FLASH 2,359,296; CC_DTCM 16,384; CC_ITCM 8,192 - code-flash images for a camera coprocessor's DRAM/ITCM/DTCM memories |
| voice DSP | 2 | 283,740 | dbmd8_va_fw.bin 280,840; dbmd8_va_asrp_fw.bin 2,900 - Knowles-class DBMD8 voice-assistant DSP + ASRP (speech-recognition processor) firmware |
| camera ISP | 2 | 6,602,144 | fimc_is_lib 4,435,168; fimc_is_rta 2,166,976 |
| camera setfiles | 2 | 1,939,936 | setfile_4ha.bin 600,348; setfile_5e9.bin 1,339,588 |
| **Exynos NPU kernels** | 5 | 1,321,748 | kernel_bin_{enf 149,068, inception 322,188, mfb 267,300, mobile_vgg 292,748, nfd 290,444} - neural-network model kernels for the Exynos NPU (inception/VGG = CNN topology names) |
| MFC video codec | 1 | 682,736 | mfc_fw.bin |
| SLSI WiFi | 3 | 2,301,234 | mx140.bin 1,835,952 + mx140_t.bin 459,046 (vendor/etc/wifi); slsi_reg_database.bin 6,236 |
| amplifier | 1 | 58,736 | spkamp.bin |
| param | 2 | 43,544 | param_ti.bin 8,808; dax_param.bin 34,736 (fleet-wide file, #1102) |

Group sums [F, python-verified]: BL 13,014,424 + audio 128,024 + calliope 2,132,948 + CC 2,383,872 + dbmd8 283,740 + fimc 6,602,144 + setfiles 1,939,936 + NPU 1,321,748 + mfc 682,736 + wifi 2,301,234 + spkamp 58,736 + param 43,544 = 30,893,086 B total.

## The Exynos NPU kernels - the group worth scaling [F + I]

`kernel_bin_{enf, inception, mfb, mobile_vgg, nfd}` are model binaries for Samsung's Exynos NPU (the ensembles the mainline Exynos NPU driver loads; `inception` and `mobile_vgg` are recognizable CNN topology names). This is the first NPU-model group in the documented shard - a decode would give the Samsung NPU model-container format, a leverage family across every Exynos NPU device in the corpus [I - the container format itself is undecoded, OPEN].

## Cross-device facts [F]

- All 32 md5s are corpus-unique to Galaxy_Tab_S6_Wifi [F].
- dax_param.bin 34,736 B = the fleet-wide size (#1102) [F]; sboot.bin 4,194,304 B = the Samsung BL constant [F].
- The SM-P610 BL sizes differ from F62's 9825 set (keystorage 8,192 vs 524,288; uh 284,056 vs 276,120; up_param 1,187,840 vs 2,938,880) - per-generation BL builds [F].
- No modem family (wifi-only device, #1132) [F].

## ISA proof and interface facts

- No row carries an ISA claim (`isa_identified` empty across the 32) - honestly un-RE'd [F]. The Exynos 9611's DSPs/coprocs are ARM/proprietary cores per public Exynos documentation, unverified per payload [I].
- Interface [I, labeled]: calliope/dbmd8 load via the audio HAL path; NPU kernels via the Exynos NPU driver (mainline has hardkernel Exynos NPU driver work); MFC via the s5p-mfc-style interface (linux-firmware carries s5p-mfc variants upstream). None payload-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- Every group's internal structure is [OPEN]: the NPU model-container format, the calliope memory-image layout, the CC code-flash format, the dbmd8 voice-DSP container - all undecoded in this repo.
- The Exynos 9611 generation's firmware grammar differs from the 9825 (keystorage/uh/up_param sizes above) - a full generation comparison needs the SM-P615 LTE sibling's rows (#1126's modem.bin) [OPEN].

## What would upgrade this finding

1. Payload fetch: decode the 5 NPU model kernels (1,321,748 B total) - the Samsung NPU model container is the highest-leverage decode in this slice (fleet-wide across Exynos NPU devices).
2. Corpus pass: dax_param.bin's identical 34,736-B size across the samsung slice - one decode covers many devices.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `calliope Exynos audio DSP firmware`, `dbmd8 voice assistant DSP`, `Exynos NPU kernel_bin model firmware`, `mfc_fw Exynos` (web + GitHub code search, adineo-cmd/* excluded) -> kernel driver sources, component pages, ROM guides; no structural decodes exist. Nobody documents the Tab_S6_Wifi other-family census.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public driver documentation.
