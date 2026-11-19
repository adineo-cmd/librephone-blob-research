# implementations/pil-manifests — clean-room Qualcomm `*.jsn` PDR manifest parser

A structural parser/validator for the Qualcomm **PDR service-registry
manifest** family (`*.jsn`) — the most widely shared small blobs in the
laptop half of the census (**one analysis covers 17 devices** on a single
md5). It parses the documented grammar, validates every invariant the
public consumers rely on, cross-checks the filename taxonomy against the
mainline kernel's own hardcoded table, and emits the field/service table as
JSON. Pure stdlib; no proprietary material was accessed (clean-room
statement in `jsn_probe.py`).

**Ground truth (fetched 2026-11-18):**

- `torvalds/linux` master `drivers/soc/qcom/qcom_pd_mapper.c` (GPL-2.0-only)
  — the same domain/instance/service table **as C data**, plus
  `SERVREG_QMI_VERSION 0x101` and the implicit `tms/servreg` rule.
- `linux-msm/pd-mapper` (BSD-3-Clause) `json.c`/`json.h`/`pd-mapper.c` —
  the **actual on-disk parser** (`pd_load_map()`), the `.jsn`/`.jsn.xz`
  directory-adjacency discovery, the 127-byte string cap and digit-only
  number rule.
- `drivers/soc/qcom/mdt_loader.c` and `drivers/remoteproc/qcom_q6v5_pas.c`
  — checked and confirmed to contain **zero** `.jsn` references (see
  "honest negative" below).

## The one thing to know first

These files are **not** split-MDT image manifests. They do not name
`.mdt`/`.bNN` segments, list sizes or carry hashes. They are **JSON PDR
service-registry manifests**: a lookup table mapping a QMI *service* to the
*protection domain* that hosts it, plus a QMI instance id. The mainline
kernel does not open them at all — it ships the identical table compiled in
(`qcom_pd_mapper.c`). The file is consumed by userspace `pd-mapper`, which
finds it by **directory adjacency** to a remoteproc's firmware path.

Full detail, citations and the byte-level proof: **`jsn-manifest-analysis.md`**.

## Files

| file | role |
|---|---|
| `jsn_probe.py` | parser/validator + JSON emitter + CLI (`python3 -I jsn_probe.py <file> [--json out.json] [--brief] [--quiet] [--allow-crlf]`; exit 1 on invariant violations, 2 on unparseable input) |
| `make_fixture.py` | deterministic **synthetic** manifest generator (self-made bytes from the established grammar; regenerates `fixtures/`) |
| `fixtures/*.jsn` | synthetic manifests — sizes mirror the measured fleet magnitudes (403/513/515/703/710/713/719 B) so the two-generation split is exercised faithfully. **No vendor bytes**; the comment text is deliberately not the vendor's prose |
| `test_jsn_probe.py` | unittest suite: `python3 -m unittest -v test_jsn_probe` |
| `jsn-manifest-analysis.md` | the analysis: grammar, full key table, suffix taxonomy, two-generation finding, kernel-consumer citation, consistency proofs, [OPEN] list |

## Family scope (measured, `blob-matrix/laptop/sharing-clusters.csv`)

Rows are fleet md5s; every one below was fetched and **md5-verified
byte-exact** (sources and route log in `jsn-manifest-analysis.md` §1).

