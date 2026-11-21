# Qualcomm SM8250 Snapdragon 865 — GPU core identification and firmware

Issue #2035. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number is from a command run 2026-11-20/21 against
`upstream-contribution/blob-database/coverage-matrix.csv`, against
`data/fleet/devices-001-222.csv`, against `torvalds/linux` master, and against
the SM8250 `a650_*` payloads extracted at
`data-fetch/second-device/instantnoodle/tree-vendor/firmware/`.

Companion documents, cited and **not** re-derived here:

| document | owns |
|---|---|
| `research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md` | the next-generation sibling; same house format |
| `research/laptop/qualcomm-adreno-a650-fleet.md` | `a650_gmu.bin` block-container decode (16 records, EOF `0xa24c`), the SQE `>= 0.95` gate, the live/carrier occupancy split |
| `research/laptop/qualcomm-adreno-gmu-content.md` | the a619 GMU content RE (ARMv7-M / Cortex-M3, ITCM+DTCM `0x4000` each) |
| `research/soc/per-soc-method-plans.md:288` | the SM8250 per-SoC plan row |

## 1. The GPU is an Adreno 650 — proven three independent ways

**Verdict: Qualcomm Adreno 650, a6xx generation 3 (`ADRENO_6XX_GEN3`), chip ID
`0x06050002`.** Not Mali, not PowerVR.

| # | evidence | class |
|---|---|---|
| 1 | Mainline DT: `sm8250.dtsi:2935` `compatible = "qcom,adreno-650.2"` | [F] |
| 2 | Mainline DT: `sm8250.dtsi:3007` `compatible = "qcom,adreno-gmu-650.2"` | [F] |
| 3 | Mainline driver: `a6xx_catalog.c:1052` `ADRENO_CHIP_IDS(0x06050002)`, `.revn = 650`, `.family = ADRENO_6XX_GEN3` | [F] |
| 4 | Matrix: the SM8250 `gpu` rows carry `a650_gmu.bin` / `a650_sqe.fw` / `a650_zap.mdt` | [F] |

The driver's own entry, `a6xx_catalog.c` lines 1052-1064 (the entry continues to
`:1077` with the `.a6xx` and `.speedbins` sub-structs):

```c
.chip_ids = ADRENO_CHIP_IDS(0x06050002),
.family = ADRENO_6XX_GEN3,
.revn = 650,
.fw = {
    [ADRENO_FW_SQE] = "a650_sqe.fw",
    [ADRENO_FW_GMU] = "a650_gmu.bin",
},
.gmem = SZ_1M + SZ_128K,
.inactive_period = DRM_MSM_INACTIVE_PERIOD,
.quirks = ADRENO_QUIRK_HAS_CACHED_COHERENT |
          ADRENO_QUIRK_HAS_HW_APRIV,
.funcs = &a6xx_gpu_funcs,
.zapfw = "a650_zap.mdt",
```

So the **chip ID is `0x06050002`** and the GMEM aperture is
**`SZ_1M + SZ_128K` = 1,179,648 B (`0x120000`)** [F]. Four hard interface
numbers follow from this one entry:

| quantity | value | why it matters |
|---|---|---|
| chip ID | `0x06050002` | the only key `adreno_info()` matches on |
| GMEM | 1,179,648 B (`0x120000`) | aperture a reimplementation must map |
| firmware family | `a650_*` | three files; all three change name at a660 |
| zap target | `a650_zap.mdt` | but see §5 — DT overrides this |

`find_chipid()` (`adreno_device.c:142-172`) computes the chip ID **from the
compatible string**, not from a fuse: `qcom,adreno-650.2` parses as core
`650/100 = 6`, major `(650%100)/10 = 5`, minor `650%10 = 0`, patch `2`, giving
`(6<<24)|(5<<16)|(0<<8)|2` = `0x06050002` [F]. The `.2` suffix is the patch
level and is part of the ID — a device tree that says `qcom,adreno-650.1`
would not match this catalog entry.

### 1.1 A generation boundary that is easy to get wrong

The enum comment in `adreno_gpu.h:47-50` is the authority, and it does not
follow the file prefix:

```c
ADRENO_6XX_GEN1,  /* a630 family */
ADRENO_6XX_GEN2,  /* a640 family */
ADRENO_6XX_GEN3,  /* a650 family */
ADRENO_6XX_GEN4,  /* a660 family */
```

`a650` is **GEN3**, one below the a660's GEN4. This is not cosmetic: the
`.gmem` value changes with it (`0x120000` for a650 vs `0x180000` for a660), and
`adreno_is_a650_family()` (`adreno_gpu.h:531-538`) deliberately spans
`GEN3 || GEN4`, so a reimplementation that keys behaviour on the *filename*
prefix would be right by luck for the a650 entry but wrong for the family test.

**Correction to the sibling document.** `research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md:33-35`
states the a660 GMEM "is 1.5x the a650's `SZ_512K`". Both halves are wrong: the
a650's `.gmem` is `SZ_1M + SZ_128K` (`a6xx_catalog.c:1059`), not `SZ_512K`, and
`SZ_1M + SZ_512K` is **3.0x** `SZ_512K`, not 1.5x. The correct ratio a660/a650
is 1,572,864 / 1,179,648 = **1.3333x** [F]. The a660 figures in that document
are otherwise correct; only the comparison clause is wrong. Recorded here
because it is the kind of one-line numeric error downstream work copies
uncritically.

