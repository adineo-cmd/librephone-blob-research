# Device census — Galaxy Tab A 8.0 (2019) Wi-Fi (`Galaxy_TabA_8.0`, `gtowifi`, SM-T290)

Issue adineo-cmd/open-device#503. Claimed `CLAIM ZC-2 zcode 2026-11-20T17:00:47Z`.
Work date: 2026-11-20 (all searches run that day; adversarial audit same session).
Gate -1 verdict: **NEW**. Gate 0 verdict: **NO-PRIOR-ART** (adversarially audited, survived).
Deliverables: this note plus `data/fleet/Galaxy_TabA_8.0-census.csv`
(sha256 `d9a68c74d09904e76bad7869ef91c73160a5fd2a9e36626b68f8cffb61009c36`, 1336 rows).

## Device chosen and why

Non-phone tablet required for the site's every-device-class scope. Package
state was `count_known`: 0 coverage-matrix rows, upstream count 44, no
per-file census anywhere. It is also the only Samsung tablet in the inventory
whose official LineageOS support is current (22.2 nightlies as of
2026-11-18) while both its device tree and vendor tree became inaccessible
on GitHub during the session — a provenance story worth recording while the
evidence is still obtainable.

## Identity, hardware and SoC (issue checklist items 2 and 3)

Codename confirmation from the inventory:
`upstream-contribution/blob-database/device-inventory.csv:152` —
`samsung,Galaxy_TabA_8.0,gtowwifi,...` with `build_codename=gtowifi`.
External confirmation: LineageOS `lineage_wiki` `_data/devices/gtowifi.yml`
(`codename: gtowifi`, `models: [SM-T290]`, `name: Galaxy Tab A 8.0 (2019)`,
`type: tablet`). `gtowifi` maps to SM-T290 and to nothing else; the older
Tab A 8.0 (2015) SM-T350 is `gt58wifi` and the Tab A 7.0 (2016) SM-T280 is
`gtexswifi` (both verified against kernel-tree descriptions). The LTE
sibling is SM-T295.

- `type=tablet` — hardware fact: 8.0" TFT LCD slate, 5100 mAh (GSMArena,
  Wikipedia); LineageOS wiki YAML `type: tablet`. Confirmed.
- `build_variant=mobile` — the image taxonomy: official artifacts are a
  standard Android signed OTA zip (~1.03 GB) plus
  boot/dtbo/recovery/vbmeta images (download.lineageos.org API v2); no ATV
  build exists for this device. Confirmed.
- SoC — the repo records **nothing beyond the codename**:
  `device-inventory.csv:152` has empty `soc`/`soc_source`;
  `site/out/devices/galaxy-taba-8-0.html` renders "SoC: not recorded";
  grep for `SM4250|SDM429|QM215|Snapdragon 429` finds no row tied to this
  device anywhere in the checkout. Verified externally: **Qualcomm SDM429
  Snapdragon 429** (12 nm, Adreno 504, 4x Cortex-A53 @ 2.0 GHz) —
  LineageOS wiki YAML `soc:` field, GSMArena spec page, the vendor kernel
  defconfig `arch/arm64/configs/lineageos_gtowifi_defconfig` in
  `LineageOS/android_kernel_samsung_sdm429` (branch lineage-22.2) with
  `CONFIG_ARCH_QM215=y`, `CONFIG_ARCH_SDM429=y`, lk2nd
  `Documentation/devices.md` ("Samsung Galaxy Tab A 8.0 2019 (gtowifi)"),
  /e/OS device page, pmaports `samsung-gtowifi`. The silicon is
  msm8917-derived; `qm215` is the vendor-kernel platform name for this
  family (qcom,msm-id 386 in `qm215.dtsi`), distinct from SDM429's socinfo
  id 354. Wording caution: `QM215` is formally Snapdragon 215's model
  number (28 nm, Adreno 308) — do not write "QM215 = Snapdragon 429";
  SDM429 is the correct part id and `SM4250` (Snapdragon 460) is wrong for
  this device.

