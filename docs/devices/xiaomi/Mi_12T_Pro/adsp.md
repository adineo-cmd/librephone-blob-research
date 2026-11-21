# xiaomi Mi_12T_Pro - `adsp` family status (67 rows - PRESENT, census-complete; two-container grammar: modem-partition split-PIL firmware + vendor-tree Hexagon-TP graph payloads; SM8475-generation signature, native sibling of unicorn)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1204](https://github.com/adineo-cmd/open-device/issues/1204)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, worktree of feat/open-device-site 0fe1ba0), `upstream-contribution/blob-database/device-inventory.csv`, the LineageOS `android_device_xiaomi_diting` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), the `TheMuppets/proprietary_vendor_xiaomi_diting` lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/` directory listing (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (fetched 2026-11-21), a torvalds/linux master probe for `sm8475.dtsi` (2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), public spec pages (2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_12/adsp.md (#1168), docs/devices/xiaomi/Mi_12S_Pro/adsp.md (#1186), docs/devices/xiaomi/Mi_12S/cdsp.md (#1180), and the pre-existing docs/devices/xiaomi/Mi_12T_Pro/leverage-families.md stub. No payloads fetched by this issue; every number is command output or a recorded fetch.

**Verdict: the `adsp` family is PRESENT on Mi_12T_Pro and the census is COMPLETE for both halves - 67 rows, 93,512,536 B, 54 distinct md5s, all db_type=MODEM.** The rows split into two different containers: (a) 28 rows at `xiaomi/diting/modem/image` = the signed split-PIL ADSP firmware image (`adsp.mdt` + `adspr.jsn` + `adspua.jsn` + `adsp.b00..b23` + `adsp.b25`; **no b24**) that the platform loads through TrustZone PAS at boot; (b) 39 rows at `xiaomi/diting/vendor/lib/rfsa/adsp` = Hexagon Tensor Processor (QNN/HTP) serialized neural-network graphs (`bm2n00-bm2n27`, `bm2n32-bm2n36` - note the gap at n28-n31) plus MiSound/HRTF audio-DSP resources, delivered at runtime over FastRPC - **not modem code** despite the MODEM db_type (in-repo fleet finding, cited below). The 39 vendor-tree rows match the LineageOS diting packaging manifest file-for-file and the TheMuppets vendor tree byte-for-size (39/39). There is no structural absence and no census gap. The 67-row shape is the SM8475-generation signature: SM8450 siblings Mi_12 and Mi_12_Pro census 46 adsp rows, the difference is exactly the 21-file bm2n fleet extension (+bm2n12-bm2n27, +bm2n32-bm2n36) in the vendor tree. 47 of the 67 rows are byte-identical to Mi_12S_Pro (unicorn); the 20-row delta is diting's own ADSP OS build plus its speaker-tuning resource.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12T Pro (global model 22081212UG); codename `diting` | `device-inventory.csv` (`build_codename=diting`) [F]; public spec pages and IMEI/device indexes (2026-11-21) [F]. The task briefing guessed "myuser" - that codename does not exist; census paths (`xiaomi/diting/...` on all 819 rows) plus the LineageOS device tree settle diting [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1** (4 nm); Adreno 730; Hexagon V69 DSP | public spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** - supplied here [F]; flag for the lead. Hardware twin of the Redmi K50 Ultra (same SM8475 platform, shared diting tree) [F] |
| released | 2022-10-06 | public spec pages (2026-11-21) [F]. The inventory's released-year cell is also empty - flag for the lead |
| stock base | `OS2.0.203.0.VLFMIXM` | LineageOS diting `proprietary-files.txt` header "All unpinned blobs below are extracted from diting OS2.0.203.0.VLFMIXM" (fetched 2026-11-21) [F] |
| census scope | 819 rows in 9 families (other 403, wifi 179, tz 91, adsp 67, modem 39, boot 14, cdsp 19, gpu 6, bt 1) | coverage-matrix.csv [F]; family sum 819 verified by python this session |
| priority | P3 | coverage-matrix.csv, all 67 adsp rows [F] |

