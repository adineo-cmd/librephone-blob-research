# Fleet analysis — clean-room RE of the Qualcomm MSM CPP firmware fleet (2026-11-19)

The `cpp_firmware_v*_*_*.fw` family has sat in the upstream database under the
`wifi` family label since the laptop matrix was built. This work settles what
it actually is, verifies all twelve identities byte-exact against that matrix,
characterises the fixed 16 KiB window end to end, and produces the N×N version
matrix. Every claim below is either a **measurement of payload bytes on disk**
or a quote from **public GPL-2.0-only source**; nothing comes from a
decompiler, a proprietary SDK, or a vendor datasheet.

Two headline corrections up front, because both change how the fleet should be
read:

1. **`cpp` is not a wireless firmware and it is not Cypress/Infineon.** It is
   the **Camera Post-Processing** block of the Qualcomm MSM camera pipeline.
   The label in the matrix is wrong, and the naming collision with the Cypress
   `cpp`-prefixed WiFi parts is coincidental. Evidence in §1.
2. **The version string is not in the file as text.** It is one little-endian
   `u16`, `0x1000 | BCD(minor)`, inside the code region, immediately beneath a
   fixed `MSM_CPP_MSG_ID_TRAILER` record. The ASCII `v1.1` at `0x3F80` that a
   naive `strings` run finds is a **fixed literal of the shared epilogue**,
   present in 11/12 files regardless of version. Evidence in §5.

Labels: **[S]** quoted from public source (file, symbol) · **[M]** my own
measurement of payload bytes · **[OPEN]** not established, gap named.

Payload bytes live only in `/tmp/astro_u/cpp/`; **no proprietary content is
committed**. Fixtures are synthetic and regenerable by a committed script.

---

## 1. What consumes these files (RULE 0)

RULE 0 says: read the public source that *consumes* the file before asserting
anything about its structure. That source exists, and it settles the identity
question outright.

### 1.1 The consumer — kernel side

`drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c`, GPL-2.0-only,
`LineageOS/android_kernel_xiaomi_msm8953` @ `lineage-21`
([source](https://raw.githubusercontent.com/LineageOS/android_kernel_xiaomi_msm8953/lineage-21/drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c),
accessed 2026-11-19). **[S]**

The load path is `cpp_load_fw()`, and it is startlingly thin:

- it requests the file from userspace by name;
- it sends `MSM_CPP_CMD_FW_LOAD` (magnitude `2`) through the command queue;
- it sends `fw->size` and `MSM_CPP_START_ADDRESS` (`0x0`);
- then it streams the payload as `fw->size / 4` little-endian 32-bit words.

**There is no header parse, no magic check, no checksum, and no length field
the kernel reads.** The kernel asserts only that `fw->size` is a multiple of
four (it divides by 4). Everything else about the layout is a property of the
payload, not a contract with the loader.

This is the single most important structural fact in the whole analysis: it
means the `[OPEN]` items below cannot be resolved by reading the kernel, and
it means a free replacement mainly has to satisfy the *microcode's* own
expectations, not the driver's.

`msm_cpp.h` in the same tree supplies the three protocol magic words the
microcode is expected to emit:

| symbol | value |
|---|---|
| `MSM_CPP_MSG_ID_CMD` | `0x3E646D63` |
| `MSM_CPP_MSG_ID_OK` | `0x0A0A4B4F` |
| `MSM_CPP_MSG_ID_TRAILER` | `0xABCDEFAA` |

### 1.2 The producer — userspace side

`mm-camera/mm-camera2/media-controller/modules/pproc-new/cpp/cpp_hardware.c`
and `cpp_hw_params.h`, `Sushrut1101/android_vendor_qcom_proprietary` @
`master`
([source](https://raw.githubusercontent.com/Sushrut1101/android_vendor_qcom_proprietary/master/mm-camera/mm-camera2/media-controller/modules/pproc-new/cpp/cpp_hardware.c),
accessed 2026-11-19). **[S]**

Two things matter here:

- `cpp_hardware_select_fw_version()` maps a hardware version to a firmware
  version. That mapping is reproduced in §7 and it explains the fleet's shape.
- `cpp_hw_params.h` defines the version as a **bitfield**, not a string:
  `CPP_FW_VERSION_*` packs major in bits 31:28, minor in 27:16, step in 15:0.

### 1.3 The refuted hypothesis, recorded honestly

The matrix files this family under `wifi`, and `cpp` reads like a Cypress /
Infineon part prefix. That hypothesis was tested and refuted:

- `linux-firmware` `WHENCE` (537,962 B, fetched 2026-11-19) contains **zero**
  `cpp_firmware` hits. **[M]**
- `brcmfmac/firmware.c` (mainline) implements a `brcmf_fw` name-composition
  scheme with no notion of a `cpp_firmware_vN_N_N.fw` payload. **[S]**
- The files live at `vendor/firmware/` beside `msm_cpp`-consumed siblings, and
  they contain MSM CPP protocol magics — which is decisive.

The `wifi` family label in `sharing-clusters.csv` is therefore a **matrix
labelling error**, not a finding about the bytes. It is not corrected here
(the CSV is outside this work's write scope); it is recorded so the next
person does not re-derive the wrong hypothesis from the label.

---

## 2. Provenance and md5 verification (12/12 MATCH)

Source of truth: `blob-matrix/laptop/sharing-clusters.csv`. Extracting the
`cpp_firmware_*` rows yields **12 identities, not 13** — worth stating because
counting the ladder by eye suggests 13. All twelve are 9-device rows except
`v1_12_1`, which is a 4-device row (`Mi8917;Mi8937;ginkgo;laurel_sprout`).

Every identity was fetched from
`TheMuppets/proprietary_vendor_xiaomi_ginkgo` @ `lineage-22.2`,
`proprietary/vendor/firmware/`, on 2026-11-19. All twelve are **MATCH** — no
NON-DB-IDENTICAL members, no fetch failures.

| file | bytes | md5 (DB = fetched) | status |
|---|---|---|---|
| `cpp_firmware_v1_1_1.fw` | **16,128** | `4d145d5a13a3956bf33aec94a8e7fe62` | **MATCH** |
| `cpp_firmware_v1_1_6.fw` | 16,384 | `738a83a673dd45fa5852b5cc9519ee94` | **MATCH** |
| `cpp_firmware_v1_2_0.fw` | 16,384 | `3f078c3d1658679a762f7d77c99517cd` | **MATCH** |
| `cpp_firmware_v1_4_0.fw` | 16,384 | `b6f54efc4675040f7b7e99398905646e` | **MATCH** |
| `cpp_firmware_v1_5_0.fw` | 16,384 | `e51087ba19409150103faafaff849627` | **MATCH** |
| `cpp_firmware_v1_5_1.fw` | 16,384 | `ed1f2071b61447924f50fe8670cd51be` | **MATCH** |
| `cpp_firmware_v1_5_2.fw` | 16,384 | `02e4044179d7dfc069aa9a42db690642` | **MATCH** |
| `cpp_firmware_v1_6_0.fw` | 16,384 | `de85a5f8196ec73cffc61382b3e0d5f6` | **MATCH** |
| `cpp_firmware_v1_8_0.fw` | 16,384 | `04423a29e78bb01d9be62256a65354a6` | **MATCH** |
| `cpp_firmware_v1_10_0.fw` | 16,384 | `8d08bfdf92db5b1df58af9b6adf61eae` | **MATCH** |
| `cpp_firmware_v1_12_0.fw` | 16,384 | `ef031a3f24f877242621ba695d8dcbd2` | **MATCH** |
| `cpp_firmware_v1_12_1.fw` | 16,384 | `a59e732fcbf71cb5fcc6c54fef0124d6` | **MATCH** |

sha256 of the verified bytes, for future re-download cross-checks:

| file | sha256 |
|---|---|
| 1.1.1 | `09fd81eb95b3187b731c201f99c5b6176df01e6d459c78fbe7bf4f0ef480e578` |
| 1.1.6 | `2533f6819be2ee4ba61ed4e1e8cbf76be93ae9f06d98a5a259fcc6165da47782` |
| 1.2.0 | `6f28bbb64cf8441fc33ee41ffb035f781488fd523b641d237cdaf840769b0689` |
| 1.4.0 | `17446858b9adad536f3da2d0130182708624b87fa0915b9ab719c313865a5674` |
| 1.5.0 | `d8599bbb0bff57b7ac5404f361c8ce72b4b1a1cbd6bf894f3acc67bf5145285f` |
| 1.5.1 | `026c5a88bc6eba3229681fc1ac5b915be674ac9ce36d9c639e9972ad97d2d7cc` |
| 1.5.2 | `7fb5366b1e52a3317d0c840821da5f85359768b9379f517a4271ed1eded552b7` |
| 1.6.0 | `22514c99720c889d4426b291aa5c9648e72901e57efb6e27bd2f90a8f1c1a2cd` |
| 1.8.0 | `f454bfaa137d2b52e235b41a2181f707c5cc421fed261095d39a1b6d852c76cc` |
| 1.10.0 | `59c1a0118f2ebe43a49a442e1273c0a794b059ccb75d6311d67f54db73da9017` |
| 1.12.0 | `9e1618c277f0f686b29a9c85e59911d0a83b81861612892eed1d9a1ba145051d` |
| 1.12.1 | `e95df96697e4de59f9d9b0f4d31179e80e60563b910dad174300990da1376e11` |

### 2.1 Two independent publishers corroborate the set

`LineageOS/android_device_xiaomi_msm8953-common` @ `lineage-19.1`
`proprietary-files.txt` lists **eleven** of the twelve under
`vendor/firmware/` — `v1_12_1` is absent. `trinket-devs/device_xiaomi_ginkgo`
@ `master` lists **all twelve**, including `v1_12_1`. So the twelve-member set
is not an artefact of one vendor tree, and `v1_12_1`'s late arrival (4 devices
vs 9) matches its position at the end of the ladder rather than contradicting
it.

### 2.2 Honest negative

`linux-firmware` does **not** ship this family. F-74-style absence holds here
too, and for the same structural reason: these are per-SoC camera microcode
blobs distributed only inside device vendor partitions.

---

## 3. The 16 KiB layout (measured)

Eleven of the twelve are exactly 16,384 B. `v1_1_1` is 16,128 B — exactly
256 B short — and that is not a fetch error (its md5 matches the DB row whose
`bytes` column says 16128).

The window decomposes as follows. Offsets are shared across the ladder; the
`code_end` boundary moves per version, so the fill region changes length.

```
0x0000            0x0002                                      0x0022
  |--lead word----||--- 16 x u16 vector table -----------------||
                                                               |
                                         code / table region   |
                                                               |
                      code_end (per version, 0x19B6..0x3B02) ---+
                                                               |
                                          0xFF fill (erased)   |
                                                               |
0x3EFC  0x3EFE                                                0x3FCA   0x4000
  |u16---||------------ 204-byte invariant epilogue -----------||0xFF---|
```

### 3.1 Per-file region table

`pad` is `[code_end, 0x3EFE)`; `epilogue` is `[0x3EFE, 0x3FCA)`; `tail pad` is
`[0x3FCA, 0x4000)`. Entropy is the code region's Shannon entropy in bits/byte.

| version | bytes | code_end | pad B | epilogue | entropy | 0xFF% in code |
|---|---|---|---|---|---|---|
| 1.1.1 | **16,128** | `0x3B02` | 1,020 | **ABSENT** | 3.32 | 59.1 |
| 1.1.6 | 16,384 | `0x3B02` | 1,020 | yes | 3.29 | 59.3 |
| 1.2.0 | 16,384 | `0x1B36` | 9,160 | yes | 3.34 | 58.3 |
| 1.4.0 | 16,384 | `0x1AFE` | 9,216 | yes | 3.33 | 58.5 |
| 1.5.0 | 16,384 | `0x1A5E` | 9,376 | yes | 3.31 | 59.0 |
| 1.5.1 | 16,384 | `0x1A5E` | 9,376 | yes | 3.31 | 59.0 |
| 1.5.2 | 16,384 | `0x1B4E` | 9,136 | yes | 3.44 | 57.4 |
| 1.6.0 | 16,384 | `0x19B6` | 9,544 | yes | 3.26 | 59.8 |
| 1.8.0 | 16,384 | `0x3B02` | 1,020 | yes | 3.83 | 50.9 |
| 1.10.0 | 16,384 | `0x2704` | 6,138 | yes | 4.48 | 38.6 |
| 1.12.0 | 16,384 | `0x28D4` | 5,674 | yes | 4.66 | 35.8 |
| 1.12.1 | 16,384 | `0x287C` | 5,762 | yes | 4.62 | 36.4 |

### 3.2 The lead word

`[0x0000, 0x0002)` is `0x7140` in **all twelve** — the only invariant
non-trivial constant outside the epilogue. **[M]**

It is *not* a magic the kernel checks (§1.1): the kernel never looks at it. It
is reported here as a measured constant only.

### 3.3 The u16 vector table `[0x0002, 0x0022)`

Sixteen little-endian `u16` values. Measured properties:

- They are **not all even**. An earlier reading of this table claimed
  "all even"; that was wrong and is corrected here. Parity is *not* invariant:
  slot 15 is odd in 10/12 files, slot 9 in 9/12, slot 0 in 6/12, others in 3–4.
  No slot is odd in all twelve. **[M]**
- **11/12 share one equality pattern**, and it has 6 distinct values: one
  value occupies slot 1 **and** slots 4–8 and 10–14 (11 slots in all), and
  slots 0, 2, 3, 9, 15 each hold their own. `v1_2_0` alone splits slot 10 off
  that block, giving a 7th distinct value. **[M]**
- Every value, doubled, lands **below that file's code_end**. That is
  consistent with halfword offsets into the payload, but the odd slots mean
  the field width (or the doubling) cannot be taken as settled. **[OPEN]**

Values are not reproduced here (they are payload content). The probe reports
them per file, plus the equality pattern and the odd-slot list.

### 3.4 The 0xFF fill

Every pad byte in every file is `0xFF`, never `0x00`. **[M]** This is the
erased-state pattern of NOR flash, and it is the reason whole-file similarity
numbers in §6 are inflated: two files with very different code lengths both
end up mostly `0xFF` in the same high offsets.

Interior `0x00` runs **do** exist (a 472-byte run at `[0x1F4, 0x3CC)` in the
1.10/1.12 family, shorter runs elsewhere) — but those are payload, not
padding. The probe therefore scopes its "zero-fill used" test to the pad
window `[code_end, EOF)`, where the answer is a clean **no** for all twelve.

### 3.5 The 204-byte invariant epilogue `[0x3EFE, 0x3FCA)`

Byte-identical in 11/12 files:

```
sha1 = f81d97b070307896ce03469472c85d6d443a5d15
```

`v1_1_1` does not contain it at all — that file ends at `0x3F00`, i.e. two
bytes *into* the epilogue region `[0x3EFE, 0x3FCA)`, and those two bytes are
`0xFF` fill like the pad before them. Its 256-byte shortfall is exactly the
`[0x3F00, 0x4000)` remainder of the window.

The epilogue carries two ASCII literals and one protocol magic:

| offset | bytes | note |
|---|---|---|
| `0x3F6C` | `4F 4B 0A 0A` | little-endian `MSM_CPP_MSG_ID_OK` (`0x0A0A4B4F`) **[S]** |
| `0x3F80` | `v1.1` | **fixed literal, not a version field** — see §5.2 |
| `0x3FB4` | `cmd>` | part of the same literal cluster |

The `MSM_CPP_MSG_ID_OK` word at `0x3F6C` explains a detail that would otherwise
look arbitrary: every windowed file reports exactly **one** `MSM_CPP_MSG_ID_OK`
hit, and `v1_1_1` reports **zero**. The single hit is this epilogue constant,
not a second emitter in the code region — and `v1_1_1` has no epilogue. So the
"OK" census is a proxy for epilogue presence, not an independent protocol
signal. `MSM_CPP_MSG_ID_TRAILER` does occur in the code region itself (1–11
occurrences, version-dependent) and is a genuine in-code emitter;
`MSM_CPP_MSG_ID_CMD` is 2 in eleven files and 1 in `v1_1_1` (its trailer
records are the epilogue-free variant).

The epilogue's byte mix (`0xFF` ×16, `0x00` ×15, and repeated
instruction-looking 16-bit words such as `21 60`, `A1 60`, `27 60`, `A0 60`,
`10 80`, `30 60`) is consistent with a small fixed code stub, which is why a
naive "all-fill run" census splits the block into several sub-runs. `21 60`
and `A1 60` each occur three times in the 204 bytes, `27 60` four times.
Its semantics remain **[OPEN]**.

### 3.6 The `u16` at `0x3EFC` is a halfword length field

This is the strongest structural contract found in the family, and it was not
in the earlier structural sketch. **[M]**

```
code_end == 2 * (u16@0x3EFC + 1)
```

| version | `u16@0x3EFC` | `2*(w+1)` | `code_end` | residual |
|---|---|---|---|---|
| 1.1.1 | `0xFFFF` | `0x20000` | `0x3B02` | erased |
| 1.1.6 | `0xFFFF` | `0x20000` | `0x3B02` | erased |
| 1.2.0 | `0x0D9A` | `0x1B36` | `0x1B36` | **0** |
| 1.4.0 | `0x0D7E` | `0x1AFE` | `0x1AFE` | **0** |
| 1.5.0 | `0x0D2E` | `0x1A5E` | `0x1A5E` | **0** |
| 1.5.1 | `0x0D2E` | `0x1A5E` | `0x1A5E` | **0** |
| 1.5.2 | `0x0DA6` | `0x1B4E` | `0x1B4E` | **0** |
| 1.6.0 | `0x0CDA` | `0x19B6` | `0x19B6` | **0** |
| 1.8.0 | `0xFFFF` | `0x20000` | `0x3B02` | erased |
| 1.10.0 | `0x1329` | `0x2654` | `0x2704` | **176** |
| 1.12.0 | `0x1411` | `0x2824` | `0x28D4` | **176** |
| 1.12.1 | `0x13E5` | `0x27CC` | `0x287C` | **176** |

Three observations:

1. **It is a region length, not the file length.** `2*(w+1)` never equals
   16,384 for any populated file. So it describes the payload's own extent, and
   the 16 KiB window is a *container* size imposed outside the payload.
2. **Three identities leave it erased** (`0xFFFF`): 1.1.1, 1.1.6, 1.8.0. These
   are exactly the three whose code_end is `0x3B02`. **[OPEN]** why that
   generation does not populate the field; plausibly a format revision, but the
   public producer source does not show it.
3. **Three identities have a 176-byte residual**: 1.10.0, 1.12.0, 1.12.1. In
   each, the 176 bytes after `2*(w+1)` are a fixed-stride table:

   ```
   14-byte prologue
   8 x 20-byte record:
       [+0,  +12)  12-byte body  — identical in all 8 records
       [+12, +14)  u16 advancing by 0x0A per record
       [+14, +16)  u16 advancing by 8    per record (0x0700, 0x0708, ...)
       [+16, +20)  4-byte constant 00 80 20 64
   2-byte tail  01 70
   ```

   `14 + 8*20 + 2 = 176`. All three identities decode identically: 8 records,
   all bodies identical, `a_step` `0x0A`, `b_step` `8`. That is a counted
   table appended after the length-described region, which is why the field
   cannot simply be `code_end/2 - 1` for those three. Semantics **[OPEN]**.

The kernel never reads this field (§1.1), so it is a payload-internal
structure, not a loader contract.

### 3.7 Interior zero table

All twelve contain a long interior `0x00` run inside the code region — 284 to
472 bytes depending on version. It is payload (a zeroed table), and for that
reason the earlier draft's "`zero_fill_used`" flag (which tested the whole
file) was a false positive for every real file. It is now scoped correctly.

