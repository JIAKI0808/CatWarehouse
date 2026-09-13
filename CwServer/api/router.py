"""API 顶层聚合 —— 把 7 个功能分区挂到 `/api` 前缀下。

分区规则见 `api/__init__.py`。本文件**只做聚合**，不定义任何端点、不做任何加工：
各分区聚合器没有 prefix、没有 tags，只把子路由原样 include 进来，
所以 `/openapi.json` 与分区重构前**逐字一致**（由 `verify_contract.py` 把关）。

分区的 include 顺序（库存 → 分析 → 财务 → 通知 → 录入 → 系统 → 售价 → 国际化）与重构前
各资源的注册顺序不同。这是**安全的**，因为每个分区占用的路径前缀互不相交
（`/api/categories`、`/api/analytics/*`、`/api/ledger`…），不存在「一条路由抢先匹配
另一分区的路径」的可能。且 `catWarehouse_server.py` 里 `app` 与 `router` 都是在
`lifespan` 之前静态构造的，没有任何运行时顺序依赖。
"""

import logging

from fastapi import APIRouter

from api.inventory.router import router as inventory_router
from api.analytics.router import router as analytics_router
from api.finance.router import router as finance_router
from api.notify.router import router as notify_router
from api.intake.router import router as intake_router
from api.system.router import router as system_router
from api.pricing.router import router as pricing_router
from api.i18n.router import router as i18n_router

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["inventory"])

router.include_router(inventory_router)
router.include_router(analytics_router)
router.include_router(finance_router)
router.include_router(notify_router)
router.include_router(intake_router)
router.include_router(system_router)
router.include_router(pricing_router)
router.include_router(i18n_router)
