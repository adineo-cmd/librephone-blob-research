import glob
import hashlib
import json
import os
import struct
import sys

KNOWN_NVM_TAGS = {
    0x0002: "BD_ADDR (EDL_TAG_ID_BD_ADDR, btqca.h)",
    0x0011: "HCI transport params (EDL_TAG_ID_HCI, btqca.h)",
    0x001b: "deep-sleep params (EDL_TAG_ID_DEEP_SLEEP, btqca.h)",
}


def parse_tlv_type_patch(d, payload_len):
    total_size, data_length = struct.unpack_from("<II", d, 4)
    return {
        "total_size": total_size,
        "data_length": data_length,
        "format_version": d[12],
        "signature": d[13],
        "download_mode": d[14],
        "reserved1": d[15],
        "product_id": struct.unpack_from("<H", d, 16)[0],
        "rom_build": "0x%04x" % struct.unpack_from("<H", d, 18)[0],
        "patch_version": struct.unpack_from("<H", d, 20)[0],
        "reserved2": "0x%04x" % struct.unpack_from("<H", d, 22)[0],
        "entry": "0x%x" % struct.unpack_from("<I", d, 24)[0],
        "check_total_eq_data_plus_24": total_size == data_length + 24,
        "tail_bytes": payload_len - total_size,
        "tail_zero_fraction": round(sum(1 for b in d[4 + total_size:4 + payload_len] if b == 0) / max(1, payload_len - total_size), 3),
        "patch_head_hex": d[28:44].hex(),
    }


def parse_nvm_set(d, base, set_len):
    idx = 0
    entries = []
    while idx + 12 <= set_len:
        tag_id, tag_len = struct.unpack_from("<HH", d, base + idx)
        if set_len < idx + 12 + tag_len:
            entries.append({"error": "truncated", "tag_id": "0x%04x" % tag_id})
            break
        val = d[base + idx + 12:base + idx + 12 + tag_len]
        entries.append({
            "tag_id": "0x%04x" % tag_id,
            "name": KNOWN_NVM_TAGS.get(tag_id, "(unknown to btqca.c)"),
            "tag_len": tag_len,
            "value_hex": val.hex(),
        })
        idx += 12 + tag_len
    return {"set_len": set_len, "consumed": idx, "exact_close": idx == set_len, "entries": entries}


def parse_file(path):
    d = open(path, "rb").read()
    tl = struct.unpack_from("<I", d, 0)[0]
    t, l = tl & 0xFF, tl >> 8
    r = {"bytes": len(d), "md5": hashlib.md5(d).hexdigest(),
         "sha256": hashlib.sha256(d).hexdigest(),
         "outer": {"type": t, "len": l, "len_check": len(d) == 4 + l}}
    if t == 1:
        r["patch"] = parse_tlv_type_patch(d, l)
    elif t == 4:
        sets, tags, bdaddr = [], {}, None
        off = 4
        while off + 4 <= 4 + l:
            itl = struct.unpack_from("<I", d, off)[0]
            it, il = itl & 0xFF, itl >> 8
            if it == 2:
                s = parse_nvm_set(d, off + 4, il)
                sets.append(s)
                for e in s["entries"]:
                    tags[e["tag_id"]] = tags.get(e["tag_id"], 0) + 1
                    if e["tag_id"] == "0x0002":
                        bdaddr = e["value_hex"]
            else:
                sets.append({"type": it, "len": il, "note": "non-NVM inner set, not parsed"})
            off += 4 + il
        r["inner_sets"] = sets
        r["tag_histogram"] = tags
        r["tag_names"] = {k: KNOWN_NVM_TAGS.get(int(k, 16), "?") for k in tags}
        r["bdaddr"] = bdaddr
    return r


def main():
    targets = sys.argv[2:] if len(sys.argv) > 2 else sorted(glob.glob("data-fetch/enchilada/bt-fat/*"))
    out = {}
    for p in targets:
        out[os.path.basename(p)] = parse_file(p)
    dest = sys.argv[1] if len(sys.argv) > 1 else "qca-bt-tlv.json"
    json.dump(out, open(dest, "w"), indent=1, sort_keys=True)
    for k, v in out.items():
        print(k, json.dumps(v.get("outer"), sort_keys=True))


if __name__ == "__main__":
    main()
