#!/usr/bin/env python3
"""prima_nv_probe.py — clean-room structural parser for the Qualcomm PRIMA
WCNSS WLAN NVRAM container (``WCNSS_wlan_nv.bin`` /
``WCNSS_qcom_wlan_nv.bin``): the "nv.bin template stream" format consumed by
the downstream prima driver's wlan_nv_parser.c.

Format summary (all from GPL sources, see CLEAN-ROOM STATEMENT):
  * file[0,4) = nvValidityBitmap (v_U32); 0xFFFFFFFF = every field valid
    (DEFAULT_NV_VALIDITY_BITMAP);
  * file[4,8) read as u32: 0xCAFEBABE (MAGIC_NUMBER) -> "NV3" template-
    stream format: a sequence of streams, each = [u16 little-endian length]
    followed by that many bytes;
      - stream byte 0 = stream header: bit7 1=template / 0=data;
      - template streams: bit6 1=table-template / 0=enum-template;
        table-template = [hdr, tableId(b6:0), then 4..7-byte field records:
        name[2], fieldId, storageType(0..3=SINGULAR/ARRAY_1..3) + 0..3 size
        bytes where size bytes pack (high2<<7|low7) values];
        enum-template = [hdr, enumId(b6:0), then 3-byte entries: name[2],
        value, peerValue];
      - data streams = [hdr, tableId(b6:0), values...];
      - tableId 0 = "table of all tables" (the name directory);
      - fieldId bit7: 0=table/enum reference, 1=basic data type (0=U8,1=U32,
        2=S8,3=S32,4=U16,5=S16).
    -> else -> "NV2" raw packed-struct format: the remainder is the packed
    sHalNvV2 image; the driver copies the whole chunk (vos_nv_parseV2bin);
    first block after the bitmap = sNvFields (72 bytes packed):
      productId(u16), productBands(u8), wlanNvRevId(u8: 0=WCN1312,
      1=WCN1314, 2=WCN3660/3680 class), numOfTxChains(u8), numOfRxChains(u8),
      macAddr[6], macAddr2[6], macAddr3[6], macAddr4[6], mfgSN[40],
      couplerType(u8), nvVersion(u8); everything after = sNvTables
      (RF calibration / regulatory tables), opaque to this probe.

The probe verifies the version decision tree exactly as the driver makes
it, walks streams in the template case, decodes the sNvFields identity
block in the raw case, and reports sha1-12 fingerprints of the
device-identifying values (MACs, serial number) without reproducing them.
It does NOT decode RF calibration values.

======================================================================
CLEAN-ROOM STATEMENT
Written 2026-11-18 from public GPL sources only:
  - prima driver drivers/staging/prima/CORE/VOSS/src/wlan_nv_stream_read.c
    (deCodeData: u16-LE length framing; CyanogenMod/android_kernel_oppo_msm8974
    @cm-12.1) and wlan_nv_parser.c (template/enum/data stream processing,
    _TABLE_FIELDS_POS=2, _TABLE_FIELD_MIN_LEN=4, _ENUM_MIN_LEN=3,
    _NV_TEMPLATE_ENUM_ENTRY_SIZE=3, storage-type sizes).
  - drivers/staging/prima/CORE/VOSS/inc/wlan_nv_template_internal.h
    (STREAM_HEADER_TYPE_MASK 0x80, STREAM_HEADER_TEMPLATE_TYPE_MASK 0x40,
    FIELD_ID_TYPE_MASK 0x80, FIELD_ID_TABLE_OR_ENUM_IDX_MASK 0x7f,
    _STORAGE_TYPE(b)=b&0x3, the field-record byte order, the tableId=0
    directory semantics, _NV_BIN_STREAM_* byte positions).
Prior art checked 2026-11-18 (RULE 0): WCNSS_Binary_Maker
(codeberg.org/LogicalErzor/WCNSS_Binary_Maker — a full parser/BUILDER for
this format with 55 pmOS device configs, bin<->JSON round-trip) EXISTS:
the lab does not rebuild a builder; the delta here is the per-device
*census* (which tables/fields the FP2 image carries, where per-device
data like MAC addresses lives, stream-level byte ranges) produced by an
independent probe written only from the kernel sources, usable to
cross-check that tool. No proprietary material was accessed during
development beyond the publicly distributed firmware file itself, which
is analysed, not redistributed.
======================================================================

Usage:
    python3 -I prima_nv_probe.py <nv.bin> [--json OUT] [--brief]

Exit status 0 on a fully-verified walk; 1 on framing errors.
"""

