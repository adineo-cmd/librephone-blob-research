import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "site" / "data" / "device-types.csv"
INV = REPO / "upstream-contribution" / "blob-database" / "device-inventory.csv"
TYPES = {"phone", "tablet", "tv_box", "sbc", "devkit", "other"}
VARIANTS = {"mobile", "atv", "none"}


class DeviceTypesTest(unittest.TestCase):
    def rows(self):
        with DATA.open(newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def test_every_distinct_model_is_classified(self):
        with INV.open(newline="", encoding="utf-8", errors="surrogateescape") as f:
            models = {r["model"] for r in csv.DictReader(f)}
        classified = {r["model"] for r in self.rows()}
        self.assertEqual(models - classified, set(), "unclassified models")
        self.assertEqual(classified - models, set(), "unknown models")

    def test_no_duplicate_models(self):
        models = [r["model"] for r in self.rows()]
        self.assertEqual(len(models), len(set(models)))

    def test_vocabularies(self):
        for r in self.rows():
            self.assertIn(r["type"], TYPES, r["model"])
            self.assertIn(r["build_variant"], VARIANTS, r["model"])

    def test_atv_set_is_exactly_seven(self):
        atv = {r["model"] for r in self.rows() if r["build_variant"] == "atv"}
        self.assertEqual(atv, {
            "Shield_TV_2019", "M5_TV", "TX1_TV", "TX2_TV",
            "Jetson_TV", "Zero_TV", "Zero_2_TV",
        })

    def test_non_phone_types(self):
        by_type = {}
        for r in self.rows():
            by_type.setdefault(r["type"], set()).add(r["model"])
        self.assertEqual(by_type.get("tv_box"), {"Shield_TV_2019"})
        self.assertEqual(by_type.get("sbc", set()), {"M5_TV", "Zero_TV", "Zero_2_TV"})
        self.assertEqual(by_type.get("devkit", set()),
                         {"TX1_TV", "TX2_TV", "Jetson_TV", "ADT_3"})
        self.assertEqual(len(by_type.get("tablet", set())), 21)
        self.assertEqual(len(by_type.get("phone", set())), 216)
        total = sum(len(v) for v in by_type.values())
        self.assertEqual(total, 245)


if __name__ == "__main__":
    unittest.main()
