#!/bin/bash

echo [`date`] [`hostname`] [`uname -a`] [`pwd`] [$0 $@] >> .fslvbmlog

HOWLONG=30
REG=""

### BET parameters
bet="-N"  # If run with -N, then set bet=1, else bet=0

### BET 1st step: copy images no need to submit a job
mkdir -p struc
for g in `$FSLDIR/bin/imglob *` ; do
    imcp $g struc/${g}_struc
done

cd struc
### BET 2nd step: copy images no need to submit a job
/bin/rm -f fslvbm1a
imagelist=""
for g in `$FSLDIR/bin/imglob *_struc.*` ; do
  echo $g
  if [ $bet = 0 ] ; then
	  echo "${FSLDIR}/bin/bet $g ${g}_brain -f 0.4" >> fslvbm1a
  else
	  echo "$FSLDIR/bin/fslreorient2std $g ${g}_std ; \
          $FSLDIR/bin/robustfov -i ${g}_std -r ${g}_fov ; \
          ${FSLDIR}/bin/bet ${g}_fov ${g}_brain ; \
	        ${FSLDIR}/bin/standard_space_roi ${g}_brain ${g}_cut -roiNONE -ssref ${FSLDIR}/data/standard/MNI152_T1_2mm_brain -altinput ${g}_fov ; \
	        ${FSLDIR}/bin/bet ${g}_cut ${g}_brain -f 0.4" >> fslvbm1a
  fi
  imagelist="$imagelist $g ${g}_brain"
done
chmod a+x fslvbm1a
fslvbm1a_id=`fsl_sub_custom -v -T $HOWLONG -N fslvbm1a -t ./fslvbm1a`
echo Running BET: ID=$fslvbm1a_id

### BET 3rd step: copy images no need to submit a job

/bin/rm -f fslvbm1b
echo "${FSLDIR}/bin/slicesdir -o ${imagelist}" >> fslvbm1b
chmod a+x fslvbm1b
fslvbm1b_id=`fsl_sub_custom -v -j $fslvbm1a_id -T $HOWLONG -N fslvbm1b -t ./fslvbm1b`
echo Running Slicedir: ID=$fslvbm1b_id

### Step 2. Template

T=${FSLDIR}/data/standard/tissuepriors/avg152T1_gray

### segmentation
/bin/rm -f fslvbm2a
for g in `$FSLDIR/bin/imglob *_struc.*` ; do
    echo $g
    echo "$FSLDIR/bin/fast -R 0.3 -H 0.1 ${g}_brain ; \
          $FSLDIR/bin/immv ${g}_brain_pve_1 ${g}_GM" >> fslvbm2a
done
chmod a+x fslvbm2a
fslvbm2a_id=`fsl_sub_custom -j $fslvbm1b_id -T 30 -N fslvbm2a -t ./fslvbm2a`
echo Running segmentation: ID=$fslvbm2a_id

### Estimation of the registration parameters of GM to grey matter standard template
/bin/rm -f fslvbm2b
for g in `$FSLDIR/bin/imglob *_struc.*` ; do
  echo "${FSLDIR}/bin/fsl_reg ${g}_GM $T ${g}_GM_to_T -a" >> fslvbm2b
done
chmod a+x fslvbm2b
fslvbm2b_id=`fsl_sub_custom -j $fslvbm2a_id -T $HOWLONG -N fslvbm2b -t ./fslvbm2b`
echo Running initial registration: ID=$fslvbm2b_id

