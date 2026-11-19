# PR-7 filing package — data/sizes.csv: the Fairphone FP6 rows (2026-11-16)

Third upstream contribution package, executing item **L-1** of the
2026-11-15 wants audit ([librephone-wants.md](librephone-wants.md), row
B-10): upstream `data/sizes.csv` (branch `main`, 15,071 data rows,
fetched 2026-11-16) carries **zero FP6 rows** while `data/devices.csv`
has 444 FP6 rows and upstream's own per-file docs already analyze the
FP6 blob set. The lab's committed censuses record every FP6 firmware
file with its byte size.

## Upstream format (matched exactly)

Fetched 2026-11-16:
https://codeberg.org/rsavoye/librephone/raw/branch/main/data/sizes.csv
(the file lives on branch `main`; branch `master` does not exist). Header:

```
vendor,model,build,path,file,size,md5sum,type,released
```

FP4/FP5 precedences used: `vendor=Fairphone`, `model=FP6`,
`build=FP6`, `released=2026`; `path` is the partition-relative directory
(`radio`, `modem/image`, `modem/image/qca6750`, `bluetooth/image`,
`vendor/firmware`, `dsp/adsp`, `dsp/cdsp`, `modem/verinfo`); `type`
labels reuse upstream's existing vocabulary with the FP5 row choices
copied wherever the same path/file kind exists on FP5.

## One honest gap: the md5sum column

The lab's committed census recorded **full sha256** per file
(`qualcomm-fp6/tools/census.py`) but its markdown table truncates to
16 hex digits, and the FP6 extraction tree is not present on this
session's box — so **no md5 value could be computed here** and none is
invented. Every row below ships with the literal token `PENDING` in the
`md5sum` column **except zero-byte files**, whose md5 is the universal
empty-input value `d41d8cd98f00b204e9800998ecf8427e` (13 rows).

Fill-in before filing is one command against the same public nightly
(see "Reproduce" in any lab census doc):

```bash
# after re-extracting trees/ from lineage-23.2-20261109-nightly-FP6-signed.zip:
find trees -type f -exec md5sum {} +   # map tree paths -> sizes.csv (path,file)
```

The sizes themselves are complete and byte-exact for all 702 rows; the
per-file sha256 (full, from the same run) lives in the lab census and is
linked per family below, so any reviewer can cross-check sizes now and
hashes after the re-hash.

---

## PR text (paste-ready)

```
data/sizes.csv: add Fairphone FP6 rows

data/devices.csv already has 444 FP6 rows and the per-file docs analyze
this device, but sizes.csv has no FP6 row. This adds 702 rows (665 files
from the modem/vendor/dsp partitions + 18 radio/boot partitions + 7
TrustZone partitions + the bluetooth partition + its 11 files) for the
public LineageOS FP6 nightly lineage-23.2-20261109.

Sizes and paths are complete; the md5sum column carries PENDING for the
files where the source census recorded sha256 (full value, committed
upstream in the lab's census files) rather than md5, plus the md5-of-
empty-file constant for the 13 zero-byte files. The hashes are one
`md5sum` pass over the same public nightly (commands in the source
census docs); every size is traceable today.

Per-family provenance (sizes + per-file sha256):
- modem/image, modem/image/qca6750, vendor/firmware, dsp/adsp,
  dsp/cdsp, modem/verinfo (665 rows):
  https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/results/census.md
- radio boot-chain partitions xbl/xbl_config/xbl_ramdump/uefi/abl/
  imagefv/shrm/aop/aop_config/cpucp/cpucp_dtb/qupfw + boot/vendor_boot/
  dtbo/pvmfw/vbmeta/vbmeta_system (18 rows):
  https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bootchain-census.md
- TrustZone partitions tz/hyp/keymaster/devcfg/uefisecapp/multiimgoem/
  featenabler (7 rows):
  https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/trustzone-census.md
- bluetooth partition + bluetooth/image (12 rows):
  https://github.com/adineo-cmd/librephone-blob-research/blob/main/qualcomm-fp6/docs/bt-firmware-census.md

Type labels follow the FP5 row choices where the same kind of file
exists on FP5 (abl/xbl=UEFIBOOT, boot=BOOT, tz=BOOT, hyp=SECUREBOOT,
keymaster=SECURITY, dtbo=DTB, vbmeta=AVB, modem/image=MODEM,
bluetooth/image=UNKNOWN, haptic_*=FIRMWARE, aw882xx_acf.bin=CODEC);
labels for kinds FP5 does not have were assigned as UNKNOWN/COMPUTE/GPU
per file kind and are trivially adjustable.
```

---

## The rows (paste-ready — 702 data rows)

