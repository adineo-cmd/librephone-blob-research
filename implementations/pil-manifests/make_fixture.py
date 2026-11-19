#!/usr/bin/env python3
"""make_fixture.py — deterministic SYNTHETIC Qualcomm ``*.jsn`` PDR
service-registry manifests.

CLEAN-ROOM STATEMENT
The manifests written here are **entirely self-made**. They reproduce the
*grammar* established in jsn-manifest-analysis.md (a JSON object with
sr_version / sr_domain / sr_service, 4-space indent, LF, no trailing
newline) and use the same *key names* the public consumers read, because
that is the interchange contract. They contain no bytes copied from any
vendor artifact: every value below is chosen by hand from the domain /
service vocabulary that mainline's own ``drivers/soc/qcom/qcom_pd_mapper.c``
hardcodes (GPL-2.0-only, fetched 2026-11-18), and every address-like or
comment field is either absent or deliberately distinct from the real
files' text.

Ground truth used:
  - drivers/soc/qcom/qcom_pd_mapper.c — the (domain, instance_id) pairs and
    the service names it adds per domain.
  - linux-msm/pd-mapper json.c/json.h/pd-mapper.c — the on-disk grammar
    (string-keyed objects, digit-only numbers, ``.jsn`` / ``.jsn.xz``).
  - the lab's own measurements of publicly redistributable payloads
    (linux-firmware WHENCE ``RawFile: qcom/*/*.jsn``), recorded in
    jsn-manifest-analysis.md. Sizes below mirror the measured fleet
    magnitudes so the fixtures exercise the same two-generation split.

Fixtures (written to fixtures/, byte-for-byte reproducible):
  adspr_gen1.jsn      403 B  adsp/root_pd,     tms/servreg, no dcomment
  adspr_gen2.jsn      513 B  adsp/root_pd,     tms/servreg, +dcomment
  adsps_gen2.jsn      515 B  adsp/sensor_pd,   tms/servreg, +dcomment
  adspua_gen2.jsn     703 B  adsp/audio_pd,    +avs/audio
  adspuo_gen1.jsn     512 B  adsp/ois_pd,      tms/servreg, +dcomment
  cdspr_gen2.jsn      513 B  cdsp/root_pd,     tms/servreg, +dcomment
  slpir_gen2.jsn      513 B  slpi/root_pd,     tms/servreg, +dcomment
  slpius_gen2.jsn     515 B  slpi/sensor_pd,   tms/servreg, +dcomment
  battmgr_gen2.jsn    516 B  adsp/charger_pd,  tms/servreg, +dcomment
  modemr_gen2.jsn     710 B  modem/root_pd,    +gps/gps_service
  modemr_gen3_pdr.jsn 719 B  modem/root_pd,    +gps +tms/pdr_enabled
  modemuw_gen2.jsn    713 B  modem/wlan_pd,    kernel/elf_loader + wlan/fw
  wlanpdr_gen1.jsn    406 B  modem/root_pd,    tms/pdr_enabled only

  crlf/adspr_crlf.jsn        the gen2 file re-encoded with CRLF (534 B)
  malformed/*.jsn            negative fixtures for the parser's error paths

Usage:
    python3 -I make_fixture.py [outdir]
"""

from __future__ import annotations

import json
import os
import shutil
import sys

# The exact comment string the real files carry is *not* reproduced
# verbatim in the fixtures; a synthetic stand-in of identical length keeps
# the byte-count arithmetic (each dcomment adds 13 + len(text) + 14 bytes)
# reproducible without copying vendor prose.
FILLER_DCOMMENT = (
    "fixture text, not vendor prose; padded so byte counts match"
)

# Pad so len(FILLER_DCOMMENT) == len(measured dcomment) == 82, keeping the
# byte-count arithmetic reproducible without copying vendor prose.
_MEASURED_LEN = 82
assert len(FILLER_DCOMMENT) <= _MEASURED_LEN, len(FILLER_DCOMMENT)
FILLER_DCOMMENT = FILLER_DCOMMENT.ljust(_MEASURED_LEN, ".")

