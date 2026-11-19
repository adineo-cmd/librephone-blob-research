#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bm2n_probe.py -- clean-room structural probe for the Qualcomm ADSP
``bm2nNN.bin`` container family (vendor/lib/rfsa/adsp).

CLEAN-ROOM STATEMENT
--------------------
This file was written from public, permissively/GPL-licensed sources only:

  * ``QNN/HTP/core/tensor.h``      -- BSD-3-Clause-Clear,
        ``#define TENSOR_MAGIC 0x1337beef`` (line 100)
  * ``QNN/HTP/include/HTP/pickle_header_tags.h`` -- BSD-3-Clause-Clear,
        ``Hdr_MAGIC = 0x7309F72B``, ``Hdr_MAGIC_MULTI = 0x3790FA5C`` and the
        16-bit tag vocabulary used by ``htp_header_locate_field()``
  * ``QNN/HTP/core/serialize_defs.h`` -- BSD-3-Clause-Clear,
        ``OP_SEQNO_MARKER_XOR = 0x1303ee71u``, ``OP_SEQNO_MARKER_MASK``
  * ``drivers/misc/fastrpc.c``     -- GPL-2.0, ADSP domain / rfsa transport

plus **own structural measurements** of the payload bytes. No decompiled
code, no proprietary documentation and no disassembly were used. Every
concrete number this tool prints is either (a) read from the file in front
of it, or (b) one of the two public constants named above. Anything else is
reported as ``[OPEN]`` rather than guessed.

WHAT IS ESTABLISHED (own measurement, see bm2n-fleet-analysis.md)
----------------------------------------------------------------
Two container families occur in the fleet:

``compact``  (48/49 measured payloads)
    ::

        0x00 u32  window size A          (0x200000 / 0x400000 / 0x800000)
        0x04 u32  0                      constant, 48/48
        0x08 u32  7                      constant, 48/48
        0x0c 8B   build-id, 7 ASCII + NUL
        0x14 u32  0xfa0000fa             constant, 48/48
        0x18 u32  4                      constant, 48/48
        0x1c u32  A                      repeat of 0x00
        0x20 u32  N                      segment-table entry count
        0x24 u32  A                      repeat of 0x00
        0x28 u32  0x10400                constant, 48/48
        0x2c      N x { u32 value, u32 kind }
                  last pair is a sentinel:
                    value == ((~N & 0xffff) << 16) | N      (48/48)
                    kind  == base == last file-resident value
        hlen = 0x2c + 8*N                (0x3c, 0x44 or 0x4c)

    then, in order: segment bodies (boundaries = the table's file-resident
    values, ascending, last == base), a prologue, a run of
    ``0x1337BEEF``-tagged records, and a ``0xBEEFF00D`` terminator followed
    by 0..8 padding bytes.

``pickle``   (1/49 measured payload)
    Standard HTP "pickle" header: ``0x7309F72B`` at offset 0 and the
    documented ``htp_header_locate_field()`` record grammar
    (``rlen = recdesc & 0xFFFF``, ``tag = recdesc >> 16``). Observed tags:
    ``Id``, ``Sz``, ``Vr`` (build-id), ``Op`` (textual option string),
    ``Zz`` (end-of-header). The same record/prologue/terminator machinery
    follows. The stretch between the pickle header and the prologue is
    reported as ``pickle_preamble`` and its layout is ``[OPEN]``.

Everything about *meaning* -- what a segment kind byte means, what the
prologue's floats are, what consumes the file at runtime -- is out of scope
and reported as ``[OPEN]``. This tool establishes STRUCTURE, not semantics.

CLI
---
    python3 -I bm2n_probe.py <file> [--json out.json] [--brief]
    python3 -I bm2n_probe.py --fleet <file> [<file> ...] [--json out.json]

Exit status: 0 = no structural violation, 1 = structural violation(s)
found, 2 = usage/IO error.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import os
import struct
import sys

# --- public constants (see clean-room statement) ---------------------------
TENSOR_MAGIC = 0x1337BEEF       # QNN/HTP/core/tensor.h:100
HTP_HDR_MAGIC = 0x7309F72B      # QNN/HTP/include/HTP/pickle_header_tags.h
HTP_HDR_MAGIC_MULTI = 0x3790FA5C
OP_SEQNO_MARKER_XOR = 0x1303EE71  # QNN/HTP/core/serialize_defs.h
OP_SEQNO_MARKER_MASK = 0x1FFFFFFF

# --- own-measured constants (see analysis doc; NOT from any public source) --
RECORD_MAGIC = b"\xef\xbe\x37\x13"      # little-endian TENSOR_MAGIC
RECORD_TERMINATOR = b"\x0d\xf0\xef\xbe"  # 0xBEEFF00D, own measurement only
COMPACT_TABLE_OFF = 0x2C
COMPACT_CONST_08 = 7
COMPACT_CONST_14 = 0xFA0000FA
COMPACT_CONST_18 = 4
COMPACT_CONST_28 = 0x00010400

