#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import struct
import sys

HEADER_SIZE = 28
EXPECTED_BPP = 4
EXPECTED_PLANES = 1
EXPECTED_ZERO_A = 0
EXPECTED_MAGIC = 99
EXPECTED_ZERO_B = 0
CLASS_GRAYSCALE = "grayscale-mask"
CLASS_COLOR = "color-texture"
CLASS_MIXED = "mixed"


def parse_header(raw):
    if len(raw) < HEADER_SIZE:
        raise ValueError("truncated header: %d bytes" % len(raw))
    fields = struct.unpack_from("<7I", raw, 0)
    return {
        "width": fields[0],
        "height": fields[1],
        "bytes_per_pixel": fields[2],
        "planes": fields[3],
        "zero_a": fields[4],
        "magic": fields[5],
        "zero_b": fields[6],
    }


def expected_size(header):
    return HEADER_SIZE + header["width"] * header["height"] * header["bytes_per_pixel"]


def channel_stats(payload):
    n = len(payload) // EXPECTED_BPP
    channels = [[], [], [], []]
    for i in range(n):
        base = i * EXPECTED_BPP
        for k in range(EXPECTED_BPP):
            channels[k].append(payload[base + k])
    out = []
    for c in channels:
        if not c:
            out.append({"min": None, "max": None, "unique": 0})
            continue
        out.append({"min": min(c), "max": max(c), "unique": len(set(c))})
    return out


def classify(identity):
    a = identity.get("ch0_eq_ch1", 0.0)
    b = identity.get("ch1_eq_ch2", 0.0)
    if a == 100.0 and b == 100.0:
        return CLASS_GRAYSCALE
    if a < 50.0 and b < 50.0:
        return CLASS_COLOR
    return CLASS_MIXED


def channel_identity(payload):
    n = len(payload) // EXPECTED_BPP
    if not n:
        return {}
    pairs = {}
    for a, b, name in ((0, 1, "ch0_eq_ch1"), (1, 2, "ch1_eq_ch2"), (0, 2, "ch0_eq_ch2")):
        hits = sum(payload[i * 4 + a] == payload[i * 4 + b] for i in range(n))
        pairs[name] = round(100.0 * hits / n, 1)
    return pairs


def inspect(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    header = parse_header(raw)
    want = expected_size(header)
    payload = raw[HEADER_SIZE:]
    stats = channel_stats(payload)
    identity = channel_identity(payload)
    result = {
        "file": os.path.basename(path),
        "bytes": len(raw),
        "md5": hashlib.md5(raw).hexdigest(),
        "header": header,
        "expected_size": want,
        "size_match": want == len(raw),
        "slack": len(raw) - want,
        "payload_bytes": len(payload),
        "pixels": len(payload) // EXPECTED_BPP,
        "channels": stats,
        "pixel_class": classify(identity),
        "identity_pct": identity,
        "header_canonical": (
            header["bytes_per_pixel"] == EXPECTED_BPP
            and header["planes"] == EXPECTED_PLANES
            and header["zero_a"] == EXPECTED_ZERO_A
            and header["magic"] == EXPECTED_MAGIC
            and header["zero_b"] == EXPECTED_ZERO_B
        ),
    }
    result["valid"] = result["size_match"] and result["header_canonical"] and result["pixels"] > 0
    return result


def brief(result):
    h = result["header"]
    return "%-28s %9d  %dx%d bpp=%d magic=%d  %-16s fit=%s" % (
        result["file"], result["bytes"], h["width"], h["height"],
        h["bytes_per_pixel"], h["magic"], result["pixel_class"],
        result["size_match"],
    )


def main(argv=None):
    ap = argparse.ArgumentParser(description="Probe Xiaomi camera render-effect asset containers")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--brief", action="store_true")
    args = ap.parse_args(argv)
    results = []
    errors = []
    for path in args.paths:
        try:
            results.append(inspect(path))
        except (OSError, ValueError, struct.error) as exc:
            errors.append({"file": path, "error": str(exc)})
    if args.brief:
        for r in results:
            print(brief(r))
        for e in errors:
            print("%-28s ERROR %s" % (e["file"], e["error"]), file=sys.stderr)
    else:
        print(json.dumps({"results": results, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
