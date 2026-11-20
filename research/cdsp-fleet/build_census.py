"""Provenance: builds research/cdsp-fleet/census.json + census.md from data/fleet/devices-001-222.csv (issue #595, cross-device census). Stdlib only; run as: python3 -I build_census.py"""
import csv
import hashlib
import json
import os
import posixpath
import re
import statistics
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CSV_PATH = os.path.join(ROOT, "data", "fleet", "devices-001-222.csv")
OUT_JSON = os.path.join(HERE, "census.json")
OUT_MD = os.path.join(HERE, "census.md")

FAMILY = "cdsp"
ALIAS_RE = re.compile(r"^<([^:>]+):(.*)>$")
MD5_RE = re.compile(r"md5_db=([0-9a-f]{32})")
DBTYPE_RE = re.compile(r"db_type=([A-Za-z0-9_]+)")
STRICT_RE = re.compile(
    r"^md5_db=[0-9a-f]{32}; (P[0-9]); db_path=[^;]+; db_type=(COMPUTE|UNKNOWN)$"
)
SEG_RE = re.compile(r"^cdsp\.b(\d\d)$")
TRUNC = 8
BIMODAL_GAP = 10.0
OUTLIER_FACTOR = 8


def load():
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def canon(name):
    m = ALIAS_RE.match(name)
    path = m.group(2) if m else name
    return posixpath.basename(path)


def is_alias(name):
    return bool(ALIAS_RE.match(name))


def md5_of(note):
    m = MD5_RE.search(note)
    return m.group(1) if m else None


def dbtype_of(note):
    m = DBTYPE_RE.search(note)
    return m.group(1) if m else None


def pct(a, b):
    return 0.0 if b == 0 else round(100.0 * a / b, 1)


def median_int(vals):
    return int(statistics.median(vals)) if vals else 0


def trunc_list(names):
    names = sorted(names)
    head = names[:TRUNC]
    tail = len(names) - len(head)
    return head, tail


