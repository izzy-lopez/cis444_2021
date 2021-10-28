import jwt
import bcrypt
import os
from flask import Flask, request, send_from_directory
from flask.json import jsonify
from flask_json import FlaskJSON
from psycopg2 import sql
from db_con import get_db

""" Assignment 3: Full stack web application that allows users to buy books.

Objective: 
    A user can create a new account or login with an existing account to access a simple UI 
    that allows them to view a list of books and their corresponding prices. The user can then
    select a book and buy it. All information is stored within a postgres database.

Additional information:
    Passwords are encrypted using the bcrypt module. JSON web token (JWT) is 
    utilized to authenticate the user's session on the web application.

NOTE: The tables being used in the database are as follows:
    users
    - id, username, password

    books
    - id, title, price

    purchased_books
    - id, user_id, book_id
"""

SECRET = ""

app = Flask(__name__)
FlaskJSON(app)

# connect to the database 
global_db_con = get_db()

# read the secret from a file
full_path = os.path.realpath(__file__)
directory = os.path.dirname(full_path)
with open(directory + "/secret.txt", "r") as f:
    SECRET = f.read()

@app.route('/') #endpoint
def index():
    return send_from_directory('static','login.html')

@app.route('/userauth', methods=['POST']) # endpoint
def user_auth():
    """Authenticates a user given their credentials.

    Queries the database to make sure the credentials are valid. If the
    account is valid, we will create a jwt containing their username and
    password which will be used for further authentication throughout the 
    application.

    Returns:
        A JSON response that includes the results of the authentication process.    
    """
    username = request.form.get('username') # get username from form

    # query the database for the user's password
    cur = global_db_con.cursor()
    cur.execute(sql.SQL("SELECT password FROM users WHERE username = %s;"), (username,))
    stored_password = cur.fetchone() 
    cur.close()

    # fetchone() returns a Tuple, so make sure the Tuple is not None
    if stored_password == None:
        print(username, 'does not exist')
        return jsonify(
            logged_in=False
        )   

    # compare the password recieved from the form with the stored password in the database
    # NOTE: stored_password is a Tuple so access its first element to get the password
    if not bcrypt.checkpw( bytes(request.form.get('password'), 'utf-8'), str.encode(stored_password[0])):
        print('password is invalid')
        return jsonify(
            logged_in=False
        )

    # encode a jwt with the username and stored password
    encoded_jwt = jwt.encode(
        {
            'username': username, 
            'password': stored_password[0]
        }, SECRET, algorithm="HS256")

    # return the jwt and logged_in boolean in json format
    return jsonify(
        jwt=encoded_jwt,
        logged_in=True
    )

@app.route('/createaccount', methods=['POST']) # endpoint
def create_account():
    """Attempts to create an account given a set of credentials.

    Queries the database to make sure the credentials are valid and 
    not already in use. If the account can be created, we will create 
    a jwt containing their username and password which will be used 
    for further authentication throughout the application.

    Returns:
        A JSON response that includes the results of the account creation process.    
    """
    username = request.form.get('username') # get username from form

    # query the database for a username matching the user's desired username
    cur = global_db_con.cursor()
    cur.execute(sql.SQL("SELECT username FROM users WHERE username = %s;"), (username,))
    usernames = cur.fetchone() 

    # make sure the username is not already taken
    if not usernames == None:
        print('Username is already in use')
        return jsonify(
            logged_in=False
        )   

    # hash the password recieved from the form
    encrypted_password = bcrypt.hashpw(bytes(request.form.get('password'), 'utf-8'), bcrypt.gensalt(10))

    # insert a new account into the database
    cur.execute(sql.SQL("INSERT INTO users (username, password) VALUES (%s, %s);"), (username, encrypted_password.decode('utf-8'),))
    cur.close()
    global_db_con.commit()

    # encode the jwt
    encoded_jwt = jwt.encode(
        {
            'username': username, 
            'password': encrypted_password.decode('utf-8') 
        }, SECRET, algorithm="HS256")

    # return the jwt and logged_in boolean in json format
    return jsonify(
        jwt=encoded_jwt,
        logged_in=True
    )

