import mysql.connector
from mysql.connector import Error

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1Semeolvido.",
    "database": "venta",
}

def get_db():
    mydb = None
    try:
        mydb = mysql.connector.connect(**DB_CONFIG)
        yield mydb
    except Error as err:
        raise RuntimeError(f"Error de conexión a la base de datos: {err}")
    finally:
        if mydb:
            mydb.close()
