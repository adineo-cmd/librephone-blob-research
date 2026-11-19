import shutil
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "site"))

from lib import loader, markdown, model, paths, render

INPUTS = (
    "upstream-contribution/blob-database/coverage-matrix.csv",
    "upstream-contribution/blob-database/device-inventory.csv",
    "site/data/device-types.csv",
    "site/data/upstream-counts.csv",
    "site/data/links.csv",
)

TYPES = ("phone", "tablet", "tv_box", "sbc", "devkit")
EXCLUDED = {
    "RENAME.md",
    "docs/ISSUE-WORKFLOW.md",
    "docs/issue-catalog/README.md",
    "docs/issue-catalog/DEVICE-PACKAGES.md",
    "docs/EXTERNAL-FIRMWARE-DIRECTORY.md",
}


def check_inputs():
    missing = [rel for rel in INPUTS if not (REPO / rel).is_file()]
    for rel in missing:
        print("missing: " + rel)
    if missing:
        return 1
    print("check ok")
    return 0


def _write(out, rel, text):
    p = out / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def build():
    out = REPO / "site" / "out"
    if out.exists():
        shutil.rmtree(out)
    (out / "assets").mkdir(parents=True)
    shutil.copy2(REPO / "site" / "assets" / "site.css", out / "assets" / "site.css")

    matrix = loader.load_matrix(REPO)
    inventory = loader.load_inventory(REPO)
    unique, duplicates = loader.dedupe_inventory(inventory)
    devices = model.build_devices(REPO)
    families = model.build_families(devices)
    docs = model.build_documents(REPO)
    links = loader.load_links(REPO)

    report = {
        "unclassified": [],
        "broken_links": [],
        "duplicates": [r["model"] for r in duplicates],
        "count_known": [d["model"] for d in devices if d["state"] == "count_known"],
        "inventory_only": [d["model"] for d in devices if d["state"] == "inventory_only"],
    }

    _write(out, "index.html", render.index_page(devices, families, docs, ""))
    _write(out, "devices/index.html", render.page(
        "Devices",
        "<h1>All devices</h1><ul>%s</ul>" % "\n".join(
            '<li><a href="%s.html">%s</a> — %s</li>' % (d["slug"], d["model"], d["state"])
            for d in devices),
        ".."))
    _write(out, "families/index.html", render.page(
        "Families",
        "<h1>Firmware families</h1><ul>%s</ul>" % "\n".join(
            '<li><a href="%s.html">%s</a> — %d devices, %d rows</li>'
            % (f["family"], f["family"], f["device_count"], f["blob_count"])
            for f in families),
        ".."))
    _write(out, "research/index.html", render.page(
        "Research",
        "<h1>Research documents</h1><ul>%s</ul>" % "\n".join(
            '<li><a href="../%s">%s</a></li>' % (d["url"], d["title"] or d["path"])
            for d in docs),
        ".."))
    _write(out, "links/index.html", render.links_page(links, ".."))
    _write(out, "methodology/index.html", render.methodology_page(".."))

    for d in devices:
        _write(out, "devices/%s.html" % d["slug"], render.device_page(d, ".."))

    for f in families:
        _write(out, "families/%s.html" % f["family"], render.family_page(f, devices, ".."))

    for kind in TYPES:
        members = [d for d in devices if d["type"] == kind]
        if not members:
            report["unclassified"].append(kind + " (empty type page)")
            continue
        _write(out, "devices-by-type/%s.html" % kind, render.type_page(kind, members, ".."))

    repo_root = REPO.resolve()
    for d in docs:
        src = REPO / d["path"]
        body_html = markdown.render(src.read_text(encoding="utf-8", errors="surrogateescape"))
        body_html, bad = paths.rewrite_links(body_html, src, repo_root)
        report["broken_links"].extend(bad)
        _write(out, d["url"], render.doc_page(d, body_html, ".."))

    _write(out, "build-report.html", render.report_page(report, ""))

    actual_files = len(list(out.rglob("*.html")))
    counts = {
        "docs": len(docs),
        "devices": len(devices),
        "families": len(families),
        "types": len(TYPES),
        "static": actual_files - len(docs) - len(devices) - len(families) - len(TYPES),
    }
    total = actual_files
    expected = (render.EXPECTED_DOCS, render.EXPECTED_DEVICES,
                render.EXPECTED_FAMILIES, render.EXPECTED_TYPES,
                render.EXPECTED_STATIC, render.EXPECTED_TOTAL)
    actual = (counts["docs"], counts["devices"], counts["families"],
              counts["types"], counts["static"], total)
    if actual != expected:
        print("page count mismatch: expected %s got %s" % (expected, actual))
        return 1

    print("wrote %d pages, %d unresolved links, %d unclassified"
          % (total, len(report["broken_links"]), len(report["unclassified"])))
    if report["unclassified"] or report["broken_links"]:
        return 1
    return 0


def main(argv):
    if "--check" in argv:
        return check_inputs()
    return build()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
