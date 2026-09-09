import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from core.config import settings

LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"


def setup_logging():
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    LOG_DIR.mkdir(exist_ok=True)

    root = logging.getLogger()
    root.setLevel(level)

    console = logging.StreamHandler(sys.stdout)
    console.setLevel(level)
    console.setFormatter(logging.Formatter(LOG_FORMAT))

    file_handler = RotatingFileHandler(
        LOG_DIR / "app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root.addHandler(console)
    root.addHandler(file_handler)

    _configure_uvicorn_loggers(level)


def _configure_uvicorn_loggers(level: int):
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]
    for name in uvicorn_loggers:
        logging.getLogger(name).setLevel(level)
