#!/home/antogeo/.venvs/age_pred/bin/python

import pandas as pd
import os.path as op
import time
from lib.leap.logging import (configure_logging, finish_logging,
                              logger)
from pathlib import Path
import itertools
from scipy.stats import pearsonr, spearmanr
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import constants as con
import nibabel as nib
import mat_to_nii
import matplotlib
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats import multitest
from statsmodels.formula.api import ols
from src.def_correl import ppln_age_corr, ppln_corr
from src.get_data import get_dataframes
from functools import reduce
%matplotlib


datasets = ['ixi', 'camcan', 'enki']
deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines'
save_nii = True


enki_df, ppln_list, ppln_label, atlases_rois, atlases_list = \
    get_dataframes('enki')
cc_df, _, _, _, _ = get_dataframes('camcan')
ixi_df, _, _, _, _ = get_dataframes('ixi')
for dataset_df in [enki_df, cc_df, ixi_df]:
    for num, df in enumerate(dataset_df):
        dataset_df[num] = df[df['QC']]

# calculate correlation between each region and age for each ppln_name
enki_merged = reduce(lambda left, right: pd.merge(left, right, on=[
                                                  'name', 'session'],
                                                  how='inner'),
                     [df[['name', 'session']] for df in enki_df])
for num, df in enumerate(enki_df):
    enki_df[num] = df.merge(enki_merged, on=['name', 'session'], how='right')

cc_merged = reduce(lambda left, right: pd.merge(left, right, on=[
                                                'name', 'session'],
                                                how='inner'),
                   [df[['name', 'session']] for df in cc_df])
for num, df in enumerate(cc_df):
    cc_df[num] = df.merge(cc_merged, on=['name', 'session'], how='right')

ixi_merged = reduce(lambda left, right: pd.merge(left, right, on=[
                                                 'name', 'session'],
                                                 how='inner'),
                    [df[['name', 'session']] for df in ixi_df])
for num, df in enumerate(ixi_df):
    ixi_df[num] = df.merge(ixi_merged, on=['name', 'session'], how='right')


ppln_df = list()
for ppln_num, ppln_name in enumerate(ppln_list):
    ppln_df.append(pd.concat([enki_df[ppln_num], cc_df[ppln_num], ixi_df[ppln_num]], axis=0).reset_index(drop=True))

selected_atlas = [con.atlas_features[3]]
atlas_name = atlases_list
select_rois = atlases_rois
atlas = con.atlas_features[3]

df_age_corr = ppln_age_corr(ppln_list, ppln_df, select_rois)

df_age_corr["fischer_z"] = np.arctanh(df_age_corr['r_score'])
# plt.figure()
# displot = sns.distplot(a=df_age_corr, axlabel='r_score')
plt.figure()
stripplot = sns.stripplot(y='r_score', data=df_age_corr,
                          palette="colorblind", x='ppln', hue='ppln')
mean_corr = np.tanh(df_age_corr.groupby('ppln').mean())

# iterate over atlases and ppls. Correct p_values for each atlas.
# Create nii's with correlations < -.7 and corrected p-values < .05
if save_nii:
    for atlas in selected_atlas:
        atlas_nii = atlas['atlas_fname']
        for ppln in ppln_list:
            array = df_age_corr[(df_age_corr['ppln'] == ppln) & (
                 df_age_corr['roi'].str.match(
                    atlas['name']))]['r_score'] * \
                         multitest.multipletests(
                        df_age_corr[(df_age_corr['ppln'] == ppln) & (
                         df_age_corr['roi'].str.match('bsf'))]['p_val'],
                        alpha=0.05, method='holm')[0]
            thres_ind = array > 0
            array[thres_ind] = 0
            output_path = op.join(deriv_path, 'holm', 'mean',
                                  'niftis', 'age_ppln_fdr',
                                  atlas['name'] + '_' + ppln + '_00.nii')
            stat_map_vol = mat_to_nii.make_nii(atlas_nii, np.array(array))
            nib.save(stat_map_vol, output_path)

# Estimate the regional correlation accros subjects for all possible
# combinations of pipelines
df_corr = ppln_corr(ppln_list, ppln_df, atlas_name, select_rois)
df_corr.to_csv(op.join(deriv_path, 'holm', 'mean', 'mean' + '_pplnpairs_rois' +
                       'corr.csv'))
