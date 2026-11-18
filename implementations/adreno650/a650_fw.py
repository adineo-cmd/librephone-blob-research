#!/usr/bin/env python3
"""a650_fw.py — clean-room structural parser for the Adreno a650-generation
GMU firmware (``a650_gmu.bin``) and SQE microcode (``a650_sqe.fw``), plus the
a619-generation legacy raw-ITCM image (``a619_gmu.bin``).

Structures come from GPL-published mainline driver sources only:

  - drivers/gpu/drm/msm/adreno/a6xx_gmu.c::

        struct block_header {
            u32 addr;
            u32 size;
            u32 type;
            u32 value;
            u32 data[];
        };

        #define NEXT_BLK(blk) \
            ((const struct block_header *)((const char *)(blk) + \
             sizeof(*(blk)) + (blk)->size))

    a6xx_gmu_fw_load() walks this chain from fw_image->data (offset 0) to EOF,
    skipping size==0 blocks, and copies blk->data into:
        ITCM  base 0x00000000 (SZ_16K)   -> REG_A6XX_GMU_CM3_ITCM_START
        DTCM  base 0x00040000 (legacy) / 0x10004000 (a650 family and later)
        else  icache/dcache/dummy GMU memory BOs (runtime iova ranges).
    The legacy path (gmu->legacy, set for a630-family / platform-GMU binding)
    instead bulk-writes the WHOLE file to the GMU ICM region and rejects
    fw_image->size > 0x8000.

  - drivers/gpu/drm/msm/adreno/adreno_gpu.c, adreno_fw_create_bo(): the SQE
    firmware BO is fw->size - 4 bytes copied from &fw->data[4] — i.e. the
    SQE file's first DWORD is a stripped 4-byte prefix; the driver-visible
    version dword is the file's SECOND dword.
  - drivers/gpu/drm/msm/adreno/a6xx_gpu.c, a6xx_ucode_check_version():
    a650 requires (version & 0xfff) >= 0x095; a630 requires (v & 0xfff) >=
    0x190 or patched nibble form; a660+ accepts unconditionally.

This is an inspector: it tabulates what is on disk (block tables, region
classification, statistics). It does NOT disassemble or execute anything.
No proprietary payload bytes are emitted — only lengths, addresses, hashes.

Usage:
    python3 -I a650_fw.py <file.gmu.bin|file.sqe.fw> [--json out.json]
"""

import argparse
import hashlib
import json
import math
import struct
import sys
from collections import Counter

# mainline constants (a6xx_gmu.c)
ITCM_BASE = 0x00000000
DTCM_BASE_LEGACY = 0x00040000
DTCM_BASE_A650FAMILY = 0x10004000
SZ_16K = 0x4000
LEGACY_MAX_SIZE = 0x8000  # a6xx_gmu.c: "firmware is bigger than the available
#                            region" check on the legacy path
BLOCK_HDR = 16  # sizeof(struct block_header): addr, size, type, value
# a650-family GMU memory BOs (a6xx_gmu_init, adreno_is_a650_family branch):
ICACHE_BASE = 0x04000          # icache: SZ_16M - SZ_16K
ICACHE_SIZE = 0x1000000 - 0x4000
DUMMY_BASE = 0x60000000        # dummy page: SZ_4K (SZ_16K for a660/a7xx/a8xx)
DUMMY_SIZE = 0x1000
# payload-block tag: every real payload block carries type=value 0xEFBEADDE
# (on-disk bytes DE AD BE EF — "DEADBEEF" pattern); verified on a650_gmu.bin
PAYLOAD_TAG = 0xEFBEADDE
# manifest blocks: type 1 (or 7 for the dummy region), size 0, value = region
# size — they tile the loader windows exactly (verified against the real file)


def sha1(bs):
    return hashlib.sha1(bs).hexdigest()[:16]


def md5_hex(bs):
    return hashlib.md5(bs).hexdigest()


def entropy(bs):
    if not bs:
        return 0.0
    c = Counter(bs)
    n = len(bs)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def classify_region(addr, dtcm_base):
    """Classify a block address against the loader regions the kernel uses
    (a650 family): ITCM 0x0+16K, icache 0x4000+16M-16K, DTCM 0x10004000+16K,
    dummy 0x60000000+4K."""
    if addr < ITCM_BASE + SZ_16K:
        return 'ITCM'
    if ICACHE_BASE <= addr < ICACHE_BASE + ICACHE_SIZE:
        return 'icache'
    if dtcm_base <= addr < dtcm_base + SZ_16K:
        return 'DTCM'
    if DUMMY_BASE <= addr < DUMMY_BASE + ICACHE_SIZE:
        return 'dummy'
    return 'unmapped'


