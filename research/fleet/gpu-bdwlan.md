# WORKORDER-001 (desktop): Adreno microcode containers, gfp9508, cross-device bdwlan

**Devices:** OnePlus 6 (enchilada, SDM845 — Adreno 630) and OnePlus Nord CE3 (larry,
SM6375 Snapdragon 695 — Adreno 619/615/660 files present).  
**Evidence classes:** `[F]` fact (measured) · `[I]` inference (strong, derived) ·
`[H]` hypothesis (plausible, unverified) · `[N]` honest negative (probed, not found).  
**Companion JSON:** `analysis/out/gpu-bdwlan-analysis.json` (main + merged follow-up;
per-file hashes, ELF tables, pairwise matrices, per-IE maps).  
**Discipline:** no proprietary payload bytes in this document — offsets, sizes,
hashes, structural facts, ≤16-byte hex samples and short ASCII strings only.

---

## 1. Adreno ZAP shader containers (mdt/bNN/elf) `[F]`

All six MDTs (`a630_zap.mdt` OP6; `a615_zap.mdt`, `a660_zap.mdt` larry) parse as
ELF32, little-endian, `e_type=2` (ET_EXEC), **`e_machine=164` (EM_QDSP6)**,
`e_entry=0x5000`, `e_flags=3`, 3 program headers, 0 section headers.

Segment geometry is identical across all three families:

| phdr | type | vaddr | memsz | file (split) | OP6 a630 | larry a615 | larry a660 |
|---|---|---|---|---|---|---|---|
| 0 | PT_NULL | 0 | 0 | `.b00` | 148 | 148 | 148 |
| 1 | PT_NULL | 0x6000 | 8192 | `.b01` | 6536 | 6560 | 6560 |
| 2 | PT_LOAD | 0x5000 (= e_entry) | =filesz | `.b02` | 1968 | 1984 | 1976 |

- `.b00` = 148 B = ELF header (52) + phdr table (3×32) exactly, in every family `[F]`.
- `mdt = b00-content + b01-content` concatenated (mdt − 148 = b01 size; verified all
  three families: 6684/6708/6708) `[F]`.
- The `.elf` file is the **page-aligned image variant of the same content**: phdr1
  payload at file offset 4096, phdr2 at 12288; both payloads are byte-identical to
  `.b01`/`.b02` (`b01_in_elf`, `b02_in_elf` true, exact find offsets) `[F]`.
  Size check: 148 + pad→4096 + b01 + pad→12288 + b02 = elf size exactly (a630:
  14256) `[F]`.
- Every `p_filesz` matches its `.bNN` size in all families `[F]`.
- Pairwise mdt equality: a630 vs a615 = 688/1671 words equal (common prefix 100 B);
  a630 vs a660 = 686/1671 — same container/ISA layout, different shader payloads `[F]`.
- All 7 OP6 GPU files match `analysis/out/enchilada-census.csv` sha256+size;
  all 14 larry GPU files match `analysis/out/second-device-census.csv` `[F]`.

## 2. GMU / SQE microcode containers across generations

### 2.1 a630 (OP6) vs a619 (larry) — same container generation `[F]`

| property | a630_gmu.bin | a619_gmu.bin |
|---|---|---|
| bytes | 32768 | 32768 |
| entropy | 3.871 | 3.867 |
| head hex16 | `803f0400 09000000 054880f3 08880548` | identical |
| nonzero frac (first 4 KiB) | 0.737 | 0.738 |
| alpha strings ≥6 | 26 | 26 (incl. the shared RTOS string `SIGABRT: Abnormal termination` at 1588) |

- Common prefix **1076 bytes**, 59% of u32 words equal over the full 32 KiB
  (4844/8192) — same firmware skeleton, different build `[F]`.
- Diffs concentrate in [1076, 16384) (two large merged regions [2748,12000) and
  [12018,16106) at gap-16 merge); **[16386, 32768) is byte-identical except 2 bytes**
  — the second half of the 32 KiB image is generation-invariant `[F]`.

### 2.2 a660 (larry) — a different container generation `[F]`

- 55,256 B, entropy 6.46, **common prefix with a630/a619 = 0 bytes**; ~0% words equal.
- Head (8 u32-LE pairs): `(0,0), (1,0x1dc), (0x4000,0), (1,0xd4cc), (0x200,0),
  (1,0x3a64), (0x100000,0), (1,0x85b4)` — a zero block, then a table-like pattern.
  **Update 2026-11-19: this leading table is DECODED as the mainline
  `struct block_header` prealloc-request TOC** (11 zero-size requests fitting
  mainline's hardcoded a660 allocations + 4 DEADBEEF-tagged data blocks routed
  ITCM/icache/DTCM) — full decode in [qsee-crossgen.md](qsee-crossgen.md) §5 `[F]`.
