import fs from 'node:fs';
import path from 'node:path';
import { parseCsv } from './csv';

export const ROOT = process.cwd();

const EXCLUDED_DOCS = new Set([
  'RENAME.md', 'docs/ISSUE-WORKFLOW.md', 'docs/issue-catalog/README.md',
  'docs/issue-catalog/DEVICE-PACKAGES.md', 'docs/EXTERNAL-FIRMWARE-DIRECTORY.md',
]);

const CANONICAL: Record<string, string> = {
  nvidia: 'NVIDIA', oneplus: 'OnePlus', lge: 'LG', lg: 'LG', asus: 'ASUS',
  zte: 'ZTE', fxtec: 'F(x)tec', google: 'Google', motorola: 'Motorola',
  samsung: 'Samsung', sony: 'Sony', xiaomi: 'Xiaomi', realme: 'Realme',
  fairphone: 'Fairphone', nothing: 'Nothing', essential: 'Essential',
  nokia: 'Nokia', shift: 'SHIFT', solana: 'Solana', bananapi: 'Banana Pi',
  radxa: 'Radxa', amlogic: 'Amlogic',
};

function read(rel: string): string {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8');
}

export function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

function vendorDisplay(v: string): string {
  return CANONICAL[v.trim().toLowerCase()] || v.trim();
}

function walk(dir: string, out: string[] = []): string[] {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (e.name === '.git' || e.name === '.superpowers' || e.name === 'site' || e.name === 'node_modules' || e.name === 'dist') continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) walk(p, out);
    else if (e.name.endsWith('.md')) out.push(p);
  }
  return out;
}

export interface Family { family: string; device_count: number; blob_count: number; top_blobs: { filename: string; reach: number }[]; }
export interface Device {
  model: string; vendor: string; vendor_display: string; slug: string;
  type: string; build_variant: string; soc: string;
  families: Record<string, Record<string, string>[]>;
  blob_count: number; total_bytes: number;
  state: 'catalogued' | 'count_known' | 'inventory_only';
  upstream_count: number | null; count_source: string | null;
}
export interface Doc { path: string; url: string; title: string; summary: string; evidence_classes: string[]; }
export interface Link { url: string; title: string; organisation: string; device_types: string; families: string; what_it_hosts: string; licence: string; verified_date: string; }

export function loadMatrix() { return parseCsv(read('upstream-contribution/blob-database/coverage-matrix.csv')); }
export function loadInventory() { return parseCsv(read('upstream-contribution/blob-database/device-inventory.csv')); }
export function loadLinks(): Link[] { return parseCsv(read('site/data/links.csv')) as Link[]; }

export function dedupe(rows: Record<string, string>[]) {
  const seen = new Set<string>(); const unique: Record<string, string>[] = []; const dropped: Record<string, string>[] = [];
  for (const r of rows) {
    if (seen.has(r.model)) { dropped.push(r); continue; }
    seen.add(r.model); unique.push(r);
  }
  return { unique, dropped };
}

export function buildDevices(): Device[] {
  const matrix = loadMatrix();
  const { unique } = dedupe(loadInventory());
  const types = new Map(parseCsv(read('site/data/device-types.csv')).map((r) => [r.model, r]));
  const counts = new Map(parseCsv(read('site/data/upstream-counts.csv')).map((r) => [r.model, r]));
  const byDev = new Map<string, Record<string, string>[]>();
  for (const r of matrix) {
    if (!byDev.has(r.device)) byDev.set(r.device, []);
    byDev.get(r.device)!.push(r);
  }
  return unique.map((row) => {
    const model = row.model;
    const rows = byDev.get(model) || [];
    const families: Record<string, Record<string, string>[]> = {};
    let total = 0;
    for (const r of rows) {
      (families[r.blob_family] ||= []).push(r);
      if (/^\d+$/.test(r.size_bytes)) total += parseInt(r.size_bytes, 10);
    }
    const state: Device['state'] = rows.length ? 'catalogued' : counts.has(model) ? 'count_known' : 'inventory_only';
    const t = types.get(model) || {};
    const c = counts.get(model);
    return {
      model, vendor: row.vendor || '', vendor_display: vendorDisplay(row.vendor || ''),
      slug: slugify(model), type: t.type || 'other', build_variant: t.build_variant || 'none',
      soc: row.soc || '', families, blob_count: rows.length, total_bytes: total, state,
      upstream_count: c ? parseInt(c.count, 10) : null, count_source: c ? c.source : null,
    };
  });
}

export function buildFamilies(devices: Device[]): Family[] {
  const by = new Map<string, { devices: number; rows: number; files: Map<string, number> }>();
  for (const d of devices) {
    for (const [fam, rows] of Object.entries(d.families)) {
      const e = by.get(fam) || { devices: 0, rows: 0, files: new Map() };
      e.devices++; e.rows += rows.length;
      for (const r of rows) e.files.set(r.filename, (e.files.get(r.filename) || 0) + 1);
      by.set(fam, e);
    }
  }
  return [...by.entries()].map(([family, e]) => ({
    family, device_count: e.devices, blob_count: e.rows,
    top_blobs: [...e.files.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 3).map(([filename, reach]) => ({ filename, reach })),
  })).sort((a, b) => b.device_count - a.device_count || a.family.localeCompare(b.family));
}

function truncate(s: string, n = 300): string {
  if (s.length <= n) return s;
  const cut = s.slice(0, n);
  const i = cut.lastIndexOf(' ');
  return (i > 0 ? cut.slice(0, i) : cut).replace(/\s+$/, '') + '…';
}

export function buildDocs(): Doc[] {
  const files = walk(ROOT).map((p) => path.relative(ROOT, p).split(path.sep).join('/')).filter((p) => !EXCLUDED_DOCS.has(p)).sort();
  return files.map((rel) => {
    const text = read(rel);
    const lines = text.replace(/\r\n/g, '\n').split('\n');
    let title = ''; let summary = '';
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].startsWith('# ')) {
        title = lines[i].slice(2).trim();
        summary = truncate(lines.slice(i + 1).find((x) => x.trim())?.trim() || '');
        break;
      }
    }
    const classes = [...new Set(text.match(/\[[FIHN]\]/g) || [])].map((s) => s[1]).sort();
    return { path: rel, url: rel.replace(/\.md$/, '.html'), title, summary, evidence_classes: classes };
  });
}
