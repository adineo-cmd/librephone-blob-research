# Qualcomm MSM8998 Snapdragon 835 — GPU core identification and firmware

Issue #2018. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number is command output from this session (2026-11-20)
against the committed 33,917-row matrix and against `torvalds/linux` master.

## 1. The GPU: Adreno 540 — an **a5xx** part, not a6xx

**Verdict: the MSM8998 GPU is an Adreno 540, chip ID `0x05040001`, family
`ADRENO_5XX`.** It is *not* a GMU-class a6xx part, and that distinction turns
out to be the whole story of this issue.

### 1.1 Device-tree evidence

```dts
/* arch/arm64/boot/dts/qcom/msm8998.dtsi:1527 */
adreno_gpu: gpu@5000000 {
    compatible = "qcom,adreno-540.1", "qcom,adreno";
```

[F] `msm8998.dtsi` is 77,917 B and there are 14 `msm8998-*` device dts files.

### 1.2 The catalog entry — a5xx firmware grammar

Adreno 540 lives in **`a5xx_catalog.c`**, not `a6xx_catalog.c` [F]:

```c
/* a5xx_catalog.c:132-150 */
.chip_ids = ADRENO_CHIP_IDS(0x05040001),
.family = ADRENO_5XX,
.revn = 540,
.fw = {
    [ADRENO_FW_PM4]  = "a530_pm4.fw",
    [ADRENO_FW_PFP]  = "a530_pfp.fw",
    [ADRENO_FW_GPMU] = "a540_gpmu.fw2",
},
.gmem = SZ_1M,
.funcs = &a5xx_gpu_funcs,
.zapfw = "a540_zap.mdt",
```

Three consequences, all [F]:

1. There is **no `a540_sqe.fw`** and **no `a540_gmu.bin`**. The a6xx naming
   pattern does not exist here at all.
2. The GMU analogue is **`a540_gpmu.fw2`** — a *GPMU* with a `.fw2` extension,
   not a GMU with a `.bin` extension.
3. The SQE analogue is a **PM4/PFP pair** (`a530_pm4.fw` + `a530_pfp.fw`),
   borrowed from the a530 entries.

The chip ID `0x05040001` also differs structurally from the a6xx IDs: `05` in
the top byte marks the 5xx generation where a6xx uses `06` [F].

### 1.3 Why the two grammars are easy to confuse — the driver aliases the slots

This is the mechanism that makes the error in §2 possible, and it is in the
driver's own data structure [F]:

```c
/* adreno_gpu.h:25-29 */
ADRENO_FW_PM4  = 0,
ADRENO_FW_SQE  = 0, /* a6xx */
ADRENO_FW_PFP  = 1,
ADRENO_FW_GMU  = 1, /* a6xx */
ADRENO_FW_GPMU = 2,
```

**Slot 0 is SQE on a6xx and PM4 on a5xx. Slot 1 is GMU on a6xx and PFP on
a5xx.** Any census that reads a firmware role without also reading the family
will equate an a6xx SQE with an a5xx PM4 — which is exactly the class of error
that produced the mislabelled cluster in §2 [I].

The a5xx-vs-a6xx architectural difference itself is **public prior art**, stated
explicitly in LWN, *Add support for Adreno a6xx* (lwn.net/Articles/762040):
"On the a5xx there was a rudimentary … On the a6xx the power complexity is
being moved to a component called the GMU". **I am not claiming that
distinction as a finding** — I cite it and apply it to this corpus [F].

## 2. The 871 "MSM8998" rows are SM8150 devices — and their GPU firmware is architecturally impossible for an 835

The SoC mislabel is **already documented in this repo** at
`research/soc/per-soc-method-plans.md:74`:

> "OnePlus 7 (`guacamoleb`) and OnePlus 7T (`hotdogb`) carry 'MSM8998 835'
> (they are SM8150). Consequence: the MSM8998 cluster's entire 871-row blob
> content is actually SM8150-family firmware."

[F] I **cite this, do not re-announce it**. What that note does not contain is
the GPU-specific proof, which is what follows.

