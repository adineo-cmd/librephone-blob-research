# STATUS-DESKTOP — WORKORDER-001 session 2026-11-16

**Status: all four phases executed; session complete, open items listed.**
No halt. No payload committed anywhere (facts-only discipline held).

## Phase 1 — deep RE (metadata-first): DONE

- Device universe reconciled (first-class finding): work order's "444
  devices" is stale — codeberg `devices.csv` yields exactly 123 distinct
  device tokens, set-equal to the matrix's 123 populated devices;
  recon.md's "248 tokens" is a parse artifact; the real listed universe is
  `device-inventory.csv`'s 249 identities. Split executed literally and
  gaplessly: desktop = rows 1–222, laptop-flagged remainder = rows
  223–249 (27 devices, all X*/Z* names, 12 of them populated Sony units).
- Codename-join correction: matrix `db_path` codename is the right join
  key — the display-name join double-counts Phone_2 (`Pong`) rows and
  misclassifies the second `Phone_2` (`aura`, blank vendor, NULL blobs).
  Arithmetic reconciles exactly (34,135 − 654 = 33,481).
- Half: **110 populated / 100 listed-not-populated / 12 builds-csv-only;
  33,481 blob rows / 67.48 GB**.
- Leverage correction (Rule 1 candidate): recomputed top shared blobs —
  **oplus VOOC pair (`oplus_vooc_fw_rk826.bin` + `oplus_vooc_fw.bin`) =
  36 devices each, outranking recon.md's #1–#6 QCA BT fleet (29)**. All
  20 recon top-20 entries still sit in the desktop half.
- OnePlus 6 (enchilada) populated from the official LineageOS 22.2
  nightly (sha256-verified 1,074,415,436 B): 23 OTA partitions dumped
  with the lab's tools; 57 unique files / 165,975,523 B censused with
  sha256 + container magic, merged into the deliverable CSV
  (`populated-local-session`). Census-negative: the wifi family is
  structurally absent from vendor (2 zero-byte stubs; WCN3990 firmware
  rides inside the modem partition).
- Deliverables: `blob-matrix/desktop/devices-001-222.csv` (33,649 rows),
  `deep-re-notes.md`, tools under `blob-matrix/desktop/tools/`.

## Phase 2 — blob families documented: DONE (for the data produced)

`docs/devices/oneplus6/` — 7 family docs, evidence-classed: gpu (a630
GMU/SQE/zap + top-20 size-class link), adsp (Hexagon ELF `.so` fleet +
`bm2n` generation comparison), bt (bt.img partition vs the `.tlv` fleet
generation), modem (119.8 MB partition, method pointers), wifi
(census-negative), radio (qcril.db config, honest not-firmware), camera/
tz/misc stubs.

## Phase 3 — clean-room implementation: DONE

`implementations/` — five components + one documented gap, all
self-tested (gcc 13.3, `-Wall -Wextra`, clean-room statement headers):

- `wmi/dispatch-registry` — the decoded two-level table-driven WMI
  dispatch architecture as a C99 reference (33 checks pass; all handler
  addresses from the lab's committed F-29 map via the committed
  generator; GPIO/SUSPEND runtime-dispatch honestly modeled, no invented
  addresses)
- `wmi/tlv` — TLV framing per public ath11k facts (36 checks)
- `ce/service-model` — 24-byte `ce_pipe_config` codec + ring arithmetic +
  reference 12-pipe table (29 checks)
- `htc/frame-layer` — HTC frame/service-connect codecs (23 checks);
  ready/setup-complete message codecs deliberately absent (layout not
  derivable from cited masks — filed, not guessed)
- `htt/` — README-only open item (no lab spec exists; fetch attempts
  failed 2026-11-16)
- `lpec/frame-parser` — the lab's LPEC frame parser packaged standalone
  with spec-doc provenance (Sony binaries never committed)

Liaison: upstream PR #58's own body confirms the gap ("WMI/HTT/CE and
the RF/PHY stack are not implemented") — these components target it.
RULE 0 queries + dates recorded in `implementations/README.md`.

## Phase 4 — device fragmentation: DONE

`blob-matrix/desktop/fragmentation-half.md` — SoC generations (29
Qualcomm chips, 14 Tensor), corrected leverage ranking, family×device
coverage, byte-weighted top-15, and merge notes for the lead.

## Flags for the lead (shared files untouched, per file-wall)

1. recon.md top-20 re-rank: oplus VOOC pair (36) above BT fleet (29).
2. recon.md "248 tokens" → 123 (parse artifact).
3. Work order "444 devices" → 249-identity universe; laptop remainder is
   rows 223–249 (imbalance 222/27 for lead rebalance).
