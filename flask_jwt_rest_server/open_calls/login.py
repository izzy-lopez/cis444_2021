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

    # query the database for the user's password
    cur = g.db.cursor()
    cur.execute(sql.SQL("SELECT password FROM users WHERE username = %s;"), (jwt_data['sub'],))
    stored_password = cur.fetchone() 
    cur.close()

    # fetchone() returns a Tuple, so make sure the Tuple is not None
    if stored_password == None:
        logger.debug('user does not exist')
        return json_response( status_ = 401, message = 'Invalid credentials', authenticated = False )

    # compare the password recieved from the form with the stored password in the database
    # NOTE: stored_password is a Tuple so access its first element to get the password
    if not bcrypt.checkpw(bytes(request.form.get('password'), 'utf-8'), str.encode(stored_password[0])):
        logger.debug('password is invalid')
        return json_response( status_ = 401, message = 'Invalid credentials', authenticated = False )

    return json_response( token = create_token(jwt_data), authenticated = True )
