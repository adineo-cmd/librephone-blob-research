# implementations/wifi-cpp-fleet — clean-room Qualcomm MSM CPP firmware probe

A structural probe for the `cpp_firmware_vN_N_N.fw` family — the twelve
identities the upstream database records under the `wifi` family label, 9
devices each (`v1_12_1`: 4). The probe answers what metadata could not: **what
is actually inside the fixed 16 KiB window, and where does the version live?**

Two answers, both measured:

1. **These are not WiFi blobs.** `cpp` is **Camera Post-Processing** (MSM CPP).
   The `wifi` family label in `sharing-clusters.csv` is a labelling error. The
   consumer is GPL-2.0-only `msm_cpp.c`; the producer is `cpp_hardware.c`. The
   Cypress/Infineon hypothesis was tested and refuted (§1.3 of the analysis).
2. **The version is not ASCII.** It is one little-endian `u16`,
   `0x1000 | BCD(minor)`, sitting immediately beneath a
   `MSM_CPP_MSG_ID_TRAILER` record. The `v1.1` a `strings` run finds at `0x3F80`
   is a fixed literal of the shared epilogue, present in 11/12 files regardless
   of version.

**RULE 0 was satisfied before any structural claim was made:** the public
source that consumes these files (`cpp_load_fw()` in `msm_cpp.c`) was read
first. It parses *nothing* — no magic, no length, no checksum; it streams
`fw->size / 4` LE words — so every structural fact below is a payload
property, not a loader contract. That distinction is load-bearing and is
repeated everywhere it matters.

Labels used in the documents: **[S]** quoted from public source (file, symbol) ·
**[M]** own measurement of payload bytes · **[OPEN]** not established, gap named.

## Clean-room statement

Written 2026-11-19 from public sources only:

| what | where |
|---|---|
| kernel consumer | `drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c` + `msm_cpp.h`, GPL-2.0-only, `LineageOS/android_kernel_xiaomi_msm8953` @ `lineage-21` |
| userspace producer | `cpp_hardware.c`, `cpp_hw_params.h`, `cpp_hardware.h`, `Sushrut1101/android_vendor_qcom_proprietary` @ `master` |
| protocol constants | `MSM_CPP_MSG_ID_CMD` `0x3E646D63`, `MSM_CPP_MSG_ID_OK` `0x0A0A4B4F`, `MSM_CPP_MSG_ID_TRAILER` `0xABCDEFAA` |
| version bitfield | `CPP_FW_VERSION_*` in `cpp_hw_params.h` — 31:28 major, 27:16 minor, 15:0 step |

No decompiled code, no proprietary documentation, no vendor datasheet. All
numbers in the analysis are computed from payload bytes on disk by
`cpp_probe.py`, or quoted from the files above.

## Documents

| document | owns |
|---|---|
| `cpp-version-matrix-analysis.md` | the full analysis: provenance, the 16 KiB layout, invariant-vs-varying by range, the version story, the N×N matrix, the hardware→firmware map, cross-fleet verdict, `[OPEN]` register |
| `../../blob-matrix/laptop/wifi-cpp-firmware-family.md` | the laptop-half summary: the family-identity correction, the window contract, the matrix verdict |
| this README | scope, usage, test status, value statement |

## Files

| file | role |
|---|---|
| `cpp_probe.py` | the probe. Single file, stdlib only. |
| `make_fixture.py` | deterministic synthetic fixtures built from the measured layout only (no proprietary bytes) |
| `fixtures/*.fw` | 15 synthetic fixtures; excluded from git by `fixtures/.gitignore` (see "Fixtures" below) |
| `test_cpp_probe.py` | unittest suite |

## Usage

```bash
# one file, human summary
python3 cpp_probe.py <file>.fw --brief

# one file, full JSON to stdout
python3 cpp_probe.py <file>.fw

# N x N identity matrix over a fleet (three variants: whole / code / content)
python3 cpp_probe.py --matrix f1.fw f2.fw ... --json matrix.json
python3 cpp_probe.py --matrix f1.fw f2.fw ... --brief   # closest-neighbour table

# ladder diff: first-diff offset and run census per consecutive pair
python3 cpp_probe.py --versions f1.fw f2.fw ... --brief

# skip hashing (faster on big fleets)
python3 cpp_probe.py --matrix ... --no-hash
```

Exit status: **0** clean, **1** error-class diagnostic (wrong size, not
word-aligned, all-fill, I/O), **2** usage error.

Brief output for one real identity:

```
cpp_firmware_v1_12_0.fw: 16384 bytes
  window: exact16K=True short16K=False words=4096
  header: lead=0x7140 vectors 0x1359..0x140a (6 distinct, even=False)
  version: name=1.12.0 enum=0x100c0000 marker=0x1012 @ 0x01f2  build-counter 0x0007
  ascii version string in image: False
  layout: code_end=0x28d4 fill=0xff (+5674 B) epilogue=0x3efe tail_fill=True
  trailer: u16@0x3efc=0x1411 -> 2*(w+1)=0x2824, code_end=0x28d4 (residual 176 B)
  entropy: code region 4.66 bits/byte, 35.8% 0xFF
  protocol magics present: MSM_CPP_MSG_ID_CMD x2, MSM_CPP_MSG_ID_OK x1, MSM_CPP_MSG_ID_TRAILER x2
```

## What the probe actually checks

Every check is either a measurement rule or a public constant. Nothing is
inferred from a filename alone.

| check | basis |
|---|---|
| window is exactly 16,384 B, or the 16,128 B outlier | [M] 11/12 + 1/12 |
| size is a multiple of 4 | [S] `cpp_load_fw()` divides by 4 |
| lead word at `0x0000` is `0x7140` | [M] invariant in 12/12 |
| 16 × `u16` vector table at `[0x0002, 0x0022)` | [M] reported with parity and equality pattern, not assumed |
| no ASCII string encodes the file's own version | [M] honest negative, 12/12 |
| exactly one `u16 == 0x1000 \| BCD(minor)` | [M] 12/12; BCD proven by 1.10 → `0x1010` |
| the `u16` below the marker is a **build counter**, not the step | [M] disagrees with the filename step in 9/12 |
| filename version ↔ `CPP_FW_VERSION_*` enum | [S] `cpp_hw_params.h` bitfield; the payload carries **no** enum word |
| three `msm_cpp.h` magics found by search | [S] header values as needles |
| fill byte is `0xFF`, never `0x00` (scoped to the pad window) | [M] 12/12 |
| epilogue `[0x3EFE, 0x3FCA)` invariant | [M] byte-identical 11/12, absent in 1.1.1 |
| `u16@0x3EFC` is a halfword count: `code_end == 2*(w+1)` | [M] exact in 6/12, erased in 3, +176 B in 3 |
| the 176-byte residual decodes as 14 B prologue + 8 × 20 B records + 2 B tail | [M] identical shape in all 3 that carry it |
| `code_end` = last non-fill byte before the epilogue | [M] |
| entropy / `0xFF`% / zero% per region | [M] |
| three identity matrices, plus adjacent first-diff | [M] |

The three matrices exist because one number is misleading for a padded
fixed-window format: `whole` is inflated by shared `0xFF` fill, `code_region`
restricts to `min(code_end)`, and `content_only` excludes positions where
either side is `0xFF`/`0x00` — that last one is the honest similarity number.
Example: 1.5.0↔1.6.0 reads **67.24** whole and **15.14** content.

## Fixtures

`make_fixture.py` writes:

```
fixtures/cpp_firmware_v1_1_1.fw      16,128 B   the short-window outlier
fixtures/cpp_firmware_v1_1_6.fw      16,384 B
fixtures/cpp_firmware_v1_2_0.fw      16,384 B
fixtures/cpp_firmware_v1_4_0.fw      16,384 B
fixtures/cpp_firmware_v1_5_0.fw      16,384 B
fixtures/cpp_firmware_v1_5_1.fw      16,384 B   modelled 2-byte step delta
fixtures/cpp_firmware_v1_5_2.fw      16,384 B
fixtures/cpp_firmware_v1_6_0.fw      16,384 B
fixtures/cpp_firmware_v1_8_0.fw      16,384 B
fixtures/cpp_firmware_v1_10_0.fw     16,384 B   modelled 176-byte stride block
fixtures/cpp_firmware_v1_12_0.fw     16,384 B   modelled 176-byte stride block
fixtures/cpp_firmware_v1_12_1.fw     16,384 B   modelled partial rewrite
fixtures/bad_size_synthetic.fw       16,383 B   not word-aligned -> exit 1
fixtures/truncated_synthetic.fw          16 B   unreadable        -> exit 1
fixtures/all_fill_synthetic.fw       16,384 B   no payload        -> exit 1
```

Every payload byte is a SHA-256 counter stream keyed by a per-fixture tag, so
re-running the script reproduces every byte (the suite asserts this). The
fixtures reproduce the **layout and the measured deltas** only — never the
vendor content. `test_fixtures_carry_no_vendor_bytes` asserts none of the 15
matches any of the twelve real md5s.

**Note on `.gitignore`:** the repo root excludes `*.bin` but not `*.fw`, and
this family ships as `.fw`. The root file is outside this work's write scope,
so `fixtures/.gitignore` excludes everything in that directory (with
`.gitignore` itself un-ignored). The fixtures are regenerable by a committed
script and are not tracked. Regenerate with:

```bash
cd implementations/wifi-cpp-fleet && rm -f fixtures/*.fw && python3 make_fixture.py
```

## Tests

```bash
cd implementations/wifi-cpp-fleet && python3 -m unittest -v test_cpp_probe
```

