#!/bin/bash

WORK_DIR='/tmp'
TMP_SUBJ=$WORK_DIR/data
BIDS_DIR=$1
OUTPUT_DIR=$2
sub=$3


for sess in $(find $BIDS_DIR/$sub -maxdepth 1 -mindepth 1 -type d -printf '%P\n'); do
    # set path of TMP file for results
    TMP_OUT=$WORK_DIR/derivatives
    [ ! -d "${TMP_OUT}" ] && mkdir -p "${TMP_OUT}"
    if [ ! -z "$(ls -A ${TMP_OUT})" ]; then
    rm -fr ${TMP_OUT}/*
    fi
    # check if there are ses-* files under subject's folder
    if [[ $sess = 'ses'* ]];
    then
         # add ses-* folder in path of tmp results folder
         # Create folder if doesn t exist and make sure is empty
         [ ! -d "${TMP_SUBJ}/${sub}/anat" ] && mkdir -p "${TMP_SUBJ}/${sub}/anat"
         if [ ! -z "$(ls -A ${TMP_SUBJ}/${sub}/anat)" ]; then
         rm -rf ${TMP_SUBJ}/${sub}/anat/*
         fi
         # save current dir and go to dataset dir
         cur_path="$PWD"
         cd "${BIDS_DIR}"
         # get current subject in project's folder
         datalad get $sub/${sess}/anat/*T1*
         # copy source of simlink symlink in tmp (node)
         cp -Lrf ${BIDS_DIR}/${sub}/${sess}/anat/*T1*.nii* ${TMP_SUBJ}/${sub}/anat
         if [ "$?" -eq 1 ]
            then
             echo "$sub ${sess} failed to copy T1 in node tmp \n"
             datalad drop ${BIDS_DIR}/${sub}/${sess}/anat/*T1*
            continue
        fi
        # run singulariy
         /data/project/age_prediction/codes/ants_fslvbm/src/segm_ppln.py -data_dir ${TMP_SUBJ} -out_dir ${TMP_OUT} -subj ${sub}
        # drop subject from dataset repo
        datalad drop ${BIDS_DIR}/${sub}/${sess}/anat/*T1*
        # create output dir 'derivatives/sub/ses-*'' if does not exist and
        # copy the results in it
        [ ! -d "${OUTPUT_DIR}/ants_fslvbm/$sub/${sess}" ] && mkdir -p "${OUTPUT_DIR}/ants_fslvbm/$sub/${sess}"
        cp -rf $TMP_OUT/posteriors/POSTERIOR_03.nii.gz ${OUTPUT_DIR}/ants_fslvbm/${sub}/${sess}/${sub}_${sess}_GM.nii
        cp -rf $TMP_OUT/log_failed_sbjs.log ${OUTPUT_DIR}/ants_fslvbm/${sub}/${sess}/${sub}_${sess}_log_failed_sbjs.log
    # if in subject's dir there are not sessions look for anat folder, then
    # go to dataset and fetch subject, copy source in tmp, run fmriprep.
    # fmriprep takes care of output files in the dataset folder. Finally drops
    # subject from dataset.
    elif [[ $sess = 'anat'* ]];
    then
      [ ! -d "${TMP_SUBJ}/$sub/anat" ] && mkdir -p "${TMP_SUBJ}/$sub/anat"
      cur_path="$PWD"
      cd "${BIDS_DIR}"
      datalad get $sub/anat/*T1*
      cp -Lrf ${BIDS_DIR}/${sub}/anat/*T1*.nii* ${TMP_SUBJ}/${sub}/anat
      if [ "$?" -eq 1 ]
        then
         echo "$sub failed to copy T1 in node tmp \n"
         datalad drop ${BIDS_DIR}/${sub}/anat/*T1*
         continue
      fi
       /data/project/age_prediction/codes/ants_fslvbm/src/segm_ppln.py -data_dir ${TMP_SUBJ} -out_dir ${TMP_OUT} -subj ${sub}

      datalad drop ${BIDS_DIR}/${sub}/anat/*T1*
      [ ! -d "${OUTPUT_DIR}/ants_fslvbm/$sub/" ] && mkdir -p "${OUTPUT_DIR}/ants_fslvbm/$sub/"
      cp -rf $TMP_OUT/posteriors/POSTERIOR_03.nii.gz ${OUTPUT_DIR}/ants_fslvbm/${sub}/${sub}_GM.nii
      cp -rf $TMP_OUT/log_failed_sbjs.log ${OUTPUT_DIR}/ants_fslvbm/${sub}/${sub}_log_failed_sbjs.log
    fi
done
