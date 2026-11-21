# xiaomi Mi_A3 (laurel_sprout) - `adsp` family status (33 rows - PRESENT, census-complete; two-container grammar: modem-partition split-PIL firmware + one vendor-tree FastRPC audio resource; SM6125-generation signature)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1240](https://github.com/adineo-cmd/open-device/issues/1240)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site c3e317c), `upstream-contribution/blob-database/device-inventory.csv`, the LineageOS `android_device_xiaomi_laurel_sprout` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), linux-firmware WHENCE and the shipped `qcom/qcm2290` servreg manifests (git.kernel.org, fetched 2026-11-21), torvalds/linux master `arch/arm64/boot/dts/qcom/sm6125.dtsi`, `sm6125-xiaomi-laurel-sprout.dts`, `drivers/remoteproc/qcom_q6v5_pas.c` (fetched 2026-11-21), `linux-msm/pd-mapper` `pd-mapper.c` (fetched 2026-11-21), public spec pages (GSMArena 9777, Qualcomm Snapdragon 665 product brief, 2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_12/adsp.md (#1168), docs/devices/xiaomi/Mi_12S_Pro/adsp.md (#1186), docs/devices/xiaomi/Mi_12T_Pro/adsp.md (#1204), docs/devices/xiaomi/Mi_13/adsp.md (#1222). No payloads fetched by this issue; every number is command output or a recorded fetch.

**Verdict: the `adsp` family is PRESENT on Mi_A3 and the census is COMPLETE - 33 rows, 15,962,970 B, 33 distinct md5s, all db_type=MODEM, priority P3.** The rows split across two containers: (a) 32 rows at `xiaomi/laurel_sprout/modem/image` = the signed split-PIL ADSP firmware image (`adsp.mdt` 8,940 B + 28 contiguous segments `adsp.b00`-`adsp.b27`, no gaps) plus the 3-file servreg JSON trio (`adspr.jsn`, `adsps.jsn`, `adspua.jsn`, 1,363 B together); (b) 1 row at `xiaomi/laurel_sprout/vendor/lib/rfsa/adsp` = `misound_res.bin` (75,756 B), the Xiaomi Mi Sound ADSP audio resource delivered at runtime over FastRPC. 30 of the 33 files are byte-identical to nothing else in the corpus (device-signed firmware); the 3 manifests are shared verbatim with 24-30 other devices, and the exact same three bytes ship upstream in linux-firmware as `qcom/qcm2290/{adspr,adsps,adspua}.jsn` (md5-verified against the kernel.org copies this session). There is no structural absence and no census gap: the modem-partition half is fully censused, unlike Mi_10T_5G (SM8250), whose adsp family holds only 4 vendor-tree misound rows and zero modem/image rows - the #1144 census-gap pattern, in a Xiaomi device.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi A3 (Android One program); codename `laurel_sprout` | `device-inventory.csv` (`laurel_sprout`) [F]; public spec pages (2026-11-21) [F] |
| SoC | Qualcomm **SM6125 Snapdragon 665** (11 nm); Adreno 610; Hexagon 686 DSP with HVX | public spec pages (2026-11-21) [F]. **The coverage-matrix and inventory SoC cells are EMPTY** - SoC supplied here [F]; flag for the lead (the leverage-families.md stub records "SoC: \N") |
| released | July 2019 | public spec pages (2026-11-21) [F] |
| stock base | Android 11 `V12.0.26.0.RFQMIXM` (RKQ1.200903.002) | LineageOS laurel_sprout `proprietary-files.txt` header "Unpinned blobs from laurel_sprout-user 11 RKQ1.200903.002 V12.0.26.0.RFQMIXM release-keys" (fetched 2026-11-21) [F] |
| census scope | 326 rows in 9 families (other 122, tz 57, wifi 45, adsp 33, modem 33, bt 11, cdsp 11, boot 8, gpu 6) | coverage-matrix.csv [F] |
| priority | P3 | coverage-matrix.csv, all 33 adsp rows [F] |

Inventory flags for the lead: the adspr.jsn share-set exposes two wrong matrix cells - OnePlus_7 carries "MSM8998 Snapdragon 835" but OnePlus 7 is SM8150 Snapdragon 855 per public specs [F]; Nord_CE3's cell carries a leading mojibake byte ("&yuml;Qualcomm SM6375...") [F, data hygiene].

## Census evidence [F]

All 33 adsp rows: `blob_family=adsp`, `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, `db_type=MODEM`, priority P3; 33 distinct md5s (no internal duplication). Note the vendor-tree row also carries db_type=MODEM although it is FastRPC payload, not modem code - the same corpus-wide db_type phenomenon documented for the SM8550 bm3 graphs (#1222).

| container | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp.mdt` + 28 `adsp.bNN`, b00-b27 contiguous) + servreg trio | 32 | 15,887,214 | `xiaomi/laurel_sprout/modem/image` |
| FastRPC audio resource (`misound_res.bin`) | 1 | 75,756 | `xiaomi/laurel_sprout/vendor/lib/rfsa/adsp` |
| total | 33 | 15,962,970 | - |

