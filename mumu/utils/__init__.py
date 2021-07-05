# coding: utf-8
# ================================================
# Project: mumu
# File: utils/_read_cfg.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 12:57
# Description:
# ================================================
from ._pandas import df_to_png
from ._pandas import value_counts_top_n as vc_top_n
from ._pandas import value_counts_bottom_n as vc_bot_n


def str_to_list(s="", delimiter=","):
    """split str to a list

    :param s: str
    :param delimiter:
    :return: list
    """
    return s.replace(" ", "").split(delimiter)
