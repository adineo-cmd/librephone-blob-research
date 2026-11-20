# CDSP split-MDT container + ISA — OnePlus 8 (`instantnoodle`), issue #595

Provenance: generated 2026-11-20 for `adineo-cmd/open-device` issue #595.
Producer: `research/cdsp-fleet/cdsp_container_probe.py` (stdlib only, `python3 -I`),
machine-readable output `research/cdsp-fleet/container.json`.
Read-only data root: `data-fetch/`. Nothing was written outside `/tmp/opencode/cdsp-595`.

Run:

```
cd research/cdsp-fleet && python3 -I cdsp_container_probe.py --json container.json
```

To reproduce §7 (the second device), the enchilada payload must first be extracted from
the FAT16 volume inside `enchilada/modem.img` — the image is not a loose file tree — and
then handed to the probe with `--mdt`:

```
python3 -I <repo>/analysis/fat_extract.py data-fetch/enchilada/modem.img /tmp/ench
cd research/cdsp-fleet && python3 -I cdsp_container_probe.py --mdt /tmp/ench/CDSP.MDT
```

Without `--mdt` the probe reads its default subject,
`second-device/instantnoodle/modem-fat-lfn/image_cdsp.mdt`. Both invocations are
byte-stable across runs.

Output is byte-identical across repeated runs (verified by `diff` on two independent
runs and on the emitted JSON).

Evidence classes used throughout:

- `[F]` fact — read directly out of the bytes, or a rule from a named public source that
  the bytes agree with exactly.
- `[I]` inference — a statistical or structural argument that is strong but not proof.
- `[H]` hypothesis — plausible, not established here.
- `[N]` honest negative — something that was checked and is absent, or a claim that
  could not be substantiated.

Scope discipline: only hashes, sizes, offsets, counts and ≤16-byte hex samples are
reproduced. No payload bytes, no full disassembly, no re-hosted firmware.

## 0. Subject and identity

- `[F]` Subject file: `second-device/instantnoodle/modem-fat-lfn/image_cdsp.mdt`,
  **7660 bytes**, sha256 `f6565bb5d676903b51412d518d10888e6be815547bd7ceca0e16bec6b9e1d71a`,
  md5 `bb2c76540ca66d4a248c200b89a2cbb8`.
- `[F]` Sibling set actually present in the same directory: `b00` 468, `b01` 7192,
  `b02` 235420, `b03` 105980, `b04` 1076, `b05` 2803308, `b06` 83426, `b08` 830592,
  `b09` 2800, `b11` 59156. There is **no** `b07`, `b10`, `b12`.
- `[F]` `cdsp.mdt` is only 7660 B while the payload is 4,129,418 B: the `.mdt` is not a
  copy of the payload — it carries only segments 0 and 1 (see §2).

## 1. ELF header (52 bytes, `Elf32_Ehdr`)

- `[F]` The file starts with a well-formed ELF32 little-endian header. Field order and
  sizes are the ELF gABI `Elf32_Ehdr` layout; the values below are measured.

| field | offset | size | value | note |
|---|---|---|---|---|
| `e_ident` | 0 | 16 | `7f454c46010101000000000000000000` | `\x7fELF`, `ELFCLASS32`, `ELFDATA2LSB`, `EV_CURRENT`, `ELFOSABI_SYSV` |
| `e_type` | 16 | 2 | `2` | `ET_EXEC` |
| `e_machine` | 18 | 2 | `164` (`0xa4`) | `EM_HEXAGON` (`EM_QDSP6`), `include/uapi/linux/elf-em.h` |
| `e_version` | 20 | 4 | `1` | `EV_CURRENT` |
| `e_entry` | 24 | 4 | `0x87800000` | matches `phdr[2].p_paddr` — the segment-2 load address |
| `e_phoff` | 28 | 4 | `52` (`0x34`) | immediately after the header |
| `e_shoff` | 32 | 4 | `0` | no section headers |
| `e_flags` | 36 | 4 | `0x00000066` | Hexagon ISA nibble `0x066` = V66; high bits zero |
| `e_ehsize` | 40 | 2 | `52` | equals `sizeof(Elf32_Ehdr)` |
| `e_phentsize` | 42 | 2 | `32` | equals `sizeof(Elf32_Phdr)` |
| `e_phnum` | 44 | 2 | `13` | 13 program headers |
| `e_shentsize` | 46 | 2 | `40` | vestigial; `e_shnum` is 0 |
| `e_shnum` | 48 | 2 | `0` | sectionless image |
| `e_shstrndx` | 50 | 2 | `0` | `SHN_UNDEF` |

- `[F]` `e_ehsize`/`e_phentsize` agreeing with the gABI struct sizes, and
  `e_phoff == e_ehsize`, mean the header is a real `Elf32_Ehdr`, not a re-purposed
  blob. `[F]` `e_shnum == 0` means everything structural is in the program headers —
  this is a loadable image, not a linkable object.
- `[F]` `e_entry == phdr[2].p_paddr` (`0x87800000`) is self-consistent: the entry point
  is the first byte of the first code-mapped segment's physical address.
