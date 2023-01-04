#!/bin/bash

# run in the derivatives folder. Requires a folder with ants_fslvbm results needs
# to be in there.
echo [`date`] [`hostname`] [`uname -a`] [`pwd`] [$0 $@] >> .fslvbmlog

HOWLONG=30
REG=""
export FSLPARALLEL=condor
### copy GM prob images no need to submit a job
[ ! -d "fmriprep_seg" ] && mkdir -p "fmriprep_seg"
# template_list=$(find * ! -name '*MNI*' -name '*_GM*')
# num=1

# for ixi dataset and in order to create a template from all the subdatasets
# find should be performed with this pattern: ../../*/derivatives/ants_fslvbm/*
for g in `find fmriprep/* ! -name '*log*' ! -name '*MNI*' -name '*GM_probseg.*' | sort -u` ; do
  f_name=$(basename $g)
  f_name=$(${FSLDIR}/bin/remove_ext $f_name)
  # if file exists copy it with number following.
  # T1 files have often the same name, therefore this way it keeps one
  # structural per subject even if multiple sessions exist
  if [ ! -f "fmriprep_seg/${f_name}.nii.gz" ]; then
      # num=1
      cp $g fmriprep_seg/${f_name}.nii.gz
      echo ${f_name}.nii.gz
  # else
  #     num=$((num+1))
  #     cp $g fmriprep_seg/${f_name}_${num}.nii.gz
  #     echo ${f_name}_${num}.nii.gz
  fi
done

cd fmriprep_seg
# template for first pass
T=${FSLDIR}/data/standard/tissuepriors/avg152T1_gray

### Estimation of the registration parameters of GM to grey matter standard template
/bin/rm -f fslvbm2b
for g in `$FSLDIR/bin/imglob *GM_probseg.*` ; do
  echo "$FSLDIR/bin/fslreorient2std $g ${g}_std ; \
       $FSLDIR/bin/robustfov -i ${g}_std -r ${g}_fov ; \
       ${FSLDIR}/bin/fsl_reg ${g}_fov $T ${g}_to_T -a" >> fslvbm2b
done
chmod a+x fslvbm2b
fslvbm2b_id=`fsl_sub_custom -T $HOWLONG -N fslvbm2b -t ./fslvbm2b`
echo Running initial registration: ID=$fslvbm2b_id

### Creation of the GM template by averaging all (or following the template_list for)
 # the GM_nl_0 and GM_xflipped_nl_0 images
cat <<stage_tpl3 > fslvbm2c
#!/bin/sh
if [ -f ../template_list ] ; then
    template_list=\`cat ../template_list\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list\`
else
    template_list=\`echo *_to_T.nii*\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list | sort -u\`
    echo "WARNING - study-specific template will be created from ALL input data - may
 not be group-size matched!!!"
fi
for g in \$template_list ; do
    mergelist="\$mergelist \${g}"
done
\$FSLDIR/bin/fslmerge -t template_4D_GM \$mergelist
\$FSLDIR/bin/fslmaths template_4D_GM -Tmean template_GM
\$FSLDIR/bin/fslswapdim template_GM -x y z template_GM_flipped
\$FSLDIR/bin/fslmaths template_GM -add template_GM_flipped -div 2 template_GM_init
stage_tpl3
chmod +x fslvbm2c

fslvbm2c_id=`fsl_sub_custom -j $fslvbm2b_id -T 15 -N fslvbm2c ./fslvbm2c`
echo Creating first-pass template: ID=$fslvbm2c_id


### Estimation of the registration parameters of GM to grey matter standard template
/bin/rm -f fslvbm2d
T=template_GM_init
for g in `$FSLDIR/bin/imglob *GM_probseg.*` ; do
  echo "$FSLDIR/bin/fslreorient2std $g ${g}_std ; \
       $FSLDIR/bin/robustfov -i ${g}_std -r ${g}_fov ; \
  ${FSLDIR}/bin/fsl_reg ${g}_fov $T ${g}_to_T_init -fnirt \"--config=GM_2_MNI152GM_2mm.cnf\"" >> fslvbm2d
done
chmod a+x fslvbm2d
fslvbm2d_id=`fsl_sub_custom -j $fslvbm2c_id -T $HOWLONG -N fslvbm2d -t ./fslvbm2d`
echo Running registration to first-pass template: ID=$fslvbm2d_id

### Creation of the GM template by averaging all (or following the template_list for) the GM_nl_0 and GM_xflipped_nl_0 images
cat <<stage_tpl4 > fslvbm2e
#!/bin/sh
if [ -f ../template_list ] ; then
    template_list=\`cat ../template_list\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list\`
else
    template_list=\`echo *_to_T_init.nii*\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list | sort -u\`
    echo "WARNING - study-specific template will be created from ALL input data - may not be group-size matched!!!"
fi
for g in \$template_list ; do
    mergelist="\$mergelist \${g}"
done
\$FSLDIR/bin/fslmerge -t template_4D_GM \$mergelist
\$FSLDIR/bin/fslmaths template_4D_GM -Tmean template_GM
\$FSLDIR/bin/fslswapdim template_GM -x y z template_GM_flipped
\$FSLDIR/bin/fslmaths template_GM -add template_GM_flipped -div 2 template_GM
stage_tpl4
chmod +x fslvbm2e
fslvbm2e_id=`fsl_sub_custom -j $fslvbm2d_id -T 15 -N fslvbm2e ./fslvbm2e`
echo Creating second-pass template: ID=$fslvbm2e_id
