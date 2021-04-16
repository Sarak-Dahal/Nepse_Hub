import math
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense, LSTM
import joblib


nepseData = pd.read_csv("nepseindex.csv")

# Creating Data Frame with only Close Column
datum = nepseData.filter(['Close Price'])
dataset = datum.values
training_data_len = math.ceil(len(dataset) * .8)

# Scaling the data
scale = MinMaxScaler(feature_range=(0, 1))
scaledData = scale.fit_transform(dataset)

# Scaled Training Data set
trainedData = scaledData[0:training_data_len, :]

# Spliting Data in X and Y datasets
x_train = []
y_train = []
for i in range(60, len(trainedData)):
    x_train.append(trainedData[i - 60:i, 0])
    y_train.append(trainedData[i, 0])

# x_train and y_train to numpy array
x_train, y_train = np.array(x_train), np.array(y_train)

# Reshape the data
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], 1))

# Building LSTM Model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(x_train.shape[1], 1)))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dense(units=25))
model.add(Dense(units=1))

# Compiling the model
model.compile(optimizer='adam', loss='mean_squared_error')

# Training the model
model.fit(x_train, y_train, batch_size=1, epochs=1)

joblib.dump(model, '../../stockModel')
