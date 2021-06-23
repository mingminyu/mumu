# coding: utf-8
# ================================================
# Project: mumu
# File: utils/_read_cfg.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 12:57
# Description:
# ================================================


def str_to_list(s="", delimiter=","):
    """split str to a list

    :param s: str
    :param delimiter:
    :return: list
    """
    return s.replace(" ", "").split(delimiter)
