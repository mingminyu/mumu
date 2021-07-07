# coding: utf-8
# ================================================
# Project: mumu
# File: feature/_eda.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/28 10:39
# Description: Explore Data Analysis
# ================================================
import os
import logging
import numpy as np
import pandas as pd
from mumu.utils import vc_top_n, vc_bot_n


def categorical_distribution(df_master=None):
    """Distribution of  categorical variables

    :param df_master: DataFrame, only contains categorical features
    :return: df_cat_report: DataFrame
    """
    cat_cols = df_master.coulumns.tolist()
    df_cat_report = pd.DataFrame(cat_cols, columns=["COLUMN_NAME"])
    df_cat_report["TYPE"] = "STRING"
    df_cat_report["ROWS"] = df_master.shape[0]
    df_cat_report["MISS"] = [df_master[col].isnull().sum() for col in cat_cols]
    df_cat_report["NOMISS"] = [df_master[col].count() for col in cat_cols]
    df_cat_report["MISSING_RATE"] = df_cat_report['MISS'] / df_cat_report['ROWS']
    df_cat_report["UNIQUE"] = [len(df_master[col].dropna().unique()) for col in cat_cols]
    df_cat_report["UNIQUE10"] = [", ".join(df_master[col].dropna().unique()[:10]) for col in cat_cols]

    df_cat_report["VC_TOP1"] = [vc_top_n(df_master[col], 1)[0] for col in cat_cols]
    df_cat_report["VC_TOP1_RATIO"] = [vc_top_n(df_master[col], 1)[1] for col in cat_cols]
    df_cat_report["VC_TOP2"] = [vc_top_n(df_master[col], 2)[0] for col in cat_cols]
    df_cat_report["VC_TOP2_RATIO"] = [vc_top_n(df_master[col], 2)[1] for col in cat_cols]
    df_cat_report["VC_TOP3"] = [vc_top_n(df_master[col], 3)[0] for col in cat_cols]
    df_cat_report["VC_TOP3_RATIO"] = [vc_top_n(df_master[col], 3)[1] for col in cat_cols]
    df_cat_report["VC_TOP4"] = [vc_top_n(df_master[col], 4)[0] for col in cat_cols]
    df_cat_report["VC_TOP4_RATIO"] = [vc_top_n(df_master[col], 4)[1] for col in cat_cols]
    df_cat_report["VC_TOP5"] = [vc_top_n(df_master[col], 5)[0] for col in cat_cols]
    df_cat_report["VC_TOP5_RATIO"] = [vc_top_n(df_master[col], 5)[1] for col in cat_cols]

    df_cat_report["VC_BOT1"] = [vc_bot_n(df_master[col], 1)[0] for col in cat_cols]
    df_cat_report["VC_BOT1_RATIO"] = [vc_bot_n(df_master[col], 1)[1] for col in cat_cols]
    df_cat_report["VC_BOT2"] = [vc_bot_n(df_master[col], 2)[0] for col in cat_cols]
    df_cat_report["VC_BOT2_RATIO"] = [vc_bot_n(df_master[col], 2)[1] for col in cat_cols]
    df_cat_report["VC_BOT3"] = [vc_bot_n(df_master[col], 3)[0] for col in cat_cols]
    df_cat_report["VC_BOT3_RATIO"] = [vc_bot_n(df_master[col])[1] for col in cat_cols]
    df_cat_report["VC_BOT4"] = [vc_bot_n(df_master[col], 4)[0] for col in cat_cols]
    df_cat_report["VC_BOT4_RATIO"] = [vc_bot_n(df_master[col])[1] for col in cat_cols]
    df_cat_report["VC_BOT5"] = [vc_bot_n(df_master[col], 5)[0] for col in cat_cols]
    df_cat_report["VC_BOT5_RATIO"] = [vc_bot_n(df_master[col], 5)[1] for col in cat_cols]

    return df_cat_report


def numeric_distribution(df_master=None):
    """Distribution of numeric variables

    :param df_master: DataFrame, only contains numeric features
    :return: df_num_report: DataFrame
    """
    num_cols = df_master.columns
    df_num_report = pd.DataFrame(num_cols, columns=["COLUMN_NAME"])
    df_num_report["TYPE"] = "NUM"
    df_num_report["ROWS"] = df_master.shape[0]
    df_num_report["MISS"] = [df_master[col].isnull().sum() for col in num_cols]
    df_num_report["NOMISS"] = [df_master[col].count() for col in num_cols]
    df_num_report["MISSING_RATE"] = df_num_report['MISS'] / df_num_report["ROWS"]
    df_num_report["UNIQUE"] = [len(df_master[col].dropna().unique()) for col in num_cols]
    df_num_report["UNIQUE10"] = [", ".join(sorted(df_master[col].dropna().unique())[:10]) for col in num_cols]
    # 分位数
    df_num_report["MEAN"] = [df_master[col].mean() for col in num_cols]
    df_num_report["STD"] = [df_master[col].std() for col in num_cols]
    df_num_report["MIN/TOP1"] = [df_master[col].min() for col in num_cols]
    df_num_report["P1/TOP2"] = [np.percentile(df_master[col].dropna(), q=1) for col in num_cols]
    df_num_report["P5/TOP3"] = [np.percentile(df_master[col].dropna(), q=5) for col in num_cols]
    df_num_report["P10/TOP4"] = [np.percentile(df_master[col].dropna(), q=10) for col in num_cols]
    df_num_report["P25/TOP5"] = [np.percentile(df_master[col].dropna(), q=25) for col in num_cols]
    df_num_report["P50/MEDIUM"] = [np.percentile(df_master[col].dropna(), q=50) for col in num_cols]
    df_num_report["P75/BOT5"] = [np.percentile(df_master[col].dropna(), q=75) for col in num_cols]
    df_num_report["P90/BOT4"] = [np.percentile(df_master[col].dropna(), q=90) for col in num_cols]
    df_num_report["P95/BOT3"] = [np.percentile(df_master[col].dropna(), q=95) for col in num_cols]
    df_num_report["P99/BOT2"] = [np.percentile(df_master[col].dropna(), q=99) for col in num_cols]
    df_num_report["MAX/BOT1"] = [df_master[col].max() for col in num_cols]

    return df_num_report


def explore_data_distribution(df_master=None, cat_cols=None, num_cols=None, save_path=None):
    """Automatic eda of your data, save results to a excel file

    :param df_master: DataFrame
    :param cat_cols: list, categorical columns
    :param num_cols: list, numeric columns
    :param save_path: str,
    :return:
    """
    df_cat_report = categorical_distribution(df_master=df_master[cat_cols])
    df_num_report = categorical_distribution(df_master=df_master[num_cols])

    if save_path:
        with pd.ExcelWriter(save_path) as writer:
            df_cat_report.to_excel(writer, sheet_name="CAT", index=False, encoding='utf8')
            df_num_report.to_excel(writer, sheet_name="NUM", index=False, encoding='utf8')