Verified decomposition: 8,940 (mdt) + 15,876,911 (28 bNN) + 1,363 (3 jsn: 403+405+555) = 15,887,214 modem/image bytes; + 75,756 misound = 15,962,970 (python, this session). The modem-partition half is 99.53% of family bytes and the vendor-tree half 0.47% - the inverse of the SM8550-generation shape (Mi_13: the vendor-tree bm3 graph tier is 85.7% of family bytes, #1222). The shell files (mdt + manifests) total 10,303 B.

### The 32 firmware rows in modem/image

Shell files (4):

| file | bytes | md5 | devices sharing md5 |
|---|---|---|---|
| adsp.mdt | 8,940 | `c510f4b8092658d8570e9c65b9006915` | 1 (Mi_A3 only) |
| adspr.jsn | 403 | `40d6edf129dec063ca3fe6cb6837488f` | 30 |
| adsps.jsn | 405 | `c7253d84bff46e4cf5cb0585e9a851c5` | 24 |
| adspua.jsn | 555 | `d0bd5030a03f631c9af5060a5645d02e` | 30 |

Segment files (28; contiguous b00-b27, no gaps - the SM6115/SM4250-generation cohort has gaps: Moto_G9 skips b11 across b00-b35, Moto_G30 skips b11 across b00-b33). `devices` = corpus-wide count of devices carrying that byte identity (md5 sweep over all 33,917 rows):

| file | bytes | md5 | devices |
|---|---|---|---|
| adsp.b00 | 980 | `7b9f70158437664c069f95615363c8e1` | 1 |
| adsp.b01 | 7,960 | `c8576a0ad63d53044d8d5612dd66f868` | 1 |
| adsp.b02 | 8,308 | `72c31a2a25425e5fc621f599837e0080` | 1 |
| adsp.b03 | 172,416 | `bda35fe12ac249f957910830d11f02b2` | 1 |
| adsp.b04 | 1,723,152 | `873db66b00907eb6a948172a5740120b` | 1 |
| adsp.b05 | 1,163,616 | `6bbbd6c81b1458aceb7e3c34969cf428` | 1 |
| adsp.b06 | 2,896 | `3cd914208333c218017213de91014728` | 1 |
| adsp.b07 | 24,516 | `efcf42ea02c9a6bdc871c5664eb346e8` | 1 |
| adsp.b08 | 114,720 | `34ba38d67715f76881dd4268cffc889d` | 1 |
| adsp.b09 | 72,508 | `b99121515cb6fd4530ad1037901d0405` | 1 |
| adsp.b10 | 1,007,616 | `89477909066242c52477967f3ae2bb8e` | 1 |
| adsp.b11 | 1,041,115 | `62f513fedf573fdac61c60f0fd7c275e` | 1 |
| adsp.b12 | 175,832 | `c171988f7be2cb14c1a7533857b78c81` | 1 |
| adsp.b13 | 127,556 | `8477290cd040f8865323a3f0961ba8aa` | 1 |
| adsp.b14 | 28,680 | `d54b4ccf490af286139c962f99fe1ee1` | 1 |
| adsp.b15 | 9,878 | `c5ff2f63cdb51d51b1f99a6a79225123` | 1 |
| adsp.b16 | 15,200 | `b1cf90559c0d7bb508b9aced37c99f44` | 1 |
| adsp.b17 | 28,404 | `c5b7d6e2eb9cb0ec52eb340e962a383e` | 1 |
| adsp.b18 | 192,604 | `c97b38212a024c1fcee6beed806a106d` | 1 |
| adsp.b19 | 471,040 | `63fd970e11767e9f4dbd9b33591c0dec` | 1 |
| adsp.b20 | 5,290,803 | `3c60db73e511e40ab26fd865790f6242` | 1 |
| adsp.b21 | 2,354,083 | `33f1d21c2e87397c2b78ba2baa201eef` | 1 |
| adsp.b22 | 13,324 | `3701ec90f6d573b999dfcd0aa60bc866` | 1 |
| adsp.b23 | 312,008 | `37d5e98ba3f5179c402a9f233506549d` | 1 |
| adsp.b24 | 3,360 | `37fcb04bb38fe7ae1ab0a28f4cdebd0e` | 1 |
| adsp.b25 | 84,076 | `d32f0efe181dfb98e69222deffc42b4a` | 1 |
| adsp.b26 | 1,430,000 | `d2c144e1486e29f19fe96144679e7e6c` | 1 |
| adsp.b27 | 260 | `81719e8fda0173c751461f24f362516f` | 1 |

Every segment and the mdt are Mi_A3-exclusive corpus-wide (30 of 33 adsp files single-device; python sweep, this session) - device-signed firmware is not shared across the corpus, only the generic manifests are [F].

### The 1 vendor-tree row

| file | bytes | md5 | devices sharing md5 | db_path |
|---|---|---|---|---|
| misound_res.bin | 75,756 | `f62ba7a57bb13e379b37308f6db79264` | 1 (Mi_A3 only) | `xiaomi/laurel_sprout/vendor/lib/rfsa/adsp` |

`misound_res.bin` is the exact-name singleton of the whole corpus: no other device carries a file of that name (python sweep, this session). Public LineageOS manifests label this exact path "ADSP modules (misound)" (laurel_sprout lineage-22.2 lines 24-25) and the same file "Audio (speaker amplifier) firmware" (dipper, xmsirius trees) [F].

## Cross-corpus facts

- The servreg trio is fleet-wide and SoC-agnostic: the exact Mi_A3 bytes appear on 30 devices (adspr.jsn, adspua.jsn) and 24 devices (adsps.jsn) spanning at least seven SoC families by matrix/public cells - SM8150 (OnePlus_7/7_Pro/7T/7T_Pro), SM8250 (OnePlus_8/8_Pro), SM7225 (FP4), SM6375 (Nord_CE2, Nord_CE3, Realme_9_Pro, Realme_10_Pro, Edge_30_Neo), SM6125 (Mi_A3), SM6115 (Moto_G9, Moto_G9_Power, Moto_G_Power, Moto_G30, Defy_2021, Pro_1X), SM4250 (Moto_E7_Plus, Moto_G10) - plus Moto_G32/G42/G52/G82_5G/G84_5G/G34_5G/G_5G_2024 and the two G_Stylus_5G entries [F]. qmi_instance_id 74 is constant in all copies [F, manifest bytes].
- **Public md5 cross-check:** linux-firmware WHENCE lines 7433-7437 ship `qcom/qcm2290/adsp.mbn` plus `qcom/qcm2290/{adspr,adsps,adspua}.jsn`; the kernel.org copies of those three manifests md5-match Mi_A3's census rows exactly (403/405/555 B; downloaded and md5summed this session) [F]. Mi_A3's device manifests are the generic upstream service-registry manifests, not device-specific data.
- The trio is the same file set the Mi_13 census (#1222) reports, one generation older and smaller: Mi_A3 403/405/555 B vs SM8550 513/515/703 B; both generations show 30-device adspr/adspua share fleets [F].
- The OnePlus contrast: OnePlus_7 (SM8150) censuses 17 adsp rows = mdt + adspr.jsn + adspua.jsn + b00-b13, with **no adsps.jsn at all** [F]; no OnePlus device appears in the 24-device adsps.jsn fleet [F] - the sensor_pd manifest is not universal.
- misound lineage inside the adsp family on Xiaomi: Mi_A3 (SM6125) ships ONE misound file; the SM8450/SM8475 generation (Mi_12, Mi_12S family, Mi_12T_Pro, Poco_F5/F5_Pro; #1168/#1186/#1204) ships a 4-5 file misound set (res_spk / res_spk4ch / res_headphone / karaoke / karaokemix); SM8550 (Mi_13, #1222) ships zero - the tier left the family. Inside the newer set some files are fleet-identical (misound_res_spk4ch.bin 71,784 B md5 `3799858ef4fd0bd081852ac41d0b53e1` on 6 devices; misound_karaoke_res.bin 9,752 B md5 `1a43838d29fc032cd37b4dac72a54ba0` on 5) but the SM6125-era file shares nothing with them [F, corpus sweeps].
- **Census-gap contrast (calibration):** Mi_10T_5G (gauguin, SM8250) censuses only 4 adsp rows - all vendor-tree misound files, zero modem/image rows [F] - the #1144 census-gap rule (families riding in the modem image gap out) in a Xiaomi device. Mi_A3 is the positive control on the same corpus: its modem/image adsp half is fully present. OnePlus_7/8 (SM8150/SM8250) hold 17/22 rows - partial censuses of their generation; Mi_A3's 33-row census is not one of them.

## Interface and ISA facts

- **Servreg manifest schema [F]** (read from the kernel.org public copies, byte-identical to Mi_A3's rows): each manifest is `sr_version` 1.1.1 + `sr_domain` {soc "msm", domain "adsp", subdomain ..., qmi_instance_id 74} + `sr_service` list. Subdomains: adspr = **root_pd**, adsps = **sensor_pd**, adspua = **audio_pd**. Services: tms/servreg on all three; adspua additionally declares **avs/audio**. The three files are service-registry declarations for the three Hexagon protected domains (root/sensor/audio) of the ADSP - not segment tables.
- **Public consumer [F]:** linux-msm/pd-mapper (successor of andersson/pd-mapper) parses exactly this schema - `pd-mapper.c` reads sr_domain soc/domain/subdomain/qmi_instance_id (lines 144-148) and builds a "soc/domain/subdomain" -> instance map (lines 183-186), enumerating `.jsn` files (lines 270-271). These are the manifests an upstream-booted SM6125 device would use for servreg domain mapping.
- **Kernel-side loading [F]:** the mdt/bNN pair is the Qualcomm split-PIL firmware shape loaded by the kernel's qcom mdt loader (drivers/soc/qcom/mdt_loader.c pattern, consumed by qcom_q6v5_pas). Mainline `sm6125.dtsi` already reserves the ADSP PIL carve-outs (`adsp_pil_mem` 0x55300000 size 0x1e00000 = 30 MiB; `adsp_mem` 0xf3400000 size 0x800000 = 8 MiB) [F], but neither `sm6125.dtsi` nor `sm6125-xiaomi-laurel-sprout.dts` declares the adsp remoteproc node yet, and `qcom_q6v5_pas.c` carries `qcom,sm6115-adsp-pas` / `qcom,sdm660-adsp-pas` compatibles but no `qcom,sm6125-adsp-pas` [F]. The 30 MiB PIL carve-out fits the 15.22 MiB firmware with headroom [I].
- **Packaging [F]:** the LineageOS laurel_sprout manifest lists exactly two adsp-related vendor files - `vendor/lib/rfsa/adsp/misound_res.bin` and `vendor/etc/acdbdata/adsp_avs_config.acdb` (an ACDB audio-calibration table, outside the rfsa tree); the adsp.mdt/bNN/jsn set ships in the modem partition and is not vendor-packaged, matching the census's db_path split 1:1.
- **ISA [F + honest negative]:** the ADSP on SM6125 is Qualcomm Hexagon (Hexagon 686 with HVX per the public product brief); the corpus records `isa_identified` EMPTY for all 33 rows and `interface_documented=n` - the segments are honestly un-RE'd here. By size alone the likely code-bearing segments are adsp.b20 (5,290,803 B, 33.1% of family bytes), adsp.b04 (1,723,152 B, 10.8%) and adsp.b26 (1,430,000 B, 9.0%) [I - no disassembly performed].

## Honest negatives ([OPEN])

- No payload of this device was fetched or analyzed (metadata-only per Phase 2 rules); all 30 device-signed files exist in the corpus as hashes only.
- No Hexagon ISA proof: `isa_identified` is empty on every row; no segment was disassembled; the root/sensor/audio PD split is proven from the public manifests, not from the segments [F for manifests, OPEN for segment-level proof].
- `misound_res.bin` is publicly un-RE'd everywhere searched (packaging labels only, no analysis found); its internal format and its relationship to the later per-role misound_res_spk/headphone/karaoke split are [OPEN].
- The 28-segment set b00-b27 is contiguous in the census, but metadata alone cannot prove the stock image lacks segments beyond b27 in every firmware revision; the LineageOS manifest does not package modem/image at all, so the census is the only completeness witness for that half [OPEN].
- No known public copy of laurel_sprout's `adsp.mdt`/`adsp.bNN` bytes exists (unlike the generic manifests), so no external byte-verification of the device-signed half was possible [OPEN].

## What would upgrade this finding

1. Fetch the laurel_sprout stock modem partition (stock fastboot image or OTA payload), byte-verify the 32 modem/image rows against the census md5s, and dump the ELF program headers of `adsp.mdt` (8,940 B) to enumerate the real segment map, including anything beyond b27.
2. Disassemble adsp.b20/b04/b26 with a public Hexagon toolchain (a Ghidra Hexagon module or a Capstone fork with Hexagon support) and record the ISA version - that would fill `isa_identified` for this device and ground the PD code split.
3. Diff `misound_res.bin` against the SM8450-generation misound_res_spk.bin files to test whether the single file is a concatenation of the later per-role resources.
4. Compare against linux-firmware's `qcom/qcm2290/adsp.mbn` (the QCM2290 IoT sibling) for shared code segments - the manifest trio is already proven identical, so shared segment code is plausible [I].

## RULE 0 record

- CLAIM posted 2026-11-21T10:05:05Z as the first comment (confirmed by re-read; no other agent claimed).
- SEARCH (Gate -1) and DELTA (Gate 0) posted 2026-11-21; work started only after the DELTA.
- All census numbers are awk/python outputs on coverage-matrix.csv at feat/open-device-site c3e317c, this session; all web fetches dated 2026-11-21 (WHENCE line numbers recorded per fetch).

Nothing in this document is legal advice; no proprietary payload bytes were fetched, stored or committed - only sizes, hashes, public-manifest schema and public-source quotations.
