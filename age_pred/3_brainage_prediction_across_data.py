#!/home/smore/.venvs/py3smore/bin/python3
import pickle
import math
import argparse
import numpy as np
import pandas as pd

from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.model_selection import RepeatedStratifiedKFold, StratifiedKFold

from julearn import run_cross_validation
# from julearn.utils import configure_logging
from julearn.transformers import register_transformer
from sklearn.feature_selection import VarianceThreshold

from skrvm import RVR
import sklearn.gaussian_process as gp
from sklearn.kernel_ridge import KernelRidge
from glmnet import ElasticNet
from scipy.stats import zscore
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

from data_cleaning import clean_data


def none_or_str(value):
    if value == 'None':
        return None
    return value


if __name__ == '__main__':

    # Read arguments from submit file
    parser = argparse.ArgumentParser()
    parser.add_argument("data_path", type=str, help="Data path")
    parser.add_argument("subs_path", type=str, help="Subject list path train")
    parser.add_argument("output_filenm", type=str, help="Output file name")
    parser.add_argument("--models", type=str, nargs='?', const=1, default="RR",
                       help="models to use (comma seperated no space): RR,LinearSVC")
    parser.add_argument("test_data_path", type=str, help="Test Data path")
    parser.add_argument("test_subs_path", type=str, help="Subject list path test")
    parser.add_argument("confounds", type=none_or_str, help="confounds", default=None)

    args = parser.parse_args()
    data = args.data_path
    subs = args.subs_path
    test_data = args.test_data_path
    test_subs = args.test_subs_path
    output_filenm = args.output_filenm
    output_path = '/data/project/age_prediction/prediction/results/' + output_filenm
    model_required = [x.strip() for x in args.models.split(',')]  # converts string into list
    confounds = args.confounds

    print('input data:', data)
    print('subject info:', subs)
    print('test_data:', test_data)
    print('test subject info:', test_subs)
    print('model_required:', model_required, type(model_required))
    print('output_path:', output_path)
    print('confounds:', confounds, type(confounds))


    # data = '/data/project/age_prediction/prediction/features_new/camcan_enki/ants_data_camcan_enki.csv'
    # subs = '/data/project/age_prediction/prediction/features_new/camcan_enki/camcan_enki_common_subj.csv'
    # test_data = '/data/project/age_prediction/prediction/features_new/ixi/features_ixi_ants_data_BSF.csv'
    # test_subs = '/data/project/age_prediction/prediction/features_new/ixi/ixi_common_subj.csv'
    # output_filenm = args.output_filenm
    # output_path = '/data/project/age_prediction/prediction/results/' + output_filenm
    # model_required = [x.strip() for x in args.models.split(',')]  # converts string into list
    # confounds = args.confounds

    # Load the train data
    data_df = pd.read_csv(open(data, 'rb'), index_col=0)
    print(data_df.columns)
    print(data_df.index)

    # read sub list
    subs_include = pd.read_csv(subs, index_col=0)
    print('subs to include: ', subs_include.shape)

    data_df, X, y = clean_data(data_df, subs_include)
    # sort dataframe in increasing order of age if need be
    #    data_df.sort_values(by='Age', inplace=True, ignore_index=True)
    print('Final number of samples:', len(data_df))

    if confounds is not None: # convert sites in numbers to perform confound removal
        site_name = data_df['site'].unique()
        if type(site_name[0]) == str:
            site_dict = {k: idx for idx, k in enumerate(site_name)}
            data_df['site'] = data_df['site'].replace(site_dict)
    print(data_df.head(), data_df.shape)

    # Load the test data
    test_df = pd.read_csv(open(test_data, 'rb'), index_col=0)
    subs_include_test = pd.read_csv(test_subs, index_col=0)
    test_df, X_test, y_test = clean_data(test_df,  subs_include_test)

    cols_keep = list(set(test_df.columns.tolist()) - set(X_test))
    output_df = test_df[cols_keep]  # initialize output df to save results

    if confounds is not None:  # add site to features & convert site in a number to predict with model trained with  confound removal
        X_test.append(confounds)
        site_name = test_df['site'].unique()[0,]
        if type(site_name) == str:
            # test_df['site'] = test_df['site'].replace({site_name: 5})
            test_df['site'] = 5

    # Initialize variables, set random seed, create classes for age
    scores_cv, models, results = {}, {}, {}
    rand_seed, n_splits, n_repeats = 200, 5, 5
    qc = pd.cut(data_df['Age'].tolist(), bins=5, precision=1)  # create bins for train data only
    print('age_bins', qc.categories, 'age_codes', qc.codes)
    data_df['bins'] = qc.codes # add bin/classes as a column in train df

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

    for ind in range(0, len(model_required)): # run only for required models and not all
        print('model required index and name:', ind, model_required[ind])

        i = model_names.index(model_required[ind])  # find index of required model in model_names list and use this index i to access model params
        assert model_required[ind] == model_names[i] # sanity check
        print('model picked from the list', model_names[i], model_list[i])

        if confounds is None:
            preprocess_X = ['variancethreshold', 'zscore']
        else:
            preprocess_X = ['variancethreshold', 'zscore', 'remove_confound']

        cv = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=rand_seed).split(data_df,
                                                                                                           data_df.bins)

        scores, model = run_cross_validation(X=X, y=y, data=data_df, preprocess_X=preprocess_X, confounds=confounds,
                                             problem_type='regression', model=model_list[i], cv=cv,
                                     return_estimator='final', model_params=model_para_list[i], seed=rand_seed,
                                             scoring=
                                     ['neg_mean_absolute_error', 'neg_mean_squared_error','r2'])

        scores_cv[model_names[i]] = scores

        if model_names[i] == 'kernel_ridge' or model_names[i] == 'gauss':
            models[model_names[i]] = model.best_estimator_
            print('best model', model.best_estimator_)
            print('best para', model.best_params_)
        else:
            models[model_names[i]] = model
            print('best model', model)

        # get predictions for test data
        y_true = test_df[y_test]
        y_pred = model.predict(test_df[X_test]).ravel()
        y_delta = y_true - y_pred
        print(y_true.shape, y_pred.shape)
        mae = round(mean_absolute_error(y_true, y_pred), 3)
        mse = round(mean_squared_error(y_true, y_pred), 3)
        corr = round(np.corrcoef(y_pred, y_true)[1, 0], 3)
        print('----------', mae, mse, corr)
        output_df[model_names[i]] = y_pred

        results[model_names[i]] = {'predictions': y_pred, 'true': y_true,
                                               'delta': y_delta, 'mae': mae, 'mse': mse, 'corr': corr}
        print(results)

    print('ALL DONE')
    output_df.to_csv(output_path + '_prediction.csv', index=False)
    pickle.dump(results, open(output_path + '.results', "wb"))
    pickle.dump(models, open(output_path + '.models', "wb"))
    pickle.dump(scores_cv, open(output_path + '.scores', "wb"))









