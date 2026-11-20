# Repo-state map — what already exists, by issue family

Generated 2026-11-20 from `git rev-parse HEAD` and the committed tree. This is
the reference for Gate -1: before any issue is worked, its family row says what
already exists and what is actually missing.

Verdicts: **DONE** = deliverable present and tested; **PARTIAL** = substantial
work committed, a named delta remains; **NEW** = no committed deliverable.

## Summary

| issue family | count | verdict | existing artifact |
|---|---:|---|---|
| Firmware family doc | 1,107 | NEW | only stubs (`docs/devices/*/leverage-families.md`, "Deep-RE status: none yet") |
| Device package | 245 | NEW | `research/devices/` does not exist |
| SoC package | 27 | NEW | `research/soc/per-soc-method-plans.md` is a plan, not per-SoC results |
| CPU/SoC core ID | 27 | NEW | none |
| GPU core ID | 27 | NEW | none |
| Driver interface | 42 | PARTIAL | 10 FP6 interface docs under `research/qualcomm/docs/` |
| Proprietary blob spec | 9 | PARTIAL | 6 families have committed format work |
| Firmware fleet | 9 | PARTIAL | 3 families have committed fleet notes |
| Deep RE | 15 | MIXED | see per-issue rows below |
| Device part | 18 | PARTIAL | `research/fleet/` covers boot/dtb and some partitions |
| Open-source implementation | 9 | PARTIAL | `implementations/` has 19 tested components |
| Clean-room implementation | 21 | DONE/PARTIAL | 19 components with code; 2 gaps (`root`, `htt`) |
| Site | 7 | DONE | deployed, closed |

## Blob spec — per family

| family | existing artifact | verdict | delta |
|---|---|---|---|
| adsp | `research/laptop/qualcomm-adsp-bm2n-container-header.md` (48/48 files, five invariants, segment table), `-fleet-content.md`, `-variant-matrix.md`; parser `implementations/adsp-fleet/` (86 tests) | PARTIAL | signature/attestation rules absent; fleet is bm2n only |
| boot | `research/qualcomm/docs/bootchain-census.md` (FP6 inventory, AVB, RISC-V cores) | PARTIAL | no byte-level cross-device container spec, no parser |
| bt | `research/fleet/qca-bt-format.md` (field-level spec, 29 devices), `research/fleet/patch-stream-structure.md`; parser `implementations/qca-bt/` (30 tests) | PARTIAL | signature/manifest semantics marked open; 24-byte vs vendor-extended header |
| cdsp | none dedicated; `research/fleet/dsp-tz-map.md` touches `dsp.img` | NEW | full spec + parser |
| gpu | `research/laptop/qualcomm-adreno-gmu.md`, `-gmu-content.md`, `-a650-fleet.md`, `research/fleet/gpu-bdwlan.md`; parsers `implementations/adreno650/` (4 tests), `adreno-fleet/` (62 tests) | PARTIAL | signature rules absent; no bdwlan GPU parser |
| modem | `research/laptop/qualcomm-pil-manifest-family.md`, `research/fleet/pil-metadata-sweep.md`; parser `implementations/pil-manifests/` (41 tests) | PARTIAL | `qdsp6sw.mbn` (84,123,868 B, 47.7% of SM8250 modem volume) undecoded — issue #606 |
| other | `research/laptop/qualcomm-data-blob-fleet.md` (hrtf5c, dax_param); parser `implementations/data-blob-fleet/` (54 tests) | PARTIAL | rest of the "other" bucket |
| tz | `research/fleet/dsp-tz-map.md` (QSEE ELF64 segment map, enchilada), `research/qualcomm/docs/trustzone-census.md` (FP6) | PARTIAL | cross-device spec, signature, `seg[10]` entropy 6.64 question |
| wifi | `research/fleet/bdwlan-format.md` (container RESOLVED, 34-file IE map, record structure) | PARTIAL | no stdlib parser, single-device scope |

## Firmware fleet — per family

