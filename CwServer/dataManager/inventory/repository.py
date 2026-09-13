"""库存明细（SpecificItem）的仓储。

标准五法全部继承自通用层 `dataManager.crud.repository.SqlAlchemyRepository`，
本类只负责把模型绑定到 `SpecificItem`。

改造前这个文件是 80 行、把五个方法各写一遍、且**从没有任何调用方**；
现在它是通用层的第一个领域实现，由 `InventoryManagerFactory` 产出、
`api/item_router.py` 真实调用。
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.crud.repository import SqlAlchemyRepository
from models.specific_item import SpecificItem


class ItemRepository(SqlAlchemyRepository):
    """商品明细仓储。"""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, SpecificItem)
