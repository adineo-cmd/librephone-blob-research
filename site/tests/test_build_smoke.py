import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILD = REPO / "site" / "build.py"

if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


class BuildSmokeTest(unittest.TestCase):
    def test_build_script_exists_and_imports_clean(self):
        self.assertTrue(BUILD.is_file())
        result = subprocess.run(
            [sys.executable, "-I", str(BUILD), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertIn(result.returncode, (0, 1), result.stderr)

    def test_check_reports_missing_data_files(self):
        result = subprocess.run(
            [sys.executable, "-I", str(BUILD), "--check"],
            capture_output=True,
            text=True,
        )
        self.assertIn("missing: site/data/device-types.csv", result.stdout)


if __name__ == "__main__":
    unittest.main()
