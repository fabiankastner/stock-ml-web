# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Fabian Kastner
# 2020.12.05
# inspired by - https://www.datacamp.com/community/tutorials/lstm-python-stock-market
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

import os
import pickle
import logging
import datetime

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
logging.getLogger('tensorflow').setLevel(logging.FATAL)

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

from retrieve_data import get_df_from_symbol
from visualize_data import plot_data

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM
from tensorflow.keras.models import load_model

# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# change tensorflow log level
def set_tf_loglevel(level):
    if level >= logging.FATAL:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    if level >= logging.ERROR:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
    if level >= logging.WARNING:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
    else:
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '0'
    logging.getLogger('tensorflow').setLevel(level)


def test_1():
    data = pickle.load(open("data/PLTR--2020-12-06.pickle", "rb"))

    high_prices = data.loc[:,'high'].to_numpy()
    low_prices = data.loc[:,'low'].to_numpy()
    mid_prices = ((high_prices+low_prices)/2.0)[-6000:]

    train_data = mid_prices[:(mid_prices.shape[0]//2)]
    test_data = mid_prices[(mid_prices.shape[0]//2):]

    scaler = MinMaxScaler()
    train_data = train_data.reshape(-1,1)
    test_data = test_data.reshape(-1,1)

    smoothing_window_size = 1000
    for di in range(0, 3000, smoothing_window_size):
        scaler.fit(train_data[di:di + smoothing_window_size, :])
        train_data[di:di + smoothing_window_size, :] = scaler.transform(train_data[di:di + smoothing_window_size, :])

    # Reshape both train and test data
    train_data = train_data.reshape(-1)

    # Normalize test data
    test_data = scaler.transform(test_data).reshape(-1)

    # Now perform exponential moving average smoothing
    # So the data will have a smoother curve than the original ragged data
    EMA = 0.0
    gamma = 0.1
    for ti in range(3000):
        EMA = gamma * train_data[ti] + (1 - gamma) * EMA
        train_data[ti] = EMA

    # Used for visualization and test purposes
    all_mid_data = np.concatenate([train_data,test_data], axis=0)

    window_size = 50
    N = train_data.shape[0]
    std_avg_predictions = []
    std_avg_x = []
    mse_errors = []

    for pred_idx in range(window_size, N):

        date = data.loc[pred_idx, "date"]

        a = train_data[pred_idx - window_size:pred_idx]
        std_avg_predictions.append(np.mean(train_data[pred_idx - window_size:pred_idx]))
        mse_errors.append((std_avg_predictions[-1] - train_data[pred_idx]) ** 2)
        std_avg_x.append(date)

    print("MSE error for standard averaging: {0}".format(round(0.5 * np.mean(mse_errors), 5)))

    import matplotlib.pyplot as plt
    plt.style.use("fivethirtyeight")
    plt.figure(figsize = (18,9))
    plt.plot(range(25, train_data.shape[0] + 25), train_data, color='blue', label='True')
    plt.plot(range(window_size, N), std_avg_predictions, color='orange', label='Prediction')
    
    plt.xticks(range(0, train_data.shape[0], 150), data['date'].loc[:3000 - 1:150], rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Mid Price')
    plt.legend(fontsize=18)
    plt.show()


class DataGenerator:

    # constructor
    def __init__(self, data, num_unroll, batch_size=None):
        self._prices = data[["high", "low", "open", "close"]]
        self._prices_length = self._prices.shape[0] - num_unroll
        
        # self._volume = data["volume"]
        
        self._num_unroll = num_unroll

        if not batch_size:
            self._batch_size = self._prices_length - self._num_unroll
        else:
            self._batch_size = batch_size if batch_size <= self._prices_length - self._num_unroll else self._prices_length - self._num_unroll
        
        self._cursor = self._num_unroll
        
        self._empty = False

    # reset data
    def set_data(self, data):
        self._prices = data[["high", "low", "open", "close"]]
        self._prices_length = self._prices.shape[0] - num_unroll
        
        self._volume = data["volume"]
        
        self._batch_size = batch_size
        self._num_unroll = num_unroll
        
        self._cursor = self._num_unroll
        
        self._empty = False

    # get next batch
    def next_batch(self):
        if self._cursor >= self._prices_length: self._empty = True
        batch_X = []
        batch_y = []
        
        for i in range(self._batch_size):
            X = self._prices.iloc[self._cursor - self._num_unroll:self._cursor, :].values
            y = self._prices.iloc[self._cursor, :].values
            
            batch_X.append(X)
            batch_y.append(y)
            
            self._cursor += 1
        
        return np.asarray(batch_X), np.asarray(batch_y)

    # scale data to [0, 1]
    def scale_data(self):
        scaler = MinMaxScaler()
        self._prices = pd.DataFrame(scaler.fit_transform(self._prices), columns = self._prices.columns)
        # self._volume = pd.DataFrame(scaler.fit_transform(self._volume), columns = self._volume.columns)

    # check if empty
    def empty(self):
        return self._empty


def get_model(input_shape):
    model = Sequential()

    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dense(25))
    model.add(Dense(1))

    model.compile(optimizer="adam", loss="mean_squared_error")

    return model


def test_2(symbol):
    symbol = symbol
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    # pickle data to minimize api requests
    data = get_df_from_symbol(symbol)
    # file_name = "{0}--{1}.pickle".format(symbol, datetime.datetime.now().strftime("%Y-%m-%d"))
    # pickle.dump(data, open("data/{0}".format(file_name), "wb"))

    #data = pickle.load(open(f"data/{symbol}--{current_date}.pickle", "rb"))

    dg = DataGenerator(data, num_unroll=10)
    dg.scale_data()

    batch_X = None
    batch_y = None

    batch_X, batch_y = dg.next_batch()
    
    # print(batch_X.shape)
    # print(batch_y.shape)

    model_name = "{0}--{1}.model".format(symbol, datetime.datetime.now().strftime("%Y-%m-%d"))
    # create model
    model = get_model(input_shape=batch_X.shape[1:])

    # train model
    set_tf_loglevel(logging.INFO)
    model.fit(batch_X, batch_y, batch_size=32, epochs=3)

    # save model
    #pickle.dump(model, open("models/{0}".format(model_name), "wb"))

    # load model
    # model = load_model("models/{0}".format(model_name))


# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == "__main__":
    test_2("ABNB")