4. Coverage matrix carries 586 true duplicate (device, filename, md5)
   triples (341 in desktop half); recon's 33,917 counts them.
5. Inventory: duplicate display names `Phone_2` (aura/Pong) and
   `Xperia_1_II` (two codenames); typo `Poco_F6_PRo`; stray `\ufffd` SOC
   byte (already flagged in recon).

## Push mechanics (honest note)

This environment has no `github-personal` SSH alias, no adineo-cmd key, and
no HTTPS credentials, so the git transport the lab's standing rules assume
was unavailable; pushes went through the GitHub MCP as adineo-cmd. The
5.9 MB `devices-001-222.csv` exceeds what can be inlined through that path;
every other deliverable is pushed. The CSV is committed locally (WO-001
Phase 1 / addendum commits) with sha256
`aebb473a972dbf47aff45ce9951026e6e1d19d45655b2b0cb6d7c646ad4276ac`, and is
byte-reproducible from committed inputs: run
`blob-matrix/desktop/tools/phase1_build.py` against the committed
`coverage-matrix.csv` + `device-inventory.csv` + `enchilada-census.csv`
(all pushed) — or push it from any environment with the adineo-cmd git
alias. (v2 of the CSV, 34,052 rows, additionally carries the 403
modem-FAT census rows — see partition-map addendum 2; the extended
census CSV is kept alongside locally.)

## Honest negatives / open items

- 100 listed-not-populated + 12 builds-csv-only devices remain
  metadata-only (OnePlus 6 is the proof-of-population; ~1.07 GB per
  device — bulk decision is the lead's).
- P2 "mainline basis" strings not verified against postmarketOS wiki.
- cmnlib/cmnlib64/keymaster/boot-chain partitions one payload_dump away
  from being censused (hashing not run this session).
- LineageOS mirrorbits dropped one transfer (0-byte, empty sha256)
  before the successful `curl -L` re-download — logged, recovered.

## Fleet deep-RE addendum (2026-11-16, same session, post-Phase-4)

Continued into actual blob RE per the leverage-first order. First pass
delivered: the OnePlus 6 `bt.img` partition is a FAT16 volume carrying
the entire QCA BT patch/NVM fleet; all six top-20 md5s extract
byte-exactly from it (two double-verified against linux-firmware); the
container format is decoded from public GPL btqca structs and verified
10/10 against real bytes (patch headers with per-generation entry
addresses 0x1b0e0/0x1b15c/0x209e4, one exact-closing NVM tag set + one
unknown type-3 set each, first public NVM tag enumeration 9→45 tags).
Patch-stream diff across families: no record framing — a flat code image
with scattered instruction-level deltas; the 256-byte tails are
per-family content. Deliverables: `blob-matrix/desktop/fleet-re/qca-bt-format.md`,
`tools/qca_tlv_parse.py`, `tools/fat_extract.py`; the 53 KB results JSON
stays local with reproducibility provenance (regenerable byte-identically
via the committed tool from any official LineageOS nightly of a
fleet-carrying device — same push-path class as the devices CSV);
`docs/devices/oneplus6/bt.md` upgraded to format-spec class. Open:
patch-stream entry structure (no record framing found — flat image),
ap*/cr* family attribution, 256-byte tails, NVM tag names ≥ 0x0020.

## Partition-map addendum 2 (2026-11-17, continued session)

Fleet deep-RE pass 2, still payload-only OnePlus 6: `modem.img` (119.8 MB)
is a **FAT16 volume** carrying **403 named firmware files / 113.5 MB** —
the full OP6 firmware set (`image_modem.b16-b24` mpss segments up to
26.3 MB, adsp/cdsp/slpi MDT sets, **`image_wlanmdsp.mbn` = the WCN3990
WiFi firmware** resolving the wifi census-negative finding, 37 ×
`image_bdwlan.*` board-data variants, gfp9508, qdsp6m.qdb, manifests).
`tz.img` is ELF64 AArch64 (e_machine 183, 17 phdrs); `dsp.img` is raw
with 60 Hexagon ELF32 blobs from 0x48f000. **201 of the 403 files md5-join
to multi-device fleet blobs in the committed matrix** — the sha256↔md5
fleet join is delivered at scale from this one device. The devices CSV
grows to 34,052 rows (v2, local, regenerable; +403 modem-FAT census rows —
regen path: `tools/fat_extract.py` on modem.img → append census rows →
`tools/phase1_build.py`). Deliverables:
`fleet-re/oneplus6-partition-map.md`, updated
`docs/devices/oneplus6/{modem,wifi}.md`. Open: the 60 dsp.img ELF
identifications, tz QSEE segment map, `bdwlan.*` board-data format
(19,152 B fixed records; 37-variant diff is the natural probe).
