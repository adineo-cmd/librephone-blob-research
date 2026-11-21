# xiaomi Mi_12 - `other` family status (391 rows - PRESENT, residual catch-all family across 6 device locations; 10 groups, python-verified sums, 307 distinct md5s, 70 corpus-unique rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1174](https://github.com/adineo-cmd/open-device/issues/1174)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site b4784e9 worktree), `upstream-contribution/blob-database/device-inventory.csv`, the sibling doc docs/devices/xiaomi/Mi_12/adsp.md (issue [#1168](https://github.com/adineo-cmd/open-device/issues/1168), device identity + two-container grammar, cited not re-derived), the LineageOS `android_device_xiaomi_cupid` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), the linux-firmware qca/ directory tree listing (fetched 2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (fetched 2026-11-21), GitHub code search (fetched 2026-11-21), public spec pages (2026-11-21). No payload fetched by this issue; every number below is command output verified with python3 (`python3 -I`, this session).

**Verdict: the `other` family is PRESENT on Mi_12 and is the residual catch-all of the 783-row census - 391 rows, 133,668,936 B (13.81 percent of the device census bytes), 307 distinct md5s, spread over 6 locations.** It decomposes into 10 groups: 15 TrustZone application split-PIL sets (150 rows), the slpi sensor-island firmware (26), modem OS pieces (7), 42 WLAN board-data ELFs, mbn/oem metadata texts (14), the WCN6750 Bluetooth NVM/TLV sets (113), mdt-only subsystem extracts in vendor/firmware (9), camera/ArcSoft resources (28), one GPU calibration blob (1), and the 64 MiB radio dsp.img (1). 70 rows (25,492,177 B) are corpus-unique to Mi_12; the dominant share pattern is the 8-device Xiaomi SM8450-generation octet (202 rows); 0 rows are unique within the Bluetooth and board-data groups. There is no structural absence: the family is a census remainder, not a coherent single firmware family, and the census is complete for what it covers (with recorded partial-coverage contrasts against the LineageOS manifest, below).

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12 (China, model 2201123C); codename `cupid` | sibling doc #1168 identity table [F] |
| SoC | Qualcomm **SM8450 Snapdragon 8 Gen 1**; Adreno 730; Hexagon V69 DSP | sibling doc #1168 (public spec pages 2026-11-21) [F]; the upstream inventory SoC cell is empty there too |
| census scope | 783 rows in 9 families; 967,886,162 B; this issue covers the 391-row `other` residual | coverage-matrix.csv [F] |
| priority | P3 on all 391 rows | coverage-matrix.csv [F] |
| corpus classes [I] | the 8-device share octet = Mi_12, Mi_12_Pro (SM8450) + Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro (SM8475-class) + Poco_F5 (SM7475-class) | public spec pages (2026-11-21); md5 spans below [F] |

## Where the family lives (family x path crosstab) [F]

`other` is residual: every row not matched by a named-family grammar lands here. The census locations and their family mix for Mi_12:

| location | all families | `other` share |
|---|---|---|
| `xiaomi/cupid/modem/image` | 585 rows in 6 families (wifi 176, other 239, tz 85, adsp 28, modem 38, cdsp 19) | 239 rows, 53,342,955 B |
| `xiaomi/cupid/bluetooth/image` | other only | 113 rows, 1,063,407 B |
| `xiaomi/cupid/vendor/etc/camera` (+ resources) | other only | 28 rows, 11,909,421 B |
| `xiaomi/cupid/vendor/firmware` | gpu 5, other 9 | 9 rows, 35,136 B |
| `xiaomi/cupid/vendor/gpu/kbc` | gpu 1 (sequence_manifest.bin), other 1 | 1 row, 209,153 B |
| `xiaomi/cupid/radio` | boot 14, tz 6, modem 1, bt 1, other 1 | 1 row, 67,108,864 B |

