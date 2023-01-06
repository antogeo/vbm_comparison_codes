import pandas as pd
import itertools
from scipy.stats import pearsonr, spearmanr


def ppln_age_corr(ppln_list, ppln_df, rois):
    age_corr = {}
    age_corr['r_score'] = []
    age_corr['p_val'] = []
    age_corr['roi'] = []
    age_corr['ppln'] = []
    for ppln_name, df in zip(ppln_list, ppln_df):
        age = df['Age'].values
        # iterate over atlases. enumerate to get the number of row in subplots
        for roi in rois:
            data_region = df[roi].fillna(0)
            # pyplot.scatter(data_age, data_region)
            r_score, p_val = pearsonr(age, data_region)
            age_corr['r_score'].append(r_score)
            age_corr['p_val'].append(p_val)
            age_corr['roi'].append(roi)
            age_corr['ppln'].append(ppln_name)
    # create dataframe with age-mean_regional_value for each ppln
    return(pd.DataFrame(age_corr))


# Estimate the regional correlation accros subjects for all possible 
# combinations of pipelines.
def ppln_corr(ppln_list, ppln_df, atlas_fname, select_rois=None):

    if select_rois is None:
        select_rois = [x for x in ppln_df[0].columns
                       if atlas_fname[0] + '_' in x]
    results = {}
    results['roi'] = []
    results['pearson_r'] = []
    results['spearman_r'] = []
    results['pearson_p'] = []
    results['spearman_p'] = []
    results['pplns'] = []
    results['atlas'] = []
    for atlas in atlas_fname:
        for roi in select_rois:
            for a, b in itertools.combinations(zip(ppln_list, ppln_df), 2):
                ppln1 = a[1][['name', 'session', roi]]
                ppln2 = b[1][['name', 'session', roi]]
                common = pd.merge(ppln1,
                                  ppln2, on=['name', 'session'])
                # common = pd.merge(a[1].sort_values(['name', 'session']),
                #                   b[1].sort_values(['name', 'session']),
                #                   on=['name', 'session'])
                p_r, p_p = pearsonr(common[roi + '_x'].fillna(0),
                                    common[roi + '_y'].fillna(0))
                s_r, s_p = spearmanr(common[roi + '_x'].fillna(0),
                                     common[roi + '_y'].fillna(0))
                results['roi'].append(roi)
                results['pearson_r'].append(p_r)
                results['pearson_p'].append(p_p)
                results['spearman_r'].append(s_r)
                results['spearman_p'].append(s_p)
                results['atlas'].append(atlas)
                results['pplns'].append(a[0]+'_vs_'+b[0])
    return(pd.DataFrame(results))
