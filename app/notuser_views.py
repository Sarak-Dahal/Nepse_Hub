# Views will contains all the views of file
import random
import smtplib
from app import app
from flask import render_template, request, session, redirect, url_for
import requests
import re
from bs4 import BeautifulSoup
from urllib.request import urlopen
import csv
import mysql.connector
import math
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from keras.models import model_from_json
import joblib
import plotly.express as px
from datetime import date, timedelta
from email.message import EmailMessage

# Creating a Database Connection
# Database connection
db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='sarak123',
    database='stockMarket'
)
myCursor = db.cursor()


@app.route("/")
def index():
    url = 'http://www.nepalstock.com/stocklive'
    response = requests.get('http://www.nepalstock.com/stocklive')

    if response.status_code == 200:
        html = urlopen(url).read()
        soup = BeautifulSoup(html, "html.parser")

        # Scraping values using Beautiful Soup and assigning to variable
        marketStat = soup.find('div', class_='top_marketinfo').text

        # date
        global marketDate
        marketDate = soup.find('div', id='market-watch').text.replace('\n', '').replace('As of ', '').split(' ')[0]

        # Performing Replace to take data from NEPSE easily
        nepseCurrentIndex = soup.find('div', class_='current-index').text.replace('\n', '').replace(' ', '').replace(
            ',', '')
        nepsePointChange = soup.find('div', class_='point-change').text.replace('\n', '').replace(' ', '').replace(',',
                                                                                                                   '')
        nepsePercentChange = soup.find('div', class_='percent-change').text.replace('\n', '').replace(' ', '').replace(
            ',', '').replace('%', '')
        shareVolume = soup.find('span', class_='left').text.replace('\n', '').replace(' ', '').replace(',', '').replace(
            'ShareVolume|', '')
        turnover = soup.find('span', class_='right').text.replace('\n', '').replace(' ', '').replace(',', '').replace(
            'Turnover|', '')

        # Converting Values to Float

        intCi = float(nepseCurrentIndex)
        intPc = float(nepsePointChange)
        intPcc = float(nepsePercentChange)
        intSv = float(shareVolume)
        intTo = float(turnover)

        if intPcc > 0:
            getColor = "green"
        elif intPcc == 0:
            getColor = "blue"
        else:
            getColor = "red"

        nepseIndex = str(intCi)
        if marketStat.strip() == "Market Closed":
            market = "red"
            df_market = pd.read_csv('static/modelCreation/nepseindex.csv')
            bottom = df_market['Date'][df_market.index[-1]]

            if marketDate != bottom:
                file = open('static/modelCreation/nepseindex.csv', 'a')
                file.write("\n" + marketDate + ",")
                file.write(nepseIndex)
                file.close()

        else:
            market = "green"

        # For top gainers and loosers
        df = pd.read_html('https://merolagani.com/LatestMarket.aspx')
        data = df[0].head(1000)
        del data['High']
        del data['Low']
        del data['Open']
        del data['Qty.']
        del data['Unnamed: 8']
        del data['Unnamed: 9']

        gainSort = data.sort_values(by=["% Change"], ascending=False)
        gainTab = gainSort.head(10)
        gainTab.to_csv('csvFiles/gainTab.csv', header=True, index=False)
        gain = []
        tGain = open('csvFiles/gainTab.csv')
        reader = csv.DictReader(tGain)
        for row in reader:
            gain.append(dict(row))
        finalGain = [key for key in gain[0].keys()]

        loseSort = data.sort_values(by=["% Change"], ascending=True)
        loseTab = loseSort.head(10)
        loseTab.to_csv('csvFiles/loseTab.csv', header=True, index=False)
        lose = []
        tLose = open('csvFiles/loseTab.csv')
        reader = csv.DictReader(tLose)
        for row in reader:
            lose.append(dict(row))
        finalLose = [key for key in lose[0].keys()]

        df = pd.read_csv('static/modelCreation/nepseindex.csv')
        figure = px.line(df, x='Date', y='ClosePrice', title="NEPSE LifeTime Advance Graph")
        figure.write_html("templates/nepseGraph.html")
        return render_template('notuser/index.html', intCi=intCi, intPc=intPc, intPcc=intPcc, intSv=intSv, intTo=intTo,
                               marketStat=marketStat, gain=gain, finalGain=finalGain, lose=lose, finalLose=finalLose,
                               len=len, getColor=getColor, market=market)

    else:
        return render_template('notuser/index.html')


@app.route("/graph")
def graph():
    return render_template('nepseGraph.html')


