# WCN3990 `bdwlan.*` board-data container — format analysis (OnePlus 6 / enchilada)

**Evidence classes:** `[F]` fact (directly measured on the files) · `[I]` inference
(strong, derived from measurements) · `[H]` hypothesis (plausible, unverified) ·
`[N]` honest negative (probed, not found).

**Source:** OnePlus 6 (enchilada) `modem.img` → FAT16 volume → `IMAGE/BDWLAN.*`
directory entries. Extracted with
`librephone-blob-research/blob-matrix/desktop/tools/fat_extract.py` to
`/tmp/modem-fat3`. Machine-readable companion:
`analysis/out/bdwlan-variants.json` (md5 clusters, full RLE variability map,
per-IE stats, aligned cluster/pair diffs, entropy blocks, strings).

**Count correction (2026-11-17):** the fleet contains **35** `BDWLAN.*` files,
not 37 as stated in `docs/devices/oneplus6/wifi.md`. Verified twice:
the extractor emits 35 files, and an independent raw FAT directory walk
(including deleted entries — there are **0** deleted entries) finds exactly 35
`IMAGE/BDWLAN.*` entries in consecutive clusters 7240..7308. The same doc's
"403 files" is also stale (raw walk: 404 entries).

---

## 1. Fleet overview `[F]`

| property | value |
|---|---|
| file count | 35 (`.102 .104 .105 .106 .107 .108 .109 .b04 .b07 .b09 .b0a .b0b .b0d .b0e .b0f .b14 .b15 .b30 .b31 .b32 .b33 .b34 .b35 .b36 .b37 .b38 .b3d .b3f .bin .cxo .qor .t0a .t0b .t1a .t1b`) |
| size | 19,152 bytes (0x4AD0) — identical for all 35 |
| md5 clusters | **29** distinct contents; 6 duplicate pairs |
| duplicate pairs | `b07==b30`, `b0d==b31`, `b09==b33`, `b0e==b32` (first-pass known) **+ `107==109`, `b35==b37` (new)** |
| variable bytes | 4,199 / 19,152 (22.0%) differ from the per-offset fleet majority |
| max differ count | 31 of 34 non-majority files |
| common prefix | 10 bytes |
| common suffix | last 71 bytes (≥ last 64 bytes are constant zero) |

The files are per-board-ID variants of one template: same container, same IE
skeleton, calibration payloads diverging by cluster.

## 2. Container format — RESOLVED `[F]`

The file is a **flat TLV chain with no outer header and no magic**:

```
IE := { u16 LE tag , u16 LE len , u8 payload[len] }   repeated back-to-back to EOF
```

Measured properties:

- All 35 files walk header-to-EOF cleanly under this grammar (`[F]`, all 35).
- 34 of 35 files carry exactly **17 IEs with strictly sequential tags 1..17**;
  one file (`b38`) carries **18 IEs** (tags 1..18, see §6).
- `Σ (4 + len)` over the chain = **19,152** exactly, on every file `[F]`.
- Tag values are strictly ascending with no duplicates — the tag is an
  enumeration (section/parameter ID), not a stream type marker `[I]`.
- Inside the first IE payload, a u16 LE at absolute offset [8,10) equals
  **19152** — the total file size self-reference, present in all 35 files `[F]`.
- No nested TLV evidence: the only payloads that parse as nested `{u16,u16}`
  chains are all-zero payloads (an artifact: zero-filled space parses as an
  infinite `(0,0)` TLV chain). Content-bearing payloads do **not** parse as
  nested TLVs at 4-byte granularity `[N]`.
- No ASCII magic anywhere (see §7) `[N]`.

This is *not* the public ath10k `board-2.bin` grammar (which uses 32-bit
`{id,len}` IEs and an ASCII name IE) — it is a distinct, simpler container
`[F vs public]`. Consumer attribution: WCN3990 board data is passed to the WLAN
firmware via the SNOC platform path (ath10k/cnss); the firmware, not the
driver, parses this TLV stream `[H]`.

