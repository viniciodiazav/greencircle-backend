from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdateActivo, MaterialOut
from app.security import require_admin

# Todos los endpoints de materiales ahora requieren autenticación
router = APIRouter(
    prefix="/api/materiales",
    tags=["Materiales (Solo Admin)"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_model=List[MaterialOut])
def listar_materiales(
    solo_activos: Optional[bool] = Query(None, description="Filtrar solo materiales activos"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Lista todos los materiales del catálogo completo (Solo Administrador)."""
    query = db.query(Material)
    if solo_activos is not None:
        query = query.filter(Material.activo == solo_activos)
    return query.offset(skip).limit(limit).all()

@router.get("/{codigo}", response_model=MaterialOut)
def obtener_material(codigo: str, db: Session = Depends(get_db)):
    """Obtiene el material detallado por su código algorítmico (Solo Administrador)."""
    material = db.query(Material).filter(Material.codigo == codigo).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con código '{codigo}' no encontrado."
        )
    return material

@router.post("", response_model=MaterialOut, status_code=status.HTTP_201_CREATED)
def crear_material(payload: MaterialCreate, db: Session = Depends(get_db)):
    """
    Crea un material nuevo (Solo Administrador).
    El código algorítmico y la fecha son autogenerados por triggers en PostgreSQL.
    """
    existente = db.query(Material).filter(Material.nombre.ilike(payload.nombre.strip())).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un material con el nombre '{payload.nombre}' (código: {existente.codigo})."
        )

    nuevo_material = Material(
        nombre=payload.nombre.strip(),
        activo=payload.activo
    )
    db.add(nuevo_material)
    try:
        db.commit()
        db.refresh(nuevo_material)
        return nuevo_material
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de integridad al registrar material: {str(e.orig)}"
        )

@router.patch("/{codigo}/activo", response_model=MaterialOut)
def actualizar_estado_activo_material(
    codigo: str,
    payload: MaterialUpdateActivo,
    db: Session = Depends(get_db)
):
    """
    Activa o desactiva un material (Solo Administrador).
    Regla: Los materiales no se eliminan jamás.
    """
    material = db.query(Material).filter(Material.codigo == codigo).first()
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Material con código '{codigo}' no encontrado."
        )

    material.activo = payload.activo
    db.commit()
    db.refresh(material)
    return material
