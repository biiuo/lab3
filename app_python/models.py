from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ClienteBase(BaseModel):
    nombre: str
    apellidos: str
    direccion: str
    fecha_nac: datetime  # Usar datetime para coincidir con la BD

class ClienteCreate(ClienteBase):
    pass

class ClienteResponse(ClienteBase):
    id: int
    class Config:
        from_attributes = True  # Para ORM

class ProveedorBase(BaseModel):
    nit: str
    nombre: str
    direccion: str

class ProveedorResponse(ProveedorBase):
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    precio_unitario: float
    nit_proveedor: str  # Coincide con el nombre de la columna en BD

class ProductoResponse(ProductoBase):
    class Config:
        from_attributes = True

class CompraBase(BaseModel):
    cantidad: int
    fecha_compra: Optional[datetime] = None  # Opcional porque tiene DEFAULT en BD

class CompraCreate(CompraBase):
    id_cliente: int
    codigo_producto: str

class CompraResponse(CompraBase):
    id: int
    cliente: ClienteResponse  # Relación anidada
    producto: ProductoBase    # Relación anidada