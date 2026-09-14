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

### `03e324d` — P2b 国际化 B-2：设置页语言切换 + 后端偏好同步

**界面改动刻意收紧在一处**：新增一个**默认折叠**的 `NCollapse` 小节，
插在「插件功能」与「版本信息」之间，**既有区块一行未动**。

**新增接口适配**（合同第 2 条「完整适配后端接口」）
- `src/types/index.ts`：+ `LocaleListResponse` / `LocalePreference` / `MessagePackResponse`
- `src/services/api.ts`：+ `i18nApi` —— **4 个方法全部实现**
  （`getLocales` / `getMessages` / `getPreference` / `updatePreference`），
  接上 P1 的 `api/i18n` 分区

**界面**（`SettingsView.vue`）
- 新增 `NCollapse`「语言」小节：`NSelect` + 一行说明，`flex-wrap` 布局不会被挤压
- 选择器绑**独立 ref** 而非 `i18n.locale`：切换必须经 `handleLocaleChange` 才能同步后端

**`i18n.ts` 补充**
- `LOCALE_LABELS`：语言用**它自己那门语言里的名字**（简体中文 / English）。
  语言选择器是给看不懂当前界面语言的人用的，用界面语言写选项名恰恰帮不到他 ——
  所以这张表**不参与翻译**
- `hasStoredLocale()`：区分「用户显式选过」与「只是取了默认值」

**采纳规则（只有一条，免得「谁覆盖谁」说不清）**
| 情形 | 行为 |
| --- | --- |
| 本机**没显式选过** | 采纳后端 `/api/i18n/preference` 的值（换设备能带过语言） |
| 本机**选过** | 以本机为准，后端**不**覆盖 |
| 服务器不可达 | 读取静默跳过；切换仍**本机立即生效**，只提示一次「未能同步到服务器」 |

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，逐文件分布与基线**完全一致**（改动文件零错误） |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 6 文件 / 0 违规 |

**真实浏览器端到端**（`vite dev` + 真实后端 + chrome-devtools，**临时库**）
1. 折叠小节渲染正常，与相邻区块**无重叠、布局未位移**
2. 切换语言 → 界面立即更新：标题变 `Language`、说明变英文、
   naive-ui 输入框占位符由「请输入」变 **`Please Input`**
   （证明 naive-ui 语言包接线覆盖了**全部**组件，不只是空状态）
3. 同步成功：`GET /api/i18n/preference` 与 `sqlite settings.locale` **都**变为 `en-US`
4. 清空 localStorage 重载（模拟换设备）→ 采纳后端 `en-US` 并**写回本机**
5. 本机显式设为 `zh-CN` 重载 → 保持 `zh-CN`，后端 `en-US` **未**覆盖本机
6. 停掉后端再切换 → 本机立即生效，提示「**已在本机切换，但未能同步到服务器**」

**排查记录（值得记）**：中途所有请求一度全部 `net::ERR_FAILED`，
原因**不是本次代码** —— 后端 `CORS_ORIGINS` 只放行 `5173`/`5175`，
而上一个 Phase 遗留的 vite 进程仍占着 `5173`，新 dev server 回落到 `5174` 被 CORS 拦下。
清掉遗留进程后一切正常。**该隐患已记入计划的技术债清单**
（vite 回落端口 ⇒ 应用失去全部 API 访问），留待后续环处理。

**真实数据库本次未被触碰**：全程用临时库，`catwarehouse.db` 的 mtime 仍是 P2a 的 `01:23`。

### `75c3ac5` — P2c-1 国际化 B-3：库存区业务文案迁移

**只动库存区组件**，其余区域仍是硬编码中文（后续批次）。

**先建公共词汇表再逐文件替换**：全站反复出现的名词/按钮/提示
（名称 / 描述 / 价格 / 库存 / 编辑 / 删除 / 保存 / 取消 / 暂无数据 / 请输入…）
统一进 `app.common`。不这么做的话，同一个「保存」会在 10 个文件里各写一份，
**改一处漏九处**。

**迁移的 7 个组件**
| 文件 | 迁移内容 |
| --- | --- |
| `ViewToggle.vue` | 表格 / 卡片（`options` 由 `const` 改 `computed`） |
| `ItemTable.vue` | 8 个列标题 + 编辑/删除（`columns` 由 `const` 改 `computed`） |
| `ItemCard.vue` | 卡片字段标签 + 编辑/删除 + 空态 |
| `FloatingButton.vue` | 下拉三项 + 导出成功/失败提示 |
| `CategoryTree.vue` | 侧栏标题、暂无描述、暂无数据、增改标题、两个删除确认框 |
| `CategoryForm.vue` | 表单标签/占位符/按钮 + **48 个图标 tooltip** |
| `ItemForm.vue` | 表单标签/占位符/按钮 |

**两个值得说的做法**
1. **`CategoryForm` 的 48 个图标 `label` 字段直接删掉**，模板改用
   `t('app.icons.' + icon.name)`。把 48 条中文留在组件里，等于语言包之外又存一份，
   翻译时必漏；键取组件名也不会出现对不上的风险。
2. **删除确认框的插值走 vue-i18n 具名插值**（`{name}`），不再用模板字符串拼接 ——
   拼接会把语序**锁死在中文**，英文语序不同就得改代码。

**刻意未迁移（并记录理由，不是漏掉）**
- `FloatingButton` 的两条 `console.log`/`console.error`：**开发者可见，非用户界面文案**
- `ItemForm` / `CategoryForm` 的 `unit: '个'`：这是**表单默认值**，会随提交写进数据库，
  属于**数据**而非界面文案。跟着界面语言变会让「同一张表里单位中英混杂」；
  要改应另开一项「单位字典」的需求，**不在本 Phase 夹带**

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，9 个文件的错误计数**逐个不变** |
| 前端行为探针 | **PROBE IDENTICAL**（未碰 stores/services，204 条文案照旧） |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |

> 行号说明：`ItemCard` 50→52、`ViewToggle` 25→29，均为新增 import 导致的**平移**，
> 不是新增错误，已逐条核对。

**真实浏览器端到端**（`vite dev` + 真实后端 + chrome-devtools，
后端指向**真实库的副本**）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 与改动前**逐项一致**（分类 / 库存列表 / 8 个列头 / 表格·卡片 / 无数据） |
| `en-US` 列表 | Inventory / Category / Name·Price·Stock·Updated·Expires·Description·Recorded by·Actions / Table·Card / No Data |
| `en-US` 下拉 | Upload receipt / Export / Import |
| `en-US` 表单 | New category / Name / Description / Icon / Icon color / Cancel / Save |
| 48 个图标 tooltip | **全部译出**（Folder…Ribbon），实测 DOM `title` 属性计数 = **48** |
| **缺失键扫描** | 全 DOM 无 `app.*`/`common.*`/`inventory.*` 形式的原始键残留 |
| **控制台** | **零 warn / 零 error**（vue-i18n 缺键会打警告 —— 这是最灵敏的一条） |
| 布局 | 与改动前一致，无元素重叠 |

**真实数据库未被触碰**：全程用真实库的**副本**，`catwarehouse.db` mtime 仍是 `01:23`。

### `880f7da` — P2c-2 国际化 B-4：账本区文案迁移

**只动账本区两个文件**：`LedgerView.vue` + `LedgerForm.vue`。

**迁移内容**
- `LedgerForm.vue`：标题（新增/编辑账单）、6 个表单标签与占位符、类型下拉、按钮
- `LedgerView.vue`：页面标题、范围下拉（按天/周/月/年）、类型筛选（全部/收入/支出）、
  表格 7 列（含类型列的「收入/支出」渲染）、图表标题与 Y 轴名、图例两条系列名、
  搜索占位符、预算概览、新增按钮、删除确认框

**一个新问题：年月与星期不是可以逐字替换的文案**
「2026年 / 9月 / 日一二三四五六」是**语言相关的格式**，不是词条 ——
英文要变 `{year}` / `Jan` / `Su`，照搬「年」「月」会出洋相。处置：

1. 提到 `app.ledger.yearLabel`（`{year}年` / `{year}`）与 `months` / `weekdays` **数组**
2. 数组用 vue-i18n 的 **`tm()`** 取原始消息（`t()` 会把数组编译成别的东西）
3. **没走 `Intl.DateTimeFormat`**：它给的中文星期是「周日/周一」，与既有界面的「日/一」不符，
   会**改变 zh-CN 的观感**。保持 zh-CN 逐字不变优先。

**⚠️ 一条踩到但确认不是本 Phase 引入的警告**
账本页控制台有一条 ECharts `Can't get DOM width or height`，图表标题被裁、图例重叠。
用 `git stash` 退回 P2c-1 状态复现，**同样出现** ⇒ 是**既有缺陷**：
图表在 `v-show="!showIntro"` 的容器里初始化，开场动画期间容器尺寸为 0。

