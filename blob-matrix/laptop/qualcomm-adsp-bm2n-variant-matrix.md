# Qualcomm ADSP `bm2nXX.bin` — variant matrix (measured)

Evidence class: **MEASURED PAYLOADS**. Every md5 in Table 2 was computed locally over bytes fetched
from a public repository on 2026-11-18; nothing in the matrix is copied from a manifest. Sizes in
Table 2 are the sizes of the fetched files (and match the git tree entry sizes reported by the
GitHub tree API for the same path/branch). Table 1's "DB" column is metadata from
`upstream-contribution/blob-database/coverage-matrix.csv` and is labelled as such. Payload bytes were
kept outside the repo in `/tmp/astro_u/hunt/`; only this document is committed.

## Table 1 — the six DB identities, and whether the DB-identical payload exists publicly

`upstream-contribution/blob-database/coverage-matrix.csv` records these identities under
`vendor/lib/rfsa/adsp/`:

| file | DB bytes | DB md5 (`md5_db`) | DB devices | DB-identical payload located publicly? | source |
|---|---|---|---|---|---|
| bm2n06.bin | 864,824 | 9010bb1a7c08222a058aaef7edd938c6 | 25 | **YES** | `TheMuppets/proprietary_vendor_oneplus@lineage-19.1` — `sm8350-common/proprietary/vendor/lib/rfsa/adsp/bm2n06.bin` |
| bm2n08.bin | 3,091,896 | 1275a2d212e5bccce734d3055ff10156 | 25 | **YES** | `TheMuppets/proprietary_vendor_oneplus@lineage-19.1` — same dir |
| bm2n12.bin | 2,623,528 | 5c86c8fcc7451f51e11d38276253aac8 | 26 | **YES** | `TheMuppets/proprietary_vendor_oneplus@lineage-19.1` — same dir |
| bm2n13.bin | 1,106,944 | bf635d9084b54633526f9ad8a84d299b | 25 | **YES (found this run)** | `TheMuppets/proprietary_vendor_motorola@lineage-19.1` — `sm7325-common/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin` |
| bm2n14.bin | 103,168 | 805176afaae27821520b79647fa5d498 | 26 | **YES** | `TheMuppets/proprietary_vendor_oneplus@lineage-19.1` — same dir |
| bm2n15.bin | 1,082,856 | 2ce8163cda60f33cbf2b50f03a3d0ea1 | 26 | **YES** | `TheMuppets/proprietary_vendor_oneplus@lineage-19.1` — same dir |

The OnePlus `sm8350-common` tree supplied five of the six but ships a *different* `bm2n13.bin`
(1,082,824 B / `2d267761f3291c9ca4a7850ab0ef1966`) — that is why one identity was missing.
The DB-identical `bm2n13.bin` was found in the Motorola `sm7325-common` tree and independently
confirmed in Sony, Nothing, Fairphone, OnePlus (`lineage-22.0+`) and ArrowOS trees.

Verification of the recovered file:

```
size    1,106,944
md5     bf635d9084b54633526f9ad8a84d299b   <- equals md5_db
sha256  90f4d8b0fe1b20f99d15b34f61dab558bec5e37b0ce72f94c16fa5e3eb8b9dc9
```

## Table 2 — full variant matrix (measured)

Every distinct `(filename, bytes, md5)` observed. "DB?" = whether that exact md5 appears in
`coverage-matrix.csv` for that filename. All fetches 2026-11-18.

