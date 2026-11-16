# implementations/qca-bt — clean-room QCA BT TLV patch/NVRAM parser

A structural parser/verifier for the Qualcomm Bluetooth ROM-patch
(`*.tlv` rampatch) and NVRAM (`*.bin` NVM) container families — the #1
leverage family in the lab's blob census (recon.md top-20 rows 1-6: **one
RE pass covers the BT bring-up of up to 29 devices**). It walks the
documented TLV structure, verifies the structural invariants the mainline
kernel's own download path relies on, decodes every field the GPL header
pins, and emits the record table as JSON. Pure stdlib; no proprietary
material was accessed (clean-room statement in `qca_tlv.py`).

**Ground truth (fetched byte-exact 2026-11-16 from torvalds/linux master):**
`drivers/bluetooth/btqca.h` + `btqca.c` — `struct tlv_type_hdr`
(`type_len` LE32; **type in the low byte, length in bits 8..31**),
`struct tlv_type_patch` (24 B: total_size, data_length, format_version,
signature, download_mode, reserved1, product_id, rom_build, patch_version,
reserved2, entry), `struct tlv_type_nvm` (12-B prefix: tag_id, tag_len,
reserve1, reserve2), the type-4 multi-NVM enclosing-header unwrap, the
three kernel-known NVM tags (BD_ADDR=2, HCI=17, DEEP_SLEEP=27), the chip→
filename switch, and the download protocol (whole file in 243-byte
segments over VSC `0xFC00`/`0x1E`; last segment always acked; synthetic
command-complete injected when VSE is skipped). ELF rampatches
(`msbtfw*.mbn`) are **raw ELF**, not TLV-wrapped — kernel reads bytes
4..6 of the file itself (btqca.c:310-320); handled as a separate path.

## Files

| file | role |
|---|---|
| `qca_tlv.py` | parser/verifier + JSON emitter + CLI (`python3 -I qca_tlv.py <file> [--json out.json] [--hash] [--brief]`; exit 1 on error-class diagnostics) |
| `make_fixture.py` | deterministic synthetic-fixture generator (self-made bytes from the documented layout; regenerates `fixtures/`) |
| `fixtures/*.tlv|.bin|.mbn` | synthetic fixtures — sizes mirror the fleet magnitudes (crbtfw20.tlv 56,180 B; crnv20.bin 3,936 B; apnv10.bin 1,243 B); byte-exact regenerable, the test suite verifies determinism. Note: repo `.gitignore` excludes `*.bin`/`*.mbn` (working-tree artifacts — rerun `python3 -I make_fixture.py`); the `*.tlv` fixtures are not gitignored |
| `test_qca_tlv.py` | unittest suite: `python3 -m unittest -v test_qca_tlv` |

## Fleet scope (coverage-matrix.csv; md5s are upstream-DB facts, payloads NOT on this box)

| file | bytes | md5 (upstream DB) | chip family (btqca.c switch) | linux-firmware |
|---|---|---|---|---|
| `crbtfw20.tlv` | 56,180 | `16077492405d178c5198b86b3cec7eef` | WCN3990/3991/3998 (`cr`) | **absent** from WHENCE |
| `apbtfw10.tlv` | 56,052 | `42a31bb8b2afa5b805dfda78cb1ed4c6` | WCN3988 (`ap`) | present (`BTFM.CHE.2.0.0-00082-QCACHROMZ-1`) |
| `crbtfw11.tlv` | 29,368 | `eae2d0a1fa6690a9eac392a1cef28092` | WCN3990/3991/3998 (`cr`) | **absent** from WHENCE |
| `crnv20.bin` | 3,936 | `bb6ca169095f116ce20029238b4ca4c1` | WCN3990/3991/3998 NVM | **absent** |
| `crnv11.bin` | 2,798 | `7c0db76f1a434d20b3ce3e261b2d00c6` | WCN3990/3991/3998 NVM | **absent** |
| `apnv10.bin` | 1,243 | `4905d516ca6ff77eee8f9f82a17a14ff` | WCN3988 NVM | present (no version string) |

