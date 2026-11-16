# Per-SoC census method plans (236-device split, top-8 clusters) — 2026-11-16

Purpose: the per-SoC execution plans for the lab's FP6/MT6785 census
pipeline (container walk → ISA identification → per-family census →
interface decode) applied to the top device clusters of the
LibrePhone 236-device universe, plus the **upstream-facing** section:
what LibrePhone could accept upstream per cluster (doc stubs,
sizes.csv rows, interface facts). This file complements the fleet docs
in [laptop/](laptop/) (ADSP bm2nXX fleet, QCA BT fleet, Adreno GMU —
which cover shared-blob families) and the matrix scaffold
(`upstream-contribution/blob-database/coverage-matrix.csv`); it is the
per-SOC planning layer.

## Data basis and provenance (RULE 0)

- **Device universe:** `/tmp/lpdb/split.json` — the 236-device split of
  the upstream `devices.sql.bz2` `devices` table (118 desktop-half +
  118 laptop-half rows; blob rows carry file/type/size/md5, no paths).
  Regeneration method per WORKORDER-001-desktop.md (recon stream).
  Counts below are complete enumerations, not samples; computed this
  session 2026-11-16 with the scripts sketched in the appendix of this
  file's history (regex-token SoC normalization, family rules at the
  bottom of this file).
- **Upstream metadata:** `upstream-contribution/blob-database/`
  (recon.md, coverage-matrix.csv, device-inventory.csv) — fetched and
  committed 2026-11-16 by the recon stream; not re-fetched (no
  download needed, per F-71: the published "database" is metadata
  only).
- **Mainline kernel support levels:** verified per-SoC this session by
  fetching `torvalds/linux` master files (every claim below names the
  file; all fetches 2026-11-16, status: OK — network flaky but all
  succeeded within 3 retries; failures would be recorded per file).
- **BT chip identities per cluster** are decoded from the DB's own
  blob filenames through the **mainline `btqca.c` rampatch-prefix →
  soc-type switch** (fetched and verified this session):
  `msbtfw*`→WCN6750, `crbtfw*`→WCN3990/91/98, `apbtfw*`→WCN3988,
  `cmbtfw*`→WCN3950, `htbtfw*`→QCA6390, `hpbtfw*`→QCA2066,
  `wcnhpbtfw*`→WCN6855, `hmtbtfw*`→WCN7850. This is a lab-derived
  fact chain (upstream DB filenames × mainline kernel case labels) —
  first recorded anywhere as a per-cluster chip census.

## The SoC distribution of the 236 devices

The `soc` column is present for only 115 of 236 devices; **121 are
blank** (including FP6 itself — the lab's flagship has no SOC cell
upstream). Grouped by chip (variant suffixes -AC/-AE merged; the
stray `\ufffd` byte on the `larry` row stripped):

| devices | SoC | blob rows in DB | GB (blob bytes) | populated |
|---|---|---|---|---|
| 121 | **(blank — 51.3% of the universe)** | 17,358 | 36.97 | 56 devices |
| 16 | SDM845 (Snapdragon 845) | 83 | 0.11 | 3 |
| 15 | SM6375 (Snapdragon 695) | 3,562 | 7.29 | 12 |
| 14 | Google Tensor (GS101 ×3, GS201 ×5, G3 ×5, G4 ×1) | 677 | 4.66 | 14 |
| 8 | SM7250 (Snapdragon 765G) | 938 | 2.00 | 4 |
| 8 | MSM8998/SDM835 (Snapdragon 835) | 871 | 1.08 | 2 (both mislabeled — see below) |
| 8 | SM8250 (Snapdragon 865/870) | 1,900 | 2.65 | 6 |
| 5 | SM8150 (Snapdragon 855) | 871 | 1.10 | 2 |
| 4 | SM7325 (Snapdragon 778G) | 880 | 1.81 | 4 |
| 4 | SM6115 (Snapdragon 662) | 967 | 2.03 | 4 |
| 4 | SM8475 (Snapdragon 8+ Gen 1) | 654 | 0.81 | 1 |
| 3 | SM8350 (Snapdragon 888) | 1,344 | 1.72 | 2 |
| 3 | SM6225 (Snapdragon 680 4G) | 704 | 1.40 | 3 |
| 3 | Amlogic S905X3/S905Y2 | 25 | 0.04 | 3 |
| 2 each | SDM632, SDM630, SDM636, SDM660, SDM670, SM8550, SM4250, MSM8996 Pro | (see device-inventory.csv) | | |
| 1 each | SM7225 (FP4), QCM6490 (FP5), SM4350, SM4375 | 286/706/44/364 | 0.69/0.59/0.15/0.78 | all |

