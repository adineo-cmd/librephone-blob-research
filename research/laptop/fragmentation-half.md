# Device fragmentation — LAPTOP half (rows 119–236 of the 236-device LibrePhone list)

**2026-11-16 · merge-ready for the lead.** Derived entirely from metadata:
`/tmp/lpdb/split.json` (`laptop_half`, 118 devices parsed from codeberg
rsavoye/librephone `data/devices.sql.bz2`, codepoint-sorted
`lower(vendor),lower(model),lower(build)`; the LAPTOP machine owns rows
119–236) joined against the master family taxonomy in
`upstream-contribution/blob-database/coverage-matrix.csv`. Generator:
`build_fragmentation_half.py` (this directory; re-runnable); machine-readable
clusters: `sharing-clusters.csv` (7,042 rows = every distinct md5 in the
half, shared clusters first then singletons); raw summary:
`fragmentation-summary.json`. No payload bytes were fetched; nothing here is
proprietary material.

Headline: **16,883 blob rows over 118 devices, 31.92 GB (29.73 GiB),
7,042 distinct md5s — 2,684 of them shared by >1 device in the half, and
10,510 of the 16,883 rows (62.3 %) are instances of a shared blob.** The
half's blob inventory is dominated by 62 blob-populated devices across
oneplus/samsung/sony/xiaomi (+2 realme, 1 zte); 72 devices carry zero blob
rows.

## 1. The extracted-vs-not picture (and a semantics finding)

The upstream `extracts` column does **not** track blob presence (verify
against the pre-built `devices-half.csv` — 0 mismatches found between the
two artifacts, but both inherit the same upstream flag):

| combination | devices |
|---|---|
| `extracts` true **and** blob rows present | 31 |
| `extracts` true, **zero** blob rows | 15 (razer cheryl/aura, shift axolotl, solana ingot, sony akari/akatsuki/aurora/xz2c, xiaomi thyme/lisa/renoir/haydn/zizhan/alioth/munch) |
| blob rows present, `extracts` **false** | 31 (all remaining oneplus/samsung/sony/xiaomi populated devices) |
| neither | 41 |

So the "46/118 extracted" figure (31+15) is the flag count, while the real
**blob-populated set is 62/118**. For leverage purposes the 62 are the
addressable devices this half contributes to the full picture.

## 2. SoC generations

The `soc` column is populated for only 28 of 118 devices — **7 distinct
strings, all Qualcomm**:

| SoC (as recorded) | devices |
|---|---|
| Qualcomm SDM845 Snapdragon 845 | 9 |
| Qualcomm SM6375 Snapdragon 695 | 8 |
| Qualcomm SM8250 Snapdragon 865 | 6 |
| Qualcomm SM8350 Snapdragon 888 | 2 |
| Qualcomm SM8150-AC Snapdragon 855 | 1 |
| Qualcomm SM8475 Snapdragon 8+ Gen 1 | 1 |
| Qualcomm SDM636 Snapdragon 636 | 1 |
| *(no SoC recorded — `\N`)* | **90** |

Data-quality finding (extends recon.md's "builds.csv SOC blank for ~122
devices" to this half): **both of the half's MediaTek devices carry a blank
SoC** — `xiaomi/Redmi_10S (rosemary)` (proven MT6785 Helio G95 by the lab's
own `mediatek/rosemary-census.md`) and `xiaomi/Poco_12C (earth)` — as do all
4 `radxa` Zero boards (unpopulated, soc blank). Every SoC actually recorded
in this half is Qualcomm; the recorded-SoC subset is 28/118 vs the master
DB's ~124/246 — consistent under-representation. (Flagship Xiaomi
Snapdragon 8-Gen-1/2/3 devices — cupid, vermeer, mondrian, nuwa, … — are
all `\N` too.)

## 3. Family distribution (master-matrix taxonomy, reused verbatim)

| family | rows | bytes | devices | note |
|---|---|---|---|---|
| boot | 487 | 13.66 GB | 62 | incl. `boot.img`/`vendor_boot`/`vm-bootsys.img` — largely the FREE kernel images (recon's caveat), not blobs |
| modem | 814 | 8.68 GB | 50 | `modem.img` + MDT segments (`modem.bNN`) |
| other | 8,574 | 6.46 GB | 59 | long tail incl. camera/`UNKNOWN`-typed rows |
| adsp | 1,435 | 2.31 GB | 29 | incl. the `bm2nXX.bin` fleet |
| wifi | 2,731 | 0.39 GB | 50 | WCN/qca firmware + manifests |
| tz | 2,115 | 0.22 GB | 31 | TAs/keymaster/DRM + `.bNN` stubs |
| cdsp | 402 | 0.14 GB | 23 | compute DSP |
| bt | 84 | 42.1 MB | 31 | QCA BT patches + NVRAM |
| gpu | 241 | 6.4 MB | 47 | Adreno GMU/SQE microcode |

Every laptop-half row inherited its family from the master matrix's own
mapping (0 rows fell back to filename heuristics; 0 unmatched).

## 4. Top-15 shared-blob clusters (identical md5 across devices in this half)

Filtered to real firmware per recon.md's precedent (≥1 KB, no
`.jsn/.json/.xml/.txt` manifests). Full unfiltered list (incl. manifest
clusters) is in `sharing-clusters.csv`.

