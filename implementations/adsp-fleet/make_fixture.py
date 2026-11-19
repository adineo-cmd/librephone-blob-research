#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""make_fixture.py -- deterministic synthetic fixtures for bm2n_probe.py.

WHY SYNTHETIC
-------------
The real ``bm2nNN.bin`` payloads are proprietary vendor blobs; the repo
``.gitignore`` excludes ``*.bin`` and the lab's rule is that no real payload
bytes are ever committed. So, following the pattern already used in
``implementations/qca-bt/make_fixture.py`` and
``implementations/mediatek/container/``, the fixtures here are **self-made
bytes** generated from the structural layout established by measurement
(see ``bm2n-fleet-analysis.md``). They prove the probe against the layout,
not against any vendor's content.

Every byte is deterministic: a SHA-256 counter stream keyed by a per-fixture
tag. Re-running this script reproduces every fixture byte-for-byte, which
``test_bm2n_probe.py`` verifies.

WHAT GETS BUILT
---------------
Sizes mirror the real fleet magnitudes so the probe is exercised at realistic
scale (the largest explains why the record walk is O(n) and not O(n^2)):

  fixtures/bm2n14_synthetic.bin      103,168 B  N=2  A=0x200000   (bm2n14)
  fixtures/bm2n06_synthetic.bin      864,824 B  N=2  A=0x400000   (bm2n06)
  fixtures/bm2n12_synthetic.bin    2,623,528 B  N=3  A=0x200000   (bm2n12)
  fixtures/bm2n12_pickle_synthetic.bin 2,359,272 B  pickle family

plus three deliberately-broken fixtures for the error paths:

  fixtures/bad_magic_synthetic.bin    unrecognised container (exit 1)
  fixtures/bad_constant_synthetic.bin header constant wrong     (exit 1)
  fixtures/truncated_synthetic.bin    body cut mid-records      (exit 1)

All fixtures are ``*.bin`` and therefore git-ignored -- re-run this script
(or let the test suite call :func:`build_all`) to materialise them.

