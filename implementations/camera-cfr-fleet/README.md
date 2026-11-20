# camera-cfr-fleet — the `CFR_*` camera parameter blobs

A clean-room probe for the `CFR_*.bin` files found under
`vendor/etc/camera/`, `odm/etc/camera/cfr_bin/` and their subdirectories in
OnePlus and Xiaomi trees. These are camera tuning tables, not firmware.

## The main result

**`CFR_*` is not one format.** It is at least four distinct container
grammars that happen to share a filename prefix:

| class | size | discriminator | example |
|---|---:|---|---|
| `short-1079` | 1,079 | no ASCII magic; 3 records, stride 337 | `CFR_para.bin` |
| `mid-2126` | 2,126 | no ASCII magic; 3 records, stride 670 | `CFR_imx766.bin` |
| `tagged-3645` | 3,645 | `L12UW` at offset 8 | `CFR_para_UW_V01.bin` |
| `text-8128` | 8,128 | ASCII `CFR400 TUNING PARAMETER` at offset 0 | `CFR_dodgemain.bin` |

The `short` and `mid` classes share an identical 20-byte signature block at
offset 20 and the same `XX 00 01 02` record tag; they differ only in record
stride. The `tagged` class carries a lens-position string (`L12UW`) and a
related tag. The `text` class has a plain-text prologue and an explicit
filesize word at offset 68. Any tool that assumes one `CFR_*` grammar will
mis-parse three quarters of the family.

## Second result: the sensor names are not the data

`CFR_imx766.bin` and `CFR_imx766_uw.bin` — presented as two different sensor
configurations — are **byte-identical except for one byte at offset 4**
(`0x7a` vs `0x70`). So the two filenames do **not** correspond to distinct
calibration tables; a single module-identification field differs. By contrast,
the 8,128-byte `CFR_dodgemain.bin` / `CFR_dodgetele.bin` differ in 222 bytes
across 60 runs. The family encodes both extremes.

## Clean-room statement

Written 2026-11-20 from public tree listings and direct byte measurements:

- `TheMuppets/proprietary_vendor_xiaomi_diting` @ `lineage-22.2`
- `TheMuppets/proprietary_vendor_xiaomi_cupid` @ `lineage-22.2`
- `TheMuppets/proprietary_vendor_xiaomi_laurel_sprout` @ `lineage-22.2`
- `TheMuppets/proprietary_vendor_oneplus_dodge` @ `lineage-22.2`
- `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`

all via the public GitHub API tree endpoint (names and sizes) and raw payload
fetches (byte measurement). md5s were checked against
`research/laptop/sharing-clusters.csv` and
`upstream-contribution/blob-database/coverage-matrix.csv`. No proprietary
code, headers, documentation or artwork is committed.

Labels: **[M]** own measurement · **[S]** public source · **[OPEN]** not
established.

## RULE 0 prior art

Searxng (2026-11-20):

| query | outcome |
|---|---|
| `"CFR_para" camera calibration blob format` | **No results found** |
| `"L12UW" camera firmware` | Hikvision/Sony firmware download pages, unrelated |
| `CFR_dodgemain.bin` | device `proprietary-files.txt` manifests only |

GitHub code search (2026-11-20): `"eye_pupil.bin"`-style searches for these
names return `proprietary-files.txt` and `*-vendor.mk` build manifests, never
a format description. One public filename is a lead worth keeping:
`libalCFR_skel.so` under `vendor/lib/rfsa/adsp/` in the OnePlus tree — an ADSP
skeleton suggesting a consumer on the DSP side. No source for it is public.

No public writeup of any `CFR_*` container was found. **Publicly listed,
publicly undecoded** — the same verdict as `bm2n` and the render-effect
assets.

## Files

| file | role |
|---|---|
| `cfr_probe.py` | stdlib-only probe; class detection, tags, markers, JSON |
| `make_fixture.py` | deterministic synthetic fixtures for all four classes |
| `test_cfr_probe.py` | unittest suite |
| `fixtures/.gitignore` | excludes synthetic fixtures from git |
| `cfr-fleet-analysis.md` | full analysis |
| `../../research/laptop/oneplus-camera-cfr-family.md` | laptop-half summary |

## Usage

```bash
cd implementations/camera-cfr-fleet
python3 -I make_fixture.py
python3 -m unittest discover -q
python3 -I cfr_probe.py <file>.bin --brief
```

## Test status

11 tests passing. Fixtures regenerate byte-identically and match no vendor
md5. Full-tree clean-room scan against all 7,042 DB md5s: zero real payload
bytes staged.
