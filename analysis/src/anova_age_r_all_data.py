#!/home/antogeo/.venvs/age_pred/bin/python

import pandas as pd
import os.path as op

from scipy.stats import pearsonr, spearmanr
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.stats import multitest
from statsmodels.formula.api import ols
from src.def_correl import ppln_age_corr
from src.get_data import get_dataframes
from functools import reduce
%matplotlib


datasets = ['ixi', 'camcan', 'enki']
deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines'
save_nii = True
ppln_label = ['ANTs \n general', 'ANTs \n data tmplt',
              'ANTs FSL \n general', 'ANTs FSL \n data tmplt',
              'fMRIprep FSL \n general', 'fMRIprep FSL \n data tmplt',
              'FSLVBM \n general', 'FSLVBM \n data tmplt',
              'CAT12.8 \n general', 'CAT12.8 \n data tmplt']

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
    ppln_df.append(pd.concat([enki_df[ppln_num], cc_df[ppln_num],
                             ixi_df[ppln_num]], axis=0).reset_index(drop=True))

atlas_name = atlases_list
select_rois = atlases_rois

df_age_corr = ppln_age_corr(ppln_list, ppln_df, select_rois)

mean_corr = np.tanh(df_age_corr.groupby('ppln').mean())
df_anova = {}
for ppln_name in ppln_list:
    df_anova[ppln_name] = []
    df_anova[ppln_name] = df_age_corr[
                df_age_corr['ppln'] == ppln_name]["r_score"]

df_describe = pd.DataFrame(df_anova).describe()
df_describe.to_csv(op.join(deriv_path, 'results_report', 'images_paper',
                           'describe_corrage.csv'))
# stats f_oneway functions takes the groups as input and returns
# ANOVA F and p value
anova_list = []
anova_list = [df_anova[ppln].values for ppln in ppln_list]
fvalue, pvalue = stats.f_oneway(df_anova['ants_icbm'],
                                df_anova['ants_data'],
                                df_anova['ants_fslvbm3'],
                                df_anova['ants_fslvbm23'],
                                df_anova['fmriprep1_3'],
                                df_anova['fmriprep1_23'],
                                df_anova['fslvbm13'],
                                df_anova['fslvbm'],
                                df_anova['cat12.8'],
                                df_anova['cat12.8_data'])

res_anova = {}
res_anova['f'] = []
res_anova['p'] = []
res_anova['f'].append(fvalue)

res_anova['p'].append(pvalue)
# Plot the r-values per Roi for each pipeline
plt.figure(figsize=(24.5, 18.3))
ax = sns.violinplot(x='ppln', y='r_score',
                    data=df_age_corr, cmap='smoke')
# ax = sns.swarmplot(x="ppln", y="r_score",
#                    data=df_age_corr, color='salmon')
ax.set_xlabel('Pipelines', fontsize=15)
ax.set_ylabel('Pearson`s r \n regional GMV-age', fontsize=15)
ax.set_title("All data")
ax.tick_params(labelsize=12)
# plt.savefig(op.join(
#             deriv_path, 'results_report', dataset + '_r_val_plot.svg'),
#             format='svg')
plt.xticks(range(len(df_age_corr['ppln'].unique())), ppln_label, fontweight='bold', rotation=45)
plt.show()
df_anova = pd.DataFrame(res_anova)
# df_anova.to_csv(op.join(deriv_path, 'results_report', 'images_paper',
#                         'anova_corrage.csv'))
