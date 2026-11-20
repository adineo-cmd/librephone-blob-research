# Qualcomm SM7325 Snapdragon 778G 5G — GPU core identification and firmware

Issue #2030. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number is from a command run this session (2026-11-20)
against the committed matrix and against `torvalds/linux` master.

## 1. The GPU: mainline calls it `adreno-635.0`, marketing calls it Adreno 642L — and mainline binds it to a660 firmware

**Verdict: the SM7325 GPU is exposed in mainline DT as `qcom,adreno-635.0`,
derives to chip ID `0x06030500`, and the driver binds that chip ID to the
`a660_sqe.fw` / `a660_gmu.bin` / `a660_zap.mbn` firmware set — not to any
`a635`-named blob.** The commercial name is **Adreno 642L**.

That three-way split (DT name 635, marketing name 642L, firmware name a660) is
the finding, and it is why a filename-keyed census of this SoC cannot work.

### 1.1 DT evidence — the compatible string

`sm7325.dtsi` is a thin overlay. It carries **no GPU node at all**; it only
rebinds the eight CPUs to Kryo 670 and inherits everything else:

```dts
#include "kodiak.dtsi"
/* SM7325 uses Kryo 670 */
&cpu0 { compatible = "qcom,kryo670"; };
...
```

[F] `arch/arm64/boot/dts/qcom/sm7325.dtsi`, 537 B, contents as above.

The GPU lives in the parent `kodiak.dtsi` (202,322 B) [F]:

```dts
/* kodiak.dtsi:3217 */
gpu: gpu@3d00000 {
    compatible = "qcom,adreno-635.0", "qcom,adreno";

/* kodiak.dtsi:3312 */
compatible = "qcom,adreno-gmu-635.0", "qcom,adreno-gmu";
```

So the SM7325 GPU is **`adreno-635.0`**, and its GMU is **`adreno-gmu-635.0`** [F].

### 1.2 Chip-ID derivation — `0x06030500`, computed from the string

`find_chipid()` (`drivers/gpu/drm/msm/adreno/adreno_device.c:142`) parses the
compatible string rather than a `qcom,chipid` property:

```c
if (sscanf(compat, "qcom,adreno-%u.%u", &r, &patch) == 2 || ...) {
    core = r / 100;  r %= 100;
    major = r / 10;  r %= 10;
    minor = r;
    *chipid = (core << 24) | (major << 16) | (minor << 8) | patch;
```

For `qcom,adreno-635.0`: `r = 635`, `patch = 0` → `core = 6`, `major = 3`,
`minor = 5` → **`(6 << 24) | (3 << 16) | (5 << 8) | 0` = `0x06030500`** [F].
Verified by running the same arithmetic:

```
$ python3 -I -c "r=635; patch=0; core=r//100; r%=100; major=r//10; r%=10; minor=r; \
  print(hex((core<<24)|(major<<16)|(minor<<8)|patch))"
0x6030500
```

### 1.3 The catalog binds `0x06030500` to **a660** firmware and gives it no `revn`

`a6xx_catalog.c` lines 1123-1149 [F]:

```c
}, {
    .chip_ids = ADRENO_CHIP_IDS(0x06030500),
    .family = ADRENO_6XX_GEN4,
    .fw = {
        [ADRENO_FW_SQE] = "a660_sqe.fw",
        [ADRENO_FW_GMU] = "a660_gmu.bin",
    },
    .gmem = SZ_512K,
    .funcs = &a6xx_gpu_funcs,
    .zapfw = "a660_zap.mbn",
    .a6xx = &(const struct a6xx_info) {
        .hwcg = a660_hwcg,
        .protect = &a660_protect,
        ...
    },
```

Three things to note, all [F]:

1. The firmware names are **`a660_*`**, not `a635_*`. There is **no
   `a635_sqe.fw` or `a635_gmu.bin` anywhere in the kernel** — `grep -n "635"
   a6xx_catalog.c` returns exactly one hit, the comment at line 586
   (`/* These are for a635 and a660 */`), and `grep -rn a635` over
   `adreno_gpu.h` and `a6xx_gpu.h` returns nothing.