- Non-zero density ≈0.87–0.92 through offset 49152, then 0.161 / 0.019 — trailing
  padding region `[F]`. 170 alphabetic strings (vs 26) — denser code, RS64-era build `[I]`.
- No ASCII banner/version string identified in any gmu file beyond the RTOS crash
  string `[N]`.

### 2.3 SQE files `[F]`

| file | bytes | entropy | head hex16 |
|---|---|---|---|
| OP6 a630_sqe.fw | 32136 | 3.79 (ent in JSON) | `…` (in JSON) |
| larry a630_sqe.fw | 32456 | — | first 4 bytes equal to OP6's |
| larry a660_sqe.fw | 40496 | — | first 4 bytes equal to both |

- All three share **exactly a 4-byte common prefix** (one u32 word) and 15/16
  non-zero words in the first 64 B — raw instruction streams, no header `[F]`.
- OP6 a630_sqe vs larry a630_sqe: +320 B delta but **not an insert-only patch**
  (common prefix 4, common suffix 43, 23,680 differing bytes ≈ 74% of the smaller
  file) — two builds of the same a630-generation SQE `[F]`.
- a660 sqe vs a630 sqe: 0.6–0.7% words equal — different generation `[F]`.
- No version/count word and no ASCII metadata in any sqe (`[N]`; the two string-like
  runs in a630 sqe are coincidental printable byte patterns).

### 2.4 Cross-generation header signature `[N]`

There is **no common gmu header magic across generations**: a630/a619 begin with
instruction words; a660 begins with a zero block and the (now-decoded) prealloc TOC.
No meaningful shared version/count word found `[N]`. Generation identity is carried
by the filename, not an in-file version field (probed: first 64 B words, string
table, fleet md5 set).

## 3. Fleet identity (md5 cross-check vs coverage-matrix.csv) `[F]`

| on-disk file | md5 | verdict | db rows (devices) |
|---|---|---|---|
| OP6 a630_gmu.bin | `1ade6a659713…` | **PROVEN fleet blob** | a630_gmu.bin: 8 devices (OnePlus 7/7T/7T Pro/7 Pro, Mi A3, Galaxy A71, Redmi Note 8, Z5 Pro GT) |
| OP6 a630_sqe.fw | `d172aac301b0…` | **PROVEN fleet blob** | a630_sqe.fw (32136 B variant): 1 device (Redmi Note 7 Pro) |
| larry a619_gmu.bin | `9e23c52057bb…` | **PROVEN fleet blob** | a619_gmu.bin: 24 devices (Pixel 4A 5G/5/5A, Moto G200/G34/G84/Stylus, Edge 20/30/30 Neo/Fusion, FP4, Xperia 5 II/5 III/1 II, Nord 200/CE2/CE3, Realme 9 Pro/10 Pro, G Stylus 2022, Edge 2021, Moto G 5G 2024) |
| larry a630_sqe.fw | `21693ef6f2d6…` | **PROVEN fleet blob** | a630_sqe.fw (32456 B variant): 19 devices |
| larry a660_gmu.bin | `179caf2e3b7d…` | **PROVEN fleet blob** | a660_gmu.bin: 19 devices |
| larry a660_sqe.fw | `08b7662ccd68…` | **PROVEN fleet blob** | a660_sqe.fw (40496 B variant): 21 devices |
| all 10 zap files (OP6 a630 ×5, larry a615 ×5 + a660 ×5 = 15) | — | **NOT IN DB** | coverage-matrix.csv contains no `*zap*` rows at all |

- The DB's a630_sqe.fw splits into 7 md5 variants (32136/32264/32272/32304/32448/
  32456/32504) — the filename is fleet-shared but the content is SoC-vendor-build
  specific; same for a660_gmu (55252/55256/53672) and a660_sqe (40496/43068) `[F]`.
- `a615_gmu.bin`, `a615_sqe.fw`, `a619_sqe.fw` have **no rows** in the DB `[N]`
  — the SM6375 generation ships `a619_gmu.bin` + `a630_sqe.fw` (naming is
  chip-generation-scoped, not device-scoped) `[I]`.

**Bottom line:** every gmu/sqe file on disk (both devices) is byte-identical to a
fleet-wide blob carried by 1–24 devices; the ZAP shader files could not be checked
against the DB (absent from it).

