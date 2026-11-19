# Qualcomm ADSP `bm2nXX.bin` — container header, segment table, and a negative result on build-id similarity

Analysis date: 2026-11-18. Evidence class: **MEASURED PAYLOADS** (every number below is computed
from bytes on disk; nothing is copied from a manifest).

Inputs: seven DB-verified payloads in `/tmp/astro_u/payloads/` (the six DB identities plus the
non-DB `bm2n13` revision), cross-validated against 48 further fetched variants in `/tmp/astro_u/hunt/`.
Tooling: `bm2n_container_probe.py` (this directory). Variant inventory: **`qualcomm-adsp-bm2n-variant-matrix.md`**
(sibling agent) — that document owns the md5/source matrix; this one owns the bytes.

Payloads used as the primary fleet, all md5-verified this session against the DB and against the
variant matrix:

| file | bytes | md5 | DB devices |
|---|---|---|---|
| bm2n06.bin | 864,824 | `9010bb1a7c08222a058aaef7edd938c6` | 25 |
| bm2n08.bin | 3,091,896 | `1275a2d212e5bccce734d3055ff10156` | 25 |
| bm2n12.bin | 2,623,528 | `5c86c8fcc7451f51e11d38276253aac8` | 26 |
| bm2n13.bin | 1,106,944 | `bf635d9084b54633526f9ad8a84d299b` | 25 |
| bm2n14.bin | 103,168 | `805176afaae27821520b79647fa5d498` | 26 |
| bm2n15.bin | 1,082,856 | `2ce8163cda60f33cbf2b50f03a3d0ea1` | 26 |
| bm2n13_sm8350.bin *(variant)* | 1,082,824 | `2d267761f3291c9ca4a7850ab0ef1966` | 1 (as `bm2n54.bin`) |

The seventh file is the genuine non-DB revision: its bytes *are* in the DB, but recorded under the
filename `bm2n54.bin` on `nothing/Pong` (variant matrix, notes to Table 2).

---

## 1. The container is now specified — 48/48 files, five invariants

The head of every `bm2nXX.bin` is a **little-endian load-header followed by a segment table**. All
five structural rules below hold on **48/48** distinct-or-duplicate container files (12 distinct
payloads, 48 files) and on **7/7** of the primary fleet. None of them is documented publicly as far
as this session's search reached (see §6).

| offset | width | field | evidence |
|---|---|---|---|
| `0x00` | u32 | **load base** | one of `0x200000`/`0x400000`/`0x800000`; repeated at `0x1c`; equals `segment[0].addr` |
| `0x04` | u32 | reserved | `0` in 48/48 |
| `0x08` | u32 | **build-id string length** | equals `strlen()` of the string at `0x0c` in 48/48 |
| `0x0c` | char[8] | **build-id**, ASCII, NUL-terminated | 7 hex chars + NUL in 48/48 |
| `0x14` | u32 | **magic `0xfa0000fa`** | 48/48 |
| `0x18` | u32 | constant `4` | 48/48; function unresolved |
| `0x1c` | u32 | load base (repeat of `0x00`) | 48/48 |
| `0x20` | u32 | **segment count** *n* | 2–4 observed |
| `0x24` | (u32 addr, u32 flags) × n | **segment table** | — |
| `0x24+8n` | u32 | **terminator**: `((~n & 0xffff) << 16) \| n` | 48/48, see below |

```
bm2n13.bin, 1,106,944 B
00000000: 0000 2000 0000 0000 0700 0000 3533 3731  .. .........5371
00000010: 3830 3600 fa00 00fa 0400 0000 0000 2000  806........... .
00000020: 0300 0000 0000 2000 0004 0100 0070 ac00  .............p..
00000030: 0001 0200 000e 0800 0001 0f00 0300 fcff  ................
          ^entry[0].addr ^entry[0].flags ^entry[1].addr ^e[1].flags  ^terminator
```

