# motorola Moto_G10 (capri) - `other` family status (44 rows - PRESENT as the residual catch-all across 5 locations; 8 clusters, 38,814,675 B, 44 distinct md5s with zero internal duplication, 24 corpus-unique rows; the venus b11-b18 gap is STRUCTURAL per the public venus-6.0/qcm2290-venus build; fngap64 is the QSEE fingerprint TrustZone app in a 64-bit split layout)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1264](https://github.com/adineo-cmd/open-device/issues/1264)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site c717d6b), `upstream-contribution/blob-database/device-inventory.csv`, the sibling doc docs/devices/motorola/Moto_G10/adsp.md (#1258, cited not re-derived), the in-repo fleet docs research/fleet/other-media.md (#2058) and research/fleet/other-audio.md (#2052), sibling `other` docs docs/devices/xiaomi/Mi_13/other.md (#1228), docs/devices/xiaomi/Mi_A3/other.md (#1246), docs/devices/samsung/Galaxy_Tab_A7_Wifi/other.md (#1120), LineageOS `android_device_motorola_capri` `proprietary-files.txt` (lineage-22.2, raw.githubusercontent, fetched 2026-11-21, header "All unpinned blobs below are extracted from capri_retail RRB31.Q1-3-48-24"), moto-sm4350/android_device_motorola_pnangn `recovery/bin/load_touch.sh` and CalyxOS/scripts `factory/hawao/flash-base.sh` (raw.githubusercontent, fetched 2026-11-21), nyl/linux-qseecom-mobile (tz-qsee-fingerprintd README + plugins/fp4_icnf7312/README.md) and nyl/device-firmware-blobs readme.md (fetched 2026-11-21), torvalds/linux master `drivers/media/platform/qcom/venus/core.c` and `arch/arm64/boot/dts/qcom/sm6115.dtsi` (fetched 2026-11-21), linux-firmware WHENCE (git.kernel.org, fetched 2026-11-21) plus the shipped public build `qcom/venus-6.0/venus.mbn` (git.kernel.org, fetched and ELF-parsed 2026-11-21), and public spec pages (GSMArena, 2026-11-21). No device payload was fetched or committed; the only binary inspected is the public linux-firmware venus-6.0 build, parsed for ELF header metadata only. Every number is command output or a recorded fetch; sums re-verified with python3 -I this session.