## 4. gfp9508.* classification (modem.img FAT: IMAGE_GFP9508.*) `[F]`

9 files: `IMAGE_GFP9508.{MDT,B00..B07}` (companion set IMAGE_GFP5288.* also present).

- MDT: ELF32 LE, **`e_machine=40` (EM_ARM)**, `e_type=3` (ET_DYN), `e_entry=0`,
  8 phdrs ↔ 8 `.bNN` segment files `[F]`.
- MDT contains an embedded X.509 chain (short ASCII strings): `QUALCOMM Attestation
  CA`, `SecTools Test User`, `San Diego`, `CDMA Technologies`, validity timestamps
  `211125155130Z`/`211125155136Z` (2021-11-25) `[F]`.
- Segment profile (9508): B00 308 B (header), B01 6,696, B02 2,792,936 (ent 6.49),
  B03 126, B04 4,470,952 (only 5.2% non-zero — sparse), B05 736, B06 152, B07 70,920.
- GFP5288 vs GFP9508: same 9-file structure, same MDT/B00/B01/B05/B06 sizes, but
  **all 18 files have distinct md5s** (zero shared content); B02/B04/B07 differ
  hugely in size (e.g. B04: 4.47 MB vs 0.95 MB) `[F]`.
- Classification: **signed ARM TrustZone (QSEE/PIL) user-app images** — not Hexagon
  DSP code (machine = ARM, e_type = DYN) `[F]`. Attribution of the `GFP` prefix to a
  fingerprint-sensor app (GF-family sensor models 5288/9508) is plausible from naming
  and app-image shape but unverified `[H]`.

## 5. Cross-device bdwlan (larry vs OnePlus 6) — same grammar, new tail

Grammar per `analysis/drafts/bdwlan-format.md`: `IE := {u16 LE tag, u16 LE len, payload[len]}`.

### 5.1 larry's three files parse cleanly `[F]`

`bdwlan.bin`, `bdwlan_in.bin`, `bdwlan_us.bin` (all 26,328 B,
`odm/etc/wifi/`): each walks header-to-EOF cleanly, **19 IEs with strictly
sequential tags 1..19**, `Σ(4+len) = 26328` exactly.

- The u16 LE self-reference at abs [8,10) = **26328** (file size) in all three —
  the same field as OP6's 19152 `[F]`.
- Per-file discriminator u16 LE at abs [10,12): three distinct values across the
  three files (mechanism identical to OP6's 28-values-across-29-clusters field;
  values differ) `[F]`. Second selector at [408,410) = 1 in all three (OP6: 3
  distinct values) `[F]`.

### 5.2 IE skeleton vs OP6 template `[F]`

| tags | lens | comparison to OP6 |
|---|---|---|
| 1–15 | 1028, 292, 484, 1028, 656, 636, 280, 4932, 920, 928, 1028, 3432, 44, 260, 1016 | **byte-length identical to the OP6 34-file layout** |
| 16 | 516 | OP6 common: 2052 — but **exactly the OP6 `b38` outlier's re-chunk** |
| 17 | 1532 | OP6 common: 68 — `b38` uses 1532 |
| 18 | 68 | absent in 34/35 OP6 files; `b38` has it |
| 19 | 7172 | **new IE, absent from the entire OP6 fleet**; payload nonzero fraction 0.4099 with six all-zero 256-B blocks, entropy 3.50. **Update 2026-11-19: tag 19 content is DECODED as a stride-14 regdb-class country table** (199 records × 14 B, 0xA028 marker, 147/199 records byte-identical to larry's regdb.bin, CC set adds CW / drops AO+IR) — full analysis in [bm2n-isa-bt.md](bm2n-isa-bt.md) §3 `[F]` (this doc's earlier "100% non-zero" claim corrected per that measurement) |

So the tail re-partition first seen in OP6's one-off `b38` (16/17/18 = 516/1532/68)
became the standard tail layout on this generation, extended by a large new
regdb-class IE (tag 19) `[I]`.

### 5.3 Per-tag variability vs OP6 consensus (file `102`) `[F]`

