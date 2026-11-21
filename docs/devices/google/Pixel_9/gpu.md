# google Pixel_9 (tokay) — `gpu` family: byte-identical to Pixel_8A, and a correction to my own #1676 §6

Analysis date 2026-11-21. Analyst: OC-3 (issue [#1712](https://github.com/adineo-cmd/open-device/issues/1712)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `defdd3c`), `torvalds/linux` master, TheMuppets
`proprietary_vendor_google_tokay` (lineage-23.0 / 24.0).

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Prior art

The container format is documented upstream and I do not claim it:
`torvalds/linux` `drivers/gpu/drm/panthor/panthor_fw.c` (complete GPL parser), and
icecream95's "Fun with CSF firmware" (2022-09-12) whose `csffw dump` transcript shows the
same section model on a Rockchip RK3588 / Mali-G610. Neither covers a Pixel device and
neither compares builds. See [#1676](https://github.com/adineo-cmd/open-device/issues/1676)
for the full container walk and [#1694](https://github.com/adineo-cmd/open-device/issues/1694)
for the revision→schema ladder.

## Verdict

`Pixel_9` (`tokay`, "Google Tensor G4") has **5 `gpu` rows / 1,474,560 B**, all
294,912 B, 5 distinct md5 — the same shape as every other Pixel device.

Three results, in order of importance:

1. **`Pixel_9`'s firmware is byte-identical to `Pixel_8A`'s on the matrix's own branch** —
   five files, five matching md5 — while the `soc` column calls them **G4** and **G3**.
   The cleanest instance yet of the `soc` defect: not a label disagreeing with a partition,
   but two different SoC names on identical bytes (§2).
2. **A scope correction to my own #1676 §6.** The Pixel 8 / Pixel 9 firmware split I
   reported there is a property of the **lineage-24.0 branch**, not of the matrix
   snapshot. In the matrix all 8 G3/G4 devices are identical. §3 states this precisely.
3. **The CONFIG first field is a VA, not a key id** — a correction to #1694 found here,
   because `tokay` gave me the build diversity needed to see it (§4).

## 1. The device's 5 `gpu` rows

| file | size (B) | md5 | `db_path` |
|---|---:|---|---|
| `mali_csffw-r50p0.bin` | 294,912 | `27c9b2b908b9ba9b4bc9809a9ad00ba6` | `google/tokay/vendor/firmware` |
| `mali_csffw-r51p0.bin` | 294,912 | `10d86c50fbf11b8ee2ba9fd4e233ca24` | `google/tokay/vendor/firmware` |
| `mali_csffw-r52p0.bin` | 294,912 | `f34ea071c8e12c8bc7aca02dd45db20a` | `google/tokay/vendor/firmware` |
| `mali_csffw-r53p0.bin` | 294,912 | `02e26e697898bcde4dee30320a6f79e7` | `google/tokay/vendor/firmware` |
| `mali_csffw-r54p0.bin` | 294,912 | `23cdc2df701a24775eeeb26b2c251baa` | `google/tokay/vendor/firmware` |

[F] 5 rows, 5 distinct md5, total **1,474,560 B**. `Pixel_9` is `tokay`; 59 matrix rows
in total.

[F] All five matrix md5 verify **5/5** against lineage-23.0 — same branch-snapshot result
as #1676 and #1694, now at 20 rows.

[F] The branch replacement is the same pattern:

```
tokay lineage-23.0: r50p0 r51p0 r52p0 r53p0 r54p0          all 294,912 B
tokay lineage-24.0: r51p0 r54p1 r54p2 r54p3 legacy-r56p0  294,912 / 299,008x3 / 303,104
```

## 2. `Pixel_9` and `Pixel_8A` ship identical firmware under different SoC names

[F] `Pixel_8A` (`akita`) lineage-23.0 md5s, fetched and hashed in #1694:

```
27c9b2b9…  10d86c50…  f34ea071…  02e26e69…  23cdc2df…
```

[F] `Pixel_9` (`tokay`) lineage-23.0 md5s, fetched and hashed here:

```
27c9b2b9…  10d86c50…  f34ea071…  02e26e69…  23cdc2df…
```

[F] **Identical, all five** — the lineage-23.0 snapshot. On lineage-24.0 the two diverge
by exactly one filename while keeping the same five sizes:

```
tokay (Pixel_9)  lineage-24.0: r51p0 r54p1 r54p2 r54p3 legacy-r56p0
akita (Pixel_8A) lineage-24.0: r49p0 r54p1 r54p2 r54p3 legacy-r56p0
                                ^^^^ only difference
sizes, both:  294,912 / 299,008 x3 / 303,104
```

[F] So `r51p0` vs `r49p0` is precisely the Pixel 9 / Pixel 8 discriminator — the 5th file
from #1676 §6 — and the other four are shared. On lineage-23.0 even that one file is
shared, which is why the matrix cannot see the split (§3).

[F] The matrix's `soc` column for these two devices:

| device | codename | `soc` column | GPU firmware (lineage-23.0, i.e. the matrix) |
|---|---|---|---|
| Pixel_8A | `akita` | **Google Tensor G3** | identical, 5/5 md5 |
| Pixel_9 | `tokay` | **Google Tensor G4** | identical, 5/5 md5 |

[I] This is the strongest form of the defect class #1676 §6 identified. There, the
argument was that the `soc` column disagreed with a *partition* derived from firmware.
Here no partition is needed: **two devices labelled as different SoCs carry byte-identical
GPU firmware.** The column cannot be derived from the firmware, because the firmware does
not distinguish them.

[N] I did not verify whether the *rest* of the two devices' blobs differ — only the five
`gpu` files are shown identical. The SoC could legitimately differ while sharing a GPU
binary, if both use the same Mali implementation. **That is a real alternative explanation
and I am not ruling it out.** What is proven is that the GPU firmware is not evidence for
the SoC label.

[F] Published specs put the Tensor G3 and G4 both at **Mali-G715 MP7** (91mobiles,
Notebookcheck, NanoReview, fetched 2026-11-21). If accurate, a shared GPU binary is
expected and the identical firmware is *consistent* with both labels — which is exactly
why this device cannot settle the `soc` question either way. It only shows the firmware is
not a witness.

## 3. Scope correction to my own #1676 §6

#1676 §6 reported that the 8 G3/G4 devices split 3/5 by their 5th firmware file
(`r49p0` vs `r51p0`). That result is correct **for lineage-24.0**, but as written it can
be read as a property of the matrix, and it is not. I am correcting that here.

[F] In the **matrix** (a lineage-23.0 snapshot), per-device md5 signatures collapse to
exactly **two**, not three:

```
signature 1: 4887611e fcb33781 acd5ceb0 56b489dd 7d1d546c   -> 5 GS201 devices
             (Pixel_7, Pixel_7_Pro, Pixel_7a, Pixel_Fold, Pixel_Tablet)
signature 2: 27c9b2b9 10d86c50 f34ea071 02e26e69 23cdc2df   -> 8 G3/G4 devices
             (Pixel_8, Pixel_8A, Pixel_8_Pro, Pixel_9, Pixel_9A,
              Pixel_9_Pro, Pixel_9_Pro_Fold, Pixel_9_Pro_XL)
```

[F] So **all 8 G3/G4 devices are byte-identical in the matrix.** The Pixel 8 / Pixel 9
split appears only from lineage-24.0, where the 5th file becomes `r49p0` for the Pixel 8
trio and `r51p0` for the five Pixel 9 devices.

[I] The corrected statement, which future notes should use:

> **The Pixel 8 / Pixel 9 firmware partition is a property of the current vendor branch,
> not of the coverage-matrix snapshot.** Any claim about it must name the branch.

[F] This is the same defect that bit me in #1676 §5: the matrix has no `source_ref`
column, so a row cannot be dated. Here it produced a subtler error — not a wrong number,
but a correct number stated at the wrong scope.

## 4. Correction: the CONFIG first field is a VA, not a key id

Found here because `tokay` contributes several builds, which gave the diversity needed to
see it. This reverses advice I gave in #1694 and I have corrected that note in place.

[F] `Log verbosity`'s first field across 24 distinct builds takes **13 different values**:

```
0x4112c4 0x4112cc 0x4112e4 0x4112ec 0x41131c 0x41132c 0x4114bc
0x4114dc 0x4114e4 0x411504 0x411514 0x4118a8 0x411a98
```

[F] So it is not an identity. It is a **VA**: all **87/87** CONFIG first fields across
every build fall inside an IFACE VA range, and no build has duplicate CONFIG VAs.

[F] The `tokay` `r51p0` CONFIG set, with each entry's containing IFACE:

```
va=0x00410000 value=7          "Compute iterator suspend stage skip mask"  -> IFACE 0x410000-0x420000
va=0x00410004 value=7          "Fragment iterator suspend stage skip mask" -> IFACE 0x410000-0x420000
va=0x00410008 value=7          "Geometry iterator suspend stage skip mask" -> IFACE 0x410000-0x420000
va=0x004114e4 value=3          "Log verbosity"                             -> IFACE 0x410000-0x420000
va=0x0041000c value=0xffffffff "WA_CFG0"                                    -> IFACE 0x410000-0x420000
```

[I] **The name string is the stable identifier; the VA is where the entry lives.** A
parser should key on the name, not the first field — the opposite of what I wrote in
#1694.

[F] `Pixel_9` confirms the #1694 revision→schema ladder from the G4 side, exactly as
predicted:

| build | `hdr.size` | CONFIG | schema |
|---|---:|---:|---|
| `r50p0` | 968 | 5 | TILER (`Tiler iterator…`) |
| `r51p0` | 972 | 5 | GEOMETRY (`Geometry iterator…`) |
| `r52p0` | 972 | 5 | GEOMETRY |
| `r53p0` | 972 | 5 | GEOMETRY |
| `r54p0` | 792 | 2 | MINIMAL |

[F] Every table ends at exactly `hdr.size`, and magic `0xc3f13a6e` / `major 0` hold on all
five. The ladder predicted in #1694 holds on a G4 device, not just the G3/GS201 ones it
was derived from.

## 5. Honest negatives

1. **The `soc` defect in §2 has an innocent explanation I cannot exclude** — Tensor G3 and
   G4 both reportedly use Mali-G715 MP7, so identical GPU firmware is *expected* even if
   the SoCs genuinely differ. The firmware is not a witness either way. My claim is
   limited to that [N].
2. **I did not read `GPU_ID` on hardware**, so I cannot confirm the Mali model for either
   device; the G715 attribution is quoted from published specs [N].
3. **I compared only the 5 `gpu` files**, not the other ~54 rows for each device, so I make
   no claim about whole-device blob identity [N].
4. **The CONFIG field meanings are still unknown.** I established that the first field is
   a VA (87/87) and that `value` exists, but not what `value` means [OPEN].
5. **No payload is committed**; all parsing used local downloads of public vendor trees.
6. **The `interface_documented = n` defect** (all 65 Mali rows) applies to these 5 rows too
   and is inherited from #1676 §5.5.

## 6. Rule 1 — corrections for the lead, not applied here

1. **`coverage-matrix.csv` still has no `source_ref` column.** This issue produced the
   subtlest instance yet: a correct number stated at the wrong scope (§3), which a branch
   column would have prevented outright.
2. **`soc` column**: `Pixel_8A` = G3 and `Pixel_9` = G4 on byte-identical GPU firmware
   (§2). Whether or not the SoCs differ, the firmware cannot be the source of that column.
3. **`docs/REPO-STATE-MAP.md:18`** still reads "5 per-SoC GPU docs"; there are now three
   device-level Mali notes as well.
4. **#1694's `key_id` naming is corrected in place** (commit `eeb2fb4`) — the field is a
   VA. Any downstream use of that note should use the corrected wording.

## 7. Reproduce

```sh
# run from the repo root

# the 5 rows
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv'))
   if x['device']=='Pixel_9' and x['blob_family']=='gpu']
for x in r: print(x['filename'], x['size_bytes'], x['md5_db'])
print('rows',len(r),'distinct md5',len({x['md5_db'] for x in r}),
      'total',sum(int(x['size_bytes']) for x in r))"

# the matrix collapses to 2 signatures across all 13 devices (scope correction, §3)
python3 -I -c "
import csv
from collections import defaultdict
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
m=[x for x in r if 'mali' in x['filename'].lower()]
sig=defaultdict(list)
for d in sorted({x['device'] for x in m}):
    xs=sorted([x for x in m if x['device']==d],key=lambda y:y['filename'])
    sig[tuple(x['md5_db'][:8] for x in xs)].append(d)
for s,ds in sig.items(): print(s,'->',len(ds),'devices')
print('distinct signatures:',len(sig))"

# Pixel_9 vs Pixel_8A: identical firmware under different soc labels
for v in tokay akita; do
  for f in r50p0 r51p0 r52p0 r53p0 r54p0; do
    printf '%s %s ' "$v" "$f"
    curl -s -L "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_$v/lineage-23.0/proprietary/vendor/firmware/mali_csffw-$f.bin" | md5sum
  done
done

# the CONFIG first field is a VA, not an id
curl -s -L -o /tmp/tokay.bin \
  "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_tokay/lineage-23.0/proprietary/vendor/firmware/mali_csffw-r51p0.bin"
python3 -I -c "
import struct
d=open('/tmp/tokay.bin','rb').read()
hs=struct.unpack('<I',d[16:20])[0]; off=20; ifaces=[]
while off<hs:
    e=struct.unpack('<I',d[off:off+4])[0]
    t=e&0xff; sz=(e>>8)&0xff
    if t==0:
        fl,vs,ve,ds,de=struct.unpack('<IIIII',d[off+4:off+24]); ifaces.append((vs,ve))
    if t==1:
        b=d[off+4:off+sz]
        va=struct.unpack('<I',b[0:4])[0]
        print('CONFIG va=0x%08x name=%r in_iface=%s' % (
            va, b[12:].split(b'\x00')[0].decode(),
            any(a<=va<z for a,z in ifaces)))
    off+=sz
print('hdr.size',hs,'ends',off,'equal',off==hs)"
# expect every CONFIG to print in_iface=True, hdr.size 972
```

## What would upgrade this finding

1. Read `GPU_ID` on both a Pixel 8A and a Pixel 9 — that alone would settle whether the
   shared firmware reflects a shared GPU or a mislabelled SoC.
2. Compare the *non*-`gpu` rows of `akita` and `tokay`; if they differ while the GPU
   firmware does not, the shared GPU is real and the `soc` column may be right.
3. Determine what the CONFIG `value` field means — the VA question is now settled.

Not legal advice. All facts are DB metadata, public GPL kernel source, public vendor
trees, and firmware-stored ASCII config names.