The terminator is self-describing: its low 16 bits repeat the segment count and its high 16 bits are
the count's complement, so `0xfffc0003` = 3 segments, `0xfffd0002` = 2, `0xfffb0004` = 4. It held on
every file including the only 4-segment blob (`bm2n12.bin` on `diting`, `0xfffb0004`). **This is the
"segment-table marker" hypothesis from the brief — confirmed, but it is a per-file terminator whose
value varies with the segment count, not a constant.**

**Segment `addr` fields are LOAD ADDRESSES, not file offsets.** They routinely exceed the file size —
`bm2n13.bin` is 0x10e400 bytes but `segment[1].addr` is `0xac7000`. Any reader treating them as
offsets will overrun. This is why no `(offset, size)` field pair sums to the file size anywhere in the
fleet; the header carries no file-offset table at all.

Segment flags observed, by table position:

| position | flags | count |
|---|---|---|
| entry[0] | `0x00010400` | 12/12 — **always** |
| entry[1] | `0x00020100` | 6 | 
| entry[1] | `0x000f0100` | 5 |
| entry[1] | `0x00000100` | 1 |
| entry[2] | `0x000f0100` | 6 |
| entry[2] | `0x00000100` | 1 |
| entry[3] | `0x000f0100` | 1 |

The flags split cleanly into a `0x0100`/`0x0400`/`0x0200` low half and a `0x0001`/`0x0002`/`0x000f`
high half, consistent with a (permission, type) pair — but the *semantics* are not established by
this data and are not claimed.

---

## 2. Question (b): what `u32[2]==7` and `u32[10]==0x010400` actually are

### `u32[10] == 0x010400` is not a format field — it is `segment[0].flags`

`0x010400` is at byte offset `0x28`, which is the second word of the **first segment-table entry**
(table starts at `0x24`). It is constant across the whole fleet for the same reason every file's first
segment is the same kind of segment: entry[0] is always the load-base/code segment, and its `.addr` is
always the load base at `0x00`. Both of entry[0]'s words are therefore predictable from `0x00`:

```
u32@0x00 == u32@0x1c == segment[0].addr   →  48/48
segment[0].flags == 0x010400              →  48/48 (12/12 distinct payloads)
```

So the constants the brief observed at `u32[2]` and `u32[10]` are **two different things wearing the
same costume**: one is a real header field, the other is data belonging to a substructure that happens
to start at a fixed offset.

If a format-version pair is wanted, the better candidates are `magic == 0xfa0000fa` at `0x14` and the
constant `4` at `0x18`. Both are 48/48 constants that sit *outside* the segment table and belong to no
identified substructure — but neither is confirmed as a version, and `4` is unexplained.

### `u32[2] == 7` is the build-id string length, not "version 7"

`u32[2]` at `0x08` equals `strlen()` of the NUL-terminated string at `0x0c` in 48/48 files. The
alternative reading — a format/build version that happens to equal 7 — **cannot be excluded by this
data**, because every build-id in the entire sampled fleet is exactly 7 characters. Both hypotheses
predict 7 everywhere. Recording this as undecidable rather than picking the tidier story.

Evidence favouring "length": the field is maximally redundant with a string it immediately precedes
(`0x08` then `0x0c`), which is the usual C pattern for a length-prefixed string. Evidence that could
settle it: a single bm2n blob with a build-id of any other length. None has been found — see §6.

---

## 3. Question (a) — NEGATIVE RESULT: the build-id does **not** predict content similarity

This is the headline of the report, and it inverts the brief's hypothesis.

The lead's framing was that build-id identifies a build lineage, and asked whether build-id equality
predicts high same-offset byte identity. Tested directly. The naive number looks encouraging; it does
not survive controls.

### 3.1 The 42.84 % figure reproduces exactly — and it is ~42 % coincident zeros

`bm2n13.bin` (1,106,944 B) vs `bm2n13_sm8350.bin` (1,082,824 B), over the 1,082,824-byte min length:

