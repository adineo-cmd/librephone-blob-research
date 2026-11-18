# Fairphone FP2 — real-payload blob census + RE (2026-11-18)

The historic-device program's **first content-level RE**: the Fairphone FP2
(MSM8974AB-v2, the free-software flagship that is absent from the upstream
249) had every obtainable firmware blob located in public repositories,
fetched, hash-verified against an independent pin (postmarketOS pmaports),
and run through the lab's new clean-room parsers (`mdt_probe.py` for the
split-peripheral-image family, `prima_nv_probe.py` for the WCNSS NVRAM).
This file documents what the real bytes actually contain, per parsed byte
range. No payload bytes are committed here — payload files live only in
`/tmp/astro_w/payloads/` (regeneratable via the route log below); everything
below is derived structural fact.

Clean-room statement: `mdt_probe.py` was written from GPL kernel sources
only (`drivers/soc/qcom/mdt_loader.c` + `include/linux/soc/qcom/mdt_loader.h`
@ torvalds/linux master); `prima_nv_probe.py` from the prima driver's GPL
sources (`drivers/staging/prima/CORE/VOSS/src/wlan_nv_parser.c`,
`wlan_nv_stream_read.c`, `CORE/VOSS/inc/wlan_nv_template_internal.h`,
`riva/inc/wlan_nv.h` @ CyanogenMod/android_kernel_oppo_msm8974 cm-12.1 /
android_kernel_motorola_msm8916). Both carry full CLEAN-ROOM STATEMENT
headers; synthetic fixtures + 28 tests in `fixtures/` + `test_parsers.py`
pass on this session's code.

## 1. Provenance and verification

FP2 firmware is **not** in the LineageOS vendor tree (TheMuppets
`proprietary_vendor_fairphone` FP2 ships only venus/adreno/cpp firmware +
userspace libs — the modem/WCNSS/ADSP images are absent there), and **not**
in the Fairphone opensource GitHub org (`user:Fairphone` search returns only
FP5-era repos; no `WW-FP2` repo exists — route tried, see §1.2). The
obtainable public source is a community extraction repo pinned by
postmarketOS:

### 1.1 The pmaports-pinned tarball (84 of 90 files)

`device/testing/firmware-fairphone-fp2` APKBUILD (fetched from
gitlab.postmarketos.org, 2026-11-18) pins:

| artifact | pin | result |
|---|---|---|
| `FP2-firmware-17.09.3.tar.gz` @ `github.com/FairBlobs/FP2-firmware` tag `17.09.3` | sha512 `f4af05a7…681` (full pin in the APKBUILD) | **MATCH** |
| `WCNSS_cfg.dat`, `WCNSS_qcom_cfg.ini`, `WCNSS_qcom_wlan_nv.bin` @ `LineageOS/android_device_fairphone_FP2` @ commit `67850874…a1d`, `wifi/` | 3 sha512 pins in the same APKBUILD | **3/3 MATCH** |

The tarball (32,193,375 B) contains 81 files: `modem.mdt`+`modem.b00…b25`
(20 segment files; the modem partition split image), `mba.mdt`+`mba.b00`,
`wcnss.mdt`+`wcnss.b00…b09` (8 segment files), `adsp.mdt`+`adsp.b00…b12`
(13 files), and the trustzone set (`cmnlib`, `isdbtmm`, `keymaste`, `mc_v2`,
`playread`, `tqs`, `widevine` — each `.b00…bNN`+`.mdt`). md5 census of all
81 + the 3 wifi files: `scratch /tmp/astro_w/analysis/fp2_md5_census.txt`
(87 lines).

Route: git clone of the tag kept failing (`fetch-pack: unexpected
disconnect` × 3), the **codeload tarball** route succeeded and is the one
pmaports itself uses — recorded as the reproducible route.

### 1.2 The venus set (6 files, TheMuppets)

`FP2/proprietary/vendor/firmware/venus.{mdt,b00…b04}` were fetched from
`TheMuppets/proprietary_vendor_fairphone` @ `lineage-18.1` via the
authenticated git-blob API (6/6 sizes match the tree listing).

### 1.3 Route log (RULE 0, all probes 2026-11-18)

