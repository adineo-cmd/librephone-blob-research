# xiaomi Mi_12T_Pro - `other` family status (403 rows - PRESENT, residual catch-all family across 14 locations; 11 groups, python-verified sums, 316 distinct md5s, 79 corpus-unique rows, full-set byte-identity with Mi_12 for the Bluetooth and board-data groups)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1210](https://github.com/adineo-cmd/open-device/issues/1210)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 5c9a4b6 worktree), `upstream-contribution/blob-database/device-inventory.csv`, the sibling docs docs/devices/xiaomi/Mi_12/other.md (issue [#1174](https://github.com/adineo-cmd/open-device/issues/1174), the SM8450-generation `other` grammar, cited not re-derived) and docs/devices/xiaomi/Mi_12T_Pro/adsp.md (issue [#1204](https://github.com/adineo-cmd/open-device/issues/1204), diting identity, cited not re-derived), the LineageOS `android_device_xiaomi_diting` `proprietary-files.txt` (lineage-22.2, raw.githubusercontent, fetched 2026-11-21), the UniXNU-diting fork manifest comment naming "QCA6490 amss/amss20/m3/regdb" as modem-partition firmware (GitHub code search, fetched 2026-11-21), the Qualcomm gpqese eSE HAL headers `securemsm/esehal/gpqese/` in tadiphone-caf/vendor_qcom_proprietary (GitHub code search, fetched 2026-11-21), linux-firmware WHENCE plus Content-Length probes of qca/hpnv21.bin, qca/hpbtfw21.tlv, qca/hpnv21g.bin, ath11k/QCA2066/hw2.1/{amss,m3}.bin (git.kernel.org, fetched 2026-11-21), vm-bootsys partition tooling (fish-shell fastboot completions, FlyGoat/miui_ota_to_fastbootd, UN1CA sm8450 recovery.fstab, aeroratech/meta-qti-bsp; GitHub code search, fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (cited from the #1174 fetch, 2026-11-21), and public spec pages (2026-11-21). No payload fetched by this issue; every number below is command output verified with python3 (`python3 -I`, this session).

**Verdict: the `other` family is PRESENT on Mi_12T_Pro and is the residual catch-all of the 819-row census - 403 rows, 430,460,697 B (33.22 percent of the device census bytes), 316 distinct md5s, spread over 14 locations.** It decomposes into 11 groups: 15 TrustZone application split-PIL sets (150 rows, including the diting-exclusive `gfdit` trustlet and the eSE trustlet `gpqese`), the slpi sensor-island firmware (26), modem OS pieces + platform metadata (7), the `qca6490` WLAN-combo firmware directory with a byte-duplicated amss.bin (2), 42 WLAN board-data ELFs (42), mbn/oem metadata texts (14), the Bluetooth NVM/TLV sets (113), mdt-only subsystem extracts + Cirrus amp + Goodix touch firmware in vendor/firmware (11), camera/ArcSoft resources including a 24.6 MiB AI segmentation model and two 4 MB ANC binaries (35), the GPU kbc calibration blob (1), and the radio partition images dsp.img + a 256 MiB vm-bootsys.img (2). 79 rows (32,899,699 B) are corpus-unique to Mi_12T_Pro; the dominant share pattern is the 8-device Xiaomi SM8450/8475-generation octet (203 rows exactly, plus 2 rows at 8-share where Poco_F5 swaps for Phone_2); and the Bluetooth NVM set (113 rows, 54 md5s) and the 42-row bd_*.elf set are each byte-identical, file for file and md5 for md5, with Mi_12's corresponding sets. There is no structural absence: the family is a census remainder, not a coherent single firmware family, and the census is complete for what it covers (with recorded partial-coverage contrasts against the LineageOS manifest, below).

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12T Pro (global model 22081212UG); codename `diting` | sibling doc #1204 identity table [F]; mi.com global specs + Notebookcheck (2026-11-21) [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1** (4 nm); Adreno 730; Hexagon V69 DSP | sibling doc #1204 (public spec pages 2026-11-21) [F]; **the upstream inventory SoC cell is empty** - supplied there, flag for the lead; the LineageOS devicetree file is literally named `qcom/diting-sm8475.dtsi` [F] |
| released | 2022-10-06 | sibling doc #1204 [F]; inventory released-year cell also empty - flag |
| stock base | `OS2.0.203.0.VLFMIXM` | sibling doc #1204 (LineageOS diting manifest header) [F] |
| WLAN/BT combo | QCA6490-class FastConnect combo: the vendor tree carries a `modem/image/qca6490/` firmware directory (amss.bin, amss20.bin, m3.bin, regdb.bin) | coverage-matrix.csv [F]; the UniXNU-diting manifest comment "QCA6490 amss/amss20/m3/regdb" names these as modem-partition firmware [F]; chip mapping from directory name [I] |
| census scope | 819 rows in 9 families (other 403, wifi 179, tz 91, adsp 67, modem 39, boot 14, cdsp 19, gpu 6, bt 1); 1,295,868,507 B; this issue covers the 403-row `other` residual | coverage-matrix.csv + device-inventory.csv [F]; family sum 819 and byte total 1,295,868,507 verified by python this session |
| priority | P3 on all 403 rows; sha256_if_listed, isa_identified empty and interface_documented=n on all 403 | coverage-matrix.csv [F], single python assertion this session |

## Where the family lives (location crosstab) [F]

`other` is residual: every row not matched by a named-family grammar lands here. The census locations and their family mix for Mi_12T_Pro:

