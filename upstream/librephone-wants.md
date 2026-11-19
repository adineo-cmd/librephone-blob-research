# LibrePhone "wants vs done" master matrix

The complete inventory of everything the FSF's LibrePhone initiative has
asked for or implicitly needs, cross-checked against the lab's committed
work and against what other contributors have already pushed upstream.
**This file is the audit of record; completeness over speed — every want
is enumerated, including blocked and out-of-scope ones.**

- Audit date: **2026-11-15** (all URLs below fetched this date unless
  noted). Auditor: Open Discovery Lab agent session (wants-vs-done audit).
- Upstream repos: https://codeberg.org/rsavoye/librephone (code + docs +
  data) and https://codeberg.org/rsavoye/librephone-web (site source).
- Note: the Codeberg *org* `librephone`
  (`/api/v1/orgs/librephone`, `/api/v1/users/librephone/repos`) is an
  empty user (created 2025-11-13, 0 repos) — all project content lives
  under `rsavoye`. `librephone.org` redirect-loops (50-redirect cap, HTTP
  302 recorded); the live site is **https://librephone.fsf.org** (linked
  from the FSF campaign page), and `librephone.org/kernel-xref/html/` +
  `/modules-xref/html/` (Doxygen trees) still resolve.

## Status vocabulary

- **LAB** — the knowledge exists in the lab (cite the FINDINGS row /
  committed doc); filing upstream is separately owner-gated.
- **OTHERS** — already pushed/answered upstream (cite commit/PR/issue).
- **OPEN-E** — open and executable now from this box (doc RE from public
  data, corrections to upstream docs, provenance/hash records, bring-up
  notes from public sources).
- **OPEN-B** — open but blocked (needs binaries/hardware/owner accounts).
- **OOS** — out of scope for the lab (writing firmware per RULE 3; owner
  exclusions: CVE hunting, classical-cipher cryptanalysis).

## Search log (RULE 0 — queries and dates)

