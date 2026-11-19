# implementations/adreno650-fleet — clean-room Adreno a650 fleet probe

A structural probe for the **a650 generation** of Qualcomm Adreno GPU firmware:
the GMU container `a650_gmu.bin` and the SQE microcode `a650_sqe.fw`, plus a
cross-generation mode that measures the format boundary across the whole
neighbouring a6xx fleet.

This extends `../../implementations/adreno-fleet/` (a619, the `gmu->legacy` raw
image) one generation forward. Where a619 asks "is there a header at all?" and
answers *no*, a650 is the first generation whose answer is *yes, and here is
what the header contains*.

**Clean-room statement.** Every claim in this directory rests on exactly two
sources: (a) public GPL-2.0 kernel sources, and (b) this work's own
measurements of payload bytes. No decompiler, disassembler, Ghidra/IDA project,
vendor datasheet, proprietary header or leaked document was consulted. The only
"decoding" performed is of ARMv7-M / Thumb-2 instruction encodings, which are
publicly specified in ARM DDI 0403 — each instruction is matched by an exact bit
mask, never by a remembered byte string. Every non-obvious fact below carries a
citation (`file:line`, fetched 2026-11-19) or is labelled `[OPEN]`.

No payload byte is committed. Fixtures are synthetic and regenerable; real
payloads live only in `/tmp/astro_u/a650/`.

## Files

| file | role |
|---|---|
| `a650_fleet_probe.py` | the probe. `python3 -I a650_fleet_probe.py <file> [--json out.json] [--brief] [--cross-gen F...]`. Exit 0 = clean, 1 = structural violation, 2 = unreadable |
| `make_fixture.py` | deterministic synthetic fixtures built from the established *shape* only. No payload byte is copied; every byte is generated here |
| `fixtures/*.bin` | 9 synthetic fixtures (3 format classes + 5 error paths + 1 unknown). **Not tracked** — regenerate with `python3 -I make_fixture.py` |
| `test_a650_fleet_probe.py` | unittest suite. **113 tests, all passing** |
| `a650-fleet-analysis.md` | the full analysis: the format boundary, the reset stub, the vector table, the SQE contract, the device correction, `[OPEN]` list |
| `../../blob-matrix/laptop/qualcomm-adreno-a650-fleet.md` | the content-level summary + the live-vs-carrying table |

## What the probe answers

It asks two questions, in this order, because the second depends on the first.

**Q1 — which container format is this file?** Mainline has two load paths,
selected by `gmu->legacy` (`a6xx_gmu.c:894`) and *not* by the filename:

- `legacy` → the file **is** the image. One size bound (`> 0x8000` rejects,
  `a6xx_gmu.c:896`), then `gmu_write_bulk()`. No parsing at all.
- otherwise → the file is a chain of
  `struct block_header {addr,size,type,value,data[]}` (`a6xx_gmu.c:857-863`,
  advanced by `NEXT_BLK`, `a6xx_gmu.c:874-875`).

The probe runs the documented walk **first** and reports honestly when it does
not fit. A negative answer is a finding, not a failure. Four classes are
distinguished: `container`, `raw-tcm`, `sqe`, `unknown`.

**Q2 — what is inside?** For the container class the probe rebuilds the loaded
address space and decodes, from the bytes themselves:

- the **reset stub** the Cortex-M3 core executes first (MSP, PSP, SCB->VTOR,
  stack paint, boot-counter addends, branch target),
- the **VTOR vector table** (16 architectural vectors + the external IRQ tail),
- the **DTCM+0xff8 handshake word** the driver polls to pick its magic
  (`a6xx_gmu.c:311-318`),
- the **SQE version dword** and the exact kernel branch it selects
  (`a6xx_gpu.c:985-1049`).

The probe reports **structure**. It does not and cannot recover what the
microcode computes.

## Usage

```
# the a650 GMU container, one-screen summary
python3 -I a650_fleet_probe.py a650_gmu.bin --brief

# full JSON report
python3 -I a650_fleet_probe.py a650_gmu.bin --json report.json

# the SQE, and the kernel verdict for that catalog filename
python3 -I a650_fleet_probe.py a650_sqe.fw --brief --sqe-name a650_sqe.fw

# measure the format boundary across the fleet
python3 -I a650_fleet_probe.py a650_gmu.bin --brief \
    --cross-gen a640_gmu.bin a619_gmu.bin a623_gmu.bin a660_gmu.bin
```

