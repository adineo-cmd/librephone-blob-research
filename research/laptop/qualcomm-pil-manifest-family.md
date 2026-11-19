# Qualcomm PIL / PDR manifest family (`*.jsn`) — laptop half

The `*.jsn` files are the **most widely shared small blobs** in the laptop
half: one md5 covers **17 devices** for five different filenames. They are
tiny (403-905 B) text manifests, and until 2026-11-18 the programme
believed they were split-MDT image manifests. **They are not.**

- **What they are:** JSON **PDR service-registry manifests** — a lookup
  table mapping a QMI *service* (`provider/service`, e.g. `tms/servreg`,
  `avs/audio`, `wlan/fw`) to the *protection domain* that hosts it
  (`soc/domain/subdomain` + a QMI instance id).
- **Who reads them:** userspace **`pd-mapper`** (`linux-msm/pd-mapper`,
  BSD-3-Clause). It finds them by **directory adjacency** to a remoteproc's
  firmware path — any `.jsn` in `/vendor/firmware` is loaded, and the
  *contents* decide the domain. The filename is a human convenience.
- **Mainline does NOT read them.** `torvalds/linux` ships the identical
  table compiled in as C (`drivers/soc/qcom/qcom_pd_mapper.c`). `grep -c -i
  jsn` is **0** in both `mdt_loader.c` and `qcom_q6v5_pas.c`.

Full analysis, citations, byte-level proofs and the [OPEN] list:
**[`implementations/pil-manifests/jsn-manifest-analysis.md`](../../implementations/pil-manifests/jsn-manifest-analysis.md)**.
Parser, fixtures and tests:
**[`implementations/pil-manifests/`](../../implementations/pil-manifests/README.md)**.

## Family table (fleet md5s from `sharing-clusters.csv`)

Every row below was fetched and **md5-verified byte-exact** from public
repositories (7/7 of the 17-device set from a single Xiaomi `marble/`
firmware dir; the older generation from `hotdog`, `Lakka-LibreELEC`,
`armbian/firmware`). All of them are also published by **linux-firmware**
(`WHENCE`, 114 `*.jsn` entries) — already-redistributable firmware.

| md5 (short) | file | bytes | devices | declared domain (instance) |
|---|---|---|---|---|
| `5d262bb7…` | `adspr.jsn` | 513 | **17** | `msm/adsp/root_pd` (74) |
| `a43d66d0…` | `adspua.jsn` | 703 | **17** | `msm/adsp/audio_pd` (74) |
| `49003ffc…` | `cdspr.jsn` | 513 | **17** | `msm/cdsp/root_pd` (76) |
| `0d755b18…` | `battmgr.jsn` | 516 | **17** | `msm/adsp/charger_pd` (74) |
| `72b46949…` | `modemr.jsn` | 710 | 15 | `msm/modem/root_pd` (180) |
| `8167cdcc…` | `slpir.jsn` | 513 | 11 | `msm/slpi/root_pd` (90) |
| `de25e460…` | `slpius.jsn` | 515 | 11 | `msm/slpi/sensor_pd` (90) |
| `40d6edf1…` | `adspr.jsn` | 403 | 6 | `msm/adsp/root_pd` (74) |
| `cddb3285…` | `adsps.jsn` | 515 | 6 | `msm/adsp/sensor_pd` (74) |
| `f2bd80d5…` | `cdspr.jsn` | 403 | 6 | `msm/cdsp/root_pd` (76) |
| `d0bd5030…` | `adspua.jsn` | 555 | 6 | `msm/adsp/audio_pd` (74) |
| `bad87cce…` | `modemuw.jsn` | 713 | 4 | `msm/modem/wlan_pd` (180) |
| `0492fd46…` | `modemr.jsn` | 719 | 3 | `msm/modem/root_pd` (180) |
| `c7253d84…` | `adsps.jsn` | 405 | 3 | `msm/adsp/sensor_pd` (74) |
| `0039483e…` | `slpius.jsn` | 405 | 3 | `msm/slpi/sensor_pd` (90) |
| `2439d687…` | `slpir.jsn` | 403 | 3 | `msm/slpi/root_pd` (90) |
| `17b87853…` | `modemr.jsn` | 562 | 2 | `msm/modem/root_pd` (180) |
| `6acb8c83…` | `modemr.jsn` | 719 | 1 | `msm/modem/root_pd` (180) |
| `1a4a6904…` | `wlanpdr.jsn` | 405 | 2 | `msm/modem/root_pd` (180) |

