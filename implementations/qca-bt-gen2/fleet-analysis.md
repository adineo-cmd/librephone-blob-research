# Content-level anatomy of the QCA Bluetooth "h-prefix" fleet

**Finding F-76** — the second chip generation of the Qualcomm Bluetooth
firmware family, `hp*` (QCA2066) and `hmt*` (WCN7850), analysed at the byte
level and compared against F-75 (`cr*`/`ap*`, WCN399x/WCN3988) in
[`../../implementations/qca-bt/fleet-analysis.md`](../qca-bt/fleet-analysis.md).

All facts below come from either **(a)** public GPL-2.0 kernel sources, or
**(b)** my own measurements of the payload bytes. Every measurement is
reproducible with the probe in this directory. Nothing here was derived from
decompiled code, disassembly, or a proprietary document.

| | |
|---|---|
| Sources fetched | 2026-11-18 / 2026-11-19 |
| Files measured | 12 distinct gen-2 patch byte-identities, 5 NVM files |
| Probe | [`hp_fleet_probe.py`](hp_fleet_probe.py) |
| Tests | [`test_hp_fleet_probe.py`](test_hp_fleet_probe.py) — 58 passing |
| Payloads | never stored in this repository (see "Fixture policy") |

---

## 0. Ground truth read *before* asserting anything (RULE 0)

The F-75 report established a layout rule for `cr*`/`ap*` files. The honest
first question here is whether that rule is a property of *the QCA BT format*
or of *one build era*. So the kernel source was re-read from scratch rather
than trusting the earlier note.

**What the kernel actually documents** — `drivers/bluetooth/btqca.h`, struct
`tlv_type_patch` (lines 120–132), verbatim:

```c
struct tlv_type_patch {
	__le32 total_size;
	__le32 data_length;
	__u8   format_version;
	__u8   signature;
	__u8   download_mode;
	__u8   reserved1;
	__le16 product_id;
	__le16 rom_build;
	__le16 patch_version;
	__le16 reserved2;
	__le32 entry;
} __packed;
```

That struct is **24 bytes** and it is **all** the kernel knows about the
patch header. `btqca.c` reads exactly those fields and nothing else
(`btqca.c:322-360`): it validates `fw_size >= sizeof(tlv_type_hdr) +
sizeof(tlv_type_patch)`, then copies `total_size`, `data_length`,
`format_version`, `signature`, `download_mode`, `product_id`, `rom_build`,
`patch_version`, `entry` into the download config.

**Consequence, and the single most important structural fact in this
report:** the kernel never validates the file's total length, never looks at
anything past `4 + 24`, and never checks a trailer. The 32-byte vendor
header and the 36-byte trailer are *not* kernel concepts. They are on-disk
facts that must be **measured**, and the measurement is what follows in
§2. This is why the report says "measured" everywhere rather than
"documented".

**Chip-to-filename mapping** — `btqca.c` `qca_uart_setup()`, verbatim:

| line | code | meaning |
|---|---|---|
| 788–791 | `case QCA_QCA2066: snprintf(..., "qca/hpbtfw%02x.tlv", rom_ver)` | `hp` → **QCA2066** |
| 792–795 | `case QCA_QCA6390: ... "qca/htbtfw%02x.tlv"` | `ht` → **QCA6390** |
| 823–825 | `case QCA_WCN6855: ... "qca/wcnhpbtfw%02x.tlv"` | `wcnhp` → **WCN6855** |
| 826–829 | `case QCA_WCN7850: ... "qca/hmtbtfw%02x.tlv"` | `hmt` → **WCN7850** |
| 848–850 | `else if (err < 0 && ... soc_type == QCA_WCN6855)` → `"qca/hpbtfw%02x.tlv"` | documented WCN6855 **fallback to `hp`** |

NVM naming goes through `qca_get_nvm_name_by_board()` (`btqca.c:716-747`),
with `stem = "hpnv"` for QCA2066 (line 882) and the `variant`/`prefix` rules:

```c
variant = ""; prefix = "b";
if (soc_type == QCA_QCA2066) prefix = "";
if (soc_type == QCA_WCN6855 || soc_type == QCA_QCA2066) {
	if ((le32_to_cpu(ver.soc_id) & QCA_HSP_GF_SOC_MASK) == QCA_HSP_GF_SOC_ID)
		variant = "g";
}
if (rom_ver != 0) {
	if (bid == 0x0 || bid == 0xffff)
		snprintf(fwname, max_size, "qca/%s%02x%s.bin", stem, rom_ver, variant);
	else
		snprintf(fwname, max_size, "qca/%s%02x%s.%s%02x", stem, rom_ver,
					variant, prefix, bid);
}
```

That is the *complete* public account of the naming scheme, and it is
reproduced exactly in the probe's `expected_nvm_name()`.

**Second independent confirmation** — linux-firmware `WHENCE` gives a
per-file version string inside a per-chip driver section (fetched
2026-11-18 from
`https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/plain/WHENCE?h=main`):

