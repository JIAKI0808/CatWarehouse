import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.pricing_category import PricingCategory
from models.pricing_sub_category import PricingSubCategory
from schemas.pricing_category import (
    PricingCategoryCreate, PricingCategoryUpdate, PricingCategoryResponse,
    PricingSubCategoryCreate, PricingSubCategoryUpdate, PricingSubCategoryResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/pricing-categories", response_model=list[PricingCategoryResponse])
async def list_pricing_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PricingCategory))
    return result.scalars().all()


@router.post("/pricing-categories", response_model=PricingCategoryResponse)
async def create_pricing_category(data: PricingCategoryCreate, db: AsyncSession = Depends(get_db)):
    item = PricingCategory(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/pricing-categories/{cat_id}", response_model=PricingCategoryResponse)
async def update_pricing_category(
    cat_id: int, data: PricingCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(PricingCategory, cat_id)
    if not item:
        raise HTTPException(404, "Pricing category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/pricing-categories/{cat_id}")
async def delete_pricing_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(PricingCategory, cat_id)
    if not item:
        raise HTTPException(404, "Pricing category not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.get("/pricing-sub-categories", response_model=list[PricingSubCategoryResponse])
async def list_pricing_sub_categories(
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(PricingSubCategory)
    if category_id is not None:
        stmt = stmt.where(PricingSubCategory.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/pricing-sub-categories", response_model=PricingSubCategoryResponse)
async def create_pricing_sub_category(data: PricingSubCategoryCreate, db: AsyncSession = Depends(get_db)):
    item = PricingSubCategory(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/pricing-sub-categories/{sub_id}", response_model=PricingSubCategoryResponse)
async def update_pricing_sub_category(
    sub_id: int, data: PricingSubCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(PricingSubCategory, sub_id)
    if not item:
        raise HTTPException(404, "Pricing sub-category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/pricing-sub-categories/{sub_id}")
async def delete_pricing_sub_category(sub_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(PricingSubCategory, sub_id)
    if not item:
        raise HTTPException(404, "Pricing sub-category not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}
