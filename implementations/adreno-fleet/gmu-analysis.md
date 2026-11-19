# GMU microcode analysis — real-payload RE of `a619_gmu.bin` (2026-11-18)

Content-level RE of the Adreno GMU microcode blob at recon.md row 10
(26 DB rows share these bytes; **13 devices actually load them** — the
correction is §2.2). Payload `a619_gmu.bin` — 32,768 B, md5
`9e23c52057bb573dee9ba31f1fdba4fa`, sha256
`9ef10b2b179054fb57af25008e29feb24300c2eaaeabf907bd741786bbacbf2e` —
fetched and md5-verified by the lead against the upstream database, then
measured here. Source:
`raw.githubusercontent.com/TheMuppets/proprietary_vendor_oneplus/lineage-19.1/dre/proprietary/vendor/firmware/a619_gmu.bin`
(dre = OnePlus Nord N200 5G). Payload bytes live only in
`/tmp/astro_u/payloads/`; nothing proprietary is committed.

Clean-room statement: every claim below rests on (a) public GPL-2.0 kernel
sources and (b) this session's structural measurements of the payload bytes.
No decompiler, disassembler, vendor datasheet or leaked document was used.
No code was interpreted beyond ARMv7-M architectural encodings that are
publicly specified. Claims are labelled:

- **[S]** source-cited — quoted from public GPL source, file + line.
- **[M]** measurement — my own count/offset/hash over the payload bytes.
- **[OPEN]** not established; the specific gap is named.

## 1. The public-header verdict — the premise is false, and here is what is true

### 1.1 What was claimed, and what the sources actually say

The task premise was that Adreno GMU firmware begins with a documented
`struct a6xx_gmu_fw_header` in `a6xx_gmu.h`. **That struct does not exist.**
Checked by fetching the real file (authenticated `gh api ... ?ref=<tag>` +
base64-decode, 2026-11-18):

| ref | `a6xx_gmu.h` lines | occurrences of `fw_header` |
|---|---|---|
| `master` | 245 | **0** |
| `v6.1` | 190 | **0** |
| `v5.15` | 190 | **0** |
| `v5.10` | 203 | **0** |
| `v5.4` | 168 | **0** |

An authenticated GitHub code search for `a6xx_gmu_fw_header` returns
`total_count: 0`. Fetching succeeded (each file parses as C and begins with
its SPDX header); these are real negatives, not rate-limit pages.

What mainline **does** document, in `a6xx_gmu.c`, is the only firmware
container struct it has [S]:

```c
/* drivers/gpu/drm/msm/adreno/a6xx_gmu.c:857-863 */
struct block_header {
	u32 addr;
	u32 size;
	u32 type;
	u32 value;
	u32 data[];
};
```

with the chain advance defined as [S]:

```c
/* a6xx_gmu.c:869-871 */
#define NEXT_BLK(blk) \
	((const struct block_header *)((const char *)(blk) + sizeof(*(blk)) + (blk)->size))
```

So a container record is a 16-byte header plus `size` bytes of payload.

### 1.2 Why this particular file is not a container — the load path decides

mainline has **two** GMU load paths, and which one runs is decided by
`gmu->legacy` [S]:

```c
/* a6xx_gmu.c:894-904 */
	if (gmu->legacy) {
		/* Sanity check the size of the firmware that was loaded */
		if (fw_image->size > 0x8000) {
			DRM_DEV_ERROR(gmu->dev,
				"GMU firmware is bigger than the available region\n");
			return -EINVAL;
		}

		gmu_write_bulk(gmu, REG_A6XX_GMU_CM3_ITCM_START,
			       (u32*) fw_image->data, fw_image->size);
		return 0;
	}
```

`gmu->legacy` is set for the `ADRENO_6XX_GEN1` family [S]:

```c
/* a6xx_gmu.c:2412-2414 */
	} else if (adreno_is_a630_family(adreno_gpu)) {
		/* HFI v1, has sptprac */
		gmu->legacy = true;
```

