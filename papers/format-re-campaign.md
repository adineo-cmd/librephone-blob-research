# Four legacy formats decoded and one database encryption completely cracked in three sessions: the format-RE campaign (F-34 → F-39)

**Research note, librephone-blob-research — 2026-11-13.**
Synthesis of Open Discovery Lab findings F-34 → F-39 (Track C discovery engine, sessions of 2026-11-12; the campaign ran in [adineo-cmd/open-discovery-lab](https://github.com/adineo-cmd/open-discovery-lab), which holds the full evidence chain). Every number below traces to a committed source document (Appendix A).

**One-line claim.** Mining the dexvert registry's "no known converter" notes as a scored target queue, the lab produced in three 2026-11-12 sessions the first public standalone decoder and format spec for ProLine Voice Data (Amiga BBS voicemail), the first public structural write-up of the Instant Graphics and Sound BBS protocol (Atari ST 640×200 space, 12/12 validated), a byte-exact 8/8 resolution of the Professional Draw clip container, and a 49-file corpus validation of Clarion .DAT with four spec corrections and a complete 6/6 crack of its header-and-record encryption with the 1991 contents recovered — plus a container census of Sony DVF/MSV voice-recorder files with a previously undocumented bitrate relation; the LPEC/TRC audio codec itself and queue items R-5..R-12 remain open.

## Abstract

We report the Open Discovery Lab's format-RE campaign: a repeatable pipeline — dexvert-registry mining → sample acquisition from a public mirror → multi-file census → arithmetic crack → stdlib decoder with independent validation → dated prior-art checks — run end-to-end against four legacy formats and one audio-container family, all drawn from a 12-item scored queue of "detected but unconverted" formats. Results: (1) **ProLine Voice Data** (.pvd): header cracked 5/5, the first public decoder (`pvd_decode.py`) and first public byte-level spec, with a visible self-correction of the campaign's own first-look byte offsets and an honestly unresolved sample rate (Paula-period ~20.5 kHz recommended, alternatives documented and reproducible); (2) **Instant Graphics and Sound** (.igs/.ig/.igm): the first public structural write-up — `letter>args` command grammar, Atari ST 640×200 coordinate space with 0 violations in 1,293 numeric args, the .IG/.IGS relationship cracked by pair diff, validated 12/12; (3) **Professional Draw** (.clips): the PDPF clip container resolved byte-exactly in 8/8 samples (100% chunk coverage, zero-length section brackets, semantic clip names), with the .pdraw document variant confirmed as a different container; (4) **Clarion .DAT**: the published layout validated 43/43 by three exact arithmetic identities, four corrections/extensions to the published spec, and — the technical centerpiece — a complete crack of the file encryption: a 2-byte periodic XOR with per-file keys and per-section keystream phase reset, all 6/6 encrypted files recovered by an exhaustive 65,536-candidate brute force scored on arithmetic identities, yielding George Tanner's 1991 journal (weekday-validated), a shareware password table, and a 1990 Torbert Data Systems control record, and pinning the Clarion date epoch to 1800-12-28. Every correction stays visible: F-34's PVD byte-offset reading corrected by F-35; F-38's "4/6 need longer keystreams" refuted by F-39's exhaustive search; and the queue's own "zero docs" premise for R-3 refuted by its Rule-0 check.

## 1. Background: the scored queue

Track C's founding premise (F-3, verified 2026-11-09) is that "zero public documentation AND obtainable samples" identifies a live queue of unique reverse-engineering targets; the lab's adversarial prior-art audit (2026-11-11, commit `a8cc9d7`) unique-confirmed that methodology claim.

F-34 (`results/format-re-v2.md`, commit `5c22031`) operationalized it for formats: `Sembiance/dexvert` SUPPORTED.md (4,017 formats) + UNSUPPORTED.md (4,025 detected-but-unconverted — the spec-gap pool) were mined at commit `b126fe4` (fetched 2026-11-12), weak-support signals taken from per-format notes ("no known converter", "room for improvement", decode-distortion), and sample availability verified against `sembiance.com/fileFormatSamples` (dexvert's own sample mirror). The output is a 12-item queue scored novelty/feasibility/value (max 15): R-1 Sony DVF/MSV (14), R-2 ProLine PVD (13), R-3 Clarion .DAT (13), R-4 IGS (12), R-5 Psion AIK (12), R-6 Professional Draw (11), R-7 Sonic Arranger, R-8 NTitler, R-9 DiamondWare DWM, R-10 ANSI Music (10 each), R-11 Beam SIFF, R-12 CMS Intelligent Organ (9 each). Downgrades at scoring time: Qualcomm QCP (ffmpeg ships both container and QCELP decoder — novelty 1), DSS, QuickTime Audio, and four items with no mirror samples.

The queue carried its own caveat honestly: novelty ratings for R-3..R-12 used Sembiance's notes as proxy and were flagged "verify before claim". That flag proved load-bearing. R-3's Rule-0 check (F-38) **refuted the inherited "zero docs" premise**: the legacy Clarion .DAT layout was documented all along (a Russian-language clarionlife.net layout article, comp.lang.clarion threads, and existing readers — SourceForge `clariondbreader`, commercial DataMeans/AETL). dexvert's "Did a Google search, couldn't find anything about it" was a search failure, not a documentation gap. The lesson is now part of the method: registry notes are *search-failure signals* that nominate targets, never uniqueness proofs; only a dated Rule-0 check gates any "first" claim.

## 2. Prior art (the uniqueness proof)

All checks were run 2026-11-12, per format, before any uniqueness claim:

- **ProLine PVD** — dexvert `prolineVoice.js` (SHA `584cba02` @ `b126fe4`) is detection-only (`unsupported = true`), with a comment doubting the files are sampled audio ("only 16 unique files on discmaster… unlikely to be sampled audio"); TrID `audio-pvd.trid.xml` and file-signature lists are ID-only; GitHub code search (`Proline Voice File`, `proline pvd voice`) and web search surface no decoder, spec, or RE write-up. The census refuted dexvert's doubt (these are real 8-bit PCM recordings). **First public standalone decoder + first public format spec** stands, with two stated caveats: the sample-rate value is hypothesis-grade (§4.2) and an unpublished private decoder cannot be ruled out.
- **IGS** — dexvert `instantGraphicsAndSound.js` is `unsupported = true` ("No known converter yet. Seen a recent resurgence in interest in 2024"; 46 unique files on discmaster). The cited resurgence was verified (Reddit r/bbs ~Oct 2024 and r/vintagecomputing Sept 2024 history series) — no tooling came out of it. No public decoder, spec, or tooling found. **First public structural write-up** stands.
- **Professional Draw** — dexvert `professionalDraw.js` is `unsupported = true` ("No known converter"; 746 unique files on discmaster), with Sembiance's own comment suspecting clip/document/page are different file types. No converter, spec, or write-up found; DigiPres/Wikidata confirm `.clips` as the clipart extension. **First public structural description** stands — and dexvert's hunch is confirmed: clips and documents are indeed different containers (§4.4).
- **Clarion .DAT** — premise refuted as above; the honest claim is **independent corpus validation + spec extensions + encryption crack**, not first documentation. Additional prior-art fact: dexvert detects by magic string "Clarion 2 DataBase for DOS", which appears in *none* of the 49 samples — all use the binary signature `0x3343` (two signature generations; only the binary one is represented in this corpus).
- **Sony DVF/MSV** — the PRONOM "Sony Voice Recorders" research submission (2023) is byte-pattern identification only; GitHub code search and web search (2026-11-12) find no open-source LPEC/TRC decoder; preservation surveys (Obsolete Thor blog, 2023-04-21) document exactly this gap. One correction to PRONOM fell out: its "DVF TRC" regex **misses LPEC-in-.dvf files** (budgtele.dvf carries LPEC-family bytes `01 01`) — the extension is not a reliable codec indicator.
- **Method-level** — the 2026-11-11 audit's treatment of the queue methodology (F-3: unique-confirmed at low depth) is the standing uniqueness proof for the pipeline itself. The audit also caught a dangling citation in a sibling track (zrax's "socboot2", cited by Track A's F-18, could not be located publicly — a false-negative risk in prior-art attribution). That failure mode is why every Rule-0 check in this campaign records its exact query strings and dates: a claim that names its check can be invalidated precisely by future prior art.

## 3. Method: the repeatable pattern

The campaign ran the same six steps on every target:

1. **Registry mining** — dexvert SUPPORTED/UNSUPPORTED @ `b126fe4`; weak-support notes nominate targets; scores rank them (N/F/V).
2. **Sample acquisition** — the `sembiance.com/fileFormatSamples` mirror (the dexvert-samples GitHub repo 404'd for the lab's token; the mirror used instead). 9 (PVD+DVF/MSV) + 12 (IGS) + 10 (Professional Draw) + 49 (Clarion) samples fetched to /tmp only. **No sample bytes are committed anywhere** — only decoded facts, per the lab's clean-room rule.
3. **Census** — hexdump head/tail, printable strings, 1 KB-block entropy maps, and above all cross-file header-field alignment; per-format raw census JSONs are committed.
4. **Arithmetic crack** — exact cross-file identities (payload == filesize−24; chunk walk == filesize; filesize == offset + numrecs·reclen). Identity failures localized byte-offset misreadings; identity successes pinned the structure.
5. **Decoder + independent validation** — stdlib-only Python decoders, committed validation JSONs, explicit negative tests (bad magic, truncation, length mismatch), and documented self-corrections: the F-35 agent caught and fixed its own defect mid-task (hand-assembled validation stats and a RIFF chunk-walk bug) and re-ran so the committed JSON is strictly decoder-reproducible.
6. **Prior-art checks with dates** — Rule 0 before every "first" (Section 2).

## 4. Results

### 4.1 Sony DVF/MSV container (R-1, first look — the one open front)

Census of 4 files (07011600.MSV, WelcometoPinkston…dvf, budgtele.dvf, taxis.dvf). Key fields: magic `MS_VOICE` + `00 00 00 50`; codec family at 0x0C (`01 01 00 00` = LPEC-family, `01 02 00 00` = TRC, matching PRONOM's BOF patterns); "SONY CORPORATION" at 0x10; origin string at 0x20 (device model `ICD-BM1` or codec DLL `PVoice.dll`/`STVoice.dll`); big-endian date/time at 0x34 (two values filename-validated; taxis.dvf has 0xFF = unset); free-text annotations embedded ("Jane Ann Knowles" recovered from strings — a forensic hook).

The structural finding: 0x3C BE u16 codec submode (42/44/48 per variant), 0x40 BE u32 = **bitrate in bits/s (16000/19200/6000)**, and 0x44 BE u32 = **exactly bitrate/8 in all three files (2000, 2400, 750 bytes/s)** — a relation not previously documented publicly. From 0x50: an 8-byte-stride tag/size table (tags 01–0E), then compressed audio at 7.7–7.9 bits/byte entropy.

**Honest negative**: the LPEC/TRC bitstream itself is undecoded — that is the actual prize and remains open (frame geometry, the 0x50 TOC, the codec).

### 4.2 ProLine Voice Data (R-2 — first public decoder + spec)

| Offset | Field | Observed (5/5 samples) |
|---|---|---|
| 0x00 | u8 Pascal length | `0x12` (18) |
| 0x01–0x12 | ASCII magic | `Proline Voice File` |
| 0x13 | version | `0x01` |
| 0x14–0x16 | u24 LE payload length | == filesize − 24, 5/5 |
| 0x17 | u8 mystery constant | `0xAD` (173) |
| 0x18 | payload start delimiter | `0x00` |
| 0x19.. | unsigned 8-bit mono PCM | silence floor `0x7F` |
| last | payload end delimiter | `0x00` |

**Correction banner (F-34 → F-35, kept visible)**: the F-34 census read `0x00AD` as a u16 at 0x17 with the body at 0x19. Arithmetic forces the reading above — payload = filesize−24 must start at 0x18, so 0x17 is a *single* byte and the `0x00`s at both payload boundaries are structural delimiters (all 5 samples open and close with a lone 0x00 adjacent to silence-floor audio — not a plausible recording artifact). The census's JUBEL duration ("10,146 samples ≈ 0.5 s") used an abandoned doubling hypothesis; the actual audio is 20,290 bytes = 0.99 s at the recommended rate. Both readings yield identical audio bytes; the decoder documents both (`--keep-delimiters`).

Decoder: `results/format-re/pvd-decoder/pvd_decode.py` (~260 lines, Python 3 stdlib only; commits `ac68585`, `e2f91350`) — validates magic/version/payload invariant, detects the delimiters and embedded RIFF, converts to 16-bit WAV; negative-tested (bad magic, truncation, length mismatch); validation JSON all-pass (`results/pvd-validation.json`).

**The sample rate stays ambiguous (candidates-not-claims)**. Byte 0x17 = 173 is constant 5/5. Ranked hypotheses: (1) **Amiga Paula audio period** — PAL clock 3,546,895/173 = 20,501.7 Hz (NTSC 3,579,545/173 = 20,685.0) — the recommended decoder default, winning on format-internal evidence; (2) **8 kHz** — argued against (no header byte points to it; spectral support runs to Nyquist with no telephony-style anti-alias cutoff); (3) **11,025 Hz stereo** — identified as a *trap*: BOMB.PVD embeds a consistent 11025 Hz stereo WAVE header declaring 2.11 s but carries only 7,689 PCM bytes — a truncated WAV import, not the format speaking (BOMB+DIA de-interleave as L≈R stereo, correlation 0.999, while the other three are native mono). No listening test was possible in-session; the clips are broadband German BBS UI sound effects, so content statistics cannot arbitrate. Every alternative is reproducible via `--rate`/`--ntsc`/`--mode embedded`. A second honest negative is documented, not fixed: BOMB's declared-vs-present size mismatch (46,636/46,600 declared vs 7,689 present).

### 4.3 Instant Graphics and Sound (R-4 — first public structural write-up)

Container: plain text, CRLF; command lines `G#`-prefixed in most samples (CLRDEMO.IGS and the TYPE*.IGS set carry unprefixed commands — an older protocol revision with identical grammar). **Command grammar cracked**: `letter>args` records separated by `:`; trailing `_` = wrapped continuation; `@` terminates `W>` text payloads — matching every stream segment across all 12 samples.

**Coordinate space cracked by arithmetic: Atari ST 640×200** — max x = 639, max y = 199 across the corpus, **0 violations in 1,293 numeric args** decoder-checked. **.IG vs .IGS cracked by pair diff**: XNET_LST.IG and XNET_LST.IGS have byte-identical command streams (1,432 commands each); .IG = message capture with a 9-line BBS header prepended, .IGS = bare protocol stream. Real strings extracted ("The LONDON SMOG BBS", "IG SUPPORT BOARD"), and TYPE3.IGS self-identifies: "Instant Graphics! Online Interpreter / Version 2.15 / VDI Graphics, Sound Effects and Music" — confirming Atari GEM VDI primitives (L/B/D/W/C already match VDI drawing ops).

Validation 12/12 (`igs-validation.json`, commit `66d6b0c`); SVG proof-of-decode regenerable via `--svg` (run on SHUT_MED.IGS: 780 line elements, none outside the viewport; artifact not committed).

**Partials (honest)**: `n>` music note events mapped to ranges (DEVO3.IG: 144 events, pitch 38–96, MIDI range) but timing unresolved; `fifth.igm`'s binary stream fingerprinted (statuses 0x90–0x94, pitches 36–79) with grammar unresolved; the `&>` macro grammar unresolved; ~14 of 25 observed command letters have unverified semantics.

### 4.4 Professional Draw (R-6 — clip container resolved 8/8)

**Clip container (`PDPF`), 8/8 samples byte-exact**: ASCII `PDPF` + u32be total size — exact match with file size in 8/8 (7774, 70228, 228346, 18466, 80296, 82756, 1238, 3338); flat IFF-style chunks (4CC + u32be, no padding) parsing with **100% byte coverage and zero anomalies** (35–7,658 chunks/file, 19–22 chunk types). Zero-length marker chunks bracket sections: `COLR…CFIN` (color table: `CNAM` + `SRGB` u16be at 0x0F=1.0 scale + `PYMC`/`YMCK` + `CFLG` + `CSCR`), `CLIP…OFIN`, file-final `CLFN`; objects `BEZ4`/`CIRC` with `VBOX`/`DBOX`/`OFLG`/`LINE`/`FILL`/`DATA`/`OEND`.

Decode is *semantic*, not just structural: clip names extracted prove it — Birds = "Finch"; Christmas = 11 clips ("Wreath", "Bells", "NorthPole", …); Logo.clips = official CDTV logo art at sizes _30/_7/_5.5/_3.5; MUS/PER/REF symbol libraries ("MUS_1"…, with MUS_1→MUS_10 a 10.04× linear scale); "TennisBall"/"TennisCourt".

**The .pdraw document variant is a different container** (confirms dexvert's own hunch): header `08 08 09 0F` + "Professional Draw V3.03" + four u32be invariants (3000, 198, 72, 102 — meaning unresolved; 72 suggests DPI); `PENV`/`PDOC`/`PPAG`/`PBOX`/`PSGR` chunks walk cleanly, then the page body resists (honest partial). Validation: `pdclips-validation.json` — 8/8 .clips byte-exact, 2/2 .pdraw headers + top chunks.

**Partials**: BEZ4 `DATA` point grammar (byte pairs span the full u16 range — normalized coordinates, grammar unresolved); VBOX unit (16.16 fixed-point hypothesis, unverified against a known page size); the 18-byte `STXT` record; no renderer.

### 4.5 Clarion .DAT (R-3 — corpus validation + 4 spec corrections)

Corpus: 49 files (46 .dat + 3 .fil) from the mirror; 43 parse clean, 6 sfatr-encrypted. The published (clarionlife.net) layout validated by **three exact arithmetic identities, 43/43 with zero exceptions**: descriptor-end == data-area offset; `offset == 0x55 + 27·numflds + key/picture/array extras`; **`filesize == offset + numrecs·reclen`**. The third identity establishes slot semantics the published docs lack: numrecs is the highest record number ever allocated (= physical slot count); deleted slots are reclaimed in place (sfatr bit 5 in 42/43 — APPOINTS.DAT the exception), so the naive `(numrecs+numdels)·reclen` formula fails exactly on the 4 files with numdels>0.

**Four corrections/extensions to the published spec**: (1) rhd bits are **bit numbers** — 0x10 = deleted (present in exactly the deleted slots of the 4 numdels>0 files), 0x04 = revised; (2) picture descriptors are **2+piclen bytes, not 2+256** (fixed-size parsing overshoots the data area by 204–468 bytes in 7 files; piclen-sized parsing is exact 43/43); (3) arrays with numdim==0 still carry one ARRPART (4 bytes); (4) **logbof/logeof are record numbers, not byte offsets**. Plus: .FIL files are the same format.

Record decode is content-validated: BBRAND → bullet brands (Penn/Hornady/Speer/Sierra), CRDTCARD → Visa/Hess's/Amoco, APPOINTS → LONG dates ≈ 1990 matching header dates; DECIMAL = packed BCD (decsig = digit count). Stdlib decoder (`clarion_dat_decode.py`, commits `b76a5ee`, `b41c85f`, `df7842e`) validates 240 records.

## 5. The technical centerpiece: the Clarion encryption crack (F-39)

Six of 49 files set sfatr bits 1|2 ("owned"+"encrypted"): DEFAULT, GENESOFT, GEORGEA, GEORGEE, GEORGEX, HHCNTRL. Bytes from 0x04 onward are key-scrambled (sig `43 33` + sfatr stay clear). F-38 cracked 2/6 headers (GENESOFT `d3c6`, GEORGEA `3e3a`) and reported the remaining four as "fail all ≤2-byte repeating keys under the section-reset model — longer keystreams". **F-39 (commit `c77d231`) refuted that negative claim by exhaustive search** and extended the crack from headers to record bodies.

### 5.1 The attack: arithmetic-identity scoring over an exhaustive keyspace

For each file, all **65,536 two-byte keys** were applied to the 81-byte encrypted header region (0x04–0x54) and scored on the arithmetic identities F-38 had validated on the plain corpus: reserved 4 bytes == 0 (**weight 12 — alone kills ~99.998% of keys**), `filesize == offset + numrecs·reclen` (weight 14), extras-window `0 ≤ offset − (0x55+27·numflds) ≤ key/pic/arr budget` (weight 8), field-count/reclen/logeof/logbof/freerec/chgtime/chgdate ranges, printable name fields. Result: **exactly one fully-valid key per file (63/63 checks)**. Calibration: the same search reproduces F-38's two known keys *uniquely* (GENESOFT→d3c6, GEORGEA→3e3a) — the scorer is calibrated, not over-fit. One scoring iteration was needed: DEFAULT has numflds=98, above the initial 64 cap informed by the plain corpus (1–38); relaxed to 128, the filesize identity holds exactly (2731 = 85 + 27·98; 2731 + 1·306 = 3037).

| file | sfatr | key (k0 k1) | F-38 status | what it is |
|---|---|---|---|---|
| DEFAULT.DAT | 0x66 | **d8 c6** | not cracked | 98-field app defaults/timeclock table |
| GENESOFT.DAT | 0xe6 | d3 c6 | cracked (F-38) | password table, 12 STRING fields |
| GEORGEA.DAT | 0x86 | 3e 3a | cracked (F-38) | author card "George Tanner / GEORGE'S JOURNAL" |
| GEORGEE.DAT | 0xa6 | **3e 3a** | not cracked | journal entry index, 29 slots / 12 live |
| GEORGEX.DAT | 0xa6 | **3e 3a** | not cracked | journal entry text, 38 slots |
| HHCNTRL.DAT | 0x26 | **50 56** | not cracked | Torbert Data Systems control record |

### 5.2 The mechanism, end-to-end

- **Cipher**: 2-byte repeating XOR with a per-file key (k0, k1) — even keystream index XORs k0, odd XORs k1.
- **Phase reset at every section boundary**: header body at 0x04; each 27-byte field descriptor at 0x55+27i; each 19-byte KEYSECT; each 6-byte KEYPART; each picture/array section. F-38 observed this for header+descriptors; F-39 confirmed it for all sections.
- **Record slots (new — closes F-38's open question)**: the 5-byte slot header (rhd u8, rptr u32) is stored **clear**; the body is XORed with the same per-file key, phase reset at body start. Evidence: all six files' slot headers read rhd 0x01/0x05 (live) or 0x11/0x15 (deleted) — exactly the plain-corpus rhd value set {1,2,5,17,18,21,22} — and bodies decode to ASCII/BCD/binary per their field descriptors.
- **KEYSECT/KEYPART layout decoded** (validated on plain BBRAND.DAT raw bytes + all four encrypted key sections): `KEYSECT(19) = ncomp u8, name[16], ktype u8, klen u8`; `KEYPART(6) = ftype u8, fldno u8, rfu u8, foffset u16 LE, flen u8`. This also corrects F-38's census, which parsed key names from offset 0 — names start at byte 1; byte 0 is the component count.

### 5.3 Recovered content (decoded facts only; no ciphertext committed)

- **George Tanner's 1991 journal** — GEORGEA: "George Tanner", "123 Main Street", "Anywhere, USA", "GEORGE'S JOURNAL", empty password. GEORGEE: 29 slots, 17 deleted (== numdels), 12 live entries from "NEW YEAR'S DAY" (1991-01-01) to "SPRING BEGINS" (1991-03-21, the equinox). GEORGEX: 38 slots of journal text linked by entry number (entry 7 "CAMPING TRIP" has 4 parts: "We went on a camping trip on Friday night…", "…scary stories…", "…tarzan-swing type vine…").
- **GENESOFT password table** — GEN:PASSWORDS = `psdjxczny`; companions incl. `qawsedrft` (keyboard-walk) and GEN:DKAPMBHSL = `shareware`.
- **DEFAULT timeclock defaults** — OVERRIDE=Y, PWDEXIT=Y, LUNCH=60.0 min, MAXHOUR=7.0, a MO–FR schedule with INTIME 2880001 cs = 08:00:00.01, OUTIME 6120001 = 17:00:00.01.
- **HHCNTRL control record** — serial `S10000004`, "Copyright 1990 Torbert Data Systems, INC.", per-screen access words Police/Fire/Ambulance/Doctor/Pediatrician/Poison with BCD phone numbers — POLICE/FIRE/AMBULANCE = …091 = **911**.

Cross-validations: GEORGEE's rptr free-list chain from freerec visits exactly its 17 deleted slots (first free-list proof on encrypted data); HHCNTRL's BCD 911 sits under PWORD="Police".

**Date-epoch pin (sharpens F-38)**: F-38 said chgdate is "days, epoch 1801 (+3 day skew)". The exact epoch is **1800-12-28** — the documented Clarion "standard date" — verified two independent ways: 69236 → 1990-07-21 matches the plain-corpus anchor (CRDTCARD), and the decrypted GEORGEE entries land on semantically correct weekdays (all three CHURCH* entries on Sundays; MOW THE LAWN DAY / CAMPING TRIP on Saturdays; BACK TO WORK on Wed 1991-01-02, the day after the holiday).

### 5.4 Why this generalizes

The recipe is format-agnostic and applies to any 1980s/90s-era scheme of the same family (2-byte periodic XOR with per-file keys — and inductively to n-byte schemes, where the keyspace is still trivially small):

1. **Detect** by periodicity, not entropy: a 2-byte XOR preserves byte-period structure, so encrypted files show only 4.3–5.2 bits/byte whole-file entropy vs 0.96–4.49 for plain — entropy alone would not flag them, periodicity analysis does.
2. **Mine arithmetic identities from the plain corpus** (the same identities that validate the format also validate a key candidate).
3. **Score every candidate key**, weighting constraints that are near-impossible to satisfy by chance (reserved==0 eliminates ~99.998% alone).
4. **Calibrate the scorer** by regressing on known keys — exactly-one-survivor is the acceptance criterion.
5. **Recover**: one ~instant brute force per file, forever. The password→key derivation question becomes moot for data recovery.

### 5.5 Honest negatives (encryption-specific)

- **reserved2 (0x53–0x54) anomaly**: under the correct keys these 2 bytes decrypt non-zero in all 6 encrypted files (9bd1, 2cd9, 2337, 5d39, 6a39, 9557) while both reserved fields are zero in all 43 plain files; no simple checksum matched. Unknown per-file marker or writer garbage — does not affect the crack.
- **KEYSECT klen byte**: 22/58/81 on GEORGEE/GEORGEX/HHCNTRL — not the component-length sums (40/4/1); plain BBRAND's 15 does match. Semantics unresolved.
- **Password→key derivation unknown** (per-file; the GEORGE* trio shares `3e3a`). Moot for recovery (§5.4) but open.
- Trailing-byte quirks characterized, not papered over: DEFAULT's final byte is a literal unencrypted 0x00 outside the keystream; GEORGEX TEXT fields carry 0xFF end-of-text markers; GENESOFT's last string ends 0xF3.
- F-39's attack tooling was throwaway (/tmp; the method is recorded in the committed `clarion-encryption-keys.json`) — reproducible, but not a turnkey tool.

## 6. Negative results and limitations (per format and campaign-level)

- **Sony DVF/MSV**: LPEC/TRC bitstream undecoded (the prize); frame geometry and 0x50 TOC open; 4 files only.
- **PVD**: sample rate unresolved-by-listening — broadband effects defeat content statistics (99.5%-energy point 0.29–0.49 cycles/sample at any hypothesized rate); BOMB declared-vs-present size mismatch documented, not silently fixed; a private unpublished decoder cannot be ruled out.
- **IGS**: .igm event grammar, `&>` macro, ~14/25 command letters unresolved; no sound renderer.
- **Professional Draw**: BEZ4 DATA point grammar, VBOX unit, STXT record, .pdraw page body unresolved; no renderer.
- **Clarion**: .K?? key files absent from the mirror (layout unexercised); comptype bits not decoded; rptr memo-pointer semantics inferred, not proven against a .MEM file; dexvert's string-magic signature generation unrepresented (all 49 samples are 0x3343).
- **Campaign-level**: novelty for R-3..R-12 rode on dexvert notes as proxy pending Rule-0 verify — and R-3's verification *refuted its own premise*; the PVD and IGS/PD checks held. Queue rows R-5..R-12 (Psion AIK, Sonic Arranger, NTitler, DiamondWare DWM, ANSI Music, Beam SIFF, CMS Intelligent Organ) remain untouched; R-1's codec is open.

## 7. Implications

1. **Preservation bodies gain working decoders today**: .pvd → WAV (first public path to ProLine BBS voicemail audio); .igs/.ig → tokenized streams + regenerable SVG proof-of-decode; .clips → palette/clip/object extraction with names; Clarion .DAT → full record decode with one-instant key recovery for the encrypted subset. All stdlib Python; no sample bytes committed anywhere; every WAV/SVG/record regenerable from public mirrors via the committed decoders.
2. **The scored queue survives contact with reality and remains the roadmap**: R-5..R-12 plus the two in-format prizes (LPEC bitstream, .igm music grammar). The queue's honest labeling ("verify before claim") is what made the R-3 refutation a recorded correction instead of a retraction.
3. **The arithmetic-identity brute force (§5) is the campaign's most transferable artifact** — a decision procedure for short-period-XOR schemes with self-describing headers, calibrated and regression-checked.
4. **Corrections are the credibility mechanism**: F-34→F-35 byte offsets, F-38→F-39 keystream claim + epoch + KEYPART parse, the R-3 premise refutation, the PRONOM regex miss, and dexvert's two refuted doubts are all visible in the record (Appendix B). Every claim carries its check date so future prior art can invalidate it precisely.

## 8. Reproduction

All sources in **adineo-cmd/open-discovery-lab** (branch main), the campaign's evidence repo:

| Artifact | Path | Commit(s) |
|---|---|---|
| F-34 scored queue + first looks | `track-c-discovery-engine/results/format-re-v2.md`; raw censuses `results/format-re/{sony-msv-dvf,proline-pvd}-census.json` | `5c22031` |
| F-35 PVD spec / decoder / validation | `track-c-discovery-engine/docs/proline-pvd-format.md`; `results/format-re/pvd-decoder/pvd_decode.py`; `results/pvd-validation.json` | `ac68585`, `e2f91350` |
| F-37a IGS census / decoder / validation | `track-c-discovery-engine/docs/igs-format-census.md`; `results/format-re/igs-census/` | `66d6b0c` |
| F-37b Professional Draw census / decoder / validation | `track-c-discovery-engine/docs/professional-draw-format-census.md`; `results/format-re/professional-draw-census/` | `99d24de`, `7354710` |
| F-38 Clarion census / spec / decoder | `track-c-discovery-engine/docs/clarion-dat-format.md`; `results/format-re/clarion-dat/` (`clarion-dat-census.json`, `clarion_dat_decode.py`) | `b76a5ee`, `b41c85f`, `df7842e` |
| F-39 encryption crack | `results/format-re/clarion-dat/clarion-encryption-attack.md`, `clarion-encryption-keys.json` | `c77d231` |
| Prior-art audit (method-level) | `results/prior-art-audit.md` | `a8cc9d7` |

Instruments: dexvert @ `b126fe4`; `sembiance.com/fileFormatSamples/{audio/prolineVoice,image/instantGraphicsAndSound,image/professionalDraw,document/clarionDatabase,document/clarionMemo}`; Python 3.12.3 (numpy 2.5.4 validation-side only). Candidate-not-claims markers carried forward: PVD sample rate; IGS music semantics; PD VBOX unit; Clarion reserved2/klen bytes.

## Appendix A: finding-to-commit map (adineo-cmd/open-discovery-lab, branch main)

| Finding | Content | Commit(s) |
|---|---|---|
| F-3 (2026-11-09) | zero-doc + obtainable-samples queue premise (Track C founding; unique-confirmed by the audit) | track-c-discovery-engine/targets.md; audit `a8cc9d7` |
| F-34 | 12-format scored queue; Sony DVF/MSV census (bitrate relation); PVD header crack | `5c22031` |
| F-35 | PVD decoded: first public decoder + spec; F-34 offsets corrected; validation all-pass | `ac68585`, `e2f91350` |
| F-37 | IGS cracked (12/12) + Professional Draw clip container resolved (8/8) | `66d6b0c`, `99d24de`, `7354710` |
| F-38 | Clarion corpus validation (43/43 identities), 4 spec corrections, 2/6 encryption crack, R-3 premise refuted | `b76a5ee`, `b41c85f`, `df7842e` |
| F-39 | Clarion encryption complete: 6/6 cracked, bodies recovered, epoch pinned 1800-12-28 | `c77d231` |
| audit | prior-art audit (F-1..F-26; F-3 method-level unique-confirmed; zrax dangling citation flagged) | `a8cc9d7` |

(F-36 is Track A — MT6785 md1dsp — and is not part of this campaign despite its number falling between F-35 and F-37.)

## Appendix B: inconsistencies found during synthesis (recorded per the lab's Rule 1 — reported, not silently fixed)

1. **PVD artifact placement.** `results/format-re/pvd-decoder/` contains only `pvd_decode.py` (13,174 B). The spec doc lives at `docs/proline-pvd-format.md` and the validation JSON at `results/pvd-validation.json` — neither inside `pvd-decoder/`, although a reader assembling F-35's evidence column might expect them there. The paths inside the F-35 documents themselves are accurate.
2. **PVD sample-count drift.** F-34's queue row says R-2 has "8 samples"; the mirror holds exactly 5 (DIA, KMERA, BOMB, GELD, JUBEL) and every analysis used 5. F-34's own method line says 9 samples fetched total (5 PVD + 4 DVF/MSV). The "8" is unexplained by any source.
3. **F-34 → F-35 byte-offset correction** (self-correction, kept visible in §4.2): the census's 0x17 u16 reading and body-at-0x19 placement are superseded; likewise JUBEL's duration (10,146 samples/0.5 s under the abandoned doubling hypothesis → 20,290 bytes/0.99 s).
4. **F-38 → F-39 refutations and sharpenings** (all visible in §5): the "4/6 need keystreams > 2 bytes" negative claim is refuted by exhaustive search; the "epoch 1801 (+3 day skew)" chgdate reading is pinned to 1800-12-28; F-38's KEYPART name-offset parse is corrected (byte 0 = component count).
5. **Clarion signature generations.** dexvert detects the "Clarion 2 DataBase for DOS" magic string, which appears in none of the 49 samples (all binary `0x3343`); F-38 documents this, but it means the corpus validates only one of two signature generations.
6. **Per-file sfatr completeness.** F-38's doc gives explicit sfatr values only for DEFAULT (0x66), GEORGEE/GEORGEX (0xa6), HHCNTRL (0x26); GENESOFT (0xe6) and GEORGEA (0x86) appear only in F-39's JSON. A fill-in, not a conflict — but the per-file sfatr set is complete only in F-39's artifact.
7. **Audit's zrax false-negative (method-level).** The 2026-11-11 prior-art audit could not locate zrax's "socboot2", cited by Track A's F-18 — flagged as a dangling-reference risk (audit item P7). Not part of this campaign, but it is the concrete failure mode behind this campaign's rule that every prior-art check records its exact queries and dates.
8. **Ledger status.** FINDINGS.md rows F-34..F-39 are marked `verified`; this note is their `published` step.
