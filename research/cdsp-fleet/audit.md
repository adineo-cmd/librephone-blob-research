# CDSP fleet + container audit — issue #595

Adversarial audit, 2026-11-20. Auditor did not read, import or run the
authors' modules to reproduce any headline number; every number below was
recomputed from the CSV and the raw blobs with throwaway scripts in
`/tmp/opencode/audit-tmp/`. One documented exception: the shipped test suite
and `cdsp_probe.py --brief` were executed as a black box, once, purely to test
the delivered artefact (see "The shipped parser" below); no author code was
imported to derive a census or container figure. No file under audit was
modified.

Evidence classes: `[F]` measured by the auditor, `[I]` inference, `[H]`
hypothesis, `[N]` honest negative.

## Verdict table

| # | Claim | Verdict | Auditor evidence |
|---|---|---|---|
| 1 | 23 canonical = 33 raw minus 10 aliases | **UPHELD** | 33/10/23 reproduced; alias set is a strict subset of canonical; 0 duplicate (device,canonical) pairs |
| 2 | `cdsp.mdt` reaches 64/64, not 63 | **QUALIFIED** | arithmetic `[F]` 64/64 correct; but "100%" is 29.2% of the CSV slice, and OnePlus_6's rows carry no `db_path` |
| 3 | 51.8% of instances (492/950) non-unique | **QUALIFIED** | `[F]` 492/950 reproduced; 60 of the 492 are the 2-value `cdspr.jsn`; excluding it the rate is 48.5% |
| 4 | `cdsp.mdt` no 30-device cluster; max 2; 54/64 unique | **UPHELD** | `[F]` max cluster 2 devices, 54 unique, 5 clusters of 2 |
| 5 | sibling `.bNN` iff `p_filesz>0`, size == `p_filesz`, 13/13 | **UPHELD (rule), QUALIFIED (novelty)** | `[F]` 10/10 + 3/3 on this image, 12/12 on a 2nd device. But `mdt_loader.c` already enforces it — not new |
| 6 | `p_filesz==0` segments {7,10,12} have no sibling | **UPHELD** | `[F]` exactly {7,10,12}, no sibling for any |
| 7 | p_flags bit layout 27/26-24/23-21/2-0 | **UPHELD** | `[F]` coreboot `MI_PBT_FLAG_ACCESS_TYPE_MASK=0x00E00000`, shift `0x15`=21 — matches author exactly |
| 8 | Zero-fill segments not tagged ZI (access 2 never appears) | **QUALIFIED** | `[F]` access 2 absent in 11426 words and in 319 firmware-only words; but 97.2% of the corpus is userspace `.so`, not firmware |
| 9 | Segments 5, 8, 11 are code-like `[I]` | **QUALIFIED (overclaimed)** | `[F]` classifier has demonstrable false positives: u32 index table, PCM audio, `0xFF` fill, ASCII/base64 all classify "code-like" |
| 10 | Segment 1 contains DER certificates | **UPHELD** | `[F]` 3 valid DER SEQUENCEs at 1048/2085/3180, chain lengths 1037/1095/1089, X.509 version INTEGER=2 |
| 11 | No second device's cdsp split image exists on disk | **REFUTED** | `[F]` 10 `OnePlus_6` CSV rows name `enchilada modem.img FAT IMAGE` as their source; the bytes are in `enchilada.zip`, md5-identical |
| 12 | `e_flags` 0x066 = Hexagon V66 | **UPHELD** | `[F]` QEMU `linux-user/hexagon/elfload.c` maps 0x66→"v66" |

## Per-claim detail

### Claim 1 — 23 canonical files — UPHELD

```
$ python3 -I recompute_census.py
cdsp rows: 950
-- distinct raw file strings: 33
-- alias raw strings: 10
   ALIAS <modem-fat:IMAGE/cdsp.b00> 1
   ... (10 total, all count 1)
-- distinct canonical file names: 23
```

`[F]` The alias-stripping is legitimate, not a fudge, and I tried to break it
three ways:

```
$ python3 -I attack_alias.py
  alias rows: 10 devices: {'OnePlus_6'}
  all from OnePlus_6: True
  OnePlus_6 total rows: 10  any canonical (non-alias): False
  -> intersection: alias names are a SUBSET of canonical names => True
  (device,canonical) duplicates: 0
```

The rule is "relabel, don't delete": OnePlus_6 contributes its 10 instances
through the alias form only. Had the aliases been *dropped*, the census would
read 940 instances / 63 devices; the author keeps them and gets 950/64. That
is the correct choice and it is not double-counting, because no device has two
rows for the same canonical file.

### Claim 2 — `cdsp.mdt` reaches 64/64 — QUALIFIED

```
$ python3 -I recompute_census.py
   cdsp.mdt             64
-- distinct devices: 64
$ python3 -I decompose.py
  devices in CSV slice: 219; with any cdsp row: 64
  '64/64 = 100%' is 100% of the 64 in-family devices, i.e. 29.2% of the slice
  devices with cdsp rows but NO cdsp.mdt: set()
```

