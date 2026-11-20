import fs from 'node:fs';

const REPO = 'adineo-cmd/open-device';
const START_HERE = 379;
const LEASE_MS = 4 * 60 * 60 * 1000;
const SHARD_OF_SLOT = { 'OC-1': 0, 'OC-2': 1, 'OC-3': 2, 'OC-4': 3, 'ZC-1': 4, 'ZC-2': 5 };

const cfg = JSON.parse(fs.readFileSync(process.env.HOME + '/.zcode/cli/config.json', 'utf8'));
const token = cfg.mcp.servers['github-adineo-cmd'].headers.Authorization.split(' ')[1];

async function api(path) {
  const r = await fetch('https://api.github.com' + path, {
    headers: { Authorization: 'Bearer ' + token, 'User-Agent': 'open-device', Accept: 'application/vnd.github+json' },
  });
  if (!r.ok) throw new Error(path + ' -> ' + r.status);
  return r.json();
}

async function allPages(path) {
  const out = [];
  for (let page = 1; ; page++) {
    const sep = path.includes('?') ? '&' : '?';
    const batch = await api(`${path}${sep}per_page=100&page=${page}`);
    if (!batch.length) break;
    out.push(...batch);
    if (batch.length < 100) break;
  }
  return out;
}

function shardOwners() {
  const owners = {};
  for (const [slot, shard] of Object.entries(SHARD_OF_SLOT)) owners[shard] = [slot];
  return owners;
}

const startComments = await allPages(`/repos/${REPO}/issues/${START_HERE}/comments`);
const owners = shardOwners();
for (const c of startComments.sort((a, b) => a.created_at.localeCompare(b.created_at))) {
  const m = c.body.match(/SHARD-REASSIGN\s+(\d)\s*->\s*([A-Z0-9,\s-]+)/);
  if (!m) continue;
  const shard = Number(m[1]);
  owners[shard] = m[2].split(',').map((s) => s.trim()).filter(Boolean);
}

const issues = (await allPages(`/repos/${REPO}/issues?state=open`)).filter((i) => !i.pull_request);
const now = Date.now();
let violations = 0;
let stale = 0;
let claims = 0;

for (const issue of issues) {
  const comments = await allPages(`/repos/${REPO}/issues/${issue.number}/comments`);
  const shard = issue.number % 6;
  const allowed = owners[shard] || [];
  const claimComments = comments.filter((c) => /^CLAIM\s+/.test(c.body.trim()));

  for (const c of claimComments) {
    const slot = c.body.trim().split(/\s+/)[1];
    claims++;
    if (!(slot in SHARD_OF_SLOT)) {
      console.log(`VIOLATION #${issue.number}: unknown slot "${slot}"`);
      violations++;
      continue;
    }
    if (!allowed.includes(slot)) {
      console.log(`VIOLATION #${issue.number}: shard ${shard} owned by ${allowed.join(',')}, claimed by ${slot}`);
      violations++;
    }
  }

  if (claimComments.length > 1) {
    console.log(`VIOLATION #${issue.number}: ${claimComments.length} CLAIM comments`);
    for (const c of claimComments) console.log('  ' + c.body.trim().split('\n')[0]);
    violations++;
  }

  if (claimComments.length) {
    const first = claimComments[0];
    const slot = first.body.trim().split(/\s+/)[1];
    const later = comments.filter((c) => c.created_at > first.created_at && c.user.login === first.user.login);
    const last = later.length ? later[later.length - 1].created_at : first.created_at;
    if (now - Date.parse(last) > LEASE_MS) {
      console.log(`STALE #${issue.number}: ${slot} claim idle since ${last}`);
      stale++;
    }
    const done = comments.find((c) => /^DONE\s+/.test(c.body.trim()));
    if (done) {
      const doneSlot = done.body.trim().split(/\s+/)[1];
      if (doneSlot !== slot || done.user.login !== first.user.login) {
        console.log(`VIOLATION #${issue.number}: DONE by ${done.user.login} as ${doneSlot}, claimant ${first.user.login} as ${slot}`);
        violations++;
      }
    }
  }
}

console.log(`checked ${issues.length} open issues, ${claims} claims, ${violations} violations, ${stale} stale leases`);
process.exit(violations ? 1 : 0);
