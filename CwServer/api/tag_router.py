import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.tag import Tag
from models.item_tag import ItemTag
from schemas.tag import TagCreate, TagUpdate, TagResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/tags", response_model=list[TagResponse])
async def list_tags(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Tag))
    return result.scalars().all()


@router.post("/tags", response_model=TagResponse)
async def create_tag(data: TagCreate, db: AsyncSession = Depends(get_db)):
    item = Tag(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/tags/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: int, data: TagUpdate, db: AsyncSession = Depends(get_db)):
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
    item = await db.get(Tag, tag_id)
    if not item:
        raise HTTPException(404, "Tag not found")
    await db.execute(delete(ItemTag).where(ItemTag.tag_id == tag_id))
    await db.delete(item)
    await db.commit()
    return {"ok": True}


@router.post("/items/{item_id}/tags/{tag_id}")
async def add_tag_to_item(item_id: int, tag_id: int, db: AsyncSession = Depends(get_db)):
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
    await db.execute(delete(ItemTag).where(ItemTag.item_id == item_id, ItemTag.tag_id == tag_id))
    await db.commit()
    return {"ok": True}


@router.get("/items/{item_id}/tags", response_model=list[TagResponse])
async def get_item_tags(item_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Tag).join(ItemTag, ItemTag.tag_id == Tag.id).where(ItemTag.item_id == item_id)
    )
    return result.scalars().all()
