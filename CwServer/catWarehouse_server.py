from contextlib import asynccontextmanager

import logging
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from api.router import router
from core.config import settings
from core.database import engine
from core.logging import setup_logging
from models import Base

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import json
    from pathlib import Path

    from datetime import datetime

    setup_logging()

    pkg = json.loads(
        (Path(__file__).parent.parent / "Cw_WebUi" / "package.json").read_text()
    )
    import api.system.settings_router as sr
    sr.APP_VERSION = pkg.get("version", "0.1.0")
    sr.set_start_time(datetime.now().isoformat())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_migrate_tables)
    yield


def _migrate_tables(conn):
    from sqlalchemy import text
    inspector_columns = conn.execute(
        text("PRAGMA table_info(specific_items)")
    ).fetchall()
    col_names = {row[1] for row in inspector_columns}
    if "expire_date" not in col_names:
        conn.execute(text("ALTER TABLE specific_items ADD COLUMN expire_date DATETIME"))
        logger.info("Migrated: added expire_date to specific_items")
    if "is_expired" not in col_names:
        conn.execute(text("ALTER TABLE specific_items ADD COLUMN is_expired INTEGER DEFAULT 0"))
        logger.info("Migrated: added is_expired to specific_items")
    if "currency" not in col_names:
        conn.execute(text("ALTER TABLE specific_items ADD COLUMN currency VARCHAR DEFAULT 'CNY'"))
        logger.info("Migrated: added currency to specific_items")
    if "image_path" not in col_names:
        conn.execute(text("ALTER TABLE specific_items ADD COLUMN image_path VARCHAR"))
        logger.info("Migrated: added image_path to specific_items")

    inspector_columns = conn.execute(
        text("PRAGMA table_info(categories)")
    ).fetchall()
    col_names = {row[1] for row in inspector_columns}
    if "icon_color" not in col_names:
        conn.execute(text("ALTER TABLE categories ADD COLUMN icon_color VARCHAR DEFAULT '#f59e0b'"))
        logger.info("Migrated: added icon_color to categories")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method,
        request.url.path,
        response.status_code,
        elapsed,
    )
    return response


app.include_router(router)


@app.get("/")
async def root():
    return {"message": "CatWareHouse API"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=11222)
