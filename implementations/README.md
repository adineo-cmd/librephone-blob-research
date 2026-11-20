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
| [qca-bt-gen2](qca-bt-gen2/) | same GPL sources, second chip generation (`hp*`=QCA2066 / `hmt*`=WCN7850); 32-byte header + 36-byte SHA-256 trailer, `4+32+len+36` size rule | unittest suite passing (58 tests); cross-family version rule **confirmed**, DB-identical payloads **[OPEN]** |
| [adsp-fleet](adsp-fleet/) | public QNN/HTP headers (BSD-3-Clause-Clear: `tensor.h` `TENSOR_MAGIC`, `pickle_header_tags.h`, `serialize_defs.h`) + `fastrpc.c` (GPL) — ADSP `bm2nXX` container | unittest suite passing (86 tests); container specified, **not DSP firmware** (serialized C++ tensor graph) |
| [adreno-fleet](adreno-fleet/) | public `a6xx_gmu.c`/`a6xx_gmu.xml`/`a6xx_catalog.c` (GPL) — Adreno GMU microcode, raw-ITCM legacy path | unittest suite passing (62 tests); `0x43f80` = initial stack pointer; 13 live devices not 26 |
| [data-blob-fleet](data-blob-fleet/) | public spatial-audio literature (SOFA/AES69, OpenAL Soft) + own measurements — opaque data blobs | unittest suite passing (54 tests); `hrtf5c.bin` decoded (40 azimuths × 2 ears × 257 bins), `dax_param.bin` matches public `dax-default.xml` |
| [pil-manifests](pil-manifests/) | public `mdt_loader.c`/`qcom_q6v5_pas.c`/`qcom_pd_mapper.c` (GPL) + userspace `pd-mapper` (BSD-3) — `*.jsn` manifests | unittest suite passing (41 tests); premise refuted — JSON PDR service registry, **not** split-MDT manifests |
| [hbt-fleet](hbt-fleet/) | public `btqca.h`/`btqca.c` + `WHENCE` — `hpbtfw20`/`hpnv20` (Hastings generation) | unittest suite passing (6 tests); 44-byte footer, 61-tag NVM |
| [adreno650](adreno650/) | public `a6xx_gmu.c` (GPL) — a650 GMU + SQE | unittest suite passing (4 tests); GMU 16-block chain, SQE v0.93 version gap |
| [adreno650-fleet](adreno650-fleet/) | public `a6xx_gmu.c`/`a6xx_gpu.c`/`a6xx_catalog.c` + linux-firmware `WHENCE` (GPL/redistributable) — a650 GMU container + SQE fleet | unittest suite passing (113 tests); **container** class (not raw-TCM like a619); SQE floor `0x095` confirmed at `a6xx_gpu.c:1032`, multiple sub-0.95 builds circulate; 9 live of 14 carried (`pdx215` mislabel corrected) |
| [historic](historic/) | public `mdt_loader.c`, prima driver GPL sources, Replicant/samsung-ipc — FP2, hammerhead, m0 | FP2 parsers passing (**28 tests**); historic-device queue first pass. **Run as `python3 -I test_parsers.py` in `historic/fp2/` — `unittest discover` collects none**, because the suite is a `check()` harness, not `unittest.TestCase` (discover exits 5, "NO TESTS RAN", so it fails loudly rather than silently passing). |
| [wifi-cpp-fleet](wifi-cpp-fleet/) | public `msm_cpp.c`/`msm_cpp.h` (GPL-2.0-only, LineageOS msm8953 @ lineage-21) + userspace `cpp_hardware.c` — `cpp_firmware_vN_N_N.fw` fixed-window images | unittest suite passing (88 tests); **not WiFi** — MSM Camera Post-Processing microcode; version = `0x1000\|BCD(minor)` u16, not ASCII |
| [camera-effect-fleet](camera-effect-fleet/) | public vendor tree listing + own byte measurements — Xiaomi `resources/render/Effect/` assets | unittest suite passing (11 tests); **28-byte header + raw `W×H×4` pixels, exact on 35/35**; artistic assets, not firmware; channel order `[OPEN]` |
| [camera-cfr-fleet](camera-cfr-fleet/) | public vendor tree listings + own byte measurements — OnePlus/Xiaomi `CFR_*.bin` | unittest suite passing (11 tests); **four distinct grammars under one prefix** (1079/2126/3645/8128); `imx766` vs `imx766_uw` differ in one byte |
| [big-clusters](big-clusters/) | metadata + public partition/fstab sources — largest sharing clusters | `vm-bootsys.img` = Qualcomm Trusted VM image (analysis only, no suite) |

Build (C components): `cd <comp> && gcc -std=c99 -Wall -Wextra -O2 -o test
test_*.c $(ls *.c | grep -v '^test_') && ./test` — the non-test sources must be
listed explicitly, otherwise `*.c` includes the test file twice and the linker
fails on a duplicate `main`. Each test binary self-validates and exits non-zero
on any failure.

Python components need their synthetic fixtures materialised first:

```
cd <comp> && python3 -I make_fixture.py && python3 -I test_*.py
```

Without that step a fresh clone reports `FileNotFoundError` on
`fixtures/*_synthetic.bin`, because every payload extension is gitignored. This
is a bootstrap gap, not a code failure. The Python
components (`qca-bt`, `qca-bt-gen2`, `adsp-fleet`, `adreno-fleet`,
`adreno650`, `adreno650-fleet`, `data-blob-fleet`, `pil-manifests`, `hbt-fleet`,
`wifi-cpp-fleet`, `camera-effect-fleet`, `camera-cfr-fleet`, the `mediatek/*`
trio) are stdlib-only;
run each with `cd <comp> && python3 -m unittest discover -q`. **Exception:
`historic/fp2`** is a plain `check()` harness rather than `unittest.TestCase`
classes, so it must be run as `cd historic/fp2 && python3 -I test_parsers.py`;
`unittest discover` collects nothing there and exits 5. Fixtures for the
Python components are synthetic and regenerated by a committed `make_fixture.py`;
`*.bin`/`*.tlv`/`*.fw`/`*.mbn`/`*.elf`/`*.img` are gitignored so no vendor
payload can be committed by accident. Where a component's fixture extension is
not covered at the repo root (e.g. `*.fw`), the component carries a
`fixtures/.gitignore` that excludes its own fixture directory.

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
  SRLabs hexagon fuzzing, bkerler QDSP walkthrough. **Partially re-run
  2026-11-19** once GitHub code search recovered: `"ConcreteTensorIN5Tdefs10QuantUint8EE"`
  -> 0 results, `"1337BEEF" qnn pickle` -> 0, `"tensor.pickle" qualcomm` -> 0;
  `"bm2n13"` -> 1,044 hits but all are `proprietary-files.txt`/`*-vendor.mk`
  inventory, none is RE. **Prose leg then completed 2026-11-19 through a
  browser (the `websearch` tool was returning HTTP 402):** DuckDuckGo gave
  "No results" for `"bm2n" firmware reverse engineering`, `"bm2n" adsp
  firmware qualcomm` and the exact RTTI string; XDA and Reddit `site:` queries
  returned only generic flashing threads, none mentioning `bm2n`. The one
  genuinely adjacent writeup — "Reverse engineering the Qualcomm NPU
  compiler" (datavorous, 2026-06) — was read in full and attacks the QNN SDK
  `*.so` files with Ghidra, never the serialised container (its counts for
  `1337BEEF`, `BEEFF00D`, `ConcreteTensor`, `pickle`, `bm2n` and `0xfa0000fa`
  are all zero). **RULE 0 satisfied on both legs: the bm2n fleet is publicly
  listed and publicly undecoded.**
- `Qualcomm Bluetooth hpbtfw hmtbtfw QCA2066 WCN7850 firmware format` (2026-11-19)
  — no dedicated RE writeup; the format facts here come from `btqca.c` plus
  measurement, as with the `cr*`/`ap*` family.
- `hrtf5c.bin Qualcomm ADSP spatial audio HRTF format` (2026-11-19) — no public
  layout for this filename. Public HRTF *formats* (SOFA/AES69, OpenAL Soft
  `MinPHR`) were checked and excluded by signature/sample-width; the content
  class is public, the encoding is not.
- `dax_param.bin Dolby DAX tuning format` (2026-11-19) — no public spec for the
  binary container; the *data* is public in the same vendor tree as
  `dax-default.xml`, which is the actionable finding.
- `"jsn" Qualcomm image manifest split mdt` (2026-11-19) — the premise is
  refuted by the public sources: mainline's `mdt_loader.c`/`qcom_q6v5_pas.c`
  contain zero `.jsn` handling (`grep -c -i jsn` → 0). The files are JSON PDR
  service registries consumed by userspace `pd-mapper` (BSD-3), and mainline
  hardcodes the same table as C in `qcom_pd_mapper.c`.
- `cpp_firmware_v1_12_0.fw MSM CPP camera post-processing microcode format`
  (2026-11-19) — no public RE writeup of the image *contents*. RULE 0 is
  nonetheless satisfied from the *consumer* side: `msm_cpp.c` (GPL-2.0-only)
  specifies the load path completely — `cpp_load_fw()` streams `fw->size/4`
  little-endian words and parses no header — and userspace `cpp_hardware.c`
  specifies the filename (`snprintf("cpp_firmware_v%d_%d_%d.fw", …)` with the
  `31:28/27:16/15:0` major/minor/step bit layout). The Cypress/Infineon WLAN
  hypothesis was tested against `linux-firmware` `WHENCE` + mainline
  `brcmfmac` and **refuted**. This also corrects the upstream database's
  `blob_family` label for these 12 identities, which reads `wifi` with an
  empty subfamily; they are camera, not WiFi.
- `ath11k WMI dispatcher firmware side reference implementation table driven
  clean room` — no firmware-side clean-room dispatcher reference exists
  publicly; ath11k's host-side dispatcher is table-driven but is not the
  decoded firmware architecture implemented here.
