# `wpss` subfamily — fleet census, PIL split-image law, and board-id indexing (73 devices)

**Issue:** #2067 · **Slot:** OC-4 · **Date:** 2026-11-20
**Scope:** every row in `upstream-contribution/blob-database/coverage-matrix.csv`
whose `blob_subfamily` is `wpss` — 5,198 rows, 73 devices, 317,873,910 B.

**Evidence classes:** `[F]` fact (measured on bytes or on a committed table, with
the command in §9) · `[I]` inference (strong, derived from measurement) · `[H]`
hypothesis (plausible, unverified) · `[N]` honest negative (probed, not found).

**Rule 0.** Prior art was searched on 2026-11-20 before any work; the queries and
the resulting DELTA are recorded on the issue. The kernel sources cited below were
fetched the same day from `git.kernel.org` / `torvalds/linux`, and the firmware
payloads from `linux-firmware`. Nothing here is copied from a proprietary payload:
only sizes, offsets, counts, hashes, and short strings.

**What this document is not.** `mdt_loader.c` already specifies the split-file
mechanism, and `cnss2/qmi.c` already specifies the `bdwlan` naming rule. Both are
cited as normative, not rebuilt. The TLV grammar is resolved in
[`bdwlan-format.md`](bdwlan-format.md) for one device; the QURT/RISC-V
identification is in [`../qualcomm/docs/wpss-qurt-rtos.md`](../qualcomm/docs/wpss-qurt-rtos.md).
This document supplies what none of them cover: the fleet-scale census, the
`b<NN> ≡ phdr NN` law, which phdr carries which role, the `b`↔`e` relation (they
are the *same body*, raw versus ELF-wrapped, and that choice tracks the chip
generation), the complete naming taxonomy, and the matrix's own defects. It
carries three Rule 1 corrections to committed artifacts — `bdwlan-format.md` §5
(field hypothesis refuted) and §10 (open item resolved), and `census.md`'s `x86`
label — plus the measurements that justify each.

**Method note.** Every number below was produced by a command in §9 and re-run
before commit. Where a claim was corrected mid-session the correction is stated in
place (`An earlier draft…`) rather than silently rewritten, so a reader can see
which numbers were wrong and why.

---

## 1. "wpss" is a directory prefix, not a format `[F]`

Splitting the 5,198 rows by filename grammar gives three components with nothing
in common but their parent directory:

| component | rows | devices | distinct md5 | bytes |
|---|---:|---:|---:|---:|
| PIL split image `wpss.mdt` + `wpss.b00..b12` + `wpss.qdb` | 74 | 6 | 68 | 47,473,106 |
| Board data `bdwlan*` | 5,120 | 73 | 1,895 | 270,399,184 |
| PDR manifest `wlanpdr.jsn` | 4 | 4 | 1 | 1,620 |
| **total** | **5,198** | **73** | **1,964** | **317,873,910** |

Command §9.1. Two consequences:

1. **Only 74 of 5,198 rows (1.4 %) are the `wpss.*` PIL image.** 98.5 % are
   `bdwlan*` board data. A reader who assumes "the wpss subfamily" means the
   `wpss.b*` split image is looking at 1.4 % of it.
2. **The 73-device figure is a `bdwlan` figure.** Only 6 devices carry the PIL
   image. Work scoped to `wpss.b*` covers 8 % of the devices in the family.

`wlanpdr.jsn` is one 405-byte file, one md5
(`1a4a6904fc55234e68b68ebf4ddefe87`), on `Nord_CE2`, `Nord_CE3`, `Realme_9_Pro`,
`Realme_10_Pro` — a PDR service registry, not firmware `[F]`.

---

## 2. The PIL split image `wpss.*` — `b<NN>` **is** program header `NN` `[F]`

### 2.1 The normative spec

`drivers/soc/qcom/mdt_loader.c` and `include/linux/soc/qcom/mdt_loader.h` specify
this container: `phdrs[0]` is non-`PT_LOAD` and holds the ELF header with
`ehdr_size = phdrs[0].p_filesz`; exactly one segment satisfies
`p_flags & QCOM_MDT_TYPE_MASK == QCOM_MDT_TYPE_HASH` with
`QCOM_MDT_TYPE_MASK (7<<24)` and `QCOM_MDT_TYPE_HASH (2<<24)`; split segment names
are formed by overwriting the last three characters of the firmware name with
`"b%02d"`; and split versus single-file ("pil-squashed") form is detected by ELF
validity, not by extension `[F]`.

The segment-name construction is `sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)`
where `segment` is the phdr loop index `i`, and the file is requested only when
`phdr->p_filesz` is non-zero. So the spec says three things at once: `b<NN>` is
phdr `NN`; a zero-`p_filesz` phdr produces **no file**, so the index set is not
contiguous; and the hash segment is found by **flags**, not by position `[F]`.

**Why upstream ships no `wpss.bNN` at all.** linux-firmware's `WHENCE` declares
`Link: ath11k/WCN6750/hw1.0/wpss.mdt -> sc7280/wpss.mbn` — the `.mdt`-named file
*is* the monolithic image, so `qcom_mdt_bins_are_split()` returns false and the
kernel never requests a segment. The split set exists only in vendor
`modem/image/` partitions, which is exactly the 6 devices in this matrix `[F]`.

That spec predicts `b<NN>` is program header `NN`. Measured, it is.

### 2.2 `b<NN> ≡ phdr NN`, exact

The mismatch thesis is that `b<NN>` drifts from phdr `NN`. It does not: on every
comparable index the two agree, and the *only* source of difference is that two
different firmware builds are being compared. Matching the right build makes the
identity exact:

| phdr | `sc7280` | `qcm6490` | Edge_30 | FP5 | Phone_1 |
|---:|---:|---:|---:|---:|---:|
| 0 | 340 | 340 | 340 | 340 | 340 |
| 1 | 6,848 | 4,272 | 7,000 | **6,848** | **6,848** |
| 2 | 10,300 | 10,300 | 10,300 | 10,300 | 10,300 |
| 3 | 4,096 | 4,096 | 4,096 | 4,096 | 4,096 |
| 4 | 5,819,999 | 6,125,113 | 5,832,775 | 5,838,263 | 5,787,087 |
| 5 | 164,332 | 118,588 | 118,420 | **118,588** | 232,432 |
| 6 | 266,684 | 266,684 | 266,684 | 266,684 | 266,684 |
| 7 | 1,176,368 | 1,188,656 | 1,180,464 | 1,180,464 | **1,176,368** |
| 8 | 0 | 0 | — | — | — |

Command §9.5b. Exact-match counts, out of 8 non-zero phdrs:

```
against sc7280 : Edge_30 4/8, FP5 5/8, Phone_1 6/8
against qcm6490: Edge_30 4/8, FP5 5/8, Phone_1 4/8
```

Indices 0, 2, 3 and 6 are exact on **all three comparable devices** against **both**
builds — 340, 10,300, 4,096 and 266,684 are build-invariant sizes `[F]`. (The three
13-phdr devices are not index-comparable to a 9-phdr build and are covered
separately in §2.5.)

**Phone_1 matches `sc7280`, not `qcm6490`** — 6 exact indices including the
1,176,368 B `b07`, where every other device matches neither. That is consistent
with the matrix: Phone_1 is `SM7325-AE` (Snapdragon 778G+), the same family as the
sc7280 reference. And FP5 (`QCM6490`) matches `qcm6490` at `b05` (118,588 exactly),
which no other device does. So the `b<NN> ≡ phdr NN` identity holds
*device-to-its-own-build*; the residual mismatches are build differences, not
index drift `[F]`.

### 2.3 The `b` count equals the number of non-empty program headers `[F]`

```
wpss_sc7280.mbn : phnum 9, non-zero p_filesz 8  -> b00..b07
wpss_qcm6490.mbn: phnum 9, non-zero p_filesz 8  -> b00..b07
```

Cross-checked on all six matrix devices: `b00 = 52 + 32·phnum` is a whole number,
and the number of `b` files is exactly the number of non-zero-`p_filesz` phdrs.

| device | `b00` | `phnum = (b00−52)/32` | `b` files | indices present | absent |
|---|---:|---:|---:|---|---|
| Edge_30 | 340 | 9 | 8 | 0–7 | 8 |
| FP5 | 340 | 9 | 8 | 0–7 | 8 |
| Phone_1 | 340 | 9 | 8 | 0–7 | 8 |
| FP6 | 468 | 13 | 12 | 0–10, 12 | 11 |
| Nord_4 | 468 | 13 | 12 | 0–10, 12 | 11 |
| Nord_CE4 | 468 | 13 | 12 | 0–10, 11 | 12 |

**This resolves the apparent "gap".** A missing index is a phdr with
`p_filesz == 0` (a `.bss`-style segment). It is not missing data, and a loader must
not stop at the gap `[F]`.

### 2.4 `.mdt = b00 ‖ b<hash-index>`, and the hash index varies `[F]`

`.mdt` is `b00` concatenated with exactly one segment — the one whose
`p_flags & QCOM_MDT_TYPE_MASK == QCOM_MDT_TYPE_HASH`. If the hash segment were
always the same index, then `mdt − b00` would always be the same file. It is not:

| device | `mdt − b00` | matching segment |
|---|---:|---|
| Edge_30 | 7,000 | `b01` |
| FP5 | 6,848 | `b01` |
| Phone_1 | 6,848 | `b01` |
| Nord_CE4 | 4,376 | `b01` |
| **FP6** | 4,376 | **`b12`** |
| **Nord_4** | 4,376 | **`b12`** |

**So the instability is real but it is in the role, not the index.** `b<NN>` always
means phdr `NN`; what moves is *which* phdr carries the hash/cert block. A
reassembler that hardcodes "hash is `b01`" produces a corrupt image on FP6 and
Nord_4 `[F]`. The correct rule is the kernel's: select the hash segment by
`p_flags`, not by position.

### 2.5 Role-versus-index table across the fleet

Roles are assigned by invariant (`mdt − b00` for the hash), by size band, and by the
nested ELF header where one exists:

| role | Edge_30 | FP5 | Phone_1 | FP6 | Nord_4 | Nord_CE4 |
|---|---|---|---|---|---|---|
| HASH/cert (4,376–7,000 B) `[F]` | b01 | b01 | b01 | **b12** | **b12** | b01 |
| main body (>4 MB) `[F]` | b04 | b04 | b04 | b06 | b06 | b07 |
| RISC-V (`e_machine=243`) `[F]` | b05 | b05 | b05 `[I]` | b07 | b07 `[I]` | b08 `[I]` |
| M3 (`e_machine=3`) `[F]` | b06 | b06 | b06 `[I]` | b08 | b08 `[I]` | b09 `[I]` |
| fixed 4,096 B `[F]` | b03 | b03 | b03 | b05 | b05 | b06 |
| 10,300 B loader `[F]` | b02 | b02 | b02 | — | — | — |
| zero-`p_filesz` gap `[F]` | b08 | b08 | b08 | **b11** | **b11** | **b12** |

Two clarifications an earlier draft of this table got wrong `[F]`:

- **The 13-phdr builds have no 10,300 B segment at all.** It is a 9-phdr-generation
  artifact (`b02` on Edge_30/FP5/Phone_1 only). On FP6/Nord_4 `b02` is 461,049 B.
- **The RISC-V segment's size is not a stable anchor.** Measured: 164,332 B
  (`sc7280`), 118,588 B (`qcm6490`), and 139,316 B on FP6 per `census.md`. Phone_1's
  `b05` at 232,432 B is therefore a large-but-ordinary RISC-V build, not a missing
  segment — an earlier draft wrongly marked it `—`. The **index** is the invariant,
  the size is not.
- **The 4,096 B segment is the only size present on all six devices** (and it stays
  at the same *size*, not the same index). It is the strongest cross-generation
  anchor `[F]`.

**Evidence boundary on this table.** The RISC-V and M3 rows are *measured* for the
9-phdr generation from the monolithic images on disk (§2.6), and for **FP6** they are
independently attested by `census.md`'s recorded ELF-machine scan of a real FP6
extraction: `wpss.b07` is `ELF / RISC-V` and `wpss.b08` is the single `EM_386`
entry. That is exactly the `b07`/`b08` assignment above, so the table's FP6 column
is `[F]`.

For `Nord_4` and `Nord_CE4` the same two rows remain an inference from ordinal
position in the payload sequence (§2.5a) — their aligned sequence matches FP6's one
for one, which is strong `[I]` but not a measurement, because no `wpss.bNN` payload
from those two devices was available to open `[N]`. Note also that `census.md`'s FP6
sizes differ from the matrix's for `b06`, `b07`, `b09`, `b10` and `qdb` — a
different build of the same tree — so only the *role* transfers across sources, not
the sizes.

The 13-phdr generation also introduces segment sizes the 9-phdr generation lacks —
256 B, 468 B (its `b00`), 1,104 B, 4,376/6,440 B (its hash), and a 275,644 B M3-class
body against 266,684 B on the older builds — so the two generations are not simple
re-indexings of one another `[F]`. Only three sizes are common to both: 4,096 B,
118,420 B and 118,588 B.

### 2.5a The payload sequence is identical; only the hash slot moves `[F]`

Comparing the two 13-phdr builds directly shows a cleaner law than "roles move".
`Nord_CE4` and `FP6` carry the **same payload sequence in the same order**, offset
by exactly one index, because the hash block is inserted at a different point:

| | b00 | b01 | b02 | b03 | b04 | b05 | b06 | b07 | b08 | b09 | b10 | b11 | b12 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| FP6 / Nord_4 | 468 | 6440 | 461049 | 1104 | 256 | 4096 | 6067704 | 118588 | 275644 | 356840 | 907982 | **∅** | **4376** |
| Nord_CE4 | 468 | **4376** | 6440 | 461049 | 1104 | 256 | 4096 | 6060574 | 118420 | 275644 | 344520 | 905942 | **∅** |

Read across: `CE4 b02..b06 ≡ FP6 b01..b05` (6440, 461049, 1104, 256, 4096 — all five
identical), `CE4 b09 ≡ FP6 b08` (275644, identical), and `CE4 b01 ≡ FP6 b12` (4376,
identical). Seven of eleven aligned sizes match exactly, which is far beyond chance on
values this large. The four that differ (`b07`, `b08`, `b10`, `b11` on CE4) are the
main body, the RISC-V-class body and the two large trailing bodies — the ones that
carry product-specific firmware `[I]`. The zero-`p_filesz` phdr and the hash phdr
**swap positions**: on FP6/Nord_4 the gap is 11 and the hash is 12; on Nord_CE4 the
hash is 1 and the gap is 12 `[F]`.

**Why this matters for a reassembler.** `b<NN> ≡ phdr NN` means a size-comparison
reassembler that matches segments *by index* across devices mis-aligns every
payload segment after the hash by one on this generation. Matching must be by
`p_flags` and `p_filesz`, never by index `[F]`.

### 2.6 The two nested ELFs, and why `e_machine=3` is not x86 `[F]`

Both monolithic images carry two nested ELF32 images inside `PT_LOAD` segments.

**The RISC-V image** has `e_machine=243` (`EM_RISCV`), `e_entry=0x404000`, 5 phdrs,
13 sections, and its `.riscv.attributes` section holds the arch string:

```
rv32i2p0_m2p0_a2p0_c2p0
```

That is RV32I base with M, A and C, each version 2.0 — **RV32IMA + C** `[F]`. Section
table (sc7280 variant): `.init` 2,330 B, `.rddm.pre.text` 14 B, `.rddm.post.text`
512 B, `.text` 101,340 B, `.rodata` 13,118 B, `.data` 8,232 B, `.sdata` 100 B,
`.sbss` 340 B, `.bss` 34,680 B, `DIAG_NON_LOAD.rodata` 17,874 B. This is the ISA
ground truth behind the earlier strings-based QURT finding: it is read from the ELF
attribute section, not inferred from strings.

**Attribution caveat `[N]`.** The kernel does *not* say WPSS is RISC-V, and says the
opposite where it says anything: `Documentation/devicetree/bindings/remoteproc/qcom,sc7280-wpss-pil.yaml`
calls it a "Hexagon core" three times (that is boilerplate inherited from the
ADSP/CDSP bindings), `qcom_q6v5_pas.c` makes no ISA claim at all, and a `grep -i risc`
over the ath11k tree returns nothing. The RISC-V evidence is **firmware-side and
twofold**: the `.riscv.attributes` string above, and linux-firmware's
`ath11k/WCN6750/hw1.0/Notice.txt` line 914, which carries a build path
`//components/rel/core.riscv/1.0/api/kernel/libstd/stringl/stringl.h` alongside five
`rel/core.wpss/1.0` paths. A RISC-V-tree component is compiled into the image. The
outer ELF's `e_machine=164` (`EM_QDSP6`) is a label for the container, not for the
RISC-V core inside it `[F]`.

**The `e_machine=3` (`EM_386`) image is not x86 code.** Its only executable section
is `.data` at `p_vaddr=0x4ff00000`, 262,144 B, and its `.strtab` contains:

```
_binary_padded_pcss_m3_tx_rx_bin_start
_binary_padded_pcss_m3_tx_rx_bin_end
_binary_padded_pcss_m3_tx_rx_bin_size
```

`m3` in the symbol name plus a single `.data` section means a raw **Cortex-M3**
image wrapped in an ELF with a placeholder machine id. On the `qcm6490` build the
`.data` payload is 262,144 B, entropy 5.524 bits/B, 174,581 of 262,144 bytes
non-zero, 2,319 bytes of trailing zero pad; the `sc7280` build differs slightly
(entropy 5.508, 173,805 non-zero) with the same size and the same trailing pad.
Both builds place it at `p_vaddr=0x4ff00000` with `p_filesz=266,684` `[F]`.

**Correction (Rule 1):** [`../qualcomm/results/census.md`](../qualcomm/results/census.md)
line 592 labelled `wpss.b08` as `ELF / x86` — only the raw `e_machine` value, never
a CPU claim. `EM_386` is a placeholder machine id here. That row now reads
`EM_386 header, Cortex-M3 body` and carries a caveat note. The `m3` finding itself
rests on the two linux-firmware builds measured here; the FP6 blob could not be
re-opened because its extraction tree is no longer on the machine, so the label
correction is evidence-based while the FP6 body-identity claim is not `[N]`.

---

## 3. `bdwlan` — the board-data family `[F]`

### 3.1 Naming families

`bdwlan` rows split by grammar:

| family | rows | devices | bytes |
|---|---:|---:|---:|
| `bdwlan.[be]NN` — two hex digits | 4,202 | 60 | 237,599,732 |
| `bdwlan.NNN` — three digits (`102`, `201`) | 400 | 29 | 10,531,200 |
| `bdwlan[u/g/s/t].*` — letter infix | 228 | 31 | 12,151,724 |
| `bdwlan_<plat>_<region>_<ipa\|epa>.bin` | 163 | 17 | 4,291,464 |
| `bdwlan.bin` / `bdwlan.elf` | 81 | 67 | 3,745,580 |
| `bdwlan.elf.<region>.<ipa\|epa>` | 16 | 4 | 1,218,340 |
| `bdwlan.*.xz` — compressed | 9 | 3 | 58,944 |
| `bdwlan-<pixel-codename>.bin` | 8 | 3 | 210,624 |
| `bdwlan.[be]NNN` — three hex (`b101`) | 6 | 3 | 354,288 |
| `bdwlan_<name>.bin` / `.elf` (`_chain0`, `_in`, `_us`) | 5 | 3 | 198,984 |
| `bdwlanb<N>.bin` | 2 | 2 | 38,304 |
| **total** | **5,120** | **73** | **270,399,184** |

Every row is classified and the column sums reconcile exactly to the family total
`[F]`; there is no residual bucket. An earlier draft of this table used a looser
grammar, mis-bucketed the platform and `elf.<region>.<type>` rows, and left a
26-row "other" — corrected by measuring the partition instead of estimating it.

**The `b`/`e` suffix space is bounded.** Two-digit suffixes run `01`–`71` for `b`
(75 distinct) and `01`–`e1` for `e` (175 distinct), i.e. max values 113 and 225
decimal — every one ≤ 0xFF, consistent with the naming rule in §4. The only
three-digit forms are `b101`/`e101`, on 3 devices — the >0xFF case of §4.1 `[F]`.

