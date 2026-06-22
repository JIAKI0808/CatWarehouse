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
    import api.settings_router as sr
    sr.APP_VERSION = pkg.get("version", "0.1.0")
    sr.set_start_time(datetime.now().isoformat())

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


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
    return {"message": "CatWarehouse API"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=11222)
