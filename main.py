import http.client
import configparser

import pandas as pd
import seaborn as sns
sns.set_style("dark")
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries

KEY = None

def plot_data(data, symbol=None):
    fig, ax = plt.subplots()

    colnames = ["date", "open", "high", "low", "close", "volume"]
    for colname in colnames[1:-1]:
        sns.lineplot(data=data, x="date", y=colname, label=colname, ax=ax)

    if symbol: plt.title(symbol)

    fig.set_size_inches(18.5, 10.5)
    plt.legend()
    plt.show()


def get_df_from_symbol(symbol):
    ts = TimeSeries(KEY)
    data_, meta = ts.get_daily(symbol=symbol)

    data = pd.DataFrame(data_)
    data = data.transpose()
    data.sort_index(ascending=True, inplace=True)
    data.reset_index(inplace=True)

    colnames = ["date", "open", "high", "low", "close", "volume"]
    data.columns = colnames
    data["date"] = pd.to_datetime(data["date"], format="%Y-%m-%d")
    
    for colname in colnames[1:]:
        data[colname] = pd.to_numeric(data[colname])

    return data


def main():

    config = configparser.ConfigParser()
    config.read(".config.ini")

    global KEY
    KEY = config["default"]["alpha_vantage_api_key"]

    symbol="PLTR"
    data = get_df_from_symbol(symbol)
    plot_data(data, symbol=symbol)

    


if __name__=="__main__":
    main()