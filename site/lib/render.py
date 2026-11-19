import html
from collections import defaultdict
from pathlib import Path

EXPECTED_DOCS = 141
EXPECTED_DEVICES = 245
EXPECTED_FAMILIES = 9
EXPECTED_TYPES = 5
EXPECTED_STATIC = 7
EXPECTED_TOTAL = 407

NAV = [
    ("index.html", "Home"),
    ("devices/index.html", "Devices"),
    ("families/index.html", "Families"),
    ("research/index.html", "Research"),
    ("links/index.html", "External code"),
    ("methodology/index.html", "Methodology"),
    ("build-report.html", "Build report"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def page(title, body, root):
    prefix = (root + "/") if root else ""
    links = "\n".join('    <a href="%s%s">%s</a>' % (prefix, href, label)
                      for href, label in NAV)
    return (
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <title>%s — Open Device</title>\n"
        "  <link rel=\"stylesheet\" href=\"%sassets/site.css\">\n"
        "</head>\n"
        "<body>\n"
        "<header><h1>Open Device</h1>\n<nav>\n%s\n</nav></header>\n"
        "<main>\n%s\n</main>\n"
        "<footer>Facts, not blobs. Every claim carries its evidence class.</footer>\n"
        "</body>\n"
        "</html>\n"
    ) % (esc(title), prefix, links, body)


def _gap(device):
    state = device["state"]
    if state == "catalogued":
        return ""
    if state == "count_known":
        return (
            '<div class="gap"><h2>Coverage gap</h2><p>%d blobs are known to exist '
            'upstream for this device; 0 are catalogued with filenames and hashes. '
            'Source: %s.</p></div>'
        ) % (device["upstream_count"], esc(device["count_source"]))
    return (
        '<div class="gap"><h2>Coverage gap</h2><p>This device is listed in the '
        'upstream inventory, but no blob count and no blob rows are recorded for it.</p></div>'
    )


def device_page(device, root):
    prefix = (root + "/") if root else ""
    fam_rows = []
    leverage = []
    for fam, rows in sorted(device["families"].items()):
        md5s = {r.get("md5_db", "") for r in rows}
        byts = sum(int(r["size_bytes"]) for r in rows if r.get("size_bytes", "").isdigit())
        fam_rows.append(
            '<tr class="blob-row"><td><a href="%sfamilies/%s.html">%s</a></td>'
            '<td>%d</td><td>%d</td><td>%d</td></tr>'
            % (prefix, esc(fam), esc(fam), len(rows), len(md5s), byts)
        )
        for r in rows:
            leverage.append((r.get("filename", ""), fam, r.get("size_bytes", "")))
    top = sorted(leverage, key=lambda x: -int(x[2]) if x[2].isdigit() else 0)[:3]
    lev_html = "\n".join(
        '<li><a href="%sfamilies/%s.html">%s</a> (%s bytes)</li>'
        % (prefix, esc(f), esc(n), esc(b or "unknown"))
        for n, f, b in top
    )
    meta = (
        "<ul><li>Vendor: %s</li><li>Type: %s</li><li>Build variant: %s</li><li>SoC: %s</li></ul>"
        % (esc(device["vendor_display"]), esc(device["type"]),
           esc(device["build_variant"]), esc(device["soc"] or "not recorded"))
    )
    body = (
        "<h1>%s</h1>\n%s\n%s\n"
        "<h2>Families</h2>\n"
        "<p>Counts below are matrix rows, not distinct blobs.</p>\n"
        "<table><tr><th>Family</th><th>Matrix rows</th><th>Distinct md5</th><th>Bytes</th></tr>\n%s\n</table>\n"
        "<h2>Leverage</h2>\n<ul>%s</ul>\n"
    ) % (esc(device["model"]), meta, _gap(device), "\n".join(fam_rows), lev_html)
    return page(device["model"], body, root)


def family_page(family, devices, root):
    prefix = (root + "/") if root else ""
    rows = []
    for d in devices:
        if family["family"] in d["families"]:
            cnt = len(d["families"][family["family"]])
            rows.append('<tr><td><a href="%sdevices/%s.html">%s</a></td><td>%d</td></tr>'
                        % (prefix, esc(d["slug"]), esc(d["model"]), cnt))
    top = "\n".join('<li>%s — %d devices</li>' % (esc(b["filename"]), b["reach"])
                    for b in family["top_blobs"])
    body = (
        "<h1>%s family</h1><p>%d devices, %d matrix rows.</p>"
        "<h2>Top blobs by device reach</h2><ul>%s</ul>"
        "<h2>Devices</h2><table><tr><th>Device</th><th>Rows</th></tr>%s</table>"
    ) % (esc(family["family"]), family["device_count"], family["blob_count"], top, "\n".join(rows))
    return page(family["family"] + " family", body, root)


def type_page(kind, devices, root):
    prefix = (root + "/") if root else ""
    rows = "\n".join('<tr><td><a href="%sdevices/%s.html">%s</a></td><td>%s</td><td>%s</td></tr>'
                     % (prefix, esc(d["slug"]), esc(d["model"]), esc(d["state"]), esc(d["vendor_display"]))
                     for d in devices)
    body = "<h1>%s devices</h1><p>%d devices.</p><table><tr><th>Device</th><th>State</th><th>Vendor</th></tr>%s</table>" % (
        esc(kind), len(devices), rows)
    return page(kind + " devices", body, root)


def index_page(devices, families, docs, root):
    states = defaultdict(int)
    for d in devices:
        states[d["state"]] += 1
    types = defaultdict(int)
    for d in devices:
        types[d["type"]] += 1
    body = (
        "<h1>Open Device</h1><p>Open-source firmware and blobs for every device class.</p>"
        "<h2>Coverage</h2><ul>"
        "<li>%d catalogued</li><li>%d count-known</li><li>%d inventory-only</li></ul>"
        "<h2>Device types</h2><ul>%s</ul>"
        "<h2>Firmware families</h2><ul>%s</ul>"
        "<h2>Research documents</h2><p>%d evidence-classed documents.</p>"
    ) % (
        states["catalogued"], states["count_known"], states["inventory_only"],
        "\n".join("<li>%s: %d</li>" % (esc(k), v) for k, v in sorted(types.items())),
        "\n".join('<li><a href="families/%s.html">%s</a>: %d devices</li>'
                  % (esc(f["family"]), esc(f["family"]), f["device_count"]) for f in families),
        len(docs),
    )
    return page("Home", body, root)


def doc_page(doc, body_html, root):
    prefix = (root + "/") if root else ""
    ev = " ".join('<span class="evidence" data-evidence="%s">%s</span>'
                  % (c.lower(), c) for c in doc["evidence_classes"])
    body = "<h1>%s</h1><p>%s</p><p>Evidence: %s</p>\n%s" % (
        esc(doc["title"]), esc(doc["summary"]), ev or "none", body_html)
    return page(doc["title"] or doc["path"], body, root)


def links_page(links, root):
    byfam = defaultdict(list)
    for l in links:
        for fam in l["families"].split(","):
            if fam.strip():
                byfam[fam.strip()].append(l)
    parts = ["<h1>External code and firmware</h1>",
             "<p>Sites that host open-source firmware, blobs and code. None of this content is re-published here.</p>"]
    for fam in sorted(byfam):
        parts.append("<h2>%s</h2><ul>" % esc(fam))
        for l in byfam[fam]:
            parts.append('<li><a href="%s">%s</a> — %s. %s. Verified %s.</li>' % (
                esc(l["url"]), esc(l["title"]), esc(l["organisation"]),
                esc(l["what_it_hosts"]), esc(l["verified_date"])))
        parts.append("</ul>")
    return page("External code", "\n".join(parts), root)


def methodology_page(root):
    body = (
        "<h1>Methodology</h1>"
        "<h2>Evidence classes</h2><p>Every claim carries [F] fact, [I] inference, "
        "[H] hypothesis or [N] negative, rendered as an inline marker.</p>"
        "<h2>Facts, not blobs</h2><p>No proprietary payload is ever committed. "
        "Only hashes, sizes, offsets, counts and short hex samples.</p>"
        "<h2>Coverage states</h2><p>Catalogued: per-file rows exist. Count-known: an "
        "upstream count exists but no per-file layer. Inventory-only: neither.</p>"
        "<h2>Leverage</h2><p>Ranked by device reach, not row count.</p>"
    )
    return page("Methodology", body, root)


def report_page(report, root):
    def block(title, items):
        if not items:
            return "<h2>%s</h2><p>none</p>" % title
        return "<h2>%s</h2><ul>%s</ul>" % (
            title, "\n".join("<li>%s</li>" % esc(x) for x in items))
    body = "\n".join([
        "<h1>Build report</h1>",
        block("Unclassified devices", report.get("unclassified", [])),
        block("Broken links", report.get("broken_links", [])),
        block("Duplicate inventory rows", report.get("duplicates", [])),
        block("Count-known devices", report.get("count_known", [])),
        block("Inventory-only devices", report.get("inventory_only", [])),
    ])
    return page("Build report", body, root)
