# `*.jsn` — the Qualcomm PDR *service registry* manifest family (2026-11-18/19)

The lab's **second content-level RE**, and the first on the Qualcomm
remoteproc control plane. The target was the `*.jsn` family: tiny text
files (403-905 B) that dominate the laptop half's sharing clusters —
`adspr.jsn` alone is **17 devices on one md5**.

**Headline correction to the mission premise.** These are **not** split-MDT
image manifests. They do not name `.mdt`/`.bNN` files, they do not list
segments or hashes, and they are **not read by the PIL / `qcom_q6v5_pas` /
`qcom_mdt_loader` path at all**. They are **JSON PDR service-registry
(`sr_*`) manifests** consumed by the *PD-mapper*: a lookup table that maps a
QMI service name to the protection domain that hosts it. §4 gives the
citation, including the much more interesting finding that **mainline
Linux carries the same table compiled in as C and never opens the file**.

Clean-room statement: every claim below comes from (a) GPL-2.0-only kernel
source or the BSD-3-Clause `pd-mapper` userspace source, both fetched
2026-11-18, and (b) the lab's own byte-level measurement of payloads that
are publicly redistributable (linux-firmware publishes this whole family —
114 `WHENCE` entries). No decompiled code, no vendor header, no proprietary
documentation. All full verbatim payload copies live in
`/tmp/astro_u/jsn/`; the repo holds excerpts and derived facts only.

---

## 1. Provenance and md5 verification

The DB md5s come from `blob-matrix/laptop/sharing-clusters.csv` and
`upstream-contribution/blob-database/coverage-matrix.csv`. Fetches
2026-11-18 and 2026-11-19.

### 1.1 The 17-device set — all 7 fleet files MATCH byte-exact

Source: `iLtanaka/firmware-xiaomi-marble` @ `HEAD`, dir `marble/` — a
Xiaomi **marble** (POCO F5, SM7475) firmware tree, i.e. a device inside the
17-device set. This single directory carries the entire fleet set.

| file | bytes | DB md5 | fetched md5 | status |
|---|---|---|---|---|
| `adspr.jsn` | 513 | `5d262bb7661402a8d7ca9724bbb45d46` | same | **MATCH** |
| `adspua.jsn` | 703 | `a43d66d0549e33cf421e25be06260ce0` | same | **MATCH** |
| `battmgr.jsn` | 516 | `0d755b18c24337ebca8313b85f8e8a6c` | same | **MATCH** |
| `cdspr.jsn` | 513 | `49003ffcd10ec16dee11caad22b11b42` | same | **MATCH** |
| `modemr.jsn` | 710 | `72b46949d078a4f226394931a4345e61` | same | **MATCH** |
| `slpir.jsn` | 513 | `8167cdcc892464ba0fed63cd439314a2` | same | **MATCH** |
| `slpius.jsn` | 515 | `de25e460ce0debb53db0bb15a122ac6f` | same | **MATCH** |

### 1.2 The older generation (403/405/555/713/719 B) — all MATCH

Source: `TheMuppets`-mirrored trees are partly GitHub-blocked (see §1.4);
these came from `Sr-0w/hotdog-linux-bringup` (OnePlus 7T, `aports/device/
testing/firmware-oneplus-hotdog/`) and `libretro/Lakka-LibreELEC`.

| file | bytes | DB md5 | status |
|---|---|---|---|
| `adspr.jsn` | 403 | `40d6edf129dec063ca3fe6cb6837488f` | **MATCH** |
| `cdspr.jsn` | 403 | `f2bd80d5f0b19b5b0d36d28383948149` | **MATCH** |
| `slpir.jsn` | 403 | `2439d6872b39e9c1282c572b266665f0` | **MATCH** |
| `slpius.jsn` | 405 | `0039483ebd20685728df72c12d13fee4` | **MATCH** |
| `adspua.jsn` | 555 | `d0bd5030a03f631c9af5060a5645d02e` | **MATCH** |
| `adsps.jsn` | 405 | `c7253d84bff46e4cf5cb0585e9a851c5` | **MATCH** |
| `modemuw.jsn` | 713 | `bad87ccee828ee70d0281db170985738` | **MATCH** |
| `modemr.jsn` | 719 | `0492fd466fcf5bf62a3d89ceba83197f` | **MATCH** |

### 1.3 The best public source — linux-firmware publishes this family

`gitlab.com/kernel-firmware/linux-firmware` `WHENCE` carries **114 `RawFile:`
/ `Link:` entries for `*.jsn`** (fetched 2026-11-18). Spot-fetched and
md5-verified byte-exact:

| path | bytes | md5 | matches |
|---|---|---|---|
| `qcom/sm8250/adspr.jsn` | 403 | `40d6edf1…` | fleet 403 variant |
| `qcom/sm8250/adspua.jsn` | 555 | `d0bd5030…` | fleet 555 variant |
| `qcom/sm8250/cdspr.jsn` | 403 | `f2bd80d5…` | fleet 403 variant |
| `qcom/qcm2290/adspr.jsn` | 403 | `40d6edf1…` | fleet 403 variant |
| `qcom/qcm2290/adsps.jsn` | 405 | `c7253d84…` | fleet 405 variant |
| `qcom/sm8250/Thundercomm/RB5/slpir.jsn` | 403 | `2439d687…` | fleet 403 variant |

