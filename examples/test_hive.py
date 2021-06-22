# coding: utf-8
# ================================================
# Project: mumu
# File: tests/test_hive.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/22 20:40
# Description:
# ================================================
from mumu.db import HiveRunner
from mumu.settings import databases

# Test 1
query = """SELECT * FROM cszc.huawu_tday LIMIT 1000"""
# Test 1.1: just run one sql
runner = HiveRunner(config=databases["hive"], sql=query)
runner.run_sql_block()
runner.close_conn()
