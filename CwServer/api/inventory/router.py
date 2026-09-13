"""库存分区的聚合门面。

**没有 prefix、没有 tags** —— 各子路由自带完整路径与标签，这里再包一层前缀或标签
会改掉 `/openapi.json`。本文件只做 include，不产生任何新端点。
"""

from fastapi import APIRouter

from api.inventory.category_router import router as category_router
from api.inventory.sub_category_router import router as sub_category_router
from api.inventory.item_router import router as item_router
from api.inventory.tag_router import router as tag_router
from api.inventory.unit_router import router as unit_router

router = APIRouter()

router.include_router(category_router)
router.include_router(sub_category_router)
router.include_router(item_router)
router.include_router(tag_router)
router.include_router(unit_router)
