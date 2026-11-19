# `qca-bt-gen2` — clean-room structural probe for the QCA `hp*`/`hmt*` BT firmware family

Finding **F-76**. This directory extends the lab's first content-level
blob RE (F-75, the `cr*`/`ap*` WCN399x/WCN3988 family in
[`../qca-bt/`](../qca-bt/)) to the **second chip generation**: the QCA2066
(`hp*`) and WCN7850 (`hmt*`) Bluetooth rampatch and NVM blobs.

The one-sentence result: **the F-75 *rule shape* generalises, but its
constants do not — and the generation boundary is temporal, not chip-family
based.**

Full detail: [`fleet-analysis.md`](fleet-analysis.md).
Companion summary: [`../../research/laptop/qualcomm-qca-bt-fleet-content.md`](../../research/laptop/qualcomm-qca-bt-fleet-content.md).

---

## Clean-room statement

Everything here comes from **(a)** public GPL-2.0 kernel sources or **(b)**
my own measurements of the payload bytes. No decompiled or disassembled code
was used, no proprietary documentation was read, and **no proprietary
firmware bytes are stored in this repository**.

Only offsets, lengths, counts, digests and statistics are reported. The patch
body is treated as opaque throughout: the probe reports entropy, printable
ratio and a word histogram, and never claims to know what the code does.

The probe is deliberately **self-contained** — it does not import
`../qca-bt/qca_tlv.py`, so this family's claims stand on their own evidence.
`--cross-check` will shell out to the older parser and report agreement, but
that is a comparison, not a dependency.

### Ground truth read *before* asserting structure (RULE 0)

The F-75 layout rule was **not** assumed to carry over. The public sources
were re-read first, from scratch:

| source | what it establishes | fetched |
|---|---|---|
| `drivers/bluetooth/btqca.h` (`torvalds/linux`, master) | `struct tlv_type_patch` = **24 B** (lines 120–132); `struct tlv_type_nvm` 12-B prefix; `MAX_SIZE_PER_TLV_SEGMENT` = 243; tag ids 2/17/27 | 2026-11-18 |
| `drivers/bluetooth/btqca.c` (same tree) | the field-by-field decode; the `switch` mapping `hp`→QCA2066, `hmt`→WCN7850, `ht`→QCA6390, `wcnhp`→WCN6855; the WCN6855→`hp` fallback; `qca_get_nvm_name_by_board()`; the `rom_ver` formulas; the 243-byte whole-file segment loop | 2026-11-18 |
| linux-firmware `WHENCE` (`git.kernel.org`, `main`) | per-chip driver sections binding `hp`→QCA2066 and `hmt`→WCN7850, with public version strings | 2026-11-18 |

The decisive RULE-0 observation: `btqca.c` reads exactly the 24-byte struct
and **never validates total file length or any trailer**. So the 32-byte
vendor header and the 36-byte trailer are *not* kernel concepts — they are
on-disk facts, and everything about them below is **measured**, not
documented.

---

## Fleet scope

Six DB byte-identities, all fetched and **md5-verified as MATCH** against
`blob-matrix/laptop/sharing-clusters.csv`. Two chip families, four
independent upstream sources.

| file | bytes | md5 | devices | `product_id` | gen-2 rule | F-75 rule | source |
|---|---|---|---|---|---|---|---|
| `hpbtfw20.tlv` | 201,560 | `922473448ce287c8bb5e849998b9ffb7` | 11 | 19 | **PASS** | FAIL (−212) | `sm8450-mainline/firmware-xiaomi-cupid` |
| `hpbtfw21.tlv` | 146,068 | `fac75b203eb19dec5ae026a0e72c7be0` | 8 | 19 | **PASS** | FAIL (−212) | `iLtanaka/firmware-xiaomi-marble` |
| `hpbtfw10.tlv` | 178,532 | `4f28663fa156321c8c8810bca6bb1549` | 3 | 19 | **PASS** | FAIL (−212) | `sm8350-mainline/firmware-oneplus-lemonade` |
| `hmtbtfw10.tlv` | 91,308 | `95bb0d97772c767ee21c0a9253df3caa` | 5 | 25 | **PASS** | FAIL (−212) | `VIKAS9793/vendor_oneplus_giulia` |
| `hmtbtfw20.tlv` | 232,348 | `380da1869e03fc4950d8f067482bec48` | 4 | 25 | **PASS** | FAIL (−212) | FAT16 extract, `..._fuxi` `radio/bluetooth.img` |
| `hmtbtfw20.tlv` | 280,628 | `7c8ee5968e701c07d605e750b3a72d44` | 1 | 25 | **PASS** | FAIL (−212) | `VIKAS9793/vendor_oneplus_giulia` |

