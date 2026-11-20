# CDSP fleet census — 23 files, 64 devices, 586 md5s

Provenance: `data/fleet/devices-001-222.csv` (sha256 `6f717a6cf57f903aafc632c4913ff809842913df39cebe5642a3b43eda4cd1dc`, 34053 rows), family=`cdsp`, 950 instances.
Generator: `research/cdsp-fleet/build_census.py` (`python3 -I`), emits `census.json` + this file.
Evidence classes: `[F]` measured from the CSV, `[I]` inference, `[H]` hypothesis, `[N]` honest negative.
No payload bytes were read or written; this note is metadata arithmetic only.

## Headline

- `[F]` **23 canonical files** (33 raw distinct `file` strings minus 10 `<modem-fat:IMAGE/...>` aliases), **64 devices**, **950 (device,file) instances**, **586 distinct md5**.
- `[F]` `cdsp.mdt` reaches **64/64 devices (100.0%)**, `cdspr.jsn` reaches **60/64 (93.8%)**.
  `[N]` Denominator caveat: those 64 are the devices that carry *any* cdsp row in this
  slice, which is **29.2% of the 219 devices** present in the CSV. "100%" means "every
  device that ships cdsp at all", not "every device in the catalogue". Three of the 64
  (`Pixel_4A_5G`, `Pixel_5`, `Pixel_5A`) carry **only** `cdsp.mdt`, so they count toward
  `.mdt` reach while contributing no evidence about the segment set.
- `[F]` **51.8% of instances** (and 24.8% of declared bytes) sit in an md5 cluster shared
  by >=2 devices.
  `[N]` That figure is **cross-device** duplication only; there are **0** within-device
  duplicate groups. It is also dominated by `cdspr.jsn`, which is 100% shared by
  construction (a 2-value file). Excluding `cdspr.jsn` the rate is **48.5%** (432/890),
  and for `cdsp.mdt` alone (excluding `cdsp_dtb.mdt`) it is **15.6%** (10/64) — the
  `.mdt` is mostly per-device unique.
- `[F]` `cdspr.jsn` is a **2-value** file fleet-wide: 60 instances collapse to 2 md5s (30 + 30 devices).
- `[N]` Sizes are **declared, not measured**, for 940 of 950 cdsp instances.

## A. Canonical file inventory

`[F]` Arithmetic: **33 raw distinct `file` values − 10 `<modem-fat:IMAGE/...>` alias values = 23 canonical files**.
The 23-file claim is **CORRECT** (`claim_23_holds=true`).

| quantity | value |
|---|---|
| distinct raw `file` strings | 33 |
| `<modem-fat:IMAGE/...>` rows | 10 |
| distinct alias raw strings | 10 |
| canonical names after stripping wrapper | 23 |
| canonical names that exist *only* in alias form | 0 |
| largest per-device file count | 21 (13 devices) |
| smallest per-device file count | 1 (Pixel_4A_5G, Pixel_5, Pixel_5A) |

`[F]` The 10 alias rows come from 1 device (OnePlus_6) and wrap 10 distinct targets, of which **0** are canonical names not already produced by an unwrapped row. The subtraction is therefore exact: no canonical name exists only in alias form.

`[F]` Canonical inventory: `cdsp.b00`, `cdsp.b01`, `cdsp.b02`, `cdsp.b03`, `cdsp.b04`, `cdsp.b05`, `cdsp.b06`, `cdsp.b07`, `cdsp.b08`, `cdsp.b09`, `cdsp.b10`, `cdsp.b11`, `cdsp.b12`, `cdsp.b13`, `cdsp.b14`, `cdsp.b15`, `cdsp.b17`, `cdsp.mdt`, `cdsp_dtb.b00`, `cdsp_dtb.b01`, `cdsp_dtb.b02`, `cdsp_dtb.mdt`, `cdspr.jsn`.

