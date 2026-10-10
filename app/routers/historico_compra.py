from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.historico_compra import HistoricoPrecioCompra
from app.schemas.historico_compra import HistoricoPrecioCompraOut
from app.security import require_admin

# Historial contable accesible únicamente por administradores
router = APIRouter(
    prefix="/api/historicos-compra",
    tags=["Histórico Precios Compra (Solo Administrador)"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_model=List[HistoricoPrecioCompraOut])
def listar_historico_compra(
    codigo_material: Optional[str] = Query(None, description="Filtrar por código de material"),
    solo_vigentes: Optional[bool] = Query(None, description="Filtrar precios activos actualmente (vigente_hasta IS NULL)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Consulta cronológica del histórico de precios de compra (Solo Admin).
    Inmutable y de solo lectura.
    """
    query = db.query(HistoricoPrecioCompra)
    if codigo_material:
        query = query.filter(HistoricoPrecioCompra.codigo_material == codigo_material)
    if solo_vigentes is True:
        query = query.filter(HistoricoPrecioCompra.vigente_hasta.is_(None))
    elif solo_vigentes is False:
        query = query.filter(HistoricoPrecioCompra.vigente_hasta.isnot(None))

    return query.order_by(HistoricoPrecioCompra.creado_en.desc()).offset(skip).limit(limit).all()

@router.get("/vigente/{codigo_material}", response_model=HistoricoPrecioCompraOut)
def obtener_precio_compra_vigente(codigo_material: str, db: Session = Depends(get_db)):
    """Obtiene el registro histórico activo actual de compra para un material (Solo Admin)."""
    registro = db.query(HistoricoPrecioCompra)\
                 .filter(HistoricoPrecioCompra.codigo_material == codigo_material,
                         HistoricoPrecioCompra.vigente_hasta.is_(None))\
                 .first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró precio de compra vigente para el material '{codigo_material}'."
        )
    return registro

@router.get("/{id}", response_model=HistoricoPrecioCompraOut)
def obtener_registro_historico_compra(id: str, db: Session = Depends(get_db)):
    """Obtiene un registro histórico específico por su ID compuesto (ej: '1-2026') (Solo Admin)."""
    registro = db.query(HistoricoPrecioCompra).filter(HistoricoPrecioCompra.id == id).first()
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Registro histórico con id '{id}' no encontrado."
        )
    return registro
