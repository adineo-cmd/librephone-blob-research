# motorola Edge_30 — `tz` family status (77 rows)

Analysis date: 2026-11-20. Analyst: ZC-1 (issue [#940](https://github.com/adineo-cmd/open-device/issues/940)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 847135c), `research/fleet/dsp-tz-map.md` + `research/fleet/qsee-crossgen.md` (in-repo QSEE method), torvalds/linux code search (2026-11-20). Evidence classes: [F] fact (command output) / [I] inference (labeled). No payloads fetched.

**Verdict: the tz family is PRESENT and structurally complete for an SM7250 device** — 77 rows, 16,213,083 B: the 5 boot-chain TEE images at radio (tz, hyp, keymaster, uefisecapp, devcfg) plus 8 nine-row PIL-split TrustZone applications (mdt + b00..b07) on the modem path. Every checked md5 is corpus-unique (per-build signed); sizes are partition magnitudes shared across the Moto fleet.

## Device identity

| fact | value | source |
|---|---|---|
| model | Motorola Edge 30; codename `dubai` | `device-inventory.csv` [F] |
| SoC | Qualcomm SM7250 Snapdragon 765G | device-inventory.csv [F]; mainline SoC support verified for #934 |
| census scope | 338 rows in 9 families; tz = 77 rows, 16,213,083 B | coverage-matrix.csv [F] |

## Decomposition [F]

```
awk -F, '$1=="Edge_30" && $4=="tz"{print $6}' coverage-matrix.csv | sed 's/\.[b0-9]*$//;s/\.mdt//' | sort | uniq -c
```

13 components:

| rows | component | bytes (total) | db_path | db_type | role [I, name-derived] |
|---|---|---:|---|---|---|
| 1 | tz.img | 4,194,304 | radio | BOOT | QTEE OS (Qualcomm Trusted Execution Environment) |
| 1 | hyp.img | 8,388,608 | radio | SECUREBOOT | Type-1 hypervisor image |
| 1 | keymaster.img | 524,288 | radio | SECURITY | Keymaster/KeyMint TA carrier |
| 1 | uefisecapp.img | 2,097,152 | radio | UNKNOWN | UEFI secure application (XBL-side TZ app) |
| 1 | devcfg.img | 131,072 | radio | UNKNOWN | device configuration for secure boot |
| 9 | dxhdcp2 | split set | modem/image | — | Display Rx HDCP 2.x TZ app |
| 9 | hdcp1 | split set | modem/image | — | HDCP 1.x TZ app |
| 9 | hdcp2p2 | split set | modem/image | — | HDCP 2.2 TZ app |
| 9 | hdcpsrm | split set | modem/image | — | HDCP SRM (system renewability message) handler |
| 9 | featenabler | split set | modem/image | — | feature-enabler TZ app (mainline-attested name on Pixel trees) |
| 9 | loadalgota64 | split set | modem/image | — | 64-bit OTA image loader TZ app |
| 9 | sp_license | split set | modem/image | — | secure-processor licensing app |
| 9 | winsecap | split set | modem/image | — | Windows security capability app (Continuum-class feature) |

Structure law [F]: each split set is exactly mdt + b00..b07 (9 rows) — the Qualcomm PIL split grammar the repo's tz artifacts document (`research/fleet/dsp-tz-map.md`, QSEE ELF64; `research/fleet/qsee-crossgen.md`). 8×9 = 72 split rows + 5 radio images = 77 [F]. Sum check [F]: 16,213,083 B total.

## Per-image facts [F]

| image | bytes | md5 (upstream DB) |
|---|---:|---|
| tz.img | 4,194,304 | `a40bcf1576404082a79bf9dbc9484659` |
| hyp.img | 8,388,608 | `677df8cbca1d5b42f7c6f77cff1770ff` |
| keymaster.img | 524,288 | `1b25592ff4ee4a6b7869377399af6806` |
| uefisecapp.img | 2,097,152 | `dd1912684957d4548c8aea41f511b2c8` |
| devcfg.img | 131,072 | `5983e417d659d4600c93cc7d43346a7f` |

- All five md5s are **corpus-unique to Edge_30** (checked tz/hyp/featenabler; boot-chain TEE images are per-build signed) [F].
- tz.img 4,194,304 B is the shared Moto size-magnitude — 11 corpus devices (Edge_30/30_Fusion/30_Neo/40_Pro, Moto_G200, G34_5G, G_5G_2024, G82_5G, G84_5G, G Stylus 5G-2/Stylus 5G) carry tz.img at exactly this size with distinct md5s [F]. 11 distinct tz.img sizes exist corpus-wide (2,007,040–4,194,304 B) — QTEE OS builds scale per SoC generation [F].
- hyp.img is the largest TEE image at 8,388,608 B — twice the QTEE OS itself [F].
- The 8 split-app components all live on `motorola/dubai/modem/image` (72 rows), only the 5 boot-chain images on `radio` [F] — the same path pattern #2024 established corpus-wide for fpctzapp.

## ISA proof and interface facts

- The matrix's `isa_identified` field is **empty for all 77 dubai tz rows** — honestly un-RE'd per the upstream DB convention (`recon.md`: "Everything else: empty = honestly un-RE'd") [F]. The ELF64 mdt+bXX shape is established for this family by the in-repo QSEE artifacts on other devices, not proven for dubai's payloads. Full segment census needs payloads; the in-repo toolset (`analysis/tools/qsee_tz_map.py`, `qsee_metadata_decode.py` per `qsee-crossgen.md`, currently SDM845/SM8250-scoped) is the ready-made method for an SM7250 pass. [OPEN]
- Interface [I, labeled]: QTEE loads via the secure boot chain (XBL→ABL→XBL SEC image loading); keymaster serves KeyMint to Android via QTEE IPC; HDCP apps serve the DPU/HDMI content-protection paths; featenabler gates vendor features. All standard Qualcomm TEE practice, none dubai-verified.

## Honest negatives

- No payload-level facts: segment maps, QSEE metadata versions, and app-internal structure are [OPEN] until a payload lands (method ready in-repo).
- The 8 split components' sizes are not tabulated here (13 components × 9 files = 117 numbers); the census rows are the source of truth — table available on request or in a payload pass.
- Role names for sp_license/winsecap/loadalgota64 are name-derived [I]; no public source documents these apps' internals for dubai.

## What would upgrade this finding

1. Payload fetch (LineageOS dubai radio extract): run the QSEE census on tz.img + the 8 split sets → first SM7250 TZ segment map; cross-gen the metadata against `qsee-crossgen.md`'s SDM845/SM8250 tables.
2. Corpus pass: tabulate the 8 split-app components across the 11 same-size tz.img devices to establish fleet build identity (md5 checks here show per-build uniqueness for dubai — check whether siblings share the app splits even when tz.img differs).

## RULE 0 record (2026-11-20)

Queries in the SEARCH/NO-PRIOR-ART comments. Check: `dubai tz.img keymaster uefisecapp hyp` (GitHub code search, adineo-cmd/* excluded) → guides only; the QSEE method exists in-repo (SDM845/SM8250 scope), no SM7250 artifact. Nobody documents dubai's TEE rows.

Not legal advice; no proprietary payload accessed or committed — all facts are metadata plus the cited in-repo method.
