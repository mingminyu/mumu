# coding: utf-8
# ================================================
# Project: mumu
# File: decorators/_progressbar.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/22 19:10
# Description:
# ================================================
import re
import time
from tqdm import tqdm
from impala.hiveserver2 import HiveServer2Cursor


def pbar_sql_query(cur=None):
    """
    显示Impala/Hive执行SQL的进度
    :param cur: 执行Query后的cursor
    :return:
    """
    if type(cur) != HiveServer2Cursor:
        raise Exception("cursor occurs error!")

    pbar = tqdm(total=100)
    pbar.set_description('Loading')
    p_last, p = 0, 0

    if hasattr(pbar, "colour"):
        pbar.colour = "green"

    for i in range(120000):
        p_last = int(re.findall(r"(\d+)%", cur.get_log(), re.S)[0]) if cur.get_log() != "" else 0
        query_state = True if cur.status() == "FINISHED_STATE" else False

        if p_last > p:
            pbar.update(p_last - p)
            time.sleep(0.05)
            p = p_last
            continue
        elif p >= 90 or query_state:
            pbar.update(100 - p_last)
            break
        else:
            time.sleep(0.05)

    pbar.close()
