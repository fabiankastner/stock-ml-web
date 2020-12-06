# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fabian Kastner
# 2020.12.05
# inspired by - https://www.datacamp.com/community/tutorials/lstm-python-stock-market
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import os
import pickle

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from modules.retrieve_data import get_df_from_symbol
from modules.visualize_data import plot_data

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_1():
    symbol = "PLTR"
    
    # pickle data to minimize api requests
    # data = get_df_from_symbol(symbol)
    # pickle.dump(data, open("data/data.pickle", "wb"))
    
    data = pickle.load(open("data/data.pickle", "rb"))

    # plot_data(data)
    
    high_prices = data.loc[:,'high'].to_numpy()
    low_prices = data.loc[:,'low'].to_numpy()
    mid_prices = ((high_prices+low_prices)/2.0)[-6000:]

    print(mid_prices.shape)

    train_data = mid_prices[:(mid_prices.shape[0]//2)]
    test_data = mid_prices[(mid_prices.shape[0]//2):]

    scaler = MinMaxScaler()
    train_data = train_data.reshape(-1,1)
    test_data = test_data.reshape(-1,1)

    smoothing_window_size = 1000
    for di in range(0, 3000, smoothing_window_size):
        scaler.fit(train_data[di:di+smoothing_window_size,:])
        train_data[di:di+smoothing_window_size,:] = scaler.transform(train_data[di:di+smoothing_window_size,:])


    # Reshape both train and test data
    train_data = train_data.reshape(-1)

    # Normalize test data
    test_data = scaler.transform(test_data).reshape(-1)

    a = 5
    
    # Now perform exponential moving average smoothing
    # So the data will have a smoother curve than the original ragged data
    EMA = 0.0
    gamma = 0.1
    for ti in range(3000):
        EMA = gamma*train_data[ti] + (1-gamma)*EMA
        train_data[ti] = EMA

    import matplotlib.pyplot as plt
    plt.plot(train_data)
    plt.show()

    # Used for visualization and test purposes
    all_mid_data = np.concatenate([train_data,test_data],axis=0)

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
