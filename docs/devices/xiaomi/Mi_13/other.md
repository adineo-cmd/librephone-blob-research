# xiaomi Mi_13 - `other` family status (342 rows - PRESENT, residual catch-all across 16 locations; 9 groups, python-verified sums, 280 distinct md5s, 63 corpus-unique rows, kiwi/WCN7850 WLAN+BT generation set, zero slpi and zero vm-bootsys rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1228](https://github.com/adineo-cmd/open-device/issues/1228)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site f974d67 worktree; matrix last touched at f757b39), `upstream-contribution/blob-database/device-inventory.csv`, the sibling docs docs/devices/xiaomi/Mi_12/other.md (issue [#1174](https://github.com/adineo-cmd/open-device/issues/1174) - the SM8450-generation `other` grammar), docs/devices/xiaomi/Mi_12S_Pro/other.md (issue [#1192](https://github.com/adineo-cmd/open-device/issues/1192), ancidf_model_tee finding, cited not re-derived) and docs/devices/xiaomi/Mi_12T_Pro/other.md (issue [#1210](https://github.com/adineo-cmd/open-device/issues/1210), amss.bin = QCA6490 WLAN correction and the vm-bootsys finding, cited not re-derived), the LineageOS `android_device_xiaomi_fuxi` `proprietary-files.txt` (lineage-22.2, raw.githubusercontent, fetched 2026-11-21), linux-firmware WHENCE (git.kernel.org, fetched 2026-11-21) plus Content-Length probes of qca/hmtnv20.bin, qca/hmtbtfw20.tlv, qca/hmtnv20.b10f, ath12k/WCN7850/hw2.0/{amss,m3}.bin (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8550.dtsi` (torvalds master, fetched 2026-11-21), the public kiwi = WCN7850 mapping (Windows-on-SNAP deployment guide with `firmware_mnt/kiwi/` carrying phy_ucode20.elf/m3.bin/board-2.bin + Qualcomm firmware bulletin "WCN7850 hw2.0 PCI WLAN.HMT.1.1.c7"; web search 2026-11-21), public spec pages (GSMArena, 2026-11-21), GitHub code search hits for the UUID trustlets (HexHive/taemu, TWRP xiaomi 17-series ramdisk-files.txt, 2026-11-21). No payload fetched by this issue; every number below is command output verified with python3 (`python3 -I`, this session).

**Verdict: the `other` family is PRESENT on Mi_13 and is the residual catch-all of the 700-row census - 342 rows, 282,574,263 B (19.37 percent of the device census bytes), 280 distinct md5s, spread over 16 locations.** It decomposes into 9 groups: 20 TrustZone application split-PIL sets (200 rows, mdt + b00..b08 each, 15 named apps + 5 UUID-named), the `kiwi` (WCN7850 FastConnect 7800) WLAN-combo firmware with a byte-duplicated amss.bin (20), the HMT-branch Bluetooth NVM/TLV set (54), modem OS pieces + platform metadata (22), mdt-only subsystem extracts + Cirrus amp + ST54J NFC firmware in odm/firmware + vendor/firmware (9), camera/ArcSoft resources including a 50 MiB and a 36 MiB LSC table and two 11 MB AI super-res models (34), the HRTF audio profile (1), the GPU kbc calibration blob (1), and the radio partition image dsp.img (1). 63 rows (83,710,955 B) are corpus-unique to Mi_13; the dominant share pattern is the 4-device SM8550 quartet (181 rows exactly shared with Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro); amss.bin is 8-shared across a cross-vendor, cross-SoC SM8550/SM8650 set (Edge_40_Pro, OnePlus_11_5G, OnePlus_12, Pad_Pro + the quartet), confirming the sibling #1210 reading that amss.bin is combo-chip WLAN firmware, not a modem OS. Two generation-wide absences distinguish Mi_13 from the SM8450/8475 siblings: zero `slpi` rows (mainline sm8550.dtsi has no SLPI remoteproc and feeds the adspslpi memory region to the aDSP) and zero `vm-bootsys` rows (radio carries only a 64 MiB dsp.img). There is no structural absence of the family itself: it is a census remainder, not a coherent single firmware family, and the census is complete for what it covers (recorded census gaps against the LineageOS manifest below, including 13 on-device CAMERA_ICP.bNN segments with zero census rows).

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 13 (model 2211133G); codename `fuxi` | device-inventory.csv codename cell `fuxi` [F]; GSMArena spec page (2026-11-21) [F] |
| SoC | Qualcomm **SM8550-AB Snapdragon 8 Gen 2** (4 nm); Adreno 740; FastConnect 7800 (WCN7850, Qualcomm codename `kiwi`); platform name `kalama` | GSMArena (2026-11-21) [F]; kiwi mapping per the deployment-guide/WHENCE evidence above [F]; `sku_kalama` audio SKU directory in the LineageOS fuxi manifest [F]; **the matrix soc cell is empty on all 700 rows and the inventory soc cell is empty** - supplied here, flag for the lead |
| released | 2022-12-11 | GSMArena news page (2026-11-21) [F] |
| stock base | `OS2.0.213.0.VMCCNXM` | LineageOS fuxi manifest header (lineage-22.2, fetched 2026-11-21) [F] |
| WLAN/BT combo | FastConnect 7800: the vendor tree carries a `modem/image/kiwi/` firmware directory (amss.bin + regdb_xiaomi.bin) and an `hmt*` Bluetooth set; linux-firmware WHENCE lists hmtbtfw20.tlv/hmtnv20.bin under "qca - Bluetooth support for WCN7850 chips" (lines 5499-5507) and ath12k lists ath12k/WCN7850/hw2.0/{amss.bin, m3.bin} (lines 4256-4260) | coverage-matrix.csv [F]; WHENCE [F]; chip mapping kiwi = WCN7850 [F public]; combo attribution [I] |
| census scope | 700 rows in 9 families (other 342, adsp 116, tz 100, wifi 57, modem 43, boot 15, cdsp 21, gpu 5, bt 1); 1,459,042,077 B; this issue covers the 342-row `other` residual | coverage-matrix.csv [F]; family sum 700 and byte total 1,459,042,077 verified by python this session |
| priority | P3 on all 342 rows; sha256_if_listed, isa_identified empty and interface_documented=n on all 342 | coverage-matrix.csv [F], single python assertion this session |
| inventory cells flagged | Xperia_1_V inventory row says "SM6375 Snapdragon 695" - **wrong**: pdx234 is SM8550 (public specs); it matters here because Xperia_1_V shares Mi_13's unified_ksqs.bin GPU calibration md5. Pad_Pro = `caihong` = OnePlus Pad Pro (SM8650-class), correctly listed under oneplus | device-inventory.csv [F]; public specs [F] |

