# Bluetooth driver ↔ blob interface (Fairphone FP6, WCN6750) — for upstream issue #15

One-page interface doc, API-doc style as the issue requests ("will be
turned into a test suite"). Written 2026-11-16 for
[upstream issue #15](https://codeberg.org/rsavoye/librephone/issues/15)
(High Priority). Companion to the lab's
[bt-firmware-census.md](bt-firmware-census.md) — that doc is the
blob-side census (container formats, headers, hashes); this doc is the
driver↔blob contract itself.

**Legend:** [PUBLIC] = public-kernel fact, source cited; [LAB] =
lab-derived fact from committed censuses; [OPEN] = not establishable
from data available to this box.

## 1. What the "blob" is on this device

- [LAB] The FP6 ships its BT firmware family in the dedicated
  `bluetooth` OTA partition — a FAT16 filesystem holding two generations
  of Moselle (WCN6750) rampatch (msbtfw11/msbtfw12 as `.mbn` ELF +
  `.tlv` container + `.ver` + NVM `.bin`) **plus a third "EVROS" family
  (evrbtfw20.tlv / evrnv20.bin) that mainline Linux cannot name or
  select**. Full inventory with sizes/sha256 in
  [bt-firmware-census.md](bt-firmware-census.md).
- [LAB] Both `.mbn` rampatches are ELF32 **e_machine = 40 (EM_ARM)**,
  e_type EXEC, entry = LOAD vaddr | 1 → **ARM Thumb entry point**. The
  WCN6750's WLAN core (wpss) on the same chip is 32-bit RISC-V running
  QURT — BT and WLAN firmware are different ISAs on this SoC (first
  public identification, per the architecture census).
- [LAB] linux-firmware carries msbtfw11/msnv11 at *different sizes*
  than the FP6 builds (different builds), and **no msbtfw12 and no
  evr\* files at all** — checked 2026-11-10 against the linux-firmware
  tree listing.

## 2. Driver ↔ blob interface, layer by layer

All [PUBLIC] anchors verified against `torvalds/linux` master on
2026-11-16 (files fetched; line-references below):

| layer | what crosses it | mainline anchor |
|---|---|---|
| transport | H4-style HCI byte stream over a UART (serdev); regulators + `bt_en` enable GPIO owned by `qca_serdev` | `drivers/bluetooth/hci_qca.c` (`qca_serdev`, `qca_regulator_enable`) |
| framing | standard HCI command/event packets, `hci_uart` protocol "qca" | `drivers/bluetooth/hci_uart.c`, `hci_qca.c` |
| power (runtime) | **HCI_IBS in-band sleep**: single-byte signals SLEEP_IND `0xFE`, WAKE_IND `0xFD`, WAKE_ACK `0xFC`; per-direction state machines, clock voting, retransmit timeout 100 ms, SoC TX-idle 200 ms, host TX-idle 2 s | `hci_qca.c` (`HCI_IBS_*` defines, `send_hci_ibs_cmd`, `serial_clock_vote`) |
| bring-up | soc-version read: HCI EDL opcode **0xFC00**, reply carries `soc_id` + `rom_ver` | `btqca.c` `qca_read_soc_version` (lines 16–89) |
| filename math | `rom_ver = ((soc_ver & 0x00000f00) >> 4) \| (soc_ver & 0x0000000f)` (default branch — the one WCN6750 takes) selects `qca/msbtfw%02x.mbn` | `btqca.c` lines 770–820 |
| patch download | rampatch as **ELF patch** (`ELF_TYPE_PATCH` → `dnld_mode = QCA_SKIP_EVT_VSE_CC`: segments are send-only, the driver injects a synthetic command-complete) for WCN6750's `.mbn`, with **`.tlv` fallback** (`TLV_TYPE_PATCH`, whose 32-byte header's `download_mode` field decides VSE/ack behavior) | `btqca.c` `qca_tlv_check_data` (lines 292–321), `qca_uart_setup` lines 779–855 |
| patch segmentation | HCI EDL opcode 0xFC00 + payload command **0x1E**, chunks of **243 bytes** (`MAX_SIZE_PER_TLV_SEGMENT`); the last segment is always acked regardless of mode | `btqca.h` lines 8–18, `qca_download_firmware` |
| patch-config | WCN6750-only pre-download config: EDL opcode **0xFC00** + sub-command **0x28** (`EDL_PATCH_CONFIG_CMD`), payload {0x01, 0, 0, 0} | `btqca.c` `qca_send_patch_config_cmd` (lines 154–175), called from `qca_uart_setup` line 780 |
| NVM download | `qca/msnv%02x.bin` TLV tag set; **the kernel rewrites tags in flight**: tag 2 = BD address (6 B), tag 17 (HCI) sets the in-band-sleep bit `0x80` + baud-rate byte, tag 27 (deep sleep) sets the sleep-enable mask; NVMs with multiple tag sets carry an **enclosing type-4 header** — the kernel skips to the first type-2 set | `btqca.c` `qca_tlv_check_data` case `TLV_TYPE_NVM` (lines 363–437); `EDL_TAG_ID_*` in `btqca.h` |
| speed | baudrate change: vendor opcode **0xFC48**, single parameter; WCN6750-family settle wait 1–10 ms | `hci_qca.c` `qca_set_baudrate` (lines 1347–1397) |
| post-setup | disable SOC logging; Microsoft vendor extension opcode **0xFD70**; HCI reset; fw-build-info query; BD-address check (quirk `HCI_QUIRK_USE_BDADDR_PROPERTY` when the controller address equals the NVM address) | `btqca.c` lines 940–1010 |
| crash path | memdump trigger byte `0xFB` + coredump trigger via opcode **0xFC0C** (param 0x26); SSR timeouts sized around FW-download + memdump windows | `hci_qca.c` `hci_coredump_qca` (lines 1889–1897), `qca_controller_memdump`, lines 71–55 |

## 3. Blob-side facts the driver source alone does not show ([LAB])

- **The kernel's filename math reproduces the shipped filenames** from
  the shipped binaries' headers: TLV field `rom_build` = 0x0101 →
  17 → msbtfw11; 0x0102 → 18 → msbtfw12; 0x0200 → 32 → evrbtfw20.
  First time shown numerically against real firmware (census doc,
  "rom_build → filename" table).
- The shipped TLV headers carry `download_mode = 3` =
  `QCA_SKIP_EVT_VSE_CC` — the value the kernel also hard-forces for
  ELF patches, i.e. FP6's controller acks only the last patch segment
  in both container flavors.
- The `.mbn` and `.tlv` are the same payload in two containers: the
  TLV `entry` field equals the ELF entry minus the Thumb bit
  (0x24c50↔0x24c51; 0x23dc4↔0x23dc5) — verified numerically.
- **Container-length delta:** the vendor TLV patch header carries 12
  extra bytes of reserved fields (on-device header is 32 bytes before
  data, entry at offset 0x24) vs upstream's 24-byte
  `struct tlv_type_patch` — a re-implementation should decode
  accordingly.
- NVM tag 1 (64 B) is the firmware version string (e.g.
  `BTFW.MOSELLE.1.1.2-00064-PATCHZ-2`); tag 2 is the BD-address slot
  the Android vendor HAL (`PatchDLManager::ReadTlvInfo`) writes before
  download. The EVROS NVM carries an outer **type-4** enclosing TLV
  plus 903 trailing bytes — the vendor HAL's multi-NVM
  (`TLV_TYPE_BT_FM_NVM`) unwrap path, of which the kernel implements
  only the skip-to-first-set part.
- **The EVROS gap:** no `evr` string exists anywhere in upstream
  `btqca.c`/`hci_qca.c`; linux-firmware has no evr\* files; the
  consumer of `evrbtfw20.tlv` is Qualcomm's Android vendor BT HAL,
  which selects patch paths from a chipset-version table not public.
  [OPEN] Which chip EVROS (product_id 29) is; flagged in the census
  doc as needing the HAL's map or a named verinfo dump.

## 4. Test-suite hooks (the issue's stated end goal)

1. **Filename math** — feed real `rom_build` values (0x0101/0x0102/
   0x0200) through the kernel's formula and assert the msbtfw11/12/
   evrbtfw20 outputs; negative case: EVROS has no kernel consumer.
2. **Version round trip** — 0xFC00 soc-version read/parse
   (`qca_btsoc_version` fields), then the rom_ver branch selection.
3. **Patch segmentation** — 243-byte chunking + last-segment-acked
   semantics for each `download_mode` (NONE/VSE/CC/VSE_CC); ELF-patch
   synthetic-CC injection path.
4. **NVM rewrite determinism** — tag 17 in-band-sleep bit + baud byte,
   tag 27 mask, tag 2 BD-address passthrough; multi-set type-4 unwrap
   (and the documented 32-byte on-device header delta).
5. **IBS state machine** — 0xFE/0xFD/0xFC sequences under the four
   timeout constants; clock-vote counters.
6. **Blob-side validation** — every downloaded file is checkable
   without a device: ELF32/Thumb entry math for `.mbn`, TLV
   type/length/entry decode against the committed header tables
   (`results/bt-tz-census.json`).

## Sources consulted (accessed 2026-11-16 unless noted; network flaky — status recorded)

- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/btqca.c (fetched, 1,032 lines — opcodes, modes, filename math quoted above)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/hci_qca.c (fetched, 2,855 lines — IBS, baudrate, memdump, patch-config)
- https://raw.githubusercontent.com/torvalds/linux/master/drivers/bluetooth/btqca.h (fetched — EDL constants, tag IDs, soc-type enum incl. QCA_WCN6750)
- Lab: `qualcomm-fp6/docs/bt-firmware-census.md` (blob census, prior art + hashes), `qualcomm-fp6/results/bt-tz-census.json` (full header decode)
- Concurrency note: the lab's QCA-BT clean-room implementation stream (from the lab's published BT specs) runs in a separate session; if/when committed under `implementations/`, its service-side stubs are the test-suite's second half.

**Clean-room statement:** public-kernel facts + lab census facts only;
no proprietary content, no decompiled code, no firmware bytes
redistributed.
