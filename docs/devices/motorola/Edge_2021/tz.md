# motorola Edge_2021 — `tz` family status (0 rows — census-scope gap, not structural absence)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#922](https://github.com/adineo-cmd/open-device/issues/922)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 060cd41), public LineageOS device trees `android_device_motorola_berlna` + `android_device_motorola_rhodep` (lineage-22.2, fetched 2026-11-20), `docs/REPO-STATE-MAP.md`. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `tz` rows in the census is a CENSUS-SCOPE GAP, not structural absence.** The berlna census mirrors its own LineageOS extract source — whose `proprietary-firmware.txt` lists exactly two firmware files — while sibling Moto hardware of the same SM7325 generation demonstrably ships the full Qualcomm boot-chain TEE set (tz/devcfg/hyp/keymaster/uefisecapp). On-device presence of the tz family on the berlna factory image is strongly expected but [OPEN] until a factory image or extract list with the boot-chain set is recorded.

## Device identity

| fact | value | source (access date) |
|---|---|---|
| model | Motorola Edge (2021); codename `berlna` | [GSMArena](https://www.gsmarena.com/motorola_edge_(2021)-11061.php) (2026-11-20); `device-inventory.csv` (`build_codename=berlna`) |
| SoC | Qualcomm SM7325 Snapdragon 778G 5G | device-inventory.csv; in-repo `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md` |
| census scope | 36 rows in 6 families: other 17, adsp 6, boot 3, bt 4, gpu 4, wifi 2 — **tz 0** | coverage-matrix.csv |

## Census evidence — what berlna's radio dir holds

```
awk -F, '$1=="Edge_2021" && $13=="motorola/berlna/radio"{print $4|"|$6|"|$7|"|$8}' coverage-matrix.csv
bt|bluetooth.img|2097152|ff5763bda1ebe0dcd735cd128dae68c4
boot|boot.img|100663296|c1dacc983d68e078ff56e56ffb71bf3b
other|dsp.img|67108864|4a82a6560998770cb7961fc37e5f5680
boot|dtbo.img|25165824|801c238a8a8ca79f02b4470bf52e1a97
boot|vbmeta.img|8192|b4b6addfba936c70d559a461e2d24f6f
```

Five files; zero tz-grammar names (`^(tz|keymaster|qsee|cmnlib|hyp|devcfg|uefisecapp|featenabler|hdcp|widevine|soter|smplap)` per the repo grammar rule in `research/soc/per-soc-method-plans.md`).

## Why the census matches its source, not the device

The LineageOS `android_device_motorola_berlna` tree (lineage-22.2, fetched 2026-11-20) `proprietary-firmware.txt` — the extract list for the factory release `berlna_global T1RMS33.1-110-17-12` — contains **exactly two** entries:

```
BTFM.bin:bluetooth.img;AB
dspso.bin:dsp.img;AB
```

The census's five berlna radio rows are precisely that pair plus the boot/dtbo/vbmeta images flashed separately. The census is **complete relative to its extract source**; the source itself omits the Qualcomm boot-chain TEE images because a custom-ROM runtime needs only the DSP/BT firmware as filesystem payloads — the TEE images are flashed to their own partitions from the factory image and never read as files by Android.

## Sibling proof that the family exists on this hardware generation

`android_device_motorola_rhodep` (Edge 30 Neo — same 2021 Moto generation, SM7325-AE) lineage-22.2 `proprietary-firmware.txt` lists **17** firmware images from its factory release, including:

```
tz.mbn:tz.img;AB   devcfg.mbn:devcfg.img;AB   hyp.mbn:hyp.img;AB
keymaster.mbn:keymaster.img;AB   uefi_sec.mbn:uefisecapp.img;AB
```

and the corpus agrees: Edge_30_Neo carries **50 tz-family rows** (tz.img, devcfg.img, hyp.img, keymaster.img, uefisecapp.img, featenabler*, dxhdcp2*, hdcpsrm*, soter64, loadalgota64*) under `motorola/miami/radio` + `motorola/miami/modem/image`. Moto ships the tz family on every SM7325-class device whose census source extracts the boot chain; berlna's source doesn't. (Census-quality note, RULE 1: Edge_30_Neo's rows sit under the `motorola/miami` path — `miami` is the Edge 30 codename, not rhodep — an upstream path/family-sharing quirk worth a lead-level review; recorded here, not edited in the shared stream.)

## The lab's tz grammar — in-repo context

The repo's tz RE artifacts (`research/fleet/dsp-tz-map.md` — QSEE ELF64 segment map on OnePlus 6; `research/fleet/qsee-crossgen.md` — SDM845 vs SM8250; `research/qualcomm/docs/trustzone-census.md` — FP6) are Qualcomm-side and establish the expected shape of `tz.img`-class payloads on this family: ELF64 mdt + bXX splits with QSEE-style segments. Nothing exists for berlna; this doc is the device-scoped delta.

## Honest negatives

- **On-device presence of tz.img/devcfg/hyp/keymaster/uefisecapp on berlna's factory image is expected but unverified** — no public extract list for berlna includes them (its LineageOS extract has 2 entries), and the factory flashfile partition list was not retrievable from public mirrors this session (mirror listing denied). [OPEN]
- Sizes/md5s of the expected berlna TEE images are unknown until such a list or payload lands — no numbers can be honestly stated for files that no public source enumerates.
- The `uefi_sec.mbn`→`uefisecapp.img` naming on rhodep confirms the corpus's `uefisecapp` grammar name; berlna would use the same Qualcomm build shape if present. Inference, not fact — [OPEN].

## What would upgrade this finding

1. A berlna factory flashfile.xml or `firmware-update` partition list from any public mirror: enumerate `tz/devcfg/hyp/keymaster/uefisecapp` image names + sizes → converts the gap verdict into a precise missing-rows list the upstream census should carry.
2. Payload fetch of the berlna factory image: run the repo's QSEE ELF64 census (`analysis/tools/dsp_tz_census.py` method) on berlna's tz payload → first SM7325-berlna TZ segment map.

## RULE 0 record (2026-11-20)

Queries in the SEARCH/DELTA comments on this issue. Key check: GitHub code search `berlna tz.img` (adineo-cmd/* excluded) → packaging references only; web flashfile search → guides only, no verifiable partition listing fetched; the two LineageOS device trees fetched 2026-11-20 are the decisive artifacts. No one documents berlna's tz status.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public device-tree extracts.
