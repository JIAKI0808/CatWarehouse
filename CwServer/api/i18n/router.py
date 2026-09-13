"""国际化分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.i18n.i18n_router import router as i18n_router

router = APIRouter()

router.include_router(i18n_router)