**Verdict: the `other` family is PRESENT on Moto_G10 and the census is COMPLETE for what the matrix grammar captures - 44 rows, 38,814,675 B, 44 distinct md5s (zero internal duplication), 24 corpus-unique rows, all P3, spread over 5 locations.** The family is the census remainder (research/soc/per-soc-method-plans.md: "other (rest - the upstream UNKNOWN tail)"): it decomposes into 8 clusters - the radio partition image trio (3 rows, 86.45% of family bytes), the `fngap64` QSEE fingerprint TrustZone app as a complete 9-row 64-bit split-PIL set (8.16%), the `venus` video firmware as a complete 13-row split set whose b11-b18 absence is STRUCTURAL - proven against the public `qcom/venus-6.0/venus.mbn` build whose program headers 11-18 all carry p_filesz 0 (1.96%), `Data.msc` + the orphaned `scuba_ipa_fws.mdt` (2 rows), the `djn_novatek` touchscreen firmware pair (2 rows), the WCN3950-branch `cm*` Bluetooth set (7 rows), the Awinic AW882XX speaker-amp trio (3 rows) and 5 camera calibration rows (542 B). One recorded census divergence: the LineageOS capri manifest lists `dual_golden_{depth,ov8856_wide,wide}.bin` and `vidhance_calibration` in vendor/etc/camera with zero rows anywhere in the 33,917-row corpus.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Moto G10, XT2127 | public spec pages (GSMArena, fetched 2026-11-21) [F]; sibling doc #1258 [F] |
| codename | `capri` (db_path and inventory agree) | coverage-matrix.csv + device-inventory.csv [F]; LineageOS wiki capri page (via #1258) [F] |
| SoC | Qualcomm **SM4250 Snapdragon 460** (11 nm), Adreno 610; video core bound in mainline as `qcom,qcm2290-venus` | inventory cell [F]; GSMArena (2026-11-21) [F]; sm6115.dtsi lines 1856-1858 [F]. **The inventory SoC cell is CORRECT for this device** - unlike the known-wrong dubai/tundra cells |
| stock build | `capri_retail RRB31.Q1-3-48-24` | LineageOS capri proprietary-files.txt header (fetched 2026-11-21) [F] |
| census scope | 211 rows in 9 families: `other` 44 (largest), modem 43, wifi 40, adsp 35, gpu 14, bt 11, cdsp 11, boot 8, tz 5 | coverage-matrix.csv, python-verified this session [F] |
| priority | P3 on all 44 rows | coverage-matrix.csv [F] |

## Where the family lives and the census grammar [F]

| db_path | rows | bytes |
|---|---|---|
| `motorola/capri/radio` (partition images) | 3 | 33,939,456 |
| `motorola/capri/modem/image` (firmware mount) | 24 | 4,560,043 |
| `motorola/capri/bluetooth/image` | 7 | 72,850 |
| `motorola/capri/vendor/firmware` | 5 | 241,784 |
| `motorola/capri/vendor/etc/camera` | 5 | 542 |
| total | 44 | 38,814,675 |

Subfamily split: misc 23 rows / 38,050,345 B; media 13 / 759,572; camera 5 / 542; audio 3 / 4,216 (python-verified, this session). Cluster sums equal the subfamily sums and the total. All 44 rows have `isa_identified` EMPTY, `interface_documented=n`, `sha256_if_listed` EMPTY. Recorded db_type pattern: mdt/monolith rows carry `ELF64`, segment rows carry `CELL` or `UNKNOWN` - including `venus.mdt` = `ELF64`, which the public-build parse below contradicts (the venus container is ELF32); flagged for the lead.

Grammar note: the lab's method-plan sketch files `venus` under a dsp-audio family (per-soc-method-plans.md family list), but the matrix files every `venus.*` row corpus-wide (371 rows) under `other`/`media` - the matrix implementation, not the sketch, is what the corpus shows [F].

## Cluster A - radio partition image trio (3 rows, 33,939,456 B, 86.45%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| dsp.img | 33,554,432 | `ee07183eb3df3b229ad137537e918aa7` | 1 (corpus-unique) |
| prov.img | 258,048 | `fb8c9a3c2a35a9c2e3d7b7f93ddadfbb` | 1 (corpus-unique) |
| storsec.img | 126,976 | `620710cca5e8131984154958a4a89114` | 1 (corpus-unique) |

- All three are Motorola radio-package partition images flashed to A/B partitions by the standard factory flash flow: CalyxOS/scripts `factory/hawao/flash-base.sh` (hawao = the SM4250-generation Moto sibling per the matrix db_paths) runs `fastboot flash storsec_a/b storsec.img`, `flash prov_a/b prov.img`, `flash dsp_a/b dsp.img` (fetched 2026-11-21) [F].
- Corpus span: `dsp.img` exists on 61 devices - exactly 32 MiB (33,554,432) on the SD425/SM6115/SM6225/SM6375 generation and 64 MiB on the SD7xx/SM8xx generation; `prov.img` on 21 devices (258,048 B on this generation, 262,144 B on 695/8550-gen devices); `storsec.img` on 28 devices (126,976 B here vs 131,072 on 695-gen, 24,576 on OnePlus 7-gen, 20,480 on Mi_A3) [F]. Every device's bytes are its own build (all corpus-unique per device) [F].
- Content: not verifiable from the census (one opaque 32 MiB image, no payload fetched). The Qualcomm `dsp` partition is the DSP system object slot in public packaging conventions [I]; capri's own adsp2/cdsp files ship in the modem firmware mount per the census (#1258 + the cdsp family), so which subsystems capri's dsp.img carries is [OPEN].

## Cluster B - `fngap64`, the QSEE fingerprint TrustZone app (9 rows, 3,165,489 B, 8.16%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| fngap64.mdt | 7,464 | `1dbb06a7a411eb5dedb69f79afc2dc8d` | 1 (corpus-unique) |
| fngap64.b00 | 512 | `8ee479d04b64f5910e1ffa934a41c7da` | 3 (Moto_G10, Moto_G30, Moto_G9_Power) |
| fngap64.b01 | 6,952 | `b02c26f79513df4ce1dc9095a8e445d8` | 1 (corpus-unique) |
| fngap64.b02 | 2,621,656 | `be667a5fc77b459b91cdf0db90ae31ba` | 1 (corpus-unique) |
| fngap64.b03 | 264 | `3ceb3cbd48cfcb5f5582a4300ceb98da` | 3 (same trio) |
| fngap64.b04 | 403,112 | `f637670d6acb979c5bb14b72aa2f0f08` | 3 (same trio) |
| fngap64.b05 | 1,728 | `eeede038681661c4ecc57c6fe0749591` | 3 (same trio) |
| fngap64.b06 | 304 | `897fb22825e714f3cf55a6e454e8e0f9` | 3 (same trio) |
| fngap64.b07 | 123,497 | `cdea27f6b0ab98b8c21a9337ec43529c` | 3 (same trio) |

- Identity (public prior art, cited not re-derived): `fngap64` is the QSEE fingerprint TrustZone application. nyl/linux-qseecom-mobile `tz-qsee-fingerprintd/plugins/fp4_icnf7312/README.md` (fetched 2026-11-21): "**TrustZone TA:** `fngap64` (`TCL_T2MFP4_qsee5.10_SM7225_android12_ca64bit_icnf7312`, loaded as `"fingerprint"`)" - the FP4 instance documents the full TCI command surface (IDs 0x00-0x23, 16-byte transport header, 64 KiB shared buffer, Pangu R60C matching algorithm). nyl/device-firmware-blobs readme.md: "`fingerprint.mdt`/`fingerprint.b00`-`b07`: Chipone ICNF7312 TrustZone Application (QSEE `fngap64`) required by tz-qsee-fingerprintd". LineageOS `android_device_vsmart_casuarina` `proprietary-files.txt` lines 398-405 ship `fngap64.b00-b06` + mdt (fetched 2026-11-21). The name spans SDM660-era vsmart through SM7225 FP4 to the Moto SM4250/SM6115/SM6225 fleet [F].
- **Container layout [F arithmetic + public anchor]:** capri's set is a complete 9-row split image: mdt = b00 + b01 exactly (512 + 6,952 = 7,464), and `fngap64.b00` 512 = 64 + 8 x 56 - the exact size of an ELF64 header (64 B) plus 8 program header entries (56 B each); the ELF32 reading (52 + 32n = 512) has no integral solution ((512-52) = 460, not divisible by 32). So **capri's fngap64 is an ELF64 image with e_phnum = 8**, matching the census db_type=ELF64 on the mdt/b00 rows and the `ca64bit` (TA 64-bit) marker in the public FP4 build string [I for the generational tie]. The same arithmetic holds on FP4 (b00 512, b01 6,800, mdt 7,312 = 512 + 6,800) [F].
- Metadata-segment algebra [I, applying the #2058/pil-metadata-sweep decomposition]: capri b01 6,952 = 168 + 48x8 + 256 + 6,144 (48x8 = 384 hash table over 8 phdrs, RSA-2048 signature, one 6,144 B cert chain); FP4 b01 6,800 = 168 + 384 + 104 + 6,144 (ECDSA P-384 signature). The two builds differ only in signature scheme and payload.
- Corpus span: 54 rows on 6 devices, all at `<codename>/modem/image` (fairphone/FP4, motorola/capri, motorola/caprip, motorola/hawao, motorola/cebu, motorola/denver per the matrix db_paths) [F]. Six of nine capri files (b00, b03-b07) are byte-identical across Moto_G10/Moto_G30/Moto_G9_Power; the mdt, b01 and the 2.6 MB b02 body are build-local [F].
- Interface [F manifest + I]: capri's LineageOS manifest ships two fingerprint HAL services - `android.hardware.biometrics.fingerprint@2.1-service-chipone` (+ `chipone.fingerprint.default.so`) and `android.hardware.biometrics.fingerprint@2.1-service-fpc` (+ `fpc_ident`) (manifest lines 195-204, fetched 2026-11-21) - so the trustlet serves Chipone- and FPC-sensor SKUs; which sensor the census build pairs with is not resolvable from the corpus [OPEN].

## Cluster C - `venus` video-firmware split set (13 rows, 759,572 B, 1.96%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| venus.mdt | 8,220 | `75205fafbbe4379595b400874739117b` | 1 (corpus-unique) |
| venus.b00 | 692 | `44e732b8a534f4afd7021f06c643534a` | 1 (corpus-unique) |
| venus.b01 | 7,528 | `ecf3e76298d637b3492c92b01f3adaf4` | 1 (corpus-unique) |
| venus.b02 | 292 | `2746cf08734c75797ba340d104d359c1` | 1 (corpus-unique) |
| venus.b03 | 20 | `4344e840708282eccd554f7d244c7e63` | 23 |
| venus.b04 | 20 | `708526c534436558ffd10ed1fdd5c86e` | 1 (corpus-unique) |
| venus.b05 | 20 | `f05c4f03a9283589091c31be065c6fed` | 30 |
| venus.b06 | 20 | `d81a5c71adbe6aae61e4b4a8e121e446` | 30 |
| venus.b07 | 24 | `eb667b725e1602ba8b9300293a4a2272` | 30 |
| venus.b08 | 16 | `ec2d6ced2030acafa2b680b83eb3ab63` | 30 |
| venus.b09 | 686,672 | `101b417410540b7d5ae0cb35261f2d99` | 1 (corpus-unique) |
| venus.b10 | 56,016 | `35e47445699b32b5cad415037d4f7057` | 1 (corpus-unique) |
| venus.b19 | 32 | `0d68af0904dd698b16ffc9cd28b9b0c8` | 34 |

- **The b11-b18 absence is STRUCTURAL, not a census gap.** Four lines of evidence: (1) size laws [F arithmetic]: mdt = b00 + b01 exactly (692 + 7,528 = 8,220) and b00 = 52 + 20 x 32 - an ELF32 header plus 20 program header entries, so **e_phnum = 20**; the shipped set is exactly {mdt, b00..b10, b19} = 13 rows, i.e. phdrs 0-19 minus phdrs 11-18. (2) Public generational witness [F, parsed this session]: linux-firmware `qcom/venus-6.0/venus.mbn` (WHENCE line 7120, Version VIDEO.VE.6.0-00055-PROD-1, 1,794,924 B, md5 `b7f437a33adbb851e75099293d0b35e1`) parses as ELF32 LE, e_machine **94 (EM_XTENSA)**, e_entry 0xf500000, e_flags 0x300, **e_phnum 20**, phdr 0 = PT_NULL p_filesz 692 (header table = capri's b00 size exactly), phdr 1 = PT_NULL p_filesz 7,376 (metadata segment), phdrs 2-8 p_filesz = 292/20/20/20/20/24/16 - **capri's b02-b08 sizes exactly, all seven** - phdr 9 = 689,760 B code, phdr 10 = 56,144 B data, **phdrs 11-18 all p_filesz 0** (phdrs 11/13/15/17 also p_memsz 0; phdrs 12/14/16/18 BSS-only with p_memsz 23,968/16,384/8,192/4,165,632), phdr 19 p_filesz 32 (= capri's b19 size). A p_filesz-0 PT_LOAD produces no `.bNN` file under the split convention (torvalds/linux `drivers/soc/qcom/mdt_loader.c` requests segments only when p_filesz > 0, lines 413-423, per #1258) - so no venus.b11..b18 files exist to census. (3) Corpus sweep [F]: all 34 devices carrying `venus.*` (371 corpus rows) show the identical 13-row shape or the older 5-row shape (b00 212 = 52 + 5 x 32, e_phnum 5, on Mi_A3/OnePlus 7-generation ARM9-era builds); zero `venus.b11`..`venus.b18` rows exist anywhere in the 33,917-row corpus. (4) In-repo prior measurement [F, #2058 sec 4.5]: on actual venus/cvpss files the metadata hash table has zero entries exactly at indices {1, 11, 12, 13, 14, 15, 16, 17, 18}, the hash-zero rule hash[i] = 0 iff i = 1 or phdr[i].p_filesz = 0.
- ISA [F]: the venus container is e_machine 94 = EM_XTENSA (public build parsed this session; #2058 measured the same on SM8250 venus/cvpss and corrected the repo's earlier "RISC-V" claim). The mainline driver groups this generation's reset path with the Xtensa XTSS branch: `qcom,qcm2290-venus` (sm6115.dtsi lines 1856-1858 - the compatible capri's SM4250 binds to) maps to `qcm2290_res` with `.vpu_version = VPU_VERSION_AR50_LITE`, `.fwname = "qcom/venus-6.0/venus.mbn"`, HFI 4XX, min_fw 6.0.55 (venus-core.c lines 1200-1233, fetched 2026-11-21), and the reset check `IS_IRIS2(core) || IS_IRIS2_1(core) || IS_AR50_LITE(core)` (venus-core.c line 260) selects the XTSS reset per #2058 sec 2.3. No disassembly was performed; the ISA verdict rests on the e_machine byte and the kernel's reset path, not on decoded instructions [I on the generational extension to capri's own bytes].
- Metadata algebra [I]: capri b01 7,528 = 168 + 48x20 + 256 + 6,144 (RSA-2048-signed metadata over 20 phdrs); the public build's phdr 1 = 7,376 = 168 + 960 + 104 + 6,144 (P-384 variant) - the same signature-scheme split #2058 records (sec 4.4) and the reason capri's mdt (8,220) differs from public-build devices' mdt (8,068 = 692 + 7,376, carried by FP4/Nord_CE2/Nord_CE3/Realme_9_Pro/Realme_10_Pro per the corpus) [F row sizes].
- Sharing: the tiny segments are fleet-wide constants - b05/b06/b07/b08 byte-identical on 30 devices, b03 on 23, b19 on 34 (and the same 32 B identity appears under the names venus.b04 on 5-phdr builds and vpu20_1v/4v.b19 on VPU devices; #2058 measured it as 0x0dd0adde repeated eight times) - while b00/b01/b02/b04/b09/b10/mdt are capri-build-local [F]. The b09 686,672 B code segment is capri's largest non-radio payload in this family.

## Cluster D - modem/image misc singles (2 rows, 634,982 B)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| Data.msc | 627,962 | `075e65d62a49db0f5055101b3bfbdda7` | 1 (corpus-unique) |
| scuba_ipa_fws.mdt | 7,020 | `c83238eac8d904b7cbd50574454ab876` | 1 (corpus-unique) |

- `Data.msc` sits in the modem firmware mount across 54 corpus devices (627,835-1,769,820 B range; capri 627,962). Its role is not publicly documented; the sibling doc #1228 carries an EFS/NV-container hypothesis [I] and public device trees place it in `/vendor/firmware_mnt/image` alongside WLAN/modem firmware [I from web search 2026-11-21]. Honest status: hypothesis only, no format facts.
- `scuba_ipa_fws.mdt` is a **classification orphan**: its five segment files (b00 212, b01 6,808, b02 12,040, b03 128, b04 320) sit in the `modem` family with db_type=CELL while the mdt alone fell into `other` with db_type=ELF64 [F]. Inside Moto_G10 the scuba set is byte-comparable to the `ipa_fws` set (modem family): b00/b02/b03/b04 md5-identical, b01/mdt differ at identical sizes 6,808/7,020 - a re-metadata'd build of the same IPA firmware under the scuba name [F md5s]. `scuba` is the SM6115 platform codename and the Moto SM6115 fleet carries the same 6-row shape (#1120, established); the Samsung Tab A7 carries an mdt-only 6,868 B variant [F, #1120].

## Cluster E - `djn_novatek` touchscreen firmware (2 rows, 237,568 B, 0.61%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| djn_novatek_ts_fw.bin | 118,784 | `23c8923d0881aa62194b88fe243958bf` | 1 (corpus-unique) |
| djn_novatek_ts_mp.bin | 118,784 | `d5b62d1d07d32721fd3492dd45fa7158` | 1 (corpus-unique) |

- Interface [F, public]: moto-sm4350/android_device_motorola_pnangn `recovery/bin/load_touch.sh` (fetched 2026-11-21) reads `/sys/class/touchscreen/*/panel_supplier` and, for `tianma`, selects `djn_novatek_ts_fw.bin` and reflashes via sysfs (`forcereflash`/`doreflash`) - so djn_novatek_ts_fw.bin is the Novatek touch-controller firmware for the Tianma panel on Moto's capri-family generation.
- The capri LineageOS manifest lists both files at vendor/firmware plus recovery copies (lines 291-292, 298-299) alongside Novatek MP criteria tables `NT36xxx_MP_Setting_Criteria_601D.csv`/`602B.csv` (lines 289-290) and Ilitek firmware for alternate panels (lines 286-288) [F, fetched 2026-11-21]. The sibling Moto_G30 census names its variant `djn1_nt36525c_novatek_ts_{fw,mp}.bin` (118,784 B each) - the NT36525C controller [F from the filename]; capri's own filename carries no IC number, so the exact NT36xxx variant is [OPEN]. The ts_fw/ts_mp pair is same-size with different bytes [F]; mp reads as the mass-production variant [I].
- Corpus: 4 rows on 2 devices (Moto_G10, Moto_G_Power), same sizes, per-device bytes [F].

## Cluster F - `cm*` WCN3950-branch Bluetooth firmware (7 rows, 72,850 B, 0.19%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| cmbtfw10.tlv | 4,803 | `505051a52545bffe76082c82adda3147` | 14 |
| cmbtfw11.tlv | 14,247 | `8ec02ba2343140c0d155ea251ef416ac` | 14 |
| cmbtfw12.tlv | 46,467 | `edcee241b8f989407356ff13da49e175` | 1 (corpus-unique) |
| cmbtfw12.ver | 33 | `eec5b2c0368f2fad927032620ec4671f` | 1 (corpus-unique) |
| cmnv10.bin | 2,034 | `2dceb768ace4075997b5ebfcccd14bc8` | 14 |
| cmnv11.bin | 2,676 | `c22408ff6a58959d28a3a2ec4b35b024` | 14 |
| cmnv12.bin | 2,590 | `761e638c1fbfd96be3f05a7c62e9334a` | 2 (Moto_G10, Moto_E7_Plus) |

- Chip identity [F, established per-soc-method-plans.md, verified against mainline btqca.c case labels]: `cmbtfw*` = WCN3950. linux-firmware WHENCE lists the mainlined siblings under "Driver: qca - Qualcomm Atheros Bluetooth support for WCN3950 chips" (lines 5345-5352, fetched 2026-11-21): `qca/cmbtfw12.tlv` (Version BTFM.CMC.1.2.0-00218-QCACHROMZ-2), `qca/cmbtfw13.tlv` (BTFM.CMC.1.3.0-00184-QCACHROM-1), `qca/cmnv12.bin` + cmnv13 variants. #1246 carries the same citation for Mi_A3; this cluster is the Moto twin of that finding, not a re-derivation.
- Why they are in `other`: the bt family grammar captured the `cr*` (WCN3990/3991/3998) and `ap*` (WCN3988) prefixes (Moto_G10's bt family: crbtfw11/20/21, crnv11/20/21, apbtfw10/11, apnv10/11) while `cm*` fell through to the residual family [F]. capri therefore ships **three** Qualcomm combo-BT chip firmware branches at once [F, grammar artifact worth a lead flag].
- Sharing: the 10/11 builds are byte-identical across 14 devices spanning 9 vendors and 5 SoC generations (Defy_2021, Mi_A3, Moto_E7_Plus, Moto_G9/G10/G30/G32/G42/G52/G9_Power/G_Power/G_Stylus_5G, Phone_1, Pro_1X - python-verified roster at c717d6b; #1246's roster adds Moto_G_5G_2024, recorded at an earlier matrix state); cmbtfw12.tlv is a 46,467 B device-local build (E7_Plus 44,895, G30 47,755, G32/G42/G52 47,307 = the mainline WHENCE size class per #1246) and cmbtfw12.ver (33 B) is a version-record file only Moto devices carry [F]. cmnv12.bin is shared only with Moto_E7_Plus - the two SM4250 twins [F].

## Cluster G - Awinic AW882XX speaker-amp firmware (3 rows, 4,216 B, 0.01%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| aw882xx_mono.bin | 2,036 | `a8f82ec066e179afc2abe1ca9b47a645` | 1 (corpus-unique) |
| aw882xx_mono_power.bin | 2,036 | `aba4d90c57402b9a2304bc591747b9ef` | 1 (corpus-unique, only row of this filename corpus-wide) |
| aw882xx_spk_reg.bin | 144 | `4c4315f5fd6cb18898a382d26de677e0` | 15 |

- The capri manifest lists all three at vendor/firmware (lines 24-26, fetched 2026-11-21) [F]. Awinic AW882XX smart-amp configuration/calibration per #2052 (the fleet audio doc: 36 Awinic devices vs 44 Cirrus, zero overlap; mainline parses Awinic ACF files via aw88395_lib.c; the Moto mono/spk_reg naming is the downstream Awinic-SDK driver's file set) [F + I].
- aw882xx_spk_reg.bin (144 B) is a fleet-wide byte-constant on 15 devices, all of them Moto-family (Defy_2021, Edge_2021/30/30_Fusion, Moto_E7_Plus, Moto_G10/G200/G30/G32/G42/G52/G9/G9_Power/G_Power/G_Stylus_5G) [F]; the two 2,036 B mono calibration files are capri-local builds (Moto_G30 carries a same-size mono with different bytes) and mono_power is G10-only corpus-wide [F].

## Cluster H - camera calibration (5 rows, 542 B, 0.00%)

| file | bytes | md5 | devices sharing |
|---|---|---|---|
| dc_mot_ov8856.bin | 256 | `b87551bcb34928fcb3dabbf823997675` | 2 (Moto_G10, Moto_G30) |
| arcsoft_calibration_u_dc.bin | 256 | `3a510b98a69ff9391d5d1bd223eacbf0` | 7 |
| aec_golden_wide.bin | 10 | `32cb197a4bcddc9e19cd014d64d0ec6e` | 1 (corpus-unique) |
| aec_golden_ov8856_wide.bin | 10 | `bcc4bbf3e478129252a8942c710a16e8` | 1 (corpus-unique) |
| aec_golden_depth.bin | 10 | `666c333183ef7441aec80467df184a4c` | 1 (corpus-unique) |

- The five census rows match the capri manifest's vendor/etc/camera entries lines 175-179 one-to-one (fetched 2026-11-21) [F].
- Sensor context [F from the manifest]: capri's camera set includes `com.qti.sensor.mot_ov8856.so`, `com.qti.tuned.mot_capri_ov8856.bin` and `com.mot.eeprom.mot_gt24p64e_ov8856_eeprom.so` - the ov8856 is the wide camera, matching the `aec_golden_ov8856_wide.bin` naming; `arcsoft_calibration_u_dc.bin` is Arcsoft-partner calibration, 256 B byte-identical across 7 Moto devices (Edge_2021/30, G10/G30/G42/G52, G_Stylus_5G) [F]. The `dc_mot_` prefix and the exact role of each golden bin are not publicly documented [OPEN].
- **Recorded census divergence:** the manifest also lists `dual_golden_depth.bin`, `dual_golden_ov8856_wide.bin`, `dual_golden_wide.bin` and `vidhance_calibration` in vendor/etc/camera (lines 180-183) with **zero rows anywhere in the 33,917-row corpus** (awk sweep, this session) [F]. Either the corpus harvest predates/excludes these files or the matrix filters them out; unresolved, [OPEN].

## Cross-corpus facts

- The family is a residual catch-all, not a coherent firmware family: its clusters span five unrelated subsystems (radio partitions, QSEE TA, video PIL, BT, touch, amp, camera calibration) and five locations [F].
- 24 of 44 rows are corpus-unique; the 20 shared rows split into fleet-wide constants (venus tiny segments on 23-34 devices, aw882xx_spk_reg on 15, cm* 10/11 builds on 14), a Moto trio share (fngap64 b00/b03-b07 on G10/G30/G9_Power), the E7_Plus pair (cmnv12.bin), and the G30 pair (dc_mot_ov8856.bin) [F].
- capri's `other` is the largest family on the device (44 vs modem 43) [F]; the SM4250 twin Moto_E7_Plus carries the same clusters with build-local bytes (Data.msc 627,835 vs 627,962; cmbtfw12.tlv 44,895 vs 46,467; aw882xx_mono 1,536 vs 2,036) [F].
- Sibling contrast: Moto_G30 (SM6115, matrix db_path codename `caprip` - capri/caprip are the SM4250/SM6115 siblings of the same Kryo 240 generation [I]) adds a `tbase.*` TrustZone set and cmnv13/cmbtfw13 builds that capri lacks, and names its novatek files djn1_nt36525c_* [F].

## ISA and interface facts

- venus: Xtensa (EM_XTENSA 94) per the parsed public build and #2058; kernel reset path XTSS for this generation (AR50_LITE grouped with IRIS2/IRIS2_1, venus-core.c line 260) [F].
- fngap64: 64-bit TrustZone application (ELF64 arithmetic on capri's own b00; `ca64bit` in the public FP4 TA build string). The FP4 public instance runs on the applications processor under QSEE with a documented TCI command surface (0x00-0x23) and the Pangu R60C matching algorithm [F public prior art]; capri's own TA bytes were not inspected - the target ISA of its executable segment is AArch64 per the TA class [I], no disassembly performed.
- cm* TLVs: Qualcomm combo-chip firmware in the TLV format the mainline btqca driver downloads to WCN3950 controllers; no format decode beyond the driver's handling [F for the driver interface, N for the format].
- aw882xx/camera bins: calibration/configuration data for the Awinic amp DSP and the camera HAL (Arcsoft/CamX stack), not executable firmware [I].
- prov.img/storsec.img/dsp.img: recorded db_type ELF64 [F cell]; the ELF class of the device files was not verified (no payload fetched) [N].
- The census records `isa_identified` EMPTY and `interface_documented=n` on all 44 rows - honestly un-RE'd at row level; this doc's interface facts come from public trees, not from the blobs [F].

## Honest negatives ([OPEN])

- No payload of this device was fetched or analyzed (metadata-only; all 44 files exist in the corpus as hashes only). The only binary touched was the public linux-firmware `qcom/venus-6.0/venus.mbn`, and only its ELF header table.
- capri's venus phdr-level facts (e_phnum 20, phdrs 11-18 file-data-less) are derived from exact size laws plus the public generational witness whose phdrs 2-8 match capri's seven smallest segment sizes - not from capri's own mdt bytes. A program-header dump of the real `venus.mdt`/`fngap64.mdt` (expect venus: ELF32 e_phnum 20, phdr11-18 p_filesz 0; fngap64: ELF64 e_phnum 8) remains the direct proof and is [OPEN].
- capri fngap64 sensor pairing (Chipone vs FPC SKU) and TA build string are unknown; the FP4 public instance is a different device's build.
- dsp.img content is unverified; its relationship to the modem-partition adsp2/cdsp files (#1258 + the cdsp family) is [OPEN].
- Data.msc's role is a hypothesis (EFS/NV container per #1228 [I]); no public format documentation exists.
- The `djn` prefix, `dc_mot_` prefix, and the exact NT36xxx IC variant on capri are unexpanded.
- The dual_golden_*/vidhance_calibration corpus absence is unexplained (harvest scope vs matrix filter) [OPEN].
- The `venus.mdt` db_type=ELF64 cell conflicts with the ELF32 public-build parse and the exact 52+20x32 arithmetic - census detection error or a non-ELF-class meaning of the field; flagged for the lead [F tension].
- No Xtensa/AArch64 disassembly was performed; no ISA claim rests on decoded instruction bytes.

## What would upgrade this finding

1. Extract the stock radio partitions (dsp/prov/storsec images) and modem partition, byte-verify all 44 census md5s, and dump the ELF header tables of `venus.mdt` (8,220 B) and `fngap64.mdt` (7,464 B) - that converts both structural [I]s into direct [F]s.
2. Byte-compare capri's `cmbtfw12.tlv` (46,467 B) against pinned linux-firmware `qca/cmbtfw12.tlv` releases to date the device's WCN3950 build.
3. Dump the 32 MiB `dsp.img` filesystem to settle what the radio `dsp` partition carries on capri.
4. Trace the `dual_golden_*`/`vidhance_calibration` harvest exclusion and the `venus.mdt` db_type=ELF64 detection in the census builder.
5. RE the `cm*` TLV container against the mainline btqca download flow and record the WCN3950 command grammar.

## RULE 0 record

- CLAIM posted 2026-11-21T10:52:20Z as the first comment (confirmed first by re-read; no other agent claimed).
- SEARCH (Gate -1) posted 2026-11-21; DELTA (Gate 0) posted 2026-11-21; work started only after both.
- All census numbers are python3 -I/awk outputs on coverage-matrix.csv at feat/open-device-site c717d6b (33,917 data rows), this session; all web fetches dated 2026-11-21 with paths and WHENCE line numbers recorded; the venus-6.0 ELF parse was stdlib python3 -I on the downloaded public file (hash and header fields only).

Nothing in this document is legal advice; no proprietary payload bytes were fetched, stored or committed - only sizes, md5s, ELF header metadata of a public build, public-source quotations and arithmetic derivations.
