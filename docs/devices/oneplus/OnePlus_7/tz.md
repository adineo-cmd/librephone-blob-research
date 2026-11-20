# oneplus OnePlus_7 — `tz` family: full grammar decomposition, a 2×2 mislabel proof, and a fleet-wide law violation

Analysis date 2026-11-20. Analyst: OC-3 (issue [#1472](https://github.com/adineo-cmd/open-device/issues/1472)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `ce5116c`), `torvalds/linux` master, public spec pages.
No payload bytes fetched; every number below is command output from this session.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Verdict

`OnePlus_7` carries **83 tz rows / 83 distinct filenames / 9,818,262 B** in the
lab's tz family: 9 split trustlets (`.mdt` + `.b00`–`.b07`) and 6 monolithic
images. The family is **structurally complete** — no absence to report, unlike
`Galaxy_A21S` (#1012) — so this note's value is the decomposition, not a
missing-data verdict.

Two findings go beyond description:

1. **The device is not an MSM8998.** Its `tz.img` md5 pairs *only* with
   `OnePlus_7_Pro` (labelled SM8150), and `OnePlus_7T`'s pairs *only* with
   `OnePlus_7T_Pro` (labelled SM8150-AC) — a perfect 2×2. This extends
   #2018's byte-identical GPU control into the tz family.
2. **The `mdt == b00 + b01` relation this device obeys is violated on 190 of
   399 `.mdt` files fleet-wide**, with an unfailing signature: `.b01 > .mdt`
   in **190 of 190** cases.

## 1. Device identity and the label problem

| fact | value | class |
|---|---|---|
| codename | `guacamoleb` | [F] |
| matrix `soc` label | "Qualcomm MSM8998 Snapdragon 835" | [F] |
| public SoC | **SM8150 Snapdragon 855** (LineageOS wiki wiki, PixelExperience wiki) | [F] |
| tz rows | 83 rows, 83 distinct filenames, 9,818,262 B | [F] |

The mislabel is **already documented in-repo** at
`research/soc/per-soc-method-plans.md:74`, and I proved its GPU half in #2018
(`research/soc/Qualcomm-MSM8998-Snapdragon-835-gpu.md`). **I claim no credit
for the discovery**; §2 supplies the tz-family proof those notes lack.

## 2. The 2×2 proof — tz-family analogue of the #2018 GPU control

```python
# every tz.img in the corpus, grouped by md5
OnePlus_7       3,190,784  b88a2c00a75f606f...
OnePlus_7_Pro   3,190,784  b88a2c00a75f606f...   <- labelled SM8150
OnePlus_7T      3,190,784  b84940cb9c7c2cde...
OnePlus_7T_Pro  3,190,784  b84940cb9c7c2cde...   <- labelled SM8150-AC
```

Enumerating the md5 of `OnePlus_7`'s `tz.img` across the whole matrix returns
**exactly two devices: `OnePlus_7` and `OnePlus_7_Pro`** [F]. Same for the 7T
pair. The cross-pairs (`OnePlus_7` vs `OnePlus_7T_Pro`, `OnePlus_7T` vs
`OnePlus_7_Pro`) do **not** match.

Whole-family byte totals confirm it independently [F]:

| device | matrix `soc` label | tz rows | tz bytes |
|---|---|---:|---:|
| OnePlus_7 | **MSM8998 835** | 83 | 9,818,262 |
| OnePlus_7_Pro | SM8150 855 | 83 | **9,818,262** |
| OnePlus_7T | **MSM8998 835** | 85 | 9,961,622 |
| OnePlus_7T_Pro | SM8150-AC 855+ | 85 | **9,961,622** |

Four devices, two distinct TrustZone images, byte-identical totals within each
pair. Two labels cannot both describe one identical firmware set; the SM8150
label is the one that matches the firmware [I].

The pairing holds for the **entire** family, not just `tz.img` [F]:

```python
# frozenset of (filename, size_bytes, md5) over ALL tz rows
OnePlus_7     == OnePlus_7_Pro   -> True
OnePlus_7T    == OnePlus_7T_Pro  -> True
OnePlus_7     == OnePlus_7T      -> False
```

That is the complete tz family — every filename, every size, every md5 — equal
within each label pair and unequal across them.

## 3. The 83-row decomposition

### 3.1 Split trustlets — 9 families, 77 files

Every one of the nine follows the same `b00 … b07` + `mdt` shape, except
`cmnlib`/`cmnlib64` which stop at `b05` [F]:

| family | segments | `.b00` | `.b01` | `.mdt` | `.b02`+ (code) |
|---|---:|---:|---:|---:|---:|
| `cmnlib` | b00–b05 | 244 | 19,984 | 20,228 | 370,570 |
| `cmnlib64` | b00–b05 | 400 | 19,984 | 20,384 | 484,158 |
| `hdcp1` | b00–b07 | 512 | 6,952 | 7,464 | 41,005 |
| `hdcp2p2` | b00–b07 | 512 | 6,952 | 7,464 | 127,656 |
| `hdcpsrm` | b00–b07 | 512 | 6,952 | 7,464 | 28,623 |
| `smplap32` | b00–b07 | 308 | 6,952 | 7,260 | 1,684,660 |
| `smplap64` | b00–b07 | 512 | 6,952 | 7,464 | 1,759,740 |
| `soter64` | b00–b07 | 512 | 6,952 | 7,464 | 63,022 |
| `widevine` | b00–b07 | 512 | 6,952 | 7,464 | 158,316 |

[F] On all nine, `mdt − b01 == b00` exactly. So the envelope splits cleanly:

- **`.b00`** — 244–512 B. The ELF header portion, sitting at the front of the
  `.mdt`. Loaded (it is not a hash segment).
- **`.b01`** — 6,952–19,984 B. The program-header table portion.
- **`.b02`+** — the actual code segments.
- **`.mdt`** — a 7,260–20,384 B concatenation of `.b00` + `.b01`, which is why
  `mdt − b01 == b00` holds exactly [I].

Naming comes from `drivers/soc/qcom/mdt_loader.c`, which builds the segment
filename with `sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)` —
overwriting the `.mdt` extension, so segment **N is the program-header index**,
not a compression part number [F].

### 3.2 The hash segment — why `.b00`/`.b01` are not code

`mdt_loader.h:9-10` [F]:

```c
#define QCOM_MDT_TYPE_MASK  (7 << 24)
#define QCOM_MDT_TYPE_HASH  (2 << 24)
```

`mdt_phdr_loadable()` in `drivers/soc/qcom/mdt_loader.c` skips any program
header where `(p_flags & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH` [F]. So
`p_flags` bits 24–26 are a **segment type**, not protection flags, and a hash
segment is carried in the file set but **never loaded into firmware memory**
[F]. This is public prior art — hardened upstream by LKML `[PATCH v2] soc: qcom:
mdt_loader: Drop PT_LOAD check on hash segment` (2021-08) — so it is **cited,
not claimed** as a finding.

### 3.3 Monolithic images — 6 files, and a trap

`devcfg.img` 57,344 B, `hyp.img` 491,520 B, `keymaster.img` 262,144 B,
`tz.img` 3,190,784 B, plus **`cmnlib.img` 397,312 B and `cmnlib64.img`
516,096 B** [F].

`cmnlib` and `cmnlib64` therefore ship **both** forms — a split set *and* a
monolithic image. They are not sums of each other [F]:

| family | `.img` | Σ(`.b00`..`.b07`) | `.img − Σ` |
|---|---:|---:|---:|
| `cmnlib` | 397,312 | 390,798 | **+6,514** |
| `cmnlib64` | 516,096 | 504,542 | **+11,554** |

**A census that sums the split segments to predict the `.img` size is wrong by
6,514 B and 11,554 B respectively** — the `.img` is a separately-built
artifact, not a concatenation [F, I]. This mirrors the `fpctzapp` overshoot
recorded in `research/soc/Qualcomm-SM4375-Snapdragon-4-Gen-1-gpu.md`.

### 3.4 Where the bytes actually are

| family | bytes | share |
|---|---:|---:|
| `tz` (the TEE core) | 3,190,784 | 32.5% |
| `smplap64` | 1,774,668 | 18.1% |
| `smplap32` | 1,699,180 | 17.3% |
| `cmnlib64` | 1,041,022 | 10.6% |
| `cmnlib` | 808,338 | 8.2% |
| `hyp` | 491,520 | 5.0% |
| `keymaster` | 262,144 | 2.7% |
| `widevine` | 173,244 | 1.8% |
| `hdcp2p2` | 142,584 | 1.5% |
| `soter64` | 77,950 | 0.8% |
| `devcfg` | 57,344 | 0.6% |
| `hdcp1` | 55,933 | 0.6% |
| `hdcpsrm` | 43,551 | 0.4% |

[F] **`smplap32` + `smplap64` are 3,473,848 B = 35.4% of the family — more than
the `tz.img` itself (32.5%).** These are Qualcomm's SMPLAP trustlets (licence /
feature-gate services), not the TEE kernel. A study of "the TrustZone firmware"
that stops at `tz.img` covers under a third of the bytes [F, I].

## 4. Why exactly 24 of 83 files differ between the two "MSM8998" phones

`OnePlus_7` and `OnePlus_7T` share 83 filenames; 59 are byte-identical and 24
differ. The boundary is not arbitrary — it falls **exactly on the metadata
boundary** [F]:

| kind | identical | differing |
|---|---:|---:|
| `.b00` (ELF header) | **9** | 0 |
| `.b02`–`.b07` (code) | **50** | 0 |
| `.b01` (program headers) | 0 | **9** |
| `.mdt` (header container) | 0 | **9** |
| monolithic `.img` | 0 | **6** |

[F] `any b00 differing? []` · `any b02+ differing? []` · `any mdt identical? []` ·
`any img identical? []`.

So **every code segment and every ELF header is shared; every signed envelope
and every monolithic image is not.** That is consistent with the same code
being re-signed per build (`.mdt` carries the hash/signature material, and the
`.b01` program-header table carries segment metadata that includes per-build
addresses/sizes) [I]. It also explains the asymmetry: `OnePlus_7` matches
`OnePlus_7_Pro` on **83 of 83** files (identical build), while it matches
`OnePlus_7T` on 59 of 83 — so the 7/7T difference is a *build* difference, not
a *hardware* difference [H].

## 5. The fleet-wide violation: `mdt == b00 + b01` fails on 190 of 399

This device obeys `mdt == b00 + b01` on all 9 families. Fleet-wide it does not
[F]:

```
testable .mdt files (device has .mdt + .b00 + .b01):  399
  mdt == b00 + b01 (clean):                            209
  violated:                                            190
devices testable:  49
  clean:           27
  violating:       22
```

The failure mode is perfectly consistent [F]: **in 190 of 190 violations,
`.b01 > .mdt`** — the arithmetic delta is always negative. Examples:

| device | family | `.mdt` | `.b00` | `.b01` | delta |
|---|---|---:|---:|---:|---:|
| Nord_CE4 | `smplap64` | 4,752 | 568 | 372,296 | −368,112 |
| Nord_CE4 | `hdcp2p2` | 4,752 | 568 | 116,330 | −112,146 |
| Nord_CE4 | `featenabler` | 11,800 | 568 | 56,288 | −45,056 |
| Nord_CE4 | `loadalgota64` | 4,752 | 568 | 49,212 | −45,028 |

[F] On those devices `.b01` is one to two orders of magnitude larger than the
`.mdt`, i.e. **`.b01` does not mean "second ELF chunk" there.** Two
possibilities I did not resolve: the newer `.mdt` is a *minimal* header whose
payload was moved wholesale into `.b01` (a layout change), or `.b01` there is a
different object entirely [H, OPEN].

**Practical consequence for this repo:** any tooling that reconstructs an image
as `mdt + b01`, or that treats `.b01` as a fixed-size trailer, or that infers a
segment count from `.mdt` size, is **wrong for 22 of 49 tz devices**. The
`mdt − b01 == b00` identity that makes this device tractable is a
*generation-specific* property, not a law [F, I].

### 5.1 A related negative: `.b00` size is a function of the trustlet, not a constant

An earlier note in this lab's work stream recorded that every `*_zap.b00` is
exactly 148 B. That remains true, but it is a **`gpu`-family** fact and does
not transfer to the tz family [F]:

```
zap .b00 rows fleet-wide: 42, all blob_family == "gpu"
  sizes: 148 B x22, 308 B x17, 512 B x3
  names: a610_zap.b00, a615_zap.b00, a660_zap.b00, a740_zap.b00,
         egtzappf.b00, fpctzapp.b00
tz-family .b00 rows: 419 — contains ZERO zap files
```

Within the **tz** family the 419 `.b00` rows span eight distinct sizes [F]:

```
568 B x188   512 B x154   308 B x41   180 B x11
212 B x9     244 B x7     400 B x7    340 B x2
```

**No tz `.b00` row is 148 B** — 0 of 419 [F]. So `.b00` size tracks the
trustlet's header/segment count, and the 148 B constant is a property of the
GPU zap set specifically, not of `.b00` files in general. Anything that
treats 148 B as a global invariant would silently mis-size every tz trustlet.

## 6. Honest negatives

1. **The mislabel is prior art.** `research/soc/per-soc-method-plans.md:74`
   documents it; #2018 proves the GPU half. I supply the tz half and claim no
   credit for the discovery [F].
2. **The split grammar, the `b%02d` naming rule, and the hash-segment
   exclusion are all public** (`NerdTIV/QDig`, `bkerler/qc_modem_tools`,
   `mdt_loader.c`, LKML 2021-08). Cited, not claimed [F].
3. **I read no payload bytes.** Every size and md5 is the DB value. Whether
   `.b00` really is the ELF header and `.b01` the phdr table is inferred from
   the arithmetic (`mdt − b01 == b00`, `mdt == b00 + b01`) plus `mdt_loader.c`
   semantics — it is **not** verified by parsing a file [I, N].
4. **I did not determine why 22 devices violate the split law** — I recorded
   the failure mode and its perfect consistency, not its cause [OPEN].
5. **Why `cmnlib.img` exceeds its own segments by 6,514 B is unexplained** [OPEN].
6. **The `tz` family is NOT structurally absent here**, unlike `Galaxy_A21S`
   (#1012). The 83 rows are a complete-looking set, but I did not verify
   against a public OTA file list that this is the *entire* TrustZone set the
   device ships — a stock `vendor`/`tz` partition walk would be needed [N].
7. **Whether the 7/7T code-identity (§4) extends to non-tz families is
   untested here** — #2018 established it for `gpu` [N].
8. **`OnePlus_7` has no tz rows in any other family label**, so this note
   covers 100% of the device's matrix tz content by construction; a device
   whose TEE files were filed under `other` would be invisible to this method [N].

## 7. RULE 0 record (2026-11-20)

Queries, in my SEARCH and DELTA comments: `Qualcomm TrustZone QTEE tz.img
structure`, `qsee trusted application mdt b00 b01 b02 format`,
`OnePlus 7 guacamoleb SM8150 chemport`, `Qualcomm mdt b00 b01 b02 segment hash
segment format split firmware`, `OnePlus 7 guacamoleb trustzone tz.img qualcomm`,
`QCOM_MDT_TYPE_HASH p_flags bits 24 segment type mdt loader`. GitHub code
search excluded `adineo-cmd/*`. Result: format documentation is abundant and
public; **no prior analysis of this device's tz family exists** in any source
found.

## Reproduce

```sh
# 83 rows, 9 families, byte accounting
python3 -I -c "
import csv
from collections import defaultdict
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
t=[x for x in r if x['device']=='OnePlus_7' and x['blob_family']=='tz']
print('rows',len(t),'bytes',sum(int(x['size_bytes']) for x in t))
d={x['filename']:int(x['size_bytes']) for x in t}
for b in ['cmnlib','hdcp1','smplap64']:
    print(b, d[b+'.b00'], d[b+'.b01'], d[b+'.mdt'], d[b+'.mdt']-d[b+'.b01']==d[b+'.b00'])"

# the 2x2 proof
python3 -I -c "
import csv
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
tz=[x for x in r if x['filename']=='tz.img']
for s in ['OnePlus_7','OnePlus_7T']:
    m=[y for y in tz if y['device']==s][0]['md5_db']
    print(s,[y['device'] for y in tz if y['md5_db']==m])"

# the fleet-wide split-law violation
python3 -I -c "
import csv
from collections import defaultdict
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
by=defaultdict(dict)
for x in r:
    if x['blob_family']=='tz': by[x['device']][x['filename']]=int(x['size_bytes'])
ok=bad=b1big=0
for dev,fs in by.items():
    for k in fs:
        if k.endswith('.mdt'):
            p=k[:-4]; a=fs.get(p+'.b00'); b=fs.get(p+'.b01')
            if a and b:
                if fs[k]==a+b: ok+=1
                else:
                    bad+=1
                    if b>fs[k]: b1big+=1
print('ok',ok,'violated',bad,'b01>mdt among violations',b1big)"
```

All kernel references from `torvalds/linux` master, 2026-11-20.

## What would upgrade this finding

1. Parse one `.mdt` + `.b00` + `.b01` triple to confirm the header/phdr
   hypothesis, and diff a violating trio (`Nord_CE4/smplap64`) against a clean
   one to explain §5.
2. Fetch `OnePlus_7` stock `tz`/`vendor` partitions and compare the file list
   against these 83 rows to test completeness (§6.6).
3. Check whether the 59/24 identity split (§4) holds for `modem`, `adsp` and
   `wlan` on the same two devices — if it does, "code shared, envelope
   re-signed" generalises.

Not legal advice; no proprietary payload accessed or committed. All facts are
DB metadata plus cited upstream sources and the lab's own prior notes.
