# QCA BT patch/NVM fleet — container format decoded (fleet-re, 2026-11-16)

**Evidence class: format-spec** (container layer fully derived from public
GPL parser code + byte-verified against the 29-device fleet; patch-entry
interior remains open). One RE pass on 10 files documents the BT bring-up
surface of up to 29 devices per file — recon.md top-20 entries #1-#6 and
their siblings.

## Identity chain (the load-bearing result)

The six top-20 fleet blobs (md5-keyed, 29 devices each in the committed
matrix) are byte-identical to files extracted from the OnePlus 6
`bluetooth` partition (official LineageOS 22.2 nightly 2026-11-11,
sha256-verified zip):

| file | bytes | md5 | fleet devices | identity provenance |
|---|---|---|---|---|
| `apbtfw10.tlv` | 56,052 | `42a31bb8…d4c6` | 29 | OP6 payload **and** public linux-firmware (qca/) — double match |
| `apnv10.bin` | 1,243 | `4905d516…14ff` | 29 | OP6 payload **and** linux-firmware — double match |
| `crbtfw20.tlv` | 56,180 | `16077492…7eef` | 29 | OP6 payload (linux-firmware lacks the name — 404) |
| `crbtfw11.tlv` | 29,368 | `eae2d0a1…8092` | 29 | OP6 payload |
| `crnv20.bin` | 3,936 | `bb6ca169…b4c1` | 29 | OP6 payload |
| `crnv11.bin` | 2,798 | `7c0db76f…00c6` | 29 | OP6 payload |

Plus four sibling variants extracted from the same volume: `apbtfw11.tlv`
(216,372), `crbtfw21.tlv` (217,676), `apnv11.bin` (4,760), `crnv21.bin`
(4,619). Facts only committed; payload bytes never leave this analysis.

## The container that carries them (new partition-level fact)

The OnePlus 6 `bt.img` partition (765,952 B) is a **FAT16 volume**
(`EB 3C 90` + `MSDOS5.0` OEM; BPB: 4,096 B/sector, 4 sec/cluster, 1
reserved sector, 2 FATs × 3 sectors, 512 root entries), whose root holds a
single `IMAGE` directory containing the ten fleet files above. The volume
declares 16,384 sectors but the OTA writes only the first 187 — the
written region contains the whole live directory tree. Upstream counts
`bt.img` as one opaque blob; it is in fact a filesystem carrying the
entire patch fleet, which is how one SDM845 device ships all 29-device
fleet files at once.

## Format spec (every field grounded in public GPL code)

Outer header — `struct tlv_type_hdr` (btqca.h): one LE32 `type_len =
(length << 8) | type`, 4 bytes; `len_check` passes 10/10.

Patch files (`type = 1 = TLV_TYPE_PATCH`), payload = `struct
tlv_type_patch` (24 bytes, btqca.h):

| field | apbtfw10 | apbtfw11 | crbtfw11 | crbtfw20 | crbtfw21 |
|---|---|---|---|---|---|
| total_size | 55,792 | 216,112 | 29,108 | 55,920 | 217,416 |
| data_length | 55,768 | 216,088 | 29,084 | 55,896 | 217,392 |
| format_version | 1 | 1 | 1 | 1 | 1 |
| signature | 2 | 2 | 2 | 2 | 2 |
| download_mode | 3 | 3 | **0** | 3 | 3 |
| product_id | 10 | 10 | 10 | 10 | 10 |
| rom_build | 0x0200 | 0x0201 | 0x0101 | 0x0200 | 0x0201 |
| patch_version | 2 | 2 | 2 | 2 | 2 |
| entry | 0x1b0e0 | 0x209e4 | 0x1b15c | 0x1b0e0 | 0x209e4 |

- `total_size == data_length + 24` holds 5/5 — the struct is exactly
  self-describing against real bytes.
