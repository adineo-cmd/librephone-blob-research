import re
from collections import defaultdict
from pathlib import Path

from lib import loader, paths

CANONICAL_VENDORS = {
    "nvidia": "NVIDIA",
    "oneplus": "OnePlus",
    "lge": "LG",
    "lg": "LG",
    "asus": "ASUS",
    "zte": "ZTE",
    "fxtec": "F(x)tec",
    "google": "Google",
    "motorola": "Motorola",
    "samsung": "Samsung",
    "sony": "Sony",
    "xiaomi": "Xiaomi",
    "realme": "Realme",
    "fairphone": "Fairphone",
    "nothing": "Nothing",
    "essential": "Essential",
    "nokia": "Nokia",
    "shift": "SHIFT",
    "solana": "Solana",
    "bananapi": "Banana Pi",
    "radxa": "Radxa",
    "amlogic": "Amlogic",
}

EXCLUDED_DOCS = {
    "RENAME.md",
    "docs/ISSUE-WORKFLOW.md",
    "docs/issue-catalog/README.md",
    "docs/issue-catalog/DEVICE-PACKAGES.md",
    "docs/EXTERNAL-FIRMWARE-DIRECTORY.md",
}


def _vendor_display(vendor):
    key = vendor.strip().lower()
    return CANONICAL_VENDORS.get(key, vendor.strip())


def build_devices(repo):
    matrix = loader.load_matrix(repo)
    unique, _ = loader.dedupe_inventory(loader.load_inventory(repo))
    types = loader.load_device_types(repo)
    counts = loader.load_upstream_counts(repo)

    matrix_by_dev = defaultdict(list)
    for r in matrix:
        matrix_by_dev[r["device"]].append(r)

    devices = []
    for row in unique:
        model = row["model"]
        rows = matrix_by_dev.get(model, [])
        blob_count = len(rows)
        total_bytes = 0
        for r in rows:
            raw = r.get("size_bytes", "")
            if raw.isdigit():
                total_bytes += int(raw)
        families = defaultdict(list)
        for r in rows:
            families[r["blob_family"]].append(r)

        if blob_count > 0:
            state = "catalogued"
        elif model in counts:
            state = "count_known"
        else:
            state = "inventory_only"

        upstream_count = counts[model]["count"] if model in counts else None
        count_source = counts[model]["source"] if model in counts else None
        t = types.get(model, {})
        devices.append({
            "model": model,
            "vendor": row.get("vendor", ""),
            "vendor_display": _vendor_display(row.get("vendor", "")),
            "slug": paths.slugify(model),
            "type": t.get("type", "other"),
            "build_variant": t.get("build_variant", "none"),
            "soc": row.get("soc", ""),
            "families": dict(families),
            "blob_count": blob_count,
            "total_bytes": total_bytes,
            "state": state,
            "upstream_count": upstream_count,
            "count_source": count_source,
        })
    return devices


def build_families(devices):
    byfam = defaultdict(lambda: {"device_count": 0, "blob_count": 0, "files": defaultdict(int)})
    for d in devices:
        for fam, rows in d["families"].items():
            entry = byfam[fam]
            entry["device_count"] += 1
            entry["blob_count"] += len(rows)
            for r in rows:
                entry["files"][r["filename"]] += 1
    out = []
    for fam, entry in byfam.items():
        top = sorted(entry["files"].items(), key=lambda x: (-x[1], x[0]))[:3]
        out.append({
            "family": fam,
            "device_count": entry["device_count"],
            "blob_count": entry["blob_count"],
            "top_blobs": [{"filename": f, "reach": n} for f, n in top],
        })
    out.sort(key=lambda f: (-f["device_count"], f["family"]))
    return out


def _truncate(text, limit=300):
    if len(text) <= limit:
        return text
    cut = text[:limit]
    if " " in cut:
        cut = cut[:cut.rfind(" ")]
    return cut.rstrip() + "…"


def build_documents(repo):
    docs = []
    for p in sorted(repo.rglob("*.md")):
        if ".git" in p.parts or ".superpowers" in p.parts or p.parts[0] == "site":
            continue
        rel = p.relative_to(repo).as_posix()
        if rel in EXCLUDED_DOCS:
            continue
        text = p.read_text(encoding="utf-8", errors="surrogateescape")
        lines = text.replace("\r\n", "\n").split("\n")
        title = ""
        summary = ""
        for i, line in enumerate(lines):
            if line.startswith("# "):
                title = line[2:].strip()
                for nxt in lines[i + 1:]:
                    if nxt.strip():
                        summary = _truncate(nxt.strip())
                        break
                break
        classes = sorted(set(re.findall(r"\[([FIHN])\]", text)))
        docs.append({
            "path": rel,
            "url": paths.doc_output_path(repo, p).as_posix(),
            "title": title,
            "summary": summary,
            "evidence_classes": classes,
        })
    return docs
