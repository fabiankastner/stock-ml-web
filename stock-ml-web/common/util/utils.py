import configparser
import pandas as pd
import datetime


def console_log(message):
    print("[{0}] {1}".format(datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S"), message))


def get_config():
    config = configparser.ConfigParser()
    config.read("common/bin/config.ini")
    return config


def get_symbol_information(symbol):
    config = get_config()
    stock_list_file_path = "common/bin/{0}".format(config["stock_list"]["file_name"])
    stock_list_df = pd.read_csv(stock_list_file_path, sep="|")
    symbol_info = stock_list_df[stock_list_df["Symbol"] == str.upper(symbol)].to_dict("list")
    for key in list(symbol_info.keys()): symbol_info[key] = symbol_info[key][0]
    return symbol_info


if __name__=="__main__":
    print(get_symbol_information("ABNB"))