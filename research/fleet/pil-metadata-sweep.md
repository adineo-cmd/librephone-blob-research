# PIL metadata sweep: per-phdr hash-slot layout across every signed PIL image (SDM845 + SM8250)

Workorder: WORKORDER-001 (desktop fleet RE). Analysis date: 2026-11-19.
Prior evidence: `blob-matrix/desktop/fleet-re/qsee-crossgen.md` (layout decoded on tz.img of both devices, SHA-256 vs SHA-384 split, first-public hash-slot decode).
Machine-readable evidence: `analysis/out/pil-metadata-sweep.json` (28 per-image records: ELF facts, phdr table, metadata candidates, width trials, per-slot status, header words, certs, sig blocks, version strings).
Script: `analysis/tools/pil_metadata_sweep.py` (stdlib-only; ELF/phdr parse, PT_NULL candidate scan, sha256/sha384/sha512 width trials with byte-search + base alignment, per-slot verify, DER cert scan).

Evidence classes: **F** = measured fact, **I** = interpretation, **H** = hypothesis, **N** = negative.

## 0. Headline answer

**The SHA-384 metadata is SM8250-wide, not TZ-specific (F).** 16/16 signed PIL images from the SM8250 device decode with SHA-384 (48 B) hash slots; 12/12 SDM845 images decode with SHA-256 (32 B) slots. 28/28 swept images match the decoded layout — zero exceptions, zero parse failures, zero metadata-less images. The per-phdr hash-slot container is **universal across the entire signed PIL/secboot chain on both SoCs**: tz, hyp, xbl, xbl_config, abl (ABOOT), aop, cmnlib, cmnlib64, keymaster, devcfg, uefisecapp, imagefv, qupfw, storsec, multiimgoem, featenabler.

Totals (F): 220 hash slots verified (178 exact digest hits + 42 zero slots), 35 X.509 chains (7 production + 28 test-only) = 105 certs, 35 signature blocks (exactly one 256-B block per chain), 29 version-string hits.

## 1. Inputs (sha256, F)

11 enchilada partitions (cmnlib, cmnlib64, keymaster, devcfg, hyp, aop, abl, qupfw, storsec, xbl, xbl_config) were dumped this session from `data-fetch/enchilada/payload.bin` with `librephone-blob-research/qualcomm-fp6/tools/payload_dump.py`. boot.img/recovery (Android bootimg) excluded as out of scope; no bootimg magic was encountered in the swept set.

| file | size | sha256 | SoC |
|---|---|---|---|
| `data-fetch/second-device/instantnoodle/tz.img` | 3,194,880 | `c75d2bd2...7018603` | SM8250 |
| `data-fetch/second-device/instantnoodle/abl.img` | 225,280 | `27bb1240...c32a24b8` | SM8250 |
| `data-fetch/second-device/instantnoodle/aop.img` | 204,800 | `b2e1330f...4f9fed43` | SM8250 |
| `data-fetch/second-device/instantnoodle/cmnlib.img` | 401,408 | `98f706db...561e874f` | SM8250 |
| `data-fetch/second-device/instantnoodle/cmnlib64.img` | 520,192 | `6cdd8073...cc9c333d` | SM8250 |
| `data-fetch/second-device/instantnoodle/devcfg.img` | 57,344 | `70f0c68e...0492750d` | SM8250 |
| `data-fetch/second-device/instantnoodle/featenabler.img` | 90,112 | `d3b540d5...e5ee22ea` | SM8250 |
| `data-fetch/second-device/instantnoodle/hyp.img` | 450,560 | `a66d4705...28a92be3` | SM8250 |
| `data-fetch/second-device/instantnoodle/imagefv.img` | 1,191,936 | `f295c675...5b671a5b` | SM8250 |
| `data-fetch/second-device/instantnoodle/keymaster.img` | 266,240 | `5412f657...63e2657e` | SM8250 |
| `data-fetch/second-device/instantnoodle/multiimgoem.img` | 16,384 | `e4969bf3...9f8c3c63` | SM8250 |
| `data-fetch/second-device/instantnoodle/qupfw.img` | 57,344 | `7c41ee2f...3de47b3c` | SM8250 |
| `data-fetch/second-device/instantnoodle/storsec.img` | 24,576 | `82f093ae...5bc9ac7e` | SM8250 |
| `data-fetch/second-device/instantnoodle/uefisecapp.img` | 126,976 | `906cb598...0f9b7543` | SM8250 |
| `data-fetch/second-device/instantnoodle/xbl.img` | 3,985,408 | `6509bafb...de084b8e` | SM8250 |
| `data-fetch/second-device/instantnoodle/xbl_config.img` | 94,208 | `f17be502...8993b28f` | SM8250 |
| `data-fetch/enchilada/tz.img` | 2,056,192 | `2d133bda...d16baca` | SDM845 |
| `data-fetch/enchilada/abl.img` | 2,183,168 | `cff7cbf5...55afbe34` | SDM845 |
| `data-fetch/enchilada/aop.img` | 184,320 | `f6311ac6...78b12629` | SDM845 |
| `data-fetch/enchilada/cmnlib.img` | 380,928 | `fc726681...ee425920` | SDM845 |
| `data-fetch/enchilada/cmnlib64.img` | 499,712 | `0cb7e040...33753725` | SDM845 |
| `data-fetch/enchilada/devcfg.img` | 40,960 | `139e0d80...adbf4b6e` | SDM845 |
| `data-fetch/enchilada/hyp.img` | 397,312 | `eaf681c1...6c83e2a8` | SDM845 |
| `data-fetch/enchilada/keymaster.img` | 233,472 | `7e61215d...7af114fb` | SDM845 |
| `data-fetch/enchilada/qupfw.img` | 65,536 | `92edf512...30eca96e` | SDM845 |
| `data-fetch/enchilada/storsec.img` | 24,576 | `6d170aef...4795fda1` | SDM845 |
| `data-fetch/enchilada/xbl.img` | 3,289,088 | `b0bd4280...847810e0` | SDM845 |
| `data-fetch/enchilada/xbl_config.img` | 98,304 | `b089b9de...62f7b84f` | SDM845 |