| WHENCE section | file | Version string |
|---|---|---|
| `... Bluetooth support for QCA2066 chips` | `qca/hpbtfw21.tlv` | `BTFW.HSP.2.1.0-00680-VER_PATCHZ-1` |
| `... Bluetooth support for WCN7850 chips` | `qca/hmtbtfw20.tlv` | `BTFW.HAMILTON.2.0.1-00349-WOS_PATCHZ-2` |
| `... Bluetooth support for QCA6390 chips` | `qca/htbtfw20.tlv` | `BTFM.HST.2.0.0-00943-QCACHROM-1` |
| `... WCN685x uart interface chips` | `qca/wcnhpbtfw21.tlv` | `BTFW.HSP.2.1.0-00660-USB_UART_PATCHZ-6` |

So the two sources agree, independently, that `hp` = QCA2066 and
`hmt` = WCN7850: the kernel's `switch` says it, and the firmware repo's own
section headers say it. Note that `hp` and `wcnhp` share the **`HSP`**
codename — they are the same silicon family in different package/interface
variants, which is exactly why the kernel has a WCN6855→`hp` fallback.

> **Caveat recorded honestly.** `hp` is *not* unique to QCA2066 across all of
> linux-firmware: there is also `qca/QCA6698/hpbtfw21.tlv`
> (`Version: BTFW.HSP.2.1.2-00079-PATCH-1`), i.e. a QCA6698 part shipped
> under the same basename in a different directory. The mapping
> `basename prefix → chip` therefore holds for the *flat* `qca/` namespace
> that `btqca.c` constructs, not for every path in the firmware tree. I
> measured that QCA6698 file too (§2) and it obeys the same gen-2 layout.

---

## 1. Fleet scope and provenance

Six DB byte-identities were fetched and md5-verified. Every one **MATCHES**
the `sharing-clusters.csv` record — no near-misses, no silent substitutions.

| file | bytes | md5 | devices | `product_id` | gen-2 rule | F-75 rule | source |
|---|---|---|---|---|---|---|---|
| `hpbtfw20.tlv` | 201,560 | `922473448ce287c8bb5e849998b9ffb7` | 11 | 19 | **PASS** | FAIL (−212) | `sm8450-mainline/firmware-xiaomi-cupid` → `bluetooth/` |
| `hpbtfw21.tlv` | 146,068 | `fac75b203eb19dec5ae026a0e72c7be0` | 8 | 19 | **PASS** | FAIL (−212) | `iLtanaka/firmware-xiaomi-marble` → `generic/qca/` |
| `hpbtfw10.tlv` | 178,532 | `4f28663fa156321c8c8810bca6bb1549` | 3 | 19 | **PASS** | FAIL (−212) | `sm8350-mainline/firmware-oneplus-lemonade` @ `338eca8f` |
| `hmtbtfw10.tlv` | 91,308 | `95bb0d97772c767ee21c0a9253df3caa` | 5 | 25 | **PASS** | FAIL (−212) | `VIKAS9793/vendor_oneplus_giulia` (Git-LFS via `media.`) |
| `hmtbtfw20.tlv` | 232,348 | `380da1869e03fc4950d8f067482bec48` | 4 | 25 | **PASS** | FAIL (−212) | FAT16 extract from `TheMuppets/..._fuxi` `radio/bluetooth.img` |
| `hmtbtfw20.tlv` | 280,628 | `7c8ee5968e701c07d605e750b3a72d44` | 1 | 25 | **PASS** | FAIL (−212) | `VIKAS9793/vendor_oneplus_giulia` (Git-LFS via `media.`) |

Four independent upstream sources, two chip families, and — importantly —
what the DB calls one filename (`hmtbtfw20.tlv`) is **two different
byte-identities** of different sizes. That is not a fetching error: see §5.

**Also measured, outside the DB** (linux-firmware `main`, to widen the
structural sample):

| file | bytes | md5 | `product_id` | gen-2 | F-75 |
|---|---|---|---|---|---|
| `hpbtfw21.tlv` | 163,332 | `9a6b0cb34a82a7015141dd19b2d779da` | 19 | **PASS** | FAIL (−212) |
| `qca/QCA6698/hpbtfw21.tlv` | 167,276 | `eafd32d10ffe85c06f3782cec03a5241` | 19 | **PASS** | FAIL (−212) |
| `hmtbtfw20.tlv` | 270,120 | `9f728e4a31c495d911e3c429b2152aa2` | 25 | **PASS** | FAIL (−212) |
| `htbtfw20.tlv` | 210,704 | `109ce4287557f1789f2e0ed41e08b5ce` | 16 | **PASS** | FAIL (−212) |
| `wcnhpbtfw21.tlv` | 152,784 | `fce856f8409759e7855a988bff7b70c4` | 19 | **PASS** | FAIL (−212) |
| `crbtfw32.tlv` | 117,664 | `f3cc84610d4a55aa8ab6f6c953772f22` | 10 | **PASS** | FAIL (−212) |
| `crbtfw21.tlv` | 177,060 | `4fceacf111c621d93666aaeafc1eaf56` | 10 | FAIL (+212) | **PASS** |

