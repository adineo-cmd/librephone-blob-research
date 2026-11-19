# a650 fleet analysis — the a650 GMU container, the SQE version gate, and the
# format boundary one generation forward of a619

Analysis date: 2026-11-19. Evidence class: **MEASURED PAYLOADS** — every number
below is computed from bytes on disk or quoted from public GPL kernel source.
Nothing is copied from a manifest except explicitly-labelled database row counts,
which are re-derived.

Primary payload: `a650_gmu.bin`, **41,548 B**, md5
`a2b9504e3d1cb8686ae7fcca21a11e1a`. Secondary: `a650_sqe.fw`, two builds
(31,632 B device / 31,964 B linux-firmware). Bytes live only in
`/tmp/astro_u/a650/`; nothing proprietary is committed.

Companion documents:

| document | owns |
|---|---|
| **`README.md`** (this directory) | usage, fleet scope, test instructions, RULE-0 delineation |
| **`../../implementations/adreno650/a650-gmu-analysis.md`** | the *first pass*: the block table, the manifest tiling, the SQE strip. Verified correct — this file extends it, does not repeat it |
| **`../../implementations/adreno-fleet/gmu-analysis.md`** | a619, the `gmu->legacy` raw image, the full per-byte-range map of that generation |
| **`../../blob-matrix/laptop/qualcomm-adreno-a650-fleet.md`** | the content-level summary + the live-vs-carrying table |
| `a650_fleet_probe.py` | the probe that produces every number below |

Labels used throughout: **[S]** quoted from public GPL source (file:line, fetched
2026-11-19) · **[M]** my own measurement of payload bytes · **[OPEN]** not
established, gap named.

---

## 1. The format boundary — and the second one inside the container class

Mainline has two load paths and picks between them with `gmu->legacy`, not with a
filename [S]:

```c
/* drivers/gpu/drm/msm/adreno/a6xx_gmu.c:886-904 */
	u32 itcm_base = 0x00000000;
	u32 dtcm_base = 0x00040000;

	if (adreno_is_a650_family(adreno_gpu) || adreno_is_a7xx(adreno_gpu) ||
	    adreno_is_a8xx(adreno_gpu))
		dtcm_base = 0x10004000;

	if (gmu->legacy) {
		if (fw_image->size > 0x8000) { ... return -EINVAL; }
		gmu_write_bulk(gmu, REG_A6XX_GMU_CM3_ITCM_START,
			       (u32*) fw_image->data, fw_image->size);
		return 0;
	}
```

and the container walk [S]:

```c
/* a6xx_gmu.c:857-863, 874-875 */
struct block_header { u32 addr; u32 size; u32 type; u32 value; u32 data[]; };
#define NEXT_BLK(blk) ((const struct block_header *) \
	((const char *)(blk) + sizeof(*(blk)) + (blk)->size))
```

`gmu->legacy` is set for `ADRENO_6XX_GEN1` [S `a6xx_gmu.c:2412-2414`]. Measured
across the fleet, that predicate is exactly the observed split [M]:

| file | bytes | walk result | class | `u32[0]` | `u32[1]` | `vt@0x200` word0 | `0xEFBEADDE` count |
|---|---|---|---|---|---|---|---|
| a619 | 32,768 | overflow @0x19 | raw-tcm | `00043f80` | `00000009` | `00043f80` (=SP) | 0 |
| a630 | 32,768 | overflow @0x19 | raw-tcm | `00043f80` | `00000009` | `00043f80` (=SP) | 0 |
| a640 | 37,680 | exact EOF, 7 rec | container | `00043f80` | `00000009` | `00000000` | 14 |
| **a650** | **41,548** | **exact EOF, 16 rec** | **container** | `10007f80` | `00000011` | `00000000` | **14** |
| a623 | 53,516 | exact EOF, 15 rec | container | `10007f80` | `00000105` | *not loaded* | 8 |
| a660 | 55,252 | exact EOF, 15 rec | container | `10007f80` | `00000105` | *not loaded* | 8 |
| a662 | 55,888 | exact EOF, 15 rec | container | `10007f80` | `00000105` | *not loaded* | 8 |
| a663 | 55,892 | exact EOF, 15 rec | container | `10007f80` | `00000105` | *not loaded* | 8 |
| gen70000 | 57,272 | exact EOF, 15 rec | container | `10007f80` | `00000105` | *not loaded* | 8 |

