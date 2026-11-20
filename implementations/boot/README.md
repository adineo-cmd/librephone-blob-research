# `boot` — replace or interoperate with the blob: a layer-by-layer answer

**Clean-room statement.** This document contains no proprietary code, headers,
strings or payload. Its sources are public GitHub repositories (including two
published by Qualcomm under BSD-3-Clause-Clear), the public GPL kernel tree,
and this repository's own committed research. No vendor bootloader binary was
disassembled to produce it.

Issue #2042. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. All remote references verified **2026-11-20**.

## 0. Answer up front

**"The boot chain" is not one thing. It is four layers with four different
answers, and conflating them is why this looks impossible.**

| # | layer | runs on | free implementation? | verdict |
|---|---|---|---|---|
| 1 | **XBL** (eXtensible BootLoader) | Cortex-A, from `xbl_a` | **no** — signed, closed | cannot replace [F] |
| 2 | **ABL** (Android BootLoader, LK-derived) | Cortex-A, from `abl_a`/`abl_b` | **yes, from Qualcomm** — `qualcomm/abl2esp`; plus the LK/aboot lineage itself at `git.codelinaro.org/linaro/qcomlt/lk` | replaceable on unlocked devices [F] |
| 3 | **OS bootloader** (what loads *your* kernel) | Cortex-A, from `boot` | **yes** — lk2nd, U-Boot, TF-A, edk2 | fully free [F] |
| 4 | **Boot control** (A/B slot, bootable flags) | Linux userspace | **yes** — `qbootctl` | fully free [F] |

The layer everyone assumes is the blocker — ABL — is the one **Qualcomm has
published a reimplementation of**. The layer that genuinely cannot be replaced
is XBL, one step below it.

### 0.1 The aboot lineage this rests on

ABL is not built from nothing. The `littlekernel/lk` README states it plainly [F]:

> "LK rarely appears on a spec sheet, but it runs underneath a great many
> devices, mostly as the bootloader or secure-world OS … Qualcomm's
> long-running aboot bootloader and MediaTek's second-stage bootloader are both
> built on LK."

And `LineageOS/android_external_lk2nd` describes itself as "a fork of the
original open-source bootloader from Qualcomm, which is a heavily modified
version of the Little Kernel Embedded Operating System" [F].

So there are **two** free sources for this layer, not one: the modern
`abl2esp` reimplementation (minimal, BSD-3-Clause-Clear) and the **original
CAF aboot lineage** published by Linaro at `git.codelinaro.org/linaro/qcomlt/lk`
(verified reachable, HTTP 200, 2026-11-20) [F]. lk2nd is itself a fork of that
lineage — which is why its licence is the LK MIT licence and not something new.

## 1. The correction: I was wrong in my own SEARCH comment

My SEARCH comment stated: *"`qualcomm/abl` -> **HTTP 404**. The vendor ABL
source is not public."*

**I retract that.** The 404 is real — there is no repo named `qualcomm/abl` —
but I searched for a *name* instead of enumerating the organisation. Doing that
found two vendor-published boot components [F]:

| repo | licence | language | stars | last push |
|---|---|---|---|---|
| `qualcomm/abl2esp` | BSD-3-Clause-Clear | Rust | 12 | 2026-01-05 |
| `qualcomm/fastboot.efi` | BSD-3-Clause-Clear | Rust | 23 | 2026-05-01 |

`abl2esp` README, verbatim [F]:

> "**abl2esp** is a minimal reimplementation of ABL that will search for
> *EFI\boot\bootaa64.efi* across all available file systems and attempt to load
> and start what it finds."

> "**Disclaimer:** this tool is made available for developer convenience. It's
> not intended for product usage."

`fastboot.efi` README, verbatim [F]:

> "*fastboot.efi* is an implementation of a subset of the fastboot protocol as a
> standalone EFI application … It also has a more optimistic memory allocation
> policy, allowing for booting large images. *fastboot.efi* supports booting
> abootimg v2 and PE32+ (EFI) images. Supported fastboot commands are **boot**,
> **continue**, and **reboot**."

