# `CFR_*` camera parameter blobs — structural analysis

Payloads fetched 2026-11-20 from public OnePlus/Xiaomi vendor trees and
measured locally. md5s were cross-checked against
`research/laptop/sharing-clusters.csv` and
`upstream-contribution/blob-database/coverage-matrix.csv`. All payloads stay
in `/tmp`; none is committed.

## 1. The name hides four formats

The upstream database records 112 `CFR_*` rows spanning five distinct sizes:
1,079 / 2,126 / 3,645 / 8,128 / 5,776,288 bytes. The last is
`alCFR_Segmodel.bin` — a different artefact entirely (a model, paired with
the public `libalCFR_skel.so`) and is out of scope here.

Representatives of the four real classes were fetched:

| file | bytes | md5 | DB | source tree |
|---|---:|---|:-:|---|
| `CFR_para.bin` | 1,079 | `1a162c7a9aa3fc9272893a217c15aa04` | Y | xiaomi_laurel_sprout @ lineage-22.2 |
| `CFR_imx766.bin` | 2,126 | `eb6fd75e5a61891bbb5cc84d062e8358` | Y | oneplus sm8350-common @ lineage-19.1 |
| `CFR_imx766_uw.bin` | 2,126 | `b47bb7860e8ba75951dd974a8b3e3c57` | Y | same |
| `CFR_s5k3m5.bin` | 2,126 | `a655281a294146bcbe1f150cfd2a34d2` | Y | same |
| `CFR_OPlus_EF017_UW_snapshot.bin` | 2,126 | `99593358b2191db96a1bb63dcbe97b54` | Y | oneplus_dodge @ lineage-22.2 |
| `CFR_para_UW_V01.bin` | 3,645 | `6e99e58fb4dd8d0c5b041ad7febcdbd0` | Y | xiaomi_diting @ lineage-22.2 |
| `CFR_dodgemain.bin` | 8,128 | `30b4728a65d39f168b87a84ae313462c` | - | oneplus_dodge @ lineage-22.2 |
| `CFR_dodgetele.bin` | 8,128 | `5f0a2bf84a8e1fe429ab20db50f977ca` | - | same |
| `CFR_dodgeultrawide.bin` | 8,128 | `7bfce3fe3620dd59347be982c8db408b` | - | same |

The `short` and `mid` classes were also confirmed in `proprietary_vendor_oneplus`
@ `lineage-19.1` and `proprietary_vendor_xiaomi_diting`/`_cupid` @
`lineage-22.2` (five 3,645-byte files each).

## 2. Class grammars

### 2.1 `short-1079` and `mid-2126`

Both begin with four u32 LE words, then a **20-byte signature block at offset
20 that is byte-identical between the two classes**:

```
offset 00: u32  width/identity   (0x8c short, 0x96 mid)
offset 04: u32  module id        (0x51 short; 0x177a/0x1770/0x1784/0x7d0 mid)
offset 08: u32  0x20             (32)
offset 0c: u32  data length      (0x413 short, 0x7fa mid)
offset 14: 20-byte signature: 00 00 00 00 03 00 00 00 00 02 00 00 00 00 00 00 00 00 00 00
offset 28: record stream, each record tagged XX 00 01 02
```

Three tagged records were found in each class:

| class | tag offsets | stride | first tag | later tags |
|---|---|---|---|---|
| `short-1079` | 40, 377, 714 | 337 | `0x46` | `0x32`, `0x32` |
| `mid-2126` | 40, 710, 1380 | 670 | `0x5A`/`0x64`/`0x19` | `0x64`, `0x64` |

`[M]` via `cfr_probe.py`. The first tag varies between files while later tags
are stable in the `mid` class, which suggests the first record is a
file-specific header and the other two are shared tables. **That is a
hypothesis, not a decoded fact — `[OPEN]`.**

Note the arithmetic does not close on a simple `header_count × record_size`
model: the `mid` data-length word is 2,042, but 2,126 − 2,042 = 84, and the
three records span 40..2,050. The remaining 76 bytes are unaccounted for.
**Do not assert a record layout beyond the measured tag offsets.**

### 2.2 `tagged-3645`

The first 36 bytes are unique to this class:

```
u32[0] = 200
u32[1] = 96
u32[2] = 0x5532314c  -> "L12U"
u32[3] = 87
u32[4..8] = 0
offset 08..16: ASCII "L12UW"
```

