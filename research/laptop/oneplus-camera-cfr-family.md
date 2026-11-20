# OnePlus/Xiaomi `CFR_*` camera parameter family

Laptop-half summary of `implementations/camera-cfr-fleet/`.

## Identity

Camera tuning data under `vendor/etc/camera/` and
`odm/etc/camera/cfr_bin/`. Not firmware, not WiFi. The upstream database has
112 `CFR_*` rows across five sizes.

## Four grammars, one prefix

| class | bytes | discriminator |
|---|---:|---|
| `short-1079` | 1,079 | 3 records stride 337, 20-byte signature at offset 20 |
| `mid-2126` | 2,126 | 3 records stride 670, same signature at offset 20 |
| `tagged-3645` | 3,645 | ASCII `L12UW` at offset 8, six tagged records |
| `text-8128` | 8,128 | ASCII `CFR400 TUNING PARAMETER`, filesize u32 at offset 68 |

A fifth size, 5,776,288 B (`alCFR_Segmodel.bin`), is a separate model
artefact.

The `short` and `mid` classes share a byte-identical 20-byte signature block
at offset 20 and an `XX 00 01 02` record tag. The `tagged` class shifts the
same marker to offset 52. The `text` class has its own plain-text framing.

## Filename correction

`CFR_imx766.bin` and `CFR_imx766_uw.bin` are **byte-identical except for one
byte at offset 4** (`0x7a` → `0x70`). The `_uw` filename does not denote a
separate calibration table. By contrast the 8,128-byte `dodge` main/tele/uw
files differ in 222/235 bytes. Fleet counts built from filenames alone
over-count the `imx766` pair.

## Evidence

Tree listings and raw payloads fetched 2026-11-20 from
`proprietary_vendor_xiaomi_diting`, `_cupid`, `_laurel_sprout`,
`proprietary_vendor_oneplus_dodge` and `proprietary_vendor_oneplus`. All
fetched md5s checked against the DB. RULE 0 found only build manifests and a
public ADSP skeleton filename (`libalCFR_skel.so`), no writeup.

## Status

Component passing: 11 tests, deterministic synthetic fixtures, zero collisions
against the 7,042-md5 DB. Full analysis:
`implementations/camera-cfr-fleet/cfr-fleet-analysis.md`.
