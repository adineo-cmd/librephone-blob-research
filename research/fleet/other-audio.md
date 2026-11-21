# The `audio` subfamily of `other` — speaker-amp DSP firmware across 83 devices

**Issue:** #2052 · **Analysis date:** 2026-11-20 · **Evidence classes:** `[F]` measured fact
(command and output shown) · `[I]` inference from stated facts · `[N]` honest negative ·
`[U]` unresolved.

**Scope.** The 422 matrix rows classified `blob_family=other, blob_subfamily=audio`:
**83 distinct devices**, 10 vendors, 124 distinct filenames, 5,418,315 B.

**Artifacts read (read-only, never committed).**
`/usr/lib/firmware/cirrus/` (2,118 entries → 770 real files, the upstream Cirrus DSP corpus);
`…/lineage-fp6/extracted/trees/vendor-firmware/aw882xx_acf.bin` (4,328 B);
`…/mediatek/extract/parts/audio_dsp.img` (1,404,928 B).
No payload byte is reproduced beyond ≤16-byte hex samples.

---

## 0. Headline

1. **`[F]` The 422 rows catalogue the coefficient half of the pair, not the bootable image.**
   Measured against the local Cirrus corpus: the `.wmfw` images span 25,808–41,364 B, the
   coefficient `.bin` files span 948–13,404 B, and those two size sets have **zero overlap**.
   The Cirrus rows in the matrix span **48–8,732 B** — every one of them below the smallest
   `.wmfw`. `research/drivers/audio.md` inferred this from the *name grammar* and marked it
   `[I]`; this issue closes it with a size-band measurement. See §3.
2. **`[F]` The corpus is 2.75× smaller than its file count suggests.** 527 `.wmfw` paths and
   1,464 `.bin` paths resolve to **25** and **742** distinct payloads. One payload,
   `halo_cspl_RAM_revB2_29.63.1.wmfw`, is behind **234 filenames**. See §5.
3. **`[F]` The single `isa_identified` claim in this subfamily is now settled — and it is
   `[F]`, not the `[N]` I expected.** `audio_dsp.img` embeds the FreeRTOS port path
   `kernel/FreeRTOS/Source/portable/XCC/Xtensa/port.c` and twelve Xtensa exception
   mnemonics. See §2. The 421 blank rows stay blank.
4. **`[F]` Cirrus and Awinic are mutually exclusive at device level.** 44 devices carry
   Cirrus amp firmware, 36 carry Awinic, **0 carry both**. That is a supply-chain split, not
   an accident of sampling. See §4.
5. **`[N]` No ISA is recorded anywhere in the `.wmfw` format**, and no instruction-level
   decode of any Cirrus DSP payload was performed here — no Xtensa backend exists in this
   environment. See §7.

---

## 1. The subfamily in numbers

```
python3 -I -c "
import csv,collections
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
au=[r for r in rows if r['blob_subfamily']=='audio']
print(len(au), len({r['device'] for r in au}), len({r['vendor'] for r in au}),
      len({r['filename'].split('/')[-1] for r in au}), sum(int(r['size_bytes']) for r in au))"
```

```
422 83 10 124 5418315
```

| vendor | rows | devices |
|---|---:|---:|
| google | 156 | 18 |
| samsung | 65 | 14 |
| xiaomi | 59 | 13 |
| motorola | 57 | 21 |
| sony | 40 | 7 |
| nothing | 13 | 1 |
| fxtec | 12 | 1 |
| fairphone | 10 | 3 |
| lenovo | 6 | 1 |
| oneplus | 4 | 4 |

`db_type` is not coherent for this bucket — the same subfamily carries five different labels:

| `db_type` | rows |
|---|---:|
| `AUDIOAMP` | 308 |
| `CODEC` | 72 |
| `AUDIO` | 24 |
| `UNKNOWN` | 15 |
| `ELF64` | 3 |

Priority is almost entirely un-triaged: **P3 376 / P2 45 / P1 1**. `interface_documented=n`
on **all 422** rows. `isa_identified` is blank on **421 of 422**.

### 1.1 Family classification `[F]`

