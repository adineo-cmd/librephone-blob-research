import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

INPUTS = (
    "upstream-contribution/blob-database/coverage-matrix.csv",
    "upstream-contribution/blob-database/device-inventory.csv",
    "site/data/device-types.csv",
    "site/data/upstream-counts.csv",
    "site/data/links.csv",
)


def main(argv):
    if "--check" in argv:
        missing = [rel for rel in INPUTS if not (REPO / rel).is_file()]
        for rel in missing:
            print("missing: " + rel)
        if missing:
            return 1
        print("check ok")
        return 0
    raise NotImplementedError("full build lands in task 9")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
