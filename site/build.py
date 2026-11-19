import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

INPUTS = (
    "upstream-contribution/blob-database/coverage-matrix.csv",
    "upstream-contribution/blob-database/device-inventory.csv",
    "site/data/device-types.csv",
    "site/data/links.csv",
)


def main(argv):
    if "--check" in argv:
        for rel in INPUTS:
            if not (REPO / rel).is_file():
                print("missing: " + rel)
                return 1
        print("check ok")
        return 0
    raise NotImplementedError("full build lands in task 9")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