```
vendor,model,build,path,file,size,md5sum,type,released
Fairphone,FP6,FP6,dsp/adsp,AudioSphereModule.so.1,81016,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,CFCM.so.1,31952,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,SAPlusCmnModule.so.1,125592,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aac_dec_module.so.1,271352,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aac_enc_etsi_module.so.1,209888,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,alac_dec_module.so.1,31536,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,amrwbplus_dec_module.so.1,178176,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,ans_module.so.1,166328,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,ape_dec_module.so.1,48952,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aptx_adaptive_enc_module.so.1,175984,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aptx_adaptive_speech_dec_module.so.1,202552,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aptx_adaptive_speech_enc_module.so.1,182168,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aptx_classic_enc_module.so.1,41776,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,aptx_hd_enc_module.so.1,40976,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,celt_enc_module.so.1,89120,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,cps_module.so.1,293112,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fastrpc_shell_0,1219384,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,ffecns_module_VUI_viii.so.1,402840,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,flac_dec_module.so.1,41688,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fluence_bs_module_fvxiii.so.1,344024,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fluence_ef_module_fvxiii.so.1,504448,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fluence_nn_module_fvxiii.so.1,498176,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fluence_pro_vc_module_fvxiii.so.1,408544,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,fluence_pro_vr_module_fvxiii.so.1,378552,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,haptics_module.so.1,133904,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,hdr_module.so.1,157144,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,lc3_dec_module.so.1,192752,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,lc3_enc_module.so.1,345776,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,ldac_enc_module.so.1,81952,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libaptXAdaptiveEnc.so,271424,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libaptXAdaptiveEnc3.so,94464,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libc++.so.1,3895768,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libc++abi.so.1,864864,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,liblc3qDec.so,163040,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsns_device_mode_skel.so,19880,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsns_direct_channel_skel.so,17496,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsns_dynamic_loader_skel.so,20408,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsns_remote_proc_state_skel.so,19720,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libstabilitydomain_skel.so,123312,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsysmondomain_skel.so,466104,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,libsysmonquery_skel.so,46472,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,lsm6dso.so,685144,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,lsm6dso_island.so,419784,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,lsm6dso_normal.so,307472,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,mm_fluence_sb_module_fvxiii.so.1,445632,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,msppv4_module.so.1,341816,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,opus_dec_module.so.1,163456,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,sbc_dec_module.so.1,47344,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,sbc_enc_module.so.1,40512,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,sdd_module.so.1,35248,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,sm_fluence_sb_module_fvxiii.so.1,289184,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,smecns_v2_module_fvxiii.so.1,277184,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,sns_tppe.so,268368,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,spf-aptx-adaptive3-ble-enc.so.1,163800,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,spv5_module.so.1,293112,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,tsm_module.so.1,91480,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,vocoder_evrc_module.so.1,122040,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,vocoder_fourgv_module.so.1,518912,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,vocoder_v13k_module.so.1,97792,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,vorbis_dec_module.so.1,87904,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,wmapro_dec_module.so.1,365728,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/adsp,wmastd_dec_module.so.1,131360,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,example_image.so,57000,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,example_image_runner.so,61576,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,fastrpc_shell_3,1303040,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,fastrpc_shell_unsigned_3,1298776,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libbenchmark_skel.so,4630808,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libc++.so.1,3337296,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libc++abi.so.1,820728,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libcrm_test_skel.so,87560,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libloadalgo_skel.so,52368,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libstabilitydomain_skel.so,106832,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libsysmondomain_skel.so,3967512,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libsysmondspload_skel.so,75312,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libsysmonhvxthrottle_skel.so,20072,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,libsysmonquery_skel.so,45064,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,dsp/cdsp,version.so,6952,PENDING,COMPUTE,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b00,568,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b01,48626,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b02,257,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b03,728,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b04,3792,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b05,304,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b06,8723,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b07,728,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.b08,4184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,05B04A44-BF30-42DF-9E2F-B366B980ED19.mdt,4752,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b00,568,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b01,31357,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b02,263,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b03,520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b04,912,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b05,304,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b06,5352,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b07,520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.b08,4184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,32552B22-89FE-42B4-8A45-A0C4E2DB0326.mdt,4752,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b00,568,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b01,56507,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b02,260,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b03,720,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b04,2272,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b05,304,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b06,10078,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b07,720,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.b08,4184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,FD719D50-FFFB-11EB-9A03-0242AC130003.mdt,4752,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b00,1588,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b01,21044,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b02,65948,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b03,88360,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b04,28372,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b05,43088,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b06,8192,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b07,240,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b08,9204,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b09,2511956,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b10,259932,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b11,2520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b12,12440,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b13,1692,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b14,145896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b15,130944,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b16,65536,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b17,2398756,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b18,37068,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b19,272,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b20,341051,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b21,131072,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b22,2175432,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b23,294916,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b25,108,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b26,1923,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b27,26768,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b28,216384,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b29,140260,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b30,4701,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b31,14560,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b32,6560,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b33,52328,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b34,64,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b35,229376,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b36,6386356,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b37,258056,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b38,244,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b39,8700,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b40,5708,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b41,100480,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b42,238807,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b43,12280,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b44,22632,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b45,559104,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.b47,6056,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp.mdt,7644,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp_dtb.b00,148,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp_dtb.b01,93164,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp_dtb.b02,3896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsp_dtb.mdt,4044,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adspr.jsn,513,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adsps.jsn,515,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,adspua.jsn,703,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,battmgr.jsn,516,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b00,564,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b01,24768,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b02,73124,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b03,122947,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b04,1192,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b05,1883844,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b06,94216,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b07,2648,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b08,111254,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b09,767676,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b10,13816,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b11,3152,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b12,103312,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b13,4576,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.b15,4520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp.mdt,5084,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp_dtb.b00,148,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp_dtb.b01,62764,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp_dtb.b02,3896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdsp_dtb.mdt,4044,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cdspr.jsn,513,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cpusys_vm.b00,180,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cpusys_vm.b01,516096,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cpusys_vm.b02,5845,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cpusys_vm.b03,10992,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,cpusys_vm.mdt,11172,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,evautil64.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b01,9992,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b02,213,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b03,392,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b04,904,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b06,4203,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b07,392,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,evautil64.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b01,61830,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b02,223,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b03,528,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b04,913,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b06,10617,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b07,528,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.b08,11232,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,featenabler.mdt,11800,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b01,2525292,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b02,261,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b03,2968,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b04,933144,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b06,121220,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b07,2968,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,focal64.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,fw_ipa_gsi_5.2_m.elf,36760,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,gptauuid.xml,10888,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b00,568,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b01,31552,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b02,214,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b03,536,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b04,5760,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b05,304,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b06,7096,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b07,536,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.b08,4184,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp1.mdt,4752,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b00,568,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b01,118778,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b02,247,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b03,1776,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b04,7680,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b05,304,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b06,18517,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b07,1776,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.b08,4184,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcp2p2.mdt,4752,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b00,568,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b01,22981,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b02,225,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b03,472,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b04,904,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b05,304,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b06,5164,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b07,472,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.b08,4184,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,hdcpsrm.mdt,4752,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,ic5.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b01,103517,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b02,232,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b03,1200,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b04,7745,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b06,6687,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b07,1200,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ic5.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.b00,212,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.b01,16696,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.b02,128,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.b03,1000,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.b04,3992,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ipa_fws.mdt,4204,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b01,40824,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b02,225,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b03,424,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b04,13392,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b06,4440,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b07,424,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,loadalgota64.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image/milos,qdsp6m.qdb,6506187,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b00,1044,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b01,7012,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b02,812180,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b03,19548,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b04,16700,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b05,12284,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b06,34896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b07,122880,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b08,2490436,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b09,36928,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b10,147456,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b11,3983696,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b12,131072,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b13,4587520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b15,3936928,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b16,473624,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b17,1044480,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b18,12520508,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b19,12412695,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b20,4968456,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b22,99136,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b23,39608384,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b24,28947136,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b25,1293698,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b26,8988,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b27,311552,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b28,11272,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.b30,5240,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modem.mdt,6284,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDA_Hybrid,mcfg_hw.mbn,36752,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDA_Hybrid_CDMALess,mcfg_hw.mbn,35916,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDA_Hybrid_SAOnly,mcfg_hw.mbn,37572,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDS,mcfg_hw.mbn,31092,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDS_CDMALess,mcfg_hw.mbn,31152,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/DSDS_SAOnly,mcfg_hw.mbn,31884,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/SS,mcfg_hw.mbn,23896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/SS_CDMALess,mcfg_hw.mbn,23688,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw/generic/common/Milos/STANDALONE/LA/SS_SAOnly,mcfg_hw.mbn,24732,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw,mbn_hw.dig,32,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_hw,mbn_hw.txt,610,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/AF/CellC/Commercial/SAfrica,mcfg_sw.mbn,43816,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/AF/MoroccoTel/Commercial/MA,mcfg_sw.mbn,43736,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/APAC/DCM/Commercial,mcfg_sw.mbn,55680,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/APAC/KDDI/Commercial,mcfg_sw.mbn,63096,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/APAC/Rakuten/Commercial,mcfg_sw.mbn,56848,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/APAC/Reliance/Commercial,mcfg_sw.mbn,62304,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/APAC/SBM/Commercial,mcfg_sw.mbn,55476,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/AUNZ/Optus/Commercial/AU,mcfg_sw.mbn,49328,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/AUNZ/Telstra/Commercial,mcfg_sw.mbn,52160,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/AUNZ/Vodafone/Commercial,mcfg_sw.mbn,48280,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CBN/Commercial,mcfg_sw.mbn,53020,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Commercial/Volte_OpenMkt,mcfg_sw.mbn,58116,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/AGNSS_LocTech,mcfg_sw.mbn,23616,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/Conf_VoLTE,mcfg_sw.mbn,51912,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/EPS_Only,mcfg_sw.mbn,20376,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/LPP_LocTech,mcfg_sw.mbn,23624,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/Nsiot_4RX_VoLTE,mcfg_sw.mbn,49112,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/Nsiot_VoLTE,mcfg_sw.mbn,50548,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/RRLP_LocTech,mcfg_sw.mbn,23616,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/TGL_Comb_Attach,mcfg_sw.mbn,20876,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CMCC/Lab/W_IRAT_Comb_Attach,mcfg_sw.mbn,20460,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Commercial/OpenMkt,mcfg_sw.mbn,49092,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Commercial/VoLTE_OpenMkt,mcfg_sw.mbn,84084,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Commercial/hVoLTE_OpenMkt,mcfg_sw.mbn,81932,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/CTA,mcfg_sw.mbn,43388,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/EPS_Only_VoLTE_Conf,mcfg_sw.mbn,60216,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/NoAPN_Vo_Conf,mcfg_sw.mbn,58140,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/TEST,mcfg_sw.mbn,44628,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/TEST_EPS_ONLY,mcfg_sw.mbn,47136,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/TEST_NO_APN,mcfg_sw.mbn,43000,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CT/Lab/VoLTE_Conf,mcfg_sw.mbn,61324,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CU/Commercial/OpenMkt,mcfg_sw.mbn,24012,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CU/Commercial/VoLTE,mcfg_sw.mbn,52796,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/China/CU/Lab/Test,mcfg_sw.mbn,18604,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/1_1/Commercial,mcfg_sw.mbn,47572,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/A1/Commercial/AT,mcfg_sw.mbn,48732,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Bouygues/Commercial/France,mcfg_sw.mbn,56556,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/Austria,mcfg_sw.mbn,55168,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/CZ,mcfg_sw.mbn,52124,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/Croatia,mcfg_sw.mbn,50240,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/Greece,mcfg_sw.mbn,51496,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/Hungary,mcfg_sw.mbn,49792,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/NL,mcfg_sw.mbn,53892,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/PL,mcfg_sw.mbn,50664,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/Commercial/Slovakia,mcfg_sw.mbn,39700,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/DT/VoLTE/Commercial,mcfg_sw.mbn,55400,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/EE/Commercial,mcfg_sw.mbn,53524,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Elisa/Commercial/FI,mcfg_sw.mbn,51548,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/H3G/Commercial/Austria,mcfg_sw.mbn,46196,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/H3G/Commercial/Denmark,mcfg_sw.mbn,49508,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/H3G/Commercial/Italy,mcfg_sw.mbn,50976,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/H3G/Commercial/SE,mcfg_sw.mbn,48520,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/H3G/Commercial/UK,mcfg_sw.mbn,46332,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/KPN/VoLTE/Netherlands,mcfg_sw.mbn,52868,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/Belgium,mcfg_sw.mbn,55184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/France,mcfg_sw.mbn,60028,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/Poland,mcfg_sw.mbn,55092,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/Romania,mcfg_sw.mbn,51896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/Slovakia,mcfg_sw.mbn,48208,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Orange/Commercial/Spain,mcfg_sw.mbn,52932,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Proximus/VoLTE/Belgium,mcfg_sw.mbn,54828,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/SFR/Commercial/FR,mcfg_sw.mbn,53956,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Sky/Commercial/UK,mcfg_sw.mbn,58616,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Swisscom/Commercial/Swiss,mcfg_sw.mbn,53580,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/TDC/Commercial/Denmark,mcfg_sw.mbn,51128,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/TDC/Commercial/Switzerland,mcfg_sw.mbn,52948,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/TIM/Commercial/Italy,mcfg_sw.mbn,50108,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Tele2/Commercial/NL,mcfg_sw.mbn,48920,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Tele2/Commercial/Sweden,mcfg_sw.mbn,45532,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telefonica/Commercial/DE,mcfg_sw.mbn,51148,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telefonica/Commercial/Spain,mcfg_sw.mbn,51324,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telefonica/Commercial/UK,mcfg_sw.mbn,52464,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telenor/Commercial/Denmark,mcfg_sw.mbn,50028,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telenor/Commercial/Norway,mcfg_sw.mbn,51488,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telenor/Commercial/Sweden,mcfg_sw.mbn,55184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telia/Commercial/Norway,mcfg_sw.mbn,50564,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Telia/Commercial/Sweden,mcfg_sw.mbn,50612,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/Commercial/Hungary,mcfg_sw.mbn,40120,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/Commercial/Ireland,mcfg_sw.mbn,49068,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/Commercial/PostLU,mcfg_sw.mbn,49456,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/M2M/Commercial/Global,mcfg_sw.mbn,42796,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/Non_VoLTE,mcfg_sw.mbn,23940,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/CZ,mcfg_sw.mbn,49076,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Ger_Ts,mcfg_sw.mbn,59144,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Germany,mcfg_sw.mbn,59060,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Italy,mcfg_sw.mbn,40524,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Netherlands,mcfg_sw.mbn,58412,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Portugal,mcfg_sw.mbn,40712,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/SAfrica,mcfg_sw.mbn,50568,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Spain,mcfg_sw.mbn,50940,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/Turkey,mcfg_sw.mbn,47348,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/EU/Vodafone/VoLTE/UK,mcfg_sw.mbn,53916,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Korea/KT/Commercial_KT_LTE,mcfg_sw.mbn,38772,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Korea/LGU/Commercial,mcfg_sw.mbn,39636,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Korea/SKT/Commercial,mcfg_sw.mbn,39764,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/AMX/Commercial/MX,mcfg_sw.mbn,46032,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/AMX/Non_VoLTE,mcfg_sw.mbn,10092,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/Claro/Commercial/Colombia,mcfg_sw.mbn,46364,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/TIM/Commercial/Brazil,mcfg_sw.mbn,38492,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/Telefonica/Commercial/Colombia,mcfg_sw.mbn,38260,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/LATAM/Telefonica/Commercial/Peru,mcfg_sw.mbn,44864,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/MEA/STC/Commercial/SA,mcfg_sw.mbn,43816,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/Cricket,mcfg_sw.mbn,52908,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/FirstNet,mcfg_sw.mbn,57736,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/FirstNet_American_Samoa,mcfg_sw.mbn,58892,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/FirstNet_Guam_CNMI,mcfg_sw.mbn,58864,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/Non_VoLTE,mcfg_sw.mbn,27324,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/ATT/VoLTE,mcfg_sw.mbn,70976,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Bell/Commercial/CA,mcfg_sw.mbn,51280,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/CBRS/Commercial/US,mcfg_sw.mbn,18480,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Dish/Commercial/US,mcfg_sw.mbn,52372,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Rogers/Commercial/CA,mcfg_sw.mbn,56472,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Sprint/Commercial,mcfg_sw.mbn,60872,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Sprint/VoWiFi,mcfg_sw.mbn,60860,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Sprint/VoWiFi_A,mcfg_sw.mbn,60872,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Sprint/VoWiFi_B,mcfg_sw.mbn,60872,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/TMO/Commercial,mcfg_sw.mbn,60864,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Telus/Commercial/CA,mcfg_sw.mbn,49412,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/USCC/Commercial,mcfg_sw.mbn,49620,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Verizon/CDMAless,mcfg_sw.mbn,77084,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Verizon/IMSless,mcfg_sw.mbn,39336,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/NA/Verizon/hVoLTE,mcfg_sw.mbn,82768,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Russia/Beeline/Gen_3GPP,mcfg_sw.mbn,47268,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Russia/MTS/Commercial/RU,mcfg_sw.mbn,45200,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Russia/MegaFon/Commercial/RU,mcfg_sw.mbn,45140,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SA/Brazil/Commercial,mcfg_sw.mbn,9244,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/3HK/Commercial/HK,mcfg_sw.mbn,46052,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/AIS/Commercial/Thailand,mcfg_sw.mbn,47928,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/APT/Commercial,mcfg_sw.mbn,45796,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Axiata/Commercial/IDN,mcfg_sw.mbn,39392,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/ChunghwaTel/Commercial/TW,mcfg_sw.mbn,48184,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/DTAC/Commercial/VoLTE,mcfg_sw.mbn,44888,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/FarEastOne/Commercial,mcfg_sw.mbn,46900,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Globe/Commercial/PH,mcfg_sw.mbn,46180,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/HKT/Commercial/HK,mcfg_sw.mbn,45432,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Indosat/Commercial/IDN,mcfg_sw.mbn,39504,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/M1/Commercial/SG,mcfg_sw.mbn,38284,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/P1/Commercial/Malaysia,mcfg_sw.mbn,38400,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Singtel/Commercial/Singapore,mcfg_sw.mbn,49196,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/SmarTone/Commercial/HK,mcfg_sw.mbn,45404,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Smartfren/Commercial/VoWiFi,mcfg_sw.mbn,46132,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Smartfren/Commercial,mcfg_sw.mbn,47316,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/StarHub/Commercial/SG,mcfg_sw.mbn,45072,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/TM/Commercial,mcfg_sw.mbn,47072,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/TStar/Commercial/TW,mcfg_sw.mbn,38896,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Telkomsel/Commercial/IDN,mcfg_sw.mbn,48176,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Truemove/Commercial/VoLTE,mcfg_sw.mbn,44316,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/UMobile/Commercial/Malaysia,mcfg_sw.mbn,47344,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/Viettel/Commercial/Vietnam,mcfg_sw.mbn,45548,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/SEA/YTL/Commercial,mcfg_sw.mbn,45068,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Test/ER_IOT,mcfg_sw.mbn,47552,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/Test/NK_IOT,mcfg_sw.mbn,47404,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/common/CustomLab/Commercial,mcfg_sw.mbn,78848,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/common/ROW/Commercial,mcfg_sw.mbn,46576,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw/generic/common/W_One/Commercial,mcfg_sw.mbn,40268,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw,mbn_sw.dig,32,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw,mbn_sw.txt,8357,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/mcfg/configs/mcfg_sw,oem_sw.txt,7538,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/so,902_0_0.mbn,604424,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/so,902_0_1.mbn,604424,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image/modem_pr/so,902_0_2.mbn,625376,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,modemr.jsn,710,PENDING,MODEM,2026
Fairphone,FP6,FP6,modem/image,ops.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b01,9416,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b02,202,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b03,344,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b04,912,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b06,3806,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b07,344,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,ops.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image/qca6750,Data.msc,1159404,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b01,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b02,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b03,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b04,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b05,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b06,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b07,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b08,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b09,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0a,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0b,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0c,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0d,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0e,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b0f,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b10,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b101,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b12,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b13,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b14,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b15,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b16,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b17,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b18,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b19,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b20,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b21,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.b22,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.bin,58180,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e01,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e02,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e03,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e04,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e05,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e06,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e07,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e08,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e09,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0a,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0b,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0c,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0d,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0e,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e0f,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e10,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e101,60004,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e12,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e13,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e14,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e15,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e16,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e17,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e18,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e19,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e20,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e21,59932,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.e22,59868,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan.elf,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,bdwlan_fcc.elf,60000,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,qdss_trace_config.cfg,1813,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,modem/image/qca6750,regdb.bin,24278,PENDING,WIFI_BLUETOOTH,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b00,468,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b01,6440,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b02,461049,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b03,1104,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b04,256,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b05,4096,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b06,6074641,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b07,139316,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b08,275644,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b09,360960,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b10,909398,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.b12,4376,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.mdt,4844,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image/qca6750,wpss.qdb,528,PENDING,WIFI,2026
Fairphone,FP6,FP6,modem/image,sbservice.mbn,36952,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b01,363256,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b02,245,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b03,10760,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b04,1494060,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b06,90642,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b07,10760,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,smplap64.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b01,59576,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b02,218,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b03,912,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b04,1736,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b06,6751,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b07,912,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,soter64.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b01,9668,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b02,217,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b03,408,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b04,896,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b06,4271,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b07,408,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,sp_license.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,widevine.mbn,256992,PENDING,DRM,2026
Fairphone,FP6,FP6,modem/image,winsecap.b00,568,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b01,28272,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b02,232,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b03,544,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b04,3344,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b05,304,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b06,6584,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b07,544,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.b08,4184,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/image,winsecap.mdt,4752,PENDING,SECURITY,2026
Fairphone,FP6,FP6,modem/verinfo,ver_info.txt,1233,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b00,724,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b01,460,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b02,16,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b03,16,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b04,16,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b05,20,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b06,24,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b07,16,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b08,433784,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b09,27652,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b10,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b11,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b12,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b13,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b14,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b15,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b16,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b17,24084,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b18,21476,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b19,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.b20,4760,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.elf,3306937,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.mbn,516760,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP.mdt,5484,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,CAMERA_ICP_170.elf,4179544,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,EPH86XX_fw.bin,206490,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,aw882xx_acf.bin,4328,PENDING,CODEC,2026
Fairphone,FP6,FP6,vendor/firmware,aw_cali.bin,0,d41d8cd98f00b204e9800998ecf8427e,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,gen70900_aqe.fw,33176,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen70900_sqe.fw,85364,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen70900_zap.mbn,12088,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen71100_gmu.bin,80680,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen71100_sqe.fw,67348,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen71100_zap.mbn,12088,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen80300_gmu.bin,88708,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen80300_sqe.fw,85844,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gen80300_zap.mbn,12088,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,gmu_gen70900.bin,78588,PENDING,GPU,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_ram.bin,1719,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_rtp.bin,1444518,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_rtp_auto_sin.bin,100,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_rtp_lighthouse.bin,1444518,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_rtp_osc_24K_5s.bin,120000,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,haptic_rtp_silk.bin,1444518,PENDING,FIRMWARE,2026
Fairphone,FP6,FP6,vendor/firmware,sec_s3nrn4v_firmware.bin,184620,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu20_2v.mbn,2036328,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu20_2v_unsigned.mbn,2029140,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu20_4v.mbn,2036328,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu20_4v_unsigned.mbn,2027972,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu30_2v.mbn,2331336,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu30_2v_unsigned.mbn,2324688,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu33_4v.mbn,2339528,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware,vpu33_4v_unsigned.mbn,2331216,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,vendor/firmware/wlan/qca_cld,WCNSS_qcom_cfg.ini,0,d41d8cd98f00b204e9800998ecf8427e,WIFI,2026
Fairphone,FP6,FP6,vendor/firmware/wlan/qca_cld/qca6750,WCNSS_qcom_cfg.ini,0,d41d8cd98f00b204e9800998ecf8427e,WIFI,2026
Fairphone,FP6,FP6,vendor/firmware/wlan/qca_cld/qca6750,wlan_mac.bin,0,d41d8cd98f00b204e9800998ecf8427e,WIFI,2026
Fairphone,FP6,FP6,vendor/firmware,wlanmdsp.otaupdate,0,d41d8cd98f00b204e9800998ecf8427e,WIFI,2026
Fairphone,FP6,FP6,radio,abl.img,245760,PENDING,UEFIBOOT,2026
Fairphone,FP6,FP6,radio,aop.img,319488,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,aop_config.img,20480,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,boot.img,100663296,PENDING,BOOT,2026
Fairphone,FP6,FP6,radio,cpucp.img,204800,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,cpucp_dtb.img,12288,PENDING,DTB,2026
Fairphone,FP6,FP6,radio,dtbo.img,31457280,PENDING,DTB,2026
Fairphone,FP6,FP6,radio,imagefv.img,53248,PENDING,UEFIBOOT,2026
Fairphone,FP6,FP6,radio,pvmfw.img,1048576,PENDING,BOOT,2026
Fairphone,FP6,FP6,radio,qupfw.img,61440,PENDING,ELF64,2026
Fairphone,FP6,FP6,radio,shrm.img,53248,PENDING,ELF64,2026
Fairphone,FP6,FP6,radio,uefi.img,2904064,PENDING,UEFIBOOT,2026
Fairphone,FP6,FP6,radio,vbmeta.img,12288,PENDING,AVB,2026
Fairphone,FP6,FP6,radio,vbmeta_system.img,4096,PENDING,AVB,2026
Fairphone,FP6,FP6,radio,vendor_boot.img,100663296,PENDING,BOOT,2026
Fairphone,FP6,FP6,radio,xbl.img,1196032,PENDING,UEFIBOOT,2026
Fairphone,FP6,FP6,radio,xbl_config.img,311296,PENDING,ELF64,2026
Fairphone,FP6,FP6,radio,xbl_ramdump.img,860160,PENDING,UEFIBOOT,2026
Fairphone,FP6,FP6,radio,bluetooth.img,864256,PENDING,BLUETOOTH,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw12.tlv,100576,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw11.mbn,210724,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,evrbtfw20.tlv,48769,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw11.tlv,198512,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw11.ver,34,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,evrbtfw20.ver,35,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw12.mbn,112788,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msbtfw12.ver,34,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msnv12.bin,6316,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,evrnv20.bin,8331,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,bluetooth/image,msnv11.bin,6366,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,featenabler.img,106496,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,uefisecapp.img,200704,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,multiimgoem.img,12288,PENDING,UNKNOWN,2026
Fairphone,FP6,FP6,radio,hyp.img,1683456,PENDING,SECUREBOOT,2026
Fairphone,FP6,FP6,radio,keymaster.img,442368,PENDING,SECURITY,2026
Fairphone,FP6,FP6,radio,tz.img,4034560,PENDING,BOOT,2026
Fairphone,FP6,FP6,radio,devcfg.img,49152,PENDING,UNKNOWN,2026
```