`[F]` The 63-vs-64 correction is right and the mechanism is exactly as stated
(OnePlus_6 has only `<modem-fat:IMAGE/cdsp.mdt>`). But the headline "100%"
invites a reading the data cannot support: it is 100% of the 64 devices that
happen to have cdsp rows, i.e. 29.2% of the 219 devices in the slice. The doc
does say "reach" not "fleet coverage", and §G records the slice limit, so this
is a framing defect, not an arithmetic one. Compounding it: OnePlus_6 is the
one device whose rows carry no `db_path`, so the device that *creates* the 64
is the least-identified device in the set.

### Claim 3 — 51.8% non-unique — QUALIFIED

```
$ python3 -I recompute_census.py
-- distinct md5: 586
-- shared instances: 492 unique instances: 458 total: 950
-- sharing rate instances: 51.8%
$ python3 -I decompose.py
  all instances            : 492/950 = 51.8%
  excluding cdspr.jsn      : 432/890 = 48.5%
  cdsp.mdt only            :  10/ 64 = 15.6%
```

`[F]` The arithmetic is exact. Two framing problems survive attack:

1. **"Non-unique content" conflates two different things.** I checked whether
   any device duplicates an md5 across its own files — zero such groups
   (`attack_denominator.py`: "total within-device duplicate md5 groups: 0").
   So the metric is purely *cross-device* md5 collision. Calling it "non-unique
   content" without the qualifier invites a reader to think a device ships
   redundant segments.
2. **`cdspr.jsn` carries the number.** 60 of the 492 shared instances are a
   two-value file (30+30). Excluding it the rate falls to 48.5%, and for the
   `.mdt` itself the rate is 15.6%. The doc does break this out per file, so
   the disclosure exists — but the headline is the most flattering number.

### Claim 4 — no 30-device `cdsp.mdt` cluster — UPHELD

```
$ python3 -I recompute_census.py
-- cdsp.mdt instances: 64 distinct md5: 59
-- cdsp.mdt md5 multiplicity: {1: 54, 2: 5}
-- cdsp.mdt max cluster (devices sharing one md5): 2
-- cdsp.mdt unique instances (md5 on 1 device): 54
$ python3 -I recompute_census.py   # cdspr.jsn for contrast
   f2bd80d5... 30 instances, 30 devices
   49003ffc... 30 instances, 30 devices
```

`[F]` This is the strongest corrective result in the two documents. The
expected "big shared `.mdt`" does not exist: 54 of 64 `.mdt` instances are
unique, the largest shared group is 2 devices, and the only 30-device clusters
belong to `cdspr.jsn`. The doc correctly redirects the leverage from shared
content to device reach.

### Claim 5 — sibling rule, 13/13 — UPHELD, novelty QUALIFIED

```
$ python3 -I parse_mdt.py
-- siblings present on disk: {0: 468, 1: 7192, 2: 235420, 3: 105980, 4: 1076,
   5: 2803308, 6: 83426, 8: 830592, 9: 2800, 11: 59156}
   seg 0..12 ... equal=True for all filesz>0
-- exact-size matches: 10 of 10
-- b00 == mdt[0:468]: True
-- b01 == mdt[468:7660]: True
-- b00+b01 == mdt: True
```

`[F]` The rule holds exactly. I also confirmed the `.bNN` numbering is
**index-based, not a counter over non-empty segments**:

```
$ python3 -I attack_minimal_fp.py
  phdr indices with filesz>0: [0,1,2,3,4,5,6,8,9,11]
  files on disk:              [0,1,2,3,4,5,6,8,9,11]
  -> INDEX-BASED confirmed: True
```

That matters because a counter-based reader would expect `b07` where the file
is `b08`. The author's table uses phdr index and is right.

**Novelty is the problem.** `drivers/soc/qcom/mdt_loader.c` in mainline
already encodes this rule verbatim:

```c
static ssize_t mdt_load_split_segment(...)
{
    sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment);
    ret = request_firmware_into_buf(&seg_fw, seg_name, dev, ptr, phdr->p_filesz);
    ...
    if (seg_fw->size != phdr->p_filesz) {
        dev_err(dev, "failed to load segment %d from truncated file %s\n", ...);
```

and `qcom_mdt_bins_are_split()` skips `!phdrs[i].p_filesz` with the comment
"The size of the MDT file is not padded to include any zero-sized segments".
The author's "rule" is a re-derivation of kernel behaviour, correctly
attributed elsewhere in the doc but not credited as prior art for this
specific finding. It is a valid *verification*, not a discovery.

### Claim 6 — zero-fill segments have no sibling — UPHELD

```
$ python3 -I parse_mdt.py
-- zero-filesz idx: [7, 10, 12]
   seg  7: filesz=0 sibling=absent ok=True
   seg 10: filesz=0 sibling=absent ok=True
   seg 12: filesz=0 sibling=absent ok=True
```

`[F]` Exact. Note the author himself records the counter-example in §7
(`larry` `evass`/`vpu20_1v` ship zero-byte `.bNN` files, and `vpu20_1v` has no
`b00` at all), so the "iff" is correctly scoped to this image rather than
stated as universal. That is good discipline.

### Claim 7 — p_flags layout — UPHELD (and I was wrong first, then corrected)

My first pass guessed coreboot used bits 20-22 for access and produced a
"one-bit disagreement". I then fetched the actual source. coreboot
`util/qualcomm/mbn_tools.py` states:

```
MI_PBT_FLAG_SEGMENT_TYPE_MASK = 0x07000000   shift 0x18 (24)
MI_PBT_FLAG_ACCESS_TYPE_MASK  = 0x00E00000   shift 0x15 (21)
MI_PBT_FLAG_POOL_INDEX_MASK   = 0x08000000   shift 0x1B (27)
MI_PBT_FLAG_PAGE_MODE_MASK    = 0x00100000   shift 0x14 (20)
```

`[F]` This is the author's layout **exactly**, including bit 20 as page mode
and bit 27 as pool/relocatable. mainline `mdt_loader.h` independently confirms
the two bits the kernel cares about:

```c
#define QCOM_MDT_TYPE_MASK  (7 << 24)
#define QCOM_MDT_TYPE_HASH  (2 << 24)
#define QCOM_MDT_RELOCATABLE BIT(27)
```

So claim 7 is upheld, and my attempted refutation failed. Recording the failed
attack explicitly: the layout is not merely asserted, it is double-sourced.

```
$ python3 -I parse_mdt.py
   seg  0 0x07000000 segtype=7 access=0 bit27=0
   seg  1 0x02200000 segtype=2 access=1 bit27=0
   seg  2 0x08000005 segtype=0 access=0 bit27=1
```

### Claim 8 — no ZI tagging — QUALIFIED

```
$ python3 -I corpus_pflags.py
total p_flags words: 11426
distinct low-3 R/W/X: [0, 4, 5, 6, 7]
segtype values: [0, 1, 2, 3, 4, 5, 7]
access values: [0, 1, 3]
bit27 set: 724 of 11426
0x07000000 count: 753   0x02200000 count: 753
```

`[F]` Every corpus number reproduces exactly, including the 753/753 PHDR/HASH
symmetry. The finding itself is sound. The weakness is the **evidence base**:

```
$ python3 -I attack_margin_bias.py
  file count by class: {'firmware dir': 22, '.mdt firmware': 32,
                        'userspace .so': 914, 'other': 724}
  p_flags words by class: {'.mdt firmware': 319, 'firmware dir': 215,
                           'userspace .so': 7976, 'other': 2916}
  -> fraction of p_flags words from actual .mdt firmware: 2.8%
```

`[F]` "access value 2 never appears" is a statement about a corpus that is
97.2% userspace shared objects. I re-ran restricted to `.mdt` only and the
conclusion still holds (319 words, access ∈ {0,1}, and all 30 zero-fill
segments across the `.mdt` corpus carry access 0) — so the claim survives, but
the doc should say the finding is upheld on firmware alone, because as written
a reader cannot tell whether the ZI evidence comes from DSP firmware or from
`libc++`.

### Claim 9 — segments 5, 8, 11 "code-like" — QUALIFIED, overclaimed

This is the weakest part of `container.md`. The author labels the call `[I]`
and devotes a paragraph to its softness, which is honest. But the label
understates how weak the test actually is.

The implemented classifier (`cdsp_container_probe.py:387-411`) is:

```python
if par["p10"] < 0.05 and par["p00"] < 0.25:
    return ("code-like (Hexagon packet statistics)", ...)
```

I replicated the full chain including its guard clauses and then fed it data
that is definitively not Hexagon code:

```
$ python3 -I attack_fullchain.py
  seg 5 -> code-like    pr=0.103 H=5.18 words=700827
  seg 8 -> code-like    pr=0.052 H=6.76 words=207648
  seg11 -> code-like    pr=0.036 H=6.49 words=14789

  u32 in [0x4000,0x5FFF] (index tbl) pr=0.000 H=4.60 n=400000 p10=0.0000 p00=0.000 -> code-like
  16-bit PCM audio (u32 packed)      pr=0.061 H=7.22 n=300000 p10=0.0000 p00=0.000 -> code-like
  u32 affine 0x4000+                 pr=0.000 H=4.40 n=400000 p10=0.0000 p00=0.000 -> code-like
```

and with the simpler threshold form:

```
$ python3 -I attack_codelike3.py
  ASCII english            p00=0.222 p10=0.0000 H=1.52 cls=3  -> CODE-LIKE
  base64(seg8)             p00=0.084 p10=0.0000 H=2.15 cls=6  -> CODE-LIKE
  0xFF*2MB                 p00=0.000 p10=0.0000 H=0.00 cls=1  -> CODE-LIKE
```

`[F]` A 2 MB run of `0xFF` passes. An index table with every word in
`[0x4000,0x5FFF]` passes. Base64 text passes. The rule reduces to "bits 15:14
are not 00 and not 10" — it accepts anything where those two bits are
constantly `01` or `11`, which is exactly what a monotone 16-bit-leaning table
produces.

Why the three real segments are still *probably* code: their `p00` values
(0.108 / 0.230 / 0.171) are nowhere near 0 or 1, they use all 16 iClasses with
entropy 2.84–3.68 bits, and segment 5's gap>4 rate has a clean minimum at byte
offset 0 (2.682% vs 5.5–6.6% at +1/+2/+3) which does indicate word structure.
So the conclusion is defensible. The *test as written* is not falsifiable in
the direction that matters, and the doc's claim that "packet statistics on
obfuscated or compressed code could imitate these marginals" understates it:
compressed data mostly does **not** imitate them (DEFLATE/gzip fail), but
plain lookup tables and PCM do.

Also note the razor margin on the weakest call:

```
$ python3 -I final_attack.py
  seg8 p00 = 0.230082; cutoff 0.25; headroom = 0.019918 (8.0% below cutoff)
```

`[F]` Segment 8 is 8% below the data/code boundary. The doc already calls
segment 8 "the weakest of the three" and keeps it at `[I]`. That is the right
call; the summary line "code_like=3" nevertheless propagates an unqualified
count.

There is also a **doc-vs-code drift**: `container.md:295` states the rule as
"`p10` is at or below ~0.03", but the code uses `< 0.05`. Both pass for these
segments, but the documentation does not describe the program that produced it.

### Claim 10 — DER certificates in segment 1 — UPHELD

```
$ python3 -I der_and_ota.py
  off=1048 tag=0x30 len_field=1033 total=1037 end=2085 fits=True
      tbs len=705 version INTEGER=2
  off=2085 tag=0x30 len_field=1091 total=1095 end=3180 fits=True
  off=3180 tag=0x30 len_field=1085 total=1089 end=4269 fits=True
  match: True  (seg1[1048:1064] == 30820409308202c1a003020102020101)

$ python3 -I der_and_ota.py   # hash-record region
  224 records; distinct: 128  all-zero: 6
  sample at 24+32*8: 5c702af1ec8d77773becc99ef659b0ab3ffca731a73a173b1be8514dc65e79ba
```

`[F]` Three contiguous DER SEQUENCEs, each parsing to a well-formed TBSCertificate
with X.509 version INTEGER=2, laid end to end (end of one == start of next).
The author's quoted "lengths 1037/1095/1089" are total object lengths (4-byte
header + content), which is the correct convention for a contiguous chain.
224 32-byte records with 128 distinct and 6 all-zero also reproduces, and
segment 1 is exactly `24 + 224*32 = 7192` bytes, i.e. the record table fills
the segment with no slack. The author marks the record *semantics* `[I]` and
that restraint is correct — but the "224 records" geometry is `[F]`.

### Claim 11 — no second device's cdsp image — REFUTED

This is the finding that breaks the work.

`container.md:354` asserts: *"There is no second device's cdsp split image on
disk. Under the data root there are 50 `.mdt` files and exactly one cdsp
family."* That is true only if "on disk" means "as a `*.mdt` file". It is
false for the data root, because `enchilada.zip` contains a full OTA whose
`modem` partition is a FAT16 firmware volume holding the complete OnePlus 6
CDSP set:

```
$ python3 -I modem_scan.py
found modem partition
ops: 58
modem.img written: 117723136
  b'image_cdsp': 0     b'.mdt': 0     b'cdsp': 64     b'CDSP': 451

$ python3 -I fat_walk.py
root: [..., ('CDSP.B00', 32), ('CDSP.B01', 32), ..., ('CDSP.MDT', 32), ...]

$ python3 -I extract_enchilada_cdsp.py
  CDSPR.JSN    decl=      403 got=      403 md5=f2bd80d5f0b19b5b0d36d28383948149
  CDSP.B00     decl=      436 got=      436 md5=138d1b26f2a655d08f17aa54fe8f717c
  CDSP.B01     decl=     6824 got=     6824 md5=901bf8a45f3a3d2343700b562efc36e7
  CDSP.B02     decl=   197840 got=   197840 md5=b7af2a81a8dfb89eba8bcc0d75b6f5d5
  CDSP.B03     decl=   104160 got=   104160 md5=e3d1ed53005aaaadd49030903280ea17
  CDSP.B04     decl=      980 got=      980 md5=5c112edb365f4e990ded9db7554a4073
  CDSP.B05     decl=  2402948 got=  2402948 md5=c3b3d21e77a2f660d42d6d01d940758f
  CDSP.B06     decl=    31596 got=    31596 md5=060b159bd477526ab17b0799330433dd
  CDSP.B08     decl=    69800 got=    69800 md5=20a48657771ff2ea51825d2961114c44
  CDSP.B10     decl=    58900 got=    58900 md5=c69353c89190d37201dc63ba73f3875e
  CDSP.MDT     decl=     7260 got=     7260 md5=d571f8ff03b0bd25c031f1e73d16b575
```

Every one of those 11 md5s is **byte-identical to the CSV `OnePlus_6` rows**
that the census in the same directory treats as the alias-form device:

```
$ python3 -I validate_second_device.py
  cdsp.b00  csv_size=436     actual=436     md5_eq=True
  cdsp.b01  csv_size=6824    actual=6824    md5_eq=True
  cdsp.b02  csv_size=197840  actual=197840  md5_eq=True
  cdsp.b03  csv_size=104160  actual=104160  md5_eq=True
  cdsp.b04  csv_size=980     actual=980     md5_eq=True
  cdsp.b05  csv_size=2402948 actual=2402948 md5_eq=True
  cdsp.b06  csv_size=31596   actual=31596   md5_eq=True
  cdsp.b08  csv_size=69800   actual=69800   md5_eq=True
  cdsp.b10  csv_size=58900   actual=58900   md5_eq=True
  cdsp.mdt  csv_size=7260    actual=7260    md5_eq=True
```

The strongest form of this refutation is not the zip at all — it is the CSV
that `census.md` is built on. All 10 OnePlus_6 cdsp rows carry a `notes` field
that names the enchilada modem FAT as their provenance:

```
$ python3 -I -c "import csv; [print(r['file'],'|',r['notes']) for r in csv.DictReader(open('data/fleet/devices-001-222.csv')) if r['family']=='cdsp' and r['device']=='OnePlus_6']"
<modem-fat:IMAGE/cdsp.b00> | md5_db=138d1b26f2a655d08f17aa54fe8f717c; source=LineageOS-22.2-20261111-nightly-enchilada modem.img FAT IMAGE dir
...
<modem-fat:IMAGE/cdsp.mdt> | md5_db=d571f8ff03b0bd25c031f1e73d16b575; source=LineageOS-22.2-20261111-nightly-enchilada modem.img FAT IMAGE dir
-- distinct source values across those 10 rows: 1
   {'LineageOS-22.2-20261111-nightly-enchilada modem.img FAT IMAGE dir'}
```

`[F]` So `census.md` — the sibling document in the same directory — derives
its 64th device *from* the enchilada modem FAT, while `container.md:357`
states "No `cdsp.mdt` exists for `larry` or `enchilada`" and `:361` states that
enchilada ships "only **userspace** cdsp artifacts … No firmware payload."
The two documents contradict each other on the identity of the same ten rows.

This has four consequences:

1. **The "one cdsp family" premise collapses.** There are two, and the second
   is a different SoC (SDM845, `e_flags=0x65`) and a different phdr count
   (12 vs 13). It is also not a new discovery: the census had already
   recorded its provenance in the CSV.
2. **The §5 rule gets a genuine second-device test the author declared
   impossible.** It passes: `9/9` exact-size siblings for `p_filesz>0`, `3/3`
   zero-fill segments correctly absent, `b00+b01 == mdt` prefix, sum of
   `p_filesz` 2,873,484 == sum of `B`-file sizes 2,873,484. So the rule is
   *stronger* than claimed, but for a reason the author denied.
3. **The repo already knew.** `research/fleet/oneplus6-partition-map.md:28`
   records the OP6 `modem.img` FAT `IMAGE/` tree containing `cdsp.b00-b10`,
   and `workorders/inbox/STATUS-DESKTOP.md:141` records the same. The author
   wrote "no second device exists" in a repo that documents the opposite one
   directory away. This is a repo-internal consistency failure, not merely a
   missed data source.
4. **The `.mdt` file census is case-sensitive and therefore wrong.** `[F]`
   `container.md:354-358` counts "50 `.mdt` files" and an `EM_HEXAGON` count of
   12. Both come from a lowercase glob. The data root holds **82** files whose
   name ends `.mdt` case-insensitively (32 are `.MDT`):

   ```
   $ find . -name '*.mdt' | wc -l      -> 50
   $ find . -iname '*.mdt' | wc -l     -> 82
   $ find . -name '*.MDT' | wc -l      -> 32

   $ python3 -I -c "...walk, any-case .mdt, e_machine histogram..."
   lowercase .mdt only: {'EM_HEXAGON': 12, 'EM_AARCH64': 18, 'EM_ARM': 14, 'EM_XTENSA': 6}
   any-case .mdt      : {'EM_HEXAGON': 16, 'EM_AARCH64': 31, 'EM_ARM': 27, 'EM_XTENSA': 8}
   ```

   The 4 extra Hexagon hits are the FAT 8.3 short-name copies of
   `image_cdsp/npu/slpi/adsp.mdt` (`PCAFUI~2_S7THG7~2.MDT` etc.). `[F]` The
   short-name directory and the long-name directory are byte-identical: all 32
   md5s match pairwise, 654 files each. So the *content* count of 12 distinct
   Hexagon images is right by luck, not by construction — the enumeration
   silently omitted a whole 654-file directory tree and would have undercounted
   had that tree held anything the LFN tree did not.

The corpus count is therefore `12 -> 13`, not the stated 12.

### Claim 12 — `e_flags` 0x066 = V66 — UPHELD

```
$ python3 -I mdt_census.py
EM_HEXAGON  enchilada/tree_firmware/a630_zap.mdt        e_flags 0x000003
EM_HEXAGON  second-device/instantnoodle/.../image_cdsp.mdt  e_flags 0x000066
EM_HEXAGON  second-device/instantnoodle/.../image_slpi.mdt  e_flags 0x000066
EM_HEXAGON  second-device/instantnoodle/.../image_adsp.mdt  e_flags 0x000066
EM_HEXAGON  second-device/instantnoodle/.../image_npu.mdt   e_flags 0x000066
```

`[F]` QEMU `linux-user/hexagon/elfload.c` maps `0x66 -> "v66"`; LLVM
`HexagonBaseInfo.h` / `EF_HEXAGON_ISA_V66` agrees. The `e_flags` split
(`0x066` on the four DSP images, `0x003` on zap/ipa) reproduces exactly, and
the newly-found enchilada CDSP is `0x065` = V65, i.e. the same nibble scheme
on a third device. The author's `[I]` note that `0x003` = V4 is an inference
not backed by a citation in the doc, but it is correct.

## Prior-art re-attack

Date of all queries: **2026-11-20**. Engine: DuckDuckGo via `websearch`.

