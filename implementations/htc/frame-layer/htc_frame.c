/* Clean-room, spec-derived HTC frame layer per public ath11k htc.h facts (GPL);
   no proprietary access. */
#include <string.h>
#include "htc_frame.h"

static uint32_t le32_load(const uint8_t *p)
{
    return (uint32_t)p[0] | ((uint32_t)p[1] << 8) | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}

static void le32_store(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v & 0xff);
    p[1] = (uint8_t)((v >> 8) & 0xff);
    p[2] = (uint8_t)((v >> 16) & 0xff);
    p[3] = (uint8_t)((v >> 24) & 0xff);
}

void htc_frame_hdr_pack(const htc_frame_hdr_t *h, uint8_t out[HTC_HDR_SIZE])
{
    uint32_t w = ((uint32_t)h->endpoint_id & 0xffu)
                 | (((uint32_t)h->flags & 0xffu) << 8)
                 | (((uint32_t)h->payload_len & 0xffffu) << 16);
    le32_store(out, w);
}

void htc_frame_hdr_unpack(const uint8_t in[HTC_HDR_SIZE], htc_frame_hdr_t *h)
{
    uint32_t w = le32_load(in);
    h->endpoint_id = (uint8_t)(w & 0xffu);
    h->flags = (uint8_t)((w >> 8) & 0xffu);
    h->payload_len = (uint16_t)((w >> 16) & 0xffffu);
}

void htc_svc_connect_pack(uint16_t message_id, uint16_t service_id,
                          uint16_t connection_flags, uint8_t service_meta_len,
                          uint8_t out[HTC_SVC_CONNECT_WIRELEN])
{
    le32_store(out + 0, ((uint32_t)service_id << 16) | (uint32_t)message_id);
    le32_store(out + 4, ((uint32_t)service_meta_len << 16) | (uint32_t)connection_flags);
}

void htc_svc_connect_unpack(const uint8_t in[HTC_SVC_CONNECT_WIRELEN],
                            uint16_t *message_id, uint16_t *service_id,
                            uint16_t *connection_flags, uint8_t *service_meta_len)
{
    uint32_t w0 = le32_load(in + 0);
    uint32_t w1 = le32_load(in + 4);
    *message_id = (uint16_t)(w0 & 0xffffu);
    *service_id = (uint16_t)(w0 >> 16);
    *connection_flags = (uint16_t)(w1 & 0xffffu);
    *service_meta_len = (uint8_t)((w1 >> 16) & 0xffu);
}

void htc_svc_connect_resp_pack(uint16_t message_id, uint16_t service_id,
                               uint8_t status, uint8_t endpoint_id,
                               uint16_t max_msg_size, uint8_t service_meta_len,
                               uint8_t out[HTC_SVC_RESP_WIRELEN])
{
    le32_store(out + 0, ((uint32_t)service_id << 16) | (uint32_t)message_id);
    le32_store(out + 4, ((uint32_t)max_msg_size << 16)
                        | ((uint32_t)endpoint_id << 8)
                        | (uint32_t)status);
    out[8] = service_meta_len;
}

void htc_svc_connect_resp_unpack(const uint8_t in[HTC_SVC_RESP_WIRELEN],
                                 uint16_t *message_id, uint16_t *service_id,
                                 uint8_t *status, uint8_t *endpoint_id,
                                 uint16_t *max_msg_size, uint8_t *service_meta_len)
{
    uint32_t w0 = le32_load(in + 0);
    uint32_t w1 = le32_load(in + 4);
    *message_id = (uint16_t)(w0 & 0xffffu);
    *service_id = (uint16_t)(w0 >> 16);
    *status = (uint8_t)(w1 & 0xffu);
    *endpoint_id = (uint8_t)((w1 >> 8) & 0xffu);
    *max_msg_size = (uint16_t)((w1 >> 16) & 0xffffu);
    *service_meta_len = in[8];
}