> 这条排查本身是「**先验证度量**」原则的一次应用：**看到警告不等于自己弄坏的**，
> 退回基线复现一次，成本很低，结论却很硬。已记入 `plan.md` §C3.2 第 12 项，
> 归属「交互优化」环，本 Phase 不修。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，9 个文件错误计数**逐个不变** |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留扫描 | 两个文件**均为 0 行** |

**真实浏览器端到端**（后端指向真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 账本 / 收支统计 / 按月 / 新增 / 全部 / 7 个列头 / 无数据；日历 `2026年`、`9月`、`日一二三四五六` —— 与改动前一致 |
| `en-US` | Ledger / Month / Add / All / Date·Type·Amount·Platform·Description·Recorded by·Actions / No Data；日历 `2026`、`Sep`、`Su Mo Tu We Th Fr Sa` |
| **整页零 CJK** | 脚本扫描 `/[一-鿿]/` 在 en-US 账本页返回 **false** —— 国际化完整性的一条硬证据 |
| 布局 | 与改动前一致，无元素重叠 |

**真实数据库未被触碰**：用真实库的**副本**，`catwarehouse.db` mtime 仍是 `01:23`。

### `de26578` — P2c-2b 国际化 B-5：分析区文案迁移

**只动分析区两个文件**：`AnalyticsCharts.vue` + `AnalyticsView.vue`。

**迁移内容**
- `AnalyticsView.vue`：页面标题
- `AnalyticsCharts.vue`：4 张概览卡、2 个选择器占位符、2 个空态描述、
  **8 个图表的标题 / 坐标轴名 / 系列名**

**一处刻意的 key 拆分：指标名与坐标轴名分成两段**
| 段 | 内容 | 用在哪 |
| --- | --- | --- |
| `analytics.metric.*` | 数量 / 价格 / 总价 / 单价 / 库存（**不带单位**） | 饼图扇区名、图例 |
| `analytics.axis.*` | `数量 ({unit})` / `价格 (¥)` …（**带单位**） | 坐标轴名 |

合成一个 key 会让饼图的扇区名变成「数量 (斤)」，很难看。
「月度收支对比」的收入/支出直接**复用** `app.ledger.typeIncome/typeExpense` —— 同一份文案不写两遍。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变**（`AnalyticsCharts` 仍是 1） |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留扫描 | 两个文件**均为 0 行** |

**真实浏览器端到端**（后端指向真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 数据分析 / 总库存数 / 总库存价值 / 总收入 / 总支出 / 选择大类 / 选择子类 / 请选择大类和子类查看趋势 |
| `en-US` | Analytics / Total items / Total stock value / Total income / Total expense / Select a category / Select a sub-category / Pick a category and sub-category to see trends |
| **图表实测**（选「日用品 → 纸巾」触发 **7 个 canvas**） | `Stock share by category` / `Quantity trend`（轴 `Quantity (包)`）/ `Price trend` / `Total price trend` / `Unit price trend` —— 标题与轴名全英文，**单位插值正确** |
| 剩余中文 | 只有**用户数据**：分类名「日用品/纸巾」、单位「包」—— 不是界面文案 |
| 控制台 | **零 warn / 零 error** |
| 布局 | 与改动前一致，无元素重叠 |

**顺带印证了 §C3.2 第 12 项的诊断**：本次**先经首页再点进**分析页（进场动画已结束），
ECharts 的 0 尺寸警告**没有出现**；而直接加载账本页（动画期间挂载）就会出现 ——
与「容器在动画期间 `display:none`」的结论一致。**同一现象两种路径下表现不同，
这条对照本身也是对诊断的一次独立验证。**

### `d339cba` — P2c-3a 国际化 B-6：售价区文案迁移

**只动售价区三个文件**：`PricingTable.vue` / `PricingForm.vue` / `PricingCategoryTree.vue`。

**迁移内容**
- `PricingTable.vue`：7 个列标题 + 编辑/删除、页面标题、搜索占位符、新增按钮、删除确认框
- `PricingForm.vue`：标题（新增/编辑售价）+ 7 个表单标签与占位符 + 按钮
- `PricingCategoryTree.vue`：侧栏标题、两处「暂无描述」、分类与子分类两个弹窗的标题/占位符/按钮

**一处 key 归属的调整（我自己之前放错了）**
「确认删除」原先叫 `app.inventory.confirmDeleteTitle`，但**账本页也要用同一句** ——
说明它并不属于库存。本次它出现**第三个使用者**（售价）时提升为
`app.common.confirmDeleteTitle`，并同步改了 `CategoryTree`（2 处）与 `LedgerView`（1 处）的引用。

> **提取的时机是「第三个使用者出现的那一刻」，不是第一个。**
> 一个使用者时留在原地最省事；两个时还可能是巧合；到第三个才确认它真的是公共词汇。

**一处刻意的「不复用」**
售价区的「新增分类 / 新增子分类 / 编辑分类 / 编辑子分类」与库存区中文**逐字相同**，
但仍各开 `app.pricing.*` 的 key —— 因为它们指的不是同一个领域对象
（`PricingCategory`/`PricingSubCategory` vs `Category`/`SubCategory`）。
**改售价页的措辞不该连带改掉库存页**。
判据依旧是「**是不是同一个东西**」，而不是「中文是不是一样」。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变**（`PricingTable` 仍是 1） |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留扫描 | 三个文件**均为 0 行** |

**真实浏览器端到端**（后端指向真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 售价分类 / 售价管理 / 搜索商品名 / 新增 / 商品名·成本·建议售价·折扣系数·描述·备注·记录日期·操作 / 无数据 |
| `en-US` | Pricing categories / Pricing / Search product name / Add / Product·Cost·Suggested price·Discount factor·Description·Notes·Recorded on·Actions / No Data |
| `en-US` 售价表单弹窗 | New pricing record / Product / Enter a product name / Cost / Suggested price / Discount factor / Description / Enter a description / Notes / Enter notes / Recorded on / Cancel |
| `en-US` 分类弹窗 | New category / Category name / Cancel / Save |
| **整页零 CJK** | 脚本断言通过（三处界面） |
| 控制台 | 零 warn / 零 error |
| 布局 | 与改动前一致，无元素重叠 |

### `689f92e` — P2c-3b 国际化 B-7：录入区与顶部栏文案迁移

**只动三个文件**：`UploadModal.vue` / `ImportModal.vue` / `MenuBar.vue`。

**迁移内容**
- `UploadModal.vue`：弹窗标题、拖拽区提示、取消/上传按钮
- `ImportModal.vue`：弹窗标题、拖拽提示、「发现以下冲突项…」、冲突表三个表头
  （跳过/类型/名称）、类型单元格（大类/子分类）、导入完成标题与结果描述、
  关闭/确认导入、两条 `alert` 兜底文案
- `MenuBar.vue`：库存预警、低库存、系统通知、已读、暂无通知

**两个复用决定（同一条判据：是不是同一个东西）**
- `UploadModal` 的标题「上传单据」**复用** `app.inventory.uploadReceipt` ——
  菜单里的「上传单据」打开的就是这个弹窗，是同一个东西，不是巧合同名
- 「取消」「关闭」进 `app.common.close`（新加）

导入结果描述改用 vue-i18n **具名插值**（`{categories}/{subCategories}/{items}`），
不再用模板字符串拼接 —— 中文「新增大类 N 个，子分类 M 个，物品 K 个」的语序与英文不同，
拼接会把语序锁死在中文。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变**（`UploadModal` 仍是 2） |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留扫描 | 三个文件**均为 0 行** |