Filenames carry leading position prefixes bolted onto the vendor name. Stripping
`^(R2|L2|TH|BH|TL|BL|R|L|B|T)-` and classifying the remainder:

| family | rows | bytes |
|---|---:|---:|
| Cirrus CS35L41/40/45 amp DSP | 221 | 672,180 |
| Awinic AW88xx/87xx ACF | 114 | 213,428 |
| Cirrus CS40L2x haptics | 42 | 47,472 |
| Realtek RT5514 DSP | 24 | 957,735 |
| Samsung SoundBoosterParam | 11 | 94,520 |
| Cirrus CS47L SoundWire codec | 3 | 4,176 |
| unclassified | 7 | 3,428,804 |

Totals reconcile to **422 rows / 5,418,315 B**. The `unclassified` bucket is 4 filenames —
`AudioSphereModule.so.1` (3 rows, an ELF shared object, not firmware),
`audio_dsp.img`, `mialgo_supernight_capture_opencl.bin` (1,697,364 B, an OpenCL kernel
blob — plainly not audio firmware), and `spkamp.bin` (2 rows). That last one and the OpenCL
blob are misclassified and are the reason the bucket holds 63% of the bytes.

Prefix histogram over the 422 rows: `(none)` 303, `R-` 67, `B-` 14, `T-` 14, `L-` 10,
`L2-` 3, `R2-` 3, `TH-` 2, `BH-` 2, `TL-` 2, `BL-` 2.

---

## 2. ISA: the one claim in this subfamily, tested

The matrix carries exactly one `isa_identified` value for `blob_subfamily=audio`, on
`Redmi_10S` / `audio_dsp.img` (1,404,928 B):

> `Cadence HiFi3 (Xtensa) per self-name hifi3_a_*; byte-level confirm pending (no Xtensa backend)`

### 2.1 `[F]` Where the name actually comes from

`hifi3_a_dram` is **not a filename**. It is the `name` field of an `mtk_hdr` record at
offset 8 of the image:

```
first 32: 88 16 88 58 00 80 00 00 68 69 66 69 33 5f 61 5f 64 72 61 6d 00 00 ...
                                            h  i  f  i  3  _  a  _  d  r  a  m
```

Three such records, all with magic `88 16 88 58`, at offsets 0 / 36,976 / 78,048, naming
`hifi3_a_dram` / `hifi3_a_iram` / `hifi3_a_sram`. The matrix's phrase "per self-name" is
accurate in substance but re-labels a *header record name* as a *self-name*. The source of
the claim is `mediatek/rosemary-census.md:139`, which itself says "name-level ID; byte-level
pending".

### 2.2 `[F]` The byte-level confirmation the earlier work could not make

The original note was blocked on "no Xtensa backend". That is still true for *disassembly* —
but the question does not require disassembly. The image carries its toolchain's vocabulary:

```
payloads containing >=1 windows path: 658 / 742     (coeff corpus, unrelated)
@1118660  kernel/FreeRTOS/Source/event_groups.c
@1118804  EXCCAUSE_ILLEGAL
@1118824  EXCCAUSE_SYSCALL
@1118844  EXCCAUSE_DIVIDE_BY_ZERO
@1118868  EXCCAUSE_LOAD_PROHIBITED
@1118896  EXCCAUSE_STORE_PROHIBITED
@1118924  EXCCAUSE_UNALIGNED
@1119572  kernel/FreeRTOS/Source/portable/XCC/Xtensa/port.c
@1167664  kernel/FreeRTOS/Source/portable/MemMang/heap_4.c
```

`EXCCAUSE_*` are the Xtensa exception-cause register names — they exist in no other
architecture. `portable/XCC/Xtensa/port.c` is the FreeRTOS port for the **Xtensa C
Compiler**. All of these sit inside the `hifi3_a_sram` region (78,048–1,398,952), i.e. in
the DSP's own code image, not in a stray metadata string.

So the verdict upgrades from name-level `[I]` to **`[F]`**, with the caveat that it is
established by embedded toolchain vocabulary, not by decoded instructions. The claim's own
"no Xtensa backend" caveat remains literally true and is preserved.

### 2.3 `[U]` The local artifact is a sibling, not the matrix row