| file | bytes | md5 | DB? | representative source (repo @ branch → path suffix) |
|---|---|---|---|---|
| bm2n06.bin | 864,824 | 9010bb1a7c08222a058aaef7edd938c6 | yes | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1` (`sm8350-common/…/rfsa/adsp/`); also `proprietary_vendor_motorola` @ `lineage-19.1` (`sm7325-common/…`), `_sony_sm8350-common` @ `lineage-20`..`24.0`, `_sony_sm6375-common` @ `24.0`, `_oneplus_sm6375-common` @ `24.0`, `TheMuppets/proprietary_vendor_oneplus_dre` @ `22.1` |
| bm2n06.bin | 836,968 | 8f8a96f2647444582a68f50d6dace25a | yes (Xiaomi/Nothing family) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `lineage-22.2`; `_xiaomi_diting` @ `24.0`; `_motorola_sm8475-common` @ `lineage-20` |
| bm2n08.bin | 3,091,896 | 1275a2d212e5bccce734d3055ff10156 | yes | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`; `_motorola_sm7325-common` @ `20`..`24.0`; `_sony_sm8350-common` @ `20`..`24.0` |
| bm2n08.bin | 3,059,736 | 44e31e18b0c9b35ca3522ba9d2b180fc | yes (Mi 12S/12T Pro/Poco F5 class) | `TheMuppets/proprietary_vendor_motorola_sm8475-common` @ `lineage-20`; `_xiaomi_marble` @ `22.2`; `_xiaomi_diting` @ `24.0` |
| bm2n08.bin | 3,059,736 | d3e4f74372a9a418bdba3b5d34ac3515 | yes (Mi 12 / Mi 12 Pro) | `TheMuppets/proprietary_vendor_xiaomi_cupid` @ `lineage-22.2` — **same size as the row above, different bytes** |
| bm2n08.bin | 3,063,776 | aabcad457a39a05e7c336002562f607d | yes (Phone 2) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `lineage-22.2`..`23.2` |
| bm2n12.bin | 2,623,528 | 5c86c8fcc7451f51e11d38276253aac8 | yes | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`; `_motorola_sm7325-common` @ `24.0`; `_fairphone_FP5` @ `lineage-21`; `_nothing_Spacewar` @ `22.1`; `_sony_sm8350-common` @ `20`..`24.0` |
| bm2n12.bin | 1,638,360 | b92a2ba4418d76c2132242342789a5e4 | yes (SM8475 class) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `22.2`; `_motorola_sm8475-common` @ `20`; `_xiaomi_mayfly` @ `22.2`; `_xiaomi_diting` @ `24.0` |
| bm2n12.bin | 2,359,272 | f87d78518cf940b7c79d0e02bd7369c4 | yes (Nord CE4 / `benz`) | `TheMuppets/proprietary_vendor_oneplus_benz` @ `lineage-22.2`..`24.0` |
| bm2n13.bin | 1,106,944 | **bf635d9084b54633526f9ad8a84d299b** | **yes** | `TheMuppets/proprietary_vendor_motorola` @ `lineage-19.1` (`sm7325-common/…`); confirmed in `_motorola_sm7325-common` @ `20`..`24.0`, `_motorola_sm6375-common` @ `22.2`..`24.0`, `_sony_sm8350-common` @ `20`..`24.0`, `_sony_sm6375-common` @ `24.0`, `_fairphone_FP5` @ `lineage-21`, `_nothing_Spacewar` @ `20`..`24.0`, `_oneplus_dre` @ `22.1`..`24.0`, `_oneplus_sm8350-common` @ `22.0`..`24.0`, `sony-sagamidev/vendor_sony_sm8350-common` @ `lineage-20`, `ArrowOS-Devices/android_vendor_motorola_sm7325-common` @ `arrow-13.1` |
| bm2n13.bin | 1,082,824 | 2d267761f3291c9ca4a7850ab0ef1966 | **no** (see note) | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`; `_oneplus_sm8350-common` @ `lineage-20`,`21`; `bheatleyyy/vendor_oneplus_oneplus9rt` @ `topaz`; `Kscope-Devices/android_vendor_oneplus_sm8350-common` @ `sunflowerleaf`; `nattolecats/proprietary_vendor_xiaomi_veux` @ `lineage-21` |
| bm2n13.bin | 1,339,032 | ea1abfc1dcb0cfd5aab2055ccb5bb4a3 | yes (SM8475 class) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `22.2`..`23.2`; `_motorola_sm8475-common` @ `20`..`23.2`; `_xiaomi_mayfly` @ `22.2`; `xiaomi_marble` @ `22.2` |
| bm2n14.bin | 103,168 | 805176afaae27821520b79647fa5d498 | yes | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`; `_motorola_sm7325-common` @ `20`..`24.0`; `_nothing_Spacewar` @ `22.1`; `_fairphone_FP5` @ `lineage-21`; `_sony_sm8350-common` @ `20`..`24.0` |
| bm2n14.bin | 1,339,032 | 281755c08b98e757f00586d0052132b1 | yes (SM8475 class) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `22.2`; `_motorola_sm8475-common` @ `20`; `_xiaomi_mayfly` @ `22.2` |
| bm2n15.bin | 1,082,856 | 2ce8163cda60f33cbf2b50f03a3d0ea1 | yes | `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1`; `_motorola_sm6375-common` @ `24.0`; `_nothing_Spacewar` @ `22.1`; `_sony_sm8350-common` @ `20`..`24.0` |
| bm2n15.bin | 1,339,032 | 281755c08b98e757f00586d0052132b1 | yes (SM8475 class) | `TheMuppets/proprietary_vendor_nothing_Pong` @ `22.2`; `_motorola_sm8475-common` @ `20`; `_xiaomi_diting` @ `24.0` |
| *(cross-file)* bm2n54.bin | 1,082,824 | 2d267761f3291c9ca4a7850ab0ef1966 | yes, but under a different filename | `TheMuppets/proprietary_vendor_nothing_Pong` @ `lineage-22.2` — byte-identical to the 1,082,824 B `bm2n13.bin` above |

Notes on the "no" row: `2d267761f3291c9ca4a7850ab0ef1966` is *not* recorded against `bm2n13.bin` in
the DB, but it *is* in the DB — as `bm2n54.bin` (1082824 B) on `nothing/Pong`. Measured directly
against the Pong tree: identical bytes. So the OnePlus/SM8350 `bm2n13.bin` revision is a live blob
in the same fleet, recorded upstream under a different name.

Distinct measured byte-identities per filename:

| file | distinct md5 measured | DB claims |
|---|---|---|
| bm2n06.bin | 2 | 2 |
| bm2n08.bin | 4 | 4 |
| bm2n12.bin | 3 | 3 |
| bm2n13.bin | 3 (two of them DB-`bm2n13`, one re-used as `bm2n54`) | 2 |
| bm2n14.bin | 2 | 2 |
| bm2n15.bin | 2 | 2 |

15 distinct md5s total across the 16 measured rows (`281755c08b98e757f00586d0052132b1` is shared by
the bm2n14 and bm2n15 SM8475 rows, and by bm2n16 on the same tree).

## What this means

- **Filename ≠ identity, again.** `bm2n13.bin` has at least three public byte-identities
  (1,106,944 / 1,082,824 / 1,339,032 bytes, three different md5s) under one name. Same shape as
  F-75 for `crbtfw21.tlv`. Size alone is also unsafe: `bm2n08.bin` exists at 3,059,736 bytes with
  **two different md5s** (`44e31e18…` on SM8475/Xiaomi 12S-class vs `d3e4f743…` on Xiaomi 12/12 Pro),
  so even `(name, size)` is not a key. Only the md5 is.
- **Branch is a version axis, not just a build axis.** `TheMuppets/proprietary_vendor_oneplus_sm8350-common`
  ships `bm2n13.bin` at 1,082,824 B on `lineage-20`/`21` and at 1,106,944 B from `lineage-22.0` onward —
  the *same repo* moved to the other revision. Anyone who probes one branch of a tree and generalises
  gets the wrong answer; this is exactly how the 1,082,824 variant got mistaken for "the" file.
- **For the "one RE pass informs N devices" argument:** an md5 covers exactly the devices that carry
  that md5 — no more. Here the DB's 25 `bf635d90…` rows are one binary and one RE pass genuinely serves
  all 25 devices. A *filename* covers up to 32-34 devices but spans 2-4 distinct binaries, so a
  filename-scoped claim would overstate coverage by 7-9 devices and, worse, attribute findings from one
  binary to devices running a different one. Leverage should be quoted per-md5 (25 devices for
  `bf635d90…`), with the filename as a *search* key only.
- The fleet is also not monolithic in count: `bm2n00`-`bm2n58` appear on the SM8475 trees while the
  SM7325/SM8350/SM6375 trees carry only `bm2n06`/`08`/`12`-`15`. The six files in scope are a small
  intersection of a much larger per-SoC set.

## Mission 1 attempt log — finding the DB-identical bm2n13.bin

Objective: a public file named `bm2n13.bin`, 1,106,944 B, md5 `bf635d9084b54633526f9ad8a84d299b`.

Method: `gh api repos/<owner>/<repo>/git/trees/<branch>?recursive=1` and filter paths matching
`bm2n`, using the DB size as the candidate filter; then raw-fetch via the contents API with retries.

DB-derived target devices (from `coverage-matrix.csv`, column `device`): OnePlus 9 / 9 Pro / 9RT /
Nord 200 / Nord CE2 / Nord CE3, Sony Xperia 5 III / 10 IV / 10 V, Motorola Edge 20 / Edge 2021 /
Edge 30 / 30 Fusion / 30 Neo / G200 / G34 5G / G82 5G / G84 5G / G Stylus 5G / G 5G 2024 / G Stylus
5G (2022) / Edge 30 Fusion, Realme 9 Pro / 10 Pro, Fairphone FP5, Nothing Phone (1).

| # | repo | branch(es) probed | result |
|---|---|---|---|
| 1 | `TheMuppets/proprietary_vendor_oneplus` | `lineage-18.0`, `18.1`, `19.0` | no `bm2n*` at all (pre-SM8350 trees) |
| 2 | `TheMuppets/proprietary_vendor_oneplus` | `lineage-19.1` | `sm8350-common/…/bm2n13.bin` = 1,082,824 → md5 `2d267761…` **mismatch** (this is the known near-miss) |
| 3 | `TheMuppets/proprietary_vendor_sony` | `lineage-18.0`, `18.1`, `19.0`, `19.1` | no `bm2n*` (monolithic repo only carries older devices; Xperia trees are in split `_sm8350-common`) |
| 4 | `TheMuppets/proprietary_vendor_motorola` | `lineage-18.0`, `18.1`, `19.0` | no `bm2n*` |
| 5 | `TheMuppets/proprietary_vendor_motorola` | `lineage-19.1` | `sm7325-common/…/bm2n13.bin` = **1,106,944** → md5 `bf635d9084b54633526f9ad8a84d299b` **MATCH** |
| 6 | `TheMuppets/proprietary_vendor_fairphone` | `lineage-18.1`, `19.1` | no `bm2n*` (FP2/FP3/FP4 only; FP5 is a split repo) |
| 7 | `TheMuppets/proprietary_vendor_realme` | `lineage-17.1` | no `bm2n*` |
| 8 | `TheMuppets/proprietary_vendor_motorola_sm7325-common` | `lineage-20`,`21`,`22.0`,`22.1`,`22.2`,`23.0`,`23.1`,`23.2`,`24.0` | 1,106,944 on every branch; fetched `20` and `24.0` → `bf635d90…` confirm |
| 9 | `TheMuppets/proprietary_vendor_motorola_sm6375-common` | `lineage-22.2`,`23.0`,`23.1`,`23.2`,`24.0` (`22.1` tree 404) | 1,106,944; fetched `22.2` and `24.0` → `bf635d90…` confirm |
| 10 | `TheMuppets/proprietary_vendor_sony_sm8350-common` | `lin-20`..`24.0` | 1,106,944; fetched `20` and `24.0` → `bf635d90…` confirm |
| 11 | `TheMuppets/proprietary_vendor_sony_sm6375-common` | `lineage-24.0` | 1,106,944; fetched → `bf635d90…` confirm |
| 12 | `TheMuppets/proprietary_vendor_oneplus_sm8350-common` | `20`,`21`,`22.0`..`24.0` | **1082824 on 20/21, 1106944 from 22.0**; fetched `21`,`22.0` → both variants measured |
| 13 | `TheMuppets/proprietary_vendor_nothing_Spacewar` | `20`,`22.1`,`22.2`,`23.0`,`23.2`,`24.0` | 1,106,944; fetched `20`,`22.1`,`23.2` → `bf635d90…` confirm |
| 14 | `TheMuppets/proprietary_vendor_nothing_Pong` | `22.2`,`23.0`..`23.2` | 1,339,032 (different generation); fetched `22.2`,`23.2` → `ea1abfc…` (DB `bm2n13` yes, but not the 1.1 MB identity) |
| 15 | `TheMuppets/proprietary_vendor_oneplus_dre` | `22.1`..`24.0` | 1,106,944; fetched `22.1` → `bf635d90…` confirm |
| 16 | `TheMuppets/proprietary_vendor_fairphone_FP5` | `21`,`22.0` | 1,106,944; fetched `21` → `bf635d90…` confirm |
| 17 | `sony-sagamidev/vendor_sony_sm8350-common` | `lineage-20` | 1,106,944; fetched → `bf635d90…` confirm (independent org) |
| 18 | `ArrowOS-Devices/android_vendor_motorola_sm7325-common` | `arrow-13.1` | 1,106,944; fetched → `bf635d90…` confirm (independent org) |
| 19 | `schqiushui/android_vendor_motorola_sm8350-common` | `fourteen` | 1,106,944 (tree; not fetched — match already established) |
| 20 | `moto-corfur/vendor_motorola_corfur`, `random-stuffimpasta/vendor_motorola_sm6375-common` | `lineage-20`, `YAAP` | 1,106,944 (tree entries only) |
| 21 | `TheMuppets/proprietary_vendor_oneplus_benz` | `22.2`..`24.0` | no `bm2n13`; only `bm2n12` at 2,359,272 |
| 22 | `TheMuppets/proprietary_vendor_realme_luigi`, `_realme_oscar`, `_realme_oscarru` | `21`..`24.0` | no `rfsa/adsp/bm2n*` in tree |
| 23 | `TheMuppets/proprietary_vendor_oneplus_larry`, `_xiaomi_diting`, `_motorola_denver`, `_milanf`, `_tundra` | default (`24.0`) | `diting` has the SM8475 set; others no `bm2n*` |
| 24 | `TheMuppets/proprietary_vendor_xiaomi_*` (`mayfly`,`marble`,`cupid`,`unicorn`,`zeus`), `_xiaomi_sm8250-common`, `_xiaomi_sm8450-common`, `_xiaomi_sm8550-common` | `20`..`24.0`, `main` | SM8475 set on mayfly/marble/diting/cupid; `sm8250`/`sm8450` trees have no `bm2n*`; `sm8550-common` empty; `TheMuppets/proprietary_vendor_xiaomi` itself is HTTP 451 (DMCA) |
| 25 | `TheMuppets/proprietary_vendor_oneplus_sm8250-common`, `_oneplus_sm8450-common`, `_oneplus_sm8550-common`, `_sm8650`, `_sm8750`, `_sony_sm8250-common`, `_sony_sm8550-common`, `_asus`, `_google*`, `_samsung*` | all listed branches | no `bm2n*` in tree paths (empty or file-less repos; `sm8650` repo 404; `sm8450` repo is empty, 409) |
| 26 | `xiaomi-sm8250-devs/proprietary_vendor_xiaomi_sm8250-common`, `crdroidandroid/proprietary_vendor_xiaomi_sm8250-common`, `PocoF3Releases/vendor_xiaomi_sm8250-common`, `ProjectElixir-Devices/vendor_xiaomi_sm8450-common`, `Evolution-X-Devices/vendor_xiaomi_sm8450-common` | default | no `bm2n*` |
| 27 | `bheatleyyy/vendor_oneplus_oneplus9rt` | `topaz` | 1,082,824 → `2d267761…` (the other revision, from a third-party org) |
| 28 | `Kscope-Devices/android_vendor_oneplus_sm8350-common` | `sunflowerleaf` | 1,082,824 → `2d267761…` |
| 29 | `nattolecats/proprietary_vendor_xiaomi_veux` | `lineage-21` | 1,082,824 → `2d267761…` (cross-vendor reuse of the same revision) |
| 30 | `TheMuppets/proprietary_vendor_xiaomi_cupid` | `22.2` | `bm2n00`-`11` only; `bm2n12`-`15` absent (contents API 404 on those paths) |
| 31 | `Paranoid-Xperia/vendor_sony_pdx225` | `main` | tree request failed: `read: connection reset by peer` (retried once, same). Not needed — match already established. |
| 32 | `DonkeyCoyote/proprietary_vendor_{motorola,sony,asus}`, `travarilo/proprietary_vendor_asus`, `Vendor-Blobs/android_vendor_tree_asus_AI2201`, `Evolution-X-Devices/vendor_oneplus_benz`, `Project-Benz/vendor_oneplus_benz` | default | no `bm2n*` paths |

Cross-check search: GitHub code search `"bm2n13.bin"` returns 909 hits, essentially all
`proprietary-files.txt` / `*-vendor.mk` *manifests*, not payloads — confirming the blob only lands in
the vendor trees above. `filename:bm2n13.bin` (path search) returns 0.

Failures, honestly:

- `gh api` contents fetches were rate-limited/flaky on large files. `TheMuppets/proprietary_vendor_sony_sm8350-common@lineage-20`
  `bm2n06.bin` returned **0 bytes** and `bm2n08.bin` **138,675 bytes** (truncated) before timeouts; both
  were discarded as unusable and are not in the matrix. Retry + `timeout` wrapper was needed
  throughout; every md5 in Table 2 comes from a fetch whose byte count matched the tree-reported size.
- Direct `raw.githubusercontent.com` fetches stalled from this network; `gh api -H "Accept: application/vnd.github.raw"`
  against the contents endpoint was reliable and is what the reproduce section uses.
- `TheMuppets/proprietary_vendor_xiaomi` → HTTP 451 (DMCA takedown, 2019). Xiaomi blobs had to be
  reached through split `proprietary_vendor_xiaomi_<device>` repos instead.
- `TheMuppets/proprietary_vendor_motorola_sm6375-common@lineage-22.1` tree → 404 (branch exists, tree
  object missing); branch skipped.

Outcome: **FOUND.** The DB-identical `bm2n13.bin` is not in the OnePlus tree that supplied the other
five; it is in the Motorola `sm7325-common` tree (`lineage-19.1` through `lineage-24.0`), and
independently in Sony SM8350/SM6375, Nothing Spacewar, Fairphone FP5, OnePlus `dre` and
`sm8350-common@22.0+`, plus two non-Muppets orgs.

## Reproduce

Prerequisites: `gh` authenticated (`gh auth status`), `python3`, `md5sum`, `curl`. Nothing is cloned;
all work goes through the GitHub tree/contents API. Work dir: `/tmp/astro_u/hunt/`.

```bash
mkdir -p /tmp/astro_u/hunt && cd /tmp/astro_u/hunt