That is **12 gen-2 files** in total, spanning `hp`, `hmt`, `ht`, `wcnhp`,
`cr` and the QCA6698 subdirectory. Plus the one gen-1 control,
`crbtfw21.tlv`, which is the direct counter-example.

**NVM files measured** (5):

| file | bytes | md5 | tags | `type` | source |
|---|---|---|---|---|---|
| `hpnv20.bin` | 6,319 | `5de36001f431a4d60c641d494a75bb60` | 61 | 2 | cupid (DB MATCH, 11 devices) |
| `hpnv10.bin` | 5,753 | `02b62ecd32ed33449b2d0cbec16c9023` | 56 | 2 | lemonade (DB MATCH, 3 devices) |
| `hpnv21.bin` | 6,610 | `a3314439a3a607df70ba207aee60414b` | 67 | 2 | linux-firmware |
| `hpnv21g.bin` | 6,450 | `f304700cae244f47fd4dd13643b05a5e` | 65 | 2 | linux-firmware |
| `hmtnv20.bin` | 9,508 | `c04972ef999748e51cd6798a4505dc6d` | 95 | 2 | linux-firmware |

> **Discrepancy recorded, not smoothed over.** The DB lists `hmtnv20.bin` at
> **9,036 B** / `55dd12492cfde0d8239a67b8e6681e2c` (4 devices) *and*, for
> `caihong`, at 9,480 B / `68ae344ac1c3`. The linux-firmware copy is
> **9,508 B** — a third size. All three parse as clean type-2 single-set
> NVM with `consumed == declared`. So `hmtnv20.bin` is a filename with at
> least three distinct builds in circulation, and the DB's 9,036 B is *not*
> the version linux-firmware ships. I did not obtain the exact 9,036 B
> bytes; the tag census below is therefore from the 9,508 B build, and the
> difference is flagged **[OPEN]** rather than claimed away.

---

## 2. The gen-2 patch layout — measured, and it is not F-75's

F-75's rule for `cr*`/`ap*` is `file_size == 4 + 24 + data_length + 256`.
Applied to the gen-2 fleet it fails on **every single file by exactly −212
bytes**:

```
4 + 24 + data_length + 256   →  212 bytes too many (delta −212)
4 + 32 + data_length + 36    →  exact match, every time (delta 0)
```

`256 − 36 = 220` and `32 − 24 = 8`; `220 − 8 = 212`. The delta is the same
constant everywhere because both the header and the trailer changed size by
fixed amounts. That is the signature of a **format revision**, not of
per-file variation.

So the measured gen-2 layout is:

```
offset 0        : 4    tlv_type_hdr   (type=1 in low byte, length in bits 8..31)
offset 4        : 24   upstream tlv_type_patch (btqca.h, verbatim)
offset 28       : 8    vendor extension — all zero on every file measured
offset 36       : L    patch body (opaque)
offset 36+L     : 4    trailer tag
offset 40+L     : 32   SHA-256 digest
                        where L = data_length
```

with

```
total_size  == 4 + 32 + data_length      (note: includes the leading 4)
file_size   == 4 + 32 + data_length + 36
```

**Verification that the 32-byte header really is "24 + 8 zeros", and not a
different struct:** on every gen-2 file, bytes `[28:36]` are eight `0x00`.
The probe reports per-range statistics; the `[4,36)` range is 62.5% zero
bytes on all of them, which is exactly `8/32` — i.e. the only zeros in that
range are the extension. The 24 upstream bytes are *not* mostly zero, so
the split is real and not an artefact of an all-zero region.

**Region statistics** (a statistical description of opaque bytes — no
disassembly performed), `hpbtfw20.tlv` as the example:

| range | role | len | entropy | printable | zero % | `0xFF` % |
|---|---|---|---|---|---|---|
| `[0,4)` | `tlv_type_hdr` | 4 | 2.000 | 0.250 | 0.00 | 0.00 |
| `[4,36)` | 24-B struct + 8-B extension | 32 | 2.002 | 0.062 | 62.50 | 0.00 |
| `[36,201524)` | patch body, opaque | 201,488 | 6.872 | 0.431 | 8.44 | 0.50 |
| `[201524,201560)` | tag + SHA-256 | 36 | 4.892 | 0.306 | 0.00 | 0.00 |

Body entropy ~6.8–7.0 bits/byte across the fleet is consistent with
compressed or dense code/data; it is *not* a claim about what the code does.
`hmt*` bodies are slightly denser (6.97–6.99) than `hp*` (6.84–6.87), but
this is a weak, descriptive signal and I do not build any argument on it.

**Honest negative on the 4-byte trailer tag.** I tested whether
`trailer[0:4]` is a checksum or digest prefix of the body. It is **not**
CRC-32, CRC-32C, Adler-32, or a prefix of SHA-256/SHA-1/MD5 over either the
body or the digested span, on any file tested. Its semantics are **[OPEN]**.
The one thing that *is* established is that the tag lies **inside** the
SHA-256's covered span (next section), which is an unusual but verifiable
design choice.

