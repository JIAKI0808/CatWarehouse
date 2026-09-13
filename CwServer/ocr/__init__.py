"""OCR recognition module for CatWareHouse.

Provides an extensible OCR framework using Builder and Observer patterns.
"""

from ocr.base import OcrEngine, OcrObserver
from ocr.builder import OcrBuilder
from ocr.config import OcrConfig
from ocr.events import OcrEvent
from ocr.manager import OcrManager

__all__ = [
    "OcrBuilder",
    "OcrConfig",
    "OcrEngine",
    "OcrEvent",
    "OcrManager",
    "OcrObserver",
]