**All six files appear on the identical 29 devices** (each md5 = 29 device
rows): Defy 2021, Edge 30 Neo, FP4, G Stylus 5G-2 2022, Mi A3, Moto E7
Plus, Moto G10, Moto G30, Moto G32, Moto G34 5G, Moto G42, Moto G52,
Moto G 5G 2024, Moto G82 5G, Moto G84 5G, Moto G9, Moto G9 Power, Moto G
Power, Moto G Stylus 5G, Nord CE2, Nord CE3, OnePlus 7 Pro, OnePlus 7,
OnePlus 7T Pro, OnePlus 7T, Phone 1, Pro 1X, Realme 10 Pro, Realme 9 Pro
(SoCs SD460/662/665/680/695/778G+/750G/835/855). Every device carries the
whole multi-family set: the kernel selects at runtime by the controller-
reported ROM version (`qca_read_soc_version` → `rom_ver` math, chip-
specific shifts for WCN3988/WCN3998), not by what the partition ships —
so e.g. OnePlus 7/7T (WCN3998-class) and FP4 (WCN3988-class) both carry
both `cr*` and `ap*` families. Structural consequence: **parsing one md5
frees the parser findings across all 29 devices at once**; per-file RE
(not per-device RE) is the multiplier, exactly as recon.md predicted.

Sibling-family prior work in this lab: `qualcomm-fp6/docs/
bt-firmware-census.md` decoded the FP6 Moselle/EVROS family headers
against the same structs (and observed the vendor 32-byte patch header +
type-4 multi-NVM form on evrnv20.bin); this component generalizes that
decode into a tested, fleet-scoped tool.

## What RE questions the parser enables

1. **Record-boundary analysis** — where the container header ends and the
   patch payload begins (and whether a fleet file uses the upstream
   24-byte header or a vendor-extended one; structurally undecidable from
   the length field alone, flagged `size_note`/[OPEN] until a payload
   lands). This is the prerequisite boundary for any later payload RE.
2. **Patch-segment coverage** — the documented download loop sends the
   WHOLE file in 243-byte segments over VSC `0xFC00` sub-command `0x1E`;
   the parser computes the exact segment map (e.g. 56,180 B → 232
   segments, last 47 B), i.e. the file↔on-wire HCI download stream
   correspondence is reconstructible without hardware.
3. **NVRAM field mapping** — full tag enumeration with stride arithmetic;
   the kernel's three mutation targets are annotated (tag 2 BD-address
   slot — the Android vendor HAL writes the device BD_ADDR there before
   download; tag 17 HCI transport params incl. the chip-dependent baud
   byte position; tag 27 deep-sleep enable). Unknown tags are kept opaque
   (sha1 + 16-byte preview only — facts-not-blobs).
4. **Format contract for a free replacement** — the kernel's acceptance
   criteria for a BT firmware file ARE this structure (`qca_tlv_check_data`
   bounds + segment loop); any future free implementation must emit
   exactly this shape. The parser is that contract, executable and tested.
5. **Fleet diffing** — md5 equality says payload identity; parser output
   adds structural identity (headers, tag sets) across nightlies/devices.

## Honest boundaries [OPEN]

**The parser covers STRUCTURE only.** What each patch payload *does* to
the ROM (the actual patch hunks, the code at `entry`) is beyond public
documentation — the kernel downloads the payload bytes opaquely — and is
NOT attempted here. Specific open items:

- [OPEN] patch payload semantics (what the hunks patch in the ROM) —
  needs payload RE; payloads are not on this box (md5s only, per
  coverage-matrix.csv).
- [OPEN] whether the cr/ap fleet files carry 24-byte or vendor-extended
  patch headers (FP6 census observed 32-byte vendor headers on the
  sibling msbtfw/evr family).
- [OPEN] NVM tag semantics beyond the kernel's 2/17/27 (tag 1 = version
  string is documented for the Moselle family by the FP6 census; cr/ap
  unknown). ~60 opaque tags per fixture-sized NVM; real crnv20.bin
  (3,936 B) will carry a similar tag census.
- [OPEN] product IDs / rom_build values actually carried by the fleet
  files (WHENCE documents versions for the linux-firmware copies; device
  builds differ — the FP6 census found linux-firmware sizes differ from
  on-device builds for the Moselle family too).