| Date | Query / fetch | Result |
|---|---|---|
| 2026-11-15 | `codeberg.org/api/v1/orgs/librephone` + `/orgs/librephone/repos` | empty user, 0 repos |
| 2026-11-15 | `codeberg.org/api/v1/users/rsavoye/repos` | 3 repos (librephone, librephone-web, abe) |
| 2026-11-15 | `/repos/rsavoye/librephone/issues?state=all&limit=50&type=issues` | 41 issues (28 open, 13 closed) — all bodies read |
| 2026-11-15 | `/repos/rsavoye/librephone/pulls?state=open` | 3 open PRs (+#58 comments, 13) |
| 2026-11-15 | `/repos/rsavoye/librephone/commits?limit=50` | last 50 commits enumerated (back to 2026-09-10) |
| 2026-11-15 | raw fetch of 13 upstream docs + 3 data CSVs | current text captured (b06/b07/b09/b10/b01, wireless, files, other, index, comparing, csvdata, totals-head, track-head) |
| 2026-11-15 | https://www.fsf.org/campaigns/librephone/ + /news/librephone-project | campaign goals + announcement text extracted |
| 2026-11-15 | librephone.fsf.org (/, /hardware, /faq, /freedom, /site/, /site/tools/) + kernel-xref + modules-xref | site want-surface captured |
| 2026-11-15 | all 41 issues scanned for prior corrections of `docs/other.md` Xtensa claims (`CAMERA_ICP`, `vpu`, `Xtensa`) — zero hits; last 50 commits — no other.md change | the newly-found errors are uncorrected anywhere |
| 2026-11-15 | grep of upstream `data/sizes.csv` (1.6 MB) for FP6 rows | 0 FP6 rows (992 Fairphone rows, all FP5/FP4) while `data/devices.csv` has 444 FP6 rows — upstream data gap confirmed |
| 2026-11-15 | grep lab `wpss.b07.strings.txt` for L4/L4Ka markers | absent (QURT vocabulary only) — backs the #38 answer |

No public "wants vs done" audit of LibrePhone exists (this matrix maps
the campaign's asks against the lab's own findings — inherently unique
per RULE 0; the per-claim novelty of the underlying lab findings was
audited at merge time, see FINDINGS.md header).

---

## Group A — explicit wants: the 28 open issues of rsavoye/librephone

Fetched via `/api/v1/repos/rsavoye/librephone/issues?state=open` on
2026-11-15. Labels as upstream set them.

| ID | Issue | Want (verbatim gist) | Status | Lab evidence | Others' evidence | Next action |
|---|---|---|---|---|---|---|
| A-1 | #15 (High, Doc) | "Document the interface between the Bluetooth driver and the blob" | LAB (firmware side) / OPEN-E (driver side) | F-14: BT partition census — FAT16 layout, btqca.h TLV decode, rom_build→filename kernel math, EVROS/WCN6450 identity (F-32) (`qualcomm-fp6/docs/bt-firmware-census.md`) | hci_qca.c/btqca.c are the driver side; upstream doc not started | Package the firmware-side facts as a doc PR (extends PR-4 text); driver-side interface doc executable-now from `sm7635-modules/qcom/opensource/bt-kernel` |
| A-2 | #17 (Medium, Doc) | NFC driver↔blob interface doc | OPEN-E | none (no NFC work in lab) | none found | Executable-now: doc from public `sm7635-modules/qcom/opensource/data-kernel`/NFC stacks |
| A-3 | #18 (Medium, Doc) | Cellular radio driver↔blob interface doc, API-doc style, "to be turned into a test suite" | OPEN-E | partial: F-36/F-31 modem ISA decodes identify the firmware side | none found | Executable-now (MTK twin is ROADMAP M-3); large task, recommend scoping session |
| A-4 | #19 (High, Research) | Identify user-space vs loaded-firmware code | OPEN-E (partial) | F-15 boot-chain census; F-22/F-28 segment executability facts | none found | Partially executable from committed censuses; needs modem AArch64 PIE analysis to finish |
| A-5 | #2 (good first issue) | UI for the device database | OPEN-B | none | PR #14 (db_interface) open since 2025-11-07 | Code contribution — out of lab's doc-RE charter; blocked on Codeberg account anyway |
| A-6 | #23 (Low) | OnePlus 15 Lineage support | OPEN-B | none | none | Needs hardware/build farm |
| A-7 | #25 | "Clean Slate — Let's consider -1 one us well. -1,0,1" | OPEN-B (noise) | — | — | Apparent spam/noise; suggest upstream close |
| A-8 | #26 (Medium, Doc) | CopyEngine API doc (8-buffer ring for HIF/HTT→blob) | OPEN-E | none | none | Executable-now from public `sm7635-modules/qcom/opensource/wlan/cmn_utils` |
| A-9 | #33 (Medium, Research) | Identify 16 shared libraries (05B04A44, 32552B22, evautil64, FD719D50, featenabler, focal64, hdcp1, hdcp2p2, hdcpsrm, ic5, loadalgota64, ops, smplap64, soter64, sp_license, winsecap) | LAB (partial — 8 of 16 identified or characterized) | trustzone-census.md: soter64 = SOTER device-attestation TA; smplap64 = Qualcomm "sample app" crypto/test TA; featenabler = RPMB-backed feature licensing (ships twice); 05B04A44+FD719D50 = secure-element service TAs (CESEService_*, GPQESE_* — GlobalPlatform SE API); 32552B22 = honest negative (no strings ≥8 chars); evautil64/hdcp* = AArch64 per census (`qualcomm-fp6/results/census.md` rows for all 16) | b4e3f282 (2026-11-03) kernel fork loads 64-bit MDTs — removes the issue's "mdt_loader is ELF32-only" premise | Paste-ready issue comment prepared (see pr5-corrections-package.md, C-3); focal64/ic5/ops/loadalgota64/sp_license/winsecap remain genuinely unidentified — executable-now if the image census is re-run against public Qualcomm trees (same method as F-32's EVROS identification) |
| A-10 | #34 (Medium) | "Figure out TrustZone exploit" | OOS | trustzone-census.md policy note: "no TrustZone code analysis, no keys, no bypass guidance" | — | Excluded by owner directive (CVE hunting excluded 2026-11-09); not lab work |
| A-11 | #35 (Medium, Doc) | Document how signed blobs get loaded (to enable future blob replacement) | LAB (chain facts) / OPEN-E (kernel-side doc) | F-14/F-15: SRoT MBNv7 → Fairphone "T2MO OEM Key" chain, X.509 validity, vbmeta flags=3, rollback_index-as-patch-date; F-18: MTK mtk_hdr dual-X.509 per-payload signing | PR #58 thread: scm PAS rejects ANY replaced segment (confirmed independently by L123123) | Lab chain censuses are the doc's facts; kernel PIL/qseecom loading doc executable-now from public sources |
| A-12 | #36 (Medium, Doc) | Identify blobs in the /radio directory | LAB (partial) | F-15 bootchain-census: xbl (3-ELF container), shrm/aop/aop_config/cpucp = RV32, qupfw = Hexagon claim, abl/uefi/xbl_ramdump build IDs — these are the radio-dir images | upstream's own docs/track.md tracks radio files per device (no ISA IDs) | Boot-chain census rows answer most of it; a paste-ready extension of PR-4's boot-chain block covers the rest |
| A-13 | #37 (Medium, Research) | Which WPSS blob is the PCIe bridge | OPEN-E (partial) | F-8 transport finding (PCIe-style WAKE# + IPC buffers); PR-2 WMI dispatch doc | PR #58: L123123 bypasses the blob's endpoint role entirely (patched ath11k treats chip as real PCIe device); issue #56 lspci capture shows Device 1105 | Partially executable from committed work + public qcacld sources; needs the bridge/ICRSS role pinned in b01/b02/b03/b05 Hexagon segments |
| A-14 | #38 (Medium, Research) | "Check for L4 kernel in WPSS blobs" | **LAB — answer available** | F-8: wpss.b07 runs Qualcomm QURT RTOS on RV32 (`QURTK_*`, UTCB/TCB, `mcause` exception path); committed strings show no L4/L4Ka vocabulary | upstream's own b07.md already says "RISCV32" | Paste-ready issue comment prepared (pr5-corrections-package.md, C-1) |
| A-15 | #39 (Medium, Research) | What is the Gunyah hypervisor used for? | OPEN-E | none | Gunyah is public (mainline `drivers/virt/gunyah`, Qualcomm's open-source pVM hypervisor) | Executable-now: short doc from public sources + FP6 boot-log references |
| A-16 | #40 (Medium, Research) | readelf vs instrumented mdt_loader.c phdr address differences | OPEN-E (partial) | F-7 junk-header methodology is adjacent (segment ELF headers untrustworthy; .mdt phdrs authoritative) | none | Executable-now: read public `mdt_loader.c` (ELF32 ET_EXEC vs ET_DYN translation) + upstream's Lineage readelf build |
| A-17 | #41 (High, Research) | Identify `05B04A44-BF30-42DF-9E2F-B366B980ED19.*` | **LAB — identified** | trustzone-census.md: secure-element service TA (`CESEService_*`, `GPQESE_Open/Transceive` — GlobalPlatform SE API); size/hash rows in results/census.md | b4e3f282 removes the ELF32-mdt_loader premise | Paste-ready issue comment prepared (pr5-corrections-package.md, C-2) |
| A-18 | #42 (High, Research) | Identify `32552B22-89FE-42B4-8A45-A0C4E2DB0326.*` | **LAB — honest negative** | trustzone-census.md: no strings ≥8 chars in the TA; size/hash rows committed | — | Paste-ready issue comment prepared (pr5-corrections-package.md, C-2) — states the negative and the census rows |
| A-19 | #43 (High, Research) | Identify `FD719D50-FFFB-11EB-9A03-0242AC130003.*` | **LAB — identified** | trustzone-census.md: secure-element service TA (same CESEService/GPQESE family as A-17) | b4e3f282 | Paste-ready issue comment prepared (pr5-corrections-package.md, C-2) |
| A-20 | #44 (High, Research) | FTM code instrumentation points | OPEN-E | none | upstream docs/ftm.md exists (8.9 KB) | Executable-now from public Qualcomm library source |
| A-21 | #45 (Medium, Doc) | Expand the FTM doc | OPEN-E | none | ftm.md exists | Executable-now from public sources |
| A-22 | #46 (High, Research) | QMMI / Diag Mode protocol from a host computer | OPEN-E | none | Qualcomm DIAG protocol (0x4B wrapper, DM/DL) is publicly documented across postmarketOS/OEM tooling literature | Executable-now as a literature survey doc; protocol capture needs hardware (blocked part) |
| A-23 | #50 (Medium) | Kernel-module debugging via Bazel external modules | OPEN-B | none | none | Build-infrastructure work — outside lab charter |
| A-24 | #56 | HIF "fake PCI" misunderstanding (WCN6750 as real PCIe endpoint) | OPEN-E (partial) | F-8 transport finding; papers/wmi-dispatch-architecture.md (the firmware-side dispatch) | issue body's own lspci capture; PR #58 entire approach; commit b75b158f already corrected the transport doc to IPCI/ICNSS2 (2026-11-01) | Lab adds the firmware-side dispatch facts; conclusion depends on hardware captures (blocked part) |
| A-25 | #59 (good first issue, Medium) | mdttool: replace a blob's certificate (needs cert-chain write path) | OPEN-B | F-14/F-15 cert-chain censuses document the chains being replaced | none | Code contribution — blocked on Codeberg account; lab cert censuses are the reference material |
| A-26 | #61 | pytest fixture lookup breaks outside tests/ | OPEN-B | none | none | Code contribution |
| A-27 | #62 | test_split_blob refusal returns empty list | OPEN-B | none | none | Code contribution |
| A-28 | #63 (Medium) | Fix Lineage-24.0 FP6 build | OPEN-B | none | none | Needs build farm/hardware |

Closed-issue completions already landed upstream (done-by-others,
cited for the ledger): #16 wifi driver interface (docs/
wifi-driver-interface.md, 26.8 KB, live on main), #27 HIF/HTT API
(docs/hif.md 15.7 KB + docs/htt.md 31.3 KB + docs/ath11k.md 8.3 KB),
#13 modem blob merging, #11 Hexagon Ghidra plugin (resolved both
upstream and in the lab via Ghidra 12.2's public Hexagon module, F-28),
#9 FP6 device files (ArianK16a tree), #8 standalone kernel, #5 initial
blob functionality (the 215-device database), #1 best dev device (FP6),
#47/#49/#52/#53 elf.py fixes (bobov, merged as PR #60, e32dfb1a,
2026-11-06), #54 cert tests (FrossGus), #55 T2H dispatcher lookup
(a92aa0df), transport correction b75b158f "docs: correct WCN6750
transport to IPCI/ICNSS2" (2026-11-01).