- `[I]` The `p_vaddr`/`p_paddr` split in §2 (vaddrs `0xfe…`/`0xc0…`/`0x01…`/`0x74…` vs
  paddrs in a contiguous `0x87800000`-based range) is the standard Qualcomm split-MDT
  convention where `p_paddr` is the firmware-relative load offset and `p_vaddr` is the
  DSP's own virtual mapping. This is consistent with `mdt_loader.c` loading by
  `p_paddr`, but the file alone does not prove which field the loader honours.

## 2. Program headers — 13 rows, sibling files, and the size rule

- `[F]` 13 × 32-byte `Elf32_Phdr` records at offset 52. Table as measured
  (`type` 0=`PT_NULL`, 1=`PT_LOAD`):

| i | type | offset | vaddr | paddr | filesz | memsz | flags | sibling | verdict |
|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | `0x0` | `0x00000000` | `0x00000000` | 468 | 0 | `0x07000000` | 468 | MATCH |
| 1 | 0 | `0x1000` | `0x88c00000` | `0x88c00000` | 7192 | 8192 | `0x02200000` | 7192 | MATCH |
| 2 | 1 | `0x3000` | `0xfe000000` | `0x87800000` | 235420 | 720896 | `0x08000005` | 235420 | MATCH |
| 3 | 1 | `0x3d000` | `0xfe0b0000` | `0x878b0000` | 105980 | 106496 | `0x08000005` | 105980 | MATCH |
| 4 | 1 | `0x57000` | `0xc00ca000` | `0x878ca000` | 1076 | 4096 | `0x08000005` | 1076 | MATCH |
| 5 | 1 | `0x58000` | `0xc00cb000` | `0x878cb000` | 2803308 | 5218304 | `0x08000007` | 2803308 | MATCH |
| 6 | 1 | `0x305000` | `0xc05c5000` | `0x87dc5000` | 83426 | 86016 | `0x08000006` | 83426 | MATCH |
| 7 | 1 | `0x31a000` | `0xc05da000` | `0x87dda000` | 0 | 155648 | `0x08000004` | — | ABSENT-as-predicted |
| 8 | 1 | `0x31a000` | `0x01000000` | `0x87e00000` | 830592 | 11603968 | `0x08000007` | 830592 | MATCH |
| 9 | 1 | `0x3e5000` | `0x01b11000` | `0x88911000` | 2800 | 4096 | `0x08000006` | 2800 | MATCH |
| 10 | 1 | `0x3e6000` | `0xc0600000` | `0x88912000` | 0 | 974848 | `0x08000004` | — | ABSENT-as-predicted |
| 11 | 1 | `0x3e6000` | `0x74000000` | `0x88a00000` | 59156 | 274432 | `0x08000007` | 59156 | MATCH |
| 12 | 1 | `0x3f5000` | `0xc06ee000` | `0x88a43000` | 0 | 1822720 | `0x08000004` | — | ABSENT-as-predicted |

- `[F]` **10 of 13** segments have `p_filesz > 0`; **10/10** have a sibling file whose
  size equals `p_filesz` exactly. The three `p_filesz == 0` segments (indices 7, 10, 12)
  have **no** sibling file (0 of 3), and that absence is the correct behaviour: a
  zero-byte payload does not get a `.bNN` file at all.
- `[F]` So the rule "segment `i` has a sibling `image_cdsp.bNN` iff `p_filesz > 0`, and
  that sibling's size equals `p_filesz`" holds **13/13** on this image (10 matches +
  3 correctly-absent), and **12/12** on the SDM845 second image (§7).
- `[F]` **Prior art (audit round).** This rule is not new — it is what the public loader
  already implements. `drivers/soc/qcom/mdt_loader.c` (GPL-2.0-only) rejects a sibling
  whose size differs (`if (seg_fw->size != phdr->p_filesz)`), and
  `qcom_mdt_bins_are_split()` skips rows with `!p_filesz`, which is exactly the
  "zero-`filesz` rows get no file" half of the rule. What this note adds is the
  **measured confirmation across two independent images and two DSP generations**, plus
  the `p_flags` decode, not the rule itself.
- `[N]` **Case matters on real payloads.** The enchilada image is uppercase
  (`CDSP.MDT` + `CDSP.B00`) because it comes from an 8.3 FAT volume, while the loader
  builds lowercase names. A case-sensitive join therefore reports a valid image as
  nine missing siblings. The probe resolves case-insensitively for that reason; a
  case-sensitive `find -name '*.mdt'` over the data root also under-counts
  (50 files / 12 Hexagon with `-name`, 82 / 16 with `-iname`).
- `[F]` `b00` (468 B) is byte-identical to `mdt[0:468]`, and `b01` (7192 B) is
  byte-identical to `mdt[468:7660]`; `b00 ++ b01` reconstructs the whole `.mdt`
  (7660 B) exactly. This is why `.mdt` is small: it is the header plus the hash
  segment, and every payload lives in a `.bNN`.
- `[F]` Segment 0 (`PT_NULL`, 468 B) is exactly `e_ehsize + e_phnum * e_phentsize`
  = `52 + 13*32` = 468. It is the ELF header plus the program-header table, given a
  `PT_NULL` header so that the loader's segment-0 read covers it.
- `[F]` Segment 1 (`PT_NULL`, 7192 B) is at file offset `0x1000` — page-aligned, with
  the 468-byte header block occupying only the first page. `[I]` The `0x1000` gap
  between the header block and segment 1 is padding to a page boundary, matching the
  `p_offset % 0x1000 == 0` alignment of every subsequent segment offset
  (`0x3000`, `0x3d000`, `0x57000`, `0x58000`, `0x305000`, `0x31a000`, `0x3e5000`,
  `0x3e6000`, `0x3f5000` — all page-multiples).
