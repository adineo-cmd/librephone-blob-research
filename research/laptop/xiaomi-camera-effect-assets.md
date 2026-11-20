# Xiaomi camera render-effect assets

Laptop-half summary of `implementations/camera-effect-fleet/`.

## Identity

These are **not firmware**. They are camera retouch masks and colour textures
under `vendor/etc/camera/resources/render/Effect/`, consumed by the vendor
camera render pipeline. `eye_pupil.bin` is a bright-eye effect mask;
`sh.bin` is a makeup effect asset. The reverse-engineering target is the
container, not the artwork.

## Container — 35/35 exact

```
u32 width | u32 height | u32 4 | u32 1 | u32 0 | u32 99 | u32 0
u8 payload[width * height * 4]
```

`filesize == 28 + width * height * 4` with **zero slack on all 35 files**
in the `Effect/` tree of `proprietary_vendor_xiaomi_diting` @ `lineage-22.2`
(sizes 4,124 B to 6,000,028 B). Fields at `0x08`/`0x0c`/`0x10`/`0x14`/`0x18`
are constant across the entire fleet at `4`, `1`, `0`, `99`, `0`.

## Payload classes

Measured by channel identity, not filename: 6 greyscale masks, 10 colour
textures, 19 mixed. `eye_pupil.bin` is 150×150 greyscale with an opaque fourth
channel; `sh.bin` is 709×278 with a fourth channel ranging 0–35. Channel order
(BGRA / RGBX / RGBA) is `[OPEN]` — no public loader found.

## Fleet evidence

Tree and payloads fetched 2026-11-20. 9 of 35 md5s are members of
`research/laptop/sharing-clusters.csv`; the rest are single-tree assets. All
35 fit the grammar and pass the canonical-header check.

RULE 0: Searxng and GitHub code search both found only `proprietary-files.txt`
build manifests (722 hits for `"eye_pupil.bin"`, 334 for
`"FacialSmoothMask_first"`, 249 for `"SkinDetial.bin"`). **Publicly listed,
publicly undecoded** — the same result as `bm2n`.

## Status

Component passing: 11 tests, deterministic synthetic fixtures, zero collisions
against the 7,042-md5 DB. Full analysis:
`implementations/camera-effect-fleet/camera-effect-analysis.md`.
