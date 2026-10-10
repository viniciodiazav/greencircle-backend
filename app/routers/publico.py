from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.material import Material
from app.models.precio import Precio
from app.models.sucursal import Sucursal
from app.schemas.publico import MaterialPublicoOut, SucursalPublicoOut

router = APIRouter(prefix="/api/publico", tags=["Público (Sin Autenticación)"])

@router.get("/materiales", response_model=List[MaterialPublicoOut])
def listar_materiales_publico(db: Session = Depends(get_db)):
    """
    Vista pública para clientes (sin autenticación).
    Devuelve ÚNICAMENTE el nombre del material y su precio de compra.
    """
    resultados = (
        db.query(
            Material.nombre,
            Precio.precio_compra.label("precio")
        )
        .outerjoin(Precio, Material.codigo == Precio.codigo)
        .filter(Material.activo == True)
        .all()
    )
    return [MaterialPublicoOut(nombre=r.nombre, precio=r.precio) for r in resultados]

@router.get("/sucursales", response_model=List[SucursalPublicoOut])
def listar_sucursales_publico(db: Session = Depends(get_db)):
    """
    Vista pública para clientes (sin autenticación).
    Devuelve ÚNICAMENTE el nombre de la sucursal y su url.
    """
    resultados = db.query(Sucursal.nombre, Sucursal.url).all()
    return [SucursalPublicoOut(nombre=r.nombre, url=r.url) for r in resultados]