---

### 2.9 Reconciliation with the sibling `hbt-fleet` "44-byte footer"

`implementations/hbt-fleet/hpbtfw20-analysis.md` describes the tail of the same
generation as a **44-byte footer** (8 build-varying bytes + 36 bytes of
hash-class content). That framing is superseded by the layout measured here, and
the disagreement is worth recording because both documents are committed.

The header settles it. `total_size` declares where the data region ends:

| boundary source | value on `hpbtfw20.tlv` | implied trailer |
|---|---|---|
| header `total_size` field | `201,524` | `file_size − total_size = **36 B**` |
| sibling doc ("last 44 bytes") | `201,516` | `44 B` |

The 8 bytes at `[28:36)` are **all zero on every gen-2 file** and sit *inside*
the 32-byte vendor header (24-byte upstream struct + 8-byte extension), i.e.
before the body starts. They are not part of the footer. The sibling doc's
"build-varying prologue" observation concerns bytes inside `[4,28)`, which is
the upstream struct — a different field.

**Resolution: the header is `4 + 32` and the trailer is 36; the "44-byte
footer" mis-assigns 8 header bytes to the tail.** The substantive finding both
documents share — a SHA-256 digest where F-75 had a 256-byte signature-class
tail — is unaffected and is verified here on 12 files.

## 3. The one invariant that does hold everywhere: a payload SHA-256

```
trailer[4:36] == SHA-256( file[4 : file_size-32] )
```

This is the strongest, cleanest result in the report. It holds on **all 12
gen-2 files**, across all five prefixes, across both families, and across
different `rom_build` values, `product_id` values and build versions. It is
absent from the gen-1 control (`crbtfw21.tlv`), which carries a 256-byte
signature-class tail instead and no digest at that position.

The subtle part, and the reason this is worth stating carefully:

- the covered span starts at **4** (after `tlv_type_hdr`, so the header is
  protected);
- it ends at `file_size - 32` (so the **digest itself** is excluded —
  necessarily, since it cannot cover itself);
- therefore the 4-byte **tag at `file_size-36` is inside the digest**.

A naive implementation that digests `file[4 : file_size-36]` — i.e. stops
before the tag — **fails on every real file**. I verified both directions
explicitly:

```
sha256(file[4 : n-32]) == trailer[4:36]   →  True   (all 12 files)
sha256(file[4 : n-36]) == trailer[4:36]   →  False  (all 12 files)
```

This is a genuine correctness trap, and the test suite pins it
(`test_trailer_digest_and_covered_span`, including the negative assertion).

The kernel does not check this digest. It is therefore presumably produced by
Qualcomm's signing/packaging tool and consumed by the controller or by a
production-line tool, not by Linux. That inference is marked **[OPEN]** —
what is *measured* is only the byte relation.

---

## 4. Header field behaviour: gen-2 vs gen-1

Decoding the 24-byte struct on all 12 gen-2 files:

| field | gen-2 value | gen-1 (`cr*`/`ap*`, F-75) | verdict |
|---|---|---|---|
| `format_version` | 1 | 1 | same |
| `signature` | 0 | 0 | same |
| `download_mode` | 3 (`QCA_SKIP_EVT_VSE_CC`) | 3 | same |
| `reserved1` | 0 | 0 | same |
| `reserved2` | `0x0000` | `0x8000` | **differs** |
| `entry` | `0x00000000` | real Thumb entry (e.g. `0x000209e4`) | **differs** |
| `product_id` | 19 `hp` / 25 `hmt` / 16 `ht` / 10 `cr` | 21 `cr` / 21 `ap` | family-dependent |
| `patch_version` | varies per build (`0x3ed8`, `0x5e81`, `0x2f3e`, `0x4a38`, `0x694d`, `0x5e21`, `0x3a98`, `0x43fc`, `0x3ac0`, `0x8674`, `0x9e3e`, `0x528a`) | constant `0x0002` | **differs** |

Two of these are worth dwelling on because they are the *behavioural*
differences between the generations, beyond mere sizes:

**`entry` is zero on every gen-2 file.** On gen-1 the `entry` field carries
the load/entry address the controller jumps to. On gen-2 it is zero
throughout the fleet. A plausible Thumb-looking word does sit immediately
after the header, at file offset **36** — the first four bytes of the body
(e.g. `0x000260f8`, `0x00025b50`, `0x00028b78`, `0x00020010`, `0x000222cc`
on various files). But I have **not** established that the kernel or the
controller reads an entry point from there, and `btqca.c` certainly does
not: it passes the whole file to `qca_download_firmware` and never
interprets a body word. So the statement I can defend is only: *gen-2 sets
`entry = 0` and the body begins with a code-like word at `+36`*. What the
controller does with it is **[OPEN]**.

**`patch_version` stops being a constant.** On gen-1/F-75 it is always
`0x0002` — effectively a format marker. On gen-2 it varies per build across
at least 12 distinct values. Combined with the varying `data_length`, this
says the gen-2 header is *build metadata* rather than a fixed format
stamp. That is consistent with (and probably the reason for) the SHA-256
trailer: once headers carry real per-build data, a payload digest becomes
worth having.

