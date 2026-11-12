# librephone-blob-research

Clean-room reverse engineering of Android proprietary blobs for the FSF's
[LibrePhone](https://www.fsf.org/news/librephone-project) initiative.
**Facts documented, never blobs committed** — every analysis ships derived
metadata only (headers, segment tables, hashes, version strings, protocol
constants) with reproducible scripts.

## Two vendor fronts

### Qualcomm — Fairphone FP6 (QCM6490), LineageOS 23.2

Verified findings (full evidence in `qualcomm-fp6/docs/`):

| # | Finding |
|---|---------|
| 1 | **wpss (WCN6750 WiFi) core = 32-bit RISC-V** — instruction-level proof; upstream's "8-bit AVR" guess disproven |
| 2 | **Camera ICP + all VPU firmware = RISC-V** (historic e_machine 94) — first public ISA interpretation + family census |
| 3 | Qualcomm .bXX segment headers carry junk e_machine values (methodology finding) |
| 4 | **wpss runs Qualcomm's QURT RTOS on RISC-V**; leaked source names incl. `dog_hal_moselle_riscv.c` |
| 5 | First ath11k↔firmware WMI constant cross-reference; IDs constructed at runtime |
| 6 | **First public BT firmware census**: dedicated FAT16 partition, Moselle 1.1.2/1.2.0 + an EVROS family upstream Linux cannot name; rampatches = ARM32 Thumb |
| 7 | **First public TrustZone census**: QTEE/QHEE = monolithic AArch64 ELFs (no .mdt split); build TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1 |
| 8 | **First public boot-chain census**: shrm/aop/cpucp are RISC-V (5th–6th RISC-V families on the SoC); xbl.img = 3-ELF container; full SoC ISA map: Hexagon modem / RV32 housekeeping / ARM32 BT / AArch64 UEFI |
| 9 | **First formal research note published** — [papers/wmi-dispatch-architecture.md](papers/wmi-dispatch-architecture.md): the WCN6750 wpss WMI dispatch architecture decoded at instruction level — b09 registry (group routing) → b06 Hexagon dispatcher 0xc02cd9cc with computed jump tables (event routing); 61 events mapped; full falsification chain preserved |

Upstream contribution package ready: `upstream-contribution/` (4 paste-ready
PRs reconciled against live Codeberg docs) + `qualcomm-fp6/upstream-pr-draft.md`.

### MediaTek — Xiaomi Redmi Note 10S (rosemary, Helio G95 / MT6785), LineageOS 24.0

Verified findings (full evidence in `mediatek/`):

| # | Finding |
|---|---------|
| 1 | **MTK tinysys (scp) = ARM Cortex-M4F + FreeRTOS** — instruction-level (vector table + Thumb-2 256/256 + embedded ARM_CM4F/port.c); **not** RISC-V |
| 2 | **Camera CCU = Synopsys ARCv2 (2× ARC EM4-FPU, e_machine=195)** — first binary-level identification on a production device (vendor GCC ident + FPUDA extensions + dual-sensor entries) |
| 3 | **MTK ships zero ELFs in firmware partitions** — the mtk_hdr record chain (0x58881688, dual X.509 per-payload signing) replaces Qualcomm's MDT/PIL entirely |
| 4 | Full ISA map: ARM32 lk/preloader, HiFi3 (Xtensa) audio DSP, spmfw = PCM microcode (not a CPU), sspm/gz encrypted, cam_vpu = ARM32 Thumb-2, 21 ARCv2 files in userspace |
| 5 | Registry correction: e_machine 195 = ARCv2 (EM_ARC_COMPACT2), not TILE64; TILE64=187, TILEGx=191, TI_PRU=144 |
| 6 | **md1rom (modem) ISA decode-verified: MIPS32 LE entry + MIPS16e compressed code islands** (88–100.8% coverage; 1,322,630 instructions, 16,297 functions via Ghidra) — nanoMIPS prior-art attribution OVERTURNED for this chip (that attribution is Dimensity MT6873+-era; MT6785 is MOLY LR13-era). Version `MOLY.LR13.R1.MP.V89.6.P79`, flavor `XIAOMI_S0MP1_K6785V1_64` |
| 7 | **md1dsp (modem L1/PHY DSP) = MTK MD32-class core, self-named by its own build tree** (`md32/usip/...`, 122 source paths; LTE DCI/PCFICH/PDSCH + HSPA + C2K task strings) — instruction-level decode stays an honest negative: 6 ISAs tested (MIPS32, MIPS16e, microMIPS, nanoMIPS, Xtensa, stock Ghidra MD32) all fail (≤6.3% on real bytes vs 88–100.8% for md1rom islands); same MOLY build as md1rom, two different core families |

The cross-vendor comparison is itself a finding: the same-generation
"unusual core for 3A" story repeats — Qualcomm puts RISC-V in the camera
ICP, MediaTek puts ARCv2 in the camera CCU. And the modem story: two
different core families inside one MOLY build (MIPS32+MIPS16e application
baseband + MD32 L1/PHY DSP).

## Principles

1. Facts, not blobs. 2. Clean-room discipline. 3. Negative results are
results. 4. Everything reproducible. 5. Contribute upstream
([LibrePhone on Codeberg](https://codeberg.org/rsavoye/librephone)).

## Provenance

Split from the [Open Discovery Lab](https://github.com/adineo-cmd/open-discovery-lab)
lab notebook (owner directive, 2026-11-10) — that repo holds the
chronological record; this repo is the blob-RE body of work.

License: MIT for code, CC BY 4.0 for documentation.
