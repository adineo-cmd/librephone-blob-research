# motorola Edge_30_Neo — `boot` family status (8 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#952](https://github.com/adineo-cmd/open-device/issues/952)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 98a360a), `upstream-contribution/blob-database/device-inventory.csv`, `research/soc/per-soc-method-plans.md` (bootchain grammar), LineageOS wiki rhodep page (fetched 2026-11-20 for #922). Evidence classes: [F] fact / [I] inference (labeled). No payloads fetched.

**Verdict: the boot family is PRESENT as an SM6375 boot-chain image set** — 8 rows at `motorola/miami/radio`: xbl, xbl_config, abl, qupfw, rpm + the AOSP triple (boot, dtbo, vbmeta). Notably **no aop/cpucp/shrm rows** (contrast dubai's 10) but **rpm.img present** (the PMIC power-manager firmware dubai lacks). All 8 md5s corpus-unique.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 30 Neo; codename `miami` | `device-inventory.csv` (`build_codename=miami`) [F]; public listings + the corpus paths (`motorola/miami/`) [F] |
| SoC | Qualcomm SM6375 Snapdragon 695 | device-inventory.csv [F] — **verified correct** (unlike the dubai/tundra cells; 12 SM6375 devices in the corpus, incl. rhodep = Moto G82 5G per the LineageOS wiki, fetched 2026-11-20) |
| census scope | 353 rows in 9 families (other 69, wifi 99, modem 47, adsp 44, tz 50, bt 14, cdsp 12, gpu 10, boot 8); 754,141,054 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 8 rows [F]

| file | bytes | md5 (upstream DB) | db_type | stage role [I] |
|---|---:|---|---|---|
| xbl.img | 5,242,880 | `43d61be3bd15242a24f93bd762ac60d5` | UEFIBOOT | XBL — primary bootloader (UEFI-based) |
| xbl_config.img | 262,144 | `006fd14dc8e6d9d0f774404149bac07b` | ELF64 | XBL config fragment |
| abl.img | 1,048,576 | `a44e86ccae47c71a224a4050ee42fd65` | UEFIBOOT | ABL — Android bootloader (AOSP, fastboot) |
| rpm.img | 524,288 | `2564c92ca6129f5b943c95530e7bf19a` | ELF64 | RPM — Resource Power Manager firmware (PMIC power sequencing) |
| qupfw.img | 81,920 | `65efa92e10702fa44d360d9c113bc641` | ELF64 | QUP serial-engine firmware (I2C/SPI/UART) |
| boot.img | 100,663,296 | `e841f8a270d38515cc36a93a4cc71b1b` | BOOT | AOSP boot image (kernel + ramdisk) |
| dtbo.img | 25,165,824 | `b0d7c12eb870ce949f808f1147b27242` | DTB | AOSP device-tree overlay image |
| vbmeta.img | 8,192 | `59740e467fe167cff52e4998f47ebbc6` | AVB | AVB metadata |

All 8 match the repo's bootchain grammar (`research/soc/per-soc-method-plans.md:415`) [F]; stage roles [I] labeled, per the pattern in #934.

## Cross-corpus facts [F]

- All 8 md5s are **corpus-unique to Edge_30_Neo** — per-build signed images.
- **rpm.img is the distinguishing row vs dubai**: 24 corpus devices carry rpm.img, with generation-clustered sizes — miami's 524,288 B shared (size-wise) with the SM6375 Moto siblings (Moto_G34_5G, G82_5G, G84_5G, Moto_G_5G_2024, G Stylus 5G-2); the SD4xx/6xx-gen1 Moto fleet uses 520,192 B; Nord_CE2/CE3 + Realme 253,952 B; Mi_A3 221,184 B; Phone_1/Pro_1X 229,376 B. dubai (SM7325-AE) has **no rpm row** — RPM-class power management moved into a different subsystem on that generation, or its extract omits it ([OPEN] which).
- **No aop/cpucp/shrm rows** — the same three-image gap as Pixel_4A_5G (SM7250, 8 rows), while dubai (SM7325-AE) carries all three at larger boot-chain sizes. Whether this is an extract-scope difference or a genuine platform difference is [OPEN] from metadata alone.
- Sizes that are corpus constants: boot.img 96 MiB (53-device magnitude), dtbo 24 MiB (modal, 72/118), vbmeta 8,192 B (modal, 94/115), xbl 5,242,880 B (10-row magnitude).

## ISA proof and interface facts

- `isa_identified=ELF64` for xbl_config, qupfw, rpm [F]; xbl/abl db_type UEFIBOOT [F]. Deeper structure needs payloads — [OPEN].
- Interface [I, labeled]: XBL→ABL→Linux chain; AVB verifies boot/dtbo; rpm loads on the PMIC-side processor before Linux. Boot-chain images are partition-flashed, never filesystem files (the #922/#934 extract-scope mechanism).
- Evidence class: all 8 rows P3, metadata-only [F].

## Honest negatives

- Stage roles [I]; no public source enumerates miami's boot-chain contents. [OPEN]
- The rpm-vs-no-rpm and aop/cpucp/shrm-vs-none differences across Moto extracts are **extract-scope vs platform questions that metadata cannot settle**. [OPEN]

## What would upgrade this finding

1. miami factory flashfile partition list → per-stage [F] confirmation.
2. Payload fetch: parse the three ELF64 images; add an SM6375 row to `research/qualcomm/docs/bootchain-census.md`.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `miami Edge 30 Neo xbl rpm firmware` (GitHub code search, adineo-cmd/* excluded) → guides only. Nobody documents miami's boot chain.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public specs.