---

## 5. The generation split is temporal, not family-based

This is the finding that most changes the picture, and it is a correction to
a natural but wrong assumption.

The tempting story is "`hp`/`hmt` are the new generation, `cr`/`ap` are the
old one". The bytes say otherwise:

| file | family | F-75 rule | gen-2 rule |
|---|---|---|---|
| `crbtfw21.tlv` (177,060 B) | WCN399x | **PASS** | FAIL (+212) |
| `crbtfw32.tlv` (117,664 B) | WCN399x | FAIL (−212) | **PASS** |
| `hpbtfw10.tlv` (178,532 B) | QCA2066 | FAIL (−212) | **PASS** |
| `htbtfw20.tlv` (210,704 B) | QCA6390 | FAIL (−212) | **PASS** |

`crbtfw32.tlv` is a **`cr` file that uses the gen-2 layout**. So the split
is not `hp`/`hmt` vs `cr`/`ap`; it is **`rom_build`-era / build-date based**.
`crbtfw21` (rom_build `0x0201`, `patch_version` `0x0002`) is an older build
in the old format; `crbtfw32` (rom_build `0x0302`, `patch_version` `0x528a`)
is a newer build of the *same* chip family in the new format. The format
revision tracks *when the firmware was built*, not which chip it targets.

This matters practically: any parser that keys the layout off the filename
prefix will mis-parse `crbtfw32.tlv`. The probe therefore keys off the
*header arithmetic* (`total_size - data_length` ∈ {24, 36}) and uses the
file size only as a corroborating second check — never the filename.

**Cross-family byte identity** (F-75 method: identical bytes at the same
offset over the common prefix, plus 16-byte-block overlap):

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
There is **no shared base image** to find here — not between `hpbtfw20` and
`hpbtfw21` (a `rom_build` bump), and not between `hp` and `hmt` (a family
change). This reproduces F-75's negative result for `crbtfw20` vs
`crbtfw11` (2.60%) and, importantly, does **not** reproduce F-75's positive
result (`crbtfw20`↔`apbtfw10` at 44% shared base). So:

> **Verdict on the F-75 "shared base" question for gen-2: negative.** The
> `hp`/`hmt` fleet shows no evidence of a common compiled base across
> builds or families. Each build is a substantially different binary. This
> is reported as a negative because that is what the bytes show.

The `hmtbtfw20` (270,120) ↔ (280,628) pair is the highest at 3.21% with
2,409 shared blocks — same chip, same `rom_build`, different vendors
(OnePlus giulia vs linux-firmware). Still far from a shared base.

---

## 6. The version story, tested across families

F-75's version conclusion was: the filename's hex digit is the controller's
`rom_ver`, derived from `soc_ver` by the kernel's default formula. Does that
survive on gen-2? The honest way to test it is to apply the *same* default
formula to the file's own 16-bit `rom_build` and see whether it reproduces
the filename digit.

The kernel formula (`btqca.c:777`, default branch):

```c
rom_ver = ((soc_ver & 0x00000f00) >> 0x04) | (soc_ver & 0x0000000f);
```

Result on every gen-2 file:

| file | `rom_build` | formula → | filename digit | match |
|---|---|---|---|---|
| `hpbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `hpbtfw21.tlv` | `0x0201` | `0x21` | 21 | ✔ |
| `hpbtfw10.tlv` | `0x0100` | `0x10` | 10 | ✔ |
| `hmtbtfw10.tlv` | `0x0100` | `0x10` | 10 | ✔ |
| `hmtbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `crbtfw32.tlv` | `0x0302` | `0x32` | 32 | ✔ |
| `htbtfw20.tlv` | `0x0200` | `0x20` | 20 | ✔ |
| `wcnhpbtfw21.tlv` | `0x0201` | `0x21` | 21 | ✔ |

**The F-75 conclusion HOLDS on gen-2**, on both families. The filename digit
is the low half of `soc_ver` in the default encoding.

But the caveat from F-75 must be carried forward honestly, and it is not
cosmetic: **the kernel never feeds `rom_build` to this formula.** It applies
the formula to the 32-bit `soc_ver` the *controller reports at runtime*
(`get_soc_ver()`), then looks for the resulting filename, and — separately —
parses `rom_build` out of whichever file it got. These are two independent
sources that happen to agree, which is strong *correlational* evidence that
`rom_build` is a stored copy of the ROM low half. It is not a derivation.
The probe's `rom_ver_from_rom_build()` docstring says exactly this, and the
report repeats it so nobody cites it as more than it is.

Additional cross-check: the `.ver` sidecar files, read as text, corroborate
the generation and family without any parsing trickery:

| sidecar | bytes | md5 | content |
|---|---|---|---|
| `hpbtfw20.ver` | 33 | `4d9090849c302b106c34e8539bcb245b` | `BTFW.HSP.2.0.1-00252-HSP_PATCH-1` |
| `hmtbtfw10.ver` | 34 | `60429040cd6a15f655528604a1564414` | `BTFW.HAMILTON.1.0.0-00214-PATCH-1` |
| `hmtbtfw20.ver` (giulia) | 52 | `0fad36bab1fded1af9c196ef2a371d24` | `BTFW.HAMILTON.2.0.1-00265-PATCHZ-1.62251.12.95457.2` |
| `hmtbtfw20.ver` (fuxi) | 51 | `40854415614d31f1035ba57bf60b7d67` | `BTFW.HAMILTON.2.0.0-00613-PATCHZ-1.35836.5.36233.9` |

All four MATCH the DB. Note `2.0.1` vs `2.0.0` between the two
`hmtbtfw20.ver` files — two builds of the same named firmware — which is
consistent with §5's "no shared base" result and with the DB having two
`hmtbtfw20.tlv` identities. `HSP` = the QCA2066/QCA6698/WCN6855 family
codename; `HAMILTON` = WCN7850; both are public strings from WHENCE.

---

## 7. NVM: a *simpler* shape than F-75, and a different tag map

F-75 found that `cr*`/`ap*` NVMs use a **type-4 multi-NVM enclosing** header
with several adjacent type-2 sets and a trailing type-3 record, and that the
kernel parses only the first set.

**All five gen-2 NVMs measured are plain type-2 single-set.** There is no
type-4 enclosing header, no adjacent second set, and no trailing type-3
record. The declared length is consumed exactly:

| file | bytes | declared | consumed | tags | trailing |
|---|---|---|---|---|---|
| `hpnv20.bin` | 6,319 | 6,315 | 6,315 | 61 | none |
| `hpnv10.bin` | 5,753 | 5,749 | 5,749 | 56 | none |
| `hpnv21.bin` | 6,610 | 6,606 | 6,606 | 67 | none |
| `hpnv21g.bin` | 6,450 | 6,446 | 6,446 | 65 | none |
| `hmtnv20.bin` | 9,508 | 9,504 | 9,504 | 95 | none |

`consumed == declared` exactly in all five, with no tag overrun and no
residue. This is a **structural simplification** relative to F-75, and it is
a real difference, not a measurement gap. (The probe still handles the type-4
shape correctly — see the `hpnv20_multi_synthetic.bin` fixture — so the
capability is not lost, it simply is not exercised by real gen-2 bytes.)

**Kernel-known tags are present and behave differently from F-75:**

| tag | kernel constant | `hpnv20` | `hpnv10` | `hpnv21` | `hmtnv20` | F-75 (`cr`/`ap`) |
|---|---|---|---|---|---|---|
| 2 | `EDL_TAG_ID_BD_ADDR` (must be 6) | 6 | 6 | 6 | 6 | 6 |
| 17 | `EDL_TAG_ID_HCI` (≥3) | **6** | **6** | **6** | **6** | 8 or 9 |
| 27 | `EDL_TAG_ID_DEEP_SLEEP` (≥1) | **9** | **9** | **11** | **12** | 1 |

Two family-level differences worth stating plainly:

- **Tag 17 is 6 bytes here, vs 8–9 on `cr`/`ap`.** The kernel's documented
  mutation is `data[0] |= 0x80` (inband-sleep) plus a baud byte at `data[1]`
  for WCN3950/WCN3991+ — a class that includes QCA2066 and WCN7850 — so a
  6-byte payload is long enough for the mutation to be meaningful, but the
  field is *shorter* than the older family's. I did not establish what the
  remaining bytes encode. **[OPEN]**
- **Tag 27 is 9–12 bytes here, vs 1 byte on `cr`/`ap`.** The kernel only
  requires ≥1 and ORs `data[0] |= 0x01`. On F-75 the payload is literally
  one byte; here it is a structured blob of 9–12. The extra content is
  **[OPEN]**, but the *length difference is a hard family signal*. Within
  `hp` it grows with `rom_build` (`hpnv10` 9 → `hpnv20` 9 → `hpnv21` 11);
  `hmtnv20` is longer again at 12.

**Tag-map comparison** (by tag id, content compared by SHA-1 of the payload):

| pair | shared ids | byte-identical content | ids only in first | ids only in second |
|---|---|---|---|---|
| `hpnv20` ↔ `hpnv10` | 55 | 16 | 31, 73, 79, 116, 154, 199 | 204 |
| `hpnv20` ↔ `hpnv21` | 61 | 23 | — (subset) | 1, 204, 205, 208, 217, 218 |
| `hpnv20` ↔ `hmtnv20` | 49 | **2** | 40, 43, 50, 51, 84, 90, 92, 150, 174, 179, 196, 200 | 46 ids incl. 54, 60, 146, 152, 157…254 |
| `hpnv21` ↔ `hmtnv20` | 53 | 8 | 40, 43, 50, 51, 84, 90, 92, 150, 174, 179, 196, 200, 204, 218 | 42 ids |

Reading this honestly:

- Within `hp`, the tag map is **stable and incremental**: `hpnv21` is a
  strict superset of `hpnv20`'s tag ids, adding 1, 204, 205, 208, 217, 218.
  `hpnv10`→`hpnv20` is *not* a superset (six ids dropped, one added), which
  is consistent with a generation-boundary change rather than a monotone
  extension.
- Across families (`hp` ↔ `hmt`), only **2 of 49** shared tag ids have
  identical content, and `hmtnv20` carries 46 further ids in the
  `198–254` range that `hp` never uses. So the NVM format is *shared*, but
  the NVM **content is family-specific**. An `hmtnv20.bin` is not a
  superset of an `hpnv20.bin`; they are different configuration sets.
- Only 16 of 55 shared ids are byte-identical between `hpnv20` and `hpnv10`.
  Those 16 are the candidates for cross-build constants — but note that
  includes tag 2 (BD_ADDR) and tag 17 (HCI), which one would *expect* to be
  device/build-specific. I am not going to claim those are "shared
  constants" without knowing what they mean; the honest statement is that
  16 payloads coincide and the semantics of most are **[OPEN]**.

The probe reports every tag with a SHA-1 of its payload and a 16-byte
preview, and marks anything outside {2, 17, 27} as "unknown to upstream
`btqca.c`" rather than guessing. 95 tags for `hmtnv20` means 95 unknowns;
that is the honest score, not a failure.

---

## 8. Download protocol (documented behaviour, computed not executed)

From `btqca.c`, `qca_download_firmware()` sends the **whole file** — container
header and trailer included — in `MAX_SIZE_PER_TLV_SEGMENT = 243`-byte
segments, each framed with a sub-command byte and a length. So the trailer
digest is *transmitted to the controller*, even though the kernel itself
never verifies it. That is another hint (not proof) that the digest is meant
for the controller or a production tool. **[OPEN]**

| file | bytes | segments | last segment |
|---|---|---|---|
| `hpbtfw20.tlv` | 201,560 | 829 × 243 + 113 | 113 |
| `hpbtfw21.tlv` | 146,068 | 601 × 243 + 25 | 25 |
| `hpbtfw10.tlv` | 178,532 | 734 × 243 + 170 | 170 |
| `hmtbtfw10.tlv` | 91,308 | 375 × 243 + 183 | 183 |
| `hmtbtfw20.tlv` (fuxi) | 232,348 | 956 × 243 + 40 | 40 |
| `hmtbtfw20.tlv` (giulia) | 280,628 | 1,154 × 243 + 206 | 206 |

`hmtbtfw20.tlv` at 280,628 B is the largest single BT blob in the fleet —
1,155 segments, i.e. 1,155 round-trips for one firmware download. That is a
concrete, user-visible cost of the format.

---

## 9. Fixture policy and clean-room discipline

The repo's `.gitignore` excludes `*.bin`, `*.mbn`, `*.b[0-9][0-9]`, so no
proprietary payload can be committed by accident. This directory therefore
ships **no real firmware bytes at all**. Instead:

- [`make_fixture.py`](make_fixture.py) generates nine fixtures whose bytes
  are a deterministic SHA-256 counter-stream tagged per fixture, at the
  *real fleet magnitudes* (201,560 / 146,068 / 280,628 / 6,319 B …) so that
  segment counts and tag counts are realistic rather than toy;
- the trailer digest in each fixture is a **real SHA-256** over that
  fixture's own bytes, computed with the same covered span as the real
  files — so the digest-positive path is genuinely tested, not stubbed;
- `hpbtfw20_badtrailer.tlv` has an all-zero digest (error path) and
  `hpbtfw20_truncated.tlv` declares more than it holds (error path);
- `hpbtfw20_gen1_synthetic.tlv` is an F-75-shaped file, proving the probe
  distinguishes the generations from bytes alone;
- `hpnv20_multi_synthetic.bin` is a type-4 multi-set NVM, so the type-4
  code path is tested even though real gen-2 bytes never exercise it.

Regeneration is **byte-exact** and the suite asserts it
(`test_regeneration_is_byte_identical`), so the fixtures are auditable
without shipping a single Qualcomm byte.

I also deliberately avoided the tempting shortcut of treating "it parses"
as "it is correct": every structural claim in this document is paired with a
falsifiable negative — F-75 rule fails by −212, the naive digest span fails,
the cross-family identity is chance-level, `crbtfw32` breaks the
prefix-based story. Those negatives are the load-bearing evidence.

---

## 10. Summary of findings

