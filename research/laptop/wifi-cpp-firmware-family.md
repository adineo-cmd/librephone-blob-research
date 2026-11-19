# Qualcomm MSM CPP `cpp_firmware_*` — content-level RE: it is camera microcode, not WiFi, and the version lives in a `u16`

Analysis date: 2026-11-19. Evidence class: **MEASURED PAYLOADS** — every
number below is computed from bytes on disk or quoted from public
GPL-2.0-only source. Device counts are re-derived from
`sharing-clusters.csv`, not copied from a manifest.

Companion documents:

| document | owns |
|---|---|
| **`qualcomm-data-blob-fleet.md`**, **`qualcomm-qca-bt-fleet.md`**, **`qualcomm-qca-bt-fleet-content.md`**, **`qualcomm-adreno-gmu.md`**, **`qualcomm-adsp-bm2n-fleet.md`** (this directory, existing) | the other fleets. *Not edited by this work.* |
| **`wifi-cpp-firmware-family.md`** (this file) | the family-identity correction, the 16 KiB window contract, the version rule, the matrix verdict |
| `../../implementations/wifi-cpp-fleet/cpp-version-matrix-analysis.md` | the full analysis: per-range invariant tables, all three matrices, hardware→firmware map, `[OPEN]` register |
| `../../implementations/wifi-cpp-fleet/cpp_probe.py` | the probe. `python3 cpp_probe.py <file> --brief` |
| `../../implementations/wifi-cpp-fleet/README.md` | usage, clean-room statement, fixture/test instructions |

Labels used throughout: **[S]** quoted from public source (file, symbol) ·
**[M]** own measurement of payload bytes · **[OPEN]** not established, gap
named.