The signature marker `03 00 00 00 00 02 00 00` appears at offset **52**, i.e.
28 bytes later than in the `short`/`mid` classes — so this class has a longer
prologue before the shared record machinery. Tagged `XX 00 01 02` records were
found at offsets 104, 780, 967, 1223, 1899 and 2086 (six, not three).

The `L12UW` string is the strongest family-identity evidence: `L12` plausibly
a lens/version index and `UW` **ultra-wide**, matching the `UW` in the
filename `CFR_para_UW_V01.bin`. Corroboration: sibling files in the same
directory are `CFR_para_W_V03.bin` (W = wide) and `CFR_para_W_V03_4x.bin`.
**`[OPEN]`:** a `W`-class file has not yet been byte-compared to confirm a
corresponding `L12W` magic. The probe detects the magic but does not claim its
semantics.

### 2.3 `text-8128`

Plain-text prologue at offset 0:

```
offset 00: "CFR400 TUNING PARAMETER"
offset 20: "AC090 W "
offset 40: 00 02 00 00   (512)
offset 44: c0 1f 00 00   (8128 == filesize)   <-- explicit length word
offset 48: 03 00 00 00
```

This is the only class with an explicit filesize field. The `03` at offset 48
echoes the third field of the shared signature block in the other classes, but
the surrounding bytes differ, so no common grammar is claimed.

`CFR400` is a version tag; `AC090 W` plausibly names the sensor module and
lens position. `[OPEN]` whether that field is a string or a fixed-width
identifier.

## 3. Sensor part numbers in filenames: only weakly corroborated

The filenames look authoritative — `imx766`, `s5k3m5`, `imx581`, `lyt808`,
`ov64b40_tele` are real camera sensor part numbers — so the obvious
hypothesis is one distinct calibration table per sensor/lens combination.
The bytes do not support that cleanly.

| pair | equal bytes | differing runs | reading |
|---|---:|---:|---|
| `CFR_imx766.bin` vs `CFR_imx766_uw.bin` | **2,125 / 2,126** | **1** | one byte at offset 4: `0x7a` vs `0x70` |
| `CFR_imx766.bin` vs `CFR_s5k3m5.bin` | 2,022 / 2,126 | 38 | genuinely different tables |
| `CFR_dodgemain.bin` vs `CFR_dodgetele.bin` | 7,906 / 8,128 | 60 | genuinely different tables |
| `CFR_dodgemain.bin` vs `CFR_dodgeultrawide.bin` | 7,893 / 8,128 | 46 | genuinely different tables |

So the family does encode sensor identity, but **`imx766` and `imx766_uw`
share the same 2,126-byte table except for a single module-ID byte**. The
`_uw` filename does not denote a separate calibration table. Any census that
counts these as two independent configurations is double-counting.

The variant with sensor part number `s5k3m5` differs in 104 bytes across 38
runs, so at that level the filenames *are* corroborated.

## 4. What this buys

- A tool can now classify any `CFR_*` file by its first 44 bytes and selects
  the right parse path. That is the prerequisite for a free camera-tuning
  reader.
- The four-class split explains why a single "CFR parser" cannot work and
  gives the exact discriminators.
- The one-byte `imx766`/`imx766_uw` result is a concrete correction to any
  fleet-level count built from filenames alone.
- `libalCFR_skel.so` is a named public lead for the consumer; if its public
  sibling `alCFR_Segmodel.bin` is ever documented, these tables may become
  readable end to end.

## 5. `[OPEN]` register

1. Record semantics — the `XX 00 01 02` tag and the bytes that follow.
   Bounded to three (or six) fixed offsets per class.
2. The 76-byte tail of the `mid` class and the 28-byte tail of `short`.
3. What `u32[0]` and `u32[1]` mean in `short`/`mid`; `u32[1]` correlates with
   sensor identity but is not proven to be a sensor ID.
4. Whether a `W`-class 3,645-byte file carries `L12W` at offset 8.
5. Whether `CFR400`/`AC090 W` in the text class are semantic identifiers.
6. Whether `libalCFR_skel.so` (ADSP) is the consumer and what it reads.
7. `alCFR_Segmodel.bin` (5,776,288 B) — a separate artefact, not analysed.

## 6. Reproduce

```bash
cd implementations/camera-cfr-fleet
python3 -I make_fixture.py
python3 -m unittest discover -q
python3 -I cfr_probe.py /tmp/work/cfr/c3645_uw.bin --brief
```
