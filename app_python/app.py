# Importamos FastAPI para crear nuestra API
from fastapi import FastAPI
# Importamos uvicorn para ejecutar el servidor
import uvicorn
# Importamos los routers (módulos de rutas) de las distintas entidades
from routes.cliente import router as cliente_router
from routes.proveedor import router as proveedor_router
from routes.producto import router as producto_router
from routes.compra import router as compra_router

# Creamos una instancia de FastAPI con un título descriptivo
app = FastAPI(title="API DE VENTAS")

# Incluimos los routers en la aplicación principal con un prefijo "/api"
app.include_router(cliente_router, prefix="/api")  # Rutas relacionadas con clientes
app.include_router(proveedor_router, prefix="/api")  # Rutas relacionadas con proveedores
app.include_router(producto_router, prefix="/api")  # Rutas relacionadas con productos
app.include_router(compra_router, prefix="/api")  # Rutas relacionadas con compras

# Definimos la ruta raíz de la API
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de ventas"}  # Mensaje de bienvenida cuando el usuario accede a la raíz

# Verificamos si el script se ejecuta directamente
if __name__ == "__main__":
    # Iniciamos el servidor Uvicorn para ejecutar la API en el puerto 8000
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
    # "app:app" indica que Uvicorn ejecutará la variable `app` en este archivo
    # `host="127.0.0.1"` hace que la API solo sea accesible en la máquina local
    # `port=8000` especifica el puerto en el que correrá la API
    # `reload=True` permite la recarga automática en caso de cambios en el código