## Census evidence [F]

All 67 adsp rows: `blob_family=adsp`, `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, `db_type=MODEM`, priority P3 (single `uniq -c` line `67 |||n|P3|MODEM`, this session); 54 distinct md5s. The only internal duplication is the 14-file byte-identical run `bm2n14.bin`-`bm2n27.bin` (1,339,032 B, md5 `281755c08b98e757f00586d0052132b1` each) - 67 rows minus 54 md5s = 13 duplicate rows, all of them that run (python, this session).

| group | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp.mdt`, 2 `.jsn`, `adsp.b00..b23` + `b25`) | 28 | 23,316,924 | `xiaomi/diting/modem/image` |
| HTP graph payloads (`bm2n00..bm2n27`, `bm2n32..bm2n36` - no n28-n31) | 33 | 69,941,304 | `xiaomi/diting/vendor/lib/rfsa/adsp` |
| audio resources (`hrtf5c.bin` + 5 `misound_*`) | 6 | 254,308 | `xiaomi/diting/vendor/lib/rfsa/adsp` |
| total | 67 | 93,512,536 | - |

Verified decomposition: 23,310,304 (25 bNN) + 1,216 (2 jsn) + 5,404 (mdt) = 23,316,924; 69,941,304 (33 bm2n) + 164,480 (hrtf5c) + 89,828 (misound x5) = 70,195,612; 23,316,924 + 70,195,612 = 93,512,536 (python, this session). The vendor-tree half is 75.1% of family bytes (bm2n graphs alone 74.8%) - the modem-partition firmware half is the minority by both rows and bytes.

### The 28 modem/image rows (split-PIL ADSP firmware)

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| adsp.mdt | 5,404 | `2055a6be3b7e60eebeb9ec19ee9e202a` | 1 (Mi_12T_Pro only) |
| adspr.jsn | 513 | `5d262bb7661402a8d7ca9724bbb45d46` | 30 |
| adspua.jsn | 703 | `a43d66d0549e33cf421e25be06260ce0` | 30 |
| adsp.b00 | 884 | `a02477359bc6e955ec54342f33250bea` | 1 |
| adsp.b01 | 6,952 | `8f02a28374f5a7b84dcedda178d98eb4` | 7 |
| adsp.b02 | 3,216,484 | `d86f4d3c1edfb9d521d783eab8da196c` | 1 |
| adsp.b03 | 25,720 | `20224bea5dea0a93d65fa290600f1bd6` | 7 |
| adsp.b04 | 34,632 | `a9b1d5b0849cd7d6afa44f08c8ae35ca` | 7 |
| adsp.b05 | 708,136 | `50b33a63694d03c0ae0ec4a25b3658d1` | 1 |
| adsp.b06 | 220 | `4d9e32c4099dc4728f793c93bd5a5c70` | 7 |
| adsp.b07 | 4,892 | `1b0b467af3469850ab16e9e45ef27a11` | 7 |
| adsp.b08 | 2,306,792 | `d903feb1ec2dff062b60c24d4dc30f4a` | 1 |
| adsp.b09 | 237,576 | `5423f414f82b99b91b7419457ef39034` | 1 |
| adsp.b10 | 720 | `1d9f1353d7a4ba2c0c4c65614f27aa27` | 9 |
| adsp.b11 | 9,960 | `47b2c79b0085e361b89dc1d1a91aa236` | 7 |
| adsp.b12 | 131,232 | `576b4827c44eeef88ccad152c8813156` | 1 |
| adsp.b13 | 83,220 | `3da74746b6a35ef62969cd533dd4e433` | 1 |
| adsp.b14 | 3,077,508 | `69aae8c237d3741c9ecb18e638b0cc55` | 1 |
| adsp.b15 | 106,644 | `11c468d6a93134413e58f80e8a714e07` | 1 |
| adsp.b16 | 280 | `0135458a8d93d15e9d9090d785932178` | 1 |
| adsp.b17 | 167,016 | `113cd19bae34ace573a16a10635192aa` | 1 |
| adsp.b18 | 11,434,264 | `d7e29417b0854bf5a296a3a143e31ea1` | 1 |
| adsp.b19 | 503,816 | `61879024742506f2e3a14d2be7498205` | 1 |
| adsp.b20 | 1,936 | `d94caa33b811c2b78cd09da626097870` | 1 |
| adsp.b21 | 201,084 | `18c38edb1b59eaf2fe29e12a82eeacb1` | 2 (Poco_F5_Pro) |
| adsp.b22 | 103,736 | `4e129d9508ac1797dd9c7d1679b710c2` | 1 |
| adsp.b23 | 942,080 | `3f907ea04f5360d947043313c1f8d390` | 1 |
| adsp.b25 | 4,520 | `5b7ee2ff5a1a51da32bb0d49295d834d` | 1 |

