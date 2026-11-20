# implementations/cdsp-fleet — clean-room Qualcomm split-MDT CDSP container probe

A parser and validation probe for the Qualcomm split-MDT firmware container: the
`image_cdsp.mdt` file plus its `.bNN` siblings, as shipped at
`vendor/firmware/` and `firmware/image/` on CDSP-class devices. The probe
answers the question the census could not: **where does the structure actually
live, and does a given image satisfy the loader's own contract?**

It lives entirely in the program headers. The `.mdt` is an ELF32
little-endian executable with **no section headers** (`e_shnum == 0`): segment 0
is the ELF header plus the program-header table, segment 1 is the hash and
certificate block, and every payload byte lives in a sibling `.bNN` file named
by segment index. That is why the measured image is 7660 B while the payload it
describes is 4,129,418 B.

Sibling documents own the other views of this family and are **not** duplicated
here:

| document | owns |
|---|---|
| `../../research/cdsp-fleet/container.md` | the per-field measurement of the real image, the packet-statistics ISA discussion, the 12-image corpus scan and the honest negatives |
| `../../research/cdsp-fleet/census.md` | the fleet census across the data root |
| `../../pil-manifests/` | the `*.jsn` files that sit next to a `.mdt`; they are PDR service registries, **not** split-MDT manifests |

## Clean-room statement

This component was written from public, permissively- or GPL-licensed sources
only, listed in the ground-truth table below. No decompiled code, no proprietary
documentation, no vendor header and no disassembly were used by the implementer.
Every number the probe prints is either (a) read from the file in front of it or
(b) one of the public constants named below. Anything else is reported as
`[OPEN]` rather than guessed. Fixtures are synthetic and generated from a
SHA-256 counter stream; no vendor payload byte is committed to this repository.

**Ground truth (public sources only):**

| what | where | what it settles |
|---|---|---|
| `EM_HEXAGON` = 164 (`EM_QDSP6`) | `include/uapi/linux/elf-em.h` (GPL-2.0 WITH Linux-syscall-note) | `e_machine` for every DSP image |
| `Elf32_Ehdr` / `Elf32_Phdr` field order and sizes; `PT_NULL`, `PT_LOAD`; `PF_R`/`PF_W`/`PF_X` | `include/uapi/linux/elf.h` (same licence) | the 52-byte header, the 32-byte program header, and the low three `p_flags` bits |
| `QCOM_MDT_TYPE_MASK` (`7 << 24`), `QCOM_MDT_TYPE_HASH` (`2 << 24`), `QCOM_MDT_RELOCATABLE` (`1 << 27`) | `include/linux/soc/qcom/mdt_loader.h` (GPL-2.0-only) | the bit positions of the segment-type field and the relocatable/pool bit — this is what makes the `p_flags` layout a fact rather than a guess |
| `mdt_phdr_loadable()`, `qcom_mdt_bins_are_split()`, `qcom_mdt_read_metadata()`, `mdt_load_split_segment()` | `drivers/soc/qcom/mdt_loader.c` (GPL-2.0-only) | which rows are loaded, the split predicate, the "hash follows the header" behaviour, the sibling naming rule `sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment)`, and the refusal of a sibling whose size differs from `p_filesz` |
| packed `p_flags`: bit 27 pool, bits 26-24 segment type, bits 23-21 access type, bit 20 page mode, bits 2-0 R/W/X, plus the segment-type and access-type vocabularies | coreboot `util/qualcomm/mbn_tools.py` (GPL-2.0) | the full decode, independent of the kernel masks |
| `INST_PARSE_*` at `[15:14]`, `INST_ICLASS_*` at `[31:28]`, `EF_HEXAGON_ISA_V*` | `llvm/lib/Target/Hexagon/MCTargetDesc/HexagonBaseInfo.h`, `llvm/include/llvm/BinaryFormat/ELF.h` (Apache-2.0-with-LLVM-exception) | the ISA nibble in `e_flags`, and the reason packet statistics stay out of this probe's claims |

## Files

| file | role |
|---|---|
| `cdsp_probe.py` | the probe: `Elf32_Ehdr` decode and validation, program-header walk, full `p_flags` decode, sibling-size classification, orphan detection, entry-point placement, text and JSON renderers. CLI `python3 -I cdsp_probe.py <image.mdt> [--json out.json] [--brief]`; exit 0 = every invariant holds, 1 = at least one violation, 2 = usage or IO error |
| `make_fixture.py` | deterministic synthetic fixtures built from the measured layout only (no proprietary bytes): six image sets, 60 files, 775,214 B total |
| `fixtures/*.mdt`, `fixtures/*.bNN` | synthetic fixtures — the good images, a BSS-dominated image, a wrong-size sibling, a bad magic, a truncated tail and a missing hash row. **`*.mdt` and `*.b[0-9][0-9]` are gitignored** — regenerate with `python3 -I make_fixture.py` |
| `test_cdsp_probe.py` | unittest suite: `python3 -m unittest discover -q` — **139 tests**; the live-image tests skip cleanly when no proprietary image is on disk |

