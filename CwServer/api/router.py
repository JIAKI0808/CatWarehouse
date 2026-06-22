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
from schemas.import_export import (
    ImportRequest,
    ConflictCheckResponse,
    ConflictItem,
    ImportExecuteRequest,
    ImportResult,
)
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

@router.get("/export")
async def export_data(db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(Category))).scalars().all()
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()
    items = (await db.execute(select(SpecificItem))).scalars().all()

    sub_map: dict[int, list] = {}
    for sc in sub_cats:
        sub_map.setdefault(sc.category_id, []).append({
            "id": sc.id,
            "name": sc.name,
            "unit": sc.unit,
            "description": sc.description,
            "notes": sc.notes,
        })

    item_map: dict[int, list] = {}
    for it in items:
        item_map.setdefault(it.sub_category_id, []).append({
            "id": it.id,
            "name": it.name,
            "recorder": it.recorder,
            "price": it.price,
            "description": it.description,
            "expire_date": it.expire_date.isoformat() if it.expire_date else None,
            "is_expired": bool(it.is_expired),
        })

    result = []
    for cat in categories:
        cat_data = {
            "name": cat.name,
            "description": cat.description,
            "icon": cat.icon,
            "icon_color": cat.icon_color,
            "sub_categories": [],
        }
        for sc in sub_map.get(cat.id, []):
            sc_data = {
                "name": sc["name"],
                "unit": sc["unit"],
                "description": sc["description"],
                "notes": sc["notes"],
                "items": item_map.get(sc["id"], []),
            }
            cat_data["sub_categories"].append(sc_data)
        result.append(cat_data)

    logger.info("Exported %d categories", len(result))
    return {"categories": result}


@router.post("/import/conflicts", response_model=ConflictCheckResponse)
async def check_import_conflicts(
    data: ImportRequest, db: AsyncSession = Depends(get_db)
):
    existing_cats = (await db.execute(select(Category))).scalars().all()
    cat_name_map = {c.name: c.id for c in existing_cats}

    conflicts: list[ConflictItem] = []
    for cat in data.categories:
        if cat.name in cat_name_map:
            conflicts.append(ConflictItem(
                type="category",
                name=cat.name,
                existing_id=cat_name_map[cat.name],
                imported_data=cat.model_dump(),
            ))

    if not conflicts:
        existing_subs = (await db.execute(select(SubCategory))).scalars().all()
        sub_names = {(s.name, s.category_id) for s in existing_subs}
        for cat in data.categories:
            cat_id = cat_name_map.get(cat.name)
            for sub in cat.sub_categories:
                if (sub.name, cat_id) in sub_names:
                    conflicts.append(ConflictItem(
                        type="sub_category",
                        name=sub.name,
                        existing_id=0,
                        imported_data=sub.model_dump(),
                    ))

    return ConflictCheckResponse(
        has_conflicts=len(conflicts) > 0,
        conflicts=conflicts,
    )


@router.post("/import/execute", response_model=ImportResult)
async def execute_import(
    data: ImportExecuteRequest, db: AsyncSession = Depends(get_db)
):
    existing_cats = (await db.execute(select(Category))).scalars().all()
    cat_name_map = {c.name: c.id for c in existing_cats}

    cats_created = 0
    subs_created = 0
    items_created = 0

    for cat in data.categories:
        skip_key = f"category:{cat.name}"
        if cat.name in cat_name_map and skip_key in data.skip_conflicts:
            cat_id = cat_name_map[cat.name]
        elif cat.name in cat_name_map:
            cat_id = cat_name_map[cat.name]
        else:
            new_cat = Category(
                name=cat.name,
                description=cat.description,
                icon=cat.icon,
                icon_color=cat.icon_color,
            )
            db.add(new_cat)
            await db.flush()
            cat_id = new_cat.id
            cats_created += 1

        existing_subs = (
            await db.execute(
                select(SubCategory).where(SubCategory.category_id == cat_id)
            )
        ).scalars().all()
        sub_name_map = {s.name: s.id for s in existing_subs}

        for sub in cat.sub_categories:
            skip_key = f"sub_category:{cat.name}:{sub.name}"
            if sub.name in sub_name_map and skip_key in data.skip_conflicts:
                continue
            elif sub.name in sub_name_map:
                continue
            else:
                new_sub = SubCategory(
                    category_id=cat_id,
                    name=sub.name,
                    unit=sub.unit,
                    description=sub.description,
                    notes=sub.notes,
                )
                db.add(new_sub)
                await db.flush()
                subs_created += 1

                for item in getattr(sub, "items", []):
                    new_item = SpecificItem(
                        sub_category_id=new_sub.id,
                        name=item["name"],
                        recorder=item.get("recorder", ""),
                        price=item.get("price", 0.0),
                        description=item.get("description", ""),
                        expire_date=item.get("expire_date"),
                        is_expired=int(item.get("is_expired", False)),
                    )
                    db.add(new_item)
                    items_created += 1

    await db.commit()
    logger.info(
        "Import complete: %d cats, %d subs, %d items",
        cats_created, subs_created, items_created,
    )
    return ImportResult(
        categories_created=cats_created,
        sub_categories_created=subs_created,
        items_created=items_created,
    )


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
