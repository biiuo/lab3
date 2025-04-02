# Importamos APIRouter para definir rutas en FastAPI
# Importamos Depends para gestionar la inyección de dependencias
# Importamos HTTPException para manejar errores HTTP personalizados
from fastapi import APIRouter, Depends, HTTPException

# Importamos mysql.connector para interactuar con la base de datos MySQL
import mysql.connector

# Importamos los modelos que se utilizarán para la validación y respuesta de los datos
from models import ProveedorBase, ProveedorResponse

# Importamos la función get_db que nos proporciona una conexión a la base de datos
from db import get_db

# Creamos un router para la gestión de proveedores
# - `prefix="/proveedores"` indica que todas las rutas de este router comenzarán con "/proveedores"
# - `tags=["Proveedores"]` agrupa estas rutas bajo la categoría "Proveedores" en la documentación de FastAPI
router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

# ---------------------------- ENDPOINT: CREAR PROVEEDOR ----------------------------

# Definimos un endpoint para crear un nuevo proveedor en la base de datos
@router.post("/", response_model=ProveedorResponse)  # La respuesta esperada es un objeto de tipo ProveedorResponse
def crear_proveedor(proveedor: ProveedorBase, db = Depends(get_db)):
    """
    Crea un nuevo proveedor en la base de datos.

    Parámetros:
    - proveedor (ProveedorBase): Objeto con los datos del proveedor a registrar.
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Un objeto `ProveedorResponse` con los datos del proveedor creado.
    """
    cursor = db.cursor()  # Creamos un cursor para ejecutar consultas SQL
    try:
        # Insertamos el nuevo proveedor en la tabla Proveedor
        cursor.execute(
            """INSERT INTO Proveedor (nit, nombre, direccion)
            VALUES (%s, %s, %s)""",
            (proveedor.nit, proveedor.nombre, proveedor.direccion)
        )
        db.commit()  # Confirmamos la transacción para guardar los cambios en la base de datos
        return proveedor  # Retornamos el proveedor creado como respuesta
    except mysql.connector.IntegrityError:  # Capturamos errores de integridad (como NIT duplicado)
        raise HTTPException(status_code=400, detail="Proveedor ya existe")  # Enviamos un error HTTP con el mensaje
    finally:
        cursor.close()  # Cerramos el cursor para liberar recursos

# ---------------------------- ENDPOINT: LISTAR PROVEEDORES ----------------------------

# Definimos un endpoint para listar todos los proveedores almacenados en la base de datos
@router.get("/", response_model=list[ProveedorResponse])  # La respuesta es una lista de objetos `ProveedorResponse`
def listar_proveedores(db = Depends(get_db)):
    """
    Obtiene una lista de todos los proveedores registrados en la base de datos.

    Parámetros:
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Una lista de objetos `ProveedorResponse`, representando los proveedores almacenados.
    """
    cursor = db.cursor(dictionary=True)  # Creamos un cursor con `dictionary=True` para obtener los resultados como diccionarios
    cursor.execute("SELECT * FROM Proveedor")  # Ejecutamos la consulta SQL para obtener todos los proveedores
    return cursor.fetchall()  # Retornamos la lista de proveedores obtenida de la base de datos
