import csv
from pathlib import Path

MATRIX = "upstream-contribution/blob-database/coverage-matrix.csv"
INVENTORY = "upstream-contribution/blob-database/device-inventory.csv"
DEVICE_TYPES = "site/data/device-types.csv"
UPSTREAM_COUNTS = "site/data/upstream-counts.csv"
LINKS = "site/data/links.csv"


def _read(repo, rel):
    with (repo / rel).open(newline="", encoding="utf-8", errors="surrogateescape") as f:
        return list(csv.DictReader(f))


def load_matrix(repo):
    return _read(repo, MATRIX)


def load_inventory(repo):
    return _read(repo, INVENTORY)


def load_device_types(repo):
    return {r["model"]: r for r in _read(repo, DEVICE_TYPES)}


def load_upstream_counts(repo):
    out = {}
    for r in _read(repo, UPSTREAM_COUNTS):
        raw = r["count"]
        if not raw.isdigit():
            raise ValueError("invalid count for " + r["model"] + ": " + repr(raw))
        r["count"] = int(raw)
        out[r["model"]] = r
    return out


def load_links(repo):
    return _read(repo, LINKS)


def dedupe_inventory(rows):
    seen = set()
    unique = []
    dropped = []
    for r in rows:
        model = r["model"]
        if model in seen:
            dropped.append(r)
            continue
        seen.add(model)
        unique.append(r)
    return unique, dropped
