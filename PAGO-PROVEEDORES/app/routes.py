from fastapi import APIRouter
from app.models import PagoProveedor

router = APIRouter(prefix="/pagos", tags=["Pagos"])

pagos = []

@router.post("/")
def crear_pago(pago: PagoProveedor):
    pagos.append(pago)
    return pago

@router.get("/")
def listar_pagos():
    return pagos
