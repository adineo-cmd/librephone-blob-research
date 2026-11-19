# Bluetooth driver ↔ blob interface (Fairphone FP6, QCM6490 / WCN6750) — for upstream issue #15

One-page interface doc, API-doc style as upstream issue #15 requests
("Document the interface between the Bluetooth driver and the blob"; the
issue says the doc "will be turned into a test suite"). Written
2026-11-17. Companion to the lab's
[bt-firmware-census.md](bt-firmware-census.md) — that doc is the
blob-side census (containers, headers, hashes, prior-art audit); this
doc is the driver↔blob contract itself: **what the driver expects from
the blob side**, byte-level.

**Legend:** [PUBLIC] = public-kernel fact, verified against
`torvalds/linux` master files fetched 2026-11-17 (fetch log below);
[LAB] = lab-derived fact from committed censuses; [OPEN] = not
establishable from data available to this box.

## 1. What the "blob" is on this device

- [LAB] The FP6's BT firmware family ships in a dedicated `bluetooth`
  OTA partition — a FAT16 filesystem (864,256 B) with 11 files forming
  **three firmware families**: two Moselle (WCN6750) rampatch
  generations (msbtfw11 / msbtfw12, each as `.mbn` ELF + `.tlv`
  container + `.ver` + NVM `.bin`) plus a third "EVROS" family
  (evrbtfw20.tlv / evrnv20.bin / .ver) **that the mainline stack cannot
  name or select** (no `evr` string anywhere in btqca.c/hci_qca.c; no
  evr files in linux-firmware). Full inventory + hashes:
  [bt-firmware-census.md](bt-firmware-census.md).
- [LAB] Both `.mbn` rampatches are ELF32 **e_machine = 40 (EM_ARM)**,
  e_type EXEC, entry = LOAD vaddr | 1 → **ARM Thumb entry**. The same
  chip's WLAN core (wpss) is 32-bit RISC-V running QURT — BT and WLAN
  firmware are different ISAs on this SoC (first public identification,
  per the architecture census).
- [LAB] linux-firmware carries msbtfw11/msnv11 at *different sizes*
  than the FP6 builds (different builds) and **no msbtfw12 and no
  evr\* files** (checked 2026-11-10 against the linux-firmware tree
  listing).

## 2. The interface boundary, layer by layer ([PUBLIC] unless noted)

All mainline anchors verified against `torvalds/linux` master on
2026-11-17 (btqca.c 1,032 lines; hci_qca.c 2,855 lines; btqca.h 205
lines — fetch log in §6):

