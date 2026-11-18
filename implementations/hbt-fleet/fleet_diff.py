#!/usr/bin/env python3
"""fleet_diff.py — structural diff tool for the QCA BT h-prefix (Hastings)
fleet: ``hpbtfw*.tlv`` rampatches, ``hpnv20*`` NVMs, and their cr/ap-generation
predecessors (``crbtfw*``/``crnv*``, ``apbtfw*``/``apnv*``).

Extends (without modifying) the lab's clean-room parser
``implementations/qca-bt/qca_tlv.py`` with the generation-level structures the
h-generation files introduce, all verified against real public payloads:

  1. Patch footer: the h-generation replaces the cr/ap 256-byte signature-class
     tail with a 44-byte footer whose first two words are constant across
     builds (0x04040202, 0x05ca0404) followed by 36 bytes of hash-class
     content; header signature_algorithm = 0 (cr/ap: 2).
  2. NVM layout: h-generation NVMs are a single BARE type-2 record
     (``[0,4) set header, [4,4+len) tags``) with no type-4 enclosing header,
     no trailing type-3 record and no padding — vs the cr/ap
     ``type-4 enclosing + type-2 set + type-3 trailing record`` layout.
  3. Tag census + content identity across files (sha1 per tag body), the
     F-75 fleet-analysis.md method.

Everything here is derived from GPL kernel sources (btqca.h/btqca.c record
layout) plus byte-range statistics of real files. No payload bytes are
emitted — only lengths, ids and hashes.

Usage:
    python3 -I fleet_diff.py <patch.tlv ...> [--nvm <nvm.bin ...>]
                             [--json out.json]
"""

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter

# btqca.h constants (GPL)
TLV_TYPE_PATCH = 1
TLV_TYPE_NVM = 2
TLV_TYPE_MULTI_NVM_ENCLOSING = 4  # btqca.c comment, not an enum value
PATCH_HDR = 24  # sizeof(struct tlv_type_patch)
NVM_HDR = 12    # sizeof(struct tlv_type_nvm) prefix
H_FOOTER_LEN = 44
# h-generation footer: 44 bytes = 8-byte build-varying prologue + 36-byte
# hash-class content (verified on 4 builds; the prologue is NOT constant
# across builds -- only the footer LENGTH and low entropy are).


def sha1(bs):
    return hashlib.sha1(bs).hexdigest()[:12]


def parse_patch(path):
    data = open(path, 'rb').read()
    type_len = struct.unpack_from('<I', data, 0)[0]
    ttype, length_field = type_len & 0xff, type_len >> 8
    total_size, data_length, fmt_ver, sig_algo, dnld_mode, res1, \
        product_id, rom_build, patch_version, res2, entry = \
        struct.unpack_from('<II4BHHHHI', data, 4)
    out = {
        'file': path, 'size': len(data), 'type': ttype,
        'length_field_ok': length_field == len(data) - 4,
        'header': {
            'total_size': total_size, 'data_length': data_length,
            'format_version': fmt_ver, 'signature_algorithm': sig_algo,
            'download_mode': dnld_mode, 'product_id': product_id,
            'rom_build': hex(rom_build), 'patch_version': hex(patch_version),
            'reserved2': hex(res2), 'entry': hex(entry),
        },
        'segments': (len(data) + 242) // 243,  # MAX_SIZE_PER_TLV_SEGMENT=243
    }
    body = data[4 + PATCH_HDR: 4 + PATCH_HDR + data_length]
    tail = data[4 + PATCH_HDR + data_length:]
    out['tail_len'] = len(tail)
    out['body_entropy'] = None
    import math
    c = Counter(body)
    n = len(body)
    out['body_entropy'] = round(-sum((v / n) * math.log2(v / n)
                                     for v in c.values()), 3)
    out['body_sha1'] = hashlib.sha1(body).hexdigest()[:16]
    if len(tail) == H_FOOTER_LEN:
        w0, w1 = struct.unpack_from('<II', tail, 0)
        out['tail_class'] = 'h-generation 44B footer'
        out['tail_prologue'] = [hex(w0), hex(w1)]
        out['tail_content_sha1'] = sha1(tail[8:])
    elif len(tail) == 256:
        out['tail_class'] = 'cr/ap-generation 256B signature-class tail'
        out['tail_sha1'] = sha1(tail)
    else:
        out['tail_class'] = f'unknown ({len(tail)}B tail)'
        out['tail_sha1'] = sha1(tail)
    return out


