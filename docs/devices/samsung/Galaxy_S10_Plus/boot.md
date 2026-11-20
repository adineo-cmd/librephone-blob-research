# samsung Galaxy_S10_Plus — `boot` family status (7 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1078](https://github.com/adineo-cmd/open-device/issues/1078)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 2126802), the sibling docs #1042/#1060, AOSP dt-table/boot-image public specs. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT in the S10-generation Samsung shape - dtb/dtbo pair included - with the family-shared unsparse placeholder.** 7 rows (6 distinct files; recovery.img dual-path), all P3. Six md5s corpus-unique to Galaxy_S10_Plus; `unsparse_super_empty.img` shared byte-identically across the 4 S10-family devices (#1060's finding, re-confirmed).

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S10+ (SM-G975F); codename `beyond2lte` | `device-inventory.csv` (`build_codename=beyond2lte`) [F] |
| SoC | Samsung **Exynos 9820**; Mali-G76 MP12 | public spec pages (2026-11-21) [F]; same SoC as Galaxy_S10 (#1060) [F] |
| census scope | 69 rows in 4 families (other 57, boot 7, modem 4, wifi 1); 382,817,647 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 7 rows [F]

| file | bytes | md5 (upstream DB) | db_type | db_path | md5 status |
|---|---:|---|---|---|---|
| boot.img | 57,671,680 (55 MiB) | `3a8c81a52c7220afd4988054bf6b72f7` | BOOT | radio | corpus-unique [F] |
| recovery.img | 67,633,152 (64 MiB) | `91911d205f4414f77dfae8b64b06ebd8` | BOOT | radio **and** vendor/etc | corpus-unique [F] |
| unsparse_super_empty.img | 4,644 | `44bcc388cadd12ca0268107c8619a187` | BOOT | radio | **family-shared** - identical on Galaxy_S10, S10_5G, S10e [F] |
| dtb.img | 8,388,608 | `87216dd3fcd983b558537551293293c3` | DTB | radio | corpus-unique [F] |
| dtbo.img | 8,388,608 | `72b460c228dde6acb0820b9cc962f57e` | DTB | radio | corpus-unique [F] |
| vbmeta.img | 8,192 | `9212cd5c5b340b1c114ed95694beae1e` | AVB | radio | corpus-unique [F] |

Distinct bytes: 57,671,680 + 67,633,152 + 4,644 + 8,388,608 + 8,388,608 + 8,192 = 142,094,884 [F] - identical to Note_10_5G's and Galaxy_S10's distinct totals (same 6-file grammar). No Qualcomm bootchain grammar - Exynos device [F].

## Cross-device facts [F]

1. **dtb/dtbo pair**: the S10/Note10-generation marker (#1042) - beyond2lte is one of the 7 samsung devices carrying `dtb.img`.
2. **family-shared unsparse**: `unsparse_super_empty.img` md5 `44bcc388...` spans Galaxy_S10, S10_5G, S10e, S10_Plus - the placeholder is family-level, not per-build (#1060's finding, re-confirmed on the 4th member).
3. The three beyond1lte/beyondx/beyond2lte slices share the identical 7-row grammar and 96-MiB-class size profile; only md5s differ (per-build boot/vbmeta) - consistent with one firmware generation across the S10 family.

## ISA proof and interface facts

- Boot-image/dt-table internals unprovable from metadata - [OPEN]; AArch64 SoC [F].
- Interface [I, labeled]: AVB verifies boot/dtbo (+dtb per generation); Odin/download-mode flashing. Not device-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- The dtb-vs-dtbo consumption split stays [OPEN] (#1042).
- Whether S10e (beyond0) also shares the unsparse md5 was verified here indirectly via the md5 query (yes - S10e is in the 4-device set). [F]

## What would upgrade this finding

1. Payload fetch: parse dtb.img/dtbo.img tables per the mkdtimg format.
2. The family-shared map (per-build vs family-level rows) from #1060 now covers all 4 S10-family members - a one-table lead-level summary would close the S10 generation.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S10 Plus beyond2lte boot firmware analysis` (web + GitHub code search, adineo-cmd/* excluded) -> guides only. Nobody documents the S10_Plus boot rows.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
