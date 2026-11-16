/* Clean-room, spec-derived implementation of the WCN6750 wpss WMI two-level
   dispatch architecture, from the lab's published spec only (papers/wmi-dispatch-architecture.md,
   qualcomm-fp6/docs/wmi-*); no proprietary code, headers, or strings were read. */
#ifndef WMI_DISPATCH_H
#define WMI_DISPATCH_H

#include <stddef.h>
#include <stdint.h>

#define WMI_ID_GRP_SHIFT 12
#define WMI_ID_GRP_MASK 0x1f
#define WMI_ID_CMD_MASK 0xfff

#define WMI_GRP_SCAN    3
#define WMI_GRP_PDEV    4
#define WMI_GRP_VDEV    5
#define WMI_GRP_PEER    6
#define WMI_GRP_MGMT    7
#define WMI_GRP_BA_NEG  8
#define WMI_GRP_DFS     10
#define WMI_GRP_ROAM    11
#define WMI_GRP_SUSPEND 0x11
#define WMI_GRP_STATS   0x16
#define WMI_GRP_MISC    0x1d
#define WMI_GRP_GPIO    0x1e

#define WMI_TLV_CMD(grp) ((((uint32_t)(grp)) << WMI_ID_GRP_SHIFT) | 1u)

#define WMI_PDEV_DISPATCHER  0xc02cd9ccu
#define WMI_VDEV_DISPATCHER  0xc031d8c8u
#define WMI_PEER_DISPATCHER  0xc02d94bcu
#define WMI_ROAM_DISPATCHER  0xc035d2e0u

#define WMI_REGISTRY_HEAD_BASE   0xc0691050u
#define WMI_REGISTRY_ARM_BASE    0xc0691068u
#define WMI_REGISTRY_MAIN_RUN    0xc0691080u
#define WMI_REGISTRY_RECORDS_PTR 0xc06913c0u
#define WMI_REGISTRY_ARM_OFFSETS_0 0xd8u
#define WMI_REGISTRY_ARM_OFFSETS_1 0x104u
#define WMI_REGISTRY_ARM_OFFSETS_2 0x118u

#define WMI_REG_RECORD_STRIDE 12
#define WMI_REG_MAX_RECORDS 256

typedef struct wmi_registry_record {
    uint32_t handler;
    uint32_t id;
    uint32_t zero;
} wmi_registry_record_t;

typedef struct wmi_registry_head {
    uint32_t base;
    uint32_t word_0x8;
    uint32_t word_0xc;
    uint32_t records_ptr;
    uint32_t word_0x24;
    uint32_t main_run_anchor;
    uint32_t enable_masks[3];
} wmi_registry_head_t;

typedef struct wmi_dispatcher {
    const struct wmi_table_entry *table;
    uint32_t table_len;
    uint32_t table_vaddr;
} wmi_dispatcher_t;

typedef struct wmi_dispatch_model {
    wmi_dispatcher_t pdev;
    wmi_dispatcher_t stats;
    wmi_registry_head_t head;
    wmi_registry_record_t records[WMI_REG_MAX_RECORDS];
    uint32_t record_count;
    uint32_t shared_exit_block;
    uint32_t shared_exit_jump;
    uint32_t dispatch_count;
} wmi_dispatch_model_t;

static inline uint32_t wmi_id_build(uint32_t grp, uint32_t cmd)
{
    return ((grp & WMI_ID_GRP_MASK) << WMI_ID_GRP_SHIFT) | (cmd & WMI_ID_CMD_MASK);
}

static inline uint32_t wmi_id_group(uint32_t id)
{
    return id >> WMI_ID_GRP_SHIFT;
}

static inline uint32_t wmi_id_cmd(uint32_t id)
{
    return id & WMI_ID_CMD_MASK;
}

static inline void wmi_id_split(uint32_t id, uint32_t *r5, uint32_t *r4)
{
    *r5 = id >> 8;
    *r4 = id & 0xff;
}

void wmi_model_init(wmi_dispatch_model_t *m);
int wmi_model_arm_head(wmi_dispatch_model_t *m);
int wmi_model_add_record(wmi_dispatch_model_t *m, uint32_t handler, uint32_t id);
const wmi_registry_record_t *wmi_model_find_record(const wmi_dispatch_model_t *m, uint32_t id);
uint32_t wmi_model_dispatch_event(wmi_dispatch_model_t *m, uint32_t id);

#endif
