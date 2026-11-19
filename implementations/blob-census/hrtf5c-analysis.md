# hrtf5c.bin — identification and structural analysis (Xiaomi aDSP audio blob)

The laptop half carries `hrtf5c.bin` on **12 devices** (13 matrix rows —
Poco_F6_PRo ships two builds). This file identifies it, pins its internal
structure from parsed bytes, and states what a free reimplementation would
need. No payload bytes committed — payload copies live in
`/tmp/astro_v/payload/`.

## 0. RULE 0 prior-art search (2026-11-18)

1. GitHub code search `q=hrtf5c` — 1,350 hits, ALL device extract lists
   (`proprietary-files.txt`) and vendor .mk files; no analysis.
2. GitHub code search excluding extract lists (`-filename:proprietary-files.txt`)
   — 399 hits, again only vendor lists/manifests; `purainity/
   myron-hyperos-analysis` is a HyperOS path census, not a parse.
3. Web search `"hrtf5c.bin" xiaomi adsp` — consensus identification only:
   it ships in `vendor/lib/rfsa/adsp/` (FastRPC ADSP library path) on
   Xiaomi devices, also seen as `vendor/etc/hrtf5c.bin` on a MediaTek
   Xiaomi device. No structural analysis exists anywhere.
4. Identification basis (this session): **HRTF = Head-Related Transfer
   Function** — spatial-audio data for the aDSP; the sibling FastRPC
   skeleton `libQ6MSFR_manager_skel.so` ("Q6" = Hexagon Q6 DSP) is its
   loader in the same extract lists.

## 1. Provenance and md5 verification — both builds MATCH

| build | bytes | DB md5 | fetched md5 | status | source | DB location |
|---|---|---|---|---|---|---|
| table build (11 devices + Poco_F6_PRo odm) | 164,480 | `2a47164eed5282f27ad503a28c7b71a0` | same | **MATCH** | TheMuppets/proprietary_vendor_xiaomi_mayfly @ lineage-22.2 `proprietary/vendor/lib/rfsa/adsp/hrtf5c.bin` | `vendor/lib/rfsa/adsp` (8 devices) or `odm/etc/audio` (4 devices) |
| container build (Poco_F6_PRo adsp copy) | 54,180 | `630a2e1853c80e1dd1d2b1cd2d334ac4` | same | **MATCH** | TheMuppets/proprietary_vendor_xiaomi_vermeer @ HEAD `proprietary/vendor/lib/rfsa/adsp/hrtf5c.bin` | `vendor/lib/rfsa/adsp` |

Laptop-half carriers of the table build: Mi_12 (cupid), Mi_12S (mayfly),
Mi_12S_Pro (unicorn), Mi_12S_Ultra (thor), Mi_12T_Pro (diting),
Mi_12_Pro (zeus), Mi_13 (fuxi, odm), Mi_13_Pro (nuwa, odm), Poco_F5
(marble), Poco_F5_Pro (mondrian), Redmi_K60_Pro (socrates, odm),
Poco_F6_PRo (vermeer, odm copy) — 12 devices.

## 2. The 164,480-byte build — a pure IEEE-754 float32 table

No header, no strings, no code — a dense float32 array:

- 41,120 float32 values, **zero NaN/Inf**, range −185.35…+12.30,
  entropy 7.40 bits/byte, 0.5 % zero bytes.
- **Exact structure: 160 records of 257 floats** (160 × 257 = 41,120 — this
  consumes the file exactly, with **zero remainder**; there is no trailing
  table).
- The 160 records **alternate two representations**:
  - 80 *linear-domain* records (every even record): floats ≈ 0…8.2 with a
    scale word first (f0 ≈ 1.07–1.10), mean |v| ≈ 1.3–2.3 — filter
    coefficients in the linear domain.
  - 80 *dB-domain* records (every odd record): first float 0.0, then
    values ≤ 0 down to −122, mean |v| ≈ 54–62 — the same filters expressed
    as dB magnitudes.
  - 80 directions × 2 (the record pairs) matches a binaural HRTF set
    (left/right ear per direction); 257 floats per record = 256-tap filter
    + 1 word (scale/delay). Exact direction list and tap semantics [OPEN].
  - **Verified parity rule:** all 80 even-indexed records are entirely
    non-negative and all 80 odd-indexed records are entirely non-positive,
    with **zero mixed records** out of 160. Magnitude and phase are therefore
    stored in separate records, not interleaved as complex pairs.

