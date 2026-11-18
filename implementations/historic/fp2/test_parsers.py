#!/usr/bin/env python3
"""test_parsers.py — synthetic-fixture tests for the clean-room parsers in
this directory. Run:

    python3 -I test_parsers.py            (from this directory)
    python3 -I make_fixture.py fixtures/  (first, if fixtures absent)

No real firmware bytes are involved: see fixtures/make_fixture.py.
"""

import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mdt_probe          # noqa: E402
import prima_nv_probe     # noqa: E402

FIXTURES = os.path.join(HERE, "fixtures")
FAILURES = []


def check(name, cond, extra=""):
    if cond:
        print("PASS %s" % name)
    else:
        print("FAIL %s %s" % (name, extra))
        FAILURES.append(name)


def setup_fixtures():
    if not os.path.exists(os.path.join(FIXTURES, "synth_modem.mdt")):
        subprocess.run([sys.executable, "-I",
                        os.path.join(FIXTURES, "make_fixture.py"), FIXTURES],
                       check=True)


def test_mdt_happy():
    p = mdt_probe.MdtProbe(os.path.join(FIXTURES, "synth_modem.mdt"))
    r = p.parse()
    errs = [d for d in r["verification"]["diagnostics"] if d["class"] == "error"]
    check("mdt: no errors on synthetic image", not errs, str(errs))
    check("mdt: machine = EM_QDSP6(164)", r["elf"]["machine"] == 164)
    check("mdt: 3 phdrs", r["elf"]["phnum"] == 3)
    check("mdt: phdr1 is hash-type",
          r["structure"]["phdr0_is_hash_type"] is False and
          r["phdrs"][1]["flags"] & mdt_probe.QCOM_MDT_TYPE_MASK == mdt_probe.QCOM_MDT_TYPE_HASH)
    check("mdt: 1 loadable", r["summary"]["num_loadable"] == 1)
    check("mdt: range 0x08000000-0x08000fdc",
          r["summary"]["min_paddr"] == 0x08000000 and
          r["summary"]["max_paddr_end"] == 0x08000000 + 4052)
    check("mdt: all declared segments present",
          r["census"]["missing_with_nonzero_filesz"] == [] and
          r["census"]["extra_files_without_phdr"] == [])
    # every bNN file's actual size equals its declared p_filesz
    for s in r["segments"]:
        if s["file"]:
            check("mdt: b%02d size matches phdr" % s["idx"],
                  s["actual_size"] == s["declared_filesz"])


def test_mdt_truncated_segment():
    tmp = tempfile.mkdtemp()
    try:
        shutil.copy(os.path.join(FIXTURES, "synth_modem.mdt"), tmp)
        shutil.copy(os.path.join(FIXTURES, "synth_modem.b00"), tmp)
        shutil.copy(os.path.join(FIXTURES, "synth_modem.b01"), tmp)
        shutil.copy(os.path.join(FIXTURES, "synth_modem.b02"), tmp)
        # truncate b02 by one byte -> loader-relevant error
        p2 = os.path.join(tmp, "synth_modem.b02")
        data = open(p2, "rb").read()[:-1]
        open(p2, "wb").write(data)
        p = mdt_probe.MdtProbe(os.path.join(tmp, "synth_modem.mdt"), tmp)
        r = p.parse()
        errs = [d for d in r["verification"]["diagnostics"] if d["class"] == "error"]
        check("mdt: truncated segment detected", any(".b02" in e["message"] for e in errs),
              str(errs))
    finally:
        shutil.rmtree(tmp)


def test_mdt_bad_magic():
    tmp = tempfile.mkdtemp()
    try:
        src = os.path.join(FIXTURES, "synth_modem.mdt")
        data = bytearray(open(src, "rb").read())
        data[0] = 0x7E
        bad = os.path.join(tmp, "synth_modem.mdt")
        open(bad, "wb").write(bytes(data))
        try:
            mdt_probe.MdtProbe(bad).parse()
            check("mdt: bad magic raises", False)
        except ValueError as e:
            check("mdt: bad magic raises", "magic" in str(e))
    finally:
        shutil.rmtree(tmp)


def test_nv2_happy():
    p = prima_nv_probe.PrimaNvProbe(os.path.join(FIXTURES, "synth_nv2.bin"))
    r = p.parse()
    check("nv2: kind = NV2-raw-struct", r["kind"] == "NV2-raw-struct")
    check("nv2: no errors", not r["errors"], str(r["errors"]))
    f = r["snv_fields"]
    check("nv2: productId 0x1234", f["product_id"] == 0x1234)
    check("nv2: revId 2", f["wlan_nv_rev_id"] == 2)
    check("nv2: 2x2 chains", f["num_tx_chains"] == 2 and f["num_rx_chains"] == 2)
    check("nv2: nvVersion 2 (Pronto LPDC)", f["nv_version_byte"] == 2)
    check("nv2: coupler INTERNAL(0)", f["coupler_type"] == 0)
    check("nv2: tables block = 128B", f["tables_block_bytes"] == 128)
    # synthetic MAC must be recoverable through the fingerprint only
    check("nv2: mac fingerprints present", len(f["mac_sha1_12"]) == 4)


def test_nv3_happy():
    p = prima_nv_probe.PrimaNvProbe(os.path.join(FIXTURES, "synth_nv3.bin"))
    r = p.parse()
    check("nv3: kind = NV3-template-stream", r["kind"] == "NV3-template-stream")
    check("nv3: framing exact", r["framing_exact"], str(r["errors"]))
    check("nv3: 3 streams", r["stream_count"] == 3)
    check("nv3: 2 table templates + 1 data stream",
          len(r["tables"]) == 2 and len(r["data_streams"]) == 1)
    ds = r["data_streams"][0]
    check("nv3: data stream targets table 1", ds["table_id"] == 1)
    check("nv3: data stream length 6", ds["length"] == 6)


def test_nv_truncation():
    tmp = tempfile.mkdtemp()
    try:
        data = bytearray(open(os.path.join(FIXTURES, "synth_nv3.bin"), "rb").read())
        data = data[:-3]  # cut inside the last stream
        bad = os.path.join(tmp, "synth_nv3.bin")
        open(bad, "wb").write(bytes(data))
        p = prima_nv_probe.PrimaNvProbe(bad)
        r = p.parse()
        check("nv3: truncated stream detected", any("truncated" in e for e in r["errors"]),
              str(r["errors"]))
    finally:
        shutil.rmtree(tmp)


def main():
    setup_fixtures()
    test_mdt_happy()
    test_mdt_truncated_segment()
    test_mdt_bad_magic()
    test_nv2_happy()
    test_nv3_happy()
    test_nv_truncation()
    print("---")
    if FAILURES:
        print("FAILED: %d" % len(FAILURES))
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
