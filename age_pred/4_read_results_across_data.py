import pickle
import pandas as pd
import os.path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


data_nm = '/camcan_enki/camcan_enki_'
# data_nm = '/ixi_enki/ixi_enki_'
# data_nm = '/ixi_camcan/ixi_camcan_'


filepath = '/data/project/age_prediction/prediction/results'


model_names = ['ridge', 'rvr', 'kernel_ridge', 'gauss', 'lasso', 'elasticnet']
model_names_new = ['RR', 'RVR', 'KRR', 'GPR', 'LR', 'ENR'] # newer naming


filenm_list = ['fslvbm1_3', 'fslvbm_data', 'fmriprep1_fslvbm23','fmriprep_fsl_3', 'cat_icbm',
               'cat_data', 'ants_icbm', 'ants_fslvbm23', 'ants_fslvbm3', 'ants_data']

filenm_list_new  = ['fslvbm1_3_BSF', 'fslvbm_data_BSF', 'fmriprep1_fslvbm23_BSF','fmriprep_fsl_3_BSF', 'cat_icbm_BSF',
               'cat_data_BSF', 'ants_icbm_BSF', 'ants_fslvbm23_BSF', 'ants_fslvbm3_BSF', 'ants_data_BSF']


# get the saved cv scores
df = pd.DataFrame()
df_cv = pd.DataFrame()
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.scores' #_ncr
    print('filename', filenm)
    if os.path.isfile(filenm):
        res = pickle.load(open(filenm, 'rb'))
        # df = pd.DataFrame(index=res.keys())
        df = pd.DataFrame()
        mae_all, key_all = list(), list()
        for key, value in res.items():
            mae = round(value['test_neg_mean_absolute_error'].mean() * -1, 3)
            print(key, mae)
            mae_all.append(mae)
            key_all.append(key)
        df['models'] = key_all
        df['data'] = len(mae_all) * [filenm_item]
        df['cv'] = mae_all

        print(df)

        df_cv = df_cv.append(df)

df_cv = df_cv.reset_index(drop=True)
cv_filename = filepath + data_nm + 'cv_scores.csv'
df_cv.to_csv(cv_filename)

# get the saved test results
df = pd.DataFrame()
df_test = pd.DataFrame()
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.results' #_ncr
    print('\n', filenm)
    if os.path.isfile(filenm):
        res = pickle.load(open(filenm,'rb'))
        # df = pd.DataFrame(index=res.keys())
        df = pd.DataFrame()
        mae_all, key_all = list(), list()
        for key, value in res.items():
            mae = value['mae']
            mae_all.append(mae)
            key_all.append(key)
        df['models'] = key_all
        df['test'] = mae_all
        df['data'] = len(mae_all) * [filenm_item]
        print(df)
        df_test = df_test.append(df)


df_test = df_test.reset_index(drop=True)
test_filename = filepath + data_nm + 'test_scores.csv'
df_test.to_csv(test_filename)

df_combined = df_cv.merge(df_test, on=['data','models'], how="left")
data_model_name = df_combined['data'].replace(filenm_list, filenm_list_new) + ' + ' + \
                  df_combined['models'].replace(model_names, model_names_new)
df_combined['name'] = data_model_name

# df_combined = df_combined.sort_values(by=['cv'], ascending=True)
combined_filename = filepath + data_nm + 'cv_test_scores.csv'
df_combined.to_csv(combined_filename)

# check model parameeters
print('Checking model parameters')
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.models'
    print('\n','filename', filenm)
    if os.path.isfile(filenm):
        res = pickle.load(open(filenm, 'rb'))
        # print(res)
        for key, value in res.items():
            print(key)
            if key == 'gauss':
                model = res['gauss']['gauss']
                print(model.kernel_.get_params())
            elif key == 'kernel_ridge':
                model = res['kernel_ridge']['kernelridge']
                print(model)
            elif key == 'rvr':
                model = res['rvr']['rvr']
                print(model)
            else:
                model = res[key]['elasticnet']
                print(model.lambda_best_)










