import os.path as op
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
%matplotlib

deriv_path = '/home/antogeo/data/cluster/results/analysis_VBMpipelines'

df_res = pd.read_csv(op.join(
                     deriv_path, 'extr_evaluation',
                     'results_plot.csv'))

ppln_label = ['ANTs \n general', 'ANTs \n data tmplt',
              'ANTs FSL \n general', 'ANTs FSL \n data tmplt',
              'fMRIprep FSL \n general', 'fMRIprep FSL \n data tmplt',
              'FSLVBM \n general', 'FSLVBM \n data tmplt',
              'CAT12.8 \n general', 'CAT12.8 \n data tmplt']

mn = [round(df_res[df_res['ppln'] == ppln]['result'].mean(), 2)
      for ppln in df_res['ppln'].unique()]
pplns_indf = df_res['ppln'].unique()

df_piv = df_res.pivot_table(index='ppln', columns='model',
                            values='result', margins=True,
                            margins_name='Mean').drop('Mean')

df_piv.rename(columns={"gauss": "GPR", "kernel_ridge": "KRR",
                       "lasso": "LASSO", "rvr": "RVR"}, inplace=True)
df_piv = df_piv[['RVR', 'GPR', 'LASSO', 'KRR', 'Mean']].loc[pplns_indf, :]

ax = df_piv.plot.bar()
for n, p in enumerate(ax.patches):
    print(n, p)
    # if not (n % 5):
    if n > 39:
        print(int((n / 5)), p)
        ax.annotate(s=mn[int(n - 40)],
                    xy=(p.get_x()+p.get_width()/2.+0.1, p.get_height()+0.01),
                    ha='center',
                    va='center',
                    xytext=(0, 10),
                    textcoords='offset points', rotation='0', weight='bold')

ax.set_xticklabels(ppln_label, rotation=45, weight='bold')
ax.set_ylabel("Mean Absolute Error", weight='bold')
ax.set_xlabel("Pipelines", weight='bold')


# Cross-site results
df_cross_site = pd.read_csv(op.join(
                     deriv_path, 'extr_evaluation',
                     'res_cross-site.csv'))
mn = [round(df_cross_site[df_cross_site['ppln'] == ppln]['Mean test'].mean(), 2)
      for ppln in df_cross_site['ppln'].unique()]
pplns_indf = df_cross_site['ppln'].unique()

df_piv = df_cross_site.pivot_table(index='ppln', columns='Models',
                                   values='Mean test', margins=True,
                                   margins_name='Mean').drop('Mean')


df_piv = df_piv[['RVR', 'GPR', 'LASSO', 'KRR', 'Mean']].loc[pplns_indf, :]

ax = df_piv.plot.bar()
for n, p in enumerate(ax.patches):

    # print(n, p)
    if n < 40:
        # print(n % 10, (n // 10))
        # print(df_cross_site[df_cross_site['ppln'] == pplns_indf[n % 10]][
        #              'Models'].values[(n // 10)],
        #       df_cross_site[df_cross_site['ppln'] == pplns_indf[n % 10]][
        #                    'Test eNKI'].values[(n // 10)])
        ax.plot(p.get_x()+p.get_width()/2.,
                df_cross_site[df_cross_site['ppln'] == pplns_indf[n % 10]][
                             'Test eNKI'].values[(n // 10)],
                marker='*', color='b', alpha=0.7, label='eNKI')
        ax.plot(p.get_x()+p.get_width()/2.,
                df_cross_site[df_cross_site['ppln'] == pplns_indf[n % 10]][
                             'Test CamCAN'].values[(n // 10)],
                marker='o', color='c', alpha=0.7, label='CamCAN')
        ax.plot(p.get_x()+p.get_width()/2.,
                df_cross_site[df_cross_site['ppln'] == pplns_indf[n % 10]][
                             'Test IXI'].values[(n // 10)],
                marker='+', color='k', alpha=0.7, label='IXI')
        if n == 0:
            plt.legend()
    # if not (n % 5):
    if n > 39:
        print(int((n / 5)), p)
        ax.annotate(s=mn[int(n - 40)],
                    xy=(p.get_x()+p.get_width()/2.+0.1, p.get_height()+0.01),
                    ha='center',
                    va='center',
                    xytext=(0, 10),
                    textcoords='offset points', rotation='0', weight="bold")

ax.set_xticklabels(ppln_label, rotation=45, weight="bold")
ax.set_ylabel("Mean Absolute Error", weight="bold")
ax.set_xlabel("Pipelines", weight="bold")
