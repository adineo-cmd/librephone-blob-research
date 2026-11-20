# Xiaomi camera render-effect assets — structural analysis

Scope: the 35 `.bin` files under
`proprietary/vendor/etc/camera/resources/render/Effect/` in
`TheMuppets/proprietary_vendor_xiaomi_diting` @ `lineage-22.2` (tree fetched
2026-11-20; payloads fetched from `raw.githubusercontent.com` the same day).
All 35 were measured; md5s were checked against
`research/laptop/sharing-clusters.csv`.

## 1. The container — fully specified

The entire file is:

```
u32 width
u32 height
u32 4            bytes per pixel      (35/35)
u32 1            plane count          (35/35)
u32 0            reserved             (35/35)
u32 99           format constant      (35/35)
u32 0            reserved             (35/35)
u8  payload[width * height * 4]
```

There is no trailing data. The arithmetic
`filesize == 28 + width * height * 4` is exact on **35 of 35** files, with
slack zero in every case. Sizes range from 4,124 B (`nose.bin`, 32×32) to
6,000,028 B (`FaceMask.bin`, 1000×1500).

This is a deliberately minimal design. The loader already knows the dimensions
from the header, so a length field and a trailer are both redundant. Contrast
with the three firmware container philosophies already on record:

| family | length field | loader parses? |
|---|---|---|
| QCA BT gen-1 (F-75) | `4 + 24 + len + 256` | TLV container |
| QCA BT gen-2 | `4 + 32 + len + 36`, SHA-256 trailer | TLV container |
| MSM CPP firmware | none | **nothing** — streams `fw->size/4` words |
| camera render-effect assets | none | dimensions from header, raw pixel copy |

The effect assets are the fourth answer: no length field, but the header is not
opaque either — it carries enough structure to size the copy.

## 2. Fleet inventory

`DB` is membership in `research/laptop/sharing-clusters.csv`. A `-` means the
file is present in this one tree but is not a shared cluster (no cross-device
duplication recorded), **not** that the fetch failed. All 35 fetched.

| file | bytes | W×H | pixel class | DB |
|---|---:|---|---|:-:|
| Eyebrow.bin | 127,628 | 290×110 | grayscale-mask | Y |
| eye_pupil.bin | 90,028 | 150×150 | grayscale-mask | Y |
| eye_refine.bin | 17,968 | 115×39 | mixed | - |
| facelift.bin | 242,028 | 250×242 | mixed | - |
| facelift.bin (variant) | 244,932 | 253×242 | mixed | - |
| FaceMask.bin | 1,382,428 | 480×720 | grayscale-mask | - |
| FaceMask.bin | 3,895,952 | 901×1081 | mixed | - |
| FaceMask.bin | 6,000,028 | 1000×1500 | grayscale-mask | - |
| FacialSmoothMask_first.bin | 241,144 | 283×213 | mixed | - |
| FacialSmoothMask_second.bin | 241,144 | 283×213 | mixed | - |
| filter.bin | 1,048,604 | 512×512 | color-texture | - |
| LeftEye.bin | 360,028 | 300×300 | mixed | Y |
| left_eye.bin | 360,028 | 300×300 | mixed | Y |
| nose.bin | 4,124 | 32×32 | mixed | - |
| right_eye.bin | 360,028 | 300×300 | mixed | Y |
| RightEye.bin | 360,028 | 300×300 | mixed | Y |
| sh.bin | 788,436 | 709×278 | mixed | Y |
| SkinDetial.bin | 4,194,332 | 1024×1024 | grayscale-mask | - |
| xr.bin | 3,895,952 | 901×1081 | mixed | - |
| yyy.bin | 360,028 | 300×300 | color-texture | - |
| yyz.bin | 360,028 | 300×300 | color-texture | - |
| zc.bin | 144,028 | 300×120 | color-texture | - |

Note the `LeftEye.bin`/`left_eye.bin` and `RightEye.bin`/`right_eye.bin` pairs:
within this tree they are byte-identical in name-insensitive terms (same size,
same dimensions, both DB-shared). This is a **filename case** duplication, the
same "filename ≠ identity" phenomenon seen in `a650_sqe.fw` and the QCA BT
fleet. `[OPEN]` whether one is a stale copy or the two paths are bound by
different effect configurations.