# 1. DB target list and the identity we are hunting
grep -i "bm2n13" upstream-contribution/blob-database/coverage-matrix.csv \
  | awk -F, '{print $1"|"$2"|"$7"|"$8}' | sort | uniq -c

# 2. Enumerate branches of a candidate vendor repo
gh api "repos/TheMuppets/proprietary_vendor_motorola/branches?per_page=100" --jq '.[].name'

# 3. Tree search without cloning — size is the candidate filter
gh api "repos/TheMuppets/proprietary_vendor_motorola/git/trees/lineage-19.1?recursive=1" \
  --jq '.tree[]|select(.path|test("bm2n"))|"\(.path)|\(.size)"'

# 4. Fetch a candidate with retries (contents API; raw.githubusercontent was flaky here)
cat > get.sh <<'EOS'
#!/bin/bash
repo="$1"; br="$2"; p="$3"; out="$4"
for i in 1 2 3 4; do
  gh api -H "Accept: application/vnd.github.raw" "repos/$repo/contents/$p?ref=$br" > "$out" 2>/dev/null
  rc=$?; sz=$(stat -c%s "$out" 2>/dev/null || echo 0)
  if [ $rc -eq 0 ] && [ "$sz" -gt 500 ]; then break; fi
  sleep $((i*2))