# --------- Make niftis from r and p values ----------------------
if save_nii:
    atlas_nii = nib.load(con.atlas_features[3]['atlas_fname'])
    atlas_voxels = atlas_nii.get_fdata().astype(int)
    affine = atlas_nii.affine
    for ppln_pair in df_corr['pplns'].unique():
        new_vol = np.zeros(atlas_voxels.shape)
        sim_vol = np.zeros(atlas_voxels.shape)
        # Make a nifti per combination with the r values:
        for roi_ind, roi in enumerate(select_rois):
            # For significant correlations
            if df_corr[(df_corr['pplns'] == ppln_pair) & (
                        df_corr['roi'] == 'bsf_' + str(roi_ind+1))][
                        'pearson_p'].values[0] <= 0.05:
                # First positive correlations (similarity)
                # if (df_corr[(df_corr['pplns'] == ppln_pair) & (
                #             df_corr['roi'] == 'bsf_' + str(roi_ind+1))][
                #             'pearson_r'].values[0] > 0):

                sim_vol[atlas_voxels == roi_ind+1] = df_corr[(
                            df_corr['pplns'] == ppln_pair) & (
                            df_corr['roi'] == 'bsf_' + str(roi_ind+1))][
                            'pearson_r'].values[0]

            else:
                sim_vol[atlas_voxels == roi_ind+1] = -2

        print(np.count_nonzero(sim_vol == -2),
              np.count_nonzero(sim_vol == 0),
              np.count_nonzero(sim_vol == 1))
        new_nifti = nib.Nifti1Image(sim_vol, affine, atlas_nii.header)
        nib.save(new_nifti, op.join(deriv_path, 'holm', 'mean', 'niftis',
                                    'BSF_' + ppln_pair + '.nii'))

# Get stats for all ppls (mean, median etc)
df_roi_corr = df_corr.pivot(columns='roi', index='pplns',
                            values='pearson_r')
df_roi_corr = df_roi_corr.rename_axis(None)
# df_roi_corr.rename_axis(columns={'roi':'ppln_pair'})
# df_roi_corr = df_roi_corr.reset_index()

# ========================================================================
# calculate size of region in voxels for schaefer regions
size_roi = {}
size_roi['roi'] = []
size_roi['size'] = []
atlas_voxels = nib.load(selected_atlas[0]['atlas_fname'])
roi_num = np.unique(atlas_voxels.get_fdata())[1:]
for val, roi in zip(roi_num, atlases_rois):
    size_roi['roi'].append(roi)
    size_roi['size'].append(np.count_nonzero(
        atlas_voxels.get_fdata() == val))
    print(roi, val, np.count_nonzero(atlas_voxels.get_fdata() == val))

df_size_roi = pd.DataFrame(size_roi)
# ========================================================================
# Save niftis with min & max of ppln pairs correlation
if save_nii:
    for atlas_set, rois in zip(selected_atlas, [select_rois]):
        atlas = atlas_set['name']
        atlas_nii = atlas_set['atlas_fname']
        df_atlas_roi = df_roi_corr[rois]
        df_atlas_roi = df_atlas_roi.reset_index()
        for ppln_pair in df_corr['pplns'].unique():
            arr = df_atlas_roi[df_atlas_roi['index'] == ppln_pair][
                                                    rois].values[0]
            max_vol = np.zeros(arr.shape[0])
            min_vol = np.zeros(arr.shape[0])
            for x, val in enumerate(arr):
                if val == arr.min():
                    min_vol[x] = 10
                elif val == arr.max():
                    max_vol[x] = 10
            min_vol = mat_to_nii.make_nii(atlas_nii, min_vol)
            max_vol = mat_to_nii.make_nii(atlas_nii, max_vol)
            output_path_min = op.join(deriv_path, 'holm', 'mean', 'niftis',
                                      atlas + '_' + ppln_pair +
                                      '_jul_min.nii')
            output_path_max = op.join(deriv_path, 'holm', 'mean', 'niftis',
                                      atlas + '_' + ppln_pair +
                                      '_Jul_max.nii')
        nib.save(max_vol, output_path_max)
        nib.save(min_vol, output_path_min)

#  ============ create stats between pipelines  =======================
df_stat = df_roi_corr.describe()