Upstream data-quality findings surfaced by this grouping (each is a
fact from the dump, verifiable in devices.sql.bz2):

1. **Mislabeled SOC cells:** Pixel 4 (`flame`) carries "SM8150 855"
   (it is SDM845); Pixel 4 XL (`coral`) carries "SM7250 765G" (it is
   SDM845); OnePlus 7 (`guacamoleb`) and OnePlus 7T (`hotdogb`) carry
   "MSM8998 835" (they are SM8150). Consequence: the MSM8998
   cluster's entire 871-row blob content is actually SM8150-family
   firmware; the genuine-835 devices (mata, joan, nx659j,
   cheeseburger, walleye, taimen) have **zero** blob rows.
2. A stray `\ufffd` byte precedes one SOC value (`larry`, OnePlus
   Nord CE 3 Lite) — already noted by the recon stream.
3. The `extracts` flag does not track blob presence (FP6:
   extracts=False with 447 blob rows; several extracts=True devices
   have 0 rows) — same finding as the laptop Phase-4 fragmentation
   half.
4. FP6's own SOC cell is `\N` — the flagship device is in the blank
   bucket.
5. **SOC cells contradict device identities** in both directions
   (device identity from the dump's own vendor/model strings, public
   SoC from the device's known spec): `tundra` (Moto Edge 30
   Fusion, public SM7325-AE) carries SM7250 with 639 rows — the
   SM7250 cluster's largest contributor; `pioneer`/`voyager`/
   `discovery` (Sony Xperia XA2/XA2 Plus/XA2 Ultra, public SDM630)
   carry SDM845 and hold the SDM845 cluster's entire 83-row blob
   content (Adreno-530-generation files — which fits the 845 label
   but not the device family, i.e. the rows and the label cannot
   both be right); `cheryl` (Razer Phone, public MSM8998) and
   `akershus` (ZTE Axon 9 Pro, public SDM845) carry SM6375;
   `nx659j` (Red Magic 5G per the model string, public SM8250)
   carries MSM8998; `caiman`/`comet` (Pixel 9 Pro/9 Pro Fold,
   public Tensor G4) carry "Tensor G3". **Consequence for this
   file:** cluster row-counts are reported under the DB's labels
   as-is, with each contradiction flagged where it affects the
   cluster's data interpretation; fixing the labels is upstream
   deliverable #2 in the summary table below.

## The census method (the FP6/MT6785 pipeline, parameterized)

Four phases; the per-SoC sections below state only what **differs**
from the FP6 exemplar (which ran all four end-to-end, see
`qualcomm-fp6/docs/fp6-architecture-census.md`):

1. **Container walk** — OTA payload.bin manifest → per-partition dump
   (`tools/payload_manifest.py`, `payload_dump.py`); vfat/ext4
   extraction (`extract_vfat.py`, `extract_ext4.py`). Per-SoC knobs:
   Tensor devices ship a different partition grammar entirely
   (bl1/bl2/bl31/pbl/ldfw/tzsw = Arm-trusted-boot chain, no
   Qualcomm .mdt splits at all); Amlogic TV boxes are Android-TV
   images (boot/recovery + dtb.img) with no per-subsystem partitions.
2. **ISA identification** — ELF header census + entry-point sanity +
   RV32/Hexagon opcode enrichment (the junk-header rule: per-segment
   `.bXX` e_machine values are noise; trust `.mdt`/`.mbn` headers and
   entry-in-LOAD checks). Per-SoC knobs: Tensor images are mostly
   raw AArch64 or AOSP-format containers (no ELF wrapper) — the
   identification anchor is the dtb/DTBO + bootloader binary
   signature, not e_machine.
