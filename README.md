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
| 2 | **Camera ICP + all VPU firmware = RISC-V** (historic e_machine 94) — first public ISA ID |
| 3 | Qualcomm .bXX segment headers carry junk e_machine values (methodology finding) |
| 4 | **wpss runs Qualcomm's QURT RTOS on RISC-V**; leaked source names incl. `dog_hal_moselle_riscv.c` |
| 5 | First ath11k↔firmware WMI constant cross-reference; IDs constructed at runtime |
| 6 | **First public BT firmware census**: dedicated FAT16 partition, Moselle 1.1.2/1.2.0 + an EVROS family upstream Linux cannot name; rampatches = ARM32 Thumb |
| 7 | **First public TrustZone census**: QTEE/QHEE = monolithic AArch64 ELFs (no .mdt split); build TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1 |
| 8 | **First public boot-chain census**: shrm/aop/cpucp are RISC-V (5th–6th RISC-V families on the SoC); xbl.img = 3-ELF container; full SoC ISA map: Hexagon modem / RV32 housekeeping / ARM32 BT / AArch64 UEFI |

Upstream contribution draft ready: `qualcomm-fp6/upstream-pr-draft.md`
(corrects LibrePhone's AVR guess to verified RISC-V).

### MediaTek (starting)

`mediatek/` — same methodology (architecture ID, segment maps, version
strings, prior-art checks) applied to MediaTek firmware families
(md1img modem, sscp/scp, mcupm, spmfw, TEE, connectivity) from public
LineageOS builds.

## Principles

1. Facts, not blobs. 2. Clean-room discipline. 3. Negative results are
results. 4. Everything reproducible. 5. Contribute upstream
([LibrePhone on Codeberg](https://codeberg.org/rsavoye/librephone)).

## Provenance

Split from the [Open Discovery Lab](https://github.com/adineo-cmd/open-discovery-lab)
lab notebook (owner directive, 2026-11-10) — that repo holds the
chronological record; this repo is the blob-RE body of work.

License: MIT for code, CC BY 4.0 for documentation.
