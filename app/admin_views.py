from app import app, notuser_views
from flask import render_template,request
import mysql.connector
import pandas as pd

def database():
    myCursor.execute("select * from register where isAdmin=0")
    global data
    data = myCursor.fetchall()

def companyCode():
    myCursor.execute("select * from company_codes")
    global companyCodes
    companyCodes = myCursor.fetchall()

db = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='sarak123',
    database='stockMarket'
)
myCursor = db.cursor()
@app.route("/admin/dashboard")
def admin_dashboard():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        myCursor.execute("select count(isAdmin) from register where isAdmin=1")
        res = myCursor.fetchone()
        adminCount=res[0]
        myCursor.execute("select count(isAdmin) from register where isAdmin=0")
        res = myCursor.fetchone()
        userCount = res[0]
        df = pd.read_csv('csvFiles/brokers.csv')
        df1=pd.read_csv('csvFiles/company.csv')
        brokerCount=df.shape[0]
        companyCount=df1.shape[0]
        return render_template("admin/dashboard.html",brokerCount=brokerCount,adminCount=adminCount,userCount=userCount,companyCount=companyCount)

@app.route("/admin/user")
def user_management():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        database()
        return render_template("admin/user.html",data=data)

@app.route("/admin/user/delete/<num>", methods = ['POST','GET'])
def user_delete(num):
    myCursor.execute("Delete from register where userid='" + num + "'")
    db.commit()
    msg="User Deleted Successfully"
    color="green"
    database()
    return render_template("admin/user.html", msg=msg,color=color,data=data)

@app.route("/admin/user/edit/<num>", methods = ['POST','GET'])
def user_edit(num):
    myCursor.execute("Select * from register where userid='" + num + "'")
    edit = myCursor.fetchone()
    editId=edit[0]
    editName=edit[1]
    editNumber=edit[2]
    editPassword=edit[3]
    editEmail=edit[4]
    editIsAdmin=edit[6]
    return render_template("admin/update.html", editId=editId,editName=editName,editNumber=editNumber,editPassword=editPassword,editEmail=editEmail,editIsAdmin=editIsAdmin)

@app.route("/admin/companyCode/delete/<num>", methods = ['POST','GET'])
def company_delete(num):
    myCursor.execute("Delete from company_codes where code='" + num + "'")
    db.commit()
    msg="User Deleted Successfully"
    color="green"
    database()
    return render_template("admin/companyCode.html", msg=msg,color=color,data=data)


@app.route("/admin/editUser", methods = ['POST','GET'])
def user_update():
    if request.method == 'POST' and 'id' in request.form and 'name' in request.form and 'number' in request.form and 'password' in request.form and 'email' in request.form and 'isAdmin' in request.form:
        userid = request.form['id'].strip()
        name = request.form['name'].strip()
        number = request.form['number'].strip()
        password = request.form['password'].strip()
        email = request.form['email'].strip()
        admin = request.form['isAdmin'].strip()
        if admin == "0" or admin == "1":
            myCursor.execute("Select * from register WHERE userid ='"+userid+"' and number = '" + number + "' and email ='" + email + "'")
            user = myCursor.fetchall()
            if user:
                myCursor.execute(
                    "Update register set name = '" + name + "',password= '" + password + "', isAdmin= '" + admin + "' where userid='" + userid + "'")
                db.commit()
                msg = "User Updated Successfully"
                color = "green"
                database()
                return render_template("admin/user.html", msg=msg, color=color, data=data)

            else:
                myCursor.execute("Select * from register WHERE number = '" + number + "'")
                userNumber = myCursor.fetchall()

                if len(userNumber) == 0:
                    myCursor.execute(
                        "Update register set name = '" + name + "',number= '" + number + "',password= '" + password + "', email= '" + email + "', isAdmin= '" + admin + "' where userid='" + userid + "'")
                    db.commit()
                    msg = "User Updated Successfully"
                    color = "green"
                    database()
                    return render_template("admin/user.html", msg=msg, color=color, data=data)

                elif len(userNumber) == 1:
                    myCursor.execute("Select * from register WHERE email = '" + email + "'")
                    userEmail = myCursor.fetchall()

                    if len(userEmail) == 0:
                        myCursor.execute(
                            "Update register set name = '" + name + "',number= '" + number + "',password= '" + password + "', email= '" + email + "', isAdmin= '" + admin + "' where userid='" + userid + "'")
                        db.commit()
                        msg = "User Updated Successfully"
                        color = "green"
                        database()
                        return render_template("admin/user.html", msg=msg, color=color, data=data)
                    else:
                        msg = 'User already Exist with Number or Email you entered'
                        color = "red"
                        database()
                        return render_template("admin/user.html", msg=msg, color=color, data=data)

                else:
                    msg = 'User already Exist with Number or Email you entered'
                    color = "red"
                    database()
                    return render_template("admin/user.html", msg=msg, color=color, data=data)
        else:
            msg = "Please enter 0 for user and 1 for admin "
            color = "red"
            database()
            return render_template("admin/user.html", msg=msg, color=color, data=data)
    database()
    return render_template("admin/user.html",data=data)



