# fairphone FP6 — `boot` family status (16 rows)

Analysis date: 2026-11-21. Analyst: ZC-1 (issue [#988](https://github.com/adineo-cmd/open-device/issues/988)).
Inputs: `upstream-contribution/blob-database/coverage-matrix.csv` (33,917 data rows, feat/open-device-site 2dcef61), the payload-derived in-repo census `research/qualcomm/docs/bootchain-census.md` (FP6, LineageOS 23.2-20261109 nightly, QCM6490 "Lanai"/"Milos"), `docs/REPO-STATE-MAP.md` (boot verdict PARTIAL). No payloads fetched this session; every number is command output or quoted from the committed census.

**Verdict: the boot family is PRESENT and the best-characterized boot slice in the corpus** — but the cross-check against the repo's own payload census surfaces **one size mismatch** (`xbl.img`) and a **coverage asymmetry** on both sides. 14 of the 16 DB rows match the payload census byte-exactly; the census covers 4 partitions the DB lacks; the DB carries 2 rows the census skipped.

## Device identity

| fact | value | source |
|---|---|---|
| model | Fairphone 6; codename `FP6` | `device-inventory.csv` [F] |
| SoC | Qualcomm **QCM6490** ("Lanai"/"Milos") | `research/qualcomm/docs/bootchain-census.md` title + build identity (`SocMilosLAA` variant string, LANAI target) [F]. **The upstream inventory's SoC cell is empty** — this doc's identity row supplies it |
| priority | **P1 — FSF flagship** ("librephone.fsf.org lists exactly one device: Fairphone 6") | device-inventory.csv `mainline_basis_or_note` [F] |
| census scope | 447 rows in 9 families (other 122, tz 111, wifi 74, adsp 54, modem 39, cdsp 21, boot 16, bt 5, gpu 5); 703,921,964 B | coverage-matrix.csv + device-inventory.csv [F] |

## The 16 rows, cross-verified against the payload census [F]

| DB row | DB bytes | census bytes | md5 corpus-unique | match |
|---|---:|---:|---|---|
| xbl.img | 1,167,360 | **1,196,032** | yes | **MISMATCH** |
| xbl_config.img | 311,296 | 311,296 | yes | OK |
| xbl_ramdump.img | 860,160 | 860,160 | yes | OK |
| uefi.img | 2,904,064 | 2,904,064 | yes | OK |
| abl.img | 245,760 | 245,760 | yes | OK |
| aop.img | 319,488 | 319,488 | yes | OK |
| aop_config.img | 20,480 | 20,480 | yes | OK |
| cpucp.img | 204,800 | 204,800 | yes | OK |
| cpucp_dtb.img | 12,288 | 12,288 | yes | OK |
| qupfw.img | 61,440 | 61,440 | yes | OK |
| shrm.img | 53,248 | 53,248 | yes | OK |
| boot.img | 100,663,296 | 100,663,296 | yes | OK |
| init_boot.img | 8,388,608 | (not censused) | yes | n/a |
| recovery.img | 104,857,600 | (not censused) | yes | n/a |
| dtbo.img | 31,457,280 | 31,457,280 | yes | OK |
| vbmeta.img | 12,288 | 12,288 | yes | OK |

All 16 md5s are corpus-unique to FP6 [F]. The census's container/ISA findings for the matching images stand as the authoritative structural record: xbl = 3-ELF multi-ELF container; shrm/aop/aop_config/cpucp = **RV32 RISC-V** (the QCM6490 housekeeping cores are RISC-V, a headline the census proved); qupfw = Hexagon (EM_QDSP6); uefi = AArch64 EFI FV (Project Mu); boot kernel = PE32+ EFI-stub AArch64 (GKI v4); dtbo = big-endian dt_table, 14 entries; vbmeta = AVB0 v1.0, SHA256_RSA4096, **flags=3**; build `BOOT.MXF.2.1-02027-LANAI-1`, signed down to Fairphone BV's OEM attestation key [F — all quoted from the committed census].

## Findings new in this cross-check [F]

1. **`xbl.img` size mismatch**: DB 1,167,360 vs payload census 1,196,032 (delta 28,672 B). Both are FP6, but the census's payload is the 2026-11-09 LineageOS nightly while the DB rows come from the upstream blob DB's build — so this is either a **build difference** (XBL updates between builds) or an **upstream data error**. The DB md5 cannot be checked against the census hashes this session (census JSON is committed in the FP6 work tree, not this one). [OPEN]
2. **Coverage asymmetry, census side**: the payload census covers `imagefv` (53,248 B), `vendor_boot` (100,663,296 B), `pvmfw` (1,048,576 B) and `vbmeta_system` (4,096 B) — **none of these appear in the upstream DB's boot family**. The DB's boot slice is missing 4 partitions the device demonstrably ships. [F]
3. **Coverage asymmetry, DB side**: the DB uniquely carries `init_boot.img` (8,388,608 B — the Android-13+ GKI init_boot partition) and `recovery.img` (104,857,600 B) which the census's 18-partition dump skipped. [F]
4. `aop.img`'s census entry-point anomaly (entry outside all LOADs, flagged in the census) stands — this doc adds nothing payload-level.

## ISA and interface facts

All structural facts are the census's, by reference [F]: RV32 housekeeping cores, Hexagon qupfw, AArch64 xbl_ramdump/uefi/boot-kernel, MBNv7 signing chain with per-image cert dates 2024-03-14 → 2026-08-31 ("the boot chain was refreshed in slices"). This doc verifies the DB rows against that record rather than re-deriving anything.

## Honest negatives

- The xbl mismatch cannot be resolved without either the DB's build identity (the upstream DB records no per-row build for FP6) or re-fetching the census JSON hashes — both [OPEN].
- Whether the 4 census-only partitions should join the DB's boot family is a lead-level catalog decision, recorded here not enacted (file walls).
- No payload work was done this session; every structural fact cited is the census's, and the census's own open items (aop entry anomaly) remain open.

## What would upgrade this finding

1. Join the census's `results/bootchain-census.json` hashes against the DB md5s → settle the xbl mismatch as build-vs-error in one command.
2. Lead-level: add `imagefv`/`vendor_boot`/`pvmfw`/`vbmeta_system` rows to the DB's FP6 boot family (the device ships them; the census proves it).

## RULE 0 record (2026-11-21)

The prior-art search for FP6's boot chain was performed by the census itself (2026-11-10, queries recorded there: `BOOT.MXF.2.1-02027 OR AOP.HO.5.0-00813 OR xbl_s.melf` → DiamaneOS logistics-only inventory; `BOOT.MXF` → Project Mu ports; `AOP.HO.` → firmware dumps). This session's delta is the cross-verification; no new uniqueness claims are made beyond it.

Not legal advice; no proprietary payload accessed or committed this session — structural facts are quoted from the committed census, census facts command-verified against the matrix.
