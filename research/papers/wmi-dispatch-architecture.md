# The WMI dispatch architecture of the WCN6750 wpss firmware: a two-level, table-driven dispatcher decoded from Hexagon machine code

**Research note, librephone-blob-research — 2026-11-12.**
Synthesis of Open Discovery Lab findings F-9 → F-29 (2026-11-09 to 2026-11-11); every number below traces to a committed finding document (Appendix A).

**One-line claim.** The Fairphone FP6's WCN6750 WiFi firmware dispatches WMI events through two table-driven levels — a static `[handler-pointer, grp<<12|cmdID, 0]` registry in data segment `wpss.b09` that routes WMI groups to Hexagon dispatcher functions in code segment `wpss.b06`, and b06-resident computed jump tables that route event IDs to per-event handler blocks — a structure reached only after two falsifications and one architecture correction, and described nowhere in public literature at decode level.

## Abstract

We report the first instruction-level map of how a production Qualcomm WiFi firmware (WCN6750, Fairphone FP6, LineageOS 23.2; build `WLAN.MSL.3.0.1-00591-QCAMSLSWPLZ-1`) dispatches WLAN Management Interface (WMI) traffic. The result came from a falsification chain, not a single analysis: a constant cross-reference (F-9) whose positive attribution was killed by a negative control (F-19); a runtime-construction hypothesis falsified by a 100%-coverage disassembly (F-20); the discovery that the hunted segments are data, not code (F-22); the message-ID registry in `wpss.b09` (F-22) and its consumers in `wpss.b06` (F-23) — revealing the code is Hexagon, not RISC-V as first assumed; the modem-side caveat closed (F-26); then Hexagon decode via Ghidra 12.2 headless (F-28), producing the payoff: the PDEV-family dispatcher at `0xc02cd9cc` fully decoded (2,457 packets), 61 events mapped to handler blocks via computed jump tables and cmp trees, and the registry pinned as the group-routing level whose head the dispatcher materializes and arms (F-29). Every correction stays visible: the credibility of the final map rests on the falsifications that produced it.

## 1. Background

