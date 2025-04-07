from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configurar Jinja2 para renderizar HTML
templates = Jinja2Templates(directory="templates")

# Ruta para renderizar el HTML principal
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("Index.html", {"request": request, "active_page": "index"})

# Rutas para cada sección con nombres de función únicos
@app.get("/clientes", response_class=HTMLResponse)
async def read_clientes(request: Request):
    return templates.TemplateResponse("Clientes.html", {"request": request, "active_page": "clientes"})

@app.get("/productos", response_class=HTMLResponse)
async def read_productos(request: Request):
    return templates.TemplateResponse("Productos.html", {"request": request, "active_page": "productos"})

@app.get("/proveedores", response_class=HTMLResponse)
async def read_proveedores(request: Request):
    return templates.TemplateResponse("Proveedores.html", {"request": request, "active_page": "proveedores"})

@app.get("/pedidos", response_class=HTMLResponse)
async def read_pedidos(request: Request):
    return templates.TemplateResponse("Pedidos.html", {"request": request, "active_page": "pedidos"})

@app.get("/consultas", response_class=HTMLResponse)
async def read_consultas(request: Request):
    return templates.TemplateResponse("Consultas.html", {"request": request, "active_page": "consultas"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)