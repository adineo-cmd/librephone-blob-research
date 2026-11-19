# Per-SoC upstream method plans — what LibrePhone could accept per SoC family (2026-11-17)

Upstream-facing half of the per-SoC planning layer: for each SoC family
in the LibrePhone device universe, **what the project could accept
upstream today** — (a) per-family doc stubs in `docs/`, (b)
`data/sizes.csv` rows, (c) driver-anchored interface facts — and which
census-method variant produces that material, adapting the lab's two
exemplar pipelines:

- **Qualcomm exemplar:** FP6 (QCM6490) — container walk → ISA
  identification → per-family census → interface decode
  ([fp6-architecture-census.md](../research/qualcomm/docs/fp6-architecture-census.md);
  already packaged upstream as pr1–pr8 + pr10 texts and pr7
  sizes.csv rows).
- **MediaTek exemplar:** MT6785 ("rosemary") — vendor container
  formats, per-payload record chains, ISA decode with the honest-gap
  discipline (`mediatek/docs/`: md1rom = MIPS32+MIPS16e hybrid,
  md1dsp = MD32 spec gap named, not guessed).

Companion files (read-only references, not duplicated here): the
device-universe distribution + data-quality findings live in
[blob-matrix/per-soc-method-plans.md](../research/soc/per-soc-method-plans.md);
the shared-blob fleets (QCA BT ×29 devices, ADSP bm2nXX ×22–26,
Adreno GMU) live in `blob-matrix/laptop/`; the device matrix is
[blob-database/coverage-matrix.csv](../upstream-contribution/blob-database/).

## Data basis (all committed, no re-fetch needed)

- `blob-matrix/laptop/devices-half.csv` (118 devices, rows 119–236):
  SoC populated for 28 (7 distinct strings, all Qualcomm: SDM845 ×9,
  SM6375 ×8, SM8250 ×6, SM8350 ×2, SM8150-AC ×1, SM8475 ×1, SDM636
  ×1); 90 blank; 62/118 blob-populated (16,883 rows, 31.92 GB, 7,042
  distinct md5s, 62.3 % shared-instance share).
- `blob-matrix/desktop/fragmentation-half.md` (222 devices): 89
  Qualcomm named across 29 generations, 14 Google Tensor, 3 Amlogic,
  116 blank.
- Mainline support levels re-verified 2026-11-17 against
  torvalds/master fetches: `qcom_q6v5_pas.c` PAS compatible table
  (includes `qcom,sdm845-adsp-pas`, `qcom,milos-{adsp,cdsp,mpss,wpss}-pas`),
  `ath11k/core.c` (`ATH11K_HW_WCN6750_HW10`), `qcom-cpucp-mbox.c`,
  `gunyah_wdt.c`; QSEECOM mainline = `drivers/firmware/qcom/
  qcom_qseecom.c` + `qcom_scm.c` ABI (TA-image loading NOT mainlined).
- BT chip identities per cluster decode from the upstream DB's own
  filenames through mainline `btqca.c`'s rampatch-prefix switch
  (verified 2026-11-16/17): msbtfw→WCN6750, crbtfw→WCN3990/91/98,
  apbtfw→WCN3988, cmbtfw→WCN3950, htbtfw→QCA6390, hpbtfw→QCA2066,
  wcnhpbtfw→WCN6855, hmtbtfw→WCN7850.

---

## 1. QCM6490 (Fairphone FP6) — the completed exemplar

- Cluster: FP6 upstream rows are 444 devices.csv entries with **zero
  sizes.csv rows** until pr7 (the FP6 row package, 2026-11-16); the
  upstream SOC cell is `\N` (blank-bucket member).
- Census method: the full four-phase pipeline, end-to-end committed
  (bt/bootchain/trustzone/architecture censuses + 9 interface
  one-pagers + results JSONs).