[LibrePhone](https://www.fsf.org/news/librephone-project) (FSF, announced October 2025) aims to replace proprietary Android radio blobs with free implementations. The blob under study here is the wireless subsystem firmware of the Fairphone FP6 (QCM6490 SoC): the `wpss` image driving the WCN6750 WiFi chip, consumed by Qualcomm's fake-PCI/IPCI transport and, on the host, by the mainline `ath11k` driver.

WMI is the host↔firmware control protocol of ath11k: every command and event carries a numeric ID built as `grp<<12|cmd` (ath11k `wmi.h`, `WMI_TLV_CMD(grp) = (grp<<12)|1`). A free reimplementation cannot be written against a protocol whose firmware-side dispatch is unknown. Before this work, the public state of knowledge was the FSF LibrePhone project's per-file documentation (committed 2026-01-16, Rob Savoye): hedged tool-level identifications ("ELF32 little endian RISCV32 binary ?" for `wpss.b07`, an Intel i386 mislabel for `wpss.b08`), an AVR guess on the wireless page, `wpss.b09` unrecognized ("data file ... thinks this a Sony PlayStation PSX image"), and `wpss.b06` left "unknown architecture".

The substrate, established earlier in the lab: the wpss image is ELF32 with junk per-segment `e_machine` values (the `.mdt` header is ground truth); `wpss.b07` is RV32+C code whose entry (0x404000) is machine-mode startup (`csrs mstatus`, `csrw mtvec`) — the core is 32-bit RISC-V running Qualcomm's QURT RTOS (F-5, F-8).

## 2. Prior art (the uniqueness proof)

The lab ran an adversarial prior-art audit of findings F-1..F-26 on 2026-11-11 (commit `a8cc9d7` in adineo-cmd/open-discovery-lab; corrections applied in `a1873ba`): 18 unique-confirmed, 3 partial overlaps, 5 corrections. Relevant here:

- **FSF LibrePhone docs (2026-01-16)** — file-level, hedged identifications of the wpss segments; explicitly failed to characterize `b09` and `b06`. No WMI constant cross-reference, no dispatcher analysis. This is the baseline this note supersedes at decode level.
- **gdrci/Research (commit `58d764f`, 2026-10-08)** — raw `e_machine` header dumps for same-generation peripheral firmware (labeled EM_XTENSA); no interpretation, no dispatch analysis.
- **Hexagon tooling** — Hexagon ISA PRMs are freely available (docs.qualcomm.com, V73 Jan 2024, V75, V79); QEMU and LLVM implement Hexagon openly; IDA Hexagon modules exist. The gap is firmware-*image* internals, not the ISA.
- **Decode-level WMI dispatch analysis of this firmware: none.** GitHub code search for the registry anchor `"0xc0691080"` returns 0 hits; searches for `wpss.b07`/`wpss.b09` return only packaging/inventory; ath11k mailing list and web searches (checked 2026-11-09 through 2026-11-11) surface no binary-side WMI dispatch map. The b09 registry, the b06 consumer mapping, and the F-29 ID→block map are first.

## 3. The investigation: hypothesis → falsification → registry → decode → map

### 3.1 F-9: the first cross-reference, and an overclaim

The lab built a C-style enum evaluator for ath11k's `wmi.h` (`tools/xref_wmi.py`) — 605 IDs (398 CMDID + 207 EVENTID), verified against hand-computed ground truth — and scanned the wpss segments for aligned LE32 constants (2026-11-09). Core command families (SCAN 0x3001, PDEV 0x4xxx, VDEV 0x5xxx) were **absent as stored constants**; only the WLAN-profile family 0x10001–0x10005 appeared (1–5 hits each), which the note first read as a positive profile-handler signal and concluded "IDs are constructed at runtime (`grp<<12|1`)". Two evaluator bugs were found and documented during development (comment-swallowed first enum entry; falsy-0 group lookup; EVENTID suffix filter).

### 3.2 F-19: the negative control that corrected F-9

Redone with the control F-9 lacked: **adsp.b36** (6.4 MB, audio/sensors DSP) alongside the ten largest modem (mpss, Hexagon) segments (~110 MB of ~120 MB). Verdict: **NO** — every value family reproduces in the unrelated control at equal or higher counts (profile 0x10001–0x10005: 513/38/31/12/17 in the control; TDLS, grp-0x30, grp-0x40 likewise). Value-presence cannot attribute WMI-ness anywhere. F-9's profile-cluster attribution was corrected in place (a strict 2 KB window on wpss.b08 yields 4/5, not 5/5 — consistent with F-9's own first-hit offsets, where 0x10001 sits 0x2d9e4 away from the rest). modem.b19 proved to be the pure cellular stack (`ds_3gpp_*`, QMI ×528, HTC/HTT/ath11k/WCN markers ×0).

### 3.3 F-20: falsifying the runtime-construction mechanism

The first full linear-sweep disassembly of `wpss.b07` (RV32+C, capstone 5.0.7): the two pure-code LOADs decode at **100.0% coverage (24,030 instructions)**, with a constant-propagation self-test proving the tracker catches every searched construction form. Result: **no construction site**. Exactly five `slli ×12` sites exist, all packed-pointer indexing (`(w<<12)+base`, dereferenced), none feeding an `ori/addi 1`. No ID-shaped materialization, no ID tables at word or halfword granularity (the 16-bit scan lands at chance level and the adsp control deflates it: 202/202 candidate values in unrelated firmware). F-9/F-19's "constructed at runtime" mechanism was falsified for b07.

### 3.4 F-22: the registry (the verdict flips)

The decisive move was cheap: read the `wpss.mdt` program headers. Only b01/b02/b03/b05/b06 are executable — **b07/b08 are RW data**, so F-20's zero was structurally guaranteed and construction-site hunting was the wrong instrument. Sweeping the remaining segments found **the message-ID registry in `wpss.b09`** (RW, 360,960 B file-backed of 14,835,712 B memsz):

- 225 records of 12-byte stride `[b06-ptr, grp<<12|cmdID, 0]` in 16 runs (main run at file 0x2a080 = **vaddr 0xc0691080–0xc06913b0**), 149 distinct IDs across WMI groups 3–13;
- 148 firmware-internal enum-name strings (`WHAL_*`/`WAL_*` — the same ID space, different enums than ath11k);
- a clean 1,072-byte `.eh_frame` chain (9 CIEs, 28 FDEs) pointing into b06's executable range;
- `wpss.b10` = the trace table (95.5% ASCII, 11,244 `file.c:` strings, 66 naming WMI IDs, e.g. `wlan_dev.c:WMI_PDEV_CONFIG_VENDOR_OUI_ACTION_CMDID Error: ...`);
- `wpss.b12` = the X.509 secure-boot chain (Fairphone BV / T2MO OEM Key, Amsterdam; validity 250305→450228), PT_NULL — closed.