This is significant for the programme: **the vendor artifacts the DB
catalogued are already public, redistributable firmware**, and a free
implementation does not have to reverse anything to obtain them. `WHENCE`
lists them under `Driver: qcom_q6v5_pas - Qualcomm remoteproc firmware`
with no version string and no licence line beyond the section header.

### 1.4 Route log (RULE 0 — every probe recorded)

1. `TheMuppets/proprietary_vendor_xiaomi` → **HTTP 451, `"reason":
   "dmca"`** (`github.com/github/dmca/blob/master/2019/08/2019-08-09-SenseTime-5.md`).
   The whole org repo is GitHub-blocked; `raw.githubusercontent.com` 404s.
   Per-device spin-offs (`…_marble`, `…_fuxi`, `…_cupid`,
   `…_sm8550-common`) exist and are reachable, but their recursive trees
   contain **zero `.jsn`** — the manifests are not in the vendor tree at
   all on those branches.
2. `TheMuppets/proprietary_vendor_oneplus` @ `lineage-19.1` → repo reachable,
   13,122 tree entries, **zero `.jsn`**. Same for `lineage-24.0` guacamole
   (TLS timeouts on repeated probes — logged, retried, abandoned).
3. Authenticated GitHub **code search** (`filename:adspr.jsn`, 271 hits;
   `filename:adspua.jsn`, 279; `filename:battmgr.jsn`, 194;
   `filename:modemuw.jsn`, 181; `filename:slpius.jsn`, 251;
   `filename:modemr.jsn`, 100+ sampled) redirected the search to the
   retro-handheld / ARM-distro firmware mirrors — `armbian/firmware`,
   `batocera-linux`, `armada-os/armada`, `libretro/Lakka-LibreELEC`,
   `radxa/linux-firmware`, `aarch64-laptops/firmware-qcom-woa` — which is
   where the byte-exact copies actually live.
4. `/tmp/astro_u/jsn/` scratch holds 71 verified manifests across 13
   SoC/device directories. No Git-LFS pointers were encountered in the
   files that mattered (the `WOA-Project` trees returned
   `null` sizes in the tree API but were not needed).
5. Honest negative: could not verify the `modemr.jsn` **562 B** and **719 B
   (laurel_sprout)** sizes against a device-local tree; 562 B was matched
   from `armbian/firmware` `qcom/qcm2290/modemr.jsn` (DB md5
   `a7f71370d2f306a50e2a3476982ad30c` for the SM4250 Moto rows — the DB
   lists **two different md5s at 562 B**, so this size is not
   content-stable; §5.3).

---

## 2. The established grammar

**Verdict: plain JSON** (RFC 8259), UTF-8, **4-space indent**, **LF**, **no
trailing newline**, **no BOM**, **no tabs**. Three top-level keys, always in
the same order. This is confirmed three ways: it parses with
`json.loads`; `pd-mapper`'s hand-written recursive-descent `json.c` parses
it (so it is JSON in the strict sense, not merely JSON-*like*); and **60 of
the 61 LF-terminated files re-render byte-identically** from
`json.dumps(obj, indent=4)` with no trailing newline. The single exception
is `wlanpdr.jsn`, which uses an 11-space indent for one nesting level and
carries a trailing newline (§9 [OPEN] 6-7).

```
{
    "sr_version": {
        "major": 1,
        "minor": 1,
        "patch": 1
    },
    "sr_domain": {
        "soc": "msm",
        "domain": "adsp",
        "subdomain": "root_pd",
        "qmi_instance_id": 74
    },
    "sr_service": [
        {
            "provider": "tms",
            "service": "servreg",
            "service_data_valid": 0,
            "service_data": 0
        },
        …
    ]
}
```

`sr_service` is the only array; everything else is a fixed-shape object.
Every field is a string except `sr_version.*`, `sr_domain.qmi_instance_id`,
`sr_service[].service_data_valid` and `sr_service[].service_data`, which are
non-negative integers.

### 2.1 Byte-level framing facts (measured, 71 files)

| property | value | evidence |
|---|---|---|
| encoding | UTF-8, ASCII-only in every sample | 0 non-ASCII bytes in 71 files |
| BOM | none | `EF BB BF` absent in all 71 |
| line ending | LF | 1 file family (`sc8280xp` **WOA redistributions**) uses CRLF — see §5.4 |
| indent | 4 spaces | universal |
| tabs | none | universal |
| **trailing newline** | **absent** (default) | present in `wlanpdr.jsn` and the `WOA`/`aarch64-laptops` copies; accounts for the +1 B sizes in §5.4 |
| terminators | none; the file ends with `}` | universal |

The "trailing newline" observation explains a whole class of off-by-one
sizes in other redistributions (514 vs 513, 406 vs 405): verified by
byte-diff — `woa/adspr.jsn` (514 B) is `marble/adspr.jsn` (513 B) plus
exactly one `\n`.

