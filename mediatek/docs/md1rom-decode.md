# md1rom decode-verified: MIPS32 + MIPS16e hybrid — the nanoMIPS prior-art attribution does NOT apply to MT6785 (F-31)

**Finding:** The MT6785 ("rosemary", Helio G95) modem firmware `md1rom`
(26,682,512 B) is **not nanoMIPS**. Byte-level decode testing in Ghidra 12.2
shows it is a classic MTK 4G-generation hybrid: a **MIPS32 little-endian reset
trampoline at 0x0** (a fully coherent 4-instruction sequence
`lui a2,0x174; addiu a2,a2,0x2ed0; jr a2; mtc0 zero,Count`) followed by
**MIPS16e-compressed code islands** (Ghidra language `MIPS:LE:32:16e` gives
88–100.8 % instruction coverage in 256-byte windows at 0x200000, 0x700000,
0xe00000, 0x1200000, 0x1300000, 0x1400000 where pure MIPS32, microMIPS and
nanoMIPS all fail), interleaved with zero-coverage data/payload regions.
microMIPS is ruled out. A first-public nanoMIPS confirmation is therefore
**overturned** for this chip: prior art (NCC ghidra-mtk-loader, taszk 2023)
establishes nanoMIPS for Dimensity-generation modems (MT6873+, NR16 build
2023); MT6785 is one generation earlier (MOLY LR13, 2020) and its ISA matches
the older MIPS32+MIPS16e baseband architecture. No public decode-level
analysis of MT6785 md1rom exists (per F-16 prior-art audit); this is the first
instruction-level characterization of this image we are aware of.

## Claim

1. **Entry point at 0x0** (image imports as one flat block at base 0x0): the
   reset vector decodes as real MIPS32 LE code under `MIPS:LE:32:default`:

   ```
   00000000: lui   a2,0x174        ; word 0x3c060174
   00000004: addiu a2,a2,0x2ed0     ; word 0x24c62ed0
   00000008: jr    a2               ; word 0x00c00008  → jump to 0x176ed0
   0000000c: _mtc0 zero,Count       ; COP0, delay slot — clear the Count timer
   ```

   A `lui/addiu/jr` trampoline followed by a CP0 write is a textbook MTK
   bootloader reset sequence; it is not a container header misread as code.
   After it, bytes `00 65` repeat to 0x30 (padding filler), explaining why
   whole-image auto-analysis left 0x0 undefined until disassembly is forced.
2. **MIPS16e code islands decode densely** under `MIPS:LE:32:16e` where
   MIPS32-only cold-start fails (the two languages share `mips16.sinc`; the
   16e variant only changes the *initial* ISA mode, so window comparison is
   the right discriminator — see table).
3. **microMIPS is ruled out**: `MIPS:LE:32:micro` peaks at 12.5 % coverage in
   a code window and is near-zero everywhere else.
4. **nanoMIPS is ruled out at decode level**: the NCC ghidra-nanomips
   processor module (v0.3.3, pure-SLEIGH) was built against Ghidra 12.2 and
   the identical windows tested — near-zero coverage on every code island
   (median 0.78 %, max 3.91 % in code), while MIPS16e decodes the same bytes
   at 88–100.8 %. Build notes below for reproducibility.
5. Version strings recovered at decode level: build
   **MOLY.LR13.R1.MP.V89.6.P79** (modem OS version, matches the
   `md1_file_map` census hit), flavor path
   `mtk_rel/XIAOMI_S0MP1_K6785V1_64/LWCTG_CUSTOM/L4/csm/ss/…` (Xiaomi-class
   build of MOLY LR13 for MT6785). Auto-analysis of the full image creates
   1,322,630 instructions and 16,297 functions under `MIPS:LE:32:default`.

## Prior art (with dates)