The structural answer: **WMI handling is table-driven** — registry in b09, handler code in b06, strings in b10; there are no arithmetic construction sites because nothing is computed.

### 3.5 F-23: consumers — and the architecture correction (b06 is Hexagon)

An independent re-derivation with a looser filter gave 193 records / 32 distinct pointers, agreeing on the main run. The load-bearing result is the per-group handler clustering: **PDEV 48 records → one pointer `0xc02cd9cc`** (51 of 193 records overall), VDEV 41 → `0xc031d8c8` (37), PEER 23 → `0xc02d94bc` (20), ROAM 24 → `0xc035d2e0` (22) — per-module shared event handlers. The registry is a set of **anchored, count-prefixed lists**: each run start is preceded 8–12 bytes earlier by its own address (e.g. `b09[0xc0691078] = 0xc0691080`), with record counts (`0x14`, `0x7`) and sentinels; two anchored runs sit outside the main window (0xc0684da0, 0xc069dfc8).

Two corrections came out of this finding. First, `wpss.mdt` declares **e_machine = 164 = EM_HEXAGON** — b06 is a Hexagon QDSP6 image segment, not RV32; the F-22 brief's RV32 assumption was wrong, confirmed diagnostically: RV32-C decodes of b06 produce coherent-looking noise *even at the 28 eh_frame-verified function starts*. Second, a consumer-constant hunt was an honest negative: no checkable instruction encoding materializes any registry address (capstone ships no Hexagon decoder — the stated cause, not proof of absence). One pointer, odd `0xc04ecc3d`, was flagged as anomalous.

### 3.6 F-26: closing the modem caveat

F-19 had left the two largest modem segments (b23/b24, 68 MB) as "packed, unverified". The unpack attempt closed it: **b24's "packed" label was wrong** (87% zero-fill; all data literal, including a 1.35 MB MCFG XML island), and b23 is 745 KB literal islands plus a 38.9 MB opaque body with **0-byte decompression yield** (zlib/gzip/bzip2/xz/lzma-alone/lz4/zstd and raw-deflate probes all fail at every candidate offset; q6z/Q6Z/ZIC markers at chance level — q6zip-like compression suspected, unconfirmed). The body's WMI-like hits are artifact-consistent with compressed tokens, not stored constants (isolation: 0 of 71 occurrences of the top hit have WMI-like neighbors; gibberish-only strings; a 16-bit value distribution characteristic of LZ-style output; duplicate-block statistics exclude encryption). **F-19's NO verdict stands.**

### 3.7 F-28: Hexagon decode unlocked

Ghidra 12.2 PUBLIC headless with the `Hexagon:LE:32:default` processor module ("Qualcomm Hexagon V69 (QDSP6), 32-bit little-endian") was installed and driven from PyGhidra (method in Section 6). wpss.b06 imports as one flat block at base 0xc0002000. Seeded disassembly at every structurally derived target:

- **21 of 22 sampled F-23 handler pointers decode as real Hexagon functions** — PDEV `0xc02cd9cc` (body 9,828 B), VDEV `0xc031d8c8` (3,864 B), ROAM `0xc035d2e0` (88 B), PEER `0xc02d94bc` (60 B), plus 17 more;
- the odd pointer `0xc04ecc3d` produces **no instruction and no function** — Hexagon packets are 4-byte-aligned; F-23's suspicion confirmed;
- **28/28 eh_frame FDE starts become functions** (bodies 4–1,032 B) — the "RV32 noise" was wrong-ISA decode, positively resolved;
- first decoded b06→b09 references via `immext` constant pairs (e.g. 0xc0146404–0xc0146468 building 0xc0682340/0xc0682348);
- the decompiler timed out on all four large handlers — decode is proven, decompilation is not.

### 3.8 F-29: the PDEV dispatcher decoded

The function at `0xc02cd9cc` (+9,828 B) was decoded to **complete coverage: 2,457 packets** (1,631 aligned gaps explicitly disassembled), its cmp/jump tree extracted (53 compares, 48 explicit jumps), its two jump tables read from raw b06 with every target verified to decode. Register semantics are pinned by the entry packet `bitsplit R5R4,R1,#0x8` → **R5 = ID>>8 (group), R4 = ID&0xff (command)**. Results:

- **61 events map to real handler blocks**: 41 PDEV (grp 4) via a b06-resident jump table at **0xc056423c** (85 words; `memw R2,(R2<<#0x2+##0xc056423c); jumpr R2`; index = (ID&0xff)-1), 9 STATS (grp 0x16) via a second table at 0xc05641fc (16 words), 6 MISC (0x1d) and 2 GPIO (0x1e) via cmp trees, 2 SUSPEND (0x11) via cmp tree, 1 VDEV (0x5022) via byte-compare. Unhandled IDs fall to a shared exit block `0xc02cedcc → jump 0xc04e61a8`.
- **The b09 registry is NOT the event jump table.** Event-level dispatch keys off b06-resident tables; a program-wide scan over **357,390 decoded instructions** found 1,850 b09 operand references (516 distinct addresses) but **zero on the 28 registry run-start addresses**.
- **The registry tie-in is real and traced (PARTIAL-YES).** The dispatcher materializes the registry **head block** by absolute address (`assign R0,##0xc0691050` @0xc02cfb8c; `assign R0,##0xc0691068` @0xc02cfba0) and writes `setbit()` enable masks into it (`memw (R0+#0xd8),setbit(#0x1)`, `+0x104`, `+0x118` → b09 0xc0691140/0xc069116c/0xc0691180) — the block containing the main-run anchor `b09[0xc0691078]=0xc0691080` and a pointer into the records (`b09[0xc0691060]=0xc06913c0`). In the SUSPEND path it loads a runtime-initialized b09 pointer variable (`memw.if(P0) R2,(##0xc06bde64)` @0xc02cda20, then field `+0x1e8`). Read: the dispatcher **initializes/arms the registry head as an event-enable-mask structure**.
- **Cross-check between two independent structures:** 49 of 58 shared IDs land on non-exit handler blocks (40/48 PDEV, 9/10 STATS ≈ 85%) — strong evidence the registry and the decoded tree describe the same live dispatch system.
- A group-label correction fell out: the 0x16xxx IDs are **WMI_GRP_STATS (0x16)**, not PROFILE; 0x1dxxx is WMI_GRP_MISC, 0x1exxx WMI_GRP_GPIO (per `enum wmi_cmd_group` in ath11k `wmi.h`). F-23's "PDEV(4)+MGMT/SUSPEND(17)" label at `0xc02cd9cc` is PDEV + SUSPEND + STATS/MISC/GPIO records at one pointer.

## 4. The final architecture

```
        host (ath11k)                                wpss firmware (WCN6750)
   WMI cmd/event, ID = grp<<12|cmd
             |
             |   (HTC/HTT frames over the IPCI/fake-PCI transport)
             v
 =====================================================================
   LEVEL 1 — GROUP ROUTING:  wpss.b09 registry  (RW data, vaddr 0xc0667000+)
 ---------------------------------------------------------------------
   head block 0xc0691050 / 0xc0691068   <-- materialized & armed by the
     [0xc0691058]=0xffff  [0xc069105c]=0x1      dispatcher (setbit masks,
     [0xc0691060]=0xc06913c0  (ptr into records) 0xc02cfb8c..0xc02cfba0)
     [0xc0691074]=0x45     [0xc0691078]=0xc0691080  (main-run anchor)
   225 x [handler-ptr, grp<<12|cmdID, 0]  (12-byte stride, anchored,
     count-prefixed runs; main run 0xc0691080+)
       PDEV(48) -> 0xc02cd9cc   VDEV -> 0xc031d8c8
       PEER -> 0xc02d94bc       ROAM -> 0xc035d2e0   ... (32 ptrs)
 ---------------------------------------------------------------------
   LEVEL 2 — EVENT ROUTING:  wpss.b06 Hexagon dispatchers (e_machine 164)
 ---------------------------------------------------------------------
   dispatcher 0xc02cd9cc  (9,828 B, 2,457 packets, complete coverage)
     bitsplit R5R4,R1,#0x8          R5 = ID>>8, R4 = ID&0xff
     cmp tree on R5:  0x40 PDEV | 0x50 VDEV | 0x110 SUSPEND
                      0x160 STATS | 0x1d0 MISC | 0x1e0 GPIO
     PDEV:  idx = (ID&0xff)-1 ; cmp.gtu idx,#0x54
            memw R2,(R2<<#0x2+##0xc056423c) ; jumpr R2     <- 85-word
                                                            jump table
     STATS: 16-word table 0xc05641fc ; MISC/GPIO/SUSPEND: cmp trees
     unhandled -> exit 0xc02cedcc -> jump 0xc04e61a8 (shared stub)
 ---------------------------------------------------------------------
             |                                   |
             v                                   v
   61 per-event handler blocks          wpss.b10 trace table
   (targets verified to decode)         (11,244 file.c: strings; 66 name
                                         WMI IDs in error text)
 =====================================================================
   context:  b09 also holds .eh_frame for b06 (28 FDEs, all verified as
   functions) and the enum-name table (148 WHAL_*/WAL_* strings);
   b12 = X.509 chain (Fairphone BV / T2MO).  b07/b08 = RW data (RV32-C
   decodable "noise" — data, not code).
```