tz.img sha256s of both devices are byte-identical to the files analyzed in qsee-crossgen.md — the controls are the same binaries (F).

## 2. Sweep table (F)

All images: metadata is PT_NULL segment **seg[1]** at file offset 0x1000 (every image). `phnum` = e_phnum; `base` = hash-table offset inside the metadata segment (== metadata header size); `w5` = metadata header word[5] (u32le); `hit`/`zero` = slot statuses; `chains` = cert chain groups (prod = CASS leaf chain present).

| image | ELF | e_type | phnum | meta filesz | algo | base | w5 (= phnum x width) | hit/zero | chains | class |
|---|---|---|---|---|---|---|---|---|---|---|
| SM8250 tz | ELF64 AArch64 | ET_EXEC | 23 | 20,800 | **SHA-384** | 288 | 1104 = 23x48 | 21/2 | 2 (prod+test) | layout-matches-sha384 |
| SM8250 abl | ELF32 ARM | ET_EXEC | 3 | 6,712 | **SHA-384** | 168 | 144 = 3x48 | 2/1 | 1 (test) | layout-matches-sha384 |
| SM8250 aop | ELF32 ARM | ET_EXEC | 7 | 6,904 | **SHA-384** | 168 | 336 = 7x48 | 6/1 | 1 (test) | layout-matches-sha384 |
| SM8250 cmnlib | ELF32 ARM | ET_DYN | 6 | 19,984 | **SHA-384** | 288 | 288 = 6x48 | 5/1 | 2 (prod+test) | layout-matches-sha384 |
| SM8250 cmnlib64 | ELF64 AArch64 | ET_DYN | 6 | 19,984 | **SHA-384** | 288 | 288 = 6x48 | 5/1 | 2 (prod+test) | layout-matches-sha384 |
| SM8250 devcfg | ELF64 AArch64 | ET_EXEC | 4 | 6,760 | **SHA-384** | 168 | 192 = 4x48 | 3/1 | 1 (test) | layout-matches-sha384 |
| SM8250 featenabler | ELF64 AArch64 | ET_DYN | 8 | 20,080 | **SHA-384** | 288 | 384 = 8x48 | 7/1 | 2 (prod+test) | layout-matches-sha384 |
| SM8250 hyp | ELF64 AArch64 | ET_EXEC | 4 | 6,760 | **SHA-384** | 168 | 192 = 4x48 | 2/2 | 1 (test) | layout-matches-sha384 |
| SM8250 imagefv | ELF32 ARM | ET_EXEC | 3 | 6,712 | **SHA-384** | 168 | 144 = 3x48 | 2/1 | 1 (test) | layout-matches-sha384 |
| SM8250 keymaster | ELF64 AArch64 | ET_DYN | 8 | 6,952 | **SHA-384** | 168 | 384 = 8x48 | 7/1 | 1 (test) | layout-matches-sha384 |
| SM8250 multiimgoem | ELF32 ARM | ET_NONE | 3 | 6,712 | **SHA-384** | 168 | 144 = 3x48 | 2/1 | 1 (test) | layout-matches-sha384 |
| SM8250 qupfw | ELF32 EM_QDSP6 (164) | ET_EXEC | 10 | 20,176 | **SHA-384** | 288 | 480 = 10x48 | 9/1 | 2 (prod+test) | layout-matches-sha384 |
| SM8250 storsec | ELF32 ARM | ET_DYN | 8 | 6,952 | **SHA-384** | 168 | 384 = 8x48 | 7/1 | 1 (test) | layout-matches-sha384 |
| SM8250 uefisecapp | ELF32 ARM | ET_DYN | 8 | 6,952 | **SHA-384** | 168 | 384 = 8x48 | 7/1 | 1 (test) | layout-matches-sha384 |
| SM8250 xbl | ELF64 AArch64 | ET_EXEC | 15 | 7,288 | **SHA-384** | 168 | 720 = 15x48 | 10/5 | 1 (test) | layout-matches-sha384 |
| SM8250 xbl_config | ELF64 ARM(40) | ET_EXEC | 6 | 6,856 | **SHA-384** | 168 | 288 = 6x48 | 5/1 | 1 (test) | layout-matches-sha384 |
| SDM845 tz | ELF64 AArch64 | ET_EXEC | 17 | 19,992 | **SHA-256** | 40 | 544 = 17x32 | 14/3 | 2 (prod+test) | layout-matches-sha256 |
| SDM845 abl | ELF32 ARM | ET_EXEC | 3 | 6,536 | **SHA-256** | 40 | 96 = 3x32 | 2/1 | 1 (test) | layout-matches-sha256 |
| SDM845 aop | ELF32 ARM | ET_EXEC | 6 | 6,632 | **SHA-256** | 40 | 192 = 6x32 | 5/1 | 1 (test) | layout-matches-sha256 |
| SDM845 cmnlib | ELF32 ARM | ET_DYN | 6 | 6,632 | **SHA-256** | 40 | 192 = 6x32 | 5/1 | 1 (test) | layout-matches-sha256 |
| SDM845 cmnlib64 | ELF64 AArch64 | ET_DYN | 6 | 6,632 | **SHA-256** | 40 | 192 = 6x32 | 5/1 | 1 (test) | layout-matches-sha256 |
| SDM845 devcfg | ELF64 AArch64 | ET_EXEC | 4 | 6,568 | **SHA-256** | 40 | 128 = 4x32 | 3/1 | 1 (test) | layout-matches-sha256 |
| SDM845 hyp | ELF64 AArch64 | ET_EXEC | 4 | 6,568 | **SHA-256** | 40 | 128 = 4x32 | 2/2 | 1 (test) | layout-matches-sha256 |
| SDM845 keymaster | ELF64 AArch64 | ET_DYN | 8 | 6,696 | **SHA-256** | 40 | 256 = 8x32 | 7/1 | 1 (test) | layout-matches-sha256 |
| SDM845 qupfw | ELF32 EM_QDSP6 (164) | ET_EXEC | 12 | 19,832 | **SHA-256** | 40 | 384 = 12x32 | 11/1 | 2 (prod+test) | layout-matches-sha256 |
| SDM845 storsec | ELF32 ARM | ET_DYN | 8 | 6,696 | **SHA-256** | 40 | 256 = 8x32 | 7/1 | 1 (test) | layout-matches-sha256 |
| SDM845 xbl | ELF64 AArch64 | ET_EXEC | 16 | 6,952 | **SHA-256** | 40 | 512 = 16x32 | 10/6 | 1 (test) | layout-matches-sha256 |
| SDM845 xbl_config | ELF64 ARM(40) | ET_EXEC | 8 | 6,696 | **SHA-256** | 40 | 256 = 8x32 | 7/1 | 1 (test) | layout-matches-sha256 |