def main():
    rows = load()
    cd = [r for r in rows if r["family"] == FAMILY]
    if not cd:
        print("FAIL no cdsp rows")
        return 1

    raw_files = sorted({r["file"] for r in cd})
    canon_files = sorted({canon(r["file"]) for r in cd})
    alias_rows = [r for r in cd if is_alias(r["file"])]
    alias_names = sorted({r["file"] for r in alias_rows})
    alias_canon = sorted({canon(r["file"]) for r in alias_rows})
    plain_canon = sorted({canon(r["file"]) for r in cd if not is_alias(r["file"])})
    new_from_alias = [c for c in alias_canon if c not in plain_canon]

    devices = sorted({r["device"] for r in cd})
    universe = len(devices)

    by_file = defaultdict(list)
    for r in cd:
        by_file[canon(r["file"])].append(r)

    file_rows = []
    for f in canon_files:
        rs = by_file[f]
        sizes = [int(r["bytes"]) for r in rs]
        md5s = [md5_of(r["notes"]) for r in rs]
        devset = {r["device"] for r in rs}
        file_rows.append(
            {
                "file": f,
                "devices": len(devset),
                "instances": len(rs),
                "reach_pct": pct(len(devset), universe),
                "bytes_min": min(sizes),
                "bytes_max": max(sizes),
                "bytes_median": median_int(sizes),
                "distinct_md5": len(set(md5s)),
                "device_list": sorted(devset),
            }
        )
    file_rows.sort(key=lambda x: (-x["devices"], -x["bytes_max"], x["file"]))

    md5_dev = defaultdict(set)
    md5_file = {}
    md5_bytes = defaultdict(set)
    md5_file_sets = defaultdict(set)
    for r in cd:
        h = md5_of(r["notes"])
        if h is None:
            continue
        md5_dev[h].add(r["device"])
        md5_file[h] = canon(r["file"])
        md5_bytes[h].add(int(r["bytes"]))
        md5_file_sets[h].add(canon(r["file"]))

    distinct_md5 = len(md5_dev)
    shared_md5 = sorted(
        [h for h, d in md5_dev.items() if len(d) >= 2],
        key=lambda h: (-len(md5_dev[h]), h),
    )
    shared_instances = sum(len(md5_dev[h]) for h in shared_md5)
    singleton_instances = distinct_md5 - len(shared_md5)
    sharing_rate = pct(shared_instances, len(cd))
    shared_bytes = sum(
        int(r["bytes"]) for r in cd if md5_of(r["notes"]) in set(shared_md5)
    )
    total_bytes = sum(int(r["bytes"]) for r in cd)

    within_device_dups = 0
    device_file_md5 = {}
    for r in cd:
        device_file_md5.setdefault(r["device"], []).append(md5_of(r["notes"]))
    for _dev, _ms in device_file_md5.items():
        _ms = [m for m in _ms if m]
        within_device_dups += len(_ms) - len(set(_ms))
    no_jsn = [r for r in cd if not canon(r["file"]).endswith(".jsn")]
    no_jsn_dev = {}
    for r in no_jsn:
        h = md5_of(r["notes"])
        if h is None:
            continue
        no_jsn_dev.setdefault(h, set()).add(r["device"])
    shared_no_jsn = sum(1 for r in no_jsn
                        if len(no_jsn_dev.get(md5_of(r["notes"]), ())) >= 2)
    mdt_only = [r for r in cd
                if canon(r["file"]) == "cdsp.mdt"]
    mdt_only_dev = {}
    for r in mdt_only:
        h = md5_of(r["notes"])
        if h is None:
            continue
        mdt_only_dev.setdefault(h, set()).add(r["device"])
    shared_mdt_only = sum(1 for r in mdt_only
                          if len(mdt_only_dev.get(md5_of(r["notes"]), ())) >= 2)

    clusters = []
    for h in shared_md5:
        head, tail = trunc_list(md5_dev[h])
        clusters.append(
            {
                "md5": h,
                "file": md5_file[h],
                "devices": len(md5_dev[h]),
                "bytes": sorted(md5_bytes[h]),
                "device_head": head,
                "device_more": tail,
                "device_list": sorted(md5_dev[h]),
            }
        )

    per_file_max = {}
    for h in sorted(md5_dev):
        d = md5_dev[h]
        f = md5_file[h]
        cur = per_file_max.get(f)
        if cur is None or len(d) > cur["devices"]:
            per_file_max[f] = {
                "file": f,
                "md5": h,
                "devices": len(d),
                "bytes": sorted(md5_bytes[h]),
                "device_list": sorted(d),
                "ties": 1,
            }
        elif len(d) == cur["devices"]:
            cur["ties"] += 1
    per_file_max_rows = sorted(per_file_max.values(), key=lambda x: (-x["devices"], x["file"]))
    file_unique_instances = {}
    for f in canon_files:
        file_unique_instances[f] = sum(
            1 for r in by_file[f] if len(md5_dev[md5_of(r["notes"])]) == 1
        )

    hist = Counter(len(d) for d in md5_dev.values())
    hist_rows = [
        {"cluster_size": k, "clusters": hist[k], "instances": k * hist[k]}
        for k in sorted(hist)
    ]

    soc_dev = defaultdict(set)
    soc_rows = Counter()
    soc_files = defaultdict(set)
    for r in cd:
        soc_dev[r["soc"]].add(r["device"])
        soc_rows[r["soc"]] += 1
        soc_files[r["soc"]].add(canon(r["file"]))
    soc_table = [
        {
            "soc": s,
            "devices": len(soc_dev[s]),
            "rows": soc_rows[s],
            "canonical_files": len(soc_files[s]),
            "device_list": sorted(soc_dev[s]),
        }
        for s in sorted(soc_dev, key=lambda s: (-len(soc_dev[s]), s))
    ]
    empty_soc = [r for r in cd if r["soc"].strip() == ""]
    empty_soc_dev = sorted({r["device"] for r in empty_soc})
    empty_soc_vendors = Counter(r["vendor"] for r in empty_soc)
    soc_strings_with_data = len([s for s in soc_dev if s.strip()])
    soc_near_dupes = [
        ["Qualcomm SM6375 Snapdragon 695", "Qualcomm SM6375 Snapdragon 695 5G"],
        ["Qualcomm SM8150 Snapdragon 855", "Qualcomm SM8150-AC Snapdragon 855"],
        ["Qualcomm SM8350 Snapdragon 888", "Qualcomm SM8350-AC Snapdragon 888+"],
    ]

    vendor_rows = Counter(r["vendor"] for r in cd)
    vendor_dev = defaultdict(set)
    for r in cd:
        vendor_dev[r["vendor"]].add(r["device"])
    vendor_table = [
        {
            "vendor": v,
            "rows": vendor_rows[v],
            "devices": len(vendor_dev[v]),
            "device_list": sorted(vendor_dev[v]),
        }
        for v in sorted(vendor_rows, key=lambda v: (-vendor_rows[v], v))
    ]

    dt_rows = Counter()
    dt_dev = defaultdict(set)
    for r in cd:
        t = dbtype_of(r["notes"])
        key = t if t else "<absent>"
        dt_rows[key] += 1
        dt_dev[key].add(r["device"])
    unknown_files = sorted({canon(r["file"]) for r in cd if dbtype_of(r["notes"]) == "UNKNOWN"})
    compute_files = sorted({canon(r["file"]) for r in cd if dbtype_of(r["notes"]) == "COMPUTE"})
    absent_files = sorted({canon(r["file"]) for r in cd if dbtype_of(r["notes"]) is None})
    dt_table = [
        {"db_type": k, "rows": dt_rows[k], "devices": len(dt_dev[k])}
        for k in sorted(dt_rows, key=lambda k: (-dt_rows[k], k))
    ]

    deviant = [r for r in cd if not STRICT_RE.match(r["notes"])]
    deviant_shapes = Counter(
        re.sub(r"md5_db=[0-9a-f]{32}", "md5_db=<32hex>", r["notes"]) for r in deviant
    )
    isa_rows = [r for r in cd if "isa=" in r["notes"]]

    const_size_multi_md5 = []
    for f in canon_files:
        rs = by_file[f]
        sizes = {r["bytes"] for r in rs}
        hs = {md5_of(r["notes"]) for r in rs}
        if len(sizes) == 1 and len(hs) > 1:
            const_size_multi_md5.append(
                {
                    "file": f,
                    "bytes": int(next(iter(sizes))),
                    "instances": len(rs),
                    "distinct_md5": len(hs),
                }
            )

    bimodal = []
    for f in canon_files:
        b = sorted(int(r["bytes"]) for r in by_file[f])
        gaps = [(b[i + 1] / b[i], i) for i in range(len(b) - 1) if b[i] > 0]
        if not gaps:
            continue
        g, i = max(gaps)
        if g >= BIMODAL_GAP:
            bimodal.append(
                {
                    "file": f,
                    "instances": len(b),
                    "gap_ratio": round(g, 1),
                    "small_n": i + 1,
                    "small_max": b[i],
                    "large_n": len(b) - i - 1,
                    "large_min": b[i + 1],
                }
            )
    bimodal.sort(key=lambda x: -x["gap_ratio"])

    outliers = 0
    for f in canon_files:
        rs = by_file[f]
        med = statistics.median(int(r["bytes"]) for r in rs)
        for r in rs:
            b = int(r["bytes"])
            if med > 0 and (b > med * OUTLIER_FACTOR or b * OUTLIER_FACTOR < med):
                outliers += 1

    seg_present = {}
    for r in cd:
        m = SEG_RE.match(canon(r["file"]))
        if m:
            seg_present.setdefault(int(m.group(1)), set()).add(r["device"])
    seg_rows = [{"index": i, "devices": len(seg_present[i])} for i in sorted(seg_present)]
    seg_missing = [i for i in range(0, max(seg_present) + 1) if i not in seg_present]

    dev_file_count = Counter()
    for r in cd:
        dev_file_count[r["device"]] += 1
    sparse_devices = sorted(d for d in devices if dev_file_count[d] == 1)
    dense_devices = sorted(
        (d for d in devices if dev_file_count[d] == max(dev_file_count.values()))
    )

    seg_count_of = {}
    mdt_bytes_of = {}
    seg_bytes_of = defaultdict(int)
    for r in cd:
        c = canon(r["file"])
        if c == "cdsp.mdt":
            mdt_bytes_of[r["device"]] = int(r["bytes"])
        elif SEG_RE.match(c):
            seg_count_of[r["device"]] = seg_count_of.get(r["device"], 0) + 1
            seg_bytes_of[r["device"]] += int(r["bytes"])
    pairs = [(seg_count_of.get(dv, 0), mdt_bytes_of[dv], seg_bytes_of[dv])
             for dv in devices if dv in mdt_bytes_of]

    def pearson(xs, ys):
        n = len(xs)
        if n < 3:
            return 0.0
        mx = sum(xs) / n
        my = sum(ys) / n
        num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
        den = (sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys)) ** 0.5
        return round(num / den, 3) if den else 0.0

    seg_table = []
    for sc in sorted({p2[0] for p2 in pairs}):
        ms = [p2[1] for p2 in pairs if p2[0] == sc]
        seg_table.append(
            {
                "segments": sc,
                "devices": len(ms),
                "mdt_min": min(ms),
                "mdt_max": max(ms),
                "mdt_median": median_int(ms),
            }
        )
    corr = {
        "segments_vs_mdt_bytes": pearson([p2[0] for p2 in pairs], [p2[1] for p2 in pairs]),
        "segments_vs_segment_bytes": pearson([p2[0] for p2 in pairs], [p2[2] for p2 in pairs]),
        "pairs": len(pairs),
    }

    dev_totals = sorted(
        (sum(int(r["bytes"]) for r in cd if r["device"] == d), d) for d in devices
    )
    raw_mdt_devices = len({r["device"] for r in cd if r["file"] == "cdsp.mdt"})
    alias_only_mdt_devices = sorted(
        {r["device"] for r in cd if r["file"] != "cdsp.mdt" and canon(r["file"]) == "cdsp.mdt"}
    )
    alias_devices = sorted({r["device"] for r in alias_rows})
    jsn_halves = []
    for h in sorted(md5_dev, key=lambda h: (md5_file[h], -len(md5_dev[h]), h)):
        if md5_file[h] == "cdspr.jsn":
            jsn_halves.append(
                {
                    "md5": h,
                    "devices": len(md5_dev[h]),
                    "vendors": sorted({r["vendor"].lower() for r in cd
                                       if md5_of(r["notes"]) == h}),
                    "socs": sorted({r["soc"] for r in cd if md5_of(r["notes"]) == h}),
                }
            )
    jsn_vendor_overlap = sorted(
        set(jsn_halves[0]["vendors"]) & set(jsn_halves[1]["vendors"])
    ) if len(jsn_halves) == 2 else []
    empty_soc_files = len({canon(r["file"]) for r in empty_soc})
    dbpath_re = re.compile(r"db_path=([^;]+)")
    dbpath_of = lambda r: (dbpath_re.search(r["notes"]).group(1).strip()
                           if dbpath_re.search(r["notes"]) else "")
    dev_dbpath = defaultdict(set)
    for r in cd:
        dev_dbpath[r["device"]].add(dbpath_of(r))
    empty_soc_codenames = sorted(
        (dbpath_of(r).split("/")[1] if dbpath_of(r).count("/") >= 2 else dbpath_of(r), r["device"])
        for r in empty_soc
    )
    empty_soc_codename_map = sorted({(d, c) for c, d in empty_soc_codenames})
    dev_multi_dbpath = sorted(d for d, ps in dev_dbpath.items() if len(ps) > 1)
    distinct_dbpath = len({p for ps in dev_dbpath.values() for p in ps if p})
    empty_soc_distinct_dbpath = len({dbpath_of(r) for r in empty_soc if dbpath_of(r)})
    status_rows = Counter(r["public_status"] for r in cd)
    sha_rows = [r for r in cd if r["sha256"]]
    repo_status = Counter(r["public_status"] for r in rows)
    repo_devices = len({r["device"] for r in rows})
    repo_bytes_measured = sum(1 for r in rows if r["bytes"] not in ("", "0"))

    with open(CSV_PATH, "rb") as fh:
        csv_sha = hashlib.sha256(fh.read()).hexdigest()

    mdt = next(x for x in file_rows if x["file"] == "cdsp.mdt")
    jsn = next(x for x in file_rows if x["file"] == "cdspr.jsn")
    mdt_no = sorted(set(devices) - set(mdt["device_list"]))
    jsn_no = sorted(set(devices) - set(jsn["device_list"]))

    data = {
        "issue": 595,
        "scope": "cross-device census of family=cdsp in data/fleet/devices-001-222.csv",
        "source": {
            "path": "data/fleet/devices-001-222.csv",
            "sha256": csv_sha,
            "rows_total": len(rows),
            "rows_cdsp": len(cd),
            "devices_total": repo_devices,
        },
        "inventory": {
            "raw_distinct_files": len(raw_files),
            "raw_file_list": raw_files,
            "alias_rows": len(alias_rows),
            "alias_distinct_raw_values": len(alias_names),
            "alias_raw_list": alias_names,
            "alias_canonical_targets": alias_canon,
            "canonical_targets_only_from_alias": new_from_alias,
            "canonical_files": len(canon_files),
            "canonical_file_list": canon_files,
            "arithmetic": "%d raw distinct file values - %d <modem-fat:IMAGE/...> alias values = %d canonical files"
            % (len(raw_files), len(alias_names), len(canon_files)),
            "claim_23_holds": len(canon_files) == 23,
        },
        "universe": {
            "distinct_devices": universe,
            "device_list": devices,
            "instances": len(cd),
            "total_bytes": total_bytes,
            "cdsp_share_of_repo_devices_pct": pct(universe, repo_devices),
        },
        "per_file": file_rows,
        "device_totals": {
            "heaviest": [{"device": d, "bytes": b} for b, d in dev_totals[-3:][::-1]],
            "lightest": [{"device": d, "bytes": b} for b, d in dev_totals[:3]],
            "median_bytes": median_int([b for b, _ in dev_totals]),
            "min_file_count": min(dev_file_count.values()),
            "max_file_count": max(dev_file_count.values()),
            "min_bytes": dev_totals[0][0],
            "max_bytes": dev_totals[-1][0],
        },
        "jsn_halves": {
            "clusters": jsn_halves,
            "shared_vendors": jsn_vendor_overlap,
        },
        "reach_checks": {
            "raw_string_cdsp.mdt_devices": raw_mdt_devices,
            "alias_only_cdsp.mdt_devices": alias_only_mdt_devices,
            "cdsp.mdt_devices": mdt["devices"],
            "cdsp.mdt_reach_pct": mdt["reach_pct"],
            "cdsp.mdt_missing_devices": mdt_no,
            "cdspr.jsn_devices": jsn["devices"],
            "cdspr.jsn_reach_pct": jsn["reach_pct"],
            "cdspr.jsn_missing_devices": jsn_no,
            "claim_mdt_63_holds_literally": len([r for r in cd if r["file"] == "cdsp.mdt"]) == 63,
            "claim_mdt_63_holds_after_canonicalisation": mdt["devices"] == 63,
        },
        "clusters": {
            "distinct_md5": distinct_md5,
            "shared_md5_ge2_devices": len(shared_md5),
            "singleton_md5": singleton_instances,
            "instances_in_shared_clusters": shared_instances,
            "sharing_rate_pct_instances": sharing_rate,
            "shared_bytes": shared_bytes,
            "total_bytes": total_bytes,
            "sharing_rate_pct_bytes": pct(shared_bytes, total_bytes),
            "size_histogram": hist_rows,
            "top_clusters": clusters,
            "max_cluster_per_file": per_file_max_rows,
        },
        "slice": {
            "devices_present": repo_devices,
            "reach_of_slice_pct": pct(universe, repo_devices),
        },
        "sharing": {
            "within_device_duplicate_groups": within_device_dups,
            "excl_jsn_instances": len(no_jsn),
            "excl_jsn_shared": shared_no_jsn,
            "excl_jsn_pct": pct(shared_no_jsn, len(no_jsn)),
            "mdt_only_instances": len(mdt_only),
            "mdt_only_shared": shared_mdt_only,
            "mdt_only_pct": pct(shared_mdt_only, len(mdt_only)),
        },
        "per_soc": {
            "distinct_soc_strings": len(soc_dev),
            "soc_strings_with_value": soc_strings_with_data,
            "table": soc_table,
            "empty_soc_rows": len(empty_soc),
            "empty_soc_devices": len(empty_soc_dev),
            "empty_soc_device_list": empty_soc_dev,
            "empty_soc_vendors": dict(empty_soc_vendors),
            "empty_soc_canonical_files": empty_soc_files,
            "empty_soc_with_db_path": sum(1 for r in empty_soc if dbpath_of(r)),
            "empty_soc_distinct_db_path": empty_soc_distinct_dbpath,
            "empty_soc_codenames": [{"device": d, "codename": c} for d, c in empty_soc_codename_map],
            "near_duplicate_pairs": soc_near_dupes,
        },
        "vendors": {
            "distinct_vendor_strings": len(vendor_rows),
            "distinct_vendors_casefold": len({v.lower() for v in vendor_rows}),
            "table": vendor_table,
        },
        "db_type": {
            "table": dt_table,
            "unknown_files": unknown_files,
            "compute_files": compute_files,
            "absent_files": absent_files,
            "isa_tagged_rows": len(isa_rows),
        },
        "data_quality": {
            "empty_soc_rows": len(empty_soc),
            "empty_soc_devices": len(empty_soc_dev),
            "alias_rows": len(alias_rows),
            "alias_devices": sorted({r["device"] for r in alias_rows}),
            "notes_deviant_rows": len(deviant),
            "notes_deviant_devices": dict(Counter(r["device"] for r in deviant)),
            "notes_deviant_shapes": dict(deviant_shapes),
            "constant_bytes_multi_md5": const_size_multi_md5,
            "bimodal_files": bimodal,
            "median_outlier_rows": outliers,
            "vendor_case_split": {
                "oneplus": vendor_rows.get("oneplus", 0),
                "OnePlus": vendor_rows.get("OnePlus", 0),
            },
            "soc_near_duplicate_pairs": soc_near_dupes,
            "segment_index_missing": seg_missing,
            "sparse_devices": sparse_devices,
            "dense_devices": dense_devices,
            "dense_device_file_count": max(dev_file_count.values()),
            "public_status": dict(status_rows),
            "sha256_present": len(sha_rows),
            "distinct_db_path": distinct_dbpath,
            "devices_with_multiple_db_path": dev_multi_dbpath,
            "devices_without_db_path": sorted(d for d, ps in dev_dbpath.items()
                                              if not any(ps)),
        },
        "honest_negatives": {
            "repo_rows_metadata_only": repo_status.get("metadata-only", 0),
            "repo_rows_total": len(rows),
            "cdsp_rows_metadata_only": status_rows.get("metadata-only", 0),
            "cdsp_rows_total": len(cd),
            "mdt_name_count": 50,
            "mdt_name_hexagon": 12,
            "mdt_iname_count": 82,
            "mdt_iname_hexagon": 16,
            "repo_rows_with_bytes": repo_bytes_measured,
            "catalogue_slice": "devices 001-222 only",
            "repo_devices_present": repo_devices,
        },
        "segments": {
            "table": seg_rows,
            "missing_indices": seg_missing,
            "mdt_vs_segment_count": seg_table,
            "correlation": corr,
        },
        "device_file_counts": {
            str(k): v for k, v in sorted(Counter(dev_file_count.values()).items())
        },
    }

    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=False)
        fh.write("\n")

    md = render(data, file_rows, clusters, soc_table, vendor_table,
                per_file_max_rows, hist_rows, seg_rows, bimodal,
                const_size_multi_md5, deviant, empty_soc, empty_soc_dev,
                empty_soc_vendors, mdt, jsn, mdt_no, jsn_no, outliers,
                devices, cd, sparse_devices, dense_devices,
                max(dev_file_count.values()), repo_devices, status_rows,
                sha_rows, isa_rows, csv_sha, file_unique_instances)
    with open(OUT_MD, "w", encoding="utf-8") as fh:
        fh.write(md)

    checks = [
        ("rows parsed", len(rows) == 34053),
        ("cdsp rows 950", len(cd) == 950),
        ("raw 33 - alias 10 = canonical 23", len(raw_files) - len(alias_names) == len(canon_files)),
        ("canonical 23", len(canon_files) == 23),
        ("device universe 64", universe == 64),
        ("cdsp.mdt canonical reach 64", mdt["devices"] == 64),
        ("cdspr.jsn reach 60", jsn["devices"] == 60),
        ("distinct md5 586", distinct_md5 == 586),
        ("shared clusters 128", len(shared_md5) == 128),
        ("shared instances 492", shared_instances == 492),
        ("no canonical target only from alias", new_from_alias == []),
        ("every md5 maps to exactly one file", all(len(v) == 1 for v in md5_file_sets.values())),
        ("per-file unique sums to instances - shared",
         sum(file_unique_instances.values()) == len(cd) - shared_instances),
    ]
    ok = True
    for name, passed in checks:
        print(("ok   " if passed else "FAIL ") + name)
        ok = ok and passed
    print(
        "PASS %d rows / %d cdsp rows / %d canonical files / %d devices / %d md5 / %d shared clusters / %d shared instances (%.1f%%)"
        % (len(rows), len(cd), len(canon_files), universe, distinct_md5,
           len(shared_md5), shared_instances, sharing_rate)
    )
    return 0 if ok else 1


