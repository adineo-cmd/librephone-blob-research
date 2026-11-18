# Third Device Population — OnePlus 8 (`instantnoodle`, SM8250) — VOOC fast-charge pair proven byte-for-byte

WORKORDER-001 desktop session, third-device population and leverage-entry proof. Raw artifacts stay local under `data-fetch/second-device/instantnoodle/`; census lives at `analysis/out/third-device-census.csv`, fleet join at `analysis/out/third-device-fleet-join.json`. Nothing was committed to `librephone-blob-research/`.

## Headline

**The lab's #1 leverage entry is proven.** Both `oplus_vooc_fw.bin` (md5 `1ec85cbd137458de72d76822a05a7595`, 6,464 B) and `oplus_vooc_fw_rk826.bin` (md5 `76835ccc9dd4ad08922e9d7616bdf4ac`, 12,432 B) are present **byte-for-byte** (md5 exact, size exact) in the official LineageOS nightly for the OnePlus 8, in exactly the 9 + 9 `odm/firmware/fastchg/` directories the coverage matrix records for `oneplus/instantnoodle`.

## Device chosen and why

- **Device:** OnePlus 8 (`instantnoodle`, matrix identity `OnePlus_8`, vendor `oneplus`, SoC Qualcomm SM8250 Snapdragon 865).
- **Method step 1 (matrix grep):** rows whose `md5_db` equals the two authoritative VOOC md5s appear only on OnePlus_8 / OnePlus_8_Pro / OnePlus_8T / OnePlus_9R (all SM8250), all with `db_path` `oneplus/<codename>/odm/firmware/fastchg/<dir>` — so the pair lives in the **odm** partition of an official LineageOS payload. 36 matrix rows carry each md5 (9 fastchg dirs × 4 devices).
- **Candidate selection:** `instantnoodle` queried first per workorder preference (OnePlus 8 preferred over 8 Pro); API 200 with current builds, so no further codenames needed. `instantnoodlep`/`kebab`/`lemonades` remain populated-by-proxy through content-identical blobs (see fleet join).

## LineageOS API URLs used

- Device: `https://download.lineageos.org/api/v2/devices/instantnoodle` → 200, `"name":"8"`, `"oem":"OnePlus"`, `"versions":["23.2","24.0"]`
- Builds: `https://download.lineageos.org/api/v2/devices/instantnoodle/builds` → 3 nightlies: 24.0-20261117, 24.0-20261110, 23.2-20261006
- Zip: `https://mirrorbits.lineageos.org/full/instantnoodle/20261117/lineage-24.0-20261117-nightly-instantnoodle-signed.zip`

## Build downloaded and verified

| field | value |
|---|---|
| zip | `lineage-24.0-20261117-nightly-instantnoodle-signed.zip` |
| size | 1,385,279,498 bytes (1.29 GiB — inside the one-zip cap) |
| sha256 (API) | `7fc7267b31ccbddd34d39dd86b4cc1f8c7dc57a9fcffc64cd1b1af17ecedf5e2` |
| sha256 (local sha256sum) | `7fc7267b31ccbddd34d39dd86b4cc1f8c7dc57a9fcffc64cd1b1af17ecedf5e2` |
| match | EXACT — sha256-verified **Y** |

Download: `curl -L -sS --retry 8 --retry-delay 5 --retry-all-errors -o <zip>`. The network stalled once at 588 MB (curl died silently); resumed with `curl -C -` against the same URL and brought to full size. Logged as an honest network failure; the single downloaded zip was never replaced.

## Payload manifest (30 partitions)

abl 225,280 / aop 204,800 / bluetooth 454,656 / boot 100,663,296 / cmnlib 401,408 / cmnlib64 520,192 / devcfg 57,344 / dsp 67,108,864 / dtbo 25,165,824 / featenabler 90,112 / hyp 450,560 / imagefv 1,191,936 / keymaster 266,240 / logo 344,064 / modem 192,278,528 / multiimgoem 16,384 / odm 80,879,616 / product 2,544,676,864 / qupfw 57,344 / recovery 100,663,296 / storsec 24,576 / system 1,179,877,376 / system_ext 611,561,472 / tz 3,194,880 / uefisecapp 126,976 / vbmeta 8,192 / vbmeta_system 4,096 / vendor 457,732,096 / xbl 3,985,408 / xbl_config 94,208. Ops mix: REPLACE_XZ dominant, plus REPLACE_BZ and REPLACE (all supported by `payload_dump.py`).

**This payload carries the OnePlus 6 pattern**: `bluetooth` and `modem` partitions exist alongside the OS partitions (unlike the second device, `larry`, whose 24.0 payload had none).

## Container types per partition (first-16-byte probe + magic probes)