That is the whole replacement strategy in two paragraphs: **make ABL be a
minimal EFI application, and hand off to an EFI payload.** Everything below the
handoff is then standard UEFI, which is where lk2nd/edk2/U-Boot come in.

## 2. The ABL container spec — stated by the vendor, and it closes a gap this repo names

`abl2esp`'s README describes the on-flash ABL image in one sentence [F]:

> "The *ABL* is a standard EFI PE32+ application, wrapped in a FV, inside a
> LZMA, inside a FV, inside an ELF file, with authentications segments added,
> which is stored in the *abl_a* and *abl_b* partitions."

That is:

```
abl_a / abl_b partition
└── ELF                        <- "with authentication segments added"
    └── FV                     <- outer firmware volume
        └── LZMA               <- compressed section
            └── FV             <- inner firmware volume
                └── PE32+ app  <- the actual ABL, a standard EFI application
```

This is not prose only — the packaging tree makes it executable [F]:

| file | size | what it fixes in place |
|---|---:|---|
| `packaging/FVMAIN_COMPACT.inf` | 618 B | inner FV: `EFI_BASE_ADDRESS = 0x80200000`, `EFI_BLOCK_SIZE = 0x200`, `EFI_NUM_BLOCKS = 0x110` |
| `packaging/FVMAIN.inf` | 636 B | outer FV: `EFI_BLOCK_SIZE = 0x40`, `EFI_NUM_BLOCKS = 0x0` |
| `packaging/image_header.py` | 4,926 B | the MBN/ELF wrapper: `IMAGE_KEY_MBN_TYPE`, `IMAGE_KEY_IMAGE_DEST`, `APPSBL_IMG`, `non_secure`, `nohash` mode |
| `packaging/elf_tools.py` | 34,939 B | 900 lines of hash-segment / ELF tooling (`hash` appears 104×) |
| `packaging/FVMAIN.ext` | 20 B | FV extended header |

`0x200 × 0x110 = 139,264 B` = `0x22000` — the inner firmware volume's declared
capacity [F].

### 2.1 Why this matters specifically to this repo

`research/qualcomm/docs/bootchain-census.md:83` records the lab's own
measurement of `abl` [F]:

```
abl | 245,760 | ELF32 mach=40 (EM_ARM) | ARM32 (self-consistent: entry = LOAD vaddr;
      instr-level unverified) | 0x9fa00000 | (payload opaque)
```

**"payload opaque" is now closed.** The payload is PE32+ → FV → LZMA → FV → ELF,
and the vendor publishes the tooling that constructs it. The 245,760 B FP6
observation is consistent with an outer ELF carrying those layers plus the
authentication segments the README names [I].

One caution the repo should carry forward: that census line records `EM_ARM`
(32-bit) for the *outer* ELF, while `abl2esp` builds `aarch64-unknown-uefi`. The
outer wrapper's `e_machine` therefore does not describe the ABL payload's bitness
— the wrapper and the payload are different architectures [I]. The lab has
already caught this exact trap one row up: `bootchain-census.md:82` annotates
`uefi` as "ELF64 mach=40 (**junk: ELF64+ARM is an invalid combo**)", and `:80`
as "ELF64, mach=1 (**junk**)". So "the outer ELF's machine field is not
meaningful" is the established pattern for this partition family, and it applies
to `abl` too. This is the same class of trap as firmware filenames not matching
GPU revisions in `research/soc/Qualcomm-SM7325-Snapdragon-778G-5G-gpu.md`.

## 3. Layer 3 — the OS bootloader, where the free options actually are

### 3.1 `msm8916-mainline/lk2nd` — MIT, 643 stars, active

