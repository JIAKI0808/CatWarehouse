import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.sub_category import SubCategory

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/alerts")
async def get_stock_alerts(threshold: int = 5, db: AsyncSession = Depends(get_db)):
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()
    alerts = []
    for sc in sub_cats:
        if sc.quantity <= threshold:
            alerts.append({
                "id": sc.id, "type": "low_stock",
                "message": f"{sc.name} 库存不足 (剩余 {sc.quantity} {sc.unit})",
                "quantity": sc.quantity, "threshold": threshold,
            })
    return alerts


@router.get("/alerts/config")
async def get_alert_config():
    return {"threshold": 5}


@router.put("/alerts/config")
async def update_alert_config(threshold: int = 5):
    return {"threshold": threshold}