Real-payload result for `a650_gmu.bin` (md5-verified, exit 0, 0 errors):

```
file      : 41548 bytes  md5 a2b9504e3d1cb8686ae7fcca21a11e1a
kind      : gmu
format    : container
  basis   : block_header chain reaches EOF exactly at 0xa24c after 16 records
header    : present -- struct block_header (a6xx_gmu.c:857-863)
blocks    : 16 (7 payload, 9 manifest), walk exact-eof
dtcm base : 0x10004000 (block at 0x10004000 (a650-family map))
reset vec : 17 -> entry 0x10
stub      : cnt+msp+psp+vtor+paint+bw
            msp=0x10007f80 psp=0xdeadbeef vtor=0x00000200 reg=0xe000ed08
            paint 3968 B @ 0x10007000 with 0xaaaaaaaa
            transfers to 0x400
vector tbl: 0x200  word0=0x00000000 (unused (zero))
            64 IRQ entries, targets 0x00000579
fw init   : 0x10004ff8 = uncovered (0) -> legacy 0xbabeface, mask 0xffffffff
markers   : payload-tag 14, host-sentinel 1, fw-init 0
strings   : 448 run(s) >= the minimum length
diagnostics: 0 error, 0 warning, 10 info
```

The `strings` line uses the probe's default minimum of 4 characters. The REX
string-table census quoted below uses `--strings-min 10` (81 runs for a650),
because 4-character runs over Thumb code are overwhelmingly false positives.

## The format boundary is the loader, not the filename

Measured across eight files (all linux-firmware or md5-verified vendor copies):

| file | bytes | walk | class | `u32[0]` | `u32[1]` | vt@0x200 word0 |
|---|---|---|---|---|---|---|
| a619 | 32,768 | overflow @0x19 | raw-tcm | `00043f80` | `00000009` | `00043f80` (=SP) |
| a630 | 32,768 | overflow @0x19 | raw-tcm | `00043f80` | `00000009` | `00043f80` (=SP) |
| a640 | 37,680 | exact EOF, 7 rec | container | `00043f80` | `00000009` | `00000000` |
| **a650** | **41,548** | **exact EOF, 16 rec** | **container** | `10007f80` | `00000011` | `00000000` |
| a623 | 53,516 | exact EOF, 15 rec | container | `10007f80` | `00000105` | not loaded |
| a660 | 55,252 | exact EOF, 15 rec | container | `10007f80` | `00000105` | not loaded |
| a663 | 55,892 | exact EOF, 15 rec | container | `10007f80` | `00000105` | not loaded |
| gen70000 | 57,272 | exact EOF, 15 rec | container | `10007f80` | `00000105` | not loaded |

**Rule, with evidence:** every `ADRENO_6XX_GEN1` file is raw and every GEN2+
file is a container — the split is exactly `gmu->legacy`. Inside the container
class there is a **second** boundary at a650: a640 still carries a 32-bit-Thumb
ARMv7-M reset vector table at ITCM 0x0 (`u32[0]` = SP, `u32[1]` = odd reset) with
VTOR → `0x200`; a650 onward begins with a code image whose `u32[0]` is an MSP
literal, and from a660/a623 the 0x200 window is **not loaded at all**
(VTOR → `0x1000`).

## The three things a650 does that its predecessors do not

1. **A stack paint loop.** Before branching to `0x400` the prologue writes
   `0xaaaaaaaa` over `0x10007000..0x10007f80` (0xf80 B) — ending *exactly* at the
   initial SP. The container never writes the stack page; the prologue
   establishes it at runtime.
2. **A boot-counter bump.** The prologue does a read-modify-write on
   `0x10007fdc` twice, adding `1` then `2` — a boot/power-cycle counter kept in
   the DTCM tail block.
3. **A REX RTOS string table.** 81 printable runs ≥10 chars (a619 has **1**),
   naming the failing function in assert/abort paths: `REX Idle Task`,
   `HfiReadMsgPool`, `GmuPwrRequestPowerOn`, `EnterIdleState`, `RsccSendVoting`,
   `InvalidateDCache`, and ~20 `rex_*` scheduler calls. This is a debug-build
   symbol table present only from the container generation onward, and it is the
   highest-value single artifact here: it names the RTOS primitives, the HFI
   protocol layer, the IFPC power/idle machine and the RSCC voltage voting
   subsystem without any decompilation.

## The SQE contract, and the device copy that fails it

