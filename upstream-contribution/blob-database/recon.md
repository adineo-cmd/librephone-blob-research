# LibrePhone blob-database reconnaissance + coverage-matrix scaffold (2026-11-16)

Session goal: locate the owner-described "~100 GB database of firmware/blobs
for listed devices" WITHOUT downloading it, enumerate it completely from
metadata APIs, and build the master coverage-matrix scaffold
(`device-inventory.csv` + `coverage-matrix.csv`, both written alongside this
file). Companion to the F-69 audit
([../librephone-wants.md](../librephone-wants.md)); all network fetches this
session are logged below with status and byte size. Scratch space:
`/tmp/lpdb/` (raw fetched artifacts + parser scripts).

## Headline finding — where the database lives (and does not)

**The published "database" is metadata only. The ~100 GB payload corpus is
not published anywhere we can find, and its existence is now pinned down to
a specific local layout on the maintainer's machine.**

1. What IS published (all under `codeberg.org/rsavoye/librephone`, branch
   `main`, dir `data/`, all fetched byte-exact this session): the dumps of a
   **PostgreSQL database** (`devices`, owner `rob`, dumped by pg_dump 18.0):
   `devices.sql.bz2` (708,066 B compressed → 6,548,830 B SQL) plus seven
   CSV projections. The dump's `blobs` jsonb column carries per-device blob
   rows whose `path` field is the maintainer's local absolute path, e.g.
   `/work/Lineage-images/blobs/fairphone/FP6/modem/image` — i.e. the corpus
   lives at **`/work/Lineage-images/`** (LineageOS install packages
   downloaded and blob-extracted), exactly matching upstream's own
   `docs/totals.md`: *"To produce these numbers, I downloaded all 210
   Lineage install packages and extracted the files from those."*
2. What is NOT published: no download/database/torrent/magnet/meta4 link on
   any librephone.fsf.org page; the git repo is 7.9 MB and contains zero
   payload archives (recursive tree, 153 entries, `truncated=false`, no
   `.zip/.tar/.xz/.zst/.img/.torrent/.magnet` blobs at all); archive.org has
   no LibrePhone corpus item under any probed name (11 probes, section
   below); no collection `librephone` exists.
3. Size arithmetic for the owner's "~100 GB" claim: the current dump
   enumerates **69.80 GB of blob files across 123 extracted devices**, with
   **113 more devices listed but not blob-populated** (extraction failed or
   pending — `blobs` jsonb is NULL). 210-250 LineageOS zips at ~1-1.3 GB
   each are ~210-325 GB of downloads; the extracted blob tree plus retained
   images comfortably spans "~100 GB". The claim is consistent with the
   evidence; the payload is simply local.

## Route history (RULE 0 — every probe, 2026-11-16, retries as noted)

