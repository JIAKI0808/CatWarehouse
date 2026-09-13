from __future__ import annotations

from typing import Any

from ocr.base import OcrEngine
from ocr.preprocess import load_image
from ocr.response import lines_from_page
from ocr.settings import DEFAULT_LANG
from ocr.types import TextLine

SUPPORTED_FORMATS = ["image/png", "image/jpeg", "image/jpg", "image/bmp", "image/webp"]
_INSTALL_HINT = (
    "PaddleOCR 未安装，无法识别。请先安装："
    "pip install -r CwServer/ocr/requirements-ocr.txt（需要 Python < 3.13）"
)


class PaddleOcrEngine(OcrEngine):
    """本地自部署模型：直接调用 `paddleocr` 包在本机推理。

    与 `HttpOcrEngine`（调远程 serving）互为替代，接口完全一致，
    因此 `create_recognizer()` 与整条流水线都不用改。

    `paddleocr` 采用**惰性导入**：未安装时本模块仍可正常 import 与实例化，
    只有真正调用识别方法时才报错并给出安装提示。

    除满足 `OcrEngine` 抽象外，还实现 `LineOcrEngine` 协议的 `recognize_lines()`，
    提供 bbox 与置信度，供 pipeline 做表格列对齐。
    """

    def __init__(self, lang: str = DEFAULT_LANG) -> None:
        self._lang = lang or DEFAULT_LANG
        self._model: Any | None = None

    def _ensure_model(self) -> Any:
        """惰性创建 PaddleOCR 实例（首次调用时才 import paddleocr）。"""
        if self._model is not None:
            return self._model
        try:
            from paddleocr import PaddleOCR
        except ImportError as exc:
            raise RuntimeError(_INSTALL_HINT) from exc
        # 只传 lang：不同大版本的构造参数差异较大，最小化参数面以降低版本耦合。
        self._model = PaddleOCR(lang=self._lang)
        return self._model

    def recognize_lines(self, image: bytes) -> list[TextLine]:
        """识别并返回带 bbox / 置信度的文本行。

        Raises:
            RuntimeError: 未安装 paddleocr。
            ValueError: 图片字节无法解码。
        """
        pages = self._ensure_model().ocr(load_image(image), cls=True)
        return [line for page in (pages or []) for line in lines_from_page(page)]

    def recognize(self, image: bytes) -> str:
        """识别整图文本，按行以换行符拼接。"""
        return "\n".join(line.text for line in self.recognize_lines(image))

    def get_supported_formats(self) -> list[str]:
        return list(SUPPORTED_FORMATS)
