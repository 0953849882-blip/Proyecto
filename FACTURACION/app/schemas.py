from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Literal

EstadoFactura = Literal["PENDIENTE", "PAGADA", "ANULADA"]

class FacturaCreate(BaseModel):
    proveedor_id: str = Field(..., min_length=1)
    nombre_proveedor: str = Field(..., min_length=1)
    monto: float = Field(..., gt=0)
    fecha_emision: date
    fecha_vencimiento: date
    referencia: str = ""
    creado_por: str = "system"

class FacturaUpdate(BaseModel):
    proveedor_id: Optional[str] = None
    nombre_proveedor: Optional[str] = None
    monto: Optional[float] = Field(default=None, gt=0)
    fecha_emision: Optional[date] = None
    fecha_vencimiento: Optional[date] = None
    referencia: Optional[str] = None
    creado_por: Optional[str] = None

class FacturaEstadoUpdate(BaseModel):
    estado: EstadoFactura
    pago_id: Optional[str] = ""

class FacturaOut(BaseModel):
    id: int
    proveedor_id: str
    nombre_proveedor: str
    monto: float
    fecha_emision: date
    fecha_vencimiento: date
    estado: str
    referencia: str
    pago_id: str
    creado_por: str
    created_at: datetime

    model_config = {"from_attributes": True}
