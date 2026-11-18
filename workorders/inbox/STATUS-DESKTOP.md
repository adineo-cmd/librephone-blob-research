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
6. Addendum 5: matrix coverage gap — `libsns_low_lat_stream_skel.so` and
   `libsns_device_mode_skel.so` are real fleet blobs (byte-identical
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
alias. (v3 of the CSV, 34,054 rows, additionally carries the 404 modem-FAT
census rows with the addendum-5/6 corrections — VERINFO/VER_INFO.TXT row
added, MBN_HW.TXT corrected to its FAT-declared size 0; the extended
census CSV is kept alongside locally.)

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
`docs/devices/oneplus6/bt.md` upgraded to format-spec class.

## Partition-map addendum 2 (2026-11-17, continued session)

Fleet deep-RE pass 2: `modem.img` (119.8 MB) is a **FAT16 volume**
carrying **404 named firmware files / 113.4 MB** — the full OP6 firmware
set (`image_modem.b16-b24` mpss segments up to 26.3 MB, adsp/cdsp/slpi
MDT sets, **`image_wlanmdsp.mbn` = the WCN3990 WiFi firmware** resolving
the wifi census-negative finding, `image_bdwlan.*` board-data variants,
gfp9508, qdsp6m.qdb, manifests). `tz.img` is ELF64 AArch64 (17 phdrs);
`dsp.img` was probed raw (later corrected to ext4, addendum 3). **201
files md5-join to fleet blobs**. Deliverables:
`fleet-re/oneplus6-partition-map.md`, updated
`docs/devices/oneplus6/{modem,wifi}.md`.

## Subagent deep-pass addendum 3 (2026-11-17, four parallel analysis streams)

1. **bdwlan board-data format RESOLVED** (`fleet-re/bdwlan-format.md`):
   flat TLV chain `{u16 tag, u16 len, payload}` to EOF, 17 strictly-
   sequential IEs (b38 re-chunks to 18), sums exactly 19,152 on every
   file; 35 files / 29 md5 clusters; stride-40 and stride-4 record
   tables; per-board ID fields at abs [10,12) and [408,410).
2. **dsp.img + tz.img mapped** (`fleet-re/dsp-tz-map.md`): dsp.img is
   **ext4** holding 62 files — 57 Hexagon ELF32 fastrpc user-PD modules
   (/adsp /cdsp /sdsp), 0/17 identity with the modem-FAT PIL set (disjoint
   by design); tz.img QSEE ELF64 segmented, version strings
   `TZ.XF.5.0.1.C5-00083.1` / `WAXAANAAA` / `CRM`.
3. **BT patch-stream + tails resolved** (`fleet-re/patch-stream-structure.md`):
   tails are per-file-unique signature/attestation-class blocks (not any
   digest of the stream); streams are flat dense images; the ap/cr 128-B
   delta accumulates in ONE localized region (a-side ≈ 23.7-24.7K);
   each stream contains exactly one literal u32 equal to its own entry
   value at a per-generation offset (472/636/428).
4. **Second device populated** (`fleet-re/second-device-larry.md`):
   `larry` (Nord CE 3 Lite, SM6375, LineageOS 24.0): **bm2n fleet 6/6
   byte-exact** (aliases bm2n12≡bm2n37, bm2n14≡bm2n55, bm2n15≡bm2n31),
   apnv11_eu/in/na 3/3; 299 files / 74.5 MB censused; vendor/odm are
   **EROFS** (`fsck.erofs --extract` method note).

## Addendum 4 (2026-11-18, GPU/bdwlan + VOOC proof)

1. **GPU/bdwlan stream** (`fleet-re/gpu-bdwlan.md`): ZAP containers
   resolved; **6/6 GMU/SQE fleet identities proven** (a619_gmu = 24-device
   top-20 blob); cross-device bdwlan same grammar (19 IEs); regdb.bin
   decoded as ISO 3166-1 record table; gfp9508 = signed ARM QSEE apps.
2. **VOOC leverage entry PROVEN** (`fleet-re/third-device-instantnoodle.md`):
   `instantnoodle` (OnePlus 8, SM8250, LineageOS 24.0 sha256-verified):
   **both VOOC blobs byte-exact (18/18 matrix rows = 100% fastchg
   coverage)**, 2,107-row census, **492 fleet md5 joins**, 98% inverse
   join, FAT16 bluetooth/modem pattern confirmed on SM8250.

## Addendum 5 (2026-11-18, sharing matrix + QSEE decode)

1. **Three-device sharing matrix** (`fleet-re/three-device-sharing.md`):
   of 2,509 distinct md5s across the three censuses, only **4 blobs on
   all 3 devices**, 17 on exactly two, 2,488 device-unique; unique
   share 98.7-99.98% by bytes; fleet coverage **574/15,091 (3.80%)**;
   **FAT-entry delta RESOLVED** (404th entry = VERINFO subdirectory);
   matrix coverage gap flagged (libsns_* skel fleet blobs absent).
2. **QSEE cross-generation decode** (`fleet-re/qsee-crossgen.md`):
   instantnoodle tz mapped (23 phdrs, e_entry 0x14680000 identical to
   OP6, **TZ.XF.5.8-00274 / DARAANAAA / CRM**); **metadata hash-slot
   layout decoded — first public** (seg[1] = header + per-phdr digest
   table + 2 RSA-2048 PSS sig blocks bound to leaf cert keys + two
   3-cert X.509 chains); fastrpc embedded-ELF magics = false positive
   (loader magic constant + error string); a660_gmu leading table
   confirmed against mainline `struct block_header`.

## Addendum 6 (2026-11-19, two parallel subagent streams — PIL sweep + bm2n/BT/tag-19)

1. **PIL metadata sweep** (`fleet-re/pil-metadata-sweep.md`): all 28
   signed PIL images across both devices (tz, hyp, xbl, xbl_config, abl,
   aop, cmnlib, cmnlib64, keymaster, devcfg, uefisecapp, imagefv, qupfw,
   storsec, multiimgoem, featenabler) match the decoded hash-slot layout
   — **zero exceptions; the container is universal across the entire
   secboot chain**. **SHA-384 is SM8250-wide, not TZ-specific** (16/16
   SM8250 = 48-B slots; 12/12 SDM845 = 32-B; 220 slots verified, 178
   digest hits). Header geometry refined (Rule-1 corrections to
   qsee-crossgen.md): SM8250 header = 168 B base + 120 B per extra
   chain (288 B = the 2-chain case); w[9] = 6144 × chain_count;
   w[4]−w[5] = 6400 + 12800 × (chains−1); w[2]/w[3] zero unless second
   chain — all 28/28. Signing facts: 35 chains / 105 certs, only 7
   production chains (28 test-only, build-time re-signing with the OEM
   test root); xbl carries embedded sub-image version triples on both
   devices.
2. **bm2n + BT + tag-19 stream** (`fleet-re/bm2n-isa-bt.md`):
   - **bm2n fleet**: raw loader-header images, not ELF (header:
     0xFA0000FA marker, size-class 0x200000, 7-hex build id at [12,19);
     bm2n13≡bm2n15 same build 5371806); **ISA verdicts: Hexagon-
     consistent [I] on all 6** — the strongest signal is 30-52 shared
     Itanium RTTI type names with verified-Hexagon
     `libbitml_nsp_v2_skel.so` (bm2n = **BitML/NSP DSP-side payload
     images**, a Qualcomm internal ML stack); bm2n08 carries 56 packed
     islands ≥7.5 bits/B (ISA of islands unknown).
   - **OnePlus 8 BT fleet**: WCN3998 ships a **third QCA prefix family
     `ht*`** (htbtfw10/20.tlv + htnv10/20.bin; LFNs recovered from the
     FAT), each md5 = OnePlus_8+8_Pro only; **zero overlap with the OP6
     ap*/cr* fleet**; ht* patch envelope changed (36-B header, 32-B
     tail, product_id 16, entry 0); NVM = direct type-2 tag sets with
     38/52 tag-ID overlap and 14 new tag IDs.
   - **larry bdwlan tag 19**: **stride-14 regdb-class country table**
     (199 records × 14 B, 0xA028 marker, 147/199 records byte-identical
     to larry's regdb.bin; CC set adds CW / drops AO+IR) — NOT an
     extended tag-8; payload byte-identical across bin/in/us; tail
     [2794,7172) unresolved. Rule-1 correction applied to gpu-bdwlan.md
     §5.2 ("100% non-zero" was wrong: nonzero 0.4099).

Census corrections applied (addendum 5+6): 404th modem-FAT row
(VERINFO/VER_INFO.TXT 1,201 B) appended; MBN_HW.TXT corrected to its
FAT-declared size 0 (was recorded at the 16,384 B cluster-chain size);
devices CSV v3 = **34,054 rows** (local, sha256 recorded in git log).

Session totals after addendum 6: **three devices populated** (SM845,
SM6375, SM8250), ~2,850 censused blob files with hashes, every
leverage-family identity proven (QCA BT fleet, bm2n fleet = BitML/NSP,
VOOC pair, GMU/SQE blobs), **8 container formats decoded** (QCA BT TLV,
bdwlan TLV, BT patch stream + tails, QSEE metadata hash-slot layout
[universal, 28/28], GMU block chain, regdb ISO-3166 table, ht* envelope,
FAT16 firmware volumes ×3 devices), clean-room WMI/CE/HTC/TLV
components + LPEC packaging shipped, three-device sharing matrix
quantified, two first-public decodes published (QSEE metadata
hash-slot layout; NVM tag enumeration).

Open after addendum 6: bm2n loader header decode + Hexagon byte-level
verification (needs a Hexagon disassembler); ht* 36-B header interior;
tag-19 tail [2794,7172); QSEE header word[0]/w[1] semantics; SIG byte
range; remaining ~100 unpopulated devices (bulk decision with the
lead).