### 2.2 The full key table

Every key observed across the 71 measured manifests, with the public
source that pins its meaning. "Consumer" = who reads it.

| key | type | observed values | meaning | backing |
|---|---|---|---|---|
| `sr_version.major` | int | `1` (71/71) | SERVREG QMI major version | `qcom_pd_mapper.c`: `#define SERVREG_QMI_VERSION 0x101` — major is the high byte (`1`) |
| `sr_version.minor` | int | `1` (71/71) | SERVREG QMI minor version | same constant; low byte `0x01` = `1` |
| `sr_version.patch` | int | `1` (71/71) | patch level | **not represented** in `SERVREG_QMI_VERSION`; [OPEN] what consumes it — `pd-mapper` ignores `sr_version` entirely |
| `sr_domain.soc` | string | `"msm"` (71/71) | SoC-family prefix of the domain path | `qcom_pd_mapper.c` domain strings are all `"msm/…"`; `pd-mapper.c` concatenates `soc/domain/subdomain` |
| `sr_domain.domain` | string | `adsp`(28), `modem`(8), `slpi`(8), `cdsp`(9) | remoteproc subsystem | `qcom_pd_mapper.c` `msm/<domain>/<subdomain>` table; `qcom_q6v5_pas.c` `firmware_name` fields are `adsp.mdt`/`cdsp.mdt`/`modem.mdt`/`slpi.mdt` |
| `sr_domain.subdomain` | string | `root_pd`(28), `audio_pd`(10), `sensor_pd`(7), `wlan_pd`(4), `charger_pd`(3), `ois_pd`(1) | protection domain **within** that subsystem | `qcom_pd_mapper.c` hardcodes exactly these six subdomains |
| `sr_domain.qmi_instance_id` | int | adsp/slpi-family `74`, cdsp `76`, slpi `90`, modem `180` | QMI instance id of the servreg service in that PD | `qcom_pd_mapper.c` `.instance_id` per `qcom_pdm_domain_data`; delivered as `instance` in the `get_domain_list` response |
| `sr_service[].provider` | string | `tms`(54), `avs`(10), `gps`(3), `kernel`(4), `wlan`(4) | provider half of the service name | `pd-mapper.c` `sprintf(map->service, "%s/%s", provider, service)` |
| `sr_service[].service` | string | `servreg`(53), `audio`(10), `gps_service`(3), `pdr_enabled`(1), `elf_loader`(4), `fw`(4) | service half of the name | same |
| `sr_service[].service_data_valid` | int | `0` (75/75) | flag making `service_data` meaningful | `pdr_interface.c` `struct pdr_service` has `u8 service_data_valid`; `qcom_pd_mapper.c` does **not** read it |
| `sr_service[].service_data` | int | `0` (75/75) | payload (the comment says: ACK timeout in seconds) | same struct field `u32 service_data` |
| `sr_service[].dcomment` | string | 2 distinct texts, 82 B and 10 B | **a comment for humans** — the QMI wire protocol has no comment field | `pd-mapper.c` never reads it; the text itself says "data can be used to configure ACK timeout. Make data_valid 1 as well. Unit is second", i.e. it documents `service_data` |

`dcomment` is **inert**: `pd-mapper`'s `pd_load_map()` reads only
`provider` and `service` from each array element, and `qcom_pd_mapper.c`
has no concept of it at all. Its only measurable effect is file size —
which is exactly what creates the §5 two-generation split.

---

## 3. The suffix taxonomy — `r` / `s` / `ua` / `uw`

**Verdict: the suffix encodes the *protection domain* (`subdomain`), and it
does so with 100 % consistency across every file measured.** Not
secure/non-secure, not signed/unsigned, not a generation. This is a
*derivable* naming scheme, verified by cross-checking 71 files against
`qcom_pd_mapper.c` with **zero contradictions**.

### 3.1 The mapping

| stem pattern | `sr_domain.domain` | `sr_domain.subdomain` | instance | suffix |
|---|---|---|---|---|
| `adspr` | adsp | `root_pd` | 74 | `r` |
| `adsps` | adsp | `sensor_pd` | 74 | `s` |
| `adspua` | adsp | `audio_pd` | 74 | `ua` |
| `adspuo` | adsp | `ois_pd` | 74 | `uo` |
| `cdspr` | cdsp | `root_pd` | 76 | `r` |
| `slpir` | slpi | `root_pd` | 90 | `r` |
| `slpius` | slpi | `sensor_pd` | 90 | `us` |
| `modemr` | modem | `root_pd` | 180 | `r` |
| `modemuw` | modem | `wlan_pd` | 180 | `uw` |
| `battmgr` | adsp | `charger_pd` | 74 | *(role-named)* |
| `wlanpdr` | modem | `root_pd` | 180 | *(role-named)* |

Read it as `<subsystem><optional u><role-letter>` where the role letter is
`r`=root, `s`=sensor, `a`=audio, `o`=ois, `w`=wlan, and the `u` infix marks
"not the root PD". `modemuw` = modem + **u** + **w**lan. `adspua` = adsp +
**u** + **a**udio. `slpius` = slpi + **u** + **s**ensor.

