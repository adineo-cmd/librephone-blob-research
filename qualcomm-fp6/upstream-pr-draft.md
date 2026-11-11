# Upstream contribution draft — LibrePhone (codeberg.org/rsavoye/librephone)

> **Status update (2026-11-12):** superseded by the full upstream
> contribution package in [`upstream-contribution/`](../../upstream-contribution/README.md)
> (PR-1 = this draft's `docs/wireless.md` fix, carried forward; PR-2 = new
> `docs/wmi-dispatch.md`; PR-3 = per-segment `wpss.bXX.md` corrections;
> PR-4 = `docs/files.md` BT + boot-chain pointers). **All claims below
> remain valid.** New since this draft, from the decoded dispatch
> analysis: the WMI *event-routing* code is **Hexagon** (`wpss.b06`,
> e_machine 164 per the mdt), not RISC-V — the RISC-V core runs the QURT
> application firmware (`wpss.b07`); the message-ID registry is in
> `wpss.b09` (149 distinct IDs, anchor `0xc0691080`). Full research note:
> [`papers/wmi-dispatch-architecture.md`](https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md).
> The `docs/fp6-riscv-cores.md` suggestion below is folded into the
> package: the ICP/VPU e_machine=94 finding stays in
> `qualcomm-fp6/docs/fp6-architecture-census.md` and is referenced from
> the PR-1/PR-4 descriptions rather than shipped as a separate upstream
> doc.

Status: **ready to submit** (needs a Codeberg account login; this lab has no
Codeberg credentials). Submit as a documentation PR against `main`, file
`docs/wireless.md`, replacing the unverified processor guess in the
"Wireless Chipset" section.

## What to submit (doc change)

Current upstream text (docs/wireless.md):

> This chip appears to have an embedded 8 bit ATMel AVR core, and
> possibly a RISCV32 core as well.

Proposed replacement:

> The wpss firmware (`modem/image/qca6750/wpss.*`) runs on a **32-bit
> RISC-V** core. Verified from the ELF headers of the LineageOS FP6 image
> (2026-11-09 nightly): `wpss.b07` is ELF32 with `e_machine=243
> (EM_RISCV)`, entry `0x404000`, and its entry code disassembles as RV32
> machine-mode startup (`csrs mstatus` / `csrw mtvec` sequences). The
> firmware version string is `WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1`; the
> ucode segment (`wpss.b08`, vaddr `0x4ff00000`) carries
> `WLAN_UCODE_MOSELLE_4.2.0-00000` ("Moselle" is the WCN6750 firmware
> codename). Note: per-segment `.bXX` ELF headers carry junk `e_machine`
> values (zeros, and even x86=3 on `wpss.b08`, which is a data segment) —
> architecture identification should use the program segment's headers +
> entry-point sanity, not segment headers.

Also suggested: a new short doc `docs/fp6-riscv-cores.md` documenting the
same finding for the camera ICP and VPUs (see our full write-up:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md):

> The camera ICP firmware (`CAMERA_ICP.mbn/.elf/.mdt`,
> `CICP.FW.7.0-00021`) and all VPU firmware (`vpu20/30/33_*.mbn`) on FP6
> are ELF32 with `e_machine=94` — the historic RISC-V machine value used
> by early toolchains (243 was assigned later). Public Qualcomm
> documentation does not state the ICP/VPU ISA; this appears to be the
> first public identification of these cores as RISC-V.

## Why upstream wants this

- `docs/wireless.md` currently guesses the ISA; clean-room documentation
  benefits from verified facts.
- Knowing the wpss is RISC-V means free-reimplementation analysis can target
  RV32 disassembly (capstone handles RV32+RVC today), whereas Hexagon
  remains the hard, toolless side.

## Submission checklist

- [ ] Fork codeberg.org/rsavoye/librephone under an account
- [ ] Branch `docs/wpss-riscv-architecture`
- [ ] Apply the doc change above (keep upstream's doc tone/format)
- [ ] PR description links to our census write-up + raw census table
- [ ] Mention the IRC channel (#librephone) for follow-up
