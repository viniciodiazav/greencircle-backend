from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.sucursal import Sucursal
from app.schemas.sucursal import SucursalCreate, SucursalUpdate, SucursalOut
from app.security import require_admin

# Todos los endpoints de sucursales ahora requieren autenticación
router = APIRouter(
    prefix="/api/sucursales",
    tags=["Sucursales (Solo Admin)"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_model=List[SucursalOut])
def listar_sucursales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Obtiene la lista completa de sucursales con IDs (Solo Administrador)."""
    return db.query(Sucursal).offset(skip).limit(limit).all()

@router.get("/{sucursal_id}", response_model=SucursalOut)
def obtener_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de una sucursal por su identificador (Solo Administrador)."""
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sucursal con id {sucursal_id} no encontrada."
        )
    return sucursal

@router.post("", response_model=SucursalOut, status_code=status.HTTP_201_CREATED)
def crear_sucursal(payload: SucursalCreate, db: Session = Depends(get_db)):
    """Registra una nueva sucursal (Solo Administrador)."""
    nueva_sucursal = Sucursal(
        nombre=payload.nombre.strip(),
        url=payload.url.strip() if payload.url else None
    )
    db.add(nueva_sucursal)
    db.commit()
    db.refresh(nueva_sucursal)
    return nueva_sucursal

@router.patch("/{sucursal_id}", response_model=SucursalOut)
def actualizar_sucursal(
    sucursal_id: int,
    payload: SucursalUpdate,
    db: Session = Depends(get_db)
):
    """Actualiza los datos de una sucursal existente (Solo Administrador)."""
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sucursal con id {sucursal_id} no encontrada."
        )

    if payload.nombre is not None:
        sucursal.nombre = payload.nombre.strip()
    if payload.url is not None:
        sucursal.url = payload.url.strip() if payload.url else None

    db.commit()
    db.refresh(sucursal)
    return sucursal

@router.delete("/{sucursal_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_sucursal(sucursal_id: int, db: Session = Depends(get_db)):
    """
    Elimina una sucursal del sistema (Solo Administrador).
    Única entidad en toda la plataforma que permite eliminación física.
    """
    sucursal = db.query(Sucursal).filter(Sucursal.id == sucursal_id).first()
    if not sucursal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sucursal con id {sucursal_id} no encontrada."
        )
    db.delete(sucursal)
    db.commit()
    return None
