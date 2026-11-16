# WORKORDER-001 — DESKTOP machine work order (LibrePhone 100 GB program)

**Issued by:** Open Discovery Lab (agent session, 2026-11-16)
**For:** the owner's DESKTOP PC (this machine has the disk space, RAM,
bandwidth, and desktop OS that the lab box lacks)
**Status channel:** when a task below is finished, put your result files
in `workorders/inbox/` (see the naming convention at the bottom) and tick
the checkbox. The lab agents poll this directory through the repo.

---

## Ground rules (read once, apply always)

1. **FACTS, NOT BLOBS.** Nothing proprietary is ever committed to the
   repository: no .bin/.mbn/.dll/.so payloads, no decompiled code dumps.
   What you commit or drop in `inbox/` is: inventories (name, size,
   sha256), extracted tables/constants, call graphs, your notes. When in
   doubt: hashes and listings are always fine; payload bytes never are.
2. **Work locally, report hashes.** Keep all extracted payloads in a
   local workspace (e.g. `D:\lpwork\` or `~/lpwork/`), never inside the
   repo clone.
3. **One work unit at a time**, in the order below. W1 unblocks
   everything else.
4. If a step fails, write what happened into
   `workorders/inbox/STATUS-<WO>.md` (commands + exact errors) — honest
   failures are deliverables; the lab adapts the plan around them.

---

## W1 — Download the LibrePhone firmware database (~100 GB)

- [ ] **W1.1** Locate the database manifest. The lab's recon
      (`upstream-contribution/blob-database/recon.md` — pull latest from
      this repo) records where the ~100 GB corpus lives. Known candidate
      endpoints to check first:
      - https://codeberg.org/rsavoye/librephone (data/ tree — look for
        .torrent/.magnet/meta4 files or per-device archives)
      - https://librephone.fsf.org (follow every download link)
      - archive.org advanced search: `q=librephone`, and any items linked
        from the FSF pages.
- [ ] **W1.2** Download the full payload. Torrent preferred (resumable,
      verifiable); otherwise `curl -C - -o out.bin <url>` in a retry
      loop, or `aria2c -x8 -s8 <url>` if you have it. Verify every file
      against the manifest hashes (or compute them if the manifest lacks
      them — that computation is itself part of the deliverable).
- [ ] **W1.3** Write `workorders/inbox/W1-manifest.csv`:
      `device,path_in_archive,bytes,sha256` — one row per file. This is
      the file that unblocks W2 and the lab's coverage matrix.

## W2 — Per-device firmware extraction

- [ ] **W2.1** For each device package in the W1 payload: unpack the
      update/ROM containers (usual Android chain: `payload.bin` →
      `payload-dumper-go`; raw .img → `simg2img` then standard
      partitions; .ozip → ozip-decrypt; Spreadtrum .pac → SPD Research
      Tool dump; MTK scatter → `mtk_extract`/pgpt). Tools the lab
      verified: python `payload_dumper`, `simg2img`, `7z` for most
      archives.
- [ ] **W2.2** Produce per-device blob trees, grouped by family:
      `modem/ wifi/ bt/ tz/ boot/ adsp/ cdsp/ camera/ gpu/ other/`
      (map by path + partition name; when ambiguous, put under `other/`
      with a note).
- [ ] **W2.3** Write `workorders/inbox/W2-blobs.csv`:
      `device,family,filename,bytes,sha256` — one row per blob. THIS IS
      THE MASTER INPUT for the lab's coverage matrix. Size expectation:
      ~444 devices × ~10-60 blobs each.
- [ ] **W2.4** Flag every device whose extraction fails in
      `workorders/inbox/W2-failures.md`.

## W3 — Ghidra headless bulk analysis (P1 blobs only)

- [ ] **W3.1** Install Ghidra (latest release, needs Java 21+) and
      confirm `analyzeHeadless` runs.
- [ ] **W3.2** Run headless analysis on the **P1 blobs only** (the lab's
      priority list: FP6 families — wpss b01/b02/b03/b04/b06/b07/b08,
      modem, adsp, cdsp, camera icp, bt, trustzone — and MT6785: md1rom,
      md1dsp, ccu, tinysys; the full per-file list is in
      `qualcomm-fp6/docs/*.md` + `mediatek/docs/*.md` in this repo).
      Command shape:
      `analyzeHeadless <proj> <proj> -import <blob> -analysisTimeoutPerFile 3600`
- [ ] **W3.3** Export per-blob ANALYSIS FACTS ONLY (script Ghidra's
      post-analysis): function list with addresses/sizes, discovered
      strings tables, per-function call targets, and section tables.
      Write `workorders/inbox/W3-ghidra/<device>_<family>.facts.json`.
- [ ] **W3.4** Do NOT export decompiled C or binaries into the repo.
      The lab agents reason over your facts files and request targeted
      follow-ups (specific functions) in the next workorder.

## W4 — Wine reference runs (LPEC/PCM — ROADMAP Q-2)

- [ ] **W4.1** Install Wine (64-bit prefix). Fetch the Sony Digital
      Voice Editor 3.3.01 installer — provenance documented in
      `qualcomm-fp6/../track-c docs lpec-dll-analysis.md` (archive.org
      item dve3301icdpx820; extract chain needs data1.cab AND data2.cab
      side by side — see F-68's correction in the lab journal).
- [ ] **W4.2** Run the DVE application under Wine; play/convert the two
      reference samples (budgtele.dvf, 07011600.MSV — from
      sembiance.com/fileFormatSamples/, hashes recorded in the F-68
      journal) to WAV via the app itself. Record the exact app actions.
- [ ] **W4.3** Drop the produced WAVs + a run log into
      `workorders/inbox/W4-wine/` (WAVs are DERIVED PCM from samples the
      lab already uses — they are analysis artifacts, allowed in inbox;
      if unsure, submit hashes + sizes and ask).
- The lab diffs this reference PCM against its LPEC decoder output —
  this closes ROADMAP Q-2 (reference-quality validation).

## W5 — Re-fetch trees that unblock the open library census (issue #33)

- [ ] **W5.1** Re-fetch the FP6 LineageOS build tree and the MT6785
      firmware tree (same sources as the lab's original sessions —
      LineageOS device trees + vendor dumps; see the provenance sections
      in `qualcomm-fp6/docs/fp6-architecture-census.md` and
      `mediatek/docs/`).
- [ ] **W5.2** Extract the 16 shared libraries named in issue #33
      (https://codeberg.org/rsavoye/librephone/issues/33) with
      sha256 + sizes.
- [ ] **W5.3** Run `strings -n 8` + `file` on the 7 unidentified ones
      (focal64, ic5, loadalgota64, ops, sp_license, winsecap, evautil64)
      and drop the outputs in `workorders/inbox/W5-libs/`. The lab's
      F-32 method then identifies them from your strings files.

---

## Inbox naming convention (how results come back)

```
workorders/inbox/
  W1-manifest.csv            W2-blobs.csv            W2-failures.md
  W3-ghidra/<facts>.json     W4-wine/<wavs+log>      W5-libs/<strings+hashes>
  STATUS-<WO>.md             (any failure/halt notes)
```

The lab processes inbox files, merges facts into the coverage matrix and
docs, and issues WORKORDER-002 for the next round. Nothing in inbox/ is
ever committed raw — the lab distills it to facts first.

---

## Why this split

| work | machine | reason |
|---|---|---|
| 100 GB download, extraction, Ghidra, Wine | **DESKTOP** | bandwidth, disk, RAM, desktop OS |
| coverage matrix, RE analysis, spec docs, solvers, upstream packaging, verification | **LAB BOX + AGENTS** | reasoning + compute + clean-room discipline |