### IE map (34-file common layout; ranges are IE spans, payload = span[4:])

| tag | len | abs span [header start, IE end) | entropy (bits/B, `bin`) | var offsets | var spans | classification |
|---|---|---|---|---|---|---|
| 1 | 1028 | [0, 1032) | 0.51 | 98 | 42 | header/config; holds file-size self-ref; **per-board ID fields at abs [10,12) and [408,410)** (§5) |
| 2 | 292 | [1032, 1328) | 0.43 | 12 | 10 | sparse config |
| 3 | 484 | [1328, 1816) | 0.00 | 37 | 5 | **optional**: zeroed in 25/35; populated in `b07,b0d,b0e,b14,b15,b30,b31,b32,cxo,qor` |
| 4 | 1028 | [1816, 2848) | 0.00 | 19 | 11 | mostly zero; populated in 33/35 |
| 5 | 656 | [2848, 3508) | 0.12 | 10 | 5 | sparse config |
| 6 | 636 | [3508, 4148) | 0.00 | 0 | 0 | **pure padding** (all-zero in all 35) |
| 7 | 280 | [4148, 4432) | 0.86 | 37 | 7 | small config |
| 8 | 4932 | [4432, 9368) | 1.57 | 2648 | 86 | **main calibration IE** — 63% of all fleet variability; contains the stride-40 record tables (§4) |
| 9 | 920 | [9368, 10292) | 2.79 | 238 | 17 | densest IE (only region approaching 4+ bits/byte) |
| 10 | 928 | [10292, 11224) | 0.93 | 0 | 0 | **constant across all variants** but non-zero content — fixed config |
| 11 | 1028 | [11224, 12256) | 2.14 | 446 | 3 | calibration; variability concentrated in 3 spans (one 357-byte contiguous) |
| 12 | 3432 | [12256, 15692) | 2.22 | 305 | 26 | calibration; 9- and 14-byte record patterns (§4) |
| 13 | 44 | [15692, 15740) | 0.90 | 30 | 10 | **stride-4 table**: 10 records × 4 B, bytes [0,3) of each record vary (§4); populated in 21/35 |
| 14 | 260 | [15740, 16004) | 0.00 | 181 | 43 | **optional**: zeroed in `bin` + 25 others; populated in `105,106,b38,cxo,qor,t0a,t0b,t1a,t1b` |
| 15 | 1016 | [16004, 17024) | 1.51 | 40 | 24 | sparse calibration |
| 16 | 2052 | [17024, 19080) | 0.00 | 96 | 12 | mostly-zero tail IE with a small non-zero island ([17032,17148)) in 16/35 files |
| 17 | 68 | [19080, 19152) | 0.00 | 0 | 0 | all-zero padding in all 34 |
| 18 | 68 | [19080, 19152) | 0.00 | — | — | exists **only in b38** (§6), all-zero |

## 3. Variability map `[F]`

- Raw-offset full RLE (2671 runs) and the differ-count histogram are in the
  JSON. 14,953 offsets are invariant; of the 4,199 variable offsets, 950 differ
  in 2–5 files, 645 in 6–13 files, and the bulk (2,604, 62%) in 14–31 files —
  i.e. most variable bytes are fields where a majority of boards disagree, not
  one-off outliers.
- Differences are **not** confined to one contiguous span: merging variable
  offsets with a 64-byte gap tolerance yields **28 disjoint variable regions**
  spread over 12 different IEs:

```
[10,96) [352,488) [1041,1105) [1185,1249) [1444,1593) [1842,1896) [2097,2156)
[2856,2861) [3000,3010) [4158,4226) [4441,5566) [6137,8398) [9376,9711)
[10040,10091) [10188,10199) [11232,11351) [11488,11845) [12372,12399)
[12540,12637) [12920,12956) [13388,13451) [13756,13848) [14180,14268)
[14532,14596) [15700,16228) [17027,17148) [17544,17548) [19080,19081)
```

