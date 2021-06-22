# coding: utf-8
# ================================================
# Project: mumu
# File: db/_check.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/22 21:53
# Description: 
# ================================================
import re


def list_tables_in_sql(query_sql=None, filename=None):
    """Check and list tables in `query_sql` or `filename`.

    :param query_sql: str, SQLr
    :param filename: str, sql file
    :return: list, tables used in `query_sql` or `filename`.
    """
    pattern = r"(?:from|FROM|join|JOIN|^\s*(?:\s*\[shuffle|SHUFFLE\])?)\s+([^ ()\s]+)\s*"

    if filename:
        with open(filename, "r", encoding="utf8") as f:
            results = list(set(re.findall(pattern, f.read())))
            return results

    if query_sql:
        results = list(set(re.findall(pattern, query_sql)))
        return results
