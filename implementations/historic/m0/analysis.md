# Samsung Galaxy S III (m0 / GT-I9300) — blob census + Samsung-IPC modem status (2026-11-18)

Third historic-device pass: the Exynos 4412 / Samsung-IPC universe opener.
Per the task brief, this device's documentation is **census + cited
status**, not re-RE of Replicant's work: the modem boot/protocol layer is
already RE'd and FREE (libsamsung-ipc, Replicant heritage); the new lab
delta is the per-file blob census with pins, and the combo-chip pin.

## 1. Combo-chip correction (matches the hammerhead finding)

The queue file and the task context pin m0's WiFi/BT as "BCM4330". The
mainline-verified chip is **BCM4334**: pmOS `device/community/
device-samsung-m0` depends on `firmware-samsung-midas-*` (the Midas board
family = m0/m3/t0lte), and `firmware-samsung-midas` APKBUILD (fetched from
the pmaports GitLab API 2026-11-18) installs:

- `brcmfmac4334-sdio.bin` (mainline brcmfmac4334)
- `brcmfmac4334-sdio.samsung,i9300.txt` — the m0 nvram
- `bcm4334.hcd` — BT patchram
- `p4412_s_fwbl1.bin` — the Midas BL1 bootloader stage

BCM4330 remains the S2/Galaxy-Nexus-era chip (and linux-firmware's
`brcmfmac4330-sdio.bin`, fetched this session for comparison: 223,581 B,
md5 `c6908817b83724800bb76b0114eec7a5`). The two chips share the Broadcom
SDIO-firmware container family (one clean-room parser could serve 4330,
4334, 4335, 4339 — [OPEN] target).

## 2. Provenance and verification (pmOS-pinned, individually fetchable)

`firmware-samsung-midas` APKBUILD pins (fetched + verified 2026-11-18):

| file | source (pinned) | fetched | md5 |
|---|---|---|---|
| `brcmfmac4334-sdio.bin` | linux-firmware `brcm/` @ `id=dc9576448222cc1922462d58796ab1c62b523ada` (pinned commit id in the APKBUILD URL) | 451,566 B | `0e5d2b9bfaaf3b6c43077405cfe92632` |
| `brcmfmac4334-sdio.samsung,i9300.txt` | `armbian/firmware` @ `5ff122ef…` — note: the file served is `brcm/brcmfmac4334-sdio.rockchip%2Crk3318-box.txt` (the APKBUILD renames a shared nvram to the Samsung DT-name; its header comments say "original nvram found in Android sources with name nvram_HS2734A.txt, substituted with a new version") | 2,406 B | in census CSV |
| `bcm4334.hcd` | `TheMuppets/proprietary_vendor_samsung` @ `fdd8c445…`, `smdk4412-common/proprietary/bin/` | 53,957 B | in census CSV |
| `p4412_s_fwbl1.bin` | `dmarszk/exynos4_uboot` @ `2460919…`, `sd_fuse/` | 8,192 B | in census CSV |

