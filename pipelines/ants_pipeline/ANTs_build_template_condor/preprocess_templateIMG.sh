#!/bin/bash

IMG=$1
t1_template=/data/project/age_prediction/extras/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii
in_template=/data/project/age_prediction/extras/mni_icbm152_nlin_asym_09a/intraTPM_sumICBM.nii

${ANTSPATH}N4BiasFieldCorrection -d 3 -i $IMG -o n4_$IMG -v 1            1 !

${ANTSPATH}antsBrainExtraction.sh -d 3 -a n4_$IMG -e $t1_template -m in_template -o TPM

${ANTSPATH}Atropos -d 3 -a TPM_n4_$IMG -i KMeans[4] -p Socrates -x TPM*mask* \
    -o [${IMG}classImage, ${IMG}%02d.nii.gz] 
