from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OcrConfig:
    """Configuration for OCR recognition.

    Attributes:
        engine_name: Name of the OCR engine to use.
        language: Recognition language(s), e.g. "chi_sim+eng".
        confidence_threshold: Minimum confidence to accept result.
        max_retries: Maximum retry attempts on failure.
        timeout: Recognition timeout in seconds.
        custom_settings: Engine-specific settings dict.
    """

    engine_name: str = "default"
    language: str = "chi_sim+eng"
    confidence_threshold: float = 0.6
    max_retries: int = 3
    timeout: int = 30
    custom_settings: dict = field(default_factory=dict)