Plus, from linux-firmware `main`, to widen the structural sample (none of
these are in the DB): `hpbtfw21.tlv` 163,332 B, `qca/QCA6698/hpbtfw21.tlv`
167,276 B, `hmtbtfw20.tlv` 270,120 B, `htbtfw20.tlv` 210,704 B,
`wcnhpbtfw21.tlv` 152,784 B, `crbtfw32.tlv` 117,664 B — all **PASS** gen-2 —
and `crbtfw21.tlv` 177,060 B, which **PASSES F-75 and FAILS gen-2**.

**12 distinct gen-2 byte-identities** measured in total, plus the gen-1
control. NVM: `hpnv20.bin` (6,319, 61 tags), `hpnv10.bin` (5,753, 56),
`hpnv21.bin` (6,610, 67), `hpnv21g.bin` (6,450, 65), `hmtnv20.bin`
(9,508, 95).

### Chip mapping, and why it is two-source

| prefix | chip | kernel evidence | WHENCE evidence |
|---|---|---|---|
| `hp` | **QCA2066** | `btqca.c:788` `"qca/hpbtfw%02x.tlv"` | `... for QCA2066 chips` → `hpbtfw21.tlv`, `BTFW.HSP.2.1.0-00680-VER_PATCHZ-1` |
| `hmt` | **WCN7850** | `btqca.c:826` `"qca/hmtbtfw%02x.tlv"` | `... for WCN7850 chips` → `hmtbtfw20.tlv`, `BTFW.HAMILTON.2.0.1-00349-WOS_PATCHZ-2` |
| `ht` | QCA6390 | `btqca.c:792` | `... for QCA6390 chips` |
| `wcnhp` | WCN6855 | `btqca.c:823` | `... WCN685x uart interface chips` |

`hp` and `wcnhp` share the **`HSP`** codename (same silicon family,
different package/interface), which is exactly why the kernel has a
documented WCN6855 → `hp` fallback (`btqca.c:848-850`). `HAMILTON` is the
WCN7850 codename.

**Caveat, stated plainly:** `hp` is not globally unique in linux-firmware —
`qca/QCA6698/hpbtfw21.tlv` exists too. The prefix→chip mapping holds for the
flat `qca/` namespace `btqca.c` constructs, not for every directory in the
firmware tree.

---

## The result in one table

The F-75 rule is `4 + 24 + data_length + 256`. On every gen-2 file it fails
by **exactly −212 bytes**. The gen-2 rule is:

```
file_size  == 4 + 32 + data_length + 36
total_size == 4 + 32 + data_length            (includes the leading 4)
trailer[4:36] == SHA-256( file[4 : file_size-32] )
```

`256 − 36 = 220`, `32 − 24 = 8`, `220 − 8 = 212` — a fixed-constant delta,
which is the signature of a **format revision**, not per-file variation.

The digest line is the strongest result here: it holds on **all 12** gen-2
files, across all five prefixes and both families, and is absent from the
gen-1 control. Note the covered span: it ends at `file_size - 32`, so the
4-byte trailer tag is **inside** the digest. Digesting
`file[4 : file_size-36]` fails on every real file — the suite pins both
directions.

### The finding that changes the picture

The generation split is **temporal, not family-based**:

| file | family | F-75 | gen-2 |
|---|---|---|---|
| `crbtfw21.tlv` (177,060) | WCN399x | **PASS** | FAIL (+212) |
| `crbtfw32.tlv` (117,664) | WCN399x | FAIL (−212) | **PASS** |
| `hpbtfw10.tlv` (178,532) | QCA2066 | FAIL (−212) | **PASS** |

