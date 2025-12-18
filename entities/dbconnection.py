import sqlite3 
from contextlib import contextmanager 

@contextmanager
def db_connection(db_name , commit=False):
    connection = sqlite3.connect(db_name)
    cursor = connection.cursor()
    try:
        yield cursor
        if commit : connection.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        if commit : connection.rollback() 
    finally:
        connection.close()