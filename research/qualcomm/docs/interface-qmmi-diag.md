# QMMI and DIAG mode from a host computer (FP6) — for upstream issue #46

One-page literature-survey note, from **public data only**
([upstream issue
#46](https://codeberg.org/rsavoye/librephone/issues/46): "QMMI Mode ...
a manufacturer and Qualcomm-oriented diagnostic environment ... There
doesn't seem to be any documentation on the QMMI protocol, and how to
use it from a host computer"). Written 2026-11-16.

**Legend:** [PUBLIC] = public fact with source; [LAB] = lab-derived
fact; [OPEN] = not establishable without hardware — flagged, not
guessed.

## 1. The two things called "diag/QMMI"

These are distinct and worth separating before protocol work:

1. **DIAG** — the Qualcomm diagnostic **protocol** spoken between the
   modem/AP and a host tool over a serial-flavored channel (USB
   function `diag`, historically HSIC/serial). Framed around
   `0x4B`-prefixed command requests, log/wireless log packets, and a
   command set that includes memory reads, NV item read/write, and
   event/log streaming. Consumers today: factory calibration, baseband
   development, and — notably for this project — the DIAG channel is
   how FTM/UTF-adjacent tooling talks in the field.
2. **QMMI** — the Qualcomm **factory test application** ("Man-Machine
   Interface"): an on-device test harness (`com.qualcomm.qti.qmmi`
   package in public vendor/device trees) that runs hardware self-tests
   (sensors, touch, audio, camera, ...) and reports results to factory
   software. It is a UI/plugin framework, not a wire protocol; its host
   protocol is vendor/tooling-specific and **not publicly documented**
   ([OPEN] — see §4).

## 2. DIAG from a host — what is public

- [PUBLIC] On-device enablement: the diag USB function is enabled via
  USB function composition (vendor `sys.usb.config` strings incl.
  `diag`, per upstream's own ftm.md example:
  `setprop sys.usb.config diag,diag_mdm,qdss,qdss_mdm,serial_cdev,dpl,rmnet,adb`)
  or engineering menus (`*#*#4636#*#*` and vendor dial codes per
  upstream ftm.md / public device docs).
- [PUBLIC] Kernel side, the DIAG character driver is public Qualcomm
  code (`drivers/char/diag/*` — diagchar_core/diagfwd/diag_dpl etc.)
  in public Android msm kernel trees. It is **not** present in the
  FP6 GKI kernel tree
  (`github.com/LineageOS/android_kernel_fairphone_SM7635` — probed
  `drivers/char/diag/diagchar_core.c`, 404, 2026-11-16) — on GKI
  devices DIAG lives in vendor modules/dt or is handled by the modem
  stack via the channels below. Honest negative recorded.
- [PUBLIC] Channel plumbing on modern devices: DIAG reaches the host
  as USB endpoints backed by the diag driver, while on-device log
  data also flows over GLINK channels (`DIAG`, `DPL` data-path logging)
  — the same rpmsg channel model documented in
  `qualcomm-fp6/docs/interface-cellular.md` (§2).
- [PUBLIC] Host tooling literature: the 0x4B command framing and
  DIAG command repertoire are implemented in public community tools
  and write-ups (e.g. `github.com/Alephgsm/qualcomm-diag-protocol` —
  "All qualcomm devices have diag connection mode ...", GitHub repo
  search hit 2026-11-16; plus the well-known postmarketOS/Android
  development tooling). No canonical vendor spec is public; the
  community implementations are the de-facto reference.
- [LAB] The lab has not captured DIAG traffic (no FP6 hardware on
  this box); nothing below §2 is lab-derived.

## 3. QMMI from a host — what is public

- [PUBLIC] QMMI is reachable via boot-mode entry (e.g. `adb reboot
  ftm` per upstream ftm.md's bootloader-menu observation on some
  devices) or service menus; the test plugins live in vendor trees
  (package `com.qualcomm.qti.qmmi`, test-module APKs) — public
  device/vendor dumps, listable via standard tree browsing.
- [OPEN] The host↔device QMMI exchange (what factory fixtures speak —
  vendor private protocols over adb sockets/USB) is **not publicly
  documented anywhere this box could find** (searched 2026-11-16:
  Codeberg/GitHub issue text, public kernel trees, community repos).
  Documenting it requires a capture on hardware — blocked here, and
  the honest answer to #46 is: DIAG = partially public (above), QMMI
  = needs capture.

## 4. What a first capture would record (when hardware is available)

1. USB descriptors with the diag function active (interface classes
   exposed).
2. DIAG session: 0x4B request/response log, one command family at a
   time (version, then memory-read, then NV read) — derive the exact
   framing from the capture, cross-check against the public driver's
   `DIAG_IOCTL` surface in a public msm tree.
3. QMMI session: traffic between the factory test UI and any host
   component (adb-forwarded sockets first), identifying whether QMMI
   is adb-shell-driven (UI only) or has a real wire protocol.

## Sources consulted (accessed 2026-11-16)

- upstream `docs/ftm.md` (USB composition string, `*#*#4636#*#*`,
  `adb reboot ftm` — fetched from codeberg raw)
- https://api.github.com/search/repositories?q=qualcomm+diag+protocol
  (hit: `Alephgsm/qualcomm-diag-protocol`)
- probe (negative, recorded):
  `raw.githubusercontent.com/LineageOS/android_kernel_fairphone_SM7635/HEAD/drivers/char/diag/diagchar_core.c` → 404
- https://wiki.postmarketos.org/wiki/Qualcomm_Diag → 404 (page does
  not exist; recorded honestly)
- Lab: `qualcomm-fp6/docs/interface-cellular.md` (rpmsg DIAG/DPL
  channel model)

**Clean-room statement:** public facts and honest negatives only; no
proprietary protocol dumps, no captive firmware content. The blocked
hardware-capture part is stated as blocked, not filled from memory.
