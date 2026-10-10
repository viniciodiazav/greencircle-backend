import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

# Ruta base del backend para localizar siempre el archivo .env
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True

    # Credenciales de conexión a PostgreSQL
    DB_USER: str = "greencircle"
    DB_PASSWORD: str = ""
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "greencircle"

    # Configuración de Seguridad y Tokens JWT
    JWT_SECRET_KEY: str = "greencircle-super-jwt-secret-key-2026-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 horas

    # Administrador inicial para seeding automático
    FIRST_ADMIN_NOMBRE: str = "Admin"
    FIRST_ADMIN_APELLIDO: str = "GreenCircle"
    FIRST_ADMIN_USUARIO: str = "admin"
    FIRST_ADMIN_PASSWORD: str = "admin"

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Construye dinámicamente la cadena de conexión SQLAlchemy."""
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