Notes (F): the wide-metadata images (~20 KB filesz) are exactly the trustlet-style images (tz, cmnlib, cmnlib64, featenabler, qupfw); all others carry compact ~6.5-7.3 KB metadata. The 40-B-header (SDM845) column also proves the header size is not fixed per generation — see section 4.

## 3. Controls re-verified (F)

- instantnoodle tz.img: word5 = 1104, table base 288, SHA-384, 21/23 in-place hits, zero slots {1 (metadata self), 2 (filesz 0)} — identical to qsee-crossgen.md section 3.2; all six certs at the same offsets (1648/2707/3811/8048/9085/10180) with the same subjects.
- enchilada tz.img: word5 = 544, base 40, SHA-256, 14/17 hits, zero slots {1, 2, 16 (BSS, memsz 8192)} — identical to prior; certs at 840/2227/3323/7240/8560/9697.

## 4. Metadata header decode — refined by the fleet (F; corrects two claims in qsee-crossgen.md)

Header base (== hash-table offset) is **chain-count dependent on SM8250, fixed on SDM845**:

| header word (u32le) | 1-chain images (n=22) | 2-chain images (n=6) | prior doc claim |
|---|---|---|---|
| base / word count | SDM845: 40 B (10 words); SM8250: **168 B (42 words)** | SDM845: 40 B; SM8250: **288 B (72 words)** = 168 + 120 | "SM8250 header 288 B" — actually the 2-chain size |
| w[1] | SDM845: 5; SM8250: 6 (constant per SoC, H: secboot metadata version) | same | "25/5 vs 0/6" — w[0] is actually image-specific, see below |
| w[2] | **0** | 256 | "w[2] = sig block size" — set only when a second chain exists |
| w[3] | **0** | 6144 | "constant 6144" — refuted; second-chain cap |
| w[4] - w[5] | **6,400** | **19,200** | "constant 19,200" — refuted; 6400 + 12800 x (chains-1) |
| w[7] | 256 | 256 | sig block size (holds, all 28) |
| w[9] | **6,144** | **12,288** | "constant 12288" — refuted; **w[9] = 6144 x chain_count** (28/28) |
| w[10] (SM8250 only) | 0 | 120 | per-chain header extension, 120 B/chain |
| w[11] (SM8250 only) | 120 | 120 | constant |
| w[0] | image-specific, in {0, 4, 5, 25} (e.g. tz: 25 SDM845 / 0 SM8250; cmnlib 4; imagefv, xbl 5) | same | unassigned |