[F] `LICENSE` is the original **LK MIT licence** ("Little Kernel (LK) was
originally created by Travis Geiselbrecht and is published under a MIT
License"). Last push **2026-11-07** — actively developed.

Its two configurations, verbatim from the README [F]:

- **lk2nd** — "secondary" bootloader. "does **not** replace the stock
  bootloader. Instead, it is packed into an Android boot image, which is then
  loaded by the stock bootloader just like the original Android image."
- **lk1st** — "primary bootloader intended for single-board computers (SBCs)".

The lk2nd trick, from `lk2nd/project/lk2nd.mk` [F]:

```
LK2ND_PARTITION_BASE ?= boot
LK2ND_PARTITION_NAME ?= lk2nd
LK2ND_PARTITION_SIZE ?= 512*1024
# Use part of the "boot" partition for the lk2nd boot image. The real Android
# boot image can be placed in the partition with 512 KiB offset.
```

**This is the decisive practical fact for this issue: lk2nd does not require
replacing anything.** It lives inside the `boot` partition as a normal Android
boot image, so it works with the stock XBL/ABL chain intact and with the
bootloader lock still enforced. No exploit, no signing, no fusing change.

**Coverage gap [F]:** `lk2nd/project/` contains `msm8909.mk`, `msm8916.mk`,
`msm8952.mk`, `msm8953.mk`, `msm8960.mk`, `msm8x60-late.mk`. **There is no
MSM8998 project file.** lk2nd is not an option for Snapdragon 835.

### 3.2 `edk2-porting/edk2-msm8998` — 188 stars, the only MSM8998 option

[F] README: "A broken but working EDK2 implementation for Snapdragon 835
platform". Default branch `new`, last push **2023-07-16** (unmaintained for
three years — flag this).

Supported devices, verbatim from its table [F]:

| device | target name | ACPI |
|---|---|---|
| OnePlus 5 | `cheeseburger` | yes |
| OnePlus 5T | `dumpling` | yes |
| LG V30 | `joan` | yes |
| Xiaomi Mi 6 | `sagit` | yes |
| Xiaomi Mi Mix 2 | `chiron` | yes |
| Essential Phone PH-1 | `mata` | yes |
| HTC U11+ | `htc_ocmdtwl` | **no** |

Two warnings from its own README that must be quoted, not paraphrased [F]:

> "**DO NOT EVER TRY TO PORT IT TO *SONY, SAMSUNG* DEVICES**"
> "**YOUR UFS WILL BE WIPED CLEAN!!!**"

### 3.3 U-Boot and TF-A — present, but not for this SoC

[F] `u-boot/u-boot` has `arch/arm/mach-snapdragon/` (7 entries:
`Kconfig`, `Makefile`, `board.c`, `capsule_update.c`, `include/`, `of_fixup.c`,
`qcom-priv.h`) but exactly **two** Qualcomm defconfigs in `configs/`:
`dragonboard410c_defconfig` and `dragonboard820c_defconfig`. So U-Boot's
Qualcomm support targets DB410c (APQ8016) and DB820c (MSM8996) — **not
MSM8998** [F].

[F] `ARM-software/arm-trusted-firmware` `plat/qti/` contains:
- `bear` — `mdm9607`, `msm8909`, `msm8916`, `msm8939`
- `bruin` — `agatti`, `shikra`
- `hoya` — `kodiak`, `lemans`, `monaco`, `qcs615`, `sc7180`, `qtiseclib`

**No MSM8998 or MSM8996 platform in TF-A** [F]. Note `plat/qti/hoya` covers
`qcs615` — the SoC that `talos.dtsi` was wrongly attributed to in my
SM4375 note (`research/soc/Qualcomm-SM4375-Snapdragon-4-Gen-1-gpu.md`), so TF-A
*qti* is the right tree to look in for that family, not MSM8998.

## 4. Layer 4 — boot control

