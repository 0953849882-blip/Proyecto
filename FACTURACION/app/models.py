from sqlalchemy import String, Float, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date
from .database import Base

class FacturaProveedor(Base):
    __tablename__ = "facturas_proveedor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    proveedor_id: Mapped[str] = mapped_column(String(50))
    nombre_proveedor: Mapped[str] = mapped_column(String(120))

    monto: Mapped[float] = mapped_column(Float)
    fecha_emision: Mapped[date] = mapped_column(Date)
    fecha_vencimiento: Mapped[date] = mapped_column(Date)

    estado: Mapped[str] = mapped_column(String(20), default="PENDIENTE")  # PENDIENTE|PAGADA|ANULADA
    referencia: Mapped[str] = mapped_column(String(80), default="")
    pago_id: Mapped[str] = mapped_column(String(80), default="")  # se llena cuando se paga

    creado_por: Mapped[str] = mapped_column(String(80), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
