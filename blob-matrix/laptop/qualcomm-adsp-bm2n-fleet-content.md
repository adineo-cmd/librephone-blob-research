# Qualcomm ADSP `bm2nNN` fleet — content-level results (laptop half)

Companion to `blob-matrix/laptop/qualcomm-adsp-bm2n-fleet.md`, which is
**metadata-only** (upstream md5/size, no payload RE) and is left untouched.
This file carries what the payload bytes actually contain. Evidence class:
**CONTENT** — real payloads fetched, md5-verified, and structurally parsed.
Full method, provenance and `[OPEN]` list live in
[`implementations/adsp-fleet/bm2n-fleet-analysis.md`](../../implementations/adsp-fleet/bm2n-fleet-analysis.md);
the parser and test suite live in
[`implementations/adsp-fleet/`](../../implementations/adsp-fleet/).

## Scope

Upstream database: 446 `bm2n*` rows, 35 devices, 65 distinct filenames
`bm2n00`–`bm2n71` (non-contiguous), all `blob_family=adsp`, all
`interface_documented=n`.

This work measured **49 payloads** (50 fetched, 1 was 0 bytes) from **11
vendor repositories**, giving **13 distinct md5s** and **8 distinct
build-ids**. Six brief files were md5-verified against the database; the rest
came from public TheMuppets/LineageOS vendor trees. **48 of 48 non-empty
payloads parse clean** under one layout.

The laptop half covers 118 devices. Its six leverage filenames are the same
six as the full database (the half holds one device per filename at the
canonical md5), so the content results below apply to it directly.

## Verdict on the file type

These are **not modem firmware**, despite the earlier "ADSP-region
modem-adjacent" framing in the metadata doc. The evidence is a serialised
neural-network graph for the Hexagon Tensor Processor:

- the record tag is `TENSOR_MAGIC = 0x1337beef` from the public
  `QNN/HTP/core/tensor.h:100`;
- the prologue embeds the C++ RTTI name
  `14ConcreteTensorIN5Tdefs10QuantUint8EE`, and `QUInt8 = 1` is
  `DType::QUInt8` in the public `dtype_enum.h`;
- one payload is a standard HTP **pickle** (`Hdr_MAGIC = 0x7309F72B`) whose
  options string names a graph sequencer:
  `O=2;initial_sequencer=df;df_subsequencer=por_dp;...`;
- operator class names throughout are `hnnx`-namespaced
  (`TypicalOpIFiR`, `VariadicOpIF`, …), and `bm2n12` additionally carries
  `ArtNet_*` op names.

The `adsp` in the path is the FastRPC domain id (`ADSP_DOMAIN_ID (0)` in
`drivers/misc/fastrpc.c:31`), not evidence of modem code.

## The container layout (validated 48/48)

### Compact family

```
0x00 u32  A            window: 0x200000 (26 files) / 0x400000 (11) / 0x800000 (12)
0x04 u32  0            constant 48/48
0x08 u32  7            constant 48/48
0x0c 8B   build-id, 7 ASCII + NUL
0x14 u32  0xfa0000fa   constant 48/48
0x18 u32  4            constant 48/48
0x1c u32  A            repeat of 0x00
0x20 u32  N            segment-table pair count (2/3/4)
0x24 u32  A            repeat of 0x00
0x28 u32  0x10400      constant 48/48
0x2c      (N-1) x { u32 value, u32 kind }
          sentinel { ((~N & 0xffff) << 16) | N , base }
hlen = 0x2c + 8*N      => 0x3c / 0x44 / 0x4c      48/48
```

Region order: header → segment bodies (boundaries = ascending file-resident
table values, last = `base`) → prologue → `0x1337BEEF` records →
`0xBEEFF00D` terminator → 0–8 pad bytes (all-zero or all-`0x55`).

**Segment-table grammar (48/48):** last entry `value` == `base`; sentinel is
the 16/16 count-complement of `N`; kinds only from
{`0x00000100`, `0x00020100`, `0x000f0100`} (low byte 0, bits 8..15 == `0x01`);
all values `0x100`-aligned; resident values strictly ascending; `0x000f0100`
always last (prologue end); `0x00020100` never file-resident, exactly one,
page-aligned, always **larger than the file** (6.29–17.67×); `0x00000100`
marks file-resident segments and appears only in the N=4 `A=0x400000`
builds.

**Prologue (48/48):** `hlen` bytes of zero padding (absent → run of 0 in some
`A=0x400000`/`0x800000` builds), then `count_complement(N+1)`, `1`, a small
word, `38`, the 38-byte type name
`14ConcreteTensorIN5Tdefs10QuantUint8EE`, 2 pad bytes, then 9–11 u32 fields
always including `0x00000411` and `1.0f`. The header sentinel counts `N`; the
prologue sentinel counts `N+1`.

**Records:** delimited only by `0x1337BEEF`; no length field (verified by
boundary-invariance under word mutation); lengths all multiples of 4; offsets
all 4-aligned.

