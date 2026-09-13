"""售价（Pricing）—— create/update/delete 走通用层，列表保持手写。

列表要 `join SubCategory` 拿分类名，是联表查询，留在本文件里。

`create` / `update` **不需要响应钩子**：`PricingResponse` 带 `from_attributes=True`，
而 `sub_category_name` 在模型上不存在、schema 里又有默认值 `""`，
所以直接返回 ORM 对象得到的 JSON 与原实现手工构造的**完全一致**
（原实现那两处也是写死 `sub_category_name=""`）。
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.pricing import Pricing
from models.sub_category import SubCategory
from schemas.pricing import PricingCreate, PricingResponse, PricingUpdate

PRICING = register_crud(
    CrudSpec(
        name="pricing",
        model=Pricing,
        response=PricingResponse,
        path="/pricing",
        id_param="pricing_id",
        not_found="Pricing not found",
        create=PricingCreate,
        update=PricingUpdate,
        names=CrudNames(
            create="create_pricing",
            update="update_pricing",
            delete="delete_pricing",
        ),
    )
)

router: APIRouter = build_crud_router(PRICING)


@router.get("/pricing", response_model=list[PricingResponse])
async def list_pricing(
    sub_category_id: int | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(Pricing, SubCategory)
        .join(SubCategory, Pricing.sub_category_id == SubCategory.id)
    )
    if sub_category_id is not None:
        stmt = stmt.where(Pricing.sub_category_id == sub_category_id)
    if q:
        stmt = stmt.where(Pricing.name.contains(q) | Pricing.description.contains(q))
    result = await db.execute(stmt)
    rows = result.all()
    return [
        PricingResponse(
            id=p.id, sub_category_id=p.sub_category_id, sub_category_name=sc.name,
            name=p.name, cost=p.cost, suggested_price=p.suggested_price,
            discount=p.discount, description=p.description, notes=p.notes,
            record_date=p.record_date,
        )
        for p, sc in rows
    ]