---

## 4. Invariant vs varying, by range

Over the twelve-file common prefix (16,128 B = `0x3F00`), counting positions
where all twelve agree and are not `0xFF`. The last two rows lie beyond that
prefix, so they are computed over the eleven full-window files only — their
scope is called out in the note below the table.

| range | bytes | invariant | `0xFF` | varying | scope |
|---|---|---|---|---|---|
| `[0x0000, 0x0022)` header | 34 | 2 | 0 | 32 | 12 files |
| `[0x0022, 0x19B6)` shared-code window | 6,548 | 35 | 2 | 6,511 | 12 files |
| `[0x19B6, 0x3B02)` version-specific | 8,524 | 0 | 354 | 8,170 | 12 files |
| `[0x3B02, 0x3EFE)` pad | 1,020 | 0 | 1,018 | 2 | 12 files |
| `[0x3EFE, 0x3FCA)` epilogue | 204 | 204 | 0 | 0 | 11 files |
| `[0x3FCA, 0x4000)` tail pad | 54 | 0 | 54 | 0 | 11 files |

The epilogue row is the 11-file result. In the strict 12-file intersection it
collapses to the 2-byte slice `[0x3EFE, 0x3F00)`, which is `0xFF` in all
twelve, because `v1_1_1` ends at `0x3F00` and carries no epilogue at all — a
good illustration of why a whole-fleet "invariant" test can undercount a real
204-byte invariant (§3.5).

