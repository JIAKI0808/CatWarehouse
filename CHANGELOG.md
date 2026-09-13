# 更新日志 (CHANGELOG)

> **追加式，永不删除旧条目**（用户合同「注意 2」：需记录哪次提交新增了哪些内容，且不容许删除内容）。
> 每条记录「提交号 + 日期 + 新增了什么」，倒序不必——**按时间正序**，越靠下越新。
>
> 更早的历史（2026-06 ~ 2026-09 的任务 A–E、CwMobile、CwClient）见 git log 与
> `CwServer/plan.md` / `CwClient/plan.md`，本文件从**优化链条任务**开始记录。

---

## 2026-09-14

### `12bd137` — CwServer 后端接口分区（优化链条 · 前置 + 契约第 9 条）

**新增**
- `CwServer/api/inventory/`、`api/pricing/`、`api/finance/`、`api/analytics/`、
  `api/intake/`、`api/notify/`、`api/system/` 共 **7 个功能分区文件夹**
- 每个分区新增 `__init__.py`（只写说明，不 import 子模块）与 `router.py`（聚合门面，无 prefix / 无 tags）
- `CwServer/api/__init__.py` 写入**分区规则**（分区表 + 4 条约定）

**移动（git mv，逐字节未改，共 18 个文件 0 insertions / 0 deletions）**
- `api/category_router.py` → `api/inventory/category_router.py`
- `api/sub_category_router.py` → `api/inventory/sub_category_router.py`
- `api/item_router.py` → `api/inventory/item_router.py`
- `api/tag_router.py` → `api/inventory/tag_router.py`
- `api/pricing_router.py` → `api/pricing/pricing_router.py`
- `api/pricing_category_router.py` → `api/pricing/pricing_category_router.py`
- `api/ledger_router.py` → `api/finance/ledger_router.py`
- `api/budget_router.py` → `api/finance/budget_router.py`
- `api/recurring_router.py` → `api/finance/recurring_router.py`
- `api/analytics_router.py` → `api/analytics/analytics_router.py`
- `api/upload_router.py` → `api/intake/upload_router.py`
- `api/ocr_router.py` → `api/intake/ocr_router.py`
- `api/voice_router.py` → `api/intake/voice_router.py`
- `api/notification_router.py` → `api/notify/notification_router.py`
- `api/alert_router.py` → `api/notify/alert_router.py`
- `api/settings_router.py` → `api/system/settings_router.py`
- `api/backup_router.py` → `api/system/backup_router.py`
- `api/currency_router.py` → `api/system/currency_router.py`

**修改（仅 2 个文件）**
- `CwServer/api/router.py`：改为 import 7 个分区聚合器（原 18 条 import 收敛为 7 条）
- `CwServer/catWarehouse_server.py`：**1 行**，`import api.settings_router as sr`
  → `import api.system.settings_router as sr`

**接口影响：零。** 验证（全绿）
- `verify_contract.py` → `CONTRACT HELD`：路由表 80 行 + `/openapi.json`（50 paths / 76 ops /
  98329 字节）与重构前**逐字一致**
- `http_probe.py` 81 条真实 HTTP 请求 → 响应**逐字段一致**（仅 ISO 时间戳归一）
- `pyright` 66 → 66 error，逐文件计数与规则分布完全一致
- `py_spec_check` 34 文件 / 3 违规 —— 与重构前**完全相同**，3 处均为既有债（见 `plan.md` §C3.2）

**工具（仓库外 `%TEMP%/cwrefactor/`，不进入版本库）**
- 新增 `py_spec_check.py`：Python 规格检查（函数 ≤50 行、行 ≤120 字符），
  **带 `--selftest`**（能抓出 60 行函数与 132 字符行，且放过干净文件）
