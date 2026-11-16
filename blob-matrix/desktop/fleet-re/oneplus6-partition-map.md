# OnePlus 6 partition map decoded — bt.img, modem.img, tz.img, dsp.img (fleet-re, 2026-11-17)

**Evidence class: format-spec** (container layer; per-file census with
matrix md5 joins). Extends `qca-bt-format.md`: what was one blob
(`bt.img`) is now three decoded containers plus one mapped one.

## Container map (all four partitions probed)

| partition | bytes | container | contents |
|---|---|---|---|
| `bluetooth` → bt.img | 765,952 | FAT16, `IMAGE/` dir | 10 QCA BT patch/NVM fleet files (see qca-bt-format.md) |
| `modem` → modem.img | 119,820,288 | **FAT16**, `IMAGE/` dir | **403 named firmware files / 113.5 MB** — the whole OP6 firmware set |
| `tz` → tz.img | 2,056,192 | **ELF64 AArch64** (e_type 2, e_machine 183, 17 phdrs: PT_LOAD RX/W segments = QSEE image) | TrustZone firmware |
| `dsp` → dsp.img | 33,554,432 | raw; first ~4.7 MB zero, then **60 Hexagon ELF32 blobs** (e_machine 164) from 0x48f000 | ADSP-adjacent payload, unparsed individually |

Both FAT volumes share the layout family (MSDOS5.0 OEM, 4,096 B/sector,
4 sec/cluster) and both declare more sectors than the OTA writes (the
live tree fits in the written region) — a Qualcomm firmware-volume
convention worth flagging: **the modem and bluetooth partitions are
filesystems, not monolithic blobs.** Upstream's per-device counting
treats them as opaque; the extractable, nameable surface is ~40× larger
for this device.

## The modem.img IMAGE tree (403 files)

Groups (by name after the `image_` prefix): `modem.b16/b17/b20/b24`
(mpss Hexagon segments; b20 alone 26.3 MB) · `adsp.b00-b13` (18 MDT
segments) · `cdsp.b00-b10` · `slpi.*` · `mba.*` · `wlanmdsp.mbn`
(**3,035,876 B, md5 `771a9c2e…90df5` — the WCN3990 WiFi firmware;
resolves the wifi-family census-negative finding**) · **37 ×
`bdwlan.*`** (19,152 B each — WCN3990 board-data variants keyed by
board ID) · `gfp9508.*` · `qdsp6m.qdb` (5.4 MB) · keymaster/cmnlib/
cmnlib64 MDT sets · the DSP launch manifests (`adspr.jsn`,
`adspua.jsn`, `cdspr.jsn`, `modemr.jsn`…).

## Fleet joins: 201 md5 matches

Cross-checking all 403 file md5s against the committed coverage matrix
**yields 201 (device, md5) fleet matches** — e.g. `image_adspr.jsn`
equals the 31-device `adspr.jsn` fleet blob; `image_cdSpr.jsn` the
30-device one. The sha256↔md5 fleet join (an open item in
deep-re-notes §6, "needs payload access per device family") is thereby
**delivered for OnePlus 6 at fleet scale**: one 1.07 GB payload pins
201 multi-device blob identities.

## Consequences for the leverage plan

1. The wifi family's "structurally absent from vendor" finding is
   confirmed AND resolved: the firmware lives in `modem.img`'s FAT tree
   as `image_wlanmdsp.mbn` + `bdwlan.*` board data.
2. The `bm2nXX.bin` fleet question (OP6 comparison point) is answered:
   the SDM845 generation ships per-DSP MDT/bNN segment sets as named
   files — the `bm2nXX.bin` naming belongs to the SM6xxx generation,
   same mechanism, different packaging (as hypothesized in adsp.md).
3. Every segment file now has a name, size, and md5 — the OP6's modem/
   adsp/cdsp surfaces are census-complete (the deep-re-notes census of
   57 vendor files under-counted the real extractable surface by ~7×).

## Deliverables

- `tools/fat_extract.py` — used for both volumes (bt.img, modem.img)
- `devices-001-222.csv` (+403 rows via the modem-FAT census, local,
  regenerable) — census now reflects the full extractable surface
- `docs/devices/oneplus6/{modem,wifi}.md` — upgraded to container-decoded

## Open items

1. `dsp.img`: identify each of the 60 Hexagon ELFs (offset, size,
   entry — one parse pass; likely the adsp split-bin set laid raw).
2. `tz.img` QSEE segment map (17 phdrs listed, contents not parsed).
3. `bdwlan.*` board-data format (19,152 B fixed-size records — likely
   per-board calibration tables; a diff across the 37 variants is the
   natural next probe).
4. The remaining 202 non-fleet-joined files are OP6-specific blobs
   (expected — not every file is fleet-shared).