**88 tests, all passing** (79 run against the committed fixtures plus 9
real-fleet assertions; those 9 **skip cleanly** when the payloads are absent,
so the suite runs from a fresh clone with no proprietary bytes).

The real-fleet class reads `/tmp/astro_u/cpp/{real,payloads}/` if present and
asserts the md5s, sizes, `code_end` values, epilogue sha1, the 2-byte 1.5.0→1.5.1
delta, marker presence, the adjacent build counter, and the absence of any
in-file `CPP_FW_VERSION_*` word, directly against the fetched bytes. It never
becomes a prerequisite.

Covers: fixture determinism and size fidelity; the window check including the
16,128 B outlier; header/vector-table probing (including the corrected
"not all even" result); the ASCII-version honest negative and the `v1.1`
decoy; the BCD marker rule and the adjacent build counter; protocol-magic
detection; padding characterisation
(0xFF scoping, epilogue invariance, trailer field); the trailer `u16`
halfword-count rule in all three of its observed shapes; entropy profile shape;
adjacent first-diff; all three matrix variants (dimensions, diagonal, symmetry,
range, padding inflation, step-pair near-identity, outlier detection);
malformed/truncated input; the CLI and JSON contracts; exit statuses.

## Fleet scope (12/12 md5 MATCH)

All twelve fetched 2026-11-19 from
`TheMuppets/proprietary_vendor_xiaomi_ginkgo` @ `lineage-22.2`,
`proprietary/vendor/firmware/`. Full table with sha256 and DB status in
`cpp-version-matrix-analysis.md` §2.

| version | bytes | md5 | devices |
|---|---|---|---|
| 1.1.1 | **16,128** | `4d145d5a13a3956bf33aec94a8e7fe62` | 9 |
| 1.1.6 | 16,384 | `738a83a673dd45fa5852b5cc9519ee94` | 9 |
| 1.2.0 | 16,384 | `3f078c3d1658679a762f7d77c99517cd` | 9 |
| 1.4.0 | 16,384 | `b6f54efc4675040f7b7e99398905646e` | 9 |
| 1.5.0 | 16,384 | `e51087ba19409150103faafaff849627` | 9 |
| 1.5.1 | 16,384 | `ed1f2071b61447924f50fe8670cd51be` | 9 |
| 1.5.2 | 16,384 | `02e4044179d7dfc069aa9a42db690642` | 9 |
| 1.6.0 | 16,384 | `de85a5f8196ec73cffc61382b3e0d5f6` | 9 |
| 1.8.0 | 16,384 | `04423a29e78bb01d9be62256a65354a6` | 9 |
| 1.10.0 | 16,384 | `8d08bfdf92db5b1df58af9b6adf61eae` | 9 |
| 1.12.0 | 16,384 | `ef031a3f24f877242621ba695d8dcbd2` | 9 |
| 1.12.1 | 16,384 | `a59e732fcbf71cb5fcc6c54fef0124d6` | **4** |

`linux-firmware` ships **none** of them (`WHENCE`, 537,962 B, zero
`cpp_firmware` hits, fetched 2026-11-19) — honest negative, consistent with
F-74's pattern for device-vendor-partition blobs.

## Value statement

What the programme gains:

- **One matrix label corrected with evidence.** `cpp_firmware_*` is not WiFi;
  it is the MSM camera post-processor. Anyone budgeting this fleet as a WiFi
  target was budgeting the wrong subsystem, and the refutation is now written
  down with the public sources that settle it.
- **The loader is fully specified and trivial.** `cpp_load_fw()` needs no RE:
  three words and a blind stream. A free loader is a few lines.
- **The version contract is pinned to an exact byte rule** —
  `0x1000 | BCD(minor)`, one occurrence, immediately below a trailer record —
  and two traps are documented so they are not rediscovered later: the ASCII
  `v1.1` at `0x3F80` is a shared epilogue literal, and the `u16` under the
  marker is a **build counter**, not the step (it disagrees with the filename
  step in 9/12 files).
- **A third container philosophy is on record.** F-75 is
  `4 + 24 + data_length + 256`; gen-2 is `4 + 32 + data_length + 36`; CPP is a
  **padded fixed window with no length field at all**, whose only length signal
  (`u16@0x3EFC` = a halfword count of the region it terminates) is ignored by
  the loader. Three families, three answers to "how big am I".
- **The remaining unknown is bounded.** The opaque surface is the code region
  plus a 204-byte invariant epilogue plus a 176-byte stride block in three
  identities — each pinned to exact offsets and labelled `[OPEN]`. It is no
  longer "twelve opaque 16 KiB binaries".

What it does **not** claim: no disassembly, no ISA identification, no statement
about what the microcode computes, and no suggestion that a free replacement
exists today. The `[OPEN]` register in the analysis names every gap.
