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

from tqdm import tqdm
import pandas as pd
from alpha_vantage.timeseries import TimeSeries

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------


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
    config.read(f"../.config.ini")

    key = config["keys"]["alpha_vantage_api"]
    stock_list_file_path= "../{0}".format(config["stock_list"]["file_name"])

    # http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs
    stock_list_df = pd.read_csv(stock_list_file_path, sep="|")

    interval = "1min"

    conn = sqlite3.connect('stock_data.db')

    cursor = conn.cursor()


    # cursor.execute('''CREATE TABLE one_min (symbol text, date text, open real, high real, low real, close real, volume int)''')
    # conn.commit()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    # print(cursor.fetchall())
    # cursor.execute("SELECT * FROM one_min")
    # print(cursor.fetchall())


    limit = 3

    for index, row in tqdm(stock_list_df.iterrows()):
        if index >= limit: break

        symbol = row["Symbol"]

        latest_date_datetime = pd.to_datetime("1970-01-01 00:00:00", format="%Y-%m-%d %H:%M:%S")

        latest_date_df = pd.read_sql_query("SELECT date FROM one_min WHERE symbol == '{0}' ORDER BY date DESC LIMIT 1".format(symbol), conn);
           
        if not latest_date_df.empty:
            latest_date_datetime = pd.to_datetime(latest_date_df['date'][0], format="%Y-%m-%d %H:%M:%S")
        
        if (datetime.datetime.now() - latest_date_datetime).days >= 3:
            data = get_df_from_symbol(symbol, key, interval)
            data = data[data['date'] > latest_date_datetime]
            data["symbol"] = symbol
            data.to_sql("one_min", conn, if_exists="replace")

    conn.commit()
    conn.close()



if __name__ == "__main__":
    load_data()
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
