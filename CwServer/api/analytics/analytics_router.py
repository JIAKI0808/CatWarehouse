import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from models.ledger import Ledger
from schemas.analytics import TrendResponse, TrendPoint

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/analytics/trend", response_model=TrendResponse)
async def get_trend(
    sub_category_id: int,
    db: AsyncSession = Depends(get_db),
):
    sub = await db.get(SubCategory, sub_category_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")

    result = await db.execute(
        select(SpecificItem).where(SpecificItem.sub_category_id == sub_category_id)
    )
    items = result.scalars().all()

    date_map: dict[str, dict] = {}
    for item in items:
        date_str = item.entry_date.strftime("%Y-%m-%d") if item.entry_date else "unknown"
        if date_str not in date_map:
            date_map[date_str] = {"quantity": 0, "price": 0.0}
        date_map[date_str]["quantity"] += 1
        date_map[date_str]["price"] += item.price

    data = [
        TrendPoint(
            date=d, quantity=v["quantity"], price=v["price"],
            total_price=v["quantity"] * v["price"],
            unit_price=v["price"] / v["quantity"] if v["quantity"] > 0 else 0.0,
        )
        for d, v in sorted(date_map.items())
    ]

    return TrendResponse(
        sub_category_id=sub.id, sub_category_name=sub.name,
        unit=sub.unit, data=data,
    )


@router.get("/analytics/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    items = (await db.execute(select(SpecificItem))).scalars().all()
    total_items = len(items)
    total_value = sum(item.price for item in items)

    ledger_items = (await db.execute(select(Ledger))).scalars().all()
    total_income = sum(l.amount for l in ledger_items if l.type == "income")
    total_expense = sum(l.amount for l in ledger_items if l.type == "expense")

    return {
        "total_items": total_items,
        "total_value": total_value,
        "total_income": total_income,
        "total_expense": total_expense,
    }


@router.get("/analytics/category-stats")
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(Category))).scalars().all()
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()

    cat_map = {c.id: c.name for c in categories}
    cat_sub_map: dict[int, int] = {}
    for sc in sub_cats:
        cat_sub_map[sc.category_id] = cat_sub_map.get(sc.category_id, 0) + sc.quantity

    return [
        {"name": cat_map.get(cid, ""), "value": qty}
        for cid, qty in cat_sub_map.items()
    ]


@router.get("/analytics/monthly-compare")
async def get_monthly_compare(db: AsyncSession = Depends(get_db)):
    ledger_items = (await db.execute(select(Ledger))).scalars().all()
    month_map: dict[str, dict[str, float]] = {}

    for item in ledger_items:
        key = item.date.strftime("%Y-%m")
        if key not in month_map:
            month_map[key] = {"income": 0.0, "expense": 0.0}
        if item.type == "income":
            month_map[key]["income"] += item.amount
        else:
            month_map[key]["expense"] += item.amount

    return [
        {"month": k, "income": v["income"], "expense": v["expense"]}
        for k, v in sorted(month_map.items())
    ]
