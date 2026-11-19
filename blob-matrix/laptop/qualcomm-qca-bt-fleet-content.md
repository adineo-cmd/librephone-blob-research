# Qualcomm QCA BT `hp*`/`hmt*` fleet — content-level RE (laptop/mobile half)

Analysis date: 2026-11-19 (payload work 2026-11-18/19). Evidence class:
**MEASURED PAYLOADS** — every number below is computed from bytes on disk or
quoted from public GPL kernel source. DB device counts are re-derived from
`sharing-clusters.csv`, not copied from a manifest.

This is **finding F-76**, the second-generation companion to F-75. It extends
the lab's first content-level blob RE (the `cr*`/`ap*` WCN399x/WCN3988
family) to the QCA2066 (`hp*`) and WCN7850 (`hmt*`) families.

Companion documents:

| document | owns |
|---|---|
| **`qualcomm-qca-bt-fleet.md`** (this directory, existing) | the F-75 **metadata** matrix: `cr*`/`ap*` md5/size per device. *Not edited by this work.* |
| **`qualcomm-qca-bt-fleet-content.md`** (this file) | the F-76 content-level summary: gen-2 layout, the digest invariant, the generation-split correction |
| **`../../implementations/qca-bt-gen2/fleet-analysis.md`** | the full analysis: per-byte-range map, per-file invariant table, identity matrix, NVM tag-map comparison, [OPEN] list |
| `../../implementations/qca-bt-gen2/hp_fleet_probe.py` | the probe. `python3 -I hp_fleet_probe.py <file> --brief` |
| `../../implementations/qca-bt-gen2/README.md` | usage, clean-room statement, fixture/test instructions |
| `../../implementations/qca-bt/fleet-analysis.md` | F-75, the gen-1 analysis this one is compared against |

Labels used throughout: **[S]** quoted from public GPL source (file:line) ·
**[M]** my own measurement of payload bytes · **[OPEN]** not established, gap
named.

Bytes live only in scratch space (`/tmp/astro_u/bt2/`); **no proprietary
content is committed**. The repo's `.gitignore` excludes `*.bin`/`*.mbn`/
`*.b[0-9][0-9]`, so this cannot happen by accident either.

---

## 1. Headline: the F-75 rule shape generalises, but its constants do not — and the generation split is temporal, not family-based

The natural assumption walking into this work was "`hp`/`hmt` are the new
generation, `cr`/`ap` are the old one". The bytes say otherwise, and that
correction is the most important result here.

F-75's rule for `cr*`/`ap*` is `file_size == 4 + 24 + data_length + 256`.
Applied to the gen-2 fleet it fails on **every file by exactly −212 bytes**
**[M]**:

| rule | result on all gen-2 files |
|---|---|
| `4 + 24 + data_length + 256` | FAIL, delta **−212** (constant) |
| `4 + 32 + data_length + 36` | **PASS**, delta 0 |

`256 − 36 = 220`, `32 − 24 = 8`, `220 − 8 = 212`. A fixed-constant delta on
every file is the signature of a **format revision**, not per-file variation.

**But the split does not follow the filename prefix** **[M]**:

| file | family | F-75 rule | gen-2 rule |
|---|---|---|---|
| `crbtfw21.tlv` (177,060 B) | WCN399x | **PASS** | FAIL (+212) |
| `crbtfw32.tlv` (117,664 B) | WCN399x | FAIL (−212) | **PASS** |
| `hpbtfw10.tlv` (178,532 B) | QCA2066 | FAIL (−212) | **PASS** |
| `htbtfw20.tlv` (210,704 B) | QCA6390 | FAIL (−212) | **PASS** |

`crbtfw32.tlv` is a **`cr` file in the gen-2 layout**. So the boundary tracks
**`rom_build` era / build date**, not chip family. `crbtfw21` (rom_build
`0x0201`, `patch_version` constant `0x0002`) is an older build in the old
format; `crbtfw32` (rom_build `0x0302`, `patch_version` `0x528a`) is a newer
build of the same family in the new format.

**Consequence for anyone writing a parser:** keying the layout off the
filename prefix mis-parses `crbtfw32.tlv`. The probe keys off the header
arithmetic — `total_size − data_length` ∈ {24, 36} — with file size as a
corroborating second check, never the filename.

