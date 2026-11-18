# hpbtfw20.tlv — the h-generation (Hastings-class) QCA BT rampatch, parsed

Fleet-level RE of the `hpbtfw20.tlv` rampatch carried by the laptop-half
devices (matrix rows for FP5 + the Xiaomi SM8450-class block + OnePlus_9RT).
This is the **h-prefix sibling of the F-75 cr/ap fleet analysis**
(`implementations/qca-bt/fleet-analysis.md`): same parser
(`implementations/qca-bt/qca_tlv.py`, unmodified), same per-byte-range
method, same [OPEN] discipline. No payload bytes are committed — payload
copies live only in `/tmp/astro_v/payload/` (regeneratable via the route
log below); everything below is derived structural fact.

## 0. RULE 0 prior-art search (all queries 2026-11-18)

1. GitHub code search `q=hpbtfw20` (authenticated `gh api search/code`) —
   114 hits, **all text files** (device extract lists, vendor .mk files,
   firmware manifests, mainlining notes). No byte-level parse anywhere.
2. GitHub code search `q=hiccup hpbtfw20` — 0 hits.
3. **Prior art found and cited (structure-free on our targets):**
   `corpunum/unumS22linux docs/research/BT_QCA6490_FIRMWARE_GATE_2026-09-21.md`
   — a host-only controller-identity audit for a QCA6490 device. It
   establishes, and we build on: (a) the hp* family is the **"Hastings"**
   generation (QTI HAL strings `HASTINGS_VER_2_0`, controller build string
   `BTFW.HSP.2.1-…`, SoCID `0x400C0210`); (b) the QTI HAL state machine
   (`PatchDLManager::SocInit` → Get-App-Version → SetBaudRateReq →
   `DownloadTlvFile` → `UpdateHastingNvm`); (c) the HAL's XML override files
   (`bt_nvm_loading.xml`) target `WCN6856_2.1`. It contains **no TLV/tag
   parse of hpbtfw20.tlv or hpnv20.bin** — the byte-level work below is the
   delta.
4. `dianqk/nixos-android-devices docs/marble/firmware.md` — mainlining notes
   for Poco F5 (marble, a laptop-half fleet member): documents that stock
   hpbtfw/hpnv21 files differ from linux-firmware's and that btqca selects
   the `hpnv21g` NVM on GlobalFoundries parts. No file parse.
5. linux-firmware `qca/` directory listing (fetched 2026-11-18): contains
   `hpbtfw10.tlv`, `hpbtfw21.tlv`, `hpnv10*`, `hpnv21*` (+`hpnv21g.*`),
   `htbtfw20.tlv`, `htnv20.bin`, `hmtbtfw20.tlv`, `msbtfw11.*` — but **no
   `hpbtfw20.tlv` and no `hpnv20.bin`** (the F-74-style absence, now
   pinned for the h-20 generation: these ship only inside device vendor
   trees).
6. Web search `"hpbtfw20.tlv" analysis` — no structural analysis exists.

## 1. Chip identity: what the mainline driver says about "h"

`drivers/bluetooth/btqca.c` (torvalds master, fetched 2026-11-18,
`/tmp/astro_v/btqca.c`):

- `QCA_QCA2066` → `qca/hpbtfw%02x.tlv` (direct), NVM via
  `qca_get_nvm_name_by_board(..., "hpnv", ...)`; the board-id naming emits
  `hpnv20.bin` (no board id) or `hpnv20.<prefix><bid>` per board, with a
  `g` variant for GlobalFoundries-fab chips (`QCA_HSP_GF_SOC_ID` — "HSP"
  = Hastings).
- `QCA_WCN6855` → `wcnhpbtfw*.tllv` with a documented historical fallback
  to `hpbtfw*.tlv` / `hpnv*.bin` ("Due to historical reasons, WCN685x chip
  has been using firmware without the 'wcn' prefix").
- `QCA_WCN6750` → `msbtfw*.mbn` (ELF) then `msbtfw*.tlv` then `msnv*.bin`
  — NOT hpbtfw.

So the lab's earlier prefix decode (`hpbtfw* → QCA2066`,
blob-matrix/per-soc-method-plans.md) is confirmed for the *mainline loader*.
The workorder brief's "WCN6750-generation" framing is right at the family
level: QCA2066 and WCN6750's BT core (QCA6490) are the same Hastings
silicon family (SoCID 0x400C02xx per the unumS22linux capture), one
generation after the cr/ap (WCN399x/WCN3988) files, with WCN6855 sharing
the same fallback names. Devices ship hpbtfw20/hpnv20 alongside msbtfw
(e.g. FP5 carries both) because the Hastings BT core can enumerate under
either name depending on the SoC-id/board flow.