Group sums: 53,342,955 + 1,063,407 + 11,909,421 + 35,136 + 209,153 + 67,108,864 = 133,668,936 (python-verified).

## Group decomposition (391 rows -> 10 groups) [F]

| # | group | rows | bytes | location |
|---|---|---|---|---|
| A | TrustZone application split-PIL sets (15 apps, mdt + b00..b08 each) | 150 | 33,991,660 | modem/image |
| B | slpi sensor-island split-PIL firmware | 26 | 9,381,764 | modem/image |
| C | modem OS + platform pieces | 7 | 7,362,851 | modem/image |
| D | WLAN board-data ELFs (`bd_*.elf`) | 42 | 2,517,136 | modem/image |
| E | mbn/oem build metadata + modem config texts | 14 | 89,544 | modem/image |
| F | Bluetooth NVM/TLV sets (hpnv/hpbtfw) | 113 | 1,063,407 | bluetooth/image |
| G | subsystem mdt extracts + Cirrus amp bins | 9 | 35,136 | vendor/firmware |
| H | camera tuning + ArcSoft renderer resources | 28 | 11,909,421 | vendor/etc/camera |
| I | GPU kbc calibration blob | 1 | 209,153 | vendor/gpu/kbc |
| J | dsp partition image | 1 | 67,108,864 | radio |
| - | total | 391 | 133,668,936 | - |

python3 assertion passed: group rows sum to 391, group bytes sum to 133,668,936; subfamily census check misc 347 / camera 30 / fingerprint 9 / audio 4 / media 1 (camera 30 = H 28 + CAMERA_ICP.mdt in G + unified_ksqs.bin in I; fingerprint 9 and audio 4 ride inside A and G).

### Group A - TrustZone application split-PIL sets (150 rows)

15 named applications, each a complete Qualcomm split-PIL trustlet: `*.mdt` (3,972 B each, 15 total 59,580 B) + `b00` (568 B each) + `b01..b08`:

cardapp, devauth, eseservice, evautil64, fingerpr, gfcupid, ic3, mfido, miriskm, mldapta, mlipay, ops, otrpapp, seccammil, secauth.

