/* Clean-room, spec-derived CopyEngine service model per public ath11k facts (GPL,
   linux master ce.h/hw.c) and the lab interface note qualcomm-fp6/docs/interface-copyengine.md;
   no proprietary access. */
#include <string.h>
#include "ce_service_model.h"

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

int ce_pipe_config_pack(const ce_pipe_config_t *c, uint8_t out[CE_CONFIG_BYTES])
{
    if (!c || !out)
        return -1;
    le32_store(out + 0, c->pipenum);
    le32_store(out + 4, c->pipedir);
    le32_store(out + 8, c->nentries);
    le32_store(out + 12, c->nbytes_max);
    le32_store(out + 16, c->flags);
    le32_store(out + 20, c->reserved);
    return 0;
}

int ce_pipe_config_unpack(const uint8_t in[CE_CONFIG_BYTES], ce_pipe_config_t *c)
{
    if (!c || !in)
        return -1;
    c->pipenum = le32_load(in + 0);
    c->pipedir = le32_load(in + 4);
    c->nentries = le32_load(in + 8);
    c->nbytes_max = le32_load(in + 12);
    c->flags = le32_load(in + 16);
    c->reserved = le32_load(in + 20);
    return 0;
}

int ce_pipe_config_validate(const ce_pipe_config_t *c)
{
    if (c->pipenum >= CE_COUNT_MAX)
        return -1;
    if (c->pipedir > CE_PIPE_DIR_H2H)
        return -1;
    if (c->nentries && (c->nentries & (c->nentries - 1)))
        return -1;
    if (c->nentries == 0 && c->pipedir != CE_PIPE_DIR_NONE)
        return -1;
    return 0;
}

int ce_service_to_pipe_pack(const service_to_pipe_t *s, uint8_t out[CE_SVC_MAP_WORDLEN * 4])
{
    if (!s || !out)
        return -1;
    le32_store(out + 0, s->service_id);
    le32_store(out + 4, s->pipedir);
    le32_store(out + 8, s->pipenum);
    return 0;
}

int ce_service_to_pipe_unpack(const uint8_t in[CE_SVC_MAP_WORDLEN * 4], service_to_pipe_t *s)
{
    if (!s || !in)
        return -1;
    s->service_id = le32_load(in + 0);
    s->pipedir = le32_load(in + 4);
    s->pipenum = le32_load(in + 8);
    return 0;
}

uint32_t ce_ring_mask(uint32_t nentries)
{
    return nentries - 1u;
}

uint32_t ce_ring_idx_incr(uint32_t nentries_mask, uint32_t idx)
{
    return (idx + 1u) & nentries_mask;
}

static const ce_pipe_config_t ref_table[] = {
    {0,  CE_PIPE_DIR_OUT, 16,   2048, 0, 0},
    {1,  CE_PIPE_DIR_IN,  512,  0,    0, 0},
    {2,  CE_PIPE_DIR_IN,  512,  0,    0, 0},
    {3,  CE_PIPE_DIR_OUT, 32,   0,    0, 0},
    {4,  CE_PIPE_DIR_OUT, 2048, 256,  CE_SVC_FLAG_NO_INTR, 0},
    {5,  CE_PIPE_DIR_IN,  512,  0,    0, 0},
    {6,  CE_PIPE_DIR_NONE, 0,   0,    0, 0},
    {7,  CE_PIPE_DIR_OUT, 32,   0,    0, 0},
    {8,  CE_PIPE_DIR_NONE, 0,   0,    0, 0},
    {9,  CE_PIPE_DIR_OUT, 32,   0,    0, 0},
    {10, CE_PIPE_DIR_IN,  512,  0,    0, 0},
    {11, CE_PIPE_DIR_NONE, 0,   0,    0, 0},
};

uint32_t ce_reference_pipe_count(void)
{
    return CE_COUNT_MAX;
}

const ce_pipe_config_t *ce_reference_table(void)
{
    return ref_table;
}
