# NFC driver ↔ blob interface (Fairphone FP6) — for upstream issue #17

One-page interface note, built **from public data only** (issue bodies,
mainline kernel sources, public kernel trees). Written 2026-11-16 for
[upstream issue #17](https://codeberg.org/rsavoye/librephone/issues/17)
("Document the interface between the NFC driver and the blob", in an
API-doc style so it can later become a test suite).

**Legend:** [PUBLIC] = public-kernel/standard fact with source; [LAB] =
lab-derived fact with committed doc; [OPEN] = not establishable from
data available here.

## 1. What the "blob" is on this device

- [PUBLIC] The FP6 public kernel tree
  (`github.com/LineageOS/android_kernel_fairphone_SM7635`, accessed
  2026-11-16) carries only the standard mainline `drivers/nfc/` set
  (`nxp-nci`, `pn533`, `st-nci`, `st21nfca`, `s3fwrn5`, ...), and the
  vendor module tree
  (`android_kernel_fairphone_sm7635-modules`, `qcom/opensource/`,
  accessed 2026-11-16) has **no** NFC module directory — the NFC stack
  is in-kernel driver + Android userspace HAL (`libnfc-nci`).
- [LAB] The lab's committed FP6 census (modem/vendor/dsp trees, 665
  files) contains **no NFC firmware image file**
  (`qualcomm-fp6/results/census.md`, 2026-11-15). The NFC firmware
  therefore ships either inside the NFC controller (OTP/flash) or is
  fetched by the HAL from a path outside the censused partitions.
- [OPEN] The exact NFC controller part on FP6 (NXP SN100 family vs
  other) is not stated in any data available to this box; the
  `nxp-nci` driver below documents the corresponding interface.

## 2. The driver ↔ controller interface, layer by layer

All anchorable in mainline (`torvalds/linux`, accessed 2026-11-16):

| layer | what crosses it | mainline anchor |
|---|---|---|
| transport | I2C/SPI byte stream to the NFC controller | `drivers/nfc/nxp-nci/i2c.c` (phy `set_mode` cold/NCI) |
| framing | **NCI** packets: 3-byte control header (MT/PBF/GID-OID) + payload; NXP variant uses a 4-byte header (`NXP_NCI_HDR_LEN = 4`) | `include/net/nfc/nci.h`, `net/nfc/nci/` core; `drivers/nfc/nxp-nci/core.c` |
| boot mode | controller cold start → FW-download mode → NCI mode (`NXP_NCI_MODE_COLD` → `NXP_NCI_MODE_NCI`) | `drivers/nfc/nxp-nci/core.c` (`nxp_nci_reset`, mode switching) |
| firmware download | the driver↔blob protocol itself — command set `0xF0 RESET`, `0xF1 GETVERSION`, `0xE0 CHECKINTEGRITY`, `0xC0 WRITE` (chunked, `NXP_NCI_FW_CHUNK_FLAG 0x0400`), `0xA2 READ`, `0xF2 GETSESSIONSTATE`, `0xA7 LOG`, `0xD0 FORCE`, `0xF4 GET_DIE_ID`; result codes (`NXP_NCI_FW_RESULT_OK = 0x00` ...); 30 s answer timeout | `drivers/nfc/nxp-nci/firmware.c` |
| runtime ops | NCI core: CORE_RESET/CORE_INIT/CORE_SET_CONFIG, RF discovery, NFCEE management — NFC Forum NCI specification (public standard) | `net/nfc/nci/`, NFC Forum NCI spec |
| userspace | generic NFC netlink/family API to the HAL | `include/uapi/linux/nfc.h`, `net/nfc/netlink.c` |

## 3. What a free re-implementation must provide (test-suite hooks)

1. Bring-up: probe → cold/NCI mode switch → `0xF1 GETVERSION` answer
   parse → NCI `CORE_RESET`/`CORE_INIT` round trip.
2. Firmware path: `0xF0` → `0xC0` WRITE chunk loop with integrity
   check → session-state query; must tolerate the 30 s timeout window.
3. Data plane: NCI data-connection open, RF interface activation,
   ISO-DEP exchange — assertable with a virtual NCI device
   (`drivers/nfc/virtual_ncidev.c` exists in mainline for exactly this
   kind of testing).
4. Config surface: `WCNSS_qcom_cfg.ini`-style runtime knobs do not
   apply to NFC (that is WLAN); NFC config is NCI SET_CONFIG + HAL
   params. [OPEN] FP6-specific HAL parameters not extractable here.

## Sources consulted (accessed 2026-11-16; network flaky, all fetched OK)

- https://raw.githubusercontent.com/torvalds/linux/master/drivers/nfc/nxp-nci/core.c and `firmware.c` (fetched; command IDs quoted above)
- https://api.github.com/repos/torvalds/linux/contents/drivers/nfc (directory listing)
- https://api.github.com/repos/LineageOS/android_kernel_fairphone_sm7635-modules/contents/qcom/opensource (no NFC module)
- https://api.github.com/repos/LineageOS/android_kernel_fairphone_SM7635/contents/drivers/nfc (mainline-equivalent set present)
- Lab: `qualcomm-fp6/results/census.md` (no NFC firmware file in the censused trees)

**Clean-room statement:** everything above is public-kernel/standard
material plus lab census negatives; no proprietary content, no
decompiled code. The FP6 controller identity and any FP6-specific
firmware file are flagged [OPEN] rather than guessed.