- Every one of the 15 sets is structurally identical: 10 files, mdt + b00..b08, no gaps (python-verified per set).
- Every set carries the same internal duplication: `b03` and `b07` are byte-identical (same md5, e.g. secauth 480 B `606fc5e1...`, fingerpr 281,192 B `dac782f3...`) - a build-grammar property of the whole 15-set generation, not per-device noise [F].
- Every `b08` is 3,404 B (the terminal segment) and every `b00` is 568 B; 14 of the 15 b00s carry db_type=ELF64, fingerpr.b00 is db_type=FINGERPRINT (fingerprint subfamily labeling).
- `fingerpr` (mdt + b00..b08) is the only set whose bNN rows carry blob_subfamily=fingerprint and db_type=FINGERPRINT: a 6,909,820 B b01 plus 8 small segments - the fingerprint TrustZone payload the fleet fpctzapp/egtzappf findings (in-repo #2024/#1000) analogize to, here correctly subfamily-labeled.
- `gfcupid` is the Mi_12-exclusive trustlet: all 10 of its files are corpus-unique (13,924,277 B total; gfcupid.b04 7,409,212 B and fingerpr.b01 6,909,820 B are the two largest trustlet segments in the whole family). GF = graphics/font cache? - naming unverified [I].
- Sharing spans: 38 rows corpus-unique (14,027,541 B) = 15 mdts + all 15 b08 terminals + the 8 remaining gfcupid segments (b00..b07); evautil64.mdt is the only 8-shared mdt; wide spans on individual segments: evautil64.b05 27 devices, evautil64.b04 + ops.b04 22 devices, ops.b05 16 devices, cardapp.b04/b05 12 devices.
- Interpretation [I]: these are SM8450-generation QSEE trustlets (secure element services eseservice/ic3, identity wallets mlipay/miriskm/mfido/mldapta, OEM security ops/otrpapp/devauth/secauth, camera TZ support seccammil/evautil64, fingerprint fingerpr, region gfcupid). Function mapping rests on vendor naming only.

### Group B - slpi sensor-island split-PIL firmware (26 rows)

`slpi.mdt` 4,944 B + `slpi.b00..b21` + `slpi.b23` (23 segments; **b22 absent** - same per-build segment-skip property the sibling doc records for adsp.b24) + `slpir.jsn` 513 B + `slpius.jsn` 515 B.

- Mainline cross-check: `remoteproc_slpi` compatible **`qcom,sm8450-slpi-pas`** exists in mainline sm8450.dtsi (fetched 2026-11-21) and in 282 repos' `drivers/remoteproc/qcom_q6v5_pas.c` - the SLPI is a mainline-recognized remote processor and this is its firmware image [F].
- 14 rows corpus-unique (9,102,624 B): slpi.mdt + b00, b02, b05, b08, b09, b11-b14, b16-b18, b23. Shared: b01/b04/b06 8 devices (octet), b03/b10 9 devices, b15 6, b19/b20/b21 4, b07 3; the two .jsn files 14 devices (octet + Edge_30_Fusion, Moto_G200, OnePlus_9/9RT/9_Pro, Phone_2) - servreg metadata is generation-generic, the sensor OS body is cupid-specific [I].

### Group C - modem OS + platform pieces (7 rows)

| file | bytes | md5 | share |
|---|---|---|---|
| amss.bin | 5,470,128 | `303dca2a3fe83e5d5dfa783f2bcea26e` | 8 (octet) |
| Data20.msc | 916,071 | `2acdcb0af37ede2ada6884b8b1292c04` | 8 (octet) |
| Data.msc | 889,524 | `b9eaf732e3289eb9d1a452a8e9083689` | 8 (octet) |
| fw_ipa_gsi_3.0_w.elf | 40,076 | `ccef725350abe678560956545cda6254` | 1 (Mi_12) |
| cpusys_vm.mdt | 16,580 | `7b1e5e456a5b181cbcf48a8ac78992f4` | 1 (Mi_12) |
| regdb_xiaomi.bin | 24,278 | `b937a474fe3644c3601ab14afaa78b23` | 5 |
| gptauuid.xml | 6,194 | `040e845630cd3b53e0078f7234452000` | 8 (octet) |

- amss.bin is the modem processor OS payload [I]; mainline `remoteproc_mpss` compatible `qcom,sm8450-mpss-pas` (sm8450.dtsi, fetched 2026-11-21) is the loader side [F]. The 38 modem-family rows in this same directory (the modem split-PIL set + modemr.jsn + battmgr.jsn + modem.img + the ipa_fws split set) are sibling content - this issue does not re-cover them; the `fw_ipa_gsi_3.0_w.elf` here is a distinct file from the modem-family ipa_fws set [F].
- `cpusys_vm.mdt` is a family-boundary quirk: its mdt sits in `other` while `cpusys_vm.b00..b04` (212 + 516,096 + 4,621 + 4,096 + 16,368 B) sit in the `tz` family (db_type=SECURITY) - the set is one split-PIL image split across two census families [F].
- `fw_ipa_gsi_3.0_w.elf` is db_type=CERT on an ELF firmware file - a db_type mislabel of the same class as the corpus-wide a660/AUDIO and fpctzapp/gpu mislabels already recorded in-repo (#946, #2024) [I]. IPA = IP accelerator offload firmware; gsi 3.0 = the SM8450 GSI generation [I]. linux-firmware WHENCE does not list it (fetched 2026-11-21) - not mainlined [F].
- `Data.msc`/`Data20.msc` are modem data images (EFS/NV-container hypothesis [I]); `regdb_xiaomi.bin` is a Xiaomi-specific regulatory-database binary; `gptauuid.xml` is partition UUID metadata. Functions from naming [I].

### Group D - WLAN board-data ELFs (42 rows)

42 files `bd_<module>[gf][<region>].elf`, 59,896-60,080 B each, 2,517,136 B total, 38 distinct md5s.

- Modules: l1, l2, l2s, l3, l3s, l10, l12, l18, m11a, m16t, m80, m81 with region/build suffixes: gf, gl, in (India), jp (Japan) [I for the region reading from the suffix names]. All 42 are db_type=ELF64.
- All 42 rows share the 8-device octet and nothing else - the board-data set is exactly the Xiaomi SM8450-generation build set [F].
- 4 byte-identical region pairs: bd_m11a.elf = bd_m11ain.elf (60,000 B), bd_m11agf.elf = bd_m11agfin.elf (60,000 B), bd_m80.elf = bd_m80gf.elf (59,924 B), bd_m81.elf = bd_m81gf.elf (59,920 B) - the India and global variants collapse to the same bytes on m11a/m80/m81 [F].
- Boundary note: the `wifi` family (176 rows) already covers the sibling WLAN board data `bdwlan.elf`/`bdwlang.elf` split files and `regdb.bin` at modem/image; the `bd_*.elf` set here is a distinct per-SKU file family, no filename overlap [F].

### Group E - mbn/oem build metadata + modem config texts (14 rows, 89,544 B)

- `mbn_*` (6 rows, 57,014 B): mbn_build_utc.txt 10 B, mbn_hw.dig 32 B, mbn_hw.txt 407 B, mbn_ota.md5sum 36,571 B, mbn_sw.dig 32 B, mbn_sw.txt 19,962 B. mbn_ota.md5sum and mbn_build_utc.txt are Mi_12-unique (36,581 B - a build timestamp and an OTA digest, i.e. build-stamping artifacts [I]); mbn_sw.dig is 2-shared, mbn_hw.dig is 8-shared (octet).
- `oem_*` (8 rows, 32,530 B): oem_hw.txt 61 B = oem_hw_cert.txt 61 B (byte-identical), oem_hw_dsda.txt 68 B, oem_hw_ss.txt 59 B, oem_sw.txt 18,895 B (5-shared), oem_sw_ct_volte.txt 13,386 B, oem_hw_null.txt 0 B, oem_sw_null.txt 0 B.
- The two 0-byte files carry md5 `d41d8cd98f00b204e9800998ecf8427e` (the empty-string md5) and are the widest-shared rows of this family: 34 corpus devices spanning Pixels (4A_5G/5/5A), Fairphones (FP4/FP5/FP6), OnePluses (8..13), Xiaomi/Redmi/Poco, Moto, Realme, Nord - trivially, empty config placeholders are universal [F].

### Group F - Bluetooth NVM/TLV sets (113 rows, 1,063,407 B)

| set | rows | bytes |
|---|---|---|
| hpnv21 (WCN6750 BT NVM) | 44 | 291,348 |
| hpnv21g (global variant) | 44 | 284,384 |
| hpnv20 / hpnv20g (older NVM generation) | 11 / 9 | 69,509 / 56,961 |
| hpbtfw20.tlv + .ver / hpbtfw21.tlv (BT firmware TLV) | 2 / 1 | 201,593 / 146,068 |
| hpnv21_sony.302 / hpnv21g_sony.302 | 2 | 13,544 |

- Structure: hpnv21 = `hpnv21.bin` + `hpnv21.301`/`.302` (NVM version files [I]) + 41 `bNN` segment files spanning b5a..bc2 with the gaps ba5 and bb4, plus 3-digit continuations b10c/b111. hpnv21g is the same 45-row shape (44 + the sony.302 sibling). hpnv20 (11 rows: bin + b2f/b3b/b4b/b59/b5a/b6a/b6b/b8b/b8d/b90) and hpnv20g (9 rows) are sparse older-generation sets. All 113 rows are db_type=UNKNOWN, subfamily misc.
- **Heavy intra-set byte duplication**: the 44 hpnv21 rows collapse to only 20 distinct md5s (hpnv21g likewise 20; hpnv20 11 rows -> 5 md5s; hpnv20g 9 -> 4). Example identity groups: hpnv21.bin = b9b = b9f = ba0 = bc1 (5 rows, `291822f4...`), b9a = b9e = ba6 = ba9 = bc0 (5), bac = bad = bb5 = bb6 = bba = bbe (6), 301 = 302. The NVM "tiles" are a small set of distinct payloads repeated under many filenames [F].
- **Mainline overlap is real and partial**: the linux-firmware `qca/` directory (tree listing fetched 2026-11-21) ships the WCN6750 Bluetooth family - 16 hpnv21 files, 17 hpnv21g files, hpbtfw21.tlv. Filename overlap with cupid: 14 files per NVM set (bin, 301, 302, b10c, b111, b8c, b9f, ba0-ba4, baa, bb8); linux-firmware additionally carries 309/30a(/30c) that cupid does not, cupid carries 41 segments that linux-firmware does not.
- **Not byte-identical** (sizes, both sides command-fetched): hpnv21.bin 6,610 B (upstream) vs 6,602 B (census); hpnv21g.bin 6,450 vs 6,442; hpbtfw21.tlv 163,332 vs 146,068; .301/.302 +24 B; segment files +8 B. Systematic size deltas - different builds of the same NVM tile scheme [F]; byte-level diff not performed, no payload fetched [OPEN].
- The `_sony` suffix variants (6,852 B / 6,692 B) match the .301 sizes of their sets - NVM tuned for a Sony radio-module SKU hypothesis [I], unverified.
- Sharing: 0 corpus-unique rows. 90 rows octet-only; 11 rows (hpbtfw21.tlv + 10 hpnv21/hpnv21g files) octet + Phone_2; 12 rows (all of hpnv20 + hpbtfw20.tlv) octet + OnePlus_9/9RT/9_Pro + Phone_2 - the older NVM generation spans SM8350-class hardware too [F spans; SoC classes [I]].

### Group G - subsystem mdt extracts + Cirrus amp bins (9 rows, 35,136 B)

| file | bytes | db_type | share |
|---|---|---|---|
| CAMERA_ICP.mdt | 4,704 | ELF64 | 1 (Mi_12) |
| evass-lt-21.mdt | 4,624 | ELF64 | 1 (Mi_12) |
| evass.mdt | 4,624 | ELF64 | 1 (Mi_12) |
| vpu20_4v.mdt | 4,624 | ELF64 | 1 (Mi_12) |
| evautil64.mdt | 3,868 | ELF64 | 8 (octet) |
| T-/B-cs35l41-dsp1-spk-{cali,prot}.bin | 1,580 + 4,764 + 4,768 + 1,580 = 12,692 | AUDIOAMP x4 | all 1 (Mi_12) |

- These are the mdt-only heads of four subsystem firmware sets whose full split-PIL bodies exist in the vendor tree but are **not in the census**: the LineageOS cupid manifest (lineage-22.2, fetched 2026-11-21) lists evass.b00-b19 + mbn, evass-lt-21.b00-b19 + mbn, vpu20_4v.b00-b09 + b18/b19 + mbn, CAMERA_ICP.b00-b21 + elf + mbn + _170/_480.elf variants. Census completeness for these subsystems is mdt-head-only - a recorded census gap, not a device absence [F vs LineageOS].
- evass/evass-lt-21 = the EVA subsystem (SM8450's vision accelerator; mainline sm8450.dtsi reserves `cvp_mem` but has **no** EVA remoteproc node, and GitHub code search for `qcom,sm8450-eva-pas` / `sm8450-eva` in C (2026-11-21, adineo-cmd excluded) returns 0 hits - no mainline EVA PAS loader [F]). vpu20_4v = the video (Venus-generation) processor firmware [I]; CAMERA_ICP = the camera ICP firmware [I from vendor naming].
- The same directory also hosts the gpu-family Adreno rows (a730_zap.mdt mdt-only too, a730_sqe.fw, a662_gmu.bin, a660_sqe.fw, gmu_gen70000.bin - 5 rows) - covered by the gpu family, not here.
- The 4 cs35l41 bins are Cirrus Logic CS35L41 smart-amp DSP coefficient/calibration files; the mainline wm_adsp loader (sound/soc/codecs/wm_adsp.c) selects per-speaker tuning by component prefix exactly like cupid's T-/B- (top/bottom speaker) naming (public wm_adsp prefix convention, code search 2026-11-21) [F convention; T/B reading [I]]. db_type=AUDIOAMP is the corpus's own label. WHENCE lists none of the cupid bins [F].

### Group H - camera tuning + ArcSoft renderer resources (28 rows, 11,909,421 B)

| slice | rows | bytes | notes |
|---|---|---|---|
| vendor/etc/camera top level | 11 | 2,601,045 | arcsat_2sat.bin 326, calibration.bin 160, CFR_para_* 5 x 3,645, deblur_sd_opencl_binary.bin 354,046, deblur_sd_opencl_params.bin 2,042, ellv.bin 2,225,696, MILDC_CALIB_0x01.bin 550 |
| resources/render/Configure/... | 13 | 8,647,056 | 4 x front.bin 1,048,600 (2 distinct md5s: Capture pair `41becbf1...`, SkinTone pair `a64ee574...`), BrightEyes/eye_pupil/left_eye/right_eye (63,416+90,024+31,608+31,832), skin_detail.bin 2,834,376, Makeup 4 files (788,432+106,520+274,368+232,080) |
| resources/kernel/32 + /64 | 4 | 661,320 | s31.../t31... hash-named kernels, 32-bit (6,796+322,112) vs 64-bit (6,800+325,612) |

- 6 rows corpus-unique (2,237,507 B): ellv.bin (the largest camera resource), arcsat_2sat.bin, MILDC_CALIB_0x01.bin, and the 3 CFR_para_UW_* files (which are byte-identical to each other, `359df251...`, one md5 over 3 rows - UW filter variants collapse). 20 rows are 2-shared (Mi_12 + Mi_12_Pro only); the deblur pair (an Adreno OpenCL compiled kernel + its parameter blob [I]) is 8-shared with the octet.
- The kernel/32 and kernel/64 filenames embed concatenated hash-like tokens (`s31bc24e5f6c4ef1752c77f3a22ad1ffcs0cc175b9c0f1b6a831c399e269772661t92eb5ffee6ae2fec3ad71c777531578fn...`); the naming structure is recorded, not parsed [F names; structure interpretation [OPEN]].
- The census camera slice is a small extract: the LineageOS manifest lists hundreds of vendor/etc/camera files (filter PNGs, bokehParams.json, GpuKernelRepo.pb, sceneDetection.xml, model trees) - most are outside the 783-row census [F].

### Group I - GPU kbc calibration blob (1 row)

`vendor/gpu/kbc/unified_ksqs.bin` 209,153 B, md5 `1a217e4b2ce9c57342343386aeef923a`, db_type UNKNOWN, subfamily camera, shared by 9 devices (octet + Phone_2). The same kbc directory carries the gpu-family row sequence_manifest.bin (1,860 B) - not covered here. Not in the LineageOS manifest (fetched 2026-11-21): the only in-census vendor-tree file LineageOS does not package - consistent with a device-generated calibration artifact rather than a shipped blob [I, unverified]. Function unknown; [OPEN].

### Group J - the radio dsp.img (1 row)

`xiaomi/cupid/radio/dsp.img` is exactly 67,108,864 B = 64 MiB, md5 `1cc3caa8c3c0b559174c2b34397492ba`, db_type UNKNOWN, shared only with Mi_12_Pro. The radio path holds exactly 2 census rows for Mi_12: this and the bt-family bluetooth.img (2,240,512 B, coverage-matrix.csv). Consistent with the Xiaomi `dsp` partition convention - a small filesystem image carrying DSP firmware copies [I]; its contents are unexamined and no in-census adsp/cdsp file md5-matches into it (the census lists files, not image contents) [OPEN].

## Cross-corpus md5-sharing profile [F]

391 rows, 307 distinct md5s. Sharing distribution (devices sharing a given md5 -> Mi_12 rows): 1->70, 2->36, 3->1, 4->3, 5->12, 6->8, 7->1, 8->204, 9->34, 12->14, 14->2, 16->1, 22->2, 27->1, 34->2 (sums 391, python-verified).

| share span | rows | content |
|---|---|---|
| corpus-unique (70 rows) | 70 | 25,492,177 B total: slpi body (14), gfcupid set (10: mdt, b00..b08), 14 remaining TZ mdts + 14 remaining b08s, EVA/VPU/ICP mdts (4), cs35l41 x4, ellv + 5 camera singles, fw_ipa + cpusys_vm.mdt, mbn_ota.md5sum + mbn_build_utc.txt |
| 2 devices (Mi_12 + Mi_12_Pro) | 36 | dsp.img, 20 camera resources, 14 TZ/app segment pairs, mbn_sw.dig |
| 8 devices (the Xiaomi octet) | 204 | all 42 bd_*.elf, most hpnv21/21g tiles, amss.bin, Data.msc/Data20.msc, gptauuid.xml, slpi.b01/b04/b06, most TZ app segments |
| 9 devices (octet + Phone_2) | 34 | unified_ksqs.bin, hpbtfw21.tlv, slpi.b03/b10, hpnv21/21g tiles |
| 12 devices (octet + OnePlus_9/9RT/9_Pro + Phone_2) | 14 | hpnv20 full set + hpbtfw20.tlv, cardapp.b04/b05 |
| 22-27 devices | 4 | evautil64.b04/b05, ops.b04 (22), evautil64.b05 (27) |
| 34 devices | 2 | oem_*_null.txt 0-byte placeholders (Pixels/Fairphone/OnePlus/Xiaomi fleet-wide) |

Leverage reading [I]: one RE pass on the octet-shared files (204 rows) covers the whole Xiaomi SM8450-generation fleet in this corpus; the corpus-unique 70 rows are where Mi_12-specific RE value concentrates (gfcupid, slpi body, dsp.img, the EVA/ICP mdts).

## ISA / interface facts

- `isa_identified` is empty on all 391 rows and `interface_documented=n` on all 391 - honestly un-RE'd at instruction level in the corpus [F]. No instruction-level claim is made here [N].
- db_type=ELF64 on exactly 80 rows, python-verified: 42 bd_*.elf + 15 TZ-app mdts + 14 TZ-app b00s + slpi.mdt + slpi.b00 + cpusys_vm.mdt + amss.bin + fw_ipa_gsi_3.0_w.elf + the 5 vendor/firmware mdt rows. The remaining 311 rows: UNKNOWN 297, FINGERPRINT 9, AUDIOAMP 4, CERT 1 (fw_ipa_gsi_3.0_w.elf - the CERT label on an ELF firmware is a db_type mislabel [I]).
- Verified loader surfaces [F]: mainline remoteproc PAS compatibles `qcom,sm8450-{adsp,cdsp,slpi,mpss}-pas` in sm8450.dtsi (fetched 2026-11-21) cover the adsp/cdsp/slpi/amss-modem images; mainline wm_adsp covers the CS35L41 coefficient files; **no** mainline loader exists for EVA (0 code hits) and none of the bd_*/hpnv NVM tiles beyond the linux-firmware qca subset is a kernel-loaded file (BT NVM tiles are HCI-config downloads by the btusb/qca driver family [I]).
- The split-PIL container grammar (mdt = ELF program-header image, bNN = loadable segments, jsn = servreg JSON) is established in-repo (research/fleet/qdsp6sw-container.md, #606) and applied by the sibling #1168 doc; groups A, B, C(cpusys_vm) and G use exactly that grammar [F].

## Honest negatives

- No payload was fetched, hashed or decoded in this issue: every byte fact is census metadata or a fetched public tree listing; byte-identity between cupid and linux-firmware WCN6750 copies is excluded by size deltas but not diffed. [OPEN]
- dsp.img (64 MiB) contents are unexamined; the Xiaomi dsp-partition semantics is naming-based inference. [OPEN]
- unified_ksqs.bin function is unknown and its absence from the LineageOS manifest is unexplained. [OPEN]
- The census under-covers the vendor-tree subsystem firmware bodies (evass, evass-lt-21, vpu20_4v, CAMERA_ICP bNN sets; a730_zap.b00-b02) and the wider camera tree (GpuKernelRepo.pb, OIS firmware cupid_imx766_bu24618_ois.{coeff,mem,prog} + cupid_wide_bu24618_ois.*, aw8697_haptic.bin, st_fts_l3 touch firmware, cs35l41 .wmfw files) that the LineageOS manifest lists - these are census gaps of the upstream extract, recorded here, not device absences. [F vs LineageOS; the gap itself is [I]]
- The exact function of gfcupid, ellv.bin, arcsat_2sat.bin, MILDC_CALIB, the ArcSoft render resources and the Data.msc/Data20.msc images is vendor-naming inference only. [I]
- The ArcSoft kernel-resource filename tokens are unparsed. [OPEN]
- Whether cupid's modem partition physically carries slpi.b22 (absent from census like adsp.b24) is not decodable from the census alone. [OPEN]

## What would upgrade this finding

1. Fetch one cupid BT NVM tile (e.g. hpnv21.ba0) and the linux-firmware qca/hpnv21.ba0 copy, diff them, and pin the +8 B delta to a header field - settles build-lineage of the WCN6750 NVM fleet.
2. Payload-decode dsp.img (mount/hash the inner filesystem) - first in-corpus look inside a Xiaomi dsp partition image.
3. Payload-decode one SM8450 TZ-app mdt (gfcupid.mdt is the Mi_12-exclusive, largest-value target) - first SM8450 PIL metadata decode in the corpus (sibling #1168 lists the same gap for adsp.mdt).
4. Byte-diff the b03/b07 pairs and the b08 terminals across the 15 trustlet sets to establish whether the shared 3,404 B terminal is a common QSEE stub (one md5 per set today - 15 distinct b08 md5s, so per-set builds).
5. Have the lead split `cpusys_vm.mdt` ownership (other vs tz) into a census rule - this is the only known file whose mdt/bNN halves sit in two families.

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment (Gate -1) and DELTA comment (Gate 0). Checks: linux-firmware qca/ tree + WHENCE (2026-11-21) -> WCN6750 hpnv/hpbtfw family mainlined in subset, nothing else of this family; mainline sm8450.dtsi + code search `qcom,sm8450-eva-pas`, `sm8450-eva` (2026-11-21, adineo-cmd excluded) -> slpi/mpss PAS mainlined, EVA not; `cs35l41-dsp1-spk-prot` code search (2026-11-21) -> mainline wm_adsp component-prefix convention; LineageOS cupid proprietary-files.txt (2026-11-21) -> manifest contrasts recorded above; no public source documents the Mi_12 other-family census itself. DELTA posted; proceeding under it.

Not legal advice; no proprietary payload accessed or committed - all facts are census metadata plus public trees, manifests and specs.
