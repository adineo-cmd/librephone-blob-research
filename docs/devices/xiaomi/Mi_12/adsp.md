# xiaomi Mi_12 - `adsp` family status (46 rows - PRESENT, census-complete; two-container grammar: modem-partition split-PIL firmware + vendor-tree Hexagon-TP graph payloads)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1168](https://github.com/adineo-cmd/open-device/issues/1168)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site a7b7b0e), `upstream-contribution/blob-database/device-inventory.csv`, the LineageOS `android_device_xiaomi_cupid` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), the `TheMuppets/proprietary_vendor_xiaomi_cupid` lineage-22.2 tree listing (fetched 2026-11-21), `TheMuppets/proprietary_vendor_xiaomi_sm8450-common` lineage-22.2 firmware listing (fetched 2026-11-21), armbian/firmware servreg JSON samples (fetched 2026-11-21), mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (fetched 2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), public spec pages (2026-11-21). No payloads fetched by this issue; every number is command output or a recorded fetch.

**Verdict: the `adsp` family is PRESENT on Mi_12 and the census is COMPLETE for both halves - 46 rows, 61,867,160 B, 46 distinct md5s, all db_type=MODEM.** The rows split into two different containers: (a) 28 rows at `xiaomi/cupid/modem/image` = the signed split-PIL ADSP firmware image (`adsp.mdt` + `adspr.jsn` + `adspua.jsn` + `adsp.b00..b23` + `adsp.b25`; **no b24**) that the SM8450 platform loads through TrustZone PAS at boot; (b) 18 rows at `xiaomi/cupid/vendor/lib/rfsa/adsp` = Hexagon Tensor Processor (QNN/HTP) serialized neural-network graphs (`bm2n00-bm2n11`) plus MiSound/HRTF audio-DSP resources, delivered at runtime over FastRPC - **not modem code** despite the MODEM db_type (in-repo fleet finding, cited below). The 18 vendor-tree rows match the LineageOS cupid packaging manifest file-for-file and byte-for-size. There is no structural absence and no census gap.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi 12 (China, model 2201123C); codename `cupid` | `device-inventory.csv` (`build_codename=cupid`) [F]; public spec pages (2026-11-21) [F] |
| SoC | Qualcomm **SM8450 Snapdragon 8 Gen 1**; Adreno 730; Hexagon V69 DSP | public spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** - supplied here [F]; flag for the lead |
| stock base | `OS2.0.202.0.VLCMIXM` | LineageOS cupid `proprietary-files.txt` header "All unpinned blobs below are extracted from cupid OS2.0.202.0.VLCMIXM" (fetched 2026-11-21) [F] |
| census scope | 783 rows in 9 families (other 391, wifi 176, tz 91, modem 39, adsp 46, cdsp 19, boot 14, gpu 6, bt 1); 967,886,162 B | coverage-matrix.csv + device-inventory.csv [F] |
| priority | P3 | coverage-matrix.csv, all 46 adsp rows [F] |

## Census evidence [F]

All 46 adsp rows: `blob_family=adsp`, `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, `db_type=MODEM`, priority P3; 46 distinct md5s (no internal duplication).

| group | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp.mdt`, 2 `.jsn`, `adsp.b00..b23` + `b25`) | 28 | 22,914,960 | `xiaomi/cupid/modem/image` |
| HTP graph payloads (`bm2n00..bm2n11`) | 12 | 38,688,856 | `xiaomi/cupid/vendor/lib/rfsa/adsp` |
| audio resources (`hrtf5c.bin` + 5 `misound_*`) | 6 | 263,344 | `xiaomi/cupid/vendor/lib/rfsa/adsp` |
| total | 46 | 61,867,160 | - |

Verified decomposition: 22,908,640 (25 bNN) + 1,216 (2 jsn) + 5,104 (mdt) = 22,914,960; 38,688,856 + 164,480 (hrtf5c) + 98,864 (misound x5) = 38,952,200; 38,952,200 + 22,914,960 = 61,867,160 (python, this session).