| md5 | file | bytes | devices | declared domain |
|---|---|---|---|---|
| `5d262bb7661402a8d7ca9724bbb45d46` | `adspr.jsn` | 513 | 17 | `msm/adsp/root_pd` (74) |
| `40d6edf129dec063ca3fe6cb6837488f` | `adspr.jsn` | 403 | 6 | `msm/adsp/root_pd` (74) |
| `a43d66d0549e33cf421e25be06260ce0` | `adspua.jsn` | 703 | 17 | `msm/adsp/audio_pd` (74) |
| `49003ffcd10ec16dee11caad22b11b42` | `cdspr.jsn` | 513 | 17 | `msm/cdsp/root_pd` (76) |
| `0d755b18c24337ebca8313b85f8e8a6c` | `battmgr.jsn` | 516 | 17 | `msm/adsp/charger_pd` (74) |
| `72b46949d078a4f226394931a4345e61` | `modemr.jsn` | 710 | 15 | `msm/modem/root_pd` (180) |
| `8167cdcc892464ba0fed63cd439314a2` | `slpir.jsn` | 513 | 11 | `msm/slpi/root_pd` (90) |
| `de25e460ce0debb53db0bb15a122ac6f` | `slpius.jsn` | 515 | 11 | `msm/slpi/sensor_pd` (90) |
| `cddb328503f04c634cc3251b89dad765` | `adsps.jsn` | 515 | 6 | `msm/adsp/sensor_pd` (74) |
| `f2bd80d5f0b19b5b0d36d28383948149` | `cdspr.jsn` | 403 | 6 | `msm/cdsp/root_pd` (76) |
| `d0bd5030a03f631c9af5060a5645d02e` | `adspua.jsn` | 555 | 6 | `msm/adsp/audio_pd` (74) |
| `bad87ccee828ee70d0281db170985738` | `modemuw.jsn` | 713 | 4 | `msm/modem/wlan_pd` (180) |
| `0492fd466fcf5bf62a3d89ceba83197f` | `modemr.jsn` | 719 | 3 | `msm/modem/root_pd` (180) |
| `c7253d84bff46e4cf5cb0585e9a851c5` | `adsps.jsn` | 405 | 3 | `msm/adsp/sensor_pd` (74) |
| `0039483ebd20685728df72c12d13fee4` | `slpius.jsn` | 405 | 3 | `msm/slpi/sensor_pd` (90) |
| `2439d6872b39e9c1282c572b266665f0` | `slpir.jsn` | 403 | 3 | `msm/slpi/root_pd` (90) |
| `17b878530e8306c3777ead5ec2b84aba` | `modemr.jsn` | 562 | 2 | `msm/modem/root_pd` (180) |
| `6acb8c836e49c5ce08edb3b097517bc0` | `modemr.jsn` | 719 | 1 | `msm/modem/root_pd` (180) |
| `1a4a6904fc55234e68b68ebf4ddefe87` | `wlanpdr.jsn` | 405 | 2 | `msm/modem/root_pd` (180) |

The 17-device set (caihong, cupid, diting, erhai, fuxi, lemonade,
lemonadep, marble, martini, mayfly, mondrian, nuwa, socrates, thor,
unicorn, vermeer, zeus) is **Xiaomi + OnePlus** on SM8250/SM8350/SM8450/
SM8550. Every file above is also published by **linux-firmware**
(`WHENCE`, 114 `*.jsn` entries) — these are already-redistributable
firmware, not secrets.

## Usage

```bash
python3 -I jsn_probe.py vendor/firmware/adspr.jsn
python3 -I jsn_probe.py vendor/firmware/adspr.jsn --brief
python3 -I jsn_probe.py vendor/firmware/adspr.jsn --json out.json --quiet
```

Brief mode prints one line:

```
adspr.jsn: 513B msm/adsp/root_pd inst=74 services=1 stem=adspr [OK 0E/0W]
```

Full mode prints the framing, the derived taxonomy, the domain/instance,
the service table and every diagnostic. Exit codes: **0** valid, **1**
parseable but violating an invariant (wrong instance for the domain,
filename/domain disagreement, unknown version, missing required key), **2**
not JSON / not a file / empty.

Validation is not cosmetic — it cross-checks the manifest against
`qcom_pd_mapper.c`: a manifest declaring `msm/adsp/root_pd` with any
instance other than 74 is an **error**, because a mainline kernel could
never answer that lookup. Filename stems are re-derived (`adspr` → adsp +
`r` → `root_pd`) and compared to `sr_domain`, catching renamed or
misplaced files.

## The suffix taxonomy (measured, 0 contradictions)

`<subsystem><optional u><role letter>`: `r`=root, `s`=sensor, `a`=audio,
`o`=ois, `w`=wlan; the `u` infix marks "not the root PD". So `modemuw` =
modem + u + wlan, `adspua` = adsp + u + audio. `battmgr` and `wlanpdr` are
role-named exceptions. The suffixes are **not** secure/non-secure — a `.jsn`
has no signature, hash or security field at all.

## The two-generation split, resolved

`adspr.jsn` at 403 vs 513 B is **one optional `dcomment` field** (110 bytes),
not a firmware generation. The same holds for `adsps` (405/515), `adspua`
(555/703), `cdspr` (403/513), `slpir` (403/513) and `slpius` (405/515):
after dropping `dcomment` the JSON documents are **equal**. `modemr` is the
one stem that genuinely varies in content (405/406/425/562/710/719/905 B =
different service lists), and off-by-one sizes elsewhere are a trailing
newline (514 vs 513) or CRLF (534 vs 513).

## Honest negative worth stating

Mainline does **not** parse these files.

- `drivers/soc/qcom/mdt_loader.c`: `grep -c -i jsn` → **0**. Split segments
  are derived arithmetically — `sprintf(seg_name + strlen(fw_name) - 3,
  "b%02d", segment)` turns `adsp.mdt` into `adsp.b00`…, no manifest involved.
