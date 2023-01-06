import pandas as pd
import os.path as op
from scipy.stats import pearsonr
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
# %matplotlib


def corrfunc(x, y, ax=None, **kws):
    """Plot the correlation coefficient in the top left hand corner of a plot."""
    r, _ = pearsonr(x, y)
    ax = ax or plt.gca()
    n = len([c for c in ax.get_children() if
            isinstance(c, matplotlib.text.Annotation)])
    pos = (.01, .90 - .1*n)
    # or make positions for every label by hand
    # pos = (.1, .9) if kws['label'] == 'Yes' else (.1, .8)

    ax.annotate("{}: r = {:.2f}".format(kws['label'], r),
                xy=pos, xycoords=ax.transAxes, size=8)


ppln_label = ['ANTs \n general', 'ANTs \n data tmplt',
              'ANTs FSL \n general', 'ANTs FSL \n data tmplt',
              'fMRIprep FSL \n general', 'fMRIprep FSL \n data tmplt',
              'FSLVBM \n general', 'FSLVBM \n data tmplt',
              'CAT12.8 \n general', 'CAT12.8 \n data tmplt']

deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines/holm'
dataset = 'mean'

age_corr = pd.read_csv(op.join(
                       deriv_path, dataset,
                       dataset + '_ppln_age_corr.csv'),
                       index_col=0)
bsf_rois = [x for x in age_corr['roi'].unique() if 'bsf_' in x]
df_roi_corr = age_corr.pivot(columns='roi', index='ppln',
                             values='r_score')
df_roi_corr = df_roi_corr[bsf_rois]
df_roi_corr = df_roi_corr.reindex(
                    ['ants_icbm', 'ants_data',  'ants_fslvbm3',
                     'ants_fslvbm23', 'fmriprep1_3',
                     'fmriprep1_23', 'fslvbm13', 'fslvbm',
                     'cat12.8', 'cat12.8_data'])

df_roi_corr.loc['level'] = ["cortex"] * 1000 + \
                            ["sub-cort"] * 36 + \
                            ["cereb"] * 37

pp = sns.PairGrid(data=df_roi_corr.T, hue='level',
                  diag_sharey=False)
pp.map_upper(sns.scatterplot, s=15)
pp.map_lower(sns.scatterplot, s=15)
pp.map_diag(sns.kdeplot)
# vars=['ants_icbm', 'ants_data',  'ants_fslvbm3',
#       'ants_fslvbm23', 'fmriprep1_3',
#       'fmriprep1_23', 'fslvbm13', 'fslvbm',
#       'cat12.8', 'cat12.8_data'])
for sub_num, ax in enumerate(pp.axes.ravel()):
    if sub_num % 11 != 0:
        ax.axvline(x=0, ls='--', linewidth=1, c='red')
        ax.set_ylim(-.9, .9)
        ax.set_xlim(-.9, .9)
        ax.axhline(y=0, ls='--', linewidth=1, c='red')
# pp.map_lower(sns.kdeplot, cmap="Wistia", shade_lowest=False, bw=0.2)
# pp.map_lower(corrfunc)
for i in range(len(ppln_label)):
    for j in range(len(ppln_label)):
        pp.axes[len(ppln_label)-1, i].xaxis.set_label_text(ppln_label[i],
                                                           fontsize=10,
                                                           fontweight='bold')
        pp.axes[j, 0].yaxis.set_label_text(ppln_label[j],
                                           fontsize=10,
                                           fontweight='bold',
                                           rotation=55)
# pp.map_lower()
pp.add_legend()
pp.fig.suptitle('All data')
plt.margins(tight=True)
plt.subplots_adjust(left=0.04, right=0.99, top=0.97, bottom=0.05)
plt.subplots_adjust(hspace=0.02, wspace=0.02)
plt.show()
# plt.close()
