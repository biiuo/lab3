from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from db import get_db
import mysql.connector
from datetime import datetime

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==============================================
# Funciones para Clientes
# ==============================================
def obtener_clientes():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id, 
                nombre, 
                apellidos,
                DATE_FORMAT(fecha_nac, '%Y-%m-%d') as fecha_nacimiento,
                direccion
            FROM Cliente
        """)
        clientes = cursor.fetchall()
        cursor.close()
        return clientes
    except Exception as e:
        print(f"Error al obtener clientes: {e}")
        return []
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Funciones para Proveedores
# ==============================================
def obtener_proveedores():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT nit, nombre, direccion FROM Proveedor")
        proveedores = cursor.fetchall()
        cursor.close()
        return proveedores
    except Exception as e:
        print(f"Error al obtener proveedores: {e}")
        return []
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Funciones para Productos
# ==============================================
def obtener_productos():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                p.codigo, 
                p.nombre,
                p.precio_unitario,
                p.nit_proveedor,
                pr.nombre as nombre_proveedor
            FROM Producto p
            JOIN Proveedor pr ON p.nit_proveedor = pr.nit
        """)
        productos = cursor.fetchall()
        cursor.close()
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Funciones para Pedidos (Compra)
# ==============================================
def obtener_pedidos():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                c.id_cliente, 
                cl.nombre as nombre_cliente,
                cl.apellidos,
                c.codigo_producto, 
                p.nombre as nombre_producto,
                c.cantidad,
                DATE_FORMAT(c.fecha_compra, '%Y-%m-%d %H:%i:%s') as fecha_compra
            FROM Compra c
            JOIN Cliente cl ON c.id_cliente = cl.id
            JOIN Producto p ON c.codigo_producto = p.codigo
            ORDER BY c.fecha_compra DESC
        """)
        pedidos = cursor.fetchall()
        cursor.close()
        return pedidos
    except Exception as e:
        print(f"Error al obtener pedidos: {e}")
        return []
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Rutas principales
# ==============================================
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("Index.html", {"request": request, "active_page": "index"})

@app.get("/clientes", response_class=HTMLResponse)
async def read_clientes(request: Request):
    clientes = obtener_clientes()
    return templates.TemplateResponse("Clientes.html", {
        "request": request,
        "active_page": "clientes",
        "clientes": clientes
    })

@app.get("/proveedores", response_class=HTMLResponse)
async def read_proveedores(request: Request):
    proveedores = obtener_proveedores()
    return templates.TemplateResponse("Proveedores.html", {
        "request": request,
        "active_page": "proveedores",
        "proveedores": proveedores
    })

@app.get("/productos", response_class=HTMLResponse)
async def read_productos(request: Request):
    productos = obtener_productos()
    proveedores = obtener_proveedores()
    return templates.TemplateResponse("Productos.html", {
        "request": request,
        "active_page": "productos",
        "productos": productos,
        "proveedores": proveedores
    })

@app.get("/pedidos", response_class=HTMLResponse)
async def read_pedidos(request: Request):
    pedidos = obtener_pedidos()
    clientes = obtener_clientes()
    productos = obtener_productos()
    return templates.TemplateResponse("Pedidos.html", {
        "request": request,
        "active_page": "pedidos",
        "pedidos": pedidos,
        "clientes": clientes,
        "productos": productos
    })

# ==============================================
# CRUD para Clientes
# ==============================================
@app.post("/clientes/agregar")
async def agregar_cliente(
    nombre: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: str = Form(...),
    direccion: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "INSERT INTO Cliente (nombre, apellidos, fecha_nac, direccion) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (nombre, apellidos, fecha_nacimiento, direccion))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al agregar cliente: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/clientes", status_code=303)

@app.post("/clientes/editar/{cliente_id}")
async def editar_cliente(
    cliente_id: int,
    nombre: str = Form(...),
    apellidos: str = Form(...),
    fecha_nacimiento: str = Form(...),
    direccion: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "UPDATE Cliente SET nombre = %s, apellidos = %s, fecha_nac = %s, direccion = %s WHERE id = %s"
        cursor.execute(query, (nombre, apellidos, fecha_nacimiento, direccion, cliente_id))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al editar cliente: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/clientes", status_code=303)

@app.get("/clientes/eliminar/{cliente_id}")
async def eliminar_cliente(cliente_id: int):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "DELETE FROM Cliente WHERE id = %s"
        cursor.execute(query, (cliente_id,))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/clientes", status_code=303)

# ==============================================
# CRUD para Proveedores
# ==============================================
@app.post("/proveedores/agregar")
async def agregar_proveedor(
    nit: str = Form(...),
    nombre: str = Form(...),
    direccion: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "INSERT INTO Proveedor (nit, nombre, direccion) VALUES (%s, %s, %s)"
        cursor.execute(query, (nit, nombre, direccion))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al agregar proveedor: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/proveedores", status_code=303)

@app.post("/proveedores/editar/{nit}")
async def editar_proveedor(
    nit: str,
    nombre: str = Form(...),
    direccion: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "UPDATE Proveedor SET nombre = %s, direccion = %s WHERE nit = %s"
        cursor.execute(query, (nombre, direccion, nit))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al editar proveedor: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/proveedores", status_code=303)

@app.get("/proveedores/eliminar/{nit}")
async def eliminar_proveedor(nit: str):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "DELETE FROM Proveedor WHERE nit = %s"
        cursor.execute(query, (nit,))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al eliminar proveedor: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/proveedores", status_code=303)

# ==============================================
# CRUD para Productos
# ==============================================
@app.post("/productos/agregar")
async def agregar_producto(
    codigo: str = Form(...),
    nombre: str = Form(...),
    precio_unitario: float = Form(...),
    nit_proveedor: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "INSERT INTO Producto (codigo, nombre, precio_unitario, nit_proveedor) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (codigo, nombre, precio_unitario, nit_proveedor))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al agregar producto: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/productos", status_code=303)

@app.post("/productos/editar/{codigo}")
async def editar_producto(
    codigo: str,
    nombre: str = Form(...),
    precio_unitario: float = Form(...),
    nit_proveedor: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "UPDATE Producto SET nombre = %s, precio_unitario = %s, nit_proveedor = %s WHERE codigo = %s"
        cursor.execute(query, (nombre, precio_unitario, nit_proveedor, codigo))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al editar producto: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/productos", status_code=303)

@app.get("/productos/eliminar/{codigo}")
async def eliminar_producto(codigo: str):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = "DELETE FROM Producto WHERE codigo = %s"
        cursor.execute(query, (codigo,))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        mydb.rollback()
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/productos", status_code=303)

# ==============================================
# CRUD para Pedidos
# ==============================================
@app.post("/pedidos/agregar")
async def agregar_pedido(
    id_cliente: int = Form(...),
    codigo_producto: str = Form(...),
    cantidad: int = Form(...),
    fecha_compra: str = Form(...)
):
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = """
            INSERT INTO Compra (id_cliente, codigo_producto, cantidad, fecha_compra)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (id_cliente, codigo_producto, cantidad, fecha_compra))
        mydb.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al agregar pedido: {e}")
        mydb.rollback()
        return RedirectResponse(url="/pedidos?error=Error al agregar pedido", status_code=303)
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
    return RedirectResponse(url="/pedidos", status_code=303)

