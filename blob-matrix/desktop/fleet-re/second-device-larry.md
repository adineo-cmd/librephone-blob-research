# Second Device Population — OnePlus Nord CE 3 Lite 5G / Nord N30 5G (`larry`, SM6375)

WORKORDER-001 desktop session, second-device population. This is the lab's first SM6xxx-generation census. Raw artifacts stay local under `data-fetch/second-device/larry/`; census lives at `analysis/out/second-device-census.csv`. Nothing was committed to `librephone-blob-research/`.

## Device chosen and why

- **Device:** OnePlus Nord CE 3 Lite 5G / Nord N30 5G (matrix identity `Nord_CE3`, vendor `oneplus`, LineageOS codename `larry`).
- **SoC:** Qualcomm SM6375 Snapdragon 695 5G — the preferred SM6375 generation per the workorder (SM6375/SM6225/SM6115 first, then SM7250).
- **Leverage:** the coverage matrix carries all six `bm2nXX.bin` fleet md5s for `oneplus/larry/vendor/lib/rfsa/adsp` (bm2n06/08/12/13/14/15), the richest SM6375 OnePlus candidate (506 matrix rows, `extract_status_22.2=completes`, 732 MB).
- **Candidate pool (method step 1):** rows whose `md5_db` equals the VOOC pair md5s appear only on OnePlus_8 / OnePlus_8_Pro / OnePlus_8T / OnePlus_9R (all SM8250, SM8xxx — outside the requested generation). The bm2n fleet md5s appear on 35+ identities across SM4350/SM6375/SM7250/SM7325/SM8250(9RT)/SM8350/SM8475. No single matrix device carries both sets; per the workorder's generation preference, the SM6375 OnePlus bm2n carrier was selected. Fallbacks `oscaro` (Nord_CE2, SM6375, same six fleet md5s), `dre` (Nord_200, SM4350) and `instantnoodle` (OnePlus_8, SM8250, VOOC carrier) were all API-queried and available but not needed.
- **Desktop half:** all candidates sit inside rows 1-222 of the model-name-sorted device inventory (larry at sorted position 118 of 249 identities).

## LineageOS API URLs used

- Device: `https://download.lineageos.org/api/v2/devices/larry` → 200, `"name":"Nord CE 3 Lite 5G / Nord N30 5G"`, `"versions":["23.2","24.0"]`
- Builds: `https://download.lineageos.org/api/v2/devices/larry/builds` → 3 nightly builds (24.0-20261114, 24.0-20261107, 23.2-20261010)
- Zip: `https://mirrorbits.lineageos.org/full/larry/20261114/lineage-24.0-20261114-nightly-larry-signed.zip`

Also queried (all 200, versions 23.2/24.0): `.../api/v2/devices/oscaro`, `.../api/v2/devices/dre`, `.../api/v2/devices/instantnoodle`.

Note: 22.2 has been superseded; the current channel is 23.2/24.0. The newest nightly (24.0 line) was taken, per "or similar".

## Build downloaded and verified

| field | value |
|---|---|
| zip | `lineage-24.0-20261114-nightly-larry-signed.zip` |
| size | 1,601,993,721 bytes (1.49 GiB — inside the one-zip <=1.5 GB cap) |
| sha256 (API) | `c73a04e8e97ad47a0fd6e4349694a1254edc09adf03544364ecbabde730f2ddf` |
| sha256 (local sha256sum) | `c73a04e8e97ad47a0fd6e4349694a1254edc09adf03544364ecbabde730f2ddf` |
| match | EXACT — sha256-verified Y |

Download: `curl -L -sS --retry 8 --retry-delay 5 --retry-all-errors -o <zip>`; single attempt, no retries needed.

## Payload manifest (12 partitions)

boot 167,772,160 / dtbo 25,165,824 / odm 620,982,272 / product 2,542,948,352 / system 1,179,967,488 / system_ext 598,708,224 / vbmeta 8,192 / vbmeta_system 4,096 / vbmeta_vendor 4,096 / vendor 383,954,944 / vendor_boot 167,772,160 / vendor_dlkm 10,178,560.

Ops mix: REPLACE_XZ dominant, plus REPLACE_BZ and a few REPLACE (all supported by `payload_dump.py`).

