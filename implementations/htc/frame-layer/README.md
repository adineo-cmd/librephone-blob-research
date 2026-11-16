# htc/frame-layer — HTC frame header + service-connect codecs

Spec facts (public ath11k `htc.h`, linux stable, fetched 2026-11-16, GPL):
frame header word `HTC_HDR_ENDPOINTID GENMASK(7,0) | HTC_HDR_FLAGS
GENMASK(15,8) | HTC_HDR_PAYLOADLEN GENMASK(31,16)` (4 bytes LE) with
trailer control bytes `HTC_HDR_CONTROLBYTES0/1`;
`ATH11K_HTC_FLAG_NEED_CREDIT_UPDATE 0x01`,
`ATH11K_HTC_FLAG_SEND_BUNDLE 0x02`,
`ATH11K_HTC_FLAG_TRAILER_PRESENT 0x02`; service-connect message fields
(`HTC_SVC_MSG_SERVICE_ID GENMASK(31,16)`,
`HTC_SVC_MSG_CONNECTIONFLAGS GENMASK(15,0)`,
`HTC_SVC_MSG_SERVICEMETALENGTH GENMASK(23,16)`,
`HTC_SVC_RESP_MSG_*` status/endpoint/max-msg-size/meta-length masks,
`HTC_MSG_MESSAGEID GENMASK(15,0)`).

Implements: frame header pack/unpack; service-connect request (8-byte wire)
and response (9-byte wire) codecs at the mask-derivable positions.

Deliberately absent (never guessed): the HTC ready / setup-complete message
codecs — their word layout is not derivable from the cited GENMASK list
alone. Filed as the open item instead of inventing an order.

Files: [htc_frame.h](htc_frame.h), [htc_frame.c](htc_frame.c), [test_htc.c](test_htc.c).

Build & run:
```
gcc -std=c99 -Wall -Wextra -O2 -o htc_test test_htc.c htc_frame.c
./htc_test
```

Result: ALL SELFTESTS PASSED (23 checks).

Clean-room statement: spec-only derivation (public GPL kernel facts), no
proprietary access.
