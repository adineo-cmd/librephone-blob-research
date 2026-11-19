# Qualcomm Adreno `a619_gmu.bin` — content-level RE: no header, a raw ITCM+DTCM image, and a corrected occupancy count

Analysis date: 2026-11-19 (payload work 2026-11-18). Evidence class: **MEASURED PAYLOADS** — every
number below is computed from bytes on disk or quoted from public GPL kernel source. Nothing is
copied from a manifest except the explicitly-labelled DB row counts, which are re-derived.

Companion documents:

| document | owns |
|---|---|
| **`qualcomm-adreno-gmu.md`** (this directory) | the metadata matrix: 5 laptop-half devices, md5/size |
| **`../../implementations/adreno-fleet/gmu-analysis.md`** | the full analysis: per-byte-range map, ISA evidence, entropy/census tables, [OPEN] list |
| `../../implementations/adreno-fleet/gmu_probe.py` | the probe. `python3 -I gmu_probe.py <file> --brief` |
| `../../implementations/adreno-fleet/README.md` | usage, fixture/test instructions |

This file owns the **content-level result summary** and the **occupancy correction** (§5, which
contradicts the device count implied by the metadata matrix — read that section even if you read
nothing else).

Primary payload: `a619_gmu.bin`, **32,768 B**, md5 `9e23c52057bb573dee9ba31f1fdba4fa`,
sha256 `9ef10b2b179054fb57af25008e29feb24300c2eaaeabf907bd741786bbacbf2e`.
md5 re-verified this session against the upstream DB. Bytes live only in `/tmp/astro_u/payloads/`;
no proprietary content is committed.

Labels used throughout: **[S]** quoted from public GPL source (file:line) · **[M]** my own
measurement of payload bytes · **[OPEN]** not established, gap named.

---

## 1. Headline: the file has no header, and that is the documented behaviour

The premise that Adreno GMU firmware begins with a documented `struct a6xx_gmu_fw_header` is
**false**. Fetched via authenticated `gh api` (2026-11-18) and grepped: `a6xx_gmu.h` has **0**
occurrences of `fw_header` at `v5.4`, `v5.10`, `v5.15`, `v6.1` and `master`; an authenticated code
search returns `total_count: 0`.

What mainline actually documents is a *container*, and — this is the deciding fact — **a619 never
goes through it** [S]:

```c
/* drivers/gpu/drm/msm/adreno/a6xx_gmu.c:894-904 */
	if (gmu->legacy) {
		/* Sanity check the size of the firmware that was loaded */
		if (fw_image->size > 0x8000) { ... return -EINVAL; }
		gmu_write_bulk(gmu, REG_A6XX_GMU_CM3_ITCM_START,
			       (u32*) fw_image->data, fw_image->size);
		return 0;
	}
```

`gmu->legacy` is set for `ADRENO_6XX_GEN1` (`a6xx_gmu.c:2412-2414`), and a619 is `ADRENO_6XX_GEN1`
with `.revn = 619` on all three of its catalog entries (`a6xx_catalog.c:872-876` sm4350,
`:898-901` sm6375, `:920-925` chip-id-only). The loader performs **no parsing at all** — one size
bound, then a bulk DMA of the whole file. There is no header because nothing looks for one.

Running mainline's own walk (`struct block_header`, `a6xx_gmu.c:857-863`) on the bytes confirms it
negatively [M]: the first record reads `addr=0x00043f80 size=0x00000009` and the chain overflows
the file immediately. `size = 9` is the raw Thumb byte `0x09` of a branch, not a length.

**Verdict: flat memory image, not a container.** Size cap `0x8000` = ITCM(`0x4000`) +
DTCM(`0x4000`) exactly — the file is two 16 KiB TCM images laid end to end, not "32 KiB of code".

### 1.1 Corroborated against the sibling generation

Same walk, run on the linux-firmware siblings fetched from
`git.kernel.org/.../linux-firmware.git/plain/qcom/<name>` [M]:

| file | bytes | md5 | walk |
|---|---|---|---|
| `a623_gmu.bin` | 53,516 | `7906b8a180c11d48d882bb9ff5c90ba5` | exact EOF (15 records) |
| `a640_gmu.bin` | 37,680 | `99d0c614ab7ca1e4f5ab9281aaee2f11` | exact EOF (7) |
| `a650_gmu.bin` | 41,548 | `a2b9504e3d1cb8686ae7fcca21a11e1a` | exact EOF (16) |
| `a660_gmu.bin` | 55,252 | `cd3a235218418f51360888637c1cb2ac` | exact EOF (15) |
| `a663_gmu.bin` | 55,892 | `bcd60be9a312caf37e3575776c0a4d3f` | exact EOF (15) |
| `a630_gmu.bin` | 32,768 | `ab20135f7adf48e0f344282a37da80e4` | **overflow** |
| **`a619_gmu.bin`** | **32,768** | **`9e23c52057bb573dee9ba31f1fdba4fa`** | **overflow** |

The split is exactly the `gmu->legacy` boundary: every `6XX_GEN1` file is raw, every GEN2+ file is a
container. `a630` (also GEN1, also 32,768 B) fails the walk identically. **The format boundary is
the load path, not the filename.**

### 1.2 linux-firmware absence — a second F-74-class finding

`a619_gmu.bin` is **not** in linux-firmware. `WHENCE` (11,885 lines, fetched this session) lists
`qcom/*_gmu.bin` as `a623, a630, a640, a650, a660, a663` plus the `gen70500`–`gen81400` series —
**no `a615`, `a618` or `a619`**. So a free reimplementation cannot source a reference image from
the standard firmware package; it must come from a vendor tree, as this one did.

Recorded `WHENCE` versions for context [S]: `a623 v3.06.01`, `a630` (none), `a640 v1.05`,
`a650 v2.1.8`, `a660 v3.01.0A`, `a663 v3.05.01`.

Note also that **this payload's md5 is not a linux-firmware md5** even where a same-named file
exists: DB `a630_gmu.bin` is `1ade6a659713b4424a27eb2afd70d614` (8 rows) vs linux-firmware's
`ab20135f7adf48e0f344282a37da80e4`; DB `a660_gmu.bin` at 55,256 B is
`179caf2e3b7d5481c3567c2987f5be32` (19 rows) vs linux-firmware's 55,252 B
`cd3a235218418f51360888637c1cb2ac`. Vendor builds and the packaged blob are **not** the same bytes.

---

## 2. `0x43f80` — settled: initial stack pointer, not a load address or magic

The lead flagged `0x43f80` appearing at u32[0] and again at u32[8]. It is the **ARMv7-M initial
stack pointer**, and four independent facts settle it [M]:

1. It lies inside the DTCM window: `0x40000 ≤ 0x43f80 < 0x44000`.
2. It equals **DTCM top − 0x80** exactly (`0x44000 − 0x80`) — the conventional reserved slot below
   a Cortex-M vector table.
3. The reset stub **loads it into MSP**, and the vector table it points `VTOR` at repeats the same
   value as word 0 — which is the ARMv7-M contract, and is why the value appears twice.
4. `0x8000` is separately explained as the loader cap, not a size field.

The decisive single piece is the reset stub at `0x08`, hand-decoded from ARMv7-M encodings [M]:

```
0x08  4805        ldr  r0,[pc,#0x14]   ; -> lit@0x20 = 0x00043f80
0x0a  f380 8808   msr  msp,r0
0x0e  4805        ldr  r0,[pc,#0x14]   ; -> lit@0x24 = 0x00041440  (PSP)
0x10  f380 8809   msr  psp,r0
0x14  4804        ldr  r0,[pc,#0x10]   ; -> lit@0x28 = 0x00000200
0x16  4905        ldr  r1,[pc,#0x14]   ; -> lit@0x2c = 0xe000ed08  (SCB->VTOR)
0x18  6008        str  r0,[r1,#0]      ; *VTOR = 0x200
0x1a  f000 b9f1   b.w  0x400
0x1e  bf00        nop
```

Every literal resolves; `b.w` decodes to target `0x400`, where the dense code begins. This 24-byte
window simultaneously identifies the core class, confirms u32[0] is an SP, and locates the vector
table. `0xe000ed08` is `SCB->VTOR` per ARM DDI 0403.