### 2.1 The label is wrong on three independent grounds

| ground | evidence | class |
|---|---|---|
| codename | all 871 rows sit under `oneplus/guacamoleb/...` (7) and `oneplus/hotdogb/...` (7T) [F] | [F] |
| public spec | LineageOS wiki: `guacamoleb` = **SM8150 Snapdragon 855**; `hotdogb` = **SM8150-AC Snapdragon 855+** | [F] |
| firmware | all 8 gpu rows are a6xx `GMU`/`SQE` files, which an a5xx Adreno 540 cannot load | [F] |

The third ground is the one that matters here: even without knowing which SoC
the devices really are, the **firmware alone falsifies the 835 label**. An
Adreno 540 loads `a530_pm4.fw` / `a530_pfp.fw` / `a540_gpmu.fw2` /
`a540_zap.mdt` and has no GMU; the rows carry `a630_gmu.bin` / `a630_sqe.fw` /
`a640_gmu.bin` / `a640_zap.mdt` [F].

### 2.2 The four-device byte-identical control

This is the cleanest proof and it needs no external source. Four OnePlus
devices carry **identical GPU firmware in filename, size and md5** [F]:

| device | `soc` label | a630_gmu.bin | a630_sqe.fw | a640_gmu.bin | a640_zap.mdt |
|---|---|---:|---:|---:|---:|
| OnePlus_7 | **MSM8998 835** | 32,768 / `1ade6a65…` | 32,304 / `42b0a156…` | 37,680 / `99d0c614…` | 6,860 / `d13ec136…` |
| OnePlus_7T | **MSM8998 835** | 32,768 / `1ade6a65…` | 32,304 / `42b0a156…` | 37,680 / `99d0c614…` | 6,860 / `d13ec136…` |
| OnePlus_7_Pro | SM8150 855 | 32,768 / `1ade6a65…` | 32,304 / `42b0a156…` | 37,680 / `99d0c614…` | 6,860 / `d13ec136…` |
| OnePlus_7T_Pro | SM8150-AC 855+ | 32,768 / `1ade6a65…` | 32,304 / `42b0a156…` | 37,680 / `99d0c614…` | 6,860 / `d13ec136…` |

Verified programmatically: `len(set(gpu_sets.values())) == 1` → **True** [F].

Two labels cannot both describe one byte-identical firmware set. The SM8150
pair is the one that matches the firmware (`a640` = Adreno 640 = SM8150), so the
MSM8998 label on the other two is the error [I].

### 2.3 What the 8 gpu rows actually are

| file | belongs to | mainline evidence |
|---|---|---|
| `a630_sqe.fw` | a610 / a615 / a618 / a619 / a630 / a640 / a680 entries, plus the unnamed `0x06010800` entry | `a6xx_catalog.c:745,777,794,824,851,875,900,924,1012,1032,1155` |
| `a640_gmu.bin` | Adreno 640 (`revn = 640`) **and** Adreno 680 (`revn = 680`) | `a6xx_catalog.c:1033,1156` |
| `a640_zap.mdt` | Adreno 640 and Adreno 680 | `a6xx_catalog.c:1040,1163` |
| `a630_gmu.bin` | a615 / a618 / a630 — **dead weight on an a640** | `a6xx_catalog.c:795,825,852,1013` |

[F] So the live SM8150 set is `a630_sqe.fw` + `a640_gmu.bin` + `a640_zap.mdt`
(76,844 B); `a630_gmu.bin` (32,768 B) is co-resident dead weight — **30% of the
device's gpu bytes cannot load** [F]. That is the same vendor-partition-superset
pattern as the a650 fleet (`research/laptop/qualcomm-adreno-a650-fleet.md` §4).

Note the `a640` pairing rule: **Adreno 680 also loads `a640_gmu.bin` and
`a640_zap.mdt`** (`a6xx_catalog.c:1156,1163`), so `a640_gmu.bin` is not
640-exclusive either — the same filename-does-not-imply-revision trap as
`a630_sqe.fw` in my SM8350 note.

## 3. The corpus holds **zero** a540 firmware