`[F]` Alias raw strings: `<modem-fat:IMAGE/cdsp.b00>`, `<modem-fat:IMAGE/cdsp.b01>`, `<modem-fat:IMAGE/cdsp.b02>`, `<modem-fat:IMAGE/cdsp.b03>`, `<modem-fat:IMAGE/cdsp.b04>`, `<modem-fat:IMAGE/cdsp.b05>`, `<modem-fat:IMAGE/cdsp.b06>`, `<modem-fat:IMAGE/cdsp.b08>`, `<modem-fat:IMAGE/cdsp.b10>`, `<modem-fat:IMAGE/cdsp.mdt>`.

`[I]` Segment series runs `cdsp.b00`–`cdsp.b17` with **b16 absent**, plus a separate `cdsp_dtb.*` split image (4 files) and the `cdspr.jsn` manifest descriptor.

## B. Per-file device reach (descending)

Device universe: **64 distinct `device` values** in the cdsp family; 950 instances over those devices.

| file | devices | reach | instances | bytes min | bytes max | bytes median | distinct md5 |
|---|---:|---:|---:|---:|---:|---:|---:|
| `cdsp.mdt` | 64 | 100.0% | 64 | 4464 | 7980 | 7580 | 59 |
| `cdsp.b08` | 61 | 95.3% | 61 | 816 | 2827764 | 116918 | 46 |
| `cdsp.b05` | 61 | 95.3% | 61 | 1000 | 2803308 | 2170428 | 51 |
| `cdsp.b04` | 61 | 95.3% | 61 | 220 | 2119844 | 1100 | 26 |
| `cdsp.b06` | 61 | 95.3% | 61 | 160 | 1834724 | 23164 | 44 |
| `cdsp.b02` | 61 | 95.3% | 61 | 8488 | 1663741 | 235672 | 32 |
| `cdsp.b03` | 61 | 95.3% | 61 | 1172 | 1070949 | 106620 | 31 |
| `cdsp.b01` | 61 | 95.3% | 61 | 6696 | 27572 | 7192 | 42 |
| `cdsp.b00` | 61 | 95.3% | 61 | 436 | 628 | 468 | 35 |
| `cdspr.jsn` | 60 | 93.8% | 60 | 403 | 513 | 458 | 2 |
| `cdsp.b09` | 49 | 76.6% | 49 | 280 | 3043668 | 63937 | 30 |
| `cdsp.b11` | 49 | 76.6% | 49 | 3152 | 86064 | 54932 | 29 |
| `cdsp.b10` | 42 | 65.6% | 42 | 2816 | 2803220 | 58900 | 30 |
| `cdsp.b07` | 30 | 46.9% | 30 | 2648 | 2674696 | 100952 | 23 |
| `cdsp.b12` | 30 | 46.9% | 30 | 2728 | 114256 | 3656 | 18 |
| `cdsp.b13` | 30 | 46.9% | 30 | 4576 | 80720 | 61952 | 15 |
| `cdsp.b15` | 30 | 46.9% | 30 | 4520 | 12288 | 8192 | 19 |
| `cdsp.b14` | 17 | 26.6% | 17 | 1436 | 4504 | 4504 | 7 |
| `cdsp_dtb.b01` | 13 | 20.3% | 13 | 512 | 62952 | 512 | 6 |
| `cdsp_dtb.mdt` | 13 | 20.3% | 13 | 4044 | 4044 | 4044 | 13 |
| `cdsp_dtb.b02` | 13 | 20.3% | 13 | 3896 | 3896 | 3896 | 13 |
| `cdsp_dtb.b00` | 13 | 20.3% | 13 | 148 | 148 | 148 | 6 |
| `cdsp.b17` | 9 | 14.1% | 9 | 3836 | 4616 | 4136 | 9 |

Reach verification `[F]`:

- `cdsp.mdt` → **64 devices (100.0%)**. The literal string `cdsp.mdt` appears on **63** devices; the difference is OnePlus_6, whose only `cdsp.mdt` row is the alias form. So the widely-quoted "63 devices" is true **only** for the raw string and **false after canonicalisation**. Devices with no `cdsp.mdt`: none.
- `cdspr.jsn` → **60 devices (93.8%)**. Devices with no `cdspr.jsn`: OnePlus_6, Pixel_4A_5G, Pixel_5, Pixel_5A.
- Reach floor: Pixel_4A_5G, Pixel_5, Pixel_5A carry exactly one cdsp file (`cdsp.mdt` only). Reach ceiling: Edge_40_Pro, FP6, Mi_13, Mi_13_Pro +9 carry 21.
- Per-device file-count histogram: 1 file(s) → 3 device(s), 10 file(s) → 1 device(s), 11 file(s) → 11 device(s), 12 file(s) → 19 device(s), 18 file(s) → 8 device(s), 19 file(s) → 9 device(s), 21 file(s) → 13 device(s).

`[F]` Segment-index presence (devices carrying each `cdsp.bNN`): b00→61, b01→61, b02→61, b03→61, b04→61, b05→61, b06→61, b07→30, b08→61, b09→49, b10→42, b11→49, b12→30, b13→30, b14→17, b15→30, b17→9.

| segments on device | devices | cdsp.mdt bytes min | max | median |
|---|---:|---:|---:|---:|
| 0 | 3 | 7660 | 7660 | 7660 |
| 9 | 12 | 7260 | 7580 | 7580 |
| 10 | 19 | 7508 | 7660 | 7660 |
| 15 | 13 | 5084 | 5084 | 5084 |
| 16 | 8 | 7828 | 7980 | 7828 |
| 17 | 9 | 4464 | 5244 | 4764 |

`[N]` Segment count does **not** predict `cdsp.mdt` size here: Pearson r = **-0.622** across 64 devices. The 17-segment group has median `.mdt` **4764 B**, while the largest median sits at the 16-segment group (7828 B).

`[I]` That negative sign is more likely a **confound than an inverse law**: segment count tracks platform generation, and 1 of the 6 groups carry a **single** `.mdt` size (largest: 15 segments → 5084 B on all 13 devices). Where within-group spread is zero, there is nothing for a correlation to fit; the global coefficient is really between-group. A per-generation regression would be the honest test, and this CSV carries no clean generation key.

`[N]` **This is not a layout claim.** No `.mdt` bytes were read; the record structure, offsets and segment table of the container remain unknown from this CSV.

`[F]` Total declared bytes across the fleet: **283509579** over 950 instances. Per-device totals run from **7660 B (Pixel_4A_5G)** to **9387575 B (Phone_2)**; the median device carries 3528575 B.

## C. Shared-content clusters

| metric | value |
|---|---:|
| distinct md5 | 586 |
| md5 shared by >=2 devices | 128 |
| singleton md5 (one device only) | 458 |
| instances sitting in a shared cluster | 492 of 950 |
| **sharing rate (instances)** | **51.8%** |
| sharing rate (declared bytes) | 24.8% (70325534 of 283509579 B) |

`[F]` Cluster-size histogram (clusters / instances): 1→458/458; 2→63/126; 3→13/39; 4→27/108; 5→7/35; 6→6/36; 7→1/7; 8→3/24; 9→4/36; 10→1/10; 11→1/11; 30→2/60.

`[F]` Sharing rate **per file** — instances whose md5 also appears on another device:

| file | instances | unique instances | shared instances | sharing rate |
|---|---:|---:|---:|---:|
| `cdsp.mdt` | 64 | 54 | 10 | 15.6% |
| `cdsp.b00` | 61 | 23 | 38 | 62.3% |
| `cdsp.b01` | 61 | 34 | 27 | 44.3% |
| `cdsp.b02` | 61 | 20 | 41 | 67.2% |
| `cdsp.b03` | 61 | 19 | 42 | 68.9% |
| `cdsp.b04` | 61 | 15 | 46 | 75.4% |
| `cdsp.b05` | 61 | 45 | 16 | 26.2% |
| `cdsp.b06` | 61 | 35 | 26 | 42.6% |
| `cdsp.b08` | 61 | 36 | 25 | 41.0% |
| `cdspr.jsn` | 60 | 0 | 60 | 100.0% |
| `cdsp.b09` | 49 | 23 | 26 | 53.1% |
| `cdsp.b11` | 49 | 23 | 26 | 53.1% |
| `cdsp.b10` | 42 | 26 | 16 | 38.1% |
| `cdsp.b07` | 30 | 19 | 11 | 36.7% |
| `cdsp.b12` | 30 | 13 | 17 | 56.7% |
| `cdsp.b13` | 30 | 10 | 20 | 66.7% |
| `cdsp.b15` | 30 | 17 | 13 | 43.3% |
| `cdsp.b14` | 17 | 5 | 12 | 70.6% |
| `cdsp_dtb.b00` | 13 | 3 | 10 | 76.9% |
| `cdsp_dtb.b01` | 13 | 3 | 10 | 76.9% |
| `cdsp_dtb.b02` | 13 | 13 | 0 | 0.0% |
| `cdsp_dtb.mdt` | 13 | 13 | 0 | 0.0% |
| `cdsp.b17` | 9 | 9 | 0 | 0.0% |
| **all files** | **950** | **458** | **492** | **51.8%** |

Top 10 clusters by device count (of 128 shared clusters; the full list with complete device sets is in `census.json` → `clusters.top_clusters`):

| # | md5 | file | devices | bytes | devices (first 8, then remainder) |
|---:|---|---|---:|---:|---|
| 1 | `49003ffcd10ec16dee11caad22b11b42` | `cdspr.jsn` | 30 | 513 | Edge_30, Edge_30_Fusion, Edge_40_Pro, FP5, FP6, Mi_12, Mi_12S, Mi_12S_Pro, +22 more |
| 2 | `f2bd80d5f0b19b5b0d36d28383948149` | `cdspr.jsn` | 30 | 403 | Defy_2021, Edge_30_Neo, FP4, G_Stylus_5G-2-2022, Mi_A3, Moto_E7_Plus, Moto_G10, Moto_G30, +22 more |
| 3 | `5a6394e3e1889607dbb3020d8a88caec` | `cdsp.b11` | 11 | 54932 | Edge_30_Neo, G_Stylus_5G-2-2022, Moto_G34_5G, Moto_G82_5G, Moto_G84_5G, Moto_G_5G_2024, Moto_G_Stylus_5G, Nord_CE2, +3 more |
| 4 | `1411cc4aae50e6b671e4fa886b8ce6fa` | `cdsp.b04` | 10 | 1100 | Edge_30_Neo, G_Stylus_5G-2-2022, Moto_G34_5G, Moto_G82_5G, Moto_G84_5G, Moto_G_5G_2024, Nord_CE2, Nord_CE3, +2 more |
| 5 | `14eb07f574826b7c3504734684d29572` | `cdsp.b03` | 9 | 1172 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Phone_2, Poco_F5, +1 more |
| 6 | `3209c0463dc7ffcdeeb05b21ed67bf61` | `cdsp.b01` | 9 | 7464 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Phone_2, Poco_F5, +1 more |
| 7 | `6ac427c5351d7c6231cdc133f8f05a52` | `cdsp.b09` | 9 | 93460 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Phone_2, Poco_F5, +1 more |
| 8 | `be34bb139199359e4123264694adcbe1` | `cdsp.b15` | 9 | 12288 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Phone_2, Poco_F5, +1 more |
| 9 | `5c3eb8e5c751cad2017d8b5abb4259f9` | `cdsp.b14` | 8 | 4504 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Poco_F5, Poco_F5_Pro |
| 10 | `6ba66561f962d2351d3b8ec819056c9d` | `cdsp.b13` | 8 | 80720 | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Poco_F5, Poco_F5_Pro |

`[F]` Most-shared md5 **per file**:

| file | max cluster | md5 clusters at that size | md5 | bytes |
|---|---:|---:|---|---:|
| `cdspr.jsn` | 30 | 2 | `49003ffcd10ec16dee11caad22b11b42` | 513 |
| `cdsp.b11` | 11 | 1 | `5a6394e3e1889607dbb3020d8a88caec` | 54932 |
| `cdsp.b04` | 10 | 1 | `1411cc4aae50e6b671e4fa886b8ce6fa` | 1100 |
| `cdsp.b01` | 9 | 1 | `3209c0463dc7ffcdeeb05b21ed67bf61` | 7464 |
| `cdsp.b03` | 9 | 1 | `14eb07f574826b7c3504734684d29572` | 1172 |
| `cdsp.b09` | 9 | 1 | `6ac427c5351d7c6231cdc133f8f05a52` | 93460 |
| `cdsp.b15` | 9 | 1 | `be34bb139199359e4123264694adcbe1` | 12288 |
| `cdsp.b13` | 8 | 1 | `6ba66561f962d2351d3b8ec819056c9d` | 80720 |
| `cdsp.b14` | 8 | 1 | `5c3eb8e5c751cad2017d8b5abb4259f9` | 4504 |
| `cdsp.b02` | 7 | 1 | `3307465f9b5ffe74956e69b547f6db17` | 1581865 |
| `cdsp.b10` | 6 | 1 | `063e55ea48ffe7baaab4d35b829c7926` | 58900 |
| `cdsp.b12` | 6 | 1 | `fdc5f5a759c421aad8b10b64fc05ac76` | 2896 |
| `cdsp_dtb.b00` | 6 | 1 | `a4fa90de9560c7d36a8b72e8b5d457d0` | 148 |
| `cdsp_dtb.b01` | 6 | 1 | `8ef92426e900be5e4cda260bcd8cd506` | 512 |
| `cdsp.b00` | 5 | 1 | `074aa5ca1131ff3432b56bf82e472f7a` | 436 |
| `cdsp.b05` | 5 | 1 | `b8d1ab1b557fc1b98f9110e8880cfede` | 1096 |
| `cdsp.b06` | 5 | 1 | `1f72d439f24dd03ded61742bded7c61b` | 160 |
| `cdsp.b07` | 4 | 1 | `ca796f329241ae9aebfd3454a3bb11da` | 99604 |
| `cdsp.b08` | 4 | 2 | `0983dfca9885d44cf2ad71ed310405a3` | 1552 |
| `cdsp.mdt` | 2 | 5 | `3621a8e6261aff1f9c96010d623e40e4` | 7508 |
| `cdsp.b17` | 1 | 9 | `20d73ebe4f40e4e20ce0836ca55b18e7` | 4136 |
| `cdsp_dtb.b02` | 1 | 13 | `22f4e930fbada04705725d9e2895af3b` | 3896 |
| `cdsp_dtb.mdt` | 1 | 13 | `1acc4f39cfd5560debf9cff0d43f0223` | 4044 |

`[F]` **Correction to the expected shape.** The 30-device cluster is `cdspr.jsn` only: 2 md5s over 60 instances, split 30 + 30. **`cdsp.mdt` has no 30-device cluster at all** — its largest shared md5 covers only **2 devices**, and **54 of its 64 instances are unique**. A "30-device `cdsp.mdt`" claim is therefore wrong; the leverage in the `.mdt` is device *reach* (64 devices), not shared content.

`[I]` The two `cdspr.jsn` values split the fleet into 30 / 30-device halves. Vendors present on **both** sides: fairphone, motorola, oneplus, xiaomi. That the split crosses OEM lines is consistent with it tracking platform generation rather than vendor, but this CSV has no build-date column to confirm it.

## D. Per-SoC breakdown

`[F]` 20 distinct `soc` strings, of which **19 carry a value and 1 is empty**. The empty string accounts for **458 rows over 25 devices** — that is 48.2% of all cdsp rows and 39.1% of the device universe.

