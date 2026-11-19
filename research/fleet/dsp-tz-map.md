# dsp.img + tz.img container map — OnePlus 6 (enchilada), LineageOS 22.2 nightly 2026-11-11

Analysis date: 2026-11-17. Inputs: `data-fetch/enchilada/dsp.img` (33,554,432 B), `data-fetch/enchilada/tz.img` (2,056,192 B).
Machine-readable evidence: `analysis/out/dsp-elf-census.json`. Scripts: `analysis/tools/dsp_tz_census.py`, `analysis/tools/dsp_ext4_extract.py`, `analysis/tools/tz_strings_entropy.py`, `analysis/tools/build_dsp_tz_draft.py`. Extracted ext4 files: `/tmp/dsp-ext4/` (62 files).

## 1. dsp.img — container is ext4 (briefing correction)

Whole image: md5 `ecdfc6320f043fe089addfff880cdc22`, sha256 `ed96e09f54bbb2c363bd9e6c04f22f20259750f1ba245fc9a739ea70dd666019`.

`file` identifies dsp.img as **Linux rev 1.0 ext4 filesystem, volume name "dsp", extents, large files** — not a raw concatenation and not FAT.

| property | value |
|---|---|
| UUID | af32c008-2a39-7e5b-a5dc-201456d93103 |
| block size / count | 4096 B / 8192 blocks (exactly 32 MiB) |
| block groups | 1 (blocks-per-group 32768 > total) |
| inode table | blocks 11-138 |
| journal | inode 8, 4 MiB = blocks 139-1162, clean: only block 139 (journal superblock) nonzero |
| resize inode (7) | blocks 2-7 + 1163 |

**Briefing correction.** "First ~4.7 MB zero" is inaccurate:

- 14 nonzero 4K sectors exist below 0x48f000 (superblock @0x0, GDT @0x1000, bitmaps @0x9000/0xa000, inode table @0xb000-0x10000, journal superblock @0x8b000, resize inode @0x48b000, dir blocks @0x48c000-0x48f000).
- The ELFs start at 0x48f000 simply because ext4 places file data after metadata + journal; they are **files inside the filesystem**, not a raw stream.
- File data ends at 0x1cc7000; 0x1cc7000-0x2000000 (819 blocks, 3,355,648 B) is a zero tail.

Directory tree (62 files):

| dir | files | ELF | non-ELF |
|---|---|---|---|
| /adsp | 24 | 22 | 2 |
| /cdsp | 17 | 16 | 1 |
| /sdsp | 21 | 19 | 2 |
| /lost+found | 0 | 0 | 0 (empty; its block still holds stale dirent bytes) |

## 2. ELF census

`\x7fELF` magic hits: **60** total = **57 file-start ELFs** + **3 embedded**:

- 0x6fc6b1 — inside ELF payload of `adsp/fastrpc_shell_0` (md5 `b9ffea38e0f6787ee2f28337e6756c6d`); not validated as a standalone header
- 0x8e572c — inside ELF payload of `cdsp/fastrpc_shell_3` (md5 `2d7756f3c676a4bc178035fa8494302b`); not validated as a standalone header
- 0x12845e1 — inside ELF payload of `sdsp/fastrpc_shell_2` (md5 `053fca51499728c69d8479439134c724`); not validated as a standalone header

All 57 ELFs share one shape: ELF32 LE, `e_machine` 164 (EM_QDSP6, Hexagon), `e_type` 3 (ET_DYN), `e_phnum` 3 (2 PT_LOAD + 1 PT_DYNAMIC), `e_entry` 0x0 or 0x94, section headers present at file end (`e_shnum` 17-36; file size == e_shoff + e_shnum*40 on every blob). Per-blob headers, all program headers, spans and hashes are in `dsp-elf-census.json` (`blobs[]`).

Totals: 25,270,112 ELF bytes; largest file `sdsp/libFastRPC_UTF_Forward_800s_sdm845_skel.so` (6,821,248 B).

Full file table (all 62 files, ext4-extracted, size/md5 verified against directory entries):

