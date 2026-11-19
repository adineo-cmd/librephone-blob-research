# External firmware and blob code directory

Verified 2026-11-20 by opening each URL (HTTP 200) or confirming its source
page. This is the curated set the website publishes; the machine-readable
version is `site/data/links.csv` (39 rows).

Facts-not-blobs: these are links to code and documentation, not repositories
this lab claims to own. Nothing here is re-published.

## By firmware family

### adsp (4)

- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.
- [Ghidra MediaTek firmware loader](https://github.com/nccgroup/ghidra-mtk-loader) — NCC Group. Ghidra loader for MediaTek firmware images. Licence: GPL-3.0-only.
- [qcom_q6v5_pas remoteproc loader](https://github.com/torvalds/linux/blob/master/drivers/remoteproc/qcom_q6v5_pas.c) — Linux Foundation. Qualcomm remote processor loader for ADSP and CDSP. Licence: GPL-2.0-only.
- [MediaTek audio DSP vulnerability research](https://research.checkpoint.com/2021/looking-for-vulnerabilities-in-mediatek-audio-dsp) — Check Point Research. Public vulnerability research on the MediaTek audio DSP firmware format. Licence: no single declared SPDX licence.

### boot (5)

- [barebox](https://barebox.org) — barebox. Free bootloader and bring-up toolkit for embedded systems with Linux-compatible driver frameworks. Licence: no single declared SPDX licence.
- [coreboot](https://github.com/coreboot/coreboot) — coreboot. coreboot: open firmware for booting devices with blob-free or reduced-blob paths. Licence: GPL-2.0-only.
- [U-Boot](https://github.com/u-boot/u-boot) — U-Boot project. U-Boot: the bootloader most ARM boards and TV boxes use. Licence: no single declared SPDX licence.
- [Libreboot](https://libreboot.org) — Libreboot. Free/open boot firmware based on coreboot, with binary-blob removal on supported hardware. Licence: no single declared SPDX licence.
- [coreboot project](https://www.coreboot.org) — coreboot. Open-source boot firmware replacing proprietary BIOS/UEFI on computers and embedded devices. Licence: no single declared SPDX licence.

### bt (4)

- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.
- [linux-wireless integration tree](https://git.kernel.org/pub/scm/linux/kernel/git/johannes/linux-wireless.git) — Linux Foundation. linux-wireless integration tree, where WiFi and BT driver changes land before mainline. Licence: GPL-2.0-only.
- [btqca Bluetooth firmware loader](https://github.com/torvalds/linux/blob/master/drivers/bluetooth/btqca.c) — Linux Foundation. Qualcomm Bluetooth firmware loading and patch download, mainline. Licence: GPL-2.0-only.
- [hci_qca HCI transport driver](https://github.com/torvalds/linux/blob/master/drivers/bluetooth/hci_qca.c) — Linux Foundation. Qualcomm HCI transport driver, mainline. Licence: GPL-2.0-only.

### cdsp (1)

- [qcom_q6v5_pas remoteproc loader](https://github.com/torvalds/linux/blob/master/drivers/remoteproc/qcom_q6v5_pas.c) — Linux Foundation. Qualcomm remote processor loader for ADSP and CDSP. Licence: GPL-2.0-only.

### gpu (1)

- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.

### modem (8)

- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.
- [OsmocomBB](https://gitea.osmocom.org/phone-side/osmocom-bb) — Osmocom. Free software GSM baseband firmware and L1/L2/L3 protocol stack. Licence: no single declared SPDX licence.
- [MediaTek LTE baseband reverse engineering](https://github.com/cyrozap/mediatek-lte-baseband-re) — cyrozap. MediaTek LTE baseband reverse-engineering notes and tools. Licence: GPL-3.0-only.
- [FirmWire](https://github.com/firmwire/firmwire) — FirmWire. Full-system baseband firmware emulation platform for fuzzing and debugging. Licence: no single declared SPDX licence.
- [Ghidra MediaTek firmware loader](https://github.com/nccgroup/ghidra-mtk-loader) — NCC Group. Ghidra loader for MediaTek firmware images. Licence: GPL-3.0-only.
- [LibreCellular](https://librecellular.org) — LibreCellular. Open-source 4G cellular networks using software-defined radio and validated open software. Licence: no single declared SPDX licence.
- [SRLabs Hexagon fuzzing](https://srlabs.de/blog/hexagon-fuzz-full-system-emulated-fuzzing-of-qualcomm-basebands) — SRLabs. Open-source toolchain for full-system emulated fuzzing of Hexagon firmware. Licence: no single declared SPDX licence.
- [Osmocom projects](https://www.osmocom.org/projects) — Osmocom. Free/open-source GSM/3G core network and phone-side protocol implementations. Licence: no single declared SPDX licence.

### other (15)

- [FSF LibrePhone repository](https://codeberg.org/rsavoye/librephone) — FSF. The FSF LibrePhone project's own repository: blob research notes and tooling. Licence: no single declared SPDX licence.
- [Router firmware list](https://en.wikipedia.org/wiki/List_of_router_firmware_projects) — Wikipedia. Index of third-party router firmware projects. Licence: no single declared SPDX licence.
- [LibreELEC](https://github.com/LibreELEC/LibreELEC.tv) — LibreELEC. LibreELEC: minimal OS images for TV boxes and single-board computers. Licence: no single declared SPDX licence.
- [Ghidra NanoMIPS module](https://github.com/nccgroup/ghidra-nanomips) — NCC Group. Ghidra processor module for the MIPS NanoMIPS instruction set. Licence: GPL-3.0-only.
- [awesome-firmware](https://github.com/open-source-firmware/awesome-firmware) — Open Source Firmware Foundation. Curated list of open-source firmware projects and their use cases. Licence: CC-BY-SA-4.0.
- [postmarketOS](https://github.com/postmarketOS) — postmarketOS. postmarketOS: mainline-Linux mobile distributions and device ports. Licence: no single declared SPDX licence.
- [binwalk](https://github.com/ReFirmLabs/binwalk) — ReFirmLabs. binwalk: firmware image extraction and entropy analysis. Licence: MIT.
- [Replicant archive](https://github.com/replicant-archive) — Replicant. Archived Replicant source repositories on GitHub. Licence: no single declared SPDX licence.
- [pmaports](https://gitlab.postmarketos.org/postmarketOS/pmaports) — postmarketOS. Device packages that define postmarketOS port coverage. Licence: no single declared SPDX licence.
- [LibrePhone hardware index](https://librephone.fsf.org/hardware) — FSF. LibrePhone hardware compatibility index and project status. Licence: no single declared SPDX licence.
- [OSFF projects list](https://opensourcefirmware.foundation/projects) — Open Source Firmware Foundation. Non-profit foundation listing open-source firmware projects. Licence: no single declared SPDX licence.
- [OpenWrt project site](https://openwrt.org) — OpenWrt. Router and embedded-device Linux distribution; docs, package sources and device support lists. Licence: no single declared SPDX licence.
- [Replicant source repositories](https://redmine.replicant.us/projects/replicant/wiki/SourceCodeRepositories) — Replicant. Where the fully free Android distribution keeps its source repositories. Licence: no single declared SPDX licence.
- [Debian Open Firmware wiki](https://wiki.debian.org/Firmware/Open) — Debian. Wiki list of open firmware projects, licences and status. Licence: no single declared SPDX licence.
- [Osmocom projects](https://www.osmocom.org/projects) — Osmocom. Free/open-source GSM/3G core network and phone-side protocol implementations. Licence: no single declared SPDX licence.

### tz (1)

- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.

### wifi (11)

- [Router firmware list](https://en.wikipedia.org/wiki/List_of_router_firmware_projects) — Wikipedia. Index of third-party router firmware projects. Licence: no single declared SPDX licence.
- [linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git) — Linux Foundation. Upstream linux-firmware tree: the vendor blob payloads themselves. Licence: no single declared SPDX licence.
- [ath10k board data in linux-firmware](https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/ath10k) — Linux Foundation. ath10k board data and firmware blobs in linux-firmware. Licence: no single declared SPDX licence.
- [linux-wireless integration tree](https://git.kernel.org/pub/scm/linux/kernel/git/johannes/linux-wireless.git) — Linux Foundation. linux-wireless integration tree, where WiFi and BT driver changes land before mainline. Licence: GPL-2.0-only.
- [OpenWrt](https://github.com/openwrt/openwrt) — OpenWrt. OpenWrt: router and embedded Linux distribution with extensive WiFi support. Licence: no single declared SPDX licence.
- [QCA Swiss Army Knife](https://github.com/qca/qca-swiss-army-knife) — Qualcomm. Qualcomm Atheros WiFi board-data and calibration tooling. Licence: no single declared SPDX licence.
- [ath10k WiFi driver](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/ath/ath10k/) — Linux Foundation. Qualcomm Atheros ath10k WiFi driver, mainline. Licence: GPL-2.0-only.
- [mt76 WiFi driver family](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/mediatek/mt76/) — Linux Foundation. MediaTek mt76 WiFi driver family, mainline. Licence: GPL-2.0-only.
- [rtw88 WiFi driver](https://github.com/torvalds/linux/blob/master/drivers/net/wireless/realtek/rtw88/) — Linux Foundation. Realtek rtw88 WiFi driver, mainline. Licence: GPL-2.0-only.
- [OpenWrt project site](https://openwrt.org) — OpenWrt. Router and embedded-device Linux distribution; docs, package sources and device support lists. Licence: no single declared SPDX licence.
- [Linux wireless wiki](https://wireless.wiki.kernel.org/) — Linux Foundation. Linux wireless subsystem documentation and driver status. Licence: no single declared SPDX licence.