3. **Per-family census** — filename-first family mapping with
   upstream bintype fallback (the generator rules embedded in
   build_scaffold.py, blob-database stream). Per-SoC knob: the BT
   fleet prefix decode (msbtfw/crbtfw/apbtfw/cmbtfw/htbtfw/hpbtfw/
   hmtbtfw) resolves the BT chip per device **without any new RE**;
   the touch-panel fleets (FW_*/LIMIT_* Samsung/Novatek/Goodix/
   FocalTech images) are the dominant row mass on Motorola/Xiaomi
   clusters and need a per-vendor touch-IC census template.
4. **Interface decode** — only where a mainline driver exists to
   decode against (ath10k/ath11k WMI+CE, btqca TLV, fastrpc,
   qseecom, QRTR/QMI). Per-SoC knob: Tensor has *no* mainline
   driver surface (verified below) — its interface half is blocked
   on AOSP kernel sources, not mainline.

## Top-8 clusters (plus the two one-device Fairphone exemplars)

### 1. SDM845 (Snapdragon 845) — 16 devices, 83 rows, 0.11 GB

- Devices (DB vendor/model strings): blueline/crosshatch (Pixel
  3/3XL), judyln/judyp/judypn (LG G7 ThinQ/V35/V40), enchilada
  (OnePlus 6), aura (Razer Phone 2), axolotl (Shift 6MQ), akari/
  xz2c/aurora/akatsuki (Sony XZ2 family), caymanslm (LG Velvet),
  pioneer/voyager/discovery (Sony XA2 family — see contradiction
  note 5 above: their SOC cell and their 83 rows disagree with the
  device family), beryllium (Poco F1) and others per
  device-inventory.csv.
- DB state: **almost unpopulated** — 3 Sony devices carry 83 rows
  (Adreno 530 GPU fleet a530*_pfp/pm4/gpmu/seq + camera cpp_firmware
  + boot.img). Everything else needs first-population from
  per-device LineageOS packages (~1-1.3 GB each).
- Mainline support (verified 2026-11-16): the strongest of any
  cluster — `sdm845.dtsi` + `sdm845-db845c.dts` + **`sdm845-google-blueline.dts`
  (Pixel 3 mainlined)** among 24 dts/dtsi files; PAS compatibles
  `qcom,sdm845-adsp-pas`, `qcom,sdm845-cdsp-pas` (+ slpi resource);
  modem via `qcom_q6v5_mss`; WiFi = **ath10k `qca6174`/`wcn3990 hw1.0`**
  (WCN3990 dir constant verified in `ath10k/core.c` lines 714-726);
  GPU = Adreno 530 (a530 firmware, freedreno/mesa public).
- Census method: run the FP6 pipeline verbatim (same MDT grammar,
  same PAS loading); the wifi family is ath10k-SNOC (wlan_firmware/
  WCNSS-style files) not ath11k — the interface decode anchors are
  `ath10k_snoc` + the WCNSS NV blob (wcnss.wcnss_nv_*), a different
  driver than FP6's.
- Upstream-facing: FP6-style per-family doc stubs would land on
  fertile ground here (upstream has zero 845-family docs); sizes.csv
  rows for the 13 unpopulated devices; interface facts: ath10k SNOC
  probe/download sequence, a530 GMU-less GPU firmware set (a530_*,
  7 files — one RE pass frees the whole cluster's GPU story).

### 2. SM6375 (Snapdragon 695) — 15 devices, 3,562 rows, 7.29 GB

- Devices (DB vendor/model strings): miami (Moto Edge 30 Neo), fogos
  (Moto G34 5G), rhodep (Moto G82 5G), bangkk (Moto G84 5G), oscaro
  (OnePlus Nord CE2), larry (OnePlus Nord CE3), gunnar (OnePlus Nord
  N20 5G), luigi (Realme 10 Pro), oscar (Realme 9 Pro), pdx225/
  pdx235/pdx234/pdx237 (Sony Xperia 10 IV/10 V/1 V/5 V); plus two
  zero-row label errors (cheryl = Razer Phone, akershus = ZTE Axon 9
  Pro — see note 5).
- DB state: the **largest populated modern cluster** (12 devices with
  345-506 rows each). Row mass is dominated by **touch-panel
  firmware fleets** (FW_NF_NT36672C_TIANMA ×28, FW_FT3518_SAMSUNG
  ×24, FW_NF_ILI7807S_TIANMA ×16 — per-panel variants).
- BT chips (decoded): **crbtfw\* → WCN3990/91/98 Rome family ×28,
  apbtfw\* → WCN3988 ×16** — consistent with mainline
  `sm6375.dtsi`'s `qcom,wcn3990-wifi` compatible (verified, line
  1736): this cluster's combo chip is the WCN39xx generation, NOT
  the FP6's WCN6750.