import argparse
import hashlib
import json
import math
import os
import struct
import sys

STORAGE_TYPES = ("SINGULAR", "ARRAY_1", "ARRAY_2", "ARRAY_3")
BASIC_DATA_TYPES = ("U8", "U32", "S8", "S32", "U16", "S16")

STREAM_HEADER_TYPE_MASK = 0x80        # 1 = template, 0 = data
STREAM_HEADER_TEMPLATE_TYPE_MASK = 0x40  # 1 = table, 0 = enum
FIELD_ID_TYPE_MASK = 0x80             # 1 = basic data type, 0 = table/enum ref
FIELD_ID_TABLE_OR_ENUM_IDX_MASK = 0x7F
_TABLE_FIELDS_POS = 2
_TABLE_FIELD_MIN_LEN = 4
_ENUM_START_POS = 2
_ENUM_MIN_LEN = 3
_TABLE_NAME_LEN = 2


def entropy(data):
    if not data:
        return 0.0
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    n = len(data)
    return -sum((c / n) * math.log2(c / n) for c in counts if c)


def decode_size_pair(low, high):
    return ((((high >> 7) & 0x3) << 7) | (low & 0x7F))


def field_name_to_str(b):
    return bytes(b).decode("latin-1")


class PrimaNvProbe:
    def __init__(self, path):
        self.path = path
        with open(path, "rb") as f:
            self.data = f.read()
        self.errors = []
        self.streams = []

    def parse(self):
        data = self.data
        if len(data) < 8:
            self.errors.append("file smaller than validity bitmap + magic")
            return self.report()
        self.validity_bitmap = struct.unpack_from("<I", data, 0)[0]
        magic = struct.unpack_from("<I", data, 4)[0]
        if magic == 0xCAFEBABE:
            self.kind = "NV3-template-stream"
            self._parse_template_stream(data[8:])
        else:
            self.kind = "NV2-raw-struct"
            self._parse_raw_struct(data[4:])
        return self.report()

    # ---- NV2 raw packed-struct path (vos_nvitem.c else-branch) ----
    SNV_FIELDS_SIZE = 72  # 2+1+1+1+1 + 4*6 + 40 + 1 + 1, PACKED

    def _parse_raw_struct(self, body):
        self.raw = {"struct_image_bytes": len(body)}
        f = body[: self.SNV_FIELDS_SIZE]
        if len(f) < self.SNV_FIELDS_SIZE:
            self.errors.append("sNvFields truncated")
            return
        product_id = struct.unpack_from("<H", f, 0)[0]
        macs = {}
        for i, off in enumerate((6, 12, 18, 24), 1):
            m = bytes(f[off:off + 6])
            macs["macAddr%d" % i] = hashlib.sha1(m).hexdigest()[:12]
        mfgsn = bytes(f[30:70])
        self.raw.update({
            "product_id": product_id,
            "product_bands": f[2],
            "wlan_nv_rev_id": f[3],
            "wlan_nv_rev_id_note": "0=WCN1312, 1=WCN1314, >=2=WCN36xx class",
            "num_tx_chains": f[4],
            "num_rx_chains": f[5],
            "mac_sha1_12": macs,
            "mfg_sn_sha1_12": hashlib.sha1(mfgsn).hexdigest()[:12],
            "mfg_sn_entropy": round(entropy(mfgsn), 2),
            "coupler_type": f[70],
            "nv_version_byte": f[71],
            "tables_block_bytes": len(body) - self.SNV_FIELDS_SIZE,
        })

    # ---- NV3 template-stream path (wlan_nv_parser.c) ----
    def _parse_template_stream(self, data):
        pos = 0
        idx = 0
        while pos + 2 <= len(data):
            length = data[pos] | (data[pos + 1] << 8)
            start = pos
            pos += 2
            if length == 0:
                self.errors.append("stream %d: zero length at offset %d" % (idx, start))
                break
            if pos + length > len(data):
                self.errors.append("stream %d: truncated (need %d, have %d)"
                                   % (idx, length, len(data) - pos))
                length = len(data) - pos
            body = data[pos:pos + length]
            rec = {
                "idx": idx, "offset": start, "length": length,
                "sha1_12": hashlib.sha1(body).hexdigest()[:12],
                "entropy": round(entropy(body), 2),
            }
            if length >= 1:
                hdr = body[0]
                rec["is_template"] = bool(hdr & STREAM_HEADER_TYPE_MASK)
                if rec["is_template"]:
                    is_table = bool(hdr & STREAM_HEADER_TEMPLATE_TYPE_MASK)
                    rec["template_kind"] = "table" if is_table else "enum"
                    rec["table_or_enum_id"] = body[1] & FIELD_ID_TABLE_OR_ENUM_IDX_MASK if length >= 2 else None
                    rec.update(self._walk_template(body, is_table))
                else:
                    rec["template_kind"] = "data"
                    rec["table_id"] = body[1] & FIELD_ID_TABLE_OR_ENUM_IDX_MASK if length >= 2 else None
                    rec["data_bytes"] = length - 2
            self.streams.append(rec)
            pos += length
            idx += 1
        self.dir_tables = {}
        self.dir_enums = {}
        for s in self.streams:
            if s.get("table_or_enum_id") == 0 and s.get("template_kind") == "table":
                for f in s.get("fields", []):
                    if not f["is_basic_datatype"]:
                        self.dir_tables[f["id"]] = f["name"]
            if s.get("table_or_enum_id") == 0 and s.get("template_kind") == "enum":
                for f in s.get("entries", []):
                    self.dir_enums[f["id"]] = f["name"]
        self.framed = sum(2 + s["length"] for s in self.streams) == len(data)

    def _walk_template(self, body, is_table):
        out = {}
        if is_table:
            pos = _TABLE_FIELDS_POS
            fields = []
            while pos + _TABLE_FIELD_MIN_LEN <= len(body):
                f = {
                    "name": field_name_to_str(body[pos:pos + _TABLE_NAME_LEN]),
                    "raw_id": body[pos + 2],
                    "is_basic_datatype": bool(body[pos + 2] & FIELD_ID_TYPE_MASK),
                    "storage_type": STORAGE_TYPES[body[pos + 3] & 0x3],
                }
                rid = body[pos + 2]
                f["id"] = rid & FIELD_ID_TABLE_OR_ENUM_IDX_MASK
                if f["is_basic_datatype"]:
                    f["basic_type"] = BASIC_DATA_TYPES[rid & FIELD_ID_BASIC_DATA_TYPES_MASK] \
                        if (rid & FIELD_ID_TYPE_MASK) and (rid & 0x7F) < 6 else None
                else:
                    f["basic_type"] = None
                pos += _TABLE_FIELD_MIN_LEN
                st = body[pos - 1] & 0x3
                if st >= 1 and pos < len(body):
                    f["size1"] = decode_size_pair(body[pos], body[pos + 1]) if pos + 1 < len(body) else None
                    pos += 1
                if st >= 2 and pos + 1 < len(body):
                    f["size2"] = decode_size_pair(body[pos], body[pos + 1])
                    pos += 1
                if st >= 3 and pos + 1 < len(body):
                    f["size3"] = decode_size_pair(body[pos], body[pos + 1])
                    pos += 1
                fields.append(f)
            out["fields"] = fields
            out["field_count"] = len(fields)
        else:
            pos = _ENUM_START_POS
            entries = []
            while pos + 3 <= len(body):
                entries.append({
                    "name": field_name_to_str(body[pos:pos + _ENUM_MIN_LEN - 1]),
                    "id": body[pos + 2] & FIELD_ID_TABLE_OR_ENUM_IDX_MASK,
                    "value": body[pos + 2] & FIELD_ID_TABLE_OR_ENUM_IDX_MASK,
                })
                pos += 3
            out["entries"] = entries
            out["entry_count"] = len(entries)
        return out

    def report(self):
        r = {
            "file": os.path.basename(self.path),
            "size": len(self.data),
            "validity_bitmap": "0x%08x" % self.validity_bitmap,
            "validity_note": "0xFFFFFFFF = all fields valid (DEFAULT_NV_VALIDITY_BITMAP)",
            "kind": getattr(self, "kind", None),
            "errors": self.errors,
        }
        if getattr(self, "kind", None) == "NV2-raw-struct":
            r["snv_fields"] = getattr(self, "raw", None)
            return r
        tables = {}
        data_streams = []
        for s in self.streams:
            if s.get("template_kind") == "table" and s.get("table_or_enum_id") not in (None,):
                tid = s["table_or_enum_id"]
                tables.setdefault(tid, {"name": self.dir_tables.get(tid, "?"),
                                        "template_sha1_12": s["sha1_12"],
                                        "fields": [f["name"] for f in s.get("fields", [])]})
            elif s.get("template_kind") == "data":
                data_streams.append(s)
        r.update({
            "stream_count": len(self.streams),
            "framing_exact": self.framed,
            "tables": {("0x%02x" % k): v for k, v in sorted(tables.items())},
            "enum_directory": {hex(k): v for k, v in sorted(self.dir_enums.items())},
            "data_streams": [
                {"idx": s["idx"], "offset": s["offset"], "length": s["length"],
                 "table_id": s.get("table_id"),
                 "table_name": self.dir_tables.get(s.get("table_id"), "?"),
                 "sha1_12": s["sha1_12"], "entropy": s["entropy"]}
                for s in data_streams
            ],
            "streams": self.streams,
        })
        return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="clean-room prima WCNSS NV probe")
    ap.add_argument("nv")
    ap.add_argument("--json", help="write JSON report")
    ap.add_argument("--brief", action="store_true")
    args = ap.parse_args(argv)
    probe = PrimaNvProbe(args.nv)
    r = probe.parse()
    if args.json:
        with open(args.json, "w") as f:
            json.dump(r, f, indent=1)
    if r["kind"] == "NV2-raw-struct":
        sf = r.get("snv_fields") or {}
        print("%s: %d bytes, NV2 raw packed struct, validity=0x%08x, "
              "productId=%d revId=%d(%s) chains=%d/%d nvVersion=%d tablesBlock=%dB errors=%d"
              % (r["file"], r["size"], int(r["validity_bitmap"], 16),
                 sf.get("product_id", -1), sf.get("wlan_nv_rev_id", -1),
                 sf.get("wlan_nv_rev_id_note", ""), sf.get("num_tx_chains", -1),
                 sf.get("num_rx_chains", -1), sf.get("nv_version_byte", -1),
                 sf.get("tables_block_bytes", -1), len(r["errors"])))
    else:
        print("%s: %d bytes, %s, %d streams, framing_exact=%s tables=%d "
              "data_streams=%d errors=%d"
              % (r["file"], r["size"], r["kind"], r["stream_count"],
                 r["framing_exact"], len(r["tables"]), len(r["data_streams"]),
                 len(r["errors"])))
    return 1 if r["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