The table makes the honest picture obvious: **almost nothing is invariant**.
Only 37 non-fill bytes hold the same value across all twelve, and 35 of those
are zero bytes scattered through `[0x019F, 0x02B7]`. They are **not** a
contiguous run: 30 are the most-significant byte of an aligned 32-bit
little-endian word in the small-value/offset table spanning
`0x019C–0x02B4` (so those 30 words are all `< 2^24` in every file), and the
other 5 are single zero bytes at `0x1DD, 0x1E1, 0x1ED, 0x1F1, 0x1F9`, inside
the trailer/command record cluster. The remaining two invariant bytes are the
`0x7140` lead word. Everything that identifies a version lives in the varying
bytes. **This is a microcode family, not a header format with a version field
bolted on.**

---

## 5. The version story

### 5.1 Filename version = the public bitfield

`cpp_hw_params.h` defines the version as a bitfield: **31:28 major, 27:16
minor, 15:0 step**. **[S]** Applying it:

| filename | `CPP_FW_VERSION_*` |
|---|---|
| 1.1.1 | `0x10010001` |
| 1.1.6 | `0x10010006` |
| 1.2.0 | `0x10020000` |
| 1.4.0 | `0x10040000` |
| 1.5.0 | `0x10050000` |
| 1.5.1 | `0x10050001` |
| 1.5.2 | `0x10050002` |
| 1.6.0 | `0x10060000` |
| 1.8.0 | `0x10080000` |
| 1.10.0 | `0x100A0000` |
| 1.12.0 | `0x100C0000` |
| 1.12.1 | `0x100C0001` |

