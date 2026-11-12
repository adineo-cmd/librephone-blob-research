# md1dsp decode: the modem DSP self-identifies as MTK **MD32** — but no available decoder decodes its bytes (F-36)

**Finding:** The MT6785 ("rosemary", Helio G95) modem DSP firmware `md1dsp`
(6,783,260 B, sha256 `265e2c5a…3636`, size matches census F-16 exactly) is the
modem **L1/PHY DSP** image, and its own embedded build tree names the core:
**122 source-path strings under `md32/…`** (`md32/usip/brp/modem/lte/…`,
`md32/rake/modem/c2k/…`, `md32/usip/common/driver/sys_drv/…`) — the same
**MD32** core for which Ghidra 12.2 ships a stock processor module
(`MD32:LE:32:default`, "MediaTek MD32"). Task strings are pure LTE L1/PHY:
`4g_dci_parse_task.c`, `4g_pcfich_parse_task.c`, `4g_pdsch_crc_task.c`,
`4g_pdsch_proc_task.c`, plus HSPA (`hspa_agch_event_task.c`) and CDMA2000
(`c2k_scheduler.c`, `LISR_c2k_pilot_arrival`). **But the instruction stream
itself is an honest negative:** decode-density testing in Ghidra 12.2
headless across **six** languages — MIPS32, MIPS16e, microMIPS, nanoMIPS
(NCC), Xtensa, and Ghidra's own MD32 module — produces no coherent code
anywhere (max **6.25 %** on non-artifact windows, vs 88–100.8 % for the
md1rom MIPS16e islands in F-31). The census's Coresonic attribution
(F-16/F-17) is superseded at string level for this generation (Coresonic
remains valid for the older MT6295 DSP per cyrozap); the ISA-level question
stays open and is now precisely characterized.

## Claim

1. **Container byte-verified:** 512-B mtk_hdr (`FILE_INFO`, declares payload
   0x678000 B at file offset 0x118) followed by a **`DSP!`** image header:
   magic at 0x118, `+0x0C` size 0x678000, `+0x10` version 1, `+0x18` marker
   `0x12345678`, `+0x1C` chip id `"MT6785"`, `+0x2C` `"DEFAULT_ASIC"`,
   `+0xAC` build string `MOLY.LR13.R1.MP.V89.6.P79` — **identical to the
   md1rom build** (same MOLY LR13 package, two different cores).
2. **Core self-identification (string level, strong):** 122 `md32/…` paths +
   `DSP_BIN_RO_ADDRESS` / `DSP_CONTROL_IDLE` asserts + DEMOD register asserts
   at 0xBD300000. This is the first self-naming evidence for any rosemary
   DSP core (audio_dsp self-names `hifi3` in its file names; md1dsp self-names
   `md32` in its build tree).
3. **Instruction-level decode: honest negative.** Six languages, identical
   256-B windows, F-31 methodology (cold-start, `clearListing` + forced
   disassembly, coverage = instruction bytes / 256). Code regions
   (0x40000–0xC0000, 0x140000–0x180000, 0x53C000–0x600000 — dense non-zero
   bytes hosting the string pools) decode at 0–6.25 % in *every* language,
   including `MD32:LE:32:default`. Whole-image auto-analysis under MIPS32
   creates **2 instructions and 0 functions** (15,594 data items — the
   strings — confirming there is no MIPS code to find).
