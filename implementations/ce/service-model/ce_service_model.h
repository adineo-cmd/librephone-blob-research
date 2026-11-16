/* Clean-room, spec-derived CopyEngine service model per public ath11k facts (GPL,
   linux master ce.h/hw.c: struct ce_pipe_config {pipenum,pipedir,nentries,nbytes_max,
   flags,reserved} all __le32 — 24 bytes, shared host/target, passed one-per-CE via QMI
   at startup; struct service_to_pipe {service_id,pipedir,pipenum} __le32; PIPEDIR_NONE 0,
   IN 1, OUT 2, INOUT 3, INOUT_H2H 4; CE_COUNT_MAX 12; CE_RING_IDX_INCR) and the lab
   interface note qualcomm-fp6/docs/interface-copyengine.md; no proprietary access. */
#ifndef CE_SERVICE_MODEL_H
#define CE_SERVICE_MODEL_H

#include <stddef.h>
#include <stdint.h>

#define CE_COUNT_MAX 12u

#define CE_PIPE_DIR_NONE  0u
#define CE_PIPE_DIR_IN    1u
#define CE_PIPE_DIR_OUT   2u
#define CE_PIPE_DIR_INOUT 3u
#define CE_PIPE_DIR_H2H   4u

#define CE_SVC_FLAG_BYTE_SWAP 2u
#define CE_SVC_FLAG_NO_INTR   8u

#define CE_CONFIG_WORDLEN 6u
#define CE_CONFIG_BYTES   24u
#define CE_SVC_MAP_WORDLEN 3u

typedef struct ce_pipe_config {
    uint32_t pipenum;
    uint32_t pipedir;
    uint32_t nentries;
    uint32_t nbytes_max;
    uint32_t flags;
    uint32_t reserved;
} ce_pipe_config_t;

typedef struct service_to_pipe {
    uint32_t service_id;
    uint32_t pipedir;
    uint32_t pipenum;
} service_to_pipe_t;

int ce_pipe_config_pack(const ce_pipe_config_t *c, uint8_t out[CE_CONFIG_BYTES]);
int ce_pipe_config_unpack(const uint8_t in[CE_CONFIG_BYTES], ce_pipe_config_t *c);
int ce_pipe_config_validate(const ce_pipe_config_t *c);

int ce_service_to_pipe_pack(const service_to_pipe_t *s, uint8_t out[CE_SVC_MAP_WORDLEN * 4]);
int ce_service_to_pipe_unpack(const uint8_t in[CE_SVC_MAP_WORDLEN * 4], service_to_pipe_t *s);

uint32_t ce_ring_mask(uint32_t nentries);
uint32_t ce_ring_idx_incr(uint32_t nentries_mask, uint32_t idx);

uint32_t ce_reference_pipe_count(void);
const ce_pipe_config_t *ce_reference_table(void);

#endif
