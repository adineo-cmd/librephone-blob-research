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
6. NEW (addendum 5): matrix coverage gap — `libsns_low_lat_stream_skel.so`
   and `libsns_device_mode_skel.so` are real fleet blobs (byte-identical
   across SM845/SM6375/SM8250) with **zero matrix rows**; same for
   `libcamera_nn_skel.so` (809,688 B, SM6375+SM8250 shared).

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
census CSV is kept alongside locally. Addendum-5 correction: the census
should carry 404 modem-FAT rows — see addendum 5 §5.)

## Honest negatives / open items

- 100 listed-not-populated + 12 builds-csv-only devices remain
  metadata-only (enchilada + larry + instantnoodle are the three
  populated proofs; ~1.1-1.6 GB per device — bulk decision is the
  lead's).
- P2 "mainline basis" strings not verified against postmarketOS wiki.
- LineageOS mirrorbits dropped transfers twice across the session
  (0-byte and a 588 MB stall) — both recovered (`curl -L` / `curl -C -`);
  logged.

## Fleet deep-RE addendum (2026-11-16, same session, post-Phase-4)

Continued into actual blob RE per the leverage-first order. First pass
delivered: the OnePlus 6 `bt.img` partition is a FAT16 volume carrying
the entire QCA BT patch/NVM fleet; all six top-20 md5s extract
byte-exactly from it (two double-verified against linux-firmware); the
container format is decoded from public GPL btqca structs and verified
10/10 against real bytes (patch headers with per-generation entry
addresses 0x1b0e0/0x1b15c/0x209e4, one exact-closing NVM tag set + one
unknown type-3 set each, first public NVM tag enumeration 9→45 tags).
Deliverables: `blob-matrix/desktop/fleet-re/qca-bt-format.md`,
`tools/qca_tlv_parse.py`, `tools/fat_extract.py`; the 53 KB results JSON
stays local with reproducibility provenance (regenerable byte-identically
via the committed tool from any official LineageOS nightly of a
fleet-carrying device — same push-path class as the devices CSV);
`docs/devices/oneplus6/bt.md` upgraded to format-spec class. Open:
patch-stream entry structure (no record framing found — flat image),
ap*/cr* family attribution, 256-byte tails, NVM tag names ≥ 0x0020.

## Partition-map addendum 2 (2026-11-17, continued session)

Fleet deep-RE pass 2, still payload-only OnePlus 6: `modem.img` (119.8 MB)
is a **FAT16 volume** carrying **404 named firmware files / 113.5 MB** —
the full OP6 firmware set (`image_modem.b16-b24` mpss segments up to
26.3 MB, adsp/cdsp/slpi MDT sets, **`image_wlanmdsp.mbn` = the WCN3990
WiFi firmware** resolving the wifi census-negative finding, `image_bdwlan.*`
board-data variants, gfp9508, qdsp6m.qdb, manifests). `tz.img` is ELF64
AArch64 (e_machine 183, 17 phdrs); `dsp.img` was probed raw. **201 of the
extracted files md5-join to multi-device fleet blobs in the committed
matrix** — the sha256↔md5 fleet join is delivered at scale from this one
device. The devices CSV grows to 34,052 rows (v2, local, regenerable).
Deliverables: `fleet-re/oneplus6-partition-map.md`, updated
`docs/devices/oneplus6/{modem,wifi}.md`.

## Subagent deep-pass addendum 3 (2026-11-17, four parallel analysis streams)

Four subagent streams (facts-only, repo untouched by them) closed four
open items:

1. **bdwlan board-data format RESOLVED** (`fleet-re/bdwlan-format.md`):
   flat TLV chain `{u16 tag, u16 len, payload}` to EOF, no outer magic,
   34 files carry 17 strictly-sequential IEs (b38 re-chunks the tail to
   18), chain sums to exactly 19,152 on every file; 35 files / 29 md5
   clusters (count corrected from 37); stride-40 and stride-4 record
   tables identified; per-board ID fields at abs [10,12) (28 values) and
   [408,410) (3 values); minimal-diff cluster pairs (2 bytes). Honest
   negatives: no checksum, no ASCII metadata, no nested TLVs. Counts
   corrected: 404 FAT entries (403 was stale), 35 bdwlan files.
2. **dsp.img + tz.img mapped** (`fleet-re/dsp-tz-map.md`): dsp.img is
   **ext4** (volume "dsp", 8,192 × 4,096 B blocks, clean journal) holding
   62 files — 57 Hexagon ELF32 fastrpc user-PD modules (/adsp /cdsp
   /sdsp; audio codecs, vpp, chre, libc++, fastrpc shells), 0/17 identity
   with the modem-FAT `IMAGE_ADSP.*` PIL set (disjoint by design — boot
   PIL vs runtime fastrpc, proven at whole-file/raw/segment levels);
   tz.img QSEE ELF64 fully segmented (17 phdrs, two vaddr regions,
   QSEE metadata seg with X.509 chain, version strings
   `TZ.XF.5.0.1.C5-00083.1` / `WAXAANAAA` / `CRM`), per-segment
   sha256 + entropy in the JSON.
3. **BT patch-stream + 256-byte tails resolved**
   (`fleet-re/patch-stream-structure.md`): tails are per-file-unique
   high-entropy signature/attestation-class blocks (table and padded
   header refuted; not sha256/md5/sha1 of the stream; 0 shared words
   across all 10 pairs); patch streams are flat dense images (zero-run
   framing refuted); the ap/cr 128-byte delta accumulates in ONE
   localized region (a-side ≈ 23.7-24.7K), not an insertion block —
   one firmware built twice with a ~128-B larger section; each stream
   contains exactly one literal u32 equal to its own entry value at a
   per-generation offset (472/636/428). Rule-1 correction recorded: the
   stale local `qca-bt-tlv.json` carried an entry misread (0x80000002);
   committed parser is correct.
4. **Second device populated** (`fleet-re/second-device-larry.md`):
   `larry` (OnePlus Nord CE 3 Lite / N30 5G, SM6375) from the official
   LineageOS **24.0** nightly (sha256-verified 1,601,993,721 B): **bm2n
   fleet 6/6 byte-exact** (first SM6375-generation fleet proof; aliases
   bm2n12≡bm2n37, bm2n14≡bm2n55, bm2n15≡bm2n31), apnv11_eu/in/na 3/3;
   299 files / 74.5 MB censused. Honest negatives: VOOC pair absent
   (SM8250-only per the matrix — the #1 leverage entry needs
   instantnoodle/kebab); no modem/bt/radio partitions in the 24.0
   payload; **vendor/odm are EROFS, not ext4** (`fsck.erofs --extract`
   used — method note for all future 24.0-era payloads). The session
   brief's VOOC md5s were corrupted (suffix collision with crnv20.bin's
   md5); matrix md5s were used correctly.