**A third alphabet exists.** Besides `bdwlan.b*` and `bdwlan.e*`, the family carries
`bdwlan[u/g/s/t].*` — a letter *infix* after `bdwlan`, not a suffix. 228 rows across
31 devices, distributed very unevenly:

| infix | rows | devices | shape |
|---|---:|---:|---|
| `g` | 183 | 12 | `bdwlang.elf` + `bdwlang.e8b…ec1` (hex suffixes in the `e8x`–`ecx` range only) |
| `u` | 34 | 19 | `bdwlanu.202`, `bdwlanu.206`, `bdwlanu.b65/b66/b69`, `bdwlanu.bin` |
| `t` | 7 | 7 | `bdwlant.202`, one per device |
| `s` | 4 | 4 | `bdwlans.202`, one per device |

The device sets are disjoint at the top: `g` and `u` share **zero** devices, and
`s` is a strict subset of `t` (4 of `t`'s 7). Only the `u` form uses `b`-suffixed
names at all. This is not covered by `bdwlan-format.md` and its meaning is
unresolved (§8) `[F]`.

### 3.2 The `b` size set is exactly two values, both attested upstream `[F]`

Every `bdwlan.b<two hex>` row in the matrix — 1,122 rows — is one of two sizes:

```
26328  rows 1020
58180  rows  102
```

The three-digit form does not add a third: all 6 `bdwlan.b101`/`e101` rows on
`FP6`, `Nord_4`, `Nord_CE4` are also 58,180 B (the `e` forms 59,872 / 60,004 B).
Nor do the letter-infixed names — the 19 `bdwlan[u/g/s/t].b<NN>` rows are all
26,328 B `[F]`. So the body size is a function of the hardware generation, not of
the filename grammar.

Both are attested as the `.data` body of an upstream `board-2.bin` entry:

| upstream file | body sizes found |
|---|---|
| `ath10k/WCN3990/hw1.0/board-2.bin` | 19,152 · 26,328 |
| `ath11k/WCN6750/hw1.0/board-2.bin` | 58,180 |
| `ath11k/WCN6855/hw2.0/board-2.bin` | 58,180 |

Command §9.6. So 26,328 B is the WCN3990-generation body and 58,180 B is the
WCN6750/WCN6855-generation body `[F]`.

**19,152 B is not a third generation — it is the short tail of the 26,328 B
grammar.** In the WCN3990 container, 8 of 36 entries ship at 19,152 B and 28 at
26,328 B; but 3 of the 28 long entries walk their TLV list to exactly **19,152 B**
and then carry 7,176 bytes of pure zero padding (`variant=xiaomi_beryllium`,
`Google_blueline`, `Google_crosshatch`). So the short form and the long form share
one grammar; the long form differs only by trailing zero-filled records `[F]`. The
short body's own last non-zero byte is at offset 19,082 of 19,152, so it too is
zero-extended to its declared length — padding to a round length is normal here,
not an anomaly.

In the matrix, 19,152 B appears on **5 devices, 7 rows**, all Sony Xperia:
`bdwlan.bin` on `Xperia_XA2`, `Xperia_XA2_Plus`, `Xperia_XA2_Ultra`, `Xperia_10`,
`Xperia_10_Plus`, plus `bdwlanb1.bin` on `Xperia_10` and `Xperia_10_Plus`. It never
appears as a `bdwlan.b<NN>` variant `[F]`. The rest of the under-20 KiB band is a
different thing — 6,136–6,752 B files on `Edge_40_Pro`, `OnePlus_12` and `Pad_Pro`,
too small to be a board body of either generation `[N]`.

### 3.3 `b` is the raw body, `e` is the same body in an ELF wrapper `[F]`

`board-2.bin` entries are ELF32 `e_machine=40` (`EM_ARM`), `e_type=2`,
`e_entry=0x8000`, one `PT_LOAD` at `p_vaddr=0x1000` with
`p_filesz = p_memsz = 58,180`, `.data` at file offset 1,024. Walking that `.data`
as `{u16 tag, u16 len, payload}` is the same grammar and the same size as the
on-device `bdwlan.bNN`. So `e` is an ARM-ELF wrapper and `b` is the unwrapped body
— but the wrapper is **not a constant**: the same 58,180-byte body ships at four
different `e` sizes:

| `b` | `e` | delta | occurrences |
|---:|---:|---:|---:|
| 58,180 | 59,932 | 1,752 | 55 |
| 58,180 | 60,000 | 1,820 | 43 |
| 58,180 | 59,868 | 1,688 | 3 |
| 58,180 | 59,836 | 1,656 | 1 |

**The wrapper decomposes exactly.** Reading 129 upstream entries, the file size is

```
e = p_filesz + 1024 + symtab.size + symstrtab.size + shstrtab.size
                 + 40·e_shnum + pad + tail
```

with zero violations. `1024` is `p_offset` (the `.data` start), `40·e_shnum` the
section-header table, `pad` a 0–3 byte align to the table, `tail` normally 32. What
varies is **`e_shnum` (5, 6 or 7)** and the string-table sizes:

| `e_shnum` | extra section | wrapper overhead | count |
|---:|---|---:|---:|
| 5 | `.symtab .strtab .shstrtab .data` | 1,720 – 1,868 | 46 |
| 6 | + `.noinit` | 1,784 – 1,792 | 10 |
| 7 | + `.noinit` **+ `.persistent`** | 1,796 – 1,956 | 73 |

**The wrapper's sections are named normally — the opposite of what an earlier draft
of this document claimed.** `e_shstrndx` is **4, 5 or 6** (tracking `e_shnum`), and on
all 129 entries it indexes a genuine `SHT_STRTAB` whose contents are
`\0.symtab\0.strtab\0.shstrtab\0.data\0[.persistent\0][.noinit\0]`. So `.data`,
`.noinit` and `.persistent` are all resolvable by name through the standard
mechanism, and a parser should use `e_shstrndx` exactly as the ELF spec says `[F]`.

This corrects a real error: an earlier draft stated "`e_shstrndx = 0` on all 129
entries, so sections are formally unnamed", reading the value from field index 6 of
the unpacked header. In an ELF32 `Ehdr` laid out from offset 16, index 6 is
**`e_flags`** (0 on all 129), not `e_shstrndx`, which is index 12. The `shnum`
counts were unaffected because index 11 is `e_shnum` — so the decomposition
arithmetic below always stood — but the "stripped names" conclusion was an artifact
of that off-by-six field read. Worked example (`qmi-board-id=25`, `e_shnum = 7`):

```
e_flags 0   e_shstrndx 6   e_shnum 7
<null>  type 0   .data  type 1 (58,180 B)   .persistent type 1 (0)
.noinit type 8   .symtab type 2 (288)       .strtab type 3 (149)
.shstrtab type 3 (53)
```

The symbols are real, though, and they confirm the naming rule independently. The
`SYMTAB`'s string table carries `_binary_bdwlan_b19_start/_size/_end` on the entry
labelled `qmi-board-id=25`, and `_binary_tempDir_bdwlan_b01_*` on older entries — so
board id 25 decimal → `b19` hex, and the `_binary_<sourcepath>_` prefix records the
build path (`tempDir/` on some, none on others). That variable-length source path is
exactly what moves `e` by ±200 B `[F]`.

**The wrapper's knob space is measured, not guessed.** Across the 129 entries the
six terms take only these values:

```
symtab  {256, 272, 288}      pad    {0, 1, 2, 3}
symstr  {33, 41, 53}         tail   {0, 32}
shstr   14 values, 149–323   shnum  {5, 6, 7}
```

That puts the constructible floor at `1024 + 256 + 33 + 149 + 200 + 0 + 0 = 1,662` B.
Three of the fleet's four deltas fall inside it; the fourth does not:

| delta | occurrences | inside measured space? |
|---:|---:|---|
| 1,656 | 1 | **no — 6 B below the floor** |
| 1,688 | 3 | yes (2 solutions) |
| 1,752 | 55 | yes (10 solutions) |
| 1,820 | 43 | yes (13 solutions) |

So the wrapper grammar is exact and explains 101 of the 102 fleet rows that pair a
`b` and an `e` at the same suffix (`55+43+3+1 = 102`), but the single 1,656 B case
is **not** reproducible from the measured knob sets `[N]`. It
would need either a `symstr`/`shstr` value outside the observed range or a smaller
`p_offset` than 1,024 — neither is attested upstream. An earlier draft of this
section claimed all four were "inside the model"; that was wrong, and the honest
statement is that three are and one is not.

The important consequence is unchanged: `b → e` is a *known function of six small
integers*, not a constant, so no fixed offset can convert between them `[F]`.

**`b`-only vs `e`-only partitions the fleet by chip generation `[F]`.**

| group | devices | what they carry |
|---|---:|---|
| `b` only | 28 | every `b` is **26,328** — a raw, unwrapped body |
| `e` only | 26 | every `e` is ≥ 57,932 — always wrapped |
| both | 6 | 58,180 raw **and** its wrapped forms |

The 28 `b`-only devices carry exactly nine part numbers — `MSM8998 SM4250 SM4375
SM6115 SM6225 SM6375 SM7225 SM8150 SM8150-AC` — and 5 of the 28 have an empty
`soc`. Their upstream counterpart is `ath10k/WCN3990/hw1.0/board-2.bin`, which
ships its 36 entries as **raw TLVs**: verified, not one entry begins with
`\x7fELF`, each is a 4+4 byte container header plus an 8-byte entry header and
name, and the body lengths are exactly **26,328 (×28) and 19,152 (×8)** — the two
sizes §3.2 attributes to that generation. The 26 `e`-only devices are SM7250 and
newer, whose upstream containers (WCN6750/WCN6855) wrap every entry in ELF. So the
matrix's naming (`bdwlan.b*` vs `bdwlan.e*`) records *whether that product's
firmware ships the body raw or ELF-framed* `[F]`.

The 6 `both` devices are **exactly** the six that also ship split `wpss.b*`
(§2.3) — a coincidence in count that turns out to be the same six device names,
verified by set equality in §9.9. Those are the products whose modem image vendors
both forms, presumably for two different carrier-selection paths `[I]`.

**The TLV tail is not uniform either — and that is a second finding.** In the same
11-entry WCN6750 container, three distinct tail layouts coexist:

| board ids | tags parsed | last tag | consumed | tail |
|---|---:|---:|---:|---|
| 1–7, 255 (8 entries) | 33 | 33 (596 B payload) | 58,180 | — |
| 9, 10 (2 entries) | 34 | 33 (10 B) + 34 (582 B) | 58,180 | — |
| 25 (`variant=Qualcomm_rb3gen2`) | 33 | 33 (**10 B**) | 57,594 | 586 B |

Entries 9 and 10 split what the others keep whole: tag 33 is 596 B in one and
10 B + 582 B in the other, and the split payload is **not** the concatenation
(checked: `b1[33] ≠ b9[33] ‖ b9[34]`).

Board 25 is the outlier worth flagging: its tag 33 declares 10 B, and the next 152
bytes are zero, after which sits a well-formed header `22 00 46 02` (tag 34, len 582)
whose payload would run 152 B past the end of the 58,180-byte body. Read naively,
the entry looks truncated; read as the other entries are read, it is a body that
**shipped with a mis-declared tail** `[F]`. Its 434-byte remainder from the tag-34
header is byte-identical to board 9's, so the bytes are present — only the length
bookkeeping is wrong `[F]`.

**Consequences for a parser `[I]`:**

1. Strip a leading ARM ELF if present, then parse TLV. A parser that hardcodes one
   form silently fails on part of the fleet. The ELF's own section names *are*
   trustworthy here (`e_shstrndx` ∈ {4,5,6}, all valid STRTABs), so
   `.data`/`.noinit`/`.persistent` can be located by name rather than by position.
2. Do not compute `b → e` size by a constant. The overhead is a six-variable
   function (`e_shnum` plus three string-table sizes, a pad and a tail), observed
   spanning 1,720–1,956 B upstream and 1,656–1,820 B in the fleet (§9.4a).
3. Do not trust the final IE's declared length, and do not assert
   `consumed == size`. Walk with a bounds check and stop at end-of-body — at least
   one upstream entry contradicts both assumptions.

### 3.4 Size bands

| band | rows | devices | distinct sizes | range |
|---|---:|---:|---:|---|
| < 20 KiB | 16 | 8 | 7 | 6,136 – 19,152 |
| 20–40 KiB | 1,676 | 37 | **1** | 26,328 |
| 40–70 KiB | 2,855 | 22 | 16 | 57,932 – 60,064 |
| 70–130 KiB | 573 | 10 | 8 | 88,728 – 125,420 |

The 20–40 KiB band having exactly one size across 1,676 rows and 37 devices is the
strongest single invariant in the family `[F]`.

### 3.5 The long-form platform tokens are silicon, not phone `[F]`

28 distinct tokens across 163 rows and 17 devices: `bangkk bathena borneo capri
caprip cebu corfup corfuq corfur cypfg cypfq denver devon fogo fogor fogos guam
guamna guamp hawao ibiza miami milanf penang pnangn rhode rhodei rhodep`.

`milanf` appears on **six** devices — `Edge_30_Neo`, `Moto_G34_5G`, `Moto_G82_5G`,
`Moto_G84_5G`, `G_Stylus_5G-2-2022`, `Moto_G_5G_2024` — which span **two** SoCs,
SM6375 (Snapdragon 695) and SM4375 (Snapdragon 4 Gen 1), always as the same
`_epa`/`_ipa` pair. So the token tracks neither the phone nor the SoC
generation `[F]`; it most plausibly names the WiFi module itself `[I]`. (An earlier
draft claimed `milanf` was on `Moto_G200`/SM8350-AC — that device carries no
`milanf` file; corrected by re-measuring `[F]`.)

The 16 `.elf.<region>.<ipa|epa>` rows on 4 devices add region tokens `berlin`,
`berlna`, `dubai` (all `ipa`) and `oberon`, `tundra`, `xpeng` (all `epa`), plus
`ctwo`/`rtwo` with `india`/`na`/`prc`/`row`/`vzw` sub-regions (all `epa`) — 8 tokens,
13 `epa` rows and 3 `ipa` rows `[F]`.

---

## 4. Board-id indexing — from upstream's own symbol tables `[F]`

`cnss2/qmi.c` `cnss_get_bdf_file_name()` is the normative rule: `board_id == 0xFF`
→ `bdwlan.bin` / `bdwlan.elf`; `board_id < 0xFF` → `bdwlan.b%02x` / `bdwlan.e%02x`;
`board_id > 0xFF` → `bdwlan.%02x.b%02x` from `board_id >> 8` and `board_id & 0xFF`.

This is confirmed independently by the ELF `.strtab` of `board-2.bin`'s entries,
which still carry their build-time source filenames:

| QMI board id | entry ELF size | symbol-named source | implied name |
|---:|---:|---|---|
| 1 | 59,900 | `bdwlan_b01` | `bdwlan.b01` |
| 2 | 59,900 | `bdwlan_b02` | `bdwlan.b02` |
| 3 | 59,900 | `bdwlan_b03` | `bdwlan.b03` |
| 4 | 59,900 | `bdwlan_b04` | `bdwlan.b04` |
| 5 | 59,964 | `bdwlan_b05` | `bdwlan.b05` |
| 6 | 59,900 | `bdwlan_b06` | `bdwlan.b06` |
| 7 | 59,900 | `bdwlan_b07` | `bdwlan.b07` |
| 9 | 59,964 | `bdwlan_b09` | `bdwlan.b09` |
| 10 | 59,964 | `bdwlan_b0a` | `bdwlan.b0a` |
| 25 | 59,976 | `bdwlan_b19` | `bdwlan.b19` |
| 255 | 59,900 | `bdwlan_bin` | `bdwlan.bin` |

Command §9.7. Exact on 11 of 11. Board id 25 → `b19` because 25 decimal = 0x19;
255 is the wildcard, named `bdwlan.bin` rather than `bdwlan.bff`.

This answers the open item in [`bdwlan-format.md`](bdwlan-format.md) §10 ("what
selects a variant at runtime"): **the filename suffix is the QMI board id in
lowercase hex** `[F]`. It explains why the suffix space stops at 0x71 and 0xe1
rather than 0xff, and why `bdwlan.bin` exists on 67 of 73 devices.

### 4.1 Board ids above 0xFF — three candidate forms, and only two appear `[F]`

For `board_id > 0xFF` the two reference implementations disagree, so the matrix is
the only arbiter. Both candidate forms are present, on **disjoint** device sets, and
the `cnss2` two-level form is **absent entirely**:

| form | producer | for board_id 0x102 | present in matrix? |
|---|---|---|---|
| `bdwlan.b%02x` | naive `"bdwlan.b" + %02x` (no truncation) | `bdwlan.b102` | as `bdwlan.b101` (3 devices: FP6, Nord_4, Nord_CE4) |
| `bdwlan.%03x` | `wlfwd` | `bdwlan.102` | **yes** — 29 devices, `bdwlan.102`…`bdwlan.206` |
| `bdwlan.%02x.b%02x` | `cnss2` | `bdwlan.01.b02` | **none** — 0 rows |

Three facts, measured `[F]`:

1. The 29 devices carrying `bdwlan.102`-style names and the 3 carrying `bdwlan.b101`
   have **zero overlap**. Every one of the 29 also carries ordinary two-hex files
   (`bdwlan.b04`, `bdwlan.b07`, …); the 3 carry no numeric-name files at all `[F]`.
2. `bdwlan.b101` is exactly what `"bdwlan.b" + "%02x" % 0x101` produces, because C's
   `%02x` is a **minimum** width and does not truncate. It is therefore consistent
   with the same rule as the two-hex family, extended naturally past 0xFF `[I]`.
3. `bdwlan.102` is exactly `"%03x" % 0x102`. The numeric family uses **18 distinct
   suffix values** across 29 devices — `0x102, 0x104–0x109, 0x10b, 0x10c, 0x10e,
   0x10f, 0x111` and `0x201–0x206` — i.e. two ranges, `0x102–0x111` and
   `0x201–0x206`, **with gaps**. An earlier draft called these contiguous; they are
   not. Two ranges still suggest two chip generations sharing a naming tool `[I]`,
   but the missing values mean the suffix is a sparse id, not a counter `[F]`.

The `cnss2` dotted form is not attested anywhere in 5,120 `bdwlan` rows, so on this
fleet it is unused `[F]`. The >0xFF case is thus **vendor-specific**: two conventions
in production, not one rule with exceptions.

**Correction (Rule 1) to `bdwlan-format.md` §5.** That document hypothesises that
the u16 at file offset `[10,12)` is a "board ID / board config selector". Measured
on the upstream bodies, it is not `[F]`:

- **WCN6750 `board-2.bin`** (11 entries, board ids 1…255): 10 distinct values, none
  equal to its board id, and not injective — board id 6 → 3,754 *and* board id 255
  → 3,754, while board id 1 → 59,475.
- **WCN3990 `board-2.bin`** (36 entries): board id `67` alone yields **6 distinct**
  values (36,948 · 39,277 · 41,326 · 41,558 · 42,326 · 43,092), and board id `ff`
  yields **16 distinct** — including 42,326, the very value also carried by the
  `67` entry. The two generic entries `bus=snoc,qmi-board-id=67` and
  `bus=snoc,qmi-board-id=ff` are **byte-identical** (md5 `7a0b6bc520a3…`), so one
  physical body is registered under two different board ids. A field that cannot
  distinguish two identically-served ids cannot be that id.

A second field, `u16@408`, is a *better* discriminator than §5 credited it with but
is still not the id. Its full value set across all 36 entries is only
`{0, 1, 5, 257, 259, 545}`. All 12 `board-id=67` bodies carry 545, and 545 also
appears on the shared body under `board-id=ff`; the other `ff` bodies take
0, 1, 5 and 257, while 259 belongs to the single `board-id=3f` body and 0 also to
`41`/`55`. Six values cannot index 5 board ids injectively, and `ff` alone spans
four of them — so it is a coarse board-class selector, not the board id `[I]`.

So neither field encodes the board id `[F]`. Board selection is by filename, and
`board-2.bin` entries are keyed by the `bus=…,qmi-chip-id=…,qmi-board-id=…` text
string, not by any body field. That document's observation stands, its hypothesis
does not.

**Honest negative `[N]`:** only 24 of the 36 WCN3990 entries are distinct bodies,
and exactly one of those 24 carries **two different board-id labels** (`67` and
`ff`, md5 `7a0b6bc520a3…`), so body content alone cannot determine the board.
(An earlier draft said 10 bodies were shared across labels; re-measured, 10 is the
number of *duplicate entries* within a single label, and the label-collision count
is 1.) No byte-identity between any upstream `board-2.bin` body and any Android
`bdwlan` row could be established — the payloads are not on this machine, only
their sizes and md5s `[N]`.

---

## 5. Which devices carry it `[F]`

**Vendors (73):** motorola 21 · oneplus 18 · xiaomi 13 · sony 7 · google,
fairphone, samsung 3 each · nothing, realme 2 each · fxtec 1.

**The six split-image devices are exactly the six with both `b` and `e`:**

```
wpss.* split image : Edge_30, FP5, FP6, Nord_4, Nord_CE4, Phone_1
both b and e files : Edge_30, FP5, FP6, Nord_4, Nord_CE4, Phone_1
equal? True
```

The fleet partitions into `b`-only (28 devices), `e`-only (26), both (6), and
neither (13, `bdwlan.bin`-only). What that partition *means* is now measured
(§3.3): `b`-only devices carry the raw **26,328**-byte body and `e`-only devices
carry only the ELF-wrapped form. The two groups' part numbers are **completely
disjoint** `[F]`:

```
b-only parts (9): MSM8998 SM4250 SM4375 SM6115 SM6225 SM6375 SM7225 SM8150 SM8150-AC
e-only parts (6): SM7250 SM8250 SM8350 SM8350-AC SM8475 SM8550
overlap: NONE
```

So the split is a clean hardware-generation boundary: everything through SM8150
ships the raw `b` body, everything from SM7250 ships only the wrapped `e` form.
The six `both` devices sit exactly on that boundary (`SM7325-AE` ×2, `QCM6490`,
plus `FP6`/`Nord_4`/`Nord_CE4` whose `soc` is empty) — the first generation to
offer both `[I]`. The set equality with split-`wpss` then follows: those same six
newest-platform products are the only ones whose `modem/image/` tree carries a full
split PIL image *and* dual-form board data.

**Device classes:** the family spans **19 distinct Qualcomm part numbers** from
MSM8998 (Snapdragon 835) through QCM6490 up to SM8550 (Snapdragon 8 Gen 2) — 2017
flagship to 2023 flagship — and includes tablets (`Galaxy_Tab_A7_Wifi`,
`Galaxy_Tab_A7_LTE`, `Pad_Pro`, `Pad_2_Pro`) and a Chromebook-class reference design
as well as phones. Every device class in the matrix with WiFi carries it `[F]`.

**Data-quality notes on the `soc` column `[F]`.** 44 of the 73 devices carry a
populated `soc`; their **21 distinct non-empty strings** collapse to **19 distinct
part numbers**, and the two collapses are both *marketing* variants of one part,
not typos:

| part number | two strings merged |
|---|---|
| `SM6375` | `Qualcomm SM6375 Snapdragon 695` · `ÿQualcomm SM6375 Snapdragon 695 5G` |
| `SM7325-AE` | `Qualcomm SM7325-AE Snapdragon 778G 5G` · `Qualcomm SM7325-AE Snapdragon 778G+ 5G` |

`SM8150`/`SM8150-AC` and `SM8350`/`SM8350-AC` are **not** merges — the `-AC` suffix
is a distinct part number and is counted separately, even though the matrix's own
marketing text for each pair is partly duplicated (`SM8150` and `SM8150-AC` both
read "Snapdragon 855", while `SM8350-AC` reads "888+"). (An earlier draft had this
backwards: it reported 18 part numbers and named the `-AC` pairs as the merges.
Re-measured: 19 parts, and the merges are the two rows above `[F]`.)

Separately, `Nord_CE3`'s `soc` value carries a spurious leading `U+00FF` byte on all
**81** of its `wpss` rows — the sole cause of the `SM6375` merge, and the only
device in the matrix with a non-ASCII `soc` field. Recorded here rather than
silently normalised `[F]`.

**Honest negative `[N]`:** 29 of 73 devices have an empty `soc` column — **all 13
Xiaomi devices**, plus `FP6`, `Nord_4` and `Nord_CE4`. No complete SoC histogram is
derivable from the committed table; it is reported as a gap rather than estimated.

---

## 6. Deduplication leverage `[F]`

| quantity | value |
|---|---:|
| rows | 5,198 |
| distinct md5 | 1,964 |
| total bytes | 317,873,910 |
| unique bytes | 159,408,375 |
| dedupe saving | 158,465,535 (49.85 %) |

| devices carrying it | distinct contents |
|---:|---:|
| 1 | 1,127 |
| 2 | 221 |
| 3 | 151 |
| 4 | 159 |
| 5–7 | 56 |
| 8 | 216 |
| 10–14 | 26 |
| 16, 21, 22 | 8 |

The rows sum to 1,964 — every distinct content is accounted for `[F]`. The single
largest sharing group is **8 devices** (216 contents): the eight Mi 12 / Poco F5
rows of §7. Contents shared by 16, 21 or 22 devices exist but are few (8 contents);
the widest is carried by 22 of the 73 devices.

Half the family's bytes are duplicate copies. One RE pass over the 1,964 distinct
contents covers all 73 devices — that is the leverage number for budgeting work
on this family `[F]`.

---

## 7. Per-device scale `[F]`

| device | bytes | distinct filenames | matrix rows |
|---|---:|---:|---:|
| FP5 | 19,215,739 | 205 | 206 |
| Edge_30_Fusion | 11,855,008 | 198 | 198 |
| Phone_2 | 11,639,824 | 194 | 194 |
| FP6 | 11,581,906 | 70 | 72 |
| Nord_4 | 11,095,209 | 62 | 64 |
| Nord_CE4 | 10,967,929 | 60 | 62 |
| Moto_G200 | 10,955,996 | 183 | 183 |

**A fifth data-quality defect `[F]`.** The matrix has 12 **excess rows** that repeat
an existing `(device, filename)` pair. Eight of the twelve are exact repeats with an
identical `md5_db`; the other four are same-name, *different-content* conflicts:

| device | filename | rows | identical md5? |
|---|---|---:|---|
| FP5 | `bdwlan.bin` | 2 | yes |
| FP6 | `bdwlan.bin`, `wpss.mdt` | 2 each | yes |
| Nord_4 | `bdwlan.bin`, `wpss.mdt` | 2 each | yes |
| Nord_CE4 | `bdwlan.bin`, `wpss.mdt` | 2 each | yes |
| Phone_1 | `bdwlan.bin` | 2 | yes |
| **Nord_CE2** | `bdwlan.bin` | 2 | **no** |
| **Nord_CE3** | `bdwlan.bin` | 2 | **no** |
| **Realme_9_Pro** | `bdwlan.bin` | 2 | **no** |
| **Realme_10_Pro** | `bdwlan.bin` | 2 | **no** |

The last four are the interesting ones: one `(device, filename)` maps to **two
different hashes**, so the table cannot be a pure key — either these devices ship
two different `bdwlan.bin` files from two partitions, or the ingest collapsed a
path distinction. That ambiguity is unresolvable from the committed columns `[N]`.
This is also why the "distinct filenames" and "matrix rows" columns above differ.

The 5,198-row total, and every byte total in this document, **includes** those
duplicates; keying on `(device, filename)` would drop 12 rows. Recorded, not
silently corrected `[F]`.

The eight Xiaomi Mi 12 / Poco F5 devices (`Mi_12`, `Mi_12_Pro`, `Mi_12S`,
`Mi_12S_Pro`, `Mi_12S_Ultra`, `Mi_12T_Pro`, `Poco_F5`, `Poco_F5_Pro`) each carry
10,368,220 B in 173 files, and their **md5 sets are identical** — one content set
duplicated across eight device rows `[F]`.

---

## 8. Open items

| item | status |
|---|---|
| meaning of `ipa` / `epa` | `[N]` — no source found; "IP accelerator" is a guess |
| meaning of `u` / `g` / `s` / `t` infixes | `[N]` — no source found |
| the residual 100 B between `e` overhead (1,820) and measured ELF overhead (1,720) | **resolved** — there is no single overhead; the wrapper is `1,024 + 6` measured terms and 1,820 is one of its values (§3.3, §9.4a) |
| the 1,656 B `b`→`e` delta (1 row) | `[N]` — 6 B below the floor the measured knob sets can produce; needs a real device `e` file to settle |
| why the hash segment is phdr 12 on FP6/Nord_4 but 1 elsewhere | `[H]` — build-order artifact; the fact is measured, the cause is not |
| why the CPU-bearing segment is phdr 5/6 on one generation and 7/8 on the other | `[H]` — same build-order cause as the row above; both move together (§2.5) |
| `u16@10` semantics | `[F]` — proven *not* the board id on two containers (§4.1); meaning still unknown, but it tracks the calibration body, not the id |
| `u16@408` semantics | `[I]` — behaves as a coarse board-class selector; separates `bdwlan_b` generations but also appears on unrelated `ff` bodies |
| TLV tag semantics 18–33 in the 58 KiB generation | open — `bdwlan-format.md` covers 1..17 for the 19 KiB generation only |
| why 2 upstream entries split tag 33 into 33+34 and `Qualcomm_rb3gen2` mis-declares it | `[F]` — three layouts measured (§3.3); the cause is a toolchain difference, unproven |
| whether 19,152 B is a distinct generation or a padded 26,328 B body | `[F]` — same grammar, short form zero-extended to 19,152 B; 3 long entries walk to exactly 19,152 B (§3.2) |
| 29 of 73 devices have empty `soc` | `[N]` — matrix gap, not filled here |
| no byte-identity upstream ↔ Android board data | `[N]` — payloads absent from this machine |
| `bdwlan_<plat>_*` maps to a `WCNxxxx` part number | `[N]` — the matrix carries no chip column; the mapping needs the vendor partition |
| whether `wpss.qdb` is ever read by the loaded firmware | `[N]` — 5 rows on 5 devices in two size classes (515/516 B and 254,139/257,170 B); no format identified; absent from linux-firmware |
| matrix defect: `Nord_CE3` `soc` carries a leading `U+00FF` byte | `[F]` — 81 rows; fix belongs at the source, recorded not patched |

---

## 9. Reproduction

`M` is `upstream-contribution/blob-database/coverage-matrix.csv`. All commands are
stdlib-only under `python3 -I`.

**9.1 Component split (§1)**
```sh
python3 -I -c "
import csv
from collections import defaultdict
rows=[r for r in csv.DictReader(open('$M')) if r['blob_subfamily']=='wpss']
k=lambda f:'wpss_split' if f.startswith('wpss.') else 'wlanpdr' if f.startswith('wlanpdr') else 'bdwlan'
d=defaultdict(list)
for r in rows: d[k(r['filename'])].append(r)
for n,v in sorted(d.items()): print(n,len(v),len({x['device'] for x in v}),len({x['md5_db'] for x in v}),sum(int(x['size_bytes']) for x in v))
"
```

**9.2 `b00` is header+phdr, and which segment `.mdt` adds (§2.3, §2.4)**
```sh
python3 -I -c "
import csv
from collections import defaultdict
rows=[r for r in csv.DictReader(open('$M')) if r['blob_subfamily']=='wpss' and r['filename'].startswith('wpss.')]
by=defaultdict(dict)
for r in rows: by[r['device']][r['filename'].replace('wpss.','')]=int(r['size_bytes'])
for d,f in sorted(by.items()):
    need=f['mdt']-f['b00']
    print(d,'b00',f['b00'],'phnum',(f['b00']-52)//32,'mdt-b00',need,
          'matches',[k for k,v in f.items() if k.startswith('b') and k!='b00' and v==need])
"
```

**9.3 Naming families (§3.1, §3.5)**
```sh
python3 -I -c "
import csv,re
from collections import Counter
rows=[r for r in csv.DictReader(open('$M')) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
def fam(f):
    if f.endswith('.xz'): return 'bdwlan.*.xz'
    if re.match(r'^bdwlan\.elf\.',f): return 'bdwlan.elf.<region>.<ipa|epa>'
    if re.match(r'^bdwlan\.[be][0-9a-f]{3}\$',f): return 'bdwlan.[be]NNN'
    if re.match(r'^bdwlan\.[be][0-9a-f]{2}\$',f): return 'bdwlan.[be]NN'
    if re.match(r'^bdwlan\.[0-9][0-9a-f]{2}\$',f): return 'bdwlan.NNN'
    if f in ('bdwlan.bin','bdwlan.elf'): return 'bdwlan.bin / bdwlan.elf'
    if re.match(r'^bdwlan_[a-z0-9]+(_[a-z0-9]+)*_(ipa|epa)\.bin\$',f): return 'bdwlan_<plat>_<region>_<ipa|epa>.bin'
    if re.match(r'^bdwlan_[a-z0-9]+\.(bin|elf)\$',f): return 'bdwlan_<name>.bin / .elf'
    if re.match(r'^bdwlan[ugst]\.',f): return 'bdwlan[u/g/s/t].x'
    if re.match(r'^bdwlan[ugst][0-9a-z]',f): return 'bdwlan[u/g/s/t]x'
    if re.match(r'^bdwlan-',f): return 'bdwlan-<pixel>.bin'
    if re.match(r'^bdwlanb\d+\.bin\$',f): return 'bdwlanb<N>.bin'
    return 'OTHER:'+f
c=Counter(); B=Counter(); D={}
for r in rows:
    k=fam(r['filename']); c[k]+=1; B[k]+=int(r['size_bytes']); D.setdefault(k,set()).add(r['device'])
for k,v in sorted(c.items(),key=lambda x:-x[1]):
    print('| %-42s | %5d | %2d | %d |'%(k,v,len(D[k]),B[k]))
print('TOTAL',sum(c.values()),sum(B.values()),'residual',sum(v for k,v in c.items() if k.startswith('OTHER')))
"
```
Output: the eleven rows of §3.1 in the same order, `TOTAL 5120 270399184 residual 0`.

The infix breakdown of §3.1 follows from the same rows:
```sh
python3 -I -c "
import csv,re
from collections import Counter
rows=[r for r in csv.DictReader(open('$M')) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
for p in ('g','u','s','t'):
    g=[r for r in rows if re.match(r'^bdwlan'+p+r'[\.0-9a-z]',r['filename'])]
    print(p,len(g),len({r['device'] for r in g}),sorted({r['filename'] for r in g})[:4])
print('g&u devices',sorted({r[\"device\"] for r in rows if r['filename'].startswith('bdwlang')}&{r[\"device\"] for r in rows if r['filename'].startswith('bdwlanu')}))
"
```
Output: `g 183 12`, `u 34 19`, `t 7 7`, `s 4 4`, and an empty `g&u` intersection.

**9.4 `b` size set and the `b`→`e` deltas (§3.2, §3.3)**
```sh
python3 -I -c "
import csv,re
from collections import Counter,defaultdict
rows=[r for r in csv.DictReader(open('$M')) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
print(Counter(int(r['size_bytes']) for r in rows if re.match(r'^bdwlan\.b[0-9a-f]{2}\$',r['filename'])))
dev=defaultdict(dict)
for r in rows:
    m=re.match(r'^bdwlan\.([be])([0-9a-f]{2})\$',r['filename'])
    if m: dev[r['device']][(m.group(1),m.group(2))]=int(r['size_bytes'])
p=Counter()
for f in dev.values():
    for (k,s),v in f.items():
        if k=='b' and ('e',s) in f: p[(v,f[('e',s)])]+=1
for k,v in p.most_common(): print(k, v)
"
```

**9.4a The ELF wrapper decomposes exactly, and `b`-only vs `e`-only is a chip-generation split (§3.3)**

The first part reads the three upstream containers and proves every overhead
equals `1024 + symtab + symstr + shstr + 40·shnum + pad + tail`:

```sh
python3 -I <<'PY'
import struct
from collections import Counter
def entries(p):
    d=open(p,'rb').read(); pos=20; out=[]
    while pos+8<=len(d):
        i,n=struct.unpack_from('<II',d,pos)
        if not n or pos+8+n>len(d): break
        b=d[pos+8:pos+8+n]
        if i==0:
            t,nl=struct.unpack_from('<II',b,0); name=b[8:8+nl].decode('latin1')
            off=(8+nl+3)&~3
            dt,dl=struct.unpack_from('<II',b,off)
            out.append((name,b[off+8:off+8+dl],dt))
        pos+=8+n
    assert pos==len(d),('walk did not consume file',p,pos,len(d))
    ne=sum(1 for x in out if x[2]==1 and x[1][:4]==b'\x7fELF')
    assert (len(out),ne)==EXP[p],('stale or truncated container',p,len(out),ne,EXP[p])
    print(p,'entries',len(out),'elf',ne,'build guard OK')
    return out
EXP={'ath11k_WCN6750_hw1.0_board-2.bin':(11,11),
     'ath11k_WCN6855_hw2.0_board-2.bin':(123,118)}
shn=Counter(); bad=0; tot=0
for p in ('ath11k_WCN6750_hw1.0_board-2.bin','ath11k_WCN6855_hw2.0_board-2.bin'):
    for name,data,dt in entries(p):
        if dt!=1 or not data.startswith(b'\x7fELF'): continue
        e=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
        phoff,shoff,shnum,shse=e[4],e[5],e[11],e[10]
        poff,pfsz=struct.unpack_from('<II',data,phoff+4)[0],struct.unpack_from('<II',data,phoff+20)[0]
        sym=0; strs=[]
        for j in range(shnum):
            nm,ty,fl,ad,so,sz=struct.unpack_from('<IIIIII',data,shoff+j*shse)
            if ty==2: sym=sz
            if ty==3: strs.append(sz)
        strs.sort(); shstr=strs[-1]; symstr=sum(strs[:-1])
        gap=shoff-(poff+pfsz); pad=gap-(sym+symstr+shstr)
        tail=len(data)-(shoff+shnum*shse)
        if poff+sym+symstr+shstr+pad+shnum*shse+tail != len(data)-pfsz: bad+=1
        shn[shnum]+=1; tot+=1
print('entries',tot,'violations',bad,'shnum counts',dict(sorted(shn.items())))
for s in (59900,59964,59976):
    for name,data,dt in entries('ath11k_WCN6750_hw1.0_board-2.bin'):
        if dt!=1 or len(data)!=s: continue
        e=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
        print(s,'e_shstrndx',e[12],'e_flags',e[6],[x for x in entries('ath11k_WCN6750_hw1.0_board-2.bin') if x[1]==data][0][0][:46])
        break
PY
```
Output: `entries 129 violations 0 shnum counts {5: 46, 6: 10, 7: 73}`, and
`e_shstrndx` 6 / 5 / 4 for the 59,976 / 59,964 / 59,900 B samples — each a valid
`SHT_STRTAB`, so sections **are** named (see §3.3 for the corrected reading; an
earlier draft printed `e[6]`, which is `e_flags`, and wrongly concluded the
opposite).

**The `assert` on entry count is not decoration — it is the difference between a
real result and a plausible wrong one.** Both failure modes produce a *shorter
container that parses cleanly*, so `consumed == len(file)` catches neither:

| failure | symptom | caught by |
|---|---|---|
| truncated download | walk ends early, `consumed < len` | `consumed == len` |
| **stale packaged build** | `consumed == len`, zero remainder, **fewer entries** | entry-count assert **only** |

The second case is the dangerous one. A distro `linux-firmware` package a few
months behind yields 106 ELF entries from WCN6855 and 10 from WCN6750 — a
self-consistent container that decomposes with zero violations and reproduces
every *qualitative* claim while making the *quantitative* ones (129 entries,
`shnum {5:46, 6:10, 7:73}`) silently wrong. A reader who checks only the grammar
would "confirm" a decomposition that is off by thirteen entries `[F]`. So the
script asserts `(entries, elf) == (11, 11)` and `(123, 118)`; the md5 of the
current WCN6855 container is `2ac84328cf0b69f373817a6faf2a24e4` (7,479,440 B).
(`entries` counts only `ie_id == 0` records, so WCN6855's 126 on-disk records are
123 `ie_id=0` + 3 `ie_id=1`; the 118 ELF bodies all sit in the `ie_id=0` set.)

Appending this to the same script prints the measured knob space and shows which
fleet deltas it can reconstruct (§3.3):

```sh
python3 -I -c "
import itertools
S=[256,272,288]; SS=[33,41,53]
SH=[149,173,179,182,218,221,224,236,272,278,302,311,314,323]
N=[5,6,7]; P=[0,1,2,3]; T=[0,32]
print('floor',1024+min(S)+min(SS)+min(SH)+40*min(N)+min(P)+min(T))
for d in (1656,1688,1752,1820):
    n=sum(1 for s,ss,sh,k,p,t in itertools.product(S,SS,SH,N,P,T)
          if 1024+s+ss+sh+40*k+p+t==d)
    print(d,n)
"
```
Output: `floor 1662`, then `1656 0`, `1688 2`, `1752 10`, `1820 13`.

The second part shows the fleet's `b`/`e` partition is the chip generation:

```sh
python3 -I -c "
import csv,re
from collections import defaultdict
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
dev=defaultdict(lambda:{'b':set(),'e':set()})
for r in rows:
    m=re.match(r'^bdwlan\.([be])([0-9a-f]{2,3})\$',r['filename'])
    if m: dev[r['device']][m.group(1)].add(int(r['size_bytes']))
bonly=[d for d,v in dev.items() if v['b'] and not v['e']]
eonly=[d for d,v in dev.items() if v['e'] and not v['b']]
both =[d for d,v in dev.items() if v['e'] and v['b']]
print('b-only',len(bonly),'all sizes 26328:',all(dev[d]['b']=={26328} for d in bonly))
print('e-only',len(eonly),'min e size:',min(s for d in eonly for s in dev[d]['e']))
print('both',len(both),sorted(both))
"
```
Output: `b-only 28 all sizes 26328: True`, `e-only 26 min e size: 57932`,
`both 6 ['Edge_30','FP5','FP6','Nord_4','Nord_CE4','Phone_1']` — the same six as §9.9's
split-`wpss` set.

The third part proves the two groups' part numbers are disjoint (§5):

```sh
python3 -I -c "
import csv,re
from collections import defaultdict
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
soc={}
for r in rows: soc.setdefault(r['device'],r['soc'])
dev=defaultdict(lambda:{'b':0,'e':0})
for r in rows:
    m=re.match(r'^bdwlan\.([be])([0-9a-f]{2,3})\$',r['filename'])
    if m: dev[r['device']][m.group(1)]+=1
part=lambda s:(re.match(r'^.{0,2}Qualcomm (\S+)',s) or [None,None])[1]
bs={part(soc[d]) for d,v in dev.items() if v['b'] and not v['e']} - {None}
es={part(soc[d]) for d,v in dev.items() if v['e'] and not v['b']} - {None}
print('b-only',sorted(bs)); print('e-only',sorted(es)); print('overlap',sorted(bs&es) or 'NONE')
"
```
Output: `b-only ['MSM8998','SM4250','SM4375','SM6115','SM6225','SM6375','SM7225','SM8150','SM8150-AC']`,
`e-only ['SM7250','SM8250','SM8350','SM8350-AC','SM8475','SM8550']`, `overlap NONE`.

**9.5 Nested ELF roles and the RISC-V attribute string (§2.2, §2.6)**
```sh
curl -sSL -o wpss_qcm6490.mbn \
  https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/ath11k/WCN6750/hw1.0/qcm6490/wpss.mbn
python3 -I -c "
import struct
d=open('wpss_qcm6490.mbn','rb').read()
e=struct.unpack_from('<HHIIIIIHHHHHH',d,16); phoff,pn=e[4],e[9]
print('phnum',pn,'header+phdr',52+32*pn)
for i in range(pn):
    t,off,va,pa,fs,ms,f,al=struct.unpack_from('<IIIIIIII',d,phoff+i*32)
    nested=''
    if d[off:off+4]==b'\x7fELF':
        n=struct.unpack_from('<HHIIIIIHHHHHH',d,off+16)
        nested='nested machine=%d entry=%#x'%(n[1],n[3])
    print(i,hex(t),hex(f),fs,'HASH' if (f&0x7000000)==0x2000000 else '',nested)
for i in range(pn):
    t,off,va,pa,fs,ms,f,al=struct.unpack_from('<IIIIIIII',d,phoff+i*32)
    if d[off:off+4]==b'\x7fELF' and struct.unpack_from('<H',d,off+18)[0]==243:
        b=off; s=struct.unpack_from('<HHIIIIIHHHHHH',d,b+16)
        shoff,sn,si,se=s[5],s[11],s[12],s[10]
        o=b+shoff+si*se; nm,ty,fl,ad,so,sz=struct.unpack_from('<IIIIII',d,o)
        st=d[b+so:b+so+sz]
        for j in range(sn):
            o=b+shoff+j*se; nm,ty,fl,ad,so,sz=struct.unpack_from('<IIIIII',d,o)
            name=st[nm:st.find(b'\x00',nm)].decode()
            if 'riscv' in name:
                blob=d[b+so:b+so+sz]
                p=blob.find(b'rv32')
                print(name, blob[p:blob.find(b'\x00',p)].decode())
"
```
`sc7280/wpss.mbn` (HTTP 200, 7,463,728 B) is the same procedure. Both fetched 2026-11-20.

The `e_machine=3` / Cortex-M3 claim (§2.6) is a separate measurement:
```sh
python3 -I -c "
import struct,math
from collections import Counter
for fn in ('wpss_sc7280.mbn','wpss_qcm6490.mbn'):
    d=open(fn,'rb').read()
    phoff=struct.unpack_from('<I',d,28)[0]; pn=struct.unpack_from('<H',d,44)[0]
    for i in range(pn):
        t,off,va,pa,fs,ms,f,al=struct.unpack_from('<IIIIIIII',d,phoff+i*32)
        if fs and d[off:off+4]==b'\x7fELF' and struct.unpack_from('<H',d,off+18)[0]==3:
            shoff=struct.unpack_from('<I',d,off+32)[0]; sn=struct.unpack_from('<H',d,off+48)[0]
            si=struct.unpack_from('<H',d,off+50)[0]
            S=[struct.unpack_from('<IIIIIIIIII',d,off+shoff+j*40) for j in range(sn)]
            base=S[si][4]
            for s in S:
                nm=d[off+base+s[0]:].split(b'\x00')[0]
                if nm==b'.data':
                    b=d[off+s[4]:off+s[4]+s[5]]
                    c=Counter(b); n=len(b)
                    H=-sum(v/n*math.log2(v/n) for v in c.values())
                    j2=len(b)
                    while j2 and b[j2-1]==0: j2-=1
                    print(fn,'ph%d filesz=%d'%(i,fs),'.data addr=%#x size=%d'%(s[3],n),
                          'entropy=%.3f'%H,'nonzero=%d'%sum(1 for x in b if x),'pad=%d'%(n-j2))
                if nm==b'.strtab':
                    for sym in d[off+s[4]:off+s[4]+s[5]].split(b'\x00'):
                        if b'pcss_m3' in sym: print('   sym:',sym.decode())
"
```
Output: both builds `ph6 filesz=266684`, `.data addr=0x4ff00000 size=262144`,
`pad=2319`, three `_binary_padded_pcss_m3_tx_rx_bin_*` symbols; entropy 5.508
(`sc7280`) and 5.524 (`qcm6490`), non-zero 173,805 and 174,581 respectively.

**9.5a `board-2.bin` TLV tail layouts (§3.3)**
```sh
python3 -I -c "
import struct,re
d=open('ath11k_WCN6750_hw1.0_board-2.bin','rb').read(); pos=20
while pos+8<=len(d):
    i,n=struct.unpack_from('<II',d,pos)
    if not n or pos+8+n>len(d): break
    b=d[pos+8:pos+8+n]
    if i==0:
        t,nl=struct.unpack_from('<II',b,0); name=b[8:8+nl].decode('latin1')
        if name.startswith('bus='):
            off=(8+nl+3)&~3; dt,dl=struct.unpack_from('<II',b,off); data=b[off+8:off+8+dl]
            e=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
            S=[struct.unpack_from('<IIIIIIIIII',data,e[5]+j*e[10]) for j in range(e[11])]
            base=S[e[12]][4]
            for sh in S:
                if data[base+sh[0]:].split(b'\x00')[0]==b'.data':
                    dd=data[sh[4]:sh[4]+sh[5]]; q=0; tags=[]
                    while q+4<=len(dd):
                        tg,ln=struct.unpack_from('<HH',dd,q)
                        if tg==0 and ln==0: break
                        tags.append((tg,ln)); q+=4+ln
                    bid=re.search(r'qmi-board-id=(\d+)',name).group(1)
                    print('%-4s tags=%2d consumed=%5d/%d last=%s tail=%d'%(
                        bid,len(tags),q,len(dd),tags[-1],len(dd)-q))
    pos+=8+n
"
```
Output: boards 1–7 and 255 → 33 tags, last `(33,596)`, tail 0; boards 9 and 10 →
34 tags, last `(34,582)`; board 25 → 33 tags, last `(33,10)`, tail 586.

**9.5b Which build each device matches (§2.2)**
```sh
python3 -I -c "
import csv,struct
from collections import defaultdict
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss' and r['filename'].startswith('wpss.')]
by=defaultdict(dict)
for r in rows: by[r['device']][r['filename'][5:]]=int(r['size_bytes'])
def phrs(fn):
    d=open(fn,'rb').read()
    phoff=struct.unpack_from('<I',d,28)[0]; pn=struct.unpack_from('<H',d,44)[0]
    return [struct.unpack_from('<IIIIIIII',d,phoff+i*32)[4] for i in range(pn)]
for fn,nm in (('wpss_sc7280.mbn','sc7280'),('wpss_qcm6490.mbn','qcm6490')):
    ref=phrs(fn)
    for d in ('Edge_30','FP5','Phone_1'):
        hits=[i for i in range(len(ref)) if ref[i] and by[d].get('b%02d'%i)==ref[i]]
        print('%-8s vs %-7s %d/%d exact at %s'%(d,nm,len(hits),sum(1 for x in ref if x),hits))
"
```
Output: `sc7280` → 4, 5, 6 exact for Edge_30/FP5/Phone_1; `qcm6490` → 4, 5, 4.
**9.6 Upstream `board-2.bin` bodies vs matrix `b` sizes (§3.2)**
```sh
for f in ath10k/WCN3990/hw1.0/board-2.bin ath11k/WCN6750/hw1.0/board-2.bin ath11k/WCN6855/hw2.0/board-2.bin; do
  curl -sSL -o "$(echo $f | tr / _)" \
    "https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/$f"
done
python3 -I -c "
import struct
for p in ('ath10k_WCN3990_hw1.0_board-2.bin','ath11k_WCN6750_hw1.0_board-2.bin','ath11k_WCN6855_hw2.0_board-2.bin'):
    d=open(p,'rb').read(); pos=20; sizes=set()
    while pos+8<=len(d):
        i,n=struct.unpack_from('<II',d,pos)
        if not n or pos+8+n>len(d): break
        b=d[pos+8:pos+8+n]
        if i==0:
            t,nl=struct.unpack_from('<II',b,0); off=(8+nl+3)&~3
            dt,dl=struct.unpack_from('<II',b,off); data=b[off+8:off+8+dl]
            if dt==1:
                if data[:4]==b'\x7fELF':
                    s=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
                    for j in range(s[11]):
                        o=s[5]+j*s[10]; nm,ty,fl,ad,so,sz=struct.unpack_from('<IIIIII',data,o)
                        if ty==1 and sz>1000: sizes.add(sz)
                else: sizes.add(len(data))
        pos+=8+n
    print(p,sorted(sizes))
"
```

**9.6a 19,152 B is a zero-padded 26,328 B body (§3.2)**
```sh
python3 -I -c "
import struct
d=open('ath10k_WCN3990_hw1.0_board-2.bin','rb').read()
seen=set()
for i in range(60,len(d)-8):
    if d[i:i+4]==b'\x01\x00\x04\x04':
        ln=struct.unpack_from('<I',d,i-4)[0]
        if ln!=26328: continue
        k=i-8
        while k>0 and 32<=d[k-1]<127: k-=1
        nm=d[k:i-8].decode('latin1')
        if not nm.startswith('bus=') or nm in seen: continue
        seen.add(nm); b=d[i:i+ln]; q=0
        while q+4<=len(b):
            tg,l2=struct.unpack_from('<HH',b,q)
            if tg==0 and l2==0: break
            q+=4+l2
        if q!=ln: print('%-70s consumed %d tail %d allzero %s'%(nm[:70],q,ln-q,set(b[q:])=={0}))
"
```
Output: exactly 3 of the 28 long entries — `xiaomi_beryllium`, `Google_blueline`,
`Google_crosshatch` — consume 19,152 B and carry 7,176 zero bytes.

**9.7 Board-id → filename from `.strtab` (§4)**
```sh
python3 -I -c "
import struct,re
d=open('ath11k_WCN6750_hw1.0_board-2.bin','rb').read(); pos=20
while pos+8<=len(d):
    i,n=struct.unpack_from('<II',d,pos)
    if not n or pos+8+n>len(d): break
    b=d[pos+8:pos+8+n]
    if i==0:
        t,nl=struct.unpack_from('<II',b,0); name=b[8:8+nl].decode()
        off=(8+nl+3)&~3; dt,dl=struct.unpack_from('<II',b,off); data=b[off+8:off+8+dl]
        s=struct.unpack_from('<HHIIIIIHHHHHH',data,16)
        for j in range(s[11]):
            o=s[5]+j*s[10]; nm,ty,fl,ad,so,sz=struct.unpack_from('<IIIIII',data,o)
            if ty==3:
                for sym in data[so:so+sz].split(b'\x00'):
                    if sym.startswith(b'_binary') and b'_start' in sym: print(name,'->',sym.decode())
    pos+=8+n
"
```

**9.8 `u16@10` and `u16@408` are not the board id (§4 correction)**
```sh
python3 -I -c "
import struct,re
from collections import defaultdict
d=open('ath10k_WCN3990_hw1.0_board-2.bin','rb').read(); pos=20
rows=[]
while pos+8<=len(d):
    i,n=struct.unpack_from('<II',d,pos)
    if not n or pos+8+n>len(d): break
    b=d[pos+8:pos+8+n]
    if i==0:
        t,nl=struct.unpack_from('<II',b,0); name=b[8:8+nl].decode()
        off=(8+nl+3)&~3; dt,dl=struct.unpack_from('<II',b,off); data=b[off+8:off+8+dl]
        if dt==1 and len(data) in (19152,26328):
            rows.append((name,struct.unpack_from('<H',data,10)[0],struct.unpack_from('<H',data,408)[0]))
    pos+=8+n
by=defaultdict(set)
for n,u10,u408 in rows: by[re.search(r'qmi-board-id=(\w+)',n).group(1)].add(u10)
for k in sorted(by): print('board-id',k,'->',len(by[k]),'distinct u16@10',sorted(by[k]))
print('u16@408 values:',sorted({r[2] for r in rows}))
print('board-id=67 rows all @408==545?',all(r[2]==545 for r in rows if 'qmi-board-id=67' in r[0]))
print('identical generic body (67 vs ff)?', rows[0][1:]==rows[1][1:])
"
```
The last line is the decisive one: the two generic entries carry the same `u16@10`
and the same `u16@408`. Confirm they are the same *body* by hashing:
```sh
python3 -I -c "
import struct,hashlib,re
from collections import defaultdict
d=open('ath10k_WCN3990_hw1.0_board-2.bin','rb').read()
rows=[]
for i in range(60,len(d)-8):
    if d[i:i+4]==b'\x01\x00\x04\x04':
        ln=struct.unpack_from('<I',d,i-4)[0]
        if ln not in (26328,19152): continue
        k=i-8
        while k>0 and 32<=d[k-1]<127: k-=1
        nm=d[k:i-8].decode('latin1')
        if nm.startswith('bus='): rows.append((nm,d[i:i+ln]))
g=defaultdict(set)
for nm,b in rows: g[hashlib.md5(b).hexdigest()].add(re.search(r'qmi-board-id=([0-9a-f]+)',nm).group(1))
print('entries',len(rows),'distinct bodies',len(g))
print('bodies with >1 board-id label:',[(k[:12],sorted(v)) for k,v in g.items() if len(v)>1])
"
```
Output: 36 entries, **24** distinct bodies, and exactly **one** body carrying two
labels (`67` and `ff`).

For WCN6750 substitute the ath11k container parser (§9.6/§9.7) and read the
`.data` body; the printed `u16@10` set has 10 members for 11 board ids, with
board id 6 and 255 both yielding 3,754, and `u16@408` taking only `{0, 1}`.

**9.9 Dedupe and device partition (§5, §6)** — build `md5_db → size_bytes` once and
sum; and intersect the device set of `wpss.*` with the set having both
`bdwlan.b[0-9a-f]{2}` and `bdwlan.e[0-9a-f]{2}`:
```sh
python3 -I -c "
import csv,re
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss']
m={}
for r in rows: m.setdefault(r['md5_db'],int(r['size_bytes']))
t=sum(int(r['size_bytes']) for r in rows); u=sum(m.values())
print('rows',len(rows),'distinct md5',len(m),'total',t,'unique',u,'saving',t-u)
sp={r['device'] for r in rows if r['filename'].startswith('wpss.')}
bd=[r for r in rows if r['filename'].startswith('bdwlan')]
b={r['device'] for r in bd if re.match(r'^bdwlan\.b[0-9a-f]{2}\$',r['filename'])}
e={r['device'] for r in bd if re.match(r'^bdwlan\.e[0-9a-f]{2}\$',r['filename'])}
all={r['device'] for r in bd}
print('split-device set == both-b-and-e set?',sp==(b&e))
print('both',len(b&e),'b-only',len(b-e),'e-only',len(e-b),'neither',len(all-b-e))
"
```

**9.10 Shared content sets (§5 SoC note, §7)**
```sh
python3 -I -c "
import csv
from collections import defaultdict
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss']
dev=defaultdict(lambda:[0,0])
for r in rows:
    dev[r['device']][0]+=int(r['size_bytes']); dev[r['device']][1]+=1
tgt=sorted(d for d in dev if dev[d][0]==10368220)
print('devices at 10,368,220 B:',tgt)
s={d:frozenset(r['md5_db'] for r in rows if r['device']==d) for d in tgt}
print('all md5 sets identical?',len(set(s.values()))==1)
print('non-ascii soc devices:',sorted({r['device'] for r in rows if r['soc'] and not r['soc'].isascii()}))
"
```

**9.11 Board ids above 0xFF (§4.1)**
```sh
python3 -I -c "
import csv,re
M='upstream-contribution/blob-database/coverage-matrix.csv'
rows=[r for r in csv.DictReader(open(M)) if r['blob_subfamily']=='wpss' and r['filename'].startswith('bdwlan')]
f={r['filename'] for r in rows}
print('cnss2 dotted form:',sorted(x for x in f if re.match(r'^bdwlan\.[0-9a-f]{2}\.[be][0-9a-f]{2}\$',x)) or 'NONE')
print('three-hex b/e    :',sorted(x for x in f if re.match(r'^bdwlan\.[be][0-9a-f]{3}\$',x)))
print('numeric          :',sorted(x for x in f if re.match(r'^bdwlan\.[0-9][0-9a-f]{2}\$',x)))
n={r['device'] for r in rows if re.match(r'^bdwlan\.[0-9][0-9a-f]{2}\$',r['filename'])}
h={r['device'] for r in rows if re.match(r'^bdwlan\.[be][0-9a-f]{3}\$',r['filename'])}
print('numeric devices',len(n),'three-hex devices',len(h),'overlap',sorted(n&h))
print('bdwlan.b%02x of 0x101 =','bdwlan.b%02x' % 0x101,' %03x of 0x102 =','bdwlan.%03x' % 0x102)
"
```
