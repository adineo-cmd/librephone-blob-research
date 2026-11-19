# Three-Device Blob Sharing — OnePlus 6 / Nord CE 3 Lite / OnePlus 8 — fragmentation vs leverage quantified

WORKORDER-001 desktop session, 2026-11-18. First cross-SoC-generation identity analysis over three fully-populated official LineageOS censuses: OnePlus 6 (`OnePlus_6`, SDM845, 22.2 nightly), OnePlus Nord CE 3 Lite (`Nord_CE3`, SM6375, 24.0 nightly), OnePlus 8 (`OnePlus_8`, SM8250, 24.0 nightly). Every number below comes from `analysis/out/three-device-sharing.json`, produced by `python3 -I analysis/tools/three_device_sharing.py`. No payload bytes were written anywhere; only counts, names, sizes and hashes.

**Evidence classes:** `[F]` fact (directly measured) · `[I]` inference (strong, derived from measurements) · `[H]` hypothesis (plausible, unverified) · `[N]` honest negative (probed, not found).

## 1. Headline sharing matrix `[F]`

| content identity (md5) | devices carrying it | count |
|---|---|---|
| on all 3 devices | OnePlus_6 + Nord_CE3 + OnePlus_8 | 4 |
| on exactly 2 | any pair | 17 |
| on exactly 1 (device-unique) | single device | 2488 |
| distinct md5 total across the 3 censuses | | 2509 |

Per family (grouping = `(family, md5)`):

| family | distinct (family,md5) | all 3 | exactly 2 | exactly 1 |
|---|---|---|---|---|
| other | 1313 | 2 | 7 | 1304 |
| modem | 914 | 2 | 13 | 899 |
| adsp | 137 | 2 | 3 | 132 |
| cdsp | 40 | 0 | 0 | 40 |
| wifi | 40 | 0 | 1 | 39 |
| gpu | 38 | 0 | 0 | 38 |
| tz | 16 | 0 | 0 | 16 |
| radio | 11 | 0 | 0 | 11 |
| bt | 10 | 0 | 0 | 10 |
| camera | 1 | 0 | 0 | 1 |

## 2. Per-device unique vs shared surface `[F]`

| device | shared files | shared bytes | of which zero-byte | shared non-zero files | unique files | unique bytes |
|---|---|---|---|---|---|---|
| OnePlus_6 | 13 | 69,197 | 2 | 11 | 447 | 279,365,433 |
| Nord_CE3 | 58 | 943,932 | 32 | 26 | 241 | 73,586,339 |
| OnePlus_8 | 24 | 962,305 | 0 | 24 | 2083 | 798,495,845 |

Unique-content share by bytes (incl. zero-byte rows in shared): OnePlus_6 99.98%, Nord_CE3 98.73%, OnePlus_8 99.88% — fragmentation dominates; cross-generation leverage concentrates in a handful of tiny files `[I]`.

Per-family breakdown for each device is in the JSON (`per_device_family_stats`). Zero-byte `d41d8cd…` rows are split out as `shared_zero_byte_files` — they are degenerate empty-file matches, not real blob leverage (see caveats).

## 3. Biggest cross-device shared blobs `[F]`

Top blobs carried by all three devices (md5-identical content):

| md5 | bytes | names | fleet matrix rows / devices |
|---|---|---|---|
| `0d902878dccc9911af8e3983f384c588` | 29,628 | Nord_CE3: lib/rfsa/adsp/libsns_low_lat_stream_skel.so; OnePlus_6: lib/rfsa/adsp/libsns_low_lat_stream_skel.so; OnePlus_8: lib/rfsa/adsp/libsns_low_lat_stream_skel.so | 0 / 0 |
| `544980e9c1c7e640f7e00ef36627bbb4` | 20,824 | Nord_CE3: lib/rfsa/adsp/libsns_device_mode_skel.so; OnePlus_6: lib/rfsa/adsp/libsns_device_mode_skel.so; OnePlus_8: lib/rfsa/adsp/libsns_device_mode_skel.so | 0 / 0 |
| `f012db03ebbde9ce8650993112ee430b` | 128 | Nord_CE3: firmware/ipa_fws.b03; OnePlus_6: firmware/ipa_fws.b03; OnePlus_8: firmware/ipa_fws.b03 | 53 / 42 |
| `0d68af0904dd698b16ffc9cd28b9b0c8` | 32 | Nord_CE3: firmware/vpu20_1v.b19, firmware/vpu20_2v.b19, firmware/vpu20_4v.b19; OnePlus_6: <modem-fat:IMAGE/venus.b04>; OnePlus_8: <modem-fat:PCAFUI~2/OQYQXB~2.B19> | 34 / 34 |

