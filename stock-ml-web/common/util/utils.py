import sys
import os
import time
import json
import requests
import datetime

import pandas as pd
import mysql.connector
import plotly.express as px
from alpha_vantage.timeseries import TimeSeries


# log to console
def console_log(message):
    print("[{0}] {1}".format(datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S"), message))


# read config
def get_config():
    response = requests.get(f"{os.environ.get('CONFIG_ADDRESS', 'http://0.0.0.0:5000')}/config")
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
    conn = mysql.connector.connect(
        user=os.environ.get('DATA_DB_USER', 'root'),
        password=os.environ.get('DATA_DB_PASSWORD', 'password'),
        host=os.environ.get('DATA_DB_HOST', '0.0.0.0'),
        port=os.environ.get('DATA_DB_PORT', 3306),
        database=os.environ.get('DATA_DB_DATABASE', 'stock_db')
    )

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


def get_line_fig_from_symbol(symbol):
    data = get_symbol_data_from_db(symbol)
    data = data.iloc[-5000: ]

    print(data.head())
    data = data.reset_index(drop=True)
    print(data.head())

    pred_len_rel = 0.1

    data_prediction = data.iloc[int(data.shape[0] * (1 - pred_len_rel)): , : ]
    data_prediction.columns = ['id', 'date', 'open_prediction', 'high_prediction', 'low_prediction', 'close_prediction', 'volume', 'symbol']
    data_prediction['high'] = None
    data_prediction['low'] = None
    data_prediction['open'] = None
    data_prediction['close'] = None

    data = data.iloc[ :int(data.shape[0] * (1 - pred_len_rel)), : ]
    data['high_prediction'] = None
    data['low_prediction'] = None
    data['open_prediction'] = None
    data['close_prediction'] = None

    print(data_prediction.shape)
    print(data_prediction.columns)

    print(data.shape)
    print(data.columns)

    data = data.append(data_prediction)

    data.high = data.high.astype('float64')
    data.low = data.low.astype('float64')
    data.open = data.open.astype('float64')
    data.close = data.close.astype('float64')

    print(data.shape)
    print(data.columns)

    data_len = data.shape[0]
    data_orig_len = data_len * (1 - pred_len_rel)
    
    print(data.dtypes)

    fig = px.line(data, x=data.index, y=["high", "low", "open", "close", "high_prediction", "low_prediction", "open_prediction", "close_prediction"],
        labels={
                        "date": "Date",
                        "value": "Value",
                        "variable": "Target"
                    },
                    color_discrete_sequence=["#99AFC2", "#C9DFB9", "#FBC888", "#FCB0B2", "#4D6880", "#7DB257", "#EC8609", "#F7262D",]
    )
    
    fig.add_vrect(x0=data_orig_len, x1=data_len, line_width=0, fillcolor="black", opacity=0.1)
    fig.add_vrect(x0=data_orig_len, x1=data_orig_len, line_dash="dash")

    fig.update_xaxes(rangeslider_visible=True)
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(
        height=418
    )

    return fig


if __name__=="__main__":
    print(get_symbol_information("ABNB"))