- Alignment caveat: tags 1–15 have identical lengths in all 35 files, so the
  raw map is alignment-clean for [0, 17024). The trailing region [17024, 19152)
  is re-chunked in `b38` (§6), which contributes the last two micro-spans.
- 48.7% of variable offsets in [0,17024) have all 35 values within ±64 of the
  majority byte (small signed corrections); the rest include larger jumps,
  consistent with multi-byte LE fields `[I]`.

## 4. Record structure inside the IEs `[F]`

The variability map exposes fixed-stride record tables (strides measured on the
variable-offset indicator, phases relative to table start, not file start):

| table | abs range | IE | record size | records | variable part |
|---|---|---|---|---|---|
| A | [5166, 5566) | tag 8 | 40 B | 10 | exactly record bytes [10,40) — **300/300** variable offsets fit the phase |
| B | [7798, 8398) | tag 8 | 40 B | 15 | exactly record bytes [10,40) — **450/450** fit |
| C | [7124, 7442) | tag 8 | 40 B | ~8 | 2 variable bytes per record, at offsets ≡ 2,3 (mod 40) |
| D | [15700, 15740) | tag 13 | 4 B | 10 | first 3 bytes of each record vary, byte 3 constant |

Additional stride signals: constant 0x3C-heavy runs at **stride 9**
([12920,12956), tag 12) and **stride 14** ([12372,12399) etc., tag 12) indicate
further 9/14-byte record tables where one field is fleet-constant `[I]`.

Plain byte autocorrelation on the raw file does **not** show sharp peaks
(0.806 @40 vs 0.866 @1) because the file is ~85–94% zero everywhere; the
variable-offset indicator is the right lens here `[N on autocorr]`.

## 5. What distinguishes the clusters `[F]`

Reference: file `102` is byte-identical to the per-offset fleet majority at
every offset (0 diffs), i.e. it *is* the consensus template.

1. **Per-board discriminator field.** A u16 LE at abs [10,12) (tag-1 payload
   bytes [6,8)) takes **28 distinct values across the 29 clusters** and is
   invariant within each cluster (including the 6 duplicate pairs). Hypothesis:
   board ID / board config selector. It does **not** equal the filename number
   under decimal or hex interpretations (0/28) — semantics unknown `[H]`.
   A second field, u16 LE at abs [408,410) (tag-1 payload [404,406)), takes only
   **3 distinct values** across the fleet — a coarse selector (e.g. region/SKU
   class) `[H]`.
2. **Minimal-diff pairs prove the template model.** Distinct md5 clusters that
   differ from each other in only a handful of bytes:
   - `107` vs `108`: **2 bytes** (abs 11 and 27, both tag-1 payload)
   - `b35` vs `b36`: **2 bytes** (abs 10 and 408, both tag-1 payload)
   - `b07` vs `b0d`: **4 bytes** (abs [10,12) + [408,410))
   So adjacent board IDs frequently share one calibration body and differ only
   in the ID/selector fields.
3. **Calibration deltas of widely varying size.** Aligned per-IE diff counts vs
   `102` range from 701 bytes (`105`, `106`) through ~1.4–2.7 KB (`bin`, `b15`,
   `104`, …) to ~3.3 KB (`cxo`, `qor`, `t*`); `b38` adds the §6 re-chunking on
   top. Diffs are distributed across tags: e.g. `105` = tag8:432, tag14:102,
   tag16:45, tag11:27, tag9:25, tag13:30, tag1:35; `107` = tag8:1725,
   tag11:416, tag9:185, tag16:73. Full 29×29 aligned pairwise matrix and
   per-cluster span lists are in the JSON.
4. **Optional-IE population pattern.** Which of the mostly-zero IEs (3, 13, 14,
   16) carry non-zero payload is cluster-correlated (see IE map), suggesting
   per-board feature/tuning options rather than uniform templates `[I]`.

## 6. `b38` — the one structural outlier `[F]`

`b38` re-partitions the trailing zero region into different IEs while keeping
the total at 19,152:

| IE | common files | b38 |
|---|---|---|
| tag 16 | len 2052 | len **516** |
| tag 17 | len 68 | len **1532** |
| tag 18 | absent | **len 68** (new) |

