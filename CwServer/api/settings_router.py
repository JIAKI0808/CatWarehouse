from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.settings import Settings
from schemas.settings import (
    AIConfig,
    PluginConfig,
    SettingsResponse,
    SettingsUpdate,
    VersionResponse,
)

router = APIRouter(prefix="/settings", tags=["settings"])

APP_VERSION = "0.1.0"
APP_NAME = "CatWarehouse"
APP_DESCRIPTION = "科学的管理每一颗螺丝钉"
_start_time: str = ""


def set_start_time(t: str) -> None:
    global _start_time
    _start_time = t


async def _get_or_create_settings(db: AsyncSession) -> Settings:
    result = await db.execute(select(Settings).where(Settings.id == 1))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = Settings(id=1, ai_config={}, plugin_config={})
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    settings = await _get_or_create_settings(db)
    return SettingsResponse(
        ai_config=AIConfig(**(settings.ai_config or {})),
        plugin_config=PluginConfig(**(settings.plugin_config or {})),
    )


@router.put("", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdate,
    db: AsyncSession = Depends(get_db),
):
    settings = await _get_or_create_settings(db)
    if data.ai_config is not None:
        settings.ai_config = data.ai_config.model_dump()
    if data.plugin_config is not None:
        settings.plugin_config = data.plugin_config.model_dump()
    await db.commit()
    await db.refresh(settings)
    return SettingsResponse(
        ai_config=AIConfig(**(settings.ai_config or {})),
        plugin_config=PluginConfig(**(settings.plugin_config or {})),
    )


@router.get("/version", response_model=VersionResponse)
async def get_version():
    return VersionResponse(
        app_name=APP_NAME,
        version=APP_VERSION,
        description=APP_DESCRIPTION,
        start_time=_start_time,
    )