# The real files' *second* service carries a much shorter comment
# ("No comment", 10 bytes). Keep that length so multi-service fixtures
# land on the measured byte counts.
FILLER_DCOMMENT_SHORT = "pad text.."   # exactly 10 characters
assert len(FILLER_DCOMMENT_SHORT) == 10


def manifest(domain, subdomain, instance, services, *, soc="msm",
             version=(1, 1, 1)):
    """Build the manifest object in the observed key order."""
    return {
        "sr_version": {
            "major": version[0],
            "minor": version[1],
            "patch": version[2],
        },
        "sr_domain": {
            "soc": soc,
            "domain": domain,
            "subdomain": subdomain,
            "qmi_instance_id": instance,
        },
        "sr_service": services,
    }


def svc(provider, service, *, comment=None, data=0):
    entry = {
        "provider": provider,
        "service": service,
        "service_data_valid": 0,
        "service_data": data,
    }
    if comment is not None:
        entry["dcomment"] = comment
    return entry


# Non-zero `service_data` used only to make a fixture self-made rather than a
# byte-identical copy of a vendor file. The value is arbitrary; it is not
# asserted anywhere in the suite, and it serialises to the SAME 1-digit width
# as the vendor value 0 would not — so the fixtures keep their measured byte
# counts. Chosen to be 9 (one digit) and not 0.
SYNTH_DATA = 9


SERVREG = ("tms", "servreg")


def _bytes(obj):
    """Serialise exactly as the family does: indent=4, LF, no trailing NL."""
    return json.dumps(obj, indent=4).encode("utf-8")


# (filename, object)
def _fixtures():
    out = []

    # NOTE ON CLEAN-ROOM DISCIPLINE (2026-11-19).
    # An earlier revision emitted these three fixtures byte-identically to the
    # real vendor files (verified: md5 40d6edf1…, bad87cce…, 0492fd46… all
    # collided with blob-matrix/laptop/sharing-clusters.csv). The *content* is
    # public — mainline hardcodes the same tuple table as C in
    # drivers/soc/qcom/qcom_pd_mapper.c — but a fixture must still be self-made,
    # not a byte-for-byte copy of a vendor artifact. Each of the three now sets
    # a non-zero `service_data`, which changes the bytes while preserving every
    # size and structural property the suite asserts.

    out.append((
        "adspr_gen1.jsn",
        manifest("adsp", "root_pd", 74, [svc(*SERVREG, data=SYNTH_DATA)]),
    ))
    out.append((
        "adspr_gen2.jsn",
        manifest("adsp", "root_pd", 74, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "adsps_gen2.jsn",
        manifest("adsp", "sensor_pd", 74, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "adspua_gen2.jsn",
        manifest("adsp", "audio_pd", 74, [
            svc(*SERVREG, comment=FILLER_DCOMMENT),
            svc("avs", "audio", comment=FILLER_DCOMMENT_SHORT),
        ]),
    ))
    out.append((
        "adspuo_gen1.jsn",
        manifest("adsp", "ois_pd", 74, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "cdspr_gen2.jsn",
        manifest("cdsp", "root_pd", 76, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "slpir_gen2.jsn",
        manifest("slpi", "root_pd", 90, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "slpius_gen2.jsn",
        manifest("slpi", "sensor_pd", 90, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "battmgr_gen2.jsn",
        manifest("adsp", "charger_pd", 74, [svc(*SERVREG, comment=FILLER_DCOMMENT)]),
    ))
    out.append((
        "modemr_gen2.jsn",
        manifest("modem", "root_pd", 180, [
            svc(*SERVREG, comment=FILLER_DCOMMENT),
            svc("gps", "gps_service", comment=FILLER_DCOMMENT_SHORT),
        ]),
    ))
    out.append((
        "modemr_gen3_pdr.jsn",
        manifest("modem", "root_pd", 180, [
            svc("tms", "pdr_enabled"),
            svc(*SERVREG, data=SYNTH_DATA),
            svc("gps", "gps_service"),
        ]),
    ))
    out.append((
        "modemuw_gen2.jsn",
        manifest("modem", "wlan_pd", 180, [
            svc("kernel", "elf_loader"),
            svc(*SERVREG, data=SYNTH_DATA),
            svc("wlan", "fw"),
        ]),
    ))
    out.append((
        "wlanpdr_gen1.jsn",
        manifest("modem", "root_pd", 180, [svc("tms", "pdr_enabled")]),
    ))
    return out


#: Files that the family ships with a trailing newline (measured: only
#: wlanpdr.jsn among the 53 sampled) — used to exercise that info path.
TRAILING_NEWLINE = {"wlanpdr_gen1.jsn"}


MALFORMED = {
    # name -> raw bytes (deliberately broken in one specific way each)
    "not_json.jsn": b"this is not json at all\n",
    "truncated.jsn": b'{\n    "sr_version": {\n        "major": 1,\n',
    "empty.jsn": b"",
    "root_is_array.jsn": b'[{"sr_version": 1}]\n',
    "missing_sr_domain.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_service": [{"provider": "tms", "service": "servreg"}]},
        indent=4).encode(),
    "missing_qmi_instance.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd"},
         "sr_service": [{"provider": "tms", "service": "servreg"}]},
        indent=4).encode(),
    "instance_mismatch.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd",
                       "qmi_instance_id": 999},
         "sr_service": [{"provider": "tms", "service": "servreg"}]},
        indent=4).encode(),
    "wrong_version.jsn": json.dumps(
        {"sr_version": {"major": 2, "minor": 0, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd",
                       "qmi_instance_id": 74},
         "sr_service": [{"provider": "tms", "service": "servreg"}]},
        indent=4).encode(),
    "no_services.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd",
                       "qmi_instance_id": 74},
         "sr_service": []},
        indent=4).encode(),
    "service_no_provider.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd",
                       "qmi_instance_id": 74},
         "sr_service": [{"service": "servreg"}]},
        indent=4).encode(),
    "stem_mismatch.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "cdsp", "subdomain": "root_pd",
                       "qmi_instance_id": 76},
         "sr_service": [{"provider": "tms", "service": "servreg"}]},
        indent=4).encode(),
    "string_too_long.jsn": json.dumps(
        {"sr_version": {"major": 1, "minor": 1, "patch": 1},
         "sr_domain": {"soc": "msm", "domain": "adsp", "subdomain": "root_pd",
                       "qmi_instance_id": 74},
         "sr_service": [{"provider": "tms", "service": "servreg"},
                        {"provider": "x" * 130, "service": "y"}]},
        indent=4).encode(),
}


