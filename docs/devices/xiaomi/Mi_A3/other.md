# xiaomi Mi_A3 - `other` family status (122 rows - PRESENT, residual catch-all across 5 locations; 8 groups, python-verified sums, 122 distinct md5s with zero internal duplication, 106 corpus-unique rows, SD665-era modem/image misc trustlets incl. the Goodix FOD trustlet gfcep, WCN3950-branch Bluetooth set with mainlined siblings, 32 MiB dsp partition image)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1246](https://github.com/adineo-cmd/open-device/issues/1246)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site worktree at 2a338f1), `upstream-contribution/blob-database/device-inventory.csv`, the sibling doc docs/devices/xiaomi/Mi_13/other.md (issue [#1228](https://github.com/adineo-cmd/open-device/issues/1228) - the SM8550-generation `other` grammar, cited not re-derived; its roster comparisons carry the Mi_12/#1174, Mi_12S_Pro/#1192 and Mi_12T_Pro/#1210 findings), the LineageOS `android_device_xiaomi_laurel_sprout` `proprietary-files.txt` (lineage-22.2, raw.githubusercontent, fetched 2026-11-21), linux-firmware WHENCE (git.kernel.org, fetched 2026-11-21) plus Content-Length probes of qca/cmbtfw12.tlv and qca/cmnv12.bin (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm6125.dtsi` (torvalds master, fetched 2026-11-21), public QTI kernel trees carrying the `qcom,img-filename = "cpe_9340"` WDSP node and Pixel/HTC vendor manifests carrying the same trustlet/segment names (GitHub code search, 2026-11-21), a public Xiaomi dmesg gist proving `QSEECOM: qseecom_load_app` runtime loads of these trustlet names (gist.github.com/grimpy/e7b38dc72944163582146b0d70a4bc47, fetched 2026-11-21), the XDA official-fastboot-ROM thread for Mi A3 (xdaforums.com/t/rom-official-fastboot-xiaomi-mi-a3-laurel_sprout.3962489, web search 2026-11-21), LineageOS wiki firmware-update templates flashing storsec.img (GitHub code search 2026-11-21) and public spec pages (GSMArena, Wikipedia, 2026-11-21). No payload fetched by this issue; every number below is command output verified with python3 (`python3 -I`, this session).

