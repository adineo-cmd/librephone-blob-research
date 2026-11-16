# PR-10 filing package — the remaining open issues (#15, #19, #35, #36, #56 + honest classification of the rest) (2026-11-16)

Fourth package. The 2026-11-15 wants audit
([librephone-wants.md](librephone-wants.md), Group A) enumerated the 28
open issues of rsavoye/librephone; the already-packaged answers cover
14 of them (pr5 C-1..C-3 for #33/#38/#41/#42/#43; pr8 Q-1..Q-8 for
#17/#18/#26/#37/#39/#40/#44/#45/#46). This package finishes the set:
the two High-priority research/doc issues the audit queued but no
package had covered yet (**#15 BT driver↔blob interface**, **#19
user-space vs loaded-firmware split**), **#36 radio-directory blobs**,
**#35 signed-blob loading** (partial, with the lab's policy boundary
stated), a **#56 firmware-side companion** comment, and the honest
classification of everything that is code-contribution, blocked, noise
or owner-excluded.

Companion docs (both new, in `qualcomm-fp6/docs/`):

| doc | issue(s) | file |
|---|---|---|
| BT driver ↔ blob interface, API-doc style | #15 | [interface-bt.md](../qualcomm-fp6/docs/interface-bt.md) |
| User space vs loaded firmware split table | #19 | [userspace-firmware-split.md](../qualcomm-fp6/docs/userspace-firmware-split.md) |

