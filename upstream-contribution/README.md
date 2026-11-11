# Upstream contribution package — codeberg.org/rsavoye/librephone

Everything needed to file the documentation PRs against Rob Savoye's
LibrePhone repo the moment a Codeberg login is available. All facts trace
to committed findings in this repo (`papers/wmi-dispatch-architecture.md`,
`qualcomm-fp6/docs/*`) and to `adineo-cmd/open-discovery-lab` (commit map
in the paper's Appendix A).

- Upstream repo: https://codeberg.org/rsavoye/librephone (Gitea/Forgejo),
  docs under `docs/` (`index.md`, `wireless.md`, `wpss.bXX.md` per-segment
  notes, `files.md`, `track.md`, `comparing.md`).
- Companion checklist: [filing-checklist.md](filing-checklist.md) — branch
  names, commit titles, submission order, prerequisites.
- Supersedes `qualcomm-fp6/upstream-pr-draft.md` (whose claims remain
  valid; it now carries a status banner pointing here).

## Before filing

1. **Codeberg login is a hard prerequisite** — the lab holds no Codeberg
   credentials; these PRs are filed manually from a logged-in browser.
2. **Reconcile against the live docs at filing time.** Upstream's current
   docs were fetched 2026-11-12 for this package (quotes below are from
   that fetch): `wireless.md` (AVR/RISCV32 guess + WPSS blob list),
   `wpss.b06.md` ("mostly a collection of error messages", "single data
   file"), `wpss.b07.md` (RISCV32 per tools, objdump "garbage" blocks),
   `wpss.b08.md` (x86 ELF header, `padded_pcss_m3_tx_rx_bin` symbols,
   CE shared-buffer reading), `wpss.b09.md` ("data file", *file* says PSX
   image), `wpss.b10.md` ("basically just an array of strings"),
   `wpss.b12.md` (thorough X.509 chain doc, CC-BY-SA-4.0, Gustavo
   Paredes), `files.md` (bluetooth.img section lists msbtfw11/12 + evr
   sets; wpss files only via a pattern line). If a target file moved,
   re-diff before applying the patch text.
3. **Tone.** Upstream docs are short, first-person field notes. The texts
   below are terse and factual (no "we", no narrative, no marketing) and
   cite only verified numbers; where upstream's original wording is kept,
   it is quoted and extended rather than contradicted.

## Rule-1 standardization applied in this package

- **b06 range end.** Canonical form: base `0xc0002000` + filesz
  6,074,641 B (`0x5CB111`) = **end-exclusive `0xc05bd111`**; the Ghidra
  flat-block end `0xc05cd110` is the *inclusive last-byte* address and is
  consistent with filesz (not an error). The transcription variants
  `0xc05cb111` and `0xc05bdb31` appear only in open-discovery-lab finding
  docs (`wmi-dispatcher-b09-b10-b12.md`, `wmi-registry-consumers.md`,
  `hexagon-decode.md`) — a different repo, outside this package's write
  scope; flagged for the owner to patch there. All upstream-facing text
  below uses the canonical value (recorded in the paper, Appendix B
  item 2).
- **`qualcomm-fp6/docs/wmi-xref.md`** carried the falsified
  "constructed at runtime" conclusion without the correction banner that
  the open-discovery-lab copy has; fixed in this repo (separate commit,
  2026-11-12).
- **`qualcomm-fp6/upstream-pr-draft.md`** updated with the supersede
  banner and the research-note pointer (separate commit, 2026-11-12).

---

## PR-1 — docs/wireless.md: the AVR→RISC-V correction

- **Target file:** `docs/wireless.md` (replace the "Wireless Chipset"
  guess sentence; keep the rest of the page).
- **Branch:** `docs/wpss-riscv-architecture`
- **Commit title:** `Fix wireless.md processor description`
- **PR title:** `docs/wireless.md: replace the AVR guess with the verified RISC-V identification`

Current upstream text being replaced (verified 2026-11-12):

> This chip appears to have an embedded 8 bit ATMel AVR core, and
> possibly a RISCV32 core as well.

**PR description (paste-ready):**

```
The "Wireless Chipset" section currently says the wcn6750 chip "appears
to have an embedded 8 bit ATMel AVR core, and possibly a RISCV32 core as
well". The AVR part can be replaced with verified facts.

From the ELF headers and entry-code disassembly of the wpss firmware in
the public LineageOS FP6 nightly (lineage-23.2-20261109):

- wpss.b07 is a complete ELF32 executable, e_machine = 243 (EM_RISCV),
  entry 0x404000. The entry code disassembles (capstone, RV32+RVC) as
  machine-mode startup: an MIE mask built with c.lui/addi, `csrs
  mstatus`, `csrci mstatus`, then `csrw mtvec`. That is RISC-V interrupt
  setup, not a header coincidence.
- The firmware runs Qualcomm's QURT RTOS on that core: QURTK_thread_stop
  / UTCB / TCB strings, and an exception path naming the RISC-V `mcause`
  CSR.
- A build artifact names the core directly: `dog_hal_moselle_riscv.c`
  (watchdog HAL; "Moselle" is the WCN6750 firmware codename).
- Firmware version: WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1; the ucode segment
  wpss.b08 (vaddr 0x4ff00000) carries WLAN_UCODE_MOSELLE_4.2.0-00000.

One caveat worth recording while touching this page: the per-segment
.bXX ELF headers carry junk e_machine values (zeros, even x86=3 on
wpss.b08, which is a data segment) — architecture identification should
use the .mdt program headers plus entry-point sanity, not the segment
files' own headers.

Related (same census): the camera ICP and VPU firmware on this SoC are
also RISC-V (ELF32 with the historic e_machine=94 value). The WMI
dispatch architecture of this firmware is documented in a follow-up PR
(docs/wmi-dispatch.md): the event-routing code turns out to be Hexagon
in wpss.b06, while the RISC-V core runs the QURT application firmware.

Census write-up with the full evidence chain:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
```

**Doc change (paste-ready replacement paragraph for the "Wireless
Chipset" guess):**

```
The wireless processor subsystem (wpss) firmware runs on a 32-bit RISC-V
core. Verified from the ELF headers of the LineageOS FP6 image
(2026-11-09 nightly): `wpss.b07` is ELF32 with `e_machine=243
(EM_RISCV)`, entry `0x404000`, and its entry code disassembles as RV32
machine-mode startup (`csrs mstatus` / `csrw mtvec` sequences). The
firmware runs Qualcomm's QURT RTOS (`QURTK_*` strings, `mcause` in the
exception path), and a build artifact names the core directly
(`dog_hal_moselle_riscv.c`). The firmware version string is
`WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1`; the ucode segment (`wpss.b08`,
vaddr `0x4ff00000`) carries `WLAN_UCODE_MOSELLE_4.2.0-00000` ("Moselle"
is the WCN6750 firmware codename).

Note: per-segment `.bXX` ELF headers carry junk `e_machine` values
(zeros, and even x86=3 on `wpss.b08`, which is a data segment) —
architecture identification should use the `.mdt` program headers +
entry-point sanity, not the segment headers. See `docs/wmi-dispatch.md`
for the decoded WMI dispatch architecture (the event-routing code is
Hexagon in `wpss.b06`).

Census write-up with the full evidence chain:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
```

---

## PR-2 — new docs/wmi-dispatch.md: the registry + dispatcher architecture

- **Target file:** `docs/wmi-dispatch.md` (new)
- **Branch:** `docs/wmi-dispatch`
- **Commit title:** `Add docs/wmi-dispatch.md`
- **PR title:** `add docs/wmi-dispatch.md: the wpss WMI dispatch architecture (registry + Hexagon dispatchers), decoded`

**PR description (paste-ready):**

```
New doc: docs/wmi-dispatch.md, documenting how the wpss firmware
(WCN6750, Fairphone FP6) dispatches WMI traffic. Key facts, all from
static analysis of the public LineageOS FP6 nightly (2026-11-09):

- WMI dispatch is two-level and table-driven. wpss.b09 holds the
  message-ID registry: [handler pointer, grp<<12|cmdID, 0] records,
  12-byte stride, 225 records in 16 anchored runs, 149 distinct IDs
  across WMI groups 3..13; main run at vaddr 0xc0691080-0xc06913b0. The
  handler pointers route each group to a dispatcher in wpss.b06 (PDEV 48
  records -> 0xc02cd9cc, VDEV 41 -> 0xc031d8c8, PEER 23 -> 0xc02d94bc,
  ROAM 24 -> 0xc035d2e0).
- wpss.b06 is executable Hexagon code (wpss.mdt declares e_machine=164,
  EM_HEXAGON; base 0xc0002000, size 6,074,641 B, end-exclusive
  0xc05bd111). It disassembles cleanly with Ghidra 12.2's
  Hexagon:LE:32:default module. This corrects the "unknown architecture"
  reading of b06 in the per-segment docs.
- The PDEV dispatcher (0xc02cd9cc, 9,828 B) decodes to complete coverage
  (2,457 packets): bitsplit R5R4,R1,#0x8 (R5 = group, R4 = command), a
  cmp tree, and computed jump tables at 0xc056423c (85 words, PDEV) and
  0xc05641fc (16 words, STATS). 61 events map to verified handler
  blocks; the registry head block (0xc0691050/0xc0691068) is
  materialized and armed by the dispatcher with setbit() enable masks.
- The dispatcher never reads the registry records (zero operand
  references to the 28 run-start addresses over 357,390 decoded
  instructions); event routing keys off the b06-resident tables. 49/58
  IDs shared between registry and decoded tree land on non-exit
  handlers.

This supersedes, at decode level, the "data file / PSX image" and
"mostly error messages" readings of b09/b06 in the per-segment docs (a
follow-up PR touches those). wpss.b10 turns out to be the firmware
trace-string table (66 of 11,244 file.c: strings name WMI IDs).

Full write-up (method, tools, complete decoded map, falsification
chain):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

**Doc content (paste-ready, the whole new file):**

```markdown
# WMI dispatch in the wpss firmware

This documents how the wpss firmware (WCN6750, Fairphone FP6, LineageOS
23.2 nightly 2026-11-09, build `WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1`)
dispatches WMI commands and events. Everything below is from static
analysis of the public images; no blob content is redistributed.

WMI IDs are `grp<<12|cmd` (same ID space as ath11k's `wmi.h`). The
firmware stores no WMI IDs as instruction immediates and builds none
arithmetically — dispatch is two-level and table-driven: a group
registry in the data segment wpss.b09, and per-group dispatcher
functions in the Hexagon code segment wpss.b06.

## Level 1: the group registry (wpss.b09)

- Record format `[handler pointer, grp<<12|cmdID, 0]`, 12-byte stride.
  225 records in 16 anchored, count-prefixed runs (an independent
  recount with a looser filter gives 193 records / 32 distinct pointers
  and agrees on the main run). 149 distinct IDs across WMI groups
  3..13.
- Main run at vaddr `0xc0691080`-`0xc06913b0` (file offset `0x2a080`);
  the segment maps at `0xc0667000`+; 360,960 bytes are file-backed of
  14,835,712 bytes of memsz.
- Each run is anchored: 8-12 bytes before the records sits the run's own
  address (e.g. `b09[0xc0691078] = 0xc0691080`) plus record counts and
  sentinels. Two anchored runs sit outside the main window
  (`0xc0684da0`, `0xc069dfc8`).
- The handler-pointer column routes a WMI group to its dispatcher in
  wpss.b06. The four largest clusters: PDEV 48 records -> `0xc02cd9cc`,
  VDEV 41 -> `0xc031d8c8`, PEER 23 -> `0xc02d94bc`, ROAM 24 ->
  `0xc035d2e0`.
- A head block at `0xc0691050`/`0xc0691068` is materialized and armed by
  the dispatcher at init (see Level 2): it holds the main-run anchor
  (`b09[0xc0691078]`), a pointer into the records
  (`b09[0xc0691060] = 0xc06913c0`), and three enable-mask words written
  with `setbit()` stores (`+0xd8`, `+0x104`, `+0x118` ->
  `0xc0691140`/`0xc069116c`/`0xc0691180`). The registry head is an
  event-enable-mask/list-head object; the decoded dispatcher never reads
  the records (a program-wide scan over 357,390 decoded instructions
  finds 1,850 b09 operand references and zero on the 28 registry
  run-start addresses).
- Also in wpss.b09: the firmware-internal enum-name table (148 `WHAL_*`
  / `WAL_*` strings — the same ID space as ath11k, different enum
  names) and the `.eh_frame` unwind data for wpss.b06's functions
  (1,072 bytes, 9 CIEs / 28 FDEs).

## Level 2: the Hexagon dispatchers (wpss.b06)

The handlers are Hexagon (QDSP6) code. The `wpss.mdt` declares
`e_machine = 164 (EM_HEXAGON)`; wpss.b06 is the executable code segment
at base `0xc0002000`, 6,074,641 bytes (end-exclusive `0xc05bd111`). It
disassembles cleanly with Ghidra 12.2 (`Hexagon:LE:32:default` processor
module, raw import at the base address). 28 of 28 eh_frame function
starts and 21 of 22 sampled registry handler pointers decode as real
functions.

The PDEV-family dispatcher at `0xc02cd9cc` (9,828 bytes) is decoded to
complete coverage (2,457 packets):

- Entry packet `bitsplit R5R4,R1,#0x8` -> R5 = ID>>8 (group),
  R4 = ID&0xff (command).
- A cmp/jump tree on R5 selects the family: `0x40` PDEV, `0x50` VDEV,
  `0x110` SUSPEND, `0x160` STATS, `0x1d0` MISC, `0x1e0` GPIO (values as
  seen in R5; names per ath11k's `enum wmi_cmd_group` — note 0x16 is
  STATS, not PROFILE).
- PDEV events index an 85-word jump table at `0xc056423c`:
  `memw R2,(R2<<#0x2+##0xc056423c); jumpr R2`, index = (ID&0xff)-1, with
  a `cmp.gtu idx,#0x54` bounds check.
- STATS uses a 16-word table at `0xc05641fc`; MISC/GPIO/SUSPEND are cmp
  trees; one VDEV event (0x5022, firmware-specific) is a byte compare.
  Unhandled IDs fall to a shared exit `0xc02cedcc` -> `0xc04e61a8`.
- 61 events map to verified handler blocks (41 PDEV, 9 STATS, 6 MISC,
  2 GPIO, 2 SUSPEND, 1 VDEV); every jump-table target was verified to
  hold decoded Hexagon instructions.
- Cross-check between the two independent structures (registry records
  vs decoded tree): 49 of 58 shared IDs land on non-exit handler blocks
  (40/48 PDEV, 9/10 STATS).
- The registry tie-in: the dispatcher materializes the head block by
  absolute address (`assign R0,##0xc0691050` @`0xc02cfb8c`; `assign
  R0,##0xc0691068` @`0xc02cfba0`) and writes the enable masks into it;
  the SUSPEND path loads a runtime-initialized b09 pointer variable
  (`memw.if(P0) R2,(##0xc06bde64)` @`0xc02cda20`).

Excerpt of the decoded PDEV map (ath11k names for 0x4001-0x4022; 0x4023+
are firmware-specific IDs unnamed in ath11k):

| ID | ath11k name | handler block |
|---|---|---|
| 0x4001 | WMI_PDEV_TPC_CONFIG_EVENTID | 0xc02cdbc8 |
| 0x4002 | WMI_CHAN_INFO_EVENTID | 0xc02ce968 |
| 0x4003 | WMI_PHYERR_EVENTID | 0xc02cea10 |
| 0x4006 | WMI_DFS_RADAR_EVENTID | 0xc02ce7c8 |
| 0x4009 | WMI_SERVICE_READY_EXT_EVENTID | 0xc02ce88c |
| 0x400a | WMI_PDEV_FIPS_EVENTID | 0xc02ce71c |
| 0x400b | WMI_PDEV_CHANNEL_HOPPING_EVENTID | 0xc02ce7b8 |
| 0x400c | WMI_PDEV_ANI_CCK_LEVEL_EVENTID | 0xc02ceac8 |
| 0x400d | WMI_PDEV_ANI_OFDM_LEVEL_EVENTID | 0xc02ce688 |
| 0x4010 | WMI_PDEV_SET_HW_MODE_RESP_EVENTID | 0xc02ce60c |
| 0x4015 | WMI_PDEV_CHIP_POWER_SAVE_FAILURE_DETECTED_EVENTID | 0xc02ce654 |
| 0x4016 | WMI_PDEV_CSA_SWITCH_COUNT_STATUS_EVENTID | 0xc02ce9f8 |
| 0x4017 | WMI_PDEV_CHECK_CAL_VERSION_EVENTID | 0xc02ce8e8 |
| 0x4018 | WMI_PDEV_DIV_RSSI_ANTID_EVENTID | 0xc02cea9c |
| 0x4019 | WMI_PDEV_BSS_CHAN_INFO_EVENTID | 0xc02ceaa4 |
| 0x401a | WMI_PDEV_UPDATE_CTLTABLE_EVENTID | 0xc02ceab0 |
| 0x401b | WMI_PDEV_DMA_RING_CFG_RSP_EVENTID | 0xc02ceb14 |
| 0x401d | WMI_PDEV_CTL_FAILSAFE_CHECK_EVENTID | 0xc02ceae0 |
| 0x401e | WMI_PDEV_CSC_SWITCH_COUNT_STATUS_EVENTID | 0xc02ce5f8 |
| 0x401f | WMI_PDEV_COLD_BOOT_CAL_DATA_EVENTID | 0xc02ce8f4 |
| 0x4020 | WMI_PDEV_RAP_INFO_EVENTID | 0xc02cebb8 |
| 0x404d / 0x404e | (fw-specific) | 0xc02ce5e0 / 0xc02ce590 |

STATS (table `0xc05641fc`): 0x16001 WMI_STATS_EXT_EVENTID -> 0xc02cdc6c,
0x16004 WMI_RADIO_LINK_STATS_EVENTID -> 0xc02ce0a0, 0x16005
WMI_UPDATE_FW_MEM_DUMP_EVENTID -> 0xc02ce058, 0x16006
WMI_DIAG_EVENT_LOG_SUPPORTED_EVENTID -> 0xc02ce198, 0x16008
WMI_RADIO_TX_POWER_LEVEL_STATS_EVENTID -> 0xc02ce1d4, 0x1600c
WMI_RADIO_CHAN_STATS_EVENTID -> 0xc02ce084, plus firmware-specific
0x1600e/0x1600f/0x16010.

MISC cmp tree: 0x1d00b WMI_VDEV_GET_KEEPALIVE_EVENTID, 0x1d010
WMI_UPDATE_VDEV_RATE_STATS_EVENTID, 0x1d014 WMI_RSSI_BREACH_EVENTID,
0x1d019 WMI_PKGID_EVENTID (+ firmware-specific 0x1d01a, 0x1d01d).
GPIO: 0x1e001 WMI_GPIO_INPUT_EVENTID, 0x1e002 WMI_UPLOADH_EVENTID.
SUSPEND: 0x11001 WMI_PDEV_RESUME_EVENTID (+ firmware-specific 0x11002).

Open items, stated plainly:

- 8 registry PDEV IDs fall to the shared exit in this dispatcher
  (0x4004, 0x4005, 0x4007, 0x4008, 0x4014, 0x4036, 0x403a, 0x404c) —
  handled elsewhere, accepted-and-dropped, or vestigial; unresolved.
  One handled ID (0x404e) has no registry record.
- The other group dispatchers (VDEV `0xc031d8c8`, PEER `0xc02d94bc`,
  ROAM `0xc035d2e0`) are decode-verified functions with the same
  expected pattern, not yet decoded.
- The call site that enters `0xc02cd9cc` with R1 = ID is not yet
  located; handler block bodies are mapped, not individually
  reverse-engineered.

Related segments: wpss.b10 is the firmware's trace/error-string table
(11,244 `file.c:` strings, 66 naming WMI IDs, e.g.
`wlan_dev.c:WMI_PDEV_CONFIG_VENDOR_OUI_ACTION_CMDID Error: ...`) — the
`file.c` names are the firmware's internal module inventory. wpss.b12 is
the X.509 secure-boot chain (own doc).

Method: raw-import disassembly seeded from registry pointers and
eh_frame FDE starts (auto-analysis is not relied on); jump tables read
from the raw file with every target verified to decode; negative control
`0xc04ecc3d` (a misaligned registry pointer) decodes to nothing, as
alignment predicts.

Full write-up with the complete falsification chain, tools and result
JSONs:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

---

## PR-3 — per-segment doc updates (wpss.b06/b07/b08/b09/b10/b12)

- **Target files:** `docs/wpss.b06.md`, `docs/wpss.b07.md`,
  `docs/wpss.b08.md`, `docs/wpss.b09.md`, `docs/wpss.b10.md`,
  `docs/wpss.b12.md`
- **Branch:** `docs/wpss-segments`
- **Commit title:** `Correct the per-segment wpss docs`
- **PR title:** `correct the per-segment wpss docs (b06/b07/b08/b09/b10; b12 cross-check)`
- **Order note:** file **after PR-2** — the new b06/b09 text links to
  `docs/wmi-dispatch.md`.
- **b12 caveat:** upstream's `wpss.b12.md` is a contributed CC-BY-SA-4.0
  doc (Gustavo Paredes) — only append the cross-check, do not rewrite.

**PR description (paste-ready):**

```
Corrections and additions to six per-segment wpss docs, from static
analysis of the LineageOS FP6 nightly (2026-11-09). Each change keeps
the original observations and adds verified facts:

- wpss.b06.md — rewritten: b06 is executable Hexagon (QDSP6) code (mdt:
  e_machine=164 EM_HEXAGON; base 0xc0002000, 6,074,641 B, end-exclusive
  0xc05bd111), not a data file. The error-message strings seen in hex
  dumps are embedded format/assert strings in the code segment. b06
  holds the WMI event dispatchers; see docs/wmi-dispatch.md.
- wpss.b07.md — update appended: RV32 confirmed at instruction level
  (entry 0x404000 = machine-mode startup), QURT RTOS strings, the
  objdump "garbage" blocks identified as padding/data between real
  functions (linear sweep of the pure-code LOADs: 100% coverage, 24,030
  instructions), and the mdt-phdr fact that b07 is carried as a data
  payload (embedded ELF) — matching the "Current Research" note about
  embedded ELFs in this image.
- wpss.b08.md — update appended: the x86 header is junk (data segment
  per the mdt phdrs; e_machine=3 with entry 0x401); Moselle ucode and
  QURT IPC buffer error strings documented; a caveat on the
  value-presence reading of the WLAN-profile IDs (negative controls
  reproduce them in unrelated firmware).
- wpss.b09.md — rewritten: b09 is the WMI message-ID registry (record
  format, anchors, per-group pointer clustering, enum-name strings,
  .eh_frame for b06) — not a PSX image; the disassembler noise is what a
  data table looks like decoded as code.
- wpss.b10.md — update appended: 11,244 file.c: strings, 66 naming WMI
  IDs; the file.c names are the firmware's internal module inventory.
- wpss.b12.md — small cross-check appended (an independent census agrees
  with the existing chain doc; b12 is PT_NULL, pure certificate data).
  Attribution/license untouched.

No blob content is redistributed; all numbers are derived metadata.
Full write-up:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

**Doc content (paste-ready, per file):**

`docs/wpss.b06.md` — replace the body with:

```markdown
# wpss.b06

wpss.b06 is executable Hexagon (QDSP6) code — not a data file. The
wpss.mdt program headers mark b01/b02/b03/b05/b06 executable, and the
mdt declares `e_machine = 164 (EM_HEXAGON)`. The segment loads at base
`0xc0002000`, 6,074,641 bytes (end-exclusive `0xc05bd111`).

The hex-dump impression ("mostly a collection of error messages", plus
filenames that aren't in the kernel) is the string data embedded in the
code segment: format strings, assert text, and build paths. The code
decodes cleanly with Ghidra 12.2's `Hexagon:LE:32:default` processor
module (raw import at base `0xc0002000`); the `.eh_frame` unwind data
for its functions lives in wpss.b09 (28 FDEs, all of which decode as
real functions when seeded).

b06 is the consumer of the WMI message-ID registry in wpss.b09: it holds
the per-group WMI event dispatchers. The PDEV-family dispatcher at
`0xc02cd9cc` (9,828 bytes) is decoded end to end — see
`docs/wmi-dispatch.md` for the dispatch tables (jump tables at
`0xc056423c` and `0xc05641fc`), the registry tie-in, and the decoded
event-to-handler map.

Full write-up:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

`docs/wpss.b07.md` — append:

```markdown
## Update (2026-11)

The RISC-V identification is confirmed beyond the tool disagreement:

- wpss.b07 is a complete ELF32 executable, `e_machine = 243 (EM_RISCV)`,
  entry `0x404000`. The entry code disassembles (capstone, RV32+RVC) as
  machine-mode startup: build an MIE mask, `csrs mstatus`, `csrci
  mstatus`, then `csrw mtvec`. Annotated first-250-instruction listing:
  https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/wpss-b07-disasm-head.md
- The "total garbage" blocks in the objdump output are the zero-filled
  padding and data regions between real functions — a full linear sweep
  of the pure-code LOADs decodes at 100% coverage (24,030 instructions),
  so the code itself is clean RV32+C; the padding and data are what
  objdump mangles.
- The core runs Qualcomm's QURT RTOS: `QURTK_thread_stop`, UTCB/TCB
  strings, and an exception path naming the RISC-V `mcause` CSR. A build
  artifact names the core directly: `dog_hal_moselle_riscv.c`.
- Per the wpss.mdt program headers, b07's segment is carried as RW data
  by the Hexagon loader (only b01/b02/b03/b05/b06 are executable in the
  mdt) — consistent with the "Current Research" note that the image is
  one MDT/DSP6 file with embedded ELFs of other architectures: b07 is a
  self-contained RV32 image handed to the RISC-V core, and its own ELF
  headers are the trustworthy ones for identifying it.
```

`docs/wpss.b08.md` — append:

```markdown
## Update (2026-11)

The x86 ELF header is junk: `e_machine = 3 (EM_386)` with entry `0x401`
on a data segment. The wpss.mdt program headers mark b07/b08 as RW data
(only b01/b02/b03/b05/b06 are executable), so the segment files'
header fields should not be trusted for architecture identification.

Content facts:

- vaddr `0x4ff00000`, 275,644 bytes, single RWX LOAD in the segment's
  own ELF; carries `WLAN_UCODE_MOSELLE_4.2.0-00000` ("Moselle" = WCN6750
  firmware codename) next to the main firmware version string in b07
  (`WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1`).
- The `padded_pcss_m3_tx_rx_bin` symbols (start/end/size markers around
  a zero-filled region) fit the CE shared-memory channel reading: an
  initially-empty buffer populated at runtime. QURT IPC error strings
  (`ERR_ZERO_IPC_BUFFER`, `ERR_append_ipc_buf_in_flight`,
  `SYS:IPC loc-1/loc-2`) support the transport-buffer role.
- ath11k's WLAN-profile command IDs 0x10001-0x10005 do appear in a
  structured config region — but control scans on unrelated firmware
  reproduce most of these values at similar rates, so value-presence
  alone is not evidence of WMI handling. The firmware's WMI surface is
  table-driven; see `docs/wmi-dispatch.md`.
```

`docs/wpss.b09.md` — replace the body with:

```markdown
# wpss.b09

wpss.b09 is a data segment, and the PSX hit from *file* is wrong — it is
the firmware's WMI message-ID registry, plus support data:

- Record format `[handler pointer, grp<<12|cmdID, 0]`, 12-byte stride;
  225 records in 16 anchored, count-prefixed runs (193 in an independent
  recount with a looser filter), 149 distinct IDs across WMI groups
  3..13. Main run at vaddr `0xc0691080`-`0xc06913b0` (file offset
  `0x2a080`); the segment maps at `0xc0667000`+; 360,960 bytes are
  file-backed of 14,835,712 bytes of memsz.
- The handler-pointer column routes a WMI group to its dispatcher in
  wpss.b06 (32 distinct pointers): PDEV 48 records -> `0xc02cd9cc`,
  VDEV 41 -> `0xc031d8c8`, PEER 23 -> `0xc02d94bc`, ROAM 24 ->
  `0xc035d2e0`.
- A head block at `0xc0691050`/`0xc0691068` is materialized and armed by
  the dispatcher at init (enable-mask stores at `+0xd8`/`+0x104`/
  `+0x118`); each run is anchored by its own address 8-12 bytes before
  the records (e.g. `b09[0xc0691078] = 0xc0691080`).
- Also in b09: 148 firmware-internal enum-name strings (`WHAL_*` /
  `WAL_*` — same ID space as ath11k, different enum names) and the
  `.eh_frame` unwind data for wpss.b06's functions (9 CIEs / 28 FDEs).

The disassembler noise ("stores the value of a register into the same
register repeatedly") is what a data table looks like when decoded as
code. See `docs/wmi-dispatch.md` for the full dispatch architecture and
the decoded event map.

Full write-up:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

`docs/wpss.b10.md` — append:

```markdown
## Update (2026-11)

The string table is the firmware's trace/error-message array, and it is
large and structured: 95.5% ASCII, 11,244 `file.c:`-style strings, of
which 66 name WMI message IDs in error text (e.g.
`wlan_dev.c:WMI_PDEV_CONFIG_VENDOR_OUI_ACTION_CMDID Error: ...`). The
`file.c` names are the firmware's internal source modules — useful as a
module inventory when mapping handlers (the WMI dispatch handlers live
in wpss.b06; see `docs/wmi-dispatch.md`).
```

`docs/wpss.b12.md` — append (leave attribution/license untouched):

```markdown
## Cross-check (2026-11)

An independent census of the same LineageOS FP6 nightly agrees with the
chain documented above: production root "Generated OEM Root CA" (OU
"Fairphone BV, T2MO OEM Key", Amsterdam), validity 2025-03-05 ->
2045-02-28, via the "Generated OEM Attestation CA" intermediate. b12 is
a PT_NULL segment (no LOAD, no code) — pure certificate data. The same
OEM chain signs the FP6 boot chain (xbl/uefi/abl and others).
```

---

## PR-4 (optional) — docs/files.md: BT partition + boot-chain pointers

- **Target file:** `docs/files.md` (append to the `bluetooth.img`
  section; add a boot-chain block under `## Top Level`)
- **Branch:** `docs/files-bt-bootchain`
- **Commit title:** `Document the bluetooth partition and boot-chain images`
- **PR title:** `docs/files.md: bluetooth partition firmware and boot-chain image facts`

**PR description (paste-ready):**

```
Two additions to docs/files.md, from censuses of the same LineageOS FP6
nightly (2026-11-09):

- bluetooth.img section: the FAT16 partition holds two Moselle (WCN6750)
  BT firmware generations plus a third "EVROS" family (TLV product_id
  29) that mainline btqca.c cannot name or select (no "evr" string
  anywhere in btqca.c/hci_qca.c; the consumer is Qualcomm's Android
  vendor BT HAL). The .mbn rampatches are ELF32 ARM (Thumb entry), and
  the kernel's own rom_ver math reproduces all three filenames from the
  shipped headers (rom_build 0x0101 -> msbtfw11, 0x0102 -> msbtfw12,
  0x0200 -> evrbtfw20). linux-firmware ships msbtfw11 at different
  sizes (different builds) and has no msbtfw12, no evr* files.
- boot-chain section: xbl.img is a multi-ELF container (matching the
  stock name xbl_s.melf); shrm/aop/aop_config/cpucp are ELF32 RISC-V
  (e_machine=243, RVC flag) — first public ISA identification for these
  images; qupfw claims EM_QDSP6 (Hexagon). One signed build generation
  (BOOT.MXF.2.1-02027-LANAI-1) down to Fairphone's own OEM attestation
  key ("T2MO OEM Key", Amsterdam).

Census write-ups (facts only, no blob content):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bt-firmware-census.md
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
```

**Doc content (paste-ready):**

Under `### bluetooth.img`, after the existing file lines, append:

```markdown
- FAT16 filesystem, 864,256 bytes, 11 files under image/.
- msbtfw11.*: ELF32 ARM rampatch (e_machine=40, entry = LOAD vaddr | 1 =
  Thumb), Moselle 1.1 (BTFW.MOSELLE.1.1.2-00064-PATCHZ-2); msnv11.bin:
  NVM TLV config, 66 tags — tag 1 is the firmware version string, tag 2
  is the BD address slot (6 bytes, written by the vendor HAL before
  download).
- msbtfw12.*: same format, Moselle 1.2
  (BTFW.MOSELLE.1.2.0-00380-PATCHZ-1). Not present in linux-firmware.
- evrbtfw20.tlv/.ver/evrnv20.bin: a third rampatch family, "EVROS"
  (BTFW.EVROS.2.0.0-00143-PATCHZ-5_DEF), TLV product_id 29 (Moselle is
  21). No "evr" string exists anywhere in mainline btqca.c/hci_qca.c;
  the consumer is Qualcomm's Android vendor BT HAL. EVROS entry
  0x20027fc8 sits in the Cortex-M SRAM window — a different load layout
  than Moselle's. Device ver_info dumps pair EVROS with its own WLAN
  image family (WLAN.EVR.1.0-01270-QCAEVRSWPLZ-1).
- The kernel's rom_ver math (btqca.c) reproduces all three filenames
  from the shipped headers: rom_build 0x0101 -> msbtfw11, 0x0102 ->
  msbtfw12, 0x0200 -> evrbtfw20.
- linux-firmware ships msbtfw11.mbn/.tlv + msnv11.bin at different sizes
  (different builds) and no msbtfw12, no evr* files.
```

Under `## Top Level`, add:

```markdown
### Boot chain partitions

- xbl.img is a multi-ELF container (xbl_s.melf): an outer junk-header
  ELF32 wrapper + an inner ELF32 RISC-V image (e_machine=243, entry
  0x20412d00) + an inner ELF64 AArch64 XBL core.
  BOOT.MXF.2.1-02027-LANAI-1 in xbl/uefi/xbl_ramdump.
- shrm, aop, aop_config, cpucp: ELF32 e_machine=243 (EM_RISCV), RVC ABI
  flag. shrm's entry decodes as RV32 machine-mode startup (auipc/addi gp
  setup + `csrw mtvec`) and carries "DDR_FW version : 19.12.0"; cpucp's
  role strings (SCMI/RPMH/CPRh/Memlat) match the mainline
  qcom-cpucp-mbox driver. First public ISA identification for these
  images; qupfw is the only remaining Hexagon claim (EM_QDSP6=164,
  header-level).
- The family is signed with the Qualcomm SRoT MBNv7 chain down to
  Fairphone's own OEM attestation key ("T2MO OEM Key", Amsterdam,
  validity 2025-03-05 -> 2045-02-28). LineageOS's vbmeta sets flags=3
  (hashtree + verification disabled); vbmeta_system's rollback_index is
  the security-patch date (2026-09-05) as a Unix timestamp.
```

---

## Source map (what each PR draws on)

| PR | Lab sources |
|---|---|
| PR-1 | `qualcomm-fp6/docs/fp6-architecture-census.md`, `wpss-qurt-rtos.md`, `wpss-b07-disasm-head.md`, `qualcomm-fp6/upstream-pr-draft.md` |
| PR-2 | `papers/wmi-dispatch-architecture.md` (F-9→F-29 synthesis; results JSONs in open-discovery-lab) |
| PR-3 | same as PR-2 + `fp6-architecture-census.md`, `wpss-b07-disasm-head.md`, census notes on b10/b12 |
| PR-4 | `qualcomm-fp6/docs/bt-firmware-census.md`, `bootchain-census.md` |
