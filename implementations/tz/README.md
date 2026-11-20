# `tz` — replace or interoperate with the blob: what open-source actually exists

**Clean-room statement.** This document contains no proprietary code, headers,
strings or payload. Its sources are the public GPL kernel tree
(`torvalds/linux`), public kernel documentation, a BSD-3-Clause GitHub
repository, and this repository's own committed research. No TA image was
disassembled and no vendor binary was read to produce it. This component ships
**documentation only — there is no code and therefore no self-test**; the
self-test requirement in `implementations/README.md` applies to parsers, not to
a usage/decision note.

Issue #2048. Evidence classed [F] fact / [I] inference / [H] hypothesis /
[N] negative. Every kernel reference verified against `torvalds/linux` master
on **2026-11-20**.

## 0. Answer up front

**You cannot replace `tz.img`. You can now interoperate with it from fully free
software, which was not true when this repo last checked.**

The TrustZone OS image is a signed Qualcomm build; nothing free replaces it, and
nothing free will, because its job is to be the thing the signature attests.
But the *access path* — talking to QTEE and invoking its loaded Trusted
Applications — is now **in-tree mainline code** plus a **BSD-3 userspace
library**. That is a genuine end-to-end free path, and this repo does not
mention it anywhere.

| question | answer |
|---|---|
| Can free software replace `tz.img`? | **No** — signed blob, no free substitute exists [F] |
| Can free software invoke TAs? | **Yes** — `CONFIG_QCOMTEE` + generic TEE API + `libqcomtee` (BSD-3) [F] |
| Does it load TA images from files? | **No** — it accesses TAs QTEE already has [F] |
| Does it verify those images? | **No** — no `request_firmware` call anywhere in the driver [F, N] |
| Is the lab's census work invalidated? | **No** — it analyses bytes; `qcomtee` does not read bytes [F] |

## 1. The correction: a load-bearing in-repo claim is now stale

`research/qualcomm/docs/userspace-vs-firmware-split.md:48` states, as verified
2026-11-17:

> "mainline QSEECOM is the **client-registration layer** … the Android-style
> driver that *loads* arbitrary TA images (`qseecom_load_app`) is **not** in
> torvalds master (`drivers/tee/qcom/qseecom.c`: 404 checked 2026-11-17)"

**The 404 is still true today** — I re-checked it (2026-11-20, still 404) [F].
**The conclusion drawn from it is not.** Mainline gained a separate driver that
the note never mentions [F]:

```
drivers/tee/Kconfig:23     source "drivers/tee/qcomtee/Kconfig"
drivers/tee/qcomtee/       Kconfig, Makefile, core.c, call.c, async.c,
                           shm.c, mem_obj.c, primordial_obj.c, user_obj.c,
                           qcomtee.h, qcomtee_msg.h, qcomtee_object.h
                           (12 files, 111,456 B)
```

`drivers/tee/qcomtee/Kconfig` [F]:

```
config QCOMTEE
	tristate "Qualcomm TEE Support"
	depends on ARCH_QCOM || COMPILE_TEST
	depends on !CPU_BIG_ENDIAN
	select QCOM_SCM
	select QCOM_TZMEM_MODE_SHMBRIDGE
	help
	  This option enables the Qualcomm Trusted Execution Environment (QTEE)
	  driver. It provides an API to access services offered by QTEE and
	  its loaded Trusted Applications (TAs).
```

That help text is the whole point: **"access services offered by QTEE and its
loaded Trusted Applications"**. The repo's note says no such path exists. It
does, and it is upstream.

### 1.1 Why the old note was reasonable when written

`qcomtee` is not the vendor `qseecom` driver. It does not live at
`drivers/tee/qcom/qseecom.c`, does not implement `qseecom_load_app`, and does
not have a DT binding. Someone looking precisely for `qseecom` would find the
404 and stop [I]. The search was right; the target moved.

## 2. What `qcomtee` is — the transport

The driver does **not** create a device from the device tree. It is probed by
SCM and self-registers [F]:

```c
/* drivers/firmware/qcom/qcom_scm.c:2489-2498 */
ret = qcom_scm_qtee_invoke_smc(0, 0, 0, 0, &result, &response_type);
if (ret == -EIO)
	return;
qtee_dev = platform_device_register_data(scm->dev, "qcomtee",
					 PLATFORM_DEVID_NONE, NULL, 0);
```

The probe is a deliberate **invalid** call: a buffer error proves the SMC
handler exists, while `-EIO` means the secure world does not implement
`smcinvoke` at all [F]. So `qcomtee` appears automatically on any SoC whose
QTEE supports it — there is nothing to enable in a `.dts` [I].

The SCM ABI, exact from `drivers/firmware/qcom/qcom_scm.h:163-166` [F]:

