#!/bin/bash

WORK_DIR='/tmp'
TMP_SUBJ=$WORK_DIR/data
BIDS_DIR=$1
OUTPUT_DIR=$2
sub=$3

extras=/data/project/age_prediction/extras
t1_template=${extras}/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii
in_template=${extras}/mni_icbm152_nlin_asym_09a/intraTPM_sumICBM.nii
gm_template=${extras}/pc_extr/tpm_ICBM_01.nii.gz

for sess in $(find $BIDS_DIR/$sub -maxdepth 1 -mindepth 1 -type d -printf '%P\n');
  do
    # set path of TMP file for results
    TMP_OUT=$WORK_DIR/derivatives
    TMP_SUBJ=${WORK_DIR}/${sub}
    [ ! -d "${TMP_OUT}" ] && mkdir -p "${TMP_OUT}"
    if [ ! -z "$(ls -A ${TMP_OUT})" ]; then
      rm -fr ${TMP_OUT}/*
    fi
    # check if there are ses-* files under subject's folder
    if [[ $sess = 'ses'* ]];
      then
       # add ses-* folder in path of tmp results folder
       # Create folder if doesn t exist and make sure is empty
       [ ! -d "${TMP_SUBJ}/anat" ] && mkdir -p "${TMP_SUBJ}/anat"
       if [ ! -z "$(ls -A ${TMP_SUBJ}/anat)" ]; then
       rm -rf ${TMP_SUBJ}/anat/*
       fi
       # save current dir and go to dataset dir
       cur_path="$PWD"
       cd "${BIDS_DIR}"
       # get current subject in project's folder
       datalad get $sub/${sess}/anat/*T1*
       # copy source of simlink symlink in tmp (node)
       cp -Lrf ${BIDS_DIR}/${sub}/${sess}/anat/*T1* ${TMP_SUBJ}/anat
       # drop subject from dataset repo
       datalad drop ${BIDS_DIR}/${sub}/${sess}/anat/*T1*
    # if in subject's dir there are not sessions look for anat folder, then
    # go to dataset and fetch subject, copy source in tmp, run fmriprep.
    # fmriprep takes care of output files in the dataset folder. Finally drops
    # subject from dataset.
    elif [[ $sess = 'anat'* ]];
      then
       [ ! -d "${TMP_SUBJ}/anat" ] && mkdir -p "${TMP_SUBJ}/anat"
       cur_path="$PWD"
       cd "${BIDS_DIR}"
       datalad get $sub/anat/*T1*
       cp -Lrf ${BIDS_DIR}/${sub}/anat/*T1* ${TMP_SUBJ}/anat

       datalad drop "${BIDS_DIR}"/"$sub"/anat/*T1*
    fi
   # run ANTs
   IMG=$(basename ${TMP_SUBJ}/anat/*T1*.nii*)
   subj_path=${TMP_SUBJ}/anat
   cd $subj_path
   ${ANTSPATH}/N4BiasFieldCorrection -d 3 -i $IMG -o n4_$IMG -v 1
   ${ANTSPATH}/antsBrainExtraction.sh -d 3 -a n4_$IMG -e $t1_template -m $in_template -o subj_
   ${ANTSPATH}/Atropos -d 3 -a subj_BrainExtractionBrain.nii.gz -i 'KMeans[3]' -p Socrates -x subj_BrainExtractionMask.nii.gz -o [classimage${IMG}, %02d${IMG}]
   ${ANTSPATH}/antsRegistration --dimensionality 3 --float 0 --output [affined_,affined_${IMG}] --transform "Rigid[0.1]" --metric "CC[${gm_template},${IMG},1,32,Regular,.25]" --convergence "[1000x500,1e-6,10]" -f 12x8 --smoothing-sigmas "4x3vox" -v 1

last ZSH
   ${ANTSPATH}/antsRegistration --dimensionality 3 --float 0 --output "[affined_, affined_${IMG}]" --transform "Rigid[0.1]" --m
etric "CC[${gm_template},${IMG},1,32,Regular,.25]" --convergence "[10x50,1e-6,10]" -f 12x8 --smoothing-sigmas '4x3vox'
  # create output dir 'derivatives/sub/ses-*'' if does not exist and
  # copy the results in it
  [ ! -d "${OUTPUT_DIR}" ] && mkdir -p "${OUTPUT_DIR}"
  cp -rf ${TMP_SUBJ}/affined_* ${OUTPUT_DIR}/
  cp -rf ${TMP_SUBJ}/0*_nii.gz ${OUTPUT_DIR}/

done
