# Qualcomm SM4375 Snapdragon 4 Gen 1 — GPU core identification and firmware

Issue #2024. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every number below is command output from this session
(2026-11-20) against the committed 33,917-row matrix and against
`torvalds/linux` master.

## 1. The GPU: Adreno 619 — but SM4375 has no mainline device tree at all

**Verdict: the SM4375 GPU is an Adreno 619, firmware `a619_gmu.bin` +
`a630_sqe.fw` + `a615_zap.mdt`.** That identity is **not new** — it is already
asserted in this repo at `research/laptop/qualcomm-adreno-gmu-content.md:265`
and `implementations/adreno-fleet/gmu-analysis.md:217` ("SoC is Adreno-619-class
(SM4350/SM4375/SM6375/SM7225)"), and it matches public spec sources (cpu-monkey,
notebookcheck: Snapdragon 4 Gen 1 = Adreno 619) [F]. **I cite it; I do not
re-derive it.** The new work in this document is §2 onward.

### 1.1 SM4375 has zero mainline DT coverage — and `talos` is a trap

There is **no** `sm4375.dtsi` and no `holi.dtsi`. I enumerated the whole
directory via the GitHub contents API rather than guessing filenames:

```
arch/arm64/boot/dts/qcom: 664 files
  '4375' -> []      'holi' -> []      '4350' -> []      'fogo' -> []
  '4450' -> ['sm4450-qrd.dts', 'sm4450.dtsi']
```

[F] So SM4375's GPU is **absent** from mainline, not partially supported. That
is a materially different verdict from the SM8350 note (fully described) and the
SM7325 note (described via the `kodiak` parent).

**A wrong turn worth recording as a negative result.** My first guess was that
`talos.dtsi` — a 129,461 B platform file with a complete `adreno-612.0` GPU node
and an `adreno-rgmu-612.0` wrapper node — was the SM4375 platform. It is not.
`talos` is **QCS615**, on **SM6150**:

```yaml
# Documentation/devicetree/bindings/arm/qcom.yaml:1088-1093
- items:
    - enum: [ qcom,qcs615-ride, qcom,talos-evk ]
    - const: qcom,qcs615
    - const: qcom,sm6150
```

```
# talos-evk.dts:11-12
model = "Qualcomm QCS615 IQ 615 EVK";
compatible = "qcom,talos-evk", "qcom,qcs615", "qcom,sm6150";
```

[F] I record this because the failure mode is instructive: `talos.dtsi` yields a
*plausible and self-consistent* Adreno-612 answer that would have been wrong.
The check that caught it was reading the board `.dts` `compatible` rather than
trusting the platform filename [F].

A second false lead: `sm4250.dtsi` exists (1,137 B) but is a CPU-only overlay on
`sm6115.dtsi` (bengal), whose GPU is `adreno-610.0` — also not SM4375 [F].

### 1.2 What the Adreno 619 binding actually requires

`a6xx_catalog.c`: the `revn = 619` entries bind `a630_sqe.fw` + `a619_gmu.bin`
with `zapfw = a615_zap.mdt` [F]:

```c
/* a6xx_catalog.c:869-882 — .machine = "qcom,sm4350" */
.chip_ids = ADRENO_CHIP_IDS(0x06010900),
.revn = 619,
.fw = {
    [ADRENO_FW_SQE] = "a630_sqe.fw",
    [ADRENO_FW_GMU] = "a619_gmu.bin",
},
.zapfw = "a615_zap.mdt",
```

There are **three** `revn = 619` entries with three different chip IDs
(`0x06010900` at `:871` guarded by `.machine = "qcom,sm4350"`, `0x06010901` at
`:896` guarded by `.machine = "qcom,sm6375"`, and a bare `0x06010900` at `:920`
that is the machine-unconstrained fallback). All three share the same firmware
triple [F]. `adreno_info()` (`adreno_device.c:54-62`) skips an entry whose
`.machine` does not match the running board, so the `.machine` field is what
disambiguates identical chip IDs [F].

Note the naming trap: an Adreno **619** loads `a630_sqe.fw` and
`a615_zap.mdt`. Any census keyed on filename-to-revision correspondence gets
this backwards — this is the third SoC in my three GPU notes where the firmware
name carries a different number than the GPU.

## 2. The finding: `fpctzapp` is a fingerprint TZ app, mislabelled `gpu` corpus-wide

This is the new contribution. **`fpctzapp` is not GPU firmware.** It is the
**FPC fingerprint TrustZone application** — `fpc` = Fingerprint Cards AB (a
sensor vendor), `tzapp` = TrustZone application, loading into the QSEE/TEE.

### 2.1 The proof is in the corpus, not in a guess

