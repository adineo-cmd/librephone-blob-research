# samsung Galaxy_A71 — `gpu` family status (3 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1018](https://github.com/adineo-cmd/open-device/issues/1018)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 06bfd27), linux-firmware WHENCE line 7258 (fetched 2026-11-20), device docs #928/#910, public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT as a compact gen-1 6xx GMU/SQE set — and it contains the corpus's second data point for the two-name GMU finding.** 3 rows: `a618_gmu.bin` (the byte-identical twin of the a619_gmu fleet build, shipped under its own name here — #928), `a630_gmu.bin` (an 8-device gen-1 GMU build), and `a630_sqe.fw` (the 13-device gen-1 SQE build). The device's GPU is an Adreno 618; the upstream inventory's SoC cell is empty and is supplied here.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy A71; codename `a71` | `device-inventory.csv` (`build_codename=a71`) [F] |
| SoC | Qualcomm **SDM7150 Snapdragon 730(G)**; GPU **Adreno 618** | public spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** — supplied here [F] |
| census scope | 22 rows in 6 families (other 9, boot 6, gpu 3, wifi 2, bt 1, modem 1); 212,057,122 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 3 rows [F]

| file | bytes | md5 | db_type | classification |
|---|---:|---|---|---|
| `a618_gmu.bin` | 32,768 | `9e23c52057bb573dee9ba31f1fdba4fa` | GPU | **the two-name GMU build** — byte-identical to the `a619_gmu.bin` fleet build (#928: 24 rows as a619_gmu + 2 rows as a618_gmu, Galaxy_A71 + Mi_A3) [F] |
| `a630_gmu.bin` | 32,768 | `1ade6a659713b4424a27eb2afd70d614` | GPU | **gen-1 GMU build** — shared byte-identically by 8 devices (Galaxy_A71, Mi_A3, OnePlus_7/7_Pro/7T/7T_Pro, Redmi_Note_8, Z5_Pro_GT); upstream name `qcom/a630_gmu.bin` (WHENCE:7258) [F] |
| `a630_sqe.fw` | 32,304 | `42b0a1566c41917df56f15f7d9c7c479` | GPU | **gen-1 SQE build** — the 13-device shared build documented in #910 [F] |

All 3 rows at `samsung/a71/vendor/firmware`, all P3, all corpus-shared builds (no corpus-unique md5 here — unlike every Moto slice) [F].

## What the three rows say together [F]

- **Two GMU generations side by side**: the a618-named build (byte-identical with the a619-named one) and the a630-named build — the vendor ships both GMU images for a GPU that binds only one. Which one the platform loads is [OPEN] from metadata.
- **No zap row**: A71's slice has no `a618_zap`/`a630_zap` — the zap-shader layer is absent from this census (contrast berlin/dubai/tundra which carry zap splits). Extract-scope vs platform question, [OPEN].
- **The Adreno 618 pairing** [I, labeled]: mainline's 618-class entries bind the a619_named GMU build family and a630_sqe (#928's law); A71's rows satisfy that pattern by name and build identity.
- All three md5s are corpus-shared builds — A71's gpu census contains zero device-unique bytes, the cleanest fleet-artifact slice documented so far.

## ISA proof and interface facts

- All three rows carry `db_type=GPU` — the cleanest labeling in the corpus's gpu family (contrast the a660 AUDIO mislabels, #946) [F]. No ELF claims from metadata [F].
- Interface [I, labeled]: GMU microcontroller + SQE microcode load per the gen-1 6xx driver path; none A71-verified at payload level.

## Honest negatives

- The a618-vs-a630 GMU loading question and the missing zap layer are [OPEN] from metadata.
- Exact mainline chip-ID binding for Adreno 618 was not re-derived this session (the repo's catalog citations in #2030/#2036 cover the a6xx law; the 618 row follows it). [I]

## What would upgrade this finding

1. Payload fetch: hash-compare A71's a618_gmu.bin against the a619_gmu.bin fleet build (md5 identity says they ARE the same bytes — a payload diff would confirm nothing vendor-specific hides in the copy).
2. Corpus pass: map every a630_gmu/a618_gmu/a619_gmu row to its device's SoC to complete the gen-1 GMU build-vs-SoC table.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy A71 Adreno 618 gpu firmware a618_gmu` (web + GitHub code search, adineo-cmd/* excluded) → guides only; the two-name GMU finding is #928's, cited.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo analyses.
