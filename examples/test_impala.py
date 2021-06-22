# coding: utf-8
# ================================================
# Project: mumu
# File: /test_impala.py
# Author: Mingmin Yu
# Email: yumingmin@xinye.com
# Date: 2021/6/22 20:40
# Description:
# ================================================
import os
from mumu.settings import databases
from mumu.db import ImpalaRunner


# Test 1
query = """SELECT * FROM cszc.huawu_tday LIMIT 1000"""
# Test 1.1: just run one sql
runner = ImpalaRunner(config=databases["impala"], sql=query)
runner.run_sql_block()

# Test 1.2: success for with
# with ImpalaRunner(config=databases["impala"], sql=query) as runner:
#     runner.run_sql_block()

# Test 1.3: success for formatted sql
# query = "SELECT * FROM cszc.huawu_tday WHERE 1=1 AND dt='${BATCH_DATE}' LIMIT 100"
# context = {"BATCH_DATE": "2021-05-01"}
# with ImpalaRunner(config=databases["impala"], sql=query, context=context) as runner:
#     runner.run_sql_block()

# Test 1.4: success for verbose
# query = "SELECT * FROM cszc.huawu_tday WHERE 1=1 AND dt='${BATCH_DATE}' LIMIT 100"
# context = {"BATCH_DATE": "2021-05-01"}
# with ImpalaRunner(config=databases["impala"], sql=query, context=context, verbose=False) as runner:
#     runner.run_sql_block()

# Test 1.5: success for retry_times and sleep_time
# query = "SELECT * FROM cszc.huawu_tday WHERE 1=1 ANDdt='${BATCH_DATE}' LIMIT 100"
# context = {"BATCH_DATE": "2021-05-01"}
# with ImpalaRunner(config=databases["impala"], sql=query, context=context,
#                   verbose=False, retry_times=3, sleep_time=20) as runner:
#     runner.run_sql_block()

# Test 1.6: success for sql file
# context = {"BATCH_DATE": "2021-05-01"}
# filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run.sql")
# runner = ImpalaRunner(config=databases["impala"], filename=filename, context=context,
#                       verbose=False, retry_times=3, sleep_time=20)
# runner.run_sql_block(sql_name="sql2")
# runner.close_conn()