| # | Exact query string | What it returned | Overlap with the work |
|---|---|---|---|
| 1 | `Qualcomm split mdt container format program header sibling segment size` | Qualcomm Hexagon ABI guide (program headers, `p_flags` permissions); `mdt_loader.c` on android.googlesource with the "In the case of split firmware the hash is found directly following the ELF header" comment; LKML "Actually use the e_phoff" | **HIGH.** Kernel source states the split model and the hash-after-header rule |
| 2 | `coreboot mbn_tools.py get_access_type p_flags bit 20 21 segment type HASH PHDR` | coreboot `util/qualcomm/mbn_tools.py`; `qtestsign/region.py` citing it; u-boot `mkmbn.py` patch | **HIGH.** The entire p_flags layout, incl. access shift 21 and ZI=2 |
| 3 | `"p_flags" qualcomm mdt 0x08000007 segment type hash phdr` | `mdt_loader.c` hash-segment detection; `qcom_common.c`; `QCOM_MDT_TYPE_MASK` usage; Motorola sm8550 tree | **HIGH.** HASH/PGDR type bits and the `0x08000007` family are standard |
| 4 | `qualcomm mbn p_flags bit 27 relocatable segment type access ZI` | coreboot mbn_tools layout block; Hex-Rays "Loading Qualcomm MBN containers" (reports relocatable, logs ISA version); `QCOM_MDT_RELOCATABLE BIT(27)` | **HIGH.** Bit 27 relocatable + ISA logging is a shipped IDA feature |
| 5 | `hexagon e_flags EF_HEXAGON_MACH_V66 0x66 V65 V68 ELF machine flags LLVM` | QEMU `elfload.c` `0x66 -> "v66"`; Qualcomm Hexagon ABI guide Table 12-1; LLVM `ELF.h`; Hexagon SDK ISA list | **HIGH.** V66 mapping is published |
| 6 | `cdsp.mdt b00 b01 parser validation qualcomm split firmware` | Qualcomm "Flash images" doc ("push adsp, cdsp, modem, wlan, ipa **pil split binaries**"); `Tecatech/qualcomm-MBN-patcher`; `mzakocs/qualcomm_baseband_scripts` | **MEDIUM.** Split-image tooling is common; no fleet-wide cdsp census found |
| 7 | `cdsp firmware cross-device census fleet qualcomm` | Kernel DT patches adding CDSP nodes; linux-firmware "update CDSP firmware for the glymur platform"; Qualcomm remoteproc docs | **LOW for census, HIGH for format.** No prior cross-device cdsp content census surfaced |
| 8 | `qualcomm modem IMAGE folder CDSP.B00 CDSP.MDT FAT partition split firmware` | XDA thread describing a FAT volume with an `image/` directory holding `modem.mdt`, `modem.b00`, `dsps.mdt`; Qualcomm "Split Modem Image FOTA Solution Guide" (`80-Pj388-39`) | **HIGH and directly adverse to claim 11.** The FAT `image/` layout holding `*.mdt`+`*.bNN` is documented prior art |

**Honest prior-art verdict.** Claims 1–10 and 12 are largely *re-derivations of
published format knowledge*: the p_flags layout is coreboot's, the sibling rule
is `mdt_loader.c`'s, V66 is QEMU's, and the FAT `image/` directory is XDA/SDK
common knowledge. What I could **not** find prior art for is the specific
deliverable here: a 64-device, 950-instance md5 census of `cdsp.*` and the
negative result that `cdsp.mdt` has no large shared cluster. That part appears
genuinely new. The problem is that the *new* part is the metadata arithmetic,
and the *format* part — presented as the headline — is a restatement.

## Defects found

