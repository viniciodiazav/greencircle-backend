from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class PrecioCreate(BaseModel):
    codigo: str = Field(..., description="Código del material existente")
    precio_compra: Decimal = Field(..., ge=0, decimal_places=2, description="Precio actual de compra (>= 0)")
    precio_venta: Decimal = Field(..., ge=0, decimal_places=2, description="Precio actual de venta (>= 0)")

class PrecioUpdate(BaseModel):
    precio_compra: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Nuevo precio de compra")
    precio_venta: Optional[Decimal] = Field(None, ge=0, decimal_places=2, description="Nuevo precio de venta")

class PrecioOut(BaseModel):
    codigo: str
    precio_compra: Decimal
    precio_venta: Decimal
    actualizado_en: datetime

    model_config = ConfigDict(from_attributes=True)