| path | size | md5 |
|---|---|---|
| `adsp/AlacDecoderModule.so.1` | 25640 | `c1c293db0348fc89a6e4a283f42fedd3` |
| `adsp/ApeDecoderModule.so.1` | 46768 | `25759cbce95ed71f4e8995d0afab3907` |
| `adsp/AudioContextDetection.so.1` | 30824 | `ad99bf7a11f2cf8ee66879676df596b4` |
| `adsp/AudioSphereModule.so.1` | 75472 | `598b4849bb64c7d505e00fbdcfd0a4d5` |
| `adsp/CFCMModule.so.1` | 25640 | `cb954c499a3551468d1f73d39df6ccbf` |
| `adsp/EtsiAmrWbPlusDecModule.so.1` | 191800 | `36ec0a709f4335b933ae7022c48c1722` |
| `adsp/EtsiEaacPlusEncAndCmnModule.so.1` | 197232 | `b03fc9af1d21a975962ff025dd83f19d` |
| `adsp/FlacDecoderModule.so.1` | 36752 | `cfd9d8711a55916f1679f86ca73ee17e` |
| `adsp/HeaacDecoderModule.so.1` | 290192 | `e76bbf7cbd43894455009c6431e96476` |
| `adsp/LdacModule.so.1` | 61368 | `32d988eee180d52dbd7a006e3b85af66` |
| `adsp/SAPlusCmnModule.so.1` | 132080 | `922a948032a2569fc2add51454515030` |
| `adsp/SVACmnModule.so.1` | 81872 | `fd8b5aa584ed591768127342a7ce0ce3` |
| `adsp/VoiceWakeup_V2_Module.so.1` | 50984 | `8662e342cbea9efacc2972c056b105f7` |
| `adsp/VorbisDecoderModule.so.1` | 83544 | `c9a36b78ce68c9888bec34f3164e0420` |
| `adsp/WmaProDecoderModule.so.1` | 372088 | `6cdd9a82efd2e38e6db09b4bef94589a` |
| `adsp/WmaStdDecoderModule.so.1` | 124184 | `610f158b6f337e80423bb8e24f9cf700` |
| `adsp/fastrpc_shell_0` | 873128 | `b9ffea38e0f6787ee2f28337e6756c6d` |
| `adsp/fluence_voiceplus_module.so.1` | 149232 | `bf5cd466cafaf0b62553f648d2358532` |
| `adsp/libstabilitydomain_skel.so` | 75880 | `d7a859df1a508352f3cbebef346776b5` |
| `adsp/libsysmon_skel.so` | 127952 | `96b66cf6f34d8ac9f51e525958c13ad1` |
| `adsp/libsysmondomain_skel.so` | 176688 | `60944282ab9105f6087063e5f4fccd84` |
| `adsp/map_AVS_SHARED_LIBS_845.adsp.prodQ.txt` | 1667 | `473190560bcc8cb5de518621b905a672` |
| `adsp/map_SHARED_LIBS_845.adsp.prodQ.txt` | 332 | `8bae239fcb81ad63f9962e38dba94477` |
| `adsp/mmecns_module.so.1` | 568760 | `9b36a05ed7864e88c1bc59e9fa19510a` |
| `cdsp/fastrpc_shell_3` | 878584 | `2d7756f3c676a4bc178035fa8494302b` |
| `cdsp/libbenchmark_skel.so` | 253416 | `4d6e953a92538e70c8c24c1e12438830` |
| `cdsp/libc++.so.1` | 3043928 | `a2be8f180755a51d362ea8ad8a1eb14e` |
| `cdsp/libc++abi.so.1` | 1385368 | `5a060c997ce78583cecd1ede7bfc0fdd` |
| `cdsp/libhcp_rpc_skel.so` | 134136 | `33704559eecfead04fb504acd5e4bc38` |
| `cdsp/libstabilitydomain_skel.so` | 76104 | `277025a86827a51a7a223700e6e93b4f` |
| `cdsp/libsysmon_skel.so` | 187792 | `a7ba843aacb75c6165b71510541b9a53` |
| `cdsp/libsysmondomain_skel.so` | 236656 | `44ee786e28c76e42c18965dad206f91e` |
| `cdsp/libvpp_aie.so` | 106624 | `d2c8db283bbd5fa15bcc06a0fdd6a2ec` |
| `cdsp/libvpp_diagtools.so` | 478176 | `65f9c50c4e5678d5dde12488dcf57ddd` |
| `cdsp/libvpp_frc.so` | 922888 | `262af4f81b849816e3f04cf01c9c68b5` |
| `cdsp/libvpp_mvp.so` | 7560 | `5190a3321b5c967d9416ed9947c4364d` |
| `cdsp/libvpp_nr.so` | 7560 | `27e81cc1ee9ca34813c4bd6889545b24` |
| `cdsp/libvpp_qbr.so` | 7560 | `f3e3ac668735b5491bddceb4c031825a` |
| `cdsp/libvpp_svc_skel.so` | 233136 | `eb0780945ec43f0c81f16251c4cb9c26` |
| `cdsp/map_SHARED_LIBS_845.cdsp.prodQ.txt` | 1314 | `5a49b39d584ed4789b75d67945399098` |
| `cdsp/ubwcdma_dynlib.so` | 114496 | `28e92568e48dcb804ac5517708a03cb7` |
| `sdsp/cellinfo_tools.so` | 16968 | `cc5168d44a9f9949ab30d79cd943bb42` |
| `sdsp/chre_app_coverage.so` | 21656 | `b94dec41eb67e33d7101031f0982959c` |
| `sdsp/chre_app_coverage2.so` | 21600 | `942e3bee65d0f3ba12bb2c78a6dd3e9e` |
| `sdsp/chre_app_oem.so` | 20480 | `9eb9beaa9af1ccdd653afce74504fcc0` |
| `sdsp/chre_app_sensor_cfg.so` | 27568 | `e59e978a67bc2d365478fb83ad2e7721` |
| `sdsp/chre_drv_bt.so` | 113344 | `ddb825852708d534f324c3e414dc410d` |
| `sdsp/chre_drv_gf.so` | 800856 | `1c7bb3ff468acd57696f54d398b38215` |
| `sdsp/chre_drv_loc.so` | 544760 | `961a3eba1e32bad90408ba2b56b1e0ef` |
| `sdsp/chre_drv_modem.so` | 229312 | `30829a824a4f2eebfc42bebe534a9d61` |
| `sdsp/chre_drv_wifi.so` | 175424 | `c36c7fec0440e9281b19f050f8f9436e` |
| `sdsp/chre_pal.so` | 9352 | `1639cf74c49ea35d76426df846592f07` |
| `sdsp/fastrpc_shell_2` | 857208 | `053fca51499728c69d8479439134c724` |
| `sdsp/libFastRPC_UTF_Forward_800s_sdm845_skel.so` | 6821248 | `76b67d85d026accdeb6aa6f784564a27` |
| `sdsp/libchre_slpi_skel.so` | 2932720 | `b4e5acef94d229816ac115ab29c76d5e` |
| `sdsp/libstabilitydomain_skel.so` | 74984 | `04dfe735f860c70a8d604f6399526764` |
| `sdsp/libsysmon_skel.so` | 127088 | `4a45f1c496132df78e2fc3ec46e21134` |
| `sdsp/libsysmondomain_skel.so` | 175824 | `ceae2e21ee8deb49cd3a6d92bf472016` |
| `sdsp/lowi_client.so` | 401136 | `f2e831f086d508680fdcd3a1d3fb0e8c` |
| `sdsp/map_SHARED_LIBS_AAAAAAAAQ.txt` | 1477 | `cb83d908ba0327514293ad95d4dd779e` |
| `sdsp/map_SSC_SLPI_USER_AAAAAAAAQ.txt` | 0 | `d41d8cd98f00b204e9800998ecf8427e` |
| `sdsp/sensor_testapp_40.so` | 26520 | `e0601ce0abfba64f1550bdb0b8d1b90d` |