## Where the family lives (location crosstab) [F]

`other` is residual: every row not matched by a named-family grammar lands here. Census locations and byte loads for Mi_13:

| location | rows | bytes |
|---|---|---|
| `xiaomi/fuxi/modem/image` | 240 | 83,034,711 |
| `xiaomi/fuxi/odm/etc/camera` (+ resources/kernel, resources/kernel/32, /64, 4 render Effect dirs) | 15 + 6 + 2 + 2 + 2 + 3 + 2 + 2 = 34 | 123,327,974 |
| `xiaomi/fuxi/bluetooth/image` | 54 | 773,223 |
| `xiaomi/fuxi/modem/image/kiwi` | 2 | 7,483,158 |
| `xiaomi/fuxi/radio` | 1 | 67,108,864 |
| `xiaomi/fuxi/vendor/firmware` | 3 | 444,780 |
| `xiaomi/fuxi/vendor/gpu/kbc` | 1 | 211,997 |
| `xiaomi/fuxi/odm/etc/audio` | 1 | 164,480 |
| `xiaomi/fuxi/odm/firmware` | 6 | 25,076 |

python3 assertion passed: 240 + 34 + 54 + 2 + 1 + 3 + 1 + 1 + 6 = 342 rows and 83,034,711 + 123,327,974 + 773,223 + 7,483,158 + 67,108,864 + 444,780 + 211,997 + 164,480 + 25,076 = 282,574,263 B. The modem/image container shape is the same one the sibling docs record for the SM8450/8475 generation (585-row 6-family container there), one generation later.

## Group decomposition (342 rows -> 9 groups) [F]

| # | group | rows | bytes | distinct md5s | location |
|---|---|---|---|---|---|
| A | TrustZone application split-PIL sets (20 apps, mdt + b00..b08 each) | 200 | 66,371,620 | 180 | modem/image |
| B | kiwi/WCN7850 WLAN-combo firmware (root copies + kiwi/ dir + phy_ucode + bd_*) | 20 | 16,808,612 | 18 | modem/image, modem/image/kiwi |
| C | Bluetooth HMT-branch NVM/TLV set | 54 | 773,223 | 18 | bluetooth/image |
| D | modem OS pieces + platform metadata | 22 | 7,337,637 | 20 | modem/image |
| E | mdt-only subsystem extracts + Cirrus amp + ST54J NFC firmware | 9 | 469,856 | 8 | odm/firmware, vendor/firmware |
| F | camera tuning + ArcSoft renderer resources | 34 | 123,327,974 | 33 | odm/etc/camera (+ resources) |
| G | HRTF audio profile | 1 | 164,480 | 1 | odm/etc/audio |
| H | GPU kbc calibration blob | 1 | 211,997 | 1 | vendor/gpu/kbc |
| I | radio partition image (dsp.img) | 1 | 67,108,864 | 1 | radio |
| - | total | 342 | 282,574,263 | 280 | - |

python3 assertion passed: group rows sum to 342, group bytes sum to 282,574,263, groups are disjoint. Subfamily census check: misc 292, camera 36, fingerprint 9, audio 4, nfc 1 (python-verified; camera 36 = F 34 + CAMERA_ICP.mdt and evass.mdt in E; fingerprint 9 = the fingerpr bNN rows; audio 4 = the cs35l41 set; nfc 1 = st54j_fw.bin). db_type census: UNKNOWN 266, ELF64 61, FINGERPRINT 9, AUDIOAMP 4, NFC 1, CERT 1 (python-verified).

### Group A - TrustZone application split-PIL sets (200 rows)