Of the 4 all-3 blobs, 2 also exist in the upstream coverage matrix (`md5_db` join) — they are fleet blobs, not local accidents `[F]`. The two `libsns_*_skel.so` blobs are carried by all three generations yet are **absent from the 123-device matrix** — a matrix coverage gap on real fleet blobs, verified by direct `md5_db` lookup (`[F]`, honest negative for the matrix).

Exactly-2 pairs (17 md5s, all listed in JSON `shared_blobs_exactly2_top`): 13 of 17 are fleet blobs in the matrix. Largest pair blob: `lib/rfsa/adsp/libcamera_nn_skel.so` (809,688 B, Nord_CE3+OnePlus_8 — `0e9f604c59103a2c86bbd6b80e2724d6`), **not in the matrix**; the SM6375+SM8250 pair also share `libapps_mem_heap.so` (58,412 B) and `libdsp_streamer_binning.so` (20,736 B), also absent from the matrix `[F]`.

Top content-alias groups (same md5, different names across devices):

| md5 | bytes | distinct paths | devices | names | fleet |
|---|---|---|---|---|---|
| `ce338fe6899778aacfc28414f2d9498b` | 16,384 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/modem_pr_mcfg_configs_mcfg_hw_mbn_hw.txt>; OnePlus_8: <modem-fat:PCAFUI~2/WMLSPW~2/CCASGL~2/YI7XVO~2/KBNBN6~2/PJYYG4~2.TXT> | 0 rows / 0 devices |
| `620f0b67a91f7f74151bc5be745b7110` | 4,096 | 2 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/evass.b19; OnePlus_8: <modem-fat:PCAFUI~2/UVYW7S~2.B19> | 15 rows / 15 devices |
| `d0bd5030a03f631c9af5060a5645d02e` | 555 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/adspua.jsn>; OnePlus_8: <modem-fat:PCAFUI~2/4K5XTO~2.JSN> | 30 rows / 30 devices |
| `0039483ebd20685728df72c12d13fee4` | 405 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/slpius.jsn>; OnePlus_8: <modem-fat:PCAFUI~2/H54GTB~2.JSN> | 6 rows / 6 devices |
| `40d6edf129dec063ca3fe6cb6837488f` | 403 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/adspr.jsn>; OnePlus_8: <modem-fat:PCAFUI~2/WNORW3~2.JSN> | 30 rows / 30 devices |
| `f2bd80d5f0b19b5b0d36d28383948149` | 403 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/cdspr.jsn>; OnePlus_8: <modem-fat:PCAFUI~2/AV7H26~2.JSN> | 30 rows / 30 devices |
| `2439d6872b39e9c1282c572b266665f0` | 403 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/slpir.jsn>; OnePlus_8: <modem-fat:PCAFUI~2/S4RWSX~2.JSN> | 6 rows / 6 devices |
| `0d68af0904dd698b16ffc9cd28b9b0c8` | 32 | 5 | Nord_CE3+OnePlus_6+OnePlus_8 | Nord_CE3: firmware/vpu20_1v.b19, firmware/vpu20_2v.b19, firmware/vpu20_4v.b19; OnePlus_6: <modem-fat:IMAGE/venus.b04>; OnePlus_8: <modem-fat:PCAFUI~2/OQYQXB~2.B19> | 34 rows / 34 devices |
| `5dd97594c3def03756451e6408954491` | 32 | 2 | OnePlus_6+OnePlus_8 | OnePlus_6: <modem-fat:IMAGE/modem_pr_mcfg_configs_mcfg_hw_mbn_hw.dig>; OnePlus_8: <modem-fat:PCAFUI~2/WMLSPW~2/CCASGL~2/YI7XVO~2/KBNBN6~2/VLDE6D~2.DIG> | 7 rows / 7 devices |
| `eb667b725e1602ba8b9300293a4a2272` | 24 | 6 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/evass.b07, firmware/vpu20_1v.b07, firmware/vpu20_2v.b07, firmware/vpu20_4v.b07; OnePlus_8: <modem-fat:PCAFUI~2/6NAYYT~2.B07>, <modem-fat:PCAFUI~2/WHKSWD~2.B07> | 35 rows / 30 devices |
| `d81a5c71adbe6aae61e4b4a8e121e446` | 20 | 5 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/vpu20_1v.b06, firmware/vpu20_2v.b06, firmware/vpu20_4v.b06; OnePlus_8: <modem-fat:PCAFUI~2/HQKKA5~2.B06>, <modem-fat:PCAFUI~2/VSDWCB~2.B06> | 34 rows / 30 devices |
| `cb24261b83d97279f0dbfa45c42c01c2` | 20 | 4 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/vpu20_1v.b03, firmware/vpu20_2v.b03, firmware/vpu20_4v.b03; OnePlus_8: <modem-fat:PCAFUI~2/VA37H6~2.B03> | 7 rows / 7 devices |
| `f05c4f03a9283589091c31be065c6fed` | 20 | 4 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/vpu20_1v.b05, firmware/vpu20_2v.b05, firmware/vpu20_4v.b05; OnePlus_8: <modem-fat:PCAFUI~2/KK77H3~2.B05> | 30 rows / 30 devices |
| `ec2d6ced2030acafa2b680b83eb3ab63` | 16 | 6 | Nord_CE3+OnePlus_8 | Nord_CE3: firmware/vpu20_1v.b08, firmware/vpu20_2v.b08, firmware/vpu20_4v.b08; OnePlus_8: <modem-fat:PCAFUI~2/6QLSMJ~2.B08>, <modem-fat:PCAFUI~2/TTU5RS~2.B04>, <modem-fat:PCAFUI~2/XT2HFG~2.B08> | 38 rows / 30 devices |
| `d41d8cd98f00b204e9800998ecf8427e` | 0 | 34 | Nord_CE3+OnePlus_6 | Nord_CE3: firmware/evass.b11..b18, firmware/vpu20_1v.b11..b18, vpu20_2v.b11..b18, vpu20_4v.b11..b18 (32 rows); OnePlus_6: firmware/wlan/qca_cld/WCNSS_qcom_cfg.ini, firmware/wlan/qca_cld/wlan_mac.bin (2 rows) | 57 rows / 34 devices |

