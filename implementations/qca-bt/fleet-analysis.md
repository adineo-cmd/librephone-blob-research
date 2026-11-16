# Fleet analysis — real-payload RE of the QCA BT leverage fleet (2026-11-17)

The program's **first content-level RE**: the six top-20 leverage blobs
(recon.md rows 1-6, `crbtfw20.tlv` / `apbtfw10.tlv` / `crbtfw11.tlv` /
`crnv20.bin` / `crnv11.bin` / `apnv10.bin` — 29 devices each in the upstream
DB) were located in public repositories, fetched, **md5-verified byte-exact
against the upstream database (6/6 MATCH)**, and run through the lab's
clean-room parser (`qca_tlv.py`, 30/30 fixtures). This file documents what
the real bytes actually contain, per parsed byte range. No payload bytes are
committed here — payload files live only in `/tmp/astro_s/payloads/`
(regeneratable via the route log below); everything below is derived
structural fact.

Clean-room statement: `qca_tlv.py` was written from GPL kernel sources only;
this session added *data* (real payloads) on top of that parser. The parser
file itself was not modified.

## 1. Provenance and md5 verification (all six MATCH)

Upstream md5s from `upstream-contribution/blob-database/coverage-matrix.csv`
(each filename maps to exactly one md5 across all 29 device rows — checked
before fetching). Fetches 2026-11-17.

| file | bytes | DB md5 | fetched md5 | status |
|---|---|---|---|---|
| `crbtfw20.tlv` | 56,180 | `16077492405d178c5198b86b3cec7eef` | same | **MATCH** |
| `apbtfw10.tlv` | 56,052 | `42a31bb8b2afa5b805dfda78cb1ed4c6` | same | **MATCH** |
| `crbtfw11.tlv` | 29,368 | `eae2d0a1fa6690a9eac392a1cef28092` | same | **MATCH** |
| `crnv20.bin` | 3,936 | `bb6ca169095f116ce20029238b4ca4c1` | same | **MATCH** |
| `crnv11.bin` | 2,798 | `7c0db76f1a434d20b3ce3e261b2d00c6` | same | **MATCH** |
| `apnv10.bin` | 1,243 | `4905d516ca6ff77eee8f9f82a17a14ff` | same | **MATCH** |

sha256 of the verified bytes (recorded for future re-download cross-checks):

| file | sha256 |
|---|---|
| crbtfw20.tlv | `d9afa5d9facd528f437e83bcc8147681afd432296ebbba5e77904c13fab28209` |
| apbtfw10.tlv | `07f0f45cff57347a73ada68bf2bd564e17998383388ef27bd2e9de5269c1986f` |
| crbtfw11.tlv | `d6532b99875890fb7969874ff6e904939ca0d6f2d2bd1e1fd3ae86470bebc9f5` |
| crnv20.bin | `6c96fe067860a79813b466a1d4644dc2748a4191b21a986a44d2cc0fe6ccaca7` |
| crnv11.bin | `206deb651dcfd187d1fd39f1f064af20324d1b4e28dcd72f5ed23bb8ef605d00` |
| apnv10.bin | `4cb35fec741a3294f5c64d41aefba45cf899c42cc4c00800bba7029cca5919d9` |

### Sources per file (public, individually fetchable — no 1.3 GB package)

