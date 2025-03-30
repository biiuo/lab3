from fastapi import FastAPI
import uvicorn
from routes.cliente import router as cliente_router
from routes.proveedor import router as proveedor_router
from routes.producto import router as producto_router
from routes.compra import router as compra_router



app = FastAPI(title="API DE VENTAS")

app.include_router(cliente_router, prefix="/api")
app.include_router(proveedor_router, prefix="/api")
app.include_router(producto_router, prefix="/api")
app.include_router(compra_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de ventas"}

if __name__ == "__main__":
      uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