Two routing levels, both table-driven; the registry's ptr column routes a group to its dispatcher, the dispatcher's b06 jump tables route an event ID to its handler block. The registry head is the one place where code touches the record structure by absolute address — as an enable-mask/list-head object — while per-event dispatch never reads the records.

## 5. The decoded PDEV map (summary)

Excerpt of the ID→handler-block map (ath11k names for 0x4001–0x4022; 0x4023+ are firmware-specific IDs unnamed in ath11k). The complete 85-row PDEV and 16-row STATS maps with registry cross-check flags are in `results/wmi-pdev-dispatch-map.json` (open-discovery-lab, commit `1a08b27`).

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

STATS (table 0xc05641fc): 0x16001 WMI_STATS_EXT_EVENTID→0xc02cdc6c, 0x16004 WMI_RADIO_LINK_STATS_EVENTID→0xc02ce0a0, 0x16005 WMI_UPDATE_FW_MEM_DUMP_EVENTID→0xc02ce058, 0x16006 WMI_DIAG_EVENT_LOG_SUPPORTED_EVENTID→0xc02ce198, 0x16008 WMI_RADIO_TX_POWER_LEVEL_STATS_EVENTID→0xc02ce1d4, 0x1600c WMI_RADIO_CHAN_STATS_EVENTID→0xc02ce084, plus fw-specific 0x1600e/0x1600f/0x16010. MISC cmp tree: 0x1d00b WMI_VDEV_GET_KEEPALIVE_EVENTID, 0x1d010 WMI_UPDATE_VDEV_RATE_STATS_EVENTID, 0x1d014 WMI_RSSI_BREACH_EVENTID, 0x1d019 WMI_PKGID_EVENTID (+ fw-specific 0x1d01a, 0x1d01d). GPIO: 0x1e001 WMI_GPIO_INPUT_EVENTID, 0x1e002 WMI_UPLOADH_EVENTID. SUSPEND: 0x11001 WMI_PDEV_RESUME_EVENTID (+ fw-specific 0x11002). Every listed target was verified to hold decoded Hexagon instructions.

## 6. Methodology: Hexagon decode with Ghidra headless (reusable by others)

The capability gap that blocked F-23 — no Hexagon decoder in capstone — is closed by Ghidra 12.2's processor module. The working recipe (full honest log in `docs/hexagon-decode.md`, commit `3f5c808`):

1. **Install**: `ghidra_12.2_PUBLIC_20261016.zip` (569,712,708 B; SHA-256 `2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67`, verified against the release page) + **Java 25** (Temurin JDK 25.0.5+8; JDK 21 is rejected). Ghidra/JDK stay out of git.
2. **Import** the raw segment at its virtual address, omitting `-loader` (loader-name flags fail; the default loader is Raw Binary and `-loader-baseAddr` still applies):
   `analyzeHeadless <projdir> wpssproj -import wpss.b06 -processor Hexagon:LE:32:default -loader-baseAddr 0xc0002000 -analysisTimeoutPerFile 300`
   (Project paths must not contain dot-prefixed elements — copy inputs to a plain directory.)
3. **Script it** from CPython via PyGhidra 3.2.0 + Jpype 1.7.1 (`GhidraProject.openProject` takes a String path; `Listing` APIs take `Address` objects). Per target address: explicit `DisassembleCommand` (follow-flow) + `CreateFunctionCmd`; record first instruction, function creation, body size.
4. **Seed from structure, not auto-analysis.** Registry pointers, eh_frame FDE starts, and jump-table words (read from the raw file) define the target set; auto-analysis timed out at 300 s and is not depended on.
5. **Cross-validate at three levels**: decode (do the pointers disassemble?), ground truth (do all 28 eh_frame starts become functions?), coherence (do the registry records and the decoded dispatch tree agree? 49/58 shared IDs here).