The matrix itself spells it out. Four devices carry the unambiguous sibling
filename **`fpctzappfingerprint.mdt`** [F]:

| device | filename | bytes | db_path |
|---|---|---:|---|
| Redmi_Note_8 | `fpctzappfingerprint.mdt` | 7,260 | `xiaomi/ginkgo/vendor/firmware` |
| Pixel_4A_5G | `fpctzappfingerprint.mdt` | 7,464 | `google/bramble/vendor/firmware` |
| Pixel_5 | `fpctzappfingerprint.mdt` | 7,464 | `google/redfin/vendor/firmware` |
| Pixel_5A | `fpctzappfingerprint.mdt` | 7,464 | `google/barbet/vendor/firmware` |

And the two naming conventions are **mutually exclusive** [F]:

```
fpctzapp.b00 devices: 12
fpctzappfingerprint.mdt devices: 4
overlap: 0
fingerprint-only: [Pixel_4A_5G, Pixel_5, Pixel_5A, Redmi_Note_8]
```

The 12 plain-`fpctzapp` devices are all Motorola; the 4 spelled-out devices are
the vendors who did not abbreviate. Same app, two naming styles, disjoint device
sets [F]. And every one of the 112 rows is filed at
`motorola/<platform>/modem/image` or `.../vendor/firmware` — a **modem/TZ**
path, never a `gpu/` path [F]. Only `sequence_manifest.bin` sits under
`vendor/gpu/kbc`.

### 2.2 The corpus-wide damage

```
gpu family, all 33,917 rows:   781 rows   88,036,049 B
  of which fpctzapp:           112 rows   34,916,316 B
  share:                        14.3% of rows, 39.7% of bytes
gpu family if corrected:       669 rows   53,119,733 B
```

[F] **Two in five bytes filed under `gpu` in this matrix are a fingerprint TZ
app.** The misfiling is not confined to the matrix: it is also baked into the
derived artifact `research/laptop/sharing-clusters.csv:5261`, which carries
`fpctzappfingerprint.mdt,...,gpu,7260,1,ginkgo` [F]. So any cluster analysis
built on that file inherits the error.

### 2.3 A byte-level rule that catches it without knowing the name

The `b00` header size separates real GPU zap firmware from this impostor [F]:

| family | `b00` size | devices | `52 + n×32`? |
|---|---:|---:|---|
| every `*_zap.b00` (`a610`/`a615`/`a660`/`a740`) | **148** | 22 rows, **all** | `52 + 3×32` — exact |
| `fpctzapp.b00` | 308 | 9 | `52 + 8×32` — exact |
| `fpctzapp.b00` | 512 | 3 | `52 + 460` — **not** a multiple of 32 |

All 22 real GPU `*_zap.b00` files are exactly 148 B, i.e. ELF header (52 B) +
3 program headers (3×32 B) [F]. No `fpctzapp.b00` is 148 B. The 512-byte variant
is not even a bare ELF-header-plus-phdr-table size, so it is not an ELF prefix at
all under this rule [I]. **A single size test on `b00` therefore flags the whole
non-GPU family**, which is useful for any future automated census.

### 2.4 The on-device consequence: 2.5% of the `gpu` bytes are live

For `Moto_G_5G_2024` (`fogo`), the only device carrying this SoC, the 19 `gpu`
rows break down as [F]:

| class | rows | bytes | share |
|---|---:|---:|---:|
| **live** (Adreno 619 set: `a619_gmu.bin`, `a630_sqe.fw`, `a615_zap.mdt`, `.b00`, `.b01`) | 5 | 78,944 | **2.5%** |
| fingerprint TZ app (`fpctzapp.*`) | 9 | 2,998,383 | **94.1%** |
| a660 firmware this SoC cannot load | 3 | 102,460 | 3.2% |
| orphan `a615_zap.b02` + `sequence_manifest.bin` | 2 | 7,688 | 0.2% |
| **total** | **19** | **3,187,475** | 100% |

So a naive reading of "3.19 MB of GPU firmware on this device" overstates the
live GPU payload by a factor of **40x**. The honest figure is **78,944 B**.

## 3. The a660 firmware on `fogo` is byte-identical to the Snapdragon 888's

The three `a660_*` files on this 4-series device match the SM8350's exactly [F]:

```
a660_gmu.bin  55,256 B  md5 179caf2e3b7d5481c3567c2987f5be32
  -> 19 rows / 19 devices, socs: SM6375 x8, blank x3, SM8350 x2,
     SM8350-AC, SM7250, SM7325-AE (778G), SM7325-AE (778G+), SM8250, SM4375
```