@app.route("/stockGraph")
def stockGraph():
    return render_template('stockGraph.html')

@app.route("/liveData")
def live():
    # Scraping for Today's Price Data
    df = pd.read_html('https://merolagani.com/LatestMarket.aspx')
    data = df[0].head(1000)
    del data['Unnamed: 8']
    del data['Unnamed: 9']
    data.to_csv('csvFiles/today.csv', header=True, index=False)
    result = []
    tData = open('csvFiles/today.csv')
    reader = csv.DictReader(tData)
    for row in reader:
        result.append(dict(row))
    fieldnames = [key for key in result[0].keys()]

    return render_template('notuser/liveData.html', result=result, fieldnames=fieldnames, len=len)


# Stock Prediction starts here
@app.route("/stockPrediction")
def prediction():
    return render_template('notuser/stockPrediction.html')


@app.route("/stockPrediction", methods=['POST', 'GET'])
def predict():
    cap = request.form['symbol']
    newCap = str(cap.upper())
    sym = newCap

    df = pd.read_html('https://merolagani.com/LatestMarket.aspx')
    data = df[0].head(1000)
    del data['Unnamed: 8']
    del data['Unnamed: 9']
    data.to_csv('csvFiles/today.csv', header=True, index=False)
    read = pd.read_csv("csvFiles/today.csv")
    value = read.loc[read['Symbol'] == sym]
    x = value.values.tolist()

    if x != []:
        sign = x[0][0]
        opn = x[0][6]
        high = x[0][4]
        low = x[0][5]
        ltp = x[0][1]
        ltv = x[0][2]
        change = x[0][3]
        quantity = x[0][7]

        if change > 0:
            predictColor = "green"
        elif change == 0:
            predictColor = "blue"
        else:
            predictColor = "red"

        # creating cursor object
        myCursor = db.cursor()

        # Retiriving datas from db using select and where clause
        myCursor.execute("SELECT code FROM company_codes WHERE name=%s", (sym + '\n',))
        result = myCursor.fetchall()
        # List to String for output
        symbol = ' '.join(map(str, result))
        symbol = symbol.replace('(', '').replace(',', '').replace(')', '')

        # Today Date and Time
        today = date.today()
        todaysDate = today.strftime("%Y/%m/%d")
        url = 'http://www.nepalstock.com/main/stockwiseprices/index/1/Date/asc/YTo0Ont1via1qwwkc2ssfu0sy7c6qhr8e4curh64j8vglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mNi0wNinECzXshLZA5C9odmaiEfopX5DYvwMbnM4hqCMEu0sy7c6qhr8e4curh64j8vglc0pz0mVHpH3f54XshLPMwriqLdDo49bt1via1qwwkc2ssfu0sy7c6qhr8e4curh64j8vglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mglc0pz0mcr8flGUkQ6P1erDc0pz0mcr8flu0sy7c6qhr8e4curh64j8vglc0pz0m30?startDate=2005-06-05&endDate=' + todaysDate + '&stock-symbol=' + symbol + '&_limit=10000000000'

        df = pd.read_html(url, header=1)
        data = df[0]
        data = data.iloc[:-1]
        data.to_csv('csvFiles/pastdata.csv')

        stockData = pd.read_csv("csvFiles/pastdata.csv")

        # Creating Data Frame with only Close Column
        datum = stockData.filter(['Close Price'])
        dataset = datum.values
        training_data_len = math.ceil(len(dataset) * .8)

        # Scaling the data
        scale = MinMaxScaler(feature_range=(0, 1))
        scaledData = scale.fit_transform(dataset)

        # Testing Data Set

        testData = scaledData[training_data_len - 60:, :]

        # Creating dataset x_test and y_test
        x_test, y_test = [], dataset[training_data_len:, :]

        for i in range(60, len(testData)):
            x_test.append(testData[i - 60:i, 0])

        # Converting data to numpy array
        x_test = np.array(x_test)

        # Reshaping the data
        x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], 1))

        # load json and create model
        json_file = open('model.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        # load weights into new model
        model.load_weights("model.h5")
        print("Loaded model from disk")


        # Get Predicted Value
        predict = model.predict(x_test)
        predict = scale.inverse_transform(predict)

        # Finding out RMSE lower value for actual prediction
        np.sqrt(np.mean(((predict - y_test) ** 2)))


        # Creating new df to store filtered values
        newDf = data.filter(['Close Price'])

        # Converting last 60 days values to array
        avaiData = newDf[-60:].values

        # Scaling
        avaiDataScaled = scale.transform(avaiData)

        # appending data to list then taking to array and reshaping
        X_test = []
        X_test.append(avaiDataScaled)
        X_test = np.array(X_test)
        X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

        prediction = model.predict(X_test)
        # undoing scaling
        prediction = scale.inverse_transform(prediction)
        # Next Day Prediction
        predi = prediction.item(0)


        lastThirty = stockData.filter(['Date','Close Price'])
        lastThirty.to_csv('csvFiles/lastThirtyDays.csv', header=True, index=False)
        df_market = pd.read_csv('csvFiles/lastThirtyDays.csv')
        bottom = df_market['Date'][df_market.index[-1]]


        newInput=X_test[0:].reshape(1,-1)
        temp_input = list(newInput)
        temp_input = temp_input[0].tolist()
        lst_output=[]
        n_steps = 60
        i = 0

        while (i < 30):
            if (len(temp_input) > 60):
                #print(temp_input)
                newInput = np.array(temp_input[1:])
                #print("{} day input {}".format(i, newInput))
                newInput = newInput.reshape(1, -1)
                newInput = newInput.reshape((1, n_steps, 1))
                #print(newInput)
                yhat = model.predict(newInput, verbose=0)
                newPredi = scale.inverse_transform(yhat)
                # Next Day Prediction
                predictor = newPredi.item(0)
                #print(predictor)
                #print("{} day output {}".format(i, yhat))
                temp_input.extend(yhat[0].tolist())
                temp_input = temp_input[1:]
                #print(temp_input)
                lst_output.extend(yhat.tolist())
                d = date.today() + timedelta(days=i)
                newDate=str(d)
                i = i + 1
                file = open('csvFiles/lastThirtyDays.csv', 'a')
                newP=str(predictor)
                file.write(newDate)
                file.write(","+newP+"\n")
                file.close()


            else:
                newInput = newInput.reshape((1, n_steps, 1))
                yhat = model.predict(newInput, verbose=0)
                print(yhat[0])
                temp_input.extend(yhat[0].tolist())
                print(len(temp_input))
                lst_output.extend(yhat.tolist())
                i = i + 1
        # print(lst_output)


        # Plotting to Graph
        df = pd.read_csv('csvFiles/lastThirtyDays.csv')
        figure = px.line(df, x='Date', y='Close Price', title="Past data and Next 30 days Predicted Data")
        figure.write_html("templates/stockGraph.html")

        # Suggestion
        suggest = prediction.item(0)

        if suggest > ltp:
            de = suggest / ltp
            if de >= 0.50:
                answer = "Stock shall be higher than Last Traded Price. Book your profit so Sell"

            else:
                answer = "Stock shall be lower than Last Traded Price. Buy stock or perform averaging"
        else:
            answer = "Stock are fluctuating better Hold "

        if ltp > predi:
            predictionColor = "red"
        elif ltp == predi:
            predictionColor = "blue"
        else:
            predictionColor = "green"

        index()
        dateHere = marketDate

        return render_template('notuser/stockPrediction.html', symbol=symbol, predi=predi, sign=sign, high=high,
                               low=low, opn=opn, ltp=ltp, ltv=ltv, change=change, quantity=quantity, answer=answer,
                               dateHere=dateHere, predictColor=predictColor, predictionColor=predictionColor)
    else:
        msg = "No Stock Symbol Found"
        return render_template('notuser/stockPrediction.html', msg=msg)


# Stock Prediction ends here


# Stock Averaging Routing with functions
@app.route("/stockAverager")
def tool():
    return render_template('notuser/stockAverager.html')


# Tools for average
@app.route('/averaging', methods=['POST'])
def average():
    if request.method == 'POST':
        share1 = request.form['SharesBought1']
        share2 = request.form['SharesBought2']
        share3 = request.form['SharesBought3']
        share4 = request.form['SharesBought4']
        share5 = request.form['SharesBought5']
        price1 = request.form['PurchasePrice1']
        price2 = request.form['PurchasePrice2']
        price3 = request.form['PurchasePrice3']
        price4 = request.form['PurchasePrice4']
        price5 = request.form['PurchasePrice5']

        totalShare = float(share1) + float(share2) + float(share3) + float(share4) + float(share5)
        num = float(share1) * float(price1) + float(share2) * float(price2) + float(share3) * float(price3) + float(
            share4) * float(price4) + float(share5) * float(price5)
        if num != 0 or totalShare != 0:
            calc = (num / totalShare)
        else:
            calc = 0
            totalShare = 0

    return render_template('notuser/stockAverager.html', calc=calc, totalShare=totalShare)


# Stock Averaging ends here


# Login/Signup Starts Here

global session

@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'num' in request.form and 'pass' in request.form:
        numb = request.form['num']
        passw = request.form['pass']
        myCursor.execute("Select * from register WHERE number = '" + numb + "' AND password = '" + passw + "'")
        data = myCursor.fetchone()
        if data:
            session['loggedin'] = True
            session['id'] = numb
            is_Admin = data[6]
            if is_Admin==1:
                return redirect('admin/dashboard')
            else:
                return redirect('user/home')
        else:
            msg = 'Incorrect username / password !'
    return render_template('notUser/loginSignUp.html', msg=msg)


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST' and 'username' in request.form and 'numb' in request.form and 'passw' in request.form and 'email' in request.form:
        name = request.form['username']
        email = request.form['email']
        number = request.form['numb']
        password = request.form['passw']
        myCursor.execute("Select * from register WHERE email = '" + email + "' OR number ='" + number + "'")
        account = myCursor.fetchone()
        #print(account)
        if account:
            msg = 'Account already exists ! Try Log In '
            color = "red"
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            color = "red"
        elif not re.match(r'[A-Za-z0-9]+', name):
            msg = 'Username must contain only characters and numbers !'
            color = "red"
        elif not name or not password or not email:
            msg = 'Please fill out the form here!'
            color = "red"
        else:
            admin=0
            myCursor.execute("INSERT INTO register (name,number,password,email,isAdmin) VALUES (%s,%s,%s,%s,%s)",(name, number, password, email,admin))
            db.commit()
            msg = 'You have successfully registered !'
            color="green"
    elif request.method == 'POST':
        msg = 'Please fill out the form !'

    return render_template('notUser/loginSignUp.html', msg=msg,color=color)


# Login/Signup ends Here


# Logout starts

@app.route('/logout')
def logout():
    session['loggedin'] = False
    return redirect(url_for('login'))

# Logout ends


# Password Forgot
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    msg = ''
    if request.method == 'POST' and 'email' in request.form:
        msg = ''
        email = request.form['email']
        myCursor.execute("Select * from register WHERE email = '" + email + "'")
        mail = myCursor.fetchone()
        print(mail)
        if mail:
            secret = str(random.randint(9999, 100000))
            myCursor.execute("Update register set secretcode = '" + secret + "' where email = '" + email + "'")
            db.commit()
            msg=EmailMessage()
            msg.set_content("Your reset code is: "+secret +" \n Do not share this code with anyone else. If you need additional help you may mail to nepsemaster@gmail.com")
            msg['Subject'] = 'Nepse Master Password Reset'
            msg['From'] = "nepsemaster@gmail.com"
            msg['To'] = email
            # send secret key to mail
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login("nepsemaster@gmail.com","$h!$h!r9861")
            server.send_message(msg)
            server.send
            server.quit()
            msg = 'Reset link have been sent successfully'
            color = "green"
            return render_template('notuser/resetPassword.html', msg=msg,color=color)
        elif mail==None:
            msg = 'Invalid Email address entered'
            color="red"
            return render_template('notuser/forgotPassword.html', msg=msg,color=color)

    return render_template('notuser/forgotPassword.html', msg=msg)


# Password Reset
@app.route("/reset", methods=['GET', 'POST'])
def reset():
    if request.method == 'POST' and 'code' in request.form:
        codes = request.form['code']
        newpass = request.form['newpassword']
        myCursor.execute("Select * from register WHERE secretcode = '" + codes + "'")
        verify = myCursor.fetchone()

        if verify:
            myCursor.execute("Update register set password = '" + newpass + "' where secretcode = '" + codes + "'")
            db.commit()
            msg = "Password Reset Successful! Try to Login"
            color="green"
            return render_template("notuser/loginSignUp.html", msg=msg,color=color)
        else:
            msg = 'Code does not match'
            color="red"
            return render_template("notuser/resetPassword.html", msg=msg,color=color)

    else:
        color="red"
        msg = "Enter values asked before submitting"
        return render_template("notUser/resetPassword.html", msg=msg,color=color)


#About Us
@app.route("/aboutUs")
def about():
    return render_template('aboutUs.html')


#contact Us
@app.route("/contactUs")
def contact():
    return render_template('contactUs.html')

#Help and Support
@app.route("/help")
def help():
    return render_template('help.html')