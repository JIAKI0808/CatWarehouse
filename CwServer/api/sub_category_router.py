"""细分类（SubCategory）—— 五个标准端点走通用层，`quantity` 保持手写。

列表端点的 `category_id` 过滤正好是「按单字段等值过滤」，交给 `list_filter` 即可，
不必手写。`/sub-categories/{sub_id}/quantity` 是跨表计数，不属于标准 CRUD。
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from dataManager.crud.registry import register_crud
from dataManager.crud.router import build_crud_router
from dataManager.crud.spec import CrudNames, CrudSpec
from models.specific_item import SpecificItem
from models.sub_category import SubCategory
from schemas.sub_category import SubCategoryCreate, SubCategoryResponse, SubCategoryUpdate

SUB_CATEGORY = register_crud(
    CrudSpec(
        name="sub_category",
        model=SubCategory,
        response=SubCategoryResponse,
        path="/sub-categories",
        id_param="sub_id",
        not_found="SubCategory not found",
        create=SubCategoryCreate,
        update=SubCategoryUpdate,
        list_filter="category_id",
        names=CrudNames(
            list="list_sub_categories",
            get="get_sub_category",
            create="create_sub_category",
            update="update_sub_category",
            delete="delete_sub_category",
        ),
    )
)

router: APIRouter = build_crud_router(SUB_CATEGORY)


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
