# xiaomi Mi_12_Pro (zeus) - `cdsp` family status (19 rows: present, complete Qualcomm split-ELF PIL image)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1216](https://github.com/adineo-cmd/open-device/issues/1216)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows; worktree checkout of feat/open-device-site at 4dae417) + `device-inventory.csv`, in-repo `research/cdsp-fleet/census.md` + `container.md` + `audit.md` (fleet cdsp census and byte-measured container grammar), sibling device docs [#1180](https://github.com/adineo-cmd/open-device/issues/1180) (mayfly) and [#1198](https://github.com/adineo-cmd/open-device/issues/1198) (thor), [LineageOS wiki zeus](https://wiki.lineageos.org/devices/zeus) + `LineageOS/android_device_xiaomi_zeus` lineage-22.2 `proprietary-files.txt` (both fetched 2026-11-21), mainline kernel facts as fetched in #1180 (torvalds master, 2026-11-21). Evidence classes: [F] fact (command output or cited source) / [I] inference. No payloads fetched or committed; every byte figure is upstream-declared metadata, sums verified with `python3 -c` before writing.

**Verdict: PRESENT - the `cdsp` family on Mi_12_Pro is a complete Qualcomm signed split-ELF PIL image: 19 rows, 7,817,282 B = cdsp.mdt (4,464 B) + 17 cdsp.bNN segments (7,812,305 B) + cdspr.jsn (513 B), all at corpus path xiaomi/zeus/modem/image, priority P3, db_type COMPUTE (18) / UNKNOWN (1). This is not a census gap: the identical 19-file grammar is the 9-device SM8450/SM8475 cluster shape (file-for-file with Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Phone_2, Poco_F5, Poco_F5_Pro), the extract is marked "completes", 9 of the 19 md5s are zeus-unique, and the 10 shared ones ride established corpus clusters. zeus's cdsp.mdt at 4,464 B is the fleet-wide family minimum (64-device reach, `census.md`).**

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi 12 Pro; build codename `zeus` | `device-inventory.csv` (build_codename=`zeus`) [F]; [LineageOS wiki zeus](https://wiki.lineageos.org/devices/zeus) (2026-11-21) [F] |
| SoC | Qualcomm **SM8450 Snapdragon 8 Gen 1**; the inventory soc cell is EMPTY (Mi_12_Pro is one of the 25 empty-soc cdsp devices, `census.md` section D, identified as `zeus` by db_path) and is corrected here from public sources | [LineageOS wiki zeus](https://wiki.lineageos.org/devices/zeus) (2026-11-21) [F] |
| released | 2021-12-31 (China) | [LineageOS wiki zeus](https://wiki.lineageos.org/devices/zeus) (2026-11-21) [F] |
| census scope | 802 device rows (adsp 46, boot 14, bt 1, cdsp 19, gpu 6, modem 39, other 410, tz 91, wifi 176; sum 802 [F, python-verified]); cdsp = 19 rows (2.37%) / 7,817,282 B (0.782% of the 999,339,189 B device census) | coverage-matrix.csv + device-inventory.csv [F] |
| priority / extract | P3; `extract_status_22.2 = completes`; 999,339,189 B device census total | device-inventory.csv [F] |

zeus is one of two SM8450 devices in the 9-device cluster (the other is Mi_12/cupid); the rest are SM8475 (mayfly, unicorn, thor, diting, mondrian, Phone_2 - Phone_2's census soc cell reads `Qualcomm SM8475 Snapdragon 8+ Gen1` [F]) and SM7250-AE (marble/Poco_F5) [I on the mappings, public specs].

## The 19 rows [F]

```
awk -F, '$1=="Mi_12_Pro" && $4=="cdsp"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv
```

All 19 rows sit on `xiaomi/zeus/modem/image`; `interface_documented=n`, priority P3; `sha256_if_listed`, `isa_identified` empty on all 19.

| file | bytes | md5 (upstream DB) | db_type | md5 shared with (corpus-wide span, command-verified) |
|---|---:|---|---|---|
| cdspr.jsn | 513 | `49003ffcd10ec16dee11caad22b11b42` | UNKNOWN | 29 other devices (the 30-device generation cluster) |
| cdsp.mdt | 4,464 | `29fd952eb34cb5bd5ed797b430d8fea3` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b00 | 628 | `d5fdb329df8314ce4f25e438c215968b` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b01 | 7,464 | `3209c0463dc7ffcdeeb05b21ed67bf61` | COMPUTE | 9 devices (cluster quartet set) |
| cdsp.b02 | 1,581,865 | `f26e7083a1f6d4570bc219044b8fd560` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b03 | 1,172 | `14eb07f574826b7c3504734684d29572` | COMPUTE | 9 devices (quartet set) |
| cdsp.b04 | 220 | `cfc9f3b0b862325f79b50aeb3445f776` | COMPUTE | 5: Mi_12, Mi_12S, Mi_12T_Pro, Poco_F5, Mi_12_Pro |
| cdsp.b05 | 2,045,572 | `36e42a7e5970d1b4651e65384914b4f9` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b06 | 160 | `1f72d439f24dd03ded61742bded7c61b` | COMPUTE | 5: same set as b04 |
| cdsp.b07 | 2,674,696 | `7747af3cc551b970dee1f3c7ac3bcf1f` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b08 | 1,552 | `0983dfca9885d44cf2ad71ed310405a3` | COMPUTE | 4: Mi_12, Mi_12S, Poco_F5, Mi_12_Pro |
| cdsp.b09 | 93,460 | `6ac427c5351d7c6231cdc133f8f05a52` | COMPUTE | 9 devices (quartet set) |
| cdsp.b10 | 1,269,032 | `0d479e8d2ce1bba045faad2f0c14ae22` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b11 | 32,240 | `2da98df708339764c132f9534dc3654c` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b12 | 2,896 | `a7664d57b1edcc9a627185b1238bb904` | COMPUTE | unique to Mi_12_Pro |
| cdsp.b13 | 80,720 | `6ba66561f962d2351d3b8ec819056c9d` | COMPUTE | 8: cluster minus Phone_2 |
| cdsp.b14 | 4,504 | `5c3eb8e5c751cad2017d8b5abb4259f9` | COMPUTE | 8: cluster minus Phone_2 |
| cdsp.b15 | 12,288 | `be34bb139199359e4123264694adcbe1` | COMPUTE | 9 devices (quartet set) |
| cdsp.b17 | 3,836 | `57eb0cbe943fc78aadda493008a35f04` | COMPUTE | unique to Mi_12_Pro |

Sum checks [F, python-verified before writing]: 19 rows total 7,817,282 B; the 17 segments (b00..b15 + b17) total 7,812,305 B; mdt + jsn = 4,977 B; the four largest segments (b02 1,581,865 + b05 2,045,572 + b07 2,674,696 + b10 1,269,032) total 7,571,165 B = 96.85% of the family; the 9 zeus-unique md5s carry 7,615,229 B = 97.42%, the 10 shared files 202,053 B = 2.58%; the shared quartet b01+b03+b09+b15 = 114,384 B; b04+b06+b08 = 1,932 B.

## Container layout

- **Grammar [F]:** cdsp.mdt + cdsp.b00..b15 + cdsp.b17 + cdspr.jsn, one directory (`xiaomi/zeus/modem/image` - the upstream DB's path taxonomy, not necessarily the on-device path). Identical 19-file set to the 8 cluster siblings (sorted-filename checksums equal across the cluster, python-verified in #1198; zeus's row set re-verified this session).
- **Split-PIL interpretation [I]:** per the byte-measured laws in `research/cdsp-fleet/container.md` (SM8250 instantnoodle and SDM845 enchilada, independently audited): `.mdt` = `b00 ++ b01` (ELF header + program-header table, then the HASH/certificate segment); every loadable segment with `p_filesz > 0` ships an exactly-sized `.bNN`; zero-`p_filesz` segments ship no file; the kernel loader is `drivers/soc/qcom/mdt_loader.c` (GPL-2.0).
- **zeus's b00 = 628 B [F]** lands on the fleet's 5-value b00 size law (436/468/564/596/628 = `52 + k*32`, #1198): 628 = 52 + 18*32, implying an **18-entry program-header table** [I], phdr indices 0..17, with the missing b16 = phdr[16] the zero-`p_filesz` segment (no file) and b17 the last segment [I]. Not measured on zeus's own bytes.
- **cdsp.mdt 4,464 B is the fleet minimum [F]:** `census.md` per-file reach gives min 4,464 / max 7,980 / median 7,580 over 64 devices, and the 17-segment group table (9 devices) reads min 4,464 / max 5,244 / median 4,764 - zeus holds the group minimum. mayfly/thor (SM8475) carry 4,764 B.
- **The b16 absence is image-specific, not extractor-generic [F]:** `awk -F, '$6=="cdsp.b16"'` over all 33,917 rows returns 0 (re-verified 2026-11-21; corpus-wide per #1180). Contrast from zeus's own census: its **adsp** image at the same path ships `adsp.b16` (280 B) while skipping `adsp.b24` (b25 4,220 B present) - the extractor demonstrably keeps bNN indices when files exist, so cdsp.b16's corpus-wide absence reflects the image builds, not a census fault [I].

## Cross-corpus facts

1. **9-device generation cluster [F]:** Mi_12 (cupid), Mi_12_Pro (zeus), Mi_12S (mayfly), Mi_12S_Pro (unicorn), Mi_12S_Ultra (thor), Mi_12T_Pro (diting), Phone_2, Poco_F5 (marble), Poco_F5_Pro (mondrian) carry the identical 19-file set (established in `census.md` + #1198, python-verified there; zeus's md5 spans re-verified command-by-command this session).
2. **9 zeus-unique md5s = 97.42% of family bytes [F]:** mdt, b00, b02, b05, b07, b10, b11, b12, b17 (7,615,229 B). The mdt uniqueness matches the fleet pattern (59 distinct md5s over 64 devices, `census.md`).
3. **b17 is the generation's private segment [F]:** it reaches only 9 devices in the entire fleet, with 9 distinct md5s (`census.md` segment-index reach b17 -> 9; #1198); zeus's b17 (3,836 B) is one of the nine, unique to zeus. The 21-file SM8550-generation devices (13 devices) are a different grammar with the cdsp_dtb.* set, absent here.
4. **Size-delta anatomy vs mayfly [F + I]:** total 7,817,282 vs 7,834,770 B = **-17,488 B**, fully decomposed: mdt -300, b10 -16,896, b11 +8, b17 -300. Five files are same-size but different-md5 (b00, b02, b05, b07, b12) and ten are byte-identical to the cluster builds. Mixed-signature pattern consistent with per-device signed builds wrapping shared payload modules [I].
5. **Mixed-generation sharing sets [F]:** b04 and b06 span exactly {Mi_12, Mi_12S, Mi_12_Pro, Mi_12T_Pro, Poco_F5} and b08 {Mi_12, Mi_12S, Mi_12_Pro, Poco_F5} - SM8450 (cupid) + SM8475 (mayfly, diting) + SM7250-AE (marble) devices that exclude unicorn/thor/mondrian. Shared prebuilt DSP modules inside per-device signed wrappers is the reading [I].
6. **cdspr.jsn is the fleet 2-value file, 513-B variant [F]:** md5 `49003ffc...` spans 30 devices; #1198 + `research/laptop/qualcomm-pil-manifest-family.md` identify this exact file as a **PDR service-registry manifest** (domain `msm/cdsp/root_pd`, QMI instance 76, service `tms/servreg`), md5-verified from public repositories; mainline `qcom_pd_mapper.c` ships the same table as C.
7. **Sibling contrast at the same path [F]:** zeus's adsp family is 46 rows - 28 at `xiaomi/zeus/modem/image` (adsp.mdt 5,104 B + b00..b23 + b25 with b24 absent + adspr.jsn 513 + adspua.jsn 703) and 18 at `xiaomi/zeus/vendor/lib/rfsa/adsp` (bm2n00..bm2n11 + hrtf5c.bin 164,480 B + 5 misound_*.bin). thor's rfsa bucket counts 33 bm2nNN blobs vs zeus's 12 - a device-specific RF-resource bundle, not a cdsp fact [F].
8. **Sibling-doc corrections [F]:** #1180's cdsp.b02 row lists Mi_12_Pro among the md5-sharers of mayfly's b02 (`3307465f...`); the direct md5 query shows that build spans exactly 7 devices and **excludes zeus**, whose b02 (`f26e7083...`) is zeus-unique (cupid = Mi_12 IS in the 7-device span). #1198's cluster summary (b02 spans 7, no Mi_12_Pro) matches the query. #1180 also maps Phone_2 to SM8550, while Phone_2's census soc cells and #1198 read SM8475. Both are #1180 slips; flagged for the lead.

## ISA and interface facts

- **PAS loader [F, torvalds master fetched 2026-11-21 in #1180]:** `drivers/remoteproc/qcom_q6v5_pas.c` maps `"qcom,sm8450-cdsp-pas"` to `sm8350_cdsp_resource`: `firmware_name = "cdsp.mdt"`, `pas_id = 18`, `minidump_id = 7`. For zeus this is the **native** SoC compatible (SM8450) - unlike the SM8475 siblings, which boot CDSP through the SM8450 path for lack of an sm8475.dtsi [I].
- **Device tree [F, #1180]:** `arch/arm64/boot/dts/qcom/sm8450.dtsi` defines `remoteproc@32300000` (compatible `qcom,sm8450-cdsp-pas`, `memory-region = <&cdsp_mem>`) with a `qcom,fastrpc` child on glink channel `fastrpcglink-apps-dsp` exposing compute-cb 1..8 (cb9 secure, downstream-only).
- **ISA generation [F, device-level]:** zeus's vendor tree ships `libQnnHtpV69.so` under `vendor/lib/rfsa/adsp` (proprietary-files.txt, fetched 2026-11-21) - the Hexagon **v69** QNN/HTP backend for SM8450. Per `container.md`'s measured e_flags law (0x065 = V65 SDM845, 0x066 = V66 SM8250), zeus's cdsp.mdt plausibly carries `0x00000069` [I, unmeasured, [OPEN]].
- **Userspace clients [F]:** the LineageOS zeus tree lists 9 CDSP compute skels at `vendor/lib/rfsa/adsp`: libhdr_cdsp_skel.so, libmialgo_basic_cdsp_skel.so, libmialgo_ldc_cdsp_skel.so, libmialgo_low_light_align_cdsp_skel.so, libmialgo_mc_bokeh_cdsp_skel.so, libmialgo_mfnr_cdsp_skel.so, libmialgo_pureview_cdsp_skel.so, libmialgo_rfs_cdsp_skel.so, libmialgo_sfnr_cdsp_skel.so, plus `vendor/lib64/libxmi_high_dynamic_range_cdsp.so` - Xiaomi's camera/compute offload modules run on the CDSP root_pd [I, name-derived]. **None of these is in the census:** zeus's `vendor/lib/rfsa/adsp` census rows are 12 bm2nNN.bin modem-RF resources + hrtf5c.bin + 5 misound_*.bin audio resources only [F]. The zeus skel set differs from mayfly's 7 (#1180: ell, night_align, slow_motion instead of low_light_align, mc_bokeh, mfnr, pureview, sfnr) - per-device camera-feature divergence [I].
- **linux-firmware ships no SM8450 cdsp image [F, #1180 WHENCE fetch 2026-11-21]:** only `qcom/sm8450/a730_zap.mbn` and `SM8450-HDK-tplg.bin` for the platform; phone-vendor CDSP builds are device firmware, and the census captures zeus's at `xiaomi/zeus/modem/image`.
- **Provenance [F absence / I]:** the LineageOS zeus `proprietary-files.txt` lists no cdsp.mdt/bNN/jsn and no partition images - the cdsp family is enumerated from the package's firmware image contents (recon: the upstream DB is metadata extracted from LineageOS install packages), riding a firmware partition image (dsp.img the likely carrier [I], per #1180's mayfly reading).
- **ISA/interface documentation status [F]:** isa_identified empty and interface_documented = 'n' on all 19 rows - honestly un-RE'd. No in-repo or public reverse engineering of zeus's cdsp build exists (Gate 0 searches, 2026-11-21).

## Present vs census gap

The #1144 rule (SM-class samsung devices show census GAPS for families riding in the modem image; OnePlus SM8250 devices are the positive controls) does not apply: zeus's cdsp enumeration is complete at the generation shape - 19 files is the maximum of the 17-segment group (9 devices, `census.md` histogram), every segment index the cluster reaches is present (b00-b15, b17), the extract is marked `completes`, and the segment indices are consistent with the b00 size law. Verdict: PRESENT, structurally complete at the census level; the only structural caveats are the fleet-wide b16 absence (explained above, adsp.b16 contrast in hand) and the SM8550-only dtb set (not expected on SM8450).

## Honest negatives

- [OPEN] All 7,817,282 B are declared, not measured; zeus carries no sha256 in any row, and the upstream corpus is metadata-only. No byte of zeus cdsp was read or hashed for this note.
- [OPEN] The 18-entry program-header reading is arithmetic on declared sizes, cross-validated on two byte-measured devices; it is not a measurement of zeus's own ELF header.
- [OPEN] Hexagon v69 is the public toolchain-generation mapping (libQnnHtpV69.so on device); zeus's e_flags ISA nibble is unmeasured and 0x069 is a prediction, not a fact.
- [OPEN] No build/version column exists in the source DB: the 9 zeus-unique md5s cannot be ordered in time against the shared cluster; "unique" means "not observed elsewhere".
- [OPEN] md5 equality is upstream-trusted (`census.md` honest negative); zeus-to-sibling sharing is per the source database, not locally re-hashed.
- [OPEN] Which firmware partition (dsp vs modem) carries the image on zeus is unestablished; the census path is the upstream DB's taxonomy.
- [OPEN] The 9 cdsp skels + libQnnHtpV69.so + libxmi_high_dynamic_range_cdsp.so are outside the census; they need a vendor-blob census pass.
- [OPEN] What processes execute in `msm/cdsp/root_pd` beyond the camera/compute skels' offload is unestablished; the jsn manifest names only the root domain and the servreg service.

## What would upgrade this finding

1. Payload pass: extract the firmware image from a LineageOS zeus package and run `research/cdsp-fleet/cdsp_container_probe.py --mdt` on zeus's `CDSP.MDT` - measure `e_flags` (expect 0x069 [I]), the 18-entry phdr table, and the `b00 ++ b01 == mdt` identity: the first SM8450 cdsp container map, cross-generational against container.md's V65/V66 rows.
2. Diff zeus-unique b10 (1,269,032 B, 16,896 B smaller than mayfly's/thor's) against the SM8475 builds to localize what the per-device delta carries.
3. Census pass over the vendor rfsa bucket (9 zeus cdsp skels + libQnnHtpV69.so) - one decode would cover the Xiaomi 12-series fleet's userspace DSP surface.
4. Byte-parse zeus's 513-B cdspr.jsn to confirm the `dcomment` variant equality at the device level (the laptop note byte-verified the 403-B variant; thor is in its byte-verified set, zeus is not).

## RULE 0 record (2026-11-21)

Gate -1 and Gate 0 queries are recorded verbatim in the SEARCH and DELTA comments on this issue. Summary: GitHub code search `"cdspr.jsn" zeus` and `"xiaomi zeus" cdsp mdt` (adineo-cmd excluded) -> 0 results; web `Xiaomi 12 Pro "zeus" codename SM8450 Snapdragon 8 Gen 1 LineageOS` -> LineageOS wiki zeus (identity only); web `Xiaomi 12 Pro zeus cdsp firmware reverse engineering mdt segmentation` -> generic Qualcomm split-ELF knowledge (pil-splitter, remoteproc docs, bkerler guide), nothing zeus-specific. In-repo: fleet-level prior art cited (census.md/container.md/audit.md, sibling #1180/#1198), not re-derived; no zeus-specific cdsp document existed before this one.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata (sizes, md5s, counts, paths) plus public sources.
