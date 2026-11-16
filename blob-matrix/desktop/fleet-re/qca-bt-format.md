## Deliverables

- `tools/qca_tlv_parse.py` — the parser (stdlib only)
- `tools/fat_extract.py` — the minimal FAT16 walker used for `bt.img`
- Full per-file parse results (headers, tag histograms + per-entry
  values, BD_ADDR placeholders, checks): regenerable byte-identically
  with `python3 blob-matrix/desktop/tools/qca_tlv_parse.py qca-bt-tlv.json
  <extracted fleet files>` — the pipeline is committed and the inputs are
  public (any official LineageOS nightly of a fleet-carrying device, e.g.
  enchilada 2026-11-11); the results JSON itself (53 KB) stayed local
  this session for the same push-path reason as `devices-001-222.csv`
  (see STATUS-DESKTOP.md push mechanics).
- The 29-device leverage entry in `fragmentation-half.md` §2 is now
  backed by an actual format spec instead of a name.

## Open items

1. Patch-stream entry structure (post-header) — needs one of: CodeLinaro
   qca-bt opensource `hci_rome.c` fetch, or a controlled diff between
   rom_build variants (2.0 vs 2.1 of the same family).
2. `ap*` vs `cr*` chip-family attribution.
3. The 256-byte patch tails (role unknown).
4. NVM tags ≥ 0x0020 naming (would need one Qualcomm-side spec leak —
   none found public; checked 2026-11-16).
5. The other four fleet files in linux-firmware's qca/ dir are named
   differently (404 on the matrix names) — upstream matrix filenames are
   LineageOS-vendor-tree names, not linux-firmware names; the md5 joins
   above prove equivalence where both exist.

RULE 0 record (2026-11-16): `Qualcomm Bluetooth ROM patch .tlv format
reverse engineering crbtfw apbtfw` — no dedicated RE writeup exists
(Broadcom/Realtek have public RE work; QCA does not, beyond btqca.c's
protocol layer). The container-layer spec + fleet identity chain here is
the first public one for these files.
