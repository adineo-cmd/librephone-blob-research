# Qualcomm Adreno `a650_gmu.bin` + `a650_sqe.fw` — content-level RE: the first container generation, and the SQE build that cannot bring up a GPU

Analysis date: 2026-11-19. Evidence class: **MEASURED PAYLOADS** — every number
below is computed from bytes on disk or quoted from public GPL kernel source.
Nothing is copied from a manifest except the explicitly-labelled DB row counts,
which are re-derived.

Primary payload: `a650_gmu.bin`, **41,548 B**, md5
`a2b9504e3d1cb8686ae7fcca21a11e1a`, sha256 re-derived this session. Secondary:
`a650_sqe.fw`, two builds (31,632 B device / 31,964 B linux-firmware). Bytes live
only in `/tmp/astro_u/a650/`; no proprietary content is committed.

Companion documents:

| document | owns |
|---|---|
| **`qualcomm-adreno-gmu.md`** (this directory) | the a619 metadata matrix (5 laptop-half devices, md5/size) |
| **`qualcomm-adreno-gmu-content.md`** (this directory) | a619 content RE: no header, raw ITCM+DTCM, the 13-of-26 occupancy correction |
| **`../../implementations/adreno650-fleet/a650-fleet-analysis.md`** | the full a650 analysis: block plan, reset-stub decode, vector table, SQE contract, `[OPEN]` list |
| **`../../implementations/adreno650/a650-gmu-analysis.md`** | the a650 first pass (block table, manifest tiling) — verified correct, extended here |
| `../../implementations/adreno650-fleet/a650_fleet_probe.py` | the probe. `python3 -I a650_fleet_probe.py <file> --brief` |
| `../../implementations/adreno650-fleet/README.md` | usage, fixture/test instructions, RULE-0 delineation |

This file owns the **content-level summary**, the **live-vs-carrying table**
(§4, which corrects the raw DB row count) and the **`pdx215` path-label
correction** (§4.1). Read §4 even if you read nothing else.

Labels used throughout: **[S]** quoted from public GPL source (file:line, fetched
2026-11-19) · **[M]** my own measurement of payload bytes · **[OPEN]** not
established, gap named.

---

## 1. Headline: a650 is the first generation whose file *is* a container

a619 answers "is there a header at all?" with **no** — it is a flat 32 KiB
ITCM+DTCM image the driver bulk-writes without parsing (`gmu->legacy`,
`a6xx_gmu.c:894-904`). a650 answers **yes**, and the header is fully specified by
mainline [S]:

```c
/* drivers/gpu/drm/msm/adreno/a6xx_gmu.c:857-863, 874-875 */
struct block_header {
	u32 addr;
	u32 size;
	u32 type;
	u32 value;
	u32 data[];
};
#define NEXT_BLK(blk) ((const struct block_header *) \
	((const char *)(blk) + sizeof(*(blk)) + (blk)->size))
```

`a650_gmu.bin` walks this chain and lands on **exact EOF at `0xa24c`** after 16
records — no slack, no padding, no overrun [M]. That exactness is the proof the
parse is right: a wrong field assignment desynchronises the walk immediately.

| | a619 (GEN1) | **a650 (GEN3-class)** |
|---|---|---|
| format | raw 0x8000 image | 16-record container |
| loader | `gmu->legacy` bulk write, no parse | block chain, `a6xx_gmu.c:906-930` |
| DTCM base | `0x00040000` | **`0x10004000`** |
| windows | ITCM + DTCM only | ITCM + icache + DTCM + dummy BO |
| reset entry | ITCM `0x08` | ITCM **`0x10`** |
| stack page pre-written? | n/a (flat image) | **no** — painted at runtime |
| string table | 1 run ≥10 chars | **81** |
| linux-firmware | absent | ships both files |