| # | Sev | File:line | Defect |
|---|---|---|---|
| D1 | **High** | `container.md:354-357` | "There is no second device's cdsp split image on disk" is **false**. The 10 `OnePlus_6` cdsp rows in the sibling `census.md`'s own CSV name `LineageOS … enchilada modem.img FAT IMAGE dir` as their `source=`; the bytes are in `enchilada.zip` (`CDSP.MDT` + 10 `CDSP.Bnn`), md5-identical. Premise for the whole §7 honest-negative is wrong. |
| D2 | **High** | `container.md:368-397` | `corpus=12/12` (and the Summary line, `:441`) undercounts by one. A 13th Hexagon split image (enchilada CDSP, V65, 12 phdrs) is extractable from the data root. |
| D13 | **High** | `container.md:354-361` vs `census.md:3,246` | The two documents in the same directory contradict each other about the same ten rows. `census.md` says its 64th device comes from the enchilada modem FAT; `container.md:357,361` says enchilada has no `cdsp.mdt` and "No firmware payload". One of the two must be wrong; both are presented `[F]`/`[N]`. |
| D14 | **Medium** | `container.md:354-358` | The `.mdt` enumeration is case-sensitive. `find -name '*.mdt'` gives 50 files / 12 Hexagon; `find -iname '*.mdt'` gives 82 / 16. A whole 654-file `modem-fat` directory of `.MDT`/`.Bnn` short names is never visited. The Hexagon *content* count of 12 survives only because that tree duplicates the LFN tree byte-for-byte (32/32 md5 pairs). |
| D15 | **High** | `implementations/cdsp-fleet/cdsp_probe.py:461-471` | `sibling_path()` hardcodes a lowercase `"b%02d"` while preserving the stem's case, so it looks for `CDSP.b00` beside a `CDSP.MDT`. On the real uppercase enchilada image it reports `siblings=0/9 VIOLATIONS:9` against an image that is actually valid — verified: the identical bytes renamed to lowercase give `siblings=9/9 OK`. The shipped probe therefore fails on the one second-device image that matters. |
| D3 | **High** | `container.md:294-296`, `:234` | The "code-like" classifier is **not falsifiable in the direction claimed**. Replicated rule accepts a constant `0xFF` run, a u32 index table and packed PCM as "code-like". The doc's caveat ("compressed code could imitate these marginals") names the wrong adversary — compressed data fails the test; plain tables pass it. |
| D4 | **High** | `container.md:295` vs `cdsp_container_probe.py:409` | Doc/code drift: doc says `p10` "at or below ~0.03", code uses `p10 < 0.05`. The documented rule is not the rule that ran. |
| D5 | **Medium** | `container.md:173-180` | "Corpus census over 1692 ELF32 files, 11426 p_flags words" is presented as if it characterises DSP firmware; 97.2% of those words come from userspace `.so` files (7,976 of 11,426). The ZI-negative happens to survive firmware-only restriction (319 words, access ∈ {0,1}), but the doc never shows that. |
| D6 | **Medium** | `container.md:99-101`, `:387-389` | The sibling-size "rule" is presented as a finding. `drivers/soc/qcom/mdt_loader.c` implements it (`if (seg_fw->size != phdr->p_filesz)`) and `qcom_mdt_bins_are_split()` skips `!p_filesz`. Not credited as prior art in the section that states it. |
| D7 | **Medium** | `container.md:141-155` | The decoded table prints `access` for `p_filesz==0` rows as `0` (RW) and then argues ZI is "false" for them. The real point — that zero-fill is expressed by `p_filesz==0 && p_memsz>0` — is correct, but presenting RW as the "access" of a BSS segment is a category error a reader can trip over. Not a factual error; a framing one. |
| D8 | **Medium** | `census.md:11`, `:71` | "64/64 devices (100.0%)" is 100% of the 64 devices that have cdsp rows — 29.2% of the 219-device slice. The `[N]` slice note exists in §G but the headline does not carry it. |
| D9 | **Medium** | `census.md:12`, `:102-104` | "51.8% of instances are non-unique content" conflates cross-device md5 collision with content duplication. Zero within-device duplicate groups exist. Excluding the 2-value `cdspr.jsn` the rate is 48.5%; for `.mdt` it is 15.6%. |
| D10 | **Low** | `container.md:11` | Reproduction instructions omit that `enchilada.zip` must be unpacked for the second-device question; as written the run command cannot reach the counter-evidence. |
| D11 | **Low** | `census.md:29` | "smallest per-device file count 1 (Pixel_4A_5G, Pixel_5, Pixel_5A)" — correct, but these 3 devices carry only `cdsp.mdt` and still count toward the 64-device `cdsp.mdt` reach, which inflates that percentage's practical meaning. |
| D12 | **Low** | `container.md:190` | "Corpus also contains `0x00000003` = `EF_HEXAGON_MACH_V4`, so the nibble is doing real work" — the V4 mapping is asserted without a citation, unlike the V66 mapping which is `[F]`. |

## The shipped parser — `implementations/cdsp-fleet/`

The same change set also adds a probe and a 139-test suite
(`implementations/README.md` row 28). I ran the suite once:

```
$ cd implementations/cdsp-fleet && python3 -I test_cdsp_probe.py
----------------------------------------------------------------------
Ran 139 tests in 0.395s

OK
```

`[F]` The suite passes and the count is honest. That is a genuine strength:
the fixtures are synthetic, the invariants are stated as the loader states
them, and the `PT_NULL`/`p_memsz==0` exception is documented rather than
special-cased away. But running *the shipped tool* on the second-device image
exposes the case bug in D15:

```
$ python3 -I cdsp_probe.py /tmp/opencode/audit-tmp/enchilada_cdsp/CDSP.MDT --brief
CDSP.MDT  7260 B  phdr=12 load=10 bss=3 hash=1 split=yes siblings=0/9  VIOLATIONS:9

$ python3 -I cdsp_probe.py /tmp/opencode/audit-tmp/ench_lower/cdsp.mdt --brief
cdsp.mdt  7260 B  phdr=12 load=10 bss=3 hash=1 split=yes siblings=9/9  OK
```

`[F]` The same bytes, differing only in filename case, go from "9 violations"
to "OK". The cause is `sibling_path()` (`cdsp_probe.py:461-471`), which
preserves the stem's case but hardcodes a lowercase `"b%02d"`, so it seeks
`CDSP.b00` beside `CDSP.MDT`. The kernel it cites does
`sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)` on whatever name
it was handed — it inherits the caller's case. `[I]` vfat is case-insensitive,
so the kernel's lookup succeeds where the probe's `os.path.isfile` does not;
either way the probe diverges from the loader it claims to model. The probe's
single most important claim (the sibling rule) therefore fails closed on a
valid image, and no test covers it because every fixture is lowercase.

The 139 passing tests and this defect coexist because the suite tests the
*rule*, and the defect is in the *path construction* feeding the rule.

## Repo-internal consistency