| file | source(s) that fetched byte-exact |
|---|---|
| crbtfw20.tlv | `commaai/vamOS` @ `master`, `kernel/firmware/qca/` (Git-LFS; via `media.githubusercontent.com/media/...`) **and** `TheMuppets/proprietary_vendor_essential_mata` @ `lineage-22.2`, `proprietary/vendor/firmware/` (raw) — mata = Essential PH-1, which is **outside** the DB's 29-carrier set (no mata row in `coverage-matrix.csv` for crbtfw20.tlv) yet ships the byte-identical blob: the real-world carrier set of these fleet files exceeds the DB's device attribution |
| crbtfw11.tlv | `commaai/vamOS` @ `master` (LFS); also listed in mata's tree (not fetched) |
| crnv20.bin | `commaai/vamOS` @ `master` (LFS) **and** TheMuppets mata (raw) — both byte-exact |
| crnv11.bin | `commaai/vamOS` @ `master` (LFS) |
| apbtfw10.tlv | `kernel.org linux-firmware` `qca/apbtfw10.tlv` (plain blob) **and** `Rentz412/Ubuntu_For_Xiaomi5_Gemini` @ `main`, `firmware/qca/` (LFS) — the device copy and the linux-firmware copy are byte-identical |
| apnv10.bin | same two sources as apbtfw10.tlv, both byte-exact |

### F-74 confirmed (linux-firmware absence)

The kernel.org `qca/` directory listing (fetched 2026-11-17) contains
`apbtfw10/11.tlv`, `apnv10/11.bin`, `crbtfw21/32.tlv`, `crnv21/32.bin`,
`hmtbtfw20`, `hpbtfw10/21`, `htbtfw20` and the old ath3k `rampatch_*`/
`nvram_*` files — but **no `crbtfw20.tlv`, `crbtfw11.tlv`, `crnv20.bin`,
`crnv11.bin`**. Those four ship only inside device/vendor packages, exactly
as the F-74 fleet finding recorded. Bonus counterexample for the general
"linux-firmware has it" assumption: mata also ships `crbtfw21.tlv`
(119,720 B, md5 `3e7167ba14a2d00f9765007e8c561562`) which is a **different
build** from linux-firmware's same-named `crbtfw21.tlv` (177,060 B, md5
`4fceacf111c621d93666aaeafc1eaf56`) — same filename, different bytes.

### Route log (RULE 0, all probes 2026-11-17)

1. Unauthenticated GitHub code search API (`/search/code`) → 401
   "Requires authentication" (expected). Authenticated `gh api` search used
   instead.
2. `q=<name> in:path` code search: `crbtfw20.tlv` → 1 hit
   (`commaai/vamOS kernel/firmware/qca/`); `apbtfw10.tlv` → 2 hits
   (`Rentz412/Ubuntu_For_Xiaomi5_Gemini firmware/qca/`,
   `microscaler/talos-dgx-spark .../linux-firmware/qca/apbtfw10.tlv.zst` —
   a compressed linux-firmware copy); `crbtfw11.tlv` / `crnv20.bin` /
   `crnv11.bin` → `commaai/vamOS` each.
3. kernel.org `linux-firmware` `qca/` tree listing → ap pair present, cr/cn
   quartet absent (F-74 confirmed); both ap files fetched plain, byte-exact.
4. First raw fetch from `commaai/vamOS` and the Mi 5 repo returned 130-byte
   **Git-LFS pointer files** — refetched via
   `media.githubusercontent.com/media/<owner>/<repo>/<ref>/<path>`, which
   yields the real content for LFS-hosted files. 6/6 md5-match.
5. `q=crbtfw20.tlv in:file` search (162 hits) surfaced device trees listing
   the blob (`LineageOS/android_device_essential_mata proprietary-files.txt`,
   omnirom oneplus6, HTC ocn, asus X00T…) → TheMuppets mata vendor repo.
   `media.githubusercontent.com` returned 0 bytes for mata (its blobs are
   plain git objects, not LFS); `raw.githubusercontent.com` worked → mata
   crbtfw20.tlv + crnv20.bin byte-exact (direct device-tree corroboration).
6. Negatives: postmarketOS wiki behind an Anubis anti-bot challenge
   (unrelated to this mission); no other fleet-file public source needed —
   every file had ≥1 byte-exact source before moving on.

## 2. Parser runs on real payloads

```
python3 -I implementations/qca-bt/qca_tlv.py <file> --json out.json --brief
```

Exit status **0 (no error-class diagnostics) for all six files** — the
container chain, record bounds, tag stride arithmetic and declared-length
consistency the kernel relies on all hold on the real fleet bytes. The only
diagnostics are the parser's info class:

- patch files: `data-length-note` (header `data_length` ≠ bytes-after-header)
  and `total-size-note` (header `total_size` ≠ file size) — both expected;
  the kernel never validates either field (see §3 — the real explanation is
  the 256-byte tail).
- NVM files: `trailing-bytes` (947/447/947) — explained below (§5): the
  trailing bytes are a further TLV record, not garbage.

Family annotations from the canonical-name re-run (offset-correct):

| file | prefix | kernel chip family | rom_ver derived from `rom_build` | parser-expected name | ships as |
|---|---|---|---|---|---|
| crbtfw20.tlv | cr | WCN3990/3991/3998 | 0x20 | `qca/crbtfw20.tlv` | same ✓ |
| apbtfw10.tlv | ap | WCN3988 | 0x20 (default formula) | `qca/apbtfw20.tlv` | `apbtfw10.tlv` ✗ (see §4) |
| crbtfw11.tlv | cr | WCN3990/3991/3998 | 0x11 | `qca/crbtfw11.tlv` | same ✓ |

## 3. Patch files: record layout and the 256-byte tail

All three rampatches are `TLV_TYPE_PATCH` (1) containers:

```
[0, 4)    tlv_type_hdr       type_len word: type=1 low byte, length = file-4
[4, 28)   tlv_type_patch     24 bytes (btqca.h offsets, verified sane)
[28, 28+data_length)         patch body (opaque, §3.2)
[28+data_length, file)       256-byte tail (opaque, §3.3)
```

### 3.1 Header fields, all three files

| field (offset in header) | crbtfw20.tlv | apbtfw10.tlv | crbtfw11.tlv |
|---|---|---|---|
| container length_field [0,4) = file−4 | 56,176 | 56,048 | 29,364 |
| total_size [+0] | 55,920 | 55,792 | 29,108 |
| data_length [+4] | 55,896 | 55,768 | 29,084 |
| format_version [+8] | 1 | 1 | 1 |
| signature_algorithm [+9] | 2 | 2 | 2 |
| download_mode [+10] | 3 = SKIP_EVT_VSE_CC | 3 = SKIP_EVT_VSE_CC | 0 = SKIP_EVT_NONE |
| reserved1 [+11] | 0 | 0 | 0 |
| product_id [+12] | 10 | 10 | 10 |
| rom_build [+14] | 0x0200 | 0x0200 | 0x0101 |
| patch_version [+16] | 0x0002 | 0x0002 | 0x0002 |
| reserved2 [+18] | 0x8000 | 0x8000 | 0x8000 |
| entry [+20] | 0x0001b0e0 | 0x0001b0e0 | 0x0001b15c |
| segments (243 B each, whole file) | 232 (last 47 B) | 231 (last 162 B) | 121 (last 208 B) |

**Structural invariants (hold in all three, error-free):**

1. container `length_field == file_size − 4` (holds in all six fleet files).
2. `total_size == data_length + 24` — the header's own idea of the file is
   "24-byte header + data_length bytes". The real file is larger by a
   **constant 256-byte tail** in every patch file:
   `file = 4 + 24 + data_length + 256`.
3. `product_id = 10`, `format_version = 1`, `signature_algorithm = 2`,
   `reserved2 = 0x8000`, `patch_version = 0x0002` across all three — i.e.
   `patch_version` does **not** encode the 1.0/1.1/2.0 in the filename (that
   digit is the ROM build targeted, §4).
4. `download_mode` tracks the ROM generation: both `rom_build 0x0200` files
   use SKIP_EVT_VSE_CC (send-only + synthetic completion); the `0x0101`
   file uses SKIP_EVT_NONE (every segment acked).
5. The upstream 24-byte header decodes sanely on these files (plausible RAM
   entry point, coherent size arithmetic) — the parser's
   "32-byte-vendor-header" alternative hypothesis (its size_note, from the
   FP6 msbtfw/evr census) is not needed for this fleet.

