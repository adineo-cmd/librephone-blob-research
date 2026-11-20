# samsung Galaxy_F62 — `tz` family status (honest negative)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#1030](https://github.com/adineo-cmd/open-device/issues/1030)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, main 3ed58f4), `upstream-contribution/blob-database/device-inventory.csv`, `research/soc/per-soc-method-plans.md` (family grammar), public LineageOS device trees + TEE research (access dates below). No payloads were fetched; every number below is the output of a command run on the checkout or a fetch recorded verbatim.

**Verdict: the `tz` family is structurally ABSENT on Galaxy_F62 — not a census gap.** Zero census rows match the lab's `tz` grammar, and public ground truth for the device's firmware packages (the LineageOS extractor file list, which pulls *every* firmware file Samsung ships in the package) matches the census exactly, with no tz-grammar file in it. The device's TrustZone stack exists but travels in different carriers: the TEEGRIS OS inside the boot partition, loadable TAs under `/vendor/tee` + `/system/tee`, and an encrypted EL3 monitor inside S-Boot — none of which the upstream DB's blob census scopes.

## Device identity

| fact | value | source (access date) |
|---|---|---|
| model | SM-E625F (Galaxy F62); census firmware dir also nests SM-M625F (Galaxy M62, same hardware, rebranded) | [Samsung Newsroom launch release](https://news.samsung.com/in/samsung-launches-galaxy-f62-the-fullonspeedy-smartphone-with-flagship-exynos-9825-processor-64mp-quad-camera-and-7000mah-battery) (2026-11-20); [GSMArena](https://www.gsmarena.com/samsung_galaxy_f62-10740.php) (2026-11-20) |
| SoC | Exynos 9825: 2× Exynos M4 Cheetah @2.73 GHz + 2× Cortex-A75 @2.4 GHz + 4× Cortex-A55 @1.95 GHz; Mali-G76 MP12 | Samsung Newsroom / GSMArena (2026-11-20) |
| released | 2021-02-15 (India) | Samsung Newsroom (2026-11-20) |
| custom-ROM codename | `f62` (device-inventory `build_codename`) | repo census |

## Census status — what the matrix holds

`coverage-matrix.csv` row census for Galaxy_F62 (all rows evidence class P3, metadata-only):

```
awk -F, '$1=="Galaxy_F62"{print $4}' coverage-matrix.csv | sort | uniq -c
      6 boot
      4 modem
     55 other
```

65 rows, 384,339,292 bytes (`device-inventory.csv`: `blob_rows_devices_sql=65`, `total_bytes_devices_sql=384,339,292`), 64 distinct md5s (recovery.img 71,102,464 B appears at two `db_path`s with md5 `6cfdbe80f91f8b06102939bd0287335e`). Path breakdown: `samsung/f62/firmware/SM-E625F` 8 rows, `SM-M625F` 8 rows, `samsung/f62/radio` 5, `samsung/f62/vendor/etc` 5, `samsung/f62/vendor/firmware` 38, `samsung/f62/vendor/firmware/nfc` 1.

Boot-family rows (the Android images): boot.img 61,865,984 B (db_type BOOT), recovery.img 71,102,464 B ×2 paths, unsparse_super_empty.img 4,644 B, dtbo.img 8,388,608 B (DTB), vbmeta.img 4,096 B (AVB). Modem-family rows: modem.bin 48,153,968 B and modem_debug.bin 5,242,880 B, once per model variant.

## The `tz` grammar — zero hits

Family grammar from `research/soc/per-soc-method-plans.md` ("Family-classification rules used in this file"): tz = `tz / keymaster / qsee / cmnlib / hyp / devcfg / uefisecapp / featenabler / hdcp / widevine / soter / smplap`.

```
awk -F, '$1=="Galaxy_F62" && ($5 ~ /^(tz|keymaster|qsee|cmnlib|hyp|devcfg|uefisecapp|featenabler|hdcp|widevine|soter|smplap)/
      || $6 ~ /^(tz|keymaster|qsee|cmnlib|hyp|devcfg|uefisecapp|featenabler|hdcp|widevine|soter|smplap)/)' coverage-matrix.csv | wc -l
0
```

The same scan over **all** samsung rows: 0 of 914 (family spread: boot 112, other 712, modem 42, gpu 23, wifi 19, bt 6 — 17 samsung devices carry census rows). A substring fallback (`tee|tz|sehos|tbase|mc` on filenames) hits only `fimc_is_fw_mcu.bin` / `fimc_is_lib.bin` / `fimc_is_rta.bin` — camera ISP files whose names merely contain `mc`; no TEE file.

For contrast, the same DB carries 4,264 tz-family rows across nine vendors: oneplus 1,669, xiaomi 1,185, motorola 731, fairphone 278, nothing 179, realme 120, google 51, fxtec 43, sony 8. The lab's own tz RE artifacts (`research/fleet/dsp-tz-map.md`, `research/fleet/qsee-crossgen.md`, `research/qualcomm/docs/trustzone-census.md`) are likewise all Qualcomm-side. **Samsung's census is not a thinner copy of the Qualcomm one — the grammar itself never occurs on it.**

## Why structural, not a census gap

Ground truth for what Samsung ships in the F62 firmware packages, from the LineageOS device tree's extract list ([android_device_samsung_f62, lineage-23.2, `proprietary-firmware.txt`](https://github.com/LineageOS/android_device_samsung_f62/blob/lineage-23.2/proprietary-firmware.txt), fetched 2026-11-20): exactly eight firmware files per model, from packages `E625FDDS7CXK1` (SM-E625F) and `M625FXXS7CXK1` (SM-M625F) — cm.bin, dqmdbg.img, keystorage.bin, modem.bin, modem_debug.bin, sboot.bin, uh.bin, up_param.bin.

```
diff <(awk -F, '$1=="Galaxy_F62" && $13 ~ /firmware\/SM/ {print $6}' coverage-matrix.csv | sort -u) \
     <(printf "cm.bin\ndqmdbg.img\nkeystorage.bin\nmodem.bin\nmodem_debug.bin\nsboot.bin\nuh.bin\nup_param.bin\n" | sort)
IDENTICAL
```

The census's 16 firmware-dir rows are **exactly** the public package file list — the census missed nothing in the package. The eight files are the same grammar the sibling Exynos 9820/9825 trees declare (beyond1lte SM-G973F/G973N, packages `G973FXXSGHWC2`/`G973NKSU7HWD3`; d1 SM-N970F, package `N970FXXS9HWHA` — each adds only `param.bin`, fetched 2026-11-20). None of the three trees lists `ldfw.bin`, `tzsw`, `tz.img`, `keymaster`, `devcfg`, `hyp.img`, or any other tz-grammar file. The Google Tensor devices in this same DB ship `tzsw` + `ldfw.img` in their radio dirs — the grammar is real, it just never ships on Exynos phone packages.

Per-file corroboration from the census (sizes + md5s, metadata-only): cm.bin 7,340,032 B (`7c97c71e645e591d6acea65b308b5ca3` SM-E625F / `29e75b92d727bd388d0d7992f3843f69` SM-M625F), sboot.bin 4,194,304 B — byte-identical size on all 10 Exynos 9820/9825 samsung devices that carry BL rows — keystorage.bin 524,288 B, uh.bin 276,120 B, up_param.bin 2,938,880 B, dqmdbg.img 53,360 B.

## Where the TrustZone stack actually is (public research)

The Exynos 9825 generation runs Samsung's TEEGRIS, not the Qualcomm TEE grammar the `tz` family encodes:

| component | EL / carrier | evidence |
|---|---|---|
| Secure monitor | EL3, **encrypted in flash**, inside S-Boot | [Quarkslab, A Deep Dive Into Samsung's TrustZone (Part 1), 2019-12-10](https://blog.quarkslab.com/a-deep-dive-into-samsungs-trustzone-part-1.html): monitor implementation found in SBOOT, based on Arm Trusted Firmware with Samsung custom `rt_svc_desc` services; "high-entropy section, which suggests it was encrypted" from Galaxy S8 onward. Keysight: "in Samsung's case, it is stored encrypted in a flash" |
| TEEGRIS kernel | S-EL1, plain text, **in the boot partition** | [Keysight, Breaking TEE Security Part 1, 2021-02-23](https://www.keysight.com/blogs/en/tech/nwvs/2021/02/23/breaking-tee-security-part-1): "TEEGRIS is a relatively recent TEE OS, introduced by Samsung on the Galaxy S10. Most of the newer (starting from 2019) Samsung phones that have Exynos chipsets will also have TEEGRIS"; "the kernel is stored in plain text in the boot partition"; boot image also carries `startup.tzar` (TSS, ACSD, root_task; signature verified at boot) |
| Loadable TAs | S-EL0, **`/vendor/tee` and `/system/tee`** | Keysight: ~30 loadable TAs on the S10; UUID filename, 8-B header (SEC2/SEC3/SEC4 + length), ELF payload (SEC4 encrypted; in practice SEC2/SEC3 on S10/S20), group/version metadata, X.509 RSA signature; anti-rollback via RPMB |
| Keymaster TA | inside TEEGRIS | [IACR ePrint 2022/208](https://eprint.iacr.org/2022/208.pdf): sboot.bin is Samsung's secure boot for Exynos, based on ATF; Keymaster TA design across TEEGRIS generations |

Predecessor TEE: Kinibi (Trustonic) through the S9 generation; TEEGRIS from S10 on ([Quarkslab](https://blog.quarkslab.com/a-deep-dive-into-samsungs-trustzone-part-1.html)). Tooling: [quarkslab/samsung-trustzone-research](https://github.com/quarkslab/samsung-trustzone-research) (Kinibi-era).

Mapping onto the F62 census: the boot-partition carrier is present as boot.img 61,865,984 B (`samsung/f62/radio`), and the TA carrier (`/vendor/tee`) is **outside the upstream DB's catalog scope** — its samsung `vendor` paths cover `vendor/firmware` + `vendor/etc` radio files only. So the TEE is not missing from the device; it is carried outside the two places this DB censuses for samsung.

## Upstream redistribution status (checked 2026-11-20)

linux-firmware `WHENCE` (git.kernel.org, 540,253 B): grep `samsung|exynos` → only `s5p-mfc` (MFC video codec driver); zero TEEGRIS/TrustZone entries. torvalds/linux master: 18 code hits for `9825`, none Samsung Exynos. No mainline or linux-firmware surface exists for this TEE — it never leaves the device, consistent with the census's metadata-only P3 rows.

## Honest negatives

- The F62 `tz` family (lab grammar) is absent: proven structurally, by census scan + exact public package-list match. **No census gap in the firmware packages.**
- Whether F62's boot.img embeds the TEEGRIS kernel + `startup.tzar` is **inferred from the S10-generation architecture, not verified on F62 payloads** — the payload is not on this box (metadata-only per Phase 2 rules) and boot.img 61,865,984 B cannot be decomposed from metadata alone. [OPEN]
- `/vendor/tee` + `/system/tee` TA sets on F62 are **uncatalogued by the upstream DB** (scope limitation, not absence). A TA census would need the super.img vendor extraction. [OPEN]
- The EL3 monitor is encrypted in flash; its content is beyond public documentation on any 9820/9825 device, F62 included. [OPEN]
- Census-quality note (Rule 1): `device-inventory.csv` carries `count_csv_total=68` vs `blob_rows_devices_sql=65` for F62 — a 3-row discrepancy in the upstream DB's own count source, recorded here rather than silently reconciled.

## What would upgrade this finding

1. Payload fetch of the `BL_E625F` package (Phase 3 gate): verify the 8-file set byte-for-byte against the census `md5_db` values above.
2. super.img vendor walk: enumerate `/vendor/tee` UUID TA files (format fully specified by Keysight) → the F62 TA census the DB cannot provide.
3. boot.img walk: locate the TEEGRIS kernel + `startup.tzar`, classify the SEC2/SEC3/SEC4 TA forms present.

## RULE 0 record (2026-11-20)

Searches before this write-up (exact strings in issue #1030 SEARCH/NO-PRIOR-ART comments): GitHub code search `SM-E625F TEEGRIS OR trustzone OR tz` (adineo-cmd/* excluded) → 0; web queries on F62/Exynos 9825 TEE layout → adjacent architecture research only (Quarkslab 2019-12-10, Keysight 2021-02-23, IACR ePrint 2022/208); linux-firmware WHENCE + torvalds master checked by fetch 2026-11-20. No one has documented the F62 TEE layout or the tz-grammar absence on samsung devices; this doc is the delta.

Not legal advice; no proprietary payload was accessed or committed — all device facts are metadata (sizes, md5s, paths) plus published research.
