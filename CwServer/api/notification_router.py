import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.notification import Notification
from models.specific_item import SpecificItem
from models.budget import Budget
from schemas.notification import NotificationResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Notification).order_by(Notification.created_at.desc()))
    return result.scalars().all()


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Notification, notification_id)
    if not item:
        raise HTTPException(404, "Notification not found")
    item.is_read = True
    await db.commit()
    return {"ok": True}


@router.post("/notifications/check")
async def check_notifications(db: AsyncSession = Depends(get_db)):
    items = (await db.execute(select(SpecificItem))).scalars().all()
    now = datetime.now()
    created = 0

    for item in items:
        if item.expire_date and item.expire_date < now:
            existing = (
                await db.execute(
                    select(Notification).where(
                        Notification.type == "expiry",
                        Notification.related_id == item.id,
                        Notification.is_read == False,
                    )
                )
            ).scalars().first()
            if not existing:
                n = Notification(
                    type="expiry", message=f"物品 {item.name} 已过期",
                    related_id=item.id,
                )
                db.add(n)
                created += 1

    await db.commit()
    return {"created": created}
