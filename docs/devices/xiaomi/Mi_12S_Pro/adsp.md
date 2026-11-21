# xiaomi Mi_12S_Pro - `adsp` family status (67 rows - PRESENT, census-complete; two-container grammar: modem-partition split-PIL firmware + vendor-tree Hexagon-TP graph payloads; SM8475-generation signature)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1186](https://github.com/adineo-cmd/open-device/issues/1186)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 937686f), `upstream-contribution/blob-database/device-inventory.csv`, the LineageOS `android_device_xiaomi_unicorn` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), the `TheMuppets/proprietary_vendor_xiaomi_unicorn` lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/` directory listing (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (fetched 2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), public spec pages (2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_12/adsp.md (#1168), docs/devices/xiaomi/Mi_12S/cdsp.md (#1180), docs/devices/xiaomi/Mi_12S_Ultra/cdsp.md (#1198). No payloads fetched by this issue; every number is command output or a recorded fetch.

**Verdict: the `adsp` family is PRESENT on Mi_12S_Pro and the census is COMPLETE for both halves - 67 rows, 93,036,000 B, 54 distinct md5s, all db_type=MODEM.** The rows split into two different containers: (a) 28 rows at `xiaomi/unicorn/modem/image` = the signed split-PIL ADSP firmware image (`adsp.mdt` + `adspr.jsn` + `adspua.jsn` + `adsp.b00..b23` + `adsp.b25`; **no b24**) that the platform loads through TrustZone PAS at boot; (b) 39 rows at `xiaomi/unicorn/vendor/lib/rfsa/adsp` = Hexagon Tensor Processor (QNN/HTP) serialized neural-network graphs (`bm2n00-bm2n27`, `bm2n32-bm2n36` - note the gap at n28-n31) plus MiSound/HRTF audio-DSP resources, delivered at runtime over FastRPC - **not modem code** despite the MODEM db_type (in-repo fleet finding, cited below). The 39 vendor-tree rows match the LineageOS unicorn packaging manifest file-for-file and the TheMuppets vendor tree byte-for-size (39/39). There is no structural absence and no census gap. The 67-row shape is the SM8475-generation signature: SM8450 siblings Mi_12 and Mi_12_Pro census 46 adsp rows, the difference is exactly the 21-file bm2n fleet extension (+bm2n12-bm2n27, +bm2n32-bm2n36) in the vendor tree.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12S Pro (China, model 2206122SC); codename `unicorn` | `device-inventory.csv` (`build_codename=unicorn`) [F]; public spec pages and /e/OS device index (2026-11-21) [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1**; Adreno 730; Hexagon V69 DSP | public spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** - supplied here [F]; flag for the lead. Note: the task briefing guessed codename "zeus"; `zeus` is Xiaomi 12 **Pro** (SM8450) - the census paths (`xiaomi/unicorn/...` on all 840 Mi_12S_Pro rows, `xiaomi/zeus/...` on all Mi_12_Pro rows) plus public sources settle unicorn [F] |
| released | July 2022 (announced 2022-07-04) | public spec pages (2026-11-21) [F] |
| stock base | `OS2.0.205.0.VLECNXM` | LineageOS unicorn `proprietary-files.txt` header "All unpinned blobs below are extracted from unicorn OS2.0.205.0.VLECNXM" (fetched 2026-11-21) [F] |
| census scope | 840 rows in 9 families (other 424, wifi 179, tz 91, modem 39, adsp 67, cdsp 19, boot 14, gpu 6, bt 1) | coverage-matrix.csv [F] |
| priority | P3 | coverage-matrix.csv, all 67 adsp rows [F] |

## Census evidence [F]

All 67 adsp rows: `blob_family=adsp`, `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, `db_type=MODEM`, priority P3; 54 distinct md5s. The only internal duplication is the 14-file byte-identical run `bm2n14.bin`-`bm2n27.bin` (1,339,032 B, md5 `281755c08b98e757f00586d0052132b1` each) - 67 rows minus 54 md5s = 13 duplicate rows, all of them that run (python, this session).

| group | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp.mdt`, 2 `.jsn`, `adsp.b00..b23` + `b25`) | 28 | 22,835,948 | `xiaomi/unicorn/modem/image` |
| HTP graph payloads (`bm2n00..bm2n27`, `bm2n32..bm2n36` - no n28-n31) | 33 | 69,941,304 | `xiaomi/unicorn/vendor/lib/rfsa/adsp` |
| audio resources (`hrtf5c.bin` + 5 `misound_*`) | 6 | 258,748 | `xiaomi/unicorn/vendor/lib/rfsa/adsp` |
| total | 67 | 93,036,000 | - |

