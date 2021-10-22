import psycopg2


def get_db():
    return psycopg2.connect(host="localhost", dbname="authme" , user="loki", password="4prez")

def get_db_instance():  
    db  = get_db()
    cur  = db.cursor( )

    return db, cur 


