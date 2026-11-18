# hpnv20.bin — the h-generation (Hastings-class) QCA BT NVM, parsed

Companion to `hpbtfw20-analysis.md` (same session, same method). This file
documents the NVM side: tag census, layout change vs the F-75 cr/ap
generation, board-variant naming, and the cross-build content identity
that makes a free NVM generator tractable. No payload bytes committed —
payloads live in `/tmp/astro_v/payload/` and `/tmp/astro_v/btimg/`.

## 0. Prior art (RULE 0, 2026-11-18)

- The unumS22linux QCA6490 gate doc (cited in hpbtfw20-analysis.md §0)
  documents the QTI HAL's `UpdateHastingNvm` and the `hpnv21g.bab` board
  question but parses no NVM bytes.
- `qca_get_nvm_name_by_board` in mainline btqca.c (GPL) gives the naming
  rules; it is the *only* public source that touches the bXX/g names.
- linux-firmware ships the `hpnv21*`/`hpnv21g.*` families but **no
  hpnv20.bin** (checked 2026-11-18; the F-74-style absence for the
  h-20 NVM generation).
- No published tag map of any hpnv20 build exists (GitHub code search
  `q=hpnv20`, web search — queries logged in hpbtfw20-analysis.md §0).
  The tag tables below are the delta.

## 1. Provenance and md5 verification

| build | bytes | DB md5 | fetched md5 | status | source |
|---|---|---|---|---|---|
| common (9 laptop-half devices) | 6,319 | `5de36001f431a4d60c641d494a75bb60` | same | **MATCH** | cupid `bluetooth` partition image, `/image/hpnv20.bin` |
| hpnv20g.bin (8 laptop-half devices) | 6,329 | `12cd1ff0c316e02d0c6a6d8264184f0e` | same | **MATCH** | same partition, `/image/hpnv20g.bin` |
| FP5 build | 6,307 | `a90468d77f1202d912fb18d4e74a3e48` | — | [OPEN: no public source found] | FP5 stock vendor/bluetooth/image (LineageOS does not extract it) |
| Samsung r0s build | 6,203 | — (no DB row carries md5 `6631b312ca661d1a12c978082a859238`) | `6631b312ca661d1a12c978082a859238` | **NOT database-identical** (third build; structurally same generation) | TheMuppets/proprietary_vendor_samsung_r0s @ lineage-24.0 |
| hpnv21.bab / hpnv21g.bab (r0s) | 7,023 / 6,863 | — | `ed2759b4…` / `d7f39ed0…` | n/a (context) | same r0s repo |

All parses by the unmodified `implementations/qca-bt/qca_tlv.py` (exit 0)
plus `implementations/hbt-fleet/fleet_diff.py` (new).

## 2. Layout: the h-generation NVM is a bare type-2 record

cr/ap generation (F-75 §5): `[0,4) type-4 enclosing | [4,8) type-2 set
header | tags | type-3 trailing record (kernel-ignored)`.

h generation (all four h-NVMs parsed):

```
[0, 4)     type-2 set header {type=2, len = file−4}
[4, 4+len) tlv_type_nvm tags, 12-byte prefix each, perfectly packed
[4+len, file)  — nothing (zero trailing bytes, zero padding)
```

| file | tags | set consumed/declared | trailing |
|---|---|---|---|
| hpnv20.bin (DB) | 61 | 6,315/6,315 | 0 |
| hpnv20g.bin (DB) | 61 | 6,325/6,325 | 0 |
| hpnv20.bin (r0s) | 60 | 6,199/6,199 | 0 |
| hpnv21.bab (r0s) | 75 | 7,019/7,019 | 0 |
| hpnv21g.bab (r0s) | 73 | 6,859/6,859 | 0 |

The type-4 enclosing wrapper AND the type-3 trailing record of the cr/ap
generation are **gone** — a wholesale layout simplification. (The
mainline parser handles both layouts; its NVM scan emits no diagnostics
on either.)

## 3. hpnv20.bin (DB build) — full tag map

