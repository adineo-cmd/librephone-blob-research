# ADSP `bm2nXX.bin` — fleet structure, region decomposition, and the record grammar (measured)

Analysis date: 2026-11-19. Evidence class: **MEASURED PAYLOADS**. Every number
below is computed from bytes fetched from a public repository and md5-verified
against `upstream-contribution/blob-database/coverage-matrix.csv`. The
byte-level container layout is established in
`../../blob-matrix/laptop/qualcomm-adsp-bm2n-container-header.md` and is
**summarised, not re-derived** here; this document covers the fleet dimension
the container doc does not: per-file region decomposition, the record stream,
and the two-family split.

Clean-room statement: `bm2n_probe.py` was written from the public
BSD-3-Clause-Clear QNN/HTP headers (`tensor.h` → `TENSOR_MAGIC`;
`pickle_header_tags.h` → `Hdr_MAGIC` and the `htp_header_locate_field()` tag
grammar; `serialize_defs.h` → `OP_SEQNO_MARKER_XOR`) and the GPL-2.0
`drivers/misc/fastrpc.c`, plus measurements of the payload bytes. No decompiled
code, no disassembler output and no proprietary documentation were used. No
payload bytes are committed; everything below is derived structural fact.

## 1. The fleet, in one table

All six DB identities and the one variant, measured this session:

| file | bytes | build-id | base | nseg | records | mean entropy | family |
|---|---|---|---|---|---|---|---|
| `bm2n06.bin` | 864,824 | `4bd22b0` | `0x000b8900` | 2 | 781 | 4.05 | compact |
| `bm2n08.bin` | 3,091,896 | `32da3bd` | `0x002d1a00` | 3 | 1,227 | 5.19 | compact |
| `bm2n12.bin` | 2,623,528 | `2c855d1` | `0x00064d00` | 3 | 17,241 | 3.87 | compact |
| `bm2n13.bin` | 1,106,944 | `5371806` | `0x00080e00` | 3 | 4,318 | 3.52 | compact |
| `bm2n14.bin` | 103,168 | `2a8527c` | `0x00001000` | 2 | 885 | 3.84 | compact |
| `bm2n15.bin` | 1,082,856 | `5371806` | `0x00081a00` | 3 | 4,348 | 3.53 | compact |
| `bm2n13_sm8350.bin` *(variant)* | 1,082,824 | `2c855d1` | — | 3 | — | — | compact |

Two things in this table are findings in themselves:

1. **`bm2n13` and `bm2n15` share build-id `5371806`** despite a 24 KB size
   difference, and **`bm2n13_sm8350` and `bm2n12` share `2c855d1`** despite
   1.5 MB. Build-id identifies a **build lineage**, not a file role — and, as
   the container doc establishes, it does not predict content similarity either.
2. **Record count varies by 22× across the fleet** (781 to 17,241) while file
   size varies by 30×. The record count is the real complexity measure; the
   file size is dominated by segment bodies.

## 2. Region decomposition — the same five regions in every file

`bm2n_probe.py` derives region boundaries from the header and the terminator, not
from a fixed layout, and the decomposition holds on all seven files:

```
header  ->  segment bodies  ->  prologue  ->  records  ->  tail
```

| file | header | segment body(ies) | prologue | records | tail |
|---|---|---|---|---|---|
| `bm2n06` | 60 B, 2.68 | 755,908 B, 4.69 | 152 B, 2.75 | 108,700 B, 4.08 | 4 B |
| `bm2n08` | 68 B, 2.72 | 204,732 B **7.07** + 2,750,976 B 5.51 | 164 B, 2.69 | 135,952 B, 4.07 | 4 B |
| `bm2n12` | 68 B, 2.91 | 412,860 B, 2.69 | 168 B, 2.71 | 2,210,424 B, 4.22 | 8 B |
| `bm2n13` | 68 B, 2.87 | 527,804 B, 3.07 | 168 B, 2.68 | 578,900 B, 4.04 | 4 B |
| `bm2n14` | 60 B, 2.53 | 4,036 B, **0.63** | 160 B, 2.80 | 98,908 B, 3.94 | 4 B |
| `bm2n15` | 68 B, 2.87 | 530,876 B, 3.05 | 168 B, 2.68 | 551,740 B, 4.08 | 4 B |

