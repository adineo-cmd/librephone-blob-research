# OnePlus 6 (enchilada) — Modem family

**Evidence class: format-spec** (container decoded 2026-11-17; per-file
census with fleet md5 joins).
Source: LineageOS 22.2 nightly 2026-11-11 enchilada, OTA payload partition
`modem` → `modem.img` (119,820,288 B, sha256 in the matrix CSV).
52 REPLACE_XZ + 5 REPLACE_BZ + 1 REPLACE ops reconstructed it from the OTA.

## Container layout (DECODED 2026-11-17)

`modem.img` (119,820,288 B) is a **FAT16 volume** (BPB: 4,096 B/sector,
4 sec/cluster, 2 FATs × 4 sectors) whose `IMAGE` directory carries **403
named firmware files / 113.5 MB** — the full OP6 firmware set laid bare:
`image_modem.b16/b17/b20/b24` (the mpss Hexagon segments, largest 26.3 MB),
`image_adsp.*` (18 segments incl. 7.1 MB b10), `image_cdsp.*`,
`image_slpi.*`, `image_wlanmdsp.mbn` (the WCN3990 WiFi firmware),
37 × `image_bdwlan.*` WCN3990 board-data variants, `image_gfp9508.*`,
`image_qdsp6m.qdb`, `image_mba.*`, keymaster/cmnlib/cmnlib64 MDT sets, and
the DSP launch manifests. **201 of the 403 files md5-join to multi-device
fleet blobs in the committed matrix** — the sha256↔md5 fleet join that was
an open item is now delivered at scale from this one device (see
`blob-matrix/desktop/fleet-re/oneplus6-partition-map.md`).

## Fragmentation significance

modem is the largest byte-weighted family across the whole matrix
(25.94 GB of 69.80 GB). Every SDM845-generation device in the half shares
this shape — and, as demonstrated here, that shape is a FAT firmware
volume, not a monolithic blob. The lab's FP6 modem findings (F-19/F-26:
b23/b24 segments, q6zip-suspected opaque bodies) map onto named segment
files at this generation: `image_modem.b20` (26.3 MB) and friends are the
directly comparable units.

## ISA/proof status

Segment files not decoded (ISA unknown at file granularity; the lab's
Hexagon decode recipe — papers/wmi-dispatch-architecture.md §6 — applies
once a target segment is chosen).

## Interface facts

Consumers: QRTR/DIAG/peripheral-image loader (mainline `qcom_q6v5_mss`
PIL driver loads this partition on sdm845 — public code); QMI/RIL above.
The FAT tree makes per-file interface attribution tractable (file name =
PIL image name).

## Open questions

- per-segment ISA/e_machine confirmation for the modem.bNN set
- q6zip-suspected compressed bodies (F-26 method) against the named files
- dsp.img's 60 Hexagon ELFs (see partition-map open items)
