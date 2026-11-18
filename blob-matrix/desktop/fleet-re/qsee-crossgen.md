# QSEE cross-generation analysis: tz.img (SDM845 vs SM8250), fastrpc embedded-ELF validation, a660 GMU table

Workorder: WORKORDER-001 (desktop fleet RE). Analysis date: 2026-11-18.
Prior evidence: `blob-matrix/desktop/fleet-re/dsp-tz-map.md` (OP6 tz.img seg table, dsp.img census).
Machine-readable evidence: `analysis/out/qsee-crossgen.json` (+ `qsee-map-enchilada.json`, `qsee-map-instantnoodle.json`, `qsee-meta-enchilada.json`, `qsee-meta-instantnoodle.json`, `qsee-meta-regions-*.json`, `fastrpc-embedded-elf.json`).
Scripts: `analysis/tools/qsee_tz_map.py`, `qsee_metadata_decode.py`, `qsee_meta_probe.py`, `fastrpc_embedded_check.py`, `gmu_block_parse.py`, `qsee_crossgen_build.py`.

Evidence classes: **F** = measured fact, **I** = interpretation, **H** = hypothesis, **N** = negative.

Inputs (sha256, F):

| file | size | sha256 |
|---|---|---|
| `data-fetch/enchilada/tz.img` (OnePlus 6, SDM845) | 2,056,192 | `2d133bda...d16baca` |
| `data-fetch/second-device/instantnoodle/tz.img` (OnePlus 8, SM8250) | 3,194,880 | `c75d2bd2...7018603` |
| `data-fetch/enchilada/dsp.img` | 33,554,432 | `ed96e09f...dd666019` |
| `data-fetch/second-device/larry/tree-vendor/firmware/a660_gmu.bin` | 55,256 | `6bb9360a...40c94e2b` |

Both tz.img are from official LineageOS nightlies (enchilada 2026-11-11; instantnoodle `lineage-24.0-20261117-nightly-instantnoodle-signed.zip`).

## 1. instantnoodle tz.img — full ELF map (F)

ELF64 LSB **ET_EXEC**, `e_machine` 183 (AArch64), `e_entry` **0x14680000** (identical to OP6), phoff 64, phentsize 56, **phnum 23**, no section headers (e_shoff 0). `e_entry` == seg[3].p_vaddr.