- **`.jsn` handling: consistent.** `container.md:335-339` says `.jsn` files are
  PDR service-registry manifests, not split-MDT manifests, and cites
  `research/laptop/qualcomm-pil-manifest-family.md`. I verified the claim
  independently: `image_cdspr.jsn` (403 B, `f2bd80d5…`) has keys
  `sr_version` / `sr_domain` / `sr_service` only, with
  `domain=cdsp, subdomain=root_pd, qmi_instance_id=76`, and no MDT, phdr,
  segment or hash key. The author's `[N]` that it "cannot validate the phdr
  table" is right. **No disagreement with the committed PDR finding.**
- **`REPO-STATE-MAP.md:35,49`: stale.** Both rows say cdsp has "none
  dedicated" / "none" and verdict `NEW`. That was true before this work; it is
  now false, and Rule 1 required fixing it in the same session. The author did
  not.
- **`research/fleet/oneplus6-partition-map.md:28`: contradicts claim 11.** It
  records the OP6 `modem.img` FAT `IMAGE/` tree as containing `cdsp.b00-b10`.
  Same for `workorders/inbox/STATUS-DESKTOP.md:141`. The claim-11 negative was
  written without reading the two documents in this repo that refute it.

## Survives audit

These I attacked and could not break:

1. **23 = 33 − 10** — exact, and the alias rule is correctly "relabel, not drop".
2. **`.bNN` numbering is phdr-index-based**, not a counter over non-empty segments (`b08` present, `b07` absent, with phdr 7 empty).
3. **`cdsp.mdt` 64/64 reach**, including the 63→64 correction mechanism.
4. **No 30-device `.mdt` cluster**; largest is 2 devices; 54/64 unique. The census's best correction.
5. **Sibling-size rule on the target image** (10/10 + 3/3) and, contrary to the author's belief, **on a second device** (9/9 + 3/3).
6. **`b00 ++ b01 == mdt`** exactly, 7660 bytes.
7. **p_flags layout** — bit-for-bit identical to coreboot's `0x00E00000`/shift 21 and mainline's `(7<<24)`/`BIT(27)`.
8. **No ZI tagging** — holds on the full corpus *and* on `.mdt`-only (319 words).
9. **DER chain in segment 1** — 3 contiguous, valid X.509 certs at 1048/2085/3180; `24 + 224*32 == 7192` exactly.
10. **`e_flags` 0x66 = V66** — QEMU-sourced, and the V65 variant on the newly-found enchilada image confirms the nibble scheme.
11. **`cdspr.jsn` is a 2-value file, 30+30 devices**, and is not a container manifest.
12. **All 586 md5 / 458 singleton / 492 shared arithmetic** and the 24.8% byte-weighted rate.

## Bottom line

The metadata arithmetic is **sound and reproducible**: every count in
`census.md` that I recomputed from the CSV matched exactly, including the
cluster histogram, the per-file sharing table and the 51.8% headline. The
corrective finding — that `cdsp.mdt` has no big shared cluster and that the
63-device figure is an artifact of un-normalised alias strings — is a real,
useful result and is the honest delta.

The container note is **mixed**. Its byte-level measurements all reproduce
(13 phdr rows, sums 4,129,418 / 20,979,712, three DER certs, 224 hash records,
`b00++b01==mdt`, all ten per-segment parse-bit tables to three decimals). Its
p_flags decoding is correct and better-sourced than most write-ups. But:

- **Claim 11 is refuted outright**, and not by obscure means — the refuting
  bytes are inside a 1 GB zip in the same data root, two committed repo
  documents describe them, and the sibling `census.md`'s own CSV `notes` field
  names the enchilada modem FAT as the provenance of the very ten rows that
  make its 64th device. A negative that emphatic needed one `grep source=`.
- **Claim 9's "code-like" test is not falsifiable as built.** A constant-`0xFF`
  buffer scores as Hexagon code. The author wraps the conclusion in `[I]` and
  hedges well, but the classifier that produced `code_like=3` would also
  certify a lookup table.
- **The genuinely novel part is prior art.** The sibling rule is
  `mdt_loader.c`; the bit layout is coreboot's; V66 is QEMU's; the FAT `image/`
  directory is XDA/SDK common knowledge. Presenting these as findings rather
  than as verification against published sources is the honest-delta problem.
- **The parser ships a bug that bites the exact image the note denies
  exists.** `sibling_path()` looks for `CDSP.b00` beside `CDSP.MDT`, so the
  probe reports 9 violations on the valid enchilada image and 0 on the same
  bytes lowercased. The 139-test suite misses it because every fixture is
  lowercase — the suite tests the rule, not the path that feeds it.

**Honest delta after this audit:** one real census correction (no 30-device
`.mdt` cluster; 63→64 via alias normalisation), one real second-device
confirmation of the container rule that the author wrongly believed impossible,
and a competent byte-level re-description of a format that was already
documented. It is *not* "a full spec + parser" of a previously unknown format,
and its central "no second device" negative is wrong — a negative the author's
own sibling document had already falsified in its `notes` field. The parser is
well-built but fails closed on the one image that would have caught the error.
Verdict on the work as submitted: **do not merge as-is** — D1/D2/D13
(factually wrong, internally contradictory, and contradicted by the repo
itself), D3/D4 (unfalsifiable classifier, doc/code drift), D15 (shipped parser
rejects a valid image) and the stale `REPO-STATE-MAP` rows must be corrected
first. D1/D2/D13 are cheap to fix and actually strengthen the deliverable: the
second device *proves* the rule.
