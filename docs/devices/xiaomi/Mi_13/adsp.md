# xiaomi Mi_13 - `adsp` family status (116 rows - PRESENT, census-complete; three-container grammar: modem-partition split-PIL firmware + companion `adsp_dtb` split image + vendor-tree Hexagon-TP `bm3` graph payloads; SM8550-generation signature)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1222](https://github.com/adineo-cmd/open-device/issues/1222)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site f974d67), `upstream-contribution/blob-database/device-inventory.csv`, the LineageOS `android_device_xiaomi_fuxi` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), torvalds/linux master `arch/arm64/boot/dts/qcom/sm8550.dtsi` (fetched 2026-11-21), linux-firmware WHENCE (git.kernel.org plain/WHENCE, fetched 2026-11-21), public spec pages (2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_12/adsp.md (#1168), docs/devices/xiaomi/Mi_12S_Pro/adsp.md (#1186), docs/devices/xiaomi/Mi_12T_Pro/adsp.md (#1204). No payloads fetched by this issue; every number is command output or a recorded fetch.

**Verdict: the `adsp` family is PRESENT on Mi_13 and the census is COMPLETE for both halves - 116 rows, 275,406,130 B, 101 distinct md5s, all db_type=MODEM.** The rows split across three different containers: (a) 60 rows at `xiaomi/fuxi/modem/image` = the signed split-PIL ADSP firmware image (`adsp.mdt` + 56 `adsp.bNN` segments, gaps at b32/b37/b57; **b24 IS present**, unlike the whole Xiaomi 12/12S family) plus the 3-file servreg JSON trio (`adspr.jsn`, `adsps.jsn`, `adspua.jsn` - one manifest more than SM8450/SM8475 devices); (b) 4 rows = the `adsp_dtb.mdt` + `b00-b02` companion split image, a new SM8550-generation container whose kernel-side memory reservation (`q6_adsp_dtb_mem`) is public in mainline `sm8550.dtsi`; (c) 52 rows at `xiaomi/fuxi/vendor/lib/rfsa/adsp` = Hexagon Tensor Processor (QNN/HTP) serialized neural-network graphs (`bm3a68v08s11nNN` 14 files + `bm3a73v08s11nNN` 38 files) delivered at runtime over FastRPC - **not modem code** despite the MODEM db_type (in-repo fleet finding, cited below). The 52 vendor-tree rows match the LineageOS fuxi packaging manifest file-for-file. There is no structural absence and no census gap. The 116-row shape is the SM8550-generation signature: SM8450 (Mi_12) censuses 46 rows and SM8475 (Mi_12S_Pro) 67; the +49-row delta over SM8475 is exactly +36 modem/image rows (31 extra bNN segments, +4 `adsp_dtb`, +1 `adsps.jsn`) and +13 vendor-tree rows (52 bm3 replacing 33 bm2n + 6 audio resources that leave the family).

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 13 (China, model 2211133C; global 2211133G); codename `fuxi` | `device-inventory.csv` (`build_codename=fuxi`) [F]; public spec pages (2026-11-21) [F] |
| SoC | Qualcomm **SM8550 Snapdragon 8 Gen 2**; Adreno 740; Hexagon V73 DSP | public spec pages (2026-11-21) [F]. **The coverage-matrix SoC cell is empty and the inventory's is fuxi only** - SoC supplied here [F]; flag for the lead. The task briefing's guess "SM8450" is wrong: Mi 13 is SM8550 [F] |
| released | December 2022 (announced 2022-12-11, China launch; global early 2023) | public spec pages (2026-11-21) [F] |
| stock base | `OS2.0.213.0.VMCCNXM` | LineageOS fuxi `proprietary-files.txt` header "Unpinned blobs from fuxi (OS2.0.213.0.VMCCNXM)" (fetched 2026-11-21) [F] |
| census scope | 700 rows in 9 families (other 342, adsp 116, tz 100, wifi 57, modem 43, cdsp 21, boot 15, gpu 5, bt 1) | coverage-matrix.csv [F] |
| priority | P3 | coverage-matrix.csv, all 116 adsp rows [F] |

Inventory flags for the lead: the matrix soc cells of the other 8-device bm3 share-group members are empty (Mi_13_Pro, Poco_F6_PRo, OnePlus_12R) or wrong - Xperia_1_V and Xperia_5_V carry `Qualcomm SM6375 Snapdragon 695` in the matrix but both are SM8550-AB phones per public specs [F; flag]. All eight members of the bm3 8-device share group are Snapdragon 8 Gen 2 devices [I - consistent share set corroborates the SoC mapping].

## Census evidence [F]

All 116 adsp rows: `blob_family=adsp`, `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, `db_type=MODEM`, priority P3; 101 distinct md5s. The only internal duplication is a 16-file byte-identical run `bm3a73v08s11n07.bin`, `bm3a73v08s11n13.bin`-`bm3a73v08s11n27.bin` (941,472 B, md5 `76063352ea0be968726175c5f7e99723` each) - 116 rows minus 101 md5s = 15 duplicate rows, all of them that run (python, this session).

| group | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp.mdt` + 56 `adsp.bNN`, gaps b32/b37/b57) | 57 | 39,423,647 | `xiaomi/fuxi/modem/image` |
| servreg manifests (`adspr.jsn`, `adsps.jsn`, `adspua.jsn`) | 3 | 1,731 | `xiaomi/fuxi/modem/image` |
| `adsp_dtb` companion split image (`adsp_dtb.mdt` + `b00`-`b02`) | 4 | 16,464 | `xiaomi/fuxi/modem/image` |
| HTP graph payloads (`bm3a68` 14 + `bm3a73` 38) | 52 | 235,964,288 | `xiaomi/fuxi/vendor/lib/rfsa/adsp` |
| total | 116 | 275,406,130 | - |

