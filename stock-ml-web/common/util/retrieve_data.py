# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fabian Kastner
# 2020.12.05
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import http.client
import configparser
import sqlite3
import time
import sys
import datetime

import pandas as pd
import mysql.connector
from alpha_vantage.timeseries import TimeSeries

from common.util.utils import get_config, console_log
# from utils import get_config

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def spinning_cursor():
    while True:
        for cursor in "⠁⠂⠄⡀⢀⠠⠐⠈":
            yield cursor


def get_connection():
    conn = mysql.connector.connect(user='stock_web', password='test123',
                            host='db', port=3306,
                            database='stock_db')
    return conn


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


def get_df_from_symbol(symbol, interval="1min"):

    config = get_config()
    key = config["keys"]["alpha_vantage_api"]

    ts = TimeSeries(key)
    # see link for api request documentation - https://www.alphavantage.co/documentation/
    data_, meta = ts.get_intraday(symbol=symbol, interval=interval, outputsize="full")

    data = pd.DataFrame(data_)
    data = data.transpose()
    data.sort_index(ascending=True, inplace=True)
    data.reset_index(inplace=True)

    colnames = ["date", "open", "high", "low", "close", "volume"]
    data.columns = colnames
    data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d %H:%M:%S")
    
    for colname in colnames[1:]:
        data[colname] = pd.to_numeric(data[colname])

    return data


def load_data():
    config = get_config()

    key = config["keys"]["alpha_vantage_api"]
    stock_list_file_path= "common/bin/{0}".format(config["stock_list"]["file_name"])

    # http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
    stock_list_df = pd.read_csv(stock_list_file_path, sep="|")

    interval = "1min"

    time.sleep(1)
    print()
    # conn = sqlite3.connect('stock_data.db')

    connection_established = False
    conn = None

    while(not connection_established):
        try:
            conn = get_connection()
            connection_established = True
        except Exception as e:
            print(str(e))
            console_log("No Database Connection Available - retrying in 5 minutes")
            time.sleep(300)

    console_log("Database Connection Established - Fetching Data")

    cursor = conn.cursor()

    # cursor.execute("""DROP TABLE IF EXISTS one_min;""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS one_min (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            date VARCHAR(19), 
            open DOUBLE(8, 3), 
            high DOUBLE(8, 3), 
            low DOUBLE(8, 3), 
            close DOUBLE(8, 3), 
            volume INT, 
            symbol VARCHAR(5));"""
    )

    # data = pd.read_sql_query("SELECT * FROM one_min;", conn)
    # print(data.shape)

    # limit = 150
    batch_from = 0

    for index, row in stock_list_df.iterrows():
        # if index >= limit: break

        success = False

        symbol = row["Symbol"]

        latest_date_datetime = pd.to_datetime("1970-01-01 00:00:00", format="%Y-%m-%d %H:%M:%S")

        latest_date_df = pd.read_sql_query("SELECT * FROM one_min WHERE symbol = '{0}' ORDER BY date DESC LIMIT 1".format(symbol), conn);
           
        if not latest_date_df.empty:
            latest_date_datetime = pd.to_datetime(latest_date_df['date'][0], format="%Y-%m-%d %H:%M:%S")
        
        days_since_last_update = (datetime.datetime.now() - latest_date_datetime).days

        if days_since_last_update >= 5:

            console_log("Updating {}".format(symbol))
            while not success:
                try:
                    data = get_df_from_symbol(symbol)

                    data = data[data['date'] > latest_date_datetime]
                    data["symbol"] = symbol
                    data["date"] = data["date"].dt.strftime("%Y-%m-%d %H:%M:%S")

                    data_list = list(data.itertuples(index=False, name=None))

                    # cursor.executemany("INSERT INTO one_min (date, open, high, low, close, volume, symbol) VALUES (?, ?, ?, ?, ?, ?, ?)", data_list)
                    sql = "INSERT INTO one_min (date, open, high, low, close, volume, symbol) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    
                    for val in data_list:
                        cursor.execute(sql, val)
                    
                    conn.commit()
                    success = True

                # reached api call frequency limit
                except ValueError as e:
                    console_log("({0}-{1}/{2}) up-to-date".format(str(batch_from + 1), str(index), str(stock_list_df.shape[0])))
                    batch_from = index

                    # spinner = spinning_cursor()
                    for _ in range(600):
                        # sys.stdout.write(next(spinner))
                        # sys.stdout.flush()
                        time.sleep(0.1)
                        # sys.stdout.write('\b')

    conn.close()



if __name__ == "__main__":
    load_data()
    # print(get_symbols())

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