and a619 is `ADRENO_6XX_GEN1` [S] — `a6xx_catalog.c:872-876` and again at
898-901 and 920-925 (three a619 entries: sm4350, sm6375, and a generic
chip-id entry), each with `.family = ADRENO_6XX_GEN1` and
`[ADRENO_FW_GMU] = "a619_gmu.bin"`. `adreno_is_a630_family()` tests
`gpu->info->family == ADRENO_6XX_GEN1` (`adreno_gpu.h:517-522`), and
`adreno_is_a615_family()` explicitly groups a618 with a619
(`adreno_gpu.h:512-515`).

**So for a619 the driver never parses the file at all.** It checks one size
bound and DMA-writes all 32,768 bytes to `GMU_CM3_ITCM_START`. There is no
header to find, because the loader does not look for one.

This is confirmed negatively on the bytes: running mainline's own walk on
`a619_gmu.bin` fails on the first record [M] —

```
@0x00000 addr=00043f80 size=00000009 type=f3804805 value=48058808
-> next = 0x19 + 0x9 = 0x22 ... chain overflows the file
```

`size = 9` is not a payload length; it is the raw byte `0x09` of a Thumb
branch. The chain desynchronises immediately. **Verdict: `a619_gmu.bin`
carries no container header.** It is a raw memory image.

### 1.3 But the sibling generation *does* have the container — measured

The same walk, run on the linux-firmware siblings, lands on **exact EOF**
[M]:

| file | bytes | md5 | walk result | records |
|---|---|---|---|---|
| `a623_gmu.bin` | 53,516 | `7906b8a180c11d48d882bb9ff5c90ba5` | EXACT EOF | 15 |
| `a640_gmu.bin` | 37,680 | `99d0c614ab7ca1e4f5ab9281aaee2f11` | EXACT EOF | 7 |
| `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` | EXACT EOF | 16 |
| `a660_gmu.bin` | 55,252 | `cd3a235218418f51360888637c1cb2ac` | EXACT EOF | 15 |
| `a663_gmu.bin` | 55,892 | `bcd60be9a312caf37e3575776c0a4d3f` | EXACT EOF | 15 |
| `a630_gmu.bin` | 32,768 | `ab20135f7adf48e0f344282a37da80e4` | **overflow** | — |
| **`a619_gmu.bin`** | **32,768** | **`9e23c52057bb573dee9ba31f1fdba4fa`** | **overflow** | — |

All six fetched from
`git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/qcom/<name>`
(2026-11-18). a640's walk in full [M]:

```
@0x00000 addr=00000000 size=00000030
@0x00040 addr=00000200 size=00000140
@0x00190 addr=00000400 size=000038bc
@0x03a5c addr=00004000 size=00003a58
@0x074c4 addr=00040000 size=00001b20
@0x08ff4 addr=00043fe0 size=00000014
@0x09018 addr=00057000 size=00000308
end 0x9330 / 0x9330   <- exact
```

This splits the family cleanly and is a **stronger** result than either
answer alone: the container format is real and documented and used — just
not by the 6XX_GEN1 generation, which is precisely the generation the driver
marks `legacy`. `a630_gmu.bin` (also 6XX_GEN1, also 32,768 B) fails the walk
exactly as a619 does. **The boundary is the load path, not the filename.**

### 1.4 The `0x43f80` question, settled

The lead's probe noted `0x43f80` at u32[0] and u32[8] and asked whether it is
a load address, a size, or a magic. It is **none of those** — it is the
**initial stack pointer**, and the evidence is decisive [M]:

1. It sits in the DTCM window: `0x40000 <= 0x43f80 < 0x44000`.
2. It equals **DTCM top − 0x80** exactly (`0x44000 - 0x80`), the conventional
   reserved slot immediately below a Cortex-M vector table.
3. The reset stub **loads it into MSP** and loads the same value as the first
   word of the vector table it points VTOR at (below).
