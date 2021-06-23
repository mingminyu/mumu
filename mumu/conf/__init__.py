# coding: utf-8
# ================================================
# Project: mumu
# File: conf/__init__.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/23 12:44
# Description:
# ================================================
from ._write_cfg import write_config
from ._read_cfg import read_config


def reload_config():
    locals()["PROJECT_CONF"], locals()["DB_CONF"], locals()["HDFS_CONF"], locals()["EMAIL_CONF"], \
        locals()["WWX_CONF"] = read_config()


PROJECT_CONF, DB_CONF, HDFS_CONF, EMAIL_CONF, WWX_CONF = read_config()
