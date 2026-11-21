# motorola Moto_G10 (capri) - `adsp` family status (35 rows - PRESENT, census-complete; SM4250/bengal-generation split-PIL audio-DSP image `adsp2` + fleet-wide servreg manifests; the missing `adsp2.b11` is STRUCTURAL, not a census gap)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1258](https://github.com/adineo-cmd/open-device/issues/1258)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 9119bd4), `upstream-contribution/blob-database/device-inventory.csv`, LineageOS `android_device_motorola_capri` `proprietary-files.txt` (lineage-22.2 branch, fetched 2026-11-21), torvalds/linux master `drivers/soc/qcom/mdt_loader.c`, `drivers/remoteproc/qcom_q6v5_pas.c`, `arch/arm64/boot/dts/qcom/sm4250.dtsi`, `sm6115.dtsi` (fetched 2026-11-21), linux-firmware WHENCE and the shipped `qcom/qcm2290/adsp.mbn` (git.kernel.org, fetched and ELF-parsed 2026-11-21), MotorolaMobilityLLC public kernel trees `kernel-devicetree` (branch android-11-release-rrb), `kernel-audio-devicetree` (branches android-13-release-tsc, android-12-release-s3sl32.16-72-46), `kernel-msm-5.4-techpack-audio` (master) (fetched 2026-11-21), public spec pages (LineageOS wiki capri page, Qualcomm Snapdragon 460 product brief, 2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_A3/adsp.md (#1240). No device payload was fetched or committed; the only binary inspected is the public linux-firmware `qcom/qcm2290/adsp.mbn`, parsed for ELF header metadata only. Every number is command output or a recorded fetch; sums re-verified with python3 this session.

**Verdict: the `adsp` family is PRESENT on Moto_G10 and the census is COMPLETE - 35 rows, 14,114,387 B, 35 distinct md5s, all db_type=MODEM, all at `motorola/capri/modem/image`, priority P3.** The family is the signed split-PIL audio-DSP (ADSP) firmware image in Qualcomm's split-ELF convention, named **`adsp2`** (not `adsp`) on this bengal-generation device: `adsp2.mdt` 9,260 B + 31 segment files `adsp2.b00`-`adsp2.b31` (14,103,764 B) + the 3-file servreg manifest trio (`adspr.jsn`, `adsps.jsn`, `adspua.jsn`, 1,363 B together). The b00-b31 range has exactly one gap, `adsp2.b11`, and that gap is **structural, not a census gap**: the bengal-generation ADSP ELF declares program header 11 as a file-data-less (BSS-only) PT_LOAD - proven against the public linux-firmware QCM2290 (SM4250-generation) build, reproduced corpus-wide by all 10 bengal Moto devices while 37 non-bengal corpus devices DO census b11 - so no `adsp2.b11` file exists to census on any bengal build. The 35-row census is complete with zero gaps.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Moto G10, XT2127 | public spec pages (2026-11-21) [F] |
| codename | `capri` (both db_path and inventory agree) | `device-inventory.csv` [F]; LineageOS wiki capri page (2026-11-21) [F] |
| SoC | Qualcomm **SM4250 Snapdragon 460** (11 nm); Adreno 610 | inventory cell [F]; public spec pages (2026-11-21) [F]. **The inventory SoC cell is CORRECT for this device** - unlike the known-wrong dubai/tundra cells |
| DSP | Hexagon 683 with Hexagon Vector eXtensions (HVX) and scalar accelerator | Qualcomm Snapdragon 460 product brief (fetched 2026-11-21) [F] |
| released | inventory `released_year` cell EMPTY (data hygiene); public pages: announced February 2021 | device-inventory.csv [F]; public spec pages (2026-11-21) [F] |
| stock build | `capri_retail RRB31.Q1-3-48-24` | LineageOS capri proprietary-files.txt header "All unpinned blobs below are extracted from capri_retail RRB31.Q1-3-48-24" (fetched 2026-11-21) [F] |
| census scope | 211 rows in 9 families (other 44, modem 43, wifi 40, adsp 35, gpu 14, bt 11, cdsp 11, tz 5, boot 8) | coverage-matrix.csv [F] |
| priority | P3 | coverage-matrix.csv, all 35 adsp rows [F] |