### 3.2 The one inconsistency, stated honestly

`adsps.jsn` and `slpius.jsn` declare the **same** `msm/*/sensor_pd` concept
with **different spellings** — bare `s` for adsp, `us` for slpi. Both forms
appear in shipped trees, both are accepted by the kernel (`adsp_sensor_pd`
and `slpi_sensor_pd` are separate structs but carry no service distinction
beyond the domain), and the files' contents differ only in the
domain/instance fields. So the vendor's own generator is inconsistent about
the `u` infix. **Why sensor is spelled two ways is [OPEN]** — nothing in the
kernel or `pd-mapper` explains it.

### 3.3 What the suffixes do NOT mean (explicitly ruled out)

- **Not secure vs non-secure.** The mission brief suggested this. Refuted:
  a `.jsn` contains no signature, no hash, no security flag, and no field
  that could carry one; the file is a plain lookup table and every one of
  the 71 samples parses as plain JSON with the same three keys. There is no
  `secure`/`auth`/`signed` key anywhere in the family.
- **Not firmware variant selection.** `qcom_q6v5_pas.c` picks its firmware
  by `firmware_name` in a per-SoC `desc` struct (`"adsp.mdt"`,
  `"cdsp.mdt"`, `"modem.mdt"`, `"slpi.mdt"`, plus `dtb_firmware_name`) — it
  never looks at a `.jsn`.
- **Not a generation counter.** The same stem ships at two sizes with
  identical semantics; §5 shows the delta is a comment field.

---

## 4. Who actually consumes these — the RULE-0 finding

### 4.1 Mainline does **not** open the file

Fetched 2026-11-18 from `torvalds/linux` master via the contents API:

- `drivers/soc/qcom/mdt_loader.c` (508 lines) — `grep -c -i jsn` → **0**.
- `drivers/remoteproc/qcom_q6v5_pas.c` (2,093 lines) — `grep -c -i jsn`
  → **0**. Its firmware selection is entirely `desc->firmware_name`.
- Code search `jsn repo:torvalds/linux` → **2 hits, both spurious**
  (`CREDITS`, `drivers/gpu/drm/msm/Makefile`).

So the mission's hypothesis — "the kernel's mdt_loader supports a JSON-ish
image manifest that names the split mdt/bXX segments" — is **false for
`*.jsn`**. `mdt_loader.c` does handle split firmware, but it derives the
segment name arithmetically from the `.mdt` filename, not from a manifest:

```c
/* drivers/soc/qcom/mdt_loader.c, mdt_load_split_segment() */
	sprintf(seg_name + strlen(fw_name) - 3, "b%02d", segment);
	ret = request_firmware_into_buf(&seg_fw, seg_name, dev,
					ptr, phdr->p_filesz);
```

That is `adsp.mdt` → `adsp.b00`, `adsp.b01`, … — a 3-character overwrite of
the extension, the classic split-MDT convention. **No manifest file is
involved anywhere in the PIL path.** This is an honest negative and it
matters: anyone expecting `*.jsn` to describe MDT segments is looking at the
wrong mechanism.

### 4.2 The real consumer #1: userspace `pd-mapper`

`github.com/linux-msm/pd-mapper`, BSD-3-Clause, cloned 2026-11-18
(`5ecd2fe926aca7abfe40724177f63b942cff3947`, 2025-12-30). This is the
component that actually parses the bytes. Its `pd-mapper.c`:

```c
static int pd_load_map(const char *file)
{
	root = json_parse_file(file);
	sr_domain = json_get_child(root, "sr_domain");
	soc       = json_get_string(sr_domain, "soc");
	domain    = json_get_string(sr_domain, "domain");
	subdomain = json_get_string(sr_domain, "subdomain");
	ret = json_get_number(sr_domain, "qmi_instance_id", &number);
	…
	sr_service = json_get_child(root, "sr_service");
	count = json_count_children(sr_service);
	for (it = sr_service->u.value; it; it = it->next) {
		provider = json_get_string(it, "provider");
		service  = json_get_string(it, "service");
		map->service = malloc(strlen(provider) + strlen(service) + 2);
		sprintf((char *)map->service, "%s/%s", provider, service);
		map->domain  = malloc(strlen(soc) + strlen(domain) + strlen(subdomain) + 3);
		sprintf((char *)map->domain, "%s/%s/%s", soc, domain, subdomain);
		map->instance = number;
	}
}
```

and it **discovers** the files by walking `/sys/class/remoteproc/*/firmware`,
taking the `dirname()` of that path, and listing every entry whose name ends
in `.jsn` or `.jsn.xz`:

```c
static char *known_extensions[] = { ".jsn.xz", ".jsn", NULL, };
…
	firmware_value_copy = strdup(firmware_value);
	firmware_path = dirname(firmware_value_copy);
	fw_dir = opendir_firmware(firmware_path, path, sizeof(path));
	…
	if (len > extens_len &&
	    !strcmp(&fw_de->d_name[len - extens_len], known_extensions[extens_index]))
		found = true;
```

