# Historic-device universe extension — the RE queue beyond the upstream 236 (2026-11-17)

The owner's directive: historically MANY mobile devices need blob RE — extend
beyond the LibrePhone upstream 236. This file builds that queue from the
four community "devices people actually want freed" lists, cross-references
every candidate against the upstream universe (249 inventory identities),
and applies RULE 0 (existing pmOS/Replicant/LineageOS/UBports documentation
cited, not duplicated; the lab's delta is **blob-level documentation per
device**, which none of those projects produce).

## 1. Headline finding — the upstream list skews modern, and the free-software flagship is missing

1. **Fairphone FP2 is not in the upstream universe at all.** The FSF-era
   famous free-software phone (2015; Replicant 6.0 100%-free device,
   UBports official port, postmarketOS port) is absent from
   `device-inventory.csv` (fairphone rows = FP3/FP4/FP5/FP6 only; verified
   by codename grep 2026-11-17) and absent from the /e/OS supported table
   too. The single most culturally important historic device for this
   program is uncovered.
2. Cross-checked against the upstream 249: of the classic RE-target devices
   below, **every row is ABSENT except Mi 5 (`gemini`), Essential PH-1
   (`mata`), F(x)tec Pro 1/1X, OnePlus 6/6T, Mi 6, POCO F1, Mi 8, Pixel 3**.
   The upstream list is a 2016-2024 Snapdragon + Tensor fleet (its
   `builds.csv` SOC strings are 29 Snapdragon generations; no pre-2016
   device survives). Nothing from the 2011-2015 era is covered.
3. The historic universe is big: **214 non-archived + 457 archived device
   packages in postmarketOS pmaports alone** (671 total), 604 devices
   currently listed by the LineageOS wiki, 111 Ubuntu Touch ports, 287
   /e/OS table rows, 10+ Replicant-supported devices — with tiny overlap
   between the lists (a device can be freed four ways and still be in none
   of them upstream).
4. The lead's P1 pointer included "Gryphon" — **no public codename match**
   (GitHub/LineageOS/pmOS searches, 2026-11-17, 0 hits for a phone device
   tree of that name). P1 below is therefore defined operationally:
   devices with active free-software communities. If "Gryphon" refers to a
   specific device the lead knows, it slots into P1 with the same blob
   treatment.

## 2. Sources (all fetched 2026-11-17, route + size logged)

