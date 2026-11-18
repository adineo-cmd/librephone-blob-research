# hbt-fleet — the h-prefix (Hastings-class) QCA Bluetooth fleet

Fleet-level RE of the `hpbtfw20.tlv` / `hpnv20*` Bluetooth files — the
QCA2066/Hastings-generation rampatch + NVM pair the mainline `btqca.c`
loads (and the sibling of the F-75 cr/ap fleet in
`implementations/qca-bt/`). Method: fetch individually from public vendor
trees → md5-verify against `upstream-contribution/blob-database/
coverage-matrix.csv` → parse with the unmodified lab parser
(`qca-bt/qca_tlv.py`) plus `fleet_diff.py` (this dir) → document per byte
range with [OPEN] markers. No payload bytes are committed.

## Contents

- `hpbtfw20-analysis.md` — rampatch: header fields, 44-byte footer format,
  body statistics, chip-identity resolution (QCA2066/Hastings), md5 table,
  route log.
- `hpnv20-analysis.md` — NVM: bare type-2 layout, full 61-tag map of the
  DB build, cross-generation tag diff vs cr/ap, cross-build identity
  (44/61 shared tag contents), bXX board variants, the GlobalFoundries
  `g` variant.
- `devices.csv` — the laptop-half carrier devices (10), their vendors,
  codenames, SoCs, md5s, bXX variant counts.
- `fleet_diff.py` — structural diff tool (patch footer classes, NVM
  layout/tag census, cross-file tag identity). Fixtures-tested.
- `make_fixture.py` + `test_hbt_fleet.py` — synthetic fixtures built from
  the documented structures only; run `python3 -I test_hbt_fleet.py`.

## md5 status (2026-11-18)

hpbtfw20.tlv common build (`92247344…`, 9 devices) **MATCH** via cupid
bluetooth partition image (XiaomiFirmwareUpdater firmware zip →
`bluetooth.img` → `/image/hpbtfw20.tlv`); hpnv20.bin (`5de36001…`) and
hpnv20g.bin (`12cd1ff0…`) **MATCH** from the same image. FP5's own builds
(184,740 / 6,307 B) remain provenance-[OPEN] — Fairphone's stock OTA
carries the bluetooth partition but no public tree hosts it yet.
