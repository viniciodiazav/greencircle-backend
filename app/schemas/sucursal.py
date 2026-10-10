from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class SucursalBase(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=150, description="Nombre de la sucursal")
    url: Optional[str] = Field(None, description="URL o enlace web/mapa")

class SucursalCreate(SucursalBase):
    pass

class SucursalUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=150, description="Nombre de la sucursal")
    url: Optional[str] = Field(None, description="URL o enlace web/mapa")

class SucursalOut(SucursalBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