done
echo "OK|$repo|$br|$p|$sz|$(md5sum "$out"|cut -d' ' -f1)"
EOS
chmod +x get.sh

# 5. The file that satisfies the DB identity
P=sm7325-common/proprietary/vendor/lib/rfsa/adsp
./get.sh TheMuppets/proprietary_vendor_motorola lineage-19.1 "$P/bm2n13.bin" bm2n13.bin
# OK|TheMuppets/proprietary_vendor_motorola|lineage-19.1|.../bm2n13.bin|1106944|bf635d9084b54633526f9ad8a84d299b

# 6. Verify against the DB row
md5sum bm2n13.bin            # bf635d9084b54633526f9ad8a84d299b
sha256sum bm2n13.bin         # 90f4d8b0fe1b20f99d15b34f61dab558bec5e37b0ce72f94c16fa5e3eb8b9dc9
stat -c%s bm2n13.bin         # 1106944

# 7. The near-miss revision, for contrast (same filename, different bytes)
./get.sh TheMuppets/proprietary_vendor_oneplus_sm8350-common lineage-21 \
  proprietary/vendor/lib/rfsa/adsp/bm2n13.bin bm2n13_sm8350.bin
# 1082824 | 2d267761f3291c9ca4a7850ab0ef1966

# 8. Branch-as-version-axis check on one repo
for b in lineage-20 lineage-21 lineage-22.0 lineage-22.1 lineage-24.0; do
  printf "%s " "$b"
  gh api "repos/TheMuppets/proprietary_vendor_oneplus_sm8350-common/git/trees/$b?recursive=1" \
    --jq '.tree[]|select(.path|test("bm2n13"))|.size'