## 2. Provenance and md5 verification

Upstream md5s from `upstream-contribution/blob-database/coverage-matrix.csv`.
The laptop half carries **two builds**; a third build (Samsung) was fetched
for cross-checks and is labeled NOT-DB-IDENTICAL below.

| build | bytes | DB md5 | fetched md5 | status | source (public, individually fetchable) |
|---|---|---|---|---|---|
| common (9 devices: cupid/mayfly/unicorn/thor/diting/zeus/marble/mondrian/martini) | 201,560 | `922473448ce287c8bb5e849998b9ffb7` | see §2.1 | see §2.1 | Xiaomi `bluetooth` partition image via XiaomiFirmwareUpdater `firmware_xiaomi_cupid` release zip (bluetooth.img) |
| FP5 build | 184,740 | `9430539dc8e602c5634896f218a591dd` | — | [OPEN: no public source found yet] | Fairphone FP5 stock vendor (`/vendor/bluetooth/image/`); LineageOS does not extract it; GitHub dumps of FP5 ship no bluetooth partition |
| Samsung r0s build (NOT a DB device; cross-check only) | 163,760 | — (no DB row carries md5 `d79f9944b6b5b666ce47e50c1fb5a4b4`) | `d79f9944b6b5b666ce47e50c1fb5a4b4` | **NOT database-identical** (third build; still structurally the same generation and parsed below) | `TheMuppets/proprietary_vendor_samsung_r0s` @ lineage-24.0, `proprietary/vendor/firmware/hpbtfw20.tlv` (raw) |
| hpbtfw21.tlv (r0s, adjacent-ROM generation, no DB rows in laptop half) | 195,916 | — | `52c94069635d08f59f5b69441cba2436` | n/a (context) | same r0s repo |

### 2.1 Common-build status [updated in session]

`bluetooth.img` was extracted from
`fw_cupid_miui_CUPID_V13.0.10.0.SLCCNXM_e5b34408f8_12.0.zip`
(XiaomiFirmwareUpdaterReleases/firmware_xiaomi_cupid @ stable-31.12.2021,
189 MB) — the `bluetooth` partition image that carries `/image/hpbtfw20.tlv`
+ `hpnv20.bin`. Verification results recorded in §4 below.

## 3. The h-generation patch format (what changed vs the F-75 cr/ap fleet)

Parsed with the unmodified lab parser (`qca_tlv.py`, exit 0 on every file of
this fleet — no error-class diagnostics) and `implementations/hbt-fleet/
fleet_diff.py` (new, fixtures-tested). Byte-range map (hpbtfw20.tlv, both
builds share the frame):

```
[0, 4)       tlv_type_hdr     type=1, length_field = file−4  (holds, all files)
[4, 28)      tlv_type_patch   24 bytes, fields below
[28, 28+data_length)          patch body (opaque ARM Thumb overlay, §3.2)
[28+data_length, file)        44-byte footer (NOT a 256-byte tail), §3.1
```

### 3.1 Header fields — h generation vs F-75 cr/ap generation

| field | hpbtfw20 (r0s build) | hpbtfw21 (r0s) | crbtfw20 (F-75) | apbtfw10 (F-75) |
|---|---|---|---|---|
| total_size | 163,724 | 195,880 | 55,920 | 55,792 |
| data_length | 163,688 | 195,844 | 55,896 | 55,768 |
| format_version | 1 | 1 | 1 | 1 |
| **signature_algorithm** | **0** | **0** | 2 | 2 |
| download_mode | 3 SKIP_EVT_VSE_CC | 3 | 3 | 3 |
| **product_id** | **19** | **19** | 10 | 10 |
| rom_build | 0x0200 | 0x0201 | 0x0200 | 0x0200 |
| **patch_version** | **0x3d71** | **0x687c** | 0x0002 | 0x0002 |
| **reserved2** | **0x0** | **0x0** | 0x8000 | 0x8000 |
| **entry** | **0x00000000** | **0x00000000** | 0x1b0e0 | 0x1b0e0 |

Generational invariants (hold on every h-build parsed):

1. `total_size = data_length + 36` (cr/ap: `data_length + 24`) and
   `file = 4 + 24 + data_length + 44` (cr/ap: `+ 256`).
