"""账本（Ledger）—— create/update/delete 走通用层，列表与统计保持手写。

列表带了 4 个过滤参数与 `date desc` 排序，统计是按周期归组的聚合，两者都不是
标准 CRUD，原样保留。`LedgerResponse` 带 `from_attributes=True` 且字段与模型一一对应，
所以增删改不需要响应钩子。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.ledger import Ledger
from schemas.ledger import LedgerCreate, LedgerResponse, LedgerStats, LedgerUpdate

LEDGER = register_crud(
    CrudSpec(
        name="ledger",
        model=Ledger,
        response=LedgerResponse,
        path="/ledger",
        id_param="item_id",
        not_found="Ledger item not found",
        create=LedgerCreate,
        update=LedgerUpdate,
        names=CrudNames(
            create="create_ledger",
            update="update_ledger",
            delete="delete_ledger",
        ),
    )
)

router: APIRouter = build_crud_router(LEDGER)


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
