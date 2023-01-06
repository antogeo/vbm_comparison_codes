#!/home/antogeo/.venvs/age_pred/bin/python

import pandas as pd
import os.path as op
from lib.leap.logging import (configure_logging, finish_logging,
                              logger)
from scipy.stats import pearsonr, spearmanr
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import constants as con
import matplotlib
from src.get_data import get_dataframes
%matplotlib


deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines/holm'

datasets = ['enki', 'camcan', 'ixi']

# ppln_list = df_age['ppln'].unique()
for dataset in datasets:
    df_age_corr = pd.read_csv(op.join(deriv_path, dataset,
                              dataset + '_ppln_age_' +
                              'corr.csv'), index_col=0)
    df_ppln_comp = pd.read_csv(op.join(deriv_path, dataset,
                               dataset + '_pplnpairs_' + 'corr.csv'),
                               index_col=0)
    df_rois_corr = pd.read_csv(op.join(deriv_path, dataset, dataset +
                               '_pplnpairs_rois' + 'corr.csv'), index_col=0)
    _, ppln_list, ppln_label, atlases_rois, atlases_list = get_dataframes(
        dataset)
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
                corr = df_ppln_comp[(df_ppln_comp['pplns'] == ppln_comb) &
                                    (df_ppln_comp['atlas'] == atlas)][
                                     'mean'].values[0]
                fdr_corr = df_ppln_comp[(df_ppln_comp['pplns'] == ppln_comb) &
                                        (df_ppln_comp['atlas'] == atlas)][
                                        'fdr_mean'].values[0]
                axs[row][col].hist(np.array(df_rois_corr[(
                    df_rois_corr['pplns'] == ppln_comb) & (
                     df_rois_corr['atlas'] == atlas)]['pearson_r']),
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

        fig.suptitle(dataset, fontsize=16)
        fig.subplots_adjust(wspace=0, hspace=0, top=.92, right=.95,
                            left=0.05, bottom=0.05)
        manager = plt.get_current_fig_manager()
        manager.full_screen_toggle()
    # fig.set_size_inches((24, 15))
    fig.show()

    matplotlib.pyplot.savefig(op.join(deriv_path, dataset,
                              dataset + '_hist_plot.svg'), dpi=None,
                              facecolor='w', edgecolor='w',
                              orientation='portrait',
                              papertype=None, format='svg',
                              transparent=False,
                              bbox_inches='tight', pad_inches=.0,
                              metadata=None)

    # matplotlib.pyplot.close('all')
