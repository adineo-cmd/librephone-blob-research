# implementations/adreno-fleet — clean-room Adreno GMU microcode probe

A structural probe for Qualcomm Adreno **GMU** (GPU Management Unit) microcode
images — the `*_gmu.bin` files shipped in `vendor/firmware/` on every Adreno
device. The component's fleet scope is the top-20 leverage blob
`a619_gmu.bin` (recon.md row 10): **26 DB rows share the bytes; 13 devices
actually load them** (the distinction is a finding — see §"Fleet scope").

The probe answers the question the metadata matrix could not: *what is actually
inside the 32 KB* — and it answers a second, sharper one first, because the
answer changes everything downstream: **does mainline's documented firmware
header apply to this file at all?**

It does not. `a619_gmu.bin` carries **no container header of any kind**. It is
a flat ARMv7-M memory image — ITCM in the first half, DTCM in the second — and
its first word is not a magic, a size or a version, but the **initial stack
pointer**. The driver that loads it never parses it (`a6xx_gmu.c:894-904`).

**Ground truth (fetched 2026-11-18 from torvalds/linux master + linux-firmware):**

| what | where | what it settles |
|---|---|---|
| `struct block_header` (`addr,size,type,value,data[]`) | `a6xx_gmu.c:857-863` | the only firmware *container* struct mainline has |
| non-legacy load path (walk the block chain) | `a6xx_gmu.c:906-930` | how a640/a650/a660/a623/a663 are loaded |
| `gmu->legacy` raw path (bulk-write whole file, cap 0x8000) | `a6xx_gmu.c:894-904` | how a619/a618/a630 **are** loaded |
| `gmu->legacy = true` for `ADRENO_6XX_GEN1` | `a6xx_gmu.c:2412-2414` | a619 is in that class (`a6xx_catalog.c`, `.family = ADRENO_6XX_GEN1`) |
| `GMU_CM3_ITCM_START` / `GMU_CM3_DTCM_START` exactly SZ_16K apart | `a6xx_gmu.xml:45-46` | why a flat 32 KiB file is a *contiguous* ITCM+DTCM dump |
| `GMU_CORE_FW_VERSION` MAJOR/MINOR/STEP | `a6xx_gmu.xml:55-58` | the printed "GMU firmware vX.Y.Z" is a **register**, not a file field |
| DTCM probe at `DTCM_START+0xff8`, magic `0xbabeface` | `a6xx_gmu.c:311-318` | corroborates the image's own `0xbabeface` constant |

## Files

| file | role |
|---|---|
| `gmu_probe.py` | the probe: tries the mainline `block_header` walk **first**, then the raw ITCM+DTCM layout. CLI `python3 -I gmu_probe.py <file> [--json out.json] [--brief]`; exit 1 on structural violations |
| `make_fixture.py` | deterministic synthetic fixtures from the established layout (no proprietary bytes; every byte generated) |
| `fixtures/*.bin` | synthetic fixtures — 6 files, both branches + 4 error paths. **`*.bin` is gitignored**: regenerate with `python3 -I make_fixture.py` |
| `test_gmu_probe.py` | unittest suite: `python3 -m unittest -v test_gmu_probe` — **62 tests, all passing** |
| `gmu-analysis.md` | the analysis: per-byte-range findings, the public-header verdict, entropy map, ISA hypothesis, [OPEN] list |

## Fleet scope (verified against `coverage-matrix.csv`, 2026-11-18)

`a619_gmu.bin`, 32,768 B, md5 `9e23c52057bb573dee9ba31f1fdba4fa`.

| quantity | value | how verified |
|---|---|---|
| rows named `a619_gmu.bin` | **24** | `grep -c ",a619_gmu.bin,"` |
| rows named `a618_gmu.bin`, **same md5** | **2** | Samsung Galaxy A71 (a71), Xiaomi Mi A3 (laurel_sprout) |
| **rows sharing this md5** | **26** | `grep -c 9e23c520…` → 26; 24 + 2 aliases |
| laptop-half devices carrying this md5 | **7** | the 5 below + a71 + laurel_sprout |
| **devices that actually load it** | **13** | see below — 15 co-resident copies are never loaded |