**This is the mechanism that explains every naming convention in §3**: a
`.jsn` is not addressed by name — it is picked up because it sits in the
same directory as a remoteproc's firmware. Any `.jsn` in `/vendor/firmware`
is loaded, and its *contents* decide which domain it registers. The
filename is a human convenience; the contract is `sr_domain`.

Two consumer-side limits worth recording (the parser enforces them):

- `json_parse_string()` copies into `char buf[128]` and stops at
  `b - buf < sizeof(buf) - 1` → **any string value over 127 bytes is
  silently truncated**. Every measured value is far below this.
- `json_parse_number()` accepts only `isdigit()` → **non-negative integers
  only**, no sign, no decimal point.

### 4.3 The real consumer #2: mainline's `qcom_pd_mapper.c` — compiled-in, no file

`drivers/soc/qcom/qcom_pd_mapper.c` (793 lines, GPL-2.0-only, added
2023 by Linaro; last touched 2026-08) implements the **same database as C
data**:

```c
#define SERVREG_QMI_VERSION 0x101
#define TMS_SERVREG_SERVICE "tms/servreg"

static const struct qcom_pdm_domain_data adsp_audio_pd = {
	.domain = "msm/adsp/audio_pd",
	.instance_id = 74,
	.services = { "avs/audio", NULL },
};
…
static const struct qcom_pdm_domain_data *sm8550_domains[] = {
	&adsp_audio_pd, &adsp_root_pd, &adsp_charger_pd,
	&adsp_sensor_pd, &cdsp_root_pd, &mpss_root_pd_gps, NULL,
};

static const struct of_device_id qcom_pdm_domains[] = {
	…
	{ .compatible = "qcom,sm8550", .data = sm8550_domains, },
```

and `qcom_pdm_add_domain()` adds `tms/servreg` **implicitly** to every
domain before the extra services:

```c
	ret = qcom_pdm_add_service_domain(data, TMS_SERVREG_SERVICE,
					  domain->domain, domain->instance_id);
	for (i = 0; domain->services[i]; i++)
		ret = qcom_pdm_add_service_domain(data, domain->services[i],
						  domain->domain, domain->instance_id);
```

**This is the clean-room gold**: the kernel source states, in C, exactly
what the `.jsn` files state in JSON. The two are interchangeable
descriptions of one table, and the kernel chose to ship the table in-tree
rather than parse vendor text.

### 4.4 Consistency proof: the two tables agree exactly

Extracting all 19 `qcom_pdm_domain_data` structs from `qcom_pd_mapper.c` and
all `(domain, instance, extra-services)` triples from the 71 measured
manifests:

- **12 distinct triples appear in the manifests.**
- **All 12 are present in the kernel's 19.** Zero contradictions.
- The 7 kernel-only triples (`msm/adsp/audio_pd` inst 4, `msm/adsp/root_pd`
  inst 4 → MSM8996; `msm/cdsp1/root_pd` 125; `msm/gpdsp{,1}/root_pd`
  192/241; `msm/modem/root_pd` 100 → MSM8996; `msm/adsp/root_pd` +
  `tms/pdr_enabled`) are older or newer SoCs whose `.jsn` I did not sample.

### 4.5 Consistency proof #2: the per-directory file set IS the per-SoC kernel table

The strongest validation of the whole reading. For each SoC directory, the
set of `.jsn` files shipped should equal the set of domains
`qcom_pd_mapper.c` lists for that `compatible`:

| SoC dir | `.jsn` shipped | kernel domains | verdict |
|---|---|---|---|
| `sm8250/xiaomi/elish` | adspr, adspua, cdspr, slpir, slpius (5) | 5 | **EXACT MATCH** |
| `sc8280xp/microsoft/blackrock` | adspr, adspua, battmgr, cdspr (4) | 4 | **EXACT MATCH** |
| `qcm2290` | adspr, adsps, adspua, modemr, modemuw (5) | 5 | **EXACT MATCH** |
| `sm8550/ayn/thor` | adspr, adsps, adspua, battmgr (4) | 6 | subset — dir listing is a partial firmware drop; `modemr`/`cdspr` absent |
| `sm8750/ayn/odin3` | adspr, adsps, adspua, adspuo, battmgr, cdspr (6) | 6 | `adspuo` (`ois_pd`) shipped but not in the `sm8550_domains` table; `modemr` absent |

Three exact matches, and the two non-matches are explained by the directory
not being a complete `/vendor/firmware` (these are third-party distro
firmware drops, not device images). The `adspuo` row is a genuine upstream
gap: **`ois_pd` ships on SM8750 hardware but mainline's sm8550 table has no
`msm/adsp/ois_pd` entry** — so a mainline kernel on that hardware would not
answer a lookup for the OIS domain. Worth filing upstream.

---

## 5. The two-generation `adspr.jsn` split (403 vs 513)

**Verdict: pure `dcomment` addition. 100 % of the delta is one optional
human-readable comment; the semantics are identical.** Not a firmware
generation, not a security change, not a schema change.