(Each payload block contributes two occurrences — `type` and `value` — so 7
payload blocks give 14 and the 4-payload a660 family gives 8.)

**Rule: GEN1 ⇒ raw, GEN2+ ⇒ container.** The boundary is the load path, and it
is enforced by a predicate the driver evaluates, not by a naming convention.

### 1.1 The second boundary, at a650

Inside the container class there is a *second* discontinuity that no driver code
announces — it is only visible in the bytes [M]:

| | a640 | **a650** | a660 family |
|---|---|---|---|
| ITCM `0x0` block | 48 B, `u32[0]`=SP `0x43f80` | 192 B, `u32[0]`=MSP `0x10007f80` | 192 B, same |
| reset entry | ITCM `0x08` (32-bit Thumb vector) | ITCM `0x10` | ITCM `0x104` |
| VTOR target | `0x200` | `0x200` | `0x1000` |
| `0x200` window loaded? | **yes** | **yes** | **no** |
| `vt@0x200` word0 | `0x00000000` | `0x00000000` | n/a |
| stub shape | `msp+psp+vtor+bw` | `cnt+msp+psp+vtor+paint+bw` | `cnt+msp+psp+vtor+call+bw` |

Three distinct reset-prologue shapes, all decoded from the bytes with exact
ARMv7-M mask tests:

```
a640:   msp + psp + vtor + b.w        (8 instructions)
a650:   cnt + msp + psp + vtor + paint + b.w   (25 instructions)
a660:   cnt + msp + psp + vtor + bl + b.w      (14 instructions, entry 0x104)
```

The a650-into-a660 step moves the entry from `0x10` to `0x104`, replaces the
stack-paint loop with a `bl` to `0x84`, and — most importantly — stops loading
the `0x200` window at all, so its vector table lives elsewhere (`0x1000`). The
probe reports `vector_table_absent` rather than inventing a table out of
zero-fill, which is the correct answer: nothing loaded there.

## 2. The a650 block plan — verified, exact EOF

41,548 B = `0xa24c`, and the walk lands on `0xa24c` **exactly** after 16 records:
9 zero-size manifest records then 7 payload blocks [M]. (The sibling
`adreno650/a650-gmu-analysis.md` block table was re-verified against this walk
and is correct; this section adds the parts it does not cover.)

### 2.1 The seven payload blocks

Every payload block carries `type == value == 0xEFBEADDE` — on disk `DE AD BE EF`,
a byte-reversed `DEADBEEF` [M]. This is the container's payload tag, not a
sentinel.

| block | addr | size | region | entropy |
|---|---|---|---|---|
| p0 | `0x00000000` | 192 | ITCM | 5.06 |
| p1 | `0x00000200` | 320 | ITCM | 1.74 |
| p2 | `0x00000400` | 14,092 | ITCM | 6.86 |
| p3 | `0x00004000` | 21,968 | icache | 6.78 |
| p4 | `0x00157000` | 920 | icache | 2.50 |
| p5 | `0x10004000` | 3,776 | DTCM | 0.52 |
| p6 | `0x10007fdc` | 24 | DTCM (tail) | 2.11 |

ITCM total 14,604 B (≤ 16K) · icache 22,888 B · DTCM 3,800 B. Whole-file
entropy 6.43 bits/byte, 19.1 % zero.

### 2.2 The nine manifest records, and why they are *not* a block index

The leading zero-size records are skipped wholesale by the kernel [S
`a6xx_gmu.c:909-910`: `if (blk->size == 0) continue;`], so their `value` field is
never read by Linux. They nonetheless tile the loader's own memory windows [M]:

| manifest | addr | value | mainline counterpart |
|---|---|---|---|
| m0–m2 | `0x0`, `0x200`, `0x400` | `0x200`, `0x200`, `0x3c00` | ITCM `0x0..0x4000` tiled |
| m3 | `0x4000` | `0x8000` | icache base (`a6xx_gmu.c:2393`) |
| m4, m5 | `0x10004000`, `0x10007fdc` | `0x3fe0`, `0x24` | DTCM `0x10004000..0x10008000` |
| m6, m7 | `0x144000`, `0x157000` | `0x13000`, `0x9000` | icache sub-windows |
| m8 | `0x60000000` (type **7**) | `0x1000` | dummy page BO (`a6xx_gmu.c:2384`) |