4. **Family map (corrects F-31's closing note):** the MT6785 modem subsystem
   runs on at least two core families — MIPS32 LE + MIPS16e islands (md1rom,
   F-31) and an md32-class DSP (md1dsp, this pass) — with HiFi3/Xtensa
   (audio_dsp) a third. The nanoMIPS story is unaffected (already overturned
   for md1rom; md1dsp decodes near-zero under nanoMIPS too).

## Decode-density table (256-B windows, coverage %; 256 KiB step)

| window | MIPS32 | MIPS16e | microMIPS | nanoMIPS | Xtensa | MD32 |
|---|---|---|---|---|---|---|
| 0x0 (hdr) | 1.6 | 10.9 | 1.6 | 0 | 0 | 0 |
| 0x118 (DSP!) | 4.7 | 20.3 | 4.7 | 18.0 | 0 | 0 |
| 0x40000 | 0 | 2.3 | 0 | 0 | 0 | 0 |
| 0x80000 (code) | 1.6 | 1.6 | 1.6 | 0.8 | 3.5 | 0 |
| 0x140000 (code) | 0 | 5.5 | 0 | 3.9 | 3.5 | 1.6 |
| 0x4c0000 (data) | 0 | 29.7 | 0 | 28.1 | 0.8 | 14.1 |
| 0x540000 (code) | 0 | 7.8 | 0 | 0 | 0 | 3.1 |
| 0x600000 (tail) | 0 | 0 | 0 | 0 | 0 | 0 |
| 0x640000 (tail) | 0 | 9.4 | 0 | 0 | 0 | 0 |
| zero windows (≈20) | 26.6 | 13.3 | 26.6 | 26.6 | 0–1.2 | 26.6 |

**Artifact note (essential):** pure-zero windows "decode" exactly 68 bytes in
every fixed 32-bit ISA (17 × 4-byte instructions — `nop` in MIPS terms), and
34 × 2-byte under MIPS16e — identical coverage appears in the same windows
under every language, so those rows are disassembler behavior on zero runs,
not evidence of code. The only other >20 % cell (16e at 0x4c0000, 29.7 %) is
a repeating 4-byte data pattern partially decoding as alternating
`addiu v1,sp,0x3a0 / addiu s0,sp,0x100` ×7 — data, not code. After removing
artifacts, the best real-content coverage anywhere is **6.25 %** (MD32 at
0xaeb00, fine sweep), and the fine sweep through every string-bearing region
(0x60000–0x5dd000, 13 windows) never exceeds 35 % under any language
(0x5dd000 under 16e — again a data artifact). Full per-window data in
`results/md1dsp-decode.json`.

## Interpretation and hypotheses (flagged as hypotheses)

- The build tree self-name `md32` is decisive for core *identity* but the
  bytes show Ghidra's stock MD32 module does not cover this image. Plausible
  causes: (a) the code sections are packed/compressed (the 0x600000+ tail is
  high-entropy; the DSP! header suggests a load protocol we have not
  expanded), (b) an MD32 ISA generation gap (Ghidra's module is evidently
  built from a different subsystem's MD32), (c) per-segment load addresses
  from the DSP! header are needed before disassembly can take.
- Prior art: [cyrozap/mediatek-lte-baseband-re](https://github.com/cyrozap/mediatek-lte-baseband-re)
  establishes the **Coresonic** DSP for the older MT6295-era modem DSP;
  CEVA acquired Coresonic in 2014 and no open Ghidra/SLEIGH decoder exists
  for that ISA family either. For MT6785 the self-naming `md32` tree makes
  Coresonic unlikely for *this* generation, but the byte-level core identity
  remains open.
- [Check Point 2021](https://research.checkpoint.com/2021/looking-for-vulnerabilities-in-mediatek-audio-dsp)
  is the closest public methodology (MTK DSP firmware, custom opcodes) but
  targets the audio DSP, not md1dsp.

## Honest negatives / limitations

- No language tested decodes md1dsp; we could not byte-verify the ISA.
- Ghidra's MD32 module was used stock: no DSP!-header segment expansion, no
  pspec tuning, base 0x0 flat import. A follow-up pass that parses the DSP!
  segment table (or unpacks the image) may still close it.
- Auto-analysis (for the string harvest) was run under MIPS32-default since
  no language won; instruction/function counts are therefore not meaningful
  beyond confirming the negative.
- The tail 0x600000–0x678000 is high-entropy and likely a compressed secondary
  image; not analyzed this pass.

## Reproduce

```
GH=/…/ghidra_12.2_PUBLIC; JAVA_HOME=/…/jdk-25.0.5+8
analyzeHeadless /tmp/proj p -import 06_md1dsp.bin -processor <LANG> \
  -loader-baseAddr 0x0 -noanalysis -scriptPath <tools> \
  -postScript window_stats.java 0x0,0x118,0x200,… out.json
```

Scripts: `window_stats.java` (per-window clearListing + forced disassembly,
JSON out) and `harvest_md1dsp.java` (auto-analysis counts + defined strings).
Languages: `MIPS:LE:32:default`, `MIPS:LE:32:16e`, `MIPS:LE:32:micro`,
`nanomips:LE:32:default`, `Xtensa:LE:32:default`, `MD32:LE:32:default`.
