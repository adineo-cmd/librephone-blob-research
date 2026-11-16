/* Clean-room, spec-derived WMI TLV framing per public ath11k wmi.h facts (GPL,
   linux master: struct wmi_tlv {u32 header; u8 value[]}, WMI_TLV_TAG GENMASK(31,16),
   WMI_TLV_LEN GENMASK(15,0), struct wmi_cmd_hdr {u32 cmd_id}, WMI_CMD_HDR_CMD_ID
   GENMASK(23,0)) and the lab dispatch paper; no proprietary access. */
#ifndef WMI_TLV_H
#define WMI_TLV_H

#include <stddef.h>
#include <stdint.h>

#define WMI_TLV_HDR_SIZE 4u
#define WMI_TLV_MAX_LEN  65535u

typedef struct wmi_tlv_hdr {
    uint16_t tag;
    uint16_t len;
} wmi_tlv_hdr_t;

static inline uint32_t wmi_tlv_header_pack(uint16_t tag, uint16_t len)
{
    return ((uint32_t)tag << 16) | (uint32_t)len;
}

static inline void wmi_tlv_header_unpack(uint32_t word, wmi_tlv_hdr_t *h)
{
    h->tag = (uint16_t)(word >> 16);
    h->len = (uint16_t)(word & 0xffffu);
}

static inline size_t wmi_tlv_padded_len(uint16_t len)
{
    return (len + 3u) & ~(size_t)3u;
}

typedef struct wmi_tlv_builder {
    uint8_t *buf;
    size_t cap;
    size_t pos;
    int error;
} wmi_tlv_builder_t;

void wmi_tlv_builder_init(wmi_tlv_builder_t *b, uint8_t *buf, size_t cap);
int wmi_tlv_builder_append(wmi_tlv_builder_t *b, uint16_t tag, const void *value, uint16_t len);
int wmi_tlv_builder_pad_end(wmi_tlv_builder_t *b);
size_t wmi_tlv_builder_len(const wmi_tlv_builder_t *b);

typedef struct wmi_tlv_cursor {
    const uint8_t *buf;
    size_t len;
    size_t pos;
} wmi_tlv_cursor_t;

void wmi_tlv_cursor_init(wmi_tlv_cursor_t *c, const void *buf, size_t len);
int wmi_tlv_cursor_next(wmi_tlv_cursor_t *c, wmi_tlv_hdr_t *h, const uint8_t **value);

uint32_t wmi_cmd_frame_build(uint32_t grp, uint32_t cmd, uint8_t *out, size_t cap,
                             const wmi_tlv_builder_t *tlvs);

#endif