**No `radio`, `bluetooth`, `modem`, `dsp` or `firmware` partition exists in this payload** — LineageOS 24.0 for `larry` flashes OS partitions only; modem/dsp/tz images stay on the stock firmware partition. This is a structural negative for the census (see below).

## Extraction steps: what worked, what failed

| step | result |
|---|---|
| `unzip -o <zip> payload.bin` | OK |
| `payload_manifest.py payload.bin` | OK — 12 partitions listed |
| `payload_dump.py payload.bin vendor vendor.img` | OK — 184 ops, 383,954,944 bytes |
| `payload_dump.py payload.bin odm odm.img` | OK — 297 ops, 620,982,272 bytes |
| FAT16 probe (first 16 bytes, EB 3C 90) | No FAT partitions exist in this payload; vendor/odm first 16 bytes are all zero (ext4 would have magic at 0x438) |
| `debugfs` / `extract_ext4.py` | **FAILED** — both images are **EROFS**, not ext4 (`debugfs` reports "contains a erofs file system"; magic `E2 E1 F5 E0` at offset 1024) |
| `fat_extract.py` | Not applicable — no FAT16 partition present |
| EROFS extraction | OK — `fsck.erofs 1.7.1` (erofs-utils 1.7.1-1build2 .deb unpacked locally with `dpkg -x`, run without sudo): `fsck.erofs --extract=tree-vendor vendor.img`, `--extract=tree-odm odm.img` |
| Symlink handling | 296 symlinks in the trees; dangling ones (`wlanmdsp.otaupdate` → `/data/vendor/firmware/wlanmdsp.mbn`, `firmware/wlan/qca_cld/wlan_mac.bin` → `/mnt/vendor/persist/wlan_mac.bin`) are excluded from the census |

Method note for future sessions: any LineageOS 24.0-era payload will be EROFS; the ext4/debugfs path in the workorder must be replaced by `fsck.erofs --extract`.

## Fleet-identity verification

Matrix md5s are authoritative. The workorder brief's md5s (`76835ccc095f116ce20029238b4ca4c1`, `1ec85cbd095f116ce20029238b4ca4c1`) are corrupted: they share only the 8-hex prefix with the matrix values, and their identical 24-hex suffix `095f116ce20029238b4ca4c1` is exactly the tail of `crnv20.bin`'s md5 (`bb6ca169095f116ce20029238b4ca4c1`, a Nord_CE3 matrix row). Matrix values were used, as the workorder instructs.

### oplus VOOC fast-charge pair — NOT PRESENT (0/2)

| blob | matrix md5 | matrix size | found in build |
|---|---|---|---|
| `oplus_vooc_fw.bin` | `1ec85cbd137458de72d76822a05a7595` | 6,464 | no |
| `oplus_vooc_fw_rk826.bin` | `76835ccc9dd4ad08922e9d7616bdf4ac` | 12,432 | no |

VOOC pair md5 match: **N** for this device. The matrix confirms why: every `oplus_vooc_fw*.bin` row belongs to OnePlus 7/7 Pro/7T/7T Pro/8/8 Pro/8T/9R (MSM8998/SM8150/SM8250). No SM6xxx/SM7xxx matrix device carries the VOOC pair, and the `larry` LineageOS odm has no `firmware/fastchg/` directory (only `firmware/tp/` touch firmware). The VOOC leverage entry stays SM8250-specific; populating `instantnoodle`/`kebab` remains the only way to prove it.

### bm2n ADSP-region fleet — 6/6 EXACT MATCHES

All in `vendor/lib/rfsa/adsp` (census path prefix `lib/rfsa/adsp`), md5 + size both identical to the matrix fleet values shared by `dre`/`oscaro`/`larry` and the wider SM6375 fleet:

| blob | md5 (matrix = local) | bytes | matrix devices sharing this md5 |
|---|---|---|---|
| `bm2n06.bin` | `9010bb1a7c08222a058aaef7edd938c6` | 864,824 | fleet md5 (dre, oscaro, larry, pdx225, miami, ...) |
| `bm2n08.bin` | `1275a2d212e5bccce734d3055ff10156` | 3,091,896 | fleet md5 (same set) |
| `bm2n12.bin` | `5c86c8fcc7451f51e11d38276253aac8` | 2,623,528 | fleet md5; ≡ `bm2n37.bin` on other devices |
| `bm2n13.bin` | `bf635d9084b54633526f9ad8a84d299b` | 1,106,944 | fleet md5 |
| `bm2n14.bin` | `805176afaae27821520b79647fa5d498` | 103,168 | fleet md5; ≡ `bm2n55.bin` |
| `bm2n15.bin` | `2ce8163cda60f33cbf2b50f03a3d0ea1` | 1,082,856 | fleet md5; ≡ `bm2n31.bin` |

