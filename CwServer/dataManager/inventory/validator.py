"""库存明细的校验器。

⚠️ **它当前不会拒绝任何请求，这是刻意的，不是漏写。**

本应用唯一的输入校验层是 Pydantic（`schemas/specific_item.py`），
`SpecificItemCreate` 已经把「`name` 必须是字符串、`sub_category_id` 必须是整数」
这两条钉死了。所以这里再查一遍是**重合**的，永远不会触发。

为什么不再加一条「更有用」的规则（例如 `price >= 0`、`name` 非空白）？
因为那会**改变既有请求的响应** —— 现在 `price=-5` 与 `name=""` 都是 200，
加了规则就变成 422。本次整改的硬目标是「接口与行为不变」，
不能为了制造「校验器在工作」的假象去改接口。

那留着它干什么：`DataManagerFactory.create_validator()` 这个接缝是**校验要离开
Pydantic 时**的落点（比如将来把校验下沉到领域层）。它在调用路径上、会被执行，
只是当前与 Pydantic 等价。这里把这个事实写清楚，而不是藏起来。

改造前它校验的是 `data["quantity"]` —— 而 `Item`、`SpecificItem`、`SpecificItemCreate`
**都没有** quantity 这个字段（库存数量在 `SubCategory` 上），所以那段校验从未生效过。
"""

from __future__ import annotations

from dataManager.base import Validator


class ItemValidator(Validator):
    """校验明细的新建入参，规则与 Pydantic 边界保持一致。"""

    def __init__(self) -> None:
        self._errors: list[str] = []

    def validate(self, data: dict) -> bool:
        """检查 Pydantic 已经保证的那两条不变量（因此不会新增拒绝）。"""
        self._errors = []
        if not isinstance(data.get("name"), str):
            self._errors.append("name must be a string")
        if not isinstance(data.get("sub_category_id"), int) or isinstance(
            data.get("sub_category_id"), bool
        ):
            self._errors.append("sub_category_id must be an integer")
        return not self._errors

    def errors(self) -> list[str]:
        """上一次 `validate()` 收集到的错误。"""
        return self._errors