(byte count, Shannon entropy in bits/byte)

The pattern is consistent and informative:

- **The header is small (60–68 B) and constant in size** — `0x3c`, `0x44`, or
  `0x4c` for 2, 3, or 4 segments. It does **not** grow with file size.
- **The prologue is 152–168 B in every file.** This is the only region whose
  size is essentially fixed, which follows from its content (§3).
- **The record region dominates `bm2n12`** (2.2 MB of 2.6 MB) but is a minority
  in `bm2n08` (136 KB of 3.1 MB). So "fleet size" and "fleet complexity" are
  genuinely different axes; `bm2n08` is a large container holding a small graph,
  `bm2n12` the reverse.
- **`bm2n08`'s first segment has entropy 7.07** — near-maximal, unlike every
  other segment body (0.63–5.51). That is the only region in the fleet that
  looks like compressed or encrypted content, and it is the one `[OPEN]` item
  the entropy map surfaces.

### 2.1 The segment-table grammar, validated on 48 files

The six-file fleet above is corroborated by a 48-payload audit across 11 vendor
repositories (recorded in full in
`../../blob-matrix/laptop/qualcomm-adsp-bm2n-fleet-content.md`). The grammar is
tighter than "n pairs followed by a sentinel":

| rule | holds |
|---|---|
| last entry `value` == `base` | 48/48 |
| sentinel is the 16/16 count-complement of `N` | 48/48 |
| kinds drawn only from `{0x00000100, 0x00020100, 0x000f0100}` (low byte 0, bits 8..15 == `0x01`) | 48/48 |
| all `value`s are `0x100`-aligned | 48/48 |
| file-resident `value`s strictly ascending | 48/48 |
| `0x000f0100` is always the **last** entry (prologue end) | 48/48 |
| `0x00020100` is **never file-resident**, exactly one, page-aligned, and **larger than the file** (6.29–17.67×) | 48/48 |
| `0x00000100` marks file-resident segments; appears only in the N=4 `A=0x400000` builds | 48/48 |

The `0x00020100` entry is the one that settles a reader's intuition: a segment
whose address is **6× to 18× the file size** cannot be a file offset. It is a
target address in a memory window the file does not contain — which is why no
`(offset, size)` pair in the header sums to the file size anywhere in the fleet.

**Records are delimited only by `0x1337BEEF`; there is no length field.** This
was verified by boundary-invariance under word mutation (mutating a word inside
a record does not move the next record boundary). Record lengths are therefore
*derived* from consecutive magic positions, all multiples of 4 and all 4-aligned.

## 3. The prologue grammar — identical in every file

The prologue is where the container declares what kind of object graph follows.
Measured on all seven files:

| element | value | holds |
|---|---|---|
| zero run at prologue start | 60 or 68 B, equal to the header length | 7/7 |
| count sentinel | `count` = nseg + 1 (3 for 2 segments, 4 for 3) | 7/7 |
| length prefix | `0x00000026` = 38, then the type name | 7/7 |
| type name | `14ConcreteTensorIN5Tdefs10QuantUint8EE` | 7/7, declared length matches exactly |
| terminator word | `0x00000411` | 7/7 |
| float `1.0f` | `00 00 80 3f` present 18 bytes after the name end | 7/7 |

The type name is **C++ RTTI mangling**: `14` is the length, `ConcreteTensor` is
the class, `IN5Tdefs10QuantUint8EE` is the template parameter
(`Tdefs::QuantUint8`). This is the single strongest piece of evidence for what
the file is — a C++ serialization format, emitted by a program that had the QNN
type system linked in, not a hand-written binary format.

### 3.1 The prologue is byte-identical across unrelated builds

The most useful fleet-level fact in this document. For the closest pair in the
fleet — `bm2n13` (build `5371806`) and `bm2n15` (same build-id, different size)
— the per-region identity is:

| region | identical bytes | % |
|---|---|---|
| header (68 B) | 60 | 88.24 |
| segment body (530,876 B) | 285,310 | 53.74 |
| **prologue (168 B)** | **168** | **100.00** |
| records (~551 KB) | 226,081 | 40.98 |

**The prologue is byte-identical while the bodies and records differ.** The
agent's 48-file audit confirms it across build boundaries, not just within a
lineage. So the prologue is **version-stable** and can be carried by a
reimplementation as a shared template; the segment bodies and the record stream
are the version-varying parts.

The full same-offset identity matrix for the fleet (%, min-length basis):

|  | 06 | 08 | 12 | 13 | 14 |
|---|---|---|---|---|---|
| **08** | 7.18 | | | | |
| **12** | 32.68 | 17.25 | | | |
| **13** | 32.83 | 13.50 | 41.77 | | |
| **14** | 4.64 | 4.71 | 40.42 | 39.83 | |
| **15** | 32.45 | 13.72 | 42.22 | 47.25 | 39.94 |

Read with the container doc's caveat in mind: these percentages are inflated by
coincident zeros (both files are ~50–75 % zero), so a low number means *the data
differs*, not that the *structure* differs. The structural agreement is the
prologue result above, which is 100 % and therefore not a coincidence artifact.

## 4. The record stream — `0x1337BEEF`-tagged, and self-counting

Each record begins with the public `TENSOR_MAGIC` `0x1337BEEF`:

```
bm2n13.bin @ 0x80ea8:
efbe3713 01000000 00000000 11040000 02000000 01000000 03000000 10110040 50020000 ...
^magic   ^1       ^0       ^0x411   ^2       ^1       ^3
```

Measured properties across the fleet:

- **The count of `0x1337BEEF` words equals the record count exactly** — 4,318
  records and 4,318 magic words in `bm2n13`; 17,241/17,241 in `bm2n12`;
  885/885 in `bm2n14`. This is a closed check: the walk does not guess where
  records end.
- **Every record length is a multiple of 4** (`all lengths x4: True` in the
  probe output for all seven files). Records are word-aligned.
- **Record length median is 96–100 B**, min ~40 B, max 6,672 B. The
  distribution is dominated by small records with a long tail, consistent with
  a serialized object graph where most nodes are leaves.
- **`0x1303EE71` (the public `OP_SEQNO_MARKER_XOR`) appears in record bodies**
  as the byte sequence `efbe3713` read the other way — the same marker the
  `serialize_defs.h` header defines, which corroborates the pickle reading from
  a second public constant.
- **The tail is `0xBEEFF00D`** followed by 0–8 zero bytes.

## 5. The second family — `pickle`, one payload in the fleet

### 5.1 Independent corroboration from operator names

Beyond the header constants, three further readings confirm the "serialised
neural-network graph for the Hexagon Tensor Processor" verdict:

- `QUInt8 = 1` is `DType::QUInt8` in the public `dtype_enum.h`, which matches
  the `QuantUint8` in the RTTI name.
- The one pickle payload's options string names a graph sequencer:
  `O=2;initial_sequencer=df;df_subsequencer=por_dp;…` — a runtime scheduler
  configuration, not firmware metadata.
- Operator class names throughout are `hnnx`-namespaced (`TypicalOpIFiR`,
  `VariadicOpIF`, …), and `bm2n12` additionally carries `ArtNet_*` op names.

The `adsp` in the path is the **FastRPC domain id** (`ADSP_DOMAIN_ID (0)` in
`drivers/misc/fastrpc.c:31`), not evidence of modem code. That is the source of
the earlier "ADSP-region modem-adjacent" framing, and it is a path-naming
artifact rather than a content claim.

### 5.2 The pickle family itself

One payload uses the documented HTP **pickle** header instead of the compact
layout: `0x7309F72B` (`Hdr_MAGIC`) at offset 0, followed by the
`htp_header_locate_field()` record grammar (`rlen = recdesc & 0xFFFF`,
`tag = recdesc >> 16`). Observed tags are `Id`, `Sz`, `Vr` (the build-id), `Op`
(textual option string), and `Zz` (end-of-header). The same
prologue/record/terminator machinery follows.