The non-zero island [17032,17148) stays inside tag 16 in both layouts; the rest
of the moved space is zeros. Effects: raw-offset maps beyond 17024 are shifted
for `b38` (its last IE header lands at [19080,19084) with tag byte differing —
hence the 1-byte "variability" at abs 19080), and aligned-by-tag comparisons
must be used for the tail (the JSON does this).

## 7. ASCII strings `[N]`

All ≥6-char printable runs extracted from all 35 files:

- **1,261 distinct runs** — none is real text. Every run is a coincidental
  sequence of bytes in the 0x20–0x3C range, i.e. small numeric calibration
  values that happen to be printable (these are *not* strings; per lab rules
  their bytes are not reproduced here).
- **10 runs are constant across all 35 files** (the longest structure-relevant
  ones are the stride-9 and stride-14 `<`-runs inside tag 12, plus repeating
  2-value patterns inside tag 9). These are byte-value patterns, not strings.
- **No alphabetic metadata exists**: no version banner, board name, build ID,
  or magic string anywhere `[N]`. Board identity lives only in the FAT filename
  and (presumably) the binary ID field of §5.

## 8. Entropy map (256-byte blocks, file `bin`) `[F]`

- mean **0.909**, min ≈ 0, max **5.108** bits/byte — no block comes anywhere
  near dense/random (8 bits); the entire file is sparse/structured.
- Only 5 blocks exceed 3.0 bits/byte, all inside known calibration islands:
  4352 and 6144 (tag 8 islands; 6144 = the [6137,7124) island is the densest),
  7424 (tag 8), 9472 (tag 9), 12288 (tag 12).
- Per-IE entropies in §2 table; full 75-block list in the JSON.

## 9. Checksum `[N]`

No checksum or CRC field identified:

- The last ≥64 bytes are byte-identical (all-zero) in all 35 variants — a
  constant tail cannot encode a per-file checksum.
- crc32/adler32/sum16/sum32/xor-accumulators over `file[:-L]` for L ∈
  {2,4,8,16,64} match no stored tail value in any file (earlier "hits" were
  trivial zero==zero matches) `[N]`.
- Curiosity: the XOR of **all** file bytes is 0x00 in every one of the 35
  files. With thousands of differing bytes per variant this is structural
  (byte-value parity symmetry of the table content), not a stored field `[I]`.

## 10. Open items

- Decode the tag enumeration 1..17 (needs a Qualcomm BDF tool/spec or firmware
  strings; tag semantics unknown).
- Confirm the §5 ID field hypothesis against the loader (cnss/firmware board-ID
  selection) — the value does not match the filename number directly, so either
  it is a different namespace or it is not the ID at all.
- Field semantics inside the big IEs (8/9/11/12): record tables A–D have clear
  geometry but unknown field meaning; tag 14's stride-4-per-2-byte pattern
  ([15748,16002), 43 spans) looks like another per-record table.
- Explain the optional-IE population pattern (which clusters populate tags
  3/13/14/16) against feature flags/regs databases.
- `105|106` differ in 652 bytes yet are the closest large-delta pair; whether
  they are two markets of one board is unresolved.

## 11. Reproduction

```sh
python3 -I librephone-blob-research/blob-matrix/desktop/tools/fat_extract.py \
    data-fetch/enchilada/modem.img /tmp/modem-fat3
python3 -I analysis/tools/bdwlan_probe.py  /tmp/modem-fat3 analysis/out/bdwlan-variants.json
python3 -I analysis/tools/bdwlan_tlv_probe.py /tmp/modem-fat3
python3 -I analysis/tools/bdwlan_final.py  /tmp/modem-fat3 analysis/out/bdwlan-variants.json
```

Scripts (lab-rule compliant: no payload bytes printed, offsets/hashes/maps
only): `analysis/tools/bdwlan_probe.py`, `analysis/tools/bdwlan_tlv_probe.py`,
`analysis/tools/bdwlan_final.py`.