The only `audio_dsp.img` on this machine is 1,404,928 B — the same size as the matrix row —
but a **different build**:

| | size | md5 |
|---|---:|---|
| matrix row (`xiaomi/rosemary/radio`) | 1,404,928 | `506d942e1a2d42cf6d6db8f8bacc1208` |
| local (`mediatek/extract/parts/`) | 1,404,928 | `4fe7061eeba2fef4a0f5120fc654f668` |

Both are MT6785/`rosemary` builds of the same partition. The Xtensa evidence above is
measured on the local sibling; that the matrix row has the same ISA is `[I]` from identical
device, partition, and size, not `[F]` from its own bytes. Recorded rather than glossed.

---

## 3. `[F]` What these rows actually are: the coefficient half

This is the measurement `research/drivers/audio.md` left open. That doc established the
Cirrus loader contract from mainline — `cs35l41` is a `cs_dsp`/`wm_adsp` client,
`dsp->fw = 9` (`WM_ADSP_FW_SPK_PROT`), and the driver requests **both** a `.wmfw` (the
executable image it boots) and a `.bin` (the coefficient file), with names derived by
`wm_adsp_request_firmware_file()`. It then wrote, correctly at the time:

> `cs35l41` `.bin` vs `.wmfw` pairing is `[I]`, not `[F]`. … that the Android
> `*-dsp1-spk-prot.bin` is specifically the coeff half of that pair is inferred from the
> name grammar, not from a byte-level comparison.

The size bands settle it without needing a byte comparison:

| set | distinct payloads | size range | median |
|---|---:|---|---:|
| `.wmfw` (magic `WMFW`) | 25 | 25,808–41,364 B | 33,868 B |
| coeff `.bin` (magic `WMDR`) | 742 | 948–13,404 B | 5,280 B |

```
size-set overlap wmfw vs coeff: 0
Cirrus CS35*/CS40L2* matrix rows: 263 size 48..8732
  rows in coeff range      : 228
  rows in wmfw range       : 0
ANY audio row whose size falls inside 25808..41364: 9
```

The 263 Cirrus rows span **48–8,732 B**; 228 fall inside the coefficient band and **none**
reach the `.wmfw` band. The only 9 audio rows inside the `.wmfw` size band are all
`rt5514*` — Realtek, a different vendor whose DSP images are genuinely image-sized.

**Conclusion `[F]`:** the `audio` subfamily as recorded in the matrix is a catalogue of
*coefficient/tuning payloads*, not of bootable DSP firmware. A census that reads this bucket
as "the DSP firmware of 83 devices" overstates what is on disk; the executable images for
the Cirrus devices live in linux-firmware under `cirrus/`, and are **not** in this dataset.

This also explains a hash result that would otherwise look like a data defect: `md5_db` is
present on all 422 rows with 292 distinct values, and **0 of 292** match any of the 742
local Cirrus coefficient hashes. Different artifacts, as expected.

---

## 4. `[F]` Device classes: a two-vendor split, not a spectrum

The matrix has **no device-class field**, so "which device classes use it" has to be
answered by proxy. Grouping the 83 devices by the filename families each carries:

| family set | devices |
|---|---:|
| Awinic only | 31 |
| Cirrus amp only | 25 |
| Cirrus amp + haptics | 7 |
| Cirrus amp + Samsung SoundBooster | 5 |
| Awinic + unclassified | 5 |
| Cirrus amp + haptics + SoundBooster | 3 |
| Cirrus amp + Realtek | 2 |
| unclassified | 1 |
| Samsung SoundBooster only | 1 |
| Cirrus amp + Cirrus codec | 1 |
| Cirrus amp + SoundBooster + unclassified | 1 |
| Realtek only | 1 |

Aggregated:

```
devices with cirrus-amp: 44
devices with awinic     : 36
devices with both       : 0
devices with realtek    : 3
devices with haptics    : 10
total devices           : 83
```

**Zero devices carry both Cirrus and Awinic.** That is the sharpest structural fact in this
subfamily: the speaker-amp choice is a per-OEM platform decision, and the two vendors'
tuning-payload formats never coexist on one device. This is a proxy, not a device-class
field, and `released_year` is empty for every row, so **no temporal claim is possible** from
this dataset.

