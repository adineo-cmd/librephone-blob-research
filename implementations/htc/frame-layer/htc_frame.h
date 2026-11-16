/* Clean-room, spec-derived HTC frame layer per public ath11k htc.h facts (GPL,
   linux stable: HTC_HDR_ENDPOINTID GENMASK(7,0), HTC_HDR_FLAGS GENMASK(15,8),
   HTC_HDR_PAYLOADLEN GENMASK(31,16), trailer control bytes CTRLBYTES0/1,
   ATH11K_HTC_FLAG_NEED_CREDIT_UPDATE 0x01, ATH11K_HTC_FLAG_SEND_BUNDLE 0x02,
   ATH11K_HTC_FLAG_TRAILER_PRESENT 0x02, service-connect field masks) and the lab
   interface note qualcomm-fp6/docs/interface-copyengine.md; no proprietary access.
   The HTC ready/setup-complete message codecs are intentionally absent: their word
   layout is not derivable from the cited masks alone — open item, never guessed. */
#ifndef HTC_FRAME_H
#define HTC_FRAME_H

#include <stddef.h>
#include <stdint.h>

#define HTC_HDR_SIZE 4u

#define HTC_TX_FLAG_NEED_CREDIT 0x01u
#define HTC_TX_FLAG_SEND_BUNDLE 0x02u
#define HTC_RX_FLAG_TRAILER_PRESENT 0x02u

#define HTC_SVC_CONNECT_WIRELEN  8u
#define HTC_SVC_RESP_WIRELEN     9u

typedef struct htc_frame_hdr {
    uint8_t endpoint_id;
    uint8_t flags;
    uint16_t payload_len;
} htc_frame_hdr_t;

void htc_frame_hdr_pack(const htc_frame_hdr_t *h, uint8_t out[HTC_HDR_SIZE]);
void htc_frame_hdr_unpack(const uint8_t in[HTC_HDR_SIZE], htc_frame_hdr_t *h);

void htc_svc_connect_pack(uint16_t message_id, uint16_t service_id,
                          uint16_t connection_flags, uint8_t service_meta_len,
                          uint8_t out[HTC_SVC_CONNECT_WIRELEN]);
void htc_svc_connect_unpack(const uint8_t in[HTC_SVC_CONNECT_WIRELEN],
                            uint16_t *message_id, uint16_t *service_id,
                            uint16_t *connection_flags, uint8_t *service_meta_len);

void htc_svc_connect_resp_pack(uint16_t message_id, uint16_t service_id,
                               uint8_t status, uint8_t endpoint_id,
                               uint16_t max_msg_size, uint8_t service_meta_len,
                               uint8_t out[HTC_SVC_RESP_WIRELEN]);
void htc_svc_connect_resp_unpack(const uint8_t in[HTC_SVC_RESP_WIRELEN],
                                 uint16_t *message_id, uint16_t *service_id,
                                 uint8_t *status, uint8_t *endpoint_id,
                                 uint16_t *max_msg_size, uint8_t *service_meta_len);

#endif
