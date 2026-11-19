# WORKORDER-001 (desktop) pass: bm2n ADSP fleet container + ISA evidence, OnePlus 8 BT fleet, larry bdwlan tag-19 geometry

**Devices:** OnePlus Nord CE3 (larry, SM6375) — bm2n fleet + bdwlan; OnePlus 8 (instantnoodle,
SM8250, WCN3998) — bluetooth partition; OnePlus 6 (enchilada, SDM845) — known-Hexagon and
BT-fleet reference side.
**Evidence classes:** `[F]` fact (measured) · `[I]` inference (strong, derived) ·
`[H]` hypothesis (plausible, unverified) · `[N]` honest negative (probed, not found).
**Companion JSON:** `analysis/out/bm2n-isa-bt.json` (all numbers quoted here are in it).
**Scripts (lab-rule compliant):** `analysis/tools/bm2n_isa_probe2.py`,
`bm2n_isa_probe3.py`, `bt_fleet_join2.py`, `tag19_geometry.py`,
`tag19_regdb_compare.py`, `bm2n_isa_bt_merge.py`.
**Discipline:** no proprietary payload bytes in this document — offsets, sizes, hashes,
statistics, ≤16-byte hex samples and short ASCII strings only.

**Method class note (per `librephone-blob-research/mediatek/docs/md1dsp-decode.md`
vocabulary, applied without reusing its MediaTek content):** capstone is not installed
in this environment and has no Hexagon backend anyway, so the `isa_probe.py`
decode-rate sanity cannot run and no byte-level decode was attempted. The probe used
is the lab's decode-gap statistics class (the same honest-negative reporting used for
the md1dsp decode-density table): alignment statistics, word-histogram comparison
against verified references, and string-level provenance. Where the evidence stops,
the verdict says "unknown" — no ISA is claimed as decoded.

Prior-art searches (Rule 0, recorded with dates in the JSON): `bm2n.bin` has no public
matches (2026-11-19); BitML is publicly a Qualcomm internal ML stack on the Hexagon NSP
via `libbitml_nsp_skel.so` (Qualcomm support forum, QNN LPAI API history, meta-qcom);
`htbtfw20.tlv`/`htnv20.bin` filenames are publicly shipped in linux-firmware for
WCN399x (Ubuntu/Fedora packages; kernel btqca WCN3998 ROM-version fix). The delta here
is byte-level: md5 joins, container measurements, and the tag-19/regdb relation.

---

## 1. bm2n fleet container — raw loader-header images, not ELF `[F]`

Files (`data-fetch/second-device/larry/tree-vendor/lib/rfsa/adsp/`), md5-verified
against the committed matrix rows (fleet identity already proven in
`second-device-larry.md`):

| file | bytes | md5 | matrix alias |
|---|---|---|---|
| bm2n06.bin | 864,824 | `9010bb1a…38c6` | — |
| bm2n08.bin | 3,091,896 | `1275a2d2…0156` | — |
| bm2n12.bin | 2,623,528 | `5c86c8fc…3aac8` | ≡ bm2n37.bin |
| bm2n13.bin | 1,106,944 | `bf635d90…d299b` | — |
| bm2n14.bin | 103,168 | `805176af…5d498` | ≡ bm2n55.bin |
| bm2n15.bin | 1,082,856 | `2ce8163c…3d0ea1` | ≡ bm2n31.bin |

- **No ELF magic in any file** — the lab suspicion of raw images is confirmed `[F]`.
- **Every file starts with the same loader-header shape** (u32-LE fields, first 64 B):
  word0 = word7 = word9 = `0x200000` (bm2n06: `0x400000`), word1 = 0, word2 = 7,
  then a **7-char lowercase-hex ASCII build id at [12,19)**, word5 = `0xFA0000FA`,
  word6 = 4, word8 = 2 or 3, word10 = `0x10400` (constant across all six), words
  11–15 per-file. Build ids: 06=`4bd22b0`, 08=`32da3bd`, 12=`2c855d1`, 13=`5371806`,
  14=`2a8527c`, 15=`5371806` `[F]`.
  - **bm2n13 and bm2n15 carry the same build id `5371806`** — two payloads of one
    build (sizes differ by 24,088 B; common prefix 45 B) `[F]`.