| layer | what crosses it | mainline anchor |
|---|---|---|
| transport | H4-style HCI byte stream over a UART (serdev); regulators + `bt_en` GPIO owned by `qca_serdev` | `drivers/bluetooth/hci_qca.c` (`qca_serdev`, `qca_regulator_enable`) |
| framing | standard HCI command/event packets; `hci_uart` protocol "qca" | `hci_uart.c` + `hci_qca.c` |
| power (runtime) | **HCI_IBS in-band sleep**: single-byte signals SLEEP_IND `0xFE`, WAKE_IND `0xFD`, WAKE_ACK `0xFC`; per-direction state machines, clock voting; wake-retransmit 100 ms, SoC TX-idle 200 ms, host TX-idle 2,000 ms (`HCI_IBS_*` defines, hci_qca.c lines 44–51) | `hci_qca.c` (`send_hci_ibs_cmd`, `serial_clock_vote`) |
| bring-up | soc-version read: HCI EDL opcode **0xFC00** carrying sub-command 0x19 (`EDL_PATCH_VER_REQ_CMD`); the vendor-event reply carries `soc_id` + `rom_ver` (`qca_btsoc_version` fields) | `btqca.c` `qca_read_soc_version` (lines 16–89); `btqca.h` line 8/14 |
| filename math | `rom_ver = ((soc_ver & 0x00000f00) >> 4) \| (soc_ver & 0x0000000f)` — the default branch, the one WCN6750 takes (WCN3988/WCN3998 have their own shifts) | `btqca.c` `qca_uart_setup` lines 767–780 |
| patch container selection | WCN6750: **ELF patch preferred** — `qca/msbtfw%02x.mbn` with `ELF_TYPE_PATCH`, which the kernel hard-forces to `dnld_mode = QCA_SKIP_EVT_VSE_CC` (segments send-only, driver injects a synthetic command-complete); **`.tlv` fallback** `qca/msbtfw%02x.tlv` (`TLV_TYPE_PATCH`), whose own 32-byte header's `download_mode` field then decides VSE/ack behavior | `btqca.c` lines 780–800 + `qca_tlv_check_data` (lines 292–348); `btqca.h` `TLV_TYPE_PATCH=1` |
| patch-config preamble | **WCN6750-only** pre-download config: EDL opcode 0xFC00 + sub-command **0x28** (`EDL_PATCH_CONFIG_CMD`), payload `{0x01, 0, 0, 0}`; response checked against `EDL_PATCH_CONFIG_RES_EVT` | `btqca.c` `qca_send_patch_config_cmd` (lines 154–179), called from `qca_uart_setup` line 782 |
| patch segmentation | sub-command **0x1E** (`EDL_PATCH_TLV_REQ_CMD`), chunks of **243 bytes** (`MAX_SIZE_PER_TLV_SEGMENT`, btqca.h line 18); in `QCA_SKIP_EVT_VSE_CC`/`QCA_SKIP_EVT_VSE` modes segments go via `__hci_cmd_send` (no event wait); the final short segment is always acked | `btqca.c` `qca_tlv_send_segment` / `qca_download_firmware` (lines 462–640) |
| NVM download | `qca/msnv%02x.bin`, a TLV tag set (`tlv_type_nvm`); **the driver rewrites three tags in flight**: tag 2 (BD address, 6 B, from `bdaddr`), tag 17 (`EDL_TAG_ID_HCI`: sets the in-band-sleep bit `0x80` + the baud-rate byte), tag 27 (`EDL_TAG_ID_DEEP_SLEEP`: sleep-enable mask) — everything else passes through verbatim | `btqca.c` `qca_tlv_check_data` case `TLV_TYPE_NVM` (lines 363–437); `btqca.h` lines 32–34 |
| multi-set NVM | NVM files with an **enclosing type-4 TLV header** (multiple tag sets in one file): the kernel skips to the first type-2 set and downloads only that one | `btqca.c` lines 336–362 |
| speed | baudrate change: HCI vendor opcode **0xFC48**, single parameter byte (the `qca_baudrate` enum value); WCN6750-family settle wait before the host side re-programs the UART | `hci_qca.c` `qca_set_baudrate` (lines 1347–1397: cmd `{0x01, 0x48, 0xFC, 0x01, baud}`) |
| post-setup | disable SOC logging (`QCA_DISABLE_LOGGING` 0xFC17 / sub-op 0x14); Microsoft vendor extension opcode **0xFD70** (explicitly enabled for WCN399x + WCN6750, btqca.c lines 959–969); HCI reset; fw-build-info query (`EDL_GET_BUILD_INFO_CMD` 0x20); BD-address quirk `HCI_QUIRK_USE_BDADDR_PROPERTY` | `btqca.c` lines 940–1010 |
| crash path | memdump trigger byte **0xFB** (`QCA_MEMDUMP_BYTE`, hci_qca.c line 71); coredump trigger opcode **0xFC0C** (param 0x26); SSR timeouts sized around the 8 s memdump + firmware-download windows (`MEMDUMP_TIMEOUT`, `IBS_DISABLE_SSR_TIMEOUT`) | `hci_qca.c` `qca_controller_memdump`, `hci_coredump_qca` (lines 1889–1897) |

## 3. What the driver expects from the blob side (the contract restated)

Reading the same code from the blob's point of view — this is the part
a firmware-side re-implementation must satisfy:

1. **Answer 0xFC00/0x19 with a vendor event carrying soc_id/rom_ver**
   (WCN3991+ wrinkle: the version response may ride a command-complete
   instead of a vendor event — btqca.c's `soc_type >= QCA_WCN3991`
   branch; WCN6750 uses the vendor-event form).
2. **Accept the patch-config preamble** (0xFC00 + 0x28) before the
   first patch segment, and answer `EDL_PATCH_CONFIG_RES_EVT`.
3. **Consume 243-byte patch segments** in the 0x1E command; in
   SKIP_EVT_VSE_CC mode emit nothing per segment (the host is not
   listening) and behave as if only the final segment is acknowledged —
   the kernel injects the synthetic command-complete itself for ELF
   patches. [LAB] All three FP6 rampatch TLV headers carry
   `download_mode = 3` = `QCA_SKIP_EVT_VSE_CC`, i.e. the shipped
   controller already behaves this way in both container flavors.
4. **Take the NVM with the driver's rewrites**: the downloaded NVM is
   the file's tag set with tags 2/17/27 replaced in flight — a
   re-implementation must apply the same three substitutions, not treat
   the file as immutable. Multi-set NVMs (type-4 wrapper) are trimmed
   to the first set by the kernel.
