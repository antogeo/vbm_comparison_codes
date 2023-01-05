#!/usr/bin/bash env python3
# -*- coding: utf-8 -*-

"""
Created: on Monday 29.03.2021
author: Leonard Sasse
"""

# --------------------------------------------------------------------------- #
# Importing Modules

import os

import pandas as pd
import numpy as np
from sklearn.neighbors import NearestNeighbors
os.environ["OPENBLAS_NUM_THREADS"] = "1"

# --------------------------------------------------------------------------- #
# Identification Methods


def get_idiff_matrix(df1, df2):
    """
    Parameters
    ----------
    df1 : Pandas DataFrame
        contains data for every subject from session 1. Each row should
        correspond to a subject.
    df2 : Pandas DataFrame
        contains data for every subject from session 2. Each row should
        correspond to a subject.
    Returns
    -------
    Differential Identifiability Matrix (In this Matrix Values on the diagonal
    represent correlations between the same person, values off the diagonal
    represent all other possible correlations between different persons).
    Amico, E., & Goñi, J. (2018). The quest for identifiability in human
    functional connectomes. Scientific Reports, 8(1), 8254.
    https://doi.org/10.1038/s41598-018-25089-1
    For implementation see:
    https://stackoverflow.com/questions/41823728/how-to-perform-correlation-between-two-dataframes-with-different-column-names
    """

    df1 = df1.T
    df2 = df2.T

    idiff_matrix = pd.concat(
        [df1, df2], axis=1, keys=['df1', 'df2']
    ).corr().loc['df2', 'df1']

    return idiff_matrix


def get_idiff(idiff_matrix):
    """
    Parameters
    ----------
    idiff_matrix : Pandas DataFrame
        Differential Identifiability Matrix.
    Returns
    -------
    idiff : float
        Differential Identifiability between two datasets.
    """

    idiff_matrix = np.array(idiff_matrix)
    diag = np.diagonal(idiff_matrix)
    mask = np.ones(idiff_matrix.shape, dtype=bool)
    np.fill_diagonal(mask, 0)
    off_diag = idiff_matrix[mask]
    idiff = 100 * (np.mean(diag) - np.mean(off_diag))

    return idiff


def identify(target, database, metric="spearman"):
    """
    Parameters
    ----------
    target : pandas dataframe:wq
        Each row should correspond to one subject, each column to a feature
    database : pandas dataframe
        Each row should correspond to one subject, each column to a feature
    id_method : str
        Metric to use for identification. Default is
        "spearman".
        Other supported metrics are the same as for:
        https://scikit-learn.org/stable/modules/generated/sklearn.neighbors.NearestNeighbors.html
    Returns
    -------
    Identification Accuracy
    Finn, E. S., Shen, X., Scheinost, D., Rosenberg, M. D., Huang, J., Chun,
    M. M., Papademetris, X., & Constable, R. T. (2015). Functional connectome
    fingerprinting: Identifying individuals using patterns of brain
    connectivity. Nature Neuroscience, 18(11), 1664–1671.
    https://doi.org/10.1038/nn.4135
    """

    """
    This is an implementation as a for loop, which is closer to Finn et al.'s
    original code, but much slower.
    count = 0  # the count variable keeps track of iterations with
    # accurate identification
    for index, subject in enumerate(target.columns):
        all_corr = database.corrwith(target.iloc[:, index], method=id_method)
        max_value = max(all_corr)
        max_index = all_corr.index[all_corr == max_value]
        if max_index[0] == subject:
            count = count + 1
    return count / len(target.columns)
    """

    D = target.shape[0]

    if metric == "spearman":
        target = target.rank()
        database = database.rank()
        metric = "correlation"
    else:
        metric = metric

    nbrs = NearestNeighbors(n_neighbors=1, metric=metric, n_jobs=1).fit(
        target
    )
    distances, indices = nbrs.kneighbors(database)

    return np.mean(indices.T == np.array(list(range(D))))
