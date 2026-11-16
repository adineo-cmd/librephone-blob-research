/* Clean-room, spec-derived implementation of the WCN6750 wpss WMI two-level
   dispatch architecture, from the lab's published spec only (papers/wmi-dispatch-architecture.md,
   qualcomm-fp6/docs/wmi-*); no proprietary code, headers, or strings were read. */
#include <stdio.h>
#include <string.h>
#include "wmi_dispatch.h"
#include "wmi_dispatch_tables.h"

void wmi_model_init(wmi_dispatch_model_t *m)
{
    memset(m, 0, sizeof(*m));
    m->pdev.table = wmi_pdev_table;
    m->pdev.table_len = WMI_PDEV_TABLE_LEN;
    m->pdev.table_vaddr = WMI_PDEV_TABLE_VADDR;
    m->stats.table = wmi_stats_table;
    m->stats.table_len = WMI_STATS_TABLE_LEN;
    m->stats.table_vaddr = WMI_STATS_TABLE_VADDR;
    m->shared_exit_block = WMI_SHARED_EXIT_BLOCK;
    m->shared_exit_jump = WMI_SHARED_EXIT_JUMP;
    m->head.base = WMI_REGISTRY_HEAD_BASE;
    m->head.word_0x8 = 0xffffu;
    m->head.word_0xc = 0x1u;
    m->head.records_ptr = WMI_REGISTRY_RECORDS_PTR;
    m->head.word_0x24 = 0x45u;
    m->head.main_run_anchor = WMI_REGISTRY_MAIN_RUN;
}

static uint32_t setbit(uint32_t word, uint32_t bit)
{
    return word | (1u << bit);
}

int wmi_model_arm_head(wmi_dispatch_model_t *m)
{
    uint32_t t0 = WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_0;
    uint32_t t1 = WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_1;
    uint32_t t2 = WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_2;
    if (t0 != 0xc0691140u || t1 != 0xc069116cu || t2 != 0xc0691180u)
        return -1;
    m->head.enable_masks[0] = setbit(m->head.enable_masks[0], 1);
    m->head.enable_masks[1] = setbit(m->head.enable_masks[1], 1);
    m->head.enable_masks[2] = setbit(m->head.enable_masks[2], 1);
    return 0;
}

int wmi_model_add_record(wmi_dispatch_model_t *m, uint32_t handler, uint32_t id)
{
    if (m->record_count >= WMI_REG_MAX_RECORDS)
        return -1;
    wmi_registry_record_t *r = &m->records[m->record_count++];
    r->handler = handler;
    r->id = id;
    r->zero = 0;
    return 0;
}

const wmi_registry_record_t *wmi_model_find_record(const wmi_dispatch_model_t *m, uint32_t id)
{
    for (uint32_t i = 0; i < m->record_count; i++) {
        if (m->records[i].id == id)
            return &m->records[i];
    }
    return NULL;
}

static const wmi_table_entry_t *table_lookup(const wmi_dispatcher_t *d, uint32_t id,
                                             int *in_bounds)
{
    uint32_t idx = (id & 0xffu) - 1u;
    *in_bounds = idx < d->table_len;
    if (!*in_bounds)
        return NULL;
    const wmi_table_entry_t *e = &d->table[idx];
    if (e->id != id)
        return NULL;
    return e;
}

static const wmi_cmp_entry_t *cmp_tree_lookup(uint32_t id)
{
    for (uint32_t i = 0; i < WMI_CMP_TREE_LEN; i++) {
        if (wmi_cmp_tree[i].id == id)
            return &wmi_cmp_tree[i];
    }
    return NULL;
}

uint32_t wmi_model_dispatch_event(wmi_dispatch_model_t *m, uint32_t id)
{
    uint32_t r5, r4;
    wmi_id_split(id, &r5, &r4);
    m->dispatch_count++;

    if (r5 == (WMI_GRP_PDEV << 4)) {
        int in_bounds;
        const wmi_table_entry_t *e = table_lookup(&m->pdev, id, &in_bounds);
        if (!in_bounds)
            return m->shared_exit_block;
        if (e && e->handled)
            return e->handler;
        return m->shared_exit_block;
    }
    if (r5 == (WMI_GRP_STATS << 4)) {
        int in_bounds;
        const wmi_table_entry_t *e = table_lookup(&m->stats, id, &in_bounds);
        if (!in_bounds)
            return m->shared_exit_block;
        if (e && e->handled)
            return e->handler;
        return m->shared_exit_block;
    }
    const wmi_cmp_entry_t *c = cmp_tree_lookup(id);
    if (c) {
        if (c->kind == WMI_CMP_KIND_BLOCK || c->kind == WMI_CMP_KIND_CALL)
            return c->block;
        return 0;
    }
    return m->shared_exit_block;
}

