# lpec/frame-parser — packaged Sony DVF/MSV LPEC frame parser

Spec-derived provenance: this is the lab's published frame-level LPEC parser
(open-discovery-lab, track-c-discovery-engine,
`results/format-re/lpec-census/lpec_decoder.py`) packaged as a standalone
component, with the lab's spec docs as its design documents:

- [lpec-codec-analysis.md] F-47 — container/packet layer (1024-byte transport
  packets, 10-byte header, `bytes[4:6]` = payload-size field, TOC tag-4
  format), frame-size arithmetic per variant
- lpec-decode-pass2/pass3 — SP layout, pump semantics, and the resolved
  per-frame bit layout for both modes (LpecLp 8 kHz / 6 kbps, LpecSp
  16 kHz / 16 kbps): frame types {48,36,60} B (LP) / {128,96,160} B (SP),
  LSP groups 3x6 / 4x6 bits, gain 7 / 8 bits (+6-bit shape), pitch
  7+6+6 bits per subframe, derived pulse budget `floor((T-C)/2) - exc_cost - 19`

Validation (from the lab's pass3, reproduced by the same code):
budgtele.dvf → 50,545 frames, byte-exact closure, 0 invalid, implied
6000.1 bps; 07011600.MSV → 159 frames, byte-exact closure, 0 invalid,
implied 16000.0 bps; tail-pad signature {3, 9, 17} bits only.

Honest scope: NOT a PCM decoder. No synthesis (LSP expansion, excitation
page decode, LPC synthesis are inventoried in F-48, not wired up); the
per-subframe pulse payload is parsed as one block; intra-block split and
the DD/NN header counters remain open per pass3.

Clean-room statement: derived facts only, from the lab's published spec
docs; Sony binaries/decompiled code never committed, never redistributed.

RULE 0 (2026-11-16): `"lpec" audio codec reverse engineering lineage phone
qmi` — no public decoder exists; the Sony LPEC codec is unrelated to
Qualcomm/QMI voice paths.
