# coding: utf-8
# ================================================
# Project: mumu
# File: conf/__init__.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/23 12:44
# Description:
# ================================================
import logging
from ._write_cfg import write_config
from ._read_cfg import read_config


PROJECT_CONF, DB_CONF, HDFS_CONF, EMAIL_CONF, WWX_CONF = read_config()


def reload_config():
    logging.info("Execute in your notebook: \n "
                 "PROJECT_CONF, DB_CONF, HDFS_CONF, EMAIL_CONF, WWX_CONF = read_config()")