Fresh-state check (RULE 1, done 2026-11-16, API
`https://codeberg.org/api/v1/repos/rsavoye/librephone/issues?state=open&limit=50&type=issues`,
plus per-issue fetches and the comment endpoints of #2/#33/#46/#56/#61):

- **The open set is unchanged since the audit**: same 28 issues, none
  closed, newest `updated_at` = #63 on 2026-11-13 — nothing has been
  answered or closed upstream since 2026-11-15, so none of the
  packaged answers (pr5/pr8) needs rework. Issue #5 from the earlier
  task framing is **not** in the open set (closed upstream; its
  completion is already cited in the audit's Group A tail).
- #61 is **claimed upstream** (bobov, 2026-11-07, maintainer
  approved) — excluded here as in-progress.
- #56 gained a substantive host-side confirmation thread on
  2026-11-01 (FrossGus: WCN6750 is a real PCIe endpoint via
  IPCI/ICNSS2; upstream's own transport docs corrected by b75b158f).
  The lab's remaining delta for #56 is the firmware-side dispatch
  spec — R-5 below.
- #46: the maintainer's own 2026-09-18 comment names **QCSuper** as
  the DIAG host implementation — Rule 1 improvement for the packaged
  Q-8 answer at the bottom of this file.
- No `implementations/qca-bt/` exists yet at packaging time (the
  lab's QCA-BT clean-room stream is a separate concurrent session);
  interface-bt.md and R-1 therefore cite only committed lab docs +
  mainline. No fake citations.

Prior-art check (RULE 0, 2026-11-16): issues #15/#19/#35/#36/#34/#50/
#59/#62/#63/#23/#25 have **zero comments** each (fetched individually);
no upstream doc covers the BT rampatch header structure (prior-art
section of bt-firmware-census.md, checked 2026-11-10), no upstream
answer states the user-space/firmware split (fresh re-check of the
28 issue bodies this date), and the radio-directory question is
answered nowhere upstream except the raw per-device file lists in
`docs/track.md` (fetched 2026-11-16, 101,712 B — 46 distinct
radio-directory images enumerated).

---

## R-1 — issue #15 ("Document the interface between the Bluetooth driver and the blob")

Post this on #15:

```markdown
Interface note from the FP6 census + mainline kernel sources
(API-doc style, test-suite-ready as requested):

- blob identity: the FP6's BT firmware ships in a dedicated
  `bluetooth` partition (FAT16): two Moselle (WCN6750) rampatch
  generations (msbtfw11/msbtfw12, each as .mbn ELF + .tlv container +
  NVM .bin) plus a third "EVROS" family (evrbtfw20.tlv/evrnv20.bin)
  that the mainline stack cannot name or select — no evr string in
  btqca.c/hci_qca.c, no evr files in linux-firmware. Both .mbn
  rampatches are ELF32 ARM (Thumb entry) — a different ISA than the
  RISC-V wpss on the same chip.
- transport: H4-style HCI over serdev UART (hci_qca.c), with
  Qualcomm's HCI_IBS in-band sleep as single-byte signals 0xFE/0xFD/
  0xFC (state machines + 100 ms retransmit / 200 ms / 2 s idle
  timeouts), baudrate change via vendor opcode 0xFC48, memdump
  trigger 0xFB.
- bring-up & download (btqca.c): EDL opcode 0xFC00 reads
  soc_id/rom_ver; the kernel's own filename math
  rom_ver = ((soc_ver & 0xf00) >> 4) | (soc_ver & 0xf) selects
  qca/msbtfw%02x.mbn (ELF patch, forced SKIP_EVT_VSE_CC = send-only
  with synthetic command-complete) with .tlv fallback whose 32-byte
  header's download_mode field decides ack behavior; segments are
  243-byte chunks of command 0x1E, last segment always acked;
  WCN6750 gets a pre-download patch-config command (EDL opcode 0xFC00 + sub-command 0x28).
- NVM (msnv%02x.bin): TLV tag set — the kernel rewrites tag 2
  (BD address), tag 17 (in-band-sleep bit 0x80 + baud byte), tag 27
  (deep sleep) in flight; multi-set NVMs carry an enclosing type-4
  header (kernel skips to the first type-2 set).
- verified against the shipped binaries: the header rom_build fields
  (0x0101/0x0102/0x0200) reproduce all three filenames through the
  kernel's math; the .tlv entry equals the ELF entry minus the Thumb
  bit (same payload, two containers); EVROS's NVM uses the vendor
  HAL's multi-NVM unwrap path the kernel only partially implements.
- test-suite hooks (per the issue's goal): filename-math vectors,
  0xFC00 version round trip, 243-byte segmentation + ack modes,
  NVM tag-rewrite determinism, IBS state machine, and blob-side
  header decode against the committed census tables — the interface
  doc below lists all six.

Interface doc (full table + header decode + test hooks):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-bt.md
Blob census (sizes, hashes, first public ISA identification of this family):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bt-firmware-census.md
```

## R-2 — issue #19 ("Identify what code is run in user space vs loaded firmware")

Post this on #19:

```markdown
Split table from the FP6 censuses + public kernel sources — the issue's
assumption first:

the AARCH64 executables in modem/image are NOT the user-space part.
They are QSEE trusted applications (TrustZone-side firmware): soter64,
smplap64, focal64, hdcp*, the UUID-named TAs, etc. — loaded via
qseecom/SCM, never executed as Android user code. Your own #33
instrumentation already shows they never pass through the kernel's
mdt_loader — their loader is a different one. The real user-space
vendor code lives in vendor.img/system (HAL executables and .so
libraries, e.g. vendor.qti.bluetooth@1.x), a separate partition family
from the firmware images.

The split, per family (user space / kernel / loaded firmware):

- Bluetooth: BlueZ (free) or Qualcomm HAL | hci_uart/hci_qca + btqca
  (mainline) | WCN6750 ROM + ARM32-Thumb rampatches + EVROS family |
  UART HCI + EDL opcodes 0xFC00/0xFC48, IBS sleep.
- WiFi: wpa_supplicant | ath11k (mainline, WCN6750 supported) or
  vendor qcacld | wpss image: Hexagon code segments + one embedded
  RV32 QURT app (wpss.b07) | IPCI/ICNSS2 + MHI + WMI/HTT/CE.
- Modem: RIL (or free oFono/ModemManager) | mdt_loader + q6v5_mss +
  GLINK + QRTR + QMI + rmnet (all mainline) | modem.mdt+b00-b30
  (Hexagon) + qdsp6m.qdb + mcfg payloads | PAS auth via SCM,
  GLINK→QRTR→QMI.
- TrustZone: TEE client libs only | drivers/tee/qcom/qseecom |
  tz.img (QTEE OS), hyp.img (QHEE), keymaster/devcfg/uefisecapp/... 
  (AArch64 PIE) + the modem/image TAs | SCM via qseecom ioctl.
- DSPs: FastRPC user libs | fastrpc + qcom_q6v5_pas (mainline) |
  adsp.img/cdsp.img (Hexagon) | FastRPC ioctls.
- Boot chain: no user space at all | — | xbl (3-ELF container: RV32 +
  AArch64), shrm/aop/aop_config/cpucp (RV32), qupfw (Hexagon per
  header), uefi (AArch64), abl (ARM32) | PBL→XBL→UEFI→ABL→Linux, AVB
  from vbmeta down.

General rule the table instantiates: user-space-vs-firmware is not one
split but one per remote processor, each with its own loader (PIL for
the Hexagon/PIL processors, qseecom for TAs, hci_qca EDL for BT,
ICNSS2/MHI for wpss, XBL/UEFI for the boot chain). The kernel layer is
the free, documentation-able surface; the ISA map (which core executes
what) is now identified for every FP6 family: Hexagon (modem/adsp/
cdsp/qupfw/wpss segments), RV32 (wpss.b07, shrm, aop, cpucp), ARM32
(BT rampatch, abl), AArch64 (TZ/TAs, uefi).

One honest open point: the modem blob's internal process structure
(the Hexagon-side equivalents of user/kernel) needs Hexagon
disassembly capacity and is stated as open rather than guessed.

Split-table doc:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/userspace-firmware-split.md
ISA map:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
Boot-chain census:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
```

## R-3 — issue #36 ("Identify blobs in radio directory")

Post this on #36:

```markdown
The radio directory, from two angles — your own data plus the FP6
census:

1. What it is: the radio directory is the extracted firmware-update
   partition set (the per-partition images, not files inside a
   partition image). Your own docs/track.md enumerates it across the
   database: 46 distinct images — the boot chain (xbl, xbl_config,
   xbl_ramdump, shrm, aop, aop_config, cpucp, qupfw, uefi, abl,
   imagefv, devcfg, hyp, storsec, tzsw, pbl, bl1/bl2/bl31,
   multiimgoem), the modem set (modem, fsg, ldfw, prov, esim-full),
   the TrustZone set (tz, cmnlib, cmnlib64, keymaster, uefisecapp,
   gsa, featenabler), the WLAN/BT image (bluetooth), plus the OS-side
   images that ride along in firmware packages (boot, recovery,
   init_boot, dtbo, dtb, vbmeta, splash, logo, pvmfw, rpm, dsp).
2. Which parts of your "mostly secure boot / firmware signing" guess
   verify (FP6, from the boot-chain census): the signing infrastructure
   is not a separate blob — each image carries its own MBNv7
   signature chain (Qualcomm SRoT root → SubCA → the OEM chain ending
   at Fairphone's "T2MO OEM Key", Amsterdam, validity 2025→2045); what
   IS dedicated to secure boot are devcfg, storsec, tzsw, xbl_config
   (boot config / secure components). The rest of the radio dir is
   executable firmware for specific cores, now ISA-identified for the
   FP6 set: xbl = 3-ELF container (RV32 + AArch64 inner images);
   shrm/aop/aop_config/cpucp = RV32 ELFs (shrm's entry decodes as a
   textbook RV32 machine-mode startup and it carries the DDR init
   firmware, "DDR_FW version : 19.12.0"); qupfw = Hexagon per the
   registered e_machine 164; uefi = AArch64 with an EFI firmware
   volume inside; abl = ARM32; xbl_ramdump = AArch64.
3. The TrustZone slice is one build: tz.img + hyp.img both carry
   TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1; keymaster/cmnlib/uefisecapp/
   featenabler are AArch64 PIE images — modern QSEE images here are
   plain ELF64 files, not .mdt+.bXX splits.
4. What stays open: the ISA/structure of the other 45 devices' radio
   images (track.md lists them per device; nothing public identifies
   them beyond filenames — same gap your track.md already flags).

Boot-chain census (containers, ISA claims, hashes, cert-chain facts):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
TrustZone census (tz/hyp/keymaster/cmnlib/... structure):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/trustzone-census.md
```

## R-4 — issue #35 ("Document how signed blobs get loaded")

Post this on #35:

```markdown
The load/auth chain, from the FP6 censuses + public kernel sources —
documented per loader, because "blobs get loaded" is not one path on
this platform:

- PIL/remoteproc processors (modem, adsp, cdsp, wpss): the kernel's
  mdt_loader places the segments from the .mdt program headers
  (relocation handled via the QCOM_MDT_RELOCATABLE flag — see the
  readelf-vs-mdtloader note), then qcom_q6v5_mss / qcom_q6v5_pas
  triggers PAS authentication: the metadata (including the hash
  segments) is passed to TrustZone via SCM, and the secure world
  verifies the MBNv7 signature chain before the core is released
  from reset.
- QSEE TAs (the .mdt+.bXX apps in modem/image and the monolithic
  AArch64 partition images tz/keymaster/devcfg/...): loaded via
  qseecom through the same SCM path — by the secure world, not the
  kernel.
- Bluetooth rampatch: downloaded over the HCI EDL opcodes (0xFC00)
  with no kernel-side signature verification at all; the .tlv headers
  carry signing-format/signature fields (observed: format_version 1,
  signature 0 in all three FP6 rampatches) — whether the controller
  verifies internally is not establishable from public data.
- The chain's public facts, from the FP6 censuses: every boot-chain
  image carries an MBNv7 signature block with visible certificate
  subjects — Qualcomm SRoT MBNv7 Image Signing Root CA 6 (SubCA 10) →
  CASS-SBL40v0 → the OEM chain (Generated OEM Root/Attestation CA →
  Fairphone BV, "T2MO OEM Key", Amsterdam, validity 2025-03-05 →
  2045-02-28). Per-image cert notBefore values range 2024-03-14 to
  2026-08-31 — the chain is refreshed in slices. AVB layer:
  SHA256_RSA4096 vbmeta; the LineageOS build ships flags=3
  (hashtree + verification disabled) with rollback_index = 0, and
  vbmeta_system's rollback_index equals the security-patch date as a
  Unix epoch timestamp.
- The replacement-relevant behavior, already empirically established
  in PR #58's thread: PAS rejects any replaced segment — the
  verification is in the secure world against fused key material,
  which is the hard boundary. Documenting the chain further stops
  here by policy (the lab's scope is census/doc, no bypass research);
  what IS freely documentable and testable: the loader mechanics
  above, the hash-segment format, and the AVB descriptor walk.

Boot-chain census (signing chain, cert subjects, AVB descriptors):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
mdt-loader mechanics note:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-mdtloader-vs-readelf.md
```

## R-5 — issue #56 ("Misunderstanding of HIF")

Post this on #56 (complements the host-side confirmations already in
this thread — FrossGus's IPCI/ICNSS2 walkthrough, 2026-11-01):

```markdown
Firmware-side companion to the host-side picture already confirmed in
this thread (IPCI/ICNSS2, real PCIe-function presentation): what the
blob does after the HIF boundary — the WMI/HTT dispatch — is now
documented from the FP6 firmware:

- the WMI command/event dispatch inside the wpss image is a
  two-level, table-driven architecture: a command registry of 225
  records / 149 distinct command IDs (WMI command IDs cross-checked
  against mainline ath11k's wmi.h), a dispatcher walking that table,
  and 61 event IDs decoded with their per-event record formats;
- the dispatch code lives in the Hexagon segments (b09/b10/b12 carry
  the registry + dispatcher; the segment executability map comes from
  the wpss.mdt program headers — b01/b02/b03/b05/b06 executable);
- what that pins for a re-implementation: a free endpoint/bridge
  implementation (PR #58's Zephyr payload) speaks QRTR/MHI/WLFW below
  this layer, and WMI/HTT/CE above it — the dispatch spec is the
  firmware-side contract for the WMI half.
- still open (stated, not guessed): which Hexagon segment implements
  the PCIe-endpoint emulator itself — needs Hexagon disassembly of
  b01/b02/b03/b05, queued with binaries by size/hash.

WMI dispatch spec:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
Transport/interface notes:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-pcie-bridge.md
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-copyengine.md
```

---

## Honest classification of the remaining open issues (no paste-ready text — none was faked)

| issue | classification | reason / next action |
|---|---|---|
| #34 "Figure out TrustZone exploit" | **OOS — owner exclusion** | The lab's owner directive (2026-11-09) excludes CVE-hunting and exploit research; trustzone-census.md's policy note states the boundary ("no TrustZone code analysis, no keys, no bypass guidance"). The issue's own premise (PAS rejects replaced segments; keys in hardware fuses) is already documented factually in R-4 above — but the exploit half is not lab work and no comment should be filed by the lab. |
| #50 "Debugging kernel module" (Bazel external modules) | OPEN-B (outside lab charter) | Build-infrastructure/code work, needs the upstream build environment. The lab contributes the public half only: the Qualcomm test-API surface the module would exercise is already covered by interface-ftm-diag.md (pr8 Q-7). |
| #59 "Figure out updating the SSL certs" (mdttool cert replacement) | OPEN-B (code contribution + no Codeberg account), **blocked-with-plan** | The lab's cert-chain censuses (bootchain-census.md: MBNv7 chain, X.509 validity, OEM key chain; bt-firmware-census.md: TLV signature fields) are the reference material a cert-replacement feature needs; the write path itself is upstream code. The R-4 comment documents the chain facts publicly. |
| #61 pytest fixture lookup | **In progress upstream** — claimed by bobov 2026-11-07, maintainer approved. Excluded (do not double-work). |
| #62 test_split_blob refusal returns empty list | OPEN-B (code contribution) | Upstream-owned bug with a full diagnosis already in the issue body; any answer would repeat it. The return-vs-raise question is a design call for the maintainer, not for a census lab. |
| #63 Fix Lineage-24.0 FP6 build | OPEN-B | Needs a build farm + device validation (same class as #23); the lab has no build environment. Note: the lab's census is against 23.2 (2026-11-09 nightly) — still-building per the issue body. |
| #2 Create UI for database | OPEN-B (code charter) | Active thread (7 comments; PR #14 flask webui open since 2025-11-07); design questions (read-only vs write-back, hosting) pending in-thread. The lab's device-inventory.csv/coverage-matrix.csv (blob-database/) are upstream-consumable data views, not UI code. |
| #23 Add support for OnePlus 15 | OPEN-B | Needs the device + build farm; no lab lever. |
| #25 "Clean Slate — Let's consider -1..." | Noise | One-line non-sequitur from a non-participant (2026-01-22); recommend upstream close (same as audit row A-7). |

**#5 note:** the earlier framing listed #5 among open issues — it is
**closed** upstream (initial 215-device blob database, cited in
librephone-wants.md's closed-issue tail); verified against the fresh
open-issues fetch (2026-11-16).

## Rule 1 improvement found this session (for the already-packaged Q-8, issue #46)

The maintainer's own 2026-09-18 comment on #46 names **QCSuper**
(his comment states it "implements the Diag protocol for a host Linux
host") before the pr8 package was written; Q-8's DIAG bullet lists
community tools generically. One-line addition to the Q-8 comment
(paste after the "community tools implement it" sentence):

> The maintainer already pointed at QCSuper (comment here 2026-09-18)
> — that is the right base: it implements the 0x4B log/packet framing
> host-side and can record a DIAG capture to bootstrap any
> test-suite work.

(pr8 is a shared file under the lead's merge control, so the edit is
recorded here rather than applied in place.)

---

## Source map (what each item draws on)

| Item | Lab sources | Public sources (all fetched 2026-11-16, status logged in the companion docs) |
|---|---|---|
| R-1 (#15) | `qualcomm-fp6/docs/bt-firmware-census.md`, `results/bt-tz-census.json` | mainline `drivers/bluetooth/btqca.c` (1,032 lines), `hci_qca.c` (2,855 lines), `btqca.h` |
| R-2 (#19) | `docs/userspace-firmware-split.md` + censuses (bt/bootchain/trustzone/architecture) | `drivers/remoteproc/qcom_q6v5_pas.c`, `drivers/tee/qcom/qseecom.c` (existence per census cross-ref), issue #33 thread |
| R-3 (#36) | `docs/bootchain-census.md`, `docs/trustzone-census.md` | upstream `docs/track.md` (46 radio-dir images), `docs/files.md` |
| R-4 (#35) | `docs/bootchain-census.md` (cert chain, AVB), `docs/interface-mdtloader-vs-readelf.md` | mainline `drivers/soc/qcom/mdt_loader.c`, PAS path in `qcom_q6v5_pas.c`; PR #58 thread (2026-11-15 fetch, unchanged) |
| R-5 (#56) | `papers/wmi-dispatch-architecture.md`, `docs/wmi-dispatcher-b09-b10-b12.md`, `docs/interface-pcie-bridge.md`, `docs/interface-copyengine.md` | #56 thread (FrossGus 2026-11-01), mainline ath11k `wmi.h` IDs (per the paper's xref) |
| Classifications | `librephone-wants.md` Group A rows A-5/A-6/A-7/A-10/A-23/A-25/A-26/A-27/A-28 | fresh per-issue API fetches incl. comment endpoints (this session) |