@app.route('/getbooks', methods=['GET']) # endpoint
def get_books():
    """Returns the books stored within the database.

    First check to see if the jwt is valid. If so, we will then 
    query the database to return a list of books.

    Returns:
        A JSON response that includes the results of querying the database.    
    """
    recieved_jwt = request.args.get("jwt")
    if not jwt.decode(recieved_jwt, SECRET, algorithms=["HS256"]):
        return jsonify(logged_in=False)

    decoded_jwt = jwt.decode(recieved_jwt, SECRET, algorithms=["HS256"])

    # query the database for all books
    cur = global_db_con.cursor()
    cur.execute(sql.SQL("SELECT * FROM books;"))
    retrieved_books = cur.fetchall() 
    cur.close()

    # store all books in a list, with each book contained in their own dictionary
    list_of_books = []
    for book in retrieved_books:
        book_dict = {"title": book[1], "price": book[2]}
        list_of_books.append(book_dict)

    return jsonify(
        books=list_of_books,
        jwt=recieved_jwt,
        logged_in=True,
        username=decoded_jwt.get('username')
    )

@app.route('/buyselectedbook', methods=['GET']) # endpoint
def buy_selected_book():
    """Attempts to purchase the user's selected book.

    First check to see if the jwt is valid. If so, we will then 
    attempt to insert the selected book into the appropriate table.

    Returns:
        A JSON response that includes the results of attempting to buy the book.    
    """
    recieved_jwt = request.args.get("jwt")
    if not jwt.decode(recieved_jwt, SECRET, algorithms=["HS256"]):
        return jsonify(logged_in=False)

    decoded_jwt = jwt.decode(recieved_jwt, SECRET, algorithms=["HS256"])

    selected_book = request.args.get("selected_book") # retrieve the selected book

    # query the database for all of the user's purchased books
    cur = global_db_con.cursor()
    cur.execute(
        sql.SQL('SELECT b.title FROM users AS u, books AS b, purchased_books AS pb ' 
        + 'WHERE u.id = pb.user_id AND b.id = pb.book_id ' 
        + 'AND u.username = %s;'), (decoded_jwt.get('username'),))
    results = cur.fetchall() 

    # store all books owned by the user in a list
    user_owned_books = []
    for book in results:
        user_owned_books.append(book[0])

    # do not let the user purchase the book if they already own it
    if selected_book in user_owned_books:
        print("User already owns this book")

        # REencode the jwt to include the user's current list of books
        reencoded_jwt = jwt.encode(
        {
            'username': decoded_jwt.get('username'), 
            'password': decoded_jwt.get('password'),
            'books': user_owned_books
        }, SECRET, algorithm="HS256")

        return jsonify(
            buy_success=False,
            jwt=reencoded_jwt,
            logged_in=True,
        )

    user_owned_books.append(selected_book) # add the book to the user's list

    # insert the desired book to be purchased
    cur.execute(sql.SQL("SELECT id FROM users WHERE username = %s;"), (decoded_jwt.get('username'),))
    user_id = cur.fetchone()

    cur.execute(sql.SQL("SELECT id FROM books WHERE title = %s;"), (selected_book,))
    book_id = cur.fetchone()

    cur.execute(sql.SQL("INSERT INTO purchased_books (user_id, book_id) VALUES (%s, %s);"), (user_id[0], book_id[0],))

    cur.close()
    global_db_con.commit()  
    print("Purchase successful")
    
    # REencode the jwt to include the user's current list of books
    reencoded_jwt = jwt.encode(
        {
            'username': decoded_jwt.get('username'), 
            'password': decoded_jwt.get('password'),
            'books': user_owned_books
        }, SECRET, algorithm="HS256")

    return jsonify(
        buy_success=True,
        jwt=reencoded_jwt,
        logged_in=True,
    )

app.run(host='0.0.0.0', port=80)
