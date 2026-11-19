# OnePlus 6 (enchilada) — GPU firmware family

**Evidence class: census** (payload extracted, files hashed; no ISA decode this session).
Source: LineageOS 22.2 nightly 2026-11-11 for enchilada, payload partition `vendor`
(`/vendor/firmware`, mount root `/firmware`), extracted 2026-11-16; sha256 per file in
[tools/fleet/phase1_build.py](../../../../tools/fleet/phase1_build.py).

## Container layout

| file | bytes | magic | role |
|---|---|---|---|
| `a630_gmu.bin` | 32,768 | raw | Adreno 630 GMU microcode |
| `a630_sqe.fw` | 32,136 | raw | Adreno 630 SQE microcode |
| `a630_zap.b00` | 148 | elf32-le | zap shader MDT segment 0 |
| `a630_zap.b01` | 6,536 | elf32-le | zap MDT segment 1 |
| `a630_zap.b02` | 1,968 | elf32-le | zap MDT segment 2 |
| `a630_zap.mdt` | 6,684 | elf32-le | zap MDT ELF header |
| `a630_zap.elf` | 14,256 | elf32-le | zap monolithic ELF |

The MDT/bNN split matches the lab's FP6 boot-chain census pattern
([qualcomm-fp6/docs/bootchain-census.md](../../../research/qualcomm/docs/bootchain-census.md)):
one ELF header (`.mdt`) plus numbered segment payloads (`.bNN`), here for the
zap shader rather than the boot chain.

## Leverage link (top-20)

`a630_gmu.bin` 32,768 B and `a630_sqe.fw` 32,136 B are the identical
filename+size classes of recon.md top-20 entries #10 (a619_gmu, ×24) and
#18 (a630_sqe.fw, ×19). Whether the OnePlus 6 build's bytes equal the
fleet-shared md5s is checked by joining this census's sha256 against the
matrix md5 in a future pass (the upstream DB lists md5 only; conversion
requires payload access per device — open item).

## ISA/proof status

Not decoded this session. Public context: Adreno microcode ISA is
undocumented; SQE/GMU analysis exists nowhere public at decode level
(RULE 0 search 2026-11-16: `"bm2n" bin adsp firmware reverse engineering
qualcomm` and the GPU-adjacent results — linux-msm/hexagon-dsp-binaries,
TR25, SRLabs — cover DSP `.bXX` split bins, not GPU microcode).

## Interface facts

Consumer: mainline `drivers/gpu/drm/msm/adreno` loads `a630_zap` via
`zap_shader` and the GMU microcode via the GMU boot path
(`a6xx_gmu` code, public kernel — file names `a630_gmu.bin`/`a630_sqe.fw`
are its load table entries). No per-blob interface doc committed yet.

## Open questions

- sha256 ↔ fleet md5 join (needs the same LineageOS build family extracted
  for the 16-24 other a630/a619-carrying devices in the half)
- GMU/SQE microcode ISA (Hexagon-family micro-ISA, undocumented)
- zap shader ISA (RV32? a630-generation zap is Hexagon QDSP6 per public
  msm driver comments — unverified here)
