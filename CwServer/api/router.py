import logging

from fastapi import APIRouter

from api.settings_router import router as settings_router
from api.category_router import router as category_router
from api.sub_category_router import router as sub_category_router
from api.item_router import router as item_router
from api.analytics_router import router as analytics_router
from api.ledger_router import router as ledger_router
from api.budget_router import router as budget_router
from api.notification_router import router as notification_router
from api.tag_router import router as tag_router
from api.alert_router import router as alert_router
from api.recurring_router import router as recurring_router
from api.upload_router import router as upload_router
from api.ocr_router import router as ocr_router
from api.voice_router import router as voice_router
from api.backup_router import router as backup_router
from api.currency_router import router as currency_router
from api.pricing_router import router as pricing_router
from api.pricing_category_router import router as pricing_category_router

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["inventory"])

router.include_router(category_router)
router.include_router(sub_category_router)
router.include_router(item_router)
router.include_router(analytics_router)
router.include_router(ledger_router)
router.include_router(budget_router)
router.include_router(notification_router)
router.include_router(tag_router)
router.include_router(alert_router)
router.include_router(recurring_router)
router.include_router(upload_router)
router.include_router(ocr_router)
router.include_router(voice_router)
router.include_router(backup_router)
router.include_router(currency_router)
router.include_router(pricing_router)
router.include_router(pricing_category_router)
router.include_router(settings_router)
