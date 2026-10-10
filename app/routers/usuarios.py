from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdateActivo, UsuarioOut
from app.security import require_admin, hash_password

router = APIRouter(prefix="/api/usuarios", tags=["Usuarios (Solo Administrador)"])

@router.get("", response_model=List[UsuarioOut], dependencies=[Depends(require_admin)])
def listar_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    es_admin: Optional[bool] = Query(None, description="Filtrar por rol admin"),
    solo_activos: Optional[bool] = Query(None, description="Filtrar por estado activo"),
    db: Session = Depends(get_db)
):
    """Obtiene la lista paginada de usuarios registrados (Solo Admin)."""
    query = db.query(Usuario)
    if es_admin is not None:
        query = query.filter(Usuario.admin == es_admin)
    if solo_activos is not None:
        query = query.filter(Usuario.activo == solo_activos)
    return query.offset(skip).limit(limit).all()

@router.get("/{usuario_id}", response_model=UsuarioOut, dependencies=[Depends(require_admin)])
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene el detalle de un usuario por su ID (Solo Admin)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {usuario_id} no encontrado."
        )
    return usuario

@router.post("", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db)):
    """
    Registra un nuevo usuario en el sistema (Solo Admin).
    Si se crea un administrador, el nombre de usuario y la contraseña son obligatorios.
    """
    usuario_limpio = payload.usuario.strip().lower() if payload.usuario else None

    if payload.admin:
        if not usuario_limpio or not payload.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Para crear un Administrador, el nombre de 'usuario' y la 'contraseña' son obligatorios."
            )

    if usuario_limpio:
        existente = db.query(Usuario).filter(Usuario.usuario.ilike(usuario_limpio)).first()
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un usuario con el nombre de usuario '{usuario_limpio}'."
            )

    password_hashed = hash_password(payload.password) if payload.password else None

    nuevo_usuario = Usuario(
        nombre=payload.nombre.strip(),
        apellido=payload.apellido.strip(),
        usuario=usuario_limpio,
        password_hash=password_hashed,
        admin=payload.admin,
        activo=payload.activo
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.patch("/{usuario_id}/activo", response_model=UsuarioOut, dependencies=[Depends(require_admin)])
def actualizar_estado_activo_usuario(
    usuario_id: int,
    payload: UsuarioUpdateActivo,
    db: Session = Depends(get_db)
):
    """
    Activa o desactiva un usuario (Solo Admin).
    Regla: Los usuarios NO se eliminan, únicamente se activan o desactivan.
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Usuario con id {usuario_id} no encontrado."
        )
    usuario.activo = payload.activo
    db.commit()
    db.refresh(usuario)
    return usuario