Note `1.10` → minor `0x00A`, so the enum value is `0x100A0000`, not a decimal
concatenation. The fixtures' synthetic images carry these words so the probe's
name→enum mapping is exercised — but **no real file contains its own enum
word** as a version field: searching `v1_5_0` for `0x10050000` yields zero
hits. Only 1.1.1, 1.1.6 and 1.6.0 contain their enum value anywhere, and in
each case it is the 32-bit word formed by the marker plus the build counter
(§6.3) reading `0x2B7C`, `0x0CB4`, `0x0100` — i.e. the three files whose
adjacent counter happens to equal the filename step (1, 6, 0). The enum is a
*userspace* identifier; the payload does not carry it. **[M]**

### 5.2 The in-file marker: `0x1000 | BCD(minor)`

Every one of the twelve files contains **exactly one** 16-bit little-endian
word of the form `0x1000 | BCD(minor)`:

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
| 1.10.0 | `0x1010` | `0x01F2`, **`0x247A`** |
| 1.12.0 | `0x1012` | `0x01F2` |
| 1.12.1 | `0x1012` | `0x01F2` |

The `1.10.0` double hit is worth being precise about, because it looks like a
second version field and is not one. The second occurrence sits at the head of
an eight-`u16` **offset table** at `0x246A`:

```
0x246a: 80 10  c8 10  34 11  66 11  a2 11  06 0b  ba 11  e4 11
        └────── eight u16 code offsets, all landing inside the code region
0x247a: 10 10  <- the second 0x1010, i.e. table slot 8 read as a marker
```

Doubled, those values are `0x2100, 0x2190, 0x2268, 0x22CC, 0x2344, 0x160C,
0x2374, 0x23C8` — all inside the code region, and the `0x160C` slot is the
outlier that makes the table look irregular. The coincidence is that this
particular table's ninth `u16` happens to equal the version marker. `1.12.0`
and `1.12.1` carry no such table at that offset (`0x246A` holds ordinary code),
which is why they report a single hit. The probe deliberately reports **all**
offsets rather than asserting uniqueness, precisely so this cannot be
mistaken for a second version field.

Two design details fall out:

- **BCD, not binary.** `1.10` encodes as `0x1010`, not `0x100A`. Without BCD,
  minor 10 would collide with... nothing, actually — but BCD does prevent
  `1.10` from being read as `1.1` by a decimal-minded parser, and it makes the
  field visually match the filename. It also means that if a reader assumes
  the payload's marker and the public `CPP_FW_VERSION_*` constant encode the
  same way, `1.10`/`1.12` will be misread — the constant packs minor as a
  plain binary field (`0x00A`, `0x00C`), the payload as BCD.
- **The marker sits immediately below a `MSM_CPP_MSG_ID_TRAILER` record.** The
  marker offset minus the nearest preceding trailer offset is `+14` in 10/12
  files and `+10` in exactly two: 1.5.0 and 1.5.1. It is *not* an
  old/new-template split — 1.5.2 and 1.6.0, which sit between 1.5.1 and 1.10.0
  in the ladder, are back at `+14`, as are 1.10.0/1.12.x. **[M]** The
  relationship is still positional rather than coincidental (the version word
  is a field of a trailer-terminated command record), but the two `+10` files
  are a local variant, not a generation boundary.

### 5.3 The ASCII decoy at `0x3F80`

`strings` on any of the eleven windowed files finds `v1.1`. It is **not** a
version field:

- it is present in 11/12 files — including 1.12.0 and 1.12.1;
- its offset is fixed (`0x3F80`), inside the invariant epilogue;
- the byte immediately before it is `0xFF` and the byte after it is `0x8D`, so
  it is an exact printable run, not part of a longer string.

It is a literal of the shared microcode epilogue. The probe reports both facts
(`self_version_string_present: false`, plus the literal's offset and
classification) so the distinction cannot be lost in a future reading.

**Honest negative: no file carries its own version as ASCII text.** The
numeric marker of §5.2 is the only self-identification, and it encodes minor
only — major and step are not recoverable from the payload by this rule alone.
The step difference between 1.5.0 and 1.5.1 is two bytes of code (§6.2), not a
marker change.

---

## 6. The N×N version matrix

Three matrices are computed, because for a padded fixed-window format one
number is misleading:

- **`matrix_whole`** — same-offset byte equality over the common prefix.
- **`matrix_code_region`** — same equality restricted to `min(code_end)`.
- **`matrix_content_only`** — equality over positions where *neither* side is
  `0xFF` or `0x00`; this is the honest similarity number.

### 6.1 Whole-file identity (%)

Rows and columns in ladder order. Diagonal omitted.

