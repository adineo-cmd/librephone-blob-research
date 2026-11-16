## Fleet deep-RE addendum (2026-11-16, same session, post-Phase-4)

Continued into actual blob RE per the leverage-first order. First pass
delivered: the OnePlus 6 `bt.img` partition is a FAT16 volume carrying
the entire QCA BT patch/NVM fleet; all six top-20 md5s extract
byte-exactly from it (two double-verified against linux-firmware); the
container format is decoded from public GPL btqca structs and verified
10/10 against real bytes (patch headers with per-generation entry
addresses 0x1b0e0/0x1b15c/0x209e4, one exact-closing NVM tag set + one
unknown type-3 set each, first public NVM tag enumeration 9→45 tags).
Deliverables: `blob-matrix/desktop/fleet-re/qca-bt-format.md`,
`tools/qca_tlv_parse.py`, `tools/fat_extract.py`; the 53 KB results JSON
and the 5.9 MB devices CSV stay local with reproducibility provenance
(see push mechanics); `docs/devices/oneplus6/bt.md` upgraded to
format-spec class. Open: patch-stream entry structure, ap*/cr* family
attribution, 256-byte tails, NVM tag names ≥ 0x0020.