## 2. What the matrix actually says — and the 652-row mislabel

The committed `coverage-matrix.csv` slice for
`soc == "Qualcomm SM8250 Snapdragon 865"`, re-derived this session:

```
raw slice        1,900 rows   6 devices   2,648,371,404 B
OnePlus_9RT        652 rows                  734,658,038 B
corrected        1,248 rows   5 devices   1,913,713,366 B
```

Family split **after** removing the `OnePlus_9RT` block:

| family | rows |
|---|---:|
| other | 810 |
| tz | 227 |
| wifi | 65 |
| adsp | 44 |
| boot | 32 |
| cdsp | 24 |
| modem | 21 |
| **gpu** | **19** |
| bt | 6 |

Per device:

| device | rows | bytes |
|---|---:|---:|
| OnePlus_8_Pro | 506 | 591,327,658 |
| OnePlus_8 | 504 | 590,857,486 |
| OnePlus_8T | 106 | 252,290,143 |
| OnePlus_9R | 106 | 252,290,143 |
| Xperia_5_II | 26 | 226,947,936 |

### 2.1 The `OnePlus_9RT` / `martini` block is SM8350, not SM8250

This is the finding. The 652 `martini` rows are labelled
`Qualcomm SM8250 Snapdragon 865`, but the device is a **Snapdragon 888 /
SM8350** handset, and its GPU rows are `a660_*`, one generation up:

| carrier | claim | source | date |
|---|---|---|---|
| OnePlus | "Qualcomm(R) Snapdragon(TM) 888 5G", "GPU: Adreno 660" | oneplus.in/9rt/specs | 2026-11-21 |
| GSMArena | "Qualcomm SM8350 Snapdragon 888 5G (5 nm)", "GPU Adreno 660" | gsmarena.com | 2026-11-21 |
| PixelExperience wiki | "SoC Qualcomm SM8350 Snapdragon 888 5G", "GPU Adreno 660" | wiki.pixelexperience.org | 2026-11-21 |
| devicespecifications | "Snapdragon 888 (SM8350)", "Qualcomm Adreno 660" | devicespecifications.com | 2026-11-21 |

The `a660_*` filenames alone would be weak evidence (a vendor partition is a
superset — §3). The discriminating evidence is **independent of the labels**,
computed from the matrix itself: of `martini`'s **591** distinct `md5_db`
values, **474 (80.2%)** also appear under `OnePlus_9_Pro`, an SM8350 device,
versus **5** under every other SM8250 device combined [F]. Firmware sets from
the same OnePlus build family share their bulk; a `martini` that were truly
SM8250 would cluster with `instantnoodle`/`kebab`/`lemonades`, and it does not.

Three consequences:

1. **The SM8250 device count is 5, not 6** in the matrix. The second fleet
   dataset loses one more — it never had `Xperia_5_II`, so its corrected count
   is 4 populated devices out of 7 names (the `Edge_20_Pro` / `Edge_S` 870 pair
   carries zero files).
2. **The SM8250 row count is 1,248, not 1,900** (65.7% of the raw slice).
3. **Byte volume drops by 27.7%** (2,648,371,404 → 1,913,713,366 B;
   the martini block is 27.74% of the raw slice).

This is a database attribution correction, not a payload finding: the md5s are
whatever they are. The action is to relabel the row block, not to delete it —
under SM8350 the 652 rows are legitimate. They are **not** already counted
there: the matrix's SM8350 slice is 1,344 rows / 3 devices (`Moto_G200` 651,
`OnePlus_9_Pro` 650, `Xperia_5_III` 43), and `OnePlus_9RT` appears nowhere under
an SM8350 label [F]. Relabelling would take SM8350 to 1,996 rows / 4 devices —
which is the number a rebuild should produce, and the reason the current 1,344
understates that SoC.

Note also that `OnePlus_9` (SM8350 in fact) carries a **blank** `soc` in the
matrix for all 651 of its rows, so the SM8350 undercount has a second cause
beyond martini [F].

### 2.2 Two SM8250-AC 870 devices carry no files

`Edge_20_Pro` and `Edge_S` (Motorola) appear under
`Qualcomm SM8250-AC Snapdragon 870` in `data/fleet/devices-001-222.csv` with
`family = none`, `file = ""`, `bytes = 0`, `public_status = listed-not-populated`
[F]. They contribute device names and nothing else. Note the SoC label: the 870
is `SM8250-AC`, a distinct string in the device inventory and a **zero-row**
match in `coverage-matrix.csv` (which files both under the bare
`Qualcomm SM8250 Snapdragon 865` string) [F]. The a650 catalog entry is shared:
`SM8250-AC` is an a650 part, and no separate Adreno variant exists for it.

### 2.3 The two datasets disagree, and both are internally consistent

