# Importamos BaseModel de Pydantic para la validación de datos
from pydantic import BaseModel
# Importamos datetime y date para manejar fechas
from datetime import datetime, date
# Importamos Optional para definir atributos opcionales en los modelos
from typing import Optional

# ---------------------------- MODELO CLIENTE ----------------------------

# Modelo base para un Cliente
class ClienteBase(BaseModel):
    nombre: str        # Nombre del cliente
    apellidos: str     # Apellidos del cliente
    direccion: str     # Dirección del cliente
    fecha_nac: date    # Fecha de nacimiento del cliente (usa `date` para coincidir con la base de datos)

# Modelo para la creación de un Cliente (se hereda de ClienteBase sin modificaciones)
class ClienteCreate(ClienteBase):
    pass  # No se agregan nuevos atributos, solo se reutiliza el modelo base

# Modelo de respuesta para un Cliente (se usa al devolver datos)
class ClienteResponse(ClienteBase):
    id: int  # Se añade el ID del cliente, que es asignado por la base de datos

    class Config:
        from_attributes = True  # Permite convertir datos obtenidos de la base de datos a un objeto Pydantic

# ---------------------------- MODELO PROVEEDOR ----------------------------

# Modelo base para un Proveedor
class ProveedorBase(BaseModel):
    nit: str       # Número de Identificación Tributaria del proveedor
    nombre: str    # Nombre del proveedor
    direccion: str # Dirección del proveedor

# Modelo de respuesta para un Proveedor (sin modificaciones adicionales)
class ProveedorResponse(ProveedorBase):
    class Config:
        from_attributes = True  # Habilita la conversión de datos desde la base de datos

# ---------------------------- MODELO PRODUCTO ----------------------------

# Modelo base para un Producto
class ProductoBase(BaseModel):
    codigo: str          # Código único del producto
    nombre: str          # Nombre del producto
    precio_unitario: float # Precio unitario del producto
    nit_proveedor: str   # Relación con el proveedor del producto (clave foránea)

# Modelo de respuesta para un Producto (se hereda sin modificaciones)
class ProductoResponse(ProductoBase):
    class Config:
        from_attributes = True  # Permite conversión automática desde la base de datos

# ---------------------------- MODELO COMPRA ----------------------------

# Modelo para la creación de una Compra
class CompraCreate(BaseModel):
    id_cliente: int       # ID del cliente que realiza la compra (clave foránea)
    codigo_producto: str  # Código del producto comprado (clave foránea)
    cantidad: int         # Cantidad de productos comprados

# Modelo de respuesta para una Compra
class CompraResponse(BaseModel):
    cliente: ClienteResponse   # Información del cliente que realizó la compra
    producto: ProductoResponse # Información del producto comprado
    cantidad: int              # Cantidad comprada
    total: float               # Total calculado (precio * cantidad)
    fecha_compra: Optional[datetime] = None  # Fecha en la que se realizó la compra (puede ser opcional)