---

## Provenance, per row

Every row carries its byte size from the lab's committed censuses
(derived facts only; no blob content redistributed). Row → source:

| rows (CSV path) | count | source doc (committed) | sha256 status |
|---|---|---|---|
| `modem/image` core (modem/adsp/cdsp/ipa_fws/cpusys_vm families, TA `.mdt+.bXX` splits, adsp/cdsp dtb + jsn) | 281 | [results/census.md](../research/qualcomm/results/census.md) table "All files" | full sha256 in lab census; 16-hex in the committed table |
| `modem/image/qca6750` (wpss family, bdwlan, regdb, Data.msc, qdss cfg, wpss.qdb) | 76 | results/census.md | full sha256 in lab census |
| `modem/image/modem_pr/**` (mcfg hw/sw configs, so/ libs) + `modem/image/milos/qdsp6m.qdb` | 173 | results/census.md | full sha256 in lab census |
| `modem/verinfo` | 1 | results/census.md | full sha256 in lab census |
| `vendor/firmware` (CAMERA_ICP family, vpu family, GPU gen7/gen8, haptic, codec, sensor fw) | 57 | results/census.md | full sha256 in lab census |
| `dsp/adsp`, `dsp/cdsp` (fastrpc compute-PD libraries) | 77 | results/census.md | full sha256 in lab census |
| `radio`: xbl, xbl_config, xbl_ramdump, uefi, abl, imagefv, shrm, aop, aop_config, cpucp, cpucp_dtb, qupfw, boot, vendor_boot, dtbo, pvmfw, vbmeta, vbmeta_system | 18 | [docs/bootchain-census.md](../research/qualcomm/docs/bootchain-census.md) + results/bootchain-census.json | sha256 (16-hex) in results JSON (table below) |
| `radio`: tz.img, hyp.img, keymaster.img, devcfg.img, uefisecapp.img, multiimgoem.img, featenabler.img | 7 | [docs/trustzone-census.md](../research/qualcomm/docs/trustzone-census.md) + results/bt-tz-census.json | sha256 (16-hex) in results JSON (table below) |
| `radio`: bluetooth.img (FAT16 partition image) + `bluetooth/image` (11 files) | 12 | [docs/bt-firmware-census.md](../research/qualcomm/docs/bt-firmware-census.md) + results/bt-tz-census.json | bluetooth.img has a **full sha256** (`274cc6812df59a7cd33b50d8bda117e2e55d639e0c4a891d5c8192ec5be3507f`); the 11 files 16-hex (table below) |

