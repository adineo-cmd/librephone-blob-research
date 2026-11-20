#!/usr/bin/env python3
import os
import struct

SIG = bytes.fromhex("000000000000000003000000000200000000000000000000")
TEXT = b"CFR400 TUNING PARAMETER"


def filler(n, seed=0):
    return bytes((0x80 | ((i + seed) & 0x7F)) for i in range(n))


def short_blob():
    out = bytearray()
    out += struct.pack("<4I", 140, 81, 32, 1043)
    out += SIG
    out += bytes((0x46, 0, 1, 2)) + filler(60)
    out += bytes((0x32, 0, 1, 2)) + filler(337 - 4 - 60 - 4, 11)
    out += bytes((0x32, 0, 1, 2)) + filler(317, 23)
    return bytes(out[:1079]).ljust(1079, b"\x00")


def mid_blob():
    out = bytearray()
    out += struct.pack("<4I", 150, 6010, 32, 2042)
    out += SIG
    out += bytes((0x5A, 0, 1, 2)) + filler(670 - 4, 3)
    out += bytes((0x64, 0, 1, 2)) + filler(666, 7)
    out += bytes((0x64, 0, 1, 2)) + filler(666, 7)
    return bytes(out[:2126]).ljust(2126, b"\xff")


def tag_blob():
    out = bytearray(3645)
    struct.pack_into("<4I", out, 0, 200, 96, 0x5532314C, 87)
    out[8:16] = b"L12UW\x00\x00\x00"
    struct.pack_into("<2I", out, 48, 0xD7D, 3)
    struct.pack_into("<I", out, 56, 0x200)
    struct.pack_into("<I", out, 104, 0x46)
    out[105:108] = b"\x00\x01\x02"
    struct.pack_into("<I", out, 780, 0x46)
    out[781:784] = b"\x00\x01\x02"
    return bytes(out)


def text_blob():
    out = bytearray(8128)
    out[0:len(TEXT)] = TEXT
    out[32:40] = b"AC090 W "
    struct.pack_into("<I", out, 64, 0x200)
    struct.pack_into("<I", out, 68, 8128)
    struct.pack_into("<I", out, 72, 3)
    for i in range(128, 8128):
        out[i] = (i * 7) & 0xFF
    return bytes(out)


def malformed(root):
    bad = os.path.join(root, "malformed")
    os.makedirs(bad, exist_ok=True)
    with open(os.path.join(bad, "empty.bin"), "wb") as fh:
        fh.write(b"")
    with open(os.path.join(bad, "truncated.bin"), "wb") as fh:
        fh.write(b"\x01\x02\x03")
    with open(os.path.join(bad, "unknown.bin"), "wb") as fh:
        fh.write(b"X" * 512)


def write_all(root):
    fixture_dir = os.path.join(root, "fixtures")
    os.makedirs(fixture_dir, exist_ok=True)
    for name, data in (
        ("short.bin", short_blob()),
        ("mid.bin", mid_blob()),
        ("tag.bin", tag_blob()),
        ("text.bin", text_blob()),
    ):
        with open(os.path.join(fixture_dir, name), "wb") as fh:
            fh.write(data)
    malformed(fixture_dir)


if __name__ == "__main__":
    write_all(os.getcwd())