`linux-msm/qbootctl` [F]: 20 stars, **GPL-3.0**, C, last push 2025-03-24.
README: "Qualcomm bootctl HAL for Linux … pulled from AOSP source code and
bastardised to build and run on a musl/glibc system." Full command surface:
`-c` current slot, `-s SLOT` set active, `-m` mark successful, `-u` mark
unbootable, `-b`/`-n`/`-x` queries, `-i` write GPT even if the UFS bLun cannot
change.

This matters because A/B slot state is stored in **GPT partition attributes**
and Qualcomm-specific UFS LUN metadata — not in a file. `qbootctl` is the free
implementation of exactly that, and the postmarketOS wiki documents it as the
standard tool (including for dual-booting postmarketOS alongside Android).

## 5. Device coverage — the honest numbers, and the gap this issue cannot fill

Corpus (`coverage-matrix.csv`) [F]:

```
boot family:      1,038 rows / 123 devices / 26 distinct filenames / 23,864,283,348 B
boot.img:           125 rows   dtbo.img: 118   vbmeta.img: 115
recovery.img:        86 rows   abl.img:   79   xbl.img: 63
xbl_config.img:      63 rows   qupfw.img:  63   aop.img: 40
abl.img:             79 rows /  79 devices / 69 distinct (size,md5) pairs
```

`abl.img` sizes across the fleet span **151,552 … 2,740,224 B** with **69
distinct (size, md5) pairs for 79 devices** — i.e. ABL is almost never shared
between devices [F]. That is expected for a signed per-device image, and it is
the reason a single free ABL cannot be a drop-in for the fleet.

### 5.1 The coverage gap is total, not partial

Mainline carries **15** MSM8998 device-tree files, of which **11 are board
`.dts`** [F]:

```
msm8998-asus-novago-tp370ql.dts   msm8998-oneplus-cheeseburger.dts
msm8998-fxtec-pro1.dts            msm8998-oneplus-dumpling.dts
msm8998-hp-envy-x2.dts            msm8998-sony-xperia-yoshino-lilac.dts
msm8998-lenovo-miix-630.dts       msm8998-sony-xperia-yoshino-maple.dts
msm8998-mtp.dts                   msm8998-sony-xperia-yoshino-poplar.dts
msm8998-xiaomi-sagit.dts
```

The other four are shared includes: `msm8998.dtsi`, `msm8998-clamshell.dtsi`,
`msm8998-oneplus-common.dtsi`, `msm8998-sony-xperia-yoshino.dtsi` [F].

I checked every device supported by `edk2-msm8998` — including four that
mainline does **not** cover (`chiron`, `mata`, `joan`, `htc_ocmdtwl`) — plus
every MSM8998 board in mainline, against the matrix [F]:

```
cheeseburger 0   dumpling 0   sagit 0   chiron 0   mata 0   joan 0
htc_ocmdtwl  0   lilac    0   maple 0   poplar 0   novago 0 pro1 0
envy-x2      0   miix-630 0
```

**All fourteen are zero.** This independently confirms #2018's finding: the
matrix holds **no Snapdragon 835 boot data at all**, only the two SM8150 phones
mislabelled as MSM8998 (`OnePlus_7` 8 boot rows, `OnePlus_7T` 9 boot rows).

So for `boot`, the corpus cannot answer "which free bootloader should device X
use" for any genuine 835 device — the devices are absent. The map in §0 is
derived from upstream sources, not from corpus rows [F].

## 6. Honest negatives