### 5.1 Byte-level proof

```
$ diff hotdog/adspr.jsn(403)  marble/adspr.jsn(513)
18c18,19
<             "service_data": 0
---
>             "service_data": 0,
>             "dcomment": "data can be used to configure ACK timeout.Make data_valid 1 as well.Unit is second"
```

Exactly one added line. Load both as JSON, drop `dcomment`, compare: they
are **equal**. The same holds for every other two-size pair:

| stem | small | large | delta | equals-mod-dcomment |
|---|---|---|---|---|
| `adspr` | 403 | 513 | +110 | **yes** |
| `adsps` | 405 | 515 | +110 | **yes** |
| `adspua` | 555 | 703 | +148 | **yes** (two comments) |
| `cdspr` | 403 | 513 | +110 | **yes** |
| `slpir` | 403 | 513 | +110 | **yes** |
| `slpius` | 405 | 515 | +110 | **yes** |
| `modemr` | 710 | 719 | +9 | no — different service list (§5.3) |

The arithmetic is exact and reproducible:

```
one added "dcomment" with an 82-byte text costs
    ','  + '\n' + 12 spaces + '"dcomment": "' + 82 + '"'
  = 1 + 1 + 12 + 13 + 82 + 1 = 110 bytes            # 403 + 110 = 513  ✓
a 10-byte "No comment" costs 1+1+12+13+10+1 = 38     # 555 + 110 + 38 = 703 ✓
```

### 5.2 Which generation is which

