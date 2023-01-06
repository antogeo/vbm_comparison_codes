"""
Constants.py
"""

import os
import os.path as op

ppln_label = ['ANTs ICBM', 'ANTs \n study tmplt', 'ANTs FSL \n default',
              'ANTs FSL \n study tmplt', 'fMRIprep FSL \n default',
              'fMRIprep FSL \n study tmplt', 'FSLVBM \n default', 'FSLVBM',
              'CAT12.8', 'CAT12.8 \n study tmplt']
ppln_list = ['ants_icbm', 'ants_data',  'ants_fslvbm3',
             'ants_fslvbm23', 'fmriprep1_3',
             'fmriprep1_23', 'fslvbm13', 'fslvbm',
             'cat12.8', 'cat12.8_data']

extras = '/home/antogeo/data/extras/'
schaefer_path = op.join(extras, 'schaefer', 'MNI',
    'Schaefer2018_1000Parcels_17Networks_order_FSLMNI152_2mm.nii.gz')
sub_cortex_path = op.join(extras,
                          'Tian_Subcortex_S1_3T.nii')
cereb_path = op.join(os.environ.get('FSLDIR'),
    'data/atlases/Cerebellum/Cerebellum-MNIflirt-maxprob-thr0-2mm.nii.gz')
bsf_path = op.join(extras, 'BSF', "1mm", 'BSF_1073.nii')

mix_atlas_path = op.join(extras, 'mix_atlas.nii')
atlases = [schaefer_path, sub_cortex_path, cereb_path]
atlas_features = [
    {'name': 'schaefer_atlas',
     'atlas_fname': schaefer_path},
    {'name': 'sub_cortex',
     'atlas_fname': sub_cortex_path},
    {'name': 'cereb',
     'atlas_fname': cereb_path},
    {'name': 'bsf',
     'atlas_fname': bsf_path}
    ]
mix_atlas = {'name': 'mix_atlas',
             'atlas_fname': mix_atlas_path}
datasets = ['enki', 'camcan', 'ixi', 'oasis']
datasets_names = ['eNKI', 'CamCAN', 'IXI', 'OASIS']
