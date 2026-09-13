from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

DIRECTION_IN = "in"    # 入库：库存累加，账目默认支出
DIRECTION_OUT = "out"  # 出库：库存扣减，账目默认收入


class LlmReplyError(ValueError):
    """大模型返回无法解析成结构化指令。

    继承 `ValueError`，所以"输入有问题"与"上游返回不可用"可以一起被
    `except ValueError` 兜住；端点则**先**捕这个子类回 502，再捕 `ValueError` 回 400，
    从而把「用户录音没内容」和「模型返回了一堆废话」两种失败分开。
    """


class UpstreamRejectedError(RuntimeError):
    """上游把我们的请求判为无效（HTTP 4xx）。

    与「5xx / 连不上」必须分开：那类是**服务不可用**，端点回 503 让前端稍后重试；
    这类是**你给的素材我用不了**（例如音频格式不对），回 400 才是准确的语义。

    这个区分是端到端实测暴露出来的：坏音频原先被上游 422 拒绝，
    却因为所有 HTTP 错误都被揉成 `RuntimeError` 而回成了 503，误导了调用方。
    """


@dataclass
class Transcript:
    """一段音频的识别结果。"""

    text: str
    language: str | None = None
    duration: float | None = None
    segments: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转成可直接 JSON 序列化的字典。"""
        return {
            "text": self.text,
            "language": self.language,
            "duration": self.duration,
            "segments": self.segments,
        }


@dataclass
class VoiceItem:
    """口述里的一条明细。

    `category_hint` 是口语中**说出来的**分类名词（如「调料」），
    不是数据库 id —— `voice/` 不认识数据库，映射成 `sub_category_id`
    由端点层负责（见 plan.md §15.2）。
    """

    name: str
    quantity: float | None = None
    unit: str | None = None
    unit_price: float | None = None
    amount: float | None = None
    category_hint: str | None = None

    def to_dict(self) -> dict:
        """转成可直接 JSON 序列化的字典。"""
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "unit_price": self.unit_price,
            "amount": self.amount,
            "category_hint": self.category_hint,
        }


@dataclass
class VoiceCommand:
    """口述解析出的结构化指令 —— 本模块对外的核心产物。"""

    direction: str = DIRECTION_IN
    items: list[VoiceItem] = field(default_factory=list)
    merchant: str | None = None
    date: str | None = None
    total: float | None = None
    note: str | None = None
    raw_text: str = ""
    extra: dict = field(default_factory=dict)

    def is_outbound(self) -> bool:
        """是否出库。"""
        return self.direction == DIRECTION_OUT

    def to_dict(self) -> dict:
        """转成可直接 JSON 序列化的字典。"""
        return {
            "direction": self.direction,
            "items": [item.to_dict() for item in self.items],
            "merchant": self.merchant,
            "date": self.date,
            "total": self.total,
            "note": self.note,
            "raw_text": self.raw_text,
            "extra": self.extra,
        }


@runtime_checkable
class AsrEngine(Protocol):
    """语音识别引擎协议（本地模型与远程接口都实现它）。

    与 `ocr.LineOcrEngine` 是同样的思路：接口只约定「给我音频字节，还我文本」，
    引擎怎么实现（本机推理 / HTTP 调用）与上层完全无关。
    """

    def transcribe(self, audio: bytes, filename: str = "") -> Transcript:
        """把音频字节转成文本。"""
        ...


@runtime_checkable
class LlmClient(Protocol):
    """大模型客户端协议（OpenAI 兼容与 Claude 原生都实现它）。

    故意只留「system + user → 文本」这一个方法：
    两家接口的差异（路径、鉴权头、取值路径）封装在各自实现里，
    上层只关心返回的文本里有没有可解析的 JSON（见 `prompt.extract_json`）。
    """

    def complete(self, system: str, user: str) -> str:
        """返回模型生成的原始文本。"""
        ...