Verified decomposition: 22,829,328 (25 bNN) + 1,216 (2 jsn) + 5,404 (mdt) = 22,835,948; 69,941,304 (33 bm2n) + 164,480 (hrtf5c) + 94,268 (misound x5) = 70,200,052; 22,835,948 + 70,200,052 = 93,036,000 (python, this session). The vendor-tree half is 75.5% of family bytes (bm2n graphs alone 75.2%) - the modem-partition firmware half is the minority by both rows and bytes.

### The 28 modem/image rows (split-PIL ADSP firmware)

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| adsp.mdt | 5,404 | `895d0380cad8d5ca4832413a1aa21727` | 1 (Mi_12S_Pro only) |
| adspr.jsn | 513 | `5d262bb7661402a8d7ca9724bbb45d46` | 30 |
| adspua.jsn | 703 | `a43d66d0549e33cf421e25be06260ce0` | 30 |
| adsp.b00 | 884 | `e05678b1789fccf3319718ef4bfcd92e` | 1 |
| adsp.b01 | 6,952 | `8f02a28374f5a7b84dcedda178d98eb4` | 7 |
| adsp.b02 | 3,216,484 | `075c55727f50c96ba6dbc864ed4ed5b7` | 1 |
| adsp.b03 | 25,720 | `20224bea5dea0a93d65fa290600f1bd6` | 7 |
| adsp.b04 | 34,632 | `a9b1d5b0849cd7d6afa44f08c8ae35ca` | 7 |
| adsp.b05 | 656,536 | `24c0441e4eeede6278533d30761cb652` | 1 |
| adsp.b06 | 220 | `4d9e32c4099dc4728f793c93bd5a5c70` | 7 |
| adsp.b07 | 4,892 | `1b0b467af3469850ab16e9e45ef27a11` | 7 |
| adsp.b08 | 2,306,792 | `a946c0d54846a5af5dc22b65d93ab6e0` | 1 |
| adsp.b09 | 237,576 | `6158e37ceca6f9327c71648249046533` | 1 |
| adsp.b10 | 720 | `1d9f1353d7a4ba2c0c4c65614f27aa27` | 9 |
| adsp.b11 | 9,960 | `47b2c79b0085e361b89dc1d1a91aa236` | 7 |
| adsp.b12 | 131,232 | `9e6f68c81d47c9b09c26c552577d4a16` | 2 (Mi_12S_Ultra) |
| adsp.b13 | 83,220 | `cfe9bef8549be26bf3fa2a5af6f7ed10` | 1 |
| adsp.b14 | 3,063,172 | `21b499491f769b77491eb15ea7a10dd0` | 1 |
| adsp.b15 | 106,396 | `9464906469b0d867f774b0eb5beb2ecf` | 1 |
| adsp.b16 | 280 | `7537c6cf6c8234a09f3db4a23db8f525` | 1 |
| adsp.b17 | 165,252 | `3b46d3943d370dd7bb7646daa9968447` | 1 |
| adsp.b18 | 11,437,528 | `5225dd83183548bdf2f040a60e793f9f` | 1 |
| adsp.b19 | 503,816 | `e0a4046ee981971606da4f6dab57077b` | 1 |
| adsp.b20 | 1,936 | `93a729776cc94333ea5160e1f7578278` | 2 (Mi_12S) |
| adsp.b21 | 167,836 | `5d26e9206e06c3c086c08415eed00907` | 5 |
| adsp.b22 | 52,376 | `424ff9dde1fc540bde01dbc65a5b85f0` | 2 (Mi_12S) |
| adsp.b23 | 610,396 | `d66b76fe8f0f363a1b7f2765a8095dc4` | 1 |
| adsp.b25 | 4,520 | `ab2de96d7d1a251b2f14f64b6db19fa0` | 1 |

