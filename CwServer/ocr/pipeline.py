from __future__ import annotations

from collections.abc import Sequence

import cv2
import numpy as np

from ocr.base import OcrEngine, OcrObserver
from ocr.engine_http import HttpOcrEngine
from ocr.engine_paddle import PaddleOcrEngine
from ocr.events import OcrEvent
from ocr.layout import detect_text_lines
from ocr.parser import parse_receipt
from ocr.preprocess import PreprocessResult, preprocess
from ocr.settings import DEFAULT_MIN_CONFIDENCE, OcrSettings, load_settings
from ocr.types import BBox, LineOcrEngine, LowConfidenceLine, Receipt, TextLine

CROP_PAD = 4  # 回退路径逐行裁剪时四周留的边距，避免切掉笔画
_EVENT_METHODS = ("on_recognition_start", "on_recognition_progress",
                  "on_recognition_complete", "on_recognition_error")
_EVENT_KINDS = ("start", "progress", "complete", "error")


def _encode(img: np.ndarray) -> bytes:
    """把处理后的图像编码成 PNG 字节。

    引擎接口（`OcrEngine` / `LineOcrEngine`）约定入参为 bytes，
    故预处理后的 ndarray 需要回编码才能复用同一套接口。
    """
    ok, buffer = cv2.imencode(".png", img)
    if not ok:
        raise ValueError("cannot encode processed image")
    return buffer.tobytes()


def _crop(img: np.ndarray, bbox: BBox, pad: int = CROP_PAD) -> np.ndarray:
    """按 bbox 裁图，四周留一点边距。"""
    x, y, w, h = bbox
    top, left = max(0, y - pad), max(0, x - pad)
    bottom = min(img.shape[0], y + h + pad)
    right = min(img.shape[1], x + w + pad)
    return img[top:bottom, left:right]


def _single_line(text: str) -> str:
    """把引擎返回的多行文本压成一行，保持与 bbox 一一对应。"""
    return " ".join(text.split())


class ReceiptRecognizer:
    """票据识别流水线：预处理 → 版面 → 文本行 → 字段解析。

    两条取文本行的路径：
      1. 引擎实现 `LineOcrEngine`（如 PaddleOcrEngine / HttpOcrEngine）→ 直接拿带 bbox 的文本行；
      2. 否则回退为「opencv 检测文本行 → 逐行裁剪 → `OcrEngine.recognize`」。
    两者都产出以「预处理后图像」为坐标空间的 TextLine，故后续解析无需坐标换算。

    Usage:
        recognizer = ReceiptRecognizer(PaddleOcrEngine(), [my_observer])
        receipt = recognizer.recognize(image_bytes)
        payload = receipt.to_dict()
    """

    def __init__(self, engine: OcrEngine, observers: Sequence[OcrObserver] | None = None,
                 min_confidence: float = DEFAULT_MIN_CONFIDENCE) -> None:
        self._engine = engine
        self._observers: list[OcrObserver] = list(observers or ())
        self._min_confidence = min_confidence

    def _low_confidence(self, lines: Sequence[TextLine]) -> list[LowConfidenceLine]:
        """挑出置信度低于阈值的行。

        **只上报，不参与解析** —— 见 `Receipt.low_confidence` 的取舍说明。

        注意回退路径（`_recognize_by_boxes`）造出来的 `TextLine` 置信度是默认的 `1.0`：
        那条路径本来就没有置信度信息（`OcrEngine.recognize()` 只回纯文本），
        于是永远不会被列进这里。这是**刻意的** —— 把「不知道」当成「可疑」
        会让所有无置信度引擎的票据都挂满警告，反而没人看了。
        """
        return [
            LowConfidenceLine(line.text, line.confidence)
            for line in lines
            if line.confidence < self._min_confidence
        ]

    def register_observer(self, observer: OcrObserver) -> None:
        """注册识别生命周期观察者。"""
        if observer not in self._observers:
            self._observers.append(observer)

    def _emit(self, kind: str, message: str, data: dict | None = None) -> None:
        """向观察者派发生命周期事件。

        派发逻辑与 `OcrManager._dispatch_event` 一致；此处未复用是因为
        `manager.py` 不在本次授权改动范围内，且其派发方法为私有（`_notify_observers`）。
        """
        event = OcrEvent(event_type=kind, message=message, data=data or {})
        index = _EVENT_KINDS.index(kind)
        for observer in self._observers:
            handler = getattr(observer, _EVENT_METHODS[index], None)
            if handler is not None:
                handler(event)

    def _recognize_by_boxes(self, result: PreprocessResult) -> list[TextLine]:
        """回退路径：opencv 检测文本行 → 逐行裁剪 → 用 recognize() 识别。"""
        lines: list[TextLine] = []
        for bbox in detect_text_lines(result.binary):
            text = _single_line(self._engine.recognize(_encode(_crop(result.image, bbox))))
            if text:
                lines.append(TextLine(text, bbox))
        return lines

    def _extract_lines(self, result: PreprocessResult) -> list[TextLine]:
        """取文本行：引擎支持 bbox 就直接用，否则走逐行裁剪回退路径。"""
        if isinstance(self._engine, LineOcrEngine):
            return self._engine.recognize_lines(_encode(result.image))
        return self._recognize_by_boxes(result)

    def recognize(self, image: bytes) -> Receipt:
        """识别一张票据图片，返回通用票据结构。

        Raises:
            ValueError: 图片无法解码。
            RuntimeError: OCR 引擎不可用（如未安装 paddleocr）。
        """
        self._emit("start", "receipt recognition started")
        try:
            result = preprocess(image)
            self._emit("progress", "image preprocessed", {"meta": result.meta})
            lines = self._extract_lines(result)
            self._emit("progress", "text lines recognized", {"line_count": len(lines)})
            receipt = parse_receipt(lines)
            receipt.extra.update(result.meta)
            receipt.low_confidence = self._low_confidence(lines)
            self._emit("complete", "receipt recognition completed", {
                "doc_type": receipt.doc_type,
                "low_confidence_count": len(receipt.low_confidence),
            })
            return receipt
        except Exception as exc:
            self._emit("error", f"receipt recognition failed: {exc}", {"error": str(exc)})
            raise


def create_recognizer(engine: OcrEngine | None = None,
                      observers: Sequence[OcrObserver] | None = None,
                      settings: OcrSettings | None = None) -> ReceiptRecognizer:
    """便捷构造识别器；不传引擎时按环境变量自动选择。

    - `OCR_ENGINE=http` 且配了 `OCR_API_BASE` → `HttpOcrEngine`（调用远程 serving）
    - 否则 → `PaddleOcrEngine`（本地自部署模型）

    两个引擎都是**惰性初始化**：未装 paddleocr / 远程服务未起时本函数仍正常返回，
    只有真正调用 `recognize()` 才报错。配置见 `ocr/settings.py`。
    """
    conf = settings or load_settings()
    if engine is None:
        engine = HttpOcrEngine(conf) if conf.use_http() else PaddleOcrEngine(conf.lang)
    return ReceiptRecognizer(engine, observers, min_confidence=conf.min_confidence)