- Header semantics unknown beyond the repeated size-class words; `0x10400` (66,560 B)
  is a strong candidate for a fixed header/TOC region `[H]`.

### 1.1 Entropy and zero-run maps `[F]`

- Mean 4K-block entropy: 06 = 3.874, 08 = 5.041, 12 = 3.678, 13 = 3.384, 14 = 3.629,
  15 = 3.375. No compressed-image profile anywhere except bm2n08: it has **56 blocks
  ≥ 7.5 bits/B** in scattered islands of 4–44 KiB — packed/compressed sections inside
  an otherwise mid-entropy image; the other five files have ≤ 5 blocks ≥ 6 bits/B and
  **zero** blocks ≥ 7.5 `[F]`.
- Zero runs: bm2n06 top runs are exactly 3,072 B (34 runs ≥ 256); bm2n13/15 top runs
  2,256 B then repeating 628 B (440 runs ≥ 256 each, identical profile); bm2n08 has
  308 runs ≥ 256; bm2n14 only 2. **Long-run start offsets are never 4,096- or
  1,024-aligned** (0% in all six) — the layout is not page-granular `[F]`.

### 1.2 ISA evidence (no Hexagon decoder — statistics + provenance)

**(a) Word alignment.** Nonzero-u32 fraction across shifts 0..3 is nearly flat
(e.g. 06: 0.593/0.599/0.601/0.604) — the literal "fraction of aligned nonzero words"
statistic is weak here because the images are data-dominant `[F]`. The sharper
statistics:

- **Nonzero-indicator autocorrelation** (lags 1–12): bm2n12/13/14/15 peak exactly at
  lags 4/8/12 — 12: 0.478/0.415/0.605 vs lag-1 0.179; 13: 0.628/0.595/0.687 vs 0.451;
  15: 0.642/0.607/0.683 vs 0.465; 14: 0.405/0.415/0.497 vs 0.138. bm2n06 is flat-high
  (long zero runs dominate); bm2n08 mixed `[F]`.
- **Endianness/word-class:** byte position mod 4 shows the LE small-value asymmetry in
  12/13/14/15 (byte[3] nonzero 10–18% vs bytes 0–2 40–63%); top-byte-zero word
  fraction 0.48–0.82 — consistent with tables/data-heavy DSP images, unlike dense code
  (Hexagon ELF code ref: 0.229 top-byte-zero; ARM64 ref: 0.060) `[F]`.

**(b) 32-bit word histogram vs verified references.** Cosine similarity of the
256-bin top-byte histogram (nonzero 4-aligned words):

| file | a630_gmu (raw Hexagon µcode) | fastcv code (Hexagon ELF) | bitml code (Hexagon ELF) | ARM64 ELF code |
|---|---|---|---|---|
| bm2n06 | 0.738 | 0.590 | 0.588 | 0.485 |
| bm2n08 | 0.658 | 0.524 | 0.491 | 0.503 |
| bm2n12 | 0.693 | 0.545 | 0.584 | 0.365 |
| bm2n13 | 0.698 | 0.550 | 0.587 | 0.373 |
| bm2n14 | 0.689 | 0.541 | 0.580 | 0.362 |
| bm2n15 | 0.699 | 0.550 | 0.587 | 0.374 |

12/13/14/15 sit far closer to both Hexagon references than to the ARM64 contrast
reference; 06 is Hexagon-leaning with a weaker margin; 08 does not separate
(hist ambiguity from its packed islands) `[F]`.