4. The same value appears at u32[0] (the architectural initial-SP slot) and
   at vector-table word 0 — **that repetition is the ARMv7-M contract**, not
   a self-referential pointer.

The `0x8000` size is separately explained: `0x8000 == ITCM(0x4000) +
DTCM(0x4000)`, and `0x8000` is exactly the loader's cap [S]. The file is not
"32 KiB of code"; it is two 16 KiB TCM images laid end to end.

## 2. Provenance and fleet scope (verified this session)

md5 re-verified: `9e23c52057bb573dee9ba31f1fdba4fa` — **MATCH** vs the
upstream DB. sha256 recorded above.

Counts re-derived from `upstream-contribution/blob-database/coverage-matrix.csv` [M]:

| query | result |
|---|---|
| rows with filename `a619_gmu.bin` | **24** |
| rows with filename `a618_gmu.bin` | **2** |
| rows with md5 `9e23c520…` (any filename) | **26** |
| distinct devices for that md5 | **26** |
| laptop-half devices carrying this md5 | **7** (luigi, oscar, pdx215, pdx206, pdx214, a71, laurel_sprout) |
| **devices that actually load it** | **13** — see §2.2 |

The two `a618_gmu.bin` rows are **Samsung Galaxy A71** (`samsung/a71`) and
**Xiaomi Mi A3** (`xiaomi/laurel_sprout`) — same md5, same size. So the
**byte-identical** footprint is 26 devices spanning both names.
`sharing-clusters.csv` line 494 records the cluster as 7 devices
(`a71; laurel_sprout; luigi; oscar; pdx206; pdx214; pdx215`) — the 5
metadata-listed laptop devices plus the 2 aliases.

Why one image serves 618 and 619: both are `ADRENO_6XX_GEN1`, and
`adreno_is_a615_family()` groups them [S].

### 2.2 Correction: 26 rows share the bytes, 13 devices load them

**A device carrying the file is not a device running it.** `a619_gmu.bin` is
only loaded by hardware mainline models as `revn = 619`
(`a6xx_catalog.c:872-876, 898-901, 920-925`, all `ADRENO_6XX_GEN1`). On a
device whose GPU is an Adreno 650 or 660 — different `revn`, different
family — the driver requests `a650_gmu.bin`/`a660_gmu.bin` and the `a619`
copy is a co-resident leftover from a shared BSP firmware directory.

Grouping the 26 by the SoC recorded in the DB [M]:

| class | devices |
|---|---|
| SoC is Adreno-619-class (SM4350/SM4375/SM6375/SM7225) | **11** |
| `a619` is the only GMU blob present (SoC field unrecorded; both SM7325) | **2** (`Edge_20`, `Edge_2021`) |
| co-resident with `a650`/`a660`, **not** 619-class → never loaded | **11** |
| `a618` alias rows (carry `a630`/`a640`) → never loaded | **2** (`Galaxy_A71`, `Mi_A3`) |
| **total** | **26** |
| **live union** | **13** |

Not loaded on: `Edge_30`, `Edge_30_Fusion`, `G_Stylus_5G-2-2022`,
`Galaxy_A71`, `Mi_A3`, `Moto_G200`, `Moto_G_Stylus_5G`, `Pixel_4A_5G`,
`Pixel_5`, `Pixel_5A`, `Xperia_1_II`, `Xperia_5_II`, `Xperia_5_III`.
(`Galaxy_A71`/`Mi_A3` carry `a630` as well, and mainline binds
`a630_gmu.bin` to `revn = 618`/sm7150 at `a6xx_catalog.c:846-852`.)

**One RE pass informs 13 devices, not 26.** The `26` stays correct as a
dedup/bandwidth figure — "how many DB rows share these exact bytes" — and is
retained for that purpose. The laptop-half live count is **2**
(`Realme_10_Pro`, `Realme_9_Pro`), not 5; `pdx215`/`pdx206`/`pdx214` are
co-resident cases. Details and the per-device table:
`../../blob-matrix/laptop/qualcomm-adreno-gmu-content.md` §5.

