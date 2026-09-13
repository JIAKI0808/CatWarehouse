"""财务分区的聚合门面（无 prefix / 无 tags，理由见 `api/inventory/router.py`）。"""

from fastapi import APIRouter

from api.finance.ledger_router import router as ledger_router
from api.finance.budget_router import router as budget_router
from api.finance.recurring_router import router as recurring_router

router = APIRouter()

router.include_router(ledger_router)
router.include_router(budget_router)
router.include_router(recurring_router)
