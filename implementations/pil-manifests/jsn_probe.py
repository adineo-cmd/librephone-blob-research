#!/usr/bin/env python3
"""jsn_probe.py — clean-room parser/validator for the Qualcomm ``*.jsn``
PDR (Protection Domain Registry) *service registry* manifest family.

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-18 from two public sources only:

  (a) GPL-2.0-only kernel source, torvalds/linux master, fetched
      2026-11-18 via the GitHub contents API:
        drivers/soc/qcom/qcom_pd_mapper.c
        drivers/soc/qcom/pdr_interface.c
        drivers/soc/qcom/mdt_loader.c            (checked: no .jsn use)
        drivers/remoteproc/qcom_q6v5_pas.c       (checked: no .jsn use)
      plus the BSD-3-Clause userspace consumer linux-msm/pd-mapper
      (json.c, json.h, pd-mapper.c, servreg_loc.h), cloned 2026-11-18,
      which contains the *actual on-disk parser* for this file family.

  (b) the lab's own byte-level measurement of publicly redistributable
      payloads. The identical files are published by linux-firmware
      (WHENCE "RawFile: qcom/*/*.jsn", 114 entries as of 2026-11-18)
      and were fetched md5-verified (see README.md). No proprietary
      artifact was decompiled and no vendor header was read.

No decompiled code, no proprietary documentation, no vendor SDK was used.

======================================================================
WHAT THIS FILE IS (established by the sources above, not assumed)

A ``.jsn`` in ``/vendor/firmware`` (or ``/lib/firmware/qcom/<soc>/...``)
is a **JSON service-registry manifest** consumed by the PD-mapper: a
lookup table mapping a *service* name to the *protection domain* that
hosts it, plus a QMI instance id. It is NOT a split-MDT segment list and
it does NOT name ``.mdt``/``.bNN`` image files. The kernel proper never
opens it: mainline carries the same table compiled in as C
(``qcom_pd_mapper.c``). See jsn-manifest-analysis.md §4.

The only public on-disk parser is pd-mapper's ``pd_load_map()``; the
grammar and validation below follows it exactly, with each rule tagged
by its source.

Usage:
    python3 -I jsn_probe.py <file.jsn> [--json OUT.json] [--brief]
                            [--allow-crlf] [--quiet]

Exit status:
    0  parses and satisfies every structural invariant
    1  parses as JSON but violates an invariant (error-class diagnostic)
    2  does not parse as JSON at all / not a file / not UTF-8
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Source-derived constants
# ---------------------------------------------------------------------------

#: pd-mapper json.c: json_parse_string() copies into ``char buf[128]`` and
#: stops at ``b - buf < sizeof(buf) - 1``, so a JSON string value longer
#: than 127 bytes is silently TRUNCATED by the only public consumer.
PD_MAPPER_STRING_MAX = 127

#: pd-mapper json.c: json_parse_number() accepts only ``isdigit()``
#: characters, i.e. non-negative integers. No sign, no decimal point.
PD_MAPPER_NUMBER_DIGITS_ONLY = True

#: pd-mapper.c: known_extensions[] = { ".jsn.xz", ".jsn", NULL } — the
#: discovery suffix set. Files are found by directory adjacency to a
#: remoteproc's ``firmware`` symlink target, not by name.
PD_MAPPER_EXTENSIONS = (".jsn.xz", ".jsn")

#: qcom_pd_mapper.c: SERVREG_QMI_VERSION 0x101 == (major 1, minor 1).
#: Every observed manifest carries sr_version {1,1,1}; the ``patch`` field
#: is not represented in the kernel constant.
SERVREG_QMI_VERSION = 0x101

#: qcom_pd_mapper.c: the (domain, instance_id) pairs it hardcodes.
#: Any manifest domain must appear here or the kernel cannot answer for it.
KERNEL_DOMAIN_INSTANCE = {
    "msm/adsp/root_pd": 74,
    "msm/adsp/sensor_pd": 74,
    "msm/adsp/audio_pd": 74,
    "msm/adsp/charger_pd": 74,
    "msm/adsp/ois_pd": 74,
    "msm/cdsp/root_pd": 76,
    "msm/cdsp1/root_pd": 125,
    "msm/gpdsp/root_pd": 192,
    "msm/gpdsp1/root_pd": 241,
    "msm/slpi/root_pd": 90,
    "msm/slpi/sensor_pd": 90,
    "msm/modem/root_pd": 180,
    "msm/modem/wlan_pd": 180,
}

#: qcom_pd_mapper.c: TMS_SERVREG_SERVICE "tms/servreg" is *implicitly*
#: added to every domain by qcom_pdm_add_domain() before the extra
#: services. Manifests therefore list it explicitly as the first element.
IMPLICIT_SERVICE = "tms/servreg"

#: Observed provider/service vocabulary across the 53 real manifests
#: measured 2026-11-18 (measurement, not spec — see analysis §3).
KNOWN_PROVIDERS = {"tms", "avs", "gps", "kernel", "wlan"}
KNOWN_SERVICES = {
    "servreg", "pdr_enabled",     # provider tms
    "audio",                       # provider avs
    "gps_service",                 # provider gps
    "elf_loader",                  # provider kernel
    "fw",                          # provider wlan
}

#: The reference silent comment text; its presence/absence is the sole
#: difference between the two size generations of a given stem (§5).
REFERENCE_DCOMMENT = (
    "data can be used to configure ACK timeout."
    "Make data_valid 1 as well.Unit is second"
)

TOP_LEVEL_KEYS = ("sr_version", "sr_domain", "sr_service")
DOMAIN_KEYS = ("soc", "domain", "subdomain", "qmi_instance_id")
SERVICE_REQUIRED = ("provider", "service")
SERVICE_OPTIONAL = ("service_data_valid", "service_data", "dcomment")


# ---------------------------------------------------------------------------
# Result model
# ---------------------------------------------------------------------------

class Diagnostic:
    __slots__ = ("level", "code", "message")

    def __init__(self, level, code, message):
        self.level = level          # "error" | "warn" | "info"
        self.code = code
        self.message = message

    def as_dict(self):
        return {"level": self.level, "code": self.code, "message": self.message}

    def __repr__(self):
        return f"<{self.level}:{self.code}> {self.message}"


class JsnError(Exception):
    """Raised when the bytes are not a parseable manifest at all."""


# ---------------------------------------------------------------------------
# Byte framing
# ---------------------------------------------------------------------------

def inspect_framing(raw):
    """Measure the exact byte-level framing of the manifest.

    Every field here is a measurement of the artifact, reported so the
    test suite can pin the family's real conventions (4-space indent, LF,
    no trailing newline, no BOM).
    """
    has_bom = raw.startswith(b"\xef\xbb\xbf")
    crlf = raw.count(b"\r\n")
    lf = raw.count(b"\n")
    trailing_nl = raw.endswith(b"\n") or raw.endswith(b"\r\n")
    # Indentation of the first nested key, i.e. width of the sr_version body.
    indent_width = 0
    for line in raw.split(b"\n")[1:]:
        stripped = line.lstrip(b" \t")
        if stripped and stripped != line:
            indent_width = len(line) - len(stripped)
            break
    return {
        "bytes": len(raw),
        "bom": has_bom,
        "crlf_lines": crlf,
        "lf_lines": lf,
        "line_ending": "crlf" if crlf else ("lf" if lf else "none"),
        "trailing_newline": trailing_nl,
        "indent_width": indent_width,
        "tabs": raw.count(b"\t") > 0,
        "md5": hashlib.md5(raw).hexdigest(),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


# ---------------------------------------------------------------------------
# Structural validation
# ---------------------------------------------------------------------------

def _is_int(v):
    # bool is an int subclass; a JSON true/false is not a valid id.
    return isinstance(v, int) and not isinstance(v, bool)


def _check_string(diags, where, value, *, required=True):
    if value is None:
        if required:
            diags.append(Diagnostic("error", "missing-string",
                                    f"{where}: required string absent"))
        return
    if not isinstance(value, str):
        diags.append(Diagnostic("error", "type",
                                f"{where}: expected string, got {type(value).__name__}"))
        return
    if len(value.encode("utf-8")) > PD_MAPPER_STRING_MAX:
        diags.append(Diagnostic(
            "warn", "pd-mapper-truncation",
            f"{where}: {len(value.encode('utf-8'))} bytes exceeds pd-mapper "
            f"json_parse_string() buf[128] limit ({PD_MAPPER_STRING_MAX}); "
            "the consumer will silently truncate"))


def validate(doc, *, strict=True):
    """Validate a parsed manifest against the grammar + consumer contract.

    Returns (diagnostics, summary). ``strict`` adds the family-convention
    checks (known provider vocabulary, key order) as warnings rather than
    errors, so an unusual-but-valid manifest still parses.
    """
    diags = []
    summary = {}

    if not isinstance(doc, dict):
        diags.append(Diagnostic("error", "root-type",
                                f"top level must be a JSON object, got {type(doc).__name__}"))
        return diags, summary

    # --- top-level shape -------------------------------------------------
    for k in TOP_LEVEL_KEYS:
        if k not in doc:
            # pd-mapper reads sr_domain and sr_service; sr_version is not
            # read at all by pd-mapper, but every real file carries it.
            level = "error" if k in ("sr_domain", "sr_service") else "warn"
            diags.append(Diagnostic(level, "missing-key",
                                    f"top level: '{k}' absent"))
    extra = [k for k in doc if k not in TOP_LEVEL_KEYS]
    if extra:
        diags.append(Diagnostic("warn", "unknown-top-key",
                                f"top level: unexpected key(s) {extra}"))
    if strict:
        order = [k for k in doc if k in TOP_LEVEL_KEYS]
        if order != [k for k in TOP_LEVEL_KEYS if k in doc]:
            diags.append(Diagnostic("info", "key-order",
                                    f"top-level order {order} differs from "
                                    f"observed convention {list(TOP_LEVEL_KEYS)}"))

    # --- sr_version ------------------------------------------------------
    ver = doc.get("sr_version")
    if ver is not None:
        if not isinstance(ver, dict):
            diags.append(Diagnostic("error", "sr_version-type",
                                    "sr_version must be an object"))
        else:
            for k in ("major", "minor", "patch"):
                if k not in ver:
                    diags.append(Diagnostic("error", "sr_version-missing",
                                            f"sr_version.{k} absent"))
                elif not _is_int(ver[k]):
                    diags.append(Diagnostic("error", "sr_version-type",
                                            f"sr_version.{k} must be an integer"))
            if _is_int(ver.get("major")) and _is_int(ver.get("minor")):
                wire = (ver["major"] << 8) | ver["minor"]
                summary["sr_version"] = [ver["major"], ver["minor"], ver.get("patch")]
                summary["sr_version_wire"] = wire
                if wire != SERVREG_QMI_VERSION:
                    diags.append(Diagnostic(
                        "error", "servreg-version",
                        f"sr_version.major/minor = 0x{wire:04x}, kernel expects "
                        f"SERVREG_QMI_VERSION 0x{SERVREG_QMI_VERSION:04x}"))
            if _is_int(ver.get("patch")) and ver["patch"] != 1:
                diags.append(Diagnostic("info", "sr_version-patch",
                                        f"sr_version.patch = {ver['patch']} "
                                        "(all 53 measured files carry 1)"))

    # --- sr_domain -------------------------------------------------------
    dom = doc.get("sr_domain")
    if dom is None:
        return diags, summary
    if not isinstance(dom, dict):
        diags.append(Diagnostic("error", "sr_domain-type",
                                "sr_domain must be an object"))
        return diags, summary

    for k in DOMAIN_KEYS:
        if k not in dom:
            diags.append(Diagnostic("error", "sr_domain-missing",
                                    f"sr_domain.{k} absent (pd_load_map requires it)"
                                    if k == "qmi_instance_id" else
                                    f"sr_domain.{k} absent"))
    for k in ("soc", "domain", "subdomain"):
        _check_string(diags, f"sr_domain.{k}", dom.get(k))

    soc = dom.get("soc")
    d = dom.get("domain")
    sub = dom.get("subdomain")
    inst = dom.get("qmi_instance_id")

    if inst is not None and not _is_int(inst):
        diags.append(Diagnostic(
            "error", "qmi_instance-type",
            f"sr_domain.qmi_instance_id must be a non-negative integer "
            f"(pd-mapper json_parse_number is isdigit-only), got {inst!r}"))
    elif _is_int(inst) and inst < 0:
        diags.append(Diagnostic("error", "qmi_instance-negative",
                                "qmi_instance_id must be non-negative"))

    if isinstance(soc, str) and isinstance(d, str) and isinstance(sub, str):
        path = f"{soc}/{d}/{sub}"
        summary["domain"] = path
        summary["subdomain"] = sub
        if _is_int(inst):
            summary["qmi_instance_id"] = inst
            expect = KERNEL_DOMAIN_INSTANCE.get(path)
            if expect is None:
                diags.append(Diagnostic(
                    "warn", "domain-unknown-to-kernel",
                    f"'{path}' is not in qcom_pd_mapper.c's hardcoded table; "
                    "mainline cannot answer a lookup for this domain"))
            elif expect != inst:
                diags.append(Diagnostic(
                    "error", "instance-mismatch",
                    f"'{path}' carries instance {inst} but qcom_pd_mapper.c "
                    f"hardcodes {expect}"))

    # --- sr_service ------------------------------------------------------
    svc = doc.get("sr_service")
    if svc is None:
        return diags, summary
    if not isinstance(svc, list):
        diags.append(Diagnostic("error", "sr_service-type",
                                "sr_service must be an array"))
        return diags, summary
    if not svc:
        diags.append(Diagnostic("error", "sr_service-empty",
                                "sr_service must contain at least one entry"))

    table = []
    for i, entry in enumerate(svc):
        where = f"sr_service[{i}]"
        if not isinstance(entry, dict):
            diags.append(Diagnostic("error", "service-type",
                                    f"{where}: expected object"))
            continue
        for k in SERVICE_REQUIRED:
            if k not in entry:
                diags.append(Diagnostic(
                    "error", "service-missing",
                    f"{where}.{k} absent (pd_load_map rejects the whole file)"))
            else:
                _check_string(diags, f"{where}.{k}", entry[k])
        for k in ("service_data_valid", "service_data"):
            if k in entry and not _is_int(entry[k]):
                diags.append(Diagnostic("error", "service-field-type",
                                        f"{where}.{k} must be an integer"))
        if "dcomment" in entry:
            _check_string(diags, f"{where}.dcomment", entry["dcomment"], required=False)

        prov = entry.get("provider")
        name = entry.get("service")
        if strict and isinstance(prov, str) and isinstance(name, str):
            full = f"{prov}/{name}"
            if prov not in KNOWN_PROVIDERS:
                diags.append(Diagnostic("warn", "provider-unseen",
                                        f"{where}: provider '{prov}' not in the "
                                        f"measured vocabulary {sorted(KNOWN_PROVIDERS)}"))
            elif name not in KNOWN_SERVICES:
                diags.append(Diagnostic("warn", "service-unseen",
                                        f"{where}: service '{name}' not in the "
                                        f"measured vocabulary {sorted(KNOWN_SERVICES)}"))
            table.append({
                "index": i,
                "provider": prov,
                "service": name,
                "service_full": full,
                "service_data_valid": entry.get("service_data_valid"),
                "service_data": entry.get("service_data"),
                "dcomment": entry.get("dcomment"),
            })

    summary["service_count"] = len(svc)
    summary["services"] = table

    if table:
        first = table[0]["service_full"]
        if first != IMPLICIT_SERVICE:
            diags.append(Diagnostic(
                "info", "servreg-not-first",
                f"first service is '{first}'; qcom_pdm_add_domain() adds "
                f"'{IMPLICIT_SERVICE}' implicitly and manifests list it first"))
        # qcom_pd_mapper.c models extra services per *domain*, not per file,
        # so duplicates are meaningless to the consumer.
        fulls = [t["service_full"] for t in table]
        if len(fulls) != len(set(fulls)):
            diags.append(Diagnostic("warn", "duplicate-service",
                                    f"duplicate service entries: {fulls}"))

    # --- derived: what the kernel would answer ---------------------------
    if "domain" in summary:
        extras = [t["service_full"] for t in table if t["service_full"] != IMPLICIT_SERVICE]
        summary["kernel_services_for_domain"] = [IMPLICIT_SERVICE] + extras

    return diags, summary


# ---------------------------------------------------------------------------
# Stem taxonomy (measurement, cross-checked against the kernel table)
# ---------------------------------------------------------------------------

#: suffix -> subdomain, established by measuring 53 real manifests and
#: cross-checking every derived (domain, instance, services) triple against
#: qcom_pd_mapper.c (0 contradictions).
#:
#: Grammar (measured, analysis §3.2): the stem is ``<subsystem>`` + an
#: OPTIONAL ``u`` infix + a role letter. ``root_pd`` never takes the ``u``
#: infix; every non-root sub-domain does — except ``sensor_pd``, which also
#: ships in a bare ``s`` spelling (``adsps`` vs ``slpius``). Both spellings
#: are byte-identical apart from the domain/instance fields, so this is a
#: naming inconsistency in the vendor's own generator, not a semantic
#: difference. Why is [OPEN].
SUFFIX_SUBDOMAIN = {
    "r": "root_pd",
    "s": "sensor_pd",
    "us": "sensor_pd",     # slpi's spelling of the same sub-domain
    "ua": "audio_pd",
    "uo": "ois_pd",
    "uw": "wlan_pd",
}

#: Stems that are role-named rather than suffix-derived.
ROLE_STEMS = {
    "battmgr": ("adsp", "charger_pd"),
    "wlanpdr": ("modem", "root_pd"),
}

STEM_DOMAIN = {
    "adsp": "adsp",
    "cdsp": "cdsp",
    "slpi": "slpi",
    "modem": "modem",
}

#: Longest-first so that "slpius" tries 'us' before 's'.
_SUFFIX_ORDER = sorted(SUFFIX_SUBDOMAIN, key=len, reverse=True)

#: Synthetic-fixture marker (``adspr_gen2``, ``modemr_gen3_pdr``). Real
#: device stems never contain an underscore, so stripping this cannot mask
#: a real naming violation.
_FIXTURE_SUFFIX_RE = re.compile(r"_gen\d+(_pdr)?$")


def classify_stem(stem):
    """Derive (domain, subdomain) from a filename stem, if derivable.

    A synthetic-fixture suffix (``_genN``, ``_genN_pdr``) is stripped first
    so that generated fixtures keep the real naming semantics; a real device
    stem never contains an underscore.

    Returns dict with keys domain/subdomain/suffix/resolved/note.
    """
    out = {"stem": stem, "domain": None, "subdomain": None,
           "suffix": None, "resolved": False, "note": ""}

    bare = _FIXTURE_SUFFIX_RE.sub("", stem)
    if bare != stem:
        out["fixture_suffix"] = stem[len(bare):]

    if bare in ROLE_STEMS:
        dom, sub = ROLE_STEMS[bare]
        out.update(domain=dom, subdomain=sub, suffix=None, resolved=True,
                   note="role-named manifest, no suffix")
        return out

    base = None
    for cand in sorted(STEM_DOMAIN, key=len, reverse=True):
        if bare.startswith(cand):
            base = cand
            break
    if base is None:
        out["note"] = "unrecognised stem prefix"
        return out

    suffix = bare[len(base):]
    out["domain"] = STEM_DOMAIN[base]
    out["suffix"] = suffix
    if suffix in SUFFIX_SUBDOMAIN:
        out["subdomain"] = SUFFIX_SUBDOMAIN[suffix]
        out["resolved"] = True
        out["u_infix"] = suffix.startswith("u")
    else:
        out["note"] = f"unrecognised suffix '{suffix}'"
    return out


# ---------------------------------------------------------------------------
# Top-level parse
# ---------------------------------------------------------------------------

def parse_bytes(raw):
    """Parse manifest bytes. Raises JsnError if not JSON at all."""
    if not raw:
        raise JsnError("empty file")
    body = raw
    text = None
    for enc in ("utf-8", "utf-8-sig"):
        try:
            text = body.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise JsnError("not valid UTF-8")
    if text.startswith("\ufeff"):
        text = text[1:]
    # pd-mapper's parser tolerates a trailing newline; json.loads does too.
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        raise JsnError(f"not valid JSON: {exc}") from exc


def probe(path, *, strict=True):
    """Probe one file. Returns a report dict; never raises for bad content."""
    report = {"file": path, "ok": False, "diagnostics": []}
    if not os.path.isfile(path):
        report["diagnostics"].append(
            Diagnostic("error", "not-a-file", f"{path} is not a regular file").as_dict())
        report["exit"] = 2
        return report

    with open(path, "rb") as fh:
        raw = fh.read()
    framing = inspect_framing(raw)
    report["framing"] = framing
    report["stem"] = os.path.basename(path)
    for ext in PD_MAPPER_EXTENSIONS:
        if path.endswith(ext):
            report["stem"] = os.path.basename(path)[: -len(ext)]
            break
    report["taxonomy"] = classify_stem(report["stem"])

    try:
        doc = parse_bytes(raw)
    except JsnError as exc:
        report["diagnostics"].append(
            Diagnostic("error", "parse", str(exc)).as_dict())
        report["exit"] = 2
        return report

    diags, summary = validate(doc, strict=strict)
    report["summary"] = summary

    # --- byte-framing conventions (measurements of the family) -----------
    # Not consumer requirements: pd-mapper accepts either. These are
    # deviations from the dominant convention, hence warn/info only.
    if framing["bom"]:
        diags.append(Diagnostic("warn", "bom",
                                "file begins with a UTF-8 BOM; no measured "
                                "fleet file carries one"))
    if framing["crlf_lines"]:
        diags.append(Diagnostic("warn", "crlf-lines",
                                f"{framing['crlf_lines']} CRLF line endings; "
                                "fleet convention is LF"))
    if framing["indent_width"] != 4:
        diags.append(Diagnostic("info", "indent",
                                f"indent width {framing['indent_width']}, fleet "
                                "convention is 4"))
    if framing["trailing_newline"]:
        diags.append(Diagnostic("info", "trailing-newline",
                                "file ends with a newline; most measured fleet "
                                "files do not (wlanpdr.jsn is the exception)"))

    report["diagnostics"].extend(d.as_dict() for d in diags)

    # Cross-check the filename against the declared domain.
    tax = report["taxonomy"]
    if tax["resolved"] and "domain" in summary:
        want = tax["domain"]
        got = summary["domain"].split("/")[1] if "/" in summary["domain"] else None
        if want != got:
            report["diagnostics"].append(Diagnostic(
                "error", "stem-domain-mismatch",
                f"filename stem implies domain '{want}' but sr_domain says "
                f"'{got}'").as_dict())
        want_sub = tax["subdomain"]
        got_sub = summary["subdomain"]
        if want_sub != got_sub:
            report["diagnostics"].append(Diagnostic(
                "error", "stem-subdomain-mismatch",
                f"filename suffix implies subdomain '{want_sub}' but sr_domain "
                f"says '{got_sub}'").as_dict())

    report["ok"] = not any(d["level"] == "error" for d in report["diagnostics"])
    report["exit"] = 0 if report["ok"] else 1
    return report


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_text(report):
    lines = []
    fr = report.get("framing", {})
    lines.append(f"file      : {report['file']}")
    if fr:
        lines.append(f"bytes     : {fr['bytes']}  md5 {fr['md5']}")
        lines.append(f"framing   : {fr['line_ending']} lines, indent "
                     f"{fr['indent_width']}, bom {fr['bom']}, "
                     f"trailing_newline {fr['trailing_newline']}")
    tax = report.get("taxonomy", {})
    if tax.get("resolved"):
        lines.append(f"stem      : {tax['stem']} -> {tax['domain']}/"
                     f"{tax['subdomain']} (suffix '{tax['suffix']}')")
    elif tax:
        lines.append(f"stem      : {tax['stem']} ({tax['note']})")

    s = report.get("summary", {})
    if s:
        dom = s.get("domain", "?")
        lines.append(f"domain    : {dom}  instance {s.get('qmi_instance_id', '?')}")
        if s.get("sr_version"):
            lines.append(f"sr_version: {s['sr_version']} "
                         f"(wire 0x{s.get('sr_version_wire', 0):04x})")
        lines.append("")
        lines.append(f"  {'#':>2}  {'provider/service':24} {'dvalid':>6} {'data':>5}  dcomment")
        for t in s.get("services", []):
            dc = t.get("dcomment")
            lines.append(f"  {t['index']:>2}  {t['service_full']:24} "
                         f"{str(t.get('service_data_valid')):>6} "
                         f"{str(t.get('service_data')):>5}  "
                         f"{'yes' if dc else '-'}")
        lines.append("")
        lines.append(f"services  : {s.get('service_count')}")

    diags = report.get("diagnostics", [])
    if diags:
        lines.append("")
        for d in diags:
            lines.append(f"  [{d['level']:5}] {d['code']}: {d['message']}")
    lines.append("")
    lines.append(f"result    : {'OK' if report.get('ok') else 'FAILED'} "
                 f"(exit {report.get('exit')})")
    return "\n".join(lines)


def render_brief(report):
    s = report.get("summary", {})
    fr = report.get("framing", {})
    tax = report.get("taxonomy", {})
    dom = s.get("domain", "?")
    n = s.get("service_count", 0)
    errs = sum(1 for d in report.get("diagnostics", []) if d["level"] == "error")
    warns = sum(1 for d in report.get("diagnostics", []) if d["level"] == "warn")
    verdict = "OK" if report.get("ok") else "FAIL"
    return (f"{os.path.basename(report['file'])}: {fr.get('bytes','?')}B "
            f"{dom} inst={s.get('qmi_instance_id','?')} services={n} "
            f"stem={tax.get('stem')} "
            f"[{verdict} {errs}E/{warns}W]")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Clean-room parser/validator for Qualcomm *.jsn PDR "
                    "service-registry manifests.")
    ap.add_argument("file", help="path to a .jsn manifest")
    ap.add_argument("--json", metavar="OUT.json", help="write the full report as JSON")
    ap.add_argument("--brief", action="store_true", help="one-line summary")
    ap.add_argument("--quiet", action="store_true", help="suppress stdout")
    ap.add_argument("--allow-crlf", action="store_true",
                    help="treat CRLF line endings as an info, not a warning "
                         "(some redistributions normalise to CRLF)")
    args = ap.parse_args(argv)

    report = probe(args.file)

    if args.allow_crlf:
        for d in report["diagnostics"]:
            if d["code"] == "crlf-lines":
                d["level"] = "info"

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2, sort_keys=True)
            fh.write("\n")

    if not args.quiet:
        print(render_brief(report) if args.brief else render_text(report))

    return report["exit"]


if __name__ == "__main__":
    sys.exit(main())