### 2.1 linux-firmware absence — a second F-74-class finding

`a619_gmu.bin` is **not** in linux-firmware's `WHENCE` [M]. Fetched
`WHENCE` (11,885 lines) and grepped: the `qcom/*_gmu.bin` entries are
`a623, a630, a640, a650, a660, a663` plus the `gen70500/71300/71500/71600/
71700/80000/80200/80100/81100/81400` Gen7/8 series. **No `a615`, `a618` or
`a619` GMU blob exists there.** So this microcode is device-vendor-only,
exactly like the `crbtfw20.tlv`/`crnv20.bin` quartet in the QCA BT work —
same structural situation, different subsystem. One consequence: a free
reimplementation cannot source a reference image from the standard firmware
package; it must come from a vendor tree (as this one did).

Context for the present ones [S, from WHENCE]:
`a623 v3.06.01`, `a630` (no version), `a640 v1.05`, `a650 v2.1.8`,
`a660 v3.01.0A`, `a663 v3.05.01`.

## 3. The layout, established

Everything below is [M] unless marked. File offsets are decimal-hex; load
addresses follow the driver's model `itcm_base = 0x0`,
`dtcm_base = 0x40000`, each `SZ_16K` [S `a6xx_gmu.c:886-887`].

```
file offset      load address      content
0x00000-0x00004  0x00000           initial SP = 0x00043f80
0x00004-0x00008  0x00004           Reset vector = 0x00000009 (Thumb)
0x00008-0x00020  0x00008           reset stub (18 bytes; see 3.1)
0x00020-0x00030  0x00020           literal pool: SP, PSP, 0x200, 0xe000ed08
0x00030-0x000D0  0x00030           10 fault/trap counter stubs
0x000D0-0x00200  0x000D0           early code, sparse, zero-padded
0x00200-0x00340  0x00200           Cortex-M vector table (16 + 64 entries)
0x00340-0x03E90  0x00340           microcode body (dense Thumb-2)
0x03E90-0x03EA4  0x03E90           tail code + literal
0x03EA4-0x03EE4  0x03EA4           region descriptor table (8 pairs)
0x03EE4-0x04000  0x03EE4           zero pad to ITCM boundary
0x04000-0x04010  0x40000           DTCM header (2 halfwords + zeros)
0x04040-0x04100  0x40040           DTCM config words
0x04100-0x044D8  0x40100           all zero
0x044D8-0x04668  0x404D8           50 x {addr, value} pairs, values all 0
0x04668-0x08000  0x40668           zero to EOF (14,744 B)
```

### 3.1 The reset stub — the piece that proves the ISA and the layout

Bytes at `0x08`, decoded by hand from ARMv7-M encodings [M, plus ARM DDI 0403
for the encodings]:

```
0x08  4805        ldr  r0,[pc,#0x14]     ; PC=0x0c -> lit@0x20 = 0x00043f80
0x0a  f380 8808   msr  msp,r0
0x0e  4805        ldr  r0,[pc,#0x14]     ; -> lit@0x24 = 0x00041440
0x10  f380 8809   msr  psp,r0
0x14  4804        ldr  r0,[pc,#0x10]     ; -> lit@0x28 = 0x00000200
0x16  4905        ldr  r1,[pc,#0x14]     ; -> lit@0x2c = 0xe000ed08
0x18  6008        str  r0,[r1,#0]        ; *SCB->VTOR = 0x200
0x1a  f000 b9f1   b.w  0x400
0x1e  bf00        nop
```

Every literal resolves; the `b.w` immediate decodes to **+994 → target
0x400**, which is inside ITCM and is where the dense code begins. `0xe000ed08`
is `SCB->VTOR` in the ARMv7-M System Control Space [ARM DDI 0403]. This one
32-byte window does four things at once: it identifies the core class, it
confirms `u32[0]` is an SP, it confirms the vector table lives at `0x200`,
and it explains the `0x200` constant the lead flagged.

