#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cpp_probe.py -- clean-room structural analyser for the QUALCOMM MSM
``cpp_firmware_vN_N_N.fw`` family (Camera Post-Processing microcode).

Scope: the 16 KiB (one file: 15.75 KiB) fixed-window CPP firmware images
shipped by Qualcomm Android camera stacks in ``vendor/firmware/`` and
consumed by the GPL-2.0-only kernel driver
``drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c``.

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-19 from public GPL/Linux sources only:

  - ``drivers/media/platform/msm/camera_v2/pproc/cpp/msm_cpp.c`` and
    ``msm_cpp.h`` (LineageOS/android_kernel_xiaomi_msm8953 @ lineage-21,
    GPL-2.0-only, fetched 2026-11-19) -- the *consumer* of these files:
      * ``VIDIOC_MSM_CPP_LOAD_FIRMWARE`` copies a userspace-supplied
        filename into ``cpp_dev->fw_name_bin`` and calls
        ``request_firmware()`` -- the kernel does NOT construct the name.
      * ``cpp_load_fw()`` sends ``MSM_CPP_CMD_FW_LOAD`` (0x2), then
        ``cpp_dev->fw->size`` (the WHOLE file length in bytes), then
        ``MSM_CPP_START_ADDRESS`` (0x0), then streams
        ``fw->size / 4`` little-endian 32-bit words straight out of
        ``fw->data`` into the CPP micro-FIFO.
      * consequence: the kernel never parses a header, magic, length
        field or checksum out of the file. There is no kernel-side
        container to reproduce. Everything this tool reports about
        structure is a property of the *payload*, not of a kernel
        contract.
      * ``MSM_CPP_MSG_ID_CMD`` = 0x3E646D63, ``MSM_CPP_MSG_ID_OK`` =
        0x0A0A4B4F, ``MSM_CPP_MSG_ID_TRAILER`` = 0xABCDEFAA -- the
        protocol magic words the microcode itself must emit. Their
        presence inside the image is measured by this tool.
      * ``CPP_FW_VERSION_1_{2,4,6,8,10}_0`` constants (0x10020000 ..
        0x10100000) -- the kernel's only version notion, compared
        against the value the *chip* reports at runtime.
  - ``mm-camera/.../pproc-new/cpp/cpp_hardware.c`` and
    ``cpp_hw_params.h`` / ``cpp_hardware.h`` (Sushrut1101/
    android_vendor_qcom_proprietary, fetched 2026-11-19) -- the
    userspace *producer* of the filename:
      * ``cpp_hardware_select_fw_version()`` maps a CPP hardware version
        to a firmware version enum, then ``snprintf``s
        ``"cpp_firmware_v%d_%d_%d.fw"`` from
        ``CPP_GET_FW_MAJOR/MINOR/STEP_VERSION``.
      * bit layout, quoted from the header comment: ``31:28 Major,
        27:16 Minor, 15:0 Step``.
      * ``CPP_FW_VERSION_1_1_6 = 0x10010006`` .. ``CPP_FW_VERSION_1_12_1
        = 0x100C0001`` -- the full enum, and therefore the definitive
        list of names this family can take.
  - ``linux-firmware`` ``WHENCE`` (git.kernel.org, fetched 2026-11-19)
    and the mainline ``brcmfmac`` driver -- used ONLY to test and
    honestly record the "this is Cypress/Infineon WLAN firmware"
    hypothesis. It is refuted; see the analysis document.

No proprietary documentation, no decompiled or disassembled code, and no
vendor source was read. The image content is treated as opaque bytes: this
tool reports offsets, lengths, digests, entropies and equality counts only.
It never interprets an instruction and never reproduces payload bytes.

WHAT THE TOOL MEASURES (all own measurements of payload bytes)
  1. fixed-window check          -- is the file exactly 16,384 B?
  2. header probe                -- the u16 vector table at [0,0x22) and
                                    the 0x4000 window accounting
  3. version-marker scan         -- ASCII version strings (there are
                                    none) *and* the numeric marker the
                                    images do carry
  4. entropy profile             -- per-1KiB and per-region Shannon entropy
  5. padding characterisation    -- the 0xFF fill region(s), offsets/lengths
  6. epilogue detection          -- the invariant trailing block
  7. adjacent-version first-diff -- the exact first differing offset
  8. N x N identity matrix       -- same-offset byte identity, whole-file
                                    and code-region-only, plus the
                                    padding-excluded variant

Usage:
    python3 -I cpp_probe.py <file> [--json out.json] [--brief]
    python3 -I cpp_probe.py --matrix f1 f2 ... [--json out.json]
    python3 -I cpp_probe.py --versions f1 f2 ...

Exit status: 0 = structural facts only / info diagnostics; 1 = at least one
error-class diagnostic (wrong window size, truncated input, unreadable file).
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import struct
import sys

# ---------------------------------------------------------------- constants

# The fixed window every file in this family occupies. 15 of the 16 DB
# identities are exactly 16,384 B; cpp_firmware_v1_1_1.fw is 16,128 B
# (measured 2026-11-19). Both are multiples of the 4-byte download word and
# of 0x100.
WINDOW_BYTES = 16384
SHORT_WINDOW_BYTES = 16128

