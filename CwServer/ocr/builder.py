from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ocr.config import OcrConfig
    from ocr.manager import OcrManager


class OcrBuilder:
    """Builder for constructing OcrManager instances with fluent API.

    Usage:
        manager = (
            OcrBuilder()
            .set_engine_name("tesseract")
            .set_language("chi_sim+eng")
            .set_confidence_threshold(0.7)
            .build()
        )
    """

    def __init__(self) -> None:
        self._engine_name: str = "default"
        self._language: str = "chi_sim+eng"
        self._confidence_threshold: float = 0.6
        self._max_retries: int = 3
        self._timeout: int = 30
        self._custom_settings: dict = {}

    def set_engine_name(self, name: str) -> OcrBuilder:
        """Set the OCR engine name."""
        self._engine_name = name
        return self

    def set_language(self, lang: str) -> OcrBuilder:
        """Set the recognition language(s)."""
        self._language = lang
        return self

    def set_confidence_threshold(self, threshold: float) -> OcrBuilder:
        """Set the minimum confidence threshold."""
        self._confidence_threshold = threshold
        return self

    def set_max_retries(self, retries: int) -> OcrBuilder:
        """Set the maximum retry attempts."""
        self._max_retries = retries
        return self

    def set_timeout(self, timeout: int) -> OcrBuilder:
        """Set the timeout in seconds."""
        self._timeout = timeout
        return self

    def set_custom_settings(self, settings: dict) -> OcrBuilder:
        """Set engine-specific custom settings."""
        self._custom_settings = settings.copy()
        return self

    def build(self) -> OcrManager:
        """Build and return an OcrManager with the configured settings."""
        from ocr.config import OcrConfig
        from ocr.manager import OcrManager

        config = OcrConfig(
            engine_name=self._engine_name,
            language=self._language,
            confidence_threshold=self._confidence_threshold,
            max_retries=self._max_retries,
            timeout=self._timeout,
            custom_settings=self._custom_settings,
        )
        return OcrManager(config)