**This is an ARMv7-M Cortex-M-class image — stated as a hypothesis supported
by these encodings, which is the honest strength of the claim.** It is not
read off any vendor document.

### 3.2 The vector table at 0x200 — self-consistency anchor

16 architectural vectors + 64 external entries, `0x200-0x340` [M]:

| idx | name | value | idx | name | value |
|---|---|---|---|---|---|
| 0 | Initial SP | `0x00043f80` | 11 | SVCall | `0x000000a1` |
| 1 | Reset | `0x00000009` | 12 | DebugMonitor | `0x00000041` |
| 2 | NMI | `0x00000081` | 13 | Reserved | 0 |
| 3 | HardFault | `0x00000051` | 14 | PendSV | `0x00000091` |
| 4 | MemManage | `0x00000071` | 15 | SysTick | `0x000000b1` |
| 5 | BusFault | `0x00000031` | 16-79 | IRQ0-63 | all `0x00000061` |
| 6 | UsageFault | `0x000000c1` | | | |

Two independent checks pass:
- word 0 **equals the SP the stub loaded** — a real Cortex-M vector table must.
- every handler value is **odd** (Thumb bit set) and points into the low ITCM
  region where the trap stubs at `0x30-0xC8` actually sit.

All 64 external interrupts collapse onto **one** handler (`0x61`) [M] — the
microcode does not use discrete IRQ dispatch.

### 3.3 The trap stubs at 0x30 — a 10-entry array

Ten 16-byte stubs, offsets `0x30,0x40,…,0xC0` (the handler targets above):
`ldr r0,[pc,#8]; ldr r1,[r0,#0x10]; adds r1,#1; str r1,[r0,#0x10]; b .;
<literal>`, all literals `0x00041200` [M]. A fault handler that increments a
counter in DTCM and then hangs — i.e. **each vector latches a distinct
counter at the same base**. Which counter is which vector is [OPEN]; the
`ldr r1,[r0,#0x10]` displacement is identical in all ten, so the distinction
is in the vector index, not the code.

### 3.4 The region descriptor table at 0x3EA4

8 pairs of ascending `{start, end}` addresses, `0x3EA4-0x3EE4` [M]:

`0x406cc→0x42000`, `0x404→0x43c`, `0x40000→0x41200`, `0x244→0x458`,
`0x406cc→0x41e00`, `0x16c→0x458`, `0x40ad0→0x43f80`, `0x4→0x458`

Every value is either an ITCM address (`< 0x4000`) or a DTCM address
(`0x40000-0x44000`), the pairs are strictly ascending, and the regions
alternate DTCM/ITCM. This is structurally a **memory-region descriptor
table** — 8 regions, retry/limit-style pairs. Semantics **[OPEN]**: nothing
in public source names it.

### 3.5 The DTCM address table at 0x44D8

50 entries, stride 8, `{address, value}` with **every value zero** [M].
Addresses span `0x44000060-0x44034008` — inside the `0x44000000` window that
the microcode's own code uses as a register base. 49 distinct addresses
(`0x4402381c` appears twice). Structurally a **register initialisation
table** (address + zero initial value). **[OPEN]**: which peripheral block
`0x44000000` denotes.

### 3.6 The DTCM header at 0x4000

`0x4002: 0x1011`, `0x4004: 0x3d79` [M]. On `a630_gmu.bin` the same slots read
`0x1006` / `0x3d61` [M] — so the first halfword **differs between the two
builds** and is plausibly a build/revision id; the second also differs. No
public source names either field. **[OPEN]** — and note this is the only
place in the file where a build identifier could plausibly live, which
matters for §4.

## 4. Strings — including the version question, answered negatively

193 printable ASCII runs ≥4 chars, **zero UTF-16LE runs** [M]. Almost all are
incidental instruction-byte coincidences (`"HAhI"`, `")F F"`, `"pG"`), which
is expected in dense Thumb-2 and is itself evidence the region is code.