# Segment-kind -> derived role. The *role* is an own measurement (48/48
# positional agreement); the kind byte's own semantics are [OPEN].
KIND_FILE = 0x00000100
KIND_MEM = 0x00020100
KIND_PROLOGUE_END = 0x000F0100
KIND_ROLE = {
    KIND_FILE: "file-segment",
    KIND_MEM: "non-resident",
    KIND_PROLOGUE_END: "prologue-end",
}

# Prologue grammar (own measurement): after `zeros` bytes of padding comes a
# count-complement sentinel, a 1, a small word, a 38-byte length prefix and
# the RTTI type name literals below.
PROLOGUE_TYPES = (
    b"14ConcreteTensorIN5Tdefs10QuantUint8EE",
)
PROLOGUE_TAIL_FLOAT_ONE = 0x3F800000


class StructureError(Exception):
    """Raised when a file violates the established layout."""

    def __init__(self, message, violations=None):
        super().__init__(message)
        self.violations = list(violations or [message])


# ---------------------------------------------------------------------------
# small helpers
# ---------------------------------------------------------------------------

def count_complement(n):
    """The 16/16 complement word: ((~n & 0xffff) << 16) | n.

    Own measurement: appears in the compact header sentinel with n = N and in
    the prologue sentinel with n = N+1, 48/48 payloads.
    """
    return ((~n & 0xFFFF) << 16) | n


def is_count_complement(word, max_count=64):
    """True if `word` has the count/complement shape, with a small count."""
    lo = word & 0xFFFF
    hi = (word >> 16) & 0xFFFF
    return 0 < lo <= max_count and hi == (~lo & 0xFFFF)


def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def ascii_or_none(raw, min_len=4, max_len=40):
    """Decode a printable-ASCII run, or return None."""
    if not (min_len <= len(raw) <= max_len):
        return None
    if any(b < 0x20 or b > 0x7E for b in raw):
        return None
    return raw.decode("ascii")


def entropy(data):
    """Shannon entropy in bits/byte."""
    if not data:
        return 0.0
    counts = collections.Counter(data)
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def hexdump_line(off, data):
    return "%08x  %-47s  |%s|" % (
        off,
        " ".join("%02x" % b for b in data),
        "".join(chr(b) if 0x20 <= b <= 0x7E else "." for b in data),
    )


# ---------------------------------------------------------------------------
# string extraction
# ---------------------------------------------------------------------------

def extract_strings(buf, min_len=6):
    """All runs of printable ASCII of at least `min_len` bytes.

    Returns a list of dicts: {"offset", "length", "text"}. Offsets are file
    offsets. This is a pure byte-classification scan, no format knowledge.
    """
    out = []
    start = None
    n = len(buf)
    for i in range(n):
        b = buf[i]
        if 0x20 <= b <= 0x7E:
            if start is None:
                start = i
        else:
            if start is not None and i - start >= min_len:
                out.append({
                    "offset": start,
                    "length": i - start,
                    "text": buf[start:i].decode("ascii", "replace"),
                })
            start = None
    if start is not None and n - start >= min_len:
        out.append({
            "offset": start,
            "length": n - start,
            "text": buf[start:].decode("ascii", "replace"),
        })
    return out


# ---------------------------------------------------------------------------
# entropy / histograms
# ---------------------------------------------------------------------------

def entropy_profile(buf, block=65536):
    """Per-block Shannon entropy over fixed-size blocks."""
    blocks = []
    for off in range(0, len(buf), block):
        chunk = buf[off:off + block]
        blocks.append({
            "offset": off,
            "length": len(chunk),
            "entropy": round(entropy(chunk), 4),
        })
    vals = [b["entropy"] for b in blocks]
    return {
        "block_size": block,
        "blocks": blocks,
        "min": round(min(vals), 4) if vals else 0.0,
        "max": round(max(vals), 4) if vals else 0.0,
        "mean": round(sum(vals) / len(vals), 4) if vals else 0.0,
    }


def word_histograms(buf, top=16):
    """Byte-aligned u32 and u16 little-endian value frequencies."""
    nw = len(buf) // 4
    words = struct.unpack_from("<%dI" % nw, buf, 0) if nw else ()
    nh = len(buf) // 2
    shorts = struct.unpack_from("<%dH" % nh, buf, 0) if nh else ()
    wc = collections.Counter(words)
    sc = collections.Counter(shorts)
    return {
        "u32_total": nw,
        "u32_top": [{"value": v, "count": c} for v, c in wc.most_common(top)],
        "u32_distinct": len(wc),
        "u16_total": nh,
        "u16_top": [{"value": v, "count": c} for v, c in sc.most_common(top)],
        "u16_distinct": len(sc),
    }


# ---------------------------------------------------------------------------
# record walk
# ---------------------------------------------------------------------------

def find_records(buf, start, stop):
    """Offsets of every 0x1337BEEF record tag in [start, stop)."""
    out = []
    i = start
    while True:
        i = buf.find(RECORD_MAGIC, i, stop)
        if i < 0:
            return out
        out.append(i)
        i += 4


