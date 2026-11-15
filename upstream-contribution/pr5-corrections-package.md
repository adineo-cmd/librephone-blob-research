# ADDITIONAL filing package — PR-5, PR-6 + issue answers (2026-11-15)

This is the **second** upstream contribution package, discovered by the
2026-11-15 "wants vs done" audit (see
[librephone-wants.md](librephone-wants.md)). It is **additional** to the
four paste-ready PRs in [README.md](README.md) — PR-1..PR-4 are
untouched and all their target texts were re-verified unchanged on
2026-11-15 (wireless.md AVR guess, b06 "error messages", b09 "PSX",
b07/b10, files.md bare bluetooth section).

Same rules as the first package: facts only, every number traces to a
committed lab finding, no blob content redistributed, terse factual tone
matching upstream's per-file doc voice, original wording extended rather
than contradicted.

New targets, re-fetched 2026-11-15 from
https://codeberg.org/rsavoye/librephone (branch `main`):

- `docs/other.md` — carries two claims the lab's verified census
  contradicts (PR-5).
- `docs/wpss.b01.md` + the WPSS section of `docs/wireless.md` — carry
  AVR-family claims the mdt program headers contradict (PR-6).
- Issues #38, #41, #42, #43, #33 — the lab already holds verified
  answers; paste-ready comments below (C-1..C-3).

Prior-art check (RULE 0, 2026-11-15): none of the 41 issues (open +
closed) mentions CAMERA_ICP, vpu, or Xtensa; the last 50 commits contain
no change to other.md or wpss.b01.md; no existing upstream doc or PR
corrects these claims. The lab's underlying ISA findings were
prior-art-audited at merge (F-6: raw e_machine values were publicly
dumped by gdrci/Research on 2026-10-08 — the lab's delta is the ISA
interpretation + family census; F-5/F-7/F-20/F-22 likewise).

---

## PR-5 — docs/other.md: CAMERA_ICP and vpu20_2v are RISC-V, not Xtensa

- **Target file:** `docs/other.md` (the `## Camera` and `## Trusted
  Computing Platform` sections)
- **Branch:** `docs/other-icp-vpu-isa`
- **Commit title:** `Correct CAMERA_ICP and vpu20_2v ISA descriptions`
- **PR title:** `docs/other.md: camera ICP and VPU firmware are RISC-V (historic e_machine 94), not Xtensa`
- **Depends on:** none

Current upstream text being corrected (verified 2026-11-15):

> * CAMERA_ICP.b\[0-9\]\[0-9\]
> 	* Tensilica Xtensa certificates
> * CAMERA_ICP.mbn
> 	* Tensilica Xtensa certificates

> * vpu20_2v.mbn
> 	* Xtensa 32 Bit executable with certs for Trusted Boot

**PR description (paste-ready):**

```
Two ISA corrections in docs/other.md, from static analysis of the
public LineageOS FP6 nightly (lineage-23.2-20261109):

- The camera ICP firmware family (CAMERA_ICP.mbn/.elf/.mdt and its
  .bXX payload segments) is not Xtensa: CAMERA_ICP.mbn is ELF32 with
  e_machine = 94, the historic RISC-V value used by early toolchains
  (EM_RISCV=243 was assigned later). Version CICP.FW.7.0-00021, with
  platform strings CAMERA_640_V1 ("Mimas") and CAMERA_740_V1 ("Skye").
- The VPU firmware family (vpu20_2v.mbn, vpu20_4v.mbn, vpu30_2v.mbn,
  vpu33_4v.mbn and the _unsigned variants) is the same historic
  RISC-V identification, e_machine = 94.

Method note (the same one already recorded in docs/wireless.md's
Current Research section): the per-segment .bXX files carry junk ELF
headers (zeros, even x86=3 on wpss.b08), so the family ISA comes from
the .mdt/.mbn headers plus entry-point sanity, not from the segment
files. The "certificates" part of the existing text is correct — the
MBN images carry the usual X.509 signing chain — only the processor
label changes.

The e_machine=94 raw values for these files have been publicly visible
in enumeration dumps since 2026-10-08; what is new here is the
interpretation (94 = early RISC-V) and the family census. Public
Qualcomm documentation does not state the ICP/VPU ISA; kernel sources
name the devices but not the cores.

Census write-up with the full evidence chain:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
```

**Doc change (paste-ready):**

In `## Camera`, replace the two description lines with:

```markdown
* CAMERA_ICP.b\[0-9\]\[0-9\]
	* payload segments of the camera ICP firmware (segment headers carry
	junk e_machine values — see the wireless.md method note)
* CAMERA_ICP.mbn
	* ELF32, e_machine = 94 (historic RISC-V; 243 was assigned later),
	version CICP.FW.7.0-00021, platforms "Mimas" / "Skye"
```

In `## Trusted Computing Platform`, replace the vpu line with:

```markdown
* vpu20_2v.mbn
	* ELF32, e_machine = 94 (historic RISC-V) with certs for Trusted
	Boot; same family as vpu20_4v, vpu30_2v, vpu33_4v
```

---

