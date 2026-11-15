# PR-8 filing package — issue-answer comments (docs L-3/L-4) + L-2 blocked-with-plan (2026-11-16)

Third-adjacent package: the **one-page interface docs** the 2026-11-15
wants audit queued as executable-now (rows A-2, A-3, A-8, A-13, A-15,
A-16, A-20/A-21, A-22 — ROADMAP L-3/L-4). Each doc was written from
public kernel sources + public trees this session (2026-11-16, network
flaky — every fetch success/failure is recorded in the doc's "sources
consulted" section); the paste-ready comments below follow the
established format of
[pr5-corrections-package.md](pr5-corrections-package.md) (C-1..C-3):
terse factual tone, lab-derived vs public parts separated, ending with
the lab census/write-up link.

Companion docs (all new, in `qualcomm-fp6/docs/`):

| doc | issue(s) | file |
|---|---|---|
| NFC driver ↔ blob | #17 | [interface-nfc.md](../qualcomm-fp6/docs/interface-nfc.md) |
| Cellular driver ↔ blob | #18 | [interface-cellular.md](../qualcomm-fp6/docs/interface-cellular.md) |
| CopyEngine API | #26 | [interface-copyengine.md](../qualcomm-fp6/docs/interface-copyengine.md) |
| WPSS PCIe bridge | #37 | [interface-pcie-bridge.md](../qualcomm-fp6/docs/interface-pcie-bridge.md) |
| Gunyah purpose | #39 | [interface-gunyah.md](../qualcomm-fp6/docs/interface-gunyah.md) |
| readelf vs mdt_loader | #40 | [interface-mdtloader-vs-readelf.md](../qualcomm-fp6/docs/interface-mdtloader-vs-readelf.md) |
| FTM instrumentation + doc expansion | #44, #45 | [interface-ftm-diag.md](../qualcomm-fp6/docs/interface-ftm-diag.md) |
| QMMI / Diag mode | #46 | [interface-qmmi-diag.md](../qualcomm-fp6/docs/interface-qmmi-diag.md) |

Not executable from public data this session (honest skips):

- **#18's full API-doc treatment** — the doc covers the load/auth +
  transport + data-plane layers from mainline; the modem blob's
  Hexagon command vocabulary (the mcfg/dms/nas internals) needs
  disassembly capacity the lab does not have on the modem yet (the
  same lever as ROADMAP I-4). The doc says so explicitly.
- **#37's segment-level pin** — the endpoint-emulator segment inside
  the wpss image needs Hexagon disassembly of b01/b02/b03/b05; the
  binaries are not on this box. Doc frames it as the open cell with a
  3-step closure plan.
- **#46's QMMI wire protocol** — no public documentation exists
  (searched 2026-11-16); needs a hardware capture. Doc gives the
  DIAG-protocol public half and records the block honestly.

---

## Paste-ready comments

### Q-1 — issue #17 ("Document the interface between the NFC driver and the blob")

Post this on #17:

```markdown
Interface note from public sources (mainline kernel + the public FP6
trees), API-doc style as requested:

- the FP6 public module tree has no NFC module; the stack is the
  in-kernel drivers/nfc set + the Android NFC HAL, and the lab's
  665-file census of the FP6 modem/vendor/dsp partitions shows no NFC
  firmware image file — the "blob" on this device is the firmware
  inside the NFC controller, reached through the NCI protocol.
- the driver↔controller interface is layered and public: transport
  (I2C/SPI) → NCI packet framing (3-byte control header; the NXP
  variant uses a 4-byte header) → the firmware-download mode, whose
  full command set is implemented in mainline
  drivers/nfc/nxp-nci/firmware.c: 0xF0 RESET, 0xF1 GETVERSION, 0xE0
  CHECKINTEGRITY, 0xC0 WRITE (chunked, flag 0x0400), 0xA2 READ, 0xF2
  GETSESSIONSTATE, 0xA7 LOG, 0xD0 FORCE, 0xF4 GET_DIE_ID, with result
  codes and a 30 s answer timeout — i.e. the test-suite-able surface
  already has a mainline reference implementation.
- test hooks: cold/NCI mode switch → GETVERSION → CORE_RESET/CORE_INIT
  round trip; mainline ships drivers/nfc/virtual_ncidev.c for exactly
  this kind of virtual-device testing.

One honest open point: the FP6 NFC controller part number is not
stated in any public data I could reach, so the doc anchors on the
mainline nxp-nci interface and flags the chip identity as open.

Interface doc:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-nfc.md
```

### Q-2 — issue #18 ("Document the interface between the cellular radio driver and the blob")

Post this on #18:

```markdown
Interface note from public kernel sources (API-doc style), covering
the layers a test suite can actually assert:

- blob identity: modem.mdt + modem.b00–b30 (Hexagon, e_machine 164)
  plus milos/qdsp6m.qdb and the per-carrier mcfg payloads (census
  below).
- load & authenticate: drivers/soc/qcom/mdt_loader.c (phdr-driven
  segment placement, relocatable-bit rebase, hash segments packed as
  metadata) → qcom_q6v5_mss.c sequencing → PAS authentication via SCM
  into TrustZone; EFS persistence via rmtfs
  (drivers/soc/qcom/rmtfs_mem.c).
- transport: GLINK/SMEM rpmsg channels (DATA_CNTL, DATA1–27, DIAG,
  RMT) → QRTR service discovery (net/qrtr) → QMI control (QMICTL
  handshake) → rmnet/QMAP data plane
  (drivers/net/ethernet/qualcomm/rmnet).
- test hooks: MDT phdr parse + relocation math identical to
  qcom_mdt_load_no_init; QRTR service enumeration; QMICTL byte
  round-trip; QMAP header codec; synthetic rmtfs block device.

Scope note (honest): the blob-side Hexagon command vocabulary (the
modem's internal handlers) is not covered — that needs Hexagon
disassembly capacity, same lever as the lab's I-4 item. The doc
states this rather than guessing.

Interface doc:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-cellular.md
Modem/wpss blob census (sizes, hashes, ISA):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/results/census.md
```

### Q-3 — issue #26 ("Document the CopyEngine API")

Post this on #26:

```markdown
CopyEngine interface note from mainline ath11k (the CE is ath11k's
DMA path) — one correction to the premise plus the API facts:

- the CopyEngine is a set of per-service descriptor rings (up to 12
  pipes, CE_COUNT_MAX), not a single 8-buffer ring: each pipe has a
  source and/or destination ring with per-target depths (e.g.
  ipq8074: CE0 HTC control 16 src / 2048 max, CE1 HTT+HTC 512 dest,
  CE2 WMI 512 dest, CE3 WMI mac0 32 src, CE4 HTT 2048 src/256 max
  with interrupts disabled, CE5 pktlog 512, CE6/CE8 hif_memcpy,
  CE7/CE9 WMI mac1/2, CE10 HTT 512 dest, CE11 unused) —
  drivers/net/wireless/ath/ath11k/ce.c.
- the host↔blob contract is literally a mainline struct flagged
  "Structure is shared between Host software and Target firmware!":
  struct ce_pipe_config {pipenum, pipedir, nentries, nbytes_max,
  flags, reserved} — passed to the target through a QMI message
  during startup, one per CE (drivers/net/wireless/ath/ath11k/hw.c,
  ath11k_target_ce_config_wlan_*). A re-implementation must accept
  this configuration and service the mapped pipes (service_to_pipe).
- send/recv model: ath11k_ce_send(skb, pipe_id, transfer_id);
  pre-posted dest rings with recv_cb/send_cb completion callbacks;
  ring wraparound via CE_RING_IDX_INCR.
- the WMI/HTT command processing after CE delivery on this exact
  firmware is documented separately (registry of 225 records / 149
  IDs / 61 decoded events).

Interface doc:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-copyengine.md
WMI dispatch spec (firmware side):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/papers/wmi-dispatch-architecture.md
```

### Q-4 — issue #37 ("Figure out which WPSS blob is the PCIe bridge")

Post this on #37:

```markdown
Research note from the FP6 census + public trees — the framing
changes the question usefully:

- there is no second WPSS blob that could be "the bridge": wpss is
  one Hexagon MDT image (wpss.mdt + b00–b12, executable Hexagon
  segments b01/b02/b03/b05/b06) containing one embedded ELF32 RISC-V
  executable (wpss.b07, QURT RTOS, entry 0x404000). All of it is the
  "bridge" firmware — the PCIe-style wake/doorbell semantics and the
  IPC buffers live inside this single image.
- the PCIe host presentation on Linux is software in the kernel
  vendor stack (ICNSS2/IPCI platform layer + MHI), matching your own
  commit b75b158f correcting the transport docs to IPCI/ICNSS2 and
  PR #58's software endpoint implementation — Android's "no PCIe
  devices" premise is exactly right: the PCIe function your lspci
  capture (Device 0x1105) sees is emulated, and the blob's firmware
  plays the endpoint peer.
- what remains open (stated honestly, not guessed): which Hexagon
  segment implements the endpoint emulator — needs disassembly of
  b01/b02/b03/b05 (Ghidra's public Hexagon module) and is on the lab
  queue; binaries referenced below by size/hash.

Census write-up (wpss segment table, sizes, hashes):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/fp6-architecture-census.md
PCIe-bridge note:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-pcie-bridge.md
```

### Q-5 — issue #39 ("What is the Gunyah hypervisor used for ?")

Post this on #39:

```markdown
Short answer from public sources + the FP6 census:

- Gunyah is Qualcomm's open-source Type-1 hypervisor ("designed for
  strong security, performance and modularity" — github.com/quic/
  gunyah-hypervisor). A Type-1 hypervisor boots before the OS: on
  your FP6 boot logs, Linux is one of its guests.
- its use on a phone: hosting protected VMs (pVMs) — isolated
  secondary VMs verified at boot — alongside the Android host. The
  FP6 OTA carries the matching partition set: pvmfw (protected-VM
  firmware, 1 MiB, AVB-verified via a vbmeta_system descriptor) plus
  the usual vbmeta plumbing.
- kernel touchpoints: mainline ships the Gunyah watchdog driver
  (drivers/watchdog/gunyah_wdt.c — SMCCC fast calls, owner
  VENDOR_HYP, functions 0x0005–0x0008, plus the public gunyah_error
  enum); the fuller VM-lifecycle driver stack is not yet in
  torvalds/master (checked 2026-11-16) and comes with vendor kernels.
- two distinctions worth keeping: (1) Gunyah (AP-side pVM hypervisor)
  vs the QURT microkernel the same chip's WPSS core runs (census
  below) — different processors, different software; (2) Gunyah vs
  the QHEE hypervisor image that ships in the same TZ build
  (hyp.img, TZ.XF.5.28.0-00021-LANAIAAAAANAZT-1) — the exact split of
  duties on shipping FP6 firmware is not establishable without
  boot-log↔image work on hardware.

Hypervisor note:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-gunyah.md
Boot-chain census (pvmfw/vbmeta_system facts):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
```

### Q-6 — issue #40 ("Resolve differences between readelf and mdt_loader.c")

Post this on #40:

```markdown
The difference is relocation, not a tooling bug — from mainline
drivers/soc/qcom/mdt_loader.c:

- readelf prints the program headers as stored in the file.
- mdt_loader.c computes post-relocation runtime addresses: if any
  loadable phdr carries QCOM_MDT_RELOCATABLE (p_flags BIT(27),
  include/linux/soc/qcom/mdt_loader.h), the loader rebases every
  loadable segment — base = the lowest stored p_paddr (min_addr),
  runtime position = mem_phys + (p_paddr - min_addr), and it reports
  reloc_base = min_addr (qcom_mdt_load_no_init). An instrumented
  loader therefore legitimately shows different numbers than readelf.
- three further filters explain most other discrepancies:
  hash segments (p_flags type bits == 2<<24) are skipped by
  mdt_phdr_loadable() and never get load addresses; zero-memsz and
  non-PT_LOAD phdrs are skipped; and qcom_mdt_bins_are_split()
  redirects payload reads to the sibling .bNN files when the phdr
  extents fall outside the .mdt.
- the PAS authentication path (qcom_pas_init_image) receives the
  un-relocated metadata, which is why signatures still validate on
  the stored layout.
- FP6 cross-check: the per-segment .bXX files carry junk ELF headers
  (zeros, even x86=3 on wpss.b08) — the .mdt phdr table is the only
  authoritative source; any tool reading a segment file in isolation
  decodes noise.

Note doc (step-by-step mechanism + test hooks):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-mdtloader-vs-readelf.md
```

### Q-7 — issues #44 and #45 ("FTM instrumentation" / "Expand the FTM doc")

Post on #44 (and reference from #45):

```markdown
Instrumentation points for the FTM/UTF channel, extending docs/ftm.md
with the where-to-hook layer list — all files verified present in the
public FP6 wlan module tree:

1. os_if/linux/ftm/src/wlan_cfg80211_ftm.c — nl80211 testmode entry
   (wrap the cmd + the rx-event pushback);
2. os_if/linux/ftm/src/wlan_ioctl_ftm.c — ioctl 0x1000/0x1001 entry;
3. ftm/dispatcher/src/wlan_ftm_ucfg_api.c — the single point where
   both user paths converge AND where responses are reassembled
   (best chokepoint for an automated test suite);
4. target_if/ftm/src/target_if_ftm.c — byte-exact capture
   immediately above wmi_unified_pdev_utf_cmd_send;
5. the WMI layer itself (format-level tracing);
6. blob side — not instrumentable without replacing segments; the
   PAS signing chain rejects any replaced segment (as PR #58's thread
   documents), and the blob's ISA map is Hexagon segments + one RV32
   QURT app image.

Custom tests without blob modification: yes — the UTF payload is
opaque end-to-end (the driver only segments/reassembles 16-byte
ftm_seg_hdr_info headers; ≤2048 B per segment), so a userspace tool
can push arbitrary payloads through nl80211 testmode or the ioctl in
FTM mode (con_mode_ftm / adb reboot ftm) and read the blob's echo.
Layer-3/4 instrumentation can also synthesize payloads in-kernel.

Doc (table + mechanics + what upstream ftm.md does not yet carry):
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-ftm-diag.md
```

For #45, post the same comment with the first line replaced by:
"For #45 — three concrete additions for docs/ftm.md (the doc below
also serves #44): the instrumentation-point table, the custom-test
mechanics, and the FTM↔CE relationship (FTM rides WMI, not the CE4
HTT data pipe)."

### Q-8 — issue #46 ("How to use QMMI or Diag Mode from a host computer")

Post this on #46:

```markdown
Literature survey from public sources — separating the two things
called "diag/QMMI", with one honest gap:

DIAG (the wire protocol — partially public):
- on-device enablement is public: USB function composition (e.g.
  setprop sys.usb.config diag,diag_mdm,qdss,serial_cdev,dpl,rmnet,adb
  — the same composition string docs/ftm.md already records) or
  engineering menus (*#*#4636#*#*).
- the on-device driver is public Qualcomm code (drivers/char/diag/*
  in public msm kernel trees) — note it is NOT in the FP6 GKI kernel
  tree itself (probed, 404).
- the host protocol is framed around 0x4B-prefixed commands and log
  packets; there is no canonical vendor spec, but community tools
  implement it (e.g. github.com/Alephgsm/qualcomm-diag-protocol).
  On modern devices the log data also flows over GLINK DIAG/DPL
  channels internally.

QMMI (the factory test harness — not public):
- it is an on-device test application (com.qualcomm.qti.qmmi in
  public vendor trees), reachable via boot modes/dial codes; its
  host-side exchange is not documented anywhere public I could find
  (searched 2026-11-16). Documenting it needs a capture on hardware —
  I've listed exactly what a first capture should record (USB
  descriptors, one DIAG command family at a time, adb-forwarded
  QMMI sockets first).

Survey doc:
https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/interface-qmmi-diag.md
```

---

## L-2 — issue #33's remaining unidentified libraries: BLOCKED-WITH-PLAN

Status check against committed artifacts (2026-11-16): the lab holds
only what `trustzone-census.md` + `results/census.md` /
`results/bt-tz-census.json` recorded — sizes/hashes/ELF-class for all
16, plus identifications for 8 (soter64, smplap64, featenabler,
05B04A44, FD719D50, 32552B22-honest-negative, evautil64 AArch64-only,
hdcp family as DRM-excluded). The function of **7 libraries remains
unidentified — focal64, ic5, loadalgota64, ops, sp_license, winsecap,
evautil64** (the audit's "8" counts the hdcp trio as one
unidentified-by-function family) — and identification requires the
**binary tree, which is not on this box** (the 2026-11-09/10
extraction workspace was cleaned; only docs/results/tools are
committed). Per the rules, results are NOT faked; this section is the
exact re-fetch + method plan, ready to paste into
librephone-wants.md row A-9's next-action cell.

**Plan (F-32 method — the EVROS identification method: full strings
census + public-tree cross-reference):**

1. **Re-fetch** (tooling already committed):
   `tools/payload_dump.py payload.bin modem modem.img` →
   `tools/extract_vfat.py modem.img trees/modem` (TA payloads are in
   `modem/image/*.mdt/.bXX` — sizes/hashes in results/census.md
   identify them; re-hashing validates byte-identity against the
   committed 16-hex values).
2. **Deep strings pass per library** (focal64, ic5, loadalgota64, ops,
   sp_license, winsecap, evautil64): lower the threshold from ≥8 to
   ≥4 chars, keep symbol-ish tokens (GUIDs, filenames, registry keys,
   error templates); commit per-lib strings tables next to
   `wpss.b07.strings.txt` (same format). 32552B22's ≥8-char negative
   gets one 4-char confirmation pass to either keep or retire the
   honest negative.
3. **Cross-reference against public trees** (the step that identified
   EVROS): sm7635-modules `securemsm-kernel` / `spu-kernel` (public
   FP6 module tree), Qualcomm TEE client literature (GlobalPlatform
   TEE APIs), public Android vendor dumps — match string tokens, not
   vibes. Each hit records the exact public file + token.
4. **Candidate hypotheses to verify or retire** (candidates-not-claims
   — from name shape only, all unverified): focal64 ↔ FocalTech/
   fingerprint-family TA (focal = touch controller vendor name);
   winsecap ↔ Widevine/secure-camera-licensing family; ops ↔
   operations/OTA-provisioning TA; ic5 ↔ image-cam-5 pipeline TA;
   loadalgota64 ↔ OTA load-algorithm companion of cdsp's
   libloadalgo_skel.so (same "loadalgo" token, dsp-cdsp census row);
   sp_license ↔ vendor licensing (sibling of featenabler). None of
   these is a claim — each is a token to check in step 3.
5. **Deliverable shape**: extend `trustzone-census.md` with a
   per-library section; append a Q-9 comment to this package updating
   the C-3 partial identification for issue #33.

**What this session contributed instead:** the want is now scoped
honestly — 7 named targets, a reproducible method, committed
size/hash anchors — so the next session with the binaries lands
identifications, not re-planning. (The librephone-wants.md matrix
cell itself is owner-editable only under this session's file wall; the
plan text above is the paste-ready cell content.)
