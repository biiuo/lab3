from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from models import ProveedorBase, ProveedorResponse
from db import get_db

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])

@router.post("/", response_model=ProveedorResponse)
def crear_proveedor(proveedor: ProveedorBase, db = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO Proveedor (nit, nombre, direccion)
            VALUES (%s, %s, %s)""",
            (proveedor.nit, proveedor.nombre, proveedor.direccion)
        )
        db.commit()
        return proveedor
    except mysql.connector.IntegrityError:
        raise HTTPException(status_code=400, detail="Proveedor ya existe")
    finally:
        cursor.close()

@router.get("/", response_model=list[ProveedorResponse])
def listar_proveedores(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Proveedor")
    return cursor.fetchall()