**(c) String provenance — the strongest signal.** All six files share
**30–52 Itanium-mangled C++ type-name fragments with
`libbitml_nsp_v2_skel.so`** — a verified Hexagon ELF (`e_machine=164`, ET_DYN)
sitting in the same directory: `10DmaStartOp`, `11TensorShapeILj4E`,
`12ArtNet_DepthIS4_`, `13QUint8CroutonEER`, `14ConcreteTensor`,
`14DmaSyncMultiOp`, `10QuantUint8EEEiRT`… (short mangled fragments only; full
inventories in the JSON). Counts: 06 = 34, 08 = 44, 12 = 52, 13 = 41, 14 = 30,
15 = 41 `[F]`. BitML is publicly a Qualcomm internal ML stack executed on the
Hexagon NSP through `libbitml_nsp_skel.so` (prior-art sources in JSON) `[F]`.

### 1.3 Per-file ISA verdicts

| file | verdict |
|---|---|
| bm2n06 | **Hexagon-consistent [I]** — header + histogram lean + lag-4/8/12 (weak) + 34 BitML type names; margin smaller |
| bm2n08 | **Hexagon-consistent with packed islands [I]** — 44 BitML type names prove the build stack; histogram does not separate; ISA of the ≥7.5-bit/B islands **unknown [N]** |
| bm2n12 | **Hexagon-consistent [I]** — strong lag-4/8/12, Hexagon>ARM 0.584 vs 0.365, 52 type names |
| bm2n13 | **Hexagon-consistent [I]** — as 12 |
| bm2n14 | **Hexagon-consistent [I]** — as 12; carries the `14ConcreteTensor` RTTI run |
| bm2n15 | **Hexagon-consistent [I]** — as 13 |

No file is claimed as *decoded* Hexagon: no public Hexagon disassembler was available
in this environment; per lab discipline the ISA-level identification is reported as
consistent-by-statistics, not verified `[N]`.

### 1.4 Inter-file structure `[F]`/`[N]`

- Pairwise common prefixes 2–45 B (header only), suffixes 0–7 B,
  **0 shared nonzero 4 KiB blocks across all 15 pairs** — six genuinely distinct
  payloads related by container format and build stack only `[F]`.
- **No internal repetition in any file**: zero duplicate nonzero 4 KiB blocks;
  half/quarter self-equality 0.09–0.56 (sparse-image baseline). The matrix aliases
  (bm2n12≡bm2n37, bm2n14≡bm2n55, bm2n15≡bm2n31) are **content identity under two
  filenames, not internal repetition** `[N for repetition]`.

---

## 2. Cross-device BT fleet — OnePlus 8 (WCN3998) ships the `ht*` family, zero md5 overlap with OP6 `[F]`

### 2.1 Volume and files

`data-fetch/second-device/instantnoodle/bluetooth.img` (454,656 B) is a FAT16 volume
with the same BPB generation as OP6's bt.img (4,096 B/sector, 4 sec/cluster, 2 FATs ×
3 sectors, 512 root entries, 16,384 declared sectors) `[F]`. Root holds one
subdirectory (8.3 short name `PCAFUI~2`) with 5 files; LFNs recovered by a direct FAT
walk (the earlier extraction kept only mangled names):

| LFN | 8.3 name | bytes | md5 |
|---|---|---|---|
| htbtfw10.tlv | PCAFUI~2_3ZDPGQ~2.TLV | 129,964 | `31268dce…80da9` |
| htbtfw20.tlv | PCAFUI~2_EXBNED~2.TLV | 205,836 | `2112a118…379b9` |
| htbtfw20.ver | PCAFUI~2_GHRMCI~2.VER | 36 | `7ea73f61…9e77d` |
| htnv10.bin | PCAFUI~2_GZOYAZ~2.BIN | 3,569 | `32a41273…f3489f` |
| htnv20.bin | PCAFUI~2_LSB5SP~2.BIN | 5,815 | `0ef258ea…f16ec3` |

`htbtfw20.ver` is ASCII: `BTFM.HST.2.0.0.c3-00476-QCACHROMZ-1` (a BTFM package
version string) `[F]`.

### 2.2 md5 joins