@app.get("/pedidos/eliminar")
async def eliminar_pedido(
    request: Request,
    id_cliente: int,
    codigo_producto: str,
    fecha_compra: str
):
    try:
        # Convertir la fecha al formato correcto si es necesario
        fecha_compra_obj = datetime.strptime(fecha_compra, '%Y-%m-%d %H:%M:%S')
        fecha_compra_formatted = fecha_compra_obj.strftime('%Y-%m-%d %H:%M:%S')
        
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor()
        
        query = """
            DELETE FROM Compra 
            WHERE id_cliente = %s 
            AND codigo_producto = %s 
            AND fecha_compra = %s
        """
        cursor.execute(query, (id_cliente, codigo_producto, fecha_compra_formatted))
        mydb.commit()
        cursor.close()
        return RedirectResponse(url="/pedidos", status_code=303)
    except Exception as e:
        print(f"Error al eliminar pedido: {e}")
        mydb.rollback()
        return RedirectResponse(url="/pedidos?error=Error al eliminar pedido: " + str(e), status_code=303)
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Otras rutas
# ==============================================
@app.get("/consultas", response_class=HTMLResponse)
async def read_consultas(request: Request):
    return templates.TemplateResponse("Consultas.html", {"request": request, "active_page": "consultas"})

# ==============================================
# Consultas adicionales
# ==============================================
@app.get("/consultas/clientes-pedidos")
async def consulta_clientes_pedidos():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        
        query = """
            SELECT 
                c.id as id_cliente,
                c.nombre,
                c.apellidos,
                COUNT(co.id_cliente) as cantidad_pedidos
            FROM Cliente c
            LEFT JOIN Compra co ON c.id = co.id_cliente
            GROUP BY c.id, c.nombre, c.apellidos
            ORDER BY cantidad_pedidos DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        
        return resultados
    except Exception as e:
        print(f"Error en consulta clientes-pedidos: {e}")
        return {"error": str(e)}
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
            
@app.get("/consultas/clientes-sin-pedidos")
async def consulta_clientes_sin_pedidos():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        
        query = """
            SELECT 
                c.id,
                c.nombre,
                c.apellidos,
                c.direccion
            FROM Cliente c
            LEFT JOIN Compra co ON c.id = co.id_cliente
            WHERE co.id_cliente IS NULL
            ORDER BY c.apellidos, c.nombre
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        
        return resultados
    except Exception as e:
        print(f"Error en consulta clientes-sin-pedidos: {e}")
        return {"error": str(e)}
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
            
