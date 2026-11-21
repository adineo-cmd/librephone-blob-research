# xiaomi Mi_12S_Ultra - `cdsp` family status (19 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1198](https://github.com/adineo-cmd/open-device/issues/1198)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site a7b7b0e) + `device-inventory.csv`, in-repo `research/cdsp-fleet/census.md` + `container.md` + `audit.md` (fleet cdsp census and byte-measured container grammar), `research/laptop/qualcomm-pil-manifest-family.md` (jsn/PDR manifests), [LineageOS wiki thor](https://wiki.lineageos.org/devices/thor) + [LineageOS/android_device_xiaomi_thor](https://github.com/LineageOS/android_device_xiaomi_thor) (fetched 2026-11-21), `android_device_xiaomi_thor/lineage-22.2/proprietary-files.txt` (fetched 2026-11-21), torvalds/linux `drivers/soc/qcom/mdt_loader.c` (cited via container.md). Evidence classes: [F] fact (command output or cited source) / [I] inference (labeled) / [N] honest negative. No payloads fetched; every byte figure below is upstream-declared metadata, sums verified with `python3 -c` before writing.

**Verdict: the cdsp family is PRESENT and structurally complete on Mi_12S_Ultra** - 19 rows, 7,834,738 B declared: the canonical split-PIL shape of the SM8450/SM8475 generation (mdt + 17 payload segments b00-b15 and b17 + cdspr.jsn manifest), all under `xiaomi/thor/modem/image`. This is not a census gap and not a structural absence: the 19-row shape is the maximum for this generation and is shared file-for-file with 8 sibling devices. 10 of the 19 md5s are unique to thor; 9 are byte-identical (per the upstream DB) inside a 9-device SM8450/SM8475/SM7475 cluster. The only ISA evidence is generation-level (SM8475 compute DSP = Hexagon v69 per the public QNN ecosystem); thor's own bytes are unmeasured.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi 12S Ultra; codename `thor` | `device-inventory.csv` (build_codename=`thor`) [F]; [LineageOS wiki](https://wiki.lineageos.org/devices/thor) (2026-11-21) [F] |
| SoC | Qualcomm **SM8475 Snapdragon 8+ Gen 1** (Adreno 730), released 2022-07 | [LineageOS wiki](https://wiki.lineageos.org/devices/thor) + [device tree](https://github.com/LineageOS/android_device_xiaomi_thor) (2026-11-21) [F]. **The upstream inventory's SoC cell is EMPTY for this device** (one of the empty-cell devices flagged by the standing method, alongside milanf/a21s/a71/gauguin/gta4xl); corrected here - the shared matrix stream is lead-owned |
| in-corpus SoC anchor | sibling Phone_2 (Nothing) carries `Qualcomm SM8475 Snapdragon 8+ Gen1` in its cdsp rows' soc cells [F] and shares 4 byte-identical segment md5s with thor (b01, b03, b09, b15) [F] - the shared segments are the SM8475-generation build per the DB's own labelling |
| census scope | 841 rows in 9 families (adsp 67, boot 14, bt 1, cdsp 19, gpu 6, modem 39, other 425, tz 91, wifi 179; sum 841 [F]) | coverage-matrix.csv [F] |

## Decomposition [F]

Source query: `awk -F, '$1=="Mi_12S_Ultra" && $4=="cdsp"{print $6"|"$7"|"$8"|"$13"|"$14}' upstream-contribution/blob-database/coverage-matrix.csv`. All 19 rows sit on `xiaomi/thor/modem/image`; db_type COMPUTE for the 18 split files, UNKNOWN for `cdspr.jsn`; `interface_documented=n`, priority `P3`, `isa_identified` and `sha256` empty on all 19 [F].

| file | bytes | md5 (upstream DB) | sharing span (devices, same md5) |
|---|---:|---|---|
| cdspr.jsn | 513 | `49003ffcd10ec16dee11caad22b11b42` | 30 |
| cdsp.mdt | 4764 | `8f7c010c65340e478b180db8c3d6f724` | 1 (unique) |
| cdsp.b00 | 628 | `fff690163b01f269c88fd133e8e40d9f` | 1 (unique) |
| cdsp.b01 | 7464 | `3209c0463dc7ffcdeeb05b21ed67bf61` | 9 |
| cdsp.b02 | 1581865 | `3307465f9b5ffe74956e69b547f6db17` | 7 |
| cdsp.b03 | 1172 | `14eb07f574826b7c3504734684d29572` | 9 |
| cdsp.b04 | 220 | `4624f0a049bb354e5cb3e26145842438` | 1 (unique) |
| cdsp.b05 | 2045540 | `3590be9db07ee50692daaa05765fb484` | 1 (unique) |
| cdsp.b06 | 160 | `24d32da5da02410525cb74424c38a21a` | 1 (unique) |
| cdsp.b07 | 2674696 | `67087a35141233942a78c9730e0440bb` | 1 (unique) |
| cdsp.b08 | 1552 | `d00850f92d182ba5b8edf4c385aa044a` | 1 (unique) |
| cdsp.b09 | 93460 | `6ac427c5351d7c6231cdc133f8f05a52` | 9 |
| cdsp.b10 | 1285928 | `b77a66343f860af53a0e9b82c2fcce84` | 1 (unique) |
| cdsp.b11 | 32232 | `c5d6f8d440498f3c7a5f9f7c72c04ba1` | 1 (unique) |
| cdsp.b12 | 2896 | `fdc5f5a759c421aad8b10b64fc05ac76` | 6 |
| cdsp.b13 | 80720 | `6ba66561f962d2351d3b8ec819056c9d` | 8 |
| cdsp.b14 | 4504 | `5c3eb8e5c751cad2017d8b5abb4259f9` | 8 |
| cdsp.b15 | 12288 | `be34bb139199359e4123264694adcbe1` | 9 |
| cdsp.b17 | 4136 | `20d73ebe4f40e4e20ce0836ca55b18e7` | 1 (unique) |

Sum checks [F, python-verified]: 19 rows; total 7,834,738 B; the 17 payload segments total 7,829,461 B; the 4 largest segments (b02 1,581,865 + b05 2,045,540 + b07 2,674,696 + b10 1,285,928) total 7,588,029 B = 96.85% of the family. Two absent names matter [F]: no `cdsp.b16` (absent corpus-wide - 0 of the 940 cdsp rows in the current matrix) and no `cdsp_dtb.*` (a 13-device feature of the SM8550 generation per `census.md`, absent here).

## Container layout [F precedents, I arithmetic]

The split-PIL grammar is established for this family on two byte-measured devices (`research/cdsp-fleet/container.md`, independently audited in `audit.md`): `.mdt` = `b00 ++ b01` (ELF header + program-header table, then the HASH/certificate segment); every loadable segment with `p_filesz > 0` ships an exactly-sized `.bNN`; zero-`p_filesz` segments ship no file; the loader is `drivers/soc/qcom/mdt_loader.c` (GPL-2.0). Those measurements were on SM8250 (`instantnoodle`, e_phnum 13, e_flags 0x066) and SDM845 (`enchilada`, e_phnum 12, e_flags 0x065) - not on thor.

A new corpus-wide size law strengthens the thor reading [I, derived from declared sizes, validated on the two byte-measured devices]:

- `cdsp.b00` (the header+phdr-table segment, measured `e_ehsize + e_phnum*e_phentsize` = 52 + 13*32 = 468 on instantnoodle) takes exactly **5 declared values across the fleet's 60 unwrapped instances: 436, 468, 564, 596, 628** - each exactly `52 + k*32` for k = 12, 13, 16, 17, 18 [F values, python-verified; I mapping to phdr counts].
- thor's `cdsp.b00` = 628 B implies an **18-entry program-header table**, so phdr indices 0..17, with the missing `b16` = phdr[16] being the zero-`p_filesz` segment (no file, per the measured rule) and `b17` the last segment [I]. The 8 sibling devices of the 19-row shape share b00 = 628 [F] and the same arithmetic reading.
- Cross-check [F]: OnePlus_8's 12 cdsp rows in the current matrix (b00 468, b01 7192, b02 235420, b03 105980, b04 1076, b05 2803308, b06 83426, b08 830592, b09 2800, b11 59156, mdt 7660, jsn 403) equal the byte-measured instantnoodle table in container.md section 0 exactly - the matrix chain and the byte chain are the same data.
- thor's `cdsp.mdt` (4764 B) is the median mdt of the 17-segment group in `census.md`'s group table (4464-5244, median 4764) [F].

## Cross-corpus facts

- **cdspr.jsn identity [F]:** md5 `49003ffc...` is the 513-byte variant of the fleet-wide 2-value file (`census.md` section C: 30 devices + 30 devices; the 403-byte variant is the other value). `research/laptop/qualcomm-pil-manifest-family.md` fetched and md5-verified this exact file from public repositories, with thor in its 17-device byte-verified set: it is a **PDR service-registry manifest** (not an image manifest) declaring domain `msm/cdsp/root_pd`, QMI instance 76, service `tms/servreg`; the 403/513 split is one optional `dcomment` field and the documents are equal after dropping it. Mainline does not read these files - `drivers/soc/qcom/qcom_pd_mapper.c` ships the same table as C; userspace `pd-mapper` does (BSD-3-Clause `linux-msm/pd-mapper`).
- **9-device generation cluster [F]:** Mi_12 (cupid), Mi_12_Pro (zeus), Mi_12S (mayfly), Mi_12S_Pro (unicorn), Mi_12S_Ultra (thor), Mi_12T_Pro (diting), Phone_2, Poco_F5 (marble), Poco_F5_Pro (mondrian) carry the identical 19-file set (sorted-filename checksums equal; python-verified). md5-sharing inside it: b01/b03/b09/b15 span all 9; b13/b14 span 8 (no Phone_2); b02 spans 7 (no Mi_12_Pro); b12 spans 6 (no Mi_12_Pro, Mi_12S_Pro, Phone_2) - a mixed-signature pattern consistent with per-device signed builds wrapping shared payload segments [I].
- **b17 is the generation's private segment [F]:** census.md records b17 reach = 9 devices with 9 distinct md5s (no shared cluster at all); those 9 devices are exactly this cluster, and thor's b17 is unique among them.
- **The 10 thor-unique md5s [F]:** mdt, b00, b04, b05, b06, b07, b08, b10, b11, b17. The mdt uniqueness matches the fleet pattern (54 of 64 mdt instances unique, no cluster larger than 2 - `census.md` section C).
- **Sibling contrast on the same path [F]:** thor's adsp family at `xiaomi/thor/modem/image` is 28 rows - `adsp.mdt` 5404 B + `b00`-`b25` (b24 absent) + `adspr.jsn` 513 + `adspua.jsn` 703 - the same split-PIL grammar with a larger series; cdsp is the smaller sibling, complete at 19.
- **Provenance [F absence / I]:** the LineageOS thor `proprietary-files.txt` (1191 lines) lists no `modem/image` files at all - the cdsp family is enumerated from the package's firmware/modem image contents (recon.md: the upstream DB is metadata extracted from LineageOS install packages), not from extract-files vendor blobs. The census therefore counts firmware-partition content, which is why thor shows the complete set.

## Present vs census gap

The corpus rule from #1144 (SM-class samsung devices show census GAPS for families riding in the modem image, with OnePlus SM8250 devices as the positive controls) does not apply here: thor's cdsp enumeration is complete, not gapped. The 19-row shape is the generation maximum (census.md per-device file-count histogram: 19 files - 9 devices; 21 files - 13 devices on the SM8550 generation), and the segment indices the fleet reaches (b00-b06, b08 at 61 devices each in the census slice) are all present here. Verdict: PRESENT, structurally complete at the census level; the only structural caveats are the fleet-wide b16 absence (explained above) and the SM8550-only dtb set (not expected on SM8475).

## ISA and interface facts

- `isa_identified` is empty on all 19 rows - honestly un-RE'd per the upstream DB convention [F]. No thor payload byte exists in this repo or upstream (recon.md: the ~70 GB payload corpus lives on the source maintainer's machine, unpublished), so no ELF header, no e_flags nibble, and no packet statistics exist for thor's cdsp [N].
- ISA generation [F, public ecosystem]: SM8475's compute DSP is **Hexagon v69** - the QNN/HTP toolchain targets `hexagon-v69` for SM8450/SM8475 (ExecuTorch Qualcomm backend docs; `ayanoby/hexanima` PITFALLS.md on Xiaomi 12T Pro = SM8475, Hexagon V69; `Panda-Young/unified_model_bench`; `rvc-mobile` - all accessed 2026-11-21). The two byte-measured precedents have the e_flags low nibble equal to the generation number (0x065 = V65 SDM845, 0x066 = V66 SM8250, `container.md` [F]), so thor's cdsp.mdt plausibly carries `0x00000069` [I] - unmeasured, [OPEN].
- Interface [F/I]: the cdsp image is loaded by the kernel PIL/remoteqd path (`mdt_loader.c`), and the compute domain serves userspace via FastRPC (mainline `drivers/misc/fastrpc.c`; public `qualcomm/fastrpc`). thor's vendor tree carries 9 userspace CDSP compute skels under `vendor/lib/rfsa/adsp/` - `libhdr_cdsp_skel.so`, `libmialgo_basic_cdsp_skel.so`, `libmialgo_ell_cdsp_skel.so`, `libmialgo_ldc_cdsp_skel.so`, `libmialgo_mc_bokeh_cdsp_skel.so`, `libmialgo_night_align_cdsp_skel.so`, `libmialgo_rawhdr_cdsp_skel.so`, `libmialgo_rfs_cdsp_skel.so`, `libmialgo_slow_motion_cdsp_skel.so` [F, proprietary-files.txt lines 71-79, fetched 2026-11-21] - name-derived reading: Xiaomi's camera/compute offload modules (HDR, low-light alignment, bokeh, raw HDR, slow motion) run on the CDSP root_pd [I]. None of these skels are in the census CSV: thor's 39 `vendor/lib/rfsa/adsp` rows are 33 `bm2nNN.bin` audio blobs + `hrtf5c.bin` + 5 `misound_*.bin` resources [F].