seg[0] PT_NULL filesz 1,352 = exactly 64 + 23x56 (ehdr + phdrs, same pattern as OP6's 1,016 = 64 + 17x56).

| # | type | flags | offset | vaddr | filesz | memsz | nonzero B | entropy |
|---|---|---|---|---|---|---|---|---|
| 0 | PT_NULL | --- | 0x0 | 0x0 | 1352 | 0 | 326 | 2.056 |
| 1 | PT_NULL | --- | 0x1000 | 0x1c3d6000 | 20800 | 24576 | 20385 | 3.961 |
| 2 | PT_LOAD | --- | 0x7000 | 0x0 | 0 | 0 | 0 | 0.000 |
| 3 | PT_LOAD | RWX | 0x7000 | 0x14680000 | 51380 | 51380 | 37198 | 5.871 |
| 4 | PT_LOAD | RW- | 0x14000 | 0x1468d000 | 8836 | 8836 | 131 | 0.171 |
| 5 | PT_LOAD | RWX | 0x17000 | 0x14690000 | 6088 | 6088 | 3510 | 4.690 |
| 6 | PT_LOAD | RW- | 0x19000 | 0x14692000 | 6552 | 6552 | 5 | 0.011 |
| 7 | PT_LOAD | R-X | 0x1b000 | 0x1c018000 | 39936 | 39936 | 31577 | 6.244 |
| 8 | PT_LOAD | RW- | 0x25000 | 0x1c022000 | 51584 | 51584 | 1172 | 0.284 |
| 9 | PT_LOAD | RW- | 0x32000 | 0x1c02f000 | 41088 | 41088 | 10686 | 2.022 |
| 10 | PT_LOAD | RWX | 0x3d000 | 0x1c03b000 | 915988 | 915988 | 812790 | 6.612 |
| 11 | PT_LOAD | R-- | 0x11d000 | 0x1c11b000 | 215760 | 215760 | 79646 | 3.565 |
| 12 | PT_LOAD | RW- | 0x152000 | 0x1c150000 | 721664 | 721664 | 78119 | 0.962 |
| 13 | PT_LOAD | RW- | 0x203000 | 0x1c281000 | 74296 | 380928 | 30648 | 3.265 |
| 14 | PT_LOAD | RW- | 0x216000 | 0x1c2de000 | 65536 | 65536 | 27554 | 2.817 |
| 15 | PT_LOAD | R-- | 0x226000 | 0x1c2ee000 | 65536 | 65536 | 20824 | 2.184 |
| 16 | PT_LOAD | R-- | 0x236000 | 0x1c300000 | 197 | 197 | 170 | 5.400 |
| 17 | PT_LOAD | R-X | 0x237000 | 0x1c301000 | 347220 | 347220 | 320932 | 7.133 |
| 18 | PT_LOAD | RW- | 0x28c000 | 0x1c356000 | 2968 | 2968 | 1200 | 3.410 |
| 19 | PT_LOAD | RW- | 0x28d000 | 0x1c357000 | 23744 | 23744 | 15022 | 4.776 |
| 20 | PT_LOAD | R-X | 0x293000 | 0x1c35d000 | 447232 | 447232 | 399347 | 6.854 |
| 21 | PT_LOAD | RW- | 0x301000 | 0x1c3cb000 | 5136 | 5136 | 1220 | 2.216 |
| 22 | PT_LOAD | RW- | 0x303000 | 0x1c3cd000 | 32832 | 32832 | 16368 | 4.080 |

Two-region structure (F): same shape as OP6 — **0x14680000** (segs 3-6, entry region) + **0x1c018000-0x1c3d6000** (segs 7-22 + metadata seg[1] at the end, vaddr 0x1c3d6000).

seg[1] = QSEE metadata segment: PT_NULL, filesz 20,800 B at file offset 0x1000, memsz 24,576.

Version strings (F), located in seg[12] (RW @0x1c150000, same segment role as OP6):

- file offset 1,471,832: `QC_IMAGE_VERSION_STRING=TZ.XF.5.8-00274`
- file offset 1,471,872: `IMAGE_VARIANT_STRING=DARAANAAA`
- file offset 1,471,903: `OEM_IMAGE_VERSION_STRING=CRM`

**SM8250 TZ version triple: TZ.XF.5.8-00274 / DARAANAAA / CRM** (vs SDM845: TZ.XF.5.0.1.C5-00083.1 / WAXAANAAA / CRM).

## 2. Cross-generation QSEE container table (F unless noted)

| property | OP6 enchilada (SDM845) | OP8 instantnoodle (SM8250) | shared? |
|---|---|---|---|
| e_type / e_machine | ET_EXEC / AArch64 | ET_EXEC / AArch64 | shared |
| e_entry | 0x14680000 | 0x14680000 | **shared (identical)** |
| phnum | 17 | 23 | gen-specific |
| seg[0] (ehdr+phdrs, PT_NULL) | 1,016 B | 1,352 B | shared pattern (64 + phnum*56) |
| seg[1] metadata (PT_NULL) | 19,992 B filesz / 20,480 memsz @0x1c1e8000 | 20,800 B filesz / 24,576 memsz @0x1c3d6000 | shared pattern |
| vaddr regions | 0x14680000 + 0x1c000000-0x1c1e8000 | 0x14680000 + 0x1c018000-0x1c3d6000 | shared layout, different extents |
| entry-region segs | 3-6 (RX,RW,RWX,RW) | 3-6 (RWX,RW,RWX,RW) | shared |
| R-- (PF_R only) segments | none | segs 11, 15, 16, 17 | gen-specific |
| RWX segments | seg 5 only | segs 3, 5, 10 | gen-specific |
| real BSS (memsz > filesz) | seg 16 (0/8,192) only | seg 13 (74,296/380,928) | gen-specific |
| version strings segment | seg[12] RW | seg[12] RW | shared |
| version triple | TZ.XF.5.0.1.C5-00083.1 / WAXAANAAA / CRM | TZ.XF.5.8-00274 / DARAANAAA / CRM | gen-specific |
| metadata hash algo | SHA-256 (32-byte slots) | **SHA-384 (48-byte slots)** | gen-specific |
| hash slots | 17 = phnum | 23 = phnum | shared pattern |
| metadata header size | 40 B | 288 B | gen-specific |
| secboot sig blocks | 2 x 256 B RSA-2048 | 2 x 256 B RSA-2048 | shared |
| cert chains | 2 groups x 3 certs | 2 groups x 3 certs | shared pattern |
| production root CA | QSEE Attestation Root CA (self-signed, valid 2015-10-02 to 2045-10-01) | **QSEE Attestation Root CA 2** (self-signed, valid 2017-06-09 to 2047-06-08) | gen-specific |
| production leaf CN | CASS - CSMS 2.0 | CASS - SBL3 | gen-specific |
| test root CA | QCT Root CA 1, OU "General Use Test Key (for testing 13 only)", O=QUALCOMM | QCT Root CA 1, OU "General Use Key", **O=OEM** | gen-specific (OEM-owned test root on SM8250) |
| test leaf | SecTools Test User | SecTools Test User | shared |

Interpretation (I): the container format is stable across the two generations; the metadata internal hash width upgraded SHA-256 -> SHA-384 between SDM845 and SM8250, and SM8250 adds read-only data segments plus an extended 288-byte metadata header.

## 3. QSEE metadata segment layout — decoded (F; first public per our knowledge)

Both images' seg[1] decode to the same 8-part structure (offsets are metadata-relative):

```
[header][hash table][SIG_A 256 B][chainA: 3 X.509 certs][0xFF pad][SIG_B 256 B][chainB: 3 X.509 certs][0xFF pad]
```

### 3.1 Header (F)

OP6 (40 B = 10 u32le words): `[25, 5, 256, 6144, 19744, 544, 0xFFFFFFFF, 256, 0xFFFFFFFF, 12288]`
SM8250 (288 B = 72 u32le words): words 0-11 = `[0, 6, 256, 6144, 20304, 1104, 0xFFFFFFFF, 256, 0xFFFFFFFF, 12288, 120, 120]`, word 14-20 = `[7, 0, 1, 0, 0, 10, 24584]`, word 44-50 = `[7, 0, 1, 0, 0, 266, 24584]`, all other words zero.

Validated field roles (F, both gens): word[2] = word[7] = 256 = signature block size; word[5] = hash table byte length (544 = 17x32 on OP6; 1,104 = 23x48 on SM8250 — exact); word[4] = word[5] + 19,200 (exact in both). Word[3]=6,144 and word[9]=12,288 are constants across gens (role unknown, H: per-chain size caps). Word[0]/word[1] differ per gen (25/5 vs 0/6, H: secboot metadata version pair). SM8250-only words 10/11 = 120/120 and the two `[7,0,1,0,0,X,24584]` descriptors are unassigned-role facts; 24,584 = memsz (24,576) + 8.

### 3.2 Hash table — per-phdr SHA slots, fully mapped (F)

- OP6: table at metadata offset **40**, 17 slots x 32 B, slot[i] = SHA-256 of phdr[i] file content (`data[p_offset : p_offset + p_filesz]`). Hits measured for phdr 0 and phdrs 3-15 at offsets 40 + 32i. Slots 1 (metadata segment itself), 2 (filesz 0/memsz 0) and 16 (filesz 0, memsz 8,192) are **all-zero**. Hit offsets: 40, 136, 168, ..., 520 (stride 32).
- SM8250: table at metadata offset **288**, 23 slots x 48 B, slot[i] = **SHA-384** of phdr[i] file content. Hits measured for phdr 0 and phdrs 3-22 (21 of 23 slots) at offsets 288 + 48i. Slots 1 (self) and 2 (filesz 0/memsz 0) all-zero.

Slot count == phdr count in both generations; segments with filesz 0 are stored as zero slots rather than hash-of-zeros (F). sha256/sha384 of the empty string do not appear anywhere in the metadata (N for those variants).

This is a **first public decode of the QSEE metadata hash-slot mapping**: the table is a per-program-header digest array indexed by phdr index, digest width = 32 B (SHA-256, SDM845) or 48 B (SHA-384, SM8250), byte length recorded in metadata header word[5].

### 3.3 Signature blocks (F for geometry and key binding, I for full-coverage claim)

Exactly two 256-byte high-entropy blocks per image, each sitting **immediately before** a cert chain:

- OP6: SIG_A @584 (entropy 7.071) before chainA; SIG_B @6984 (255 non-0xFF bytes + 1 embedded 0xFF byte) before chainB; rest of the two sig regions is 0xFF padding (regions 4,378-7,240 and 10,850-19,992 are 0xFF except the sig bytes; trailing 9,142 B of the segment are pure 0xFF).
- SM8250: SIG_A @1392, SIG_B @7792; trailing 9,531 B pure 0xFF.

RSA structural check (F): RSA public keys extracted from the leaf certs (2048-bit, e=65537). Decrypting each 256-B block (s^65537 mod n) yields an encoded message whose **last byte is 0xBC** in all four sig/leaf pairings — the RSASSA-PSS encoded-message terminator:

| image | sig | verified against | EM tail | PSS shape |
|---|---|---|---|---|
| OP6 | @584 | leaf@840 (CASS - CSMS 2.0) | 0xBC | yes |
| OP6 | @6984 | leaf@7240 (SecTools Test User) | 0xBC | yes |
| OP8 | @1392 | leaf@1648 (CASS - SBL3) | 0xBC | yes |
| OP8 | @7792 | leaf@8048 (SecTools Test User) | 0xBC | yes |

Cross-key controls (wrong leaf key): EM tails 0xE0/0x06/0xB5/0x2E — no 0xBC (F, 4/4 negative controls). So each 256-B block is an RSA-2048 signature bound to the paired chain's leaf key; PSS parameters/salt prevent recovering the signed message bytes, so which exact byte range is signed is (I), not proven. Interpretation: SIG_A = metadata (header+hash table) signature for the production chain, SIG_B = same for the test chain.

### 3.4 X.509 chains (F; DER facts)

All six DER units per image parse as complete X.509 certificates (SEQUENCE of tbs+sigalg+sig); all use sigalg OID 2a864886f70d01010a (RSASSA-PSS) and 2,048-bit RSA keys (SPKI keybits 2,168 = DER bit-string overhead included).

OP6 chainA (production): leaf@840 (1,387 B, valid 190801141737Z-210801141737Z, subject CN "CASS - CSMS 2.0", carries QSEE policy OUs `15 0001 OEM_ID_INDEPENDENT`, `14 0000 USE_SERIAL_NUMBER_IN_SIGNING`, `13 0001 IN_USE_SOC_HW_VERSION`, `07 0001 SHA256`, `06 0000 MODEL_ID`, `05 00000020 SW_SIZE`, `04 0001 OEM_ID`, `03 ... DEBUG`, `02 6000000000010000 HW_ID`, `01 ... SW_ID`) <- SubCA@2227 (1,096 B, 160304000001Z-260304000001Z, CN "QSEE Attestation Root SubCA 1") <- root@3323 (1,055 B, 151002000001Z-451001235959Z, self-signed "QSEE Attestation Root CA").

OP6 chainB (test): leaf@7240 (1,320 B, 211125155112Z-411120155112Z, "SecTools Test User" with the same OU policy set, SW_SIZE `05 00000248`) <- intermediate@8560 (1,137 B, 171222100313Z-371217100313Z, "QUALCOMM Attestation CA") <- root@9697 (1,153 B, 171222100111Z-371217100111Z, self-signed "QCT Root CA 1", OU "General Use Test Key (for testing 13 only)").

SM8250 chainA (production): leaf@1648 (1,059 B, 211102185026Z-231102185026Z, subject CN "CASS - SBL3", O=QUALCOMM, no policy OUs in subject) <- SubCA@2707 (1,104 B, 170609000001Z-270608235959Z, "QSEE Attestation Root CA 2 SubCA 1") <- root@3811 (1,060 B, 170609000001Z-470608235959Z, self-signed "QSEE Attestation Root CA 2").

SM8250 chainB (test): leaf@8048 (1,037 B, 240611135825Z-440606135825Z, "SecTools Test User", no policy OUs) <- intermediate@9085 (1,095 B, 191024151003Z-391019151003Z, "OEM Attestation CA", O=OEM) <- root@10180 (1,089 B, 191024150934Z-391019150934Z, self-signed "QCT Root CA 1", OU "General Use Key", **O=OEM** — an OEM-owned test root, vs Qualcomm's own test root on SDM845).

Issuer/subject CN matching forms a consistent leaf<-intermediate<-root ordering in all four chains (F). SHA-256 of each cert DER does not occur elsewhere in the metadata (N, checked).

## 4. fastrpc embedded ELF magics — verdict: false positive (N)

Re-extracted `/tmp/dsp-ext4x` from `data-fetch/enchilada/dsp.img` via `debugfs -R 'rdump / /tmp/dsp-ext4x'` (md5s of all three shells match the prior census). Each shell contains exactly one extra `\x7fELF` beyond offset 0:

| shell | size | magic at file offset | dsp.img abs offset | implied data start (4K-aligned) |
|---|---|---|---|---|
| adsp/fastrpc_shell_0 | 873,128 | 689,841 (0xa86b1) | 0x6fc6b1 | 0x654000 |
| cdsp/fastrpc_shell_3 | 878,584 | 694,060 | 0x8e572c | 0x83c000 |
| sdsp/fastrpc_shell_2 | 857,208 | 677,345 | 0x12845e1 | 0x11df000 |

Byte check (F): `dsp.img` bytes at each briefed abs offset are identical to the shell file bytes at the relative offset (3/3 true).

Decode (F): the 16 bytes at each magic are `7f 45 4c 46 00` followed by ASCII `bad elf mag...` — i.e. the loader's 4-byte ELF magic constant stored as data (`\x7fELF\0`), immediately followed by its own error string `bad elf magic in %s` (next string: `wrong ELF class %d expected %d in %s`). The 512 bytes at the three offsets are byte-identical across all three shells (sha256 prefix `7f1351b6...`).

**Verdict (N): none of the three briefed magics is a standalone ELF header.** They are the QDSP6 fastrpc loader's ELF-magic compare constant + error-message rodata. No inner/appended images exist in the OP6 fastrpc shells. This closes the open item from dsp-tz-map.md section 6.

## 5. a660_gmu.bin leading table vs public driver (F + I)

Public loader (GPL, fetched 2026-11-18, both URLs recorded):
- `https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git/plain/drivers/gpu/drm/msm/adreno/a6xx_gmu.c` (70,934 B)
- `.../adreno/a6xx_gmu.xml.h` (8,862 B)

What the mainline loader expects at offset 0 of the GMU fw (non-legacy path, `a6xx_gmu_fw_load`):

```c
struct block_header {
	u32 addr;
	u32 size;
	u32 type;
	u32 value;
	u32 data[];
};
```

Iteration from offset 0, stride 16+size (`NEXT_BLK`); `size == 0` blocks are skipped; `size > 0` blocks are routed: addr in [0,16K) -> ITCM (REG_A6XX_GMU_CM3_ITCM_START), addr in [dtcm_base, +16K) -> DTCM (dtcm_base = 0x10004000 for a650 family incl. a660), else `fw_block_mem` into icache/dcache/dummy BOs (a660: icache iova 0x04000 size 16M-16K; dummy iova 0x60000000 size 16K; debug BO 0x60400000 28K exists but is not in the fw_block_mem list). `gmu->legacy` (raw bulk copy <= 0x8000) is set only for a630 family. The type/value fields of data blocks are **not consumed** by mainline. "RS64" appears **0 times** in both fetched files — the public driver has no RS64-specific struct; the a660 fw format is the block-header chain (N for an RS64-named header).

Test of `data-fetch/second-device/larry/tree-vendor/firmware/a660_gmu.bin` (55,256 B) against that format — **exact match (F)**:

- 15 blocks; the chain ends at exactly 55,256 (chain_exact_end true, no overflow).
- Leading 8 u32-LE pairs from the briefing = the first **4** of **11 zero-size block_headers** (the briefing's "section table" hypothesis is confirmed with a refinement: they are prealloc requests, see below).
- 11 zero-size blocks `{addr, size=0, type, value=requested_bytes}`:

| # | offset | addr | type | value (bytes) | mainline region containing it |
|---|---|---|---|---|---|
| 1 | 0 | 0x0 | 1 | 476 (0x1dc) | ITCM [0,0x4000) |
| 2 | 16 | 0x4000 | 1 | 54,476 (0xd4cc) | icache [0x4000, 0x1004000) |
| 3 | 32 | 0x200 | 1 | 14,948 (0x3a64) | ITCM |
| 4 | 48 | 0x100000 | 1 | 34,228 (0x85b4) | icache |
| 5 | 64 | 0x200000 | 1 | 76,416 (0x12a80) | icache |
| 6 | 80 | 0x300000 | 1 | 28,768 (0x7060) | icache |
| 7 | 96 | 0x10004000 | 1 | 12,064 (0x2f20) | DTCM [0x10004000, 0x10008000) |
| 8 | 112 | 0x10007000 | 1 | 3,972 (0xf84) | DTCM |
| 9 | 128 | 0x10007fdc | 1 | 24 (0x18) | DTCM |
| 10 | 144 | 0x60000000 | 7 | 4,096 | dummy [0x60000000, +16K) |
| 11 | 160 | 0x60001000 | 7 | 4,096 | dummy |

- 4 data blocks with `{addr, size, 0xEFBEADDE, 0xEFBEADDE}` — both type and value are the Qualcomm DEADBEEF sentinel (bytes de ad be ef):

| offset | addr | size | data at | mainline routing |
|---|---|---|---|---|
| 176 | 0x0 | 476 | 192 | ITCM |
| 668 | 0x4000 | 54,476 | 684 | icache |
| 55,160 | 0x10007f98 | 40 | 55,176 | DTCM |
| 55,216 | 0x10007fdc | 24 | 55,232 | DTCM |

- Mapping TOC<->data: prealloc request sizes equal the corresponding data block sizes for addr 0x0 (476), 0x4000 (54,476) and 0x10007fdc (24); the remaining eight requests have no data block — they are pure preallocation requests (I). Every request range [addr, addr+value) fits inside mainline's hardcoded a660 allocations (F, 11/11), consistent with the mainline comment at a6xx_gmu.c:2364: "A660 now requires handling 'prealloc requests' in GMU firmware. For now just hardcode allocations based on the known firmware."

Interpretation (I): the briefing's "8 u32-LE pairs as a section table" is decoded as the a660 GMU firmware's **prealloc-request TOC** — zero-size `block_header`s whose `addr` is the requested region base and whose `value` is the requested byte count, followed by DEADBEEF-tagged data blocks loaded ITCM/icache/DTCM. This is the structure the public loader consumes (except it ignores the TOC and hardcodes the allocations).

Contrast (F): `a619_gmu.bin` in the same firmware dir is 32,768 B and does **not** parse as a block chain (garbage headers from byte 0) — it is a raw legacy-format image (`fw_image->size <= 0x8000` legacy path), showing the block-header format is fw-generation-specific.

## 6. Open items

- Metadata header word[0]/word[1] semantics (25/5 vs 0/6) and the SM8250-only words (120,120; descriptors `[7,0,1,0,0,10,24584]` / `[7,0,1,0,0,266,24584]`) — H: secboot version pair and per-chain descriptors; needs a downstream secimage reference to settle.
- Exact byte range covered by SIG_A/SIG_B (PSS salt prevents message recovery; would need dynamic or downstream-source evidence).
- Word[4] = hash_size + 19,200 (constant 19,200 both gens) — role unknown.
- Same decode should be re-run on other PIL images (cmnlib/keymaster/devcfg from instantnoodle) to check whether the SHA-384 metadata is TZ-specific or SM8250-wide.

## 7. Honest negatives

- The three briefed fastrpc-shell embedded ELF magics are NOT ELFs — loader magic constant + error string rodata (false positives, 0/3 valid).
- No sha256(empty), hash-of-zero-memsz, or self-hash-with-zeroed-table variants occur in either metadata (5+ variants tested per image).
- Cert DER hashes do not occur elsewhere in the metadata; the 256-byte sig blocks do not verify under the root keys (they verify only under the paired leaf keys).
- No "RS64" string or RS64-specific structure exists in the fetched public driver (0 mentions); the a660 GMU fw format is the block_header chain.
- a619_gmu.bin is a raw legacy image, not a block chain (chain parse invalid by design).
- OP6 metadata contains no strings beyond the cert subjects/extension text; SM8250 metadata contains zero ASCII runs >= 8 chars outside certs (both checked).