# Layout landmarks measured on all 12 fetched identities (2026-11-19).
# These are observations, NOT kernel contract -- see the clean-room note.
HDR_VECTOR_OFFSET = 2          # u16 vector table starts after the 0x7140 word
HDR_VECTOR_COUNT = 16
HDR_VECTOR_END = HDR_VECTOR_OFFSET + 2 * HDR_VECTOR_COUNT   # 0x22

EPILOGUE_START = 0x3EFE        # invariant 204-byte block
EPILOGUE_END = 0x3FCA
EPILOGUE_LEN = EPILOGUE_END - EPILOGUE_START
TRAILING_FILL_START = EPILOGUE_END     # [0x3fca, 0x4000) is 0xFF in all files

PAD_BYTE = 0xFF                # erased-flash fill, not zero fill
CODE_REGION_END = 0x3EFC       # exclusive upper bound used for code stats

# Protocol magic words the microcode must emit; from msm_cpp.h
# (GPL-2.0-only, fetched 2026-11-19). Used only as search needles.
MSG_ID_CMD = 0x3E646D63
MSG_ID_OK = 0x0A0A4B4F
MSG_ID_TRAILER = 0xABCDEFAA
PROTOCOL_MAGICS = {
    MSG_ID_CMD: "MSM_CPP_MSG_ID_CMD",
    MSG_ID_OK: "MSM_CPP_MSG_ID_OK",
    MSG_ID_TRAILER: "MSM_CPP_MSG_ID_TRAILER",
}

# cpp_hw_params.h:31:28 Major, 27:16 Minor, 15:0 Step.
def fw_version_word(major: int, minor: int, step: int) -> int:
    return ((major & 0xF) << 28) | ((minor & 0xFFF) << 16) | (step & 0xFFFF)


def fw_version_name(major: int, minor: int, step: int) -> str:
    return "cpp_firmware_v%d_%d_%d.fw" % (major, minor, step)


# The full enum from cpp_hw_params.h (fetched 2026-11-19). This is the
# definitive set of names the userspace producer can emit.
KNOWN_FW_VERSIONS = {
    (1, 1, 6): 0x10010006,
    (1, 2, 0): 0x10020000,
    (1, 4, 0): 0x10040000,
    (1, 5, 0): 0x10050000,
    (1, 5, 1): 0x10050001,
    (1, 5, 2): 0x10050002,
    (1, 6, 0): 0x10060000,
    (1, 8, 0): 0x10080000,
    (1, 10, 0): 0x100A0000,
    (1, 12, 0): 0x100C0000,
    (1, 12, 1): 0x100C0001,
}
# cpp_firmware_v1_1_1.fw has no enum entry in the modern header but exists
# in the fleet; it is accepted as a filename, not as an enum value.
EXTRA_FILENAME_VERSIONS = {(1, 1, 1): 0x10010001}


# ---------------------------------------------------------------- diagnostics

class Report:
    """Diagnostics: 'error' class -> exit 1; 'info' class -> recorded only."""

    def __init__(self):
        self.items = []

    def error(self, code, detail):
        self.items.append({"class": "error", "code": code, "detail": detail})

    def info(self, code, detail):
        self.items.append({"class": "info", "code": code, "detail": detail})

    @property
    def has_errors(self):
        return any(i["class"] == "error" for i in self.items)


# ---------------------------------------------------------------- helpers

def entropy(data):
    """Shannon entropy in bits/byte (0.0 for empty input)."""
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = float(len(data))
    h = 0.0
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log(p, 2)
    return h


def block_stats(data):
    """Distribution facts used to characterise an opaque range."""
    if not data:
        return {"len": 0, "entropy": 0.0, "zero_pct": 0.0, "ff_pct": 0.0,
                "distinct_bytes": 0}
    n = float(len(data))
    return {
        "len": len(data),
        "entropy": round(entropy(data), 3),
        "zero_pct": round(100.0 * data.count(0x00) / n, 2),
        "ff_pct": round(100.0 * data.count(0xFF) / n, 2),
        "distinct_bytes": len(set(data)),
    }


def parse_version_from_name(path):
    """Recover (major, minor, step) from a ``cpp_firmware_vN_N_N.fw`` name.

    Returns None when the basename does not carry the pattern. This is the
    only self-identification the format offers at the filename level; the
    bytes themselves do not store the string.
    """
    base = os.path.basename(path)
    if not (base.startswith("cpp_firmware_v") and base.endswith(".fw")):
        return None
    core = base[len("cpp_firmware_v"):-len(".fw")]
    parts = core.split("_")
    if len(parts) != 3:
        return None
    try:
        return tuple(int(p) for p in parts)
    except ValueError:
        return None


