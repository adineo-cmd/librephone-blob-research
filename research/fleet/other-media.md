# The `media` subfamily of `other` — Qualcomm Venus/VPU video firmware

**Issue:** #2058 · **Analysis date:** 2026-11-20 · **Evidence classes:** `[F]` measured fact
(command and output shown) · `[I]` inference from stated facts · `[N]` honest negative ·
`[U]` unresolved.

**Scope.** The 470 matrix rows classified `blob_family=other, blob_subfamily=media`:
**53 distinct devices**, 9 vendors. Two filename families: `venus.*` (371 rows) and
`vpu20_*` (99 rows).

**Artifacts read (read-only, never committed).**
`data-fetch/second-device/larry/tree-vendor/firmware/vpu20_{1v,2v,4v}.*` (66 files, SM6375
OnePlus Nord CE 3), `data-fetch/second-device/instantnoodle/modem-fat/*.MDT` (32 files,
SM8250 OnePlus 8), `data-fetch/enchilada/tree_firmware/*` (MSM8998 OnePlus 6). No payload
byte is reproduced beyond ≤16-byte hex samples.

---

## 0. Headline

1. **`[F]` This issue corrects the repository's own ISA claim, in place.** Both
   `research/qualcomm/results/census.md` and `research/qualcomm/docs/fp6-architecture-census.md`
   labelled the `vpu20/30/33_*.mbn` and `CAMERA_ICP.*` images **"RISC-V (old, bespoke)"**,
   justified in `upstream/pr5-corrections-package.md` as *"e_machine = 94, the historic
   RISC-V value used by early toolchains (243 was assigned later)"*. **`e_machine=94` is
   `EM_XTENSA`. It has never been a RISC-V value.** `EM_RISCV` is 243. All of those files
   are corrected in this change (§8); PR-5 is withdrawn, because it would have introduced
   the error into upstream text that was already right. See §2.
2. **`[F]` The census and container measurements.** 470 rows / 53 devices / 9 vendors, and
   the first measurement of the container invariants across this subfamily: the metadata
   header identity `w[4] == w[5]+w[7]+w[9]` holds on **5/5** media images, and
   `w[5] == 48 × e_phnum` on the same 5/5. See §4. §9 is explicit about which parts of
   this are prior art.
3. **`[F]` `venus` and `cvpss` are the same container on the same core**, structurally
   distinguishable only by payload size — and both carry `e_machine=94`. This crosses a
   family boundary the matrix draws. See §5.
4. **`[N]` The ISA is not proven by disassembly here.** No Xtensa disassembler exists in
   this environment; the verdict rests on registry evidence plus the kernel's reset path,
   not on decoded instructions of *this* image. See §2.4.

**What is *not* claimed.** The container is not new work. Qualcomm's own MBN/SIF
documentation describes the hash segment and its 40-byte header, mainline
`drivers/soc/qcom/mdt_loader.c` has implemented it since 2017, and `pil-splitter`,
the Rust `mbn` crate and IDA's loader all parse it. §3 credits this rather than
re-deriving it.

---

## 1. The subfamily in numbers

Command: `python3 -c` over `upstream-contribution/blob-database/coverage-matrix.csv`,
filtering `blob_subfamily=='media'`.

| measure | value |
|---|---|
| rows | 470 |
| distinct devices | 53 |
| vendors | 9 — motorola 291, oneplus 86, realme 32, fairphone 14, xiaomi 14, nothing 14, fxtec 13, google 3, sony 3 |
| distinct filenames | 40 |
| distinct `(device, filename)` pairs | 468 |
| `venus.*` rows / devices | 371 / 34 |
| `vpu20_*` rows / devices | 99 / 31 |
| devices carrying **both** families | 12 |
| `isa_identified` populated | **0 of 470** |
| `interface_documented = n` | **470 of 470** |
| priority | P3 450, P2 20 |

`[F]` Two duplicate `(device, filename)` rows exist — `vpu20_4v.mdt` harvested from two
partitions on `Moto_G200` and `Edge_30_Fusion` — which is why 470 rows yield 468 pairs.

`[F]` **Data defect.** 16 rows carry a `U+00FF` byte prefix in the `soc` field
(`ÿQualcomm SM6375 Snapdragon 695 5G`), splitting SM6375 into two apparent values
(112 + 16). The true SM6375 count is 128. This is a matrix defect, not a firmware fact.

