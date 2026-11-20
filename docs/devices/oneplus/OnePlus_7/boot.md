# oneplus OnePlus_7 — `boot` family: 8 rows, and the mixed-column problem under the whole family

Analysis date 2026-11-20. Analyst: OC-3 (issue [#1466](https://github.com/adineo-cmd/open-device/issues/1466)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `09cf1b7`), AOSP documentation, `torvalds/linux` master.
No payload bytes fetched; every number is command output from this session.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Verdict

`OnePlus_7` has **8 boot rows / 129,646,592 B**. The device note is short because
the set is small — but establishing it surfaced a problem that affects **the
whole `boot` family**, and that is the substance of this note:

> **The `boot` family's `size_bytes` column is a mixed column.** For most rows it
> is the *partition capacity*, not the image size. **364 of 1,038 rows are exact
> MiB multiples and carry 86.8% of the family's bytes.**

Any cross-family byte comparison, dedup-by-size heuristic, or "largest blob"
ranking that treats `boot` as homogeneous is wrong by up to 87% of its mass.

## 1. The device's 8 boot rows

| file | size (B) | MiB | md5 (first 12) | kind |
|---|---:|---:|---|---|
| `boot.img` | 100,663,296 | **96.00** | `6480d74ff12f` | partition dump |
| `dtbo.img` | 25,165,824 | **24.00** | `4ed0af342e14` | partition dump |
| `xbl.img` | 3,182,592 | 3.04 | `535defd0554f` | real image |
| `abl.img` | 225,280 | 0.21 | `5110fec123e9` | real image |
| `aop.img` | 204,800 | 0.20 | `ee447332f423` | real image |
| `xbl_config.img` | 126,976 | 0.12 | `12dd81620700` | real image |
| `qupfw.img` | 73,728 | 0.07 | `cda17267c339` | real image |
| `vbmeta.img` | 4,096 | 0.004 | `197582fb3810` | real image (AVB) |

[F] Total 129,646,592 B. **Two rows (`boot.img`, `dtbo.img`) are 97% of the
device's boot bytes** and both are exact MiB multiples; the other six are
irregular and small.

Note there is **no `recovery.img`** — `OnePlus_7T` has one (100,663,296 B, also
96 MiB) and `OnePlus_7` does not [F]. The 7T sets 9 files against the 7's 8.

## 2. The mixed column — the family-wide finding

### 2.1 The test

A real image built by a tool (`avbtool`, a linker, a packer) has an irregular
size. A partition dump has the partition's capacity, which on Android is
conventionally a round number of MiB. So: **what fraction of each filename's
rows are exact MiB multiples (`size % 1048576 == 0`)?** [F]

| file | rows | exact MiB | % | reading |
|---|---:|---:|---:|---|
| `dtbo.img` | 118 | **118** | 100% | partition dump |
| `init_boot.img` | 29 | **29** | 100% | partition dump |
| `dtb.img` | 7 | **7** | 100% | partition dump |
| `boot.img` | 125 | **118** | 94% | partition dump |
| `pvmfw.img` | 18 | 16 | 89% | mostly dump |
| `recovery.img` | 86 | 53 | 62% | mixed |
| `xbl.img` | 63 | 10 | 16% | real image |
| `cpucp.img` | 30 | 4 | 13% | real image |
| `abl.img` | 79 | 9 | 11% | real image |
| **`vbmeta.img`** | 115 | **0** | **0%** | real image |
| **`qupfw.img`** | 63 | **0** | **0%** | real image |
| **`xbl_config.img`** | 63 | **0** | **0%** | real image |
| **`aop.img`** | 40 | **0** | **0%** | real image |
| **`shrm.img`** | 30 | **0** | **0%** | real image |
| `bl1.img` / `bl31.img` / `tzsw.img` | 16 each | **0** | 0% | real image |

[F] The distribution is **bimodal with almost nothing in the middle**: the
dumpable partitions sit at 89–100%, the tool-built images at 0–16%.

### 2.2 It is not coincidence — many unrelated devices share one value

If 96 MiB were a real image size, devices would not agree on it. They do [F]:

| `boot.img` size | rows | **distinct devices** | example devices |
|---:|---:|---:|---|
| 100,663,296 (**96 MiB**) | 53 | **53** | Defy_2021, Edge_20, Edge_2021, Edge_30, Edge_30_Fusion |
| 67,108,864 (**64 MiB**) | 25 | 24 | Galaxy_A71, Galaxy_S20_FE, Mi_A3, Pixel_6, Pixel_6A |
| 201,326,592 (**192 MiB**) | 21 | **21** | Mi_12, Mi_12S, Mi_12S_Pro, Mi_12S_Ultra, Mi_12T_Pro |
| 57,671,680 (55 MiB) | 7 | 7 | Galaxy_Note_10, Galaxy_S10, Galaxy_S10_5G |
| 167,772,160 (160 MiB) | 4 | 4 | Nord_CE2, Nord_CE3, Realme_10_Pro, Realme_9_Pro |
| 61,865,984 (59 MiB) | 3 | 3 | Galaxy_F62, Galaxy_Tab_S6_LTE, Galaxy_Tab_S6_Wifi |

**53 different phones from at least four vendors all report exactly
100,663,296 B.** That is a partition capacity inherited from a board layout,
not a shared build [I]. The same argument applies to the 64 MiB and 192 MiB
groups.

### 2.3 The control group proves the test is sound

`vbmeta.img` is **0 of 115** MiB-exact, with exactly three distinct sizes [F]:

```
8,192 B x94     12,288 B x11     4,096 B x10
```

Those are AVB descriptor sizes — 4/8/12 KiB — which is what `avbtool` emits for
a small number of descriptors. `abl.img`'s sizes are likewise irregular
(151,552 / 155,648 / 176,128 / 204,800 …) because a linker produced them [F].

**So the test discriminates cleanly in both directions.** It is not "most
Android files are round" — `vbmeta`, `qupfw`, `xbl_config`, `aop`, `shrm` are
all 0%.

### 2.3.1 The pipeline names its own artifacts

The boot family contains a filename that settles part of the interpretation
without inference [F]:

```
unsparse_super_empty.img    25 rows, sizes 4,592–4,772 B, 0% MiB-exact
```

That is the lab's own name for an *un-sparsed, empty `super` partition*
capture. Two things follow [F, I]:

1. **Boot-family rows are not all build outputs.** Some are partition-level
   captures, and this row says so in its name.
2. **But "partition capture" and "round size" are different properties.** This
   artifact is 4.5 KB, not a multi-MiB window — an *empty* partition captures
   to almost nothing. The round sizes in §2.1 come specifically from
   **fixed-capacity** partitions (`boot`, `dtbo`, `dtb`, `init_boot`) whose
   extraction reads the whole window, not from every partition artifact.

So the correct statement is narrower than "boot rows are partition dumps": the
round-size rows are dumps of *fixed-capacity* partitions, and the test in §2.1
identifies exactly those.

### 2.4 The mass involved

```
boot family total:        23,864,283,348 B  = 22.2 GiB
MiB-exact rows:              364 of 1,038
MiB-exact bytes:          20,720,910,336 B  = 86.8% of the family
```

[F] **86.8% of the boot family's byte mass is a partition-capacity figure.**
For `OnePlus_7` alone the two dump rows are 97% of its boot bytes; for
`OnePlus_7T`, 98%.

## 3. What this does and does not mean

**Does not mean the data is wrong.** A partition dump is a legitimate artifact —
it is what you get imaging `/dev/block/by-name/boot`. It is *useful* for size
accounting of the partition.

**Does mean the column cannot be compared across filenames.** Concretely:

| use | status |
|---|---|
| "how big is the boot partition on device X" | valid [F] |
| "which device has the largest boot image" | **invalid** — measures partition capacity |
| dedup across devices by `(filename, size, md5)` | **safe** (md5 still distinguishes), but size-keyed dedup is not |
| "boot family is 22.2 GiB of firmware" | **misleading** — 86.8% is padding |
| cross-family byte share ("boot vs tz vs gpu") | **invalid** without excluding dump rows |

The last row is the sharp one. Comparing `boot` against `tz` (665,173,154 B) or
`gpu` (88,036,049 B) on raw bytes overstates `boot` by roughly a factor
attributable to padding [I].

The lab already carries this lesson in two other places —
`research/laptop/wifi-cpp-firmware-family.md:230` ("one number lies for a
padded window") and `research/cdsp-fleet/audit.md:170` ("The size of the MDT
file is not padded") — but it has never been applied to `boot`.

## 4. The 2×2 that partially holds — and a contrast with `tz`

I established in #1472 that `OnePlus_7`'s **tz** family is byte-identical to
`OnePlus_7_Pro` (83 of 83 files). The **boot** family behaves differently [F]:

| pair | common files | byte-identical |
|---|---:|---:|
| OnePlus_7 vs OnePlus_7_Pro | 8 | **4** |
| OnePlus_7T vs OnePlus_7T_Pro | 9 | **5** |
| OnePlus_7 vs OnePlus_7T | 8 | **0** |
| OnePlus_7 vs OnePlus_7T_Pro | 8 | **0** |
| OnePlus_7T vs OnePlus_7_Pro | 8 | **0** |
| OnePlus_7_Pro vs OnePlus_7T_Pro | 8 | **0** |

[F] The four files identical between `OnePlus_7` and `OnePlus_7_Pro` are exactly
`aop.img`, `qupfw.img`, `xbl.img`, `xbl_config.img` — **the four non-dump
images, and none of the dump rows**. `abl.img`, `boot.img`, `dtbo.img`,
`vbmeta.img` all differ.

The 7T pair adds a fifth: `OnePlus_7T` and `OnePlus_7T_Pro` also share
`abl.img`. That is the only ABL image in the whole 2×2 that is shared, and it
is worth noting as a carve-out rather than a general rule [F].

That is coherent: the *pre-ABL* firmware (XBL and its config, AOP, QUP) is
board-level and identical when two SKUs share a board; the ABL-and-later images
are built per product [I]. And it explains the tz result: TrustZone images in
this build family are shared wholesale, while boot-chain images are not [H].

**But it does not rescue the MSM8998 label.** `OnePlus_7` vs `OnePlus_7_Pro`
sharing 4 of 8 boot files is consistent with them being the same platform,
which is the *opposite* of what "MSM8998" vs "SM8150" claims [I].

## 5. Honest negatives

1. **I read no payload bytes.** Whether `boot.img` really contains zero padding
   to 96 MiB is inferred from the size being an exact MiB multiple shared by 53
   unrelated devices — **not** verified by opening one [I, N]. A single
   `boot.img` header read would settle it.
2. **"MiB-exact ⇒ partition dump" is a heuristic, not an identity.** A tool
   could coincidentally emit a round size. The 0% control group
   (`vbmeta`/`qupfw`/`xbl_config`/`aop`/`shrm`) makes coincidence implausible
   for the *aggregate*, but individual rows are not proven [I]. And as §2.3.1
   shows, *being* a partition artifact does not imply a round size — only
   fixed-capacity partitions produce those.
3. **`recovery.img` is the ambiguous middle (62%)** — I did not determine
   whether most recovery images are dumps or real images [OPEN].
4. **I did not identify which extraction produced these rows.** Whether the DB
   imaged partitions or unpacked images is a question for `tools/phase1_build.py`,
   which I did not read [N].
5. **The 4/8-file boot identity (§4) is a small sample** — 8 filenames. It is
   suggestive, not conclusive [I].
6. **Padding does not imply the *content* is a raw partition image.** A dump
   could still be a sparse image or a vendor-packed container within the window.
   Not tested [N].
7. **`OnePlus_7` has no `recovery.img` row**; I did not determine whether the
   device genuinely lacks a recovery partition or the extraction missed it [N].

## 6. Rule 1 — corrections for the lead, not applied here

1. **`coverage-matrix.csv` `size_bytes` for the boot family.** A `is_partition_dump`
   boolean (or a `size_kind` enum) derived from the §2.1 test would make the
   column usable. Suggested rows: `dtbo`, `init_boot`, `dtb`, `boot`,
   `pvmfw` (dump); `vbmeta`, `qupfw`, `xbl_config`, `aop`, `shrm`, `bl1`,
   `bl31`, `tzsw`, `abl`, `xbl` (image).
2. **`docs/REPO-STATE-MAP.md:33,47`** read boot = PARTIAL / "no byte-level
   cross-device container spec". The `abl` container spec is now documented
   (`implementations/boot/README.md`, #2042), and this note adds the
   size-column caveat. Still PARTIAL — no parser — but the stated reason is
   out of date.
3. **`docs/REPO-STATE-MAP.md:18`** still reads "GPU core ID | 27 | NEW | none".
   **Sixth flag**; `research/soc/` holds four shipped per-SoC GPU notes.

## Reproduce

```sh
# the MiB-exactness test, per filename
python3 -I -c "
import csv
from collections import defaultdict
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
agg=defaultdict(lambda:[0,0])
for x in r:
    if x['blob_family']!='boot': continue
    s=int(x['size_bytes']); agg[x['filename']][0]+=1
    if s%1048576==0: agg[x['filename']][1]+=1
for f,(t,e) in sorted(agg.items(),key=lambda y:-y[1][0]):
    print(f'{f:22s} {t:4d} rows {e:4d} MiB-exact {100*e/t:5.0f}%')"

# the mass
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot']
tot=sum(int(x['size_bytes']) for x in r)
ex=[x for x in r if int(x['size_bytes'])%1048576==0]
print('total',tot,'MiB-exact',len(ex),'of',len(r),'=',sum(int(x['size_bytes']) for x in ex),f'{100*sum(int(x[\"size_bytes\"]) for x in ex)/tot:.1f}%')"

# 53 distinct devices share 96 MiB
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['blob_family']=='boot' and x['filename']=='boot.img']
for s in sorted({int(x['size_bytes']) for x in r}):
    d={x['device'] for x in r if int(x['size_bytes'])==s}
    if s%1048576==0: print(s, s//1048576,'MiB', len(d),'distinct devices')"

# this device's rows
python3 -I -c "
import csv
for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')):
    if x['device']=='OnePlus_7' and x['blob_family']=='boot':
        print(f\"{x['filename']:18s} {x['size_bytes']:>10s} {x['md5_db'][:12]}\")"
```

## What would upgrade this finding

1. Read a `boot.img` header (AOSP `boot_img_hdr_v*`) from any of the 53 96-MiB
   rows: if `header_size + kernel_size + ramdisk_size` ≪ 96 MiB, §2 is proven
   directly rather than inferentially.
2. Read `tools/phase1_build.py` to confirm whether the pipeline images
   partitions or unpacks images (settles §5.4).
3. Apply the same MiB test to the other 12 blob families — if `modem`, `adsp`
   or `wlan` show dump rows too, the mixed-column problem is lab-wide and not
   boot-specific.

Not legal advice; no proprietary payload accessed or committed. All facts are DB
metadata plus cited public sources.
