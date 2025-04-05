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

@router.put("/{codigo_producto}", response_model=ProductoResponse)
def actualizar_producto(codigo_producto: str, producto: ProductoBase, nuevo_codigo: str = None, db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Verificar si el producto original existe
        cursor.execute("SELECT * FROM Producto WHERE codigo = %s", (codigo_producto,))
        producto_actual = cursor.fetchone()
        if not producto_actual:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Si se va a cambiar el código
        if nuevo_codigo and nuevo_codigo != codigo_producto:
            # Verificar que el nuevo código no esté en uso
            cursor.execute("SELECT * FROM Producto WHERE codigo = %s", (nuevo_codigo,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="El nuevo código ya está en uso")

            # Insertar nuevo producto con nuevo código
            cursor.execute("""
                INSERT INTO Producto (codigo, nombre, precio_unitario, nit_proveedor)
                VALUES (%s, %s, %s, %s)
            """, (nuevo_codigo, producto.nombre, producto.precio_unitario, producto.nit_proveedor))

            # Actualizar todas las compras con el nuevo código
            cursor.execute("""
                UPDATE Compra SET codigo_producto = %s WHERE codigo_producto = %s
            """, (nuevo_codigo, codigo_producto))

            # Eliminar el producto viejo
            cursor.execute("DELETE FROM Producto WHERE codigo = %s", (codigo_producto,))
        else:
            # Solo actualizar datos si no se cambia el código
            cursor.execute("""
                UPDATE Producto 
                SET nombre = %s, precio_unitario = %s, nit_proveedor = %s
                WHERE codigo = %s
            """, (producto.nombre, producto.precio_unitario, producto.nit_proveedor, codigo_producto))

        db.commit()

        # Retornar el producto actualizado (nuevo o modificado)
        codigo_resultado = nuevo_codigo if nuevo_codigo else codigo_producto
        cursor.execute("SELECT * FROM Producto WHERE codigo = %s", (codigo_resultado,))
        producto_actualizado = cursor.fetchone()
        return ProductoResponse(**producto_actualizado)

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{codigo_producto}")
def eliminar_producto(codigo_producto: str, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Producto WHERE codigo = %s", (codigo_producto,))
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # Eliminar compras relacionadas
        cursor.execute("DELETE FROM Compra WHERE codigo_producto = %s", (codigo_producto,))
        # Eliminar el producto
        cursor.execute("DELETE FROM Producto WHERE codigo = %s", (codigo_producto,))
        db.commit()

        return {"message": f"Producto con código '{codigo_producto}' y sus compras fueron eliminados exitosamente"}

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()