A `cr` file uses the gen-2 layout. So any parser keying the layout off the
filename prefix will mis-parse `crbtfw32.tlv`. This probe keys off the
header arithmetic (`total_size − data_length` ∈ {24, 36}) and uses file size
only as a corroborating second check.

### Honest negatives

- **No shared base image.** Every cross-file identity is 2–3% (chance level):
  `hpbtfw20`↔`hpbtfw21` 2.60%, `hpbtfw20`↔`hmtbtfw20` 2.15%,
  `hmtbtfw20`(270,120)↔(280,628) 3.21%. F-75's 44% `cr`↔`ap` positive result
  does **not** recur. Each build is a substantially different binary.
- **The 4-byte trailer tag is not a checksum** — not CRC-32, CRC-32C,
  Adler-32, nor a prefix of SHA-256/SHA-1/MD5. Semantics **[OPEN]**.
- **`entry` is 0 on every gen-2 file** (gen-1 carries a real Thumb entry). A
  code-like dword sits at body offset `+36`; what consumes it is **[OPEN]**.
- **`hmtnv20.bin` has ≥3 circulating builds** (9,036 / 9,480 / 9,508 B);
  only the 9,508 B linux-firmware build was measured.
- **The DB's third `hpbtfw21.tlv` identity** (130,680 B) was not obtained; the
  closest public candidate is a *different* build, so it cannot stand in.

---

## Usage

```bash
python3 -I make_fixture.py                    # regenerate fixtures (byte-exact)
python3 -m unittest test_hp_fleet_probe -v    # 58 tests
python3 -I hp_fleet_probe.py <file> --brief   # one file
python3 -I hp_fleet_probe.py <file> --json out.json
python3 -I hp_fleet_probe.py --fleet f1 f2 f3 --json out.json
python3 -I hp_fleet_probe.py <file> --cross-check ../qca-bt/qca_tlv.py
```

Options: `--brief`, `--json PATH`, `--no-hash`, `--fleet FILES…`,
`--cross-check PATH`.

**Exit status:** `0` = structural facts / info diagnostics only; `1` = at
least one error-class diagnostic (truncation, bad digest, tag overflow,
unreadable file). The gen-1 control `crbtfw21.tlv` exits **`0`** — the
gen-2 rule fails on it but the probe *recognises* it as gen-1 and reports
that as a fact, which is the discriminator working rather than an error.

`--brief` output for a real file:

```
hpbtfw20.tlv: 201560 bytes type=TLV_TYPE_PATCH
  header: product_id 19 rom_build 0x0200 patch_version 0x3ed8 download_mode QCA_SKIP_EVT_VSE_CC entry 0x00000000
  layout: gen2-32byte-header hdr=32 trailer=36  F-75 FAIL(delta -212)  gen-2 PASS
  segments: 830 x 243 B (last 113 B)
  trailer sha256 matches: True
  family: hp -> QCA2066 (filename match: True)
```

### What it checks

- type/length decomposition (type in the low byte — `btqca.c` semantics);
- the full 24-byte upstream `tlv_type_patch` decode at offset 4, plus the
  8-byte vendor extension at `[28:36)`;
- **both** size invariants, reported side by side, never assumed;
- the gen-2 SHA-256 trailer, including the covered-span boundary;
- 243-byte segment math (`ceil(size/243)`, last-segment size, wire overhead);
- single-set and type-4 multi-set NVM walks with the kernel's
  first-set-only semantics, plus tag-length invariants for tags 2/17/27;
- the per-family chip annotation and expected filename;
- a cross-file identity matrix (F-75 method: same-offset bytes + 16-B blocks).

Tags unknown to upstream stay **opaque**: reported with a SHA-1 and a
16-byte preview, labelled "unknown to upstream btqca.c", never guessed. On
`hmtnv20` that is 92 of 95 tags — the honest score.

---

## Fixtures

`.gitignore` excludes `*.bin`, `*.mbn`, `*.b[0-9][0-9]`, so no proprietary
payload can be committed by accident. This directory ships **no real
firmware bytes**. `make_fixture.py` builds nine fixtures from a
deterministic SHA-256 counter-stream tagged per fixture, at **real fleet
magnitudes** (201,560 / 146,068 / 280,628 / 6,319 B …) so segment and tag
counts are realistic:

| fixture | purpose |
|---|---|
| `hpbtfw20_synthetic.tlv` | gen-2, `product_id` 19, `rom_build` 0x0200 |
| `hpbtfw21_synthetic.tlv` | gen-2, `rom_build` 0x0201 |
| `hmtbtfw20_synthetic.tlv` | gen-2, `product_id` 25, non-zero `entry` |
| `hpbtfw20_gen1_synthetic.tlv` | F-75-shaped, proves generation discrimination |
| `hpnv20_synthetic.bin` | type-2 single-set NVM with tags 2/17/27 |
| `hmtnv20_synthetic.bin` | second family's tag plan |
| `hpnv20_multi_synthetic.bin` | type-4 enclosing + two sets + type-3 trailer |
| `hpbtfw20_badtrailer.tlv` | all-zero digest → error path |
| `hpbtfw20_truncated.tlv` | declares more than it holds → error path |

The trailer digest in each fixture is a **real** SHA-256 over that fixture's
own bytes using the same covered span as real files, so the positive path is
genuinely exercised. Regeneration is byte-exact and asserted by the suite.

---

## Test status

```
$ python3 -m unittest test_hp_fleet_probe -v
Ran 58 tests in 2.1s
OK
```

58 tests, all passing. They cover: the documented constants and the
*measured* generation constants; the full header decode; the gen-2 invariant
positive **and** the F-75 invariant negative (delta −212) on the same file;
gen-1 discrimination (including the real `entry`); the digest and its
boundary negative; segment math; NVM single-set, multi-set and trailing
records; the fleet matrix; truncation / bad-digest / unknown-type / empty /
unreadable inputs with exit 1; the rom_ver story; CLI and JSON contracts;
fixture determinism; and a check that the module imports nothing from
`../qca-bt/`.

Bugs found and fixed while building this (recorded because they were real):

1. the fixture generator digested `head[4:]` and excluded the 4-byte tag,
   while real files digest `file[4 : n-32]` — the tag is inside. Caught by
   running the probe against real bytes.
2. `parse_nvm()` built `expected_nvm_name` on a throwaway dict copy using a
   `patch_header` that does not exist for NVM files, so it never reached the
   output. Now derives the rom digit from the basename.
3. `--brief` raised `KeyError` on an unreadable file instead of reporting
   cleanly. Fixed and pinned by a test.
4. `--cross-check PATH` analysed the *parser path* as if it were the input
   file (reporting `unknown-container-type` on `qca_tlv.py` itself) instead
   of running the F-75 parser on the data file. Fixed; three tests pin it.
5. the docs initially claimed the gen-1 control exits `1`; it exits `0`,
   because a recognised gen-1 file is a reported *fact*, not an error. Docs
   corrected and the behaviour pinned by a test.

---

## Value

- **A second, independently-sourced generation of the format is now
  documented**, with 12 byte-identities across five prefixes and two chip
  families, every one md5-MATCHed against the lab DB.
- **The generation rule is a tested predicate, not a filename heuristic.**
  `crbtfw32.tlv` proves the difference matters in practice.
- **One strong new invariant** (the payload SHA-256, with its exact covered
  span) plus **one crisp negative** (no shared base across builds or
  families), both reproducible from fixtures.
- **The kernel's fixed 24-byte view is separated from the on-disk 32/36
  reality**, which is the thing a future contributor is most likely to get
  wrong — and the new `+36`-entry question is flagged rather than assumed.
- **F-75's version story survives cross-family testing**, so the two
  reports now rest on the same conclusion instead of one extrapolated claim.

## Known limits

Only 12 gen-2 patch byte-identities and 5 NVMs were measured. The tag
semantics for 92–95 tags per NVM are unknown to upstream; the 4-byte trailer
tag, the `+36` body word, and the canonical `hmtnv20.bin` build are **[OPEN]**.
No controller was exercised, so nothing here claims runtime behaviour — the
download protocol numbers are computed from the documented 243-byte
segmentation, not observed on a wire.
