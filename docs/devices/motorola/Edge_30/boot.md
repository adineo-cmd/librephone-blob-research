# motorola Edge_30 — `boot` family status (10 rows)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#934](https://github.com/adineo-cmd/open-device/issues/934)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 19f87d0), `upstream-contribution/blob-database/device-inventory.csv`, `research/soc/per-soc-method-plans.md` (bootchain grammar, line 415), LineageOS `android_device_motorola_rhodep` extract list (fetched 2026-11-20 for #922), torvalds/linux code search (2026-11-20). Evidence classes: [F] fact (command output) / [I] inference (labeled). No payloads fetched.

**Verdict: the boot family is PRESENT as the complete Qualcomm SM7250 boot-chain image set** — 7 boot-chain images (xbl, xbl_config, abl, aop, cpucp, qupfw, shrm) plus the AOSP verified-boot triple (boot, dtbo, vbmeta), all at `motorola/dubai/radio`. Every md5 is corpus-unique (per-build artifacts); sizes are partition magnitudes shared corpus-wide. Stage roles are labeled [I]; census facts [F].

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 30; codename `dubai` | `device-inventory.csv` (`build_codename=dubai`) [F] |
| SoC | Qualcomm SM7250 Snapdragon 765G | device-inventory.csv [F]; mainline knows SM7250 (7 hits: socinfo.c, rpmhpd.c, clk-rpmh.c, qcom,ids.h, 3 binding yamls — code search 2026-11-20) [F]; no sm7250.dtsi in torvalds master [F] |
| census scope | 338 rows in 9 families (other 88, tz 77, wifi 43, modem 37, adsp 51, cdsp 18, gpu 10, boot 10, bt 4); 805,161,240 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 10 rows [F]

| file | bytes | md5 (upstream DB) | db_type | stage role [I] |
|---|---:|---|---|---|
| xbl.img | 5,242,880 | `95cee5ee147b04991159c89c6462e8ed` | UEFIBOOT | XBL — primary bootloader (UEFI-based, eXtensible Boot Loader) |
| xbl_config.img | 262,144 | `b969b23ee6aed93840fd943e409f3a85` | ELF64 | XBL config fragment |
| abl.img | 1,048,576 | `7aacfae9b3176d7adb659d4c59af02ce` | UEFIBOOT | ABL — Android bootloader (AOSP bootloader, loads boot.img, fastboot) |
| aop.img | 524,288 | `dc5d662535b4031c8bc8f5f5da751715` | UNKNOWN | AOP — Always-On Processor firmware |
| cpucp.img | 1,048,576 | `9d3375f5a84dee2dec96390bcf4c523c` | UNKNOWN | CPU Control-Plane firmware |
| qupfw.img | 81,920 | `297f1bb8c22772c6e741a32a441571d6` | ELF64 | QUP serial-engine firmware (I2C/SPI/UART cores, loaded before Linux drivers run) |
| shrm.img | 131,072 | `2709d9f02afe1118633def452597a8f8` | ELF64 | shared-memory boot firmware for the low-power island |
| boot.img | 100,663,296 | `a660df562a45d54424f672f69fbf98ca` | BOOT | AOSP boot image (kernel + ramdisk) |
| dtbo.img | 25,165,824 | `17299d9a11434d45c902e371dccb23b9` | DTB | AOSP device-tree overlay image |
| vbmeta.img | 8,192 | `8a8e558669adb3fcce04216328517a3f` | AVB | AVB metadata chaining the verified-boot hash tree |

All rows match the repo's bootchain grammar (`xbl/abl/aop/shrm/cpucp/qupfw/uefi/vbmeta/dtbo/...`, `research/soc/per-soc-method-plans.md:415`) [F]. The `.elf`/`.mbn` → `.img` naming law is corroborated on sibling Moto hardware by the rhodep extract list (`abl.elf:abl.img;AB`, `qupfw.elf:qupfw.img;AB`, `xbl.elf:xbl.img;AB`, `xbl_config.elf:xbl_config.img;AB` — fetched 2026-11-20) [F].

## Cross-corpus facts [F]

- All seven boot-chain md5s are **corpus-unique to Edge_30** — per-build signed images, as expected for boot chain stages.
- xbl.img 5,242,880 B is the modal-magnitude variant (10 rows corpus-wide at exactly this size, 10 more at 5,238,784); same-SoC Pixel_4A_5G carries xbl.img 3,604,480 B — boot-chain builds differ per vendor even within one SoC.
- Same-grammar contrast (SM7250 sibling, 8 boot rows): Pixel_4A_5G has **no cpucp.img/shrm.img rows** and smaller aop (196,608) / qupfw (57,344) / xbl_config (81,920) — the dubai extract carries two extra peripheral-core images, a vendor-extract-scope difference, not a device difference provable from metadata.
- dtbo 25,165,824 B = modal corpus size (72/118 rows); boot.img 96 MiB = the 53-device corpus magnitude; vbmeta 8,192 B = modal (94/115 rows).

## ISA proof and interface facts

- `isa_identified=ELF64` in the matrix for xbl_config, qupfw, shrm [F]; xbl/abl carry db_type UEFIBOOT [F]; aop/cpucp bintypes UNKNOWN [F]. Deeper ISA/structure proof needs payloads — [OPEN].
- Interface [I, labeled]: XBL→ABL→Linux boot chain; boot/dtbo/vbmeta verified by AVB at boot; boot-chain images are flashed to their own partitions via fastboot and never read as filesystem files by Android (the same mechanism that makes them absent from extract-based censuses — see #922's berlna analysis).
- Evidence class: all 10 rows P3, metadata-only [F].

## Honest negatives

- Stage-role table is [I]: no public source enumerates dubai's boot-chain contents; roles follow standard Qualcomm SM7250 firmware practice plus the rhodep naming law. A factory flashfile.xml would upgrade every [I] to [F]. [OPEN]
- ELF internals (xbl_config/qupfw/shrm headers, machine type) are unverified from metadata. [OPEN]
- Whether dubai's factory image also ships devcfg/hyp/keymaster/uefisecapp (the #922 rhodep set) is out of this issue's family — they would be tz-family rows and Edge_30's tz census (77 rows) already covers them. [F — see coverage]

## What would upgrade this finding

1. dubai factory flashfile partition list → per-stage [F] confirmation + exact build provenance.
2. Payload fetch: parse xbl/abl UEFI volumes and the three ELF64 images; extend `research/qualcomm/docs/bootchain-census.md` (FP6-only today) with an SM7250 row.

## RULE 0 record (2026-11-20)

Queries in the SEARCH/NO-PRIOR-ART comments. Prior-art check: `dubai xbl abl firmware` (GitHub code search, adineo-cmd/* excluded) → guides only; `sm7250 repo:torvalds/linux` → 7 driver/binding hits, no dtsi; `qupfw repo:torvalds/linux` → 0. Nobody documents dubai's boot chain.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public specs and the cited sibling extract.