A tempting reading is that a manifest `(addr, value)` names a payload block.
Measured across the fleet, that hypothesis fails: only **3 of 11** a660-family
manifests have a pair that exactly matches a payload block, and **a650 matches
0 of 9** [M]. The manifest is a *window map* the chip consumes, not an index of
the blocks the kernel copies. Reporting it as the latter would be a fabricated
correlation — this is exactly the kind of claim that RULE 0 exists to prevent, so
it is recorded as a **negative** result.

## 3. The a650 reset stub, decoded

Entry `0x10` (`u32[1] = 0x11`, Thumb bit set). All seven literals resolve inside
the 192-byte ITCM block. Full linear decode [M]:

```
0x10  4811         ldr   r0,[pc,#0x44]   ; -> 0x58 = 0x10007fdc  (boot counter)
0x12  6801         ldr   r1,[r0,#0]
0x14  ea4f 2101    mov.w r1,r1,lsl #8
0x18  f101 0101    add.w r1,r1,#1
0x1c  6001         str   r1,[r0,#0]      ; counter = (counter<<8)+1
0x1e  480f         ldr   r0,[pc,#0x3c]   ; -> 0x5c = 0x10007f80  (MSP)
0x20  f380 8808    msr   msp,r0
0x24  480e         ldr   r0,[pc,#0x38]   ; -> 0x60 = 0xdeadbeef  (PSP sentinel)
0x26  f380 8809    msr   psp,r0
0x2a  480e         ldr   r0,[pc,#0x38]   ; -> 0x64 = 0x00000200  (VTOR value)
0x2c  490e         ldr   r1,[pc,#0x38]   ; -> 0x68 = 0xe000ed08  (SCB->VTOR)
0x2e  6008         str   r0,[r1,#0]      ; *VTOR = 0x200
0x30  4809         ldr   r0,[pc,#0x24]   ; -> 0x58 = 0x10007fdc  (counter again)
0x32  6801         ldr   r1,[r0,#0]
0x34  ea4f 2101    mov.w r1,r1,lsl #8
0x38  f101 0102    add.w r1,r1,#2
0x3c  6001         str   r1,[r0,#0]      ; counter = (counter<<8)+2
0x3e  480b         ldr   r0,[pc,#0x2c]   ; -> 0x6c = 0x10007000  (paint base)
0x40  f44f 6178    mov.w r1,#0xf80
0x44  f04f 32aa    mov.w r2,#0xaaaaaaaa
0x48  6002         str   r2,[r0,#0]
0x4a  f100 0004    add.w r0,r0,#4
0x4e  3904         subs  r1,#4
0x50  d1fa         bne   0x48
0x52  f000 b9d5    b.w   0x400
0x56  bf00         nop
```

Every mnemonic above is an exact mask test on the published ARMv7-M encoding, not
a pattern match against a remembered byte sequence. The probe's decoder and the
fixture generator's encoder were written independently from the same
specification, so an encoder/decoder disagreement surfaces as a test failure.

### 3.1 What the numbers mean

- **MSP `0x10007f80` = DTCM top `0x10008000` − `0x80`** — the conventional
  reserved slot below a Cortex-M vector table. `0x80` is not arbitrary: it is the
  architectural minimum stack alignment plus the space the core itself may claim.
- **The paint loop covers `0x10007000..0x10007f80` (0xf80 B), ending exactly at
  MSP.** The 0xaaaaaaaa pattern is a stack-high-water detector: unwritten bytes
  stay `0xaaaaaaaa`, so post-mortem you can read how deep the stack went.
- **PSP holds `0xdeadbeef`.** This is the host-order sentinel, deliberately
  distinct from the `0xefbeadde` payload tag. Both spellings occur in this file;
  conflating them is a reading error the doc calls out explicitly.
- **The counter is bumped twice, +1 then +2**, using `(v << 8) + n`. Two
  sequential bumps in one prologue means the field is a *sequence* counter, not a
  single boot flag — the low byte is effectively a stage marker.

### 3.2 The stack page is never written by the container

A consequence worth stating because it looks like an error and is not [M]: the
DTCM blocks cover `0x10004000..0x10004ec0` and `0x10007fdc..0x10007ff4`. The
initial SP `0x10007f80` falls in the **gap**. Nothing in the file initialises the
stack. That is correct behaviour — a firmware that shipped pre-filled stack bytes
would be initialising a region the core overwrites on the first push, and the
paint loop exists precisely so the runtime can detect its own usage. The probe
reports this as `msp-unmapped` (info, not error) rather than as a defect.