### Creation of the GM template by averaging all (or following the template_list for) the GM_nl_0 and GM_xflipped_nl_0 images
cat <<stage_tpl3 > fslvbm2c
#!/bin/sh
if [ -f ../template_list ] ; then
    template_list=\`cat ../template_list\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list\`
else
    template_list=\`echo *_struc.* | sed 's/_struc\./\./g'\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list | sort -u\`
    echo "WARNING - study-specific template will be created from ALL input data - may not be group-size matched!!!"
fi
for g in \$template_list ; do
    mergelist="\$mergelist \${g}_struc_GM_to_T"
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
for g in `$FSLDIR/bin/imglob *_struc.*` ; do
  echo "${FSLDIR}/bin/fsl_reg ${g}_GM $T ${g}_GM_to_T_init $REG -fnirt \"--config=GM_2_MNI152GM_2mm.cnf\"" >> fslvbm2d
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
    template_list=\`echo *_struc.* | sed 's/_struc\./\./g'\`
    template_list=\`\$FSLDIR/bin/remove_ext \$template_list | sort -u\`
    echo "WARNING - study-specific template will be created from ALL input data - may not be group-size matched!!!"
fi
for g in \$template_list ; do
    mergelist="\$mergelist \${g}_struc_GM_to_T_init"
done
\$FSLDIR/bin/fslmerge -t template_4D_GM \$mergelist
\$FSLDIR/bin/fslmaths template_4D_GM -Tmean template_GM
\$FSLDIR/bin/fslswapdim template_GM -x y z template_GM_flipped
\$FSLDIR/bin/fslmaths template_GM -add template_GM_flipped -div 2 template_GM
stage_tpl4
chmod +x fslvbm2e
fslvbm2e_id=`fsl_sub_custom -j $fslvbm2d_id -T 15 -N fslvbm2e ./fslvbm2e`
echo Creating second-pass template: ID=$fslvbm2e_id

echo "Study-specific template will be created, when complete, check results with:"
echo "fslview struc/template_4D_GM"
echo "and turn on the movie loop to check all subjects, then run:"
echo "fslview " ${FSLDIR}/data/standard/tissuepriors/avg152T1_gray " struc/template_GM"
echo "to check general alignment of mean GM template vs. original standard space template."


### step 3, without "randomize"

echo [`date`] [`hostname`] [`uname -a`] [`pwd`] [$0 $@] >> .fslvbmlog
cd ..
mkdir -p stats
cd struc

echo "Now running the preprocessing steps and the pre-analyses"

/bin/rm -f fslvbm3a
for g in `$FSLDIR/bin/imglob *_struc.*` ; do
  echo $g
  echo "${FSLDIR}/bin/fsl_reg ${g}_GM template_GM ${g}_GM_to_template_GM -fnirt \"--config=GM_2_MNI152GM_2mm.cnf --jout=${g}_JAC_nl\"; \
        $FSLDIR/bin/fslmaths ${g}_GM_to_template_GM -mul ${g}_JAC_nl ${g}_GM_to_template_GM_mod -odt float" >> fslvbm3a
done
chmod a+x fslvbm3a
fslvbm3a_id=`fsl_sub_custom -j $fslvbm2e_id -T 40 -N fslvbm3a -t ./fslvbm3a`
echo Doing registrations: ID=$fslvbm3a_id

cd ../stats

cat <<stage_preproc2 > fslvbm3b
#!/bin/sh

\$FSLDIR/bin/imcp ../struc/template_GM template_GM

\$FSLDIR/bin/fslmerge -t GM_merg     \`\${FSLDIR}/bin/imglob ../struc/*_GM_to_template_GM.*\`
\$FSLDIR/bin/fslmerge -t GM_mod_merg \`\${FSLDIR}/bin/imglob ../struc/*_GM_to_template_GM_mod.*\`

\$FSLDIR/bin/fslmaths GM_merg -Tmean -thr 0.01 -bin GM_mask -odt char

/bin/cp ../design.* .

for i in GM_mod_merg ; do
  for j in 2 3 4 ; do
    \$FSLDIR/bin/fslmaths \$i -s \$j \${i}_s\${j}
   # \$FSLDIR/bin/randomise -i \${i}_s\${j} -o \${i}_s\${j} -m GM_mask -d design.mat -t design.con -V
  done
done

stage_preproc2

chmod a+x fslvbm3b

fslvbm3b_id=`fsl_sub_custom -T 15 -N fslvbm3b -j $fslvbm3a_id ./fslvbm3b`

echo Doing subject concatenation and initial randomise: ID=$fslvbm3b_id

echo "Once this has finished, run randomise with 5000 permutations on the 'best' smoothed 4D GM_mod_merg. We recommend using the -T (TFCE) option. For example:"
echo "randomise -i GM_mod_merg_s3 -o GM_mod_merg_s3 -m GM_mask -d design.mat -t design.con -n 5000 -T -V"