2. This entry has **no `.revn` field** — so `adreno_is_revn(gpu, 635)` is never
   true and there is **no `adreno_is_a635()` helper**.
3. `.zapfw` is `a660_zap.mbn` — note the **`.mbn`** suffix, whereas the SM8350
   a660 entry uses `a660_zap.mdt`. Different container extension for the same
   core.

### 1.4 The one code path that does name this chip ID calls it **7c3**

Because there is no `revn`, the driver identifies `0x06030500` by explicit chip
ID in `adreno_gpu.h:471-474` [F]:

```c
static inline int adreno_is_7c3(const struct adreno_gpu *gpu)
{
	return gpu->info->chip_ids[0] == 0x06030500;
}
```

It is used in two places:

- `a6xx_gpu.c:2769` — `if (adreno_is_a618(adreno_gpu) || adreno_is_7c3(adreno_gpu)) priv->gpu_clamp_to_idle = true;`
- `a6xx_gmu.c:572` — asserts Qactive during power collapse for `adreno_is_7c3(adreno_gpu)`.

**`7c3` is the Snapdragon 7c Gen 3** (an SC7280-family compute part), not the
778G. So mainline's own identifier for the GPU in the 778G names a *different
SoC* [F]. This is consistent with the public patch history: `[PATCH v3 3/3]
drm/msm/a6xx: Add support for Adreno 7c Gen 3 gpu` describes the core as
"similar to the existing a660 gpu" — which is exactly why the firmware is
`a660_*` [F, lore.kernel.org, accessed 2026-11-20].

**Interpretation [I]:** the 778G's Adreno 642L and the 7c Gen 3 share one
silicon core that Qualcomm brands two ways. Mainline grew the 7c Gen 3 support
first and the 778G DT reused the same chip ID, so the helper kept the `7c3`
name. The consequence is practical: any tool that looks for a per-SoC GPU
identity in mainline will see this SoC reported as *7c3*, and any tool that
looks for `a635_*` firmware will find nothing.

### 1.5 Marketing name is Adreno 642L — a third name for the same core

Public specification sources identify the Snapdragon 778G's GPU as **Adreno
642L** (cpu-monkey, notebookcheck, both 2026-11-20) [F]. So the same silicon
carries three names in three registers:

| register | name |
|---|---|
| marketing | Adreno 642L |
| mainline DT compatible | `adreno-635.0` |
| mainline firmware binding | `a660_sqe.fw` / `a660_gmu.bin` |
| mainline code helper | `adreno_is_7c3()` |

This is the clearest instance in the lab's data of why "Adreno NNN" is not an
identifier. The number in the marketing name (642) resolves to neither the DT
number (635) nor the firmware number (660), and Qualcomm's naming is documented
as non-ordinal by users comparing 642L against 640 [F, Reddit r/PickAnAndroidForMe].

## 2. What the matrix says

The matrix's SM7325 slice [F]:

```
total SM7325 rows  67
devices            Edge_20 (31 rows), Edge_2021 (36 rows)
gpu-family rows    8
```

Family split and the 8 GPU rows:

| device | filename | bytes | md5 | db_path |
|---|---|---:|---|---|
| Edge_20 | `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` | `motorola/berlin/vendor/gpu/kbc` |
| Edge_20 | `a615_zap.mdt` | 6,708 | `222f87861803bae8de24f0eb28bfc0d2` | `motorola/berlin/vendor/firmware` |
| Edge_20 | `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | `motorola/berlin/vendor/firmware` |
| Edge_20 | `a630_sqe.fw` | 32,456 | `21693ef6f2d686ce79ebb3716a099970` | `motorola/berlin/vendor/firmware` |
| Edge_2021 | `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` | `motorola/berlna/vendor/gpu/kbc` |
| Edge_2021 | `a615_zap.mdt` | 6,708 | `222f87861803bae8de24f0eb28bfc0d2` | `motorola/berlna/vendor/firmware` |
| Edge_2021 | `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | `motorola/berlna/vendor/firmware` |
| Edge_2021 | `a630_sqe.fw` | 32,456 | `21693ef6f2d686ce79ebb3716a099970` | `motorola/berlna/vendor/firmware` |

