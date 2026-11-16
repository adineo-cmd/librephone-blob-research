# OnePlus 6 partition map decoded — bt.img, modem.img, tz.img, dsp.img (fleet-re, 2026-11-17)

**Evidence class: format-spec** (container layer; per-file census with
matrix md5 joins). Extends `qca-bt-format.md`: what was one blob
(`bt.img`) is now four decoded containers.

## Container map (all four partitions probed)

| partition | bytes | container | contents |
|---|---|---|---|
| `bluetooth` → bt.img | 765,952 | FAT16, `IMAGE/` dir | 10 QCA BT patch/NVM fleet files (see qca-bt-format.md) |
| `modem` → modem.img | 119,820,288 | **FAT16**, `IMAGE/` dir | **404 named firmware files / 113.5 MB** — the whole OP6 firmware set (403 extracted; count corrected 2026-11-17 per raw FAT walk) |
| `tz` → tz.img | 2,056,192 | **ELF64 AArch64** QSEE (e_type 2, e_machine 183, 17 phdrs; two vaddr regions 0x14680000 + 0x1c000000; version strings TZ.XF.5.0.1.C5-00083.1 / WAXAANAAA / CRM) | TrustZone firmware — full segment map in dsp-tz-map.md |
| `dsp` → dsp.img | 33,554,432 | **ext4** (volume "dsp", 4,096 B blocks, clean 4 MiB journal) | 62 files: 57 Hexagon ELF32 fastrpc user-PD modules under /adsp /cdsp /sdsp (25.3 MB) + map .txt files — see dsp-tz-map.md |

Both FAT volumes share the layout family (MSDOS5.0 OEM, 4,096 B/sector,
4 sec/cluster) and both declare more sectors than the OTA writes (the
live tree fits in the written region) — a Qualcomm firmware-volume
convention worth flagging: **the modem and bluetooth partitions are
filesystems, not monolithic blobs; the dsp partition is ext4.** Upstream's
counting treats them as opaque; the extractable, nameable surface is ~40×
larger for this device.

## The modem.img IMAGE tree (404 entries, 403 extracted)

Groups (by name after the `image_` prefix): `modem.b16/b17/b20/b24`
(mpss Hexagon segments; b20 alone 26.3 MB) · `adsp.b00-b13` (18 MDT
segments) · `cdsp.b00-b10` · `slpi.*` · `mba.*` · `wlanmdsp.mbn`
(**3,035,876 B, md5 `771a9c2e…90df5` — the WCN3990 WiFi firmware;
resolves the wifi-family census-negative finding**) · **35 ×
`bdwlan.*`** (19,152 B each — WCN3990 board-data variants; format decoded,
see bdwlan-format.md) · `gfp9508.*` · `qdsp6m.qdb` (5.4 MB) ·
keymaster/cmnlib/cmnlib64 MDT sets · the DSP launch manifests
(`adspr.jsn`, `adspua.jsn`, `cdspr.jsn`, `modemr.jsn`…).

## Fleet joins: 201 md5 matches

Cross-checking all extracted file md5s against the committed coverage matrix
**yields 201 (device, md5) fleet matches** — e.g. `image_adspr.jsn`
equals the 31-device `adspr.jsn` fleet blob. The sha256↔md5 fleet join
(an open item in deep-re-notes §6, "needs payload access per device
family") is thereby **delivered for OnePlus 6 at fleet scale**: one
1.07 GB payload pins 201 multi-device blob identities.

## Consequences for the leverage plan

1. The wifi family's "structurally absent from vendor" finding is
   confirmed AND resolved: the firmware lives in `modem.img`'s FAT tree
   as `image_wlanmdsp.mbn` + `bdwlan.*` board data.
2. The `bm2nXX.bin` fleet question (OP6 comparison point) is answered
   two ways: the SDM845 generation ships per-DSP MDT/bNN segment sets as
   named files (`image_adsp.*`), AND the SM6375-generation `bm2nXX.bin`
   fleet md5s are now byte-verified from a real SM6375 payload (see
   second-device-larry.md — 6/6 exact).
3. Every segment file now has a name, size, and md5 — the OP6's modem/
   adsp/cdsp surfaces are census-complete (the deep-re-notes census of
   57 vendor files under-counted the real extractable surface by ~7×).

## Deliverables

- `tools/fat_extract.py` — used for both FAT volumes (bt.img, modem.img)
- `devices-001-222.csv` (+403 rows via the modem-FAT census, local,
  regenerable) — census now reflects the full extractable surface
- `docs/devices/oneplus6/{modem,wifi}.md` — upgraded to container-decoded
- Companion deep-dives: `dsp-tz-map.md` (ext4 + QSEE segment maps),
  `bdwlan-format.md` (board-data container), `qca-bt-format.md` (BT fleet),
  `patch-stream-structure.md` (patch/tail structure),
  `second-device-larry.md` (SM6375 population)

## Open items

1. `tz.img` QSEE metadata layout (seg[1] hash-table geometry, cert chain
   order) and the 3 embedded ELF magics inside fastrpc shells.
2. `bdwlan.*` tag 1..17 semantics (needs a Qualcomm BDF tool/spec — none
   public; the 35-variant diff and ID fields are mapped in bdwlan-format.md).
3. The remaining 202 non-fleet-joined modem-FAT files are OP6-specific
   blobs (expected — not every file is fleet-shared).

## Count-correction note (2026-11-17)

First pass recorded 403 extracted files and 37 bdwlan variants; the
subagent deep-pass verified 404 FAT directory entries (0 deleted) and 35
bdwlan files (29 md5 clusters). Both numbers here are corrected; the
403-vs-404 delta is one unresolved entry, flagged for the lead.