The negative-control discipline of F-19/F-20 transfers to decode work: the odd pointer 0xc04ecc3d, predicted dead by alignment reasoning, produced no instruction — a decode-level confirmation of the structural suspicion.

## 7. Negative results and limitations

The chain contains four falsifications/corrections that are part of the result (Section 3), plus these standing limits:

- **No decompiler.** DecompInterface launches but timed out on all four large handlers (60 s each); all analysis is disassembly-level. Handler-block *bodies* are mapped but not individually reverse-engineered — "handler" means the decoded block reached for that ID.
- **The per-record consumption loop was not located.** No decoded instruction materializes a registry run start; no 12-stride pointer-chase was identified inside the dispatcher. Who calls `0xc02cd9cc` with R1 = ID remains unknown.
- **8 registry PDEV IDs route to the shared exit** in this dispatcher (0x4004 PDEV_DUMP, 0x4005 TX_PAUSE, 0x4007 L1SS_TRACK, 0x4008 TEMPERATURE, 0x4014 CHIP_POWER_STATS, 0x4036, 0x403a, 0x404c) — handled elsewhere, accepted-and-dropped, or vestigial; unresolved. One handled ID (0x404e) has no registry record.
- **The other group dispatchers are separate functions** (VDEV `0xc031d8c8` etc., decode-verified in F-28) — same pattern expected, not yet decoded.
- **Coverage**: the saved program holds 357,390 decoded packets of b06's ~6 MB; the program-wide b09-reference scan is over decoded instructions, not all bytes. The unidentified 16-byte-stride id+hash table in b09 (file 0xd000–0xe0xx) and the b23 38.9 MB opaque body (q6zip-suspected) remain open.
- Kept for the record: the b09 ptr-column semantics were undetermined until F-28/F-29 pinned the dispatcher reading; the 0xc04ecc3d records likely point at data or a mis-recorded pointer.

## 8. Implications for LibrePhone

What a free WMI/WCN6750 implementation must know:

1. **WMI dispatch in this firmware is two-level and table-driven** — never arithmetic. Any tool hunting for `grp<<12|cmd` constants or construction sites in this image will find nothing, for a structural reason (the data segments are not code), not a coincidental one.
2. **The ID space is shared but the enums are not**: b09's 148 `WHAL_*`/`WAL_*` names are firmware-internal; ath11k names cover 0x4001–0x4022 of the PDEV family, while 0x4023+ (e.g. 0x404d/0x404e), 0x1600e–0x160010, 0x5022, 0x11002, 0x1d01a/0x1d01d are firmware-specific.
3. **Concrete routing facts**: registry anchor 0xc0691080 (head 0xc0691050/0xc0691068, armed by the dispatcher); PDEV jump table 0xc056423c (85 entries, index = (ID&0xff)-1); STATS table 0xc05641fc; shared exit 0xc02cedcc→0xc04e61a8; per-group dispatchers PDEV 0xc02cd9cc / VDEV 0xc031d8c8 / PEER 0xc02d94bc / ROAM 0xc035d2e0.
4. **Clean-room discipline**: everything published here is derived metadata (addresses, structures, protocol constants), never blob content — consistent with this repo's principles. The 61-entry map is the decoded shape of the firmware's event surface.
5. **Upstream angle**: LibrePhone's per-file wpss docs can be corrected (b06 = Hexagon, b07/b08 = data, b09 = the registry) with the evidence chain cited here; a decoded firmware event surface is a candidate for the ath11k mailing list.

## 9. Reproduction

All inputs derive from the public LineageOS 23.2 FP6 nightly (`wpss.mdt` + `wpss.bNN`; `instruments/ath11k/wmi.h` for the 605-ID enum evaluation; `adsp.b36` and `modem.b19/b23/b24` as controls). No blobs are committed anywhere; every analysis ships as a script plus a curated JSON.

**Tools** (adineo-cmd/open-discovery-lab, `track-a-android-blobs/tools/`): `xref_wmi.py` (F-9 enum evaluator + aligned scanner), `wpss_disasm.py` (F-20 sweep + pattern scanner), `wmi_b091012_scan.py` (F-22 registry scan), F-23's `wmi_b06_consumer_scan{,2,3}.py` (host scratch, documented in its doc), F-28's Ghidra/PyGhidra scripts (host `tools-ghidra/`, documented). Ghidra 12.2 + Temurin JDK 25 per Section 6.

