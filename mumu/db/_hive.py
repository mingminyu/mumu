# coding: utf-8
# ================================================
# Project: mumu
# File: db/hive.py
# Author: Mingmin Yu
# Email:yu_mingm623@163.com
# Date: 2021/6/22 17:21
# Description:
# ================================================
from mumu.db import ImpalaRunner


class HiveRunner(ImpalaRunner):
    def __init__(self, config=None, sql=None, filename=None, context=None,
                 verbose=False, retry_times=1, sleep_time=10):
        """Initialization for ImpalaRunner class
        :param sql: Just one query sql.
        :param filename: SQL file
        :param context: Formatted parameters in SQL file
        :param verbose: bool, default True
        :param retry_times: int, Times for retry when run failed.
        :param sleep_time: int, restart time when run failed.
        """
        super(ImpalaRunner, self).__init__(config=config, sql=sql, filename=filename, context=context,
                                           verbose=verbose, retry_times=retry_times, sleep_time=sleep_time)