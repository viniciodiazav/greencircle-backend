from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class MaterialCreate(BaseModel):
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre único del material")
    activo: bool = Field(False, description="Estado de disponibilidad para clientes")

class MaterialUpdateActivo(BaseModel):
    activo: bool = Field(..., description="Nuevo estado activo (único campo mutable)")

class MaterialOut(BaseModel):
    codigo: str
    nombre: str
    fecha_creacion: date
    activo: bool

    model_config = ConfigDict(from_attributes=True)

class MaterialCatalogoPublicoOut(BaseModel):
    """Vista pública para clientes: solo materiales activos con su precio de compra."""
    codigo: str
    nombre: str
    precio_compra: Optional[Decimal] = Field(None, description="Precio al que el centro compra el material al cliente")
    actualizado_en: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
