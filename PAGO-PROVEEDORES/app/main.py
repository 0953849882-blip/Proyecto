import os
import httpx
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select

from fastapi import Depends
from .auth_guard import require_user

from .database import Base, engine, get_db
from .models import PagoProveedor
from .schemas import PagoCreate, PagoOut, FacturaMini

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Microservicio Pago a Proveedores")


origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins] if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FACTURACION_URL = os.getenv("FACTURACION_URL", "http://localhost:8001")  

@app.get("/health")
def health():
    return {"status": "ok", "service": "pagos", "facturacion_url": FACTURACION_URL}

async def obtener_factura(factura_id: int) -> FacturaMini:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{FACTURACION_URL}/facturas/{factura_id}")
    if r.status_code == 404:
        raise HTTPException(400, "La factura no existe en Facturación")
    if r.status_code != 200:
        raise HTTPException(502, "No se pudo consultar Facturación")
    data = r.json()
    return FacturaMini(
        id=data["id"],
        proveedor_id=data["proveedor_id"],
        nombre_proveedor=data["nombre_proveedor"],
        monto=data["monto"],
        estado=data["estado"],
    )

async def marcar_factura_pagada(factura_id: int, pago_id: str):
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.patch(
            f"{FACTURACION_URL}/facturas/{factura_id}/estado",
            json={"estado": "PAGADA", "pago_id": pago_id},
        )
    if r.status_code != 200:
        raise HTTPException(502, "No se pudo actualizar el estado en Facturación")

@app.post("/pagos", response_model=PagoOut)
async def crear_pago(data: PagoCreate, db: Session = Depends(get_db), user=Depends(require_user)):

    factura = await obtener_factura(data.factura_id)

    if factura.estado != "PENDIENTE":
        raise HTTPException(400, f"No se puede pagar: estado actual = {factura.estado}")


    pago = PagoProveedor(
        factura_id=data.factura_id,
        proveedor_id=factura.proveedor_id,
        nombre_proveedor=factura.nombre_proveedor,
        monto=factura.monto,
        fecha_pago=data.fecha_pago,
        metodo_pago=data.metodo_pago,
        referencia=data.referencia,
        estado="CONFIRMADO",
        creado_por=user,
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)


    await marcar_factura_pagada(data.factura_id, str(pago.id))

    return pago

@app.get("/pagos", response_model=list[PagoOut])
def listar_pagos(db: Session = Depends(get_db)):
    rows = db.execute(select(PagoProveedor).order_by(PagoProveedor.id.desc())).scalars().all()
    return rows

@app.get("/pagos/{pago_id}", response_model=PagoOut)
def obtener_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.get(PagoProveedor, pago_id)
    if not pago:
        raise HTTPException(404, "Pago no encontrado")
    return pago

@app.delete("/pagos/{pago_id}")
def eliminar_pago(pago_id: int, db: Session = Depends(get_db)):
    pago = db.get(PagoProveedor, pago_id)
    if not pago:
        raise HTTPException(404, "Pago no encontrado")
    db.delete(pago)
    db.commit()
    return {"deleted": True, "id": pago_id}
