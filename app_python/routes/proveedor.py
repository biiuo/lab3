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

@router.put("/{nit_proveedor}", response_model=ProveedorResponse)
def actualizar_proveedor(nit_proveedor: str, proveedor: ProveedorBase, nuevo_nit: str = None, db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Verificar si el proveedor existe
        cursor.execute("SELECT * FROM Proveedor WHERE nit = %s", (nit_proveedor,))
        proveedor_actual = cursor.fetchone()
        if not proveedor_actual:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        # Si se va a cambiar el NIT
        if nuevo_nit and nuevo_nit != nit_proveedor:
            # Verificar que el nuevo NIT no esté en uso
            cursor.execute("SELECT * FROM Proveedor WHERE nit = %s", (nuevo_nit,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="El nuevo NIT ya está en uso")

            # Insertar nuevo proveedor con nuevo NIT
            cursor.execute("""
                INSERT INTO Proveedor (nit, nombre, direccion)
                VALUES (%s, %s, %s)
            """, (nuevo_nit, proveedor.nombre, proveedor.direccion))

            # Actualizar los productos que usaban el NIT anterior
            cursor.execute("""
                UPDATE Producto SET nit_proveedor = %s WHERE nit_proveedor = %s
            """, (nuevo_nit, nit_proveedor))

            # Eliminar proveedor viejo
            cursor.execute("DELETE FROM Proveedor WHERE nit = %s", (nit_proveedor,))
        else:
            # Solo actualizar campos si no se cambia el NIT
            cursor.execute("""
                UPDATE Proveedor SET nombre = %s, direccion = %s
                WHERE nit = %s
            """, (proveedor.nombre, proveedor.direccion, nit_proveedor))

        db.commit()

        # Retornar proveedor actualizado
        nit_resultado = nuevo_nit if nuevo_nit else nit_proveedor
        cursor.execute("SELECT * FROM Proveedor WHERE nit = %s", (nit_resultado,))
        proveedor_actualizado = cursor.fetchone()
        return ProveedorResponse(**proveedor_actualizado)

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.delete("/{nit_proveedor}")
def eliminar_proveedor(nit_proveedor: str, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM Proveedor WHERE nit = %s", (nit_proveedor,))
        proveedor = cursor.fetchone()
        if not proveedor:
            raise HTTPException(status_code=404, detail="Proveedor no encontrado")

        # Obtener productos del proveedor
        cursor.execute("SELECT codigo FROM Producto WHERE nit_proveedor = %s", (nit_proveedor,))
        productos = cursor.fetchall()

        # Eliminar compras de cada producto
        for producto in productos:
            cursor.execute("DELETE FROM Compra WHERE codigo_producto = %s", (producto[0],))

        # Eliminar productos del proveedor
        cursor.execute("DELETE FROM Producto WHERE nit_proveedor = %s", (nit_proveedor,))

        # Eliminar proveedor
        cursor.execute("DELETE FROM Proveedor WHERE nit = %s", (nit_proveedor,))
        db.commit()

        return {"message": f"Proveedor con NIT '{nit_proveedor}', sus productos y compras relacionadas fueron eliminados exitosamente"}

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()