## What the repo already knew (Gate -1)

- Coverage matrix: 0 of 33,917 rows in
  `upstream-contribution/blob-database/coverage-matrix.csv` — "0 matrix
  rows" is exact.
- Upstream count: `site/data/upstream-counts.csv:16` —
  `Galaxy_TabA_8.0,samsung,44,librephone-upstream/data/count.csv (9339 rows)`;
  echoed in `device-inventory.csv:152` (`count_csv_total=44`,
  `extract_status_22.2=fails`) and
  `data/fleet/devices-001-222.csv:4748`
  (`listed-not-populated`, `P3; extract22.2=fails`).
- `state=count_known` is derived, not hand-written (`src/lib/data.ts:81`).
- `research/devices/` never existed in the checkout or the history
  (`git log --all -- research/devices/` empty;
  `docs/REPO-STATE-MAP.md:15` — "Device package | 245 | NEW").

## Prior art (RULE 0, with adversarial audit)

Recorded queries (all 2026-11-20): GitHub code/repo search
`"gtowwifi" "proprietary_files" OR "proprietary-files.txt"`,
`"gtowwifi" blob inventory OR census OR "blob matrix" OR "blob list"`,
`"gtowwifi" "vendor partition"`,
`"SM-T290" "firmware table" OR "blob table" OR "partition table"`;
authenticated `gh search code "gtowwifi"` (0 results); Sourcegraph
`context:global gtowwifi` (0); GitLab/Gitee project search (0); XDA threads
4535635 (official LOS 22.2), 4803222 (mainline LOS 23.2), 4795892 (T295
port) — no blob census posted; Reddit r/LineageOS; postmarketOS wiki
`samsung-gtowifi` (archived porting page, no inventory); LWN/HN (none);
arXiv:2410.11075 "Keep Me Updated" (13,901 firmware images, aggregate
GPU-blob statistics only — no SM-T290, no per-device enumeration);
AndroidDumps search for T290/gtowifi (none); HuggingFace dataset search
(none); opensource.samsung.com SM-T290 kernel 4.9 (source releases only).
Tooling caveat recorded: GitHub legacy code search, grep.app (429) and the
GitHub web code-search UI returned broken/rate-limited/empty results even
for control queries with provable matches, so all absence claims were
re-verified with direct API probes and Wayback lookups instead of search
indexes.

Verdict **NO-PRIOR-ART**: nobody has published a per-file census (sizes,
hashes, format classification) of gtowifi blobs. Closest existing work, for
the record: arXiv:2410.11075 (aggregate only) and the public per-file *list*
(not census) in `Manoel26/lineageOS24-gtowifi` — a community mirror of the
official gtowwifi device tree whose `proprietary-files.txt` has 1,335
non-comment entries and whose header records the extraction source:
`gtoxx-user 11 RP1A.200720.012 T295XXS6CWG6 release-keys` (LTE-sibling
firmware). A dedicated adversarial audit re-attacked the verdict with 18
further queries; it survived.

## Public blob set — the census (issue checklist item 1)

Source: `TheMuppets/proprietary_vendor_samsung_gtowwifi`, branch
`lineage-22.2`, cloned 2026-11-20. HEAD
`6c3f39621fa61f44c20a10891c694fce61d2ee48` (commit dated 2025-06-22,
message "gtoxx-user 11 RP1A.200720.012 T295XXS6CWG6 release-keys" — the
vendor set is extracted from the SM-T295 LTE Android 11 release-keys dump,
matching the mirror header above).

Availability caveat, recorded honestly: the repo was accessible at
retrieval time and the GitHub trees API listing (`truncated: false`,
sha `6c3f3962...`) cross-checked against the local clone with zero
mismatches (1340 blobs, 308,126,973 bytes; every worktree file re-hashed
against its git blob id). Later the same day it returns 404 on
authenticated API and web from two independent accounts, with no forks,
mirrors or Wayback snapshots — the same GitHub visibility flapping already
observed for `LineageOS/android_device_samsung_gtowwifi` (404; last public
capture 2025-07-17). The census therefore stands on the locally verified
clone; the commit SHA above pins it.

