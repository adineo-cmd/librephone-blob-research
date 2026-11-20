# fairphone FP5 — `gpu` family status (4 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#982](https://github.com/adineo-cmd/open-device/issues/982)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 5523fd8), `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md` (#2030), `research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md` (#2036), device docs #946/#964. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT and mainline-complete** — FP5's SoC (QCM6490, the SM7325-derived IoT variant) exposes the `0x06030500` GPU that mainline binds to the **a660 firmware set** (#2030 §1.3), and all three bound blobs are in FP5's slice: `a660_sqe.fw` + `a660_gmu.bin` + `a660_zap.mdt`. Two of the three are **QCM6490-specific builds** (corpus-unique), and the fourth row is the gen3 `sequence_manifest.bin` fleet artifact. The upstream `db_type=AUDIO` mislabel recurs here.

## Device identity

| fact | value | source |
|---|---|---|
| model | Fairphone 5; codename `FP5` | `device-inventory.csv` (`build_codename=FP5`) [F] |
| SoC | Qualcomm QCM6490 (SM7325-derived IoT SoC); GPU bound by mainline as `adreno-635.0`/`0x06030500` → a660 firmware | device-inventory.csv [F]; #2030 §1.3 [F] |
| priority | **P2** — pmOS community port noted in the inventory [F] | device-inventory.csv |
| census scope | 706 rows in 9 families (other 270, wifi 210, tz 106, adsp 52, cdsp 18, modem 32, boot 10, bt 4, gpu 4); 588,299,075 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 4 rows [F]

| file | bytes | md5 | db_type | classification |
|---|---:|---|---|---|
| `a660_zap.mdt` | 6,708 | `0711c6bc3b5bde15a7f989dae027d390` | ELF64 isa field | **genuine, QCM6490-specific** — corpus-unique md5; note the size equals `a615_zap.mdt`'s (6,708) while tundra's a660_zap.mdt is 6,860 B — per-SoC zap builds [F] |
| `a660_gmu.bin` | **55,252** | `cd3a235218418f51360888637c1cb2ac` | AUDIO (mislabel) | **genuine, QCM6490-specific** — corpus-unique md5 AND size: the fleet build is 55,256 B (19 devices, #946); FP5's is 4 bytes smaller [F] |
| `a660_sqe.fw` | 40,496 | `08b7662ccd6815333aed6bce9bd69bd7` | AUDIO (mislabel) | **genuine, shared** — the 21-device gen-2 SQE build (#946) [F] |
| `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` | UNKNOWN | gen3 fleet GPU manifest — 25 devices incl. FP5 (#928) [F] |

Sum check [F]: 108,160 B total.

## Why this slice is mainline-complete [F]

#2030 §1.3: mainline's `0x06030500` catalog entry requires `a660_sqe.fw`, `a660_gmu.bin`, `a660_zap.mdt`. FP5's census carries **all three** — unlike Edge_20/Edge_2021 (#928), whose slices carry none of the bound set. FP5 is therefore the first device in the documented shard whose gpu rows satisfy mainline's own requirements by name. The two corpus-unique builds (zap mdt, gmu) mark FP5's QCM6490-specific firmware, while the SQE matches the shared gen-2 build.

## The db_type=AUDIO mislabel [F]

`a660_sqe.fw` and `a660_gmu.bin` carry `db_type=AUDIO` here too — the same corpus-wide mislabel recorded for all 51 a660 rows in #946. These are GPU firmware blobs bound by the a6xx/a7xx catalog, not audio payloads. Recorded per file-wall rules; relabelling is lead-owned.

## ISA proof and interface facts

- `a660_zap.mdt` is `isa_identified=ELF64` [F]; sqe/gmu/manifest are UNKNOWN/AUDIO bintypes [F].
- Interface: per #2030, mainline's `adreno-gmu-635.0` node loads `a660_gmu.bin` + `a660_sqe.fw`; zap at GPU reset. FP5's files satisfy this by name [F]; payload-level behavior unverified [OPEN].
- Evidence class: all 4 rows P3, metadata-only [F].

## Honest negatives

- Whether FP5's vendor stack binds the same a660 set mainline does is [OPEN] (vendor driver introspection needs payloads).
- The 4-byte a660_gmu difference (55,252 vs 55,256) is a build variant, not a truncation — content-level comparison needs both payloads. [OPEN]
- `sequence_manifest.bin` decoding remains [OPEN] (#928).

## What would upgrade this finding

1. Payload fetch: compare FP5's 55,252-B a660_gmu.bin against the 19-device 55,256-B build — a 4-byte delta on a fleet-shared blob is a fingerprint worth having.
2. Corpus pass: a660_zap.mdt sizes corpus-wide (6,708 FP5 vs 6,860 tundra vs others) to test whether zap builds track SoC stepping.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/DELTA comments. Check: `FP5 QCM6490 Adreno gpu firmware a660 zap` (GitHub code search, adineo-cmd/* excluded) → packaging only; the a660 binding identity is #2030/#2036's in-repo contribution, cited not re-derived.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo SoC analyses.