5. **Honor the IBS byte protocol** (0xFE/0xFD/0xFC) with the timeout
   envelope above, and the 0xFC48 baudrate switch mid-setup.
6. **Surface the Microsoft extension on 0xFD70** and accept the
   logging-disable (0xFC17) and build-info (0x20) queries after setup.

## 4. Blob-side facts the driver source alone does not show ([LAB])

- **The kernel's filename math reproduces the shipped filenames** from
  the shipped binaries' own headers: TLV field `rom_build` 0x0101 →
  17 → `msbtfw11`; 0x0102 → 18 → `msbtfw12`; 0x0200 → 32 →
  `evrbtfw20`. First time shown numerically against real firmware
  (census doc, "rom_build → filename" table).
- The `.mbn` and `.tlv` are the same payload in two containers: the TLV
  `entry` field equals the ELF entry minus the Thumb bit
  (0x24c50↔0x24c51; 0x23dc4↔0x23dc5) — verified numerically.
- **Container-length delta:** the vendor TLV patch header carries 12
  extra bytes of reserved fields (on-device header is 32 bytes before
  data, entry at offset 0x24) vs upstream's 24-byte
  `struct tlv_type_patch` — a parser written only from the upstream
  struct mis-decodes the vendor containers.
- NVM tag 1 (64 B) is the firmware version string (e.g.
  `BTFW.MOSELLE.1.1.2-00064-PATCHZ-2`); tag 2 is the BD-address slot
  the Android vendor HAL (`PatchDLManager::ReadTlvInfo`) pre-fills.
  The EVROS NVM carries the outer **type-4** enclosing TLV plus 903
  trailing bytes — the vendor HAL's multi-NVM unwrap path, of which
  the kernel implements only the skip-to-first-set part.
- **The EVROS gap:** no `evr` string exists anywhere in upstream
  btqca.c/hci_qca.c (re-verified 2026-11-17); linux-firmware has no
  evr\* files; the consumer of `evrbtfw20.tlv` is Qualcomm's Android
  vendor BT HAL, which selects patch paths from a chipset-version
  table not public. [OPEN] Which chip EVROS (product_id 29) is —
  flagged in the census doc as needing the HAL's map or a named
  verinfo dump.

## 5. Test-suite hooks (the issue's stated end goal)

1. **Filename math** — feed the real `rom_build` values (0x0101/0x0102/
   0x0200) through the kernel formula; assert msbtfw11/12/evrbtfw20;
   negative case: EVROS has no kernel consumer.
2. **Version round trip** — 0xFC00 + 0x19 read/parse, then the
   rom_ver branch selection (incl. the WCN3988/WCN3998 alternate
   shifts as negative cases).
3. **Patch segmentation** — 243-byte chunking; last-segment-acked
   semantics per `download_mode` (NONE/VSE/CC/VSE_CC); the ELF-patch
   synthetic-CC injection path.
4. **NVM rewrite determinism** — tag 17 in-band-sleep bit + baud byte,
   tag 27 mask, tag 2 BD-address passthrough; type-4 multi-set unwrap;
   the 32-byte on-device header delta.
5. **IBS state machine** — 0xFE/0xFD/0xFC sequences under the 100 ms /
   200 ms / 2 s timeout constants; clock-vote counters.
6. **Blob-side validation (no device needed)** — ELF32/Thumb entry
   math for `.mbn`; TLV type/length/entry decode against the committed
   header tables (`qualcomm-fp6/results/bt-tz-census.json`).

## 6. Sources consulted (accessed 2026-11-17 unless noted; network flaky — status recorded)

- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/btqca.c — fetched OK, 1,032 lines (opcodes, modes, filename math)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/hci_qca.c — fetched OK, 2,855 lines (IBS bytes/timeouts lines 44–51, baudrate 0xFC48, memdump 0xFB/0xFC0C)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/btqca.h — fetched OK, 205 lines (EDL constants, tag IDs 2/17/27, `QCA_WCN6750` enum)
- Lab: `qualcomm-fp6/docs/bt-firmware-census.md` (blob census, prior art + hashes), `qualcomm-fp6/results/bt-tz-census.json` (full header decode)
- Related lab docs: [interface-bt.md](interface-bt.md) (companion one-pager from 2026-11-16), `blob-matrix/laptop/qualcomm-qca-bt-fleet.md` (the same families across 29 devices of the upstream DB)

**Clean-room statement:** public-kernel facts + lab census facts only;
no proprietary content, no decompiled code, no firmware bytes
redistributed.
