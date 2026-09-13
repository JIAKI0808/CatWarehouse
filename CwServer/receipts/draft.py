from __future__ import annotations

from pydantic import BaseModel, Field

from ocr.types import Receipt

DIRECTION_IN = "in"    # 入库：库存累加，账目默认支出
DIRECTION_OUT = "out"  # 出库：库存扣减，账目默认收入

LEDGER_DEFAULT_TYPE = "expense"
LEDGER_OUTBOUND_TYPE = "income"


class ReceiptItemDraft(BaseModel):
    """一条明细的草稿。

    字段全部可由客户端修改后再提交；`sub_category_id` 用于**逐项**指定落库分类，
    留空则回落到顶层 `ReceiptDraft.sub_category_id`。
    """

    name: str
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None
    selected: bool = True
    sub_category_id: int | None = None


class ReceiptDraft(BaseModel):
    """落库草稿 —— 识别结果与数据库之间唯一的中间契约。

    设计上**不依赖任何数据库模型**：分类由调用方决定（不做猜测），
    映射规则 `draft_from_receipt()` 是纯函数，写库由 `ReceiptSink` 负责。
    这样识别、映射、落库三层可各自替换。

    `direction` 决定库存是累加还是扣减、账目默认是支出还是收入。
    默认 `in`，故既有的票据入库调用方行为**完全不变**。
    `voice/types.py` 里有一份同值的 `DIRECTION_IN|OUT`：
    那是为了让语音层不依赖本模块而刻意复制的两个字面量。
    """

    sub_category_id: int | None = None
    recorder: str = ""
    image_path: str | None = None
    items: list[ReceiptItemDraft] = Field(default_factory=list)
    direction: str = DIRECTION_IN
    update_stock: bool = True
    create_ledger: bool = False
    ledger: dict = Field(default_factory=dict)
    meta: dict = Field(default_factory=dict)

    def is_outbound(self) -> bool:
        """是否出库：决定库存扣减方向与账目默认类型。"""
        return self.direction == DIRECTION_OUT

    def selected_items(self) -> list[ReceiptItemDraft]:
        """勾选了要入库的明细。"""
        return [item for item in self.items if item.selected]

    def total_amount(self) -> float:
        """已勾选明细的金额合计。"""
        return _sum_amounts(self.selected_items())


class ApplyResult(BaseModel):
    """落库结果，逐项如实汇报（含被跳过的原因）。"""

    created_items: list[int] = Field(default_factory=list)
    updated_sub_categories: list[int] = Field(default_factory=list)
    created_ledger_id: int | None = None
    skipped: list[str] = Field(default_factory=list)
    clamped: list[str] = Field(default_factory=list)
    """出库扣减被**归零**的明细及其说明。

    库存不足时按用户要求归零而不是扣成负数，但归零必须**说出来** ——
    静默改数会让人以为库存是准的。这里记下「原本要扣多少、实际只扣了多少」。
    """


def _sum_amounts(items: list[ReceiptItemDraft]) -> float:
    """明细金额合计（忽略没有金额的行）。"""
    return round(sum(item.amount for item in items if item.amount is not None), 2)


def _describe(receipt: Receipt) -> str:
    """账目描述：抬头 + 前几个品名。"""
    names = "、".join(item.name for item in receipt.items[:3])
    return f"票据入库: {names}" if names else "票据入库"


def draft_from_receipt(receipt: Receipt) -> ReceiptDraft:
    """把识别结果映射成可编辑草稿（纯函数，不碰数据库）。

    刻意**不猜分类**：`sub_category_id` 留空由调用方决定；
    `create_ledger` 默认 False，避免「识别一下」就产生账目。
    票面总额优先作为账目默认金额，缺失时用明细金额合计。
    """
    items = [
        ReceiptItemDraft(
            name=item.name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            amount=item.amount,
        )
        for item in receipt.items
    ]
    total = receipt.total if receipt.total is not None else _sum_amounts(items)
    return ReceiptDraft(
        recorder=receipt.merchant or "",
        items=items,
        ledger={
            "amount": total,
            "date": receipt.date,
            "platform": receipt.merchant or "",
            "type": LEDGER_DEFAULT_TYPE,
            "description": _describe(receipt),
        },
        meta={
            "source": "ocr_receipt",
            "doc_type": receipt.doc_type,
            "merchant": receipt.merchant,
            "date": receipt.date,
            "order_no": receipt.order_no,
            "total": receipt.total,
        },
    )