Aligned per-tag differing-byte counts (larry `bdwlan.bin` / `_in` / `_us` vs OP6 102):
tag1 66/66/66 · tag2 2/2/2 · **tag3 0/0/0** · tag4 12/3/12 · **tag5 0** · **tag6 0**
· tag7 60/60/60 · tag8 625/642/635 · tag9 91/117/92 · **tag10 0/0/0** · tag11
330/356/347 · tag12 573/473/**105** · tag13 30/30/30 · tag14 104/104/104 · tag15
28/28/28.

- Tags 3, 5, 6, 10 are **byte-identical across both device generations**. Tag 10 was
  already fleet-constant across all 35 OP6 files — it is constant across
  generations too; tags 5/6 are zero-padding there and here `[F]`.
- Tag 12 shows the strongest region selectivity: the `_us` variant differs from the
  OP6 consensus by only 105 bytes while `_in` differs by 473 `[F]`.
- Within larry: bin vs in = 1,428 differing B (350 spans), bin vs us = 1,147 (282),
  in vs us = 1,272 (292); first diffs at [10,12), then [38,39), [62,63), then
  calibration islands inside tag 8 — the same "ID/selector fields + calibration
  delta" model as OP6 `[F]`.

### 5.4 Fleet-identity verdict `[N]`

None of larry's four wifi files matches any of the 29 OP6 md5 clusters (sizes
26,328 vs 19,152 cannot match). Board data is **device/chip-generation specific**;
only the container grammar and the fixed-config IEs are shared across generations.

## 6. regdb.bin — a different container `[F]`

19,348 B, entropy 1.60, md5 `f94fc7f186e6…`.

- **Not the bdwlan TLV grammar**: the LE {u16,u16} walk from offset 0 produces
  nonsense IEs and degenerates into a (0,0) chain after 17152 (558 nominal IEs) `[F]`.
- Actual structure (measured): 6-byte head, then a **fixed-stride 14-byte record
  table from offset 6**. A recurring u32 LE marker `28 a0 00 00` occurs 189 times at
  record offset +6 with dominant stride 14 (179 of 188 consecutive gaps) `[F]`.
- Each record: ISO 3166-1 alpha-2 code + NUL at +0, **the same code repeated** at +3,
  constant u32 0xA028 at +6, two u16 fields at +10/+12. First records: `AF, AX, AL,
  DZ, AS, AD` — the official ISO 3166-1 list order `[F]` (codes are short ASCII,
  reproduced as facts).
- Table extent: last marker at 2770, last uppercase pair at 2781 (~198 records);
  beyond it a sparse region [~2774, 17152) with 1,315 non-zero bytes (structure
  unanalyzed), tail [17152, 19348) all-zero `[F]`.
- Classification: regulatory database (country → rules), structurally unrelated to
  the bdwlan container `[I]`; semantics of the two u16 fields and the 0xA028
  constant unknown `[open]`. **Note 2026-11-19: the same record shape is embedded
  as bdwlan tag 19 in the SM6375 generation — see bm2n-isa-bt.md §3.**

## 7. Honest negatives

1. No cross-generation gmu header signature/magic exists (§2.4) `[N]`.
2. No meaningful shared version word across the three gmu files (only a zero) `[N]`.
3. No zap rows in coverage-matrix.csv — zap fleet identity not checkable `[N]`.
4. a615/a619 gmu+sqe naming absent from the DB (`a619_gmu.bin` is the one gmu that
   exists for this generation) `[N]`.
5. No larry bdwlan/regdb md5 matches any OP6 cluster `[N]`.
6. No ASCII version/banner strings in gmu/sqe beyond the shared RTOS crash string `[N]`.
7. OP6 FAT re-extraction (`/tmp/modem-fat-b`) reproduced all 35 BDWLAN md5s exactly —
   consistent with the previous session's JSON `[F]` (positive, listed as repro check).

## 8. Open items

- Decode the a630 vs a615/a660 zap payload differences (100-byte mdt prefix).
- Confirm the `[10,12)` discriminator semantics (board ID namespace) for larry's
  three values; link to QMI/board-id selection.
- Decode the regdb.bin post-table sparse region and the u16 fields; find the public
  qcacld/qcacmn parser for confirmation.

## 9. Reproduction

```sh
python3 -I librephone-blob-research/blob-matrix/desktop/tools/fat_extract.py \
    data-fetch/enchilada/modem.img /tmp/modem-fat-b
python3 -I analysis/tools/gpu_bdwlan_probe.py
python3 -I analysis/tools/gpu_bdwlan_followup.py
```

Scripts (lab-rule compliant): `analysis/tools/gpu_bdwlan_probe.py`,
`analysis/tools/gpu_bdwlan_followup.py`. Machine-readable outputs:
`analysis/out/gpu-bdwlan-analysis.json` (merged), `analysis/out/gpu-bdwlan-followup.json`.