Open after addendum 3: tz QSEE metadata layout + fastrpc embedded ELFs;
bdwlan tag semantics; tail construction; VOOC proof via an SM8250
payload; the 403-vs-404 FAT-entry delta (one unresolved entry).

## Addendum 4 (2026-11-18, two parallel subagent streams — GPU/bdwlan + VOOC proof)

1. **GPU/bdwlan stream** (`fleet-re/gpu-bdwlan.md`): ZAP shader
   containers fully resolved (ELF32 EM_QDSP6 ET_EXEC, e_entry 0x5000,
   mdt = b00+b01 concat, .elf = page-aligned variant, geometry identical
   across a630/a615/a660); **6/6 GMU/SQE fleet identities proven** (OP6
   a630_gmu = 8-device blob; larry a619_gmu = 24-device top-20 blob,
   a630_sqe = 19, a660_gmu = 19, a660_sqe = 21; zap absent from the
   matrix entirely); a630/a619 share one container generation (1,076-B
   common prefix, second 16 KiB byte-identical), a660 is a different
   generation (table-style head); gfp9508/gfp5288 = **signed ARM
   TrustZone QSEE apps** (EM_ARM, X.509 chain, fingerprint-sensor [H]) —
   not Hexagon; cross-device bdwlan: larry's files parse under the same
   TLV grammar (19 IEs, tags 1-15 lens byte-identical to OP6, tail =
   b38-style re-chunk + NEW dense tag 19 of 7,172 B), tags 3/5/6/10
   byte-identical across generations, 0 md5 matches (board data is
   generation-specific); regdb.bin decoded as an ISO 3166-1 record
   table (stride 14, ~198 records) — a different container.