Rules w[9] = 6144 x chains, w[4]-w[5] = 6400 + 12800 x (chains-1), w[2]/w[3] zero unless second chain, w[10] = 120 x (chains-1) hold **28/28** (F). Interpretation (I): the SM8250 header is a fixed 168-B base plus one 120-B extension per extra chain; w[9] and w[3] are per-chain size caps of 6144 B; w[4]-w[5] encodes the same per-chain budget in the "offset of the first sig/chain region" field. The qsee-crossgen.md descriptor pairs `[7,0,1,0,0,X,24584]` at words 14-20 and 44-50 sit inside this 120-B per-chain region; single-chain images carry one region (values differ per image, e.g. abl `28,0,81,19821,0,258,24584`, xbl `0,0,81,19821,0,2,24584`) — values unassigned (H).

## 5. Hash-slot semantics — confirmed fleet-wide (F)

- slot count == phnum and word5 == phnum x digest width in **28/28** images.
- Zero slots occur exactly at (a) the metadata segment itself (always phdr index 1) and (b) segments with filesz == 0 (incl. both xbl's 4-5 empty phdrs and SDM845 tz's BSS seg 16). No exceptions; the prior "empty segment = zero slot, self = zero slot" rules generalize to the whole fleet.
- Digest hit totals: 100 SHA-384 slot verifications (SM8250) + 78 SHA-256 (SDM845) = 178; plus 42 zero slots = 220 = sum of all phnum.
- sha512 (64 B) probes: 0 hits in all 28 metadata segments (N).

## 6. Version strings (F)

29 string hits total; `QC_IMAGE_VERSION_STRING=` / `IMAGE_VARIANT_STRING=` / `OEM_IMAGE_VERSION_STRING=` values (all in RW segments):

| image | triple |
|---|---|
| SM8250 tz (@1471832/1471872/1471903) | `TZ.XF.5.8-00274` / `DARAANAAA` / `CRM` |
| SM8250 aop (@98726/98767/98798) | `AOP.HO.2.0-00194` / `AAAAANAZO` / `dg02-pool06-kvm58` |
| SM8250 hyp (@363134/363174/363205) | `TZ.XF.5.8-00274` / `DARAANAAA` / `CRM` (carries the TZ triple) |
| SM8250 xbl (@440207 seg4, @734242 seg8) | `BOOT.XF.3.2-00358-SM8250-1` / `Soc8250LAB` / `dg02-pool06-kvm58` |
| SM8250 xbl (@3751716 seg9) | `TZ.XF.5.8-00174` / `DARAANAAA` / `CRM` (embedded second image) |
| SDM845 tz (@1122340/1122387/1122418) | `TZ.XF.5.0.1.C5-00083.1` / `WAXAANAAA` / `CRM` |
| SDM845 hyp (@313982/314029/314060) | `TZ.XF.5.0.1.C5-00083.1` / `WAXAANAAA` / `CRM` |
| SDM845 xbl (@41155 seg2, @665985 seg11) | `BOOT.XF.2.0-00364-SDM845LZB-1` / `SDM845LA` / `rd-build-73` |
| SDM845 xbl (@2698864 seg12) | `TZ.XF.5.0.1-00106` / `WAXAANAAA` / `CRM` (embedded second image) |

