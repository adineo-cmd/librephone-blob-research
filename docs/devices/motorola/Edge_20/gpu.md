# motorola Edge_20 — `gpu` family status (4 rows)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#928](https://github.com/adineo-cmd/open-device/issues/928)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 1579b8d), the in-repo SoC ground truth `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md` (issue #2030, commit 976387a). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT in the census and UNUSABLE by mainline.** All 4 rows are already identified and explained at SoC level by [#2030](../../../research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md): the SM7325 GPU is mainline `adreno-635.0` (chip ID `0x06030500`), commercially Adreno 642L, and mainline binds it to the **a660 firmware set — none of which appears in the matrix**. The four present rows belong to other GPU generations. This doc records the device slice and adds corpus-wide sharing facts; nothing here re-derives #2030.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 20; codename `berlin` | `device-inventory.csv` (`build_codename=berlin`) |
| SoC | Qualcomm SM7325 Snapdragon 778G 5G (GPU: mainline `adreno-635.0`, commercial Adreno 642L) | device-inventory.csv; [#2030](../../../research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md) §1 |
| census scope | 31 rows total (other 12, adsp 6, bt 4, gpu 4, boot 3, wifi 2); 139,626,681 B | coverage-matrix.csv + device-inventory.csv |

## The 4 rows (census + what #2030 established about each)

```
awk -F, '$1=="Edge_20" && $4=="gpu"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv
```

| file | bytes | md5 | class per #2030 |
|---|---:|---|---|
| `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` | Qualcomm GPU manifest, at `motorola/berlin/vendor/gpu/kbc` — not a mainline-bound firmware name |
| `a615_zap.mdt` | 6,708 | `222f87861803bae8de24f0eb28bfc0d2` | ELF64; belongs to the **a615** (Adreno 615) catalog entry — wrong generation for 0x06030500 |
| `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | GMU firmware of **Adreno 619** (`a6xx_catalog.c:876`/`:901`, revn 619 per #2030) |
| `a630_sqe.fw` | 32,456 | `21693ef6f2d686ce79ebb3716a099970` | SQE of the gen-1/2 a630 line; the 0x06030500 entry binds `a660_sqe.fw` instead |

Missing for mainline (set difference from #2030 §3): `a660_sqe.fw`, `a660_gmu.bin`, `a660_zap.mbn` — zero of the four blobs mainline requires are in the corpus slice.

## Corpus-wide sharing (new, command-verified 2026-11-20)

| md5 | file | devices sharing it byte-identically |
|---|---|---|
| `252630742d895255d66b5be984bdabda` | `sequence_manifest.bin` | **25** — the Moto Edge + G fleet, FP5, Moto G200, OnePlus 9/9 Pro/9RT, Nothing Phone 1, Nord CE2/CE3/200, Realme 9/10 Pro, Xperia 10 IV/V and 5 III, G Stylus 5G-2 — spanning SM7325, SM8350 and SM6375 SoC classes |
| `9e23c52057bb573dee9ba31f1fdba4fa` | `a619_gmu.bin` | **26 rows under two filenames** — 24 as `a619_gmu.bin` (same fleet plus Pixel 4A_5G/5/5A, Xperia 1 II/5 II/5 III) and 2 as `a618_gmu.bin` (Galaxy_A71, Mi_A3): the corpus's a618/a619 GMU "files" are one byte-identical build shipped under two names |
| `21693ef6f2d686ce79ebb3716a099970` | `a630_sqe.fw` | **19** — the 32,456-B gen-2 SQE build (Edge_2021/30/30_Fusion/30_Neo, Moto G200/34_5G/5G-2024/82_5G/84_5G, Nord CE2/CE3/CE4, Realme 9/10 Pro, Xperia 10 IV/V, Xperia 5 III, G Stylus 5G-2) |
| `222f87861803bae8de24f0eb28bfc0d2` | `a615_zap.mdt` | **5** — Edge_20, Edge_2021, Edge_30, Edge_30_Fusion, Moto_G200 |

Reading: these four files are **fleet artifacts, not device-unique firmware** — they ship identically across whole SoC generations, which is exactly why the filename-keyed census cannot identify the SM7325 GPU (the #2030 headline finding) and why per-device RE work here reduces to pointing at the shared builds.

## ISA proof and interface facts

- `a615_zap.mdt` is `isa_identified=ELF64` in the matrix (verified field); the other three rows are `UNKNOWN`/`GPU` bintypes — ELF-ness unproven from metadata.
- Interface: per #2030, mainline's `adreno-gmu-635.0` node expects `a660_gmu.bin`/`a660_sqe.fw`; the a619/a630 files here satisfy a **different** driver entry and would not be bound by a mainline SM7325 DT. The `vendor/gpu/kbc` path for `sequence_manifest.bin` indicates a vendor GPU-manifest location, not a firmware-loader path.
- Evidence class: all 4 rows P3 (metadata-only; md5s from the upstream DB).

## Honest negatives

- What `sequence_manifest.bin` contains (5,704 B manifest grammar) is **not decoded in this repo** — #2030 documents its presence and path only; decoding needs the payload. [OPEN]
- Whether the berlna/berlin vendor builds bind these files through a vendor-specific GPU driver (rather than mainline's naming) is unknowable from metadata. [OPEN]
- The missing `a660_zap.mbn`/`a660_gmu.bin`/`a660_sqe.fw` would come from a linux-firmware fetch, not from this device's vendor tree — the vendor ships generation-mismatched names on this hardware, per #2030.

## What would upgrade this finding

1. Decode `sequence_manifest.bin` (payload gate) — a 25-device-shared manifest across the whole 642L fleet is a leverage family on its own.
2. Cross-check the a619_gmu/a630_sqe builds against linux-firmware's `qcom/a619_gmu.bin` + `qcom/a630_sqe.fw` (v2.07) to fingerprint which upstream build each fleet device carries.

## RULE 0 record (2026-11-20)

Queries in the SEARCH/DELTA comments on this issue. Prior-art check: GitHub code search `sequence_manifest.bin gpu kbc` (adineo-cmd/* excluded) → packaging only; the SoC identity work is #2030's in-repo contribution and is cited throughout rather than duplicated.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo SoC analysis.