- **Coverage matrix:** every md5 matches exactly **2 rows** — OnePlus_8 and
  OnePlus_8_Pro (`db_path oneplus/instantnoodle{,p}/bluetooth/image`). These files are
  **device-pair-scoped, not a broad fleet** `[F]`.
- **vs OP6 10-file fleet (`data-fetch/enchilada/bt-fat/`): zero md5 overlap** `[F]`.
  The OnePlus 8 WCN3998 ships a **third QCA prefix family (`ht*`)** alongside OP6's
  `ap*` (apbtfw/apnv) and `cr*` (crbtfw/crnv) families. Of the OP6 set, the six
  fleet files still show 29-device rows; the four sibling variants (apbtfw11, apnv11,
  crbtfw21, crnv21) remain 0-row device-specific builds `[F]` (matches
  `qca-bt-format.md`).
- **Same filename, different content elsewhere:** Samsung Tab S7 (LTE/WiFi) and
  Galaxy S20 FE carry `htnv20.bin` at 5,950 B, md5 `993c5274…d5603` — a different
  NVM variant; no other-device rows exist for the four OnePlus-8 ht* md5s `[F]`.
- Public linux-firmware ships `htbtfw20.tlv`/`htnv20.bin` for WCN399x (Ubuntu/Fedora
  package file lists; kernel `btqca` has a WCN3998 ROM-version fix naming this file
  pair) — chip attribution `WCN3998 → ht*` is public knowledge `[F]`; **md5 identity
  of the OnePlus-8 copies vs upstream not checked** (local snapshot contains only the
  ap/cr six; upstream copies are .zst/.xz) `[N]`.

### 2.3 Container parses (committed `qca_tlv_parse.py` + direct field dump)

Patches (outer type 1, `len_check` true):

| field | htbtfw10.tlv | htbtfw20.tlv | OP6 apbtfw10 (ref) |
|---|---|---|---|
| total_size | 129,928 | 205,800 | 55,792 |
| data_length | 129,892 | 205,764 | 55,768 |
| total − data | **36** | **36** | 24 |
| format_version | 1 | 1 | 1 |
| signature | **0** | **0** | 2 |
| download_mode | 3 | 3 | 3 |
| product_id | **16** | **16** | 10 |
| rom_build | 0x0100 | 0x0200 | 0x0200 |
| patch_version | 0x1050 | 0x4509 | 2 |
| entry word | 0x0 | 0x0 | 0x1b0e0 |
| tail after total | **32 B** | **32 B** | 256 B |

- `rom_build` still equals the filename suffix (same filename↔header identity rule as
  the ap/cr families) `[F]`.
- The ht* generation changed the patch envelope: 36-B header (24 in ap/cr), 32-B tail
  (256 B), signature 0 (2), product_id 16 (10), entry word 0 (0x1b0e0) `[F]`.
  The exact ht* header field layout (words at +24/+28/+32) is **not decoded** `[N]`.
- Both ht* patch streams begin (after the 36-B header) with `…f8 b5 …` — the same
  ARM-Thumb-consistent push pattern documented for apbtfw10; observed pattern only,
  ISA unconfirmed (same caveat as the OP6 draft) `[F pattern, I interpretation]`.

NVM (outer type **2** — a direct tag set, vs OP6's outer type-4 envelope wrapping
type-2 + type-3 sets):

- htnv10.bin: 35 tags, walk closes exactly at EOF; htnv20.bin: 51 tags, exact close
  `[F]`.
- Both start with tag `0x0002` (EDL_TAG_ID_BD_ADDR, len 6), value
  `ad5a00000000` — identical placeholder in both files (OP6 files carry
  per-file addresses like `200000108039`) `[F]`.
- Tag-ID overlap with the OP6 fleet's 64 distinct (set-type, tag) pairs: **38**; 14
  tag IDs are new to this generation (up to `0xc5`) `[F]`.
- Full `(tag_id, len)` streams in the JSON; the 12-byte tag header
  (id, len, 8 zero bytes) matches the OP6 grammar exactly `[F]`.

