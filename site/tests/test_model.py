import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from lib import model

REPO = Path(__file__).resolve().parents[2]


class DevicesTest(unittest.TestCase):
    def setUp(self):
        self.devices = model.build_devices(REPO)
        self.by = {d["model"]: d for d in self.devices}

    def test_one_row_per_distinct_model(self):
        self.assertEqual(len(self.devices), 245)
        self.assertEqual(len({d["model"] for d in self.devices}), 245)

    def test_catalogued_device_has_rows_and_bytes(self):
        d = self.by["OnePlus_8"]
        self.assertEqual(d["state"], "catalogued")
        self.assertGreater(d["blob_count"], 0)
        self.assertGreater(d["total_bytes"], 0)

    def test_count_known_device_has_no_rows_but_has_count(self):
        d = self.by["Jetson_TV"]
        self.assertEqual(d["state"], "count_known")
        self.assertEqual(d["blob_count"], 0)
        self.assertEqual(d["upstream_count"], 35)
        self.assertTrue(d["count_source"])

    def test_m5_tv_is_inventory_only(self):
        d = self.by["M5_TV"]
        self.assertEqual(d["state"], "inventory_only")
        self.assertEqual(d["blob_count"], 0)
        self.assertIsNone(d["upstream_count"])

    def test_vendor_case_folded(self):
        displays = {d["vendor_display"] for d in self.devices}
        self.assertIn("NVIDIA", displays)
        self.assertNotIn("Nvidia", displays)
        self.assertNotIn("nvidia", displays)

    def test_tv_box_page_has_zero_blobs(self):
        d = self.by["Shield_TV_2019"]
        self.assertEqual(d["type"], "tv_box")
        self.assertEqual(d["blob_count"], 0)
        self.assertEqual(d["upstream_count"], 33)

    def test_family_partition_sums_to_total(self):
        d = self.by["OnePlus_8"]
        self.assertEqual(sum(len(v) for v in d["families"].values()), d["blob_count"])

    def test_state_distribution(self):
        states = {}
        for d in self.devices:
            states[d["state"]] = states.get(d["state"], 0) + 1
        self.assertEqual(states, {"catalogued": 123, "count_known": 104, "inventory_only": 18})


class FamiliesTest(unittest.TestCase):
    def test_nine_families(self):
        fams = model.build_families(model.build_devices(REPO))
        self.assertEqual(len(fams), 9)
        self.assertEqual({f["family"] for f in fams},
                         {"adsp", "boot", "bt", "cdsp", "gpu", "modem", "other", "tz", "wifi"})

    def test_wifi_is_highest_row_count(self):
        fams = {f["family"]: f for f in model.build_families(model.build_devices(REPO))}
        self.assertEqual(fams["wifi"]["blob_count"], 5642)

    def test_ranking_is_by_device_reach_not_rows(self):
        fams = model.build_families(model.build_devices(REPO))
        self.assertEqual(fams, sorted(fams, key=lambda f: (-f["device_count"], f["family"])))


class DocumentsTest(unittest.TestCase):
    def test_corpus_floor(self):
        self.assertGreaterEqual(len(model.build_documents(REPO)), 187)

    def test_title_from_h1(self):
        docs = {d["path"]: d for d in model.build_documents(REPO)}
        self.assertIn("Boot-chain firmware census",
                      docs["research/qualcomm/docs/bootchain-census.md"]["title"])

    def test_evidence_classes_detected(self):
        docs = {d["path"]: d for d in model.build_documents(REPO)}
        self.assertIn("F", docs["research/fleet/bm2n-isa-bt.md"]["evidence_classes"])

    def test_url_is_under_research(self):
        for d in model.build_documents(REPO):
            self.assertTrue(d["url"].startswith("research/"), d["url"])
            self.assertTrue(d["url"].endswith(".html"), d["url"])


if __name__ == "__main__":
    unittest.main()
