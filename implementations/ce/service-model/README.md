# ce/service-model — CopyEngine descriptor codec + ring arithmetic

Spec facts (public ath11k `ce.h`/`hw.c`, linux master, fetched 2026-11-16,
GPL — the in-source note "Structure is shared between Host software and
Target firmware!" quoted in the lab note):
`struct ce_pipe_config { pipenum, pipedir, nentries, nbytes_max, flags,
reserved }` — six `__le32`, 24 bytes, delivered to the target one-per-CE
through QMI at startup; `struct service_to_pipe { service_id, pipedir,
pipenum }` `__le32`; `PIPEDIR_NONE 0 / IN 1 / OUT 2 / INOUT 3 / INOUT_H2H 4`;
`CE_COUNT_MAX 12`; `CE_RING_IDX_INCR(nentries_mask, idx) = ((idx)+1) &
(nentries_mask)`. Reference pipe shape from the lab note
[interface-copyengine.md](../../../research/qualcomm/docs/interface-copyengine.md)
(ipq8074 table, same CE service model).

Implements: 24-byte descriptor pack/unpack (LE), validation (pipe < 12,
direction ≤ 4, nentries power-of-two-or-zero, zero-entry ⇔ NONE direction),
service→pipe codec, ring mask/increment, and the reference 12-pipe table
(CE0 HTC ctrl 16/2048, CE1 HTT+HTC 512 in, CE2 WMI 512 in, CE3 WMI 32 out,
CE4 HTT 2048 out + NO_INTR, CE5 pktlog 512 in, CE6/CE8 hif_memcpy NONE,
CE7/CE9 WMI 32 out, CE10 HTT 512 in, CE11 unused).

Files: [ce_service_model.h](ce_service_model.h), [ce_service_model.c](ce_service_model.c),
[test_ce.c](test_ce.c).

Build & run:
```
gcc -std=c99 -Wall -Wextra -O2 -o ce_test test_ce.c ce_service_model.c
./ce_test
```

Result: ALL SELFTESTS PASSED (29 checks).

Open item: the WCN6750-specific per-pipe table lives in the public FP6 vendor
wlan module tree (`qcom/opensource/wlan/`); the table here is the mainline
ipq8074 reference shape and is marked as such, per the lab note.

Clean-room statement: spec-only derivation (public GPL kernel facts + lab
note), no proprietary access.
