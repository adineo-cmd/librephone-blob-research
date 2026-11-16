#!/usr/bin/env python3
"""test_lpec.py — synthetic-fixture tests for the re-homed LPEC decoders.

CLEAN-ROOM STATEMENT
Written from the lab's published LPEC spec documents on 2026-11-16
(F-47/F-49/F-51 layout facts — see lpec_decoder.py header); no proprietary
material accessed. The bitstreams below are SELF-MADE, constructed from the
documented frame layout (bit targets 384/288/480/384 LP, 1024/768/1280/1024
SP; field order per F-51's layout table); no Sony sample is used or needed.
"""

import os
import struct
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import lpec_decoder as d3            # noqa: E402  (F-51 pass-3 parser)
import lpec_decoder_pass2 as d2      # noqa: E402  (F-49 pass-2 parser)


class BitWriter:
    """MSB-first bit writer — the documented LPEC pump order (F-49)."""

    def __init__(self):
        self.bits = []

    def write(self, value, n):
        for i in range(n - 1, -1, -1):
            self.bits.append((value >> i) & 1)
        return self

    def to_bytes(self):
        out = bytearray((len(self.bits) + 7) // 8)
        for i, b in enumerate(self.bits):
            if b:
                out[i >> 3] |= 1 << (7 - (i & 7))
        return bytes(out)


class BitReaderTests(unittest.TestCase):
    def test_msb_first_read(self):
        r = d3.BitReader(b"\xA5")  # 1010 0101
        self.assertEqual([r.read(1) for _ in range(8)], [1, 0, 1, 0, 0, 1, 0, 1])

    def test_skip_align(self):
        r = d3.BitReader(b"\x00\xFF\x00\x00\x00\x00\x00\x00\xFF")
        r.skip(8)
        self.assertEqual(r.read(8), 0xFF)
        r.align()
        self.assertEqual(r.pos, 16)


def lp_type0_frame(block=0, lsp_set=None, gains=(0, 0), exc=(0, 0), target=384):
    """Build a synthetic LP type-0 frame per the F-51 layout table.

    Returns the frame bits padded to exactly `target` bits with the
    documented tail-pad shape. Fields (F-51 layout, MSB-first):
      2b type=0 | 1b block | LSP set(s) 3x6 | gain sub1 7b (+6b shape if
      nonzero) | gain sub2 same | exc sub1 1b [+7b page] | exc sub2 same |
      sub1 pitch 7+6+6 | sub1 pulses | sub2 pitch 7+6+6 | sub2 pulses | pad
    Pulse budget = floor((T-C)/2) - exc_cost - 19 per subframe.
    """
    w = BitWriter()
    w.write(0, 2)
    w.write(block, 1)
    nsets = 2 if block else 1
    if lsp_set is None:
        lsp_set = [[1] * 3] * nsets  # any 6-bit groups (documented width 6)
    for s in lsp_set:
        for g in s:
            w.write(g, 6)
    exc_cost = 0
    for g in gains:
        if g:
            w.write(g, 7)
            w.write(1, 6)  # shape index (documented +6b when nonzero)
        else:
            w.write(0, 7)
        if g:
            exc_cost += 0
    for p in exc:
        w.write(p, 1)
        if p:
            w.write(3, 7)  # codebook page index (documented +7b when present)
            exc_cost += 8
        else:
            exc_cost += 1
    consumed = w.pos if hasattr(w, "pos") else len(w.bits)
    rem = target - consumed
    half = rem // 2
    i7 = [8 if e else 1 for e in exc]
    a0 = half - i7[0]
    a1 = half - i7[1]
    assert a0 >= 19 and a1 >= 19, (a0, a1)
    # sub1 pitch 7+6+6
    w.write(32, 7); w.write(5, 6); w.write(6, 6)
    w.write(0, a0 - 19)          # sub1 pulse block (opaque, derived size)
    w.write(33, 7); w.write(7, 6); w.write(8, 6)   # sub2 pitch
    w.write(0, a1 - 19)          # sub2 pulse block
    tail = target - len(w.bits)
    w.write(0, tail)
    return w.to_bytes(), len(w.bits)


class FrameLayoutTests(unittest.TestCase):
    """The documented layout, round-tripped through the F-51 parser."""

    def test_lp_type0_valid(self):
        blob, bits = lp_type0_frame()
        self.assertEqual(bits, 384)
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["type"], 0)
        self.assertEqual(f["bytes"], 48)         # documented frame_bytes[0]
        self.assertEqual(f["end_bit"], 384)
        self.assertEqual(f["tail_skip"], 3)      # exc cost 1+1 -> pad 2+1
        self.assertEqual(r.pos, 384)

    def test_lp_type0_dual_lsp_blocks(self):
        blob, _ = lp_type0_frame(block=1, gains=(0, 0))
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 48)
        self.assertEqual(len(f["lsp"]), 2)       # two LSP sets when block=1

    def test_lp_type0_with_excitation_pages(self):
        blob, _ = lp_type0_frame(exc=(1, 0))
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 48)
        self.assertEqual(f["exc"][0], [1, 3])    # page index read back
        self.assertEqual(f["tail_skip"], 9)      # (384-385-... parity) +8+1

    def test_lp_type1(self):
        w = BitWriter()
        w.write(1, 2)
        for g in [1] * 3:
            w.write(g, 6)                        # LSP 3x6
        w.write(0, 7)                            # gain sub2 (muted)
        consumed = len(w.bits)                   # 2 + 18 + 7 = 27
        a = d3.LP_CFG["targets"][1] - consumed   # 288 - 27 = 261
        w.write(32, 7); w.write(5, 6); w.write(6, 6)
        w.write(0, a - 19)
        blob = w.to_bytes()
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 36)         # documented frame_bytes[1]
        self.assertEqual(f["tail_skip"], 0)      # types 1/2/3 pad exactly 0

    def test_lp_type2(self):
        w = BitWriter()
        w.write(2, 2)
        for g in [2] * 3:
            w.write(g, 6)
        w.write(0, 7); w.write(0, 7)             # both gains muted
        c1 = len(w.bits)                         # 34
        rem1 = d3.LP_CFG["targets"][0] - c1      # 350
        a1 = rem1 // 2                           # 175
        w.write(32, 7); w.write(5, 6); w.write(6, 6)
        w.write(0, a1 - 19)
        c2 = c1 + a1
        a2 = d3.LP_CFG["targets"][2] - c2        # 480 - 209 = 271
        w.write(33, 7); w.write(7, 6); w.write(8, 6)
        w.write(0, a2 - 19)
        blob = w.to_bytes()
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 60)         # documented frame_bytes[2]

    def test_lp_type3(self):
        w = BitWriter()
        w.write(3, 2)
        for g in [3] * 3:
            w.write(g, 6)
        w.write(0, 7)
        a = d3.LP_CFG["targets"][3] - len(w.bits)  # 384 - 27 = 357
        w.write(32, 7); w.write(5, 6); w.write(6, 6)
        w.write(0, a - 19)
        blob = w.to_bytes()
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.LP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 48)

    def test_sp_type0_uses_sp_cfg(self):
        w = BitWriter()
        w.write(0, 2); w.write(0, 1)
        for g in [1] * 4:                        # SP: 4 LSP groups (F-51)
            w.write(g, 6)
        w.write(0, 8)                            # SP gain field is 8 bits
        w.write(0, 8)
        w.write(0, 1); w.write(0, 1)             # excitation absent x2
        consumed = len(w.bits)                   # 2+1+24+16+2 = 45
        rem = d3.SP_CFG["targets"][0] - consumed  # 1024 - 45 = 979
        half = rem // 2                          # 489
        a0 = half - 1
        a1 = half - 1
        w.write(32, 7); w.write(5, 6); w.write(6, 6)
        w.write(0, a0 - 19)
        w.write(33, 7); w.write(7, 6); w.write(8, 6)
        w.write(0, a1 - 19)
        w.write(0, d3.SP_CFG["targets"][0] - len(w.bits))
        blob = w.to_bytes()
        r = d3.BitReader(blob)
        f = d3.parse_frame(r, d3.SP_CFG)
        self.assertIsNone(f["invalid"])
        self.assertEqual(f["bytes"], 128)        # documented frame_bytes[0] SP


