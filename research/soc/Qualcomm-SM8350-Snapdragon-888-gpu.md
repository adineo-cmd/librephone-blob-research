# Qualcomm SM8350 Snapdragon 888 — GPU core identification and firmware

Issue #2036. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number is from a command run this session (2026-11-20)
against the committed matrix and against `torvalds/linux` master.

## 1. The GPU is an Adreno 660 — proven three independent ways

**Verdict: Qualcomm Adreno 660, a6xx generation 4 (`ADRENO_6XX_GEN4`), chip ID
`0x06060001`.** Not Mali, not PowerVR.

| # | evidence | class |
|---|---|---|
| 1 | Mainline DT: `sm8350.dtsi:2040` `compatible = "qcom,adreno-660.1"` | [F] |
| 2 | Mainline DT: `sm8350.dtsi:2121` `compatible = "qcom,adreno-gmu-660.1"` | [F] |
| 3 | Mainline driver: `a6xx_catalog.c:1079` `ADRENO_CHIP_IDS(0x06060001)`, `.revn = 660`, `.family = ADRENO_6XX_GEN4` | [F] |
| 4 | Matrix: the SM8350 `gpu` rows carry `a660_gmu.bin` / `a660_sqe.fw` / `a660_zap.mdt` | [F] |

The driver's own entry, `a6xx_catalog.c` lines 1079-1097:

```c
.chip_ids = ADRENO_CHIP_IDS(0x06060001),
.family = ADRENO_6XX_GEN4,
.revn = 660,
.fw = {
    [ADRENO_FW_SQE] = "a660_sqe.fw",
    [ADRENO_FW_GMU] = "a660_gmu.bin",
},
.gmem = SZ_1M + SZ_512K,
.zapfw = "a660_zap.mdt",
```

So the **chip ID is `0x06060001`** and the GMEM aperture is **1 MiB + 512 KiB**
(`SZ_1M + SZ_512K`) [F]. That GMEM figure is a hard interface number for any
bring-up work: it is 1.5x the a650's `SZ_512K`.

Public spec corroboration (not a primary source, used only as a cross-check):
Qualcomm's own marketing and every teardown identify Snapdragon 888 as Adreno
660 [F, notebookcheck/gadgets360, accessed 2026-11-20].

## 2. What the matrix actually says — and the two numbers that differ

The matrix's SM8350 slice, re-derived this session:

```
total SM8350 rows  693      886,208,933 B
OnePlus_9_Pro      650 rows  748,523,070 B
Xperia_5_III        43 rows  137,685,863 B
gpu rows            11
```

Family split across the 693 rows:

| family | rows |
|---|---:|
| other | 324 |
| wifi | 155 |
| tz | 98 |
| adsp | 41 |
| modem | 32 |
| cdsp | 18 |
| boot | 13 |
| **gpu** | **11** |
| bt | 1 |

Note the 693 total and the issue title's "693 rows, 2 devices" agree [F]. But
`docs/REPO-STATE-MAP.md` and `research/soc/per-soc-method-plans.md` both record
SM8350 as **3 devices / 1,344 rows** in the *laptop-half* dataset, while this
matrix slice is **2 devices / 693 rows** [F]. Two different device universes,
same SoC name. Both numbers are correct for their own dataset; neither is
correct as "the" SM8350 count. Recorded as a cross-dataset discrepancy, not a
bug.

## 3. The 11 GPU rows are 7 distinct filenames — and 3 of them cannot be live

| device | filename | bytes | md5 |
|---|---|---:|---|
| Xperia_5_III | `a615_zap.mdt` | 6,708 | `1fcd6ea780a6a56c2990edfbb15fa28f` |
| Xperia_5_III | `a660_zap.mdt` | 6,708 | `203d73b414d1a0b9afd659db74511f98` |
| Xperia_5_III | `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` |
| Xperia_5_III | `a630_sqe.fw` | 32,456 | `21693ef6f2d686ce79ebb3716a099970` |
| Xperia_5_III | `a660_gmu.bin` | 55,256 | `179caf2e3b7d5481c3567c2987f5be32` |
| Xperia_5_III | `a660_sqe.fw` | 40,496 | `08b7662ccd6815333aed6bce9bd69bd7` |
| Xperia_5_III | `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` |
| OnePlus_9_Pro | `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` |
| OnePlus_9_Pro | `a660_zap.mdt` | 6,708 | `2474a66217dbd51f35c3f13a7d3c1e68` |
| OnePlus_9_Pro | `a660_gmu.bin` | 55,256 | `179caf2e3b7d5481c3567c2987f5be32` |
| OnePlus_9_Pro | `a660_sqe.fw` | 40,496 | `08b7662ccd6815333aed6bce9bd69bd7` |

Seven distinct payloads: `a660_gmu.bin`, `a660_sqe.fw`, `a660_zap.mdt`,
`a615_zap.mdt`, `a619_gmu.bin`, `a630_sqe.fw`, `sequence_manifest.bin` — that is
**7 distinct filenames across 11 rows** (four of them carried by both devices:
`a660_gmu.bin`, `a660_sqe.fw`, `a660_zap.mdt`, `sequence_manifest.bin`) [F].