- `download_mode` 0 vs 3 is the Rome-generation split btqca.c documents
  ("Rome 1.1-3.1 acks every segment via VSE; >= 3.2 may skip; field
  indicates"): crbtfw11 (ROM 1.1) = 0, all 2.x = 3 (`SKIP_EVT_VSE_CC`).
- **`rom_build` equals the filename suffix** — filename ↔ header identity
  proven 5/5; `ap*`/`cr*` are two patch families for the same ROM
  versions (chip-family split not yet attributed — open item).
- **`entry` pairs by generation**: the 2.0 files carry 0x1b0e0 (crbtfw11's
  1.1 variant: 0x1b15c), the 2.1 files carry 0x209e4 — per-generation
code entry addresses, ap* and cr* agreeing.
- Every patch file carries a **256-byte tail after `total_size`** (0.4-1.2%
  zero bytes — content, not padding). Unknown role: attestation/
  signature/manifest — open item.
- `data_length` bytes after the 24-byte header are the patch stream;
  first bytes of apbtfw10's stream (`f8 b5 5e 48 00 24 00 68 80 47…`)
  are consistent with ARM Thumb (0xb5f8 = push {r2-r7,lr}) — **observed
  byte pattern, ISA unconfirmed**; the entry-level structure of the
  stream is not parsed by any public code we found (btqca.c sends it
  verbatim in 243-byte segments per `MAX_SIZE_PER_TLV_SEGMENT`).

NVM files (`type = 4` enclosing): each wraps **one inner `type = 2` tag
set + one `type = 3` set** (443-1,237 B, unknown content — btqca.c reads
only the first type-2 set and skips the type-3 set entirely). Each type-2
entry is a `struct tlv_type_nvm` = 12-byte header (`tag_id u16, tag_len
u16, reserve1 u32, reserve2 u32`) + `tag_len` data bytes; the parser
consumes set 1 **exactly** (6/6 `exact_close`).

- All 6/6 carry the three tags btqca.c handles: `0x0002` BD_ADDR
  (tag_len 6 ✓), `0x0011` HCI transport (baud-rate byte per soc_type),
  `0x001b` deep-sleep.
- Tag-table growth decodes ROM progression: apnv10 = 9 tags →
  apnv11 = 44 / crnv21 = 45 tags. **First public enumeration of the NVM
  tag surface beyond the 3 kernel-handled tags** (RULE 0: btqca.c handles
  exactly 3; no public tag-name table beyond it was found — checked
  2026-11-16; tag IDs ≥ 0x0020 are honest unknowns).
- BD_ADDR placeholders differ per variant (`200000108039`,
  `000774118039`, `006401019039`, `000053209039`, `000774219039`) —
  default/template addresses replaced at provisioning; the generic
  linux-firmware `apnv10.bin` carries the same placeholder as the OP6
  copy (byte-identical).

## Deliverables

- `tools/qca_tlv_parse.py` — the parser (stdlib only)
- `tools/fat_extract.py` — the minimal FAT16 walker used for `bt.img`
- Full per-file parse results (headers, tag histograms + per-entry
  values, BD_ADDR placeholders, checks): regenerable byte-identically
  with `python3 blob-matrix/desktop/tools/qca_tlv_parse.py
  qca-bt-tlv.json <extracted fleet files>` — the pipeline is committed
  and the inputs are public (any official LineageOS nightly of a
  fleet-carrying device, e.g. enchilada 2026-11-11); the 53 KB results
  JSON stayed local this session for the same push-path reason as
  `devices-001-222.csv` (see STATUS-DESKTOP.md push mechanics).
- The 29-device leverage entry in `fragmentation-half.md` §2 is now
  backed by an actual format spec instead of a name.

## Open items

1. Patch-stream entry structure (post-header) — needs one of: CodeLinaro
   qca-bt opensource `hci_rome.c` fetch, or a controlled diff between
   rom_build variants (2.0 vs 2.1 of the same family).
2. `ap*` vs `cr*` chip-family attribution.
3. The 256-byte patch tails (role unknown).
4. NVM tags ≥ 0x0020 naming (would need one Qualcomm-side spec leak —
   none found public; checked 2026-11-16).
5. The other four fleet files in linux-firmware's qca/ dir are named
   differently (404 on the matrix names) — upstream matrix filenames are
   LineageOS-vendor-tree names, not linux-firmware names; the md5 joins
   above prove equivalence where both exist.

RULE 0 record (2026-11-16): `Qualcomm Bluetooth ROM patch .tlv format
reverse engineering crbtfw apbtfw` — no dedicated RE writeup exists
(Broadcom/Realtek have public RE work; QCA does not, beyond btqca.c's
protocol layer). The container-layer spec + fleet identity chain here is
the first public one for these files.
