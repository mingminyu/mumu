# coding: utf-8
# ================================================
# Project: mumu
# File: decorators/_timeit.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021-01-26 00:01:01
# Description: A time-computed decorator for functions
# ================================================
import logging
from datetime import datetime
from functools import wraps


def timeit(func):
    """ Print runtime of `func`.

    :param func: running function
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        res = func(*args, **kwargs)
        end = datetime.now()
        logging.info("cost time: \033[0;32m{0}\033[0m seconds".format(round((end - start).total_seconds(), 3)))

        return res
    return wrapper