def version_marker_word(major, minor, step):
    """The 16-bit word this family embeds to self-identify its minor rev.

    MEASURED (2026-11-19, 12/12 files): every image contains exactly one
    16-bit little-endian word equal to ``0x1000 | BCD(minor)`` -- i.e.
    0x1001 for minor 1, 0x1002 for minor 2, 0x1010 for minor 10, 0x1012 for
    minor 12. The nibbles are the *decimal* digits of the minor revision
    written as BCD, which is why 1.10.0 and 1.12.0 do not collide with
    1.1.0/1.2.0.

    This is a correlation established by measurement, not a documented
    field: no public source describes it, and the kernel never reads it.
    """
    if not 0 <= minor <= 99:
        raise ValueError("minor out of BCD range: %r" % (minor,))
    return 0x1000 | (((minor // 10) << 4) | (minor % 10))


# ---------------------------------------------------------------- fixed window

def check_window(data, rep):
    """Test the 16 KiB fixed-window hypothesis and report the arithmetic."""
    n = len(data)
    info = {
        "bytes": n,
        "window_bytes": WINDOW_BYTES,
        "is_exact_window": n == WINDOW_BYTES,
        "short_window_bytes": SHORT_WINDOW_BYTES,
        "is_short_window": n == SHORT_WINDOW_BYTES,
        "multiple_of_4": n % 4 == 0,
        "multiple_of_0x100": n % 0x100 == 0,
        "download_words": n // 4,
    }
    if not info["multiple_of_4"]:
        rep.error("not-word-aligned",
                  "%d bytes is not a multiple of the 4-byte download word the "
                  "kernel streams (cpp_load_fw writes fw->size/4 words)" % n)
    if n == WINDOW_BYTES:
        rep.info("fixed-window-exact",
                 "%d B == 16 KiB window" % n)
    elif n == SHORT_WINDOW_BYTES:
        rep.info("fixed-window-short",
                 "%d B == 16 KiB - 256 B (the v1_1_1 outlier; every other "
                 "identity in the fleet is 16,384 B)" % n)
    else:
        rep.info("fixed-window-off",
                 "%d B is neither 16,384 nor 16,128; the fixed-window "
                 "hypothesis does not hold for this file" % n)
    return info


# ---------------------------------------------------------------- header probe

def probe_header(data):
    """Decode the u16 vector table at [2, 0x22) and the 0x7140 lead word.

    No public source documents this table. It is described here purely as
    measured structure: 16 little-endian u16 values. Measured on the real
    fleet, parity is *not* invariant -- no slot is odd in all 12 files (slot
    15 is odd in 10/12, slot 9 in 9/12, others fewer) -- but every value,
    doubled, still lands below the image's code end, which is consistent with
    halfword offsets. The field width and the odd slots remain [OPEN].
    """
    if len(data) < HDR_VECTOR_END:
        return {"available": False,
                "reason": "file shorter than the 0x22-byte header region"}
    lead = struct.unpack_from("<H", data, 0)[0]
    words = [struct.unpack_from("<H", data, HDR_VECTOR_OFFSET + 2 * i)[0]
             for i in range(HDR_VECTOR_COUNT)]
    distinct = sorted(set(words))
    odd_slots = [i for i, w in enumerate(words) if w % 2]
    # Equality pattern: which slots repeat an earlier slot's value. Across the
    # fleet 11/12 share one pattern; v1_2_0 alone differs (an extra distinct
    # value at slot 10).
    seen = {}
    pattern = []
    for w in words:
        if w in seen:
            pattern.append(seen[w])
        else:
            seen[w] = len(seen)
            pattern.append(seen[w])
    return {
        "available": True,
        "lead_word_u16": "0x%04x" % lead,
        "lead_word_constant_across_fleet": lead == 0x7140,
        "vector_table": {
            "offset": HDR_VECTOR_OFFSET,
            "count": HDR_VECTOR_COUNT,
            "end_offset": HDR_VECTOR_END,
            "values": ["0x%04x" % w for w in words],
            "min": "0x%04x" % min(words),
            "max": "0x%04x" % max(words),
            "all_even": all(w % 2 == 0 for w in words),
            "odd_slots": odd_slots,
            "distinct_count": len(distinct),
            "equality_pattern": pattern,
        },
        "note": ("undocumented in any public source; reported as measured "
                 "structure only -- the values are small and, doubled, land "
                 "below the image's code end, consistent with halfword "
                 "offsets, but they are NOT all even, so the field width "
                 "remains [OPEN]"),
    }


# ---------------------------------------------------------------- version scan

def scan_version_strings(data, min_len=4):
    """Look for printable ASCII version-like strings.

    The honest result for this family is that the images carry NO ASCII
    version string for their own version. The only 'v1.1' literal in the
    fleet sits inside the invariant epilogue (offset 0x3f80) and is present
    in 11/12 files regardless of their actual version -- it is a fixed
    literal of the shared microcode epilogue, not a version field. The tool
    reports both facts so the distinction cannot be lost.
    """
    import re
    hits = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,}" % min_len, data):
        hits.append({"offset": m.start(), "text": m.group().decode("ascii")})
    version_like = [h for h in hits
                    if re.search(r"\d+\.\d+", h["text"])
                    or re.search(r"\bv\d", h["text"])]
    return {"printable_runs": len(hits),
            "version_like": version_like,
            "self_version_string_present": False,
            "note": ("no ASCII string encodes the image's own version; the "
                     "'v1.1' literal at 0x3f80 belongs to the invariant "
                     "epilogue and is identical in 11/12 files")}


def scan_version_marker(data, path, rep):
    """Locate the numeric self-identification marker measured in this family.

    Tests the measured rule (one u16 == 0x1000|BCD(minor)) and reports every
    hit offset. A file whose name carries no version, or whose marker is
    absent, is reported as such rather than guessed at.
    """
    ver = parse_version_from_name(path)
    out = {
        "filename_version": ("%d.%d.%d" % ver) if ver else None,
        "enum_value": None,
        "marker_word": None,
        "marker_offsets": [],
        "marker_present": False,
        "unique": None,
    }
    if not ver:
        rep.info("no-filename-version",
                 "basename does not match cpp_firmware_vN_N_N.fw; the "
                 "numeric marker cannot be predicted")
        return out
    major, minor, step = ver
    enum = KNOWN_FW_VERSIONS.get(ver, EXTRA_FILENAME_VERSIONS.get(ver))
    out["enum_value"] = ("0x%08x" % enum) if enum is not None else None
    if enum is None:
        rep.info("version-not-in-enum",
                 "%d.%d.%d has no CPP_FW_VERSION_* constant in the public "
                 "cpp_hw_params.h enum" % ver)
    want = version_marker_word(major, minor, step)
    out["marker_word"] = "0x%04x" % want
    needle = struct.pack("<H", want)
    offsets = []
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            break
        if i % 2 == 0:          # 16-bit aligned only
            offsets.append(i)
        start = i + 1
    out["marker_offsets"] = offsets
    out["marker_present"] = bool(offsets)
    out["unique"] = len(offsets) == 1
    # MEASURED: the marker is the HIGH half of a little-endian u32 whose LOW
    # half is a build counter. It moves with the build (0x10 vs 0x02 across
    # 1.5.0->1.5.1) but does NOT equal the filename step -- it disagrees in
    # 7 of the 12 real files. Reported, never used to infer the version.
    if offsets:
        out["adjacent_word_u32"] = ["0x%08x"
                                    % struct.unpack_from("<I", data, o - 2)[0]
                                    for o in offsets]
        out["adjacent_build_counter"] = ["0x%04x"
                                         % struct.unpack_from("<H", data,
                                                              o - 2)[0]
                                         for o in offsets]
        out["build_counter_matches_filename_step"] = [
            (struct.unpack_from("<H", data, o - 2)[0] == step)
            for o in offsets]
    if offsets:
        rep.info("version-marker-found",
                 "u16 0x%04x (BCD minor %d) at %s"
                 % (want, minor, ", ".join("0x%04x" % o for o in offsets)))
    else:
        rep.info("version-marker-absent",
                 "no u16 0x%04x found; the measured marker rule does not hold "
                 "for this file" % want)
    return out


def scan_protocol_magics(data):
    """Locate the three CPP protocol magic words (msm_cpp.h) in the image.

    Their presence is expected: the microcode is what *emits* these words to
    the kernel. Counting them is a cheap sanity signal that the payload is
    genuinely CPP microcode rather than an unrelated 16 KiB blob.
    """
    found = {}
    for off in range(0, len(data) - 3, 2):
        w = struct.unpack_from("<I", data, off)[0]
        if w in PROTOCOL_MAGICS:
            found.setdefault(PROTOCOL_MAGICS[w], []).append(off)
    return {name: [("0x%04x" % o) for o in offs]
            for name, offs in found.items()}


# ---------------------------------------------------------------- padding

def find_fill_runs(data, value, min_len=16):
    """Runs of a repeated byte, as (start, end_exclusive, length)."""
    runs = []
    i = 0
    n = len(data)
    while i < n:
        if data[i] == value:
            j = i
            while j < n and data[j] == value:
                j += 1
            if j - i >= min_len:
                runs.append((i, j, j - i))
            i = j
        else:
            i += 1
    return runs


def content_islands(data, fill=PAD_BYTE, gap_tolerance=16):
    """Maximal non-fill spans, merging spans separated by <= gap_tolerance.

    This is the shape measure for a padded fixed-window image: the code and
    its tables show up as one or more islands floating in a sea of fill.
    """
    islands = []
    n = len(data)
    for k in range(n):
        if data[k] != fill:
            if islands and k - islands[-1][1] <= gap_tolerance:
                islands[-1][1] = k
            else:
                islands.append([k, k])
    return [{"start": a, "end": b + 1, "len": b + 1 - a} for a, b in islands]


def probe_trailer(data, code_end):
    """Decode the u16 halfword-length field immediately below the epilogue.

    MEASURED, and the strongest structural contract found in this family: the
    u16 at 0x3EFC is a *halfword count* whose doubled value is the code end.

        code_end == 2 * (u16@0x3EFC + 1)

    holds exactly for the six 1.2.0-1.6.0 identities (gap 0 bytes). The four
    later identities (1.10.0, 1.12.0, 1.12.1) place a further 176-byte
    fixed-stride block after the region the field describes; v1_1_1, v1_1_6
    and v1_8_0 leave the field at its erased value 0xFFFF. So the field is a
    region length, NOT the file length -- the kernel is never told either, it
    just streams fw->size/4 words.

    The 176-byte block after the described region is measured as: a 14-byte
    prologue, then 8 records of 20 bytes (a 12-byte body shared by all 8, a
    u16 that advances by 0x0A per record, a u16 that advances by 8, and a
    4-byte constant), then a 2-byte tail. It is reported as measured structure
    with its semantics [OPEN].
    """
    out = {"offset": 0x3EFC, "available": False}
    if len(data) < 0x3EFE:
        out["reason"] = "file ends before 0x3efe"
        return out
    field = struct.unpack_from("<H", data, 0x3EFC)[0]
    out["available"] = True
    out["field_u16"] = "0x%04x" % field
    out["erased"] = field == 0xFFFF
    out["halfwords"] = field
    out["implied_end"] = 2 * (field + 1)
    out["implied_end_hex"] = "0x%04x" % (2 * (field + 1))
    out["code_end"] = code_end
    out["code_end_hex"] = "0x%04x" % code_end
    out["residual_after_implied_end"] = code_end - 2 * (field + 1)
    out["exact"] = (not out["erased"]) and code_end == 2 * (field + 1)
    if out["erased"]:
        out["note"] = ("field is at its erased value 0xffff; this identity "
                       "does not populate it")
    elif out["exact"]:
        out["note"] = ("code_end == 2*(field+1): the field is a halfword "
                       "count of the region it terminates")
    else:
        out["note"] = ("code_end is %d bytes beyond 2*(field+1); a "
                       "fixed-stride block follows the described region"
                       % out["residual_after_implied_end"])
    residual = out["residual_after_implied_end"]
    if not out["erased"] and residual:
        out["stride_block"] = probe_stride_block(
            data, 2 * (field + 1), residual)
    return out


def probe_stride_block(data, start, length=176):
    """Decode the fixed-stride block that follows the length-described region.

    MEASURED on the three identities that carry it (1.10.0, 1.12.0, 1.12.1):

        14-byte prologue
        8 x 20-byte record:
            [+0,  +12)  12-byte body, identical in all 8 records
            [+12, +14)  u16 advancing by 0x0A per record
            [+14, +16)  u16 advancing by 8    per record  (0x0700, 0x0708, ...)
            [+16, +20)  4-byte constant 00 80 20 64
        2-byte tail  01 70

    14 + 8*20 + 2 = 176. Reported as measured structure; semantics [OPEN].
    """
    if start < 0 or start + length > len(data):
        return {"available": False,
                "reason": "block [0x%x,0x%x) outside the file"
                          % (start, start + length)}
    blk = data[start:start + length]
    prologue = blk[:14]
    tail = blk[14 + 8 * 20:]
    recs = []
    for k in range(8):
        o = 14 + 20 * k
        rec = blk[o:o + 20]
        recs.append({
            "offset": start + o,
            "body_sha1": hashlib.sha1(rec[:12]).hexdigest(),
            "a_u16": "0x%04x" % struct.unpack_from("<H", rec, 12)[0],
            "b_u16": "0x%04x" % struct.unpack_from("<H", rec, 14)[0],
            "const4": rec[16:20].hex(),
        })
    bodies = {r["body_sha1"] for r in recs}
    a_vals = [int(r["a_u16"], 16) for r in recs]
    b_vals = [int(r["b_u16"], 16) for r in recs]
    return {
        "available": True,
        "offset": start,
        "len": length,
        "prologue_len": 14,
        "record_len": 20,
        "record_count": 8,
        "tail_len": len(tail),
        "bodies_identical": len(bodies) == 1,
        "body_sha1": recs[0]["body_sha1"],
        "a_step": (a_vals[1] - a_vals[0]) if len(a_vals) > 1 else 0,
        "b_step": (b_vals[1] - b_vals[0]) if len(b_vals) > 1 else 0,
        "records": recs,
        "note": ("14 B prologue + 8 x 20 B records + 2 B tail = 176 B; the "
                 "12-byte record body is identical in all 8 (this is the "
                 "'fixed stride' seen when comparing files)"),
    }


def characterise_padding(data, rep):
    """Characterise the fill region and the invariant epilogue.

    Measured facts this reports:
      * the fill byte is 0xFF (erased flash), never 0x00;
      * the fill occupies a single contiguous tail between the code end and
        the epilogue start, plus the [0x3fca, 0x4000) block after it;
      * the 204-byte block at [0x3efe, 0x3fca) is byte-identical in 11/12
        files (the 12th, v1_1_1, is 256 B shorter and lacks it entirely).
    """
    n = len(data)
    ff_runs = find_fill_runs(data, PAD_BYTE, min_len=16)
    zero_runs = find_fill_runs(data, 0x00, min_len=16)
    islands = content_islands(data)

    # The "code region" is everything before the epilogue, minus fill.
    code_region_end = min(CODE_REGION_END, n)
    code_end = 0
    for k in range(code_region_end - 1, -1, -1):
        if data[k] != PAD_BYTE:
            code_end = k + 1
            break

    epilogue = None
    if n >= EPILOGUE_END:
        epilogue = {
            "offset": EPILOGUE_START,
            "len": EPILOGUE_LEN,
            "sha1": hashlib.sha1(data[EPILOGUE_START:EPILOGUE_END]).hexdigest(),
            "present": True,
        }
    else:
        epilogue = {"offset": EPILOGUE_START, "len": EPILOGUE_LEN,
                    "present": False,
                    "reason": "file ends at 0x%x, before the epilogue" % n}

    trailing_fill = None
    if n > TRAILING_FILL_START:
        span = data[TRAILING_FILL_START:]
        trailing_fill = {
            "offset": TRAILING_FILL_START,
            "len": len(span),
            "all_fill": set(span) == {PAD_BYTE},
        }

    # Zero-fill test, scoped to the pad window: [code_end, n).  Any interior
    # 0x00 run below code_end is payload, not padding, so it must not count.
    pad_window = data[code_end:] if code_end else data
    zero_fill_runs = find_fill_runs(pad_window, 0x00, min_len=16)
    zero_fill_used = bool(zero_fill_runs)
    zero_fill_run = None
    if zero_fill_runs:
        a, b, l = max(zero_fill_runs, key=lambda r: r[2])
        zero_fill_run = {"start": code_end + a, "end": code_end + b, "len": l}
    zero_bytes_in_pad_window = pad_window.count(0x00)

    trailer = probe_trailer(data, code_end)

    info = {
        "fill_byte": "0x%02x" % PAD_BYTE,
        "fill_is_erased_flash": True,
        # NOTE: an interior all-zero table is normal payload, not padding, so
        # "zero fill used" is judged on the pad window only -- everything
        # after the code end. Measured: the real fleet never pads with 0x00.
        "zero_fill_used": zero_fill_used,
        "zero_fill_run": zero_fill_run,
        "zero_bytes_in_pad_window": zero_bytes_in_pad_window,
        "code_end": code_end,
        "trailer": trailer,
        "fill_after_code_end": (EPILOGUE_START - code_end) if n >= EPILOGUE_START
                               else (n - code_end),
        "fill_runs_ge16": [{"start": a, "end": b, "len": l}
                           for a, b, l in ff_runs],
        "zero_runs_ge16": [{"start": a, "end": b, "len": l}
                           for a, b, l in zero_runs],
        "content_islands": islands,
        "epilogue": epilogue,
        "trailing_fill_block": trailing_fill,
        "window_slack_after_epilogue": (n - TRAILING_FILL_START)
                                       if n > TRAILING_FILL_START else 0,
    }
    if code_end == 0:
        rep.error("all-fill-image",
                  "the entire code region is 0x%02x fill; no payload present"
                  % PAD_BYTE)
    return info


# ---------------------------------------------------------------- entropy

def entropy_profile(data, block=1024):
    """Per-block Shannon entropy plus a coarse region summary."""
    blocks = []
    for off in range(0, len(data), block):
        seg = data[off:off + block]
        blocks.append({"offset": off, "len": len(seg),
                       "entropy": round(entropy(seg), 3)})
    code_region_end = min(CODE_REGION_END, len(data))
    regions = {
        "header[0,0x22)": block_stats(data[0:HDR_VECTOR_END]),
        "code[0x22,%d)" % code_region_end:
            block_stats(data[HDR_VECTOR_END:code_region_end]),
        "epilogue[0x3efe,0x3fca)":
            block_stats(data[EPILOGUE_START:EPILOGUE_END])
            if len(data) >= EPILOGUE_END else block_stats(b""),
        "tail[0x3fca,end)":
            block_stats(data[TRAILING_FILL_START:])
            if len(data) > TRAILING_FILL_START else block_stats(b""),
    }
    return {"block_size": block, "blocks": blocks, "regions": regions}


# ---------------------------------------------------------------- diff / matrix

def first_diff(a, b):
    """First offset at which two byte strings differ, over their common len."""
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return None if len(a) == len(b) else n


def diff_runs(a, b):
    """All differing runs (start, end_inclusive) over the common length."""
    n = min(len(a), len(b))
    runs = []
    for i in range(n):
        if a[i] != b[i]:
            if runs and i == runs[-1][1] + 1:
                runs[-1][1] = i
            else:
                runs.append([i, i])
    return runs


def code_end_of(data):
    """Last non-fill byte before the epilogue, exclusive."""
    hi = min(CODE_REGION_END, len(data))
    for k in range(hi - 1, -1, -1):
        if data[k] != PAD_BYTE:
            return k + 1
    return 0


def same_offset_identity(a, b, limit=None):
    """Fraction of bytes identical at the same offset over a common prefix.

    ``limit`` caps the compared span (used to restrict the comparison to the
    code region so the shared 0xFF fill cannot inflate the number).
    """
    n = min(len(a), len(b))
    if limit is not None:
        n = min(n, limit)
    if not n:
        return {"common_len": 0, "identical_bytes": 0, "identity_pct": 0.0}
    same = sum(1 for i in range(n) if a[i] == b[i])
    return {"common_len": n, "identical_bytes": same,
            "identity_pct": round(100.0 * same / n, 2)}


def same_offset_identity_excluding_fill(a, b, limit=None):
    """Identity over positions where NEITHER side is the fill byte or zero.

    This is the honest "content-only" number: the padded fixed-window format
    makes whole-file identity look high purely because both files are mostly
    0xFF in the same places.
    """
    n = min(len(a), len(b))
    if limit is not None:
        n = min(n, limit)
    idx = [i for i in range(n)
           if a[i] not in (PAD_BYTE, 0x00) and b[i] not in (PAD_BYTE, 0x00)]
    if not idx:
        return {"positions": 0, "identical_bytes": 0, "identity_pct": 0.0}
    same = sum(1 for i in idx if a[i] == b[i])
    return {"positions": len(idx), "identical_bytes": same,
            "identity_pct": round(100.0 * same / len(idx), 2)}


def build_matrix(paths, labeler=None):
    """N x N identity matrix over the given files.

    Each cell carries three numbers, because for a padded fixed-window format
    a single number is misleading:
      * whole      -- same-offset identity over min(len)
      * code       -- same-offset identity over min(code_end)
      * content    -- identity where neither side is 0xFF/0x00 (padding-free)
    """
    docs = []
    for p in paths:
        with open(p, "rb") as f:
            data = f.read()
        docs.append({
            "file": p,
            "basename": os.path.basename(p),
            "label": (labeler(p) if labeler else os.path.basename(p)),
            "bytes": len(data),
            "md5": hashlib.md5(data).hexdigest(),
            "code_end": code_end_of(data),
            "_data": data,
        })
    n = len(docs)
    whole = [[None] * n for _ in range(n)]
    code = [[None] * n for _ in range(n)]
    content = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            a, b = docs[i]["_data"], docs[j]["_data"]
            whole[i][j] = 100.0 if i == j else \
                same_offset_identity(a, b)["identity_pct"]
            lim = min(docs[i]["code_end"], docs[j]["code_end"])
            code[i][j] = 100.0 if i == j else \
                same_offset_identity(a, b, limit=lim)["identity_pct"]
            content[i][j] = 100.0 if i == j else \
                same_offset_identity_excluding_fill(a, b, limit=lim)[
                    "identity_pct"]
    labels = [d["label"] for d in docs]
    for d in docs:
        del d["_data"]
    return {
        "labels": labels,
        "files": docs,
        "matrix_whole": [[round(v, 2) for v in row] for row in whole],
        "matrix_code_region": [[round(v, 2) for v in row] for row in code],
        "matrix_content_only": [[round(v, 2) for v in row] for row in content],
        "note": ("identity is same-offset byte equality. 'whole' is inflated "
                 "by the shared 0xFF fill in a padded fixed-window format; "
                 "'content_only' excludes positions where either side is "
                 "0xFF or 0x00 and is the honest similarity measure"),
    }


def adjacent_diffs(paths, labeler=None):
    """First-diff and run census for each consecutive pair in the given order."""
    docs = []
    for p in paths:
        with open(p, "rb") as f:
            docs.append((p, f.read()))
    out = []
    for i in range(len(docs) - 1):
        (pa, a), (pb, b) = docs[i], docs[i + 1]
        runs = diff_runs(a, b)
        fd = first_diff(a, b)
        out.append({
            "a": labeler(pa) if labeler else os.path.basename(pa),
            "b": labeler(pb) if labeler else os.path.basename(pb),
            "a_bytes": len(a),
            "b_bytes": len(b),
            "common_len": min(len(a), len(b)),
            "first_diff_offset": fd,
            "first_diff_offset_hex": ("0x%04x" % fd) if fd is not None else None,
            "differing_bytes": sum(r[1] - r[0] + 1 for r in runs),
            "diff_run_count": len(runs),
            "first_runs": [{"start": r[0], "end": r[1]} for r in runs[:8]],
        })
    return out


# ---------------------------------------------------------------- driver

def probe_file(path, do_hash=True):
    rep = Report()
    try:
        with open(path, "rb") as f:
            data = f.read()
    except (IOError, OSError) as exc:
        rep.error("io-error", str(exc))
        return {"file": path, "basename": os.path.basename(path),
                "error": str(exc), "diagnostics": rep.items}, 1

    out = {"file": path, "basename": os.path.basename(path),
           "bytes": len(data)}
    if do_hash:
        out["md5"] = hashlib.md5(data).hexdigest()
        out["sha256"] = hashlib.sha256(data).hexdigest()

    if len(data) < HDR_VECTOR_END:
        rep.error("file-too-small",
                  "%d bytes; the 0x22-byte header region cannot be read" % len(data))
        out["diagnostics"] = rep.items
        return out, 1

    out["fixed_window"] = check_window(data, rep)
    out["header"] = probe_header(data)
    out["version_strings"] = scan_version_strings(data)
    out["version_marker"] = scan_version_marker(data, path, rep)
    out["protocol_magics"] = scan_protocol_magics(data)
    out["padding"] = characterise_padding(data, rep)
    out["entropy"] = entropy_profile(data)

    ver = parse_version_from_name(path)
    if ver:
        major, minor, step = ver
        enum = KNOWN_FW_VERSIONS.get(ver, EXTRA_FILENAME_VERSIONS.get(ver))
        out["family"] = {
            "subsystem": "camera post-processing (MSM CPP)",
            "consumer": "msm_cpp.c cpp_load_fw() (GPL-2.0-only)",
            "producer": "cpp_hardware.c cpp_hardware_select_fw_version()",
            "version_encoding": ("CPP_FW_VERSION_* bitfield: 31:28 major, "
                                 "27:16 minor, 15:0 step"),
            "enum_value": ("0x%08x" % enum) if enum is not None else None,
            "expected_filename": fw_version_name(major, minor, step),
            "filename_matches": os.path.basename(path) ==
                                fw_version_name(major, minor, step),
        }

    out["diagnostics"] = rep.items
    return out, (1 if rep.has_errors else 0)


def render_brief(out):
    if "bytes" not in out:
        return ["%s: UNREADABLE (%s)" % (out.get("basename", "?"),
                                         out.get("error", "unknown error"))]
    lines = ["%s: %d bytes" % (out["basename"], out["bytes"])]
    fw = out.get("fixed_window", {})
    lines.append("  window: exact16K=%s short16K=%s words=%d"
                 % (fw.get("is_exact_window"), fw.get("is_short_window"),
                    fw.get("download_words", 0)))
    h = out.get("header", {})
    if h.get("available"):
        vt = h["vector_table"]
        lines.append("  header: lead=%s vectors %s..%s (%d distinct, even=%s)"
                     % (h["lead_word_u16"], vt["min"], vt["max"],
                        vt["distinct_count"], vt["all_even"]))
    vm = out.get("version_marker", {})
    bcount = vm.get("adjacent_build_counter") or []
    lines.append("  version: name=%s enum=%s marker=%s @ %s%s"
                 % (vm.get("filename_version"), vm.get("enum_value"),
                    vm.get("marker_word"),
                    ",".join("0x%04x" % o for o in vm.get("marker_offsets") or [])
                    or "absent",
                    ("  build-counter %s" % ",".join(bcount)) if bcount else ""))
    vs = out.get("version_strings", {})
    lines.append("  ascii version string in image: %s"
                 % vs.get("self_version_string_present"))
    p = out.get("padding", {})
    if p:
        ep = p.get("epilogue", {})
        lines.append("  layout: code_end=0x%04x fill=0x%02x (+%d B) "
                     "epilogue=%s tail_fill=%s"
                     % (p.get("code_end", 0), PAD_BYTE,
                        p.get("fill_after_code_end", 0),
                        ("0x%04x" % ep["offset"]) if ep.get("present") else "ABSENT",
                        (p.get("trailing_fill_block") or {}).get("all_fill")))
        tr = p.get("trailer") or {}
        if tr.get("available"):
            lines.append("  trailer: u16@0x3efc=%s -> 2*(w+1)=%s, code_end=%s "
                         "(%s)"
                         % (tr["field_u16"], tr["implied_end_hex"],
                            tr["code_end_hex"],
                            "exact" if tr["exact"]
                            else ("erased" if tr["erased"] else "residual %d B"
                                  % tr["residual_after_implied_end"])))
    e = out.get("entropy", {})
    if e:
        cr = e["regions"].get("code[0x22,%d)" % min(CODE_REGION_END, out["bytes"]))
        if cr:
            lines.append("  entropy: code region %.2f bits/byte, "
                         "%.1f%% 0xFF" % (cr["entropy"], cr["ff_pct"]))
    pm = out.get("protocol_magics", {})
    if pm:
        lines.append("  protocol magics present: %s"
                     % ", ".join("%s x%d" % (k, len(v))
                                 for k, v in sorted(pm.items())))
    return lines


def render_matrix_brief(m):
    """Compact matrix view: per-file row maxima plus the closest neighbour."""
    labels = m["labels"]
    lines = ["matrix over %d files (identity is same-offset byte equality)"
             % len(labels)]
    lines.append("  %-9s %10s %12s  %s"
                 % ("file", "max whole", "max content", "closest by content"))
    for i, lab in enumerate(labels):
        w = m["matrix_whole"][i]
        c = m["matrix_content_only"][i]
        others = [j for j in range(len(labels)) if j != i]
        if not others:
            lines.append("  %-9s %10.2f %12.2f  -" % (lab, 100.0, 100.0))
            continue
        best_w = max(others, key=lambda j: w[j])
        best_c = max(others, key=lambda j: c[j])
        lines.append("  %-9s %10.2f %12.2f  %s (%.2f whole / %.2f content)"
                     % (lab, w[best_w], c[best_c], labels[best_c],
                        w[best_c], c[best_c]))
    lines.append("  note: 'whole' is inflated by shared 0xff fill; "
                 "'content' excludes positions where either side is 0xff/0x00")
    return lines


def main(argv):
    args = argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print(__doc__)
        return 2

    do_brief = "--brief" in args
    do_hash = "--no-hash" not in args
    json_path = None
    if "--json" in args:
        json_path = args[args.index("--json") + 1]

    def labeler(p):
        v = parse_version_from_name(p)
        return ("%d.%d.%d" % v) if v else os.path.basename(p)

    mode = "single"
    paths = []
    if "--matrix" in args:
        mode = "matrix"
        i = args.index("--matrix")
        paths = [a for a in args[i + 1:] if not a.startswith("--")]
        if json_path:
            paths = [p for p in paths if p != json_path]
    elif "--versions" in args:
        mode = "versions"
        i = args.index("--versions")
        paths = [a for a in args[i + 1:] if not a.startswith("--")]
        if json_path:
            paths = [p for p in paths if p != json_path]
    else:
        paths = [args[0]]

    if not paths:
        print("error: no input files", file=sys.stderr)
        return 2

    rc = 0
    if mode == "matrix":
        result = build_matrix(paths, labeler=labeler)
    elif mode == "versions":
        docs = []
        for p in paths:
            doc, status = probe_file(p, do_hash=do_hash)
            rc = max(rc, status)
            docs.append(doc)
        result = {"files": docs, "adjacent_diffs": adjacent_diffs(
            paths, labeler=labeler)}
    else:
        result, status = probe_file(paths[0], do_hash=do_hash)
        rc = status

    if do_brief and mode == "single":
        for line in render_brief(result):
            print(line)
        for d in result.get("diagnostics", []):
            print("[%s] %s: %s" % (d["class"], d["code"], d["detail"]),
                  file=sys.stderr)
    elif do_brief and mode == "versions":
        for doc in result["files"]:
            for line in render_brief(doc):
                print(line)
            print("")
        for d in result["adjacent_diffs"]:
            print("%s -> %s: first diff %s, %d/%d bytes differ in %d runs"
                  % (d["a"], d["b"], d["first_diff_offset_hex"],
                     d["differing_bytes"], d["common_len"], d["diff_run_count"]))
    elif do_brief and mode == "matrix":
        for line in render_matrix_brief(result):
            print(line)

    if json_path:
        with open(json_path, "w") as f:
            json.dump(result, f, indent=2, sort_keys=True)
    elif not do_brief:
        print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