| dataset | SM8250 rows | devices | bytes |
|---|---:|---:|---:|
| `coverage-matrix.csv` (raw label) | 1,900 | 6 | 2,648,371,404 |
| `coverage-matrix.csv` (corrected) | 1,248 | 5 | 1,913,713,366 |
| `data/fleet/devices-001-222.csv` (non-empty, corrected) | 1,222 | 4 | 1,686,765,430 |
| `per-soc-method-plans.md:288` (plan) | 1,900 | 8 | 2.65 GB |

The plan row's "1,900 rows" matches the **raw** slice exactly, and its "2.65 GB"
matches 2,648,371,404 B, so the plan was derived from the same matrix — it
inherits the martini mislabel. Its "8 devices" does not match any count here:
6 in the matrix, 5 corrected, 7 in the fleet CSV. That row is a plan, not a
result, and its device count is unverified [N].

## 3. The corrected GPU rows are 7 filenames — only 3 can bind to an a650

Raw slice: **23** `gpu` rows / 11 distinct filenames across 6 devices. Corrected
slice: **19** rows / 7 distinct filenames across 5 devices. (The other fleet
dataset, `data/fleet/devices-001-222.csv`, holds 16 raw and 12 corrected `gpu`
rows for the same SoC — a different device universe, same mislabel; see §2.3.)

| device | filename | bytes | md5 |
|---|---|---:|---|
| OnePlus_8 | `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` |
| OnePlus_8 | `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` |
| OnePlus_8 | `a650_zap.mdt` | 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` |
| OnePlus_8T | `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` |
| OnePlus_8T | `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` |
| OnePlus_8T | `a650_zap.mdt` | 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` |
| OnePlus_8_Pro | `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` |
| OnePlus_8_Pro | `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` |
| OnePlus_8_Pro | `a650_zap.mdt` | 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` |
| OnePlus_9R | `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` |
| OnePlus_9R | `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` |
| OnePlus_9R | `a650_zap.mdt` | 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` |
| Xperia_5_II | `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` |
| Xperia_5_II | `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` |
| Xperia_5_II | `a650_zap.mdt` | **7,116** | `b56d71ce556b5b1a65dbed5f14a1360a` |
| Xperia_5_II | `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` |
| Xperia_5_II | `a630_sqe.fw` | 32,264 | `df35307c61eaaf826f62bada432d47ee` |
| Xperia_5_II | `a615_zap.mdt` | 6,708 | `9767ca057d012413dbfeace049a8eea2` |
| Xperia_5_II | `a620_zap.mdt` | 6,860 | `97098b9c43d6a1b1e57238fda83c5279` |

**Live set: 3 distinct filenames / 15 rows** (`a650_gmu.bin`, `a650_sqe.fw`,
`a650_zap.mdt`, carried by all five devices). **15 of 19 rows are live; the
other 4 are co-resident leftovers on `Xperia_5_II`** — `a619_gmu.bin` (Adreno
619, the two `revn = 619` entries at `a6xx_catalog.c:871-877` and `:896-902`),
`a630_sqe.fw` and `a615_zap.mdt` (the `revn = 615` entry at `:790-801` pairs
exactly these two), and `a620_zap.mdt` (the `0x06020100` entry at `:947-958`,
whose own `.zapfw` is `a620_zap.mbn`, not `.mdt`) [F].

A census reading the `gpu` family column as "GPU firmware this SoC runs"
therefore overstates by **19/15 = 1.27x** in rows and **7/3 = 2.33x** in
distinct filenames. For comparison, the raw slice (before the martini removal)
gives 23/15 = 1.53x, and the sibling document's SM8350 slice gives
**11/6 = 1.83x** in rows and **7/3 = 2.33x** in filenames
(`research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md:145-148`) [F]. SM8250 is
therefore milder than SM8350 on both measures — 1.27x vs 1.83x in rows — and the
filename ratio is identical at 2.33x. That equality is the more honest
comparison: in both SoCs, roughly two thirds of the GPU filenames present cannot
bind to the SoC's own Adreno part.

### 3.1 `a650_zap.mdt` has four builds and two sizes across the fleet

`a650_zap.mdt` is not a single blob. Across the whole matrix, 11 rows name it,
in **four** distinct md5s and **two** sizes [F]:

| size | md5 | carriers | SoC (as labelled) |
|---:|---|---|---|
| 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` | OnePlus_8, OnePlus_8T, OnePlus_8_Pro, OnePlus_9R | SM8250 |
| 6,860 | `1d776a3cfede2c8c2aec952f7d0f176f` | Pixel_4A_5G, Pixel_5, Pixel_5A | SM7250 |
| 6,860 | `91c1429b0981cb8804e5709dae5ea8a1` | Galaxy_Tab_A7_LTE, Galaxy_Tab_A7_Wifi | blank |
| 7,116 | `b56d71ce556b5b1a65dbed5f14a1360a` | Xperia_1_II, Xperia_5_II | blank / SM8250 |

Same filename, same GPU, four different builds — three at 6,860 B and one 256 B
larger. The 6,860-group is the `a650_zap.elf` layout below; the 7,116 B build is
a different segment table (256 B = two extra 128 B entries' worth, not
established) [I]. A zero-tolerance parser must accept all four, and the sizes
alone do not discriminate: three builds share one size.

`a660_zap.mdt` shows the same pattern one generation up: **21 rows, 11 distinct
md5s**, split 8 builds at 6,708 B and 3 at 6,860 B [F]. `OnePlus_9RT` carries
6,708 B `9f61a84f…`, while `OnePlus_9_Pro` and `Xperia_5_III` carry 6,708 B
`2474a662…` and `203d73b4…` — same size as martini's build, three different
digests, same GPU. So neither size nor md5 identifies the GPU: the 8 builds at
6,708 B span SM4350, SM4375, SM6375, SM7325-AE, SM8350, QCM6490 and — via
martini's own mislabel — SM8250, while the 3 at 6,860 B span SM7250,
SM7325-AE and SM8350-AC [F]. So the same filename at the same size occurs under
**seven distinct SoCs** (eight distinct label strings — `SM6375` appears as both
`Snapdragon 695` and `Snapdragon 695 5G`).

### 3.2 `sequence_manifest.bin` is not GPU firmware

Both `martini` (mislabeled, §2.1) and the SM8350 slice carry
`sequence_manifest.bin`, 5,704 B, md5 `252630742d895255d66b5be984bdabda` —
byte-identical. It lives at `vendor/gpu/kbc/`, is a KBC manifest, and has no
`adreno` loader [N]. It was never part of the true SM8250 slice; the corrected
count of 19 contains none of it.

## 4. The `a650_*` payloads — what is on disk, measured

Extracted from `data-fetch/second-device/instantnoodle/tree-vendor/firmware/`
(this session, `hashlib` + `struct` from bytes):

| file | bytes | md5 | sha256 (first 16 hex) |
|---|---:|---|---|
| `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` | `df79fa8482fcc758` |
| `a650_sqe.fw` | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` | `b4c27420fd6a5c6b` |
| `a650_zap.mdt` | 6,860 | `7c8bf961fcfca0e4f5503bc4b6364a1e` | `e2def9eb448466bd` |
| `a650_zap.elf` | 13,964 | `c9b059d3283f78641dd58f312504be6a` | `2b0e2832c95b0fa9` |
| `a650_zap.b00` | 148 | `00f1b291a2b30c98f05c25506e3f4761` | `ec9b9d5a67456384` |
| `a650_zap.b01` | 6,712 | `2fec76c23e945bd2ed399b2027d6b2ac` | `22393cf4be103e93` |
| `a650_zap.b02` | 1,676 | `35273e4135147a269076144a3051b498` | `a415e5452fa8f597` |

All three matrix md5s reproduce exactly [F]. No payload bytes are committed;
only digests, sizes and offsets.

The GMU and SQE files are **not** analysed here beyond their digests: the
block-container walk to exact EOF `0xa24c` after 16 records
(`0xa24c` = 41,548 = the file size exactly), and the SQE `>= 0.95` version gate
that this 31,632 B build **fails** (file dword 1 = `0x016dd093`, `v & 0xfff` =
`0x093` = 0.93), are already established in
`research/laptop/qualcomm-adreno-a650-fleet.md` §2 and §5. Re-measured and
confirmed, not re-derived [F].

### 4.1 `.mdt` = ELF header + hash segment, with the `.elf` offsets left unrewritten

`a650_zap.mdt` (6,860 B) is **byte-exactly** `a650_zap.b00` (148 B) followed by
`a650_zap.b01` (6,712 B):

```
m[:148]  == b00      True
m[148:]  == b01      True
148 + 6712 = 6860    True   (== len(m), no padding at all)
```

`b00` is the ELF header plus its 3×32 B program-header table (52 + 96 = 148 B).
`b01` is **not** a loadable segment — it is the hash/metadata segment, identified
by its `p_flags` type bits (§ below). So the `.mdt` carries the header and the
**hash**, and the one loadable segment (1,676 B of code) is absent — that is
`b02`, fetched separately at load time [F].

The program headers in the `.mdt` still describe the **`.elf`** layout, and are
not rewritten for the repacked file. That is the whole mechanism:

| # | p_type | p_offset | p_filesz | `p_offset+p_filesz` | > `fw->size` (6,860)? |
|---|---|---:|---:|---:|:--:|
| 0 | 0 | `0x0` | 148 | `0x94` (148) | no |
| 1 | 0 | `0x1000` | 6,712 | `0x2a38` (10,808) | **yes** |
| 2 | 1 | `0x3000` | 1,676 | `0x368c` (13,964) | **yes** |

Both segments 1 and 2 claim offsets past EOF, so
`qcom_mdt_bins_are_split()` (`mdt_loader.c:296-326`, test at `:317`:
`seg_start > fw->size || seg_end > fw->size`) returns true on **segment 1** —
the hash segment — not on the code segment [F]. So the `.mdt` is not a
truncated `.elf`; it is a **deliberately offset-inconsistent** file whose header
points into a layout that no longer exists. The offsets are stale metadata from
the pre-split `.elf`.