---

## 2. Scope and provenance

Six DB byte-identities fetched and **md5-verified as MATCH**. Two chip
families, four independent upstream sources.

| file | bytes | md5 | devices | `product_id` | source |
|---|---|---|---|---|---|
| `hpbtfw20.tlv` | 201,560 | `922473448ce287c8bb5e849998b9ffb7` | **11** | 19 | `sm8450-mainline/firmware-xiaomi-cupid` → `bluetooth/` |
| `hpbtfw21.tlv` | 146,068 | `fac75b203eb19dec5ae026a0e72c7be0` | **8** | 19 | `iLtanaka/firmware-xiaomi-marble` → `generic/qca/` |
| `hpbtfw10.tlv` | 178,532 | `4f28663fa156321c8c8810bca6bb1549` | **3** | 19 | `sm8350-mainline/firmware-oneplus-lemonade` @ `338eca8f` (GitLab) |
| `hmtbtfw10.tlv` | 91,308 | `95bb0d97772c767ee21c0a9253df3caa` | **5** | 25 | `VIKAS9793/vendor_oneplus_giulia` (Git-LFS via `media.`) |
| `hmtbtfw20.tlv` | 232,348 | `380da1869e03fc4950d8f067482bec48` | **4** | 25 | FAT16 extract from `TheMuppets/..._fuxi` `radio/bluetooth.img` |
| `hmtbtfw20.tlv` | 280,628 | `7c8ee5968e701c07d605e750b3a72d44` | **1** | 25 | `VIKAS9793/vendor_oneplus_giulia` (Git-LFS via `media.`) |

Devices carrying the 11-device `hpbtfw20.tlv` / `hpnv20.bin`:
`cupid;diting;lemonade;lemonadep;marble;martini;mayfly;mondrian;thor;unicorn;zeus`.
The 8-device `hpbtfw21.tlv`: the same set minus `lemonade;lemonadep;martini`.
The 5-device `hmtbtfw10.tlv`: `caihong;fuxi;nuwa;socrates;vermeer`.

**Also measured from linux-firmware `main`** (not in the DB, to widen the
structural sample) **[M]**: `hpbtfw21.tlv` 163,332 B,
`qca/QCA6698/hpbtfw21.tlv` 167,276 B, `hmtbtfw20.tlv` 270,120 B,
`htbtfw20.tlv` 210,704 B, `wcnhpbtfw21.tlv` 152,784 B, `crbtfw32.tlv`
117,664 B — all **PASS** gen-2 — plus `crbtfw21.tlv` 177,060 B, the gen-1
control.

**Total: 12 distinct gen-2 patch byte-identities**, five prefixes (`hp`,
`hmt`, `ht`, `wcnhp`, `cr`), plus one gen-1 control.

NVMs measured (5, all plain type-2 single-set): `hpnv20.bin` 6,319 B /
61 tags (DB MATCH, 11 devices), `hpnv10.bin` 5,753 B / 56,
`hpnv21.bin` 6,610 B / 67, `hpnv21g.bin` 6,450 B / 65,
`hmtnv20.bin` 9,508 B / 95.

---

## 3. The gen-2 layout, measured [M]

The kernel does **not** know this layout. `btqca.c` reads exactly the
24-byte `struct tlv_type_patch` and never validates total file length or any
trailer **[S]**. So the 32-byte header and 36-byte trailer are on-disk
facts, not documentation:

```
offset 0     : 4    tlv_type_hdr      (type=1 low byte, length in bits 8..31)
offset 4     : 24   upstream tlv_type_patch  (btqca.h:120-132, verbatim)
offset 28    : 8    vendor extension — ALL ZERO on every file measured
offset 36    : L    patch body          (opaque)
offset 36+L  : 4    trailer tag
offset 40+L  : 32   SHA-256 digest
                      L = data_length

total_size == 4 + 32 + data_length      (includes the leading 4)
file_size  == 4 + 32 + data_length + 36
```

**The 32-byte header really is "24 + 8 zeros", not a different struct:** the
`[4,36)` range is 62.5% zero bytes on every gen-2 file — exactly `8/32` — and
the 24 upstream bytes are *not* mostly zero, so the split is real. Region
statistics for `hpbtfw20.tlv`:

| range | role | len | entropy | printable | zero % | `0xFF` % |
|---|---|---|---|---|---|---|
| `[0,4)` | `tlv_type_hdr` | 4 | 2.000 | 0.250 | 0.00 | 0.00 |
| `[4,36)` | 24-B struct + 8-B ext | 32 | 2.002 | 0.062 | **62.50** | 0.00 |
| `[36,201524)` | body, opaque | 201,488 | 6.872 | 0.431 | 8.44 | 0.50 |
| `[201524,201560)` | tag + SHA-256 | 36 | 4.892 | 0.306 | 0.00 | 0.00 |

Body entropy ~6.8–7.0 bits/byte across the fleet; `hmt*` is marginally
denser (6.97–6.99) than `hp*` (6.84–6.87). Descriptive only — no argument
rests on it. No disassembly was performed anywhere in this work.

---

## 4. The one invariant that holds everywhere: a payload SHA-256 [M]

```
trailer[4:36] == SHA-256( file[4 : file_size-32] )
```

Holds on **all 12** gen-2 files, across all five prefixes and both families,
across different `rom_build`/`product_id`/build versions. Absent from the
gen-1 control, which carries a 256-byte signature-class tail instead.

The subtlety worth stating precisely: the covered span **starts at 4** (so
the container header is protected) and **ends at `file_size − 32`** (so the
digest is excluded — it cannot cover itself). Therefore the 4-byte tag at
`file_size − 36` is **inside** the digest. Verified both ways:

```
sha256(file[4 : n-32]) == trailer[4:36]   →  True    (all 12 files)
sha256(file[4 : n-36]) == trailer[4:36]   →  False   (all 12 files)
```

A parser that stops the digest before the tag fails on every real file. This
is a genuine correctness trap and the test suite pins both directions.

The kernel never checks this digest **[S]**, yet `qca_download_firmware()`
transmits the whole file — trailer included — in 243-byte segments **[S]**.
So the digest reaches the controller even though Linux does not verify it.
Whether the controller or a production tool consumes it is **[OPEN]**; what
is *measured* is only the byte relation.

---

## 5. Header field behaviour: gen-2 vs gen-1 [M]

| field | gen-2 | gen-1 (`cr`/`ap`) | verdict |
|---|---|---|---|
| `format_version` | 1 | 1 | same |
| `signature` | 0 | 0 | same |
| `download_mode` | 3 (`QCA_SKIP_EVT_VSE_CC`) | 3 | same |
| `reserved1` | 0 | 0 | same |
| `reserved2` | `0x0000` | `0x8000` | **differs** |
| `entry` | `0x00000000` (all files) | real Thumb entry, e.g. `0x000209e4` | **differs** |
| `product_id` | 19 `hp` / 25 `hmt` / 16 `ht` / 10 `cr` | 21 | family-dependent |
| `patch_version` | varies per build: `0x3ed8`, `0x5e81`, `0x2f3e`, `0x4a38`, `0x694d`, `0x5e21`, `0x3a98`, `0x43fc`, `0x3ac0`, `0x8674`, `0x9e3e`, `0x528a` | constant `0x0002` | **differs** |

Two of these matter beyond bookkeeping:

- **`entry` is zero on every gen-2 file.** On gen-1 it carries the address the
  controller jumps to. A Thumb-looking dword *does* sit at body offset `+36`
  (`0x260f8`, `0x25b50`, `0x28b78`, `0x20010`, `0x222cc` on various files),
  but nothing in `btqca.c` reads it — the whole file is handed to
  `qca_download_firmware()` and no body word is interpreted **[S]**. So the
  defensible statement is only: *gen-2 sets `entry = 0` and the body begins
  with a code-like word at `+36`*. What consumes it is **[OPEN]**.
- **`patch_version` stops being a constant.** Gen-1 always `0x0002`
  (effectively a format stamp); gen-2 varies across ≥12 values. The gen-2
  header is *build metadata*, and that is plausibly why a payload digest
  becomes worth carrying.

---

## 6. Version story: F-75's conclusion survives cross-family testing [M]

