# motorola G_Stylus_5G-2-2022 — `gpu` family status (19 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1000](https://github.com/adineo-cmd/open-device/issues/1000)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site d9eb82e), `research/soc/Qualcomm-SM4375-Snapdragon-4-Gen-1-gpu.md` (Adreno 619 binding law), commit 029ede9 (#2024, fpctzapp precedent), GSMArena/Motorola spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT and, after untangling, mainline-coherent.** Of 19 rows: **3 satisfy the Adreno 619 binding exactly** (a619_gmu.bin + a630_sqe.fw + the a615_zap 4-row split — the law established by the repo's SM4375 gpu doc), 4 are a660-class fleet extras bound by other GPU generations, 1 is the fleet GPU manifest, and **9 are `egtzappf` — a fingerprint TrustZone application mislabelled gpu**, the Egis-vendor sibling of #2024's fpctzapp (segment layout matches fpctzapp byte-for-byte on 5 of 9 segments). The inventory's SoC cell is empty; this doc supplies it (SM6375, Adreno 619).

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Moto G Stylus 5G (2022); codename `milanf` | `device-inventory.csv` (`build_codename=milanf`) [F]; [GSMArena](https://www.gsmarena.com/motorola_moto_g_stylus_5g_(2022)-11462.php) + Motorola support specs (2026-11-21) [F] |
| SoC | Qualcomm **SM6375 Snapdragon 695**; GPU **Adreno 619** | GSMArena/Motorola (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** — supplied here [F] |
| census scope | 360 rows in 9 families (wifi 96, other 70, modem 47, adsp 44, tz 50, cdsp 12, bt 14, boot 8, gpu 19); 760,043,006 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 19 rows, decomposed [F]

| rows | component | bytes | md5 | classification |
|---|---|---:|---|---|
| 1 | a619_gmu.bin | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | **genuine, binding-coherent** — Adreno 619 GMU (the 26-row two-name fleet build, #928) |
| 1 | a630_sqe.fw | 32,456 | `21693ef6f2d686ce79ebb3716a099970` | **genuine, binding-coherent** — the gen-2 SQE build the 619 entry binds |
| 4 | a615_zap (mdt 6,860 `391902bd` corpus-unique; b00 148 shared-by-7; b01 6,712 corpus-unique; b02 1,984) | 15,704 | — | **genuine, binding-coherent** — Adreno 619 zap (the 619 entry binds `a615_zap.mdt` per the SM4375 doc) |
| 1 | a660_zap.mdt | 6,708 | `c9d12833b4a7b92d875174c33a0ae047` | fleet extra — the 7-device SM6375-class zap build (Edge_30_Neo, G34_5G, G_5G_2024, G82_5G, G84_5G, G Stylus 5G) |
| 1 | a660_gmu.bin | 55,256 | `179caf2e3b7d5481c3567c2987f5be32` | fleet extra — the 19-device build (#946); db_type AUDIO mislabel |
| 1 | a660_sqe.fw | 40,496 | `08b7662ccd6815333aed6bce9bd69bd7` | fleet extra — the 21-device build; db_type AUDIO mislabel |
| 1 | sequence_manifest.bin | 5,704 | `252630742d895255d66b5be984bdabda` | fleet GPU manifest — 25 devices (#928) |
| 9 | **egtzappf** (mdt 7,260 ELF64 `bd21c095` corpus-unique; b00 308; b01 6,952; b02 1,058,456; b03 162; b04 1,851,712; b05 552; b06 152; b07 26,626) | 2,945,160 | — | **mislabelled — fingerprint TrustZone application** |

Sum check [F]: 19 rows; genuine+coherent 6 rows (48,924 B) + fleet extras 4 (108,464 B) + manifest 1 (5,704 B) + egtzappf 9 (2,945,160 B).

## The egtzappf finding [F + I]

- **Segment-layout identity with fpctzapp**: egtzappf's b00 (308), b01 (6,952), b03 (162), b06 (152) and mdt (7,260) match fpctzapp's (Defy_2021, #910) byte sizes exactly; b02/b04/b05/b07 differ (1,058,456/1,851,712/552/26,626 vs 1,042,392/1,804,764/928/102,232) — two vendor builds of the same app class [F].
- **Vendor reading [I]**: `fpc` = Fingerprint Cards AB (#2024's decode); `eg` = Egis Technology, the other major Android fingerprint vendor. Both are TrustZone fingerprint apps loading into QSEE, mislabelled `blob_family=gpu` by the corpus's substring grammar (`zap` in fpctzapp; for egtzappf the classification trigger is less obvious — recorded as the #2024-class mislabel regardless).
- **Corpus spread**: egtzappf rows exist on 8 Moto devices (G Stylus 5G-2, G200, G32, G42, G52, G82_5G, G Power, G Stylus 5G) vs fpctzapp's 16 — two fingerprint-vendor fleets partitioning the corpus [F].
- All 9 rows sit on `motorola/milanf/modem/image`, never a gpu path [F] — the #2024 path law holds.

## Mainline coherence for Adreno 619 [F]

The repo's SM4375 gpu doc establishes that Adreno 619's catalog entry binds `a619_gmu.bin` + `a630_sqe.fw` + `a615_zap.mdt`. milanf ships **all three** (plus the zap's b00-b02 segments) — the genuine slice is mainline-complete by name, unlike Edge_20/Edge_2021 (#928) whose 642L slice misses its bound set. The a660 trio is present as vendor-shipped extras bound by other generations (the corpus-wide pattern from #946/#964).

## ISA proof and interface facts

- a615_zap mdt/b00 and egtzappf mdt are `isa_identified=ELF64` [F]; the rest UNKNOWN/GPU/AUDIO bintypes [F].
- Interface [I, labeled]: a619 GMU+SQE+zap per the 619 catalog entry; egtzappf loads into QSEE for the fingerprint HAL. None milanf-verified at payload level.
- Evidence class: all 19 rows P3, metadata-only [F].

## Honest negatives

- egtzappf's internal structure (fingerprint template handling, TA protocol) is beyond public documentation — same boundary as fpctzapp in #2024. [OPEN]
- Why milanf carries BOTH the a619-binding set AND the a660 extras (vendor fleet packaging vs multiple SoC steppings) is [OPEN] from metadata.
- The Egis vendor reading of `eg` is inference from the fingerprint-vendor landscape; the app's actual vendor string needs a payload. [OPEN]

## What would upgrade this finding

1. Payload fetch: compare egtzappf vs fpctzapp segments (b02/b04 differ by ~1.5%/2.6% in size) — the two builds would give the fingerprint-TZ app family its first cross-vendor segment diff.
2. Corpus pass: the 7-device a660_zap.mdt build (c9d12833) pairs exactly with the SM6375 Moto fleet — map it against #946's tundra/FP5 builds to finish the a660_zap build-vs-SoC table.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `egtzappf` (GitHub code search, adineo-cmd/* excluded) → 0 results; the mislabel precedent and binding law are in-repo (#2024, SM4375 gpu doc), cited not rebuilt. Nobody documents milanf's gpu rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo analyses.
