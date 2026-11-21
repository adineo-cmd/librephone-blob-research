# samsung Galaxy_Tab_S6_Wifi — `other` family status (32 rows)

Analysis date: 2026-11-21. Analyst: ZC-2 (issue [#509](https://github.com/adineo-cmd/open-device/issues/509)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site f737c8b), TheMuppets `proprietary_vendor_samsung_gta4xlwifi` + `proprietary_vendor_samsung_gta4xl-common` trees @ lineage-23.2 (all 32 rows md5-verified against these public files, 2026-11-21), `LineageOS/android_kernel_samsung_gta4xl` @ lineage-23.2 (DTS + drivers, fetched 2026-11-21), the lab's dax_param decode (`research/laptop/qualcomm-data-blob-fleet.md`), public spec pages. Evidence classes: [F] fact / [I] inference (labeled) / [H] hypothesis / [N] honest negative. No payload committed; hex samples ≤16 bytes.

**Verdict: the `other` family is PRESENT and fully md5-verified — 32 of 32 rows FOUND-MATCH against the public TheMuppets vendor trees @ lineage-23.2 (public md5 == upstream `md5_db`). The set decomposes into: the 5-file Samsung `bota` radio container (all corpus-device-unique), the SLSI Wi-Fi trio, and 24 Exynos 9611 vendor-firmware blobs (audio DSP, voice processor, vision DSP, camera ISP, video codec, speaker amp, tuning params, NPU model kernels) that are byte-identical with the LTE sibling. Identity correction: every one of these files is Galaxy Tab S6 **Lite** (SM-P610) hardware; the DB label "Galaxy Tab S6 WiFi" is a misnomer (see `boot.md` § Device identity). Note: issue [#1138](https://github.com/adineo-cmd/open-device/issues/1138) (ZC-1) produced an independent metadata-only analysis of the same 32 rows the same day — including the Exynos NPU reading of the `kernel_bin_*` group adopted below; this file supersedes it as the device-package (#509) deliverable and adds payload-level verification.**

## The 32 rows [F] — md5-verified against public trees

Verification method: each public file fetched from `raw.githubusercontent.com/TheMuppets/{proprietary_vendor_samsung_gta4xlwifi,proprietary_vendor_samsung_gta4xl-common}/lineage-23.2/...`, git-blob-sha1-checked against the trees API, then md5-compared to `md5_db` — 32/32 equal. Subfamily split: 31 `misc` + 1 `audio` (`spkamp.bin`). Magic probes are first-4..16 bytes of the verified public files [F].

### bota radio set (5) — db_path `samsung/gta4xlwifi/firmware/SM-P610` — all corpus-device-unique

| file | bytes | md5 | magic / first bytes |
|---|---:|---|---|
| `cm.bin` | 7,340,032 | `bb4614ec3b7a862a61ff7cb2eaf8cc98` | `1eabad10` = LE 0x10adab1e (hexspeak "LOADABLE") [I] |
| `keystorage.bin` | 8,192 | `d80a5fa4b69701ceda59819a31a8e4a3` | ASCII `SLSI ` |
| `sboot.bin` | 4,194,304 | `01bcfa003b05745bf636b3e2282018a5` | raw (Samsung S-Boot bootloader; format RE exists for older Exynos builds only — see RULE 0) |
| `uh.bin` | 284,056 | `d8782e98a1c291870a1dad890abc92b7` | ASCII `GREENTEA` |
| `up_param.bin` | 1,187,840 | `78519a8ce8f8e4db7509817d7dfaeb45` | ASCII `android_logo.jpg` — param-partition image (boot logos) |

These five are the platform's `bota` partition set (packed with 36-byte per-file headers, header magic 3142939818, per `android_device_samsung_gta4xl-common` releasetools.py @ lineage-23.2 [F]); sharing-clusters.csv records each as a 1-device cluster [F].

### SLSI Wi-Fi (3) — db_path `samsung/gta4xlwifi/vendor/etc/wifi`

| file | bytes | md5 | notes |
|---|---:|---|---|
| `mx140.bin` | 1,835,952 | `e12a29d322fec4af3b8ee2418c54ea99` | ASCII `smxf` at offset 8; SLSI (Samsung LSI) WLAN firmware |
| `mx140_t.bin` | 459,046 | `bd46002d3f7b048d774d8877773b2a78` | same `smxf` container prefix |
| `slsi_reg_database.bin` | 6,236 | `25f83d49fb05114aac800c3189556edb` | regulatory database |

Kernel interface [F]: `drivers/misc/samsung/scsc/` in `android_kernel_samsung_gta4xl` (mx140_file.c, mx140_clk.c, …) is the loading stack; no public format analysis exists [N].

### ABOX audio-DSP ext_bin set (6) — db_path `samsung/gta4xlwifi/vendor/firmware`

| file | bytes | md5 | magic | DTS load slot [F] |
|---|---:|---|---|---|
| `calliope_dram.bin` | 2,042,328 | `a6693246e317e8c4f30a35ab9069d5f1` | ASCII `CLP80012` | (device-tree-local firmware) |
| `calliope_iva.bin` | 57,728 | `c5fcd02b2edac6868d530ecd7e8a7beb` | ARM code words | (device-tree-local) |
| `calliope_sram.bin` | 32,892 | `9ff3f0065d46bb339f0caf3c1f539d6a` | ARM branch words (`18f09fe5` ×4) | (device-tree-local) |
| `AP_AUDIO_SLSI.bin` | 116,782 | `1bd16bc4a557967e8e66bea2bab89c77` | ASCII `FM4.9.X ` @8 | `ext_bin@1`, offset 0x7F0000 |
| `APBargeIn_AUDIO_SLSI.bin` | 10,818 | `98ac1252951f493f8f65ce86742df13c` | ASCII `FM4.9.X ` @8 | `ext_bin@2`, offset 0x7EC000 |
| `APBiBF_AUDIO_SLSI.bin` | 424 | `f23e6826f17de3b5784a467e8e659f0c` | ASCII `FM4.0.4 ` @8 | `ext_bin@5`, offset 0x7EF000 |

Calliope is the Exynos ABOX audio DSP firmware family; `arch/arm64/boot/dts/samsung/exynos9611-gta4xl_sound.dtsi` @ lineage-23.2 names each file with its exact ABOX load offset (lines 403-435) [F].

### Always-on voice processor (2)

| file | bytes | md5 | notes |
|---|---:|---|---|
| `dbmd8_va_fw.bin` | 280,840 | `c3c5ecdedc2297be0335e18bd35f15ab` | DTS `va-firmware-name` (sound dtsi line 327) [F] |
| `dbmd8_va_asrp_fw.bin` | 2,900 | `e6929b81800a7a92008520d3efcb1b56` | DTS `va-asrp-params-firmware-name` (line 328) [F] |

DBMD8 = DSP Group (Synaptics) always-on voice processor over SPI; kernel drivers `sound/soc/codecs/dbmdx/` [F].

### Vision DSP VIPX (3)

| file | bytes | md5 | kernel macro [F] |
|---|---:|---|---|
| `CC_DRAM_CODE_FLASH.bin` | 2,359,296 | `de7e0c47c20993545a3e6a8b92d8b905` | `VIPX_FW_DRAM_NAME` (vipx-binary.h line 18) |
| `CC_ITCM_CODE_FLASH.bin` | 8,192 | `36aeab276da2393781ebb64009b4d9bb` | `VIPX_FW_ITCM_NAME` (line 19) |
| `CC_DTCM_CODE_FLASH.bin` | 16,384 | `97213dfd871944630d52cfc7a7fb3113` | `VIPX_FW_DTCM_NAME` (line 20) |

`drivers/vision/vipx/vipx-binary.h` @ lineage-23.2 — each memory bank maps to its own file (DRAM/ITCM/DTCM respectively) [F; corrected against the audit: DTCM owns `CC_DTCM_CODE_FLASH.bin`, not ITCM]. Code words in ITCM/DTCM blobs are Thumb-2-style [I].

### Camera ISP (2) + sensor setfiles (2)

| file | bytes | md5 | notes |
|---|---:|---|---|
| `fimc_is_lib.bin` | 4,435,168 | `7e8283f2a5535490c0d2a405e6c9c46f` | AArch64 prologue (`fd7bbda9`) [I]; Exynos FIMC-IS camera ISP library |
| `fimc_is_rta.bin` | 2,166,976 | `336df377a2177b5e4c10ae1afef2e2ca` | AArch64 prologue [I]; runtime-tuning blob |
| `setfile_4ha.bin` | 600,348 | `a5aea67a322b7d04eab389f77d21143e` | `ISV7NC01` container prefix; per-sensor tuning (S5K4HA) [H] |
| `setfile_5e9.bin` | 1,339,588 | `c6ced62671bf216a8705dea95b4c2591` | `ISV7NC01` container prefix; per-sensor tuning (S5K5E9) [H] |

Sensor names [H] from the postmarketOS hardware table for samsung-gta4xlwifi (S5K4HA wide + S5K5E9 front, 2026-11-21); the two setfiles share an identical 16-byte container prefix but differ in payload [F].

### Video codec (1)

| file | bytes | md5 | notes |
|---|---:|---|---|
| `mfc_fw.bin` | 682,736 | `70fef51f5a0983e4a7643ddc98d4d0ba` | ARM32 branch-vector prologue (`770000ea` …) [I]; Exynos MFC codec firmware — distinct name/layout from mainline `s5p-mfc-v8.fw` in linux-firmware [F] |

### Tuning parameters + speaker amp (3)

| file | bytes | md5 | notes |
|---|---:|---|---|
| `dax_param.bin` | 34,736 | `70727b648c00a14bad7ede05ba9b4bd3` | **already decoded by this lab**: compiled Dolby DAX audio-tuning database — `research/laptop/qualcomm-data-blob-fleet.md` (measured + public-artifact match) [F] |
| `param_ti.bin` | 8,808 | `6f3d91643581209e61844ee9fbd75529` | `ext_bin@4`, offset 0x600000 (sound dtsi) [F]; TI audio-codec parameter blob [I] |
| `spkamp.bin` | 58,736 | `5e128ae4c9d4a7000308753249ee5ec9` | subfamily `audio`; `ext_bin@0`, offset 0x502000 [F]; Thumb-2-style code [I]; speaker-amp firmware (CS35L41-class per the pmOS hardware table) [H] |

### ABOX neural-net kernels (5)

| file | bytes | md5 |
|---|---:|---|
| `kernel_bin_enf.bin` | 149,068 | `7b25e670f7f1fd64056d57a5004522af` |
| `kernel_bin_inception.bin` | 322,188 | `5828ed537252c9b59fc68ad1e2cc3bef` |
| `kernel_bin_mfb.bin` | 267,300 | `af2069bd1665c68217a6c976f976e1f6` |
| `kernel_bin_mobile_vgg.bin` | 292,748 | `73ef882614fcc9f64f84bfbab7e04a91` |
| `kernel_bin_nfd.bin` | 290,444 | `e8d76f11700e55601b8d3263d0140dca` |

The `kernel_bin_*` set is Exynos NPU model kernels — `inception` and `mobile_vgg` are recognizable CNN topology names, matching the ensemble-model containers the Exynos NPU driver family loads (reading credited to the independent #1138 analysis [I]); each file carries an 8-byte header + payload. The Samsung NPU model-container format itself is undecoded — a decode would be a leverage family across every Exynos NPU device in the corpus [N].

## Fleet sharing [F]

Per `research/laptop/sharing-clusters.csv`: all 27 vendor-firmware + Wi-Fi rows are byte-identical with `Galaxy_Tab_S6_LTE` (gta4xl, SM-P615 — the same Lite hardware with cellular); `dax_param.bin` sits in the lab's largest data-blob cluster (11 devices, md5 `70727b64…`). The 5 bota radio files are corpus-device-unique (1-device clusters), as are the boot images — per-build signed binaries. Both "Tab S6" DB identities are Tab S6 Lite hardware (SM-P610 / SM-P615); the real 2019 Tab S6 (SM-T860, SM8150) appears nowhere in the corpus.

## RULE 1 improvements (this session, before → after)

- `research/laptop/qualcomm-data-blob-fleet.md` "What is still open": the item "Which `dax_param.bin` md5 the `a21s`/`a71`/`f62`/`gta4l*`/`gta4xl*` trees carry — the CSV says `70727b64…`, but those trees returned no `dax_param.bin` hit in this pass" is RESOLVED with evidence: `dax_param.bin` md5 `70727b648c00a14bad7ede05ba9b4bd3` (34,736 B) is md5-verified in the public `proprietary_vendor_samsung_gta4xl-common` tree @ lineage-23.2 (2026-11-21); the 11-device cluster stands.
- The document-corpus pins were stale and the site build exited 1 on any current tree: `site/tests/test_model.py` `test_141_documents` pinned 141 documents (the corpus had drifted past 185 by the time of this fix and kept growing under concurrent agents) and `site/build.py`+`site/lib/render.py` pinned exact (141 docs, 407 pages). The corpus only grows in normal operation, so the two drifting counts became floors (`test_corpus_floor`, `MIN_DOCS`/`MIN_TOTAL` with a `>=` check in build.py) while the inventory-locked counts (devices/families/types/static) keep exact pins; before → after: red suite + failing build → all 8 test suites and `site/build.py` green.
- Reported for the lead (shared files, no winning claim here): `site/data/device-types.csv:52` note reads "gta4xlwifi, Samsung Galaxy Tab S6 WiFi" — proposed one-line diff: `Galaxy_Tab_S6_Wifi,tablet,mobile,"gta4xlwifi, Samsung Galaxy Tab S6 Lite WiFi (SM-P610; DB label misnomer)"`. The SoC cell of `device-inventory.csv:151` is empty and can now be filled with "Samsung Exynos 9611".

## Honest negatives

- No public format analysis exists for any of the 24 vendor-firmware blobs (adversarial audit 2026-11-21, 20+ filename-scoped queries; adjacent S9/S22-era calliope work cited in the issue) [N].
- `cm.bin`'s role on a Wi-Fi-only tablet (LOS flashes a CM partition even without cellular) is unresolved — the SSTIC-2016 Shannon-crypto reading is from modem-bearing devices [OPEN].
- The `kernel_bin_*` NN-stage mapping, `mx140` container layout, and `setfile` internals are undecoded [N].
- The identity misnomer reaches upstream: the LibrePhone DB labels SM-P610 files "Galaxy Tab S6 WiFi" (db_path `firmware/SM-P610` proves the payloads); upstream-side correction is owner-gated [N].

## What would upgrade this finding

1. Decode the `bota` 36-byte header chain (releasetools magic 3142939818) end-to-end from a stock `bota` partition dump.
2. Instrument the ABOX loader path (`abox.c` + ext_bin offsets) to map each `kernel_bin_*` to its DSP stage.
3. md5-join the SLSI Wi-Fi trio against the scsc driver's expected firmware versions to date the build.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments; adversarial audit re-attacked identity, prior-art, kernel citations, sizes and counts the same day (one vipx macro corrected before publication). Check: per-blob filename searches + `exynos9611 SM-P610 blob analysis` (web + GitHub code search, adineo-cmd/* excluded) → vendor manifests, kernel interface files and ROM threads only; no census or format analysis of this set exists.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata, hashes of publicly available files, and cited public sources.