**真实浏览器端到端**（后端指向真实库副本；用真实 `/api/export` 结果作为导入文件，
**真的把导入流程走到第 2 步**）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` 第 1 步 | 导入数据 / 点击或者拖动 JSON 文件到此区域 / 关闭 —— 与改动前一致 |
| `zh-CN` 冲突步 | 发现以下冲突项，勾选的项目将被跳过： / `跳过·类型·名称` 表头 / 8 行「大类」/ 关闭·确认导入 |
| `en-US` 菜单 | Upload receipt / Export / Import |
| `en-US` 冲突步 | Import data / The following conflicts were found. Checked items will be skipped: / `Skip·Type·Name` / `Category` 行 / Close·Confirm import |
| 剩余中文 | 只有**导出的用户数据**（分类名），不是界面文案 |
| 控制台 | 零 warn / 零 error |

> 这一步的价值在于：**冲突表格是最复杂的一处文案面**（三个表头 + 单元格内的条件文案 +
> 按钮），只靠读代码改是没法确认的。实际把流程走完才看得到。
> 未点「确认导入」，所以没有发生任何写库。

### `79906e9` — P2c-3c 国际化 B-8：设置页收尾 + 后端文案接线

迁移 `SettingsView.vue` 剩余 **23 处**文案。**这是 `.vue` 的最后一批** ——
到此全部界面组件与视图迁完。

**本次最有价值的一处：`translateBackendMessage()` 的首次真实使用**

「版本信息」的描述来自**后端** `/api/settings/version` 的 `description`
（`科学的管理每一颗螺丝钉`）。它不是前端文案，也不能靠改前端来国际化 ——
**它是后端数据**。处置：用 P1 建好的 `translateBackendMessage()` 查 `backend.*` 对照表。

| 语言 | 显示 |
| --- | --- |
| `zh-CN` | 科学的管理每一颗螺丝钉（目录里映射到自身，**与原状逐字一致**） |
| `en-US` | **Keep every last screw in order** |

**这是 P1 那份语言包自建好以来的第一个真实使用者** —— 在此之前它只是一份没人读的数据，
现在整条链路（后端目录 → 前端对照表 → 界面）被证明是通的。

**排查记录：截图里数值不一致，查清后不是数据被改坏**

本次截图显示 Max Tokens `80000`、插件全关；早前几轮显示 `4096`、全开。
**不猜，逐条核对**：① 临时库副本与真实库的 `settings` 行逐字段比对 → 完全一致；
② 查 `stores/settings.ts` → 默认值恰好是 `4096` / 三开一关。
⇒ 早前显示的是**store 默认值**（设置还没拉到），本次是**真实后端值**，**没有数据被改坏**。

真因是一条**既有缺陷**：设置拉取失败时界面**静默显示默认值**，不报错也不提示，
用户会以为「配置被重置了」。已记为 `plan.md` §C3.2 第 14 项。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变** |
| 前端行为探针 | **PROBE IDENTICAL** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留扫描 | `SettingsView.vue` **零残留** |

**真实浏览器端到端**
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 设置 / 模型供应商配置 / 模型名称 / 保存配置 / 服务器配置 / 服务器地址 / 端口 / 测试连接 / 插件功能 / 4 个开关名 / 版本信息 / 应用名称 / 版本号 / 描述 |
| `zh-CN` 点「测试连接」 | 提示 **连接成功** |
| `en-US` | Settings / Model provider / Model name / Save / Server / Server address / Port / Test connection / Plugins / Version / Application / Description |
| `en-US` 点 "Test connection" | 提示 **Connected** |
| **整页零 CJK** | 脚本断言通过（含后端 tagline 已译出） |
| 控制台 | 零 warn / 零 error |

### `219a032` — P2c-4 国际化 B-9：store/api 兜底文案迁移（链条第 1 环收尾）

**这是唯一动 `stores/services` 的一批**，动它之前前端探针一直是「零变化」闸门，故排到最后。

**迁移 48 条兜底文案 + 2 条 api 文案**
- 11 个 store 的 fetch/create/update/remove/自定义动作兜底（按 store 分组命名，便于对照排查）
- `services/api.ts` 的 `请求失败 ({status})` 与 `上传失败`

**关键设计：传 key，在出错那一刻才查表**

`actions.ts` 的三个零件原先收**中文常量**，现在收**语言包 key**
（`message` → `messageKey`、`messages` → `messageKeys`），在 `catch` 里调 `translate(key)`。

**为什么不是「直接传 `translate(key)` 的结果」**：store 是**单例**，配置对象在
**首次创建 store 时**求值一次。若那时就把中文取成常量，用户切语言后这些兜底文案会
**停在旧语言直到刷新页面**。传 key 就没有这个问题。

`i18n.ts` 新增 `translate()` —— 供**组件之外**（store / api 层）取译文。
docstring 明确写了它**不是响应式的**、**禁止在模板与 computed 里用**；
用途只有一类：「出错时取一条消息」这种一次性读取。

**⚠️ 计划里「会动探针、需重采基线」的预判没有成立 —— 而且是好事**

计划预判本批会改变探针观测到的文案、必须重采基线。**实际不需要**：
zh-CN 下每条译文与原中文**逐字节相同**，探针捕获的 **204 条文案 / 46 条兜底文案一字未变**
⇒ **`PROBE IDENTICAL`**。探针没失去「零变化」闸门的作用，也就不需要为「为什么文案变了」逐条辩解。

这不是运气，是前面每一步都坚持「zh-CN 逐字不变」的自然结果。

**唯一剩下的中文**：`stores/subCategory.ts` 的 `unit: string = '个'` —— **表单默认值**，
会随提交写进数据库，属**数据**而非界面文案（同 P2c-1 的判断）。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| **前端行为探针** | **PROBE IDENTICAL** —— 本批最要紧的一条 |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 4 文件 / 0 违规 |
| 中文残留扫描 | stores/services 仅剩 1 行（上述表单默认值） |

> **类型闸门当场逮到一次真错**：改了 pricing/recurring 的内层 key 却漏改外层 `messages:`
> 属性名，`vue-tsc` 立刻报 2 处 `TS2353`。已修 —— 这说明「18 → 18」这个数字背后有判别力。

**真实浏览器验证（探针覆盖不到的一层）**
探针跑的是 zh-CN，**en-US 的这 46 条兜底文案它看不到**。补了一次直接求值：
- 动态 `import('/src/i18n.ts')`，把 `app.stores.*` + `app.api.*` **全部 49 个 key**
  在两种语言下逐个求值 → **无缺失**（没有任何 key 回落成 key 本身）
- `zh-CN`：`获取分类失败`、`请求失败 (500)`
- `en-US`：`Could not load categories`、`Request failed (500)`、`Could not load the statistics`
- 起真实后端确认改名后 `fetchInto` / `writeActions` 仍正常：库存页分类数据照常渲染

**至此链条第 1 环「国际化」的网页端部分全部完成** —— `.vue` / `.ts` 全部迁完，
仅剩 1 行表单默认值刻意保留。

### `9e0165d` — P3 国际化 C：CwClient 镜像同步

**这一步没有「翻译」**：客户端是网页端的逐字节镜像（`mirror.manifest.json` + `mirror.mjs`），
本 Phase 只有「把源端的新内容同步过去」，没有任何适配或改写。

**清单变更**
```
+ src/i18n.ts
+ src/locales/en-US.ts
+ src/locales/zh-CN.ts
```
这三条此前是 `EXTRA_SOURCE`（源端有、清单未收录）。**镜像工具主动报了出来**，
不是静默漏掉 —— `uncovered()` 两端都查（源端漏收 = 新页面没被镜像；
目标端多出 = 违规本地改动）。没有这个检查，新增的 i18n 文件会一直不在客户端里，
而 `--check` 仍然「通过」。

依赖：`package.json` + `vue-i18n ^11.4.10`。**这一条不加就会炸** ——
镜像过去的 `main.ts` 与各 store 都 `import` 了 `@/i18n`，客户端缺这个包直接起不来。

**同步结果**
| 命令 | 结果 |
| --- | --- |
| `mirror.mjs --apply` | 52 entries — **ADDED 3, UPDATED 34**, UNCHANGED 15, PRUNED 0, NO_SOURCE 0 |
| `mirror.mjs --check` | 52 entries, **52 SAME, 0 drifted** → `OK: mirror is byte-identical to Cw_WebUi` |

**验证**
| 项 | 结果 |
| --- | --- |
| **源端只读性** | 同步后 `git status --short Cw_WebUi` **无输出** |
| 客户端 `vue-tsc` | **18 error / 9 文件，与网页端逐个文件计数完全一致** |
| 客户端 `vite build` | 退出码 0 |
| **真实 Electron 端到端** | 见下 |

**真实 Electron 端到端**（`npm run dev -- --remote-debugging-port=9333`）
1. CDP `/json` 确认渲染进程已加载 `http://localhost:5173/`，标题 `CatWareHouse`；
2. 窗口截图：原生菜单栏（File/Edit/View/Window/Help）+ 应用外壳正常渲染；
3. 起真实后端后，**后端访问日志确证客户端发出了请求**：`OPTIONS` 预检 +
   `GET /api/categories`、`/api/notifications`、`/api/alerts`、
   `POST /api/notifications/check`，**全部 200**；
4. 截图确认侧栏渲染出**真实 8 个大类**（日用品 / 3d打印耗材 / 调料 / 衣物 /
   电子产品 / 车辆 / 猫猫 / 打印件，各带彩色图标）、库存列表表头与空态。

> **一次排查值得记**：首次启动时客户端侧栏是**空的**。查后端访问日志发现
> **一条请求都没有** —— 因为客户端在**后端起来之前**就挂载了，`onMounted` 只取一次，
> 失败后不重试也不提示。重启客户端后一切正常。这是既有的「失败不重试、不提示」模式
> （同 §C3.2 第 13/14 项），**不是 P3 引入的回归**——
> 但它再次说明：**判断「是不是我弄坏的」要靠日志证据，不能靠界面表现猜。**

**一个观察（非本次引入，未深究）**：客户端窗口跟随系统深色主题，主内容区呈深色，
但表格头与部分区域仍是浅色，**明暗混用**。只记录现象、**没有查成因**，归属「交互优化」环。

