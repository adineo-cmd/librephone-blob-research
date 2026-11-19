# WMI constant cross-reference: ath11k ↔ WCN6750 wpss firmware

> **Correction (2026-11-12):** The conclusion below — "the firmware
> evidently constructs IDs arithmetically (`grp << 12 | 1` at runtime)" —
> was falsified by follow-up findings (F-19, F-20, F-22). The negative
> control (adsp.b36 + ten modem segments) reproduces the profile-family
> values in unrelated firmware at equal or higher counts, so
> value-presence attributes nothing (F-19); a 100%-coverage linear-sweep
> disassembly of wpss.b07 found no ID-construction sites (F-20); and the
> wpss.mdt program headers show b07/b08 are RW data, not code, so the
> original scan never had the right instrument (F-22). The actual answer:
> WMI dispatch is **table-driven** — the message-ID registry lives in
> `wpss.b09` (`[handler-ptr, grp<<12|cmdID, 0]` records, 12-byte stride,
> main run at vaddr `0xc0691080`–`0xc06913b0`, 149 distinct IDs) and the
> dispatchers are **Hexagon** code in `wpss.b06` (e_machine 164 per the
> mdt; PDEV dispatcher `0xc02cd9cc` decoded end-to-end). Full chain:
> `papers/wmi-dispatch-architecture.md` (F-9 → F-29 synthesis). The
> profile-cluster reading in the table below is likewise deflated (a
> strict 2 KB window on wpss.b08 yields 4/5, not 5/5 — F-19 correction).
> The original text is kept as-is below for the record.

**Claim:** First systematic cross-reference of ath11k's WMI command/event IDs
(605 values, evaluated from `wmi.h` enums with a C-style evaluator) against
the WCN6750 wpss firmware segments. Result: the **WLAN-profile command
family is fully present** in `wpss.b08` (all five IDs 0x10001–0x10005,
adjacent, in a structured config region); the broader WMI command space is
**absent as stored constants** — the firmware evidently constructs IDs
arithmetically (`grp << 12 | 1` at runtime), so naive static cross-reference
does not scale. Nothing about this comparison exists in public literature.

## Method

1. `tools/xref_wmi.py` evaluates ath11k's `wmi.h` enums the way the C
   preprocessor would: implicit `+1` increments, chained symbol references
   (`WMI_GRP_SCAN = WMI_GRP_START`), and the `WMI_TLV_CMD(grp) = grp<<12|1`
   macro family. Verified against hand-computed ground truth:
   `WMI_START_SCAN_CMDID=0x3001`, `WMI_SERVICE_READY_EVENTID=0x1`,
   `WMI_SCAN_EVENTID=0x3001`, `WMI_PDEV_TPC_CONFIG_EVENTID=0x4001`. 605 IDs
   (398 CMDID + 207 EVENTID).
2. Scan each wpss segment at 4-byte alignment for LE32 encodings.

## Results (wpss.b08, 262 KB ucode segment)

| value | ath11k name(s) | hits | first@ | assessment |
|---|---|---|---|---|
| 0x10001 | WLAN_PROFILE_TRIGGER_CMDID | 1 | 0x395f0 | family ✓ |
| 0x10002 | WLAN_PROFILE_SET_HIST_INTVL_CMDID | 2 | 0xb58c | family ✓ |
| 0x10003 | WLAN_PROFILE_GET_PROFILE_DATA_CMDID | 4 | 0xb5cc | family ✓ |
| 0x10004 | WLAN_PROFILE_ENABLE_PROFILE_ID_CMDID | 5 | 0xb60c | family ✓ |
| 0x10005 | WLAN_PROFILE_LIST_PROFILE_ID_CMDID | 4 | 0xbc0c | family ✓ |
| 0x20001 | TDLS_SET_STATE_CMDID / TDLS_PEER_EVENTID | 1 | 0x3881c | likely coincidence |
| 0x2c001 | EXTSCAN_START_CMDID / EXTSCAN_START_STOP_EVENTID | 1 | 0x38c90 | likely coincidence |
| 0x30001 | SAP_OFL_ENABLE_CMDID / SAP_OFL_ADD_STA_EVENTID | 2 | 0x38b10 | ambiguous |
| 0x30002 | SAP_SET_BLACKLIST / SAP_OFL_DEL_STA (0x10 = ELF header) | 1 | 0x10 | bogus (header) |

wpss.b07: only DFS (0xa001 ×4) and isolated coincidences.

**Family-cluster evidence:** all five WLAN-profile IDs — and *only* those
among 605 — appear within a 2 KB window of each other, several repeatedly,
in a region with repeating (cmd, status) word pairs. That structure is
consistent with a registered-handler/config table for the profile/FWTEST
subsystem, and implausible as random data (5/5 of one family, 0/398 of the
rest as aligned stores).

**The negative result matters:** core commands (SCAN=0x3001, PDEV=0x4xxx,
VDEV=0x5xxx families) are *not* stored as aligned constants anywhere in
either segment. Combined with the earlier immediate-operand null (see
[[wpss-qurt-rtos]]), the conclusion is that the firmware's WMI dispatcher
computes IDs from group numbers at runtime. Static constant matching alone
therefore cannot map the WMI surface of this firmware — the next step is
analyzing the dispatcher's construction sites (`slli`/`ori` sequences on
group immediates) or the IPCI transport layer.

## Tool provenance

- `tools/xref_wmi.py` — enum evaluator + aligned scanner (bugs found and
  fixed during development, documented here for reproducibility: block
  comments swallowing the first enum entry; `or` treating a legitimate
  group value 0 as missing; EVENTID suffix filter).

## Prior art

No public work cross-references ath11k WMI IDs against this firmware
(GitHub code search: `wpss.b08`, `WCN6750 wmi`; ath11k mailing list; XDA —
checked 2026-11-09).