The sequence runs b00..b23 then b25 - **adsp.b24 does not occur in the Mi_12S_Pro census**. This is the whole-family property recorded in docs/devices/xiaomi/Mi_12/adsp.md (#1168): the 9-device Xiaomi/Nothing group (Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro) has zero b24 rows, while 39 other corpus devices carry `adsp.b24`. `adsp.mdt` at 5,404 B sits exactly in the SM8475-class cluster that #1168 recorded (Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro - re-verified this session), distinct from the 5,104 B SM8450 pair (Mi_12, Mi_12_Pro) and the 8,524 B SM8550-class five (Mi_13, Mi_13_Pro, OnePlus_11_5G, Poco_F6_PRo, Redmi_K60_Pro) [F]. (The sibling #1168 doc says "four" for the 8,524 B set; the corpus shows five members including OnePlus_11_5G - flag for the lead.)

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
| misound_res_spk.bin | 10,492 | `9d0874793cad0bd8302fa01ae17db193` | 1 |
| misound_res_spk4ch.bin | 71,784 | `3799858ef4fd0bd081852ac41d0b53e1` | 8 |

The 14-file run (bm2n14-bm2n27) is 18,746,448 B of literally one payload copied under fourteen filenames (14 x 1,339,032 B, python, this session). Filename is not identity, fleet-content finding F-75 (research/laptop/qualcomm-adsp-bm2n-fleet-content.md): this same byte identity serves the `bm2n07` filename slot on SM8450 trees (cupid/zeus bm2n07 = `281755c0...`, #1168) and the n14-n27 slots on SM8475-generation trees [F].

## Census completeness - proven against the LineageOS packaging manifest [F]

- `LineageOS/android_device_xiaomi_unicorn` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21) lists under `vendor/lib/rfsa/adsp/` exactly the 39 vendor-tree files the census carries (bm2n00-bm2n27, bm2n32-bm2n36, hrtf5c, 5 misound) - file-for-file match, lines 14-47 and 91-95 of the manifest.
- The same manifest contains **zero** `adsp.mdt` / `adsp.bNN` / `adspr.jsn` / `adspua.jsn` entries (grep count 0): LineageOS does not package the split-PIL firmware into the vendor tree; on unicorn those files live in the device's modem partition, which is where the census's 28 `modem/image` rows come from. This is the Xiaomi/OnePlus packaging pattern recorded in #1168 (citing docs/devices/samsung/Galaxy_S20_FE/adsp.md #1096 for the Samsung contrast: Samsung integrates DSP firmware inside its modem image; Xiaomi ships it as modem-partition split files).
- `TheMuppets/proprietary_vendor_xiaomi_unicorn` @ lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/` (fetched 2026-11-21) holds 82 entries: all 39 census `.bin` files with **byte-exact census sizes (39/39, programmatic comparison, zero mismatches)** plus 43 DSP skel `.so` libraries. Those `.so` files appear **nowhere in Mi_12S_Pro's 840-row census** - the census's adsp family is the `.bin`/firmware payload view, not the shared-library view.
- The skel library names are direct vendor evidence that the Mi 12S Pro DSP stack targets **Hexagon V69**: `libQnnHtpAltPrepV69Skel.so` (5,443,792 B), `libSnpeHtpV69Skel.so` (6,390,632 B), plus a backward-compat `libSnpeHtpV68Skel.so` (5,196,748 B) and `libVppFrcQnnHtp.so`/`libVppQnnHtp.so` (both 11,901,184 B) [F].
- The manifest's own stock-base header (`OS2.0.205.0.VLECNXM`) ties the whole vendor-tree set to a specific unicorn MIUI/HyperOS build [F].

## Container and interface facts

### Split-PIL firmware (the 28 modem/image rows)

- The mdt+bNN form is Qualcomm's signed PIL split container: `adsp.mdt` (5,404 B) is the ELF header/program-header image, the `bNN` files are its loadable segments, and the `.jsn` files are servreg metadata. Mainline Linux parses this format in its Qualcomm peripheral image loader; the in-repo modem-DSP container study (research/fleet/qdsp6sw-container.md, #606) documents the public `QCOM_MDT_RELOCATABLE` p_flags bit in mainline since v4.11 [F].
- Mainline has **no SM8475 device tree at all** (probes of `arch/arm64/boot/dts/qcom/sm8475*.dts*` on torvalds/linux master, 2026-11-21: 404). The nearest in-tree grammar is `sm8450.dtsi`: `remoteproc_adsp: remoteproc@3000000`, compatible **`qcom,sm8450-adsp-pas`**, `memory-region = <&adsp_mem>` (fetched 2026-11-21, lines 2756-2775). PAS = peripheral authentication service: the kernel hands the signed adsp image to TrustZone for verify-and-boot. The SM8475 platform reuses this PAS mechanism at the same address map (the 8+ Gen 1 is a frequency-bumped SM8450), so the loader grammar carries over [I - platform identity is public; a dedicated sm8475 compatible does not exist in mainline].
- The two `.jsn` files are servreg (service registry) JSON, publicly shipped by Linux distros beside the mdt/bNN under `lib/firmware/qcom/<soc>/<device>/` (#1168, citing armbian/firmware, batocera-linux, Lakka samples). Mi_12S_Pro's copies (513 B / 703 B, md5s `5d262bb7...`/`a43d66d0...`) are byte-identical across the 30-device fleet set that #1168 recorded - re-verified this session, members: Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Moto_G200, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, OnePlus_9, OnePlus_9_Pro, OnePlus_9RT, Pad_2_Pro, Pad_Pro, Phone_1, Phone_2, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro. SoC-generic text spanning SM8350 through SM8750-class hardware [I]. They are NOT byte-identical to the public SM8250-era distro samples (403 B / 555 B) [F].
- `adsp.mdt` is unicorn-exclusive (share 1). The ADSP OS image itself (mdt + 16 of 25 segments) is a unicorn-specific build; no other corpus device carries its mdt bytes [F].
- The b24 gap: with b00..b23 + b25 present, the segment table of unicorn's adsp build skips index 24 [I - per-build program-header indices are the known source of bNN numbering; verifying requires the payload, [OPEN].
- The in-repo signed-PIL metadata decode (research/fleet/pil-metadata-sweep.md) proves the per-phdr hash-slot metadata layout fleet-wide on SM8250 (SHA-384 slots) and SDM845 (SHA-256 slots). No SM8450/SM8475 image has been decoded in-repo; the adsp.mdt phdr count, hash width and cert chains for unicorn are [OPEN].

### HTP graph payloads (the 33 bm2n rows) - established in-repo findings, not re-derived

- research/laptop/qualcomm-adsp-bm2n-fleet-content.md (measured payloads, 49 fetched, 48/48 parse): the bm2n blobs are **serialized neural-network graphs for the Hexagon Tensor Processor**, not modem firmware - record tag `0x1337beef` = `TENSOR_MAGIC` from the public `QNN/HTP/core/tensor.h:100`, prologue RTTI name `14ConcreteTensorIN5Tdefs10QuantUint8EE`, `hnnx`-namespaced operator classes, one HTP pickle variant (`0x7309F72B`). The `adsp` in the path is the FastRPC domain id (`ADSP_DOMAIN_ID (0)`, `drivers/misc/fastrpc.c:31`), not evidence of modem code [F]. This re-classifies Mi_12S_Pro's db_type=MODEM on all 67 rows as a mislabel for the 39 rfsa rows [I].
- The compact container header is specified at 48/48 files (research/laptop/qualcomm-adsp-bm2n-container-header.md): load base at 0x00 (one of 0x200000/0x400000/0x800000), 7-char ASCII build-id at 0x0c, magic `0xfa0000fa` at 0x14, segment table at 0x24, count-complement terminator. No unicorn bm2n blob is payload-measured in-repo; all structural attribution for unicorn rests on md5 identity with measured siblings [F for the method; unicorn blobs themselves unmeasured].
- The n28-n31 gap mirrors the b24 gap in the firmware half: unicorn's HTP fleet runs bm2n00-bm2n27 then bm2n32-bm2n36, four filename slots missing in the middle. The LineageOS manifest ships exactly the same 33 files, so the gap is a property of the unicorn SM8475-generation build, not an extraction accident [F]; whether payloads under other indices absorb the n28-n31 roles is not decodable without the payloads [OPEN]. (Cf. #1168: cupid trees ship bm2n00-bm2n11 only.)
- Corpus scale (#1168, re-verified there): 446 bm2n* rows, 35 devices, 65 distinct filenames bm2n00-bm2n71 [F].
- ISA status: `isa_identified` is empty on all 67 rows - honestly un-RE'd at instruction level in the corpus; the bm2n work measured container structure and record framing, not Hexagon instructions. The DSP ISA generation is Hexagon V69 (QNN library naming above + public specs) [F], but no instruction-level fact about any of these 67 blobs is claimed here [N].

## Cross-corpus md5-sharing summary [F]

| share set | files | members |
|---|---|---|
| 30 devices | adspr.jsn, adspua.jsn (identical set) | the 30-device fleet listed above (includes Mi_12S_Pro) |
| 12 devices | hrtf5c.bin | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 9 devices | bm2n00-bm2n06, bm2n10, bm2n11, bm2n14-bm2n27 (the 14-file run), adsp.b10 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro |
| 8 devices | misound_karaokemix_res, misound_res_spk4ch | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| 7 devices (set A) | adsp.b01, b03, b04, b06, b07, b11 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro |
| 7 devices (set B) | bm2n07, bm2n12, bm2n13, bm2n32-bm2n36 | Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro |
| 6 devices (set A) | bm2n08, bm2n09, misound_karaoke_res | Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5, Poco_F5_Pro |
| 6 devices (set B) | misound_res_headphone | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12T_Pro, Poco_F5_Pro |
| 5 devices | adsp.b21 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra |
| 2 devices | adsp.b12 | Mi_12S_Pro, Mi_12S_Ultra |
| 2 devices | adsp.b20, b22 | Mi_12S, Mi_12S_Pro |
| 1 device (unicorn-exclusive, 16 files) | adsp.mdt, adsp.b00, b02, b05, b08, b09, b13, b14, b15, b16, b17, b18, b19, b23, b25, misound_res_spk.bin | Mi_12S_Pro |

16 of 67 files are unicorn-exclusive; the ADSP OS image itself (mdt + most large bNN segments) is a unicorn-specific build, while the metadata shell (jsn) is fleet-generic, the HTP/audio payloads are generation-shared, and one 1,339,032 B graph payload is copied fourteen times inside unicorn's own vendor tree. (Corpus device label `Poco_F6_PRo` is the database's own spelling; kept as recorded.)

## Sibling contrast - what makes 67 the SM8475 signature [F]

| device | SoC | adsp rows | modem/image | rfsa | bm2n fleet |
|---|---|---|---|---|---|
| Mi_12 (cupid) | SM8450 | 46 | 28 | 18 | bm2n00-bm2n11 (12) |
| Mi_12_Pro (zeus) | SM8450 | 46 | 28 | 18 | bm2n00-bm2n11 (12) |
| **Mi_12S_Pro (unicorn)** | **SM8475** | **67** | **28** | **39** | **bm2n00-bm2n27, n32-n36 (33)** |
| Mi_12S (mayfly) | SM8475 | 67 | 28 | 39 | same 33-file fleet |
| Mi_12S_Ultra (thor) | SM8475 | 67 | 28 | 39 | same 33-file fleet |

- The +21-row delta over SM8450 is exactly `bm2n12`-`bm2n27` (16 files) plus `bm2n32`-`bm2n36` (5 files) - all in the vendor tree, zero delta in the modem/image half (28 rows there on every member, b24 gap included) [F].
- Byte delta: unicorn 93,036,000 B vs Mi_12 61,867,160 B = +31,168,840 B, of which +31,247,852 B is the vendor tree (rfsa) and -79,012 B is the modem/image half - the SM8475 adsp story is entirely "more HTP graphs", not a different firmware structure (python, this session) [F].
- 50 of Mi_12S_Pro's 67 rows are byte-identical (filename+size+md5) to Mi_12S's: all 33 bm2n files, hrtf5c, and 4 of 5 misound files. The 17 differing rows are the modem/image build (adsp.mdt + 15 segments: b00, b02, b05, b08, b09, b12-b19, b23, b25) plus `misound_res_spk.bin` - per-device OS builds differ only where the vendor personalized them (speaker tuning and the DSP OS image), exactly as #1168's variant-matrix finding predicted for same-generation devices [F].
- Same-generation cdsp parallel: unicorn's cdsp family censuses 19 rows, all at `xiaomi/unicorn/modem/image` - the same split-ELF PIL grammar documented for mayfly (#1180) and thor (#1198) [F].

## Honest negatives

- No Mi_12S_Pro payload was fetched or decoded in this issue: the split-PIL metadata (phdr count, hash width, signing chains of unicorn's adsp.mdt) is unverified for SM8475; the bm2n structural facts are carried from the in-repo measured fleet work, identity resting on md5 equality. [OPEN]
- Whether unicorn's modem partition physically contains an `adsp.b24` (or the build's ELF simply has no segment 24) is not decodable from the census alone. [OPEN]
- The role of filename slots bm2n28-bm2n31 in the SM8475-generation fleet (absent from both the census and the LineageOS manifest) is unknown; no corpus device carries them. [OPEN]
- The function of each misound_* and hrtf5c resource is inferred from vendor naming (MiSound audio tuning / head-related transfer function) and their tiny sizes, not payload-verified. [I]
- The 43 DSP skel `.so` libraries in the vendor tree are outside the census; their absence from the 840-row extract is recorded, not explained (the upstream devices.sql enumeration did not include them). [I]
- The exact byte content of unicorn's adspr.jsn/adspua.jsn is not diffed against the public servreg samples (sizes differ from the SM8250 copies). [OPEN]
- linux-firmware WHENCE (fetched 2026-11-21) lists none of bm2n/misound/hrtf5c/adspr.jsn/adspua.jsn/adsp.mdt for this platform - none of this family is mainlined; the 24 WHENCE adspr.jsn entries belong to other SoCs (apq8096, qcm2290, qcm6490, qcs615, qrb4210 and friends). [F]

## What would upgrade this finding

1. Payload fetch (unicorn modem partition or a unicorn firmware dump): decode adsp.mdt program headers + metadata segment - the first SM8475 ADSP metadata decode; settles the hash-width question against the SM8250 SHA-384 precedent and explains the b24 skip.
2. Run the bm2n container probe (research/laptop/bm2n_container_probe.py) over the TheMuppets unicorn-tree bm2n files - zero of 33 are payload-measured; the 14-fold copy under n14-n27 makes one measurement serve 14 filename slots on this device.
3. Byte-diff unicorn's 513/703 B jsn files against the public servreg samples and record the SM8450/SM8475-era schema delta.
4. Explain the bm2n28-bm2n31 absence (build-generation pruning vs index remapping into n32-n36) using a second SM8475 device outside the Xiaomi family (Poco_F5_Pro, Phone_2 censuses both carry the same fleet - check their LineageOS manifests).
5. Extend the variant matrix's per-md5 leverage tables with the 9-device bm2n share group confirmed here (one RE pass on `5e94ea8b...` or `281755c0...` genuinely serves 9 corpus devices; the latter 14 times over on unicorn alone).

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment. Checks: `Xiaomi 12S Pro codename unicorn SM8475 Snapdragon 8+ Gen 1 model 2206122SC` (web, 2026-11-21) -> identity confirmed; `"bm2n" bin qualcomm adsp vendor/lib/rfsa reverse engineering format documentation` (web, 2026-11-21) -> no public bm2n documentation; `"Xiaomi 12S Pro" unicorn adsp firmware hexagon dsp analysis` (web, 2026-11-21) -> no device-specific analysis; GitHub code search `"bm2n14.bin" unicorn adsp -repo:adineo-cmd/open-device` (2026-11-21, adineo-cmd/* excluded) -> 13 hits, all packaging manifests; linux-firmware WHENCE (2026-11-21) -> no member of this family for this platform; torvalds/linux master sm8475 dts probes (2026-11-21) -> 404, no SM8475 device tree. Format-level prior art (mainline PIL loader, public QNN/HTP headers, servreg schema) is cited, not rebuilt; NO-PRIOR-ART with DELTA posted on the issue.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public device trees, manifests and specs.