2. **VOOC leverage entry PROVEN** (`fleet-re/third-device-instantnoodle.md`):
   `instantnoodle` (OnePlus 8, SM8250) from the official LineageOS
   24.0 nightly (sha256-verified 1,385,279,498 B; one stall at 588 MB
   recovered via `curl -C -`): **both VOOC blobs byte-exact (18/18
   matrix rows = 100% of instantnoodle fastchg coverage)**, plus 25
   newer/older fastchg variants the matrix lacks (free fleet-delta).
   Census: **2,107 rows** across 30 partitions (bluetooth/modem FAT16 —
   the OnePlus 6 pattern confirmed on SM8250; odm/vendor EROFS; dsp
   EXT4 with 75 modules; 16 single-ELF firmware partitions); **492
   fleet md5 joins** (454 distinct matrix md5s) and the inverse join
   covers **98% of instantnoodle's own matrix rows**. Honest negatives:
   0/84 adsp rows matched (SM8250 ships no bm2n fleet), 11/504 matrix
   md5s unmatched (build drift).

Open after addendum 4: tz QSEE metadata layout, bdwlan tag semantics,
tail construction, three-device sharing quantification.

## Addendum 5 (2026-11-18, two parallel subagent streams — sharing matrix + QSEE decode)

1. **Three-device sharing matrix** (`fleet-re/three-device-sharing.md`):
   first cross-SoC-generation identity analysis (SM845 × SM6375 ×
   SM8250): of 2,509 distinct md5s across the three censuses, only **4
   blobs are carried by all three devices** (2 of them — `libsns_*_skel.so`
   — absent from the 123-device matrix: a coverage gap), 17 on exactly
   two, 2,488 device-unique; unique-content share 98.7-99.98% by bytes —
   fragmentation dominates, leverage concentrates in tiny shared files.
   Fleet coverage: the three devices cover **574 of the 15,091 upstream
   fleet md5s (3.80%)**. **FAT-entry delta RESOLVED**: the OP6 modem.img
   404th entry is a root-level **`VERINFO` subdirectory** whose child
   `VER_INFO.TXT` (1,201 B) is the 404th named file (0 deleted entries,
   0 volume labels); the 113,460,308 B prior total over-counted
   `MBN_HW.TXT` (FAT-declared size 0) by one 16,384 B cluster chain.
   Census actions for the owner: append the 404th row, correct
   MBN_HW.TXT.
2. **QSEE cross-generation decode** (`fleet-re/qsee-crossgen.md`):
   instantnoodle tz.img fully mapped (ELF64, 23 phdrs, e_entry
   0x14680000 **identical to OP6**, version triple
   **TZ.XF.5.8-00274 / DARAANAAA / CRM**); **QSEE metadata hash-slot
   layout decoded — first public**: seg[1] = header + per-phdr digest
   table + two RSA-2048 signature blocks + two 3-cert X.509 chains;
   slot count == phdr count, slot[i] = digest of phdr[i] file content,
   width 32 B (SHA-256, SDM845) → 48 B (SHA-384, SM8250), header word[5]
   records the table length exactly; empty segments stored as zero
   slots; signatures bind to the paired chain's leaf keys (RSASSA-PSS
   EM tail 0xBC, 4/4, with 4/4 cross-key negative controls); root CAs:
   Qualcomm-owned on SDM845 vs an OEM-owned test root on SM8250.
   fastrpc embedded-ELF magics: **false positive** (0/3 — the loader's
   magic constant + error-string rodata); a660_gmu.bin leading table
   **confirmed against mainline** (`struct block_header` chain, 15
   blocks, 11 zero-size prealloc-request TOC entries fitting mainline's
   hardcoded a660 allocations, 4 DEADBEEF-tagged data blocks routed
   ITCM/icache/DTCM; a619_gmu is the raw legacy format).

Open after addendum 5: metadata header word semantics (word[0]/[1],
word[4] constant 19,200); SIG byte-range (PSS salt); bdwlan tag
semantics; SHA-384 metadata: TZ-specific or SM8250-wide (re-run on
cmnlib/keymaster); VERINFO census-row append (census owner).

Session totals after addendum 5: **three devices populated** (SM845,
SM6375, SM8250), ~2,850 censused blob files with hashes, every
leverage-family identity proven (QCA BT fleet, bm2n fleet, VOOC pair,
GMU/SQE blobs), **7 container formats decoded** (QCA BT TLV, bdwlan TLV,
BT patch stream + tails, QSEE metadata, GMU block chain, regdb
ISO-3166 table, FAT16 firmware volumes ×2), clean-room WMI/CE/HTC/TLV
components + LPEC packaging shipped, three-device sharing matrix
quantified, and the QSEE metadata layout published as a first-public
decode.