| # | source | URL | result | route notes |
|---|---|---|---|---|
| S1 | postmarketOS pmaports device packages (the wiki's own package source of truth; the wiki is generated from it) | `https://gitlab.postmarketos.org/api/v4/projects/postmarketOS%2Fpmaports/repository/tree?path=device/<cat>&recursive=true&per_page=100&page=N` | **671 device packages**: community 38, testing 157, downstream 19, archived 457, main 0 (main = shared components only) | `wiki.postmarketos.org` is behind an **Anubis anti-bot proof-of-work gate** (page + api.php both 403/challenge, 2 UA variants tried) — pmaports used instead; it is strictly more authoritative for "what has a port" |
| S2 | LineageOS official supported devices | `https://wiki.lineageos.org/devices/` (full index HTML fetched) | **604 device pages** (current support list — historically-supported devices are dropped from the wiki when support ends; their device trees remain on GitHub) | direct fetch, 2,495,778 B |
| S3 | LineageOS installed-base stats (demand signal: what people actually run) | `https://stats.lineageos.org/api/v1/stats` | 250 codenames with installs, 1,439,442 total | SPA shell at `/` needed bundle grep to find `/api/v1/stats` |
| S4 | Ubuntu Touch ports | `https://devices.ubuntu-touch.io/` | **111 device codenames** (incl. release channel xenial/focal per link) | Astro static site, links parsed from HTML |
| S5 | /e/OS supported devices | `https://doc.e.foundation/devices` | **287 device rows** (24 on the official channel, incl. FP3/FP4/FP5/FP6; rest community installs) | server-rendered table (`<tr data-device-type=…>`), parsed per row |
| S6 | Replicant supported devices | `https://replicant.us/supported-devices.php` | Galaxy Nexus, S2, S3(+4G), Note, Note 2, Note 8.0, Tab 2 7/10, GT-I9000… | fetched, 10,795 B |
| S7 | upstream universe (cross-ref target) | repo: `upstream-contribution/blob-database/device-inventory.csv` (249 identities) + `blob-matrix/laptop/devices-half.csv` | membership by codename grep | — |

Overlap of S1-S6 with upstream, verified by codename: only FP3/FP4/FP5/FP6,
mata, gemini, pro1/pro1x, enchilada/fajita, beryllium, dipper, blueline,
sagit, kirin, devon, axolotl, and a few crosshatch/flame-era Pixels are in
the upstream 249 — i.e. the four community lists and upstream intersect on
roughly **a dozen devices**. Everything else in this queue is unreached by
the upstream program.

## 3. The queue

Columns: codename; year; SoC; blob families of interest (the blob-level
targets); where payloads are obtainable (all from public LineageOS/pmOS/UBports
builds or vendor trees — same individually-fetchable pattern Mission 1
proved for the QCA fleet); the known-hard blob; existing effort (RULE 0);
priority (P1 free-software-community device / P2 popular legacy / P3 long
tail); upstream-236 status (all ABSENT unless noted).

### P1 — free-software-community devices

| device (codename) | yr | SoC | blobs of interest | payloads from | known-hard blob | existing effort (RULE 0) | upstream? |
|---|---|---|---|---|---|---|---|
| Fairphone FP2 (`FP2`) | 2015 | MSM8974AB-v2 (SD801) | modem `mpss` (8974), WCN3680 WiFi/BT/FM (prima `wlan/prima`, `wcnss.mdtt`-class), adsp, sensors | pmOS testing image; LineageOS 18.1-21 community builds; Replicant 6.0; UBports official | **WCN3680 prima firmware + 8974 modem** (Replicant documents WiFi/modem as the residual nonfree items) | pmOS testing (device-fairphone-fp2); Replicant 6.0 supported; UBports official (focal) | ABSENT |
| PinePhone 1.2 (`pine64-pinephone`) | 2019 | Allwinner A64 | RTL8723CS WiFi/BT firmware; EG25-G modem (Qualcomm MDM9x07-class inside a Quectel module — fully opaque); Mali-400 GPU is FREE (lima) | pmOS testing image; UBports; Megi's kernel trees | **EG25-G modem internals** (the only nonfree piece with RE interest; AT/QMI surface already documented by community) | pmOS testing; UBports community; extensive mainline docs (megous) | ABSENT |
| PinePhone Pro (`pine64-pinephonepro`) | 2021 | RK3399S | minimal — mainline nearly everything; optional M.2 modem | pmOS community | modem module if fitted | pmOS community | ABSENT |
| Purism Librem 5 (`purism-librem5`) | 2019 | NXP i.MX8M | Redpine RS9116 WiFi firmware (known-hard), BM818/M.2 modem (Qualcomm class inside), GC7000 GPU is FREE (etnaviv) | PureOS + pmOS community; Purism publishes schematic-level docs | **RS9116 firmware** (the last big blob; Purism has documented modem/vboot parts extensively) | pmOS community; Purism's own docs (librem5-devkit) | ABSENT |
| Nokia N900 (`nokia-n900`) | 2009 | TI OMAP3430 | TI WL1273 WiFi/BT firmware; Calypso GSM modem (RE'd: OsmocomBB layer1 is free); ads7846 touch is plain Linux | pmOS community image; Maemo-era firmware dumps | WL1273 firmware (in linux-firmware, still a blob); modem is the historic success story | pmOS community (strong page); OsmocomBB; Neo900 heritage | ABSENT |
| Samsung Galaxy S3 i9300 (`samsung-m0`) | 2012 | Exynos 4412 | BCM4330 WiFi/BT + nvram; XMM6262 modem via Samsung-IPC userspace (Replicant heritage, free load protocol); MFC codec | pmOS community image; Replicant 6.0 | **BCM4330 firmware + Samsung-IPC modem bring-up** (protocol free, firmware blob) | pmOS community; Replicant 6.0 supported; mainline Linux port (wichtel/SCRIPTed) | ABSENT |
| Nexus 10 (`google-manta`) | 2012 | Exynos 5250 | bcmdhd WiFi class (BCM4330-family) + nvram; Exynos MFC; modem n/a (tablet) | pmOS community | Exynos 5-series display/codec blobs | pmOS community | ABSENT |
| SHIFT6mq (`shift-axolotl`) | 2020 | SD845 | same blob family as OnePlus 6 (WCN3990 TLV fleet — Mission 1 files apply!) | pmOS community; SHIFT's own images | covered by the fleet analysis + SDM845 common trees | pmOS community; SHIFT officially friendly | **COVERED** (shift/Shift_6MQ) |
| Fairphone FP1 (`fairphone-fp1`) | 2013 | MT6589 | MOLY modem stack (MediaTek), MT6628 WiFi/BT combo, MediaTek preloader/LK | pmOS downstream image; FP1-era LineageOS | **MTK MOLY modem + MT6628 combo** — opens the entire MediaTek historic family | pmOS downstream | ABSENT |
| Openmoko Neo FreeRunner + Neo900 | 2008/… | S3C2442 / OMAP3530 | Calypso modem (free via OsmocomBB); the only fully-free modem lineage ever | historic; GTA02 archives; Neo900 project repo (on hold) | none left — the monument | OsmocomBB, Neo900 | ABSENT |

### P2 — popular legacy (the classic RE-target devices)

| device (codename) | yr | SoC | blobs of interest | payloads from | known-hard blob | existing effort (RULE 0) | upstream? |
|---|---|---|---|---|---|---|---|
| Nexus 4 (`mako`) | 2012 | APQ8064T | modem 8960, WCN3660 prima, adsp | pmOS archived; LineageOS 18.1-era builds (dropped from wiki) | WCN3660 prima fw | pmOS archived; long LineageOS history | ABSENT |
| Nexus 5 (`hammerhead`) | 2013 | MSM8974 | modem `mpss` 8974, **WCN3680 prima**, adsp, venus | pmOS **testing**; LineageOS 14.1-18.1 builds; UBports community | WCN3680 prima + 8974 modem | pmOS testing; UBports community | ABSENT |
| Nexus 6 (`shamu`) | 2014 | APQ8084 | modem 8084, WCN3660B prima, adsp | LineageOS builds; pmOS absent | prima fw | LineageOS heritage | ABSENT |
| Nexus 5X (`bullhead`) | 2015 | MSM8992 | modem 8992, **BCM4356** WiFi/BT, venus | LineageOS 14.1-15.1 builds | BCM4356 firmware + nvram | LineageOS heritage | ABSENT |
| Nexus 6P (`angler`) | 2015 | MSM8994 | modem 8994, **BCM4356**, adsp | LineageOS builds; device trees live on GitHub | BCM4356 fw | LineageOS heritage | ABSENT |
| Nexus 7 2013 (`flo`/`deb`) | 2013 | APQ8064T | WCN3660 prima, adsp | pmOS archived (flo); LineageOS builds | prima fw | pmOS archived | ABSENT |
| Nexus 9 (`flounder`) | 2014 | Tegra K1 | BCM4356; NVIDIA Tegra bc, DSI panel chain | LineageOS builds; pmOS archived | Tegra display/avp blobs | pmOS archived | ABSENT |
| OnePlus One (`bacon`) | 2014 | MSM8974AC | modem 8974, WCN3660 prima, adsp | pmOS **testing**; LineageOS builds | prima fw | pmOS testing; the single most-flashed custom-ROM device of its era | ABSENT |
| OnePlus 2 (`oneplus2`) | 2015 | MSM8994 | modem 8994, combo chip per vendor tree (not pinned this session), adsp | pmOS archived | 8994 modem | pmOS archived | ABSENT |
| OnePlus 3/3T (`oneplus3`) | 2016 | MSM8996 | modem 8996, `qcwcn` WiFi/BT (BoardConfig `BOARD_WLAN_DEVICE:=qcwcn`, verified this session), adsp, venus | pmOS archived; LineageOS 14.1-18.1 | qcwcn prima-class fw | pmOS archived | ABSENT |
| Galaxy S4 LTE (`jfltexx`) | 2013 | APQ8064T | modem 8960, WCN3680, adsp | pmOS archived; Replicant-adjacent trees | prima fw | pmOS archived | ABSENT |
| Galaxy S5 (`klte`) | 2014 | MSM8974 | modem 8974, WCN3680, adsp | pmOS archived; LineageOS builds | prima fw | pmOS archived | ABSENT |
| Galaxy Note 3 (`hlte`) | 2013 | MSM8974 | same family as S5 | pmOS archived | prima fw | pmOS archived | ABSENT |
| Galaxy S6 (`zerofltexx`) | 2015 | Exynos 7420 | **BCM4359** WiFi/BT (verified in universal7420 vendor lists), Samsung-IPC modem (Shannon333) | pmOS testing-era trees; mainline project exists | **Shannon modem + BCM4359 fw** | mainline Linux port; LineageOS 18.1 unofficial | ABSENT |
| Galaxy S7 (`herolte`) | 2016 | Exynos 8890 | Shannon 359 modem, BCM4359-class combo | pmOS archived; LineageOS 18.1-21 | **Shannon 359 modem** (mainline projects exist) | pmOS archived; LineageOS heritage; installed base 52,588+52,360 = ~105k (S3 source) — biggest legacy install base | ABSENT |
| Galaxy Note 8 (`greatlte`) | 2017 | Exynos 8895 | Shannon 363 modem, Broadcom combo | LineageOS official-era builds; installed base 21,031 | Shannon modem | LineageOS heritage | ABSENT |
| Galaxy S2 (`i9100`) | 2011 | Exynos 4210 | BCM4330, XMM6272 modem via Samsung-IPC | Replicant 6.0; historic LineageOS | Samsung-IPC + BCM4330 | Replicant 6.0 supported | ABSENT |
| Galaxy Note 2 (`n7100`) | 2012 | Exynos 4412 | BCM4330, XMM6262 modem | Replicant 6.0 | Samsung-IPC + BCM4330 | Replicant 6.0 supported | ABSENT |
| Galaxy Tab 2 7/10 (`p31xx`/`p51xx`) | 2012 | OMAP4430 | WL1273 TI firmware, XMM modem | Replicant 6.0 | TI combo fw | Replicant 6.0 supported | ABSENT |
| Galaxy Nexus (`maguro`) | 2011 | OMAP4460 | WL1285 TI combo, XMM6270 modem | Replicant 6.0; pmOS-era trees | TI combo fw | Replicant 6.0 supported | ABSENT |
| Xperia Z (`yuga`) | 2013 | APQ8064 | WCN3660, modem 8960 | pmOS archived | prima fw | pmOS archived | ABSENT |
| Xperia Z1 (`honami`) | 2013 | MSM8974 | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| Xperia Z3 Compact (`amami`) | 2014 | MSM8974 | WCN3680, modem 8974 | pmOS archived; huge community | prima fw | pmOS archived | ABSENT |
| Xperia X (`suzu`) | 2016 | MSM8952 | WCN3660B?/combo per vendor tree, modem 8952 | UBports community | 8952 modem | UBports community | ABSENT |
| LG G2 (`d802`) | 2013 | MSM8974 | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| LG G3 (`d855`) | 2014 | MSM8974AC | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| LG G4 (`h815`) | 2015 | MSM8994 | combo per vendor tree, modem 8994 | pmOS absent; mainline project exists | 8994 modem | mainline port (G4 mainline project) | ABSENT |
| Moto G 2013 (`falcon`) | 2013 | MSM8226 | modem 8226, WCN3620 combo | pmOS archived | 8226 modem | pmOS archived | ABSENT |
| Moto G 2014 (`titan`) | 2014 | MSM8226 | modem 8226, WCN3620 | pmOS archived | 8226 modem | pmOS archived | ABSENT |
| Moto G 2015 (`osprey`/`merlin`) | 2015 | MSM8916 | modem 8916 (known pmOS hard case), WCN3660B | pmOS archived | **MSM8916 modem** (pmOS documentation discusses its difficulty) | pmOS archived | ABSENT |
| Moto X 2014 (`victara`) | 2014 | MSM8974AC | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| Xiaomi Mi 4 (`cancro`) | 2014 | MSM8974 | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| Xiaomi Mi A1 (`tissot`) | 2017 | SD625 (MSM8953) | modem 8953, WCN3680B? per tree; pmOS has generic-qcom-msm8953 | pmOS msm8953 community target; LineageOS builds; installed base 15,661 | 8953 modem (pmOS msm8953 effort documents it) | pmOS community (device-qcom-msm8953 generic); LineageOS heritage | ABSENT |
| Redmi Note 4 (`mido`) | 2017 | SD625/MT6797 | same 8953 family | LineageOS builds | 8953 modem | LineageOS heritage | ABSENT |
| Nokia N9 (`nokia-n9`) | 2011 | TI OMAP3630 | WL1271 TI combo, modem (ST-Ericsson) | pmOS archived | TI combo fw | pmOS archived (MeeGo heritage) | ABSENT |
| BQ Aquaris E4.5 Ubuntu Edition (`krillin`) | 2015 | MT6582 | MOLY modem, MT66 combo | UBports heritage trees | MTK MOLY stack | UBports historic flagship | ABSENT |
| Meizu Pro 5 (`arale`) | 2015 | Exynos 7420 | BCM4356-class combo (pin per vendor tree), Shannon modem via Samsung-IPC | UBports official (xenial) | Samsung-IPC + combo fw | UBports official | ABSENT |
| HTC One M7 (`m7ul`) | 2013 | APQ8064T | WCN3660, modem 8960 | pmOS absent; LineageOS heritage | prima fw | LineageOS heritage | ABSENT |
| HTC One M8 (`m8`) | 2014 | MSM8974AC | WCN3680, modem 8974 | pmOS archived | prima fw | pmOS archived | ABSENT |
| HTC 10 (`pme`) | 2016 | MSM8996 | qcwcn, modem 8996 | pmOS absent; LineageOS heritage | qcwcn fw | LineageOS heritage | ABSENT |
| Essential PH-1 (`mata`) | 2017 | SDM845 | the SDM845 blob set — carries crbtfw20.tlv/crnv20.bin (Mission 1 sources came from mata's own vendor tree) | LineageOS 18.1-22.2 official-era builds (TheMuppets mata tree verified in Mission 1) | SDM845 modem | LineageOS official heritage | **COVERED** (essential/PH_1) |

### P3 — long tail (enumerated, not row-documented)

The long tail is enumerated in Appendix A (full lists) rather than
row-documented: 157 pmOS testing devices (from `device-sony-amami`-class
archive returns to `device-xiaomi-ido`-class downstream keepers), 457
archived pmOS devices (every device pmOS ever ported but retired), the
historic tail of the 604 LineageOS wiki devices, 111 Ubuntu Touch ports,
287 /e/OS rows. Priority within P3 = the LineageOS installed-base ranking
(S3 source): herolte ~105k installs, sagit 48k (covered), greatlte 21k,
tissot 16k, chiron 13k, crownlte 12k… — i.e. the Exynos 8890/8995 Shannon
modem family is the highest-demand P3 cluster.

## 4. Fragmentation insight for HISTORIC devices

Historic devices repeat SoCs far more than modern ones — one RE pass frees
whole eras:

| SoC / platform | devices above sharing it | blob families RE'd once |
|---|---|---|
| MSM8974 / APQ8064T (SD800/801 era, 2012-2015) | FP2, Nexus 5, OnePlus One, LG G2/G3, Moto X 2014, Sony Z1/Z3, Mi 4, S5, Note 3, HTC M8 | 8974 modem (mpss), **WCN3680/WCN3660 prima firmware**, adsp — the prima firmware family is COMPLETELY different from the modern WCN399x TLV fleet (Mission 1) and is the single biggest historic blob family |
| MSM8994/8992 (SD808/810, 2015) | Nexus 5X/6P, OnePlus 2, LG G4, Xperia Z5 | 8994/8992 modem + BCM4356 combo |
| MSM8996 (SD820/821, 2016) | OnePlus 3/3T, HTC 10, Xperia XZ, Mi 5 (covered) | 8996 modem + qcwcn combo |
| MSM8226/8916 (2013-2016 budget) | Moto G 2013/2014/2015 | small modems + WCN36xx — the pmOS budget-phone universe |
| MSM8953 (SD625, 2017) | Mi A1, Redmi Note 4, pmOS generic-msm8953 | 8953 modem — pmOS has an ACTIVE generic target |
| Exynos 4412/5250 (2012) | S3, Note 2, Nexus 10, Replicant set | BCM4330 + Samsung-IPC/XMM modems — protocol free (Replicant), firmware blob |
| Exynos 7420/8890/8895 (2015-2017) | S6, S7, Note 8, Meizu Pro 5 | **Shannon modem** (the un-RE'd Samsung modem lineage) + BCM4359-class |
| OMAP3/4/5 TI | N900, Galaxy Nexus, Tab 2 | TI WL12xx combo firmware; Calypso modem already free (OsmocomBB) |
| MediaTek MT6589/82 | FP1, Aquaris E4.5 | MOLY modem + MT66xx combos — the historic-MTK gate |

Blob-family insight: the historic WiFi/BT gate is **WCN36xx prima** (the
8974 era's integrated combo — ~15 devices above) and **Broadcom bcmdhd
(BCM4330/4339/4356/4359)** — both completely different firmware containers
from the modern QCA TLV fleet; the historic modem gate is either **Qualcomm
mpss (per generation)** or **Samsung-IPC Shannon/XMM** or **MTK MOLY**.
Mission 1's fleet analysis + this table together now cover the BT blob
families of both the modern (TLV) and the 8974-era (prima) Qualcomm fleets.

## 5. Recommended first-3 RE targets

1. **Fairphone FP2** (P1, 2015, MSM8974AB-v2). The free-software flag the
   FSF-leaning community actually holds up — and it is absent from the
   upstream 236, so the lab owns it outright. Its blob set (8974 modem +
   WCN3680 prima + adsp) is exactly the MSM8974-era cluster (§4 row 1), so
   the documentation transfers to Nexus 5, OnePlus One, LG G3, Sony Z3 and
   the rest. Payloads: small pmOS testing / LineageOS community builds;
   RULE 0 anchoring exists (Replicant's freedom audit, pmOS page) but no
   project produces blob-level docs — pure delta.
2. **Nexus 5 `hammerhead`** (P2, 2013). Same blob families as FP2 (one RE
   pass, two flagships), the most-bought-and-flashed 8974 device, pmOS
   testing + UBports community + years of LineageOS builds to diff blobs
   against; every payload individually fetchable.
3. **Galaxy S3 `samsung-m0`** (P1/P2 bridge, 2012). pmOS *community*
   (actively maintained), Replicant 6.0's other 100%-free device, and a
   completely different modem lineage (Samsung-IPC + XMM6262 + BCM4330) —
   the pass that opens the Exynos/Samsung-IPC universe (S2, Note 2, Galaxy
   Nexus, Meizu Pro 5, S6/S7 Shannon family) rather than a second
   Qualcomm generation.

## Appendix A — source lists (fetched verbatim, 2026-11-17)

### A1. postmarketOS pmaports device packages (671)

- **community (38)**: device-fairphone-fp4, device-generic-ppc64le,
  device-generic-x86_64, device-google-asurada, device-google-bonito,
  device-google-cherry, device-google-corsola, device-google-gru,
  device-google-kukui, device-google-manta, device-google-oak,
  device-google-peach-pit, device-google-sargo, device-google-trogdor,
  device-google-veyron, device-google-x64cros, device-lenovo-21bx,
  device-nokia-n900, device-odroid-xu4, device-oneplus-enchilada,
  device-oneplus-fajita, device-pine64-pinebookpro, device-pine64-pinenote,
  device-pine64-pinephonepro, device-pine64-rockpro64,
  device-purism-librem5, device-qcom-msm8953, device-qcom-qcs6490,
  device-qcom-sm7150, device-qemu-aarch64, device-qemu-amd64,
  device-samsung-coreprimevelte, device-samsung-espresso10,
  device-samsung-espresso7, device-samsung-m0, device-samsung-starqltechn,
  device-shift-axolotl. (Phone-class devices — PinePhone, FP2, Nexus 5,
  OnePlus One — verified this session to sit under **device/testing** in
  current pmaports; the community category holds
  mainline-chromebook/tablet-class devices plus n900, m0, manta, librem5,
  axolotl.)
- **testing (157)** and **downstream (19)**: full machine lists retained in
  scratch (`/tmp/astro_s/pmos_devices_all.json`, regeneratable via the
  route in §2 S1). Historic-relevant downstream picks: device-fairphone-fp1,
  device-xiaomi-ido (Redmi 1S), device-lg-elsa (L Bello), device-lg-vee3e
  (G2 mini), device-samsung-j4lte, device-samsung-m20lte,
  device-htc-golfu, device-bq-gohan, device-amazon-sheldon.
- **archived (457)**: every retired pmOS port — the long tail's long tail;
  counts by category in the JSON; notable archived members verified this
  session: device-lg-hammerhead's sibling generations, device-sony-amami/
  yuga/honami, device-samsung-klte/herolte, device-xiaomi-cancro/gemini,
  device-google-crosshatch/manta-class tablets, device-htc-m8,
  device-oneplus-oneplus2/oneplus3, device-motorola-titan/falcon,
  device-nokia-n9, device-essential-mata.

### A2. Ubuntu Touch ports (111 codenames)

algiz, amar-row-lte, amar-row-wifi, angelica, angelican, angler, ansuz,
arale, axolotl, bacon, begonia, beryllium, beyond0lte, beyond1lte,
beyond2lte, billie, billie2, biloba, bonito, cancro, cheeseburger, citrus,
cooler, cosmo-communicator, curtana, d2s, deb, denniz, dipper, dora,
dumpling, enchilada, excalibur, fajita, flo, (…full list in scratch
`/tmp/astro_s/ut_devices.txt`) — including the historic UT flagships
(arale = Meizu Pro 5, bacon = OnePlus One, angler = Nexus 6P, cancro =
Mi 4) and the LP-environment devices.

### A3. /e/OS table (287 rows; 24 official channel)

Brand distribution: Xiaomi 61, Motorola 41, Samsung 37, OnePlus 34,
Google 28, LG 22, Sony 19, Nubia 8, Fairphone 4 (FP3/FP4/FP5/FP6 — FP2
absent), Asus 3, Nothing 3, Razer 3, BQ 2, F(x)tec 2, Essential 1,
Gigaset 1, SHIFT 1, Solana 1, ZUK 1 (scratch: `efdn_devices.json`).

### A4. Replicant supported (from fetched page)

Galaxy Nexus (maguro/toro), Galaxy S (GT-I9000), S 2 (GT-I9100),
S 3 (GT-I9300 + 4G), Note (GT-I9250/N7000), Note 2 (N7100),
Note 8.0 (GT-N5110), Tab 2 7.0/10.1 (P31xx/P51xx), Nexus S-era GT-I9020
heritage devices.

### A5. LineageOS installed-base top (historic-relevant only; S3)

herolte 52,588 + hero2lte 52,360 (Galaxy S7/S7 Edge), greatlte 21,031
(Note 8), tissot 15,661 (Mi A1), crownlte 12,251 (Note 9), starlte 26,548
(S9), chiron 13,379 (Mi 6 Plus-era), j7y17lte 11,701 — versus covered
devices: sagit (Mi 6) 48,267, dipper (Mi 8) 33,767, instantnoodlep 33,803
(OnePlus 8? — modern). The uncovered legacy installed base rivals the
covered one: more evidence the list skews modern.

## Appendix B — method + honesty notes

- Membership greps were run against `build_codename` in
  `device-inventory.csv` (2026-11-17); every "ABSENT" claim in the queue
  table was checked individually (incl. alias attempts m7/m7ul, FP1/FP2).
- WiFi/BT combo chips: pinned this session for FP2 (WCN3680), hammerhead
  (WCN3680), oneplus3 (qcwcn via BoardConfig fetch), zerofltexx (BCM4359
  via universal7420 proprietary-files search); where a combo could not be
  verified this session the row says so — pinning those is exactly the
  per-device blob documentation the lab should produce next.
- `wiki.postmarketos.org` Anubis gate: both `wiki.postmarketos.org/wiki/Devices`
  and `/w/api.php` returned the Anubis challenge (2 user-agents tried);
  pmaports GitLab API used as the authoritative substitute. A browser-tool
  pass could retrieve the wiki's mainline-status columns per device as a
  follow-up session.
- Years/SoCs in the queue table are well-established device facts, not
  fetched per-device from the blocked wiki; the blob columns are the lab's
  new content. Payload obtainability column reflects the Mission 1 route
  proof (LineageOS/TheMuppets/pmOS/vendor trees, individually fetchable).
- No git commit / no push (per instructions). Scratch:
  `/tmp/astro_s/` (pmOS JSONs, UT list, e-fdn JSON, lineage stats JSON,
  lineage wiki index, replicant page).