| location | all families | `other` share |
|---|---|---|
| `xiaomi/diting/modem/image` | 585 rows in 6 families (wifi 176, other 239, tz 85, adsp 28, modem 38, cdsp 19) | 239 rows |
| `xiaomi/diting/bluetooth/image` | other only | 113 rows |
| `xiaomi/diting/vendor/etc/camera` (+ resources/kernel, resources/kernel/32, resources/kernel/64, 4 render Effect dirs) | other only | 16 + 6 + 2 + 2 + 9 = 35 rows |
| `xiaomi/diting/vendor/firmware` | gpu 5, other 11 | 11 rows |
| `xiaomi/diting/modem/image/qca6490` | wifi 3, other 2 | 2 rows |
| `xiaomi/diting/radio` | boot 14, other 2, tz 6, bt 1, modem 1 | 2 rows |
| `xiaomi/diting/vendor/gpu/kbc` | gpu 1 (sequence_manifest.bin), other 1 | 1 row |

python3 assertion passed: 239 + 113 + 35 + 11 + 2 + 2 + 1 = 403. The modem/image family mix (wifi 176 / other 239 / tz 85 / adsp 28 / modem 38 / cdsp 19) is identical to Mi_12's - same 585-row container shape one generation apart [F].

## Group decomposition (403 rows -> 11 groups) [F]

| # | group | rows | bytes | distinct md5s | location |
|---|---|---|---|---|---|
| A | TrustZone application split-PIL sets (15 apps, mdt + b00..b08 each) | 150 | 28,385,621 | 135 | modem/image |
| B | slpi sensor-island split-PIL firmware | 26 | 9,033,768 | 26 | modem/image |
| C | modem OS pieces + platform metadata | 7 | 7,363,151 | 7 | modem/image |
| C2 | qca6490 WLAN-combo firmware (byte-duplicates of C rows) | 2 | 5,494,406 | 2 | modem/image/qca6490 |
| D | WLAN board-data ELFs (`bd_*.elf`) | 42 | 2,517,136 | 38 | modem/image |
| E | mbn/oem build metadata + modem config texts | 14 | 89,544 | 12 | modem/image |
| F | Bluetooth NVM/TLV sets (hpnv/hpbtfw) | 113 | 1,063,407 | 54 | bluetooth/image |
| G | vendor/firmware: mdt heads + Cirrus amp + Goodix touch firmware | 11 | 436,720 | 11 | vendor/firmware |
| H | camera tuning + ArcSoft renderer resources | 35 | 38,762,895 | 30 | vendor/etc/camera (+ resources) |
| I | GPU kbc calibration blob | 1 | 209,153 | 1 | vendor/gpu/kbc |
| J | radio partition images (dsp.img + vm-bootsys.img) | 2 | 337,104,896 | 2 | radio |
| - | total | 403 | 430,460,697 | 316 | - |

python3 assertion passed: group rows sum to 403, group bytes sum to 430,460,697; subfamily census check misc 350 / camera 37 / fingerprint 9 / audio 4 / touch 2 / media 1 (camera 37 = H 35 + CAMERA_ICP.mdt in G + unified_ksqs.bin in I; fingerprint 9 = the fingerpr set; audio 4 = the cs35l41 set; touch 2 = the goodix pair; media 1 = vpu20_4v.mdt); db_type census UNKNOWN 305 / ELF64 81 / FINGERPRINT 9 / AUDIOAMP 4 / TOUCHSCREEN 2 / CERT 1 / FIRMWARE10 1 (all python-verified this session).

### Group A - TrustZone application split-PIL sets (150 rows)

15 named applications, each a complete Qualcomm split-PIL trustlet: `*.mdt` (4,272 B each, 15 total 64,080 B) + `b00` (568 B each, 15 total 8,520 B) + `b01..b08` (each `b08` 3,704 B, 15 total 55,560 B):

cardapp, devauth, eseservice, evautil64, fingerpr, gfdit, gpqese, ic3, mfido, miriskm, mldapta, mlipay, ops, otrpapp, secauth.

