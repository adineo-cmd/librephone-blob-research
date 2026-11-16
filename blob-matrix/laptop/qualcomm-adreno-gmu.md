# Qualcomm Adreno GMU microcode (laptop half)

Phase 2 (WORKORDER-002-laptop) — evidence class: METADATA (upstream SQL md5/size; no payload RE yet).

a619_gmu.bin (Adreno 619 GMU) appears on 5 laptop-half devices. The GMU microcode format has partial public context via the msm drm driver (a6xx_gmu documentation) but the microcode payload itself is undocumented. METADATA-LEVEL.

| device (vendor/model/build) | file | type | bytes | md5 (upstream) |
|---|---|---|---|---|
| realme/Realme_10_Pro (luigi) | a619_gmu.bin | GPU | 32768 | 9e23c52057bb573dee9ba31f1fdba4fa |
| realme/Realme_9_Pro (oscar) | a619_gmu.bin | GPU | 32768 | 9e23c52057bb573dee9ba31f1fdba4fa |
| sony/Xperia_1_II (pdx215) | a619_gmu.bin | GPU | 32768 | 9e23c52057bb573dee9ba31f1fdba4fa |
| sony/Xperia_5_II (pdx206) | a619_gmu.bin | GPU | 32768 | 9e23c52057bb573dee9ba31f1fdba4fa |
| sony/Xperia_5_III (pdx214) | a619_gmu.bin | GPU | 32768 | 9e23c52057bb573dee9ba31f1fdba4fa |

Every md5 above is the durable identification key — the same blob bytes shared across devices (see fragmentation-half analysis when it lands).