`[N]` The matrix stores only md5, so it **cannot** answer whether `venus` and `vpu20`
payloads are content-equivalent. §5 answers that from files, not from the matrix.

`[N]` `device-inventory.csv` has `released_year` empty on every row, so no temporal
correlation is possible. The matrix has no device-class field, so "which device classes use
it" is **unanswerable from the data** — I do not invent one.

---

## 2. ISA: 94 is `EM_XTENSA`, and the repo's "historic RISC-V" is wrong

### 2.1 `[F]` The registry evidence

Four independent sources, each quoted:

| source | line | value |
|---|---|---|
| `/usr/include/elf.h` | 197 / 251 / 357 | `EM_ARM 40`, `EM_XTENSA 94`, `EM_RISCV 243` |
| gABI registry (`gabi.xinuos.com/elf/a-emachine.html`) | — | `EM_XTENSA 94`, `reserved 225–242`, `EM_RISCV 243` |
| Linux `include/uapi/linux/elf-em.h` | 38 / 51 | `EM_XTENSA 94`, `EM_RISCV 243` |
| LLVM `llvm/BinaryFormat/ELF.def` | 96 / 200 | `ELF_MACHINE(EM_XTENSA, 94, "xtensa", …)`, `ELF_MACHINE(EM_RISCV, 243, "riscv", …)` |

`readelf -h` on the artifact agrees independently:

```
Machine:                           Tensilica Xtensa Processor
Entry point address:               0xf500000
```

### 2.2 `[F]` Why "historic RISC-V 94" is chronologically impossible

- glibc 2.3.2 (**2002**) already defined `EM_XTENSA 94` — eight years before RISC-V was
  designed.
- The gABI registry reserves **225–242** as "reserved for future use", so **243 is the first
  number RISC-V could legally take**. 94 sits between `EM_ARC_COMPACT` (93) and
  `EM_VIDEOCORE` (95), in a block assigned long before RISC-V existed.
- The 2008 binutils thread cited by the repo
  (`sourceware.org/pipermail/binutils/2008-June/056623.html`) shows `EM_XTENSA 94` as an
  **unchanged context line** — a registry sync, not an assignment.
- The RISC-V psABI requires `EM_RISCV` (243) unconditionally.

`[N]` No source was found in which any toolchain emitted 94 for RISC-V. The claim is
**unsupported**, not merely imprecise.

### 2.3 `[F]` The kernel names the two cores explicitly

`drivers/media/platform/qcom/venus/firmware.c`, `venus_reset_cpu()`:

```c
if (IS_IRIS2(core) || IS_IRIS2_1(core)) {
        /* Bring XTSS out of reset */
        writel(0, wrapper_base + WRAPPER_TZ_XTSS_SW_RESET);
} else {
        /* Bring ARM9 out of reset */
        writel(0, wrapper_base + WRAPPER_A9SS_SW_RESET);
}
```

The kernel's own comment pairs `A9SS` with "ARM9". By that same naming pattern,
`XTSS` reads as **Xtensa SubSystem** — `[I]` a high-confidence inference from the kernel's
own parallel, **not** a quoted vendor definition. `XTSS` is never expanded publicly.

`[F]` **Correction to the framing.** The reset branch is not keyed on `IS_V6` in current
mainline but on `IS_IRIS2 || IS_IRIS2_1`; `IS_V6` is the older spelling. Both point at the
same generation boundary.

### 2.4 `[N]` What this does *not* establish

- **No Xtensa disassembler is available here.** Capstone 5.0.7 has no Xtensa backend and
  this machine's `objdump` lists only x86 targets. The ISA verdict therefore rests on
  header/registry evidence and the kernel reset path — **not** on decoding instructions in
  `vpu20_*.mbn`. An independent subagent extracted `binutils-xtensa-lx106` and reported
  coherent Xtensa disassembly with windowed-ABI epilogues, but that was a separate
  environment and is recorded as a secondary observation, not as my measurement.
- **Entropy is not evidence.** The code segment measures 7.179 bits/byte, but it is
  heterogeneous (~156 KB code, ~760 KB data), so entropy cannot discriminate ISAs. It is
  reported and **not** used.
- **`CAMERA_ICP` is out of local reach** — the local copies are `EM_ARM` (40), not 94. I make
  **no** claim about the FP6 `CAMERA_ICP` ISA; only about `vpu20/30/33`, which is what this
  issue's subfamily contains.
