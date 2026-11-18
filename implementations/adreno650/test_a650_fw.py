#!/usr/bin/env python3
"""Tests for a650_fw.py (GMU block chain, legacy raw image, SQE version
semantics) against synthetic fixtures built from documented structures."""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, 'fixtures')
sys.path.insert(0, HERE)

import a650_fw  # noqa: E402


class TestA650Fw(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, '-I', os.path.join(HERE, 'make_fixture.py')],
                       check=True, capture_output=True)

    def test_a650_block_chain(self):
        r = a650_fw.parse_gmu(os.path.join(FIX, 'a650_gmu.bin'))
        self.assertEqual(r['format'], 'block-chain (non-legacy a650-family '
                                      'loader)')
        self.assertTrue(r['chain_clean'])
        self.assertEqual(r['zero_size_blocks'], 2)
        regions = r['regions']
        self.assertEqual(regions['ITCM']['count'], 3)  # 2 markers + 1 block
        self.assertEqual(regions['ITCM']['bytes'], 0 + 0 + 256)
        self.assertEqual(regions['DTCM']['count'], 2)
        self.assertIn('icache', regions)
        # DTCM base used must be the a650-family one (0x10004000)
        self.assertEqual(regions['DTCM']['bytes'], 64 + 24)
        self.assertEqual(r['payload_blocks'], 4)
        self.assertEqual(r['manifest_blocks'], 2)

    def test_a619_legacy_raw(self):
        r = a650_fw.parse_gmu(os.path.join(FIX, 'a619_gmu.bin'))
        self.assertFalse(r['chain_clean'])
        self.assertIn('raw image', r['format'])
        self.assertTrue(r['legacy_size_candidate'])
        self.assertEqual(r['size'], 0x8000)
        self.assertEqual(r['first_words'][0], '0x43f80')

    def test_sqe_version_semantics(self):
        ok = a650_fw.parse_sqe(os.path.join(FIX, 'a650_sqe_ok.fw'))
        old = a650_fw.parse_sqe(os.path.join(FIX, 'a650_sqe_old.fw'))
        self.assertEqual(ok['lead_dword'], '0x0')
        self.assertTrue(ok['a650_check_pass'])
        self.assertFalse(old['a650_check_pass'])
        self.assertEqual(ok['driver_version_dword'], '0x16dd112')
        self.assertEqual(old['driver_version_dword'], '0x16dd093')

    def test_real_payload_smoke(self):
        """md5-verified real payloads in scratch must reproduce the
        documented facts (skipped when scratch is absent)."""
        import json
        for p, expect in [
            ('/tmp/astro_v/payload/a650_gmu.bin.pdx',
             {'chain_clean': True, 'block_count': 16}),
            ('/tmp/astro_v/payload/a650_sqe.fw.pdx',
             {'a650_check_pass': False}),
        ]:
            if not os.path.exists(p):
                self.skipTest('real payload not available')
            r = a650_fw.parse_gmu(p) if 'gmu' in p else a650_fw.parse_sqe(p)
            for k, v in expect.items():
                self.assertEqual(r[k], v, f'{p}: {k}')
            self.assertEqual(r['md5'],
                             'a2b9504e3d1cb8686ae7fcca21a11e1a'
                             if 'gmu' in p else
                             '353e247b2c4ea8c16c49cb31b574edc1')


if __name__ == '__main__':
    unittest.main()