- **Upstream-acceptable (done or in packages):** pr7 sizes.csv rows
  (B-10); pr1–pr4 doc corrections; pr5 ISA corrections; pr8 interface
  docs; pr10 split/BT/radio/signed-loading comments; one-cell SOC
  fix (SOC = QCM6490). Mainline cross-check exists:
  `milos-fairphone-fp6.dts` (Luca Weiss, compatible
  `fairphone,fp6`/`qcom,milos`) — the device is partially mainlined,
  so every interface fact can be anchored to an in-tree dts/driver.
- Blocked: Hexagon disassembly (mdt tooling negative on this box) —
  modem internals and the wpss endpoint-emulator segment stay [OPEN].

## 2. MT6785 / Helio G95 (MediaTek "rosemary") — the second exemplar

- Cluster: the lab's MediaTek device doc (12 partitions, ISA map,
  `mediatek/docs/` + rosemary-census.md). Upstream has **zero
  MediaTek content** (audit C-3) — the largest open landing zone.
- Census method: the MTK variant of the pipeline — vendor container
  grammar (documented byte-for-byte in the lab docs), per-payload
  record chains, and the two decode verdicts: md1rom = MIPS32 LE
  trampoline + MIPS16e islands (nanoMIPS attribution does NOT apply
  to this generation), md1dsp = MD32 with a **named spec gap** (the
  SLEIGH spec is a stalled WIP; machine id 0x2454) — the gap is
  filed, not papered over.
- **Upstream-acceptable:** a MediaTek hardware/firmware page from the
  committed rosemary census (first MTK content upstream); md1rom/
  md1dsp/md32 doc stubs; sizes.csv rows from the rosemary census;
  interface facts for the public kernel side (mtk-serial/modem
  helpers). Owner call on timing (audit flags it as a large package).
- Blocked: MD32 payload decode (spec gap), MTK boot-chain ISA map
  beyond committed census.

## 3. SDM845 (Snapdragon 845) — the best-mainlined cluster

- Cluster: 16 devices universe-wide (9 in the laptop half's populated
  SoC set: OnePlus 6/7T-Pro class, Sony XZ2 family, Pixel 3, Poco F1,
  LG G7/V35/V40, Razer Phone 2, Shift 6MQ). DB state: nearly
  unpopulated (3 devices, 83 rows — Adreno a530 fleet + camera cpp).
- Census method: FP6 pipeline verbatim — same MDT grammar, same PAS
  loading; the WiFi anchor differs (ath10k SNOC + WCNSS NV blob, not
  ath11k).
