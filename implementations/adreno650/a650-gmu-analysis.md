# a650_gmu.bin + a650_sqe.fw — the Adreno 650 GMU/SQE firmware, parsed

Fleet-level RE of the a650-generation GPU firmware carried by the laptop
half (8 devices, single md5 per file). Both files are parsed per the
**mainline-documented structures** (`drivers/gpu/drm/msm/adreno/a6xx_gmu.c`,
`adreno_gpu.c`, `a6xx_gpu.c`), md5-verified against the upstream database,
and compared one generation back (a619). No payload bytes committed —
payload copies live in `/tmp/astro_v/payload/`.

## 0. RULE 0 prior-art search (2026-11-18)

1. GitHub code search `q=a650_gmu.bin` — 2,896 hits, all text files
   (vendor .mk lists, BUILDING docs, device trees). **No parse of the GMU
   or SQE binary format exists publicly** — the only public "analysis" of
   these files is the mainline driver source that *consumes* them.
2. kernel.org linux-firmware `qcom/` listing: **`a650_gmu.bin` and
   `a650_sqe.fw` ARE shipped by linux-firmware** (unlike the BT cr/h
   fleets — no F-74 absence here). Their md5s vs the device copies are the
   first result below.
3. Web search for GMU firmware structure analyses — none found beyond the
   driver source and phone-mainlining discussion.

## 1. Provenance and md5 verification