| container | partitions |
|---|---|
| **FAT16** (`EB 3C 90`, MSDOS5.0) | bluetooth.img, modem.img |
| **EROFS** (`E2 E1 F5 E0` @ 1024) | odm.img, vendor.img |
| **EXT4** (`53 EF` @ 0x438) | dsp.img, product.img, system.img, system_ext.img |
| **ELF** (`7F 45 4C 46`) | abl, aop, cmnlib, cmnlib64, devcfg, featenabler, hyp, imagefv, keymaster, multiimgoem, qupfw, storsec, tz, uefisecapp, xbl, xbl_config |
| raw | boot/recovery (bootimg `ANDR`), dtbo (`D7B7AB1E`), logo (zero head), vbmeta/vbmeta_system (`AVB0`) |

## Extraction steps

| step | result |
|---|---|
| `unzip -o <zip> payload.bin` | OK |
| `payload_manifest.py payload.bin` | OK — 30 partitions |
| `payload_dump.py` × 30 | OK — all partitions dumped |
| FAT16 probe | bluetooth.img and modem.img both FAT16 — OnePlus 6 pattern holds on SM8250 |
| `fat_extract.py bluetooth.img bt-fat` | OK — 5 files extracted, `size_check=true` for all |
| `fat_extract.py modem.img modem-fat` | OK — 654 files extracted (nested dirs flattened by `dir_name` join), `size_check=true` |
| `fsck.erofs --extract=tree-odm odm.img` | OK — erofs-utils 1.7.1-1build2 .deb downloaded and unpacked with `dpkg -x` into `data-fetch/second-device/instantnoodle/tools-erofs/` (no sudo; no /tmp leftover from prior sessions existed, so re-fetched) |
| `fsck.erofs --extract=tree-vendor vendor.img` | OK |
| `debugfs -R 'rdump / dsp-ext4' dsp.img` | OK — the dsp partition is EXT4 (not EROFS), so the prescribed debugfs path worked here |
| Symlink handling | `tree-vendor/rfs` (84 dangling symlinks into /data) and `tree-vendor/odm -> /odm` excluded from the census via the regular-file check |

## VOOC verification (the leverage entry)

| file | matrix md5 | matrix size | local md5 (all 18 copies) | local size | match | fastchg dirs found |
|---|---|---|---|---|---|---|
| `oplus_vooc_fw.bin` | `1ec85cbd137458de72d76822a05a7595` | 6,464 | `1ec85cbd137458de72d76822a05a7595` | 6,464 | **Y — EXACT** | 19811, 19813, 19821, 19823, 19835, 19837, 19839, 19841, 19855 (9/9 matrix db_paths) |
| `oplus_vooc_fw_rk826.bin` | `76835ccc9dd4ad08922e9d7616bdf4ac` | 12,432 | `76835ccc9dd4ad08922e9d7616bdf4ac` | 12,432 | **Y — EXACT** | 19805, 20806, 20807, 20808, 20809, 2080E, 20819, 20828, 20838 (9/9 matrix db_paths) |

All 18 `odm/firmware/fastchg/` matrix rows for `oneplus/instantnoodle` are now proven present byte-for-byte from an official source — 100% of the instantnoodle fastchg matrix coverage. The tree additionally carries 25 fastchg blobs (16 distinct md5s) the matrix does not list for this device: newer rk826 variants (dirs 20135/20137/20139/20235/21615/21619/2169A/2169B/20061/20062), `oplus_vooc_fw_rt5125.bin` (20161/20163/20351), and older `oplus_vooc_fw.bin` builds (19063/19065/19066/19067/19161/19361/19362/19705/19706/19795/20607) — free fleet-delta intelligence on top of the proven pair.

## Census highlights (`analysis/out/third-device-census.csv`, 2,107 rows)

Header: `device,vendor,soc,family,file,bytes,sha256,md5,public_status` (`populated-local-session` throughout). Row origins: 1,352 odm/vendor tree files + 2 explicit odm-root blobs (`etc/irissoft.fw`, `lib/libfastov_dsp.so`) + 19 `<partition:*.img>` rows (16 ELF firmware partitions incl. tz, plus bluetooth/modem/dsp containers) + 654 `<modem-fat:...>` + 5 `<bt-fat:...>` FAT-extracted files + 75 `dsp/...` rows from the EXT4 dsp partition.

| family | rows | contents |
|---|---|---|
| adsp | 84 | vendor+odm `lib/rfsa/adsp` (fastrpc/hta/ktv skel libs) 48, dsp-partition adsp modules 36 |
| bt | 6 | bluetooth.img container + 5 bt-FAT TLV/VER/BIN files (QCA TLV calibration/firmware set) |
| cdsp | 30 | dsp-partition cdsp modules (fastrpc_shell_3, vpp_*, nn_preproc, snpe skels) |
| gpu | 7 | a650_gmu.bin, a650_sqe.fw, a650_zap.{mdt,elf,b00,b01,b02} |
| modem | 662 | modem.img container + 654 modem-FAT files (stock modem/image tree: adsp/cdsp/tz/cmnlib mdt-bXX splits, .mbn, .tlv) + ipa_fws.{mdt,elf,b00-b04} |
| tz | 1 | tz.img (single signed ELF) |
| wifi | 5 | bdwlan.elf, WCNSS_qcom_cfg.ini, wpa_supplicant(.overlay).conf, p2p_supplicant_overlay.conf |
| other | 1,312 | fastchg 43 (18 target + 25 variants), odm/firmware haptics RTP + tfa98xx.cnt + tp/, gfp9608/gfp9638 fast-pair mdt-bXX sets, sn100u.bin, CAMERA_ICP.elf, ipa_uc, dsp sdsp modules, qcril_database, firmware partitions abl/aop/cmnlib/devcfg/hyp/keymaster/xbl/xbl_config etc. |

