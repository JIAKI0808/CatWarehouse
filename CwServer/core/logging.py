import logging
import sys
from datetime import datetime
from pathlib import Path

from core.config import settings

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


class DailyRotatingFileHandler(logging.Handler):
    """Log handler that rotates files daily as cw_YYYYMMDD.log."""

    def __init__(self, log_dir: Path, encoding: str = "utf-8") -> None:
        super().__init__()
        self._log_dir = log_dir
        self._encoding = encoding
        self._current_date: str = ""
        self._stream = None

    def emit(self, record: logging.LogRecord) -> None:
        try:
            today = datetime.now().strftime("%Y%m%d")
            if today != self._current_date:
                self._open_file(today)
            self._stream.write(self.format(record) + "\n")
            self._stream.flush()
        except Exception:
            self.handleError(record)

    def _open_file(self, date_str: str) -> None:
        if self._stream:
            self._stream.close()
        self._current_date = date_str
        filename = f"cw_{date_str}.log"
        self._stream = open(
            self._log_dir / filename, "a", encoding=self._encoding
        )

    def close(self) -> None:
        if self._stream:
            self._stream.close()
        super().close()


def setup_logging():
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    LOG_DIR.mkdir(exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(LOG_FORMAT))

    file_handler = DailyRotatingFileHandler(LOG_DIR)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root.addHandler(console)
    root.addHandler(file_handler)

    _configure_uvicorn_loggers(level)


def _configure_uvicorn_loggers(level: int):
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for name in uvicorn_loggers:
        logging.getLogger(name).setLevel(level)
