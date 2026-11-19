import html
import re

ATX_RE = re.compile(r"^(#{1,6})\s+(.*)$")
FENCE_RE = re.compile(r"^```(\w*)\s*$")
TABLE_SEPARATOR_RE = re.compile(r"^:?-+:?$")
LIST_RE = re.compile(r"^(?:[-*+]|\d+\.)\s+(.*)$")
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
EVIDENCE_RE = re.compile(r"\[([FIHN])\](?!\()")


def escape(s):
    return html.escape(s, quote=False)


def split_table_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    out = []
    cur = []
    ticks = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            cur.append("|")
            i += 2
            continue
        if c == "`":
            ticks = not ticks
            cur.append(c)
            i += 1
            continue
        if c == "|" and not ticks:
            out.append("".join(cur).strip())
            cur = []
            i += 1
            continue
        cur.append(c)
        i += 1
    out.append("".join(cur).strip())
    return out


def render_inline(text):
    text = escape(text)
    codes = []

    def stash(m):
        codes.append(m.group(1))
        return "\x00%d\x00" % (len(codes) - 1)

    text = re.sub(r"`([^`]+)`", stash, text)

    def repl_link(m):
        label, target = m.group(1), m.group(2)
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) and not target.startswith(("/", "#")):
            if target.endswith(".md"):
                target = target[:-3] + ".html"
        return '<a href="%s">%s</a>' % (escape(target), label)

    text = LINK_RE.sub(repl_link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)

    def ev(m):
        letter = m.group(1)
        return '<span class="evidence" data-evidence="%s">%s</span>' % (letter.lower(), letter)

    text = EVIDENCE_RE.sub(ev, text)

    def restore(m):
        return "<code>" + codes[int(m.group(1))] + "</code>"

    text = re.sub(r"\x00(\d+)\x00", restore, text)
    return text


def _table(lines, i):
    header = split_table_row(lines[i])
    i += 1
    if i < len(lines) and lines[i].strip().startswith("|"):
        sep = split_table_row(lines[i])
        if sep and all(TABLE_SEPARATOR_RE.match(c) for c in sep):
            aligns = []
            for c in sep:
                if c.startswith(":") and c.endswith(":"):
                    aligns.append("text-align:center")
                elif c.endswith(":"):
                    aligns.append("text-align:right")
                elif c.startswith(":"):
                    aligns.append("text-align:left")
                else:
                    aligns.append("")
            i += 1
        else:
            aligns = ["" for _ in header]
    else:
        aligns = ["" for _ in header]
    out = ["<table>", "<tr>"]
    for idx, c in enumerate(header):
        style = ' style="%s"' % aligns[idx] if idx < len(aligns) and aligns[idx] else ""
        out.append("<th%s>%s</th>" % (style, render_inline(c)))
    out.append("</tr>")
    while i < len(lines) and lines[i].strip().startswith("|"):
        row = split_table_row(lines[i])
        out.append("<tr>")
        for idx, c in enumerate(row):
            style = ' style="%s"' % aligns[idx] if idx < len(aligns) and aligns[idx] else ""
            out.append("<td%s>%s</td>" % (style, render_inline(c)))
        out.append("</tr>")
        i += 1
    out.append("</table>")
    return "\n".join(out), i


def render(text):
    if not text:
        return ""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out = []
    i = 0
    fence = None
    list_kind = None
    while i < len(lines):
        line = lines[i]
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                lang = m.group(1)
                attr = ' class="language-%s"' % lang if lang else ""
                out.append("<pre><code%s>" % attr)
                fence = "open"
                i += 1
                body = []
                while i < len(lines) and not FENCE_RE.match(lines[i]):
                    body.append(escape(lines[i]))
                    i += 1
                out.append("\n".join(body))
                if i < len(lines):
                    i += 1
                out.append("</code></pre>")
                fence = None
                continue
            i += 1
            continue
        if fence is not None:
            i += 1
            continue
        if not line.strip():
            if list_kind:
                out.append("</%s>" % list_kind)
                list_kind = None
            i += 1
            continue
        m = ATX_RE.match(line)
        if m:
            if list_kind:
                out.append("</%s>" % list_kind)
                list_kind = None
            level = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (level, render_inline(m.group(2)), level))
            i += 1
            continue
        if line.lstrip().startswith("|"):
            if list_kind:
                out.append("</%s>" % list_kind)
                list_kind = None
            table, i = _table(lines, i)
            out.append(table)
            continue
        if line.startswith(">"):
            if list_kind:
                out.append("</%s>" % list_kind)
                list_kind = None
            out.append("<blockquote>%s</blockquote>" % render_inline(line.lstrip("> ")))
            i += 1
            continue
        m = LIST_RE.match(line)
        if m:
            kind = "ol" if re.match(r"\d+\.", line) else "ul"
            if list_kind != kind:
                if list_kind:
                    out.append("</%s>" % list_kind)
                out.append("<%s>" % kind)
                list_kind = kind
            out.append("<li>%s</li>" % render_inline(m.group(1)))
            i += 1
            continue
        if list_kind:
            out.append("</%s>" % list_kind)
            list_kind = None
        out.append("<p>%s</p>" % render_inline(line))
        i += 1
    if list_kind:
        out.append("</%s>" % list_kind)
    return "\n".join(out)