- Every one of the 15 sets is structurally identical: 10 files, mdt + b00..b08, no gaps (python-verified per set). Every set carries the same internal duplication: `b03` and `b07` are byte-identical within the set - 15 duplicate rows, so 150 rows collapse to 135 md5s (python-verified) - the same build-grammar property the sibling #1174 doc records for the 15 cupid sets [F].
- Trustlet roster vs Mi_12: 13 of 15 names are identical; diting carries `gfdit` + `gpqese` where cupid carries `gfcupid` + `seccammil` [F]. The `gf*` prefix pairing (gfcupid on cupid, gfdit on diting) reads as a per-device Goodix trustlet, consistent with diting's Goodix touch controller (Group G evidence below) [I]. `gpqese` is Qualcomm's embedded-Secure-Element trustlet: the userspace half is public in tadiphone-caf/vendor_qcom_proprietary `securemsm/esehal/gpqese/` (GPQeSE-HAL, `GPQESE_CMD_TRANSCEIVE_RAW 0x10000003`, `GPQESE_CMD_GENERIC 0x20000000`, TEEC-based APDU transport) [F headers; trustlet-to-HAL pairing [I]].
- `gfdit` is the Mi_12T_Pro-exclusive trustlet: all 10 of its files are corpus-unique (15,270,968 B total; gfdit.b01 7,900,040 B and gfdit.b04 7,158,676 B are the two largest trustlet segments in the whole family) - the direct analog of cupid's corpus-unique gfcupid set [F].
- `fingerpr` is the only set whose bNN rows carry blob_subfamily=fingerprint and db_type=FINGERPRINT: a 6,909,820 B b01 (7 devices: the octet minus Poco_F5 - byte-identical with cupid's fingerpr.b01) plus b04 3,078,048 B (8-share octet) and 7 small segments [F].
- Sharing spans: 38 rows corpus-unique (15,382,632 B) = all 15 mdts + all 15 b08 terminals (15 distinct mdt and 15 distinct b08 md5s, each per-set build) + the 8 non-terminal gfdit segments. b00 spans: gfdit.b00 unique; mfido.b00 2 devices (diting + Poco_F5_Pro); devauth.b00 4 devices (Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro); the other 12 b00s share one md5 across exactly 5 devices (Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro) - the SM8475-class quintet of the sibling #1174 octet classing. Body segments: gpqese.b01-b07 are 6-shared with exactly the SM8475-class sextet (Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro); devauth.b01-b07 are 6-shared with exactly the Xiaomi sextet (Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro); mfido.b02/b06 are 5-shared with Mi_12, Mi_12_Pro, Poco_F5, Poco_F5_Pro; fingerpr.b01 is 7-shared (the octet minus Poco_F5); 56 rows are 8-shared (55 exactly the octet; ic3.b01 with Phone_2 in place of Poco_F5); 19 rows are 9-shared (octet + Phone_2); cardapp.b04/b05 are 12-shared (octet + Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro - the same wide span the #1174 doc records for cupid); ops.b05 16; evautil64.b04 + ops.b04 22; evautil64.b05 27 devices [F spans].
- Interpretation [I]: SM8475-generation QSEE trustlets (secure element eseservice/ic3, identity wallets mlipay/miriskm/mfido/mldapta, OEM security ops/otrpapp/devauth/secauth, camera TZ support evautil64, fingerprint fingerpr, Goodix gfdit, eSE gpqese). Function mapping rests on vendor naming plus the public gpqese HAL only.

### Group B - slpi sensor-island split-PIL firmware (26 rows)

`slpi.mdt` 5,244 B + `slpi.b00..b21` + `slpi.b23` (23 segments; **b22 absent** - the same per-build segment-skip property the sibling docs record for adsp.b24) + `slpir.jsn` 513 B + `slpius.jsn` 515 B. 26 rows, 9,033,768 B, 26 distinct md5s (zero intra-set duplication).

- Mainline cross-check: `remoteproc_slpi` compatible **`qcom,sm8450-slpi-pas`** exists in mainline sm8450.dtsi and in 282 repos' `drivers/remoteproc/qcom_q6v5_pas.c` (cited from #1174's fetch, 2026-11-21) - the SLPI is a mainline-recognized remote processor and this is its firmware image [F].
- 15 rows corpus-unique (8,759,968 B): mdt, b00, b02, b05, b07, b08, b09, b11-b14, b16-b18, b23 - the sensor OS body is diting's own build. Shared: b01 8 devices (octet minus Poco_F5 plus Phone_2), b04/b06 8 devices (exactly the octet), b03/b10 9 devices (octet + Phone_2), b15 6 devices (Mi_12, Mi_12_Pro, the 12S trio, Mi_12T_Pro), b19/b20/b21 2 devices (diting + Poco_F5_Pro), and the two `.jsn` files 14 devices (octet + Phone_2 + Edge_30_Fusion, Moto_G200, OnePlus_9/9RT/9_Pro) - servreg metadata is generation-generic, the sensor OS body is diting-specific [F spans; reading [I]].

### Group C - modem OS pieces + platform metadata (7 rows)

| file | bytes | md5 | share |
|---|---|---|---|
| amss.bin | 5,470,128 | `303dca2a3fe83e5d5dfa783f2bcea26e` | 8 (octet) - see Group C2 |
| Data20.msc | 916,071 | `2acdcb0af37ede2ada6884b8b1292c04` | 8 (octet) |
| Data.msc | 889,524 | `b9eaf732e3289eb9d1a452a8e9083689` | 8 (octet) |
| fw_ipa_gsi_3.0_w.elf | 40,376 | `6dbfeef2a468dc6234a9ac6a7491b8b7` | 1 (Mi_12T_Pro) |
| cpusys_vm.mdt | 16,580 | `9ed8d6e7f3dd24a8c94b037631186664` | 1 (Mi_12T_Pro) |
| regdb_xiaomi.bin | 24,278 | `b937a474fe3644c3601ab14afaa78b23` | 5 (Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro) |
| gptauuid.xml | 6,194 | `040e845630cd3b53e0078f7234452000` | 8 (octet) |