@app.route("/admin/companyCode")
def company_code():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        companyCode()
        return render_template("admin/companyCode.html",companyCodes=companyCodes)


@app.route("/admin/createAdmin")
def create_Admin():
    if notuser_views.session['loggedin'] == False:
        msg = "You Must Login to access the Page"
        color='red'
        return render_template("notuser/loginSignUp.html",msg=msg,color=color)
    else:
        return render_template("admin/createAdmin.html")


# Add New Company
@app.route("/admin/addNewCompany", methods=['GET', 'POST'])
def addNewCompany():
    companyCode()
    if request.method == 'POST' and 'companyCode' in request.form:
        codes = request.form['companyCode']
        symbol = request.form['symbol']
        myCursor.execute("Select * from company_codes WHERE code = '" + codes + "' OR name ='" + symbol + "'")
        stock = myCursor.fetchone()
        if stock:
            msg = 'Stock Already Added'
            color = "red"

            return render_template("admin/companyCode.html", msg=msg, color=color,companyCodes=companyCodes)
        else:
            myCursor.execute("Insert into company_codes (code,name) VALUES (%s,%s)",(codes,symbol))
            db.commit()
            msg="Company Added Successfully"
            color="green"
            return render_template("admin/companyCode.html", msg=msg,color=color,companyCodes=companyCodes)

    return render_template("admin/companyCode.html",companyCodes=companyCodes)


# Add New User
@app.route("/admin/addNewUser", methods=['GET', 'POST'])
def addNewUser():
    if request.method == 'POST' and 'name' in request.form and 'number' in request.form and 'password' in request.form and 'email' in request.form and 'isAdmin' in request.form:
        name = request.form['name']
        number = request.form['number']
        password = request.form['password']
        email = request.form['email']
        admin= request.form['isAdmin']
        if admin =="0" or admin =="1":
            myCursor.execute("Select * from register WHERE email = '" + email + "' OR number ='" + number + "'")
            user = myCursor.fetchone()
            if user:
                msg = 'User Already Registered'
                color = "red"
                database()
                return render_template("admin/user.html", msg=msg, color=color, data=data)
            else:
                myCursor.execute("INSERT INTO register (name,number,password,email,isAdmin) VALUES (%s,%s,%s,%s,%s)",
                                 (name, number, password, email, admin))
                db.commit()
                msg = "User Added Successfully"
                color = "green"
                database()
                return render_template("admin/user.html", msg=msg, color=color, data=data)
        else:
            msg = "Please enter 0 for user and 1 for admin "
            color = "red"
            database()
            return render_template("admin/user.html", msg=msg, color=color, data=data)
    database()
    return render_template("admin/user.html",data=data)


# Add New Admin
@app.route("/addNewAdmin", methods=['GET', 'POST'])
def addNewAdmin():
    if request.method == 'POST' and 'name' in request.form and 'number' in request.form and 'password' in request.form and 'email' in request.form:
        name = request.form['name']
        number = request.form['number']
        password = request.form['password']
        email = request.form['email']
        admin=1
        myCursor.execute("Select * from register WHERE email = '" + email + "' OR number ='" + number + "'")
        user = myCursor.fetchone()
        if user:
            msg = 'Admin Already Registered'
            color = "red"
            return render_template("admin/createAdmin.html", msg=msg, color=color)
        else:
            myCursor.execute("INSERT INTO register (name,number,password,email,isAdmin) VALUES (%s,%s,%s,%s,%s)",(name, number, password, email,admin))
            db.commit()
            msg="Admin Added Successfully"
            color="green"
            return render_template("admin/createAdmin.html", msg=msg,color=color)

    return render_template("admin/createAdmin.html")


