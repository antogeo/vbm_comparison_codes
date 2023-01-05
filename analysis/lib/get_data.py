import pandas as pd
from glob import glob
import os.path as op


deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines'


def get_dataframes(dataset, all=False):
    # fmirprep fslvbm

    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_fmriprep1*23*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_fmriprep1*23*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'fMRIprep FSL \n data tmplt'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_fmriprep1_23 = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_fmriprep1_23 = df

    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_fmriprep_*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_fmriprep_*test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'fMRIprep FSL \n general'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_fmriprep1_3 = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_fmriprep1_3 = df
    # fslvbm
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_fslvbm_*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_fslvbm_*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'FSLVBM \n data tmplt'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_fslvbm = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_fslvbm = df
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_fslvbm1_3*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_fslvbm1_3*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'FSLVBM \n general'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_fslvbm13 = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_fslvbm13 = df
    # ants
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_ants_ic*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_ants_icbm*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'ANTs general'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_ants_icbm = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_ants_icbm = df
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_ants_dat*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_ants_dat*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'ANTs \n data tmplt'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_ants_data = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_ants_data = df
    # ants fslvbm
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_ants_*bm3_**BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_ants*bm3_*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'ANTs FSL \n general'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_ants_fsl3 = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_ants_fsl3 = df
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_ants_*vbm23_*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_ants_*vbm_*test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'ANTs FSL \n data tmplt'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_ants_fsl23 = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_ants_fsl23 = df
    # cat
    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_cat_icbm*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_cat*_icbm*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'CAT12.8'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_cat = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_cat = df

    df_rois = pd.read_csv(glob(op.join(deriv_path, dataset, 'features', '*' +
                          dataset + '_cat_data*BSF.csv'))[0], index_col=0)
    df_tissue = pd.read_csv(glob(op.join(deriv_path, 'segm_qc_files',
                            '*' + dataset + '_cat*_data*_test.csv'))[0],
                            index_col=0)
    df = pd.merge(df_rois, df_tissue, on=['name', 'session'], how='inner')
    df['gm_wm'] = df.gm_mean.div(df.wm_mean)
    df.loc[:, 'label'] = 'CAT12.8 \n data tmplt'
    df.loc[:, 'dataset'] = dataset
    if all is False:
        df_cat_data = df[(df['Age'] > 18.0) & (df['gm_wm'] > 1.5)]
    else:
        df_cat_data = df

    ppln_df = [df_ants_icbm, df_ants_data, df_ants_fsl3, df_ants_fsl23,
               df_fmriprep1_3, df_fmriprep1_23,
               df_fslvbm13, df_fslvbm, df_cat, df_cat_data]
    ppln_label = ['ANTs \n general', 'ANTs \n data tmplt',
                  'ANTs FSL \n general', 'ANTs FSL \n data tmplt',
                  'fMRIprep FSL \n general', 'fMRIprep FSL \n data tmplt',
                  'FSLVBM \n general', 'FSLVBM \n data tmplt',
                  'CAT12.8 \n general', 'CAT12.8 \n data tmplt']

    bsf_rois = [x for x in df_ants_icbm.columns if 'bsf_' in x]
    bsf_rois = bsf_rois[1:]

    # Create lists of atlases, pipelines and dataframes
    atlases_rois = bsf_rois
    atlases_list = ['bsf']
    ppln_list = ['ants_icbm', 'ants_data',  'ants_fslvbm3',
                 'ants_fslvbm23', 'fmriprep1_3',
                 'fmriprep1_23', 'fslvbm13', 'fslvbm',
                 'cat12.8', 'cat12.8_data']
    return(ppln_df, ppln_list, ppln_label, atlases_rois, atlases_list)
