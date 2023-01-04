#!/home/antogeo/.venvs/age_pred/bin/python

import argparse
import logging
import os
import os.path as op
import mask
from glob import glob
import nibabel as nib
import pandas as pd
from qc import qc_z
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

# gm_mask = op.join(data_folder, 'derivatives', pipeline, 'T1s',
#                   'stats', 'GM_mask.nii.gz')
schaefer_path = op.join(extras, 'schaefer',
    'Schaefer2018_1000Parcels_17Networks_order_FSLMNI152_2mm.nii.gz')
sub_cortex_path = op.join(extras,
                          'Tian_Subcortex_S1_3T.nii')
cereb_path = op.join(os.environ.get('FSLDIR'),
    'data/atlases/Cerebellum/Cerebellum-MNIflirt-maxprob-thr0-2mm.nii.gz')

if 'fsl' in pipeline:
    mm = '2mm/r'
else:
    mm = '1mm/'

bsf_path = op.join(extras, 'BSF', mm + 'BSF_1073.nii')
# cog18_atlas = op.join(db_path, 'extra', 'cog_atlas_79_95_78.nii')

# meta_fname = glob(dataset_path + '/participants*v')
#
# imgs_path = op.join(dataset_path, 'derivatives', 'fmriprep')
# images, subjects = rd.read_data(imgs_path)
# df = rd.read_metadata(subjects, meta_fname[0])


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

#
# atlases = [schaefer_path, sub_cortex_path, cereb_path]
# atlases_resized = []
# for atlas in atlases:
#     atlases_resized.append(mask.atlas_prep(atlas, vol_sample[0]))
#
# atlas_features = [
#     {'name': 'schaefer_atlas',
#      'atlas_fname': atlases_resized[0]},
#     {'name': 'sub_cortex',
#      'atlas_fname': atlases_resized[1]},
#     {'name': 'cereb',
#      'atlas_fname': atlases_resized[2]},
#     {'name': 'bsf',
#      'atlas_fname': atlases_resized[3]}
#     ]
atlases = [bsf_path]
atlases_resized = []
atlases_resized.append(mask.atlas_prep(bsf_path, vol_sample[0]))
atlas_features = [
    {'name': 'bsf',
     'atlas_fname': atlases_resized[0]}
    ]


meta_fname = glob(data_folder + '/participants*v')
filename, file_extension = op.splitext(meta_fname[0])
if file_extension == '.csv':
    df = pd.read_csv(meta_fname[0])
elif file_extension == '.tsv':
    df = pd.read_csv(meta_fname[0], delimiter='\t')
else:
    raise ValueError(
        'I do not know how to read {}'.format(file_extension))
df['participant_id'] = 'sub-' + df['participant_id'].astype(str)
age_col, = [x for x in df.columns if (
    ('age' in x) or ('Age' in x) or ('AGE' in x))]

# List all the subjects in subj_path
subjects = sorted(
    [x.split('/')[-1] for x in glob(op.join(subj_path, 'sub-[!.]*'))
        if op.isdir(x)])

# Read the nifti/img file
images = []
read_subjects = {}
read_subjects['name'] = []
read_subjects['session'] = []
read_subjects['Age'] = []
atlas_dict = {}
rois_data = {}
for subject in subjects:
    print(subject)
    if (df['participant_id'].str.contains(subject).any() or
            df['participant_id'].str.contains(subject[4:]).any()):
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
            if 'ses-' in files[0].split('/'):
                sess = [part for part in files[0].split(
                        '/') if 'ses-' in part]
            else:
                sess = 'ses-1'
            for feature in atlas_features:
                atlas_img = nib.load(feature['atlas_fname'])
                atlas_name = feature['name']
                atlas_flat = np.round(
                    atlas_img.get_fdata().reshape(-1)).astype(np.int)
                for value in np.unique(atlas_flat):
                    this_image[this_image == 0] = np.nan
                    try:
                        roi_value = np.nanmean(this_image[atlas_flat == value])
                    except:
                        roi_value = 0.0
                    if atlas_name + '_' + str(value) not in rois_data:
                        rois_data[atlas_name + '_' + str(value)] = []
                    rois_data[atlas_name + '_' + str(value)].append(roi_value)
            read_subjects['name'].append(subject)
            read_subjects['session'].append(sess)
            read_subjects['Age'].append(float(df[df[
                    'participant_id'] == subject][age_col].values))
        else:
            continue
    else:
        logging.info('Subject {} is not in metadata file'.format(subject))

read_subjects.update(rois_data)
df_parcels = pd.DataFrame.from_dict(read_subjects, orient='columns')

logging.info(
    'Mean values of {} atlas regions were succesfully calculated'
    .format(feature['name']))

atlases = [d['name'] for d in atlas_features]
df_qc = qc_z(df_parcels, atlases)
logging.info(
    'QC test (z-scores<3) for {} were succesfully calculated'.format(atlases))
dir_name = op.join(data_folder, 'derivatives', pipeline)
f_name = op.join(data_folder, 'derivatives', pipeline, output)
if not os.path.exists(dir_name):
    os.makedirs(dir_name)
print("File with mean regional values was saved in {}".format(f_name))
df_qc.to_csv(f_name)
