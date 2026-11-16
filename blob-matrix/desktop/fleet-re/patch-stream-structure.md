# QCA BT ROM-patch files — 256-byte tail + patch-stream structure (OnePlus 6 / enchilada)

**Evidence classes:** `[F]` fact (directly measured) · `[I]` inference (strong, derived from
measurements) · `[H]` hypothesis (plausible, unverified) · `[N]` honest negative (probed, not found).

**Source:** `data-fetch/enchilada/bt-fat/` — `APBTFW10.TLV` (56,052 B, rom 0x0200),
`APBTFW11.TLV` (216,372 B, 0x0201), `CRBTFW11.TLV` (29,368 B, 0x0101), `CRBTFW20.TLV`
(56,180 B, 0x0200), `CRBTFW21.TLV` (217,676 B, 0x0201). Machine-readable companion:
`analysis/out/patch-stream-structure.json` (regenerable byte-identically with
`python3 -I analysis/tools/patch_stream_structure.py data-fetch/enchilada/bt-fat
analysis/out/patch-stream-structure.json`). Discipline: offsets/lengths/hashes and ≤16-byte
hex samples only; no payload committed.

**Layout recap (per `blob-matrix/desktop/fleet-re/qca-bt-format.md`):** 4-byte outer
`type_len` (type 1) → 24-byte patch struct → `data_length`-byte stream (abs offset 28) →
256-byte tail. Re-verified here 5/5: `len == 4 + total_size + 256 == 28 + data_length + 256`
and `total_size == data_length + 24` `[F]`.

**Header recheck (Rule 1 correction):** the local artifact `analysis/out/qca-bt-tlv.json`
records `entry: "0x80000002"` for the patch files — a u32 misread at offset 20
(patch_version 0x0002 | reserved2 0x8000<<16). The actual u32 at offset 24 is
`e0 b0 01 00` / `e4 09 02 00` / `5c b1 01 00` = **0x1b0e0 / 0x209e4 / 0x1b15c**, matching
qca-bt-format.md's table and the committed parser (`blob-matrix/desktop/tools/qca_tlv_parse.py`
reads entry@24 correctly) `[F]`. The stale JSON predates that fix; regenerate it or patch the
field when the repo copy is next touched.

---

## 1. The 256-byte tail — verdict: per-file-unique high-entropy block, signature/attestation-like `[F]`

Every tail byte-compared pairwise across all 10 file pairs, plus per-file structure tests:

| test | result |
|---|---|
| entropy (bits/byte) | 7.129 – 7.203 (5/5) |
| distinct byte values | 157 / 160 / 157 / 158 / 163 of 256 |
| zero fraction | 0 – 0.0117 (expected 0.0039 for uniform bytes) |
| max count of any single byte value | 4 – 5 (expected ~4–6 for 256 iid uniform bytes) |
| stride periodicity (k = 4, 8, 16, 32, 64, 128) | match fraction 0 – 0.016 — at/below chance; **no repeating stride** |
| repeated 4-byte LE words inside a tail | **0** in all 5 tails (64 aligned words, all distinct) |
| 4-byte words shared between any two tails | **0** of 320 distinct aligned words |
| pairwise byte differences | 254–256 of 256 differ on **all 10 pairs**; common prefix 0, common suffix 0; 0/16 identical 16-byte rows on every pair |
| same-ROM cross-family pair (apbtfw10 vs crbtfw20) | 256/256 bytes differ — **completely** |
| same-family cross-ROM pairs (crbtfw20 vs crbtfw21, crbtfw11 vs crbtfw20/21) | 254/256 differ |
| tail vs 24-byte patch-struct prefix / outer 4 bytes | not equal (5/5) |
| tail head-16 present in own stream | 0 hits (5/5) |
| tail == sha256/md5/sha1 of stream (or struct+stream, or outer+stream) | **no** (full and first-16 comparisons, 5/5) `[N]` |
| any 4-byte word == rom_build or entry (u32 and u16 LE patterns, all values) | **0 hits in all tails** |

Interpretation:

- The distinct-value counts, zero fractions and max-value counts match the statistics of 256
  uniformly random bytes (expected distinct ≈ 162; observed 157–163) `[I]`.
- No internal structure at any tested granularity: no repeats, no stride, no shared words even
  between the two 2.0-family files whose patch streams are 98.3% identical (§3). The tail is
  unique per file even when the payload it follows is near-identical `[F]`.
