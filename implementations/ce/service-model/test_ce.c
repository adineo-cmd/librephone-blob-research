/* Clean-room, spec-derived CopyEngine service-model self-test: 24-byte descriptor
   roundtrip, validation rules, ring wraparound, reference pipe table. */
#include <stdio.h>
#include <string.h>
#include "ce_service_model.h"

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
    ce_pipe_config_t c = {3, CE_PIPE_DIR_OUT, 32, 0, 0, 0};
    uint8_t wire[CE_CONFIG_BYTES];
    check("pack", ce_pipe_config_pack(&c, wire) == 0 ? 1 : 0, 1);
    check("wire len", (long)sizeof(wire), 24);
    check("wire pipenum", wire[0], 3);
    check("wire dir", wire[4], 2);
    check("wire nentries", wire[8], 32);
    ce_pipe_config_t d;
    check("unpack", ce_pipe_config_unpack(wire, &d) == 0 ? 1 : 0, 1);
    check("roundtrip pipenum", d.pipenum, 3);
    check("roundtrip dir", d.pipedir, 2);
    check("roundtrip nentries", d.nentries, 32);
    check("roundtrip reserved", d.reserved, 0);

    ce_pipe_config_t bad = {12, CE_PIPE_DIR_OUT, 16, 0, 0, 0};
    check("validate pipe oob", ce_pipe_config_validate(&bad), -1);
    ce_pipe_config_t bad2 = {1, 9, 16, 0, 0, 0};
    check("validate dir oob", ce_pipe_config_validate(&bad2), -1);
    ce_pipe_config_t bad3 = {1, CE_PIPE_DIR_OUT, 24, 0, 0, 0};
    check("validate non-pow2", ce_pipe_config_validate(&bad3), -1);
    ce_pipe_config_t bad4 = {1, CE_PIPE_DIR_OUT, 0, 0, 0, 0};
    check("validate zero-dir", ce_pipe_config_validate(&bad4), -1);
    ce_pipe_config_t okc = {11, CE_PIPE_DIR_NONE, 0, 0, 0, 0};
    check("validate none ok", ce_pipe_config_validate(&okc), 0);

    service_to_pipe_t s = {1, CE_PIPE_DIR_OUT, 3};
    uint8_t sw[12];
    check("svc pack", ce_service_to_pipe_pack(&s, sw) == 0 ? 1 : 0, 1);
    service_to_pipe_t s2;
    ce_service_to_pipe_unpack(sw, &s2);
    check("svc roundtrip svc", s2.service_id, 1);
    check("svc roundtrip pipe", s2.pipenum, 3);

    check("ring mask", ce_ring_mask(512), 511);
    uint32_t idx = 511;
    idx = ce_ring_idx_incr(ce_ring_mask(512), idx);
    check("ring wrap", idx, 0);
    idx = ce_ring_idx_incr(ce_ring_mask(512), 100);
    check("ring incr", idx, 101);

    check("ref pipe count", ce_reference_pipe_count(), 12);
    const ce_pipe_config_t *rt = ce_reference_table();
    uint32_t bad_rows = 0;
    for (uint32_t i = 0; i < ce_reference_pipe_count(); i++)
        bad_rows += ce_pipe_config_validate(&rt[i]) != 0 ? 1 : 0;
    check("ref table valid", bad_rows, 0);
    check("ref ce0", rt[0].nentries, 16);
    check("ref ce0 max", rt[0].nbytes_max, 2048);
    check("ref ce4", rt[4].nentries, 2048);
    check("ref ce4 nointr", rt[4].flags, CE_SVC_FLAG_NO_INTR);
    check("ref ce6 none", rt[6].pipedir, 0);
    check("ref ce11 none", rt[11].pipedir, 0);

    if (failures) {
        printf("SELFTEST FAILURES: %d\n", failures);
        return 1;
    }
    printf("ALL SELFTESTS PASSED\n");
    return 0;
}
