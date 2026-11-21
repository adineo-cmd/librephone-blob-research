# samsung Galaxy_Tab_S7_Wifi — `other` family status (14 rows - zero device-unique bytes)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#1156](https://github.com/adineo-cmd/open-device/issues/1156)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site d7a5ec8), the sibling docs #1102/#1150, public 3GPP PLMN knowledge. No payloads fetched; every number is command output or a recorded fetch.

**Verdict: the `other` family is PRESENT and entirely fleet-shared - zero of the 14 rows carry a corpus-unique md5.** Every file is byte-identical with at least one sibling device: the Cirrus amp pair and `ipa_uc.mdt` with gts7l (#1150's byte-identity), the 9 PLMN tables with up to **15 samsung devices**, and the ToF calibration pair with Galaxy_S20_FE + gts7l. This is the cleanest common-infrastructure slice documented so far - nothing here is device-specific.

## Device identity

| fact | value | source |
|---|---|---|
| model | Samsung Galaxy Tab S7 Wifi (SM-T970); codename `gts7lwifi` | `device-inventory.csv` [F] |
| SoC | Qualcomm SM8250-AC Snapdragon 865+ | public spec pages (2026-11-21) [F]; #1150 [F] |
| census scope | 26 rows in 6 families; other = 14 rows | coverage-matrix.csv [F] |

## The 14 rows, grouped [F]

| group | rows | bytes | md5 sharing span |
|---|---|---:|---|
| Cirrus amp | 2 | 5,204 | cs35l40-spk-dsp1-spk-prot.bin 4,220 + -calib 984 - shared with gts7l only (#1150 identity) [F] |
| IPA firmware | 1 | 6,860 | ipa_uc.mdt ELF64 - shared with Galaxy_S20_FE + gts7l [F] |
| PLMN tables | 9 | 42,709 | plmn_se13.bin 24,562 (7 devices); plmn_delta.bin 11,412 (**15 devices**); plmn_delta_attaio.bin 449 (**15 devices**); plmn_delta_eng.bin 959 (3); plmn_delta_hktw.bin 1,233 (5); plmn_delta_usagsm.bin 446 (**15**); plmn_delta_zh-rCN.bin 1,216 (4); plmn_delta_zh-rHK.bin 1,216 (4); plmn_delta_zh-rTW.bin 1,216 (4) [F] |
| ToF calibration | 2 | 1,520 | t_tof 760 + w_tof 760 - shared with Galaxy_S20_FE + gts7l [F] |

Group sums [F, python-verified]: Cirrus 5,204 + IPA 6,860 + PLMN 42,709 + ToF 1,520 = 56,293 B total - the smallest other-family byte total in the documented shard.

## The fleet-sharing finding [F]

- `plmn_delta_attaio.bin` and `plmn_delta.bin` are **byte-identical across 15 samsung devices** (the whole samsung slice: A21S, A71, F62, Note10 family, S10 family, S20_FE, Tab_A7_LTE, Tab_S6_LTE, Tab_S7 pair) - the samsung-wide carrier/region PLMN tables are one shared build, not per-device files [F].
- The regional deltas have narrower spans (eng/hktw/usagsm/zh-* at 3-5 devices) - region-packaged variants [F].
- Combined with #1150's 23/26 LTE/Wifi identity and #1060's family-shared unsparse: the samsung census separates cleanly into **device-unique layers** (boot/recovery/vbmeta, per-build BL files) and **fleet-shared layers** (PLMN tables, calibration blobs, amplifier configs, placeholders) [F].

## ISA proof and interface facts

- `ipa_uc.mdt` is `isa_identified=ELF64` [F]; the rest UNKNOWN [F].
- Interface [I, labeled]: PLMN tables feed the modem's network-selection logic; Cirrus amps load via ASoC; ToF calibration via the camera stack. None payload-verified.
- Evidence class: all rows P3, metadata-only [F].

## Honest negatives

- The PLMN binary format (record layout inside plmn_delta/plmn_se13) is [OPEN] - semantics are public 3GPP knowledge, the Samsung container is not.
- The ToF calibration blob structure (760 B each, front/rear sensors) is [OPEN].

## What would upgrade this finding

1. Payload fetch: decode plmn_se13.bin (24,562 B, 15-device fleet) - the PLMN record layout would apply to every samsung device in the corpus at once.
2. Corpus pass: extend the fleet-sharing map (#1060/#1150/#1156) to all samsung devices - a lead-level table of per-build vs fleet-shared layers.

## RULE 0 record (2026-11-21)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `samsung plmn_delta.bin PLMN table format`, `sec ToF calibration samsung` (web + GitHub code search, adineo-cmd/* excluded) -> 3GPP knowledge + guides; no binary-format decodes exist. Nobody documents the Tab_S7_Wifi other-family census or the fleet-sharing spans.

Not legal advice; no proprietary payload accessed or committed - all facts are metadata plus public 3GPP knowledge.
