import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
from schemas.specific_item import SpecificItemCreate, SpecificItemResponse, SpecificItemUpdate
from api.settings_router import router as settings_router

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["inventory"])


# ── Category CRUD ──

@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    logger.debug("Listed %d categories", len(categories))
    return categories


@router.post("/categories", response_model=CategoryResponse)
async def create_category(data: CategoryCreate, db: AsyncSession = Depends(get_db)):
    cat = Category(**data.model_dump())
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    logger.info("Created category id=%d name=%s", cat.id, cat.name)
    return cat


@router.get("/categories/{cat_id}", response_model=CategoryResponse)
async def get_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    cat = await db.get(Category, cat_id)
    if not cat:
        logger.warning("Category not found id=%d", cat_id)
        raise HTTPException(404, "Category not found")
    return cat


@router.put("/categories/{cat_id}", response_model=CategoryResponse)
async def update_category(
    cat_id: int, data: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    cat = await db.get(Category, cat_id)
    if not cat:
        logger.warning("Category not found id=%d", cat_id)
        raise HTTPException(404, "Category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, value)
    await db.commit()
    await db.refresh(cat)
    logger.info("Updated category id=%d", cat_id)
    return cat


@router.delete("/categories/{cat_id}")
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    cat = await db.get(Category, cat_id)
    if not cat:
        logger.warning("Category not found id=%d", cat_id)
        raise HTTPException(404, "Category not found")
    await db.delete(cat)
    await db.commit()
    logger.info("Deleted category id=%d", cat_id)
    return {"ok": True}


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
    subs = result.scalars().all()
    logger.debug("Listed %d sub-categories (category_id=%s)", len(subs), category_id)
    return subs


@router.post("/sub-categories", response_model=SubCategoryResponse)
async def create_sub_category(data: SubCategoryCreate, db: AsyncSession = Depends(get_db)):
    sub = SubCategory(**data.model_dump())
    db.add(sub)
    await db.commit()
    await db.refresh(sub)
    logger.info("Created sub-category id=%d name=%s", sub.id, sub.name)
    return sub


@router.get("/sub-categories/{sub_id}", response_model=SubCategoryResponse)
async def get_sub_category(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        logger.warning("SubCategory not found id=%d", sub_id)
        raise HTTPException(404, "SubCategory not found")
    return sub


@router.put("/sub-categories/{sub_id}", response_model=SubCategoryResponse)
async def update_sub_category(
    sub_id: int, data: SubCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        logger.warning("SubCategory not found id=%d", sub_id)
        raise HTTPException(404, "SubCategory not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(sub, key, value)
    await db.commit()
    await db.refresh(sub)
    logger.info("Updated sub-category id=%d", sub_id)
    return sub


@router.get("/sub-categories/{sub_id}/quantity")
async def get_sub_category_quantity(sub_id: int, db: AsyncSession = Depends(get_db)):
    sub = await db.get(SubCategory, sub_id)
    if not sub:
        logger.warning("SubCategory not found id=%d", sub_id)
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
        logger.warning("SubCategory not found id=%d", sub_id)
        raise HTTPException(404, "SubCategory not found")
    await db.delete(sub)
    await db.commit()
    logger.info("Deleted sub-category id=%d", sub_id)
    return {"ok": True}


# ── SpecificItem CRUD ──

@router.get("/items", response_model=list[SpecificItemResponse])
async def list_items(
    sub_category_id: int | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SpecificItem, SubCategory)
        .join(SubCategory, SpecificItem.sub_category_id == SubCategory.id)
    )
    if sub_category_id is not None:
        stmt = stmt.where(SpecificItem.sub_category_id == sub_category_id)
    result = await db.execute(stmt)
    rows = result.all()
    items = [
        SpecificItemResponse(
            id=item.id,
            sub_category_id=item.sub_category_id,
            sub_category_name=sub.name,
            quantity=sub.quantity,
            unit=sub.unit,
            name=item.name,
            entry_date=item.entry_date,
            update_date=item.update_date,
            recorder=item.recorder,
            price=item.price,
            description=item.description,
        )
        for item, sub in rows
    ]
    logger.debug("Listed %d items (sub_category_id=%s)", len(items), sub_category_id)
    return items


@router.post("/items", response_model=SpecificItemResponse)
async def create_item(data: SpecificItemCreate, db: AsyncSession = Depends(get_db)):
    item = SpecificItem(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    logger.info("Created item id=%d name=%s", item.id, item.name)
    return item


@router.get("/items/{item_id}", response_model=SpecificItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(SpecificItem, item_id)
    if not item:
        logger.warning("Item not found id=%d", item_id)
        raise HTTPException(404, "Item not found")
    return item


@router.put("/items/{item_id}", response_model=SpecificItemResponse)
async def update_item(
    item_id: int, data: SpecificItemUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(SpecificItem, item_id)
    if not item:
        logger.warning("Item not found id=%d", item_id)
        raise HTTPException(404, "Item not found")
    item_data = data.model_dump(exclude_unset=True, exclude={"quantity", "unit"})
    for key, value in item_data.items():
        setattr(item, key, value)
    if data.quantity is not None or data.unit is not None:
        sub = await db.get(SubCategory, item.sub_category_id)
        if sub:
            if data.quantity is not None:
                sub.quantity = data.quantity
            if data.unit is not None:
                sub.unit = data.unit
    await db.commit()
    await db.refresh(item)
    logger.info("Updated item id=%d", item_id)
    return item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(SpecificItem, item_id)
    if not item:
        logger.warning("Item not found id=%d", item_id)
        raise HTTPException(404, "Item not found")
    await db.delete(item)
    await db.commit()
    logger.info("Deleted item id=%d", item_id)
    return {"ok": True}


# ── Image Analysis ──

@router.post("/image-analysis")
async def image_analysis(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")

    contents = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size": len(contents),
        "message": "Image received successfully",
    }


router.include_router(settings_router)