def walk_records(buf, prologue_end, terminator):
    """Summarise the record stream between the prologue and the terminator.

    Records are delimited *only* by the magic: a record runs from one
    TENSOR_MAGIC to the next. This is the whole of the claimed record
    grammar -- there is no length field (own measurement: no u32 at any of
    the first six word positions of any record equals the record length in
    more than noise-level cases).
    """
    offs = find_records(buf, prologue_end, terminator + 4)
    if not offs:
        return {
            "count": 0,
            "first": None,
            "lengths": {},
            "note": "no 0x1337BEEF record tag found",
        }
    bounds = offs + [terminator]
    lengths = [bounds[i + 1] - bounds[i] for i in range(len(bounds) - 1)]
    uniq = len(set(lengths))
    return {
        "count": len(offs),
        "first": offs[0],
        "last": offs[-1],
        "length_min": min(lengths),
        "length_max": max(lengths),
        "length_median": sorted(lengths)[len(lengths) // 2],
        "all_lengths_multiple_of_4": all(l % 4 == 0 for l in lengths),
        "all_offsets_aligned_4": all(o % 4 == 0 for o in offs),
        "distinct_lengths": uniq,
        "tail_record_length": terminator - offs[-1],
        "lengths": lengths,
    }


# ---------------------------------------------------------------------------
# prologue
# ---------------------------------------------------------------------------

def parse_prologue(buf, start, end):
    """Characterise the prologue block [start, end).

    Own measurement, 48/48 compact payloads: a run of zero padding whose
    length equals the header length, then
    ``cc(N+1), 1, <small>, 38, "14ConcreteTensor...", ...`` and a trailing
    field run ending in the float constant 1.0f. The zero run is absent in
    some variants (the A=0x400000/0x800000 builds), so it is reported, not
    required.
    """
    block = buf[start:end]
    zeros = 0
    while zeros < len(block) and block[zeros] == 0:
        zeros += 1

    info = {
        "start": start,
        "end": end,
        "length": end - start,
        "zero_run": zeros,
        "sentinel": None,
        "count": None,
        "type_strings": [],
    }

    # sentinel: the first count-complement word at/after the zero run
    for off in range(start + (zeros // 4) * 4, end - 3, 4):
        w = u32(buf, off)
        if is_count_complement(w):
            info["sentinel"] = off
            info["count"] = w & 0xFFFF
            break

    # length-prefixed type names
    for lit in PROLOGUE_TYPES:
        pos = buf.find(lit, start, end)
        if pos < 0:
            continue
        prefix = struct.unpack_from("<I", buf, pos - 4)[0] if pos >= start + 4 else None
        info["type_strings"].append({
            "offset": pos,
            "text": lit.decode("ascii"),
            "declared_length": prefix,
            "length_matches": prefix == len(lit),
        })

    # trailing scalar fields
    words = [u32(buf, o) for o in range(start, end - 3, 4)]
    info["tail_words"] = words
    info["has_float_one"] = PROLOGUE_TAIL_FLOAT_ONE in words
    info["pointer_words"] = [
        {"offset": o, "value": u32(buf, o)}
        for o in range(start, end - 3, 4)
        if 0x40000000 <= u32(buf, o) < 0x40100000
    ]
    return info


# ---------------------------------------------------------------------------
# compact family
# ---------------------------------------------------------------------------

def parse_compact(buf, path):
    """Parse the `compact` container family. Raises StructureError."""
    n = len(buf)
    v = []                                  # violations

    if n < COMPACT_TABLE_OFF + 8:
        raise StructureError("file too small for a compact header (%d B)" % n)

    window = u32(buf, 0x00)
    c04 = u32(buf, 0x04)
    c08 = u32(buf, 0x08)
    build_raw = buf[0x0C:0x14]
    c14 = u32(buf, 0x14)
    c18 = u32(buf, 0x18)
    rep1c = u32(buf, 0x1C)
    count = u32(buf, 0x20)
    rep24 = u32(buf, 0x24)
    c28 = u32(buf, 0x28)

    build_id = build_raw.rstrip(b"\x00").decode("ascii", "replace")

    if c04 != 0:
        v.append("header[0x04] = 0x%08x, expected 0" % c04)
    if c08 != COMPACT_CONST_08:
        v.append("header[0x08] = %d, expected %d" % (c08, COMPACT_CONST_08))
    if c14 != COMPACT_CONST_14:
        v.append("header[0x14] = 0x%08x, expected 0x%08x" % (c14, COMPACT_CONST_14))
    if c18 != COMPACT_CONST_18:
        v.append("header[0x18] = %d, expected %d" % (c18, COMPACT_CONST_18))
    if c28 != COMPACT_CONST_28:
        v.append("header[0x28] = 0x%08x, expected 0x%08x" % (c28, COMPACT_CONST_28))
    if not (rep1c == window == rep24):
        v.append(
            "window field not repeated: 0x00=0x%08x 0x1c=0x%08x 0x24=0x%08x"
            % (window, rep1c, rep24)
        )
    if not 1 <= count <= 64:
        raise StructureError(
            "segment count %d out of range 1..64" % count, v or None
        )

    hlen = COMPACT_TABLE_OFF + 8 * count
    if hlen > n:
        raise StructureError(
            "header length 0x%x exceeds file size 0x%x" % (hlen, n), v or None
        )

    if not (build_raw[7:8] in (b"\x00", b"") or all(
            0x20 <= b <= 0x7E for b in build_raw[:7])):
        v.append("build-id at 0x0c is not 7 printable ASCII bytes + NUL")

    # --- segment table -----------------------------------------------------
    entries = []
    for i in range(count - 1):
        off = COMPACT_TABLE_OFF + 8 * i
        value = u32(buf, off)
        kind = u32(buf, off + 4)
        entries.append({"index": i, "offset": off, "value": value,
                        "kind": kind, "kind_hex": "0x%08x" % kind,
                        "role": KIND_ROLE.get(kind, "unknown")})

    sentinel_off = hlen - 8
    sentinel = u32(buf, sentinel_off)
    base = u32(buf, sentinel_off + 4)

    expected_sentinel = count_complement(count)
    if sentinel != expected_sentinel:
        v.append(
            "header sentinel at 0x%04x = 0x%08x, expected %.8x (N=%d)"
            % (sentinel_off, sentinel, expected_sentinel, count)
        )

    if entries:
        last = entries[-1]
        if last["value"] != base:
            v.append(
                "last table entry value 0x%08x does not equal the base field "
                "0x%08x" % (last["value"], base)
            )
        if last["kind"] != KIND_PROLOGUE_END:
            v.append(
                "last table entry kind 0x%08x, expected 0x%08x across 48/48 "
                "measured payloads" % (last["kind"], KIND_PROLOGUE_END)
            )

    # kind vocabulary: low byte 0, bits 8..15 == 0x01
    for e in entries:
        if e["kind"] & 0xFF != 0 or ((e["kind"] >> 8) & 0xFF) != 0x01:
            v.append(
                "entry %d kind 0x%08x outside the observed vocabulary "
                "(low byte 0, bits 8..15 == 0x01)" % (e["index"], e["kind"])
            )
        if e["value"] % 0x100:
            v.append(
                "entry %d value 0x%08x not 0x100-aligned" % (e["index"], e["value"])
            )

    if base > n or base < hlen:
        raise StructureError(
            "base 0x%x outside [0x%x, 0x%x]" % (base, hlen, n), v or None
        )

    # --- derived segment boundaries ---------------------------------------
    resident = sorted({hlen} | {e["value"] for e in entries
                                if hlen <= e["value"] <= base})
    segments = []
    for i in range(len(resident) - 1):
        a, b = resident[i], resident[i + 1]
        segments.append({"index": i, "start": a, "end": b, "length": b - a})
    if not segments:
        segments.append({"index": 0, "start": hlen, "end": base,
                         "length": base - hlen})

    non_resident = [e for e in entries if not hlen <= e["value"] <= base]

    # --- prologue / records / tail ----------------------------------------
    first_rec = buf.find(RECORD_MAGIC, base)
    if first_rec < 0:
        raise StructureError(
            "no 0x1337BEEF record tag found at or after base 0x%x" % base,
            v or None,
        )
    term_at = buf.rfind(RECORD_TERMINATOR)
    if term_at < 0:
        raise StructureError("no 0xBEEFF00D terminator found", v or None)
    if term_at < first_rec:
        raise StructureError(
            "terminator 0x%x precedes first record 0x%x" % (term_at, first_rec),
            v or None,
        )

    prologue = parse_prologue(buf, base, first_rec)
    if prologue["zero_run"] not in (0, hlen):
        v.append(
            "prologue zero run is %d B, expected 0 or hlen (%d B)"
            % (prologue["zero_run"], hlen)
        )
    if not prologue["type_strings"]:
        v.append("prologue carries no known length-prefixed RTTI type name")
    else:
        for t in prologue["type_strings"]:
            if not t["length_matches"]:
                v.append(
                    "prologue type name at 0x%x declares length %s but is %d "
                    "bytes" % (t["offset"], t["declared_length"], len(t["text"]))
                )

    records = walk_records(buf, first_rec, term_at)
    if records["count"] == 0:
        v.append("record region contains no records")
    else:
        if not records["all_lengths_multiple_of_4"]:
            v.append("record boundaries are not all 4-byte multiples")
        if not records["all_offsets_aligned_4"]:
            v.append("record tags are not all 4-byte aligned")

    pad = buf[term_at + 4:]
    if len(pad) > 8:
        v.append("tail padding is %d B, expected <= 8" % len(pad))
    pad_kinds = set(pad)
    if pad and not (pad_kinds == {0x00} or pad_kinds == {0x55}):
        v.append("tail padding is not all-zero and not all-0x55")

    regions = [
        {"name": "header", "start": 0, "end": hlen},
    ]
    for s in segments:
        regions.append({"name": "segment%d" % s["index"],
                        "start": s["start"], "end": s["end"]})
    regions.append({"name": "prologue", "start": base, "end": first_rec})
    regions.append({"name": "records", "start": first_rec, "end": term_at})
    regions.append({"name": "tail", "start": term_at, "end": n})
    for r in regions:
        seg = buf[r["start"]:r["end"]]
        r["length"] = r["end"] - r["start"]
        r["entropy"] = round(entropy(seg), 4)
        r["zero_pct"] = round(100.0 * seg.count(0) / len(seg), 2) if seg else 0.0

    return {
        "family": "compact",
        "header": {
            "length": hlen,
            "window": window,
            "window_hex": "0x%08x" % window,
            "const_0x04": c04,
            "const_0x08": c08,
            "build_id": build_id,
            "build_id_offset": 0x0C,
            "const_0x14": "0x%08x" % c14,
            "const_0x18": c18,
            "repeat_0x1c": "0x%08x" % rep1c,
            "count": count,
            "repeat_0x24": "0x%08x" % rep24,
            "const_0x28": "0x%08x" % c28,
            "sentinel_offset": sentinel_off,
            "sentinel": "0x%08x" % sentinel,
            "sentinel_expected": "0x%08x" % expected_sentinel,
            "base": base,
            "base_hex": "0x%08x" % base,
        },
        "segment_table": {
            "offset": COMPACT_TABLE_OFF,
            "entry_count": count,
            "entries": entries,
            "non_resident_entries": non_resident,
        },
        "segments": segments,
        "prologue": prologue,
        "records": records,
        "tail": {
            "terminator_offset": term_at,
            "terminator": "0xbeeff00d",
            "padding_length": len(pad),
            "padding_hex": pad.hex(),
        },
        "regions": regions,
        "violations": v,
    }


# ---------------------------------------------------------------------------
# pickle family
# ---------------------------------------------------------------------------

def parse_htp_header_tags(buf):
    """Walk the documented HTP pickle-header tag records.

    Faithful to ``htp_header_locate_field()`` in pickle_header_tags.h:
    word 0 is the magic, ``word 1 & 0xFFFF`` is the header length in words,
    then each record is ``recdesc = (tag << 16) | rlen`` with ``rlen`` in
    32-bit words including the descriptor word itself.
    """
    if len(buf) < 12:
        raise StructureError("too short for a pickle header")
    magic = u32(buf, 0)
    hwords = u32(buf, 4) & 0xFFFF
    limit = min(hwords, len(buf) // 4) * 4
    tags = []
    off = 8
    while off < limit:
        recdesc = u32(buf, off)
        rlen = recdesc & 0xFFFF
        tag = recdesc >> 16
        if rlen < 1 or off + 4 * rlen > limit:
            raise StructureError(
                "bad pickle header record at 0x%x (rlen=%d)" % (off, rlen)
            )
        tags.append({
            "offset": off,
            "tag": tag,
            "tag_ascii": "".join(
                chr((tag >> (8 * i)) & 0xFF) for i in range(2)
                if 0x20 <= ((tag >> (8 * i)) & 0xFF) <= 0x7E
            ),
            "rlen_words": rlen,
            "payload_offset": off + 4,
            "payload_bytes": (rlen - 1) * 4,
        })
        off += 4 * rlen
    return {
        "magic": "0x%08x" % magic,
        "header_words": hwords,
        "header_bytes": off,
        "tags": tags,
    }


def parse_pickle(buf, path):
    """Parse the `pickle` container family (lightly: header + shared tail)."""
    v = []
    n = len(buf)
    hdr = parse_htp_header_tags(buf)

    hdr_end = hdr["header_bytes"]
    window = None
    for t in hdr["tags"]:
        if t["tag_ascii"] == "Sz" and t["payload_bytes"] >= 8:
            window = u32(buf, t["payload_offset"] + 4)
            break

    build_id = None
    for t in hdr["tags"]:
        if t["tag_ascii"] == "Vr":
            raw = buf[t["payload_offset"]:t["payload_offset"] + 8]
            build_id = raw.rstrip(b"\x00").decode("ascii", "replace")
            break

    first_rec = buf.find(RECORD_MAGIC, hdr_end)
    if first_rec < 0:
        raise StructureError("no 0x1337BEEF record tag after the pickle header")
    term_at = buf.rfind(RECORD_TERMINATOR)
    if term_at < first_rec:
        raise StructureError("no 0xBEEFF00D terminator after the first record")

    # prologue start: nearest count-complement sentinel before the first record
    pro_start = None
    scan_from = max(hdr_end, first_rec - 512)
    for off in range((scan_from // 4) * 4, first_rec - 3, 4):
        if is_count_complement(u32(buf, off), max_count=64):
            pro_start = off
            break
    if pro_start is None:
        pro_start = first_rec
        v.append("no count-complement prologue sentinel located before the "
                 "first record; prologue not separated")

    prologue = parse_prologue(buf, pro_start, first_rec)
    records = walk_records(buf, first_rec, term_at)

    pad = buf[term_at + 4:]
    if len(pad) > 8:
        v.append("tail padding is %d B, expected <= 8" % len(pad))
    pad_kinds = set(pad)
    if pad and not (pad_kinds == {0x00} or pad_kinds == {0x55}):
        v.append("tail padding is not all-zero and not all-0x55")

    regions = [
        {"name": "pickle_header", "start": 0, "end": hdr_end},
        {"name": "pickle_preamble", "start": hdr_end, "end": pro_start},
        {"name": "prologue", "start": pro_start, "end": first_rec},
        {"name": "records", "start": first_rec, "end": term_at},
        {"name": "tail", "start": term_at, "end": n},
    ]
    for r in regions:
        seg = buf[r["start"]:r["end"]]
        r["length"] = r["end"] - r["start"]
        r["entropy"] = round(entropy(seg), 4)
        r["zero_pct"] = round(100.0 * seg.count(0) / len(seg), 2) if seg else 0.0

    return {
        "family": "pickle",
        "header": {
            "length": hdr_end,
            "magic": hdr["magic"],
            "header_words": hdr["header_words"],
            "build_id": build_id,
            "build_id_offset": next(
                (t["payload_offset"] for t in hdr["tags"]
                 if t["tag_ascii"] == "Vr"), None),
            "window": window,
            "window_hex": "0x%08x" % window if window else None,
            "count": None,
        },
        "pickle_tags": hdr["tags"],
        "segment_table": {
            "offset": None,
            "entry_count": 0,
            "entries": [],
            "note": "pickle_preamble layout is [OPEN] -- no segment table is "
                    "claimed for this family",
        },
        "segments": [],
        "prologue": prologue,
        "records": records,
        "tail": {
            "terminator_offset": term_at,
            "terminator": "0xbeeff00d",
            "padding_length": len(pad),
            "padding_hex": pad.hex(),
        },
        "regions": regions,
        "violations": v,
    }


# ---------------------------------------------------------------------------
# top-level probe
# ---------------------------------------------------------------------------

def detect_family(buf):
    if len(buf) < 12:
        return "unknown"
    magic = u32(buf, 0)
    if magic == HTP_HDR_MAGIC:
        return "pickle"
    if magic == HTP_HDR_MAGIC_MULTI:
        return "pickle-multi"
    return "compact"


def probe_bytes(buf, path="<memory>"):
    """Full probe of one in-memory payload. Returns a result dict."""
    family = detect_family(buf)
    result = {
        "path": path,
        "size": len(buf),
        "md5": hashlib.md5(buf).hexdigest(),
        "sha256": hashlib.sha256(buf).hexdigest(),
        "family": family,
        "violations": [],
        "open": [],
    }

    parsed = {}
    try:
        if family == "pickle":
            parsed = parse_pickle(buf, path)
        elif family == "pickle-multi":
            parsed = parse_pickle(buf, path)
            parsed["family"] = "pickle-multi"
            result["open"].append(
                "Hdr_MAGIC_MULTI (0x3790fa5c) multi-pickle form detected; only "
                "the first pickle header is walked"
            )
        elif family == "compact":
            parsed = parse_compact(buf, path)
        else:
            raise StructureError(
                "unrecognised container: first u32 0x%08x is neither the "
                "compact layout nor a documented HTP pickle magic"
                % (u32(buf, 0) if len(buf) >= 4 else 0)
            )
    except StructureError as exc:
        result["violations"] = exc.violations or [str(exc)]
        result["parse_error"] = str(exc)
        parsed = {"family": family, "header": None, "segment_table": None,
                  "segments": [], "prologue": None, "records": None,
                  "tail": None, "regions": []}

    parse_violations = list(parsed.pop("violations", None) or [])
    result.update(parsed)
    result["violations"] = result["violations"] + parse_violations

    result["strings"] = extract_strings(buf)
    result["entropy"] = entropy_profile(buf)
    result["words"] = word_histograms(buf)

    if family == "compact":
        result["open"].extend([
            "meaning of the window field A (0x200000 / 0x400000 / 0x800000)",
            "semantics of the segment-table `kind` tags (only the positional "
            "roles are established, 48/48)",
            "semantics of the non-resident table entry (kind 0x00020100): "
            "page-aligned, always larger than the file, never a file offset",
            "0xBEEFF00D terminator constant: own measurement only, not found "
            "in any public source",
            "prologue scalar fields beyond the length-prefixed RTTI type name",
            "what consumes these files at runtime (FastRPC / rfsa loader)",
        ])
    elif family.startswith("pickle"):
        result["open"].extend([
            "pickle_preamble layout between the HTP header and the prologue",
            "relationship between this family's records and the compact "
            "family's records (same grammar, unproven byte equivalence)",
        ])

    result["structural_ok"] = not result["violations"]
    return result


def probe_file(path):
    with open(path, "rb") as fh:
        buf = fh.read()
    return probe_bytes(buf, path)


# ---------------------------------------------------------------------------
# fleet diff
# ---------------------------------------------------------------------------

def fleet_diff(paths):
    """Pairwise same-offset byte-identity percentages.

    Method (the lab's F-75 method): for each pair, compare byte i of both
    files over i in [0, min(len_a, len_b)) and report the percentage of
    positions that are byte-identical. No alignment, no diffing -- this is a
    deliberately dumb, reproducible metric whose only virtue is that two
    independent implementations agree on it.
    """
    loaded = []
    for p in paths:
        with open(p, "rb") as fh:
            buf = fh.read()
        loaded.append({
            "path": p,
            "name": os.path.basename(p),
            "size": len(buf),
            "md5": hashlib.md5(buf).hexdigest(),
            "family": detect_family(buf),
            "buf": buf,
        })

    pairs = []
    for i in range(len(loaded)):
        for j in range(i + 1, len(loaded)):
            a, b = loaded[i], loaded[j]
            n = min(a["size"], b["size"])
            same = 0
            ab, bb = a["buf"], b["buf"]
            for k in range(n):
                if ab[k] == bb[k]:
                    same += 1
            pairs.append({
                "a": a["name"],
                "b": b["name"],
                "common_prefix": n,
                "identical_bytes": same,
                "pct": round(100.0 * same / n, 2) if n else 0.0,
                "same_md5": a["md5"] == b["md5"],
                "size_equal": a["size"] == b["size"],
            })

    return {
        "files": [{k: v for k, v in f.items() if k != "buf"} for f in loaded],
        "pairs": pairs,
    }


# ---------------------------------------------------------------------------
# output
# ---------------------------------------------------------------------------

def brief_line(res):
    hdr = res.get("header") or {}
    rec = res.get("records") or {}
    return "%s  %d B  family=%s  build=%s  N=%s  base=%s  records=%s  %s" % (
        os.path.basename(res["path"]),
        res["size"],
        res.get("family"),
        hdr.get("build_id") or "-",
        hdr.get("count"),
        hdr.get("base_hex") or "-",
        rec.get("count"),
        "OK" if res.get("structural_ok") else "VIOLATIONS:%d" % len(res["violations"]),
    )


def render_text(res):
    out = []
    a = out.append
    a("file            : %s" % res["path"])
    a("size            : %d bytes" % res["size"])
    a("md5             : %s" % res["md5"])
    a("sha256          : %s" % res["sha256"])
    a("family          : %s" % res.get("family"))

    hdr = res.get("header")
    if hdr:
        a("")
        a("HEADER")
        for k in ("length", "window_hex", "build_id", "count", "sentinel",
                  "sentinel_expected", "base_hex"):
            if k in hdr and hdr[k] is not None:
                a("  %-18s: %s" % (k, hdr[k]))

    st = res.get("segment_table")
    if st and st.get("entries") is not None:
        a("")
        a("SEGMENT TABLE @ 0x%04x, %d entr%s"
          % (st["offset"] or 0, st["entry_count"],
             "y" if st["entry_count"] == 1 else "ies"))
        for e in st["entries"]:
            a("  [%d] value=%#010x kind=%s  role=%s"
              % (e["index"], e["value"], e["kind_hex"], e["role"]))
        if st.get("non_resident_entries"):
            a("  non-resident: %s" % ", ".join(
                "%#010x" % e["value"] for e in st["non_resident_entries"]))

    if res.get("regions"):
        a("")
        a("REGIONS")
        a("  %-10s %-11s %-11s %10s %7s %8s"
          % ("name", "start", "end", "length", "entropy", "zero%"))
        for r in res["regions"]:
            a("  %-10s 0x%08x  0x%08x  %10d %7.3f %7.1f%%"
              % (r["name"], r["start"], r["end"], r["length"],
                 r["entropy"], r["zero_pct"]))

    pro = res.get("prologue")
    if pro:
        a("")
        a("PROLOGUE [0x%x, 0x%x) %d B" % (pro["start"], pro["end"], pro["length"]))
        a("  zero run      : %d B" % pro["zero_run"])
        if pro["sentinel"] is not None:
            a("  sentinel      : @0x%x count=%d" % (pro["sentinel"], pro["count"]))
        for t in pro["type_strings"]:
            a("  type name     : %r (declared_len=%s ok=%s)"
              % (t["text"], t["declared_length"], t["length_matches"]))
        a("  float 1.0f    : %s" % pro["has_float_one"])

    rec = res.get("records")
    if rec and rec.get("count"):
        a("")
        a("RECORDS")
        a("  count         : %d" % rec["count"])
        a("  first / last  : 0x%x / 0x%x" % (rec["first"], rec["last"]))
        a("  length min/max: %d / %d" % (rec["length_min"], rec["length_max"]))
        a("  length median : %d" % rec["length_median"])
        a("  all lengths x4: %s" % rec["all_lengths_multiple_of_4"])

    tail = res.get("tail")
    if tail:
        a("")
        a("TAIL")
        a("  terminator    : %s @0x%x" % (tail["terminator"],
                                          tail["terminator_offset"]))
        a("  padding       : %d B %s" % (tail["padding_length"],
                                         tail["padding_hex"] or "-"))

    ent = res.get("entropy")
    if ent:
        a("")
        a("ENTROPY (%d B blocks): min %.2f max %.2f mean %.2f"
          % (ent["block_size"], ent["min"], ent["max"], ent["mean"]))
        a("  " + " ".join("%.1f" % b["entropy"] for b in ent["blocks"][:24]))

    words = res.get("words")
    if words:
        a("")
        a("WORD HISTOGRAM (u32, top 8 of %d)" % words["u32_total"])
        for w in words["u32_top"][:8]:
            a("  %08x  %d" % (w["value"], w["count"]))
        a("SHORT-WORD HISTOGRAM (u16, top 8 of %d)" % words["u16_total"])
        for w in words["u16_top"][:8]:
            a("  %04x  %d" % (w["value"], w["count"]))

    strings = res.get("strings") or []
    a("")
    a("STRINGS (>=6 printable ASCII): %d" % len(strings))
    for s in strings[:40]:
        a("  %08x %4d  %s" % (s["offset"], s["length"], s["text"][:110]))
    if len(strings) > 40:
        a("  ... %d more" % (len(strings) - 40))

    if res.get("violations"):
        a("")
        a("STRUCTURAL VIOLATIONS")
        for m in res["violations"]:
            a("  - %s" % m)
    else:
        a("")
        a("STRUCTURAL VIOLATIONS: none")

    if res.get("open"):
        a("")
        a("[OPEN] (not claimed by this tool)")
        for m in res["open"]:
            a("  - %s" % m)
    return "\n".join(out)


def render_fleet_text(fleet):
    out = ["FLEET DIFF -- same-offset byte identity, common prefix",
           "",
           "%-34s %10s %-8s %s" % ("file", "bytes", "family", "md5")]
    for f in fleet["files"]:
        out.append("%-34s %10d %-8s %s"
                   % (f["name"], f["size"], f["family"], f["md5"]))
    out.append("")
    out.append("%-30s %-30s %10s %10s %8s %s"
               % ("a", "b", "prefix", "identical", "pct", "note"))
    for p in fleet["pairs"]:
        note = []
        if p["same_md5"]:
            note.append("same md5")
        if not p["size_equal"]:
            note.append("sizes differ")
        out.append("%-30s %-30s %10d %10d %7.2f%% %s"
                   % (p["a"], p["b"], p["common_prefix"],
                      p["identical_bytes"], p["pct"], ",".join(note) or "-"))
    return "\n".join(out)


def json_ready(obj):
    """Make a result JSON-serialisable (records include long int lists)."""
    if isinstance(obj, dict):
        return {k: json_ready(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [json_ready(v) for v in obj]
    if isinstance(obj, bytes):
        return obj.hex()
    return obj


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog="bm2n_probe.py",
        description="Clean-room structural probe for Qualcomm ADSP bm2nNN.bin "
                    "payloads. Structure only; semantics are [OPEN].",
    )
    ap.add_argument("files", nargs="+", help="payload file(s)")
    ap.add_argument("--json", metavar="PATH", help="write full JSON to PATH")
    ap.add_argument("--brief", action="store_true",
                    help="one line per file instead of the full report")
    ap.add_argument("--fleet", action="store_true",
                    help="pairwise same-offset byte-identity mode")
    args = ap.parse_args(argv)

    if any(not os.path.isfile(p) for p in args.files):
        for p in args.files:
            if not os.path.isfile(p):
                sys.stderr.write("error: not a file: %s\n" % p)
        return 2

    if args.fleet:
        if len(args.files) < 2:
            sys.stderr.write("error: --fleet needs at least two files\n")
            return 2
        fleet = fleet_diff(args.files)
        if args.json:
            with open(args.json, "w") as fh:
                json.dump(json_ready(fleet), fh, indent=2)
                fh.write("\n")
        sys.stdout.write(render_fleet_text(fleet) + "\n")
        return 0

    results = []
    rc = 0
    for p in args.files:
        try:
            res = probe_file(p)
        except OSError as exc:
            sys.stderr.write("error: %s: %s\n" % (p, exc))
            rc = 2
            continue
        results.append(res)
        if not res["structural_ok"]:
            rc = 1

    if args.json:
        payload = results[0] if len(results) == 1 else results
        with open(args.json, "w") as fh:
            json.dump(json_ready(payload), fh, indent=2)
            fh.write("\n")

    if args.brief:
        for res in results:
            sys.stdout.write(brief_line(res) + "\n")
    else:
        for i, res in enumerate(results):
            if i:
                sys.stdout.write("\n" + "=" * 78 + "\n\n")
            sys.stdout.write(render_text(res) + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