- `[F]` `p_memsz` exceeds `p_filesz` on every loadable segment that has content, and is
  non-zero where `p_filesz` is zero — i.e. `.bss`-style tail expansion is expressed in
  the header only. Sum of `p_memsz` over all 13 rows = **20,979,712**; sum of
  `p_filesz` = **4,129,418**; the `.mdt` itself is 7660.
- `[N]` The `.mdt` is **not** a superset of the `.bNN` files and cannot be used to
  reconstruct them; only `b00` and `b01` are recoverable from it.

## 3. `p_flags` decoding

- `[F]` Decode follows the public GPL-2.0-only layout in coreboot
  `util/qualcomm/mbn_tools.py` (bits 20–27):

```
31 30 29 28 | 27 pool/relocatable | 26-24 segment type | 23-21 access | 20 page | 2-0 R/W/X
```

  with segment types 0=L4/AMSS, 1=AMSS, 2=HASH, 3=BOOT, 4=L4BSP, 5=SWAPPED/XBL_SEC,
  6=SWAP_POOL, 7=PHDR; access types 0=RW, 1=RO, 2=ZI, 3=NOTUSED, 4=SHARED, 7=RWE.

- `[F]` The same bit assignments appear independently in torvalds/linux
  `include/linux/soc/qcom/mdt_loader.h` as `QCOM_MDT_TYPE_MASK`/`QCOM_MDT_TYPE_HASH`
  and `QCOM_MDT_RELOCATABLE`. Two independent public sources agreeing on the bit
  positions is what makes the *layout* `[F]` rather than `[I]`.

Decoded, per segment:

| i | p_flags | R/W/X | segtype | access | bit27 | bits 31–28 |
|---|---|---|---|---|---|---|
| 0 | `0x07000000` | — | 7 PHDR | 0 RW | 0 | 0 |
| 1 | `0x02200000` | — | 2 HASH | 1 RO | 0 | 0 |
| 2 | `0x08000005` | R-X | 0 L4/AMSS | 0 RW | 1 | 0 |
| 3 | `0x08000005` | R-X | 0 L4/AMSS | 0 RW | 1 | 0 |
| 4 | `0x08000005` | R-X | 0 L4/AMSS | 0 RW | 1 | 0 |
| 5 | `0x08000007` | RWX | 0 L4/AMSS | 0 RW | 1 | 0 |
| 6 | `0x08000006` | RW- | 0 L4/AMSS | 0 RW | 1 | 0 |
| 7 | `0x08000004` | R-- | 0 L4/AMSS | 0 RW | 1 | 0 |
| 8 | `0x08000007` | RWX | 0 L4/AMSS | 0 RW | 1 | 0 |
| 9 | `0x08000006` | RW- | 0 L4/AMSS | 0 RW | 1 | 0 |
| 10 | `0x08000004` | R-- | 0 L4/AMSS | 0 RW | 1 | 0 |
| 11 | `0x08000007` | RWX | 0 L4/AMSS | 0 RW | 1 | 0 |
| 12 | `0x08000004` | R-- | 0 L4/AMSS | 0 RW | 1 | 0 |

- `[F]` **Two independent role agreements**, which is the real evidence that the decode
  is right rather than merely self-consistent:
  - `phdr[0].p_flags = 0x07000000` decodes to segment-type **7 = PHDR**, and segment 0
    *is* the ELF header + program-header table (§2).
  - `phdr[1].p_flags = 0x02200000` decodes to segment-type **2 = HASH**, and segment 1
    *is* the hash/certificate segment (§8 shows DER certs inside it).
- `[F]` Bit 27 (`QCOM_MDT_RELOCATABLE`) is set on **all 11** `PT_LOAD` rows and on none
  of the two `PT_NULL` rows. That matches the loader's "this image is relocatable, load
  by `p_paddr`" path.
- `[F]` Bits 31–28 are zero on all 13 rows; there are no unknown high bits in this image.
- `[N]` **Read the `access` column with care on the zero-fill rows (framing, audit
  round).** Rows 7, 10 and 12 print `access = 0 (RW)` because that is literally what
  bits 23–21 hold — but a segment with `p_filesz == 0` reserves memory and loads nothing,
  so describing its *access* as RW is a category error a reader can trip over. Those
  rows are **BSS**: their defining property is `p_filesz == 0 && p_memsz > 0`, and their
  `p_flags` access field is not telling you anything useful. The separate R/W/X columns
  are also derived from bits 2–0 and read `R--` on these rows, which is equally
  non-informative. The one solid conclusion from the flags on these rows is the
  segment-type and bit-27 fields.
- `[N]` **The zero-fill segments are not tagged `ZI`.** `p_flags = 0x08000004` has access
  bits `0b000` = RW, not `0b010` = ZI. So for this image the tempting shortcut
  "`access == ZI` ⟺ `p_filesz == 0`" is **false**: the `p_filesz == 0` set is
  `{7, 10, 12}` while the ZI-tagged set is `{}`. Zero-fill here is expressed purely by
  `p_filesz == 0 && p_memsz > 0`, not by the access field. Anyone who "confirms" ZI from
  the access bits will get this image wrong.