**Results** (`track-a-android-blobs/results/`): `modem-wmi-xref.json` (F-19), `wmi-dispatcher-search.json` (F-20), `wmi-dispatcher-b091012.json` (F-22), `wmi-registry-consumers.json` (F-23), `modem-b23-b24-scan.json` (F-26), `hexagon-decode.json` (F-28), `wmi-pdev-dispatch-map.json` (F-29 — full 101-entry ID→block maps, trees, tie-in chain, cross-tabs).

**Finding documents** (`track-a-android-blobs/docs/`): `wmi-xref.md` (with its correction banner), `modem-wmi-xref.md`, `wmi-dispatcher-search.md`, `wmi-dispatcher-b09-b10-b12.md`, `wmi-registry-consumers.md`, `modem-b23-b24-unpack.md`, `hexagon-decode.md`, `wmi-pdev-dispatch-map.md`.

**Prior-art audit**: `results/prior-art-audit.md` (commit `a8cc9d7`, applied `a1873ba`).

## Appendix A: finding-to-commit map (adineo-cmd/open-discovery-lab, branch main)

| Finding | Content | Commit(s) |
|---|---|---|
| F-9 | ath11k↔wpss WMI xref (605 IDs; corrected later) | docs/wmi-xref.md + correction banner per F-19 |
| F-19 | modem xref NO, adsp.b36 control; F-9 correction | d012567, cea22ca, ledger 1154ffe |
| F-20 | b07 construction-site search: none (mechanism falsified) | d410643, ledger e9e7838 |
| F-22 | b09 registry found; b07/b08 are data; table-driven story | 81c4200, ledger 9e3a635 |
| F-23 | b06 = Hexagon; per-group handler mapping; anchored lists | 85b05aa, f232e66 |
| F-26 | modem b23/b24 unpack; F-19 caveat closed | c7443a6 |
| F-28 | Ghidra 12.2 Hexagon decode; 21/22 + 28/28 verified | 3f5c808 |
| F-29 | PDEV dispatcher decoded; 61 events; registry head traced | 1a08b27 |
| audit | prior-art audit (F-1..F-26) | a8cc9d7, applied a1873ba |

## Appendix B: inconsistencies found during synthesis (recorded, per the lab's Rule 1)

Small discrepancies in the source documents, none affecting the conclusions; recorded here so the underlying docs can be patched:

1. **F-number drift inside docs.** `wmi-dispatcher-b09-b10-b12.md` self-identifies as "F-21" in its claim text and calls the consumers doc "the natural F-22 target" — in the final ledger those are F-22 and F-23 (F-numbers are assigned at merge time; the earlier 2026-11-10 commits carry the pre-assignment labels, e.g. commit `81c4200` is titled "F-21"). Likewise commit `c7443a6` calls the b23/b24 unpack "F-25" (ledger: F-26) — a conflict the prior-art audit already flagged (item 9).
2. **b06 end-address variants.** The three docs give the b06 range end as 0xc05cb111 (F-22 header table text), 0xc05bdb31 (F-23), and Ghidra's flat block end 0xc05cd110 (F-28), while all agree base 0xc0002000 and filesz 6,074,641 (= 0x5CB111, so end-exclusive 0xc05bd111). These look like transcription variants of the same fact; the load-bearing numbers (base, size) agree everywhere.
3. **F-22 main-run arithmetic.** "69 records" is paired with file range 0x2a080–0x2a3b0, which spans 0x330 = 816 bytes = 68 records; 69 records would span 0x33c (end 0x2a3bc). One of the two is off by exactly one record.
4. **F-26 zero-fill percentage.** The claim line says b24 is "90% all-zero fill"; the entropy table computes 386/442 blocks = 87% (also stated in the body). The 87% figure is the computed one.
5. **F-29 header date vs commit date.** The F-29 doc header says 2026-11-12; its commit `1a08b27` is dated 2026-11-11T18:44Z (and F-28's `3f5c808` 2026-11-11T18:10Z) — plausibly a local-time vs UTC difference; noted for the record.
6. **Ledger lag.** The FINDINGS.md snapshot consulted during synthesis ends at F-27, while the F-28/F-29 documents and commits exist; the ledger rows for F-28/F-29 postdate the docs.
