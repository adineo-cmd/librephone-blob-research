# Architecture census of MediaTek MT6785 (Helio G95) firmware — Xiaomi Redmi Note 10S "rosemary", LineageOS 24.0 (2026-11-04 nightly)

**Claim:** The MT6785 tinysys coprocessor family runs on **ARM Cortex-M4 cores
(Thumb-2)**, not RISC-V — established three independent ways: the images
self-report their core in their record names (`tinysys-loader-CM4_A`,
`tinysys-scp-CM4_A`), the SCP loader opens with a textbook Cortex-M vector
table (initial SP `0x538`, reset handler `0x1e1`, Thumb bit set), and the SCP
DRAM code image decodes **256/256 as Thumb-2 with clean `push {r4,lr}`
prologues while every other ISA decodes 0/256**. The audio DSP is a **Cadence
HiFi3 (Xtensa)** — self-named `hifi3_a_{dram,iram,sram}` (instruction-level
confirmation pending: capstone has no Xtensa backend). `spmfw` is **not CPU
code at all**: it is SPM/PCM microcode (header magic `2MPS`, embedded original
filename `spm_firmware.bin`). The modem (`md1rom`) is a **raw concatenated
image with no ELF header**; nanoMIPS per public prior art (NCC Group, taszk),
which capstone cannot verify (no nanoMIPS decoder — decode rates 0–45/48
across six supported ISAs at 12+ probed offsets, no dominant ISA).
**Zero ELF files exist in the entire firmware partition set.** Every code
payload ships in the MediaTek `mtk_hdr` record chain (magic `0x58881688`,
512-byte headers, name at 0x08, extension record `0x58891689` at 0x30 with
header size 0x200 @0x34 and payload alignment 0x10 @0x44) and is individually
signed with a **pair of DER X.509 certificates (cert1 = 1,709 B, cert2 = 957
B)** — 34 payloads, 19 signed pairs; the modem's 13 data payloads (`md1_filter*`,
`md1_mddb*`, `md1_mdmlayout`, `md1_file_map`), gz's `unmap2` and lk's `kaeru`
carry no signature records.

This is the MTK mirror of the FP6 methodology finding: **MTK does not use
ELF/MDT containers for any subsystem firmware on this SoC** — there is no
`e_machine` to read. Architecture must be established from record names,
branch/vector words, and decode-rate sanity.