| # | devices | bytes | family | file | md5 | devices (codenames) |
|---|---|---|---|---|---|---|
| 1 | 12 | 164,480 | adsp | `hrtf5c.bin` | `2a47164e…b71a0` | cupid, diting, fuxi, marble, mayfly, mondrian, nuwa, socrates, thor, unicorn, vermeer, zeus |
| 2 | 11 | 473,648 | modem | `modem.b16` | `30c22653…4ca7e` | cupid…zeus (11 Xiaomi flagship set) |
| 3 | 11 | 201,560 | other* | `hpbtfw20.tlv` | `92247344…9ffb7` | cupid, diting, lemonade(+p), marble, martini, mayfly, mondrian, thor, unicorn, zeus |
| 4 | 11 | 41,548 | gpu | `a650_gmu.bin` | `a2b9504e…11e1a` | gta4l(lwifi), gts7l(lwifi), instantnoodle(+p), kebab, lemonades, pdx206, pdx215, r8q |
| 5 | 11 | 34,736 | other | `dax_param.bin` | `70727b64…4bd3` | a21s, a71, beyond0/1/2lte, beyondx, f62, gta4l(lwifi), gta4xl(lwifi) |
| 6 | 11 | 31,632 | gpu | `a650_sqe.fw` | `353e247b…edc1` | same set as #4 |
| 7–11 | 11 ×5 | 6,319 | other* | `hpnv20.bin` / `.b2f` / `.b3b` / `.b4b` / `.b8b` | (distinct md5s) | 11 devices each (cupid, diting, lemonades, mayfly, …) |
| 12 | 10 | 11,458 | other | `plmn_delta.bin` | `9df3aeb9…3aeb9` | samsung 2018-20 set + xiaomi Mi439 |
| 13 | 10 | 4,096 | tz | `cpusys_vm.b03` | `620f0b67…0b67` | samsung set |
| 14 | 10 | 2,126 | other | `CFR_OPlus_EF017_UW_snapshot.bin` | `99593358…3dcbe` | erhai, lemonade(+p), luigi, martini, oscar — plus instantnoodle(+p) under its `CFR_para2_OnePlus_…` twin name |
| 15 | 9 | 788,436 | other | `sh.bin` | `e0f9a9be…9a9be` | samsung/xiaomi set |

\* `hpbtfw20.tlv`/`hpnv20*` sit in `bluetooth/image` and are QCA BT
firmware — the master matrix types them `other`/`misc`; recon.md's own
family table puts `.tlv` BT patches + NVRAM under **bt**. Candidate
correction for the lead (not changed here — shared file, out of my
file-wall).

## 5. Leverage notes (RE once, frees N devices)

- **Device-count leverage in this half is the Xiaomi flagship block.**
  `hrtf5c.bin` (ADSP HRTF data, 164 KB) ×12, `modem.b16` ×11, the
  `hpnv20*` BT-NVRAM fleet ×11 ×5 variants, `hpbtfw20.tlv` ×11 — one RE
  pass each covers 11–12 of the half's 62 populated devices. These are the
  half's own additions on top of the recon global top-20 (which is
  bt/adsp-weighted): the half's vendor mix (52 xiaomi) makes the
  2021-2024 Xiaomi flagship set the densest sharing block.
- **Byte-weighted leverage** (devices × bytes, top rows): `vm-bootsys.img`
  270 MB ×5 = **1.35 GB** (the Xiaomi flagship vm guest image — mayfly,
  unicorn, thor, diting, mondrian, all SoC-blank in the DB); `dsp.img`
  64 MB ×5 = 335 MB; `night_align_lsc_tbl_*.bin` camera calibration 50 MB +
  37 MB ×6 = 528 MB combined; `modem.img` ×2 at 220/187 MB. Full top-10 in
  `fragmentation-summary.json`.
