from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MaterialPublicoOut(BaseModel):
    """Vista pública: únicamente nombre y precio del material."""
    nombre: str
    precio: Optional[Decimal] = None

    model_config = ConfigDict(from_attributes=True)

class SucursalPublicoOut(BaseModel):
    """Vista pública: únicamente nombre y url de la sucursal."""
    nombre: str
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
