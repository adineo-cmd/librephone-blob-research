import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from lib import loader

REPO = Path(__file__).resolve().parents[2]


class LoaderTest(unittest.TestCase):
    def test_matrix_row_count(self):
        rows = loader.load_matrix(REPO)
        self.assertEqual(len(rows), 33917)
        self.assertEqual(len({r["device"] for r in rows}), 123)

    def test_matrix_columns_present(self):
        row = loader.load_matrix(REPO)[0]
        for col in ("device", "vendor", "soc", "blob_family", "filename",
                    "size_bytes", "md5_db", "db_path"):
            self.assertIn(col, row)

    def test_inventory_dedupe_reports_four_duplicate_rows(self):
        rows = loader.load_inventory(REPO)
        self.assertEqual(len(rows), 249)
        unique, dropped = loader.dedupe_inventory(rows)
        self.assertEqual(len(unique), 245)
        self.assertEqual(len(dropped), 4)
        self.assertEqual({r["model"] for r in dropped},
                         {"Phone_2", "TX2_Tablet", "Xperia_1_II", "Redmi_Note_10_Pro"})

    def test_device_types_cover_all_distinct_models(self):
        unique, _ = loader.dedupe_inventory(loader.load_inventory(REPO))
        types = loader.load_device_types(REPO)
        self.assertEqual({r["model"] for r in unique} - set(types), set())

    def test_upstream_counts_absent_for_m5_tv(self):
        counts = loader.load_upstream_counts(REPO)
        self.assertNotIn("M5_TV", counts)
        self.assertEqual(counts["Jetson_TV"]["count"], 35)
        self.assertIsInstance(counts["Jetson_TV"]["count"], int)

    def test_inventory_encoding_survives_surrogates(self):
        rows = loader.load_inventory(REPO)
        self.assertTrue(all(isinstance(r["model"], str) for r in rows))


if __name__ == "__main__":
    unittest.main()
