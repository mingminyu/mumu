# coding: utf-8
# ================================================
# Project: mumu
# File: conf/_read_cfg.py
# Author: Mingmin Yu
# Email: yu_ming623@163.com
# Date: 2021/6/23 12:57
# Description:
# ================================================
import os
import logging
from configparser import ConfigParser
from mumu.conf import write_config
from mumu.utils import str_to_list


def read_config(cfg_file=None):
    """Read project.cfg file in your project.

    :param cfg_file: str, filepath of configurations
    :return: project_conf, db_conf, hdfs_conf, email_conf, wwx_conf
    """
    if cfg_file:
        config_file = cfg_file
    else:
        config_file = os.path.join(os.getcwd(), "project.cfg")

    if not os.path.exists(config_file):
        write_config()
        logging.warning("🚄 Please complete configurations of your project.cfg,"
                        "then execute `PROJECT_CONF, DB_CONF, HDFS_CONF, EMAIL_CONF, WWX_CONF = read_config()` again!")

    config = ConfigParser()
    config.read(config_file, encoding="utf8")

    project_conf = {
        "project_name": config.get("project", "PROJECT_NAME"),
        "project_path": config.get("project", "PROJECT_PATH"),
        "description": config.get("project", "DESCRIPTION"),
        "data_path": config.get("project", "DATA_PATH"),
        "sql_path": config.get("project", "SQL_PATH"),
        "model_path": config.get("project", "MODEL_PATH"),
    }

    db_conf = {
        "impala": {
            "host": str_to_list(config.get("impala", "HOST")),
            "port": config.getint("impala", "PORT"),
            "user": config.get("impala", "USER"),
            "password": config.get("impala", "PASSWORD"),
            "auth_mechanism": config.get("impala", "AUTH_MECHANISM"),
        },
        "impala2": {
            "host": str_to_list(config.get("impala2", "HOST")),
            "port": config.getint("impala2", "PORT"),
            "user": config.get("impala2", "USER"),
            "password": config.get("impala2", "PASSWORD"),
            "auth_mechanism": config.get("impala2", "AUTH_MECHANISM"),
        },
        "hive": {
            "host": str_to_list(config.get("hive", "HOST")),
            "port": config.getint("hive", "PORT"),
            "user": config.get("hive", "USER"),
            "password": config.get("hive", "PASSWORD"),
            "auth_mechanism": config.get("hive", "AUTH_MECHANISM"),
        }
    }

    hdfs_conf = {
        "url": config.get("hdfs", "HOST"),
        "user": config.get("hdfs", "USER")
    }

    email_conf = {
        "user": config.get("email", "USER"),
        "password": config.get("email", "PASSWORD"),
        "recipients": config.get("email", "RECIPIENTS"),
    }

    wwx_conf = {
        "key": config.get("wwx", "KEY"),
        "at": config.get("wwx", "REMINDERS")
        }

    return project_conf, db_conf, hdfs_conf, email_conf, wwx_conf