F-75 concluded the filename's hex digit is the controller's `rom_ver`,
derived from `soc_ver` by the kernel's default formula. Tested here by
applying the *same* default formula to each file's own 16-bit `rom_build`
**[S]** (`btqca.c:777`):

```c
rom_ver = ((soc_ver & 0x00000f00) >> 0x04) | (soc_ver & 0x0000000f);
```

| file | `rom_build` | formula → | digit | match |
|---|---|---|---|---|
| `hpbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `hpbtfw21.tlv` | `0x0201` | `0x21` | 21 | ✔ |
| `hpbtfw10.tlv` | `0x0100` | `0x10` | 10 | ✔ |
| `hmtbtfw10.tlv` | `0x0100` | `0x10` | 10 | ✔ |
| `hmtbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `crbtfw32.tlv` | `0x0302` | `0x32` | 32 | ✔ |
| `htbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `wcnhpbtfw21.tlv` | `0x0201` | `0x21` | 21 | ✔ |

**The F-75 conclusion HOLDS on gen-2, on both families.**

The F-75 caveat carries forward and is not cosmetic: **the kernel never feeds
`rom_build` to this formula.** It applies it to the 32-bit `soc_ver` the
controller reports at runtime, then looks for the resulting filename, and
separately parses `rom_build` out of whatever file it got **[S]**. Two
independent sources that agree is strong *correlational* evidence that
`rom_build` is a stored copy of the ROM low half — not a derivation. Do not
cite it as more than that.

Corroboration from the `.ver` sidecars, read as plain text (all md5-MATCH):

| sidecar | bytes | md5 | content |
|---|---|---|---|
| `hpbtfw20.ver` | 33 | `4d9090849c302b106c34e8539bcb245b` | `BTFW.HSP.2.0.1-00252-HSP_PATCH-1` |
| `hmtbtfw10.ver` | 34 | `60429040cd6a15f655528604a1564414` | `BTFW.HAMILTON.1.0.0-00214-PATCH-1` |
| `hmtbtfw20.ver` (giulia) | 52 | `0fad36bab1fded1af9c196ef2a371d24` | `BTFW.HAMILTON.2.0.1-00265-PATCHZ-1.62251.12.95457.2` |
| `hmtbtfw20.ver` (fuxi) | 51 | `40854415614d31f1035ba57bf60b7d67` | `BTFW.HAMILTON.2.0.0-00613-PATCHZ-1.35836.5.36233.9` |

`HSP` = the QCA2066/QCA6698/WCN6855 family codename; `HAMILTON` = WCN7850.
Both are public WHENCE strings. The two `hmtbtfw20.ver` files differ
(`2.0.1` vs `2.0.0`) — two builds of the same named firmware, consistent
with the DB carrying two `hmtbtfw20.tlv` identities.

---

## 7. No shared base image — an honest negative [M]

Cross-file identity, F-75 method (identical bytes at the same offset over the
common prefix, plus 16-byte-block overlap):

| pair | identity | shared 16-B blocks |
|---|---|---|
| `hmtbtfw20` (270,120) ↔ `hmtbtfw20` (280,628) | 3.21% | 2,409 |
| `hpbtfw21` (146,068) ↔ `wcnhpbtfw21` | 2.94% | 1,140 |
| `hpbtfw21` (163,332) ↔ `wcnhpbtfw21` | 2.87% | 1,260 |
| `hpbtfw21` (146,068) ↔ `hpbtfw21` (163,332) | 2.80% | 1,440 |
| `hpbtfw20` ↔ `hpbtfw10` | 2.67% | 201 |
| `hpbtfw20` ↔ `hpbtfw21` | 2.60% | 46 |
| `hmtbtfw20` (280,628) ↔ `hmtbtfw10` | 2.34% | 41 |
| `hpbtfw20` ↔ `hmtbtfw20` | 2.15% | 49 |

Every pair sits at **2–3%**, i.e. chance level for unrelated byte streams.
There is **no shared base** to find — not across a `rom_build` bump
(`hpbtfw20`↔`hpbtfw21`), not across a family change (`hp`↔`hmt`), and not
between two builds of the *same* named firmware.

This reproduces F-75's negative for `crbtfw20` vs `crbtfw11` (2.60%) and,
importantly, does **not** reproduce F-75's positive result — `crbtfw20`↔
`apbtfw10` at 44% shared base. So F-75's shared-base relationship is specific
to those two families, not a general property.

---

## 8. NVM: a simpler shape than F-75, and a family-specific tag map [M]

F-75 found `cr`/`ap` NVMs use a **type-4 multi-NVM enclosing** header with
several adjacent type-2 sets and a trailing type-3 record, the kernel parsing
only the first set. All five gen-2 NVMs are **plain type-2 single-set**:
no enclosing header, no adjacent set, no trailing type-3. The declared length
is consumed exactly:

| file | bytes | declared | consumed | tags | trailing |
|---|---|---|---|---|---|
| `hpnv20.bin` | 6,319 | 6,315 | 6,315 | 61 | none |
| `hpnv10.bin` | 5,753 | 5,749 | 5,749 | 56 | none |
| `hpnv21.bin` | 6,610 | 6,606 | 6,606 | 67 | none |
| `hpnv21g.bin` | 6,450 | 6,446 | 6,446 | 65 | none |
| `hmtnv20.bin` | 9,508 | 9,504 | 9,504 | 95 | none |

**Kernel-known tags differ from F-75 at two ids:**

| tag | kernel constant **[S]** | `hpnv20` | `hpnv10` | `hpnv21` | `hmtnv20` | F-75 (`cr`/`ap`) |
|---|---|---|---|---|---|---|
| 2 | `EDL_TAG_ID_BD_ADDR` (must be 6) | 6 | 6 | 6 | 6 | 6 |
| 17 | `EDL_TAG_ID_HCI` (≥3) | **6** | **6** | **6** | **6** | 8 or 9 |
| 27 | `EDL_TAG_ID_DEEP_SLEEP` (≥1) | **9** | **9** | **11** | **12** | 1 |

Two hard family signals: tag 17 is **6 B** here vs 8–9 on `cr`/`ap`; tag 27
is **9–12 B** here vs **1 B**. Within `hp`, tag 27 grows with `rom_build`
(nv10 9 → nv20 9 → nv21 11); `hmtnv20` is longer again at 12. What the extra
bytes encode is **[OPEN]**.

Tag-map comparison (by id, content compared by SHA-1 of the payload):

| pair | shared ids | identical content | ids only in first | ids only in second |
|---|---|---|---|---|
| `hpnv20` ↔ `hpnv10` | 55 | 16 | 31, 73, 79, 116, 154, 199 | 204 |
| `hpnv20` ↔ `hpnv21` | 61 | 23 | — (strict subset) | 1, 204, 205, 208, 217, 218 |
| `hpnv20` ↔ `hmtnv20` | 49 | **2** | 40, 43, 50, 51, 84, 90, 92, 150, 174, 179, 196, 200 | 46 ids incl. 54, 60, 146…254 |

Within `hp` the tag map is **stable and incremental** (`hpnv21` is a strict
superset of `hpnv20`'s ids). Across families, only **2 of 49** shared ids
have identical content, and `hmtnv20` carries 46 further ids in the
`198–254` range `hp` never uses. So the NVM *format* is shared but the
*content is family-specific* — `hmtnv20.bin` is not a superset of
`hpnv20.bin`.

Tags unknown to upstream stay **opaque**: reported with a SHA-1 and a 16-byte
preview, labelled "unknown to upstream btqca.c", never guessed. On
`hmtnv20.bin` that is 92 of 95 tags — the honest score.

---

## 9. Discrepancies, recorded rather than smoothed over

1. **`hmtnv20.bin` has at least three circulating builds**: 9,036 B /
   `55dd12492cfde0d8239a67b8e6681e2c` (DB, 4 devices), 9,480 B /
   `68ae344ac1c3` (DB, `caihong`), and 9,508 B /
   `c04972ef999748e51cd6798a4505dc6d` (linux-firmware, measured here). All
   three parse as clean type-2 with `consumed == declared`. The DB's 9,036 B
   is **not** what linux-firmware ships. The exact 9,036 B bytes were not
   obtained; the tag census in §8 is from the 9,508 B build. **[OPEN]**
2. **The DB's third `hpbtfw21.tlv` identity** — 130,680 B /
   `856b729705f932f80677a947634d5daa`, 3 devices
   (`lemonade`/`lemonadep`/`martini`) — was **not** obtained. The closest
   public candidate (`sm8450-mainline/firmware-xiaomi-cupid` →
   `bluetooth/hpbtfw21.tlv`, 125,468 B /
   `1b5ef707ce41e6e8b569c94a34da63a7`) is **not** DB-identical, i.e. a
   different build, so it cannot stand in. **[OPEN]**
3. **The 4-byte trailer tag is not a checksum**: not CRC-32, CRC-32C,
   Adler-32, nor a prefix of SHA-256/SHA-1/MD5 over the body or the digested
   span. Tested on four files, no candidate matched. **[OPEN]**
4. **linux-firmware ships no `qca/hpbtfw20.tlv` or `qca/hpnv20.bin`** (both
   requests returned a 404 HTML page, not a blob). The 11-device
   `hpbtfw20.tlv` exists only in vendor trees. Worth knowing before assuming
   linux-firmware is a complete source for this family.
5. **`hp` is not globally unique in linux-firmware**:
   `qca/QCA6698/hpbtfw21.tlv` exists (`BTFW.HSP.2.1.2-00079-PATCH-1`).
   The prefix→chip mapping holds for the flat `qca/` namespace `btqca.c`
   constructs, not for every directory in the tree. That file *does* obey the
   gen-2 layout (measured, 167,276 B, PASS).

### Fetch failures, recorded

- `TheMuppets/proprietary_vendor_xiaomi` → **HTTP 451** (DMCA,
  2019-08-09-SenseTime-5).
- `TheMuppets/proprietary_vendor_xiaomi_{marble,cupid}`: branches are
  `lineage-22.2`/`23.0`/`24.0` only; their firmware dirs contain no
  `hp*`/`hmt*` files.
- `TheMuppets/proprietary_vendor_oneplus` (default `lineage-19.1`) has no
  `hp*`/`hmt*` `.tlv`; only `lemonade/.../bt/hpnv10.bin` (5,709 B, not DB).
- The lemonade `hpbtfw10.ver` URL returned a GitLab HTML error page
  (2,699 B of `<!DOCTYPE html>`); that sidecar was not measured. The
  `hpbtfw10.tlv` itself fetched correctly and MATCHES.
- `unifreq/openwrt_packit` `files/firmware/qca/hpbtfw21.tlv` is a 33-byte
  file despite listing 160,124 B (an LFS-ish stub); `media.` returned 404.

---

## 10. Reproducing

```bash
cd implementations/qca-bt-gen2
python3 -I make_fixture.py                    # regenerate fixtures (byte-exact)
python3 -m unittest test_hp_fleet_probe -v    # 58 tests, all pass
python3 -I hp_fleet_probe.py <file> --brief   # one file
python3 -I hp_fleet_probe.py --fleet f1 f2 f3 --json out.json
```

Exit status `0` = structural facts / info only; `1` = an error-class
diagnostic (truncation, bad digest, tag overflow, unreadable file). The gen-1
control `crbtfw21.tlv` exits **`0`**: the gen-2 rule fails on it, but the
probe recognises it as gen-1 and reports that as a fact — the discriminator
working, not a bug.

---

## 11. What this changes for the laptop-half work

- **The `hp*`/`hmt*` fleet is now content-characterised, not just
  metadata.** One RE pass covers 11 devices for `hpbtfw20.tlv` and 5 for
  `hmtbtfw10.tlv`; the layout constants are measured and the digest invariant
  is verified, so future work can parse these files with confidence.
- **Do not infer layout from filename.** `crbtfw32.tlv` is the counter-example
  that makes this concrete. Any tool in this repo that branches on `cr`/`hp`/
  `hmt` for layout must be fixed to branch on `total_size − data_length`.
- **The gen-2 digest is a free integrity check** for any future fetch: if
  `trailer[4:36] == SHA-256(file[4 : n-32])` fails, the download is corrupt or
  truncated. That is directly useful for blob acquisition hygiene.
- **NVM content is family-specific**, so `hmtnv20.bin` cannot substitute for
  `hpnv20.bin` in any test or fixture comparison, despite the identical
  container format.
