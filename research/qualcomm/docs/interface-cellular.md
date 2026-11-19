# Cellular modem driver ↔ blob interface (Fairphone FP6) — for upstream issue #18

One-page interface note, from **public data only**, in API-doc style for
the future test suite ([upstream issue
#18](https://codeberg.org/rsavoye/librephone/issues/18)). Written
2026-11-16.

**Legend:** [PUBLIC] = mainline kernel / public tree fact; [LAB] =
lab-derived fact (committed doc); [OPEN] = needs data not on this box.

## 0. The blob

- [LAB] The modem firmware on FP6 is the `modem` family: `modem.mdt` +
  `modem.b00–b30`, Hexagon (QDSP6, e_machine 164) — sizes/hashes in
  `qualcomm-fp6/results/census.md`; plus `modem/image/milos/qdsp6m.qdb`
  (6,506,187 B) and per-carrier mcfg payloads (`modem_pr/mcfg/...`).
- [LAB] ISA identification at instruction level: Hexagon (F-5/F-6,
  `qualcomm-fp6/docs/fp6-architecture-census.md`).

## 1. Load & authenticate (kernel → TrustZone → modem)

All [PUBLIC], mainline `torvalds/linux` (accessed 2026-11-16):

| step | interface | anchor |
|---|---|---|
| fetch `.mdt` + `.bNN` via request_firmware | firmware-loader ABI | `drivers/soc/qcom/mdt_loader.c` (`qcom_mdt_load`, `qcom_mdt_bins_are_split`) |
| segment placement | phdr-driven: `offset = p_paddr - mem_reloc`; relocatable images (`p_flags & QCOM_MDT_RELOCATABLE`, BIT(27)) rebase onto the allocated region | `mdt_loader.c` (`qcom_mdt_load_no_init`) |
| metadata + auth | hash segments (`QCOM_MDT_TYPE_HASH`) packed into "metadata" → `qcom_pas_init_image` → **SCM/PAS call into TrustZone**; PAS must return OK or the modem never starts | `mdt_loader.c` (`__qcom_mdt_pas_init`), `drivers/soc/qcom/qcom_scm.c` |
| reset & boot | mss power sequencing, halt/release | `drivers/remoteproc/qcom_q6v5_mss.c` |
| EFS store | modem reads/writes `/persist` via the **rmtfs** protocol over the transport below; host allocates shared memory and answers block read/write requests | `drivers/soc/qcom/rmtfs_mem.c` |

## 2. Transport & channels (kernel ↔ running modem)

- [PUBLIC] **GLINK/SMEM**: the modem exposes rpmsg channels over
  Shared Memory; channel types include `DATA_CNTL` (control/QMI), the
  `DATA1…DATA27` data channels (QMAP/rmnet), `DIAG`, `RMT` (rmtfs),
  `LOOPBACK` — `drivers/rpmsg/qcom_glink_smem.c`,
  `drivers/rpmsg/qcom_smd.c`.
- [PUBLIC] **QRTR**: the modem publishes services (QMI services:
  dms/nas/wds/wda/pdc, plus DIAG) as QRTR service:instance tuples on
  an IP-like node addressing scheme; the kernel network family is
  `AF_QIPCRTR` — `net/qrtr/af_qrtr.c`, `net/qrtr/ns.c` (name server).
- [PUBLIC] **QMI**: TLV-based control protocol; encoding helpers in
  `include/linux/soc/qcom/qmi.h` + `drivers/soc/qcom/` qmi helpers;
  control handshake = QMICTL (`QMICTL_GET_VERSION`,
  `QMICTL_GET_CLIENT_ID`).

## 3. Data plane

- [PUBLIC] **rmnet / QMAP**: per-channel network devices; packets
  carry the rmnet MAP header (aggregation, mux, checksum offload
  flags) — `drivers/net/ethernet/qualcomm/rmnet/` (`rmnet_config.c`,
  `rmnet_map.h`).
- [PUBLIC] MHI is the PCIe-attached variant of the same layering
  (`drivers/bus/mhi/`) — not the transport on QCM6490, where the modem
  is a glink/q6v5 remoteproc, but the same service model.

## 4. Test-suite hooks (what #18's suite can assert without hardware)

1. Parse a public `modem.mdt`: phdr table → loadable segments →
   relocation math identical to `qcom_mdt_load_no_init`
   ([LAB]+[PUBLIC] cross — also answers #40's mechanics).
2. QRTR service discovery: enumerate modem service IDs on a live
   device; assert dms/nas/wds presence before radio enable.
3. QMICTL handshake bytes: build/parse `QMICTL_GET_VERSION`
   request/response with the public TLV codec.
4. QMAP header round-trip: encode/decode MAP v1/v2 frames incl.
   aggregation.
5. rmtfs: serve a synthetic EFS block device over an rpmsg loopback.

## Sources consulted (accessed 2026-11-16)

- mainline: `drivers/soc/qcom/mdt_loader.c` (fetched, 508 lines),
  `drivers/remoteproc/qcom_q6v5_mss.c`, `drivers/soc/qcom/rmtfs_mem.c`,
  `net/qrtr/af_qrtr.c`, `drivers/rpmsg/qcom_glink_smem.c`,
  `drivers/net/ethernet/qualcomm/rmnet/rmnet_config.c`,
  `include/linux/soc/qcom/qmi.h`, `include/linux/soc/qcom/mdt_loader.h`
  (all fetched OK / status 200)
- lab: `qualcomm-fp6/results/census.md`,
  `qualcomm-fp6/docs/fp6-architecture-census.md`

**Clean-room statement:** public-kernel facts + lab-derived census
facts only. The modem blob's internal Hexagon handlers are NOT
documented here (that is the WMI-paper level of detail for WLAN; for
the modem it remains [OPEN] pending disassembly capacity).
