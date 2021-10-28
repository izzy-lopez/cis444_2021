import jwt
import datetime
import bcrypt
import os
import re
from re import S
from flask import Flask,render_template,request
from flask.json import jsonify
from flask_json import FlaskJSON, JsonError, json_response, as_json
from psycopg2 import sql
from db_con import get_db_instance, get_db

app = Flask(__name__)
FlaskJSON(app)

USER_PASSWORDS = { "cjardin": "strong password"}

IMGS_URL = {
            "DEV" : "/static",
            "INT" : "https://cis-444-fall-2021.s3.us-west-2.amazonaws.com/images",
            "PRD" : "http://d2cbuxq67vowa3.cloudfront.net/images"
            }

CUR_ENV = "DEV"
SECRET = ""

# connect to the database 
global_db_con = get_db()

# read the secret from a file
full_path = os.path.realpath(__file__)
directory = os.path.dirname(full_path)
with open(directory + "/secret.txt", "r") as f:
    SECRET = f.read()

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
    print(request.form)
    salted = bcrypt.hashpw( bytes(request.form['fname'],  'utf-8' ) , bcrypt.gensalt(10))
    print(salted)

    print(  bcrypt.checkpw(  bytes(request.form['fname'],  'utf-8' )  , salted ))

    return render_template('backatu.html',input_from_browser= str(request.form) )

@app.route('/auth',  methods=['POST']) #endpoint
def auth():
        print(request.form)
        return json_response(data=request.form)

# ---------------------
# start of Assignment 2
@app.route('/ss1') #endpoint
def ss1():
    return render_template('server_time.html', server_time= str(datetime.datetime.now()) )

# creating my own endpoint for Assignment 2
@app.route('/halloween') #endpoint
def halloween():
    time_until_halloween = datetime.datetime(2021, 10, 31) - datetime.datetime.now()
    
    days = time_until_halloween.days
    seconds = time_until_halloween.seconds
    hours = (seconds // 3600) # note that the server is 7 hours ahead of PST
    minutes = (seconds // 60) % 60
    seconds = seconds % 60

    return render_template('countdown_halloween.html', days_remain = str(days), 
    hours_remain = str(hours), minutes_remain = str(minutes), seconds_remain = str(seconds), 
    img_url=IMGS_URL[CUR_ENV])
# end of Assignment 2
# ---------------------

@app.route('/getTime') #endpoint
def get_time():
    return json_response(data={"password" : request.args.get('password'),
                                "class" : "cis44",
                                "serverTime":str(datetime.datetime.now())
                            }
                )

@app.route('/auth2') #endpoint
def auth2():
    jwt_str = jwt.encode({"username" : "cary", "age" : "so young"} , SECRET, algorithm="HS256")
    #print(request.form['username'])
    return json_response(jwt=jwt_str)

@app.route('/exposejwt') #endpoint
def exposejwt():
    jwt_token = request.args.get('jwt')
    print(jwt_token)
    return json_response(output=jwt.decode(jwt_token, SECRET, algorithms=["HS256"]))

@app.route('/hellodb') #endpoint
def hellodb():
    cur = global_db_con.cursor()
    cur.execute("select 5+5, 1+1")
    first,second = cur.fetchone()
    return json_response(a=first, b=second)

app.run(host='0.0.0.0', port=80)