### `dfe2792` — P4a 国际化 D-1：CwMobile 接入 vue-i18n 基础设施

**移动端不是镜像**：镜像只覆盖 `Cw_WebUi → CwClient`。`CwMobile` 有自己的构建与发布节奏，
所以这一步是**独立接入**，不是「同步」。

**新增**
- `src/locales/zh-CN.ts` — 简体中文语言包（默认），导出 `MessageSchema`
- `src/locales/en-US.ts` — 英文语言包，用 `MessageSchema` 约束 ⇒ 漏翻键 = 编译错误
- `src/i18n.ts` — i18n 实例 + 偏好读写 + `translate()` + `translateBackendMessage()`
  （与网页端**同构但不共享模块**）

**修改**
- `src/main.ts` — +2 行（`app.use(i18n)`）
- `src/App.vue` — 5 个 Tab 文案改用 `t('app.nav.*')`；`van-config-provider` 接上 `:locale`
- `package.json` — + `vue-i18n ^11.4.10`

**为什么移动端各存一份语言包，不与网页端共享**
两端文案**大部分相同但并不完全一致** —— 列表 Tab 移动端叫「数据」「售价」，
网页端叫「数据分析」「售价管理」。硬共享要开一堆「移动端特例」开关。
代价是公共文案要改两处；与 `ocr/` 和 `voice/` 各自留一份 `UpstreamRejectedError`
是同一个取舍：**用少量重复换两端互不牵制**。

**实测的文案规模**（决定了 P4 要继续分批）
`src/` 共 **324 行用户可见中文，分布在 28 个文件** —— 与网页端的 360 行同量级。
最大单文件：`utils/categoryIcons.ts` 48 行、`views/PricingView.vue` 36 行、
`views/AnalyticsView.vue` 35 行。

**一个直接复用到的经验**
`createI18n` 泛型顺序是 `<Schema, Locales, Legacy>`，第三个**必须显式传 `false`**
（不传则 legacy 模式，`global.locale` 不是 `ref`，切语言不触发重渲染）。
网页端在 P2a 踩过这个坑，移动端这次直接写对，**没有再踩一遍**。

Vant 的语言包同样是单独一份：`van-config-provider` 的 `:locale` 要显式绑，
它**不**走 vue-i18n。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error**（移动端本来就干净，改后仍是 0） |
| `vite build` | 退出码 0 |
| `spec_check.py` | 5 文件 / 0 违规 |
| 真实浏览器（390×844 移动视口） | `zh-CN`：库存/数据/账本/售价/设置；`en-US`：Stock/Charts/Ledger/Pricing/Settings；布局正常、无重叠 |

> 页面主体文案仍是中文 —— 属 P4b 范围，本阶段刻意不动，把界面回归风险压到零。

### `4f1841e` — P4b 国际化 D-2：移动端分类管理区文案迁移

**批次收窄的理由**：原计划 P4b 是「库存区」，实测约 140 行文案、横跨 9 个文件。
按「一批只做一块、每批独立跑闸门」的既有做法拆开，
本批只做**分类管理**（`categoryIcons` + `CategoryForm` + `CategoryManager`），
范围自洽、不留跨文件半成品。

**迁移内容**
| 文件 | 内容 |
| --- | --- |
| `utils/categoryIcons.ts` | 48 个图标 `label` **字段删除**，改键驱动 |
| `components/CategoryForm.vue` | 名称/描述/图标/图标颜色/单位/备注 + 占位符 + 取消/保存 + 图标 tooltip |
| `components/CategoryManager.vue` | 页面标题、增改标题、两个删除确认框、两个空态 |

词汇表新增：`app.common`（27 条）、`app.categoryManager`（11 条）、`app.icons`（48 条）。

**两个做法**
1. **图标 label 键驱动**（沿用网页端 P2c-1 的结论）：删掉 `label` 字段，
   模板用 `t('app.icons.' + icon.name)`。48 条中文留在 util 里 = 语言包之外又存一份。
   `categoryIcons.ts` 因此**净减 48 行**。
2. **弹层标题存键 + `computed`**：原先点击时就把中文取成字符串存进 ref，
   改为存键、computed 取译文 —— 弹层开着时切语言，标题才会跟着变。

**🐞 控制台检查抓到一个我自己引入的真问题**

`catFormTitleKey` 初值是空串，直接 `t('')` 会让 vue-i18n 打出 **四条**警告
（`Not found '' key in 'en' / 'zh-CN' / 'zh' …`）并逐级回落。
改为 `key ? t(key) : ''` 后消失。

**为什么值得单独记**：这个问题**类型检查过、构建过、界面也看不出异常** ——
唯一能发现它的手段就是「控制台零警告」这条检查。
它不是我碰巧看到的，是**逐条核对控制台输出**核对出来的。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error**（移动端基线本就是 0） |
| `vite build` | 退出码 0 |
| `spec_check.py` | 3 文件 / 0 违规 |
| 中文残留 | 仅 4 处 `'个'` 表单默认值（属数据，同 P2c-1 的判断） |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 分类管理 / 取消·新增大类·保存 / 名称·描述·图标·图标颜色 / **48 个图标 tooltip**（文件夹…丝带） |
| `en-US` | Categories / Cancel·New category·Save / Name·Description·Icon·Icon color / **48 个图标 tooltip**（Folder…Ribbon） |
| 控制台 | 除一条既有的 `<meta apple-mobile-web-app-capable>` 弃用提示外**零警告** |

### `a8120e9` — P4c 国际化 D-3：移动端库存页 + 物品表单 + 修 Vant 语言包接线

**迁移内容**
- `views/InventoryView.vue` — 顶栏提示、空态与按钮、加载中、物品行「已过期」标签、
  价格·库存行、过期行、录入人兜底、滑出删除、新增按钮、分类选择器标题、2 个 toast、删除确认框
- `components/ItemForm.vue` — 标题、取消/保存、7 个字段标签与占位符、过期值占位符

新增 `app.inventory` 段（14 条）。**「价格 ¥… · 库存」原本由模板里两行拼成，
合并为一条带插值的 `priceStock`** —— 英文语序才不会被中文写死
（实测 en-US 渲染为 `Price ¥5.00 · Stock 0 包`）。

另外把「请选择子分类」（toast）与「选择子分类」（顶栏提示）**拆成两个 key** ——
字面不同、语气也不同，不是同一个东西。

**🐞 修掉一个真问题：只绑 `van-config-provider :locale` 不足以切换 Vant 文案**

实测：切到 en-US 后，Vant `picker` 工具栏的按钮**仍然是「取消 / 确认」**。

**查源码定位根因**（不是猜）：
1. `ConfigProvider` 只做了 `provide(CONFIG_PROVIDER_KEY, props)`，**从不调用 `Locale.use()`**；
2. `PickerToolbar` 读的是 `t("cancel")`，而那个 `t` 绑在**模块级的全局 `Locale`** 上
   （`es/locale/index.mjs`：`const lang = ref('zh-CN')` + `messages`）。

**处置：两条线都接。** `watch(locale, …)` 里调 `Locale.use(name, messages)` 切全局，
同时保留 `:locale` prop（给走 provide/inject 的组件用）。
修后实测：en-US 下 picker 显示 `Cancel / Confirm`；zh-CN 下仍是「取消 / 确认」。

> **为什么值得单独记**：P4a 时我把 `:locale` 接上就以为完事了 ——
> **类型检查过、构建过、界面在静态下也看不出问题**，要真的点开 picker 才暴露。
> 与 P4b 的 `t('')` 是同一种性质：只有「真的走一遍交互」或「逐条读控制台」才抓得到。

**本轮往浏览器验证里新加的一步**
以前只比对「页面文案」，本次**额外读了 Vant 自己渲染的 DOM**
（`.van-picker__cancel` / `__confirm` / `__title`）——
正是因为多看了这一眼，才发现 `:locale` 没生效。
**第三方组件自带文案也算界面文案的一部分。**

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留 | 仅 2 处 `'个'` 表单默认值（属数据） |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 选择子分类 / 请选择子分类后查看物品 / 选择分类 / 新增物品 / picker 取消·确认·选择分类 / 物品行「价格 ¥5.00 · 库存 0 包」「删除」—— **与改动前一致** |
| `en-US` | Pick a sub-category / Pick a sub-category to see its items / Choose category / New item / picker `Cancel`·`Confirm`·`Choose category` / 物品行 `Price ¥5.00 · Stock 0 包`、`Delete` |
| 剩余中文 | 只有**用户数据**（分类名、子分类名、单位「包」、商品名） |
| 控制台 | 除既有的 `<meta>` 弃用提示外**零警告** |

### `530464d` — P4d 国际化 D-4：移动端录入区与通知区文案迁移

