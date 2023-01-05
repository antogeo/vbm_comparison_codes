from lib.get_data import get_dataframes
from lib.idiff_calc import get_idiff_matrix, get_idiff, identify
from functools import reduce
import pandas as pd
import os.path as op

deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines'
dataset = 'mean'

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
    enki_df[num] = df.merge(enki_merged.drop_duplicates(
                            subset='name', keep='first'),
                            on=['name', 'session'], how='right')

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
                   ixi_df[ppln_num]],
                   axis=0).reset_index(drop=True))

accur = {}
accur['dataset'] = []
accur['ppln1'] = []
accur['ppln2'] = []
accur['accuracy'] = []
for df_1, ppln1 in zip(ppln_df, ppln_list):
    df_ppln1 = df_1.set_index('name')[atlases_rois]
    df_ppln1.rename_axis(None, inplace=True)
    for df_2, ppln2 in zip(ppln_df, ppln_list):
        df_ppln2 = df_2.set_index('name')[atlases_rois]
        df_ppln2.rename_axis(None, inplace=True)
        if ppln1 != ppln2:
            accur['ppln1'].append(ppln1)
            accur['ppln2'].append(ppln2)
            accur['dataset'].append(dataset)
            accur['accuracy'].append(identify(df_ppln1.fillna(0),
                                              df_ppln2.fillna(0),
                                              metric="correlation"))
df_ident = pd.DataFrame(accur)
df_ident.to_csv(op.join(deriv_path, 'holm', dataset, 'ident_accur_unique.csv'))
# identification
simil = {}
simil['dataset'] = []
simil['ppln1'] = []
simil['ppln2'] = []
simil['idiff'] = []
for df_1, ppln1 in zip(ppln_df, ppln_list):
    df_ppln1 = df_1.set_index('name')[atlases_rois]
    df_ppln1.rename_axis(None, inplace=True)
    for df_2, ppln2 in zip(ppln_df, ppln_list):
        df_ppln2 = df_2.set_index('name')[atlases_rois]
        df_ppln2.rename_axis(None, inplace=True)
        if ppln1 != ppln2:
            print(dataset, ppln1, ppln2)
            idiff_mat = get_idiff_matrix(df_ppln1, df_ppln2)
            idiff_val = get_idiff(idiff_mat)
            simil['idiff'].append(idiff_val)
            simil['ppln1'].append(ppln1)
            simil['ppln2'].append(ppln2)
            simil['dataset'].append(dataset)
df_ident = pd.DataFrame(simil)
df_ident.to_csv(op.join(deriv_path, 'holm', dataset, 'idiff_unique.csv'))
