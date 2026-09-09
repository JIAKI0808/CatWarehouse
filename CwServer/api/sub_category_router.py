import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/sub-categories", response_model=list[SubCategoryResponse])
async def list_sub_categories(
    category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SubCategory)
    if category_id is not None:
        stmt = stmt.where(SubCategory.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/sub-categories", response_model=SubCategoryResponse)
async def create_sub_category(data: SubCategoryCreate, db: AsyncSession = Depends(get_db)):
    sub = SubCategory(**data.model_dump())
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.get("/sub-categories/{sub_id}", response_model=SubCategoryResponse)
async def get_sub_category(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")
    return sub


@router.put("/sub-categories/{sub_id}", response_model=SubCategoryResponse)
async def update_sub_category(
    sub_id: int, data: SubCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sub, key, value)
    await db.commit()
    await db.refresh(sub)
    return sub


@router.get("/sub-categories/{sub_id}/quantity")
async def get_sub_category_quantity(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")
    result = await db.execute(
        select(SpecificItem).where(SpecificItem.sub_category_id == sub_id)
    )
    count = len(result.scalars().all())
    return {"sub_category_id": sub_id, "quantity": count}


@router.delete("/sub-categories/{sub_id}")
async def delete_sub_category(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")
    await db.delete(sub)
    await db.commit()
    return {"ok": True}