### 3.2 Patch body [28, file−256)

- Entropy 6.85-6.91 bits/byte, 8.7-8.8% zero bytes, <1% 0xFF — dense
  machine-code-like content, no compression markers observed at the range
  boundaries.
- Most-common little-endian 4-byte words are shared across all three files:
  `0x4801b403` ×133/133/104 and `0xbd019001` ×133/133/104 (crbtfw20/apbtfw10/
  crbtfw11). As little-endian 16-bit instruction words these are `b403 4801`
  (`push {r0,r1}`; `ldr r0,[pc,#4]`) and `9001 bd01` (`str r0,[sp,#4]`;
  `pop {r0,r1}`) — classic ARM Thumb stack-veneer pairs; `0x47886809` =
  `6809 4788` (`ldr r1,[r1,#8]`; `blx r3`). **Interpretation [OPEN]:** the
  patch bodies are ARM Thumb machine code for the controller's ARM core,
  with the repeating pattern being patch-entry veneers. Every claim above is
  tied to the parsed word histogram over [28, file−256); no disassembly was
  performed and no code was interpreted beyond these statistics.
- crbtfw20 vs apbtfw10 (same `rom_build`, same `entry`, same everything but
  the size fields): **43.69% of bytes identical at the same offsets**
  (24,487/56,052). 1,257 differing runs; 821 of them are <16 bytes
  (instruction-word-level edits, 3,733 bytes total); the rest coalesce into
  140 regions (≥8-byte gap), dominated by two wholesale blocks: [24,160,
  22,804 B) and [47,918, 8,134 B) (to end of common range). So the two
  chip-variant patches share one overlay base (~24 KB) with chip-specific
  blocks swapped in — **one RE pass informs both families**.
- crbtfw20 vs crbtfw11 (different `rom_build`): 2.60% same-offset equality,
  10/1,818 shared 16-byte blocks — **wholly different builds**, consistent
  with the different entry point and download mode.

### 3.3 The 256-byte tail [file−256, file)

Exactly 256 bytes beyond `28 + data_length` in every patch file — the file
region the header's own arithmetic does not account for. Entropy 7.13-7.18
bits/byte (higher than the body), near-zero runs of 0x00/0xFF. Size and
statistics are consistent with an RSA-2048 signature block, but **content
semantics [OPEN]** — the kernel never inspects them, yet streams them to the
chip (whole-file segmentation), so the controller evidently consumes them.
Tails differ between crbtfw20 and apbtfw10 (different sha1) even though 44%
of their bodies match.

## 4. What "1.0 / 1.1 / 2.0" actually mean (the version story)

The filename digit is the **ROM build the patch targets**, recovered through
the kernel's chip-specific formula — not a linear patch release number:

- `crbtfw20.tlv`: `rom_build 0x0200`, default formula → rom_ver 0x20 → "20".
- `crbtfw11.tlv`: `rom_build 0x0101` → rom_ver 0x11 → "11".
- `apbtfw10.tlv`: `rom_build 0x0200` — **the same ROM build as crbtfw20** —
  but WCN3988's chip-specific shift (`(soc&0xf00)>>5 | soc&0xf`) maps it to
  rom_ver 0x10 → "10". The parser (default formula) expected
  `apbtfw20.tlv`; the shipped name is the WCN3988-specific resolution. This
  resolves the parser's `[OPEN]` formula note with real data: same 32-bit
  ROM-build field, different per-chip shift, different filename digit.

Consequences:

- `apbtfw10.tlv` (WCN3988) and `crbtfw20.tlv` (WCN399x) are patches against
  the **same ROM build** and share 44% body content with identical entry
  points — the WCN3988/WCN399x BT cores are one patch-generation apart.
- `crbtfw11.tlv` targets an older ROM build (0x0101) and shares nothing
  with the 0x0200-generation files — "1.1" is *not* an intermediate of
  crbtfw20's codebase.
