import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from keras.models import Sequential, load_model
from keras.layers import Dense, LSTM, Dropout
from sklearn.preprocessing import MinMaxScaler


BATCH_SIZE = 10
TIME_STEP = 50


def prepare_data(file_name, usercols, sc):
    raw_data = pd.read_csv(file_name,
                        index_col='Date',
                        squeeze=True,
                        usecols=usercols,
                        parse_dates=True)
    return sc.fit_transform(np.array(raw_data).reshape(-1, 1))


def get_train_set(scaled_data):
    X_train = []
    Y_Train = []
    for i in range(TIME_STEP, len(scaled_data)):
        X_train.append(scaled_data[i - TIME_STEP:i, 0])
        Y_Train.append(scaled_data[i, 0])
    X_train, Y_Train = np.array(X_train), np.array(Y_Train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
    return (X_train, Y_Train)


def get_test_set(scaled_data):
    X_test = []
    y_test = []
    for i in range(TIME_STEP, len(scaled_data)):
        X_test.append(scaled_data[i-TIME_STEP:i, 0])
        y_test.append(scaled_data[i,0])
    X_test, y_test = np.array(X_test), np.array(y_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    return X_test, y_test


def train_network(x_train, y_train, eps):
    regressor = Sequential()
    regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (x_train.shape[1], 1)))
    regressor.add(Dropout(rate = 0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(rate = 0.2))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(rate = 0.3))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(rate = 0.3))
    regressor.add(LSTM(units = 50, return_sequences = True))
    regressor.add(Dropout(rate = 0.4))
    regressor.add(LSTM(units = 50, return_sequences = False))
    regressor.add(Dropout(rate = 0.2))
    regressor.add(Dense(units = 1))
    regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')
    regressor.fit(x = x_train, y = y_train, batch_size = BATCH_SIZE, epochs = eps)
    return regressor



if __name__ == "__main__":
    sc = MinMaxScaler(feature_range=(0, 1))
    data = prepare_data('stock_price_train.csv', ['Date','Close'], sc)
    X_train, y_train = get_train_set(data)
    lstm_network = train_network(X_train,y_train,5)
    lstm_network.save("asd_lstm")
    lstm_network = load_model("asd_lstm")
    test_data = prepare_data('stock_price_test.csv', ['Date','Close'], sc)
    X_test, y_test = get_test_set(test_data)
    result = lstm_network.evaluate(X_test,y_test)
    predicted_stock_price = lstm_network.predict(X_test)
    predicted_stock_price = sc.inverse_transform(predicted_stock_price)
    y = sc.inverse_transform(y_test.reshape(1, -1))
    diff = np.subtract(y, predicted_stock_price[:, 0])
    plt.scatter(list(range(1, len(diff))), diff)
    plt.show()


