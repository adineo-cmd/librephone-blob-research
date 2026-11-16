/* Clean-room, spec-derived WMI TLV framing per public ath11k wmi.h facts (GPL,
   linux master: struct wmi_tlv {u32 header; u8 value[]}, WMI_TLV_TAG GENMASK(31,16),
   WMI_TLV_LEN GENMASK(15,0), struct wmi_cmd_hdr {u32 cmd_id}, WMI_CMD_HDR_CMD_ID
   GENMASK(23,0)) and the lab dispatch paper; no proprietary access. */
#include <string.h>
#include "wmi_tlv.h"

void wmi_tlv_builder_init(wmi_tlv_builder_t *b, uint8_t *buf, size_t cap)
{
    b->buf = buf;
    b->cap = cap;
    b->pos = 0;
    b->error = 0;
}

int wmi_tlv_builder_append(wmi_tlv_builder_t *b, uint16_t tag, const void *value, uint16_t len)
{
    size_t padded = wmi_tlv_padded_len(len);
    if (b->error)
        return -1;
    if (padded > WMI_TLV_MAX_LEN || b->pos + WMI_TLV_HDR_SIZE + padded > b->cap) {
        b->error = 1;
        return -1;
    }
    uint32_t hdr = wmi_tlv_header_pack(tag, len);
    memcpy(b->buf + b->pos, &hdr, 4);
    b->pos += WMI_TLV_HDR_SIZE;
    if (len) {
        memcpy(b->buf + b->pos, value, len);
        if (padded > len)
            memset(b->buf + b->pos + len, 0, padded - len);
        b->pos += padded;
    }
    return 0;
}

int wmi_tlv_builder_pad_end(wmi_tlv_builder_t *b)
{
    if (b->error)
        return -1;
    while (b->pos & 3u) {
        if (b->pos >= b->cap) {
            b->error = 1;
            return -1;
        }
        b->buf[b->pos++] = 0;
    }
    return 0;
}

size_t wmi_tlv_builder_len(const wmi_tlv_builder_t *b)
{
    return b->pos;
}

void wmi_tlv_cursor_init(wmi_tlv_cursor_t *c, const void *buf, size_t len)
{
    c->buf = (const uint8_t *)buf;
    c->len = len;
    c->pos = 0;
}

int wmi_tlv_cursor_next(wmi_tlv_cursor_t *c, wmi_tlv_hdr_t *h, const uint8_t **value)
{
    if (c->pos + WMI_TLV_HDR_SIZE > c->len)
        return 0;
    uint32_t word;
    memcpy(&word, c->buf + c->pos, 4);
    wmi_tlv_header_unpack(word, h);
    c->pos += WMI_TLV_HDR_SIZE;
    size_t padded = wmi_tlv_padded_len(h->len);
    if (c->pos + padded > c->len)
        return -1;
    *value = c->buf + c->pos;
    c->pos += padded;
    return 1;
}

uint32_t wmi_cmd_frame_build(uint32_t grp, uint32_t cmd, uint8_t *out, size_t cap,
                             const wmi_tlv_builder_t *tlvs)
{
    uint32_t id = ((grp & 0x1fu) << 12) | (cmd & 0xfffu);
    size_t need = 4 + (tlvs ? tlvs->pos : 0);
    if (need > cap)
        return 0;
    memcpy(out, &id, 4);
    if (tlvs && tlvs->pos)
        memcpy(out + 4, tlvs->buf, tlvs->pos);
    return (uint32_t)need;
}
