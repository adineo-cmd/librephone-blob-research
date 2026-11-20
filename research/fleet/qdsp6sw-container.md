# `qdsp6sw.mbn` — Qualcomm modem DSP container, metadata segment and CLADE contract (SM8250 / SDX55M)

**Issue:** #606 · **Analysis date:** 2026-11-20 · **Evidence classes:** `[F]` measured fact
(command and output shown) · `[I]` inference from stated facts · `[N]` honest negative ·
`[U]` unresolved.

**Artifact.** `image_sdx55m_qdsp6sw.mbn`, 84,123,868 B, sha256
`1cfd9082c3a820d5f24eaf52760d08d888fc01c60d4a2fdde96b1f527207bd92`, extracted from the
OnePlus 8 (`instantnoodle`, SM8250) LineageOS 24.0-20261117 nightly `modem.img`, FAT16
volume `modem-fat-lfn/` (654 files, 176,550,702 B). Read-only throughout; no payload byte
is reproduced here beyond short hex prefixes.

**Companion tool.** `implementations/hexagon-qdsp6/` — clean-room parser, 47 tests.

---

## 0. Headline

This image is the modem DSP firmware of an SDX55M, built 2022-02-01, running **Hexagon V67**.
It is a standard ELF32 `ET_EXEC` with **29 program headers and no section headers at all**, so
every name in it survives only as a string, never as a section-header entry.

Three findings, ordered by how well they survive prior art:

1. **`[F]` The QuRT linker/memory-map XML is embedded verbatim in the image** and is the
   vendor's machine-readable statement of the CLADE compressed-region contract. It is
   invisible to a `<?xml` scan because it carries no declaration. **This is the contribution
   that no public source covers** (§4).
2. **`[F]` The metadata segment (program header 1) is the same hash-segment format already
   decoded in this repo** at `research/fleet/pil-metadata-sweep.md`, with one measurable
   difference: this image signs with **ECDSA P-384**, not RSA-2048 (§3). The repo's existing
   "constant 6400" is refined to `w[4]-w[5] = w[9]+w[7]` (§3.4).
3. **`[I]` A per-segment classification of all 29 headers**, using the vocabulary
   rizin/radare2 already define but never actually assign (§5).

**What is explicitly *not* claimed.** The private `p_flags` bit `0x08000000` is **not** a
discovery: it is `BIT(27)` = `QCOM_MDT_RELOCATABLE`, public in mainline Linux since v4.11
(2017) and reimplemented in radare2/rizin. See §2.1 and §7.

---

## 1. Outer container `[F]`

```
$ sha256sum image_sdx55m_qdsp6sw.mbn
1cfd9082c3a820d5f24eaf52760d08d888fc01c60d4a2fdde96b1f527207bd92
$ stat -c '%s' image_sdx55m_qdsp6sw.mbn
84123868
```

| field | value |
|---|---|
| `e_type` | 2 (`ET_EXEC`) |
| `e_machine` | 164 (`EM_QDSP6`) |
| `e_entry` | `0x81600000` |
| `e_phoff` / `e_phentsize` / `e_phnum` | 52 / 32 / **29** |
| `e_shoff` / `e_shnum` / `e_shstrndx` | **0 / 0 / 0** — no section headers |
| `e_flags` | `0x67` → `EF_HEXAGON_ISA_V67` |

`[F]` The arch claim is not inferred from a filename. LLVM
`llvm/include/llvm/BinaryFormat/ELF.h` defines `EF_HEXAGON_ISA_V67 = 0x00000067` and
`EF_HEXAGON_MACH_V67 = EF_HEXAGON_ISA_V67`; bit 15 (`EF_HEXAGON_TINY_CORE`) is clear, so this
is full V67, not V67T. Independently corroborated inside the image: the machine string table
at offset 25,783,013 contains `MSS_QDSP6V67SS_PUB` and `MSS_VQ6_QDSP6V67SS_PUB` — and the two
distinct prefixes (`Q6`, `VQ6`) indicate **two DSP instances** in one image.

`[F]` File-space reconciliation is exact:

```
sum p_filesz        84,087,632
+ inter-segment pad     36,236   (20 gaps, all page-alignment)
= file size         84,123,868
```

