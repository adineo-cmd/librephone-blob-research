# samsung Galaxy_Note_10_5G — `boot` family status (7 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1042](https://github.com/adineo-cmd/open-device/issues/1042)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 9eee6ba), the sibling doc `docs/devices/samsung/Galaxy_F62/boot.md` (#1024), AOSP dt-table/boot-image public specs. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT in the Samsung shape, with a generational marker: a `dtb.img` + `dtbo.img` pair.** 7 rows (6 distinct files; recovery.img at two census paths, one md5), all corpus-unique, all P3. The dtb/dtbo pair appears on exactly 7 samsung devices - the S10/Note10 Exynos generation - and nowhere else in the corpus.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Note 10 5G (SM-N971N); codename `d1x` | `device-inventory.csv` (`build_codename=d1x`) [F] |
| SoC | Samsung **Exynos 9825** | #1030 identity table (same SoC as Note 10/F62) [F]; public spec pages (2026-11-21) [F] |
| census scope | 69 rows in 3 families (other 58, boot 7, modem 4); 335,370,158 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 7 rows [F]

| file | bytes | md5 (upstream DB) | db_type | db_path | role [I] |
|---|---:|---|---|---|---|
| boot.img | 57,671,680 (55 MiB) | `5ec8cfd51faf3a090af81eca3e370450` | BOOT | radio | AOSP boot image |
| recovery.img | 67,633,152 (64 MiB) | `c1118714fe122a352913c2ec22d2f028` | BOOT | radio **and** vendor/etc | AOSP recovery image - one file, two census paths |
| unsparse_super_empty.img | 4,644 | `10d5562dda0364a497d9811d9fdf2c08` | BOOT | radio | dynamic-partition placeholder |
| **dtb.img** | 8,388,608 | `f7c56be4c11276d488ceb08a6e8eab40` | DTB | radio | base device-tree blob image |
| dtbo.img | 8,388,608 | `1ec7efe5daf6439a707f5e59be43a2ba` | DTB | radio | device-tree overlay image |
| vbmeta.img | 8,192 | `a92c142f9dbf9a516609426d51ba385c` | AVB | radio | AVB metadata |

Distinct bytes: 57,671,680 + 67,633,152 + 4,644 + 8,388,608 + 8,388,608 + 8,192 = 142,094,884 [F]. All 6 distinct md5s **corpus-unique to Galaxy_Note_10_5G** [F]. No Qualcomm bootchain grammar - Exynos device, BL chain in the firmware-dir files (the #1030/#1024 Samsung shape) [F].

## The dtb/dtbo generational marker [F]

```
awk -F, '$6=="dtb.img"{print $1}' coverage-matrix.csv | sort -u
```
-> exactly **7 samsung devices** carry `dtb.img`: Galaxy_S10, S10e, S10_Plus, S10_5G, Note_10, Note_10_5G, Note_10_Plus - the complete Exynos 9820/9825 flagship generation - and **each also carries dtbo.img** (verified: 7/7 dtbo rows). No other samsung device in the corpus has dtb.img. The pair marks this hardware generation's boot layout (base DTB + overlay DTB flashed as separate partitions); which partition the bootloader actually consumes is [OPEN] from metadata.

## Cross-corpus facts [F]

- boot.img 57,671,680 B is the Samsung 5G-generation magnitude (Note_10/Note_10_Plus/S10 family share the size class; the 53-device 96-MiB magnitude is the Qualcomm-radio one).
- recovery.img dual-path (radio + vendor/etc, one md5) - the Samsung census convention (#1024).
- vbmeta 8,192 B = the corpus modal class (94/115 rows).

## ISA proof and interface facts

- Boot-image/dt-table internals are not provable from metadata - [OPEN]; AArch64 SoC [F].
- Interface [I, labeled]: AVB verifies boot/dtbo (and per the generation's layout, likely dtb); Odin/download-mode flashing. Not device-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- The dtb.img vs dtbo.img consumption split (base DTB at boot vs overlays selected per hardware variant) is [I] from public Android dt-table practice - payload-verify to upgrade.
- GKI status [OPEN] (Android 10 launch device, pre-GKI era).

## What would upgrade this finding

1. Payload fetch: parse dtb.img/dtbo.img dt-tables (mkdtimg format) - 14-entry-class tables per the FP6 census precedent.
2. Lead-level: the dtb/dtbo pair could join the family-classification grammar as an S10/Note10-generation marker.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy Note 10 5G dtb.img dtbo firmware analysis` (web + GitHub code search, adineo-cmd/* excluded) -> guides only. Nobody documents the Note_10_5G boot rows or the dtb/dtbo pair.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
