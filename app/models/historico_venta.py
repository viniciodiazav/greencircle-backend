from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from app.database import Base

class HistoricoPrecioVenta(Base):
    __tablename__ = "historico_precios_venta"

    id = Column(String(50), primary_key=True)
    codigo_material = Column(String(50), ForeignKey("materiales.codigo", ondelete="CASCADE"), nullable=False)
    precio = Column(Numeric(12, 2), nullable=False)
    creado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())
    vigente_hasta = Column(DateTime(timezone=True), nullable=True)
