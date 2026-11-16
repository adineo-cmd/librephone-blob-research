# htt — open item (no implementation)

HTT message-layout facts are NOT spec'd anywhere in the lab's published
documents: the WMI dispatch paper covers WMI dispatch only; the CE/HTC notes
cover the transport, not the HTT payload. The wpss.b10 trace table names HTT
85 times (F-22) but contains no message layout.

Per the clean-room rule ("never guess beyond the spec"), no HTT codec is
implemented here. This README is the honest gap marker.

Next levers, in spec-source order:
1. mainline ath11k HTT structures (GPL public) — a fetchable spec source for
   host-side message layouts; a future component can derive from them with
   the same provenance discipline as wmi/tlv and htc/frame-layer. (The two
   fetch attempts this session failed: raw.githubusercontent 404 + rate
   limit, kernel.org path returned a directory page — the ath11k HTT header
   path needs locating first.)
2. PR #58's payload defines the transport it needs (PCIe endpoint + MHI
   slave + QRTR); HTT-over-CE frames are what its author lists as missing.
3. The lab's CE interface note section 3 sketches the emulated-blob test
   shape this component should plug into.

RULE 0 note (2026-11-16): searches above; no existing open implementation of
HTT for WCN6750 found.