1. `gh api search/repositories?q=org:Fairphone+FP2` → 0 hits; `q=user:Fairphone`
   → `android_device_fairphone_FP5`, `fairphone-moments`,
   `fairphone-switch-button-settings` only. **No FP2 vendor/firmware repo in
   the Fairphone org** (the task-context hint `github.com/fairphone/WW-FP2?`
   resolves to nothing public — recorded as a negative route).
2. TheMuppets `proprietary_vendor_fairphone` FP2 tree enumerated on 5
   branches (cm-14.1 … lineage-18.1): 353-366 files each, firmware = venus +
   a330 + cpp only. Negative: no wcnss/modem payloads in any LineageOS FP2
   vendor branch.
3. pmaports is the bridge: `device-fairphone-fp2` APKBUILD depends on
   `firmware-fairphone-fp2-{wcnss,adsp,modem}` → `firmware-fairphone-fp2`
   APKBUILD → FairBlobs tarball + LineageOS wifi files (this is how pmOS
   mainline FP2 gets its blobs; the wiki itself is Anubis-gated, the GitLab
   API is the route, as in the queue file §2).
4. postmarketOS wiki (`wiki.postmarketos.org`) not retried this session
   (queue file already recorded the Anubis gate); pmaports GitLab used
   directly.

## 2. The split-image (MDT) family — structure verified on 4 FP2 images

`mdt_probe.py` (clean-room from `mdt_loader.c`) parses `modem`, `wcnss`,
`adsp`, `venus`, `mba`. Exit 0 (no error-class diagnostics) on all; every
phdr with nonzero `p_filesz` has a sibling `.bNN` file whose size equals the
declared size exactly (loader-fragment arithmetic holds byte-perfectly).

### 2.1 New structural fact: `.mdt` == `.b00` ‖ `.b01`

Verified byte-for-byte on FP2 `modem` (1820 = 916+904), FP2 `wcnss`
(732 = 372+360) and hammerhead `modem` (8156 = 884+7272, §hammerhead doc):

- `.b00` = the ELF32 header (52 B) + the program-header table
  (`e_phentsize` = 32 = `sizeof(elf32_phdr)`, `e_phnum` phdrs) — exactly the
  extent of phdr[0], whose `p_flags` type-bits are 7 (0x07000000);
- `.b01` = the hash/metadata segment (phdr[1], PT_NULL with
  `QCOM_MDT_TYPE_HASH` type-bits 0x02000000, `p_memsz` = 4096);
- the `.mdt` file is the concatenation of the two. The kernel's
  `qcom_mdt_read_metadata` consumes precisely these bytes for the
  TrustZone authentication handshake; the modern
  "split iff ehdr+hash==file" rule (`mdt_loader.c`) resolves to
  `ehdr+phdr0.filesz` vs the mdt — the FP2-era images store BOTH the
  phdr-table extent AND the hash segment as separate `bNN` files
  (phdr[0].filesz == 52+32·phnum here), a cleaner invariant than the
  modern check assumes.

### 2.2 modem.mdt — the MPSS 8974 image, per-byte-range map

machine = 164 (EM_QDSP6), entry 0x08000000, **not relocatable**, memory
range 0x08000000–0x0d100000. 27 phdrs: 2 metadata + 25 PT_LOAD. Build ID
string inside `modem.b13/b14` (factual metadata): 
`QC_IMAGE_VERSION_STRING=MPSS.DI.4.0.1-00190` /
`MPSS.DI.4.0.1-00190-M8974AAAAANAZM-1.101722.1.104161.1`
(CRM build stamp 2016-02-09).

