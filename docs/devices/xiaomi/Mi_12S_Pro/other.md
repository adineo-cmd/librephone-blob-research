# xiaomi Mi_12S_Pro - `other` family status (424 rows - PRESENT, residual catch-all family across 6 device locations; 11 groups, python-verified sums, 335 distinct md5s, 79 corpus-unique rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1192](https://github.com/adineo-cmd/open-device/issues/1192)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 0fe1ba0 worktree), `upstream-contribution/blob-database/device-inventory.csv`, the sibling docs docs/devices/xiaomi/Mi_12/adsp.md (issue [#1168](https://github.com/adineo-cmd/open-device/issues/1168)), docs/devices/xiaomi/Mi_12/other.md (issue [#1174](https://github.com/adineo-cmd/open-device/issues/1174) - the SM8450-generation `other` grammar this decomposition mirrors), docs/devices/xiaomi/Mi_12S/cdsp.md (issue [#1180](https://github.com/adineo-cmd/open-device/issues/1180)), docs/devices/xiaomi/Mi_12S_Pro/adsp.md (issue [#1186](https://github.com/adineo-cmd/open-device/issues/1186) - device identity, cited not re-derived), the LineageOS `android_device_xiaomi_unicorn` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), the /e/OS device page doc.e.foundation/devices/unicorn (fetched 2026-11-21), public fastboot flash-guide documentation of `vm-bootsys.img` (DroidWin, 4PDA; fetched 2026-11-21), public TrustZone trustlet-format sources (Check Point Research 2019, Quarkslab, LSE MBN format guide; fetched 2026-11-21), linux-firmware qca/ WHENCE facts as recorded in #1174 (fetched there 2026-11-21). No payload fetched by this issue; every number below is command output verified with python3 (`python3 -I`, this session).

