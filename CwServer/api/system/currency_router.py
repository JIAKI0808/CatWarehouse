"""货币 —— 货币清单（既有）+ **计价货币偏好**（2026-09-14「通用化」环新增）。

## 为什么加偏好端点

`GET /currencies` 与 `SpecificItem.currency` 列早就存在，两端前端也都定义了 `currencyApi`，
但**没有任何界面用过它们** —— 界面上到处写死 `¥`（图表轴名、价格前缀、卡片行）。
这是与任务 D 修掉的 `dataManager/` 同一个 signature：**造了零件却没接线**。
「通用化」的正确动作是**给它真实使用者**，而不是再抽一层。

## 默认值就是现状（风险压到零的手法）

偏好默认 `CNY` ⇒ 符号 `¥` ⇒ **界面逐字不变**。
与 `api/i18n` 默认 `zh-CN` 是同一个做法：先让「什么都不改」成为默认路径，
再让选择成为可选增量。

## 与 i18n 分区的三处一致约定

1. 偏好存 `settings` 表的独立列（`currency`），**不**进 `SettingsResponse`
   —— 否则会改掉 `/api/settings` 的响应；
2. 单行取用走 `models.settings.get_or_create()`（本环新抽出的共享实现）；
3. 未知取值 -> **422**（与 `PUT /api/i18n/preference` 同一口径：
   请求体里的参数不合法是 422，路径里请求的资源不存在才是 404）。
"""

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from models.settings import get_or_create

logger = logging.getLogger(__name__)
router = APIRouter()

CURRENCIES = [
    {"code": "CNY", "name": "人民币", "symbol": "¥"},
    {"code": "USD", "name": "美元", "symbol": "$"},
    {"code": "EUR", "name": "欧元", "symbol": "€"},
    {"code": "GBP", "name": "英镑", "symbol": "£"},
    {"code": "JPY", "name": "日元", "symbol": "¥"},
    {"code": "KRW", "name": "韩元", "symbol": "₩"},
    {"code": "HKD", "name": "港币", "symbol": "HK$"},
    {"code": "TWD", "name": "新台币", "symbol": "NT$"},
]

DEFAULT_CURRENCY = "CNY"

_BY_CODE = {item["code"]: item for item in CURRENCIES}


class CurrencyCode(BaseModel):
    """写入用的请求体 —— 只认代码，符号由服务端查表得到，不接受客户端自报。"""

    code: str


class CurrencyPreference(BaseModel):
    code: str
    symbol: str


async def _preference(db: AsyncSession) -> CurrencyPreference:
    """当前计价货币。

    存的值若不在清单里（例如列被手工改过），**退回默认而不是报错** ——
    读接口不该因为一个脏值就 500；写接口那边才是校验的地方。
    """
    row = await get_or_create(db)
    stored = getattr(row, "currency", None)
    code = stored if isinstance(stored, str) and stored in _BY_CODE else DEFAULT_CURRENCY
    return CurrencyPreference(code=code, symbol=_BY_CODE[code]["symbol"])


@router.get("/currencies")
async def list_currencies():
    return CURRENCIES


@router.get("/currencies/preference", response_model=CurrencyPreference)
async def get_currency_preference(db: AsyncSession = Depends(get_db)):
    """当前计价货币 + 它的符号。前端拿 `symbol` 去替换写死的 `¥`。"""
    return await _preference(db)


@router.put("/currencies/preference", response_model=CurrencyPreference)
async def update_currency_preference(
    data: CurrencyCode,
    db: AsyncSession = Depends(get_db),
):
    """写入计价货币。未知代码 -> 422（理由见模块 docstring 第 3 条）。"""
    if data.code not in _BY_CODE:
        raise HTTPException(status_code=422, detail=f"Unknown currency: {data.code}")
    row = await get_or_create(db)
    # setattr 而非 `row.currency = ...`：老式 Column 声明让 pyright 把属性推断成
    # `Column[str]`（同一种类型噪声本仓库既有 7 处），不为它改 models 的声明风格。
    setattr(row, "currency", data.code)
    await db.commit()
    await db.refresh(row)
    logger.info("Currency preference updated to %s", data.code)
    return await _preference(db)