## PR-6 — docs/wpss.b01.md is not an ATmega8; wireless.md WPSS-section AVR instance

- **Target files:** `docs/wpss.b01.md` (append), `docs/wireless.md`
  (WPSS section, the "It seems to contain an ATmel AVR core..." paragraph)
- **Branch:** `docs/wpss-b01-hexagon-segment`
- **Commit title:** `Correct the wpss.b01 AVR reading`
- **PR title:** `docs: wpss.b01 is an executable segment of the Hexagon MDT image, not an ATmega8`
- **Depends on:** file **after PR-1** (same file, wireless.md; PR-1
  replaces the Wireless Chipset section, this PR touches the WPSS
  section — no textual conflict, but PR-1 first keeps the diff clean)

Current upstream text (verified 2026-11-15):

> This binary appears to be an ATMel AVR8 (ATmega8) micro-controller
> embedded in the WCN6750. ... Using the *radre2* program you can
> disassemble the raw binary into assembly. `r2 -e bin.relocs.apply=true
> -a avr wpss.b01` ... What weird is while the GNU toolchain has AVR
> support, objdump refuses to recognize the format, so it's also
> possible the generated disassembly is junk.

and (wireless.md, WPSS section):

> It seems to contain an ATmel AVR core for some application code. It
> looks like it also contains a RISCV core. The blob that seems to be
> an Intel x86_32 is suspicious.

**PR description (paste-ready):**

```
The AVR8/ATmega8 reading of wpss.b01 is not supported once the MDT
file structure (documented in docs/mdt.md) is taken into account:

- The wpss.mdt program headers mark exactly b01/b02/b03/b05/b06 as
  executable (PF_X) and declare e_machine = 164 (EM_HEXAGON). b01 is
  one of the executable code segments of that single Hexagon (DSP6)
  image — consistent with the Current Research note in wireless.md
  ("the various sections are probably split from a single file, which
  appears to be DSP6").
- The ATmega8 identification comes from radare2's forced `-a avr` on
  the raw segment bytes. Per-segment .bXX files carry junk ELF headers
  (zeros, even x86=3 on wpss.b08, a data segment), so any tool reading
  a segment file in isolation is decoding a slice of the Hexagon image.
  radare2 producing "assembly that looks good" and objdump refusing
  are both what a wrong-ISA forcing produces on such a slice — the
  same effect seen when wpss.b09's data tables are decoded as code.
- The x86_32-suspicious blob (wpss.b08) is a data segment: its x86
  header is junk (e_machine=3, entry 0x401) on a segment that carries
  the WLAN_UCODE_MOSELLE_4.2.0 ucode and QURT IPC buffer strings.

Verified facts that replace the AVR guess in both places:

- wpss.b07 is a complete ELF32 RISC-V executable (e_machine=243,
  entry 0x404000 = RV32 machine-mode startup), running Qualcomm's QURT
  RTOS (QURTK_* strings, mcause exception path, a build artifact named
  dog_hal_moselle_riscv.c). The event-dispatch code is Hexagon in
  wpss.b06 (see docs/wmi-dispatch.md). No AVR core is required to
  explain any wpss segment.

Census write-up with the full evidence chain:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
```

**Doc change (paste-ready):**

`docs/wpss.b01.md` — append (keep the original observations):

```markdown
## Update (2026-11)

The ATmega8 reading is not supported by the MDT structure documented in
[mdt.md](mdt.md): the wpss.mdt program headers mark exactly
b01/b02/b03/b05/b06 as executable and declare e_machine = 164
(EM_HEXAGON), so b01 is one of the executable code segments of a single
Hexagon (DSP6) image — matching the Current Research note in
[wireless.md](wireless.md) that the sections are probably split from
one DSP6 file.

The `-a avr` disassembly that "looks good" is a wrong-architecture
forcing on a slice of that image: the per-segment .bXX files carry junk
ELF headers (zeros, even x86=3 on wpss.b08, a data segment), so a tool
decoding a segment file in isolation sees an arbitrary byte stream.
objdump refusing the format and radare2 producing plausible-looking
noise are both expected in that case. The verified processor inventory
for this image: Hexagon code segments (b01/b02/b03/b05/b06), one
embedded ELF32 RISC-V executable (wpss.b07, QURT RTOS), and data
segments (b04, b08, b09, b10, b12).
```

`docs/wireless.md` WPSS section — replace the paragraph with:

```markdown
The firmware runs on a 32-bit RISC-V core (wpss.b07, verified at
instruction level) with Hexagon (QDSP6) code segments in the same MDT
image — see the Wireless Chipset section above and
[docs/wmi-dispatch.md](wmi-dispatch.md). No AVR core is present: the
earlier AVR readings came from forcing `-a avr` on raw segment files
whose ELF headers are junk (the method note in the Wireless Chipset
section). The blob that seems to be an Intel x86_32 (wpss.b08) is a
data segment — its x86 header is junk (e_machine=3, entry 0x401); it
carries the WLAN_UCODE_MOSELLE_4.2.0 ucode and QURT IPC buffer error
strings.
```

---

## Paste-ready issue answers