- **The Black Hat 2019 deck does not say what the repo implies.** Full-text search of the
  PDF returns **0** hits for `IDA`, `disassem`, `decompil` and `drag`; the often-quoted
  "drag the firmware into IDA" line **is not in the deck**. The "ARM 32Bit" label sits beside
  *Control Registers* in the HFI/host column — it labels the **host application processor**,
  not the firmware CPU. Pre-IRIS Venus genuinely ran ARM9, so the deck was right about the
  parts it examined. It is **out of scope**, not wrong.

### 2.5 `[I]` The reconciled three-generation picture

| generation | core | `e_machine` in firmware | kernel path |
|---|---|---|---|
| pre-IRIS Venus (`venus-5.4` and earlier) | ARM9 | 40 (`EM_ARM`) or 0 | `WRAPPER_A9SS_SW_RESET` |
| IRIS1/2 (`vpu20`, `cvpss`) | Xtensa | **94 (`EM_XTENSA`)** | `WRAPPER_TZ_XTSS_SW_RESET` |
| WCN6750 `wpss` | RISC-V | **243 (`EM_RISCV`)** | n/a |

Only `wpss.b07` is genuinely RISC-V. The repo's single "RISC-V" bucket collapsed all three.

---

## 3. The container, credited rather than re-derived

`[F]` A `.mdt` is ELF32 LE, `e_type=2`, `e_shnum=0`, and

```
.mdt  =  ELF header + phdr table (p_filesz of phdr[0])  ++  the full metadata segment
```

measured byte-exact: for `vpu20_1v`, `mdt[692:] == b01` where `len(b01) == 7376` and
`mdt[692:] == mbn[4096:8064]`. `[N]` An earlier note in my own working draft said the
relationship was `mdt[692:] == b01[:3972]`; **that was a truncation artefact and is
withdrawn** — 3,972 is not a boundary anywhere in the file.

`[F]` Both `pt_load`-like header entries carry the hash-segment marker in **`p_flags`**, not
`p_type`: `phdr[0].p_flags=0x07000000` and `phdr[1].p_flags=0x02200000`. This is why the
`| 0x1f` rule fails here, and it is why the kernel selects the segment by the `p_flags` type
field. `[F]` Because phdr 0 **also** carries the flag, a parser that scans from index 0
locks onto the wrong segment; the kernel starts its scan at index **1**. This bit me
mid-analysis and is worth recording: `mdt` hash-segment discovery must begin at 1.

`[N]` **Not claimed as new.** Qualcomm's MBN/SIF documentation states the hash segment
"contains its own 40-byte header which specifies the size of the entire hash segment, the
size of the table of hashes, the size of the attestation signature, and the size of the
certificate chain". Mainline has parsed this since 2017; `pil-splitter.py`, the Rust `mbn`
crate and IDA's built-in MBN loader all implement it.

---

## 4. What *is* measured here: the header identity across this subfamily

### 4.1 `[F]` The identity

For every media image, the metadata header's first 10 u32 words are the documented 40-byte
header. Measured (`python3 -I`, reading `phdr[1]` via `p_flags & 0x02000000`, table base
`= 120 + 48`):

| image | `w[4]` image_size | `w[5]` hash table | `w[7]` sig | `w[9]` cert | `w[5]+w[7]+w[9]` | `w[4] == sum` |
|---|---|---|---|---|---|---|
| `vpu20_1v.b01` | 7208 | 960 | 104 | 6144 | 7208 | **YES** |
| `vpu20_2v.b01` | 7208 | 960 | 104 | 6144 | 7208 | **YES** |
| `vpu20_4v.b01` | 7208 | 960 | 104 | 6144 | 7208 | **YES** |
| `…J3LNH3…MDT` (`venus.mdt`) | 7360 | 960 | 256 | 6144 | 7360 | **YES** |
| `…H3UZRV…MDT` (`cvpss.mdt`) | 7360 | 960 | 256 | 6144 | 7360 | **YES** |

**5 of 5, zero padding, zero counterexamples.**

### 4.2 `[F]` `w[5] = 48 × e_phnum` — the hash table is sized by segment count

| image | `e_phnum` | `w[5]` | `48 × phnum` | match |
|---|---|---|---|---|
| `vpu20_1v` | 20 | 960 | 960 | ✓ |
| `vpu20_2v` | 20 | 960 | 960 | ✓ |
| `vpu20_4v` | 20 | 960 | 960 | ✓ |
| `venus.mdt` | 20 | 960 | 960 | ✓ |
| `cvpss.mdt` | 20 | 960 | 960 | ✓ |

