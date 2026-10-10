from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.precio import Precio
from app.models.material import Material
from app.schemas.precio import PrecioCreate, PrecioUpdate, PrecioOut
from app.security import require_admin

# Todos los endpoints de precios ahora requieren autenticación
router = APIRouter(
    prefix="/api/precios",
    tags=["Precios Vigentes (Solo Admin)"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_model=List[PrecioOut])
def listar_precios(db: Session = Depends(get_db)):
    """Lista todos los precios actuales vigentes de compra y venta (Solo Administrador)."""
    return db.query(Precio).all()

@router.get("/{codigo}", response_model=PrecioOut)
def obtener_precio(codigo: str, db: Session = Depends(get_db)):
    """Obtiene los precios actuales vigentes de un material (Solo Administrador)."""
    precio = db.query(Precio).filter(Precio.codigo == codigo).first()
    if not precio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay precios asignados para el material '{codigo}'."
        )
    return precio

@router.post("", response_model=PrecioOut, status_code=status.HTTP_201_CREATED)
def fijar_precio_inicial(payload: PrecioCreate, db: Session = Depends(get_db)):
    """
    Fija el precio inicial de un material (Solo Administrador).
    El trigger de PostgreSQL registrará automáticamente la primera tupla en ambos históricos.
    """
    material = db.query(Material).filter(Material.codigo == payload.codigo).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El material con código '{payload.codigo}' no existe."
        )

    existente = db.query(Precio).filter(Precio.codigo == payload.codigo).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El material '{payload.codigo}' ya cuenta con precios. Use el endpoint PATCH para actualizar."
        )

    nuevo_precio = Precio(
        codigo=payload.codigo,
        precio_compra=payload.precio_compra,
        precio_venta=payload.precio_venta
    )
    db.add(nuevo_precio)
    try:
        db.commit()
        db.refresh(nuevo_precio)
        return nuevo_precio
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar precio: {str(e.orig)}"
        )

@router.patch("/{codigo}", response_model=PrecioOut)
def actualizar_precio(codigo: str, payload: PrecioUpdate, db: Session = Depends(get_db)):
    """
    Actualiza el precio de compra y/o venta de un material (Solo Administrador).
    PostgreSQL cerrará la vigencia del precio anterior y generará una nueva tupla histórica (SCD Tipo 2).
    """
    precio = db.query(Precio).filter(Precio.codigo == codigo).first()
    if not precio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay precios registrados para el material '{codigo}'."
        )

    if payload.precio_compra is None and payload.precio_venta is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe proporcionar al menos 'precio_compra' o 'precio_venta' para actualizar."
        )

    if payload.precio_compra is not None:
        precio.precio_compra = payload.precio_compra
    if payload.precio_venta is not None:
        precio.precio_venta = payload.precio_venta

    try:
        db.commit()
        db.refresh(precio)
        return precio
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar precio: {str(e.orig)}"
        )
