from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class Precio(Base):
    __tablename__ = "precios"

    codigo = Column(String(50), ForeignKey("materiales.codigo", ondelete="CASCADE"), primary_key=True)
    precio_venta = Column(Numeric(12, 2), nullable=False)
    precio_compra = Column(Numeric(12, 2), nullable=False)
    actualizado_en = Column(DateTime(timezone=True), nullable=False, server_default=func.current_timestamp())

    material = relationship("Material", back_populates="precio")