There is exactly **one** 55,256-byte `a660_gmu.bin` build in the corpus, shared
by **19 devices across eight distinct SoC labels** — from a 4-series SM4375 to
an 8-series SM8350-AC [F]. Two other builds exist (53,672 B on SM4350; 55,252 B
on QCM6490) [F]. So the a660 GMU image is a
**single shared blob**, not a per-SoC artifact — the same conclusion my SM8350
note reached from the other direction.

But `fogo`'s chip is Adreno 619, so it **cannot execute any of the three**
[F] — they are vendor-partition co-residency, the pattern already documented at
`research/laptop/qualcomm-adreno-a650-fleet.md` §4.

Correction to a tempting inference: `a619_gmu.bin` on this SM4375 device is
**byte-identical** to the one on the SM8350 Xperia_5_III (`9e23c52057bb...`,
32,768 B) [F] — a fleet-wide invariant across a 4-series and an 8-series part,
not a per-SoC build.

## 4. The split-segment law, and the orphan `.b02`

`research/fleet/gpu-bdwlan.md:22-29` already proves the `.mdt`/`.b00` split
format with exact arithmetic, so I cite it rather than re-prove the format [F].
What is new here is that **the naive reconstruction rule fails on this device**:

- `a615_zap`: `b00` 148 + `b01` 6,712 = **6,860** = `a615_zap.mdt` exactly. But
  `a615_zap.b02` (1,984 B) is referenced by **neither** — an orphan segment [F].
- `fpctzapp`: `b00` 512 + `b01` 6,952 = **7,464** = `fpctzapp.mdt` exactly.
  Summing *all* segments gives 2,990,919, which is 2,983,455 B larger than the
  `.mdt` [F].

So "sum every `.bNN` and compare to `.mdt`" is **not** a valid integrity check on
this corpus. Only `b00 + b01` binds to the `.mdt`; `b02` onward are independently
loaded segments (hashes/signatures and payload). `fpctzapp.b02` alone is
1,038,632 B and `.b04` is 1,804,816 B — those are the fingerprint template and
sensor payload, far larger than any `.mdt` [I].

A cross-check that the 6,860-byte `a615_zap.mdt` is a *split-only* variant:
all **7** devices carrying the 6,860 B build also carry the `.b00`/`.b01` split,
while **none** of the **19** devices carrying the 6,708 B build do [F]. The two
build sizes partition cleanly by shipping style — 6,708 B is a self-contained
`.mdt`, 6,860 B is header-plus-segment [I].

## 5. Honest negatives

1. **The GPU identity is prior art.** Adreno 619 is already in-repo at
   `qualcomm-adreno-gmu-content.md:265`; I did not re-derive it and claim no
   credit for it [F].
2. **SM4375 mainline support is zero**, verified by directory enumeration, not
   by guessing filenames [F]. Absence of `sm4375.dtsi` and `holi.dtsi` is a fact
   about `master` on 2026-11-20, not a permanent claim [N].
3. **`talos` is QCS615/SM6150, not SM4375.** Recorded as a negative result
   because its `adreno-612.0` node is a convincing wrong answer [F].
4. **I did not read any `fpctzapp` payload bytes.** The identification rests on
   the corpus's own `fpctzappfingerprint.mdt` sibling name, the mutually
   exclusive device sets, the modem/TZ file paths, and the `b00` size rule — all
   [F] — plus the interpretation of `fpc`/`tzapp` as Fingerprint Cards /
   TrustZone app, which is [I] from the filename and public TZ-app literature.
   Confirming it would need the ELF headers or a strings pass on `fpctzapp.mdt`;
   **not done** [N].
5. **I did not verify that the SM4375 Xperia/QCS615 `adreno-612.0` path is
   irrelevant to SM4375** beyond the `compatible` check; a vendor kernel could
   describe SM4375 differently [N].
6. **The `b00` = `52 + n×32` rule is inferred from sizes only**, not from reading
   the actual ELF headers. The 148 B figure matching `52 + 3×32` exactly on all
   22 real zap files is strong [I], but the program-header count is not directly
   observed [N].
7. **`a660_gmu.bin`'s 19-device md5 identity is a db fact**, not a re-hash of
   the corpus [F].
8. **No claim about whether `fpctzapp` should be reclassified in the committed
   CSVs.** I am reporting the mislabelling, not editing another family's data.

## 6. Recommended corpus corrections (not applied — outside my file wall)

1. Reclassify the 112 `fpctzapp*` rows from `gpu` to `tz` (or a new
   `fingerprint` family). This shrinks `gpu` from 781 rows / 88,036,049 B to
   **669 rows / 53,119,733 B**.
2. Fix `research/laptop/sharing-clusters.csv:5261` for the same reason.
3. Add a `b00`-size sanity check (`== 148` for `*_zap`) to the census builder so
   non-GPU families cannot silently enter `gpu`.