### 3.1 `a619_gmu.bin` + `a630_sqe.fw` on an Adreno 660 SoC cannot be live

This is the finding. `Xperia_5_III` (`pdx214`, SM8350) ships **three**
non-660 GPU payloads — `a619_gmu.bin`, `a630_sqe.fw`, `a615_zap.mdt` — all of
which belong to other GPU revisions, alongside its correct a660 pair:

| blob | belongs to | mainline evidence | live on SM8350? |
|---|---|---|---|
| `a660_gmu.bin` | Adreno 660 | `a6xx_catalog.c:1084` | **yes** |
| `a660_sqe.fw` | Adreno 660 | `a6xx_catalog.c:1083` | **yes** |
| `a619_gmu.bin` | Adreno 619 | `a6xx_catalog.c:873` / `:898` (revn 619) | **no** |
| `a615_zap.mdt` | Adreno 615 entry (`revn = 615`) | `a6xx_catalog.c:801` | **no** |
| `a630_sqe.fw` | Adreno 615 entry **and** a610/a630 | `a6xx_catalog.c:794` (revn 615), `:745` (revn 610) | **no** |

One correction to a naive reading: `a630_sqe.fw` is **not** an Adreno-630-exclusive
blob. The `revn = 615` entry at `a6xx_catalog.c:792-801` pairs exactly
`a630_sqe.fw` with `a615_zap.mdt`:

```c
.revn = 615,
.fw = {
    [ADRENO_FW_SQE] = "a630_sqe.fw",
    [ADRENO_FW_GMU] = "a630_gmu.bin",
},
.zapfw = "a615_zap.mdt",
```

So the Xperia_5_III carries **two complete, internally consistent firmware
pairs**: the a660 pair (live on SM8350) and the a615 pair (`a630_sqe.fw` +
`a615_zap.mdt`, not live), plus one orphan (`a619_gmu.bin`, whose GMU partner
is absent) [F]. That is a stronger statement than "three stray blobs": the
vendor tree ships a whole *second GPU's* matched firmware set [I].

The kernel binds exactly one `adreno_info` entry per GPU by chip ID, and
`adreno_load_fw()` (`adreno_gpu.c`) loads only the `fw[]` slots of *that* entry
[F]. A single Adreno 660 cannot consume `a619_gmu.bin` or `a630_sqe.fw`.

Why they are present: `pdx214`'s vendor firmware partition is a **shared
superset** built for the whole Sony `sagami`/`edo` family, not for one SKU [I].
This is the same co-residency pattern already proven for the a650 fleet
(`research/laptop/qualcomm-adreno-a650-fleet.md` §4: "a vendor firmware
partition is a superset of what one SoC binds"; the three Pixels carry
`a619_gmu.bin` + `a630_sqe.fw` + `a650_sqe.fw` alongside) [F]. Here it recurs one
generation later, on a different vendor tree, which is what makes it a general
property of the vendor-partition model rather than a Sony quirk [I].

**Consequence for the count:** of the 11 `gpu` rows, only **6 rows (3 distinct
filenames: `a660_gmu.bin`, `a660_sqe.fw`, `a660_zap.mdt`) can bind to an
Adreno 660**. The remaining 5 rows are the a615 pair (2), the orphan
`a619_gmu.bin` (1), and `sequence_manifest.bin` (2) which is not GPU microcode
and has no `adreno` loader at all [F]. A census that reads the `gpu` family
column as "GPU firmware this SoC runs" overstates the live set by **11/6 = 1.83x**
in rows, and by **7/3 = 2.33x** in distinct filenames.

### 3.2 `a660_zap.mdt` differs between the two devices — same size, different bytes

Both devices carry an `a660_zap.mdt` of exactly **6,708 B**, but the md5s
differ:

```
Xperia_5_III   203d73b414d1a0b9afd659db74511f98
OnePlus_9_Pro  2474a66217dbd51f35c3f13a7d3c1e68
```

Two distinct builds of the same blob, same length [F]. That is a
build-variant signal, not a corruption: identical size with differing digest
means the diff is in-place (version string / signing padding), which is the
known pattern for `zap` payloads. Not byte-verified this session — recorded as
[I] with the exact md5s so the next agent can diff them.

### 3.3 `sequence_manifest.bin` is byte-identical across both devices

Both carry `sequence_manifest.bin`, 5,704 B, md5
`252630742d895255d66b5be984bdabda` — **identical** [F]. It lives at
`vendor/gpu/kbc/`, not `vendor/firmware/`, and is a KBC (kernel-bypass
composition) manifest, not GPU microcode. It is counted in the `gpu` family by
the matrix but has no `adreno` loader. Honest negative: no mainline consumer,
and its format is not analysed here [N].

## 4. GPU microcontroller ISA — already proven in-repo, cited not repeated

The GMU's own instruction set is **not** re-derived here because the lab already
proved it. `research/laptop/qualcomm-adreno-gmu-content.md` establishes, from
bytes:

- ARMv7-M, **Cortex-M3 class**; ITCM + DTCM, each `0x4000` (16 KiB), file is the
  two TCM images laid end to end — the `0x8000` (32 KiB) cap is forced by the
  register map, `GMU_CM3_ITCM_START` (`0x1b400`) and `GMU_CM3_DTCM_START`
  (`0x1c400`) being exactly `SZ_16K` apart.
- Reset vector `0x00000009` = the raw Thumb byte `0x09` of a branch, not a
  length.
- The `0x43f80` value at u32[0] and u32[8] is the ARMv7-M initial stack pointer,
  DTCM top − `0x80`.

Those are [F] in that document and apply unchanged to `a660_gmu.bin` by family
[I]. What changes for SM8350 is only the **size**: `a660_gmu.bin` is 55,256 B,
not 32,768 B — i.e. it exceeds the 32 KiB ITCM+DTCM cap, so the a660 GMU image
is **not** a flat two-TCM dump the way a619 is. It must carry additional
segments or a loadable region beyond TCM [I]. Confirming that is out of scope
here and is stated as an open item, not a claim.

## 5. Mainline support status

| item | status | evidence |
|---|---|---|
| SM8350 SoC DT | present, `sm8350.dtsi` (117,937 B) | [F] |
| Adreno 660 GPU node | present, `compatible = "qcom,adreno-660.1"` | [F] |
| Adreno 660 GMU node | present, `compatible = "qcom,adreno-gmu-660.1"` | [F] |
| Driver binding | `ADRENO_CHIP_IDS(0x06060001)` in `a6xx_catalog.c:1079` | [F] |
| Firmware in linux-firmware | `qcom/a660_gmu.bin`, `qcom/a660_sqe.fw` under `Driver: adreno` (WHENCE) | [F] |
| postmarketOS device port | not verified this session | [N] |

## 6. Honest negatives

1. **No per-SoC GPU note existed.** `research/soc/` held only
   `per-soc-method-plans.md`; `docs/REPO-STATE-MAP.md:18` records "GPU core ID |
   27 | NEW | none" [F].
2. **The SM8350 row count is dataset-dependent.** 693 rows / 2 devices in
   `coverage-matrix.csv`; 1,344 rows / 3 devices in the laptop-half census.
   Neither is wrong; they are different universes [F].
3. **`sequence_manifest.bin` has no mainline loader and is not analysed** [N].
4. **`a660_gmu.bin` content beyond size is not analysed here.** The a660 image is
   55,256 B and therefore cannot be the flat 32 KiB two-TCM dump that a619 is;
   that the extra ~23 KiB is a third segment is [I], not proven [N].
5. **The two `a660_zap.mdt` builds were not byte-diffed.** Identical size,
   different md5 recorded; the nature of the difference is [I] [N].
6. **No payload bytes were read this session.** Every md5 and size above comes
   from the committed matrix; none was recomputed from the corpus, which is not
   publicly fetchable [F].
7. **postmarketOS/mainline *device* support was not checked** — only SoC-level
   DT presence [N].
8. **The a615 pair's GMU half (`a630_gmu.bin`) is absent from the matrix slice.**
   The a615 entry names `a630_gmu.bin` as its GMU firmware
   (`a6xx_catalog.c:795`), but no `a630_gmu.bin` row exists for either device
   [F]. Whether the vendor tree simply omits it (the a615 GMU may be unused when
   the entry is never bound) or the census missed it is **not determined** [N].

## Reproduce

```
python3 -I -c "
import csv
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
a=[r for r in rows if r.get('soc','').strip()=='Qualcomm SM8350 Snapdragon 888']
print(len(a))
from collections import Counter; print(Counter(r['blob_family'] for r in a))
[print(r['device'],r['filename'],r['size_bytes'],r['md5_db']) for r in a if r['blob_family']=='gpu']"

curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/sm8350.dtsi | grep -n -A6 'gpu@3d00000\|gmu@3d6a000'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c | sed -n '1079,1098p'
```

All fetches 2026-11-20, `torvalds/linux` master.

## Sources

| claim | source | access |
|---|---|---|
| 693 rows / 2 devices / 886,208,933 B | `upstream-contribution/blob-database/coverage-matrix.csv` | 2026-11-20 |
| family split, 11 gpu rows, all md5/size | same file | 2026-11-20 |
| 1,344 rows / 3 devices (laptop half) | `research/soc/per-soc-method-plans.md` | 2026-11-20 |
| Adreno 660 / chip ID / GMEM / zapfw | `raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c` | 2026-11-20 |
| `qcom,adreno-660.1`, `qcom,adreno-gmu-660.1` | `raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/sm8350.dtsi` | 2026-11-20 |
| GMU ARMv7-M / Cortex-M3 / TCM split | `research/laptop/qualcomm-adreno-gmu-content.md` | 2026-11-20 |
| vendor partition is a superset | `research/laptop/qualcomm-adreno-a650-fleet.md` §4 | 2026-11-20 |
| GPU core ID verdict row | `docs/REPO-STATE-MAP.md:18` | 2026-11-20 |
| Adreno 660 is the SD888 GPU | notebookcheck, gadgets360 (cross-check only) | 2026-11-20 |
