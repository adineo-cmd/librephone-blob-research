# fairphone FP4 — `tz` family status (61 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#976](https://github.com/adineo-cmd/open-device/issues/976)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 8f9a8ed), the sibling decomposition docs (#940/#958), the in-repo QSEE toolset. Evidence classes: [F] fact / [I] inference (labeled). No payloads fetched.

**Verdict: the tz family is PRESENT and structurally rich for an SM7225 device** — 61 rows, 8,079,433 B: 7 radio images + 6 nine-row PIL splits. Three firsts in this device's slice: **featenabler ships in both single-file (.img) and 9-row split form**; **multiimgoem.img** (an FP/OnePlus-family radio image) sits in the tz census; **smplap32 + smplap64** (the grammar's namesake pair) both present. All 7 radio-image md5s corpus-unique; the SM7225-generation images are 25-75% smaller than the Moto SM7325+ builds.

## Device identity

| fact | value | source |
|---|---|---|
| model | Fairphone 4; codename `FP4` | `device-inventory.csv` [F] |
| SoC | Qualcomm SM7225 Snapdragon 750G | device-inventory.csv [F]; mainline `sm7225-fairphone-fp4.dts` verified for #970 |
| census scope | 286 rows in 9 families; tz = 61 rows, 8,079,433 B | coverage-matrix.csv [F] |

## Decomposition [F]

| rows | component | bytes (total) | db_path | db_type | role [I, name-derived] |
|---|---|---:|---|---|---|
| 1 | tz.img | 3,031,040 | radio | BOOT | QTEE OS |
| 1 | hyp.img | 409,600 | radio | SECUREBOOT | Type-1 hypervisor image |
| 1 | keymaster.img | 266,240 | radio | SECURITY | Keymaster/KeyMint TA carrier |
| 1 | uefisecapp.img | 126,976 | radio | UNKNOWN | UEFI secure application |
| 1 | devcfg.img | 45,056 | radio | UNKNOWN | device configuration for secure boot |
| 1 | featenabler.img | 90,112 | radio | UNKNOWN | feature-enabler TZ app — single-file form |
| 1 | multiimgoem.img | 16,384 | radio | UNKNOWN | multi-image OEM radio app (FP/OnePlus-family file) |
| 9 | featenabler | split set | modem/image | — | feature-enabler TZ app — split form |
| 9 | loadalgota64 | split set | modem/image | — | 64-bit OTA image loader TZ app |
| 9 | smplap32 | split set | modem/image | — | SMPLAP 32-bit app (secure memory protect layer) |
| 9 | smplap64 | split set | modem/image | — | SMPLAP 64-bit app |
| 9 | soter64 | split set | modem/image | — | Soter attestation-class TZ app |
| 9 | widevine | split set | modem/image | — | Widevine DRM TZ app |

Structure law [F]: 6 × 9 = 54 split rows + 7 radio images = 61. Sum check [F]: 8,079,433 B.

## Per-image facts [F]

| image | bytes | md5 (upstream DB) |
|---|---:|---|
| tz.img | 3,031,040 | `7c27a38419e0c442192a96a6c0bc32b3` |
| hyp.img | 409,600 | `6eabfce1fb5a6a28cd07cafd4913e5f5` |
| keymaster.img | 266,240 | `9337fb687bc5d689f417f3e27c8ccf4f` |
| uefisecapp.img | 126,976 | `be649e1a24c886e9839fe755cbaef3c1` |
| devcfg.img | 45,056 | `a85234031f5bd3f13effe070fe81ec54` |
| featenabler.img | 90,112 | `45aa306bc32fc404135d131bb1518285` |
| multiimgoem.img | 16,384 | `04310459c65113424f4ebf907059f8f3` |

- All 7 md5s **corpus-unique to FP4** [F].
- Generation scale: tz.img 3,031,040 B (SM7225) vs 4,194,304 (Moto SM7325-AE/SM6375 Moto builds) and 3,473,408 (non-Moto SM6375) — QTEE builds scale per SoC and vendor [F]; **hyp.img 409,600 B vs dubai's 8,388,608 B** — a 20x vendor/SoC difference in the hypervisor image, the corpus's widest hyp spread [F].
- `featenabler` dual-form: the single-file `featenabler.img` (90,112 B) and the 9-row split coexist in the census — the vendor ships both forms; which one the platform loads is [OPEN] from metadata.
- `multiimgoem.img` appears on 13 corpus devices (FP4/FP5/FP6, OnePlus 7T/8/9 family, Phone 1/2, Pro 1X) — an FP/OnePlus-family radio image inside the tz census [F].
- `smplap32`/`smplap64` rows span 43 corpus devices — the grammar's namesake pair is a fleet-wide TZ app [F].

## Comparison with the sibling decompositions (#940/#958) [F]

| aspect | dubai (SM7325-AE) | miami (SM6375) | FP4 (SM7225) |
|---|---|---|---|
| tz rows / bytes | 77 / 16,213,083 | 50 / 16,039,093 | 61 / 8,079,433 |
| radio images | 5 | 5 | **7** (+featenabler.img, multiimgoem.img) |
| split apps | 8 | 5 | 6 (+widevine, smplap pair) |
| hyp.img | 8,388,608 | 8,388,608 | **409,600** |
| tz.img | 4,194,304 | 4,194,304 | 3,031,040 |

The radio image *set* grows with vendor (Fairphone carries two extras), image *sizes* shrink with SoC generation, and the split-app mix is vendor-configured. All three decompositions agree on the grammar.

## ISA proof and interface facts

- `isa_identified` is empty for all 61 FP4 tz rows — honestly un-RE'd per the upstream convention [F]; the ELF64 split shape is family-established, not payload-proven. [OPEN]
- Interface [I, labeled]: QTEE chain as in #940; widevine serves the DRM path; smplap = secure memory protect layer. None FP4-verified.

## Honest negatives

- No payload-level facts (segment maps, metadata versions) — [OPEN], method ready in-repo.
- The featenabler dual-form loading question and the hyp 20x size question are [OPEN] from metadata.
- multiimgoem.img's internal structure (16,384 B) is undecoded; it sits in the tz census by upstream classification. [OPEN]

## What would upgrade this finding

1. Payload fetch (P2 device — highest priority): QSEE census on tz.img + the 6 split sets → first SM7225 TZ segment map; resolve the featenabler dual-form question by content.
2. Corpus pass: smplap32/64 and multiimgoem.img build-identity clusters across their 43/13-device spreads.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `FP4 tz.img keymaster hyp smplap` (GitHub code search, adineo-cmd/* excluded) → guides only; no FP4 TEE artifact in-repo or public.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo method.
