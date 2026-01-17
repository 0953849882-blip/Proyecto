from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional

class PagoCreate(BaseModel):
    factura_id: int = Field(..., gt=0)
    metodo_pago: str = "Transferencia"
    referencia: str = ""
    fecha_pago: date
    creado_por: str = "system"

class PagoOut(BaseModel):
    id: int
    factura_id: int
    proveedor_id: str
    nombre_proveedor: str
    monto: float
    fecha_pago: date
    metodo_pago: str
    referencia: str
    estado: str
    creado_por: str
    created_at: datetime

    model_config = {"from_attributes": True}

class FacturaMini(BaseModel):
    id: int
    proveedor_id: str
    nombre_proveedor: str
    monto: float
    estado: str
