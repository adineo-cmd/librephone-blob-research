#!/usr/bin/env python3
"""test_jsn_probe.py — unittest suite for the clean-room ``*.jsn``
PDR service-registry manifest parser.

Run with:
    python3 -m unittest -v test_jsn_probe

(Do not add ``-I`` here: it drops the CWD from ``sys.path`` and the loader
cannot find the module. ``jsn_probe.py`` itself is always runnable with
``-I``, which is how the CLI tests invoke it.)

Fixtures are synthetic (see make_fixture.py); no vendor artifact is
required or referenced. Tests that need a real file are skipped unless
``JSN_REAL_DIR`` points at a directory of the real manifests.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import jsn_probe                                    # noqa: E402
import make_fixture                                 # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
PROBE = os.path.join(HERE, "jsn_probe.py")
REAL_DIR = os.environ.get("JSN_REAL_DIR")


def fx(*parts):
    return os.path.join(FIXTURES, *parts)


def run_cli(args, cwd=HERE):
    """Invoke the CLI as a subprocess so exit codes are genuinely tested."""
    proc = subprocess.run(
        [sys.executable, "-I", PROBE, *args],
        capture_output=True, text=True, cwd=cwd,
    )
    return proc.returncode, proc.stdout, proc.stderr


class TestFixtureDeterminism(unittest.TestCase):
    def test_fixtures_exist(self):
        for name in ("adspr_gen1.jsn", "adspr_gen2.jsn", "adspua_gen2.jsn",
                     "modemuw_gen2.jsn", "crlf/adspr_crlf.jsn"):
            self.assertTrue(os.path.isfile(fx(*name.split("/"))), name)

    def test_regeneration_is_byte_identical(self):
        before = {}
        for root, _dirs, files in os.walk(FIXTURES):
            for f in files:
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    before[os.path.relpath(p, FIXTURES)] = hashlib.sha256(
                        fh.read()).hexdigest()

        with tempfile.TemporaryDirectory() as tmp:
            make_fixture.write_all(tmp)
            after = {}
            base = os.path.join(tmp, "fixtures")
            for root, _dirs, files in os.walk(base):
                for f in files:
                    p = os.path.join(root, f)
                    with open(p, "rb") as fh:
                        after[os.path.relpath(p, base)] = hashlib.sha256(
                            fh.read()).hexdigest()

        self.assertEqual(before, after,
                         "make_fixture.py is not deterministic")

    def test_fixture_sizes_match_measured_fleet(self):
        # Sizes measured from the real fleet (analysis §1). The synthetic
        # manifests must land on the same magnitudes to exercise the
        # two-generation split faithfully.
        expected = {
            "adspr_gen1.jsn": 403, "adspr_gen2.jsn": 513,
            "adsps_gen2.jsn": 515, "adspua_gen2.jsn": 703,
            "adspuo_gen1.jsn": 512, "cdspr_gen2.jsn": 513,
            "slpir_gen2.jsn": 513, "slpius_gen2.jsn": 515,
            "battmgr_gen2.jsn": 516, "modemr_gen2.jsn": 710,
            "modemr_gen3_pdr.jsn": 719, "modemuw_gen2.jsn": 713,
        }
        for name, size in expected.items():
            self.assertEqual(os.path.getsize(fx(name)), size, name)

    def test_dcomment_is_not_vendor_prose(self):
        # The fixtures must not reproduce the vendor comment text.
        with open(fx("adspr_gen2.jsn"), "rb") as fh:
            raw = fh.read()
        self.assertNotIn(b"data can be used to configure ACK timeout", raw)
        # ...but must be the same length so sizes match.
        self.assertEqual(len(make_fixture.FILLER_DCOMMENT), 82)

    def test_no_fixture_is_byte_identical_to_a_vendor_blob(self):
        # Regression guard for a real clean-room violation found 2026-11-19:
        # adspr_gen1.jsn, modemuw_gen2.jsn and modemr_gen3_pdr.jsn were once
        # emitted byte-identically to the vendor files (md5 40d6edf1…,
        # bad87cce…, 0492fd46…), which collide with real rows in
        # blob-matrix/laptop/sharing-clusters.csv. The *content* is public, but
        # a fixture must be self-made, never a byte-for-byte vendor copy.
        #
        # Hashes every fixture against the lab DB's md5 set. Skipped when the
        # DB file is absent (partial checkout) so it never false-fails.
        db = os.path.join(HERE, "..", "..", "blob-matrix", "laptop",
                          "sharing-clusters.csv")
        if not os.path.isfile(db):
            self.skipTest("sharing-clusters.csv not present")

        import csv
        known = set()
        with open(db, newline="") as fh:
            for row in csv.DictReader(fh):
                known.add(row["md5"])

        collisions = []
        for root, _dirs, files in os.walk(FIXTURES):
            for f in files:
                p = os.path.join(root, f)
                with open(p, "rb") as fh:
                    raw = fh.read()
                if not raw:
                    continue  # empty is a legitimate malformed-input fixture
                digest = hashlib.md5(raw).hexdigest()
                if digest in known:
                    collisions.append((os.path.relpath(p, FIXTURES), digest))

        self.assertEqual(
            collisions, [],
            "fixtures byte-identical to a real vendor blob: %r" % (collisions,))


class TestGrammar(unittest.TestCase):
    def test_gen1_shape(self):
        rep = jsn_probe.probe(fx("adspr_gen1.jsn"))
        self.assertTrue(rep["ok"])
        self.assertEqual(rep["exit"], 0)
        self.assertEqual(rep["summary"]["domain"], "msm/adsp/root_pd")
        self.assertEqual(rep["summary"]["qmi_instance_id"], 74)
        self.assertEqual(rep["summary"]["service_count"], 1)
        self.assertEqual(rep["summary"]["services"][0]["service_full"],
                         "tms/servreg")
        self.assertIsNone(rep["summary"]["services"][0]["dcomment"])

    def test_gen2_adds_dcomment_only(self):
        gen1 = jsn_probe.probe(fx("adspr_gen1.jsn"))
        gen2 = jsn_probe.probe(fx("adspr_gen2.jsn"))
        self.assertTrue(gen1["ok"] and gen2["ok"])
        self.assertEqual(gen1["summary"]["domain"], gen2["summary"]["domain"])
        self.assertIsNotNone(gen2["summary"]["services"][0]["dcomment"])
        # 513 - 403 == 110 == cost of one 82-char dcomment
        self.assertEqual(gen2["framing"]["bytes"] - gen1["framing"]["bytes"], 110)

    def test_multi_service(self):
        rep = jsn_probe.probe(fx("adspua_gen2.jsn"))
        self.assertTrue(rep["ok"])
        fulls = [s["service_full"] for s in rep["summary"]["services"]]
        self.assertEqual(fulls, ["tms/servreg", "avs/audio"])
        self.assertEqual(rep["summary"]["kernel_services_for_domain"],
                         ["tms/servreg", "avs/audio"])

    def test_modemuw_three_services(self):
        rep = jsn_probe.probe(fx("modemuw_gen2.jsn"))
        self.assertTrue(rep["ok"])
        fulls = [s["service_full"] for s in rep["summary"]["services"]]
        self.assertEqual(fulls, ["kernel/elf_loader", "tms/servreg", "wlan/fw"])
        self.assertEqual(rep["summary"]["domain"], "msm/modem/wlan_pd")
        self.assertEqual(rep["summary"]["qmi_instance_id"], 180)

    def test_sr_version_wire_encoding(self):
        rep = jsn_probe.probe(fx("adspr_gen2.jsn"))
        # major 1, minor 1 -> 0x0101 == SERVREG_QMI_VERSION
        self.assertEqual(rep["summary"]["sr_version_wire"], 0x0101)
        self.assertEqual(jsn_probe.SERVREG_QMI_VERSION, 0x101)


class TestFraming(unittest.TestCase):
    def test_lf_no_trailing_newline_no_bom(self):
        with open(fx("adspr_gen2.jsn"), "rb") as fh:
            fr = jsn_probe.inspect_framing(fh.read())
        self.assertEqual(fr["line_ending"], "lf")
        self.assertFalse(fr["trailing_newline"])
        self.assertFalse(fr["bom"])
        self.assertEqual(fr["indent_width"], 4)
        self.assertFalse(fr["tabs"])

    def test_crlf_variant_is_flagged(self):
        rep = jsn_probe.probe(fx("crlf", "adspr_crlf.jsn"))
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("crlf-lines", codes)
        self.assertTrue(rep["ok"], "CRLF must be a warning, not an error")
        fr = rep["framing"]
        self.assertEqual(fr["line_ending"], "crlf")

    def test_crlf_is_pure_reencoding(self):
        # Exactly 21 extra bytes: 21 LF -> CRLF.
        with open(fx("adspr_gen2.jsn"), "rb") as fh:
            a = fh.read()
        with open(fx("crlf", "adspr_crlf.jsn"), "rb") as fh:
            b = fh.read()
        self.assertEqual(b.replace(b"\r\n", b"\n"), a)
        self.assertEqual(len(b) - len(a), b.count(b"\r\n"))

    def test_wlanpdr_trailing_newline_is_info_only(self):
        rep = jsn_probe.probe(fx("wlanpdr_gen1.jsn"))
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("trailing-newline", codes)
        self.assertTrue(rep["ok"])

    def test_hashes_reported(self):
        with open(fx("adspr_gen2.jsn"), "rb") as fh:
            raw = fh.read()
        fr = jsn_probe.inspect_framing(raw)
        self.assertEqual(fr["md5"], hashlib.md5(raw).hexdigest())
        self.assertEqual(len(fr["sha256"]), 64)


class TestTaxonomy(unittest.TestCase):
    CASES = [
        ("adspr", "adsp", "root_pd", "r"),
        ("adsps", "adsp", "sensor_pd", "s"),
        ("adspua", "adsp", "audio_pd", "ua"),
        ("adspuo", "adsp", "ois_pd", "uo"),
        ("cdspr", "cdsp", "root_pd", "r"),
        ("slpir", "slpi", "root_pd", "r"),
        ("slpius", "slpi", "sensor_pd", "us"),
        ("modemr", "modem", "root_pd", "r"),
        ("modemuw", "modem", "wlan_pd", "uw"),
        ("battmgr", "adsp", "charger_pd", None),
    ]

    def test_suffix_table(self):
        for stem, dom, sub, suffix in self.CASES:
            with self.subTest(stem=stem):
                c = jsn_probe.classify_stem(stem)
                self.assertTrue(c["resolved"])
                self.assertEqual(c["domain"], dom)
                self.assertEqual(c["subdomain"], sub)
                self.assertEqual(c["suffix"], suffix)

    def test_unknown_stem(self):
        c = jsn_probe.classify_stem("foobar")
        self.assertFalse(c["resolved"])

    def test_stem_matches_declared_domain(self):
        # Every generated fixture's filename must agree with its sr_domain,
        # AND the taxonomy must actually resolve (so the check is live).
        checked = 0
        for name in os.listdir(FIXTURES):
            if not name.endswith(".jsn"):
                continue
            rep = jsn_probe.probe(fx(name))
            self.assertTrue(rep["taxonomy"]["resolved"],
                            f"{name}: taxonomy did not resolve "
                            f"({rep['taxonomy']['note']}) — the stem/domain "
                            "cross-check would be silently skipped")
            codes = {d["code"] for d in rep["diagnostics"]}
            self.assertNotIn("stem-domain-mismatch", codes, name)
            self.assertNotIn("stem-subdomain-mismatch", codes, name)
            checked += 1
        self.assertGreaterEqual(checked, 13)


class TestKernelContract(unittest.TestCase):
    def test_all_fixture_instances_match_kernel_table(self):
        for name in sorted(os.listdir(FIXTURES)):
            if not name.endswith(".jsn"):
                continue
            rep = jsn_probe.probe(fx(name))
            if not rep.get("summary", {}).get("domain"):
                continue
            codes = {d["code"] for d in rep["diagnostics"]}
            self.assertNotIn("instance-mismatch", codes, name)
            self.assertNotIn("domain-unknown-to-kernel", codes, name)

    def test_kernel_instance_table_values(self):
        t = jsn_probe.KERNEL_DOMAIN_INSTANCE
        self.assertEqual(t["msm/adsp/root_pd"], 74)
        self.assertEqual(t["msm/cdsp/root_pd"], 76)
        self.assertEqual(t["msm/slpi/root_pd"], 90)
        self.assertEqual(t["msm/modem/root_pd"], 180)
        self.assertEqual(t["msm/modem/wlan_pd"], 180)
        self.assertEqual(t["msm/cdsp1/root_pd"], 125)
        self.assertEqual(t["msm/gpdsp/root_pd"], 192)

    def test_implicit_servreg_constant(self):
        self.assertEqual(jsn_probe.IMPLICIT_SERVICE, "tms/servreg")


class TestMalformed(unittest.TestCase):
    def test_not_json_exits_2(self):
        code, out, _err = run_cli([fx("malformed", "not_json.jsn"), "--brief"])
        self.assertEqual(code, 2, out)

    def test_truncated_exits_2(self):
        code, _out, _err = run_cli([fx("malformed", "truncated.jsn"), "--brief"])
        self.assertEqual(code, 2)

    def test_empty_exits_2(self):
        code, _out, _err = run_cli([fx("malformed", "empty.jsn"), "--brief"])
        self.assertEqual(code, 2)

    def test_missing_file_exits_2(self):
        code, _out, _err = run_cli(["/nonexistent/nope.jsn", "--brief"])
        self.assertEqual(code, 2)

    def test_root_is_array_exits_1(self):
        code, _out, _err = run_cli([fx("malformed", "root_is_array.jsn"), "--brief"])
        self.assertEqual(code, 1)

    def test_missing_sr_domain_exits_1(self):
        code, _out, _err = run_cli([fx("malformed", "missing_sr_domain.jsn"), "--brief"])
        self.assertEqual(code, 1)

    def test_missing_qmi_instance_exits_1(self):
        code, _out, _err = run_cli(
            [fx("malformed", "missing_qmi_instance.jsn"), "--brief"])
        self.assertEqual(code, 1)

    def test_instance_mismatch_exits_1(self):
        code, _out, _err = run_cli([fx("malformed", "instance_mismatch.jsn"), "--brief"])
        self.assertEqual(code, 1)
        rep = jsn_probe.probe(fx("malformed", "instance_mismatch.jsn"))
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("instance-mismatch", codes)

    def test_wrong_version_exits_1(self):
        code, _out, _err = run_cli([fx("malformed", "wrong_version.jsn"), "--brief"])
        self.assertEqual(code, 1)
        rep = jsn_probe.probe(fx("malformed", "wrong_version.jsn"))
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("servreg-version", codes)

    def test_no_services_exits_1(self):
        code, _out, _err = run_cli([fx("malformed", "no_services.jsn"), "--brief"])
        self.assertEqual(code, 1)

    def test_service_without_provider_exits_1(self):
        code, _out, _err = run_cli(
            [fx("malformed", "service_no_provider.jsn"), "--brief"])
        self.assertEqual(code, 1)

    def test_stem_mismatch_exits_1(self):
        # A file named adspr*.jsn that declares cdsp -> stem/domain conflict.
        tmp = tempfile.mkdtemp()
        path = os.path.join(tmp, "adspr.jsn")
        with open(fx("malformed", "stem_mismatch.jsn"), "rb") as src, \
                open(path, "wb") as dst:
            dst.write(src.read())
        code, _out, _err = run_cli([path, "--brief"])
        self.assertEqual(code, 1)
        rep = jsn_probe.probe(path)
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("stem-domain-mismatch", codes)

    def test_overlong_string_warns_but_parses(self):
        rep = jsn_probe.probe(fx("malformed", "string_too_long.jsn"))
        codes = {d["code"] for d in rep["diagnostics"]}
        self.assertIn("pd-mapper-truncation", codes)
        self.assertTrue(rep["ok"], "truncation warning must not fail the parse")


class TestCliContract(unittest.TestCase):
    def test_exit_zero_on_valid(self):
        code, out, _err = run_cli([fx("adspr_gen2.jsn")])
        self.assertEqual(code, 0)
        self.assertIn("result    : OK", out)

    def test_brief_is_one_line(self):
        code, out, _err = run_cli([fx("adspr_gen2.jsn"), "--brief"])
        self.assertEqual(code, 0)
        self.assertEqual(len(out.strip().splitlines()), 1, out)
        self.assertIn("msm/adsp/root_pd", out)

    def test_json_output_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "out.json")
            code, _out, _err = run_cli(
                [fx("adspua_gen2.jsn"), "--json", out_path, "--quiet"])
            self.assertEqual(code, 0)
            with open(out_path) as fh:
                doc = json.load(fh)
        for key in ("file", "ok", "diagnostics", "framing",
                    "summary", "stem", "taxonomy", "exit"):
            self.assertIn(key, doc)
        self.assertIsInstance(doc["diagnostics"], list)
        self.assertEqual(doc["summary"]["service_count"], 2)
        # JSON must be strict (no NaN/Infinity) and UTF-8.
        json.dumps(doc, allow_nan=False)

    def test_quiet_suppresses_stdout(self):
        code, out, _err = run_cli([fx("adspr_gen2.jsn"), "--quiet"])
        self.assertEqual(code, 0)
        self.assertEqual(out, "")

    def test_allow_crlf_downgrades_warning(self):
        code, out, _err = run_cli(
            [fx("crlf", "adspr_crlf.jsn"), "--brief", "--allow-crlf"])
        self.assertEqual(code, 0)
        self.assertIn("0W", out)

    def test_json_written_even_on_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            out_path = os.path.join(tmp, "bad.json")
            code, _out, _err = run_cli(
                [fx("malformed", "instance_mismatch.jsn"),
                 "--json", out_path, "--quiet"])
            self.assertEqual(code, 1)
            with open(out_path) as fh:
                doc = json.load(fh)
            self.assertFalse(doc["ok"])


class TestRealPayloads(unittest.TestCase):
    """Optional: run against fetched real manifests when available."""

    @unittest.skipUnless(REAL_DIR and os.path.isdir(REAL_DIR),
                         "set JSN_REAL_DIR to a directory of real .jsn files")
    def test_real_files_parse_clean(self):
        seen = 0
        for name in sorted(os.listdir(REAL_DIR)):
            if not name.endswith(".jsn"):
                continue
            rep = jsn_probe.probe(os.path.join(REAL_DIR, name))
            self.assertTrue(rep["ok"],
                            f"{name}: {[d for d in rep['diagnostics'] if d['level']=='error']}")
            seen += 1
        self.assertGreater(seen, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
