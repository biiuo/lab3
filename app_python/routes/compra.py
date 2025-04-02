from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import mysql.connector
from datetime import datetime
from pydantic import BaseModel
from db import get_db
from models import ClienteResponse, ProductoResponse, CompraCreate, CompraResponse, ProductoBase

# Crear el router para gestionar las rutas relacionadas con compras
router = APIRouter(prefix="/compras", tags=["Compras"])

@router.post("/", response_model=CompraResponse)
def crear_compra(compra: CompraCreate, db: mysql.connector.MySQLConnection = Depends(get_db)):
    """
    Endpoint para crear una nueva compra en la base de datos.
    Recibe los datos de la compra, verifica que el cliente y el producto existan,
    calcula el total de la compra y almacena la información en la base de datos.
    """
    cursor = db.cursor(dictionary=True)
    
    try:
        # 1. Verificar si el cliente existe en la base de datos
        cursor.execute("SELECT id, nombre, apellidos, direccion, fecha_nac FROM Cliente WHERE id = %s", (compra.id_cliente,))
        cliente = cursor.fetchone()
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")

        # 2. Verificar si el producto existe en la base de datos
        cursor.execute("SELECT codigo, nombre, precio_unitario, nit_proveedor FROM Producto WHERE codigo = %s", (compra.codigo_producto,))
        producto = cursor.fetchone()
        if not producto:
            raise HTTPException(status_code=404, detail="Producto no encontrado")

        # 3. Calcular el total de la compra
        total = producto["precio_unitario"] * compra.cantidad
        
        # 4. Insertar la compra en la base de datos
        cursor.execute(
            """INSERT INTO Compra (id_cliente, codigo_producto, cantidad, total) 
            VALUES (%s, %s, %s, %s)""",
            (compra.id_cliente, compra.codigo_producto, compra.cantidad, total)
        )
        db.commit()  # Confirmar la transacción

        # 5. Obtener la fecha exacta de la compra recién insertada
        cursor.execute(
            """SELECT fecha_compra FROM Compra 
            WHERE id_cliente = %s AND codigo_producto = %s 
            ORDER BY fecha_compra DESC LIMIT 1""",
            (compra.id_cliente, compra.codigo_producto)
        )
        compra_fecha = cursor.fetchone()
        if not compra_fecha:
            raise HTTPException(status_code=500, detail="Error obteniendo fecha de compra")

        # 6. Devolver la compra creada como respuesta
        return CompraResponse(
            cliente=ClienteResponse(**cliente),  # Convertir el diccionario en objeto ClienteResponse
            producto=ProductoResponse(**producto),  # Convertir el diccionario en objeto ProductoResponse
            cantidad=compra.cantidad,
            fecha_compra=compra_fecha["fecha_compra"],
            total=total,
        )

    except Exception as e:
        db.rollback()  # Deshacer cambios en caso de error
        raise HTTPException(status_code=400, detail=str(e))

    finally:
        cursor.close()  # Cerrar el cursor para liberar recursos

@router.get("/", response_model=List[CompraResponse])
def listar_compras(db: mysql.connector.MySQLConnection = Depends(get_db)):
    """
    Endpoint para listar todas las compras registradas en la base de datos.
    Recupera información sobre cada compra, incluyendo detalles del cliente y producto.
    """
    cursor = db.cursor(dictionary=True)
    try:
        # Consultar todas las compras con los detalles del cliente y del producto
        cursor.execute("""
            SELECT 
                c.id_cliente,
                c.codigo_producto,
                c.cantidad,
                c.fecha_compra,
                c.total,  -- Si total es NULL, lo convertimos en 0
                p.codigo AS producto_codigo,
                p.nombre AS producto_nombre,
                p.precio_unitario,
                p.nit_proveedor,
                cli.id AS cliente_id,
                cli.nombre AS cliente_nombre,
                cli.apellidos AS cliente_apellidos,
                cli.direccion AS cliente_direccion,
                cli.fecha_nac AS cliente_fecha_nac
            FROM Compra c
            JOIN Producto p ON c.codigo_producto = p.codigo
            JOIN Cliente cli ON c.id_cliente = cli.id
            ORDER BY c.fecha_compra DESC
        """)
        
        compras = cursor.fetchall()  # Obtener todas las compras en una lista de diccionarios
        respuesta = []  # Lista para almacenar las respuestas formateadas

        for compra in compras:
            # Convertir los datos obtenidos en objetos de respuesta
            compra_respuesta = CompraResponse(
                cliente=ClienteResponse(
                    id=compra["cliente_id"],
                    nombre=compra["cliente_nombre"],
                    apellidos=compra["cliente_apellidos"],
                    direccion=compra["cliente_direccion"],
                    fecha_nac=compra["cliente_fecha_nac"]
                ),
                producto=ProductoBase(
                    codigo=compra["producto_codigo"],
                    nombre=compra["producto_nombre"],
                    precio_unitario=compra["precio_unitario"],
                    nit_proveedor=compra["nit_proveedor"]  
                ),
                cantidad=compra["cantidad"],
                fecha_compra=compra["fecha_compra"],
                total=float(compra["total"])  # Asegurar que sea float
            )
            respuesta.append(compra_respuesta)  # Agregar la compra formateada a la respuesta

        return respuesta  # Retornar la lista de compras

    finally:
        cursor.close()  # Cerrar el cursor para liberar recursos
