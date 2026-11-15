# CopyEngine (CE) API — ath11k's DMA path to the WCN6750 blob — for upstream issue #26

One-page interface note from **public data only**
([upstream issue #26](https://codeberg.org/rsavoye/librephone/issues/26):
"ring of 8 buffers used to contain the commands from the HIF/HTT layer
to the binary blob"). Written 2026-11-16. Issue text points at the
public FP6 tree
`kernel/fairphone/sm7635-modules/qcom/opensource/wlan/` — mirrored at
`github.com/LineageOS/android_kernel_fairphone_sm7635-modules`
(accessed 2026-11-16, path verified).

**Legend:** [PUBLIC] = mainline kernel / public tree fact; [LAB] =
lab-derived fact; [OPEN] = needs data not available here.

## 1. What the CopyEngine is

- [PUBLIC] The CopyEngine is the WLAN subsystem's DMA engine: fixed
  number of pipes (mainline `CE_COUNT_MAX = 12`), each pipe a
  **descriptor ring** (not a flat 8-buffer FIFO) with a source ring
  and/or destination ring per service —
  `drivers/net/wireless/ath/ath11k/ce.h` (PIPEDIR_NONE/IN/OUT/INOUT).
- [PUBLIC] The per-target host-side ring table defines each pipe's
  shape. For `ipq8074` (same CE service model; fetched 2026-11-16):
  CE0 host→target HTC control (16 src, 2048 max), CE1 target→host HTT
  + HTC (512 dest), CE2 target→host WMI (512), CE3 host→target WMI
  mac0 (32 src), CE4 host→target HTT (2048 src, 256 max, interrupts
  disabled), CE5 target→host pktlog (512), CE6/CE8 autonomous
  hif_memcpy, CE7/CE9 WMI mac1/mac2, CE10 target→host HTT (512), CE11
  unused — `drivers/net/wireless/ath/ath11k/ce.c`
  (`ath11k_host_ce_config_ipq8074/qca6390/qcn9074`). [OPEN] the
  WCN6750-specific table lives in the vendor `wlan` module (public
  tree above); mainline maps wcn6750 hw params in
  `drivers/net/wireless/ath/ath11k/hw.c` (ring masks, tcl2wbm maps).
- [PUBLIC] The **shared host↔target pipe contract** is literally a
  struct in mainline, with the in-source note *"Structure is shared
  between Host software and Target firmware!"*: `struct ce_pipe_config
  { pipenum; pipedir; nentries; nbytes_max; flags; reserved }`, passed
  to the target **through a QMI message during startup, one per CE** —
  `drivers/net/wireless/ath/ath11k/hw.c`
  (`ath11k_target_ce_config_wlan_*`). This is the anchor for any
  re-implementation: the blob learns its CE configuration at boot from
  these 24-byte descriptors.
- [PUBLIC] Service→pipe mapping (`struct service_to_pipe`) ties each
  service (HTC/HTT/WMI/...) to (src CE, dst CE) pairs; send path
  `ath11k_ce_send(ab, skb, pipe_id, transfer_id)`; per-pipe callbacks
  `send_cb`/`recv_cb` in `struct ce_attr` — `ce.h`/`ce.c`.

## 2. Command flow HIF/HTT → blob

1. [PUBLIC] HTT/WMI layer hands an skb to HIF → `ath11k_ce_send` on
   the service's src ring; descriptor written, doorbell register
   updated; completion via interrupt/polling (`send_cb`).
2. [PUBLIC] Target→host: dest ring pre-posted with receive buffers
   (src_nentries = 0, dest_nentries = N in the config table);
   `recv_cb` delivers each completed buffer to HTC/HTT/WMI.
3. [LAB] On the blob side, the same WMI events/registry the lab
   decoded in the WMI dispatch paper apply: the WCN6750 image's
   dispatch layer routes the CE-delivered WMI commands —
   `papers/wmi-dispatch-architecture.md` (225-record registry, 149
   IDs, 61 decoded events; first public WMI dispatch spec for this
   firmware).
4. [PUBLIC] The vendor tree implementing this for FP6:
   `qcom/opensource/wlan/` → qcacld-3.0 `core/hif/src/ce/` and
   qca-wifi-host-cmn — public, same struct layouts.

## 3. Test-suite hooks

1. Encode/decode `ce_pipe_config` + `service_to_pipe` tables and
   compare against the vendor table for wcn6750 (public tree) — pure
   struct-level, no hardware.
2. Ring arithmetic: wraparound via `CE_RING_IDX_INCR(nentries_mask,
   idx)` semantics; descriptor size/format from
   `ath11k_ce_ring` usage.
3. Emulated blob: a userspace process that speaks the CE service
   model (QMI-shaped startup config + HTC/HTT/WMI frames on the
   mapped pipes) — the exact shape of upstream PR #58's payload
   approach (which deliberately stops short of CE/WMI/HTT — the gap
   this doc + the WMI paper fill).

## Sources consulted (accessed 2026-11-16)

- mainline: `drivers/net/wireless/ath/ath11k/ce.c` (fetched, 1079
  lines), `ce.h` (fetched), `hw.c` (fetched; quoted note verbatim)
- public FP6 vendor tree:
  `github.com/LineageOS/android_kernel_fairphone_sm7635-modules` path
  `qcom/opensource/wlan` (exists; FTM sibling files fetched OK)
- lab: `papers/wmi-dispatch-architecture.md` (lab-original spec)

**Clean-room statement:** public-kernel struct/service facts +
lab-derived WMI registry facts. No decompiled blob code.
