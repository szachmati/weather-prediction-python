import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from keras.models import Sequential
from keras.layers import *
from sklearn.preprocessing import MinMaxScaler
import time
from datetime import date, timedelta
from .dataCreator import DataCreator


def predict(city, condition):
    data_creator = DataCreator()
    # data_creator.retrieve_hist_data([city], getStartDate(), getEndDate(), 24, location_label=False, export_csv=True,store_df=True)

    # Tworzony jest objekt Dataframe z zawartością danych historycznych ze wskazanego miasta
    df = pd.read_csv(city + '.csv', sep=',')

    kol_od = data_creator.setColumnX(condition)
    kol_do = data_creator.setColumnY(condition)
    df.head(5)
    # pobierany jest index, który umożliwi podział danych
    split_idx = int(len(df) * 0.9)
    # w celu trenowania modelu pobierane jest 90% danych
    training_set = df.iloc[:split_idx, kol_od:kol_do].values

    # wartości ze zbioru skalowane są tak aby wpasować się w zakres między 0 a 1
    sc = MinMaxScaler(feature_range=(0, 1))
    training_set_scaled = sc.fit_transform(training_set)

    X_train = []
    y_train = []

    # Z danych treningowych zostają wydzielone próbki o wielkości 60
    for i in range(60, split_idx):
        X_train.append(training_set_scaled[i - 60:i, 0])
        y_train.append(training_set_scaled[i, 0])
    # =========================================================
    X_train, y_train = np.array(X_train), np.array(y_train)
    X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

    # Wskazywana jest ilość epok (EPOCHS) oraz rozmiar porcji danych (BATCH_SIZE)
    EPOCHS = 1
    BATCH_SIZE = 5
    # Do stworzenia modelu wykorzystywana jest klasa Sequential
    model = Sequential()
    # Dodajemy 1 warstwę
    model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
    model.add(Dropout(0.2))
    # Dodajemy 2 warstwę
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    # Dodajemy 3 warstwę
    model.add(LSTM(units=50, return_sequences=True))
    model.add(Dropout(0.2))
    # Dodajemy 4 warstwę
    model.add(LSTM(units=50))
    model.add(Dropout(0.2))
    # Dodajemy warstwę wyjścia, która zwraca jeden neuron
    model.add(Dense(units=1))
    # W celach analitycznych odmierzany jest czas wykonywania predykcji
    start = time.time()
    # Następuje kompilacja modelu z wykorzystaniem algorytmu optymalizującego Adam.
    model.compile(optimizer='adam', loss='mean_squared_error')
    # Program wywołuje trenowanie modelu. Wskazywana jest ilość epok (EPOCHS) oraz rozmiar porcji danych (BATCH_SIZE)
    model.fit(X_train, y_train, epochs=EPOCHS, batch_size=BATCH_SIZE)

    # Następnie przygotowywany są dane do testowania
    X_test = []
    dataset_train = df.iloc[:split_idx, kol_od:kol_do]
    dataset_test = df.iloc[split_idx:, kol_od:kol_do]
    dataset_total = pd.concat((dataset_train, dataset_test), axis=0)
    inputs = dataset_total[len(dataset_total) - len(dataset_test) - 60:].values
    inputs = inputs.reshape(-1, 1)
    inputs = sc.transform(inputs)

    for i in range(60, len(inputs)):
        X_test.append(inputs[i - 60:i, 0])
    X_test = np.array(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

    print(X_test.shape)

    # Do modelu zostaje przekazany zbiór testowy
    predicted_param = model.predict(X_test)
    # Wynik przewidywania zostaje spowrotem przeskalowany
    predicted_param = sc.inverse_transform(predicted_param)
    # Czas przestaje być odmierzany tuż po skalowaniu
    # tak tworzenie wykresu nie miało wpływu na wynik
    end = time.time()
    elapsed = end - start

    # Zostaje utworzont wykres zestawiający przewidziane parametry z prawdziwymi wartościami
    plt.plot(df.loc[split_idx:, 'date_time'], dataset_test.values, color='black', label='Real ' + condition)
    plt.plot(df.loc[split_idx:, 'date_time'], predicted_param, color='orange', label='Predicted ' + condition)

    plt.xticks(np.arange(0, len(dataset_test.values), 5), rotation='vertical')
    plt.title(' Prediction EPOCHS = ' + str(EPOCHS) + ' BATCH_SIZE = ' + str(BATCH_SIZE) + ' INPUT_DATA = ' + str(
        len(df)) + ' CALCULATION TIME: ' + str(round(elapsed, 4)) + 's')
    plt.xlabel('Time')
    plt.ylabel('parameters')
    plt.legend()
    plt.show()
    return predicted_param

def getEndDate():
    return date.today().strftime("%d-%b-%Y")


def getStartDate():
    return (date.today() - timedelta(days=729)).strftime("%d-%b-%Y")
