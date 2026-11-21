# Qualcomm data blob fleet — `hrtf5c.bin` + `dax_param.bin` (laptop half)

Phase 2 (WORKORDER-002-laptop) — evidence class: **MEASURED PAYLOADS**.
Full analysis: [`implementations/data-blob-fleet/data-blob-analysis.md`](../../implementations/data-blob-fleet/data-blob-analysis.md).
Analyser + tests: [`implementations/data-blob-fleet/`](../../implementations/data-blob-fleet/).

Two blobs in the laptop half were taken past metadata to real content:
`hrtf5c.bin` (an ADSP audio blob, 12 devices, 164,480 B) and `dax_param.bin`
(34,736 B, 11 devices + 3 variants). Both were fetched from public per-device
vendor repositories, md5-verified byte-exact against
`sharing-clusters.csv`, and parsed. **5 of 5 distinct md5s MATCH.** No
proprietary bytes are committed.

## Fleet rows (from `sharing-clusters.csv`)

| md5 | file | family | bytes | devices | status |
|---|---|---|---|---|---|
| `2a47164eed5282f27ad503a28c7b71a0` | `hrtf5c.bin` | adsp | 164,480 | 12 | **MATCH** (11 of 12 fetched; see note) |
| `630a2e1853c80e1dd1d2b1cd2d334ac4` | `hrtf5c.bin` | adsp | 54,180 | 1 | **MATCH** |
| `70727b648c00a14bad7ede05ba9b4bd3` | `dax_param.bin` | other | 34,736 | 11 | **MATCH** |
| `9bd0f50ab41f2bbff3172923bf734525` | `dax_param.bin` | other | 34,736 | 2 | **MATCH** |
| `72ec897bbd599d470561707bfdfc0d24` | `dax_param.bin` | other | 34,736 | 1 | **MATCH** |
| `23750b395f6fc5906bb1c3da69d684a8` | `dax_param.bin` | other | 34,736 | 1 | **MATCH** |

Device sets:

- `2a47164e…` — cupid; diting; fuxi; marble; mayfly; mondrian; nuwa; socrates;
  thor; unicorn; vermeer; zeus
- `630a2e18…` — vermeer
- `70727b64…` — a21s; a71; beyond0lte; beyond1lte; beyond2lte; beyondx; f62;
  gta4l; gta4lwifi; gta4xl; gta4xlwifi
- `9bd0f50a…` — d1; d1x
- `72ec897b…` — d2s
- `23750b39…` — r8q

**`vermeer` is double-attributed** by the CSV (it appears under both the
164,480 B and the 54,180 B md5). Its vendor tree ships only the 54,180 B file,
so the 164,480 B cluster is 11 devices confirmed + vermeer unconfirmed
`[OPEN]`.

## Verdict per target

| target | container | content class | evidence class |
|---|---|---|---|
| `hrtf5c.bin` 164,480 B | **none** — flat table, no magic, entropy 7.395 flat | HRTF magnitude/phase, 40 azimuths × 2 ears × 257 one-sided bins | measured |
| `hrtf5c.bin` 54,180 B | **4CC chunk container** (`VER0`…`ENDM`) | HRTF impulse responses, 13 dirs × 2 ears × 512 taps @ 48 kHz | measured |
| `dax_param.bin` 34,736 B | **none** — 16-byte tag records, entropy 2.775 falling-tail | compiled Dolby DAX audio tuning database | measured + public-artifact match |

## Key findings

1. **One filename, two unrelated formats.** The 164,480 B `hrtf5c.bin` is a
   bare numeric table with no header at all; the 54,180 B file is a
   self-describing 4CC chunk stream. A 451,512 B third build
   (`d11e8ed2511de9e09b4d55d0ae330667`, `PixelOS-Nuwa/Nuwa-Dump`) is the
   tagged format with a two-channel reverb tail. Filename ≠ identity — the
   same caution the QCA BT fleet recorded for `crbtfw21.tlv`.
2. **The 164 kB table decodes cleanly.** 160 records × 257 float32. Rows at
   even index are all ≥ 0 (magnitude), rows at odd index all ≤ 0 (phase), with
   **zero exceptions**. 4-row groups give 40 directions × 2 ears. The derived
   ITD peaks at **770.8 µs**, at the human-head physical ceiling, and fits a
   single sinusoid over the 40 directions with 599.0 µs amplitude and 53.5 µs
   RMS residual — i.e. one azimuth sweep.
3. **The 54 kB container is self-describing and its arithmetic is exact.**
   `SPKN=13`, `FFTN=512`, `HLEN=256`, `SMPR=48000`, and
   `13 × 2 × 512 × 4 = 53,248` equals the `HRTF` body length exactly. The
   451 kB variant's reverb chunks also resolve exactly
   (`49664 × 4 × 2 + 24 = 397,336`).
4. **`dax_param.bin` is a compiled Dolby DAX tuning database, not camera
   tuning.** The work-order premise is corrected: the file ships beside
   `dax-default.xml` and `libswdap.so` under the audio set. Its tag `iebs`
   carries a 20-band frequency array and a 20-band target array that are
   **byte-identical** to the public XML's `<ieq-bands>` table, and the
   header's `u32[0] = 9` matches the XML's nine `<profile>` entries.
5. **The record format is pinned.** `[tag][u32 a][u32 b][u32 c]` + payload,
   in nine groups of 2,824 B at a fixed stride, each group exactly 93 records
   laid out as 6 sections of 14 plus a 9-record tail. Groups 1–8 are
   tag-identical; group 9 differs in its sixth section only.
6. **Cross-version variation is localised.** All four `dax_param.bin`
   variants are 99.61–99.86% identical at the same offsets; the
   beyond0lte↔d1 delta is 119 bytes confined to `[27225, 27383]`, a per-device
   tuning table that is zero on beyond0lte/r8q and populated on d1/d2s.

## What is still open

- `vermeer`'s second md5 attribution (§ above).
- RESOLVED 2026-11-21 (issue #509): `dax_param.bin` md5 `70727b648c00a14bad7ede05ba9b4bd3`
  (34,736 B) is md5-verified in the public TheMuppets
  `proprietary_vendor_samsung_gta4xl-common` tree @ lineage-23.2
  (`proprietary/vendor/firmware/dax_param.bin`) — the `gta4xlwifi` DB row
  and the 11-device `70727b64…` cluster stand.
- Header words `706` and `342` in `dax_param.bin`.
- `BLSG`/`INVM` semantics in the 4CC HRTF container.
- Which DSP path consumes which `hrtf5c.bin` family.

## Reproduce

```sh
cd implementations/data-blob-fleet
python3 -I make_fixture.py            # regenerate synthetic fixtures
python3 -m unittest test_blob_probe   # 54 tests
python3 -I blob_probe.py <file> --brief
```

Payload bytes are not committed; fetch routes are in §1.3 of the analysis doc.