## 4. Fleet coverage — the "three devices vs the 15,091" number `[F]`

| metric | value |
|---|---|
| coverage-matrix rows / devices / distinct `md5_db` | 33,917 / 123 / 15,091 |
| distinct md5s across the three censuses | 2,509 |
| of those, fleet blobs present in the matrix | **574 (3.80% of 15,091)** |
| three-device md5s with no matrix row | 1,935 |
| per-device distinct md5 (OnePlus_6 / Nord_CE3 / OnePlus_8) | 413 / 196 / 1,925 |
| per-device matrix hits (OnePlus_6 / Nord_CE3 / OnePlus_8) | 19 / 118 / 454 |

## 5. OP6 `modem.img` FAT-entry delta — RESOLVED `[F]`

Raw FAT16 walk of `data-fetch/enchilada/modem.img` (119,820,288 bytes), re-derived from the BPB: bytes/sector 4096, sectors/cluster 4, reserved 1, FATs 2 × 4 sectors, root dir at sector 9 (byte offset 36,864), 512 root slots. OEM name `MSDOS5.0`.

| entry class | count |
|---|---|
| allocated_files | 404 |
| subdir_entries | 118 |
| dot_entries | 236 |
| volume_labels | 0 |
| deleted | 0 |
| lfn | 0 |
| end_markers | 119 |

