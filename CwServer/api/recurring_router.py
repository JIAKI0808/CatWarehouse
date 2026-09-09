import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.recurring import RecurringBill
from models.ledger import Ledger
from schemas.recurring import RecurringBillCreate, RecurringBillUpdate, RecurringBillResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/recurring", response_model=list[RecurringBillResponse])
async def list_recurring(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(RecurringBill))
    return result.scalars().all()


@router.post("/recurring", response_model=RecurringBillResponse)
async def create_recurring(data: RecurringBillCreate, db: AsyncSession = Depends(get_db)):
    item = RecurringBill(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/recurring/{bill_id}", response_model=RecurringBillResponse)
async def update_recurring(
    bill_id: int, data: RecurringBillUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(RecurringBill, bill_id)
    if not item:
        raise HTTPException(404, "Recurring bill not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/recurring/{bill_id}")
async def delete_recurring(bill_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(RecurringBill, bill_id)
    if not item:
        raise HTTPException(404, "Recurring bill not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.post("/recurring/generate")
async def generate_recurring_bills(db: AsyncSession = Depends(get_db)):
    now = datetime.now()
    result = await db.execute(
        select(RecurringBill).where(
            RecurringBill.is_active == True,
            RecurringBill.next_date <= now,
        )
    )
    bills = result.scalars().all()
    created = 0

    for bill in bills:
        ledger_item = Ledger(
            amount=bill.amount, date=now, platform=bill.platform,
            description=bill.description, person=bill.person, type=bill.type,
        )
        db.add(ledger_item)

        if bill.frequency == "monthly":
            if bill.next_date.month < 12:
                bill.next_date = bill.next_date.replace(month=bill.next_date.month + 1)
            else:
                bill.next_date = bill.next_date.replace(year=bill.next_date.year + 1, month=1)
        elif bill.frequency == "yearly":
            bill.next_date = bill.next_date.replace(year=bill.next_date.year + 1)
        created += 1

    await db.commit()
    return {"created": created}