| soc | devices | rows | canonical files |
|---|---:|---:|---:|
| *(empty)* | 25 | 458 | 23 |
| Qualcomm SM6375 Snapdragon 695 | 7 | 84 | 12 |
| Qualcomm SM7250 Snapdragon 765G | 5 | 39 | 18 |
| Qualcomm SM6115 Snapdragon 662 | 4 | 46 | 13 |
| Qualcomm SM6225 Snapdragon 680 4G | 3 | 36 | 12 |
| Qualcomm SM8250 Snapdragon 865 | 3 | 42 | 18 |
| Qualcomm MSM8998 Snapdragon 835 | 2 | 22 | 11 |
| Qualcomm SM4250 Snapdragon 460 | 2 | 22 | 11 |
| Qualcomm SM8550 Snapdragon 8 Gen2 | 2 | 42 | 21 |
| Qualcomm QCM6490 | 1 | 18 | 18 |
| Qualcomm SDM845 Snapdragon 845 | 1 | 10 | 10 |
| Qualcomm SM4375 Snapdragon 4 Gen 1 | 1 | 12 | 12 |
| Qualcomm SM6375 Snapdragon 695 5G | 1 | 12 | 12 |
| Qualcomm SM7225 Snapdragon 750G | 1 | 12 | 12 |
| Qualcomm SM7325-AE Snapdragon 778G+ 5G | 1 | 18 | 18 |
| Qualcomm SM8150 Snapdragon 855 | 1 | 11 | 11 |
| Qualcomm SM8150-AC Snapdragon 855 | 1 | 11 | 11 |
| Qualcomm SM8350 Snapdragon 888 | 1 | 18 | 18 |
| Qualcomm SM8350-AC Snapdragon 888+ | 1 | 18 | 18 |
| Qualcomm SM8475 Snapdragon 8+ Gen1 | 1 | 19 | 19 |

`[F]` The 25 empty-soc devices are: FP6, G_Stylus_5G-2-2022, Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro, Mi_12_Pro, Mi_13, Mi_13_Pro, Mi_A3, Moto_G9, Moto_G9_Power, Moto_G_Stylus_5G, Nord_4, Nord_CE4, OnePlus_12, OnePlus_13, OnePlus_9, Pad_2_Pro, Pad_Pro, Poco_F5, Poco_F5_Pro, Poco_F6_PRo, Redmi_K60_Pro.

`[F]` Each of those 25 devices has **zero** cdsp rows carrying a soc value — the gap is per-device, not per-row noise. They span all 23 canonical files.

`[F]` The empty-soc devices are identifiable by `db_path` codename even without a SoC: FP6→`FP6`, G_Stylus_5G-2-2022→`milanf`, Mi_12→`cupid`, Mi_12S→`mayfly`, Mi_12S_Pro→`unicorn`, Mi_12S_Ultra→`thor`, Mi_12T_Pro→`diting`, Mi_12_Pro→`zeus`, Mi_13→`fuxi`, Mi_13_Pro→`nuwa`, Mi_A3→`laurel_sprout`, Moto_G9→`guamp`, Moto_G9_Power→`cebu`, Moto_G_Stylus_5G→`denver`, Nord_4→`avalon`, Nord_CE4→`benz`, OnePlus_12→`waffle`, OnePlus_13→`dodge`, OnePlus_9→`lemonade`, Pad_2_Pro→`erhai`, Pad_Pro→`caihong`, Poco_F5→`marble`, Poco_F5_Pro→`mondrian`, Poco_F6_PRo→`vermeer`, Redmi_K60_Pro→`socrates`.

`[I]` 3 `soc` string pairs are the same silicon spelled twice: `Qualcomm SM6375 Snapdragon 695` vs `Qualcomm SM6375 Snapdragon 695 5G`; `Qualcomm SM8150 Snapdragon 855` vs `Qualcomm SM8150-AC Snapdragon 855`; `Qualcomm SM8350 Snapdragon 888` vs `Qualcomm SM8350-AC Snapdragon 888+`. Counting strings (20) therefore overstates distinct SoCs.