## 3. Identity vs modem FAT `IMAGE_ADSP.*`

FAT source: `/tmp/modem-fat/` (extracted from modem.img in a prior session). FAT 8.3 naming makes the names uppercase `IMAGE_ADSP.*` — the same set referenced as `IMAGE_image_adsp.*`. `IMAGE_ADSP.MDT` = ELF32 ET_EXEC, EM_QDSP6, e_entry 0x8c400000, 15 phdrs (phdr0 = header segment 532 B = ehdr+phdrs; phdr1 = 6920 B hash segment = B01; B02..B13 = phdr2..13 contents).

Identity results — **honest negative at all three levels**:

1. Whole-file md5: **0 / 17** FAT files match any dsp.img ext4 file.
2. Raw containment: **0** exact byte-occurrences of any FAT file anywhere in the raw dsp.img.
3. Segment level: **0** matches between any `IMAGE_ADSP.Bxx` content and any of the 57 dsp ELFs' program-header content slices (md5).

Interpretation: the two artifacts are disjoint by design. The modem FAT `IMAGE_ADSP.*` split-bin is the boot-time PIL image; the dsp.img ext4 holds **fastrpc user-PD process binaries** (audio/cdsp/sensor modules, fastrpc shells, libc++), loaded at runtime through fastrpc, never through PIL. The identity check therefore confirms the lab's family split rather than exposing missing data.

