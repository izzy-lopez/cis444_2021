from flask import g
from psycopg2 import sql
from flask_json import json_response
from tools.token_tools import create_token
from tools.logging import logger

def handle_request():
    logger.debug("Get Books Handle Request")

    # query the database for all books
    cur = g.db.cursor()
    cur.execute(sql.SQL("SELECT * FROM books;"))
    retrieved_books = cur.fetchall() 
    cur.close()

    # store all books in a list, with each book contained in their own dictionary
    list_of_books = []
    for book in retrieved_books:
        book_dict = {"title": book[1], "price": book[2]}
        list_of_books.append(book_dict)

    return json_response( token = create_token(g.jwt_data), books = list_of_books, username = g.jwt_data['sub'] )