**The format boundary is the load path, not the filename** [S `a6xx_gmu.c:2412-2414`
sets `gmu->legacy` for `ADRENO_6XX_GEN1`]. Measured across the fleet, that
predicate is exactly the observed split: a619 and a630 (both GEN1, both 32,768 B)
fail the walk identically; a640 onward all walk to exact EOF [M].

## 2. The block plan — 9 manifest + 7 payload, and one refuted hypothesis

The 16 records split cleanly [M]:

- **9 zero-size manifest records** (`type` 1, one `type` 7). The kernel skips
  these wholesale [S `a6xx_gmu.c:909-910`: `if (blk->size == 0) continue;`], so
  their `value` field is **never read by Linux**.
- **7 payload blocks**, every one tagged `type == value == 0xEFBEADDE` — on disk
  `DE AD BE EF`, a byte-reversed `DEADBEEF`. This is the container's payload tag,
  not a terminal sentinel [M].

| payload | addr | size | region | entropy |
|---|---|---|---|---|
| p0 | `0x00000000` | 192 | ITCM | 5.06 |
| p1 | `0x00000200` | 320 | ITCM | 1.74 |
| p2 | `0x00000400` | 14,092 | ITCM | 6.86 |
| p3 | `0x00004000` | 21,968 | icache | 6.78 |
| p4 | `0x00157000` | 920 | icache | 2.50 |
| p5 | `0x10004000` | 3,776 | DTCM | 0.52 |
| p6 | `0x10007fdc` | 24 | DTCM (tail) | 2.11 |

Totals: ITCM 14,604 B (≤ 16K) · icache 22,888 B · DTCM 3,800 B. Whole-file
entropy 6.43 bits/byte, 19.1 % zero.

### 2.1 The manifest is a window map, not a block index — established negatively

The 9 manifest `(addr, value)` pairs tile the loader's own windows exactly, which
makes it tempting to read them as an index of the payload blocks [M]:

| manifest | addr | value | mainline counterpart |
|---|---|---|---|
| m0–m2 | `0x0`, `0x200`, `0x400` | `0x200`, `0x200`, `0x3c00` | ITCM `0x0..0x4000` tiled |
| m3 | `0x4000` | `0x8000` | icache base (`a6xx_gmu.c:2393`) |
| m4, m5 | `0x10004000`, `0x10007fdc` | `0x3fe0`, `0x24` | DTCM `0x10004000..0x10008000` |
| m6, m7 | `0x144000`, `0x157000` | `0x13000`, `0x9000` | icache sub-windows |
| m8 | `0x60000000` (type 7) | `0x1000` | dummy page BO (`a6xx_gmu.c:2384`) |

**That hypothesis is refuted by measurement** [M]: only **3 of 11** a660-family
manifests have a pair that exactly matches a payload block, and **a650 matches 0
of 9**. The manifest is a *window map* the chip consumes — not an index of what
the kernel copies. Recording this as a negative result is the point: a
reimplementation that built a block-index table from these records would be
building something the hardware does not use.

## 3. What a650 does that its predecessors do not

Three firsts, all measured from the bytes [M], all decoded with exact ARMv7-M
mask tests (ARM DDI 0403) rather than pattern matching:

**3.1 A stack paint loop.** Before branching to `0x400`, the prologue writes
`0xaaaaaaaa` over `0x10007000..0x10007f80` (0xf80 B) — ending *exactly* at the
initial SP `0x10007f80` (= DTCM top `0x10008000` − `0x80`). The 0xaaaaaaaa pattern
is a stack-high-water detector: bytes the stack never reaches stay painted. The
container **never writes the stack page** — it falls in a gap between the DTCM
blocks — and that is correct: a firmware shipping pre-filled stack bytes would be
initialising a region the core overwrites on its first push.

**3.2 A boot counter.** The prologue does a read-modify-write on `0x10007fdc`
twice, adding `1` then `2`, each as `(v << 8) + n`. Two sequential bumps in one
prologue means this is a stage-tagged sequence counter, not a single boot flag.
The consumer is `[OPEN]`.