```
identical bytes = 463,905 / 1,082,824 = 42.842142 %   -> 42.84 %   (lead's figure: CONFIRMED)
  of which coincident zeros : 454,842  (42.01 %)
  of which non-zero agreement:   9,063  ( 0.84 %)
```

Both files are ~61 % zero bytes (60.96 % / 61.13 %). Two files that share nothing but their sparsity
pattern will show ~42 % "identity" by construction. **Non-zero agreement — 0.84 % — is the only part of
that number carrying information.**

### 3.2 Same-build pairs sit *inside* the cross-build range

Primary fleet, all 21 pairs, decomposed. "Same build-id" means the 7-char ids at `0x0c` match.

| pair | build-id | identity | coincident zeros | non-zero agree |
|---|---|---|---|---|
| bm2n13_sm8350 vs bm2n15 | **differs** | **47.25 %** | 44.49 % | 2.76 % |
| bm2n13 vs bm2n13_sm8350 | differs | 42.84 % | 42.01 % | 0.84 % |
| bm2n13 vs bm2n15 | **same `5371806`** | 42.67 % | 41.84 % | 0.83 % |
| bm2n12 vs bm2n15 | differs | 42.22 % | — | 0.79 % |
| bm2n12 vs bm2n13_sm8350 | **same `2c855d1`** | 41.77 % | 40.94 % | 0.83 % |
| … 14 pairs omitted … | | 32–41 % | | 0.3–0.8 % |
| bm2n06 vs bm2n08 | differs | 7.18 % | 6.67 % | 0.51 % |

- The **highest** identity in the whole matrix (47.25 %, and the only pair with elevated non-zero
  agreement at 2.76 %) is a **cross-build** pair.
- The two same-build pairs (42.67 %, 41.77 %) are unremarkable members of the 41–43 % band.
- bm2n13 vs bm2n15 share a build-id and sit *below* bm2n13 vs bm2n13_sm8350, which do not.

Grouped means: same-build **42.22 %** (n=2) vs different-build **28.23 %** (n=19). That gap looks like
signal but is an artifact of the different-build group containing the two tiny/oddly-shaped files
(bm2n06, bm2n14), which have low zero-fraction. Controlling for it with a chance model below removes it.

### 3.3 The chance model removes the effect

Expected same-offset identity under the null "these two bodies are statistically independent" is
`Σ_v p_A(v)·p_B(v)`, computed per pair from each file's own byte histogram. Ratio = measured / chance;
1.0 means the pair is no more similar than its byte histograms predict.

| group | n | measured | chance | ratio (mean) | ratio (max) |
|---|---|---|---|---|---|
| same build-id | 2 | 42.22 % | 35.51 % | **1.19** | 1.24 |
| different build-id | 19 | 28.23 % | 27.43 % | **0.97** | **1.36** |

The best ratio in the entire 7-file matrix (1.36) belongs to a **different-build** pair
(bm2n12 vs bm2n14). The same-build pairs are 1.19 and 1.14 — unremarkable.

### 3.4 The 48-file corpus confirms it, and is harsher

Distinct payloads in `/tmp/astro_u/hunt` (12 containers, 60 pairs):

| group | n pairs | identity mean | non-zero mean | chance mean | ratio mean | ratio max |
|---|---|---|---|---|---|---|
| same build-id | 6 | **21.75 %** | 0.59 % | 20.29 % | 0.99 | 1.37 |
| different build-id | 60 | **23.79 %** | 0.83 % | 22.73 % | 1.01 | **2.54** |

Same-build pairs are, on average, **less** similar than different-build pairs, and the single most
similar pair in the corpus by ratio (2.54) is cross-build. The build-id carries no content-similarity
signal.

Decisive counterexample inside one build lineage: build-id `bab1be8` covers **three** file roles —
`bm2n06.bin` (836,968 B), `bm2n08.bin` (3,059,736 B) and `bm2n12.bin` (1,638,360 B) — and the
bm2n06/bm2n12 pair scores **4.46 %**, the lowest of any same-build pair and the floor of the
same-build group. A second example: `594e022` covers `bm2n08` (3,059,736 B) and `bm2n13`
(1,339,032 B) at **15.44 %**. One build-id demonstrably spans wholly different file roles.

