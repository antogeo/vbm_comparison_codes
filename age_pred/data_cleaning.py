#!/home/smore/.venvs/py3smore/bin/python3
import pandas as pd

def clean_data(data_df, subs_include):

    X = [col for col in data_df if col.startswith('bsf_')]  # Features
    X.remove('bsf_0')
    y = 'Age'  # Dependent var

    data_df = data_df.merge(subs_include, on=["name", "session"], how="right") # keep selected subjects
    data_df = data_df.reset_index(drop=True)

    data_df[X] = data_df[X].fillna(0) # fill nans with zeros in features
    data_df = data_df[data_df['QC']].reset_index(drop=True) # drop QC=False

    data_df['Age'] = data_df['Age'].round().astype(int) # round off age and convert to integer
    data_df = data_df[data_df['Age'].between(18, 90)].reset_index(drop=True)

    # check for duplicates
    duplicated_subs_1 = data_df[data_df.duplicated(['name'], keep='first')]
    data_df = data_df.drop(duplicated_subs_1.index).reset_index(drop=True)

    return data_df, X, y