**3.3 A REX RTOS string table.** 81 printable runs ≥10 chars, against **1** in
a619 and a630 [M]. The jump arrives with the container generation (a640 has 62).
These are assert/abort format strings that **name the failing function**:

| subsystem | strings |
|---|---|
| REX RTOS scheduler | `REX Idle Task`, `Trying to create more than REX_MAX_TASKS`, `rex_leave_crit_sect_internals() Failure: save_ptr == NULL`, ~20 more `rex_*` |
| signals / heap | `SIGABRT: Abnormal termination`, `SIGRTMEM: Out of heap memory`, `: Heap memory corrupted` |
| event map | `EventMapAdd/Remove`, `RegisterFuncForEvent`, `AllocEventPool`, `RecordEvent`, `PopTaskQueue` |
| cache / memory | `InvalidateDCache`, `InvalidateICache`, `GmuDCacheOp`, `FlushWriteBuffer`, `InvalidateReadBuffer` |
| HFI protocol | `HfiReadMsgPool`, `HfiGetMemDescriptor`, `HfiValueHandler`, `HandleHfiCommand`, `HfiMsgToHost`, `HfiQueueTryRead` |
| power / idle (IFPC) | `GmuPwrStart`, `GmuPwrRequestPowerOn`, `GmuPwrGxBwVote`, `beginHmPwrCollapse`, `EnterIdleState`, `ExitIdleState`, `PwrIdleStateGetStateIdx` |
| clock / voltage (RSCC) | `ResMgrReqClkThrot`, `RsccSetVoltageVoteData`, `RsccSendVoting`, `HAL_clk_ValidateRegTimeout` |

This is the highest-value artifact in the file: it names the RTOS primitives, the
HFI layer, the IFPC idle-state machine and the RSCC voltage path **without any
code interpretation**. Caveat: a naive `>= 8`-char ASCII filter over 16-bit Thumb
also catches machine-code false positives (`` `pGpG ``, `g2F)F F'`); the sample is
a sample, not a symbol table.

## 4. Occupancy correction — 14 DB rows, **9 devices that actually load it**

**This corrects the leverage implied by the raw row count.** All **14** DB rows
named `a650_gmu.bin` share md5 `a2b9504e…` [M, re-derived from
`coverage-matrix.csv`]. But mainline names the file in exactly **one** catalog
entry [S `a6xx_catalog.c:1052-1057`]:

```c
	.chip_ids = ADRENO_CHIP_IDS(0x06050002),
	.family = ADRENO_6XX_GEN3,
	.revn = 650,
	.fw = { [ADRENO_FW_SQE] = "a650_sqe.fw",
	        [ADRENO_FW_GMU] = "a650_gmu.bin" },
```

Chip id `0x06050002` is what `find_chipid()` computes from `"qcom,adreno-650.2"`
[S `adreno_device.c:142-170`], the compatible `dts_sm8250.dtsi:2935` binds. So a
device *carrying* the file is not a device *loading* it.

| class | devices | platform (verified) | verdict |
|---|---|---|---|
| **Adreno 650 / SM8250 `kona`** | `instantnoodle`, `instantnoodlep`, `kebab`, `lemonades`, `gts7l`, `gts7lwifi`, `r8q`, `pdx206`, `Xperia_1_II` | `TARGET_BOARD_PLATFORM := kona` | **live — 9** |
| Adreno 610 / SM6115 `bengal` | `gta4l`, `gta4lwifi` | `gta4l-common`: `TARGET_BOARD_PLATFORM := bengal`, `TARGET_BOARD_PLATFORM_GPU := qcom-adreno610` | not loaded |
| Adreno 620 / SM7250 `lito` | `Pixel_4A_5G` (bramble), `Pixel_5` (redfin), `Pixel_5A` (barbet) | the DB's own `soc` column: `Qualcomm SM7250 Snapdragon 765G`; `redbull/BoardConfig-common.mk`: `lito` | not loaded |
| **total** | **14** | — | **9 live** |