`docs/REPO-STATE-MAP.md:18` still reads "GPU core ID | 27 | NEW | none"; this is
now the third per-SoC GPU note in `research/soc/`, so that verdict is stale for
at least 3 of the 27. Flagged, not edited (shared file).

## Reproduce

```sh
# GPU identity (prior art) — cited, not re-derived
sed -n '265p' research/laptop/qualcomm-adreno-gmu-content.md

# SM4375 has no mainline DT (664-file enumeration, not a guess)
curl -s "https://api.github.com/repos/torvalds/linux/contents/arch/arm64/boot/dts/qcom?ref=master" \
  | python3 -I -c "import json,sys;n=[x['name'] for x in json.load(sys.stdin)];print(len(n),[f for f in n if '4375' in f or 'holi' in f])"

# talos is QCS615, not SM4375
curl -s https://raw.githubusercontent.com/torvalds/linux/master/arch/arm64/boot/dts/qcom/talos-evk.dts | sed -n '11,12p'

# fpctzapp is the fingerprint TZ app: sibling filename, disjoint device sets
python3 -I -c "
import csv
from collections import Counter
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
f=[x for x in r if 'fpctzapp' in x['filename']]
print(Counter(x['filename'] for x in f))
print('fpctzapp.b00 devices',len({x['device'] for x in f if x['filename']=='fpctzapp.b00'}))
print('fpctzappfingerprint.mdt',len({x['device'] for x in f if 'fingerprint' in x['filename']}))"

# damage accounting
python3 -I -c "
import csv
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
g=[x for x in r if x['blob_family']=='gpu']; f=[x for x in r if 'fpctzapp' in x['filename']]
gb=sum(int(x['size_bytes']) for x in g); fb=sum(int(x['size_bytes']) for x in f)
print(len(g),gb,'->',len(g)-len(f),gb-fb, round(100*fb/gb,1),'%')"

# b00 size rule
python3 -I -c "
import csv
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
print('zap b00 sizes',sorted({x['size_bytes'] for x in r if x['filename'].endswith('_zap.b00')}))
print('fpc b00 sizes',sorted({x['size_bytes'] for x in r if x['filename']=='fpctzapp.b00'}))"

# split law + orphan
python3 -I -c "
import csv
d={x['filename']:int(x['size_bytes']) for x in csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')) if x['device']=='Moto_G_5G_2024'}
for f in ('a615_zap','fpctzapp'):
    print(f, d[f+'.mdt'], d[f+'.b00']+d[f+'.b01'], d[f+'.b00']+d[f+'.b01']==d[f+'.mdt'])"
```

All kernel fetches 2026-11-20, `torvalds/linux` master; matrix read the same day.

## Sources

| claim | source | access |
|---|---|---|
| Adreno 619 for SM4375 (prior art) | `research/laptop/qualcomm-adreno-gmu-content.md:265`; cpu-monkey, notebookcheck | 2026-11-20 |
| No `sm4375`/`holi` in 664-file qcom DT dir | GitHub contents API, `arch/arm64/boot/dts/qcom` | 2026-11-20 |
| `talos` = QCS615/SM6150 | `qcom.yaml:1088-1093`, `talos-evk.dts:11-12` | 2026-11-20 |
| `revn = 619` firmware triple, three chip IDs, `.machine` guards | `a6xx_catalog.c:869-945`, `adreno_device.c:54-62` | 2026-11-20 |
| `fpctzappfingerprint.mdt` sibling, disjoint device sets | `coverage-matrix.csv`, 4 rows | 2026-11-20 |
| 112 rows / 34,916,316 B / 14.3% rows / 39.7% bytes | `coverage-matrix.csv` | 2026-11-20 |
| misfiling in derived artifact | `research/laptop/sharing-clusters.csv:5261` | 2026-11-20 |
| `*_zap.b00` = 148 B on all 22 rows | `coverage-matrix.csv` | 2026-11-20 |
| 6,860 B `a615_zap.mdt` ⟺ split shipped; 6,708 B ⟺ not | `coverage-matrix.csv`, 26 rows | 2026-11-20 |
| `.mdt`/`.bNN` split format | `research/fleet/gpu-bdwlan.md:22-29`; Tencent ModKit (public) | 2026-11-20 |
| `a660_gmu.bin` single 55,256 B build, 19 devices | `coverage-matrix.csv` | 2026-11-20 |
| `a619_gmu.bin` byte-identical across SM4375 and SM8350 | `coverage-matrix.csv` | 2026-11-20 |
| vendor partition is a superset | `research/laptop/qualcomm-adreno-a650-fleet.md` §4 | 2026-11-20 |
| `fogo` = moto g 5G (2024) = SM4375 | LineageOS wiki, thecustomrom | 2026-11-20 |