|  | 1.1.6 | 1.2.0 | 1.4.0 | 1.5.0 | 1.5.1 | 1.5.2 | 1.6.0 | 1.8.0 | 1.10.0 | 1.12.0 | 1.12.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1.1.1** | 26.21 | 22.22 | 22.25 | 23.26 | 23.26 | 22.35 | 23.90 | 15.87 | 10.78 | 10.90 | 10.82 |
| **1.1.6** | | 64.48 | 62.65 | 63.96 | 63.96 | 62.85 | 63.48 | 56.76 | 43.62 | 40.69 | 41.24 |
| **1.2.0** | | | 65.37 | 64.18 | 64.18 | 62.31 | 64.08 | 56.37 | 43.56 | 40.57 | 41.17 |
| **1.4.0** | | | | 64.12 | 64.13 | 63.20 | 64.20 | 56.88 | 43.78 | 40.59 | 40.97 |
| **1.5.0** | | | | | **99.99** | 65.36 | 67.24 | 58.39 | 44.89 | 42.18 | 42.35 |
| **1.5.1** | | | | | | 65.37 | 67.24 | 58.39 | 44.89 | 42.18 | 42.35 |
| **1.5.2** | | | | | | | 65.33 | 59.34 | 45.73 | 42.40 | 43.10 |
| **1.6.0** | | | | | | | | 58.53 | 45.39 | 42.18 | 42.58 |
| **1.8.0** | | | | | | | | | 48.55 | 45.17 | 46.14 |
| **1.10.0** | | | | | | | | | | 50.10 | 50.65 |
| **1.12.0** | | | | | | | | | | | 61.06 |

### 6.2 Content-only identity (%), the honest measure

|  | 1.1.6 | 1.2.0 | 1.4.0 | 1.5.0 | 1.5.1 | 1.5.2 | 1.6.0 | 1.8.0 | 1.10.0 | 1.12.0 | 1.12.1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **1.1.1** | 89.22 | 20.14 | 10.24 | 6.40 | 6.40 | 8.37 | 4.35 | 2.90 | 2.57 | 4.22 | 3.45 |
| **1.1.6** | | 14.98 | 8.16 | 8.18 | 8.18 | 6.73 | 7.35 | 7.16 | 5.55 | 5.19 | 5.19 |
| **1.2.0** | | | 13.23 | 12.35 | 12.35 | 8.23 | 11.11 | 8.31 | 8.09 | 7.52 | 7.72 |
| **1.4.0** | | | | 10.83 | 10.85 | 10.81 | 10.56 | 9.80 | 8.63 | 7.35 | 6.79 |
| **1.5.0** | | | | | **99.97** | 13.95 | 15.14 | 11.44 | 9.39 | 9.76 | 8.66 |
| **1.5.1** | | | | | | 13.96 | 15.14 | 11.44 | 9.39 | 9.76 | 8.66 |
| **1.5.2** | | | | | | | 14.55 | 12.13 | 9.95 | 8.45 | 8.95 |
| **1.6.0** | | | | | | | | 11.87 | 11.00 | 9.94 | 9.52 |
| **1.8.0** | | | | | | | | | 13.42 | 12.22 | 13.32 |
| **1.10.0** | | | | | | | | | | 14.90 | 14.93 |
| **1.12.0** | | | | | | | | | | | 32.95 |

The padding inflation is large and systematic: 1.5.0↔1.6.0 is **67.24** whole
but **15.14** content. Any conclusion drawn from the whole-file number alone
is wrong by a factor of four.

**One caveat about the `1.1.1` row, stated so it is not over-read.** Its
`89.22` against `1.1.6` rests on only **334** eligible positions. The reason
is that the two files' erase windows are almost exactly complementary:
`v1_1_1` is **100% `0xFF`** through `[0x02C4, 0x2204)` while `v1_1_6` is
**100% `0xFF`** through `[0x2204, 0x3B00)`. Every position in either span
therefore has one side at fill, and nothing there survives the "neither side
is fill or zero" filter. The 334 survivors sit in `[0x0000, 0x0198)` (329 of
them, the shared code prologue), plus 3 bytes in `[0x0198, 0x02C4)` and 2 at
`0x3B00`. 298 of those 334 match, and the differences are exactly three runs:
the 32-byte vector table (`[0x0002, 0x0022)`), one 2-byte spot at `0x02C0`,
and a 2-byte word at `0x3B00`. So "1.1.1 is 89% identical to 1.1.6" means
"the tiny part of both files that is neither fill nor zero agrees 89% of the
time" — consistent with them being siblings, but not comparable in weight to
the 5,903-position comparison behind 1.5.0↔1.5.1. The probe reports the
denominator (`positions`) alongside every cell for this reason.

### 6.3 Adjacent-version first diff

| pair | common span | differing B | runs | first diff |
|---|---|---|---|---|
| 1.1.1 → 1.1.6 | 16,128 | 11,901 | 175 | `0x0002` |
| 1.1.6 → 1.2.0 | 16,384 | 5,820 | 577 | `0x0002` |
| 1.2.0 → 1.4.0 | 16,384 | 5,674 | 464 | `0x0002` |
| 1.4.0 → 1.5.0 | 16,384 | 5,878 | 481 | `0x0002` |
| **1.5.0 → 1.5.1** | 16,384 | **2** | **2** | `0x0034` |
| 1.5.1 → 1.5.2 | 16,384 | 5,674 | 508 | `0x0002` |
| 1.5.2 → 1.6.0 | 16,384 | 5,680 | 558 | `0x0002` |
| 1.6.0 → 1.8.0 | 16,384 | 6,795 | 526 | `0x0002` |
| 1.8.0 → 1.10.0 | 16,384 | 8,429 | 690 | `0x0002` |
| 1.10.0 → 1.12.0 | 16,384 | 8,176 | 673 | `0x0002` |
| 1.12.0 → 1.12.1 | 16,384 | 6,380 | 387 | `0x0002` |

