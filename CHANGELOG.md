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

### `e8d2ff5` — P2a 国际化 B-1：Cw_WebUi 接入 vue-i18n 基础设施

**目标**：先立地基，**不动任何既有界面文案**，把界面回归风险压到零。

**新增**
- `Cw_WebUi/src/locales/zh-CN.ts` — 简体中文语言包（默认语言），导出 `MessageSchema`
- `Cw_WebUi/src/locales/en-US.ts` — 英文语言包，用 `MessageSchema` 约束
  ⇒ **漏翻一个键 = `vue-tsc` 编译错误**，而不是界面上显示出一串 raw key
- `Cw_WebUi/src/i18n.ts` — i18n 实例 + 语言偏好读写 + `translateBackendMessage()`

**修改**
- `Cw_WebUi/src/main.ts` — +2 行（import + `app.use(i18n)`）
- `Cw_WebUi/src/App.vue` — 外壳接入：`navItems` 由 `const` 改 `computed`；
  侧栏「设置」tooltip 改用 `t('app.nav.settings')`；
  `NConfigProvider` 接上 `:locale` / `:date-locale`
- `Cw_WebUi/package.json` — + `vue-i18n ^11.4.10`（含 lock）

**三条设计决策**（写进 `src/i18n.ts` docstring）
1. 语言偏好以 **localStorage 为准**，后端 `/api/i18n/preference` 用于多设备一致（P2b 接）。
   首屏渲染不能等后端 —— 服务端不可达是本应用的正常状态。
2. 默认语言写死 **`zh-CN`，不跟随 `navigator.language`**。国际化之前界面硬编码中文，
   跟随浏览器语言会让老用户升级后突然看到英文 —— 那是行为变化，不是改进。
3. 语言包分两区：`app.*` 是前端自己的界面文案；`backend.*` 是后端 `detail` 原文的对照表
   （与 `CwServer/locales/*.json` 内容一致），用 `translateBackendMessage()` 查询，
   查不到**原样显示原文**，绝不返回空串。

**一个踩到的坑**（已记录在 `src/i18n.ts`）
`createI18n` 的泛型顺序是 `<Schema, Locales, Legacy>`，第三个**必须显式传 `false`**。
不传时默认 `legacy: true`，`global.locale` 会是普通字符串而不是 `ref` ——
切语言**不触发重渲染**，且类型上拿不到 `.value`。这是 `vue-tsc` 直接报出来的。

**验证（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18 error，逐文件分布与基线**完全一致**（新文件零错误） |
| 前端行为探针 | **PROBE IDENTICAL**（78 api 调用 / 13 store / 58 动作 / 204 文案） |
| `vite build` | 退出码 0 |
| `spec_check.py` | 4 文件 / 0 违规 |
| **真实浏览器端到端** | 见下 |

**浏览器端到端**（`vite dev` + 真实后端 + chrome-devtools，非 mock）
| 语言 | 侧栏 tooltip | naive-ui 空状态 | 布局 |
| --- | --- | --- | --- |
| `zh-CN`（默认，无 localStorage） | **设置** | **无数据** | 正常 |
| `en-US`（写 localStorage 后重载） | **Settings** | **No Data** | 正常 |

两侧均无元素重叠/错位。业务文案在 en-US 下**仍是中文** —— 这是 P2a 的**预期状态**
（本阶段刻意不迁移业务文案），P2c 分批迁移。

**⚠️ 副作用（如实记录）**
做浏览器验证时以**默认 `DATABASE_URL`** 起了真实服务器，`lifespan` 里的
`create_all` + `_migrate_tables` 因此在**真实 `catwarehouse.db`** 上执行了一次迁移：
`settings` 表新增 `locale` 列（默认 `zh-CN`）。**数据完好** ——
categories 8 / sub_categories 6 / specific_items 2 / settings 1 行，无丢失。

该迁移此前已在**库副本**上演练过（`smoke_i18n_migrate.py` 7/7），实际执行结果与演练一致。
但这与本计划「不动 `catwarehouse.db`」的说法不符，**如实记录，不掩饰**。
后续涉及真实库的验证会继续用临时库，只有确实需要端到端时才动真库并在此登记。
