# OnePlus 6 (enchilada) — Bluetooth family

**Evidence class: format-spec** (container decoded; fleet files extracted
with byte-exact identity; patch-entry interior still open).
Source: LineageOS 22.2 nightly 2026-11-11 enchilada, OTA payload partition
`bluetooth` → `bt.img` (765,952 B, sha256
`a01be531d8f9bcab42beda4c84032492bedbb3c9896902111311420e14fe5721`).

## The partition is a FAT16 filesystem (container decoded 2026-11-16)

`bt.img` opens `EB 3C 90` + `MSDOS5.0` — a FAT16 volume (BPB:
4,096 B/sector, 4 sec/cluster, 1 reserved sector, 2 FATs × 3 sectors, 512
root entries; declares 16,384 sectors while the OTA writes only the first
187 — the live tree fits entirely in the written region). Root holds one
`IMAGE` directory containing **the complete QCA BT patch/NVM fleet**:

| file | bytes | md5 (first 8) | matrix fleet match |
|---|---|---|---|
| APBTFW10.TLV | 56,052 | `42a31bb8` | ✓ 29 devices (also = public linux-firmware) |
| APBTFW11.TLV | 216,372 | `3eaa6452` | sibling variant |
| APNV10.BIN | 1,243 | `4905d516` | ✓ 29 devices (also = linux-firmware) |
| APNV11.BIN | 4,760 | `b88ce73d` | sibling variant |
| CRBTFW11.TLV | 29,368 | `eae2d0a1` | ✓ 29 devices |
| CRBTFW20.TLV | 56,180 | `16077492` | ✓ 29 devices |
| CRBTFW21.TLV | 217,676 | `bad9ca7b` | sibling variant |
| CRNV11.BIN | 2,798 | `7c0db76f` | ✓ 29 devices |
| CRNV20.BIN | 3,936 | `bb6ca169` | ✓ 29 devices |
| CRNV21.BIN | 4,619 | `114219c8` | sibling variant |

So one SDM845 device ships every top-20 QCA BT fleet blob (recon.md #1-#6)
byte-exactly, and the desktop half's single highest-leverage RE family is
fully covered by this one payload. Full format spec + per-file parse
results: [../../blob-matrix/desktop/fleet-re/qca-bt-format.md]
(../../blob-matrix/desktop/fleet-re/qca-bt-format.md).

`/vendor/bt_firmware` in the vendor image is an empty mount point —
consistent with the payload living in this partition.

## What the fleet files are (format layer)

- Patch files (`type 1`): 24-byte `tlv_type_patch` header (public btqca.h
  struct, verified against real bytes: `total_size == data_length + 24`
  5/5), `rom_build` equals the filename suffix (0x0101/0x0200/0x0201),
  `download_mode` splits by Rome generation (1.1 → 0, 2.x → 3), 256-byte
  unknown tail per file, per-generation entry addresses (0x1b0e0 / 0x1b15c
  / 0x209e4).
- NVM files (`type 4` enclosing): one inner type-2 tag set (parsed
  exactly) plus one type-3 set (443-1,237 B, unknown, skipped by
  btqca.c entirely), 9-45 tags per variant, all six carry BD_ADDR
  (0x0002), HCI transport (0x0011), deep-sleep (0x001b); the further
  tag IDs are enumerated as honest unknowns.

## ISA/proof status

Patch-stream interior: byte pattern consistent with ARM Thumb
(0xb5f8 push) — observation only, ISA unconfirmed; no public parser of
the entry-level structure exists (checked 2026-11-16).

## Open questions

- patch-stream entry structure + the 256-byte tails
- `ap*` vs `cr*` chip-family attribution
- WCN3990-specific semantics (this device's chip) vs the fleet files it
  carries (it ships files for several generations)
