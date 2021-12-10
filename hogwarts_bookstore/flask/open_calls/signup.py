import bcrypt
from flask import request, g
from psycopg2 import sql
from flask_json import json_response
from tools.token_tools import create_token
from tools.logging import logger

def handle_request():
    logger.debug("Login Handle Request")

    #use data here to auth the user
    jwt_data = {
            "sub" : request.form['username'] #sub is used by pyJwt as the owner of the token
    }

    # query the database for a username matching the user's desired username
    cur = g.db.cursor()
    cur.execute(sql.SQL("SELECT username FROM users WHERE username = %s;"), (jwt_data['sub'],))
    username = cur.fetchone() 

    # make sure the username is not already taken
    if not username == None:
        logger.debug('Username is already in use')
        return json_response( status_ = 401, message = 'Username taken', authenticated =  False )

    # hash the password recieved from the form
    encrypted_password = bcrypt.hashpw(bytes(request.form.get('password'), 'utf-8'), bcrypt.gensalt(10))

    # insert a new account into the database
    cur.execute(sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s);"), (jwt_data['sub'], encrypted_password.decode('utf-8'),))
    cur.close()
    g.db.commit()

    return json_response( token = create_token(jwt_data), authenticated = True )