```
a540_zap.mdt   anywhere in 33,917 rows: 0
a540_gpmu.fw2  anywhere in 33,917 rows: 0
any a540_* file at all:                 0
```

[F] The matrix contains **none of the four files** mainline binds to an Adreno
540. The 871-row cluster labelled MSM8998 therefore has **no GPU firmware for
the SoC it names** and a full a6xx set for a SoC it does not name.

### 3.1 The a5xx files that do exist belong to a different device set

47 rows across 6 devices carry a5xx firmware, and **none** is an MSM8998 device
[F]:

| device | `soc` label | files |
|---|---|---|
| Xperia_XA2 | SDM845 845 | `a508_zap.mdt`, `a530*` ×8 |
| Xperia_XA2_Plus | SDM845 845 | `a508_zap.mdt`, `a530*` ×8 |
| Xperia_XA2_Ultra | SDM845 845 | `a508_zap.mdt`, `a530*` ×8 |
| Xperia_10 | *(blank)* | `a508_zap.mdt`, `a530*` ×8 |
| Xperia_10_Plus | SDM636 636 | `a508_zap.mdt`, `a530*` ×8 |
| Poco_3S | *(blank)* | `a530_pfp.fw`, `a530_pm4.fw` |

[F] Two observations:

- These are **a530/a508-generation** devices, so an SDM845 label carrying
  `a530_*` files is itself a generation mismatch of the same kind — SDM845 is
  Adreno 630 (`a6xx`), not a530 [F]. Recorded as an open inconsistency, not
  pursued further here.
- `a530_pm4.fw` is **byte-identical on all 6 holders** (19,652 B,
  `68d56e5b6460…`) [F] — another fleet-wide invariant, like `a619_gmu.bin`
  across SM4375/SM8350 in my previous note.

### 3.2 The genuine Snapdragon 835 devices have **zero** rows

`per-soc-method-plans.md:265` names the genuine-835 devices — mata, joan,
nx659j, cheeseburger, walleye, taimen. I checked each against the matrix [F]:

```
mata          0 rows      walleye       0 rows
joan          0 rows      taimen        0 rows
cheeseburger  0 rows      nx659j        0 rows
```

And the only two devices carrying the MSM8998 label are the two SM8150 phones
[F]:

```
devices with soc containing "MSM8998": ['OnePlus_7', 'OnePlus_7T']
```

So the honest statement is: **the matrix has no Snapdragon 835 GPU data at
all.** Not "sparse" — absent. First population of a real 835 device (Pixel 2 /
2 XL are the priority per `per-soc-method-plans.md:270`) is the entire task for
this cluster, and this issue cannot be completed from the corpus alone.

## 4. Cluster totals

```
MSM8998-labelled slice: 871 rows, 2 devices, 1,079,157,014 B
  families: other 452, tz 168, modem 70, wifi 68, adsp 34,
            bt 32, cdsp 22, boot 17, gpu 8
  OnePlus_7  433 rows / OnePlus_7T 438 rows
```

[F] The `docs/REPO-STATE-MAP.md:18` figure of "871 rows / 8 devices" (from
`per-soc-method-plans.md:56`) counts 8 devices for the cluster; the **matrix**
holds only 2 of them, both mislabelled [F]. These are the two different device
universes already noted in my SM8350 deliverable.

## 5. Honest negatives

1. **The SoC mislabel is prior art** at `per-soc-method-plans.md:74`; I cite it
   and supply the GPU proof, and claim no credit for the discovery [F].
2. **The a5xx-vs-a6xx GMU difference is public** (LWN 762040). My SEARCH comment
   proposed it as a delta; that was too broad and I retracted it in the Gate 0
   comment before writing [F].
3. **The Adreno 540 catalog entry is public** — it appears verbatim in the
   `[PATCH v3 2/5] drm/msm/adreno: Split catalog` series. Primary source [F].
4. **I did not verify why the `soc` column says MSM8998.** I proved it is wrong;
   I did not trace whether it came from a model-string parse, a heuristic, or a
   transcription error in `tools/phase1_build.py` [N].