Extended by the container subagent to non-media images to test generality: 23 phdr → 1104,
13 → 624, 8 → 384, all exact. So `w[5]` is a derived quantity, not an independent budget.

### 4.3 `[F]` The exact layout, and where the earlier "6400" constant came from

```
[0, 120)           30 u32 words; w[0..9] are the documented 40-byte header,
                   w[10..29] hold further fields (w[11] = 120 = this region's
                   own size), remaining words zero
[120, 168)         48 bytes, all zero in every image examined
[168, 168+w5)      hash table, w5 = 48 × e_phnum
[168+w5, +w7)      signature blob
[+w7, +w9)         certificate chain
total = 168 + w4 = metadata segment size
```

`[F]` For `vpu20_1v`: 120 + 48 + 960 + 104 + 6144 = 7376 = `phdr[1].p_filesz`, exactly.
And `168 + w[4] == len(b01) == 7376` with **zero** trailing bytes.

`[F]` **This reconciles with, rather than contradicts, `research/fleet/pil-metadata-sweep.md`.**
That document reports `w[4] - w[5] = 6,400` for single-chain SM8250 images. That is
exactly `w[7] + w[9] = 256 + 6144` — an RSA-2048 signature plus one 6,144 B cert chain —
which is the same identity restated. The two documents now agree: the constant is the
*decomposition*, not a magic number, and it shifts with signature algorithm
(104 + 6144 = 6,248 here) and with chain count (the sweep's `+12,800` per extra chain).
`[U]` The sweep notes it could not assign which sub-regions the 6,400 accounts for; this
measurement assigns them.

### 4.4 `[F]` Signature size varies with the signing key: 104 B (P-384) vs 256 B (RSA-2048)

| family | signature bytes | meaning |
|---|---|---|
| `vpu20_1v/2v/4v` | **104** | ECDSA P-384 (96 B raw + 8 B DER/prefix) |
| `venus.mdt`, `cvpss.mdt` | **256** | RSA-2048 |

`[F]` 104 is not 96 because a P-384 `r,s` pair is 96 B and the stored blob carries 8
additional bytes; `[U]` the exact prefix is unresolved and I do not guess at it.

### 4.5 `[F]` Exactly which hash entries are zero — a rule with no exceptions

```
hash[i] == 0   <=>   i == 1  OR  phdr[i].p_filesz == 0
```

For all five media images: 11 populated, 9 zero, zero indices `{1,11,12,13,14,15,16,17,18}`.
Index 1 is always zero regardless of its non-zero `p_filesz` (it cannot hash itself); every
other zero entry has `p_filesz == 0`. `[F]` **11/11 populated entries verify** as SHA-384
over the raw `p_filesz` slice, on all three `vpu20_*.mbn` images; SHA-256, SHA-512, SHA-1 and
md5 all score **0/11**.

`[F]` **Scope note on where the check can run.** Inside a packed `.mdt` only `phdr[0]` is
physically present (the rest of the metadata segment sits at declared `p_offset`s beyond
EOF), so a `.mdt`-only check scores 1/11. The 11/11 figure requires the full `.mbn`, where
all segments are contiguous. Both were run; the numbers above are the `.mbn` result.

`[F]` **The `_unsigned` variants use a different scheme entirely**, and an earlier draft of
this section described it wrongly. Measured: `w[1] == 5` (vs 6 for signed), `p_filesz == 680
== 40 + 32 × e_phnum` (vs 7376), and the table starts at **+40 with 32-byte entries** (vs
+168 with 48). They verify **11/11 as SHA-256**, zero counters, zero mismatches. No signature
and no cert chain are present (`w[7] == w[9] == 0`). So the "unsigned" name means precisely
"hash-only": same segment set, same zero rule, SHA-256 instead of SHA-384, header instead of
signature.

---

## 5. `[F]` `venus` and `cvpss` are the same container on the same core

Found by md5-matching the FAT-mangled instantnoodle files against the matrix:

| file | md5 | matrix identity |
|---|---|---|
| `PCAFUI~2_J3LNH3~2.MDT` | `4b20ab5ea40c50865cd1ba4fb3eb6055` | `venus.mdt` (media) |
| `PCAFUI~2_H3UZRV~2.MDT` | `8b1dff7f520343e4f021e95203c7b82a` | **`cvpss.mdt` (misc)** |
| `PCAFUI~2_WUMRJ2~2.MDT` | `2bc4868991a1400ded4bf64b71b940a2` | `adsp.mdt` (adsp) |

`[F]` `cvpss` — the Computer Vision Processor subsystem — is **not** in the `media`
subfamily. It is filed under `misc`. It is nonetheless `e_machine=94`, 20 phdrs, metadata at
`p_paddr=0x0fa00000`, code at `0x0f500000`, same `e_flags=0x300`, same entry `0x0f500000`.
And its small segments are **byte-identical to `venus`**:

| segment | `venus` md5 | `cvpss` md5 | identical |
|---|---|---|---|
| b06 | `d81a5c71adbe` | `d81a5c71adbe` | **yes** |
| b07 | `eb667b725e16` | `eb667b725e16` | **yes** |
| b08 | `ec2d6ced2030` | `ec2d6ced2030` | **yes** |
| b05 | `f05c4f03a928` | `8a9adc57a5c0` | no |
| b09 (code) | `564766be96bd` (885,120 B) | `203103820df1` (385,308 B) | no |

`[I]` So `venus`/`cvpss` are two instances of one Xtensa container template differing in
payload. The matrix's `media` vs `misc` split reflects *which directory the blob was found
in*, not the firmware's structure. **Anyone working the `media` family is working the same
codebase as the `misc` `cvpss` rows.**

`[F]` My own working note that `WUMRJ2` was a "second generation" of the Venus container was
**wrong**: it is `e_machine=164` (`EM_HEXAGON`), i.e. the ADSP, a different processor. It
shares the container *discipline* (phdr[0] table, phdr[1] metadata, same flags) but is not
a Venus generation. Corrected here rather than propagated.

---

## 6. `[F]` Cross-device sharing — one RE pass informs many devices

From the 470 rows, per segment index, distinct md5 count:

| segment | rows | distinct md5 | note |
|---|---|---|---|
| b05 | 29 | **1** | `f05c4f03a928…`, 20 B |
| b06 | 29 | **1** | `d81a5c71adbe…`, 20 B |
| b07 | 29 | **1** | `eb667b725e16…`, 24 B |
| b08 | 29 | **1** | `ec2d6ced2030…`, 16 B |
| b19 | 29 | **1** | `0d68af0904dd…`, 32 B |
| b03 | 34 | 4 | dominant `4344e8407082…` on 23 devices |
| b01 | 34 | 29 | per-image metadata, expected |
| b09 | 29 | 12 | the code segment |
| b10 | 29 | 12 | the data segment |

`[F]` Five segments are **single-valued across all 29 devices carrying them**. `b19` is
`0x0dd0adde` repeated eight times. These are constants, not per-device data — a device
carrying them adds no new RE surface.

`[N]` `b03` is **not** a shared constant, contrary to an assumption I carried into the
analysis: it has 4 distinct md5s (23-device dominant, a 6-device 20-byte variant, a 4-device
40,516-byte variant, and 1 singleton). Citing it as shared would be an error.

---

## 7. Honest negatives

- **No ISA proof from disassembly.** No Xtensa disassembler in this environment. §2 rests on
  registries and the kernel, not on decoded bytes of this image.
- **`CAMERA_ICP` ISA not asserted.** The local copies are `EM_ARM`; the FP6 set the repo
  discusses is not in the local tree.
- **No runtime behaviour established.** Nothing here shows what the firmware does; 0 pointers
  to any document were checked, and no HFI exchange was traced.
- **Matched-semantics words unresolved.** `w[19]` (`2` vs `258`), `w[20]`, `w[12..18]` are
  measured but unexplained. `w[6]==w[8]==p_paddr+40+32*phnum` is arithmetic only; its role
  is `[U]`.
- **Padding cases excluded as out-of-scope.** A fleet-wide scan found 4 images with
  +6,656 B slack, but md5-identity shows they are `featenabler`, `haventkn`, `cmnlib64`,
  `cmnlib` — TZ images, **not** media. All 5 media images have **zero** padding. An earlier
  draft of this section reported "4 of 42 with padding" as a media finding; that was a
  scope error and is withdrawn.
- **The matrix cannot answer device class or era** — no such fields exist.
- **Fleet breadth is 53 devices**, and only 3 device trees were inspected at file level. The
  census is matrix-derived for 470 rows; only ~37 files were opened.

---

## 8. Corrections filed against existing repo text

Per Rule 1, the wrong statements were corrected **in place**, not merely contradicted in a
new file. This table records what changed:

| file | statement before | status after |
|---|---|---|
| `research/qualcomm/results/census.md` | `RISC-V (old, bespoke)` on the histogram row + 12 file rows | **corrected** to `Xtensa` (13 replacements) |
| `research/qualcomm/docs/fp6-architecture-census.md` | arch-table row `RISC-V historic (94)` | **corrected** to `Xtensa (94, EM_XTENSA)` |
| `research/qualcomm/docs/fp6-architecture-census.md` | *"e_machine=94, the historic RISC-V value used by early toolchains (243 was assigned later)"* | **corrected**, with the gABI reservation and kernel reset-path evidence added |
| `research/qualcomm/docs/fp6-architecture-census.md` | *"kernel sources name the devices but not the cores"* | **removed** — `firmware.c` names `XTSS` and `A9SS` in comments |
| `research/qualcomm/docs/fp6-architecture-census.md` | *"This appears to be the first public identification of FP6 ICP/VPU firmware as RISC-V"* | **removed** — the identification was wrong, so "first" is moot |
| `upstream/pr5-corrections-package.md` §PR-5 | full paste-ready PR relabeling upstream Xtensa → RISC-V | **withdrawn in full**, with the reason recorded |
| `upstream/README.md` | PR-5 listed as a live filing | **marked withdrawn** |
| `upstream/librephone-wants.md` B-6 | *"LAB — NEW error found this session"* | **retracted**; upstream text is correct |
| `research/qualcomm/upstream-pr-draft.md` | proposed `docs/fp6-riscv-cores.md` with RISC-V label | **corrected** to Xtensa |

`[F]` **LibrePhone was right and this repo was wrong.** Upstream `docs/other.md` already said
"Tensilica Xtensa certificates" for the ICP family and "Xtensa 32 Bit executable with certs
for Trusted Boot" for `vpu20_2v.mbn`. PR-5 existed solely to overturn that. Withdrawing it
is the deliverable, not a side effect.

`[N]` The repo's own method note (junk `e_machine` in `.bXX` segment headers) is **correct**
and worth keeping; the error was applying `.mbn`-level header evidence and then naming the
value from memory instead of from `elf.h`.

---

## 9. Prior art, credited

| topic | prior art | my relation |
|---|---|---|
| MDT/MBN container, hash segment, 40-byte header | Qualcomm MBN/SIF documentation; `drivers/soc/qcom/mdt_loader.c` (2017–); `pil-splitter`, Rust `mbn`, IDA MBN loader | **cited, not claimed** |
| Venus HFI protocol, `0xE0000000` aperture, `0x70800000` message queue, GetBits/CCE | Black Hat USA 2019, Xiling Gong (Tencent Blade Team) | **cited, not claimed** |
| Venus driver, firmware naming, `venus.mdt → venus.mbn` symlinks | `drivers/media/platform/qcom/venus/`, linux-firmware `WHENCE` | **cited** |
| Xtensa on the VPU | kernel `firmware.c` comments; Garodia 2026 patch series | **cited** |
| `QCOM_MDT_RELOCATABLE` = `BIT(27)` = `0x08000000` | mainline since v4.11 (2017) | **not a discovery** |
| Fleet inventory of Qualcomm video firmware | librephone already inventories 210 Lineage devices per-file | **narrowed**: this is the first *structural* census of the family, not the first inventory |

`[N]` `vpu20_2v` is close to unmentioned publicly, but librephone already classified it as
"Xtensa 32 Bit executable with certs for Trusted Boot" — i.e. **the correct architecture was
already published there**, which is precisely the claim this repo's PR-5 package set out to
*correct*. PR-5 would have introduced an error into a document that was right.

---

## 10. Reproduce

```
python3 -I hexagon_probe.py <image>            # container + metadata, from #606
python3 -c "import csv; ..." over coverage-matrix.csv   # the 470-row census
readelf -h <image>                              # e_machine, phnum, entry
```

All measurements in this document were produced by stdlib Python 3 under
`python3 -I`, plus `readelf`. Working scripts and subagent reports:
`/tmp/opencode/2058/{container,isa,census,audit}/`.