The kernel states this outright in `qcom_mdt_read_metadata()`
(`mdt_loader.c:154-156`): *"In the case of split firmware the hash is found
directly following the ELF header, rather than at p_offset described by the
second program header."* And the branch it takes here is the first one, at
`:208`, `ehdr_size + hash_size == fw->size` (148 + 6,712 = 6,860 = exact file
size) — the "split, hash packed following the ELF header" case [F].
Reconstructed exactly as the kernel does, the metadata blob is
`m[:148] + m[148:148+6712]`, which is the entire file.

The `.elf` is the union with the padding put back:

```
0x0    .. 0x94     hdr     148 B   (b00)
0x94   .. 0x1000   pad   3,948 B
0x1000 .. 0x2a38   hash  6,712 B   (b01)
0x2a38 .. 0x3000   pad   1,480 B
0x3000 .. 0x368c   code  1,676 B   (b02)
                   total 13,964 B
```

`148 + 6,712 + 1,676 = 8,536` B of content plus `3,948 + 1,480 = 5,428` B of
zero padding = 13,964 B [F]. So `.mdt` = `.elf` minus the code segment minus
both pad regions, and `.b00/.b01/.b02` = `.elf` split at its own `p_filesz`
boundaries with the padding dropped.

This generalises in the extracted tree, which is the useful part:

| file | bytes | segments | `b00+b01` is the whole file? | hash segment | code segments |
|---|---:|---:|---|---:|---:|
| `a650_zap.mdt` | 6,860 | 3 | **yes** (148 + 6,712) | 6,712 | 1 (1,676 B) |
| `ipa_uc.mdt` | 6,860 | 3 | **yes** (148 + 6,712) | 6,712 | 1 (37,412 B) |
| `ipa_fws.mdt` | 7,020 | 5 | **yes** (212 + 6,808) | 6,808 | 3 (19,200 + 128 + 560 B) |

`ipa_uc.mdt` is the same size and the same `148 + 6,712` split as `a650_zap.mdt`
with a completely unrelated payload (hash-segment `p_paddr` `0x10000` vs
`0x6000`; code 37,412 B at `p_paddr` `0x0` vs 1,676 B at `0x5000`) [F]. That is
strong evidence the `148 / 6,712 / 0x1000` shape is a **fixed toolchain
layout**: a `.mdt` from this Qualcomm tooling starts with a 52 B ELF header plus
a 3×32 B phdr table, and carries a 6,712 B hash segment, whatever the payload.
`ipa_fws.mdt` corroborates with a 5-segment variant whose `b00` is
`212 = 52 + 5×32` and whose hash is 6,808 B at `p_paddr` `0x9000` [F].

The type encoding is what identifies the hash segment.
`mdt_phdr_loadable()` (`mdt_loader.c:55-66`) requires `p_type == PT_LOAD` **and**
rejects `(p_flags & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH`, with
`TYPE_MASK = 7<<24` and `TYPE_HASH = 2<<24`
(`include/linux/soc/qcom/mdt_loader.h:6-7`) [F]. Decoding all three:

| # | `p_flags` | `>>24 & 7` | bit 27 | R/W/X | loadable? |
|---|---|---:|---:|---|---|
| 0 | `0x07000000` | 7 | clear | none | no (`p_type` 0) |
| 1 | `0x02200000` | **2 = HASH** | clear | none | no (hash type) |
| 2 | `0x08000007` | 0 | **SET** | 7 = RWX | **yes** — the only one |

Segment 2 is the sole loadable segment, and **bit 27
(`QCOM_MDT_RELOCATABLE`) is set on it** — so `relocate = true` and
`mem_reloc = min_addr` = `0x5000`, not `mem_phys`
(`mdt_loader.c:369-371`, `:377-387`) [F]. The code segment therefore loads at
offset `p_paddr - min_addr = 0x5000 - 0x5000 = 0`, i.e. at the **base** of the
reserved region, and `qcom_pas_mem_setup()` is invoked with
`max_addr - min_addr` = `0x6000 - 0x5000` = 4,096 B to establish the
relocation (`mdt_loader.c:283-284`) [F].

That the a650 zap is relocatable is itself a usable interface fact: the secure
world is told the image may be placed at an arbitrary base, which is why
`p_paddr` need not be honoured literally. `ipa_uc.mdt`'s code segment carries
the same `0x08000007`, and `ipa_fws.mdt`'s three code segments all do [F].

### 4.2 `qcom_mdt_get_size()` yields 4,096 B against an 8,192 B reservation

`qcom_mdt_get_size()` (`mdt_loader.c:110-140`) computes
`ALIGN(max(p_paddr + p_memsz), SZ_4K) - min(p_paddr)` over loadable segments.
For this file only segment 2 is loadable (`0x5000`, 1,676 B):

```
min = 0x5000 ; max = ALIGN(0x5000 + 0x68c, 0x1000) = 0x6000
size = 0x1000 = 4,096 B
```

The DT reserves **`0x2000` (8,192 B)** — `sm8250.dtsi:822-825`,
`gpu_mem: memory@8681a000 { reg = <0x0 0x8681a000 0x0 0x2000>; }` [F]. So the
reservation is **2.0x** what the loader says it needs. The check
`if (mem_size > resource_size(&r))` (`adreno_gpu.c:117`) passes either way;
the 2x headroom is unexplained here and is recorded as an honest negative, not
as padding for a second image [N].