### The 28 modem/image rows (split-PIL ADSP firmware)

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| adsp.mdt | 5,104 | `5313ce7b148c3ba058d6301ddc5e6066` | 1 (Mi_12 only) |
| adspr.jsn | 513 | `5d262bb7661402a8d7ca9724bbb45d46` | 30 |
| adspua.jsn | 703 | `a43d66d0549e33cf421e25be06260ce0` | 30 |
| adsp.b00 | 884 | `02b55a5d66f5f00996d23e0c8aa853e0` | 1 |
| adsp.b01 | 6,952 | `8f02a28374f5a7b84dcedda178d98eb4` | 7 |
| adsp.b02 | 3,216,484 | `ab2613c219da2ec3c23e07ea75bda087` | 1 |
| adsp.b03 | 25,720 | `20224bea5dea0a93d65fa290600f1bd6` | 7 |
| adsp.b04 | 34,632 | `a9b1d5b0849cd7d6afa44f08c8ae35ca` | 7 |
| adsp.b05 | 657,480 | `08130341f3ffee81f9d081393c3b301e` | 1 |
| adsp.b06 | 220 | `4d9e32c4099dc4728f793c93bd5a5c70` | 7 |
| adsp.b07 | 4,892 | `1b0b467af3469850ab16e9e45ef27a11` | 7 |
| adsp.b08 | 2,306,824 | `f746b9143af235d7837175bb1d498e46` | 1 |
| adsp.b09 | 237,576 | `98f5688c36a3dabe0c1c52d2cb0370ff` | 1 |
| adsp.b10 | 720 | `1d9f1353d7a4ba2c0c4c65614f27aa27` | 9 |
| adsp.b11 | 9,960 | `47b2c79b0085e361b89dc1d1a91aa236` | 7 |
| adsp.b12 | 131,232 | `c0680ea9646ff7fd0e315364e80e40ef` | 1 |
| adsp.b13 | 83,220 | `632ca2f46b12a34402920f6597e723a8` | 1 |
| adsp.b14 | 3,153,060 | `2f060b035bc5aef6628d02c83fed3424` | 1 |
| adsp.b15 | 107,372 | `4ea3d7aa5490355b96a89fdef120038d` | 1 |
| adsp.b16 | 280 | `9c737fdb61c3c46baf82fffa4075f687` | 1 |
| adsp.b17 | 180,608 | `9a9c3341641d5f53db6a79fc650c072d` | 1 |
| adsp.b18 | 11,409,944 | `3fc16f340651f2ba924959ba693804eb` | 1 |
| adsp.b19 | 503,816 | `48e891f87facfb15fc9c682ae1fb8cbd` | 1 |
| adsp.b20 | 1,936 | `bfb65dba6962dafe24b3942bdf75f856` | 2 |
| adsp.b21 | 167,836 | `5d26e9206e06c3c086c08415eed00907` | 5 |
| adsp.b22 | 52,376 | `45a5c39aeb2d968336e831901f66a084` | 2 |
| adsp.b23 | 610,396 | `276799d70d134e0e5271029ec16404f5` | 2 |
| adsp.b25 | 4,220 | `c9673dc9796780ea4aae92623e4dea63` | 1 |

The sequence runs b00..b23 then b25 - **adsp.b24 does not occur in the Mi_12 census** while 39 other device censuses corpus-wide carry `adsp.b24` (none of them a Xiaomi 12/12S-family device), and `adsp.b25` occurs on 48 corpus devices including the entire Xiaomi 12/12S family. The b24 gap is a whole-family property, not a Mi_12 extraction accident [F].

### The 18 vendor/lib/rfsa/adsp rows (HTP graphs + audio resources)

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| bm2n00.bin | 1,246,136 | `5e94ea8bf6f3d350d5f62a65c578dcd9` | 9 |
| bm2n01.bin | 1,322,216 | `bf260b9e44a392867fea2746cb4bd215` | 9 |
| bm2n02.bin | 1,508,808 | `a05c4d80ccad64ff5144cc377c9eb9f9` | 9 |
| bm2n03.bin | 570,128 | `6cffe9648942c8aeceb3303898a5c89a` | 9 |
| bm2n04.bin | 768,624 | `68d4dcdf4c7ccfc23c64b452f08bdca0` | 9 |
| bm2n05.bin | 8,337,984 | `15b6df71a304f7ec97f6d281e9b0cfec` | 9 |
| bm2n06.bin | 836,968 | `8f8a96f2647444582a68f50d6dace25a` | 9 |
| bm2n07.bin | 1,339,032 | `281755c08b98e757f00586d0052132b1` | 9 |
| bm2n08.bin | 3,059,736 | `d3e4f74372a9a418bdba3b5d34ac3515` | 2 |
| bm2n09.bin | 3,021,464 | `79e107c90b40544477729192968d4d1e` | 2 |
| bm2n10.bin | 8,339,888 | `0f653ef5d5bae2120a58bb61985b2b47` | 9 |
| bm2n11.bin | 8,337,872 | `ec4792d8abc54b8211fb23138c1a82e8` | 9 |
| hrtf5c.bin | 164,480 | `2a47164eed5282f27ad503a28c7b71a0` | 12 |
| misound_karaoke_res.bin | 9,724 | `06c1e0504c3c5f022adb86c48af1e9f8` | 2 |
| misound_karaokemix_res.bin | 192 | `a9484f0c7da94ce6cdd870d84483b0af` | 8 |
| misound_res_headphone.bin | 2,048 | `53fe67652944f4ee760b50e48c7a614e` | 6 |
| misound_res_spk.bin | 15,116 | `2460b6f3bcb6bfe0e18b1be66604f8dd` | 1 |
| misound_res_spk4ch.bin | 71,784 | `3799858ef4fd0bd081852ac41d0b53e1` | 8 |

