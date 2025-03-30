from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from models import ProductoBase, ProductoResponse
from db import get_db

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", response_model=ProductoResponse)
def crear_producto(producto: ProductoBase, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO Producto (codigo, nombre, precio_unitario, nit_proveedor)
            VALUES (%s, %s, %s, %s)""",
            (producto.codigo, producto.nombre, producto.precio_unitario, producto.nit_proveedor)
        )
        db.commit()
        return producto
    except mysql.connector.IntegrityError as e:
        raise HTTPException(status_code=400, detail="Error: " + str(e))
    finally:
        cursor.close()

@router.get("/", response_model=list[ProductoResponse])
def listar_productos(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Producto")
    return cursor.fetchall()
