# OnePlus 6 (enchilada) — Radio (RIL) surface

**Evidence class: census** (files extracted + hashed; content NOT analyzed —
SQL/config, not firmware). Source: LineageOS 22.2 nightly 2026-11-11 enchilada,
`/vendor/radio/qcril_database/`.

## Contents

| file | bytes |
|---|---|
| `qcril.db` | 126,976 |
| `upgrade/0_initial.sql` … `9_version_update_ecc_table.sql` | 691-67,038 (9 files, 155,935 total) |

A SQLite radio-config database plus its versioned SQL upgrade chain
(emergency-call table updates, WPS config). These are configuration
artifacts of the RIL stack, not radio firmware — kept in the census
because the upstream DB counts the same surface, but marked honestly:
nothing here is executable, nothing here is a blob in the firmware sense.

## ISA/proof status

Not applicable (data files).

## Open questions

- none for this family at census level; deep value only if the lab later
  models RIL config drift across devices.
