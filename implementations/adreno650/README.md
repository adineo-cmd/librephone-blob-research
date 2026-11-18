# adreno650 — the Adreno 650 GMU/SQE GPU firmware, parsed

`a650_gmu.bin` + `a650_sqe.fw` (8 laptop-half devices, one md5 each),
parsed per the mainline-documented structures only
(`drivers/gpu/drm/msm/adreno/a6xx_gmu.c` block_header chain,
`adreno_gpu.c` 4-byte SQE strip, `a6xx_gpu.c` version check), md5-verified
against the upstream database, with the a619 one-generation-back delta.

## Contents

- `a650-gmu-analysis.md` — the analysis: block table (9 manifest + 7
  DEADBEEF-tagged payload blocks), region map vs the kernel's BO bases,
  SQE version-dword findings (device fleet build v0.93 FAILS mainline's
  ≥0.95 floor; linux-firmware v1.12 passes), a619 raw-0x8000-format delta,
  md5 table, route log.
- `a650_fw.py` — clean-room structural parser (GMU block chain incl.
  manifest/payload classes + region classification; SQE version
  semantics). Inspector only — no disassembly.
- `make_fixture.py` + `test_a650_fw.py` — synthetic fixtures from the
  documented structures; run `python3 -I test_a650_fw.py`.

## md5 status (2026-11-18)

a650_gmu.bin (`a2b9504e…`) **MATCH from two independent sources**
(linux-firmware `qcom/` AND the Sony sm8250-common device tree — the
device copy and the linux-firmware copy are byte-identical).
a650_sqe.fw device build (`353e247b…`) **MATCH** (Sony tree); the
linux-firmware copy is a different build (`dc02e77a…`, v1.12) — labeled
NOT-database-identical in the analysis. a619_gmu.bin (`9e23c520…`, FP4
copy) **MATCH** for the 7-device a619 laptop-half fleet.