ppln_vs_size = {}
ppln_vs_size['ppln_pair'] = []
ppln_vs_size['p'] = []
ppln_vs_size['R'] = []
for ppln_pair in df_roi_corr.index:
    arr = df_roi_corr[df_roi_corr.index == ppln_pair][select_rois].values
    p_r, p_p = pearsonr(arr[0], df_size_roi['size'].values)
    ppln_vs_size['ppln_pair'].append(ppln_pair)
    ppln_vs_size['R'].append(p_r)
    ppln_vs_size['p'].append(p_p)
df_roiVSsize = pd.DataFrame(ppln_vs_size)
logger.info("Correlations between size of ROI (Voxels) and regional "
            "correlations across pipelines \nMax: " +
            str(df_roiVSsize['R'].max()) + "\n" +
            "Min: " + str(df_roiVSsize['R'].min()))

pearson_cor_size_median = pearsonr(df_stat.loc[
    '50%', [col for col in select_rois]].values, df_size_roi['size'])
spearman_cor_size_median = spearmanr(df_stat.loc[
    '50%', [col for col in select_rois]].values, df_size_roi['size'])

# =========== create nifti from non significant correlations (between pplns) ==
if save_nii:
    atlas = 'bsf'
    atlas_nii = selected_atlas[0]['atlas_fname']
    for ppln_pair in df_corr['pplns'].unique():
        corr = df_corr[(df_corr['pplns'] == ppln_pair) & (
             df_corr['atlas'] == atlas)]['pearson_r'] * \
             (1 - multitest.multipletests(
              df_corr[(df_corr['pplns'] == ppln_pair) & (
                 df_corr['atlas'] == atlas)]['pearson_p'],
                 alpha=0.05, method='holm')[0])
        corr.replace(0, np.nan)
        output_path = op.join(deriv_path, 'holm', 'mean', 'niftis',
                              atlas + '_' + ppln_pair +
                              'nonsignif_Jul.nii')
        stat_map_vol = mat_to_nii.make_nii(atlas_nii, corr.values)
        nib.save(stat_map_vol, output_path)
# create an save niftis with min max and median values of ppln pairs corr
    array = df_stat.loc['50%', select_rois]
    max_vol = np.zeros(array.shape[0])
    min_vol = np.zeros(array.shape[0])
    for x, val in enumerate(array):
        if val == array.min():
            min_vol[x] = 10
        elif val == array.max():
            max_vol[x] = 10
    min_vol = mat_to_nii.make_nii(atlas_nii, min_vol)
    max_vol = mat_to_nii.make_nii(atlas_nii, max_vol)
    stat_map_vol = mat_to_nii.make_nii(atlas_nii, array.values)
    # output_path_min = op.join(deriv_path, 'holm', 'mean', 'niftis',
    #                           atlas + '_median_min_Jul.nii')
    # output_path_max = op.join(deriv_path, 'holm', 'mean', 'niftis',
    #                           atlas + '_median_max_Jul.nii')
    output_path = op.join(deriv_path, 'holm', 'mean', 'niftis',
                          atlas + '_median_Jul.nii')
    # nib.save(max_vol, output_path_max)
    nib.save(stat_map_vol, output_path)
    # nib.save(min_vol, output_path_min)

mean_corr = {}
mean_corr['pplns'] = []
mean_corr['fdr_mean'] = []
mean_corr['mean'] = []
mean_corr['atlas'] = []

for atlas_set in [con.atlas_features[3]]:
    atlas = atlas_set['name']
    atlas_nii = atlas_set['atlas_fname']
    for ppln_pair in df_corr['pplns'].unique():
        corr = df_corr[(df_corr['pplns'] == ppln_pair) & (
             df_corr['atlas'] == atlas)]['pearson_r'] * \
             multitest.multipletests(
            df_corr[(df_corr['pplns'] == ppln_pair) & (
                 df_corr['atlas'] == atlas)]['pearson_p'],
                 alpha=0.05, method='holm')[0]

        unsign_rois = 1073 - sum(multitest.multipletests(
                  df_corr[(df_corr['pplns'] == ppln_pair) & (
                   df_corr['atlas'] == atlas)]['pearson_p'],
                  alpha=0.05, method='holm')[0] * 1)
        print(unsign_rois, ppln_pair)
        corr.replace(0, np.nan)
        uncor_corr = df_corr[(df_corr['pplns'] == ppln_pair) & (
             df_corr['atlas'] == atlas)]['pearson_r']
        output_path = op.join(deriv_path, 'holm', 'mean', 'niftis',
                              atlas + '_' + ppln_pair + '.nii')
        array = df_corr[(df_corr['pplns'] == ppln_pair) & (
             df_corr['atlas'] == atlas)]['pearson_r']
        # stat_map_vol = mat_to_nii.make_nii(atlas_nii, array.values)
        # view = plotting.view_img_on_surf(stat_map_vol, threshold='90%',
        #                                 title=ppln_pair)
        # nib.save(stat_map_vol, output_path)
        mean_corr['fdr_mean'].append(np.tanh(
                                      np.nanmean(
                                       np.arctanh(corr))))
        mean_corr['mean'].append(np.tanh(
                                      np.nanmean(
                                       np.arctanh(uncor_corr))))
        mean_corr['pplns'].append(ppln_pair)
        mean_corr['atlas'].append(atlas)
