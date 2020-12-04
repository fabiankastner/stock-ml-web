import http.client

import pandas as pd
import seaborn as sns
sns.set_style("dark")

import matplotlib.pyplot as plt
from alpha_vantage.timeseries import TimeSeries


def main():
    key = "cb53b74ad7mshd96157672a5da7fp171cd0jsnfae25e94c672"

    symbol="AAPL"

    ts = TimeSeries(key)
    aapl, meta = ts.get_daily(symbol=symbol)

    df = pd.DataFrame(aapl)
    df = df.transpose()

    df.sort_index(ascending=True, inplace=True)
    df.reset_index(inplace=True)

    df.columns = ["date", "open", "high", "low", "close", "volume"]

    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    
    df["open"] = pd.to_numeric(df["open"])
    df["high"] = pd.to_numeric(df["high"])
    df["low"] = pd.to_numeric(df["low"])
    df["close"] = pd.to_numeric(df["close"])
    df["volume"] = pd.to_numeric(df["volume"])

    fig, ax = plt.subplots()

    sns.lineplot(data=df, x="date", y="open", label="open", ax=ax)
    sns.lineplot(data=df, x="date", y="high", label="high", ax=ax)
    sns.lineplot(data=df, x="date", y="low", label="low", ax=ax)
    sns.lineplot(data=df, x="date", y="close", label="volume", ax=ax)

    plt.title(symbol)
    plt.legend()

    plt.show()


if __name__=="__main__":
    main()