- `drivers/remoteproc/qcom_q6v5_pas.c`: `grep -c -i jsn` → **0**. Firmware
  selection is `desc->firmware_name`.
- Code search `jsn repo:torvalds/linux` → 2 hits, both spurious.

The compiler-in replacement is `drivers/soc/qcom/qcom_pd_mapper.c`, which
holds the same table as C. Its 19 `qcom_pdm_domain_data` structs are a
**superset** of the 12 distinct tuples found in 71 measured manifests — zero
contradictions. For the three SoCs where a complete firmware directory was
available, the set of shipped `.jsn` files matches the kernel's per-SoC
domain list **exactly** (sm8250, sc8280xp, qcm2290).

## Database type corrections

`coverage-matrix.csv` labels are wrong for this family and the analysis
corrects them (`jsn-manifest-analysis.md` §7). In short: `adspr/adsps/
adspua` are typed `MODEM`, which is wrong (they describe the ADSP);
`battmgr.jsn` is in family `modem` but declares `msm/adsp/charger_pd` (it is
**adsp**); `slpir/slpius` are family `other` but SLPI is a first-class
remoteproc (they should be **slpi**); `wlanpdr.jsn` is family `wifi` but
declares `msm/modem/root_pd` (it is **modem**). Recommended `db_type` for
the whole family: `PDR-MANIFEST` rather than `UNKNOWN`/`MODEM`.

## Test status

```
python3 -m unittest -v test_jsn_probe
→ 40 tests, 40 passing (1 optional real-payload test skipped by default)
```

Coverage: grammar (gen1/gen2/multi-service), every field type, the
two-size variants and the exact 110-byte `dcomment` arithmetic, byte
framing (LF/no-BOM/no-trailing-newline, CRLF detection and downgrade),
the full suffix table, kernel-contract cross-checks (instance table, domain
sets), 13 malformed inputs across both failure classes, exit codes for all
three outcomes, the CLI/JSON contract (strict JSON, quiet, `--brief`), and
fixture determinism (regeneration is byte-identical).

Run against real manifests with:

```bash
JSN_REAL_DIR=/tmp/astro_u/jsn/realall python3 -m unittest test_jsn_probe
```

**71/71 real manifests parsed with zero error-class diagnostics.**

## Value statement

One analysis covers **17 devices** for five files (`adspr`, `adspua`,
`cdspr`, `battmgr`, plus the 11-device `slpi` pair) because the md5 is stable
across the whole fleet. The format is fully specified by GPL/BSD public
source — the *contents* of the table are literally in `qcom_pd_mapper.c` —
so a free implementation can generate a correct manifest for any declared
SoC **without ever looking at a vendor file**. The open cost is not this
family: it is the DSP/modem images (`adsp.mdt` + segments) that the manifest
merely points a directory service at.

## RULE 0 prior-art check (2026-11-18/19, recorded queries)

Searches before building: GitHub code search for `filename:adspr.jsn` (271
hits), `adspua.jsn` (279), `battmgr.jsn` (194), `modemuw.jsn` (181),
`slpius.jsn` (251), `modemr.jsn` (100+ sampled); `servreg jsn` (219 hits);
`jsn repo:torvalds/linux` (2, spurious). **No public tool parses these
files structurally.** The only parsers are:

- `linux-msm/pd-mapper` `json.c` + `pd_load_map()` — the real consumer,
  BSD-3-Clause; it reads only `sr_domain` + `sr_service` and does no
  validation, no taxonomy derivation and no kernel cross-check.
- `drivers/soc/qcom/qcom_pd_mapper.c` — the same data as C, not a file
  parser.
- `nshnt-xyz/chef-cyclo` `tools/servreg-locator/jsn.{c,h}` — a small
  servreg locator, not a manifest validator.

Delta built here: structural validation + filename-taxonomy derivation +
kernel-table cross-check + JSON emission + tests + synthetic fixtures. All
other code-search hits are firmware packagers (distro `firmware-*.bb`,
`proprietary-files.txt`, retro-handheld overlays) and the QTI build script
`tms_builder_servreg.py`, which *emits* these manifests in the vendor build.

Pattern precedent for fixtures: `implementations/qca-bt/` and
`implementations/mediatek/container/` (parser + make_fixture + tests +
README; fixtures regenerable).

## Sibling prior work in this lab

`blob-matrix/desktop/fleet-re/oneplus6-partition-map.md` already noticed
that `image_adspr.jsn` in the OnePlus 6 image equals the 31-device fleet
blob, without identifying what the file was. This component closes that
gap: it is a PDR service registry, not a firmware image manifest.

Not legal advice, not a replacement implementation. Regulatory context:
`../../upstream-contribution/radio-regulatory-hurdles.md`.