Verified decomposition: 8,524 (mdt) + 39,415,123 (56 bNN) + 1,731 (3 jsn) + 16,464 (adsp_dtb) = 39,441,842 modem/image bytes over 64 rows; 180,211,528 (14 bm3a68) + 55,752,760 (38 bm3a73) = 235,964,288; 39,441,842 + 235,964,288 = 275,406,130 (python, this session). The vendor-tree half is 85.7% of family bytes (bm3a68 graphs alone 65.4%) - the modem-partition half is a shell around the graph payloads. There are **no** hrtf5c/misound rows in the fuxi adsp family: `hrtf5c.bin` (164,480 B) exists on fuxi but is classified family=`other` at `xiaomi/fuxi/odm/etc/audio`, and no misound file occurs in Mi_13's 700-row census - the audio-resource tier that sits inside the adsp family on SM8450/SM8475 Xiaomi devices (#1168, #1186) has left the family here [F].

### The 60 firmware rows in modem/image (split-PIL ADSP firmware + servreg trio)

Shell files (8):

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| adsp.mdt | 8,524 | `a147518a03a0ad79b062d488d940366e` | 1 (Mi_13 only) |
| adspr.jsn | 513 | `5d262bb7661402a8d7ca9724bbb45d46` | 30 |
| adsps.jsn | 515 | `cddb328503f04c634cc3251b89dad765` | 16 |
| adspua.jsn | 703 | `a43d66d0549e33cf421e25be06260ce0` | 30 |
| adsp_dtb.mdt | 4,044 | `3b610c4805736e39870200115f3ec45f` | 1 (Mi_13 only) |
| adsp_dtb.b00 | 148 | `50447221088ab1b5ac1ed18c04697a7f` | 6 |
| adsp_dtb.b01 | 8,376 | `722a1b083ca9d6c36dfc682dff7039c6` | 6 |
| adsp_dtb.b02 | 3,896 | `b12298c60e7ac1f1576030205d15175e` | 1 (Mi_13 only) |

Segment files (56; `devices` = corpus-wide count of devices carrying that byte identity, from the md5 sweep):

