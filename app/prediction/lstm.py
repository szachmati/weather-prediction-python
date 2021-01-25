import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers import LSTM
from keras.layers import Dropout
from sklearn.preprocessing import MinMaxScaler

BATCH_SIZE = 10
TIME_STEP = 50



def prepare_data(file_name, usercols):
    raw_data = pd.read_csv(file_name, index_col='Date', squeeze=True, usecols=['Date', 'Close'], parse_dates=True)
    sc = MinMaxScaler(feature_range=(0, 1))
    return sc.fit_transform(np.array(raw_data).reshape(-1, 1))

def get_train_set(scaled_data):
    X_train = []
    y_train = []
    for i in range(TIME_STEP, len(scaled_data)):
        X_train.append(training_set_scaled[i - TIME_STEP:i, 0])
        y_train.append(scaled_data[i, 0])
    X_train, y_train = np.array([X_train]), np.array(y_train)



if __name__ == "__main__":
    cdpr_stocks = pd.read_csv('stock_price.csv',
                              index_col='Date',
                              squeeze=True,
                              usecols=['Date', 'Close'],
                              parse_dates=True)
    cdpr_stocks = cdpr_stocks.rename_axis('Date')
    cdpr_stocks = cdpr_stocks.rename('Price')

    sc = MinMaxScaler(feature_range=(0, 1))
    training_set_scaled = sc.fit_transform(np.array(cdpr_stocks["2010-01-01":"2018-12-31"]).reshape(-1, 1))

    X_train = []
    y_train = []
    for i in range(TIME_STEP, len(training_set_scaled)):
        X_train.append(training_set_scaled[i - TIME_STEP:i, 0])
        y_train.append(training_set_scaled[i, 0])
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    regressor = Sequential()
    regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    regressor.add(Dropout(rate=0.2))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(rate=0.3))
    regressor.add(LSTM(units=50, return_sequences=True))
    regressor.add(Dropout(rate=0.4))
    regressor.add(LSTM(units=50, return_sequences=False))
    regressor.add(Dropout(rate=0.5))
    regressor.add(Dense(units=1))
    regressor.compile(optimizer='adam', loss='mean_squared_error')
    regressor.fit(x=X_train, y=y_train, batch_size=BATCH_SIZE, epochs=20)

    # Optionally save the model to a file
    # regressor.save("test_mod_new")
    # load a model from a file with below function
    # regressor = load_model("test_mod_new")

    offset = len(cdpr_stocks["1/1/2019":].index)
    inputs = np.array(cdpr_stocks[-offset - TIME_STEP:]).reshape(-1, 1)
    inputs = sc.transform(inputs)
    X_test = []
    y_test = []
    for i in range(TIME_STEP, len(inputs)):
        X_test.append(inputs[i - TIME_STEP:i, 0])
        y_test.append(inputs[i, 0])
    X_test, y_test = np.array(X_test), np.array(y_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    result = regressor.evaluate(X_test, y_test)
    # print(result)

    predicted_stock_price = regressor.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    preds_ts = pd.Series(predicted_stock_price[:, 0], index=cdpr_stocks[-offset:].index)
    plt.plot(preds_ts, color='red', label='Predykcja')
    plt.plot(cdpr_stocks["1/1/2019":], label='Kurs')
    plt.legend(loc='lower right')