- Not a digest of the stream under any simple construction (sha256/md5/sha1, raw/with-header)
  `[N]`; not a header copy, not zero padding.
- **Verdict:** attestation/signature/hash-material-like per-file block. "Table" and "padded
  header" hypotheses are refuted; "signature/attestation" is the only surviving class, with
  the exact construction still unknown (open item §7).

## 2. Patch-stream composition — flat dense image, no zero-run framing `[F]`

Per-stream facts (stream = bytes 28..28+data_length):

| stream | len | zero frac | zero runs ≥16 B | longest | dup 16-B block values | max nonzero mult | longest repeated substring |
|---|---|---|---|---|---|---|---|
| apbtfw10 | 55,768 | 0.088 | 3 | 45 | 14 | ×4 | 79 |
| apbtfw11 | 216,088 | 0.0885 | 14 | 284 | 31 | ×7 | 97 |
| crbtfw11 | 29,084 | 0.087 | 2 | 25 | 1 | ×3 | 46 |
| crbtfw20 | 55,896 | 0.088 | 3 | 42 | 14 | ×4 | 79 |
| crbtfw21 | 217,392 | 0.0885 | 15 | 284 | 32 | ×7 | 97 |

- Zero fraction ~8.8% with all 256 byte values present and per-4-KB entropy 4.4–7.0 bits —
  code-like density everywhere `[F]`.
- **Long zero runs are essentially absent from the body** (2–15 runs ≥16 B in files of
  29–217 KB). The few that exist cluster in the **last ~3 KB** of each stream (e.g. apbtfw10:
  runs at 55348/45, 55394/42, 55698/26 — the final 420 bytes; apbtfw11: 284-byte run at
  214704 of a last-3-KB cluster) — end-of-image padding-like, not block separators
  `[F]`. The "zero runs as record/block separators" framing hypothesis is **refuted** `[N]`.
- Duplicate 16-B blocks are rare (1–32 duplicated values per stream, mostly ×2; the ×39/×37
  multiplicities are the zero tail blocks). Longest repeated substrings are 46–97 bytes.
  Two notable repeats: an **80-byte run of byte 0x66** near the stream end (apbtfw10
  55032–55111; crbtfw20 55160–55239 — exactly +128 apart, matching the pair's offset shift,
  §3), and a **46-byte nonzero span duplicated at stream offsets 2974 and 10262** in
  crbtfw11 — the only mid-body duplicate found `[F]`. Role unknown (open item §7).

## 3. Same-ROM pair apbtfw10 vs crbtfw20 (delta exactly 128) — near-identical builds, offset shift +128

Byte-exact diff (difflib, autojunk off) of the two streams `[F]`:

| property | value |
|---|---|
| common prefix (after 24-B header) | **214 bytes** |
| common suffix | **0** (final byte differs — every stream ends uniquely, all 6 pairs §5) |
| equal bytes | 54,749 (98.33% of the longer stream) |
| edit sites | 524 replaces (765 a-bytes / 899 b-bytes), 7 inserts (34 B), 10 deletes (40 B); net +134+34−40 = **+128 ✓** |
| largest single insert | 24 B at b-stream offset 24000 |
| largest single delete | 16 B at a-stream offset 24653 |
| opcode offset alignment | insert/replace sites spread over all mod-16 classes; the few ≥16-B inserts are 16-aligned |

Drift profile (b-offset − a-offset at each edit boundary, per 4-KB region) `[F]`:

| a-offset region | drift |
|---|---|
| 0 – 20,480 | **0** throughout (221 length-neutral edit sites) |
| 20,480 – 24,576 | rises 0 → **128** (the 23.7–24.7K edit cluster) |
| 24,576 – 55,288 | **exactly 128** throughout (equal spans up to 2,879 B) |
| 55,288 – end | ±3–8 wobble, resolving so final drift = 128 ✓ |

**Insertion-point answer:** the extra 128 bytes do **not** sit in one insertion block. They
accumulate inside one localized region (a-side ≈ 23,668–24,674), as a cluster of small
inserts/deletes/replaces (largest 24 B), while the remaining ~500 scattered 1–2-byte edits
are length-neutral. Before the region the streams are byte-identical positionally; after it
they are byte-identical at a constant +128 shift — one firmware built twice with a ~128-byte
larger section in the cr variant `[I]`. Corroboration: the rom_build u32 literal sits at
stream offset 24267 (apbtfw10) vs 24395 (crbtfw20) = +128, and again at 54335/54463 = +128 `[F]`.

