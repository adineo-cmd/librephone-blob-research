# OnePlus 6 (enchilada) — Bluetooth family

**Evidence class: census** (partition extracted + hashed; no decode). Source:
LineageOS 22.2 nightly 2026-11-11 enchilada, OTA payload partition
`bluetooth` → `bt.img` (765,952 B, magic raw, sha256 in the matrix CSV).

## Container layout

One raw partition image, 765,952 B. This is the WCN3990 BT firmware
partition (enchilada's BT chip is WCN3990, integrated into SDM845).
`/vendor/bt_firmware` in the vendor image is an empty mount point — the
BT payload lives in this partition, not in the vendor filesystem.

## Relationship to the top-20 QCA BT patch fleet

The fleet-shared `crbtfw20.tlv` / `apbtfw10.tlv` / `crbtfw11.tlv` +
`crnv20.bin` / `crnv11.bin` / `apnv10.bin` files (recon.md top-20 #1-#6,
29 devices each — the desktop half's Phase-2/3 headline) belong to the
WCN39xx generation of devices, not the WCN3990. The OnePlus 6 BT patch
payload is embedded in `bt.img` rather than shipped as the `.tlv`/`nv`
file set. RE value: the btqca download protocol (mainline
`drivers/bluetooth/btqca.c`, public) reads these images on both
generations — a `bt.img` parse (expected MDT/ELF container with BT ROM
patch sections) would extend the fleet story to the WCN3990 generation.

## ISA/proof status

Not decoded. Magic probe: raw 16-byte head (no ELF magic at offset 0 —
container type unknown; candidates per Qualcomm PIL naming: packed MDT or
raw signed image).

## Interface facts

Consumer: `hci_qca` mainline driver + `btqca.c` patch/NVM download
sequence (public code). No interface doc committed yet.

## Open questions

- `bt.img` container type + section map
- does `bt.img` embed a `.tlv`-equivalent patch stream?
- WCN3990 generation chip-side patch semantics (vs the crbtfw/apbtfw fleet)
