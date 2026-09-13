"""系统分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.system.backup_router import router as backup_router
from api.system.currency_router import router as currency_router
from api.system.settings_router import router as settings_router

router = APIRouter()

router.include_router(backup_router)
router.include_router(currency_router)
router.include_router(settings_router)
