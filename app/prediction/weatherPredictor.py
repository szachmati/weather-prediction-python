import pandas as pd
import numpy as np
from keras.models import Sequential
from sklearn.preprocessing import MinMaxScaler
from datetime import date, timedelta
from keras.layers import LSTM, Dense, Dropout, Bidirectional


def predict(training_set, test_set, parameter, sc):
    x_train = []
    y_train = []
    n_future = 5  # Next 5 days forecast
    n_past = 30  # Past 30 days
    for i in range(0, len(training_set) - n_past - n_future + 1):
        x_train.append(training_set[i: i + n_past, 0])
        y_train.append(training_set[i + n_past: i + n_past + n_future, 0])

    x_train, y_train = np.array(x_train), np.array(y_train)
    x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

    EPOCHS = 50
    BATCH_SIZE = 32
    regressor = Sequential()
    regressor.add(Bidirectional(LSTM(units=30, return_sequences=True, input_shape=(x_train.shape[1], 1))))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=30, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=30, return_sequences=True))
    regressor.add(Dropout(0.2))
    regressor.add(LSTM(units=30))
    regressor.add(Dropout(0.2))
    regressor.add(Dense(units=n_future, activation='relu'))
    regressor.compile(optimizer='adam', loss='mean_squared_error', metrics=['acc'])
    regressor.fit(x_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

    x_test = test_set[: n_past, 0]
    y_test = test_set[n_past: n_past + n_future, 0]
    x_test, y_test = np.array(x_test), np.array(y_test)
    x_test = np.reshape(x_test, (1, x_test.shape[0], 1))
    predicted_temperature = regressor.predict(x_test)
    predicted_temperature = sc.inverse_transform(predicted_temperature)
    predicted_temperature = np.reshape(predicted_temperature,
                                       (predicted_temperature.shape[1], predicted_temperature.shape[0]))
    print('Predicted ' + parameter + ' {}'.format(predicted_temperature))
    print('Real temperature {}'.format(y_test))


def startProcessing(cityName, parameter) :
    data = pd.read_csv( cityName+'.csv', sep=',')

    parameter_df = data[[parameter]].astype(np.float32)
    print(parameter_df)

    train_split = 0.9
    split_idx = int(len(parameter_df) * 0.9)
    test_set = parameter_df[split_idx:].values
    training_set = parameter_df[:split_idx].values
    sc = MinMaxScaler(feature_range=(0, 1))
    training_set_scaled = sc.fit_transform(training_set)
    predict(training_set_scaled, test_set, parameter, sc)

def getEndDate():
    return date.today().strftime("%d-%b-%Y")

def getStartDate():
    return (date.today() - timedelta(days=365)).strftime("%d-%b-%Y")

def run_menu():
    print("*" * 67)
    print("-" * 22 + "5 DAYS WEATHER FORECAST" + "-" * 22)
    print(" " * 5 + " Write name of the city (e.g. Warsaw, New York, London)" + " " * 5)
    cityName = input("Enter city name: ")
    #dataCreator.retrieve_hist_data([cityName], getStartDate(), getEndDate(), 24, location_label=False, export_csv=True, store_df=True)
    print("-" * 67)
    print(" " * 5 + "Program can predict the following parameters for " + cityName + " " * 5)
    print(" " * 3 + "|tempC     |maxtempC  |mintempC|totalSnow_cm|FeelsLikeC   |")
    print(" " * 3 + "|HeatIndexC|WindChillC|humidity|pressure    |windspeedKmph|")
    parameter = input("Enter parameter name: ")
    print("-" * 67)
    print(" " * 5 + "Program now is now making forecast of " + parameter + " for next 5 days in " + cityName + " " * 5)
    startProcessing(cityName,parameter)
    print("*" * 67)


if __name__ == "__main__":
    # X is our input variables that will be used to predict y which is our output so temperature
    # the data in X needs to be converted to numeric values to simplify our process
    while True:
        option = run_menu()

