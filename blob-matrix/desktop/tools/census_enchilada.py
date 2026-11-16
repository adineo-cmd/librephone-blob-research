import csv
import hashlib
import json
import os
import struct
import sys

BASE = "/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-6cf6375c0730"
ENCH = os.path.join(BASE, "data-fetch", "enchilada")
OUT = os.path.join(BASE, "analysis", "out")
os.makedirs(OUT, exist_ok=True)

TREES = [
    ("tree_firmware", "firmware"),
    ("tree_firmware_wlan", "firmware/wlan"),
    ("tree_lib_rfsa_adsp", "lib/rfsa/adsp"),
    ("tree_radio", "radio"),
    ("tree_etc_firmware_tp", "etc/firmware/tp"),
]

PARTS = [
    ("bt.img", "bt"),
    ("tz.img", "tz"),
    ("dsp.img", "adsp"),
    ("modem.img", "modem"),
]

FAMILY_RULES = [
    (("a630", "a619", "a660", "gmu", "sqe", "zap"), "gpu"),
    (("wlan", "wcnss", "qca_cld", "clb", "bdwlan", "otp.bin", "amss.bin"), "wifi"),
    (("btfw", "crnv", "apnv", "nvram", "bdaddress", "hci"), "bt"),
    (("bm2n",), "adsp"),
    (("camera", "camx", "chromatix", "icp"), "camera"),
    (("tz", "cmnlib", "keymaster", "keystore", "hyp."), "tz"),
    (("nfc", "qnfc"), "nfc"),
    (("ipa",), "other"),
    (("touch", "synaptics", "focaltech", "goodix"), "other"),
]


def probe_magic(path):
    try:
        with open(path, "rb") as f:
            head = f.read(16)
    except OSError:
        return ""
    if head[:4] == b"\x7fELF":
        ei_class, ei_data = head[4], head[5]
        mach = struct.unpack_from("<H", head, 6)[0]
        return "elf32-le" if ei_class == 1 and ei_data == 1 else "elf"
    if head[:4] == b"BZh9":
        return "bzip2"
    if head[:2] == b"\xfd7":
        return "xz"
    if head[:4] == b"QCMH" or head[:4] == b"\x4d\x44\x54\x00":
        return "mdt?"
    return "raw"


def classify(name, where):
    low = name.lower()
    for keys, fam in FAMILY_RULES:
        if any(k in low for k in keys):
            return fam
    if "rfsa" in where or "adsp" in where:
        return "adsp"
    if "wlan" in where:
        return "wifi"
    if "radio" in where:
        return "radio"
    return "other"


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


rows = []
for tree, where in TREES:
    root = os.path.join(ENCH, tree)
    for dirpath, _dirs, files in os.walk(root):
        rel = os.path.relpath(dirpath, root)
        for fn in sorted(files):
            p = os.path.join(dirpath, fn)
            if os.path.islink(p):
                continue
            sz = os.path.getsize(p)
            rel_where = os.path.join(where, rel) if rel != "." else where
            rows.append({
                "device": "OnePlus_6",
                "vendor": "OnePlus",
                "soc": "Qualcomm SDM845 Snapdragon 845",
                "family": classify(fn, rel_where),
                "file": os.path.join(rel_where, fn),
                "bytes": sz,
                "sha256": sha256_of(p),
                "public_status": "populated-local-session",
                "notes": "magic=%s; source=LineageOS-22.2-20261111-nightly-enchilada payload/vendor" % probe_magic(p),
            })

for fname, fam in PARTS:
    p = os.path.join(ENCH, fname)
    if not os.path.exists(p):
        continue
    sz = os.path.getsize(p)
    rows.append({
        "device": "OnePlus_6",
        "vendor": "OnePlus",
        "soc": "Qualcomm SDM845 Snapdragon 845",
        "family": fam,
        "file": "<partition:%s>" % fname,
        "bytes": sz,
        "sha256": sha256_of(p),
        "public_status": "populated-local-session",
        "notes": "magic=%s; partition image from OTA payload" % probe_magic(p),
    })

with open(os.path.join(OUT, "enchilada-census.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["device", "vendor", "soc", "family", "file", "bytes", "sha256", "public_status", "notes"])
    for r in rows:
        w.writerow([r[k] for k in ("device", "vendor", "soc", "family", "file", "bytes", "sha256", "public_status", "notes")])

fam_bytes = {}
for r in rows:
    fam_bytes.setdefault(r["family"], [0, 0])
    fam_bytes[r["family"]][0] += 1
    fam_bytes[r["family"]][1] += r["bytes"]

summary = {
    "rows": len(rows),
    "total_bytes": sum(r["bytes"] for r in rows),
    "families": {k: {"files": v[0], "bytes": v[1]} for k, v in sorted(fam_bytes.items(), key=lambda kv: -kv[1][1])},
}
with open(os.path.join(OUT, "enchilada-census.json"), "w") as f:
    json.dump(summary, f, indent=1, sort_keys=True)
print(json.dumps(summary, indent=1, sort_keys=True))