The five non-live are **co-resident leftovers** — a vendor firmware partition is
a superset of what one SoC binds. Both non-live Android classes corroborate
independently: `gta4l` also ships `a702_sqe.fw` / `a702_zap.mdt` (the a702 GMU
wrapper, `sm6115.dtsi:1811`), and the three Pixels carry `a619_gmu.bin` +
`a630_sqe.fw` + `a650_sqe.fw` alongside — a whole family of GMU blobs for one GPU.

**So: one RE pass informs 9 devices, not 14.** The `14` remains correct as "how
many DB rows share these exact bytes" (the right number for dedup and bandwidth
accounting); it is wrong as "how many devices run this firmware". Both numbers
are recorded because the distinction is the finding.

### 4.1 The `pdx215` row is mislabelled — and the fix makes it **live**, not dead

The DB row reads `Xperia_1_II | sony/pdx215 | a650_gmu.bin`. The codename is
wrong, and the *contents* identify the real device:

1. **Mainline DTS.** `sm8250-sony-xperia-edo-pdx203.dts` is the Xperia 1 II
   (`model = "Sony Xperia 1 II"`, `compatible = "sony,pdx203-generic"`, SM8250);
   `sm8350-sony-xperia-sagami-pdx215.dts` is the **Xperia 1 III** (SM8350). So
   `Xperia_1_II | pdx215` is internally inconsistent on its face.
2. **Contents match pdx203.** All 21 files under the DB's
   `sony/pdx215/vendor/firmware` path exist in the pre-split `sm8250-common`
   tree or the pre-split `pdx203` directory. The discriminating file is
   `touch_module_id_0x83.img` — the DB lists it at 169,224 B / md5
   `279ca2f166d1c051a86f6dbc4165e937`, and `proprietary_vendor_sony_pdx203`
   carries a **byte-identical** copy. The genuine `pdx215` split tree carries
   `touch_module_id_0x28.img` instead.
3. **The real `pdx215` does not carry this blob.** Its split vendor tree has
   `a619_gmu.bin`, `a630_sqe.fw`, `a660_gmu.bin`, `a660_sqe.fw` — and **no
   `a650_gmu.bin`** — on `lineage-22.1`, `22.2` and `24.0`, and its
   `proprietary-files.txt` agrees. It inherits `sm8350-common`
   (`TARGET_BOARD_PLATFORM := lahaina`) → SM8350 → Adreno 660.
4. **`pdx203` is SM8250/kona.** Its `BoardConfig.mk` inherits `sm8250-common`,
   whose `BoardConfigCommon.mk` sets `TARGET_BOARD_PLATFORM := kona`.

So the row is a duplicate of the **Xperia 1 II / pdx203** firmware set carrying
the wrong codename in `db_path`. `device-inventory.csv` already lists
`Xperia_1_II` twice — once as `pdx203` (SM8250) and once as `pdx215` (soc blank)
— which is how the two got crossed.

**Consequence, and a correction to this document's own earlier draft.** I first
counted this row as a dead SM8350/Adreno-660 leftover, giving 8 live. That was
wrong: the device behind the row is SM8250/kona, so it is **live**, and the
count is **9**. The correction *raises* the impact of the SQE finding rather than
lowering it. The md5 is byte-identical to the other 13 rows either way, so this
stays a **database attribution correction, not a payload finding** — and the
action is to relabel the row, not to drop it.

Note this also refines the a619 sibling analysis: `qualcomm-adreno-gmu-content.md`
§5.1 lists `pdx215` as carrying `a650_gmu.bin` (taking the DB at face value). The
vendor-tree evidence says the block is pdx203's, and that the genuine `pdx215`
carries `a660_gmu.bin` instead. The a619 conclusion for that device — "not
loaded, co-resident" — is unchanged; only the identity of the co-resident blob
differs.

## 5. The SQE gate — the device copy cannot bring up a GPU