## 4. Same-ROM pair apbtfw11 vs crbtfw21 (delta 1,304) — same generation, substantially different builds

16-byte block-anchored diff with byte-level edge refinement (byte-exact difflib is
quadratic-risk at 216 KB) `[F]`:

| property | value |
|---|---|
| common prefix | **176 bytes** |
| common suffix | 0 |
| bytes in ≥16-B exact-match spans | 44,278 ≈ **20.5%** of the stream |
| opcode totals | 426 replaces (171,634 / 172,762 B), **2 inserts** (64 B @ b216384, 112 B @ b217024 — both 16-aligned, both in the final ~1.5 KB), 0 deletes |
| largest replace | a35392, 23,004 → 23,052 B |

Alignment is **not stable**: block-level drift oscillates in the front region (0–24 K), is
locally flat at ~544–576 through ~60–118 K, then wanders to ~1300 `[F]`. Independent anchors
agree with a slowly growing shift: the rom_build 0x0200 u32 literals sit at 62087 (apbtfw11)
vs 62631 (crbtfw21) = **+544**, and at 212291 vs 213591 = **+1300**; the end-of-stream
zero-run skeleton (284/88/81/57/50-byte runs) corresponds at +1300 … +1308 `[F]`.

**Insertion-point answer:** no single insertion block. The +1304 accumulates across the
stream (front-heavy: ~+300 by 16 K, +544 by 62 K, +1300 by 212 K), only two discrete pure
inserts exist (64 + 112 = 176 B, both at the very end, 16-aligned), and ~80% of bytes differ
in place — the two 2.1-family files are substantially different builds of the same-generation
patch that nevertheless keep a parallel section layout `[I]`.

## 5. Cross-generation context pairs `[F]`

| pair | delta | common prefix | bytes in ≥16-B equal spans | similarity |
|---|---|---|---|---|
| crbtfw11 vs crbtfw20 (same family) | +26,812 | 2 | 4,605 | 8.2% |
| crbtfw11 vs apbtfw10 | +26,684 | 2 | 4,574 | 8.2% |
| apbtfw10 vs apbtfw11 (same family) | +160,320 | 2 | 487 | 0.23% |
| crbtfw20 vs crbtfw21 (same family) | +161,496 | 2 | 483 | 0.22% |

Different ROM generations share essentially nothing beyond the first 2 stream bytes — the
"flat image" is per-generation content. Every one of the 6 pairs has **common suffix 0**:
each stream ends with a byte unique to that file — weak but consistent hint of a per-file
end marker/checksum byte (unverified, open item §7).

## 6. Literal entry / rom_build words in the stream `[F]`

- Each stream contains **exactly one** u32 LE equal to its own `entry` value: at stream
  offset 472 (apbtfw10, crbtfw20 — 2.0 gen), 636 (apbtfw11, crbtfw21 — 2.1 gen), 428
  (crbtfw11 — 1.1). Same offset per generation across both families; no other generation's
  entry word appears anywhere. Reads as an early self-reference to the entry address `[I]`.
- rom_build u32 literals: 1–7 scattered hits per stream (e.g. 0x0200 at 24267/54335 in
  apbtfw10 vs 24395/54463 in crbtfw20, both +128; 0x0101 appears 7–8× in the 2.1 files).
  No framing role; the u16 pattern (`00 02` etc.) is too generic to be meaningful
  (9–193 hits).
- Tails: 0 hits for all entry/rom patterns (§1).

## 7. Open items

1. **Tail role** — signature/attestation-class per file (§1); exact construction unknown.
   Next lever: public loader/protocol sources for the post-download 256-byte block (ath3k /
   btusb / Qualcomm QDL docs); digest constructions probed here are all negative.
2. **Trailing byte uniqueness** — every stream's final byte is pairwise-unique (6/6 pairs,
   common suffix 0). Possible end checksum; needs a second fleet sample set to attack.
3. **0x66 × 80 run** near stream end in both 2.0 files (+128 apart); the crbtfw11 46-B
   mid-body duplicate (2974 vs 10262) — unexplained.
4. **2.1 front region** — the first ~24 K hosts the largest replace blocks (incl. one
   23,004-B replace at a35392) and unstable alignment; section boundary semantics unknown.
5. **ISA attribution** — unchanged from qca-bt-format.md (Thumb-consistent byte patterns,
   unconfirmed).
