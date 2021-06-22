# coding: utf-8
# ================================================
# Project: mumu
# File: decorators/_retry.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/22 19:19
# Description:
# ================================================
import time
import logging
from functools import wraps


def retry(n=5, sleep_time=60):
    def func_retry(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cnt = 1
            while cnt <= n:
                try:
                    res = func(*args, **kwargs)
                    return res
                except Exception as e:
                    logging.info("RUN ERROR! Retry {0} times \n".format(cnt))
                    cnt += 1
                    time.sleep(sleep_time)
                    logging.info("RUN ERROR Messages: {0}".format(e))
            else:
                raise Exception("retry {0} times, but all failed!".format(n))
        return wrapper
    return func_retry
