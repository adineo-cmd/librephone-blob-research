import csv
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
COUNTS = REPO / "site" / "data" / "upstream-counts.csv"
LINKS = REPO / "site" / "data" / "links.csv"
INV = REPO / "upstream-contribution" / "blob-database" / "device-inventory.csv"
MATRIX = REPO / "upstream-contribution" / "blob-database" / "coverage-matrix.csv"


class DataFilesTest(unittest.TestCase):
    def test_counts_cover_every_uncatalogued_device_that_has_one(self):
        with COUNTS.open(newline="", encoding="utf-8") as f:
            rows = {r["model"]: r for r in csv.DictReader(f)}
        self.assertEqual(len(rows), 104)
        self.assertEqual(rows["Jetson_TV"]["count"], "35")
        self.assertEqual(rows["TX1_TV"]["count"], "33")
        self.assertEqual(rows["Shield_TV_2019"]["count"], "33")
        self.assertEqual(rows["TX2_TV"]["count"], "22")
        self.assertEqual(rows["Zero_TV"]["count"], "22")
        self.assertEqual(rows["Zero_2_TV"]["count"], "22")
        self.assertEqual(rows["ADT_3"]["count"], "8")
        self.assertNotIn("M5_TV", rows)
        self.assertNotIn("M5_Tablet", rows)

    def test_counted_devices_are_uncatalogued_inventory_models(self):
        with COUNTS.open(newline="", encoding="utf-8") as f:
            counted = {r["model"] for r in csv.DictReader(f)}
        with INV.open(newline="", encoding="utf-8", errors="surrogateescape") as f:
            models = {r["model"] for r in csv.DictReader(f)}
        with MATRIX.open(newline="", encoding="utf-8", errors="surrogateescape") as f:
            catalogued = {r["device"] for r in csv.DictReader(f)}
        self.assertEqual(counted - models, set(), "counted device not in inventory")
        self.assertEqual(counted & catalogued, set(), "catalogued device must not carry a count row")
        self.assertEqual(len(models - catalogued), 122)
        self.assertEqual(len(counted), 104)
        self.assertEqual(len(models - catalogued - counted), 18)

    def test_counts_file_is_hermetic(self):
        text = COUNTS.read_text(encoding="utf-8")
        self.assertNotIn("/home/", text)
        self.assertNotIn("/tmp/", text)

    def test_every_count_cites_a_source(self):
        with COUNTS.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                self.assertTrue(r["source"], r["model"])
                self.assertTrue(r["count"].isdigit(), r["model"])

    def test_links_are_https_and_dated(self):
        with LINKS.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertGreaterEqual(len(rows), 12)
        for r in rows:
            self.assertTrue(r["url"].startswith("https://"), r["url"])
            self.assertRegex(r["verified_date"], r"^\d{4}-\d{2}-\d{2}$")
            self.assertTrue(r["what_it_hosts"], r["url"])
            self.assertTrue(r["device_types"], r["url"])

    def test_no_blob_bytes_field(self):
        with LINKS.open(newline="", encoding="utf-8") as f:
            header = f.readline().strip().split(",")
        self.assertNotIn("payload", header)
        self.assertNotIn("blob_data", header)


if __name__ == "__main__":
    unittest.main()