`[F]` `p_offset` is non-decreasing and **no two `p_filesz` ranges overlap**. There is **no
trailing gap** — the file ends exactly at `0x0503A0DC`, the last byte of segment 27. Segment
28 declares `p_offset=0x0503B000`, which is **past EOF**; it has `p_filesz=0`, so the phantom
3,876-byte "gap" it implies is harmless. `[I]` the linker emitted a pure `.bss` region and
still advanced the file cursor.

`[F]` `e_entry = 0x81600000` equals the `p_paddr` of segment 2 — the entry segment. `p_vaddr =
p_paddr | 0x40000000` holds for **segments 2–26** and fails in three different ways elsewhere:
segment 0 is the all-zero header placeholder, segment 1 has `p_vaddr == p_paddr` (no alias at
all), and 27/28 use a different alias window (`0xA0920000`/`0xA0921000` against `p_paddr`
`0x8E6F0000`/`0x8E6F1000`). `[U]` why 27–28 use a different window.

---

## 2. The 29-entry program-header table

Full table in `implementations/hexagon-qdsp6` output; the structural facts:

`[F]` `p_type` is `PT_NULL` (0) for indices **0 and 1**, `PT_LOAD` (1) for **2–28**. Segment 0
is not merely "non-LOAD": it *is* the ELF header plus the program-header table, with
`p_filesz = 980 = e_ehsize + e_phnum × e_phentsize` exactly.

`[F]` Exactly three segments have `p_filesz = 0` — indices **15, 22, 28** — totalling
`4,096 + 46,280,704 + 16,838,656 = 63,123,456` bytes of zero-initialised memory with no file
backing.

`[F]` `sum p_memsz` = 233,836,764, i.e. **2.78×** `sum p_filesz`. The two low-fill segments
(19 at 0.26, 20 at 0.15) account for 86,593,916 bytes of declared-but-not-stored memory.

### 2.1 The `p_flags` bit — prior art, stated plainly

**This is not a discovery and must not be presented as one.** `[F]` mainline Linux has defined
these bits since **v4.11 (2017)**, in `include/linux/soc/qcom/mdt_loader.h`:

```c
#define QCOM_MDT_TYPE_MASK   (7 << 24)
#define QCOM_MDT_TYPE_HASH   (2 << 24)
#define QCOM_MDT_RELOCATABLE BIT(27)
```

Applied to this image (`[F]`, arithmetic check):

| idx | `p_flags` | `TYPE_MASK` field | `TYPE_HASH`? | `RELOCATABLE`? |
|---|---|---|---|---|
| 0 | `0x07000000` | `0x7` | no | no |
| 1 | `0x02200000` | `0x2` | **yes** | no |
| 2 | `0x08000005` | `0x0` | no | **yes** |

`[F]` All 27 `PT_LOAD` segments carry `BIT(27)`; the two `PT_NULL` segments do not. radare2
(`libr/bin/format/mdt/mdt.h`) and rizin (`librz/bin/format/mdt/mdt.h`) both ship a dedicated
MDT/MBN loader decoding exactly this field.

**`[F]` A correction that matters for any trust argument.** The kernel locates the metadata
segment by its **type field**, not by `p_type`:

```c
/* mdt_loader.c, qcom_mdt_read_metadata() */
for (i = 1; i < ehdr->e_phnum; i++) {
    if ((phdrs[i].p_flags & QCOM_MDT_TYPE_MASK) == QCOM_MDT_TYPE_HASH) {
        hash_segment = i; break;
    }
}
```

So segment 1 being `PT_NULL` does **not** mean it escapes validation — it is found and hashed
precisely because it is `PT_NULL` *and* carries the type field `0x2`. A verifier that walked
only `PT_LOAD` would skip it, but that is not what mainline does. The tool in this repo now
reports the segment this way (`hash segment 1`), not as a "non-loadable" block.

`[U]` The remaining high bits on segments 0 (`0x07000000`) and 1 (`0x02200000`) beyond the type
field are unnamed here; `0x07000000` is the header-table marker measured across the corpus, and
`0x02200000` encodes `TYPE_HASH` plus an unassigned `0x00200000`.

---

## 3. Segment 1 — the metadata / hash segment `[F]`

`p_offset=0x1000`, `p_vaddr=p_paddr=0x8F700000`, `p_filesz=7,808` (`0x1E80`), `p_memsz=8,192`.

### 3.1 Five regions tiled exactly by four size fields

