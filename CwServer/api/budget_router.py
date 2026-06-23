import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.budget import Budget
from models.category import Category
from models.sub_category import SubCategory
from models.ledger import Ledger
from schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/budget", response_model=list[BudgetResponse])
async def list_budget(month: str | None = None, db: AsyncSession = Depends(get_db)):
    stmt = select(Budget)
    if month:
        stmt = stmt.where(Budget.month == month)
    result = await db.execute(stmt)
    budgets = result.scalars().all()

    cat_ids = {b.category_id for b in budgets}
    cats = (await db.execute(select(Category).where(Category.id.in_(cat_ids)))).scalars().all()
    cat_map = {c.id: c.name for c in cats}

    return [
        BudgetResponse(
            id=b.id, category_id=b.category_id, category_name=cat_map.get(b.category_id, ""),
            month=b.month, amount=b.amount, spent=0.0,
        )
        for b in budgets
    ]


@router.post("/budget", response_model=BudgetResponse)
async def create_budget(data: BudgetCreate, db: AsyncSession = Depends(get_db)):
    item = Budget(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return BudgetResponse(
        id=item.id, category_id=item.category_id, category_name="",
        month=item.month, amount=item.amount, spent=0.0,
    )


@router.put("/budget/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int, data: BudgetUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(Budget, budget_id)
    if not item:
        raise HTTPException(404, "Budget not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return BudgetResponse(
        id=item.id, category_id=item.category_id, category_name="",
        month=item.month, amount=item.amount, spent=0.0,
    )


@router.delete("/budget/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Budget, budget_id)
    if not item:
        raise HTTPException(404, "Budget not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.get("/budget/summary")
async def get_budget_summary(month: str, db: AsyncSession = Depends(get_db)):
    budgets = (await db.execute(select(Budget).where(Budget.month == month))).scalars().all()
    cat_ids = {b.category_id for b in budgets}
    cats = (await db.execute(select(Category).where(Category.id.in_(cat_ids)))).scalars().all()
    cat_map = {c.id: c.name for c in cats}

    return [
        {"budget_id": b.id, "category_id": b.category_id,
         "category_name": cat_map.get(b.category_id, ""),
         "amount": b.amount, "spent": 0.0, "percentage": 0.0}
        for b in budgets
    ]