| file | bytes | DB md5 (8 laptop-half devices) | fetched md5 | status | source |
|---|---|---|---|---|---|
| a650_gmu.bin | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` | same — from **two independent sources** | **MATCH** | linux-firmware `qcom/a650_gmu.bin` (git.kernel.org plain) AND TheMuppets/proprietary_vendor_sony @ lineage-19.1 `sm8250-common/proprietary/vendor/firmware/a650_gmu.bin` (Sony pdx206/pdx215 device copy) |
| a650_sqe.fw (device build) | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` | same | **MATCH** | TheMuppets/proprietary_vendor_sony (device copy only) |
| a650_sqe.fw (linux-firmware build) | 31,964 | — | `dc02e77a04b97b985281d36ab159c130` | **NOT database-identical** — a different, newer build (see §4) | linux-firmware `qcom/a650_sqe.fw` |
| a619_gmu.bin (FP4 device copy, delta comparison) | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` (7 laptop-half devices) | same | **MATCH** | TheMuppets/proprietary_vendor_fairphone @ lineage-19.1 `FP4/proprietary/vendor/firmware/a619_gmu.bin` |

Laptop-half a650 carriers: Xperia_1_II (pdx215), Xperia_5_II (pdx206),
Galaxy_Tab_S7_LTE/Wifi (gts7l), Galaxy_Tab_A7_LTE/Wifi (gta4l),
Galaxy_S20_FE (r8q), OnePlus_9R (lemonades) — 8 devices, one md5 per file
(whole-DB fleet: 14 devices). linux-firmware has **no** a619 files.

## 2. a650_gmu.bin — block-chain format (parsed per a6xx_gmu.c)

`a6xx_gmu.c` (`a6xx_gmu_fw_load`, non-legacy path) walks the file as a
chain of `struct block_header {u32 addr; u32 size; u32 type; u32 value;
u32 data[];}` (16-byte header) via `NEXT_BLK`, skipping `size==0`, copying
`data` into ITCM (0x0+16K), DTCM (0x10004000+16K for a650 family), and the
icache/dummy GMU-memory BOs. The real file (41,548 B = 0xa24c) walks
**clean to EOF**: 16 blocks, no overruns.

### 2.1 The two block classes

- **9 manifest blocks** (size 0, type 1 — one type 7): the kernel skips
  them, but their `(addr, value)` pairs **tile the loader windows
  exactly**, matching the BOs `a6xx_gmu_init` allocates for the a650
  family:

| manifest block | addr | value (= size) | mainline counterpart |
|---|---|---|---|
| m0–m2 | 0x0, 0x200, 0x400 | 0x200, 0x200, 0x3c00 | ITCM 0x0..0x4000 (tiled) |
| m3 | 0x4000 | 0x8000 | icache base (icache BO = SZ_16M−SZ_16K @ 0x04000) |
| m4, m5 | 0x10004000, 0x10007fdc | 0x3fe0, 0x24 | DTCM 0x10004000..0x10008000 (tiled) |
| m6, m7 | 0x144000, 0x157000 | 0x13000, 0x9000 | icache sub-windows |
| m8 | 0x60000000 (type 7) | 0x1000 | dummy page BO (SZ_4K @ 0x60000000) |

  Manifest semantics [OPEN] (chip-consumed — the kernel never reads
  `value`), but the correspondence with the kernel's own BO map is exact.

- **7 payload blocks** (every one tagged `type = value = 0xEFBEADDE` —
  the on-disk bytes DE AD BE EF, a "DEADBEEF" pattern; this is the
  payload tag of the format, not a terminal sentinel):

| block | addr | size | region (per mainline BO map) | entropy |
|---|---|---|---|---|
| p0 | 0x00000000 | 192 | ITCM | 5.06 |
| p1 | 0x00000200 | 320 | ITCM | 1.74 |
| p2 | 0x00000400 | 14,092 | ITCM | 6.86 |
| p3 | 0x00004000 | 21,968 | icache | 6.78 |
| p4 | 0x00157000 | 920 | icache | 2.50 |
| p5 | 0x10004000 | 3,776 | DTCM | 0.52 |
| p6 | 0x10007fdc | 24 | DTCM (end) | 2.11 |

Totals: ITCM 14,604 B (≤16K), icache 22,888 B (≤16M−16K), DTCM 3,800 B
(≤16K). Whole-file entropy 6.43 bits/byte; 19 % zero bytes; top code words
after 0x0 are Thumb idioms (`0x4770` = `bx lr` ×33, `0x41f0e92d` =
`push {r2-r8,lr}` ×32, `0x4010e8bd` = pop epilogue ×25, `0xbd10` ×38) —
Cortex-M3 (GMU) Thumb code, same idiom family the F-75 BT patch bodies
showed.

## 3. a650_sqe.fw — 4-byte-stripped upload + version dword

Mainline facts that pin the format:

- `adreno_gpu.c::adreno_fw_create_bo` allocates `fw->size − 4` and copies
  from `&fw->data[4]` — **the SQE file's first dword is a stripped 4-byte
  prefix** (0x00000000 in both builds examined); the file body from
  offset 4 is the microcode uploaded verbatim to `REG_A6XX_CP_SQE_INSTR_BASE`.
- `a6xx_gpu.c::a6xx_ucode_check_version` reads the **driver-visible
  version dword** (= file dword 1): a650 requires `(v & 0xfff) >= 0x095`.

| build | bytes | file dword 0 | version dword | `(v & 0xfff)` | passes a650 check |
|---|---|---|---|---|---|
| device fleet (DB md5) | 31,632 | 0x00000000 | `0x16dd093` | 0x093 | **NO** (0.93 < 0.95) |
| linux-firmware | 31,964 | 0x00000000 | `0x16dd112` | 0x112 | YES (1.12) |

**Finding: the device fleet's a650_sqe.fw is BELOW mainline's minimum
security-version floor** — a phone-tablet carrier build (v0.93), while
linux-firmware carries a newer build (v1.12) that passes. The two builds
share only 18.0 % same-offset bytes (1/1,977 identical 16-byte blocks;
4,492 differing runs, 93 % under 16 bytes = instruction-word-level
edits) — wholly different microcode, same format. Consequence for free
systems: mainline msm will refuse the phone-carried SQE
("a650 SQE ucode is too old") and needs a ≥0.95 build; the byte-exact
device copy is recorded here for fleet completeness, not as a
mainline-usable artifact.

The leading stripped dword is 0x00000000 in both builds — semantic [OPEN]
(format tag?). Entropy 5.53/5.54; zero fraction 26 %.

## 4. a619_gmu.bin — one generation back, a different format

The a619 device copy (FP4; 7 laptop-half devices carry it: FP4,
Nord_CE2, Realme_10_Pro, Realme_9_Pro, Xperia_1_II, Xperia_5_II,
Xperia_5_III — all one md5, 32,768 B):

- **Not a block chain**: the first words (0x00043f80, 0x00000009) do not
  decode as a sane block header; a chain walk overruns the file at
  offset 25.
- **Exactly 0x8000 bytes** — the mainline legacy loader's hard cap
  ("GMU firmware is bigger than the available region" check rejects
  `size > 0x8000`); the legacy path bulk-writes the WHOLE file into the
  GMU ICM region.
- Content: ARM Thumb code from byte 0, 57.8 % zero bytes, a 14,748-byte
  zero run, all-zero tail padding — a raw ITCM image (code + bss-like
  padding), entropy 3.87.

Mainline ties `a619_gmu.bin` to sm4350/sm6375-class targets (chip ids
0x06010900/0x06010901, revn 619, ADRENO_6XX_GEN1); whether the FP4-class
DT binding selects the legacy GMU path at runtime [OPEN] — but the FILE
FORMAT evidence (0x8000 raw image) is unambiguous, and linux-firmware
ships no a619 files at all.

**The a650-vs-a619 delta (one generation):**
| | a619 (GEN1) | a650 (GEN3-class, a650 family) |
|---|---|---|
| GMU format | raw 0x8000 ITCM image | 16-block chain: 9-block manifest + 7 DEADBEEF-tagged payload blocks |
| regions | single ICM bulk region | ITCM + icache (0x4000, 16M) + DTCM (0x10004000) + dummy (0x60000000) |
| loader path | legacy (gmu->legacy) | non-legacy block loader |
| linux-firmware | absent | ships both files |
| size | 32,768 | 41,548 (gmu) |

The SQE side (a619 uses `a630_sqe.fw` per mainline) was out of the DB
scope for these devices (no a619_sqe rows in the laptop half).

## 5. Free-reimplementation consequences

- The GMU block-chain format is FULLY specified by mainline + this file:
  a free loader/driver stack already exists (msm); the remaining opaque
  content is the microcode itself (ITCM/icache/DTCM images, Thumb code,
  [OPEN] semantics — needs synthesis or unpatched-ROM operation, not
  byte-copying).
- The manifest blocks are a bonus: they document the chip's own view of
  the memory windows, matching the kernel's hardcoded BO bases — useful
  cross-check for any reimplementation.
- SQE: the 4-byte-strip + version-dword contract is pinned; the device
  fleet build fails the mainline version floor, which any free stack must
  source (or synthesize) a ≥0.95 microcode for.

## 6. Route log (2026-11-18)

1. `gh api search/code q=a650_gmu.bin` (2,896 hits — no parse exists).
2. kernel.org linux-firmware `qcom/` listing + plain fetch of
   a650_gmu.bin/a650_sqe.fw (a650_gmu md5-matched the device fleet;
   a650_sqe did NOT — second build fetched from the Sony device tree).
3. TheMuppets/proprietary_vendor_sony @ lineage-19.1
   `sm8250-common/proprietary/vendor/firmware/` (pdx206/pdx215 copies —
   both md5-matched).
4. TheMuppets/proprietary_vendor_fairphone @ lineage-19.1 FP4
   `a619_gmu.bin` (md5-matched the 7-device a619 fleet).
5. linux-firmware qcom/ has no a619 files (negative finding).
6. Mainline sources fetched from kernel.org plain (torvalds linux.git):
   a6xx_gmu.c, a6xx_gpu.c, adreno_gpu.c, a6xx_catalog.c, msm_gpu.c.
