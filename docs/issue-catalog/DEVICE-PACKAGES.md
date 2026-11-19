# Device work packages — 2026-11-20

One package = one device or one sustained firmware-fleet RE task, designed for
hours of agent work rather than minute-scale micro-tasks. Replaces the 2,836
atomic issues described in `issues.jsonl`.

Machine-readable: `device-packages.jsonl` (276 rows).

| priority | packages |
|---|---|
| priority:deep-re | 24 |
| priority:high | 58 |
| priority:nonphone | 26 |

| area | packages |
|---|---|
| area:firmware | 266 |
| area:historic | 1 |
| area:site | 7 |
| area:soc | 2 |

| device type | packages |
|---|---|
| device-type:devkit | 7 |
| device-type:phone | 219 |
| device-type:sbc | 6 |
| device-type:tablet | 12 |
| device-type:tv_box | 1 |

## Selection

All 245 inventory models get a device package. Non-phone devices (TV box,
SBCs, devkits, tablets) are ordered first. Every one of the 9 firmware
families gets a fleet package, including the WiFi and modem fleets named in
the owner directive. 15 named RE open items are kept as deep packages.

## Claiming

See `docs/ISSUE-WORKFLOW.md`. One agent holds one device package for a
sustained session; claims are exclusive and partitioned by harness.