Scope discipline: blob-bearing trees only (firmware incl. fastchg/tp/haptics, rfsa/adsp, gpu, bt/wifi configs, radio/qcril_database, dsp partition); OS `.so` trees (`lib/`, `lib64/`, `bin/`), camera/acdbdata/sensor/faceunlock tuning configs, overlays, and all dangling symlinks excluded, matching the enchilada/larry methodology. Empty dirs (`vendor/bt_firmware`, `vendor/dsp`, `vendor/firmware_mnt`) yielded nothing.

## Fleet join (global, name-independent)

`analysis/out/third-device-fleet-join.json`: **492 of 2,107 census files carry an md5 that exists somewhere in the matrix** — 98 match on (filename, md5), 394 are content aliases (same md5 under a different name). 454 distinct matrix md5s matched out of 15,091. Top matrix identities hit: OnePlus_8 (488), OnePlus_8_Pro (470), OnePlus_8T (95), OnePlus_9R (95), then Motorola Edge_30_Neo/G-Stylus/G34/G82 (~17-18 each). Split by family: modem 372 (2 exact + 370 alias), other 110, bt 6, gpu 3, tz 1.

**Inverse join (instantnoodle's own matrix coverage):** 504 matrix rows exist for `oneplus/instantnoodle/*`; **493 of their md5s (98%) are matched by this census** — including all 113 tz-family, 22 adsp, 12 cdsp, 9 modem and 32 wifi rows, and all 18 fastchg rows. The 11 unmatched rows are 6 `other` + 5 `boot` (kernel/boot-image rows expected to differ between the matrix capture build and this nightly).

The modem FAT volume reproduces the OnePlus 6 finding on SM8250: it stores the stock `modem/image` tree (e.g. matrix row `cmnlib.b01` 19,984 B md5 `bbb4a744...` = `<modem-fat:PCAFUI~2/ZSB6IT~2.B01>`; `cmnlib.b02` 347,220 B = `<modem-fat:PCAFUI~2/ER5IQG~2.B02>`), which is why 370 alias hits land on tz/adsp/cdsp matrix rows recorded under `modem/image`.

## Method notes for future sessions

1. LineageOS 24.0 payloads for SM8250 OnePlus devices: OS partitions are **EROFS** (`fsck.erofs --extract`, erofs-utils 1.7.1 deb + `dpkg -x`, no sudo), but the **dsp partition is plain EXT4** (debugfs works), and **bluetooth/modem are FAT16** (`fat_extract.py`). Probe every partition; do not assume one container type per build.
2. `fat_extract.py` reads only the 8.3 short names (no LFN records), and flattens dirs into `dir1_dir2_name` filenames. Census display paths reconstruct `/` by replacing `_`, which is correct for this volume's mangled short names but would corrupt display (not md5s) if a short name contained `_`.
3. The bluetooth FAT BPB declares 67,108,864 volume bytes while the partition image is 454,656 — the extraction is still consistent (`size_check=true` per file); treat BPB-claimed size vs image size mismatch as expected on these OEM volumes.
4. Download resilience: mirrorbits drops long transfers; `curl -C -` resume against the same URL completes the same zip and sha256 verification still passes.

## Honest negatives

1. **0/84 adsp-family census rows matched the matrix.** This SM8250 build ships no `bm2n*` fleet files (its rfsa/adsp holds fastrpc/hta/ktv skel libs only); the instantnoodle matrix adsp rows all reference `modem/image`, not `lib/rfsa/adsp`. The bm2n fleet coverage must be proven on its own carriers (already done for `larry`).
2. **11/504 instantnoodle matrix md5s unmatched** (6 other, 5 boot) — attributable to build drift (nightly vs the matrix capture build), not extraction failure.
3. **Partition content not byte-verified against payload metadata** beyond size (`payload_dump.py` writes what the payload defines); container-level sha256 rows are recorded for every partition in the census for future cross-checks.
4. FAT short-name display paths are 8.3-mangled; long names are not recoverable from these volumes with the current tool.
5. All 19 firmware/OS partition images plus payload remain local-only under `data-fetch/second-device/instantnoodle/` (uncommitted, per lab rules).
