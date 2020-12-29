# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fabian Kastner
# 2020.12.05
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import http.client
import configparser
import sqlite3
import datetime
import time
import sys

import mysql.connector

import pandas as pd
from alpha_vantage.timeseries import TimeSeries

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def spinning_cursor():
    while True:
        for cursor in "⠁⠂⠄⡀⢀⠠⠐⠈":
            yield cursor


def console_log(message):
    print("[{0}] [{1}]".format(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), message))


def get_df_from_symbol(symbol, key, interval):
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
    config = configparser.ConfigParser()
    config.read(".config.ini")

    key = config["keys"]["alpha_vantage_api"]
    stock_list_file_path= config["stock_list"]["file_name"]

    # http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
    stock_list_df = pd.read_csv(stock_list_file_path, sep="|")

    interval = "1min"

    # conn = sqlite3.connect('stock_data.db')
    conn = mysql.connector.connect(user='root', password='password',
                            host='127.0.0.1', port=3306,
                            database='stock_db')
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

    data = pd.read_sql_query("SELECT * FROM one_min;", conn)

    print(data.shape)

    """ limit = 100
    batch_from = 0

    for index, row in stock_list_df.iterrows():
        if index >= limit: break

        success = False

        symbol = row["Symbol"]

        latest_date_datetime = pd.to_datetime("1970-01-01 00:00:00", format="%Y-%m-%d %H:%M:%S")

        latest_date_df = pd.read_sql_query("SELECT * FROM one_min WHERE symbol = '{0}' ORDER BY date DESC LIMIT 1".format(symbol), conn);
           
        if not latest_date_df.empty:
            latest_date_datetime = pd.to_datetime(latest_date_df['date'][0], format="%Y-%m-%d %H:%M:%S")
        
        days_since_last_update = (datetime.datetime.now() - latest_date_datetime).days

        if days_since_last_update >= 5:

            print("Updating {}".format(symbol))
            while not success:
                try:
                    data = get_df_from_symbol(symbol, key, interval)

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
                    console_log("({0}-{1}/{2}) up-to-date".format(str(batch_from + 1), str(index), str(limit)))
                    batch_from = index

                    spinner = spinning_cursor()
                    for _ in range(600):
                        sys.stdout.write(next(spinner))
                        sys.stdout.flush()
                        time.sleep(0.1)
                        sys.stdout.write('\b')

    conn.close() """



if __name__ == "__main__":
    load_data()
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
