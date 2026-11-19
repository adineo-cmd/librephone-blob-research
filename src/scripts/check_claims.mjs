import fs from 'node:fs';

const REPO = 'adineo-cmd/open-device';
const cfg = JSON.parse(fs.readFileSync(process.env.HOME + '/.zcode/cli/config.json', 'utf8'));
const token = cfg.mcp.servers['github-adineo-cmd'].headers.Authorization.split(' ')[1];

async function api(path) {
  const r = await fetch('https://api.github.com' + path, {
    headers: { Authorization: 'Bearer ' + token, 'User-Agent': 'open-device', Accept: 'application/vnd.github+json' },
  });
  if (!r.ok) throw new Error(path + ' -> ' + r.status);
  return r.json();
}

let page = 1;
const issues = [];
while (true) {
  const batch = await api(`/repos/${REPO}/issues?state=open&per_page=100&page=${page}`);
  if (!batch.length) break;
  issues.push(...batch.filter((i) => !i.pull_request));
  if (batch.length < 100) break;
  page++;
}

let violations = 0;
for (const issue of issues) {
  const comments = await api(`/repos/${REPO}/issues/${issue.number}/comments?per_page=100`);
  const claims = comments.filter((c) => /^CLAIM\s+/.test(c.body.trim()));
  if (claims.length > 1) {
    console.log(`VIOLATION issue #${issue.number}: ${claims.length} CLAIM comments`);
    claims.forEach((c) => console.log('  ' + c.body.trim().split('\n')[0]));
    violations++;
  }
  if (claims.length) {
    const winner = claims[0].body.trim().split(/\s+/)[1];
    const otherDone = comments.find((c) => c.body.trim().startsWith('DONE ') && c.body.includes(winner) === false && c.user.login !== winner);
    if (otherDone) {
      console.log(`VIOLATION issue #${issue.number}: DONE by ${otherDone.user.login}, claimant ${winner}`);
      violations++;
    }
  }
}
console.log(`checked ${issues.length} open issues, ${violations} violations`);
process.exit(violations ? 1 : 0);
