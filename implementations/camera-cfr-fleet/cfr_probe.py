#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import struct
import sys

CLASS_SHORT = "short-1079"
CLASS_MID = "mid-2126"
CLASS_TAG = "tagged-3645"
CLASS_TEXT = "text-8128"
CLASS_UNKNOWN = "unknown"
SIG_3_512 = b"\x03\x00\x00\x00\x00\x02\x00\x00"
SIG_BLOCK = bytes.fromhex("0000000003000000000200000000000000000000")
TAG_RECORD = b"\x00\x01\x02"
TEXT_MAGIC = b"CFR400 TUNING PARAMETER"
LENS_MAGIC = b"L12U"


def find_all(data, needle):
    out = []
    pos = 0
    while True:
        i = data.find(needle, pos)
        if i < 0:
            return out
        out.append(i)
        pos = i + 1


def record_tags(data):
    return [{"offset": i, "tag": data[i]} for i in range(len(data) - 3) if data[i + 1:i + 4] == TAG_RECORD]


def classify(data):
    if data.startswith(TEXT_MAGIC):
        return CLASS_TEXT
    if len(data) >= 12 and data[8:12] == LENS_MAGIC:
        return CLASS_TAG
    if len(data) == 1079:
        return CLASS_SHORT
    if len(data) == 2126:
        return CLASS_MID
    return CLASS_UNKNOWN


def inspect(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    kind = classify(raw)
    result = {
        "file": os.path.basename(path),
        "bytes": len(raw),
        "md5": hashlib.md5(raw).hexdigest(),
        "class": kind,
        "u32": [hex(x) for x in struct.unpack_from("<8I", raw, 0)] if len(raw) >= 32 else [],
        "ascii": [s.decode("ascii", "replace") for s in re.findall(rb"[ -~]{4,}", raw[:64])],
        "marker_3_512_offsets": find_all(raw, SIG_3_512),
        "record_tags": record_tags(raw),
        "size_word_offsets": [o for o in range(0, len(raw) - 3, 4) if struct.unpack_from("<I", raw, o)[0] == len(raw)],
    }
    if kind == CLASS_TEXT:
        result["prologue"] = raw[:32].decode("ascii", "replace").rstrip("\x00")
        result["has_size_word"] = len(result["size_word_offsets"]) > 0
    if kind == CLASS_TAG:
        result["lens_magic"] = raw[8:12].decode("ascii", "replace")
        result["lens_string"] = raw[8:16].decode("ascii", "replace").rstrip("\x00")
    if kind in (CLASS_SHORT, CLASS_MID):
        result["signature_block_ok"] = raw[20:40] == SIG_BLOCK
        tags = [t["offset"] for t in result["record_tags"]]
        if len(tags) >= 2:
            result["record_stride"] = tags[1] - tags[0]
        result["first_record_offset"] = tags[0] if tags else None
    return result


def brief(result):
    extra = ""
    if result["class"] == CLASS_TEXT:
        extra = " prologue=%r" % result.get("prologue", "")
    elif result["class"] == CLASS_TAG:
        extra = " lens=%s" % result.get("lens_string", "")
    elif result["class"] in (CLASS_SHORT, CLASS_MID):
        extra = " stride=%s sig=%s" % (result.get("record_stride"), result.get("signature_block_ok"))
    return "%-24s %6d  %-12s%s" % (result["file"], result["bytes"], result["class"], extra)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Probe OnePlus/Xiaomi CFR camera parameter blobs")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--brief", action="store_true")
    args = ap.parse_args(argv)
    results = []
    errors = []
    for path in args.paths:
        try:
            results.append(inspect(path))
        except (OSError, struct.error) as exc:
            errors.append({"file": path, "error": str(exc)})
    if args.brief:
        for r in results:
            print(brief(r))
        for e in errors:
            print("%-24s ERROR %s" % (e["file"], e["error"]), file=sys.stderr)
    else:
        print(json.dumps({"results": results, "errors": errors}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