| file | flags | filesz | memsz | paddr | class |
|---|---|---|---|---|---|
| b00 | 0x07000000 | 916 | 0 | — | header+phdr table (metadata) |
| b01 | 0x02200000 | 904 | 4096 | 0x0d100000 | hash segment (signature/metadata) |
| b02 | 5 | 4,052 | 4,052 | 0x08000000 | RX |
| b03 | 7 | 81,920 | 81,920 | 0x08010000 | RXW |
| b06 | 7 | 176,224 | 176,224 | 0x08024000 | RXW |
| b08 | 7 | 48,688 | 124,392 | 0x08054000 | RXW (+BSS tail) |
| b09 | 7 | 46,568 | 46,568 | 0x08078000 | RXW |
| b11 | 7 | 99,508 | 99,508 | 0x08088000 | RXW |
| b12 | 5 | 115,764 | 115,764 | 0x080a8000 | RX |
| b13 | 5 | 1,699,496 | 1,699,496 | 0x080d0000 | RX |
| b14 | 5 | 19,333,136 | 19,333,136 | 0x0826f000 | RX — the main modem code segment |
| b15 | 6 | 663,520 | 663,520 | 0x09500000 | RW |
| b16 | 6 | 139,264 | 139,264 | 0x095a4000 | RW |
| b17 | 6 | 5,376 | 5,376 | 0x095c8000 | RW — **5,376 zero bytes** (see §2.5) |
| b18 | 4 | 8,757,872 | 8,757,872 | 0x09600000 | R — the second big code segment |
| b19 | 6 | 2,990,128 | 2,990,128 | 0x09e5c000 | RW |
| b20 | 6 | 0 | 1,459,752 | 0x0a137000 | pure BSS (no file) |
| b21 | 6 | 0 | 34,163,456 | 0x0a29c000 | pure BSS (no file) — 32.6 MB heap |
| b22 | 6 | 75,584 | 75,584 | 0x0c331000 | RW |
| b23 | 4 | 425,078 | 425,078 | 0x0c344000 | R |
| b24 | 4 | 7,249,212 | 7,249,212 | 0x0c3ac000 | R |
| b25 | 6 | 1,052,652 | 1,052,652 | 0x0ca96000 | RW |
| b26 | 6 | 0 | 5,672,960 | 0x0cb97000 | pure BSS |

phdr indexes 4,5,7,10 are zero-everything placeholders (paddr 0, all sizes
0, flags 0) — the vendor image generator emits them rather than compacting
the table. On-disk payload total 42,965,862 B == Σ p_filesz (probe-verified);
BSS adds 41,374,148 B at load time. `mba.mdt`: 1 phdr, PT_LOAD,
0x0d100000–0x0d148310, right after the modem's memory range (the Modem Boot
Authenticator the 8974 boot chain runs before MPSS).

### 2.3 wcnss.mdt — the PRIMA (WCN3680) image

machine = 40 (EM_ARM — the Pronto's Riva/ARM side, vs the modem's QDSP6),
entry 0x0d201a70, **relocatable** (QCOM_MDT_RELOCATABLE bit set on the
loadable segments), range 0x0d200000–0x0d7af9e0, 10 phdrs, 8 segment files:

| file | flags | filesz | memsz | paddr |
|---|---|---|---|---|
| b02 | 0x88000007 | 14,180 | 14,504 | 0x0d200000 |
| b03 | 0x08000006 | 0 | 32,768 | 0x0d204000 (pure BSS) |
| b04 | 0x08000006 | 61,440 | 61,440 | 0x0d20c000 |
| b05 | 0x08000006 | 0 | 57,344 | 0x0d21b000 (pure BSS) |
| b06 | 0x88000007 | **2,823,520** | 4,923,744 | 0x0d229000 — the main prima WLAN/BT/FM firmware |
| b07 | 0x08000006 | 60 | 368 | 0x0d6e0000 |
| b08 | 0x08000006 | 786,432 | 786,432 | 0x0d6e1000 |
| b09 | 0x08000007 | 43,272 | 59,872 | 0x0d7a1000 |

b06's strings identify the payload as the prima image:
`dpd_fxdpnt_SW_PRIMA.c`, and the WCNSS-CTRL NV runtime protocol:
`WCNSSCTRL_ProcessNVDownloadReq` / `SendNVDownloadReply` /
`SendCalDataDownloadReply` — i.e. the firmware itself implements the SMD
service through which the host pushes `WCNSS_qcom_wlan_nv.bin` and cal data
at runtime. Free-reimplementation note: a free WCNSS stack must speak that
NV/CalData exchange, not merely load the NV file to disk.

### 2.4 adsp.mdt / venus.mdt

