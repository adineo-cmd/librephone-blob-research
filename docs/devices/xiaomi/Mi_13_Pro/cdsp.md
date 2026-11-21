# xiaomi Mi_13_Pro (nuwa) - `cdsp` family status (21 rows - PRESENT, census-complete; current-generation split-ELF PIL grammar: `cdsp.mdt` + 15 segments + `cdsp_dtb` companion split image + `cdspr.jsn`, with kernel-side PAS proof for the companion)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1234](https://github.com/adineo-cmd/open-device/issues/1234)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows; worktree checkout of feat/open-device-site at 87cfee5), `upstream-contribution/blob-database/device-inventory.csv`, torvalds/linux master `arch/arm64/boot/dts/qcom/sm8550.dtsi` + `drivers/remoteproc/qcom_q6v5_pas.c` (fetched 2026-11-21), linux-firmware WHENCE (git.kernel.org plain/WHENCE, fetched 2026-11-21), the LineageOS `android_device_xiaomi_nuwa` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21), public spec pages (2026-11-21), sibling in-repo docs docs/devices/xiaomi/Mi_12S/cdsp.md (#1180) and docs/devices/xiaomi/Mi_13/adsp.md (#1222). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: PRESENT - the `cdsp` family on Mi_13_Pro is a complete, current-generation Qualcomm signed split-ELF PIL image plus its DTB companion: 21 rows, 7,022,211 B, 21 distinct md5s, all at corpus path `xiaomi/nuwa/modem/image`, priority P3, db_type COMPUTE (20) / UNKNOWN (1). The 21 rows are `cdspr.jsn` (513 B) + `cdsp.mdt` (5,084 B) + 15 `cdsp.bNN` segments (b00-b13, b15; 7,008,014 B) + the 4-file `cdsp_dtb` companion (`cdsp_dtb.mdt` 4,044 B + b00 148 + b01 512 + b02 3,896 = 8,600 B). This is not a census gap: the identical 21-file grammar appears on all 13 current-generation census devices, the extract that produced this census is marked `completes`, and the LineageOS nuwa packaging manifest ships zero cdsp-firmware entries - the split-PIL image rides the modem partition, which is where the census captured it. The `cdsp_dtb` companion is not a guess: mainline `qcom_q6v5_pas.c` names `dtb_firmware_name = "cdsp_dtb.mdt"` with `dtb_pas_id = 0x25` for `qcom,sm8550-cdsp-pas`, and `sm8550.dtsi` reserves the 512 KiB `q6_cdsp_dtb_mem` region the node consumes.**

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi 13 Pro (China 2210132C, global 2210132G); build codename `nuwa` | `device-inventory.csv` (`build_codename=nuwa`) [F]; GSMArena + mi.com spec pages (2026-11-21) [F] |
| SoC | Qualcomm **SM8550 Snapdragon 8 Gen 2**; Adreno 740; Hexagon V73 DSP. **The matrix and inventory soc cells are EMPTY and are corrected here** - flag for the lead | public spec pages (2026-11-21) [F]; codename-to-SoC corroborated by the byte-share sets below [I] |
| released | December 2022 (announced 2022-12-11, released 2022-12-14 China; global early 2023) | public spec pages (2026-11-21) [F] |
| stock base | `OS2.0.215.0.VMBCNXM` (build id AQ3A.240912.001) | LineageOS nuwa `proprietary-files.txt` header "All proprietary files ... are taken from Xiaomi 13 Pro AQ3A.240912.001 OS2.0.215.0.VMBCNXM" (fetched 2026-11-21) [F] |
| census scope | 706 device rows / 1,484,043,637 B; cdsp = 21 rows (2.97%) / 7,022,211 B (0.473%) | coverage-matrix.csv + device-inventory.csv; shares via python3 [F] |
| priority / extract | P3; `extract_status_22.2 = completes` | device-inventory.csv [F] |