## 4. The vector table at `0x200`

80 words: 16 architectural entries then 64 external interrupts [M].

| index | vector | value | Thumb |
|---|---|---|---|
| 0 | Initial SP | `0x00000000` | — |
| 1 | Reset | `0x00000011` | odd ✓ |
| 2 | NMI | `0x000004d1` | odd ✓ |
| 3–6 | HardFault, MemManage, BusFault, UsageFault | `0x000004a1` | odd ✓ |
| 11 | SVCall | `0x000035a1` | odd ✓ |
| 14 | PendSV | `0x00000509` | odd ✓ |
| 15 | SysTick | `0x000035a3` | odd ✓ |
| 16–79 | 64 external IRQs | `0x00000579` | odd ✓ |

**word0 is zero, not a stack pointer.** This is the a650 discriminator: a
Cortex-M vector table conventionally repeats the initial SP at word 0, and a619
and a640 both do. From a650 the SP comes from the prologue's own literal, so the
`0x200` table is a pure handler table. The probe names the role (`initial-SP
copy` / `unused (zero)`) instead of assuming.

Two independent self-consistency checks pass [M]: every non-zero handler is odd
(Thumb) **and** every one resolves into loaded code. A vector pointing at an
address no block maps would be an immediate red flag; there are none.

All 64 external interrupts collapse onto a **single** handler. The microcode does
not do discrete per-IRQ dispatch — consistent with a management unit that polls
rather than serves.

## 5. The DTCM `0xff8` handshake — all generations take the legacy branch

The driver decides which magic to write by reading one word [S]:

```c
/* a6xx_gmu.c:311-318 */
	val = gmu_read(gmu, REG_A6XX_GMU_CM3_DTCM_START + 0xff8);
	if (val <= 0x20010004) {
		mask = 0xffffffff;
		reset_val = 0xbabeface;
	} else {
		mask = 0x1ff;
		reset_val = 0x100;
	}
```

Measured per generation [M]: a650's DTCM payload block ends at `0x10004ec0`, so
`0x10004ff8` is **not covered** and reads 0 → `0 <= 0x20010004` → the legacy
`0xbabeface` path. a640 covers it and stores `0x20000105`, still ≤ the
threshold, so also legacy. Every generation measured selects the **legacy**
branch. (Correction to a common misreading: the 24-byte tail block at
`0x10007fdc` does *not* cover `0x4ff8`; the value that would matter is in the
`0x10004000` block, if it were large enough — and at 3,776 B it is not.)

`0xBABEFACE` as a little-endian u32 appears **twice** in a619/a630, **once** in
a640, and **zero** times in a650. Do not generalise the a619 count.

## 6. The SQE version gate — and why the device copy cannot bring up a GPU

### 6.1 The strip

`adreno_fw_create_bo()` allocates `fw->size − 4` and copies from `&fw->data[4]`
[S `adreno_gpu.c:644-656`]. So **file dword 0 is a stripped prefix** and the
driver's `buf[0]` is **file dword 1**. In all 15 builds examined, file dword 0 is
`0x00000000`.

The probe therefore classifies an SQE by `dword0 == 0` plus a non-zero version
dword plus a plausible size, and reads the version from `dword1`. A 4-byte zero
prefix on a multi-KiB, dword-aligned file is a 2⁻³² coincidence elsewhere, so the
discriminator is strong; what the prefix *means* is `[OPEN]`.

### 6.2 The four branches

[S `a6xx_gpu.c:985-1049`]:

```c
	if (adreno_is_a7xx(...) || adreno_is_a702(...) || adreno_is_a8xx(...))
		return true;                                   /* early return */

	if (!strcmp(sqe_name, "a630_sqe.fw")) {
		if ((((buf[0] & 0xf) == 0xa) && (buf[2] & 0xf) >= 1) ||
		    (buf[0] & 0xfff) >= 0x190) { ...; ret = true; }
	} else if (!strcmp(sqe_name, "a650_sqe.fw")) {
		if ((buf[0] & 0xfff) >= 0x095) { ret = true; }
	} else if (!strcmp(sqe_name, "a660_sqe.fw")) {
		ret = true;                                    /* unconditional */
	} else {
		DRM_DEV_ERROR(... "unknown GPU, add it to a6xx_ucode_check_version()!!");
	}
```

