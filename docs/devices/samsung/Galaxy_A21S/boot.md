# samsung Galaxy_A21S — `boot` family status (12 rows = 6 distinct, duplicated)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1006](https://github.com/adineo-cmd/open-device/issues/1006)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 06f608b), `upstream-contribution/blob-database/recon.md` (upstream DB row-duplication pathology), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT as the standard Android verified-boot set — and the census doubles it.** The 12 rows are exactly **6 distinct rows duplicated twice** (identical filename, size, md5 and db_path): boot.img, recovery.img (radio + a vendor/etc copy), unsparse_super_empty.img, dtbo.img, vbmeta.img. The doubling is an upstream DB join artifact (the same pathology `recon.md` documents for count.csv), not device data. No Qualcomm bootchain-grammar files exist — correct for an Exynos device.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy A21s; codename `a21s` | `device-inventory.csv` (`build_codename=a21s`) [F] |
| SoC | Samsung **Exynos 850** | public spec pages (GSMArena et al., 2026-11-21) [F]. **The upstream inventory's SoC cell is empty** — supplied here [F] |
| census scope | 82 rows in 3 families (other 68, boot 12, modem 2); 395,669,880 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 12 rows (= 6 distinct) [F]

```
awk -F, '$1=="Galaxy_A21S" && $4=="boot"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv | sort | uniq -c
      2 boot.img|37748736|4610bca9db0d9148044d3fa4cb829f9a|samsung/a21s/radio|BOOT
      2 dtbo.img|8388608|e1ee81b9c834a6ff7ab17beaba2599e6|samsung/a21s/radio|DTB
      2 recovery.img|55574528|54b5160ae5c0f535d555a08d446b72ec|samsung/a21s/radio|BOOT
      2 recovery.img|55574528|54b5160ae5c0f535d555a08d446b72ec|samsung/a21s/vendor/etc|BOOT
      2 unsparse_super_empty.img|4644|a46e373db58b5a607ed7ef0b92483337|samsung/a21s/radio|BOOT
      2 vbmeta.img|4096|9c0c34f051a181486b762753c021fa12|samsung/a21s/radio|AVB
```

| distinct file | bytes | md5 (upstream DB) | db_type | role [I] |
|---|---:|---|---|---|
| boot.img | 37,748,736 (36 MiB) | `4610bca9db0d9148044d3fa4cb829f9a` | BOOT | AOSP boot image |
| recovery.img | 55,574,528 (53 MiB) | `54b5160ae5c0f535d555a08d446b72ec` | BOOT | AOSP recovery image (radio copy + vendor/etc copy, same md5) |
| unsparse_super_empty.img | 4,644 | `a46e373db58b5a607ed7ef0b92483337` | BOOT | dynamic-partition placeholder |
| dtbo.img | 8,388,608 (8 MiB) | `e1ee81b9c834a6ff7ab17beaba2599e6` | DTB | device-tree overlay image |
| vbmeta.img | 4,096 | `9c0c34f051a181486b762753c021fa12` | AVB | AVB metadata (the corpus's small 4,096-B class) |

## The duplication finding [F]

Every one of the 6 distinct rows appears **exactly twice** with identical `db_path`, `md5` and size — a pure upstream join artifact. Contrast: the same radio+vendor/etc dual-path pattern on Galaxy_A71/F62/Note10_5G carries **single** rows. `recon.md` already documents the upstream DB's duplication pathology in `count.csv`; this extends it to A21S's devices-table rows. The honest census for A21S boot is **6 rows / 101,424,608 distinct bytes**, not 12.

## Why no Qualcomm bootchain grammar [F]

Zero `xbl/abl/aop/cpucp/qupfw/shrm` rows — correct for an Exynos 850 device: Samsung's Exynos boot chain (S-Boot et al.) ships in the BL-package files, which for Samsung devices live in the `firmware` census dirs (the #1030 Galaxy_F62 analysis covers that layer; A21S's own BL rows fall under its `other` family). The Android images here are the same AOSP triple as every device.

## ISA proof and interface facts

- Boot-image internals (header version, kernel ISA) are not provable from metadata — [OPEN]; the Exynos 850 is an AArch64 part (public specs).
- Interface [I, labeled]: AVB verifies boot/dtbo/recovery; fastboot/download-mode flashing. Samsung-specific flashing flows (Odin/Loki) are public knowledge, not device-verified here.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- The duplication's upstream cause (which join produced it) is not determinable from the matrix alone. [OPEN]
- recovery.img appears at two paths with one md5 — a census convenience (same file packaged twice), not two files. [F]

## What would upgrade this finding

1. Lead-level: de-duplicate the A21S rows in the upstream DB stream (or annotate the join artifact) — the corpus-wide duplication audit should extend beyond count.csv.
2. Payload fetch: parse boot.img/recovery.img headers per the AOSP boot-image format.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy A21S boot.img dtbo vbmeta analysis` (web + GitHub code search, adineo-cmd/* excluded) → guides only. Nobody documents the A21S boot rows or the duplication artifact.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public specs.
