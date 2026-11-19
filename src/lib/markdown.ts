function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function splitRow(line: string): string[] {
  let s = line.trim();
  if (s.startsWith('|')) s = s.slice(1);
  if (s.endsWith('|') && !s.endsWith('\\|')) s = s.slice(0, -1);
  const out: string[] = []; let cur = ''; let ticks = false;
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (c === '\\' && s[i + 1] === '|') { cur += '|'; i++; continue; }
    if (c === '`') { ticks = !ticks; cur += c; continue; }
    if (c === '|' && !ticks) { out.push(cur.trim()); cur = ''; continue; }
    cur += c;
  }
  out.push(cur.trim());
  return out;
}

export function inline(src: string): string {
  let s = esc(src);
  const codes: string[] = [];
  s = s.replace(/`([^`]+)`/g, (_, c) => { codes.push(c); return `\u0000${codes.length - 1}\u0000`; });
  s = s.replace(/\[([^\]]*)\]\(([^)]+)\)/g, (_, label, target) => {
    let t = target;
    if (!/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(t) && !t.startsWith('#') && t.endsWith('.md')) t = t.slice(0, -3) + '.html';
    return `<a href="${esc(t)}">${label}</a>`;
  });
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>').replace(/\*([^*]+)\*/g, '<em>$1</em>');
  s = s.replace(/\[([FIHN])\](?!\()/g, (_, c) => `<span class="evidence" data-evidence="${c.toLowerCase()}">${c}</span>`);
  s = s.replace(/\u0000(\d+)\u0000/g, (_, i) => `<code>${codes[Number(i)]}</code>`);
  return s;
}

function table(lines: string[], start: number): [string, number] {
  const header = splitRow(lines[start]);
  let i = start + 1;
  let aligns: string[] = header.map(() => '');
  if (i < lines.length && lines[i].trim().startsWith('|')) {
    const sep = splitRow(lines[i]);
    if (sep.length && sep.every((c) => /^:?-+:?$/.test(c))) {
      aligns = sep.map((c) => c.startsWith(':') && c.endsWith(':') ? 'text-align:center'
        : c.endsWith(':') ? 'text-align:right' : c.startsWith(':') ? 'text-align:left' : '');
      i++;
    }
  }
  const out = ['<table>', '<tr>'];
  header.forEach((c, idx) => out.push(`<th${aligns[idx] ? ` style="${aligns[idx]}"` : ''}>${inline(c)}</th>`));
  out.push('</tr>');
  while (i < lines.length && lines[i].trim().startsWith('|')) {
    const row = splitRow(lines[i]);
    out.push('<tr>');
    row.forEach((c, idx) => out.push(`<td${aligns[idx] ? ` style="${aligns[idx]}"` : ''}>${inline(c)}</td>`));
    out.push('</tr>'); i++;
  }
  out.push('</table>');
  return [out.join('\n'), i];
}

export function render(src: string): string {
  if (!src) return '';
  const lines = src.replace(/\r\n/g, '\n').replace(/\r/g, '\n').split('\n');
  const out: string[] = []; let i = 0; let list: string | null = null;
  while (i < lines.length) {
    const line = lines[i];
    const fence = line.match(/^```(\w*)\s*$/);
    if (fence) {
      if (list) { out.push(`</${list}>`); list = null; }
      const lang = fence[1];
      out.push(`<pre><code${lang ? ` class="language-${lang}"` : ''}>`);
      const body: string[] = []; i++;
      while (i < lines.length && !/^```\s*$/.test(lines[i])) { body.push(esc(lines[i])); i++; }
      out.push(body.join('\n'));
      if (i < lines.length) i++;
      out.push('</code></pre>'); continue;
    }
    if (!line.trim()) { if (list) { out.push(`</${list}>`); list = null; } i++; continue; }
    const h = line.match(/^(#{1,6})\s+(.*)$/);
    if (h) {
      if (list) { out.push(`</${list}>`); list = null; }
      const n = h[1].length; out.push(`<h${n}>${inline(h[2])}</h${n}>`); i++; continue;
    }
    if (line.trimStart().startsWith('|')) {
      if (list) { out.push(`</${list}>`); list = null; }
      const [html, next] = table(lines, i); out.push(html); i = next; continue;
    }
    if (line.startsWith('>')) {
      if (list) { out.push(`</${list}>`); list = null; }
      out.push(`<blockquote>${inline(line.replace(/^>\s?/, ''))}</blockquote>`); i++; continue;
    }
    const li = line.match(/^(?:[-*+]|\d+\.)\s+(.*)$/);
    if (li) {
      const kind = /^\d+\./.test(line) ? 'ol' : 'ul';
      if (list !== kind) { if (list) out.push(`</${list}>`); out.push(`<${kind}>`); list = kind; }
      out.push(`<li>${inline(li[1])}</li>`); i++; continue;
    }
    if (list) { out.push(`</${list}>`); list = null; }
    out.push(`<p>${inline(line)}</p>`); i++;
  }
  if (list) out.push(`</${list}>`);
  return out.join('\n');
}