The **larger** file is the later/annotated one: it carries the comment that
documents `service_data` as an ACK timeout in seconds ("Make data_valid 1 as
well. Unit is second"). The smaller file is the same table without the
annotation. Both are accepted identically by `pd-mapper` (it never reads
`dcomment`) and both describe the same domain, so **the split is cosmetic**.

This resolves the mission's observation (i) completely: the two-size
`adspr.jsn` is not "a two-generation family like other fleets" in any
functional sense. It is **one manifest with an optional comment field**.

### 5.3 The `modemr` sizes are NOT a generation split

`modemr.jsn` ships at **405, 406, 425, 562, 710, 719 and 905 bytes** across
the DB (6 distinct md5s at 710/719/905/562×2/…). These are **different
service lists**, not formatting:

| size | services | note |
|---|---|---|
| 405 | `tms/servreg` | bare, no comment, LF |
| 406 | `tms/servreg` | 405 + one trailing newline |
| 425 | `tms/servreg` | 405 with **CRLF** (20 × +1 B) — verified identical after `\r\n`→`\n` |
| 562 | `tms/servreg`, `gps/gps_service` | 2 services |
| 710 | `tms/servreg`, `gps/gps_service` | 2 services + `dcomment`s |
| 719 | `tms/pdr_enabled`, `tms/servreg`, `gps/gps_service` | **3 services** — the `pdr_enabled` variant |
| 905 | [OPEN] — not fetched | DB md5 `e420bddba517a143811164b32ef5c841`, 3 Motorola rows |

So only three of those sizes are genuine *content* variants (562 / 710 / 719);
405↔406 and 405↔425 are the trailing-newline and CRLF artefacts of §5.4. The
same artefact explains `slpir.jsn` at **423 B** (403 CRLF) and `slpius.jsn`
at **425 B** (405 CRLF) — both verified byte-identical to the LF originals
after `\r\n`→`\n`. Note the DB assigns **two different md5s to 562 B**
(`17b878530e8306c3777ead5ec2b84aba` and `a7f71370d2f306a50e2a3476982ad30c`),
proving that size is not a key for this stem.

### 5.4 The trailing-newline class (off-by-one sizes)

| size | variant |
|---|---|
| 405 | `modemr` bare, no trailing newline |
| 406 | the same bytes **plus `\n`** — verified byte-identical after `rstrip` |
| 513 / 514 | same relation (`aarch64-laptops/jsн/adspr.jsn` 514 = `marble/adspr.jsn` 513 + `\n`) |
| 534 | the 513 B file with **CRLF** line endings (21 × +1 B) — verified: `replace(b'\r\n', b'\n')` reproduces the 513 B file exactly |

None of these is a semantic variant. They are redistribution artefacts
(Windows-authored WOA trees wrote CRLF; some packagers append a newline).

---

## 6. Cross-check: do the files make sense in place?

Task 5 asked whether referenced filenames exist alongside. **This family
references no filenames** — that is the point of §4.3. The real
consistency test is the domain set, done in §4.5 (3 exact matches, 2
explained).

A second, independent spot-check: `WHENCE` files these under
`Driver: qcom_q6v5_pas`, alongside `adsp.mbn`/`modem.mbn`/`cdsp.mbn`/etc.
for the same SoC. The manifests and the MDT images are co-located because
`pd-mapper` **requires** it (§4.2) — the `.jsn` is found by listing the
directory the remoteproc firmware lives in. Verified in the tree:

```
qcom/sm8250/xiaomi/elish/   adsp.mbn  adspr.jsn  adspua.jsn  cdsp.mbn  cdspr.jsn  slpi.mbn  slpir.jsn  slpius.jsn
```

Every subsystem with an `.mbn` has the matching manifest(s), in one flat
directory. This is the structural validation the task asked for, and it
confirms both the reading of the format and the discovery mechanism.

---

## 7. Correcting the upstream database's type labels

The DB (`coverage-matrix.csv`) types these rows as follows, and **all of
these labels are wrong in a specific, correctable way**:

| filename | DB `blob_family` | DB `db_type` | evidence says |
|---|---|---|---|
| `adspr.jsn`, `adsps.jsn`, `adspua.jsn` | `adsp` | **`MODEM`** | family `adsp` is right; **`MODEM` is wrong** — these describe the ADSP's protection domains, nothing to do with the modem |
| `cdspr.jsn` | `cdsp` | `UNKNOWN` | family right; type should be **PDR-MANIFEST** (not UNKNOWN — it is fully decoded) |
| `modemr.jsn`, `modemuw.jsn`, `modemuo.jsn` | `modem` | `UNKNOWN` | family right; type **PDR-MANIFEST** |
| `battmgr.jsn` | **`modem`** | `UNKNOWN` | **family is wrong** — `battmgr.jsn` declares `msm/adsp/charger_pd`, instance 74. It is an **ADSP** manifest, not modem |
| `slpir.jsn`, `slpius.jsn` | **`other`** | `UNKNOWN` | **family is wrong** — `slpi` is a first-class remoteproc (`slpi.mdt` in `qcom_q6v5_pas.c`). Should be **`slpi`**, not `other` |
| `wlanpdr.jsn` | `wifi` | `UNKNOWN` | **family is wrong** — it declares `msm/modem/root_pd` with service `tms/pdr_enabled`. It is a **modem** PD manifest, not wifi firmware |

Recommended `db_type` for the whole family: **`PDR-MANIFEST`** (or
`MANIFEST-PDR`) — the rows are neither `MODEM` nor `UNKNOWN`; they are fully
specified text manifests. Recommended families: `adsp` / `cdsp` / `slpi` /
`modem`, derived from `sr_domain.domain` (which the parser now computes).

The root cause of the mislabels is visible in the DB: it classifies by
**filename stem and path**, so `battmgr` (no recognisable prefix, but in
`modem/image/`) got `modem`, and `slpi*` (unrecognised prefix) fell into
`other`. The manifest's own `sr_domain` is the authoritative field and the
DB never parsed it.

---

## 8. What this means for a free reimplementation

**Fully specified and writable today, with zero proprietary bytes:**

- The exchange format is JSON with three fixed keys — trivially emittable.
- The *contents* of the table are already stated in GPL kernel C
  (§4.3). A free implementation can generate a complete, correct `.jsn`
  for every declared SoC **from `qcom_pd_mapper.c` alone**, without ever
  looking at a vendor file.
- `pd-mapper` (BSD-3-Clause) is a complete, licensable reference
  implementation of the consumer side.
- Validation is mechanical: `jsn_probe.py` re-derives the domain from the
  filename and cross-checks it against the QMI instance the kernel
  hardcodes (§4.4).

**The real lever:** mainline already does not need these files. The kernel
carries the table in-tree, so a mainline-based free system is
**unaffected** by this family entirely. The family matters only for
systems that run the vendor's userspace `pd-mapper` — i.e. Android-derived
and postmarketOS-style stacks using `linux-msm/pd-mapper`.

**Honest scope limit:** `.jsn` is a *directory service*, not firmware. It
launches nothing, patches nothing, and contains no code. Freeing it frees
the control-plane plumbing of an Android userspace on these devices — a
real but small piece. The DSP/modem images themselves (`adsp.mdt` +
`adsp.bNN`, 18 MB for `elish`'s `adsp.mbn`) remain the actual blob problem.

---

## 9. [OPEN] items

1. **[OPEN]** What consumes `sr_version.patch`? It is `1` in all 71 files.
   `pd-mapper` ignores `sr_version`; `qcom_pd_mapper.c` encodes only
   major/minor in `SERVREG_QMI_VERSION 0x101`. No public consumer reads it.
2. **[OPEN]** Why does the vendor generator spell `sensor_pd` as bare `s`
   for adsp (`adsps.jsn`) but `us` for slpi (`slpius.jsn`)? Both parse; the
   kernel has separate `adsp_sensor_pd`/`slpi_sensor_pd` structs. Unexplained
   by any public source.
3. **[OPEN]** `modemr.jsn` at 905 B (DB md5 `e420bddba517a143811164b32ef5c841`,
   3 Motorola rows: Moto G200, Edge 40 Pro, Edge 30 Fusion). Not fetched —
   no public tree found in the probes. Service list unknown.
4. **[OPEN]** `modemuo.jsn` (704 B, OnePlus 13 `dodge`). Not fetched; name
   suggests modem + `u` + `o`, but `o` is `ois_pd` on adsp. Whether
   `msm/modem/ois_pd` exists as a domain is unconfirmed — `qcom_pd_mapper.c`
   has no such entry.
5. **[OPEN]** Mainline's `sm8550_domains[]` omits `msm/adsp/ois_pd`, yet
   `adspuo.jsn` ships on SM8750 hardware (odin3/konkr). Whether this is an
   upstream bug (missing domain entry) or intentional is unresolved.
   **Flagged for upstream.**
6. **[OPEN]** `wlanpdr.jsn`'s role. It declares `msm/modem/root_pd` +
   `tms/pdr_enabled` — the same tuple as `adsp_root_pd_pdr` in the kernel but
   for the modem domain. Why a separate file (rather than a service entry in
   `modemr.jsn`) is unclear; **no public tree in these probes shipped both
   `wlanpdr.jsn` and `modemr.jsn` together**, so co-residence is unverified.
7. **[OPEN]** Whether the trailing newline / CRLF variants ever shipped from
   a *device* (rather than a redistributor). All anomalies trace to
   `aarch64-laptops`, `WOA-Project`, and `sc8280xp` third-party packs.
8. **[OPEN]** `battmgr.jsn` semantics beyond the domain mapping: the name
   suggests a battery/charger manager service, but its only service entry is
   the generic `tms/servreg`. Whether a vendor-specific `battmgr/*` service
   ever appears is unverified.

---

## 10. Scratch artifacts (regeneratable)

- `/tmp/astro_u/jsn/marble/` — the 7 fleet manifests, md5-verified (§1.1).
- `/tmp/astro_u/jsn/hotdog/` — the 7 older-generation manifests (§1.2).
- `/tmp/astro_u/jsn/all/`, `cen/`, `raw/`, `woa/`, `lfw/` — 71 total
  manifests across 13 SoC/device directories, plus the linux-firmware and
  WOA cross-checks.
- `/tmp/astro_u/jsn/realall/` — the flat 71-file corpus the test suite
  consumes via `JSN_REAL_DIR`.
- `/tmp/astro_u/jsn/qcom_pd_mapper.c`, `mdt_loader.c`, `qcom_q6v5_pas.c` —
  kernel sources as fetched.
- `/tmp/astro_u/jsn/pdmapper/` — `linux-msm/pd-mapper` clone.
- `/tmp/astro_u/jsn/WHENCE` — linux-firmware `WHENCE` (537,962 B).

Payload bytes are **not** committed per programme rules; the tool/fixtures
in `implementations/pil-manifests/` are synthetic.

---

## 11. Sources (all accessed 2026-11-18 unless noted)

| # | source | what it pins |
|---|---|---|
| 1 | https://github.com/torvalds/linux/blob/master/drivers/soc/qcom/qcom_pd_mapper.c | the domain/instance/service table as C; `SERVREG_QMI_VERSION 0x101`; implicit `tms/servreg`; per-SoC `compatible` lists |
| 2 | https://github.com/torvalds/linux/blob/master/drivers/soc/qcom/mdt_loader.c | split-MDT naming `b%02d`; **no** manifest parsing (the negative) |
| 3 | https://github.com/torvalds/linux/blob/master/drivers/remoteproc/qcom_q6v5_pas.c | `firmware_name` per SoC; **no** `.jsn` reference |
| 4 | https://github.com/torvalds/linux/blob/master/drivers/soc/qcom/pdr_interface.c | `struct pdr_service` (`service_data_valid`, `service_data`) |
| 5 | https://github.com/linux-msm/pd-mapper (`json.c`, `json.h`, `pd-mapper.c`, `servreg_loc.h`) | the on-disk grammar, `pd_load_map()`, `.jsn`/`.jsn.xz` discovery, 127-byte string cap, digit-only numbers |
| 6 | https://gitlab.com/kernel-firmware/linux-firmware/-/raw/main/WHENCE | 114 `*.jsn` RawFile/Link entries — public redistribution |
| 7 | https://github.com/armbian/firmware (trees `qcom/*`) | byte-exact 403/405/512/513/515/516/534/555/562/703/713/731 B copies |
| 8 | https://github.com/iLtanaka/firmware-xiaomi-marble (`marble/`) | the **7/7** 17-device-set md5 matches (2026-11-19) |
| 9 | https://github.com/Sr-0w/hotdog-linux-bringup (`aports/.../firmware-oneplus-hotdog/`) | the older-generation 403/405/555/713/719 B fleet md5s |
| 10 | https://github.com/libretro/Lakka-LibreELEC (`projects/Ayn/devices/Odin/firmwares/files/qcom/sdm845/`) | sdm845 baseline seeds (403/555/713/425/423 B) |
| 11 | https://github.com/aarch64-laptops/firmware-qcom-woa (`jsn/`) | the +1-byte trailing-newline variants (514/406 B) |
| 12 | https://github.com/batocera-linux/batocera.linux, https://github.com/armada-os/armada | per-SoC file-set census (batocera `sm6115/mangmi`, armada `sm8550/thor`, `sm8750/odin3`) |

Not legal advice. Regulatory context for actually replacing radio
firmware: `../../upstream-contribution/radio-regulatory-hurdles.md`.
