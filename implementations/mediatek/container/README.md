# implementations/mediatek/container — clean-room mtk_hdr + GFH record-chain parser

A verification-first parser/walker for the two MediaTek firmware container
formats the lab has documented byte-for-byte on production images
(Xiaomi Redmi Note 10S "rosemary", MT6785, LineageOS 24.0 — see
`mediatek/rosemary-census.md`, section "Container formats"):

1. **mtk_hdr signed record chain** — magic `0x58881688` @0x00, payload size
   @0x04, NUL-padded ASCII name @0x08 (>=20 bytes on MT6785), extension
   record `0x58891689` @0x30 (header size 0x200 @0x34, payload alignment
   0x10 @0x44), next record at `align(payload_end)`; per-payload signature
   pairs `cert1` (1,709 B) + `cert2` (957 B), both DER (`30 82 …`)
   X.509 sequences.
2. **GFH `MMM` record chain** — `gfh_common_header` (magic `"MMM"`,
   version 1, size u16, type u16), types {0 FILE_INFO, 1 BL_INFO,
   2 ANTI_CLONE, 3 BL_SEC_KEY, 7 BROM_CFG, 8 BROM_SEC_CFG} per U-Boot
   `tools/mtk_image.h` (the census confirms rosemary matches U-Boot's
   structs exactly), plus md1dsp's type **260 (0x104)** which is beyond
   U-Boot's enum (F-36).

Every source file carries the clean-room statement header (written from the
published spec documents on 2026-11-16; no proprietary material accessed).

## Files

| file | role |
|---|---|
| `mtk_container.py` | parser/verifier + JSON emitter + CLI (`python3 -I mtk_container.py <file> [--json out.json] [--hash]`) |
| `make_fixture.py` | deterministic synthetic-fixture generator (self-made bytes exercising the documented layout; regenerates `fixtures/`) |
| `fixtures/*.bin` | generated synthetic fixtures (mtk_hdr signed chain, GFH preloader chain, GFH md1dsp chain) — regenerable byte-exactly; the repo `.gitignore` excludes `*.bin`, so these are working-tree artifacts: run `python3 -I make_fixture.py` to recreate, the test suite verifies regeneration matches |
| `test_mtk_container.py` | unittest suite: `python3 -m unittest -v test_mtk_container` |

## What the verifier checks

- record bounds at every step; payload truncation is reported, never
  silently zero-filled (the lab's extraction walker `mediatek/tools/
  payload_walk.py` truncates silently and caps at 64 records — this
  component is the verifying counterpart);
- extension-record fields (`0x34` header size, `0x38`/`0x3C` verbatim,
  `0x44` alignment) and power-of-two alignment;
- chain stride progress (next record = `align(payload_end, align)`);
- GFH record sizes/types, with per-type field decode only where the
  public struct layout pins fields; everything else stays opaque
  (facts-not-blobs);
- signature-block classification: cert1/cert2 by DER shape + the
  documented rosemary pair sizes; per-record `signed-by-cert-pair` /
  `none` flags reproducing the census's signed/unsigned payload split;
- diagnostics in `verification` (`bad-magic`, `truncated-payload`,
  `bad-alignment`, `non-advancing-chain`) with exit status 1.

## Scope boundary (honest)

RSA verification of the cert1/cert2 chain is **out of scope here** —
public tooling already does it (prior art, below). This component detects
and tabulates the signature records; it does not validate the crypto.

## RULE 0 prior-art check (2026-11-16, recorded queries)

Before building, the following checks were run; no existing tool combines
chain verification + GFH-record decode (incl. type 260) + signature-block
classification + JSON emission + tests:

- Web search `"0x58881688" OR "58881688" MediaTek mtk_hdr parser record
  chain` → U-Boot `tools/mtk_image.h` documents the magic (`LK_PART_MAGIC`)
  for boot-image *generation/detection* only; no firmware-partition record
  walker.
- GitHub code search `"58881688" language:python` (147 hits) → closest:
  [R0rt1z2/kaeru `utils/dump.py`](https://github.com/R0rt1z2/kaeru) walks
  the chain and prints text (no verification beyond magic, no certs, no
  GFH, no JSON, no tests);
  [Maikyxd/val-protocol `tools/verify_mtk_image.py`](https://github.com/Maikyxd/val-protocol)
  walks the chain and fully verifies cert1/cert2 via RSA-PSS + hash
  comparison (text output; no GFH MMM records; no JSON; no tests);
  [blackeangel/md1img_repacker](https://github.com/blackeangel/md1img_repacker)
  (repacking); remaining hits are logo/bootimg tooling.
- GitHub code search `"58891689"` (103 hits) → same families plus
  [19h/zrax-isa-workbench `docs/socboot2.md`](https://github.com/19h/zrax-isa-workbench)
  (the empirical layout doc; synthetic fixtures only — the rosemary census
  is the production-image confirmation); `NatleoJ/MediaTek` raw fetch
  404'd on `main` (unresolved branch — recorded as a check gap).
- GitHub code search `gfh "0x104"` → **0 hits**: no public tool names
  md1dsp's GFH type 260. The lab census (F-36, 2026-11-13) remains the
  only public documentation of that record type.
- Lab-internal: `mediatek/tools/payload_walk.py` (committed) is the
  extraction walker this component generalizes and hardens.

## Fixtures note

No MediaTek firmware exists on this machine (checked 2026-11-16: no
`rosemary`/`md1rom`/`preloader` images anywhere in the home tree), so per
the workorder the fixtures are **synthetic, self-made bytes** generated by
`make_fixture.py` from the documented field layout alone. They prove the
parser against the documented layout, not against real firmware; the
parser has also been written so a real rosemary partition image can be
dropped in (`python3 -I mtk_container.py md1img.img --json out.json`).
