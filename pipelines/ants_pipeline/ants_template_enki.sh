#!/bin/bash
# v1.3

CPUS='1'
RAM='8G'
DISK='1G'
LOGS_DIR='/data/project/age_prediction/logs/ants_gm_mod'

WORK_DIR='/tmp'
BIDS_DIR='/data/project/age_prediction/datasets/datasets_repo/original/enki/bids'
OUTPUT_DIR='/data/project/age_prediction/datasets/datasets_repo/original/enki/bids/derivatives'

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

executable     = /data/project/age_prediction/codes/ants_pipeline/ants_wrapper.sh
notification = Error
\n"

subj_list=$(find "$BIDS_DIR" -type d -name "sub*" -exec sh -c 'basename {}' \; | sort | uniq )

# loop over all subjects
for sub in $subj_list; do
    printf "arguments = ${BIDS_DIR} ${OUTPUT_DIR} ${sub} ${CPUS} \n"
    printf "log       = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.log\n"
    printf "output    = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.out\n"
    printf "error     = ${LOGS_DIR}/\$(Cluster).\$(Process).${sub}.err\n"
    printf "Queue\n\n"
done
