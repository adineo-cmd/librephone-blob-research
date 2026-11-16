#!/usr/bin/env python3
"""build_fragmentation_half.py — Phase 4 fragmentation analysis for the
LAPTOP half of the LibrePhone device list (rows 119-236 of the
codepoint-sorted 236-device universe from codeberg rsavoye/librephone
data/devices.sql.bz2, parsed into /tmp/lpdb/split.json).

Inputs:
  /tmp/lpdb/split.json                  laptop_half: 118 devices with blob
                                        rows {file,type,size,md5}
  upstream-contribution/blob-database/coverage-matrix.csv
                                        the master matrix (33,917 rows) —
                                        family taxonomy reused verbatim for
                                        merge-consistency with the desktop
                                        half and the master matrix.
  upstream-contribution/blob-database/recon.md top-20 (embedded below)
                                        for the leverage cross-reference.

Outputs (written next to this script):
  sharing-clusters.csv      md5,file,family,bytes,device_count,devices
                            (all clusters in this half: shared first, then
                            singletons — merge tooling filters as needed)
  fragmentation-summary.json  machine-readable headline numbers
  (fragmentation-half.md is written by hand from this summary)

Metrics follow recon.md's precedents: a "cluster" is a set of devices
sharing an IDENTICAL md5; the recon cross-reference additionally reports
file-presence (any md5) counts, because nightly drift splits one blob
into several md5 clusters. The headline top-15 uses recon's "real
firmware" filter (>= 1 KB, no .jsn/.json/.xml/.txt manifests).

Derived facts only; no payload bytes are fetched or committed.
"""

import csv
import json
import os
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SPLIT = "/tmp/lpdb/split.json"
MATRIX = os.path.join(HERE, "..", "..", "upstream-contribution",
                      "blob-database", "coverage-matrix.csv")

EMPTY_MD5 = "d41d8cd98f00b204e9800998ecf8427e"  # md5 of the empty string

# recon.md top-20 (upstream-contribution/blob-database/recon.md 2026-11-16):
# file -> (global device count, bytes, family)
RECON_TOP20 = {
    "crbtfw20.tlv": (29, 56180, "bt"),
    "apbtfw10.tlv": (29, 56052, "bt"),
    "crbtfw11.tlv": (29, 29368, "bt"),
    "crnv20.bin": (29, 3936, "bt"),
    "crnv11.bin": (29, 2798, "bt"),
    "apnv10.bin": (29, 1243, "bt"),
    "bm2n12.bin": (26, 2623528, "adsp"),
    "bm2n15.bin": (26, 1082856, "adsp"),
    "bm2n14.bin": (26, 103168, "adsp"),
    "a619_gmu.bin": (26, 32768, "gpu"),
    "bm2n08.bin": (25, 3091896, "adsp"),
    "bm2n13.bin": (25, 1106944, "adsp"),
    "bm2n06.bin": (25, 864824, "adsp"),
    "unified_ksqs.bin": (25, 796357, "other"),
    "sequence_manifest.bin": (25, 5704, "gpu"),
    "a660_sqe.fw": (21, 40496, "gpu"),
    "a660_gmu.bin": (19, 55256, "gpu"),
    "a630_sqe.fw": (19, 32456, "gpu"),
    "CFR_OPlus_EF017_UW_snapshot.bin": (19, 2126, "other"),
    "aoa_cldb_falcon.bin": (17, 839856, "wifi"),
}


def load_matrix_family_maps():
    fn_fam = defaultdict(Counter)
    md5_fam = defaultdict(Counter)
    with open(MATRIX, newline="") as fh:
        for row in csv.DictReader(fh):
            fam = row["blob_family"].strip()
            if not fam:
                continue
            fn = row["filename"].strip()
            if fn:
                fn_fam[fn][fam] += 1
            md5 = row["md5_db"].strip().lower()
            if md5:
                md5_fam[md5][fam] += 1
    return ({fn: c.most_common(1)[0][0] for fn, c in fn_fam.items()},
            {m: c.most_common(1)[0][0] for m, c in md5_fam.items()})


def fallback_family(fname):
    """Filename-first heuristics mirroring recon.md's family table; only
    used for rows absent from the master matrix."""
    f = fname.lower()
    if f.endswith((".jsn", ".json", ".xml", ".txt", ".mdc")):
        return "other"
    if f.endswith(".tlv") or f.startswith(("crnv", "apnv", "crbtfw", "apbtfw", "hpbtfw", "hpnv")):
        return "bt"
    if f.startswith(("bm2n", "adsp")):
        return "adsp"
    if f.startswith("cdsp"):
        return "cdsp"
    if "_gmu" in f or "sqe.fw" in f or "zap" in f or "kbc" in f:
        return "gpu"
    if f.startswith(("wcn", "qca")) or "wlanmdss" in f:
        return "wifi"
    if f.startswith(("boot", "vendor_boot", "xbl", "abl", "uefi", "hyp")):
        return "boot"
    if f.startswith(("modem", "mpss", "md1img")) or f.endswith((".mdt", ".b00")):
        return "modem"
    if "keymaster" in f or "keym" in f or f.endswith(".ta"):
        return "tz"
    return "other"