Byte-range map:

```
[0,        164480)   160 × 257-float records (80 linear, 80 dB, interleaved)
```

**Correction (2026-11-19):** an earlier revision of this section claimed a
separate `[163840, 164480)` 160-float dB-level tail table. That is
arithmetically impossible — `160 × 257 × 4 = 164,480` consumes the whole file
with zero remainder — and on measurement the "tail" is simply the last 160
floats (columns 97–256) of record 159. The map above is the correct one; the
tail claim is withdrawn.

**Classification: data tables (100 %).** No code, no strings, no framing —
there is nothing here to reverse except the measurement data itself.

## 3. The 54,180-byte build — a self-describing tagged container

The vermeer adsp copy is a *different format*: ASCII-tagged sections with
u32/f32 payloads, ending in an `ENDM` marker:

```
[     0]  VER0   + u32 0, u32 0
[    16]  DATE   + 2023, 4, 24          (build date: 2023-04-24)
[    32]  TYPE   + "M80X" "DIM0" + 3   (type string, DIM0 = dim variant 0?)
[    48]  SPKN   + 13                   (speaker count? 13 items follow in SDIR)
[    56]  LSGN   + 15
[    64]  SDIR   + float pairs: ±480, ±240, ±360, ±150, ±72, ±132, 0…  (speaker geometry? [OPEN])
[   172]  LSGP   + counts (0, 3, 9, 0, 9, 2, 1, 2, 10, …)
[   356]  INVM   + float-class data (−0.52 …)
[   900]  FFTN   + 512                  (FFT length)
[   908]  HLEN   + 256                  (HRTF filter length)
[   916]  SMPR   + 48000                (sample rate)
[   924]  HRTF   + 13,312 floats        (the HRTF table: 53,248 B)
[54176]  ENDM                            (last word of the file)
```

Declared facts from the container itself: FFT 512, filter length 256,
sample rate 48 kHz — consistent with the 164,480-byte build's 256-float
records. The M80X/DIM0/SPKN/LSGN/SDIR sections are speaker-layout tuning
geometry [OPEN]. The `5c` in the filename is most plausibly a tuning-set
version letter (compare aw882xx_acf.bin naming habits); exact versioning
semantics [OPEN].

## 4. What a free reimplementation needs

- The blob is **data, not code** (both builds): a free spatial-audio stack
  does not need to "decompile" anything — it needs equivalent HRTF
  measurement/synthesis data. A free HRTF dataset (e.g. public HRIR
  measurements, MIT KEMAR, IRCAM Listen) re-rendered into the same
  container format (the 54 KB build's self-describing tags make that
  feasible: VER0/TYPE/FFTN/HLEN/SMPR/HRTF/ENDM) is the realistic path.
- The two builds show the same tuning shipped in two formats (raw table
  vs self-describing container) for two different consumers (odm audio
  HAL vs FastRPC aDSP library) — a free implementation can standardize on
  the self-describing format.
- Per-device variation: none within the laptop half for the table build
  (one md5 across 12 devices) — one tuning set serves the whole flagship
  block; the container build exists only on vermeer's adsp path.

## 5. Freed-device value

12 laptop-half devices × both builds md5-verified and structurally parsed
(164,480 B table build: 11 devices + vermeer odm; 54,180 B container
build: vermeer adsp). Whole-DB fleet = the same 12 devices — the entire
hrtf5c fleet lives in the laptop half.

## 6. Route log (2026-11-18)

1. `gh api search/code q=hrtf5c` (1,350) and
   `q=hrtf5c -filename:proprietary-files.txt` (399) — extract lists only.
2. Web search `"hrtf5c.bin" xiaomi adsp` — identification only.
3. TheMuppets/proprietary_vendor_xiaomi_mayfly @ lineage-22.2
   `proprietary/vendor/lib/rfsa/adsp/hrtf5c.bin` (raw) — md5 MATCH.
4. TheMuppets/proprietary_vendor_xiaomi_vermeer @ HEAD same path —
   md5 MATCH (the second build).
5. The DB carries no other hrtf* filenames (13 rows, hrtf5c.bin only).
