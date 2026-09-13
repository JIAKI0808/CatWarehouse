"""售价分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.pricing.pricing_router import router as pricing_router
from api.pricing.pricing_category_router import router as pricing_category_router

router = APIRouter()

router.include_router(pricing_router)
router.include_router(pricing_category_router)
