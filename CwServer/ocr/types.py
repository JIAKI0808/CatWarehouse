from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

# bbox 统一约定：(x, y, w, h)，坐标原点在图像左上角，单位为像素。
BBox = tuple[int, int, int, int]


@dataclass
class TextLine:
    """一条识别出的文本行及其在「处理后图像」上的位置。

    Attributes:
        text: 识别出的文本内容。
        bbox: 该文本行外接矩形 (x, y, w, h)。
        confidence: 识别置信度，取值 0.0 ~ 1.0。
    """

    text: str
    bbox: BBox
    confidence: float = 1.0


@dataclass
class ReceiptItem:
    """票据上的一条明细行。

    金额字段允许为 None，表示该列未能从图中解析出来。
    """

    name: str
    quantity: float | None = None
    unit_price: float | None = None
    amount: float | None = None


@dataclass
class LowConfidenceLine:
    """置信度低于阈值的识别文本行。

    只**上报**，不影响解析结果 —— 见 `Receipt.low_confidence` 的说明。
    """

    text: str
    confidence: float


@dataclass
class Receipt:
    """通用票据识别结果。

    doc_type 取值：invoice / receipt / delivery / unknown。

    Attributes:
        low_confidence: 置信度低于阈值的文本行。**只上报，不影响解析**。
    """

    doc_type: str = "unknown"
    merchant: str | None = None
    date: str | None = None
    order_no: str | None = None
    items: list[ReceiptItem] = field(default_factory=list)
    total: float | None = None
    raw_text: str = ""
    extra: dict = field(default_factory=dict)
    #: 2026-09-14「OCR 优化」环新增。此前 `TextLine.confidence` 一直被采集却**无人读取**，
    #: `OcrConfig.confidence_threshold` 也是**配了不生效**的旋钮。
    #:
    #: **为什么是「上报」而不是「丢弃」**：把低置信度的行直接扔掉，会**静默少一条明细**，
    #: 合计随之变错 —— 那比留着一条可能不准的行更糟。所以解析照旧跑全部行，
    #: 这里如实列出哪些行不可靠，由调用方决定怎么提示。
    #: （与 receipts 那边「出库扣不足要归零并汇报」同一个取向：不静默。）
    low_confidence: list[LowConfidenceLine] = field(default_factory=list)

    def to_dict(self) -> dict:
        """转换为可直接 JSON 序列化的 dict。"""
        return {
            "doc_type": self.doc_type,
            "merchant": self.merchant,
            "date": self.date,
            "order_no": self.order_no,
            "items": [
                {
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "amount": item.amount,
                }
                for item in self.items
            ],
            "total": self.total,
            "raw_text": self.raw_text,
            "extra": self.extra,
            "low_confidence": [
                {"text": line.text, "confidence": line.confidence}
                for line in self.low_confidence
            ],
        }


class UpstreamRejectedError(RuntimeError):
    """远程 OCR 服务把我们的请求判为无效（HTTP 4xx）。

    与「5xx / 连不上」必须分开：那类是**服务不可用**，端点回 503 让前端稍后重试；
    这类是**你给的图片我用不了**（格式不对、损坏等），回 400 才准确。

    与 `voice/types.py` 里同名的类**刻意各留一份**：`ocr` 与 `voice` 两个包
    按设计互不依赖（见 plan.md §11.1 的导入约定），为共用这几行而让其中一个
    去 import 另一个，是把解耦换成了省事。风险是两处可能漂移 —— 端点的
    `except` 顺序已各自覆盖，测试也分别断言。
    """


@runtime_checkable
class LineOcrEngine(Protocol):
    """可返回带坐标文本框的 OCR 引擎协议。

    既有 OcrEngine.recognize() 只返回纯文本，无法支撑表格列对齐；
    能提供 bbox 的引擎额外实现本协议，pipeline 会优先使用它。
    """

    def recognize_lines(self, image: bytes) -> list[TextLine]:
        """识别图像中的文本行及其位置。"""
        ...