The BL1 file deserves its own sentence: pmOS comments it as "subpackage
with bl1 that does not check signature of next bootloader, allowing open
bootloaders like u-boot or xboot. Not yet used by pmOS." — i.e. the
Exynos bootloader blob availability question has a public, already-extracted
answer for the signature-bypass BL1 (the stock signed chain remains
device-resident; Replicant's GalaxySIII table says "Signed" bootloader).
The "exonoma" name in the task context does not resolve to any public
Exynos bootloader project (web + GitHub searches, 2026-11-18, 0 hits) —
recorded as a negative route; the real Exynos 4412 bootloader stack is
BL1 (`p4412_s_fwbl1.bin`) → s-boot (signed, device-resident) with the
U-Boot route above.

## 3. The modem: Samsung-IPC + XMM6260 (cited, not re-RE'd)

All statements in this section are **citations from Replicant's wiki**
(redmine.replicant.us, fetched 2026-11-18, pages retrieved as `.txt`
exports) plus pmOS's packaging of the free userspace:

- `wiki/GalaxySIIIGTI9300` hardware table: Modem = **XMM6260** with "Free
  userspace implementation: Samsung-RIL/libsamsung-ipc"; Wi-Fi = **BCM4334**
  ("Linux kernel support, proprietary loaded firmware"); Bluetooth =
  **BCM4334**. (The queue file's "XMM6262" and the task-context chip name
  are variant labels; Replicant's primary device page pins XMM6260, and
  libsamsung-ipc's i9300 boot functions are the xmm626_hsic_* family.)
- `wiki/GalaxySIII`: GT-I9300 runs Replicant 4.0/4.2/6.0; SoC Exynos 4412;
  bootloader "Signed"; modem link "Isolated (HSIC)"; modem protocol
  **samsung-ipc**. (GT-I9305 = QMI protocol instead, incomplete Replicant
  support — the 4G variant is the different-lineage device.)
- `wiki/GalaxySIIIGTI9300` partition table: RADIO (mmcblk0p7, 32 MiB,
  "Unknown, raw data? — Modem OS partition") is device-resident; EFS
  (mmcblk0p3, ext4) holds the modem data (/efs, nv_data).
- `wiki/Samsung-ipc`: the protocol is implemented free in
  **libsamsung-ipc**, with the Android RIL adapter in libsamsung-ril
  (rild ↔ libsamsung-ril ↔ libsamsung-ipc ↔ kernel); used by S II, S III,
  Note, Note II, Galaxy Nexus, Tab 2, Note 8.0. The pmOS repo packages the
  same library (`pmaports/modem/libsamsung-ipc` — free, packaged).
- `wiki/ModemFirmwarePartitions`: the GT-I9300 modem firmware partition
  layout is DOCUMENTED with byte ranges — TOC `[0x0→0xfff]`,
  PSIRAM (first-stage bootloader) `[0x1000→0xefff]`, EBL
  `[0xF000→0x27fff]`, MAIN (firmware) `[0x28000→0x9fffff]`, SECPACK
  `[0x9ff800→0x9fffff]`, NV (nvdata defaults) `[0xa00000→0xbfffff]` —
  verified on GT-I9300 hardware by Replicant; load functions per stage:
  `xmm626_hsic_psi_send` / `xmm626_hsic_ebl_send` /
  `xmm626_hsic_firmware_send` / `xmm626_hsic_sec_start_send` /
  `xmm626_hsic_nv_data_send` (libsamsung-ipc, free source).
- `wiki/XMMBoot`: the boot sequence (power-off → configure link → send
  firmware → re-enumeration) and per-device GPIO assignments are
  documented; the XMM6262-era modem boots via the HSIC link.
- `wiki/CellularModem` index also documents the Samsung backdoor research
  (SamsungGalaxyBackdoor — the nonfree RIL side), ModemIsolationResearch,
  BackupTheEFS, and the Wireshark dissector (SamsungIpcDissector).

Modem status summary: **the load protocol and userspace are free
(libsamsung-ipc); the modem firmware itself (XMM6260 MAIN section) is the
nonfree blob**, delivered from the radio partition at every boot by the
free loader. The firmware bytes are device-resident (radio partition) and
are NOT re-RE'd here per the task brief and RULE 0 (Replicant's
documentation covers the container; the code inside is the same class of
[OPEN] as every modem code segment).

nv_data (`/efs/nv_data.bin`): the IMEI/RF NV handled by libsamsung-ipc's
`nv_data_*` (documented in BackupTheEFS) — per-device secret-class data,
not part of any repo census.

## 4. What the m0 set adds to the program

- The **Samsung-IPC universe** (S2/S3/Note/Note2/Nexus/Tab2/Note8 + the
  Meizu Pro 5 and Shannon-era devices in the queue) has a free host stack
  and a documented firmware container — the lab's per-device delta for the
  rest of that universe is exactly this kind of census (pins + container
  facts), not protocol RE.
- The **Broadcom SDIO WiFi family** census now spans 4330/4334/4339 across
  three devices (m0/m0-4334, hammerhead-4339, m0-comparison-4330) — a
  clean-room brcm SDIO-firmware parser + nvram generator is the natural
  next implementation target [OPEN].
- pmOS's BL1 note is the concrete Exynos free-bootloader hook (U-Boot on
  Midas exists upstream — `dmarszk/exynos4_uboot` is the packaging repo).

## 5. Files created (this directory)

- `analysis.md` (this file)
- `m0-blob-census.csv` — fetched files with md5 + pinned source

Scratch (regeneratable): `/tmp/astro_w/payloads/m0/`,
`/tmp/astro_w/web/rep_*.txt` (Replicant wiki exports), pmaports APKBUILDs
in `/tmp/astro_w/web/`. Payload bytes NOT committed.