@app.get("/consultas/detalle-compras")
async def consulta_detalle_compras():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        
        query = """
            SELECT 
                cl.nombre as nombre_cliente,
                cl.apellidos as apellidos_cliente,
                p.nombre as nombre_producto,
                co.cantidad,
                p.precio_unitario,
                pr.nombre as nombre_proveedor
            FROM Compra co
            JOIN Cliente cl ON co.id_cliente = cl.id
            JOIN Producto p ON co.codigo_producto = p.codigo
            JOIN Proveedor pr ON p.nit_proveedor = pr.nit
            ORDER BY co.fecha_compra DESC
        """
        
        cursor.execute(query)
        resultados = cursor.fetchall()
        cursor.close()
        
        return resultados
    except Exception as e:
        print(f"Error en consulta detalle-compras: {e}")
        return {"error": str(e)}
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()
            
@app.get("/consultas/proveedores-productos")
async def consulta_proveedores_productos():
    try:
        db_gen = get_db()
        mydb = next(db_gen)
        cursor = mydb.cursor(dictionary=True)
        
        # Primero obtenemos todos los proveedores
        cursor.execute("SELECT nit, nombre as nombre_proveedor, direccion FROM Proveedor")
        proveedores = cursor.fetchall()
        
        # Para cada proveedor, obtenemos sus productos
        resultados = []
        for proveedor in proveedores:
            cursor.execute("""
                SELECT codigo, nombre, precio_unitario
                FROM Producto
                WHERE nit_proveedor = %s
                ORDER BY nombre
            """, (proveedor['nit'],))
            productos = cursor.fetchall()
            
            resultados.append({
                'nit': proveedor['nit'],
                'nombre_proveedor': proveedor['nombre_proveedor'],
                'direccion': proveedor['direccion'],
                'productos': productos
            })
        
        cursor.close()
        return resultados
    except Exception as e:
        print(f"Error en consulta proveedores-productos: {e}")
        return {"error": str(e)}
    finally:
        if 'mydb' in locals() and mydb.is_connected():
            mydb.close()

# ==============================================
# Iniciar la aplicación
# ==============================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)