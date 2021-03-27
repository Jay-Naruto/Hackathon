from random import randint
from math import sin, cos, sqrt, atan2, radians
import params as params
import pyrebase
from flask import Flask, render_template, request, flash
import smtplib
import urllib
import requests, time
from tabulate import tabulate

import os

app = Flask(__name__, template_folder='templates')

firebaseConfig = {
    'apiKey': "AIzaSyB-WcwxaE7oUbkjCjzeoSU30w5GR1DwNEY",
    'authDomain': "hackathon-fcd00.firebaseapp.com",
    'databaseURL': "https://hackathon-fcd00-default-rtdb.firebaseio.com/",
    'projectId': "hackathon-fcd00",
    'storageBucket': "hackathon-fcd00.appspot.com",
    'messagingSenderId': "551820546736",
    'appId': "1:551820546736:web:6a2f59b91f396212a7e175",
    'measurementId': "G-QZ23EDYLFF"
}

firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()
authe = firebase.auth()
var = randint(100000, 999999)
email_first = ""
mobile = ""
mobilem = ""


def get_msg(msg, rec):
    rec = str(rec)
    url = "https://www.fast2sms.com/dev/bulk"
    payload = f"sender_id=FSTSMS&message={msg}&language=english&route=p&numbers={rec}"
    headers = {
        'authorization': "XOUhrtuT7xvfm8YiAc3qbQ4PeZg0NDjzSFLopKw51RWnkC9aJISzjBidwZu7a3W5JmQkcn8hXpyLfx9H",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)


def get_lat_lon(address):
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    return response[0]["lat"], response[0]["lon"]


def get_distance(lat1, lon1, lat2, lon2):
    R = 6373.0
    latr = radians(lat1)
    lonr = radians(lon1)
    laty = radians(lat2)
    lony = radians(lon2)
    dlon = lony - lonr
    dlat = laty - latr
    a = sin(dlat / 2) ** 2 + cos(latr) * cos(laty) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance


def mail_func(rec, msg):
    sender = "khoj.alerts@gmail.com"
    password = "Khoj@123"
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender, password)
    server.sendmail(sender, rec, msg)
    print("done")


@app.route("/", methods=['GET', 'POST'])
def print0():
    return render_template("index.html")


@app.route("/login", methods=['GET', 'POST'])
def print1():

    if request.method == 'POST':
        email_t = request.form.get('loginemail')
        password_t = request.form.get('loginpass')
        lst2 = []
        try:

            isha = authe.sign_in_with_email_and_password(email_t, password_t)
            # authe.send_email_verification(user['idToken'])
            users = db.child('Users').order_by_child('Email').equal_to(email_t).get()
            for user in users.each():
                fullname_s = user.val()['FullName']
                Email_s = user.val()['Email']
                Mobile_s = user.val()['Mobile']
                Password_s = user.val()['Password']

            return render_template('index2.html', params=params, fullname_s=fullname_s, Email_s=Email_s,Mobile_s=Mobile_s)
        except:
            return render_template('login.html', params=params)

    return render_template("login.html")


@app.route("/first", methods=['GET', 'POST'])
def print2():
    if request.method == 'POST':
        try:
            global email_first
            mail_func(request.form.get('Verify'), str(var))
            email_first = str(request.form.get('Verify'))
            return render_template('OTP.html', params=params)
        except:
            return render_template('First.html', params=params)
    return render_template('First.html', params=params)


@app.route("/otp", methods=['GET', 'POST'])
def print3():
    if request.method == 'POST':
        if request.form.get('OTP') == str(var):
            return render_template('signup.html', params=params)
    return render_template('OTP.html', params=params)


@app.route("/signup", methods=['GET', 'POST'])
def print4():
    if request.method == 'POST':

        PA = request.form.get('Confirm')
        try:
            xd = authe.create_user_with_email_and_password(email_first, PA)
            print(xd)

            # return render_template('index.html', params=params)

            data3 = {
                "FullName": request.form.get('FullName'),
                "Email": email_first,
                "Mobile": request.form.get('Mobile'), "Password": request.form.get('Confirm'),
            }
            db.child("Users").child(str(request.form.get('Mobile'))).set(data3)
        except:
            return render_template('signup.html', params=params)
    return render_template('signup.html', params=params)


@app.route("/mechanic", methods=['GET', 'POST'])
def print5():
    if request.method == 'POST':
        lst = []

        data3 = {
            "FullName": request.form.get('fnameuser'),
            "Mobile": request.form.get('MobileNouser'),
            "Vehicle": request.form.get('Vehicleuser'),
            "Lift": request.form.get('Liftuser'),
            "Address": request.form.get('Addressuser'),
        }
        print(data3)
        print(request.form.get('MobileNouser'))
        db.child("Services").child(str(request.form.get('MobileNouser'))).set(data3)

        latr, lonr = get_lat_lon(str(request.form.get('Addressuser')))
        users_r = db.child('Mechanics').order_by_child('Email').get()
        for user in users_r.each():

            toappend = get_distance(float(latr), float(lonr), float(user.val()["Lat"]), float(user.val()['Lon']))

            if toappend < 50:
                rate = toappend * 10
                rate = "{:.2f}".format(round(rate, 2))
                toappend = "{:.2f}".format(round(toappend, 2))
                lst.append({"Distance": toappend, "Email": user.val()['Email'], "FullName": user.val()['FullName'],
                            "Mobile": user.val()['Mobile'], "Address": user.val()['Address'],
                            "Shop": user.val()['Shop Name'], "Rate": rate})
        variable = (tabulate(lst, tablefmt='html'))
        return render_template("Display.html", lst=lst)
    return render_template("Mechanic.html")