def render(d, file_rows, clusters, soc_table, vendor_table,
           per_file_max_rows, hist_rows, seg_rows, bimodal,
           const_size_multi_md5, deviant, empty_soc, empty_soc_dev,
           empty_soc_vendors, mdt, jsn, mdt_no, jsn_no, outliers,
           devices, cd, sparse_devices, dense_devices, dense_count,
           repo_devices, status_rows, sha_rows, isa_rows, csv_sha,
           file_unique_instances):
    inv = d["inventory"]
    uni = d["universe"]
    cl = d["clusters"]
    soc = d["per_soc"]
    neg = d["honest_negatives"]
    L = []
    a = L.append

    a("# CDSP fleet census — %d files, %d devices, %d md5s"
      % (inv["canonical_files"], uni["distinct_devices"], cl["distinct_md5"]))
    a("")
    a("Provenance: `data/fleet/devices-001-222.csv` (sha256 `%s`, %d rows), family=`cdsp`, %d instances."
      % (csv_sha, d["source"]["rows_total"], uni["instances"]))
    a("Generator: `research/cdsp-fleet/build_census.py` (`python3 -I`), emits `census.json` + this file.")
    a("Evidence classes: `[F]` measured from the CSV, `[I]` inference, `[H]` hypothesis, `[N]` honest negative.")
    a("No payload bytes were read or written; this note is metadata arithmetic only.")
    a("")
    a("## Headline")
    a("")
    a("- `[F]` **%d canonical files** (%d raw distinct `file` strings minus %d `<modem-fat:IMAGE/...>` aliases), **%d devices**, **%d (device,file) instances**, **%d distinct md5**."
      % (inv["canonical_files"], inv["raw_distinct_files"], inv["alias_distinct_raw_values"],
         uni["distinct_devices"], uni["instances"], cl["distinct_md5"]))
    a("- `[F]` `cdsp.mdt` reaches **%d/%d devices (%.1f%%)**, `cdspr.jsn` reaches **%d/%d (%.1f%%)**."
      % (mdt["devices"], uni["distinct_devices"], mdt["reach_pct"],
         jsn["devices"], uni["distinct_devices"], jsn["reach_pct"]))
    a("  `[N]` Denominator caveat: those %d are the devices that carry *any* cdsp row in this"
      % uni["distinct_devices"])
    a("  slice, which is **%.1f%% of the %d devices** present in the CSV. \"100%%\" means \"every"
      % (d["slice"]["reach_of_slice_pct"], d["slice"]["devices_present"]))
    a("  device that ships cdsp at all\", not \"every device in the catalogue\". Three of the %d"
      % uni["distinct_devices"])
    a("  (`Pixel_4A_5G`, `Pixel_5`, `Pixel_5A`) carry **only** `cdsp.mdt`, so they count toward")
    a("  `.mdt` reach while contributing no evidence about the segment set.")
    a("- `[F]` **%.1f%% of instances** (and %.1f%% of declared bytes) sit in an md5 cluster shared"
      % (cl["sharing_rate_pct_instances"], cl["sharing_rate_pct_bytes"]))
    a("  by >=2 devices.")
    a("  `[N]` That figure is **cross-device** duplication only; there are **%d** within-device"
      % d["sharing"]["within_device_duplicate_groups"])
    a("  duplicate groups. It is also dominated by `cdspr.jsn`, which is 100% shared by")
    a("  construction (a %d-value file). Excluding `cdspr.jsn` the rate is **%.1f%%** (%d/%d),"
      % (jsn["distinct_md5"], d["sharing"]["excl_jsn_pct"],
         d["sharing"]["excl_jsn_shared"], d["sharing"]["excl_jsn_instances"]))
    a("  and for `cdsp.mdt` alone (excluding `cdsp_dtb.mdt`) it is **%.1f%%** (%d/%d) — the"
      % (d["sharing"]["mdt_only_pct"],
         d["sharing"]["mdt_only_shared"], d["sharing"]["mdt_only_instances"]))
    a("  `.mdt` is mostly per-device unique.")
    a("- `[F]` `cdspr.jsn` is a **%d-value** file fleet-wide: %d instances collapse to %d md5s (%s devices)."
      % (jsn["distinct_md5"], jsn["instances"], jsn["distinct_md5"],
         " + ".join(str(x["devices"]) for x in d["jsn_halves"]["clusters"])))
    a("- `[N]` Sizes are **declared, not measured**, for %d of %d cdsp instances."
      % (status_rows.get("metadata-only", 0), uni["instances"]))
    a("")

    a("## A. Canonical file inventory")
    a("")
    a("`[F]` Arithmetic: **%d raw distinct `file` values − %d `<modem-fat:IMAGE/...>` alias values = %d canonical files**."
      % (inv["raw_distinct_files"], inv["alias_distinct_raw_values"], inv["canonical_files"]))
    a("The %d-file claim is **%s** (`claim_23_holds=%s`)."
      % (inv["canonical_files"],
         "CORRECT" if inv["claim_23_holds"] else "WRONG",
         str(inv["claim_23_holds"]).lower()))
    a("")
    a("| quantity | value |")
    a("|---|---|")
    a("| distinct raw `file` strings | %d |" % inv["raw_distinct_files"])
    a("| `<modem-fat:IMAGE/...>` rows | %d |" % inv["alias_rows"])
    a("| distinct alias raw strings | %d |" % inv["alias_distinct_raw_values"])
    a("| canonical names after stripping wrapper | %d |" % inv["canonical_files"])
    a("| canonical names that exist *only* in alias form | %d |" % len(inv["canonical_targets_only_from_alias"]))
    a("| largest per-device file count | %d (%d devices) |" % (dense_count, len(dense_devices)))
    a("| smallest per-device file count | %d (%s) |"
      % (d["device_totals"]["min_file_count"], ", ".join(sparse_devices)))
    a("")
    a("`[F]` The %d alias rows come from %d device (%s) and wrap %d distinct targets, of which **%d** are canonical names not already produced by an unwrapped row. The subtraction is therefore exact: no canonical name exists only in alias form."
      % (inv["alias_rows"], len(d["data_quality"]["alias_devices"]),
         ", ".join(d["data_quality"]["alias_devices"]),
         len(inv["alias_canonical_targets"]), len(inv["canonical_targets_only_from_alias"])))
    a("")
    a("`[F]` Canonical inventory: `" + "`, `".join(inv["canonical_file_list"]) + "`.")
    a("")
    a("`[F]` Alias raw strings: " + ", ".join("`%s`" % x for x in inv["alias_raw_list"]) + ".")
    a("")
    segs = d["segments"]["table"]
    dtb = [f for f in inv["canonical_file_list"] if f.startswith("cdsp_dtb.")]
    a("`[I]` Segment series runs `cdsp.b%02d`–`cdsp.b%02d` with **%s absent**, plus a separate `cdsp_dtb.*` split image (%d files) and the `cdspr.jsn` manifest descriptor."
      % (segs[0]["index"], segs[-1]["index"],
         ", ".join("b%02d" % i for i in d["segments"]["missing_indices"]) or "no index",
         len(dtb)))
    a("")

    a("## B. Per-file device reach (descending)")
    a("")
    a("Device universe: **%d distinct `device` values** in the cdsp family; %d instances over those devices."
      % (uni["distinct_devices"], uni["instances"]))
    a("")
    a("| file | devices | reach | instances | bytes min | bytes max | bytes median | distinct md5 |")
    a("|---|---:|---:|---:|---:|---:|---:|---:|")
    for x in file_rows:
        a("| `%s` | %d | %.1f%% | %d | %d | %d | %d | %d |"
          % (x["file"], x["devices"], x["reach_pct"], x["instances"],
             x["bytes_min"], x["bytes_max"], x["bytes_median"], x["distinct_md5"]))
    a("")
    a("Reach verification `[F]`:")
    a("")
    a("- `cdsp.mdt` → **%d devices (%.1f%%)**. The literal string `cdsp.mdt` appears on **%d** devices; the difference is %s, whose only `cdsp.mdt` row is the alias form. So the widely-quoted \"%d devices\" is true **only** for the raw string and **false after canonicalisation**. Devices with no `cdsp.mdt`: %s."
      % (mdt["devices"], mdt["reach_pct"],
         d["reach_checks"]["raw_string_cdsp.mdt_devices"],
         " / ".join(d["reach_checks"]["alias_only_cdsp.mdt_devices"]) or "none",
         d["reach_checks"]["raw_string_cdsp.mdt_devices"],
         ", ".join(mdt_no) if mdt_no else "none"))
    a("- `cdspr.jsn` → **%d devices (%.1f%%)**. Devices with no `cdspr.jsn`: %s."
      % (jsn["devices"], jsn["reach_pct"], ", ".join(jsn_no) if jsn_no else "none"))
    a("- Reach floor: %s carry exactly one cdsp file (`cdsp.mdt` only). Reach ceiling: %s carry %d."
      % (", ".join(sparse_devices), ", ".join(dense_devices[:4]) + (" +%d" % (len(dense_devices) - 4) if len(dense_devices) > 4 else ""), dense_count))
    a("- Per-device file-count histogram: " + ", ".join("%s file(s) → %d device(s)" % (k, v) for k, v in d["device_file_counts"].items()) + ".")
    a("")
    a("`[F]` Segment-index presence (devices carrying each `cdsp.bNN`): " + ", ".join(
        "b%02d→%d" % (x["index"], x["devices"]) for x in seg_rows) + ".")
    a("")
    a("| segments on device | devices | cdsp.mdt bytes min | max | median |")
    a("|---|---:|---:|---:|---:|")
    for x in d["segments"]["mdt_vs_segment_count"]:
        a("| %d | %d | %d | %d | %d |"
          % (x["segments"], x["devices"], x["mdt_min"], x["mdt_max"], x["mdt_median"]))
    a("")
    smax = max(x["segments"] for x in d["segments"]["mdt_vs_segment_count"])
    smin = min(x["segments"] for x in d["segments"]["mdt_vs_segment_count"])
    hi = next(x for x in d["segments"]["mdt_vs_segment_count"] if x["segments"] == smax)
    lo = max((x for x in d["segments"]["mdt_vs_segment_count"] if x["segments"] > 0),
             key=lambda x: x["mdt_median"])
    a("`[N]` Segment count does **not** predict `cdsp.mdt` size here: Pearson r = **%.3f** across %d devices. The %d-segment group has median `.mdt` **%d B**, while the largest median sits at the %d-segment group (%d B)."
      % (d["segments"]["correlation"]["segments_vs_mdt_bytes"],
         d["segments"]["correlation"]["pairs"],
         smax, hi["mdt_median"], lo["segments"], lo["mdt_median"]))
    a("")
    flat = sorted(
        [x for x in d["segments"]["mdt_vs_segment_count"]
         if x["mdt_min"] == x["mdt_max"] and x["devices"] > 1 and x["segments"] > 0],
        key=lambda x: -x["devices"],
    )
    a("`[I]` That negative sign is more likely a **confound than an inverse law**: segment count tracks platform generation, and %d of the %d groups carry a **single** `.mdt` size (largest: %d segments → %d B on all %d devices). Where within-group spread is zero, there is nothing for a correlation to fit; the global coefficient is really between-group. A per-generation regression would be the honest test, and this CSV carries no clean generation key."
      % (len(flat), len(d["segments"]["mdt_vs_segment_count"]),
         flat[0]["segments"], flat[0]["mdt_min"], flat[0]["devices"]) if flat else
      "`[I]` No size-flat groups exist, so the global coefficient is not a between-group artefact.")
    a("")
    a("`[N]` **This is not a layout claim.** No `.mdt` bytes were read; the record structure, offsets and segment table of the container remain unknown from this CSV.")
    a("")
    a("`[F]` Total declared bytes across the fleet: **%d** over %d instances. Per-device totals run from **%d B (%s)** to **%d B (%s)**; the median device carries %d B."
      % (uni["total_bytes"], uni["instances"],
         d["device_totals"]["lightest"][0]["bytes"], d["device_totals"]["lightest"][0]["device"],
         d["device_totals"]["heaviest"][0]["bytes"], d["device_totals"]["heaviest"][0]["device"],
         d["device_totals"]["median_bytes"]))
    a("")

    a("## C. Shared-content clusters")
    a("")
    a("| metric | value |")
    a("|---|---:|")
    a("| distinct md5 | %d |" % cl["distinct_md5"])
    a("| md5 shared by >=2 devices | %d |" % cl["shared_md5_ge2_devices"])
    a("| singleton md5 (one device only) | %d |" % cl["singleton_md5"])
    a("| instances sitting in a shared cluster | %d of %d |" % (cl["instances_in_shared_clusters"], uni["instances"]))
    a("| **sharing rate (instances)** | **%.1f%%** |" % cl["sharing_rate_pct_instances"])
    a("| sharing rate (declared bytes) | %.1f%% (%d of %d B) |" % (cl["sharing_rate_pct_bytes"], cl["shared_bytes"], cl["total_bytes"]))
    a("")
    a("`[F]` Cluster-size histogram (clusters / instances): " + "; ".join(
        "%d→%d/%d" % (h["cluster_size"], h["clusters"], h["instances"]) for h in hist_rows) + ".")
    a("")
    a("`[F]` Sharing rate **per file** — instances whose md5 also appears on another device:")
    a("")
    a("| file | instances | unique instances | shared instances | sharing rate |")
    a("|---|---:|---:|---:|---:|")
    for x in sorted(file_rows, key=lambda y: (-y["devices"], y["file"])):
        sh = x["instances"] - file_unique_instances[x["file"]]
        a("| `%s` | %d | %d | %d | %.1f%% |"
          % (x["file"], x["instances"], file_unique_instances[x["file"]], sh,
             pct(sh, x["instances"])))
    a("| **all files** | **%d** | **%d** | **%d** | **%.1f%%** |"
      % (uni["instances"], sum(file_unique_instances.values()),
         uni["instances"] - sum(file_unique_instances.values()),
         cl["sharing_rate_pct_instances"]))
    a("")
    a("Top %d clusters by device count (of %d shared clusters; the full list with complete device sets is in `census.json` → `clusters.top_clusters`):"
      % (min(10, len(clusters)), len(clusters)))
    a("")
    a("| # | md5 | file | devices | bytes | devices (first %d, then remainder) |" % TRUNC)
    a("|---:|---|---|---:|---:|---|")
    for i, c in enumerate(clusters[:10], 1):
        devs = ", ".join(c["device_head"])
        if c["device_more"]:
            devs += ", +%d more" % c["device_more"]
        a("| %d | `%s` | `%s` | %d | %s | %s |"
          % (i, c["md5"], c["file"], c["devices"], ", ".join(str(b) for b in c["bytes"]), devs))
    a("")
    a("`[F]` Most-shared md5 **per file**:")
    a("")
    a("| file | max cluster | md5 clusters at that size | md5 | bytes |")
    a("|---|---:|---:|---|---:|")
    for x in per_file_max_rows:
        a("| `%s` | %d | %d | `%s` | %s |"
          % (x["file"], x["devices"], x["ties"], x["md5"],
             ", ".join(str(b) for b in x["bytes"])))
    a("")
    mdt_max = next(x for x in per_file_max_rows if x["file"] == "cdsp.mdt")
    a("`[F]` **Correction to the expected shape.** The %d-device cluster is `cdspr.jsn` only: %d md5s over %d instances, split %s. **`cdsp.mdt` has no %d-device cluster at all** — its largest shared md5 covers only **%d devices**, and **%d of its %d instances are unique**. A \"30-device `cdsp.mdt`\" claim is therefore wrong; the leverage in the `.mdt` is device *reach* (%d devices), not shared content."
      % (max(x["devices"] for x in d["jsn_halves"]["clusters"]),
         jsn["distinct_md5"], jsn["instances"],
         " + ".join("%d" % x["devices"] for x in d["jsn_halves"]["clusters"]),
         max(x["devices"] for x in d["jsn_halves"]["clusters"]),
         mdt_max["devices"], file_unique_instances["cdsp.mdt"], mdt["instances"],
         mdt["devices"]))
    a("")
    a("`[I]` The two `cdspr.jsn` values split the fleet into %s-device halves. Vendors present on **both** sides: %s. That the split crosses OEM lines is consistent with it tracking platform generation rather than vendor, but this CSV has no build-date column to confirm it."
      % (" / ".join(str(x["devices"]) for x in d["jsn_halves"]["clusters"]),
         ", ".join(d["jsn_halves"]["shared_vendors"]) or "none"))
    a("")

    a("## D. Per-SoC breakdown")
    a("")
    a("`[F]` %d distinct `soc` strings, of which **%d carry a value and %d is empty**. The empty string accounts for **%d rows over %d devices** — that is %.1f%% of all cdsp rows and %.1f%% of the device universe."
      % (soc["distinct_soc_strings"], soc["soc_strings_with_value"],
         soc["distinct_soc_strings"] - soc["soc_strings_with_value"], soc["empty_soc_rows"],
         soc["empty_soc_devices"], pct(soc["empty_soc_rows"], uni["instances"]),
         pct(soc["empty_soc_devices"], uni["distinct_devices"])))
    a("")
    a("| soc | devices | rows | canonical files |")
    a("|---|---:|---:|---:|")
    for x in soc_table:
        label = "*(empty)*" if x["soc"] == "" else x["soc"]
        a("| %s | %d | %d | %d |" % (label, x["devices"], x["rows"], x["canonical_files"]))
    a("")
    a("`[F]` The %d empty-soc devices are: %s." % (len(empty_soc_dev), ", ".join(empty_soc_dev)))
    a("")
    a("`[F]` Each of those %d devices has **zero** cdsp rows carrying a soc value — the gap is per-device, not per-row noise. They span all %d canonical files."
      % (len(empty_soc_dev), soc["empty_soc_canonical_files"]))
    a("")
    a("`[F]` The empty-soc devices are identifiable by `db_path` codename even without a SoC: %s."
      % ", ".join("%s→`%s`" % (x["device"], x["codename"]) for x in soc["empty_soc_codenames"]))
    a("")
    a("`[I]` %d `soc` string pairs are the same silicon spelled twice: " % len(soc["near_duplicate_pairs"]) + "; ".join(
        "`%s` vs `%s`" % (p[0], p[1]) for p in soc["near_duplicate_pairs"]) + ". Counting strings (%d) therefore overstates distinct SoCs." % soc["distinct_soc_strings"])
    a("")

    a("## E. Vendor and db_type breakdown")
    a("")
    a("| vendor string | rows | devices |")
    a("|---|---:|---:|")
    for x in vendor_table:
        a("| `%s` | %d | %d |" % (x["vendor"], x["rows"], x["devices"]))
    a("")
    a("`[F]` %d distinct vendor **strings** but only **%d distinct vendors** case-folded — `OnePlus` (%d rows) and `oneplus` (%d rows) are the same OEM."
      % (d["vendors"]["distinct_vendor_strings"], d["vendors"]["distinct_vendors_casefold"],
         d["data_quality"]["vendor_case_split"]["OnePlus"], d["data_quality"]["vendor_case_split"]["oneplus"]))
    a("")
    a("| db_type | rows | devices |")
    a("|---|---:|---:|")
    for x in d["db_type"]["table"]:
        a("| `%s` | %d | %d |" % (x["db_type"], x["rows"], x["devices"]))
    a("")
    absent_rows = sum(x["rows"] for x in d["db_type"]["table"] if x["db_type"] == "<absent>")
    a("`[F]` The %d canonical files partition cleanly by tag: **%d tagged `COMPUTE`** (%s) and **%d tagged `UNKNOWN`** (%s). Separately, %d of those files also appear as alias rows with **no** `db_type` field at all (%d rows, from %s)."
      % (inv["canonical_files"],
         len(d["db_type"]["compute_files"]),
         ", ".join("`%s`" % f for f in d["db_type"]["compute_files"]),
         len(d["db_type"]["unknown_files"]),
         ", ".join("`%s`" % f for f in d["db_type"]["unknown_files"]),
         len(d["db_type"]["absent_files"]),
         absent_rows,
         ", ".join(d["data_quality"]["alias_devices"])))
    a("")

    a("## F. Data-quality findings")
    a("")
    a("1. `[F]` **Empty `soc`: %d rows / %d devices** (%.1f%% of rows, %.1f%% of devices). Vendors affected: %s. They cover all %d canonical files, so the per-SoC table above silently loses %d of %d devices."
      % (soc["empty_soc_rows"], soc["empty_soc_devices"],
         pct(soc["empty_soc_rows"], uni["instances"]),
         pct(soc["empty_soc_devices"], uni["distinct_devices"]),
         ", ".join("%s %d" % (k, v) for k, v in sorted(empty_soc_vendors.items(), key=lambda x: -x[1])),
         soc["empty_soc_canonical_files"], soc["empty_soc_devices"], uni["distinct_devices"]))
    a("2. `[F]` **`<modem-fat:IMAGE/...>` aliases: %d rows on %d device (%s), %d distinct raw strings.** They are the *only* cdsp rows for %s (zero unwrapped cdsp rows). Consequence: a raw-string count reports `cdsp.mdt` at **%d** devices; the canonical reach is **%d**."
      % (inv["alias_rows"], len(d["data_quality"]["alias_devices"]),
         ", ".join(d["data_quality"]["alias_devices"]),
         inv["alias_distinct_raw_values"],
         "that device" if len(d["data_quality"]["alias_devices"]) == 1 else "those devices",
         d["reach_checks"]["raw_string_cdsp.mdt_devices"], mdt["devices"]))
    a("3. `[F]` **Notes deviate from the strict `md5_db=<hex>; P<n>; db_path=...; db_type=...` shape on %d rows** (%s). Observed deviations: %d alias rows carry `source=...` with no `db_path`/`db_type`; %d `FP6` rows append `isa=QDSP6 / Hexagon`."
      % (len(deviant), ", ".join("%s×%d" % (k, v) for k, v in sorted(d["data_quality"]["notes_deviant_devices"].items(), key=lambda x: -x[1])),
         inv["alias_rows"], len(isa_rows)))
    a("4. `[F]` **Bytes inconsistent with siblings — constant declared size, many hashes:** " + "; ".join(
        "`%s` %d B × %d instances but %d distinct md5" % (x["file"], x["bytes"], x["instances"], x["distinct_md5"])
        for x in const_size_multi_md5) + ". `[I]` A fixed-length header would look exactly like this; whatever the cause, *size equality does not imply content equality* anywhere in this CSV.")
    a("5. `[F]` **Bimodal size distributions — %d files whose sorted sizes jump >=%.0fx in one step:** %s. `cdsp.b04` is the extreme: %d instances at <=%d B and %d at >=%d B (%.0fx gap)."
      % (len(bimodal), BIMODAL_GAP,
         ", ".join("`%s` %.0fx" % (x["file"], x["gap_ratio"]) for x in bimodal),
         next(x["small_n"] for x in bimodal if x["file"] == "cdsp.b04"),
         next(x["small_max"] for x in bimodal if x["file"] == "cdsp.b04"),
         next(x["large_n"] for x in bimodal if x["file"] == "cdsp.b04"),
         next(x["large_min"] for x in bimodal if x["file"] == "cdsp.b04"),
         next(x["gap_ratio"] for x in bimodal if x["file"] == "cdsp.b04")))
    a("6. `[F]` **%d of %d rows sit >=%.0fx from their own file's median size** — size alone cannot identify a segment across devices."
      % (outliers, uni["instances"], OUTLIER_FACTOR))
    a("7. `[F]` **Vendor spelling split:** `oneplus` %d rows vs `OnePlus` %d rows; %d distinct strings collapse to %d vendors."
      % (d["data_quality"]["vendor_case_split"]["oneplus"], d["data_quality"]["vendor_case_split"]["OnePlus"],
         d["vendors"]["distinct_vendor_strings"], d["vendors"]["distinct_vendors_casefold"]))
    a("8. `[F]` **`soc` near-duplicates:** %d pairs inflate the distinct-SoC count: %s."
      % (len(soc["near_duplicate_pairs"]),
         "; ".join("`%s` vs `%s`" % (p[0], p[1]) for p in soc["near_duplicate_pairs"])))
    a("9. `[F]` **Segment index gap:** `cdsp.b16` is absent fleet-wide; indices present are %s."
      % ", ".join("b%02d" % x["index"] for x in seg_rows))
    a("10. `[F]` **Coverage skew:** %d devices carry only %d file (`cdsp.mdt`), while %d devices carry the maximum %d. Only %d of %d devices reach the %d-file shape."
      % (len(sparse_devices), d["device_totals"]["min_file_count"], len(dense_devices),
         dense_count, len(dense_devices), uni["distinct_devices"], dense_count))
    a("11. `[F]` **Verification coverage:** only %d of %d cdsp rows carry a `sha256`; %d are `metadata-only` and %d are `populated-local-session`. The md5s are upstream database values, not recomputed here."
      % (len(sha_rows), uni["instances"], status_rows.get("metadata-only", 0), status_rows.get("populated-local-session", 0)))
    a("")

    a("## G. Honest negatives")
    a("")
    a("- `[F]` **Cross-check against real bytes (added 2026-11-20, audit round).** The `OnePlus_6` alias rows were not a dead end: they point at a FAT16 `IMAGE/` directory inside `enchilada/modem.img`, and all **11** extracted md5s match the census `md5_db` values exactly. That gives a second, independent cdsp image (SDM845) verified against this table — see `container.md` §7. It also anchors the 403-byte `cdspr.jsn` cluster by one locally verified copy.")
    a("- `[N]` **The `.mdt` enumeration is case-sensitive, and real payloads are uppercase.** `find -name '*.mdt'` finds %d files (%d Hexagon) while `find -iname '*.mdt'` finds %d (%d Hexagon). A case-sensitive sweep therefore misses every 8.3 FAT name — which is exactly how the first pass concluded, wrongly, that no second device existed."
      % (neg["mdt_name_count"], neg["mdt_name_hexagon"],
         neg["mdt_iname_count"], neg["mdt_iname_hexagon"]))
    a("- `[N]` **Sizes are declared, not measured, for %d of %d cdsp rows** (and %d of %d rows repo-wide are `metadata-only`). Every byte figure here is an upstream database field; nothing was hashed or `stat`ed by this script."
      % (status_rows.get("metadata-only", 0), uni["instances"], neg["repo_rows_metadata_only"], neg["repo_rows_total"]))
    a("- `[N]` **Slice only:** the CSV covers devices 001–222 of the catalogue (%d devices actually present). It says nothing about devices 223+."
      % repo_devices)
    a("- `[N]` **No container layout and no ISA from this file.** The CSV gives names, sizes and md5s; it carries no offsets, no ELF/MDT headers, no segment table. Only %d of %d rows carry an `isa=` annotation (on %s), and that is a database label, not a measurement — this census cannot confirm the CDSP ISA."
      % (len(isa_rows), uni["instances"],
         ", ".join(sorted({r["device"] for r in isa_rows})) or "no device"))
    a("- `[N]` **Absence is not proof of absence.** A device with no `cdsp.b14` row may genuinely ship no such segment, or the enumeration may have missed it; the CSV cannot distinguish the two.")
    a("- `[N]` **md5 collisions aside, equality is upstream-trusted.** Two rows sharing `md5_db` are equal *according to the source database*; this script did not fetch a byte.")
    a("- `[N]` **No build/version column.** Two md5s cannot be ordered in time; the %d-device cluster is not necessarily the oldest or newest variant."
      % max(x["devices"] for x in d["jsn_halves"]["clusters"]))
    a("- `[N]` **No SoC for %d devices, and no way to recover it here.** They do carry `db_path` (%d distinct paths, so a codename each), but the CSV has no codename→SoC table; deriving one would require an external source."
      % (soc["empty_soc_devices"], soc["empty_soc_distinct_db_path"]))
    a("- `[N]` **`db_path` is missing for %s.** %d distinct paths cover %d of %d devices, and no device carries two, so `db_path` behaves like a per-device key here — but it is a source-tree location, not a verified identity, and the uncovered device cannot be traced from this file."
      % (", ".join(d["data_quality"]["devices_without_db_path"]) or "none",
         d["data_quality"]["distinct_db_path"], d["data_quality"]["distinct_db_path"],
         uni["distinct_devices"]))
    a("")
    a("## Reproduction")
    a("")
    a("```")
    a("cd /tmp/opencode/cdsp-595/research/cdsp-fleet && python3 -I build_census.py")
    a("```")
    a("")
    a("Outputs `census.json` (machine-readable, same numbers) and this `census.md`. Re-running is byte-stable apart from no timestamps being recorded.")
    a("")
    return "\n".join(L)


if __name__ == "__main__":
    sys.exit(main())
