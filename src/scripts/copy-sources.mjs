import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const dist = path.join(root, 'dist');
const filter = (s) => !s.includes('.git') && !s.includes('__pycache__') && !s.includes('node_modules');
for (const base of [dist, path.join(dist, 'research')]) {
  for (const dir of ['implementations', 'tools', 'data']) {
    const src = path.join(root, dir);
    if (!fs.existsSync(src)) continue;
    fs.cpSync(src, path.join(base, dir), { recursive: true, filter });
  }
}
console.log('copied source trees into dist and dist/research');
