import csv, json, os
from collections import defaultdict

BASE = "/home/aditya/.zcode/workspace/draft-edfb884f-51a0-40a6-ae53-6cf6375c0730"
REPO = os.path.join(BASE, "librephone-blob-research")
BD = os.path.join(REPO, "upstream-contribution", "blob-database")
OUTDIR = os.path.join(REPO, "blob-matrix", "desktop")
os.makedirs(OUTDIR, exist_ok=True)
OUT = os.path.join(BASE, "analysis", "out")
os.makedirs(OUT, exist_ok=True)

def clean(s):
    if s is None:
        return ""
    return s.replace("\ufffd", "").strip()

inventory = []
with open(os.path.join(BD, "device-inventory.csv"), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        for k in row:
            row[k] = clean(row[k])
        name = row["model"] if row["model"] else row["build_codename"]
        row["_name"] = name
        inventory.append(row)

inventory.sort(key=lambda r: r["_name"])
universe_size = len(inventory)
desktop_rows = inventory[:222]
laptop_flagged = inventory[222:]
desktop_names = {r["_name"] for r in desktop_rows}

matrix_by_device = defaultdict(list)
with open(os.path.join(BD, "coverage-matrix.csv"), newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        for k in row:
            row[k] = clean(row[k])
        matrix_by_device[row["device"]].append(row)

matrix_codename = {}
for mdev, mrows in matrix_by_device.items():
    parts = mrows[0]["db_path"].split("/")
    if len(parts) >= 2 and parts[1]:
        matrix_codename[parts[1]] = mdev

desktop_codenames = {r["build_codename"] for r in desktop_rows}
populated_codenames = desktop_codenames & set(matrix_codename)

inv_by_name = {}
for r in inventory:
    inv_by_name.setdefault(r["_name"], r)

out_csv = os.path.join(OUTDIR, "devices-001-222.csv")
n_blob_rows = 0
n_populated = 0
half_bytes = 0
fam = defaultdict(lambda: [0, 0])
per_device_bytes = {}
status_counts = defaultdict(int)

with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["device", "vendor", "soc", "family", "file", "bytes", "sha256", "public_status", "notes"])
    for dev in desktop_rows:
        name = dev["_name"]
        vendor = dev["vendor"]
        soc = dev["soc"]
        mdev = matrix_codename.get(dev["build_codename"])
        rows = matrix_by_device.get(mdev, []) if mdev else []
        if rows:
            n_populated += 1
            dev_bytes = 0
            if not vendor:
                vendor = rows[0]["vendor"]
            if not soc:
                for r0 in rows:
                    if r0["soc"]:
                        soc = r0["soc"]
                        break
            status_counts["populated-upstream-metadata"] += 1
            for m in rows:
                try:
                    b = int(m["size_bytes"])
                except ValueError:
                    b = 0
                n_blob_rows += 1
                dev_bytes += b
                half_bytes += b
                fam[m["blob_family"]][0] += 1
                fam[m["blob_family"]][1] += b
                notes = []
                if m["md5_db"]:
                    notes.append("md5_db=" + m["md5_db"])
                if m["blob_subfamily"]:
                    notes.append("subfamily=" + m["blob_subfamily"])
                if m["priority"]:
                    notes.append(m["priority"])
                if m["db_path"]:
                    notes.append("db_path=" + m["db_path"])
                if m["db_type"]:
                    notes.append("db_type=" + m["db_type"])
                if m["isa_identified"]:
                    notes.append("isa=" + m["isa_identified"])
                if m["interface_documented"] == "y":
                    notes.append("interface-documented")
                w.writerow([name, vendor, soc, m["blob_family"], m["filename"], b,
                            m["sha256_if_listed"], "metadata-only",
                            "; ".join(notes)])
            per_device_bytes[name] = dev_bytes
        else:
            if dev["in_devices_sql"] == "y" and not dev["blob_rows_devices_sql"]:
                st = "listed-not-populated"
            elif dev["in_builds_csv"] == "y":
                st = "builds-csv-only"
            else:
                st = "inventory-only"
            status_counts[st] += 1
            notes = []
            if dev["mainline_basis_or_note"]:
                notes.append("mainline_note=" + dev["mainline_basis_or_note"])
            if dev["priority"]:
                notes.append(dev["priority"])
            if dev["extract_status_22.2"] if "extract_status_22.2" in dev else False:
                notes.append("extract22.2=" + dev["extract_status_22.2"])
            w.writerow([name, vendor, soc, "none", "", 0, "", st, "; ".join(notes)])

group = defaultdict(set)
for dev, rows in matrix_by_device.items():
    for m in rows:
        try:
            sz = int(m["size_bytes"])
        except ValueError:
            sz = 0
        if sz < 1024:
            continue
        if m["filename"].lower().endswith((".jsn", ".json", ".xml", ".txt")):
            continue
        group[(m["filename"], m["md5_db"])].add(dev)

top20 = sorted(group.items(), key=lambda kv: -len(kv[1]))[:20]
top20_in_half = []
for (fn, md5), devs in top20:
    d = sorted(devs & desktop_names)
    if d:
        top20_in_half.append({"file": fn, "md5": md5, "devices_all": len(devs),
                              "devices_in_half": len(d), "devices": d})
top20_in_half.sort(key=lambda e: -e["devices_in_half"])
top20_out_half = [{"file": fn, "devices_all": len(devs),
                   "devices_out": sorted(devs - desktop_names)}
                  for (fn, md5), devs in top20 if not (devs & desktop_names)]

soc_count = defaultdict(int)
for r in desktop_rows:
    soc_count[r["soc"] if r["soc"] else "(blank)"] += 1

shared_in_half = defaultdict(int)
for (fn, md5), devs in group.items():
    devs_half = devs & desktop_names
    if len(devs_half) > 1:
        shared_in_half[(fn, md5)] = len(devs_half)

summary = {
    "universe": "device-inventory.csv 249 identities, sorted codepoint by model-fallback-codename name",
    "universe_size": universe_size,
    "desktop_rows": "1-222 (literal workorder rows)",
    "desktop_devices": len(desktop_rows),
    "laptop_flagged_rows": "223-249",
    "laptop_flagged_devices": [r["_name"] for r in laptop_flagged],
    "devices_csv_tokens": 123,
    "tokens_equal_matrix_devices": True,
    "desktop_populated": n_populated,
    "desktop_status_counts": dict(status_counts),
    "desktop_blob_rows": n_blob_rows,
    "desktop_total_bytes": half_bytes,
    "family_breakdown": {k: {"rows": v[0], "bytes": v[1]} for k, v in sorted(fam.items(), key=lambda kv: -kv[1][1])},
    "top20_leverage_in_half": top20_in_half,
    "top20_leverage_out_half": top20_out_half,
    "soc_counts": dict(sorted(soc_count.items(), key=lambda kv: -kv[1])),
    "top15_devices_by_bytes": sorted(per_device_bytes.items(), key=lambda kv: -kv[1])[:15],
    "shared_blob_instances_in_half": len(shared_in_half),
    "shared_blob_top15_in_half": [
        {"file": k[0], "md5": k[1], "devices": v}
        for k, v in sorted(shared_in_half.items(), key=lambda kv: -kv[1])[:15]],
    "desktop_device_list_with_rows": [
        {"row": i + 1, "name": r["_name"], "vendor": r["vendor"], "soc": r["soc"],
         "priority": r["priority"], "populated": r["build_codename"] in populated_codenames}
        for i, r in enumerate(desktop_rows)],
}

with open(os.path.join(OUT, "phase1-final.json"), "w") as f:
    json.dump(summary, f, indent=1, sort_keys=True)

compact = {k: summary[k] for k in ["universe_size", "desktop_devices", "desktop_populated",
                                   "desktop_status_counts", "desktop_blob_rows", "desktop_total_bytes",
                                   "laptop_flagged_devices"]}
census_path = os.path.join(OUTDIR, "enchilada-census.csv")
if not os.path.exists(census_path):
    census_path = os.path.join(BASE, "analysis", "out", "enchilada-census.csv")
census_rows = []
if os.path.exists(census_path):
    with open(census_path, newline="", encoding="utf-8") as f:
        r = csv.reader(f)
        next(r)
        census_rows = [row for row in r]

with open(out_csv, newline="", encoding="utf-8") as f:
    all_rows = list(csv.reader(f))

header, body = all_rows[0], all_rows[1:]
kept = [row for row in body if not (row[0] == "OnePlus_6" and row[3] == "none")]
seen = set()
deduped_census = []
for row in census_rows:
    key = (row[4], row[6])
    if key not in seen:
        seen.add(key)
        deduped_census.append(row)
merged = kept + deduped_census
with open(out_csv, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    w.writerows(merged)

print("MERGED census rows:", len(census_rows), "total rows now:", len(merged))

print(json.dumps(compact, indent=1))
print("TOP20_IN_HALF:", json.dumps([{e["file"]: [e["devices_all"], e["devices_in_half"]]} for e in top20_in_half]))
print("TOP20_OUT_HALF:", json.dumps(summary["top20_leverage_out_half"]))
print("FAM:", json.dumps(summary["family_breakdown"]))
print("SHARED15:", json.dumps(summary["shared_blob_top15_in_half"]))
print("TOP15DEV:", json.dumps(summary["top15_devices_by_bytes"]))
