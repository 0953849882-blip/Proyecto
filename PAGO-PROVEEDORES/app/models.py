from sqlalchemy import String, Float, Date, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, date
from .database import Base

class PagoProveedor(Base):
    __tablename__ = "pagos_proveedor"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    factura_id: Mapped[int] = mapped_column(Integer)  
    proveedor_id: Mapped[str] = mapped_column(String(50))
    nombre_proveedor: Mapped[str] = mapped_column(String(120))

    monto: Mapped[float] = mapped_column(Float)
    fecha_pago: Mapped[date] = mapped_column(Date)

    metodo_pago: Mapped[str] = mapped_column(String(30), default="Transferencia")
    referencia: Mapped[str] = mapped_column(String(80), default="")
    estado: Mapped[str] = mapped_column(String(20), default="CONFIRMADO")  

    creado_por: Mapped[str] = mapped_column(String(80), default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
