import http.client

import pandas as pd
import seaborn as sns
sns.set_style("dark")

import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries


KEY = "cb53b74ad7mshd96157672a5da7fp171cd0jsnfae25e94c672"


def plot_data(data, symbol=None):
    fig, ax = plt.subplots()

    colnames = ["date", "open", "high", "low", "close", "volume"]
    for colname in colnames[1:-1]:
        sns.lineplot(data=data, x="date", y=colname, label=colname, ax=ax)

    if symbol: plt.title(symbol)
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

    symbol="PLTR"
    data = get_df_from_symbol(symbol)
    plot_data(data, symbol=symbol)

    


if __name__=="__main__":
    main()