#!/home/smore/.venvs/py3smore/bin/python3
import pickle
import math
import argparse
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import train_test_split, RepeatedStratifiedKFold

from julearn import run_cross_validation
from julearn.utils import configure_logging
from julearn.transformers import register_transformer
# from julearn.model_selection import StratifiedGroupsKFold

from skrvm import RVR
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import Lasso
from sklearn.kernel_ridge import KernelRidge
import sklearn.gaussian_process as gp
from sklearn.decomposition import PCA

from create_splits import *
from glmnet import ElasticNet
from scipy.stats import zscore
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import VarianceThreshold

from data_cleaning import clean_data


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=str, help="Data path")
    parser.add_argument("subs_path", type=str, help="Subject list path")
    parser.add_argument("output_filenm", type=str, help="Output file name")

    args = parser.parse_args()
    data = args.data_path
    subs = args.subs_path
    output_filenm = args.output_filenm
    output_path = '/data/project/age_prediction/prediction/results/' + output_filenm
    print('output_path', output_path)

    # # example inputs
    # data = '/data/project/age_prediction/prediction/features_new/enki/features_enki_ants_data_tmplt_BSF.csv'
    # subs = '/data/project/age_prediction/prediction/features_new/enki/enki_common_subj.csv'
    # output_path = '/data/project/age_prediction/prediction/results/enki/xx'

    # read the data
    data_df = pd.read_csv(open(data, 'rb'), index_col=0)
    print('data columns:', data_df.columns)
    print('data index:', data_df.index)

    # read sub list
    subs_include = pd.read_csv(subs, index_col=0)
    print('subs to include: ', subs_include.shape)

    data_df, X, y = clean_data(data_df, subs_include)
    data_df.sort_values(by='Age', inplace=True, ignore_index=True) # sort dataframe in increasing order of age
    print('Final number of samples:', len(data_df))

    # initialize random seed and create test indices
    rand_seed = 200
    num_splits = 5  # how many train and test split
    n_repeats = 5

    num_bins = math.floor(len(data_df)/num_splits) # num of bins to be created = num of labels created
    test_indices = stratified_splits(bins_on=data_df.index, num_bins=num_bins, data=data_df, num_splits=num_splits,
                                     shuffle=False, random_state=None)  # creates dictionary of test indices
    all_idx = np.array(range(0, len(data_df)))

    # initialize dictionaries to save scores, models and results
    scores_cv = {k: {} for k in test_indices.keys()}
    models = {k: {} for k in test_indices.keys()}
    results = {k: {} for k in test_indices.keys()}

    # register VarianceThreshold as a transformer
    register_transformer('variancethreshold', VarianceThreshold, returned_features='unknown',
                         apply_to='all_features')
    var_threshold = 1e-5

    # Define all models
    rvr = RVR()
    kernel_ridge = KernelRidge()  # kernelridge
    lasso = ElasticNet(alpha=1, standardize=False)
    elasticnet = ElasticNet(alpha=0.5, standardize=False)
    ridge = ElasticNet(alpha=0, standardize=False)
    pca = PCA(.90)  # 90% variance explained

    model_list = [rvr, 'gauss', lasso, kernel_ridge]
    model_names = ['rvr', 'gauss', 'lasso', 'kernel_ridge']

    model_para_list = [{'variancethreshold__threshold': var_threshold, 'rvr__kernel': 'linear'},

                       {'variancethreshold__threshold': var_threshold,
                        'gauss__kernel': gp.kernels.RBF(10.0, (1e-7, 10e7)), 'gauss__n_restarts_optimizer': 300,
                        'gauss__normalize_y': [True, False], 'gauss__random_state': rand_seed, 'cv': 5},

                       {'variancethreshold__threshold': var_threshold, 'elasticnet__random_state': rand_seed},

                       {'variancethreshold__threshold': var_threshold,
                        'kernelridge__alpha': [0.0, 0.001, 0.01, 0.1, 0.5, 1.0, 10.0, 100.0, 1000.0],
                        'kernelridge__kernel': 'polynomial', 'kernelridge__degree': [1, 2], 'cv': 5}
                       ]  # 'search_params':{'n_jobs': 5}

    iter = 0
    for repeat_key in test_indices.keys(): # For 5 fold cv (test_indices have index for test data - generated myself)
        print('repeat', iter)
        test_idx = test_indices[repeat_key]  # get test indices
        train_idx = np.delete(all_idx, test_idx)  # get train indices
        train_df, test_df = data_df.loc[train_idx,:], data_df.loc[test_idx,:]  # get test and train dataframes
        print('train size:', train_df.shape, 'test size:', test_df.shape)

        qc = pd.cut(train_df['Age'].tolist(), bins=5, precision=1)  # create bins for only train set
        print('bin on age on train data (info)', qc.codes)
        print('age_bins', qc.categories, 'age_codes', qc.codes)

        for i in range(0, len(model_names)):
            print(i, model_names[i])

            preprocess_X = ['variancethreshold', 'zscore'] # or None

            cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=rand_seed).split(train_df, qc.codes)

            scores, model = run_cross_validation(X=X, y=y, data=train_df, preprocess_X=preprocess_X,
                                                 problem_type='regression', model=model_list[i], cv=cv,
                                         return_estimator='final', model_params=model_para_list[i], seed=rand_seed,
                                                 scoring=
                                         ['neg_mean_absolute_error', 'neg_mean_squared_error','r2'])

            scores_cv[repeat_key][model_names[i]] = scores

            if model_names[i] == 'kernel_ridge' or model_names[i] == 'gauss':
                models[repeat_key][model_names[i]] = model.best_estimator_
                print('best model', model.best_estimator_)
                print('best para', model.best_params_)
            else:
                models[repeat_key][model_names[i]] = model
                print('best model', model)

            y_true = test_df[y]
            y_pred = model.predict(test_df[X]).ravel()
            y_delta = y_true - y_pred
            print(y_true.shape, y_pred.shape)
            mae = round(mean_absolute_error(y_true, y_pred), 3)
            mse = round(mean_squared_error(y_true, y_pred), 3)
            corr = round(np.corrcoef(y_pred, y_true)[1, 0], 3)

            print('----------', mae, mse, corr)
            results[repeat_key][model_names[i]] = {'predictions': y_pred, 'true': y_true, 'test_idx': test_idx,
                                                   'delta': y_delta, 'mae': mae, 'mse': mse, 'corr': corr}
        iter = iter + 1
    print('ALL DONE')

    pickle.dump(results, open(output_path + '.results', "wb"))
    pickle.dump(scores_cv, open(output_path + '.scores', "wb"))
    pickle.dump(models, open(output_path + '.models', "wb"))