CLEAN-ROOM
----------
Only the structural layout is reproduced. The layout itself is an own
measurement of payload bytes plus two constants taken from public
BSD-3-Clause-Clear Qualcomm headers (``TENSOR_MAGIC`` in ``tensor.h``,
``Hdr_MAGIC``/tag grammar in ``pickle_header_tags.h``). No proprietary
content, no decompilation.
"""

from __future__ import annotations

import hashlib
import os
import struct
import sys

FIXTURE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "fixtures")

# --- public constants (QNN/HTP headers, BSD-3-Clause-Clear) ----------------
TENSOR_MAGIC = 0x1337BEEF
HTP_HDR_MAGIC = 0x7309F72B
HTP_TAG_IDENT = ord("I") + 256 * ord("d")
HTP_TAG_SIZE = ord("S") + 256 * ord("z")
HTP_TAG_VERSION = ord("V") + 256 * ord("r")
HTP_TAG_OPTIONS = ord("O") + 256 * ord("p")
HTP_TAG_ENDHDR = ord("Z") + 256 * ord("z")

# --- own-measured constants ------------------------------------------------
RECORD_TERMINATOR = 0xBEEFF00D
KIND_FILE = 0x00000100
KIND_MEM = 0x00020100
KIND_PROLOGUE_END = 0x000F0100
TYPE_NAME = b"14ConcreteTensorIN5Tdefs10QuantUint8EE"   # 38 bytes
FLOAT_ONE = 0x3F800000

# fleet magnitudes taken from the real payloads
FLEET_SIZES = {
    "bm2n06": 864824,
    "bm2n08": 3091896,
    "bm2n12": 2623528,
    "bm2n13": 1082824,
    "bm2n14": 103168,
    "bm2n15": 1082856,
}


# ---------------------------------------------------------------------------
# deterministic byte source
# ---------------------------------------------------------------------------

def tagcat(tag, suffix):
    """Concatenate a tag (str or bytes) with a bytes suffix, always bytes."""
    if isinstance(tag, str):
        tag = tag.encode()
    return tag + suffix


def pattern(n, tag):
    """Deterministic pseudo-random byte stream: SHA-256 of a counter, tagged
    per fixture so unrelated fixtures never share payload bytes."""
    tag = tag.encode() if isinstance(tag, str) else tag
    out = bytearray()
    counter = 0
    while len(out) < n:
        out += hashlib.sha256(b"%s:%d" % (tag, counter)).digest()
        counter += 1
    return bytes(out[:n])


def count_complement(n):
    return ((~n & 0xFFFF) << 16) | n


def align4(n):
    return (n + 3) & ~3


# ---------------------------------------------------------------------------
# record stream
# ---------------------------------------------------------------------------

def record_stream(tag, total_bytes, seed=0):
    """A synthetic record stream of exactly `total_bytes`.

    Grammar (own measurement, 48/48 real payloads): each record starts with
    the 4-byte TENSOR_MAGIC and runs to the next magic; lengths are multiples
    of 4 and the observed minimum is 36-40 bytes. There is no length field.

    The stream is closed with the 0xBEEFF00D terminator, so the caller passes
    the number of payload bytes to fill.
    """
    tag = tag.encode() if isinstance(tag, str) else tag
    body = bytearray()
    short_lengths = (40, 44, 48, 56, 64, 76, 96, 104, 128)
    i = 0
    while len(body) + 40 + 4 <= total_bytes:
        # vary the record length in a deterministic cycle, clamped so we do
        # not overrun the budget
        want = short_lengths[i % len(short_lengths)]
        want = align4(want)
        if len(body) + want + 4 > total_bytes:
            want = align4(total_bytes - len(body) - 4)
            if want < 40:
                break
        body += struct.pack("<I", TENSOR_MAGIC)
        body += struct.pack("<I", (i + seed) & 0x1FFFFFFF)
        body += pattern(want - 8, tagcat(tag, b":rec%d" % i))
        i += 1
    # pad the remainder with a final record of legal size
    remainder = total_bytes - len(body) - 4
    if remainder >= 40:
        remainder = align4(remainder)
        body += struct.pack("<I", TENSOR_MAGIC)
        body += struct.pack("<I", (i + seed) & 0x1FFFFFFF)
        body += pattern(remainder - 8, tagcat(tag, b":rec-tail"))
    elif remainder > 0:
        # absorb the crumbs into the previous record's pad area
        body += pattern(align4(total_bytes - len(body) - 4), tagcat(tag, b":pad"))
    assert len(body) + 4 <= total_bytes, (len(body), total_bytes)
    body += struct.pack("<I", RECORD_TERMINATOR)
    while len(body) < total_bytes:
        body += b"\x00"
    return bytes(body[:total_bytes])


# ---------------------------------------------------------------------------
# compact family
# ---------------------------------------------------------------------------

def build_compact(tag, file_size, count, window, build_id,
                  kinds, mem_value=None, prologue_tail_words=None,
                  record_seed=0, bad_constant=False):
    """Build one synthetic `compact` container of exactly `file_size` bytes.

    `kinds` is the list of kinds for the file-resident entries; the sentinel
    pair is appended automatically. `mem_value`, when given, adds one
    non-resident KIND_MEM entry in front (as the real A=0x200000/0x400000
    variants do).
    """
    assert len(build_id.encode()) == 7, "build-id is 7 ASCII bytes"

    # N counts every table pair including the sentinel pair; a non-resident
    # KIND_MEM entry (when requested) sits in front of the file-resident ones.
    expect_count = len(kinds) + (1 if mem_value is not None else 0) + 1
    assert count == expect_count, (
        "count=%d but kinds=%d + mem=%s + sentinel => %d"
        % (count, len(kinds), mem_value is not None, expect_count))

    hlen = 0x2C + 8 * count

    # ---- prologue tail-word run -------------------------------------------
    # Own measurement (real fleet): after the 38-byte type name come 9-11 u32
    # fields. Every measured file includes 0x00000411 and the float constant
    # 1.0f, and most carry a 0x40xxxxxx word that decodes to an in-file
    # offset. Mirror that shape rather than inventing a different one.
    if prologue_tail_words is None:
        prologue_tail_words = 9 if count == 2 else 11
    tail = [0x00000411, 1]
    if count > 2:
        tail += [1, 0]
    tail += [FLOAT_ONE]
    if count > 2:
        tail += [2]
    tail += [0x40001110, 0x60, 0x80]
    while len(tail) < prologue_tail_words:
        tail.append(1)
    tail = tail[:prologue_tail_words]

    prologue_len = hlen + 16 + len(TYPE_NAME) + 2 + 4 * len(tail)

    # ---- layout ------------------------------------------------------------
    # base is the last file-resident boundary => the prologue start.
    # Choose base so the file splits sensibly: header + bodies + prologue +
    # records + terminator + pad == file_size.
    # Give the bodies ~40% and records the rest, at 0x100 alignment.
    tail_total = 4 + 4                      # terminator + one pad word
    overhead = hlen + prologue_len + tail_total
    if file_size <= overhead + 4096:
        raise ValueError("fixture too small: %d B" % file_size)

    # allocate: `n_file` file-resident segments, ascending, last boundary is base
    n_file = len(kinds)
    body_budget = file_size - overhead          # bytes available to bodies+records
    if body_budget < 8192:
        raise ValueError("fixture too small: %d B" % file_size)

    body_span = align_page(int(body_budget * 0.60), 0x100)
    if body_span < 0x1000:
        body_span = 0x1000
    # Table VALUES are 0x100-aligned (48/48 real payloads). The first segment
    # starts at the raw header end, which need not be aligned; every
    # subsequent boundary is.
    bounds = [hlen]
    for i in range(1, n_file + 1):
        bounds.append(align_page(hlen + body_span * i // n_file, 0x100))
    # force strictly ascending
    for i in range(1, len(bounds)):
        if bounds[i] <= bounds[i - 1]:
            bounds[i] = bounds[i - 1] + 0x100
    base = bounds[-1]

    if base + prologue_len + 2048 >= file_size:
        raise ValueError("no room for records at %d B" % file_size)

    rec_bytes = file_size - base - prologue_len
    rec_bytes = align4(rec_bytes)

    # ---- header ------------------------------------------------------------
    hdr = bytearray()
    hdr += struct.pack("<I", window)
    hdr += struct.pack("<I", 0xDEAD if bad_constant else 0)   # 0x04 must be 0
    hdr += struct.pack("<I", 7)                               # 0x08
    hdr += build_id.encode().ljust(8, b"\x00")                # 0x0c..0x13
    hdr += struct.pack("<I", 0xFA0000FA)                      # 0x14
    hdr += struct.pack("<I", 4)                               # 0x18
    hdr += struct.pack("<I", window)                          # 0x1c
    hdr += struct.pack("<I", count)                           # 0x20
    hdr += struct.pack("<I", window)                          # 0x24
    hdr += struct.pack("<I", 0x00010400)                      # 0x28
    assert len(hdr) == 0x2C

    if mem_value is not None:
        hdr += struct.pack("<II", mem_value, KIND_MEM)
    for i, kind in enumerate(kinds):
        hdr += struct.pack("<II", bounds[i + 1], kind)
    hdr += struct.pack("<II", count_complement(count), base)
    assert len(hdr) == hlen, (len(hdr), hlen)

    # ---- bodies ------------------------------------------------------------
    body = bytearray()
    for i in range(n_file):
        a, b = bounds[i], bounds[i + 1]
        body += pattern(b - a, tagcat(tag, b":seg%d" % i))
    assert len(body) == base - hlen, (len(body), base - hlen)

    # ---- prologue ----------------------------------------------------------
    pro = bytearray()
    pro += b"\x00" * hlen
    pro += struct.pack("<I", count_complement(count + 1))
    pro += struct.pack("<I", 1)
    pro += struct.pack("<I", 0)
    pro += struct.pack("<I", len(TYPE_NAME))
    pro += TYPE_NAME
    pro += b"\x00" * 2                      # align the string to 4 bytes
    for w in tail:
        pro += struct.pack("<I", w)
    if len(pro) < prologue_len:
        pro += b"\x00" * (prologue_len - len(pro))
    pro = bytes(pro[:prologue_len])

    # ---- records + tail ----------------------------------------------------
    recs = record_stream(tagcat(tag, b":records"), rec_bytes, record_seed)

    out = bytes(hdr) + bytes(body) + pro + recs
    assert len(out) == file_size, (len(out), file_size)
    return out


def align_page(n, page=0x100):
    return (n + page - 1) // page * page


# ---------------------------------------------------------------------------
# pickle family
# ---------------------------------------------------------------------------

def _htp_record(tag, payload_words):
    """One pickle-header record: recdesc=(tag<<16)|rlen, then payload words.

    rlen counts 32-bit words INCLUDING the descriptor word
    (htp_header_locate_field in pickle_header_tags.h).
    """
    rlen = len(payload_words) + 1
    return struct.pack("<I", (tag << 16) | rlen) + b"".join(
        struct.pack("<I", w) for w in payload_words)


def build_pickle(tag, file_size, window, build_id,
                 prologue_tail_words=11, record_seed=0):
    """Build a synthetic `pickle`-family container of exactly `file_size`."""
    assert len(build_id.encode()) == 7

    ident_words = [0] * 50                      # 200-byte Id payload
    size_words = [0x0008FFF9, window, 0x00000000, 0x00000049]
    # Vr payload, own measurement: 8 raw ASCII bytes = build-id + NUL, read
    # back by the probe as a NUL-stripped string. Emit as two LE words so the
    # bytes round-trip exactly (no truncation).
    vr_bytes = build_id.encode().ljust(8, b"\x00")[:8]
    version_words = [
        int.from_bytes(vr_bytes[0:4], "little"),
        int.from_bytes(vr_bytes[4:8], "little"),
    ]
    opt_text = (b"O=2;initial_sequencer=df;df_subsequencer=por_dp;"
                b"00dp_op_sort_mode=overlap;allocator_version=reserved;")
    opt_words = []
    padded = opt_text + b"\x00" * ((4 - len(opt_text) % 4) % 4)
    for i in range(0, len(padded), 4):
        opt_words.append(int.from_bytes(padded[i:i + 4], "little"))

    body = bytearray()
    body += _htp_record(HTP_TAG_IDENT, ident_words)
    body += _htp_record(HTP_TAG_SIZE, size_words)
    body += _htp_record(HTP_TAG_VERSION, version_words)
    body += _htp_record(HTP_TAG_OPTIONS, opt_words)
    body += _htp_record(HTP_TAG_ENDHDR, [])

    header_bytes = 8 + len(body)
    header_words = header_bytes // 4
    hdr = struct.pack("<II", HTP_HDR_MAGIC, header_words & 0xFFFF) + bytes(body)

    # post-header: a small integer field run, then the prologue
    preamble = bytearray()
    preamble += struct.pack("<I", 0xFA0000FA)
    preamble += struct.pack("<I", 4)
    preamble += struct.pack("<I", window)
    preamble += struct.pack("<I", 4)
    preamble += struct.pack("<I", window)
    preamble += struct.pack("<I", 0x00000400)
    preamble += struct.pack("<I", 1)
    preamble += struct.pack("<I", 0x00001E00)
    preamble += struct.pack("<I", 0x00000100)
    preamble += struct.pack("<I", 0)
    while len(preamble) % 0x100:
        preamble += b"\x00"

    tail = [0x00000411, 1, 1, 0, FLOAT_ONE]
    while len(tail) < prologue_tail_words:
        tail.append(1 if len(tail) % 3 else 0)
    tail = tail[:prologue_tail_words]

    pro = bytearray()
    pro += struct.pack("<I", count_complement(5))     # N+1 for N=4 entries
    pro += struct.pack("<I", 1)
    pro += struct.pack("<I", 0)
    pro += struct.pack("<I", len(TYPE_NAME))
    pro += TYPE_NAME
    pro += b"\x00" * 2
    for w in tail:
        pro += struct.pack("<I", w)
    pro = bytes(pro)

    overhead = len(hdr) + len(preamble) + len(pro) + 8
    if file_size <= overhead + 4096:
        raise ValueError("pickle fixture too small: %d B" % file_size)
    rec_bytes = align4(file_size - overhead)
    recs = record_stream(tagcat(tag, b":records"), rec_bytes, record_seed)

    out = bytes(hdr) + bytes(preamble) + pro + recs
    if len(out) < file_size:
        out += b"\x00" * (file_size - len(out))
    assert len(out) == file_size, (len(out), file_size)
    return out


# ---------------------------------------------------------------------------
# deliberate breakage
# ---------------------------------------------------------------------------

def build_bad_magic(tag, file_size=4096):
    """Unrecognised container: no compact layout, no pickle magic."""
    return pattern(file_size, tag)


def build_truncated(tag, keep_fraction=0.55):
    """A synthetic bm2n12 with the tail (terminator + records) chopped off.

    The header claims a base and segment table that the file can no longer
    satisfy, which is exactly the diagnostic the probe must report rather
    than crash on.
    """
    full = build_compact(tag, FLEET_SIZES["bm2n12"], 3, 0x200000,
                         "2c855d1", [KIND_PROLOGUE_END],
                         mem_value=0x02C39000)
    return full[: int(len(full) * keep_fraction)]


# ---------------------------------------------------------------------------
# driver
# ---------------------------------------------------------------------------

def build_all(out_dir=None):
    """Build every fixture. Returns a list of (name, bytes)."""
    d = out_dir or FIXTURE_DIR
    os.makedirs(d, exist_ok=True)

    jobs = [
        ("bm2n14_synthetic.bin",
         build_compact("fx-bm2n14", FLEET_SIZES["bm2n14"], 2, 0x200000,
                       "2a8527c", [KIND_PROLOGUE_END], prologue_tail_words=9)),
        ("bm2n06_synthetic.bin",
         build_compact("fx-bm2n06", FLEET_SIZES["bm2n06"], 2, 0x400000,
                       "4bd22b0", [KIND_PROLOGUE_END], prologue_tail_words=9)),
        ("bm2n12_synthetic.bin",
         build_compact("fx-bm2n12", FLEET_SIZES["bm2n12"], 3, 0x200000,
                       "2c855d1", [KIND_PROLOGUE_END],
                       mem_value=0x02C39000)),
        ("bm2n12_pickle_synthetic.bin",
         build_pickle("fx-bm2n12-pickle",
                      build_pickle_size(FLEET_SIZES["bm2n12"]),
                      0x200000, "2c855d1")),
        ("bad_magic_synthetic.bin", build_bad_magic("fx-bad-magic")),
        ("bad_constant_synthetic.bin",
         build_compact("fx-bad-const", 65536, 2, 0x200000, "0000000",
                       [KIND_PROLOGUE_END], prologue_tail_words=9,
                       bad_constant=True)),
        ("truncated_synthetic.bin", build_truncated("fx-truncated")),
    ]
    return jobs


def build_pickle_size(n):
    """Round a target size down to something the pickle builder can hit."""
    return (n // 0x1000) * 0x1000


def main():
    jobs = build_all()
    total = 0
    for name, blob in jobs:
        path = os.path.join(FIXTURE_DIR, name)
        with open(path, "wb") as fh:
            fh.write(blob)
        total += len(blob)
        print("%-34s %9d bytes  md5=%s"
              % (name, len(blob), hashlib.md5(blob).hexdigest()))
    print("\n%d fixtures, %d bytes total, in %s"
          % (len(jobs), total, FIXTURE_DIR))
    print("fleet magnitudes mirrored: " + ", ".join(
        "%s=%d" % (k, v) for k, v in sorted(FLEET_SIZES.items())))
    print("\nnote: fixtures are *.bin and therefore git-ignored; re-run this "
          "script to materialise them.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