All five same-build pairs in the corpus, for completeness:

| pair | build-id | identity |
|---|---|---|
| bm2n13 / bm2n15 (Moto SM6375, ArrowOS) | `5371806` | 42.67 % |
| bm2n13 / bm2n12 (bheatleyyy, FP5) | `2c855d1` | 41.77 % |
| bm2n08 / bm2n06 (cupid, diting) | `bab1be8` | 20.23 % |
| bm2n08 / bm2n13 (diting, mayfly) | `594e022` | 15.44 % |
| bm2n08 / bm2n12 (cupid, diting) | `bab1be8` | 5.93 % |
| bm2n06 / bm2n12 (diting, diting) | `bab1be8` | 4.46 % |

### 3.5 What build-id equality *does* predict: the header, exactly

Here is the real (and genuinely useful) fleet-structure finding. Longest common prefix from offset 0
separates the fleet **perfectly**:

| lcp | n pairs | all same build-id? | mechanical meaning |
|---|---|---|---|
| `0x2d` (45) | 3 | **yes** | agree through `0x2c` — same base, build-id, *n*, and `segment[0]`; first difference at `segment[1].addr` |
| `0x20` (32) | 2 | **yes** | agree through `0x1f`; first difference at `0x20` = **segment count** |
| `0x0d` (13) | 3 | no | agree through first build-id char; differ at `0x0d` (inside the id) |
| `0x0c` (12) | 13 | no | differ at `0x0c` — first build-id character |
| `0x02` (2) | 45 | no | differ at `0x02` — **different load base** (0x00..0x01 zero for all) |

Every lcp value is **fully explained by the header fields** and nothing else:

- lcp = 2 ⟺ different load base.
- lcp = 12 or 13 ⟺ same load base, different build-id.
- lcp = 32 ⟺ same load base **and** same build-id, different segment count.
- lcp = 45 ⟺ same load base, same build-id, same segment count — first divergence is the second
  segment's address.

So `lcp == 0x2d` is a **perfect predictor of same build-id** (0 contradictions, 21/21 pairs), and
`lcp ≤ 0x1f` a perfect predictor of a different one. But it predicts the header, not the body — and
that is the trap: the identity percentages in §3.2 are inflated by header agreement plus zero
coincidence, both of which track sparse-structure alignment rather than shared code.

**Practical consequence for the lab's leverage argument:** build-id is a safe *tier-1 grouping key*
(it partitions the fleet exactly, and is cheaper to read than a hash — 7 bytes at `0x0c`), but it is
**not** a substitute for md5 and gives no licence to attribute one file's RE findings to another file
in the same lineage. That is the same conclusion the variant matrix reached from the filename side,
now established independently from the byte side.

---

## 4. Question 3: `u32[0]` is a load base, and the "only bm2n06 has 0x400000" premise is a 7-file artifact

### The field cannot be a size

Decisive single counterexample in the wider corpus:

```
v_fp5_bm2n12.bin   u32[0] = 0x00200000   file size = 0x00280828   <- file is 786 KB larger than u32[0]
```

A section or region **size** cannot be smaller than the file it describes. Across 12 distinct payloads
this is the only violation, and one counterexample is enough.

Corroborating evidence that it is an address:

1. It is **duplicated** at `0x1c` (48/48) — headers repeat an address they need, not a size.
2. It **equals `segment[0].addr`** (48/48) — it is literally the first entry of the segment table.
3. All values are page-aligned plausible DSP memory bases: `0x200000`, `0x400000`, `0x800000`.
4. It does **not** track file size monotonically: `bm2n14.bin` (103,168 B) and `bm2n13.bin`
   (1,106,944 B) share base `0x200000`; `v_diting_bm2n15.bin` (1,339,032 B) uses `0x800000`.

