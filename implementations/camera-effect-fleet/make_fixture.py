#!/usr/bin/env python3
import os
import struct

SYNTH_MAGIC = 99
SYNTH_ZERO = 0
SYNTH_BPP = 4
SYNTH_PLANES = 1

CASES = [
    ("opaque_mask", 16, 12, "gray"),
    ("color_lut", 8, 8, "color"),
    ("low_alpha", 10, 5, "lowalpha"),
    ("wide", 64, 3, "gray"),
    ("tall", 3, 64, "color"),
]


def synth_pixels(width, height, kind):
    out = bytearray()
    for y in range(height):
        for x in range(width):
            if kind == "gray":
                v = (x * 7 + y * 13) & 0xFF
                out += bytes((v, v, v, 0xFF))
            elif kind == "lowalpha":
                out += bytes(((x * 31) & 0xFF, (y * 17) & 0xFF, 0xFF, (x + y) & 0x1F))
            else:
                out += bytes(((x * 29) & 0xFF, (y * 37) & 0xFF, ((x + y) * 11) & 0xFF, 0xFF))
    return bytes(out)


def build(path, name, width, height, kind):
    header = struct.pack(
        "<7I", width, height, SYNTH_BPP, SYNTH_PLANES, SYNTH_ZERO, SYNTH_MAGIC, SYNTH_ZERO
    )
    with open(path, "wb") as fh:
        fh.write(header)
        fh.write(synth_pixels(width, height, kind))


def malformed(root):
    bad = os.path.join(root, "malformed")
    os.makedirs(bad, exist_ok=True)
    with open(os.path.join(bad, "truncated_header.bin"), "wb") as fh:
        fh.write(b"\x04\x00\x00\x00")
    good = struct.pack("<7I", 4, 4, 4, 1, 0, SYNTH_MAGIC, 0)
    with open(os.path.join(bad, "size_mismatch.bin"), "wb") as fh:
        fh.write(good + b"\x00" * 63)
    badmagic = struct.pack("<7I", 4, 4, 4, 1, 0, 98, 0)
    with open(os.path.join(bad, "wrong_magic.bin"), "wb") as fh:
        fh.write(badmagic + b"\x00" * 64)
    badbpp = struct.pack("<7I", 4, 4, 3, 1, 0, SYNTH_MAGIC, 0)
    with open(os.path.join(bad, "wrong_bpp.bin"), "wb") as fh:
        fh.write(badbpp + b"\x00" * 64)


def write_all(root):
    fixture_dir = os.path.join(root, "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    for name, w, h, kind in CASES:
        build(os.path.join(fixture_dir, name + ".bin"), name, w, h, kind)
    malformed(fixture_dir)


if __name__ == "__main__":
    write_all(os.getcwd())