- **Upstream-acceptable:** (a) doc stubs — the strongest landing zone
  of any cluster: `sdm845.dtsi` + 24 dts files incl. mainlined Pixel 3
  (`sdm845-google-blueline.dts`), PAS compatibles verified
  (`qcom,sdm845-adsp-pas`), modem via `qcom_q6v5_mss` — one doc stub
  per family lands on an in-tree anchor; (b) sizes.csv rows for the 13
  unpopulated devices (first-population from ~1–1.3 GB LineageOS
  packages each — fetch-plan-gated); (c) interface facts: ath10k-SNOC
  probe/download sequence, a530 GMU-less GPU firmware set (one RE pass
  frees the whole cluster's GPU story — a530_* 7 files).
- Blocked: payload RE for the unpopulated devices (packages not on
  this box).

## 4. SM6375 (Snapdragon 695) — the largest modern populated cluster

- Cluster: 15 devices universe-wide (8 in the laptop half: Moto G34/
  G82/G84/Edge 30 Neo, OnePlus Nord CE2/CE3/N20, Realme 9/10 Pro,
  Sony Xperia 10 IV/V); 12 populated at 345–506 rows each; row mass
  dominated by touch-panel firmware fleets (FW_NF_NT36672C_TIANMA
  ×28, FW_FT3518_SAMSUNG ×24, FW_NF_ILI7807S_TIANMA ×16).
- BT chips (decoded): crbtfw→WCN3990/91/98 ×28, apbtfw→WCN3988 ×16 —
  the WCN39xx generation, NOT FP6's WCN6750.
- Census method: FP6 pipeline + two additions: (a) a touch-IC census
  template (filename → vendor token → panel vendor; sizes/hashes
  only); (b) the BT census is the Rome flavor — the lab's QCA BT
  fleet doc + btqca.c's crbtfw branches cover the driver side.
- **Upstream-acceptable:** (a) per-family doc stubs (modem/adsp/cdsp/
  mpss + WCN39xx WiFi/BT) — upstream has zero 6xx-generation content;
  `sm6375.dtsi` + Xperia murray dts exist in-tree (PAS compatibles
  verified: adsp/cdsp/mpss); (b) sizes.csv rows for the 12 populated
  devices — sizes.csv has **zero 695-family rows** today (mechanical
  from the DB dump); (c) interface facts: the crbtfw/WCN39xx download
  path straight from btqca.c (public), the touch-fleet naming grammar.
- Blocked: nothing census-side; touch-IC payload RE needs packages.

## 5. SM8250 (Snapdragon 865/870) — the OnePlus-8 cluster

- Cluster: 8 devices (6 in the laptop half: OnePlus 8/8 Pro/8T/9R/9RT,
  Xperia 5 II, Moto Edge 20 Pro/Edge S); 6 populated; row mass =
  OnePlus fast-charge firmware (oplus_vooc_fw*.bin ×80+ — the ×36
  fleet's home) + Samsung touch fleets.
- BT chips (decoded): htbtfw→QCA6390 ×6, hpbtfw→QCA2066 ×4 — the
  discrete-BT-chip generation (QCA6390 is PCIe-attached, unlike
  WCN6750's UART).
- Census method: FP6 pipeline verbatim; WiFi/BT interface anchors =
  ath11k QCA6390 hw params (a genuinely different transport — PCIe
  MHI); the fast-charge/touch fleets need the vendor "other" template.
- **Upstream-acceptable:** (a) sizes.csv rows for the 6 populated
  devices; (b) a fast-charge firmware family doc (oplus_vooc_fw: one
  RE pass covers ×80+ device-rows fleet-wide — the #1 leverage
  family in the desktop half's corrected ranking); (c) interface
  facts: QCA6390 BT (htbtfw branch + PCIe transport note), ath11k
  QCA6390_HW20 anchor.
- Blocked: no OnePlus dts in mainline (checked 2026-11-16) — device
  dts anchoring waits for upstream device support; VOOC payload RE
  needs packages.

## 6. SM8150 (Snapdragon 855) — the mislabel-affected cluster

- Cluster: 5 devices universe-wide (OnePlus 7 Pro/7T Pro populated at
  435/436 rows; flame/fajita/guacamoleb/hotdogb carry wrong SOC cells
  — the data-quality finding that shifts 871 rows between clusters).
- BT chips (decoded): crbtfw ×6 + apbtfw ×4 (Rome/WCN39xx generation).
- Census method: FP6 pipeline verbatim; the data lever is the SOC-cell
  corrections themselves.
- **Upstream-acceptable:** (a) SOC-cell corrections upstream (flame =
  SDM845 not SM8150; coral = SDM845 not SM7250; guacamoleb/hotdogb =
  SM8150 not MSM8998; fajita = SDM845 not SM8150) — a small data PR
  that fixes the matrix's join keys for every downstream consumer;
  (b) sizes.csv rows for guacamole/hotdog; (c) interface facts:
  `sm8150.dtsi` + 7 dts in-tree (HDK855, Surface Duo, MTP), full PAS
  set verified.
- Blocked: payload RE for the OnePlus 7 family (packages not fetched).

## 7. SM8350 (Snapdragon 888)

- Cluster: 3 devices (OnePlus 9 Pro, Xperia 5 III, Moto G200); 2
  populated (1,344 rows).
- Census method: FP6 pipeline verbatim (same generation grammar as
  SM8250; the discrete-BT generation).
- **Upstream-acceptable:** (a) doc stubs — `sm8350.dtsi` + 7 dts
  in-tree, PAS full set; (b) sizes.csv rows for the 2 populated
  devices; (c) interface facts: same QCA6390/QCA2066 decode as SM8250
  (per-device BT filenames decide which).
- Blocked: payload RE (packages); nothing else specific.

## 8. SM7325 (Snapdragon 778G) — the BT-reuse cluster

- Cluster: 4 devices (berlin/berlna/dubai = Moto Edge 20 family,
  Spacewar = Nothing Phone 1); all populated (bluetooth.img/boot/
  vbmeta/sequence_manifest.bin ×4).
- BT chips (decoded): **msbtfw→WCN6750 ×12** (msbtfw10 + msbtfw11,
  msnv10 + msnv11) + cmbtfw→WCN3950 ×6 — the **same BT firmware
  family as the FP6**, at different patch versions; msnv10 is absent
  from FP6's partition, so this cluster extends the lab's BT census by
  one NVM generation.
- Census method: FP6 pipeline; the BT half reuses the lab's
  msbtfw/WCN6750 expertise directly (bt-firmware-census.md +
  interface-bt-driver.md — same btqca branches).
- **Upstream-acceptable:** (a) extend the BT census doc with the
  SM7325-variant rows (msnv10 vs msnv11 NVM tag diff as the first
  deliverable); (b) sizes.csv rows for the 4 populated devices
  (zero 7325-family rows today); (c) interface facts: reuse
  interface-bt-driver.md wholesale (the driver side is identical).
- Blocked/flagged: no sm7325-specific PAS entries in mainline
  (nearest resources: sm8350) — stated honestly in the plans file.

## 9. SM6115 (Snapdragon 662) — the best landing zone of the mid tier

- Cluster: 4 devices (Fxtec Pro1-X, Moto Defy 2021, Moto G30, Moto G
  Power); fully populated (967 rows).
- BT chips (decoded): cmbtfw→WCN3950 ×20.
- Census method: FP6 pipeline (older-grammar alert: WCN3950 combo
  generation).
- **Upstream-acceptable:** (a) doc stubs anchored to in-tree support:
  `sm6115.dtsi` + `sm6115-fxtec-pro1x.dts` + `sm6115-xiaomi-lemon.dts`
  (the Pro1-X is an official mainline-adjacent device — the cluster's
  natural first stub), PAS full set (adsp/cdsp/mpss) verified;
  (b) sizes.csv rows for the 4 populated devices; (c) interface
  facts: the cmbtfw/WCN3950 download path from btqca.c.
- Blocked: payload RE (packages not fetched).

## 10. Google Tensor (GS101/GS201/G3/G4) — the non-Qualcomm contrast

- Cluster: 14 devices (Pixel 6 → 9 Pro Fold), every one populated with
  a uniform Arm-trusted-boot file set (abl/bl1/bl2/bl31/tzsw/pbl/ldfw
  ×14 — identical filenames, one grammar; no Qualcomm MDT anywhere).
- Census method: the **MT6785-style grammar** (vendor containers,
  raw-AArch64 identification, DTB/DTBO parsing) adapted to Samsung's
  chain — NOT the FP6 pipeline; interface decode is blocked on AOSP
  kernel sources (no gs101/gs201/zuma dtsi in torvalds master —
  verified 2026-11-16).
- **Upstream-acceptable:** (a) a **radio-directory inventory doc per
  Tensor device** (what files, sizes, hash identity across the 14 —
  the DB already shows shared filenames; the Exynos modem is the
  freedom-critical blob and this is the honest, interface-claim-free
  deliverable); (b) sizes.csv rows (all 14 devices); (c) SOC-cell
  additions (caiman/comet are public Tensor G4).
- Blocked: all interface claims until the AOSP kernel cross-reference
  is done (exynos9820-era drivers; gs101/gs201 are public in AOSP —
  citable but not mainline).

---

## Upstream acceptance summary (ranked by devices covered × effort)

| # | deliverable | SoC families | upstream target | evidence class | effort |
|---|---|---|---|---|---|
| 1 | sizes.csv rows for populated devices (zero 695/7325/8550 rows today; FP6 rows packaged as pr7) | all Qualcomm clusters + Tensor | `data/sizes.csv` | METADATA (from the DB dump / committed censuses) | mechanical |
| 2 | SOC-cell corrections (flame, coral, guacamoleb, hotdogb, fajita, caiman/comet; FP6 blank cell) | SDM845/SM8150/SM7250/Tensor/FP6 | `data/` CSVs + SQL | METADATA (public device identity vs recorded cell) | one-session data PR |
| 3 | per-family doc stubs for the PAS clusters (modem/adsp/cdsp + WiFi + BT per decoded chip) | SM6375, SM8250, SM8150, SM8350, SM6115, SM7325, SDM845, QCM6490 | `docs/` one stub per family per device-class | census + mainline anchors (verified per family above) | 1 session each, FP6-exemplar format |
| 4 | BT-fleet generation doc (WCN39xx vs WCN6750 vs QCA6390/QCA2066/WCN7850 across the DB's own filenames; driver side = btqca.c branches) | all Qualcomm clusters | extend `docs/files.md` bluetooth section / new fleet doc | METADATA + PUBLIC kernel | small; decode table committed |
| 5 | Tensor radio-directory inventory (14-device shared-filename analysis) | Tensor | `docs/` (track.md-style) | METADATA only; interface claims stay blocked | medium |
| 6 | touch-panel firmware family template (FW_*/LIMIT_* naming grammar: vendor, panel, FAE/AGING variants) | SM6375, SM8250, MSM8998 | new `docs/other.md` section | METADATA (DB-derivable grammar) | small |
| 7 | oplus fast-charge fleet doc (oplus_vooc_fw*.bin, ×36-device fleet) | SM8250 (+ blank bucket) | new `docs/other.md` section | METADATA + one payload RE pass when packages land | small |
| 8 | MediaTek first-content package (rosemary census → hardware page + md1rom/md1dsp/md32 stubs + sizes rows) | MT6785 | `docs/` + `data/` | census (committed) | owner call (large) |

## Honest limits

- Row counts and BT decodes above are **metadata-level** (upstream SQL
  md5/size + filename grammar); payload RE for the non-FP6 clusters is
  fetch-plan-gated (~1–1.3 GB per device package) and stated as
  blocked where it is.
- Mainline support claims were re-verified 2026-11-17 (fetch log in
  the companion docs); the two negative results (no sm7250/sm6225/
  sm8475/gs101 dtsi; no mainline TA-image loader) are recorded as
  negatives, not assumed.
- SOC-cell contradictions mean cluster row-counts are reported under
  the DB's labels as-is; fixing the labels (deliverable #2 above) is
  itself an upstream contribution.

## Sources

- Committed: `blob-matrix/laptop/devices-half.csv`,
  `blob-matrix/laptop/fragmentation-half.md` + summary JSON,
  `blob-matrix/desktop/fragmentation-half.md`,
  `blob-matrix/per-soc-method-plans.md` (universe distribution +
  mislabels), `blob-matrix/laptop/qualcomm-{qca-bt,adsp-bm2n,adreno-gmu}-fleet.md`,
  `upstream-contribution/blob-database/coverage-matrix.csv`,
  `upstream-contribution/pr7-sizes-fp6.md`,
  `qualcomm-fp6/docs/*` (the FP6 exemplar), `mediatek/docs/*` (the
  MT6785 exemplar).
- Public (torvalds/linux master, fetched 2026-11-16/17, failures
  logged): `drivers/remoteproc/qcom_q6v5_pas.c` (PAS compatible
  table), `drivers/net/wireless/ath/ath11k/core.c` (WCN6750_HW10),
  `drivers/bluetooth/btqca.{c,h}` (rampatch-prefix switch),
  `drivers/firmware/qcom/qcom_qseecom.c` + `Kconfig` + `qcom_scm.c`,
  `drivers/mailbox/qcom-cpucp-mbox.c`, `drivers/watchdog/gunyah_wdt.c`;
  dts/dtsi presence per cluster per the plans file's 2026-11-16
  fetches.