- **Cross-generation identical bytes**: `a619_gmu.bin` (Adreno 619 GMU
  microcode, 32,768 B) is md5-identical to `a618_gmu.bin` in 2 further
  devices — one 32 KB RE pass covers Adreno 618 **and** 619 GMU. Same
  pattern for the `CFR_OPlus…`/`CFR_para2_OnePlus…` camera-calibration pair
  (§4 #14).
- **Nightly drift splits clusters**: e.g. `bm2n12.bin` exists on 14 half
  devices but as **2 md5 clusters** (8 + 6), `a630_sqe.fw` on 14 devices as
  **4 clusters**, `unified_ksqs.bin` on 24 devices as **5 clusters**. Any
  merged full-DB leverage ranking must therefore track BOTH metrics —
  file-presence (RE coverage) and identical-md5 (byte-exact reuse) — which
  `sharing-clusters.csv` + `fragmentation-summary.json` provide per cluster.
- **Degenerate cluster (data quality)**: md5 `d41d8cd9…8427e` (the empty
  string) spans 33 zero-byte rows across 21 devices
  (`oem_hw_null.txt` ×12, `oem_sw_null.txt` ×12, `oem_hw.txt` ×8,
  `eye_retouch_chinese.bin` ×1) — the upstream DB stores zero-byte files as
  blob rows; excluded from the top-15 ranking, kept in the CSV for the
  merge.

## 6. Recon.md top-20 cross-reference (expected vs computed)

All 20 recon top-20 blobs **do** occur in this half; the two metric flavors
reconcile the workorder's expected counts with the computed md5 clusters:

| file | recon global devs | half devices w/ file (any md5) | half md5 clusters | largest same-md5 cluster |
|---|---|---|---|---|
| `crbtfw20.tlv` / `apbtfw10.tlv` / `crbtfw11.tlv` / `crnv20.bin` / `crnv11.bin` / `apnv10.bin` (QCA BT fleet) | 29 each | **4** each | 1 each | **4** ✓ (expected ×4) |
| `bm2n12.bin` / `bm2n14.bin` / `bm2n15.bin` (ADSP fleet) | 26 each | **14** each ✓ (expected ×14) | 2 each | **8** (nightly drift) |
| `a619_gmu.bin` | 26 | **5** ✓ (expected ×5) | 1 | **7** (5 as `a619_gmu.bin` + 2 as `a618_gmu.bin`, identical bytes) |
| `bm2n08.bin` / `bm2n06.bin` | 25 | 16 | 3 / 2 | 8 |
| `bm2n13.bin` | 25 | 14 | 2 | 8 |
| `unified_ksqs.bin` / `sequence_manifest.bin` | 25 | 24 | 5 | 8 |
| `a660_sqe.fw` | 21 | 14 | 2 | 8 (size drifted 40,496 → 43,068 B between nightlies) |
| `a660_gmu.bin` | 19 | 6 | 1 | 6 |
| `a630_sqe.fw` | 19 | 14 | 4 | 5 |
| `CFR_OPlus_EF017_UW_snapshot.bin` | 19 | 6 | 1 | 10 (twin `CFR_para2_…` name) |
| `aoa_cldb_falcon.bin` | 17 | 2 | 1 | 2 |

So: the workorder's expected "bm2n12/14/15 ×14, QCA BT ×4, a619_gmu ×5" are
**file-presence counts and are verified exactly**; the same-md5 cluster
counts are smaller where nightly drift split a fleet (documented above) and
larger where identical bytes shipped under a second filename (a619/a618).

## 7. Merge instructions (lead, laptop-half → full 236-device picture)

1. **Clusters**: union on `md5` across `blob-matrix/desktop/`'s clusters and
   `blob-matrix/laptop/sharing-clusters.csv`. Device sets are disjoint by
   construction (the halves partition the device list), so the full-DB
   device count of a cluster = desktop_count + laptop_count − 0; re-derive
   family from the master matrix (both halves already inherit it, so no
   re-mapping is needed).
2. **Leverage ranking**: recompute the full-DB top-20 as
   `full_devices = sum of halves' file-presence counts` and keep the
   identical-md5 decomposition per cluster (§5) — recon.md's global table
   is file-presence-based and will reconcile exactly with the sum.
3. **SoC table**: merge §2 with the desktop's half; the "SoC recorded ⇒
   Qualcomm-only in this half" finding and the two blank-SoC MediaTek
   devices are global data-quality items (candidate corrections for the
   master `device-inventory.csv`, lead-owned).
4. **Semantics finding** (§1) applies DB-wide; merge with recon.md's
   "upstream data-quality findings" section (lead-owned file).
5. **Totals reconciliation**: this half = 16,883 rows / 31.92 GB /
   7,042 distinct md5s; the master DB is 33,917 rows / 69.80 GB /
   15,091 md5s, so the desktop half should carry ≈17,034 rows / 37.88 GB;
   distinct-md5 subtraction needs the cross-half shared set (clusters that
   span both halves), which the union in step 1 yields.
6. **Rule-1 candidates found this pass** (reported, not silently fixed):
   `hpbtfw20.tlv`/`hpnv20*` family `other`→`bt` candidate (§4); the two
   blank-SoC MTK devices (§2); `a660_sqe.fw` nightly size drift vs recon's
   recorded bytes (§6).
