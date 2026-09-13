from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ocr.events import OcrEvent


class OcrEngine(ABC):
    """Abstract OCR engine interface.

    Concrete implementations should wrap a specific OCR library
    (Tesseract, PaddleOCR, EasyOCR, etc.) and expose a uniform
    recognition API.
    """

    @abstractmethod
    def recognize(self, image: bytes) -> str:
        """Recognize text from image bytes.

        Args:
            image: Raw image data (PNG, JPEG, etc.).

        Returns:
            Recognized text string.
        """
        ...

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Return list of supported image MIME types.

        Returns:
            List of MIME types, e.g. ["image/png", "image/jpeg"].
        """
        ...


class OcrObserver(ABC):
    """Observer that receives OCR lifecycle events.

    Implement any subset of callbacks you need; default implementations
    are provided as no-ops so subclasses only override what they use.
    """

    def on_recognition_start(self, event: "OcrEvent") -> None:
        """Called before recognition begins."""
        ...

    def on_recognition_progress(self, event: "OcrEvent") -> None:
        """Called during recognition with progress updates."""
        ...

    def on_recognition_complete(self, event: "OcrEvent") -> None:
        """Called after successful recognition."""
        ...

    def on_recognition_error(self, event: "OcrEvent") -> None:
        """Called when recognition fails."""
        ...
