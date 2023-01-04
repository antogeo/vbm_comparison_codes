#!/bin/bash
# v1.3

CPUS='1'
RAM='8G'
DISK='1G'
LOGS_DIR='/data/project/age_prediction/logs/fmriprep_fsltemplate'

# FMRIPREP_DIR=/data/project/age_prediction/datasets/datasets_repo/original/ixi/bids/IOP/derivatives/fmriprep
FMRIPREP_DIR=$1
OUTPUT_DIR=${FMRIPREP_DIR}_fsl_3

# create the logs dir if it doesn't exist
[ ! -d "${LOGS_DIR}" ] && mkdir -p "${LOGS_DIR}"

# print the .submit header
printf "# The environment
universe       = vanilla
getenv         = True
request_cpus   = ${CPUS}
request_memory = ${RAM}
request_disk   = ${DISK}

# Execution
initial_dir    = /data/project/age_prediction/codes/fsl_vbm_nipype

executable     = /data/project/age_prediction/codes/fsl_vbm_nipype/fmriprep_fsl_3.sh
notification = Complete
\n"

subj_list=$(find "$FMRIPREP_DIR" -type d -name "sub*" -exec sh -c 'basename {}' \; | sort | uniq )

# loop over all subjects
for sub in $subj_list; do
  for sess in $(find ${FMRIPREP_DIR}/${sub} -maxdepth 1 -mindepth 1 -type d \( -name 'anat' -or -name 'ses*' \) -printf '%P\n'); do
    printf "arguments = ${FMRIPREP_DIR} ${sub} ${sess} ${OUTPUT_DIR} \n"
    printf "log       = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.log\n"
    printf "output    = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.out\n"
    printf "error     = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.err\n"
    printf "Queue\n\n"
  done
done