- Mainline support (verified): `sm6375.dtsi` +
  `sm6375-sony-xperia-murray-pdx225.dts` (+ pdx235); PAS compatibles
  `qcom,sm6375-adsp-pas`, `qcom,sm6375-cdsp-pas`,
  `qcom,sm6375-mpss-pas` — the full four-processor PAS set.
- Census method: FP6 pipeline; two additions — (a) a **touch-IC
  census template** (file → vendor token NT36672C/FT3518/ILI7807S →
  panel vendor; type/size/hashes only), because touch is the family
  mass here; (b) the BT census is the *Rome* flavor — the lab's QCA
  BT fleet doc (laptop/qualcomm-qca-bt-fleet.md) plus the crbtfw
  branches of btqca.c.
- Upstream-facing: upstream's docs have no 6xx-generation content at
  all; the single highest-leverage upstream artifact for this
  cluster is the per-family doc stub set (modem/adsp/cdsp/mpss +
  WCN39xx WiFi/BT) — sizes.csv rows for the 12 populated devices are
  a 10-minute contribution (sizes.csv has zero 695-family rows).

### 3. Google Tensor (GS101/GS201/G3/G4) — 14 devices, 677 rows, 4.66 GB

- Devices: oriole, raven, bluejay (GS101), panther, cheetah, lynx,
  felix, tangorpro (GS201), shiba, husky, akita, caiman, comet (G3
  per the DB's SOC cell; caiman/comet are Pixel 9 Pro/9 Pro Fold —
  public Tensor G4, note 5), tokay (G4) — every device populated
  (abl.img/bl1/bl2/bl31/tzsw/pbl/ldfw ×14 identical filenames).
- DB state: uniform boot-chain file set across all 14 devices — the
  Tensor family is one **Arm trusted-boot grammar**: bl1/bl2/bl31
  (ARM Trusted Firmware stages), pbl, ldfw, tzsw (Samsung TZ
  software), abl, mfc_fw.bin (Exynos MFC video codec), evt.ec.bin
  (embedded controller). No Qualcomm .mdt/.bXX splits anywhere.
- Mainline support (verified): **none** —
  `arch/arm64/boot/dts/google/` contains only lga-* files (a
  different platform); no gs101/gs201/zuma dtsi in master (checked
  2026-11-16 via the contents API). Tensor mainlining lives in AOSP
  and out-of-tree series, not torvalds master.
- Census method: the pipeline must switch to the **MT6785-style
  grammar** (lab mediatek/rosemary census: vendor-container formats,
  per-payload records) adapted to Samsung's chain: container walk =
  per-image ELF/raw classification, ISA identification = AArch64
  raw-code detection + DTB/DTBO parsing, family census = Exynos
  names (mfc/shldrdm?), interface decode = **blocked on AOSP kernel
  sources** (exynos9820-era drivers; gs101/gs201 are public in
  AOSP — citable but not mainline).
- Upstream-facing: upstream has zero Tensor content; the modem
  (Exynos Modem 5123/5300/5400, "shut in radio/" per the recon's
  regulatory stub) is the freedom-critical blob — the honest
  upstream deliverable here is a **radio-directory inventory doc per
  Tensor device** (what files, what sizes, what hash identity across
  the 14 devices — the DB already shows they share filenames), plus
  sizes.csv rows. No interface claims should be filed until the AOSP
  kernel cross-reference is done.

### 4. SM7250 (Snapdragon 765G) — 8 devices, 938 rows, 2.00 GB

- Devices: sunfish (Pixel 4A), bramble (Pixel 4A 5G), redfin
  (Pixel 5), barbet (Pixel 5A), tundra (Moto Edge 30 Fusion — SOC
  cell contradiction, note 5: the cluster's largest contributor at
  639 rows carries the SM7250 label), kiev (Moto G 5G), nairo (Moto
  G 5G Plus), coral (Pixel 4 XL — mislabel, data-quality finding 1).
  Populated: bramble (105), redfin (103), barbet (91), tundra (639).
