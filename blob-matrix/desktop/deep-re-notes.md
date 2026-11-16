# Desktop Phase 1 deep-RE notes (metadata-first) — 2026-11-16

WORKORDER-001-desktop v3 (F-71 amended), Phase 1, desktop half. Everything
below is derivable from committed sources; scratch scripts and downloaded
artifacts stay off-repo.

## 1. The device-universe reconciliation (first-class finding)

The work order's premise ("444 listed devices", `devices.csv` split
222/222) does not survive contact with the file it names:

- `devices.csv` (codeberg `data/devices.csv`, fetched 2026-11-16,
  518,612 B, 3,880 rows, repr'd-list quoting) yields **exactly 123
  distinct device tokens**, bidirectional set-equality with the 123
  blob-populated devices of `coverage-matrix.csv` (verified by parse:
  tokens-matrix = ∅ both ways).
- recon.md's "248 tokens / 47% coverage (123/248)" line is therefore a
  parse artifact of the recon session — the true token count is 123 and
  coverage is 100%. Flagged for the lead (shared file, not edited
  here per file-wall rules).
- The "444" number traces to the F-69 audit's FP6-rows count (444,
  corrected to 418 in recon.md's own recheck note) — it was never a
  device count.
- The full listed universe = `device-inventory.csv` **249 identities**
  (236 SQL devices incl. the 113 listed-not-populated + 13
  builds.csv-only).

**Split executed (literal + gapless):** codepoint sort by device name
(`model`, fallback `build_codename`; identical rule derivable by both
machines from the committed inventory) over the 249 identities →
**desktop = rows 1–222, laptop remainder = rows 223–249 (27 devices,
flagged to the lead)**. This satisfies Phase 1(a)'s own arithmetic
(123 extracted + 113 listed-not-populated both in range) and tiles the
universe with zero overlap/gap under both work orders' literal row
numbers. Workload imbalance (222 vs 27) is a lead-rebalance decision;
12 of the 123 populated devices (all Sony Xperia + tail X/Z names) fall
in the laptop-flagged zone.

## 2. Half mapping (Phase 1a answer)

Desktop rows 1–222 contain:

| status | devices |
|---|---|
| populated (matrix rows present) | 110 of the 123 |
| listed-not-populated (SQL NULL blobs) | 100 |
| builds-csv-only | 12 |

Identity-join finding: the inventory carries two `Phone_2` identities —
`aura` (blank vendor, SQL NULL blobs → listed-not-populated) and `Pong`
(nothing, 654 blob rows → populated). A display-name join misclassifies
aura and double-counts Pong's rows; the correct join key is the matrix
`db_path` codename, which this deliverable uses (341+654 row arithmetic
reconciles exactly: 34,135 name-joined rows − 654 double-counted = 33,481
codename-joined rows).

Desktop half matrix extent: **33,481 blob rows / 67.48 GB** (matrix total
33,917 / 69.80 GB). The deliverable CSV holds 33,649 rows (33,481
metadata + 111 summary rows + 57 OnePlus_6 census rows).

Family breakdown of the half (matrix rows): modem 2,533 rows /
25.94 GB · boot 1,000 / 22.05 GB · other 14,870 / 14.15 GB · adsp 3,173 /
3.49 GB · wifi 5,568 / 0.71 GB · tz 4,256 / 0.67 GB · cdsp 940 /
0.28 GB · bt 445 / 0.12 GB · gpu 696 / 0.09 GB.

Upstream duplicate-row finding (lead, shared files — not edited): the
committed coverage matrix itself contains **586 true duplicate
(device, filename, md5) triples** (341 inside the half) — same blob
listed twice per device — plus 264 same-filename/different-md5 rows in
the half that are legitimate versioned entries. recon.md's "33,917 blob
rows (device,file)" counts the duplicates. This deliverable mirrors the
matrix faithfully and quantifies the duplication rather than silently
deduping it.

## 3. Leverage-first ordering (Phase 1b answer, corrected)

Recomputing the recon.md ranking from the committed matrix (≥1 KB,
non-manifest, grouped by (filename, md5)) produces a correction to the
work order's input: **the true fleet-wide #1 is the oplus VOOC fast-charge
firmware pair, not the QCA BT fleet.**

| entry | fleet-wide devices | in half |
|---|---|---|
| `oplus_vooc_fw_rk826.bin` (md5 `76835ccc…`) + `oplus_vooc_fw.bin` (md5 `1ec85cbd…`) — OnePlus/realme VOOC charge firmware pair | **36 + 36** | 36 + 36 |
| `crbtfw20.tlv` / `apbtfw10.tlv` / `crbtfw11.tlv` + `crnv20.bin` / `crnv11.bin` / `apnv10.bin` (QCA BT patch fleet, #3-#8) | 29 | 29 |
| `bm2n06/08/12/13/14/15.bin` ADSP fleet | 25 | 22 |
| `sequence_manifest.bin` / `unified_ksqs.bin` | 25 | 22 |
| `a619_gmu.bin` | 24 | 21 |
| `a660_sqe.fw` | 21 | 20 |
| `a630_sqe.fw` | 19 | 16 |
| `aoa_cldb_falcon.bin` / `aoa_cldb_swl14.bin` | 17 | 16 |

**All 20 of recon.md's top-20 entries still sit inside the desktop half**
(the 27 flagged laptop devices carry no top-20 member), so the
leverage-first headline is: (1) the oplus VOOC pair — one RE pass covers
the fast-charge firmware of 36 devices, all in the half; (2) the QCA BT
`.tlv`/NVRAM fleet — 29 devices; (3) the `bm2nXX` ADSP fleet — the
byte-weighted third target. recon.md's top-20 table (shared file) should
be re-ranked by the lead accordingly.

Phase-2/3 headline: **one QCA BT `.tlv`/NVRAM RE pass covers BT bring-up
of 29 devices in the half**; the `bm2nXX` ADSP fleet is the
byte-weighted second target. md5s for every fleet entry are in the
half's matrix rows (e.g. `crnv20.bin` = `bb6ca169…4c1`).

## 4. Phase 1(c): first not-populated device populated — OnePlus 6 (enchilada)

Candidate chosen: P2-priority (public mainline/ports basis), official
LineageOS 22.2, Adreno 630 + QCA BT families.

- Fetch: `lineage-22.2-20261111-nightly-enchilada-signed.zip`,
  1,074,415,436 B, sha256 `dfb50b750c32b9b534cf43b5523f5a461297dd82cbeca6fa02389a17c7ef7b6e`
  (matches the LineageOS API value byte-exact; one 0-byte transfer
  failure recovered by following mirrorbits redirects — logged as an
  honest negative in the session notes).
- Unpacked with the lab's own tools (`payload_dump.py` — 23 partitions;
  `extract_ext4.py` + debugfs): vendor (1,073,741,824 B), bluetooth
  (765,952), tz (2,056,192), dsp (33,554,432), modem (119,820,288).
- Census: **57 unique files, 165,975,523 B**, sha256 + container magic
  per file, merged into `devices-001-222.csv` with
  `public_status=populated-local-session`. Family summary: adsp 24
  files/39.5 MB (Hexagon ELF `.so` fleet) · modem 119.8 MB (partition)
  · camera 3.3 MB (CAMERA_ICP.elf ELF) · gpu 7 files (a630_gmu.bin
  32,768 B + a630_sqe.fw 32,136 B — the exact size classes of top-20
  #10/#18 — + zap MDT set) · bt 765,952 B (bt.img partition) · tz
  2.06 MB · radio 11 qcril.db/SQL files (config, not firmware) ·
  wifi **structurally absent from vendor** (2 zero-byte stubs — the
  WCN3990 firmware rides inside the modem partition; census-negative
  finding).
- A/B lesson (method finding): vendor blob dirs (`bt_firmware`, `dsp`,
  `radio`) are empty mount points on A/B devices — the blob surface
  lives in the OTA's named partitions. Upstream's per-device extraction
  counts both surfaces; ours records where each actually lives.
- No payload committed. Only names, sizes, sha256, magic strings.

## 5. RULE 0 prior-art record (2026-11-16, exact queries)

Recorded in [implementations/README.md](../../implementations/README.md)
(searched before each built artifact) and summarized: no RE-status
coverage matrix exists (closest: arXiv:2410.11075 staleness study); no
QCA `.tlv` format RE beyond mainline `btqca.c`; no `bm2n` analysis; no
open LPEC decoder; no firmware-side clean-room WMI dispatcher reference.

## 6. Honest negatives / open items

- 100 listed-not-populated + 12 builds-csv-only devices in the half
  remain metadata-only; OnePlus 6 is the proof-of-population. Per-device
  cost: ~1.07 GB + ~6 tool invocations — 100 more devices ≈ ~107 GB
  fetch + storage budget decision needed (lead).
- sha256↔md5 join across the matrix needs payload access per device
  family (upstream publishes md5 only).
- P2 devices' "mainline basis" strings in the inventory are
  agent-knowledge flagged for verification against the postmarketOS
  wiki — not verified this session.
- `bt.img`/`dsp.img`/`modem.img` container parsing, MDT segment maps:
  open (method exists, budget pending).
- cmnlib/cmnlib64/keymaster/boot-chain partitions are one payload_dump
  call each from being censused (hashing not run this session).

## 7. Deliverables this phase

- `blob-matrix/desktop/devices-001-222.csv` — 33,649 rows (110 populated
  upstream-metadata devices + 100 listed-not-populated + 12
  builds-csv-only summaries + 57 OnePlus_6 census rows with sha256);
  sha256 `aebb473a972dbf47aff45ce9951026e6e1d19d45655b2b0cb6d7c646ad4276ac`,
  byte-reproducible from the committed matrix + inventory +
  `enchilada-census.csv` via `tools/phase1_build.py`
- `blob-matrix/desktop/deep-re-notes.md` — this file
- `blob-matrix/desktop/fragmentation-half.md` — Phase 4 analysis
- `docs/devices/oneplus6/` — 7 family docs (Phase 2)
- `implementations/` — 5 components + open-item marker (Phase 3)
- `workorders/inbox/STATUS-DESKTOP.md` — session status
