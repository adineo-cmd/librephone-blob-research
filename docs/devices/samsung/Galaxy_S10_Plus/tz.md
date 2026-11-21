# samsung Galaxy_S10_Plus — `tz` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1084](https://github.com/adineo-cmd/open-device/issues/1084)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site f80f251), the method docs #1030/#1066 (same-SoC sibling), the LineageOS `beyond1lte`-class package list (fetched 2026-11-20 for #922). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `tz` family (Qualcomm TEE grammar) is structurally ABSENT on Galaxy_S10_Plus - not a census gap.** Exynos 9820 device: 0 of 69 census rows match the tz grammar, 0 TEE-name substrings in the `other` rows, and the census's BL file set matches the S10-generation package grammar exactly. TEE is the Samsung chain per #1030.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S10+ (SM-G975F); codename `beyond2lte` | `device-inventory.csv` [F] |
| SoC | Samsung **Exynos 9820** (Mali-G76 MP12) | public spec pages (2026-11-21) [F]; same SoC as Galaxy_S10 (#1066) [F] |
| census scope | 69 rows in 4 families (boot 7, other 57, modem 4, wifi 1) | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 of 69 rows match the tz grammar (`tz/keymaster/qsee/cmnlib/hyp/devcfg/uefisecapp/featenabler/hdcp/widevine/soter/smplap`) [F].
- TEE-substring scan (`tee|sehos|tbase|trustonic`) over the 57 `other` rows: **0 hits** [F].
- The `other` profile is the S10 BL grammar plus vendor peripherals: cm.bin (7,340,032 B), dqmdbg.img, keystorage.bin, param.bin, sboot.bin (4,194,304 B), uh.bin, up_param.bin - the S10-generation package grammar (9 files per model incl. param.bin, per the beyond1lte-class LineageOS lists fetched 2026-11-20) - plus vendor audio/camera/NFC peripherals [F]. Census complete against its public package source.
- All-samsung tz-grammar check: **0 of 914 samsung rows** [F].

## Why structural, not a census gap [F]

The #1030/#1012/#1048/#1066 reasoning applies unchanged: Samsung Exynos hardware never ships the Qualcomm PIL TEE grammar; the TEE is the Samsung chain (TEEGRIS-class kernel + `startup.tzar` in boot, `/vendor/tee` + `/system/tee` loadable TAs, encrypted EL3 monitor inside S-Boot) - all outside this DB's blob census scope. S10-generation (2019): TEEGRIS per the Quarkslab/Keysight timeline, payload-level confirmation [OPEN].

## Honest negatives

- `/vendor/tee` + `/system/tee` TA sets uncatalogued by the upstream DB (scope limitation, not absence). [OPEN]
- The S10-generation family (beyond0/beyond1lte/beyond2lte/beyondx + d1/d1x/d2s) shares one BL grammar - a family-level TEE doc would cover the whole generation at once (lead-level suggestion, also recorded on #1066). [OPEN]

## What would upgrade this finding

1. Payload fetch (S10+ stock firmware or LineageOS beyond2lte package): walk the boot partition and `/vendor/tee` - the #1030 three-step path.
2. Lead-level family TEE doc for the S10/Note10 generation (7 devices, one grammar).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S10 Plus TEE trustzone Exynos 9820` (web + GitHub code search, adineo-cmd/* excluded) -> marketing/spec pages only; the Samsung Exynos TEE method is #1030's, cited throughout.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus the cited in-repo method and public specs.
