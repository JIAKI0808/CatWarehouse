"""分析分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.analytics.analytics_router import router as analytics_router

router = APIRouter()

router.include_router(analytics_router)
