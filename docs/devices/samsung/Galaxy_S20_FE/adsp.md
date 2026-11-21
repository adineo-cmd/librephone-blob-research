# samsung Galaxy_S20_FE — `adsp` family status (0 rows - vendor-tree absence, DSP firmware inside the modem image)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1096](https://github.com/adineo-cmd/open-device/issues/1096)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site e411404), the LineageOS `android_device_samsung_r8q` lineage-24.0 `proprietary-files.txt` (257 entries, package G780GXXSHEYJ1, fetched 2026-11-21), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: separate `adsp` files are structurally ABSENT from Galaxy_S20_FE's vendor tree - while the DSP firmware itself is present on-device, carried inside Samsung's modem partition image.** The census has 0 adsp rows and no modem/image directory at all; the same-SoC contrast (OnePlus_8, SM8250, 22 adsp rows at `modem/image`) proves the files exist as separate split images only in the OnePlus packaging style. The upstream inventory's SoC cell is empty - this doc supplies it (SM8250, Galaxy S20 FE 5G).

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy S20 FE 5G (SM-G781B); codename `r8q` | `device-inventory.csv` (`build_codename=r8q`) [F]; LineageOS r8q tree header `Samsung package version G780GXXSHEYJ1` (fetched 2026-11-21) [F] |
| SoC | Qualcomm **SM8250 Snapdragon 865**; Adreno 650; Hexagon DSP | public spec pages (2026-11-21) [F]. **The upstream inventory's SoC cell is empty** - supplied here [F] |
| census scope | 38 rows in 6 families (other 26, boot 5, wifi 3, gpu 2, modem 1, bt 1); 246,012,751 B | coverage-matrix.csv + device-inventory.csv [F] |

## Census evidence [F]

- 0 adsp rows; the adsp/`mdt`/`b0` substring scan over all 38 rows hits only `ipa_uc.mdt` (6,860 B, ELF64, at `vendor/firmware`, classified `other`) - the IPA (IP accelerator) firmware, a modem-class image, not adsp [F].
- The census has **no modem/image directory** - its paths are `samsung/r8q/{radio, vendor/etc(+locale,+nfc), vendor/firmware(+nfc), vendor/lib64/camera}` [F]. The modem family is a single row: `ipa_fws.mdt` 7,020 B ELF64 at `vendor/firmware` [F].
- `adsp_avs_config.acdb` exists in the r8q extract list under `vendor/etc/acdbdata/` - an audio-calibration config file, not the DSP OS [F].

## The same-SoC contrast that proves packaging, not absence [F]

OnePlus_8 and OnePlus_8_Pro (SM8250, same SoC generation) carry **22 adsp rows each** - `adsp.mdt` + `adsp.b00..b07` + manifest - at `oneplus/instantnoodle/modem/image`. The SM8250 adsp firmware exists as split images wherever the vendor ships them as files. Samsung instead integrates the DSP firmware into its modem partition image; the r8q extract list (257 entries) contains **zero** adsp/DSP image entries, confirming no vendor-tree copy exists to extract.

So the 0-row census is a **packaging-grammar difference** (Samsung: DSP inside the modem image; OnePlus: DSP as modem/image split files), not a missing-firmware condition. The berlna lesson from #922 applies: the census mirrors its extract source.

## Honest negatives

- The DSP firmware's presence inside r8q's modem partition image is **inferred from the SM8250 platform architecture + the packaging contrast, not payload-verified** - decomposing Samsung's modem.bin would prove it. [OPEN]
- Whether Samsung's modem image carries the same adsp.mdt/bXX split grammar internally is [OPEN] (the OnePlus rows show the split form; Samsung's integrated form may differ).
- r8q's `ipa_fws.mdt`/`ipa_uc.mdt` (the only modem-image-class rows) are undecoded; their relationship to the OnePlus modem/image grammar is [OPEN].

## What would upgrade this finding

1. Payload fetch (r8q stock modem image): decompose modem.bin for the embedded adsp/cdsp images - the first Samsung-SM8250 DSP segment map; compare against the OnePlus adsp grammar (#592-class fleet work).
2. Corpus pass: extend the adsp fleet tables (#592's 253-file catalog) with a "Samsung-style integrated modem image" column - the r8q case is the template for all Samsung SM8250+ devices.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Galaxy S20 FE r8q adsp firmware modem` (web + GitHub code search, adineo-cmd/* excluded) -> ROM guides only; the SM8250 adsp split grammar is the in-repo adsp-fleet work, cited.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public device trees and specs.