The 17-device set: caihong, cupid, diting, erhai, fuxi, lemonade,
lemonadep, marble, martini, mayfly, mondrian, nuwa, socrates, thor,
unicorn, vermeer, zeus — Xiaomi + OnePlus on SM8250/SM8350/SM8450/SM8550.

## Three findings that change how the fleet is read

1. **The two-size `adspr.jsn` (403 vs 513) is cosmetic.** The delta is
   exactly one optional `dcomment` string field (110 B: `,` + newline + 12
   spaces + `"dcomment": "` + 82 + `"`). After dropping `dcomment` the two
   JSON documents are **equal**. The same holds for `adsps` (405/515),
   `adspua` (555/703), `cdspr` (403/513), `slpir` (403/513), `slpius`
   (405/515). Other off-by-one sizes are a trailing newline (514 vs 513) or
   CRLF (534 vs 513) from third-party redistributors.
2. **The `r`/`s`/`ua`/`uw` suffixes name the protection domain**, not a
   security variant. `<subsystem><optional u><role letter>`: `r`=root,
   `s`=sensor, `a`=audio, `o`=ois, `w`=wlan. Verified against
   `qcom_pd_mapper.c` across 71 files with **zero contradictions**. A `.jsn`
   has no signature, hash or security field at all.
3. **Mainline replaced the file with C.** `qcom_pd_mapper.c` hardcodes 19
   `(domain, instance, services)` tuples; the 12 distinct tuples found in 71
   real manifests are a strict **subset** of those 19. For sm8250, sc8280xp
   and qcm2290 the set of shipped `.jsn` files matches the kernel's per-SoC
   domain list **exactly**.

## Database corrections

`coverage-matrix.csv` mislabels this whole family (`jsn-manifest-analysis.md`
§7). `adspr/adsps/adspua` are typed `MODEM` (wrong — they describe the ADSP);
`battmgr.jsn` sits in family `modem` but declares `msm/adsp/charger_pd` (it
is **adsp**); `slpir/slpius` are family `other` but SLPI is a first-class
remoteproc (should be **slpi**); `wlanpdr.jsn` is family `wifi` but declares
`msm/modem/root_pd` (it is **modem**). Recommended `db_type` for the family:
**`PDR-MANIFEST`**, not `UNKNOWN`/`MODEM`.

## Why it matters (and how much)

One md5 covers 17 devices, so a single parse frees five-and-a-bit files
across the flagship set at once — and because the table is *in the GPL
kernel source*, a free implementation can generate a correct manifest for
any declared SoC without a vendor artifact.

Be honest about the size of the win: a `.jsn` launches nothing, patches
nothing, contains no code. It is a **directory service** for a userspace
daemon. And a mainline-based system does not need it at all, because the
kernel already has the table. The real blob problem on these devices stays
where it was — the DSP/modem images (`adsp.mdt` + `adsp.bNN`, ~18 MB for
`elish`'s `adsp.mbn`) that the manifest merely points at.

## Cross-links

- `blob-matrix/laptop/sharing-clusters.csv` — source of the md5/device rows
- `blob-matrix/laptop/fragmentation-half.md` — the manifest clusters filtered
  out of the top-15; this doc explains them
- `upstream-contribution/blob-database/recon.md` — noted `adspr.jsn` ×30
  "dominates the raw top-by-count"; now explained
- `blob-matrix/desktop/fleet-re/oneplus6-partition-map.md` — spotted that
  `image_adspr.jsn` equals the fleet blob; this doc identifies what it is
- `implementations/pil-manifests/` — the parser, fixtures, tests and analysis