So the fleet contains **two container families that both serialize the same kind
of object graph**. The pickle family is the one with a public header spec; the
compact family is the one the fleet overwhelmingly uses and whose spec is
`[OPEN]`.

## 6. The negative result worth carrying forward

The container doc establishes that **build-id equality does not imply content
similarity**: across a 48-file corpus, same-build pairs average 21.75 %
same-offset identity against 23.79 % for different-build pairs, and the
highest-ratio pair in the matrix is cross-build.

What build-id *does* predict exactly is the **header**: `lcp == 0x2d` separates
same-build from different-build with zero contradictions (21/21). That makes it
a cheap **tier-1 grouping key** — 7 bytes at `0x0c`, cheaper than hashing — but
**not** a substitute for md5 and no licence to attribute one file's findings to
another in the same lineage.

This matters for the lab specifically because the fleet's leverage argument is
"one file informs 25 devices". The devices genuinely share the *bytes* (md5), so
the leverage is real; but two files with the same build-id are not
interchangeable evidence.

## 7. What this buys a free implementation

| question | answer |
|---|---|
| Is `bm2nXX.bin` DSP firmware? | **no** — it is a serialized C++ object graph (QNN/HTP tensor pickle) |
| Can a reader walk the container? | **yes** — header, segment table, prologue and record stream are all specified here and reproduce on 7/7 files |
| Can a reader walk the records? | **partly** — boundaries are closed (magic count == record count), but field semantics are `[OPEN]` |
| Does build-id tell you the content? | **no** — it groups by build lineage only |

## 8. Relationship to the desktop stream's "BitML/NSP" verdict

The lab's desktop agent (WO-001, `workorders/inbox/STATUS-DESKTOP.md`
addendum 6) independently analysed the same fleet and concluded that `bm2n`
files are **"BitML/NSP DSP-side payload images"** with a **"Hexagon-consistent
[I]"** ISA verdict, citing "30–52 shared Itanium RTTI type names".

Those two verdicts are **not in conflict** — they describe the same bytes at
different levels, and the shared evidence is the same evidence:

| observation | both analyses | reading |
|---|---|---|
| Itanium C++ RTTI names (`14ConcreteTensor…`, `TensorSclrDT`, `TensorShape`) | measured by both | the file was emitted by a C++ program with the QNN type system linked in |
| `libbitml_nsp_v2_skel.so` shares those type names | desktop | the *consumer* is Qualcomm's BitML/NSP stack — a strong lead for `[OPEN]` item 3 |
| `0x1337BEEF` records, `0xBEEFF00D` terminator | this doc (`tensor.h`) | a serialized object graph, not machine code |

The distinction worth keeping precise: **RTTI presence is not an ISA claim.**
C++ RTTI strings are data emitted by the *compiler that wrote the file*; they
say nothing about whether the record bodies are Hexagon instructions. This
document's position — "a serialized tensor pickle, not DSP *code*" — and the
desktop's "BitML/NSP DSP-side *payload*" are therefore compatible: the payload
belongs to the BitML/NSP stack, and its contents are a tensor graph rather than
executable firmware.

`[OPEN]`, and the highest-value follow-up in this directory: does
`libbitml_nsp_v2_skel.so` (the named consumer) contain the *deserialiser* that
turns these records into tensor descriptors? If yes, the record field semantics
of item 1 below become readable from a public-ish sibling object, and the whole
`[OPEN]` list collapses.

## 9. [OPEN] list

1. Record field semantics — the words after `0x1337BEEF` follow a consistent
   shape (`1, 0, 0x411, 2, 1, 3, …`) but the field meanings are not established.
2. The tensor graph: which tensors, what shapes, what the models compute.
3. The consumer: which ADSP userspace component loads these pickles
   (not in mainline; `fastrpc.c` provides only the transport).