## Census completeness - proven against the LineageOS packaging manifest [F]

- `LineageOS/android_device_xiaomi_cupid` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21) lists under "# ADSP modules" exactly the 18 vendor-tree files the census carries (bm2n00-bm2n11, hrtf5c, 5 misound) - file-for-file match.
- The same manifest contains **no** `adsp.mdt` / `adsp.bNN` / `.jsn` entries: LineageOS does not package the split-PIL firmware into the vendor tree; on cupid those files live in the device's modem partition, which is where the census's `modem/image` rows come from. This mirrors the OnePlus packaging contrast recorded in docs/devices/samsung/Galaxy_S20_FE/adsp.md (#1096): Samsung integrates DSP firmware inside its modem image; Xiaomi/OnePlus ship it as modem-partition split files.
- `TheMuppets/proprietary_vendor_xiaomi_cupid` @ lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/` (fetched 2026-11-21) holds all 18 files with byte-exact census sizes, plus 40 DSP skel `.so` libraries (`libQnnHtpV69.so` 9,341,540 B, `libSnpeHtpV69Skel.so` 5,457,672 B, `libtracker_6dof_skel_8350.so` 24,208,000 B, ...). Those `.so` files appear **nowhere in Mi_12's 783-row census** - the census's adsp family is the `.bin`/firmware payload view, not the shared-library view.
- The `libQnnHtpV69.so`/`libSnpeHtpV69Skel.so` naming in the same directory is direct vendor evidence that the Mi 12 DSP stack targets **Hexagon V69** [F] - the SoC's DSP ISA generation.
- `TheMuppets/proprietary_vendor_xiaomi_sm8450-common` @ lineage-22.2 firmware dir holds only Adreno GPU files (a662_gmu.bin, a660_sqe.fw, a730_sqe.fw, gmu_gen70000.bin) - no bm2n, no adsp firmware; the variant matrix's negative (#"sm8450 trees have no bm2n") re-confirmed this session [F].

## Container and interface facts

### Split-PIL firmware (the 28 modem/image rows)

- The mdt+bNN form is Qualcomm's signed PIL split container: `adsp.mdt` (5,104 B) is the ELF header/program-header image, the `bNN` files are its loadable segments, and the `.jsn` files are servreg metadata. Mainline Linux parses this format in its Qualcomm peripheral image loader; the in-repo modem-DSP container study (research/fleet/qdsp6sw-container.md, #606) additionally documents the public `QCOM_MDT_RELOCATABLE` p_flags bit in mainline since v4.11 [F].
- Mainline `arch/arm64/boot/dts/qcom/sm8450.dtsi` (fetched 2026-11-21): `remoteproc_adsp` compatible **`qcom,sm8450-adsp-pas`** with `memory-region = <&adsp_mem>`; `remoteproc_cdsp` compatible `qcom,sm8450-cdsp-pas`. PAS = peripheral authentication service: the kernel hands the signed adsp image to TrustZone for verify-and-boot [F].
- The two `.jsn` files are servreg (service registry) JSON, publicly shipped by Linux distros beside the mdt/bNN under `lib/firmware/qcom/<soc>/<device>/` (armbian/firmware, batocera-linux, Lakka; 283 GitHub hits for `filename:adspua.jsn`, 2026-11-21). A public SM8250 sample (armbian `qcom/sm8250/xiaomi/elish/adspr.jsn`, fetched 2026-11-21) shows the schema: `sr_version`, `sr_domain {soc: msm, domain: adsp, subdomain: root_pd, qmi_instance_id: 74}`, `sr_service [{tms/servreg}]`; `adspua.jsn` carries `subdomain: audio_pd` plus the `avs/audio` service [F]. Mi_12's copies (513 B / 703 B) are byte-identical across a 30-device set spanning SM8350-class (OnePlus_9), SM8450 (Mi_12), SM8475-class (Phone_2, Mi_12T_Pro), SM8550-class (Mi_13) and SM8650/SM8750-class (OnePlus_12, OnePlus_13) hardware - SoC-generic text [I]. The SM8450-era files are larger than the SM8250 samples (403 B / 555 B), so they are not byte-identical to those public samples [F].
- `adsp.mdt` size clusters by SoC generation across the corpus (59 `adsp.mdt` rows, range 5,104-9,660 B): 5,104 B for the SM8450 pair (Mi_12, Mi_12_Pro), 5,404 B for the SM8475-class five (Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Poco_F5_Pro), 8,524 B for the SM8550-class four (Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro) [F sizes; SoC-generation mapping [I] from public device specs].
- The in-repo signed-PIL metadata decode (research/fleet/pil-metadata-sweep.md) proves the per-phdr hash-slot metadata layout fleet-wide on SM8250 (SHA-384 slots) and SDM845 (SHA-256 slots). No SM8450 image has been decoded in-repo; the adsp.mdt phdr count, hash width and cert chains for cupid are [OPEN].
- The b24 gap: with b00..b23 + b25 present, the segment table of cupid's adsp build skips index 24 [I - per-build program-header indices are the known source of bNN numbering; verifying requires the payload, [OPEN]. The 9-device Xiaomi/Nothing group shares the same gap (0 b24 rows on all of Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro) [F].

### HTP graph payloads (the 12 bm2n rows) - established in-repo findings, not re-derived

- research/laptop/qualcomm-adsp-bm2n-fleet-content.md (measured payloads, 49 fetched, 48/48 parse): the bm2n blobs are **serialized neural-network graphs for the Hexagon Tensor Processor**, not modem firmware - record tag `0x1337beef` = `TENSOR_MAGIC` from the public `QNN/HTP/core/tensor.h:100`, prologue RTTI name `14ConcreteTensorIN5Tdefs10QuantUint8EE`, `hnnx`-namespaced operator classes, one HTP pickle variant (`0x7309F72B`). The `adsp` in the path is the FastRPC domain id (`ADSP_DOMAIN_ID (0)`, `drivers/misc/fastrpc.c:31`), not evidence of modem code [F]. This re-classifies Mi_12's db_type=MODEM on all 46 rows as a mislabel for the 18 rfsa rows [I].
- The compact container header is specified at 48/48 files (research/laptop/qualcomm-adsp-bm2n-container-header.md): load base at 0x00 (one of 0x200000/0x400000/0x800000), 7-char ASCII build-id at 0x0c, magic `0xfa0000fa` at 0x14, segment table at 0x24, count-complement terminator. Mi_12's bm2n06 and bm2n08 are payload-verified members of that fleet: the cupid/diting `bm2n08`/`bm2n06` pairs share build-id `bab1be8` with load base 0x400000 (measured 2026-11-18) [F].
- research/laptop/qualcomm-adsp-bm2n-variant-matrix.md (Table 2, fetched 2026-11-18): Mi_12's `bm2n08.bin` revision (`d3e4f743...`, 3,059,736 B, Mi 12 / Mi 12 Pro only) was fetched from `TheMuppets/proprietary_vendor_xiaomi_cupid` @ lineage-22.2 - **same size as** the SM8475-class revision (`44e31e18...`) **but different bytes**; and the cupid tree ships `bm2n00`-`bm2n11` only (bm2n12-bm2n15 absent), exactly matching Mi_12's census [F].
- Filename is not identity (fleet-content F-75): Mi_12's `bm2n07.bin` (1,339,032 B, `281755c0...`) is the same byte identity that serves `bm2n14`/`bm2n15`/`bm2n16` filename slots on SM8475-class trees [F].
- Corpus scale (re-verified this session): 446 bm2n* rows, 35 devices, 65 distinct filenames bm2n00-bm2n71 [F].
- ISA status: `isa_identified` is empty on all 46 rows - honestly un-RE'd at instruction level in the corpus; the bm2n work measured container structure and record framing, not Hexagon instructions. The DSP ISA generation is Hexagon V69 (QNN library naming above + public specs) [F], but no instruction-level fact about any of these 46 blobs is claimed here [N].

## Cross-corpus md5-sharing summary [F]

| share set | files | members |
|---|---|---|
| 30 devices | adspr.jsn, adspua.jsn (identical set) | Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_13, Mi_13_Pro, Moto_G200, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, OnePlus_9, OnePlus_9_Pro, OnePlus_9RT, Pad_2_Pro, Pad_Pro, Phone_1, Phone_2, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 12 devices | hrtf5c.bin | Mi_12 family x6, Mi_13, Mi_13_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro |
| 9 devices | bm2n00-bm2n07, bm2n10, bm2n11, adsp.b10 | Mi_12 family x6, Phone_2, Poco_F5, Poco_F5_Pro |
| 8 devices | misound_karaokemix_res, misound_res_spk4ch | Mi_12 family x6, Poco_F5, Poco_F5_Pro |
| 7 devices | adsp.b01, b03, b04, b06, b07, b11 | Mi_12 family x6, Poco_F5_Pro |
| 6 devices | misound_res_headphone | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12T_Pro, Poco_F5_Pro |
| 5 devices | adsp.b21 | Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra |
| 2 devices | bm2n08, bm2n09, misound_karaoke_res | Mi_12, Mi_12_Pro |
| 2 devices | adsp.b20, b22, b23 | Mi_12, Mi_12S_Ultra |
| 1 device (Mi_12 exclusive, 16 files) | adsp.mdt, adsp.b00, b02, b05, b08, b09, b12-b19, b25, misound_res_spk | Mi_12 |

16 of 46 files are Mi_12-exclusive; the ADSP OS image itself (mdt + most large bNN segments) is a cupid-specific build, while the metadata shell (jsn) is fleet-generic and the audio/HTP payloads are generation-shared. (Corpus device label `Poco_F6_PRo` is the database's own spelling; kept as recorded.)

## Honest negatives

- No Mi_12 payload was fetched or decoded in this issue: the split-PIL metadata (phdr count, hash width, signing chains of cupid's adsp.mdt) is unverified for SM8450; the bm2n structural facts are carried from the in-repo measured fleet work, identity resting on md5 equality. [OPEN]
- The exact byte content of Mi_12's adspr.jsn/adspua.jsn is not diffed against the public servreg samples (sizes differ from the SM8250 copies; a re-serialization md5 test this session did not match, so the 513/703 B texts carry SM8450-era differences). [OPEN]
- Whether cupid's modem partition physically contains an `adsp.b24` (or the build's ELF simply has no segment 24) is not decodable from the census alone. [OPEN]
- The function of each misound_* and hrtf5c resource is inferred from vendor naming (MiSound audio tuning / head-related transfer function) and their tiny sizes, not payload-verified. [I]
- The 40 DSP skel `.so` libraries in the vendor tree are outside the census; their absence from the 783-row extract is recorded, not explained (the upstream devices.sql enumeration did not include them). [I]
- linux-firmware WHENCE (fetched 2026-11-21) lists none of bm2n/misound/hrtf5c/adspr.jsn/adspua.jsn/adsp.mdt - none of this family is mainlined. [F]

## What would upgrade this finding

1. Payload fetch (cupid modem partition or a cupid LineageOS firmware dump): decode adsp.mdt program headers + metadata segment - the first SM8450 ADSP metadata decode; settles the hash-width question against the SM8250 SHA-384 precedent and explains the b24 skip.
2. Byte-diff Mi_12's 513/703 B jsn files against the public servreg samples and record the SM8450-era schema delta.
3. Run the bm2n container probe (implementations/adsp-fleet/) over the cupid-tree bm2n00-11 variants - only bm2n06/bm2n08 of cupid's set were payload-measured; ten of twelve are structurally unmeasured.
4. Extend the variant matrix's per-md5 leverage tables with the 9-device bm2n share group recorded here (one RE pass on `5e94ea8b...` genuinely serves 9 corpus devices).

## RULE 0 record (2026-11-21)

Queries in the SEARCH comment. Checks: `Xiaomi 12 cupid SM8450 Snapdragon 8 Gen 1 codename specs` (web, 2026-11-21) -> identity only; `"bm2n" qualcomm adsp file hexagon tensor processor QNN graph blob` (web, 2026-11-21) -> no public bm2n documentation; `filename:adspua.jsn` (GitHub code search, 2026-11-21, adineo-cmd/* excluded) -> distro firmware packaging only; linux-firmware WHENCE (2026-11-21) -> no member of this family. Format-level prior art (mainline PIL loader, public QNN/HTP headers, servreg schema) is cited, not rebuilt; DELTA posted on the issue.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public device trees, manifests and specs.