(F) xbl.img on both devices embeds at least two distinct image version triples in different segments — the XBL ELF container wraps multiple sub-images (BOOT plus a TZ-tree image). (N) No version strings found in the other 21 images.

## 7. Signature and cert-chain facts (F)

- Every image carries at least one full secboot chain: one 256-B high-entropy signature block immediately before a 3-cert X.509 chain (entropy 7.06-7.26 per block; 35 blocks / 35 chains / 105 certs total). Region after the last cert is pure 0xFF padding to segment end (all_ff true, 28/28).
- All 105 certs: RSASSA-PSS (OID 1.2.840.113549.1.1.10), RSA-2048 SPKIs; issuer/subject CN ordering forms leaf<-intermediate<-root in every chain.
- Production chains (CASS leaf, QSEE Attestation CA path): SM8250 tz/cmnlib/cmnlib64/featenabler/qupfw; SDM845 tz/qupfw. 7 production chains total.
- All remaining 28 chains are the test chain: leaf `SecTools Test User`; intermediate `OEM Attestation CA` + self-signed `QCT Root CA 1` (OU "General Use Key", O=OEM) on SM8250, or `QUALCOMM Attestation CA` + `QCT Root CA 1` (OU "General Use Test Key (for testing 13 only)") on SDM845.
- Test-leaf issuance dates cluster at 2021-11-25 (SDM845 set), 2024-06-11 (most SM8250), and 2025-11-04 (SM8250 abl) — (I) partitions were re-signed at build/package time with the OEM test key rather than carrying the factory production signature.
- (I) The single-chain vs two-chain split correlates exactly with metadata header size on SM8250 (168 vs 288 B), giving a structural fingerprint of signing mode without parsing certs.

## 8. Per-image structure notes (F)

- **abl** (both): ABOOT ELF32 ARM, entry 0x9fa00000, 3 phdrs — same QSEE metadata layout as everything else; on SM8250 its test leaf was issued 2025-11-04 (freshest signature in the fleet).
- **aop**: ELF32 ARM ET_EXEC, entry 0xb000009 (both); 6-7 phdrs.
- **qupfw**: EM_QDSP6 (164) ELF, 10-12 phdrs, wide ~20 KB metadata, both devices carry prod+test chains.
- **imagefv**: ELF32 ARM wrapper (3 phdrs; seg0 filesz 0/memsz 112 MB) — the UEFI firmware volume (`_FVH` magic at file offset 0x3028) lives inside seg2; the outer ELF carries the standard metadata/test chain.
- **multiimgoem**: 16 KB ELF32 ARM with e_type 0 (ET_NONE) — unusual but parses fine; standard metadata.
- **xbl**: biggest phnum (15/16); 5-6 zero slots from empty segments; single test chain; embedded sub-image version strings (section 6).
- **xbl_config**: ELF64 with e_machine 40 (ARM) — 64-bit ARM, not AArch64; standard metadata.
- **hyp**: carries its platform's TZ version triple on both devices.

## 9. Open items

- w[0] semantics ({0,4,5,25}); descriptor-region word values (per-image).
- Exact byte range signed by each 256-B PSS block (unchanged from qsee-crossgen.md).
- w[4]-w[5] budget decomposition (6400 + 12800/chain) — which sub-regions the 6400/12800 account for.
- Whether w[1] (5 vs 6) is a secboot metadata format version and whether it flips with the hash width or with the SoC generation (only one SoC per value observed).
- Root-of-trust question (I/H): whether the OEM test-root chain is accepted by retail fuse state or only on engineering devices — needs boot-chain evidence beyond blobs.

## 10. Honest negatives

- **No metadata-less signed image in this fleet**: every devcfg/qupfw carries a full header + hash table + sig + chain (+ 0xFF pad).
- No SHA-256 digest hits in any SM8250 metadata and no SHA-384 hits in any SDM845 metadata (0/28 for the wrong width of its own SoC); sha512 never occurs.
- 21 of 28 images contain no version strings at all.
- No image lacks at least one signature block + cert chain; none carries more than two chains; no chain has other than 3 certs.
- The multi-chain descriptors and w[0]/w[1] remain role-unassigned; no claims made beyond the recorded values.
