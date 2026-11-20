#!/usr/bin/env python3
import csv
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cfr_probe
import make_fixture

FIXTURES = os.path.join(HERE, "fixtures")
DB = os.path.join(HERE, "..", "..", "research", "laptop", "sharing-clusters.csv")


def fx(name):
    return os.path.join(FIXTURES, name)


class TestClasses(unittest.TestCase):
    def test_four_classes(self):
        expect = {
            "short.bin": cfr_probe.CLASS_SHORT,
            "mid.bin": cfr_probe.CLASS_MID,
            "tag.bin": cfr_probe.CLASS_TAG,
            "text.bin": cfr_probe.CLASS_TEXT,
        }
        for name, kind in expect.items():
            r = cfr_probe.inspect(fx(name))
            self.assertEqual(r["class"], kind, name)

    def test_sizes(self):
        for name, size in (("short.bin", 1079), ("mid.bin", 2126), ("tag.bin", 3645), ("text.bin", 8128)):
            self.assertEqual(os.path.getsize(fx(name)), size, name)

    def test_short_mid_signature_block_identical(self):
        a = cfr_probe.inspect(fx("short.bin"))
        b = cfr_probe.inspect(fx("mid.bin"))
        self.assertTrue(a["signature_block_ok"])
        self.assertTrue(b["signature_block_ok"])

    def test_mid_record_stride(self):
        r = cfr_probe.inspect(fx("mid.bin"))
        self.assertEqual(r["record_stride"], 670)

    def test_tag_lens_magic(self):
        r = cfr_probe.inspect(fx("tag.bin"))
        self.assertEqual(r["lens_magic"], "L12U")
        self.assertEqual(r["lens_string"], "L12UW")

    def test_text_prologue_and_size_word(self):
        r = cfr_probe.inspect(fx("text.bin"))
        self.assertIn("CFR400 TUNING PARAMETER", r["prologue"])
        self.assertTrue(r["has_size_word"])
        self.assertIn(68, r["size_word_offsets"])


class TestMalformed(unittest.TestCase):
    def test_empty_and_truncated(self):
        for name in ("empty.bin", "truncated.bin"):
            r = cfr_probe.inspect(fx("malformed/" + name))
            self.assertEqual(r["class"], cfr_probe.CLASS_UNKNOWN)

    def test_unknown(self):
        r = cfr_probe.inspect(fx("malformed/unknown.bin"))
        self.assertEqual(r["class"], cfr_probe.CLASS_UNKNOWN)
        self.assertEqual(r["record_tags"], [])


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
        for args, needle in ((["--brief"], "short.bin"), ([], '"class": "short-1079"')):
            p = subprocess.run(
                [sys.executable, "-I", os.path.join(HERE, "cfr_probe.py"), fx("short.bin"), *args],
                capture_output=True, text=True,
            )
            self.assertEqual(p.returncode, 0)
            self.assertIn(needle, p.stdout)


if __name__ == "__main__":
    unittest.main()