| offset | size | size source | content |
|---|---|---|---|
| `0x0000` | 120 | header word `0x2c` = `0x78` | fixed header, 21 u32 |
| `0x0078` | 48 | constant | **all zero** — self-referential digest slot |
| `0x00A8` | 1,392 | word `0x14` = `0x570` = 29×48 | SHA-384 table, 29 entries |
| `0x0618` | 104 | word `0x1c` = `0x68` | DER ECDSA P-384 signature |
| `0x0680` | 6,144 | word `0x24` = `0x1800` | 3-cert X.509 chain, then `0xff` |

`[F]` Zero slack: `0x78 + 48 + 1392 + 104 + 6144 = 7808` = `p_filesz`. The last **4,180 bytes
are `0xff` fill** (`0x0E2C` → `0x1E80`), and the digest slot at `0x78` is 48 zero bytes.

### 3.2 The digest table is SHA-384 over raw `p_filesz`

`[F]` Entry *j* is `SHA-384` over exactly the `p_filesz` bytes of outer segment *j*, with **no
padding to `p_memsz`**:

```
candidates (p_filesz>0, excluding self)  25
matching                                 25
failed                                   []
```

So **25 of 25** verifiable entries reproduce byte-for-byte. Entry 1 is zeroed because it would
hash itself; entries 15/22/28 are zeroed because `p_filesz=0`.

`[F]` Negative controls, all clean: SHA-256, SHA-512, and SHA-384-over-`p_memsz`-zero-padded
variants each produce **zero** matches. A 32-byte stride finds no run; 40-byte records are not
integral (`7808/40 = 195.2`). This simultaneously fixes the record size (48), the algorithm
(SHA-384) and the hashed range (raw `p_filesz`, unpadded).

### 3.3 Signature and chain `[F]`

`[F]` The signature at `0x618` is DER `SEQUENCE { INTEGER(48), INTEGER(48) }` — two 48-byte
integers, i.e. **ECDSA P-384**, 102 bytes padded to the declared 104 with two `0x00`.

`[F]` The chain is three consecutive DER `SEQUENCE`s tiling `0x680..0x0E2C` (1,964 B). OID
counts across the chain:

```
ecPublicKey 1.2.840.10045.2.1            3
secp384r1   1.3.132.0.34                 3
ecdsa-with-SHA384 1.2.840.10045.4.3.3    6
rsaEncryption 1.2.840.113549.1.1.1       0
```

`[F]` Readable subjects: `QUALCOMM Attestation CA`, `QCT Root CA 1`, `SanDiego`,
`SecTools Test User`, `General Use Key`; validity stamps `240611142926Z`/`440606142926Z` and
`191030043301Z`/`391025043301Z`.

`[I]` `SecTools Test User` + `General Use Key` mark this as a **development/test** attestation
chain, not a production one. Trust in this image is therefore not established by this metadata
alone — consistent with the same test-chain finding in `research/fleet/pil-metadata-sweep.md`
(28 of 35 chains there are test-only).

### 3.4 The header is the repo's known format, with a different signature size

This is the part that connects to existing work rather than duplicating it. `[F]` Compare this
image against the AP-side images already swept in `research/fleet/pil-metadata-sweep.md`:

| image | phnum | `w[0]` | `w[1]` | `w[4]` | `w[5]` | `w[4]-w[5]` | `w[7]` | `w[9]` | `w[9]+w[7]` |
|---|---|---|---|---|---|---|---|---|---|
| abl | 3 | 0 | 6 | 6,544 | 144 | 6,400 | 256 | 6,144 | 6,400 |
| devcfg | 4 | 0 | 6 | 6,592 | 192 | 6,400 | 256 | 6,144 | 6,400 |
| hyp | 4 | 0 | 6 | 6,592 | 192 | 6,400 | 256 | 6,144 | 6,400 |
| xbl_config | 6 | 0 | 6 | 6,688 | 288 | 6,400 | 256 | 6,144 | 6,400 |
| **qdsp6sw** | **29** | **12** | **6** | **7,640** | **1,392** | **6,248** | **104** | **6,144** | **6,248** |

`[F]` Two consequences, both verified by arithmetic above:

1. **The repo's "constant 6400" is `w[9] + w[7]`, not a constant.** It is 6,400 on the AP
   images only because their signature is RSA-2048 (256 B). This image's ECDSA P-384 signature
   is 104 B, so the same sum is 6,248. The relation holds on every 1-chain image measured.
   `[I]` the 2-chain images (tz, qupfw) instead show 19,200 = 3 × 6,400, so the general form
   needs a per-chain term — left open rather than guessed.
