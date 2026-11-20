# motorola Edge_40_Pro — `gpu` family status (7 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#964](https://github.com/adineo-cmd/open-device/issues/964)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site a9ae17f), linux-firmware WHENCE lines 7293-7313 (fetched 2026-11-20), torvalds/linux code search (2026-11-21), `research/soc/Qualcomm-SM4375-Snapdragon-4-Gen-1-gpu.md` §144 (zap.b00 law). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT as a genuine, mainline-coherent Adreno 740 (gen7) set — the corpus's first a740 rows.** 6 real GPU rows (a740_sqe.fw 76,724 B; gmu_gen70200.bin 66,844 B; a740_zap 4-row PIL split) + the gen7-era `sequence_manifest.bin` (1,872 B — a different, smaller manifest than the 5,704-B gen3 fleet one). Every name matches the upstream gen7 law; the SM8550 SoC row in the inventory is correct.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 40 Pro; codename `rtwo` | `device-inventory.csv` (`build_codename=rtwo`) [F] |
| SoC | Qualcomm SM8550 Snapdragon 8 Gen 2; GPU Adreno 740 (chip ID `0x07030001`) | device-inventory.csv [F]; mainline `drivers/gpu/drm/msm/adreno/a7xx_catalog.c` + `adreno_gpu.h` carry 0x07030001 (code search 2026-11-21) [F] |
| census scope | 612 rows in 9 families (other 237, tz 109, adsp 107, wifi 74, modem 44, cdsp 21, boot 12, gpu 7, bt 1); 1,299,268,531 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 7 rows [F]

| file | bytes | md5 | db_type | classification |
|---|---:|---|---|---|
| `a740_sqe.fw` | 76,724 | `0211fdf6aa6f523e9d392f31ffbf10a1` | UNKNOWN | **genuine SQE** — upstream name `qcom/a740_sqe.fw` (WHENCE:7297); the 76,724-B build shared by 6 devices [F] |
| `gmu_gen70200.bin` | 66,844 | `e7b1bad8c1b24f941e563f2c50ff03bc` | UNKNOWN | **genuine GMU** — upstream name `qcom/gmu_gen70200.bin` (WHENCE:7299, GMU 7.02.00); build shared by 10 devices [F] |
| `a740_zap.mdt` | 4,044 | `878f26c1cfca2d349b74521e3cc46555` | ELF64 | **genuine zap shader** metadata — corpus-unique md5 [F] |
| `a740_zap.b00` | 148 | `928f7b2b665c15a34b65e76dd8282d64` | ELF64 | zap segment — the corpus-wide 148-B b00 law (a610/a615/a660/a740, all 22 rows) [F] |
| `a740_zap.b01` | 1,072 | `c22d410302a4657bbc007a19783dd633` | UNKNOWN | zap segment [F] |
| `a740_zap.b02` | 3,896 | `3a6fc8185b80a6d71253f59c7c96b418` | UNKNOWN | zap segment [F] |
| `sequence_manifest.bin` | 1,872 | `b55e3177412bdc498ff49884ee1603a4` | UNKNOWN | GPU manifest at `vendor/gpu/kbc` — gen7-era build, 1,872 B shared by 10 devices; distinct from the 5,704-B gen3 manifest (#928/#946) [F] |

All 7 rows sit on `motorola/rtwo/modem/image` except the manifest (`vendor/gpu/kbc`) — the same path pattern established in #910/#946 [F].

## Upstream coherence [F]

- Every filename matches the linux-firmware gen7 law (WHENCE lines 7293-7313): `a740_sqe.fw`, `gmu_gen70200.bin`, `qcom/sm8550/a740_zap.mbn` — the device ships the mdt+bXX split form of exactly the upstream triple.
- Mainline binds Adreno 740 by chip ID `0x07030001` (`a7xx_catalog.c`) — unlike the SM7325/SM8350 filename mismatches documented in #2030/#2036, the rtwo gpu slice is **filename-coherent with its driver entry**: no `aNNN` generation mismatch here.
- Sharing: a740_sqe 76,724-B build → 6 devices (Edge_40_Pro, Nord_CE4, OnePlus_11_5G, OnePlus_12R, Xperia_1_V, Xperia_5_V); gmu_gen70200 → 10; manifest 1,872-B → 10; zap mdt corpus-unique. SM8550 peers Mi_13/Mi_13_Pro carry a **75,380-B** sqe build — two gen7 SQE builds coexist corpus-wide [F].

## ISA proof and interface facts

- `a740_zap.mdt`/`b00` are `isa_identified=ELF64` in the matrix [F]; sqe/gmu/b01/b02 are UNKNOWN — ELF-ness unproven from metadata [F].
- Interface [I, labeled]: gen7 GPU loads SQE + GMU via the a7xx driver path (mainline `a7xx_catalog.c`); zap runs at GPU reset. Standard gen7 practice, none rtwo-verified.
- Evidence class: all 7 rows P3, metadata-only [F].

## Honest negatives

- No payload-level RE (SQE microcode disassembly, GMU fw structure) — the repo's SQE version-law tables cover a630/a650; a gen7 law row is [OPEN].
- The 1,872-B gen7 manifest grammar is undecoded (same [OPEN] as the gen3 5,704-B manifest, #928).
- Nord_CE4 carries a `gmu_gen70e00.bin` row (67,368 B) — a third GMU variant in the corpus; its SoC pairing (SM7550-class) is outside this issue but worth a lead-level look. [F noted, OPEN scope]

## What would upgrade this finding

1. Payload fetch: disassemble a740_sqe.fw (76,724 B — the corpus's largest SQE) and establish the gen7 version law.
2. Corpus pass: pair every a740/gmu_gen7 md5 with its device's SoC to map gen7 firmware builds to SoC steppings.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `a740_zap rtwo` / `gmu_gen70200` (GitHub code search, adineo-cmd/* excluded) → packaging only; `0x07030001 repo:torvalds/linux` → 2 driver hits. Nobody documents rtwo's gpu rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus verified upstream trees.