**The 1.5.0 → 1.5.1 pair is the anomaly, and it is the most informative row in
this document.** Exactly two bytes differ:

| offset | 1.5.0 | 1.5.1 | context |
|---|---|---|---|
| `0x0034` | `0x58` | `0x08` | inside the code region, in a run of `u16` immediates |
| `0x00C4` | `0x10` | `0x02` | low half of the 32-bit word that carries the version marker |

The second byte deserves care, because the obvious reading of it is wrong.
`0x00C4` is at marker offset `0x00C6` **minus 2**, i.e. it is the *low* `u16`
of the same little-endian 32-bit word whose high `u16` is the `0x1005` marker.
This fleet contains **no** `CPP_FW_VERSION_*` enum word — the values
`0x10010001`…`0x100C0001` never appear as a version field (`v1_5_0`'s own enum
`0x10050000` has zero hits in `v1_5_0`). So `0x00C4` is a build counter
adjacent to the marker, not the step digit: it reads `0x10` in 1.5.0 and
`0x02` in 1.5.1 while the filename step goes 0→1, and it disagrees with the
filename step in **9 of the 12 files** — the only three where it agrees are
1.1.1 (`0x01`), 1.1.6 (`0x06`) and 1.6.0 (`0x00`), i.e. precisely the three
files whose enum value happens to appear in the payload at all (§5.1).
**[M]** Its semantics are **[OPEN]**; what is established is only that it
moves when the build moves.

So a **step bump is a two-byte change**: one code byte plus one byte of the
marker's own word. This is still the cleanest evidence that the ladder is a
genuine code lineage with in-band identification — it just isn't evidence of a
step field, because there is no step field to bump.

**1.12.0 → 1.12.1 is the opposite extreme**: 6,380 differing bytes, only 32.95
content identity. A step bump that is a near-total rewrite means the "step"
digit is not a semantic patch level — it is a build revision, and 1.12.1 was a
substantive rework. Note also that 1.12.1 ships to only 4 devices while 1.12.0
ships to 9; a rework that did not roll out fleet-wide is consistent with that.

### 6.4 Clustering

Threshold-clustering on the whole-file matrix:

| threshold | clusters |
|---|---|
| ≥70% | `{1.1.1}`, `{1.1.6}`, `{1.2.0}`, `{1.4.0}`, `{1.5.0, 1.5.1}`, `{1.5.2}`, `{1.6.0}`, `{1.8.0}`, `{1.10.0}`, `{1.12.0}`, `{1.12.1}` |
| ≥60% | `{1.1.1}`, `{1.1.6 … 1.6.0}`, `{1.8.0}`, `{1.10.0}`, `{1.12.0, 1.12.1}` |
| ≥50% | `{1.1.1}`, `{1.1.6 … 1.8.0}`, `{1.10.0, 1.12.0, 1.12.1}` |

Verdict: **clustering is monotone in semantic version distance.** The
`{1.1.6 … 1.6.0}` block, the `{1.10.0, 1.12.0, 1.12.1}` block, and the isolated
`1.1.1` and `1.8.0` are exactly what a version-ordered lineage with two
structural jumps should produce. Version sort order **does** match byte-identity
clustering — worth stating explicitly because it is the assumption most likely
to fail, and here it holds.

`1.1.1` is the structural outlier throughout (content identity 2.57–20.14
against everything, 89.22 only against 1.1.6, and it is the only file that
lacks the epilogue and is 256 B short).

**No file is a byte-prefix of another.** Checked explicitly. The 16 KiB window
is filled independently per version, not by extending an older image.

---

## 7. Which hardware gets which firmware

From `cpp_hardware_select_fw_version()` **[S]**:

| hardware version | firmware |
|---|---|
| 1.1.x, 2.0.0 | 1.2.0 |
| 4.0.0, 4.2.0 | 1.4.0 |
| 4.1.0 | 1.6.0 |
| 4.3.2, 4.3.3, 4.3.4 | 1.5.0 |
| 4.3.0 | 1.5.1 |
| 5.0.0, 5.1.0 | 1.8.0 |
| 6.0.0 | 1.10.0 |
| 6.1.0, 6.1.2 | 1.12.0 |
| 6.1.4 | 1.12.1 |

The mapping is **non-monotone in one place, and the exception is real**:
hardware 4.3.0 (MSM8952) takes 1.5.1, while 4.3.3 (MSM8953) takes 1.5.0. A
newer hardware minor gets an *older* firmware minor. Since the 1.5.0→1.5.1
delta is those two bytes (§6.3), 1.5.1 is a targeted fix for the MSM8952
variant, not a general successor. Anyone building a version-choice table from
"higher hardware ⇒ higher firmware" will get 4.3.x wrong.

This also explains the fleet's device counts: nine devices share the same
eight-plus firmware identities because they share the same CPP hardware
generations, and `v1_12_1` (4 devices) is the newest hardware 6.1.4 population.

---

## 8. Cross-fleet verdict

### 8.1 vs F-75 (`cr*`/`ap*` QCA BT, gen 1)

| aspect | F-75 (QCA BT gen 1) | this family (MSM CPP) |
|---|---|---|
| declared length | `4 + 24 + data_length + 256` | **none declared**; `u16` at `0x3EFC` counts a region, not the file |
| container magic checked by loader | yes (TLV type) | **no** — kernel streams words blindly |
| size | 1,243 – 56,180 B (variable) | **fixed 16 KiB window** (one 16,128 B outlier) |
| filename digit meaning | ROM build targeted (a *target* id) | true semantic `major.minor.step` |
| version in file | header `patch_version` = format rev, not the filename digit | numeric marker `0x1000\|BCD(minor)` (+ adjacent build counter) |
| padding | 256-byte signature-class tail | `0xFF` erase fill in a padded window |
| kernel validates | container framing, segments | nothing but word alignment |