static int failures;

static void check(const char *what, uint32_t got, uint32_t want)
{
    if (got != want) {
        printf("FAIL %s: got 0x%08x want 0x%08x\n", what, got, want);
        failures++;
    } else {
        printf("ok   %s = 0x%08x\n", what, got);
    }
}

int main(void)
{
    wmi_dispatch_model_t m;
    wmi_model_init(&m);

    check("id_build(PDEV,1)", wmi_id_build(WMI_GRP_PDEV, 1), 0x4001u);
    check("id_group(0x16001)", wmi_id_group(0x16001u), 0x16u);
    uint32_t r5, r4;
    wmi_id_split(0x16001u, &r5, &r4);
    check("split_r5(0x16001)", r5, 0x160u);
    check("split_r4(0x16001)", r4, 0x01u);

    uint32_t handled = 0;
    for (uint32_t i = 0; i < WMI_PDEV_TABLE_LEN; i++)
        handled += wmi_pdev_table[i].handled ? 1 : 0;
    check("pdev_handled", handled, 41u);
    handled = 0;
    for (uint32_t i = 0; i < WMI_STATS_TABLE_LEN; i++)
        handled += wmi_stats_table[i].handled ? 1 : 0;
    check("stats_handled", handled, 9u);
    check("cmp_tree_len", WMI_CMP_TREE_LEN, 11u);

    check("dispatch 0x4001", wmi_model_dispatch_event(&m, 0x4001u), 0xc02cdbc8u);
    check("dispatch 0x4002", wmi_model_dispatch_event(&m, 0x4002u), 0xc02ce968u);
    check("dispatch 0x4004 (unhandled)", wmi_model_dispatch_event(&m, 0x4004u), WMI_SHARED_EXIT_BLOCK);
    check("dispatch 0x16001", wmi_model_dispatch_event(&m, 0x16001u), 0xc02cdc6cu);
    check("dispatch 0x16002 (unhandled)", wmi_model_dispatch_event(&m, 0x16002u), WMI_SHARED_EXIT_BLOCK);
    check("dispatch 0x5022", wmi_model_dispatch_event(&m, 0x5022u), 0xc02cb6dcu);
    check("dispatch 0x1d00b", wmi_model_dispatch_event(&m, 0x1d00bu), 0xc02cdfb4u);
    check("dispatch 0x1d019", wmi_model_dispatch_event(&m, 0x1d019u), 0xc02cdffcu);
    check("dispatch 0x1d014 (call-tail)", wmi_model_dispatch_event(&m, 0x1d014u), 0xc02cf388u);
    check("dispatch 0x11001 (runtime)", wmi_model_dispatch_event(&m, 0x11001u), 0x0u);
    check("dispatch 0x11002 (call)", wmi_model_dispatch_event(&m, 0x11002u), 0xc04913e4u);
    check("dispatch 0x1e001 (runtime)", wmi_model_dispatch_event(&m, 0x1e001u), 0x0u);
    check("dispatch 0x3001 (other grp)", wmi_model_dispatch_event(&m, 0x3001u), WMI_SHARED_EXIT_BLOCK);
    check("dispatch OOB 0x40ff", wmi_model_dispatch_event(&m, 0x40ffu), WMI_SHARED_EXIT_BLOCK);
    check("dispatch unknown misc", wmi_model_dispatch_event(&m, 0x1d00cu), WMI_SHARED_EXIT_BLOCK);

    check("arm targets 0", WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_0, 0xc0691140u);
    check("arm targets 1", WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_1, 0xc069116cu);
    check("arm targets 2", WMI_REGISTRY_ARM_BASE + WMI_REGISTRY_ARM_OFFSETS_2, 0xc0691180u);
    check("arm ok", wmi_model_arm_head(&m) == 0 ? 1u : 0u, 1u);
    check("mask set", m.head.enable_masks[0], 0x2u);

    check("add record", wmi_model_add_record(&m, 0xc02cd9ccu, 0x4001u) == 0 ? 1u : 0u, 1u);
    check("add record 2", wmi_model_add_record(&m, 0xc02cd9ccu, 0x4002u) == 0 ? 1u : 0u, 1u);
    const wmi_registry_record_t *r = wmi_model_find_record(&m, 0x4002u);
    check("find record handler", r ? r->handler : 0, 0xc02cd9ccu);
    check("record zero word", r ? r->zero : 1, 0u);
    r = wmi_model_find_record(&m, 0x4fffu);
    check("find miss", r == NULL ? 1u : 0u, 1u);

    if (failures) {
        printf("SELFTEST FAILURES: %d\n", failures);
        return 1;
    }
    printf("ALL SELFTESTS PASSED\n");
    return 0;
}
