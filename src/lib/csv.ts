export function parseCsv(text: string): Record<string, string>[] {
  const rows: string[][] = [];
  let field = '';
  let row: string[] = [];
  let quoted = false;
  const s = text.replace(/^\uFEFF/, '');
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (quoted) {
      if (c === '"') {
        if (s[i + 1] === '"') { field += '"'; i++; }
        else quoted = false;
      } else field += c;
      continue;
    }
    if (c === '"') { quoted = true; continue; }
    if (c === ',') { row.push(field); field = ''; continue; }
    if (c === '\n') {
      if (field.endsWith('\r')) field = field.slice(0, -1);
      row.push(field);
      if (row.some((x) => x !== '')) rows.push(row);
      row = []; field = ''; continue;
    }
    field += c;
  }
  if (field || row.length) {
    if (field.endsWith('\r')) field = field.slice(0, -1);
    row.push(field);
    if (row.some((x) => x !== '')) rows.push(row);
  }
  if (!rows.length) return [];
  const header = rows[0];
  return rows.slice(1).map((cells) => {
    const o: Record<string, string> = {};
    header.forEach((h, i) => { o[h] = cells[i] ?? ''; });
    return o;
  });
}
