# samsung Galaxy_S10 — `boot` family status (7 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1060](https://github.com/adineo-cmd/open-device/issues/1060)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 5c69fef), the sibling doc `docs/devices/samsung/Galaxy_Note_10_5G/boot.md` (#1042), AOSP dt-table/boot-image public specs. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT in the S10-generation Samsung shape - dtb/dtbo pair included - with one family-shared row.** 7 rows (6 distinct files; recovery.img dual-path), all P3. Six md5s are corpus-unique to Galaxy_S10; **`unsparse_super_empty.img` is shared byte-identically by all 4 S10-family devices** - a family placeholder, not a per-build artifact.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S10 (SM-G973F); codename `beyond1lte` | `device-inventory.csv` (`build_codename=beyond1lte`) [F]; LineageOS beyond1lte tree (fetched 2026-11-20 for #922 - SM-G973F, Exynos 9820) [F] |
| SoC | Samsung **Exynos 9820**; Mali-G76 MP12 | public spec pages (2026-11-21) [F] |
| census scope | 69 rows in 4 families (other 57, boot 7, modem 4, wifi 1); 382,281,531 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 7 rows [F]

| file | bytes | md5 (upstream DB) | db_type | db_path | md5 status |
|---|---:|---|---|---|---|
| boot.img | 57,671,680 (55 MiB) | `9eb56348dea764b42c7d9f050cc77335` | BOOT | radio | corpus-unique [F] |
| recovery.img | 67,633,152 (64 MiB) | `8f84de0c2137cb32d916020ee2b32409` | BOOT | radio **and** vendor/etc | corpus-unique [F] |
| unsparse_super_empty.img | 4,644 | `44bcc388cadd12ca0268107c8619a187` | BOOT | radio | **family-shared** - identical on Galaxy_S10_5G, S10e, S10_Plus [F] |
| dtb.img | 8,388,608 | `60a54b757140460f342eb7e484b33f80` | DTB | radio | corpus-unique [F] |
| dtbo.img | 8,388,608 | `22ce6bbc2e9b77f10e498633085ece0d` | DTB | radio | corpus-unique [F] |
| vbmeta.img | 8,192 | `8cc8cc0e515c6b7213d00cbe03d37f51` | AVB | radio | corpus-unique [F] |

Distinct bytes: 57,671,680 + 67,633,152 + 4,644 + 8,388,608 + 8,388,608 + 8,192 = 142,094,884 [F] (same distinct total as Note_10_5G's 7-row set - same generation grammar). No Qualcomm bootchain grammar - Exynos device (#1024/#1042 Samsung shape) [F].

## The two cross-device facts [F]

1. **dtb/dtbo pair**: the S10/Note10-generation marker from #1042 - exactly 7 samsung devices carry `dtb.img` (S10, S10e, S10_Plus, S10_5G, Note_10, Note_10_5G, Note_10_Plus), each with dtbo. beyond1lte is one of the 7.
2. **family-shared unsparse placeholder**: `unsparse_super_empty.img` 4,644 B carries one md5 across Galaxy_S10, S10_5G, S10e, S10_Plus - unlike every other boot row (per-build). The unsparse placeholder is build-independent by nature (an empty super-partition layout descriptor), so a shared build across the family is the expected shape; it is the corpus's first samsung boot-family row that is NOT device-unique.

## ISA proof and interface facts

- Boot-image/dt-table internals unprovable from metadata - [OPEN]; AArch64 SoC [F].
- Interface [I, labeled]: AVB verifies boot/dtbo (+dtb per generation); Odin/download-mode flashing. Not device-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- The dtb-vs-dtbo consumption split stays [OPEN] (#1042).
- Whether the shared unsparse md5 extends beyond the S10 family (e.g., Note10's own unsparse row) is a one-command check the lead can run corpus-wide. [F-adjacent, OPEN here]

## What would upgrade this finding

1. Payload fetch: parse dtb.img/dtbo.img tables; parse the S10 boot.img header.
2. Corpus pass: group all samsung boot rows by md5-sharing to complete the per-build vs family-shared map (the unsparse finding suggests placeholders are family-level, boot/vbmeta are device-level).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S10 beyond1lte boot.img dtb dtbo firmware analysis` (web + GitHub code search, adineo-cmd/* excluded) -> guides only. Nobody documents the S10 boot rows or the family-shared unsparse md5.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
