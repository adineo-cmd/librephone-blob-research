# OnePlus 6 (enchilada) — WiFi family

**Evidence class: format-spec** (RESOLVED 2026-11-17 — the census-negative
finding is confirmed AND resolved; bdwlan container format decoded).
Source: LineageOS 22.2 nightly 2026-11-11 enchilada, partition `modem`.

## What is actually in the vendor image

| file | bytes | note |
|---|---|---|
| `WCNSS_qcom_cfg.ini` | 0 | zero bytes in this build |
| `wlan_mac.bin` | 0 | zero bytes in this build |

Both zero-byte: the A/B OTA vendor tree carries no WLAN calibration/config
payload for this chip.

## Where the WLAN firmware really is (RESOLVED 2026-11-17)

`modem.img` is a FAT16 volume (same layout family as `bt.img`) whose
`IMAGE` directory carries 404 named firmware files — including
**`image_wlanmdsp.mbn` (3,035,876 B, md5 `771a9c2e…90df5`)**, the
WCN3990 WLAN firmware, plus a **35-file** `image_bdwlan.*` board-data set
(19,152 B each). The hypothesis below is confirmed and upgraded to fact.

SDM845's WiFi is the integrated WCN3990; its firmware image ships inside
the `modem` partition's FAT tree, not as a standalone vendor file. This
mirrors the upstream DB's mislabeling class (recon.md finding 4:
`a660_sqe.fw` typed AUDIO, `bm2nXX.bin` typed MODEM) — on enchilada the
entire wifi family is structurally hidden inside the modem partition.

## Board-data format (decoded 2026-11-17)

The `bdwlan.*` container is a **flat TLV chain** (`{u16 LE tag, u16 LE len,
payload}` to EOF, no outer magic): 34 files carry 17 strictly sequential
IEs (tags 1..17; `b38` re-chunks the tail into 18), chain sums to exactly
19,152 on every file, IE-1 payload self-references the file size. Distinct
from ath10k `board-2.bin` (32-bit IEs). Variability map: 4,199/19,152 bytes
vary, 28 disjoint regions over 12 IEs, stride-40 and stride-4 record tables
identified, per-board ID fields at abs [10,12) (28 values) and [408,410)
(3 values); **29 md5 clusters** with minimal-diff pairs (2 bytes). Full
spec: [../../blob-matrix/desktop/fleet-re/bdwlan-format.md]
(../../blob-matrix/desktop/fleet-re/bdwlan-format.md).

## Interface facts

Consumers: WCN3990 support is in mainline `ath10k` via the SNOC bus;
`bdwlan.*` board files are the per-board calibration variants the firmware
selects from (board-ID keyed). No interface doc committed yet.

## Open questions

- tag 1..17 semantics (needs a Qualcomm BDF tool/spec — none public)
- board-ID field decode vs the cnss loader (28 values ≠ filename numbers)
- zero-byte `WCNSS_qcom_cfg.ini`: generated at runtime by the driver?