- `patch_version 0x0002` is constant everywhere → it is the patch *format*
  revision, not the ROM generation.

## 5. NVM files: full tag map + the kernel-ignored type-3 record

All three NVRAMs are **type-4 multi-NVM containers** (`MULTI_NVM_ENCLOSING`
enclosing header at [0,4), first set header at [4,8)):

```
[0, 4)    type-4 enclosing header   (length = file-4)
[4, 8)    type-2 set header         (length = declared set bytes)
[8, 8+set)  tlv_type_nvm tags, 12-byte prefix each (tag_id u16, tag_len u16,
            reserve1 u32, reserve2 u32), back-to-back, zero padding
[8+set, file)  a type-3 TLV record the mainline parser never reads
```

### 5.1 The type-3 record — new structural fact

The trailing region flagged as `trailing-bytes` by the parser is a **further
TLV record**: its first word decodes as type **3** with length exactly
`trailing − 4`, in all three files:

| file | record offset | first word | type-3 declared len | consistency |
|---|---|---|---|---|
| crnv20.bin | 2,989 | 0x0003af03 | 943 | declared = actual ✓ |
| crnv11.bin | 2,351 | 0x0001bb03 | 443 | declared = actual ✓ |
| apnv10.bin | 296 | 0x0003af03 | 943 | declared = actual ✓ |

- **crnv20.bin's and apnv10.bin's type-3 records are byte-identical**
  (947 B, sha1 `71de3a2841065e88…`) — the same record ships inside the NVRAM
  of two different chip families.
- crnv11.bin's is a different 447-byte record (sha1 `4adfca24587d0acd…`).
- The kernel parses only the first type-2 set ("only parse the first set
  when it has type 2 for now") and ignores this record entirely, but streams
  it to the chip like every other byte. Vendor-consumed semantics **[OPEN]**.
  Note this is a counterexample to the parser docstring's claim that type 3
  is "never a container type byte on disk" — on these files it *is* on disk,
  as an NVM-internal record type. (`qca_tlv.py` deliberately left
  unmodified; its NVM scan path handles the observation correctly as
  info-level.)
- Trailing-region statistics: entropy 3.40/4.35/3.40 bits/byte (far below
  the patch tail — table-like content), 54.7%/42.7%/54.7% zero bytes,
  12.6%/0.9%/12.6% 0xFF; crnv20/apnv10 show a repeating 16-byte-block
  structure (59 blocks, 39 distinct, most-common block repeats 14×).

### 5.2 Full tag tables (offsets are file offsets; tag data NOT reproduced —
sha1 prefixes only)

**crnv20.bin — 33 tags, set [8, 2989), consumed 2,981/2,981, zero padding**

| off | tag | len | sha1-12 | off | tag | len | sha1-12 |
|---|---|---|---|---|---|---|---|
| 8 | 2 BD_ADDR | 6 | dabb72163cfd | 1283 | 83 | 8 | 0e0cddbc8105 |
| 26 | 17 HCI | 9 | e11b08b702f6 | 1379 | 85 | 124 | ab0a5a373fe9 |
| 47 | 22 | 60 | c8315263d15e | 1515 | 86 | 16 | 9c5784d4a951 |
| 119 | 27 DEEP_SLEEP | 1 | bf8b4530d8d2 | 1543 | 87 | 16 | cf688d8a9cad |
| 132 | 35 | 68 | 968c5e1981f7 | 1571 | 88 | 144 | 4a814a1a6625 |
| 212 | 36 | 16 | 9b43f463ae67 | 1727 | 89 | 196 | a3cf9f345367 |
| 240 | 37 | 32 | 594ea1952110 | 1935 | 90 | 8 | 2b299c192d25 |
| 284 | 38 | 55 | cbe511870d77 | 1955 | 91 | 188 | 39fb0071eafe |
| 351 | 39 | 4 | 61e4653de420 | 2155 | 92 | 64 | 6b48ea23532b |
| 367 | 41 | 180 | 1af48383f114 | 2231 | 95 | 100 | 24a72a91ce35 |
| 559 | 50 | 222 | 509692e62d96 | 2343 | 111 | 204 | 6788f95b50f1 |
| 793 | 51 | 48 | 10c6c1564c32 | 2559 | 112 | 232 | 7f734d70372d |
| 853 | 60 | 129 | fa6095298884 | 2803 | 114 | 132 | ea3314e3ac4a |
| 994 | 64 | 88 | 9d236b029009 | 2947 | 150 | 30 | 656fa199d455 |
| 1094 | 65 | 22 | 7c0cb8f29f1b | | | | |
| 1128 | 73 | 1 | 356a192b7913 | | | | |
| 1141 | 79 | 82 | f61ebddf8d40 | | | | |
| 1235 | 80 | 16 | 04d1467a4d5f | | | | |