FAT file table (for the record):

| FAT file | size | md5 |
|---|---|---|
| `IMAGE_ADSP.B00` | 532 | `d0ad580c79ec9e68e9eb3a7b34f15549` |
| `IMAGE_ADSP.B01` | 6920 | `9fe60f6300d43b2359284f3fcb9d47b1` |
| `IMAGE_ADSP.B02` | 8408 | `64822a245699c36e71987ac97d2bcc6e` |
| `IMAGE_ADSP.B03` | 120932 | `87e9dc26a6487b2b1cda79916e266e0d` |
| `IMAGE_ADSP.B04` | 1849248 | `2abaa227d7616b43b4bdc77a85db8834` |
| `IMAGE_ADSP.B05` | 1144444 | `185f923d03af95fb1942c20324926a78` |
| `IMAGE_ADSP.B06` | 2880 | `f46bbeb791df6606df8318965a116595` |
| `IMAGE_ADSP.B07` | 34096 | `e10d0c694831d34eb7b6d7b45dbfe72c` |
| `IMAGE_ADSP.B08` | 313984 | `285ac7f5b013f9a8c3d3077ff741e04d` |
| `IMAGE_ADSP.B09` | 84 | `17d3146bae7eb08e8106f265fd8ff967` |
| `IMAGE_ADSP.B10` | 7131580 | `10579c86ecf6b903365aceaf622e4469` |
| `IMAGE_ADSP.B11` | 314312 | `2b9e45694e1b6514b2ec58b691779f26` |
| `IMAGE_ADSP.B12` | 2896 | `6f15783ee39d49bcca3c48e72a310569` |
| `IMAGE_ADSP.B13` | 167848 | `c5dbc34085ec4777ad032b1dd45fb3a9` |
| `IMAGE_ADSP.MDT` | 7452 | `45d56da07aaa11bbaf4eb0b535977253` |
| `IMAGE_ADSPR.JSN` | 403 | `40d6edf129dec063ca3fe6cb6837488f` |
| `IMAGE_ADSPUA.JSN` | 555 | `d0bd5030a03f631c9af5060a5645d02e` |

## 4. Non-ELF nonzero 4K-sector regions

6,150 of 8,192 sectors are nonzero. Outside ELF file data, 9 runs remain, all accounted for:

| range | bytes | classification |
|---|---|---|
| 0x0 - 0x2000 | 8192 | group_desc, primary_superblock |
| 0x9000 - 0x10000 | 28672 | block_bitmap, inode_bitmap, inode_table |
| 0x8b000 - 0x8c000 | 4096 | journal |
| 0x48b000 - 0x48f000 | 16384 | dir_block(/), dir_block(/adsp), dir_block(/lost+found), resize_inode |
| 0x7ae000 - 0x7b0000 | 8192 | non_elf_file:adsp/map_AVS_SHARED_LIBS_845.adsp.prodQ.txt, non_elf_file:adsp/map_SHARED_LIBS_845.adsp.prodQ.txt |
| 0x83b000 - 0x83c000 | 4096 | dir_block(/cdsp) |
| 0xfd9000 - 0xfda000 | 4096 | non_elf_file:cdsp/map_SHARED_LIBS_845.cdsp.prodQ.txt |
| 0xff6000 - 0xff7000 | 4096 | dir_block(/sdsp) |
| 0x1cbf000 - 0x1cc0000 | 4096 | non_elf_file:sdsp/map_SHARED_LIBS_AAAAAAAAQ.txt |