- **amss.bin is NOT the modem processor OS.** The sibling #1174 doc read cupid's amss.bin as "modem processor OS payload [I]"; diting's evidence contradicts that reading: the same 5,470,128 B file (same md5) is shipped TWICE on diting - here and as `qca6490/amss.bin` (Group C2); it is byte-identical across all 8 octet devices including Poco_F5 (SM7475-class), which an SoC-specific modem OS build cannot be; it sits beside amss20.bin, m3.bin and regdb.bin in the qca6490 directory; the UniXNU-diting fork's public manifest comment names "QCA6490 amss/amss20/m3/regdb" as firmware taken from the phone's modem partitions; and linux-firmware's ath11k QCA2066 firmware family (the PCIe/USB sibling of the same combo generation) ships m3.bin in exactly 266,684 B - the byte size of diting's qca6490/m3.bin. Reading: amss.bin is the QCA6490-class WLAN-combo firmware image, duplicated into the modem/image root across the generation's extracts [F evidence chain; conclusion [I] - flag to the lead as a correction candidate for #1174's Group C].
- `Data.msc`/`Data20.msc` are byte-identical with cupid's (same md5s) - modem data images (EFS/NV-container hypothesis [I], carried over from #1174); `regdb_xiaomi.bin` is the Xiaomi regulatory-database binary, 5-shared with the two SM8450 devices and the 12S_Pro/12S_Ultra builds; `gptauuid.xml` partition UUID metadata, octet-identical [F].
- `fw_ipa_gsi_3.0_w.elf` is db_type=CERT on an ELF firmware file - a db_type mislabel of the same class as the corpus-wide a660/AUDIO and fpctzapp/gpu mislabels already recorded in-repo (#946, #2024, and #1174's identical CERT row on cupid, 40,076 B there vs 40,376 B here) [I]. IPA = IP accelerator offload firmware; gsi 3.0 = the GSI generation [I]. Not listed in linux-firmware WHENCE (fetched 2026-11-21) - not mainlined [F].
- `cpusys_vm.mdt` is the family-boundary quirk again, one generation later: 16,580 B like cupid's copy but a different build (md5 `9ed8d6e7...` vs cupid `7b1e5e45...`), corpus-unique to diting, while `cpusys_vm.b00..b04` (212 + 516,096 + 4,621 + 4,096 + 16,368 = 541,393 B, db_type=SECURITY) sit in the `tz` family - one split-PIL image split across two census families, verified on both devices [F].

### Group C2 - qca6490 WLAN-combo firmware directory (2 rows, 5,494,406 B)

`modem/image/qca6490/amss.bin` - byte-identical duplicate of modem/image/amss.bin (ELF64, 5,470,128 B, `303dca2a...`) - and `modem/image/qca6490/regdb_xiaomi.bin` - byte-identical duplicate of modem/image/regdb_xiaomi.bin (24,278 B, `b937a474...`). The directory's 3 remaining rows belong to the `wifi` family (amss20.bin 5,296,128, regdb.bin 24,278 with a different md5 `a087cf07...`, m3.bin 266,684) - not covered here.

- Corpus-wide, the `qca6490` extract directory exists on exactly 7 devices - Mi_12S (mayfly), Mi_12S_Pro (unicorn), Mi_12S_Ultra (thor), Mi_12T_Pro (diting), Poco_F5 (marble), Poco_F5_Pro (mondrian), Phone_2 - and on none of Mi_12/Mi_12_Pro: it is the WiFi-6E-class generation's WLAN firmware container, and on those 6 devices with both copies the amss.bin bytes are identical to the modem/image root copy [F spans; the 12S-class reading [I] per #1174's octet classing].
- The m3.bin size match with linux-firmware `ath11k/QCA2066/hw2.1/m3.bin` (266,684 B, Content-Length probe 2026-11-21) ties the directory to the public ath11k QCA2066/QCA6490 firmware family [F].

### Group D - WLAN board-data ELFs (42 rows, 2,517,136 B)

42 files `bd_<module>[<build/region suffix>].elf`, 59,860-60,084 B each, 38 distinct md5s, all db_type=ELF64.

- **The entire 42-row set is byte-identical with Mi_12's**: same 42 filenames, same 38 md5s (python set-equality this session). One board-data RE pass covers both devices and, since all 42 rows are 8-shared, the whole Xiaomi octet [F].
- Modules: l1, l2, l2s, l3, l3s, l10, l12, l18, m11a, m16t, m80, m81 with gf/gl/in (India [I])/jp (Japan [I]) suffixes. 4 byte-identical region pairs: bd_m11a.elf = bd_m11ain.elf (60,000 B), bd_m11agf.elf = bd_m11agfin.elf (60,000 B), bd_m80.elf = bd_m80gf.elf (59,924 B), bd_m81.elf = bd_m81gf.elf (59,920 B) - the India and global variants collapse to the same bytes [F].
- Boundary note: the `wifi` family (176 rows) already covers the sibling WLAN board data and regdb files; the `bd_*.elf` set here is a distinct per-SKU file family, no filename overlap [F].

### Group E - mbn/oem build metadata + modem config texts (14 rows, 89,544 B)

- `mbn_*` (6 rows, 57,014 B): mbn_build_utc.txt 10 B (corpus-unique), mbn_hw.dig 32 B (corpus-unique), mbn_hw.txt 407 B (9-share), mbn_ota.md5sum 36,571 B (corpus-unique), mbn_sw.dig 32 B (corpus-unique), mbn_sw.txt 19,962 B (5-share with Mi_12, Mi_12_Pro, Poco_F5, Poco_F5_Pro). A build timestamp, OTA digest and digests - build-stamping artifacts [I]. Contrast with cupid: #1174 recorded mbn_ota.md5sum + mbn_build_utc.txt as cupid-unique and mbn_sw.dig as 2-shared; on diting all three are corpus-unique - per-device build stamping [F].
- `oem_*` (8 rows, 32,530 B): oem_hw.txt 61 B = oem_hw_cert.txt 61 B (byte-identical, 8-share octet), oem_hw_dsda.txt 68 B, oem_hw_ss.txt 59 B (8-share), oem_sw.txt 18,895 B (5-share, same quintet as mbn_sw.txt), oem_sw_ct_volte.txt 13,386 B, oem_hw_null.txt 0 B, oem_sw_null.txt 0 B.
- The two 0-byte files carry md5 `d41d8cd98f00b204e9800998ecf8427e` (the empty-string md5) and are 34-shared corpus-wide (Pixels, Fairphones, OnePluses, Xiaomi/Redmi/Poco, Moto, Realme, Nord) - the widest-shared rows of the whole family, trivially universal empty config placeholders [F].

### Group F - Bluetooth NVM/TLV sets (113 rows, 1,063,407 B) - byte-identical with Mi_12

| set | rows | bytes | distinct md5s |
|---|---|---|---|
| hpnv21 (BT NVM) | 44 | 291,348 | 20 |
| hpnv21g (global variant) | 44 | 284,384 | 20 |
| hpnv20 / hpnv20g (older NVM generation) | 11 / 9 | 69,509 / 56,961 | 5 / 4 |
| hpbtfw20.tlv + .ver (BT firmware TLV) | 2 | 201,593 | - |
| hpbtfw21.tlv (BT firmware TLV) | 1 | 146,068 | - |
| hpnv21_sony.302 + hpnv21g_sony.302 | 2 | 13,544 | - |