- `[F]` Corpus census over **1692** ELF32 files under the data root, **11426** total
  `p_flags` words, **28** distinct values. **Scope caveat (audit round):** this corpus is
  dominated by userspace `.so` files, so its percentages are not firmware statistics.
  An independent re-measurement restricted to ELF32 files reached by the probe found
  7869 of 8486 words coming from `.so` and 617 from firmware; the qualititative result
  is unchanged either way — **access value 2 (ZI) never appears in either subset**, so
  the ZI-negative is not an artifact of the userspace majority.
  - distinct low-3 (R/W/X) values `[0, 4, 5, 6, 7]` — all inside `0..7`, i.e. nobody
    ever writes garbage into the standard PF_R/W/X bits;
  - segment-type values observed `[0, 1, 2, 3, 4, 5, 7]` — seven of the eight defined
    values, missing only 6;
  - access values observed `[0, 1, 3]` — RW, RO, NOTUSED; **2 (ZI) never appears**,
    in the whole corpus *and* in the firmware-only subset;
  - bit 27 set on **724 of 11426** words;
  - `0x07000000` appears 753 times, exactly matching `0x02200000`'s 753 — the
    PHDR/HASH pair is systematic across the whole corpus, not a quirk of this file.
- `[I]` The per-segment *semantic intent* (why segment 5 is RWX while segment 6 is RW)
  is not decodable from the bits; that is a linker-policy choice and is only `[I]`.

## 4. ISA evidence — is this really Hexagon code?

- `[F]` `e_machine = 164` = `EM_HEXAGON`/`EM_QDSP6` (`include/uapi/linux/elf-em.h`).
- `[F]` `e_flags` on this SM8250 image is `0x00000066`; the low 12 bits `0x066` are
  Hexagon ISA **V66**, high bits zero. The SDM845 second image (§7) carries
  `0x00000065` = **V65** at the same field, so the nibble tracks the DSP generation
  rather than being a constant.
- `[F]` `e_flags` `0x00000003` = `EF_HEXAGON_MACH_V4` also occurs in the corpus
  (zap/ipa firmware), so the field is doing real work across generations. The V4
  mapping is cited rather than asserted: `llvm/include/llvm/BinaryFormat/ELF.h`
  (Apache-2.0-with-LLVM-exception) defines `EF_HEXAGON_MACH_V4 = 0x00000003`
  alongside `EF_HEXAGON_ISA_V66 = 0x00000066`, and QEMU's
  `linux-user/hexagon/elfload.c` (GPL-2.0-or-later) maps the same nibbles in
  `get_elf_cpu_model()` (it lists `0x04` = v5 upward but omits `0x03`, so V4 is
  sourced from LLVM, not QEMU).
- `[F]` Those two header fields are the *only* hard ISA facts in the file. Everything
  below is statistical.

Parse-bit model `[F]` as a rule, from LLVM `HexagonBaseInfo.h`
(Apache-2.0-with-LLVM-exception), `INST_PARSE_*`:

- parse bits are **bits [15:14]** of each little-endian 32-bit word — *not* the low two
  bits;
- `00` + iClass 0 → constant extender or duplex word (not a packet end);
- `00` + iClass ≠ 0 → duplex packet, both halves end together;
- `01` → more instructions follow in this packet;
- `10` → end of inner loop;
- `11` → end of packet;
- a packet is 1–4 words. A 5th instruction word in one packet is architecturally
  impossible, so the >4-word rate is a validity probe.

Controls, both measured on this machine:

- `[F]` Positive control — real Hexagon code, `libnn_preproc.so` `.text` (offset 10176,
  16380 B, sha256 `ae92a786fa3ef84c34df61b165aa796ad44c5ef1adc7db395359d9cee0ecd66a`),
  at byte offset +0: `p00=0.092 p01=0.509 p10=0.004 p11=0.395`, gap>4-word **6.242%**.
- `[F]` Negative control — 300000 bytes of uniform random data: `p00..p11 ≈ 0.25` each at
  every byte offset, gap>4-word **6.18–6.39%** at every offset.
- `[F]` Key consequence: the gap>4-word rate of random data (≈6.2%) is *the same* as
  the positive control's (6.242%). **The gap rate alone does not discriminate.** What
  discriminates is the parse-bit marginal distribution and the `p10` (loop-end) rate.

Per-segment measurement:

| i | bytes | p00 | p01 | p10 | p11 | gap>4% | iClass H | aligned |
|---|---|---|---|---|---|---|---|---|
| 0 | 468 | 0.726 | 0.103 | 0.120 | 0.051 | 45.000 | 1.067 | yes |
| 1 | 7192 | 0.274 | 0.137 | 0.095 | 0.494 | 3.777 | 3.047 | yes |
| 2 | 235420 | 0.491 | 0.247 | 0.016 | 0.246 | 3.831 | 2.760 | yes |
| 3 | 105980 | 0.972 | 0.028 | 0.000 | 0.000 | 75.000 | 0.193 | no (+2) |
| 4 | 1076 | 0.000 | 0.390 | 0.000 | 0.610 | 0.000 | 2.468 | yes |
| 5 | 2803308 | 0.108 | 0.319 | 0.007 | 0.566 | 2.682 | 3.090 | yes |
| 6 | 83426 | 0.238 | 0.761 | 0.001 | 0.001 | 18.182 | 2.443 | no (+1) |
| 8 | 830592 | 0.230 | 0.408 | 0.020 | 0.341 | 6.198 | 3.683 | yes |
| 9 | 2800 | 0.513 | 0.156 | 0.139 | 0.193 | 12.931 | 3.165 | no (+1) |
| 11 | 59156 | 0.171 | 0.439 | 0.011 | 0.380 | 5.664 | 3.542 | yes |

