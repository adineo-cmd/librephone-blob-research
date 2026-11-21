# google Pixel_9_Pro (caiman) — `gpu` family: byte-identical to `Pixel_9` on all five lineage-24.0 files, under a "G3" label

Analysis date 2026-11-21. Analyst: OC-3 (issue [#1730](https://github.com/adineo-cmd/open-device/issues/1730)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `1bf64bd`), `torvalds/linux` master, TheMuppets
`proprietary_vendor_google_caiman` (lineage-23.0 / 24.0), plus `tokay` and `akita` for
comparison.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Prior art and prior results

The container format is documented upstream and I do not claim it:
`torvalds/linux` `drivers/gpu/drm/panthor/panthor_fw.c` (complete GPL parser), and
icecream95's "Fun with CSF firmware" (2022-09-12) whose `csffw dump` transcript shows the
same section model on a Rockchip RK3588 / Mali-G610. Neither covers a Pixel device and
neither compares builds.

Three results are already established in this lab and are **cited, not re-derived**:

| result | where |
|---|---|
| full container walk; `hdr.size` is the descriptor-table size; sections alias one payload | [#1676](https://github.com/adineo-cmd/open-device/issues/1676), `docs/devices/google/Pixel_7a/gpu.md` §3 |
| `hdr.size` alone (bytes 16–19) dates a build to a revision band: 792/968/972 | [#1694](https://github.com/adineo-cmd/open-device/issues/1694), `docs/devices/google/Pixel_8A/gpu.md` §3 |
| CONFIG first field is a VA, not a key id; the name string is the stable identifier | [#1712](https://github.com/adineo-cmd/open-device/issues/1712), `docs/devices/google/Pixel_9/gpu.md` §4 |

## Verdict

`Pixel_9_Pro` (`caiman`) has **5 `gpu` rows / 1,474,560 B**, all `mali_csffw-rNNpM.bin` at
294,912 B, 5 distinct md5, and its `soc` column says **"Google Tensor G3"**.

Two results:

1. **`caiman` is byte-identical to `tokay` (`Pixel_9`, labelled "Google Tensor G4") on
   all five lineage-24.0 files** — verified with `cmp`, not just md5. This is the branch
   on which the Pixel 8 / Pixel 9 split *is* observable, so the identity cannot be
   dismissed as a snapshot artefact (§2).
2. **This resolves a doubt #1712 raised about its own result.** That note conceded its 5/5
   identity might be a lineage-23.0 artefact, since the two devices diverge by one file on
   lineage-24.0. For the Pixel 9 group the identity survives on the discriminating branch
   (§3).

**Scope, stated up front:** #1676 already analysed `caiman` and already knew its 5th file
is `r51p0`, shared with `tokay`. This note does not discover the partition. What it adds is
a byte-level 5/5 comparison on lineage-24.0 (previously only the 5th file was compared
across devices) and the `version_hash` difference that shows the discriminator is a
generation change (§3).

## 1. The device's 5 `gpu` rows

| file | size (B) | md5 | `interface_documented` |
|---|---:|---|---|
| `mali_csffw-r50p0.bin` | 294,912 | `27c9b2b908b9ba9b4bc9809a9ad00ba6` | `n` |
| `mali_csffw-r51p0.bin` | 294,912 | `10d86c50fbf11b8ee2ba9fd4e233ca24` | `n` |
| `mali_csffw-r52p0.bin` | 294,912 | `f34ea071c8e12c8bc7aca02dd45db20a` | `n` |
| `mali_csffw-r53p0.bin` | 294,912 | `02e26e697898bcde4dee30320a6f79e7` | `n` |
| `mali_csffw-r54p0.bin` | 294,912 | `23cdc2df701a24775eeeb26b2c251baa` | `n` |

[F] 5 rows, 5 distinct md5, total **1,474,560 B**, `db_path`
`google/caiman/vendor/firmware`. 59 matrix rows for the device in total.

[F] All five verify **5/5** against lineage-23.0. **These five were already verified in
#1676** (that note's 10-row check was `lynx` + `caiman`), so this is a redundant
confirmation, not a new extension. Branch-checked rows across the Pixel `gpu` family
remain **20**: `lynx` 5 + `caiman` 5 (#1676), `akita` 5 (#1694), `tokay` 5 (#1712).

[F] Branch replacement follows the established pattern:

```
caiman lineage-23.0: r50p0 r51p0 r52p0 r53p0 r54p0          all 294,912 B
caiman lineage-24.0: r51p0 r54p1 r54p2 r54p3 legacy-r56p0  294,912 / 299,008x3 / 303,104
```

## 2. `caiman` is byte-identical to `tokay` on all five lineage-24.0 files

This is the core result. Verified with `cmp`, not merely md5:

```
caiman (Pixel_9_Pro) vs tokay (Pixel_9), lineage-24.0

r51p0         10d86c50fbf11b8ee2ba9fd4e233ca24    cmp: identical
r54p1         d3ad66dc464abb6519d19cefe15f614a    cmp: identical
r54p2         e9a6697fbd887625095ba6dedb7fafca    cmp: identical
r54p3         8c9ae7023ee0b119ce161552f662fdd2    cmp: identical
legacy-r56p0  95dd50fd1039a2a2b8e9c6bcb69dc507    cmp: identical
```

[F] **5/5 byte-identical.** And against `akita` (`Pixel_8A`, also labelled "G3") on the
same branch, `caiman` differs in **exactly one** file:

```
caiman vs akita, lineage-24.0
  r51p0   10d86c50…  vs  r49p0   86e5bb92…   <- the only difference
  r54p1 / r54p2 / r54p3 / legacy-r56p0       identical
```

[F] The two files that differ also differ in `version_hash`:

| file | `version_hash` | `hdr.size` |
|---|---|---|
| `caiman`/`tokay` `r51p0` | `0x02080000` | 972 |
| `akita` `r49p0` | `0x02050000` | 968 |

[I] So the Pixel 8 / Pixel 9 discriminator is not just a different build of the same
generation — it carries a different `version_hash`, consistent with the two groups being
on different firmware generations within `0x02`.

## 3. This closes an open doubt from #1712

#1712 reported that `Pixel_8A` and `Pixel_9` share all five files, but honestly qualified
it: on lineage-24.0 those two devices diverge by one file, so the 5/5 identity might be a
lineage-23.0 artefact where the matrix simply cannot see the split.

[F] For the Pixel 9 group that doubt is now resolved. `caiman` and `tokay` are 5/5
identical **on lineage-24.0** — the branch where the split exists and is observable. The
identity is therefore not an artefact of a blind snapshot.

[I] The precise statement:

> On lineage-24.0, the Pixel 9 family shares one GPU firmware set across `tokay`,
> `caiman`, and (per #1676 §6) `tegu`, `comet`, `komodo`. The Pixel 8 family shares a
> different one, differing in exactly the 5th file. The matrix cannot see this because it
> snapshots lineage-23.0.

**Scope note on what is new here.** #1676 already parsed `caiman`'s five lineage-23.0
files and already established that `caiman` and `tokay` share the `r51p0` 5th file — so
`caiman` is not a device that note ignored. What is new in §2 is narrower and should be
stated as such: #1676 compared **the 5th file only** and its sizes; it did not compare all
five files byte-for-byte across the two devices on lineage-24.0. §2 does, and finds a
complete 5/5 identity. That is a confirmation at higher resolution, not a new partition.

[I] The one thing genuinely added to #1676 §6 is the `version_hash` difference between the
two groups' 5th file (`0x02050000` vs `0x02080000`), which #1676 did not record and which
shows the discriminator is a generation change, not a rebuild.

## 4. What this says about the `soc` column — and what it does not

[F] The matrix's own contradiction for this device:

| device | codename | `soc` column | lineage-24.0 GPU firmware |
|---|---|---|---|
| Pixel_9 | `tokay` | Google Tensor **G4** | baseline |
| Pixel_9_Pro | `caiman` | Google Tensor **G3** | **identical, 5/5** |

[I] On lineage-23.0 this could be waved away as "the matrix cannot discriminate". On
lineage-24.0 it cannot: two devices labelled as **different SoC generations** carry
indistinguishable GPU firmware on every one of their five files.

[N] **But I am not claiming the `soc` labels are wrong, and this is important.** Tensor G3
and Tensor G4 both reportedly use the **Mali-G715 MP7** (91mobiles, Notebookcheck,
NanoReview, fetched 2026-11-21). If that is accurate, a shared GPU binary across the two
SoCs is *expected*, and identical firmware is fully consistent with a genuine G3/G4
difference. The firmware is simply **not a witness** for the SoC label in either
direction.

[I] What is proven is narrower and still useful: **the `soc` column cannot be derived from
the GPU firmware.** #1712 reached the same conclusion from `akita`/`tokay`; this note
strengthens it by removing the "but the matrix can't see the difference" escape, and by
showing the identity survives byte-level comparison on the discriminating branch.

[N] I did not compare the other ~54 rows of `caiman` and `tokay`. If those differ, the SoCs
plausibly do too. That comparison is the single most valuable follow-up and I did not do
it.

## 5. Container and schema, verified on this device

[F] Every `caiman` build parses cleanly against `panthor_fw.c` and lands on the
revision→schema ladder predicted in #1694:

| build | branch | size | `hdr.size` | CONFIG | schema | table ends at `hdr.size` |
|---|---|---:|---:|---:|---|---|
| `r50p0` | 23.0 | 294,912 | 968 | 5 | TILER | ✅ |
| `r51p0` | 23.0 | 294,912 | 972 | 5 | GEOMETRY | ✅ |
| `r52p0` | 23.0 | 294,912 | 972 | 5 | GEOMETRY | ✅ |
| `r53p0` | 23.0 | 294,912 | 972 | 5 | GEOMETRY | ✅ |
| `r54p0` | 23.0 | 294,912 | 792 | 2 | MINIMAL | ✅ |
| `r51p0` | 24.0 | 294,912 | 972 | 5 | GEOMETRY | ✅ |
| `r54p1` | 24.0 | 299,008 | 792 | 2 | MINIMAL | ✅ |
| `r54p2` | 24.0 | 299,008 | 792 | 2 | MINIMAL | ✅ |
| `r54p3` | 24.0 | 299,008 | 792 | 2 | MINIMAL | ✅ |
| `legacy-r56p0` | 24.0 | 303,104 | 792 | 2 | MINIMAL | ✅ |

[F] **10/10 exact**, across both branches. `r50p0`→TILER/968, `r51–53`→GEOMETRY/972,
`r54+`→MINIMAL/792, with no exceptions. This is a **consistency check, not new evidence**:
`caiman`'s files were already among the 24 builds from which #1694 derived the ladder, so
this confirms the derivation applies to this device rather than extending it.

[F] All ten carry `magic 0xc3f13a6e`, `major 0`, `version_hash 0x02080000`.

## 6. Honest negatives

1. **The identical firmware does not prove a mislabelled SoC.** Both generations are
   reported to use Mali-G715 MP7, so sharing a GPU binary is expected. My claim is limited
   to "the `soc` column cannot be derived from the GPU firmware" [N].
2. **I compared only the 5 `gpu` files**, not the other ~54 rows per device, so I make no
   claim about whole-device blob identity [N].
3. **I did not read `GPU_ID` on hardware**, so no measured Mali model for this device [N].
4. **CONFIG field semantics remain unknown.** #1712 settled that the first field is a VA;
   what `value` means is still open [OPEN].
5. **No payload is committed.** All parsing used local downloads of public vendor trees;
   only firmware-stored ASCII config names are quoted.
6. **The `interface_documented = n` defect** applies to all 5 of these rows; inherited from
   #1676 §5.5, cause not investigated [N].
7. **I did not verify Google's published SoC for `Pixel_9_Pro`.** The argument rests on
   the firmware identity plus the internal contradiction with `Pixel_9`'s label [N].

## 7. Rule 1 — corrections for the lead, not applied here

1. **`coverage-matrix.csv` still has no `source_ref` column.** This issue is the clearest
   case yet: the same five rows read as "identical to Pixel_9" on one branch and "differs
   by one file" on another, and the matrix cannot say which branch it is.
2. **`soc` column**: `Pixel_9_Pro` = G3 and `Pixel_9` = G4 on byte-identical lineage-24.0
   firmware (§4). Whatever the truth, the firmware is not the source.
3. **`docs/REPO-STATE-MAP.md:18`** still reads "5 per-SoC GPU docs"; there are now four
   device-level Mali notes in addition.
4. **`interface_documented`** is wrong for these 5 rows — the interface is fully documented
   in mainline `panthor_fw.c` and §5 exercises it.

## 8. Reproduce

```sh
# run from the repo root

# the 5 rows
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv'))
   if x['device']=='Pixel_9_Pro' and x['blob_family']=='gpu']
for x in r: print(x['filename'], x['size_bytes'], x['md5_db'])
print('rows',len(r),'distinct md5',len({x['md5_db'] for x in r}),
      'total',sum(int(x['size_bytes']) for x in r))"

# caiman vs tokay, lineage-24.0: expect 5/5 identical by cmp
for f in r51p0 r54p1 r54p2 r54p3 legacy-r56p0; do
  curl -s -L -o /tmp/c.bin \
    "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_caiman/lineage-24.0/proprietary/vendor/firmware/mali_csffw-$f.bin"
  curl -s -L -o /tmp/t.bin \
    "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_tokay/lineage-24.0/proprietary/vendor/firmware/mali_csffw-$f.bin"
  printf '%s ' "$f"
  cmp -s /tmp/c.bin /tmp/t.bin && echo "identical $(md5sum /tmp/c.bin | cut -d' ' -f1)" || echo DIFFER
done

# the 5th file is the only difference vs akita, and it changes version_hash
curl -s -L -o /tmp/ak.bin \
  "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_akita/lineage-24.0/proprietary/vendor/firmware/mali_csffw-r49p0.bin"
python3 -I -c "
import struct
for n in ('/tmp/c.bin','/tmp/ak.bin'):
    d=open(n,'rb').read()
    print(n, 'version_hash=0x%08x' % struct.unpack('<I',d[8:12])[0],
          'hdr.size', struct.unpack('<I',d[16:20])[0])"
# expect 0x02080000 / 972 for caiman r51p0, 0x02050000 / 968 for akita r49p0

# the ladder: hdr.size alone predicts the schema band
python3 -I -c "
import struct,glob,os
for f in sorted(glob.glob('/tmp/*.bin')):
    d=open(f,'rb').read()
    if len(d)<1000 or d[:4]!=b'\x6e\x3a\xf1\xc3': continue
    hs=struct.unpack('<I',d[16:20])[0]; off=20; cf=[]
    while off<hs:
        e=struct.unpack('<I',d[off:off+4])[0]
        t=e&0xff; sz=(e>>8)&0xff
        if t==1: cf.append(d[off+16:off+sz].split(b'\x00')[0])
        off+=sz
    print(os.path.basename(f), hs, len(cf), off==hs)"
# expect hdr.size 792 -> 2 CONFIG, 968 -> 5, 972 -> 5
```

## What would upgrade this finding

1. Compare the ~54 **non-`gpu`** rows of `caiman` and `tokay`. If they differ while the GPU
   firmware does not, the shared GPU is real and the G3/G4 labels may both be correct —
   which would make this a clean example of "firmware is not a witness" rather than a
   suspicious label.
2. Read `GPU_ID` on a Pixel 9 Pro and a Pixel 9 — settles the Mali model question that
   every note in this series has had to leave open.
3. Determine what the CONFIG `value` field means; the VA question is settled as of #1712.

Not legal advice. All facts are DB metadata, public GPL kernel source, public vendor trees,
and firmware-stored ASCII config names.