**crnv11.bin — 27 tags, set [8, 2351), consumed 2,343/2,343, zero padding**

| off | tag | len | sha1-12 | off | tag | len | sha1-12 |
|---|---|---|---|---|---|---|---|
| 8 | 2 BD_ADDR | 6 | 9e4093c0b241 | 999 | 84 | 56 | 04d52349bd73 |
| 26 | 17 HCI | 8 | 2c7c06e240c4 | 1067 | 85 | 124 | f45fff4b57c8 |
| 46 | 27 DEEP_SLEEP | 1 | bf8b4530d8d2 | 1203 | 86 | 16 | c8d39550e5c3 |
| 59 | 28 | 20 | c6e7cf0e895c | 1231 | 87 | 16 | e129f27c5103 |
| 91 | 35 | 168 | a0f9815376c0 | 1259 | 88 | 144 | ec334c9191f3 |
| 271 | 38 | 45 | 202b33ba9097 | 1415 | 91 | 148 | e9f664058eca |
| 328 | 39 | 4 | b0449d8ebb02 | 1575 | 92 | 64 | 6b48ea23532b |
| 344 | 41 | 116 | 94b2661bd4e4 | 1651 | 95 | 98 | c76d03f758ef |
| 472 | 45 | 132 | 5f0fed37a231 | 1761 | 111 | 204 | 189e923b367c |
| 616 | 60 | 101 | ad1f0f4c6514 | 1977 | 112 | 232 | 2eccb1e12461 |
| 729 | 64 | 82 | d36657af08be | 2221 | 114 | 84 | 5a22075714b0 |
| 823 | 65 | 22 | 7c0cb8f29f1b | 2317 | 150 | 22 | dde7ff3b8d21 |
| 857 | 79 | 82 | f61ebddf8d40 | | | | |
| 951 | 80 | 16 | 04d1467a4d5f | | | | |
| 979 | 83 | 8 | 0e0cddbc8105 | | | | |

**apnv10.bin — 9 tags, set [8, 296), consumed 288/288, zero padding**

| off | tag | len | sha1-12 |
|---|---|---|---|
| 8 | 2 BD_ADDR | 6 | eb1861258b7c |
| 26 | 17 HCI | 9 | e11b08b702f6 |
| 47 | 22 | 60 | d7cb00ab36e7 |
| 119 | 27 DEEP_SLEEP | 1 | bf8b4530d8d2 |
| 132 | 37 | 32 | 1cc8b9d6bdae |
| 176 | 38 | 55 | cbe511870d77 |
| 243 | 39 | 4 | 96760d655a51 |
| 259 | 41 | 12 | e1c9ea677c5c |
| 283 | 73 | 1 | 356a192b7913 |

### 5.3 Cross-file tag findings (content identity via sha1 — not bytes)

- **Byte-identical tag content across chip families:** tag 27 (1 B, all
  three files), 65 (22 B, crnv20+crnv11), 73 (1 B, crnv20+apnv10), 79
  (82 B, crnv20+crnv11), 80 (16 B, crnv20+crnv11), 83 (8 B, crnv20+crnv11),
  92 (64 B, crnv20+crnv11). Also crnv20↔apnv10: tag 17 (9 B) and tag 38
  (55 B) identical. These are family-level constants, not per-device tuning.