20 named applications, each a complete Qualcomm split-PIL trustlet: `*.mdt` (4,752 B each - one byte larger class than the siblings' 4,272 B, a new build grammar) + `b00` (568 B each) + `b01..b08` (each `b08` 4,184 B):

cardapp, evautil64, faceutils, fingerpr, gffuxi, ic3, ic4, mfido, miriskm, mkeybag, mlipay, ops, otrpapp, secauth, seccammi, 05B04A44-BF30-42DF-9E2F-B366B980ED19, 32552B22-89FE-42B4-8A45-A0C4E2DB0326, 3d08821c-33a6-11e6-a1fa-089e01c83aa2, A985D3EB-3B52-4D44-BE6C-628A813561E8, FD719D50-FFFB-11EB-9A03-0242AC130003.

- All 20 sets are structurally identical: 10 files, mdt + b00..b08, no gaps (python-verified per set). Every set carries the same internal duplication as the sibling generations: `b03` and `b07` are byte-identical within the set (python-verified in all 20), so 200 rows collapse to 180 md5s, with zero md5 overlap across sets.
- Trustlet roster vs Mi_12T_Pro's 15 sets (#1210): 10 names are identical (cardapp, evautil64, fingerpr, ic3, mfido, miriskm, mlipay, ops, otrpapp, secauth); fuxi adds faceutils, gffuxi, ic4, mkeybag, seccammi and the 5 UUID-named apps; diting's devauth, eseservice, gfdit, gpqese, mldapta have no fuxi counterpart in the census.
- `seccammi` is the largest set: 36,788,555 B, `b01` alone 34,827,936 B (4-share quartet) - the camera-secure trustlet reading carries over from cupid's seccammil (#1174) [I, name-based].
- `gffuxi` is the Mi_13-exclusive trustlet, the direct analog of cupid's gfcupid and diting's gfdit: all 10 files are corpus-unique, 12,678,782 B total (b04 7,243,084 B, b01 5,216,288 B are the two largest segments). The `gf*` prefix pairing (gfcupid/gfdit/gffuxi, one per device codename) reads as a per-device Goodix trustlet [I].
- `fingerpr` is again the only set whose bNN rows carry db_type=FINGERPRINT: 14,024,513 B total, b01 8,814,764 B (4-share quartet - a different build from diting's 7-share 6,909,820 B b01) [F].
- The 5 UUID-named apps are Qualcomm vendor-image trustlets that persist across generations: TWRP device trees for Xiaomi 17-series devices (nezha, pudding, pandora, popsicle) list the same UUIDs plus 7C2FC71B as `vendor/firmware_mnt/image/*.bNN` ramdisk entries (GitHub code search 2026-11-21), and HexHive/taemu (EPFL QSEE-TA emulator) carries `3D08821C-33A6-11E6-A1FA-089E01C83AA2.ta` in its public fuzzing dataset - public binary coverage exists for that UUID, but no public format/interface documentation [F]. Function mapping of all 5 is [OPEN].
- Sharing spans: 48 of the 63 corpus-unique rows are the mdt/b08 terminals of this group - all 20 mdt heads (each set's own build) + all 20 b08 terminals + the 8 gffuxi body segments (gffuxi.mdt/gffuxi.b08 are inside the 40). b00 spans: 13 of the 20 b00s are 4-shared with exactly the quartet (Mi_13_Pro/Poco_F6_PRo/Redmi_K60_Pro), 6 are 7-shared (05B04A44, FD719D50, evautil64, ic3, ic4, ops - the heptad Edge_40_Pro, Mi_13, Mi_13_Pro, Nord_CE4, OnePlus_11_5G, Poco_F6_PRo, Redmi_K60_Pro), and gffuxi.b00 is corpus-unique. Body segments: 34 rows are 7-shared with the heptad (evautil64.b00-b03/b06, ic3.b00-b06, ic4.b00-b06, ops.b00-b03/b06, 05B04A44.b02, FD719D50.b02/b04); mkeybag.b04 is 7-shared with a different heptad (Mi_12S_Ultra, Mi_13, Mi_13_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro); cardapp.b04/b05 are 12-shared (the Xiaomi SM8450/8475 octet + this quartet - the same wide span #1174 records for cupid); evautil64.b04 22, evautil64.b05 27, ops.b04 22, ops.b05 16 devices - the wide fleet-sharing of Qualcomm OTA trustlets continues into the 8550 generation [F spans].
- Interpretation [I]: SM8550-generation QSEE trustlets (identity wallets mlipay/miriskm/mfido/mkeybag/cardapp, OEM security ops/otrpapp/secauth, camera TZ support evautil64/ic3/ic4/seccammi/faceutils, fingerprint fingerpr, Goodix gffuxi). Function mapping rests on vendor naming and the public QSEE trustlet format (Check Point 2019, Quarkslab, LSE MBN guide - cited from the sibling docs).

### Group B - kiwi/WCN7850 WLAN-combo firmware (20 rows, 16,808,612 B)

| file | rows | bytes | md5 | share |
|---|---|---|---|---|
| amss.bin | 2 (modem/image + kiwi/) | 7,458,880 each, byte-identical | `81f39ee463469b02a5098599ad792f03` | 8 |
| regdb_xiaomi.bin | 2 (modem/image + kiwi/) | 24,278 each, byte-identical | `018738528b0813591ad6dc288226e3e3` | 4 (quartet) |
| phy_ucode.elf | 1 | 299,660 | `93bb73f7f14c0d7f8a548c70fa7b60a2` | 8 |
| phy_ucode20.elf | 1 | 299,660 | 3-share (Mi_13, Mi_13_Pro, Poco_F6_PRo) | 3 |
| bd_*.elf | 14 | 88,720..88,972 (1,242,976 total, 14 distinct md5s) | e.g. bd_m1.elf `d6cf233099ac694f2bd8efe4b8480d68` | 4 (quartet) |

- **amss.bin is the WCN7850 WLAN-combo firmware, not the modem processor OS** - the sibling #1210 correction, now confirmed on the 8550 generation: fuxi ships the same 7,458,880 B file twice (root + `kiwi/` extract directory); its md5 is byte-identical across 8 devices spanning two SoCs - Edge_40_Pro (SM8550), OnePlus_11_5G (SM8550), OnePlus_12 (SM8650), Pad_Pro (`caihong`, OnePlus Pad Pro, SM8650-class) and the SM8550 quartet - which an SoC-specific modem build cannot be, and `kiwi` is the public Qualcomm codename of the WCN7850/FastConnect 7800 combo (mainline ath12k serves `ath12k/WCN7850/hw2.0/amss.bin`; Content-Length probe 6,090,816 B vs fuxi 7,458,880 B - same file family, different build) [F evidence chain; conclusion [I], consistent with #1210's correction of #1174].
- `modem/image/kiwi/` is the SM8550-generation analog of the `qca6490/` extract directory the siblings record on the 12S-class devices: a 2-row directory (amss.bin + regdb_xiaomi.bin) whose contents are byte-identical duplicates of the modem/image root copies [F].
- `bd_*.elf` = 14 board-data ELFs (bd_m1/m1gl/m2/m2gl/m3/m3gl/m11/m11gl/m18/m18gl/n11/n11gl/n81a/n81agl, all 4-share quartet) - the same grammar diting records as 42 rows for the 6490 generation; the smaller fuxi set matches the kiwi generation's board-data model (public WCN7850 firmware uses board-2.bin built with ath12k-bdencoder) [F names; board-data reading [I] per #1210].
- `phy_ucode.elf`/`phy_ucode20.elf` (299,660 B each, different builds) = WLAN PHY microcode, present in public WCN7850 firmware layouts [I, name-based]. Both are exactly the byte size of mainline `ath12k/WCN7850/hw2.0/m3.bin` (299,660 B, probe 2026-11-21) - recorded as a size coincidence, not claimed as byte-identity.

### Group C - Bluetooth HMT-branch NVM/TLV set (54 rows, 773,223 B, 18 md5s)

| subset | rows | bytes | share |
|---|---|---|---|
| hmtnv20.bin + 47 segments (b14, b16-b19, b1e-b24, b29-b3b, b104-b113) | 48 | 435,880 | 4 (quartet) |
| hmtnv10.bin + hmtnv10.b0c | 2 | 13,602 | 8 |
| hmtbtfw20.tlv + hmtbtfw20.ver | 2 | 232,399 | 4 (quartet) |
| hmtbtfw10.tlv + hmtbtfw10.ver | 2 | 91,342 | 8 |

- The `hmt` prefix is the HAMILTON/HMT firmware branch: linux-firmware WHENCE lines 5499-5507 list `qca/hmtbtfw20.tlv` (Version BTFW.HAMILTON.2.0.1-00349-WOS_PATCHZ-2) and `qca/hmtnv20.bin` (+ .b10f/.b112/.b201/.b202 segment files) under "Driver: qca - Qualcomm Atheros Bluetooth support for WCN7850 chips" - the same file grammar Mi_13 ships, for the same combo chip [F]. The QCA6390-generation predecessors (htbtfw20.tlv/htnv20.bin, BTFM.HST branch, WHENCE lines 5490-5492) and the 8450-generation HP branch (hpnv/hpbtfw, diting's 113-row set) complete the per-combo-generation prefix table [F].
- Not byte-identical with mainline: fuxi hmtnv20.bin 9,036 B vs mainline 9,508 B; hmtbtfw20.tlv 232,348 B vs mainline 270,120 B (Content-Length probes 2026-11-21) - an earlier build of the same firmware family [F].
- The hmtnv20 set is heavily internally duplicated: 48 rows collapse to 12 distinct md5s (sizes cluster at 9,036/9,084/9,100/9,153/9,564 B; the 9,036 B md5 `efb6ade2...` alone covers 18 rows). Segment indices are sparse (b15, b1a-b1d, b25-b28 absent; nothing between b3b and b104) - [OPEN] why.

### Group D - modem OS pieces + platform metadata (22 rows, 7,337,637 B)

| file | bytes | md5 | share |
|---|---|---|---|
| ancidf_model_tee | 4,271,903 | `5bd954e0968922a759fcc4a821645919` | 7 |
| Data20.msc | 1,455,586 | `989a8e88a2acd0cd4086884dd6f70cb6` | 4 (quartet) |
| Data.msc | 1,455,171 | `bdadd14504b797d0f77af81b1ee8743f` | 4 (quartet) |
| mbn_ota.md5sum | 36,052 | (unique) | 1 |
| oem_sw.txt | 18,546 | (3-share with Mi_13_Pro, Redmi_K60_Pro) | 3 |
| mbn_sw.txt | 19,648 | (3-share) | 3 |
| oem_sw_ct_volte.txt | 6,689 | (4-share) | 4 |
| gptauuid.xml | 10,399 | `5ea13584a60c6498c60f5ca928331a7c` | 5 |
| fw_ipa_gsi_5.5_w.elf | 36,760 | `22e0e9320a16b739b6abd7e9bd7b600c` | 1 |
| cpusys_vm.mdt | 16,500 | `b47c8347205db5412f239bc76377669a` | 1 |
| qdss_trace_config_v1.cfg / v2.cfg | 4,742 / 4,911 | (8-share / 4-share) | 8 / 4 |
| mbn_hw.txt, mbn_hw.dig, mbn_sw.dig, mbn_build_utc.txt | 407 / 32 / 32 / 10 | - | 5 / 4 / 3 / 1 |
| oem_hw.txt, oem_hw_ss.txt | 68 / 59 | (4-share) | 4 |
| oem_hw_dsds.txt, oem_hw_cert.txt | 61 / 61 | **byte-identical** `007bf5ee381ec1a1df9a5e5621a97b90` | 4 |
| oem_sw_null.txt, oem_hw_null.txt | 0 / 0 | `d41d8cd98f00b204e9800998ecf8427e` (empty-file md5) | 34 |

- `ancidf_model_tee` (4,271,903 B) is byte-identical with the file #1192 recorded as undocumented: same md5, 7-share with the 12S trio + this quartet. Web and code search for the exact name still return 0 results (2026-11-21). The `tee` suffix suggests a TrustZone-consumed model payload [I]; function unknown, [OPEN].
- `Data.msc`/`Data20.msc` are new quartet builds (1,455,171/1,455,586 B, distinct md5s from cupid's 889,524/916,071 B 8-share copies) - the EFS/NV-container hypothesis carries over [I]; `gptauuid.xml` grows to 10,399 B (5-share) from cupid's 6,194 B - the SM8550 partition layout changed [F].
- `fw_ipa_gsi_5.5_w.elf` is db_type=CERT on an ELF firmware file - the same db_type mislabel class as cupid's (40,076 B) and diting's fw_ipa_gsi_3.0_w.elf (40,376 B, #1210); corpus-unique to Mi_13 here. IPA = IP-accelerator offload firmware; gsi 5.5 = the GSI generation [I]. Not in linux-firmware WHENCE (fetched 2026-11-21) - not mainlined [F].
- `cpusys_vm.mdt` is the family-boundary quirk, one generation later: 16,500 B corpus-unique mdt in `other`, while `cpusys_vm.b00..b03` (180 + 516,096 + 4,621 + 16,320 = 537,217 B, db_type=SECURITY) sit in the `tz` family - one split-PIL image split across two census families (fuxi's body has 4 segments vs diting's 5) [F].
- `oem_sw_null.txt`/`oem_hw_null.txt` are 0-byte files whose md5 (the empty-file md5) is shared with 34 corpus devices - fleet-wide platform placeholders [F].

### Group E - mdt-only subsystem extracts + Cirrus amp + ST54J NFC firmware (9 rows, 469,856 B)

| file | bytes | md5 | db_type | share |
|---|---|---|---|---|
| CAMERA_ICP.mdt | 5,484 | `fce3c902273f22b9447f3b1d570aec71` | ELF64 | 1 |
| evass.mdt | 5,404 | `08dc30bb670b21f7861dbfe950efb385` | ELF64 | 4 |
| evass.mdt | 5,404 | `0e45fdb030f4ae0cb1a85cac30b4b593` | ELF64 | 4 |
| T-cs35l41-dsp1-spk-prot.bin | 5,516 | `88d3bb5ff5f13444b3cd55eec926a36f` | AUDIOAMP | 1 |
| T-cs35l41-dsp1-spk-cali.bin | 1,576 | `c07adfe2c8bd1ebae19fbc72bc2e0004` | AUDIOAMP | 1 |
| B-cs35l41-dsp1-spk-prot.bin | 5,516 | `71daeaf60465229160d379b6e9b06ed2` | AUDIOAMP | 1 |
| B-cs35l41-dsp1-spk-cali.bin | 1,580 | `82e0b665c7fa8bb36841abd72f6b9db5` | AUDIOAMP | 1 |
| st54j_fw.bin | 219,688 | `86a23d642374de60b397caa8d0ecaccb` | NFC | 4 |
| st54k_conf_38.4MHz.bin | 219,688 | `86a23d642374de60b397caa8d0ecaccb` | UNKNOWN | 4 |

- `st54j_fw.bin` = STMicroelectronics ST54J NFC controller firmware (single-die CLF+SE, Android Ready SE; distributed via the ST54-android-vendor packages, loaded by the ST NFC HAL) [F public product identity; load path [I]]. `st54k_conf_38.4MHz.bin` is **byte-identical** with st54j_fw.bin (same md5, same size) - a config-named byte-duplicate of the firmware, [OPEN] why.
- The 4 `cs35l41-dsp1-spk-{prot,cali}.bin` rows (T/B = top/bottom Cirrus CS35L41 smart amps) are corpus-unique calibration variants; the generic prot bin is mainlined as `cirrus/cs35l41-dsp1-spk-prot.bin` (WHENCE line 8091) and the LineageOS manifest adds the two `cs35l41-dsp1-spk-{cali,prot}.wmfw` files and B/T-handfree/music/handset.txt which the census does not carry [F].
- `evass.mdt` exists in two different builds (odm/firmware vs vendor/firmware, same size different md5) - the EVA (encode/video) subsystem mdt head, mdt-only in both locations [I, name-based]; why two builds [OPEN].
- `CAMERA_ICP.mdt` is corpus-unique and mdt-only - and it is the biggest census gap in this family: the LineageOS fuxi manifest lists `odm/firmware/CAMERA_ICP.b00..b12` (13 segment files on device) with **zero** census rows anywhere on Mi_13 [F manifest; census gap].

### Group F - camera tuning + ArcSoft renderer resources (34 rows, 123,327,974 B, 33 md5s)

| subgroup | rows | bytes | representative facts |
|---|---|---|---|
| odm/etc/camera top level | 15 | 118,606,166 | night_align_lsc_tbl_40963072.bin 50,331,648 B and _40962304.bin 37,748,736 B (pair 88,080,384 B, 6-share: Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_13, Mi_13_Pro, Poco_F5 - exactly the pair #1192 records); mialgo_nn_xmi_slmt_4x_1080p.bin 11,619,895 B + _720p.bin 11,436,300 B (3-share with Mi_13_Pro, Poco_F6_PRo); mialgo_ailab_raw_hdr.bin 1,596,596 B and mdbokeh_{sft,prt,ngt,bwt}.bin 491,920 B each (2-share with Mi_13_Pro; **mdbokeh_ngt and mdbokeh_sft are byte-identical**, md5 `fc91c189...`); ellv.bin 3,635,040 B corpus-unique (md5 `c7569e596d720f1015f5cbdfcb0062e4`; the LineageOS manifest ships `odm/lib64/libellv.so` as its userspace half); mage_yuv_hdr_opencl.bin 260,780 B (2-share with Poco_F6_PRo); CFR_para_UW_V01.bin 8,128 B, MILDC_CALIB_0x01.bin 550 B, arcsat_{2sat,3sat}.bin 367/446 B corpus-unique |
| resources/kernel (+/32, /64) | 10 | 1,359,540 | numeric model pairs 1720888_32/64.bin (225,224/233,112 B), 2821809890_32/64.bin (36,552/40,840 B), 3711416411_32/64.bin (11,596/12,876 B) 3-share; the s31bc24e5.../t31bc24e5... long-md5-named pair in 32/64 builds (10,072/10,076 and 386,880/392,312 B, 3-share) - the names are md5 concatenations: two components identified as md5("a") = `0cc175b9...` and md5("b") = `92eb5ff...`; the 31bc24e5... component unresolved [OPEN] |
| render/Effect BrightEye + BrightEyeV3 | 5 | 1,530,140 | LeftEye/RightEye.bin 360,028 B each (3-share); eye_pupil.bin 90,028 B (9-share incl. the 12S trio and both Poco F5s); left_eye/right_eye.bin 360,028 B (3-share) |
| render/Effect 60_Makeup ModeClassical + ModeNative | 4 | 1,832,128 | sh.bin 788,436 B (ModeClassical copy 9-share, ModeNative copy 3-share - two different builds under one name) and Eyebrow.bin 127,628 B (both copies 3-share, different md5s) |

- The 9-share set (eye_pupil.bin, sh.bin ModeClassical copy) reads as the shared ArcSoft/ArcSoft-class retouch payload across the 12S/13 generations [I, name-based].

### Groups G, H, I - audio, GPU calibration, radio (3 rows, 67,485,341 B)

- `hrtf5c.bin` (164,480 B, md5 `2a47164eed5282f27ad503a28c7b71a0`, odm/etc/audio) is 12-shared: the Xiaomi SM8450/8475 octet + this SM8550 quartet - an HRTF (head-related transfer function) audio profile for the Dirac/Mi Sound stack, generation-stable [I, name-based].
- `unified_ksqs.bin` (211,997 B, md5 `7e747992f5683d0c1a713b7d749857e3`, vendor/gpu/kbc) is 10-shared with Edge_40_Pro, Nord_CE4, OnePlus_11_5G, OnePlus_12R, Xperia_1_V, Xperia_5_V + this quartet - the SM8550-generation Adreno GPU kbc calibration, cross-vendor (the same slot diting's census records in vendor/gpu/kbc) [F spans; function [I] per sibling grammar].
- `dsp.img` (67,108,864 B = exactly 64 MiB, md5 `62f08cfbec9a57064c7b7b0ef24d813c`, radio) is corpus-unique - the only radio-partition extract on fuxi. No `vm-bootsys.img` exists anywhere on the device (0 rows in all families): the 256-270 MiB vm-bootsys radio image the siblings record for the 12S generation is absent on all four SM8550-quartet members (0 rows each) - either a structural generation change or a generation-wide census-extraction gap; unresolved, [OPEN].

## Share structure (corpus-wide md5 spans) [F]

| devices sharing an md5 | rows | bytes | who |
|---|---|---|---|
| 1 | 63 | 83,710,955 | the mdt/b08 terminal class (all 20 TZ mdt heads + all 20 TZ b08 terminals + CAMERA_ICP.mdt + cpusys_vm.mdt), the 8 gffuxi body segments, dsp.img, fw_ipa_gsi_5.5_w.elf, the 4 cs35l41 bins, ellv.bin, CFR_para, MILDC_CALIB, arcsat pair, mbn_ota.md5sum, mbn_build_utc.txt |
| 4 (SM8550 quartet: Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro) | 181 | - | the hmtnv20/hmtbtfw20 set, all 14 bd_*.elf, 13 TZ b00s + the b01..b07 bodies of 13 TZ sets (the quartet-b00 dozen + fingerpr), seccammi.b01, fingerpr.b01, Data.msc/Data20.msc, regdb_xiaomi.bin, st54j_fw.bin, evass.mdt, oem_hw/mbn metadata, camera AI models |
| 8 (Edge_40_Pro, OnePlus_11_5G, OnePlus_12, Pad_Pro + quartet) | 8 | 15,327,106 | amss.bin (2 rows), hmtbtfw10.tlv/.ver, hmtnv10.bin/.b0c, phy_ucode.elf, qdss_trace_config_v1.cfg - the cross-vendor SM8550/SM8650 WLAN-combo octet-analog |
| 12 (Xiaomi SM8450/8475 octet + quartet) | 3 | 165,688 | cardapp.b04, cardapp.b05, hrtf5c.bin |
| 34 (fleet) | 2 | 0 | oem_sw_null.txt, oem_hw_null.txt (0-byte files) |
| 3 / 5 / 6 / 7 / 9 / 10 / 11 / 16 / 22 / 27 | 24 / 6 / 5 / 34 / 2 / 3 / 1 / 1 / 2 / 1 | - | see group sections (3-share = quartet minus Redmi_K60_Pro for camera models; 7-share = the Edge_40_Pro/Nord_CE4/OnePlus_11_5G heptad; 10-share = the unified_ksqs GPU-calibration set; 27-share = evautil64.b05) |

python3-verified histogram: 1:63, 2:6, 3:24, 4:181, 5:6, 6:5, 7:34, 8:8, 9:2, 10:3, 11:1, 12:3, 16:1, 22:2, 27:1, 34:2 (sum 342). Byte-identity with sibling devices: 13 rows (93,234,383 B) are byte-identical with Mi_12S_Pro `other` rows (night_align pair + ancidf_model_tee + eye_pupil + the 9-share sh.bin + 8 tiny rows totalling 3,632 B); 10 rows (882,096 B) with Mi_12T_Pro; 8 rows (3,632 B) with Mi_12 (cardapp.b04/b05, evautil64.b04/b05, ops.b04/b05, the two 0-byte nulls). The 12S-generation vm-bootsys.img (256-270 MiB) and slpi sensor-island rows have no fuxi counterpart - see below.

## Generation contrasts vs the SM8450/8475 siblings [F unless noted]

1. **WLAN-combo extract directory renamed with the combo generation**: `qca6490/` (12S-class devices) -> `kiwi/` (fuxi); same 2-row byte-duplicate shape (amss.bin + regdb).
2. **Bluetooth firmware branch renamed**: hp* (hpnv21/hpbtfw21, diting 113 rows) -> hmt* (hmtnv20/hmtbtfw20, fuxi 54 rows) - matching the per-chip linux-firmware qca/ sections (WCN6750-class HP branch vs WCN7850 HMT branch).
3. **Zero slpi rows, generation-wide**: mainline sm8550.dtsi has no SLPI remoteproc (only `qcom,sm8550-{mpss,adsp,cdsp}-pas`) and the reserved `adspslpi_mem` region (line 983) is consumed by the aDSP `memory-region` (line 3183) - consistent with the sensor island merging into the aDSP on Kalama [F mainline structure; reading [I]]. Contrast: 26-row slpi sets in `other` on Mi_12/12S_Pro/12T_Pro.
4. **Zero vm-bootsys rows, generation-wide** (all four quartet members): radio = dsp.img only. Structural or census gap - [OPEN].
5. **mdt grammar**: 4,752 B mdt heads (fuxi) vs 4,272 B (SM8450/8475 siblings); b08 4,184 B vs siblings' 3,704 B - the split-PIL container grew one byte-class.
6. **gptauuid.xml** 10,399 B (5-share) vs 6,194 B (8-share) - partition-UUID metadata updated for the SM8550 layout.

## Census gaps recorded (LineageOS fuxi manifest, lineage-22.2, fetched 2026-11-21)

The manifest (1,221 lines, `OS2.0.213.0.VMCCNXM` header) ships device files the census does not carry; the census targets firmware payloads, so these are coverage notes, not census errors:

- `odm/firmware/CAMERA_ICP.b00..b12` - 13 on-device segment files, **0 census rows in any family** (only CAMERA_ICP.mdt was captured). The largest single gap in this decomposition.
- `odm/firmware/cs35l41-dsp1-spk-{cali,prot}.wmfw` + `B/T-handfree.txt`, `B/T-music.txt`, `T-handset.txt` - amp WMFW and tuning texts absent from the census.
- `odm/etc/audio/misound_res_spk_power_{game,video}.bin` + the `odm/etc/audio/sku_kalama/` XML set - Mi Sound resources absent (the `sku_kalama` directory name independently confirms the Kalama platform [F]).
- `odm/etc/camera`: 460 manifest entries vs 34 census rows (af_*.dlc, aivsModels1-3, arcsoft ini, beauty json, ellv_params.xml, ...). The census's camera selection is a small payload subset by design.

## ISA / interface facts

- isa_identified is empty and interface_documented=n on all 342 rows - honestly un-RE'd at the census level; nothing below upgrades the census cells, it records public interface evidence per group [F census; public facts follow].
- Group B/C (WCN7850): the load interface is mainline-public - ath12k serves `ath12k/WCN7850/hw2.0/{amss.bin, m3.bin, board-2.bin}` and btusb/qca serves `qca/hmtbtfw20.tlv` + `qca/hmtnv20.bin(.bNN)` for "WCN7850 chips" (WHENCE, fetched 2026-11-21) [F]. The fuxi copies are same-family different-build (size probes above) [F].
- Group E (CS35L41): mainline ALSA cs35l41 driver + linux-firmware `cirrus/cs35l41-dsp1-spk-prot.bin` define the DSP-firmware load path; the T/B pairs are per-speaker calibration variants [F public driver; variant reading [I]].
- Group E (ST54J): ST54J is Android Ready SE compliant (st.com); the NFC HAL loads st54j_fw.bin [F product identity; load path [I]]. Not mainlined (WHENCE grep empty) [F].
- Group A (QSEE trustlets): the split-PIL mdt/bNN container format is public (Check Point 2019, Quarkslab, LSE MBN guide - cited from siblings); HexHive/taemu publicly fuzzes the 3D08821C UUID trustlet binary. No public interface documentation exists for any of the 20 fuxi trustlet functions [F coverage; [OPEN] functions].
- Group D (IPA): fw_ipa_gsi_5.5_w.elf is not in linux-firmware WHENCE - not mainlined [F].

## Honest negatives ([OPEN])

1. `ancidf_model_tee` (4,271,903 B): function unknown; still undocumented anywhere we searched (2026-11-21), carried from #1192 with the same md5 and now extended to a 7-device span.
2. The 5 UUID trustlets (05B04A44, 32552B22, 3d08821c, A985D3EB, FD719D50): functions unmapped; 3D08821C has public fuzzing coverage (HexHive/taemu) but no identification.
3. `hmtnv20` segment-index gaps (b15, b1a-b1d, b25-b28 absent; b3b->b104 jump) unexplained.
4. `evass.mdt` ships in two different builds (odm/firmware vs vendor/firmware, same size) - reason unknown.
5. `mdbokeh_ngt.bin` == `mdbokeh_sft.bin` byte-identical - reason unknown.
6. `st54k_conf_38.4MHz.bin` byte-identical with `st54j_fw.bin` - a config-named duplicate of the NFC firmware; reason unknown.
7. The long md5-joined camera file names (s31bc24e5.../t31bc24e5...): md5("a") and md5("b") components identified; the `31bc24e5f6c4ef1752c77f3a22ad1ffc` component unresolved.
8. `vm-bootsys.img` absence on the whole SM8550 quartet: structural generation change vs census-extraction gap - unresolved without a full SM8550 OTA extract.
9. `CAMERA_ICP.b00..b12` census backfill (13 on-device rows, 0 census rows) - the decomposition above is census-scoped and does not cover those bytes.
10. Which Xiaomi pad/tablet the corpus `Pad_Pro` (caihong) SoC actually is - its inventory SoC cell is empty; it rides the amss.bin 8-share either way.

## What would upgrade this finding

1. Census backfill of CAMERA_ICP.b00..b12 (and size/md5 capture) so Group E's ICP subsystem can be decomposed like the TZ sets.
2. A full SM8550 OTA extract (fuxi or nuwa) that includes the radio partition image list, to settle vm-bootsys structural-vs-gap.
3. strings/headers of `gffuxi` (12,678,782 B, corpus-unique): the Goodix trustlet is the highest-value un-RE'd fuxi-exclusive blob; Goodix sensor documentation is partially public.
4. Byte-comparison of fuxi's hmt*/amss.bin/phy_ucode* against pinned linux-firmware WCN7850 releases to date the phone's combo firmware build.
5. strings of `ellv.bin` + the shipped `libellv.so` to identify the "ellv" subsystem (name unresolved in all public sources we searched).
6. Identify the 5 UUID trustlets by matching their mdt hashes against the taemu dataset's .ta images.

## RULE 0 record

- 2026-11-21T09:33:55Z: CLAIM ZC-1 zcode posted (first comment, re-verified).
- 2026-11-21: SEARCH comment (Gate -1) and Gate 0 DELTA comment posted; no PRIOR-ART found for the device-scoped decomposition.
- 2026-11-21: deliverable pushed to feat/open-device-site; byte-verified against the remote; DONE comment with the remote sha.
- Evidence classes: [F] = command output from the local census clone or a fetched public source with access date; [I] = labeled inference from names/shapes/spans. Every sum in this document re-verified with python3 -I this session (assertion script: totals, location crosstab, group sums, share histogram, sibling byte-identity counts, and the detail rows all asserted equal before writing).

This document analyzes firmware containers at the metadata level only (sizes, hashes, names, locations). It is not legal advice; no proprietary payload bytes were fetched or committed.
