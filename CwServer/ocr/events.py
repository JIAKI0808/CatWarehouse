from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class OcrEvent:
    """Event emitted during OCR recognition lifecycle.

    Attributes:
        event_type: One of "start", "progress", "complete", "error".
        message: Human-readable description of the event.
        data: Optional dict with event-specific payload.
    """

    event_type: str
    message: str
    data: dict | None = field(default_factory=dict)