- Tag 2 (BD_ADDR): 6 B in all three, content differs pairwise (shared
  leading bytes: crnv20/crnv11 = 1, others = 0) — per-chip default address
  templates, not shared.
- Tag census progression: crnv20 = 33 tags/2,981 B; crnv11 = 27/2,343;
  apnv10 = 9/288. apnv10's set is a strict subset by count (its tags are a
  reduced bring-up set); crnv20-only tags: 36, 50, 51, 89, 90; crnv11-only:
  28, 45; tag 22 present in crnv20+apnv10 but not crnv11.
- The two kernel in-flight mutations are **already pre-applied** in all
  three files: tag 17 data[0] bit 7 (inband-sleep) is set, and tag 27
  data[0] bit 0 (sleep-enable) is set — the kernel's ORs are idempotent
  no-ops on these bytes. The baud-rate byte the kernel writes into tag 17
  (data[1] for WCN3991+, data[2] otherwise) is not verifiable from the file
  alone; tag 17 lens are 9 (crnv20, apnv10) and 8 (crnv11).
- No tag overruns, no BD_ADDR length violations (kernel's tag-2 `==6`
  check passes), zero padding inside sets — the vendor NVM generator emits
  perfectly packed 12-byte-prefix records.

## 6. What this means for a free reimplementation

**Fully specified, writable today with zero proprietary bytes** (GPL kernel
code + the range map above, now verified on real files):

- Container framing, patch header field semantics, NVM set/tag framing,
  the type-4 enclosing unwrap, the download protocol (VSC 0xFC00 /
  sub-command 0x1E, 243-byte segments, last-segment-ack rule, synthetic
  completion for VSE-skipping modes), and the tag-17/tag-27 in-flight
  mutations. The lab's parser already implements all of it and passed on
  all six real files — a free *loader* is the next step, not new RE.
- NVM structure: a free NVM generator can emit the same record framing;
  tag payloads are chip-tuning values (RF/calibration), of which seven
  tag contents are provably family-constant (§5.3) and could be carried
  as shared constants; per-device tags (BD_ADDR tag 2) must be provisioned
  at generation time.

**Opaque content — needs synthesis or further RE, not byte-copying:**

- Patch body [28, file−256): ARM Thumb-consistent machine code overlay
  (~6.9 bits/byte). A free replacement means generating an equivalent
  overlay (or determining the controller can run unpatched ROM with
  reduced features); the 44% crbtfw20↔apbtfw10 overlap shows the overlay
  base is shared and the chip-specific deltas are localized to two large
  blocks.
- 256-byte patch tail: signature-class content [OPEN] — a free build must
  either satisfy the chip's verification or find the chip's unsigned
  download mode.
- Type-3 NVM record: kernel-ignored, chip-consumed, family-shared between
  crnv20 and apnv10 [OPEN].

**Program-level:** the fleet is six small files (1.2-56 KB), fetchable
individually from public repos (no 1.3 GB package), md5-stable across the
entire 29-device fleet (one md5 per filename), and structurally identical
under the lab's parser. Every remaining unknown is now pinned to an exact
byte range with [OPEN] labels — the RE surface went from "six opaque
binaries" to "two opaque regions per patch + one record per NVM".

## 7. Scratch artifacts (regeneratable)

- `/tmp/astro_s/payloads/` — verified payload bytes (canonical copies in
  `canonical/`, plus per-source copies: `vamos_*`, `mi5_*`, `mata_*`,
  `linuxfw_*`).
- `/tmp/astro_s/analysis/` — parser JSON per file (`*_parsed.json`),
  brief/diag outputs, `fleet_struct.py` (the statistics script; all numbers
  in this document come from its runs or the parser JSONs).
- Payload bytes are NOT committed to the repo per program rules.
