# samsung Galaxy_A21S — `tz` family status (0 rows — honest negative)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1012](https://github.com/adineo-cmd/open-device/issues/1012)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site d9b457c), the method doc `docs/devices/samsung/Galaxy_F62/tz.md` (#1030), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the lab's `tz` family (Qualcomm TEE grammar) is structurally ABSENT on Galaxy_A21S — not a census gap.** Zero of the device's 82 census rows match the tz grammar, and the device is an Exynos 850: Samsung Exynos hardware carries no Qualcomm PIL TEE image set at all. Its TrustZone stack is Samsung's own chain (TEEGRIS-class), carried outside this DB's blob census scope — the same three-carrier structure proven for Galaxy_F62 in #1030.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy A21s; codename `a21s` | `device-inventory.csv` [F] |
| SoC | Samsung **Exynos 850** | public spec pages (2026-11-21) [F]; inventory SoC cell empty, supplied in #1006 [F] |
| census scope | 82 rows in 3 families (boot 12, other 68, modem 2) | coverage-matrix.csv [F] |

## Census evidence [F]

```
awk -F, '$1=="Galaxy_A21S" && ($5 ~ /^(tz|keymaster|qsee|cmnlib|hyp|devcfg|uefisecapp|featenabler|hdcp|widevine|soter|smplap)/
      || $6 ~ /^(tz|keymaster|qsee|cmnlib|hyp|devcfg|uefisecapp|featenabler|hdcp|widevine|soter|smplap)/)' coverage-matrix.csv | wc -l
0
```

- 0 of 82 rows match the tz grammar (`tz/keymaster/qsee/cmnlib/hyp/devcfg/uefisecapp/featenabler/hdcp/widevine/soter/smplap`, per `research/soc/per-soc-method-plans.md`) [F].
- The 68 `other` rows are vendor peripherals: Exynos audio DSP (abox_tplg, calliope_*, AP*_AUDIO_SLSI), camera (setfile_*, is_lib/is_rta), NFC (sec_s3nrn4v_*), MFC video codec, PLMN tables — no TEE names [F]. A substring fallback (`tee|tz|sehos|tbase|mc`) adds no candidates beyond the camera `fimc`-class false positives excluded in #1030.
- The all-samsung tz-grammar check (re-verified for #1030): **0 of 914 samsung rows**; the matrix's 4,264 tz rows all sit on non-samsung vendors [F].

## Why structural, not a census gap [F]

1. **Grammar, not scarcity**: the tz family encodes Qualcomm's PIL TEE image set (tz.img/keymaster.img/devcfg.img/hyp.img/uefisecapp.img and the TZ-app splits). Samsung Exynos devices — every samsung device in this DB — never ship those filenames; their TEE is Samsung's TEEGRIS stack, reached through a different chain entirely (#1030's three carriers: TEEGRIS kernel + `startup.tzar` in the boot partition, loadable TAs in `/vendor/tee` + `/system/tee`, encrypted EL3 monitor inside S-Boot).
2. **Package-level completeness**: for Galaxy_F62 (#1030) the census matched the public LineageOS package file list exactly. A21S's census profile (boot images + vendor peripheral firmware + BL-type files under `other`) is the same Samsung shape; no public Samsung Exynos package ships Qualcomm TEE images.
3. **The DB's samsung slice has no SoC mix that could carry the grammar**: every samsung device in the corpus is Exynos-class in its census scope (the Snapdragon-sourced Samsung models are not in this DB's samsung rows with radio extracts).

## Honest negatives

- **Where A21S's TEE actually lives is inferred from the Samsung Exynos architecture (#1030's TEEGRIS findings), not verified on A21S payloads** — no public extract list of A21S includes TEE files, and the boot.img/vendor decomposition is payload-gated. [OPEN]
- The `/vendor/tee` + `/system/tee` TA sets on A21S are uncatalogued by the upstream DB (scope limitation, not absence). [OPEN]
- A21S launched on Android 10; its TEE generation (TEEGRIS vs Kinibi transition era) is [OPEN] — the S10-generation TEEGRIS switch postdates it, and public documentation of A21S's exact TEE is absent.

## What would upgrade this finding

1. Payload fetch (A21S stock firmware): walk the boot partition and `/vendor/tee` for the TEEGRIS kernel + UUID TAs — the same three-step upgrade path recorded in #1030.
2. A21S BL-package file list (public mirror metadata) to confirm the 8-file grammar (#1030's F62 pattern) holds for Exynos 850 builds.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy A21S TEE trustzone Exynos 850` (web + GitHub code search, adineo-cmd/* excluded) → marketing/spec pages only; the Samsung Exynos TEE method is #1030's, cited throughout.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo method and public specs.