Offsets are file offsets; `sha1` is the first 12 hex of the tag BODY
(12-byte prefix excluded). "kernel-known" tags per btqca.h: 2 = BD_ADDR,
17 = HCI, 27 = DEEP_SLEEP. `qca_get_nvm_name_by_board` is the only other
kernel consumer context (board-id naming). Everything else is
chip-consumed [OPEN semantics].

| off | tag | len | sha1-12 | off | tag | len | sha1-12 |
|---|---|---|---|---|---|---|---|
| 4 | 2 BD_ADDR | 6 | a43ddfc409e4 | 3017 | 91 | 248 | 379abb56c244 |
| 22 | 8 | 8 | b9a3f0f4c216 | 3277 | 92 | 196 | a2a60f3f26d2 |
| 42 | 10 | 5 | 928852de071e | 3485 | 95 | 168 | 38f42e7937f4 |
| 59 | 17 HCI | 6 | 0b55c9b2deb3 | 3665 | 111 | 218 | 02f7e9d849c0 |
| 77 | 22 | 112 | 162c7ac7ca28 | 3895 | 112 | 218 | 02f7e9d849c0 |
| 201 | 27 DEEP_SLEEP | 9 | 8129d19acc85 | 4125 | 113 | 200 | d7643af7a8a7 |
| 222 | 28 | 20 | 6379f6605032 | 4337 | 114 | 52 | 137137536f88 |
| 254 | 31 | 2 | f3e84b722399 | 4401 | 116 | 38 | 582eeeb1b5ba |
| 268 | 32 | 2 | c5fb09de08e0 | 4451 | 150 | 30 | 0ebe4cbc65d6 |
| 282 | 35 | 120 | 381b0d3e3657 | 4493 | 151 | 24 | 9c99d89d586e |
| 414 | 36 | 48 | f36ec10972c3 | 4529 | 153 | 152 | 70732663d893 |
| 474 | 37 | 44 | bdfaa219b5b2 | 4693 | 154 | 252 | 41dd19c6d0ce |
| 530 | 38 | 140 | 4747f878a7b4 | 4957 | 155 | 16 | d08ab67e8d08 |
| 682 | 39 | 60 | 077a95c87e67 | 4985 | 161 | 124 | 248682eb3774 |
| 754 | 40 | 18 | b0c3b4a56bba | 5121 | 162 | 80 | e8fdc6b1e46c |
| 784 | 42 | 56 | 252acd404d16 | 5213 | 174 | 158 | ab0302ef3a51 |
| 852 | 43 | 234 | 0b420088f53b | 5383 | 176 | 68 | 044f26257eb3 |
| 1098 | 44 | 64 | 65069c9a9b9f | 5463 | 177 | 108 | 549200b906d3 |
| 1174 | 50 | 232 | 813b0fce3353 | 5583 | 178 | 132 | bc86c9a826f4 |
| 1418 | 51 | 236 | 3194faa6db6f | 5727 | 179 | 14 | 9d5406e47350 |
| 1666 | 57 | 56 | c5a9bfb252b0 | 5753 | 180 | 68 | cb2643af9754 |
| 1734 | 62 | 48 | b2c61ad4c260 | 5833 | 196 | 228 | e141f6b1e9e5 |
| 1794 | 64 | 244 | 376a051c8940 | 6073 | 197 | 176 | 851e7592051c |
| 2050 | 65 | 44 | ea2af7f7f328 | 6261 | 199 | 6 | 271d5073279b |
| 2106 | 72 | 65 | 6cd92a3cb73a | 6279 | 200 | 28 | d924046878b4 |
| 2183 | 73 | 5 | 30ca9a3b4c98 |  |  |  |  |
| 2200 | 78 | 2 | 528f35403f03 |  |  |  |  |
| 2214 | 79 | 107 | cb5f25454c49 |  |  |  |  |
| 2333 | 80 | 24 | 98da7f6b807c |  |  |  |  |
| 2369 | 83 | 8 | 6c1c41f5396a |  |  |  |  |
| 2389 | 84 | 112 | 86487110fbb8 |  |  |  |  |
| 2513 | 85 | 116 | 27360574e641 |  |  |  |  |
| 2641 | 86 | 56 | ba02ac838161 |  |  |  |  |
| 2709 | 87 | 80 | 7dfe5645ef66 |  |  |  |  |
| 2801 | 88 | 184 | b97071d428b9 |  |  |  |  |
| 2997 | 90 | 8 | 2dcdc28ae76a |  |  |  |  |