Note the field asymmetry, which is easy to get wrong: the a630 patched test reads
`buf[2]` — the **BO's** dword 2, i.e. **file dword 3** — while the version is
`buf[0] & 0xfff`, i.e. file dword 1. The probe reports `dword3_low_nibble`
separately for exactly this reason.

### 6.3 Measured, both directions

| build | bytes | md5 | file dword 1 | `v & 0xfff` | text | passes a650 |
|---|---|---|---|---|---|---|
| device fleet (DB md5) | 31,632 | `353e247b2c4ea8c16c49cb31b574edc1` | `0x016dd093` | `0x093` | 0.93 | **NO** |
| linux-firmware | 31,964 | `dc02e77a04b97b985281d36ab159c130` | `0x016dd112` | `0x112` | 1.12 | YES |

**The device-fleet a650 SQE fails mainline's floor.** The consequence is not
cosmetic and is fully traceable in public source [S]:

```
a6xx_ucode_load()      returns -EPERM      (a6xx_gpu.c:1077)
  -> adreno_load_gpu() returns NULL        (adreno_device.c:96-100)
    -> the GPU never registers
```

So a phone carrying this exact SQE cannot bring up its GPU under mainline. The
fix is a `>= 0.95` build, which linux-firmware has had for years — the two builds
share only 18 % of same-offset bytes, so this is genuinely different microcode,
not a repack.

#### 6.3.1 Independent corroboration — a third build found during review

Reviewing this document (2026-11-19), a third `a650_sqe.fw` was located that is
**not** the DB identity and **not** the linux-firmware one:

| build | bytes | md5 | file dword 1 | `v & 0xfff` | text | passes a650 |
|---|---|---|---|---|---|---|
| OnePlus `sm8250-common` @ lineage-19.1 | 31,488 | `540773bd30e4713fa32b9eb2b869ef8c` | `0x016dd091` | `0x091` | 0.91 | **NO** |

This matters for two reasons. First, it is a **third independent build** of the
same filename that also fails the `0x095` floor — so the "the fleet's a650 SQE is
too old" finding does not rest on a single vendor copy. Second, it shows the
version axis is real and populated: three distinct `a650_sqe.fw` builds exist in
public trees at `0x091`, `0x093` and `0x112`, i.e. the filename is *not* an
identity here either (the F-75 phenomenon, observed again on GPU microcode).

The DB identity (`353e247b…`, 31,632 B, v0.93) was **not** re-fetched during this
review; the claim about that specific md5 remains as originally measured. The
finding that survives independently is the structural one: multiple sub-0.95
`a650_sqe.fw` builds circulate on real devices, and mainline rejects every one of
them at `a6xx_gpu.c:1032`.

### 6.4 An independent cross-check that the decode is right

`WHENCE` declares a version per firmware file. For the **SQE** files that string
decodes exactly as `%x.%02x` of `(dword1 & 0xfff)` — all five checked [M]:

| file | WHENCE | decoded |
|---|---|---|
| `a650_sqe.fw` | `v1.12` | 1.12 ✓ |
| `a630_sqe.fw` | `v2.07` | 1.97 device / 2.07 linux-fw (WHENCE tracks the linux-fw build) |
| `a660_sqe.fw` | `v1.12` | 1.12 ✓ |
| `a730_sqe.fw` | `v1.81` | 1.81 ✓ |
| `a740_sqe.fw` | `v1.81` | 1.81 ✓ |

The **GMU** files do *not* carry that version. `a650_gmu.bin` dword 1 is
`0x00000000` — the same field a container must keep zero, since dword 1 is the
first block header's `size` field. The driver does not read a GMU version from
the file at all: it reads a register after the firmware is running,
`ver = gmu_read(gmu, REG_A6XX_GMU_CORE_FW_VERSION)` [S `a6xx_gmu.c:933-937`].
So `WHENCE`'s `qcom/a650_gmu.bin v2.1.8` is a *release label*, not a field in the
blob, and this check is deliberately scoped to the five SQE files.

## 7. The REX string table — the highest-value artifact in this file

Printable-run census at minimum length 10 [M]:

| file | runs ≥10 chars |
|---|---|
| a619 | **1** |
| a630 | **1** |
| a640 | 62 |
| **a650** | **81** |
| a623 | 96 |
| a660 | 78 |
| a663 | 99 |
| gen70000 | 104 |

