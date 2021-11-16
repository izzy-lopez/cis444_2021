from flask import request, g
from psycopg2 import sql
from flask_json import FlaskJSON, JsonError, json_response, as_json
from tools.token_tools import create_token
from tools.logging import logger

def handle_request():
    logger.debug("Get Books Handle Request")

    selected_book = request.args.get("selected_book") # retrieve the selected book

    # query the database for all of the user's purchased books
    cur = g.db.cursor()
    cur.execute(
        sql.SQL('SELECT b.title FROM users AS u, books AS b, purchased_books AS pb ' 
        + 'WHERE u.id = pb.user_id AND b.id = pb.book_id ' 
        + 'AND u.username = %s;'), (g.jwt_data['sub'],))
    results = cur.fetchall() 

    # store all books owned by the user in a list
    user_owned_books = []
    for book in results:
        user_owned_books.append(book[0])

    # do not let the user purchase the book if they already own it
    if selected_book in user_owned_books:
        g.jwt_data['books'] = user_owned_books # include the user's books in the token
        return json_response( token = create_token(g.jwt_data), purchase_success =  False )

    user_owned_books.append(selected_book) # add the book to the user's list
    g.jwt_data['books'] = user_owned_books # include the user's books in the token

    # get the user id
    cur.execute(sql.SQL("SELECT id FROM users WHERE username = %s;"), (g.jwt_data['sub'],))
    user_id = cur.fetchone()

    # get the book id
    cur.execute(sql.SQL("SELECT id FROM books WHERE title = %s;"), (selected_book,))
    book_id = cur.fetchone()

    # insert the desired book to be purchased
    cur.execute(sql.SQL("INSERT INTO purchased_books (user_id, book_id) VALUES (%s, %s);"), (user_id[0], book_id[0],))

    cur.close()
    g.db.commit()  
    logger.debug("Purchase successful")

    return json_response( token = create_token(g.jwt_data), purchase_success = True )

