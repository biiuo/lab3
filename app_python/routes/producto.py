# Importamos APIRouter para definir rutas en FastAPI
# Importamos Depends para gestionar la inyección de dependencias
# Importamos HTTPException para manejar errores HTTP personalizados
from fastapi import APIRouter, Depends, HTTPException

# Importamos mysql.connector para interactuar con la base de datos MySQL
import mysql.connector

# Importamos los modelos que se utilizarán para la validación y respuesta de los datos
from models import ProductoBase, ProductoResponse

# Importamos la función get_db que nos proporciona una conexión a la base de datos
from db import get_db

# Creamos un router para la gestión de productos
# - `prefix="/productos"` indica que todas las rutas de este router comenzarán con "/productos"
# - `tags=["Productos"]` agrupa estas rutas bajo la categoría "Productos" en la documentación de FastAPI
router = APIRouter(prefix="/productos", tags=["Productos"])

# ---------------------------- ENDPOINT: CREAR PRODUCTO ----------------------------

# Definimos un endpoint para crear un nuevo producto en la base de datos
@router.post("/", response_model=ProductoResponse)  # La respuesta esperada es un objeto de tipo ProductoResponse
def crear_producto(producto: ProductoBase, db = Depends(get_db)):
    """
    Crea un nuevo producto en la base de datos.

    Parámetros:
    - producto (ProductoBase): Objeto con los datos del producto a registrar.
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Un objeto `ProductoResponse` con los datos del producto creado.
    """
    cursor = db.cursor()  # Creamos un cursor para ejecutar consultas SQL
    try:
        # Insertamos el nuevo producto en la tabla Producto
        cursor.execute(
            """INSERT INTO Producto (codigo, nombre, precio_unitario, nit_proveedor)
            VALUES (%s, %s, %s, %s)""",
            (producto.codigo, producto.nombre, producto.precio_unitario, producto.nit_proveedor)
        )
        db.commit()  # Confirmamos la transacción para guardar los cambios en la base de datos
        return producto  # Retornamos el producto creado como respuesta
    except mysql.connector.IntegrityError as e:  # Capturamos errores de integridad (como claves duplicadas)
        raise HTTPException(status_code=400, detail="Error: " + str(e))  # Enviamos un error HTTP con el mensaje del error
    finally:
        cursor.close()  # Cerramos el cursor para liberar recursos

# ---------------------------- ENDPOINT: LISTAR PRODUCTOS ----------------------------

# Definimos un endpoint para listar todos los productos almacenados en la base de datos
@router.get("/", response_model=list[ProductoResponse])  # La respuesta es una lista de objetos `ProductoResponse`
def listar_productos(db = Depends(get_db)):
    """
    Obtiene una lista de todos los productos registrados en la base de datos.

    Parámetros:
    - db: Conexión a la base de datos obtenida mediante `Depends(get_db)`.

    Retorna:
    - Una lista de objetos `ProductoResponse`, representando los productos almacenados.
    """
    cursor = db.cursor(dictionary=True)  # Creamos un cursor con `dictionary=True` para obtener los resultados como diccionarios
    cursor.execute("SELECT * FROM Producto")  # Ejecutamos la consulta SQL para obtener todos los productos
    return cursor.fetchall()  # Retornamos la lista de productos obtenida de la base de datos