## Honest negatives

- [OPEN] All 7,834,738 bytes are declared, not measured; thor carries no sha256 in any row, and the upstream corpus is metadata-only (recon.md). No byte of thor cdsp was read or hashed for this note.
- [OPEN] The 18-program-header reading of thor's container is arithmetic on declared sizes, cross-validated on two other devices' bytes; it is not a measurement of thor's own ELF header.
- [OPEN] Hexagon v69 is the public toolchain-generation mapping; thor's `e_flags` ISA nibble is unmeasured and 0x069 is a prediction, not a fact.
- [OPEN] No build/version column exists in the source DB: the 10 thor-unique md5s cannot be ordered in time against the shared cluster, so "unique" means "not observed elsewhere", not "older/newer".
- [OPEN] md5 equality is upstream-trusted (`census.md` honest negative): thor-to-sibling sharing is per the source database, not locally re-hashed.
- [OPEN] The fleet-wide absence of `cdsp.b16` is consistent with the zero-`p_filesz`-no-file rule measured on two devices, but the reason it holds for every build of this generation is unverified.
- [OPEN] Which processes actually execute in thor's `msm/cdsp/root_pd` beyond the 9 camera/compute skels' offload is unestablished; the jsn manifest names only the root domain and the servreg service.

## What would upgrade this finding