**Exactly one semantic string** [M]:

```
0x00634  "SIGABRT: Abnormal termination"
```

Null-terminated, embedded in the code stream at a `str`/literal site — an
assert/abort path banner. It is the sole human-readable message in the image.

**The GMU firmware version is NOT in this file.** The driver prints
`"Loaded GMU firmware v%u.%u.%u"` [S `a6xx_gmu.c:934-938`], but it reads
`REG_A6XX_GMU_CORE_FW_VERSION` — a **register** at `0x1d3f8` with
MAJOR/MINOR/STEP bitfields [S `a6xx_gmu.xml:55-58`] — populated by the
microcode **at runtime**. There is no version string to find, and its absence
is correct behaviour, not a parsing failure. Corroborating detail: the exact
word the driver reads to choose its init handshake, `DTCM_START + 0xff8`,
coincides numerically with `GMU_CORE_FW_VERSION` [S; verified
`0x1c400 + 0xff8 == 0x1d3f8`], and the corresponding file word
(DTCM+0xff8 = file `0x4ff8`) is `0x00000000` [M] — i.e. zero in the image,
produced at runtime.

**Also absent: any `0xefbeadde`/`0xdeadbeef` container marker** [M]. The
sibling container files carry 8-14 of them; a619 and a630 carry **zero**.
A cheap, decisive discriminator, and the probe reports it.

## 5. Entropy map — code vs data, cleanly separated

Whole-file 3.87 bits/byte, which is meaningless on its own; the split is the
finding [M]:

| region | file range | bytes | entropy | zero % |
|---|---|---|---|---|
| ITCM (all) | `0x0000-0x4000` | 16,384 | **6.34** | 16.9 |
| — startup stub | `0x0000-0x0020` | 32 | 3.76 | 18.8 |
| — vector table | `0x0200-0x0340` | 320 | 1.10 | 75.9 |
| — code body | `0x00D0-0x3E90` | 15,808 | **6.41** | 15.2 |
| — descriptor table | `0x3E90-0x3EF0` | 96 | 3.13 | 47.9 |
| DTCM (all) | `0x4000-0x8000` | 16,384 | **0.15** | 98.8 |
| — address table | `0x44D8-0x4668` | 400 | 2.69 | 56.2 |

512-byte block profile: `0x0400-0x3E00` sits at **5.5-6.5** bits (uniform
code), then `0x3E00` drops to 2.95, `0x4000` to 0.50, and **0x4200 onward is
exactly 0.00 for 30 consecutive blocks** (15 KB of zeros, `0x4668-0x8000`).
The ITCM/DTCM boundary at `0x4000` is sharp in the entropy profile — one of
the cleanest code/data splits in the program so far. 6.41 bits is consistent
with Thumb-2 code (dense but not compressed); it is well above the 6.85-6.91
seen on the QCA BT patch bodies, consistent with a different toolchain.

## 6. Thumb-2 census — and how strong the ISA claim is

Region `0x340-0x3E90` (the body, excluding the vector table and tables),
7,592 halfwords [M]. Counted by exact bit-mask match on the 16-bit encodings,
each of which is a one-line predicate from the ARMv7-M ARM:

| encoding | count | rate |
|---|---|---|
| `bl`/`blx` prefix (`0xF0xx`/`0xF8xx`) | 1,539 | 20.3% |
| `movs Rd,#imm8` | 765 | 10.1% |
| `str Rt,[Rn,#imm5]` | 566 | 7.5% |
| `ldr Rt,[pc,#imm8]` | 496 | 6.5% |
| `ldr Rt,[Rn,#imm5]` | 465 | 6.1% |
| `b<cond>` | 282 | 3.7% |
| `mov Rd,Rm` | 147 | 1.9% |
| `push {…,lr}` | 129 | 1.7% |
| `pop {…,pc}` | 104 | 1.4% |
| `bx lr` | 49 | 0.6% |
| `b .` (infinite loop) | 2 | 0.03% |
| `nop` | 0 | 0.0% |

