#!/usr/bin/env python3
"""Tests for the h-generation (Hastings) BT fleet structures in fleet_diff.py
against synthetic fixtures built from documented structures only."""

import os
import subprocess
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
FIX = os.path.join(HERE, 'fixtures')
sys.path.insert(0, HERE)

import fleet_diff  # noqa: E402


class TestHFleetStructures(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, '-I', os.path.join(HERE, 'make_fixture.py')],
                       check=True, capture_output=True)

    def test_hgen_patch_tail_and_header(self):
        r = fleet_diff.parse_patch(os.path.join(FIX, 'hgen_patch.tlv'))
        self.assertEqual(r['type'], 1)
        self.assertTrue(r['length_field_ok'])
        self.assertEqual(r['header']['product_id'], 19)
        self.assertEqual(r['header']['signature_algorithm'], 0)
        self.assertEqual(r['header']['entry'], '0x0')
        self.assertEqual(r['header']['rom_build'], '0x200')
        self.assertEqual(r['tail_class'], 'h-generation 44B footer')
        self.assertEqual(r['tail_prologue'], ['0x4040202', '0x5ca0404'])
        self.assertEqual(r['segments'], (1024 + 24 + 44 + 4 + 242) // 243)

    def test_crap_patch_tail_and_header(self):
        r = fleet_diff.parse_patch(os.path.join(FIX, 'crap_patch.tlv'))
        self.assertEqual(r['header']['product_id'], 10)
        self.assertEqual(r['header']['signature_algorithm'], 2)
        self.assertEqual(r['header']['reserved2'], '0x8000')
        self.assertEqual(r['header']['entry'], '0x1b0e0')
        self.assertEqual(r['tail_class'],
                         'cr/ap-generation 256B signature-class tail')

    def test_hgen_nvm_bare_layout(self):
        r = fleet_diff.parse_nvm(os.path.join(FIX, 'hgen_nvm.bin'))
        self.assertEqual(r['layout'],
                         'bare type-2 record (h generation: no enclosing, '
                         'no trailing type-3)')
        self.assertEqual(r['trailing'], 0)
        self.assertEqual(r['tag_count'], 5)
        ids = [t['tag'] for t in r['tags']]
        self.assertEqual(ids[:3], [2, 17, 27])
        lengths = {t['tag']: t['len'] for t in r['tags']}
        self.assertEqual(lengths[2], 6)   # BD_ADDR still 6 bytes
        self.assertEqual(lengths[17], 6)  # h-generation HCI tag length
        self.assertEqual(lengths[27], 9)  # h-generation deep-sleep length
        self.assertIn(206, ids)           # extended tag id > 150

    def test_crap_nvm_enclosing_layout(self):
        r = fleet_diff.parse_nvm(os.path.join(FIX, 'crap_nvm.bin'))
        self.assertEqual(r['layout'],
                         'type-4 enclosing + type-2 set (cr/ap generation)')
        self.assertEqual(r['trailing_record']['type'], 3)
        self.assertEqual(r['trailing_record']['len'], 943)
        self.assertEqual(r['tag_count'], 3)
        lengths = {t['tag']: t['len'] for t in r['tags']}
        self.assertEqual(lengths[17], 9)  # cr/ap HCI tag length
        self.assertEqual(lengths[27], 1)  # cr/ap deep-sleep length

    def test_tag_diff_finds_generation_change(self):
        h = fleet_diff.parse_nvm(os.path.join(FIX, 'hgen_nvm.bin'))
        c = fleet_diff.parse_nvm(os.path.join(FIX, 'crap_nvm.bin'))
        d = fleet_diff.diff_tag_sets(h, c)
        # tag content sha1s must not collide across synthetic generations
        self.assertEqual(d['shared_tag_contents'], [])
        self.assertIn(206, d['only_in_' + h['file']])
        self.assertIn(27, d['shared_tag_ids'])  # id shared, content differs

    def test_real_fleet_parse_smoke(self):
        """If real (md5-verified) payloads are present in the scratch dir,
        the parser must reproduce the documented generation facts."""
        p = '/tmp/astro_v/payload/hpnv20.bin.r0s'
        if not os.path.exists(p):
            self.skipTest('real payload not available')
        r = fleet_diff.parse_nvm(p)
        self.assertTrue(r['layout'].startswith('bare type-2'))
        self.assertEqual(r['tag_count'], 60)
        p2 = '/tmp/astro_v/payload/hpbtfw20.tlv.r0s'
        r2 = fleet_diff.parse_patch(p2)
        self.assertEqual(r2['header']['product_id'], 19)
        self.assertEqual(r2['tail_class'], 'h-generation 44B footer')
        # DB-identical common build (cupid bluetooth partition image)
        p3 = '/tmp/astro_v/btimg/hpbtfw20.tlv'
        if os.path.exists(p3):
            r3 = fleet_diff.parse_patch(p3)
            self.assertEqual(r3['header']['patch_version'], '0x3ed8')
            self.assertEqual(r3['header']['product_id'], 19)
            self.assertEqual(r3['tail_prologue'], ['0x0', '0x10'])
            n3 = fleet_diff.parse_nvm('/tmp/astro_v/btimg/hpnv20.bin')
            self.assertEqual(n3['tag_count'], 61)
            self.assertTrue(n3['layout'].startswith('bare type-2'))


if __name__ == '__main__':
    unittest.main()
