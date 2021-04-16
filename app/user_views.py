#Views will contains all the views of file
import csv
from app import app,notuser_views
from flask import render_template
import pandas as pd

@app.route("/user/home")
def dashboard():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        df = pd.read_csv('csvFiles/gainTab.csv')
        gain=df['Symbol'].iloc[0]
        df = pd.read_csv('csvFiles/loseTab.csv')
        lose = df['Symbol'].iloc[0]

        df = pd.read_html('https://merolagani.com/LatestMarket.aspx')
        data = df[0].head(1000)
        del data['Unnamed: 8']
        del data['Unnamed: 9']
        transaction = data.sort_values(by=["Qty."], ascending=False)
        highestT = transaction.head(20)
        highestT.to_csv('csvFiles/highestT.csv', header=True, index=False)
        tran = []
        hTran = open('csvFiles/highestT.csv')
        reader = csv.DictReader(hTran)
        for row in reader:
            tran.append(dict(row))
        finalTran = [key for key in tran[0].keys()]
        df = pd.read_csv('csvFiles/highestT.csv')
        highestTrans = df['Symbol'].iloc[0]
        return render_template("user/dashboard.html",gain=gain,tran=tran,lose=lose,finalTran=finalTran,len=len,highestTrans=highestTrans)



@app.route("/user/company")
def company():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        result = []
        tData = open('csvFiles/listedCompany.csv',encoding='utf-8-sig')
        reader = csv.DictReader(tData)
        for row in reader:
            result.append(dict(row))
        fieldnames = [key for key in result[0].keys()]

        return render_template('user/company.html', result=result, fieldnames=fieldnames, len=len)

@app.route("/user/brokers")
def brokers():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        result = []
        tData = open('csvFiles/brokers.csv',encoding='utf-8-sig')
        reader = csv.DictReader(tData)
        for row in reader:
            result.append(dict(row))
        fieldnames = [key for key in result[0].keys()]

        return render_template('user/brokers.html', result=result, fieldnames=fieldnames, len=len)


@app.route("/model")
def model():
    import math
    import numpy as np
    import pandas as pd
    from sklearn.preprocessing import MinMaxScaler
    from keras.models import Sequential
    from keras.layers import Dense, LSTM
    import joblib

    nepseData = pd.read_csv("static/modelCreation/nepseindex.csv")

    # Creating Data Frame with only Close Column
    datum = nepseData.filter(['ClosePrice'])
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

    joblib.dump(model, 'stockModel')
    return render_template('notUser/stockPrediction.html')