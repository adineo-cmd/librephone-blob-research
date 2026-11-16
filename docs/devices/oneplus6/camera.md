# OnePlus 6 (enchilada) — Camera + TrustZone + misc families (stubs)

**Evidence class: census** (hashed, container magic only).

## Camera

`/firmware/CAMERA_ICP.elf` — 3,299,320 B, magic elf32-le. The ICP (Image
Collaborative Processor) firmware ELF. Upstream matrix camera families on
SM845+ devices are larger sets; OP6's single-file camera surface is the
SDM845 generation shape. Not decoded.

## TrustZone

Partition `tz` → `tz.img`, 2,056,192 B, magic elf (ELF at offset 0 — the
QSEE image). Plus `cmnlib`/`cmnlib64`/`keymaster` partitions present in the
OTA manifest (dumped but not hashed this session — listed in
`data-fetch/enchilada/payload manifest`, kept out of the committed matrix
to keep the census to what was actually hashed; next session can extend).
The lab's TrustZone census method
([qualcomm-fp6/docs/trustzone-census.md](../../qualcomm-fp6/docs/trustzone-census.md))
applies.

## Other

`ipa_fws.{b00..b04,mdt,elf}` — IPA firmware MDT set (elf32-le, 65,984 B
total). `etc/firmware/tp/fw_synaptics_17819.img` — Synaptics touch
firmware (103,920 B, raw).

## Open questions

- hash cmnlib/cmnlib64/keymaster/boot-chain partitions (they are in the
  payload and one payload_dump call each away)