**迁移内容**
| 文件 | 内容 |
| --- | --- |
| `DataActionsSheet.vue` | 说明文案、3 个动作名、取消、导出成功/失败提示 |
| `UploadModal.vue` | 标题、选图提示、上传中…、取消、上传成功/失败提示 |
| `ImportModal.vue` | 标题、选文件提示、冲突说明、类型单元格、确认导入、完成标题与结果描述、关闭、取消、解析/导入失败提示 |
| `NotificationSheet.vue` | 消息中心、库存预警、低库存、系统通知、已读、暂无通知 |

新增 `app.intake`（19 条）、`app.notify`（6 条）、`common.close`。

**复用判断**：「上传单据」「导入数据」在**菜单项**与**弹层标题**两处出现，
且指的是同一个东西 —— 各只有一个 key。不是巧合重名。

导入结果描述改用具名插值（`{categories}/{subCategories}/{items}`），
中文语序与英文不同，模板字符串拼接会把语序锁死。

**⚠️ 发现一处现有设计覆盖不到的缺口（如实记录，本 Phase 不动）**

库存预警的具体消息（`petg 库存不足 (剩余 0 卷)`）是**后端生成**的字符串 ——
`GET /api/alerts` 返回的 `a.message` 在服务端拼好，前端只能原样显示。

**为什么现有机制接不住**：
- 它**动态**（含分类名与数量），静态的 `backend_messages` 对照表覆盖不了；
- 改服务端生成逻辑会**改变既有响应**，与「既有接口零改动」的硬约束冲突。

⇒ **「前端管界面文案、后端管自己的文案」这条边界，漏了第三类：
后端生成的、读起来像界面文案的**数据**。**
`notification.message` 同理。已记入 `plan.md` §C3.2 第 15 项。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留 | 四个文件**均为 0 行** |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 库存数据工具 / 上传单据·导出数据·导入数据 / 取消；消息中心 / 库存预警 / 低库存；导入数据 / 选择 JSON 备份文件 / 取消 —— **与改动前一致** |
| `en-US` | Stock data tools / Upload receipt·Export·Import / Cancel；Notifications / Stock alerts / Low stock；Import / Choose a JSON backup file / Cancel |
| 控制台 | 除既有的 `<meta>` 弃用提示外**零警告** |

### `00207ae` — P4e 国际化 D-5：移动端账本区文案迁移

**迁移内容**
- `LedgerView.vue` — 页面标题、范围切换、图表标题与 Y 轴名、两条系列名、`typeTag`、
  删除确认框、预算概览标题、搜索占位符、3 个筛选 chip、空态、「未命名」兜底、滑出删除
- `LedgerForm.vue` — 标题、取消/保存、7 个字段、收支两个单选、金额校验 toast、3 个占位符

新增 `app.ledger` 段（28 条）。

**⚠️ 踩到一个作用域遮蔽（vue-tsc 抓不到的那种）**

`LedgerView.vue` 原有：
```ts
function typeTag(t: string): string { return t === 'income' ? '收入' : '支出' }
```
形参就叫 `t`，**会把 i18n 的 `t` 遮住** —— 在函数体里写 `t('app...')`，
调用的其实是那个字符串形参，运行时会直接 `TypeError: t is not a function`。

**处置**：形参改名 `kind`，并把原因写进注释。

> **为什么值得单独记**：`vue-tsc` **抓不到** ——
> 形参类型是 `string`，而「把 string 当函数调」是**我引入**的新用法；
> 类型检查只在签名对不上时报错，这里签名完全「合法」。
> 与 P4b 的 `t('')`、P4c 的 Vant 语言包同性质：
> **改文案这件事，静态检查能覆盖的面比想象中窄。**

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留 | 两个文件**均为 0 行** |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 账本 / 按天·按周·按月·按年 / 全部·收入·支出 / 暂无账单记录 / 占位符「搜索描述/平台/记账人」—— **与改动前一致** |
| `en-US` | Ledger / Day·Week·Month·Year / All·Income·Expense / No ledger entries yet / 占位符 `Search description / platform / person` |
| `en-US` 新增账单弹层 | Cancel / New entry / Save / Amount / Type / Expense·Income / Date / Platform / Description / Recorded by / Notes |
| **整页零 CJK** | 脚本断言在两处界面均为 `false` |
| 控制台 | 零 warn / 零 error |

### `e591b30` — P4f 国际化 D-6：移动端售价区文案迁移

**迁移内容**
- `PricingView.vue` — 页面标题、分类管理器（标题/「全部售价」/2 个空态/名称表单）、
  选择器标题、搜索占位符、加载中、**3 个删除确认框**、4 个 `nameFormTitle`、
  3 条 toast、售价卡片两行、滑出删除
- `PricingForm.vue` — 标题、取消/保存、6 个字段与占位符、商品名校验 toast

新增 `app.pricing`（31 条）与 `app.stores`（**先建 2 条，P4h 复用**）。

**两处刻意的决定**
1. **先建 `app.stores`，而不是把「获取分类失败」塞进 `pricing`** ——
   同一个文案即将在 P4h 的 store 兜底里**再出现一次**。放 `stores` 段两处共用，
   语言包里就不会出现两份「获取分类失败」。
   （这是「提取时机」的另一面：**能预见到第二个使用者时，不必等到它真的出现**。）
2. **售价的分类/子分类各开各的 key**，不复用 `categoryManager.*` ——
   `PricingCategory` 与 `Category` 是**不同的领域对象**，中文逐字相同是巧合。

售价卡片那行原本由模板三行拼成（成本 / 建议售价 / 折扣），
合并为一条带插值的 `costSuggestedPrice` —— 英文语序才不会被中文写死。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 0 违规 |
| 中文残留 | 两个文件**均为 0 行** |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 售价管理 / 全部售价 / 暂无售价记录 / 占位符「搜索商品名/描述」—— **与改动前一致** |
| `en-US` | Pricing / All pricing / No pricing records yet / 占位符 `Search product name / description` |
| `en-US` 分类管理器 | Pricing categories / All pricing / No pricing categories yet |
| `en-US` 分类名称表单 | Cancel / New pricing category / Save / Name |
| **三处界面零 CJK** | 脚本断言通过 |
| 控制台 | 零 warn / 零 error |

### `d48be29` — P4g 国际化 D-7：移动端分析区文案迁移

只动 `views/AnalyticsView.vue`：页面标题、4 张概览卡、加载中、2 个空态、
2 个页签（趋势/分布）、选择器标题、`contextLabel` 兜底，
以及 **8 个图表的标题 / 坐标轴名 / 系列名**。新增 `app.analytics` 段（27 条）。

**沿用的两条做法（与网页端一致）**
1. **`metric.*` 与 `axis.*` 分开**：前者不带单位（饼图扇区/图例用），后者带单位（坐标轴用）。
   合成一个 key 会让饼图扇区叫成「数量 (斤)」。
2. **月度收支对比的收入/支出复用 `app.ledger.typeIncome/typeExpense`** —— 同一份文案不写两遍。

**📝 一次重复踩到的坑（如实记）**

本轮 8 个图表 Edit 里，**前 4 个又失配了** —— 我按印象写了 `old_string`，
读原文后一次通过。这正是 **P2c-2b 已记录过**的那条教训：**改之前先读原文**。

同一个坑在不同 Phase 踩第二次，说明它**没有被真正内化成习惯**。
记在这里不是为了自罚，而是因为「已记录」不等于「已改正」。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 3 文件 / 0 违规 |
| 中文残留 | `AnalyticsView.vue` **零残留** |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 数据分析 / 总库存数 / 总库存价值 / 总收入 / 总支出 / 选择分类 / 选择大类和子类查看趋势 —— **与改动前一致** |
| `en-US` | Analytics / Total items / Total stock value / Total income / Total expense / Choose category / Pick a category and sub-category to see trends |
| **图表实测** | 选「日用品 → 纸巾」渲染 **5 个 canvas**：`Stock share by category` / `Quantity trend`（轴 `Quantity (包)`）/ `Price trend` / `Total price trend` / `Unit price trend`；页签 `Trends` / `Distribution` |
| 剩余中文 | 只有**用户数据**（分类名、单位「包」） |
| **Vant 语言包** | picker 显示 `Cancel / Choose category / Confirm` —— P4c 修的接线在这里复现有效 |

**⚠️ 一条既有的控制台警告（只记录，未深究）**
ECharts `Can't get DOM width or height`（4 次），与 §C3.2 第 12 项同类。
**判定非本次引入**（文案替换不可能影响 DOM 尺寸），
**但移动端的具体成因未验证，不臆测**。归属「交互优化」环。

### `2bf52e2` — P4h 国际化 D-8：移动端设置页 + store/api 兜底文案迁移

**迁移内容**
| 范围 | 内容 |
| --- | --- |
| `views/SettingsView.vue` | 页面标题、外观/深色模式、服务器配置、模型供应商配置、插件功能、版本信息、4 条 toast |
| `stores/actions.ts` | 三个零件改收**语言包 key**（`message`→`messageKey`、`messages`→`messageKeys`） |
| 9 个 store | 兜底文案全部改为 key |
| `services/api.ts` | `请求失败 ({status})`、`上传失败` |