**Bottom line:** the OnePlus 8 BT bring-up surface is the same container technology
family as OP6 (btqca TLV patch + NVM tags) but a distinct chip-family file set with a
newer patch envelope and a mostly-shared NVM tag dictionary; **no file is shared
byte-for-byte across the two devices** `[F]`.

---

## 3. larry bdwlan tag 19 — a stride-14 regdb-class country table, not an extended tag-8 `[F]`

### 3.1 Walk and placement `[F]`

All three files (`bdwlan.bin`, `bdwlan_in.bin`, `bdwlan_us.bin`, 26,328 B,
`odm/etc/wifi/`) walk header-to-EOF cleanly with 19 sequential IEs (tags 1..19),
`Σ(4+len) = 26,328`. Tag 19 spans abs **[19,152, 26,328)** in all three — it begins
exactly at the OP6 file size (19,152): the SM6375 layout = OP6 tail re-chunk
(tags 16/17/18 = 516/1,532/68, the b38-style partition totalling the same 2,120 B)
plus a 7,176-B tag 19 appended `[F]`.

### 3.2 Cross-file variability: no signal `[N]`

**The tag-19 payload is byte-identical across bin/in/us** (0 differing bytes, equal
md5s). The OP6 variable-offset-indicator method therefore has nothing to fit —
phase-fit for candidate strides 20/28/40/44 returns var_count = 0 `[N]`. Per-board
calibration deltas live in tags 1–8 as in OP6; tag 19 is generation-constant, not
board-constant-or-variable calibration `[F]`.

### 3.3 Internal structure: stride-14 record table with the regdb marker `[F]`

With cross-file variability unavailable, the lab's internal-structure probes were
used instead (nonzero-indicator autocorrelation + recurring-marker stride analysis,
the regdb method of `gpu-bdwlan.md` §6):

- **Nonzero-indicator autocorrelation peaks at lag 28** (0.735) with the whole
  28-family up (70: 0.716, 14: 0.707, 42: 0.680, 56: 0.641) `[F]`.
- **Byte-level marker scan:** u32 `0xa028` occurs **194 times**, consecutive gaps 14
  (×188) and 28 (×5), at a single phase (record byte +6), first at payload 14, last
  at 2,786 `[F]`.
- Table geometry: **199 records × 14 B from payload offset 8** (8 + 199×14 = 2,794),
  each record = 2-letter country code at +0, `0xa028` marker at +6, numeric fields at
  +10/+12 — the **same record shape, stride, marker and +6 offset as
  `regdb.bin`** (larry's 19,348-B regulatory DB: records from abs 6, 189 markers,
  dominant stride 14) `[F]`. CC order matches the official ISO 3166 list:
  AF, AX, AL, DZ, AS, AD, AI, AG, AR, AM … WF, YE, ZW; 198 distinct codes `[F]`.

### 3.4 Content relation to regdb.bin: substantial `[F]`

- **147 of 199 full 14-byte records are byte-identical to larry's regdb.bin
  records** (199 records there as well) `[F]`.
- The 50 differing records differ only in value fields: 40 records differ **only at
  record byte 12**, 5 only at byte 7, 3 at bytes 10–12, 1 at 7+12, 1 (`XA`) at
  10–11 `[F]`.
- Country-set delta vs regdb: tag 19 **adds `CW`** and **drops `AO` and `IR`**
  (policy/ISO update or rule-set change — attribution open `[H]`) `[F]`.

### 3.5 Relation to OP6 tag 8: none `[N]`

- **0 shared nonzero 16-B blocks** between tag 19 and OP6 tag 8 / 9 / 11 / 12 and
  larry's own tag 8 `[N]`.
- Geometry differs: OP6 tag 8 = stride-40 record tables (known); tag 19 = stride-14.
  **Tag 19 is not an extended tag-8** — it is a regdb-class table appended to the
  board-data container `[F]`.