`adreno_fw_create_bo()` allocates `fw->size − 4` and copies from `&fw->data[4]`
(`adreno_gpu.c:644-656`), so **file dword 0 is a stripped prefix** and the
driver-visible version is **file dword 1**. `a6xx_ucode_check_version()` then
applies one of four branches (`a6xx_gpu.c:985-1049`):

| catalog name | branch | floor |
|---|---|---|
| `a630_sqe.fw` | patched nibble OR `>= 1.90` | `0x190` |
| `a650_sqe.fw` | `>= 0.95` | `0x095` |
| `a660_sqe.fw` | unconditional accept | — |
| `a702_sqe.fw` / a7xx / a8xx | early return `true` | — |

Measured, both directions:

| build | bytes | md5 | version dword | `v & 0xfff` | passes a650 |
|---|---|---|---|---|---|
| device fleet (DB md5) | 31,632 | `353e247b…` | `0x016dd093` | `0x093` (0.93) | **NO** |
| linux-firmware | 31,964 | `dc02e77a…` | `0x016dd112` | `0x112` (1.12) | YES |

**Finding:** every vendor tree examined ships an a650 SQE **below mainline's
minimum**. The failure path is fully traced: `a6xx_ucode_load()` returns
`-EPERM` (`a6xx_gpu.c:1077`) → `adreno_load_gpu()` returns NULL
(`adreno_device.c:96-100`) → the GPU never registers. A device carrying this
exact SQE therefore cannot bring up its GPU under mainline, and the fix is a
`>= 0.95` build, which linux-firmware has.

Cross-check that the SQE decode is right, independently of the kernel branch:
`WHENCE` declares an SQE version per file, and it decodes exactly as `%x.%02x`
of `(dword1 & 0xfff)` for all five SQE files checked — a650 `v1.12`, a630
`v2.07`, a660 `v1.12`, a730 `v1.81`, a740 `v1.81`. The GMU files carry **no**
version in the container: `a650_gmu.bin` dword 1 is `0x00000000`, and the driver
reads the GMU version from a register instead
(`gmu_read(gmu, REG_A6XX_GMU_CORE_FW_VERSION)`, `a6xx_gmu.c:933`). `WHENCE`'s
`qcom/a650_gmu.bin v2.1.8` is therefore *not* recoverable from the file, and the
`%x.%02x` rule is asserted for SQEs only.

## Fleet scope — 14 rows, 9 devices that actually load it

`a650_gmu.bin`, 41,548 B, md5 `a2b9504e3d1cb8686ae7fcca21a11e1a`. All 14
database rows share that md5. But `a6xx_catalog.c` names it in exactly **one**
entry — chip id `0x06050002`, `ADRENO_6XX_GEN3`, `.revn = 650`
(`a6xx_catalog.c:1052-1057`), the chip `dts_sm8250.dtsi:2935` binds as
`qcom,adreno-650.2`. A device *carrying* the file is not a device *running* it.

| verdict | count | evidence |
|---|---|---|
| **live** — SM8250 / kona, Adreno 650 | **9** | `TARGET_BOARD_PLATFORM := kona` in each device's inherited BoardConfig |
| SM6115 / bengal, Adreno 610 (`gta4l`, `gta4lwifi`) | 2 | `gta4l-common/BoardConfigCommon.mk`: `TARGET_BOARD_PLATFORM := bengal`, `TARGET_BOARD_PLATFORM_GPU := qcom-adreno610`; vendor tree also carries `a702_sqe.fw`/`a702_zap.mdt` |
| SM7250 / lito, Adreno 620 (`bramble`, `redfin`, `barbet`) | 3 | the DB's own `soc` column says `Qualcomm SM7250 Snapdragon 765G`; `redbull/BoardConfig-common.mk` says `lito`; mainline has **no** `revn = 620` catalog entry at all |

The two non-live classes are co-resident leftovers — a vendor firmware
partition is a superset of what any one SoC binds.