新增 `app.stores`（34 条补齐）、`app.settingsPage`（23 条）、`app.api`（2 条）。

**关键设计（与网页端一致）**
传 **key** 而非「直接传 `translate(key)` 的结果」—— store 是**单例**，
配置对象在首次创建 store 时求值一次；那时取成常量会让兜底文案**停在旧语言直到刷新**。
传 key、出错那一刻才查表，就没有这个问题。

**设置页也接通了 `translateBackendMessage()`**
版本描述由**后端**返回（`/api/settings/version` 的 description）。
实测：`zh-CN` 显示「科学的管理每一颗螺丝钉」（映射到自身，与原状逐字一致），
`en-US` 显示 **"Keep every last screw in order"**。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 4 文件 / 0 违规 |
| **全仓扫描** | 排除语言包本身后，非语言包文件里**仅剩 7 处 `'个'`** 表单默认值（属数据） |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| 检查 | 结果 |
| --- | --- |
| `zh-CN` | 设置 / 外观 / 深色模式 / 服务器配置 / 服务器地址 / 端口 / 测试连接 / 模型供应商配置 / 模型名称 / 保存配置 / 插件功能 / 4 项 / 版本信息 / 应用名称 / 版本号 / 描述 —— **与改动前一致** |
| `zh-CN` 点「测试连接」 | 提示 **连接成功** |
| `en-US` | Settings / Appearance / Dark mode / Server / Server address / Port / Test connection / Model provider / Model name / Save / Plugins / Version / Application / Description |
| `en-US` 点 "Test connection" | 提示 **"Connected"** |
| **整页零 CJK** | 脚本断言通过（含后端 tagline 已译出） |
| 控制台 | 零 warn / 零 error |

**⚠️ 一个尚未完成的缺口（如实记录，不当作已完成）**
**移动端目前没有语言切换入口。** 网页端设置页有「语言」小节（P2b），
移动端这一批只做了文案迁移，界面上没有任何地方能换语言 —— 用户只能靠改 localStorage。

它属于合同第 3 条「完成移动端对后端接口的适配」的一部分：
`/api/i18n/preference` 在移动端**完全没接**（连 `i18nApi` 都没有）。
⇒ 单列为 **P4i**，不混在本批的「完成」里。

### `9eac349` — P4i 国际化 D-9：移动端语言切换 + 后端偏好同步（链条第 1 环收尾）

补的正是 P4h 里**如实记下**的那个缺口 —— 没有把它混进上一批的「完成」里。

**交付**
| 范围 | 内容 |
| --- | --- |
| `types/index.ts` | `LocaleListResponse` / `LocalePreference` / `MessagePackResponse` |
| `services/api.ts` | `i18nApi`（4 个方法**全部实现**，不只是界面用到的两个） |
| `SettingsView.vue` | 「外观」卡片内**一行** `van-cell` + 一个动作面板 |

**界面做法：收纳型控件，不新增页面元素**
- 语言平时只占**一行** `van-cell`（语言 → 当前语言名），点开才是动作面板；
- 面板列出 `简体中文` / `English` —— **endonym，不参与翻译**
  （语言选择器是给看不懂当前界面语言的人用的）；
- **未新增任何顶栏元素**，未改动其它卡片布局。

**采纳规则（与网页端完全一致）**
| 情形 | 行为 |
| --- | --- |
| 本机**没显式选过** | 采纳后端偏好（换设备能带过语言） |
| 本机**选过** | 以本机为准，后端**不**覆盖 |
| 服务器不可达 | 读取静默跳过；切换仍**本机立即生效**，只提示一次同步失败 |

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `vue-tsc` | **0 error** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 4 文件 / 0 违规 |

> 中途两处类型问题已修：① `ref(currentLocale())` 推断成 `AppLocale`，而动作面板回调
> 给的是 `string | undefined` ⇒ 显式标 `ref<string>`；② 模板里 `LOCALE_LABELS[langValue]`
> 索引不上 ⇒ 走一次 `isSupportedLocale` 收窄。
> **两者都是类型闸门当场逮到的**，不是靠肉眼。

**真实浏览器端到端（390 移动视口 + 真实后端 + 真实库副本）—— 7 项行为逐个实测**
| # | 行为 | 结果 |
| --- | --- | --- |
| 1 | 「外观」卡片内渲染出「语言 → 简体中文」一行 | ✅ |
| 2 | 面板列出 `简体中文` / `English`（endonym 未被翻译） | ✅ |
| 3 | 选 English → **整页立即切换，无需刷新**（断言 `hasCjk=false`） | ✅ |
| 4 | 同步成功：`GET /api/i18n/preference` 与 sqlite `settings.locale` **都**变 `en-US` | ✅ |
| 5 | 清空 localStorage 重载（模拟换设备）→ **采纳后端值并写回本机** | ✅ |
| 6 | 再切回 `简体中文` → UI / localStorage / 后端**三处一起回到** `zh-CN` | ✅ |
| 7 | 停掉后端再切换 → 本机生效 + 提示「未能同步到服务器」 | ✅ |

控制台仅一条 `ERR_CONNECTION_REFUSED`（停后端测离线时**浏览器自身**的记录），**无应用级告警**。

**链条第 1 环「国际化」至此收尾**
| 端 | 状态 |
| --- | --- |
| `CwServer` | `api/i18n` 分区 + `locales/` 语言包；`translateBackendMessage` 被两端真实使用 |
| `Cw_WebUi` | 全部 `.vue` / `.ts` 迁完，剩 1 处 `'个'`（数据） |
| `CwClient` | 镜像同步零漂移，Electron 实测通过 |
| `CwMobile` | 全部迁完 + 语言切换入口 + 后端偏好同步 |

### `aa3575b` — P5 通用化-1：货币偏好接口 + 抽出共享的 settings 单行取用

**先把「通用化」的判据定下来**（`plan.md` §C29）：链条里的方向都是产品向的
（国际化 / 交互优化 / 快捷键优化 / 打包…），所以通用化 = **把写死的具体值变成通用能力**，
不是「重构代码」。

**选货币作为第一刀的证据**：后端早就有 `GET /api/currencies`（8 种货币含符号）、
模型早有 `SpecificItem.currency` 列、**两端前端也都定义了 `currencyApi`** ——
但**没有任何界面用过**，UI 到处写死 `¥`。这与任务 D 修掉的 `dataManager/` 是同一个
signature：**造了零件却没接线**。

**新增接口（只增不改）**
| 方法 | 路径 | 作用 |
| --- | --- | --- |
| GET | `/api/currencies/preference` | `{code, symbol}` |
| PUT | `/api/currencies/preference` | 写入；未知代码 → **422** |

**三条设计**
1. **默认值就是现状**：默认 `CNY` ⇒ 符号 `¥` ⇒ **界面逐字不变**
   （与 i18n 默认 `zh-CN` 同一个把风险压到零的手法）；
2. **符号由服务端查表**：PUT 只接受 `code`，客户端自报的 `symbol` 一律忽略
   （已实测：传 `symbol="!!!FAKE!!!"` 仍返回 `€`）；
3. **读接口对脏值宽容、写接口才校验**：列被手工改坏时读回默认而不是 500。
   与「未知 locale 不回退」取向不同 —— 那是**请求**不存在，这是**存量数据**脏。

**顺带做掉本环的一处真实重复**
`api/system/settings_router.py` 与 `api/i18n/i18n_router.py` 各有一份私有的
「取或建 settings 单行」（i18n 那份当时是为遵守「分区之间不互相 import」**刻意复制**的）。
货币分区会带来**第三份** ⇒ 上移到 `models/settings.py::get_or_create()`。
**放 `models/` 而不是某个分区里**：三个分区都不必 import 另一个分区，
**既去了重、也没破坏分区独立性**。顺手删掉两处因改动而变成孤儿的 `select` import。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| `verify_contract_additive` | 既有面逐字冻结，只多出 **2 条**货币路由 |
| `http_probe`（81 条真实请求） | **逐字段一致** |
| `pyright` | **66 → 66**，逐文件计数完全一致 |
| `py_spec_check` | 52 文件 / **3 违规**（全部既有） |
| `smoke_currency.py` | **14/14** |
| 迁移冒烟（真实库副本） | **通过** |

`smoke_currency.py` 覆盖：`/api/currencies` 仍 8 条且键未变；默认 `CNY/¥`；
`PUT USD -> $`；客户端自报 symbol 被忽略；未知代码 422 且**不改动已存值**；
**`/api/settings` 未长出 `currency` 字段**；**`/api/i18n/preference` 在共用助手重构后
仍正常**（回归）；重启后偏好仍在。

