import logging

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from models.ledger import Ledger
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from schemas.sub_category import SubCategoryCreate, SubCategoryUpdate, SubCategoryResponse
from schemas.specific_item import SpecificItemCreate, SpecificItemResponse, SpecificItemUpdate
from schemas.ledger import LedgerCreate, LedgerUpdate, LedgerResponse, LedgerStats
from schemas.budget import BudgetCreate, BudgetUpdate, BudgetResponse
from schemas.notification import NotificationResponse
from schemas.tag import TagCreate, TagUpdate, TagResponse
from schemas.recurring import RecurringBillCreate, RecurringBillUpdate, RecurringBillResponse
from schemas.pricing import PricingCreate, PricingUpdate, PricingResponse
from schemas.pricing_category import (
    PricingCategoryCreate, PricingCategoryUpdate, PricingCategoryResponse,
    PricingSubCategoryCreate, PricingSubCategoryUpdate, PricingSubCategoryResponse,
)
from schemas.import_export import (
    ImportRequest,
    ConflictCheckResponse,
    ConflictItem,
    ImportExecuteRequest,
    ImportResult,
)
from schemas.analytics import TrendResponse, TrendPoint
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


# ── Analytics ──

@router.get("/analytics/trend", response_model=TrendResponse)
async def get_trend(
    sub_category_id: int,
    db: AsyncSession = Depends(get_db),
):
    sub = await db.get(SubCategory, sub_category_id)
    if not sub:
        raise HTTPException(404, "SubCategory not found")

    result = await db.execute(
        select(SpecificItem).where(SpecificItem.sub_category_id == sub_category_id)
    )
    items = result.scalars().all()

    date_map: dict[str, dict] = {}
    for item in items:
        date_str = item.entry_date.strftime("%Y-%m-%d") if item.entry_date else "unknown"
        if date_str not in date_map:
            date_map[date_str] = {"quantity": 0, "price": 0.0}
        date_map[date_str]["quantity"] += 1
        date_map[date_str]["price"] += item.price

    data = [
        TrendPoint(
            date=d,
            quantity=v["quantity"],
            price=v["price"],
            total_price=v["quantity"] * v["price"],
            unit_price=v["price"] / v["quantity"] if v["quantity"] > 0 else 0.0,
        )
        for d, v in sorted(date_map.items())
    ]

    return TrendResponse(
        sub_category_id=sub.id,
        sub_category_name=sub.name,
        unit=sub.unit,
        data=data,
    )


# ── Ledger CRUD ──

@router.get("/ledger", response_model=list[LedgerResponse])
async def list_ledger(
    q: str | None = None,
    type: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Ledger).order_by(Ledger.date.desc())
    if q:
        stmt = stmt.where(
            Ledger.description.contains(q) | Ledger.platform.contains(q) | Ledger.person.contains(q)
        )
    if type:
        stmt = stmt.where(Ledger.type == type)
    if start_date:
        stmt = stmt.where(Ledger.date >= start_date)
    if end_date:
        stmt = stmt.where(Ledger.date <= end_date)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/ledger", response_model=LedgerResponse)
