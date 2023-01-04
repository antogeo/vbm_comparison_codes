#!/bin/bash

WORK_DIR='/tmp'
TMP_SUBJ=$WORK_DIR/data
FMRIPREP_DIR=$1
subj=$2
sess=$3
OUTPUT_DIR=$4
template_GM=${FSLDIR}/data/standard/tissuepriors/avg152T1_gray

# if there sessions make folders accordingly and prepare output dir
if [[ $sess = 'ses'* ]] ;
then
  cd ${FMRIPREP_DIR}/${subj}/${sess}/anat
  dest=${OUTPUT_DIR}/${subj}/${sess}/anat
elif [[ $sess = 'anat'* ]] ;
then
  cd ${FMRIPREP_DIR}/${subj}/anat
  dest=${OUTPUT_DIR}/${subj}/anat
else
  echo "no anat or sess folder"
  exit 1
fi
# create TMP and output dirs if they do not exist
[ ! -d "${TMP_SUBJ}/${subj}/${sess}" ] && mkdir -p "${TMP_SUBJ}/${subj}/${sess}"
[ ! -d "${dest}" ] && mkdir -p "${dest}"
# [ ! -d "${TMP_SUBJ}/${sub}" ] && mkdir -p "${TMP_SUBJ}/${sub}"
# copy GM probseg in tmp folder
cp *-GM_probseg* ${TMP_SUBJ}/${subj}/${sess}
cd ${TMP_SUBJ}/${subj}/${sess}

# get only the GM in native space
g=$(find * ! -name '*MNI*' -name '*GM_probseg*')
# awk -F_label splits string in two parts one before _label and one after

sub_name=$(echo "$g" | awk -F_label '{print $1}')
# if sessions -> add session in the subject's name
if [[ $sess = 'ses'* ]] ;
then
  new_name=${sub_name}_${sess}
else
  new_name=${sub_name}
fi

# run registration and segmentation
${FSLDIR}/bin/fsl_reg ${g} $template_GM ${new_name}_GM_to_template -fnirt "--config=GM_2_MNI152GM_2mm.cnf --lambda=400,200,150,75 --jout=${new_name}_JAC_nl"
${FSLDIR}/bin/fslmaths ${new_name}_GM_to_template -mul ${new_name}_JAC_nl ${new_name}_GM_mod -odt float

# move files from tmp results to derivatives folder
mv ${new_name}_GM_to_template.nii* $dest
mv ${new_name}_GM_mod.nii* $dest
mv ${new_name}_JAC_nl* $dest
