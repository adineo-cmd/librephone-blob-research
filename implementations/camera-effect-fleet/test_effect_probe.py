#!/usr/bin/env python3
import csv
import hashlib
import os
import struct
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import effect_probe
import make_fixture

FIXTURES = os.path.join(HERE, "fixtures")
DB = os.path.join(HERE, "..", "..", "research", "laptop", "sharing-clusters.csv")


def fx(name):
    return os.path.join(FIXTURES, name)


class TestHeader(unittest.TestCase):
    def test_header_shape(self):
        r = effect_probe.inspect(fx("opaque_mask.bin"))
        h = r["header"]
        self.assertEqual(h["width"], 16)
        self.assertEqual(h["height"], 12)
        self.assertEqual(h["bytes_per_pixel"], 4)
        self.assertEqual(h["planes"], 1)
        self.assertEqual(h["magic"], 99)
        self.assertTrue(r["header_canonical"])

    def test_size_arithmetic_exact(self):
        for name in ("opaque_mask.bin", "color_lut.bin", "low_alpha.bin", "wide.bin", "tall.bin"):
            r = effect_probe.inspect(fx(name))
            h = r["header"]
            self.assertTrue(r["size_match"], name)
            self.assertEqual(r["slack"], 0, name)
            self.assertEqual(r["bytes"], 28 + h["width"] * h["height"] * 4)

    def test_pixel_classes(self):
        self.assertEqual(effect_probe.inspect(fx("opaque_mask.bin"))["pixel_class"], "grayscale-mask")
        self.assertEqual(effect_probe.inspect(fx("color_lut.bin"))["pixel_class"], "color-texture")
        self.assertEqual(effect_probe.inspect(fx("low_alpha.bin"))["pixel_class"], "color-texture")

    def test_identity_detection(self):
        r = effect_probe.inspect(fx("opaque_mask.bin"))
        self.assertEqual(r["identity_pct"]["ch0_eq_ch1"], 100.0)
        self.assertEqual(r["identity_pct"]["ch1_eq_ch2"], 100.0)


class TestMalformed(unittest.TestCase):
    def test_truncated_header(self):
        with self.assertRaises(ValueError):
            effect_probe.inspect(fx("malformed/truncated_header.bin"))

    def test_size_mismatch(self):
        r = effect_probe.inspect(fx("malformed/size_mismatch.bin"))
        self.assertFalse(r["size_match"])
        self.assertFalse(r["valid"])

    def test_wrong_magic(self):
        r = effect_probe.inspect(fx("malformed/wrong_magic.bin"))
        self.assertFalse(r["header_canonical"])
        self.assertFalse(r["valid"])

    def test_wrong_bpp(self):
        r = effect_probe.inspect(fx("malformed/wrong_bpp.bin"))
        self.assertFalse(r["header_canonical"])


class TestDeterminism(unittest.TestCase):
    def test_regeneration_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_fixture.write_all(tmp)
            for root, _dirs, files in os.walk(FIXTURES):
                for f in files:
                    if f == ".gitignore":
                        continue
                    p = os.path.join(root, f)
                    rel = os.path.relpath(p, FIXTURES)
                    other = os.path.join(tmp, "fixtures", rel)
                    self.assertTrue(os.path.isfile(other), rel)
                    self.assertEqual(
                        hashlib.sha256(open(p, "rb").read()).digest(),
                        hashlib.sha256(open(other, "rb").read()).digest(),
                        rel,
                    )

    def test_no_fixture_is_byte_identical_to_a_vendor_blob(self):
        if not os.path.isfile(DB):
            self.skipTest("sharing-clusters.csv not present")
        known = set()
        with open(DB, newline="") as fh:
            for row in csv.DictReader(fh):
                known.add(row["md5"])
        collisions = []
        for root, _dirs, files in os.walk(FIXTURES):
            for f in files:
                p = os.path.join(root, f)
                raw = open(p, "rb").read()
                if raw and hashlib.md5(raw).hexdigest() in known:
                    collisions.append(os.path.relpath(p, FIXTURES))
        self.assertEqual(collisions, [])


class TestCLI(unittest.TestCase):
    def test_brief_and_json(self):
        import subprocess
        p = subprocess.run(
            [sys.executable, "-I", os.path.join(HERE, "effect_probe.py"), fx("opaque_mask.bin"), "--brief"],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 0)
        self.assertIn("opaque_mask.bin", p.stdout)
        p = subprocess.run(
            [sys.executable, "-I", os.path.join(HERE, "effect_probe.py"), fx("opaque_mask.bin")],
            capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, 0)
        self.assertIn('"size_match": true', p.stdout)


if __name__ == "__main__":
    unittest.main()