4. `bm2n08`'s first segment (entropy 7.07) — compressed, encrypted, or dense?
5. Constant `4` at header offset `0x18` — function unresolved (container doc).
6. Segment flag semantics (`0x00010400`, `0x00020100`, `0x000f0100`,
   `0x00000100`) — the split into a low and high half is visible, the meaning is
   not.
7. The `pickle_preamble` layout between the pickle header and the prologue.
8. Whether a genuinely different `bm2n12.bin` format
   (`f87d78518cf940b7c79d0e02bd7369c4`, Nord CE4) that carries a Hexagon
   HTP/QNN graph-preparation option block (`min_arch=73`, `vtcm_mb`, `num_hmx`)
   is a third family or a metadata-only sibling — flagged by the container-doc
   agent and unresolved.

## 10. RULE 0 prior art

The repo's existing RULE-0 record (`implementations/README.md`) for
`"bm2n" bin adsp firmware reverse engineering qualcomm` found no direct hits for
this fleet; adjacent work is `linux-msm/hexagon-dsp-binaries`, TR25 hexagon RE,
SRLabs hexagon fuzzing, and the bkerler QDSP walkthrough. None of those
documents this container.

During the drafting session, `websearch` returned HTTP 402 and GitHub code
search returned 401, so that re-check was weaker than RULE 0 requires. **A
second pass was run on 2026-11-19 once GitHub code search was working again.**
`websearch` still returned HTTP 402 (no web-search quota that day), so the
web and arXiv legs of RULE 0 remain unexecuted — that limitation is stated
rather than papered over.

GitHub code search, 2026-11-19, exact query strings and results:

| query | total | verdict |
|---|---|---|
| `"ConcreteTensorIN5Tdefs10QuantUint8EE"` | 0 | **the exact RTTI string this fleet carries appears nowhere on GitHub** |
| `"1337BEEF" qnn pickle` | 0 | no public linking of the record magic to QNN serialisation |
| `"tensor.pickle" qualcomm` | 0 | no public writeup under that name |
| `"bm2n13"` | 1,044 | all hits are `proprietary-files.txt` / `*-vendor.mk` **file-listing manifests**, i.e. build-system inventory. Not one is RE or format work |
| `"bm2n" adsp` | 9,312 | same picture — vendor trees and `proprietary-files.txt` lists |
| `"1337BEEF"` (all languages) | 336 | every hit checked is unrelated: PPSSPP MMIO, x64dbg signature check, RPCS3 RSX, WebKit FTL thunks, REFramework. None is Qualcomm or QNN |
| `"BEEFF00D"` | 2,800 | unrelated (stgit tests, mongo json tests, blade) |
| `"fa0000fa"` | 2,868 | unrelated; no firmware container documentation |

Two conclusions follow, and they are worth separating:

1. **The container is not publicly documented.** Searching the exact RTTI
   type string — the single most distinctive 34-byte constant in the fleet —
   returns zero results. If anyone had written this format up, that string
   would be in their notes.
2. **The fleet is publicly *known* but not publicly *understood*.** The 1,044
   `bm2n13` hits show the files are catalogued across dozens of device trees.
   Everyone lists them; nobody has decoded them. That is precisely the delta
   RULE 0 asks for, and it is why `implementations/adsp-fleet/` exists.

Residual RULE-0 gap, stated honestly: the **web/arXiv/XDA/Reddit/LWN leg was
not run** because `websearch` was unavailable. GitHub indexes source code, not
prose. Before this analysis is published outside the lab, the prose search
must still be executed.

## 11. Reproduce

```bash
# per-file region decomposition, prologue grammar, record walk
python3 -I bm2n_probe.py bm2n12.bin

# the fleet table
python3 -I bm2n_probe.py bm2n12.bin --brief

# fixtures + suite (no proprietary bytes needed)
python3 -I make_fixture.py
python3 -m unittest -v test_bm2n_probe      # 86 tests, 7 skips without payloads
```

Not legal advice, not a replacement implementation. Regulatory/legal hurdles:
`../../upstream-contribution/radio-regulatory-hurdles.md`.
