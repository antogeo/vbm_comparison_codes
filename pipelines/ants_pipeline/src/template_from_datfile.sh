#!/bin/bash
# v1.3

CPUS='1'
RAM='8G'
DISK='1G'
LOGS_DIR='/data/project/age_prediction/logs/ants_gm_mod'

WORK_DIR='/tmp'
BIDS_DIR='/data/project/age_prediction/datasets/datasets_repo/original/camcan/cc700_mri'
OUTPUT_DIR='/data/project/age_prediction/datasets/datasets_repo/original/camcan/cc700_mri/derivatives'

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
initial_dir    = /data/project/age_prediction/codes/ants_pipeline

executable     = /data/project/age_prediction/codes/ants_pipeline/segm_ppln.py
notification = Complete
\n"

input="/data/project/age_prediction/datasets/datasets_repo/original/camcan/cc700_mri/derivatives/ants/failed_subjs.dat"
while IFS= read -r sub
do
# loop over all subjects
    printf "arguments = -subj_path ${BIDS_DIR}/$sub \
                        -out_dir ${OUTPUT_DIR} \
                        \n"
    printf "log       = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.log\n"
    printf "output    = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.out\n"
    printf "error     = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.err\n"
    printf "Queue\n\n"
done < "$input"