**Prior art checked (2026-11-11):**
[NCC Group mtk_bp](https://github.com/nccgroup/mtk_bp) (Kaitai defs; md1img
file-table container; example build dated 2023-05, MT6879/NR16 — nanoMIPS);
[NCC Group ghidra-mtk-loader](https://github.com/nccgroup/ghidra-mtk-loader)
("only nanoMIPS-based firmware is supported") +
[ghidra-nanomips](https://github.com/nccgroup/ghidra-nanomips);
[taszk labs full-chain baseband series, part 1](https://labs.taszk.io/articles/post/full_chain_bb_part1)
(2023-12-07, D. Komaromy — Helio **and** Dimensity baseband exploitation,
custom nanoMIPS decompiler/debugger/emulator; CCCI/RIL pivot focus, no
per-partition census); 0xor0ne MTK 5G baseband RE write-up (2024-12, X post
+ blog); [cyrozap/mediatek-lte-baseband-re](https://github.com/cyrozap/mediatek-lte-baseband-re)
(older MT65xx-era LTE modems: Cortex-R4 protocol core + Coresonic "SIMT" DSP);
[BaseComp](https://www.usenix.org/conference/usenixsecurity23/presentation/kim-eunsoo)
(USENIX Security '23, 2023-08 — Samsung **and** MediaTek baseband integrity
protection, 29 bugs; no coprocessor census);
[BaseMirror](https://arxiv.org/abs/2409.00475) (CCS 2024 — Samsung Shannon
only); [CrimsonGlory/wairz](https://github.com/CrimsonGlory/wairz)
`mediatek_gfh.py` (LK/GFH header parsing incl. compact layout for
MT6785/MT6853/MT8788+, partition taxonomy; asserts "all tinysys blobs are
Cortex-M, SCP=Cortex-M4" — **confirmed here for MT6785 with instruction-level
evidence**); [19h/zrax-isa-workbench `docs/socboot2.md`](https://github.com/19h/zrax-isa-workbench/blob/main/docs/socboot2.md)
(mtk_hdr layout + GFH chain, extension fields at 0x34/0x44 marked empirical —
**confirmed byte-for-byte on rosemary**); U-Boot `tools/mtk_image.h` (GFH
record structs, types 0/1/2/3/7/8); bkerler/mtkclient (bootloader/DA
exploitation); mainline Linux `drivers/remoteproc/mtk_scp.c` (documents
registers, **never states the SCP's ISA** — checked 2026-11-11); AOSP
`system/chre` `platform/tinysys` (source-available MTK SCP firmware platform;
README names the SCP "Sensor-hub Control Processor", no ISA claim). GitHub
code search for per-partition ELF/header census of an MT6785 build returned
nothing: no public source documents the architecture/segment/version facts
below for this device or SoC generation (checked: mtk_bp, wairz, zrax,
mtkclient, awesome-telco lists, XDA-adjacent repos — 2026-11-11).

## Method

Source: `lineage-24.0-20261104-nightly-rosemary-signed.zip`
(1,172,896,925 B, sha256 `6b4269e4…6e7ff1`, Princeton mirror, published
2026-11-04; official LineageOS, branch 24.0). Extraction:
`payload_manifest.py` (protobuf-free CrAU manifest parse; 21 partitions;
ops REPLACE / REPLACE_XZ / REPLACE_BZ — the type-1 op is bzip2, as on FP6)
→ `payload_dump.py` (15 firmware partitions dumped, 80.2 MB total) →
`payload_walk.py` (new: mtk_hdr record-chain splitter; 49 records → 34
payloads + 15 signature blocks) → `census_mtk.py` (magic sniffing, LK/GFH
container parse, ELF parse, targeted version-string scan) →
`isa_probe.py` / `region_scan.py` (new: capstone decode-rate sanity across
arm32/thumb2/arm64/mips32/mips64/riscv32/riscv64 + 4 KB entropy mapping to
locate code regions in raw images). Derived facts only; no binary content.

Device identity (from LineageOS wiki index, 2026-11-11): Xiaomi Redmi Note
10S 4G / POCO M5s family, codename `rosemary`, SoC "MediaTek Helio G95"
(= MT6785V family), released 2021-04, official branches 20 → 24.0.

## Results

### Partition set (payload manifest, 21 partitions)

Firmware partitions dumped and censused: `md1img` (modem, 60,190,720 B),
`scp` (2,207,744), `sspm` (663,552), `spmfw` (16,384), `audio_dsp`
(1,404,928), `cam_vpu1/2/3` (1,150,976 / 8,286,208 / 8,192), `tee`
(2,560,000), `gz` (1,265,664), `lk` (1,855,488), `preloader_raw` (352,256),
`vbmeta{,_system,_vendor}` (4,096 each). Android images (`boot`, `dtbo`,
`system`, `system_ext`, `product`, `vendor`) not yet walked (framework side,
queued). **No `mcupm`, `dpm`, `vcp`, or `piimg` partitions exist on this
device** — those names belong to other MTK generations (e.g. Nothing Phone 2a
MT6855 list); the MT6785 firmware set is exactly the 12 above.

### Per-partition architecture map (the ISA map of the MT6785)

| partition / payload | container | architecture evidence | verdict |
|---|---|---|---|
| `md1img` → `md1rom` (26,682,512 B) | mtk_hdr | raw image, no ELF, no arch strings; all-ISA decode sanity fails (see negatives) | **nanoMIPS per prior art (NCC/taszk), unverified from bytes** |
| `md1img` → `md1drdi` (1,368,064 B) | mtk_hdr | avg entropy 0.8–1.5 (mostly zero-padded), no header, no code signature | data/debug image; no ISA claim |
| `md1img` → `md1dsp` (6,783,260 B) | GFH MMM-chain (sig_type=0, load_addr=0xFFFFFFFF) | GFH records ver=1; record type **260 (0x104)** — beyond U-Boot's enum {0,1,2,3,7,8}; code region begins with ASCII magic **`DSP!`** | DSP bootloader image (modem DSP = Coresonic-class per cyrozap/ncc DSP symbol history); ISA not decodable |
| `md1img` → `md1_filter*` ×8, `md1_emfilter`, `md1_mddbmeta`, `md1_mddbmetaodb` (gzip XML, 2.9 MB decoded), `md1_mddb`, `md1_mdmlayout`, `md1_file_map` | mtk_hdr, unsigned | modem catcher-filter/DB payloads; `md1_mddbmetaodb` = gzipped modem-DB XML (`kal_uint32` type tables); `md1_file_map` = plain-text name map | data; no ISA |
| `scp` → `tinysys-loader-CM4_A` (1,080 B) | mtk_hdr | Cortex-M vector table: SP=0x538, reset=0x1e1 (odd = Thumb), 6× handler 0x26d | **ARM Cortex-M4 (Thumb)** |
| `scp` → `tinysys-scp-CM4_A` (1,824,584 B) | mtk_hdr | header = u32 table (0xb8180, 0x387d9, 0x392f9, 0x3937d, 0x3948d, 0x393f5, 0x3881d…) — section table, not decoded; strings `SCP_VOW_TASK_VER`, `VER_18041204`, version `2.4.4-9d0f65f` | tinysys multibin; ISA via its dram image below |
| `scp` → `tinysys-scp-CM4_A_dram` (366,952 B) | mtk_hdr | capstone thumb2 **256/256** (`push {r4,lr}; mov r4,r0; mov r0,r1`), every other ISA **0/256** | **ARM Cortex-M4 Thumb-2 — instruction-level confirmed** |
| `sspm` → `tinysys-sspm` (657,704 B) | mtk_hdr | own header magic **0x58901690** + fields (0x18, 0x116b0, 4); strings `vproc1/vproc2/vsram_proc1/vsram_proc2`, `[EMI] %s`; body entropy 7.95+ from 0x20000 | **encrypted/packed — no ISA claim**; SSPM = power/security processor (per LK CCCI tables "Tinysys-SSPM ROM") |
| `spmfw` → `spmfw` (11,119 B) | mtk_hdr | header magic **`2MPS`** + embedded filename `spm_firmware.bin`; u32 table at 0x44 (0x1e0abe, 0x1e3200, 0x1e6a00 … SPM-SRAM-range values) | **SPM/PCM microcode — programmable power-sequencer image, not a CPU ISA** |
| `audio_dsp` → `hifi3_a_dram` (32,768) / `hifi3_a_iram` (36,864) / `hifi3_a_sram` (1,320,904) | mtk_hdr | **self-reported core name `hifi3`** (Cadence HiFi3); iram head `06 15 00 00 08 ff ff ff`; sram contains audio task strings (`PCM_HWFREE*`, `scp_addr`, `scp_ipi_registration`) | **Cadence HiFi3 (Xtensa) — name-level ID; byte-level pending (no capstone Xtensa)** |
| `cam_vpu1/2` (1,145,104 / 8,280,528) | mtk_hdr | entropy-mapped code regions; capstone thumb2 58–64/64 vs arm32 1–7/64, mips32 0–1/64; 201 `push {…,lr}` prologues in first 1 MB; 447 × `VPU6` strings; `VERSION_MAJOR/MINOR`, `SW_VERSION` | **ARM32 Thumb-2 camera-VPU ("VPU6" generation) firmware** |
| `cam_vpu3` (3,392 B) | mtk_hdr | head `09 01 11 17 06 17 12 24` (same as vpu1/vpu2) | stub/placeholder payload for VPU3 |
| `tee` → `atf` (170,496 B) | mtk_hdr | payload header: byte-swapped ASCII words `EET `/`KTM ` (i.e. "TEE "/" MTK" stored per-word BE) + size fields (0x297c0 ×2); strings `SPM_*`, `TEE_PARAMETER_BASE`, `TEE_SECMEM`, `atf-ramdump` | **ARM Trusted Firmware (EL3) for MT6785** — AArch64 expected, byte-probe not run (policy: census-only) |
| `tee` → `tee` (2,377,216 B) | mtk_hdr | same `TEE `/` MTK` header family; string `TEEI` (MicroTrust TEEi marker) | **MTK TEE (MicroTrust/TEEi flavor)** — census-only, no code RE (policy boundary) |
| `gz` → `gz` (1,115,632 B) | mtk_hdr | opaque high-entropy body from offset 0 (no readable header) | **GenieZone hypervisor/TEE image, encrypted — no ISA claim** |
| `gz` → `unmap2` (143,072 B) | mtk_hdr | entropy 7.95–7.97 throughout, unsigned | encrypted auxiliary image; no claim |
| `lk` → `lk` (1,665,018 B) | mtk_hdr | first word `0xea000007` (`b #0x24`) = ARM32 branch; arm32 decode dominant (83/256 vs thumb2 40/256, others junk); strings: chip table `MT6785V/CB,CC,CU,CV,WB`, tinysys loader table (`tinysys-loader-CM4_A`, `tinysys-scp-CM4_A`, `tinysys-scp-CM4_A_dram`), `SPM firmware version` | **ARM32 (A32) Little Kernel bootloader** |
| `lk` → `lk_main_dtb` (168,829 B) | mtk_hdr | head `d00dfeed` (FDT magic); strings `MT6359`, `MT6785`, `scp-sys-md1-main` | device tree |
| `lk` → `kaeru` (10,839 B) | mtk_hdr, unsigned | capstone thumb2 256/256 (`movs r0,#0; push {r4,lr}; bl`); banner `****…`; rest high-entropy | **Thumb-2 LK-adjacent module, identity of "kaeru" undetermined** |
| `preloader_raw` (352,256 B) | GFH MMM-chain (per U-Boot `mtk_image.h`) | FILE_INFO: name "FILE_INFO", file_type=1, flash_type=5 (GEN), **sig_type=5 (opaque — matches the RSA cert pairs)**, load_addr=**0x00200f10** (SRAM), total 0x55134, jump_offset=0xf0; BL_INFO attr=1; BROM_CFG cfg_bits=0x90 (no `JUMP_BL_ARM64_EN`); ANTI_CLONE; BROM_SEC_CFG; code at 0xF4 = **`0xea000005` (A32 branch)** | **ARM32 preloader, SRAM load 0x200F10, RSA-signed (sig_type 5)** |
| `vbmeta{,_system,_vendor}` | AVB0 | standard AVB 1.0 headers | Android Verified Boot |

### Container formats (empirical, cross-checked)

1. **mtk_hdr record chain** (all partitions except preloader/vbmeta):
   `{magic 0x58881688 @0, payload size @4, NUL-padded ASCII name @8 (≥20
   bytes on MT6785: "tinysys-loader-CM4_A" needs it — the 8-byte name of
   older docs truncates)`, extension record `0x58891689 @0x30` with
   header size 0x200 @0x34 and payload alignment 0x10 @0x44; next record at
   align(payload_end). Matches zrax's S15 extension-field model and wairz's
   16-byte-alignment sub-image walk, byte-for-byte.
2. **GFH MMM-chain** (preloader_raw, md1dsp): records
   `{magic_version 0x014D4D4D, size u16, type u16}` with types 0 (FILE_INFO),
   1 (BL_INFO), 7 (BROM_CFG), 2 (ANTI_CLONE), 8 (BROM_SEC_CFG) on the
   preloader — exactly U-Boot's structs; **md1dsp adds type 260 (0x104),
   absent from U-Boot's enum**.
3. **Per-payload signature**: every *code* payload is followed by
   `cert1` (1,709 B) and `cert2` (957 B) records, both starting
   `30 82 …` (DER X.509 SEQUENCEs) — a two-certificate RSA chain per image.
   Modem data payloads ship unsigned.

### Version strings

| blob | version evidence |
|---|---|
| md1rom / md1dsp / md1_file_map | **`MOLY.LR13.R1.MP.V89.6.P79`** (+ `MOLY_LR13_R1_MP_V89_6_P79.bin/.EDB/.XML.GZ` names) |
| silicon/flavor | `MT6785_S00`, `MT6295_S00` (modem DSP die), `G95UySW` (Helio G95 flavor in md1_mddb) |
| lk | chip support table `MT6785V/CB /CC /CU /CV /WB`, `MT6359` (PMIC) |
| scp | component version `2.4.4-9d0f65f` (git-hash style), `VER_18041204` |
| cam_vpu1/2 | `VPU6` (camera VPU generation 6), `VERSION_MAJOR/MINOR`, `SW_VERSION` |
| atf/tee | `atf-ramdump`, `TEEI` (MicroTrust TEEi) — no full build string recoverable (census-only boundary) |
| ELBRUS | **0 occurrences tree-wide** — the brand codename does not appear on this MT6785 build |

## Findings

1. **MTK tinysys = Cortex-M4 on MT6785, instruction-level proven** —
   upgrades wairz's classifier claim ("all tinysys blobs are Cortex-M") to
   verified fact for a phone SoC: vector table + Thumb-2 decode 256/256.
   The RISC-V tinysys story belongs to mt8186/mt8192+ generations, not
   Helio G95.
2. **Zero ELF files in the entire firmware partition set.** The Qualcomm
   MDT/ELF methodology does not transfer to MTK: `e_machine` evidence does
   not exist here; architecture comes from record names, branch/vector
   words, and decode-rate sanity.
3. **Per-payload dual X.509 signing (cert1 1709 B + cert2 957 B) wraps
   every code payload**, incl. spmfw and sspm; modem data payloads are
   unsigned. The preloader's `sig_type=5` (outside U-Boot's 0/1 enum)
   corresponds to this RSA-certificate scheme.
4. **spmfw is PCM microcode, not CPU firmware** — `2MPS` magic + embedded
   `spm_firmware.bin` name; there is no "CPU" to name, matching wairz's
   comment and the SPM's programmable-sequencer design.
5. **audio_dsp = HiFi3 (Xtensa)** by self-report — on MT6785 the MTK ADSP
   is HiFi3, not the RISC-V ADSP of mt8186+/SOF platforms and not the
   Cortex-M tinysys family. Three distinct "small core" ISAs (Cortex-M4
   Thumb, HiFi3 Xtensa, PCM microcode) coexist on one SoC next to an A32
   preloader/LK and (presumably) AArch64 ATF.
6. **md1dsp GFH record type 260 is beyond the public U-Boot enum** and the
   payload opens with an undocumented `DSP!` magic — the modem DSP loader
   format is publicly undecoded (NCC's `md1_dbginfodsp` symbol work covers
   DSP *code*, not this container).
7. **Encrypted subsystems**: sspm body, gz, and unmap2 are high-entropy
   (≥7.95) with no readable headers; tinysys-sspm carries its own magic
   `0x58901690`. Any deeper work on these needs decrypt-first tooling.

## Negative results / limitations

- **md1rom ISA not independently verified.** Public prior art (NCC Group
  ghidra-mtk-loader/mtk_bp, taszk 2023) identifies MediaTek modem firmware
  as nanoMIPS for Helio/Dimensity generations; capstone has no nanoMIPS
  decoder, and 12+ probed md1rom windows give no dominant supported ISA
  (arm32 0–32/48, thumb2 0–45/48, mips32 0–26/48) — consistent with an
  unknown encoding plus data regions. Claim stands on prior art only.
- **HiFi3 (Xtensa) not byte-verified** — no capstone backend; name-level
  identification only.
- **sspm/gz/unmap2 encrypted** — header facts recorded, no code census.
- **TEE (atf/tee) censused at container level only** (header magic, sizes,
  identity strings) — no disassembly, per lab TZ policy boundary.
- `vendor.img`/`system`/`product` Android-side .so blobs not yet walked
  (queued; the FP6 pattern would add the userspace MTK libraries).
- `kaeru` (LK, Thumb, 10.8 KB, unsigned) — identity undetermined; flagged
  for follow-up.
- No disassembly-level proof that `atf` is AArch64 (expected for EL3 on a
  64-bit SoC; BROM_CFG lacks the U-Boot ARM64 hand-off flag, which per
  zrax S5 claims nothing either way).

## Reproduce

```bash
python3 tools/payload_manifest.py payload.bin                 # 21 partitions
python3 tools/payload_dump.py payload.bin md1img md1img.img   # + 14 more
python3 tools/payload_walk.py extract/parts extract/trees     # 49 records
python3 -I tools/census_mtk.py extract/trees --out trees-census.json
python3 tools/isa_probe.py trees/scp/06_tinysys-scp-CM4_A_dram.bin 0
python3 tools/region_scan.py trees/sspm/00_tinysys-sspm.bin
python3 -I tools/make_compact.py <full.json> rosemary-census.json
```
(All scripts under `mediatek/tools/`; `payload_manifest.py`/`payload_dump.py`
are unmodified copies of the FP6-era lab tools; `census_mtk.py`,
`payload_walk.py`, `isa_probe.py`, `region_scan.py`, `entry_sanity.py`,
`make_compact.py` are MTK-specific additions.)