1. **I retracted a claim I made in my own SEARCH comment** (§1: "the vendor ABL
   source is not public" → wrong; `qualcomm/abl2esp` is published). Recorded in
   public rather than silently corrected [F].
2. **I built and booted nothing.** No ARM64 device was available. Every
   recommendation is a documented path, not a tested one [N].
3. **`abl2esp` explicitly disclaims product use** — "made available for
   developer convenience … not intended for product usage" [F].
4. **Signing is not public.** `abl2esp`'s README says to "sign this with a test
   signature using *sectools*, or equivalent". `sectools` is not a public
   Qualcomm repository [N]. So a rebuilt ABL still needs a device whose secure
   boot is unlocked or disabled — the free ABL does not defeat the signature
   check, it *replaces the signed payload* on devices that do not enforce it.
5. **`edk2-msm8998` is unmaintained since 2023-07-16** and self-describes as
   "broken but working". Treat it as a research vehicle, not a supported port [F].
6. **The 32-bit `EM_ARM` outer ELF vs 64-bit AArch64 payload** (§2.1) is my
   inference from two facts in two sources; I did not verify it by unpacking an
   ABL image — the payloads are not in this checkout [I, N]. The repo's own
   `uefi`/`xbl_config` rows being annotated "junk" supports the inference but
   does not prove it for `abl`.
7. **lk2nd's device list was not enumerated** — only its SoC project files,
   which is enough to show MSM8998 is absent, but not enough to say which of the
   643-star project's devices use which project file [N].
8. **The metasearch backend returned zero results for all eight initial boot
   queries.** I recorded that as a tool outage and substituted the GitHub REST
   API. It is possible additional prior art exists that those queries would have
   found [N].
9. **`qualcomm/edk2` (1 star, NOASSERTION) was found but not examined** — it
   may be Qualcomm's own EDK2 tree and could be more current than
   `edk2-porting/edk2-msm8998` [N].
10. **`git.codelinaro.org/linaro/qcomlt/lk` returned HTTP 200 at its root but I
    could not read a file from it** — `/-/raw/` paths gave 404 and one gave 429.
    I verified the repository is reachable, **not** what it contains, so I make
    no claim about which SoCs its ABL tree supports [N].

## 7. Rule 1 — corrections for the lead, not applied here

1. **`research/qualcomm/docs/bootchain-census.md:83`** says `abl` "payload
   opaque". Suggested replacement:

   > "payload = PE32+ EFI application → inner FV (`0x200`×`0x110`) → LZMA →
   > outer FV (`0x40` block) → ELF with authentication segments, per
   > `qualcomm/abl2esp` README and `packaging/*.inf` (BSD-3-Clause-Clear,
   > verified 2026-11-20). The outer ELF's `EM_ARM` describes the wrapper, not
   > the payload."

2. **`docs/REPO-STATE-MAP.md:33` and `:47`** both read boot = PARTIAL /
   "FP6 only". With this note the boot family is mapped corpus-wide
   (1,038 rows / 123 devices) and each of the four layers has a stated answer.
   Still not COMPLETE — no parser exists and no 835 device is in the corpus —
   but "FP6 only" is no longer accurate.

3. **`docs/REPO-STATE-MAP.md:18`** still reads "GPU core ID | 27 | NEW | none".
   `research/soc/` now holds **five** per-SoC GPU identifications (SM8350,
   SM7325, SM4375, MSM8998, and the implied a5xx family). Fifth flag.

## Sources

| claim | source | access |
|---|---|---|
| ABL is a PE32+ app in FV in LZMA in FV in ELF | `qualcomm/abl2esp` README.md | 2026-11-20 |
| aboot/ABL built on LK; MediaTek too | `littlekernel/lk` README.md | 2026-11-20 |
| lk2nd is a fork of Qualcomm's open-source aboot | `LineageOS/android_external_lk2nd` repo description | 2026-11-20 |
| CAF aboot lineage source reachable | `git.codelinaro.org/linaro/qcomlt/lk` → HTTP 200 | 2026-11-20 |
| `abl2esp` = minimal ABL reimplementation, not for product use | same README | 2026-11-20 |
| inner FV `0x80200000` / `0x200` × `0x110` | `abl2esp/packaging/FVMAIN_COMPACT.inf` | 2026-11-20 |
| outer FV block size `0x40` | `abl2esp/packaging/FVMAIN.inf` | 2026-11-20 |
| MBN/ELF wrapper keys, `APPSBL_IMG`, `nohash` | `abl2esp/packaging/image_header.py` | 2026-11-20 |
| 34,939 B / 900-line ELF hash tooling | `abl2esp/packaging/elf_tools.py` | 2026-11-20 |
| fastboot subset over EFI, abootimg v2 + PE32+ | `qualcomm/fastboot.efi` README.md | 2026-11-20 |
| BSD-3-Clause-Clear on both | GitHub licenses API | 2026-11-20 |
| lk2nd = MIT (LK licence), 643 stars, active | `msm8916-mainline/lk2nd` LICENSE, repo API | 2026-11-20 |
| lk2nd does not replace stock bootloader; 512 KiB offset | `lk2nd` README + `lk2nd/project/lk2nd.mk` | 2026-11-20 |
| lk2nd SoC projects (no MSM8998) | `lk2nd/lk2nd/project/` listing | 2026-11-20 |
| edk2-msm8998 device table + wipe warning | `edk2-porting/edk2-msm8998` README.md | 2026-11-20 |
| U-Boot: only db410c + db820c Qualcomm defconfigs | `u-boot/u-boot` `configs/`, `arch/arm/mach-snapdragon/` | 2026-11-20 |
| TF-A `plat/qti` = bear/bruin/hoya, no msm8998 | `ARM-software/arm-trusted-firmware` | 2026-11-20 |
| qbootctl GPL-3.0, command surface | `linux-msm/qbootctl` README | 2026-11-20 |
| postmarketOS documents qbootctl for A/B | wiki.postmarketos.org, *Android AB Slots* | 2026-11-20 |
| 15 msm8998 dts files (11 board `.dts`) | `arch/arm64/boot/dts/qcom/` listing | 2026-11-20 |
| 14/14 devices have 0 matrix rows | `coverage-matrix.csv` | 2026-11-20 |
| boot family 1,038 rows / 123 devices / 23,864,283,348 B | `coverage-matrix.csv` | 2026-11-20 |
| `abl` "payload opaque", 245,760 B, `EM_ARM` | `research/qualcomm/docs/bootchain-census.md:83` | 2026-11-20 |

## Reproduce

```sh
# the vendor ABL reimplementation and its container spec
curl -s https://raw.githubusercontent.com/qualcomm/abl2esp/main/README.md
curl -s https://raw.githubusercontent.com/qualcomm/abl2esp/main/packaging/FVMAIN_COMPACT.inf
curl -s https://raw.githubusercontent.com/qualcomm/abl2esp/main/packaging/FVMAIN.inf

# lk2nd coverage (no msm8998)
curl -s https://api.github.com/repos/msm8916-mainline/lk2nd/contents/lk2nd/project
curl -s https://raw.githubusercontent.com/msm8916-mainline/lk2nd/main/lk2nd/project/lk2nd.mk

# U-Boot / TF-A SoC coverage
curl -s https://api.github.com/repos/u-boot/u-boot/contents/configs | grep -o '"dragonboard[^"]*"'
curl -s https://api.github.com/repos/ARM-software/arm-trusted-firmware/contents/plat/qti

# corpus numbers
python3 -I -c "
import csv
from collections import Counter
r=list(csv.DictReader(open('upstream-contribution/blob-database/coverage-matrix.csv')))
b=[x for x in r if x['blob_family']=='boot']
print('rows',len(b),'devices',len({x['device'] for x in b}),
      'files',len({x['filename'] for x in b}),
      'bytes',sum(int(x['size_bytes']) for x in b))
a=[x for x in b if x['filename']=='abl.img']
print('abl',len(a),'distinct',len({(x['size_bytes'],x['md5_db']) for x in a}))
for d in ['cheeseburger','dumpling','sagit','chiron','mata','joan','htc_ocmdtwl',
          'lilac','maple','poplar','novago','pro1','envy-x2','miix-630']:
    print(' ',d,len([x for x in r if x['device'].lower()==d]))"
```
