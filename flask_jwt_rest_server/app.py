from flask import Flask, redirect, g
from flask_json import FlaskJSON, json_response
from db_con import get_db
from tools.token_required import token_required
from tools.get_aws_secrets import get_secrets
from tools.logging import logger
import traceback

ERROR_MSG = "Ooops.. Didn't work!"

app = Flask(__name__) #Create our app
FlaskJSON(app) #add in flask json

#g is flask for a global var storage 
def init_new_env():
    if 'db' not in g:
        g.db = get_db()

    g.secrets = get_secrets()


#This gets executed by default by the browser if no page is specified
#So.. we redirect to the endpoint we want to load the base page
@app.route('/') #endpoint
def index():
    return redirect('/static/login.html')


@app.route("/secure_api/<proc_name>", methods = ['GET', 'POST'])
@token_required
def exec_secure_proc(proc_name):
    logger.debug("Secure Call to " + proc_name)

    #setup the env
    init_new_env()

    #see if we can execute it..
    resp = ""
    try:
        fn = getattr(__import__('secure_calls.'+proc_name), proc_name)
        resp = fn.handle_request()
    except Exception as err:
        ex_data = str(Exception) + '\n'
        ex_data = ex_data + str(err) + '\n'
        ex_data = ex_data + traceback.format_exc()
        logger.error(ex_data)
        return json_response( status_=500, data=ERROR_MSG )

    return resp


@app.route("/open_api/<proc_name>", methods = ['GET', 'POST'])
def exec_proc(proc_name):
    logger.debug("Call to " + proc_name)

    #setup the env
    init_new_env()

    #see if we can execute it..
    resp = ""
    try:
        fn = getattr(__import__('open_calls.'+proc_name), proc_name)
        resp = fn.handle_request()
    except Exception as err:
        ex_data = str(Exception) + '\n'
        ex_data = ex_data + str(err) + '\n'
        ex_data = ex_data + traceback.format_exc()
        logger.error(ex_data)
        return json_response( status_=500, data=ERROR_MSG )

    return resp


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80)