### 5.1 The strip and the version field

`adreno_fw_create_bo()` allocates `fw->size − 4` and copies from `&fw->data[4]`
[S `adreno_gpu.c:644-656`], so **file dword 0 is a stripped prefix** and the
driver's `buf[0]` is **file dword 1**. In all 15 builds examined, file dword 0 is
`0x00000000`. What the prefix *means* is `[OPEN]`.

### 5.2 Four branches, one field asymmetry

[S `a6xx_gpu.c:985-1049`]:

| catalog name | branch | floor |
|---|---|---|
| `a630_sqe.fw` | patched nibble OR `>= 1.90` | `0x190` |
| **`a650_sqe.fw`** | **`>= 0.95`** | **`0x095`** |
| `a660_sqe.fw` | unconditional accept | — |
| `a702_sqe.fw` / a7xx / a8xx | early return `true` | — |

The asymmetry worth flagging: the a630 patched test reads `buf[2]` — the **BO's**
dword 2, i.e. **file dword 3** — while the version is `buf[0] & 0xfff`, i.e. file
dword 1. Two different dwords, one `if`. The probe reports them separately.

### 5.3 Measured, both directions

| build | bytes | md5 | file dword 1 | `v & 0xfff` | text | passes a650 |
|---|---|---|---|---|---|---|
| device fleet (DB md5) | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` | `0x016dd093` | `0x093` | 0.93 | **NO** |
| linux-firmware | 31,964 | `dc02e77a04b97b985281d36ab159c130` | `0x016dd112` | `0x112` | 1.12 | YES |

**Every vendor tree examined ships an a650 SQE below mainline's floor.** The
consequence is fully traceable in public source [S]:

```
a6xx_ucode_load()      returns -EPERM      (a6xx_gpu.c:1077)
  -> adreno_load_gpu() returns NULL        (adreno_device.c:96-100)
    -> the GPU never registers
```

A device carrying this exact SQE cannot bring up its GPU under mainline, and the
two builds share only 18 % of same-offset bytes — genuinely different microcode,
not a repack. The fix is a `>= 0.95` build, which linux-firmware has had for
years.

### 5.4 An independent cross-check that the decode is right

`WHENCE` declares a version per file. For the **SQE** files it decodes exactly as
`%x.%02x` of `(dword1 & 0xfff)` — all five checked [M]:

| file | WHENCE | decoded |
|---|---|---|
| `a650_sqe.fw` | `v1.12` | 1.12 ✓ |
| `a660_sqe.fw` | `v1.12` | 1.12 ✓ |
| `a730_sqe.fw` | `v1.81` | 1.81 ✓ |
| `a740_sqe.fw` | `v1.81` | 1.81 ✓ |
| `a630_sqe.fw` | `v2.07` | 1.97 device / 2.07 linux-fw (WHENCE tracks the linux-fw build) |

The **GMU** files carry no such field: `a650_gmu.bin` dword 1 is `0x00000000`,
which a container *must* keep zero because dword 1 is the first block header's
`size`. The driver reads the GMU version from a register instead
(`gmu_read(gmu, REG_A6XX_GMU_CORE_FW_VERSION)`, [S `a6xx_gmu.c:933-937`]), so
`WHENCE`'s `qcom/a650_gmu.bin v2.1.8` is a release label, not a blob field.

A version field reproducing the vendor's own declared string across five
unrelated SQE files is not a coincidence, and it validates the whole
"read dword 1 → mask `0xfff` → format major.minor" chain without depending on it.

## 6. The vector table at `0x200` — word0 is *not* a stack pointer

80 words: 16 architectural entries then 64 external interrupts [M].

| index | vector | value |
|---|---|---|
| 0 | Initial SP slot | `0x00000000` |
| 1 | Reset | `0x00000011` |
| 2 | NMI | `0x000004d1` |
| 3–6 | HardFault, MemManage, BusFault, UsageFault | `0x000004a1` |
| 11 | SVCall | `0x000035a1` |
| 14 | PendSV | `0x00000509` |
| 15 | SysTick | `0x000035a3` |
| 16–79 | 64 external IRQs | `0x00000579` |

**word0 is zero, and that is the a650 discriminator.** A Cortex-M vector table
conventionally repeats the initial SP at word 0 — a619 and a640 both do. From
a650 the SP comes from the prologue's own literal, so `0x200` is a pure handler
table. The probe names the role (`initial-SP copy` / `unused (zero)`) instead of
assuming, because assuming would silently mis-read a640 and a650 as the same
shape.

Two independent self-consistency checks pass [M]: every non-zero handler is odd
(Thumb) **and** every one resolves into loaded code. All 64 external interrupts
collapse onto a **single** handler — the microcode polls rather than dispatching
per-IRQ.

From a660/a623/a663 the `0x200` window is **not loaded at all** (VTOR → `0x1000`),
so the probe reports `vector_table_absent` rather than inventing one out of
zero-fill.

## 7. Provenance and md5 verification (2026-11-19)

| file | bytes | md5 | status | source |
|---|---|---|---|---|
| `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` | **MATCH** DB | linux-firmware `qcom/a650_gmu.bin`; byte-identical in 5 vendor trees |
| `a650_sqe.fw` (device) | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` | **MATCH** DB | oneplus/samsung/sony/xiaomi vendor trees; **not** in linux-firmware |
| `a650_sqe.fw` (linux-fw) | 31,964 | `dc02e77a04b97b985281d36ab159c130` | not in DB | linux-firmware `qcom/a650_sqe.fw` |

