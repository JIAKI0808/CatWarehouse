import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.backup import create_backup, list_backups
from models.category import Category
from models.sub_category import SubCategory
from models.specific_item import SpecificItem
from models.ledger import Ledger

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/backup")
async def create_backup_endpoint(db: AsyncSession = Depends(get_db)):
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
    return list_backups()
