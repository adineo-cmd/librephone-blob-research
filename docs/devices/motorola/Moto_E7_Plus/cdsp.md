# motorola Moto_E7_Plus - `cdsp` family status (11 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1252](https://github.com/adineo-cmd/open-device/issues/1252)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 945ad74), `upstream-contribution/blob-database/device-inventory.csv`, torvalds/linux `sm6115.dtsi`/`sm4250.dtsi` (fetched 2026-11-21), linux-firmware WHENCE (fetched 2026-11-21), LineageOS wiki + device trees (fetched 2026-11-21), GSMArena (2026-11-21). Evidence classes: [F] fact (command output or recorded fetch) / [I] inference (labeled). No payloads fetched.

**Verdict: the cdsp family is PRESENT and structurally complete on guam** - 11 rows, 2,969,603 B: one full Qualcomm split-PIL CDSP container (cdsp.mdt + 9 payload segments b00..b06, b08, b10) plus the cdspr.jsn resource JSON, all packaged in the modem image directory (`motorola/guam/modem/image`). 8 of 11 md5s are corpus-unique to guam; the remaining 3 (jsn, b04, b10) are byte-identical with Trinket-family Moto siblings. The CDSP subsystem itself is mainline-attested for this platform family. This is presence, not a census gap.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Moto E7 Plus (XT2081-class); also sold as Lenovo K12 | LineageOS wiki `devices/guam` (fetched 2026-11-21) [F]; XDA threads tie XT2081-1 to guam (searched 2026-11-21) [F] |
| codename | `guam` | `device-inventory.csv` [F]; official [LineageOS/android_device_motorola_guam](https://github.com/LineageOS/android_device_motorola_guam) = "Device tree configuration for Motorola Moto E7 Plus" (fetched 2026-11-21) [F]. Inventory codename cell is CORRECT - verified because codename traps are common in this corpus (playbook: rhodep/gta4xl) |
| SoC | Qualcomm **SM4250 Snapdragon 460** (Adreno 610, Kryo 240 octa-core) | LineageOS wiki variant page, exact string "Qualcomm SM4250 Snapdragon 460" (fetched 2026-11-21) [F]; inventory SoC cell agrees [F] |
| release | 2020-09-16, Android 10 ship build | LineageOS wiki (fetched 2026-11-21) [F] |
| census scope | 210 rows, 9 families, priority P3, build status "fails" | `device-inventory.csv` [F] |
| platform family | Trinket: mainline `sm4250.dtsi` is a thin overlay that `#include`s `sm6115.dtsi` | torvalds/linux master (fetched 2026-11-21) [F] |

Family histogram [F]: adsp 35, boot 9, bt 11, cdsp 11, gpu 14, modem 43, other 44, tz 5, wifi 38 - sums to 210 (verified with python3 before writing).

## Row decomposition [F]

```
awk -F, '$1=="Moto_E7_Plus" && $4=="cdsp"{print $6" "$7" "$8" "$13" "$14}' upstream-contribution/blob-database/coverage-matrix.csv
```

11 rows, one component set, all `db_path = motorola/guam/modem/image`, all priority P3:

| file | bytes | md5 (upstream DB) | db_type |
|---|---:|---|---|
| cdspr.jsn | 403 | `f2bd80d5f0b19b5b0d36d28383948149` | UNKNOWN |
| cdsp.mdt | 7,580 | `76a8ac58a16eac1e5e919fdf07ff6b8d` | COMPUTE |
| cdsp.b00 | 436 | `5e9ddcc41762245aa3578b9646c7f1a4` | COMPUTE |
| cdsp.b01 | 7,144 | `1034330660ea1ff93b84558dfa54e09b` | COMPUTE |
| cdsp.b02 | 234,904 | `1a853be52f25ddca93d548a62f6100b7` | COMPUTE |
| cdsp.b03 | 106,620 | `6688972a049ec907f1d0cf07252ba49a` | COMPUTE |
| cdsp.b04 | 1,068 | `c69dd780be80b22abce11cec49f37903` | COMPUTE |
| cdsp.b05 | 2,435,164 | `f272ec4fd382869f251dd974467d36b8` | COMPUTE |
| cdsp.b06 | 22,896 | `037c79bf1939f43ef7f0c12bf479fb74` | COMPUTE |
| cdsp.b08 | 94,488 | `eed9f5aef1aabe65ddc5863cfa51a0d4` | COMPUTE |
| cdsp.b10 | 58,900 | `063e55ea48ffe7baaab4d35b829c7926` | COMPUTE |

Structure law [F]: one split-PIL set = mdt + 9 payload segments (b00..b06 contiguous, then b08, b10; **b07, b09, b11 are absent**). This matches the Qualcomm ELF-less split grammar: the .mdt carries the ELF program headers, each .bNN is one raw loadable segment [I, standard Qualcomm PIL structure, corpus-established for the tz family in `research/fleet/dsp-tz-map.md`]. `cdspr.jsn` is the companion resource/service-registry JSON [I]: linux-firmware co-ships `cdspr.jsn` beside `cdsp.mbn` for sibling platforms (WHENCE lines 7452/7494/7507/7523, fetched 2026-11-21) [F].

Sum checks [F, python3-verified]: all 11 rows = 2,969,603 B; the 10 COMPUTE rows = 2,969,200 B; the 9 payload segments alone = 2,961,620 B; largest segment b05 = 2,435,164 B = 82.2% of payload bytes. No b07/b09/b11 rows exist anywhere under the device's cdsp family [F].

## Cross-corpus md5-sharing facts [F]

Corpus context [F]: 63 corpus devices carry cdsp rows, 940 rows total (880 COMPUTE + 60 UNKNOWN). guam's split is 10 COMPUTE + 1 UNKNOWN.

- `cdspr.jsn` `f2bd80d5...` (403 B) is byte-identical across **30 devices in 6 vendor groups** (motorola 17, oneplus 8, realme 2, xiaomi 1, fairphone 1, fxtec 1; sums to 30) - a fleet-wide, vendor-neutral CDSP resource descriptor, the same per-fleet pattern #1156 found for Samsung PLMN tables [F].
- `cdsp.b04` `c69dd780...` (1,068 B) is byte-identical across **8 devices**: guam, bathena (Defy_2021), capri (G10), caprip (G30), guamp (G9), cebu (G9_Power), borneo (G_Power), pro1x (Pro_1X) - an 8-device Trinket-family span [F].
- `cdsp.b10` `063e55ea...` (58,900 B) is byte-identical across **6 devices**: guam, bathena, capri, guamp, cebu, borneo [F].
- The other 8 files (mdt, b00, b01, b02, b03, b05, b06, b08) are **corpus-unique to guam** - each of those md5s occurs exactly once in the 33,917-row matrix [F]. Per-build CDSP payloads with shared small resource segments [I].

## Sibling contrast [F]

| device | codename | SoC | cdsp fingerprint | generation read [I] |
|---|---|---|---|---|
| Moto_E7_Plus | guam | SM4250 | mdt 7580, b05 2,435,164, 9 segments, no b09/b11 | Android 10-era Moto build |
| Moto_G10 | capri | SM4250 | identical sizes to guam except b05 2,443,100 (+7,936) | same generation |
| Moto_G9 | guamp | inventory cell EMPTY - SM6115 per LineageOS wiki + GSMArena (fetched 2026-11-21) | b05 2,443,100, rest same as capri | same generation |
| Moto_G9_Power | cebu | inventory cell EMPTY - SM6115 per LineageOS wiki | same sizes as guamp | same generation |
| Moto_G_Power | borneo | SM6115 | same sizes as guamp | same generation |
| Defy_2021 | bathena | SM6115 | same sizes as guamp | same generation |
| Moto_G30 | caprip | SM6115 | mdt 7660 (+80), b00 468 (+32), b01 7192 (+48), b02 235,672 (+768), b05 2,447,100, b06 23,392 (+496), b08 103,812 (+9,324), plus b09 280 and b11 58,900, no b10 | Android 11-era grammar |
| Pro_1X | pro1x | SM6115 | like caprip (b05 2,443,004, b06 23,212) | Android 11-era grammar |

- guam matches 5 siblings (capri/guamp/cebu/borneo/bathena) on 9 of 10 non-jsn sizes; only b05 differs (+7,936 B on the siblings) [F]. Yet guam's b05/mdt/b00/b01/b02/b03/b06/b08 md5s are byte-distinct from every sibling [F] - per-build payload builds on a common size skeleton [I].
- The b09+b11 grammar appears only on the corpus's Android-11-generation builds (caprip, pro1x); guam's set lacks them, consistent with its Android 10 ship build [I].
- SD460 (SM4250) and SD662 (SM6115) are one platform family - mainline `sm4250.dtsi` literally includes `sm6115.dtsi` [F] - which explains one shared CDSP size fingerprint across both SoCs.
- Inventory corrections for the lead [F]: `Moto_G9` (guamp) and `Moto_G9_Power` (cebu) SoC cells are EMPTY; guamp = Moto G9 Play = **SM6115 Snapdragon 662** (LineageOS wiki `devices/guamp/variant1` exact string "Qualcomm SM6115 Snapdragon 662" + GSMArena, fetched 2026-11-21), cebu = Moto G9 Power = SM6115 (LineageOS wiki `devices/cebu/variant1`, fetched 2026-11-21).

## Interface and platform facts

- Mainline CDSP node on the platform [F]: torvalds/linux master `arch/arm64/boot/dts/qcom/sm6115.dtsi` defines `remoteproc_cdsp@b300000`, compatible **"qcom,sm6115-cdsp-pas"**, memory-region `pil_cdsp_mem` (0x51a00000, size 0x1e00000) plus `cdsp_sec_mem` (0x46200000, size 0x1e00000); under the CDSP glink edge sits a fastrpc node labeled **"cdsp"** exposing compute-cb@1..compute-cb@6 (iommus 0x0c01..0x0c06). `sm4250.dtsi` inherits all of it via `#include "sm6115.dtsi"` (both fetched 2026-11-21). The ADSP (`qcom,sm6115-adsp-pas` @0x0a400000) and modem (`qcom,sm6115-mpss-pas` @0x06080000) nodes sit alongside [F].
- Device-level fastrpc enablement [OPEN]: GitHub code search for "cdsp" in `LineageOS/android_device_motorola_guam` returned 0 hits (2026-11-21) - the public device tree does not reference cdsp; the vendor kernel DT (Motorola kernel source drop for guam) is the right source and was not fetched in this pass.
- linux-firmware [F, negative for this platform]: WHENCE (git.kernel.org, fetched 2026-11-21, 11,916 lines) ships `cdsp.mbn` + `cdspr.jsn` for qcm6490 (line 7450), qcs615 (7482), **qrb4210 (7492, version string "CDSP.VT.2.4.1-00269-KAMORTA-1" - QRB4210 is the IoT sibling of SM4250 on the same Trinket platform)**, sdm845 (7505), sm8250 (7521), sc8280xp and x1e80100 - and nothing for sm4250/sm6115 phones. Device CDSP firmware ships from the vendor, exactly as guam's census shows: 11 rows in the device's own modem image [F].
- Packaging location [F]: all 11 cdsp rows sit in `modem/image` alongside adsp (35 rows), gpu (13), wifi (38) and modem (41); only tz/boot live in `radio` and bt/other in `bluetooth/image`. DSP firmware riding in the modem image is the established corpus packaging pattern (cf. #1144's Samsung modem-riding families with OnePlus SM8250 positive controls) [I].

## ISA proof

- `isa_identified` is **empty for all 11 rows** [F] - honestly un-RE'd per the upstream DB convention. No payload was fetched (facts-not-blobs), so this doc contains no ISA-level proof of Hexagon content for guam's cdsp.
- Hexagon attribution [I, labeled]: the cDSP on Trinket-family SoCs is a Hexagon compute processor and mainline's CDSP remoteproc + fastrpc nodes treat the domain as a Hexagon compute target; which Hexagon version guam's payload targets is unproven here. [OPEN]

## Honest negatives

- No ISA proof, no container internals: the payload segments' ELF content, signing metadata, and CDSP app layout are [OPEN] until a payload pass runs.
- No guam vendor kernel DT fetch: the kernel tree's fastrpc/cdsp node would move the interface facts from platform-level [F] + device-level [I] to device-level [F]. [OPEN]
- `cdspr.jsn`'s exact runtime consumer (kernel remoteproc vs userspace loader) is not established for guam; co-shipment with CDSP images in linux-firmware and required-firmware lists for sc8280xp-class platforms is the only public evidence [I]. [OPEN]
- The census does not record which ROM build guam's dump came from; sibling b05 divergence (+7,936 B) shows CDSP payloads are build-sensitive, so version attribution of guam's md5s is [OPEN].

## What would upgrade this finding

1. Payload pass on a guam modem image: read cdsp.mdt ELF headers (machine class, program headers mapping the 9 bNN segments) and enumerate CDSP services; cross-gen first against capri (same SoC, b05 differs by 7,936 B).
2. Fetch the guam vendor kernel DT (Motorola kernel source drop) for the fastrpc "cdsp" node - turns the interface section into a device-level [F].
3. Corpus pass: build a CDSP generation map from the md5 clusters (b04/b10 across 8 Trinket devices) vs the Android-11 grammar (b09+b11 on caprip/pro1x).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/DELTA comments on this issue. GitHub code search (adineo-cmd/* excluded): `"cdspr.jsn"` -> 1,254 hits, all firmware packaging scripts, WHENCE copies and driver file-list code; no guam/E7 Plus cdsp analysis anywhere. Web: "Moto E7 Plus codename guam OR sahara LineageOS device tree SM4250" -> guam identity confirmed (LineageOS wiki + official device tree); "guamp Motorola G9 Play LineageOS codename SM4250" + GSMArena -> G9 Play = SM6115 SD662; torvalds/linux sm4250/sm6115 dtsi and linux-firmware WHENCE fetched 2026-11-21. Nobody documents Moto_E7_Plus cdsp - the deliverable is new.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public documentation.