## E. Vendor and db_type breakdown

| vendor string | rows | devices |
|---|---:|---:|
| `oneplus` | 293 | 18 |
| `motorola` | 273 | 21 |
| `xiaomi` | 247 | 13 |
| `fairphone` | 51 | 3 |
| `nothing` | 37 | 2 |
| `realme` | 24 | 2 |
| `fxtec` | 12 | 1 |
| `OnePlus` | 10 | 1 |
| `google` | 3 | 3 |

`[F]` 9 distinct vendor **strings** but only **8 distinct vendors** case-folded — `OnePlus` (10 rows) and `oneplus` (293 rows) are the same OEM.

| db_type | rows | devices |
|---|---:|---:|
| `COMPUTE` | 880 | 63 |
| `UNKNOWN` | 60 | 60 |
| `<absent>` | 10 | 1 |

`[F]` The 23 canonical files partition cleanly by tag: **22 tagged `COMPUTE`** (`cdsp.b00`, `cdsp.b01`, `cdsp.b02`, `cdsp.b03`, `cdsp.b04`, `cdsp.b05`, `cdsp.b06`, `cdsp.b07`, `cdsp.b08`, `cdsp.b09`, `cdsp.b10`, `cdsp.b11`, `cdsp.b12`, `cdsp.b13`, `cdsp.b14`, `cdsp.b15`, `cdsp.b17`, `cdsp.mdt`, `cdsp_dtb.b00`, `cdsp_dtb.b01`, `cdsp_dtb.b02`, `cdsp_dtb.mdt`) and **1 tagged `UNKNOWN`** (`cdspr.jsn`). Separately, 10 of those files also appear as alias rows with **no** `db_type` field at all (10 rows, from OnePlus_6).

## F. Data-quality findings

1. `[F]` **Empty `soc`: 458 rows / 25 devices** (48.2% of rows, 39.1% of devices). Vendors affected: xiaomi 247, oneplus 144, motorola 46, fairphone 21. They cover all 23 canonical files, so the per-SoC table above silently loses 25 of 64 devices.
2. `[F]` **`<modem-fat:IMAGE/...>` aliases: 10 rows on 1 device (OnePlus_6), 10 distinct raw strings.** They are the *only* cdsp rows for that device (zero unwrapped cdsp rows). Consequence: a raw-string count reports `cdsp.mdt` at **63** devices; the canonical reach is **64**.
3. `[F]` **Notes deviate from the strict `md5_db=<hex>; P<n>; db_path=...; db_type=...` shape on 12 rows** (OnePlus_6×10, FP6×2). Observed deviations: 10 alias rows carry `source=...` with no `db_path`/`db_type`; 2 `FP6` rows append `isa=QDSP6 / Hexagon`.
4. `[F]` **Bytes inconsistent with siblings — constant declared size, many hashes:** `cdsp_dtb.b00` 148 B × 13 instances but 6 distinct md5; `cdsp_dtb.b02` 3896 B × 13 instances but 13 distinct md5; `cdsp_dtb.mdt` 4044 B × 13 instances but 13 distinct md5. `[I]` A fixed-length header would look exactly like this; whatever the cause, *size equality does not imply content equality* anywhere in this CSV.
5. `[F]` **Bimodal size distributions — 8 files whose sorted sizes jump >=10x in one step:** `cdsp.b04` 1284x, `cdsp.b05` 90x, `cdsp.b03` 87x, `cdsp_dtb.b01` 58x, `cdsp.b08` 45x, `cdsp.b07` 35x, `cdsp.b12` 22x, `cdsp.b06` 14x. `cdsp.b04` is the extreme: 54 instances at <=1376 B and 7 at >=1767108 B (1284x gap).
6. `[F]` **186 of 950 rows sit >=8x from their own file's median size** — size alone cannot identify a segment across devices.
7. `[F]` **Vendor spelling split:** `oneplus` 293 rows vs `OnePlus` 10 rows; 9 distinct strings collapse to 8 vendors.
8. `[F]` **`soc` near-duplicates:** 3 pairs inflate the distinct-SoC count: `Qualcomm SM6375 Snapdragon 695` vs `Qualcomm SM6375 Snapdragon 695 5G`; `Qualcomm SM8150 Snapdragon 855` vs `Qualcomm SM8150-AC Snapdragon 855`; `Qualcomm SM8350 Snapdragon 888` vs `Qualcomm SM8350-AC Snapdragon 888+`.
9. `[F]` **Segment index gap:** `cdsp.b16` is absent fleet-wide; indices present are b00, b01, b02, b03, b04, b05, b06, b07, b08, b09, b10, b11, b12, b13, b14, b15, b17.
10. `[F]` **Coverage skew:** 3 devices carry only 1 file (`cdsp.mdt`), while 13 devices carry the maximum 21. Only 13 of 64 devices reach the 21-file shape.
11. `[F]` **Verification coverage:** only 4 of 950 cdsp rows carry a `sha256`; 940 are `metadata-only` and 10 are `populated-local-session`. The md5s are upstream database values, not recomputed here.