`e_entry` is `0x5000` — the `p_vaddr` of the *executable* segment — and the
single loadable segment has `p_flags` `0x08000007`: bits 0-2 = `7` (R|W|X) and
bit 27 set (relocatable). That is the shader's authority contract: one
writable, executable, relocatable segment of 1,676 B nominally at virtual
`0x5000` [F]. Note the RWX combination — the secure world receives one segment
that is simultaneously writable and executable, which is the opposite of the
W^X discipline a general-purpose loader would enforce.

### 4.3 The zap shader is **Hexagon** code, not ARM

`e_machine` is **164**, and `include/uapi/linux/elf-em.h:43` defines
`EM_HEXAGON 164 /* QUALCOMM Hexagon */` [F]. `e_flags` is `0x3`, which matches
`EF_HEXAGON_MACH_V4` in LLVM's `ELF.h:468` [F].

This is the counter-intuitive result: the Adreno GPU's secure-world shader is
not an ARM or a6xx program. It is Hexagon firmware, run by the secure processor
under PAS ID 1 — consistent with the shader being authenticated and then
executed by a Hexagon core in the trusted execution environment rather than by
the GPU's own SQE/GMU [I].

Cross-check inside the same vendor tree: `ipa_fws.elf`/`.mdt`, `ipa_uc.elf`/
`.mdt` are **also** `e_machine = 164, e_flags = 0x3`, while
`CAMERA_ICP.elf` is `e_machine = 40 (EM_ARM), e_flags = 0x5000000` [F]. So the
"co-processor firmware in this vendor partition is Hexagon V4-flagged" pattern
holds across four unrelated subsystems, and the one ARM ELF present is a
different class of component entirely. Nothing about the a650 zap is special
except that it is the GPU's.

## 5. The mainline load path does **not** request `a650_zap.mdt`

`a6xx_catalog.c:1064` sets `.zapfw = "a650_zap.mdt"`, which invites the
conclusion that a mainline SM8250 board loads that file. It does not.

`zap_shader_load_mdt()` (`adreno_gpu.c:31-174`) reads, in order:

1. `of_property_read_string_index(np, "firmware-name", 0, &signed_fwname)` on
   the `zap-shader` child node (`:82`);
2. if set — `request_firmware_direct(&fw, fwname, …)` with **that** path,
   bypassing `adreno_request_fw()` and its `qcom/` prefix search entirely
   (`adreno_gpu.c:82-88`);
3. only if unset does it fall back to the catalog's `.zapfw` string via
   `adreno_request_fw()`.

Every SM8250 board DT in mainline sets the property:

| board DT | line | value |
|---|---:|---|
| `sm8250-mtp.dts` | 490 | `qcom/sm8250/a650_zap.mbn` |
| `sm8250-hdk.dts` | 377 | `qcom/sm8250/a650_zap.mbn` |
| `qrb5165-rb5.dts` | 565 | `qcom/sm8250/a650_zap.mbn` |

So on any mainline SM8250 board the requested name is
**`qcom/sm8250/a650_zap.mbn`**, and the catalog's `a650_zap.mdt` is dead
metadata [F]. This matters twice over:

- **The `.mdt` name in the catalog is legacy compatibility only.** The comment at
  `adreno_gpu.c:92-102` says exactly this: the gpulist fallback exists "for
  backwards compatibility for older targets", and "for new targets, we require
  the firmware-name property".
- **The `.mbn` and the `.mdt` are the same ELF, differently signed.** See §5.1.

The path resolution is a three-step probe with a sticky result:
`qcom/<name>` direct → `<name>` legacy direct → `qcom/<name>` via usermode
helper (`adreno_gpu.c:536-614`). `fwloc` latches on first success, so a system
that has the file only in the legacy location keeps loading from there [F].

### 5.1 linux-firmware's `.mbn` and the vendor `.elf`: identical layout, signature-only difference

Downloaded `qcom/sm8250/a650_zap.mbn` from linux-firmware (`main`, 13,964 B,
md5 `22d41ed3f78026773951988f04d34205`) and compared to the vendor
`a650_zap.elf` (13,964 B, md5 `c9b059d3283f78641dd58f312504be6a`) [F]:

| region | range | identical? |
|---|---|:--:|
| ELF header + phdr table | `[0x0, 0x94)` = 148 B | **yes** |
| pad to first segment | `[0x94, 0x1000)` | **yes** |
| hash/metadata segment | `[0x1000, 0x2a38)` | **no** |
| pad to code segment | `[0x2a38, 0x3000)` | **yes** |
| code segment | `[0x3000, 0x368c)` | **yes** |

**3,432 differing bytes (24.58% of the file), every one inside the hash
segment** — diff range `0x1040`–`0x1f36` — **and the entire 1,676 B code
segment is byte-identical.** Same `e_entry` `0x5000`, same three program
headers, same `p_paddr`s [F].