- `[I]` Segments 5, 8 and 11 match the known-code reference on the two features that
  actually discriminate: `p10` (loop-end) is *rare* — 0.007, 0.020, 0.011 vs the
  reference's 0.004 and random's 0.25 — and `p00` (extender/duplex) is *not* 0.25.
  Segments 2 and 3 fail that test (`p10 = 0.016` is fine but `p00 = 0.491`/`0.972` and
  the gap rates of 3.8%/75% are not code-like). This is `[I]`, not `[F]`: packet
  statistics on obfuscated or compressed code could imitate these marginals.
- `[I]` The >4-word residue for segment 5 is **2.682%**, i.e. 10772 architecturally
  impossible packets out of 401689. That is non-zero. Real code should be ~0%. The
  plausible explanations are data interleaved inside a loadable segment (literal pools,
  jump tables, unaligned padding) rather than misalignment — supported by the alignment
  sweep below, which shows byte offset +0 is the *minimum* of the four offsets.
- `[F]` Byte-alignment sweep on segment 5, gap>4-word rate: `+0 → 2.682%`,
  `+1 → 5.868%`, `+2 → 5.490%`, `+3 → 6.630%`. The true alignment is the minimum, and
  the others sit at the random-data baseline (≈6.2%). This is a *reported non-result*
  for the >4-word rate as a code detector, but it does correctly identify alignment.
- `[N]` **The alignment sweep is not evidence of "Hexagon code" by itself.** It only
  shows the segment is word-structured with offset 0 correct. Uniform random data would
  show no minimum at all, but plenty of non-code binary formats are 4-byte structured.
  I initially expected this sweep to discriminate code from data and it does not.

Packet-length distribution, segment 5 (parse bits `[15:14]`, gap model):

```
1 word   304995  75.928%
2 words   42583  10.601%
3 words   26420   6.577%
4 words   16919   4.212%
5 words    4350   1.083%
6 words    2821   0.702%
7 words    1547   0.385%
8 words     519   0.129%
>4 words  10772   2.682%
residue after last packet end: 0 words
```

- `[I]` **The packet-length distribution is an inference, not proof.** A 1-word-packet
  mode at 75.9% with a monotonically decaying tail is the shape compiled Hexagon takes
  (mostly short packets, occasional long ones), and 2.682% >4-word residue is low enough
  to be data-in-text rather than garbage. But this is a shape argument. It does not
  prove these bytes execute, and I am not claiming it does.
- `[F]` Extender/duplex consistency, segment 5: 28875 words have `parse=00, iClass=0`
  (extender candidates) of which **20466 are packet-leading** — illegal for a constant
  extender, which must follow an instruction. 46595 words have `parse=00, iClass≠0`
  (duplex), of which 78 have iClass outside 0..14. `[I]` The 20466 "illegal" extenders
  are consistent with extender-shaped words that are really data; the number is large
  enough that it is the main reason I keep the code claim at `[I]`.
- `[F]` iClass histogram for segment 5 covers **all 16** opcode classes, entropy 3.090
  bits: `0x0 EXTENDER 64153`, `0x1 J_1 17901`, `0x2 J_2 26578`, `0x3 LD_ST_1 18232`,
  `0x4 LD_ST_2 20309`, `0x5 J_3 68671`, `0x6 CR 29066`, `0x7 ALU32_1 77785`,
  `0x8 XTYPE_1 9589`, `0x9 LD 31314`, `0xa ST 20063`, `0xb ALU32_2 13741`,
  `0xc XTYPE_2 16089`, `0xd XTYPE_3 3668`, `0xe XTYPE_4 7040`, `0xf ALU32_3 276628`.
  `[I]` All 16 classes present with ALU32_3 dominant is what a general-purpose compiled
  image looks like; random data would give a flat 6.25% per class. But a compressed blob
  would also look non-flat, so this narrows rather than settles.
- `[N]` No disassembly was performed. No instruction was decoded to a mnemonic. The ISA
  claim rests on `e_machine`/`e_flags` `[F]` plus packet statistics `[I]`.

## 5. Segment role classification

Classifier rule: a segment is called `code-like` only if (a) it is ≥2048 words, so the
parse-bit estimate is stable, (b) `p10` is below **0.05**, and (c) `p00` is
materially below 0.25. Segments under 2048 words are reported as **too small for
packet statistics** rather than guessed at.

**Falsifiability limit `[N]` (audit round, 2026-11-20).** This classifier is
**one-sided**: it can reject a segment, but it cannot certify one. The audit
replicated the rule against non-code inputs and found a constant `0xFF` run, a plain
u32 index table, packed PCM, ASCII text and base64 all **pass** it, because each has
either no parse-bit `10` words or an unremarkable `p00`. Compressed data, by contrast,
*fails* it — the earlier draft named the wrong adversary. So `code-like` here means
"consistent with a compiled Hexagon stream and inconsistent with compression", not
"is executable code". Only a disassembly could settle that, and none was done. The
`[I]` tag on those three rows carries this weight and should be read that way.

