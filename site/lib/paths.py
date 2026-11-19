import re
from pathlib import Path

HREF_RE = re.compile(r'href="([^"]+)"')


def slugify(model):
    return re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")


def doc_output_path(repo, md_path):
    rel = md_path.relative_to(repo) if md_path.is_absolute() else md_path
    if rel.parts and rel.parts[0] == "research":
        return rel.with_suffix(".html")
    return Path("research") / rel.with_suffix(".html")


def device_output_path(slug):
    return "devices/" + slug + ".html"


def _resolve(target, source_md, repo):
    base = source_md.parent if source_md.is_absolute() else repo / source_md.parent
    raw = (base / target).resolve()
    try:
        return raw.relative_to(repo.resolve())
    except ValueError:
        return raw


def rewrite_links(html, source_md, repo):
    bad = []

    def repl(m):
        target = m.group(1)
        if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//") or target.startswith("#"):
            return m.group(0)
        clean = target.split("#")[0].split("?")[0]
        if not clean:
            return m.group(0)
        if not clean.endswith(".html"):
            return m.group(0)
        src_md = clean[:-5] + ".md"
        resolved = _resolve(src_md, source_md, repo)
        if not (repo / resolved).exists():
            bad.append(target)
            return m.group(0)
        out = doc_output_path(repo, repo / resolved)
        return 'href="' + out.as_posix() + '"'

    return HREF_RE.sub(repl, html), bad
