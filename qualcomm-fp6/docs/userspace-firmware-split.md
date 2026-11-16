# User space vs loaded firmware (Fairphone FP6) — for upstream issue #19

Answer to [upstream issue #19](https://codeberg.org/rsavoye/librephone/issues/19)
("Identify what code is run in user space vs loaded firmware", High
Priority): the split table of **which function lives where** for every
firmware family on the FP6, from the lab's committed censuses + public
kernel sources. Written 2026-11-16.

**Legend:** [PUBLIC] = public-kernel fact, source cited; [LAB] =
lab-derived fact from committed censuses (all in `qualcomm-fp6/docs/` +
`results/`); [OPEN] = not establishable from data available here.

## 1. The issue's assumption, answered first

The issue assumes "the AARCH64 executable in the modem.img blob is
potentially the user space part". **It is not.** The AArch64
executables inside `modem/image/` (soter64, smplap64, focal64,
hdcp1/2p2, evautil64, the UUID-named TAs, ...) are **QSEE trusted
applications — TrustZone-side firmware**, loaded through
`qseecom`/SCM, not through the kernel's PIL path and not by the
Android user session:

- [LAB] The trustzone census identifies them by string inventory as
  TAs (QSEE/GlobalPlatform vocabulary, `.mdt+.bXX` splits), size/hash
  rows in `qualcomm-fp6/results/census.md`.
- [PUBLIC] Mainline's `drivers/tee/qcom/qseecom.c` loads QSEE app
  images via SCM calls — TA images are the userspace side of that ABI
  in the sense of *client*, but the code itself executes in the secure
  world, never as Android user-space code.
- Consistent with the maintainer's own finding on issue #33
  (2026-07-22): these files "never get loaded at boot time" by an
  instrumented `mdt_loader.c` — because their loader is qseecom, not
  the PIL remoteproc loader.

**The actual user space** vendor code on this device lives in
`vendor.img`/`system` (HAL executables and `.so`s, e.g.
`vendor.qti.bluetooth@1.x`), which is a separate partition family from
the firmware images — and is *also* proprietary on the stock device.
The kernel-side drivers are the free, mainline-able middle layer.

## 2. The split table, per firmware family

| family | user space (what runs there) | kernel (mainline-able drivers) | loaded firmware (the blob) | driver↔blob boundary |
|---|---|---|---|---|
| Bluetooth | free: BlueZ/btuserland; stock: Qualcomm vendor BT HAL (patch download + chipset tables) [LAB] | `hci_uart`/`hci_qca` + `btqca` — fully mainline, free [PUBLIC] | WCN6750 ROM + rampatch msbtfw11/12 (**ARM32 Thumb**) + EVROS family mainline cannot name [LAB] | UART HCI + EDL download opcodes 0xFC00/0xFC48; IBS sleep 0xFE/0xFD/0xFC — see [interface-bt.md](interface-bt.md) |
| WiFi | wpa_supplicant (free) + Android HAL [PUBLIC] | `ath11k` (mainline, WCN6750_HW10 supported) or vendor qcacld LKM [PUBLIC] | wpss image: Hexagon (DSP6) code segments + one embedded ELF32 **RV32 QURT** app (wpss.b07) [LAB] | IPCI/ICNSS2 PCIe-style platform + MHI + WMI/HTT/CE; the WMI dispatch spec is the lab's papers/wmi-dispatch-architecture.md |
| Modem (cellular) | RIL daemon (stock proprietary; free alternative = oFono/ModemManager speaking QRTR/QMI) [PUBLIC] | `mdt_loader` + `qcom_q6v5_mss` + GLINK/rpmsg + `qrtr` + QMI + `rmnet` — all mainline [PUBLIC] | modem.mdt + modem.b00–b30 (**Hexagon**, e_machine 164) + milos/qdsp6m.qdb + per-carrier mcfg payloads [LAB] | PAS authentication via SCM; GLINK/SMEM channels → QRTR → QMI — see [interface-cellular.md](interface-cellular.md) |
| TrustZone / TAs | TEE client libraries only (KeyMint/gatekeeper HALs talk to TAs, never execute their code) [PUBLIC] | `drivers/tee/qcom/qseecom.c` (mainline since v6.8-era) [PUBLIC] | tz.img (QTEE OS, AArch64, 45 phdrs), hyp.img (QHEE, PIE entry 0x80000000), keymaster/devcfg/uefisecapp/featenabler (AArch64 PIE), modem/image UUID TAs [LAB] | SCM call interface via qseecom ioctl; census-only policy per trustzone-census.md |
| DSPs (adsp/cdsp) | FastRPC user libraries (stock proprietary `.so`s) [PUBLIC] | `fastrpc` char devices + `qcom_q6v5_pas` remoteproc — mainline [PUBLIC] | adsp.img / cdsp.img (**Hexagon**) + bm2nXX-region payloads in `vendor/lib/rfsa/adsp` [LAB] | FastRPC ioctls (compute offload), PAS auth (load) |
| Boot chain | none — runs before any OS [LAB] | none (kernel is itself loaded by this chain) [LAB] | xbl (3-ELF container: RV32 + AArch64), xbl_config, shrm/aop/aop_config/cpucp (**RV32**), qupfw (**Hexagon per header**), uefi (AArch64 FV), abl (ARM32), xbl_ramdump (AArch64) [LAB] | PBL → XBL → UEFI → ABL → Linux; AVB verification from vbmeta down (bootchain-census.md) |
| AVB / verified boot | avbctl/userspace verity toggles; LineageOS userdebug sets vbmeta flags=3 (hashtree + verification disabled) [LAB] | dm-verity + `qcom,rmtfs` style helpers [PUBLIC] | vbmeta.img + vbmeta_system.img (SHA256_RSA4096 descriptors; rollback_index = security-patch epoch date) [LAB] | vbmeta descriptors → partition hashes; OEM signing chain ends at Fairphone's "T2MO OEM Key" [LAB] |
| Protected VMs | crosvm/pVM framework (Android 16 side) [PUBLIC] | Gunyah drivers: only `gunyah_wdt.c` in mainline; VM lifecycle stack ships with vendor kernels [PUBLIC] | pvmfw.img (raw AArch64 machine code, AVB-verified via vbmeta_system descriptor) [LAB] | Gunyah SMCCC calls; see [interface-gunyah.md](interface-gunyah.md) |
| NFC | NFC HAL (`libnfc-nci`) [PUBLIC] | `drivers/nfc/*` (in-kernel) [PUBLIC] | firmware inside the NFC controller (no image file in the censused partitions) [LAB] | NCI + vendor fw-download opcodes — see [interface-nfc.md](interface-nfc.md) |

## 3. The three-layer rule this table instantiates

For every family on this platform the same shape holds — worth stating
as the answer's headline:

1. **User space** = Android HALs/vendor daemons (proprietary on stock,
   replaceable by free equivalents *that speak the kernel interface* —
   BlueZ, wpa_supplicant, oFono/ModemManager over QRTR). None of the
   firmware images' code runs here.
2. **Kernel** = load/auth/transport drivers, all mainline or
   mainline-able (mdt_loader/PAS, qseecom, hci_qca/btqca, ath11k,
   fastrpc, qrtr). This layer is the stable, documentation-able
   surface — the part librephone's doc set (wifi-driver-interface.md,
   the planned BT/NFC/cellular docs) already targets.