---

## 5. `[F]` The corpus is heavily symlinked: 2.75× inflation

`/usr/lib/firmware/cirrus/` looks like a large corpus and is not:

```
total entries: 2118
symlinks: 1348
distinct realpath: 770
inflation factor: 2.75x
wmfw entries 527 -> 25 distinct
bin  entries 1464 -> 742 distinct
```

The fan-out is concentrated on a handful of shared payloads:

```
234 names -> halo_cspl_RAM_revB2_29.63.1.wmfw.zst
 81 names -> CS35L63_Rev2.5.7.wmfw.zst
 63 names -> halo_cspl_RAM_revB2_29.85.0.wmfw.zst
 21 names -> CS35L56_Rev3.11.11.1.wmfw.zst
```

The naming scheme is *per-OEM alias → shared versioned payload*. `cs35l41/` holds nine
version directories, each containing exactly one `.wmfw`:

| version dir | payload |
|---|---|
| v6.39.0 | `halo_cspl_RAM_revB2_29.41.0.wmfw` |
| v6.47.0 | `halo_cspl_RAM_revB2_29.49.0.wmfw` |
| v6.56.0 | `halo_cspl_RAM_revB2_29.58.0.wmfw` |
| v6.61.1 | `halo_cspl_RAM_revB2_29.63.1.wmfw` |
| v6.63.0 | `halo_cspl_RAM_revB2_29.65.0.wmfw` |
| v6.68.0 | `halo_cspl_RAM_revB2_29.70.0.wmfw` |
| v6.78.0 | `halo_cspl_RAM_revB2_29.80.0.wmfw` |
| v6.80.0 | `halo_cspl_RAM_revB2_29.82.0.wmfw` |
| v6.83.0 | `halo_cspl_RAM_revB2_29.85.0.wmfw` |

All 742 coefficient payloads have distinct md5; all 25 `.wmfw` payloads have distinct md5.
There is no accidental duplication — only intentional aliasing.

---

## 6. `[F]` Firmware age and embedded provenance

### 6.1 The `.wmfw` footer is not at the end of the file

`wmfw_header` is 12 B (`magic[4]`, `le32 len`, `le16 rev`, `u8 core`, `u8 ver`), followed by
16 B of region sizes, then `wmfw_footer` (12 B: `le64 timestamp`, `le32 checksum`) at
**offset 28** — *before* the regions, not after. Verified on the 29.63.1 image:

```
magic b'WMFW' len 40 rev 768 core 4 ver 3
bytes 12..28 (sizes): 00 05 00 00 d0 07 00 00 f4 0f 00 00 00 00 00 00  -> (1280, 2000, 4084, 0)
bytes 28..40: 6b e1 28 61 00 00 00 00 00 00 00 00  -> ts 1630069099 ck 0x0
first region starts at 40
```

All 25 payloads walk cleanly to EOF with **0 trailing bytes**, so there is no trailing
footer to find. Every footer checksum is `0x0`.

### 6.2 The build dates, and that they are self-consistent

Footer timestamp and the `INFO_TEXT` region agree on **25/25** payloads (0 mismatches),
range **2020-10-09 → 2025-10-14**:

| payload | footer ts | INFO string |
|---|---:|---|
| 29.41.0 | 1602241676 | Fri 09 Oct 2020 13:07:57 W. Europe Daylight Time |
| 29.63.1 | 1630069099 | Fri 27 Aug 2021 14:58:19 W. Europe Daylight Time |
| 29.85.0 | 1680252169 | Fri 31 Mar 2023 10:42:49 W. Europe Daylight Time |
| CS35L56 Rev3.11.11 | 1701812241 | Tue 05 Dec 2023 21:37:21 GMT Standard Time |
| CS35L56 Rev4.5.9 | 1758570376 | Mon 22 Sep 2025 14:46:15 Central Daylight Time |
| CS35L63 Rev2.5.7 | 1760473919 | Tue 14 Oct 2025 21:31:58 GMT Daylight Time |