Both devices carry **byte-identical** sets — identical md5s across `berlin` and
`berlna` for all four [F].

## 3. The gap: the matrix holds **none** of the four blobs mainline needs

Mainline's `0x06030500` entry requires, by name [F]:

| required | present in SM7325 slice? |
|---|---|
| `a660_sqe.fw` | **no** |
| `a660_gmu.bin` | **no** |
| `a660_zap.mbn` | **no** |
| (`a615_zap.mdt` is present but belongs to the a615 entry) | — |

Verified by set difference:

```
present: {a615_zap.mdt, a619_gmu.bin, a630_sqe.fw, sequence_manifest.bin}
missing: {a660_zap.mdt, a660_sqe.fw, a660_zap.mbn, a660_gmu.bin}
```

So the 8 `gpu` rows contain **zero** of the firmware this SoC actually binds.
Worse, the blobs that *are* present belong to two other GPU generations:

| blob | belongs to | mainline evidence |
|---|---|---|
| `a619_gmu.bin` | Adreno 619 | `a6xx_catalog.c:876` / `:901` (revn 619) |
| `a630_sqe.fw` | a610 / a615 / a630 entries | `a6xx_catalog.c:745`, `:794`, `:1012` |
| `a615_zap.mdt` | a615 entry | `a6xx_catalog.c:801` |
| `sequence_manifest.bin` | KBC manifest, no `adreno` loader | — |

### 3.1 Is this a real absence or a census gap? — honest answer: undetermined

This is the crux, and I will not overclaim it.

**Arguments it is a census gap [I]:**

- `a660_zap.mbn` appears on **zero** devices in the entire 33,917-row matrix
  [F]. A blob that mainline requires and that no census row anywhere contains is
  far more likely uncollected than universally absent.
- The two Motorola device trees are shallow (31 and 36 rows) versus e.g.
  SM8350's 693. Their `gpu` family has 4 entries each; a real vendor tree that
  ships `sequence_manifest.bin` almost certainly also ships the a660 microcode.
- The matrix's own pre-existing note for these devices is `P3` priority with
  `isa_identified` empty for all 67 rows [F] — i.e. no ISA work has been done,
  so nothing here is verified-complete.

**Arguments it is a real absence [H]:**

- Both devices carry a coherent *other* GPU's firmware set, which is the
  co-residency pattern already documented for Sony/Motorola trees
  (`research/laptop/qualcomm-adreno-a650-fleet.md` §4).

**Verdict: the honest negative is that the matrix cannot answer this question
for SM7325** [N]. The finding that *is* solid is the three-way name split in §1
and the fact that no `a635_*` firmware exists in mainline at all. Any agent
following the filename would search for `a635_*` and find nothing — the correct
search target is `a660_*` with the `.mbn` zap suffix.

## 4. ISA

The GPU itself is an Adreno 6xx-generation part, and the matrix records no
`isa_identified` value for any of the 67 SM7325 rows [F]. The GMU microcontroller
ISA is **not** re-derived here: it is already proven in-repo as ARMv7-M /
Cortex-M3 class with the ITCM+DTCM `0x4000` split and Thumb reset vector
(`research/laptop/qualcomm-adreno-gmu-content.md`), and that family result
applies to Adreno 6xx GMUs generally [I].

What is specific to this entry and IS recorded: `.family = ADRENO_6XX_GEN4`
[F] — the same generation bucket as the SM8350's Adreno 660, which is consistent
with sharing the a660 firmware.

## 5. Mainline support status