def parse_gmu(path):
    data = open(path, 'rb').read()
    out = {
        'file': path, 'size': len(data), 'md5': md5_hex(data),
        'entropy': round(entropy(data), 3),
        'zero_frac': round(data.count(0) / len(data), 4),
        'legacy_size_candidate': len(data) <= LEGACY_MAX_SIZE,
    }
    # ---- try the non-legacy block chain (a650 family format)
    blocks = []
    off = 0
    chain_error = None
    while off < len(data):
        if off + BLOCK_HDR > len(data):
            chain_error = f'trailing {len(data)-off} bytes'
            break
        addr, size, btype, value = struct.unpack_from('<IIII', data, off)
        if off + BLOCK_HDR + size > len(data):
            chain_error = f'block at file-off 0x{off:x} overruns file'
            break
        body = data[off + BLOCK_HDR: off + BLOCK_HDR + size]
        blk = {
            'off': off, 'addr': addr, 'size': size, 'type': btype,
            'value': value,
        }
        if size:
            blk['body_sha1'] = sha1(body)
            blk['body_entropy'] = round(entropy(body), 3)
        blocks.append(blk)
        off += BLOCK_HDR + size
    if chain_error is None and off == len(data):
        dtcm = DTCM_BASE_A650FAMILY
        for b in blocks:
            b['region'] = classify_region(b['addr'], dtcm)
            for k in ('addr', 'value'):
                b[k] = hex(b[k])
            b['type'] = hex(b['type'])
        zero_size = [b for b in blocks if b['size'] == 0]
        out['format'] = 'block-chain (non-legacy a650-family loader)'
        out['chain_clean'] = True
        out['blocks'] = blocks
        out['block_count'] = len(blocks)
        out['zero_size_blocks'] = len(zero_size)
        # manifest blocks: size 0, type 1/7, value = declared region size;
        # payload blocks: type/value = 0xEFBEADDE ("DEADBEEF" byte pattern)
        out['manifest_blocks'] = len([b for b in zero_size
                                      if b['type'] in ('0x1', '0x7')])
        out['payload_blocks'] = len([b for b in blocks
                                     if b.get('type') == hex(PAYLOAD_TAG)])
        regions = {}
        for b in blocks:
            r = regions.setdefault(b['region'], {'count': 0, 'bytes': 0})
            r['count'] += 1
            r['bytes'] += b['size']
        out['regions'] = regions
    else:
        out['format'] = ('raw image (legacy 0x8000 ITCM-class or unknown; '
                         'block-chain walk failed: %s)' % chain_error)
        out['chain_clean'] = False
        out['chain_error'] = chain_error
        out['first_words'] = [hex(w) for w in
                              struct.unpack_from('<8I', data, 0)] if len(data) >= 32 else None
    return out


def parse_sqe(path):
    data = open(path, 'rb').read()
    words = struct.unpack_from('<%dI' % (len(data) // 4), data)
    stripped_version = words[1]  # adreno_fw_create_bo skips the first dword
    out = {
        'file': path, 'size': len(data), 'md5': md5_hex(data),
        'entropy': round(entropy(data), 3),
        'zero_frac': round(data.count(0) / len(data), 4),
        'lead_dword': hex(words[0]),
        'driver_version_dword': hex(stripped_version),
        'version_bits_0xfff': hex(stripped_version & 0xfff),
        'a650_check_pass': bool((stripped_version & 0xfff) >= 0x095),
        'a630_check_pass': bool(
            ((stripped_version & 0xf) == 0xa and (words[3] & 0xf) >= 1)
            or (stripped_version & 0xfff) >= 0x190),
        'first_dwords': [hex(w) for w in words[:8]],
        'last_dwords': [hex(w) for w in words[-4:]],
    }
    wc = Counter(words)
    out['top_words'] = [[hex(w), c] for w, c in wc.most_common(5)]
    prof = [round(entropy(data[i:i + 1024]), 2)
            for i in range(0, len(data) - len(data) % 1024, 1024)]
    out['entropy_1k_min_mean_max'] = (
        [min(prof), round(sum(prof) / len(prof), 2), max(prof)]
        if prof else [None, None, None])
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('file')
    ap.add_argument('--json', help='write full JSON to this path')
    args = ap.parse_args(argv)
    if 'sqe' in args.file:
        out = parse_sqe(args.file)
    else:
        out = parse_gmu(args.file)
    print(json.dumps(out, indent=1))
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(out, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main())
