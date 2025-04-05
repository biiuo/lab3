# Importamos APIRouter para definir rutas en FastAPI
# Importamos Depends para gestionar la inyección de dependencias
# Importamos HTTPException para manejar errores HTTP personalizados
from fastapi import APIRouter, Depends, HTTPException

# Importamos mysql.connector para interactuar con la base de datos MySQL
import mysql.connector

# Importamos los modelos que utilizaremos para validar los datos
from models import ClienteCreate, ClienteResponse, ClienteBase

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

@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(cliente_id: int, cliente: ClienteBase, nuevo_id: int = None, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Verificar si el cliente existe
        cursor.execute("SELECT * FROM Cliente WHERE id = %s", (cliente_id,))
        cliente_actual = cursor.fetchone()
        if not cliente_actual:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        if nuevo_id and nuevo_id != cliente_id:
            # Verificar que el nuevo ID no esté en uso
            cursor.execute("SELECT id FROM Cliente WHERE id = %s", (nuevo_id,))
            if cursor.fetchone():
                raise HTTPException(status_code=400, detail="El nuevo ID ya está en uso")

            # Insertar el nuevo cliente con el nuevo ID
            cursor.execute(
                "INSERT INTO Cliente (id, nombre, apellidos, direccion, fecha_nac) VALUES (%s, %s, %s, %s, %s)",
                (nuevo_id, cliente.nombre, cliente.apellidos, cliente.direccion, cliente.fecha_nac)
            )
            
            # Actualizar id_cliente en Compra
            cursor.execute("UPDATE Compra SET id_cliente = %s WHERE id_cliente = %s", (nuevo_id, cliente_id))

            # Eliminar el cliente antiguo
            cursor.execute("DELETE FROM Cliente WHERE id = %s", (cliente_id,))

        else:
            # Actualizar solo los datos del cliente si el ID no cambia
            cursor.execute(
                "UPDATE Cliente SET nombre = %s, apellidos = %s, direccion = %s, fecha_nac = %s WHERE id = %s",
                (cliente.nombre, cliente.apellidos, cliente.direccion, cliente.fecha_nac, cliente_id)
            )

        db.commit()

        # Obtener los datos actualizados
        cursor.execute("SELECT * FROM Cliente WHERE id = %s", (nuevo_id if nuevo_id else cliente_id,))
        cliente_actualizado = cursor.fetchone()

        return ClienteResponse(**cliente_actualizado)

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()

@router.delete("/{id_cliente}")
def eliminar_cliente(id_cliente: int, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        # Verificar si el cliente existe
        cursor.execute("SELECT * FROM Cliente WHERE id = %s", (id_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # Eliminar las compras asociadas al cliente
        cursor.execute("DELETE FROM Compra WHERE id_cliente = %s", (id_cliente,))

        # Eliminar el cliente
        cursor.execute("DELETE FROM Cliente WHERE id = %s", (id_cliente,))
        db.commit()

        return {"message": f"Cliente con ID {id_cliente} y sus compras fueron eliminados exitosamente"}

    except mysql.connector.Error as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

#Consulta 1
@router.get("/reporte/pedidos", tags=["Reportes"])
def clientes_cantidad_pedidos(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT CONCAT(nombre, " ", apellidos) AS nombre_completo,
                   COUNT(codigo_producto) AS cantidad_pedidos
            FROM cliente
            LEFT JOIN compra ON id_cliente = id
            GROUP BY id;
        """)
        return cursor.fetchall()
    finally:
        cursor.close()

@router.get("/reporte/sin-pedidos", tags=["Reportes"])
def clientes_sin_pedidos(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT CONCAT(nombre, " ", apellidos) AS nombre_completo
            FROM cliente
            WHERE id NOT IN (
                SELECT id_cliente FROM compra
            );
        """)
        return cursor.fetchall()
    finally:
        cursor.close()
