# The WPSS "PCIe bridge" — WCN6750 transport stack (FP6) — for upstream issue #37

One-page research note from **public data + lab-derived facts**
([upstream issue #37](https://codeberg.org/rsavoye/librephone/issues/37):
"identify if one of the WPSS blobs is the PCIe bridge, and which file
it is"). Written 2026-11-16.

**Legend:** [PUBLIC] = public fact; [LAB] = lab-derived, committed doc
cited; [OPEN] = needs data not available on this box.

## 1. Answer available now

**The "PCIe bridge" is not a separate blob file — it is a firmware
function inside the single wpss MDT image**, and the software bridge
that plays the PCIe host role on Linux runs in the kernel vendor
module (ICNSS/IPCI), not in the blob. Component by component:

- [LAB] The wpss firmware is **one** Hexagon MDT image
  (`wpss.mdt` + `.b00–.b12`, e_machine 164, executable code segments
  b01/b02/b03/b05/b06) containing one embedded ELF32 RISC-V executable
  (`wpss.b07`, QURT RTOS, e_machine 243, entry 0x404000) —
  `qualcomm-fp6/docs/fp6-architecture-census.md` +
  `qualcomm-fp6/docs/wpss-qurt-rtos.md` (F-5/F-8/F-20/F-22). There is
  no second image that could be "the bridge".
- [LAB] The endpoint-side transport behaviors live in that image: the
  F-8 transport finding records PCIe-style semantics at the WPSS
  boundary (WAKE# GPIO handshake + doorbell/IPC buffers), and the
  committed WMI dispatch paper documents what the Hexagon segments do
  with the traffic once it arrives (`papers/wmi-dispatch-architecture.md`).
- [PUBLIC] On the Linux side the vendor wlan stack talks through the
  **ICNSS2/IPCI** platform layer — upstream's own transport doc was
  corrected to exactly this in commit `b75b158f` "docs: correct
  WCN6750 transport to IPCI/ICNSS2" (2026-11-01), and PR #58's author
  (L123123) implements the endpoint/bridge role in **software**
  (BHI load, MHI slave, QRTR v1, WLFW stub) for the free replacement,
  confirming the role split: the real "bridge" is partly kernel
  emulation, partly blob firmware.
- [PUBLIC] Issue #56's own capture shows `lspci` enumerating the
  WCN6750 as a PCI device (Device 0x1105) — expected, because the
  host kernel side presents a (fake) PCIe function; Android's "no PCIe
  devices" premise in #37 matches: ICNSS2 is a platform driver that
  emulates the PCIe attach for MHI.

## 2. Which file implements which piece (current state)

| piece | location | evidence class |
|---|---|---|
| PCIe-style wake/doorbell semantics | wpss image (b06 Hexagon dispatch segments; b07 RV32 QURT app) | [LAB] F-8 |
| WMI command processing after transport | wpss.b06 dispatch (registry of 225 records) | [LAB] WMI paper |
| "PCIe" host presentation + MHI | kernel vendor ICNSS2/IPCI + MHI (public wlan module tree) | [PUBLIC] |
| Endpoint/MHI/QRTR re-implementation (free) | PR #58 payload | [PUBLIC] |
| Exact segment that implements the endpoint emulator | **[OPEN]** — needs disassembly of b01/b02/b03/b05 Hexagon segments; binaries not on this box (see wants-matrix A-13 "blocked part") | — |

## 3. What would close the [OPEN] cell (not runnable here)

1. Re-fetch the FP6 wpss segments (`modem/image/qca6750/wpss.b0*` from
   the public nightly — sizes/hashes already in
   `qualcomm-fp6/results/census.md`).
2. Disassemble the four executable Hexagon segments with Ghidra
   12.2's public Hexagon module (the lab's validated tool, F-28); look
   for MHI/doorbell/WAKE register offsets and the QRTR/IPC buffer
   handlers.
3. Cross-check register offsets against the public ath11k MHI/BHI
   register map (`drivers/net/wireless/ath/ath11k/mhi.c`, `bhie`,
   `mhi` — mainline).

## Sources consulted (accessed 2026-11-16)

- Upstream issues #37, #56 (bodies via Codeberg API), PR #58 thread
  summary in `upstream-contribution/librephone-wants.md` rows D-1/A-24
- Commit `b75b158f` (cited in librephone-wants.md; fetched there
  2026-11-15)
- Lab: `qualcomm-fp6/docs/fp6-architecture-census.md`,
  `wpss-qurt-rtos.md`, `papers/wmi-dispatch-architecture.md`,
  `results/census.md`

**Clean-room statement:** identification is stated only where
committed evidence exists; the segment-level pin is marked open, not
guessed.
