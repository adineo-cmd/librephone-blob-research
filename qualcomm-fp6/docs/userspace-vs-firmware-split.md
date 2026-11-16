# User space vs loaded firmware (Fairphone FP6) — for upstream issue #19

Answer to [upstream issue #19](https://codeberg.org/rsavoye/librephone/issues/19)
("Identify what code is run in user space vs loaded firmware", High
Priority, Research): the split table of **which function lives in which
world** for every firmware family on the FP6, built from the lab's
committed censuses + public kernel sources. Written 2026-11-17.

**Legend:** [PUBLIC] = public-kernel fact, source cited (torvalds/linux
master files fetched 2026-11-17); [LAB] = lab-derived fact from
committed censuses (qualcomm-fp6/docs/ + results/); [OPEN] = not
establishable from data available here.

## 1. The issue's premise, answered first

The issue hypothesizes that "the AARCH64 executable in the modem.img
blob is potentially the user space part". **It is not.** The AArch64
executables inside `modem/image/` (soter64, smplap64, focal64,
hdcp1/2p2, evautil64, the UUID-named TAs, ...) are **QSEE trusted
applications — TrustZone-side firmware**: they are loaded through the
QSEECOM/SCM path and execute in the secure world, never as Android
user-space code.

- [LAB] The trustzone census identifies them by string inventory as
  TAs (QSEE/GlobalPlatform vocabulary, `.mdt+.bXX` splits); size/hash
  rows in `qualcomm-fp6/results/census.md` cover all 16.
- [PUBLIC] Mainline's QSEECOM plumbing (see the kernel row below)
  talks to SEE applications via SCM calls — a TA's *client* is
  user space, but the TA's code itself executes in the secure world.
- Consistent with the maintainer's own finding on issue #33
  (2026-07-22): these files never pass through an instrumented
  `mdt_loader.c` at boot — because their loader is qseecom, not the
  PIL remoteproc loader.

**The actual user-space** vendor code on this device lives in
`vendor.img`/`system` (HAL executables and `.so` libraries, e.g.
`vendor.qti.bluetooth@1.x`) — a separate partition family from the
firmware images, and *also* proprietary on the stock device. The
kernel-side drivers are the free, mainline-able middle layer.

## 2. The split table, per firmware family

| family | user space (what runs there) | kernel (mainline-able drivers) | loaded firmware (the blob) | driver↔blob boundary |
|---|---|---|---|---|
| Bluetooth | free: BlueZ; stock: Qualcomm vendor BT HAL (patch download + chipset tables) [LAB] | `hci_uart`/`hci_qca` + `btqca` — fully mainline, free [PUBLIC] | WCN6750 ROM + rampatches msbtfw11/12 (**ARM32 Thumb**) + EVROS family mainline cannot name [LAB] | UART HCI + EDL download opcodes 0xFC00/0xFC48; IBS sleep 0xFE/0xFD/0xFC — see [interface-bt-driver.md](interface-bt-driver.md) |
| WiFi | wpa_supplicant (free) + Android HAL [PUBLIC] | `ath11k` (mainline; `ATH11K_HW_WCN6750_HW10` verified in core.c 2026-11-17) or vendor qcacld LKM [PUBLIC] | wpss image: Hexagon (DSP6) code segments + one embedded ELF32 **RV32 QURT** app (wpss.b07) [LAB] | IPCI/ICNSS2 PCIe-style platform + MHI + WMI/HTT/CE; the WMI dispatch spec is the lab's papers/wmi-dispatch-architecture.md |
| Modem (cellular) | RIL daemon (stock proprietary; free alternative = oFono/ModemManager over QRTR/QMI) [PUBLIC] | `mdt_loader` + `qcom_q6v5_mss` + GLINK/rpmsg + `qrtr` + QMI + `rmnet` — all mainline [PUBLIC] | modem.mdt + modem.b00–b30 (**Hexagon**, e_machine 164) + milos/qdsp6m.qdb + per-carrier mcfg payloads [LAB] | PAS authentication via SCM; GLINK/SMEM channels → QRTR → QMI — see [interface-cellular.md](interface-cellular.md) |
| TrustZone / TAs | TEE client libraries only (KeyMint/gatekeeper HALs *talk to* TAs, never execute their code) [PUBLIC] | mainline QSEECOM is the **client-registration layer**: `drivers/firmware/qcom/qcom_qseecom.c` (registers auxiliary client devices; verifies app IDs via `qcom_scm_qseecom_app_get_id`), `qcom_qseecom_uefisecapp.c`, client API `include/linux/firmware/qcom/qcom_qseecom.h`, SCM-side ABI in `qcom_scm.c` — all verified in torvalds/master 2026-11-17. **[OPEN]/[PUBLIC]** the Android-style driver that *loads* arbitrary TA images (`qseecom_load_app`) is not in torvalds master (drivers/tee/qcom/qseecom.c: 404 checked 2026-11-17) — on-device TA loading stays vendor-kernel territory | tz.img (QTEE OS, AArch64, 45 phdrs), hyp.img (QHEE, PIE entry 0x80000000), keymaster/devcfg/uefisecapp/featenabler (AArch64 PIE), modem/image UUID TAs — one TZ build: TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1 [LAB] | SCM call interface; census-only policy per trustzone-census.md |
| DSPs (adsp/cdsp) | FastRPC user libraries (stock proprietary `.so`s) [PUBLIC] | `fastrpc` char devices + `qcom_q6v5_pas` remoteproc (`qcom,milos-adsp-pas` / `qcom,milos-cdsp-pas` verified in the PAS compatible table 2026-11-17) — mainline [PUBLIC] | adsp.img / cdsp.img (**Hexagon**) + bm2nXX-region payloads in `vendor/lib/rfsa/adsp` [LAB] | FastRPC ioctls (compute offload); PAS auth (load) |
| Boot chain | none — runs before any OS [LAB] | none (the kernel is itself loaded by this chain) [LAB] | xbl (3-ELF container: RV32 + AArch64 inner images), xbl_config, shrm/aop/aop_config/cpucp (**RV32**), qupfw (**Hexagon per header**), uefi (AArch64 EFI FV), abl (ARM32), xbl_ramdump (AArch64) [LAB] | PBL → XBL → UEFI → ABL → Linux; AVB verification from vbmeta down (bootchain-census.md) |
| AVB / verified boot | avbctl/userspace verity toggles; the LineageOS userdebug build sets vbmeta flags=3 (hashtree + verification disabled) [LAB] | dm-verity + rmtfs helpers [PUBLIC] | vbmeta.img + vbmeta_system.img (SHA256_RSA4096; rollback_index = the security-patch date as a Unix epoch) [LAB] | vbmeta descriptors → partition hashes; the OEM signing chain ends at Fairphone's "T2MO OEM Key" [LAB] |
| Protected VMs | crosvm/pVM framework (Android 16 side) [PUBLIC] | Gunyah watchdog `drivers/watchdog/gunyah_wdt.c` in mainline (verified 2026-11-17); the fuller VM-lifecycle stack ships with vendor kernels [PUBLIC] | pvmfw.img (raw AArch64 machine code, AVB-verified via a vbmeta_system descriptor) [LAB] | Gunyah SMCCC calls; see [interface-gunyah.md](interface-gunyah.md) |
| NFC | NFC HAL (`libnfc-nci`) [PUBLIC] | `drivers/nfc/*` (in-kernel) [PUBLIC] | firmware inside the NFC controller (no NFC image file in the censused partitions) [LAB] | NCI + vendor fw-download opcodes — see [interface-nfc.md](interface-nfc.md) |
| Housekeeping cores | none — invisible to Android [LAB] | AP-side mailbox only: `drivers/mailbox/qcom-cpucp-mbox.c` (SCMI/RPMH channel, verified 2026-11-17) [PUBLIC] | shrm/aop/aop_config/cpucp RV32 ELFs (shrm carries "DDR_FW version : 19.12.0") [LAB] | SCMI/RPMH mailbox; no user-visible ABI |

## 3. The three-layer rule this table instantiates

The table's headline, worth stating as the answer's general form:

1. **User space** = Android HALs / vendor daemons (proprietary on
   stock; replaceable by free equivalents *that speak the kernel
   interface* — BlueZ, wpa_supplicant, oFono/ModemManager over QRTR).
   **None of the firmware images' code runs here** — the issue's
   AArch64=user-space hypothesis inverts the truth: those images are
   the *most* firmware-side code on the device (secure-world TAs).
2. **Kernel** = the load/auth/transport drivers, all mainline or
   mainline-able (mdt_loader/PAS, qseecom client layer, hci_qca/btqca,
   ath11k, fastrpc, qrtr, qcom-cpucp-mbox). This is the stable,
   documentation-able surface — the part upstream's doc set
   (wifi-driver-interface.md, the planned BT/NFC/cellular docs)
   already targets.
3. **Firmware** = the signed images. User-space-vs-firmware is not one
   binary split but **one split per remote processor**, each with its
   own loader (PIL/mdt_loader for the Hexagon/PIL processors, QSEECOM
   for TAs, hci_qca EDL for BT, ICNSS2/MHI for wpss, XBL/UEFI for the
   boot chain). The ISA map (who executes what) is identified for
   every FP6 family: Hexagon (modem, adsp, cdsp, qupfw, wpss code
   segments), RV32 (wpss.b07, shrm, aop, aop_config, cpucp,
   xbl-inner), ARM32 (BT rampatches, abl), AArch64 (QTEE/QHEE/TAs,
   uefi, xbl core).

[OPEN] The modem blob's own internal structure (Hexagon-side processes
vs the "AARCH64 executable" the issue hypothesized) needs Hexagon
disassembly capacity — stated as open in interface-cellular.md rather
than guessed.