Row-count checks: the 665-row census table parses byte-identically to
its committed header (`files: 665 · total bytes: 240,352,566` — the
generated modem/vendor/dsp rows sum to exactly that figure).

### sha256 (16-hex) for the boot-chain / TrustZone / BT rows

For cross-checking these 37 rows before the md5 re-hash (source:
`results/bootchain-census.json` + `results/bt-tz-census.json`):

| file | sha256 (16) | file | sha256 (16) |
|---|---|---|---|
| abl.img | 0a08171b90a75d7a | tz.img | c4acad0f8b0f5e10 |
| aop.img | 66cf5f1fa090de5c | hyp.img | 210cc7647547dec8 |
| aop_config.img | 676e00e4e8b1fb58 | keymaster.img | b5ed87a964da2b63 |
| boot.img | 930766ab03d90791 | devcfg.img | e5e75f48b376bba2 |
| cpucp.img | 5aedb89f0857d17c | uefisecapp.img | 8034362fb2d6c61d |
| cpucp_dtb.img | de6bd9d7927a9dfa | multiimgoem.img | ebe632dc09a8a796 |
| dtbo.img | f9545d15daaa8978 | featenabler.img | 3a15317844f7dbc6 |
| imagefv.img | 2b5d1f6375b84159 | msbtfw11.mbn | 2cbd53302e199e21 |
| pvmfw.img | c5cd3afe1ef9724e | msbtfw11.tlv | 4cb4b8381d07c42a |
| qupfw.img | 3c93bb6da560d919 | msbtfw11.ver | 085e678b2cc25e3e |
| shrm.img | 8bd6d7c1ed6cf793 | msnv11.bin | 3111b607ee56e015 |
| uefi.img | 849a2e5fe34f5741 | msbtfw12.mbn | 06cff4fb357c5d09 |
| vbmeta.img | 091ce4b00f95d35e | msbtfw12.tlv | 67a676c68912cb55 |
| vbmeta_system.img | 782c83159132f2f6 | msbtfw12.ver | 74d9ed895317165b |
| vendor_boot.img | 142676fa3e0de2bd | msnv12.bin | d4f266a342ed88cf |
| xbl.img | a95645eeb3391812 | evrbtfw20.tlv | a88dac0dee09e4f7 |
| xbl_config.img | b3722f53eda51ca5 | evrnv20.bin | 6b75dbad35667521 |
| xbl_ramdump.img | 7126dc25a0c2817e | evrbtfw20.ver | e5c011da755a4f8e |
| bluetooth.img | full sha256 `274cc6812df59a7cd33b50d8bda117e2e55d639e0c4a891d5c8192ec5be3507f` | | |