**Verdict: the `other` family is PRESENT on Mi_A3 and is the residual catch-all of the 326-row census - 122 rows, 43,947,746 B (13.26 percent of the device census bytes), 122 distinct md5s with zero internal byte-duplication, spread over 5 locations.** It decomposes into 8 groups: 9 modem/image misc split-PIL trustlet sets (81 rows, mdt + b00..b07 each, 6,652,954 B) including the 5,683,239 B Goodix fingerprint trustlet `gfcep`, the venus video-codec split-PIL set (6 rows, 918,428 B, media subfamily), the cpe_9340 audio-codec WDSP split-PIL set (13 sparse rows, 359,088 B), the WCN3950-branch `cm*` Bluetooth firmware set (6 rows, 70,315 B - mainlined siblings under qca/, device copies are earlier builds), the radio partition images dsp.img (33,554,432 B = exactly 32 MiB, 76.35 percent of the family bytes) + storsec.img (20,480 B), 5 camera tuning bins (5 rows, 1,695,635 B), the Goodix FOD fingerprint firmware goodix_firmware.bin (1 row, 71,936 B) and 8 modem/platform metadata files (604,478 B). 106 rows (43,922,487 B, 99.94 percent of the family bytes) are corpus-unique to Mi_A3; only 16 rows (25,259 B) share md5s with the fleet. There is no structural absence: `other` is a census remainder of the modem/image + radio + bluetooth/image extraction, not a coherent single firmware family, and the census is complete for what it covers (recorded census gaps against the LineageOS manifest below: goodix_cfg_group.bin, ipa_fws.b00..b04 + elf, a610_zap.b00..b02 + elf - on-device files with zero census rows).

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi A3 (Android One program); codename `laurel_sprout` | device-inventory.csv codename cell `laurel_sprout` [F]; GSMArena (2026-11-21) [F] |
| SoC | Qualcomm **SM6125 Snapdragon 665** (11 nm), Kryo 260, Adreno 610; platform generation trinket | GSMArena (2026-11-21) [F]; Wikipedia (2026-11-21) [F]; **the matrix soc cell is empty on all 326 rows and the inventory soc cell is empty** - supplied here, flag for the lead |
| released | 2019-07-24 | GSMArena (2026-11-21) [F] |
| stock base | `laurel_sprout-user 11 RKQ1.200903.002 V12.0.26.0.RFQMIXM release-keys` (Android 11, MIUI 12 global) | LineageOS laurel_sprout manifest header (lineage-22.2, fetched 2026-11-21) [F] |
| fingerprint | under-display optical = Goodix FOD (Fingerprint On Display): the manifest ships `vendor/lib64/hw/fingerprint.goodix_fod.so` and `libvendor.goodix.hardware.biometrics.fingerprint@2.1.so`; the census carries `goodix_firmware.bin` + the `gfcep` trustlet as the firmware half | GSMArena (2026-11-21) [F]; manifest line 1008 [F]; pairing [I] |
| census scope | 326 rows in 9 families (other 122, tz 57, adsp 33, modem 33, wifi 45, cdsp 11, bt 11, boot 8, gpu 6); 331,543,576 B; this issue covers the 122-row `other` residual | coverage-matrix.csv [F]; family sum 326 and byte total 331,543,576 verified by python this session; inventory row agrees [F] |
| priority | P3 on all 122 rows; sha256_if_listed, isa_identified empty and interface_documented=n on all 122 | coverage-matrix.csv [F], single python assertion this session |
| census locations | modem/image 108 rows (8,534,948 B), radio 2 (33,574,912 B), vendor/etc/camera 5 (1,695,635 B), bluetooth/image 6 (70,315 B), vendor/firmware 1 (71,936 B) | coverage-matrix.csv [F]; python-verified crosstab, sums 122 rows / 43,947,746 B |

## Where the family lives and the census grammar [F]

The census extracts the device's modem/image, radio, bluetooth/image and vendor trees into named families by file grammar; every unmatched row lands in `other`. On Mi_A3 the modem/image directory alone splits across five families (adsp 32, tz 50, other 108, modem 31, cdsp 11), and bluetooth/image splits two ways: the `bt` family caught the `apbtfw*/apnv*/crbtfw*/crnv*` files (10 rows) while the `cm*` branch (6 rows) fell into `other` - a family-boundary quirk of the grammar, not a device property [F census shape; grammar reason [I]]. Subfamily census: misc 110, media 6 (venus), camera 5, touch 1 (goodix_firmware.bin); db_type census: ELF64 22 (= 11 mdt heads + 10 b00 heads + storsec.img), UNKNOWN 100 (python-verified).

## Group decomposition (122 rows -> 8 groups) [F]

| # | group | rows | bytes | location |
|---|---|---|---|---|
| A | modem/image misc split-PIL trustlet sets (9 apps, mdt + b00..b07 each) | 81 | 6,652,954 | modem/image |
| B | venus video-codec split-PIL set (media subfamily) | 6 | 918,428 | modem/image |
| C | cpe_9340 audio-codec WDSP split-PIL set | 13 | 359,088 | modem/image |
| D | WCN3950-branch `cm*` Bluetooth firmware | 6 | 70,315 | bluetooth/image |
| E | radio partition images (dsp.img + storsec.img) | 2 | 33,574,912 | radio |
| F | camera tuning bins | 5 | 1,695,635 | vendor/etc/camera |
| G | Goodix FOD fingerprint firmware | 1 | 71,936 | vendor/firmware |
| H | modem/platform metadata | 8 | 604,478 | modem/image |
| - | total | 122 | 43,947,746 | - |

python3 assertion passed: group rows sum to 122, group bytes sum to 43,947,746, groups are disjoint, and every row is accounted for exactly once.

