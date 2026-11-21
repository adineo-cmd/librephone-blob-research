# xiaomi Mi_10T_5G — `cdsp` family status (0 rows - census gap; the extract covers almost nothing)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1162](https://github.com/adineo-cmd/open-device/issues/1162)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 213d0b3), public spec pages (2026-11-21). No payloads fetched; every number is command output or a recorded fetch.

**Verdict: 0 `cdsp` rows is a CENSUS GAP - and this device's census is the thinnest in the documented shard: only 9 rows total.** The device is an SM7250 (Snapdragon 765G, codename `gauguin`) whose CDSP exists per Qualcomm's SoC spec; the census covers just 5 Android boot images (boot.img and recovery.img at **128 MiB each - the corpus's largest**) plus 4 Xiaomi MiSound audio-resource files. The entire vendor/modem firmware set - adsp OS, cdsp images, modem splits, everything that makes a modern flagship work - is outside this extract.

## Device identity

| fact | value | source |
|---|---|---|
| model | Xiaomi Mi 10T 5G; codename `gauguin` | `device-inventory.csv` [F] |
| SoC | Qualcomm **SM7250 Snapdragon 765G**; Hexagon CDSP present per Qualcomm's SoC spec (mainline carries no sm7250.dtsi - 7 driver/binding hits only, verified for #934's class) | public spec pages (2026-11-21) [F] |
| census scope | **9 rows in 2 families** (adsp 4, boot 5); 302,116,860 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 9 rows [F]

```
awk -F, '$1=="Mi_10T_5G"{print $4"|"$6"|"$7"|"$13"|"$14}' coverage-matrix.csv | sort
```

| family | file | bytes | md5 (upstream DB) | db_path | note |
|---|---|---:|---|---|---|
| adsp | misound_karaokemix_res.bin | 8,552 | `90ba47442879a558a474f603780e359b` | xiaomi/gauguin/vendor/lib/rfsa/adsp | Xiaomi MiSound karaoke-mix resource [I] |
| adsp | misound_karaoke_res.bin | 11,252 | `11eaf8e7fdcb51d4b17610f5eb12813b` | same | MiSound karaoke resource [I] |
| adsp | misound_res_headphone.bin | 83,184 | `8167617e406c7d7c27fe51062e17a465` | same | MiSound headphone profile [I] |
| adsp | misound_res_spk.bin | 11,148 | `44972f6a0394d87230cf52ba053e8a2f` | same | MiSound speaker profile [I] |
| boot | boot.img | **134,217,728 (128 MiB)** | `9313d35618fc7cad5fab75f51b70280c` | xiaomi/gauguin/radio | AOSP boot image - the corpus's largest boot.img [F] |
| boot | recovery.img | **134,217,728 (128 MiB)** | `be5a59f1987ab16d2003c06a58fdfb07` | xiaomi/gauguin/radio | AOSP recovery image [F] |
| boot | dtbo.img | 33,554,432 (32 MiB) | `9c91abdbacfbbe152ce7c41d3b3fcd40` | xiaomi/gauguin/radio | device-tree overlay image [F] |
| boot | unsparse_super_empty.img | 4,644 | `61a9cfbd4284b170f3112a45c040205a` | xiaomi/gauguin/radio | dynamic-partition placeholder [F] |
| boot | vbmeta.img | 8,192 | `dac717523db84090b0074549c70a8340` | xiaomi/gauguin/radio | AVB metadata [F] |

All 9 md5s corpus-unique to Mi_10T_5G [F].

## The two findings [F]

1. **The misound rows are not the ADSP OS.** They carry the `blob_family=adsp` label only because they live in `vendor/lib/rfsa/adsp/` (the DSP-side fastrpc library path). They are Xiaomi MiSound audio-effect resources - karaoke/headphone/speaker profiles loaded by the audio effects stack. The actual SM7250 ADSP OS (adsp.mdt/bXX) is absent from the census, as is everything else from the vendor tree.
2. **The census is the thinnest for any flagship-class device in the corpus**: 9 rows / 302,116,860 B, of which 302,112,216 B is just boot+recovery+dtbo. A modern SM7250 device's firmware set (adsp/cdsp/modem/wifi/BL images) would run to hundreds of files - none are here. The extract source covered only the radio images and 4 audio resources.

## Honest negatives

- Where the SM7250 cdsp/adsp firmware lives on Xiaomi devices (modem partition vs vendor/lib/rfsa) is [OPEN] - the census cannot see it, and no public extract list for gauguin was fetched this session.
- The misound resource format (MiSound audio-profile containers) is [OPEN].
- Whether boot.img at 128 MiB indicates a GKI 2.0 image or just a padded partition is [OPEN].

## What would upgrade this finding

1. Payload fetch (Mi 10T 5G stock firmware or LineageOS gauguin package): the vendor/modem walk would populate the adsp/cdsp/modem families in one pass - the census would grow from 9 rows to hundreds.
2. Corpus pass: the misound resource files appear across the Xiaomi fleet (one decode covers many devices).

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `Mi 10T 5G gauguin cdsp firmware` / `gauguin misound adsp resources` (web + GitHub code search, adineo-cmd/* excluded) -> ROM guides + MiSound app pages; no structural firmware analysis exists. Nobody documents the Mi_10T_5G census shape or the cdsp gap.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public specs.
