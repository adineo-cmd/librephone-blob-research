# fairphone FP4 — `boot` family status (9 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#970](https://github.com/adineo-cmd/open-device/issues/970)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 8dffa67), `upstream-contribution/blob-database/device-inventory.csv`, `research/soc/per-soc-method-plans.md` (bootchain grammar), torvalds/linux code search (2026-11-21). Evidence classes: [F] fact / [I] inference (labeled). No payloads fetched.

**Verdict: the boot family is PRESENT as an SM7225 boot-chain image set** — 9 rows at `fairphone/FP4/radio`: xbl, xbl_config, abl, aop, qupfw + AOSP boot/dtbo/vbmeta **plus recovery.img** (FP4 is one of the few corpus devices whose radio census carries recovery). All 9 md5s corpus-unique. Fairphone's boot-chain builds are markedly smaller than Moto's on comparable SoCs — a vendor-build fact, recorded per row.

## Device identity

| fact | value | source |
|---|---|---|
| model | Fairphone 4; codename `FP4` | `device-inventory.csv` (`build_codename=FP4`) [F] |
| SoC | Qualcomm SM7225 Snapdragon 750G | device-inventory.csv [F]; **mainline carries `arch/arm64/boot/dts/qcom/sm7225-fairphone-fp4.dts`** + `sm7225.dtsi` (torvalds master, code search 2026-11-21 — 10 sm7225 hits incl. socinfo/pd_mapper) [F] — FP4 has real mainline DT support, consistent with the inventory's P2 mainline-effort note |
| priority | **P2** — public mainline/pmOS effort noted in the inventory (`Fairphone 4 (sm7225): vendor-backed mainline effort + pmOS port`) | device-inventory.csv [F] |
| census scope | 286 rows in 9 families (other 69, wifi 44, tz 61, adsp 37, modem 37, bt 14, cdsp 12, boot 9, gpu 3); 689,737,383 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 9 rows [F]

| file | bytes | md5 (upstream DB) | db_type | stage role [I] |
|---|---:|---|---|---|
| xbl.img | 3,379,200 | `fb0d533c4d0e87571758dcc5ed962653` | UEFIBOOT | XBL — primary bootloader (UEFI-based) |
| xbl_config.img | 98,304 | `64f35bd5b1886b63ee71c3a414882ddd` | ELF64 | XBL config fragment |
| abl.img | 155,648 | `6685fdfa7107a65cac61b42d25fe2e6c` | UEFIBOOT | ABL — Android bootloader (AOSP, fastboot) |
| aop.img | 180,224 | `168c523cb9f87f3e5fa329c4d36fdca4` | UNKNOWN | AOP — Always-On Processor firmware |
| qupfw.img | 57,344 | `114393dcd07b4d4563bf74bfd723da75` | ELF64 | QUP serial-engine firmware (I2C/SPI/UART) |
| boot.img | 100,663,296 | `8e090fdca26f3dfe6844d5c391951c37` | BOOT | AOSP boot image (kernel + ramdisk) |
| recovery.img | 100,663,296 | `2850d305032c3b922b7aa196bede87bd` | BOOT | AOSP recovery image |
| dtbo.img | 25,165,824 | `c5398b49fba9d3dfeb8d0c44a4d004ad` | DTB | AOSP device-tree overlay image |
| vbmeta.img | 8,192 | `df8854d757da64286daa0dd427de598c` | AVB | AVB metadata |

All 9 match the repo's bootchain grammar [F]; stage roles [I] labeled per the #934 pattern.

## Cross-corpus facts [F]

- All 9 md5s **corpus-unique to FP4** — per-build signed images.
- **recovery.img is the distinguishing row**: FP4's radio census carries recovery.img at 100,663,296 B (the 96-MiB magnitude) — the Moto slices (berlin/berlna/dubai/miami) have no recovery row, while Samsung devices carry recovery at different magnitudes (36-71 MiB). Extract-scope difference ([OPEN]: platform vs scope).
- **Vendor build sizes are smaller than Moto's** on the boot chain: xbl 3,379,200 vs the Moto 5,242,880 magnitude; abl 155,648 vs Moto 1,048,576; xbl_config 98,304 vs 262,144. Same grammar, different vendor builds — sizes are not SoC constants across vendors.
- aop.img present (180,224 B) — miami (SM6375) lacks it, dubai (SM7325-AE) has it at 524,288 B. qupfw 57,344 B equals Pixel_4A_5G's size.
- boot.img/dtbo/vbmeta sizes are the corpus constants (96 MiB / 24 MiB / 8,192 B).

## ISA proof and interface facts

- `isa_identified=ELF64` for xbl_config, qupfw [F]; xbl/abl db_type UEFIBOOT; aop UNKNOWN [F]. Deeper structure needs payloads — [OPEN].
- Interface [I, labeled]: XBL→ABL→Linux chain; AVB verifies boot/dtbo/recovery. FP4's mainline/pmOS relevance makes the boot chain the natural first payload target of the whole P2 slice.
- Evidence class: all 9 rows P3, metadata-only [F].

## Honest negatives

- Stage roles [I]; no public source enumerates FP4's boot-chain contents. [OPEN]
- recovery-vs-no-recovery and per-vendor size differences remain extract-scope vs platform questions from metadata alone. [OPEN]

## What would upgrade this finding

1. FP4 factory/LineageOS flashfile partition list → per-stage [F] confirmation.
2. Payload fetch (highest value on a P2 device): parse xbl/abl UEFI volumes + the two ELF64 images; add an SM7225 row to `research/qualcomm/docs/bootchain-census.md`.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `FP4 xbl abl firmware boot` (GitHub code search, adineo-cmd/* excluded) → device trees/guides only. Nobody documents FP4's boot rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public specs.