3. **Firmware** = the signed images: user-space-vs-firmware is not one
   binary split but one per remote processor, each with its own loader
   (PIL/mdt_loader for Hexagon/PIL processors, qseecom for TAs,
   hci_qca EDL for BT, ICNSS2/MHI for wpss, UEFI/XBL for the boot
   chain). The ISA map (who executes what) is the lab's
   fp6-architecture-census.md + bootchain-census.md: Hexagon (modem,
   adsp, cdsp, qupfw, wpss code segments), RV32 (wpss.b07, shrm, aop,
   aop_config, cpucp, xbl-inner), ARM32 (BT rampatch, abl),
   AArch64 (QTEE/QHEE/TAs, uefi, xbl core).

[OPEN] The modem's own internal user/kernel-ish split (Hexagon-side
QURT processes vs the "AARCH64 executable" the issue hypothesized)
needs Hexagon disassembly capacity — stated as open in
interface-cellular.md rather than guessed.

## Sources consulted (accessed 2026-11-16)

- Lab committed censuses: `qualcomm-fp6/docs/{bt-firmware-census,bootchain-census,trustzone-census,fp6-architecture-census,interface-cellular,interface-bt,interface-nfc,interface-gunyah}.md`, `qualcomm-fp6/results/census.md` (665-file census), `results/bootchain-census.json`, `results/bt-tz-census.json`
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/remoteproc/qcom_q6v5_pas.c (fetched 2026-11-16 — PAS processor list incl. `qcom,milos-*-pas`)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/tee/qcom/ (qseecom; existence per the trustzone census kernel cross-reference)
- Issue #33 thread (maintainer's own mdt_loader instrumentation, 2026-07-22) — the negative evidence the TAs never pass through PIL

**Clean-room statement:** lab census facts + public-kernel facts only;
no proprietary content, no disassembly beyond committed entry-sanity
checks, no key material.