迁移冒烟：**真实库副本**原本只有 `locale` 列 → 启动后多出 `currency`（默认 `CNY`），
`categories` 仍 8 行；**真 `catwarehouse.db` 未被触碰**（mtime + sha256 前后一致）。

**未做的事（刻意）**：未改任何前端 —— 本 Phase 只做后端接口（合同第 1 条）。
把 UI 里写死的 `¥` 换成后端符号是 **P6（WebUi）/ P7（Mobile + 镜像）**。

**另外两个候选被评估后拒绝**（理由记在 `plan.md` §C29）：
- **WebUi ↔ Mobile 的近重复**（`types/index.ts` 364 行仅 1 行不同等，约 500 行）：
  去重需要把三个独立构建根合成 monorepo workspace，而根目录没有 `package.json`、
  `.gitignore` 带冲突标记未授权改、客户端镜像以 `../Cw_WebUi` 为源。
  **代价是一整套构建架构迁移，收益只是 500 行重复** ⇒ 记为「评估后拒绝」，不是遗漏。
- **后端手工逐字段构造响应**：任务 D 已判「把原代码搬进钩子并没有减少任何东西」。

### `1750bed` — P6 通用化-2：WebUi 货币适配（写死的 `¥` 换成后端符号）

接 P5 新增的 `/api/currencies/preference`，让界面不再写死 `¥`。

**交付**
| 范围 | 内容 |
| --- | --- |
| `stores/currency.ts`（新增） | `code` / `symbol` / `fetchPreference()` |
| `types/index.ts` | `CurrencyPreference` / `CurrencyInfo` |
| `services/api.ts` | `currencyApi` + `getPreference` / `updatePreference`（写只传 code） |
| 组件（10 处 `¥`） | ItemTable / ItemCard / ItemForm / PricingTable ×2 / AnalyticsCharts ×3 / LedgerView ×2 |
| 语言包（10 处 `(¥)`） | `analytics.axis.{price,totalPrice,unitPrice,amount}`、`ledger.chartAmountAxis`（中英各 5） |

`App.vue` 启动时拉一次偏好，符号全局共用。

**语言包里的 `(¥)` 怎么处理**
改成 `价格 ({symbol})`，由调用点传 `{ symbol: currencyStore.symbol }`。
**没有**把符号写进语言包 —— 货币是**数据**不是**文案**，
写进语言包会让「切语言」与「切货币」两个正交的维度缠在一起。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| **前端行为探针** | **PROBE IDENTICAL**（204 条文案 / 78 次 api 调用一字未变） |
| `vue-tsc` | 18 → 18，逐文件计数**逐个不变** |
| `vite build` | 退出码 0 |
| `spec_check.py` | 5 文件 / 0 违规 |
| 硬编码扫描 | 组件里已无 `¥`（仅剩注释与 `DEFAULT_SYMBOL` 常量本身） |

**真实浏览器端到端**（真实后端 + 真实库副本）
| # | 检查 | 结果 |
| --- | --- | --- |
| 1 | **默认 CNY**：库存表价格列 | `¥5.00` —— 与改动前**逐字一致** |
| 2 | `PUT {"code":"USD"}` | 返回 `{"code":"USD","symbol":"$"}` |
| 3 | 重载后库存表 | `$5.00`；分析页概览卡 `$10 / $0 / $0` |
| 4 | **图表轴名** | `价格 ($)`（截图确认，canvas 读不到）；数量轴仍是 `数量 (包)` |
| 5 | 控制台 | 零 warn / 零 error |

> **本节最要紧的一条**：整个过程**一行代码都没改**，只改了后端的偏好值，
> 界面符号就跟着变了 —— 这正是「通用化」要的效果。

**未做的事（刻意）**：未做货币切换的 UI 入口（与 P7 Mobile 一起考虑，
避免两端做出两套交互）；未改 `SpecificItem.currency` 列的语义 ——
它是**逐条目**的货币，本次做的是**全局计价货币**，两者不是一回事。

### `df20074` — P7 通用化-3：Mobile 货币适配 + CwClient 镜像同步

**交付**
| 端 | 内容 |
| --- | --- |
| `CwMobile` | `stores/currency.ts`（新增，与网页端同构的另一份）+ `types` + `currencyApi` + `App.vue` 启动拉取；替换 **9 处**组件 `¥`、**12 处**语言包 `¥` 为 `{symbol}` 插值 |
| `CwClient` | `mirror.manifest.json` +1 条；`--apply` 同步 11 个文件 |

移动端 `stores/currency.ts` 与网页端是**同构的另一份**，不是共享模块 ——
移动端不参与镜像，是独立构建的应用。

**镜像工具又一次主动报出了问题**
`--apply` 后 `--check` 报 `EXTRA_SOURCE (1): src/stores/currency.ts` ——
新 store **源端有、清单未收录**。没有这个检查，它会一直不在客户端里，
而 `--check` 仍显示「通过」。已补进清单并重新 apply。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| 移动端 `vue-tsc` | **0 error** |
| 移动端 `vite build` | 退出码 0 |
| `spec_check.py` | 4 文件 / 0 违规 |
| 客户端 `vue-tsc` | **18 error / 9 文件，与网页端逐个文件计数完全一致** |
| `mirror.mjs --check` | **53 entries, 53 SAME, 0 drifted** |
| 源端只读性 | `git status --short Cw_WebUi` **无输出** |

**真实浏览器端到端**（390 移动视口 + 真实后端 + 真实库副本）
| # | 检查 | 结果 |
| --- | --- | --- |
| 1 | **默认 CNY** | `价格 ¥5.00 · 库存 0 包` —— 与改动前**逐字一致** |
| 2 | 切 **EUR** 后重载 | `价格 €5.00 · 库存 0 包` |
| 3 | 分析页概览卡 | `总库存价值 €10`、`总收入 €0`、`总支出 €0` |
| 4 | 控制台 | 零 warn / 零 error |

**货币通用化四端打通**
| 端 | 状态 |
| --- | --- |
| `CwServer` | `/api/currencies/preference` 两个新端点；符号由服务端查表 |
| `Cw_WebUi` | 10 处 `¥` → 后端符号；轴名走 `{symbol}` 插值 |
| `CwClient` | 镜像同步零漂移 |
| `CwMobile` | 9 处 `¥` → 后端符号；语言包 12 处改插值 |

**仍未做**：货币切换的 **UI 入口**（两端都还没有）。后端与数据通路已完备，
缺的只是一个设置项 —— 留待后续，可能需要与「单位字典」P8 一起考虑，
两者都是「用户可配置的计价/计量口径」。

### `1da7946` — P8 通用化-4：货币切换 UI 入口（两端）+ 镜像同步

**⚠️ 本次改了计划，理由记在最前面**

原定 P8 是「单位字典」。动手前核对现状发现：**货币能力此时是不可达的** ——
后端与数据通路（P5/P6/P7）都做完了，界面上却没有任何地方能改货币，只能调 API。

> **把已开工的能力做成用户够得着的，优先于再开一个半成品。**
> 「单位字典」顺延为 **P9** —— 不是被砍掉，只是排在后面。

**交付（两端都不新增区块）**
| 端 | 做法 |
| --- | --- |
| `Cw_WebUi` | 在**既有的**「语言」折叠区里加**第二项「货币」**（同一个 `NCollapse`），选项来自后端 `GET /api/currencies`，展示形如 `¥ CNY` |
| `CwMobile` | 「外观」卡片里加**第二行 cell**，点开是动作面板，与「语言」完全同构 |

新增语言包键（中英各 3 条）：`currency` / `currencyNote` / `currencySyncFailed`。

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| 网页端 `vue-tsc` | 18 → 18（逐文件一致） |
| 移动端 `vue-tsc` | **0 error** |
| 两端 `vite build` | 退出码 0 |
| `spec_check.py` | 两端各 3 文件 / 0 违规 |
| `mirror.mjs --check` | **53 entries, 53 SAME, 0 drifted** |

**真实浏览器端到端**（真实后端 + 真实库副本）
| 端 | 检查 | 结果 |
| --- | --- | --- |
| 网页端 | 折叠区出现「语言」「货币」两项 | ✅ |
| 网页端 | 货币下拉列出**后端返回的全部 8 种**（`¥ CNY` … `NT$ TWD`） | ✅ |
| 网页端 | 选 EUR → 后端 `{code:EUR,symbol:€}` → **库存页价格列即时变 `€5.00`（无需刷新）** | ✅ |
| 移动端 | 「货币」行显示后端当前值 `EUR`；面板列出 8 种 | ✅ |
| 移动端 | 选 USD → 后端 `{code:USD,symbol:$}`、该行变 `货币 USD` → 库存页 `价格 $5.00 · 库存 0 包` | ✅ |
| 两端 | 控制台 | **零 warn / 零 error** |

> **这一节验证的正是本环的目标**：货币从「代码里的常量」变成了
> 「用户可在界面上改、且全站即时生效的配置」。

