# implementations/lpec — the lab's LPEC (Sony DVF/MSV voice codec) bitstream decoder, as a standalone component

Re-homed from the Open Discovery Lab evidence repo
(`adineo-cmd/open-discovery-lab`,
`track-c-discovery-engine/results/format-re/lpec-census/`) so the decoders
can be consumed as a component. Code is unchanged from the committed lab
versions except the clean-room statement headers.

CLEAN-ROOM STATEMENT: written from the lab's own published LPEC spec
documents on **2026-11-16**; no proprietary material accessed during
development. The codec facts behind these decoders were established by
static analysis of the user-owned Sony reference DLLs and documented as
derived facts only — no Sony binaries or decompiled code exist in either
repo, and none were accessed during this re-home (F-48 policy, maintained).

## Spec provenance (the F-chain)

| finding | content | artifact here |
|---|---|---|
| F-47 | LPEC/TRC container census: 1024-B packets from 0x400 (0x800 after a 1 KB 0xFF annotation block), 10-B header, `bytes[4:6]` BE = payload bytes used; 48-B/384-bit LP frames at 6000 bps exact; no byte-identical silence frames | `extract_audio`/container model in `lpec_decoder.py` |
| F-48 | Sony reference DLLs obtained (DVE 3.3.01 CD-ROM) and statically analyzed; codec family confirmed CELP; per-mode codebook inventory (~15 tables/mode); LPEC.dll 329,064 B, sha256 `d0d8d888…ab50ce` (recorded in F-68) | facts behind `LP_CFG`/`SP_CFG` |
| F-49 | bit pump confirmed MSB-first; SP mode resolved (128-B type-0 frames, 96/160-B type-1/2); SP:LP = 8:3; the **pass-2 parser** | `lpec_decoder_pass2.py` |
| F-51 | LP bit layout RESOLVED from code: full field walk per type, per-type bit targets 384/288/480/384 (LP) and 1024/768/1280/1024 (SP), derived pulse budgets, byte-exact closure on both real samples (50,545 LP frames / 159 SP frames, 0 invalid, 6000.1/16000.0 bps); per-packet-reset container model REFUTED — the stream is continuous and frames straddle packet boundaries | `lpec_decoder.py` (the F-51 pass-3 parser) |
| F-52 | synthesis path wired (LSP→LPC Chebyshev, interpolation, PCM16) — first open-source LPEC decoder producing audible audio; plausibility-validated, not sample-validated | lives in the lab repo (`lpec_synthesis.py`); not re-homed in this pass |
| F-58 | pulse-position generation extracted: bit-budget allocator, 4:2:1 class split, 8-bit codes = rows of 2/4/8 pulse values | facts; allocator port lives in the lab repo |
| F-68 | ROADMAP Q-1 resolved: per-slot weight calibration fully attributed — **exact bit-economy closure 100.00 % on 94,600 LP and 100.00 % on 313 SP real subframes** (vs F-58's 74.2 %/62.9 % raw-weight baseline) | the closure the layout tables here implement |

Note: F-59 is DiamondWare (a different format) — the LPEC chain is
F-47 → F-48 → F-49 → F-51 → F-52 → F-58 → F-68.

## Files

| file | role |
|---|---|
| `lpec_decoder.py` | F-51 bit-exact frame parser: `BitReader`, `LP_CFG`/`SP_CFG`, `parse_frame` (types 0-3), `extract_audio` (packet container), `parse_stream`, byte-closure diagnostics |
| `lpec_decoder_pass2.py` | F-49 pass-2 parser: packet layer + per-packet-reset (LP) and continuous-straddle (SP) framing models |
| `test_lpec.py` | 16 synthetic-fixture tests (self-made bitstreams from the documented layout — see below) |

## Tests without Sony samples

The suite builds **synthetic bitstreams** from the documented layout only:
MSB-first `BitWriter` frames for LP types 0/1/2/3 and SP type 0, asserting
the parser consumes exactly the documented bit targets, returns the
documented frame byte sizes (48/36/60/48, 128/96/160/128), produces the
documented type-0 tail-pad signature (only {3, 9, 17}-bit pads; types
1/2/3 pad exactly 0), and closes byte-exactly on multi-frame streams. The
packet container tests reproduce the F-47/F-51 container semantics
(including the 0xFF annotation block skip and full-1024 packet chunking),
and the pass-2 straddle test demonstrates frames crossing packet
boundaries. The invalid-path test exercises the documented
pulse-budget guard via a synthetic config. Run:
`python3 -m unittest -v test_lpec`.

## Honest scope

These parsers account for **every transmitted bit** (frame → fields →
derived pulse budgets) but are not a sample-exact PCM decoder: the pulse
intra-block split (F-58/F-68 allocator), excitation-page decode, LSP
expansion and synthesis (F-52) live in the lab repo and are the next
layers to re-home. TRC (dsp_trc.dll codec) is a different codec and
intentionally out of scope (F-47/F-51).
