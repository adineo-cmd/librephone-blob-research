# samsung Galaxy_Note_10_5G — `tz` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1048](https://github.com/adineo-cmd/open-device/issues/1048)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 208f3ce), the method docs `docs/devices/samsung/Galaxy_F62/tz.md` (#1030) and `docs/devices/samsung/Galaxy_A21S/tz.md` (#1012), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `tz` family (Qualcomm TEE grammar) is structurally ABSENT on Galaxy_Note_10_5G - not a census gap.** The device is an Exynos 9825 flagship: 0 of its 69 census rows match the tz grammar, 0 TEE-name substrings appear anywhere in its 58 `other` rows, and the all-samsung check holds (0 of 914 samsung rows). Its TEE is the Samsung chain mapped in #1030 - TEEGRIS-class carriers outside this DB's blob census scope.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Note 10 5G (SM-N971N); codename `d1x` | `device-inventory.csv` [F] |
| SoC | Samsung **Exynos 9825** (Mali-G76 MP12) | #1030 identity table (F62 shares the SoC) [F]; public spec pages (2026-11-21) [F] |
| census scope | 69 rows in 3 families (boot 7, other 58, modem 4) | coverage-matrix.csv [F] |

## Census evidence [F]

- 0 of 69 rows match the tz grammar (`tz/keymaster/qsee/cmnlib/hyp/devcfg/uefisecapp/featenabler/hdcp/widevine/soter/smplap`) [F].
- TEE-name substring scan (`tee|sehos|tbase|trustonic`) over all 58 `other` rows: **0 hits** [F]. The other-family profile is Exynos vendor peripherals - SLSI audio (AP*_AUDIO_SLSI, CP_AUDIO_SLSI), the calliope audio DSP family, camera setfiles + fimc_is, txse1/2/3 apps, PLMN tables, NFC (sec_s3nrn4v_* per the F62-class shape) [F].
- All-samsung tz-grammar check: **0 of 914 samsung rows**; the corpus's 4,264 tz rows sit entirely on 9 non-samsung vendors [F].

## Why structural, not a census gap [F]

The #1030/#1012 reasoning applies unchanged to this device:
1. The tz family encodes Qualcomm's PIL TEE image set; Samsung Exynos hardware never ships those filenames.
2. Note_10_5G's TEE is the Samsung chain: TEEGRIS-class kernel + `startup.tzar` in the boot partition, loadable TAs in `/vendor/tee` + `/system/tee`, encrypted EL3 monitor inside S-Boot (sboot.bin 4,194,304 B is in this device's BL census rows) - all outside this DB's blob census scope.
3. The census is complete relative to its package shape: the BL file set (cm.bin, dqmdbg.img, keystorage.bin, modem.bin, modem_debug.bin, sboot.bin, uh.bin, up_param.bin - the d1-generation grammar per the #1030 LineageOS-table method) plus vendor peripherals and the Android boot images (#1042).

## Honest negatives

- **A21S's TEE-generation caveat applies here too**: Note_10_5G is S10-generation (2019) - TEEGRIS per the Quarkslab/Keysight timeline cited in #1030, but the payload-level confirmation on this specific device is [OPEN].
- `/vendor/tee` + `/system/tee` TA sets are uncatalogued by the upstream DB (scope limitation, not absence). [OPEN]
- Note_10_5G shares its firmware grammar with Note_10/Wifi (the d1/d1x family); a combined d1-family TEE census would be the natural payload pass. [OPEN]

## What would upgrade this finding

1. Payload fetch (Note_10_5G stock firmware or the LineageOS d1x package): walk the boot partition and `/vendor/tee` for the TEEGRIS kernel + UUID TAs - the #1030 three-step path.
2. Lead-level: the d1/d1x/dm1 (Note 10 family) devices share one firmware grammar - a family-level TEE doc would cover three issues' worth of devices at once.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy Note 10 5G TEE trustzone Exynos 9825` (web + GitHub code search, adineo-cmd/* excluded) -> marketing/spec pages only; the Samsung Exynos TEE method is #1030's, cited throughout.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus the cited in-repo method and public specs.
