# MediaTek front — Xiaomi Redmi Note 10S (rosemary, Helio G95 / MT6785), LineageOS 24.0

MediaTek firmware research front (same methodology as `qualcomm-fp6/`:
architecture ID, segment maps, version strings, prior-art checks).

Content so far: `rosemary-census.md` — the first MTK device census (12
firmware partitions; the zero-ELF `mtk_hdr` container finding; ARCv2 CCU
identification) — plus decode follow-ups in `docs/` (`md1rom-decode.md`,
`md1dsp-decode.md`, `md32-gap.md`), machine results in `results/`, and
tooling in `tools/`. Headline findings are summarized in the repo-root
README's MediaTek section.

Families covered (from the rosemary census): `md1img` (modem: md1rom
MIPS32+MIPS16e per F-31, md1dsp MD32-class per F-36 with the decode-gap
diagnosis in F-45), `scp` (Cortex-M4F + FreeRTOS), `sspm` (encrypted),
`spmfw` (SPM/PCM microcode), `audio_dsp` (HiFi3/Xtensa, name-level),
`cam_vpu*` (ARM32 Thumb-2), CCU (ARCv2). No `mcupm`, `dpm`, `vcp`, or
`piimg` partitions exist on this device.