Bytes live only in `/tmp/astro_u/cpp/`; **no proprietary content is
committed**. The repo root `.gitignore` excludes `*.bin` but not `*.fw` (this
family's extension), so `implementations/wifi-cpp-fleet/fixtures/.gitignore`
excludes the fixture directory locally; the fixtures are synthetic and
regenerable and are not tracked.

---

## 1. Headline: the matrix calls this fleet `wifi`, and that is wrong

`sharing-clusters.csv` files all twelve `cpp_firmware_*` rows under family
`wifi`. They are not wireless firmware. They are the **Camera
Post-Processing** microcode of the Qualcomm MSM camera pipeline.

Four independent lines of evidence, in the order they were established:

1. **The consumer is a camera driver.** `drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c`
   (GPL-2.0-only, `LineageOS/android_kernel_xiaomi_msm8953` @ `lineage-21`,
   fetched 2026-11-19) loads exactly these files through
   `cpp_load_fw()`. "pproc" = post-processing; "cpp" = camera
   post-processor. **[S]**
2. **The producer is a camera userspace module.**
   `mm-camera/mm-camera2/media-controller/modules/pproc-new/cpp/cpp_hardware.c`
   (`Sushrut1101/android_vendor_qcom_proprietary` @ `master`) selects the
   firmware version from a camera hardware version. **[S]**
3. **`linux-firmware` has none of them.** `WHENCE`, 537,962 B, fetched
   2026-11-19: **zero** `cpp_firmware` hits. **[M]** A WiFi/BT blob of this
   lineage would normally appear there (F-74's pattern).
4. **The `brcmfmac` naming hypothesis fails.** Mainline
   `brcmfmac/firmware.c` composes `brcmf_fw` names; it has no notion of a
   `cpp_firmware_vN_N_N.fw` payload. The `cpp` prefix collision with
   Cypress/Infineon parts is coincidental. **[S]**

Corroboration already in the repo: `blob-matrix/per-soc-method-plans.md`
line 152 lists "camera cpp_firmware" alongside the Adreno 530 fleet for
SDM845 — i.e. the camera reading was present in the planning notes, while the
sharing-clusters family column said `wifi`.

The CSV is outside this work's write scope, so the label is **not** corrected
here. It is recorded, with evidence, so the next person does not spend a
session re-deriving the wrong hypothesis from it.

## 2. Fleet rows (from `sharing-clusters.csv`)

Twelve identities, not thirteen — the ladder reads like 13 by eye but `cpp`
rows are 12. All are 9-device rows except `v1_12_1` (4 devices).

| md5 | file | bytes | devices | fetched |
|---|---|---|---|---|
| `4d145d5a13a3956bf33aec94a8e7fe62` | `cpp_firmware_v1_1_1.fw` | **16,128** | 9 | **MATCH** |
| `738a83a673dd45fa5852b5cc9519ee94` | `cpp_firmware_v1_1_6.fw` | 16,384 | 9 | **MATCH** |
| `3f078c3d1658679a762f7d77c99517cd` | `cpp_firmware_v1_2_0.fw` | 16,384 | 9 | **MATCH** |
| `b6f54efc4675040f7b7e99398905646e` | `cpp_firmware_v1_4_0.fw` | 16,384 | 9 | **MATCH** |
| `e51087ba19409150103faafaff849627` | `cpp_firmware_v1_5_0.fw` | 16,384 | 9 | **MATCH** |
| `ed1f2071b61447924f50fe8670cd51be` | `cpp_firmware_v1_5_1.fw` | 16,384 | 9 | **MATCH** |
| `02e4044179d7dfc069aa9a42db690642` | `cpp_firmware_v1_5_2.fw` | 16,384 | 9 | **MATCH** |
| `de85a5f8196ec73cffc61382b3e0d5f6` | `cpp_firmware_v1_6_0.fw` | 16,384 | 9 | **MATCH** |
| `04423a29e78bb01d9be62256a65354a6` | `cpp_firmware_v1_8_0.fw` | 16,384 | 9 | **MATCH** |
| `8d08bfdf92db5b1df58af9b6adf61eae` | `cpp_firmware_v1_10_0.fw` | 16,384 | 9 | **MATCH** |
| `ef031a3f24f877242621ba695d8dcbd2` | `cpp_firmware_v1_12_0.fw` | 16,384 | 9 | **MATCH** |
| `a59e732fcbf71cb5fcc6c54fef0124d6` | `cpp_firmware_v1_12_1.fw` | 16,384 | **4** | **MATCH** |

Device sets:

- 9-device set: `Mi8917; Mi8937; discovery; ginkgo; kirin; laurel_sprout; mermaid; pioneer; voyager`
- `v1_12_1` (4): `Mi8917; Mi8937; ginkgo; laurel_sprout`

**12/12 md5 MATCH**, no NON-DB-IDENTICAL members, no fetch failures. Source:
`TheMuppets/proprietary_vendor_xiaomi_ginkgo` @ `lineage-22.2`,
`proprietary/vendor/firmware/`, fetched 2026-11-19.

Set corroboration from two independent publishers:
`LineageOS/android_device_xiaomi_msm8953-common` @ `lineage-19.1`
`proprietary-files.txt` lists eleven (all but `v1_12_1`);
`trinket-devs/device_xiaomi_ginkgo` @ `master` lists all twelve.

The `v1_1_1` size is **16,128 B**, not 16,384 — and that is genuine, not a
truncated fetch: the md5 matches the DB row whose own `bytes` column says
16128. It is exactly 256 B short of the window and lacks the epilogue entirely.

## 3. The window contract: there isn't one — and that is the finding

Across the programme, three Qualcomm firmware families now have three
different answers to "how big am I":

| family | declared-length rule | self-describing? |
|---|---|---|
| QCA BT gen 1 (F-75) | `file = 4 + 24 + data_length + 256` | yes — TLV container |
| QCA BT gen 2 (F-76) | `file = 4 + 32 + data_length + 36` | yes — TLV container |
| **MSM CPP** (this fleet) | **none** | **no** |

`cpp_load_fw()` in `msm_cpp.c` does not parse anything. It sends
`MSM_CPP_CMD_FW_LOAD`, then `fw->size` and `MSM_CPP_START_ADDRESS` (`0x0`),
then streams `fw->size / 4` little-endian 32-bit words. The only assertion is
implicit in the division: **size must be a multiple of 4**. **[S]**

So CPP is a **placed image in a padded fixed window**:

```
0x0000  0x0002                                              0x0022
  |lead ||--- 16 x u16 vector table (32 B) ------------------||
                                                             |
                              opaque code / table region     |
                                                             |
                code_end (per version: 0x19B6 .. 0x3B02) ----+
                                                             |
                                   0xFF fill (erased flash)  |
                                                             |
0x3EFC  0x3EFE                                              0x3FCA  0x4000
  |len||--- 204-byte invariant epilogue ---------------------||0xFF--|
```

Measured facts about the window [M]:

- **Lead word** `0x7140` at `[0x0000, 0x0002)` — invariant in 12/12.
- **16 × `u16` vector table** at `[0x0002, 0x0022)`. Not all even (slot 15 is
  odd in 10/12, slot 9 in 9/12). 11/12 share one equality pattern — a single
  value covering slot 1 plus slots 4–8 and 10–14; `v1_2_0` alone splits slot
  10 off, giving a 7th distinct value. Every value, doubled, lands below that
  file's `code_end`. **[OPEN]** semantics.
- **Fill is `0xFF`, never `0x00`** — 12/12. Interior `0x00` runs exist
  (284–472 B) but are *payload tables*, not padding; a whole-file zero-run
  test gives a false positive, so the probe scopes it to `[code_end, EOF)`.
- **Epilogue** `[0x3EFE, 0x3FCA)`, 204 B, byte-identical in 11/12:
  `sha1 f81d97b070307896ce03469472c85d6d443a5d15`. Absent in `v1_1_1`
  (which ends at `0x3F00` — the 256-byte discrepancy).
- **Tail fill** `[0x3FCA, 0x4000)`, 54 B, all `0xFF` in all eleven windowed
  files.

### 3.1 The one real length signal is payload-internal and unread

The `u16` at `0x3EFC` is a **halfword count of the region it terminates**:

```
code_end == 2 * (u16@0x3EFC + 1)
```

| versions | field | result |
|---|---|---|
| 1.2.0, 1.4.0, 1.5.0, 1.5.1, 1.5.2, 1.6.0 | populated | **exact**, residual 0 |
| 1.1.1, 1.1.6, 1.8.0 | `0xFFFF` (erased) | not populated |
| 1.10.0, 1.12.0, 1.12.1 | populated | exact **+ a 176 B** fixed-stride block after the region |

`2*(w+1)` never equals 16,384, so the field describes the **payload**, not the
container. The loader never reads it. Its three observed shapes are exactly
why it cannot be treated as a file-length field — and §5 of the full analysis
shows 1.5.0→1.5.1 is a **two-byte** change, one of which is *not* this field.

## 4. Where the version actually lives

### 4.1 The rule

Every one of the twelve files contains **exactly one** 16-bit little-endian
word of the form **`0x1000 | BCD(minor)`**, and in every case the nearest
preceding `MSM_CPP_MSG_ID_TRAILER` (`0xABCDEFAA`) record sits `+14` bytes above
it — except in 1.5.0 and 1.5.1, where the gap is `+10`. **[M]**

| version | marker | offset(s) |
|---|---|---|
| 1.1.1 | `0x1001` | `0x2B7E` |
| 1.1.6 | `0x1001` | `0x0CB6` |
| 1.2.0 | `0x1002` | `0x0CBA` |
| 1.4.0 | `0x1004` | `0x0CD6` |
| 1.5.0 | `0x1005` | `0x00C6` |
| 1.5.1 | `0x1005` | `0x00C6` |
| 1.5.2 | `0x1005` | `0x011A` |
| 1.6.0 | `0x1006` | `0x0102` |
| 1.8.0 | `0x1008` | `0x015A` |
| 1.10.0 | `0x1010` | `0x01F2`, `0x247A`¹ |
| 1.12.0 | `0x1012` | `0x01F2` |
| 1.12.1 | `0x1012` | `0x01F2` |

¹ The second `1.10.0` hit is not a version field — it is the ninth `u16` of an
eight-entry code-offset table at `0x246A` that happens to equal the marker.
Full analysis §5.2.

**BCD matters:** minor 10 encodes as `0x1010` and minor 12 as `0x1012`, which
is what keeps `1.10` from reading as `1.1`. Note this is a *different
encoding of the same number* from the public enum, which packs minor as a
plain binary field:

- `CPP_FW_VERSION_*` bitfield (`cpp_hw_params.h`): 31:28 major, 27:16 minor,
  15:0 step → `1.10.0` = `0x100A0000`. **[S]**
- In-file marker: `0x1000 | BCD(minor)` → `1.10.0` = `0x1010`. **[M]**

Anyone mapping one onto the other with a shift will get `1.10` and `1.12`
wrong.

### 4.2 The decoy

`strings` on any windowed file returns `v1.1`. It is **not** a version field:

- present in 11/12 files, including 1.12.0 and 1.12.1;
- fixed offset `0x3F80`, inside the invariant epilogue;
- `0xFF` immediately before it, `0x8D` immediately after — an exact printable
  run, not a fragment of a longer string.

It is a literal of the shared epilogue. **No file carries its own version as
ASCII text** — an honest negative, asserted across all twelve.

Also in the epilogue: `MSM_CPP_MSG_ID_OK` (`0x0A0A4B4F`) at `0x3F6C` and
`cmd>` at `0x3FB4`, both invariant. The OK word at a fixed epilogue offset
means the "exactly one `MSG_ID_OK` per file" census is a **proxy for epilogue
presence**, not an independent protocol signal — `v1_1_1`, the only file with
no epilogue, reports zero.

## 5. The matrix verdict

Three matrices are computed because one number lies for a padded window:
`whole` (inflated by shared `0xFF`), `code_region` (restricted to
`min(code_end)`), and `content_only` (excludes positions where either side is
`0xFF`/`0x00`).

Selected cells, whole / content:

| pair | whole | content |
|---|---|---|
| 1.5.0 ↔ 1.5.1 | **99.99** | **99.97** |
| 1.12.0 ↔ 1.12.1 | 61.06 | 32.95 |
| 1.10.0 ↔ 1.12.0 | 50.10 | 14.90 |
| 1.5.0 ↔ 1.6.0 | 67.24 | 15.14 |
| 1.1.1 ↔ anything | 10.78–26.21 | 2.57–20.14 |

Padding inflation is systematic and large — 1.5.0↔1.6.0 is 4.4× higher whole
than content. Any conclusion from the whole-file number alone is wrong.

**Clustering is monotone in version distance.** At a 60% whole-file
threshold the fleet splits into `{1.1.1}`, `{1.1.6 … 1.6.0}`, `{1.8.0}`,
`{1.10.0}`, `{1.12.0, 1.12.1}` — exactly a version-ordered lineage with two
structural jumps. Version sort order **does** match byte-identity clustering.
No file is a byte-prefix of another.

The two informative deltas:

- **1.5.0 → 1.5.1: exactly 2 bytes** (`0x0034`, one code byte; `0x00C4`, the
  low half of the 32-bit word carrying the marker). A step bump is a two-byte
  change. This is the cleanest evidence that the ladder is a real code
  lineage with in-band identification. Note the `0x00C4` byte is **not** the
  step digit — it reads `0x10` vs `0x02` and disagrees with the filename step
  in 9 of 12 files; it is a build counter beside the marker (`[OPEN]`).
- **1.12.0 → 1.12.1: 6,380 differing bytes**, 32.95 content identity. A
  near-total rewrite under a step bump — so "step" is a *build revision*, not
  a semantic patch level. Consistent with 1.12.1 shipping to only 4 devices:
  a rework that did not roll out fleet-wide.

## 6. Which hardware gets which firmware

From `cpp_hardware_select_fw_version()` **[S]**:

| hardware | firmware |
|---|---|
| 1.1.x, 2.0.0 | 1.2.0 |
| 4.0.0, 4.2.0 | 1.4.0 |
| 4.1.0 | 1.6.0 |
| 4.3.2, 4.3.3, 4.3.4 | 1.5.0 |
| **4.3.0** | **1.5.1** |
| 5.0.0, 5.1.0 | 1.8.0 |
| 6.0.0 | 1.10.0 |
| 6.1.0, 6.1.2 | 1.12.0 |
| 6.1.4 | 1.12.1 |

**Non-monotone, and really so:** hardware 4.3.0 (MSM8952) takes 1.5.1 while
4.3.3 (MSM8953) takes 1.5.0. Given the two-byte delta of §5, 1.5.1 is a
targeted fix for the MSM8952 variant, not a general successor. Any
"higher hardware ⇒ higher firmware" table gets 4.3.x wrong.

## 7. Cross-fleet verdict

| aspect | F-75 (QCA BT gen 1) | this fleet (MSM CPP) |
|---|---|---|
| declared length | `4 + 24 + data_length + 256` | none |
| loader checks a container | yes | **no — blind word stream** |
| size | 1,243–56,180 B variable | fixed 16 KiB window (one 16,128 B) |
| filename digit | ROM build *target* (misleading) | true `major.minor.step` |
| in-file version | `patch_version` = format rev, not the filename digit | `0x1000\|BCD(minor)` (+ adjacent build counter) |
| padding | 256-byte signature-class tail | `0xFF` erase fill |
| loader validates | framing, segments | word alignment only |

The filename-semantics inversion is the transferable lesson. F-75 taught
"don't trust the filename digit" (it names a target ROM, and the same ROM
build appears under two digits for different chips). CPP teaches the mirror
image: "here the filename digit **is** trustworthy — but the `v1.1` string
inside the file is not." Same class of trap, opposite direction.

Against the ADSP `bm2n` fleet the similarity is only superficial (fixed vendor
path, Qualcomm, per-variant family): `bm2n` is a serialized QNN/HTP object
graph with a real load header and record grammar; CPP is position-dependent
microcode in an erased-flash window with no in-band grammar beyond the
trailer records.

## 8. What a free reimplementation needs

**Writable today:**

- The **loader** — fully specified by GPL source, no RE required: send
  `MSM_CPP_CMD_FW_LOAD`, send size and `MSM_CPP_START_ADDRESS` 0, stream
  `size/4` LE words.
- The **window shape** — any multiple of 4 works as far as the kernel is
  concerned; the fleet's own convention is 16,384 B.
- The **identification convention** — `0x7140` at `0x0000`, one
  `0x1000|BCD(minor)` marker in the code region below a trailer record, and
  the three `msm_cpp.h` magic words present.

**Opaque, needs synthesis or further RE:**

- The code region `[0x0022, code_end)`, 3.3–4.7 bits/byte, 35–60% `0xFF`
  interleaved. ISA and semantics **[OPEN]**; no disassembly performed, none
  claimed.
- The 204-byte invariant epilogue — byte-identical but unexplained **[OPEN]**.
- The 176-byte fixed-stride block in 1.10.0/1.12.x — 14 B prologue + 8 × 20 B
  records + 2 B tail, the 12-byte body identical in all 8 and two `u16`
  counters stepping by `0x0A` and `8`. Semantics **[OPEN]**.
- Any core-side verification — kernel verifies nothing; crc32/sum32/halfword
  sums over the code region match no trailer field in any file. **[OPEN]**.

## 9. `[OPEN]` register

| # | question | range |
|---|---|---|
| 1 | semantics of the 16×`u16` vector table | `[0x0002, 0x0022)` |
| 2 | semantics of the 204-byte invariant epilogue | `[0x3EFE, 0x3FCA)` |
| 3 | why 1.1.1/1.1.6/1.8.0 leave the length `u16` erased (`code_end` 0x3B02) | `0x3EFC` |
| 4 | semantics of the 176-byte fixed-stride block | 1.10.0/1.12.x |
| 5 | why 1.1.1 is 256 B short and lacks the epilogue | whole file |
| 6 | microcode ISA / core architecture | `[0x0022, code_end)` |
| 7 | does the core verify a checksum? | whole payload |
| 8 | why 1.12.0→1.12.1 is a rewrite while 1.5.0→1.5.1 is 2 bytes | — |
| 9 | does anything consume the `0x7140` lead word? | `0x0000` |
| 10 | meaning of the build counter beside the marker (disagrees with the filename step in 9/12) | `marker-2` |

Full detail, all three matrices, and the invariant-vs-varying census are in
`../../implementations/wifi-cpp-fleet/cpp-version-matrix-analysis.md`.