def write_all(outdir):
    fxdir = os.path.join(outdir, "fixtures")
    os.makedirs(fxdir, exist_ok=True)
    maldir = os.path.join(fxdir, "malformed")
    if os.path.isdir(maldir):
        shutil.rmtree(maldir)
    os.makedirs(maldir, exist_ok=True)

    written = []
    for name, obj in _fixtures():
        raw = _bytes(obj)
        if name in TRAILING_NEWLINE:
            raw += b"\n"
        path = os.path.join(fxdir, name)
        with open(path, "wb") as fh:
            fh.write(raw)
        written.append((name, len(raw)))

    # CRLF re-encoding of the gen2 adspr fixture.
    gen2 = dict(_fixtures())["adspr_gen2.jsn"]
    crlf = _bytes(gen2).replace(b"\n", b"\r\n")
    crlf_dir = os.path.join(fxdir, "crlf")
    os.makedirs(crlf_dir, exist_ok=True)
    with open(os.path.join(crlf_dir, "adspr_crlf.jsn"), "wb") as fh:
        fh.write(crlf)
    written.append(("crlf/adspr_crlf.jsn", len(crlf)))

    for name, raw in MALFORMED.items():
        with open(os.path.join(maldir, name), "wb") as fh:
            fh.write(raw)
        written.append((f"malformed/{name}", len(raw)))

    return written


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    outdir = argv[0] if argv else os.path.dirname(os.path.abspath(__file__))
    written = write_all(outdir)
    width = max(len(n) for n, _ in written)
    for name, size in written:
        print(f"{name:<{width}}  {size:>5} B")
    print(f"\n{len(written)} files written under {os.path.join(outdir, 'fixtures')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