| # | finding | confidence |
|---|---|---|
| 1 | gen-2 layout is `4 + 32 + data_length + 36`, measured on 12 files; F-75's `+256` fails by exactly −212 on all of them | **measured, high** |
| 2 | `trailer[4:36] == SHA-256(file[4 : file_size-32])` on all 12 gen-2 files; the 4-byte tag is inside the span; the naive span fails | **measured, high** |
| 3 | the 32-byte header is the 24-byte upstream `tlv_type_patch` + 8 zero bytes; the kernel knows only the first 24 | **measured + source, high** |
| 4 | the generation split is **temporal, not family-based** — `crbtfw32.tlv` is gen-2, `crbtfw21.tlv` is gen-1 | **measured, high** |
| 5 | `hp` = QCA2066, `hmt` = WCN7850 (kernel `switch` + WHENCE section headers agree) | **source, high** |
| 6 | the F-75 version story **holds**: default formula on `rom_build` reproduces the filename digit on every gen-2 file | **measured, high** (correlational by construction) |
| 7 | no shared base image: every cross-file identity is 2–3%; the F-75 44% `cr`↔`ap` positive result does **not** recur | **measured, high (negative)** |
| 8 | gen-2 NVMs are plain type-2 single-set with `consumed == declared`; no type-4, no trailing type-3 | **measured, high** |
| 9 | tag 17 is 6 B (vs 8–9) and tag 27 is 9–12 B (vs 1) — hard family signals | **measured, high** |
| 10 | `entry = 0` on all gen-2; a code-like word sits at `+36`; what consumes it is unknown | **measured / [OPEN]** |
| 11 | `patch_version` varies per build on gen-2 (vs constant `0x0002` on gen-1) | **measured, high** |
| 12 | the 4-byte trailer tag is not CRC-32/C/Adler-32/SHA-x/MD5 prefix | **measured (negative)** |

### [OPEN] items, stated as open

1. Semantics of the 4-byte trailer tag — not any common checksum tested.
2. Whether the controller or a production tool verifies the SHA-256 trailer
   (the kernel does not).
3. Meaning of the code-like dword at body offset `+36`, and of `entry = 0`.
4. Payload meaning of tags 17 (6 B) and 27 (9–12 B) beyond the kernel's
   documented bit-OR mutations; and of the 92–95 tags unknown to
   `btqca.c` in each NVM.
5. Which of the ≥3 circulating `hmtnv20.bin` builds (9,036 / 9,480 / 9,508 B)
   is canonical; only the 9,508 B build was measured here.
6. The DB's third `hpbtfw21.tlv` identity (130,680 B /
   `856b729705f932f80677a947634d5daa`, 3 devices: lemonade/lemonadep/martini)
   was **not** obtained. The closest public candidate
   (`sm8450-mainline/firmware-xiaomi-cupid` → `bluetooth/hpbtfw21.tlv`,
   125,468 B / `1b5ef707ce41e6e8b569c94a34da63a7`) is **not** DB-identical, so
   it is a different build and cannot stand in for it.
7. Why `rom_build` agrees with the runtime `soc_ver` formula — whether the
   file is generated from `soc_ver` or `soc_ver` is read from the ROM the file
   was built for. The correlation is solid; the causal direction is not
   established here.

### Fetch failures, recorded rather than hidden

- `TheMuppets/proprietary_vendor_xiaomi` → **HTTP 451** (DMCA, 2019-08-09).
- `TheMuppets/proprietary_vendor_xiaomi_{marble,cupid}`: branches are
  `lineage-22.2`/`23.0`/`24.0` only; their firmware dirs contain no
  `hp*`/`hmt*` files.
- `TheMuppets/proprietary_vendor_oneplus_{lemonade,lemonadep}` in-tree
  `hpnv10.bin` is 5,737 B / `2e03f8f0110c870189f173de93e61c9b`, which the DB
  lists for **one** device; the 3-device `hpnv10.bin` (5,753 B) came from the
  GitLab sm8350-mainline tree instead.
- linux-firmware ships **no** `qca/hpbtfw20.tlv` or `qca/hpnv20.bin`
  (both requests returned a 404 HTML page, not a blob) — so the 11-device
  `hpbtfw20` is *not* in linux-firmware, only in vendor trees.
- The lemonade `hpbtfw10.ver` URL returned a GitLab HTML error page
  (2,699 B of `<!DOCTYPE html>`), so that sidecar was not measured; the
  `hpbtfw10.tlv` itself fetched correctly.

---

## 11. Reproducing

```bash
cd implementations/qca-bt-gen2
python3 -I make_fixture.py                  # regenerate fixtures (byte-exact)
python3 -m unittest test_hp_fleet_probe -v  # 58 tests
python3 -I hp_fleet_probe.py <file> --brief # one file
python3 -I hp_fleet_probe.py --fleet f1 f2 f3 --json out.json
```

Exit status is `0` when only facts/info diagnostics are produced and `1` when
an error-class diagnostic fires (truncation, bad digest, tag overflow). The
gen-1 control `crbtfw21.tlv` exits **`0`**: the gen-2 rule fails on it, but
the probe recognises it as gen-1 and reports that as a fact rather than an
error — the discriminator working, not a bug.

Cross-checking against the F-75 parser is optional and one-way, so this
module's claims stand alone:

```bash
python3 -I hp_fleet_probe.py <file> --cross-check ../qca-bt/qca_tlv.py
```

On gen-2 bytes that reports `returncode: 0` plus the F-75 parser's two
informational notes, i.e. the older parser does not *fail* on gen-2 (it never
validates total length either) — it just doesn't describe the trailer. Worth
remembering when comparing the two tools' output.
