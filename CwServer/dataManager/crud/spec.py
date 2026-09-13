"""资源规格：用数据描述「一个资源的标准 CRUD 长什么样」。

设计取向：**一切显式**。端点函数名、路径参数名、404 文案都要求逐字给出，
不允许由约定推导 —— 既有命名并不规则（`list_categories` 是复数、
`get_category` 是单数），任何「复数化 / 驼峰化」的猜测都会改掉 operationId，
进而改掉 `/openapi.json`。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class CrudNames:
    """五个端点的函数名。为 None 表示该端点不生成。

    FastAPI 的 `operationId` 与 `summary` 都由函数名派生，所以这里必须逐字
    对应改造前的既有函数名，否则 `/openapi.json` 会漂移。
    """

    list: str | None = None
    get: str | None = None
    create: str | None = None
    update: str | None = None
    delete: str | None = None

    def has(self, action: str) -> bool:
        """该动作是否要生成端点。"""
        return getattr(self, action) is not None


@dataclass(frozen=True)
class CrudSpec:
    """一个资源的 CRUD 声明。

    `model` 是 SQLAlchemy 模型，`response` / `create` / `update` 是对应的
    Pydantic schema。`list_filter` 给列表端点加一个同名可选查询参数（按该字段
    等值过滤）；`to_response` 是响应钩子，只在响应 schema 带了模型上没有、
    又没有默认值的字段时才需要（如 `BudgetResponse.category_name`）。

    清单里**没有** `list_query`：设计时留了这个口子想要承接联表列表，实际做下来
    那些列表（pricing / budget / ledger）都留在各自文件里手写 —— 把原始代码原样
    搬进一个钩子并没有减少任何东西，只是换了个地方放。没有使用者的旋钮不留。
    """

    name: str
    model: type
    response: type
    path: str
    names: CrudNames
    id_param: str = "id"
    not_found: str = ""
    create: type | None = None
    update: type | None = None
    list_filter: str | None = None
    to_response: Callable[[Any], Any] | None = None

    def actions(self) -> list[str]:
        """按固定顺序返回要生成的端点动作名。"""
        return [a for a in ("list", "get", "create", "update", "delete") if self.names.has(a)]
