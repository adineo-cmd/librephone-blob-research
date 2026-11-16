# OnePlus 6 (enchilada) — ADSP family

**Evidence class: census** (files extracted + hashed; container magics recorded; no
ISA decode). Source: LineageOS 22.2 nightly 2026-11-11 enchilada, partition `vendor`
(`/vendor/lib/rfsa/adsp`, 24 files) + partition `dsp` (33,554,432 B raw image).

## Container layout

- `/vendor/lib/rfsa/adsp/*.so` — 24 Hexagon shared objects, all magic
  `elf32-le`: compute/audio/sensor DSP skel libraries (`libfastcvadsp.so`
  1,277,032 B, `libhexagon_nn_skel.so` 1,177,940 B, `libFastRPC_UTF_Forward_skel.so`
  963,716 B, `libfastcvdsp_skel.so` 639,952 B, `libdirac-capiv2.so` 370,468 B,
  `libscveT2T_skel.so`, `libdepthmap_skel.so`, `libVC1Dec.so`, `libVC1DecDsp_skel.so`,
  aptX/HD capi_v2 codecs, dirac resource `.dar`, sns_* sensors, dspCV, halide
  remote, morpho HVX, thread blur, apps_mem_heap, dsp_streamer).
- Partition `dsp` (33,554,432 B, magic raw) — the ADSP PIL image itself
  (the `adsp` boot image; upstream's 23-partition manifest carries no separate
  `adsp` name on enchilada, the partition is named `dsp`).

## Fragmentation significance

This is the OP6-side sibling of recon.md top-20 #7-#13 (the `bm2nXX.bin`
ADSP-region fleet, 25-26 devices, 0.8-3.1 MB each, typed `MODEM` upstream but
living in `vendor/lib/rfsa/adsp`). OnePlus 6 (SDM845) carries named `.so`
DSP libraries instead of the `bm2nXX.bin` naming of the SM6xxx generation —
same family, different file-naming generation. The `bm2n` fleet RE would
benefit from this device as a second-generation comparison point: both are
Hexagon ELF shared objects on the same DSP.

## ISA/proof status

The `.so` files are standard ELF32 little-endian Hexagon QDSP6 shared
objects (magic `elf32-le` recorded per file; full e_machine check not run
this session — expected 164/EM_QDSP6 per the lab's wpss finding; verify in
a follow-up). No decode.

## Interface facts

Consumers: FastRPC user→DSP calling convention (public: `libadsprpc` /
`fastrpc` mainline kernel driver); each `_skel.so` is the DSP-side skeleton
of an interface whose host side ships in the vendor APK/lib set. No
per-file interface doc committed yet.

## Open questions

- e_machine confirmation per file (one hexdump pass)
- `dsp` partition image container type (raw PIL header vs ELF MDT — magic
  probe says raw 16-byte head; parse its header next session)
- which of these files are shared fleet-wide (needs cross-device payloads)
