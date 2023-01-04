#!/bin/bash

# run in the derivatives folder. Requires a folder with ants_fslvbm results needs
# to be in there.
echo [`date`] [`hostname`] [`uname -a`] [`pwd`] [$0 $@] >> .fslvbmlog

HOWLONG=30
REG=""
export FSLPARALLEL=condor

# template for first pass
T=${FSLDIR}/data/standard/tissuepriors/avg152T1_gray
  [ ! -d "ants_fslvbm3" ] && mkdir -p "ants_fslvbm3"
# iterate over the GM prob files of all subjects
for g in `find ants_fslvbm/sub*/* -name '*_GM.nii*' | sort -u` ; do
  # extract file name and remove extension
  f_name=$(basename $g)
  f_name=$(${FSLDIR}/bin/remove_ext $f_name)
  # remove extension from file with whole path and get folders. We need that
  # so that we keep the dir structure (sessions)
  g=$(${FSLDIR}/bin/remove_ext $g)
  folders=$(echo "$(dirname $g)" | awk -F ants_fslvbm/ '{print $2}')
  echo $g
  [ ! -d "ants_fslvbm3/${folders}" ] && mkdir -p "ants_fslvbm3/${folders}"

  # run registration and then multply jac with registered image. results are
  # saved directly in the previous file.
  echo "$FSLDIR/bin/fslreorient2std $g ${g}_std ; \
        $FSLDIR/bin/robustfov -i ${g}_std -r ${g}_fov ; \
        ${FSLDIR}/bin/fsl_reg ${g}_fov $T ants_fslvbm3/${folders}/${f_name}_to_cust_tmplt -fnirt \"--config=GM_2_MNI152GM_2mm.cnf --jout=${f_name}_JAC_nl\"; \
        $FSLDIR/bin/fslmaths ants_fslvbm3/${folders}/${f_name}_to_cust_tmplt -mul ${f_name}_JAC_nl ants_fslvbm3/${folders}/${f_name}_mod -odt float" >> fslvbm3a
done
chmod a+x fslvbm3a
fslvbm3a_id=`fsl_sub_custom -T 20 -N fslvbm3a -t ./fslvbm3a`
echo Doing registrations: ID=$fslvbm3a_id
