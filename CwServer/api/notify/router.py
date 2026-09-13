"""通知分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.notify.notification_router import router as notification_router
from api.notify.alert_router import router as alert_router

router = APIRouter()

router.include_router(notification_router)
router.include_router(alert_router)
