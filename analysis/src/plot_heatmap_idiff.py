import pandas as pd
import seaborn as sns
import os.path as op
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import pearsonr
%matplotlib
deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines/holm'

df_idif = pd.read_csv(op.join(deriv_path, 'mean/idiff.csv'), index_col=0)
df_sq = df_idif.pivot(index='ppln1',
                      columns='ppln2',
                      values='idiff').rename_axis(None, axis=0)
ppln_list = ['ants_icbm', 'ants_data',  'ants_fslvbm3',
             'ants_fslvbm23', 'fmriprep1_3', 'fmriprep1_23',
             'fslvbm13', 'fslvbm', 'cat12.8', 'cat12.8_data']

df_sq = df_sq[ppln_list].reindex(ppln_list)

ticks = ['ANTs \n general', 'ANTs \n data tmplt',
         'ANTs FSL \n general', 'ANTs FSL \n data tmplt',
         'fMRIprep FSL \n general', 'fMRIprep FSL \n data tmplt',
         'FSLVBM \n general', 'FSLVBM \n data tmplt',
         'CAT12.8 \n general', 'CAT12.8 \n data tmplt']

ax1 = sns.heatmap(df_sq, annot=True, cmap='YlOrRd')
ax1.set_yticklabels(ticks)
ax1.set_xticklabels(ticks)
ax1.set_title('Idiff')

# deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines/holm'
df_corr = pd.read_csv(op.join(deriv_path, 'mean', 'mean' + '_pplnpairs_' +
                      'corr.csv'), index_col=0)

only_gen = [1, 3, 5, 7, 18, 20, 22, 31, 33, 40]
only_data = [10, 12, 14, 16, 25, 27, 29, 36, 38, 43]

# First plot all pipeline pairs
plt.figure()
plt.scatter(df_sq.values[np.triu_indices(10, k=1)],
            df_corr['fdr_mean'], c='k',
            label='All')
plt.scatter(df_sq.values[np.triu_indices(10, k=1)][only_data],
            df_corr['fdr_mean'][only_data],
            facecolors='none', edgecolors='r',
            label='Pipelines using Data template')
plt.scatter(df_sq.values[np.triu_indices(10, k=1)][only_gen],
            df_corr['fdr_mean'][only_gen],
            facecolors='none', edgecolors='y',
            label='Pipelines using general template')
r, p = pearsonr(df_sq.values[np.triu_indices(10, k=1)], df_corr['fdr_mean'])
plt.text(33, 0.28, "All")
plt.text(33, 0.25, "r={:.3f}".format(r))
plt.text(33, 0.22, "p={:.3f}".format(p))
r, p = pearsonr(df_sq.values[np.triu_indices(10, k=1)][only_data],
                df_corr['fdr_mean'][only_data])
plt.text(40, 0.28, "Data")
plt.text(40, 0.25, "r={:.3f}".format(r))
plt.text(40, 0.22, "p={:.3f}".format(p))
r, p = pearsonr(df_sq.values[np.triu_indices(10, k=1)][only_gen],
                df_corr['fdr_mean'][only_gen])
plt.text(36.5, 0.28, "General")
plt.text(36.5, 0.25, "r={:.3f}".format(r))
plt.text(36.5, 0.22, "p={:.3f}".format(p))
plt.xlabel('Idiff values')
plt.ylabel('Pearson r values')
plt.title("Idiff vs Correlation bewteen pairs of pipelines")
plt.xlim(12, 47)
plt.ylim(0.2, 1)
plt.legend(loc='upper left')
plt.show()

r, p = pearsonr(df_sq.values[np.triu_indices(10, k=1)][only_gen],
                df_corr['fdr_mean'][only_gen])
plt.figure()
plt.scatter(df_sq.values[np.triu_indices(10, k=1)][only_gen],
            df_corr['fdr_mean'][only_gen])
plt.text(40, 0.35, "r={:.3f}".format(r))
plt.text(40, 0.3, "p={:.3f}".format(p))
plt.xlabel('Idiff values')
plt.ylabel('Pearson r values')
plt.title("General template")
plt.xlim(12, 47)
plt.ylim(0.2, 1)
plt.show()

r, p = pearsonr(df_sq.values[np.triu_indices(10, k=1)][only_data],
                df_corr['fdr_mean'][only_data])
plt.figure()
plt.scatter(df_sq.values[np.triu_indices(10, k=1)][only_data],
            df_corr['fdr_mean'][only_data])
plt.text(40, 0.35, "r={:.3f}".format(r))
plt.text(40, 0.3, "p={:.3f}".format(p))
plt.xlabel('Idiff values')
plt.ylabel('Pearson r values')
plt.title("Data template")
plt.xlim(12, 47)
plt.ylim(0.2, 1)
plt.show()
