"""库存明细的「组合视图」产品。

列表响应里混着两张表的信息：明细自己的字段，加上所属子分类的
`name` / `quantity` / `unit`。`Item` 就是那个组合的载体 —— 拿两个 ORM 对象，
`to_dict()` 给出可直接交给 `response_model` 的形状。

原先这段拼装写死在 `api/item_router.py::list_items` 里，现在由本类承担，
`DataProduct` 这个 ABC 也就第一次有了真实使用者。
"""

from __future__ import annotations

from typing import Any

from dataManager.base import DataProduct


class Item(DataProduct):
    """一条明细 + 所属子分类。"""

    def __init__(self, item: Any, sub: Any) -> None:
        self._item = item
        self._sub = sub

    def to_dict(self) -> dict:
        """字段与原 `list_items` 里手工构造的 `SpecificItemResponse` **逐一对应**。

        刻意**不含** `expire_date` / `is_expired`：原列表端点就没有传这两个字段，
        它们取的是 schema 默认值（`None` / `False`）。补上会让带过期信息的明细
        在列表里凭空多出两个字段 —— 那是接口变化，不是重构。
        """
        return {
            "id": self._item.id,
            "sub_category_id": self._item.sub_category_id,
            "sub_category_name": self._sub.name,
            "quantity": self._sub.quantity,
            "unit": self._sub.unit,
            "name": self._item.name,
            "entry_date": self._item.entry_date,
            "update_date": self._item.update_date,
            "recorder": self._item.recorder,
            "price": self._item.price,
            "description": self._item.description,
        }
