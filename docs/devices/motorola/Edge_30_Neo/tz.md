# motorola Edge_30_Neo — `tz` family status (50 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#958](https://github.com/adineo-cmd/open-device/issues/958)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 9ea02f4), the sibling method doc `docs/devices/motorola/Edge_30/tz.md` (#940), the in-repo QSEE toolset. Evidence classes: [F] fact / [I] inference (labeled). No payloads fetched.

**Verdict: the tz family is PRESENT and structurally complete for an SM6375 device** — 50 rows, 16,039,093 B: 5 boot-chain TEE images at radio + 5 nine-row PIL-split TZ apps on the modem path. All 5 radio-image md5s corpus-unique. The app set differs from dubai's (same vendor, adjacent SoC): miami carries **soter64** and lacks hdcp1/hdcp2p2/sp_license/winsecap.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 30 Neo; codename `miami` | `device-inventory.csv` [F]; corpus paths `motorola/miami/` [F] |
| SoC | Qualcomm SM6375 Snapdragon 695 | device-inventory.csv [F] — verified correct (12 SM6375 devices in the corpus) |
| census scope | 353 rows in 9 families; tz = 50 rows, 16,039,093 B | coverage-matrix.csv [F] |

## Decomposition [F]

| rows | component | bytes (total) | db_path | db_type | role [I, name-derived] |
|---|---|---:|---|---|---|
| 1 | tz.img | 4,194,304 | radio | BOOT | QTEE OS |
| 1 | hyp.img | 8,388,608 | radio | SECUREBOOT | Type-1 hypervisor image |
| 1 | keymaster.img | 524,288 | radio | SECURITY | Keymaster/KeyMint TA carrier |
| 1 | uefisecapp.img | 2,097,152 | radio | UNKNOWN | UEFI secure application |
| 1 | devcfg.img | 131,072 | radio | UNKNOWN | device configuration for secure boot |
| 9 | dxhdcp2 | split set | modem/image | — | Display Rx HDCP 2.x TZ app |
| 9 | featenabler | split set | modem/image | — | feature-enabler TZ app |
| 9 | hdcpsrm | split set | modem/image | — | HDCP SRM handler |
| 9 | loadalgota64 | split set | modem/image | — | 64-bit OTA image loader TZ app |
| 9 | soter64 | split set | modem/image | — | Soter — attestation/key-provisioning-class TZ app |

Structure law [F]: 5 × 9 = 45 split rows + 5 radio images = 50. Sum check [F]: 16,039,093 B.

## Per-image facts [F]

| image | bytes | md5 (upstream DB) |
|---|---:|---|
| tz.img | 4,194,304 | `13a1af1952382365af6e082b6ba2e228` |
| hyp.img | 8,388,608 | `a7f2c15a9a6321d76870acaffe562b7d` |
| keymaster.img | 524,288 | `fed33dd1e4da94171197b23d521c2422` |
| uefisecapp.img | 2,097,152 | `e90e4c5031f3ee74444cb38952b37f48` |
| devcfg.img | 131,072 | `1512cb319065b0afb775440b2d4a153c` |

- All five md5s **corpus-unique to Edge_30_Neo** [F].
- tz.img 4,194,304 B matches the Moto-generation magnitude — same-size tz.img on Moto_G34_5G/G82_5G/G84_5G; the non-Moto SM6375 devices (Nord_CE2/CE3, Realme_9_Pro/10_Pro) carry **3,473,408 B** tz.img — same SoC, different vendor build/extract sizes [F].
- `soter64` rows span **46 corpus devices across all vendors** (Moto, OnePlus, Nothing, Fairphone, Sony, Xiaomi/Redmi/Poco, Pad) — a cross-vendor Qualcomm TZ app, not a Xiaomi-specific one despite the name's association [F].

## Comparison with the sibling decomposition (dubai, #940) [F]

| aspect | Edge_30 (dubai, SM7325-AE) | Edge_30_Neo (miami, SM6375) |
|---|---|---|
| tz rows / bytes | 77 / 16,213,083 | 50 / 16,039,093 |
| radio images | 5 (same set, same sizes) | 5 (same set, same sizes) |
| split apps | 8 (dxhdcp2, featenabler, hdcp1, hdcp2p2, hdcpsrm, loadalgota64, sp_license, winsecap) | 5 (dxhdcp2, featenabler, hdcpsrm, loadalgota64, **soter64**) |
| soter64 | absent | present |
| hdcp1/hdcp2p2/sp_license/winsecap | present | absent |

The radio-image layer is identical in shape (same 5 files, same sizes, per-build md5s); the split-app layer is vendor-configured per device/SoC. Both are honest census differences — not errors.

## ISA proof and interface facts

- `isa_identified` is empty for all 50 miami tz rows — honestly un-RE'd per the upstream DB convention [F]. The ELF64 mdt+bXX shape is family-established by the in-repo QSEE artifacts, not proven for miami payloads. [OPEN]
- Interface [I, labeled]: same QTEE loading chain as #940; soter64 serves the attestation/key-provisioning class. None miami-verified.

## Honest negatives

- No payload-level facts for miami's TEE (segment maps, QSEE metadata versions) — [OPEN], method ready in-repo (`analysis/tools/qsee_tz_map.py` path per `qsee-crossgen.md`).
- Split-app sizes not tabulated (10 components × 9 files = 90 numbers); census rows are the source of truth.
- Why dubai's extract carries 8 apps and miami's 5 (product configuration vs extract scope) is [OPEN] from metadata.

## What would upgrade this finding

1. Payload fetch (LineageOS miami radio extract): QSEE census on tz.img + the 5 split sets → first SM6375 TZ segment map.
2. soter64 corpus pass: 46 devices carry it — establish build-identity clusters (md5/sha sharing) across the whole fleet.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `miami Edge 30 Neo tz.img keymaster TEE` (GitHub code search, adineo-cmd/* excluded) → guides only; no SM6375/miami TEE artifact in-repo or public.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo method.
