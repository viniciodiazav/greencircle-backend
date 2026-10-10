from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.config import settings
from app.database import get_db, engine, SessionLocal
from app.models.usuario import Usuario
from app.security import hash_password
from app.routers import (
    auth_router,
    publico_router,
    usuarios_router,
    materiales_router,
    precios_router,
    historico_compra_router,
    historico_venta_router,
    sucursales_router
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Verificación de conectividad con la base de datos
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1;"))
            print("🚀 Conexión a PostgreSQL establecida con éxito.")
    except Exception as e:
        print(f"⚠️ Advertencia: No se pudo conectar a PostgreSQL al iniciar: {e}")

    # 2. Inicialización automática del Administrador por Defecto si no existe ninguno
    try:
        with SessionLocal() as db:
            admin_existente = db.query(Usuario).filter(Usuario.admin == True).first()
            if not admin_existente:
                primer_admin = Usuario(
                    nombre=settings.FIRST_ADMIN_NOMBRE,
                    apellido=settings.FIRST_ADMIN_APELLIDO,
                    usuario=settings.FIRST_ADMIN_USUARIO.lower(),
                    password_hash=hash_password(settings.FIRST_ADMIN_PASSWORD),
                    admin=True,
                    activo=True
                )
                db.add(primer_admin)
                db.commit()
                print(f"👤 Administrador inicial creado automáticamente: usuario='{settings.FIRST_ADMIN_USUARIO}'")
    except Exception as e:
        print(f"⚠️ Error al verificar/crear administrador inicial: {e}")

    yield

    # Shutdown
    engine.dispose()

app = FastAPI(
    title="🌿 Green Circle API",
    description=(
        "API REST para la administración y operación de centros de reciclaje y acopio de materiales.\n\n"
        "### 🔐 Política de Seguridad y Control de Acceso:\n"
        "- **Endpoints Públicos (Únicos 2 sin autenticación):**\n"
        "  1. `GET /api/publico/materiales`: Devuelve exclusivamente `nombre` y `precio` de los materiales activos.\n"
        "  2. `GET /api/publico/sucursales`: Devuelve exclusivamente `nombre` y `url` de las sucursales.\n"
        "- **Endpoints Protegidos (TODOS los demás requieren Bearer Token):**\n"
        "  - `/api/materiales/*` (Catálogo completo, códigos, estados)\n"
        "  - `/api/sucursales/*` (Gestión completa, creación, edición y eliminación)\n"
        "  - `/api/precios/*` (Consulta y actualización de precios vigentes)\n"
        "  - `/api/usuarios/*` (Gestión y activación de cuentas)\n"
        "  - `/api/historicos-compra/*` y `/api/historicos-venta/*` (Auditoría contable inmutable)\n"
        "- **Autenticación:** Mediante `POST /api/auth/login-json` (`usuario: admin`, `password: admin`)."
    ),
    version="1.4.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Habilitar CORS para permitir llamadas desde clientes web y móviles
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers: público, autenticación y entidades protegidas
app.include_router(publico_router)
app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(materiales_router)
app.include_router(precios_router)
app.include_router(historico_compra_router)
app.include_router(historico_venta_router)
app.include_router(sucursales_router)

@app.get("/", tags=["General"])
def root():
    """Ruta raíz de bienvenida e información básica de la API."""
    return {
        "sistema": "🌿 Green Circle API",
        "version": "1.4.0",
        "estado": "online",
        "documentacion": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health", tags=["General"])
def healthcheck(db: Session = Depends(get_db)):
    """Verifica el estado del servicio y la conectividad con PostgreSQL."""
    try:
        db.execute(text("SELECT 1;"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status
    }
