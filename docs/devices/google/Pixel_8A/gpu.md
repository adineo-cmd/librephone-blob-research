# google Pixel_8A (akita) — `gpu` family: 5 Mali CSF images, and the container has **three** schema variants, not one

Analysis date 2026-11-21. Analyst: OC-3 (issue [#1694](https://github.com/adineo-cmd/open-device/issues/1694)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `89b5fc6`), `torvalds/linux` master, TheMuppets
`proprietary_vendor_google_akita` (lineage-23.0 / 24.0).

Header and descriptor bytes were parsed from **full local downloads** of the public
TheMuppets files; no payload is committed and no proprietary content is reproduced
beyond short ASCII config names that the firmware itself stores in plain text.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Read this first — what is prior art and what is new

The container format is **not** my discovery and I do not claim it:

- **`torvalds/linux` `drivers/gpu/drm/panthor/panthor_fw.c`** — complete GPL parser for
  this exact format (header, entry types, section headers, flag bits).
- **icecream95, "Fun with CSF firmware", 2022-09-12** — an RE writeup whose `csffw dump`
  transcript independently shows the same section model (VA span + data span + flags +
  name), on a Rockchip RK3588 / Mali-G610.

Both are generic v10 CSF work. **Neither connects the firmware to a Pixel device, and
neither notices that the descriptor set varies between builds** — which is the new result
here (§3). The device-level facts and the schema census are mine; the format is theirs.

## Verdict

`Pixel_8A` (`akita`, "Google Tensor G3") has **5 `gpu` rows / 1,474,560 B**, all
`mali_csffw-rNNpM.bin` at 294,912 B with 5 distinct md5 — the same shape as the other 12
Pixel devices in the matrix.

Two results are worth the note:

1. **The CONFIG schema is a monotonic function of the ARM release number.** Across 24
   distinct builds the descriptor set takes exactly three forms, and they partition
   perfectly by `rNN` with zero overlap: `r48–50` → TILER (968 B header), `r51–53` →
   GEOMETRY (972 B), `r54+` → MINIMAL (792 B). Two of them differ only by a *renamed*
   config key. That makes `hdr.size` a revision fingerprint readable from 20 bytes.
2. **`Pixel_8A` independently reproduces the Pixel 8 / Pixel 9 firmware partition** found
   in [#1676](https://github.com/adineo-cmd/open-device/issues/1676) §6, from a device
   that note never analysed. That is a real out-of-sample confirmation, not a restatement.

## 1. The device's 5 `gpu` rows

| file | size (B) | md5 | `db_path` |
|---|---:|---|---|
| `mali_csffw-r50p0.bin` | 294,912 | `27c9b2b908b9ba9b4bc9809a9ad00ba6` | `google/akita/vendor/firmware` |
| `mali_csffw-r51p0.bin` | 294,912 | `10d86c50fbf11b8ee2ba9fd4e233ca24` | `google/akita/vendor/firmware` |
| `mali_csffw-r52p0.bin` | 294,912 | `f34ea071c8e12c8bc7aca02dd45db20a` | `google/akita/vendor/firmware` |
| `mali_csffw-r53p0.bin` | 294,912 | `02e26e697898bcde4dee30320a6f79e7` | `google/akita/vendor/firmware` |
| `mali_csffw-r54p0.bin` | 294,912 | `23cdc2df701a24775eeeb26b2c251baa` | `google/akita/vendor/firmware` |

[F] 5 rows, 5 distinct md5, total **1,474,560 B**. `Pixel_8A` is `akita`; the device has
54 matrix rows in total.

### 1.1 The matrix is a faithful lineage-23.0 snapshot here too

[F] I fetched all five from the real branch and hashed them:

| file | matrix md5 | lineage-23.0 | match |
|---|---|---|---|
| `r50p0` | `27c9b2b908b9…` | `27c9b2b908b9…` | ✅ |
| `r51p0` | `10d86c50fbf1…` | `10d86c50fbf1…` | ✅ |
| `r52p0` | `f34ea071c8e1…` | `f34ea071c8e1…` | ✅ |
| `r53p0` | `02e26e697898…` | `02e26e697898…` | ✅ |
| `r54p0` | `23cdc2df701a…` | `23cdc2df701a…` | ✅ |

[F] **5/5 exact.** This extends #1676's branch-dating proof from 10 rows to 15. The
`Pixel_8A` rows carry no branch identifier either, and on lineage-24.0 the set has again
been replaced:

```
akita lineage-23.0:  r50p0 r51p0 r52p0 r53p0 r54p0          all 294,912 B
akita lineage-24.0:  r49p0 r54p1 r54p2 r54p3 legacy-r56p0  294,912 / 299,008x3 / 303,104
```

[I] Same defect class as #1676 §5.4: a row cannot be dated from the matrix alone. Cited,
not re-claimed.

## 2. The container, verified on this device's bytes

[F] All three distinct `akita` builds parse cleanly against `panthor_fw.c`:

| build | file | `hdr.size` | entries | `magic` | `major` | `minor` | `version_hash` | table ends at `hdr.size` |
|---|---:|---:|---:|---|---:|---:|---|---|
| `r49p0` | 294,912 | 968 | 27 | `0xc3f13a6e` | 0 | 3 | `0x02050000` | ✅ |
| `r50p0` | 294,912 | 968 | 27 | `0xc3f13a6e` | 0 | 3 | `0x02080000` | ✅ |
| `r54p0` | 294,912 | 792 | 24 | `0xc3f13a6e` | 0 | 3 | `0x02080000` | ✅ |

[F] Magic and `major` match `CSF_FW_BINARY_HEADER_MAGIC` / `CSF_FW_BINARY_HEADER_MAJOR_MAX`
on every build, and every descriptor table ends at **exactly** `hdr.size`.

[F] Entry-type census on this device:

| type | `r49p0` / `r50p0` (968 B hdr) | `r54p0` (792 B hdr) |
|---|---:|---:|
| 0 IFACE | 8 | 8 |
| 1 CONFIG | **5** | **2** |
| 3 TRACE_BUFFER | 8 | 8 |
| 4 TIMELINE_METADATA | 1 | 1 |
| 5, 7, 8, 9 (undocumented) | 1 each | 1 each |
| 6 BUILD_INFO_METADATA | 1 | 1 |
| **total** | **27** | **24** |

[F] The 176-byte header difference is **exactly** the three extra CONFIG entries:
`968 − 792 = 176` and `60 + 60 + 56 = 176`.

## 3. New result: three CONFIG schemas, and the header size follows exactly

This is the finding no prior-art source has, because it requires comparing builds rather
than parsing one file.

[F] Across **24 distinct builds** (deduplicated by md5; drawn from the whole Pixel
family — GS201 and G3/G4, since the schema is a property of the ARM release rather than
the SoC) the CONFIG name-sets fall into exactly **three** groups:

| schema | builds | CONFIG names |
|---|---:|---|
| MINIMAL | 11 | `Log verbosity`, `WA_CFG0` |
| GEOMETRY | 8 | `Compute iterator suspend stage skip mask`, `Fragment iterator suspend stage skip mask`, **`Geometry iterator suspend stage skip mask`**, `Log verbosity`, `WA_CFG0` |
| TILER | 5 | `Compute iterator suspend stage skip mask`, `Fragment iterator suspend stage skip mask`, **`Tiler iterator suspend stage skip mask`**, `Log verbosity`, `WA_CFG0` |

[F] `11 + 8 + 5 = 24`, the full set.

### 3.1 The schema is a monotonic function of the ARM release number

[F] Sorting the 24 builds by the `rNN` in their filename gives a **perfect, zero-overlap**
partition:

| `rNN` | schema | `hdr.size` | builds |
|---|---|---:|---:|
| 48, 49, 50 | TILER | 968 | 5 |
| 51, 52, 53 | GEOMETRY | 972 | 8 |
| 54, 56 | MINIMAL | 792 | 11 |

[F] Every build with `rNN ≤ 50` is TILER, every build with `51 ≤ rNN ≤ 53` is GEOMETRY,
and every build with `rNN ≥ 54` is MINIMAL. **Not one build violates the ordering**, and
the partition holds across both generations (GS201 and G3/G4) and across all three
LineageOS branches.

[I] So the CONFIG schema is not random and not device-specific — it is a **build-generation
fingerprint**. Two consequences worth stating:

1. **You can date a `mali_csffw.bin` to a revision band from its descriptor table alone**,
   with no filename and no payload — read `hdr.size` (792 / 968 / 972) and you know
   whether it is an `r54+`, an `r48–50`, or an `r51–53` build. This is the same *kind* of
   result as the `git_sha` finding in #1676 §3.5, but works on 20 bytes instead of a full
   download.
2. **The evolution is rename-then-remove, not independent variants.** Going
   TILER → GEOMETRY → MINIMAL the three `… iterator suspend stage skip mask` keys are
   first **renamed** (`Tiler` → `Geometry`) and then **dropped entirely**. That is a
   coherent authoring sequence, which is what makes the monotonic correlation meaningful
   rather than coincidental.

[N] This is still inference from filename revision tags, not from an ARM release note. The
correlation is exact on 24 builds; the *cause* is my reading.

[F] **TILER and GEOMETRY are the same schema with one key renamed**, and the header size
tracks the rename to the byte:

```
TILER:    hdr.size = 968,  CONFIG sizes 60 + 60 + 56 + 32 + 24 = 232
GEOMETRY: hdr.size = 972,  CONFIG sizes 60 + 60 + 60 + 32 + 24 = 236
972 − 968 = 4,  and "Geometry iterator" is 3 chars longer than "Tiler iterator",
                padded to the 4-byte entry boundary
```

[I] So "Tiler" and "Geometry" are the **same hardware unit under two names**, and the
rename is visible in the firmware's own descriptor table. This is a small but genuinely
useful result: it means a parser keyed on the *name string* would break across builds,
while one keyed on the numeric key id would not.

### 3.2 The CONFIG entry size is fully determined — 288/288

[F] I checked every CONFIG entry in every build on disk (288 of them) against a predicted
size:

```
size == 4 + align4(12 + strlen(name) + 1)
```

[F] **288 matched, 0 mismatched.** The payload is `u32 key_id; u32 zero; u32 value;
char name[];` NUL-terminated and padded to a 4-byte boundary, and the whole entry
(including its 4-byte `ehdr`) is that plus 4.

[F] Sample decode from `akita/r49p0`:

```
key_id=0x00410000 zero=0 value=7  name="Compute iterator suspend stage skip mask"   size=60
key_id=0x00410004 zero=0 value=7  name="Fragment iterator suspend stage skip mask"  size=60
key_id=0x00410008 zero=0 value=7  name="Tiler iterator suspend stage skip mask"     size=56
key_id=0x00411504 zero=0 value=3  name="Log verbosity"                              size=32
key_id=0x0041000c zero=0 value=0xffffffff name="WA_CFG0"                            size=24
```

[N, OPEN] `panthor_fw.c` does **not** define a struct for CONFIG entries — it explicitly
skips them (`/* FIXME: handle those entry types? */`). So the layout above is **my
reverse-engineering from 288 consistent instances**, not a vendor or kernel statement.
The size rule is proven; the *meaning* of `key_id` and `value` is not.

[N] The `WA_CFG0` entry has `value = 0xffffffff`, which reads as "all workarounds". I did
not verify that interpretation.

## 4. `Pixel_8A` independently confirms the Pixel 8 / Pixel 9 partition

[F] #1676 §6 found that four of the five G3/G4 files are byte-identical across all 8
devices, and the fifth (`r49p0` vs `r51p0`) splits them 3/5 along the Pixel 8 / Pixel 9
line. `Pixel_8A` was **not** analysed in that note. Its lineage-24.0 5th file is:

```
akita/mali_csffw-r49p0.bin   294,912 B   md5 86e5bb9275e8adef361b5a186fce25f4
```

[F] That is **exactly** the Pixel-8-group hash (`86e5bb9275e8…`) from #1676 §6, shared
with `shiba` (Pixel_8) and `husky` (Pixel_8_Pro) and **not** with any Pixel 9 device.

[F] This is an out-of-sample confirmation: the partition was derived from 8 devices
without `akita`, and `akita` lands on the correct side. #1676 §6 stands.

[F] `Pixel_8A`'s `soc` column says "Google Tensor G3", which agrees with the firmware
partition — unlike `Pixel_9_Pro` and `Pixel_9_Pro_Fold`, which #1676 §6 flags as labelled
G3 while carrying Pixel-9 firmware. So this device is one of the 4-of-8 that are correct.

## 5. The GPU model — quoted, not measured

[N] I could **not** verify the GPU model from the firmware. `panthor_hw.c:120` maps
`(arch_major, prod_major)` → name, but that requires reading `GPU_ID` on hardware, which
I did not do. The header's `version_hash` is not the GPU id.

[F] Published specifications for the Tensor G3 in `Pixel_8A` give **Mali-G715 MP7**
(91mobiles, Notebookcheck, Android Authority, all fetched 2026-11-21). `panthor_hw.c`
maps `(11,2)` → `Mali-G715`, which is consistent — but this is a *consistency check
between two secondary sources*, not a measurement [I].

[N] I did not establish which of `arch10.8 / 10.10 / 10.12 / 11.8 / 12.8 / 13.8 / 14.8`
(the 7 `MODULE_FIRMWARE` variants) `Pixel_8A` actually loads. The vendor filenames
(`rNNpM`) do not encode it — #1676 §3.3.

## 6. Honest negatives

1. **I did not read `GPU_ID` on hardware.** The Mali-G715 attribution is quoted from
   published specs and only *checked for consistency* against `panthor_hw.c` [N].
2. **The CONFIG payload layout is my RE**, not a documented struct — `panthor_fw.c`
   skips type 1 entirely. The size rule is verified 288/288; the field meanings are not
   [I].
3. **The "Tiler == Geometry" conclusion is inference** from a rename plus a 4-byte header
   delta. I did not find ARM documentation naming the unit [I].
4. **Only 3 of `akita`'s builds were parsed in detail** (`r49p0`, `r50p0`, `r54p0`). The
   schema census covers 24 builds, but the per-device table in §2 is a subset [N].
5. **I did not verify the lineage-24.0 files' git SHAs** for this device, so I cannot say
   whether `akita`'s `r54p1..p3` are the same builds as `lynx`'s [N].
6. **No payload bytes are committed.** All parsing used local downloads of public vendor
   trees; the matrix's own stored bytes were never read [N].
7. **The `interface_documented = n` defect** is inherited from #1676 §5.5 and confirmed
   for this device (all 65 Mali rows say `n`); I did not investigate its cause [N].

## 7. Rule 1 — corrections for the lead, not applied here

1. **`coverage-matrix.csv` still has no `source_ref` column.** This device is the 15th
   row proving the gap. Highest-value fix, unchanged from #1676 §8.1.
2. **`interface_documented` is wrong for these 5 rows too** — the interface is fully
   documented in mainline, and §2–§3 exercise that documentation.
3. **`docs/REPO-STATE-MAP.md:18`** still reads "GPU core ID | 27 | PARTIAL | 5 per-SoC GPU
   docs"; the `gpu` family now has two device-level Mali notes in addition to the five
   Adreno SoC notes.
4. **Any parser of this format should key CONFIG entries on `key_id`, not on the name
   string** — §3 shows the name changes between builds while the id does not.

## 8. Reproduce

```sh
# run from the repo root

# the 5 rows and that they are 5 distinct payloads
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv'))
   if x['device']=='Pixel_8A' and x['blob_family']=='gpu']
for x in r: print(x['filename'], x['size_bytes'], x['md5_db'])
print('rows',len(r),'distinct md5',len({x['md5_db'] for x in r}),
      'total',sum(int(x['size_bytes']) for x in r))"

# the 5/5 branch check
for f in r50p0 r51p0 r52p0 r53p0 r54p0; do
  printf '%s ' "$f"
  curl -s -L "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_akita/lineage-23.0/proprietary/vendor/firmware/mali_csffw-$f.bin" | md5sum
done

# descriptor walk + CONFIG decode for one build
curl -s -L -o /tmp/akita.bin \
  "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_akita/lineage-24.0/proprietary/vendor/firmware/mali_csffw-r49p0.bin"
python3 -I -c "
import struct
d=open('/tmp/akita.bin','rb').read()
hs=struct.unpack('<I',d[16:20])[0]; off=20
while off<hs:
    e=struct.unpack('<I',d[off:off+4])[0]
    t=e&0xff; sz=(e>>8)&0xff
    if t==1:
        b=d[off+4:off+sz]
        print('CONFIG key=0x%08x val=%d name=%r' % (
            struct.unpack('<I',b[0:4])[0], struct.unpack('<I',b[8:12])[0],
            b[12:].split(b'\x00')[0].decode()))
    off+=sz
print('ends at',off,'hdr.size',hs,'equal',off==hs)"
# expect hdr.size=968, 27 entries, 5 CONFIG incl. 'Tiler iterator suspend stage skip mask'

# the revision-band fingerprint: hdr.size alone (bytes 16-19) determines the schema
python3 -I -c "
import struct,glob,os,hashlib
from collections import defaultdict
by=defaultdict(set)
for f in glob.glob('/tmp/*.bin')+glob.glob('/tmp/opencode/*'):
    if not os.path.isfile(f): continue
    try: d=open(f,'rb').read()
    except: continue
    if len(d)<1000 or d[:4]!=b'\x6e\x3a\xf1\xc3': continue
    hs=struct.unpack('<I',d[16:20])[0]; off=20; cf=[]
    while off<hs:
        e=struct.unpack('<I',d[off:off+4])[0]
        t=e&0xff; sz=(e>>8)&0xff
        if t==1:
            b=d[off+4:off+sz]
            cf.append(b[12:].split(b'\x00')[0].decode('ascii','replace'))
        off+=sz
    sch='GEOMETRY' if any('Geometry' in x for x in cf) else ('TILER' if any('Tiler' in x for x in cf) else 'MINIMAL')
    by[hs].add(sch)
for hs in sorted(by): print(hs, sorted(by[hs]))
print('hdr.size uniquely determines schema:', all(len(v)==1 for v in by.values()))"
# expect 792->MINIMAL, 968->TILER, 972->GEOMETRY, and True
```

## What would upgrade this finding

1. Read `GPU_ID` on a Pixel 8A and apply `panthor_hw.c:120` — converts §5 from a quoted
   consistency check into a measured fact.
2. Determine what `key_id` and `value` mean for CONFIG entries — the 288-instance size
   rule is solid, the semantics are open.
3. Check whether the TILER→GEOMETRY rename correlates with a GPU stepping or an ARM
   release, which would make it a build fingerprint.

Not legal advice. All facts are DB metadata, public GPL kernel source, public vendor
trees, and firmware-stored ASCII config names.
