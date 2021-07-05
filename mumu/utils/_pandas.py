# coding: utf-8
# ================================================
# Project: mumu
# File: utils/_pandas.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/24 15:48
# Description:
# ================================================
import os
import pandas as pd
import numpy as np
import dataframe_image as dfi


def df_to_png(df_styled=None):
    try:
        dfi.export(df_styled, filename=os.path.join(os.getcwd(), "tmp.png"))
    except OSError:
        dfi.export(df_styled, filename=os.path.join(os.getcwd(), "tmp.png"), table_conversion="matplotlib")


def value_counts_top_n(series=None, n=1, ascending=True):
    """value counts of the categorical feature, and return top n `value` and ratio

    :param series: Series
    :param n: int, default 1, top n in ascending
    :param ascending: bool, default True.
    :return: list
    """
    if type(series) != pd.Series:
        raise Exception("parameter series must be a pandas series!")

    if ascending:
        df = series.value_counts(normalize=True).head(n).reset_index()
    else:
        df = series.value_counts(normalize=True, ascending=False).head(n).reset_index()

    if len(df) < n:
        return [np.nan, np.nan]

    df.columns = ["value", series.name]
    return df.iloc[n].values.tolist()


def value_counts_bottom_n(series=None, n=1):
    """value counts of the categorical feature, and return bottom n `value` and ratio

    :param series: Series
    :param n: int, default 1, bottom n in ascending
    :return: list
    """
    return value_counts_top_n(series=series, n=n, ascending=False)