## 3. Pixel payload classes — measured, not inferred from names

Classification uses per-channel identity: the percentage of pixels where
channel 0 equals channel 1, and channel 1 equals channel 2.

| class | rule | count |
|---|---|---:|
| `grayscale-mask` | ch0≡ch1 and ch1≡ch2 at exactly 100% | 6 |
| `color-texture` | both identities < 50% | 10 |
| `mixed` | anything between | 19 |

Per-file examples (**[M]**, full statistics in `effect_probe.py` JSON output):

| file | ch0≡ch1 | ch1≡ch2 | channel 4 range | reading |
|---|---:|---:|---|---|
| `eye_pupil.bin` | 100.0% | 100.0% | 255 only | greyscale mask with opaque fourth channel |
| `Eyebrow.bin` | 100.0% | 100.0% | 255 only | greyscale mask, values 0–128 |
| `FaceMask.bin` (1000×1500) | 100.0% | 100.0% | 255 only | large greyscale mask |
| `SkinDetial.bin` | 100.0% | 100.0% | 255 only | large greyscale mask |
| `filter.bin` | 0.9% | 0.8% | 255 only | true-colour 512×512 texture |
| `sh.bin` | 32.4% | 62.8% | 0–35 | three busy channels plus a low-range fourth |
| `nose.bin` | 100.0% | 42.5% | 97–130 | two channels identical, two correlated |

The constant fourth channel on the masks is consistent with BGRA with alpha
fixed at 255. It is equally consistent with RGBX and with an unused padding
byte. **`[OPEN]` — the channel order is not established.** No public loader
was found (§5), and there is no header field that varies with the observed
classes: `bpp=4`, `planes=1` and `magic=99` are identical on greyscale masks,
colour textures and mixed files alike. So the class is a property of the pixel
data, and cannot be predicted from the header.

`sh.bin` deserves a specific note because it was the second file in the
original lead. Its fourth channel takes 36 distinct values in the range 0–35,
while its first pixel is `ff ff ff 00`. If that channel is alpha, this is a
near-transparent overlay; if it is a weight map, it is a low-amplitude
modulation. Both readings fit a makeup effect. **Do not assert which.**

## 4. What this buys

- The container is **completely specified** for the purpose of a free
  implementation: any decoder can consume all 35 files with no `[OPEN]` in
  the framing logic. That is a real deliverable even though the artwork stays
  proprietary.
- The format is **not firmware**. Treating these as executable blobs would
  be a category error in the lab's coverage matrix; they belong in the asset
  column, alongside HRTF/DAX data rather than the GMU/SQE microcode.
- The case-duplication pair and the existence of three `eye_refine.bin` copies
  with one shared md5 give concrete targets for the "filename ≠ identity"
  theme already established elsewhere.

## 5. `[OPEN]` register

1. **Channel order** — BGRA vs RGBX vs RGBA; no public loader found. Bounded:
   it is a four-byte-per-pixel layout with a constant or low-range fourth
   channel on most assets.
2. **Meaning of `magic = 99`** — constant on all 35. Version? format tag?
   Bounded to a single u32 at `0x14`.
3. **Meaning of `planes = 1`** — no file in this tree has any other value, so
   the field is untested. A different vendor tree may exercise it.
4. **Consumer** — no public render-pipeline source reads these paths. A
   sibling `effect.json` exists in each effect directory; whether it names
   the `.bin` and supplies the channel semantics is unexamined here (and no
   bytes from it are committed).
5. **The low-range fourth channel of `sh.bin`** — alpha or weight?
6. **Case-duplicate eye files** — intentional or stale.

## 6. Reproduce

```bash
cd implementations/camera-effect-fleet
python3 -I make_fixture.py
python3 -m unittest discover -q
python3 -I effect_probe.py /tmp/work/effect_bins/eye_pupil.bin --brief
```

Real payloads are kept outside the repo and are never committed.
