# Nexus 5 hammerhead — real-payload blob census + RE (2026-11-18)

Second historic-device RE pass: the Nexus 5 (MSM8974, the most-flashed
8974 device, ABSENT from the upstream 249). Every obtainable firmware blob
was located from public, **independently hash-pinned** sources (postmarketOS
pmaports pins), fetched, verified, and run through the lab's clean-room
`mdt_probe.py` (`implementations/historic/fp2/mdt_probe.py` — same parser,
fixture-tested). This file documents the real bytes per parsed byte range;
payloads stay in `/tmp/astro_w/payloads/hh/` only.

**Combo-chip correction (the session's headline finding):** the queue file
(`historic-devices/historic-devices-queue.md`, §queue row + §App B) pins
hammerhead's combo as "WCN3680 prima". That is **wrong** — verified against
three primary sources on 2026-11-18:

1. `CyanogenMod/android_device_lge_hammerhead` `BoardConfig.mk` (cm-13.0):
   `BOARD_WLAN_DEVICE := bcmdhd`, driver fw paths `/vendor/firmware/fw_bcmdhd.bin`
   — the stock WiFi is Broadcom, driven by bcmdhd;
2. Google's own public driver package `broadcom-hammerhead-m4b30z-*.tgz`
   (the stock extraction, pmOS-pinned) ships `bcm4335c0.hcd` (Bluetooth) +
   `bcm2079x-b5_firmware.ncd` (NFC) — Broadcom BT/NFC;
3. pmOS `firmware-lg-hammerhead` ships `brcmfmac4339-sdio.txt` (BCM4339
   srom nvram, "for 4339 iPA/eLNA / AARDVARK_6_30_271") — the mainline WiFi
   is **brcmfmac4339**, i.e. Broadcom BCM4339 WiFi.

hammerhead has **no WCNSS/prima firmware at all**: its radio partition
contains only modem + mba (verified — the fetched modem archive has 22
files, none named wcnss/WCNSS; the AOSP-era extraction lists no prima
files either). The FP2, not the Nexus 5, is the WCN3680-prima representative
of the MSM8974 fleet (see `implementations/historic/fp2/fleet-analysis.md`).

## 1. Provenance and verification (all pmOS-pinned, all MATCH)

pmaports `device/testing/firmware-lg-hammerhead` APKBUILD (fetched from the
GitLab API 2026-11-18) pins four sources; each was fetched and
sha512-verified byte-exact:

| source | pmOS sha512 pin | result |
|---|---|---|
| `gitlab.com/JuniorJPDJ/hammerhead-modem` @ `d0565ebb…` (`hammerhead-modem-*.tar.gz` — extracted radio modem partition, `image/`) | `a63a0fad…8a` | **MATCH** (22,416,262 B) |
| `dl.google.com/dl/android/aosp/qcom-hammerhead-m4b30z-d6c0fe26.tgz` (Google's public qcom driver package) | `a421b547…df2` | **MATCH** |
| `dl.google.com/dl/android/aosp/broadcom-hammerhead-m4b30z-21cf8433.tgz` (Google's public broadcom driver package) | `003502ff…ed0` | **MATCH** |
| `brcmfmac4339-sdio.txt` (committed in the pmaports package itself) | `59baf815…345` | **MATCH** |

Negatives (routes tried, recorded per RULE 0):

- TheMuppets `proprietary_vendor_lge` @ lineage-15.1/16.0/17.1
  `hammerhead/` tree (506 files enumerated): **no modem/wcnss/WCNSS NV
  firmware** — only adsp/venus/cmnlib/keymaster/widevine/discretix images +
  userspace libs. hammerhead firmware comes from the radio partition, not
  the vendor tree (the CM `extract-files.sh` extracts from adb, i.e. a
  provisioned device).
- `LineageOS/android_device_lge_hammerhead` tree: no wlan/prima files, no
  root/firmware dir (device-side only).
- linux-firmware `brcm/` directory listing (kernel.org cgit, fetched
  2026-11-18): contains `brcmfmac4330-sdio.bin` but **no
  `brcmfmac4339-sdio.bin`** — the hammerhead WiFi chip's firmware bin is
  not in linux-firmware; only the nvram txt is pinned by pmOS (the .bin
  must come from device trees/vendor OTA `fw_bcmdhd.bin` — same chip image
  family as the 4330/4335). [OPEN] route for a clean bin source.

## 2. modem.mdt — MPSS.DI.2.0.C5 image, per-byte-range map

Same container family as FP2 (machine 164 = EM_QDSP6, entry 0x08000000,
not relocatable, 0x08000000–0x0d100000, `.mdt == .b00‖.b01` duplication —
verified byte-for-byte here: 8156 = 884 + 7272). Build ID strings (factual
metadata) from `modem.b13/b18`:
`QC_IMAGE_VERSION_STRING=MPSS.DI.2.0.C5-00024`, carrier build
`VU_MODEM_FW_LTE_MPSS_DI_2_0_C5.02.06.52.04.04`, CRM build stamp
2014-09-03.

| file | flags | filesz | memsz | paddr | note |
|---|---|---|---|---|---|
| b00 | 0x07000000 | 884 | 0 | — | ehdr + 26 phdrs (52+832) |
| b01 | 0x02200000 | 7,272 | 8,192 | 0x0d100000 | hash segment |
| b02 | 5 | 3,284 | 3,284 | 0x08000000 | RX |
| b03 | 7 | 81,920 | 81,920 | 0x08010000 | RXW |
| b06 | 7 | 179,305 | 179,305 | 0x08024000 | RXW |
| b08 | 7 | 47,860 | 122,984 | 0x08054000 | RXW+BSS |
| b09 | 7 | 50,884 | 50,884 | 0x08078000 | RXW |
| b11 | 7 | 106,488 | 106,488 | 0x0808c000 | RXW |
| b12 | 5 | 104,856 | 104,856 | 0x080ac000 | RX |
| b13 | 5 | 1,381,296 | 1,381,296 | 0x080d0000 | RX |
| b14 | 5 | **30,721,712** | 30,721,712 | 0x08222000 | main code (larger than FP2's 19.3 MB) |
| b15 | 6 | 663,456 | 663,456 | 0x09f80000 | RW |
| b16 | 6 | 73,728 | 73,728 | 0x0a024000 | RW |
| b17 | 6 | 5,376 | 5,376 | 0x0a038000 | all-zero RW (md5 `c4ca1e4b…` = FP2's b17, §FP2 doc 2.5) |
| b18 | 4 | 7,504,488 | 7,504,488 | 0x0a040000 | R |
| b19 | 6 | 3,762,568 | 3,762,568 | 0x0a76a000 | RW |
| b20 | 6 | 0 | 1,375,972 | 0x0ab01000 | pure BSS |
| b21 | 6 | 0 | 35,040,448 | 0x0ac52000 | pure BSS |
| b22 | 6 | 270,840 | 270,840 | 0x0cdbd000 | RW |
| b23 | 4 | 736,468 | 736,468 | 0x0ce00000 | R |
| b24 | 4 | 378,600 | 378,600 | 0x0ceb4000 | R |
| b25 | 4 | 0 | 2,027,520 | 0x0cf11000 | pure BSS |

Σ p_filesz 46,081,285 B on disk (probe-verified == segment files), +38.5 MB
BSS. phdr 4,5,7,10 are zero placeholders (as in FP2). `mba.mdt`: 1 phdr,
PT_LOAD 0x0d800000–0x0d839b70 (MBA at a different offset than FP2's
0x0d100000 — the boot-allocator address differs per board).

FP2-vs-hammerhead modem comparison: 12/26 identical paddr, 8/26 identical
filesz; byte-identical segments = the all-zero b17 only. Two 8974 builds,
zero shared code bytes — the free-specification delta is the container +
loader (done) and the per-build synthesis question [OPEN].

## 3. adsp.mdt (from Google's qcom package)

machine 164, 14 phdrs, entry 0x0dc00000, **not relocatable** (vs FP2's
relocatable adsp — per-chip/brand difference), range 0x0dc00000–0x0f000000,
13 segment files on disk, Σ filesz 9,296,139 B, +10.7 MB BSS. b03 = the
5,039,216 B main segment. Notable: b02 is a 1-byte PT_LOAD with R flag at
0x0e3424f0 and b08 a 120-byte RW blob — tiny segments the loader streams
like any other.

## 4. Broadcom BT/NFC (from Google's broadcom package)

- `bcm4335c0.hcd` — 72,299 B, md5 `d39b8d63936ca939d01f2d5f6d9d545f`: the
  BCM4335C0 Bluetooth HCD patchram. HCD = Broadcom's patchram format
  (documented publicly in btusb/brcm patchram sources); class = H4
  patchram download, NOT QCA-TLV.
- `bcm2079x-b5_firmware.ncd` (10,101 B) + `_pre_firmware.ncd` (571 B) —
  the Broadcom NFC controller firmware.

These confirm the third Broadcom family member of the historic fleet
(BCM4330 = m0-era, BCM4334 = m0 per pmOS, BCM4335/4339 = hammerhead, cf.
`implementations/historic/m0/analysis.md`).

## 5. What this means for a free reimplementation

- Same conclusions as FP2 §4 for the modem: container/loader fully
  specified and machine-verified here; modem code synthesis [OPEN]; the
  hash-segment signature question [OPEN].
- WiFi mainline path is ALREADY free on the host side (brcmfmac4339) — the
  remaining blob is the BCM4339 firmware bin itself (not in linux-firmware,
  see negative route above) and the nvram txt (pmOS-committed, fetched).
- BT mainline path (btusb + bcm4335c0.hcd) is the same Broadcom patchram
  class as m0's bcm4334.hcd — one clean-room HCD tool could serve the
  whole Broadcom BT historic fleet [OPEN as parser target].

## 6. Files created (this directory)

- `fleet-analysis.md` (this file)
- `hammerhead-blob-census.csv` — 56 firmware files with md5 + source
- (parsers shared with `implementations/historic/fp2/`: `mdt_probe.py`,
  fixtures, tests)

Scratch (regeneratable): `/tmp/astro_w/payloads/hh/` (modem archive,
qcom/broadcom packages, nvram), `/tmp/astro_w/analysis/hh_*.json`,
`/tmp/astro_w/web/muppets_hh_tree.txt`. Payload bytes NOT committed.