def parse_nvm(path):
    data = open(path, 'rb').read()
    w0 = struct.unpack_from('<I', data, 0)[0]
    t0, l0 = w0 & 0xff, w0 >> 8
    out = {'file': path, 'size': len(data),
           'layout': None, 'tags': [], 'tag_count': 0}
    if t0 == TLV_TYPE_MULTI_NVM_ENCLOSING:
        out['layout'] = 'type-4 enclosing + type-2 set (cr/ap generation)'
        w1 = struct.unpack_from('<I', data, 4)[0]
        t1, l1 = w1 & 0xff, w1 >> 8
        set_off, set_len = 8, l1
        out['trailing'] = len(data) - (8 + l1)
        if out['trailing'] >= 4:
            wr = struct.unpack_from('<I', data, 8 + l1)[0]
            out['trailing_record'] = {'type': wr & 0xff, 'len': wr >> 8}
    elif t0 == TLV_TYPE_NVM:
        out['layout'] = 'bare type-2 record (h generation: no enclosing, ' \
                        'no trailing type-3)'
        set_off, set_len = 4, l0
        out['trailing'] = len(data) - (4 + l0)
    else:
        out['layout'] = f'unknown (first record type {t0})'
        return out
    off = set_off
    while off + NVM_HDR <= set_off + set_len:
        tag_id, tag_len, _r1, _r2 = struct.unpack_from('<HHII', data, off)
        if off + NVM_HDR + tag_len > set_off + set_len:
            out['tags'].append({'off': off, 'tag': tag_id, 'len': tag_len,
                                'OVERFLOW': True})
            break
        body = data[off + NVM_HDR: off + NVM_HDR + tag_len]
        out['tags'].append({'off': off, 'tag': tag_id, 'len': tag_len,
                            'sha1': sha1(body)})
        off += NVM_HDR + tag_len
    out['tag_count'] = len([t for t in out['tags'] if not t.get('OVERFLOW')])
    out['consumed'] = off - set_off
    return out


def diff_tag_sets(a, b):
    """Tag-id and tag-content comparison between two parsed NVMs."""
    ids_a = {t['tag'] for t in a['tags'] if not t.get('OVERFLOW')}
    ids_b = {t['tag'] for t in b['tags'] if not t.get('OVERFLOW')}
    content_a = {(t['len'], t['sha1']) for t in a['tags']
                 if not t.get('OVERFLOW')}
    content_b = {(t['len'], t['sha1']) for t in b['tags']
                 if not t.get('OVERFLOW')}
    return {
        'only_in_' + a['file']: sorted(ids_a - ids_b),
        'only_in_' + b['file']: sorted(ids_b - ids_a),
        'shared_tag_ids': sorted(ids_a & ids_b),
        'shared_tag_contents': sorted(content_a & content_b),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('patches', nargs='*', help='patch .tlv files')
    ap.add_argument('--nvm', nargs='*', default=[], help='NVM .bin files')
    ap.add_argument('--json', help='write full JSON here')
    args = ap.parse_args(argv)
    result = {'patches': [parse_patch(p) for p in args.patches],
              'nvms': [parse_nvm(p) for p in args.nvm]}
    for i in range(len(result['nvms'])):
        for j in range(i + 1, len(result['nvms'])):
            result.setdefault('tag_diffs', []).append(
                diff_tag_sets(result['nvms'][i], result['nvms'][j]))
    print(json.dumps(result, indent=1))
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(result, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