| file | bytes | md5 | devices |
|---|---|---|---|
| adsp.b00 | 1,940 | `f5eada83e2d2d5e0935e58605c8deb64` | 1 |
| adsp.b01 | 6,824 | `eb26f77eb6293479eba82956b6e535e3` | 4 |
| adsp.b02 | 6,453,380 | `aeb04ec056bfe5a1d30ddb2115ad940f` | 1 |
| adsp.b03 | 27,380 | `2dd7c0c473d460f1124030e16499a2c8` | 4 |
| adsp.b04 | 43,088 | `5888babb1d38ae6a8f8d5d10020633ee` | 4 |
| adsp.b05 | 802,816 | `7932fb5396e0d55b0756c2247c102b80` | 1 |
| adsp.b06 | 236 | `8012a2aa374b5b7ee866bbdc158dc575` | 3 |
| adsp.b07 | 20,660 | `6f81752bf6cc8e6e1d2d5a00fb7b2feb` | 3 |
| adsp.b08 | 2,610,360 | `f9fcdc08aa3ad1e039ab69cc4d543c86` | 1 |
| adsp.b09 | 264,032 | `53390a2c3935545e62c975a43f6da419` | 1 |
| adsp.b10 | 1,488 | `ede78053c6f76c09e65b01b25e337750` | 4 |
| adsp.b11 | 22,572 | `de1e5e897e8529b2097c7440e0c81624` | 4 |
| adsp.b12 | 5,684 | `8a37e08c7df83acde8a544bd454aea85` | 4 |
| adsp.b13 | 209,504 | `1a31d4d8a755caad3a0f415b75017f70` | 1 |
| adsp.b14 | 10,872 | `993fc1a0a4acb0c22dd0feca1bafa095` | 1 |
| adsp.b15 | 108 | `54fce8140fd50e3200fb7ef2a3649dda` | 3 |
| adsp.b16 | 140,032 | `13dd9865f392c1216cb51d782d92e030` | 1 |
| adsp.b17 | 82 | `b0a979071af76ae44d67a82a2139abcf` | 1 |
| adsp.b18 | 434,176 | `2f19bcb3470eaa1863bacae26946262c` | 1 |
| adsp.b19 | 3,602,756 | `df363c80749a458e957b37d1985e40de` | 1 |
| adsp.b20 | 238,712 | `3dffb2fdf3115a3f5c0e9e328ae07a3c` | 1 |
| adsp.b21 | 272 | `33dfb400eb0f1306146731116476bc2c` | 1 |
| adsp.b22 | 526,929 | `305020b741b50276f3e0a95a4751c0b9` | 1 |
| adsp.b23 | 901,120 | `a6548e1440944212dcc308d4584db82c` | 1 |
| adsp.b24 | 2,623,640 | `277bf5e1fdeb94e567546c9eeccf7843` | 1 |
| adsp.b25 | 2,912,260 | `b792a4ae5751c9c3ea696ef8d9f300a2` | 1 |
| adsp.b26 | 868 | `cc20a5d454c5bbede0807e49f6f0c7b3` | 2 (Mi_13_Pro carries it as `adsp.b25`) |
| adsp.b27 | 5,484 | `3eef8bc0984562f0ebc2a4c9c9d530cd` | 4 (Mi_13_Pro + Poco_F6_PRo carry it as `adsp.b26`) |
| adsp.b28 | 23,642 | `c15155815a6922ad2e136c7cbd97cea9` | 1 |
| adsp.b29 | 6,776 | `67e77c3397f887752911db0966113966` | 1 |
| adsp.b30 | 109,320 | `dc9fb8b3b3793849c346020c06c220e2` | 1 |
| adsp.b31 | 130,107 | `e3ec33b19cef9bf930257e4d195d2318` | 1 |
| adsp.b33 | 17,200 | `099b61061c6eacb3b647b39e4acd3805` | 1 |
| adsp.b34 | 24,732 | `9e1663120253b71c6bb6bec35410b762` | 1 |
| adsp.b35 | 304 | `b23541033517ee178793c3cb3f030b63` | 1 |
| adsp.b36 | 8,100 | `fb218b59dacf93430e4ae66f71e1067c` | 1 |
| adsp.b38 | 63,320 | `978f593c224d1f30359509500d95f508` | 1 |
| adsp.b39 | 4,148 | `9a3b2a38231234400bc882718b9de369` | 1 |
| adsp.b40 | 53,988 | `4375ee4cafe1d33f49dbb9e8a7d99ce6` | 1 |
| adsp.b41 | 1,029,852 | `9d599c5fc45729d833aaca60d887d86c` | 1 |
| adsp.b42 | 495,616 | `346b79e32ef6b577d530828eb23e36bf` | 1 |
| adsp.b43 | 11,590,128 | `06b1dddf79f0895b8c9228bdbb479751` | 1 |
| adsp.b44 | 851,976 | `5b1b3e240d2bba7e8acf844d800b55aa` | 1 |
| adsp.b45 | 1,352 | `565e91b425cf5c625250db86fce06d6d` | 4 |
| adsp.b46 | 192,928 | `65629528d13651848d8e68a904f34fd5` | 4 |
| adsp.b47 | 5,600 | `559a5a848b747b198e397d3c8d8c8ce4` | 4 |
| adsp.b48 | 11,224 | `bd2ffcceba924fe43ccc943dc55a522c` | 4 |
| adsp.b49 | 5,064 | `50aa98f52b791958eca11ca80cc18168` | 4 |
| adsp.b50 | 79,040 | `d54b3110bec6f25703b0554191cf328c` | 4 |
| adsp.b51 | 592,292 | `83ee8bf48dbb2c59e911bcb41f6c233e` | 4 |
| adsp.b52 | 880,640 | `199f2a917f7710a542e7eda4563c2220` | 1 |
| adsp.b53 | 79,499 | `08c2049688030ec693b5c37e7e968d6f` | 1 |
| adsp.b54 | 966,656 | `33616c73c4ea3fe61c6768de5e6bfc2b` | 1 |
| adsp.b55 | 49,152 | `52b6f29c5b5a48694ff2e062cd2d5b43` | 1 |
| adsp.b56 | 268,608 | `241f8db61247d77bee0ccf32bc19a78c` | 1 |
| adsp.b58 | 6,584 | `c00c990aad7cd3e36a6177f044bc184c` | 1 |

