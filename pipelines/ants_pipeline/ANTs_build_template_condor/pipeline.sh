# Activate appropriate environment
source ~/.venvs/age_pred/bin/activate

# cd to folder with scripts, otherwise provide full paths

# The following script is submitting job with gm_ants_wrapper.sh as executable
# Reads subjects in the given path (1st argument) and provides to the executable
# path of subject, subject's name and output path.

./gm_ants_submit.sh /path/to/data/folder /path/of/output/dir | condor_submit

# The executable is using datalad to fetch subjects in the tmp folder the nodes.
# N4 bias field correction, brain extraction, header correction, Atropos
# segmentation and affine registration are applied to all volumes. Output files
# are all copied into OUTPUT directory.

# cd to dir with affined GM volume

# waitForCONDORJobs has to saved as executable in the $ANTSPATH dir

# Run build template:
# c: 5 is for Condor
# n: N4 bas field correction. Bias field correction has been applied before
#    brain extraction in previous script.
buildtemplate_condor.sh -d 3 -m 30x50x20 -n 0 -t GR -s CC -c 5 -z /data/project/age_prediction/extras/mni_icbm152_nlin_asym_09a/mni_icbm152_t1_tal_nlin_asym_09a.nii -o MY aff*.nii*

# To clean folder from previous command's products, in case rerun is needed,
# run the following in the OUTPUT folder.
 
# rm -rf SyN* MY* tmp* job* rigid subj_nlin_job.sh
