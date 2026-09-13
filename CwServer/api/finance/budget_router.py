"""预算（Budget）—— create/update/delete 走通用层，列表与汇总保持手写。

这两个端点**必须**用响应钩子：`BudgetResponse.category_name` 与 `spent` 在模型上
不存在，schema 里又**没有默认值**，直接返回 ORM 对象会因缺字段序列化失败。
原实现在这两处写死 `category_name=""` / `spent=0.0`，钩子里照旧
（`spent` 是尚未实现的占位，本次重构不改行为）。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.budget import Budget
from models.category import Category
from schemas.budget import BudgetCreate, BudgetResponse, BudgetUpdate


def budget_response(item: Budget) -> BudgetResponse:
    """响应钩子：补上模型里没有的两个字段（取值与改造前一致）。"""
    return BudgetResponse(
        id=item.id,
        category_id=item.category_id,
        category_name="",
        month=item.month,
        amount=item.amount,
        spent=0.0,
    )


BUDGET = register_crud(
    CrudSpec(
        name="budget",
        model=Budget,
        response=BudgetResponse,
        path="/budget",
        id_param="budget_id",
        not_found="Budget not found",
        create=BudgetCreate,
        update=BudgetUpdate,
        to_response=budget_response,
        names=CrudNames(
            create="create_budget",
            update="update_budget",
            delete="delete_budget",
        ),
    )
)

router: APIRouter = build_crud_router(BUDGET)


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