- **The entire 113-row set is byte-identical with Mi_12's**: same 113 filenames, same 54 md5s (python set-equality this session), and every set byte-sum equals the #1174 figures. The BT firmware/NVM content does not change between the SM8450 and SM8475 generations [F].
- Structure: hpnv21 = `hpnv21.bin` + `.301`/`.302` + 41 `bNN` segment files; heavy intra-set tile duplication (44 rows -> 20 md5s; identity groups include hpnv21.bin = b9b = b9f = ba0 = bc1, md5 `291822f4...`, 5 rows; a 6-row group `90d48517...`; hpnv21g likewise 44 -> 20 with `fd89ecd2...` x6 and `838c13ab...` (the g.bin) x5; hpnv20 11 -> 5; hpnv20g 9 -> 4) - a small set of distinct NVM payloads repeated under many filenames [F].
- Sharing: the hpnv21 and hpnv21g sets plus the two `_sony` variants are 8-shared with exactly the octet (90 rows); hpbtfw21.tlv (`fac75b20...`), hpbtfw20.ver and the hpnv20g set are 9-shared (octet + Phone_2, 11 rows); hpbtfw20.tlv and the hpnv20 set are 12-shared (octet + OnePlus_9/9RT/9_Pro + Phone_2, 12 rows - the older NVM generation spans SM8350-class hardware too); the `_sony` variants (6,852 / 6,692 B) ride the 8-share octet - the Sony radio-module SKU hypothesis carries over from #1174 [I].
- **linux-firmware overlap, with a chip correction**: the plain `hpnv21`/`hpbtfw21` family in linux-firmware WHENCE sits under "Driver: qca - Qualcomm Atheros Bluetooth support for **QCA2066** chips" (WHENCE line 5445, files at 5447-5470: hpbtfw21.tlv, hpnv21.bin, hpnv21g.bin, .301/.302, .309/.30a/30c, b8c, b9f, ba0-ba4, baa, bb8, b10c, b111); the `wcn`-prefixed siblings belong to a "WCN685x uart interface chips" section (WHENCE line 5403); WCN6750's own BT section ships only msbtfw11/msnv11 (WHENCE line 5388). #1174 attributed cupid's set to "WCN6750" - the WHENCE section headings say otherwise; flag to the lead. Sizes (Content-Length probes, 2026-11-21): qca/hpnv21.bin 6,610 B vs census 6,602 B; qca/hpnv21g.bin 6,450 vs 6,442; qca/hpbtfw21.tlv 163,332 vs 146,068 - the same systematic build deltas #1174 recorded, so the linux-firmware copies are different builds of the same NVM tile scheme, not byte-identical [F; byte-level diff not performed, no payload fetched [OPEN]].

### Group G - vendor/firmware: mdt heads + Cirrus amp + Goodix touch firmware (11 rows, 436,720 B)