| item | status | evidence |
|---|---|---|
| `sm7325.dtsi` | present, 537 B, CPU-only overlay | [F] |
| `kodiak.dtsi` (parent, owns the GPU) | present, 202,322 B | [F] |
| GPU node | `qcom,adreno-635.0` at `kodiak.dtsi:3217` | [F] |
| GMU node | `qcom,adreno-gmu-635.0` at `kodiak.dtsi:3312` | [F] |
| chip ID | `0x06030500`, derived from the compatible string | [F] |
| driver binding | `a6xx_catalog.c:1124`, `ADRENO_6XX_GEN4`, no `.revn` | [F] |
| `adreno_is_a635()` helper | **does not exist** | [F] |
| `a635_*` firmware in kernel | **does not exist** | [F] |
| postmarketOS port | exists per public wiki (778G/778G+/782G page) — not verified against this matrix | [N] |

## 6. Honest negatives

1. **No `a635_sqe.fw` / `a635_gmu.bin` exists anywhere in mainline.** A
   filename-keyed search for this SoC's GPU firmware fails by construction [F].
2. **No `adreno_is_a635()` helper exists**, because the catalog entry omits
   `.revn`; the driver identifies this core via `adreno_is_7c3()` [F].
3. **`a660_zap.mbn` has zero rows in the entire 33,917-row matrix**, so its
   absence from the SM7325 slice cannot be distinguished from a census gap [N].
4. **None of the four blobs mainline requires for this SoC is in the matrix.**
   The 8 `gpu` rows are entirely other generations' firmware [F].
5. **The `7c3` ↔ 778G equivalence is [I], not [F].** Both share chip ID
   `0x06030500` and the a660 firmware; that the marketing names differ for one
   silicon is inference from the kernel's own naming, not a vendor statement [I].
6. **No payload bytes were read this session**; every md5/size is from the
   committed matrix, not recomputed from the corpus [F].
7. **`sequence_manifest.bin` has no `adreno` loader** and its format is not
   analysed here [N].

## Reproduce

```
python3 -I -c "
import csv
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
a=[r for r in rows if r.get('soc','').strip()=='Qualcomm SM7325 Snapdragon 778G 5G']
print(len(a), sorted({r['device'] for r in a}))
[print(r['device'],r['filename'],r['size_bytes'],r['md5_db']) for r in a if r['blob_family']=='gpu']"

curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/sm7325.dtsi
curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/kodiak.dtsi | grep -n 'adreno-6'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c | sed -n '1123,1150p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/adreno_gpu.h | sed -n '471,475p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/adreno_device.c | sed -n '142,170p'
```

All fetches 2026-11-20, `torvalds/linux` master.

## Sources

| claim | source | access |
|---|---|---|
| 67 rows / 2 devices / 8 gpu rows / all md5+size | `upstream-contribution/blob-database/coverage-matrix.csv` | 2026-11-20 |
| `adreno-635.0`, `adreno-gmu-635.0` | `kodiak.dtsi:3217,3312` | 2026-11-20 |
| sm7325.dtsi is CPU-only overlay | `sm7325.dtsi` (537 B) | 2026-11-20 |
| chip ID derivation arithmetic | `adreno_device.c:142` (`find_chipid`) | 2026-11-20 |
| `0x06030500` binds `a660_*` + `a660_zap.mbn`, no `.revn` | `a6xx_catalog.c:1123-1149` | 2026-11-20 |
| `adreno_is_7c3()` = `chip_ids[0] == 0x06030500` | `adreno_gpu.h:471` | 2026-11-20 |
| 7c3 uses `gpu_clamp_to_idle`; Qactive on power collapse | `a6xx_gpu.c:2769`, `a6xx_gmu.c:572` | 2026-11-20 |
| "similar to the existing a660 gpu" | `lore.kernel.org` — `[PATCH v3 3/3] drm/msm/a6xx: Add support for Adreno 7c Gen 3 gpu` | 2026-11-20 |
| GPU marketed as Adreno 642L | cpu-monkey, notebookcheck | 2026-11-20 |
| 642L naming is non-ordinal | Reddit r/PickAnAndroidForMe | 2026-11-20 |
| GMU ARMv7-M / Cortex-M3 ISA | `research/laptop/qualcomm-adreno-gmu-content.md` | 2026-11-20 |
| vendor partition is a superset | `research/laptop/qualcomm-adreno-a650-fleet.md` §4 | 2026-11-20 |
