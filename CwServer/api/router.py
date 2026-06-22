from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from schemas.category import CategoryCreate, CategoryResponse
from schemas.sub_category import SubCategoryCreate, SubCategoryResponse
from schemas.specific_item import SpecificItemCreate, SpecificItemResponse, SpecificItemUpdate

router = APIRouter(prefix="/api", tags=["inventory"])


# ── Category CRUD ──

@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = Category(**data.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return cat


@router.get("/categories/{cat_id}", response_model=CategoryResponse)
async def get_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    cat = await db.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Category not found")
    return cat


# ── SubCategory CRUD ──

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


# ── SpecificItem CRUD ──

@router.get("/items", response_model=list[SpecificItemResponse])
async def list_items(
    sub_category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(SpecificItem)
    if sub_category_id is not None:
        stmt = stmt.where(SpecificItem.sub_category_id == sub_category_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/items", response_model=SpecificItemResponse)
async def create_item(data: SpecificItemCreate, db: AsyncSession = Depends(get_db)):
    item = SpecificItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/items/{item_id}", response_model=SpecificItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(SpecificItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.put("/items/{item_id}", response_model=SpecificItemResponse)
async def update_item(
    item_id: int, data: SpecificItemUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(SpecificItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(SpecificItem, item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}
