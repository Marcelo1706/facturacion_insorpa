from fastapi import APIRouter

from .datos_empresa import router as datos_empresa_router
from .dte import router as dte_router
from .factura import router as factura_router
from .login import router as login_router
from .logout import router as logout_router

# from .users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(login_router)
router.include_router(logout_router)
router.include_router(datos_empresa_router)
router.include_router(dte_router)
router.include_router(factura_router)
# router.include_router(users_router)
