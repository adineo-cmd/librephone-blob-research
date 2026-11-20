# samsung Galaxy_F62 — `boot` family status (6 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1024](https://github.com/adineo-cmd/open-device/issues/1024)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 06bfd27), the device-identity doc `docs/devices/samsung/Galaxy_F62/tz.md` (#1030), AOSP boot-image/AVB public format specs. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the boot family is PRESENT as the standard Android verified-boot set — the Samsung shape with no Qualcomm bootchain grammar.** 6 rows (5 distinct files; recovery.img appears at two census paths with one md5), all corpus-unique, all P3. Device identity and the Exynos boot-chain context are #1030's, cited throughout.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy F62 (SM-E625F); census nests SM-M625F (Galaxy M62) firmware | `device-inventory.csv` [F]; [Samsung Newsroom](https://news.samsung.com/in/samsung-launches-galaxy-f62-the-fullonspeedy-smartphone-with-flagship-exynos-9825-processor-64mp-quad-camera-and-7000mah-battery) + [GSMArena](https://www.gsmarena.com/samsung_galaxy_f62-10740.php) (2026-11-20, via #1030) |
| SoC | Samsung **Exynos 9825** (2x M4 Cheetah + 2x A75 + 4x A55; Mali-G76 MP12) | #1030 identity table [F] |
| census scope | 65 rows in 3 families (other 55, boot 6, modem 4); 384,339,292 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 6 rows [F]

```
awk -F, '$1=="Galaxy_F62" && $4=="boot"{print $6"|"$7"|"$8"|"$13"|"$14}' coverage-matrix.csv | sort
```

| file | bytes | md5 (upstream DB) | db_type | db_path | role [I] |
|---|---:|---|---|---|---|
| boot.img | 61,865,984 (59 MiB) | `21b4804230c1a3bd1dae726b4627da72` | BOOT | radio | AOSP boot image (kernel + ramdisk) |
| recovery.img | 71,102,464 (68 MiB) | `6cfdbe80f91f8b06102939bd0287335e` | BOOT | radio **and** vendor/etc | AOSP recovery image — same file packaged at two census paths, one md5 |
| unsparse_super_empty.img | 4,644 | `c36b42ebde9643412c110c4a4f1f10a5` | BOOT | radio | dynamic-partition placeholder |
| dtbo.img | 8,388,608 (8 MiB) | `45553939f944bc940f58ec1221f18dda` | DTB | radio | device-tree overlay image |
| vbmeta.img | 4,096 | `f6759b32e72155a568b336fa7e76c46a` | AVB | radio | AVB metadata (corpus's 4,096-B class) |

Distinct bytes: 61,865,984 + 71,102,464 + 4,644 + 8,388,608 + 4,096 = 141,865,796 [F]. All 5 distinct md5s **corpus-unique to Galaxy_F62** [F] — per-build signed images.

## Samsung-shape observations [F]

- **No Qualcomm bootchain grammar** (xbl/abl/aop/cpucp/qupfw/shrm) — correct for an Exynos device: Samsung's own chain (S-Boot et al.) ships in the BL-package files, which this DB holds under the `firmware` census dir (cm.bin 7,340,032; sboot.bin 4,194,304; uh.bin 276,120; up_param.bin 2,938,880 — see #1030's file table). The Android images here are the AOSP triple plus recovery.
- **recovery.img dual-path**: radio + vendor/etc copies with one md5 — the same Samsung census convention seen on Galaxy_A71/Note10_5G (single rows) and Galaxy_A21S (duplicated rows, #1006). One file, packaged twice; not two images.
- boot.img 61,865,984 B is the Samsung magnitude shared with Galaxy_Tab_S6_LTE/Wifi (53-device 96-MiB magnitude does not apply here — Samsung phone/tablet builds use 36-71 MiB sizes per #916's spread); recovery.img 71,102,464 B matches the Tab_S7 pair's size.
- vbmeta.img 4,096 B = the corpus's small class (10 rows) vs the modal 8,192 B (94 rows) — the same AVB0 v1.0 format at a smaller descriptor count [F, size only].

## ISA proof and interface facts

- Boot-image internals (header version, kernel ISA) are not provable from metadata — [OPEN]; the Exynos 9825 is an AArch64 part [F].
- Interface [I, labeled]: AVB verifies boot/dtbo/recovery; Samsung download-mode flashing (Odin/Lheimdal). Not device-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- Whether F62's boot.img embeds the TEEGRIS kernel + `startup.tzar` (the #1030 [OPEN]) applies here too — the boot partition is the TEE carrier per the S10-generation architecture, unverified without payloads.
- Header-version and GKI status of boot.img/recovery.img are [OPEN] (F62 launched on Android 10 with an Android 11 update — GKI unlikely, but metadata cannot prove it).

## What would upgrade this finding

1. Payload fetch: parse boot.img/recovery.img per the AOSP boot-image format; locate the TEEGRIS payload (#1030's upgrade path step 3).
2. Cross-check the two recovery.img paths in the upstream DB stream (lead-level catalog hygiene, as in #1006).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy F62 boot.img dtbo vbmeta analysis` (web + GitHub code search, adineo-cmd/* excluded) -> guides only. Nobody documents F62's boot rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus public specs and the cited sibling doc.