The jump from 1 to 62 at a640 is the arrival of a debug-build string table with
the container generation. a650's 81 runs sit almost entirely in
`0xb4c..0x398c`, and they are **assert/abort format strings that name the failing
function** — precisely the call sites a rebuild would need to satisfy. Grouped by
subsystem [M]:

| subsystem | strings |
|---|---|
| REX RTOS scheduler | `REX Idle Task`, `Trying to create more than REX_MAX_TASKS`, `rex_leave_crit_sect_internals() Failure: save_ptr == NULL`, ~20 further `rex_*` calls |
| signals / heap | `SIGABRT: Abnormal termination`, `SIGRTMEM: Out of heap memory`, `: Heap memory corrupted`, `SIGRTRED: Redirect: can't open: ` |
| event map | `EventMapAdd`, `EventMapRemove`, `RegisterFuncForEvent`, `AllocEventPool`, `FreeEventPool`, `RecordEvent`, `PopTaskQueue` |
| cache / memory ops | `InvalidateDCache`, `InvalidateICache`, `GmuDCacheOp`, `FlushWriteBuffer`, `InvalidateReadBuffer` |
| HFI protocol layer | `HfiReadMsgPool`, `HfiWriteMsgPool`, `HfiGetMemDescriptor`, `HfiMemReply`, `HfiValueHandler`, `HfiUseBottomHalf`, `HandleHfiCommand`, `HfiMsgToHost`, `HfiQueueTryRead` |
| power / idle state (IFPC) | `GmuPwrStart`, `GmuPwrRequestPowerOn`, `GmuPwrQueryGxPowerState`, `GmuPwrGxBwVote`, `abortPwrCollapse`, `beginHmPwrCollapse`, `beginHmPwrOn`, `IfpcProfiling`, `EnterIdleState`, `ExitIdleState`, `PwrIdleStateGetStateIdx` |
| clock / voltage (RSCC) | `ResMgrReqClkThrot`, `RsccSetVoltageVoteData`, `RsccSendVoting`, `HAL_clk_ValidateRegTimeout` |
| sysmgr / timers | `SysMgrTask`, `GenericTimerHandler`, `SMSetValue`, `SMSetDebug`, `LogEventEnable` |

This names the RTOS primitives (REX), the HFI protocol layer, the IFPC power/idle
state machine, the RSCC voltage-voting path and the RSC/clock HAL — without a
single line of decompiled code. It is the closest thing to documentation this
artifact has.

**Caveat, stated because it is real:** a naive `>= 8`-char ASCII filter over
16-bit Thumb code also catches machine-code false positives (e.g. `` `pGpG ``,
`g2F)F F'`). The extracted sample is a *sample*, not a symbol table; the
semantic strings above were selected by reading them, not by regex. The probe
uses minimum 4 by default and reports the count, so the number is honest about
being a count of printable runs.

## 8. Fleet scope — a correction to the raw database row count

The database lists **14** distinct devices against `a650_gmu.bin`, all sharing
md5 `a2b9504e3d1cb8686ae7fcca21a11e1a`. Mainline names the file in exactly
**one** catalog entry [S `a6xx_catalog.c:1052-1057`]:

```c
	.chip_ids = ADRENO_CHIP_IDS(0x06050002),
	.family = ADRENO_6XX_GEN3,
	.revn = 650,
	.fw = { [ADRENO_FW_SQE] = "a650_sqe.fw",
	        [ADRENO_FW_GMU] = "a650_gmu.bin" },
```

and chip id `0x06050002` is what `find_chipid()` computes from
`"qcom,adreno-650.2"` [S `adreno_device.c:142-170`], the compatible
`dts_sm8250.dtsi:2935` binds. So *carrying* the file and *loading* it are
different claims, and only one device class loads it.

| class | devices | `TARGET_BOARD_PLATFORM` | evidence |
|---|---|---|---|
| **live — Adreno 650** | `instantnoodle`, `instantnoodlep`, `kebab`, `lemonades`, `gts7l`, `gts7lwifi`, `r8q`, `pdx206`, `Xperia_1_II` | `kona` (SM8250) | each device's inherited `BoardConfigCommon.mk` sets `kona` |
| Adreno 610 | `gta4l`, `gta4lwifi` | `bengal` (SM6115) | `gta4l-common`: `TARGET_BOARD_PLATFORM := bengal`, `TARGET_BOARD_PLATFORM_GPU := qcom-adreno610` |
| Adreno 620 | `Pixel_4A_5G` (bramble), `Pixel_5` (redfin), `Pixel_5A` (barbet) | `lito` (SM7250) | the DB's own `soc` column says `Qualcomm SM7250 Snapdragon 765G`; `redbull/BoardConfig-common.mk` says `lito` |

