import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "site"))

from lib import loader, paths

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "research" / "qualcomm" / "docs" / "interface-bt.md"


class SlugTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(paths.slugify("OnePlus_8_Pro"), "oneplus-8-pro")

    def test_punctuation_and_runs(self):
        self.assertEqual(paths.slugify("Galaxy_TabA_8.0"), "galaxy-taba-8-0")

    def test_no_leading_or_trailing_dash(self):
        self.assertEqual(paths.slugify("__X__"), "x")

    def test_collision_free_across_all_models(self):
        unique, _ = loader.dedupe_inventory(loader.load_inventory(REPO))
        slugs = [paths.slugify(r["model"]) for r in unique]
        self.assertEqual(len(slugs), len(set(slugs)), "slug collision")


class LinkTest(unittest.TestCase):
    def test_relative_md_resolves(self):
        html, bad = paths.rewrite_links(
            '<a href="bt-firmware-census.html">x</a>', DOC, REPO
        )
        self.assertEqual(bad, [])

    def test_missing_target_reported(self):
        html, bad = paths.rewrite_links(
            '<a href="nope-missing.html">x</a>', DOC, REPO
        )
        self.assertEqual(len(bad), 1)
        self.assertIn("nope-missing", bad[0])

    def test_external_link_untouched(self):
        html, bad = paths.rewrite_links(
            '<a href="https://e.example/x">x</a>', REPO / "README.md", REPO
        )
        self.assertEqual(bad, [])
        self.assertIn("https://e.example/x", html)

    def test_doc_output_path_mirrors_source(self):
        got = paths.doc_output_path(
            REPO, REPO / "research" / "qualcomm" / "docs" / "bootchain-census.md"
        )
        self.assertEqual(got.as_posix(), "research/qualcomm/docs/bootchain-census.html")


if __name__ == "__main__":
    unittest.main()
