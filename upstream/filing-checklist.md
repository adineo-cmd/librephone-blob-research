# Filing checklist — LibrePhone upstream PRs

Companion to [README.md](README.md), which holds the full paste-ready PR
descriptions and doc texts. Upstream repo:
https://codeberg.org/rsavoye/librephone (Gitea/Forgejo — "New Pull
Request" from the fork, base branch `main`).

## Prerequisites (owner actions)

- [ ] **Log in to codeberg.org** — the lab holds no Codeberg credentials;
      every PR below is filed manually from a logged-in browser.
- [ ] Fork `rsavoye/librephone` under the filing account.
- [ ] **Reconcile against live upstream docs at filing time.** The
      "current upstream text" quotes in README.md were fetched
      2026-11-12 (`wireless.md`, `wpss.b06/07/08/09/10/12.md`, `files.md`).
      If upstream changed since, re-diff and adjust the patch text.
- [ ] Optional: mention the #librephone IRC channel in the PRs for
      follow-up (per the original draft's submission checklist).

## Submission order

| # | PR title | Branch | Target file(s) | Commit title | Depends on |
|---|---|---|---|---|---|
| PR-1 | docs/wireless.md: replace the AVR guess with the verified RISC-V identification | `docs/wpss-riscv-architecture` | `docs/wireless.md` | Fix wireless.md processor description | none |
| PR-2 | add docs/wmi-dispatch.md: the wpss WMI dispatch architecture (registry + Hexagon dispatchers), decoded | `docs/wmi-dispatch` | `docs/wmi-dispatch.md` (new) | Add docs/wmi-dispatch.md | none |
| PR-3 | correct the per-segment wpss docs (b06/b07/b08/b09/b10; b12 cross-check) | `docs/wpss-segments` | `docs/wpss.b06.md`, `docs/wpss.b07.md`, `docs/wpss.b08.md`, `docs/wpss.b09.md`, `docs/wpss.b10.md`, `docs/wpss.b12.md` | Correct the per-segment wpss docs | file after PR-2 (b06/b09 text links to `docs/wmi-dispatch.md`) |
| PR-4 | docs/files.md: bluetooth partition firmware and boot-chain image facts | `docs/files-bt-bootchain` | `docs/files.md` | Document the bluetooth partition and boot-chain images | none (optional; last) |

## Per-PR one-liners (full text in README.md)

- **PR-1** — one-paragraph fix: wireless.md's "8 bit ATMel AVR" guess is
  replaced by the verified RV32 identification (e_machine=243, entry
  0x404000 machine-mode startup, QURT strings, `dog_hal_moselle_riscv.c`)
  plus the junk-.bXX-header caveat.
- **PR-2** — new per-segment-facts doc: b09 registry
  (`[ptr, grp<<12|cmdID, 0]`, 12-byte stride, 225 records / 149 IDs,
  anchor 0xc0691080), b06 Hexagon dispatchers (PDEV 0xc02cd9cc decoded;
  jump tables 0xc056423c / 0xc05641fc; 61 events mapped), registry-head
  tie-in, open items. Corrects the ISA assumptions of the per-segment
  docs (b06 is Hexagon, not "unknown").
- **PR-3** — six files: b06 rewritten (Hexagon code, not data), b09
  rewritten (the registry, not a PSX image), b07/b08/b10 updates
  appended, b12 cross-check appended (CC-BY-SA-4.0 doc — append only).
- **PR-4** — files.md: bluetooth.img FAT16 facts (Moselle 1.1/1.2 + EVROS
  product_id 29, ARM Thumb rampatches, rom_build→filename math,
  linux-firmware gaps) + boot-chain block (xbl multi-ELF container;
  shrm/aop/cpucp RV32; Fairphone OEM signing chain).

## Filing mechanics (Forgejo)

1. On the fork: create the branch from `main` (names in the table).
2. Apply the doc text from README.md (commit titles in the table;
   one commit per PR keeps review simple).
3. Open the PR against `rsavoye/librephone` `main`; paste the PR
   description block from README.md.
4. PR-3 note: if PR-2 has not merged yet, keep its link line
   (`docs/wmi-dispatch.md`) — Forgejo links resolve once PR-2 merges;
   mention "follow-up to the docs/wmi-dispatch.md PR" in the PR-3
   description's first line if filing out of order.

## Content rules observed by this package

- Facts only: every number traces to a committed lab finding
  (`papers/wmi-dispatch-architecture.md` Appendix A commit map).
- No blob content redistributed; addresses/structures/strings only.
- No new speculation in upstream-facing text; open items are marked
  unresolved in the upstream doc itself (wmi-dispatch.md).
- Upstream voice: short factual notes matching their existing per-file
  docs; original observations are preserved and extended, not replaced.