```
QCOM_SCM_SVC_SMCINVOKE            0x06
QCOM_SCM_SMCINVOKE_INVOKE_LEGACY  0x00
QCOM_SCM_SMCINVOKE_CB_RSP         0x01
QCOM_SCM_SMCINVOKE_INVOKE         0x02
```

The message layer is `qcomtee_msg.h`, which documents two shared buffers [F]:

- **inbound** buffer — direct invocation (kernel → QTEE object operation)
- **outbound** buffer — callback requests (QTEE → non-secure object), with the
  unused tail used for asynchronous messages
- four argument types: **IO** (input object), **OO** (output object),
  **IB** (input buffer), **OB** (output buffer); buffers are `(offset, size)`
  pairs into the two shared regions

Memory for those buffers comes from **SHM Bridge**, forced by
`select QCOM_TZMEM_MODE_SHMBRIDGE` — which is why the driver cannot be built
with the plain generic allocator [F].

## 3. How to actually use it

```sh
# 1. kernel
CONFIG_QCOMTEE=y            # implies QCOM_SCM + QCOM_TZMEM_MODE_SHMBRIDGE
# appears as /dev/tee0 automatically; no device-tree change

# 2. userspace client
git clone https://github.com/quic/quic-teec   # BSD-3-Clause, provides libqcomtee
# link against it and use the generic TEE API (TEE_IOC_* ioctls)
```

The stack, bottom-up [F]:

```
Client  (your app)                    <- generic TEE API
  |  TEE_IOC_* ioctls
QTEE driver (drivers/tee/qcomtee)     <- in-tree, QCOMTEE
  |  qcomtee_msg  (inbound/outbound, IO/OO/IB/OB)
  |  SMCCC  QCOM_SCM_SMCINVOKE_*
SCM  (drivers/firmware/qcom/qcom_scm.c)
  |
QTEE  (secure world, the signed tz.img)
```

## 4. What it does **not** do — the boundary that matters here

This is the part no single source states plainly, and it is why the lab's
existing work remains valid.

- **No image loading.** `grep -n "request_firmware\|load_app\|\.mdt"` over the
  driver's `core.c` and `qcomtee_msg.h` returns **only** the `#include` of
  `qcom_scm.h` — no firmware-loading call at all [F]. `qcomtee` talks to TAs
  that QTEE already hosts. It does not take a `tz.img`, a `.mdt`, or a `.bXX`
  and load it [F, N].
- **No image verification.** Nothing in the driver reads or validates a TA
  image [F, N].
- **Not the vendor loader.** `drivers/tee/qcom/qseecom.c` is still 404 in
  master (re-checked 2026-11-20) [F]. `qseecom_load_app` exists only in the
  out-of-tree vendor driver, e.g.
  `android.googlesource.com/kernel/msm/.../drivers/misc/qseecom.c` [F].

So the honest split is:

| layer | free replacement? |
|---|---|
| TrustZone images (`tz.img`, `hyp.img`, `keymaster.img`, TA `.mdt`) | **no** — signed, replaceable only by Qualcomm/OEM |
| TA **loading** from those files | **no** — vendor-kernel only (`qseecom_load_app`) |
| TA **invocation** at runtime | **yes** — `qcomtee` + `libqcomtee` [F] |
| TA **analysis** (structure, segment map, strings) | **yes** — this lab's own census tooling |

## 5. Why the census work is unaffected

The `tz` family is **4,264 rows / 87 devices / 171 distinct filenames /
665,173,154 B** in the matrix [F]. The filenames split into two shapes that
`qcomtee` does nothing about [F]:

| shape | example (rows) | rows | distinct filenames |
|---|---|---:|---:|
| monolithic `.img` | `tz.img` (63), `devcfg.img` (63), `hyp.img` (63), `keymaster.img` (63), `uefisecapp.img` (61) | **401** | 11 |
| split TA `.mdt` + `.bXX` | `hdcpsrm.mdt` (48), `featenabler.mdt` (46), `soter64.mdt` (46), `soter64.b00`/`.b01` (46 each) | **3,859** | 158 |

Together those are 4,260 of the 4,264 `tz` rows; the remaining 4 rows are
`tmel_peach_10.elf` / `tmel_peach_20.elf` [F]. So the split `.mdt`/`.bXX` shape
dominates this family by almost 10:1 over the monolithic `.img` shape — the
opposite of the FP6 (`research/qualcomm/docs/trustzone-census.md`), where
TrustZone ships as monolithic AArch64 ELF partitions with no `.mdt` split at
all [F].

`qcomtee` reads neither. It calls into an already-running QTEE. So
`research/fleet/dsp-tz-map.md` and `research/fleet/qsee-crossgen.md` — the ELF
segment maps, the 256-byte signature blocks, the `seg[10]` entropy question —
remain exactly as valid as before [F]. **This issue changes the runtime story,
not the byte story.**