class StreamAndContainerTests(unittest.TestCase):
    def test_parse_stream_byte_closure(self):
        frames = [lp_type0_frame()[0],
                  lp_type0_frame(exc=(1, 0))[0],
                  lp_type0_frame()[0]]
        audio = b"".join(frames)
        parsed = d3.parse_stream(audio, d3.LP_CFG)
        self.assertEqual(len(parsed), 3)
        self.assertTrue(all(f["invalid"] is None for f in parsed))
        self.assertEqual(sum(f["bytes"] for f in parsed), len(audio))
        self.assertEqual(parsed[-1]["end_bit"], len(audio) * 8)

    def test_parse_stream_stops_on_invalid(self):
        # an all-0xFF frame parses as a structurally valid type-3 frame, so
        # invalidity is exercised through the documented pulse-budget guard
        # instead: a synthetic cfg whose type-0 target cannot fit the header
        # forces "pulse-budget-negative" (F-51's derived-budget invariant)
        cfg = dict(d3.LP_CFG)
        cfg["targets"] = [40, 288, 480, 384]
        audio = lp_type0_frame()[0] * 2
        parsed = d3.parse_stream(audio, cfg)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["invalid"], "pulse-budget-negative")

    def _packet_container(self, payloads, annotate=False):
        """Build a synthetic DVF/MSV-style packet container per F-47/F-51:
        1024-B packets from 0x400 (0x800 when a 1 KB 0xFF annotation block
        precedes), 10-B header, bytes[4:6] BE = payload bytes used."""
        head = bytearray(0x400)
        if annotate:
            head += b"\xFF" * 0x400
        blob = bytearray(head)
        for p in payloads:
            pkt = bytearray(1024)
            used = 10 + len(p)
            pkt[0] = 0
            pkt[2] = 0
            pkt[3] = 0x0A
            struct.pack_into(">H", pkt, 4, used)
            pkt[10:10 + len(p)] = p
            blob += pkt
        return bytes(blob)

    def test_extract_audio_from_0x400(self):
        # non-final packets must use the full 1024-byte area (sizes == 1024);
        # the audio is one continuous bitstream chunked at 1014 bytes (F-51:
        # frames straddle packet boundaries)
        f1 = lp_type0_frame()[0]
        f2 = lp_type0_frame(exc=(1, 0))[0]
        audio = f1 + f2 + b"\x00" * 1000          # 1096 B
        chunks = [audio[:1014], audio[1014:]]      # 1014 + 82
        data = self._packet_container(chunks)
        payloads, packets, endpos = d3.extract_audio(data)
        self.assertEqual(payloads, chunks)
        self.assertEqual(packets, [1024, 10 + 82])
        self.assertEqual(endpos, 0x400 + 2 * 1024)
        self.assertEqual(b"".join(payloads), audio)

    def test_extract_audio_annotation_block_skipped(self):
        p1 = lp_type0_frame()[0]
        data = self._packet_container([p1], annotate=True)
        payloads, packets, endpos = d3.extract_audio(data)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0], p1)
        self.assertEqual(endpos, 0x800 + 1024)

    def test_pass2_continuous_straddle_sp(self):
        """F-49/F-51: the stream is continuous and frames straddle packet
        boundaries — build two packets whose payloads do not tile on frame
        boundaries and confirm the straddle parse still closes."""
        def sp_type0():
            w = BitWriter()
            w.write(0, 2); w.write(0, 1)
            for g in [1] * 4:
                w.write(g, 6)
            w.write(0, 8); w.write(0, 8)
            w.write(0, 1); w.write(0, 1)
            consumed = len(w.bits)
            rem = d3.SP_CFG["targets"][0] - consumed
            half = rem // 2
            w.write(32, 7); w.write(5, 6); w.write(6, 6)
            w.write(0, half - 1 - 19)
            w.write(33, 7); w.write(7, 6); w.write(8, 6)
            w.write(0, half - 1 - 19)
            w.write(0, d3.SP_CFG["targets"][0] - len(w.bits))
            return w.to_bytes()

        f1, f2, f3 = sp_type0(), sp_type0(), sp_type0()
        audio = (f1 + f2 + f3) * 3 + sp_type0()[:24]   # 384*3 + 24 = 1176 B
        chunks = [audio[:1014], audio[1014:]]           # 1014 + 162
        data = self._packet_container(chunks)
        pkts = d2.audio_packets(data)
        self.assertEqual([p["used"] for p in pkts], [1024, 10 + 162])
        frames = d2.parse_frames(pkts, d2.MODES["lpec_sp_16000"])
        # 1176 * 8 / 1024 = 9.18 -> 9 full 1024-bit frames; the 1014-B first
        # packet area (8.11 frames) proves frame 8 straddles the boundary
        self.assertEqual(len(frames), 9)
        self.assertEqual([f["type"] for f in frames], [0] * 9)

    def test_pass2_lp_per_packet_reset(self):
        # LP mode uses per-packet framing in the pass-2 model (F-49):
        # each packet's payload area is framed independently at 48-B steps.
        f = lp_type0_frame()[0]
        data = self._packet_container([f + f + f])   # 3 x 48 B in one packet
        pkts = d2.audio_packets(data)
        frames = d2.parse_frames(pkts, d2.MODES["lpec_lp_6000"])
        self.assertEqual(len(frames), 3)
        self.assertTrue(all(fr["type"] == 0 for fr in frames))


class ConfigTests(unittest.TestCase):
    def test_documented_mode_tables(self):
        # F-51: LP targets 384/288/480/384 (48/36/60/48 B), SP 1024/768/1280/1024
        # (128/96/160/128 B); LSP groups 3 (LP) / 4 (SP); gain 7 (LP) / 8 (SP)
        self.assertEqual(d3.LP_CFG["targets"], [384, 288, 480, 384])
        self.assertEqual(d3.LP_CFG["frame_bytes"], [48, 36, 60, 48])
        self.assertEqual(d3.SP_CFG["targets"], [1024, 768, 1280, 1024])
        self.assertEqual(d3.SP_CFG["frame_bytes"], [128, 96, 160, 128])
        self.assertEqual((d3.LP_CFG["lsp_groups"], d3.SP_CFG["lsp_groups"]), (3, 4))
        self.assertEqual((d3.LP_CFG["gain_bits"], d3.SP_CFG["gain_bits"]), (7, 8))
        self.assertEqual(d2.MODES["lpec_lp_6000"]["frame_bytes"], 48)
        self.assertEqual(d2.MODES["lpec_sp_16000"]["frame_bytes"], 128)


if __name__ == "__main__":
    unittest.main(verbosity=2)