2. **This image is a new row in that table, not a new format.** Header base is 168 (`0xa8`) as
   for SM8250 1-chain, `w[1]=6` as for SM8250, `w[5] = phnum × 48` as before. `w[0]=12` is a
   value not in the sweep's observed set `{0, 4, 5, 25}` — recorded as an extension.

`[F]` Header word meanings confirmed here: `0x14`=table size 1,392, `0x1c`=signature size 104,
`0x24`=cert region 6,144, `0x2c`=fixed header size 120, `0x10`=7,640 = size of everything after
header+digest slot.

`[U]` Words `0x18`/`0x20` are both `0x8F7003C8` = segment base + `0x3C8`. That value is **not**
the table base (`0xA8`), the signature (`0x618`) or the certs (`0x680`), and no page or 48-byte
boundary maps it onto any of them. `[I]` they are load-time destination addresses in a scratch
buffer, not file offsets. `[U]` words `0x40`/`0x44`/`0x4c`/`0x50` remain unassigned.

---

## 4. The embedded QuRT linker/memory-map XML — the real delta

### 4.1 Where it is, and why naive scanning misses it

`[F]` The image contains **9 XML documents, only 8 of which carry `<?xml`**. The ninth — the
memory map — starts directly with `<image>`:

```
total <?xml: 9
image doc first 24B: b'<image><program_name_map'
has decl? False
```

**`[F]` Methodological finding: enumerate by root-element close-tag, not by declaration.** A
scanner keying on `<?xml` misses the single most informative document in the file.

`[F]` Extents and containers:

| # | document | offset | len | root | outer PH |
|---|---|---|---|---|---|
| 1–6 | policyman (`hw_bands_filter`, `policy_list`, 4× `policy`) | 25,636,840… | 740…113,141 | — | 20 |
| 7 | `NvData` format-string template | 33,798,162 | 364 | `NvData` | 20 |
| 8 | QuRT `build_vars` | 36,553,056 | 344 | `build_vars` | 20 |
| 9 | **QuRT `image` memory map** | **37,082,172** | **5,221** | **`image`** | **21** |

`[F]` Two of the nine `<?xml` hits are not live documents: offset 32,918,190 is a bare `<?xml`
string literal with no terminator, and the `NvData` hit contains `%08X` placeholders and fails
to parse. Both are recorded so no later reader mistakes them for documents.

`[F]` Both QuRT documents are **length-prefixed**: the u32 immediately before each equals its
measured length (`0x158`=344, `0x1465`=5221). `[I]` a build-time blob table is walked by
length, not by scanning for XML.

### 4.2 The document parses natively

`[F]` The 5,221-byte document is complete and well-formed — `xml.etree.ElementTree.fromstring`
accepts it with **no synthetic root**, contrary to the assumption that it was a fragment. It has
15 root children: 2 `program_name_map`, `build`, 11 `cache_policy`, 1 `memsection_gap`; `build`
holds 64 children — **56 `<section>` elements** plus 8 scalars. Two further `<section` strings
are inside XML comments and must not be counted.

`[F]` `<program_name_map>` declares exactly two QuRT processes: `root_process` (0) and
`audio_process` (1).

`[F]` The eight scalars:

| element | value |
|---|---|
| `clade_base_paddr` | `0xE0000000` |
| `max_elf_tlb` | `0x1000000` |
| `relocatable_image` | `false` |
| `gap_reclaim` | `unrestricted` |
| `pool_allocation_order` | `address` |
| `tlbdump_usage` | `compare` |
| `mapping_method` | `optimal` |
| `allow_map_wx` | `false` |

`[F]` 11 cache policies; the table aliases numerically (`writeback` and `l1_wb_l2_uncacheable`
both `0x0`; `writethrough` and `l1_wt_l2_uncacheable` both `0x1`), so the names are
documentation labels over a smaller hardware encoding, not distinct states.