`WHENCE` records `qcom/a650_gmu.bin v2.1.8` and `qcom/a650_sqe.fw v1.12`. Only
the SQE version is a field in the blob (`%x.%02x` of dword 1 & `0xfff`); the GMU
label is a release tag, and the driver reads the GMU version from a register
after start (`a6xx_gmu.c:933`).

## 8. What this buys a free reimplementation

- **The container format is fully specified** by mainline plus a file that walks
  to EOF exactly. A free loader already exists (`msm`); what is missing is the
  microcode, not the format.
- **Three reset-prologue shapes are pinned** (`a640` / `a650` / `a660`) and each
  is decoded into the architectural facts a reimplementation must reproduce:
  where the stack is, where VTOR points, whether the stack page is pre-written,
  whether a boot counter is maintained.
- **The SQE gate is a hard, checkable contract.** Any free stack shipping the
  device copy fails `a6xx_ucode_load()` with `-EPERM` and registers no GPU. A
  `>= 0.95` build is required. That single fact is actionable for all 9 live
  devices.
- **The string table names the services** — REX, HFI, IFPC idle states, RSCC
  voting, the RSC/clock HAL — so a reimplementation knows what it must provide
  without any code having been decompiled.
- **The manifest is a window map, not an index** — established negatively, which
  saves a reimplementation from building a table the chip does not use.

## 9. `[OPEN]`

1. **Manifest semantics.** The pairs tile the windows exactly, but the kernel
   never reads `value` [S `a6xx_gmu.c:909-910`]. Only the chip consumes them; the
   "names a payload block" reading is *refuted* for a650 (0 of 9).
2. **The stripped SQE dword 0.** Zero in all 15 builds; semantic unknown, and not
   a size (the BO is `size − 4` regardless).
3. **The `0xdeadbeef` PSP sentinel's purpose.** It marks PSP deliberately invalid
   on entry; whether an exception handler checks it is not established.
4. **The boot-counter consumer.** `(v << 8) + n`, bumped `+1` then `+2`; the
   reader is unidentified.
5. **What the microcode computes.** Out of scope for any clean-room structural
   method.
6. **`pdx215` path label** (§4.1) — the row's contents are pdx203's; only the
   `db_path` codename is wrong, and the device is live. Resolve by relabelling
   the row.