---

## 3. Layout map

Load addresses follow the driver's model: `itcm_base = 0x0`, `dtcm_base = 0x40000`, each `SZ_16K`
[S `a6xx_gmu.c:886-887`]. The `0x4000` split is *forced* by the register map — `GMU_CM3_ITCM_START`
(`0x1b400`) and `GMU_CM3_DTCM_START` (`0x1c400`) are exactly `SZ_16K` apart
[S `a6xx_gmu.xml:45-46`], verified `0x1c400 − 0x1b400 = 0x1000` dwords = `0x4000` bytes.

```
file offset       load addr     content
0x00000-0x00004   0x00000       initial SP = 0x00043f80
0x00004-0x00008   0x00004       Reset vector = 0x00000009 (Thumb)
0x00008-0x00020   0x00008       reset stub (§2)
0x00020-0x00030   0x00020       literal pool: SP, PSP, 0x200, 0xe000ed08
0x00030-0x000D0   0x00030       10 fault/trap counter stubs
0x000D0-0x00200   0x000D0       early code, sparse
0x00200-0x00340   0x00200       Cortex-M vector table (16 architectural + 64 IRQ)
0x00340-0x03E90   0x00340       microcode body (dense Thumb-2)
0x03E90-0x03EA4   0x03E90       tail code + literal
0x03EA4-0x03EE4   0x03EA4       region descriptor table (8 {start,end} pairs)
0x03EE4-0x04000   0x03EE4       zero pad to ITCM boundary
0x04000-0x04010   0x40000       DTCM header: 0x1011 / 0x3d79
0x04040-0x04100   0x40040       DTCM config words
0x04100-0x044D8   0x40100       all zero
0x044D8-0x04668   0x404D8       50 x {addr, value} pairs, every value 0
0x04668-0x08000   0x40668       zero to EOF (14,744 B)
```

### 3.1 The vector table anchors the whole model

`0x200-0x340`, 16 architectural + 64 external entries. Two independent checks pass [M]:

- **word 0 equals the SP the stub loaded** (`0x00043f80`) — a real Cortex-M vector table must.
- every handler value is **odd** (Thumb bit) and points into the low ITCM where the trap stubs at
  `0x30-0xC8` actually are.

All **64 external interrupts collapse onto one handler** (`0x61`) — the microcode does not use
discrete IRQ dispatch.

### 3.2 The ten trap stubs at `0x30`

Ten 16-byte stubs at `0x30, 0x40, …, 0xC0` (matching the vector targets), each
`ldr r0,[pc,#8]; ldr r1,[r0,#0x10]; adds r1,#1; str r1,[r0,#0x10]; b .; <literal>`, all literals
`0x00041200` [M]. A fault handler that bumps a counter in DTCM then hangs. Which vector maps to
which counter is **[OPEN]** — the code is identical in all ten, so the distinction is in the vector
index, not the stub.

### 3.3 Region descriptor table at `0x3EA4` — 8 ascending pairs

| # | start | end | region |
|---|---|---|---|
| 0 | `0x000406cc` | `0x00042000` | DTCM |
| 1 | `0x00000404` | `0x0000043c` | ITCM |
| 2 | `0x00040000` | `0x00041200` | DTCM |
| 3 | `0x00000244` | `0x00000458` | ITCM |
| 4 | `0x000406cc` | `0x00041e00` | DTCM |
| 5 | `0x0000016c` | `0x00000458` | ITCM |
| 6 | `0x00040ad0` | `0x00043f80` | DTCM |
| 7 | `0x00000004` | `0x00000458` | ITCM |

Every value is an ITCM (`< 0x4000`) or DTCM (`0x40000-0x44000`) address, the pairs are strictly
ascending, the regions alternate, and pair 6's end is **`0x43f80` — the initial SP**. Structurally
a memory-region descriptor table. Semantics **[OPEN]**; no public source names it.

### 3.4 DTCM `{addr, 0}` table at `0x44D8`

50 entries, stride 8, **every value zero**, 49 distinct addresses (`0x4402381c` twice), spanning
`0x44000060-0x44034008` [M] — the `0x44000000` window the microcode's own code uses as a register
base. Structurally a register-initialisation table (address + zero init). **[OPEN]**: which
peripheral block `0x44000000` denotes.