### Group A - modem/image misc split-PIL trustlet sets (81 rows, 6,652,954 B)

9 named applications, each a complete Qualcomm split-PIL trustlet: `*.mdt` head + `b00..b07` (9 rows per set, no gaps, python-verified per set):

| set | rows | bytes | notes |
|---|---|---|---|
| gfcep | 9 | 5,683,239 | largest by far: b02 3,385,264 B + b04 2,203,320 B + b07 78,969 B + b01 6,952 B; all 9 corpus-unique |
| mfido | 9 | 281,585 | b02 180,476 B |
| haventkn | 9 | 198,034 | b01 20,080 B and mdt 20,592 B - the odd size class; b03 240 B is the 10-share segment |
| gptest | 9 | 148,330 | |
| securemm | 9 | 108,859 | mdt 7,464 B (not 7,260); b03 175 B and b06 304 B are 5-share |
| mlipay | 9 | 77,667 | |
| cardapp | 9 | 56,822 | |
| vsimapp | 9 | 53,833 | |
| secauth | 9 | 44,585 | |

- Size classes are rigid: mdt 7,260 B on 7 of 9 sets (securemm 7,464, haventkn 20,592); b00 308 B on 7 (securemm and haventkn 512); b01 6,952 B on all 8 small sets (haventkn 20,080); b06 152 B on 7 (securemm and haventkn 304) (python-verified). The same 6,952 B b01 class recurs on the Mi_13 generation's trustlets (sibling #1228), confirming it as a stable QTI build grammar [I].
- **Zero internal duplication**: all 81 rows carry 81 distinct md5s - the sibling generations record b03==b07 byte-identity inside each set (180 md5s per 200 rows on Mi_13); the SD665-era build duplicates nothing [F].
- Trustlet roster vs Mi_13 Group A (#1228): cardapp, mfido, mlipay, secauth persist by name from 2019 (SD665) to 2022 (SM8550) - generation-stable Xiaomi identity/payment trustlets [F names; functions [I]]. haventkn, securemm, vsimapp, gptest are the cross-vendor QTI set: haventkn.b03's 10-device share is the OnePlus 7/7T/7 Pro/9/9RT/9 Pro fleet + Moto_G200 + Edge_30_Fusion, and securemm.b03/b06 + cpe_9340.b03/b07/b11/b13/b15 are 5-shared with exactly the OnePlus 7 generation (guacamole/guacamoleb/hotdog/hotdogb, all `other`/misc/modem/image there - cross-device family assignment is consistent) [F spans]. The corpus also shows haventkn shipped by Google Pixels (flame/coral/sunfish/redfin/bramble/barbet vendor manifests) and QTI SDM660 trustzone build trees (SPLITBINS_KAJAANAA flist) [F public file lists].
- Public runtime proof: a Xiaomi dmesg gist shows `QSEECOM: qseecom_load_app: App (haventkn) does'nt exist, loading apps for first time` and `App with id 11 (haventkn) now loaded` (log lines 2022/2036; mfido at 1810/1869, mlipay 1883/1884, cardapp 1885/1887 also load via QSEECOM) - the modem/image misc sets are QSEE trustlets loaded through the QSEECOM interface [F public log; the log device is an SM8150-class Xiaomi, not laurel_sprout [I]].
- `gfcep` is the Mi_A3-exclusive Goodix trustlet: all 9 md5s corpus-unique, and the name pairs with goodix_firmware.bin (Group G) and the goodix_fod HAL. The newer generations name their Goodix trustlet after the device codename (gfcupid/gfdit/gffuxi per #1228); `cep` does not follow that pattern [F census; [OPEN] what CEP stands for].
- Function mapping for the remaining names is [I, name-based only]: vsimapp = virtual-SIM/eSIM app, securemm = secure multimedia, secauth = secure authentication, mlipay = Xiaomi payment wallet, mfido = Xiaomi FIDO authenticator, gptest = GlobalPlatform test app, haventkn = Haven trusted-key/token manager. No public interface documentation exists for any of the 9 functions [OPEN].

### Group B - venus video-codec split-PIL set (6 rows, 918,428 B)

mdt 7,020 B + b00 212 B + b01 6,808 B + b02 870,564 B + b03 33,792 B + b04 32 B. The subfamily is `media`. venus is publicly documented as the "Qualcomm Venus video codec accelerator" (linux-firmware WHENCE lines 7098-7120 serve qcom/venus-{1.8,4.2,5.2,5.4,6.0}/venus.mbn with venus.mdt symlinks); mainline sm6125.dtsi (fetched 2026-11-21) reserves `venus_mem: memory@52e00000` (line 299) but carries no venus node yet - partial mainline support [F]. The mdt/bNN split shape is the pre-mainline on-device container format; b02 (870,564 B) is the payload [I]. `venus.b04` is a 32 B fleet stub whose md5 (`0d68af0904dd698b16ffc9cd28b9b0c8`) is byte-identical to the 32 B venus.b19 / vpu20_4v.b19 segments on 33 other corpus devices spanning SDM855/SM8250/SD665/SD460-class generations (Moto E7/G10/G30/G32/G42/G52/G9/G200/Edge 30 series, OnePlus 7/8, FP4, Phone_1, Pro_1X, Realme 9/10 Pro, Nord CE2/CE3, Defy_2021) - a cross-generation stub segment, one of only two 34-device shares in the family [F]. Not in linux-firmware WHENCE as a device split-bin - not mainlined in this format [F].

### Group C - cpe_9340 audio-codec WDSP split-PIL set (13 rows, 359,088 B)

mdt only 724 B (smallest head in the family) + 12 segments: b01 240, b03 368, b05 20, b06 4, b07 24, b09 20, b11 8, b13 8, b15 8, b16 168,720, b18 174,336, b20 14,608 B - the payload is b16 + b18 + b20 (357,664 B). Segment indices are sparse: b00/b02/b04/b08/b10/b12/b14/b17/b19/b21/b22 absent (python-verified). Public identification: the QTI kernel DTS audio snippets (`arch/arm/boot/dts/qcom/sdm660-audio.dtsi`, `msm-audio.dtsi` incl. EssentialOpenSource/linux) carry a `qcom,wdsp` node with `qcom,img-filename = "cpe_9340"` - cpe_9340 is the audio-codec DSP (WDSP) firmware image [F public kernel DTS, GitHub code search 2026-11-21; the CPE = codec-processing-engine reading [I]]. The same build ships across the wcd934x-generation fleet: Pixel 2 (walleye/taimen) vendor manifests list cpe_9340.b01/b03/b05/b06/b09/b11/b13, the HTC U11+ (msm8998) device tree lists the full b00..b22 23-file set, and the OnePlus 7 census carries the same 5 shared segments as Mi_A3 (5-share rows b03/b07/b11/b13/b15) [F]. Not in linux-firmware WHENCE [F].

### Group D - WCN3950-branch `cm*` Bluetooth firmware (6 rows, 70,315 B)

| file | bytes | md5 | share |
|---|---|---|---|
| cmbtfw12.tlv | 43,991 | `201acb6f47e2176b0df36cff0255978e` | 1 (corpus-unique) |
| cmbtfw11.tlv | 14,247 | `8ec02ba2343140c0d155ea251ef416ac` | 14 |
| cmbtfw10.tlv | 4,803 | `505051a52545bffe76082c82adda3147` | 14 |
| cmnv12.bin | 2,564 | `7c647f72825b1192fc2ac629fd75c156` | 1 (corpus-unique) |
| cmnv11.bin | 2,676 | `c22408ff6a58959d28a3a2ec4b35b024` | 14 |
| cmnv10.bin | 2,034 | `2dceb768ace4075997b5ebfcccd14bc8` | 14 |

- The `cm` branch is mainlined: linux-firmware WHENCE lines 5345-5352 list `qca/cmbtfw12.tlv` (Version BTFM.CMC.1.2.0-00218-QCACHROMZ-2), `qca/cmbtfw13.tlv` (BTFM.CMC.1.3.0-00184-QCACHROM-1) and `qca/cmnv12.bin` (+ cmnv13 variants) under "Driver: qca - Qualcomm Atheros Bluetooth support for **WCN3950** chips" [F]. The device copies are earlier builds of the same family: Mi_A3 cmbtfw12.tlv 43,991 B vs mainline 47,307 B and cmnv12.bin 2,564 B vs mainline 2,690 B (Content-Length probes 2026-11-21) [F]. The 10/11 builds (cmbtfw10/11.tlv, cmnv10/11.bin) are not in current WHENCE and are 14-shared across the corpus: Defy_2021, Moto_E7_Plus, Moto_G9/G10/G30/G32/G42/G52/G9_Power/G_Power/G_Stylus_5G/G_5G_2024, Phone_1, Pro_1X + Mi_A3 - a cross-vendor, cross-SoC WCN3950-generation set (the corpus's Moto fleet docs cover it from the other side) [F].
- Boundary note: the sibling `ap*` (WCN3988, BTFM.CHE, WHENCE lines 5359-5366) and `cr*` (WCN399x, lines 5373-5381) branches on this same device sit in the `bt` family, so the family split here is purely a census-grammar artifact [F census shape; [I] grammar reason].

### Group E - radio partition images (2 rows, 33,574,912 B)

- `dsp.img` (33,554,432 B = exactly 32 MiB = 2^25, md5 `e41b4275c2f093ea7d760c37c784cc2f`, db_type UNKNOWN) is corpus-unique and is 76.35 percent of the family bytes. It is the Mi A3 `dsp` fastboot partition image: the official fastboot ROM flow flashes it with `fastboot flash dsp dsp.img` (XDA official-fastboot-ROM thread, web search 2026-11-21) [F]. On SD665 the dsp partition is the DSP-so PIL container holding the aDSP/CDSP processor images [I]; the census carries the aDSP (33 rows) and CDSP (11 rows) families separately at modem/image, but does not record whether those rows were extracted from dsp.img - [OPEN] provenance.
- `storsec.img` (20,480 B, db_type ELF64, md5 `b03c18a50cd7cb7f08217ccfa5720f83`) is corpus-unique. The QTI firmware-update flow flashes `fastboot flash storsec storsec.img` on OPlus SM7250/SM8150 and Xiaomi SDM845 devices (LineageOS wiki firmware-update templates, GitHub code search 2026-11-21) - the storage-security partition image [F flow; function reading [I]]. Not in linux-firmware WHENCE [F].

### Group F - camera tuning bins (5 rows, 1,695,635 B, vendor/etc/camera)

| file | bytes | share | notes |
|---|---|---|---|
| sdm_ys_32p_120_21_5_perturb50.bin | 1,690,160 | 1 | corpus-unique; "perturb50" naming reads as a per-module tuning/LSC table [I] |
| goldResult_586.bin | 2,048 | 1 | corpus-unique |
| goldResult_582.bin | 2,048 | 1 | corpus-unique |
| CFR_para.bin | 1,079 | 1 | corpus-unique; cf. Mi_13's CFR_para_UW_V01.bin 8,128 B (#1228) - same name family, later generation [F names] |
| libalfpc_tuning.bin | 300 | 5 | 5-share with Mi_12T_Pro, Poco_F5_Pro, Redmi_10S, Redmi_K60_Pro - a Xiaomi camera-tuning fleet file that outlives the 2019 platform [F] |

All 5 files are listed in the LineageOS laurel_sprout manifest (lines 796, 807, 808, 830, 840) [F].

### Group G - Goodix FOD fingerprint firmware (1 row, 71,936 B)

`goodix_firmware.bin` (md5 `a7efc5cf3ede7c5661dfb54ad251e446`, vendor/firmware, db_type UNKNOWN) is corpus-unique and is the firmware half of the under-display Goodix fingerprint solution (GSMArena in-display fingerprint; manifest ships the `fingerprint.goodix_fod.so` HAL and `libvendor.goodix.hardware.biometrics.fingerprint@2.1.so`; the `gfcep` trustlet is the secure-world half) [F HAL/firmware presence; pairing [I]]. Census gap: the manifest also lists `goodix_cfg_group.bin` (line 1117) which has **zero census rows corpus-wide** [F manifest vs census].

### Group H - modem/platform metadata (8 rows, 604,478 B, modem/image)

| file | bytes | share | notes |
|---|---|---|---|
| data.msc | 590,389 | 1 | corpus-unique; the EFS/NV-container reading carries over from the sibling generations (Mi_13 Data.msc 1,455,171 B, #1228) [I] |
| mbn_sw.txt | 7,701 | 1 | corpus-unique (Mi_13's is 19,648 B) [F] |
| oem_sw.txt | 3,206 | 1 | corpus-unique |
| mbn_hw.txt | 2,635 | 1 | corpus-unique |
| gptauuid.xml | 483 | 1 | corpus-unique partition-UUID metadata; Mi_13's is 10,399 B - layouts differ per generation [F; reading [I]] |
| mbn_sw.dig | 32 | 1 | corpus-unique |
| mbn_hw.dig | 32 | 7 | 7-share with FP4 + the OnePlus 8/9 fleet |
| oem_hw.txt | 0 | 34 | 0-byte file carrying the empty-file md5 `d41d8cd98f00b204e9800998ecf8427e`, 34-shared (FP4/FP5/FP6, Mi_12/12S/12T/13 generations, Nord fleet, OnePlus 8-13, Pixel 4A/5/5A, Poco F5/F6, Realme 9/10 Pro, Redmi_K60_Pro, Pad_2_Pro) - the fleet-wide platform placeholder class #1228 records on Mi_13 [F] |

## Share structure (corpus-wide md5 spans) [F]

| devices sharing an md5 | rows | bytes | who |
|---|---|---|---|
| 1 | 106 | 43,922,487 | everything else: all 11 mdt heads, all 10 b00 heads, all trustlet bodies except the shared segments below, dsp.img, storsec.img, goodix_firmware.bin, sdm_ys/goldResult/CFR camera bins, data.msc, gptauuid.xml, mbn_sw.txt/mbn_hw.txt/mbn_sw.dig, oem_sw.txt, cmbtfw12.tlv, cmnv12.bin |
| 34 | 2 | 32 | venus.b04 (32 B fleet stub, incl. the b19-named copies) and oem_hw.txt (0 B empty-file placeholder) |
| 14 | 4 | 23,760 | cmnv10.bin, cmnv11.bin, cmbtfw10.tlv, cmbtfw11.tlv - the cross-vendor WCN3950-generation Bluetooth set |
| 10 | 1 | 240 | haventkn.b03 (Edge_30_Fusion, Moto_G200, OnePlus 7/7T/7 Pro/9/9RT/9 Pro) |
| 7 | 1 | 32 | mbn_hw.dig (FP4, OnePlus 8/8 Pro/9/9RT/9 Pro) |
| 5 | 8 | 1,195 | libalfpc_tuning.bin (Xiaomi/Redmi quartet) + securemm.b03/b06 and cpe_9340.b03/b07/b11/b13/b15 (OnePlus 7 fleet) |

python3-verified histogram: 1:106, 5:8, 7:1, 10:1, 14:4, 34:2 (sum 122). The family is Mi_A3-specific in bytes (99.94 percent) but rides four long fleet spans in rows: the WCN3950 Bluetooth generation set, the venus 32 B stub, the QTI trustlet mini-segments and the 0-byte placeholder.

## Generation contrasts vs the SM8550 sibling (#1228) [F unless noted]

1. **mdt grammar**: 7,260 B heads (laurel_sprout 2019) vs 4,752 B (fuxi SM8550) and 4,272 B (SM8450/8475); b01 6,952 B here vs the sibling generations' different body classes - the split-PIL container is a per-generation build artifact [F].
2. **No internal duplication** on the 2019 build (81 rows / 81 md5s) vs the SM8550 sets' b03==b07 identity (180 md5s / 200 rows) [F].
3. **Roster continuity**: cardapp/mfido/mlipay/secauth persist from 2019 to the SM8550 generation; 5 names (vsimapp/securemm/gptest/haventkn + cpe_9340) drop out of the fuxi census while faceutils/ic3/ic4/miriskm/mkeybag/ops/otrpapp and the UUID trustlets are new there [F rosters].
4. **Bluetooth branch split across census families** on laurel_sprout (cm in `other`, ap/cr in `bt`); on fuxi the whole hmt* set is in `other` - the grammar's branch coverage evolved with the file-name generation [F; [I] reason].
5. **Radio content**: laurel_sprout radio = 19 rows across 5 families (dsp.img 32 MiB + storsec.img here; modem.img 117,198,848 B, bluetooth.img, tz.img, xbl/abl/boot set elsewhere); fuxi radio = dsp.img 64 MiB only - the 2019 radio extraction is richer per family [F].
6. **dsp.img doubles** (32 MiB -> 64 MiB) across the three platform generations; whether that tracks aDSP/CDSP payload growth or packaging is [OPEN].

## Census gaps recorded (LineageOS laurel_sprout manifest, lineage-22.2, fetched 2026-11-21)

The manifest (1,122 lines, `V12.0.26.0.RFQMIXM` header) ships device files the census does not carry; the census targets firmware payloads, so these are coverage notes, not census errors - but the following firmware payloads are on device with zero census rows on Mi_A3 [F manifest vs census]:

- `vendor/firmware/goodix_cfg_group.bin` - 0 census rows corpus-wide (the fingerprint config sibling of goodix_firmware.bin).
- `vendor/firmware/ipa_fws.b00..b04` + `ipa_fws.elf` - 5 segment files + elf on device; the census carries only `ipa_fws.mdt` (7,020 B, in the `modem` family at vendor/firmware). The scuba_ipa_fws fleet rows (#1120 class) show the full split set is capturable elsewhere.
- `vendor/firmware/a610_zap.b00..b02` + `a610_zap.elf` - 3 segments + elf on device; the census carries only `a610_zap.mdt` (6,860 B, `gpu` family). The gpu-family census on Mi_A3 (a610_zap.mdt + a612_rgmu.bin + a618_gmu.bin + a630_gmu.bin + a640_gmu.bin + a630_sqe.fw) is the generic Adreno gmu set, not the device's actual zap shader image (see #928 for the a618_gmu build-identity class).

The modem/image and radio files (Groups A, B, C, E, H) do not appear in the manifest because they ride the partition images (modem.img, dsp.img, radio folder) rather than /vendor - the census's modem/image extraction is the only public file-level view of them, and there is no evidence of a gap there [I].

## ISA / interface facts

- isa_identified is empty and interface_documented=n on all 122 rows - honestly un-RE'd at the census level; nothing below upgrades the census cells, it records public interface evidence per group [F census; public facts follow].
- Group A (QSEE trustlets): the load interface is QSEECOM (public kernel module; the dmesg gist shows the exact `qseecom_load_app` path for haventkn/mfido/mlipay/cardapp), and the split-PIL mdt/bNN container format is public (imlk.top's OnePlus 6 QSEE analysis, Check Point 2019/Quarkslab write-ups - cited from the sibling docs). No public format or interface documentation exists for any of the 9 trustlet functions; Pixel/QTI trees provide file lists only [F coverage; [OPEN] functions].
- Group B (venus): the load interface is mainline-public - the venus driver and linux-firmware qcom/venus-*/venus.mbn define the format family (WHENCE lines 7098-7120); the device ships the split-bin on-device variant. Mainline sm6125.dtsi has the venus_mem reservation but no venus node yet [F].
- Group C (cpe_9340/WDSP): the QTI kernel `qcom,wdsp` node with `qcom,img-filename = "cpe_9340"` is public (sdm660-audio.dtsi / msm-audio.dtsi trees) - the loader and image name are documented, the image content is not [F].
- Group D (cm* Bluetooth): the load interface is mainline-public - the btusb/qca driver serves qca/cmbtfw12.tlv + qca/cmnv12.bin for WCN3950 chips (WHENCE lines 5345-5352); the device copies are earlier builds of the same two files [F].
- Group E (dsp.img/storsec.img): both are fastboot-flashable partition images (XDA Mi A3 fastboot flow; LineageOS wiki storsec template) [F]; content-level interface unproven from public sources [I].
- Groups F/G: userspace HALs are public in the LineageOS manifest (camera vendor blobs; goodix_fod HAL); the firmware files themselves are un-RE'd [F presence].

## Honest negatives ([OPEN])

1. `gfcep` (5,683,239 B, 9 rows): function unmapped; "cep" breaks the per-codename Goodix trustlet naming the newer generations follow; zero firmware prior art for the name (GitHub code search 2026-11-21).
2. Function mapping for vsimapp/securemm/secauth/mlipay/mfido/gptest/haventkn rests on vendor naming only; haventkn additionally has the QSEECOM runtime proof but no identification.
3. dsp.img (32 MiB) content unextracted in the census; whether the separate adsp/cdsp family rows were derived from it is not recorded - provenance [OPEN].
4. `goodix_cfg_group.bin`, `ipa_fws.b00..b04 + elf`, `a610_zap.b00..b02 + elf`: on-device per the LineageOS manifest, 0 census rows corpus-wide - the census's vendor/firmware coverage captured only the mdt heads.
5. Why cmbtfw12.tlv/cmnv12.bin are corpus-unique while the 10/11 builds are 14-shared across 13 other devices (a build-locality artifact of the 2020 MIUI radio package vs the Moto/Nothing/Fxtec set) - unresolved.
6. cpe_9340's sparse segment indices (no b00/b02/b04/b08/b10/b12/b14/b17/b19/b21/b22) vs the full b00..b22 set the HTC U11+ tree lists - different builds of the same firmware, exact segment pruning unknown.
7. The 8 B cpe_9340 stubs (b11/b13/b15) and the 32 B venus.b04 stub: why QTI ships byte-stub segments at fleet-wide-identical content - [OPEN].
8. The `bt`-vs-`other` family split of the Bluetooth branches (ap/cr in `bt`, cm in `other`) is a census-grammar artifact whose matching rule is not documented in-repo - flag for the lead.

## What would upgrade this finding

1. A full Mi A3 fastboot ROM extract to enumerate dsp.img's internal container layout (settle the aDSP/CDSP provenance and the 32 MiB packing).
2. strings/headers of gfcep (5.7 MB corpus-unique Goodix trustlet) - the highest-value un-RE'd Mi_A3-exclusive blob; Goodix sensor documentation is partially public.
3. Byte-comparison of cmbtfw12.tlv/cmnv12.bin against a pinned linux-firmware release to date the device's WCN3950 build (43,991/2,564 B device vs 47,307/2,690 B mainline today).
4. Census backfill of goodix_cfg_group.bin, ipa_fws.b00..b04 and a610_zap.b00..b02 (size/md5 capture) so the vendor/firmware groups can be decomposed completely.
5. Identify haventkn by matching its mdt against public QSEE trustlet datasets (HexHive/taemu class, per sibling #1228's method).

## RULE 0 record

- 2026-11-21T10:08:28Z: CLAIM ZC-1 zcode posted (first comment, re-verified).
- 2026-11-21: SEARCH comment (Gate -1) and Gate 0 NO-PRIOR-ART comment posted.
- 2026-11-21: deliverable pushed to feat/open-device-site; byte-verified against the remote; DONE comment with the remote sha.
- Evidence classes: [F] = command output from the local census clone or a fetched public source with access date; [I] = labeled inference from names/shapes/spans. Every sum in this document re-verified with python3 -I this session (assertion script: device totals, location crosstab, 8-group sums, per-trustlet sums, share histogram, segment size classes, dsp.img 32 MiB identity - all asserted equal before writing).

This document analyzes firmware containers at the metadata level only (sizes, hashes, names, locations). It is not legal advice; no proprietary payload bytes were fetched or committed.
