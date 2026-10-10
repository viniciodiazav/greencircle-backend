from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del usuario")
    usuario: Optional[str] = Field(None, min_length=3, max_length=100, description="Nombre de usuario (login)")
    admin: bool = Field(False, description="True para Admin PC, False para Cliente Móvil")
    activo: bool = Field(True, description="True si está activo, False si está desactivado")

class UsuarioCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del usuario")
    apellido: str = Field(..., min_length=1, max_length=100, description="Apellido del usuario")
    usuario: Optional[str] = Field(None, min_length=3, max_length=100, description="Nombre de usuario para login")
    password: Optional[str] = Field(None, min_length=3, description="Contraseña de acceso (obligatoria si es admin)")
    admin: bool = Field(False, description="True para Admin PC, False para Cliente Móvil")
    activo: bool = Field(True, description="True para activar por defecto al crear")

class UsuarioUpdateActivo(BaseModel):
    activo: bool = Field(..., description="Nuevo estado activo (activar/desactivar usuario)")

class UsuarioOut(BaseModel):
    id: int
    nombre: str
    apellido: str
    usuario: Optional[str] = None
    admin: bool
    activo: bool
    creado_en: datetime

    model_config = ConfigDict(from_attributes=True)
