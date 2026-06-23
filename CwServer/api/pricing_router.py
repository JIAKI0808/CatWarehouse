import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.pricing import Pricing
from models.sub_category import SubCategory
from schemas.pricing import PricingCreate, PricingUpdate, PricingResponse

logger = logging.getLogger(__name__)
router = APIRouter()


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


@router.post("/pricing", response_model=PricingResponse)
async def create_pricing(data: PricingCreate, db: AsyncSession = Depends(get_db)):
    item = Pricing(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return PricingResponse(
        id=item.id, sub_category_id=item.sub_category_id, sub_category_name="",
        name=item.name, cost=item.cost, suggested_price=item.suggested_price,
        discount=item.discount, description=item.description, notes=item.notes,
        record_date=item.record_date,
    )


@router.put("/pricing/{pricing_id}", response_model=PricingResponse)
async def update_pricing(
    pricing_id: int, data: PricingUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(Pricing, pricing_id)
    if not item:
        raise HTTPException(404, "Pricing not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return PricingResponse(
        id=item.id, sub_category_id=item.sub_category_id, sub_category_name="",
        name=item.name, cost=item.cost, suggested_price=item.suggested_price,
        discount=item.discount, description=item.description, notes=item.notes,
        record_date=item.record_date,
    )


@router.delete("/pricing/{pricing_id}")
async def delete_pricing(pricing_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Pricing, pricing_id)
    if not item:
        raise HTTPException(404, "Pricing not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}