### `0x400000` is not unique to bm2n06

The brief's observation was correct for the seven-file fleet and dissolves on the wider sample:

| load base | distinct payloads (48-file corpus) |
|---|---|
| `0x200000` | 5 (`2a8527c`, `2c855d1`×2, `5371806`×2) |
| `0x400000` | 5 (`594e022`/bm2n08, `5da2bda`, `bab1be8`×3) |
| `0x800000` | 2 (`33e15da`, `594e022`/bm2n13) |
`bm2n08` and `bm2n12` also occur at `0x400000` on other device generations. (`bm2n15` does not — it
appears only at `0x200000` and `0x800000`; the earlier claim that it does was wrong and is corrected
here.) There is no build-generation correlation either: `bm2n06`'s build-id `4bd22b0` is unique in the
corpus, so "the only file whose build-id starts with 4" has a sample of one and cannot establish a
trend.

Within a build lineage the load base is *usually* constant (6 of 7 lineages) but **not always**:

```
lineage 594e022:  v_diting_bm2n08.bin  base=0x400000
                  v_mayfly_bm2n13.bin  base=0x800000   <- same build-id, different base
```

So the load base is a **per-build choice recorded in the header**, correlated with but not determined
by the build lineage. It is not a version marker and does not track the filename index either
(`bm2n12` and `bm2n15` each appear with two different bases).

Not forced to a conclusion: whether the base is chosen by the SoC memory map, the linker, or the
packaging tool is **not** settled by these bytes. What is settled is that it is an address, not a size.

---

## 5. Two by-products worth recording

### 5.1 A `bm2n12.bin` in the DB is a completely different file *format*

`f87d78518cf940b7c79d0e02bd7369c4`, 2,359,272 B, DB row `Nord_CE4 / oneplus / bm2n12.bin`
(variant matrix Table 2, the `benz` row). It is **not** the bm2n container:

```
first 32 bytes: 2bf70973 78020100 33004964 00000000 ...
u32@0x00 = 0x7309f72b   (not a load base; magic absent; whole header shape differs)
```

It carries a machine-generated option-string block instead, and the option names identify it:

```
min_arch=73; tile_height=8; vtcm_mb=2; num_hmx=4/8; hvx=8; soc_type=; ...
supertile=0; afterburner=true; largest_memory_alloc_size=1073741824
```

`min_arch=73` (Hexagon v73), `vtcm_mb`, `num_hmx`, `num_hvx` and the `tile`/`crouton` vocabulary are
**Hexagon HTP / QNN graph-preparation context** parameters, not DSP firmware. Flagged as
*strongly-indicated* rather than confirmed — no QNN/HTP header magic was matched.

This sharpens the variant matrix's "filename ≠ identity" thesis beyond what either document claimed
alone: `bm2n12.bin` in the DB does not merely span two builds of one format, it spans **two unrelated
file formats**. A `bm2n12.bin` sweep that hashes without parsing will fold an ML context blob into
DSP-firmware statistics.

### 5.2 The container doubles as a cheap md5 pre-screen

Because `build-id + load-base + segment-count + segment[0..k]` is a near-unique header fingerprint, the
first 0x40 bytes reject most non-matches without hashing: within the corpus, all 12 distinct payloads
have distinct first-0x2d-byte prefixes except the same-build/same-shape pairs, which the build-id
already ties. Useful for triaging large vendor trees; not a replacement for md5 on exact identity.

---

## 6. Honest limitations and failed checks

- **Prior-art search was impaired.** `websearch` returned HTTP 402 and the GitHub code-search API
  returned 401 from this session; the prior-art claim in §1 is therefore weaker than RULE 0 wants.
  In-repo grep (all `*.md`) found no prior header parse: the only `bm2n` docs are metadata tables
  (`qualcomm-adsp-bm2n-fleet.md`, `qualcomm-adsp-bm2n-variant-matrix.md`). **A follow-up session must
  re-run the public prior-art check before this is published.**