- DB state: full firmware-update partition set per device (xbl/abl/
  aop/devcfg/uefisecapp/modemr.jsn/tz/hyp ×4).
- BT chips (decoded): hpbtfw\* → QCA2066 ×2 (tundra generation).
- Mainline support (verified): **no sm7250.dtsi in mainline** (404
  checked) — this cluster has no upstream kernel surface; its
  kernel-side interface facts must come from Qualcomm/AOSP vendor
  trees (cite as vendor-tree facts, not mainline).
- Census method: FP6 pipeline works as-is (same MDT grammar); ISA
  identification will find the same generation mix (Hexagon
  modem/adsp/cdsp + AArch64 TZ). Flag: without mainline dts, the
  interface-decode phase has no in-tree anchor — record as
  interface_documented=n until a vendor tree is chosen.
- Upstream-facing: sizes.csv rows for the 4 populated devices; a
  Pixel-4a-5G/5/5a/7-tundra? note — no. Honest scope: blob census
  + BT chip decode only.

### 5. MSM8998/SDM835 (Snapdragon 835) — 8 devices, 871 rows (0 from 835 devices), 1.08 GB

- Devices: mata (Essential PH-1), joan (LG V30), nx659j (Red Magic 5G
  per the model string — public SM8250, another SOC contradiction,
  0 rows), cheeseburger (OnePlus 5), walleye/taimen (Pixel 2/2 XL),
  guacamoleb/hotdogb (**mislabeled SM8150 devices carrying all 871
  rows**).
- DB state: the genuine-835 devices are **empty** — first-population
  is the whole task for this cluster. Pixel 2/2 XL are the priority
  (long mainline pedigree: walleye/taimen mainline dts exist —
  `msm8998-*` dts files verified present, 15 files incl.
  `msm8998-fxtec-pro1.dts` and Pixel 2 entries).
- Mainline support (verified): `msm8998.dtsi` + 14 device dts;
  PAS compatible `qcom,msm8998-adsp-pas`; modem via mss driver.