done

# 9. Sweep the SM8475 generation (Pong / sm8475-common / mayfly / diting)
./get.sh TheMuppets/proprietary_vendor_nothing_Pong lineage-22.2 \
  proprietary/vendor/lib/rfsa/adsp/bm2n13.bin v_pong_bm2n13.bin     # 1339032 | ea1abfc1…

# 10. Cross-filename identity: Pong bm2n54.bin is the OnePlus bm2n13.bin revision
./get.sh TheMuppets/proprietary_vendor_nothing_Pong lineage-22.2 \
  proprietary/vendor/lib/rfsa/adsp/bm2n54.bin v_pong_bm2n54.bin     # 1082824 | 2d267761…
```

Fetch URLs (raw form, for citation):

```
https://github.com/TheMuppets/proprietary_vendor_motorola/raw/lineage-19.1/sm7325-common/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin
https://github.com/TheMuppets/proprietary_vendor_sony_sm8350-common/raw/lineage-20/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin
https://github.com/TheMuppets/proprietary_vendor_oneplus_sm8350-common/raw/lineage-21/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin   (the 1,082,824 variant)
https://github.com/TheMuppets/proprietary_vendor_nothing_Pong/raw/lineage-22.2/proprietary/vendor/lib/rfsa/adsp/bm2n13.bin      (the 1,339,032 variant)
```

Local payload store (not committed): `/tmp/astro_u/hunt/` — 56 files, ~70 MB, one file per fetched
`(repo, branch, path)`; the canonical recovered blob is `/tmp/astro_u/hunt/bm2n13.bin`.