def is_real_firmware(files, size):
    f = sorted(files)[0].lower()
    return size >= 1024 and not f.endswith((".jsn", ".json", ".xml", ".txt"))


def main():
    data = json.load(open(SPLIT))
    half = data["laptop_half"]
    assert len(half) == 118, len(half)
    fn_map, md5_map = load_matrix_family_maps()

    inv = {}
    with open(os.path.join(HERE, "devices-half.csv"), newline="") as fh:
        for row in csv.DictReader(fh):
            inv[(row["vendor"], row["model"], row["build"])] = row

    devices = []
    unmatched_family = Counter()
    for i, dev in enumerate(half):
        row_no = 119 + i
        name = "%s/%s" % (dev["vendor"], dev["build"])
        d = {"row": row_no, "name": name,
             "vendor": dev["vendor"], "model": dev["model"],
             "build": dev["build"],
             "soc": None if dev["soc"] == "\\N" else dev["soc"],
             "extracts_flag": bool(dev["extracts"]),
             "has_blobs": bool(dev["blobs"])}
        inv_row = inv.get((dev["vendor"], dev["model"], dev["build"]))
        d["inv_check"] = None if inv_row is None else (
            (inv_row["extracted"] == "y") == d["extracts_flag"] and
            int(inv_row["blob_count"]) == len(dev["blobs"]))
        d["blobs"] = []
        for b in dev["blobs"]:
            md5 = (b.get("md5") or "").lower()
            fam = md5_map.get(md5) or fn_map.get(b["file"])
            if fam is None:
                fam = fallback_family(b["file"])
                unmatched_family[b["file"]] += 1
            d["blobs"].append({"file": b["file"], "type": b.get("type"),
                               "size": b["size"], "md5": md5, "family": fam})
        devices.append(d)

    total_rows = sum(len(d["blobs"]) for d in devices)
    total_bytes = sum(b["size"] for d in devices for b in d["blobs"])
    both = [d for d in devices if d["extracts_flag"] and d["has_blobs"]]
    ext_only = [d for d in devices if d["extracts_flag"] and not d["has_blobs"]]
    blobs_only = [d for d in devices if not d["extracts_flag"] and d["has_blobs"]]
    neither = [d for d in devices if not d["extracts_flag"] and not d["has_blobs"]]

    # SoC
    soc_counter = Counter((d["soc"] or "UNSPECIFIED") for d in devices)
    mtk_devices = [d for d in devices if any(
        b["file"].startswith(("md1img", "scp", "sspm", "spmfw", "preloader"))
        for b in d["blobs"])]

    # families
    fam_rows = Counter()
    fam_bytes = Counter()
    fam_devices = defaultdict(set)
    for d in devices:
        for b in d["blobs"]:
            fam_rows[b["family"]] += 1
            fam_bytes[b["family"]] += b["size"]
            fam_devices[b["family"]].add(d["build"])

    # md5 clusters
    clusters = defaultdict(lambda: {"devices": set(), "files": Counter(),
                                    "size": 0, "family": None})
    for d in devices:
        for b in d["blobs"]:
            c = clusters[b["md5"]]
            c["devices"].add(d["build"])
            c["files"][b["file"]] += 1
            c["size"] = b["size"]
            c["family"] = b["family"]
    shared = {m: c for m, c in clusters.items() if len(c["devices"]) > 1}
    singletons = {m: c for m, c in clusters.items() if len(c["devices"]) == 1}
    empty_cluster = clusters.get(EMPTY_MD5)

    real_shared = {m: c for m, c in shared.items()
                   if is_real_firmware(c["files"], c["size"])}
    top15 = sorted(real_shared.items(),
                   key=lambda kv: (-len(kv[1]["devices"]), -kv[1]["size"]))[:15]
    lev10 = sorted(real_shared.items(),
                   key=lambda kv: (-len(kv[1]["devices"]) * kv[1]["size"]))[:10]

    def bucket(n):
        return ("2-4" if n <= 4 else "5-9" if n <= 9 else
                "10-19" if n <= 19 else "20+")
    hist_all = Counter(bucket(len(c["devices"])) for c in shared.values())
    hist_real = Counter("2-4" if len(c["devices"]) <= 4 else
                        "5-9" if len(c["devices"]) <= 9 else
                        "10-19" if len(c["devices"]) <= 19 else "20+"
                        for c in real_shared.values())

    # recon cross-reference: identical-md5 AND file-presence metrics
    recon = {}
    for fname, (glob_n, glob_size, fam) in RECON_TOP20.items():
        rec = {"global_devices": glob_n, "global_bytes": glob_size,
               "recon_family": fam}
        file_devs, file_md5s = set(), set()
        for d in devices:
            for b in d["blobs"]:
                if b["file"] == fname:
                    file_devs.add(d["build"])
                    file_md5s.add(b["md5"])
        if file_devs:
            rec["half_file_devices"] = len(file_devs)
            rec["half_md5_clusters"] = len(file_md5s)
            # biggest same-md5 cluster among this file's md5s
            best = max((len(clusters[m]["devices"]) for m in file_md5s
                        if m in clusters), default=0)
            rec["half_largest_same_md5"] = best
            rec["half_devices"] = sorted(file_devs)
        recon[fname] = rec

    # sharing-clusters.csv (all clusters; shared first, then singletons)
    with open(os.path.join(HERE, "sharing-clusters.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["md5", "file", "family", "bytes", "device_count", "devices"])
        for group in (sorted(shared.items(),
                             key=lambda kv: (-len(kv[1]["devices"]),
                                             -kv[1]["size"],
                                             sorted(kv[1]["files"]))),
                      sorted(singletons.items(),
                             key=lambda kv: (-kv[1]["size"],
                                             sorted(kv[1]["files"])))):
            for m, c in group:
                w.writerow([m, ";".join(sorted(c["files"])), c["family"],
                            c["size"], len(c["devices"]),
                            ";".join(sorted(c["devices"]))])

    summary = {
        "half": "laptop rows 119-236 (codepoint sort)",
        "devices": len(devices),
        "extracts_flag_true": len(both) + len(ext_only),
        "semantics": {
            "extracts_and_blobs": len(both),
            "extracts_only_no_blobs": len(ext_only),
            "blobs_only_no_extracts_flag": len(blobs_only),
            "neither": len(neither),
            "note": "the upstream `extracts` column does NOT track blob "
                    "presence: 15 devices are flagged extracts-true with "
                    "zero blob rows and 31 carry blob rows flagged "
                    "extracts-false",
        },
        "blob_rows": total_rows,
        "total_bytes": total_bytes,
        "distinct_md5": len(clusters),
        "shared_md5": len(shared),
        "singleton_md5": len(singletons),
        "shared_instances": sum(len(c["devices"]) for c in shared.values()),
        "shared_instance_share_pct": round(
            100.0 * sum(len(c["devices"]) for c in shared.values()) / total_rows, 1),
        "real_shared_md5": len(real_shared),
        "real_shared_instances": sum(len(c["devices"]) for c in real_shared.values()),
        "hist_all": dict(hist_all),
        "hist_real": dict(hist_real),
        "empty_md5_cluster": None if not empty_cluster else {
            "devices": len(empty_cluster["devices"]),
            "files": dict(empty_cluster["files"])},
        "soc_strings": sorted(soc_counter.items()),
        "mtk_devices_with_blank_soc": [d["build"] for d in mtk_devices],
        "families": {f: {"rows": fam_rows[f], "bytes": fam_bytes[f],
                         "devices": len(fam_devices[f])}
                     for f in sorted(fam_bytes, key=lambda f: -fam_bytes[f])},
        "top15": [{"md5": m, "file": sorted(c["files"])[0],
                   "family": c["family"], "bytes": c["size"],
                   "device_count": len(c["devices"]),
                   "devices": sorted(c["devices"])} for m, c in top15],
        "leverage_top10": [{"md5": m, "file": sorted(c["files"])[0],
                            "bytes": c["size"],
                            "device_count": len(c["devices"]),
                            "freed_bytes": len(c["devices"]) * c["size"]}
                           for m, c in lev10],
        "recon_crossref": recon,
        "unmatched_family_rows": dict(unmatched_family),
        "inventory_mismatches": [d["name"] for d in devices
                                 if d["inv_check"] is False],
    }
    with open(os.path.join(HERE, "fragmentation-summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1)

    print(json.dumps({k: v for k, v in summary.items()
                      if k not in ("soc_strings", "top15", "leverage_top10",
                                   "recon_crossref", "families")}, indent=1))
    print("SoC:", json.dumps(summary["soc_strings"], indent=1))
    print("Families:")
    for f, v in summary["families"].items():
        print("  %-7s rows=%5d bytes=%12d devices=%2d" % (
            f, v["rows"], v["bytes"], v["devices"]))
    print("Top-15 (real firmware):")
    for e in summary["top15"]:
        print("  %2d devs %9d B %-7s %-32s %s" % (
            e["device_count"], e["bytes"], e["family"], e["file"], e["md5"][:8]))
    print("Leverage top-10 (freed bytes):")
    for e in summary["leverage_top10"]:
        print("  %2d x %9d = %12d %-32s" % (
            e["device_count"], e["bytes"], e["freed_bytes"], e["file"]))
    print("Recon cross-ref (half):")
    for f, r in summary["recon_crossref"].items():
        if "half_file_devices" in r:
            print("  %-30s file=%2d md5clusters=%d largest=%2d (global %2d)" % (
                f, r["half_file_devices"], r["half_md5_clusters"],
                r["half_largest_same_md5"], r["global_devices"]))
    print("Recon files absent from this half:",
          sorted(f for f, r in summary["recon_crossref"].items()
                 if "half_file_devices" not in r) or "none")
    print("Unmatched families:", dict(unmatched_family) or "none")
    print("Inventory mismatches:", summary["inventory_mismatches"] or "none")


if __name__ == "__main__":
    main()