This is the cleanest available explanation of why the split-`.mdt` apparatus
exists at all: the two builds differ **only in the signature block**. The code
is the same shader. A device-signed `.mbn` and a release-signed `.mbn` cannot
share a hash segment, so the `.mdt`/`.bNN` decomposition lets the hash travel
separately from the payload — which is precisely what
`qcom_mdt_read_metadata()` does with the 148 + 6,712 pair [I].

`WHENCE:7267-7272` records `qcom/a650_gmu.bin v2.1.8`, `qcom/a650_sqe.fw
v1.12`, and `qcom/sm8250/a650_zap.mbn v0.10` [F]. Note the path: the zap is
shipped **per-SoC** (`sm8250/`) while the GMU and SQE are shipped **per-GPU**
(`a650_*`), consistent with the zap being device-signed and the other two not.

## 6. Mainline support status

| item | status | evidence |
|---|---|---|
| SM8250 SoC DT | present, `sm8250.dtsi` (178,419 B, 7,067 lines) | [F] |
| Adreno 650 GPU node | present, `compatible = "qcom,adreno-650.2"` at `:2935` | [F] |
| Adreno 650 GMU node | present, `compatible = "qcom,adreno-gmu-650.2"` at `:3007` | [F] |
| Adreno SMMU node | present, `qcom,sm8250-smmu-500` at `:3061` | [F] |
| Driver binding | `ADRENO_CHIP_IDS(0x06050002)` at `a6xx_catalog.c:1052` | [F] |
| GMU register windows | 4: `gmu`, `rscc`, `gmu_pdc`, `gmu_pdc_seq` (`:3009-3013`) | [F] |
| GMU interrupt names | `hfi` (SPI 304), `gmu` (SPI 305) (`:3014-3016`) | [F] |
| GPU clock domains | 7 OPPs, 305 MHz – 670 MHz (`:2959-3003`) + 1 GMU OPP at 200 MHz | [F] |
| Firmware in linux-firmware | `qcom/a650_gmu.bin`, `qcom/a650_sqe.fw`, `qcom/sm8250/a650_zap.mbn` | [F] |
| GPU support since | Linux 5.9 (linux-msm mainline-status) | [F] |
| Board DTs setting zap name | mtp, hdk, qrb5165-rb5 | [F] |
| postmarketOS device port | not verified this session | [N] |

The four GMU windows are worth recording because they are a bring-up
requirement the sibling doc did not enumerate: `gmu` at `0x03d6a000`
(`0x30000`), `rscc` at `0x3de0000`, `gmu_pdc` at `0xb290000`, `gmu_pdc_seq` at
`0xb490000` — all `0x10000` except the first [F]. Three of the four are outside
the `0x3d…` GPU block entirely, in the `0xb2…`/`0xb4…` register region.

## 7. Honest negatives

1. **No per-SoC SM8250 GPU note existed.** At Gate 0, `research/soc/` held
   MSM8998, SM4375, SM7325, SM8350, and `docs/REPO-STATE-MAP.md:18` read
   "GPU core ID | 27 | NEW | none" [F]. Both are addressed by this commit: the
   note is this file, and the map row now reads PARTIAL with the five per-SoC
   docs named. The remaining 22 SoC labels in the matrix still have no per-SoC
   GPU doc [N].
2. **The Adreno 650 identification is not new.** It is published in
   `sm8250.dtsi` and already exploited in-repo at
   `research/laptop/qualcomm-adreno-a650-fleet.md` §4. This document adds
   the per-SoC consolidation and the corrections, not the identification [F].
3. **`a650_gmu.bin` content beyond its digest is not analysed here.** The
   16-record block decode is cited from the fleet document; it was not re-walked
   this session [N].
4. **The SQE failure is cited, not re-proven.** File dword 1 = `0x016dd093`,
   `v & 0xfff` = `0x093` = 0.93, below the `0x095` floor — consistent with the
   fleet document's finding, but the four-branch gate in `a6xx_gpu.c` was not
   re-read this session [I].
5. **The 7,116 B `a650_zap.mdt` build was not opened.** Two Xperia devices carry
   it; whether the extra 256 B is a fourth segment, a longer hash, or padding is
   not determined [N].
6. **The 2.0x `gpu_mem` headroom is unexplained.** `qcom_mdt_get_size()` says
   4,096 B, the DT reserves 8,192 B. No reason established [N].
7. **`sequence_manifest.bin` (KBC) format is not analysed**, and it is not part
   of the corrected SM8250 slice at all [N].
8. **`SM8250-AC` (Snapdragon 870) is not covered by bytes.** Both 870 devices in
   the fleet CSV are `listed-not-populated`; the a650 catalog entry is shared
   with SM8250 but no 870 payload was examined [N].
9. **`per-soc-method-plans.md:288`'s "8 devices" is unverified** and matches no
   count in either dataset [N].
10. **The a650/a660 GMEM ratio error in the sibling document is reported, not
    fixed here.** Correcting another issue's committed deliverable is out of
    this issue's scope; §1.1 records the correct numbers [F].
11. **The martini mislabel is not corrected in the source CSV.** `coverage-matrix.csv`
    is a generated artifact; this document records the correction and the
    evidence, and a rebuild is a separate task [N].
