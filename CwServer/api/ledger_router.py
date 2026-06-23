import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.ledger import Ledger
from schemas.ledger import LedgerCreate, LedgerUpdate, LedgerResponse, LedgerStats

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/ledger", response_model=list[LedgerResponse])
async def list_ledger(
    q: str | None = None, type: str | None = None,
    start_date: str | None = None, end_date: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Ledger).order_by(Ledger.date.desc())
    if q:
        stmt = stmt.where(Ledger.description.contains(q) | Ledger.platform.contains(q) | Ledger.person.contains(q))
    if type:
        stmt = stmt.where(Ledger.type == type)
    if start_date:
        stmt = stmt.where(Ledger.date >= start_date)
    if end_date:
        stmt = stmt.where(Ledger.date <= end_date)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/ledger", response_model=LedgerResponse)
async def create_ledger(data: LedgerCreate, db: AsyncSession = Depends(get_db)):
    item = Ledger(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/ledger/{item_id}", response_model=LedgerResponse)
async def update_ledger(
    item_id: int, data: LedgerUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(Ledger, item_id)
    if not item:
        raise HTTPException(404, "Ledger item not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/ledger/{item_id}")
async def delete_ledger(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Ledger, item_id)
    if not item:
        raise HTTPException(404, "Ledger item not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.get("/ledger/stats", response_model=list[LedgerStats])
async def get_ledger_stats(range: str = "month", db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Ledger))
    items = result.scalars().all()

    period_map: dict[str, dict[str, float]] = {}
    for item in items:
        if range == "year":
            key = item.date.strftime("%Y")
        elif range == "month":
            key = item.date.strftime("%Y-%m")
        elif range == "week":
            key = item.date.strftime("%Y-W%W")
        else:
            key = item.date.strftime("%Y-%m-%d")

        if key not in period_map:
            period_map[key] = {"income": 0.0, "expense": 0.0}

        if item.type == "income":
            period_map[key]["income"] += item.amount
        else:
            period_map[key]["expense"] += item.amount

    return [
        LedgerStats(period=k, income=v["income"], expense=v["expense"])
        for k, v in sorted(period_map.items())
    ]
