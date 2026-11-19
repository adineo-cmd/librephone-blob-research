# md1dsp MD32 decode gap: diagnosis (F-36 follow-up, F-45)

**Finding:** The F-36 decode failure is **not** a wrong-offset artifact and
**not** an endianness artifact. Ghidra's MD32 module traces to
[cyrozap/ghidra-md32](https://github.com/cyrozap/ghidra-md32) — a **stalled
work-in-progress SLEIGH spec** for the *older* ADI-heritage MD32
([mediatek-lte-baseband-re issue #6](https://github.com/cyrozap/mediatek-lte-baseband-re/issues/6):
`cycle_count_md32.h` carries an Analog Devices 2004-2008 copyright; MTK bought
ADI's cellular ops in 2007; MD32 ELF files use machine id **0x2454** = MTK's
TWSE ticker). The LR13-era (MT6785, 2019-20) md1dsp payload is a
**sectioned image** — the DSP! header carries a descriptor table with named
sections (`USIP` @0x274, `RAKE` @0x4b4) whose (offset,size,crc32) records chain
exactly over the `md32/rake/` string zone (0x58c814+0x4d0c=0x591520→…→0x60a9d0)
— and the string families map 1:1 onto the section tags (`md32/usip/`,
`md32/rake/`, `md32/scq16/`, `md32/brp/`, `md32/inner/`, `md32/common/`).
Decoding at the string-adjacent regions fails under MD32 (native **0–3.13 %**
real coverage), MD32 with 16-bit byte-swap (tests the spec's
`instructionEndian="big"` against LE fetch — the two 100 % windows are pure
**data artifacts**: endless `mv rX,#imm` with monotonically increasing
immediates and cycling registers, zero control-flow mnemonics), and MIPS32 BE
(≤6.25 %). **Diagnosis: generation/variant mismatch of the only public MD32
spec is the leading cause; wrong-region is refuted for the tested windows
(they are rodata/data, and no window under any language yields control flow);
the true code most plausibly lives in the unexplained dense zone
0x120000–0x160000 (H≈6.9, no strings) or the packed tail 0x600000+.**

## Claim

1. **Region map (new, supersedes F-36's unstructured view).** 64 KB-block
   entropy/zero/ASCII census (full image) + 9,796 ASCII runs (≥6 chars):
   - header 0x0–0x6xx (DSP! magic @0x118 re-verified; size 0x678000 @0x124,
     version 1 @0x128, marker 0x12345678 @0x134, "MT6785" @0x138);
     descriptor table @0x248: three 16-B records (u32 off, u32 len, u32 rsv,
     u32 tag) — (0x15c,0x58b814,0,1), (0x39c,0x73d4,0,2),
     (0x56c,0x49a58,0,"USIP"); `USIP` section body @0x278 with
     (0x1,0x100000,0xaee80,crc) + (0x0,0x101000,0x48b814,crc) style records
     (field semantics not fully pinned); `RAKE` @0x4b4 with 16-B records
     chaining (off=0x58c814,len=0x4d0c,crc)→(0x591520,0x26c8)→(0x5d6540,
     0x12484)→(0x5efac4,0x54a8)→(0x5f4f6c,0x10c68)→(0x605bd4,0x4dfc) —
     **tiling 0x58c814→0x60a9d0**, exactly the md32/rake/scq16 string zone.
   - rodata/assert pools: 0x80000–0xa0000 (`md32/usip/`, `md32/brp/`,
     `md32/inner/` LTE/HSPA/c2k task strings), 0x4b0000–0x530000,
     0x590000–0x5e0000 (`md32/rake/` c2k + `md32/scq16/` + `md32/common/`,
     1,022 strings in the RAKE window alone).
   - plain LE data tables: 0x4c0000 (`e8034000` repeats, increasing u32s),
     0xa0000+ (monotonic u16 index table), 0xb0000–0x100000 all-zero hole.
   - **unexplained dense zone 0x120000–0x160000**: H≈6.85–6.95, ASCII ~35 %,
     but *no* long strings (only ≤8-char noise runs) — consistent with code in
     an unknown encoding or LZ-compressed data; byte samples show high
     byte-pair diversity with recurring 16-bit patterns.
   - tail 0x600000–0x678000: H up to 7.9 — compressed secondary image
     (F-36's note stands).
2. **Language tests at string-adjacent regions (F-31 methodology, 21 windows
   ×256 B, cold-start `clearListing`+forced disassembly; new runs this pass).**
   - `MD32:LE:32:default` native: max real coverage **3.13 %** (2 insns at
     0x86000); the three 26.56 % cells are the known 68-B zero-run artifact.
   - MD32 on a **16-bit byte-swapped copy** of the whole image (converts LE
     storage→BE fetch, testing the spec's `instructionEndian="big"` in both
     directions): 100.00 % at 0xa0000 and 100.78 % at 0x540000 — **but** the
     dumped listings are disassembler artifacts: 40/40 instructions are `mv
     rX,#imm` with strictly increasing immediates (0x2000, 0x7000, 0xf001,
     0x16001, …) and a cycling register pattern; **no jump/call/load/store in
     any window**. The `mv` opcode space in cyrozap's spec is so permissive it
     absorbs arbitrary data. Coverage alone is not evidence here.
   - `MIPS:BE:32:default` (MTK big-endian hypothesis): max real **6.25 %**
     (0x591520, 0x5dd000 — string bytes), nothing elsewhere.
3. **Provenance of the stock MD32 module (web, 2026-11-13).** Ghidra 12.2's
   `Ghidra/Processors/md32` ships `MD32:LE:32:default` with ldefs
   `instructionEndian="big"`, `alignment=2`, and a sinc declaring
   r0–r15, loop registers (ls0/le0/lc0 ×3), accumulator a0, bundle/phase
   context bits — the ADI-heritage shape. cyrozap's README states the module
   is WIP and **stalled** because Ghidra cannot model instruction bundles and
   lacks delay-slot support for variable-length ISAs (Ghidra issues #3942,
   #4390, #4581); the chip it was derived from is the older
   mediatek-lte-baseband-re target (MT6295-era), not an LR13 Helio modem.
   [Check Point 2021](https://research.checkpoint.com/2021/looking-for-vulnerabilities-in-mediatek-audio-dsp)
   reversed the *audio* DSP (also self-named MD32-class) with custom opcodes —
   methodology prior art, different subsystem.

## Hypotheses tested (F-36's a/b/c + new d)

| hypothesis | verdict | evidence |
|---|---|---|
| (a) MD32 generation mismatch | **leading** | only public spec is stalled WIP from MT6295-era core; MT6785 is 6+ years newer; no byte evidence of cyrozap's encodings |
| (b) code region compressed/packed | **partial, localized** | tail 0x600000+ H≈7.9 (compressed); dense zone 0x120000–0x160000 unidentified; string zones plaintext so image is not wholly packed |
| (c) wrong offset tested | **refuted for tested windows** | F-36's 0x80000/0x140000/0x540000 are rodata/data/table zones; the string-adjacent code candidates were also tested this pass (21 windows incl. 0x84000/0x86000/0x591520/0x5dd000) — no control flow under any language |
| (d) instruction endianness (new) | **refuted** | 16-bit-swapped import under MD32: 100 % cells are `mv`-only data artifacts |

## Honest negatives / limitations

- We still cannot byte-verify the MT6785 MD32 ISA; no decoder produces
  control-flow-coherent code anywhere in the image.
- The 0x120000–0x160000 dense zone is *not* string-localized: it may be the
  code (unknown encoding) or packed data — unproven either way.
- DSP! descriptor field semantics (esp. the USIP block's addr/size/crc
  records) are partially parsed; a full expansion (esp. whether some sections
  decompress into DSP memory) may relocate the code.
- The `mv`-absorbs-everything behavior means *any* future MD32 coverage number
  must be judged on mnemonic coherence (control-flow + register pipeline), not
  coverage %.
- Tail 0x600000–0x678000 not decompressed (no known container for it).

## Named next lever

1. **Get a real MD32 ELF (machine 0x2454) or newer spec**: search MTK's
   GPL modem source drops and cyrozap's repo history for a newer
   `md32.sinc`; a symbol-bearing ELF pins the encoding of the *matching*
   generation and would immediately falsify/confirm the variant gap.
2. Parse the DSP! section descriptors end-to-end (esp. USIP block) and check
   per-section crc32 against file content — proves which sections are stored
   vs packed, and whether the 0x120000 zone or tail is a compressed segment.
3. Hand-build a minimal SLEIGH from the 0x120000–0x160000 zone using the
   Check Point methodology (find NOP-ish patterns, register fields, branch
   structure) if 1–2 fail.

## Reproduce

```
# three headless runs (JDK 25, Ghidra 12.2), windows: 0x0,0x40000,0x60000,
# 0x80000,0x84000,0x86000,0xa0000,0x120000,0x140000,0x180000,0x4b0000,
# 0x4d0000,0x530000,0x540000,0x580000,0x590000,0x591520,0x5a0000,
# 0x5c0000,0x5dd000,0x600000
analyzeHeadless /tmp/f45proj p1 -import 06_md1dsp.bin -processor MD32:LE:32:default \
  -loader-baseAddr 0x0 -noanalysis -scriptPath mediatek/tools \
  -postScript window_stats.java "$WINS" out.json
# + same on a 16-bit byte-swapped copy (md32_swap16 build script in scratch)
# + MIPS:BE:32:default; listing dumps via dump_win.java
```
Scripts: `mediatek/tools/window_stats.java`, `mediatek/tools/dump_win.java`
(new). Per-window data: `results/md32-gap.json`.