2. The **256-byte signature-class tail is GONE**. The h-generation ends in
   a **44-byte footer**: an 8-byte build-varying prologue followed by 36
   bytes of hash-class content (footer entropy 5.05 bits/byte vs 7.13 for
   the cr/ap RSA-class tail; prologues observed: `04040202 05ca0404` on
   both r0s builds, `00000000 10000000` on cupid hp20, `6d750e10 20000000`
   on cupid hp21 — see §4). With `signature_algorithm = 0` this reads as:
   the h-generation drops the on-file RSA signature block and ships a
   compact checksum/MAC-class footer instead. Exact verification algorithm
   [OPEN] (the mainline kernel streams the footer to the chip and never
   inspects it).
3. `entry = 0x00000000`: the h-generation patches do not declare a RAM
   entry point (cr/ap declared 0x1b0e0/0x1b15c). Entry semantics moved
   into the body [OPEN].
4. `patch_version` becomes a per-file build id (0x3d71 / 0x687c), not the
   constant format revision (0x0002) of the cr/ap generation.
5. `product_id` 19 (cr/ap: 10) — the product_id field now separates the
   Hastings generation.
6. `rom_build 0x0200` matches crbtfw20's ROM build digit — but the two
   bodies share only **2.64 %** same-offset bytes (cr20 vs hp20): a wholly
   different code base patching a different controller's ROM. hpbtfw20 vs
   hpbtfw21 (adjacent ROM builds 0x0200/0x0201): 2.44 % — same-story
   within the h generation (cf. F-75 §3.2: cr20 vs ap10 = 43.7 % shared
   base; the h fleet does NOT share one overlay base between its own
   ROM builds).

### 3.2 Patch body [28, file−44)

- Entropy 6.94/6.98 bits/byte, 8.7 %/8.9 % zero bytes — same dense
  machine-code profile as the F-75 bodies.
- The ARM Thumb stack-veneer idiom from F-75 is present and MORE dominant:
  most-common little-endian words in hpbtfw20.r0s body are `0x4801b403`
  ×389 and `0xbd019001` ×389 (crbtfw20: ×133) — `push {r0,r1}`;
  `ldr r0,[pc,#4]` / `str r0,[sp,#4]`; `pop {r0,r1}` pairs — plus
  `0xb081b5f0` ×120 (`push {r4-r7,lr}; sub sp,#4`) and `0x46c0bdf0` ×116
  (`pop {r4-r7,pc}; nop`). **Interpretation [OPEN]** (same discipline as
  F-75): ARM Thumb machine code for the controller core with
  patch-entry veneers; statistics only, no disassembly performed.

### 3.3 The 44-byte footer [file−44, file)

| file | prologue (8 B) | sha1-12 of content[8:] |
|---|---|---|
| hpbtfw20.tlv (r0s) | `02020404 0404ca05` | `f841c03e01c8` |
| hpbtfw21.tlv (r0s) | `02020404 0404ca05` | `130f891e2046` |
| hpbtfw20.tlv (DB/cupid) | `00000000 10000000` | `c2e518fae594` |
| hpbtfw21.tlv (cupid, 91,344 B) | `6d750e10 20000000` | `e57ff8b5e420` |

The 8+36 footer structure is a NEW structural fact for this generation
(no 256-byte signature block exists in these files; the "total_size ≠ file"
notes the parser emits are exactly this footer, now quantified instead of
unexplained). The prologue is build-varying (the r0s pair shares one
because both files ship in one firmware build).

## 4. Common-build (DB md5) verification — MATCH

The cupid `bluetooth` partition image (FAT16, 1,470,464 B; parsed with a
scratch minimal FAT16 reader, `/tmp/astro_v/analysis/fat16_read.py`)
extracted 71 files under `/image/` — the exact layout the DB records under
`<vendor>/bluetooth/image`. Both common-build targets verified byte-exact:

| file | bytes | DB md5 | fetched md5 | status |
|---|---|---|---|---|
| hpbtfw20.tlv (cupid bluetooth partition) | 201,560 | `922473448ce287c8bb5e849998b9ffb7` | same | **MATCH** |
| hpnv20.bin (cupid bluetooth partition) | 6,319 | `5de36001f431a4d60c641d494a75bb60` | same | **MATCH** |