**Resolution:** volume labels: (none); deleted entries: 0. Subdirectory entries: 118 total — at root level: `IMAGE`, `VERINFO` (full tree in JSON `fat_walk.subdirs`). The 403-row census and `analysis/out/modem-fat-census.json` cover exactly the 403 allocated files under `IMAGE/`; the walk finds **404 allocated files / 113,443,924 bytes**. File(s) walked but absent from the census: `IMAGE/MODEM_PR/MCFG/CONFIGS/MCFG_HW/MBN_HW.TXT` (0 bytes declared, md5 `d41d8cd98f00b204e9800998ecf8427e`, first_cluster 6363); `VERINFO/VER_INFO.TXT` (1,201 bytes, md5 `624973d80f73a1c0a6670ee87afdd08c`, first_cluster 7311). All 402 walked file md5s that exist in `modem-fat-census.json` match it exactly; the remaining walked file (`IMAGE/.../MBN_HW.TXT`) is present in the census but with the chain-hash md5 documented in caveats (`[F]`).

Consequence: the OP6 census is missing one 8.3-named file (`VERINFO/VER_INFO.TXT`, 1,201 B); the modem.img directory-entry-true content total is **113,443,924 bytes across 404 files**, not 403 / 113,460,308 B. Reconciliation: the previously-published 113,460,308 B figure = this total + 16,384 — i.e. it counted VER_INFO.TXT and also charged MBN_HW.TXT at its 16,384 B chain size instead of its declared size 0 `[F]`.

## 6. Method / provenance

- Censuses deduped on `(device,file)` keep-last: raw rows OnePlus_6 462, Nord_CE3 299, OnePlus_8 2107. Dedupe events: OnePlus_6 2 (the 0-byte `firmware/wlan/qca_cld/` duplicate rows, content-identical re-walk); Nord_CE3 0; OnePlus_8 0 (`[F]`).
- OnePlus_6 md5 provenance: 403 modem-FAT rows from `analysis/out/modem-fat-census.json` (bytes + notes cross-checked, 0 mismatches); 59 vendor rows recomputed from local files, accepted only when local sha256 equals the census sha256 (`[F]`).
- Nord_CE3 and OnePlus_8 md5s from their census `md5` columns (sha256-verified at population time) `[F]`.
- Matrix join key `md5_db`, 33,917 rows × 123 devices, 15,091 distinct values, 0 empty `[F]`. 11 md5s carry different family labels across devices — normalization needed `[F]`.

## 7. Honest negatives `[N]`

- No deleted FAT16 entries, no volume labels, no LFN entries in modem.img (0/0/0) — the delta is not a deleted-entry artifact.
- No md5 with conflicting byte sizes across devices.
- No md5-based cross-device identity for OnePlus_6 vendor rows beyond local recomputation (the enchilada census carries no `md5` column).
- Entries after the first end-of-dir marker: 0.
- The brief's example alias pair (OP6 `image_wlanmdsp.mbn` vs larry `wlanmdsp.otaupdate`) does not exist: Nord_CE3 has no wlanmdsp row; OP6's `wlanmdsp.mbn` (3,035,876 B) matches no md5 on either other device.
- No zero-byte rows on OnePlus_8; the degenerate zero-byte group exists only between OP6 (2 rows) and Nord_CE3 (32 rows).

## 8. Caveats

- OP6 modem-FAT row MBN_HW.TXT: FAT directory entry declares size 0 (true content = empty) but the census recorded 16,384 bytes with md5 ce338fe6… (full cluster-chain hash) — the recorded OP6+OP8 pairing on that md5 reflects chain bytes, not declared content.
- The zero-byte md5 groups 34 census rows and is itself carried by 57 matrix rows — all zero-byte 'shared' counts are degenerate, split out separately.
- Census scope limits cross-device conclusions: the OP6 census has no odm/ tree, so the VOOC pair (proven on Nord_CE3 and OnePlus_8) cannot appear for OnePlus_6 — a scope fact, not a content fact.

## 9. Open items

- Append `VERINFO/VER_INFO.TXT` as the 404th modem-FAT row (one-line append; census owner per write discipline).
- Correct the `MBN_HW.TXT` row (declared size 0).
- Family-label normalization for identical content across devices (11 md5s) before fleet-wide roll-up.
- Extend the identity matrix to more of the 123 matrix devices to turn the 3-device leverage numbers into a fleet curve.
