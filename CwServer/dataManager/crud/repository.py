"""通用仓储：把 `AsyncSession` 适配成统一的存取接口。

实现 `dataManager/base.py` 的 `Repository` ABC —— 该 ABC 此前从没有真实使用者，
本类是它的第一个具体实现，抽象契约因此从「死代码」变成「活的」。

刻意返回 **ORM 实例**而不是 DTO：既有的端点 `response_model` 都带
`from_attributes=True`，换成 DTO（比如 `dataManager/inventory/item.py` 的 `Item`）
会让响应里凭空少掉它没有的列。
"""

from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dataManager.base import Repository


class SqlAlchemyRepository(Repository):
    """一个模型 + 一个会话 = 一套标准存取。"""

    def __init__(self, db: AsyncSession, model: type) -> None:
        self._db = db
        self._model = model

    @property
    def model(self) -> type:
        """本仓储负责的模型。"""
        return self._model

    async def get(self, id: int) -> Any | None:
        """按主键取一条，不存在返回 None。"""
        return await self._db.get(self._model, id)

    async def get_all(self) -> Sequence[Any]:
        """取全部。"""
        result = await self._db.execute(select(self._model))
        return result.scalars().all()

    async def find(self, field: str, value: Any) -> Sequence[Any]:
        """按单个字段等值过滤。"""
        column = getattr(self._model, field)
        result = await self._db.execute(select(self._model).where(column == value))
        return result.scalars().all()

    async def create(self, data: dict) -> Any:
        """新建一条并返回持久化后的实例。"""
        obj = self._model(**data)
        self._db.add(obj)
        await self._db.commit()
        await self._db.refresh(obj)
        return obj

    async def update(self, id: int, data: dict) -> Any | None:
        """按主键部分更新，不存在返回 None。"""
        obj = await self._db.get(self._model, id)
        if obj is None:
            return None
        for key, value in data.items():
            setattr(obj, key, value)
        await self._db.commit()
        await self._db.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        """按主键删除，返回是否真的删掉了。"""
        obj = await self._db.get(self._model, id)
        if obj is None:
            return False
        await self._db.delete(obj)
        await self._db.commit()
        return True
