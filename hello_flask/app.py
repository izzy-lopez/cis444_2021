from flask import Flask,render_template,request

import datetime
import pytz

app = Flask(__name__)


USER_PASSWORDS = { "cjardin": "strong password"}

IMGS_URL = {
            "DEV" : "/static",
            "INT" : "https://cis-444-fall-2021.s3.us-west-2.amazonaws.com/images",
            "PRD" : "http://d2cbuxq67vowa3.cloudfront.net/images"
            }

CUR_ENV = "DEV"

@app.route('/') #endpoint
def index():
    return 'Web App with Python Caprice!' + USER_PASSWORDS['cjardin']

@app.route('/buy') #endpoint
def buy():
    return 'Buy'

@app.route('/hello') #endpoint
def hello():
    return render_template('hello.html',img_url=IMGS_URL[CUR_ENV] ) 

@app.route('/back',  methods=['GET']) #endpoint
def back():
    return render_template('backatu.html',input_from_browser=request.args.get('usay', default = "nothing", type = str) )

@app.route('/backp',  methods=['POST']) #endpoint
def backp():
    return render_template('backatu.html',input_from_browser= str(request.form) )


#Assigment 2
@app.route('/ss1') #endpoint
def ss1():
    return render_template('server_time.html', server_time= str(datetime.datetime.now()) )

#creating my own endpoint for Assignment 2
@app.route('/halloween') #endpoint
def halloween():
    time_until_halloween = datetime.datetime(2021, 10, 31) - datetime.datetime.now()
    
    days = time_until_halloween.days
    seconds = time_until_halloween.seconds
    hours = (seconds // 3600) # note that the server is 7 hours ahead of PST
    minutes = (seconds // 60) % 60
    seconds = seconds % 60

    return render_template('countdown_halloween.html', days_remain = str(days), hours_remain = str(hours), minutes_remain = str(minutes), seconds_remain = str(seconds), img_url=IMGS_URL[CUR_ENV])

app.run(host='0.0.0.0', port=80)