No unexplained non-ELF data. (Dir blocks sit adjacent to each directory's first file: /adsp @0x48e000 -> AlacDecoderModule @0x48f000, /cdsp @0x83b000 -> fastrpc_shell_3 @0x83c000, /sdsp @0xff6000 -> cellinfo_tools @0xff7000.)

## 5. tz.img — QSEE ELF64 segment map

Whole image: md5 `785583b96d12cb39cb3e64363863000e`, sha256 `2d133bdafc70122ff18c12766c855c8f8490c825bf91e1da95c6535d1d16baca`.

ELF64 LSB **ET_EXEC**, `e_machine` 183 (AArch64), `e_entry` 0x14680000, phoff 64, phentsize 56, phnum 17, no section headers (e_shoff 0). `e_entry` equals seg[3] `p_vaddr` exactly.

Per-segment sha256 is in `dsp-elf-census.json` (`tz.segments[]`); the table below adds entropy and role:

| # | type | flags | role | offset | vaddr | filesz | memsz | nonzero B | entropy B/byte |
|---|---|---|---|---|---|---|---|---|---|
| 0 | PT_NULL | - | ?? | 0x0 | 0x0 | 1016 | 0 | 231 | 1.892 |
| 1 | PT_NULL | - | ?? | 0x1000 | 0x1c1e8000 | 19992 | 20480 | 19815 | 4.022 |
| 2 | PT_LOAD | - | ?? | 0x6000 | 0x0 | 0 | 0 | 0 | 0.000 |
| 3 | PT_LOAD | RX | RX | 0x6000 | 0x14680000 | 36160 | 36160 | 26542 | 5.969 |
| 4 | PT_LOAD | RW | RW | 0xf000 | 0x14689000 | 15624 | 15624 | 72 | 0.058 |
| 5 | PT_LOAD | RWX | RW | 0x13000 | 0x1468e000 | 4040 | 4040 | 2279 | 4.483 |
| 6 | PT_LOAD | RW | RW | 0x14000 | 0x1468f000 | 11376 | 11376 | 5 | 0.007 |
| 7 | PT_LOAD | RX | RX | 0x17000 | 0x1c000000 | 2432 | 2432 | 1980 | 5.766 |
| 8 | PT_LOAD | RW | RW | 0x18000 | 0x1c001000 | 28880 | 28880 | 4 | 0.002 |
| 9 | PT_LOAD | RW | RW | 0x20000 | 0x1c009000 | 45056 | 45056 | 11111 | 1.898 |
| 10 | PT_LOAD | RX | RX | 0x2b000 | 0x1c017000 | 782192 | 782192 | 688801 | 6.640 |
| 11 | PT_LOAD | RW | RW | 0xea000 | 0x1c0d6000 | 132680 | 132680 | 86212 | 5.594 |
| 12 | PT_LOAD | RW | RW | 0x10b000 | 0x1c0f7000 | 713552 | 713552 | 68466 | 0.921 |
| 13 | PT_LOAD | RW | RW | 0x1ba000 | 0x1c1aa000 | 114688 | 114688 | 0 | -0.000 |
| 14 | PT_LOAD | RW | RW | 0x1d6000 | 0x1c1c6000 | 65536 | 65536 | 25451 | 2.449 |
| 15 | PT_LOAD | RW | RW | 0x1e6000 | 0x1c1d6000 | 65536 | 65536 | 23767 | 2.176 |
| 16 | PT_LOAD | RW | RW | 0x1f6000 | 0x1c1e6000 | 0 | 8192 | 0 | 0.000 |

Structure notes:

- Two virtual regions: **0x14680000** (segs 3-6: entry/RX code + RW data — QSEE root region) and **0x1c000000-0x1c1e8000** (segs 7-16 + metadata seg 1: main TZ image).
- seg[0] PT_NULL filesz 1016 = exactly ELF header + 17 phdrs (64 + 17x56); seg[1] PT_NULL filesz 19992 at vaddr 0x1c1e8000 = QSEE metadata (hash table + signing certificates).
- seg[2] and seg[16] are empty placeholders (seg[16] is pure BSS: filesz 0, memsz 8192); segs 4, 6, 8, 13 are file-backed but essentially zero-filled (BSS-like).
- seg[5] is the only RWX segment (4,040 B).

### Strings

Briefing targets, honest negatives first:

- First 4 KB: **0 strings** — bytes 0-1016 are ELF header + phdrs, 1016-4096 is zero padding.
- First RO PT_LOAD (seg[3], RX @0x14680000, 36,160 B): **8 hits, all binary noise** (e.g. `6,x16,x16,...` immediates), no version/build strings.

The version/build strings live elsewhere:

- **seg[12] RW @0x1c0f7000** carries the image identity: at file offsets 0x112024/0x112053/0x112072 — `QC_IMAGE_VERSION_STRING=TZ.XF.5.0.1.C5-00083.1`, `IMAGE_VARIANT_STRING=WAXAANAAA`, `OEM_IMAGE_VERSION_STRING=CRM` (plus crypto strings `KS key derivation for aes [xts]`, `ssdksimg`).
- **seg[11] RW @0x1c0d6000** (1,513 strings) = target-config symbol table (`DalEnv`, `TargetCfg`, `qupv3_*`, `TZ_CE_POLICY_MAP`, `tcsr_base`, `NOCError_Propdata`, `bam_tgt_config`, ...).
- **seg[1]** (87 strings) = embedded X.509 chain: `QSEE Attestation Root CA` / `QSEE Attestation Root SubCA 1` (Qualcomm Cryptographic Operations; validity 190801-210801, 160304000001Z-260304000001Z, 151002000001Z-451001235959Z), `QCT Root CA 1` marked `General Use Test Key (for testing 13 only)`, extension text `OEM_ID_INDEPENDENT`, `USE_SERIAL_NUMBER_IN_SIGNING`, `IN_USE_SOC_HW_VERSION`, `SHA256`, `MODEL_ID`, `SW_SIZE`, `OEM_ID`, `DEBUG`, `HW_ID`, `SW_ID`, `San Diego`, `CASS - CSMS 2.00`.

Whole-image scan (all 2,056,192 B): 1,851 ASCII runs >=6 chars + 5 UTF-16LE runs; the UTF-16 hits are binary noise. seg[10] (main RX, 782,192 B, entropy 6.640) yields only noise hits — no plaintext strings in the main binary.

## 6. Open items

- Validate the 3 embedded ELF magic offsets inside the fastrpc shells (0x6fc6b1 / 0x8e572c / 0x12845e1) — likely appended/inner images, not yet parsed.
- Decode seg[1] QSEE metadata layout (hash-table geometry vs phdr indices) and cert chain order.
- seg[10] entropy 6.640 with no strings: determine compressed-vs-dense-code (affects any future symbol recovery).
- Cross-link: check whether the same adsp/cdsp/sdsp modules exist in vendor.img (`/vendor/lib/rfsa/adsp` etc.) and extend the fleet md5 matrix with the 57 ELFs.
- lost+found block (0x48d000) holds stale dirent bytes — recoverable names not investigated (structural fact only).

## 7. Honest negatives

- No `IMAGE_ADSP.*` identity match at whole-file, raw-containment, or segment-content level (0/17, 0, 0).
- No version strings in the briefing-specified tz regions (first 4 KB, first RO PT_LOAD).
- No unexplained nonzero region in dsp.img; every non-ELF nonzero run is ext4 metadata, dir blocks, journal, resize inode, or a non-ELF map .txt file.
- `sdsp/map_SSC_SLPI_USER_AAAAAAAAQ.txt` is a genuine 0-byte file.
- tz.img carries no section headers; dsp ELFs do (17-36 sections each).
