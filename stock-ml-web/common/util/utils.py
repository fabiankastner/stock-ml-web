import sys
import time
import json
import requests
import datetime

import pandas as pd
import mysql.connector
from alpha_vantage.timeseries import TimeSeries


# log to console
def console_log(message):
    print("[{0}] {1}".format(datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S"), message))


# read config
def get_config():
    # response = requests.get("http://configservice:5000/config")
    response = requests.get("http://0.0.0.0:5000/config")
    return response.json()


# get symbol information from stock_list file
def get_symbol_information(symbol):
    config = get_config()
    stock_list_file_path = "common/bin/{0}".format(config["stock_list"]["file_name"])
    stock_list_df = pd.read_csv(stock_list_file_path, sep="|")
    symbol_info = stock_list_df[stock_list_df["Symbol"] == str.upper(symbol)].to_dict("list")
    for key in list(symbol_info.keys()): symbol_info[key] = symbol_info[key][0]
    return symbol_info


# get database connection
def get_connection():
    # conn = mysql.connector.connect(
    #     user='stock_web',
    #     password='test123',
    #     host='db',
    #     port=3306,
    #     database='stock_db')

    conn = mysql.connector.connect(
        user='root',
        password='password',
        host='localhost',
        port=3306,
        database='stock_db')

    return conn


# function to get data from db
def get_symbols():
    conn = get_connection()
    cursor = conn.cursor()
    symbols_df = pd.read_sql_query("SELECT DISTINCT symbol FROM one_min", conn)
    return symbols_df["symbol"].to_list()


def get_symbol_data_from_db(symbol):
    conn = get_connection()
    symbol_data = pd.read_sql_query("SELECT * FROM one_min WHERE symbol = '{0}'".format(symbol), conn);
    symbol_data["date"] = pd.to_datetime(symbol_data["date"], format="%Y-%m-%d %H:%M:%S")
    return symbol_data


if __name__=="__main__":
    print(get_symbol_information("ABNB"))
