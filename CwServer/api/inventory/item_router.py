"""商品明细（SpecificItem）—— 端点保持手写，但取数与落库走 `dataManager` 的抽象工厂。

这个资源的列表要 join 子分类、更新要跨表写子分类库存、还带导入导出，不属于标准 CRUD，
所以端点不交给 `build_crud_router`。但「取对象 + 404」「新建」「删除」这些通用动作
改由 `get_factory("inventory", db)` 产出的仓储承担 ——
这是 `dataManager/` 那套抽象工厂第一次被真实调用（此前它对全仓库零引用）。

列表的响应构造交给了 `dataManager.inventory.item.Item`（组合视图产品），
不再在端点里手工堆 `SpecificItemResponse` 的字段。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.factory import get_factory
from dataManager.inventory.item import Item
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from schemas.import_export import (
    ConflictCheckResponse,
    ConflictItem,
    ImportExecuteRequest,
    ImportRequest,
    ImportResult,
)
from schemas.specific_item import SpecificItemCreate, SpecificItemResponse, SpecificItemUpdate

router = APIRouter()


@router.get("/items", response_model=list[SpecificItemResponse])
async def list_items(
    sub_category_id: int | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(SpecificItem, SubCategory)
        .join(SubCategory, SpecificItem.sub_category_id == SubCategory.id)
    )
    if sub_category_id is not None:
        stmt = stmt.where(SpecificItem.sub_category_id == sub_category_id)
    if q:
        stmt = stmt.where(
            SpecificItem.name.contains(q) | SpecificItem.description.contains(q)
        )
    result = await db.execute(stmt)
    return [Item(item, sub).to_dict() for item, sub in result.all()]


@router.post("/items", response_model=SpecificItemResponse)
async def create_item(data: SpecificItemCreate, db: AsyncSession = Depends(get_db)):
    factory = get_factory("inventory", db)
    validator = factory.create_validator()
    payload = data.model_dump()
    if not validator.validate(payload):
        raise HTTPException(422, "; ".join(validator.errors()))
    return await factory.create_repository().create(payload)


@router.get("/items/{item_id}", response_model=SpecificItemResponse)
async def get_item(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await get_factory("inventory", db).create_repository().get(item_id)
    if not item:
        raise HTTPException(404, "Item not found")
    return item


@router.put("/items/{item_id}", response_model=SpecificItemResponse)
async def update_item(
    item_id: int, data: SpecificItemUpdate, db: AsyncSession = Depends(get_db)
):
    item = await get_factory("inventory", db).create_repository().get(item_id)
    if not item:
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
    return item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: AsyncSession = Depends(get_db)):
    if not await get_factory("inventory", db).create_repository().delete(item_id):
        raise HTTPException(404, "Item not found")
    return {"ok": True}


@router.get("/export")
async def export_data(db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(Category))).scalars().all()
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()
    items = (await db.execute(select(SpecificItem))).scalars().all()

    sub_map: dict[int, list] = {}
    for sc in sub_cats:
        sub_map.setdefault(sc.category_id, []).append({
            "id": sc.id, "name": sc.name, "unit": sc.unit,
            "description": sc.description, "notes": sc.notes,
        })

    item_map: dict[int, list] = {}
    for it in items:
        item_map.setdefault(it.sub_category_id, []).append({
            "id": it.id, "name": it.name, "recorder": it.recorder,
            "price": it.price, "description": it.description,
            "expire_date": it.expire_date.isoformat() if it.expire_date else None,
            "is_expired": bool(it.is_expired),
        })

    result = []
    for cat in categories:
        cat_data = {
            "name": cat.name, "description": cat.description,
            "icon": cat.icon, "icon_color": cat.icon_color, "sub_categories": [],
        }
        for sc in sub_map.get(cat.id, []):
            sc_data = {
                "name": sc["name"], "unit": sc["unit"],
                "description": sc["description"], "notes": sc["notes"],
                "items": item_map.get(sc["id"], []),
            }
            cat_data["sub_categories"].append(sc_data)
        result.append(cat_data)

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
                type="category", name=cat.name,
                existing_id=cat_name_map[cat.name], imported_data=cat.model_dump(),
            ))

    if not conflicts:
        existing_subs = (await db.execute(select(SubCategory))).scalars().all()
        sub_names = {(s.name, s.category_id) for s in existing_subs}
        for cat in data.categories:
            cat_id = cat_name_map.get(cat.name)
            for sub in cat.sub_categories:
                if (sub.name, cat_id) in sub_names:
                    conflicts.append(ConflictItem(
                        type="sub_category", name=sub.name,
                        existing_id=0, imported_data=sub.model_dump(),
                    ))

    return ConflictCheckResponse(has_conflicts=len(conflicts) > 0, conflicts=conflicts)


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
                name=cat.name, description=cat.description,
                icon=cat.icon, icon_color=cat.icon_color,
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
                    category_id=cat_id, name=sub.name, unit=sub.unit,
                    description=sub.description, notes=sub.notes,
                )
                db.add(new_sub)
                await db.flush()
                subs_created += 1

                for item in getattr(sub, "items", []):
                    new_item = SpecificItem(
                        sub_category_id=new_sub.id, name=item["name"],
                        recorder=item.get("recorder", ""), price=item.get("price", 0.0),
                        description=item.get("description", ""),
                        expire_date=item.get("expire_date"),
                        is_expired=int(item.get("is_expired", False)),
                    )
                    db.add(new_item)
                    items_created += 1

    await db.commit()
    return ImportResult(
        categories_created=cats_created, sub_categories_created=subs_created,
        items_created=items_created,
    )
