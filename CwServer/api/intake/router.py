"""录入分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.intake.upload_router import router as upload_router
from api.intake.ocr_router import router as ocr_router
from api.intake.voice_router import router as voice_router

router = APIRouter()

router.include_router(upload_router)
router.include_router(ocr_router)
router.include_router(voice_router)
