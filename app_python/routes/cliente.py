from fastapi import APIRouter, Depends, HTTPException
import mysql.connector
from models import ClienteCreate, ClienteResponse
from db import get_db

router = APIRouter(prefix="/clientes", tags=["Clientes"])

@router.post("/", response_model=dict)  # Cambiamos response_model a dict para incluir el mensaje
def crear_cliente(cliente: ClienteCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor()
    try:
        cursor.execute(
            """INSERT INTO Cliente (nombre, apellidos, direccion, fecha_nac)
            VALUES (%s, %s, %s, %s)""",
            (cliente.nombre, cliente.apellidos, cliente.direccion, cliente.fecha_nac)
        )
        db.commit()
        return {
            "message": "Cliente creado con éxito",
            "id": cursor.lastrowid,
            "cliente": cliente.model_dump()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.get("/", response_model=list[ClienteResponse])
def listar_clientes(db = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Cliente")
    return cursor.fetchall()
