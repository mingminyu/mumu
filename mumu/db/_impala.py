# coding: utf-8
# ================================================
# Project: mumu
# File: db/_impala.py
# Author: Mingmin Yu
# Email: yu_mingm623@163.com
# Date: 2021/6/22 17:02
# Description:
# ================================================
import os
import re
import time
import logging
import pandas as pd
from impala.dbapi import connect
from impala.util import as_pandas
from mumu.decorators import pbar_sql_query, timeit, retry


class ImpalaRunner(object):
    def __init__(self, config=None, sql=None, filename=None, context=None, verbose=True,
                 retry_times=1, sleep_time=10):
        """Initialization for ImpalaRunner class

        :param config: dict, Configurations for Impala.
            example:
                {
                    'host': ['1.1.1.1', '2.2.2.2'],
                    'port': 25005,
                    'user': '',
                    'password': '',
                    'auth_mechanism': 'PLAIN'
                }
        :param sql: Just one query sql.
        :param filename: SQL file
        :param context: Formatted parameters in SQL file
        :param verbose: bool, default True
        :param retry_times: int, Times for retry when run failed.
        :param sleep_time: int, restart time when run failed.
        """
        self.config = config
        self.filename = filename
        self.conn = self._create_conn()
        self.context = context or {}
        self.verbose = verbose
        self.retry_times = retry_times
        self.sleep_time = sleep_time

        if filename:
            self.sqls = self._parse_filename()
        elif sql:
            self.sqls = {"query": self._formatted_sql(sql)}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Make `ImpalaRunner` class support with.

        :param exc_type:
        :param exc_val:
        :param exc_tb:
        :return:
        """
        self.close_conn()
        logging.info("DB connection has been closed!")

    def _create_conn(self):
        """Create a conn for ImpalaRunner.

        :return: Impala conn
        """
        host = self.config["host"]
        auth_mechanism = self.config["auth_mechanism"]
        port = self.config["port"]
        user = self.config["user"]
        password = self.config["password"]
        conn = None

        if not isinstance(host, list):
            conn = connect(host=host, auth_mechanism=auth_mechanism, port=port,
                           user=user, password=password, timeout=60)
        else:
            for h in host:
                try:
                    conn = connect(host=h, auth_mechanism=auth_mechanism, port=port,
                                   user=user, password=password, timeout=60)
                    break
                except Exception as e:
                    logging.error(e)

        if conn is None:
            raise Exception("No Connection Established.")

        return conn

    def close_conn(self):
        self.conn.close()

    def _parse_filename(self):
        """Parse SQL file and get a dict of pre-run SQLs.

        :return: dict,
            key is sql title, value is pre-run sql.
            example:
                {
                    "sql1": "select * from t1",
                    "sql2": "select * from t2"
                }
        """
        with open(self.filename, "r", encoding="utf8") as f:
            file_context = f.read().replace("${", "{")
            pat = r"--\[(.*?)\](.*?)\n--\[end\].*?"
            sqls = dict([(k, v.format_map(self.context))
                         for k, v in re.findall(pat, file_context, re.S) if v != ""])

        return sqls

    def _formatted_sql(self, sql):
        """Formatted query sql with parameters in context.

        :param sql: str, Query SQL
        :return: str, Formatted SQL
        """
        if self.context:
            sql = sql.replace("${", "{").format_map(self.context)

        return sql

    @staticmethod
    def _verify_df(df=None):
        """修正列名

        :param df: DataFrame
        :return: DataFrame
        """
        if df is None:
            raise Exception("Parameter `df` can not be None!")

        # 修正列名
        df.columns = [col.rsplit('.', 1)[-1] for col in df.columns]

        # 修正列类型
        for col in df.columns:
            series = df[col][df[col].notnull()]

            if not series.empty:
                if type(series.iloc[0]).__name__ == 'Decimal':
                    df[col] = df[col].astype(float)
                if type(series.iloc[0]).__name__ == 'Timestamp':
                    df[col] = df[col].astype(str)

        return df

    def _cursor_to_df(self, cursor):
        """Fetch all records with cursor.

        :param cursor:
        :return:
        """
        data = cursor.description

        if data is not None and hasattr(data, '__iter__'):
            names = [metadata[0] for metadata in data]
            df = as_pandas(cursor)
            df.columns = names
        else:
            df = pd.DataFrame()

        df = self._verify_df(df)

        return df

    @timeit
    def _run_sql(self, sql=""):
        """Execute One SQL.

        :param sql: str, Pre-run SQL.
        :return:
        """
        cur = self.conn.cursor()

        if sql.replace(" ", "") == "":
            logging.info("Executed sql is null")
            cur.close()
            return pd.DataFrame()
        else:
            logging.info("Starting run sql:\n \033[1;34m{sql}\033[0m \n".format(sql=sql))

            if self.verbose and sql.upper().find("SELECT") != -1:
                cur.execute_async(sql)
                time.sleep(2)
                pbar_sql_query(cur)
            else:
                cur.execute(sql)

            df = self._cursor_to_df(cur)
            cur.close()

            return df

    def run_sql_block(self, sql_name=None):
        @retry(n=self.retry_times, sleep_time=self.sleep_time)
        def _run_sql_block(sqlname=None):
            """According to `sql_name` to execute corresponding sql.

            :param sqlname: str, index for block sql in filename.
            :return: DataFrame
            """
            if sqlname is not None:
                sqls = self.sqls[sqlname]
                results = [self._run_sql(sql) for sql in sqls.split(";")]
            else:
                results = []

                for sn in self.sqls.keys():
                    sqls = self.sqls[sn]
                    results += [self._run_sql(sql) for sql in sqls.split(";")]

            results = [res for res in results if not res.empty]
            df = results[-1] if results else None

            return df

        df = _run_sql_block(sqlname=sql_name)
        return df


def impala_query(config=None, sql=None, context=None, verbose=True):
    """Run one query sql

    :param config:
    :param sql:
    :param context:
    :param verbose:
    :return:
    """
    with ImpalaRunner(config=config, sql=sql, context=context,verbose=verbose) as runner:
        df = runner.run_sql_block()

    return df