## Sources consulted (accessed 2026-11-17 unless noted)

- Lab committed censuses: `qualcomm-fp6/docs/{bt-firmware-census,bootchain-census,trustzone-census,fp6-architecture-census}.md`, `qualcomm-fp6/results/census.md` (665-file census), `results/bootchain-census.json`, `results/bt-tz-census.json`
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/remoteproc/qcom_q6v5_pas.c — fetched OK, 2,093 lines (PAS compatible list incl. `qcom,milos-{adsp,cdsp,mpss,wpss}-pas`, `qcom,sdm845-adsp-pas`)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/firmware/qcom/qcom_qseecom.c — fetched OK, 120 lines (client-registration driver; `qcom.tz.uefisecapp` app table)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/firmware/qcom/Kconfig — fetched OK (`config QCOM_QSEECOM`, `QCOM_QSEECOM_UEFISECAPP`)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/firmware/qcom/qcom_scm.c — fetched OK (QSEECOM SCM ABI structs)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/tee/qcom/qseecom.c — **404** (checked twice 2026-11-17 — the prior session's "drivers/tee/qcom/qseecom.c" path claim is corrected in this doc: the driver lives under drivers/firmware/qcom/, and TA-image loading is not mainlined)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/mailbox/qcom-cpucp-mbox.c — fetched OK, 231 lines
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/watchdog/gunyah_wdt.c — present (confirmed via GitHub contents API 2026-11-17 after a rate-limited direct fetch)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/wireless/ath/ath11k/core.c — fetched OK (`ATH11K_HW_WCN6750_HW10`, dir `WCN6750/hw1.0`)
- Issue #33 thread (maintainer's own mdt_loader instrumentation, 2026-07-22) — the negative evidence that TAs never pass through PIL
- GitHub API rate-limit note: one contents-API call returned 429 mid-session; retried after delay, recorded per file above

**Clean-room statement:** lab census facts + public-kernel facts only;
no proprietary content, no disassembly beyond committed entry-sanity
checks, no key material.
