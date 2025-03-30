from fastapi import APIRouter, Depends, HTTPException
from typing import List
import mysql.connector
from db import get_db
from models import CompraResponse, CompraBase,CompraCreate  # Asegúrate de tener este modelo

router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=CompraResponse)
def crear_compra(compra: CompraCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # 1. Verificar existencia de cliente y producto
        cursor.execute("SELECT 1 FROM Cliente WHERE id = %s", (compra.id_cliente,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        cursor.execute(
            "SELECT nombre, precio_unitario FROM Producto WHERE codigo = %s", 
            (compra.codigo_producto,)
        )
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # 2. Insertar compra
        cursor.execute(
            """INSERT INTO Compra (id_cliente, codigo_producto, cantidad)
            VALUES (%s, %s, %s)""",
            (compra.id_cliente, compra.codigo_producto, compra.cantidad)
        )
        db.commit()

        # 3. Calcular total y construir respuesta
        total = producto["precio_unitario"] * compra.cantidad
        
        return {
            "id_cliente": compra.id_cliente,
            "codigo_producto": compra.codigo_producto,
            "cantidad": compra.cantidad,
            "fecha_compra": compra.fecha_compra,
            "total": total,  # Campo calculado
            "producto_nombre": producto["nombre"],
            "precio_unitario": producto["precio_unitario"]
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cursor.close()

@router.get("/", response_model=List[CompraResponse])
def listar_compras(db: mysql.connector.MySQLConnection = Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        # Consulta con JOIN para obtener todas las compras + total calculado
        cursor.execute("""
            SELECT 
                c.id_cliente,
                c.codigo_producto,
                c.cantidad,
                c.fecha_compra,
                (p.precio_unitario * c.cantidad) AS total,  # Cálculo directo en SQL
                p.nombre AS producto_nombre,
                p.precio_unitario,
                cli.nombre AS cliente_nombre  # Opcional: añadir info del cliente
            FROM Compra c
            JOIN Producto p ON c.codigo_producto = p.codigo
            JOIN Cliente cli ON c.id_cliente = cli.id
            ORDER BY c.fecha_compra DESC
        """)
        return cursor.fetchall()
    finally:
        cursor.close()