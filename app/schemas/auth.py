from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.usuario import UsuarioOut

class LoginJSONRequest(BaseModel):
    """Esquema para login mediante JSON estándar { usuario, password }."""
    usuario: str = Field(..., description="Nombre de usuario registrado")
    password: str = Field(..., description="Contraseña del usuario")

class TokenResponse(BaseModel):
    """Respuesta con token JWT de acceso."""
    access_token: str
    token_type: str = "bearer"
    user: UsuarioOut
