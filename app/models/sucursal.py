from sqlalchemy import Column, BigInteger, String, Text
from app.database import Base

class Sucursal(Base):
    __tablename__ = "sucursales"

    id = Column(BigInteger, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    url = Column(Text, nullable=True)