A 5-year span across 25 payloads, with two independent internal clocks agreeing, is a
reasonable consistency check that the timestamps are genuine build times and not
file-copy times.

### 6.3 `[F]` 88.7% of coefficient files leak a Windows build path

```
payloads containing >=1 windows path: 658 / 742
distinct path strings: 568
  80  C:\Users\atsai\OneDrive - Cirrus Logic\
   2  D:\Amp Tuning\HP\840\0930\103C8B45_220930.bin
   2  C:\Users\tyang\Desktop\Product Setting\SmartAMP\ASUS\ASUS_Zenbook\2023Projects\UX7602Reflash\tuning Release\
```

These sit in `NAME_TEXT` (block type high byte `0xfe`) blocks. They are provenance
metadata — which tuning engineer, which OEM program, which dated release — not firmware
content, and they name commercial laptop programs (Dell, HP, ASUS Zenbook) rather than the
Android phones this issue is about. That the same coefficient-file pipeline serves both is
the finding; no payload bytes are reproduced here.

---

## 7. Honest negatives

1. **`[N]` No instruction-level decode was performed on any Cirrus DSP payload.** capstone
   5.0.7 in this environment has no `CS_ARCH_XTENSA`; local binutils is x86-only
   (`objdump --info` lists no xtensa target); there is no `xtensa-*` or `llvm-objdump`
   binary. Every ISA statement in §2 rests on embedded strings, not on decoded opcodes.
2. **`[N]` The `.wmfw` format records no ISA.** It carries `magic`, `rev`, `core`, `ver`,
   four memory-region sizes (`xm`/`ym`/`pm`/`zm`) and opaque region payloads — and nothing
   architecture-identifying. `grep -ci isa` on `wmfw.h` returns **0**; on `cs_dsp.c` it
   returns 27, every one of them a substring of `disable`/`disabled`. The DSP's ISA is
   simply not a property this container exposes.
3. **`[N]` The `wmfw_halo_id_hdr` cannot be decoded from the file.** Naively unpacking the
   first `0x11` region as that struct yields `n_algs` in the 1.3e8–1.3e9 range on 25/25
   payloads — obviously wrong. The cause is now identified: `cs_dsp_halo_setup_algs()`
   reads that header from **DSP memory** via `regmap_raw_read(dsp->regmap, mem->base,
   &halo_id, sizeof(halo_id))` (`cs_dsp.c:2169`), not from the firmware file. The
   3-byte→32-bit unpacking is done in hardware. Reading it out of the file is a category
   error, and this doc does not claim an algorithm count.
4. **`[N]` `aw_cali.bin` in the FP6 tree is a zero-byte file.** It is present but empty, so
   it yields no format evidence.
5. **`[N]` No `SoundBoosterParam.bin` format content was found.** Searches return only
   consumer "sound booster" applications and one XDA thread listing the file in a vendor
   tree. The 11 rows / 94,520 B are catalogued but their container is **not** analysed.
6. **`[U]` The 60-byte vendor prefix on `aw882xx_acf.bin` is undocumented.** See §8.
7. **`[N]` The `audio_dsp.img` Xtensa evidence is from a sibling build**, not the matrix
   row's exact bytes (§2.3).

---

## 8. `[F]` A vendor-prefixed ACF variant that the mainline grammar rejects

Mainline parses Awinic ACF files with `aw88395_lib.c`, which expects `HEADER_VERSION_V1`
(`0x01000000`) at offset 4 and `BIN_DATA_TYPE` at offset 8. FP6's
`aw882xx_acf.bin` does not conform:

```
mainline aw88395 grammar applied at base 0:
  check_sum      @0   = 0x0a15f908
  header_ver     @4   = 0x00365046   <- "FP6\0", NOT 0x01000000
  bin_data_type  @8   = 0x00000000
mainline expects header_ver==0x01000000 -> MISMATCH
```

Re-applying the **identical** grammar at **base 60** makes it validate:

```
re-applied at base 60:
  header_ver  @64 = 0x01000000  MATCHES HEADER_VERSION_V1
  chip_type   @84 = b'aw88261'
prefix bytes: 08 f9 15 0a 46 50 36 00 ... 41 77 69 6e 69 63 00 ... 04 7b 09 00 00 80 04 00 00 0c 00 00 00
```

