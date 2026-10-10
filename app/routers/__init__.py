from app.routers.auth import router as auth_router
from app.routers.publico import router as publico_router
from app.routers.usuarios import router as usuarios_router
from app.routers.materiales import router as materiales_router
from app.routers.precios import router as precios_router
from app.routers.historico_compra import router as historico_compra_router
from app.routers.historico_venta import router as historico_venta_router
from app.routers.sucursales import router as sucursales_router

__all__ = [
    "auth_router",
    "publico_router",
    "usuarios_router",
    "materiales_router",
    "precios_router",
    "historico_compra_router",
    "historico_venta_router",
    "sucursales_router"
]