Fleet identity for the bm2n ADSP-region blobs is **proven byte-for-byte** for the SM6375 generation — first direct confirmation outside SM4350/SM8350 dumps.

### Bonus QCA BT NVM matches — 3/3 EXACT

| blob | md5 (matrix = local) | bytes |
|---|---|---|
| `odm/etc/bt/apnv11_eu.bin` | `6f9cf45a440a8787b19a9b5152a1823a` | 4,903 |
| `odm/etc/bt/apnv11_in.bin` | `1f58bde391c2e2742d1919cbcddf11c4` | 4,903 |
| `odm/etc/bt/apnv11_na.bin` | `f5a8f5543b2d06d09d18ffee2f36be01` | 4,903 |

`crbtfw*/apbtfw*/crnv*` (matrix paths `oneplus/larry/bluetooth/image`) are absent — they live in the stock `bluetooth`/`radio` partition, which this payload does not carry.

## Census (`analysis/out/second-device-census.csv`)

- **299 files, 74,530,271 bytes** (71.05 MiB), 196 unique sha256, header `device,vendor,soc,family,file,bytes,sha256,md5,public_status`, `public_status=populated-local-session`.
- Scope: blob-bearing trees only — `vendor/firmware` (incl. `wlan/qca_cld` real files), `vendor/lib/rfsa/adsp`, `vendor/gpu`, `vendor/bt_firmware` (empty), `vendor/dsp` (empty), `odm/etc/bt`, `odm/etc/wifi`, `odm/vendor/firmware` (face-unlock), `odm/firmware/tp` (touch). Camera tuning configs and OS `.so` trees outside `rfsa/adsp` were excluded, matching the enchilada methodology.

| family | files | bytes |
|---|---|---|
| adsp | 21 (6 bm2n fleet + 15 fastrpc skel libs) | 21,947,448 |
| bt | 3 (apnv11_eu/in/na) | 14,709 |
| gpu | 15 (a615/a619/a630/a660 gmu-sqe-zap, kbc) | 226,008 |
| modem | 7 (ipa_fws) | 62,848 |
| wifi | 4 (bdwlan.bin, bdwlan_in.bin, bdwlan_us.bin, regdb.bin) | 98,332 |
| other | 249 (touch FW 131, face-unlock 27, evass/vpu20/wlanmdsp etc.) | 52,180,926 |
| cdsp | 0 — stock-partition only | 0 |
| tz | 0 — stock-partition only | 0 |

- 182/299 census files match a matrix row exactly on (filename, md5); 38 more match an md5 under a different filename (content aliasing).
- 33 duplicate-content groups (136 files); largest: `FW_NF_ILI7807S_HUAXING.img` 392,133 B ×4 across touch-panel dirs.

## Honest negatives

1. **VOOC pair absent (0/2).** See verification above; leverage entry remains SM8250-only. The workorder's premise that one SM6xxx/SM7xxx device carries the VOOC pair is not supported by the matrix or by this build.
2. **No modem-family partitions in the payload.** `adsp.b0*/cdsp.b*/tz*/mpss*` images from matrix paths `oneplus/larry/modem/image` cannot be censused from an official LineageOS nightly; census shows cdsp=0, tz=0. Those rows stay desktop-dump-only.
3. **EROFS, not ext4.** The prescribed `extract_ext4.py`/debugfs step cannot run on LineageOS 24.0 images; `fsck.erofs` used instead.
4. **No FAT16 partitions** — `fat_extract.py` had nothing to run on (unlike OnePlus 6's bt.img/modem.img).
5. **Brief md5 corruption** documented in the verification section; matrix md5s used throughout.
6. **22.2 superseded** by 23.2/24.0; newest nightly used. `oscaro`/`dre`/`instantnoodle` remain unpopulated fallbacks.
