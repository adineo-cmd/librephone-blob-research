/* Clean-room, spec-derived HTC frame-layer self-test: header bit fields, flags,
   service-connect/resp message roundtrips, trailer-present semantics. */
#include <stdio.h>
#include <string.h>
#include "htc_frame.h"

static int failures;

static void check(const char *what, long got, long want)
{
    if (got != want) {
        printf("FAIL %s: got %ld want %ld\n", what, got, want);
        failures++;
    } else {
        printf("ok   %s = %ld\n", what, got);
    }
}

int main(void)
{
    htc_frame_hdr_t h = {2, HTC_TX_FLAG_NEED_CREDIT, 513};
    uint8_t w[HTC_HDR_SIZE];
    htc_frame_hdr_pack(&h, w);
    check("hdr epid byte", w[0], 2);
    check("hdr flags byte", w[1], 0x01);
    check("hdr len lo", w[2], 513 & 0xff);
    check("hdr len hi", w[3], 513 >> 8);
    htc_frame_hdr_t h2;
    htc_frame_hdr_unpack(w, &h2);
    check("hdr roundtrip epid", h2.endpoint_id, 2);
    check("hdr roundtrip flags", h2.flags, 0x01);
    check("hdr roundtrip len", h2.payload_len, 513);

    htc_frame_hdr_t tr = {3, HTC_RX_FLAG_TRAILER_PRESENT, 0};
    uint8_t tw[HTC_HDR_SIZE];
    htc_frame_hdr_pack(&tr, tw);
    htc_frame_hdr_unpack(tw, &h2);
    check("trailer flag", h2.flags, 0x02);
    check("trailer len", h2.payload_len, 0);
    check("max payload", ((htc_frame_hdr_t){0, 0, 0xffff}).payload_len, 0xffff);

    uint8_t cm[HTC_SVC_CONNECT_WIRELEN];
    htc_svc_connect_pack(3, 0x1301, 0x1234, 0x56, cm);
    uint16_t mid, sid, cf;
    uint8_t ml;
    htc_svc_connect_unpack(cm, &mid, &sid, &cf, &ml);
    check("svc msgid", mid, 3);
    check("svc svcid", sid, 0x1301);
    check("svc flags", cf, 0x1234);
    check("svc metalen", ml, 0x56);
    check("svc wire word0 hi", cm[3], 0x13);

    uint8_t rp[HTC_SVC_RESP_WIRELEN];
    htc_svc_connect_resp_pack(4, 0x1301, 0, 4, 1792, 0x11, rp);
    uint16_t rmid, rsid, rmms;
    uint8_t rst, rep, rml;
    htc_svc_connect_resp_unpack(rp, &rmid, &rsid, &rst, &rep, &rmms, &rml);
    check("resp msgid", rmid, 4);
    check("resp svcid", rsid, 0x1301);
    check("resp status", rst, 0);
    check("resp epid", rep, 4);
    check("resp maxmsg", rmms, 1792);
    check("resp metalen", rml, 0x11);
    check("resp wirelen", (long)HTC_SVC_RESP_WIRELEN, 9);

    if (failures) {
        printf("SELFTEST FAILURES: %d\n", failures);
        return 1;
    }
    printf("ALL SELFTESTS PASSED\n");
    return 0;
}