| i | role | bytes | H | zero% | ascii% | gap>4% | why |
|---|---|---|---|---|---|---|---|
| 0 | header/phdr-table | 468 | 3.15 | 59.2 | 8.8 | 45.000 | `PT_NULL`; `p_filesz == e_ehsize + e_phnum*e_phentsize`; type-bits 7 |
| 1 | hash/cert-segment | 7192 | 5.28 | 5.0 | 22.0 | 3.777 | type-bits 2 = HASH; DER certs inside (§8) |
| 2 | data (parse bits inconsistent with code) | 235420 | 4.50 | 50.2 | 19.3 | 3.831 | `p10=0.016`, `p00=0.491` — not a compiled stream |
| 3 | data (sparse / zero-heavy) | 105980 | 0.20 | 97.1 | 0.1 | 75.000 | entropy 0.205 bits/byte |
| 4 | data (too small) | 1076 | 4.51 | 29.5 | 29.4 | 0.000 | 269 words; below 2048-word threshold |
| 5 | code-like | 2803308 | 5.18 | 7.5 | 28.5 | 2.682 | `p10=0.0075`, `p00=0.108`, iClass H 3.09 |
| 6 | data (string/table blob) | 83426 | 5.10 | 8.2 | 91.5 | 18.182 | 91.5% of bytes in printable runs ≥8 |
| 7 | BSS (zero-fill) | 0 | 0.00 | — | — | — | `p_filesz==0`, `p_memsz=155648`, no sibling |
| 8 | code-like | 830592 | 6.76 | 16.7 | 33.8 | 6.198 | `p10=0.0204`, `p00=0.230`, iClass H 3.68 |
| 9 | data (too small) | 2800 | 5.93 | 32.4 | 26.4 | 12.931 | 700 words; below 2048-word threshold |
| 10 | BSS (zero-fill) | 0 | 0.00 | — | — | — | `p_filesz==0`, `p_memsz=974848`, no sibling |
| 11 | code-like | 59156 | 6.49 | 17.5 | 35.5 | 5.664 | `p10=0.0108`, `p00=0.171`, iClass H 3.54 |
| 12 | BSS (zero-fill) | 0 | 0.00 | — | — | — | `p_filesz==0`, `p_memsz=1822720`, no sibling |

- `[F]` 3 segments classified `code-like` (5, 8, 11); 3 BSS; 1 header; 1 hash; 5 data.
- `[F]` Segment 8's gap>4 rate (6.198%) sits *at* the random baseline while its `p10`
  (0.020) is code-like. `[I]` This is the weakest of the three code calls: it is
  probably code with substantial embedded data, but it could be a different structured
  payload. I am not upgrading it to `[F]`.
- `[H]` Segment 6 (91.5% printable runs, 18.2% >4-word gaps) is a string/table region —
  the printable fraction is strong, but "what table" is a guess.
- `[N]` Segments 4 and 9 are **not** classified. At 269 and 700 words the parse-bit
  marginals are within noise of random; calling either "code" or "data" would be
  overreach. They are left as "too small for packet statistics".

## 6. Cross-check against `image_cdspr.jsn`

- `[F]` `second-device/instantnoodle/modem-fat-lfn/image_cdspr.jsn` is **403 bytes**,
  sha256 `15e148599165b38f68e62302d63c87caa5f0b164deb81aa419bbb4ecf920bc4b`,
  md5 `f2bd80d5f0b19b5b0d36d28383948149`.
- `[F]` Parsed content: `sr_version = 1.1.1`; `sr_domain = {soc: "msm", domain: "cdsp",
  subdomain: "root_pd", qmi_instance_id: 76}`; `sr_service = [{provider: "tms",
  service: "servreg", service_data_valid: 0, service_data: 0}]`.
- `[F]` It contains **no** MDT key, no program-header data, no segment table, no sibling
  filename, no hash of `cdsp.mdt`. Zero overlap with the container structure in §2.
- `[F]` This is not a local guess: `research/laptop/qualcomm-pil-manifest-family.md`
  establishes the whole `*.jsn` family as **PDR service-registry manifests**, a lookup
  table mapping a QMI provider/service to a protection domain — explicitly *not*
  split-MDT image manifests. That doc's table lists `f2bd80d5…` as `cdspr.jsn`, 403 B,
  domain `msm/cdsp/root_pd` (instance 76) — the same three identifiers measured here.
- `[F]` `research/cdsp-fleet/census.md` shows `cdspr.jsn` is a **2-value** file
  fleet-wide: 60 instances collapsing to md5s `49003ffc…` (513 B, 30 devices) and
  `f2bd80d5f0b19b5b0d36d28383948149` (403 B, 30 devices). Our md5 is the 403-byte
  variant, i.e. the common one.
- `[N]` So `cdspr.jsn` **cannot** be used to validate the phdr table, the sibling
  sizes, or the segment count. The only thing it corroborates is that this `.mdt`'s
  protection domain is `msm/cdsp/root_pd` with QMI instance 76 — a naming fact, not a
  structural one.
- `[I]` The 403 vs 513 byte split is cosmetic: per the laptop note the delta is exactly
  one optional `dcomment` string field (110 B), and after dropping `dcomment` the two
  JSON documents are **equal**. So the two fleet variants describe the same domain.

