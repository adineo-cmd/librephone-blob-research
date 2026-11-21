# samsung Galaxy_Tab_S6_Wifi — `boot` family status (6 rows)

Analysis date: 2026-11-21. Analyst: ZC-2 (issue [#509](https://github.com/adineo-cmd/open-device/issues/509)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site f737c8b), `upstream-contribution/blob-database/device-inventory.csv`, LineageOS builds API + mirrorbits artifacts of the gta4xlwifi 23.2 nightlies (fetched 2026-11-21, per-file sha256-verified against the API), TheMuppets vendor trees @ lineage-23.2 (2026-11-21), LineageOS `lineage_wiki` device YAML, `LineageOS/android_device_samsung_gta4xl-common` releasetools.py @ lineage-23.2, public spec pages (2026-11-21). Evidence classes: [F] fact / [I] inference (labeled) / [H] hypothesis / [N] honest negative. No payload committed; hex samples ≤16 bytes.

**Verdict: the boot family is PRESENT as a Samsung Exynos 9611 Android boot-image set — boot/recovery (ANDROID! header v2), a Samsung-format dtbo (`dt_table` big-endian, 5 DTB entries), an unsigned Samsung-style vbmeta, and a liblp `super_empty` geometry blob that is the only row byte-identical to the public artifacts. The DB's boot md5s match none of the three hosted 23.2 nightlies (sizes match all five exactly — partition-fixed constants from older, no-longer-hosted builds). Literal db_type split: 4 BOOT + 1 DTB + 1 AVB; the "6 boot rows" count holds under the boot-partition-image interpretation.**

## Device identity

| fact | value | source |
|---|---|---|
| DB label | `Galaxy_Tab_S6_Wifi` — **a misnomer**: the blob set is Galaxy Tab S6 **Lite (Wi-Fi)**, SM-P610, codename `gta4xlwifi` | coverage-matrix.csv db_path `samsung/gta4xlwifi/firmware/SM-P610` [F]; LOS lineage_wiki `gta4xlwifi.yml`: `name: Galaxy Tab S6 Lite (Wi-Fi)`, `models: [SM-P610]`, `soc: Samsung Exynos 9611` [F]; TheMuppets radio files suffixed `_SM-P610` [F] |
| real Tab S6 | SM-T860 (Wi-Fi) / SM-T865 (LTE) = codename `gts6lwifi`/`gts6l`, Qualcomm SM8150 — absent from this repo and from LineageOS (no wiki page, builds API `[]`); note `gts4lwifi` is the Tab **S4** (SM-T830/SM-T835), not the Tab S6 | public spec pages + LOS wiki device list (2026-11-21) [F] |
| SoC | inventory `soc` cell is **empty** — supplied here: Samsung **Exynos 9611** (4x Cortex-A73 @ 2.3 GHz + 4x Cortex-A53 @ 1.7 GHz, ARMv8-A, Mali-G72 MP3, 10 nm, integrated LTE Cat.12/13) | device-inventory.csv:151 [F]; Samsung semiconductor page + LOS YAML [F] |
| type / variant | `tablet` (hardware: 10.4" LCD slate with S-Pen; LOS YAML `type: tablet`) / `mobile` (standard Android OTA + heimdall flashing, no ATV build) — CONFIRMED | LOS YAML + spec pages (2026-11-21) [F] |
| census scope | 38 rows in 2 families (boot 6 = 5 distinct files, other 32); 243,369,538 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 6 rows [F]

| file | bytes | md5 (upstream DB) | db_type | db_path | public verification |
|---|---:|---|---|---|---|
| `boot.img` | 61,865,984 | `18786b4e75f98470395e98f6d08207fb` | BOOT | `samsung/gta4xlwifi/radio` | FOUND-DIFFERENT — LOS rebuilds it per nightly |
| `recovery.img` | 71,106,560 | `685d8fe9e9027f33305e8e56df2d2fcc` | BOOT | `samsung/gta4xlwifi/radio` | FOUND-DIFFERENT |
| `recovery.img` | 71,106,560 | `685d8fe9e9027f33305e8e56df2d2fcc` (same file, second db_path) | BOOT | `samsung/gta4xlwifi/vendor/etc` | duplicate row (join artifact, as Galaxy_A21S #1006) |
| `unsparse_super_empty.img` | 4,644 | `2661586e1e54c0b26a50028ebe25883d` | BOOT | `samsung/gta4xlwifi/radio` | **FOUND-MATCH** — byte-identical across all three hosted builds |
| `dtbo.img` | 8,388,608 | `8d225d9f79de14358870e0291e4d5a48` | DTB | `samsung/gta4xlwifi/radio` | FOUND-DIFFERENT |
| `vbmeta.img` | 4,096 | `2b67df5ee75932922451953d63a8ea7b` | AVB | `samsung/gta4xlwifi/radio` | FOUND-DIFFERENT |

All six md5-checked against the three hosted 23.2 nightlies (2026-11-14/07/10-31; 15 files, each sha256-verified against the builds API): the four rebuilt images match **none** of the three builds, while every size matches all three exactly — the DB rows are partition-fixed constants from an older LOS extract [F]. Hosted builds older than 2026-10-31 return 404 (probed 2026-09-19 through 2026-11-13) [N].

## Container layout [F] (parsed from the sha256-verified LOS 23.2 artifacts, 2026-11-14 build)

- **boot.img / recovery.img** — `ANDROID!` magic, header version 2, header_size 1660, page_size 2048. boot: kernel 37,771,296 B @ 0x10008000, ramdisk 1,572,920 B @ 0x11000000, dtb 135,168 B @ 0x10000000, second 0. recovery: identical kernel size, ramdisk 14,526,526 B, **recovery_dtbo 479,232 B @ 52,303,872** — exactly the `dtbo` hash-descriptor image_size inside vbmeta (Samsung's stock "dtbo" partition carries the recovery_dtbo blob). os_version raw field 0x200001ab does not decode per the AOSP bit layout (Samsung-legacy value) [I].
- **dtbo.img** — `DT_TABLE_MAGIC` 0xd7b7ab1e, big-endian **Samsung dt_table format** (32-byte header, not AOSP mkdtboimg's 60-byte header): 5 entries × 32 B, page_size 2048; offset/size chain verified exactly (192 → 95,040 → 190,084 → 284,952 → 379,820; total_size 478,748; zero-padded to the 8,388,608 partition size); every dt_offset begins with the DTB magic `d00dfeed`; `custom[0]/[1]` (little-endian) hold Samsung hw_rev selection pairs (0,3), (4,6), (7,7), (8,8), (9,255) [I for the hw_rev reading].
- **vbmeta.img** — `AVB0` v1.0, **algorithm_type 0 = unsigned** (zero-size auth block); release string `avbtool 1.3.0` at offset **128** (non-standard; AOSP puts it at 124); Samsung-era descriptor tag scheme (0 = property, 1 = hashtree, 2 = hash — differs from current AOSP constants). rollback_index = 1793491200 = 2026-11-01T00:00:00Z (build-month anti-rollback; the two older builds carry 2026-10-01). 24 descriptors: 17 properties (fingerprints `samsung/lineage_gta4xlwifi/gta4xlwifi:16/BP4A.251205.006/a412150b61:userdebug/{test,release}-keys`; security_patch system/system_ext/product 2026-11-01, **vendor 2024-05-01** — Samsung stock vendor); 2 hash descriptors (`boot` 39,485,440 B, `dtbo` 479,232 B — **stock Samsung sizes**, not the LOS artifact sizes, so this vbmeta does not verify the shipped LOS boot/dtbo); 5 sha1 hashtree descriptors (odm 389,120; product 2,467,872,768; system 1,126,703,104; system_ext 530,460,672; vendor 159,379,456; shared salt prefix `a5be78925b256f6b61c4daed5952b816`).
- **unsparse_super_empty.img** — NOT an Android sparse image (no 0xed26ff3a): `LP_METADATA_GEOMETRY_MAGIC` 0x616c4467 per AOSP `fs_mgr/liblp/include/liblp/metadata_format.h`; geometry struct_size 52, metadata_max_size 65,536, slot_count 2, logical_block_size 4096; metadata header at 4096 (`LP_METADATA_HEADER_MAGIC`, version 10.0, tables_size 420) declaring 5 empty partitions (system, system_ext, vendor, product, odm) in group `samsung_dynamic_partitions` and block device `super` with first_logical_sector 524,288; 4096 + 128 + 420 = 4644 = file size, exact. The DB name `unsparse_super_empty.img` is literally accurate — which is why this row, and only this row, md5-matches the DB [F].

## Interface facts

- The five radio files of the `other` family (cm/keystorage/sboot/uh/up_param — documented in `other.md`) are packed by the platform's releasetools into one `bota` partition: `android_device_samsung_gta4xl-common` `releasetools/releasetools.py` @ lineage-23.2 lines 65-70 — per-file 36-byte headers, header magic 3142939818, written to `/dev/block/by-name/bota`; lines 49-50 write dtbo.img/vbmeta.img to `/dev/block/by-name/dtbo` and `/dev/block/by-name/vbmeta` [F].
- LOS firmware recipe flashes the five radio files via heimdall as CM/KEYSTORAGE/BOOTLOADER/UH/UP_PARAM [F] (LOS wiki firmware template for gta4xlwifi, 2026-11-21).
- ISA: LOS YAML `architecture: arm64`; kernel repo `android_kernel_samsung_gta4xl` (4.14); Exynos 9611 = ARMv8-A (A73/A53). No ELF header claims are possible at metadata level (db_type BOOT/DTB/AVB; `isa_identified` empty in the matrix) [F + honest].

## Honest negatives

- The DB's boot-family md5s cannot be pinned to a hosted build: the four rebuilt images differ from all three hosted nightlies and older builds are no longer served. Sizes are the only surviving join key (they match exactly) [N].
- What actually verifies what at boot: the shipped vbmeta is unsigned (algorithm NONE) with stock Samsung hash sizes merged with LOS properties [OPEN].
- No mainline Exynos 9611 DTS exists in torvalds/linux (code search 2026-11-21: 0 hits) — consistent with the P3 no-mainline-basis inventory note [F].

## What would upgrade this finding

1. A retained older LOS nightly (or a stock SM-P610 AP dump) to md5-pin the four DB boot rows instead of size-joining.
2. Parse the boot.img kernel payload (compressed arm64 Image) for instruction-level ISA proof beyond metadata.
3. Correlate the five dt_table hw_rev pairs against Samsung service manuals to name each DTB variant.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments on the issue; adversarial audit ran the same day (identity, prior-art, kernel-citation, size and count claims all re-attacked; one kernel citation corrected pre-publication). Check: `gta4xlwifi SM-P610 boot.img dtbo vbmeta format` (web + GitHub code search, adineo-cmd/* excluded) → device trees, flashing guides and GSI threads only; nobody documents this device's boot rows or the Samsung dt_table variant it uses.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata, parsed public artifacts, and cited public sources.
