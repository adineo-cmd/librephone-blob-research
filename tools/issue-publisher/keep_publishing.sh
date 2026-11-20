#!/usr/bin/env bash
# Keep the full-coverage publisher alive until all 1,239 issues exist on GitHub.
cd "$(dirname "$0")"
while true; do
  if pgrep -f 'resume_full.py' > /dev/null 2>&1; then
    sleep 60
    continue
  fi
  python3 -I - <<'PY'
import json, urllib.request
cfg=json.load(open('/home/aditya/.zcode/cli/config.json'))
t=cfg['mcp']['servers']['github-adineo-cmd']['headers']['Authorization'].split(' ',1)[1]
h={'Authorization':'Bearer '+t,'User-Agent':'p','Accept':'application/vnd.github+json'}
cat=[json.loads(l)['title'] for l in open('docs/issue-catalog/full-coverage.jsonl')]
titles=set()
for state in ('open','closed'):
    p=1
    while True:
        d=json.load(urllib.request.urlopen(urllib.request.Request(f'https://api.github.com/repos/adineo-cmd/open-device/issues?state={state}&per_page=100&page={p}',headers=h),timeout=20))
        if not d: break
        titles.update(i.get('title','') for i in d)
        if len(d)<100: break
        p+=1
missing=[x for x in cat if x not in titles]
print('present',len(cat)-len(missing),'of',len(cat),'missing',len(missing),flush=True)
if not missing:
    open('./FULL_PUBLISH_DONE','w').write('done')
PY
  if [ -f ./FULL_PUBLISH_DONE ]; then
    echo "ALL 1239 PRESENT - watcher exiting"
    break
  fi
  echo "restarting publisher at $(date -u +%H:%M:%SZ)"
  nohup python3 -u -I resume_full.py >> ./resume.out 2>&1 &
  sleep 60
done
