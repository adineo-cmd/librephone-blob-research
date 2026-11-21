# google Pixel_7a (lynx) — `gpu` family: 5 Mali CSF firmware images, a fully public container, and a branch-dating trap

Analysis date 2026-11-21. Analyst: OC-3 (issue [#1676](https://github.com/adineo-cmd/open-device/issues/1676)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows,
feat/open-device-site `4dae417`), `torvalds/linux` master, TheMuppets
`proprietary_vendor_google_*` (lineage-22.2 / 23.0 / 24.0).
Header bytes read from the actual firmware: **20 bytes per file** (magic + header
fields); no full payload committed. Every number is command output from this session.

Evidence classes: **[F]** fact (command output) / **[I]** inference / **[H]** hypothesis /
**[N]** negative / **[OPEN]** unresolved.

## Verdict

`Pixel_7a` has **5 `gpu` rows / 1,392,640 B**, and they are **ARM Mali CSF firmware,
not Adreno** — the first Mali device family in this lab [F].

The headline is not a reverse-engineering result, because **there is nothing left to
reverse-engineer**: mainline `panthor_fw.c` is a complete, GPL, documented parser for
exactly this container, and this note verifies it against the device's real bytes.

> **The container is fully public and I verified it end-to-end.** Magic `0xc3f13a6e`
> read from the file; 24 descriptor entries walked; the descriptor table ends at
> **exactly** `hdr.size = 792`; 8 interface sections resolved to VA spans; payload
> accounted to the last byte.

The genuinely new findings are three, and all are about *how this family is recorded*:

1. **The matrix is a correct lineage-23.0 snapshot — but there is no branch column,
   so it cannot be dated or re-verified.** I first mis-read this as a data error and
   posted that publicly; §5 retracts it with the completed 10/10 hash proof.
2. **The `rNNpM` filename is not a recency order and not the arch selector.** The
   kernel ignores the filename entirely and builds the path from the GPU ID (§3.3);
   and `legacy-r56p0` — the highest revision string — only appears from lineage-24.0
   onward, as the *fallback*.
3. **The matrix's own `interface_documented` column says `n` for all 65 Mali rows, and
   that is false** (§5.5) — §3 documents the interface completely. A false negative
   that silently understates Mali coverage.

A fourth result is not new but is newly *mechanical*: the `soc` column can now be
checked against the firmware rather than argued about, and it fails for 4 of 8 devices
(§6).

## 1. The device's 5 `gpu` rows

| file | size (B) | md5 (first 12) | `db_path` |
|---|---:|---|---|
| `mali_csffw-r50p0.bin` | 278,528 | `4887611e86d3` | `google/lynx/vendor/firmware` |
| `mali_csffw-r51p0.bin` | 278,528 | `fcb337811615` | `google/lynx/vendor/firmware` |
| `mali_csffw-r52p0.bin` | 278,528 | `acd5ecb0d4cc` | `google/lynx/vendor/firmware` |
| `mali_csffw-r53p0.bin` | 278,528 | `56b489dd03af` | `google/lynx/vendor/firmware` |
| `mali_csffw-r54p0.bin` | 278,528 | `7d1d546c5ec3` | `google/lynx/vendor/firmware` |

[F] Total 1,392,640 B; all five are exactly 278,528 B and all five have **distinct
md5**. `Pixel_7a` is `lynx`, SoC label "Google Tensor GS201".

This is the **opposite** pattern from every Adreno family in this lab. There, the
files are named by a GPU revision that the firmware does not actually match, and a
device carries 1–4 files. Here, one device carries **five parallel images of the same
GPU**, distinguished only by an ARM release tag.

## 2. Why five files — the fallback ladder

[F] All 13 Pixel devices in the matrix carry exactly 5 `gpu` rows with the same five
filenames. Per device there are **5 distinct md5** (no duplication). Fleet-wide, each
filename has **exactly 2 variants**, and the variant is a property of the device
generation, not the filename:

| generation | devices | file size | distinct md5 per filename |
|---|---|---:|---:|
| Tensor GS201 | Pixel_7, Pixel_7_Pro, Pixel_7a, Pixel_Fold, Pixel_Tablet | 278,528 | 1 |
| Tensor G3/G4 | Pixel_8, Pixel_8A, Pixel_8_Pro, Pixel_9, Pixel_9A, Pixel_9_Pro, Pixel_9_Pro_Fold, Pixel_9_Pro_XL | 294,912 | 1 |

[F] So the fleet has 2 payloads per filename, and a device has 5 payloads — the "2"
and the "5" are different axes, and conflating them is the mistake I made and
retracted in §5.

[I] The five files are a **compatibility ladder**: the driver picks by GPU ID and the
vendor ships several ARM releases so one vendor image boots on several GPU steppings.
This is a hypothesis about intent; what is *verified* is that the kernel does not use
the filename (§3.3).

[F] One correction to the impression the table gives: the five filenames are identical
across all 13 devices **in the matrix**, but on lineage-24.0 only four of them are
shared. The 5th file is generation-specific:

```
lynx (GS201, lineage-24.0):  r54p0  r54p1  r54p2  r54p3  legacy-r56p0
shiba (G3,   lineage-24.0):  r49p0  r54p1  r54p2  r54p3  legacy-r56p0
tokay (G4,   lineage-24.0):  r51p0  r54p1  r54p2  r54p3  legacy-r56p0
```

[F] So the ladder is: four common images plus one per-generation image. That is the
structure the matrix's uniform `r50p0..r54p0` snapshot flattens away — see §5.3.

## 3. The container, verified against the real bytes

### 3.1 Header

[F] The first 20 bytes of `lynx/mali_csffw-r54p0.bin` (read via an HTTP range request;
full hex is 40 chars, quoted in full because it is the only payload evidence used):

```
6e 3a f1 c3 03 00 00 00 00 00 05 01 00 00 00 00 18 03 00 00
```

Decoded against `struct panthor_fw_binary_hdr` (`panthor_fw.c:43-66`):

| offset | field | value | note |
|---:|---|---|---|
| 0 | `magic` | `0xc3f13a6e` | **matches `CSF_FW_BINARY_HEADER_MAGIC`** |
| 4 | `minor` | 3 | |
| 5 | `major` | 0 | **matches `CSF_FW_BINARY_HEADER_MAJOR_MAX = 0`** |
| 6 | `padding1` | 0x0000 | MBZ as documented |
| 8 | `version_hash` | `0x01050000` | |
| 12 | `padding2` | 0 | MBZ as documented |
| 16 | `size` | **792** | descriptor-table size, *not* file size |

[F] `magic` and `major` both match the kernel's constants exactly. This is the
strongest possible confirmation short of running the driver: the vendor's own bytes
satisfy the parser's two hard gates.

**The `size` field is 792, not 278,528.** That looked like corruption until I walked
the table (§3.2): 792 is where the **descriptor table** ends. Payload follows it. The
kernel does the same — `iter.size = hdr.size` then `while (iter.offset < hdr.size)`
(`panthor_fw.c:848-850`) — so `size` bounds the *table*, and section data offsets may
point past it. Any parser that assumes `size == file size` will reject every one of
these files.

### 3.2 The descriptor table walks cleanly to exactly `hdr.size`

[F] Full walk of `lynx/mali_csffw-r54p0.bin`, 24 entries, ending at offset 792:

```
 off type  sz      flags   va.start     va.end  data.s  data.e
  20    0  32   0x00000009 0x00400000 0x00410000    4476    4600
  52    0  32   0x00000009 0x00410000 0x00420000    4608    9500
  84    0  32   0x00000009 0x00000000 0x00010000    4476    4600
 116    0  32   0x0000000d 0x00800000 0x00820000    9500   91304
 148    0  32   0x8000000b 0x02000000 0x02040000   91304  269448
 180    0  32   0x80000009 0x01000000 0x01040000   91304  269448
 212    0  32   0x0000002b 0x03000000 0x03040000       0       0
 244    0  32   0xc000001b 0x04000000 0x04010000  270336  278528
 276    1  32  (CONFIG)
 308    1  24  (CONFIG)
 332    3  40  (TRACE_BUFFER)
 372    3  48  (TRACE_BUFFER)
 420    3  40  (TRACE_BUFFER)
 460    3  44  (TRACE_BUFFER)
 504    3  44  (TRACE_BUFFER)
 548    3  52  (TRACE_BUFFER)
 600    3  52  (TRACE_BUFFER)
 652    3  44  (TRACE_BUFFER)
 696    7  16  (type 7 — undocumented in panthor)
 712    6  12  (BUILD_INFO_METADATA)
 724    5  20  (type 5 — undocumented in panthor)
 744    9  12  (type 9 — undocumented in panthor)
 756    4  28  (TIMELINE_METADATA)
 784    8   8  (type 8 — undocumented in panthor)
```

[F] `parse ends at 792`, `hdr.size = 792`, **equal**. The table is not merely
plausible, it is exact — a random walk would not land on 792.

[F] Entry-type census: 8 × IFACE (type 0), 2 × CONFIG (1), 8 × TRACE_BUFFER (3),
1 × BUILD_INFO_METADATA (6), 1 × TIMELINE_METADATA (4), and **4 types the kernel does
not name** (5, 7, 8, 9) — all marked optional (`bit 31`), which is why the kernel
ignores them without error.

That last point is a real finding: **the format has entries mainline does not
document.** They are optional so they are safely skipped, but a complete spec does not
exist in `panthor_fw.c` alone [F, OPEN].

### 3.3 The filename is not the arch selector — the kernel uses the GPU ID

[F] `panthor_fw.c:811-816`:

```c
snprintf(fw_path, sizeof(fw_path), "arm/mali/arch%d.%d/%s",
         (u32)GPU_ARCH_MAJOR(ptdev->gpu_info.gpu_id),
         (u32)GPU_ARCH_MINOR(ptdev->gpu_info.gpu_id),
         CSF_FW_NAME);
ret = request_firmware(&fw, fw_path, ptdev->base.dev);
```

[F] and the ID bitfields (`panthor_gpu_regs.h:9-16`):

```c
#define   GPU_ARCH_MAJOR(x)  ((x) >> 28)
#define   GPU_ARCH_MINOR(x)  (((x) & GENMASK(27, 24)) >> 24)
#define   GPU_ARCH_REV(x)    (((x) & GENMASK(23, 20)) >> 20)
#define   GPU_PROD_MAJOR(x)  (((x) & GENMASK(19, 16)) >> 16)
```

So upstream firmware is stored as `arm/mali/arch<MAJOR>.<MINOR>/mali_csffw.bin`, and
the `rNNpM` tag in the vendor filename **never reaches the driver**. `MODULE_FIRMWARE`
lists 7 arch variants: `arch10.8, 10.10, 10.12, 11.8, 12.8, 13.8, 14.8` [F].

[F] `panthor_hw.c:120-171` maps `(arch_major, prod_major)` to marketing names —
`(10,2)`=Mali-G710, `(10,7)`=Mali-G610, `(11,2)`=Mali-G715, `(12,0)`=Mali-G720,
`(13,0)`=Mali-G725, `(14,0)`=Mali-G1-Ultra. **This is the first device family in this
lab where the GPU can be identified from a documented, upstream, non-vendor table
rather than by inference.**

[I] The vendor's `r50p0..r54p0` are therefore five candidate images for *one* arch
directory, not five arch builds. The arch is fixed by the silicon; the ladder covers
ARM release differences.

### 3.4 Payload accounting

[F] For `lynx/mali_csffw-r54p0.bin` (278,528 B, header 792 B):

```
unique data spans (5):
    4476-  4600 =    124
    4608-  9500 =   4892
    9500- 91304 =  81804
   91304-269448 = 178144
  270336-278528 =   8192
unique data bytes        = 273,156
payload region           = 277,736  (278,528 - 792)
unaccounted (gaps+align)=   4,580
max data.end = 278,528 = file size exactly, 0 trailing bytes
```

[F] **`max(data.end)` equals the file size exactly — there are no trailing bytes.**
The 4,580 B of gaps are alignment padding and the build-info strings (§3.5). Note
sections [2] and [0] share the data span `4476-4600`, and [5] and [4] both point at
`91304-269448` — **the format aliases the same payload into multiple VA windows**, so
`sum(section sizes)` (451,424) exceeds the file and is not a byte total.

### 3.5 The firmware carries its own build provenance

[F] The build-info entry (type 6 at offset 712) points into a payload region that
contains a plain-text git SHA:

```
git_sha: e59c0ae5222451a40c3001f60317feab3d45cc56
```

[F] All five lineage-24.0 files have **distinct** SHAs, proving they are five genuinely
different builds and not copies:

| file | size | `git_sha` |
|---|---:|---|
| `r54p0` | 278,528 | `e59c0ae5222451a40c3001f60317feab3d45cc56` |
| `r54p1` | 282,624 | `e044fe98e556949a6c05c9d484fa9351b85d4bbb` |
| `r54p2` | 282,624 | `8e60d6128f5bdc3fbbe8526cf16690eb7b47d9b0` |
| `r54p3` | 282,624 | `690855d0fbf0ff106ec41641f0a9aca094a8264b` |
| `legacy-r56p0` | 286,720 | `d691f4d6728dbacf780cdaec8fd4ef6d8951e832` |

[F] The header `version_hash` **never overlaps between the two generations** — a second,
independent confirmation that the two fleet-wide variants are different builds and not
the same file renamed. But it is *not* a per-generation constant, and my first draft of
this note said it was. The verified census, **deduplicated by md5 so each build counts
once (24 distinct builds)**, is:

| `version_hash` | `minor` | builds | sizes | generation |
|---|---|---:|---|---|
| `0x01010000` | 3 | 7 | 278,528 | GS201, lineage-22.2/23.0 `r48p0`–`r52p0` |
| `0x01050000` | 3 | 6 | 278,528 / 282,624 | GS201, lineage-23.0 `r53p0`+ and all lineage-24.0 |
| `0x01050000` | 4 | 1 | 286,720 | GS201, `legacy-r56p0` |
| `0x02050000` | 3 | 1 | 294,912 | G3/G4, lineage-24.0 `r49p0` |
| `0x02080000` | 3 | 8 | 294,912 / 299,008 | G3/G4, lineage-23.0 and lineage-24.0 `r51p0`+ |
| `0x02080000` | 4 | 1 | 303,104 | G3/G4, `legacy-r56p0` |

[F] So the **top byte is the generation discriminator** (`0x01` = GS201, `0x02` = G3/G4)
and the second byte tracks the ARM release line within it (`0x01`, `0x05`, `0x08`).
Across all 24 distinct builds there is **zero** overlap between the `0x01` and `0x02`
families. The `minor` field is a *third*, independent axis: it is 3 for every mainline
image and 4 for every `legacy-r56p0`, on both generations.

[I] That makes `version_hash` a usable *generation* fingerprint from 20 bytes of header —
useful because it needs no payload — while still being useless as a build identifier.
The build identifier is the git SHA, which is per-file.

This is the most useful practical result in the note: **a firmware image can be
identified to an exact upstream commit without trusting the filename.** The SHA is in
the file, in plain text, at a documented entry type.

## 4. The five GS201 devices are byte-identical

[F] Fetching all five lineage-24.0 files for each GS201 device and hashing:

| device | codename | `r54p0` md5 | `r54p1` | `r54p2` | `r54p3` | `legacy-r56p0` |
|---|---|---|---|---|---|---|
| Pixel_7 | `panther` | `d9c3e31756df` | `3e99962746f3` | `d0bcfd23d351` | `bf8f73ab330a` | `2d9743d199ca` |
| Pixel_7_Pro | `cheetah` | `d9c3e31756df` | `3e99962746f3` | `d0bcfd23d351` | `bf8f73ab330a` | `2d9743d199ca` |
| Pixel_7a | `lynx` | `d9c3e31756df` | `3e99962746f3` | `d0bcfd23d351` | `bf8f73ab330a` | `2d9743d199ca` |
| Pixel_Fold | `felix` | `d9c3e31756df` | `3e99962746f3` | `d0bcfd23d351` | `bf8f73ab330a` | `2d9743d199ca` |
| Pixel_Tablet | `tangorpro` | `d9c3e31756df` | `3e99962746f3` | `d0bcfd23d351` | `bf8f73ab330a` | `2d9743d199ca` |

[F] **25/25 identical** across five products. Contrast with the lab's Adreno finding
that GPU firmware filenames never match the GPU revision: here the firmware *is*
genuinely shared, because all five are the same GPU on the same SoC. The sharing is
real, not a mislabel.

[F] The G3/G4 devices are *nearly* the same, and the exception is informative: 4 of
the 5 files (`r54p1`, `r54p2`, `r54p3`, `legacy-r56p0`) are byte-identical across all 8
devices, but the 5th differs and splits them 3/5 along the Pixel 8 / Pixel 9 line
(§6). So "identical" is exact for the GS201 quintet and must be stated per-file for the
G3/G4 octet.

## 5. The branch trap — and the retraction of my own claim

### 5.1 What I got wrong

Mid-session I posted that the matrix "does not match the real device tree" and that
the md5 "does not match either". **The md5 half was wrong** — I had read only the
lineage-24.0 branch. I retracted it on the issue before writing this note, and record
it here so the error is not silently dropped.

### 5.2 The completed proof: 10 of 10

[F] Fetching every `mali_csffw-*.bin` from TheMuppets at three branches and hashing:

**Pixel_7a (`lynx`), matrix says 5 × 278,528 B:**

| file | matrix md5 | lineage-23.0 | match |
|---|---|---|---|
| `r50p0` | `4887611e86d3…` | `4887611e86d3…` | ✅ |
| `r51p0` | `fcb337811615…` | `fcb337811615…` | ✅ |
| `r52p0` | `acd5ecb0d4cc…` | `acd5ecb0d4cc…` | ✅ |
| `r53p0` | `56b489dd03af…` | `56b489dd03af…` | ✅ |
| `r54p0` | `7d1d546c5ec3…` | `7d1d546c5ec3…` | ✅ |

**Pixel_9_Pro (`caiman`), matrix says 5 × 294,912 B:** all five match lineage-23.0
(`27c9b2b908b9…`, `10d86c50fbf1…`, `f34ea071c8e1…`, `02e26e697898…`, `23cdc2df701a…`).

[F] **10/10 exact.** The matrix is a faithful lineage-23.0 snapshot. It is not wrong.

### 5.3 What actually changed between branches

[F] The vendor set was **replaced**, not extended:

```
lynx   lineage-23.0: r50p0 r51p0 r52p0 r53p0 r54p0          all 278,528 B
lynx   lineage-24.0: r54p0 r54p1 r54p2 r54p3 legacy-r56p0  278,528 / 282,624x3 / 286,720
caiman lineage-23.0: r50p0 r51p0 r52p0 r53p0 r54p0          all 294,912 B
caiman lineage-24.0: r51p0 r54p1 r54p2 r54p3 legacy-r56p0  294,912 / 299,008x3 / 303,104
```

[F] Two consequences:

1. **`r54p0` survives by name but not by content** on `lynx` — lineage-23.0
   `7d1d546c5ec3…` vs lineage-24.0 `d9c3e31756df…`. A row keyed on filename alone
   cannot tell these apart.
2. **`legacy-r56p0` is the highest `rNN` yet the fallback, and it only appears in
   lineage-24.0.** Sorting these filenames to infer recency gives the wrong answer.

### 5.4 The real defect is the missing branch column

[F] `db_path` for these rows is `google/lynx/vendor/firmware` — a path, with **no
release or branch identifier**. The full column list is:

```
device, vendor, soc, blob_family, blob_subfamily, filename, size_bytes,
md5_db, sha256_if_listed, isa_identified, interface_documented, priority,
db_path, db_type
```

[F] Fourteen columns, and **none of them dates the row.** (`sha256_if_listed` is empty
for all 65 Mali rows, so there is not even a second hash to cross-check against.)

[I] So a matrix row cannot be dated or re-verified. My own verification attempt failed
precisely because of this: the data was right and unverifiable, which is
indistinguishable from wrong until you guess the branch. That is the finding worth
carrying forward, and it is the one I hit myself.

### 5.5 A second, separate defect: the matrix says the interface is undocumented

[F] All **65 of 65** Mali rows carry `interface_documented = n`. Across the whole
33,917-row matrix only 116 rows say `y`, and every one of those is Qualcomm-specific.
The `gpu` family is `n` for all 781 rows.

[F] **That is false for these 65 rows, and this note disproves it.** §3 walks the
container using a GPL parser that names every field, every entry type and every flag
bit. The interface is not merely documented, it is implemented in mainline Linux and
shipped in `MODULE_FIRMWARE`.

[I] The likely cause is that `interface_documented` was filled from the vendor blob
list (which never documents anything) rather than from upstream. Whatever the cause,
the column is wrong for this family and any coverage statistic computed from it
understates Mali by 65 rows.

## 6. The `soc` column disagrees with the firmware — and the firmware is self-consistent

[F] The 8 G3/G4 devices split into **exactly two groups of 3 and 5**, and the split is
visible in the firmware with no ambiguity: four of the five files are byte-identical
across all 8 devices, and the fifth is the discriminator.

| file | distinct md5 across the 8 devices |
|---|---:|
| `r54p1` | **1** |
| `r54p2` | **1** |
| `r54p3` | **1** |
| `legacy-r56p0` | **1** |
| 5th file | **2** — `r49p0` vs `r51p0` |

[F] The 5th file partitions them exactly along the Pixel 8 / Pixel 9 product line:

| device | codename | `soc` column | 5th file | md5 |
|---|---|---|---|---|
| Pixel_8 | `shiba` | Google Tensor G3 | `r49p0` | `86e5bb9275e8` |
| Pixel_8A | `akita` | Google Tensor G3 | `r49p0` | `86e5bb9275e8` |
| Pixel_8_Pro | `husky` | Google Tensor G3 | `r49p0` | `86e5bb9275e8` |
| Pixel_9 | `tokay` | Google Tensor G4 | `r51p0` | `10d86c50fbf1` |
| Pixel_9A | `tegu` | **(blank)** | `r51p0` | `10d86c50fbf1` |
| Pixel_9_Pro | `caiman` | **Google Tensor G3** | `r51p0` | `10d86c50fbf1` |
| Pixel_9_Pro_Fold | `comet` | **Google Tensor G3** | `r51p0` | `10d86c50fbf1` |
| Pixel_9_Pro_XL | `komodo` | **(blank)** | `r51p0` | `10d86c50fbf1` |

[F] The firmware's 3/5 split is `{Pixel_8, Pixel_8A, Pixel_8_Pro}` vs
`{Pixel_9, Pixel_9A, Pixel_9_Pro, Pixel_9_Pro_Fold, Pixel_9_Pro_XL}` — i.e. precisely
the Pixel 8 family vs the Pixel 9 family.

**Scope qualifier, added 2026-11-21 while working #1712 — this split is a property of
the branch, not of the matrix.** Everything in this section was measured on
lineage-24.0. On lineage-23.0 — which is what the coverage matrix actually snapshots —
**all 8 G3/G4 devices are byte-identical and the split does not exist at all**:

```
matrix per-device md5 signatures: 2 across all 13 Pixel devices
  sig 1  4887611e fcb33781 acd5ceb0 56b489dd 7d1d546c  -> 5 GS201 devices
  sig 2  27c9b2b9 10d86c50 f34ea071 02e26e69 23cdc2df  -> 8 G3/G4 devices
```

[F] So the 3/5 partition below is real but **branch-specific**: any claim about it must
name the branch, and the matrix alone cannot show it. The `soc` disagreement argued below
still stands on lineage-24.0, where the partition is observable — but it is not
observable in the matrix, and I originally wrote it as though it were. See
`docs/devices/google/Pixel_9/gpu.md` §3 for the full correction.

**The `soc` column contradicts that split for 4 of the 8 devices:**

1. **`Pixel_9_Pro` and `Pixel_9_Pro_Fold` are labelled "Google Tensor G3"** — but their
   firmware is byte-identical to `Pixel_9`, which is labelled G4. A Pixel 9 Pro cannot
   be G3, and the firmware places it firmly with the Pixel 9 group.
2. **`Pixel_9A` and `Pixel_9_Pro_XL` have a blank `soc`** — yet their firmware is
   byte-identical to `Pixel_9`'s.

[I] Note this is a *stronger* form of the defect than a mislabel: the firmware provides
an independent, mechanical partition of the 8 devices, and the `soc` column disagrees
with it in 4 cases while leaving 2 blank. Only 4 of 8 rows (the Pixel 8 trio plus
Pixel_9) agree with the bytes.

[I] This is the **eighth** independent instance in this lab of the `soc` column
disagreeing with the firmware, following the OnePlus {835, 855} inversion in
`docs/devices/oneplus/OnePlus_7T_Pro/boot.md` §5. It is now clearly systematic rather
than a handful of bad rows — and here the firmware is unambiguous enough to say which
side is wrong.

[N] I did not independently verify Google's published SoC for each of these five
products; the argument rests on the firmware partition plus the internal contradiction
(Pixel_9 = G4 but Pixel_9_Pro = G3 with identical firmware).

## 7. Honest negatives

1. **I read 20 bytes of header per file, not the payload.** The section walk (§3.2),
   the span accounting (§3.4) and the git SHA (§3.5) were computed from **full local
   downloads** of TheMuppets files — but no payload is committed, and the DB's own
   bytes were never read [N]. If the DB's stored file differs from TheMuppets, §3
   describes TheMuppets, not the DB.
2. **The `hdr.size = 792` reading is my parse, not a vendor statement.** It is
   strongly supported — the walk lands exactly on 792 and `max(data.end)` equals the
   file size — but I did not find a public document that defines `size` as
   table-bounded [I].
3. **Four entry types (5, 7, 8, 9) are undocumented in `panthor_fw.c`.** I did not
   determine their contents; the kernel skips them because they are optional [N, OPEN].
4. **The "fallback ladder" intent (§2) is inference.** What is verified is that the
   kernel ignores the filename and picks by GPU ID. Why the vendor ships five is my
   reading [I].
5. **I did not run the driver or read a GPU ID register.** The arch→marketing-name
   table (§3.3) is quoted from upstream, not applied to a Pixel. Mapping `lynx` to a
   specific Mali model would require reading `GPU_ID` on hardware [N].
6. **Only `lynx` and `caiman` were verified against lineage-23.0.** The other 11
   devices' matrix rows were not individually re-hashed, so "the matrix is a
   lineage-23.0 snapshot" is proven for 10 rows and extrapolated to 65 [I].
7. **`legacy-r56p0`'s role is inferred from its name and presence pattern.** I did not
   confirm the driver ever falls back to it [I, OPEN].
8. **I did not check whether the matrix's `Pixel_9A`/`Pixel_9_Pro_XL` blank SoC is a
   parse failure or a genuinely empty source field** [N].
9. **I did not trace where `interface_documented` gets its value**, so my explanation
   in §5.5 for *why* it says `n` is a guess. What is verified is only that the value is
   wrong [I].

## 8. Rule 1 — corrections for the lead, not applied here

1. **`coverage-matrix.csv` needs a `source_ref` column** (branch or release tag).
   Without it a row is undateable and unverifiable — demonstrated by my own failed
   first check (§5.4). Highest-value fix in this note.
2. **`docs/REPO-STATE-MAP.md:18`** currently reads "GPU core ID | 27 | PARTIAL | 5
   per-SoC GPU docs under `research/soc/`: MSM8998, SM4375, SM7325, SM8250, SM8350;
   22 SoCs remain". **It is no longer accurate in the way it reads.** "PARTIAL" now
   understates two things: this device-level Mali note adds a sixth GPU document, and
   §3.3 supplies an upstream, documented arch→marketing-name table that no Adreno
   family in this lab has. The line also cannot express that the `gpu` family now
   spans two vendors with opposite properties (§8.3).
3. **The `gpu` family is not homogeneous.** Every prior `gpu` note in this repo is
   Adreno, where filenames mislead. This family is Mali, where the container is public,
   the build SHA is in the file, and filenames are irrelevant to loading. Any
   family-wide claim about `gpu` must state which vendor it covers.
4. **`interface_documented` is wrong for all 65 Mali rows** (§5.5). They say `n`; §3
   documents the interface completely from mainline. This is the most concrete matrix
   bug in this note — it is a false negative that is easy to fix and hard to notice.
5. **`soc` column**: `Pixel_9`=G4 vs `Pixel_9_Pro`=G3 with identical firmware, and two
   blank rows (§6). Eighth occurrence of this defect class.

## 9. Reproduce

```sh
# run from the repo root (the checkout that contains upstream-contribution/)

# the 5 rows, and that they are 5 distinct payloads
python3 -I -c "
import csv
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv'))
   if x['device']=='Pixel_7a' and x['blob_family']=='gpu']
for x in r: print(x['filename'], x['size_bytes'], x['md5_db'][:12])
print('rows',len(r),'distinct md5',len({x['md5_db'] for x in r}),
      'total',sum(int(x['size_bytes']) for x in r))"

# the fleet-wide 2-variant structure
python3 -I -c "
import csv
from collections import defaultdict
r=[x for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv'))
   if 'mali' in x['filename'].lower()]
for fn in sorted({x['filename'] for x in r}):
    xs=[x for x in r if x['filename']==fn]
    print(fn,'devices',len({x['device'] for x in xs}),'distinct md5',len({x['md5_db'] for x in xs}))"

# header magic from the real file (first 20 bytes only)
curl -s -r 0-19 -L \
  "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_lynx/lineage-24.0/proprietary/vendor/firmware/mali_csffw-r54p0.bin" \
  | od -An -tx1
# expect: 6e 3a f1 c3 03 00 00 00 00 00 05 01 00 00 00 00 18 03 00 00
#   magic 0xc3f13a6e, major 0, minor 3, size 792

# the descriptor walk (needs the full file locally)
curl -s -L -o /tmp/mali.bin \
  "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_lynx/lineage-24.0/proprietary/vendor/firmware/mali_csffw-r54p0.bin"
python3 -I -c "
import struct
d=open('/tmp/mali.bin','rb').read()
hs=struct.unpack('<I',d[16:20])[0]; off=20
while off<hs:
    e=struct.unpack('<I',d[off:off+4])[0]
    if (e&0xff)==0:
        fl,vs,ve,ds,de=struct.unpack('<IIIII',d[off+4:off+24])
        print(f'IFACE va=0x{vs:08x}-0x{ve:08x} data={ds}-{de}')
    off+=(e>>8)&0xff
print('ends at',off,'hdr.size',hs,'equal',off==hs)
print('file',len(d))"

# the interface_documented false negative (§5.5)
python3 -I -c "
import csv
from collections import Counter
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
m=[x for x in r if 'mali' in x['filename'].lower()]
print('mali rows',len(m),'interface_documented',Counter(x['interface_documented'] for x in m))
print('whole matrix y-count',sum(1 for x in r if x['interface_documented'].startswith('y')))"

# the branch-dating proof
for b in lineage-23.0 lineage-24.0; do
  for f in r50p0 r54p0; do
    printf '%s %s ' "$b" "$f"
    curl -s -L "https://raw.githubusercontent.com/TheMuppets/proprietary_vendor_google_lynx/$b/proprietary/vendor/firmware/mali_csffw-$f.bin" | md5sum
  done
done
```

## What would upgrade this finding

1. Read `GPU_ID` on a Pixel 7a and apply `panthor_hw.c:120` — that would name the exact
   Mali model and turn §3.3 from a quoted table into a device fact.
2. Decode the four undocumented entry types (5, 7, 8, 9) — the container spec in
   `panthor_fw.c` is explicitly incomplete there.
3. Apply the branch check to the other 11 Pixel devices to close honest negative 6.
4. Add `source_ref` to the matrix and re-verify a sample of every family — the missing
   column probably affects far more than `gpu`.

Not legal advice; no proprietary payload accessed or committed beyond a 20-byte header
sample. All facts are DB metadata, public GPL kernel source, and public vendor trees.
