#!/bin/sh

data_path=$1
out_dir=$2

[ ! -d "$out_dir" ] && mkdir -p "$out_dir"

cur_dir=$(pwd)

if [ $cur_dir != $data_path ]]; then
    echo "changing dir to ${data_path}"
    cd $data_path
fi

datalad get sub*/**/*T1w.nii*

cp sub*/**/*T1w.nii* $out_dir

datalad drop sub*/**/*T1w.nii*
cd $cur_dir

# subj_list=$(find "$data_path" -type d -name "sub*" -exec sh -c 'basename {}'; | sort | uniq )             

# for subj in $subj_list; do
#  for sess in $(find $data_path/$subj -maxdepth 1 -mindepth 1 -type d -printf '%P\n'); do
#    if [[ $sess = 'ses'* ]];
#    then
#        cd $data_path/$subj/$sess/anat
#        dest=$output_dir/$subj/$sess/anat
#    elif [[ $sess = 'anat'* ]];
#    then
#        cd $data_path/$subj/anat
#        dest=$output_dir/$subj/anat
#    else
#        continue
#    fi
#  done
# done
