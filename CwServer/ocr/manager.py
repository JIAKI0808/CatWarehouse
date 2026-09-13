from __future__ import annotations

from typing import TYPE_CHECKING

from ocr.base import OcrObserver
from ocr.events import OcrEvent

if TYPE_CHECKING:
    from ocr.config import OcrConfig
    from ocr.base import OcrEngine


class OcrManager:
    """Central OCR manager that coordinates recognition and observer notifications.

    Uses the Observer pattern to notify registered observers about
    recognition lifecycle events.

    Usage:
        manager = OcrManager(config)
        manager.register_observer(my_observer)
        result = manager.recognize(image_bytes)
    """

    def __init__(self, config: OcrConfig) -> None:
        self._config = config
        self._engine: OcrEngine | None = None
        self._observers: list[OcrObserver] = []

    def get_config(self) -> OcrConfig:
        """Return the current configuration."""
        return self._config

    def set_engine(self, engine: OcrEngine) -> None:
        """Set the OCR engine to use for recognition."""
        self._engine = engine

    def register_observer(self, observer: OcrObserver) -> None:
        """Register an observer for recognition events."""
        if observer not in self._observers:
            self._observers.append(observer)

    def unregister_observer(self, observer: OcrObserver) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(self, event: OcrEvent) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            self._dispatch_event(observer, event)

    def _dispatch_event(self, observer: OcrObserver, event: OcrEvent) -> None:
        """Dispatch a single event to the appropriate observer method."""
        handlers = {
            "start": observer.on_recognition_start,
            "progress": observer.on_recognition_progress,
            "complete": observer.on_recognition_complete,
            "error": observer.on_recognition_error,
        }
        handler = handlers.get(event.event_type)
        if handler:
            handler(event)

    def recognize(self, image: bytes) -> str:
        """Recognize text from image bytes using the configured engine.

        Notifies observers at each lifecycle stage:
        start -> progress -> complete | error

        Raises:
            RuntimeError: If no engine has been set.
        """
        if self._engine is None:
            raise RuntimeError("No OCR engine configured. Call set_engine() first.")

        self._notify_observers(OcrEvent(
            event_type="start",
            message="Recognition started",
        ))

        try:
            self._notify_observers(OcrEvent(
                event_type="progress",
                message="Processing image",
            ))
            result = self._engine.recognize(image)
            self._notify_observers(OcrEvent(
                event_type="complete",
                message="Recognition completed",
                data={"result": result},
            ))
            return result
        except Exception as exc:
            self._notify_observers(OcrEvent(
                event_type="error",
                message=f"Recognition failed: {exc}",
                data={"error": str(exc)},
            ))
            raise
