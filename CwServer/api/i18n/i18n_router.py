"""国际化端点 —— 语言包下发 + 语言偏好读写。

## 为什么是「新增分区」而不是「改造既有接口」

合同第 1 条要求「以增加接口的方式添加功能」「不允许影响或耦合其它接口」。
按 `Accept-Language` 改写既有接口的 `detail` 文案**会改变既有响应**，
与历轮建立的「路由表 + `/openapi.json` 逐字不变、响应逐字段一致」基线直接冲突。
所以本分区**只新增**：既有 80 条路由一个字都不碰，前端改为自己来取语言包。

## 边界（与 `locales/__init__.py` 的说明互为补充）

- 本分区下发的是**后端自己产生的文案**（`Category not found` 这类）的对照表。
- **界面文案不在这里** —— 那是各前端语言包的事（离线也要能渲染，理由见 `locales/__init__.py`）。

## 四个端点

| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/api/i18n/locales` | 支持哪些语言 + 默认语言 |
| GET | `/api/i18n/messages/{locale}` | 取一门语言的语言包；未知 locale → **404** |
| GET | `/api/i18n/preference` | 当前语言偏好 |
| PUT | `/api/i18n/preference` | 写语言偏好；未知 locale → **422** |

## 两个状态码为什么不一样（不是笔误）

`/messages/{locale}` 的 locale 在**路径**里，它**就是**被请求的资源 —— 资源不存在是 404。
`PUT /preference` 的 locale 在**请求体**里，是**参数**不合法 —— 那是 422。
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from locales import catalog
from models.settings import Settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/i18n", tags=["i18n"])


class LocaleListResponse(BaseModel):
    default: str
    locales: list[str]


class LocalePreference(BaseModel):
    locale: str


class MessagePackResponse(BaseModel):
    locale: str
    meta: dict
    backend_messages: dict


async def _settings_row(db: AsyncSession) -> Settings:
    """取（或建）`id=1` 的 Settings 行。

    与 `api/system/settings_router._get_or_create_settings` 是**刻意重复**的 8 行：
    `api/__init__.py` 的规则 3 写明「分区之间不互相 import」，
    为这 8 行让 i18n 分区去依赖 system 分区，等于用分区独立性换省事。
    与 `ocr/` 和 `voice/` 各自保留一份 `UpstreamRejectedError` 是同一个取舍。
    """
    result = await db.execute(select(Settings).where(Settings.id == 1))
    row = result.scalar_one_or_none()
    if row is None:
        row = Settings(id=1, ai_config={}, plugin_config={})
        db.add(row)
        await db.commit()
        await db.refresh(row)
    return row


def _stored_locale(row: Settings) -> str | None:
    """行上存的语言标签；没存过 / 列不存在时返回 None。

    用 `getattr` 而不是 `row.locale`，两个原因：
    ① SQLAlchemy 老式 `Column` 声明让 pyright 把 `row.locale` 推断为 `Column[str]`，
       直接传会多出 `reportArgumentType` —— 同一种类型噪声本仓库既有 7 处
       （见 pyright 基线），**不**为它把 `models/` 改成 `Mapped[]` 风格（那是另一件事）。
    ② 万一列没迁移成功（老库），`getattr` 取到的是**列描述符**而不是字符串，
       这里会安全地当成「没存过」，而不是把描述符喂给 `normalize`。
    """
    value = getattr(row, "locale", None)
    return value if isinstance(value, str) else None


def _effective_locale(row: Settings) -> str:
    """行上存的语言；若它指向的语言包已被删除，退回默认而不是 500。"""
    return catalog.normalize(_stored_locale(row)) or catalog.default_locale()


@router.get("/locales", response_model=LocaleListResponse)
async def list_locales():
    """支持的语言清单。前端据此渲染语言选择器，不必写死。"""
    return LocaleListResponse(
        default=catalog.default_locale(),
        locales=catalog.available_locales(),
    )


@router.get("/messages/{locale}", response_model=MessagePackResponse)
async def get_messages(locale: str):
    """下发一门语言的语言包。

    未知 locale **不回退**到默认语言 —— 回退会让调用方以为拿到了译文，
    实际拿到的是另一种语言（理由详见 `locales/catalog.py`）。
    """
    resolved = catalog.normalize(locale)
    if resolved is None:
        raise HTTPException(status_code=404, detail=f"Unknown locale: {locale}")
    try:
        messages = catalog.load_messages(resolved)
    except catalog.UnknownLocaleError as exc:
        logger.error("Locale pack unreadable: %s", exc)
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return MessagePackResponse(
        locale=resolved,
        meta=messages.get("_meta", {}),
        backend_messages=messages.get("backend_messages", {}),
    )


@router.get("/preference", response_model=LocalePreference)
async def get_preference(db: AsyncSession = Depends(get_db)):
    """当前语言偏好。首次调用会自动建行，返回默认语言。"""
    row = await _settings_row(db)
    return LocalePreference(locale=_effective_locale(row))


@router.put("/preference", response_model=LocalePreference)
async def update_preference(data: LocalePreference, db: AsyncSession = Depends(get_db)):
    """写入语言偏好。未知 locale → 422（理由见模块 docstring）。"""
    resolved = catalog.normalize(data.locale)
    if resolved is None:
        raise HTTPException(status_code=422, detail=f"Unknown locale: {data.locale}")
    row = await _settings_row(db)
    # setattr 而非 `row.locale = ...`：理由同 `_stored_locale`（老式 Column 的类型噪声）
    setattr(row, "locale", resolved)
    await db.commit()
    await db.refresh(row)
    logger.info("Locale preference updated to %s", resolved)
    return LocalePreference(locale=resolved)