The task briefing's row count (21) is confirmed exactly; the family is cdsp (the title's device/family is authoritative). The SoC guess implied by the SM8550 sibling generation is correct for nuwa - same generation as fuxi (#1222), not the SM8450/8475 generation of the 19-row cdsp grammar (#1180).

## The 21 rows [F]

```
awk -F, '$1=="Mi_13_Pro" && $4=="cdsp"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv | sort
```

All 21 rows: `blob_subfamily` empty, `sha256_if_listed` empty, `isa_identified` empty, `interface_documented = n`, `db_path = xiaomi/nuwa/modem/image`, priority P3, db_type COMPUTE except `cdspr.jsn` (UNKNOWN). All 21 md5s are distinct within the device. `devices` = corpus-wide count of devices carrying that byte identity (md5 sweep, this session):

| file | bytes | md5 (upstream DB) | db_type | devices |
|---|---:|---|---|---|
| cdspr.jsn | 513 | `49003ffcd10ec16dee11caad22b11b42` | UNKNOWN | 30 |
| cdsp.mdt | 5,084 | `f8fa7d176ee4a7d8c5a83edc5daafb1d` | COMPUTE | 1 (nuwa only) |
| cdsp.b00 | 564 | `3fa84f82895eb402a889b66b7023b2a4` | COMPUTE | 4 |
| cdsp.b01 | 6,696 | `f0c7e76005fdce637c5b5f4971705485` | COMPUTE | 6 |
| cdsp.b02 | 1,663,741 | `2374c76b2422a1cbe8dc12014bcdc6fa` | COMPUTE | 4 |
| cdsp.b03 | 1,192 | `6d97cece7ff5467a19c7916da1b47834` | COMPUTE | 6 |
| cdsp.b04 | 2,112,676 | `a9c887f3b84180f835f6409b7d3ea7a3` | COMPUTE | 1 (nuwa only) |
| cdsp.b05 | 118,792 | `365e20ad2b477f81af63594640dca3be` | COMPUTE | 1 (nuwa only) |
| cdsp.b06 | 1,616 | `e2503f6a5491b3341e6e75002c208492` | COMPUTE | 1 (nuwa only) |
| cdsp.b07 | 99,604 | `ca796f329241ae9aebfd3454a3bb11da` | COMPUTE | 4 |
| cdsp.b08 | 2,827,764 | `2d372687495f613e01dbe3c88f2d8adc` | COMPUTE | 1 (nuwa only) |
| cdsp.b09 | 63,937 | `f4e0d2c0d3b7f6094f928affc9606bc8` | COMPUTE | 1 (nuwa only) |
| cdsp.b10 | 4,024 | `c5d6849dac7cf60a78a22c4f17e2b9b6` | COMPUTE | 4 |
| cdsp.b11 | 85,968 | `5cebe1f7b26adb874434fd1d32ac95d7` | COMPUTE | 4 |
| cdsp.b12 | 4,632 | `93ca932c20d51b3585608f493394a702` | COMPUTE | 4 |
| cdsp.b13 | 12,288 | `c37aa2a09f2494b9c954fde594408f86` | COMPUTE | 4 |
| cdsp.b15 | 4,520 | `3f696083a9ec298dfdf9058609de9642` | COMPUTE | 1 (nuwa only) |
| cdsp_dtb.mdt | 4,044 | `68b04541d8b215f5584cc8b266ba620d` | COMPUTE | 1 (nuwa only) |
| cdsp_dtb.b00 | 148 | `a4fa90de9560c7d36a8b72e8b5d457d0` | COMPUTE | 6 |
| cdsp_dtb.b01 | 512 | `8ef92426e900be5e4cda260bcd8cd506` | COMPUTE | 6 |
| cdsp_dtb.b02 | 3,896 | `5508e265f09351ac46f966e749d03310` | COMPUTE | 1 (nuwa only) |

Sum checks (python3, before writing): 15 cdsp.bNN segments = 7,008,014 B; split-PIL half = 5,084 + 7,008,014 = 7,013,098 B; cdsp_dtb half = 4,044 + 148 + 512 + 3,896 = 8,600 B; + jsn 513 = 7,022,211 B total. The two largest segments (b08 2,827,764 + b04 2,112,676 = 4,940,440 B) are 70.4% of family bytes.

## Container layout

- **Grammar [F]:** `cdspr.jsn` + `cdsp.mdt` + `cdsp.b00..b13` + `cdsp.b15` + `cdsp_dtb.mdt` + `cdsp_dtb.b00..b02`, one directory (`xiaomi/nuwa/modem/image` - the upstream DB's path taxonomy, not necessarily the on-device path).
- **Interpretation [I]:** `cdsp.mdt` is the ELF header + program-header table of a Qualcomm signed split ELF; each `cdsp.bNN` is the load segment numbered by its program-header index; `cdspr.jsn` is the JSON servreg/protection-domain descriptor the PIL loader consumes; `cdsp_dtb.mdt` + its 3 segments are a second, independently loaded split image (see the PAS proof below - the kernel loads it separately, so "dtb companion" describes its name, not necessarily a plain device-tree blob).
- **Kernel-side proof of the two-image grammar [F]:** mainline `drivers/remoteproc/qcom_q6v5_pas.c` (torvalds master, fetched 2026-11-21) defines `sm8550_cdsp_resource` (line 1719): `firmware_name = "cdsp.mdt"`, **`dtb_firmware_name = "cdsp_dtb.mdt"`**, `pas_id = 18`, **`dtb_pas_id = 0x25`**, `minidump_id = 7`, `crash_reason_smem = 601`, proxy power domains `cx`/`mxc`/`nsp`; compatible `qcom,sm8550-cdsp-pas` (line 2070). The SM8550 CDSP loader consumes exactly the two signed images the nuwa census captures, each under its own PAS id. This upgrades the corresponding [I] in the fuxi adsp doc (#1222): the `*_dtb` companion is a kernel-loaded, TrustZone-authenticated PAS image, not merely a devicetree sidecar.
- **Device tree [F]:** mainline `arch/arm64/boot/dts/qcom/sm8550.dtsi` (fetched 2026-11-21): `remoteproc_cdsp: remoteproc@32300000`, compatible `qcom,sm8550-cdsp-pas`, `memory-region = <&cdsp_mem>, <&q6_cdsp_dtb_mem>` (line 6056); `cdsp_mem: cdsp-region@9c900000` (32 MiB, no-map, line 968); **`q6_cdsp_dtb_mem: q6-cdsp-dtb-region@9e900000` (512 KiB, no-map, line 973)** - the 8,600 B companion image fits the 512 KiB reservation [I]; there is also `cdsp_secure_heap_mem` (0x4600000 = 70 MiB, no-map, line 906). The glink edge runs `fastrpc` on channel `fastrpcglink-apps-dsp` with 7 compute-cb nodes (`compute-cb@1`..`@7`, lines 6085+).
- **The b14 and b17 gaps are grammar properties of this generation, not census omissions [F]:** nuwa runs b00..b13 then b15 (b14 absent) and has no b17. Corpus-wide: `cdsp.b16` = 0 rows in all 33,917 (re-confirms #1180); `cdsp.b14` exists on exactly 17 older-generation devices (4,504 B on the nine 19-row devices, 1,436/1,564 B on the eight 18-row devices); `cdsp.b17` exists on exactly 9 devices (the 19-row generation, 3,836-4,616 B). The 13 current-generation devices carry neither. Segment numbering tracks the source ELF program-header layout, so skipped indices reflect the image build [I].
- **jsn is a real shipped artifact [F]:** linux-firmware WHENCE records `RawFile: qcom/sdm845/cdspr.jsn` (line 7507), `qcom/sm8250/cdspr.jsn` (7523), `qcom/qcm6490/cdspr.jsn` (7452) beside their cdsp.mbn images, with Hexagon build-chain tags such as `CDSP.HT.2.3.c1-00076-SM8250-1` (7522); cited from #1180, re-verified in WHENCE this session.

## Census completeness - proven against the LineageOS packaging manifest [F]

- `LineageOS/android_device_xiaomi_nuwa` `proprietary-files.txt` (lineage-22.2, fetched 2026-11-21, stock base OS2.0.215.0.VMBCNXM) contains **zero** `cdsp.mdt` / `cdsp.bNN` / `cdsp_dtb.*` / `cdspr.jsn` entries and zero `.img` partition images: LineageOS does not package the split-PIL DSP firmware into the vendor tree; on nuwa it lives in the device's modem partition, which is where the census's 21 `modem/image` rows come from (the Xiaomi/OnePlus packaging pattern recorded in #1180/#1222).
- The manifest's cdsp-named content is all userspace: 9 fastrpc skel libraries (`odm/lib/rfsa/adsp/libmialgo_ell_cdsp_skel.so`, `libmialgo_night_align_cdsp_skel.so`; `vendor/lib/rfsa/adsp/` via `odm/mount/camera/lib/rfsa/adsp/`: `libhdr_cdsp_skel.so`, `libmialgo_basic_cdsp_skel.so`, `libmialgo_ldc_cdsp_skel.so`, `libmialgo_mc_bokeh_cdsp_skel.so`, `libmialgo_rawhdr_cdsp_skel.so`, `libmialgo_rfs_cdsp_skel.so`, `libmialgo_slow_motion_cdsp_skel.so`) plus `libxmi_high_dynamic_range_cdsp.so` and the `libqvr_cdsp_driver_stub.so` / `libqvr_cam_cdsp_driver_stub.so` stubs. **None of these is in the census** - the cdsp family here is the firmware payload view, not the shared-library view (same contrast as #1180/#1222) [F].
- The same manifest ships the 52 bm3 HTP graph payloads and the 2 misound audio bins that #1222 records for nuwa's adsp side; they belong to the adsp family analysis and are only noted here as extract-scope context [F].

## Cross-corpus facts

1. **The 21-file grammar is exactly 13 devices, and nuwa is one of them [F].** `awk '$6=="cdsp_dtb.mdt"'` returns one row for each of: Edge_40_Pro, FP6, Mi_13, Mi_13_Pro, Nord_4, Nord_CE4, OnePlus_11_5G, OnePlus_12, OnePlus_13, Pad_2_Pro, Pad_Pro, Poco_F6_PRo, Redmi_K60_Pro - the same 13 devices that carry 21 cdsp rows (corpus cdsp total: 940 rows / 63 devices; python-checked 13x21 + 9x19 + 8x18 + 19x12 + 11x11 + 3 = 940). The companion grammar is the current generation, not SM8550-exclusive: it spans SM8550 (fuxi, nuwa, socrates, vermeer, rtwo, salami), SM8650 (OnePlus_12/waffle), SM8750 (OnePlus_13/dodge), SM7675 (Nord_4/avalon), SM7550 (Nord_CE4/benz), SM7635 (FP6) [I on the unverified SoC labels; rtwo/salami SM8550 are inventory cells [F], nuwa/fuxi web-verified [F]].
2. **Grammar evolution, one table [F]:** 18-row generation (8 devices: mdt + b00-b15 incl. b14 + jsn - Edge_30/Edge_30_Fusion/FP5/Moto_G200/OnePlus_9/OnePlus_9_Pro/OnePlus_9RT/Phone_1); 19-row generation (9 devices: adds b17 - Mi_12, Mi_12_Pro, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro; the #1180 grammar); 21-row generation (13 devices: drops b14+b17, adds the 4-file `cdsp_dtb` companion: 19 + 4 - 2 = 21, python-checked). Older 12/11-row grammars (19 + 11 devices) and three Pixel rows (a lone 7,660 B `cdsp.mdt` each - Pixel_4A_5G, Pixel_5, Pixel_5A; a census gap on those devices, not a grammar) complete the corpus.
3. **Byte share by group [F]:** 9 of 21 rows (5,142,329 B = 73.2%) are nuwa-exclusive: `cdsp.mdt`, `cdsp_dtb.mdt`, b04, b05, b06, b08, b09, b15, `cdsp_dtb.b02`. Seven segments (b00, b02, b07, b10, b11, b12, b13 = 1,870,821 B) are shared by exactly the four Xiaomi-family SM8550 devices {Mi_13, Mi_13_Pro, Poco_F6_PRo, Redmi_K60_Pro}. Four rows (b01, b03, `cdsp_dtb.b00`, `cdsp_dtb.b01` = 8,548 B) extend to a 6-device set {+Edge_40_Pro, OnePlus_11_5G} - **the identical 6-device set that shares `adsp_dtb.b00`/`b01` on the fuxi side (#1222)**, though the bytes differ (adsp_dtb.b00 and cdsp_dtb.b00 are both 148 B but carry different md5s). `cdspr.jsn` rides the 30-device fleet `49003ffc...` recorded in #1180 (Mi_13_Pro is a member) [F].
4. **The personalized-OS pattern holds on cdsp exactly as on adsp [F].** fuxi and nuwa carry the same 21-file set with identical per-file sizes, and 12 rows are byte-identical between them (jsn, b00, b01, b02, b03, b07, b10, b11, b12, b13, `cdsp_dtb.b00`, `cdsp_dtb.b01`); the 9 differing rows are the same 9 identities that are device-exclusive on each side (nuwa's by the md5 sweep; fuxi's `cdsp.mdt` `7be1036c...`, `cdsp_dtb.mdt` `b62c8092...`, b04 `0b48e3a4...`, b15 `32289df7...` verified Mi_13-exclusive this session). Per-device vendor personalization touches the OS image core, while the platform-generic segments stay fleet-shared - the #1222 adsp variant-matrix prediction, now confirmed on cdsp.
5. **Size law [F]:** nuwa's cdsp total (7,022,211 B) is 812,559 B smaller than mayfly's 19-row image (7,834,770 B, #1180), and `cdsp.mdt` grew from 4,764 to 5,084 B (+320) - a bigger program-header table consistent with a restructured, companion-split image [I]. The 513 B `cdspr.jsn` build is byte-identical from SM8450 through SM8750 generations (30-device fleet, #1180 + this sweep) [F].
6. **linux-firmware ships no SM8550 cdsp image [F]:** WHENCE (fetched 2026-11-21) lists only `qcom/sm8550/a740_zap.mbn` (line 7301) and two SM8550 tplg files (10914-10915) for the platform. The `cdsp_dtb` companion construct is public one generation later and on other platforms: `qcom/sm8750/cdsp.mbn` + `cdsp_dtb.mbn` + `cdspr.jsn` (7704-7707), `qcom/x1e80100/cdsp_dtb.mbn` (7552), `glymur/cdsp_dtb.mbn` (7608), `hawi/cdsp_dtb.mbn` (7621), `kaanapali/cdsp_dtb.mbn` (7634), and `cdsp_dtbs.elf` for x1e80100 device dirs (7559, 7581). Phone-vendor cdsp builds are device firmware; nuwa's is captured only by this census.

## Interface facts

- **PAS loader [F]:** `qcom,sm8550-cdsp-pas` -> `sm8550_cdsp_resource` (details above): pas_id 18 for `cdsp.mdt`, dtb_pas_id 0x25 (37) for `cdsp_dtb.mdt`, minidump_id 7, crash_reason_smem 601. The kernel hands both signed images to TrustZone for verify-and-boot; the DTB image is loaded and authenticated separately from the OS image [F for the driver facts; the authentication mechanics are the driver's PAS design, not payload-derived].
- **FastraPC surface [F]:** the sm8550.dtsi cdsp glink edge exposes `fastrpc` on `fastrpcglink-apps-dsp` with `compute-cb@1`..`@7` (7 nodes, non-secure domain); nuwa's 9 `*_cdsp_skel.so` userspace libraries (manifest, fetched 2026-11-21) are the camera-pipeline clients of exactly this surface [I on the client mapping].
- **linux-firmware precedent [F]:** the split `cdsp.mbn` + `cdspr.jsn` + (from this generation on) `cdsp_dtb.mbn` triple is what mainline linux-firmware packages for qcm6490/qcs615/sdm845/sm8250/x1e80100/sm8750 (WHENCE lines cited above) - nuwa's census set is the same artifact family in split-PIL (mdt+bNN) rather than monolithic-mbn form [I on the form difference].
- **ISA/interface documentation status [F]:** `isa_identified` empty and `interface_documented = n` on all 21 rows - honestly un-RE'd. The DSP ISA generation is Hexagon V73 (public SoC specs + vendor skel naming), but no instruction-level fact about any of these 21 blobs is claimed here [N]. No public reverse engineering of this cdsp build exists (web + GitHub code searches, 2026-11-21; see RULE 0).

## Honest negatives

- No payload access: the ELF program-header layout, the signing/MBN container version, the per-phdr hash-slot metadata (the in-repo pil-metadata-sweep covers SM8250/SDM845 only), and the CDSP build tag (the `CDSP.HT.x.y` pattern WHENCE records for board SoCs) are [OPEN] for SM8550. The census records md5/size/path only.
- The mechanism of the b14/b17 skips in this generation is [I] (program-header layout); payload verification [OPEN]. The corpus-wide cdsp.b16 absence extends to all 63 cdsp devices (#1180 + re-check).
- What `cdsp_dtb.mdt` actually carries (which DTBs, or other boot metadata) and whether the 512 KiB `q6_cdsp_dtb_mem` reservation is its load target is consistent-but-unproven. [I] [OPEN]
- The `cdspr.jsn` subdomain strings are not decoded; only its size (513 B), 30-device byte-identity span and public WHENCE analogs are recorded. [OPEN]
- Physical partition mapping [OPEN]: the LineageOS nuwa manifest ships no `.img` partition images, so the carrier (modem vs dsp partition) is inferred from the `modem/image` census path and the #1180/#1222 packaging pattern. [I]
- Pad_Pro (caihong) and Pad_2_Pro (erhai) sit in the 13-device grammar group but have empty SoC cells and their inventory vendor cell (`oneplus`) conflicts with the Xiaomi-family codename style; their SoCs are unverified [OPEN; flag for the lead]. OnePlus_12R - a member of the adsp bm3 8-device share group (#1222) - has **zero** cdsp rows corpus-wide, extending #1222's OnePlus_12R census-scope question to cdsp [F; scope question for the extract, not a device property [I]].
- Hashes are upstream-DB md5s (`md5_db`); no sha256 is recorded for any of the 21 rows [F].

## What would upgrade this finding

1. Payload fetch (nuwa firmware package or a LineageOS nuwa build): parse `cdsp.mdt` + `cdsp_dtb.mdt` program headers - the first SM8550 cdsp metadata decode; settles the hash-width question against the SM8250 SHA-384 precedent, confirms the b14/b17 skip mechanics, and reads the `CDSP.HT` build tag.
2. Decode the 513 B `cdspr.jsn` schema and diff it against the public servreg samples - one decode covers the 30-device fleet, since the file is byte-identical from SM8450 to SM8750 generations.
3. Byte-diff the four Xiaomi-shared segments (b00, b02, b07, b10-b13) across fuxi/vermeer/socrates builds to test whether shared md5 means shared code modules or common tooling output.
4. Explain the 4-vs-6-device share split (why b01/b03/`cdsp_dtb.b00`/`b01` extend to rtwo/salami while the rest stay Xiaomi-only) - build-line granularity vs vendor personalization.
5. Resolve the OnePlus_12R zero-cdsp-row census scope and the Pad_Pro/Pad_2_Pro SoC cells.

## RULE 0 record (2026-11-21)

Queries recorded in the SEARCH + NO-PRIOR-ART comments on this issue. Checks: GitHub code search `"cdsp_dtb.mdt" NOT repo:adineo-cmd/open-device` -> 533 hits, all format-level (qcom_q6v5_pas.c forks, sm8550 device trees, a Lenovo Y700 port patch); `"nuwa" "cdsp" NOT repo:adineo-cmd/open-device` -> packaging manifests only (TheMuppets/proprietary_vendor_xiaomi_nuwa, crdroidandroid/android_device_xiaomi_nuwa); web `"Xiaomi 13 Pro" OR "nuwa" cdsp firmware "cdsp.mdt" reverse engineering hexagon` -> ROM/flash pages and generic Hexagon RE tooling (programa-stic/hexag00n, linux-msm/hexagon-dsp-binaries) only; web `Xiaomi Mi 13 Pro codename nuwa Snapdragon 8 Gen 2 SM8550 specs` -> identity confirmed (2210132C/G, SM8550, 2022-12-14); torvalds `sm8550.dtsi` + `qcom_q6v5_pas.c` + linux-firmware WHENCE + LineageOS android_device_xiaomi_nuwa proprietary-files.txt fetched 2026-11-21. Nobody documents the Mi_13_Pro cdsp census; no device-level prior art exists. Format-level facts (mainline PAS driver, DT nodes, WHENCE analogs, in-repo #1180/#1222 findings) are cited, not rebuilt.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata (sizes, md5s, counts, paths) plus public kernel sources, manifests and specs.