- Census method: FP6 pipeline + older-grammar alert: 835-era
  firmware uses the **older split-ELF and WCNSS grammar** (WiFi =
  wcn3990 or qca6174 PCIe; BT per DB decode = crbtfw ×6 / apbtfw ×4
  — but those rows belong to the mislabeled SM8150 devices, so the
  835 devices' BT chips are **[OPEN] until first population**).
- Upstream-facing: doc stubs would target the already-mainlined
  devices (Pixel 2, Fxtec Pro1) — the "docs one per mainlined
  device" pattern; sizes.csv rows after population.

### 6. SM8250 (Snapdragon 865/870) — 8 devices, 1,900 rows, 2.65 GB

- Devices: instantnoodle, instantnoodlep, kebab, lemonades, martini
  (OnePlus 8/8 Pro/8T/9R/9RT), pdx206 (Sony Xperia 5 II), pstar/nio
  (Moto Edge 20 Pro/Edge S, 870).
- DB state: 6 populated; row mass = OnePlus fast-charge firmware
  (oplus_vooc_fw*.bin ×80/x80/x12) + Samsung touch fleets
  (FW_S3908_SAMSUNG ×25) — the "other" long tail dominates.
- BT chips (decoded): **htbtfw\* → QCA6390 ×6, hpbtfw\* → QCA2066
  ×4** — the discrete BT-chip generation (QCA6390 is a real
  PCIe-attached BT chip, unlike WCN6750's UART).
- Mainline support (verified): `sm8250.dtsi` + 13 dts files (HDK,
  MTP, Samsung); PAS `qcom,sm8250-adsp-pas`/`cdsp` (+ mss modem);
  no OnePlus dts in mainline (404 checked for
  sm8250-oneplus-common.dtsi).
- Census method: FP6 pipeline verbatim; the fast-charge/touch fleet
  needs the vendor "other" template; WiFi/BT = the QCA6390 discrete
  generation (BT decode above; `ath11k` supports QCA6390_HW20 per
  the verified core.c table) — interface decode anchors at
  `ath11k` qca6390 hw params, a genuinely different transport
  (PCIe MHI) than FP6's IPCI.
- Upstream-facing: the OnePlus 8-series is the largest populated
  OnePlus cluster upstream — sizes.csv rows + a fast-charge firmware
  family doc (oplus_vooc_fw: one RE pass covers ×80+ device-rows).

### 7. SM8150 (Snapdragon 855) — 5 devices, 871 rows, 1.10 GB

- Devices: guacamole, hotdog (OnePlus 7 Pro/7T Pro — the two
  populated), flame (mislabeled Pixel 4), fajita (OnePlus 6T? no —
  fajita is OnePlus 6T which is SDM845; **another likely upstream
  SOC mislabel** — fajita's DB SOC says SM8150; OnePlus 6T is
  SDM845), TP1803.
- DB state: rows split guacamole 435 / hotdog 436 (OnePlus 7
  family firmware).
- BT chips (decoded): crbtfw\* ×6 + apbtfw\* ×4 (Rome/WCN39xx
  generation) — from the guacamole/hotdog rows.
- Mainline support (verified): `sm8150.dtsi` + 7 dts files (HDK855,
  Surface Duo, MTP); PAS `qcom,sm8150-adsp/cdsp/mpss-pas` full set.
- Census method: FP6 pipeline verbatim. Data-quality lever: filing
  upstream SOC corrections for fajita/flame/guacamoleb/hotdogb rows
  (see upstream-facing) would fix the matrix's join keys.
- Upstream-facing: SOC-cell corrections upstream (a small data PR),
  sizes.csv rows, and the OnePlus-7-family doc stubs.

### 8. SM7325 (Snapdragon 778G) — 4 devices, 880 rows, 1.81 GB

- Devices: berlin, berlna, dubai, Spacewar (Nothing Phone 1,
  SM7325-AE) — all populated (bluetooth.img/boot/vbmeta/sequence_
  manifest.bin ×4 each).
- BT chips (decoded): **msbtfw\* → WCN6750 ×12** (msbtfw10+msbtfw11
  both shipped, + msnv10/11) + cmbtfw\* → WCN3950 ×6 — the same BT
  firmware family as the FP6, at different patch versions.
- Mainline support (verified): `sm7325.dtsi` + 8 dts files (Motorola
  dubai variants); PAS: no sm7325-specific entries (nearest:
  sm8350 resources) — flagged honestly.
- Census method: FP6 pipeline + the BT census is directly the lab's
  msbtfw/WCN6750 expertise (bt-firmware-census.md) — the msnv10 vs
  msnv11 NVM tag diff is a natural first deliverable (msnv10 is
  absent from FP6's partition, so this cluster extends the lab's BT
  census by one generation).
- Upstream-facing: extend the lab's BT census doc with the
  SM7325-variant rows; interface facts reuse interface-bt.md (the
  driver side is identical — same btqca branches).

### 9-12. The next tier (SM6115 ×4, SM8475 ×4, SM8350 ×3, SM6225 ×3)

- SM6115 (662): pro1x (Fxtec Pro1-X), bathena (Moto Defy 2021),
  caprip (Moto G30), borneo (Moto G Power) — fully populated (967
  rows); BT = cmbtfw\* → WCN3950 ×20; mainline:
  `sm6115.dtsi` + `sm6115-fxtec-pro1x.dts` + `sm6115-xiaomi-lemon.dts`;
  PAS full set (adsp/cdsp/mpss). Best upstream landing zone of the
  tier: the Fxtec Pro1-X is an official mainline-adjacent device.
- SM8475 (8+ Gen 1): eqs (Moto Edge 30 Ultra), Pong (Nothing Phone
  2), ingot (Solana Saga) + bronco (Moto ThinkPhone — the
  mislabeled "8 Gen1" row); only 1 populated (amss.bin/amss20.bin/
  m3.bin/regdb.bin ×2 = the raw-modem-image era begins); mainline
  has no sm8475 dtsi (404) — upstream support routes through
  sm8450.
- SM8350 (888): lemonadep (OnePlus 9 Pro), pdx214 (Xperia 5 III) +
  xpeng (Moto G200); 2 populated (1,344 rows); mainline
  `sm8350.dtsi` + 7 dts; PAS full set.
- SM6225 (680 4G): devon, hawao, rhode (Moto G32/G42/G52) — 3
  populated (704 rows); **no sm6225.dtsi in mainline** (404) — same
  vendor-tree-only situation as SM7250.

### The Fairphone exemplars (1 device each — the method's proof points)

- **QCM6490 = FP5**: 706 rows/0.59 GB; BT = msbtfw\* (WCN6750) +
  hpbtfw\* (QCA2066); mainline `qcm6490-fairphone-fp5.dts` with
  `qcom,wcn6750-bt` bluetooth compatible (verified line 1537) — the
  FP6 census method applies unchanged and its upstream cross-check
  already exists.
- **SM7225 = FP4**: 286 rows; BT = crbtfw\*/apbtfw\*; mainline
  `sm7225-fairphone-fp4.dts` exists — FP4 is the cheapest full
  pipeline run (1 device, mainlined, populated DB).
- **FP6**: in the (blank) bucket upstream (SOC cell `\N`) with 447
  blob rows; the lab's FP6 census is the completed exemplar; a
  one-cell upstream fix (SOC = QCM6490/"milos") plus the
  `milos-fairphone-fp6.dts` existence (verified: 1,106 lines by
  Luca Weiss, 2025, compatible `fairphone,fp6`/`qcom,milos` —
  **the FP6 is now partially mainlined**) are the upstream-facing
  items.

## Upstream-facing summary (what LibrePhone could accept, per cluster)

Ranked by (devices covered × effort):

| # | deliverable | clusters | upstream target | effort |
|---|---|---|---|---|
| 1 | sizes.csv rows for populated devices (63 devices → 123+; zero 695/7325/8550 rows today) | all | `data/sizes.csv` | mechanical (rows exist in the DB dump) |
| 2 | SOC-cell corrections (flame, coral, guacamoleb, hotdogb, fajita; +FP6 blank cell) | 845/8150/835/FP6 | `data/` SQL/CSVs | one-session data PR |
| 3 | per-family doc stubs for the PAS clusters (modem/adsp/cdsp + WiFi + BT per decoded chip) | SM6375, SM8250, SM8150, SM8350, SM6115, SM7325, QCM6490 | `docs/` one stub per family per device-class | 1 session each, FP6-exemplar format |
| 4 | BT-fleet generation doc (Rome/WCN39xx vs WCN6750 vs QCA6390/QCA2066/WCN7850 across the DB's own filenames) | all Qualcomm clusters | extend `docs/files.md` bluetooth section / new fleet doc | small; the decode table is already in this file |
| 5 | Tensor radio-directory inventory (14-device shared-filename analysis; modem identity facts only) | Tensor | extend `docs/track.md`-style doc | medium; interface claims stay blocked |
| 6 | touch-panel firmware family template (FW_*/LIMIT_* naming grammar: vendor, panel, FAE/AGING/LIMIT variants) | SM6375, SM8250, MSM8998 | new `docs/other.md` section | small; naming grammar is DB-derivable |
| 7 | oplus fast-charge fleet doc (oplus_vooc_fw*.bin ×80+ rows) | SM8250 (+ blank bucket) | new `docs/other.md` section | small |

## Family-classification rules used in this file (reproducible)

BT prefix map (verified against mainline `btqca.c` case labels,
2026-11-16): msbtfw→WCN6750, crbtfw→WCN3990/3991/3998, apbtfw→
WCN3988, cmbtfw→WCN3950, htbtfw→QCA6390, hpbtfw→QCA2066,
wcnhpbtfw→WCN6855, hmtbtfw→WCN7850, rampatch_%08x→default.
Families: bt (the prefixes + nvn/nvram), wifi-wlan (bdwlan/wlanmac/
wmdr/wcnss/wlan/wpss/ath/regdb), modem (modem/mpss/mba/efs/fsg/modemst/
md1img/moly), dsp-audio (adsp/cdsp/slpi/venus/sns/sensor/audio),
tz (tz/keymaster/qsee/cmnlib/hyp/devcfg/uefisecapp/featenabler/hdcp/
widevine/soter/smplap/...), bootchain (xbl/abl/aop/shrm/cpucp/qupfw/
uefi/vbmeta/dtbo/splash/pbl/bl1/bl2/bl31/ldfw/...), gpu (gmu/sqe/zap/
aNNN_*), other (rest — the upstream UNKNOWN 8,664-row tail).