## Usage

```bash
# single file, full report
python3 -I cdsp_probe.py /path/to/image_cdsp.mdt

# one line per file
python3 -I cdsp_probe.py /path/to/image_cdsp.mdt --brief

# machine-readable
python3 -I cdsp_probe.py /path/to/image_cdsp.mdt --json out.json
```

## The p_flags bit layout

`decode_pflags()` reports every field of the 32-bit word and asserts nothing it
cannot source. The layout is the coreboot one, cross-checked against the kernel
masks:

| bits | field | values |
|---|---|---|
| 31-28 | not part of any public layout | expected 0; a non-zero value is a violation, reported as `unknown_high` |
| 27 | pool index / `QCOM_MDT_RELOCATABLE` | 0 or 1 |
| 26-24 | segment type | 0 `L4/AMSS`, 1 `AMSS`, 2 `HASH`, 3 `BOOT`, 4 `L4BSP`, 5 `SWAPPED/XBL_SEC`, 6 `SWAP_POOL`, 7 `PHDR` |
| 23-21 | access type | 0 `RW`, 1 `RO`, 2 `ZI`, 3 `NOTUSED`, 4 `SHARED`, 5, 6, 7 `RWE` |
| 20 | page mode | 0 `NON_PAGED`, 1 `PAGED` |
| 2-0 | ordinary ELF permissions | `PF_X` 1, `PF_W` 2, `PF_R` 4 |

Two independent role agreements make the decode verifiable rather than merely
self-consistent, and both are asserted by the suite on the synthetic fixture and
on the real image:

- segment 0 decodes to type **7 (PHDR)** and really is the ELF header plus the
  program-header table — its `p_filesz` equals
  `e_ehsize + e_phnum * e_phentsize` (468 on the measured image);
- segment 1 decodes to type **2 (HASH)** and really is the hash/certificate
  block.

A negative worth carrying: the ZI access value is **not** a proxy for a zero-fill
segment. On the measured image the `p_filesz == 0` rows are `{7, 10, 12}` and the
ZI-tagged set is empty. Zero-fill is expressed by `p_filesz == 0 && p_memsz > 0`,
never by the access field.

## The sibling-size invariant

Stated as the loader states it, not as a convention invented here:

> For every program-header row with `p_filesz > 0`, a sibling
> `<stem>.bNN` exists next to the `.mdt` and its size equals `p_filesz`
> exactly. A row with `p_filesz == 0` has no payload to place and therefore
> no sibling.

`mdt_load_split_segment()` builds the name by overwriting the last three
characters of the `.mdt` name (`image_cdsp.mdt` becomes `image_cdsp.b00`) and
rejects a sibling whose size differs from `p_filesz`, so the size half of the
invariant is the loader's own contract. The probe classifies each row into one
of five verdicts:

| verdict | meaning | counts as ok |
|---|---|---|
| `MATCH` | sibling present, size equals `p_filesz` | yes |
| `SIZE-MISMATCH` | sibling present, size differs | no |
| `MISSING` | `p_filesz > 0` but no sibling | no |
| `ABSENT-as-predicted` | `p_filesz == 0` and no sibling | yes |
| `ZERO-BYTE-SIBLING` | `p_filesz == 0` and an explicit 0-byte sibling exists | yes, and noted |

The measured image satisfies the invariant 13/13: ten `MATCH` and three
`ABSENT-as-predicted`. The wider corpus diverges in both directions, and the
probe reports each without crashing: `larry` `evass.mdt` and `vpu20_1v.mdt`
ship explicit zero-byte siblings (`ZERO-BYTE-SIBLING`, accepted with a note),
and `vpu20_1v.mdt` has no `b00` at all despite `phdr[0].p_filesz = 692`
(`MISSING`, a violation naming the expected size). So the zero-fill half of the
rule is an observation about this image and the 12-image Hexagon corpus, not a
law.

## The header block carries a file size and no memory size

Segment 0 is `PT_NULL` with segment type 7 and carries `p_filesz = 468` with
`p_memsz = 0`. Every Qualcomm split image does this: a header block, and the
hash block after it, have a file image and no memory image, so `p_memsz` is
legitimately zero while `p_filesz` is not. The probe reports this as an
`[F] observed convention` note rather than a violation. The general
`p_filesz > p_memsz` refusal is **not** weakened: it still fires for a
`PT_LOAD` row, where it is a real error. Both directions are tested — the note
for the `PT_NULL`/PHDR case, and the violation for a load row.

## Invariants checked