- adsp: machine 164 (QDSP6), 14 phdrs, 13 segment files on disk, relocatable,
  0x0dc00000–0x0f000000, Σ filesz 9,292,835 B (+10.7 MB BSS).
- venus: machine 164, 5 phdrs, 5 files, relocatable, 0x0f500000–0x0f9ff020,
  Σ filesz 995,852 B (+4.2 MB BSS).

### 2.5 Cross-device segment census: FP2 modem vs hammerhead modem

Both are MPSS 8974 images (§hammerhead doc): FP2 `MPSS.DI.4.0.1-00190`
(2016-02) vs hammerhead `MPSS.DI.2.0.C5-00024` (2014-09). Per-index phdr
comparison: 12/26 identical paddr, 8/26 identical filesz — same firmware
architecture, different builds. **Byte-identical segments: exactly one** —
`modem.b17` (5,376 B, md5 `c4ca1e4b64dadd773d546a6e920e56ec`) which is
**100% zero bytes** (all-zero RW segment, shipped as a file in both
builds; loaded at different addresses). I.e. aside from the mandated
zero-fill segment, the two 8974 modem builds share nothing at the byte
level — each device fleet needs its own build's bytes, while the container
format (§2.1) and loader protocol are the free-specification part.

## 3. The WCNSS NVRAM (`WCNSS_qcom_wlan_nv.bin`) — NV2 raw struct

`prima_nv_probe.py` classifies the FP2 file (29,816 B, from the LineageOS
FP2 device tree, pmaports-sha512-verified) as the **NV2 raw packed-struct**
format (`vos_nvitem.c` decision tree: bytes [4,8) ≠ 0xCAFEBABE ⇒ raw image,
size must equal 4 + packed `sHalNvV2`):

| byte range | field | value |
|---|---|---|
| [0,4) | nvValidityBitmap | 0xFFFFFFFF (every field valid) |
| [4,6) | productId | 0 |
| [6] | productBands | 1 = 11A/B/G |
| [7] | wlanNvRevId | 2 = WCN36xx class (0=WCN1312, 1=WCN1314, 2=WCN3660/3680) |
| [8,10) | chains | 1 TX / 1 RX |
| [10,16) etc. | macAddr1..4 | 4 distinct 6-byte values (sha1-12 fingerprints `772274…`, `91f04f…`, `bdc765…`, `ec9df5…` — not reproduced) |
| [34,74) | mfgSN[40] | all zero (no serial in this file) |
| [74] | couplerType | 48 (0x30) — **out of the 0/1 INTERNAL/EXTERNAL domain** [OPEN] |
| [75] | nvVersion | 2 = NV_VERSION_LPDC_FW_CONFIG — matches the WCN_PRONTO driver's `WLAN_NV_VERSION` expectation |
| [76,29816) | sNvTables | 29,740 B RF-calibration/regulatory tables (opaque here) |

The **NV3 template-stream format** (magic 0xCAFEBABE, then
[u16-len][stream] chains of table/enum/data streams per
`wlan_nv_parser.c`) is implemented and tested in the same probe but is NOT
what FP2 ships — FP2 is NV2. Prior art (RULE 0): `WCNSS_Binary_Maker`
(codeberg.org/LogicalErzor/WCNSS_Binary_Maker) is an existing full
parser/builder for this format family (55 pmOS device configs) — the lab
does not rebuild it; the delta here is the per-device census above, the
NV2/NV3 disambiguation written from kernel sources only, and a
cross-checkable probe.

The prima firmware container is **not QCA-TLV**: the WCN36xx-era BT/WLAN
patch/NVM TLV fleet (`crbtfw*/crnv*`) belongs to WCN399x+ chips (Mission 1
fleet-analysis.md); the 8974-era WCNSS firmware is a PIL split-ELF image
and its NV is the NV2 struct above — `qca_tlv.py` does not apply to either
container. Honest classification; no parser extension was needed.

## 4. What the FP2 blob set means for a free reimplementation

Fully specified by public sources + this census (writable today with zero
proprietary bytes):