### Pickle family

1 of 49. Standard HTP pickle: `0x7309F72B` at 0, header word count in word 1,
tags `Id`/`Sz`/`Vr`/`Op`/`Zz` by the documented
`htp_header_locate_field()` grammar, then the same prologue/record/
terminator machinery. The preamble between header and prologue is `[OPEN]`.

## Per-file content summary (the six brief payloads)

| brief file | bytes | build-id | N | base | records | DB identity |
|---|---|---|---|---|---|---|
| `bm2n06.bin` | 864,824 | `4bd22b0` | 2 | 0x000b8900 | 781 | `bm2n06.bin` |
| `bm2n08.bin` | 3,091,896 | `32da3bd` | 3 | 0x002d1a00 | 1,227 | `bm2n08.bin` |
| `bm2n12.bin` | 2,623,528 | `2c855d1` | 3 | 0x00064d00 | 17,241 | `bm2n12.bin` |
| `bm2n13_sm8350.bin` | 1,082,824 | `2c855d1` | 3 | 0x00081a00 | 4,348 | **`bm2n54.bin`** |
| `bm2n14.bin` | 103,168 | `2a8527c` | 2 | 0x00001000 | 885 | `bm2n14.bin` |
| `bm2n15.bin` | 1,082,856 | `5371806` | 3 | 0x00081a00 | 4,348 | `bm2n15.bin` |

All six pass the probe with zero structural violations.

## Fleet-diff matrix (same-offset byte identity, %)

|  | 06 | 08 | 12 | 13 | 14 |
|---|---|---|---|---|---|
| **08** | 7.18 | | | | |
| **12** | 32.68 | 17.25 | | | |
| **13** | 32.83 | 13.50 | 41.77 | | |
| **14** | 4.64 | 4.71 | 40.42 | 39.83 | |
| **15** | 32.45 | 13.72 | 42.22 | 47.25 | 39.94 |

Low percentages mean the *data* differs, not that the structure differs. The
per-region breakdown for the closest pair (bm2n13 vs bm2n15) is the important
one:

| region | identical | % |
|---|---|---|
| header (68 B) | 60 | 88.24 |
| body (530,876 B) | 285,310 | 53.74 |
| **prologue (168 B)** | **168** | **100.00** |
| records (~551 KB) | 226,081 | 40.98 |

**The prologue is byte-identical across two unrelated builds.** It is
version-stable; the bodies and records are version-varying. For a
reimplementation this means the prologue can be carried as a shared template.

## Filename is not identity (F-75, confirmed at scale)

16 of the 65 DB filenames carry more than one md5, and single md5s span many
filenames. Highlights:

| md5 | bytes | filenames |
|---|---|---|
| `bf635d9084b54633526f9ad8a84d299b` | 1,106,944 | 14 names incl. `bm2n13.bin`, `v_pong_bm2n54.bin` |
| `2d267761f3291c9ca4a7850ab0ef1966` | 1,082,824 | 5 names incl. `v_pong_bm2n54.bin` |
| `281755c08b98e757f00586d0052132b1` | 1,339,032 | 7 names incl. `bm2n14`/`bm2n15`/`bm2n16` |
| `5c86c8fcc7451f51e11d38276253aac8` | 2,623,528 | 3 names incl. `bm2n12` |
| `2ce8163cda60f33cbf2b50f03a3d0ea1` | 1,082,856 | 2 names incl. `bm2n15` |

Notably `281755c0…` serves three DB filename slots at once, and
`bm2n14.bin` in the DB has two entirely different payloads (103,168 B and
1,339,032 B).

The brief's `bm2n13_sm8350.bin` (`2d267761…`) is DB-canonical **`bm2n54.bin`**,
not DB `bm2n13.bin` (`bf635d90…`). It is a genuine non-DB-identical variant,
not a fetch failure, and it parses clean under the same layout — the variant
differs in content, not structure.

## Entropy shape

64 KiB-block entropy separates the files: bm2n06 has long near-zero stretches
(0.35–0.4 bits/byte) consistent with large zeroed bodies and low records; bm2n08
reaches 7.56 bits/byte in its body; bm2n12/13/15 sit around 3.5–4.0 mean.
Nothing hits 8.0 uniformly, so these are structured data, not encrypted or
compressed containers — consistent with the record stream being walkable.

## What a reimplementation can and cannot do

**Can build now, zero proprietary bytes:** family detection (including the
documented pickle magic), the compact header and its five constants, the
segment table with its full invariant set, the prologue grammar (and its
byte-identical template), and the record/terminator framing.

**Cannot yet:** decode record payload semantics, the three `kind` values, the
window field `A`, `0xBEEFF00D`'s origin, the prologue's 9–11 scalar fields,
the pickle preamble, the sequence-number field's meaning, or anything at
instruction level.

See the analysis doc's §10 for the complete `[OPEN]` list, and
`implementations/adsp-fleet/README.md` for tool usage and the 86-test status.