Census numbers (all verified by command output):

- Git tree: 1340 blobs, 308,126,973 bytes total.
- CSV rows: 1336 = 1340 tree blobs minus 4 root build-manifest files
  excluded from the per-file CSV (`Android.bp` 674,956 B, `gtowifi-vendor.mk`
  61,311 B, `BoardConfigVendor.mk` 50 B, `Android.mk` 80 B; together
  736,397 B). Row bytes total 307,390,576. The 1336 includes the repo's
  0-byte `.gitignore` (retained for exact tree parity).
- 1333 distinct sha256: three content-duplicate pairs under
  `proprietary/vendor/firmware/` — `aw87319l_rcv.bin`/`aw87319r_rcv.bin`
  (sha256 `4e7e482b...`), `aw87319l_spk.bin`/`aw87319r_spk.bin`
  (`df0597bb...`), `aw87319l_vspk.bin`/`aw87319r_vspk.bin`
  (`2095906c...`) — left/right speaker-channel variants with identical
  content.
- Manifest reference check: `gtowifi-vendor.mk` contains 165
  `PRODUCT_COPY_FILES` pairs; `Android.bp` declares 1148 distinct `srcs`;
  165 + 1148 + 23 unreferenced = 1336 (the unreferenced set: `.gitignore`,
  `TimeService.apk`, `tcmclient.jar`, 10 system_ext jars, 2 VINTF XMLs,
  6 `rfsa/adsp/*_skel.so`).
- Magic probe (first bytes): 884 elf32-le, 273 elf64-le, 86 raw, 79 text,
  14 zip.
- Per-bucket: `proprietary/vendor` 1310 files / 305,360,079 B;
  `proprietary/system_ext` 24 / 2,023,403; `proprietary/system` 1 / 7,094
  (plus `.gitignore` 0 B).
- Largest files: `libllvm-qcom.so` (lib64 30,043,560 B / lib 22,883,936 B),
  `libOpenCv.camera.samsung.so` (lib64 15,845,760 B / lib 8,804,128 B),
  `libllvm-glnext.so` (lib64 13,644,360 B / lib 9,819,396 B),
  `thermal-engine` 7,637,592 B, `libGLESv2_adreno.so` 3,744,864 B.

Family column in the CSV is a mechanical path-rule classification (first
match wins on tokenized lowercase path; `data` matches exact token only),
using the repo's 9-value family vocabulary — it is a rule output, not a
semantic claim:

| order | family | keywords |
|---|---|---|
| 1 | wifi | wlan, wcnss, wpa, wifi, hostapd, wiphy, wigh, softap |
| 2 | bt | bluetooth, btdun, bt, qfm, fm |
| 3 | modem | modem, qmi, ims, netmgr, rmnet, data (exact token) |
| 4 | gpu | gpu, adreno, kgsl, vulkan, egl, gles |
| 5 | boot | bootloader, xbl, sbl1, rpm |
| 6 | tz | tz, trustzone, qsee, skeymaster, keymaster, gatekeeper, secure |
| 7 | cdsp | cdsp (before adsp: `cdsp` ends with `dsp`) |
| 8 | adsp | adsp, acdb, audio, mixer, soundfx, dsp |
| 9 | other | (no match) |

Resulting counts (files / bytes): other 1224 / 282,131,738; adsp 35 /
4,995,611; modem 24 / 2,775,109; gpu 16 / 12,505,284; bt 15 / 1,355,310;
tz 13 / 396,393; wifi 7 / 3,214,703; cdsp 2 / 16,428. `boot` matched 0
files — the vendor set contains no bootloader/xbl/sbl1/rpm paths. An
example of the rule's mechanical (not semantic) behaviour:
`MTP_Bluetooth_cal.acdb` classifies as `bt` via the path token
`bluetooth`.

## Reconciling the upstream count of 44

The 44 is an upstream-asserted artifact-class count, not a device-manifest
count, and upstream publishes no per-file backing for it:

- LibrePhone `count.csv` (9339 rows; codeberg rsavoye/librephone, mirrored
  github fabiorafaelcoutada/librephone): the row
  `Samsung,Galaxy_TabA_8.0,gtowifi,44` appears 44 times verbatim.
- `sort-totals.csv`: `samsung,Galaxy_TabA_8.0,gtowwifi,5,14,25,0` —
  5 images + 14 binaries + 25 firmware + 0 hex = 44.
- Upstream's own dumps carry **zero** per-file records for this device:
  `devices.sql` has the gtowwifi row with the file-data column NULL (every
  other populated device carries per-file JSON), and `sizes.csv`,
  `sizes-22.2.csv`, `binfiles_devices.csv`, `contains-binaries.csv`,
  `devices-22.2.sql.bz2` have 0 gtowwifi rows. `builds.csv` records
  `Samsung,Galaxy_TabA_8.0,gtowifi,fails` (extract 22.2 fails).
- The actual public LineageOS blob manifest is three orders of magnitude
  larger: 1336 files in the 22.2 vendor tree (delta +1292 vs 44), 1530
  manifest pairs / 1561 blobs in the 19.1-era tree. No natural subset of
  either manifest equals 44 (closest 19.1-era subset: 33 `vendor/etc/
  firmware` + 9 `system/etc/firmware` = 42).

Delta verdict for the checklist: per-file population **succeeded** from a
public LineageOS source; the honest finding is that the recorded 44 and
the real blob set differ by +1292 and that 44 decomposes only as the
upstream database's own (unverifiable, extraction-failed) artifact
categories.

## Cross-era context (lineage-19.1 shared tree)

`TheMuppets/proprietary_vendor_samsung` branch lineage-19.1 contains a
`gtowwifi` directory (subtree
`f780c17829ba74a16994991c1b29cae2e6867fba`): its generated
`gtowifi-vendor.mk` (228,106 B, sha256
`7a8c8cedb9fbd67bc1c1a62edf111924b644c573732a52c79e9e319f177b7097`) holds
1530 `PRODUCT_COPY_FILES` pairs (1502 distinct destinations: vendor 1472,
system_ext 48, system 10), and the tree holds 1561 blobs / 360,730,485 B,
with 31 files unreferenced by the .mk (jars installed via Android.bp,
VINTF manifests, TimeService.apk, libaudioparsers, libsdm-disp-vndapis,
lib+lib64). LineageOS never officially supported 19.1 for gtowifi
(official versions: 20, 21, 22.2); the 19.1 numbers are kept as
cross-era context only.

## Partition table

From the mainline port's BoardConfig (yarons/gtowifi_lineageos, branch
lineage-23.2, comments cite the device PIT) — provenance flagged: the
official tree is inaccessible, so these are PIT-derived sizes with one
independent cross-check:

| partition | bytes |
|---|---|
| boot | 67,108,864 |
| cache | 317,718,528 |
| recovery | 67,108,864 |
| system | 4,076,863,488 |
| vendor | 796,917,760 |
| vendor_dlkm | 469,762,048 |
| flash block | 131,072 |

Cross-check that passes: the official build API reports
`boot.img = 67,108,864` bytes, equal to `BOARD_BOOTIMAGE_PARTITION_SIZE`.
fstab by-name mapping (same source): `apnhlos -> /vendor/firmware_mnt`,
`persist -> /mnt/vendor/persist`, `logdump -> /metadata` (64 MiB),
`product -> /vendor_dlkm`.

## Provenance of the official build vs the vendor repo

The official 22.2 nightly build manifest
(`mirrorbits.lineageos.org/full/gtowifi/20261118/build-manifest.xml`,
sha256 `2e8ce6db5a7f7c4f5712454fbb1476ac7e6423ecebebb49772606fe30a3c8fe5`,
1,144 projects) contains **no** vendor/blob project — `remote="private"`
is declared but used by zero projects — and the device tree's
`lineage.dependencies` lists only `android_hardware_samsung` and
`android_kernel_samsung_sdm429`. The maintainer's stated blob source is
`extract-files.py` run against the signed nightly zip (XDA thread; the
Manoel26 CI mirror does exactly that against
`lineage-22.2-20261028-nightly-gtowifi-signed.zip`). The vendor repo
censused here (last push 2025-07-08) therefore documents the public blob
set, not the shipped build's sync pipeline; both record the same
extraction provenance (`T295XXS6CWG6 release-keys`).