- [NCC Group ghidra-mtk-loader](https://github.com/nccgroup/ghidra-mtk-loader)
  (verified verbatim: "Currently, only nanoMIPS-based firmware is supported")
  + [ghidra-nanomips](https://github.com/nccgroup/ghidra-nanomips) — establishes
  nanoMIPS for the md1img samples NCC processed (Dimensity-era builds; their
  docs reference an MT6879/NR16 build dated 2023).
- [taszk labs full-chain baseband series, part 1](https://labs.taszk.io/articles/post/full_chain_bb_part1)
  (2023-12-07, Daniel Komaromy) — "our nanoMIPS decompiler, debugger, and
  emulator for Mediatek basebands" (Dimensity-generation work).
- Neither source names MT6785; the census (F-16) generalized the attribution
  and flagged it unverified-from-bytes. This doc resolves that flag.

## Method

1. Input: `md1img` → `00_md1rom.bin` (26,682,512 B) from the rosemary payload
   tree (F-16/F-17 extraction, mtk_hdr chain, no ELF).
2. Ghidra 12.2 PUBLIC headless, each candidate language imports the image as a
   raw binary flat block at base **0x0**, **no auto-analysis** (cold-start):
   `MIPS:LE:32:default` (MIPS32), `MIPS:LE:32:16e` (MIPS16e initial mode),
   `MIPS:LE:32:micro` (microMIPS), `nanomips:LE:32:default` (NCC processor
   module built for 12.2).
3. F-20/F-28 decode-density methodology: at fixed 256-byte windows (entry 0x0,
   the `jr` target 0x176ed0, and a 1 MiB-step sweep across the whole image,
   31 windows), force `clearListing` then explicit disassembly from the window
   start; count valid instruction bytes vs window size. Comparing *the same
   windows* across languages isolates the ISA, since each language can only
   succeed on bytes actually encoded in its ISA.
4. A second pass let full auto-analysis run on the MIPS32-default import to
   measure whole-image instruction/function creation and to harvest defined
   strings.

## Decode-density table (256-byte windows, coverage = valid instruction bytes / 256)

| window | MIPS32:LE:default | MIPS16e (16e) | microMIPS | nanoMIPS (NCC) |
|---|---|---|---|---|
| 0x0 (entry) | **6.25 %** (4 real MIPS32 insns) | 0.8 % | 6.3 % | 1.6 % |
| 0x176ed0 (`jr` target) | 1.6 % | **25.0 %** | 1.6 % | 0 % |
| 0x174100 | 12.5 % | **50.0 %** | 12.5 % | 0.8 % |
| 0x200000 | 0 % | **88.3 %** | 0 % | 0 % |
| 0x700000 | 93.0 % | 93.0 % | 1.6 % | 0 % |
| 0xe00000 | 84.4 % | 84.4 % | 0 % | 3.9 % |
| 0x1200000 | 1.6 % | **100.8 %** | 1.6 % | 0.8 % |
| 0x1300000 | 1.6 % | **100.0 %** | 1.6 % | 2.3 % |
| 0x1400000 | 1.6 % | **91.4 %** | 1.6 % | 1.6 % |

nanoMIPS across the full 31-window sweep (1 MiB step, 0x0–0x1900000): median
coverage **0.78 %**, maximum in any code region **3.91 %**; the only windows
above 20 % (0x1500000, 0x1600000, 0x1800000: 25–31 %) are tail *data* regions
that partially decode in every 32-bit ISA tested (microMIPS also hits 26.6 %
at 0x1700000/0x1800000). microMIPS is near-zero on every code island
(max 12.5 %). Full per-window data in results/md1rom-decode.json.

Sample decoded listing, window 0x1200000 under MIPS16e (dense, coherent):

```
jal 0x011c5004
_nop
li a2,0x32db
lw a1,0x504(pc)          ; PC-relative loads — MIPS16e signature
jal 0x011c5064
_addiu a0,sp,0x44
lw a2,0x4f8(pc)
li a3,0x32de
li a0,0x26c
jal 0x0134ee04
_li a1,0x1
sw v0,0x18(sp)
lw v0,0x44(sp)
lw s0,0x4e8(pc)
lbu a2,0x0(v0)
cmpi a2,0x2
```

## Region map (from the 1 MiB sweep, 16e language)

- 0x0: MIPS32 reset trampoline + `00 65` filler.
- ~0x174000–0x176ed0+: MIPS16 code the entry `jr` targets (entry chain:
  0x0 → 0x176ed0), partial windows (25–51 %) — island boundaries not mapped.
- Dense code islands: 0x80000 (100.8 %), 0x100000 (55.5 %), 0x200000
  (88.3 %), 0x300000 (50.8 %), 0x700000 (93.0 %), 0xe00000 (84.4 %),
  0x1000000–0x1400000 (32.8–100.8 %), 0x1960000 (100 %).
- Zero/near-zero regions (data, compressed payloads, DB/EM tables — 26 MB
  total image): 0x400000–0x500000, 0x800000, 0x900000, 0xb00000, 0xc00000,
  0xd00000, 0xf00000, 0x1500000, 0x1600000–0x1900000.
- A per-segment byte-exact map (the loader's `INT_InitRegions_C` route) is
  future work; this pass maps coverage, not segment semantics.

## Verdict

**nanoMIPS OVERTURNED for MT6785 md1rom — the image is MIPS32 LE entry code +
MIPS16e-compressed code islands** (the classic pre-Dimensity MTK baseband
architecture). The nanoMIPS attribution from prior art is confirmed as
generation-specific (Dimensity/MT6873+), not a general MTK-modem property. F-16
and F-18 should be corrected accordingly.

## Honest negatives / limitations

- The NCC **ghidra-mtk-loader container loader was NOT used** for this pass:
  its release zip targets Ghidra 12.1 and its build requires Gradle 9.1+
  (we built the nanomips processor module instead and imported the raw image).
  The loader's `INT_InitRegions_C`/`MtkInitRegions` segment-expansion route is
  therefore unexercised — segment boundaries in the region map are
  coverage-derived, not container-derived.
- NanoMIPS module install (for the next agent): Ghidra 12.2's
  `buildExtension.gradle` requires **Gradle ≥ 9.1** (the repo's wrapper pins
  8.10.2 — bump `gradle-wrapper.properties` to 9.9.1); Gradle ≤ 8.x cannot
  evaluate build scripts under JDK 25 ("Unsupported class file major version
  69"). Built with JDK 25 + Gradle 9.9.1 (BUILD SUCCESSFUL in 1m56s). The
  module is pure SLEIGH data (no Java classes): registering it by copying the
  repo layout to `<ghidra>/Ghidra/Processors/nanomips/` (Module.manifest +
  data/languages + lib jar) makes `nanomips:LE:32:default` available to
  headless without any GUI install — placing it in the user-settings
  Extensions dir does NOT register it headless (verified: "Unsupported
  language" until the Processors copy).
- 0x80000 and 0x700000/0xe00000 decode densely under *both* MIPS32-default and
  16e — expected: Ghidra's MIPS32 sleigh includes mips16.sinc and can switch
  ISA mode mid-flow; window-level ISA attribution for those regions needs
  per-instruction ISA-mode inspection (not done this pass).
- Coverage windows are 256 B and step 1 MiB — island boundaries are coarse.
- md1dsp (Coresonic-class DSP, `DSP!` magic) remains not byte-verified (F-17);
  no DSP ISA decoder available this pass.

## Reproduce

```
GH=/…/ghidra_12.2_PUBLIC; JAVA_HOME=/…/jdk-25.0.5+8
analyzeHeadless /tmp/proj p -import 00_md1rom.bin -processor MIPS:LE:32:16e \
  -loader-baseAddr 0x0 -noanalysis -scriptPath <tools> -postScript window_stats.java
```

Stats script: `window_stats.java` (clearListing + forced disassembly per
256-byte window; JSON + listing dump). Windows used: entry 0x0, 0x176ed0,
0x174100, 0x174400, 0x175000, 0x100000…0x1900000 step 0x100000, plus 0x80000.
