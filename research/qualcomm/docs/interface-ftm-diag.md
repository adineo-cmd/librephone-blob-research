# FTM/UTF instrumentation points (WLAN) — for upstream issues #44 and #45

One-page extension of upstream `docs/ftm.md`, from **public source
trees** ([upstream issue
#44](https://codeberg.org/rsavoye/librephone/issues/44): "identify
where instrumentation code can be inserted, and if it's possible to
update that code for our own custom tests"; and #45: "expand the FTM
doc"). Written 2026-11-16. All cited files verified present in the
public FP6 tree
`github.com/LineageOS/android_kernel_fairphone_sm7635-modules`
(`qcom/opensource/wlan/...` — three probes fetched OK 2026-11-16).

**Legend:** [PUBLIC] = public-tree fact (upstream `docs/ftm.md` +
the wlan module tree); [LAB] = lab-derived fact; [OPEN] = needs the
blob binary, not on this box.

## 0. Scope note

Upstream `docs/ftm.md` already documents the FTM/UTF command channel
(ioctl `0x1000/0x1001`, nl80211 testmode cmd 0, `ftm_seg_hdr_info`
16-byte reassembly, 2048 B/segment, `wmi_pdev_utf_cmd_id`/`_event_id`).
This page adds what #44 asks for: **where to hook**.

## 1. Instrumentation points, outermost → blob boundary

Each layer is a public file; hooks at earlier layers are pure kernel
work and need no blob knowledge:

| # | layer / file | hook type | use |
|---|---|---|---|
| 1 | `os_if/linux/ftm/src/wlan_cfg80211_ftm.c` (nl80211 entry) | wrap `wlan_cfg80211_ftm_testmode_cmd` + the rx-event pushback | record every userspace↔driver FTM exchange; ideal for logging/test-harness harnessing |
| 2 | `os_if/linux/ftm/src/wlan_ioctl_ftm.c` (ioctl `0x1000/0x1001`) | wrap the two ioctl handlers | same, for the ioctl-based daemon path |
| 3 | `ftm/dispatcher/src/wlan_ftm_ucfg_api.c` (`ucfg_wlan_ftm_testmode_cmd` + reassembly) | insert at the converged single point both paths pass through | one chokepoint sees all commands AND complete reassembled responses — the best place for an automated test suite |
| 4 | `target_if/ftm/src/target_if_ftm.c` (`target_if_ftm_cmd_send` / `target_if_ftm_process_utf_event`) | shim immediately above `wmi_unified_pdev_utf_cmd_send` | byte-exact capture of what actually goes to/comes from the blob |
| 5 | WMI layer (`wmi_unified_pdev_utf_cmd_send`) | filter/patch outbound UTF commands | format-level tracing; [LAB] the WMI registry/decorators this firmware uses are documented in `papers/wmi-dispatch-architecture.md` |
| 6 | blob side (WCN6750 UTF handler) | — | [OPEN] the handler lives in the Hexagon/RV32 wpss image; instrumenting *inside* the blob means replacing segments, which is blocked upstream by the PAS signing chain (PR #58 thread: scm PAS rejects any replaced segment) |

**Activation context** [PUBLIC]: the FTM channel is only live in
`QDF_GLOBAL_FTM_MODE` — module param `con_mode_ftm`
(`/sys/module/qca_cld3_qca6750/parameters/con_mode_ftm` in upstream's
own list) or `adb reboot ftm`; the driver must be loaded in FTM mode
before any of layers 1–5 see traffic.

## 2. Custom tests without touching the blob

Yes — [PUBLIC] the UTF payload is **opaque** end-to-end: the driver
only segments/reassembles (`ftm_seg_hdr_info`), it does not parse
UTF content. Consequences:

- a userspace test tool can send arbitrary ≤2048-byte blobs through
  nl80211 testmode or the ioctl and get the blob's echo back;
- instrumentation inserted at layer 3 or 4 can synthesize/modify UTF
  payloads in-kernel, i.e. "our own custom tests" at the command
  level without any blob modification;
- constraints to respect: FTM mode active, one pdev priv-obj per
  interface, 2048 B/segment, `total_segments`/`current_seq` bookkeeping
  on responses.

What is **not** possible without blob work: adding new *blob-side*
behaviors (the blob executes only its own Hexagon/RV32 code). That is
the [LAB] boundary the lab's census work frames — see
`qualcomm-fp6/docs/fp6-architecture-census.md` for the blob's ISA
map (Hexagon segments + RV32 QURT app) and the F-8 QURT finding.

## 3. Doc-expansion checklist for #45 (what upstream ftm.md does not yet carry)

1. the instrumentation table above;
2. the custom-test mechanics (opaque payload path, limits);
3. the FTM↔HTT independence note (already there) plus the CE pipe
   numbers FTM does NOT use (FTM rides WMI, not the CE4 HTT data pipe
   — see `qualcomm-fp6/docs/interface-copyengine.md`);
4. a pointer to the WMI dispatch spec for anyone decoding UTF event
   IDs against the registry.

## Sources consulted (accessed 2026-11-16)

- upstream `docs/ftm.md`
  (https://codeberg.org/rsavoye/librephone/raw/branch/main/docs/ftm.md —
  fetched, 260 lines)
- public FP6 wlan module tree: `wlan_ftm_svc.c`, `wlan_hdd_ftm.c`,
  `wlan_cfg80211_ftm.c` — HTTP 200 on
  `raw.githubusercontent.com/LineageOS/android_kernel_fairphone_sm7635-modules/HEAD/qcom/opensource/wlan/...`
- lab: `papers/wmi-dispatch-architecture.md`,
  `qualcomm-fp6/docs/interface-copyengine.md`,
  `qualcomm-fp6/docs/fp6-architecture-census.md`

**Clean-room statement:** public-tree file/struct facts + lab
census/paper facts; no decompiled code, no blob payload contents.