| # | Endpoint / probe | Result |
|---|---|---|
| 1 | `https://librephone.fsf.org/` | 200, 29,379 B — nav-only link surface |
| 2 | `https://librephone.fsf.org/hardware` | 200, 17,589 B — links: `/hardware/fairphone6` only |
| 3 | `https://librephone.fsf.org/hardware/fairphone6` | 200, 47,689 B |
| 4 | `https://librephone.fsf.org/faq` | 200, 39,697 B |
| 5 | `https://librephone.fsf.org/freedom` | 200, 48,904 B |
| 6 | `https://librephone.fsf.org/site/` | 200, 33,667 B (after 301) |
| 7 | `https://librephone.fsf.org/site/tools/` | 200, 37,442 B |
| 8 | `https://librephone.fsf.org/home`, `/javascript` | 200/301 — home = same body as `/` |
| 9 | tag-stripped text grep of all 8 pages for `download/database/torrent/.zip/corpus/100 GB/mirror` | **zero hits** — the site has no download surface at all |
| 10 | `api/v1/repos/rsavoye/librephone` | 200, 2,765 B — repo `size` **7,910 KB**, 119 stars, 28 open issues |
| 11 | `api/v1/repos/rsavoye/librephone/contents/` | 200, 24,015 B — root: `data/ docs/ kmod/ librephone/ m4/ tests/` + autotools |
| 12 | `api/v1/repos/rsavoye/librephone/contents/data` | 200, 14,198 B — 14 artifacts (table below) |
| 13 | `api/v1/repos/rsavoye/librephone/branches` | 200, 2,346 B — `main` @ `12dd433d5eda47a73d8bf800248ba72e394fad2d` |
| 14 | `api/v1/repos/rsavoye/librephone/git/trees/{sha}?recursive=true` | 200, 35,760 B — **153 entries, 142 blobs, 6,746,882 B, `truncated=false`**; largest artifact = `data/sizes.csv` (1.6 MB); regex scan for `torrent\|magnet\|metalink\|.zip\|.xz\|.zst\|.tar\|.img` → **0 hits** |
| 15 | raw fetch × 11 `data/` artifacts (sizes below) | all 200; 3 transfers dropped mid-stream (curl exit 56/92 — this box's flaky network), recovered on retry `--retry 3 --retry-delay 5`, byte-exact vs the contents-API sizes |
| 16 | raw `docs/csvdata.md` (996 B), `docs/comparing.md` (8,933 B), `docs/totals.md` (43,180 B) | 200 — csvdata.md documents the dump set; totals.md: *"I downloaded all 210 Lineage install packages"* |
| 17 | archive.org `advancedsearch.php q=librephone` (fl=identifier,title,item_size,mediatype,creator) | 200, 982 B — **numFound 4**: `hpr4499` (HPR interview with Librephone lead Rob Savoye, 832.5 MB audio), a Fireship OGG, an LWN video, FSF Bulletin 46 — **no corpus** |
| 18 | archive.org `q=creator:rsavoye` / `creator:Rob_Savoye` / `title:(librephone)` / `collection:librephone` / `librephone_blobs` / `librephone-database` / `lineageos_blobs` | 2 mapillary photo dumps / 0 / hpr4499 / 0 / 0 / 0 / 7 unrelated LineageOS misc items — **no corpus item anywhere** |
| 19 | `api/v1/repos/rsavoye/abe` | 200 — "Advanced Build Environment" cross-compiler tool; not the corpus |
| 20 | `api/v1/repos/rsavoye/librephone-web` + branches + recursive tree | 200 — 32 files, 6.9 MB: pure site source (bootstrap/jquery/aos assets, 9 PHP pages); no download/database page |
| 21 | `librephone.org` itself | NOT re-probed this session: F-69 audit (2026-11-15) recorded a 50-redirect 302 loop; `/kernel-xref/html/` + `/modules-xref/html/` Doxygen trees were the only resolvers then. No download route was found via those pages in the audit. |

Honest negatives: no host timeout this session; the three mid-transfer
drops are logged with their recovery. The FSF hub and the web repo were
completely swept for links — every href captured; none leads to a payload.

## What the published database actually is

`data/` directory, `codeberg.org/rsavoye/librephone@main` (sizes = contents
API, verified by re-download):

| Artifact | Bytes | Content |
|---|---|---|
| `devices.sql.bz2` | 708,066 | pg_dump 18.0 of DB `devices` (owner `rob`). 5 tables: **devices (236 rows)** — version/vendor/model/build/**blobs jsonb**/available/builds/extracts/soc/released; gsmarena, images, linux, specs — **all 0 rows (empty tables shipped in the dump)**. Enums: `bintypes` (67 values incl. WIFI_BLUETOOTH, CELL_WIFI_GPS_BLUETOOTH, FASTCHG, UEFIBOOT...), `archtypes` (ARM/AARCH64/RISCV/XTENSA/MIPS/QUALCOMM/CORTEXM...), `celltypes`, `cputypes`, `gpumodels`, `devstatus`. |
| `devices-22.2.sql.bz2` | 230,113 | same schema, older Lineage-22.2-era DB: **220 device rows** |
| `devices.csv` | 518,612 | **3,880 rows = per-BLOB table**: `file,count,devices` — which devices use each distinct blob filename (quoting style: a repr'd Python list, inner single quotes) |
| `sizes.csv` | 1,608,802 | **15,071 rows**: `vendor,model,build,path,file,size,md5sum,type,released` — 63 devices, 30.11 GB, 8,004 distinct md5. **Stale**: zero FP6/rosemary rows (the FP5 rows are present, 706 of them) |
| `count.csv` | 277,985 | **204 distinct devices** (rows duplicated per-something — e.g. larry ×203 — every duplicate carries the same total) |
| `builds.csv` | 12,494 | **246 devices** + `Extract 22.2`/`Build 22.2` status (`completes`/`fails`) + `SOC` string + `Released` — the widest device list; SOC filled for ~124, blank for ~122 |
| `contains-binaries.csv` | 359,773 | files-with-binary-content → device lists |
| `binfiles_devices.csv` | 88,983 | `file,count,devices` subset (binary files only) |
| `track.csv` | 19,625 | per-IMAGE → comma list of devices containing it (the blob-sharing cluster map, image granularity) |
| `sort-totals.csv` | 7,392 | per-device `images,binaries,firmware,hex` counts |
| `totals.csv` | 25 | **empty (header only)** |
| `files.csv` | 0 | **empty file** |
| `sizes-22.2.csv.bz2` / `devices-22.2.csv.bz2` | 110,707 / 15,423 | 22.2-era projections |

`blobs` jsonb row shape: `{"file", "path": "/work/Lineage-images/blobs/<vendor>/<build>/...", "size", "type" (bintype), "md5sum", "version": 23.0}`.

Device-count reconciliation across the five sources (this is itself a
fragmentation finding — the same "database" has five different device
universe definitions):

| Source | Distinct devices |
|---|---|
| `builds.csv` (widest) | 246 |
| `devices.csv` blob-list device tokens | 248 tokens — **all 248 matched** a `builds.csv`/SQL identity (0 orphans) |
| `devices.sql.bz2` devices table | 236 (123 with blob jsonb, 113 NULL) |
| `count.csv` | 204 |
| `sizes.csv` (file-level) | 63 |
| `devices-22.2.sql.bz2` | 220 (older era) |

## Total enumeration (no sampling — these are complete counts)

- **Blob rows (device,file) enumerated: 33,917** across **123 devices**,
  totaling **69,797,539,502 bytes = 69.80 GB (65.00 GiB)**.
- **Distinct blobs by md5: 15,091** — i.e. behind the 33,917 device-rows
  there are only 15,091 actual file images.
- **Shared blobs: 4,763** distinct md5s appear on >1 device;
  **23,080 of 33,917 rows (68.0%) are instances of a shared blob**.
- Sharing histogram (distinct blobs by device count): 10,328 on 1 device ·
  3,472 on 2-4 · 1,104 on 5-9 · 144 on 10-19 · **43 on 20+ devices**.
- 113 further devices are listed with NULL blob data; 123 more exist only
  in `builds.csv`/`count.csv` (no blob enumeration at all).

### Size breakdown by family (mapped from filename + upstream bintype)

| family | rows | bytes | note |
|---|---|---|---|
| modem | 2,539 | 25.94 GB | incl. `modem.img`/`md1img.img` partition dumps + MDT segments |
| boot | 1,038 | 23.86 GB | **incl. `boot.img`/`vendor_boot` (67 MB each × many devices) — these are the FREE kernel images, not blobs**; also xbl/abl/uefi chains |
| other | 14,987 | 14.15 GB | long tail: camera 1,493+ rows, touch, audio, fastchg, media/venus, 8,664 rows typed UNKNOWN upstream |
| adsp | 3,281 | 3.98 GB | incl. `bm2nXX.bin` ADSP-region fleet (upstream types them MODEM; they live in `vendor/lib/rfsa/adsp`) |
| wifi | 5,642 | 0.71 GB | WCN/qca firmware + MTK combo (WIFI_BLUETOOTH 3,243 rows) |
| tz | 4,264 | 0.67 GB | TrustZone TAs/keymasters/DRM |
| cdsp | 940 | 0.28 GB | compute DSP |
| bt | 445 | 0.12 GB | QCA BT ROM patches (`.tlv`) + NVRAM |
| gpu | 781 | 0.09 GB | Adreno GMU/SQE/zap + kbc math libs |

### By vendor (bytes with blob data; devices with data / devices listed)

oneplus 18.31 GB · xiaomi 16.96 · motorola 14.58 · google 6.71 · samsung
5.50 · sony 1.99 · fairphone 1.98 · realme 1.52 · nothing 1.47 · fxtec
0.45 · lenovo 0.33 — rows: oneplus 10,772 · xiaomi 9,830 · motorola 7,041 ·
google 1,089 · samsung 914 · fairphone 1,439 · nothing 1,129 · sony 416 ·
realme 980 · fxtec 287 · lenovo 20. Devices with blob data per vendor:
motorola 23, oneplus 22, xiaomi 21, google 19, samsung 17, sony 12,
fairphone 3 (FP3/FP5/FP6), nothing 2, realme 2, lenovo 1, fxtec 1. Devices
listed but not extracted (NULL blobs) concentrate on the same vendors plus
nvidia/nubia/lge/asus/nokia/razer/radxa/essential/shift/zte. Top-3 vendors
carry 49.85 GB = 71.4% of all enumerated bytes.

### SoC fragmentation (from `builds.csv` + SQL `soc`)

- 39 distinct SoC strings → **35 distinct chips: 29 Qualcomm Snapdragon
  generations** (MSM8996/8998 → SDM630-845 → SM4250-8550 incl. -AC/−AE
  variants, QCM6490), **4 Google Tensor** (GS101/GS201/G3/G4), **2
  Amlogic** (TV boxes). SOC is blank for ~122 of 246 devices — the known
  set under-represents MediaTek (rosemary = MT6785 Helio G95 per the lab
  census, yet its `builds.csv` SOC cell is blank).
- SoC generation spread: every Snapdragon generation 2016-2024 is present —
  release years in the DB span 2016-2024 (peak 2018/2021, 19 devices each).

## Top-20 highest-leverage blobs (RE once, frees many devices)

Ranked by distinct device count sharing the identical file (md5), filtered
to real firmware (≥1 KB, no `.jsn/.json/.xml/.txt` manifests — the raw
top-by-count is dominated by <1 KB DSP launch manifests `adspr.jsn` ×30 and
zero-byte MDT segment stubs `venus.b17` ×34, themselves a fragmentation
finding). md5s and device lists are in `coverage-matrix.csv`.

| # | devices | bytes | family | file |
|---|---|---|---|---|
| 1 | 29 | 56,180 | bt | `crbtfw20.tlv` (QCA BT ROM patch 2.0) |
| 2 | 29 | 56,052 | bt | `apbtfw10.tlv` (BT patch 1.0) |
| 3 | 29 | 29,368 | bt | `crbtfw11.tlv` (BT patch 1.1) |
| 4 | 29 | 3,936 | bt | `crnv20.bin` (BT NVRAM 2.0) |
| 5 | 29 | 2,798 | bt | `crnv11.bin` (BT NVRAM 1.1) |
| 6 | 29 | 1,243 | bt | `apnv10.bin` (BT NVRAM 1.0) |
| 7 | 26 | 2,623,528 | adsp | `bm2n12.bin` (ADSP-region, `vendor/lib/rfsa/adsp`) |
| 8 | 26 | 1,082,856 | adsp | `bm2n15.bin` |
| 9 | 26 | 103,168 | adsp | `bm2n14.bin` |
| 10 | 26 | 32,768 | gpu | `a619_gmu.bin` (Adreno 619 GMU microcode) |
| 11 | 25 | 3,091,896 | adsp | `bm2n08.bin` |
| 12 | 25 | 1,106,944 | adsp | `bm2n13.bin` |
| 13 | 25 | 864,824 | adsp | `bm2n06.bin` |
| 14 | 25 | 796,357 | other | `unified_ksqs.bin` |
| 15 | 25 | 5,704 | gpu | `sequence_manifest.bin` (kbc/GPU calibration) |
| 16 | 21 | 40,496 | gpu | `a660_sqe.fw` (Adreno 660 SQE) |
| 17 | 19 | 55,256 | gpu | `a660_gmu.bin` |
| 18 | 19 | 32,456 | gpu | `a630_sqe.fw` |
| 19 | 19 | 2,126 | other | `CFR_OPlus_EF017_UW_snapshot.bin` |
| 20 | 17 | 839,856 | wifi | `aoa_cldb_falcon.bin` (wlan calibration DB) |

The whole QCA BT patch fleet (rows 1-6) is the single highest-leverage
family: one RE pass covers the BT bring-up of up to 29 devices. The
`bm2nXX.bin` ADSP fleet (0.8-3.1 MB each, 25-26 devices) is the largest
byte-weighted target. Image-granularity sharing (`track.csv`) adds the boot
chain: `abl.img` ×75, `devcfg.img` ×76, `dsp.img` ×71 devices — structurally
similar signed containers per the lab's F-15 census, so tooling RE (not
per-file RE) is the multiplier there.

## The coverage-matrix scaffold (what each cell holds)

`coverage-matrix.csv` — 33,917 rows, one per blob per device, columns:
`device, vendor, soc, blob_family, blob_subfamily, filename, size_bytes,
md5_db, sha256_if_listed, isa_identified, interface_documented, priority,
db_path, db_type`. Family mapping is filename-first with upstream bintype
fallback (rules embedded in the generator; misc subfamily = 8,664 rows the
upstream DB itself types UNKNOWN). Filled cells, honestly:

- `isa_identified`: **101 rows** (0.30%). FP6: 95 rows carry the lab's
  committed ISA facts (`qualcomm-fp6/results/census.md` table matched on
  filename+size — sizes differ across nightlies, so matches were
  filename+size first, then unique-filename; source recorded per rule in
  the generator) + the boot-chain doc-level facts (xbl/shrm/aop/aop_config/
  cpucp RV32, qupfw Hexagon header-claim, uefi AArch64 FV, abl ARM32 —
  `results/bootchain-census.json` + `docs/bootchain-census.md`, which
  supersedes that JSON's raw container labels e.g. xbl "M32"). rosemary/
  MT6785: 6 rows (`md1img.img` = mtk_hdr container w/ F-31 MIPS32 LE +
  MIPS16e modem region + F-36 MD32-class md1dsp; `scp.img` Cortex-M4 +
  FreeRTOS; `sspm.img` CM4 per tinysys family claim; `audio_dsp.img` HiFi3
  Xtensa byte-confirm-pending; `lk.img`/`gz.img` container labels).
  **Everything else: empty = honestly un-RE'd.**
- `sha256_if_listed`: 102 rows (16-hex truncated values from the lab
  censuses; the upstream DB lists **md5 only**, never sha256 — full
  64-hex sha256 lives in the lab census docs but the FP6 nightly mismatch
  limits safe joins).
- `interface_documented`: **116 rows, all FP6** (`y` with doc pointer for
  modem → `interface-cellular.md`; wifi → `interface-copyengine.md`,
  `interface-pcie-bridge.md`, `interface-ftm-diag.md`; NFC subfamily →
  `interface-nfc.md`). All non-FP6 rows `n` — consistent with the F-69
  audit row B-9 (no per-family interface docs upstream).
- `priority`: P1 = FP6 (447 rows) — the FSF flagship per F-69 (C-3:
  hardware page lists exactly one device). P2 = 1,608 rows across 21
  devices with public mainline/ports progress (FP3/FP4/FP5, OnePlus 6/6T/
  7 Pro, POCO F1, Mi 8, Shift 6MQ, Pixel 3/3a/3a XL/4/4 XL/4a/6/6a/7/7 Pro,
  Sony Xperia XA2 — basis string recorded per device in
  `device-inventory.csv`; **agent-knowledge list, dated 2026-11, flagged
  for verification against the postmarketOS wiki**). P3 = 31,862 rows.

`device-inventory.csv` — **249 devices**, one row per distinct identity
(join key = build codename; vendor/model normalized), with per-source
membership columns (`in_devices_sql`, `blob_rows_devices_sql`,
`total_bytes_devices_sql`, `in_builds_csv`, `extract_status_22.2`,
`in_count_csv`, `in_sizes_csv`, `in_devices_csv_bloblists`, `soc`,
`soc_source`, `priority`, `mainline_basis_or_note`, `source_artifacts`).
This resolves the "444 devices" question from the owner/task framing: the
real per-BLOB table (`devices.csv`) has 3,880 rows; **FP6 is mentioned in
418 of them** (the F-69 audit's "444 FP6 rows" number, from 2026-11-15,
differs — either the file changed that day or the audit's parse counted
multi-device rows differently; recheck on next fetch). The DB itself
carries FP6 as 447 blob rows / 703,921,964 B (Lineage 23.0) vs the lab
census's 665 files / 240,352,566 B (23.2-20261109) — different nightly and
different scope; both recorded.

### Upstream data-quality findings (new this session)

1. `files.csv` is a 0-byte file; `totals.csv` header-only; the SQL dump's
   `gsmarena`, `images`, `linux`, `specs` tables ship empty (schema with no
   rows) — the DB's relational enrichment is aspirational, only `devices`
   is populated.
2. `count.csv` duplicates every device row dozens-hundreds of times (larry
   ×203) with identical totals — a generator join artifact.
3. `builds.csv` SOC blank for ~122 devices; one row (Phone_2/aura) even has
   a blank vendor; a stray `\ufffd` byte precedes one SOC value.
4. `a660_sqe.fw` (Adreno 660 SQE microcode, GPU) is typed `AUDIO` in
   upstream's bintypes — a bintypes mislabel; same for the `bm2nXX.bin`
   ADSP-region fleet typed `MODEM` while living in `vendor/lib/rfsa/adsp`.
5. `devices.csv`'s device lists use repr'd Python lists with inner single
   quotes inside the CSV double quotes — nonstandard quoting that breaks
   naive CSV parsers (and likely explains audit-count drift).
6. `sizes.csv` (63 devices) lags `devices.sql.bz2` (123 populated devices):
   the SQL dump is the only artifact with FP6 + rosemary rows.

## What remains (the honest mountain)

- **33,816 of 33,917 matrix rows (99.70%) have no ISA identified**; even
  for FP6, 352 of 447 rows (mostly camera/unknown tail) carry no committed
  ISA fact. ISA is *unknown*, not *knowable-now* — the lab's FP6/MT6785
  method (ELF e_machine + decode-rate sanity + container records) applies
  to any extracted device, but nothing else has been run.
- **116 of 33,917 rows (0.34%) have a documented driver↔blob interface.**
- **113 devices** in the DB have zero blob data; **123 more** exist only as
  names in `builds.csv`/`count.csv`. The matrix's per-device coverage is
  52% of the SQL device universe (123/236), 50% of `count.csv` (123/204),
  47% of `devices.csv` tokens (123/248).
- The payload corpus itself is not publicly fetchable; everything above was
  derived from metadata (git trees API + dump + CSVs), zero payload bytes
  downloaded. The one-actionable cross-check that remains owner-gated:
  a full-corpus torrent/archive.org mirror would collapse the corpus-access
  blocker for every downstream RE effort.

## Radio / regulatory stub — hurdles to replacing radio firmware

**Flag: dedicated documentation session required; nothing below is a
conclusion — these are the enumerated dimensions to fill.**
(FILLED 2026-11-16: the full document now lives at
[../radio-regulatory-hurdles.md](../radio-regulatory-hurdles.md) — primary
texts fetched verbatim, precedents surveyed, RULE-0 query log included.
The stub below is retained as the original dimension list.)

1. **Type-approval per radio (modem/WiFi/BT/GNSS/NFC are certified as a
   unit per device):** FCC (US; Part 15 + Part 22/24/27 for cellular,
   SAR rules), CE / EU Radio Equipment Directive 2014/53/EU, UKCA, India
   TEC/MTCTE, Japan TELEC/MIC, China SRRC, Brazil ANATEL. A free radio
   firmware replacement re-opens the approval; modular-approval vs
   per-device economics needs documenting.
2. **Legality of RE-ing radio firmware:** US DMCA §1201 rulemaking
   exemptions (computer-program interoperability; wireless-device
   unlocking exemptions 2015/2018/2021) — scope for *firmware*
   interoperability RE specifically; EU Software Directive 2009/24/EC
   decompilation-for-interop; India/UK fair dealing. Carrier/SDO contract
   terms (GCF/PTCRB certification conditions) as a separate non-statutory
   hurdle.
3. **Export controls on crypto:** modem firmware embeds crypto (A5/3, RSA,
   ECDH for SIM/network auth) → EAR Cat.5 Pt.2 / Wassenaar / EU dual-use
   2021/1080 — where RE tooling and published specs sit; the lab's
   no-keys/no-bypass charter (F-14 policy note) intersects this.
4. **The FSF's own position:** campaign texts (fsf.org campaign + news
   pages, librephone.fsf.org/{freedom,faq}) demand RE-and-replace of the
   proprietary modules; historical FSF line on secondary-processor
   firmware (RYF certification criteria) vs radio firmware as the
   acknowledged hard case — collect exact citations.
5. **Precedents to survey:** Openmoko/Calypso (the only fully-free modem
   attempt), Replicant's modem status page, Qualcomm's mainline Linux
   firmware split (ath11k/wcn6750 board data vs amss), MediaTek MOLY
   stack, Google Tensor modem (Samsung Exynos-derived, shut in radio/).
6. **Safety/EMC liability + spectrum-coexistence testing** (SAR re-test,
   coex between WiFi/BT/modem antennas) as the practical bring-up gate
   beyond legality.

## Files written (this session)

- `upstream-contribution/blob-database/recon.md` — this file.
- `upstream-contribution/blob-database/device-inventory.csv` — 249 devices.
- `upstream-contribution/blob-database/coverage-matrix.csv` — 33,917 rows.
- Scratch (re-generatable): `/tmp/lpdb/` — raw fetched artifacts
  (`devices.sql` decompressed, all CSVs/JSONs) + `build_scaffold.py` (the
  generator; family/ISA/interface rules embedded and commented).

No git commit, no push (per instructions).

## Workorder impact (lead note, 2026-11-16)

The finding above CORRECTS workorder W1 (desktop): no payload corpus is
published, so there is nothing to bulk-download. Desktop payloads come
**per-device from the public LineageOS install packages** (~1-1.3 GB each,
fetched only when a device in its half reaches a payload-needing phase).
The published metadata needs no download — it is already distilled into
`coverage-matrix.csv` (33,917 rows) and `device-inventory.csv` (249
devices), which the two-machine 222/222 program consumes directly.