The sequence runs b00..b31, b33..b36, b38..b56, b58 - the build skips segment indices 32, 37 and 57 (python, this session). **adsp.b24 IS present** (2,623,640 B): the b24 gap recorded for the Xiaomi 12/12S family (#1168: zero b24 rows on Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro) is a family property of those builds, not of Xiaomi or of the SM8450/8475 platforms - every SM8550-generation adsp census in the corpus carries b24 (Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro, Edge_40_Pro, OnePlus_11_5G, OnePlus_13) [F]. 18 of the 56 bNN rows carry byte identities shared with other corpus devices: nine 3-4-device segments (b01, b03, b04, b10, b11, b12 with Mi_13_Pro/Poco_F6_PRo/Redmi_K60_Pro; b06, b07, b15 with Mi_13_Pro/Redmi_K60_Pro), seven 4-device segments (b45-b51 with Mi_13_Pro/Poco_F6_PRo/Redmi_K60_Pro), the index-shifted b27 (Mi_13_Pro and Poco_F6_PRo carry it as `adsp.b26`) and b26 (Mi_13_Pro carries it as `adsp.b25`) - see below; the other 38 bNN identities are fuxi-exclusive.

### The 52 vendor/lib/rfsa/adsp rows (HTP graph payloads)

bm3a68 set (14 files, 180,211,528 B):

| file | bytes | md5 | devices |
|---|---|---|---|
| bm3a68v08s11n29.bin | 18,246,152 | `b3fa6733cdd910467543f0babd0ecf2d` | 2 |
| bm3a68v08s11n30.bin | 12,343,240 | `e8b6f92fb148d5b6353acd539266123c` | 2 |
| bm3a68v08s11n35.bin | 18,252,160 | `73227839cd139b160a62168b9dbe7a9c` | 2 |
| bm3a68v08s11n36.bin | 18,231,000 | `ab682c079127ae46f6f671f13db97386` | 2 |
| bm3a68v08s11n37.bin | 18,250,920 | `1903c2614d8a12bb555fc4aa273bbae7` | 2 |
| bm3a68v08s11n38.bin | 12,339,496 | `c28b4c68448d285355a80cf7f3d48df9` | 2 |
| bm3a68v08s11n39.bin | 12,335,984 | `56ed5b2f1e5f67bf7ada698aa5d1bd3c` | 2 |
| bm3a68v08s11n40.bin | 12,356,704 | `ca6e325efa0582c074f00be2c440d60d` | 2 |
| bm3a68v08s11n46.bin | 12,503,928 | `d30eb513ddd5d585f26dba4a38fce945` | 2 |
| bm3a68v08s11n47.bin | 12,503,888 | `d35450026436a74e738ea3fbade1d851` | 2 |
| bm3a68v08s11n48.bin | 12,506,752 | `eebbb529861401f9c229309246e8cd7b` | 2 |
| bm3a68v08s11n49.bin | 12,506,816 | `c2a6b7ff364d4fffae0a0a1604df7012` | 2 |
| bm3a68v08s11n52.bin | 3,923,272 | `8e5f14d19af0bd8c24eb5d3cd9af5633` | 8 |
| bm3a68v08s11n53.bin | 3,911,216 | `7c6ad0e8fad6f70846ea384f402b8e3c` | 8 |

bm3a73 set (38 files, 55,752,760 B; the 16-file run collapsed to one identity):

| file | bytes | md5 | devices |
|---|---|---|---|
| bm3a73v08s11n02.bin | 2,246,760 | `01f2c92ac8323b913e914f2a6e4656d8` | 8 |
| bm3a73v08s11n03.bin | 444,120 | `7266bfa2a79d46193db08533ebd6456b` | 8 |
| bm3a73v08s11n04.bin | 596,520 | `38f58f4f91527dd45e760459cc196987` | 8 |
| bm3a73v08s11n06.bin | 762,616 | `88f4ccd34ec3bd8a5e0db25f1037f8e3` | 8 |
| bm3a73v08s11n07.bin | 941,472 | `76063352ea0be968726175c5f7e99723` | 8 |
| bm3a73v08s11n08.bin | 2,641,560 | `a91de7554dc4d2c38ddebc2f308af4d4` | 8 |
| bm3a73v08s11n09.bin | 2,629,776 | `de05ecc113cd0f093dc75295038879fe` | 8 |
| bm3a73v08s11n12.bin | 2,351,360 | `649a755ac1ae5d3e6ce0fe58b073bbdd` | 8 |
| bm3a73v08s11n13.bin .. n27.bin | 941,472 each (15 slots) | `76063352ea0be968726175c5f7e99723` (all) | 8 (as one identity) |
| bm3a73v08s11n28.bin | 1,290,128 | `5d2b0e108e6e199294216287e6530a1b` | 8 |
| bm3a73v08s11n41.bin | 2,876,456 | `881026c0eff6eb08864595d66af8c2ad` | 8 |
| bm3a73v08s11n42.bin | 2,857,688 | `57c5afd62c028d9feaba8fda0ab7da11` | 8 |
| bm3a73v08s11n43.bin | 3,835,064 | `6b67955255621fe40c44bafc6862c253` | 8 |
| bm3a73v08s11n44.bin | 4,020,128 | `2832aa5e40e9584a6e7ba3c1f38ea10d` | 8 |
| bm3a73v08s11n45.bin | 718,752 | `41babdba62df0ce3b2e2e275d0893a8f` | 8 |
| bm3a73v08s11n50.bin | 4,203,432 | `3f7f87b0e1cc2efe450f14e8f5d5d60d` | 8 |
| bm3a73v08s11n51.bin | 4,183,584 | `4f0cd2417fc97916ee37b18f1e6f35a2` | 8 |
| bm3a73v08s11n57.bin | 718,752 | `fc021a80971442e0222bc010eb98560f` | 3 |
| bm3a73v08s11n58.bin | 718,752 | `5334f1cb412f688b95f94e96904d17f2` | 3 |
| bm3a73v08s11n59.bin | 718,752 | `aa38f17039b9e77eff151b448a48b3c7` | 3 |
| bm3a73v08s11n60.bin | 718,752 | `b355d4b2bdc12805f4fec4c26d169de5` | 3 |
| bm3a73v08s11n61.bin | 718,752 | `99a1f93020c9ab6f073699076b875974` | 3 |
| bm3a73v08s11n62.bin | 718,752 | `c888b729b1af9618386e9722b4501327` | 3 |
| bm3a73v08s11n63.bin | 718,752 | `f820af51bcd194170a588f4651c34794` | 3 |

The 16-file run (n07, n13-n27) is 15,063,552 B of literally one payload copied under sixteen filenames (16 x 941,472 B, python, this session). Filename is not identity, fleet-content finding F-75 (research/laptop/qualcomm-adsp-bm2n-fleet-content.md): on SM8450 trees the same principle put `281755c0...` under bm2n07 and n14-n27 slots; the SM8550-generation equivalent is `76063352...` under bm3a73 n07 + n13-n27, and corpus-wide that one byte identity serves 8 devices x 16 filename slots = 128 rows [F].

## Census completeness - proven against the LineageOS packaging manifest [F]

- `LineageOS/android_device_xiaomi_fuxi` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21) lists under `odm/mount/camera/lib/rfsa/adsp/` (mapped onto `vendor/lib/rfsa/adsp/`) exactly the 52 bm3 files the census carries - bm3a68 n29-n40, n46-n49, n52, n53 + bm3a73 n02-n09, n12-n28, n41-n45, n50, n51, n57-n63 - file-for-file match, zero extra, zero missing (programmatic set comparison, 52 == 52).
- The same manifest contains **zero** `adsp.mdt` / `adsp.bNN` / `adsp_dtb.*` / `.jsn` entries: LineageOS does not package the split-PIL firmware into the vendor tree; on fuxi those files live in the device's modem partition, which is where the census's 64 `modem/image` rows come from (the Xiaomi/OnePlus packaging pattern recorded in #1168/#1186, citing #1096 for the Samsung contrast) [F].
- The manifest ships stock-base `OS2.0.213.0.VMCCNXM` blobs; its ADSP skel `.so` inventory is direct vendor evidence of the SM8550 DSP stack: `libQnnHtpV73.so`, `libQnnHtpV73Skel.so`, `libSnpeHtpV73Skel.so` (V73 native), plus backward-compat `libSnpeHtpV68Skel.so`, `libSnpeHtpV69Skel.so`, `libSnpeDspV65Skel.so`, `libSnpeDspV66Skel.so`, and `libVppFrcQnnHtp.so` [F]. Those `.so` files appear nowhere in Mi_13's 700-row census - the census's adsp family is the `.bin`/firmware payload view, not the shared-library view (same contrast as #1168/#1186) [F].
- The manifest also carries `odm/etc/audio/misound_res_spk_power_game.bin` and `odm/etc/audio/misound_res_spk_power_video.bin` - neither occurs in Mi_13's 700-row census extract (census scope gap, recorded not explained); fuxi's `hrtf5c.bin` (164,480 B) is in the census but classified family=`other` at `xiaomi/fuxi/odm/etc/audio` [F].

## Container and interface facts

### Split-PIL firmware (the 57 segment+mdt rows) and the servreg trio

- The mdt+bNN form is Qualcomm's signed PIL split container: `adsp.mdt` (8,524 B) is the ELF header/program-header image, the `bNN` files are its loadable segments, the `.jsn` files are servreg metadata. Mainline Linux parses this format in its Qualcomm peripheral image loader; the in-repo modem-DSP container study (research/fleet/qdsp6sw-container.md, #606) documents the public `QCOM_MDT_RELOCATABLE` p_flags bit [F]. `adsp.mdt` at 8,524 B sits exactly in the SM8550-class cluster recorded in #1186 (Mi_13, Mi_13_Pro, OnePlus_11_5G, Poco_F6_PRo, Redmi_K60_Pro) - re-verified this session [F].
- Mainline `arch/arm64/boot/dts/qcom/sm8550.dtsi` (torvalds/linux master, fetched 2026-11-21): `remoteproc_adsp: remoteproc@6800000`, compatible **`qcom,sm8550-adsp-pas`**, `memory-region = <&adspslpi_mem>, <&q6_adsp_dtb_mem>` (lines 3161-3183). Unlike SM8475 (no mainline DT at all, #1186), the SM8550 ADSP loader grammar is first-class mainline [F]. PAS = peripheral authentication service: the kernel hands the signed adsp image to TrustZone for verify-and-boot.
- The second memory region is the public kernel-side counterpart of the census's `adsp_dtb` 4-file set: `q6_adsp_dtb_mem: q6-adsp-dtb-region@9e980000` (512 KiB, no-map; sm8550.dtsi line 978). The fuxi modem partition ships that companion image as its own 4-file split ELF (`adsp_dtb.mdt` 4,044 + `b00` 148 + `b01` 8,376 + `b02` 3,896 = 16,464 B), which fits the 512 KiB reservation [I - structural reading of the name + mainline reservation + linux-firmware precedent; the image contents are undecoded, [OPEN]]. The same construct is mainlined as `adsp_dtb.mbn` for qcom/sm8750, glymur, hawi, kaanapali, maili, nord, eliza, x1e80100 and as `adsp_dtbs.elf` inside the x1e80100 device dirs in linux-firmware WHENCE (fetched 2026-11-21, lines 7557-7747) - i.e. the ADSP-firmware DTB companion is a public Qualcomm pattern from the SM8550 generation onward, here seen in split-PIL form [F for the public analogs; fuxi's mapping [I]].
- The servreg trio: `adspr.jsn` (513 B) and `adspua.jsn` (703 B) are byte-identical across the exact 30-device fleet #1168/#1186 recorded - re-verified this session, members: Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Moto_G200, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, OnePlus_9, OnePlus_9_Pro, OnePlus_9RT, Pad_2_Pro, Pad_Pro, Phone_1, Phone_2, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro [F]. `adsps.jsn` (515 B) is the third manifest SM8450/SM8475 Xiaomi devices do not carry; its fuxi byte identity spans 16 devices (Edge_30, Edge_40_Pro, FP5, FP6, Mi_13, Mi_13_Pro, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, Pad_2_Pro, Pad_Pro, Phone_1, Poco_F6_PRo, Redmi_K60_Pro) [F]. `adsps.jsn` is publicly shipped by linux-firmware for other SoCs (qcm2290, qcm6490, qcs6490, qcs615, qrb4210, x1e80100, sm8750 - WHENCE lines 7436-7747) [F]; its subdomain semantics are not decoded here [OPEN].
- Per-build segment-index gaps: fuxi skips b32/b37/b57; Mi_13_Pro, Poco_F6_PRo and OnePlus_11_5G skip b31/b36/b57; Edge_40_Pro skips b32/b37/b55/b57/b58; OnePlus_12 (SM8650) skips b24/b55/b57/b58 while OnePlus_13 (SM8750) keeps b24. The bNN gaps are per-build program-header artifacts, not extraction accidents - the LineageOS manifest does not package them, so no packaging-side check is possible [I; payload verification [OPEN]].
- One-slot index shift across builds: fuxi's `adsp.b26` (868 B, `cc20a5d4...`) is the same payload that sits at Mi_13_Pro's `adsp.b25` slot, and fuxi's `adsp.b27` (5,484 B, `3eef8bc0...`) sits at Mi_13_Pro's and Poco_F6_PRo's `b26` slots and Redmi_K60_Pro's `b27` slot (md5 sweep, this session) [F]. Filename is not identity, now also at the segment-index level: per-build program-header numbering shifts between nominally same-platform builds [I]. fuxi b28 and nuwa b27 are both 23,642 B but carry different bytes (`c1515581...` vs `9b0bc9cf...`) - the builds diverge beyond the shift [F].
- Mi_13 vs Mi_13_Pro (nuwa): 73 of 116 rows are byte-identical (filename+size+md5): all 52 bm3 files, the 3 jsn files, 16 same-index bNN segments (b01, b03, b04, b06, b07, b10, b11, b12, b15, b45-b51) and `adsp_dtb.b00`/`b01`. The 43 differing rows are the personalized ADSP OS build: `adsp.mdt` + 40 bNN segments + `adsp_dtb.mdt`/`b02` (python, this session) - per-device OS builds differ only where the vendor personalized them, exactly the #1186 variant-matrix prediction [F].
- 41 of Mi_13's 101 adsp md5s are fuxi-exclusive (38 bNN segments + `adsp.mdt` + `adsp_dtb.mdt` + `adsp_dtb.b02`) - the ADSP OS image itself is a fuxi-specific build [F].
- The in-repo signed-PIL metadata decode (research/fleet/pil-metadata-sweep.md) proves the per-phdr hash-slot metadata layout fleet-wide on SM8250 (SHA-384 slots) and SDM845 (SHA-256 slots). No SM8550 image has been decoded in-repo; the fuxi adsp.mdt/adsp_dtb.mdt phdr counts, hash widths and cert chains are [OPEN].

### HTP graph payloads (the 52 bm3 rows) - established in-repo findings, not re-derived

- research/laptop/qualcomm-adsp-bm2n-fleet-content.md (measured payloads, 49 fetched, 48/48 parse): the bm2n blobs are **serialized neural-network graphs for the Hexagon Tensor Processor**, not modem firmware - record tag `0x1337beef` = `TENSOR_MAGIC` from the public `QNN/HTP/core/tensor.h:100`, prologue RTTI name `14ConcreteTensorIN5Tdefs10QuantUint8EE`, `hnnx`-namespaced operator classes, one HTP pickle variant (`0x7309F72B`). The `adsp` in the path is the FastRPC domain id (`ADSP_DOMAIN_ID (0)`, `drivers/misc/fastrpc.c:31`) [F]. The bm3 fleet is the SM8550-generation continuation of the same vendor-tree graph tier; the structural attribution for fuxi's 52 bm3 files rests on md5 identity with that documented tier plus the identical vendor-tree role (rfsa/adsp `.bin` payloads beside QNN/HTP skel libraries) [I - no fuxi bm3 payload is measured in-repo, [OPEN]].
- Filename grammar: `bm3` + `a68`/`a73` + `v08s11` + `nNN`. The `a68`/`a73` fields map to the Hexagon HTP target generations V68/V73 - corroborated by the fuxi vendor tree shipping BOTH `libSnpeHtpV68Skel.so` and `libSnpeHtpV73Skel.so`/`libQnnHtpV73Skel.so` beside the graphs [F for the .so names; the filename-field mapping is [I]]. Nord_4 (SM7550) carries a separate `bm3b68v04s12*`/`bm3b73v04s12*` series (53 files), so the second letter tracks the platform build series, and the version fields differ (v08s11 vs v04s12) [F].
- Corpus scale (sweep, this session): 436 bm3* rows across 10 devices in three shapes - 52 files (Mi_13, Mi_13_Pro, Poco_F6_PRo), 45 files (Edge_40_Pro, OnePlus_11_5G, OnePlus_12R, Xperia_1_V, Xperia_5_V - the 45-file set is fuxi's 52 minus exactly bm3a73 n57-n63), and Nord_4's separate 53-file bm3b series; OnePlus_12 carries 2 bm3 rows. The 8-device share set is exactly the eight SM8550 devices [F].
- The 7-file bm3a73 n57-n63 group (718,752 B each, distinct md5s) is shared only by Mi_13, Mi_13_Pro, Poco_F6_PRo - the three Xiaomi-family 52-file devices - and is absent from the five 45-file devices [F].
- ISA status: `isa_identified` is empty on all 116 rows - honestly un-RE'd at instruction level in the corpus; the bm2n work measured container structure and record framing, not Hexagon instructions, and no bm3 payload has been measured at all. The DSP ISA generation is Hexagon V73 (vendor skel naming + public specs) [F], but no instruction-level fact about any of these 116 blobs is claimed here [N].

## Cross-corpus md5-sharing summary [F]

| share set | files | members |
|---|---|---|
| 30 devices | adspr.jsn, adspua.jsn (identical set) | the 30-device fleet listed above (includes Mi_13) |
| 16 devices | adsps.jsn | Edge_30, Edge_40_Pro, FP5, FP6, Mi_13, Mi_13_Pro, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, Pad_2_Pro, Pad_Pro, Phone_1, Poco_F6_PRo, Redmi_K60_Pro |
| 8 devices (18 md5 identities, incl. the 16-file run) | bm3a68 n52, n53; bm3a73 n02, n03, n04, n06, n07, n08, n09, n12, n13-n27 (one identity), n28, n41-n45, n50, n51 | Mi_13, Mi_13_Pro, Poco_F6_PRo, Edge_40_Pro, OnePlus_11_5G, OnePlus_12R, Xperia_1_V, Xperia_5_V |
| 6 devices | adsp_dtb.b00, adsp_dtb.b01 | Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro, OnePlus_11_5G, Edge_40_Pro |
| 4 devices (14 identities) | adsp.b01, b03, b04, b10, b11, b12, b27, b45, b46, b47, b48, b49, b50, b51 | Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 3 devices (10 identities) | adsp.b06, b07, b15 (with Redmi_K60_Pro); bm3a73 n57-n63 (7, with Poco_F6_PRo) | Mi_13, Mi_13_Pro, Redmi_K60_Pro / Poco_F6_PRo |
| 2 devices (13 identities) | bm3a68 n29, n30, n35-n40, n46-n49 (12); adsp.b26 (`cc20a5d4...`, = Mi_13_Pro's b25 slot) | Mi_13, Mi_13_Pro |
| 1 device (fuxi-exclusive, 41 identities) | adsp.mdt, adsp.b00, b02, b05, b08, b09, b13, b14, b16-b25, b28-b31, b33-b36, b38-b44, b52-b56, b58, adsp_dtb.mdt, adsp_dtb.b02 | Mi_13 |

41 of 101 identities are fuxi-exclusive; the ADSP OS image itself (mdt + most large bNN segments) is a fuxi-specific build, while the metadata shell (jsn trio) is fleet-generic, the HTP graph payloads are SM8550-generation-shared, and one 941,472 B graph payload is copied sixteen times inside fuxi's own vendor tree. (Corpus device label `Poco_F6_PRo` is the database's own spelling; kept as recorded.)

## Sibling contrast - what makes 116 the SM8550 signature [F]

| device | SoC | adsp rows | modem/image | vendor tree | graph fleet | audio resources in family |
|---|---|---|---|---|---|---|
| Mi_12 (cupid) | SM8450 | 46 | 28 | 18 | bm2n00-bm2n11 (12) | hrtf5c + 5 misound (6 rows) |
| Mi_12S_Pro (unicorn) | SM8475 | 67 | 28 | 39 | bm2n00-bm2n27, n32-n36 (33) | hrtf5c + 5 misound (6 rows) |
| **Mi_13 (fuxi)** | **SM8550** | **116** | **64** | **52** | **bm3a68 (14) + bm3a73 (38)** | **none (hrtf5c recategorized `other` at odm/etc/audio)** |

- Row delta over SM8475 = +49: modem/image 28 -> 64 (+31 bNN segments 25 -> 56, +4 `adsp_dtb`, +1 `adsps.jsn`) and vendor tree 39 -> 52 (52 bm3 replacing 33 bm2n + 6 audio rows that leave the family). Byte delta = +182,370,130 B (rfsa +165,764,236, modem/image +16,605,894; python, this session). The SM8550 adsp story is "a 56-segment OS image with a DTB companion, a third servreg manifest, and a much larger HTP graph fleet" [F].
- The graph fleet changes series entirely: bm2n (SM8450/8475) -> bm3a68/bm3a73 (SM8550) - zero md5 overlap between Mi_13's 52 rfsa rows and the bm2n tier, while 41 of Mi_13's 52 rfsa rows are byte-shared across the eight-device SM8550 group [F].
- The b24 gap that defines the Xiaomi 12/12S family (#1168) is gone: every SM8550-generation census carries adsp.b24 [F].
- The segment-index shift (fuxi b26/b27 = nuwa b25/b26) and per-build gap sets (b31/b32, b36/b37) show the SM8550 builds renumber program headers between devices, unlike the byte-stable b45-b51 tier that all four Xiaomi/Redmi SM8550 devices share [F].
- Same-generation cdsp parallel: fuxi's cdsp family censuses 21 rows at `xiaomi/fuxi/modem/image` (split-ELF PIL grammar, cf. unicorn #1180/thor #1198) [F].

## Honest negatives

- No Mi_13 payload was fetched or decoded in this issue: the split-PIL metadata (phdr counts, hash widths, signing chains of fuxi's adsp.mdt and adsp_dtb.mdt) is unverified for SM8550. [OPEN]
- The bm3 structural attribution rests on md5 identity with the measured bm2n fleet plus vendor-tree role; zero fuxi bm3 payload is payload-measured in-repo, and the bm2n container probe (research/laptop/bm2n_container_probe.py) has not been run over bm3 files. The 0x1337beef/HTP record facts are therefore carried, not re-proven, for bm3. [I] [OPEN]
- Which device-tree blobs fuxi's `adsp_dtb` image carries, and whether the 512 KiB `q6_adsp_dtb_mem` reservation is its load target, is consistent-but-unproven. [I] [OPEN]
- The semantics of the third servreg manifest `adsps.jsn` (its subdomain string) are not decoded; only its size (515 B), byte-identity span (16 devices) and public presence on other SoCs are recorded. [OPEN]
- The bNN gap sets (fuxi b32/b37/b57; nuwa b31/b36/b57) and the one-slot index shift are per-build program-header artifacts per [I]; payload-level verification requires the firmware. [OPEN]
- `misound_res_spk_power_game.bin` / `misound_res_spk_power_video.bin` ship in the fuxi vendor tree (LineageOS manifest) but are absent from Mi_13's 700-row census extract; the census scope does not include them. [I]
- linux-firmware WHENCE (fetched 2026-11-21) lists no member of this family for sm8550 (only a740_zap.mbn and two tplg files) and no bm3* anywhere - none of this family is mainlined. [F]
- Inventory/matrix SoC-cell corrections needed (flag for the lead): matrix soc empty on Mi_13/Mi_13_Pro/Poco_F6_PRo/OnePlus_12R; Xperia_1_V and Xperia_5_V carry SM6375 cells but are SM8550-AB devices [F per public specs].

## What would upgrade this finding

1. Payload fetch (fuxi modem partition or a fuxi firmware dump): decode adsp.mdt + adsp_dtb.mdt program headers + metadata segments - the first SM8550 ADSP metadata decode; settles the hash-width question against the SM8250 SHA-384 precedent, explains the b32/b37/b57 skips and the fuxi-vs-nuwa index shift.
2. Run the bm2n container probe (research/laptop/bm2n_container_probe.py) over the bm3 fleet (TheMuppets/AOSPA fuxi trees) - establishes whether the 0xfa0000fa compact container header and HTP record framing extend to bm3; one measurement serves 8 corpus devices (the 16-file run 128 filename slots).
3. Byte-diff fuxi's 513/515/703 B jsn trio against the public servreg samples and record the SM8550-era schema delta including the adsps.jsn subdomain string.
4. Explain the bm3a68/bm3a73 duality (V68-compat vs V73-native graph sets) by correlating graph build-ids with the skel library versions in the fuxi tree.
5. Explain why the five 45-file devices lack bm3a73 n57-n63 while the three 52-file Xiaomi-family devices carry them (build-generation pruning vs QNN release delta).
6. Clarify the OnePlus_12R census shape: its adsp family is 45 vendor-tree rows with zero modem/image rows - a census-scope question for the extract, not a device property [I].

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment. Checks: `Xiaomi 13 codename fuxi SM8550 Snapdragon 8 Gen 2 model 2211133C release date specs` (web, 2026-11-21) -> identity confirmed, codename fuxi, SM8550, 2211133C/G, announced 2022-12-11; `"bm3a73" OR "bm3a68" qualcomm adsp rfsa bin hexagon tensor processor file format` (web, 2026-11-21) -> no public bm3 documentation; `"bm3a73v08s11n14.bin" -repo:adineo-cmd/open-device` (GitHub code search, 2026-11-21) -> 199 hits, all packaging manifests; linux-firmware WHENCE grep `adsps.jsn|adsp_dtb|bm3a|sm8550` (2026-11-21) -> no sm8550 ADSP-family blobs, adsps.jsn/adsp_dtb public on other SoCs; torvalds/linux master sm8550.dtsi (2026-11-21) -> `qcom,sm8550-adsp-pas` + `q6_adsp_dtb_mem` quoted; LineageOS android_device_xiaomi_fuxi proprietary-files.txt (2026-11-21) -> 52/52 bm3 match, stock base OS2.0.213.0.VMCCNXM. Format-level prior art (mainline PAS loader, linux-firmware adsp_dtb/adsps.jsn analogs, public QNN/HTP headers, servreg schema, in-repo bm2n fleet work) is cited, not rebuilt; NO-PRIOR-ART with DELTA posted on the issue.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public device trees, manifests and specs.