**Verdict: the `other` family is PRESENT on Mi_12S_Pro and is the residual catch-all of the 840-row census - 424 rows, 525,854,485 B (37.26 percent of the device census bytes), 335 distinct md5s, spread over 6 locations.** It decomposes into 11 groups: 17 TrustZone application split-PIL sets (170 rows), the slpi sensor-island firmware (26), modem OS + platform pieces (9), 42 WLAN board-data ELFs, mbn/oem metadata texts (14), the WCN6750 Bluetooth NVM/TLV sets (113), mdt-only subsystem extracts + Cirrus amp bins in vendor/firmware (9), camera tuning + ArcSoft renderer resources (37), one GPU calibration blob (1), two radio partition images (2), and one undocumented modem/image model file `ancidf_model_tee` (1). 79 rows (34,603,676 B) are corpus-unique to Mi_12S_Pro; the dominant share pattern is the 8-device Xiaomi SM8450/SM8475 octet (205 rows); 333 rows (491,173,350 B) are byte-identical with a Mi_12S `other`-family row and 283 rows (37,150,736 B) with a Mi_12 `other`-family row. There is no structural absence: the family is a census remainder, not a coherent single firmware family, and the census is complete for what it covers (with recorded partial-coverage contrasts against the LineageOS manifest, below). The +33 rows / +392,185,549 B delta vs the sibling Mi_12 census (#1174) is concentrated in the 12S-generation additions: `vm-bootsys.img` (269,996,032 B), the `night_align_lsc_tbl` pair (88,080,384 B), `snsc.bin` (17,329,600 B), `ancidf_model_tee` (4,271,903 B) and a second region trustlet set.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12S Pro (China, model 2206122SC); codename `unicorn` | sibling doc #1186 identity table [F]; /e/OS device page "Info about Xiaomi - 12S Pro - unicorn" (fetched 2026-11-21) [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1**; Adreno 730; Hexagon V69 DSP | sibling doc #1186 (public spec pages 2026-11-21) [F]; the upstream inventory SoC cell is empty and stays flagged for the lead |
| released | July 2022 (announced 2022-07-04) | sibling doc #1186 [F] |
| stock base | `OS2.0.205.0.VLECNXM` | sibling doc #1186, from the LineageOS unicorn manifest header [F] |
| census scope | 840 rows in 9 families (other 424, wifi 179, tz 91, modem 39, adsp 67, cdsp 19, boot 14, gpu 6, bt 1); 1,411,166,715 B; this issue covers the 424-row `other` residual | coverage-matrix.csv [F] |
| priority | P3 on all 424 rows | coverage-matrix.csv [F] |
| corpus classes [I] | the 8-device share octet = Mi_12, Mi_12_Pro (SM8450) + Mi_12S (mayfly), Mi_12S_Ultra (thor), Mi_12S_Pro (unicorn), Mi_12T_Pro (diting), Poco_F5_Pro (mondrian) (SM8475-class) + Poco_F5 (SM7475-class) | sibling docs #1174/#1180 classing; md5 spans below [F] |

## Where the family lives (location crosstab) [F]

`other` is residual: every row not matched by a named-family grammar lands here. Census locations for Mi_12S_Pro `other` rows and their byte loads:

| location | rows | bytes |
|---|---|---|
| `xiaomi/unicorn/modem/image` (+ 2 rows in its `qca6490` subdirectory) | 262 | 74,352,908 |
| `xiaomi/unicorn/bluetooth/image` | 113 | 1,063,407 |
| `xiaomi/unicorn/radio` | 2 | 337,104,896 |
| `xiaomi/unicorn/vendor/etc/camera` (+ resources/kernel, resources/kernel/32, /64, render Effect dirs) | 37 | 113,086,821 |
| `xiaomi/unicorn/vendor/firmware` | 9 | 37,300 |
| `xiaomi/unicorn/vendor/gpu/kbc` | 1 | 209,153 |
| total | 424 | 525,854,485 |

python3 assertion passed: location rows sum to 424, location bytes sum to 525,854,485. The modem/image directory hosts 6 census families for this device (wifi 176, other 260 at the root, tz 85, modem 38, adsp 28, cdsp 19) plus a `qca6490` subtree holding wifi 3 + other 2 - the QCA6490 (WCN6855-class) WLAN chip's firmware directory [I on the chip mapping from the directory name].

## Group decomposition (424 rows -> 11 groups) [F]

| # | group | rows | bytes | distinct md5s | location |
|---|---|---|---|---|---|
| A | TrustZone application split-PIL sets (17 apps, mdt + b00..b08 each) | 170 | 45,539,876 | 153 | modem/image |
| B | slpi sensor-island split-PIL firmware | 26 | 9,077,772 | 26 | modem/image |
| C | modem OS + platform pieces | 9 | 12,857,557 | 7 | modem/image + modem/image/qca6490 |
| D | WLAN board-data ELFs (`bd_*.elf`) | 42 | 2,517,136 | 38 | modem/image |
| E | mbn/oem build metadata + modem config texts | 14 | 88,664 | 12 | modem/image |
| F | Bluetooth NVM/TLV sets (hpnv/hpbtfw) | 113 | 1,063,407 | 54 | bluetooth/image |
| G | subsystem mdt extracts + Cirrus amp bins | 9 | 37,300 | 9 | vendor/firmware |
| H | camera tuning + ArcSoft renderer resources | 37 | 113,086,821 | 32 | vendor/etc/camera tree |
| I | GPU kbc calibration blob | 1 | 209,153 | 1 | vendor/gpu/kbc |
| J | radio partition images (dsp.img, vm-bootsys.img) | 2 | 337,104,896 | 2 | radio |
| K | undocumented modem/image model file | 1 | 4,271,903 | 1 | modem/image |
| - | total | 424 | 525,854,485 | 335 | - |

python3 assertion passed: group rows sum to 424, group bytes sum to 525,854,485; subfamily census check misc 371 / camera 38 / fingerprint 9 / audio 4 / media 1 / sensors 1 (camera 38 = H 36 camera-labeled + CAMERA_ICP.mdt in G + unified_ksqs.bin in I; sensors 1 = snsc.bin in H; fingerprint 9 = fingerpr.b00..b08 in A; audio 4 = cs35l41 in G).

### Group A - TrustZone application split-PIL sets (170 rows)

17 named applications, each a complete Qualcomm split-PIL trustlet: `*.mdt` (4,272 B each, db_type=ELF64) + `b00` (568 B each, db_type=ELF64) + `b01..b08` (db_type=UNKNOWN, terminal `b08` 3,704 B each):

cardapp, devauth, eseservice, evautil64, fingerpr, gfuni, gfuni6, gpqese, ic3, mfido, miriskm, mlipay, mldapta, ops, otrpapp, seccammil, secauth.

- python3-verified for all 17 sets: exactly 10 files (mdt + b00..b08), no gaps, mdt 4,272 B, b00 568 B, b08 3,704 B, and `b03` = `b07` byte-identical within every set (same size and md5) - the same build-grammar property the sibling #1174 records for cupid's 15 sets [F].
- A second `evautil64.mdt` copy (3,868 B) sits in vendor/firmware and is counted in group G below; the modem/image set is complete without it.
- `fingerpr` carries db_type=FINGERPRINT and blob_subfamily=fingerprint on all 9 bNN rows (b00..b08): b01 6,909,820 B is shared by exactly 7 devices {unicorn, Mi_12, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Poco_F5_Pro} - the fingerprint TrustZone payload is one byte-identical build across the whole Xiaomi SM8450/SM8475 octet generation; b02..b07 are octet-exact; b03 = b07 = 281,192 B md5 `dac782f3e5fc3ff756e29dbc23238edb`, the exact md5 #1174 records for cupid's pair.
- **The `gfuni` + `gfuni6` pair is fully corpus-unique** (all 20 rows): gfuni 10 rows, 14,934,557 B (b01 8,140,550 B is the largest trustlet segment in the family); gfuni6 10 rows, 10,441,196 B. These are unicorn's analogs of cupid's device-unique `gfcupid` set (#1174); unicorn is the only census device with two region trustlet sets, and no `gfcupid`/`gfuni*` rows exist on Mi_12S [F census]. GF naming unverified [I].
- `gpqese` exists only on the 12S generation: 10 rows each on unicorn, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro, and 0 rows on Mi_12/Mi_12_Pro [F census]. Its b01..b07 span {Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro} (6 total); mdt and b08 are corpus-unique.
- Span lattice over the remaining sets: every mdt and every b08 terminal is corpus-unique (30 rows); 12 b00s span {Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro}; devauth.b00 spans {Mi_12S, Mi_12S_Ultra, Mi_12T_Pro}; mfido.b00 and seccammil.b00 span {Mi_12S, Mi_12S_Ultra}; seccammil.b01..b07 spans {Mi_12, Mi_12S, Mi_12S_Ultra, Mi_12_Pro}; devauth.b01..b07 spans {Mi_12, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro}; 56 rows are octet-exact (the b01..b07 bodies of eseservice, miriskm, mlipay, otrpapp, secauth plus parts of cardapp, evautil64, fingerpr, ic3, mfido, mldapta, ops); 19 rows span octet + Phone_2 (evautil64 b01/b02/b03/b07, ic3 b02/b03/b04/b05/b07, mldapta b01..b05/b07, ops b01/b02/b03/b07); cardapp.b04/b05 span 12 devices; ops.b05 16; evautil64.b04 and ops.b04 22; evautil64.b05 27 devices - the same wide cross-vendor spans #1174 records for cupid.
- Interpretation [I]: SM8475-generation QSEE trustlets (secure element services eseservice/ic3, identity wallets mlipay/miriskm/mfido/mldapta, OEM security ops/otrpapp/devauth/secauth, camera TZ support seccammil/evautil64, fingerprint fingerpr, region pair gfuni/gfuni6). Function mapping rests on vendor naming only; the trustlet container format is publicly documented (Check Point 2019; Quarkslab; LSE MBN guide; fetched 2026-11-21) [F].

### Group B - slpi sensor-island split-PIL firmware (26 rows)

`slpi.mdt` 5,244 B (cupid's is 4,944 B - different build) + `slpi.b00..b21` + `slpi.b23` (23 segments; **b22 absent** - the same per-build segment-skip property the sibling docs record for adsp.b24 and cupid's slpi) + `slpir.jsn` 513 B + `slpius.jsn` 515 B. 26 rows, all 26 md5s distinct (no intra-set duplication).

- Mainline cross-check (cited from #1174, fetched there 2026-11-21): `remoteproc_slpi` compatible **`qcom,sm8450-slpi-pas`** exists in mainline sm8450.dtsi and in drivers/remoteproc/qcom_q6v5_pas.c across 282 repos - the SLPI is a mainline-recognized remote processor and this is its firmware image [F].
- 14 rows corpus-unique (8,798,632 B): slpi.mdt, b00, b02, b05, b08, b09, b11-b14, b16-b18, b23 - the sensor OS body is unicorn-build. Shared: b01/b04/b06 octet-exact; b03/b10 octet + Phone_2 (9); b15 {Mi_12, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro} (6); b19/b20/b21 {Mi_12, Mi_12S, Mi_12_Pro} (4); b07 {Mi_12, Mi_12_Pro} (3); the two .jsn files span 14 devices (octet + Edge_30_Fusion, Moto_G200, OnePlus_9/9RT/9_Pro, Phone_2) - servreg metadata is generation-generic, exactly as in #1174 [I].

### Group C - modem OS + platform pieces (9 rows)

| file | bytes | md5 | db_type | span |
|---|---|---|---|---|
| amss.bin (modem/image) | 5,470,128 | `303dca2a3fe83e5d5dfa783f2bcea26e` | ELF64 | 8 (octet) |
| amss.bin (modem/image/qca6490) | 5,470,128 | `303dca2a3fe83e5d5dfa783f2bcea26e` | ELF64 | 8 (octet) |
| Data20.msc | 916,071 | `2acdcb0af37ede2ada6884b8b1292c04` | UNKNOWN | 8 (octet) |
| Data.msc | 889,524 | `b9eaf732e3289eb9d1a452a8e9083689` | UNKNOWN | 8 (octet) |
| regdb_xiaomi.bin x2 (modem/image + modem/image/qca6490) | 24,278 each | `b937a474fe3644c3601ab14afaa78b23` | UNKNOWN | 5 {+ Mi_12, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro} |
| gptauuid.xml | 6,194 | `040e845630cd3b53e0078f7234452000` | UNKNOWN | 8 (octet) |
| cpusys_vm.mdt | 16,580 | `12cd1ff0c316e02d0c6a6d8264184f0e` | ELF64 | 1 (unicorn) |
| fw_ipa_gsi_3.0_w.elf | 40,376 | `1b15ec34082f02bf14539bef98612acd` | CERT | 1 (unicorn) |

- amss.bin is the modem processor OS payload [I]; its md5 equals the value #1174 records for cupid's amss.bin - one modem OS build across the octet [F]. The `modem/image/qca6490` copies of amss.bin and regdb_xiaomi.bin are byte-identical duplicates of the modem/image root copies [F]. mainline `remoteproc_mpss` compatible `qcom,sm8450-mpss-pas` (cited from #1174's sm8450.dtsi fetch) is the loader side [F].
- regdb_xiaomi.bin's md5 equals the value #1174 records for cupid's copy - the Xiaomi regulatory-database binary is one build shared by 5 octet devices (unicorn, cupid, Mi_12_Pro, Mi_12S_Ultra, Mi_12T_Pro; Poco_F5/Poco_F5_Pro/Mi_12S carry none) [F].
- `cpusys_vm.mdt` is the same family-boundary quirk #1174 records on cupid: its mdt sits in `other` while `cpusys_vm.b00..b04` (212 + 516,096 + 4,621 + 4,096 + 16,368 B) sit in the `tz` family - one split-PIL image split across two census families, here verified on unicorn's own rows [F].
- `fw_ipa_gsi_3.0_w.elf` is db_type=CERT on an ELF firmware file - a db_type mislabel of the same class as the corpus-wide a660/AUDIO and fpctzapp/gpu mislabels already recorded in-repo (#946, #2024) [I]. Its size differs from cupid's 40,076 B (unicorn build). IPA = IP accelerator offload firmware; gsi 3.0 = the SM8450/SM8475 GSI generation [I]; not in linux-firmware WHENCE per #1174's fetch [F].
- `Data.msc`/`Data20.msc` are modem data images (EFS/NV-container hypothesis [I], sizes identical to cupid's); `gptauuid.xml` is partition UUID metadata (naming [I]).

### Group D - WLAN board-data ELFs (42 rows)

42 files `bd_<module>[<region>].elf`, 59,860-60,080 B each, 2,517,136 B total, 38 distinct md5s, all db_type=ELF64, all octet-exact - the same corpus build cupid carries (#1174: 42 rows, 38 md5s, octet-only).

- Modules l1, l2, l2s, l3, l3s, l10, l12, l18, m11a, m16t, m80, m81 with region/build suffixes gf, gl, in (India), jp (Japan) [I for the region reading from the suffix names].
- 4 byte-identical region pairs, the exact pairs #1174 records: bd_m11a.elf = bd_m11ain.elf (60,000 B), bd_m11agf.elf = bd_m11agfin.elf (60,000 B), bd_m80.elf = bd_m80gf.elf (59,924 B), bd_m81.elf = bd_m81gf.elf (59,920 B) [F].
- Boundary note: the `wifi` family (179 rows: 176 at modem/image + 3 at modem/image/qca6490) already covers the sibling WLAN board data and the qca6490 WLAN firmware; the `bd_*.elf` set here is a distinct per-SKU file family, no filename overlap [F].

### Group E - mbn/oem build metadata + modem config texts (14 rows, 88,664 B)

- `mbn_*` (6 rows, 56,370 B): mbn_build_utc.txt 10 B and mbn_ota.md5sum 36,167 B are corpus-unique (build-stamping artifacts [I]); mbn_hw.dig 32 B octet-exact; mbn_hw.txt 407 B spans octet + Phone_2 (9); mbn_sw.dig 32 B and mbn_sw.txt 19,722 B span only {Mi_12S, Mi_12S_Ultra} - unlike cupid, whose mbn_ota.md5sum/mbn_build_utc were unique but whose mbn_sw.dig was 2-shared with Mi_12_Pro; the 12S-generation mbn_sw text build pairs with Mi_12S/Mi_12S_Ultra instead [F].
- `oem_*` (8 rows, 32,294 B): oem_hw.txt 61 B = oem_hw_cert.txt 61 B (byte-identical, octet-exact), oem_hw_dsda.txt 68 B and oem_hw_ss.txt 59 B octet-exact, oem_sw_ct_volte.txt 13,386 B octet-exact, oem_sw.txt 18,659 B {Mi_12S, Mi_12S_Ultra}-only, oem_hw_null.txt 0 B and oem_sw_null.txt 0 B.
- The two 0-byte files carry md5 `d41d8cd98f00b204e9800998ecf8427e` (the empty-string md5) and are the widest-shared rows of this family: 34 corpus devices spanning Pixels (4A_5G/5/5A), Fairphones (FP4/FP5/FP6), OnePluses (8..13), Xiaomi/Redmi/Poco, Moto, Realme, Nord, Mi_A3, Pad - trivially, empty config placeholders are universal [F].

### Group F - Bluetooth NVM/TLV sets (113 rows, 1,063,407 B)

| set | rows | bytes |
|---|---|---|
| hpnv21 (WCN6750 BT NVM) | 44 | 291,348 |
| hpnv21g (global variant) | 44 | 284,384 |
| hpnv20 / hpnv20g (older NVM generation) | 11 / 9 | 69,509 / 56,961 |
| hpbtfw20.tlv + .ver / hpbtfw21.tlv (BT firmware TLV) | 2 / 1 | 201,593 / 146,068 |
| hpnv21_sony.302 / hpnv21g_sony.302 | 2 | 13,544 |

python3 assertion passed: set rows sum to 113, set bytes sum to 1,063,407.

- Structure identical to cupid's (#1174): hpnv21 = `hpnv21.bin` + `.301`/`.302` + 41 `bNN` segment tiles spanning b5a..bc2 with gaps ba5/bb4 and 3-digit continuations b10c/b111; hpnv21g the same 44-row shape; hpnv20 = bin + 10 tiles all 6,319 B; hpnv20g = bin + 8 tiles all 6,329 B (b4b and b90 of hpnv20 absent); hpbtfw20.tlv + .ver; hpbtfw21.tlv. All 113 rows db_type=UNKNOWN, subfamily misc.
- **Heavy intra-set byte duplication, same as cupid**: hpnv21's 44 rows collapse to 20 distinct md5s (hpnv21g likewise 20; hpnv20 11 rows -> 5; hpnv20g 9 -> 4). Example: hpnv21.bin = b9b = b9f = ba0 = bc1, md5 `291822f46166c0872408fb984a5e8149` - the exact md5 #1174 records for cupid's 5-row identity group: the NVM tiles are one corpus build shared by the octet [F].
- Sharing profile identical to cupid's: 90 rows octet-exact; 11 rows (hpbtfw21.tlv + 10 hpnv21/hpnv21g tiles) octet + Phone_2; 12 rows (all of hpnv20 + hpbtfw20.tlv) octet + OnePlus_9/9RT/9_Pro + Phone_2 - the older NVM generation spans SM8350-class hardware too [F spans; SoC classes [I]].
- linux-firmware contrast (cited from #1174, fetched there 2026-11-21): the upstream qca/ directory ships the WCN6750 family in subset (16 hpnv21, 17 hpnv21g files, hpbtfw21.tlv), with systematic small size deltas (+8 B per tile, hpbtfw21.tlv 163,332 B upstream vs 146,068 census) - different builds of the same tile scheme; byte-level diff not performed, no payload fetched [OPEN].

### Group G - subsystem mdt extracts + Cirrus amp bins (9 rows, 37,300 B)

| file | bytes | db_type | span |
|---|---|---|---|
| CAMERA_ICP.mdt | 5,004 | ELF64 | 1 (unicorn) |
| evass.mdt | 4,924 | ELF64 | 1 (unicorn) |
| evass-lt-21.mdt | 4,924 | ELF64 | 1 (unicorn) |
| vpu20_4v.mdt | 4,924 | ELF64 | 1 (unicorn) |
| evautil64.mdt (second copy) | 3,868 | ELF64 | 8 (octet) |
| T-cs35l41-dsp1-spk-cali.bin / -prot.bin | 1,940 + 4,888 | AUDIOAMP | 1 (unicorn) |
| B-cs35l41-dsp1-spk-cali.bin / -prot.bin | 1,944 + 4,884 | AUDIOAMP | 1 (unicorn) |

- These are the mdt-only heads of four subsystem firmware sets whose full split-PIL bodies exist in the vendor tree but are **not in the census**: the LineageOS unicorn manifest (lineage-22.2, fetched 2026-11-21) lists CAMERA_ICP 27 entries (b00..b21, .elf, .mbn, .mdt, _170.elf, _480.elf), evass 20 bNN + .mbn, evass-lt-21 20 bNN + .mbn, vpu20_4v 12 bNN + .mbn. Census completeness for these subsystems is mdt-head-only - a recorded census gap, not a device absence [F vs LineageOS].
- evass/evass-lt-21 = the EVA (camera vision accelerator) subsystem - no mainline EVA PAS loader exists (0 code hits for `qcom,sm8450-eva-pas`, per #1174's 2026-11-21 search) [F]; vpu20_4v = the video processor firmware head and CAMERA_ICP = the camera ICP firmware head [I from vendor naming].
- The 4 cs35l41 bins are Cirrus Logic CS35L41 smart-amp DSP coefficient/calibration files; the mainline wm_adsp loader selects per-speaker tuning by component prefix exactly as #1174 records for cupid's T-/B- naming (cited, fetched there 2026-11-21) [F convention; T/B reading [I]]. db_type=AUDIOAMP is the corpus's own label. The unicorn bins differ in size from cupid's (1,940/4,888/1,944/4,884 vs 1,580/4,768/1,580/4,764) - different tuning builds [F].
- The manifest also lists cs35l41 .wmfw files, T-/B-handfree.txt, T-handset.txt, T-music.txt and the OIS firmware `unicorn_wide_bu24618_ois.{coeff,mem,prog}` in vendor/firmware - none of these are in the census (part of the vendor/firmware gap above) [F vs LineageOS].

### Group H - camera tuning + ArcSoft renderer resources (37 rows, 113,086,821 B)

| slice | rows | bytes | notes |
|---|---|---|---|
| vendor/etc/camera top level | 18 | 108,706,641 | night_align_lsc_tbl pair 88,080,384, snsc.bin 17,329,600, ellv.bin 2,733,792, deblur pair 356,088, mage_yuv_hdr_opencl.bin 182,168, CFR_para_* 9 files 23,691, arcsat_3sat.bin 368, MILDC_CALIB_0x01.bin 550 |
| resources/kernel + /32 + /64 | 10 | 1,017,912 | numeric-hash kernels x6 (1720888, 2821809890, 3711416411 in _32/_64 pairs), s31/t31 hash-named kernels 32-bit (6,796+322,112) vs 64-bit (6,800+325,612) |
| resources/render Effect dirs (BrightEye, BrightEyeV3, Makeup Classical/Native) | 9 | 3,362,268 | LeftEye/RightEye/left_eye/right_eye 360,028 each, eye_pupil.bin 90,028, Eyebrow.bin 127,628 x2, sh.bin 788,436 x2 |

python3 assertion passed: slice rows sum to 37, slice bytes sum to 113,086,821.

- The three `CFR_para_UW_V01{,_HD,_SN}.bin` files are byte-identical to each other (one md5, 3,645 B, 3 rows); `CFR_para_W_V01.bin` = `CFR_para_W_V01_SN.bin` (2,126 B) and `CFR_para_T_2x_V01.bin` = `CFR_para_T_2x_V01_HD.bin` (2,126 B) collapse pairwise; all 9 CFR rows share span exactly {Mi_12_Pro} - the CFR parameter set is byte-identical with zeus (Xiaomi 12 Pro), not with cupid [F].
- `ellv.bin` 2,733,792 B spans exactly {Mi_12S} (cupid's ellv is 2,225,696 B - a different build; unicorn's pairs with mayfly) [F]. `snsc.bin` 17,329,600 B spans {Mi_12S, Mi_12S_Ultra} (subfamily sensors - a sensor-calibration/scene binary hypothesis [I], function unverified). The `night_align_lsc_tbl_40962304.bin` (37,748,736 B = 36 MiB) and `night_align_lsc_tbl_40963072.bin` (50,331,648 B = 48 MiB) pair spans {Mi_12S, Mi_12S_Ultra, Mi_13, Mi_13_Pro, Poco_F5} - large night-mode lens-shading tables shared into the SM8475/SM8550 generation [F span; function naming-based [I]].
- The 4 eye renderer resources are 4 distinct md5s at the same 360,028 B size (LeftEye, RightEye, left_eye, right_eye) - mirrored per-eye models, not copies [F]; each spans {Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro}. eye_pupil.bin 90,028 B and the two sh.bin 788,436 B copies span exactly 9 devices {unicorn, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo} - the 12S-generation set extended with Mi_13/Mi_13_Pro/Poco_F6_PRo, notably without cupid/zeus [F]. The two Eyebrow.bin copies (127,628 B) are distinct md5s spanning the 6-device 12S set.
- The deblur pair (an Adreno OpenCL compiled kernel + its parameter blob [I]) is octet-exact, as in #1174. The numeric `1720888/2821809890/3711416411_32/_64` kernel pair set and the s31/t31 hash-named kernels span {Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro} - the 12S-generation ArcSoft OpenCL build set; the s31/t31 filenames embed concatenated hash-like tokens, recorded not parsed (same token structure as #1174's) [F names; structure interpretation [OPEN]].
- The census camera slice is a small extract: the LineageOS manifest lists 418 vendor/etc/camera entries for unicorn - most are outside the 840-row census [F].

### Group I - GPU kbc calibration blob (1 row)

`vendor/gpu/kbc/unified_ksqs.bin` 209,153 B, md5 `1a217e4b2ce9c57342343386aeef923a` (equals the value #1174 records for cupid's copy), db_type UNKNOWN, subfamily camera, shared by 9 devices (octet + Phone_2). The same kbc directory carries the gpu-family row sequence_manifest.bin (1,860 B) - not covered here. Not in the LineageOS manifest (fetched 2026-11-21), as with cupid - consistent with a device-generated calibration artifact rather than a shipped blob [I, unverified]. Function unknown; [OPEN].

### Group J - the radio partition images (2 rows)

| file | bytes | md5 | span |
|---|---|---|---|
| dsp.img | 67,108,864 (exactly 64 MiB) | `a6334ef3df24069beb3919bf716e34cb` | 5 {+ Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro} |
| vm-bootsys.img | 269,996,032 | `db7c51a3ae0d3f096a7e4ebcf605c5a2` | 5 {+ Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro} |

- dsp.img is exactly 64 MiB like cupid's, but is a different build (cupid's md5 `1cc3caa8c3c0b559174c2b34397492ba` per #1174) shared with the SM8475-class devices instead of Mi_12_Pro. Consistent with the Xiaomi `dsp` partition convention - a small filesystem image carrying DSP firmware copies [I]; contents unexamined [OPEN].
- vm-bootsys.img is new at the 12S generation (census: present on unicorn, Mi_12S, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro, Poco_F5; absent from cupid's census). Public fastboot flash guides list `fastboot flash vm-bootsys vm-bootsys.img` as a standard step on modern Qualcomm devices - a flashable partition image, distinct from radio/bluetooth [F from DroidWin/4PDA guides, fetched 2026-11-21]. VM = the virtualization/hypervisor guest boot system hypothesis [I, unverified]; contents unexamined [OPEN].

### Group K - undocumented modem/image model file (1 row)

`ancidf_model_tee` 4,271,903 B, md5 `5bd954e0968922a759fcc4a821645919`, db_type UNKNOWN, subfamily misc, at `xiaomi/unicorn/modem/image`, no file extension. Shared by exactly 7 devices: unicorn, Mi_12S, Mi_12S_Ultra, Mi_13, Mi_13_Pro, Poco_F6_PRo (corpus spelling), Redmi_K60_Pro - the Xiaomi SM8475/SM8550 generation. Web search and GitHub code search for the exact name return 0 results (2026-11-21): undocumented anywhere. The `tee` suffix suggests a TrustZone-consumed model payload and the `anc` prefix suggests an audio/anc or AI-model function - both naming-based [I]; function unknown, [OPEN].

## Cross-corpus md5-sharing profile [F]

424 rows, 335 distinct md5s. Sharing distribution (devices sharing a given md5, Mi_12S_Pro excluded -> rows): 0->79, 1->10, 2->9, 3->4, 4->33, 5->23, 6->2, 7->205, 8->37, 11->14, 13->2, 15->1, 21->2, 26->1, 33->2 (sums 424, python-verified). Bucket bytes: 34,603,676 + 2,757,483 + 17,423,265 + 120,970 + 345,219,100 + 89,987,825 + 11,181,723 + 21,966,631 + 2,318,083 + 272,277 + 1,028 + 304 + 1,816 + 304 + 0 = 525,854,485 (python-verified).

| share span | rows | content |
|---|---|---|
| corpus-unique (79 rows, 34,603,676 B) | 79 | gfuni + gfuni6 sets (20), 15 remaining TZ mdts + 15 b08 terminals (30), slpi body (14), mbn_ota.md5sum + mbn_build_utc.txt, EVA/VPU/ICP mdts (4), cs35l41 x4, cpusys_vm.mdt + fw_ipa_gsi_3.0_w.elf, arcsat_3sat + mage_yuv_hdr_opencl + MILDC_CALIB |
| 2 devices | 9 | snsc.bin, mfido.b00/b02/b06, seccammil.b00, slpi.b07, mbn_sw.dig/.txt, oem_sw.txt - all with the {Mi_12S, Mi_12S_Ultra} pair except slpi.b07 ({Mi_12, Mi_12_Pro}) |
| 4-5 devices (12S-generation sets) | 33 + 23 | 12 TZ b00s + seccammil.b01-b07 + the 6 numeric OpenCL kernels + s31/t31 x4 + dsp.img + vm-bootsys.img (4); devauth.b00 + devauth.b01-b07 + gpqese.b00 + gpqese.b01-b07 + night_align pair + 4 eye resources + 2 Eyebrow + slpi.b15 (5) |
| 6 devices | 2 | ancidf_model_tee, fingerpr.b01 |
| 7 devices (octet-exact) | 205 | all 42 bd_*.elf, 90 hpnv tiles, 56 TZ-app segments, amss.bin x2 + Data/Data20.msc + gptauuid.xml, slpi.b01/b04/b06, oem_hw/dsda/ss/ct_volte + mbn_hw.dig, evautil64.mdt (vendor copy), deblur pair |
| 8-9 devices | 37 | unified_ksqs.bin, hpbtfw21.tlv + 10 hpnv tiles, 19 TZ segments, slpi.b03/b10, mbn_hw.txt (all octet + Phone_2); eye_pupil + sh.bin x2 (the 12S-generation set + Mi_13/Mi_13_Pro/Poco_F6_PRo, no cupid/zeus) |
| 14 devices | 2 | slpir.jsn, slpius.jsn (octet + Edge_30_Fusion, Moto_G200, OnePlus_9/9RT/9_Pro, Phone_2) |
| 12 devices (octet + OnePlus_9/9RT/9_Pro + Phone_2) | 14 | hpnv20 full set + hpbtfw20.tlv, cardapp.b04/b05 |
| 22-27 devices | 4 | evautil64.b04, ops.b04 (22), evautil64.b05 (27), ops.b05 (16) |
| 34 devices | 2 | oem_*_null.txt 0-byte placeholders (fleet-wide) |

- 333 of 424 rows (491,173,350 B) are byte-identical with at least one Mi_12S `other`-family row (Mi_12S censuses 407 `other` rows of its own - a decomposition is a separate sibling issue, not this one); 331 with Mi_12S_Ultra; 283 rows (37,150,736 B) with a Mi_12 `other`-family row [F].
- Leverage reading [I]: one RE pass on the octet-shared rows (205) covers the whole Xiaomi SM8450/SM8475 fleet in this corpus; the corpus-unique 79 rows are where Mi_12S_Pro-specific RE value concentrates (gfuni/gfuni6, slpi body, the region pair, the EVA/ICP/VPU mdts).

## ISA / interface facts

- `isa_identified` is empty on all 840 Mi_12S_Pro rows and `interface_documented=n` on all 840 - honestly un-RE'd at instruction level in the corpus [F]. No instruction-level claim is made here [N].
- db_type on the 424 rows, python-verified: UNKNOWN 325, ELF64 85, FINGERPRINT 9, AUDIOAMP 4, CERT 1 (fw_ipa_gsi_3.0_w.elf - the CERT label on an ELF firmware is a db_type mislabel [I]). ELF64 = 17 TZ mdts + 16 TZ b00s + slpi.mdt + slpi.b00 + 42 bd_*.elf + amss.bin x2 + cpusys_vm.mdt + the 5 vendor/firmware mdts.
- Verified loader surfaces [F]: mainline remoteproc PAS compatibles `qcom,sm8450-{adsp,cdsp,slpi,mpss}-pas` in sm8450.dtsi (cited from #1174's fetch) cover the adsp/cdsp/slpi/amss-modem images; the trustlet mdt+bNN container is the publicly documented QSEE/PIL format (Check Point 2019, Quarkslab, LSE MBN guide; fetched 2026-11-21), loaded by QSEE at boot [I for the load path]; mainline wm_adsp covers the CS35L41 coefficient files (cited from #1174); the BT NVM tiles are HCI-config downloads by the btusb/qca driver family [I]; none of bd_*/hpnv beyond the linux-firmware qca subset is a kernel-loaded file [I].
- The split-PIL container grammar (mdt = ELF program-header image, bNN = loadable segments, jsn = servreg JSON) is established in-repo (research/fleet/qdsp6sw-container.md, #606) and applied by siblings #1168/#1174/#1186; groups A, B, C (cpusys_vm) and G use exactly that grammar [F].

## Honest negatives

- No payload was fetched, hashed or decoded in this issue: every byte fact is census metadata or a fetched public manifest/spec page; byte-identity claims rest on the corpus md5 column, not on fresh hashing. [OPEN]
- `ancidf_model_tee` (4,271,903 B) is undocumented everywhere we searched; its name is the only evidence of function. [OPEN]
- vm-bootsys.img (269,996,032 B) and dsp.img (67,108,864 B) contents are unexamined; the partition semantics are naming/public-guide inference. [OPEN]
- The exact function of gfuni/gfuni6 (and why unicorn carries two region trustlet sets where cupid carries one) is unknown; GF naming unverified. [OPEN]
- The census under-covers the vendor-tree subsystem firmware bodies (CAMERA_ICP 26 non-mdt entries, evass/evass-lt-21 bNN+mbn sets, vpu20_4v bNN+mbn, cs35l41 .wmfw, OIS unicorn_wide_bu24618_ois files) and the wider camera tree (manifest 418 entries vs census 37) that the LineageOS unicorn manifest lists - census gaps of the upstream extract, recorded here, not device absences. [F vs LineageOS; the gap reading is [I]]
- The modem/image TZ-app bodies and the bluetooth/image BT sets have no LineageOS-manifest contrast (the manifest packages neither directory - they ship inside the radio partition images [I]); census completeness for them is not independently checkable. [OPEN]
- Byte-level diff between unicorn's and linux-firmware's WCN6750 NVM tiles is excluded by #1174's size deltas but not performed. [OPEN]
- Whether unicorn's radio partition physically carries slpi.b22 (absent from census like adsp.b24) is not decodable from the census alone. [OPEN]
- The ArcSoft kernel-resource filename tokens (s31/t31... and the numeric 1720888/2821809890/3711416411 pairs) are recorded, not parsed. [OPEN]
- The corpus device name `Poco_F6_PRo` (capital R) is a census naming quirk, recorded as-is. [F]

## What would upgrade this finding

1. Payload-decode vm-bootsys.img - the largest single artifact in the family (269,996,032 B) and new at the 12S generation; a mount/hash of its inner filesystem would be the first in-corpus look inside a vm-bootsys partition image.
2. Payload-decode one SM8475 TZ-app mdt (gfuni.mdt is corpus-unique and heads the largest unique payload) - first SM8475 PIL metadata decode in the corpus (sibling #1174 lists the same gap for cupid).
3. Have the lead split `cpusys_vm.mdt` ownership (other vs tz) into a census rule - now confirmed on two devices (cupid #1174, unicorn).
4. Correct the inventory SoC cell for Mi_12S_Pro (empty; SM8475) - already flagged by #1186; still empty at 0fe1ba0.
5. Byte-diff one hpnv21 tile against the linux-firmware qca copy to pin the +8 B delta (carried over from #1174).
6. Identify ancidf_model_tee: strings/headers of the 4,271,903 B payload would settle whether it is an audio-ANC or camera-AI model consumed through TrustZone.

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment (Gate -1) and DELTA comment (Gate 0). Checks: GitHub code search `"gfuni" unicorn trustlet` and `"ancidf_model_tee"` (2026-11-21, adineo-cmd excluded) -> 0 results; web `"vm-bootsys.img" Xiaomi radio partition` -> fastboot-guide documentation only; web `"ancidf_model_tee"` -> 0 results; web `Xiaomi 12S Pro firmware trustlet mdt b00 reverse engineering` -> format-level public sources (Check Point 2019, Quarkslab, LSE MBN guide, Google Project Zero) only; linux-firmware WHENCE/qca facts cited from #1174's 2026-11-21 fetch; mainline sm8450.dtsi compatibles cited from #1168/#1174 fetches; LineageOS unicorn proprietary-files.txt (lineage-22.2) fetched 2026-11-21 for the manifest contrasts; no public source documents the Mi_12S_Pro other-family census itself. DELTA posted; proceeding under it.

Not legal advice; no proprietary payload accessed or committed - all facts are census metadata plus public trees, manifests and specs.