## 7. Second device — SDM845 cross-check

**Correction (2026-11-20, audit round).** An earlier draft of this section claimed no
second device's cdsp image existed. That was wrong, and the error is instructive: the
first search used `find . -name '*.mdt'` and `cdsp`, both case-sensitive, while the
enchilada payload sits inside `modem.img` behind **8.3 uppercase FAT names**
(`CDSP.MDT`, `CDSP.B00`, …). The census CSV itself records the ten rows
(`device=OnePlus_6`, `source=LineageOS-22.2-20261111-nightly-enchilada modem.img FAT
IMAGE dir`) — the evidence was in the sibling document's own input.

- `[F]` A **second, independent cdsp split image exists**: OnePlus 6 (`enchilada`,
  SDM845), extracted from a FAT16 volume inside `enchilada/modem.img`. 11 files:
  `CDSP.MDT` 7260 B plus `B00` 436, `B01` 6824, `B02` 197840, `B03` 104160, `B04` 980,
  `B05` 2402948, `B06` 31596, `B08` 69800, `B10` 58900, and `CDSPR.JSN` 403.
- `[F]` All 11 md5s equal the `md5_db=` values recorded for `OnePlus_6` in
  `data/fleet/devices-001-222.csv`, md5-for-md5, so the extraction is verified against
  the census rather than assumed.
- `[F]` **The sibling rule generalises: 12/12 on this image** (9 exact matches + 3
  correctly-absent), with the zero-`p_filesz` rows again being exactly `7, 9, 11`.
  Every present sibling's size equals its `p_filesz`, 9/9.
- `[F]` The two images differ in generation, and the headers say so:
  `e_flags` is **`0x00000066` (V66) on SM8250** and **`0x00000065` (V65) on SDM845**.
  Same `e_machine` 164, same `PT_NULL`/`PT_LOAD` shape, 13 vs 12 program headers.
- `[F]` The `.mdt`-holds-only-header-plus-hash rule holds on both: `b00 ++ b01`
  reconstructs the whole `.mdt` (7660 B on SM8250, 7260 B on SDM845).
- `[F]` Running the same probe on the second image gives
  `cdsp.mdt bytes=7260 phdr=12 nonzero_filesz=9 sibling_exact=9/9 zero_filesz_idx=7,9,11
  zero_filesz_sibling=0 b00_plus_b01=True relocatable=True isa_nibble=0x065
  largest_seg=5 code_like=3` — the same shape as SM8250 with one fewer payload segment.
  `e_flags` is `0x00000065` (V65) against SM8250's `0x00000066` (V66).
- `[F]` The certificate structure repeats on the second device's hash segment: 13 DER
  `SEQUENCE (0x30 0x82)` candidates with a contiguous chain of three at offsets
  680 / 1963 / 3100 (lengths 1283 / 1137 / 1153), and 212 32-byte records after a 24-byte
  prefix. So the hash/cert layout is a format property, not a one-off.
- `[F]` `CDSPR.JSN` on enchilada is the **403-byte** `cdspr.jsn` variant, md5
  `f2bd80d5f0b19b5b0d36d28383948149` — the same md5 the census records for 30 devices
  (see `census.md` §C). So the 30-device `cdspr.jsn` cluster is now anchored by a
  locally verified byte-exact copy.
- `[N]` `cdsp_dtb.*` still has no on-disk instance in this dump, so the `cdsp_dtb`
  sibling-series claim in `census.md` remains unverified by bytes.

The extraction command is `python3 -I analysis/fat_extract.py data-fetch/enchilada/modem.img <outdir>`;
no payload byte is committed. The audit record is `audit.md`.

- `[F]` What *was* possible instead: a corpus generalisation over the **12**
  `EM_HEXAGON` split-MDT images present, spanning 3 devices (`instantnoodle`, `larry`,
  `enchilada`) and 7 subsystem names (cdsp, slpi, npu, adsp, ipa_fws, ipa_uc, zap):

| path | loadable segs | e_flags |
|---|---|---|
| `second-device/instantnoodle/modem-fat-lfn/image_cdsp.mdt` | 8 | `0x066` |
| `second-device/instantnoodle/modem-fat-lfn/image_slpi.mdt` | 20 | `0x066` |
| `second-device/instantnoodle/modem-fat-lfn/image_npu.mdt` | 5 | `0x066` |
| `second-device/instantnoodle/modem-fat-lfn/image_adsp.mdt` | 17 | `0x066` |
| `second-device/instantnoodle/tree-vendor/firmware/ipa_fws.mdt` | 3 | `0x003` |
| `second-device/instantnoodle/tree-vendor/firmware/ipa_uc.mdt` | 1 | `0x003` |
| `second-device/instantnoodle/tree-vendor/firmware/a650_zap.mdt` | 1 | `0x003` |
| `second-device/larry/tree-vendor/firmware/a660_zap.mdt` | 1 | `0x003` |
| `second-device/larry/tree-vendor/firmware/a615_zap.mdt` | 1 | `0x003` |
| `second-device/larry/tree-vendor/firmware/ipa_fws.mdt` | 3 | `0x003` |
| `enchilada/tree_firmware/ipa_fws.mdt` | 3 | `0x003` |
| `enchilada/tree_firmware/a630_zap.mdt` | 1 | `0x003` |

