"""库存领域的抽象工厂实现。

`dataManager/factory.py::get_factory("inventory", db)` 就是从这里取的。
改造前这一族从未被任何代码调用过；现在 `api/item_router.py` 通过
`get_factory("inventory", db)` 拿到它，抽象工厂由「死代码」变成「活的」。
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.base import DataManagerFactory, DataProduct, Repository, Validator
from dataManager.inventory.item import Item
from dataManager.inventory.repository import ItemRepository
from dataManager.inventory.validator import ItemValidator


class InventoryManagerFactory(DataManagerFactory):
    """商品明细这一族的产品 / 校验器 / 仓储。"""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    def create_product(self, **kwargs) -> DataProduct:
        """组合视图产品：`create_product(item=..., sub=...)`。"""
        return Item(**kwargs)

    def create_validator(self) -> Validator:
        """明细校验器（当前与 Pydantic 边界等价，见 `validator.py`）。"""
        return ItemValidator()

    def create_repository(self) -> Repository:
        """绑定 `SpecificItem` 的仓储。"""
        return ItemRepository(self.db)