5. **No payload bytes were read**; every md5/size is the db value, not recomputed
   from the corpus [F].
6. **The `a530_*`-on-SDM845 inconsistency** (§3.1) is recorded but not resolved
   — it may be the same mislabel class or a genuine vendor superset [N].
7. **`nx659j` is described in `per-soc-method-plans.md:266` as a Red Magic 5G
   (public SM8250)**, i.e. a third SoC contradiction in the same cluster. I did
   not investigate it; it has 0 rows so it cannot affect the GPU count [N].
8. **No claim that any of these files are loadable at runtime** — firmware
   presence is a census fact, not a boot proof [N].

## 6. Recommended corpus corrections (not applied — outside my file wall)

1. The `soc` value on the 871 OnePlus_7/7T rows should be `SM8150` /
   `SM8150-AC` respectively. This is a data correction the lead should make at
   source (`tools/phase1_build.py` inputs), not a research finding.
2. `docs/REPO-STATE-MAP.md:18` reads "GPU core ID | 27 | NEW | none"; with this
   note the count of per-SoC GPU identifications in `research/soc/` is **4**
   (SM8350, SM7325, SM4375, MSM8998). Still flagged, still not edited.

## Reproduce

```sh
# GPU identity
curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/msm8998.dtsi | sed -n '1526,1528p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a5xx_catalog.c | sed -n '132,150p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/adreno_gpu.h | sed -n '25,31p'

# zero a540 firmware; the 8 gpu rows
python3 -I -c "
import csv
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
print('a540 rows', sum(1 for x in r if x['filename'].startswith('a540')))
for x in r:
    if x['soc'].strip()=='Qualcomm MSM8998 Snapdragon 835' and x['blob_family']=='gpu':
        print(x['device'],x['filename'],x['size_bytes'],x['md5_db'][:12])"

# four-device byte-identical control
python3 -I -c "
import csv
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
d=['OnePlus_7','OnePlus_7T','OnePlus_7_Pro','OnePlus_7T_Pro']
s={k:frozenset((x['filename'],x['size_bytes'],x['md5_db']) for x in r if x['device']==k and x['blob_family']=='gpu') for k in d}
print('identical:', len(set(s.values()))==1)"
```

All kernel fetches 2026-11-20, `torvalds/linux` master.

## Sources

| claim | source | access |
|---|---|---|
| `qcom,adreno-540.1` | `msm8998.dtsi:1527` | 2026-11-20 |
| a540 chip ID `0x05040001`, `ADRENO_5XX`, `a540_gpmu.fw2`, `a540_zap.mdt` | `a5xx_catalog.c:132-150` | 2026-11-20 |
| firmware slot aliasing (SQE=PM4=0, GMU=PFP=1) | `adreno_gpu.h:25-29` | 2026-11-20 |
| a5xx vs a6xx GMU distinction (prior art) | LWN, *Add support for Adreno a6xx*, lwn.net/Articles/762040 | 2026-11-20 |
| a540 catalog hunk (prior art) | `[PATCH v3 2/5] drm/msm/adreno: Split catalog`, LKML archive | 2026-11-20 |
| SoC mislabel (prior art) | `research/soc/per-soc-method-plans.md:74`, `:265` | 2026-11-20 |
| 871 rows / 2 devices / 1,079,157,014 B / 8 gpu rows | `coverage-matrix.csv` | 2026-11-20 |
| four devices byte-identical GPU sets | `coverage-matrix.csv` | 2026-11-20 |
| zero `a540_*` rows; 47 a5xx rows / 6 devices | `coverage-matrix.csv` | 2026-11-20 |
| genuine-835 devices have 0 rows | `coverage-matrix.csv` | 2026-11-20 |
| `guacamoleb` = SM8150, `hotdogb` = SM8150-AC | LineageOS wiki | 2026-11-20 |
| `a640_gmu.bin` also serves Adreno 680 | `a6xx_catalog.c:1156` | 2026-11-20 |
| vendor partition is a superset | `research/laptop/qualcomm-adreno-a650-fleet.md` §4 | 2026-11-20 |