df_mean_corr = pd.DataFrame(mean_corr)

df_mean_corr.to_csv(op.join(deriv_path, 'holm', 'mean', 'mean' + '_pplnpairs_' +
                    'corr.csv'))
df_age_corr.to_csv(op.join(deriv_path, 'holm', 'mean', 'mean' + '_ppln_age_' +
                   'corr.csv'))
n = len(ppln_list)
fig, axs = plt.subplots(nrows=n, ncols=n, figsize=(8, 8),
                        constrained_layout=False,
                        subplot_kw={'xticks': [], 'yticks': []})

atlas_ref = con.atlas_features[3]
atlas = atlas_ref['name']
for row in range(n):
    for col in range(row, n):
        ppln_comb = ppln_list[row] + '_vs_' + ppln_list[col]
        if row == 0:
            axs[row][col].set_xlabel(ppln_label[col], fontsize=16)
            axs[row][col].xaxis.set_label_position('top')
            axs[col][row].set_ylabel(ppln_label[col], fontsize=12)
            # axs[col][row].yaxis.set_label_coords(-.1, 0)
        if row == col:
            axs[row][col].hist(np.array(df_age_corr[
                    df_age_corr['ppln'] == ppln_list[row]][
                    'r_score']), bins=100, color="orange")
            corr_d = np.tanh(np.arctanh(df_age_corr[
                    df_age_corr['ppln'] == ppln_list[row]][
                    'r_score'].values).mean())
            axs[row][col].set_xlim([-1, 1])
            axs[row][col].axvline(x=0, linewidth=.5, color='r')
            leg_d = str("{:.3f}".format(corr_d))
            print(corr_d)
            y_max = axs[col][row].get_ylim()[1]
            axs[col][row].text(-.90, y_max * .8, 'r = ' + leg_d,
                               fontsize=14,
                               style='oblique')
            axs[row][col].set_xticks(np.arange(-.9, 1, .3))
        if row != col:
            corr = df_mean_corr[(df_mean_corr['pplns'] == ppln_comb) &
                                (df_mean_corr['atlas'] == atlas)][
                                 'mean'].values[0]
            fdr_corr = df_mean_corr[(df_mean_corr['pplns'] == ppln_comb) &
                                    (df_mean_corr['atlas'] == atlas)][
                                    'fdr_mean'].values[0]
            axs[row][col].hist(np.array(df_corr[(
                df_corr['pplns'] == ppln_comb) & (
                 df_corr['atlas'] == atlas)]['pearson_r']),
                    bins=100, range=[0, 1])
            leg = str("{:.3f}".format(corr))
            leg_fdr = str("{:.3f}".format(fdr_corr))
            print(corr)
            y_max = axs[row][col].get_ylim()[1]
            axs[row][col].set_ylim([0, y_max + y_max/10])
            axs[row][col].set_xlim([-.01, 1])
            axs[row][col].axvline(x=0, linewidth=.5, color='r')
            # ax.set_ylim([0, y_max +.1])
            axs[row][col].text(.04, y_max * .88,
                               # 'r=' + leg +
                               '  r =' + leg_fdr,
                               fontsize=14,
                               style='oblique')
            axs[row][col].set_facecolor(((1, 1-corr**2, 1-abs(corr))))
            axs[row][col].set_xticks(np.arange(0, 1, .1))

    fig.suptitle("All datasets", fontsize=16)
    fig.subplots_adjust(wspace=0, hspace=0, top=.92, right=.95,
                        left=0.05, bottom=0.05)
    manager = plt.get_current_fig_manager()
    manager.full_screen_toggle()
# fig.set_size_inches((24, 15))
fig.show()
plt.close()
