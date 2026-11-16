# implementations/mediatek/md32-interface — clean-room MD32 interface-layer parser

The **spec'd subset** of the MT6785 md1dsp image interface (the workorder's
"MD32 spec-derived interface stubs"): everything the lab's published
documents pin about the md1dsp container/interface layer, and — explicitly —
nothing about the MD32 *instruction encoding*, which is an open gap
(F-45; ROADMAP M-1/I-4).

CLEAN-ROOM STATEMENT: written from `mediatek/docs/md1dsp-decode.md` (F-36),
`mediatek/docs/md32-gap.md` (F-45) + `mediatek/results/md32-gap.json`, and
`mediatek/rosemary-census.md` on **2026-11-16**; no proprietary material
accessed during development.

## What it parses (`python3 -I md32_interface.py <md1dsp-file> [--json out.json] [--no-crc]`)

- **GFH MMM prefix** — records from 0x0 up to the DSP! magic, with the
  F-36-documented md1dsp FILE_INFO values (sig_type=0, load_addr=
  0xFFFFFFFF, total_size=0x678000). Full GFH field decode lives in
  `implementations/mediatek/container/`.
- **DSP! image header** — magic re-verified at 0x118, size 0x678000 @0x124,
  version 1 @0x128, marker 0x12345678, chip "MT6785", "DEFAULT_ASIC",
  build "MOLY.LR13.R1.MP.V89.6.P79". The marker/chip offsets are read under
  **both** documented maps (F-36 relative +0x18/+0x1C vs F-45 absolute
  0x134/0x138 — a 4-byte documented internal conflict) and the parser
  reports which matched; it never guesses.
- **Descriptor table @0x248** — three 16-B records; shape + documented
  values verified, `off/len` semantics left opaque (F-45's own honest
  negative).
- **USIP @0x274/0x278** — record shape parsed up to the RAKE tag; record
  count/termination and field semantics explicitly NOT pinned (F-45:
  "records_partially_parsed"); the two documented sample records are matched.
- **RAKE chain @0x4b4** — six 16-B records `(w0 opaque, off, len, crc32)`
  per the results-JSON field order; verifies the documented window
  0x58c814 → 0x60a9d0, sorted non-overlapping offsets, per-record match
  against the documented values, and — the F-45 "named next lever" —
  **per-region crc32 against file content** when a real image is supplied.

This directly implements F-45's next lever 2 ("Parse the DSP! section
descriptors end-to-end and check per-section crc32 against file content —
proves which sections are stored vs packed"), so a future pass holding
`06_md1dsp.bin` can run it as-is.

## The ISA gap (TODO, kept open)

The module docstring carries the standing TODO: no public spec pins the
LR13-era MD32 instruction encoding (Ghidra's stock module is a stalled WIP
for the older ADI-heritage core; F-45's 6-language decode pass found no
coherent control flow anywhere). Any future coverage number must be judged
on mnemonic coherence, not percentage (F-45's artifact note).

## Files

| file | role |
|---|---|
| `md32_interface.py` | parser + CLI (clean-room header) |
| `make_fixture.py` | synthetic-fixture generator incl. a GF(2) crc32-forge helper |
| `fixtures/md1dsp_header_fixture.bin` | generated 1,408-byte self-made fixture — regenerable byte-exactly (`python3 -I make_fixture.py`); the repo `.gitignore` excludes `*.bin`, so it is a working-tree artifact verified by the test suite |
| `test_md32_interface.py` | 14 tests; the full-layout fixture (0x60a9d0 B, with the documented RAKE crc32 constants forged into real content) is generated into scratch at test time and NOT committed |

## Fixture honesty

No md1dsp image exists on this machine (checked 2026-11-16), so the
fixtures are self-made bytes from the documented layout. The full fixture's
RAKE regions carry the **documented F-45 crc32 constants** — obtained by
forging 4 suffix bytes per region (crc32 is GF(2)-affine in the message
bits) — which proves the crc-verification path against the real constants
without any proprietary bytes.

## RULE 0 note

GitHub code search for public tools handling md1dsp's GFH type 260 or the
DSP! header returned 0 relevant hits (checked 2026-11-16, query `gfh
"0x104"` and the container component's searches); the lab census (F-36,
2026-11-13) states the md1dsp loader format "is publicly undecoded". This
component implements the lab's own documented spec — no equivalent public
tool exists to our knowledge.