- `[F]` The §2 rules hold **12/12**: every `p_filesz > 0` segment has an exact-size
  sibling, `mdt == b00 ++ b01` in all 12, and every image has
  `QCOM_MDT_RELOCATABLE` (bit 27) on at least one loadable segment.
- `[F]` `e_flags` splits cleanly into two ISA generations across the corpus:
  `0x00000066` for the four `instantnoodle` DSP images (cdsp/slpi/npu/adsp) and
  `0x00000003` for all zap/ipa firmware. So the container format is stable across ISA
  generations even though the payload ISA is not.
- `[N]` **Corpus scope (corrected).** The 12 images in the table above are one device's
  four DSP subsystems plus zap/ipa firmware from three devices — a cross-*subsystem*
  generalisation, not a cross-SoC cdsp one. The second **cdsp** image (§7, SDM845 V65)
  is the one that supplies the cross-SoC test, and it passes; the table itself was never
  the cross-SoC evidence. Adding `enchilada` `CDSP.MDT` to this corpus makes it **13**,
  which is why the probe's `corpus=12/12` line counts the table as written and the
  second-image run reports separately.
- `[F]` Divergences the corpus scan did find, which are real and worth recording:
  `larry` `evass.mdt` and `vpu20_1v.mdt` **do** ship zero-byte `.bNN` files for their
  `p_filesz == 0` segments (`evass.b11`–`b18` are all 0 bytes), unlike cdsp which omits
  them entirely; and `vpu20_1v.mdt` has **no `b00` at all** despite
  `phdr[0].p_filesz=692`. `[F]` Both are `e_machine = 94` (`EM_XTENSA`, not
  `EM_ARM` — the `vpu20`/`evass` firmware is Tensilica), which is exactly why they fall
  outside the 12-image corpus: the container format is shared with Xtensa firmware,
  the ISA is not.
- `[F]` Consequently "no sibling for a zero-fill segment" is a cdsp/instantnoodle
  behaviour, not a universal one, and the missing-`b00` case breaks the "iff" direction
  of the rule. This is the main reason the §2 rule is stated as an observation about
  this image and the 12-image corpus, not as a law.

## 8. Entropy and layout facts

- `[F]` `p_filesz` totals: sum over all 13 rows = **4,129,418**; `.mdt` on disk = 7660
  (0.19% of the payload). Largest segment `phdr[5]` = **2,803,308** B (2.673 MiB),
  67.9% of all payload bytes. Smallest non-zero segment `phdr[0]` = 468 B.
- `[F]` Segment 5 alone accounts for 401,689 packets and 46595 duplex words; its
  iClass entropy is 3.090 bits (vs 4.0 maximum for 16 classes).
- `[F]` Per-segment byte entropy spans the full range: 0.205 (segment 3, 97.1% zero
  bytes) to 6.76 (segment 8). A single-image entropy figure would be meaningless —
  the file is deliberately heterogeneous.
- `[F]` Segment 1 (the hash segment) carries a recognisable certificate structure:
  prefix 24 B `0c000000060000000000000000000000701b000070020000` (u32 LE
  `0xc, 0x6, 0, 0, 0x1b70, 0x270`), then **224** 32-byte records (128 distinct, 6
  all-zero), then **12** DER `SEQUENCE (0x30 0x82)` candidates, of which a contiguous
  chain of three at offsets **1048 / 2085 / 3180** with lengths **1037 / 1095 / 1089**.
  First certificate starts `30820409308202c1a003020102020101`. A sample of the
  hash-record region at `24 + 32*8` is `5c702af1ec8d77773becc99ef659b0ab`.
  `[I]` The 224 records / 128 distinct pattern is consistent with per-segment hashes
  plus padding, but the record semantics are not established here.
- `[F]` Segment offsets are all page-aligned in the image's payload address space, and
  `p_offset` values increase monotonically except for two deliberate equal pairs
  (`0x31a000` shared by segments 7 and 8, `0x3e6000` shared by segments 10 and 11) —
  a zero-fill segment and the next segment share an offset because the zero-fill one
  occupies no file space.
- `[F]` Three segments (7, 10, 12) reserve **2,951,216** bytes of memory with zero file
  bytes — 14.1% of total `p_memsz` is BSS.

## Summary

```
SUMMARY cdsp.mdt bytes=7660 phdr=13 nonzero_filesz=10 sibling_exact=10/10 zero_filesz_idx=7,10,12 zero_filesz_sibling=0 b00_plus_b01=True relocatable=True isa_nibble=0x066 largest_seg=5 over4=2.682% align0=2.682% align1=5.868% code_like=3 corpus=12/12
```

## What this note does not establish

- `[N]` It does not prove any byte in segments 5/8/11 is executable Hexagon
  instruction — no disassembly was done, and the code call is `[I]`.
- `[N]` It does not explain the 2.682% >4-word residue or the 20466 packet-leading
  extender candidates.
- `[N]` It does not identify the 224 hash records' semantics, or the format of any of the
  ten segments not classified `code-like`.
- `[N]` It does not compare cdsp across SoCs — no second cdsp image exists on disk.
- `[N]` It does not show that the loader honours `p_paddr` over `p_vaddr`; that is
  `[I]` from `mdt_loader.c` reading, not from this file.
