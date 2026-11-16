# OnePlus 6 (enchilada) — Modem family

**Evidence class: census** (partition extracted + hashed; container not parsed).
Source: LineageOS 22.2 nightly 2026-11-11 enchilada, OTA payload partition
`modem` → `modem.img` (119,820,288 B, magic raw, sha256 in the matrix CSV).
52 REPLACE_XZ + 5 REPLACE_BZ + 1 REPLACE ops reconstructed it from the OTA.

## Container layout

Single raw partition image (SDM845 modem PIL image; expected to unpack to
`mpss`-style MDT + `.bNN` segments — the lab's FP6 modem work found the
same pattern upstream). Not parsed this session.

## Fragmentation significance

modem is the largest byte-weighted family across the whole matrix
(25.94 GB of 69.80 GB). Every SDM845-generation device in the half shares
this shape. The lab's FP6 modem findings (F-19/F-26: b23/b24 segments,
q6zip-suspected 38.9 MB opaque body) give the method: unpack MDT segments,
then constant-xref with negative controls.

## ISA/proof status

Not decoded (ISA unknown, not knowable-now without the unpack pass).
The lab's Hexagon decode recipe (papers/wmi-dispatch-architecture.md §6)
applies directly once unpacked.

## Interface facts

Consumers: QRTR/DIAG/Peripherial-image loader (mainline `qcom_q6v5_mss`
PIL driver loads this partition on sdm845 — public code); QMI/RIL above.
Also expected inside: the WCN3990 WLAN firmware (`wlanmdsp`) — see
[wifi.md](wifi.md).

## Open questions

- MDT segment map of this build
- q6zip-suspected compressed bodies (F-26 method)
- WLAN firmware location verification
