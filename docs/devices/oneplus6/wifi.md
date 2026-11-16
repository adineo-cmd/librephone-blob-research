# OnePlus 6 (enchilada) — WiFi family

**Evidence class: census-negative** (the interesting result is what is absent).
Source: LineageOS 22.2 nightly 2026-11-11 enchilada, `/vendor/firmware/wlan/qca_cld/`.

## What is actually in the vendor image

| file | bytes | note |
|---|---|---|
| `WCNSS_qcom_cfg.ini` | 0 | zero bytes in this build |
| `wlan_mac.bin` | 0 | zero bytes in this build |

Both zero-byte: the A/B OTA carries no WLAN calibration/config payload for
this chip. No `qca_cld` board files, no `bdwlan`, no `amss.bin` in the
vendor filesystem.

## Where the WLAN firmware really is

SDM845's WiFi is the integrated WCN3990; its firmware image (`wlanmdsp.mbn`
per the Qualcomm partition naming) ships inside the `modem` partition image,
not as a standalone vendor file. This mirrors the upstream DB's
mislabeling class (recon.md finding 4: `a660_sqe.fw` typed AUDIO,
`bm2nXX.bin` typed MODEM) — on enchilada the entire wifi family is
structurally hidden inside the modem partition. Verification requires
parsing modem.img (open item; see [modem.md](modem.md)).

## Interface facts

Consumer: mainline `ath10k`-successor `ath11k` does NOT cover WCN3990
(sdm845 uses `ath10k`-SNOC per public kernel history — WCN3990 support
landed in ath10k via the snoc bus). Calibration data absent here is
consistent with runtime provisioning.

## Open questions

- confirm `wlanmdsp` presence inside modem.img
- zero-byte `WCNSS_qcom_cfg.ini`: generated at runtime by the driver?