@app.route("/cp", methods=['GET', 'POST'])
def print6():
    if request.method == 'POST':
        data3 = {
            "FullName": request.form.get('fnamepart'),
            "Mobile": request.form.get('MobileNopart'),
            "Vehicle type": request.form.get('Type'),
            "Vehicle name": request.form.get('Vehiclename'),
            "Engine Qty": request.form.get('checkpart1'),
            "Tyre Qty": request.form.get('checkpart2'),
            "Transmission Qty": request.form.get('checkpart3'),
            "Suspensions Qty": request.form.get('checkpart4'),
            "Brakes Qty": request.form.get('checkpart5'),
            "Address": request.form.get('Addresspart'),
        }
        db.child("CarParts").child(str(request.form.get('MobileNopart'))).set(data3)

        msg = f"Hello! {request.form.get('fnamepart')} is in need of assistance.\nThey require:\n{request.form.get('checkpart1')}:Engines\n" \
              f"{request.form.get('checkpart2')}:Tyres\n{request.form.get('checkpart3')}:Transmission\n" \
              f"{request.form.get('checkpart4')}:Suspensions\n{request.form.get('checkpart5')}:Brakes\n{request.form.get('fnamepart')} has the following vehicle:{request.form.get('fnamepart')}" \
              f"\nPlease contact the following number: {request.form.get('MobileNopart')}"

        users = db.child('Mechanics').order_by_child('Email').get()
        # for user in users.each():
        #     try:
        #       get_msg(msg,user.val()['Mobile'])
        #     except:
        #         print("Nahi jhala")

    return render_template("CarParts.html")


@app.route("/login2", methods=['GET', 'POST'])
def print7():
    if request.method == 'POST':
        email_t = request.form.get('loginemail2')
        password_t = request.form.get('loginpass2')

        try:

            isha = authe.sign_in_with_email_and_password(email_t, password_t)
            # authe.send_email_verification(user['idToken'])
            users = db.child('Mechanics').order_by_child('Email').equal_to(email_t).get()
            for user in users.each():
                fullname_m = user.val()['FullName']
                Email_m = user.val()['Email']
                Mobile_m = user.val()['Mobile']
                Address_m = user.val()['Address']
                Shop_m = user.val()['Shop Name']

            return render_template('index3.html', params=params, data3=fullname_m, data4=Email_m, data5=Mobile_m,
                                   data6=Address_m, data7=Shop_m)

        except:
            return render_template('LoginMech.html', params=params)
    return render_template("LoginMech.html")


@app.route("/mechsignup", methods=['GET', 'POST'])
def print8():
    if request.method == 'POST':
        email_t = request.form.get('loginemail')
        password_t = request.form.get('loginpass')

        PA = request.form.get('ConfirmM')
        try:
            xd = authe.create_user_with_email_and_password(request.form.get('EmailM'), PA)
            print(xd)

            # return render_template('index.html', params=params)
            try:
                lat, lon = get_lat_lon(request.form.get('AddressM'))
            except:
                lat, lon = 0, 0
            data3 = {
                "FullName": request.form.get('FullNameM'),
                "Email": request.form.get('EmailM'),
                "Mobile": request.form.get('MobileM'),
                "Password": request.form.get('ConfirmM'),
                "Shop Name": request.form.get('Shop'),
                "Address": request.form.get('AddressM'),
                "Lat": lat,
                "Lon": lon,

            }
            db.child("Mechanics").child(str(request.form.get('MobileM'))).set(data3)
        except:
            return render_template('Mechsignup.html', params=params)
    return render_template('Mechsignup.html', params=params)


@app.route("/mechprofile", methods=['GET', 'POST'])
def print9():
    return render_template("index3.html")


@app.route("/display", methods=['GET', 'POST'])
def print10():
    return render_template("Display.html")


@app.route("/index", methods=['GET', 'POST'])
def print11():
    if request.method == 'POST':
        fname = request.form.get('fname')
        email_index = request.form.get('email')
        mobile_index = request.form.get('MobileNo')
        Desc = request.form.get('Description')
        msg = f"{fname} has sent a feedback\n{Desc}"
        mail_func("Khoj.alerts@gmail.com", msg)
        return render_template("index.html")
    return render_template("index.html")


if __name__ == "__main__":
    app.secret_key = 'some secret key'
    app.run(debug=True)
