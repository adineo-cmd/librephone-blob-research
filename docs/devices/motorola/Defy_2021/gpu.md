# motorola Defy_2021 — `gpu` family status (14 rows)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#910](https://github.com/adineo-cmd/open-device/issues/910)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 85d1d5c), `upstream-contribution/blob-database/device-inventory.csv`, linux-firmware WHENCE (git.kernel.org, fetched 2026-11-20), torvalds/linux (GitHub code search, 2026-11-20). No payloads fetched; every number below is command output or a recorded fetch.

**Verdict: the gpu family is PRESENT but overstated.** Of the 14 `blob_family=gpu` rows, **5 are genuine Adreno 610 firmware** (the 4-row `a610_zap` PIL split + `a630_sqe.fw`, 48,120 B) and **9 are mislabelled `fpctzapp` rows — the FPC fingerprint TrustZone application** (2,965,148 B), following the corpus-wide mislabel proven in-repo by commit 029ede9 (issue #2024). Live GPU payload in this census: 48,120 of 3,013,268 gpu-labelled bytes (1.6%) — a naive gpu census overstates the live payload ~63×.

## Device identity

| fact | value | source (access date) |
|---|---|---|
| model | Motorola Defy (2021), XT2075 / XT2083-8; codename `bathena` | GSMArena / PhoneArena / Notebookcheck (2026-11-20); in-repo `device-inventory.csv` (`build_codename=bathena`) |
| SoC | Qualcomm SM6115 Snapdragon 662; GPU Adreno 610 | device-inventory.csv; mainline `arch/arm64/boot/dts/qcom/sm6115.dtsi` carries compat string `adreno-610.0` (verified by code search 2026-11-20); in-repo `research/soc/per-soc-method-plans.md:354` lists bathena among SM6115 devices |
| census scope | 226 rows total (adsp 39, other 53, modem 43, wifi 41, gpu 14, boot 9, bt 11, cdsp 11, tz 5); 562,085,430 B | coverage-matrix.csv + device-inventory.csv (`blob_rows_devices_sql=226`) |

## The 14 rows, decomposed

```
awk -F, '$1=="Defy_2021" && $4=="gpu"{print $6, $7, $8, $13, $14}' coverage-matrix.csv
```

| rows | component | classification | evidence |
|---|---|---|---|
| 4 | `a610_zap.mdt` 6,860 B ELF64 (md5 `571da33022d67db695ab867abc0c870f`), `.b00` 148 B ELF64 (`fac927275ef4f969398b189882afa6d4`), `.b01` 6,712 B (`723c3be07c3bae13afbc96c86bc77412`), `.b02` 2,096 B (`ca88ac01d8a4e8004983cf53f0b02e01`) | **genuine Adreno 610 zap-shader PIL split** | upstream name law `qcom/qrb4210/a610_zap.mbn` v0.20 (WHENCE line 7248, fetched 2026-11-20); QRB4210 = SM6115-family platform |
| 1 | `a630_sqe.fw` 32,304 B (md5 `42b0a1566c41917df56f15f7d9c7c479`), db_type GPU, at `motorola/bathena/vendor/firmware` | **genuine SQE microcode** | upstream `qcom/a630_sqe.fw` v2.07 (WHENCE line 7259) — the gen-1 6xx SQE build |
| 9 | `fpctzapp.mdt` 7,260 B ELF64 (`abfd7bc4290d774df8b97834f60dbf18`) + `.b00` 308 B (`bb550946ac85bada70420c7ca4573da3`), `.b01` 6,952 B (`0ebaf9dfe65040148e8fc853d550e72c`), `.b02` 1,042,392 B (`ffc9fb8a2d0157a57a14087eda57e930`), `.b03` 160 B (`7778174cfec8f4416e90484da0d9d7a2`), `.b04` 1,804,764 B (`89a9caac41104e64ee4201a2ef0cec30`), `.b05` 928 B (`d70344cf09b478a7fd6d5756bde28a77`), `.b06` 152 B (`e1f9ed433baf5f91639b7e1e067bc933`), `.b07` 102,232 B (`edac2c610fe771c0c3b3f4e428763cbe`) | **mislabelled — FPC fingerprint TrustZone application** | in-repo commit 029ede9 (issue #2024): `fpc` = Fingerprint Cards AB, `tzapp` = TrustZone app loading into QSEE; the gpu-family grammar (`gmu/sqe/zap/aNNN_*`, per `research/soc/per-soc-method-plans.md`) matches the `zap` substring inside `fpctzapp` — the presumable misclassification mechanism (mechanism inferred, mislabel itself proven in #2024) |

Sum check (command-verified): total gpu-labelled 3,013,268 B = a610_zap 15,816 + a630_sqe.fw 32,304 + fpctzapp 2,965,148. Thirteen of the 14 rows sit on `motorola/bathena/modem/image` (the 4 zap rows and all 9 fpctzapp rows); only `a630_sqe.fw` carries db_type=GPU and lives at `motorola/bathena/vendor/firmware`.

## Cross-corpus identity facts

```
awk -F, '$6 ~ /^a610_zap/{print $6, $8}' coverage-matrix.csv | sort -u
```

- `a610_zap.b00` and `.b02` are **byte-identical across all 11 devices** that carry the full split set (single md5 each corpus-wide; 16 devices carry any a610_zap row, 5 of them mdt-only); the `.mdt` (14 md5s) and `.b01` (10 md5s) vary per build. Defy_2021's `mdt`/`b01` pair is **unique in the corpus** — no other device shares them; its b00/b02 are the shared ones.
- `a630_sqe.fw` exists in 7 byte-distinct builds corpus-wide (32,136 / 32,264 / 32,272 / 32,304 / 32,448 / 32,456 / 32,504 B); Defy_2021's 32,304-B build is the shared gen-1 build, byte-identical on 12 sibling devices (Galaxy_A71, Mi_A3, Moto_G10/G9/G9_Power/G_Power, OnePlus_7/7_Pro/7T/7T_Pro, Redmi_Note_8, Z5_Pro_GT).
- Five devices (Mi_A3, Phone_1, Phone_2, Pro_1X, Redmi_Note_8) carry only the `a610_zap.mdt` row without its `bXX` splits — a partial-census pattern, not a different firmware shape.

## Container layout, ISA proof, interface facts (the 5 genuine rows)

- **PIL split layout**: `a610_zap.mdt` is the ELF metadata header, `.b00`–`.b02` the program segments; mdt and b00 are `isa_identified=ELF64` in the matrix (verified field, not inferred). Same 4-file grammar as every Qualcomm mdt/bXX firmware in this DB.
- **Interface**: loaded by the mainline msm GPU driver's zap-shader path; the GPU binds via the `adreno-610.0` compat string in `sm6115.dtsi` (torvalds/linux, code search 2026-11-20). SQE microcode is fetched by the GPU at init (upstream filename contract `qcom/a630_sqe.fw`, WHENCE v2.07).
- **Location anomaly**: all four zap rows sit under `motorola/bathena/modem/image` — the vendor shipped the GPU zap inside the modem image directory, not vendor/firmware where `a630_sqe.fw` lives. Recorded as a census-path fact; harmless for identification, worth knowing when the payload lands.
- **Evidence class**: all 14 rows P3 (metadata-only, no payload on box); upstream DB md5s recorded above.

## Honest negatives

- The fpctzapp reclassification is **not fixed in the matrix** — `coverage-matrix.csv` still labels these 9 rows gpu. Per file-wall rules this deliverable records the correction; relabelling the upstream DB stream is lead-owned (issue #2024 established the same for the corpus).
- Payload-level RE (what the zap microcode does at GPU reset, SQE syscall surface) is out of scope without payloads; the repo's [OPEN] SQE register/patch-semantics questions (`research/soc/Qualcomm-SM4375-Snapdragon-4-Gen-1-gpu.md`) apply to the 32,304-B SQE build too.
- No Defy-specific prior art exists for these files (see NO-PRIOR-ART comment, 2026-11-20); all naming/structure facts derive from upstream trees + in-repo precedent, both command-verified here.

## What would upgrade this finding

1. Payload fetch of the Defy 2021 vendor image: byte-verify the 14 md5s above; disassemble `a630_sqe.fw` against the repo's SQE version-law table (WHENCE v2.07 ⇒ `0x207`).
2. Walk `motorola/bathena/modem/image` to map the fpctzapp TZ app against the sibling `fpctzappfingerprint.mdt` devices (#2024's proof set).

## RULE 0 record (2026-11-20)

Exact query strings in the SEARCH/NO-PRIOR-ART comments on this issue. Key prior-art check: `a610_zap fpctzapp` (GitHub code search, adineo-cmd/* excluded) → 0 structural results; WHENCE `a610_zap`/`a630_sqe` naming verified at lines 7248/7259; mainline `adreno-610.0` verified in `sm6115.dtsi`.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata (sizes, md5s, paths, bintypes) plus published upstream trees and in-repo precedents.
