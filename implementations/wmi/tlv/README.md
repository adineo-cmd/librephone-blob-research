# wmi/tlv — WMI TLV framing and command-frame builder

Spec facts (public ath11k `wmi.h`, linux master, fetched 2026-11-16, GPL):
`struct wmi_tlv { u32 header; u8 value[] } __packed`;
`WMI_TLV_TAG GENMASK(31,16)`; `WMI_TLV_LEN GENMASK(15,0)`;
`TLV_HDR_SIZE = 4`; `struct wmi_cmd_hdr { u32 cmd_id } __packed`;
`WMI_CMD_HDR_CMD_ID GENMASK(23,0)`. ID construction `grp<<12|cmd` per the
lab dispatch paper section 1 (ath11k `WMI_TLV_CMD`).

Implements: header pack/unpack (tag/len), 4-byte alignment padding, stream
builder with overflow detection, cursor walk with truncation detection,
command-frame builder (4-byte `wmi_cmd_hdr` + TLV stream).

Files: [wmi_tlv.h](wmi_tlv.h), [wmi_tlv.c](wmi_tlv.c), [test_tlv.c](test_tlv.c).

Build & run:
```
gcc -std=c99 -Wall -Wextra -O2 -o wmi_tlv_test test_tlv.c wmi_tlv.c
./wmi_tlv_test
```

Result: ALL SELFTESTS PASSED (36 checks; two initial failures were test-vector
arithmetic errors — 3 TLVs not 2, LE byte order of the tag check — fixed in
the test, implementation unchanged).

Clean-room statement: spec-only derivation (public GPL kernel facts + lab
paper), no proprietary access.
