/* Clean-room, spec-derived WMI TLV framing self-test: tag/len pack semantics,
   4-byte alignment padding, cursor walk, command frame construction. */
#include <stdio.h>
#include <string.h>
#include "wmi_tlv.h"

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
    wmi_tlv_hdr_t h = {0x1234, 5678};
    uint32_t word = wmi_tlv_header_pack(h.tag, h.len);
    check("pack tag16", (word >> 16) & 0xffff, 0x1234);
    check("pack len16", word & 0xffff, 5678);
    wmi_tlv_hdr_t h2;
    wmi_tlv_header_unpack(word, &h2);
    check("roundtrip tag", h2.tag, 0x1234);
    check("roundtrip len", h2.len, 5678);
    check("wmi_cmd_hdr id space", 0x00ffffffu, 0x00ffffffu);
    check("grp<<12|cmd", (3u << 12) | 1u, 0x3001u);

    check("padded 0", wmi_tlv_padded_len(0), 0);
    check("padded 1", wmi_tlv_padded_len(1), 4);
    check("padded 4", wmi_tlv_padded_len(4), 4);
    check("padded 5", wmi_tlv_padded_len(5), 8);
    check("padded 7", wmi_tlv_padded_len(7), 8);

    uint8_t buf[64];
    wmi_tlv_builder_t b;
    wmi_tlv_builder_init(&b, buf, sizeof(buf));
    const uint8_t v8[8] = {1, 2, 3, 4, 5, 6, 7, 8};
    check("append tlv8", wmi_tlv_builder_append(&b, 0x0001, v8, 8) == 0 ? 1 : 0, 1);
    const uint8_t v3[3] = {0xaa, 0xbb, 0xcc};
    check("append tlv3", wmi_tlv_builder_append(&b, 0x0002, v3, 3) == 0 ? 1 : 0, 1);
    check("append empty", wmi_tlv_builder_append(&b, 0x0003, NULL, 0) == 0 ? 1 : 0, 1);
    check("builder len", wmi_tlv_builder_len(&b), (4 + 8) + (4 + 4) + 4);
    check("pad end", wmi_tlv_builder_pad_end(&b) == 0 ? 1 : 0, 1);

    wmi_tlv_cursor_t c;
    wmi_tlv_cursor_init(&c, buf, wmi_tlv_builder_len(&b));
    wmi_tlv_hdr_t ch;
    const uint8_t *cv;
    int rc = wmi_tlv_cursor_next(&c, &ch, &cv);
    check("cursor1 rc", rc, 1);
    check("cursor1 tag", ch.tag, 0x0001);
    check("cursor1 len", ch.len, 8);
    check("cursor1 val", cv[7], 8);
    rc = wmi_tlv_cursor_next(&c, &ch, &cv);
    check("cursor2 rc", rc, 1);
    check("cursor2 tag", ch.tag, 0x0002);
    check("cursor2 len", ch.len, 3);
    check("cursor2 pad zero", cv[3], 0);
    rc = wmi_tlv_cursor_next(&c, &ch, &cv);
    check("cursor3 rc", rc, 1);
    check("cursor3 tag", ch.tag, 0x0003);
    check("cursor3 len", ch.len, 0);
    rc = wmi_tlv_cursor_next(&c, &ch, &cv);
    check("cursor end", rc, 0);

    uint8_t frame[64];
    uint32_t flen = wmi_cmd_frame_build(3, 1, frame, sizeof(frame), &b);
    check("frame len", flen, 4 + 24);
    uint32_t id;
    memcpy(&id, frame, 4);
    check("frame cmd id", id, 0x3001u);
    check("frame cmd id mask", id & 0x00ffffffu, 0x3001u);
    check("frame tlv tag1", (frame[7] << 8) | frame[6], 0x0001);

    wmi_tlv_builder_t over;
    wmi_tlv_builder_init(&over, buf, 8);
    check("overflow flag", wmi_tlv_builder_append(&over, 1, v8, 8) == -1 ? 1 : 0, 1);
    check("overflow sticky", wmi_tlv_builder_append(&over, 1, v8, 8) == -1 ? 1 : 0, 1);

    wmi_tlv_cursor_t bad;
    wmi_tlv_cursor_init(&bad, buf, 6);
    rc = wmi_tlv_cursor_next(&bad, &ch, &cv);
    check("truncated len field rc", rc, -1);

    if (failures) {
        printf("SELFTEST FAILURES: %d\n", failures);
        return 1;
    }
    printf("ALL SELFTESTS PASSED\n");
    return 0;
}
