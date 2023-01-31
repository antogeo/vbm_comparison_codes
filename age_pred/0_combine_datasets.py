import pandas as pd
from glob import glob
import os.path as op
import os

ixi_subs = './ixi/ixi_common_subj.csv'
enki_subs = './enki/enki_common_subj.csv'
camcan_subs = './camcan/cc_common_subj.csv'

df_ixi = pd.read_csv(ixi_subs, index_col=0)
df_enki = pd.read_csv(enki_subs, index_col=0)
df_camcan = pd.read_csv(camcan_subs, index_col=0)

df1 = pd.concat([df_ixi, df_enki], axis=0)
df1.to_csv('./ixi_enki/ixi_enki_common_subj.csv')

df2 = pd.concat([df_ixi, df_camcan], axis=0)
df2.to_csv('./ixi_camcan/ixi_camcan_common_subj.csv')

df3 = pd.concat([df_camcan, df_enki], axis=0)
df3.to_csv('./camcan_enki/camcan_enki_common_subj.csv')


# Change the current working directory
os.chdir('/data/project/age_prediction/prediction/features_new/')

savepath = '/data/project/age_prediction/prediction/features_new/camcan_enki/'

ppln_list = ['ants_icbm', 'ants_data',  'ants_fslvbm3',
             'ants_fslvbm23', 'fmriprep1_fslvbm23',
             'fmriprep_fsl_3', 'fslvbm1_3', 'fslvbm_data',
             'cat_icbm', 'cat_data']

datasets = ['camcan', 'enki']

for ppln in ppln_list:
    df_all = pd.DataFrame()
    print(ppln, '---\n')
    for dataset in datasets:
        print(dataset)
        print(glob(op.join(dataset, 'features_' + dataset + '_' + ppln + '*BSF.csv'))[0])
        df = pd.read_csv(glob(op.join(dataset, 'features_' +
                         dataset + '_' + ppln + '*BSF.csv'))[0], index_col=0)
        print(df.shape)
#         # df = df[df['Age'] > 18.0]
# #        df['ppln'] = ppln
        df['site'] = dataset
        if not df_all.empty:
            # df_all = df_all.append(df, ignore_index=True)
            df_all = pd.concat([df_all, df], axis=0)
            df_all = df_all.reset_index(drop=True)
        else:
            df_all = df
    print(df_all.shape)
    df_all.to_csv(savepath + ppln + '_camcan_enki.csv')