The filename alias is a real finding, not a bookkeeping quirk: the *same bytes*
ship as `a618_gmu.bin` on two devices and as `a619_gmu.bin` on twenty-four.
Adreno 618 and 619 are both `ADRENO_6XX_GEN1` (`adreno_is_a615_family()` groups
them explicitly, `adreno_gpu.h:512-515`), so one microcode image serves both —
consistent with mainline's own model.

**Leverage is 13 devices, not 26.** A device *carrying* the file is not a device
*running* it: mainline loads `a619_gmu.bin` only for `revn = 619`
(`a6xx_catalog.c:872-876, 898-901, 920-925`), so on an Adreno 650/660 device the
`a619` copy is a co-resident leftover. 11 devices are 619-class SoCs, 2
(`Edge_20`, `Edge_2021`) have no competing GMU blob, and 11 are co-resident
`a650`/`a660` devices that never load it. Full per-device table:
`../../blob-matrix/laptop/qualcomm-adreno-gmu-content.md` §5.

Laptop-half cluster detail (`sharing-clusters.csv`): md5 cluster of **7**
devices = the 5 laptop-half + `a71` + `laurel_sprout`, i.e. the two alias rows.

## Usage

```
python3 -I gmu_probe.py a619_gmu.bin --brief
python3 -I gmu_probe.py a619_gmu.bin --json report.json
python3 -I gmu_probe.py a640_gmu.bin --brief         # container branch
```

Real-payload result for `a619_gmu.bin` (md5-verified, exit 0, 0 errors):

```
format    : raw-tcm-image  [measured-and-cross-checked]
header    : ABSENT — flat memory image; u32[0] is the ARMv7-M initial SP
initial SP: 0x00043f80 (DTCM=True, == DTCM top 0x44000 - 0x80)
reset vec : 0x00000009
vector tbl: 0x200, 16 architectural vectors + 64 external IRQs (1 target)
dtcm table: 50 x {addr,value} at 0x44d8 (all values zero)
region tbl: 8 {start,end} address pairs at 0x3ea4
entropy   : whole 3.87 — ITCM 6.34 (17% zero), DTCM 0.15 (99% zero)
```

## Why this is worth doing

- **13 live devices from one md5.** Per-file RE (not per-device RE) is the
  multiplier. The naive count is 26 DB rows; the correction is that only 13 of
  those devices actually load the image (§"Fleet scope"), and both numbers
  matter — 26 for dedup, 13 for impact.
- **The header question is settled, negatively and usefully.** Anyone building
  a free loader now knows a619 needs the *raw bulk-write* path and a
  ITCM+DTCM image, not a parsed container. That is a smaller job than the
  container family, and it is the same job for a618.
- **The layout is cross-checked three ways**, not asserted: the register map
  (TCMs exactly SZ_16K apart), the image's own startup stub (which sets VTOR
  and loads the SP the vector table repeats), and the driver's `0xbabeface`
  init magic (which appears twice in the microcode's own code).
- **The sibling generation is scoped.** The other linux-firmware Adreno GMU
  blobs use the *container* format; a619/a630 do not. That boundary is now
  measured rather than guessed.

## Honest boundaries

The probe reports **structure only**. It does not decode a single microcode
function, and it makes no claim about what the firmware computes. The Thumb
census is a *census*, not a disassembly. Full [OPEN] list in
`gmu-analysis.md` §8.

Not legal advice, not a replacement implementation. Regulatory/legal hurdles
for actually replacing GPU firmware: `../../upstream-contribution/radio-regulatory-hurdles.md`
(same class of question — signed/attested firmware loading).