### Type-label mapping (documented for reviewers)

- Copied from FP5 rows for identical file kinds: abl/xbl → UEFIBOOT;
  boot → BOOT; tz → BOOT; hyp → SECUREBOOT; keymaster → SECURITY;
  dtbo → DTB; vbmeta → AVB; aop/cpucp/devcfg/uefisecapp/multiimgoem/
  featenabler → UNKNOWN; xbl_config/shrm/qupfw → ELF64;
  modem/image core families → MODEM (FP5 precedent: adsp.mdt, .jsn,
  .bXX all MODEM); bluetooth/image → UNKNOWN (FP5 precedent);
  haptic_* → FIRMWARE; aw882xx_acf.bin → CODEC; regdb.bin →
  WIFI_BLUETOOTH; bdwlan → WIFI.
- FP6-only kinds (no FP5 row exists): xbl_ramdump/uefi/imagefv →
  UEFIBOOT; aop_config → UNKNOWN; cpucp_dtb → DTB; pvmfw → BOOT;
  vendor_boot → BOOT; vbmeta_system → AVB; wpss family → WIFI (WLAN
  firmware of the WCN6750); QSEE TA families (UUID TAs, soter64,
  smplap64, featenabler split, focal64, evautil64, ic5, loadalgota64,
  ops, sp_license, winsecap, sbservice) → SECURITY; widevine.mbn +
  hdcp* → DRM; dsp/adsp + dsp/cdsp fastrpc libraries → COMPUTE;
  GPU gen7*/gen8* zap/gmu/sqe/aqe → GPU; CAMERA_ICP*/vpu* → UNKNOWN
  (their ISA/structure is documented in
  [docs/fp6-architecture-census.md](../research/qualcomm/docs/fp6-architecture-census.md),
  but no upstream CAMERA type exists to map onto).

## Flags (honest scoping)

1. **md5 column**: pending everywhere except the 13 zero-byte rows
   (universal empty-input md5) and provenance-hashable via the tables
   above; fill command in this document. The trees were not present on
   the box that produced this package (the 2026-11-09/10 extraction
   workspace was cleaned); nothing was invented.
2. **Partition images not covered**: upstream lists FP5's
   radio/modem.img, radio/vendor.img, radio/dsp.img whole-partition
   rows; the lab censuses record per-file contents (and
   bluetooth.img's partition image size + full sha256) but not the
   modem.img/vendor.img/dsp.img partition-image sizes — those three
   rows are **omitted** rather than guessed.
3. **system/product/system_ext**: not in scope of the lab census
   (Android framework, not firmware blobs — flagged as queued in
   results/census.md); no rows contributed from there.
