# motorola Edge_30_Fusion — `gpu` family status (10 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#946](https://github.com/adineo-cmd/open-device/issues/946)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site a515f38), `research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md` (#2036, commit 8b304e9) and `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md` (#2030), LineageOS wiki tundra variants page + GSMArena (fetched 2026-11-21). Evidence classes: [F] fact (command output) / [I] inference (labeled). No payloads fetched.

**Verdict: the gpu family is PRESENT and, unusually for this corpus, REAL.** Tundra is a Snapdragon 888+ device, so its 6 `a660` rows are its genuine Adreno 660 firmware (111,448 of the 189,084 gpu-labelled bytes); the other 4 rows are the shared Moto fleet artifacts (byte-identical with Edge_20's set). The upstream DB's SoC cell ("SM7250 Snapdragon 765G") is **wrong** — corrected here; and all 51 `a660_gmu.bin`/`a660_sqe.fw` rows corpus-wide carry `db_type=AUDIO` — a systematic upstream mislabel.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 30 Fusion (also sold as Moto S30 Pro); codename `tundra` | [LineageOS wiki tundra variants page](https://wiki.lineageos.org/devices/tundra/) ("edge 30 fusion", "moto S30 Pro", fetched 2026-11-21) [F]; `device-inventory.csv` (`build_codename=tundra`) [F] |
| SoC | Qualcomm **SM8350-AC Snapdragon 888+ 5G**; GPU Adreno 660 (chip ID `0x06060001`, ADRENO_6XX_GEN4) | GSMArena spec page (fetched 2026-11-21) [F]; [#2036](../../../research/soc/Qualcomm-SM8350-Snapdragon-888-gpu.md) §1 [F]. **The upstream DB's SoC cell says "SM7250 Snapdragon 765G" — wrong**; recorded here (Rule 1), the shared matrix stream is lead-owned |
| census scope | 639 rows total (other 229, wifi 203, tz 95, modem 38, adsp 35, cdsp 18, gpu 10, boot 10, bt 1); 843,007,454 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 10 rows, decomposed [F]

```
awk -F, '$1=="Edge_30_Fusion" && $4=="gpu"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv
```

| file | bytes | md5 | db_type | classification |
|---|---:|---|---|---|
| `a660_zap.mdt` | 6,860 | `de5c028d4b1aa8c619dda06ebe0fb71f` | (ELF64 isa field) | **genuine Adreno 660 zap** — corpus-unique md5; the 0x06060001 catalog entry binds `a660_zap.mdt` (#2036 §1) [F] |
| `a660_zap.b00` | 148 | `e1901644968ddf9b76af1d03626a466d` | (ELF64) | genuine, shared with Edge_30 + Moto_G200 [F] |
| `a660_zap.b01` | 6,712 | `9e598a0995bbceb47499988463e13a50` | UNKNOWN | genuine, corpus-unique [F] |
| `a660_zap.b02` | 1,976 | `e1341c9fa6f3b4d55ec0ecca0980198f` | UNKNOWN | genuine, shared with Edge_30 + Moto_G200 [F] |
| `a660_gmu.bin` | 55,256 | `179caf2e3b7d5481c3567c2987f5be32` | **AUDIO** (mislabel) | **genuine GMU firmware** — the 55,256-B build shared by 19 devices across eight SoC labels (per commit 029ede9; re-verified 2026-11-21) [F] |
| `a660_sqe.fw` | 40,496 | `08b7662ccd6815333aed6bce9bd69bd7` | **AUDIO** (mislabel) | **genuine SQE microcode** — shared by 21 devices [F] |
| `a615_zap.mdt` | 6,708 | `222f87861803bae8de24f0eb28bfc0d2` | (ELF64) | shared fleet artifact — byte-identical with Edge_20/Edge_2021/Edge_30 (5 devices) [F] |
| `a619_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | GPU | shared fleet artifact — 26 rows under two filenames (#928) [F] |
| `a630_sqe.fw` | 32,456 | `21693ef6f2d686ce79ebb3716a099970` | GPU | shared fleet artifact — the gen-2 build, 19 devices (#928) [F] |
| `sequence_manifest.bin` | 5,704 | `252630742d895255d66b5be984bdabda` | UNKNOWN | shared GPU manifest at `vendor/gpu/kbc` — 25 devices (#928) [F] |

Sum check [F]: 189,084 B total = genuine a660 set 111,448 (6860+148+6712+1976+55256+40496) + shared artifacts 77,636. 21 corpus devices carry a660_zap rows; tundra's mdt/b01 pair is unique (its own zap build), b00/b02 shared with Edge_30 and Moto_G200.

## The SoC-cell correction and what it fixes [F]

- The upstream DB labels tundra SM7250 765G. Public + in-repo evidence: SM8350-AC (GSMArena; LineageOS variants page; #2036's Adreno 660 identity for SM8350). The gpu census is *consistent with the correct SoC*: an SM7250 device (Adreno 620) would not carry the a660 zap/GMU/SQE set its own vendor ships here.
- Consequence for the corpus: the same wrong-SoC pattern flagged for dubai (#934/#940 corrections) recurs in the motorola slice — worth a lead-level SoC-cell audit across `device-inventory.csv`.

## The db_type=AUDIO mislabel [F]

All 51 `a660_gmu.bin` (21) and `a660_sqe.fw` (30) rows corpus-wide carry `db_type=AUDIO`. These are GPU firmware blobs (GMU microcontroller + SQE microcode, bound by the `a6xx_catalog.c` 0x06060001 entry per #2036 §1). The label is wrong corpus-wide; recorded here per file-wall rules — relabelling is lead-owned.

## ISA proof and interface facts

- `a660_zap.mdt` and `a615_zap.mdt` carry `isa_identified=ELF64` in the matrix [F]; the bXX/gmu/sqe rows are UNKNOWN/GPU/AUDIO bintypes — ELF-ness unproven from metadata [F].
- Interface: per #2036, mainline's SM8350 GPU node (`qcom,adreno-660.0` family, chip ID 0x06060001) loads exactly `a660_sqe.fw` + `a660_gmu.bin` + `a660_zap.mdt` — tundra ships all three, so its genuine GPU firmware set is **mainline-complete** (unlike Edge_20/Edge_2021, whose slice misses the bound set — #928/#2030) [F].
- Evidence class: all 10 rows P3, metadata-only [F].

## Honest negatives

- The vendor ships TWO GPU firmware generations side by side (a660 set + the a615/a619/a630 fleet artifacts). Which one the device's vendor driver actually binds is unknowable from metadata — mainline would bind a660; the vendor stack is [OPEN].
- `sequence_manifest.bin` decoding remains [OPEN] (#928).
- Whether the tundra-unique a660_zap mdt/b01 md5s reflect a tundra-specific GPU build or just a different OTA snapshot vs Edge_30/Moto_G200 is [OPEN] (payload compare).

## What would upgrade this finding

1. Payload fetch: disassemble tundra's `a660_sqe.fw` (40,496 B — the largest SQE build in the corpus at 40,496 vs the gen-1/2 32 KB builds) against the repo's SQE version law.
2. Corpus pass on the a660_zap split: 21 devices carry rows; establish which md5s pair with which SoC labels to test the "one build per SoC generation" law.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/DELTA comments on this issue. Check: `a660_zap tundra` (GitHub code search, adineo-cmd/* excluded) → packaging only; the SM8350 GPU identity is #2036's in-repo contribution, cited not re-derived. Nobody documents tundra's gpu rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo SoC analyses.