**Verdict: 9 live of 14 carried.** The other five are co-resident leftovers — a
vendor firmware partition is a superset of what one SoC binds. Both non-live
Android classes corroborate: `gta4l` also ships `a702_sqe.fw`/`a702_zap.mdt`
(the a702 GMU wrapper, `sm6115.dtsi:1811`), and the Pixels carry `a619_gmu.bin` +
`a630_sqe.fw` alongside, i.e. a whole family of GMU blobs for one GPU.

### 8.1 The `pdx215` row is mislabelled — and correcting it *adds* a live device

The DB row reads `Xperia_1_II | sony/pdx215 | a650_gmu.bin`. The codename is
wrong, but the contents identify the real device.

1. **Mainline DTS:** `sm8250-sony-xperia-edo-pdx203.dts` is the Xperia 1 II
   (`model = "Sony Xperia 1 II"`, `compatible = "sony,pdx203-generic"`, SM8250);
   `sm8350-sony-xperia-sagami-pdx215.dts` is the **Xperia 1 III** (SM8350). So
   the pair `Xperia_1_II | pdx215` is internally inconsistent.
2. **Contents match pdx203, not pdx215.** All 21 files under the DB's
   `sony/pdx215/vendor/firmware` path are present in the pre-split
   `sm8250-common` tree or the pre-split `pdx203` directory. The discriminating
   file is `touch_module_id_0x83.img`: the DB lists it at 169,224 B / md5
   `279ca2f166d1c051a86f6dbc4165e937`, and `proprietary_vendor_sony_pdx203`
   carries a byte-identical copy. The genuine `pdx215` split tree carries
   `touch_module_id_0x28.img` instead.
3. **The real `pdx215` does not carry this blob.** Its split vendor tree has
   `a619_gmu.bin`, `a630_sqe.fw`, `a660_gmu.bin`, `a660_sqe.fw` — and **no
   `a650_gmu.bin`** — on `lineage-22.1`, `22.2` and `24.0`. Its
   `proprietary-files.txt` lists the same four. `pdx215` also inherits
   `sm8350-common` (`TARGET_BOARD_PLATFORM := lahaina`), i.e. Adreno 660.
4. **`pdx203` is SM8250/kona.** Its `BoardConfig.mk` inherits `sm8250-common`,
   whose `BoardConfigCommon.mk` sets `TARGET_BOARD_PLATFORM := kona`.

So the row is a duplicate of the **Xperia 1 II / pdx203** firmware set carrying
the wrong codename in `db_path`. `device-inventory.csv` already lists
`Xperia_1_II` twice — once as `pdx203` (SM8250) and once as `pdx215` (soc blank)
— which is how the two got crossed.

**Consequence for the headline number.** Earlier in this session I had this row
counted as a dead SM8350/Adreno-660 leftover, giving 8 live. That was wrong: the
device behind the row is SM8250/kona, so it is **live**. The count is **9 live of
14 carried**, and the correction *raises* the impact of the SQE finding rather
than lowering it. The md5 is byte-identical to the other 13 rows either way, so
this remains a database attribution correction, not a payload finding.

## 9. What this buys a free reimplementation

- **The container format is fully specified** by mainline plus a file that walks
  to EOF exactly. A free loader already exists (`msm`); what is missing is not
  the format but the microcode itself.
- **Three reset-prologue shapes are now pinned** (`a640`/`a650`/`a660`) and each
  is decoded into architectural facts a reimplementation must reproduce: where
  the stack is, where VTOR points, whether the stack page is pre-written, and
  whether a boot counter is maintained.
- **The SQE gate is a hard, checkable contract.** Any free stack shipping the
  device copy will fail `a6xx_ucode_load()` with `-EPERM` and register no GPU. A
  `>= 0.95` build is required, and linux-firmware has one. That single fact is
  actionable for all 9 live devices.
- **The string table names the services.** REX, HFI, IFPC idle states, RSCC
  voting, the RSC/clock HAL — a reimplementation knows what it must provide,
  without any code having been decompiled.
- **The manifest is a window map, not an index.** Establishing this *negatively*
  saves a reimplementation from building a block-index table the chip does not
  use.

## 10. `[OPEN]` list