| file | bytes | db_type | share |
|---|---|---|---|
| CAMERA_ICP.mdt | 5,004 | ELF64 | 1 (Mi_12T_Pro) |
| evass-lt-21.mdt | 4,924 | ELF64 | 1 (Mi_12T_Pro) |
| evass.mdt | 4,924 | ELF64 | 1 (Mi_12T_Pro) |
| vpu20_4v.mdt | 4,924 | ELF64 | 1 (Mi_12T_Pro) |
| evautil64.mdt | 3,868 | ELF64 | 8 (octet; `c53f8342...`, byte-identical with cupid's vendor/firmware copy) |
| T-/B-cs35l41-dsp1-spk-{cali,prot}.bin | 2,184 + 5,184 + 2,184 + 5,188 = 14,740 | AUDIOAMP x4 | all 1 (Mi_12T_Pro) |
| goodix_firmware_l12.bin + goodix_firmware_l12_new.bin | 199,168 + 199,168 = 398,336 | UNKNOWN (subfamily touch) | both 1 (Mi_12T_Pro) |

- The same mdt-only census-gap pattern as cupid: the LineageOS diting manifest (lineage-22.2, fetched 2026-11-21) lists the full bodies - CAMERA_ICP.b00-b21 + .elf + .mbn + _170/_480.elf variants, evass.b00-b19 + mbn, evass-lt-21.b00-b19 + mbn, evautil64.b00-b07, vpu20_4v.b00-b09 + b18/b19 + mbn - while the census carries only the mdt heads. Census completeness for these subsystems is mdt-head-only - a recorded census gap, not a device absence [F vs LineageOS]. The manifest also packages 2 cs35l41 `.wmfw` files, goodix_cfg_group_l12(_new).bin, goodix_test_limits_*.csv and st_fts_l12.ftb, and deblur_txt_{dsp,gpu}.dlc - none in the census [F; gap reading [I]].
- evass/evass-lt-21 = the EVA (vision accelerator) subsystem, vpu20_4v = the video processor, CAMERA_ICP = the camera ICP - mainline has no EVA PAS loader (0 code hits for `qcom,sm8450-eva-pas` / `sm8450-eva`, per #1174's 2026-11-21 search) and the same holds for this SM8475 device [F; file functions [I from vendor naming]].
- The 4 cs35l41 bins are Cirrus Logic CS35L41 smart-amp DSP coefficient/calibration files under the mainline wm_adsp component-prefix convention (T-/B- = top/bottom speaker), carried over from #1174's analysis [F convention; T/B reading [I]]. Sizes differ from cupid's four bins (diting 2,184/5,184/2,184/5,188 vs cupid 1,580/4,768/1,580/4,764) - per-device tuning builds, all corpus-unique [F].
- **goodix_firmware_l12.bin / _new** is the touch-controller firmware: the LineageOS devicetree `qcom/diting-sm8475.dtsi` sets `goodix,firmware-name = "goodix_firmware_l12.bin"`, and live-device testimony in the UniXNU-diting project identifies the touch IC as a Goodix Berlin-D (GT9916, panel 1220x2712) [F DT + testimony; both fetched 2026-11-21]. The two 199,168 B builds are corpus-unique to diting [F]. This is the first touch-controller payload in the corpus's `other` family [I].

### Group H - camera tuning + ArcSoft renderer resources (35 rows, 38,762,895 B)

| slice | rows | bytes | notes |
|---|---|---|---|
| vendor/etc/camera top level | 16 | 34,382,715 | anc_cn/anc_eu 4 MB pair, LDC_ALTEK_AI_SEGMETATION 25.8 MB, arcsat pair, CFR x5, deblur pair, fusion_mecp, LDC_FPC x2 + PACKDATA |
| resources/kernel (+ kernel/32 + kernel/64) | 10 | 1,017,912 | 6 numeric-ID OpenCL kernel bins + 4 hash-named bins, 32/64-bit pairs |
| resources/render/Effect (4 dirs) | 9 | 3,362,268 | BrightEye/V3 eye bins, Makeup Eyebrow + sh bins |

- **anc_cn.bin 4,113,934 B and anc_eu.bin 4,096,318 B** (cn/eu = China/Europe builds [I]) are corpus-unique to diting and carry db_type=TOUCHSCREEN inside the camera directory - a db_type mislabel of the same class as the corpus's recorded CERT-on-ELF and fpctzapp/gpu mislabels [I]. ANC = active noise cancellation [I, unverified]; these are the largest camera-tree rows after LDC_ALTEK. Not parsed [OPEN].
- **LDC_ALTEK_AI_SEGMETATION.bin** (corpus spelling "SEGMETATION") 25,783,952 B, 4-share (Mi_12T_Pro, Poco_F5_Pro, Poco_F6_PRo - corpus device-name typo - and Redmi_K60_Pro): an AI segmentation model for lens-distortion-correction pipelines, Altek = the camera ISP vendor [I]. The largest camera file in the family [F].
- **fusion_mecp.bin** 11,697 B, db_type=FIRMWARE10, 2-share (diting + Poco_F5_Pro) [F]. Function unverified [OPEN].
- CFR_para x5 (UW_V01, UW_V01_HD, UW_V01_SN, W_V03, W_V03_4x; 3,645 B each, 18,225 B total) are byte-identical to each other (one md5, `6e99e58f...`) and the whole group is corpus-unique to diting - cupid's three CFR files carry a different md5 (per #1174), so the CFR build is generation-specific [F]. arcsat_2sat.bin 316 B + arcsat_2sat_pro.bin 317 B corpus-unique; deblur_sd_opencl_{binary,params}.bin (354,046 + 2,042 B) 8-shared with the octet - byte-identical with cupid's pair, an Adreno OpenCL compiled kernel + its parameter blob [I]; LDC_FPC_TUNING_DATA.bin 300 B has a curious cross-generation 5-share (Mi_A3, Redmi_10S, Redmi_K60_Pro, Poco_F5_Pro, Mi_12T_Pro) [F span]; LDC_FPC_TUNING_DATA_AI.bin 1,024 B and LDC_PACKDATA_VENDORID_0x01.bin 544 B corpus-unique.
- The kernel slice (10 rows, all 5-shared with the SM8475 quintet Mi_12S/Mi_12S_Pro/Mi_12S_Ultra/Mi_12T_Pro/Poco_F5_Pro - cupid's equivalents were 2-shared per #1174, so ArcSoft's kernel builds are generation-specific [F span; reading [I]]): numeric-ID OpenCL bins 1720888_{32,64}, 2821809890_{32,64}, 3711416411_{32,64} (131,136/137,760, 33,000/37,152, 8,220/9,324 B), plus the 4 hash-named bins s31.../t31... (6,796/6,800 B and 322,112/325,612 B). The hash-name tokens embed concatenated digests; one token decodes (the repeated `92eb5ffee6ae2fec3ad71c777531578f` = md5 of the single character "b", python-checked); the `31bc24e5...` and `c0cc175b...` tokens have no single-byte preimage - naming structure recorded, not parsed [F names; decode [OPEN]].
- The render slice (9 rows): BrightEye LeftEye/RightEye 360,028 B each (different md5s), BrightEyeV3 eye_pupil 90,028 B (9-share with Mi_13, Mi_13_Pro, Poco_F6_PRo - the retouch resources span into the SM8475/SM8475-successor generation) + left_eye/right_eye 360,028 B each (6-share sextet), Makeup Eyebrow.bin x2 127,628 B (two different builds; 6-share) and sh.bin x2 788,436 B byte-identical across the two Makeup modes (9-share). All 35 H rows are manifest-covered (present in the LineageOS diting manifest) [F].

### Group I - GPU kbc calibration blob (1 row)

`vendor/gpu/kbc/unified_ksqs.bin` 209,153 B, md5 `1a217e4b2ce9c57342343386aeef923a`, db_type UNKNOWN, subfamily camera, 9-share (octet + Phone_2) - byte-identical with cupid's copy. The kbc directory's other row (sequence_manifest.bin, 1,860 B) is gpu-family content - not covered here. Not in the LineageOS manifest (fetched 2026-11-21): the only in-census vendor-tree file LineageOS does not package on diting as well - consistent with a device-generated calibration artifact [I, unverified]. Function unknown; [OPEN].

### Group J - radio partition images (2 rows, 337,104,896 B)

| file | bytes | md5 | share |
|---|---|---|---|
| vm-bootsys.img | 269,996,032 (= 257.48828125 MiB) | `db7c51a3ae0d3f096a7e4ebcf605c5a2` | 5 (SM8475 quintet: Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro) |
| dsp.img | 67,108,864 (= 64 MiB) | `a6334ef3df24069beb3919bf716e34cb` | 5 (same quintet) |

- **vm-bootsys.img is the new largest `other` row on the SM8475 generation** - 62.72 percent of the family's bytes, and the corpus's Mi_12 census has no vm-bootsys row at all: it is a generation addition to the radio partition set [F census; addition reading [I]]. Public tooling establishes what the partition is: fastboot flashes it (`fastboot flash vm-bootsys vm-bootsys.img` - MIUI OTA conversion scripts and fish-shell fastboot completions list the partition name), UN1CA's sm8450 recovery.fstab mounts the `vm-bootsys` partition as ext4, and Qualcomm's meta-qti-bsp builds and mounts vm-bootsys with dm-verity - a Qualcomm VM (hypervisor guest) boot-system image [F tooling, all fetched 2026-11-21; contents unexamined [OPEN]; the VM-stack reading [I]].
- `dsp.img` is the Xiaomi `dsp` partition convention - a 64 MiB filesystem image carrying DSP firmware copies [I]. Its build differs from cupid's (diting `a6334ef3...` vs cupid's `1cc3caa8...` per #1174) but it is byte-identical across the SM8475 quintet, like vm-bootsys.img [F].

## Cross-corpus md5-sharing profile [F]

403 rows, 316 distinct md5s. Sharing distribution (devices sharing a given md5 -> Mi_12T_Pro rows): 1->79, 2->5, 4->2, 5->31, 6->21, 7->1, 8->205, 9->37, 12->14, 14->2, 16->1, 22->2, 27->1, 34->2 (sums 403, python-verified).

| share span | rows | content |
|---|---|---|
| corpus-unique (79 rows, 32,899,699 B) | 79 | gfdit set (10) + 14 other TZ mdts + 15 TZ b08s + gfdit body counted once (A, 38 rows / 15,382,632 B), slpi body (B, 15 / 8,759,968), fw_ipa + cpusys_vm.mdt (C, 2 / 56,956), mbn_ota.md5sum + mbn_build_utc + mbn_sw.dig (E, 3 / 36,613), all of Group G except evautil64.mdt (10 / 432,852), anc pair + arcsat pair + 5 CFR + 2 LDC + LDC_PACKDATA + LDC_AI (H, 11 / 8,230,678) |
| 2 devices (diting + Poco_F5_Pro) | 5 | mfido.b00, slpi.b19/b20/b21, fusion_mecp.bin |
| 4 devices | 2 | devauth.b00 (12S trio + diting), LDC_ALTEK_AI_SEGMETATION.bin (+ Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro) |
| 5 devices | 31 | 12 TZ b00s + dsp.img + vm-bootsys.img + 10 ArcSoft kernel resources (SM8475 quintet Mi_12S/Mi_12S_Pro/Mi_12S_Ultra/Mi_12T_Pro/Poco_F5_Pro, 24 rows); regdb_xiaomi.bin x2 (with Mi_12, Mi_12_Pro, Mi_12S_Pro, Mi_12S_Ultra); mbn_sw.txt + oem_sw.txt + mfido.b02/b06 (with Mi_12, Mi_12_Pro, Poco_F5); LDC_FPC_TUNING_DATA.bin (with Mi_A3, Redmi_10S, Redmi_K60_Pro) |
| 6 devices | 21 | gpqese body + eye/Eyebrow render bins (SM8475-class sextet with Poco_F5, 13 rows); devauth body + slpi.b15 (Xiaomi sextet Mi_12..Mi_12T_Pro, 8 rows) |
| 8 devices | 205 | 203 rows exactly the Xiaomi octet: all 42 bd_*.elf, 90 BT NVM rows, amss.bin x2, Data.msc/Data20.msc, gptauuid.xml, slpi.b04/b06, most TZ body segments, deblur pair, oem_hw pair, oem_hw_ss; plus ic3.b01 and slpi.b01 (same octet with Phone_2 in place of Poco_F5) |
| 9 devices | 37 | 34 rows exactly octet + Phone_2: hpbtfw21.tlv + hpbtfw20.ver + hpnv20g set, unified_ksqs.bin, slpi.b03/b10, mbn_hw.txt, TZ body segments; plus eye_pupil.bin + sh.bin x2 (with Mi_13, Mi_13_Pro, Poco_F6_PRo in place of Mi_12/Mi_12_Pro) |
| 12 devices | 14 | hpnv20 full set + hpbtfw20.tlv (octet + OnePlus_9/9RT/9_Pro + Phone_2, 12 rows); cardapp.b04/b05 (octet + Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro, 2 rows) |
| 14 devices | 2 | slpir.jsn + slpius.jsn (servreg metadata, generation-generic) |
| 16-27 devices | 4 | ops.b05 (16), evautil64.b04 + ops.b04 (22), evautil64.b05 (27) |
| 34 devices | 2 | oem_*_null.txt 0-byte placeholders (fleet-wide) |

Leverage reading [I]: one RE pass on the octet-shared files (203 rows exactly the octet, plus the 2 near-octet rows) covers the whole Xiaomi SM8450/8475-generation fleet in this corpus; the Bluetooth NVM set and the board-data set are FULLY byte-identical between Mi_12 and Mi_12T_Pro (155 rows), so they need no diting-specific RE at all; the corpus-unique 79 rows are where Mi_12T_Pro-specific RE value concentrates (gfdit, the slpi body, vm-bootsys.img, the anc pair, LDC_ALTEK, goodix_firmware_l12).

## ISA / interface facts

- `isa_identified` is empty on all 403 rows and `interface_documented=n` on all 403 (single python assertion, this session) - honestly un-RE'd at instruction level in the corpus [F]. No instruction-level claim is made here [N].
- db_type census on the 403 rows: UNKNOWN 305, ELF64 81 (42 bd_*.elf + 15 TZ mdts + 14 TZ b00s + slpi.mdt + slpi.b00 + amss.bin x2 + cpusys_vm.mdt + fw_ipa_gsi_3.0_w.elf + 5 vendor/firmware mdts), FINGERPRINT 9, AUDIOAMP 4, TOUCHSCREEN 2 (anc bins - mislabel [I]), CERT 1 (fw_ipa_gsi_3.0_w.elf - mislabel [I]), FIRMWARE10 1 (fusion_mecp.bin). All counts python-verified this session.
- Verified loader/interface surfaces [F]: mainline remoteproc PAS compatibles `qcom,sm8450-{adsp,cdsp,slpi,mpss}-pas` in sm8450.dtsi cover the adsp/cdsp/slpi images (the platform's PAS machinery, cited from #1174); mainline wm_adsp covers the CS35L41 coefficient files; the public GPQeSE HAL (`securemsm/esehal/gpqese/`) is the userspace counterpart of the gpqese trustlet (TEEC APDU transport, raw-transceive + generic command interfaces) [F]; fastboot + recovery.fstab + meta-qti-bsp document vm-bootsys as a flashable, verity-mounted partition [F]; the BT NVM tiles are HCI-config downloads by the btusb/qca driver family (linux-firmware qca sections) [I]; the ath11k QCA2066 family documents the qca6490 WLAN firmware container (amss.bin/m3.bin/regdb.bin shapes) [F]. **No** mainline loader exists for EVA (per #1174's code search) and none of the bd_*/camera resources is kernel-loaded.
- The split-PIL container grammar (mdt = ELF program-header image, bNN = loadable segments, jsn = servreg JSON) is established in-repo (research/fleet/qdsp6sw-container.md, #606) and applied by the sibling docs; groups A, B, C(cpusys_vm) and G use exactly that grammar [F].

## Honest negatives

- No payload was fetched, hashed or decoded in this issue: every byte fact is census metadata or a fetched public tree listing/manifest/header. Byte-identity claims are md5-set equalities from the census, not byte-level diffs. [OPEN]
- vm-bootsys.img (257.5 MiB) and dsp.img contents are unexamined; the VM-boot-system and dsp-partition semantics are tooling/naming-based inference. [OPEN]
- The anc_cn/anc_eu binaries (4 MB each, db_type=TOUCHSCREEN in the camera tree), fusion_mecp.bin, unified_ksqs.bin, LDC_ALTEK_AI_SEGMETATION.bin and the ArcSoft hash-named kernel resources are function-unknown beyond naming and sharing evidence. [OPEN]
- The ArcSoft kernel-resource filename tokens are only partially decoded (one token = md5("b")). [OPEN]
- The census under-covers the vendor-tree subsystem firmware bodies (evass, evass-lt-21, vpu20_4v, evautil64, CAMERA_ICP bNN sets; cs35l41 .wmfw; goodix cfg/test files; deblur .dlc) that the LineageOS manifest lists - these are census gaps of the upstream extract, recorded here, not device absences. [F vs LineageOS; the gap itself is [I]]
- Whether diting's modem partition physically carries slpi.b22 (absent from census like adsp.b24) is not decodable from the census alone. [OPEN]
- The gfdit trustlet function rests on the gfcupid naming parallel and diting's Goodix hardware; no public source names it. [I]
- amss.bin's QCA6490-class WLAN-firmware reading is an inference from duplication, sharing and public testimony; it contradicts #1174's cupid reading and is flagged for the lead rather than silently applied there. [I]

## What would upgrade this finding

1. Payload-decode vm-bootsys.img (mount the ext4/vfat filesystem inside) - first in-corpus look inside a Qualcomm VM boot-system partition image, 62.7 percent of this family's bytes.
2. Payload-decode one SM8475 TZ-app mdt (gfdit.mdt is the diting-exclusive, largest-value target) - first SM8475 PIL metadata decode in the corpus.
3. Byte-diff qca6490/amss.bin against linux-firmware ath11k/QCA2066/hw2.1/amss.bin (5,349,376 B vs census 5,470,128 B) to pin the build lineage of the QCA6490 WLAN firmware fleet, and diff qca/hpnv21.bin (6,610 B) against the census 6,602 B tile to pin the +8 B delta #1174 recorded.
4. Have the lead split `cpusys_vm.mdt` ownership (other vs tz) into a census rule - now verified on two devices (cupid, diting) with identical structure.
5. Reconcile the amss.bin reading across #1174 (cupid: modem OS [I]) and this doc (diting: QCA6490 WLAN-combo firmware [I]) - the corpus-wide octet byte-identity means one of the two readings is wrong fleet-wide, and the correction propagates to 8 devices' docs.
6. Decode the ArcSoft kernel-resource hash names (t31.../s31...) beyond the one confirmed md5("b") token.

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment (Gate -1) and DELTA comment (Gate 0). Checks: GitHub code search `gfdit`, `gpqese`, `"vm-bootsys"`, `"goodix_firmware_l12"` (adineo-cmd excluded, 2026-11-21) -> gpqese HAL public, vm-bootsys partition tooling public, goodix touch firmware documented in LineageOS DTs, gfdit 0 firmware hits; LineageOS diting proprietary-files.txt (2026-11-21) -> manifest contrasts recorded above; linux-firmware WHENCE + Content-Length probes (2026-11-21) -> hpnv21 = QCA2066 section, wcnhpnv21 = WCN685x-uart section, m3.bin size match, hpnv21.bin/hpbtfw21.tlv size deltas; public spec pages (2026-11-21) -> SM8475/22081212UG/diting identity; no public source documents the Mi_12T_Pro other-family census itself. DELTA posted; proceeding under it.

Not legal advice; no proprietary payload accessed or committed - all facts are census metadata plus public trees, manifests, headers and specs.