### 3.5 DTCM header at `0x4000` — the only plausible build id

`0x4002: 0x1011`, `0x4004: 0x3d79` on a619; **`0x1006` / `0x3d61`** on a630 [M]. Both halfwords
differ between builds, so this is the only place in the file where a build identifier could
plausibly live. Unnamed in public source. **[OPEN]**

---

## 4. What the file does *not* contain

Results that are as useful as the positive ones:

| claim | result | basis |
|---|---|---|
| a GMU firmware version string | **absent — and correctly so** | [S]+[M] |
| any UTF-16 string | **0 runs** | [M] |
| container markers `0xefbeadde`/`0xdeadbeef` | **0 occurrences** | [M] |
| semantic strings | **exactly 1** | [M] |

**The version is a register, not a file field.** The driver prints `"Loaded GMU firmware
v%u.%u.%u"` [S `a6xx_gmu.c:934-938`] but reads `REG_A6XX_GMU_CORE_FW_VERSION` — a register at
`0x1d3f8` with MAJOR/MINOR/STEP bitfields [S `a6xx_gmu.xml:55-58`] — which the microcode populates
**at runtime**. Its absence from the file is correct behaviour, not a parsing failure.

**Marker absence is itself the discriminator.** The sibling containers carry 8–14 `0xdeadbeef`
words; a619 and a630 carry **zero**. A cheap decisive test the probe reports as `no-container-markers`.

The **one** semantic string [M]:

```
0x00634  "SIGABRT: Abnormal termination"
```

Null-terminated, embedded at a literal site in the code — an assert/abort banner. The other 192
printable runs ≥4 chars are instruction-byte coincidences (`"HAhI"`, `")F F"`), which is itself
evidence the region is dense code.

**A cross-check that closes the loop with the public driver:** `a6xx_gmu.c:311-318` polls for
`0xbabeface` in `GMU_CM3_FW_INIT_RESULT` after reset [S]. That constant occurs **twice** in the
microcode's own code, at file `0x1AF4` and `0x2EC8` [M] — the image carries the handshake value the
driver documents. Corroborating: the word the driver reads to pick its branch, `DTCM_START + 0xff8`,
is numerically exactly `GMU_CORE_FW_VERSION` (verified `0x1c400 + 0xff8 == 0x1d3f8`), and the
corresponding file word is `0x00000000` [M] — zero in the image, produced at runtime, which selects
the legacy `0xbabeface` handshake.

---

## 5. Occupancy correction — the 26-device figure is a *byte* footprint, not 26 Adreno-619 devices

**This corrects the leverage claim implied by the metadata matrix.** The byte footprint is genuinely
26 DB rows / 26 devices for md5 `9e23c520…` [M, re-derived from `coverage-matrix.csv`]. But a
device *carrying* the file is not a device that *runs* it.

Mechanism: `a619_gmu.bin` must only be loaded by hardware mainline models as `revn = 619`
(`a6xx_catalog.c:872-876, 898-901, 920-925`, all `ADRENO_6XX_GEN1`). On a device whose GPU is an
Adreno 650 or 660 — different `revn`, different family — the driver requests `a650_gmu.bin` /
`a660_gmu.bin` and the `a619` copy is a **co-resident leftover** from a shared BSP firmware
directory, never loaded.

Grouping the 26 by the SoC recorded in the DB [M]:

| class | devices | what it means |
|---|---|---|
| SoC is Adreno-619-class (SM4350/SM4375/SM6375/SM7225) | **11** | live — mainline revn 619 |
| `a619` is the *only* GMU blob on the device (SoC field unrecorded) | **2** | live — nothing else to load (`Edge_20`, `Edge_2021`, both SM7325) |
| co-resident with `a650`/`a660`, **not** 619-class | **11** | **not loaded** |
| `a618` alias rows (carry `a630`/`a640`, not 619-class) | **2** | **not loaded** (`Galaxy_A71`, `Mi_A3`) |
| **total** | **26** | — |
| **live union** | **13** | 11 + 2 |

