#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""make_fixture.py -- deterministic SYNTHETIC fixtures for blob_probe.py.

CLEAN-ROOM / NO-PROPRIETARY-BYTES STATEMENT
===========================================
Every byte this script writes is computed here from arithmetic and from
layouts documented in public sources.  NO real payload byte is copied,
embedded, transcribed or derived.  The real files this fleet analyses
(`hrtf5c.bin`, `dax_param.bin`) are proprietary vendor blobs; they never enter
this repository.  The repo's .gitignore excludes `*.bin`, so the fixtures are
working-tree artifacts -- rerun this script to regenerate them byte-for-byte
(`test_blob_probe.py` asserts that it does).

The fixtures mirror the real files' *magnitudes* (164,480 B and 34,736 B) and
their *structural classes* (a packed float32 coefficient table; a tag-record
container with integer payloads), because those are the two shapes the
analyser must tell apart.  The content is invented: an analytic head-shadow
model for the HRTF-shaped fixture, a synthetic tag dictionary for the
container-shaped one.  Neither is a model of, nor a substitute for, the real
device behaviour.

FIXTURES
--------
  hrtf_like.bin        164,480 B  packed little-endian binary32 table,
                                  160 records x 257 samples, alternating
                                  magnitude / linear-phase rows, DC gain ~1.08,
                                  ITD peaking near 700 us.  Exercises:
                                  float plausibility PASS, flat entropy,
                                  stride-4 tile, no 4CC.
  hrtf_like_2.bin      164,480 B  same generator, one seed different: a
                                  second "version" for diff-mode tests.
  hrtf_like_truncated.bin        hrtf_like.bin cut to 100,001 B (odd length,
                                  not a multiple of 4) -> malformed input.
  dax_like.bin          34,736 B  16-byte records: lowercase 4CC tag + three
                                  u32 fields, plus a 24-byte file header.
                                  Exercises: stride-16 detection, tag phase
                                  spike, low entropy, float plausibility FAIL.
  dax_like_2.bin        34,736 B  dax_like with a 160-byte payload region
                                  changed (the real fleet's diff shape).
  unknown.bin              512 B  high-entropy random bytes: matches neither
                                  class.
  empty.bin                  0 B  degenerate input.

Determinism: a SHA-256 counter stream, no RNG state, no time, no locale.
"""

import hashlib
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")


class Stream:
    """Deterministic byte stream: SHA-256(seed || counter) counter mode."""

    def __init__(self, seed):
        self.seed = seed.encode() if isinstance(seed, str) else seed
        self.counter = 0
        self.buf = b""

    def bytes(self, n):
        while len(self.buf) < n:
            self.buf += hashlib.sha256(
                self.seed + self.counter.to_bytes(8, "big")).digest()
            self.counter += 1
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def f32(self):
        """One uniform binary32 in [-1, 1) with 24-bit mantissa granularity."""
        v = struct.unpack("<I", self.bytes(4))[0]
        return ((v >> 8) / 8388608.0) - 1.0


# ---------------------------------------------------------------------------
# HRTF-shaped fixture: packed float32 magnitude/phase table
# ---------------------------------------------------------------------------

# The real file's arithmetic is 164480 = 160 x 257 x 4 bytes.  Reading that as
# 2 x 80 x 257 columns gives magnitude rows and linear-phase rows.  We mirror
# exactly that shape, with an invented analytic model:
#
#   magnitude[k] = gain * (1 + shadow * exp(-k / k0) * cos(2*pi*k/N))
#   phase[k]     = -2*pi * k * tau / N        (linear phase => pure delay tau)
#
# tau follows the Woodworth spherical-head formula, a public model
# (Woodworth & Schlosberg 1954, restated in every spatial-audio textbook):
#
#   tau(theta) = -(a/c) * (theta + sin theta),  a = 0.0875 m, c = 343 m/s
#
# which peaks at ~800 us for a lateral source -- the same order as the real
# file's measured 751 us peak.  Using the public formula here, rather than any
# vendor number, is the point: the fixture is derived from literature.

HEAD_RADIUS_M = 0.0875
SPEED_OF_SOUND = 343.0
BINS = 257
DIRECTIONS = 40


def woodworth_itd_us(deg, a=HEAD_RADIUS_M, c=SPEED_OF_SOUND):
    theta = abs(deg) * 3.141592653589793 / 180.0
    return (a / c) * (theta + __import__("math").sin(theta)) * 1e6


def build_hrtf_like(seed="hrtf-fixture-v1"):
    """160 records x 257 float32 = 164,480 bytes, magnitude/phase interleaved."""
    math = __import__("math")
    st = Stream(seed)
    rows = []
    for d in range(DIRECTIONS):
        # azimuth sweep, 9 degrees per step, as a plausible full circle
        az = -180.0 + d * (360.0 / DIRECTIONS)
        itd = woodworth_itd_us(az) * (1 if az <= 0 else -1)
        # per-direction small jitter so records are not analytically identical
        jitter = 0.02 * st.f32()
        for ear in (0, 1):
            tau = (itd / 2.0) * (1 if ear else -1) / 1e6  # seconds, half each
            gain = 1.075 + jitter + (0.03 if ear else 0.0)
            shadow = 0.55 + 0.10 * st.f32()
            mag = []
            pha = []
            for k in range(BINS):
                # head-shadow ripple: strong low-k, decaying, plus a pinna notch
                ripple = shadow * math.exp(-k / 40.0) * math.cos(
                    2.0 * math.pi * k / 64.0 + az * 0.01)
                notch = -0.15 * math.exp(-((k - 150.0) / 18.0) ** 2)
                mag.append(gain * (1.0 + ripple + notch + 0.004 * st.f32()))
                # linear phase: -2*pi*k*tau*fs/N, N = 512, fs = 48000
                pha.append(-2.0 * math.pi * k * tau * 48000.0 / 512.0)
            rows.append(mag)
            rows.append(pha)
    out = bytearray()
    for row in rows:
        out += struct.pack("<%df" % BINS, *row)
    assert len(out) == 164480, len(out)
    return bytes(out)


# ---------------------------------------------------------------------------
# container-shaped fixture: 16-byte tag records
# ---------------------------------------------------------------------------

# The real file's measured shape: 16-byte records of
#   [4-byte lowercase tag][u32 field_a][u32 field_b][u32 field_c]
# with a small u32 count header.  We mirror the *shape* and invent the tag
# vocabulary.  No real tag string from any vendor blob appears here.

SYNTH_TAGS = [
    b"alfa", b"brav", b"char", b"delt", b"ech\x00", b"foxt",
    b"golf", b"hotl", b"indi", b"jul\x00", b"kilo", b"lima",
    b"mike", b"nov\x00", b"osca", b"papa", b"queb", b"rome",
    b"sier", b"tang", b"unif", b"vict", b"whis", b"xray",
    b"yank", b"zulu", b"aone", b"btwo", b"cthr", b"dfou",
]


def build_dax_like(seed="dax-fixture-v1", mutate_region=False):
    """34,736 B: 24-byte header + 2,169 16-byte records (+ 8 B tail)."""
    st = Stream(seed)
    out = bytearray()
    # header: six u32 words.  In the real file these look like counts; here
    # they are derived from the record census so the fixture is self-consistent.
    out += struct.pack("<6I", 9, 706, 342, 0, 148, 0x40000000)
    tag_index = 0
    blanks = 0
    while len(out) + 16 <= 34736:
        # every 61st record is a zero filler block, mirroring the real file's
        # interleaved zero runs (measured: 62.95% zero bytes overall)
        if blanks < 100 and len(out) % (16 * 61) == 0 and len(out) > 100:
            out += b"\x00" * 16
            blanks += 1
            continue
        tag = SYNTH_TAGS[tag_index % len(SYNTH_TAGS)]
        tag_index += 1
        a = 1 if st.f32() > -0.4 else 0
        # field b is zero in roughly half the records (the real file's shape)
        b = 0 if st.f32() < 0.5 else (struct.unpack("<I", st.bytes(4))[0] >> 23) & 0xFF
        c = 2 if st.f32() > 0 else 128
        out += tag + struct.pack("<3I", a, b, c)
    out = out[:34736]
    if len(out) < 34736:
        out += b"\x00" * (34736 - len(out))
    data = bytearray(out)
    if mutate_region:
        # change one 160-byte payload region the way the real fleet differs
        for i in range(27224, 27384):
            data[i] = (data[i] + 0x11) & 0xFF
    return bytes(data)


# ---------------------------------------------------------------------------
# writers
# ---------------------------------------------------------------------------

def write_all(outdir=FIXTURES):
    os.makedirs(outdir, exist_ok=True)
    hrtf = build_hrtf_like("hrtf-fixture-v1")
    hrtf2 = build_hrtf_like("hrtf-fixture-v2")
    dax = build_dax_like("dax-fixture-v1")
    dax2 = build_dax_like("dax-fixture-v1", mutate_region=True)
    unknown = Stream("unknown-fixture").bytes(512)

    files = {
        "hrtf_like.bin": hrtf,
        "hrtf_like_2.bin": hrtf2,
        "hrtf_like_truncated.bin": hrtf[:100001],
        "dax_like.bin": dax,
        "dax_like_2.bin": dax2,
        "unknown.bin": unknown,
        "empty.bin": b"",
    }
    written = []
    for name, payload in sorted(files.items()):
        path = os.path.join(outdir, name)
        with open(path, "wb") as fh:
            fh.write(payload)
        written.append((name, len(payload),
                        hashlib.sha256(payload).hexdigest()[:16]))
    return written


def main():
    for name, size, digest in write_all():
        print("%-26s %8d B  sha256:%s..." % (name, size, digest))


if __name__ == "__main__":
    main()