## Honest negatives

1. `LineageOS/android_device_samsung_gtowwifi` is 404 on every protocol
   (REST, GraphQL, HTML, raw, codeload, Gerrit, jsDelivr, git ls-remote),
   under two accounts; last public proof is the 2025-07-17 Wayback capture
   (branch lineage-22.2, 315 commits, `proprietary-files.txt` present).
   No public fork found.
2. `TheMuppets/proprietary_vendor_samsung_gtowwifi` was accessible at
   clone time and is 404 later the same day (two accounts, API + web); no
   mirrors, no Wayback snapshots. Our verified clone is the evidence copy.
3. No public full PIT dump (per-partition sizes above are PIT-derived via
   a porting BoardConfig, cross-checked only for boot).
4. samfw.com per-build AP/BL/CSC file listings return 403 (24 stock builds
   for SM-T290/XAR recorded, newest `T290UES5CWG5`, Android 11;
   wiki-required bootloader `T290XXU3CVG3` present in the list).
5. gtowifix/SM-T295: no public blob data, and the community codename for
   T295 is not consistent across sources (`gto`, `gto4lte`) — recorded as
   unresolved.
6. LibrePhone's 44 cannot be decomposed further from upstream's published
   data (NULL/absent per-file records; see reconciliation).
7. FCC filings for SM-T290 (A3LSMT290) were not retrievable in-session
   (fcc.report 403, fccid.io incomplete) — no contradicting evidence
   either.

## RULE 1 findings

All 13 files / 24 in-repo occurrences of the device were cross-checked; no
dangling references, no contradictory counts (44 agrees across
`upstream-counts.csv:16`, `device-inventory.csv:152`, catalog echoes and
generated pages; 0 matrix rows agrees with `coverage-matrix.csv`;
`count_known` is derived in `src/lib/data.ts:81`). Two soft findings are
reported for the lead rather than edited, because both files are shared
artifacts outside this session's file wall:

- `research/laptop/devices-half.csv:48` carries the codename `gtowifi` in
  its `soc` column (upstream builds.csv SOC was blank for this device);
  the verified chip is now on record above (SDM429) for whoever owns that
  file.
- `upstream-contribution/blob-database/device-inventory.csv:152` has empty
  `soc`/`soc_source`; filling them with "Qualcomm SDM429 Snapdragon 429"
  would let the generated device page drop "SoC: not recorded".

## Reproduction

```
git clone --depth 1 -b lineage-22.2 https://github.com/TheMuppets/proprietary_vendor_samsung_gtowwifi.git
git -C proprietary_vendor_samsung_gtowwifi rev-parse HEAD   # 6c3f39621fa61f44c20a10891c694fce61d2ee48
git -C proprietary_vendor_samsung_gtowwifi ls-tree -r -l HEAD | awk '$4 != "-" {n++; b+=$4} END {print n, b}'
sha256sum data/fleet/Galaxy_TabA_8.0-census.csv              # d9a68c74d09904e76bad7869ef91c73160a5fd2a9e36626b68f8cffb61009c36
awk -F, 'NR>1 {n++; s+=$6} END {print n, s}' data/fleet/Galaxy_TabA_8.0-census.csv   # 1336 307390576
curl -s https://raw.githubusercontent.com/LineageOS/lineage_wiki/master/_data/devices/gtowifi.yml
curl -s https://download.lineageos.org/api/v2/devices/gtowifi/builds
curl -s https://codeberg.org/rsavoye/librephone/raw/branch/main/data/count.csv | grep -c Galaxy_TabA_8.0   # 44
```
