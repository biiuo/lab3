# Importamos APIRouter para definir rutas en FastAPI
# Importamos Depends para gestionar la inyección de dependencias
# Importamos HTTPException para manejar errores HTTP personalizados
from fastapi import APIRouter, Depends, HTTPException

# Importamos mysql.connector para interactuar con la base de datos MySQL
import mysql.connector

# Importamos los modelos que utilizaremos para validar los datos
from models import ClienteCreate, ClienteResponse

# Importamos la función get_db que nos proporciona una conexión a la base de datos
from db import get_db

# Creamos un router para la gestión de clientes
# - `prefix="/clientes"` indica que todas las rutas de este router comenzarán con "/clientes"
# - `tags=["Clientes"]` agrupa estas rutas bajo la categoría "Clientes" en la documentación de FastAPI
router = APIRouter(prefix="/clientes", tags=["Clientes"])

# ---------------------------- ENDPOINT: CREAR CLIENTE ----------------------------

# Definimos un endpoint para crear clientes en la base de datos
@router.post("/hola", response_model=dict)  # El response_model se cambia a `dict` para incluir un mensaje personalizado
def crear_cliente(cliente: ClienteCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    """
    Crea un nuevo cliente en la base de datos.

    Parámetros:
    - cliente (ClienteCreate): Objeto con los datos del cliente a registrar.
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Un diccionario con un mensaje de éxito, el ID del cliente creado y los datos del cliente.
    """
    cursor = db.cursor()  # Creamos un cursor para ejecutar consultas SQL
    try:
        # Insertamos un nuevo cliente en la tabla Cliente
        cursor.execute(
            """INSERT INTO Cliente (nombre, apellidos, direccion, fecha_nac)
            VALUES (%s, %s, %s, %s)""",
            (cliente.nombre, cliente.apellidos, cliente.direccion, cliente.fecha_nac)
        )
        db.commit()  # Confirmamos la transacción para guardar los cambios en la base de datos

        # Retornamos un mensaje de éxito junto con el ID del cliente creado y sus datos
        return {
            "message": "Cliente creado con éxito",
            "id": cursor.lastrowid,  # `lastrowid` obtiene el ID del último registro insertado
            "cliente": cliente.model_dump()  # Convertimos el modelo Pydantic a un diccionario
        }
    except Exception as e:
        db.rollback()  # Si ocurre un error, deshacemos cualquier cambio realizado en la base de datos
        raise HTTPException(status_code=400, detail=str(e))  # Enviamos un error HTTP con el mensaje del error
    finally:
        cursor.close()  # Cerramos el cursor para liberar recursos

# ---------------------------- ENDPOINT: LISTAR CLIENTES ----------------------------

# Definimos un endpoint para listar todos los clientes almacenados en la base de datos
@router.get("/", response_model=list[ClienteResponse])  # Especificamos que la respuesta será una lista de `ClienteResponse`
def listar_clientes(db = Depends(get_db)):
    """
    Obtiene una lista de todos los clientes registrados en la base de datos.

    Parámetros:
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Una lista de objetos `ClienteResponse`, representando los clientes almacenados.
    """
    cursor = db.cursor(dictionary=True)  # Creamos un cursor con `dictionary=True` para obtener los resultados como diccionarios
    cursor.execute("SELECT * FROM Cliente")  # Ejecutamos la consulta SQL para obtener todos los clientes
    return cursor.fetchall()  # Retornamos la lista de clientes obtenida de la base de datos

