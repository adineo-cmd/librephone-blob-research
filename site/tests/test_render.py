import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from lib import model, render

REPO = Path(__file__).resolve().parents[2]


class PageShellTest(unittest.TestCase):
    def test_every_page_is_valid_shell(self):
        h = render.page("T", "<p>b</p>", "..")
        self.assertTrue(h.startswith("<!DOCTYPE html>"))
        self.assertIn("<title>T — Open Device</title>", h)
        self.assertIn('href="../index.html"', h)
        self.assertIn('href="../assets/site.css"', h)
        self.assertIn("build-report.html", h)

    def test_root_page_uses_bare_asset_path(self):
        h = render.page("T", "", "")
        self.assertIn('href="assets/site.css"', h)
        self.assertNotIn('href="/assets/site.css"', h)

    def test_escaping_in_title(self):
        h = render.page("A & B <x>", "", ".")
        self.assertIn("A &amp; B &lt;x&gt;", h)
        self.assertNotIn("<x>", h)


class DevicePageTest(unittest.TestCase):
    def setUp(self):
        self.by = {d["model"]: d for d in model.build_devices(REPO)}

    def test_catalogued_device_shows_counts(self):
        h = render.device_page(self.by["OnePlus_8"], "..")
        self.assertIn("matrix rows", h)
        self.assertNotIn('class="gap"', h)

    def test_count_known_device_shows_gap_with_number(self):
        h = render.device_page(self.by["Jetson_TV"], "..")
        self.assertIn('class="gap"', h)
        self.assertIn("35", h)
        self.assertIn("known to exist upstream", h)

    def test_inventory_only_states_no_count(self):
        h = render.device_page(self.by["M5_TV"], "..")
        self.assertIn('class="gap"', h)
        self.assertIn("no blob count", h)

    def test_device_page_never_claims_blobs_it_lacks(self):
        h = render.device_page(self.by["Shield_TV_2019"], "..")
        self.assertIn("0", h)
        self.assertEqual(h.count("blob-row"), 0)


class ReportPageTest(unittest.TestCase):
    def test_lists_unclassified(self):
        h = render.report_page({"unclassified": ["Foo_9"], "broken_links": [],
                                "duplicates": [], "count_known": [], "inventory_only": []}, ".")
        self.assertIn("Foo_9", h)


if __name__ == "__main__":
    unittest.main()