- Method control passed: the same 3-file phase-fit applied to OP6 tag 8 (files 102 /
  105 / CXO) reproduces the known tables — matching `bdwlan-format.md` §4; and
  **larry's own tag 8 autocorrelates at lag 40** (0.846) — the stride-40 geometry
  persists in this generation while tag 19 uses stride 14 `[F]`.

### 3.6 The tail `[2794, 7172)` — unresolved `[N]`

4,378 B, 27.6% nonzero, entropy 2.43; six all-zero 256-B blocks (payload offsets
2,816, 6,144, 6,400, 6,656, 6,912, 7,168); no dominant marker constant; no clean
single-stride table at tested strides 16/20/28/40/44 `[N]`. Mixed 10/16/20-family
periodicity hints at a second table with a different shape — open item.

### 3.7 Correction to prior doc (applied in the same push)

`librephone-blob-research/blob-matrix/desktop/fleet-re/gpu-bdwlan.md` §5.2 described
tag 19 as "payload 100% non-zero, entropy 3.50". Measured: **byte-level nonzero
fraction 0.4099**, entropy 3.501 (confirmed), and **six all-zero 256-B blocks** —
"100% non-zero" is wrong at byte and block level. Corrected in gpu-bdwlan.md §5.2 in
the same push (file owner = same agent session).

---

## 4. Honest negatives (summary)

1. No Hexagon disassembler available; bm2n ISA verdicts are statistical + string
   provenance, never byte-decoded `[N]`.
2. No ELF magic and no matched public container signature for the bm2n
   `0xFA0000FA` header family `[N]`.
3. No internal block repetition in any bm2n file; matrix aliases are pure content
   identity `[N]`.
4. Zero md5 overlap between OnePlus 8 `ht*` and OP6 `ap*/cr*` BT fleets; local
   linux-firmware snapshot has no ht* copies (upstream check pending) `[N]`.
5. ht* patch header interior (+24/+28/+32 fields) not decoded `[N]`.
6. Tag 19: variable-offset method has no signal (payload identical across all three
   larry files) `[N]`; zero shared blocks vs OP6 tag 8/9/11/12 and larry tag 8 `[N]`.
7. Tag 19 tail [2794, 7172) has no clean table at the tested strides `[N]`.
8. No REGDB file in the OP6 modem FAT — no OP6-side regdb comparison possible `[N]`.

## 5. Open items

- Decode the bm2n loader header (size-class words, `0xFA0000FA`, `0x10400`,
  per-file words 11–15) against the BitML/NSP loader; obtain a Hexagon disassembler
  and byte-verify the ISA verdicts.
- Attribute bm2n08's packed islands (compressed weights vs encrypted section).
- Check linux-firmware upstream md5s for htbtfw10/20.tlv + htnv10/20.bin vs the
  OnePlus-8 payload copies.
- Decode the ht* 36-B patch header and the 32-B tail role.
- Decode the tag-19 tail (4,378 B, mixed 10/16/20-family periodicity).
- Confirm the CW add / AO+IR remove against qcacld regulatory rule builds.

## 6. Reproduction

```sh
python3 -I analysis/tools/bm2n_isa_probe2.py /tmp/bm2n-parts/bm2n.json
python3 -I analysis/tools/bm2n_isa_probe3.py /tmp/bm2n-parts/bm2n3.json
python3 -I analysis/tools/bt_fleet_join2.py  /tmp/bm2n-parts/bt.json
python3 -I librephone-blob-research/blob-matrix/desktop/tools/qca_tlv_parse.py \
    /tmp/bm2n-parts/bt-tlv.json data-fetch/second-device/instantnoodle/bt-fat/*
python3 -I analysis/tools/tag19_geometry.py  /tmp/bm2n-parts/tag19.json
python3 -I analysis/tools/tag19_regdb_compare.py /tmp/bm2n-parts/tag19regdb.json
python3 -I analysis/tools/bm2n_isa_bt_merge.py
```

Machine-readable output: `analysis/out/bm2n-isa-bt.json`.
