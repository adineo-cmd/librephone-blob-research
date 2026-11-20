# fairphone FP6 — `tz` family status (111 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#994](https://github.com/adineo-cmd/open-device/issues/994)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 0c488af), the payload-derived in-repo census `research/qualcomm/docs/trustzone-census.md` (FP6, QCM6490), the sibling decompositions (#940/#958/#976). No payloads fetched this session; every number is command output or quoted from the committed census.

**Verdict: the tz family is PRESENT in two structurally distinct layers** — 7 radio TEE images (payload-censused in-repo: monolithic AArch64 ELFs, no mdt/bXX split) + 104 split-form rows the census does **not** cover (ten 10-row PIL splits — a generational grammar change, mdt + b00..b08 — plus the 4-row `cpusys_vm`). Cross-check of the DB radio rows against the census: **6 of 7 match byte-exactly; tz.img is off by exactly one 4-K page** ([OPEN]: partition padding vs build difference).

## Device identity

| fact | value | source |
|---|---|---|
| model | Fairphone 6; codename `FP6` | `device-inventory.csv` [F] |
| SoC | Qualcomm QCM6490 ("Lanai"/"Milos") | `research/qualcomm/docs/trustzone-census.md` + bootchain-census.md [F]; inventory SoC cell empty — supplied here |
| priority | **P1 — FSF flagship** | device-inventory.csv [F] |
| census scope | 447 rows in 9 families; tz = 111 rows, 13,210,040 B | coverage-matrix.csv [F] |

## The radio layer — cross-verified against the payload census [F]

| DB row | DB bytes | census bytes | md5 corpus-unique | match |
|---|---:|---:|---|---|
| tz.img | 4,030,464 | **4,034,560** | yes | **MISMATCH (one 4-K page)** |
| hyp.img | 1,683,456 | 1,683,456 | yes | OK |
| keymaster.img | 442,368 | 442,368 | yes | OK |
| uefisecapp.img | 200,704 | 200,704 | yes | OK |
| devcfg.img | 49,152 | 49,152 | yes | OK |
| multiimgoem.img | 12,288 | 12,288 | yes | OK |
| featenabler.img | 106,496 | 106,496 | yes | OK |

The census's structural findings for these images stand as the authoritative record [F, quoted]: **monolithic AArch64 ELF partition images — no .mdt/.bXX split at all** (a format change vs older platforms); QTEE (tz, 45 program headers) and QHEE (hyp, entry 0x80000000) are one build `TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1`; KeyMaster TA, devcfg, and the QSEE TAs uefisecapp/multiimgoem/featenabler complete the set. The tz.img delta (4,034,560 - 4,030,464 = 4,096) is exactly one page — partition-image padding vs a build difference cannot be distinguished from metadata. [OPEN]

## The split layer — 104 rows the census does not cover [F]

| rows | component | db_path | role [I, name-derived] |
|---|---|---|---|
| 10 each | featenabler, focal64, hdcp1, hdcp2p2, hdcpsrm, loadalgota64, smplap64, soter64, sp_license, winsecap | modem/image | QSEE-class TZ apps: fingerprint (focal64 — the FocalTech-family fingerprint app), HDCP set, OTA loader, Soter attestation, SMPLAP, secure-processor licensing, Windows security |
| 4 | cpusys_vm (mdt + b00..b03) | modem/image | CPU-subsystem VM image — a **4-row split**, a third shape |

Grammar evolution [F]: FP6's split apps are **10-row** (mdt + b00..b08 — nine segments) vs the 9-row grammar on dubai/miami/FP4 and the 4-row cpusys_vm. 10 x 10 + 4 + 7 = 111 [F]. Sum check [F]: 13,210,040 B total. `isa_identified` is empty on all 111 rows — honestly un-RE'd [F]; though the census proved the radio images are AArch64 ELFs, and the census's own architecture histogram (fp6-architecture-census.md) classed hdcp/soter64/smplap64/evautil64 in modem/image as AArch64 [F].

## Comparison with the sibling decompositions [F]

| aspect | dubai (#940) | miami (#958) | FP4 (#976) | FP6 (this doc) |
|---|---|---|---|---|
| tz rows / bytes | 77 / 16,213,083 | 50 / 16,039,093 | 61 / 8,079,433 | 111 / 13,210,040 |
| radio images | 5 | 5 | 7 | **7** |
| radio form | mdt-split era? unknown | unknown | unknown | **monolithic ELF (proven)** |
| split grammar | 9-row | 9-row | 9-row | **10-row** + a 4-row form |
| split apps | 8 | 5 | 6 | **10** (+cpusys_vm) |
| tz.img | 4,194,304 | 4,194,304 | 3,031,040 | 4,030,464 (census: 4,034,560) |
| hyp.img | 8,388,608 | 8,388,608 | 409,600 | 1,683,456 |

FP6 is the only device in the documented shard whose radio TEE images are payload-proven monolithic ELFs — the census's "format change worth documenting".

## Honest negatives

- The 104 modem/image split rows have **no payload census** — the trustzone census covered the 7 radio partitions only; segment tables, QSEE metadata versions and the 10-row grammar's segment semantics are [OPEN] (method ready in-repo).
- The tz.img page-delta and the xbl.img delta from #988 share a shape (both FP6, both small, both [OPEN]) — a systematic DB-vs-nightly build offset is plausible but unproven from metadata.
- cpusys_vm's role is name-derived [I]; no public source documents it.

## What would upgrade this finding

1. Payload fetch: extend the trustzone census to the 10 split apps + cpusys_vm (the modem/image tree is already extracted per fp6-architecture-census.md) — the 10-row grammar would get its first segment table.
2. Settle both FP6 size deltas by joining the census JSON hashes against the DB md5s.

## RULE 0 record (2026-11-21)

Prior-art search for FP6's TEE was performed by the census itself (2026-11-10: `LANAIAAAAANAZT OR TZ.XF.5.28` -> 18 Xiaomi board-info hits, zero analysis). This session's delta is the cross-verification and the split-layer decomposition; no new uniqueness claims beyond it.

Not legal advice; no proprietary payload accessed or committed this session — structural facts quoted from the committed census, census facts command-verified against the matrix.