| family | existing artifact | verdict | delta |
|---|---|---|---|
| adsp | `research/laptop/qualcomm-adsp-bm2n-fleet.md` (metadata, 20 devices), `-fleet-content.md` (48/48), `-variant-matrix.md`; `implementations/adsp-fleet/` | PARTIAL | catalog cites 253 files / `adspua.jsn` 60 devices; docs cover 48 bm2n |
| boot | `research/qualcomm/docs/bootchain-census.md` | PARTIAL | FP6 only |
| bt | `research/laptop/qualcomm-qca-bt-fleet.md`, `-content.md` (gen-1/gen-2, SHA-256 invariant), `research/fleet/qca-bt-format.md`, `patch-stream-structure.md` | PARTIAL | cross-device beyond laptop/mobile half |
| cdsp | none | NEW | full |
| gpu | `research/laptop/qualcomm-adreno-a650-fleet.md`, `qualcomm-adreno-gmu-content.md`, `research/fleet/gpu-bdwlan.md` | PARTIAL | bdwlan GPU fleet |
| modem | `research/fleet/pil-metadata-sweep.md` (SDM845 + SM8250), `research/laptop/qualcomm-pil-manifest-family.md` | PARTIAL | `qdsp6sw.mbn` |
| other | `research/laptop/qualcomm-data-blob-fleet.md` (2 blobs) | PARTIAL | rest |
| tz | `research/fleet/dsp-tz-map.md`, `research/fleet/qsee-crossgen.md` (SDM845 vs SM8250) | PARTIAL | cross-device |
| wifi | `research/fleet/bdwlan-format.md` (enchilada) | PARTIAL | cross-device |

## Deep RE — per issue

| issue | existing artifact | verdict |
|---|---|---|
| Adreno A650 GMU/SQE continuation | `research/laptop/qualcomm-adreno-a650-fleet.md`; `implementations/adreno650-fleet/` (113 tests) | DONE — only manifest record semantics `[OPEN]` |
| bdwlan tag semantics 1..30 | `research/fleet/bdwlan-format.md` | NEW — genuinely open |
| bm2n header words 11-15 + `0x10400` TOC | `qualcomm-adsp-bm2n-container-header.md` §2 resolves `u32[10]==0x010400` = `segment[0].flags` and `u32[2]==7` = build-id length | PARTIAL — words 11-15 open |
| bm2n tail `[2794,7172)` | none | NEW |
| 256-byte QCA patch tail | `research/fleet/patch-stream-structure.md` §1: per-file-unique high-entropy, signature/attestation-like `[F]` | PARTIAL — role not proven |
| WiFi `cpp_firmware` continuation | `research/laptop/wifi-cpp-firmware-family.md`; `implementations/wifi-cpp-fleet/` (88 tests) | DONE — only `[OPEN]` register |
| historic-device queue | `research/historic/historic-devices-queue.md` | PARTIAL — pmaports/LineageOS/UT/eOS expansion |
| MediaTek interface claims vs AOSP kernel | `research/mediatek/docs/*`, `research/mediatek/rosemary-census.md` | PARTIAL |
| patch-stream section boundary | `research/fleet/patch-stream-structure.md` line 181: "section boundary semantics unknown" | NEW |
| PIL `B01[40+32*n]` signing | `research/fleet/pil-metadata-sweep.md` | PARTIAL |
| PIL `.jsn` manifest extension | `research/laptop/qualcomm-pil-manifest-family.md`; `implementations/pil-manifests/` (41 tests) | DONE — only `[OPEN]` list |
| `qdsp6sw.mbn` | none | NEW — issue #606, claimed |
| QSEE PSS blocks | `research/fleet/qsee-crossgen.md` | PARTIAL |
| Tensor radio-directory inventory | none | NEW |
| `tz.img` `seg[10]` entropy 6.64 | `research/fleet/dsp-tz-map.md` open item | NEW |

## Rule

An issue marked DONE here is closed with `ALREADY-DONE`. An issue marked PARTIAL
gets a `REPO-STATE` comment naming the existing path and the delta; the agent
does the delta only. An issue marked NEW proceeds to Gate 0 unchanged.
