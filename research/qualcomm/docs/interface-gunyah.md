# What the Gunyah hypervisor is used for (FP6) — for upstream issue #39

One-page note from **public data + lab-derived facts**
([upstream issue #39](https://codeberg.org/rsavoye/librephone/issues/39):
"I noticed in the boot logs a mention of the Gunyah hypervisor, which
is a free software project maintained by Qualcomm. What is this used
for ?"). Written 2026-11-16.

**Legend:** [PUBLIC] = public fact; [LAB] = lab-derived fact; [OPEN] =
not establishable from data on this box.

## 1. What Gunyah is

- [PUBLIC] Gunyah is Qualcomm's open-source **Type-1 hypervisor** —
  its own description: "Gunyah is a Type-1 hypervisor designed for
  strong security, performance and modularity"
  (`github.com/quic/gunyah-hypervisor`, accessed 2026-11-16). A Type-1
  hypervisor runs below the OS: the kernel (Linux) becomes one guest,
  and Gunyah multiplexes the CPU/other resources between it and
  **protected VMs (pVMs)** — isolated secondary VMs for things like
  trusted execution environments, DRM media paths, or OEM services,
  each verified at boot (the Android "pvmfw" = protected-VM firmware
  mechanism).
- [PUBLIC] Kernel-side, the mainline tree ships the Gunyah
  **watchdog** driver speaking Gunyah's SMCCC hypercall convention
  (fast calls, owner `ARM_SMCCC_OWNER_VENDOR_HYP`, functions
  0x0005–0x0008: CONTROL/STATUS/PING/SET_TIME, and the public
  `gunyah_error` enum) — `drivers/watchdog/gunyah_wdt.c`,
  `torvalds/linux` (fetched 2026-11-16). The fuller Gunyah driver
  stack (VM lifecycle, resource manager RPC) has been posted upstream
  over the years but is **not** in `torvalds/master` as of
  2026-11-16 (checked: `drivers/virt/` has no `gunyah`; both probed
  2026-11-16) — on Android devices it comes with the vendor kernel.
- [PUBLIC] Qualcomm's reference hypervisor implementation and docs
  are public at `github.com/quic/gunyah-hypervisor`.

## 2. What it is used for on FP6

- [PUBLIC/asker's evidence] FP6 boot logs mention Gunyah — i.e., the
  device boots Linux **under** the Gunyah hypervisor, not bare-metal:
  Linux is guest 0, and the hypervisor owns the boot chain handoff.
- [LAB] The FP6 OTA carries the supporting partition set:
  `pvmfw` (protected-VM firmware, 1,048,576 B; AVB-verified with a
  descriptor in `vbmeta_system`; built from source by LineageOS) and
  `vbmeta_system` descriptors covering pvmfw/product/system/system_ext
  — `qualcomm-fp6/docs/bootchain-census.md`. That is the standard
  Android pKVM/pVM arrangement Gunyah hosts.
- [LAB] The AP's second stage also ships the classic QTEE/QHEE pair:
  `tz.img` (QTEE OS) + `hyp.img` (QHEE hypervisor, one TZ build
  `TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1`) —
  `qualcomm-fp6/docs/trustzone-census.md`. Relation: QHEE/Gunyah-style
  pVM hosting operate at different layers of the secure-boot stack;
  which exact combination the shipping FP6 firmware orchestrates is
  **[OPEN]** from committed data (needs the boot-log ↔ image mapping
  on hardware).
- [LAB, the F-8 cross] Gunyah (AP-side pVM hypervisor) is distinct
  from the QURT microkernel the lab identified on the WPSS small core
  (`qualcomm-fp6/docs/wpss-qurt-rtos.md`): same vendor lineage of
  microkernel-style RTOS/hypervisor software, different processors
  and roles — worth stating so "Gunyah" and "QURT" are not conflated.

## 3. Bottom line for the issue

Gunyah on FP6 = the chip vendor's free, open-source hypervisor that
boots before Linux and hosts protected VMs (pvmfw-verified) next to
the Android host; Linux talks to it over SMCCC vendor-hyp hypercalls.
For LibrePhone purposes: the hypervisor itself is **free software**
(the goal state of the campaign), the interesting RE surface is the
blob-side firmware and the pVM boundary, both already partially
censused by the lab.

## Sources consulted (accessed 2026-11-16)

- https://api.github.com/repos/quic/gunyah-hypervisor (repo metadata,
  description quoted)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/watchdog/gunyah_wdt.c (fetched)
- probes that returned 404 (recorded as honest negatives):
  `drivers/virt/gunyah/*`, `Documentation/virt/gunyah/*`,
  `include/linux/gunyah.h` in `torvalds/master`
- Lab: `qualcomm-fp6/docs/bootchain-census.md` (pvmfw/vbmeta_system),
  `qualcomm-fp6/docs/trustzone-census.md` (QTEE/QHEE),
  `qualcomm-fp6/docs/wpss-qurt-rtos.md` (F-8 QURT)

**Clean-room statement:** public facts + lab census facts only; no
hypervisor internals, no keys, no bypass content.