Reading: a normal compiled Cortex-M function mix — call-heavy (20% `bl`
prefixes), immediate-heavy, with matched `push {…,lr}` / `pop {…,pc}` at
roughly 1:0.8. The ten `b .` sites are the trap stubs; `nop` appears in the
stub area but not in the body (padding is zeros, not `nop`).

**Honest strength of the ISA claim.** The 16-bit predicates above are exact,
but this is a *census over a 2-byte stride*, not a disassembly: halfwords
belonging to the second half of a 32-bit Thumb-2 instruction, and immediate
data that happens to match a pattern, are counted too. So the **rates are
approximate**, and no instruction-level meaning is claimed for any specific
site. What *is* established beyond reasonable doubt: the vector table
(§3.2), the reset stub (§3.1, every encoding hand-verified and every literal
resolving), and the `0xbabeface` constant (§6.1). Those three are decoded,
not inferred.

### 6.1 An independent corroboration: the driver's init magic is in the code

`a6xx_gmu.c:311-318` polls for `0xbabeface` in `GMU_CM3_FW_INIT_RESULT`
after reset [S]. That constant occurs **twice** in the microcode's own code,
at file `0x1AF4` and `0x2EC8` [M] — i.e. the image contains the literal it is
expected to report back. This closes the loop between the public driver and
the payload without reading a single instruction's semantics: the driver
documents a handshake value, and the firmware carries it.

## 7. What this buys a free reimplementation

**Specified and writable today, with zero proprietary bytes:**

- The **load contract**: 32,768 B, image = ITCM[0,0x4000) then
  DTCM[0x4000,0x8000), bulk-written to `GMU_CM3_ITCM_START`; ≤ `0x8000` or
  the driver refuses [S]. A replacement must produce this shape.
- The **entry contract**: u32[0] = initial SP inside DTCM at top−0x80;
  u32[1] = odd (Thumb) Reset vector inside ITCM; a stub that sets
  `SCB->VTOR` to an in-image Cortex-M table whose word 0 repeats the SP.
- The **handshake contract**: `0xbabeface` in `FW_INIT_RESULT`, and
  `DTCM+0xff8` = 0 to select the legacy branch [S+M].
- The **runtime tables**: vector table (16+64), region descriptor pairs,
  DTCM address/zero-value table — all enumerated above with offsets.

**Opaque — needs synthesis or further RE:**

- The ~15.8 KB Thumb-2 body: what any function *does*. This is the bulk of
  the work for a functional replacement and is not attempted here [OPEN].
- The DTCM header halfwords at `0x4002` (build id?) [OPEN].
- The `0x44000000` register window's identity [OPEN].
- The region descriptor table's semantics [OPEN].

**Program-level:** the RE surface went from "a 32 KB opaque blob" to "a
two-window memory image with a fully specified load/entry/init contract, an
enumerated vector table, two enumerated runtime tables, and one opaque code
body". The format question — the one that gates any reimplementation — is
**answered**, and answered negatively in a useful direction: a619 does not
need a container parser at all.

## 8. [OPEN] list

1. **[OPEN]** Microcode body semantics (`0x340-0x3E90`) — what the functions
   compute. Not attempted; would need real disassembly, which is out of scope
   for a clean-room pass.
2. **[OPEN]** DTCM+0x02 halfwords (`0x1011`/`0x3d79` on a619,
   `0x1006`/`0x3d61` on a630). Differ per build; plausibly a version; unnamed
   in public source.
3. **[OPEN]** Region descriptor table at `0x3EA4` — 8 ascending
   `{start,end}` TCM pairs. Structure clear, meaning not.
4. **[OPEN]** DTCM `{addr, 0}` table at `0x44D8` — 50 entries; which
   peripheral block `0x44000000` is, and why all values are zero.
5. **[OPEN]** Trap-stub counter mapping — all 10 stubs use the same DTCM base
   `0x41200` and same displacement; which vector increments which counter is
   not determinable from the stubs alone.
