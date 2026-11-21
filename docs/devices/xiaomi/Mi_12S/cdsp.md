# xiaomi Mi_12S (mayfly) - `cdsp` family status (19 rows: present, complete Qualcomm split-ELF PIL image)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1180](https://github.com/adineo-cmd/open-device/issues/1180)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows; worktree checkout of feat/open-device-site at a7b7b0e), `upstream-contribution/blob-database/device-inventory.csv`, mainline kernel sources (torvalds/linux master, fetched 2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), LineageOS mayfly device/vendor trees (fetched 2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: PRESENT - the `cdsp` family on Mi_12S is a complete Qualcomm signed split-ELF PIL image: 19 rows, 7,834,770 B = cdsp.mdt (4,764 B) + 17 cdsp.bNN segments (7,829,493 B) + cdspr.jsn (513 B), all at corpus path xiaomi/mayfly/modem/image, priority P3, db_type COMPUTE (18) / UNKNOWN (1). This is not a census gap: the identical 19-file grammar appears on all 8 census siblings (Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro - 19 cdsp rows each), and the extract that produced this census is marked "completes" for mayfly.**

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi 12S; build codename `mayfly` | `device-inventory.csv` [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1**; the inventory soc cell is EMPTY and is corrected here from public sources | /e/OS device page (doc.e.foundation/devices/mayfly) + mainline `include/dt-bindings/arm/qcom,ids.h` (`QCOM_ID_SM8475 = 530`), accessed 2026-11-21 [F] |
| released | July 2022 (announced 2022-07-04, China) | public spec pages (2026-11-21) [F] |
| census scope | 823 device rows; cdsp = 19 rows (2.31%) / 7,834,770 B (0.564% of the 1,388,874,906 B device census) | coverage-matrix.csv + device-inventory.csv [F] |
| priority / extract | P3; `extract_status_22.2 = completes` | device-inventory.csv [F] |

## The 19 rows [F]

```
awk -F, '$1=="Mi_12S" && $4=="cdsp"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv | sort
```

| file | bytes | md5 (upstream DB) | db_type | md5 shared with (corpus-wide) |
|---|---:|---|---|---|
| cdspr.jsn | 513 | `49003ffcd10ec16dee11caad22b11b42` | UNKNOWN | 29 other devices (see fleet list below) |
| cdsp.mdt | 4,764 | `01584c41a24ea1c4708cbaf2e8416520` | COMPUTE | unique to Mi_12S |
| cdsp.b00 | 628 | `728eb7ce283e30f64cf9a20ee63818d7` | COMPUTE | Mi_12T_Pro, Poco_F5_Pro |
| cdsp.b01 | 7,464 | `3209c0463dc7ffcdeeb05b21ed67bf61` | COMPUTE | 8 devices (b01 quartet set) |
| cdsp.b02 | 1,581,865 | `3307465f9b5ffe74956e69b547f6db17` | COMPUTE | Mi_12, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| cdsp.b03 | 1,172 | `14eb07f574826b7c3504734684d29572` | COMPUTE | 8 devices (b01 quartet set) |
| cdsp.b04 | 220 | `cfc9f3b0b862325f79b50aeb3445f776` | COMPUTE | Mi_12, Mi_12_Pro, Mi_12T_Pro, Poco_F5 |
| cdsp.b05 | 2,045,572 | `5d3e437074c63f6237d07bceb8c424ca` | COMPUTE | unique to Mi_12S |
| cdsp.b06 | 160 | `1f72d439f24dd03ded61742bded7c61b` | COMPUTE | Mi_12, Mi_12_Pro, Mi_12T_Pro, Poco_F5 |
| cdsp.b07 | 2,674,696 | `d6c2a771323a1cba477b93b1b5ac9baf` | COMPUTE | unique to Mi_12S |
| cdsp.b08 | 1,552 | `0983dfca9885d44cf2ad71ed310405a3` | COMPUTE | Mi_12, Mi_12_Pro, Poco_F5 |
| cdsp.b09 | 93,460 | `6ac427c5351d7c6231cdc133f8f05a52` | COMPUTE | 8 devices (b01 quartet set) |
| cdsp.b10 | 1,285,928 | `8d61d1fca6fcac5c8400730f11908c0d` | COMPUTE | unique to Mi_12S |
| cdsp.b11 | 32,232 | `4b0465c7460d8c51832bd6aaef6bbd04` | COMPUTE | unique to Mi_12S |
| cdsp.b12 | 2,896 | `fdc5f5a759c421aad8b10b64fc05ac76` | COMPUTE | Mi_12, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| cdsp.b13 | 80,720 | `6ba66561f962d2351d3b8ec819056c9d` | COMPUTE | Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| cdsp.b14 | 4,504 | `5c3eb8e5c751cad2017d8b5abb4259f9` | COMPUTE | Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| cdsp.b15 | 12,288 | `be34bb139199359e4123264694adcbe1` | COMPUTE | 8 devices (b01 quartet set) |
| cdsp.b17 | 4,136 | `3aa3a5ef338064ac18efc23394e5ae33` | COMPUTE | unique to Mi_12S |

Sum check (python3, before writing): 17 segments = 7,829,493 B; + mdt 4,764 + jsn 513 = 7,834,770 B. sha256_if_listed is empty on all 19 rows; isa_identified empty; interface_documented = 'n'.

## Container layout

- **Grammar [F]:** cdsp.mdt + cdsp.b00..b15 + cdsp.b17 + cdspr.jsn, one directory (`xiaomi/mayfly/modem/image` - the upstream DB's path taxonomy, not necessarily the on-device path).
- **Interpretation [I]:** cdsp.mdt (4,764 B) is the ELF header + program header table of a Qualcomm signed split ELF; each cdsp.bNN is the load segment numbered by its program-header index; cdspr.jsn is the JSON region/protection-domain descriptor the PIL loader consumes alongside the image.
- **jsn is a real shipped artifact [F]:** linux-firmware WHENCE records `RawFile: qcom/sdm845/cdspr.jsn` (line 7507), `qcom/sm8250/cdspr.jsn` (7523), `qcom/qcm6490/cdspr.jsn` (7452), `qcom/x1e80100/cdspr.jsn` (7554) beside their cdsp.mbn images, with Hexagon build-chain version tags such as `CDSP.HT.2.3.c1-00076-SM8250-1` (7522). Public format notes describe the .jsn as JSON descriptors naming the protection domains the image hosts (thinkoid/artix-xps13-9345 usb-primer, accessed 2026-11-21).
- **The b15 -> b17 gap is structural, not a census omission [F]:** `awk -F, '$6=="cdsp.b16"'` over all 33,917 census rows returns 0. All 9 grammar devices share the exact 19-file set. The sibling ADSP image on mayfly shows the same pattern one index up: its 28-row set runs b00..b23 then b25 (adsp.b24 absent). Segment numbering tracks the source ELF program-header layout, so a skipped index reflects the image build, not the extractor [I].

## Cross-corpus facts

1. **cdsp.mdt is mayfly-unique [F].** No other device in the corpus carries `01584c41a24ea1c4708cbaf2e8416520`.
2. **cdspr.jsn is a two-build fleet, and mayfly rides the newer one [F].** The corpus has 60 cdspr.jsn rows in two clusters: 513 B / `49003ffc...` (30 devices) and 403 B / `f2bd80d5...` (30 devices, the older SDM660/SM6250-class generation). The 29 siblings of mayfly's cluster: Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Moto_G200, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, OnePlus_9, OnePlus_9_Pro, OnePlus_9RT, Pad_2_Pro, Pad_Pro, Phone_1, Phone_2, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro.
3. **The b01/b03/b09/b15 quartet (7,464 + 1,172 + 93,460 + 12,288 = 114,384 B) is byte-identical across exactly 9 devices** - the same set for all four segments: {Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro, Mi_12S}. SoC mapping [I]: SM8450 (cupid, zeus), SM8475 (mayfly, unicorn, thor, diting, mondrian), SM8550 (Phone_2), SM7250-AE (marble). Only mayfly's SoC was web-verified this session.
4. **cdsp.b00 (628 B) is shared by exactly the three SM8475-class devices in the census** - Mi_12S, Mi_12T_Pro (diting), Poco_F5_Pro (mondrian) [I on the SoC labels] - a per-SoC signature segment.
5. **77.2% of the family bytes are mayfly-unique [F]:** 6 files (mdt, b05, b07, b10, b11, b17) = 6,047,328 B; the 13 shared files carry 1,787,442 B. The four largest segments (b07 2,674,696 + b05 2,045,572 + b02 1,581,865 + b10 1,285,928 = 7,588,061 B) are 96.9% of the family bytes, and only b02 of them is fleet-shared.
6. **The .jsn region files are fleet-wide constant builds [F]:** mayfly's adspr.jsn (513 B, `5d262bb7661402a8d7ca9724bbb45d46`) and battmgr.jsn (516 B, `0d755b18c24337ebca8313b85f8e8a6c`) each appear on exactly 30 corpus rows - the same 30-device generation cluster as cdspr.jsn. These JSON templates ride unchanged across Xiaomi/Motorola/OnePlus/Nothing/Fairphone devices and several SoC generations [I on mechanism].

## Interface facts

- **PAS loader [F]:** mainline `drivers/remoteproc/qcom_q6v5_pas.c` maps `"qcom,sm8450-cdsp-pas"` to `sm8350_cdsp_resource`: `firmware_name = "cdsp.mdt"`, `pas_id = 18`, `minidump_id = 7` (torvalds master, fetched 2026-11-21). The driver has no sm8475-specific compatible.
- **Device tree [F]:** `arch/arm64/boot/dts/qcom/sm8450.dtsi` defines `remoteproc@32300000` (compatible `qcom,sm8450-cdsp-pas`, `memory-region = <&cdsp_mem>`) with a `qcom,fastrpc` child on glink channel `fastrpcglink-apps-dsp` exposing 8 compute-cb nodes (`compute-cb@1`..`@8`; cb9 secure, downstream-only), fetched 2026-11-21.
- **SM8475 reuses the SM8450 path [F + I]:** there is no `sm8475.dtsi` in mainline (raw fetch returns HTTP 404, 2026-11-21), but `QCOM_ID_SM8475 = 530` exists in `include/dt-bindings/arm/qcom,ids.h` and SM8475-specific PLL tables live in SM8450 clock drivers (e.g. `sm8475_gpu_cc_pll0_config` in `drivers/clk/qcom/gpucc-sm8450.c`). SM8475 boards therefore boot CDSP through the SM8450 PAS path [I].
- **linux-firmware ships no SM8450/SM8475 cdsp image [F]:** WHENCE lists only `qcom/sm8450/a730_zap.mbn` (line 7295) and `SM8450-HDK-tplg.bin` (10913) for the platform. Phone-vendor CDSP builds are device firmware; the census captures mayfly's build at `xiaomi/mayfly/modem/image`.
- **Userspace clients [F]:** the LineageOS mayfly vendor tree (`TheMuppets/proprietary_vendor_xiaomi_mayfly` mayfly-vendor.mk; `LineageOS/android_device_xiaomi_mayfly` proprietary-files.txt, fetched 2026-11-21) lists 7 cDSP fastrpc skel libraries at `vendor/lib/rfsa/adsp`: libhdr_cdsp_skel.so, libmialgo_basic_cdsp_skel.so, libmialgo_ell_cdsp_skel.so, libmialgo_ldc_cdsp_skel.so, libmialgo_night_align_cdsp_skel.so, libmialgo_rfs_cdsp_skel.so, libmialgo_slow_motion_cdsp_skel.so - the camera-pipeline CDSP clients. **None of the 7 is in the census:** mayfly's vendor/lib/rfsa/adsp census rows are 33 bm2nXX.bin modem-RF resources + 6 MiSound/hrtf audio resources (hrtf5c.bin, 5 misound_*.bin) only. The rfsa-path mislabel pattern matches the Mi_10T_5G finding (#1162 class): files labelled `adsp` because of their directory are userspace resources, not DSP OS images [I].
- **ISA/interface documentation status [F]:** isa_identified empty and interface_documented = 'n' on all 19 rows - honestly un-RE'd. No in-repo or public reverse engineering of this cdsp build exists (web + GitHub code searches, 2026-11-21).

## Honest negatives

- No payload access: the ELF program-header layout, the signing/MBN container version, and the CDSP build tag (the `CDSP.HT.x.y` version-string pattern WHENCE records for board SoCs) are [OPEN]. The census records md5/size/path only.
- The missing cdsp.b16: mechanism [OPEN] (ELF program-header layout [I]). Its corpus-wide absence across all 9 grammar devices makes an extraction fault unlikely.
- Physical partition mapping [OPEN]: the LineageOS mayfly tree ships `dsp.img;AB` and `modem.img;AB` as partition images and lists no individual cdsp blobs, so the cdsp set rides inside one of them (dsp.img is the likely carrier [I]). The census path `xiaomi/mayfly/modem/image` is the upstream DB's taxonomy, not the on-device path.
- The 7 vendor/lib/rfsa/adsp cDSP skel libraries are outside the census [OPEN]; they need a vendor-blob census pass.
- Hashes are upstream-DB md5s (`md5_db`); no sha256 is recorded for any of the 19 rows [F].

## What would upgrade this finding

1. Payload fetch (mayfly fastboot dsp image or a LineageOS package): parse cdsp.mdt program headers to confirm the segment/index map and the b16 story; read the build tag and confirm the Hexagon version.
2. Byte-level diff of the 9-device shared quartet (b01/b03/b09/b15) across cupid/mayfly/Phone_2 to test whether shared md5 means shared code modules or common tooling output.
3. Census pass over the vendor rfsa bucket (the 7 cdsp skels) - one decode would cover the whole Xiaomi 12-series fleet, since the skels may span the same 9-device set.

## RULE 0 record (2026-11-21)

Queries recorded in the SEARCH + DELTA comments on this issue. Check: GitHub code search `"sm8475-cdsp-pas"` and `"mayfly" "cdsp.mdt"` (adineo-cmd excluded) -> 0 results; web `"mayfly" Xiaomi 12S "cdsp" firmware` / `"cdspr.jsn" "cdsp.mdt" format` -> generic Qualcomm split-ELF knowledge only; torvalds `qcom_q6v5_pas.c` + `sm8450.dtsi` + linux-firmware WHENCE fetched 2026-11-21. Nobody documents the Mi_12S cdsp census; no prior device-level reverse engineering exists.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata (sizes, md5s, counts, paths) plus public sources.
