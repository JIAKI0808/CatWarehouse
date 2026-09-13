from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from models.ledger import Ledger
from models.specific_item import SpecificItem
from models.sub_category import SubCategory
from receipts.draft import (
    LEDGER_DEFAULT_TYPE,
    LEDGER_OUTBOUND_TYPE,
    ApplyResult,
    ReceiptDraft,
    ReceiptItemDraft,
)

logger = logging.getLogger(__name__)

# 客户端只能通过 ledger 覆盖这些字段，防止任意键打进 ORM
LEDGER_FIELDS = ("amount", "date", "platform", "description", "notes", "person", "type")


class ReceiptSink(Protocol):
    """落库出口协议。

    默认实现是 `InventoryReceiptSink`。想换落库目标（别的表 / 别的业务语义），
    只需实现本协议并在 `api/ocr_router.py` 里换一行构造，
    `ocr/` 与草稿映射都不受影响 —— 这就是本层存在的意义。
    """

    async def write(self, draft: ReceiptDraft) -> ApplyResult:
        """把草稿写入存储。"""
        ...


def _coerce_date(value: object) -> datetime | None:
    """把客户端传来的日期转成 datetime；无法解析返回 None（交给模型默认值）。"""
    if isinstance(value, datetime):
        return value
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


class InventoryReceiptSink:
    """把票据草稿写进 库存(SpecificItem/SubCategory) 与 账本(Ledger)。

    写入语义（想改就改这里，`draft.py` 与 API 不用动）：
      - 每条勾选明细 → 一条 `SpecificItem`；单价优先取票面单价，其次 金额/数量。
      - `update_stock` 为真且明细带数量时，把数量**按 `direction` 的方向**加到所属
        `SubCategory.quantity`：`in` 累加、`out` 扣减；**出库扣不足时归零**并记进
        `ApplyResult.clamped`（不扣成负数，也不静默改数）。
        库存数量只存在子分类上（`SpecificItem` 没有数量列），
        数量/单价/金额摘要同时写进 `SpecificItem.description` 以便追溯。
      - `create_ledger` 为真时额外记一条 `Ledger`；金额为 0 则跳过，
        类型默认取 `direction`（`in` → expense、`out` → income），但可被 `ledger` 覆盖。
      - 全程**单事务**提交，失败不留半截数据。
    """

    def _stock_delta(self, item: ReceiptItemDraft, draft: ReceiptDraft) -> int:
        """库存变动量：入库为正、出库为负。"""
        amount = int(round(float(item.quantity)))
        return -amount if draft.is_outbound() else amount

    def _apply_stock(self, sub: SubCategory, item: ReceiptItemDraft,
                     draft: ReceiptDraft, result: ApplyResult) -> None:
        """把数量变动写进子分类库存；出库扣不足时**归零**并如实汇报。

        归零而不是扣成负数：库存为负不是有效状态，用户多半只是先卖了货、
        还没来得及登记进货。但归零必须**说出来**（记进 `ApplyResult.clamped`），
        否则静默改数会让人以为库存是准的。
        """
        delta = self._stock_delta(item, draft)
        current = int(sub.quantity or 0)
        target = current + delta
        if target < 0:
            result.clamped.append(f"{item.name}: 库存不足已归零（原 {current}，需扣 {-delta}）")
            logger.warning("Stock clamped to 0 for %s: had %d, needed %d", item.name, current, -delta)
            target = 0
        sub.quantity = target
        if sub.id not in result.updated_sub_categories:
            result.updated_sub_categories.append(sub.id)

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def _resolve_sub_category(self, item: ReceiptItemDraft, draft: ReceiptDraft):
        """定位明细的落库子分类；未指定或不存在返回 None。"""
        target = item.sub_category_id or draft.sub_category_id
        if target is None:
            return None
        return await self._db.get(SubCategory, target)

    def _price_of(self, item: ReceiptItemDraft) -> float:
        """单价：优先票面单价，其次 金额/数量，最后退化为金额。"""
        if item.unit_price is not None:
            return float(item.unit_price)
        if item.amount is not None and item.quantity:
            return round(float(item.amount) / float(item.quantity), 4)
        return float(item.amount or 0.0)

    def _description_of(self, item: ReceiptItemDraft) -> str:
        """明细描述：把数量/单价/金额摘要记下来（SpecificItem 无数量列）。"""
        parts = []
        if item.quantity is not None:
            parts.append(f"数量 {item.quantity:g}")
        if item.unit_price is not None:
            parts.append(f"单价 {item.unit_price:g}")
        if item.amount is not None:
            parts.append(f"金额 {item.amount:g}")
        return " / ".join(parts)

    async def _write_item(self, item: ReceiptItemDraft, draft: ReceiptDraft, result: ApplyResult) -> None:
        """写入一条明细，并按需把数量累加到子分类。"""
        sub = await self._resolve_sub_category(item, draft)
        if sub is None:
            result.skipped.append(f"{item.name}: 未指定或找不到分类")
            return
        model = SpecificItem(
            sub_category_id=sub.id,
            name=item.name,
            price=self._price_of(item),
            recorder=draft.recorder,
            description=self._description_of(item),
            image_path=draft.image_path,
            extra=json.dumps(draft.meta, ensure_ascii=False) if draft.meta else "{}",
        )
        self._db.add(model)
        await self._db.flush()  # 取回自增 id
        result.created_items.append(model.id)
        if draft.update_stock and item.quantity:
            self._apply_stock(sub, item, draft, result)

    async def _write_ledger(self, draft: ReceiptDraft) -> int | None:
        """按草稿的 ledger 覆盖项写一条账目；金额为 0 则跳过。"""
        overrides = {k: v for k, v in (draft.ledger or {}).items() if k in LEDGER_FIELDS}
        amount = overrides.pop("amount", None)
        if amount is None:
            amount = draft.total_amount()
        if not amount:
            return None
        fields: dict = {"amount": float(amount)}
        date = _coerce_date(overrides.pop("date", None))
        if date is not None:
            fields["date"] = date
        fields.update(overrides)
        fields.setdefault("type", LEDGER_OUTBOUND_TYPE if draft.is_outbound() else LEDGER_DEFAULT_TYPE)
        fields.setdefault("platform", draft.recorder)
        ledger = Ledger(**fields)
        self._db.add(ledger)
        await self._db.flush()
        return ledger.id

    async def write(self, draft: ReceiptDraft) -> ApplyResult:
        """把草稿写入库存与账本，单事务提交。"""
        result = ApplyResult()
        for item in draft.selected_items():
            await self._write_item(item, draft, result)
        if draft.create_ledger:
            result.created_ledger_id = await self._write_ledger(draft)
        await self._db.commit()
        logger.info(
            "Receipt sink wrote items=%d sub_categories=%d ledger=%s skipped=%d",
            len(result.created_items), len(result.updated_sub_categories),
            result.created_ledger_id, len(result.skipped),
        )
        return result
