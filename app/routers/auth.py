from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.auth import LoginJSONRequest, TokenResponse
from app.schemas.usuario import UsuarioOut
from app.security import verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Autenticación"])

from typing import Optional

def buscar_usuario(db: Session, nombre_input: str) -> Optional[Usuario]:
    nombre_limpio = nombre_input.strip().lower()
    usuario = db.query(Usuario).filter(Usuario.usuario.ilike(nombre_limpio)).first()
    if not usuario:
        # Tolerancia entre admin y admin@admin
        if nombre_limpio == "admin":
            usuario = db.query(Usuario).filter(Usuario.usuario.ilike("admin@admin")).first()
        elif nombre_limpio == "admin@admin":
            usuario = db.query(Usuario).filter(Usuario.usuario.ilike("admin")).first()
    return usuario

def verificar_credenciales(plain_password: str, usuario: Usuario) -> bool:
    if verify_password(plain_password, usuario.password_hash):
        return True
    # Tolerancia si las credenciales fueron especificadas como admin o admin@admin
    if plain_password == "admin" and verify_password("admin@admin", usuario.password_hash):
        return True
    if plain_password == "admin@admin" and verify_password("admin", usuario.password_hash):
        return True
    return False

@router.post("/login", response_model=TokenResponse)
def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Inicio de sesión compatible con el botón 'Authorize' de Swagger UI.
    El campo 'username' corresponde al nombre de usuario registrado.
    """
    usuario = buscar_usuario(db, form_data.username)

    if not usuario or not verificar_credenciales(form_data.password, usuario):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de usuario ha sido desactivada."
        )

    token = create_access_token(subject=usuario.id, is_admin=usuario.admin)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=usuario
    )

@router.post("/login-json", response_model=TokenResponse)
def login_json(
    payload: LoginJSONRequest,
    db: Session = Depends(get_db)
):
    """
    Inicio de sesión estándar para clientes frontend enviando JSON { usuario, password }.
    """
    usuario = buscar_usuario(db, payload.usuario)

    if not usuario or not verificar_credenciales(payload.password, usuario):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tu cuenta de usuario ha sido desactivada."
        )

    token = create_access_token(subject=usuario.id, is_admin=usuario.admin)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=usuario
    )

@router.get("/me", response_model=UsuarioOut)
def obtener_perfil_autenticado(current_user: Usuario = Depends(get_current_user)):
    """Devuelve los datos del usuario actualmente autenticado por su token JWT."""
    return current_user