`[F]` `<physpool>` elements: **zero**. Pools are only referenced by attribute
(`CLADE_DICT`, `TCM_POOL`, `ITCM_POOL`, `QURTOS_ISLAND_REGION_DDR`). Their definitions live
elsewhere in the image, in a NUL-terminated ASCII run at offset 42,256,300+ listing 12 pools in
order (`DEFAULT_PHYSPOOL` … `CLADE_DICT`, `AUTOSTACK_IMAGE_POOL`). `[I]` that run is the QuRT
physpool name table — the definition side of the XML's references.

### 4.3 The CLADE contract, as the vendor states it

`[F]` Eight `<section>` entries name the CLADE family, and two wildcards govern the region
windows:

| section | mapping | tlb_lock | cache_policy | physpool | copybytes | clade_register |
|---|---|---|---|---|---|---|
| `.clade.dict` | rx | boot | — | `CLADE_DICT` | 4 | — |
| `.clade.exception_high` | rx | — | 1 | `TCM_POOL` | — | — |
| `.region_high_clade_protected_memory` | — | — | — | — | — | `clade_region_high_pd0` |
| `.region_low_clade` | — | — | — | — | — | `clade_region_low_pd0` |
| `.clade.comp` | rx | boot | — | — | — | `clade_comp` |
| `.clade.exception_high` | — | — | — | — | — | `clade_exception_high` |
| `.clade.exception_low_large` | rx | boot | — | — | — | `clade_exception_low_large` |
| `.clade.exception_low_small` | rx | boot | — | — | — | `clade_exception_low_small` |
| `.clade.metadata` | rx | boot | — | — | — | — |

| wildcard | attributes |
|---|---|
| `*region_*_clade*` | `tlb_lock="root"` |
| `*region_*_clade*` | `tlb_lock_min_size="0x100000"` |

`[F]` The document's own comments state the purpose of each directive, and the register names
line up with diagnostics compiled into the same image:

| XML `clade_register` | register named in kernel strings |
|---|---|
| `clade_comp` | `CladeCompPDX` ("used to program CladeCompPDX register") |
| `clade_exception_high` | `CladeExcHiPDX` |
| `clade_exception_low_large` | `CladeExcLowPDX` |
| `clade_exception_low_small` | `CladeExcLowSmallPDX` |
| `clade_region_high_pd0` / `clade_region_low_pd0` | `CladeRegion` |

`[F]` The matching runtime errors exist at offset 971,600–972,400: `Invalid Clade address!!!`,
the filename `clade.c`, `Kernel Error: invalid QURTK_clade_exc_hi_word or
QURTK_clade_dict_word!!!`, `Kernel Error: invalid QURTK_clade_cfg_base !!!`, `Kernel Error:
Invalid QURTK_clade2_cfg_base !!!`, `Kernel Error: Invalid CLADE2 configuration !!!`.

`[I]` (basis: the register correspondence and the in-file comments) the XML is **build-time
input to the QuRT image builder**, which turns each `clade_register="X"` into the physical
address of the named section and bakes it into the corresponding `QURTK_clade_*_cfg_base` /
`Clade*PDX` value. The runtime kernel then *validates* those baked values — which is exactly why
the "invalid … cfg_base" strings exist.

`[F]` The XML is **not read at runtime**: no pointer to either document's virtual address exists
anywhere in the image (0 references to `0xc8d1043c` and `0xc51aa160`). `[I]` it is carried as
inert build provenance.

`[F]` The four roles the contract assigns, with the asymmetry that proves intent: `.clade.dict`
and `.clade.comp` are `tlb_lock="boot"` (**dynamic** remap), while the two `.region_*_clade*`
windows inherit `tlb_lock="root"` with a **1 MiB** `tlb_lock_min_size` (**static**, large-page).
The vendor deliberately gave the two address spaces opposite TLB treatment.

`[F]` `clade_base_paddr = 0xE0000000` lies **outside every LOAD segment** in both address
spaces (max `p_paddr` end `0x8F702000`, max vaddr end `0xCE6F0000`). `[I]` CLADE is a separate
physical aperture, not a LOAD segment — which is precisely why the `.region_*_clade*` VA-side
descriptors exist at all: the CPU sees uncompressed code at `0xc…` VAs, the decompressor reads
compressed data from `0x8…` PAs, and the dictionary sits at `0xE0000000`.

### 4.4 The ELF corroborates the XML

`[F]` Two LOAD segments are compressed-in-file / expanded-in-memory, and they are exactly the
ones the XML's `candidate_compress_section` names point at:

| PH | `p_paddr` | `p_filesz` | `p_memsz` | ratio |
|---|---|---|---|---|
| 19 | `0x8270E000` | 8,720,200 | 33,562,624 | **3.85×** |
| 20 | `0x84710000` | 11,120,444 | 72,871,936 | **6.55×** |

`[F]` PH 19 ends at vaddr `0xC4710000` and PH 20 begins there — exactly contiguous.

`[I]` This is *why* the XML ships inside the image: the ELF alone gives compressed bytes and an
expanded size but no contract for expansion, so the ELF is **not self-describing** for these
two segments.

---

## 5. Per-segment classification `[I]`

Using rizin/radare2's vocabulary — `ELF` / `MBN` signature / `Q6ZIP` / `CLADE2` / `zlib` — but
assigning every class with stated evidence, which no public tool does (see §7.3).

| class | segments | evidence |
|---|---|---|
| header table | 0 | `p_filesz=980 = ehsize+phnum×phentsize`; contains `0x7fELF` at 0 |
| metadata / hash | 1 | 5-region layout, SHA-384 table, ECDSA P-384 sig, 3-cert chain |
| code (entry) | 2 | `R-X`; `p_paddr == e_entry`; packet structure, see below |
| code | 9, 11, 12 | `PF_X`; packet-≤4 fraction 0.816 / 0.814 / 0.831 |
| code, partly empty | 3, 4, 7, 8, 14 | `PF_X` but 22–80% zero words |
| rodata / data | 6, 10, 20, 21, 26 | no `PF_X`; entropy 8.6–14.8 bits/word |
| rw data | 18, 19, 23 | no `PF_X`, `PF_W`; entropy 4.8–7.5, 4.6–75% zero |
| fill / near-empty | 5, 13, 16, 17 | no `PF_X`; 93–100% zero words |
| `.bss` | 15, 22, 28 | `p_filesz=0` |
| zlib-compressed | **25** | `78 9c`; inflates 1,130,444 → 6,247,419 B |
| high-entropy RW blob | 24 | no `PF_X`; 19.69 bits/word over 40.4 MB |
| 220-byte rodata | 27 | `R--`; 220 B; head `00 00 00 00`, entropy 5.64 bits/word |

That is all 29 indices: 0, 1, 2, 3–17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28.

`[F]` **Segment 25 is the only zlib stream.** Every other segment fails the header check
(`CM=8`, `FCHECK` divisible by 31). It inflates with `eof=True`, **zero unused and zero
unconsumed bytes**, so `p_filesz` is exactly the stream with no slack. Inflated content does not
begin with an ELF (`130020578fcf30ec…`) — `[U]` its meaning.

`[F]` `p_memsz` for segment 25 is 1,130,496 = `p_filesz + 52`, far below the 6,247,419-byte
inflated size. `[I]` `p_memsz` is meaningless for this segment; decompression allocates its own
buffer at runtime.

### 5.1 Two corrections to the working brief

`[F]` **Parse bits are `bits[15:14]`, not the low 2 bits.** LLVM
`HexagonBaseInfo.h` defines `INST_PARSE_MASK = 0x0000c000`. On segment 2 the low-2-bit
distribution is near-uniform (1114/307/392/823 — noise), while `bits[15:14]` is strongly
structured (152/1264/31/1189). Using the low 2 bits would have produced a meaningless 100%
"legal" rate.

`[F]` **Segment 24 is not executable.** Its `p_flags` is `0x08000006` = R|W; `PF_X` is clear. The
executable segments are only **2, 3, 4, 7, 8, 9, 11, 12**, and the largest is **12**
(2,754,352 B), not 24.

`[F]` **Segment 2 is not purely code.** Words 0–16 are an interrupt/exception vector table —
word 0 jumps forward to `0xC1601834`, words 1–6 branch to **themselves** (`imm=0`), the standard
"unhandled vector" trap. From word 17 it is a descriptor table of 4-word records whose second
word is a segment vaddr (e.g. `0xC1610000` = PH 3). `[U]` the table's field semantics.

### 5.2 A heuristic that failed, reported as such

`[F]` "Fraction of words with a legal parse field" is **worthless**: all four 2-bit values are
defined, so it is 100% by construction. It is reported as a failed test, not a result.