The partition also carries (context, not DB targets): `hpbtfw21.tlv`
(**91,344 B here vs 195,916 B in the r0s Samsung tree — same filename,
wholly different build**, the F-74 counterexample pattern again),
`hpbtfw20.ver` (33 B), `hpnv20.bXX` ×10 (exactly the 10 board-variant names
the DB lists for this device block) + `hpnv20g.bXX` ×9 + `hpnv20g.bin`, and
the whole `hpnv21`/`hpnv21g` family (`.301/.302` numeric board ids and
`.bXX` ones). qca_tlv.py on the DB build: exit 0; header
product_id 19, rom_build 0x0200, **patch_version 0x3ed8** (r0s build:
0x3d71 — per-build build-id confirmed), entry 0x00000000, 830 segments
(last 113 B), **44-byte footer** with prologue `0x00000000 0x00000010`.

**Footer-prologue correction (recorded):** the r0s pair shared prologue
`0x04040202 0x05ca0404`, which initially looked constant; the cupid builds
use different prologues (`00000000 00000000 10 00 00 00` for hp20,
`6d750e10 20000000` for its hp21). The generation invariant is the **44-byte
length + 36-byte hash-class content**, not the prologue (4/4 builds differ
in it; the r0s pair shared one because both files came from one Samsung
firmware build). `fleet_diff.py` documents this and reports the prologue
without asserting constancy.

## 5. What the h-generation adds (generation delta, one line each)

- product_id 19; signature_algorithm 0; reserved2 0; entry 0.
- 44-byte checksum-class footer with constant prologue, replacing the
  256-byte RSA-class tail.
- No shared overlay base between ROM builds (2.4 % cross-build equality
  vs 43.7 % in the cr/ap generation).
- Same filename, different bytes across device families: hpbtfw21.tlv is
  195,916 B (Samsung r0s) vs 91,344 B (cupid) — vendor fleet files are
  not interchangeable across the generation.
- Same TLV download protocol (243-byte segments, SKIP_EVT_VSE_CC,
  whole-file framing) — the mainline loader needs NO changes to carry
  these files (qca_tlv.py parses them error-free, unmodified).

## 6. Freed-device value

The laptop half carries hpbtfw20.tlv on **10 devices** (matrix rows 119-236
exact match): FP5 (own build) + 9 devices sharing one md5 (8 Xiaomi + 1
OnePlus_9RT). Whole-DB fleet: 13 devices / 2 md5s. With the common build
md5-verified from a public source, 9 of the 10 laptop-half devices have a
publicly fetchable, byte-identical, structurally parsed rampatch; FP5's
build remains [OPEN] on provenance (no public copy found after the honest
routes in §0/§2 — recorded).

## 7. Route log (all probes 2026-11-18)

1. `gh api search/code q=hpbtfw20` → 114 hits (text only; no binaries —
   GitHub code search does not index binary paths).
2. TheMuppets repos checked for `bluetooth/image` extracts:
   proprietary_vendor_xiaomi_mayfly (hrtf5c only), proprietary_vendor_
   oneplus_martini (odm/etc/bt/hpnv10.bin only), proprietary_vendor_
   samsung_r0s (**has** vendor/firmware/hpbtfw20.tlv + hpnv20.bin +
   hpbtfw21.tlv + hpnv21.bab + hpnv21g.bab) — fetched raw.
3. fairphone FP5 sources probed: TheMuppets/proprietary_vendor_fairphone
   (branches ≤ lineage-19.1, no FP5), proprietary_vendor_fairphone_FP5
   (lineage-21…24.0 — BT images not extracted), FairBlobs/FP5-firmware
   (pil images only), gm-stuffs + Jiovanni-dump fp5 dumps (no bluetooth
   partition), fairphone-mirror/vendor_fairphone_hiccup (overlay only,
   83 KB) — FP5 build unfetchable from these routes; recorded.
4. Stock dumps for the Xiaomi block: Jiovanni-dump/xiaomi_cupid_dump and
   Klozz/xiaomi_cupid_dump — vendor/ trees carry no bluetooth partition
   (it is a separate partition; also confirmed by DB db_paths
   `<vendor>/bluetooth/image`).
5. XiaomiFirmwareUpdaterReleases/firmware_xiaomi_cupid release
   `fw_cupid_miui_CUPID_V13.0.10.0.SLCCNXM_e5b34408f8_12.0.zip` — 189 MB
   zip downloaded with resumable curl (connection resets required ~14
   resumes; script in scratch), contains the `bluetooth` partition image.
6. kernel.org linux-firmware `qca/` listing — h-20 files absent
   (F-74-style absence pinned for hpbtfw20.tlv/hpnv20.bin).
