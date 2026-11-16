# implementations — clean-room, spec-derived components

Everything here is implemented from the lab's published spec documents and
public GPL kernel sources only. No proprietary code, headers, or strings
were read by any implementer; no proprietary payload is committed. Each
component carries a clean-room statement header and a self-test.

| component | source spec | status |
|---|---|---|
| [wmi/dispatch-registry](wmi/dispatch-registry/) | papers/wmi-dispatch-architecture.md + qualcomm-fp6/docs/wmi-* (F-22/F-23/F-28/F-29) | self-test passing (33 checks) |
| [wmi/tlv](wmi/tlv/) | public ath11k wmi.h (GPL) framing facts | self-test passing (36 checks) |
| [ce/service-model](ce/service-model/) | public ath11k ce.h/hw.c + docs/interface-copyengine.md | self-test passing (29 checks) |
| [htc/frame-layer](htc/frame-layer/) | public ath11k htc.h (GPL) frame/service facts | self-test passing (23 checks) |
| [htt](htt/) | none committed — open item | documented gap |
| [lpec/frame-parser](lpec/frame-parser/) | open-discovery-lab track-c lpec spec docs (F-47/F-48/F-49 + pass3) | packaged, byte-exact per pass3 validation |
| [mediatek/container](mediatek/container/) | rosemary census "Container formats" + U-Boot tools/mtk_image.h (GPL) | self-test passing (57 checks incl. md32-interface) |
| [mediatek/md1rom-taskmap](mediatek/md1rom-taskmap/) | rosemary census md1rom regions (F-31) | self-test passing; 6 explicit stubs |
| [mediatek/md32-interface](mediatek/md32-interface/) | F-45 MD32 interface lever-2 facts | self-test passing |
| [qca-bt](qca-bt/) | public btqca.h/btqca.c (GPL, torvalds/linux master, fetched 2026-11-16) — TLV patch/NVRAM container families (crbtfw/apbtfw/crnv/apnv …) | unittest suite passing (30 tests) |

Build: `gcc -std=c99 -Wall -Wextra -O2 -o test <comp>/test_*.c <comp>/*.c` (each
test binary self-validates and exits non-zero on any failure).

## Liaison target

[upstream PR #58](https://codeberg.org/rsavoye/librephone/pulls/58) ("Add WCN6750
AMSS Zephyr implementation", state open, author L123123, fetched 2026-11-16)
states in its own body: "WMI/HTT/CE and the RF/PHY stack are not implemented."
The WMI/CE/HTC components here are written against the lab's decoded WCN6750
wpss dispatch spec — the exact gap the PR names.

## RULE 0 prior-art record (all searches 2026-11-16)

- `Qualcomm Bluetooth ROM patch .tlv format reverse engineering crbtfw apbtfw`
  — no dedicated RE writeup of the QCA .tlv patch format exists; adjacent work
  is Broadcom/Realtek RE + mainline `drivers/bluetooth/btqca.c` protocol code.
- `"lpec" audio codec reverse engineering lineage phone qmi` — zero hits; LPEC
  is Sony's voice-recorder codec (MultimediaWiki MSV page, 2009, container-only);
  no open-source decoder (confirmed again 2026-11-14 in the lab's F-47 census).
- `android proprietary blob database coverage matrix per-device firmware census
  lineageos` — closest: "An Empirical Study of Proprietary Vendor Blobs in
  Android" (ICPADS 2024, arXiv:2410.11075, 13k firmware releases, staleness
  focus) and per-device `proprietary-blobs.txt` build manifests. Neither is a
  RE-status coverage matrix; delta recorded, not rebuilt.
- `"bm2n" bin adsp firmware reverse engineering qualcomm` — no direct hits for
  the bm2nXX fleet; adjacent: linux-msm/hexagon-dsp-binaries, TR25 hexagon RE,
  SRLabs hexagon fuzzing, bkerler QDSP walkthrough.
- `ath11k WMI dispatcher firmware side reference implementation table driven
  clean room` — no firmware-side clean-room dispatcher reference exists
  publicly; ath11k's host-side dispatcher is table-driven but is not the
  decoded firmware architecture implemented here.
