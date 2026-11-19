# implementations/adsp-fleet — clean-room ADSP `bm2nXX.bin` container probe

A structural probe for the Qualcomm ADSP `bm2nNN.bin` fleet — the files that
ship at `vendor/lib/rfsa/adsp/` and that the upstream coverage database records
under 25–26 devices each. The probe answers the question the metadata matrix
could not: **what is inside the container, and is it DSP firmware at all?**

It is not. `bm2nXX.bin` is a **serialized C++ object graph** — a QNN/HTP
tensor pickle — not Hexagon DSP code. The head is a load-header plus a segment
table, followed by a prologue carrying length-prefixed RTTI type names, followed
by a run of `0x1337BEEF`-tagged records and a `0xBEEFF00D` terminator.

Sibling documents own the other two views of this fleet and are **not**
duplicated here:

| document | owns |
|---|---|
| `../../blob-matrix/laptop/qualcomm-adsp-bm2n-container-header.md` | the byte-level container layout, the 48-file invariant audit, and the negative result on build-id similarity |
| `../../blob-matrix/laptop/qualcomm-adsp-bm2n-variant-matrix.md` | the measured md5/source matrix across 15+ fleet variants |
| `bm2n-fleet-analysis.md` (this directory) | the per-file fleet table, the region decomposition, the record grammar, and the tool contract |

**Ground truth (public sources only):**

| what | where | what it settles |
|---|---|---|
| `TENSOR_MAGIC = 0x1337beef` | `QNN/HTP/core/tensor.h` (BSD-3-Clause-Clear) | the record tag; its count equals the record count exactly |
| `Hdr_MAGIC = 0x7309F72B`, `Hdr_MAGIC_MULTI = 0x3790FA5C` | `QNN/HTP/include/HTP/pickle_header_tags.h` | the second container family (one payload in the fleet) |
| `htp_header_locate_field()` record grammar (`rlen = recdesc & 0xFFFF`, `tag = recdesc >> 16`) | same header | the pickle-family field walk |
| `OP_SEQNO_MARKER_XOR = 0x1303ee71` | `QNN/HTP/core/serialize_defs.h` | the `0x1303ee71` marker in record bodies |
| ADSP domain / rfsa transport | `drivers/misc/fastrpc.c` (GPL-2.0) | why the files live under `lib/rfsa/adsp/` |

## Files

| file | role |
|---|---|
| `bm2n_probe.py` | the probe: header decode, segment-table walk, prologue grammar, record walk, region entropy, string census, word histograms, fleet diff. CLI `python3 -I bm2n_probe.py <file> [--json out.json] [--brief] [--fleet f1 f2 …]`; exit 1 on structural violations |
| `make_fixture.py` | deterministic synthetic fixtures built from the measured layout only (no proprietary bytes) |
| `fixtures/*.bin` | synthetic fixtures, both container families + error paths. **`*.bin` is gitignored** — regenerate with `python3 -I make_fixture.py` |
| `test_bm2n_probe.py` | unittest suite: `python3 -m unittest -v test_bm2n_probe` — **86 tests, all passing** when the real payloads are present in `/tmp/astro_u/payloads`; the real-payload tests skip cleanly when they are not, so the suite runs from a fresh clone with no proprietary bytes |
| `bm2n-fleet-analysis.md` | the analysis: per-file fleet table, region decomposition, record grammar, the two families, [OPEN] list |

## Fleet scope

All six DB identities were fetched from public repositories on 2026-11-19 and
md5-verified byte-exact against `coverage-matrix.csv`:

| file | bytes | DB md5 | verified | DB devices |
|---|---|---|---|---|
| `bm2n06.bin` | 864,824 | `9010bb1a7c08222a058aaef7edd938c6` | **MATCH** | 25 |
| `bm2n08.bin` | 3,091,896 | `1275a2d212e5bccce734d3055ff10156` | **MATCH** | 25 |
| `bm2n12.bin` | 2,623,528 | `5c86c8fcc7451f51e11d38276253aac8` | **MATCH** | 26 |
| `bm2n13.bin` | 1,106,944 | `bf635d9084b54633526f9ad8a84d299b` | **MATCH** | 25 |
| `bm2n14.bin` | 103,168 | `805176afaae27821520b79647fa5d498` | **MATCH** | 26 |
| `bm2n15.bin` | 1,082,856 | `2ce8163cda60f33cbf2b50f03a3d0ea1` | **MATCH** | 26 |

Source: `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`,
`sm8350-common/proprietary/vendor/lib/rfsa/adsp/<name>`, except `bm2n13.bin`
which comes from `TheMuppets/proprietary_vendor_motorola` @ `lineage-19.1`,
`sm7325-common/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin`.

Plus one genuine non-DB variant, kept in the fleet diff as the version axis:

| file | bytes | md5 | note |
|---|---|---|---|
| `bm2n13_sm8350.bin` | 1,082,824 | `2d267761f3291c9ca4a7850ab0ef1966` | the OnePlus `sm8350-common` revision; byte-identical to `bm2n54.bin` on Nothing Pong |

## Usage

```bash
# single file, full report
python3 -I bm2n_probe.py /path/to/bm2n12.bin

# fleet table only
python3 -I bm2n_probe.py /path/to/bm2n12.bin --brief

# cross-file identity matrix
python3 -I bm2n_probe.py bm2n12.bin --fleet bm2n08.bin bm2n12.bin bm2n15.bin

# machine-readable
python3 -I bm2n_probe.py bm2n12.bin --json out.json
```

Exit status is `0` when every structural invariant holds and `1` when the
prologue grammar, the segment sentinel, the record walk, or the tail terminator
fails.

## Test status

```
$ python3 -m unittest discover -q
Ran 86 tests in 82.5s
OK
```

All 86 pass with the seven real payloads present in `/tmp/astro_u/payloads`
(verified this session). Without them the real-payload tests skip cleanly, so
the suite is runnable from a fresh clone with no proprietary bytes.

## Value statement

**What this buys the program.** The fleet's 25–26 devices per file can now be
described in terms a free implementation can act on: the container is
specified well enough that a reader can walk it and reach the record stream, and
the record stream is a serialized object graph rather than opaque machine code —
which means the *class* of the content is known (QNN/HTP tensor pickles) even
though the individual record semantics are `[OPEN]`.

**What it does not buy.** It does not decode the tensor graph. Which tensors
the graph describes, what the models compute, and how the ADSP consumer
schedules them are all `[OPEN]` and are listed explicitly rather than guessed.
The probe also establishes a *negative* that matters: build-id is **not** a
proxy for content similarity, so a reader must not attribute one file's findings
to another file in the same lineage.

Not legal advice, not a replacement implementation. Regulatory/legal hurdles:
`../../upstream-contribution/radio-regulatory-hurdles.md`.