**The `pdx215` row is mislabelled, and the fix makes it live, not dead.** The DB
row reads `Xperia_1_II | sony/pdx215 | a650_gmu.bin`. Mainline says
`sm8250-sony-xperia-edo-pdx203.dts` is the Xperia 1 II (SM8250) and
`sm8350-sony-xperia-sagami-pdx215.dts` is the **Xperia 1 III** (SM8350), so the
codename looks wrong — but the *contents* settle it. All 21 files under the DB's
`sony/pdx215/vendor/firmware` path exist in the pre-split `sm8250-common` tree or
the pre-split `pdx203` directory, and the discriminating file
`touch_module_id_0x83.img` (169,224 B, md5 `279ca2f1…`) is **byte-identical** to
`pdx203`'s copy. The real `pdx215` (SM8350) split tree carries
`touch_module_id_0x28.img`, `a660_gmu.bin` and `a660_sqe.fw` — and **no
`a650_gmu.bin`**. So this row is a duplicate of the **Xperia 1 II / pdx203**
firmware set with the wrong codename in `db_path`, and `pdx203` is SM8250/kona.
The device is live; only the path label is wrong. `device-inventory.csv`
corroborates by listing `Xperia_1_II` twice, once as `pdx203` (SM8250) and once
as `pdx215` (soc blank).

The real `pdx215` (Xperia 1 III) is a separate, correctly-excluded case: it is
SM8350/lahaina/Adreno 660 and is not one of the 14 rows at all. Recorded as a
database attribution correction, not a payload finding — the md5 is identical to
the other 13 rows either way.

Full per-device table: `../../blob-matrix/laptop/qualcomm-adreno-a650-fleet.md`.

## RULE 0 — prior art (searched 2026-11-19)

Searched before writing anything, because a re-derivation that duplicates prior
public work is worthless:

| query | hits | verdict |
|---|---|---|
| `a650_fleet_probe` | 0 | no prior probe |
| `a6xx_gmu_fw_header` | 0 | the premise struct does not exist anywhere |
| `a650_gmu.bin` + `efbeadde` | 1 repo | `xVanTuring/UniXNU-pipa` |
| `a650_gmu.bin` + `block_header` | 1 repo | same |

The single hit is `xVanTuring/UniXNU-pipa` (`package/A650Gmu.c`,
`A650GmuTests.c`, `A650Gmu.h`). Read in full: it builds a **synthetic**
`0xefbeadde`-tagged container in a host unit test and consumes the
`0x10007fdc` DTCM handshake the way mainline does. It does **not** decode the
reset stub, the vector table, the manifest tiling, the stack paint, the boot
counter or the SQE version contract. That set is the delta claimed here, and it
is derived independently — this probe's decoder and that project's parser agree
on the block layout and on nothing else.

## Tests

```
cd implementations/adreno650-fleet
python3 -m unittest -v test_a650_fleet_probe     # 113 tests
```

Coverage, in the order the probe applies it: the RULE-0 source premise;
format classification **positive and negative** (every near-miss rejected); the
vector-table decode including the a650-specific "word0 is not an SP" shape; the
reset-stub decode; SQE version extraction and the per-arm kernel verdict in both
directions; the cross-generation table; malformed and truncated input (including
every prefix of a container, a flipped Thumb bit, and an out-of-image reset
vector); the CLI and JSON contracts with exit codes; and fixture determinism
plus the no-proprietary-bytes guarantee.

The suite regenerates its own fixtures, so it passes from a clean checkout with
no `fixtures/*.bin` present.

## Why this is worth doing

- The container format is **fully specified** by mainline plus a file that walks
  to EOF exactly. A free loader already exists (`msm`); what is missing is not
  the format but the microcode.
- The a650 string table names the RTOS/HFI/power/clock subsystems, which is the
  closest thing to documentation this artifact has. It tells a reimplementation
  *what services exist* without any code interpretation.
- The SQE floor is a hard, checkable gate: any free stack that ships the device
  copy will silently fail to register a GPU. That is an actionable finding for
  every one of the 9 live devices.

## Honest boundaries

- The probe decodes ARMv7-M **architectural** encodings only, and only the
  small alphabet a reset prologue uses. It is not a disassembler for the body.
- What the microcode *computes* is not recovered, here or by any clean-room
  means short of running it.
- Manifest record semantics are `[OPEN]`: the kernel skips `size == 0` records
  entirely (`a6xx_gmu.c:909-910`), so `value` is never read by Linux. The
  `(addr, value)` pairs tile the loader windows exactly, but only 3 of 11
  a660-family manifests match a payload block exactly — **a650 matches 0 of 9**.
  The manifest is a window map, not a block index.
- The naive `>= 8`-char string filter also catches machine-code false positives
  (`g2F)F F'`). The string sample is a sample, not a symbol table.
- The fixture magnitudes (41,548 / 37,680 / 32,768 B) mirror the fleet, but the
  contents are synthetic by construction: different fill constant, different
  counter magic, different branch target and different build id from anything
  measured, so no fixture byte can be mistaken for a payload byte.
