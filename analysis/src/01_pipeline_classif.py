#!/home/antogeo/.venvs/age_pred/bin/python

import pandas as pd
import os.path as op
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import seaborn as sns
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn import svm
from lib.get_data import get_dataframes
from julearn import run_cross_validation
from pprint import pprint
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
    ppln_df.append(pd.concat([enki_df[ppln_num], cc_df[ppln_num],
                   ixi_df[ppln_num]], axis=0).reset_index(drop=True))

rois = atlases_rois

df_all = pd.concat(ppln_df, axis=0, ignore_index=True)
# df_all = df_all.reset_index(drop=True, inplace=True)
df_all = df_all.fillna(0)

scaler = StandardScaler(copy=False)
df_subsc = pd.concat([df_all[
                     ['name', 'session', 'Age', 'label']].reset_index(
                     drop=True),
                     pd.DataFrame(data=scaler.fit_transform(
                                df_all[rois].values.T).T, columns=rois)],
                     axis=1)

# X = df_scaled[rois]
# y = df_scaled['label']
model_params = {'svm__kernel': 'linear'}
df_scaled = [df_all, df_subsc]
scale_methods = ['zscore', '']
for scale_cnt, (scale_method, df_feat) in enumerate(zip(
                scale_methods, df_scaled)):
    rkf = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=35)
    splits = list(rkf.split(df_feat[rois], df_feat['label']))
    # run multiclass classification using julearn
    scores, model = run_cross_validation(
        X=rois, y='label', data=df_feat,
        model=svm.LinearSVC(),
        problem_type='multiclass_classification',
        scoring=['accuracy'], cv=rkf,
        return_estimator='all')
    df_accuracy = scores.set_index(
        ['repeat', 'fold'])['test_accuracy'].unstack()
    df_accuracy.index.name = 'Repeats'
    df_accuracy.columns.name = 'K-fold splits'
    print(df_accuracy)
    y_pred = np.zeros((5, df_feat.shape[0]), dtype='object')
    for iter, (_, val_ind) in enumerate(splits):
        cv_repeat_id = scores.repeat[iter]
        y_pred_i = scores.estimator[iter].predict(
                    df_feat.iloc[val_ind][rois])
        y_pred[cv_repeat_id, val_ind] = y_pred_i
    cm = np.zeros((len(df_feat['label'].unique()),
                   len(df_feat['label'].unique())))
    for cv_pred in y_pred:
        cm = confusion_matrix(df_feat['label'].values,
                              cv_pred.astype(str)) + cm
    np.set_printoptions(suppress=True, precision=4)
    cm = cm / 5
    print(cm)

    sns.set(font_scale=1.2)
    fig, ax = plt.subplots(1, 1, figsize=(10, 7))

    cm_sum = np.sum(cm, axis=1, keepdims=True)
    cm_perc = cm / cm_sum.astype(float) * 100
    annot = np.empty_like(cm).astype(str)
    nrows, ncols = cm.shape
    for i in range(nrows):
        for j in range(ncols):
            c = cm[i, j]
            p = cm_perc[i, j]
            if c == 0:
                annot[i, j] = ''
            else:
                s = cm_sum[i]
                annot[i, j] = '%g/%g' % (c, s)
    df_cm = pd.DataFrame(cm, index=np.array(
                      ppln_label), columns=np.array(ppln_label))
    df_cm.index.name = 'Actual'
    df_cm.columns.name = 'Predicted'
    sns.heatmap(df_cm, cmap="YlGnBu", annot=annot, fmt='').set(
                title='All data Confusion matrix\n ' + scale_method)
    plt.show()
    # plt.savefig(op.join(deriv_path, dataset, sc_name + '.png'))
