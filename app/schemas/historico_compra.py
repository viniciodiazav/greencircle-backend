from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict

class HistoricoPrecioCompraOut(BaseModel):
    id: str
    codigo_material: str
    precio: Decimal
    creado_en: datetime
    vigente_hasta: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
