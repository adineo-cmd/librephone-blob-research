# oneplus OnePlus_7T_Pro (hotdog) — `boot` family: 9 rows, and the structural test that replaces the round-size heuristic

Analysis date 2026-11-21. Analyst: OC-3 (issue [#1484](https://github.com/adineo-cmd/open-device/issues/1484)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `f80f251`). No payload bytes fetched; every number below is
command output from this session.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Verdict

`OnePlus_7T_Pro` has **9 boot rows / 230,313,984 B**, and **3 of them are 98.3% of
the mass** [F]. The device note alone would be a footnote. What makes it worth
filing is that this second sample **refuted part of my own #1466 argument** and
supplied a stronger test in its place:

> **#1466's "MiB-exact ⇒ partition dump" heuristic is not the right test.** The
> sharper test is structural: **a device's `boot.img` is MiB-exact if and only if
> the device also has a `dtbo.img` row** — 116 of 116, with **zero** exceptions in
> either direction [F]. Round size is the *symptom*; the presence of a `dtbo`
> partition is the *marker*. (I tried to explain the marker as device age and
> **failed** — see §3.2.1. The correlation is exact; the mechanism is open.)

I also found a **new data-integrity defect** (#1466 did not catch it): the boot
family contains **29 duplicate rows** — 27 `(device, filename)` pairs — that
inflate the family by **1,673,573,576 B = 7.0%** [F]. All 29 are benign
re-extractions (identical md5), but they mean the family's row count and byte
total are both wrong as published.

## 1. The device's 9 boot rows

| file | size (B) | MiB | md5 (first 12) | kind |
|---|---:|---:|---|---|
| `boot.img` | 100,663,296 | **96.00** | `f03f80962cd4` | partition dump |
| `recovery.img` | 100,663,296 | **96.00** | `ab0525e63b52` | partition dump |
| `dtbo.img` | 25,165,824 | **24.00** | `21ba4962963f` | partition dump |
| `xbl.img` | 3,182,592 | 3.04 | `310de3f0c7ca` | real image |
| `abl.img` | 225,280 | 0.21 | `21f4c419fa0d` | real image |
| `aop.img` | 204,800 | 0.20 | `8144da9fb5f4` | real image |
| `xbl_config.img` | 126,976 | 0.12 | `21e6d1402d13` | real image |
| `qupfw.img` | 73,728 | 0.07 | `d18e8fc6b06f` | real image |
| `vbmeta.img` | 8,192 | 0.008 | `f0f1e8a04f02` | real image (AVB) |

[F] Total 230,313,984 B. The three dump rows are **226,492,416 B = 98.3%** of the
device's boot bytes; the six real images are **1.7%** (3,821,568 B) — together
less than a 4 MiB block.

This is the 9-row variant: `OnePlus_7T_Pro` carries `recovery.img` while
`OnePlus_7` and `OnePlus_7_Pro` do not [F]. Row counts across the 2×2 are
9 / 9 / 8 / 8 for 7T_Pro / 7T / 7 / 7_Pro.

## 2. The `boot.img == recovery.img` evidence

This is the sharpest single observation in this note, and it is the reason I
went looking for a better test.

### 2.1 The observation

Of the **65 devices in the fleet that carry both `boot.img` and `recovery.img`**,
**17 report the byte-identical size for both** [F]:

| size | devices |
|---:|---|
| 100,663,296 (96 MiB) | FP4, OnePlus_7T, **OnePlus_7T_Pro**, OnePlus_8, OnePlus_8T, OnePlus_8_Pro, OnePlus_9R, Phone_1, Pro_1X, Xperia_1_II, Xperia_5_II, Z5_Pro_GT |
| 67,108,864 (64 MiB) | Galaxy_A71, Redmi_8, Redmi_Note_7_Pro, Redmi_Note_8 |
| 134,217,728 (128 MiB) | Mi_10T_5G |

[F] **All 17 are exact MiB multiples. All 17 have different md5 for the two
files — 0 of 17 are byte-identical content.** Both facts matter:

- Different md5 proves the extraction really did capture two distinct
  partitions; it is not the same file copied twice [F].
- Equal size with different content, on 17 devices across 8 vendors, is what a
  **fixed-capacity window** looks like: both partitions are sized from the same
  board layout, and each contains different bytes padded to that size [I].

This is stronger than the #1466 argument. #1466 inferred dumps from round sizes
alone; here two *different* files on the same device agree exactly, which a
coincidence in build output would have to reproduce 17 times independently.

### 2.2 But it also shows the inference is not airtight

The 48 devices with both files where the sizes *differ* are still mostly
MiB-exact: **46 of 48 have a MiB-exact `boot.img`, 30 of 48 have a MiB-exact
`recovery.img`, 30 have both** [F]. So "same size" is a *sufficient* signal for
a dump pair, not a necessary one. It sharpens the case without covering it.

## 3. The structural test — what actually predicts a dump

### 3.1 The correlation

I tested a different hypothesis: a MiB-exact `boot.img` is not about the image at
all, it is about **whether the device also has a `dtbo` partition**. The result is
exact [F]:

```
devices with a boot.img row:            123
of those, with a dtbo.img row:          116
of those, MiB-exact boot.img:           116
devices with dtbo but not MiB-exact:      0
devices MiB-exact but no dtbo:            0
```

**`has dtbo.img` ⇔ `boot.img % 1048576 == 0`, 116/116, both directions, no
exceptions** [F].

### 3.2 The 7 counterexamples name themselves

The 7 devices with a non-MiB-exact `boot.img` are exactly the 7 with no `dtbo`
row [F]:

| device | boot.img (B) | MiB | SoC (DB) |
|---|---:|---:|---|
| Poco_3S | 21,788,672 | 20.779 | (blank in DB) |
| Redmi_4A | 21,241,856 | 20.258 | (blank in DB) |
| Xperia_10 | 35,610,624 | 33.961 | (blank in DB) |
| Xperia_10_Plus | 35,954,688 | 34.289 | SDM636 |
| Xperia_XA2 | 35,913,728 | 34.250 | SDM845 |
| Xperia_XA2_Plus | 35,905,536 | 34.242 | SDM845 |
| Xperia_XA2_Ultra | 35,917,824 | 34.254 | SDM845 |

[F] Their sizes are irregular to the last KiB (34.2422 / 34.2500 / 34.2539 MiB —
three XA2 variants within 12 KiB of each other, none equal). That is the
signature of a real built image. **No device has both a `dtbo` row and a
non-round `boot.img`, and none has a round `boot.img` and no `dtbo`.**

### 3.2.1 The age story does not survive — and the failure is informative

My first reading of §3.1 was "`dtbo` marks a post-2018 board layout". I checked
it and **it is wrong** [F]. Of the 116 devices in the `dtbo` set:

```
have an SoC string at all:        63
no SoC string (blank):            68
SoC strings that name SM6xxx/SM7xxx/SM8xxx (2019+): 59
SoC strings that name MSM8998:     2   -- OnePlus_7, OnePlus_7T
```

[F] So the age hypothesis has **68 unverifiable rows and 2 direct
counterexamples**, and I cannot claim it. Two further facts make the
counterexamples less damaging than they look, but neither rescues the claim:

1. `OnePlus_7` and `OnePlus_7T` are the **exact two devices whose `soc` label I
   demonstrate to be wrong in §5** — they are SM8150 `hotdog` hardware labelled
   MSM8998. So the only two apparent counterexamples sit on the only two rows
   already known to carry a bad SoC string [F, I].
2. The `dtbo` set is overwhelmingly SM-era: 11× SM6375, 6× SM8250, 4× SM7250,
   4× SM6115, 4× SM7325, 5× Google Tensor GS201, 5× Tensor G3 [F].

[I] So the correlation stands at 116/116 and is real; my *causal* explanation of
it is not established. The honest statement is: **`dtbo` presence predicts a
MiB-exact `boot.img` perfectly, and the mechanism is unresolved.** The 7
counterexamples are all old parts, which is suggestive, but "old" cannot be read
off this table for 68 devices and is contradicted on 2 more.

This matters for how the finding is used: it is a reliable **test** (you can
predict a dump from a `dtbo` row with 116/116 accuracy) but not yet an
**explanation**. Recording the failed age hypothesis is the point — a later
agent should not re-derive it from the same table.

Even without a mechanism it is a better test than #1466's, because it is
falsifiable and structural: any device added to the DB with a `dtbo.img` row
should have a MiB-exact `boot.img`, and any without should not.

### 3.3 The same test on `init_boot` and `pvmfw`

The correlation does not generalise blindly, which is the useful part [F]:

- `init_boot.img`: **29 devices, 29 MiB-exact (100%)** — this partition only
  exists on the newer layout, so the correlation is trivially satisfied.
- `pvmfw.img`: 18 devices, **16 MiB-exact**; the two exceptions are
  `OnePlus_13` and `Pad_2_Pro`, **both exactly 925,696 B**. Two devices with an
  identical irregular size is not a build coincidence — it is the same
  prebuilt payload shipped on two products [I].

So the rule is not "has `dtbo` ⇒ round"; it is "fixed-capacity window ⇒ round",
and `pvmfw` on those two is evidently a *content-sized* artifact, not a window.

### 3.4 Why the round-size fraction is misleading without this

The granularity ladder over all 1,038 boot rows [F]:

```
multiple of 1 MiB    :  364/1038 = 35.1%
multiple of 512 KiB  :  392/1038 = 37.8%
multiple of 64 KiB   :  449/1038 = 43.3%
multiple of 4 KiB    : 1010/1038 = 97.3%
```

97.3% at 4 KiB is just block alignment and says nothing. The signal lives
entirely in the 1 MiB step. §3.1 shows which devices produce it, and §3.2.1 shows
I could not establish *why* — so "1 MiB-exact" should be read as a marker to be
explained, not as a mechanism.

### 3.5 Where the MiB-exact rows cluster by vendor — a caution for #1466

`abl.img` and `xbl.img` are supposed to be the *real-image* controls, and their
MiB-exact rates are low (9/79 and 10/63) [F]. But the exact rows are not
scattered — they are concentrated [F]:

```
abl.img 1 MiB rows:  9  -> google 3, motorola 6   (of 79 rows: google 19, motorola 21)
xbl.img 5 MiB rows: 10  -> motorola 10            (of 63 rows: motorola 21)
```

[F] All 10 MiB-exact `xbl.img` rows are Motorola and all are exactly 5,242,880 B,
with **10 distinct md5**. All 9 MiB-exact `abl.img` rows are exactly 1,048,576 B,
also **9 distinct md5**.

**So a round size on a nominally real image is not proof of a dump.** Two
readings are possible and I did not distinguish them [OPEN]: either Motorola
pads `xbl`/`abl` partitions to a fixed window (dump), or its build packs to a
round size. The 1 MiB `abl` on Pixel_5/Pixel_5A/Pixel_4A_5G makes "dump of a
1 MiB abl partition" plausible but unproven.

The within-vendor ladder below is strong evidence for the *window* reading,
though not proof [F, I]:

```
Motorola xbl.img:  5,238,784 B x10 devices  (4.9961 MiB)  -- Moto_G10, G30, G32, G42, G52,
                                                             G9, G9_Power, G_Power, E7_Plus, Defy_2021
                   5,242,880 B x10 devices  (5.0000 MiB)  -- Moto_G200, G34_5G, G82_5G, G84_5G,
                                                             G_Stylus_5G, G_5G_2024, Edge_30,
                                                             Edge_30_Neo, Edge_30_Fusion, G_Stylus_5G-2-2022
difference: 4,096 B = exactly one 4 KiB block
```

Twenty Motorola devices, ten at 4.9961 MiB and ten at 5.0000 MiB, separated by
exactly one block, all 20 with distinct md5 [F]. A linker does not plausibly
produce that ladder. A partition window does — the older ten may carry a 4 KiB
header/table that the newer ten do not [I]. **This is the cleanest single
demonstration in the family that near-round sizes are capacity, and it is inside
one vendor, so it cannot be a cross-vendor coincidence.**

## 4. The duplicate rows — a defect #1466 missed

### 4.1 The numbers

```
boot family as published:      1,038 rows   23,864,283,348 B
after dedup (device,filename): 1,009 rows   22,190,709,772 B
removed:                          29 rows    1,673,573,576 B  = 7.013% of the family
```

[F] **The boot family's published byte total is 7.0% inflated by duplicate
rows.** #1466 reported the 23,864,283,348 B figure and the 86.8% MiB-exact share
without deduplicating; both numbers need restating (see §6).

### 4.2 What the duplicates are

[F] 27 `(device, filename)` pairs carry 2–4 rows each; **all 29 extra rows have
identical `size_bytes` *and* identical md5 to their sibling** — zero content
disagreements. So this is not a data conflict, it is double-counting.

The pattern is mechanical and identifiable by `db_path` [F]:

- **`recovery.img` accounts for 19 of the 27 pairs**, and in **18 of them** the
  two rows sit at `vendor/<dev>/radio` and `vendor/<dev>/vendor/etc`. Samsung
  contributes 44 of the 56 rows involved. The one exception is `Redmi_8`, whose
  duplicate `recovery.img` rows both sit at `xiaomi/Mi439/radio`.
- `Galaxy_A21S` is the worst: 5 duplicated filenames, and `recovery.img`
  appears **4 times** (`radio` plus `vendor/etc`, two rows each).
- `Redmi_8` duplicates 5 filenames at a single path (`xiaomi/Mi439/radio`) — so
  the cause is not only the two-directory split.

[I] The `radio` + `vendor/etc` pairing is the lab extracting the same partition
from two different package locations. The fix is a uniqueness constraint on
`(device, blob_family, filename)` or an explicit `source_path` column.

### 4.3 Consequence for the 17-device `boot == recovery` result

Three of the 17 same-size devices are among the duplicated ones (`Galaxy_A71`,
`Redmi_8`, `Z5_Pro_GT`) [F]. That does not weaken §2.1 — the sizes still agree
and the md5 still differ — but it means the *provenance* of those recovery rows
is a different extraction route (`Galaxy_A71` and `Z5_Pro_GT` carry both a
`radio` and a `vendor/etc` copy; `Redmi_8` carries two copies at
`xiaomi/Mi439/radio`). Flagged, not resolved [OPEN].

## 5. The 2×2 identity matrix — boot does not behave like tz

[F] The completed matrix for the four devices — `guacamoleb` (OnePlus_7),
`guacamole` (OnePlus_7_Pro), `hotdogb` (OnePlus_7T), `hotdog` (OnePlus_7T_Pro).
Note the codenames already group them {guacamole, guacamoleb} and
{hotdog, hotdogb} — **exactly the md5 grouping, and not the `soc` grouping**:

| file | OnePlus_7 | OnePlus_7T | OnePlus_7_Pro | OnePlus_7T_Pro |
|---|---|---|---|---|
| `abl.img` | `5110fec123` | `21f4c419fa` | `871670ed30` | `21f4c419fa` |
| `aop.img` | `ee447332f4` | `8144da9fb5` | `ee447332f4` | `8144da9fb5` |
| `boot.img` | `6480d74ff1` | `98b5345d68` | `157987009d` | `f03f80962c` |
| `dtbo.img` | `4ed0af342e` | `d35e259100` | `1e22713788` | `21ba4962963f` |
| `qupfw.img` | `cda17267c3` | `d18e8fc6b0` | `cda17267c3` | `d18e8fc6b0` |
| `recovery.img` | — | `12a4982918` | — | `ab0525e63b` |
| `vbmeta.img` | `197582fb38` | `39a45a32e2` | `700e569334` | `f0f1e8a04f` |
| `xbl.img` | `535defd055` | `310de3f0c7` | `535defd055` | `310de3f0c7` |
| `xbl_config.img` | `12dd816207` | `21e6d1402d` | `12dd816207` | `21e6d1402d` |

Pairwise [F]:

| pair | common | byte-identical | which |
|---|---:|---:|---|
| OnePlus_7 vs OnePlus_7_Pro | 8 | **4** | `aop`, `qupfw`, `xbl`, `xbl_config` |
| OnePlus_7T vs OnePlus_7T_Pro | 9 | **5** | those four + `abl` |
| OnePlus_7 vs OnePlus_7T | 8 | **0** | — |
| OnePlus_7 vs OnePlus_7T_Pro | 8 | **0** | — |
| OnePlus_7T vs OnePlus_7_Pro | 8 | **0** | — |
| OnePlus_7_Pro vs OnePlus_7T_Pro | 8 | **0** | — |

This confirms and completes #1466's partial matrix. The structure is clean [F, I]:

- **The identical set is exactly the pre-ABL firmware** — XBL, XBL config, AOP,
  QUP — plus, in the 7T pair, ABL itself. `boot`, `dtbo`, `recovery`, `vbmeta`
  always differ.
- **The grouping is by product line and the codenames say so independently.**
  The `db_path` codenames are `guacamoleb` / `guacamole` for 7 / 7_Pro and
  `hotdogb` / `hotdog` for 7T / 7T_Pro [F] — i.e. two product families of two
  devices each, **exactly the md5 grouping**.
- **The `soc` column contradicts both.** The DB labels `OnePlus_7` *and*
  `OnePlus_7T` as "MSM8998 Snapdragon 835", and `OnePlus_7_Pro` as SM8150,
  `OnePlus_7T_Pro` as SM8150-AC. That groups {7, 7T} / {7_Pro, 7T_Pro}. But the
  md5 grouping is {7, 7_Pro} / {7T, 7T_Pro}, which follows the codenames
  (`guacamole`/`guacamoleb`, `hotdog`/`hotdogb`) and **not** the `soc` column:
  every cross-group pair is 0 of 8 identical [F].

  The DB's own two `_Pro` rows anchor the codename→SoC mapping: `guacamole` =
  SM8150 and `hotdog` = SM8150-AC. On that anchor the non-Pro rows should be
  SM8150 (`guacamoleb`) and SM8150-AC (`hotdogb`) — so **the `soc` column is
  wrong for exactly the two rows it labels MSM8998**, and it is the md5 groups
  that are right [F, I].

### 5.1 Contrast with tz — the same 2×2, opposite result

[F] Re-running the identical test on the `tz` family for the same four devices:

| pair | common | byte-identical |
|---|---:|---:|
| OnePlus_7 vs OnePlus_7_Pro | 83 | **83 (100%)** |
| OnePlus_7T vs OnePlus_7T_Pro | 85 | **85 (100%)** |
| OnePlus_7 vs OnePlus_7T | 83 | 59 |
| OnePlus_7 vs OnePlus_7T_Pro | 83 | 59 |
| OnePlus_7T vs OnePlus_7_Pro | 83 | 59 |
| OnePlus_7_Pro vs OnePlus_7T_Pro | 83 | 59 |

[F] The line grouping is **identical** ({7, 7_Pro}, {7T, 7T_Pro}) and in `tz` it
is byte-complete: 83/83 and 85/85. In `boot` it is only 4/8 and 5/9.

**So the two families agree on the grouping and disagree on the depth** [F, I].
That is a real result and it refutes a tempting generalisation: #1466 warned
against reading the 4/8 boot identity as platform evidence, but combined with
`tz` at 100% the *grouping* is now doubly attested. The correct statement is
narrower than either note alone: **the product-line grouping is confirmed by two
independent families; the amount of shared content is family-specific, with `tz`
wholly shared and `boot` sharing only the pre-ABL layer.**

Note that #1472's `tz` 83/83 result is not a property of OnePlus or of
Snapdragon — it is a property of `tz` builds. It must not be extended to `boot`,
`gpu`, or `modem` without the same measurement.

### 5.2 The `gpu` family: 4 rows, identical on all four devices

[F] For completeness, since it bears on the `soc`-label question:

| file | size | md5 | OnePlus_7 | 7T | 7_Pro | 7T_Pro |
|---|---:|---|---|---|---|---|
| `a630_gmu.bin` | 32,768 | `1ade6a6597` | ✓ | ✓ | ✓ | ✓ |
| `a630_sqe.fw` | 32,304 | `42b0a1566c` | ✓ | ✓ | ✓ | ✓ |
| `a640_gmu.bin` | 37,680 | `99d0c614ab` | ✓ | ✓ | ✓ | ✓ |
| `a640_zap.mdt` | 6,860 | `d13ec13678` | ✓ | ✓ | ✓ | ✓ |

[F] All four files are byte-identical on all four devices — 4/4, every pair. The
`gpu` family therefore carries **no** product-line signal at all: it is a single
Adreno 630/640 firmware set shipped on all four.

This is a useful negative and it is consistent with the lab-wide finding that
**GPU firmware filenames never match the GPU revision** (`a630_*` and `a640_*`
coexist on one device; `a640_zap.mdt` present where the DB claims MSM8998). It
is direct evidence that the `gpu` family cannot be used to date or identify a
device's SoC [F, I].

## 6. What this corrects in #1466 (Rule 1 — corrections for the lead, not applied)

These are defects in my own shipped note `docs/devices/oneplus/OnePlus_7/boot.md`
(`f80f251`). I am not editing that file in this session's commit; they are listed
for the lead to apply, per the file-wall rule.

1. **Byte totals are 7.0% inflated.** `boot.md:135` states the family total as
   `23,864,283,348 B`. After removing 29 duplicate rows the correct figure is
   **22,190,709,772 B**. The 22.2 GiB claim at `boot.md:157` and the "boot vs tz
   vs gpu" comparison at `boot.md:160-162` inherit the error.
2. **The 86.8% mass figure is wrong for the same reason.** Dedup gives
   **354 MiB-exact rows of 1,009 = 20,197,670,912 B = 91.0%** — the mixed-column
   conclusion gets *stronger* (91.0%, not 86.8%), but the number changes. The
   figure appears four times in the shipped note (`boot.md:19`, `:137`, `:140`,
   `:157`); all four need the dedup'd value.
3. **The MiB-exact heuristic should be replaced by the `dtbo` correlation**
   (`boot.md:44-72`, §2.1's table). The `has dtbo ⇔ MiB-exact` biconditional at
   116/116 is a stronger and falsifiable claim than "89–100% vs 0–16%".
4. **`recovery.img`'s [OPEN] at `boot.md:213-214` is now resolved.** It is not an
   ambiguous middle: 53/86 MiB-exact as published (47/65 after dedup), and the
   decisive evidence is the 17-device `boot == recovery` size agreement with
   differing md5 (§2.1). The MiB-exact recovery rows are dumps of a fixed
   window; the non-exact ones are 15/18 Samsung after dedup — a different
   extraction. This also corrects the 62% figure at `boot.md:60` (61.6% before
   dedup, 72.3% after).
5. **`abl.img` / `xbl.img` are not clean controls.** `boot.md:100-102` presents
   them as evidence the test "discriminates cleanly in both directions", and
   cites `abl.img`'s irregular sizes as proof a linker produced them. §3.5
   shows the round `abl`/`xbl` rows are 100% vendor-concentrated (9
   Google/Motorola `abl` at exactly 1 MiB, 10 Motorola `xbl` at exactly 5 MiB)
   with 19 distinct md5 — i.e. those are probably *dumps* of a round partition,
   not build output. The control argument survives for
   `vbmeta`/`qupfw`/`xbl_config`/`aop`/`shrm` (genuinely 0%) but not for
   `abl`/`xbl`. The cited irregular `abl` sizes (151,552 / 155,648 / …) are real
   but they are the *majority* of `abl` rows, not all of them.
6. **`docs/REPO-STATE-MAP.md:33,47`** still reads boot = PARTIAL / "no byte-level
   cross-device container spec". Two of my notes now supply exactly that kind of
   cross-device evidence (`#1466`, `#1484`), plus the ABL container spec
   (`implementations/boot/README.md`, #2042). The stated reason is out of date;
   the PARTIAL verdict itself still holds (no parser).
7. **`docs/REPO-STATE-MAP.md:18`** still reads "GPU core ID | 27 | NEW | none".
   **Seventh flag** — `research/soc/` holds four shipped per-SoC GPU notes, and
   §5.2 above adds a fifth device-level GPU result.

## 7. Honest negatives

1. **I read no payload bytes.** Every claim about *what* is inside these files
   is inference from size, md5 and `db_path` [I, N]. The `dtbo` correlation in
   §3.1 is a 116/116 fit to a *hypothesis about cause*; I did not open a `dtbo`
   image to confirm it is a device-tree table [N].
2. **The `dtbo` correlation is confounded and I could not isolate it.** The
   "device age" explanation I first proposed is **refuted in §3.2.1** (68 rows
   have no SoC string, and 2 `dtbo` devices are labelled MSM8998). I therefore
   have an exact 116/116 correlation with no established mechanism [I, OPEN].
3. **I did not identify the extraction tool.** Whether `radio/` and `vendor/etc/`
   are different tools or the same tool at two paths is unread; I did not open
   `tools/phase1_build.py` [N]. §4.2's "two package locations" is inference.
4. **`boot == recovery` at 17 of 65 does not prove dumps.** Equal size with
   different md5 is consistent with a fixed window, but also with two builds
   padded to the same target. The 17/17 MiB-exactness and the §3.5 Motorola
   ladder make the window reading much more likely; it is not proof [I].
5. **The Motorola 4 KiB ladder (§3.5) has two readings** — partition window with
   and without a 4 KiB header, or two build recipes. I lean to the window
   because 20 distinct md5 at exactly two sizes is implausible for a linker, but
   a single `xbl.img` header read would settle it [I, OPEN].
6. **The `soc` column contradiction (§5) is not a finding about OnePlus alone.**
   I showed the four devices' firmware groups {7, 7_Pro} / {7T, 7T_Pro} while the
   `soc` column groups {7, 7T} / {7_Pro, 7T_Pro}. I did not audit how widespread
   this mislabel is across the other multi-device families in the matrix [OPEN].
7. **`unsparse_super_empty.img` duplicates (§4.2) were not investigated.** Two
   devices (`Galaxy_A21S`, `Redmi_8`) duplicate this file at a single path, which
   the two-directory explanation does not cover [N].
8. **The `gpu` result (§5.2) is 4 files on 4 devices.** It is consistent with
   #2018's four-device GPU byte-identity but is not an independent confirmation
   of it — same device family, likely same source [I].

## 8. Reproduce

```sh
# run from the repo root (the checkout that contains upstream-contribution/)

# the device's 9 rows
python3 -I -c "
import csv
for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')):
    if x['device']=='OnePlus_7T_Pro' and x['blob_family']=='boot':
        print(f\"{x['filename']:14s} {x['size_bytes']:>10s} {x['md5_db'][:12]} {x['db_path']}\")"

# the dtbo biconditional
python3 -I -c "
import csv
from collections import defaultdict
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot']
d=defaultdict(dict)
for x in r: d[x['device']][x['filename']]=int(x['size_bytes'])
boot=[k for k,v in d.items() if 'boot.img' in v]
has=[k for k in boot if 'dtbo.img' in d[k]]
ex=[k for k in boot if d[k]['boot.img']%1048576==0]
print(len(boot),len(has),len(ex),set(has)==set(ex))"

# the 17-device boot == recovery agreement
python3 -I -c "
import csv
from collections import defaultdict
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot']
d=defaultdict(dict)
for x in r: d[x['device']][x['filename']]=(int(x['size_bytes']),x['md5_db'])
b={k:v for k,v in d.items() if 'boot.img' in v and 'recovery.img' in v}
s=[k for k in b if b[k]['boot.img'][0]==b[k]['recovery.img'][0]]
print('both',len(b),'same-size',len(s),'md5-equal',sum(1 for k in s if b[k]['boot.img'][1]==b[k]['recovery.img'][1]))"

# the duplicate rows
python3 -I -c "
import csv
from collections import Counter
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot']
c=Counter((x['device'],x['filename']) for x in r)
dup={k for k,v in c.items() if v>1}
extra=[x for x in r if (x['device'],x['filename']) in dup]
seen=set(); rem=0
for x in r:
    k=(x['device'],x['filename'])
    if k in seen: rem+=int(x['size_bytes'])
    seen.add(k)
print('rows',len(r),'dup pairs',len(dup),'extra rows',sum(v-1 for v in c.values() if v>1),'extra bytes',rem)"

# the Motorola xbl 4 KiB ladder
python3 -I -c "
import csv
from collections import Counter
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot' and x['filename']=='xbl.img' and x['db_path'].startswith('motorola')]
print(Counter(int(x['size_bytes']) for x in r))"
```

## What would upgrade this finding

1. Read one `dtbo.img` header and one `boot.img` header from the same device: if
   the boot window is the partition size and `dtbo` is a real DTB table, §3.1's
   *mechanism* would finally have evidence — currently the correlation is exact
   but unexplained (§3.2.1).
2. Read `tools/phase1_build.py` and settle whether `radio/` and `vendor/etc/` are
   different extraction routes (§4.2, honest negative 3 in §7).
3. Apply the `has dtbo ⇔ MiB-exact` test to the other 12 blob families. If it
   holds for `recovery` but not for `modem`/`adsp`, the test is partition-shaped
   rather than layout-shaped.
4. Audit the `soc` column across all multi-device families, not just these four
   (§5, honest negative 6 in §7). The `guacamole`/`hotdog` codenames give an
   independent anchor; if
   the same {product-line vs `soc`-label} inversion recurs, it is a systematic
   column defect rather than four bad rows.
5. Read one Motorola `xbl.img` from each of the two size groups (§3.5) — the
   4,096 B difference would immediately show whether the smaller one carries a
   header the larger lacks.

Not legal advice; no proprietary payload accessed or committed. All facts are DB
metadata plus cited public sources.