The 13 non-live devices carry the bytes but never load them. Eleven are co-resident with an
`a650`/`a660` build — `Edge_30`, `Edge_30_Fusion`, `G_Stylus_5G-2-2022`, `Moto_G200`,
`Moto_G_Stylus_5G`, `Pixel_4A_5G`, `Pixel_5`, `Pixel_5A`, `Xperia_1_II`, `Xperia_5_II`,
`Xperia_5_III` — and two are the `a618` alias rows `Galaxy_A71` and `Mi_A3` (11 + 2 = 13).

The two "orphan" devices still count as live: `Edge_20` and `Edge_2021` are SM7325
(Adreno 642L-class), but with **no competing GMU blob present** the `a619` file is the only
candidate — hence 13 live, not 11. Their mainline support status is separately **[OPEN]** (§8.9).

Devices where `a619` is **not** the operative image (co-resident with a 650/660 build):
`Edge_30`, `Edge_30_Fusion`, `G_Stylus_5G-2-2022`, `Galaxy_A71`, `Mi_A3`, `Moto_G200`,
`Moto_G_Stylus_5G`, `Pixel_4A_5G`, `Pixel_5`, `Pixel_5A`, `Xperia_1_II`, `Xperia_5_II`,
`Xperia_5_III`.

The `a618` alias rows are the same story: `Galaxy_A71` carries `a618` **plus** `a630`, and mainline
binds `a630_gmu.bin` to `revn = 618` / sm7150 (`a6xx_catalog.c:846-852`) — not `a619`. `Mi_A3`
carries `a618` + `a630` + `a640`.

**So: one RE pass informs 13 devices, not 26.** The `26` remains correct as "how many DB rows share
these exact bytes" (and it is the right number for dedup/bandwidth accounting); it is wrong as
"how many devices this firmware runs on". Both numbers are recorded here because the distinction is
the finding, and it is a correction to work already in the tree.

### 5.1 The laptop-half 5, classified

`blob-matrix/laptop/qualcomm-adreno-gmu.md` lists five devices; 7 laptop-half devices carry this
md5 (the 5 plus the `a71`/`laurel_sprout` alias rows):

| device | build | SoC (DB) | GMU blobs present | live? |
|---|---|---|---|---|
| `realme/Realme_10_Pro` | luigi | SM6375 | a619, a660 | **yes** — 619-class |
| `realme/Realme_9_Pro` | oscar | SM6375 | a619, a660 | **yes** — 619-class |
| `sony/Xperia_1_II` | pdx215 | *(unrecorded)* | a619, a650 | **no** — co-resident |
| `sony/Xperia_5_II` | pdx206 | SM8250 | a619, a650 | **no** — co-resident |
| `sony/Xperia_5_III` | pdx214 | SM8350 | a619, a660 | **no** — co-resident |

The laptop-half *live* count is **2**, not 5. The `pdx215` SoC field is `\N` in the DB; the
co-resident `a650_gmu.bin` on it is the evidence, and `a650` is bound to `revn = 650`
(`a6xx_catalog.c`). Recorded as a DB gap rather than guessed.

---

## 6. Entropy and instruction census (summary)

Whole-file 3.87 bits/byte is meaningless alone; the split is the finding [M]:

| region | range | bytes | entropy | zero % |
|---|---|---|---|---|
| ITCM (all) | `0x0000-0x4000` | 16,384 | **6.34** | 16.9 |
| — startup stub | `0x0000-0x0020` | 32 | 3.76 | 18.8 |
| — vector table | `0x0200-0x0340` | 320 | 1.10 | 75.9 |
| — code body | `0x0340-0x3E90` | 15,184 | **6.53** | 12.4 |
| DTCM (all) | `0x4000-0x8000` | 16,384 | **0.15** | 98.8 |
| — address table | `0x44D8-0x4668` | 400 | 2.69 | 56.2 |

The `0x4000` ITCM/DTCM boundary is sharp: **15 KB of contiguous zeros** from `0x4668` to EOF
(entropy exactly 0.00 for 30 consecutive 512-B blocks).

Thumb-2 census over the body, 7,592 halfwords, exact bit-mask predicates from the ARMv7-M ARM [M]:

| encoding | count | rate |
|---|---|---|
| `bl`/`blx` prefix | 1,539 | 20.3% |
| `movs Rd,#imm8` | 765 | 10.1% |
| `str Rt,[Rn,#imm5]` | 566 | 7.5% |
| `ldr Rt,[pc,#imm8]` | 496 | 6.5% |
| `ldr Rt,[Rn,#imm5]` | 465 | 6.1% |
| `b<cond>` | 282 | 3.7% |
| `push {…,lr}` / `pop {…,pc}` | 129 / 104 | 1.7 / 1.4 |

A normal compiled Cortex-M mix: call-heavy, immediate-heavy, matched prologue/epilogue.

**Honest strength:** the 16-bit predicates are exact, but this is a *census over a 2-byte stride*,
not a disassembly — second halfwords of 32-bit Thumb-2 instructions and data literals are counted
too. The **rates are approximate**; no instruction-level meaning is claimed. What *is* established
beyond doubt is the vector table (§3.1), the reset stub (§2, every literal resolving), and the
`0xbabeface` constant (§4) — those are decoded, not inferred.

---

## 7. Implementation consequence

**Specified and writable today, zero proprietary bytes:**

- **Load contract** — 32,768 B; ITCM`[0,0x4000)` then DTCM`[0x4000,0x8000)`; bulk-written to
  `GMU_CM3_ITCM_START`; ≤ `0x8000` or the driver refuses [S].
- **Entry contract** — u32[0] = initial SP in DTCM at top−0x80; u32[1] = odd Thumb Reset vector in
  ITCM; a stub setting `SCB->VTOR` to an in-image table whose word 0 repeats the SP.
- **Handshake contract** — `0xbabeface` in `FW_INIT_RESULT`; `DTCM+0xff8` = 0 selects the legacy
  branch [S+M].
- **Runtime tables** — vector table (16+64), 8 region descriptor pairs, 50-entry DTCM address table,
  all at enumerated offsets.

**Opaque:** the ~14.8 KB Thumb-2 body (`0x340-0x3E90`; 15,808 B if measured from
`0xD0`) — what any function computes — **[OPEN]**, the bulk of a
functional-replacement effort and not attempted here.

The gating question — *does a replacement need a container parser?* — is answered **no**.

---

## 8. [OPEN]

1. **[OPEN]** Microcode body semantics (`0x340-0x3E90`). Needs real disassembly; out of scope for a
   clean-room pass.
2. **[OPEN]** DTCM+0x02 halfwords (`0x1011`/`0x3d79` vs a630's `0x1006`/`0x3d61`) — differ per
   build, plausibly a version, unnamed publicly.
3. **[OPEN]** Semantics of the 8 region descriptor pairs at `0x3EA4`.
4. **[OPEN]** Identity of the `0x44000000` window and why all 50 table values are zero.
5. **[OPEN]** Trap-stub → counter mapping (identical code in all ten stubs).
6. **[OPEN]** Whether the 13 live devices are byte-identical across *all* vendor trees. The DB
   records one md5, but only one vendor tree was fetched, and §1.2 shows vendor vs packaged builds
   of the same filename already differ.
7. **[OPEN]** `pdx215`/`Xperia_1_II` SoC is `\N` in the DB; co-residency with `a650` is the current
   evidence, not a recorded SoC.
8. **[OPEN]** The abort path guarded by `SIGABRT: Abnormal termination` at `0x634`.
9. **[OPEN]** Why SM7325 devices (`Edge_20`, `Edge_2021`) ship only a 619-class GMU blob; their
   Adreno 642L-class GPU is not in mainline's catalog at all (no `sm7325` machine, no revn 642) —
   so mainline support status for those two is unestablished.

---

## 9. Reproduce

```
cd implementations/adreno-fleet
python3 -I gmu_probe.py /tmp/astro_u/payloads/a619_gmu.bin --brief    # exit 0, 0 errors
python3 -m unittest -v test_gmu_probe                                  # 62 tests, OK
```

Fixtures are synthetic and regenerable (`make_fixture.py`); `*.bin` is gitignored per repo policy.
Payload bytes are not committed.
