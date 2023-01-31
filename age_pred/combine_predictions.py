import pickle
import pandas as pd
import os.path
import numpy as np



# results file to load
data_nm = '/camcan/features_camcan_'
file_nm = '/camcan/camcan_'
data_path = '/data/project/age_prediction/prediction/features_all_data'
filepath = '/data/project/age_prediction/prediction/results'

filenm_list = ['fslvbm1_3_BSF', 'fslvbm_BSF', 'fmriprep1_fslvbm23_BSF','fmriprep_fsl_3_BSF', 'cat_icbm_BSF',
               'cat_data_BSF', 'ants_icbm_BSF', 'ants_fslvbm23_BSF', 'ants_fslvbm3_BSF', 'ants_data_tmplt_BSF']

# filenm_list = ['fslvbm1_3_BSF', 'fslvbm_BSF']

save_file_nm = 'camcan_within_site.csv'

xx_all = pd.DataFrame()
df_pred = pd.DataFrame()
df = pd.DataFrame()

for idx, filenm_item in enumerate(filenm_list):
    data = data_path + data_nm + filenm_item + '.csv'
    filenm = filepath + file_nm + filenm_item + '.results'
    filenm_model = filepath + file_nm + filenm_item + '.models'

    print('data file: ', data)
    print('results file: ', filenm)
    print('model file:', filenm_model, '\n')

    if os.path.exists(filenm):
        print('Results exists')

        # read the data
        data_df = pd.read_csv(open(data, 'rb'), index_col=0)
        data_df = data_df[data_df['QC']].reset_index(drop=True)
        print(data_df.columns)
        print(data_df.index)

        X = [col for col in data_df if col.startswith('bsf_')]  # Features
        X.remove('bsf_0')
        y = 'Age'  # Dependent var

        data_df[X] = data_df[X].fillna(0)
        data_df = data_df[data_df['QC']].reset_index(drop=True)

        data_df['Age'] = data_df['Age'].round().astype(int) # round off age and convert to integer
        data_df = data_df[data_df['Age'].between(18, 90)].reset_index(drop=True)

        # check for duplicates
        duplicated_subs_1 = data_df[data_df.duplicated(['name'], keep='first')]
        data_df = data_df.drop(duplicated_subs_1.index).reset_index(drop=True)

        # check for duplicates (multiple sessions for one subject)
        duplicated_subs_1 = data_df[data_df.duplicated(['name'], keep='first')]
        data_df = data_df.drop(duplicated_subs_1.index).reset_index(drop=True)

        # sort dataframe in increasing order of age
        data_df.sort_values(by='Age', inplace=True, ignore_index=True)
        print('Number of samples:', len(data_df))
        print('any nans', data_df[X].isnull().values.any(), '\n')

        # Read the results file
        res = pickle.load(open(filenm,'rb'))
        res_model = pickle.load(open(filenm_model, 'rb'))

        df = pd.DataFrame()
        df_pred = pd.DataFrame()

        for key1, value1 in res.items():
            df = pd.DataFrame()
            for key2, value2 in value1.items():
                # print(key1, key2)
                test_idx = value2['test_idx']
                df['name'] = data_df.iloc[test_idx]['name']
                df['Age'] = data_df.iloc[test_idx]['Age']  # just for checking, should be same as df['true']
                df['session'] = data_df.iloc[test_idx]['session']
                df['QC'] = data_df.iloc[test_idx]['QC']
                df['QC_bsf'] = data_df.iloc[test_idx]['QC_bsf']

                model = res_model[key1][key2]
                test_pred = value2['predictions']

                # if (key2 == 'gauss') and (key1 == 'repeat_4'):
                #     X_preprocessed, _ = model.preprocess(data_df.loc[test_idx, X], data_df.iloc[test_idx]['age'])
                #     print(data_df.loc[test_idx, X].shape, X_preprocessed.shape)

                df[filenm_item + ' + ' + key2] = value2['predictions']  # predictions
                # print(df)

            df_pred = df_pred.append(df)
            df_pred.sort_index(axis=0, level=None, ascending=True, inplace=True)

        if len(xx_all) == 0:
            print('getting xx_all for first time')
            print(xx_all)
            xx_all = df_pred
        else:
            print('getting xx_all for SECOND time')
            print(xx_all)
            print(df_pred)
            # xx_all = xx_all.merge(df_pred, on=list(set(data_df.columns.tolist()) - set(X)), how="left")
            xx_all = xx_all.merge(df_pred, on=['name', 'Age','session', 'QC'], how="left") # 'QC_bsf' can't be usd for merging as it has different numbers in diff feature spaces


save_path = filepath + file_nm + save_file_nm
print(save_path)
# xx_all.to_csv(save_path, index=False)