The 60-byte prefix carries `"FP6"` at offset 4 and `"Awinic"` at 28. So ACF files exist in
at least two layouts, and a parser assuming base 0 **silently misreads the header rather
than failing** — it reads `"FP6\0"` as a version and accepts `bin_data_type = 0`.

This is not a hypothetical: the matrix row `FP6` / `aw882xx_acf.bin` / 4,328 B /
`f2c752807f9ea62fb7552880797434be` is **byte-identical** to the local file this was measured
on (verified by md5). The same filename appears across 12 devices at **seven different
sizes** (1,048 / 1,504 / 1,792 / 2,672 / 3,440 / 4,328 / 4,976 B), so this is a
per-platform format, not a single fixed layout. Awinic's own FAQ does not describe the
container at all — it instructs the user to convert ACF to `aw_params.h` with a Windows
tool, `acf_parse_h.exe`.

---

## 9. Matrix defects found (Rule 1)

| # | defect | count | evidence |
|---|---|---:|---|
| 1 | `isa_identified` blank | 421 / 422 | `Counter` on the column |
| 2 | `interface_documented = n` | 422 / 422 | `Counter` on the column |
| 3 | duplicate `(device, filename)` pair | 1 | `Galaxy_A21S` / `SoundBoosterParam.bin` |
| 4 | same filename at different sizes | 28 filenames | `aw882xx_acf.bin` spans 7 sizes; `R-cs35l41-dsp1-spk-prot.bin` spans 18 |
| 5 | stray position prefix on vendor filename | 119 / 422 | `R-`, `B-`, `T-`, `L-`, `L2-`, `R2-`, `TH-`, `BH-`, `TL-`, `BL-` |
| 6 | `db_type` incoherent for one subfamily | 5 labels | `AUDIOAMP`/`CODEC`/`AUDIO`/`UNKNOWN`/`ELF64` |
| 7 | non-audio files inside the bucket | ≥3 rows | `mialgo_supernight_capture_opencl.bin` (OpenCL), `AudioSphereModule.so.1` (ELF), `audio_dsp.img` (whole partition image) |

Defect 4 is the most consequential: it means `size_bytes` is a *build* property, not an
*artifact identity*. Two rows with the same filename and different sizes are different
builds, and the matrix gives no field to distinguish them.

Cross-dataset check: `data/fleet/devices-001-222.csv` filtered to `subfamily=audio` holds
**376 rows / 75 devices / 5,321,635 B** — a strict subset of the matrix's 422/83. All 108
fleet basenames appear in the matrix's 124. The fleet set is 8 devices behind, not
contradictory.

---

## 10. Corrections filed against existing repo text

1. **`research/drivers/audio.md`** — its "Honest negatives" item 6 marks the
   `.bin`-is-the-coefficient-half claim as `[I]` "inferred from the name grammar, not from a
   byte-level comparison". §3 of this document supplies the size-band measurement that
   settles it. Corrected in place to `[F]` with a pointer here, rather than left standing as
   an open inference.
2. **`docs/REPO-STATE-MAP.md`** — had no `audio` row at all. Added, in the same form as the
   existing `media` row.

No other file was modified. No payload was committed.

---

## 11. Prior art, credited

Neither container format is undocumented, and this document does not claim to have
discovered either one.

