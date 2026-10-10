from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Engine de SQLAlchemy conectado a PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica la conexión antes de emitir queries
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG  # Loguea queries SQL si DEBUG es True
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para modelos ORM
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI que gestiona el ciclo de vida de la sesión de BD."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
