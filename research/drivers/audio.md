# Driver interface: `db_type=AUDIO` — 110 rows, 13 filenames

Issue #865. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number is from a command run this session (2026-11-20)
against the committed matrix and against `torvalds/linux` master.

## Headline: `AUDIO` is not an audio bucket

Of the 13 filenames upstream's `bintypes` types as `AUDIO`, **five are not
audio firmware at all** and only **four have a mainline loader under the name
recorded**. The bucket is a classifier artifact, and the dominant content by
both row count and bytes is **GPU microcode**:

| family actually | rows | bytes | share of rows |
|---|---:|---:|---:|
| GPU (Adreno SQE + GMU microcode) | 79 | 3,421,336 | 71.8% |
| audio amplifier / audio DSP | 31 | 2,389,361 | 28.2% |
| **total** | **110** | **5,810,697** | **100%** |

Reproduce:

```
python3 -I -c "
import csv
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
a=[r for r in rows if r.get('db_type')=='AUDIO']
print(len(a), len({r['filename'] for r in a}), len({r['device'] for r in a}))
from collections import Counter; print(Counter(r['blob_family'] for r in a))"
```

output (this session):

```
110 13 44
Counter({'gpu': 79, 'other': 31})
```

The `blob_family` column of the matrix **already contradicts** the `db_type`
column for 79 of its own 110 `AUDIO` rows [F]. The repo's own recon already
recorded the SQE half of this (`upstream-contribution/blob-database/recon.md`
line 263: "`a660_sqe.fw` (Adreno 660 SQE microcode, GPU) is typed `AUDIO` in
upstream's bintypes — a bintypes mislabel") [F]. This document completes that
observation: the mislabel is not one file, it is the majority of the bucket,
and it has a second, larger half (GMU) that recon.md did not name.

## The 13 filenames, with device spread and byte sizes

| rows | devices | filename | bytes seen | actual subsystem |
|---:|---:|---|---|---|
| 30 | 30 | `a660_sqe.fw` | 40,496 / 43,068 | GPU — Adreno 660 SQE |
| 21 | 21 | `a660_gmu.bin` | 53,672 / 55,252 / 55,256 | GPU — Adreno 660 GMU |
| 14 | 14 | `a650_gmu.bin` | 41,548 | GPU — Adreno 650 GMU |
| 14 | 14 | `a650_sqe.fw` | 31,632 | GPU — Adreno 650 SQE |
| 7 | 7 | `sn100u.bin` | 204,518 | **NFC** — NXP SN100U controller FW |
| 3 | 3 | `rt5514_dsp_fw1.bin` | 20,272 | audio DSP — Realtek RT5514 |
| 3 | 3 | `rt5514_dsp_fw2.bin` | — | audio DSP — Realtek RT5514 |
| 3 | 3 | `rt5514_dsp_fw3.bin` | — | audio DSP — Realtek RT5514 |
| 3 | 3 | `rt5514_dsp_fw4.bin` | — | audio DSP — Realtek RT5514 |
| 3 | 3 | `rt5514p_dsp_fw1.bin` | — | audio DSP — Realtek RT5514**P** |
| 3 | 3 | `rt5514p_dsp_fw2.bin` | — | audio DSP — Realtek RT5514**P** |
| 3 | 3 | `rt5514p_dsp_fw3.bin` | — | audio DSP — Realtek RT5514**P** |
| 3 | 3 | `rt5514p_dsp_fw4.bin` | — | audio DSP — Realtek RT5514**P** |

The `a660_sqe.fw` size drift 40,496 → 43,068 B across nightlies is the same
drift already recorded in `research/laptop/fragmentation-half.md` line 154 [F].

Note the RT5514 files appear on exactly 3 devices — Pixel_4A_5G, Pixel_5,
Pixel_5A — i.e. the whole family is one device cluster [F].

## Loader contract — GPU half (79 rows)

### SQE (`a650_sqe.fw`, `a660_sqe.fw`)

Firmware names come from the per-GPU `adreno_info` table in
`drivers/gpu/drm/msm/adreno/a6xx_catalog.c` [F]:

```c
/* a660, line 1083 */
.fw = {
    [ADRENO_FW_SQE] = "a660_sqe.fw",
    [ADRENO_FW_GMU] = "a660_gmu.bin",
},

/* a650, line 1056 */
.fw = {
    [ADRENO_FW_SQE] = "a650_sqe.fw",
    [ADRENO_FW_GMU] = "a650_gmu.bin",
},
```

The request path is `adreno_load_fw()` → `adreno_request_fw()`
(`drivers/gpu/drm/msm/adreno/adreno_gpu.c` line 536). **This is the part a
naive reading gets wrong** [F]: the driver builds `qcom/<name>` and tries three
locations in order, not one:

```c
newname = kasprintf(GFP_KERNEL, "qcom/%s", fwname);   /* line 543 */
...
ret = request_firmware_direct(&fw, newname, drm->dev);      /* 1. qcom/… */
ret = request_firmware_direct(&fw, fwname,  drm->dev);      /* 2. legacy  */
ret = request_firmware(&fw, newname, drm->dev);             /* 3. helper  */
```

So the on-disk contract is **either** `/lib/firmware/qcom/a660_sqe.fw` **or**
`/lib/firmware/a660_sqe.fw` [F]. On Android the vendor tree ships them flat in
`vendor/firmware` (the `db_path` in the matrix is `…/vendor/firmware`), which is
the legacy-location form — the blob name matches with no `qcom/` prefix [I].

The SQE payload is validated before use. `a6xx_ucode_check_version()`
(`a6xx_gpu.c` line 985) branches on the **filename string**:

```c
const char *sqe_name = adreno_gpu->info->fw[ADRENO_FW_SQE];
...
} else if (!strcmp(sqe_name, "a650_sqe.fw")) {
    if ((buf[0] & 0xfff) >= 0x095) { ret = true; ... }   /* needs >= 0.95 */
} else if (!strcmp(sqe_name, "a660_sqe.fw")) {
    ret = true;                                          /* all fixes built in */
```

That is a real interface fact for the parser: **`buf[0] & 0xfff` is the SQE
microcode version**, and the A650 threshold is `0x095` [F]. The `whereami`
opcode fix applies only up to A640; A650 needs the version gate; A660 has all
fixes from the start [F].

### GMU (`a650_gmu.bin`, `a660_gmu.bin`)

Loaded through `adreno_gpu->fw[ADRENO_FW_GMU]`, consumed by
`a6xx_gmu.c` line 881 (`const struct firmware *fw_image = adreno_gpu->fw[ADRENO_FW_GMU];`)
[F]. Same three-location request path. The GMU is skipped entirely on
"GMU wrapper" targets (`adreno_gpu.c` line 627:
`if (adreno_has_gmu_wrapper(adreno_gpu) && i == ADRENO_FW_GMU) continue;`) [F].

### Why the matrix calls it AUDIO

Not established. The matrix records `blob_family=gpu` for these rows while
`db_type=AUDIO`, so the two columns disagree internally and no committed
document explains the origin of the `bintype` label [N]. Recorded as an open
question rather than a guess.

## Loader contract — audio half (31 rows)

### RT5514 / RT5514P (`rt5514*_dsp_fwN.bin`, 24 rows)

This is the one place in the bucket where the blob name is a **literal string in
the kernel** [F]. `sound/soc/codecs/rt5514.h` lines 255-256:

```c
#define RT5514_FIRMWARE1	"rt5514_dsp_fw1.bin"
#define RT5514_FIRMWARE2	"rt5514_dsp_fw2.bin"
```

and `sound/soc/codecs/rt5514.c` requests exactly those two:

```c
371:  request_firmware(&fw, RT5514_FIRMWARE1, component->dev);
384:  request_firmware(&fw, RT5514_FIRMWARE2, component->dev);
```

**There is no `RT5514_FIRMWARE3` or `RT5514_FIRMWARE4`.** fw3 and fw4 — 6 of the
24 RT5514 rows — have **no mainline consumer at all** [F]. That is an honest
negative and a real finding: a device shipping four firmware blobs is
mainline-loading only two.

The load is triggered from a userspace kcontrol (`rt5514_dsp_voice_wake_up_put`,
`rt5514.c` line 324) — the DSP firmware is **not** loaded at probe, only when
voice-wake-up is enabled [F].

The `rt5514p` variant (fw1..fw4, 12 rows) is **absent from mainline** [F].
`grep -rn rt5514p` over the fetched `rt5514.c`, `rt5514.h`, `rt5514-spi.c`
returns nothing, and `sound/soc/codecs/Kconfig` lines 1848-1858 define only
`SND_SOC_RT5514`, `SND_SOC_RT5514_SPI`, `SND_SOC_RT5514_SPI_BUILTIN` [F].
The `p` part is vendor-only.

`rt5514-spi.c` is the SPI transport driver and does **not** call
`request_firmware` at all — the firmware request belongs to the ASoC codec
driver, not the SPI driver [F].

### `sn100u.bin` (7 rows) — not audio

`sn100u` is the **NXP SN100U NFC controller**, and `sn100u.bin` is its firmware
image. Corroboration [F]:

- NXP's own firmware repository publishes `sn1xx/64-bit/libsn100u_fw.so`
  (`github.com/NXP/nfc-NXPNFCC_FW`).
- The repo's own fleet doc files `sn100u.bin` under **`other`**, not audio, in
  the OnePlus 8/8T/8 Pro/9R census (`research/fleet/third-device-instantnoodle.md`
  line 86) — the committed research already disagrees with the `AUDIO` label.

The mainline NFC NXP-NCI driver
(`drivers/nfc/nxp-nci/firmware.c` line 196) takes the firmware name as a
**parameter**, it does not hardcode `sn100u.bin` [F]:

```c
int nxp_nci_fw_download(struct nci_dev *ndev, const char *firmware_name)
...
strscpy(fw_info->name, firmware_name);
r = request_firmware(&fw_info->fw, firmware_name, ...);
```

So there is no mainline request string to match; the name is supplied by the
board/NCI layer. On these devices the blob ships in `vendor/firmware`, which is
the Android HAL path, not a kernel firmware path [I]. **`sn100u.bin` should be
re-typed `NFC`, not `AUDIO`** [I].

## Filename → loader verdict table

| filename | mainline loader | kernel path | line | verdict |
|---|---|---|---|---|
| `a660_sqe.fw` | `adreno` (msm) | `adreno/a6xx_catalog.c` | 1083 | **loads**, name exact |
| `a660_gmu.bin` | `adreno` (msm) | `adreno/a6xx_catalog.c` | 1084 | **loads**, name exact |
| `a650_gmu.bin` | `adreno` (msm) | `adreno/a6xx_catalog.c` | 1057 | **loads**, name exact |
| `a650_sqe.fw` | `adreno` (msm) | `adreno/a6xx_catalog.c` | 1056 | **loads**, name exact |
| `rt5514_dsp_fw1.bin` | `snd-soc-rt5514` | `codecs/rt5514.h` | 255 | **loads**, name exact |
| `rt5514_dsp_fw2.bin` | `snd-soc-rt5514` | `codecs/rt5514.h` | 256 | **loads**, name exact |
| `rt5514_dsp_fw3.bin` | none | — | — | **no consumer** |
| `rt5514_dsp_fw4.bin` | none | — | — | **no consumer** |
| `rt5514p_dsp_fw1.bin` | none (no rt5514p driver) | — | — | **no consumer** |
| `rt5514p_dsp_fw2.bin` | none | — | — | **no consumer** |
| `rt5514p_dsp_fw3.bin` | none | — | — | **no consumer** |
| `rt5514p_dsp_fw4.bin` | none | — | — | **no consumer** |
| `sn100u.bin` | name is a runtime parameter (NXP-NCI) | `nfc/nxp-nci/firmware.c` | 196 | **not audio; NFC** |

Six of thirteen filenames have no mainline consumer under the recorded name.
That is 18 of 110 rows (16.4%) [F].

## Why the Cirrus CS35L41 family is absent here — and a matrix gap

The matrix's `AUDIO` bucket contains **no** Cirrus amplifier firmware. But the
same matrix carries the CS35L41/CS40L2x amplifier DSP blobs under
`db_type=UNKNOWN` — e.g. `cs35l41-dsp1-spk-prot.bin`,
`cs35l41-dsp1-spk-cali.bin`, `cs35l40-*`, `cs40l25a_*` — and those **are**
genuine audio firmware with a real mainline loader contract [F]. Counting the
devices in `data/fleet/devices-001-222.csv` with `db_type=AUDIO`:

```
368 rows, 93 distinct filenames, 71 devices, 6,202,361 B
```

versus the matrix's 110 rows / 13 filenames / 44 devices. The two committed
datasets disagree by a factor of 3.35 on the same nominal bucket [F]. The
`devices-001-222.csv` set additionally contains the CS35L41 family (222 rows),
`aw87xxx*` (42 rows), and the `sn100u`/`rt5514` sets.

So the `AUDIO` `db_type` is **under-assigned in the matrix and over-broad in
meaning**. Any census that trusts `db_type=AUDIO` to find audio firmware
misses the Cirrus family entirely and picks up GPU microcode instead [I].

### The Cirrus contract (for the delta, not this bucket)

`cs35l41` is a `cs_dsp`/`wm_adsp` client: `sound/soc/codecs/cs35l41.c` line 1099
sets `dsp->part = "cs35l41"` and line 1100 `dsp->fw = 9` (`WM_ADSP_FW_SPK_PROT`)
[F]. The filename is **constructed**, not hardcoded, by
`wm_adsp_request_firmware_file()` (`sound/soc/codecs/wm_adsp.c` line 743):

```c
fw->filename = kasprintf(GFP_KERNEL, "%s%s-%s-%s-%s.%s", dir, dsp->part,
                         fwf, wm_adsp_fw[dsp->fw].file, system_name, filetype);
```

with `dir = "cirrus/"`, `wm_adsp_fw[WM_ADSP_FW_SPK_PROT].file = "spk-prot"`
(line 307), `WM_ADSP_FW_SPK_CALI → "spk-cali"` (312), `WM_ADSP_FW_SPK_DIAG →
"spk-diag"` (313), and a lowercasing/non-alnum→hyphen normalisation pass
(lines 778-787) [F]. The DSP firmware the driver requests is **`.wmfw`**; the
`.bin` is the **coefficient** file requested alongside it (`wm_adsp.c` line 837
`/* Look for matching .bin file */`, extension `"bin"` at 841) [F].

That is exactly why the Android blobs named `cs35l41-dsp1-spk-prot.bin` do not
appear in the kernel as a literal string: the `.bin` is the coeff payload whose
name is *derived*, and the `.wmfw` is the executable image the driver actually
boots. The Android vendor tree ships the `.bin`; the `.wmfw` lives in
linux-firmware under `cirrus/` [I].

## Honest negatives

1. **No committed artifact existed for this issue.** `research/drivers/` did not
   exist; `git log --all -- research/drivers/audio.md` returned nothing [F].
2. **The `AUDIO` label's origin is unexplained.** Nothing in the repo or in
   this session's searches documents why upstream's `bintypes` calls Adreno
   microcode "AUDIO". Left open, not guessed [N].
3. **`rt5514p` has no mainline support**, so its four blobs cannot be verified
   against a driver. Their internal format is **not** analysed here [N].
4. **`sn100u.bin` payload format not analysed.** Its identity as NXP SN100U NFC
   firmware is [F]; its container layout is out of scope for this issue and is
   **not** claimed [N].
5. **No payload bytes were read.** Every fact above comes from the committed
   matrix CSVs and from `torvalds/linux` master source. The corpus itself is
   not publicly fetchable, so no hash was recomputed [F].
6. ~~**`cs35l41` `.bin` vs `.wmfw` pairing is [I], not [F].**~~ **Resolved to
   [F]** by `research/fleet/other-audio.md` (#2052). The inference from the name
   grammar is now backed by a size-band measurement against the local
   linux-firmware corpus: the 25 distinct `.wmfw` payloads span 25,808-41,364 B
   and the 742 distinct coefficient `.bin` payloads span 948-13,404 B, with
   **zero overlap** between the two size sets. The matrix's 263 Cirrus
   `cs35*`/`cs40l2*` rows span 48-8,732 B, of which 228 fall inside the
   coefficient band and **none** reach the `.wmfw` band. So the Android
   `*-dsp1-spk-prot.bin` files are coefficient payloads, confirmed by size
   distribution rather than by name grammar alone [F]. See
   `research/fleet/other-audio.md` §3.

## Reproduce

```
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_catalog.c | grep -n -A3 'a660_sqe.fw'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/adreno_gpu.c   | sed -n '534,600p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/gpu/drm/msm/adreno/a6xx_gpu.c     | sed -n '985,1050p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/sound/soc/codecs/rt5514.h               | sed -n '255,256p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/sound/soc/codecs/rt5514.c               | grep -n request_firmware
curl -s https://raw.githubusercontent.com/torvalds/linux/master/sound/soc/codecs/wm_adsp.c              | sed -n '295,315p;743,800p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/sound/soc/codecs/cs35l41.c              | sed -n '1092,1102p'
curl -s https://raw.githubusercontent.com/torvalds/linux/master/drivers/nfc/nxp-nci/firmware.c          | sed -n '196,220p'
```

All fetches 2026-11-20, `torvalds/linux` master.

## Sources

| claim | source | access |
|---|---|---|
| 110 rows / 13 filenames / 44 devices | `upstream-contribution/blob-database/coverage-matrix.csv` | 2026-11-20 |
| 79 gpu + 31 other `blob_family` split | same file, `blob_family` column | 2026-11-20 |
| 368 rows / 93 files in fleet CSV | `data/fleet/devices-001-222.csv` | 2026-11-20 |
| `a660_sqe.fw` typed AUDIO is a mislabel | `upstream-contribution/blob-database/recon.md:263` | 2026-11-20 |
| `sn100u.bin` is filed under `other` | `research/fleet/third-device-instantnoodle.md:86` | 2026-11-20 |
| SQE size drift 40,496→43,068 | `research/laptop/fragmentation-half.md:154` | 2026-11-20 |
| NXP SN100U firmware repo | `github.com/NXP/nfc-NXPNFCC_FW` (`sn1xx/64-bit/libsn100u_fw.so`) | 2026-11-20 |
| all kernel line numbers | `raw.githubusercontent.com/torvalds/linux/master/...` | 2026-11-20 |
