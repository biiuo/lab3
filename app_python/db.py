# Importamos el módulo mysql.connector para conectarnos a la base de datos MySQL
import mysql.connector
from mysql.connector import Error  # Importamos la clase Error para manejar excepciones

# Configuración de la base de datos con los datos de conexión
DB_CONFIG = {
    "host": "localhost",       # Servidor donde se encuentra la base de datos (local en este caso)
    "user": "root",            # Usuario de la base de datos
    "password": "1Semeolvido.", # Contraseña del usuario (considera no compartir contraseñas en código público)
    "database": "venta",       # Nombre de la base de datos a la que queremos conectarnos
}

# Función generadora para obtener una conexión a la base de datos
def get_db():
    mydb = None  # Inicializamos la variable de conexión como None
    try:
        # Intentamos establecer la conexión usando la configuración definida en DB_CONFIG
        mydb = mysql.connector.connect(**DB_CONFIG)
        yield mydb  # Retornamos la conexión para que pueda ser utilizada en una consulta

    except Error as err:  # Capturamos cualquier error de conexión
        # Lanzamos una excepción en caso de que haya un error en la conexión
        raise RuntimeError(f"Error de conexión a la base de datos: {err}")

    finally:
        # Aseguramos que la conexión se cierre después de ser utilizada
        if mydb:
            mydb.close()