The sequence runs b00..b23 then b25 - **adsp.b24 does not occur in the Mi_12T_Pro census**, and this is a whole-family property, not a diting accident: re-verified this session, 39 corpus devices carry `adsp.b24` rows while the 9-device Xiaomi/Nothing group (#1168: Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro) has zero (awk counts, this session). `adsp.mdt` at 5,404 B sits exactly in the SM8475-class size cluster that #1168 recorded, re-verified this session with md5s: five devices at 5,404 B - Mi_12S `efd05d7b...`, Mi_12S_Pro `895d0380...`, Mi_12S_Ultra `19099908...`, Mi_12T_Pro `2055a6be...`, Poco_F5_Pro `3cf6356d...` - five distinct builds of the same size class, distinct from the 5,104 B SM8450 pair (Mi_12, Mi_12_Pro) [F]. Each of the five mdt builds is device-exclusive in the corpus.

### The 39 vendor/lib/rfsa/adsp rows (HTP graphs + audio resources)

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| bm2n00.bin | 1,246,136 | `5e94ea8bf6f3d350d5f62a65c578dcd9` | 9 |
| bm2n01.bin | 1,322,216 | `bf260b9e44a392867fea2746cb4bd215` | 9 |
| bm2n02.bin | 1,508,808 | `a05c4d80ccad64ff5144cc377c9eb9f9` | 9 |
| bm2n03.bin | 570,128 | `6cffe9648942c8aeceb3303898a5c89a` | 9 |
| bm2n04.bin | 768,624 | `68d4dcdf4c7ccfc23c64b452f08bdca0` | 9 |
| bm2n05.bin | 8,337,984 | `15b6df71a304f7ec97f6d281e9b0cfec` | 9 |
| bm2n06.bin | 836,968 | `8f8a96f2647444582a68f50d6dace25a` | 9 |
| bm2n07.bin | 1,339,032 | `580ede38589f3ec421055398b08a0d17` | 7 |
| bm2n08.bin | 3,059,736 | `44e31e18b0c9b35ca3522ba9d2b180fc` | 6 |
| bm2n09.bin | 3,021,464 | `5764742fc0c8cd253ce19c35b48d6297` | 6 |
| bm2n10.bin | 8,339,888 | `0f653ef5d5bae2120a58bb61985b2b47` | 9 |
| bm2n11.bin | 8,337,872 | `ec4792d8abc54b8211fb23138c1a82e8` | 9 |
| bm2n12.bin | 1,638,360 | `b92a2ba4418d76c2132242342789a5e4` | 7 |
| bm2n13.bin | 1,339,032 | `ea1abfc1dcb0cfd5aab2055ccb5bb4a3` | 7 |
| bm2n14.bin .. bm2n27.bin | 1,339,032 each | `281755c08b98e757f00586d0052132b1` (all 14) | 9 (as one identity) |
| bm2n32.bin | 3,079,416 | `91c78db15ac5e67dbd8be5f1ecf17200` | 7 |
| bm2n33.bin | 1,246,536 | `302359d349dc46e6d226cfd24d41599c` | 7 |
| bm2n34.bin | 1,322,808 | `e3acff622e59015e5e9686097b75d33e` | 7 |
| bm2n35.bin | 845,656 | `da95cf0ad73fd13a68cf3d515f79a003` | 7 |
| bm2n36.bin | 3,034,192 | `5ec2559ba25dad28cbea43154ac4e5e3` | 7 |
| hrtf5c.bin | 164,480 | `2a47164eed5282f27ad503a28c7b71a0` | 12 |
| misound_karaokemix_res.bin | 192 | `a9484f0c7da94ce6cdd870d84483b0af` | 8 |
| misound_karaoke_res.bin | 9,752 | `1a43838d29fc032cd37b4dac72a54ba0` | 6 |
| misound_res_headphone.bin | 2,048 | `53fe67652944f4ee760b50e48c7a614e` | 6 |
| misound_res_spk.bin | 6,052 | `df9587250f946c571fc20f746b5ca7a1` | 1 (Mi_12T_Pro only) |
| misound_res_spk4ch.bin | 71,784 | `3799858ef4fd0bd081852ac41d0b53e1` | 8 |

The 14-file run (bm2n14-bm2n27) is 18,746,448 B of literally one payload copied under fourteen filenames (14 x 1,339,032 B, python, this session). Filename is not identity, fleet-content finding F-75 (research/laptop/qualcomm-adsp-bm2n-fleet-content.md): this same byte identity serves the `bm2n07` filename slot on SM8450 trees (cupid/zeus bm2n07 = `281755c0...`, #1168) and the n14-n27 slots on SM8475-generation trees [F]. The diting-exclusive `misound_res_spk.bin` at 6,052 B differs from unicorn's 10,492 B copy (also device-exclusive) - each device's speaker-tuning resource is personalized.

## Census completeness - proven against the LineageOS packaging manifest [F]

- `LineageOS/android_device_xiaomi_diting` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21) lists under `vendor/lib/rfsa/adsp/` exactly the 39 vendor-tree files the census carries (bm2n00-bm2n27, bm2n32-bm2n36 at lines 14-46, hrtf5c at line 47, 5 misound at lines 88-92) - file-for-file match.
- The same manifest contains **zero** `adsp.mdt` / `adsp.bNN` / `adspr.jsn` / `adspua.jsn` entries (grep count 0): LineageOS does not package the split-PIL firmware into the vendor tree; on diting those files live in the device's modem partition, which is where the census's 28 `modem/image` rows come from. This is the Xiaomi/OnePlus packaging pattern recorded in #1168/#1186 (citing docs/devices/samsung/Galaxy_S20_FE/adsp.md #1096 for the Samsung contrast).
- `TheMuppets/proprietary_vendor_xiaomi_diting` @ lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/` (fetched 2026-11-21) holds 80 entries: all 39 census `.bin` files with **byte-exact census sizes (39/39, programmatic comparison, zero mismatches)** plus 41 DSP skel/`.so` libraries. Those `.so` files appear **nowhere in Mi_12T_Pro's 819-row census** - the census's adsp family is the `.bin`/firmware payload view, not the shared-library view.
- The skel library names are direct vendor evidence that the 12T Pro DSP stack targets **Hexagon V69**: `libQnnHtpAltPrepV69Skel.so` (5,443,792 B), `libSnpeHtpV69Skel.so` (6,390,632 B), plus a backward-compat `libSnpeHtpV68Skel.so` (5,196,748 B) and `libVppFrcQnnHtp.so`/`libVppQnnHtp.so` (both 11,901,184 B) - sizes identical to the unicorn tree recorded in #1186, i.e. the same-generation DSP stack [F]. The tree also carries older-ISA compat skels (`libsnpe_dsp_v65/v66/v68_domains_*`) and tracker skels tagged `_8250`/`_8350` [F].
- The manifest's own stock-base header (`OS2.0.203.0.VLFMIXM`) ties the whole vendor-tree set to a specific diting MIUI/HyperOS build [F].
- The pre-existing docs/devices/xiaomi/Mi_12T_Pro/leverage-families.md stub already flagged 6 of these blobs (bm2n06, bm2n08, bm2n12-bm2n15) as leverage blobs with md5s matching this census - consistent, now completed with the full 67-row decomposition [F].

## Container and interface facts

### Split-PIL firmware (the 28 modem/image rows)

- The mdt+bNN form is Qualcomm's signed PIL split container: `adsp.mdt` (5,404 B) is the ELF header/program-header image, the `bNN` files are its loadable segments, and the `.jsn` files are servreg metadata. Mainline Linux parses this format in its Qualcomm peripheral image loader; the in-repo modem-DSP container study (research/fleet/qdsp6sw-container.md, #606) documents the public `QCOM_MDT_RELOCATABLE` p_flags bit in mainline since v4.11 [F].
- Mainline has **no SM8475 device tree at all** (probe of `arch/arm64/boot/dts/qcom/sm8475.dtsi` on torvalds/linux master, 2026-11-21: HTTP 404). The nearest in-tree grammar is `sm8450.dtsi`: `remoteproc_adsp: remoteproc@3000000`, compatible **`qcom,sm8450-adsp-pas`**, `memory-region = <&adsp_mem>` (fetched 2026-11-21, lines 2756-2757). PAS = peripheral authentication service: the kernel hands the signed adsp image to TrustZone for verify-and-boot. The SM8475 platform reuses this PAS mechanism at the same address map (the 8+ Gen 1 is a frequency-bumped SM8450), so the loader grammar carries over [I - platform identity is public; a dedicated sm8475 compatible does not exist in mainline]. Public mainline-porting projects for diting (royka1/diting-ubuntu kernel patches enabling adsp/cdsp remoteproc on `qcom,sm8475-xiaomi-diting` device trees, found via GitHub code search 2026-11-21) confirm the same PAS loader path is what runs this image [F for the patches' existence].
- The two `.jsn` files are servreg (service registry) JSON, publicly shipped by Linux distros beside the mdt/bNN under `lib/firmware/qcom/<soc>/<device>/` (#1168, citing armbian/firmware, batocera-linux, Lakka samples). Mi_12T_Pro's copies (513 B / 703 B, md5s `5d262bb7...`/`a43d66d0...`) are byte-identical across the 30-device fleet set (full member list in the cross-corpus table below, re-verified this session) - SoC-generic text spanning SM8350 through SM8750-class hardware [I]. They are NOT byte-identical to the public SM8250-era distro samples (403 B / 555 B) [F, per #1168].
- `adsp.mdt` is diting-exclusive (share 1). The ADSP OS image itself (mdt + 17 of 25 segments) is a diting-specific build; no other corpus device carries its mdt bytes [F].
- The b24 gap: with b00..b23 + b25 present, the segment table of diting's adsp build skips index 24 [I - per-build program-header indices are the known source of bNN numbering; verifying requires the payload, [OPEN].
- The in-repo signed-PIL metadata decode (research/fleet/pil-metadata-sweep.md) proves the per-phdr hash-slot metadata layout fleet-wide on SM8250 (SHA-384 slots) and SDM845 (SHA-256 slots). No SM8450/SM8475 image has been decoded in-repo; the adsp.mdt phdr count, hash width and cert chains for diting are [OPEN].

### HTP graph payloads (the 33 bm2n rows) - established in-repo findings, not re-derived

- research/laptop/qualcomm-adsp-bm2n-fleet-content.md (measured payloads, 49 fetched, 48/48 parse): the bm2n blobs are **serialized neural-network graphs for the Hexagon Tensor Processor**, not modem firmware - record tag `0x1337beef` = `TENSOR_MAGIC` from the public `QNN/HTP/core/tensor.h:100`, prologue RTTI name `14ConcreteTensorIN5Tdefs10QuantUint8EE`, `hnnx`-namespaced operator classes, one HTP pickle variant (`0x7309F72B`). The `adsp` in the path is the FastRPC domain id (`ADSP_DOMAIN_ID (0)`, `drivers/misc/fastrpc.c:31`), not evidence of modem code [F]. This re-classifies Mi_12T_Pro's db_type=MODEM on all 67 rows as a mislabel for the 39 rfsa rows [I].
- The compact container header is specified at 48/48 files (research/laptop/qualcomm-adsp-bm2n-container-header.md): load base at 0x00 (one of 0x200000/0x400000/0x800000), 7-char ASCII build-id at 0x0c, magic `0xfa0000fa` at 0x14, segment table at 0x24, count-complement terminator. No diting bm2n blob is payload-measured in-repo; all structural attribution for diting rests on md5 identity with measured siblings [F for the method; diting blobs themselves unmeasured].
- The n28-n31 gap mirrors the b24 gap in the firmware half: diting's HTP fleet runs bm2n00-bm2n27 then bm2n32-bm2n36, four filename slots missing in the middle. The LineageOS manifest ships exactly the same 33 files, so the gap is a property of the diting SM8475-generation build, not an extraction accident [F]; whether payloads under other indices absorb the n28-n31 roles is not decodable without the payloads [OPEN]. (Cf. #1168: cupid trees ship bm2n00-bm2n11 only.)
- Corpus scale (#1168, re-verified there): 446 bm2n* rows, 35 devices, 65 distinct filenames bm2n00-bm2n71 [F].
- ISA status: `isa_identified` is empty on all 67 rows - honestly un-RE'd at instruction level in the corpus; the bm2n work measured container structure and record framing, not Hexagon instructions. The DSP ISA generation is Hexagon V69 (QNN/HTP V69 skel naming above + public specs) [F], but no instruction-level fact about any of these 67 blobs is claimed here [N].

## Cross-corpus md5-sharing summary [F]

| share set | files | members |
|---|---|---|
| 30 devices | adspr.jsn, adspua.jsn (identical set) | Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Moto_G200, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, OnePlus_9, OnePlus_9RT, OnePlus_9_Pro, Pad_2_Pro, Pad_Pro, Phone_1, Phone_2, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 12 devices | hrtf5c.bin | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 9 devices | bm2n00-bm2n06, bm2n10, bm2n11, bm2n14-bm2n27 (the 14-file run), adsp.b10 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro |
| 8 devices | misound_karaokemix_res, misound_res_spk4ch | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| 7 devices (set A) | adsp.b01, b03, b04, b06, b07, b11 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro |
| 7 devices (set B) | bm2n07, bm2n12, bm2n13, bm2n32-bm2n36 | Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro |
| 6 devices (set A) | bm2n08, bm2n09, misound_karaoke_res | Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| 6 devices (set B) | misound_res_headphone | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12T_Pro, Poco_F5_Pro |
| 2 devices | adsp.b21 (201,084 B - a different build from the 167,836 B b21 of the Mi_12S group) | Mi_12T_Pro, Poco_F5_Pro |
| 1 device (diting-exclusive, 19 files) | adsp.mdt, adsp.b00, b02, b05, b08, b09, b12, b13, b14, b15, b16, b17, b18, b19, b20, b22, b23, b25, misound_res_spk.bin | Mi_12T_Pro |

19 of 67 files are diting-exclusive; the ADSP OS image itself (mdt + most large bNN segments) is a diting-specific build, while the metadata shell (jsn) is fleet-generic, the HTP/audio payloads are generation-shared, and one 1,339,032 B graph payload is copied fourteen times inside diting's own vendor tree. The b21 pairing is notable: diting's 201,084 B b21 matches Poco_F5_Pro and nothing else - the two late-2022 SM8475 devices outside the Mi 12S sub-family share it, while all five Mi 12S-family members share the 167,836 B build (corpus md5 query, this session). (Corpus device label `Poco_F6_PRo` is the database's own spelling; kept as recorded.)

## Sibling contrast - what makes 67 the SM8475 signature [F]

| device | SoC | adsp rows | modem/image | rfsa | bm2n fleet |
|---|---|---|---|---|---|
| Mi_12 (cupid) | SM8450 | 46 | 28 | 18 | bm2n00-bm2n11 (12) |
| Mi_12_Pro (zeus) | SM8450 | 46 | 28 | 18 | bm2n00-bm2n11 (12) |
| Mi_12S (mayfly) | SM8475 | 67 | 28 | 39 | bm2n00-bm2n27, n32-n36 (33) |
| Mi_12S_Pro (unicorn) | SM8475 | 67 | 28 | 39 | same 33-file fleet |
| Mi_12S_Ultra (thor) | SM8475 | 67 | 28 | 39 | same 33-file fleet |
| **Mi_12T_Pro (diting)** | **SM8475** | **67** | **28** | **39** | **same 33-file fleet** |

- The +21-row delta over SM8450 is exactly `bm2n12`-`bm2n27` (16 files) plus `bm2n32`-`bm2n36` (5 files) - all in the vendor tree, zero delta in the modem/image half (28 rows there on every member, b24 gap included) [F].
- Byte delta vs unicorn: diting 93,512,536 B vs Mi_12S_Pro 93,036,000 B = +476,536 B, of which +480,976 B is the modem/image half (diting's own, larger OS build) and -4,440 B is the vendor tree (`misound_res_spk.bin` 6,052 vs 10,492 B) (python, this session) - the SM8475 adsp story between cousins is a per-device OS build swap over an otherwise identical 33-file HTP fleet [F].
- 47 of Mi_12T_Pro's 67 rows are byte-identical (filename+size+md5) to Mi_12S_Pro's: all 33 bm2n files, hrtf5c, 4 of 5 misound files, and 9 of 28 modem/image rows (both jsn + b01, b03, b04, b06, b07, b10, b11). The 20 differing rows are adsp.mdt + 18 segments (b00, b02, b05, b08, b09, b12, b13, b14, b15, b16, b17, b18, b19, b20, b21, b22, b23, b25) plus `misound_res_spk.bin` - per-device OS builds differ only where the vendor personalized them (speaker tuning and the DSP OS image), exactly as #1168's variant-matrix finding predicted for same-generation devices [F].
- Same-generation cdsp parallel: diting's cdsp family censuses 19 rows, matching the 19-row all-`modem/image` split-ELF PIL grammar documented for mayfly (#1180) and thor (#1198) [F].

## Honest negatives

- No Mi_12T_Pro payload was fetched or decoded in this issue: the split-PIL metadata (phdr count, hash width, signing chains of diting's adsp.mdt) is unverified for SM8475; the bm2n structural facts are carried from the in-repo measured fleet work, identity resting on md5 equality. [OPEN]
- Whether diting's modem partition physically contains an `adsp.b24` (or the build's ELF simply has no segment 24) is not decodable from the census alone. [OPEN]
- The role of filename slots bm2n28-bm2n31 in the SM8475-generation fleet (absent from both the census and the LineageOS manifest) is unknown; no corpus device carries them. [OPEN]
- The function of each misound_* and hrtf5c resource is inferred from vendor naming (MiSound audio tuning / head-related transfer function) and their tiny sizes, not payload-verified. [I]
- The 41 DSP skel `.so` libraries in the vendor tree are outside the census; their absence from the 819-row extract is recorded, not explained (the upstream devices.sql enumeration did not include them). [I]
- The exact byte content of diting's 513/703 B jsn files is not diffed against the public servreg samples (sizes differ from the SM8250 copies). [OPEN]
- linux-firmware WHENCE (fetched 2026-11-21) lists none of bm2n*/misound_*/hrtf5c for any device, and adspr.jsn/adspua.jsn only for other SoCs (apq8096, qcm2290, qcm6490, qcs615, qcs6490 variants, qrb4210, sdm845, sm8250, sc8280xp, x1e80100, glymur, hawi, kaanapali, maili, sa8775p/qcs8300, nord) - there is no diting/waipio/sm8450/sm8475 adsp entry at all: none of this family is mainlined. [F]
- Redmi K50 Ultra (the 12T Pro's hardware twin) is not a separate corpus device under another name as far as the census shows; if the lab ever ingests it, its adsp build may be byte-identical to diting's exclusive half. [I]

## What would upgrade this finding

1. Payload fetch (diting modem partition or a diting firmware dump): decode adsp.mdt program headers + metadata segment - the second SM8475 ADSP metadata decode after unicorn, and the first that can also settle whether the five 5,404 B mdt builds share a program-header table with different section payloads.
2. Run the bm2n container probe (research/laptop/bm2n_container_probe.py) over the TheMuppets diting-tree bm2n files - zero of 33 are payload-measured; the 14-fold copy under n14-n27 makes one measurement serve 14 filename slots on this device.
3. Byte-diff diting's 513/703 B jsn files against the public servreg samples and record the SM8450/SM8475-era schema delta.
4. Explain the bm2n28-bm2n31 absence (build-generation pruning vs index remapping into n32-n36) using a second SM8475 device outside the Xiaomi family (Poco_F5_Pro, Phone_2 censuses both carry the same fleet - check their LineageOS manifests).
5. Explain the b21 split: diting + Poco_F5_Pro carry a 201,084 B b21 that no Mi 12S-family member has - a dated-feature segment whose identity requires the payload.
6. Extend the variant matrix's per-md5 leverage tables with the 9-device bm2n share group confirmed here (one RE pass on `5e94ea8b...` or `281755c0...` genuinely serves 9 corpus devices; the latter 14 times over on diting alone).

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment. Checks: `Xiaomi 12T Pro codename diting 22081212UG Snapdragon 8+ Gen 1 SM8475` (web, 2026-11-21) -> identity confirmed, diting settles it (devcheck.app/devices/xiaomi/diting, doc.e.foundation/devices/diting, Xiaomi-SM8475-Development/android_device_xiaomi_diting); `"Xiaomi 12T Pro" OR "diting" adsp firmware hexagon dsp reverse engineering analysis` (web, 2026-11-21) -> no device-specific analysis; GitHub code search `"bm2n14.bin" diting adsp -repo:adineo-cmd/open-device` (2026-11-21, adineo-cmd/* excluded) -> 27 hits, all packaging manifests (LineageOS/android_device_xiaomi_diting and forks, Klozz/xiaomi_diting_dump, beet-stuffs/vendor_xiaomi_diting); GitHub code search `"adsp.mdt" diting -repo:adineo-cmd/open-device` (2026-11-21) -> 63 hits, mostly unrelated build scripts, the only substantive item is royka1/diting-ubuntu mainline-port DTS patches (remoteproc enablement, not format RE); linux-firmware WHENCE (2026-11-21) -> no member of this family for this platform; torvalds/linux master sm8475.dtsi probe (2026-11-21) -> 404, no SM8475 device tree. Format-level prior art (mainline PIL loader, public QNN/HTP headers, servreg schema) is cited, not rebuilt; DELTA posted on the issue.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public device trees, manifests and specs.
