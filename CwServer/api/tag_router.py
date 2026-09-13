"""标签（Tag）—— list/create/update 走通用层，其余端点保持手写。

`delete_tag` **刻意不交给通用层**：它在删除前要先清掉 `ItemTag` 里的关联行，
比标准 CRUD 多一步，硬塞进模板反而要把「例外」写成模板的一部分。
标签与条目的关联三个端点同理，都是这一处业务特有的。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.item_tag import ItemTag
from models.tag import Tag
from schemas.tag import TagCreate, TagResponse, TagUpdate

TAG = register_crud(
    CrudSpec(
        name="tag",
        model=Tag,
        response=TagResponse,
        path="/tags",
        id_param="tag_id",
        not_found="Tag not found",
        create=TagCreate,
        update=TagUpdate,
        names=CrudNames(list="list_tags", create="create_tag", update="update_tag"),
    )
)

router: APIRouter = build_crud_router(TAG)


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