12. **No disassembly was performed.** `EM_HEXAGON` is established from the ELF
    header only; no instruction was decoded [N].

## Reproduce

```bash
python3 -I -c "
import csv
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
s=[r for r in rows if r['soc'].strip()=='Qualcomm SM8250 Snapdragon 865']
print('raw',len(s),len({r['device'] for r in s}),sum(int(r['size_bytes']) for r in s))
c=[r for r in s if r['device']!='OnePlus_9RT']
print('corrected',len(c),len({r['device'] for r in c}),sum(int(r['size_bytes']) for r in c))
from collections import Counter; print(Counter(r['blob_family'] for r in c).most_common())"
```

```bash
curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/sm8250.dtsi \
  | sed -n '822,825p;2934,2936p;3006,3008p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c \
  | sed -n '1052,1064p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/adreno_gpu.h \
  | sed -n '47,50p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/soc/qcom/mdt_loader.c \
  | sed -n '55,66p;110,140p;296,326p'
```

```bash
python3 -I -c "
import struct,hashlib
d='data-fetch/second-device/instantnoodle/tree-vendor/firmware/'
m=open(d+'a650_zap.mdt','rb').read()
b00=open(d+'a650_zap.b00','rb').read(); b01=open(d+'a650_zap.b01','rb').read()
e=struct.unpack_from('<16sHHIIIIIHHHHHH',m,0)
print('e_machine',e[2],'e_flags',hex(e[7]),'phnum',e[10])
print('mdt==b00+b01', m==b00+b01)
mn=0x5000; mx=(0x5000+1676+0xfff)&~0xfff
print('qcom_mdt_get_size', hex(mx-mn))"
```

All fetches 2026-11-20/21, `torvalds/linux` master.

## Sources

| claim | source | access |
|---|---|---|
| 1,900 / 6 / 2,648,371,404 raw; 1,248 / 5 / 1,913,713,366 corrected; family split; all md5/size | `upstream-contribution/blob-database/coverage-matrix.csv` | 2026-11-21 |
| 1,876 rows / 7 devices; 1,222 non-empty corrected rows | `data/fleet/devices-001-222.csv` | 2026-11-21 |
| martini 474/591 = 80.2% md5 overlap with OnePlus_9_Pro | computed from `coverage-matrix.csv` | 2026-11-21 |
| Adreno 650 / chip ID `0x06050002` / GMEM / zapfw / GEN3 | `raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c:1052-1064` | 2026-11-21 |
| GEN1-GEN4 enum comments | `.../adreno_gpu.h:47-50` | 2026-11-21 |
| `find_chipid()` compatible-string parse | `.../adreno_device.c:142-172` | 2026-11-21 |
| `qcom,adreno-650.2`, `qcom,adreno-gmu-650.2`, `gpu_mem` `0x2000` | `.../arch/arm64/boot/dts/qcom/sm8250.dtsi:822-825,2935,3007` | 2026-11-21 |
| zap `firmware-name` override on mtp/hdk/rb5 | `sm8250-mtp.dts:490`, `sm8250-hdk.dts:377`, `qrb5165-rb5.dts:565` | 2026-11-21 |
| `zap_shader_load_mdt()` property-first path | `.../adreno_gpu.c:31-174` | 2026-11-21 |
| `adreno_request_fw()` three-step probe | `.../adreno_gpu.c:536-614` | 2026-11-21 |
| split test, loadable test, get_size | `.../drivers/soc/qcom/mdt_loader.c:55-66,110-140,296-326` | 2026-11-21 |
| `QCOM_MDT_TYPE_MASK` / `RELOCATABLE` | `.../include/linux/soc/qcom/mdt_loader.h:6-8` | 2026-11-21 |
| `EM_HEXAGON 164` | `.../include/uapi/linux/elf-em.h:43` | 2026-11-21 |
| `EF_HEXAGON_MACH_V4 = 0x3` | `llvm/llvm-project` `llvm/include/llvm/BinaryFormat/ELF.h:468` | 2026-11-21 |
| `a650_gmu.bin` / `a650_sqe.fw` / `sm8250/a650_zap.mbn` versions | `linux-firmware` `WHENCE:7267-7272` (git.kernel.org, `h=main`) | 2026-11-21 |
| all payload digests, sizes, ELF fields, region diffs | `data-fetch/second-device/instantnoodle/tree-vendor/firmware/a650_*` measured this session | 2026-11-21 |
| a650 GMU block decode / SQE gate / occupancy | `research/laptop/qualcomm-adreno-a650-fleet.md` §2, §4, §5 | 2026-11-21 |
| GMU ARMv7-M / Cortex-M3 / TCM split | `research/laptop/qualcomm-adreno-gmu-content.md` | 2026-11-21 |
| GPU support since Linux 5.9 | `linux-msm.github.io/mainline-status/soc/sm8250` | 2026-11-21 |
| OnePlus 9RT is SM8350 / Adreno 660 | oneplus.in/9rt/specs; gsmarena.com; wiki.pixelexperience.org; devicespecifications.com | 2026-11-21 |