These are comments for existing upstream issues the lab's committed
censuses already answer. Post as plain comments (no PR needed); keep
the terse factual tone. LineageOS build: lineage-23.2-20261109 (FP6).

### C-1 — issue #38 ("Check for L4 kernel in WPSS blobs")

```markdown
Census result from static analysis of the FP6 wpss firmware
(LineageOS 23.2 nightly 2026-11-09, build WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1):

no L4/L4Ka-style vocabulary appears in the application firmware. The
RTOS is Qualcomm's QURT, running on the 32-bit RISC-V core:

- QURTK_thread_stop, "control reached after QURTK_thread_stop",
  thread start/stop with utcb= fields, TCB mutex/futex strings,
  qurt_lib, qurt_interrupt_status, "Could not register qurt fatal
  notification handler"
- the exception path prints the RISC-V mcause CSR
- a build artifact names the core directly: dog_hal_moselle_riscv.c

So for this device: QURT microkernel, not L4. This covers wpss.b07
(the RV32 application image) and the string surfaces of the other
segments; older Qualcomm wireless firmware generations may still be
L4-based — worth checking per-device rather than assuming either way.

Full census:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
```

### C-2 — issues #43, #41, #42 (the three UUID-named blobs)

Post on #43 (FD719D50-FFFB-11EB-9A03-0242AC130003) and #41
(05B04A44-BF30-42DF-9E2F-B366B980ED19):

```markdown
Identification from a census of the same FP6 image
(LineageOS 23.2 nightly 2026-11-09): these two UUID-named images are
QSEE trusted-app TAs for the secure-element service. The string
evidence:

- CESEService_* strings (secure-element service)
- GPQESE_Open / GPQESE_Transceive (GlobalPlatform SE API)

They ship as .mdt + .bXX splits inside modem/image — the QSEE TA
format handled by the qseecom interface, not by the PIL mdt_loader
(that is also why the kernel's mdt_loader being ELF32-only is not the
blocker it appears to be; a kernel fork that loads 64-bit MDT files
landed on 2026-11-03). Sizes for this build: FD719D50....b01 56,507 B;
05B04A44....b01 48,626 B (+ .b02 257 B).

Census write-up:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/trustzone-census.md
```

Post on #42 (32552B22-89FE-42B4-8A45-A0C4E2DB0326):

```markdown
Census result for this TA in the FP6 image (LineageOS 23.2 nightly
2026-11-09): an honest negative — no strings of ≥8 characters anywhere
in the payload, so the census cannot name it. It is a .mdt + .bXX
QSEE TA split inside modem/image (b01 = 31,357 B for this build), same
packaging as the identified secure-element TAs (#43/#41). If it has
identifiable functionality, it will need disassembly rather than
string evidence.

Size/hash rows for every FP6 blob (including this one):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/results/census.md
```

### C-3 — issue #33 ("Identify what these shared libraries do")

```markdown
Partial identifications from the FP6 census (LineageOS 23.2 nightly
2026-11-09); the rest are honestly unidentified. None of these are
QCA test-API libraries — the identified ones are QSEE trusted-app TAs
(.mdt+.bXX splits in modem/image), except where noted:

- soter64 — SOTER device-attestation TA (construct_soter_sign_data,
  /persist/data/soter/, SOTER_CE)
- smplap64 — Qualcomm's "sample app" crypto/test TA
  (tz_app_crypto_aes_*, qsee_malloc) — a development sample shipping
  in a production device, 1,653,528 B payload
- featenabler — per-SoC feature licensing (soc_hw_version,
  FeatureEnabler_*, RPMB-backed); interestingly ships twice: as its
  own featenabler partition (merged ELF) and as a .mdt+.bXX split in
  modem/image — byte-identical spot checks
- 05B04A44-... and FD719D50-... — secure-element service TAs
  (CESEService_*, GPQESE_Open/Transceive — GlobalPlatform SE API)
- 32552B22-... — no strings ≥8 chars; unidentified (honest negative)
- evautil64, focal64, ic5, loadalgota64, ops, sp_license, winsecap —
  size/hash rows only so far, function not identified
- hdcp1/hdcp2p2/hdcpsrm — HDCP content protection family (AArch64);
  excluded from deeper analysis as DRM

So the guess "used for testing" holds only for smplap64; the rest are
production TAs. Size/hash rows for all 16:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/results/census.md
TrustZone census:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/trustzone-census.md
```

---

## Source map (what each item draws on)

| Item | Lab sources |
|---|---|
| PR-5 | `qualcomm-fp6/docs/fp6-architecture-census.md` (F-6), `results/census.md` rows |
| PR-6 | F-5/F-7/F-8/F-20/F-22 (`fp6-architecture-census.md`, `wpss-qurt-rtos.md`, `wmi-dispatcher-b09-b10-b12.md`), PR-1/PR-2 texts |
| C-1 | F-8 + `qualcomm-fp6/docs/wpss.b07.strings.txt` (committed string census) |
| C-2 | `qualcomm-fp6/docs/trustzone-census.md` + `results/census.md` rows |
| C-3 | `qualcomm-fp6/docs/trustzone-census.md` + `results/census.md` rows |
