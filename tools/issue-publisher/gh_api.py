import json
import time
import urllib.error
import urllib.request

CONFIG = "/home/aditya/.zcode/cli/config.json"
REPO = "adineo-cmd/open-device"
API = "https://api.github.com"


def token(account="github-adineo-cmd"):
    cfg = json.load(open(CONFIG))
    return cfg["mcp"]["servers"][account]["headers"]["Authorization"].split(" ", 1)[1]


def call(method, path, payload=None, account="github-adineo-cmd", retries=4):
    body = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(retries):
        req = urllib.request.Request(
            API + path, data=body, method=method,
            headers={
                "Authorization": "Bearer " + token(account),
                "User-Agent": "open-device-publisher",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, json.load(r)
        except urllib.error.HTTPError as e:
            raw = e.read().decode(errors="replace")
            if e.code in (403, 429) and "rate limit" not in raw.lower() and attempt < retries - 1:
                time.sleep(2 ** (attempt + 1)); continue
            return e.code, {"error": raw[:400]}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** (attempt + 1)); continue
            return 0, {"error": str(e)}
    return 0, {"error": "exhausted"}