- **`u32[2]==7` is undecidable as "length" vs "version"** with current data (§2). Needs a blob with a
  non-7-character build-id.
- **`u32@0x18 == 4` is unexplained.** Constant in 48/48 and belongs to no identified substructure.
- **Segment `flags` semantics are not decoded.** The (low-half, high-half) split is suggestive of
  permission/type but no bit meaning is claimed.
- **Load-base origin is not determined** (§4).
- **One corpus file was empty** (`v_moto7325_bm2n06.bin`, 0 B) — a truncated fetch, consistent with the
  variant matrix's own note that large `gh api` fetches stalled. Excluded, not interpreted.
- **`bm2n13` DB coverage differs from the other five** (25 devices vs 26 for bm2n12/14/15) — the
  variant matrix's Table 1 states 25 for all six; that discrepancy is in *its* table, not re-derived
  here, and is flagged for the lead rather than silently corrected.
- Identity percentages use **min length**, which favours long/short pairs toward the shorter file's
  prefix. The chance model and non-zero decomposition are given precisely so the reader need not
  trust the raw percentage.

---

## 7. Reproduce

```bash
# primary fleet + variant (7 files, all md5-verified in §0 of this doc)
cd /tmp/astro_u/payloads
python3 bm2n_container_probe.py .

# full 48-file cross-validation corpus
python3 bm2n_container_probe.py /tmp/astro_u/hunt

# the specific claims, standalone
python3 - <<'EOF'
import struct
A=open('/tmp/astro_u/payloads/bm2n13.bin','rb').read()
B=open('/tmp/astro_u/payloads/bm2n13_sm8350.bin','rb').read()
n=min(len(A),len(B))
same=sum(1 for i in range(n) if A[i]==B[i])
nz  =sum(1 for i in range(n) if A[i]==B[i] and A[i]!=0)
print(f"identity      {same/n*100:.6f}%   (lead said 42.84%)")
print(f"coincident 0s {sum(1 for i in range(n) if A[i]==B[i]==0)/n*100:.2f}%")
print(f"non-zero agree{nz/n*100:.4f}%")
EOF
```

Expected: `identity 42.842142%`, coincident zeros `42.01 %`, non-zero agreement `0.84 %`.

Header dump for any single file:

```bash
xxd -l 96 bm2n13.bin
```

---

## 8. Answers, in one block

**(a)** No. Build-id equality does **not** predict content similarity; the apparent effect is
zero-coincidence plus header agreement. Same-build pairs score 42.22 % vs 28.23 % raw, but
1.19 vs 0.97 measured/chance, and on the corpus 21.75 % vs 23.79 % — i.e. the sign flips inversely and
the maximum-ratio pair is always cross-build. The lead's 42.84 % is **verified exactly** but decomposes
to 42.01 % coincident zeros + 0.84 % non-zero agreement. Build-id *does* partition the fleet exactly via
`lcp == 0x2d` (perfect, 0 contradictions) — a header fingerprint, not a content fingerprint.

**(b)** `u32[10] == 0x010400` is **`segment[0].flags`** (byte `0x28`, first entry of the table at
`0x24`); it is constant because entry[0] is always the load-base segment. `u32[2] == 7` is the
**build-id string length**, matching `strlen` in 48/48, though "version 7" cannot be excluded because
every sampled build-id is 7 chars. The "segment-table marker" is the table **terminator**
`((~n & 0xffff) << 16) | n`, confirmed 48/48 — it is per-file, not a constant.

**(3)** `u32[0]` is a **load base address**, not a section size: it is duplicated at `0x1c`, equals
`segment[0].addr`, and one payload (`v_fp5_bm2n12.bin`, 0x280828 B) is **larger than** its own
`u32[0] == 0x200000`, which no size field can be. The "only bm2n06 has 0x400000" premise holds only
within these seven files: the wider corpus shows `bm2n08` and `bm2n12` at `0x400000` too, and
`bm2n06`'s build-id is unique, so no build-generation correlation can be measured.