## Group B — implicit wants: upstream docs and data state

| ID | Want | Source (fetched 2026-11-15) | Status | Lab evidence | Next action |
|---|---|---|---|---|---|
| B-1 | Correct `docs/wireless.md` "8 bit ATMel AVR core, and possibly a RISCV32 core" guess | https://codeberg.org/rsavoye/librephone/raw/branch/main/docs/wireless.md (lines 22-23, unchanged from 2026-11-12 fetch) | LAB | F-5 (RV32 instruction-level proof); packaged as PR-1 in upstream-contribution/README.md | Owner files PR-1 |
| B-2 | Second AVR instance in wireless.md's WPSS section ("It seems to contain an ATmel AVR core... The blob that seems to be an Intel x86_32 is suspicious", lines 90-92) | same URL | LAB | F-5/F-8 (QURT on RV32); F-7 (b08's x86 header is junk on a data segment) | Newly packaged as PR-6 (pr5-corrections-package.md) |
| B-3 | `docs/wpss.b01.md` claims "ATMel AVR8 (ATmega8) micro-controller embedded in the WCN6750" | https://codeberg.org/rsavoye/librephone/raw/branch/main/docs/wpss.b01.md | LAB | F-20/F-22: wpss.mdt phdrs mark only b01/b02/b03/b05/b06 executable and declare e_machine=164 (EM_HEXAGON) — b01 is a Hexagon code segment; F-7 methodology (r2 `-a avr` on raw segment bytes = plausible noise, the junk-header trap); upstream's own "Current Research" section already suspects one DSP6 image | Newly packaged as PR-6 |
| B-4 | Per-segment docs wrong: b06 "single data file/error messages", b09 "PSX image", b07 "total garbage" blocks, b10 unexamined, b12 cross-check | docs/wpss.b0{6,7,9}*.md — re-fetched 2026-11-15, unchanged | LAB | F-20/F-22/F-23/F-28/F-29; packaged as PR-2 + PR-3 | Owner files PR-2, PR-3 |
| B-5 | files.md lacks bluetooth-partition facts and a boot-chain section | docs/files.md re-fetched (bluetooth.img section is still a bare file list, lines 81-90) | LAB | F-14/F-15; packaged as PR-4 | Owner files PR-4 |
| B-6 | `docs/other.md` says CAMERA_ICP.b[0-9][0-9]/CAMERA_ICP.mbn = "Tensilica Xtensa certificates" and vpu20_2v.mbn = "Xtensa 32 Bit executable" | https://codeberg.org/rsavoye/librephone/raw/branch/main/docs/other.md | **LAB — NEW error found this session** | F-6: CAMERA_ICP.mbn/.elf/.mdt + vpu20/30/33_*.mbn are ELF32 **e_machine=94 (historic RISC-V)**, ICP version `CICP.FW.7.0-00021`, platforms Mimas/Skye (`qualcomm-fp6/docs/fp6-architecture-census.md`); audit note: raw values publicly dumped by gdrci/Research 2026-10-08 — lab delta is the ISA interpretation | **Newly packaged as PR-5 (pr5-corrections-package.md)** |
| B-7 | BDF format unknown ("only documentation available from Qualcomm requires an NDA"); ath_bdf_tool could be updated | wireless.md lines 67-76 | OPEN-E | lab census has bdwlan.* as ARM ELF board-data files (60,000 B each) but has not decoded the BDF payload | Executable-now: public ath11k BDF/wil6210 literature + lab census rows; recommend as future session |
| B-8 | wpss.b02/b03/b04 "a bit mysterious... not ELF executables... raw binary files" | wireless.md lines 94-101 | LAB | F-20/F-22 phdr facts (executable segments of the Hexagon MDT image) | Fold into PR-6 or a future per-segment PR; owner files |
| B-9 | No docs exist for the modem/adsp/cdsp/camera/audio/sensor firmware families (other.md admits "more reverse engineering would be required") | docs/other.md + docs/ tree listing | OPEN-E | Lab has censuses for: TrustZone (F-14), boot chain (F-15), BT (F-14), full ISA map (F-5/F-6) — Qualcomm side largely covered by lab docs; upstream-facing doc stubs not yet packaged | Package per-family doc stubs as a future PR (after PR-1..PR-6 land, to avoid conflicts) |
| B-10 | `data/sizes.csv` (1.6 MB) has **zero FP6 rows** while `data/devices.csv` has 444 FP6 rows — the per-file hash/size/type dump predates the FP6 build | data/sizes.csv + data/devices.csv (fetched 2026-11-15) | OPEN-E | Lab results/census.md carries FP6 per-file size/type/md5 rows (16-hex truncated md5s) for 665 files | Executable-now: re-run the census with full md5 and contribute FP6 rows to sizes.csv (provenance cross-check at the same time) |
| B-11 | PR #58's Zephyr payload implements the PCIe endpoint/MHI/QRTR/WLFW layers but explicitly NOT WMI/HTT/CE — whoever completes it needs a firmware-side WMI spec | https://codeberg.org/rsavoye/librephone/pulls/58 (body + 13 comments, fetched 2026-11-15) | LAB | papers/wmi-dispatch-architecture.md = the first public WMI dispatch spec for this firmware (registry format, 225 records/149 IDs, 61 decoded events, dispatcher addresses) | Reference the paper in a PR-58 comment once filed (owner-gated); the spec is the lab's RULE 3 contribution to the free implementation |