Note tag 111 and 112 carry IDENTICAL content (same sha1, 218 B each) in
both the DB and r0s builds — a duplicated tuning block.

## 4. Cross-generation diff vs the F-75 cr/ap NVMs

- Tag-id census: hpnv20 (DB) has 61 tags vs crnv20's 33, crnv11's 27,
  apnv10's 9. IDs extend to 200 (hpnv21 family reaches 261); the cr/ap
  files stop at 150. hpnv20-only ids: 8, 10, 28, 31, 32, 40, 42, 43, 44,
  57, 62, 72, 78, 113, 151, 153–155, 157, 161, 174, 176–180, 196, 197,
  199, 200, 206; crnv20-only: 41, 60, 73, 89.
- Kernel-known tags changed length: tag 17 (HCI) 6 B (was 9/8);
  tag 27 (DEEP_SLEEP) 9 B (was 1). The kernel's in-flight mutations
  (tag 17 `data[0]|=0x80`, tag 27 `data[0]|=0x01`) still land inside
  these records.
- **Tag content identity across generations: ZERO.** No (len,sha1) pair
  is shared between any h-NVM and any cr/ap NVM — the tag-content base is
  wholly new (contrast F-75 §5.3 where 7 tag contents were family-shared
  inside the cr/ap generation).

## 5. Cross-BUILD identity (the tractable part)

The r0s (Samsung) build and the cupid (DB) build differ in md5 and size
(6,203 vs 6,319) but share the same tag-id census and **44 of 60/61 tag
contents byte-identical** (same len+sha1). The varying 16–17 tags are the
per-build/per-device set (includes BD_ADDR tag 2 — the DB build's tag-2
sha1 `a43ddfc409e4` is in fact shared across ALL hp builds parsed, i.e.
it is a fleet-default address template, not a per-device value).

hpnv20g.bin vs hpnv20.bin (cupid partition, same generation): same 61-tag
census, **56/61 contents identical**; only tags 32, 42, 113, 176 (len
68→78) and 197 differ — a minimal GlobalFoundries-fab tuning delta on top
of the shared base. (btqca.c: the `g` suffix is selected when the chip's
SoC-id matches `QCA_HSP_GF_SOC_ID` — "manufactured by GlobalFoundries".)

bXX board variants: `hpnv20.b2f … b90` (10 files on the cupid partition,
matching the DB's 10 per-device variant names; FP5 ships 64). The mainline
naming rule `hpnv20.<prefix><board-id>` (prefix "b", board id from the
`qca_read_fw_board_id` VSC) explains the names; the DB's md5 census shows
most bXX files collapse to a handful of distinct contents (FP5's 64 → 5
distinct md5s; the 10-variant block → the same few groups), i.e. boards
share NVM content and only the board-id byte in the name changes. Which
tags the board byte influences [OPEN].

## 6. Free-reimplementation consequences

- Layout: fully specified (bare type-2, packed 12-byte prefixes) — a free
  NVM generator can emit this framing today; `fleet_diff.py` +
  `make_fixture.py` already produce and verify it.
- Content: the 44/61 shared tag base across builds is evidence the
  majority of the NVM is family-level tuning constants, but the values
  themselves are chip-tuning [OPEN semantics] — same honesty line as
  F-75 §6.
- The kernel's loader path (VSC 0xFC00 sub 0x1E, TLV_TYPE_NVM) already
  works unmodified for these files.

## 7. Freed-device value

hpnv20.bin: **10 laptop-half devices** (FP5 own build + 9 common-build
devices, 8 of which also carry hpnv20g.bin); whole-DB fleet 13 devices.
Both common-build files (hpnv20.bin + hpnv20g.bin) are now md5-verified
from a public source and fully tag-mapped; FP5's build remains provenance
[OPEN] (honest routes logged in hpbtfw20-analysis.md §7).