6. **[OPEN]** Whether the 26-device fleet is byte-identical across *all* vendor
   trees, or whether on-device builds differ from this LineageOS-sourced copy.
   The DB md5 is one value for 26 rows, but only one vendor tree was fetched,
   and §1.2 shows vendor vs packaged builds of the same filename already differ.
7. **[OPEN]** a618 vs a619 attribution: the same bytes ship under both names;
   whether any device ships a *different* a618/a619 image is not established
   (the DB records exactly one md5).
8. **[OPEN]** Occupancy of the 13 live devices vs the 26 byte-sharing rows: the
   co-residency classification (§2.2) rests on the DB `soc` column and mainline
   `revn` bindings. Two devices (`Edge_20`, `Edge_2021`, both SM7325) keep their
   `a619` only because no competing GMU blob is present; SM7325 has no mainline
   catalog entry at all, so their support status is unestablished.
8. **[OPEN]** `SIGABRT: Abnormal termination` at `0x634` — the abort path it
   guards is not identifiable without body RE.

## 9. Scratch artifacts (regeneratable)

- `/tmp/astro_u/payloads/a619_gmu.bin` — verified payload (md5 9e23c520…).
- `/tmp/astro_u/peers/*.bin` — the six linux-firmware siblings compared in §1.3.
- `/tmp/astro_u/kernelsrc/` — the fetched GPL sources (`a6xx_gmu.c/.h/.xml`,
  `adreno_gpu.h`, `a6xx_catalog.c`, `a6xx_gpu.c`, plus v5.4/5.10/5.15/6.1
  `a6xx_gmu.c/.h` for the history check in §1.1).
- `/tmp/astro_u/WHENCE` — linux-firmware manifest used for §2.1.
- Probe reports: `--json` output from `gmu_probe.py`.
- Payload bytes are NOT committed (repo policy).

## 10. RULE 0 route log (2026-11-18)

1. `raw.githubusercontent.com` for torvalds/linux was rate-limited from this
   network (HTTP 429 / short HTML body), as the lead warned. Switched to
   authenticated `gh api "repos/torvalds/linux/contents/<path>?ref=<ref>" --jq
   .content | base64 -d`; every fetched file verified to be real C (SPDX
   header + `#include`) before use. All kernel citations above come from that
   route.
2. History check for the `a6xx_gmu_fw_header` premise: fetched `a6xx_gmu.h` at
   `v5.4`, `v5.10`, `v5.15`, `v6.1`, `master` — 0 occurrences at every ref.
   Authenticated code search `a6xx_gmu_fw_header` → `total_count: 0`.
3. Register documentation: `a6xx.xml.h` no longer exists at master (404); the
   register definitions moved to `drivers/gpu/drm/msm/registers/adreno/
   a6xx_gmu.xml`, which is where `GMU_CM3_ITCM_START`, `GMU_CM3_DTCM_START`
   and `GMU_CORE_FW_VERSION` were read from.
4. linux-firmware siblings: fetched six `qcom/*_gmu.bin` from
   `git.kernel.org/.../linux-firmware.git/plain/`; md5s recorded in §1.3.
   `WHENCE` fetched from the same tree for the absence finding (§2.1).
5. Negative recorded honestly: no public source names the DTCM header fields,
   the region descriptor table, or the `0x44000000` window. Those stay [OPEN]
   rather than being guessed.
6. Prior art: this component's `gmu_probe.py` was already committed on branch
   `main` (commit `4b1a547`, prior F-76 batch) with the same RULE-0 reading of
   `struct block_header` and the legacy raw path. This session's contribution
   is the *content-level* measurement layer on top of it: the fleet-count
   verification, the linux-firmware sibling comparison (§1.3), the
   linux-firmware absence finding (§2.1), the string/version negative result
   (§4), the entropy and census tables (§5-6), the `0xbabeface` corroboration
   (§6.1), and the synthetic-fixture + test suite.