1. **Manifest semantics.** `(addr, value)` pairs tile the windows exactly, but the
   kernel skips `size == 0` records and never reads `value` [S
   `a6xx_gmu.c:909-910`]. Only the chip consumes them. Which field means what is
   unknown; the "manifest names a payload block" hypothesis is *refuted* for a650
   (0 of 9).
2. **The stripped SQE dword 0.** Zero in all 15 builds examined; semantic
   unknown. It is not a size, since the BO is `size − 4` regardless.
3. **The `0xdeadbeef` PSP sentinel's purpose.** It marks PSP as deliberately
   invalid on entry, but whether an exception handler later checks it is not
   established.
4. **The boot-counter encoding.** `(v << 8) + n` with two bumps of `+1` then `+2`
   suggests a stage-tagged sequence, but the counter's consumer is not identified.
5. **What the microcode computes.** Out of scope for any clean-room structural
   method; requires execution or synthesis.
6. **The a660-family `0x1000` vector window.** Nothing in the file loads it, so
   its contents at runtime are unknown from static bytes alone.
7. **`pdx215` path label** (§8.1) — the row's contents are pdx203's; only the
   `db_path` codename is wrong. The device itself is live. Resolve by relabelling
   the row, not by dropping it.

## 11. Scratch artifacts (regeneratable)

Under `/tmp/astro_u/a650/` (never committed):

```
payloads/oneplus_a650_gmu.bin        41,548 B  md5 a2b9504e…  (5 vendor trees, byte-identical)
payloads/oneplus_a650_sqe.fw         31,632 B  md5 353e247b…  (device build, fails the floor)
peers/a650_sqe.fw                    31,964 B  md5 dc02e77a…  (linux-firmware, v1.12)
peers/{a623,a630,a640,a660,a663}_gmu.bin                  cross-generation set
payloads/{xi8450_a662,gmu_gen70000,*_a730,*_a740}*        cross-generation set
kernelsrc/{a6xx_gmu.c,a6xx_gmu.h,a6xx_gpu.c,a6xx_catalog.c,
           adreno_gpu.c,adreno_gpu.h,adreno_device.c}     ground truth
WHENCE                                                     declared versions
out/a650_gmu.json  out/a650_sqe_device.json  out/a650_sqe_linuxfw.json
```

Regenerate the reports:

```
python3 -I a650_fleet_probe.py <payload> --json out/x.json --cross-gen <files...>
python3 -I make_fixture.py          # synthetic fixtures
python3 -m unittest -v test_a650_fleet_probe
```

## 12. Route log (2026-11-19)

1. **RULE 0 first.** `gh api search/code` for `a650_fleet_probe` → 0;
   `a6xx_gmu_fw_header` → 0; `a650_gmu.bin+efbeadde` → 1 repo
   (`xVanTuring/UniXNU-pipa`), `a650_gmu.bin+block_header` → same. Read that
   project's `A650Gmu.c` / `A650Gmu.h` / `A650GmuTests.c` in full: it builds a
   synthetic container in a host unit test and consumes the `0x10007fdc` DTCM
   handshake as mainline does. It does **not** decode the reset stub, the vector
   table, the manifest tiling, the paint loop, the counter or the SQE contract —
   that set is the delta here.
2. **Ground truth fetched** from torvalds/linux master and linux-firmware
   (`git.kernel.org` plain, reliable; `raw.githubusercontent.com` intermittently
   times out and needs retries).
3. **Payloads fetched and md5-verified.** All five vendor trees' `a650_gmu.bin`
   are byte-identical to linux-firmware and to the DB md5. The device
   `a650_sqe.fw` is byte-identical across all five and is **not** in
   linux-firmware.
4. **Walk first, then decode.** The documented `block_header` walk reaches EOF
   exactly at `0xa24c`; only then was the reset stub decoded, then the vector
   table, then the DTCM handshake, then the SQE.
5. **Negative results kept, and one of them was corrected.** The
   manifest-is-a-block-index hypothesis was tested and refuted (0 of 9). The
   `pdx215` DB row was tested; the first reading (SM8350/Adreno 660, dead) was
   wrong, and the contents-based check showed the row is pdx203's Xperia 1 II
   set, which is live — so the live count moved from 8 to 9. Both the refutation
   and the self-correction are recorded rather than quietly dropped.
6. **Prior-art honesty.** The one overlapping public project is named and
   delineated in `README.md` so a reader can see exactly what is new and what is
   agreement.