| source | what it supplies |
|---|---|
| `research/drivers/audio.md` (#865, in-repo) | the full Cirrus `cs_dsp`/`wm_adsp` loader contract, the derived-filename grammar, `.wmfw` vs `.bin` roles |
| `include/linux/firmware/cirrus/wmfw.h` | `wmfw_header` / `wmfw_footer` / `wmfw_region` / `wmfw_coeff_hdr` / `wmfw_coeff_item` structs and region constants |
| `drivers/firmware/cirrus/cs_dsp.c` | `cs_dsp_load()` magic `WMFW` (:1553); `cs_dsp_load_coeff()` magic `WMDR` (:2245), coeff rev 1/2/3 (:2250-2260), 4-byte block advance (:2412); region decode (:1606-1607); halo ID read from DSP memory (:2169) |
| `sound/soc/codecs/aw88395/aw88395_lib.c` + `.h` | the ACF grammar: `HEADER_LEN=60`, `HEADER_VERSION_V1=0x01000000`, `BIN_DATA_TYPE_OFFSET=8` |
| `sound/soc/codecs/Makefile` | mainline Awinic set `aw8738 aw87390 aw88081 aw88166 aw88261 aw88395 aw88399` |
| `drivers/firmware/cirrus/test/cs_dsp_mock_wmfw.c` | the kernel's own `.wmfw` builder — confirms upstream treats the format as documented |
| `mediatek/rosemary-census.md:139` | origin of the `hifi3_a_*` observation, correctly self-labelled "name-level ID; byte-level pending" |

**What is new here** is measurement, not format: the coefficient-vs-image size-band
separation (§3), the 2.75× symlink inflation and 234-name fan-out (§5), the footer
position and the 25/25 timestamp agreement (§6), the 658-file build-path leak (§6.3), the
zero-overlap Cirrus/Awinic device split (§4), and the 60-byte ACF prefix (§8).

---

## 12. Reproduce

```
# census
python3 -I -c "
import csv,collections
rows=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
au=[r for r in rows if r['blob_subfamily']=='audio']
print(len(au), len({r['device'] for r in au}), len({r['vendor'] for r in au}),
      len({r['filename'].split('/')[-1] for r in au}), sum(int(r['size_bytes']) for r in au))"

# corpus shape
find /usr/lib/firmware/cirrus -type l | wc -l
find /usr/lib/firmware/cirrus -type f | wc -l

# decompress (a symlink needs its realpath or -f)
zstd -dc "$(realpath /usr/lib/firmware/cirrus/cs35l41/v6.61.1/halo_cspl_RAM_revB2_29.63.1.wmfw.zst)" | xxd -l 48

# mainline contract
curl -sL https://raw.githubusercontent.com/torvalds/linux/master/include/linux/firmware/cirrus/wmfw.h
curl -sL https://raw.githubusercontent.com/torvalds/linux/master/drivers/firmware/cirrus/cs_dsp.c | sed -n '1553p;1606,1607p;2245p;2412p;2169p'
curl -sL https://raw.githubusercontent.com/torvalds/linux/master/sound/soc/codecs/aw88395/aw88395_lib.h
```

All fetches 2026-11-20, `torvalds/linux` master. Corpus read 2026-11-20 from the local
linux-firmware install.

## 13. Sources

| claim | source | access |
|---|---|---|
| 422 rows / 83 devices / 10 vendors / 124 filenames / 5,418,315 B | `upstream-contribution/blob-database/coverage-matrix.csv` | 2026-11-20 |
| family split and prefix histogram | same file, filename column | 2026-11-20 |
| 2,118 entries / 1,348 symlinks / 770 real files | `find /usr/lib/firmware/cirrus` | 2026-11-20 |
| `.wmfw` 25 payloads 25,808–41,364 B; coeff 742 payloads 948–13,404 B | local corpus, zstd-decompressed | 2026-11-20 |
| 234-name fan-out onto 29.63.1 | `realpath` over the symlink tree | 2026-11-20 |
| footer at offset 28; 25/25 timestamp agreement | `wmfw.h` struct order + measured | 2026-11-20 |
| 658/742 payloads with a Windows build path | regex over decompressed `NAME_TEXT` blocks | 2026-11-20 |
| 44 Cirrus / 36 Awinic / 0 both | matrix device→family grouping | 2026-11-20 |
| `audio_dsp.img` Xtensa strings | `mediatek/extract/parts/audio_dsp.img` | 2026-11-20 |
| ACF 60-byte prefix | FP6 `aw882xx_acf.bin`, md5 `f2c752807f9ea62fb7552880797434be` | 2026-11-20 |
| all kernel line numbers | `raw.githubusercontent.com/torvalds/linux/master/...` | 2026-11-20 |
| fleet CSV 376 rows / 75 devices | `data/fleet/devices-001-222.csv` | 2026-11-20 |