- [OPEN] filename↔content codename question: linux-firmware WHENCE lists
  `apbtfw10.tlv` as build `BTFM.CHE.2.0.0-*` (Cherokee naming) while
  wairz's content-derived table maps the `apbtfw` prefix to APA (Apache)
  banners — only a payload settles it (wairz's own postmortem flags
  filename↔content mismatches as a class).

## RULE 0 prior-art check (2026-11-16, recorded queries)

Searches before building (GitHub code search + web). No public tool
combines structural TLV walking + kernel-faithful verification + NVM tag
enumeration + JSON emission + tests:

- `"crbtfw" OR "apbtfw" parser` (GitHub code search, 84 hits) → closest
  prior art: [CrimsonGlory/wairz](https://github.com/CrimsonGlory/wairz)
  `backend/app/services/hardware_firmware/parsers/bt_firmware_banner.py`
  + `data/bt_qca_codenames.yaml` — a **content-banner parser** (extracts
  vendor/version/chipset from banners; filename-prefix→codename table
  CMC/CHE/APA/HAS/MOS; postmortem documents banner-at-end scanning and a
  "filename↔content mismatch" flag). It does NOT walk TLV record
  structure (their postmortem: `.tlv` files "returned family=unknown"
  until the banner scan was added; it never parses records). Delta built:
  structural record walk + verification + NVM tags, complementary to
  their banner layer. All other code-search hits are packaging manifests
  (TheMuppets/LineageOS vendor.mk `crbtfw21.tlv` lines, fs_config lists —
  incl. board-variant `crnv21.b71` naming in the wild, confirming
  `qca_get_nvm_name_by_board`'s output form) and one kernel backport
  patch (Emilelu/UniXNU-mondrian) — zero structural analysis.
- `"qca tlv firmware parser"` / `"btqca parse"` — the kernel's own
  `btqca.c`/`btqca.h` (GPL, fetched 2026-11-16, the ground truth cited
  above) is the only public TLV-structure documentation; BlueZ has no QCA
  TLV parser (bluez-firmware is Broadcom-only). The lab's
  `qualcomm-fp6/tools/bt_tz_analyze.py` decoded the sibling Moselle/EVROS
  family headers (results doc committed) but is a FP6-census script, not
  a fleet component with tests/fixtures.
- [qualcomm-linux/qcom-linux-testkit](https://github.com/qualcomm-linux/qcom-linux-testkit)
  `Runner/utils/lib_bluetooth.sh` — filename-family matcher
  (msbtfw/cmbtfw/apbtfw/crbtfw/htbtfw/hmtbtfw/hpbtfw/wcnhpbtfw + nvm
  stems) — corroborates the family list parsed here; not a parser.
- Repo-internal (implementations/README.md, 2026-11-16): "Qualcomm
  Bluetooth ROM patch .tlv format reverse engineering crbtfw apbtfw — no
  dedicated RE writeup of the QCA .tlv patch format exists" — confirmed
  again this session and sharpened: the one adjacent tool is wairz's
  banner parser, named above.
- Pattern precedent for fixtures: `implementations/mediatek/container/`
  (parser + make_fixture + tests + README; fixtures regenerable).

## Test results

`python3 -m unittest -v test_qca_tlv` — **30 tests, all passing** (2026-11-16):
struct sizes vs btqca.h (24-B patch header, 12-B NVM tag prefix), type/
length decomposition (type low byte / length bits 8..31), full patch-
header field decode at fleet magnitude (56,180 B → 232×243-B segments,
last 47 B), single-set + multi-set (type-4) NVM walks with kernel
first-set-only semantics, kernel-known tag annotations, opaque-tag
handling, truncation/length-mismatch/unknown-type error paths (exit 1),
raw-ELF msbtfw path, per-chip rom_ver math (default + WCN3988 + WCN3998
formulas, u8 truncation modelled), fixture determinism, and the JSON/
brief CLI contracts. Fixture generation is deterministic (SHA-256 counter
stream); regeneration reproduces every fixture byte-for-byte.

Not legal advice, not a replacement implementation: this component
documents the documented container format. Regulatory/legal hurdles for
actually replacing radio firmware: `../../upstream-contribution/
radio-regulatory-hurdles.md`.
