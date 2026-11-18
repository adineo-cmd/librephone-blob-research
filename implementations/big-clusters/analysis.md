# The laptop-half big clusters — vm-bootsys.img (×5) and modem.b16 (×11), fetched + identified (2026-11-19)

The two biggest unreached clusters in `blob-matrix/laptop/sharing-clusters.csv`
are now **fetched from public sources, md5-verified byte-exact against the
upstream database, and structurally identified**. This was the last large
unknown in the laptop half: a 257.5 MiB "other" partition image shared by 5
Xiaomi devices and a 473,648 B "modem" file shared by 11. Headline
results:

- `vm-bootsys.img` (269,996,032 B, md5 `db7c51a3…`) = the **Qualcomm
  Trusted VM (TVM) boot+system partition image**: a raw ext4 filesystem
  containing a complete Linux guest (`/trustedvm/system.img`, 225 MiB,
  "genericarmv8" LE/Yocto rootfs) plus the guest kernel shipped as
  **another Qualcomm split-ELF (MDT) image** (`trustedvm.mdt` + `.b00…b05`,
  which the lab's `mdt_probe.py` parses with zero errors). It is a whole
  second operating system for the hypervisor/trusted-UI stack, not a
  firmware blob.
- `modem.b16` (473,648 B, md5 `30c22653…`) = **a single mpss segment that
  is 100% zero bytes except for ONE 16-bit value** (`0x4f 0x12` = u16
  0x124f at offset 469,536). The 11-device "cluster" of one md5 across
  three Snapdragon generations is one almost-empty BSS-class data segment
  carrying a single 16-bit constant.

Provenance: both files came from ONE public release zip —
`XiaomiFirmwareUpdaterReleases/firmware_xiaomi_mayfly` release
`stable-29.07.2025` =
`fw_mayfly_mayfly-ota_full-OS2.0.202.0.VLTCNXM-user-15.0-2f4d12241d.zip`
(192,155,633 B, asset size matches the release API). Payloads stay in
`/tmp/astro_w/payloads/bc/`; only derived facts below.

Clean-room statement: `bigcluster_probe.py` (copied to this directory) is
written from public format documentation only — the AOSP sparse-image
format (`system/core/libsparse` semantics), the public FAT spec (BPB,
clusters, LFN), and the ext4 superblock magic. `mdt_probe.py` (from
`implementations/historic/fp2/`, GPL kernel sources — see its header) was
reused for the MDT containers. No proprietary payload bytes were used in
writing any parser.

## 1. Provenance and verification

| artifact | source | verification |
|---|---|---|
| `firmware-update/vm-bootsys.img` | mayfly (Mi 12S) HyperOS 2.0.202.0 China-stable firmware zip, XFU GitHub release asset | **md5 `db7c51a3ae0d3f096a7e4ebcf605c5a2` — MATCH with `sharing-clusters.csv` row (5 devices: diting; mayfly; mondrian; thor; unicorn)** |
| `firmware-update/modem.img` | same zip (294,195,200 B) | FAT16 filesystem, md5 `3a54ecbcc265cd62acede7eebc34e0ca` (not DB-pinned — the DB pins the extracted `image/` files) |
| `image/modem.b16` (extracted from modem.img's FAT) | same zip | **md5 `30c22653187904f76d4c591fbdb4ca7e` — MATCH with the 11-device row (cupid; diting; fuxi; marble; mayfly; mondrian; nuwa; socrates; thor; unicorn; zeus)** |

Secondary provenance: the LineageOS vendor tree
(`TheMuppets/proprietary_vendor_xiaomi_mayfly` @ `lineage-22.2`) pins the
same partition as `radio/vm-bootsys.img` via
`add-radio-file-sha1-checked,radio/vm-bootsys.img,ba20165c…`, and the
LFS pointer's declared size (269,996,032) equals the DB size; the device
trees (`LineageOS/android_device_xiaomi_{mayfly,diting,thor,unicorn}`'s
`proprietary-firmware.txt`) state the source OS ("mayfly
OS2.0.204.0.VLTCNXM", "diting OS2.0.203.0.VLFMIXM") — i.e. one partition
image shared across the whole SM8475 Xiaomi family (matches the 5-device
cluster being exactly the 5 SM8475-class devices in devices-half.csv).

Routes tried (RULE 0, 2026-11-18/19):

1. TheMuppets mega repo `proprietary_vendor_xiaomi` — **HTTP 451 DMCA
   block** (SenseTime 2019 notice); per-device forks
   (`proprietary_vendor_xiaomi_cupid/mayfly/diting`) are separate repos and
   listable, but their `radio/*.img` are **git-LFS pointer files whose
   backing objects 404 at `media.githubusercontent.com`** (all URL variants
   tried: `/media/<o>/<r>/<ref>/<path>`, `/refs/heads/<ref>`, raw redirect;
   contents API with raw Accept returns the 134-byte pointer). Recorded as
   a negative route — the LFS sha256 pin `d1a9864bb85d2448…` remains a
   useful cross-check anchor for future re-fetches.
2. SourceForge `xiaomi-firmware-updater` files API — dead (HTML shell /
   404s; the project's GitHub release org is the live successor).
3. GitHub release asset download succeeded via a **resumable retry loop**
   (the network path reset connections repeatedly; `curl -C -` resume, 5
   resumes over ~80 min) — route script `tools/dl_retry.sh` in scratch.

## 2. vm-bootsys.img — identification + per-byte-range findings

- Container: **raw (non-sparse) ext4**, superblock @1024, magic 0xEF53,
  block size 4096, 65,917 blocks (= 269,996,032 B exactly — the partition
  image is the full partition, not a sparse package), features
  `has_journal ext_attr resize_inode filetype extent sparse_super
  large_file uninit_bg`, state clean, UUID
  `57f8f4bc-abf4-655f-bf67-946fc0f9f25b` (the stock AOSP `make_ext4fs`
  default UUID — build-system fingerprint, not a per-device identity).
- Directory map (debugfs listing, read-only):

```
/                       (root)
  lost+found/           (std)
  trustedvm/            16-Apr-2021 00:24   ← the entire content
    system.img          224,997,376 B       ← the VM's root filesystem (ext4)
    boot/
      trustedvm.mdt     3,504 B             ← the VM kernel, Qualcomm split-ELF
      trustedvm.b00     244 B               ←   ehdr + phdr table (52+6·32=244)
      trustedvm.b01     12,814,848 B        ←   kernel image (starts "MZ…": ARM64 EFI-stub)
      trustedvm.b02     29,892 B
      trustedvm.b03     8,388,609 B         ←   initramfs (starts "07070100": cpio newc)
      trustedvm.b04     4,096 B
      trustedvm.b05     3,260 B             ←   hash segment (see below)
```

- **trustedvm.mdt parses cleanly with the lab's MDT parser** (0 errors, all
  6 segment files present with exact declared sizes): machine 40 (EM_ARM),
  entry 0xe0b00000, relocatable (QCOM_MDT_RELOCATABLE on every loadable),
  memory range 0xe0b00000–0xe8500000, Σ p_filesz 21,240,949 B. Structural
  delta vs the 8974-era images (`fp2/fleet-analysis.md` §2.1): the hash
  segment moved from phdr[1] to the **last** phdr (phdr[5], type 0,
  flags 0x02000000, 3,260 B), and the `.mdt == b00‖b01` duplication became
  `.mdt == b00‖b05` (mdt 3,504 = 244 + 3,260, byte-verified) — the
  "mdt = header-phdr ‖ hash-phdr" rule survives across 9 years and three
  SoC generations, only the hash position changed.
- `/trustedvm/system.img` (225 MiB): another raw ext4 rootfs — top-level
  `bin boot build.prop cache data dev etc home lib media mnt overlay
  persist proc run sbin sdcard sys target tmp usr var`; `build.prop` = 
  `genericarmv8`; `/sbin` = busybox symlink farm — a minimal Linux
  Embedded (Yocto/LE) guest, built 2021-04-16 (the image predates the
  SM8475 devices; Qualcomm's TVM BSP is carried forward per-generation).

### Identity (cited, secondary sources)

`vm-bootsys` is Qualcomm's **trusted VM boot/system partition** of the
hypervisor stack (Trusted-UI use cases; A/B slotted, companion partition
`vm-persist`): CSDN Qualcomm partition reference
(blog.csdn.net/qq_42867266/details/145612364) and Qualcomm developer-support
threads (mysupport.qualcomm.com — RB5 Gen 2 "vm-bootsys.img / vm-persist.img
LE-built secure VM images"; missing partitions → boot loops). A Linux-on-
Lenovo project independently documents repurposing the (FAT-formatted)
`vm-bootsys_a` on a 2024 device as its GRUB boot FAT
(xiaquwan1001/lenovo-legion-y700-gen4-tb322fc-elden-linux,
`uefi-boot-chain-vm-bootsys.md`) — on that device the partition is FAT32 on
the bootloader LUN; on the Xiaomi SM8450/8475 class it mounts as **ext4**
(`recovery.fstab` in salvogiangri/UN1CA platform/sm8450: 
`by-name/vm-bootsys /vm-bootsys ext4 default recoveryonly`) — which is what
the bytes show.

### What this means for the program

The single biggest "other" blob in the laptop half is **not a modem or
codec blob — it is an entire second OS** (Qualcomm's trusted-VM guest).
Free-software consequences: (a) its Linux guest is built from LE/Yocto
sources (the genericarmv8 BSP class) — a free rebuild is plausible in
principle; (b) the guest kernel is a normal MDT image — same container as
every other Qualcomm peripheral; (c) the opaque parts are the hypervisor
interface expectations (QSEE/VM loader signature checks on `trustedvm.b05`
etc.) [OPEN]. The 5-device md5 equality says the TVM image is unchanged
across the whole SM8475 Xiaomi family and (since the content timestamps are
2021) across HyperOS generations.

## 3. modem.b16 — identification + per-byte-range findings

The upstream DB path for this file is `xiaomi/<codename>/modem/image/` —
the extracted contents of the **modem partition**, which on SM8450+ is a
**FAT16 filesystem** (OEM `MSDOS5.0`, bytes/sector 4096, cluster 16 KiB,
root entries 512) containing an `image/` directory with the full split
images (`modem.mdt` + `modem.b00…b31`, `adsp.*`, `cardapp.*`,
per-chip dirs `waipio/` (SM8450/8475 SoC codename) + `qca6490/` (the
FastConnect 6490 BT/WLAN subsystem), and ServiceRegistry manifests
(`modemr.jsn`: `sr_domain soc=msm domain=modem subdomain=root_pd
qmi_instance_id=180`)). The DB's "modem/image/" path is literally this
FAT's `image/` directory extracted.

- The SM8475 (mayfly) `image/` holds **30 modem segment files** (b00–b31
  with gaps) + `modem.mdt` (5,884 B). The lab's MDT parser runs on it with
  **0 errors**: machine 164 (EM_QDSP6), entry 0x8bc00000, 32 phdrs, 30
  loadable + 1 hash (phdr[31] — hash-at-end like trustedvm), relocatable,
  range 0x8bc00000–0x9ee00000, Σ p_filesz 109,103,576 B (+211,007,728 B
  BSS). Build ID (factual metadata from b18):
  `QC_IMAGE_VERSION_STRING=MPSS.DE.2.0.c1-00381-WAIPIO_GEN_PACK-1.82267.44`.
- **b16 (the ×11 cluster blob): phdr[16] = PT_LOAD, flags 0x08000006
  (RELOCATABLE | RW), paddr 0x8cbcb000, filesz 473,648, memsz 475,136** —
  a 16 KB-aligned RW data segment. Its content: **473,646 zero bytes + one
  u16 = 0x124f (4,687) at offset 469,536** (entropy 0.000; 118,411 zero
  u32-words + 1 word `0x0000124f`). So the "modem.b16 shared by 11 devices
  across SM8450/SM8475/SM8550" is a BSS-with-one-constant segment — the
  md5 cluster is real but the payload is a single half-word. Which
  semantic the 0x124f carries (a feature mask, version counter, capacity
  constant) is [OPEN]; the fleet-level fact is that Qualcomm ships a
  near-empty data segment identically across three SoC generations.
- Note the name-collision trap: FP2's 8974-era `modem.b16` (139,264 B,
  `79bfd1d6…`) and hammerhead's (§fp2/§hammerhead docs) are different
  files that merely share the segment index; segment indexes have NO
  cross-generation meaning. The DB's modem.b16 row is the SM8450+ one.

## 4. Raw census (facts only)

`blob-matrix/laptop/big-clusters-census.csv` (new file) — the two clusters
with md5, size, device lists, identity, and fetch source. The SM8475 modem
split-image census (29 files + mdt, all md5-checked against declared phdr
sizes, plus the FAT16 directory map above) is in scratch
`/tmp/astro_w/payloads/bc/modem_image/` + `/tmp/astro_w/analysis/
mayfly_modem_mdt.json`; it is NOT committed (payload-adjacent detail; the
committed facts are in this file).

## 5. What remains open

- `trustedvm.b01` (12.8 MB kernel) and the 225 MiB LE rootfs: rebuildable
  in principle from LE/Yocto; nobody has published a free rebuild for the
  TVM guest [OPEN — a genuine implementation target: the VM image is
  Linux-based, unlike the DSP/MPSS blobs].
- The hypervisor-side loader expectations for `trustedvm.*` (signature
  checks, memory map) [OPEN].
- The meaning of modem.b16's u16 0x124f [OPEN].
- The DMCA-blocked TheMuppets LFS objects: the DB should record the
  `d1a9864bb85d2448…` sha256 pin for vm-bootsys.img (this session verified
  the md5 path via Xiaomi's official firmware instead).

## 6. Files created

- `analysis.md` (this file)
- `bigcluster_probe.py` — clean-room sparse/FAT/ext4 structural probe
  (validated on synthetic sparse+FAT fixtures in scratch)
- `big-clusters-census.csv` — raw census of both clusters

Scratch (regeneratable): `/tmp/astro_w/payloads/bc/` (firmware zip,
vm-bootsys.img, modem.img, extracted `modem_image/`, extracted
`vmboot/`), `/tmp/astro_w/analysis/*.json` (probe JSONs),
`/tmp/astro_w/tools/dl_retry.sh`. Payload bytes NOT committed per program
rules.
