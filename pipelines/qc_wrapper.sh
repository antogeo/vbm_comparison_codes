#!/bin/bash

datasets='enki camcan ixi'


for dataset in $datasets; do

  ppln_list=$(ls /data/project/age_prediction/results/datasets/${dataset}/derivatives/);
  for ppln in $ppln_list; do
    echo ${dataset}
    echo $ppln
    python qc_mask.py -data_folder /data/project/age_prediction/results/datasets/${dataset} \
                      -pipeline ${ppln} \
                      -extras /data/project/age_prediction/extras \
                      -output_name ${dataset}_${ppln}_segm_test.csv
  done
done