**未做的事（刻意）**：单位字典顺延为 P9；未动 `SpecificItem.currency`。

### `5ef8976` — P9 通用化-5：单位字典（后端接口 + 两端「选或自由输入」+ 镜像）

补掉的是 §C12 里**如实记下**的那笔债（原文：「要改应另开一项『单位字典』的需求，
**不在本 Phase 夹带**」）—— 与 P4i 补 i18n 缺口同样的做法。

**它解决的问题其实是两件**（之前只记了第一件）
1. `SubCategory.unit` 是**自由文本**，没有约束 ——「斤」「市斤」「500g」会同时出现在
   同一列，统计与票据对照都会失准；
2. 新建表单把默认值写死成 `'个'`（本仓库共 **12 处**），而 `'个'` 是**语言相关的**。
   §C12 记过「跟着界面语言翻译会让同一张表里中英混杂」——
   **真正的解法不是翻译它，而是让默认值来自字典。**

**后端（新增接口）**
`api/inventory/unit_router.py` —— `GET /api/units`，22 个常用单位。
**放 `inventory` 而不是 `system`**：单位是**库存词汇**（`SubCategory.unit` 属库存），
而 `currencies` 放 `system` 是因为它服务**全站计价**。分区按功能，不按「像不像参考数据」。

**两端（`stores/units.ts` + `unitApi`）**
| 设计 | 说明 |
| --- | --- |
| **默认值 = 字典第一项** | 默认值仍然存在，但来自后端，不再散落在 12 个文件里 |
| **离线兜底 `FALLBACK_UNIT = '个'`** | 与接入前**逐字相同** ⇒ 接入字典本身不产生任何可见变化 |
| **选或自由输入** | WebUi 用 `NSelect` 的 `filterable + tag`；Mobile 保留输入框 + **下方一行 chips** |

**刻意不改成枚举**：那需要一次**数据迁移**，而 `unit` 还会被 **OCR / 语音两条写入路径**
碰到 —— 项目级的决定，不夹在本环里。**字典只作建议，不是约束。**

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| additive contract | 只多 **1 条**路由（`GET /api/units`） |
| `http_probe`（81 条） | **逐字段一致** |
| 后端 `pyright` | 66 → 66 |
| 后端 `py_spec_check` | 7 文件 / 1 违规（既有） |
| WebUi `vue-tsc` / build / **探针** | 18 → 18 / 0 / **PROBE IDENTICAL** |
| Mobile `vue-tsc` / build | **0 error** / 0 |
| CwClient `vue-tsc` | 18（与网页端一致） |
| `mirror.mjs --check` | **54 entries, 54 SAME, 0 drifted** |

**真实浏览器端到端**（真实后端 + 真实库副本）
| 端 | 检查 | 结果 |
| --- | --- | --- |
| 后端 | `GET /api/units` | 22 项，首项 `个` |
| WebUi | 新增子分类弹层：单位字段变下拉，**默认 `个`**，展开列出后端单位 | ✅ |
| Mobile | 新增子分类弹层：**22 个 chips**（个 包 箱 … ml），`个` 高亮 | ✅ |
| Mobile | 截图确认**布局无重叠、无错位** | ✅ |

**链条第 2 环「通用化」至此收尾**：P5 后端货币接口 → P6 WebUi 货币适配 →
P7 Mobile 货币适配 + 镜像 → P8 两端货币切换 UI → P9 单位字典。

### `47860d7` — P10 OCR优化-1：让置信度真正生效（低置信度行如实上报）

链条第 3 环「OCR 优化」第一刀。

**动手前核对到的现状：两个「造了零件没接线」**
1. `TextLine.confidence` 一直被引擎采集（`response.py` 两处都填），
   **但 parser / pipeline 从不读取**；
2. `OcrConfig.confidence_threshold` 由 builder 写入（`builder.py:69`），**没有任何地方读**。

与前两环修掉的 currency / unit 是**同一个 signature**。

**核心取舍：上报而不是丢弃**
把低置信度的行直接扔掉看起来更"干净"，但那会**静默少一条明细**、合计随之变错 ——
比留着一条可能不准的行更糟。所以解析**照旧跑全部行**（本轮不改变任何解析结果），
`Receipt.low_confidence` 如实列出哪些行不可靠，由调用方决定怎么提示。
与 receipts「出库扣不足要归零并**汇报**」同一个取向：**不静默**。

**改动（3 个文件，均为追加）**
| 文件 | 内容 |
| --- | --- |
| `ocr/types.py` | `LowConfidenceLine`；`Receipt.low_confidence`；`to_dict()` 多一个键 |
| `ocr/settings.py` | `OCR_MIN_CONFIDENCE`（默认 0.6）+ `_clamp01` |
| `ocr/pipeline.py` | `ReceiptRecognizer(min_confidence=…)` + `_low_confidence()`；`create_recognizer()` 传入 |

**阈值夹到 0~1**：写 `-1` 会让所有行都成噪声，写 `2` 会让功能彻底失效 ——
两者都是「配置写错但看起来在工作」。

**回退路径刻意不误报**：引擎不实现 `LineOcrEngine` 时本来就没有置信度信息，
造出的 `TextLine` 置信度是默认 `1.0`，永不进 `low_confidence`。
**警告一旦永远亮着就没人看了。**

**闸门（全绿）**
| 闸门 | 结果 |
| --- | --- |
| additive contract | **CONTRACT HELD** |
| `http_probe`（81 条） | **逐字段一致** |
| `pyright` | 66 → 66（逐文件一致） |
| `py_spec_check`（ocr 15 文件） | **0 违规** |
| 单元冒烟 | **14/14** |
| 端到端冒烟（**真实 HTTP 两跳**） | **17/17** |

端到端断言含：8 个既有键一个不少、新增 `low_confidence`、恰好两条低置信度行带置信度值、
高置信度行不上报、**低置信度行仍被解析进明细（没被丢）**、
**合计仍取自那条低置信度的「合计」行**。

**诚实说明**：桩服务是**替身**（本机 3.13 装不上 paddleocr），本轮验证的是
**「逐行置信度能穿过整条链路并出现在响应里」**，**不是识别准确率** ——
后者仍是 `CwServer/plan.md` §10 记录的未验证项。

**未做的事**：未删既有的死配置 `OcrConfig.confidence_threshold`（Karpathy 准则 3）；
未改前端（前端目前完全不调用 `/api/ocr/*`）。

### `4de74de` — P11 OCR优化-2：WebUi 接入 OCR（上传单据 → 识别 → 核对 → 入库）

把「造好了却没人用」的 `/api/ocr/*` 端点接到网页端，并把「上传单据」这个
**原本是死代码**的入口变成真正可用的功能。

**动手前核对到的现状**：后端 `/api/ocr/receipt` + `/api/ocr/receipt/apply` 已实现，
但**没有任何前端调用**；前端唯一 OCR 痕迹是 `FloatingButton.handleUpload` 里的
`fetch('/api/image-analysis')` —— **该路径不存在**，结果只 console.log。

**新增**：`OcrReceiptModal.vue`（核对+入库弹层，两态）；`types/index.ts` 8 个类型；
`services/api.ts` 的 `ocrApi` + 共享 `postForm`。

**修改**：`FloatingButton.vue`（死 fetch → 识别 → 打开核对弹层）；
`UploadModal.vue`（修掉一个阻塞本功能的既有 bug）。

**核对弹层（界面谨慎、收纳型）**：复用既有 UploadModal 作选择器（未改其 UI）；
核对视图（商户/日期/总额 + 低置信度警告 + 分类下拉 + 明细勾选）→ 结果视图
（新增物品/更新子分类/账本/跳过/归零）；分类下拉来自后端；低置信度行如实显示。

**🐞 修掉一个阻塞本功能的既有 bug**（18 个基线错误之一）：`handleUploadChange({ fileList })`
把 naive-ui emit 的**数组**解构成 undefined、覆盖 v-model 的正确值，「上传」按钮永远不可用。
改成正确签名后恢复可用。

**闸门（全绿）**：vue-tsc **18 → 17**（修掉那 1 个签名错误）；探针 PROBE IDENTICAL；
build 0；spec_check 6 文件 0 违规。

**真实浏览器端到端**（真实后端 + 真实 HttpOcrEngine + PaddleX 契约桩 OCR）：
上传 → 识别弹层（商户/日期/总额 ¥33.00/两条明细）→ 低置信度警告（花椒 45%、合计 30%）
→ 分类下拉选「调料/香料」→ 入库 → 结果（新增 2、更新子分类 1、账本 -）。
**数据库实测**：香料子分类 0→3、两条明细写入、description 带摘要、ledger 仍为 0。

**诚实说明**：桩 OCR 是替身，验证的是「整条 OCR 链路在界面上可用」，不是识别准确率。

**未做的事**：Mobile OCR 适配（P12）、语音端 UI 接线（独立链路，不混本 Phase）。