`[F]` Packet-length (≤4 words) is a *real but imperfect* discriminator: executable segments 2,
4, 7, 9, 11, 12 score 0.675–0.846; non-executable 5, 13, 16, 17, 19, 23 score 0.000–0.104. But
it **false-negatives** on exec segments 3/8/14 and **false-positives** on 24 (0.637) and 25
(0.822 — compressed data). `[I]` it separates in aggregate and fails on individual large
segments; it cannot certify a segment as code on its own.

---

## 6. Content census `[F]`

| pattern | count |
|---|---|
| `Assertion (` | 2,661 |
| `Kernel Error` | 6 |
| `Kernel Warning` | 2 |
| `*.c\0` occurrences | 8,635 |
| distinct `.c` basenames | 5,173 |

`[F]` The text after `Assertion (` is a **C condition expression**, not a component name
(`Assertion (coproc_id < FW_COPROC_NUM_COPROC) failed`). A prefix-count over that text returns
variable names (`0`, `data`, `buf_addr`, `status`) and is **wrong** — discarded. The real
component signal is the **source filename** that follows each assertion string.

`[I]` Top component prefixes by distinct basenames: `rflm` 1190, `lte` 954, `nr5g` 536, `rfe`
390, `ds` 304, `ps` 259. This is primarily an **RF front-end + LTE + 5G NR** firmware. `sdr865`
appears 66 times, naming the **SDR865 transceiver** — a concrete hardware identification.
`csf` (274) is the highest-signal non-RF token (crypto offload); `q6zip` (9), `dlpager` (13) and
`QURTK` (7) confirm the layered kernel/DMA/paging/compression structure.

`[F]` Identity strings, verbatim:

```
QC_IMAGE_VERSION_STRING=MPSS.HI.2.5-01066-SDX55_RMTEFS_PACK-1.57117.5.64392.4
IMAGE_VARIANT_STRING=sdx55.rmtefsmd.prodQ
OEM_IMAGE_VERSION_STRING=dg02-pool06-kvm58
```

Build stamp `20220201_221948` (2022-02-01). `[I]` V67 ↔ SDX55M ↔ 2022-02-01 are mutually
consistent. `[U]` a fat container can embed strings from sibling images, so 1:1 attribution of
every `MPSS.` string to this ELF is inference from co-location, not proof.

### 6.1 The "47.7%" figure — corrected

`[F]` The issue title's share is **47.65% of the 654 extracted FAT files** (176,550,702 B), not
of the partition. Against the 192,278,528-byte `modem.img` partition it is **43.75%**. Both
numbers are given so the headline figure is not misread as a partition share.

---

## 7. Prior art — what survives, what does not

Queries run **2026-11-20**; 47 queries across Sourcegraph, DuckDuckGo and SearXNG. Exact strings
and hit counts in the issue comment ledger.

### 7.1 Refuted — must not be claimed

`[F]` **`p_flags` bit `0x08000000` as a discovery is dead.** It is `BIT(27)` =
`QCOM_MDT_RELOCATABLE`, in mainline since **v4.11 (2017)** (bisected across tags: absent in
v4.10, present v4.11→master), used at `mdt_loader.c:258,369` and `qcom_q6v5_mss.c:1474`, and
independently reimplemented in radare2 and rizin (2025).

`[F]` **"We discovered the CLADE contract" is dead.** cub3d, *"CLADE, SLAYED"*
(`https://cub3d.pw/blog/03-clade-slayed/`) already publishes the TLV tags (`0x04` dictionary,
`0x05` base/config, `0x13` exc-hi), the four-region decomposition, the `0x2000`-byte dictionary
sizes and `clade_on()`. mzakocs ships `clade_extractor_pixel_5.c`; nlitsme ships `unclade.py`;
srlabs documents `.clade.comp` extraction; patent **US9300320B2** is the primary source.

`[F]` **"A novel per-segment taxonomy" is dead.** rizin and radare2 already define
`RZ_BIN_MDT_PART_COMPRESSED_Q6ZIP` / `_CLADE2` / `_ZLIB` alongside `ELF` and `MBN`.

### 7.2 What survives

`[F]` **No prior art for the XML-embedding claim.** Zero hits across all three engines for
`clade_base_paddr`, `clade_register`, `region_low_clade`, `max_elf_tlb`, `tlbdump_usage`,
`gap_reclaim`, `.clade.metadata`, `.clade.exception_*`, `QURTK_clade_cfg_base`. These are exactly
the identifiers a QuRT linker/memory-map XML contains.

