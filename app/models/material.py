from sqlalchemy import Column, String, Boolean, Date, func, FetchedValue
from sqlalchemy.orm import relationship
from app.database import Base

class Material(Base):
    __tablename__ = "materiales"

    # server_default=FetchedValue() indica a SQLAlchemy que la PK se genera en PostgreSQL via trigger
    codigo = Column(String(50), primary_key=True, server_default=FetchedValue())
    nombre = Column(String(100), unique=True, nullable=False)
    fecha_creacion = Column(Date, nullable=False, server_default=func.current_date())
    activo = Column(Boolean, nullable=False, default=False)

    # Relación 1 a 1 con precios
    precio = relationship("Precio", back_populates="material", uselist=False, cascade="all, delete-orphan")
