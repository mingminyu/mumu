# coding: utf-8
# ================================================
# Project: mumu
# File: conf/_write_cfg.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 12:57
# Description:
# ================================================
import os


def _default_config_file_path(file_name: str):
    templates_dir = os.path.join(os.path.dirname(__file__))
    return os.path.join(templates_dir, file_name)


def _default_config():
    """Default config file template.

    :return:
    """
    path = _default_config_file_path('default.cfg')
    with open(path, 'r', encoding='utf8') as fh:
        return fh.read()


def write_config():
    """Write config file with default.cfg

    :return:
    """
    config_filename = os.path.join(os.getcwd(), "project.cfg")

    with open(config_filename, 'w', encoding="utf8") as f:
        f.write(_default_config())