> **The delta, stated precisely:** the CLADE contract is not merely *inferable* from decompiled
> QuRT code (as cub3d showed) but is **declared by the vendor in a machine-readable document
> carried inside the firmware image itself**. The novelty is **provenance and form**, not
> content.

`[F]` **The taxonomy vocabulary is prior art; the assignment is not.** rizin/radare2 name all
five classes but **never assign the compressed ones** — grepping `rz_mdt.c` and `r2_mdt.c` shows
`part->format` is only ever `ELF`, `MBN` or `UNIDENTIFIED`; the enum members appear only in the
`switch` that prints them. So a defended per-segment classification of a real image is a
legitimate **application**, and the unimplemented enum is both the opening and the proof the
taxonomy itself cannot be claimed.

`[F]` **The metadata-segment format is already documented in this repo.** `research/fleet/pil-metadata-sweep.md`
covers 28 images (16 SM8250 + 12 SDM845). This note adds the modem row and the
`w[4]-w[5] = w[9]+w[7]` refinement (§3.4); it does not re-derive the format.

### 7.3 Honest negatives

`[N]` **`clade_base_paddr = 0xE0000000` is not a format constant.** cub3d's Pixel 5 example uses
`0xCD100000` and dicts near `0xCF5E8000`. One value in one image is not a device-independent
constant, and this note does not present it as one.

`[N]` **`29` is a property of this file, not of the format.** rizin/radare2 handle variable part
counts across `.bNN` splits.

`[N]` **`.clade.metadata` is the weakest-named element** — zero public hits outside this
artifact, and it carries no `clade_register`. Recorded as declared by the vendor, not as
corroborated.

`[N]` **No byte layout for `.clade.dict` / `.clade.comp` was recovered.** The XML names them but
gives no sizes or offsets, and with `e_shnum=0` they cannot be located by name. Locating them
needs the image builder's blob table or dynamic analysis. `[I]` (weak) PH 20 is the better
`.clade.comp` candidate because the companion `build_vars` blob sits at its very end, while PH
19's tail is zero padding.

`[N]` **No device count is asserted.** `qdsp6sw.mbn` is **not** an SDX55-only name:
`qcom_q6v5_pas.c:1813-1815` binds it to `shikra_mpss_resource`, and linux-firmware ships it for
QDU100. Defensible floor: **≥32 mainline DT bindings** (19 `-mpss-pas` + 13 `-mss-pil`) and
**≥4 SoC families** sharing the filename (SDX55, SDX65, Shikra, QDU100). A phone count is
`[U]`.

`[N]` **GitHub code search was unavailable** (`api.github.com/search/code` → HTTP 401 without a
token; `grep.app` → Vercel checkpoint; `searchcode` → 404; `git.kernel.org` cgit → Anubis
proof-of-work wall). All GitHub coverage came via Sourcegraph's index, which may be incomplete.
The (b)-identifiers should be re-run with a token before publication.

`[N]` **`allocframe` / `dealloc_return` / `deallocframe` occur 0 times in segment 2.** Expected
for a vector table (no frame, no return) — they are absent from this 10 KB stub, not from the
image; the bulk code is in segments 9 and 12.

---

## 8. Reproduce

```
cd implementations/hexagon-qdsp6
python3 -I make_fixture.py
python3 -m unittest -q                 # 47 tests, 1 skip
python3 -I hexagon_probe.py <path to image_sdx55m_qdsp6sw.mbn>
```

`python3 -I` for the CLI; `python3 -m unittest` **without** `-I` for the suite, because `-I`
drops the CWD from `sys.path`. Fixtures are synthetic and gitignored — `fixtures/.gitignore`
excludes the whole directory, since the root `.gitignore` does not cover the `.hexbin`
extension.

`[F]` The parser is validated across all three container generations on the real corpus —
**39 `EM_QDSP6` objects** (enchilada 6, instantnoodle modem volume 15, instantnoodle vendor 9,
larry vendor 9) parse with **zero invariant violations**, spanning `monolithic`, `split-mdt` and
`self-contained` forms. Of those, 15 resolve to a named ISA (8 × v66, 7 × v67); the other 24
carry `e_flags = 0x3`, a value LLVM's `EF_HEXAGON_ISA_*` table does not name, so the parser
reports `unknown(0x3)` rather than guessing.
