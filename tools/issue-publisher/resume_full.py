import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from gh_api import call, REPO

REPO_ROOT = HERE.parents[1]
CAT = REPO_ROOT / 'docs/issue-catalog/full-coverage.jsonl'
STATE = HERE / 'full-published.jsonl'
LOG = HERE / 'full-publish.log'
DELAY = 8.0
MAX_WINDOW = 430

cfg = json.load(open('/home/aditya/.zcode/cli/config.json'))
TOK = cfg['mcp']['servers']['github-adineo-cmd']['headers']['Authorization'].split(' ', 1)[1]
HEADERS = {'Authorization': 'Bearer ' + TOK, 'User-Agent': 'p', 'Accept': 'application/vnd.github+json'}


def log(msg):
    LOG.open('a', encoding='utf-8').write(
        datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ') + ' ' + msg + '\n')


def existing_titles():
    titles = set()
    for state in ('open', 'closed'):
        p = 1
        while True:
            req = urllib.request.Request(f'https://api.github.com/repos/{REPO}/issues?state={state}&per_page=100&page={p}', headers=HEADERS)
            data = json.load(urllib.request.urlopen(req, timeout=20))
            if not data: break
            titles.update(i.get('title', '') for i in data)
            if len(data) < 100: break
            p += 1
    return titles


def main():
    pkgs = [json.loads(l) for l in CAT.read_text(encoding='utf-8').splitlines()]
    have = existing_titles()
    todo = [p for p in pkgs if p['title'] not in have]
    log(f'START catalog={len(pkgs)} already_on_github={len(pkgs)-len(todo)} todo={len(todo)}')
    STATE.parent.mkdir(parents=True, exist_ok=True)
    made = 0
    window = time.time()
    with STATE.open('a', encoding='utf-8') as f:
        for p in todo:
            if made >= MAX_WINDOW or time.time() - window >= 3500:
                log(f'WINDOW END made={made} - sleeping 120s')
                time.sleep(120); made = 0; window = time.time()
            st, r = call('POST', f'/repos/{REPO}/issues',
                         {'title': p['title'], 'body': p['body'], 'labels': p['labels']})
            if st == 201:
                f.write(json.dumps({'key': p['key'], 'number': r['number'], 'title': p['title']}) + '\n'); f.flush()
                made += 1
                log(f"#{r['number']} {p['title'][:64]}")
            elif st in (403, 429) and 'rate limit' in str(r).lower():
                log('BLOCKED - sleeping 300s'); time.sleep(300)
            else:
                log(f'FAIL {st} {str(r)[:100]} - retry 30s'); time.sleep(30)
            time.sleep(DELAY)
    log('COMPLETE')


if __name__ == '__main__':
    main()
