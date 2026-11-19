# Why readelf and mdt_loader.c show different addresses — for upstream issue #40

One-page answer note, from **public kernel source + lab-derived MDT
facts** ([upstream issue
#40](https://codeberg.org/rsavoye/librephone/issues/40): "When I run
*readelf*, I get different addresses than what I see after
instrumenting mdt_loader.c ... why does mdt_loader show different
addresses in the phdr header?"). Written 2026-11-16.

**Legend:** [PUBLIC] = mainline kernel fact; [LAB] = lab-derived fact.

## 1. The short answer

`readelf` prints the program headers **as stored in the file**.
`mdt_loader.c` does not show stored addresses — it computes
**post-relocation runtime addresses**. If the image is relocatable,
every loadable segment's runtime location differs from the stored
`p_paddr` by a base shift, so an instrumented loader legitimately
prints different numbers than readelf. Both are "correct"; they
answer different questions (file layout vs runtime layout).

## 2. The mechanism, step by step (all [PUBLIC], mainline
`drivers/soc/qcom/mdt_loader.c`, fetched 2026-11-16, 508 lines)

1. **Relocatable bit.** Each loadable phdr carries Qualcomm flags in
   `p_flags`' upper bits: `QCOM_MDT_RELOCATABLE = BIT(27)`
   (`include/linux/soc/qcom/mdt_loader.h`). If **any** loadable
   segment has the bit set, `relocate = true` —
   `mdt_loader.c` lines ~258 and ~369.
2. **Base selection.**
   - relocatable image: `mem_reloc = min_addr` (the lowest stored
     `p_paddr` of all loadable segments);
   - non-relocatable: `mem_reloc = mem_phys` (the physically
     allocated chunk).
3. **Per-segment rebase.** The loader copies each segment to
   `offset = phdr->p_paddr - mem_reloc` inside the allocated region
   and reports `*reloc_base = mem_reloc` (`qcom_mdt_load_no_init`,
   lines ~344–435). So a segment stored at paddr P appears at runtime
   at `mem_phys + (P - min_addr)` for relocatable images — while the
   PAS metadata path (`__qcom_mdt_pas_init` → `qcom_pas_init_image`)
   hands the **un-relocated** metadata to TrustZone for
   authentication, which is why signature checks still pass on the
   stored layout.
4. **Also filtered out before any of this** (common source of
   confusion):
   - hash segments (`p_flags & QCOM_MDT_TYPE_MASK ==
     QCOM_MDT_TYPE_HASH`, i.e. type bits `2<<24`) are skipped by
     `mdt_phdr_loadable()` — they exist in readelf's phdr list but
     never get load addresses;
   - zero-`memsz` and non-PT_LOAD phdrs are skipped;
   - `qcom_mdt_bins_are_split()` decides whether payloads come from
     the `.mdt` itself or from the sibling `.bNN` files (segments
     whose extent falls outside `fw->size`).

So the visible discrepancies an instrumented loader reports are: (a)
relocated bases for relocatable images, (b) missing hash segments,
(c) split-image file offsets. None of these is a readelf bug.

## 3. The FP6 cross-check ([LAB])

The lab's committed censuses make this concrete for this device:
- `wpss.mdt` declares e_machine 164 (EM_HEXAGON) with phdrs marking
  b01/b02/b03/b05/b06 executable — the per-segment `.bXX` files carry
  **junk ELF headers** (zeros, even x86=3 on wpss.b08), so any tool
  that reads a segment file in isolation sees noise: the `.mdt` phdr
  table is the only authoritative address/permission source
  (`qualcomm-fp6/docs/fp6-architecture-census.md`, F-7/F-20/F-22).
- The same junk-header rule shows up in the boot-chain family
  (outer xbl wrapper ELF machine=1, multiimgoem e_type=0) —
  `qualcomm-fp6/docs/bootchain-census.md`,
  `qualcomm-fp6/docs/trustzone-census.md` (F-7).
- Practical consequence for #40's tooling: parse the `.mdt` phdrs and
  apply the relocatable-bit math; ignore the `.bXX` headers entirely.

## 4. Test-suite hooks

1. Assert the rebase formula on a public FP6 relocatable MDT:
   runtime_addr(P) = mem_phys + (P − min_addr) over all loadable
   segments, and hash-type segments excluded.
2. Assert `qcom_mdt_bins_are_split`'s decision against the on-disk
   family (modem/adsp/cdsp/wpss = split; tz/hyp = monolithic ELF64).
3. Round-trip: a loader that reproduces `qcom_mdt_load_no_init`'s
   segment placement in memory must match byte-for-byte on a
   re-extracted nightly.

## Sources consulted (accessed 2026-11-16)

- https://raw.githubusercontent.com/torvalds/linux/master/drivers/soc/qcom/mdt_loader.c (fetched, quoted line references)
- https://raw.githubusercontent.com/torvalds/linux/master/include/linux/soc/qcom/mdt_loader.h (QCOM_MDT_RELOCATABLE = BIT(27), TYPE_MASK/TYPE_HASH)
- Lab: `qualcomm-fp6/docs/fp6-architecture-census.md`,
  `docs/bootchain-census.md`, `docs/trustzone-census.md` (F-7
  junk-header methodology)

**Clean-room statement:** the mechanism above is upstream-kernel
source reading plus lab census facts; nothing from disassembly.