## G. Honest negatives

- `[F]` **Cross-check against real bytes (added 2026-11-20, audit round).** The `OnePlus_6` alias rows were not a dead end: they point at a FAT16 `IMAGE/` directory inside `enchilada/modem.img`, and all **11** extracted md5s match the census `md5_db` values exactly. That gives a second, independent cdsp image (SDM845) verified against this table — see `container.md` §7. It also anchors the 403-byte `cdspr.jsn` cluster by one locally verified copy.
- `[N]` **The `.mdt` enumeration is case-sensitive, and real payloads are uppercase.** `find -name '*.mdt'` finds 50 files (12 Hexagon) while `find -iname '*.mdt'` finds 82 (16 Hexagon). A case-sensitive sweep therefore misses every 8.3 FAT name — which is exactly how the first pass concluded, wrongly, that no second device existed.
- `[N]` **Sizes are declared, not measured, for 940 of 950 cdsp rows** (and 33481 of 34053 rows repo-wide are `metadata-only`). Every byte figure here is an upstream database field; nothing was hashed or `stat`ed by this script.
- `[N]` **Slice only:** the CSV covers devices 001–222 of the catalogue (219 devices actually present). It says nothing about devices 223+.
- `[N]` **No container layout and no ISA from this file.** The CSV gives names, sizes and md5s; it carries no offsets, no ELF/MDT headers, no segment table. Only 2 of 950 rows carry an `isa=` annotation (on FP6), and that is a database label, not a measurement — this census cannot confirm the CDSP ISA.
- `[N]` **Absence is not proof of absence.** A device with no `cdsp.b14` row may genuinely ship no such segment, or the enumeration may have missed it; the CSV cannot distinguish the two.
- `[N]` **md5 collisions aside, equality is upstream-trusted.** Two rows sharing `md5_db` are equal *according to the source database*; this script did not fetch a byte.
- `[N]` **No build/version column.** Two md5s cannot be ordered in time; the 30-device cluster is not necessarily the oldest or newest variant.
- `[N]` **No SoC for 25 devices, and no way to recover it here.** They do carry `db_path` (25 distinct paths, so a codename each), but the CSV has no codename→SoC table; deriving one would require an external source.
- `[N]` **`db_path` is missing for OnePlus_6.** 63 distinct paths cover 63 of 64 devices, and no device carries two, so `db_path` behaves like a per-device key here — but it is a source-tree location, not a verified identity, and the uncovered device cannot be traced from this file.

## Reproduction

```
cd /tmp/opencode/cdsp-595/research/cdsp-fleet && python3 -I build_census.py
```

Outputs `census.json` (machine-readable, same numbers) and this `census.md`. Re-running is byte-stable apart from no timestamps being recorded.
