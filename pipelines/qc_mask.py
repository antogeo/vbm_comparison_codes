#!/home/antogeo/.venvs/age_pred/bin/python

import argparse
import logging
import os
import os.path as op
import mask
from glob import glob
import nibabel as nib
import pandas as pd
import numpy as np


parser = argparse.ArgumentParser()
parser.add_argument("-data_folder", help="path to data folder")
parser.add_argument("-pipeline",
                    help="name of pipeline as mentioned in the\
                    derivatives folder")
parser.add_argument("-extras",
                    help="path to folders that contains masks/atlases")
parser.add_argument("-output_name", help="output file name",
                    default="regional_values_mask.csv")

args = parser.parse_args()
data_folder = args.data_folder
pipeline = args.pipeline
extras = args.extras
output = args.output_name

gm_mask = op.join(extras, 'masks', 'ICBM_gm_05.nii')
wm_mask = op.join(extras, 'masks', 'ICBM_wm_csf_04.nii')

if 'fsl' in pipeline:
    mm = '2mm/r'
else:
    mm = '1mm/'

subj_path = op.join(data_folder, 'derivatives', pipeline)
if (('ants' in pipeline) or ('fslvbm' in pipeline) or
                ('fmriprep' in pipeline)):
    vol_patern = op.join(subj_path, 'sub*', '**', '*mod*.nii*')
elif 'cat12.8' in pipeline:
    vol_patern = op.join(subj_path, 'sub*', '**', 'mw*.nii*')
else:
    logging.warning(
        'Cannot get a sample of {}'.format(pipeline))
vol_sample = glob(vol_patern, recursive=True)

masks = [gm_mask, wm_mask]
masks_resized = []
for tissue_mask in masks:
    masks_resized.append(mask.atlas_prep(tissue_mask, vol_sample[0]))

masks_features = [
    {'name': 'gm',
     'mask_fname': masks_resized[0]},
    {'name': 'wm',
     'mask_fname': masks_resized[1]},
    ]

subjects = sorted(
    [x.split('/')[-1] for x in glob(op.join(subj_path, 'sub-[!.]*'))
        if op.isdir(x)])

# Read the nifti/img file
images = []
read_subjects = {}
read_subjects['name'] = []
read_subjects['session'] = []
read_subjects['gm_mean'] = []
read_subjects['wm_mean'] = []
rois_data = {}
for subject in subjects:
    print(subject)
    s_path = op.join(subj_path, subject)
    # print(s_path)
    if (('ants' in pipeline) or ('fslvbm' in pipeline) or
                    ('fmriprep' in pipeline)):
        foi = op.join(s_path, '**', '*mod*.nii*')
    elif 'cat12.8' in pipeline:
        foi = op.join(s_path, '**', 'mw*.nii*')
    else:
        logging.warning(
            'Pipeline {} has not been defined'.format(pipeline))
    files = glob(foi, recursive=True)
    if len(files) == 0:
        logging.warning(
            'No files found for {}'.format(subject))
    elif len(files) == 1:
        this_image = nib.load(files[0]).get_fdata().reshape(-1)
        # if 'ses-' in files[0].split('/'):
        #     sess = [part for part in files[0].split(
        #             '/') if 'ses-' in part]
        # else:
        #     sess = 'ses-1'
        for feature in masks_features:
            mask_img = nib.load(feature['mask_fname'])
            mask_name = feature['name']
            mask_flat = np.round(
                mask_img.get_fdata().reshape(-1)).astype(int)
            roi_value = np.mean(this_image[mask_flat == 1])
            read_subjects[mask_name + '_mean'].append(roi_value)
        sess = [part for part in files[0].split('/') if 'ses-' in part]
        read_subjects['name'].append(subject)
        read_subjects['session'].append(sess)
    else:
        for file in files:
            this_image = nib.load(file).get_fdata().reshape(-1)
            # if 'ses-' in file.split('/'):
            #     sess = [part for part in file.split(
            #             '/') if 'ses-' in part]
            # else:
            #     sess = 'ses-1'
            for feature in masks_features:
                mask_img = nib.load(feature['mask_fname'])
                mask_name = feature['name']
                mask_flat = np.round(
                    mask_img.get_fdata().reshape(-1)).astype(int)

                roi_value = np.mean(this_image[mask_flat == 1])
                read_subjects[mask_name + '_mean'].append(roi_value)
            read_subjects['name'].append(subject)
            sess = [part for part in file.split('/') if 'ses-' in part]
            read_subjects['session'].append(sess[0])

read_subjects.update(rois_data)
re = pd.DataFrame.from_dict(read_subjects, orient='columns')


dir_name = op.join(data_folder, 'derivatives', pipeline)
f_name = op.join(dir_name, output)
if not os.path.exists(dir_name):
    os.makedirs(dir_name)
print("File with mean mask values was saved in {}".format(f_name))
re.to_csv(f_name)
