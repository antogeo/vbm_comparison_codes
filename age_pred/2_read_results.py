import pickle
import pandas as pd
import os.path
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# data_nm = '/ixi/ixi_'
data_nm = '/enki/enki_'
# data_nm = '/camcan/camcan_'

filepath = '/data/project/age_prediction/prediction/results'

cv_file_ext = 'cv.csv'
test_file_ext = 'test.csv'
combined_file_ext = 'cv_test_scores.csv'

model_names = ['ridge', 'rvr', 'kernel_ridge', 'gauss', 'lasso', 'elasticnet']
model_names_new = ['RR', 'RVR', 'KRR', 'GPR', 'LR', 'ENR'] # newer naming

filenm_list = ['fslvbm1_3_BSF', 'fslvbm_data_BSF', 'fmriprep1_fslvbm23_BSF','fmriprep_fsl_3_BSF', 'cat_icbm_BSF',
               'cat_data_BSF', 'ants_icbm_BSF', 'ants_fslvbm23_BSF', 'ants_fslvbm3_BSF', 'ants_data_BSF']

# get the saved cv scores
df = pd.DataFrame()
df_cv = pd.DataFrame()
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.scores'
    print('filename', filenm)
    if os.path.isfile(filenm):
        print('yes')
        res = pickle.load(open(filenm,'rb'))
        df = pd.DataFrame()
        for key1, value1 in res.items():
            print('key1', key1)
            mae_all = list()
            key_all = list()
            for key, value in value1.items():
                mae = round(value['test_neg_mean_absolute_error'].mean() * -1, 3)
                mae_all.append(mae)
                key_all.append(key)

            df['models'] = key_all
            df['data'] = len(mae_all) * [filenm_item]
            df[key1] = mae_all
        print(df)

        df_cv = df_cv.append(df)

xx = df_cv.loc[:, df_cv.columns.str.startswith('repeat_')].values # ro take average over repeats
mean_cv = np.mean(xx, axis=1)
df_cv['mean_cv'] = mean_cv.round(3)
df_cv.reset_index(drop=True, inplace=True)
cv_filename = filepath + data_nm + cv_file_ext
print('cv_filename', cv_filename)
df_cv.to_csv(cv_filename)

# get the saved test results
df = pd.DataFrame()
df_test = pd.DataFrame()
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.results'
    print('\n', filenm)
    if os.path.isfile(filenm):
        res = pickle.load(open(filenm,'rb'))
        df = pd.DataFrame()
        for key1, value1 in res.items():
            mae_all = list()
            key_all = list()
            for key, value in value1.items():
                mae = value['mae']
                mae_all.append(mae)
                key_all.append(key)
            df['models'] = key_all
            df['data'] = len(mae_all) * [filenm_item]
            df[key1] = mae_all
        print(df)
        df_test = df_test.append(df)

xx = df_test.loc[:, df_test.columns.str.startswith('repeat_')].values # ro take average over repeats
xx = xx.astype(float)
mean_test = np.mean(xx, axis=1)
df_test['mean_test'] = mean_test.round(3)
df_test.reset_index(drop=True, inplace=True)
test_filename = filepath + data_nm + test_file_ext
print('test_filename', test_filename)
df_test.to_csv(test_filename)

# combine files
df_combined = df_cv[['models','data', 'mean_cv']].copy()
df_combined['mean_test'] = df_test['mean_test']
# df_combined = df_combined.sort_values(by=['mean_cv'], ascending=True)
df_combined.reset_index(drop=True, inplace=True)
combined_filename = filepath + data_nm + combined_file_ext
print('combined_filename', combined_filename)
df_combined.to_csv(combined_filename)


# check model parameters
print('Checking model parameters')
for filenm_item in filenm_list:
    filenm = filepath + data_nm + filenm_item + '.models'
    print('\n','filename', filenm)
    if os.path.isfile(filenm):
        print('loading model')
        res = pickle.load(open(filenm, 'rb'))

        for key1, value1 in res.items():
            for key2, value2 in value1.items():
                print(key1, key2)
                if key2 == 'linreg':
                    print(res[key1]['linreg']['linreg'].intercept_, res[key1]['linreg']['linreg'].coef_)
                if key2 == 'gauss':
                    model = res[key1]['gauss']['gauss']
                    print(model.kernel_.get_params())
                elif key2 == 'kernel_ridge':
                    model = res[key1]['kernel_ridge']['kernelridge']
                    print(model)
                elif key2 == 'rvr':
                    model = res[key1]['rvr']['rvr']
                    print(model)
                elif key2 == 'rf':
                    model = res[key1]['rf']['rf']
                    print(model)
                else:
                    model = res[key1][key2]['elasticnet']
                    print(model.lambda_best_)


