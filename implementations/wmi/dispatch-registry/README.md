# wmi/dispatch-registry — the decoded two-level WMI dispatch architecture, as a reference implementation

Implements the lab's decoded WCN6750 wpss WMI dispatch model
([papers/wmi-dispatch-architecture.md](../../../research/papers/wmi-dispatch-architecture.md),
sections 4-5; findings F-22/F-23/F-28/F-29 in open-discovery-lab):

- ID space `grp<<12|cmd` (24-bit command header, per public ath11k `WMI_CMD_HDR_CMD_ID`)
- level 1, group routing: the b09 registry record model
  `[handler-ptr, grp<<12|cmdID, 0]` (12-byte stride, anchored count-prefixed
  runs; main run `0xc0691080-0xc06913b0`), head block `0xc0691050/0xc0691068`
  with the dispatcher's enable-mask arming (`setbit` at +0xd8/+0x104/+0x118 →
  `0xc0691140/0xc069116c/0xc0691180`)
- level 2, event routing: PDEV jump table `0xc056423c` (85 words, index =
  `(ID&0xff)-1`, bounds `<= 0x54`), STATS table `0xc05641fc` (16 words), MISC/
  GPIO/SUSPEND/VDEV cmp-tree entries, shared exit `0xc02cedcc → 0xc04e61a8`
- the firmware mechanics are modeled exactly: `R5 = ID>>8`, `R4 = ID&0xff`

All handler addresses come from the lab's committed F-29 map
(`wmi-dispatch-map.json`) via the committed generator
[gen_wmi_tables.py](gen_wmi_tables.py)
→ generated [wmi_dispatch_tables.h](wmi_dispatch_tables.h). Where the map
commits no static address (GPIO `0x1e001/0x1e002`, SUSPEND `0x11001` — runtime
b09 pointer dispatch), the table honestly carries kind `RUNTIME` instead of an
invented address.

Files: [wmi_dispatch.h](wmi_dispatch.h), [wmi_dispatch.c](wmi_dispatch.c)
(model + dispatch + self-test `main`), [wmi_dispatch_tables.h](wmi_dispatch_tables.h)
(generated data).

Build & run:
```
gcc -std=c99 -Wall -Wextra -O2 -o wmi_dispatch_test wmi_dispatch.c
./wmi_dispatch_test
```

Result: ALL SELFTESTS PASSED (33 checks: ID build/split, 41 PDEV + 9 STATS
handled counts matching F-29, 61 decoded events routed to committed blocks,
unhandled IDs → shared exit, registry head arming, record add/find).

Open items (spec gaps, never guessed): the per-record 12-stride consumption
loop and the dispatcher's call-site were not decoded by F-29; the model
exposes the registry data structure but not a firmware-internal walker.
SCAN/PEER/ROAM group dispatchers are separate functions (F-28
decode-verified, not decoded end-to-end) and are outside this component.

Clean-room statement: spec-only derivation, no proprietary access.