async def create_ledger(data: LedgerCreate, db: AsyncSession = Depends(get_db)):
    item = Ledger(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/ledger/{item_id}", response_model=LedgerResponse)
async def update_ledger(
    item_id: int, data: LedgerUpdate, db: AsyncSession = Depends(get_db)
):
    item = await db.get(Ledger, item_id)
    if not item:
        raise HTTPException(404, "Ledger item not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/ledger/{item_id}")
async def delete_ledger(item_id: int, db: AsyncSession = Depends(get_db)):
    item = await db.get(Ledger, item_id)
    if not item:
        raise HTTPException(404, "Ledger item not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.get("/ledger/stats", response_model=list[LedgerStats])
async def get_ledger_stats(
    range: str = "month",
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import func, extract

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


# ── Budget CRUD ──

@router.get("/budget", response_model=list[BudgetResponse])
async def list_budget(month: str | None = None, db: AsyncSession = Depends(get_db)):
    from models.budget import Budget
    from models.category import Category

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
            id=b.id,
            category_id=b.category_id,
            category_name=cat_map.get(b.category_id, ""),
            month=b.month,
            amount=b.amount,
            spent=0.0,
        )
        for b in budgets
    ]


@router.post("/budget", response_model=BudgetResponse)
async def create_budget(data: BudgetCreate, db: AsyncSession = Depends(get_db)):
    from models.budget import Budget

    item = Budget(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return BudgetResponse(
        id=item.id,
        category_id=item.category_id,
        category_name="",
        month=item.month,
        amount=item.amount,
        spent=0.0,
    )


@router.put("/budget/{budget_id}", response_model=BudgetResponse)
async def update_budget(
    budget_id: int, data: BudgetUpdate, db: AsyncSession = Depends(get_db)
):
    from models.budget import Budget

    item = await db.get(Budget, budget_id)
    if not item:
        raise HTTPException(404, "Budget not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return BudgetResponse(
        id=item.id,
        category_id=item.category_id,
        category_name="",
        month=item.month,
        amount=item.amount,
        spent=0.0,
    )


@router.delete("/budget/{budget_id}")
async def delete_budget(budget_id: int, db: AsyncSession = Depends(get_db)):
    from models.budget import Budget

    item = await db.get(Budget, budget_id)
    if not item:
        raise HTTPException(404, "Budget not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.get("/budget/summary")
async def get_budget_summary(month: str, db: AsyncSession = Depends(get_db)):
    from models.budget import Budget
    from models.category import Category
    from models.sub_category import SubCategory

    budgets = (
        await db.execute(select(Budget).where(Budget.month == month))
    ).scalars().all()

    cat_ids = {b.category_id for b in budgets}
    cats = (await db.execute(select(Category).where(Category.id.in_(cat_ids)))).scalars().all()
    cat_map = {c.id: c.name for c in cats}

    sub_cats = (
        await db.execute(select(SubCategory).where(SubCategory.category_id.in_(cat_ids)))
    ).scalars().all()
    sub_cat_map = {sc.id: sc for sc in sub_cats}

    summary = []
    for b in budgets:
        spent = sub_cat_map.get(b.category_id, None)
        summary.append({
            "budget_id": b.id,
            "category_id": b.category_id,
            "category_name": cat_map.get(b.category_id, ""),
            "amount": b.amount,
            "spent": 0.0,
            "percentage": 0.0,
        })

    return summary


# ── Analytics Overview ──

@router.get("/analytics/overview")
async def get_analytics_overview(db: AsyncSession = Depends(get_db)):
    from sqlalchemy import func

    items = (await db.execute(select(SpecificItem))).scalars().all()
    total_items = len(items)
    total_value = sum(item.price for item in items)

    ledger_items = (await db.execute(select(Ledger))).scalars().all()
    total_income = sum(l.amount for l in ledger_items if l.type == "income")
    total_expense = sum(l.amount for l in ledger_items if l.type == "expense")

    return {
        "total_items": total_items,
        "total_value": total_value,
        "total_income": total_income,
        "total_expense": total_expense,
    }


@router.get("/analytics/category-stats")
async def get_category_stats(db: AsyncSession = Depends(get_db)):
    categories = (await db.execute(select(Category))).scalars().all()
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()

    cat_map = {c.id: c.name for c in categories}
    cat_sub_map: dict[int, int] = {}
    for sc in sub_cats:
        cat_sub_map[sc.category_id] = cat_sub_map.get(sc.category_id, 0) + sc.quantity

    return [
        {"name": cat_map.get(cid, ""), "value": qty}
        for cid, qty in cat_sub_map.items()
    ]


@router.get("/analytics/monthly-compare")
async def get_monthly_compare(db: AsyncSession = Depends(get_db)):
    from datetime import datetime

    ledger_items = (await db.execute(select(Ledger))).scalars().all()
    month_map: dict[str, dict[str, float]] = {}

    for item in ledger_items:
        key = item.date.strftime("%Y-%m")
        if key not in month_map:
            month_map[key] = {"income": 0.0, "expense": 0.0}
        if item.type == "income":
            month_map[key]["income"] += item.amount
        else:
            month_map[key]["expense"] += item.amount

    return [
        {"month": k, "income": v["income"], "expense": v["expense"]}
        for k, v in sorted(month_map.items())
    ]


# ── Notification CRUD ──

@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(db: AsyncSession = Depends(get_db)):
    from models.notification import Notification

    result = await db.execute(
        select(Notification).order_by(Notification.created_at.desc())
    )
    return result.scalars().all()


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    from models.notification import Notification

    item = await db.get(Notification, notification_id)
    if not item:
        raise HTTPException(404, "Notification not found")
    item.is_read = True
    await db.commit()
    return {"ok": True}


@router.post("/notifications/check")
async def check_notifications(db: AsyncSession = Depends(get_db)):
    from models.notification import Notification
    from models.specific_item import SpecificItem
    from models.budget import Budget

    created = 0

    # Check expired items
    items = (await db.execute(select(SpecificItem))).scalars().all()
    now = datetime.now()
    for item in items:
        if item.expire_date and item.expire_date < now:
            existing = (
                await db.execute(
                    select(Notification).where(
                        Notification.type == "expiry",
                        Notification.related_id == item.id,
                        Notification.is_read == False,
                    )
                )
            ).scalars().first()
            if not existing:
                n = Notification(
                    type="expiry",
                    message=f"物品 {item.name} 已过期",
                    related_id=item.id,
                )
                db.add(n)
                created += 1

    await db.commit()
    return {"created": created}


# ── Tag CRUD ──

@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    from models.tag import Tag

    result = await db.execute(select(Tag))
    return result.scalars().all()


@router.post("/tags", response_model=TagResponse)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    from models.tag import Tag

    item = Tag(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int, data: TagUpdate, db: AsyncSession = Depends(get_db)
):
    from models.tag import Tag

    item = await db.get(Tag, tag_id)
    if not item:
        raise HTTPException(404, "Tag not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    from models.tag import Tag
    from models.item_tag import ItemTag

    item = await db.get(Tag, tag_id)
    if not item:
        raise HTTPException(404, "Tag not found")
    await db.execute(delete(ItemTag).where(ItemTag.tag_id == tag_id))
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.post("/items/{item_id}/tags/{tag_id}")
async def add_tag_to_item(item_id: int, tag_id: int, db: AsyncSession = Depends(get_db)):
    from models.item_tag import ItemTag

    existing = (
        await db.execute(
            select(ItemTag).where(ItemTag.item_id == item_id, ItemTag.tag_id == tag_id)
        )
    ).scalars().first()
    if existing:
        return {"ok": True}

    item_tag = ItemTag(item_id=item_id, tag_id=tag_id)
    db.add(item_tag)
    await db.commit()
    return {"ok": True}


@router.delete("/items/{item_id}/tags/{tag_id}")
async def remove_tag_from_item(item_id: int, tag_id: int, db: AsyncSession = Depends(get_db)):
    from models.item_tag import ItemTag

    await db.execute(
        delete(ItemTag).where(ItemTag.item_id == item_id, ItemTag.tag_id == tag_id)
    )
    await db.commit()
    return {"ok": True}


@router.get("/items/{item_id}/tags", response_model=list[TagResponse])
async def get_item_tags(item_id: int, db: AsyncSession = Depends(get_db)):
    from models.tag import Tag
    from models.item_tag import ItemTag

    result = await db.execute(
        select(Tag).join(ItemTag, ItemTag.tag_id == Tag.id).where(ItemTag.item_id == item_id)
    )
    return result.scalars().all()


# ── Stock Alert ──

@router.get("/alerts")
async def get_stock_alerts(threshold: int = 5, db: AsyncSession = Depends(get_db)):
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()
    alerts = []
    for sc in sub_cats:
        if sc.quantity <= threshold:
            alerts.append({
                "id": sc.id,
                "type": "low_stock",
                "message": f"{sc.name} 库存不足 (剩余 {sc.quantity} {sc.unit})",
                "quantity": sc.quantity,
                "threshold": threshold,
            })
    return alerts


@router.get("/alerts/config")
async def get_alert_config():
    return {"threshold": 5}


@router.put("/alerts/config")
async def update_alert_config(threshold: int = 5):
    return {"threshold": threshold}


# ── Recurring Bill CRUD ──

@router.get("/recurring", response_model=list[RecurringBillResponse])
async def list_recurring(db: AsyncSession = Depends(get_db)):
    from models.recurring import RecurringBill

    result = await db.execute(select(RecurringBill))
    return result.scalars().all()


@router.post("/recurring", response_model=RecurringBillResponse)
async def create_recurring(data: RecurringBillCreate, db: AsyncSession = Depends(get_db)):
    from models.recurring import RecurringBill

    item = RecurringBill(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/recurring/{bill_id}", response_model=RecurringBillResponse)
async def update_recurring(
    bill_id: int, data: RecurringBillUpdate, db: AsyncSession = Depends(get_db)
):
    from models.recurring import RecurringBill

    item = await db.get(RecurringBill, bill_id)
    if not item:
        raise HTTPException(404, "Recurring bill not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/recurring/{bill_id}")
async def delete_recurring(bill_id: int, db: AsyncSession = Depends(get_db)):
    from models.recurring import RecurringBill

    item = await db.get(RecurringBill, bill_id)
    if not item:
        raise HTTPException(404, "Recurring bill not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.post("/recurring/generate")
async def generate_recurring_bills(db: AsyncSession = Depends(get_db)):
    from models.recurring import RecurringBill

    now = datetime.now()
    result = await db.execute(
        select(RecurringBill).where(
            RecurringBill.is_active == True,
            RecurringBill.next_date <= now,
        )
    )
    bills = result.scalars().all()
    created = 0

    for bill in bills:
        ledger_item = Ledger(
            amount=bill.amount,
            date=now,
            platform=bill.platform,
            description=bill.description,
            person=bill.person,
            type=bill.type,
        )
        db.add(ledger_item)

        if bill.frequency == "monthly":
            bill.next_date = bill.next_date.replace(month=bill.next_date.month + 1) if bill.next_date.month < 12 else bill.next_date.replace(year=bill.next_date.year + 1, month=1)
        elif bill.frequency == "yearly":
            bill.next_date = bill.next_date.replace(year=bill.next_date.year + 1)
        created += 1

    await db.commit()
    return {"created": created}


# ── File Upload ──

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    import os
    from pathlib import Path

    upload_dir = Path(__file__).parent.parent / "uploads"
    upload_dir.mkdir(exist_ok=True)

    file_ext = file.filename.split(".")[-1] if file.filename else "bin"
    file_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_path = upload_dir / file_name

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    return {"path": str(file_path), "filename": file_name}


# ── Backup ──

@router.post("/backup")
async def create_backup_endpoint(db: AsyncSession = Depends(get_db)):
    from core.backup import create_backup

    categories = (await db.execute(select(Category))).scalars().all()
    sub_cats = (await db.execute(select(SubCategory))).scalars().all()
    items = (await db.execute(select(SpecificItem))).scalars().all()
    ledger_items = (await db.execute(select(Ledger))).scalars().all()

    data = {
        "categories": [{"id": c.id, "name": c.name, "description": c.description, "icon": c.icon} for c in categories],
        "sub_categories": [{"id": s.id, "category_id": s.category_id, "name": s.name, "unit": s.unit, "quantity": s.quantity} for s in sub_cats],
        "items": [{"id": i.id, "name": i.name, "price": i.price, "description": i.description} for i in items],
        "ledger": [{"id": l.id, "amount": l.amount, "date": str(l.date), "type": l.type, "description": l.description} for l in ledger_items],
    }

    filename = create_backup(data)
    return {"filename": filename}


@router.get("/backup/list")
async def list_backups_endpoint():
    from core.backup import list_backups

    return list_backups()


# ── Currencies ──

CURRENCIES = [
    {"code": "CNY", "name": "人民币", "symbol": "¥"},
    {"code": "USD", "name": "美元", "symbol": "$"},
    {"code": "EUR", "name": "欧元", "symbol": "€"},
    {"code": "GBP", "name": "英镑", "symbol": "£"},
    {"code": "JPY", "name": "日元", "symbol": "¥"},
    {"code": "KRW", "name": "韩元", "symbol": "₩"},
    {"code": "HKD", "name": "港币", "symbol": "HK$"},
    {"code": "TWD", "name": "新台币", "symbol": "NT$"},
]


@router.get("/currencies")
async def list_currencies():
    return CURRENCIES


# ── Pricing CRUD ──

@router.get("/pricing", response_model=list[PricingResponse])
async def list_pricing(
    sub_category_id: int | None = None,
    q: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    from models.pricing import Pricing
    from models.sub_category import SubCategory

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
            id=p.id,
            sub_category_id=p.sub_category_id,
            sub_category_name=sc.name,
            name=p.name,
            cost=p.cost,
            suggested_price=p.suggested_price,
            discount=p.discount,
            description=p.description,
            notes=p.notes,
            record_date=p.record_date,
        )
        for p, sc in rows
    ]


@router.post("/pricing", response_model=PricingResponse)
async def create_pricing(data: PricingCreate, db: AsyncSession = Depends(get_db)):
    from models.pricing import Pricing

    item = Pricing(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return PricingResponse(
        id=item.id,
        sub_category_id=item.sub_category_id,
        sub_category_name="",
        name=item.name,
        cost=item.cost,
        suggested_price=item.suggested_price,
        discount=item.discount,
        description=item.description,
        notes=item.notes,
        record_date=item.record_date,
    )


@router.put("/pricing/{pricing_id}", response_model=PricingResponse)
async def update_pricing(
    pricing_id: int, data: PricingUpdate, db: AsyncSession = Depends(get_db)
):
    from models.pricing import Pricing

    item = await db.get(Pricing, pricing_id)
    if not item:
        raise HTTPException(404, "Pricing not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    await db.commit()
    await db.refresh(item)
    return PricingResponse(
        id=item.id,
        sub_category_id=item.sub_category_id,
        sub_category_name="",
        name=item.name,
        cost=item.cost,
        suggested_price=item.suggested_price,
        discount=item.discount,
        description=item.description,
        notes=item.notes,
        record_date=item.record_date,
    )


@router.delete("/pricing/{pricing_id}")
async def delete_pricing(pricing_id: int, db: AsyncSession = Depends(get_db)):
    from models.pricing import Pricing

    item = await db.get(Pricing, pricing_id)
    if not item:
        raise HTTPException(404, "Pricing not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


# ── Pricing Category CRUD ──

@router.get("/pricing-categories", response_model=list[PricingCategoryResponse])
async def list_pricing_categories(db: AsyncSession = Depends(get_db)):
    from models.pricing_category import PricingCategory

    result = await db.execute(select(PricingCategory))
    return result.scalars().all()


@router.post("/pricing-categories", response_model=PricingCategoryResponse)
async def create_pricing_category(data: PricingCategoryCreate, db: AsyncSession = Depends(get_db)):
    from models.pricing_category import PricingCategory

    item = PricingCategory(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/pricing-categories/{cat_id}", response_model=PricingCategoryResponse)
async def update_pricing_category(
    cat_id: int, data: PricingCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    from models.pricing_category import PricingCategory

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
    from models.pricing_category import PricingCategory

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
    from models.pricing_sub_category import PricingSubCategory

    stmt = select(PricingSubCategory)
    if category_id is not None:
        stmt = stmt.where(PricingSubCategory.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/pricing-sub-categories", response_model=PricingSubCategoryResponse)
async def create_pricing_sub_category(data: PricingSubCategoryCreate, db: AsyncSession = Depends(get_db)):
    from models.pricing_sub_category import PricingSubCategory

    item = PricingSubCategory(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/pricing-sub-categories/{sub_id}", response_model=PricingSubCategoryResponse)
async def update_pricing_sub_category(
    sub_id: int, data: PricingSubCategoryUpdate, db: AsyncSession = Depends(get_db)
):
    from models.pricing_sub_category import PricingSubCategory

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
    from models.pricing_sub_category import PricingSubCategory

    item = await db.get(PricingSubCategory, sub_id)
    if not item:
        raise HTTPException(404, "Pricing sub-category not found")
    await db.delete(item)
    await db.commit()
    return {"ok": True}


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
