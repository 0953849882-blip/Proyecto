import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import Depends
from .auth_guard import require_user


from .database import Base, engine, get_db
from .models import FacturaProveedor
from .schemas import FacturaCreate, FacturaUpdate, FacturaOut, FacturaEstadoUpdate

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio Facturación (Proveedor)")

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins] if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok", "service": "facturacion"}

@app.post("/facturas", response_model=FacturaOut)
def crear_factura(data: FacturaCreate, db: Session = Depends(get_db), user=Depends(require_user)):
    factura = FacturaProveedor(**data.model_dump())
    factura.creado_por = user
    db.add(factura)
    db.commit()
    db.refresh(factura)
    return factura


@app.get("/facturas", response_model=list[FacturaOut])
def listar_facturas(db: Session = Depends(get_db)):
    rows = db.execute(select(FacturaProveedor).order_by(FacturaProveedor.id.desc())).scalars().all()
    return rows

@app.get("/facturas/{factura_id}", response_model=FacturaOut)
def obtener_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = db.get(FacturaProveedor, factura_id)
    if not factura:
        raise HTTPException(404, "Factura no encontrada")
    return factura

@app.put("/facturas/{factura_id}", response_model=FacturaOut)
def actualizar_factura(factura_id: int, data: FacturaUpdate, db: Session = Depends(get_db)):
    factura = db.get(FacturaProveedor, factura_id)
    if not factura:
        raise HTTPException(404, "Factura no encontrada")

    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(factura, k, v)

    db.commit()
    db.refresh(factura)
    return factura

@app.patch("/facturas/{factura_id}/estado", response_model=FacturaOut)
def cambiar_estado_factura(factura_id: int, data: FacturaEstadoUpdate, db: Session = Depends(get_db)):
    factura = db.get(FacturaProveedor, factura_id)
    if not factura:
        raise HTTPException(404, "Factura no encontrada")

    factura.estado = data.estado
    factura.pago_id = data.pago_id or ""
    db.commit()
    db.refresh(factura)
    return factura

@app.delete("/facturas/{factura_id}")
def eliminar_factura(factura_id: int, db: Session = Depends(get_db)):
    factura = db.get(FacturaProveedor, factura_id)
    if not factura:
        raise HTTPException(404, "Factura no encontrada")
    db.delete(factura)
    db.commit()
    return {"deleted": True, "id": factura_id}