- **Container/loader**: the PIL split-image format (ELF32 header + bNN
  segments + hash metadata segment), the loadable-segment rules, the
  relocatable-base arithmetic (already documented for FP6 in
  `qualcomm-fp6/docs/interface-mdtloader-vs-readelf.md`; the 8974-era
  images here are the non-8996 predecessors and follow the same rules —
  probe-verified). A free loader is a solved problem; what remains is
  synthesizing firmware content, not parsing it.
- **NV handling**: the NV2/NV3 container formats (probe + tests in this
  directory) and the NV validity-bitmap semantics; per-device fields
  (MACs, serial) are provisioned values, RF tables are calibration data.
- **Host protocols**: WCNSS-CTRL NV/CalData download (SMD service, names
  pinned from the firmware's own strings), the WCN36xx mainline driver's
  expectations (kernel.org wcn36xx docs, Linaro LVC21 talk), the modem
  userspace via pmOS `msm-modem` (QMI/RIL stack).

Opaque content (needs synthesis or further RE — every one now pinned to an
exact file/range):

- `wcnss.b06` (2.82 MB) — the prima WLAN/BT/FM code. A free replacement
  would mean a from-scratch Pronto firmware OR running the WCN36xx chips in
  ROM mode where supported; [OPEN].
- `modem.b14/b18/b24/b13/b19` (~38.6 MB combined) — the MPSS 8974 modem
  code. Same class of problem as every Qualcomm modem; the lab's modem-RE
  methodology (md1rom-taskmap for MTK; the FP6 modem docs) transfers
  structurally (ELF phdr map is above).
- Hash segment (`b01`, 904 B) + TrustZone-signed boot chain — the
  signature/synthesis question, same as the QCA-TLV 256-byte tail [OPEN]
  (fleet-analysis.md §3.3).
- `couplerType=48` semantics [OPEN] (§3).

## 5. Existing effort (RULE 0) + status corrections this session

- pmOS: `device-fairphone-fp2` (testing) + `firmware-fairphone-fp2` — the
  provenance source for everything above; mainline kernel
  `linux-postmarketos-qcom-msm8974` with wcn36xx + lk2nd.
- FSF/Replicant status: the queue file's "Replicant 6.0 supported" for FP2
  could not be re-confirmed from primary sources this session — the current
  Replicant wiki Devices index (redmine.replicant.us, fetched 2026-11-18)
  contains **no FP2 page** ( GalaxyNexus/GalaxyS*/Tab2/… only), and
  `ryf.fsf.org`'s product index contains **no Fairphone entry** (5-page
  probe, routes logged). Secondary sources repeatedly claim FP2+Replicant
  was RYF-certified; the primary page is [OPEN]. What is primary-verified:
  pmOS testing support, UBports official (queue file S4), LineageOS device
  tree, Fairphone's own opensource kernel releases.
- Combo-chip pin: FP2 = WCN3680 (WCNSS PRIMA) for WLAN **and** BT/FM —
  confirmed by the wcnss image itself (single Pronto image, prima strings)
  and pmOS's wcnss firmware package. No separate BT firmware file exists
  for FP2 — unlike hammerhead (see that doc), which is Broadcom.
- The task-context phrase "Replicant's documentation of the XMM modem" for
  FP2 is a misattribution: FP2's modem is Qualcomm MPSS 8974 (documented
  here); the XMM/Samsung-IPC lineage belongs to the Exynos devices (see
  `implementations/historic/m0/analysis.md`).

## 6. Files created (this directory)

- `fleet-analysis.md` (this file)
- `mdt_probe.py` — clean-room split-image parser/verifier (fixture-tested)
- `prima_nv_probe.py` — clean-room NV2/NV3 NVRAM probe (fixture-tested)
- `fixtures/make_fixture.py` + generated synthetic fixtures (no real bytes)
- `test_parsers.py` — 28 tests, all passing
- `fp2-blob-census.csv` — per-file md5 census (facts only)

Scratch (regeneratable): `/tmp/astro_w/payloads/{fp2,fp2_wifi}/`,
`/tmp/astro_w/analysis/fp2_*.json`, `/tmp/astro_w/web/fp2_*` (APKBUILDs,
tree listings). Payload bytes are NOT committed per program rules.