| name | rule | source |
|---|---|---|
| `header_block` | `phdr[0]` is `PT_NULL`, decodes to type 7, and `p_filesz == e_ehsize + e_phnum * e_phentsize` | ELF gABI + measurement |
| `hash_follows_header` | exactly one further `PT_NULL` row carries type 2, its `p_type` is `PT_NULL`, and `phdr[0].p_filesz + phdr[hash].p_filesz == len(mdt)` | `qcom_mdt_read_metadata()` |
| `sibling_size` | the five-verdict rule above | `mdt_load_split_segment()` |
| `relocatable_uniform` | bit 27 agrees across every `PT_LOAD` row | `QCOM_MDT_RELOCATABLE` |
| `flags_high_clear` | bits 31-28 are zero on every row | no public layout defines them |
| `entry_in_load` | `e_entry` lies in some `PT_LOAD` row's `[p_paddr, p_paddr + p_memsz)` | measurement: `0x87800000` equals `phdr[2].p_paddr` exactly on the measured image |

## Test status

```
$ python3 -I make_fixture.py && python3 -m unittest discover -q
Ran 139 tests in 0.389s
OK
```

Coverage, by class: fixture existence, count, total byte size, byte-for-byte
determinism and the no-vendor-bytes guard (11); every `Elf32_Ehdr` field plus
each rejection path (21); the `p_flags` decode against the known-good words, the
bit layout, every access value and the page-mode field (17); the program-header
walk with each field read back from the file bytes (18); the sibling rule in all
five verdicts, BSS rows, explicit zero-byte siblings, a named missing sibling
and orphans (17); the structural rules including the `PT_NULL` convention (14);
the BSS-dominated fixture (5); malformed input (8); the text and JSON renderers
(7); the CLI contracts (10); and 13 tests that read real, git-ignored firmware
when it happens to be on disk (11 in the real-blob class, 2 in the sibling
class) — all 13 skip cleanly on a fresh clone, so the suite never requires a
proprietary byte.

## [OPEN]

- Why a given segment is RWX and the next is RW. That is linker policy, not
  decodable from `p_flags`.
- What consumes the payload at runtime beyond the generic PAS loader. That
  includes whether the loader honours `p_paddr` over `p_vaddr`: `mdt_loader.c`
  reads as if it loads by `p_paddr`, but the file alone does not prove it.
- Whether a segment holds Hexagon instructions. `p_flags` and `p_type` do not
  say, and this probe performs no disassembly. The packet statistics in
  `../../research/cdsp-fleet/container.md` are `[I]` and stay out of this
  component's claims.
- The meaning of `e_flags` nibbles outside the public `EF_HEXAGON_ISA_V*` table.
- The contents and record semantics of the hash/certificate segment.

## RULE 0 prior-art record

Searches run 2026-11-20 for the split-MDT container as a *validation and decode*
target. The prior art is real and is acknowledged here rather than ignored:

| project | what it does | relation |
|---|---|---|
| `linux-msm/pil-squasher` | reassembles a split `.mdt` plus `.bNN` set into one ELF | adjacent: it consumes the same sibling layout, for a different purpose |
| `bkerler/qc_modem_tools` (`unify_trustlet`) | merges a split image back into a flat ELF for analysis | adjacent: same file family, merge only |
| `remittor/qcom-mbn-tools` (`pil-splitter.py`) | splits a single ELF into `.mdt` + `.bNN` | adjacent, and the *inverse* direction |
| LibrePhone MDT Tool | reads and splits Qualcomm MDT images | adjacent: tooling, not validation |
| `NerdTIV/QDig` | an IDA loader that recognises the Qualcomm ELF variant | adjacent: loads for disassembly, does not check the invariants |

**Distinct delta.** All five are *transformers*: they move bytes between the
split and flat representations, and none of them reports whether a given image
satisfies the loader's contract. This component is a **validation and decode
probe**: it does not write, merge or split any byte, and it emits a per-row
verdict against the `mdt_load_split_segment()` contract, a full `p_flags` decode
sourced to two independent public layouts, and an explicit `[OPEN]` list for
everything it cannot source. It is not another squasher. Where a prior-art tool
would silently produce an output file from a wrong-sized sibling, this one names
the sibling, the expected size and the observed size, and exits non-zero.

## Value statement

**What this buys the program.** A split-MDT image can now be checked, not just
unpacked. The container is specified well enough that a free implementation can
walk it, classify every row, and know whether the sibling set on disk is the one
the loader expects — which is the failure mode that matters in practice, since a
short or missing `.bNN` file is silent to every merge tool and fatal to the
loader.

**What it does not buy.** It does not decode payload semantics. Which segments
hold code, what the hash records mean, and how the DSP schedules the result are
all `[OPEN]` and are listed explicitly rather than guessed.

Not legal advice, not a replacement implementation. Regulatory/legal hurdles:
`../../upstream-contribution/radio-regulatory-hurdles.md`.
