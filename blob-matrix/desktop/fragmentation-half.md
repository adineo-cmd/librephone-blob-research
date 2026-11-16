# Desktop half — device fragmentation analysis (Phase 4, merge-ready)

Rows 1–222 of the 249-identity universe (split rule in
[deep-re-notes.md](deep-re-notes.md) §1). All numbers from the committed
coverage matrix + device inventory, codename-joined; the OnePlus 6
payload census is included where noted. 2026-11-16.

## 1. SoC generations (222 devices)

- **Qualcomm: 89 named** across 29 chip generations (SM6375 ×12, SM8250
  ×7, SM8475 ×3, SM6115 ×5, SM7250 ×5, SM8550 ×3, SM4250 ×3, SM6225 ×4,
  SM7325 family ×5, SDM845 ×4, SM8350 family ×4, MSM8998 ×2, plus
  singles: QCM6490, SDM636, SM8150 family ×2, SM4375, SM4350, SM8475,
  SM7225, SM7325-AE variants)
- **Google Tensor: 14** (GS101 ×3, GS201 ×5, G3 ×5, G4 ×1)
- **Other named: 3** (Amlogic S905Y2/S905X3 TV boxes)
- **Blank SOC: 116** — the upstream DB's biggest fragmentation-data hole
  (concentrated on Samsung/Motorola/Xiaomi rows where `builds.csv` never
  filled the cell)

SoC-vendor split of the 110 populated devices: Qualcomm 89, Google 14,
other 3, blank 4.

## 2. Family sharing (blobs shared across the most devices)

Corrected leverage ranking (in-half device counts; md5-keyed):

1. `oplus_vooc_fw_rk826.bin` + `oplus_vooc_fw.bin` — **36 devices each**
   (VOOC fast-charge firmware, OnePlus+realme rows only)
2. QCA BT patch fleet (`crbtfw20.tlv`, `apbtfw10.tlv`, `crbtfw11.tlv`,
   `crnv20.bin`, `crnv11.bin`, `apnv10.bin`) — **29 devices each**
3. `bm2n06/08/12/13/14/15.bin` (ADSP-region fleet) + `sequence_manifest.bin`
   + `unified_ksqs.bin` — 22 each in half (25-26 fleet-wide)
4. `a619_gmu.bin` — 21; `a660_sqe.fw` — 20; `a660_gmu.bin` — 18;
   `a630_sqe.fw` — 16; `aoa_cldb_falcon.bin`/`aoa_cldb_swl14.bin` — 16

Shared-blob histogram in the half (16,063 distinct blobs keyed by
filename+md5, size-as-proxy where the upstream DB lists no md5):
10,759 on 1 device · 2,095 on 2 · 693 on 3 · 1,112 on 4 · 223 on 5 ·
… down to 7 blobs on 29 and 7 on 30 devices (the BT fleet and VOOC
pair). **5,304 distinct blobs (33.0%) are shared by ≥2 devices, and
22,137 of 33,481 rows (66.1%) are instances of a shared blob** —
consistent with recon.md's fleet-wide 68.0%.

## 3. Family × device coverage

| family | devices carrying it (of 110 populated) |
|---|---|
| boot | 110 |
| other (camera/touch/audio long tail) | 107 |
| modem | 101 |
| wifi | 95 |
| gpu | 92 |
| tz | 79 |
| bt | 73 |
| adsp | 68 |
| cdsp | 63 |

92 of 110 populated devices carry ≥5 families — the modern
(SDM660-and-later) shape; the pre-2018 devices carry fewer.

## 4. Byte-weighted fragmentation

Top devices by enumerated bytes (halving the corpus is concentrated at
the top): Nord_4 1.94 GB · OnePlus_12 1.87 · OnePlus_11_5G 1.60 ·
Mi_13_Pro 1.48 · Mi_13 1.46 · Poco_F6_PRo 1.42 · Mi_12S_Pro 1.41 ·
Nord_CE4 1.40 · Mi_12S_Ultra 1.39 · Mi_12S 1.39 · Poco_F5_Pro 1.31 ·
Edge_40_Pro 1.30 · Mi_12T_Pro 1.30 · OnePlus_13 1.23 · Redmi_K60_Pro
1.14. All 15 are 2021-2024 SM8-series/SM7-series flagships — byte
weight tracks SoC generation, and the OnePlus/oxygen ecosystem alone
accounts for ~9 of the top 15.

By family (half): modem 25.94 GB · boot 22.05 GB (of which the
free-kernel boot.img/vendor_boot rows are a large upstream-mislabeled
share — see recon.md's family-note) · other 14.15 GB · adsp 3.49 GB ·
wifi 0.71 GB · tz 0.67 GB · cdsp 0.28 GB · bt 0.12 GB · gpu 0.09 GB.

## 5. Merge notes for the lead (444 → 249 reconciliation)

1. The laptop-flagged remainder is rows 223–249: 27 devices, all
   X*/Z*-named — 12 Sony Xperia (incl. 12 of the 123 populated), Nubia
   Z17/Z18/Z5_Pro_GT/Z6_Pro, Zenfone 5Z/8, Zero TV/tablet boxes.
   Nothing in the top-20 leverage list lands there.
2. Split rule to re-derive identically: sort `device-inventory.csv` by
   `model` (fallback `build_codename`), plain codepoint, desktop rows
   1–222, laptop 223–249. Codename-join to the matrix via `db_path`
   (NOT display name — the `Phone_2`/aura/`Pong` collision, see
   deep-re-notes §2).
3. Upstream-matrix data quality to fix at merge: 586 true duplicate
   (device, filename, md5) triples; duplicate display names `Xperia_1_II`
   (two codenames) and `Phone_2` (aura + Pong); typo `Poco_F6_PRo`;
   stray `\ufffd` byte in one SOC cell.
4. The OnePlus 6 census rows (57, sha256-bearing,
   `populated-local-session`) merge cleanly: device `OnePlus_6`,
   vendor `OnePlus`, soc `Qualcomm SDM845 Snapdragon 845`.

## 6. What the merge enables

Desktop half + laptop half = the full 444→249 device picture at the
same evidence level; the corrected leverage ranking applies fleet-wide
(VOOC pair 36, BT fleet 29 — both fully inside desktop rows), and the
Phase-3 clean-room components cover the transport/dispatch layer shared
by every Qualcomm device in both halves.
