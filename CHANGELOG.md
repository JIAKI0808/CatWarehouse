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

### `4364372` — 新增更新日志（本文件）

- 新建根 `CHANGELOG.md`，声明追加式、永不删除旧条目
- 说明：根 `plan.md` 被 `.gitignore:260` 的 `plan.md` 规则命中（匹配任意层级），
  且 `git ls-files` 显示历轮 plan.md 从未入库 —— 属仓库既有约定，故不 force-add

### `4caca0d` — 修复 P0 引入的真实 bug：上传目录漂移

> ⚠️ **这一条是「纯 rename」推不出来的**：18 个文件内容一字未改，
> 但 `__file__` 变了。前一版提交里「0 insertions / 0 deletions」的说法对**内容**成立，
> 对**行为**不成立。

**修复**
- `CwServer/api/intake/upload_router.py`：`Path(__file__).parent.parent / "uploads"`
  → `Path(__file__).parents[2] / "uploads"`

**根因**：P0 把 `upload_router.py` 从 `api/` 移到 `api/intake/`，`parent.parent`
只上溯到 `api/`，上传目录从 `CwServer/uploads` 静默漂到 `CwServer/api/uploads`。

**为什么四道闸门都没抓到**：81 条行为探针**不含 `/api/upload`** —— 覆盖盲区。

**新增工具**（仓库外）
- `upload_probe.py`：起真实服务器、真实 multipart 上传、记录落盘位置
  （相对 server_dir，故可跨 worktree 比对），用完自动清理产物

**对抗性验证**（证明探针真的会咬）
| 代码状态 | 落盘位置 |
| --- | --- |
| `5afdd56`（重构前） | `uploads/probe.png` |
| `12bd137`（有 bug） | **`api/uploads/probe.png`** ← 探针精确抓到 |
| 当前（已修） | `uploads/probe.png` |

### `ae18e86` — P1 国际化 A：新增 `api/i18n` 分区（既有接口零改动）

**新增**
- `CwServer/locales/`：`__init__.py`（边界说明）、`catalog.py`、`zh-CN.json`、`en-US.json`
- `CwServer/api/i18n/`：`__init__.py`、`router.py`、`i18n_router.py`
- 4 个新端点：
  - `GET /api/i18n/locales` — 支持的语言 + 默认语言
  - `GET /api/i18n/messages/{locale}` — 语言包下发；未知 locale → **404**（不回退）
  - `GET /api/i18n/preference` — 语言偏好
  - `PUT /api/i18n/preference` — 写偏好；未知 locale → **422**

**修改（4 处，全部增量）**
- `models/settings.py`：+ `locale` 列（**刻意不加进 `SettingsResponse`**，故 `/api/settings` 响应不变）
- `catWarehouse_server.py`：`_migrate_tables` 补 `settings.locale` 的 `ALTER TABLE` 迁移
- `api/router.py`：+2 行（import + include）
- `api/__init__.py`：分区表补 `api.i18n` 一行

**边界决策**（已写进代码 docstring）
语言包**只覆盖后端自己产生的文案**（`Category not found` 这类）的「原文 → 本地化」对照表；
**界面文案由各前端自己的语言包负责** —— 界面必须在后端尚未应答时就能渲染
（离线 / 连不上服务端是既有正常状态），做成远程依赖等于给首屏加一个失败点。

**验证（7 道闸门全绿）**
| 闸门 | 结果 |
| --- | --- |
| `verify_contract_additive.py` | 80 → 84 路由，**只多 4 条**，既有面逐字冻结 |
| `http_probe.py`（81 条真实请求） | 逐字段一致 |
| `upload_probe.py` | `uploads/`，与重构前一致 |
| `pyright` | 66 → 66，逐文件计数一致 |
| `py_spec_check.py` | 54 文件 / 3 违规（全部既有） |
| `smoke_i18n.py` | **23/23** |
| `smoke_i18n_migrate.py` | **7/7** |

`smoke_i18n.py` 覆盖：真服务器 + 真 sqlite；标签归一（`zh` / `ZH-cn` / `zh_CN` / `zh-Hans`）；
未知 locale 404 不回退；422 拒写且不污染已有值；**重启后偏好持久化**；
以及关键否定断言 —— **`/api/settings` 没有长出新字段**（只有 `ai_config` + `plugin_config`）。

`smoke_i18n_migrate.py` 覆盖：在**真实库的副本**上验证 `ALTER TABLE` 迁移路径
（新建库走的是 `create_all`，覆盖不到老库）；真 `catwarehouse.db` 的
**mtime + sha256 前后一致**，全程未被触碰。

**工具**（仓库外）
- `verify_contract_additive.py`：只允许**新增**的契约校验（既有路由不许删/改名、
  OpenAPI 既有子树不许变、列表只许增长）。**带 `--selftest` 6/6** ——
  能拒删除、拒改名、拒 schema 变异、拒列表重排，且放过良性新增。
- `smoke_i18n.py` / `smoke_i18n_migrate.py` / `upload_probe.py`