## 6. Honest negatives

1. **I could not re-measure any image.** The payloads those notes reference
   (`data-fetch/enchilada/tz.img`, `analysis/out/qsee-crossgen.json`, the
   `/tmp/dsp-ext4` extract) are **not present in this checkout** — the repo was
   re-cloned and the fetch/analysis directories are gone [F, N]. Everything I
   say about image bytes is quoted from the committed notes, not re-derived.
2. **I did not run `qcomtee`.** No ARM64 device with an `smcinvoke`-capable
   QTEE was available, so the usage section is a documented path, not a
   tested one [N].
3. **I did not trace when `qcomtee` was merged.** I verified it is in `master`
   on 2026-11-20 and referenced by `drivers/tee/Kconfig`, and found the
   `[PATCH v6 09/12] tee: add Qualcomm TEE driver` series, but I did not pin
   the merge commit or release [N].
4. **Whether a given retail device's QTEE actually implements `smcinvoke` is
   undetermined** [N]. The `-EIO` probe path means support is silently absent
   on older firmware rather than an error, so absence of `/dev/tee0` is the
   only signal.
5. **`libqcomtee`/`quic-teec` API details were not read** — I verified the
   repository and its BSD-3-Clause licence, not its headers [N].
6. **I am not asserting there is no other mainline path.** I enumerated
   `drivers/firmware/qcom/` (14 entries) and `drivers/tee/` (6 dirs) and found
   `qcomtee` plus the QSEECOM client-registration layer; I did not audit
   `drivers/misc/` or out-of-tree-for-mainline staging trees [N].

## 7. Rule 1 — the correction I am making

I am **not** editing `userspace-vs-firmware-split.md` in this commit: it belongs
to a different work stream and another agent may hold it. The exact fix the lead
should apply to line 48 is:

> **before:** "the Android-style driver that *loads* arbitrary TA images
> (`qseecom_load_app`) is **not** in torvalds master (`drivers/tee/qcom/qseecom.c`:
> 404 checked 2026-11-17)"
>
> **after:** "…is **not** in torvalds master (`drivers/tee/qcom/qseecom.c`: 404,
> re-checked 2026-11-20). However **`drivers/tee/qcomtee/` IS in master** and
> exposes QTEE *and its loaded TAs* over the generic TEE API
> (`CONFIG_QCOMTEE`) — it invokes TAs but does **not** load or verify their
> image files, so vendor-kernel `qseecom_load_app` remains the only image-loader."

`docs/REPO-STATE-MAP.md:39` also still reads tz = PARTIAL with the
`seg[10]` entropy question outstanding — that question is genuinely still open
and is **not** answered here, because the payload is no longer available.

## Sources

| claim | source | access |
|---|---|---|
| `drivers/tee/qcomtee/` exists, 12 files, 111,456 B | GitHub contents API, `torvalds/linux` master | 2026-11-20 |
| `CONFIG_QCOMTEE` help text | `drivers/tee/qcomtee/Kconfig` | 2026-11-20 |
| sourced by TEE Kconfig | `drivers/tee/Kconfig:23` | 2026-11-20 |
| self-registration via SCM probe | `drivers/firmware/qcom/qcom_scm.c:2478-2499` | 2026-11-20 |
| SMCINVOKE ABI 0x06/0x00/0x01/0x02 | `drivers/firmware/qcom/qcom_scm.h:163-166` | 2026-11-20 |
| inbound/outbound buffers, IO/OO/IB/OB arguments | `drivers/tee/qcomtee/qcomtee_msg.h` (DOC block) | 2026-11-20 |
| SHM Bridge forced | `select QCOM_TZMEM_MODE_SHMBRIDGE`; `drivers/firmware/qcom/Kconfig:38-44` | 2026-11-20 |
| no `request_firmware` in driver | `grep` over `core.c`, `qcomtee_msg.h` | 2026-11-20 |
| no TA image loader in mainline | `drivers/tee/qcom/qseecom.c` → 404 | 2026-11-20 |
| user-space architecture diagram, libqcomtee | `kernel.org/doc/html/v7.1/tee/qtee.html` | 2026-11-20 |
| BSD-3 userspace client | `github.com/quic/quic-teec` | 2026-11-20 |
| legacy `qseecom_load_app` | `android.googlesource.com/kernel/msm/.../drivers/misc/qseecom.c` | 2026-11-20 |
| tz family 4,264 rows / 87 devices / 171 files / 665,173,154 B | `coverage-matrix.csv` | 2026-11-20 |
| stale claim being corrected | `research/qualcomm/docs/userspace-vs-firmware-split.md:48` | 2026-11-20 |
| ELF segment maps, signature blocks | `research/fleet/dsp-tz-map.md`, `research/fleet/qsee-crossgen.md` | 2026-11-20 |
