# OnePlus 6 (enchilada) — WiFi family

**Evidence class: format-spec** (RESOLVED 2026-11-17 — the census-negative
finding is confirmed AND resolved).
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
`IMAGE` directory carries 403 named firmware files — including
**`image_wlanmdsp.mbn` (3,035,876 B, md5 `771a9c2e…90df5`)**, the
WCN3990 WLAN firmware, plus a 37-file `image_bdwlan.*` board-data set
(19,152 B each). The hypothesis below is confirmed and upgraded to fact.

SDM845's WiFi is the integrated WCN3990; its firmware image ships inside
the `modem` partition's FAT tree, not as a standalone vendor file. This
mirrors the upstream DB's mislabeling class (recon.md finding 4:
`a660_sqe.fw` typed AUDIO, `bm2nXX.bin` typed MODEM) — on enchilada the
entire wifi family is structurally hidden inside the modem partition.

## Interface facts

Consumers: WCN3990 support is in mainline `ath10k` via the SNOC bus;
`bdwlan.*` board files are the per-board calibration variants the driver
selects from (board-ID keyed). No interface doc committed yet.

## Open questions

- `bdwlan.*` format (19,152 B fixed records; 37-variant diff = natural
  probe — see `blob-matrix/desktop/fleet-re/oneplus6-partition-map.md`
  open items)
- zero-byte `WCNSS_qcom_cfg.ini`: generated at runtime by the driver?