Inventory flags for the lead: (a) `count_csv_total` = 34 for Moto_G10 while the coverage-matrix holds 35 adsp rows (artifact accounting drift, cell worth a look) [F]; (b) `extract_status_22.2` = "fails" for capri [F]; (c) the adspr.jsn share-fleet below again contains the two wrong/mangled matrix cells already flagged in #1240 - OnePlus_7 is labeled "MSM8998 Snapdragon 835" but is SM8150 Snapdragon 855 per public specs, and Nord_CE3's cell carries a leading mojibake byte - re-citing those flags, not re-deriving them.

## Census evidence [F]

All 35 adsp rows: `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented=n`, db_type `MODEM`, priority P3; 35 distinct md5s (no internal duplication). db_type=MODEM is here genuinely accurate - unlike the corpus-wide a660 mislabels (#946) - because the whole image ships in the modem partition (see packaging below).

| container | rows | bytes | db_path |
|---|---|---|---|
| split-PIL firmware (`adsp2.mdt` + 31 `adsp2.bNN`, b00-b31 minus b11) | 32 | 14,113,024 | `motorola/capri/modem/image` |
| servreg manifest trio (`adspr.jsn`, `adsps.jsn`, `adspua.jsn`) | 3 | 1,363 | `motorola/capri/modem/image` |
| total | 35 | 14,114,387 | - |

Verified decomposition: 9,260 (mdt) + 14,103,764 (31 bNN) + 1,363 (3 jsn: 403+405+555) = 14,114,387 (python, this session). Min segment 196 B (`adsp2.b31`), max 5,108,316 B (`adsp2.b24`, 36.19% of family bytes).

### Shell files (4)

| file | bytes | md5 | distinct devices sharing md5 |
|---|---|---|---|
| adsp2.mdt | 9,260 | `de3c79bcf90298d899762a7c58c16bc0` | 1 (Moto_G10 only) |
| adspr.jsn | 403 | `40d6edf129dec063ca3fe6cb6837488f` | 30 |
| adsps.jsn | 405 | `c7253d84bff46e4cf5cb0585e9a851c5` | 24 |
| adspua.jsn | 555 | `d0bd5030a03f631c9af5060a5645d02e` | 30 |

### Segment files (31; b00-b31 minus b11)

`devices` = distinct corpus devices carrying that byte identity (md5 sweep over all 33,917 rows; Pro_1X carries some bytes twice under both `adsp.bNN` and `adsp2.bNN` names and is counted once per python set):

| file | bytes | md5 | devices |
|---|---|---|---|
| adsp2.b00 | 1,108 | `e29bfc3f876c88ecb0bb34a51ce6b982` | 1 |
| adsp2.b01 | 8,152 | `b940836fe4e3d2cca5fb3ca3c76f75c1` | 1 |
| adsp2.b02 | 85,300 | `b698935492399fd1bd8d7bb0bfb503db` | 1 |
| adsp2.b03 | 256,000 | `2e1e11cdeab74cfeec15b70488befccc` | 1 |
| adsp2.b04 | 1,796,028 | `20485afeaf096fc5d308fd230191a249` | 1 |
| adsp2.b05 | 1,171,868 | `77bd918d5f8d91f138899f540ccd863d` | 1 |
| adsp2.b06 | 2,912 | `9fbbe90a9b14b9d6bf97fd7c26607a65` | 1 |
| adsp2.b07 | 17,036 | `886b893c812c6df5203063eddb1b956d` | 5 (Moto_G10, Defy_2021, Moto_G9, Moto_G9_Power, Moto_G_Power) |
| adsp2.b08 | 28,492 | `da171123fc6c5163f32000fa3920bbc3` | 1 |
| adsp2.b09 | 4,828 | `d2f85c06886634b0e0d62fa63bbf01e4` | 1 |
| adsp2.b10 | 260 | `a9e7f9c09da4996f46c25e259243e6d2` | 3 (Moto_G10, Phone_1, Pro_1X) |
| adsp2.b12 | 53,888 | `629ffe05861835e72da525ffeb80c675` | 1 |
| adsp2.b13 | 72,936 | `ec336cb36b01a9cf5d7d2bb0dd03cd74` | 1 |
| adsp2.b14 | 8,192 | `c1d73c247bde2afc2d9b158741cf48b6` | 3 (Moto_G10, Phone_1, Pro_1X) |
| adsp2.b15 | 1,624,292 | `c13328327944e4d790b66979877cb1d0` | 1 |
| adsp2.b16 | 28,676 | `350ab5336f5865164a8d889c4976d664` | 1 |
| adsp2.b17 | 11,771 | `cd5437663d720d325105c667faf96210` | 8 |
| adsp2.b18 | 7,008 | `35c11334a6ffd806fe04c581db4e5a12` | 11 (10 Moto bengal devices + Phone_1) |
| adsp2.b19 | 732 | `5d001094c390fd433ddd3a9ceabe71ce` | 3 (Moto_G10, Phone_1, Pro_1X) |
| adsp2.b20 | 5,496 | `cb5f6fca7f09e322d805d048ee54fafa` | 1 |
| adsp2.b21 | 28,444 | `c5f9c7c5b17315ac52a11e0444469bfd` | 1 |
| adsp2.b22 | 136,404 | `b58671075d829a496eb29bb3488c98e8` | 1 |
| adsp2.b23 | 245,760 | `a4197280cf9dd8454c4c8f565a37edb1` | 1 |
| adsp2.b24 | 5,108,316 | `426c92d73b48fae60df5a38f413c0c64` | 1 |
| adsp2.b25 | 1,428,493 | `4b15815bd3f0e5501de5e2ac5f605fac` | 1 |
| adsp2.b26 | 2,500 | `d079ba32ab2f20931dca3479527f9f45` | 1 |
| adsp2.b27 | 313,848 | `3b4e86e99067870ef7615b9094544714` | 1 |
| adsp2.b28 | 2,920 | `8ea52d62633bec4f4072b9e35d5df6c0` | 1 |
| adsp2.b29 | 98,868 | `74b3f7b4f11dadd92f7f905b8243f963` | 1 |
| adsp2.b30 | 1,553,040 | `010fd35193e4d5bc8bb50e052a13fd24` | 1 |
| adsp2.b31 | 196 | `5c1edfe006ae736a90e6914920b56ba3` | 1 |

28 of 31 segments (and the mdt) are Moto_G10-exclusive corpus-wide - device-signed firmware is not shared, only the generic manifests and a handful of small low-index segments [F].

## Container layout - derived from two exact arithmetic laws

The census sizes alone expose the ELF structure (all arithmetic python-verified this session):

- **Law 1: `adsp2.b00` = 1,108 = 52 + 33 x 32.** A little-endian ELF32 header is 52 B and each program header entry 32 B; program header 0 in Qualcomm split-ELF images is a self-referential segment holding the header table itself (public cross-check: linux-firmware `qcom/qcm2290/adsp.mbn` program header 0 is 1,012 B = 52 + 30 x 32, matching its parsed e_phnum of 30). So **capri's ADSP ELF has e_phnum = 33** [F arithmetic + public anchor].
- **Law 2: mdt = b00 + b01 exactly: 1,108 + 8,152 = 9,260.** The mdt retains the header table (phdr 0) plus the hash/metadata segment (phdr 1); the kernel mdt loader reads ehdr size from phdrs[0].p_filesz and the hash table from the mdt itself (torvalds/linux `drivers/soc/qcom/mdt_loader.c` lines 183-210, fetched 2026-11-21) [F].
- The kernel loader names split segments `b%02d` by **program-header index** (mdt_loader.c line 84), requests them only for PT_LOAD headers that are not the hash segment (mdt_phdr_loadable, lines 55-64) and only when `p_filesz > 0` (lines 413-423) [F].
- **Public cross-check on the same generation:** linux-firmware `qcom/qcm2290/adsp.mbn` (WHENCE line 7433; fetched 2026-11-21, md5 `4bd1f8342a7e5071295abf86b319dc28`, 12,826,756 B) parses as ELF32 LE, e_type 2 (EXEC), **e_machine 164 (EM_QUALCOMM_DSP6 / Hexagon QDSP6)**, e_entry 0x91a00000, e_flags 0x66, e_phnum 30: phdr 0 = 1,012 B header-table self-reference (type 0), phdr 1 = 7,856 B hash/metadata (type 0, flags 0x2200000), 28 file-backed PT_LOADs, **phdr 11 = PT_LOAD with p_filesz 0 and p_memsz 15,520 (BSS-only)**, and phdr 29 (last) = PT_LOAD p_filesz 0, p_memsz 3,575,808 (a second, huge trailing BSS) [F, parsed this session].
- **Boot-time request set [I]:** applying the loader rules to the derived capri roles, the kernel at boot would fetch only `adsp2.b02`-`adsp2.b31` minus b11 (29 files) - phdr 0's content rides in the mdt and phdr 1 is the hash segment; b00/b01 exist on the device filesystem because Motorola's packaging tool dumps every segment, but are not fetched at boot.

## The b11 absence is STRUCTURAL, not a census gap

Four independent lines of evidence, all command-verified:

1. **Public generational witness [F]:** the bengal-generation (SM4250) public ADSP build `qcom/qcm2290/adsp.mbn` has program header 11 with p_filesz 0 (BSS-only). A filesz-0 PT_LOAD produces no `.bNN` file under the split convention (kernel requests only when p_filesz > 0, mdt_loader.c line 423). [I] the capri build follows the same generational layout (its own mdt bytes are not in the corpus).
2. **Corpus sweep [F]:** every bengal Moto device skips **exactly** b11, while spanning different maxima - Moto_G10/Moto_E7_Plus b00-b31 (31 segs), Moto_G32/G42/G52 b00-b32 (32), Moto_G30 b00-b33 (33), Moto_G9/G9_Power/G_Power/Defy_2021 b00-b35 (35). The expected shipped set {b00..b(phnum-2)} minus {b11} matches the census **exactly, file for file, on all 10 bengal Moto devices** (python model check, this session), where phnum comes from each device's b00 via Law 1: 1108->33, 1140->34, 1172->35, 1236->37. Law 2 (mdt = b00+b01) also holds exactly on all 10 (e.g. G30: 1,172+8,248=9,420; G9: 1,236+8,344=9,580).
3. **Contrast cohort [F]:** 37 non-bengal corpus devices DO census `adsp.b11`/`adsp2.b11` (OnePlus 7-13 generations, Mi_12/13 generations, Edge_30/Edge_40_Pro, FP5/FP6, Phone_1/2, Poco_F5 family, Moto_G200 SM8350, Nord_4/CE4, Pad_Pro/Pad_2_Pro, Redmi_K60_Pro, Mi_A3). Inside Moto itself the split is clean: G200 (SM8350) has b11; all 10 bengal devices lack it.
4. **Size anchors [F]:** `adsp2.b09` (4,828 B) and `adsp2.b10` (260 B) have identical sizes across three independent bengal builds - capri, guam (Moto_E7_Plus) and the public QCM2290 monolith (phdr 9 = 4,828, phdr 10 = 260) - while all three byte identities differ (md5s distinct), pinning the phdr-index mapping across the generation.

Conclusion: the 35-row census is the complete shipped file set; there is no missing b11 to find. This mirrors and extends the b11-skip observation already recorded for Moto_G9/G30 in #1240.

## Cross-corpus facts

- **The servreg trio is fleet-wide and SoC-agnostic:** Moto_G10's adspr.jsn/adspua.jsn md5s appear on 30 corpus devices each, adsps.jsn on 24 - the exact same bytes Mi_A3 (#1240) carries and md5-matches against the public linux-firmware `qcom/qcm2290/{adspr,adsps,adspua}.jsn` (WHENCE lines 7435-7437). Per #1240's byte-verified schema: sr_version 1.1.1, sr_domain {soc "msm", domain "adsp", qmi_instance_id 74}, subdomains adspr = root_pd, adsps = sensor_pd, adspua = audio_pd; adspua additionally declares the avs/audio service [F, cited from #1240].
- **Bengal sibling spread:** the 10 bengal Moto adsp families hold 35 (G10, E7_Plus), 36 (G32, G42, G52), 37 (G30) or 39 rows (G9, G9_Power, G_Power, Defy_2021) - row count = 35-ish shell + phnum-2-minus-b11 segments, i.e. purely a phdr-count difference, not a census difference [F + I on the phnum mapping].
- **SM4250 twins:** Moto_E7_Plus (guam) shows the identical 35-row shape, identical mdt size (9,260 B), identical b00/b01 sizes (1,108/8,152), identical jsn md5s, but different payload bytes on every segment - total 13,920,844 B, 193,543 B (1.4%) smaller than capri's. Two independent builds, same structure [F].
- **Small-segment sharing:** adsp2.b07 (17,036 B) is byte-identical across 5 Moto devices, adsp2.b17 (11,771 B) across 8, adsp2.b18 (7,008 B) across 11 devices including the non-Moto Phone_1 (SM7325); b10/b14/b19 are shared by Moto_G10 + Phone_1 + Pro_1X. Pro_1X (fxtec, SM6115) carries some of these bytes under BOTH `adsp.bNN` and `adsp2.bNN` names - so the adsp/adsp2 naming is a per-build packaging choice, not a SoC property (Moto_G30 on the same SM6115 uses plain `adsp.*`) [F rows, I on the naming conclusion].
- **Packaging [F]:** the LineageOS capri manifest (fetched 2026-11-21) packages NO adsp2 files at all - the only adsp-related vendor file is `vendor/etc/acdbdata/adsp_avs_config.acdb` (audio calibration). The adsp2 image ships in the modem partition and is extracted from there, matching the census db_path 1:1 and confirming the census as the only completeness witness for this family.

## Interface and ISA facts

- **Motorola's own public trees document the load chain [F]:** `qcom/bengal-audio-overlay.dtsi` on MotorolaMobilityLLC/kernel-devicetree branch `android-11-release-rrb` (the RRB software line matching capri's RRB31.Q1-3-48-24 stock build [I on the line match]) declares, lines 338-343: `&adsp_loader { nvmem-cells = <&adsp_variant>; nvmem-cell-names = "adsp_variant"; adsp-fw-names = "adsp2"; adsp-fw-bit-values = <0x1>; };`. The downstream loader `dsp/adsp-loader.c` (MotorolaMobilityLLC/kernel-msm-5.4-techpack-audio, GPL-2.0, lines 383-472) reads the nvmem `adsp_variant` cell, selects among `adsp-fw-names` by `adsp-fw-bit-values`, and calls `subsystem_get_with_fwname("adsp", priv->adsp_fw_name)` (line 188) - i.e. the audio ADSP subsystem is booted with firmware name **"adsp2"**, which PIL resolves as `adsp2.mdt` + `adsp2.bNN`. Later Motorola audio DTs carry the full filename form (`ukee-audio-mtp.dtsi` line 9: `adsp-fw-name = "adsp2.mdt"`). This explains the family name in the census: **adsp2 is the bengal-generation Moto audio-ADSP image name.**
- **Mainline support state [F]:** torvalds/linux `sm4250.dtsi` (77 lines) merely includes `sm6115.dtsi` and overrides the CPU compatibles to Kryo 240 - all platform nodes are inherited. `sm6115.dtsi` declares `remoteproc_adsp: remoteproc@a400000` with compatible `qcom,sm6115-adsp-pas` (lines 2772-2800), memory-region `pil_adsp_mem` at 0x53800000 size 0x2800000 = 41,943,040 B (40 MiB), glink edge "lpass" with apr audio service and a fastrpc node with compute-cb 3-7 (lines 2877-2912); `qcom_q6v5_pas.c` registers `qcom,sm6115-adsp-pas` (lines 2045-2047). No Motorola capri board file exists upstream [F]; the 40 MiB carve-out fits the 14.11 MiB image with ample headroom [I].
- **Firmware location [I]:** with modem-partition shipping, a booted stock device exposes the image under the firmware mount point (vendor firmware mount of the modem partition, `image/adsp2.*`), which is what the extraction corpus recorded as `motorola/capri/modem/image`; the exact firmware-name string in capri's non-public vendor DT is unconfirmed.
- **ISA [F + honest negative]:** the ADSP on SM4250 is Hexagon 683 with HVX (Qualcomm product brief, fetched 2026-11-21); the public QCM2290 sibling build's e_machine 164 (Hexagon QDSP6) confirms the executable format [F]. The corpus records `isa_identified` EMPTY and `interface_documented=n` on all 35 rows - the segments are honestly un-RE'd here. By size alone the likely code/resource-bearing segments are adsp2.b24 (5,108,316 B, 36.19%), adsp2.b04 (1,796,028 B, 12.72%), adsp2.b15 (1,624,292 B, 11.51%), adsp2.b30 (1,553,040 B, 11.00%) and adsp2.b25 (1,428,493 B, 10.12%) - together 81.55% of family bytes [I - no disassembly performed].

## Honest negatives ([OPEN])

- No payload of this device was fetched or analyzed (metadata-only; the 32 device-signed files exist in the corpus as hashes only). The only binary touched was the public linux-firmware QCM2290 build, and only its ELF header table.
- The capri phdr-level facts (e_phnum 33; phdr 11 BSS-only; phdr 32 trailing BSS) are derived from two exact size laws plus the public generational witness - not from capri's own mdt bytes. A program-header dump of the real `adsp2.mdt` remains the direct proof and is [OPEN].
- No Hexagon ISA proof: no segment was disassembled; Hexagon 683 is from the SoC spec, not from the blobs.
- The `adsp_variant` nvmem cell / `adsp-fw-bit-values = <0x1>` semantics (which fuse selects which firmware variant) are not traced further.
- Mainline boot of the ADSP on capri is untested: no sm4250 motorola board DT exists upstream, and the vendor firmware-name string is unknown [OPEN].
- The QCM2290 `adsp.mbn` is a different firmware drop than capri's image; shared code segments between them are plausible (same generation) but unverified [OPEN].

## What would upgrade this finding

1. Extract the stock modem partition (fastboot image or OTA payload), byte-verify all 35 census md5s, and dump the ELF program headers of `adsp2.mdt` (9,260 B): expect e_phnum 33, phdr 11 with p_filesz 0/p_memsz ~15,520, phdr 32 with p_filesz 0, phdr 1 as the hash segment - that would convert the structural-b11 [I] into a direct [F].
2. Disassemble adsp2.b24/b04/b15 with a public Hexagon toolchain (Ghidra Hexagon module or a Capstone fork) and record the Hexagon ISA revision - fills `isa_identified`.
3. Trace the `adsp_variant` nvmem cell to its fuse definition in Motorola's public kernel trees to explain `adsp-fw-bit-values = <0x1>`.
4. Diff capri's payloads against the public `qcom/qcm2290/adsp.mbn` segment table to test generational code sharing (the servreg trio is already proven identical upstream).

## RULE 0 record

- CLAIM posted 2026-11-21T10:28:00Z as the first comment (confirmed first by re-read at 10:28:37Z; no other agent claimed).
- SEARCH (Gate -1) and DELTA (Gate 0) posted 2026-11-21; work started only after both.
- All census numbers are awk/python outputs on coverage-matrix.csv at feat/open-device-site 9119bd4, this session; all web fetches dated 2026-11-21 (WHENCE line numbers and raw-file paths recorded per fetch; the QCM2290 adsp.mbn ELF parse was performed with stdlib python3 -I on the downloaded public file, hashes and header fields only).

Nothing in this document is legal advice; no proprietary payload bytes were fetched, stored or committed - only sizes, md5s, ELF header metadata of a public build, public-source quotations and arithmetic derivations.
