# motorola Edge_2021 — `boot` family status (3 rows)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#916](https://github.com/adineo-cmd/open-device/issues/916)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 4072b47), `upstream-contribution/blob-database/device-inventory.csv`, AOSP boot-image/AVB public format specs, GSMArena/Phone Scoop (access dates in-line). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT — the standard Android Verified Boot triple** (`boot.img` + `dtbo.img` + `vbmeta.img`), all from the device's radio directory. Sizes are partition-magnitude constants shared corpus-wide; contents are build-specific (all three md5s unique in the corpus). Container layout follows the public AOSP formats; kernel ISA cannot be proven from metadata (honest negative below).

## Device identity

| fact | value | source (access date) |
|---|---|---|
| model | Motorola Edge (2021); codename `berlna` | [GSMArena](https://www.gsmarena.com/motorola_edge_(2021)-11061.php), Phone Scoop, /e/OS device page (2026-11-20); in-repo `device-inventory.csv` (`build_codename=berlna`) |
| SoC | Qualcomm SM7325 Snapdragon 778G 5G (Kryo 670, Adreno 642L) | device-inventory.csv; GSMArena (2026-11-20); in-repo `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md` |
| census scope | 36 rows total (other 17, adsp 6, boot 3, bt 4, gpu 4, wifi 2); 207,166,791 B | coverage-matrix.csv + device-inventory.csv (`blob_rows_devices_sql=36`) |

## The 3 rows

```
awk -F, '$1=="Edge_2021" && $4=="boot"{print $6, $7, $8, $13, $14}' coverage-matrix.csv
```

| file | bytes | md5 (upstream DB) | db_type | db_path |
|---|---|---|---|---|
| boot.img | 100,663,296 (96 MiB) | `c1dacc983d68e078ff56e56ffb71bf3b` | BOOT | motorola/berlna/radio |
| dtbo.img | 25,165,824 (24 MiB) | `801c238a8a8ca79f02b4470bf52e1a97` | DTB | motorola/berlna/radio |
| vbmeta.img | 8,192 | `b4b6addfba936c70d559a461e2d24f6f` | AVB | motorola/berlna/radio |

## Container layout (public format contracts)

- **boot.img** — Android boot image (kernel + ramdisk container, AOSP boot-image format; v3/v4 era for an Android 11 launch device). The 96-MiB size is the flash-partition magnitude, not payload: 53 corpus builds share the same size with distinct md5s. Payload decomposition (header version, page size, kernel/ramdisk spans) needs the payload — metadata-only census cannot prove it.
- **dtbo.img** — device-tree blob overlay image (AOSP dtbo format: dt_table header + per-entry offsets/size/id). 24 MiB is the modal corpus size (72 of 118 dtbo rows); build-specific md5.
- **vbmeta.img** — AVB (Android Verified Boot) metadata: `AvbVBMetaImageHeader` + auth (RSA) + hash descriptors chaining boot/dtbo/system verification. 8,192 B is the modal corpus size (94 of 115 vbmeta rows); Edge_2021's md5 is unique — vbmeta embeds per-build hash descriptors.

## Cross-corpus facts (command-verified)

- The 96-MiB `boot.img` size is the standard Qualcomm radio boot-image magnitude in this corpus: **53 devices** share it (motorola Edge/Defy/Moto G families, Fairphone FP4/FP5/FP6, OnePlus 7–13, Nothing Phone 1/2, Pixels 4A_5G/5/5A, Sony Xperia 10/1/5 series, Samsung Tab A7 pair, Pro_1X, Z5_Pro_GT among others) — sizes are constants, contents are per-build. Samsung phone devices in the same DB use different magnitudes (36/64/60/55 MiB for A21S/A71/F62/Note10-class). Per-device membership re-verified: `awk -F, '$6=="boot.img" && $7=="100663296" && $4=="boot"{print $1}' | sort -u | wc -l` → 53.
- dtbo.img 25,165,824 B: modal (72 rows); vbmeta.img 8,192 B: modal (94 rows), vs 12,288 (11 rows) and 4,096 (10 rows).
- Edge_2021's three md5s are each **unique in the corpus** — per-build artifacts, as expected for images embedding a device-specific kernel/DTB and AVB hash chain.
- The berlna radio directory additionally holds `bluetooth.img` (family bt) and `dsp.img` (family adsp) — separate families, not boot.

## ISA proof and interface facts

- **ISA**: the boot.img payload embeds the AArch64 kernel — not provable from metadata alone (no payload on box); the SoC's AArch64 CPU (Kryo 670 = Cortex-A78/A55, GSMArena 2026-11-20) and mainline `qcom/sm7325.dtsi` make AArch64 the only plausible kernel ISA. Marked [OPEN] until a payload lands.
- **Interface**: flashed to the `boot` / `dtbo` / `vbmeta` partitions via fastboot; vbmeta's hash descriptors verify boot/dtbo at boot time under the AOSP Verified Boot chain. Unlock/flash flows are public (AOSP docs); no berlna-specific interface doc exists in this repo (REPO-STATE-MAP boot verdict: PARTIAL, FP6-only).
- **Evidence class**: all 3 rows P3 (metadata-only, upstream DB md5s recorded above).

## Honest negatives

- boot.img internal layout (header version, page size, kernel/ramdisk/GKI split) is **unverified without the payload** — the AOSP format is the reference, the device's actual header fields are [OPEN].
- Whether berlna ships GKI 2.0 (Android 12+ upgrade) or a legacy 5.x kernel boot image is [OPEN]; the upstream DB records no kernel version for boot rows.
- The `radio` directory's `bluetooth.img`/`dsp.img` belong to other families; their status is the scope of #922/#928-class issues, not this one.

## What would upgrade this finding

1. Payload fetch (LineageOS berlna package or stock radio image): parse boot.img header per AOSP boot-image format, dtbo table entries, and vbmeta descriptors — one pass converts all three [OPEN]s into byte-verified facts.
2. Extend `research/qualcomm/docs/bootchain-census.md` (currently FP6-only) with a berlna/SM7325 row.

## RULE 0 record (2026-11-20)

Exact query strings in the SEARCH/NO-PRIOR-ART comments on this issue: GitHub code search `berlna boot.img` (adineo-cmd/* excluded) → packaging references only; web `Motorola Edge 2021 berlna boot.img dtbo vbmeta analysis` → flash guides only; AOSP boot-image + AVB specs are the public format contracts (source.android.com), device-agnostic. Nobody documents this device's boot-family census rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata (sizes, md5s, paths, db_types) plus public format specs.