1. Payload pass: extract the modem image from a LineageOS thor package and run `research/cdsp-fleet/cdsp_container_probe.py --mdt` on thor's `CDSP.MDT` - measure `e_flags` (expect 0x069 [I]), the 18-entry phdr table, and the `b00 ++ b01 == mdt` identity - the first SM8475 cdsp container map, cross-generational against container.md's V65/V66 rows.
2. Diff the 10 thor-unique payloads against sibling Phone_2 (whose b01/b03/b09/b15 are byte-identical to thor's): localize what the unique files carry (per-device signed hash tables vs rebuilt payloads).
3. Parse thor's 513-byte `cdspr.jsn` directly to confirm the `dcomment` hypothesis for the 513/403 pair on this variant (the laptop note verified the 403-byte copy by bytes; the 513-byte variant's equality claim is currently document-level).

## RULE 0 record (2026-11-21)

Gate -1 and Gate 0 queries are recorded verbatim in the SEARCH and DELTA comments on this issue. Summary: GitHub code search `"cdspr.jsn" language:markdown` - 68 hits, all packaging lists (Qualcomm driver packs, Windows-on-ARM firmware), none thor; `"12S Ultra" "cdsp" path:LineageOS` - 0. Web: identity via LineageOS wiki/device tree; ISA generation via public QNN/HTP projects; no reverse-engineering of this device's cdsp anywhere. In-repo: fleet-level prior art cited, not re-derived; no thor-specific cdsp document existed before this one.

Not legal advice; no proprietary payload accessed or committed - metadata facts plus cited in-repo and public sources only.