## Group C — campaign-level wants (FSF pages)

| ID | Want | Source | Status | Lab evidence | Next action |
|---|---|---|---|---|---|
| C-1 | "Reverse-engineer and replace those proprietary modules with fully free software, for at least one modern phone" | https://www.fsf.org/news/librephone-project | OPEN-E (spec side) / OOS (implementation side) | RULE 3: the lab is the clean-room SPEC producer — F-5..F-29 (Qualcomm), F-16..F-45 (MediaTek); B-11 shows the spec being consumed by the free-replacement PR | Keep producing per-family specs; implementation is out of lab scope |
| C-2 | Triage device packages; find the phone with the fewest, most fixable freedom problems (210-215 Lineage devices downloaded) | announcement + docs/comparing.md + closed #5 | OTHERS (infrastructure) + OPEN-E (cross-device RE) | Upstream has the database (devices.csv/count.csv/sizes.csv/devices.sql.bz2); the lab contributes per-device ISA censuses | The lab's cross-vendor censuses (FP6 + rosemary) are exactly the "fewest fixable problems" evidence; continue per ROADMAP Rule 2 |
| C-3 | Hardware documentation page currently lists exactly ONE device (Fairphone 6) | https://librephone.fsf.org/hardware | OPEN-E | Lab's mediatek/rosemary-census.md = complete MediaTek device doc (12 partitions, ISA map) — upstream has ZERO MediaTek content | Package a MediaTek hardware/firmware page from committed lab docs (owner-gated filing; packaging executable) |
| C-4 | "Once there is sufficient interest and funding, a detailed specification will be written so that programmers who are not bound by the DMCA can code free implementations" | https://librephone.fsf.org/faq | OPEN-E (spec side) / OOS (code side) | Same as C-1 | Specs first (lab charter) |
| C-5 | Donations, IRC community (#librephone Libera.chat) | campaign page + FAQ | OPEN-B | — | Not lab-actionable |
| C-6 | Website FAQ volunteer links are plain list items with no hrefs (pages/faq.php lines 23-25) — the "how to help" path is incomplete | codeberg.org/rsavoye/librephone-web raw pages/faq.php | OPEN-B | none | Trivial site PR (link to Codeberg issues) — owner-gated filing |

## Group D — open pull requests (other people's in-flight work)

| ID | PR | Status | Notes |
|---|---|---|---|
| D-1 | #58 "Add WCN6750 AMSS Zephyr implementation" (L123123, opened 2026-11-01, 13 comments) | OTHERS (in progress) | A Zephyr bring-up payload for the wpss RISC-V core (BHI load, PCIe endpoint, MHI slave, QRTR v1, WLFW stub); WMI/HTT/CE and RF/PHY NOT implemented; author works on a OnePlus ACE 3V (sm7675); confirms scm PAS rejects any replaced segment; SRAM <200 KB constraint noted. Thread confirms lab facts: "the RISCV blob is wpss.b07" (maintainer), signing-chain lock (issue #34's premise) |
| D-2 | #14 "db_interface" (zsaunders, 2025-11-07) | OTHERS (stalled) | Database interface work — overlaps A-5 |
| D-3 | #10 "WIP: Improvement on Issue #5" (S54, 2025-10-28) | OTHERS (stalled) | Blob-functionality spike |

---

## Classification counts (as of 2026-11-15)

Over the 47 enumerated actionable rows (28 issue rows minus noise row
A-7, 11 doc/data rows, 6 campaign rows, 3 PR rows), one primary status
per row (rows with a dual status are counted under their actionable
half):

| Status | Count | Rows |
|---|---|---|
| LAB (knowledge done in the lab; filing owner-gated where upstream text is the target) | 15 | A-9*, A-11*, A-12*, A-14, A-17, A-18, A-19, B-1, B-2, B-3, B-4, B-5, B-6, B-8, B-11 |
| OTHERS (already pushed/answered upstream) | 4 | C-2 (device database infrastructure), D-1, D-2, D-3 — plus the closed-issue completions and merged PRs cited in the Group A tail (#16, #27, #5, PR-#60, PR-#55, b75b158f), which are done-by-others evidence rather than separate rows |
| OPEN-E (open, executable now from this box) | 18 | A-1(driver side), A-2, A-3, A-4, A-8, A-13, A-15, A-16, A-20, A-21, A-22, A-24, B-7, B-9, B-10, C-1, C-3, C-4 |
| OPEN-B (blocked: hardware / build farm / owner accounts / code charter) | 9 | A-5, A-6, A-23, A-25, A-26, A-27, A-28, C-5, C-6 |
| OOS (out of lab scope per RULE 3 / owner exclusions) | 1 | A-10 (TrustZone exploit); the firmware-implementation halves of C-1/C-4/B-11 are noted OOS inside their rows |

\* A-9/A-11/A-12 are partial: lab evidence covers the identified
subset; the remainder is executable-now with another census pass.

## Owner-gated items surfaced by this audit

1. **File PR-1..PR-4** (existing package, upstream-contribution/
   README.md) — all four target texts re-verified unchanged 2026-11-15.
2. **File PR-5 + PR-6 and issue comments C-1..C-3** (new package,
   pr5-corrections-package.md) — newly-discovered upstream errors
   (other.md Xtensa claims, wpss.b01.md ATmega8 claim, wireless.md WPSS
   section) plus ready answers for issues #38/#41/#42/#43/#33.
3. **Comment on PR #58** with the WMI dispatch spec reference (B-11) —
   the free-replacement implementers are the spec's first consumers.
4. **Codeberg login** remains the single gate for all filings.
5. **MediaTek contribution decision** — upstream has zero MediaTek
   content; the lab's rosemary censuses could become the first (C-3).
   Owner call on timing (large package).