Three distinct philosophies now on record across the programme: F-75's
`4 + 24 + data_length + 256`, gen-2's `4 + 32 + data_length + 36`
(see `implementations/qca-bt-gen2/fleet-analysis.md`), and CPP's **padded
fixed window with no length field at all**. CPP is the odd one out in the
strongest sense: the other two are *self-describing* containers, CPP is a
*placed* image whose only length signal is a payload-internal `u16` the loader
ignores.

The filename-semantics inversion is the finding worth carrying forward: in F-75
the filename digit **misleads** (it names a target ROM, and the same ROM build
appears under two different digits for different chips), whereas in CPP the
filename **is** the bitfield value, verifiable against a public header and
against a marker word inside the payload. F-75 taught "don't trust the
filename digit"; CPP teaches "here the filename digit is trustworthy, but the
`v1.1` string inside the file is not." Both are traps, in opposite directions.

### 8.2 vs the ADSP `bm2n` fleet

Superficial similarity (fixed vendor path, Qualcomm, per-variant family) but
nothing structural in common: `bm2n` is a serialized QNN/HTP object graph with
a real load header and record grammar; CPP is position-dependent microcode in
an erased-flash window with no in-band grammar beyond the trailer records.

---

## 9. What this means for a free reimplementation

**Writable today, with zero proprietary bytes:**

- The loader side is *trivial*: `cpp_load_fw()` semantics are fully specified by
  GPL source and need no reverse engineering. Send `MSM_CPP_CMD_FW_LOAD`, send
  size and `MSM_CPP_START_ADDRESS` 0, stream `size/4` LE words.
- The window contract: any replacement payload must be a multiple of 4 bytes;
  the fleet's own convention is a 16,384-byte window (16,128 seen once). A
  free build can pick its own size as far as the kernel is concerned.
- The version-reporting convention is now known: to look like this family, a
  free image should carry `0x7140` at `0x0000`, a `0x1000|BCD(minor)` marker
  word inside the code region, and the three `msm_cpp.h` magic words so the
  protocol handshake can complete.

**Opaque — needs synthesis or further RE:**

- The code region itself (`[0x0022, code_end)`), 3.3–4.7 bits/byte, 35–60%
  `0xFF` interleaved. It is microcode for an undocumented CPP core. Its ISA is
  **[OPEN]**; no disassembly was performed and none is claimed.
- The 204-byte invariant epilogue. It is byte-identical across 11/12 files,
  which makes it a *constant* a free build could carry verbatim only if its
  semantics were known — they are not. **[OPEN]**
- The 176-byte fixed-stride block in 1.10.0/1.12.x. 14 B prologue + 8 × 20 B
  records + 2 B tail; the 12-byte record body is identical in all 8, with two
  `u16` counters advancing by `0x0A` and `8`. Counted table, semantics
  **[OPEN]**.
- Whether the core verifies anything at all. No checksum was found: crc32,
  sum32, and 16-bit halfword sums over the code region do not match any
  trailer field in any file. **[OPEN]** — but the kernel certainly does not
  verify anything (§1.1), so any verification would be core-side.

---

## 10. `[OPEN]` register

| # | question | range | why it is still open |
|---|---|---|---|
| 1 | semantics of the 16×`u16` vector table | `[0x0002, 0x0022)` | undocumented in public source; odd slots refute a plain halfword-offset read |
| 2 | semantics of the 204-byte invariant epilogue | `[0x3EFE, 0x3FCA)` | byte-identical but unexplained; contains `v1.1` and `cmd>` literals |
| 3 | why 1.1.1/1.1.6/1.8.0 leave the length `u16` erased and use `code_end` 0x3B02 | `0x3EFC` | no public source shows the format revision |
| 4 | semantics of the 176-byte fixed-stride block | 1.10.0/1.12.x, after `2*(w+1)` | measured stride only |
| 5 | why 1.1.1 is 256 B short and lacks the epilogue | whole file | one-off; no sibling to compare |
| 6 | microcode ISA / core architecture | `[0x0022, code_end)` | no disassembly performed, none claimed |
| 7 | does the core verify a checksum? | whole payload | crc32/sum32/halfword sums tested, no match |
| 8 | why 1.12.0→1.12.1 is a near-total rewrite while 1.5.0→1.5.1 is 2 bytes | — | build process question, not a byte question |
| 9 | does anything consume the `0x7140` lead word? | `0x0000` | kernel does not; core-side unverified |
| 10 | what the build counter beside the marker means (and why it disagrees with the filename step in 9/12 files) | `marker-2` | measured to move with the build; no public source names it |

---

## 11. Scratch artefacts (regeneratable)

- `/tmp/astro_u/cpp/payloads/`, `/tmp/astro_u/cpp/real/` — the twelve verified
  payloads (**never committed**).
- `/tmp/astro_u/cpp/analysis/matrix.json`, `summary.json` — probe output.
- `/tmp/astro_u/cpp/{msm_cpp.c,msm_cpp.h,cpp_hardware.c,cpp_hw_params.h,cpphw.h,WHENCE,brcm_fw.c}`
  — the public sources quoted above, as fetched on 2026-11-19.

Everything in this document is reproducible with:

```
python3 implementations/wifi-cpp-fleet/cpp_probe.py --matrix <12 paths> --json m.json
python3 implementations/wifi-cpp-fleet/cpp_probe.py --versions <12 paths> --brief
```
